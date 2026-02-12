"""Audience inheritance system - adapted from metaphor-mcp-server.

Handles audience inheritance and property resolution through a 3-level tree.
"""

from typing import Any, Dict, List, Optional
from cognitive_scaffolding.core.concept import Concept


class AudienceInheritance:
    """Handles audience inheritance and property resolution."""

    def __init__(self):
        self.inheritance_tree = {
            # Level 1: Base categories
            "technical": {
                "children": ["technical_workers", "academics"],
                "properties": {
                    "technical_background": "expert",
                    "show_formulas": True,
                    "complexity_preference": "high",
                    "attention_span": "long",
                },
            },
            # Level 2: Technical sub-categories
            "technical_workers": {
                "parent": "technical",
                "children": ["data_analyst", "data_scientist", "business_analyst", "ml_engineer", "genai_engineer"],
                "properties": {
                    "communication_style": "precise_detailed",
                    "show_code": True,
                    "show_proofs": "optional",
                    "benchmark_focus": "performance_metrics",
                },
            },
            "academics": {
                "parent": "technical",
                "children": [],
                "properties": {
                    "communication_style": "formal_rigorous",
                    "show_proofs": "required",
                    "show_citations": True,
                    "benchmark_focus": "academic_metrics",
                },
            },
            # Level 3: Specific technical roles
            "data_analyst": {
                "parent": "technical_workers",
                "properties": {
                    "role": "Analyze existing data to generate insights and support data-driven decision making",
                    "core_skills": ["SQL", "Excel", "Statistics", "Data_Visualization", "Python", "VBA"],
                    "primary_tools": ["SQL", "Excel", "Tableau", "PowerBI", "JIRA"],
                    "show_formulas": "basic_stats_only",
                    "show_code": "sql_python_only",
                    "show_proofs": False,
                    "benchmark_focus": "business_metrics",
                    "preferred_domains": ["data_analysis_workflows", "business_intelligence", "statistical_interpretation"],
                },
            },
            "data_scientist": {
                "parent": "technical_workers",
                "properties": {
                    "role": "Develop and implement machine learning models and algorithms",
                    "core_skills": ["Python", "R", "Machine_Learning", "Statistics", "Data_Wrangling", "Feature_Engineering"],
                    "primary_tools": ["Python", "R", "Jupyter", "TensorFlow", "PyTorch", "Scikit_learn"],
                    "show_formulas": "full_mathematical",
                    "show_code": "full_implementations",
                    "show_proofs": "mathematical_derivations",
                    "benchmark_focus": "model_performance",
                    "complexity_preference": "very_high",
                    "preferred_domains": ["statistical_learning", "experimental_design", "model_evaluation"],
                },
            },
            "business_analyst": {
                "parent": "technical_workers",
                "properties": {
                    "role": "Analyze and document business processes to identify scalability and requirements",
                    "core_skills": ["Business_Process_Modeling", "Requirements_Gathering", "Data_Analysis", "Excel"],
                    "primary_tools": ["Microsoft_Office", "Visio", "JIRA", "Confluence"],
                    "show_formulas": "business_calculations_only",
                    "show_code": False,
                    "show_proofs": False,
                    "benchmark_focus": "business_value",
                    "complexity_preference": "medium",
                    "preferred_domains": ["business_operations", "process_optimization", "workflow_analysis"],
                },
            },
            "ml_engineer": {
                "parent": "technical_workers",
                "properties": {
                    "role": "Design and deploy ML systems ensuring scalability and reliability",
                    "core_skills": ["Python", "SQL", "Data_Warehousing", "ETL", "Big_Data", "MLOps"],
                    "primary_tools": ["Python", "SQL", "Hadoop", "Spark", "Airflow", "Kubernetes", "Docker"],
                    "show_formulas": "performance_metrics",
                    "show_code": "architecture_implementations",
                    "show_proofs": "system_design_rationale",
                    "benchmark_focus": "system_performance",
                    "preferred_domains": ["system_architecture", "scalability_patterns", "infrastructure_design"],
                },
            },
            "genai_engineer": {
                "parent": "technical_workers",
                "properties": {
                    "role": "Develop and build generative AI models and applications",
                    "core_skills": ["Python", "ML", "Deep_Learning", "LLMs", "Transformers", "Prompt_Engineering"],
                    "primary_tools": ["Python", "Hugging_Face", "Transformers", "OpenAI_API", "Langchain"],
                    "show_formulas": "loss_functions_attention",
                    "show_code": "model_implementations",
                    "show_proofs": "architecture_explanations",
                    "benchmark_focus": "generation_quality",
                    "preferred_domains": ["neural_architectures", "language_modeling", "generative_systems"],
                },
            },
        }

    def resolve_audience_properties(self, audience_id: str) -> Dict[str, Any]:
        """Resolve all properties for an audience through inheritance chain."""
        if audience_id not in self.inheritance_tree:
            return {}
        resolved = {}
        chain = self._build_inheritance_chain(audience_id)
        for ancestor_id in chain:
            ancestor = self.inheritance_tree[ancestor_id]
            if "properties" in ancestor:
                resolved.update(ancestor["properties"])
        return resolved

    def _build_inheritance_chain(self, audience_id: str) -> List[str]:
        """Build inheritance chain from root to specific audience."""
        chain = []
        current_id = audience_id
        while current_id:
            chain.insert(0, current_id)
            current_node = self.inheritance_tree.get(current_id, {})
            current_id = current_node.get("parent")
        return chain

    def get_specialized_content(self, audience_id: str, concept: Concept) -> Dict[str, Any]:
        """Generate specialized content based on audience inheritance."""
        properties = self.resolve_audience_properties(audience_id)
        return {
            "code_examples": self._generate_code_examples(audience_id, concept, properties),
            "formulas": self._generate_formulas(audience_id, concept, properties),
            "benchmarks": self._generate_benchmarks(audience_id, concept, properties),
            "learning_assets": self._generate_learning_assets(audience_id, concept, properties),
        }

    def _generate_code_examples(self, audience_id: str, concept: Concept, properties: Dict) -> Optional[str]:
        show_code = properties.get("show_code", False)
        if not show_code:
            return None
        if audience_id == "data_analyst":
            return f"-- SQL example for {concept.name}\nSELECT feature_column, COUNT(*) as frequency\nFROM dataset\nWHERE {concept.name.lower().replace(' ', '_')}_applied = true\nGROUP BY feature_column;"
        elif audience_id == "data_scientist":
            return f"# Python implementation for {concept.name}\nimport numpy as np\nfrom sklearn.model_selection import train_test_split\n\ndef implement_{concept.concept_id}(X, y):\n    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)\n    return model.evaluate(X_test, y_test)"
        return f"# Code example for {concept.name} (generic)"

    def _generate_formulas(self, audience_id: str, concept: Concept, properties: Dict) -> Optional[str]:
        show_formulas = properties.get("show_formulas", False)
        if not show_formulas:
            return None
        if show_formulas == "basic_stats_only":
            return "Mean: mu = sum(x)/n | Std Dev: sigma = sqrt(sum((x-mu)^2)/n)"
        elif show_formulas in ("full_mathematical", "mathematical"):
            return f"L(theta) = argmin loss for {concept.name}"
        elif show_formulas == "business_calculations_only":
            return "ROI = (Gain - Cost) / Cost * 100%"
        return f"Mathematical foundation for {concept.name}"

    def _generate_benchmarks(self, audience_id: str, concept: Concept, properties: Dict) -> Dict[str, Any]:
        focus = properties.get("benchmark_focus", "general")
        benchmarks = {
            "business_metrics": {"productivity_gain": "15-30%", "time_savings": "2-4 hours/week"},
            "model_performance": {"accuracy": "92.5%", "f1_score": "90.5%"},
            "system_performance": {"latency": "<100ms p95", "throughput": "1000 req/s"},
        }
        return benchmarks.get(focus, {"general_metric": "Varies by implementation"})

    def _generate_learning_assets(self, audience_id: str, concept: Concept, properties: Dict) -> List[str]:
        tools = properties.get("primary_tools", [])
        assets = []
        if "SQL" in tools:
            assets.append(f"sql_examples_{concept.concept_id}.sql")
        if "Python" in tools:
            assets.append(f"notebook_{concept.concept_id}.ipynb")
        if properties.get("show_citations", False):
            assets.append(f"references_{concept.concept_id}.bib")
        return assets
