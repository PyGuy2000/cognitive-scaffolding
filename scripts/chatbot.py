#!/usr/bin/env python3
"""Streamlit chatbot UI for the Cognitive Scaffolding pipeline.

Usage:
    streamlit run scripts/chatbot.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure project root is on sys.path so imports resolve
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

import streamlit as st

from cognitive_scaffolding.core.data_loader import DataLoader
from cognitive_scaffolding.core.models import LayerName
from cognitive_scaffolding.orchestrator.conductor import CognitiveConductor
from cognitive_scaffolding.adapters.chatbot_adapter import ChatbotAdapter
from utils.ai_client import AIClient

# ── Constants ──────────────────────────────────────────────

PROFILES = ["chatbot_tutor", "rag_explainer", "etl_explain"]

LAYER_LABELS = {
    "diagnostic": "Diagnostic",
    "activation": "Activation",
    "contextualization": "Contextualization",
    "metaphor": "Metaphor",
    "narrative": "Narrative",
    "structure": "Structure",
    "interrogation": "Interrogation",
    "encoding": "Encoding",
    "transfer": "Transfer",
    "challenge": "Challenge",
    "reflection": "Reflection",
    "elaboration": "Elaboration",
    "synthesis": "Synthesis",
}

# ── Cached resources ───────────────────────────────────────


@st.cache_resource
def get_data_loader() -> DataLoader:
    return DataLoader(str(PROJECT_ROOT / "data"))


@st.cache_resource
def get_conductor(use_ai: bool) -> CognitiveConductor:
    ai_client = None
    if use_ai:
        ai_client = AIClient()
        if not ai_client.is_available():
            st.sidebar.warning("AI credentials not found — using template fallbacks")
            ai_client = None
    return CognitiveConductor(
        ai_client=ai_client,
        profiles_dir=str(PROJECT_ROOT / "profiles"),
        data_dir=str(PROJECT_ROOT / "data"),
    )


def get_ai_client(use_ai: bool) -> AIClient | None:
    """Get a standalone AI client for raw LLM comparison."""
    if not use_ai:
        return None
    client = AIClient()
    return client if client.is_available() else None


# ── Sidebar ────────────────────────────────────────────────


def render_sidebar() -> dict:
    """Render sidebar controls and return the current configuration."""
    st.sidebar.title("Settings")

    # Profile
    profile = st.sidebar.selectbox("Profile", PROFILES)

    # AI toggle
    st.sidebar.markdown("---")
    use_ai = st.sidebar.toggle("Enable AI", value=False)

    # Audience
    st.sidebar.markdown("---")
    loader = get_data_loader()
    audiences = sorted(loader.list_audiences())
    audience = st.sidebar.selectbox(
        "Audience",
        audiences,
        index=audiences.index("general") if "general" in audiences else 0,
    )

    # Domain
    domains = sorted(loader.list_domains())
    domain_options = ["Auto (from audience)"] + domains
    domain_choice = st.sidebar.selectbox("Domain", domain_options)
    domain_id = None if domain_choice == "Auto (from audience)" else domain_choice

    # Layer toggles
    st.sidebar.markdown("---")
    st.sidebar.subheader("Layer Toggles")

    # Detect profile change and reset toggle keys
    if "prev_profile" not in st.session_state:
        st.session_state.prev_profile = profile
    if st.session_state.prev_profile != profile:
        for layer in LAYER_LABELS:
            key = f"layer_{layer}"
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.prev_profile = profile
        st.rerun()

    # Load profile defaults for initial checkbox values
    conductor = get_conductor(use_ai)
    layer_configs = conductor.toggle_manager.load_profile(profile)

    overrides = {}
    for layer_value, label in LAYER_LABELS.items():
        default = layer_configs[layer_value].enabled
        enabled = st.sidebar.checkbox(
            label, value=default, key=f"layer_{layer_value}"
        )
        if enabled != default:
            overrides[layer_value] = {"enabled": enabled}

    return {
        "profile": profile,
        "use_ai": use_ai,
        "audience": audience,
        "domain_id": domain_id,
        "overrides": overrides if overrides else None,
    }


# ── Compilation ────────────────────────────────────────────


def compile_topic(topic: str, config: dict) -> tuple[list, dict]:
    """Compile a topic and return (messages, scores)."""
    conductor = get_conductor(config["use_ai"])
    record = conductor.compile(
        topic=topic,
        audience_id=config["audience"],
        profile_name=config["profile"],
        overrides=config["overrides"],
        domain_id=config["domain_id"],
    )
    messages = ChatbotAdapter().format(record)
    scores = _extract_scores(record)
    return messages, scores


def generate_raw_response(topic: str, audience: str, use_ai: bool) -> str:
    """Generate a raw LLM response with no scaffolding for comparison."""
    client = get_ai_client(use_ai)
    if not client:
        return "_Enable AI to see raw LLM comparison._"
    prompt = f"Explain {topic} for a {audience} audience."
    return client.generate(prompt)


def _extract_scores(record) -> dict:
    """Extract overall and per-layer scores from a compilation result."""
    evaluation = record.artifact.evaluation
    if evaluation:
        return {
            "overall": evaluation.overall_score,
            "layers": dict(evaluation.layer_scores),
            "penalty": evaluation.penalty_applied,
            "penalty_reason": getattr(evaluation, "penalty_reason", None),
        }
    return {"overall": 0.0, "layers": {}, "penalty": False, "penalty_reason": None}


# ── Rendering ──────────────────────────────────────────────


def render_scores(scores: dict) -> None:
    """Render overall + per-layer scores."""
    st.metric("Overall Score", f"{scores['overall']:.0%}")

    if scores.get("penalty"):
        reason = scores.get("penalty_reason") or "missing required layers"
        st.caption(f"Penalty applied: {reason}")

    layer_scores = scores.get("layers", {})
    if layer_scores:
        import pandas as pd

        df = pd.DataFrame(
            {"Score": [v for v in layer_scores.values()]},
            index=[LAYER_LABELS.get(k, k) for k in layer_scores.keys()],
        )
        st.bar_chart(df)


def get_synthesis_content(messages: list) -> str | None:
    """Extract the synthesized response text from messages."""
    for msg in messages:
        if msg.get("layer") == "synthesis":
            return msg["content"]
    return None


def render_layer_details(messages: list) -> None:
    """Render individual layer outputs inside an expander."""
    with st.expander("Layer Details"):
        for msg in messages:
            layer = msg.get("layer", "unknown")
            if layer in ("evaluation", "synthesis"):
                continue
            confidence = msg.get("confidence", 0)
            label = LAYER_LABELS.get(layer, layer)
            st.markdown(f"**{label}** ({confidence:.0%})")
            st.markdown(msg["content"])
            st.markdown("---")


# ── Main ───────────────────────────────────────────────────


def main() -> None:
    st.set_page_config(
        page_title="Cognitive Scaffolding Chatbot",
        page_icon="🧠",
        layout="wide",
    )
    st.title("Cognitive Scaffolding Chatbot")

    config = render_sidebar()

    # Topic input
    topic = st.text_input("Topic", placeholder="e.g., neural networks")
    compile_btn = st.button("Compile", disabled=not topic, type="primary")

    if compile_btn and topic:
        st.session_state.topic = topic

        with st.spinner("Compiling cognitive scaffold..."):
            messages, scores = compile_topic(topic, config)
            st.session_state.messages = messages
            st.session_state.scores = scores

        with st.spinner("Generating raw LLM baseline..."):
            raw = generate_raw_response(topic, config["audience"], config["use_ai"])
            st.session_state.raw_response = raw

    # Render results
    if st.session_state.get("messages"):
        scores = st.session_state.get("scores", {})

        # Scores bar chart
        if scores:
            render_scores(scores)

        # Side-by-side: scaffolded synthesis vs raw LLM
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Scaffolded Response")
            synthesis = get_synthesis_content(st.session_state["messages"])
            if synthesis:
                st.markdown(synthesis)
            else:
                st.info("No synthesis layer output. Enable the Synthesis layer to see a unified response.")

        with col2:
            st.subheader("Raw LLM Response")
            raw = st.session_state.get("raw_response", "")
            if raw:
                st.markdown(raw)
            else:
                st.info("No raw response available.")

        # Layer details in expander
        render_layer_details(st.session_state["messages"])


if __name__ == "__main__":
    main()
