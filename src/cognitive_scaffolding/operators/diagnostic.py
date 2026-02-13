"""Diagnostic operator - Pre-assessment layer.

Runs before Activation. Reads concept prerequisites + audience expertise to
assess what the learner already knows, identify prerequisite gaps, and
recommend appropriate depth. Downstream operators read context["diagnostic"]
to adjust their behavior.
"""

import json
from typing import Any, Dict

from cognitive_scaffolding.core.models import AudienceProfile, LayerName
from cognitive_scaffolding.operators.base import BaseOperator


# Expertise level ordering for comparison
_EXPERTISE_LEVELS = {
    "beginner": 0,
    "intermediate": 1,
    "advanced": 2,
    "expert": 3,
}


class DiagnosticOperator(BaseOperator):
    """Pre-assesses learner knowledge to calibrate downstream operators."""

    layer_name = LayerName.DIAGNOSTIC
    expected_keys = [
        "knowledge_assessment", "prerequisite_gaps", "recommended_depth",
        "skip_basics", "estimated_familiarity",
    ]

    def build_prompt(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        cv = audience.control_vector
        concept = config.get("concept", {})
        prereqs = concept.get("prerequisite_concepts", []) if concept else []
        complexity = concept.get("complexity", "medium") if concept else "medium"

        prereqs_text = f"\nPrerequisite concepts: {', '.join(p.replace('_', ' ') for p in prereqs)}" if prereqs else ""

        return f"""Perform a diagnostic pre-assessment for the topic "{topic}".

Target audience: {audience.name} (expertise: {audience.expertise_level})
Language level: {cv.language_level:.1f}, Cognitive load: {cv.cognitive_load:.1f}
Topic complexity: {complexity}
{prereqs_text}

Produce a JSON object with:
- "knowledge_assessment": Dict mapping each prerequisite to an estimated mastery level ("none", "basic", "solid", "expert")
- "prerequisite_gaps": List of prerequisite concepts the audience likely lacks
- "recommended_depth": One of "introductory", "intermediate", "advanced", "expert"
- "skip_basics": Boolean - whether to skip basic explanations
- "estimated_familiarity": Float 0-1 estimating how familiar the audience is with this topic

Return ONLY valid JSON, no markdown."""

    def generate_fallback(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        concept = config.get("concept")
        aud = config.get("audience_data")
        expertise = audience.expertise_level

        expertise_num = _EXPERTISE_LEVELS.get(expertise, 1)

        prereqs = []
        complexity = "medium"
        if concept:
            prereqs = concept.get("prerequisite_concepts", [])
            complexity = concept.get("complexity", "medium")

        # Estimate prerequisite mastery based on audience expertise
        knowledge_assessment = {}
        prerequisite_gaps = []
        for prereq in prereqs:
            prereq_name = prereq.replace("_", " ")
            if expertise_num >= 3:  # expert
                knowledge_assessment[prereq_name] = "expert"
            elif expertise_num >= 2:  # advanced
                knowledge_assessment[prereq_name] = "solid"
            elif expertise_num >= 1:  # intermediate
                knowledge_assessment[prereq_name] = "basic"
            else:  # beginner
                knowledge_assessment[prereq_name] = "none"
                prerequisite_gaps.append(prereq_name)

        # Add gaps for beginners/intermediates on complex topics
        if expertise_num <= 1 and complexity in ("high", "advanced"):
            for prereq in prereqs:
                pn = prereq.replace("_", " ")
                if pn not in prerequisite_gaps:
                    prerequisite_gaps.append(pn)

        # Recommended depth mapping
        depth_map = {
            "beginner": "introductory",
            "intermediate": "intermediate",
            "advanced": "advanced",
            "expert": "expert",
        }
        recommended_depth = depth_map.get(expertise, "intermediate")

        # Adjust depth based on topic complexity
        if complexity in ("basic", "simple") and expertise_num >= 2:
            recommended_depth = "advanced"
        elif complexity in ("high", "advanced") and expertise_num <= 1:
            recommended_depth = "introductory"

        # Skip basics for advanced+ audiences on non-complex topics
        skip_basics = expertise_num >= 2 and complexity not in ("high", "advanced")

        # Familiarity estimate
        familiarity_base = {0: 0.1, 1: 0.3, 2: 0.6, 3: 0.85}
        familiarity = familiarity_base.get(expertise_num, 0.3)

        # Adjust for audience-specific indicators
        if aud:
            preferred_domains = aud.get("preferred_domains") or []
            category = (concept.get("category", "") if concept else "").replace("_", " ")
            if any(category in d.replace("_", " ") for d in preferred_domains):
                familiarity = min(1.0, familiarity + 0.15)

        return json.dumps({
            "knowledge_assessment": knowledge_assessment,
            "prerequisite_gaps": prerequisite_gaps,
            "recommended_depth": recommended_depth,
            "skip_basics": skip_basics,
            "estimated_familiarity": round(familiarity, 2),
        })
