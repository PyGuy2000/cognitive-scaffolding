#!/usr/bin/env python3
"""CLI demo for the Cognitive Scaffolding pipeline.

Validates the full pipeline end-to-end across all three adapters
and the experiment runner.

Usage:
    python scripts/demo.py chatbot    --topic "neural networks" --audience child
    python scripts/demo.py rag        --topic "gradient descent" --audience data_scientist
    python scripts/demo.py etl        --topic "transformers"    --audience general
    python scripts/demo.py experiment --topic "neural networks" --audience general --layers metaphor encoding
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

# Ensure project root is on sys.path so imports resolve
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from cognitive_scaffolding.orchestrator.conductor import CognitiveConductor
from cognitive_scaffolding.adapters.chatbot_adapter import ChatbotAdapter
from cognitive_scaffolding.adapters.rag_adapter import RAGAdapter
from cognitive_scaffolding.adapters.etl_adapter import ETLAdapter
from cognitive_scaffolding.orchestrator.experiment_runner import (
    ExperimentConfig,
    ExperimentRunner,
)
from utils.ai_client import AIClient

SEPARATOR = "=" * 60


def _header(title: str) -> None:
    """Print a section header."""
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def _build_conductor(args: argparse.Namespace) -> CognitiveConductor:
    """Build a CognitiveConductor pointed at project dirs."""
    ai_client = None
    if not args.no_ai:
        ai_client = AIClient(provider=args.provider, model=args.model)
        if not ai_client.is_available():
            print("  [warn] AI client failed to initialize — falling back to templates")
            ai_client = None

    status = ai_client.get_status() if ai_client else None
    _header("AI Status")
    if status:
        print(f"  Provider  : {status['provider']}")
        print(f"  Model     : {status['model']}")
        print(f"  Available : yes")
    else:
        reason = "disabled (--no-ai)" if args.no_ai else "no valid credentials"
        print(f"  Available : no ({reason})")

    return CognitiveConductor(
        ai_client=ai_client,
        profiles_dir=str(PROJECT_ROOT / "profiles"),
        data_dir=str(PROJECT_ROOT / "data"),
    )


# ── Chatbot ─────────────────────────────────────────────────

def cmd_chatbot(args: argparse.Namespace) -> None:
    profile = args.profile or "chatbot_tutor"
    _header(f"Chatbot  |  topic={args.topic!r}  audience={args.audience!r}  profile={profile!r}")

    conductor = _build_conductor(args)
    record = conductor.compile(args.topic, args.audience, profile)
    messages = ChatbotAdapter().format(record)

    for msg in messages:
        layer = msg.get("layer", "?")
        confidence = msg.get("confidence", 0)
        role = msg.get("role", "assistant")
        print(f"\n--- [{layer}] (confidence: {confidence:.0%}, role: {role}) ---")
        print(msg["content"])

    print(f"\n{SEPARATOR}")
    print(f"  Total messages: {len(messages)}")
    print(SEPARATOR)


# ── RAG ─────────────────────────────────────────────────────

def cmd_rag(args: argparse.Namespace) -> None:
    profile = args.profile or "rag_explainer"
    _header(f"RAG  |  topic={args.topic!r}  audience={args.audience!r}  profile={profile!r}")

    conductor = _build_conductor(args)
    record = conductor.compile(args.topic, args.audience, profile)
    chunks = RAGAdapter().format(record)

    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        print(f"\n--- Chunk {i}/{len(chunks)} ---")
        print(f"  chunk_id   : {chunk['chunk_id']}")
        print(f"  layer      : {meta.get('layer', '?')}")
        print(f"  field      : {meta.get('field', '?')}")
        print(f"  confidence : {meta.get('confidence', 0):.2f}")
        print(f"  score      : {meta.get('score', 'N/A')}")
        content_preview = chunk["content"][:200]
        if len(chunk["content"]) > 200:
            content_preview += "..."
        print(f"  content    : {content_preview}")

    print(f"\n{SEPARATOR}")
    print(f"  Total chunks: {len(chunks)}")
    print(SEPARATOR)


# ── ETL ─────────────────────────────────────────────────────

def cmd_etl(args: argparse.Namespace) -> None:
    profile = args.profile or "etl_explain"
    _header(f"ETL  |  topic={args.topic!r}  audience={args.audience!r}  profile={profile!r}")

    conductor = _build_conductor(args)
    record = conductor.compile(args.topic, args.audience, profile)
    flat = ETLAdapter().format(record)

    # Group keys for readability
    groups = {
        "Artifact": ["artifact_id", "record_id", "topic", "audience_id",
                      "audience_name", "expertise_level", "profile_name",
                      "revision", "created_at", "updated_at"],
        "Control Vector": [k for k in flat if k.startswith("cv_")],
        "Scores": ["score", "penalty_applied", "penalty_reason", "missing_required"],
        "Layers": ["layers_populated", "num_layers"]
                  + [k for k in flat if k.startswith("layer_")],
    }

    for group_name, keys in groups.items():
        print(f"\n  [{group_name}]")
        for key in keys:
            if key in flat:
                val = flat[key]
                if isinstance(val, float):
                    print(f"    {key:30s} : {val:.4f}")
                else:
                    print(f"    {key:30s} : {val}")

    print(f"\n{SEPARATOR}")
    print(f"  Total fields: {len(flat)}")
    print(SEPARATOR)


# ── Experiment ──────────────────────────────────────────────

def cmd_experiment(args: argparse.Namespace) -> None:
    profile = args.profile or "chatbot_tutor"
    _header(
        f"Experiment  |  topic={args.topic!r}  audience={args.audience!r}"
        f"  profile={profile!r}  layers={args.layers}"
    )

    conductor = _build_conductor(args)
    runner = ExperimentRunner(conductor)

    config = ExperimentConfig(
        topic=args.topic,
        audience_id=args.audience,
        profile_name=profile,
        toggle_layers=args.layers,
    )

    report = runner.run(config)

    print(f"\n  Baseline score: {report.baseline_score:.4f}")

    for lr in report.layer_results:
        print(f"\n  --- Layer: {lr.layer} ---")
        print(f"    Enabled  score : {lr.enabled_score:.4f}")
        print(f"    Disabled score : {lr.disabled_score:.4f}")
        delta_sign = "+" if lr.score_delta >= 0 else ""
        print(f"    Delta          : {delta_sign}{lr.score_delta:.4f}")
        print(f"    Enabled layers : {lr.enabled_result.populated_layers}")
        print(f"    Disabled layers: {lr.disabled_result.populated_layers}")

    summary = ExperimentRunner.summary(report)
    print(f"\n  [Summary]")
    print(f"    Best layer  : {summary['best_layer']}")
    print(f"    Worst layer : {summary['worst_layer']}")
    print(f"    Duration    : {summary['total_duration_ms']:.0f} ms")
    for layer, delta in summary["layer_deltas"].items():
        delta_sign = "+" if delta >= 0 else ""
        print(f"    {layer:15s} : {delta_sign}{delta:.4f}")

    print(f"\n{SEPARATOR}")
    print(f"  Experiment {report.experiment_id} complete")
    print(SEPARATOR)


# ── CLI ─────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cognitive Scaffolding CLI demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # Shared arguments helper
    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--topic", required=True, help="Concept to explain")
        p.add_argument("--audience", default="general", help="Audience ID (default: general)")
        p.add_argument("--profile", default=None, help="Override the default profile")
        p.add_argument("--no-ai", action="store_true", help="Disable AI, use template fallbacks")
        p.add_argument("--provider", default=None, help="AI provider (anthropic or openai)")
        p.add_argument("--model", default=None, help="Override the default model")

    # chatbot
    p_chat = sub.add_parser("chatbot", help="Compile and format as chat messages")
    add_common(p_chat)

    # rag
    p_rag = sub.add_parser("rag", help="Compile and format as RAG document chunks")
    add_common(p_rag)

    # etl
    p_etl = sub.add_parser("etl", help="Compile and format as flat ETL record")
    add_common(p_etl)

    # experiment
    p_exp = sub.add_parser("experiment", help="Run A/B experiment on layer toggles")
    add_common(p_exp)
    p_exp.add_argument(
        "--layers", nargs="+", required=True,
        help="Layers to A/B test (e.g. metaphor encoding)",
    )

    return parser


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "chatbot": cmd_chatbot,
        "rag": cmd_rag,
        "etl": cmd_etl,
        "experiment": cmd_experiment,
    }

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
