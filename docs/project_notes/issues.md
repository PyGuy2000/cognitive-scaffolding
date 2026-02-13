# Work Log

Track completed work, in-progress tasks, and ticket references.

---

### 2026-02-12 - Initial Implementation: Phases 0-4
- **Status**: Completed
- **Description**: Built full cognitive scaffolding layer — core models, 8 operators, orchestrator with conductor/toggle manager/call plan/provenance/regeneration, 3 adapters, 3 profiles, and 34 passing tests. Migrated shared code from metaphor-mcp-server.
- **URL**: https://github.com/PyGuy2000/cognitive-scaffolding
- **Notes**: Built via parallel agent team (9 agents). All code Pydantic v2 BaseModel.

### 2026-02-12 - PRD Cleanup and Alignment
- **Status**: Completed
- **Description**: Rewrote `docs/PRD.md` to match actual implementation. Original PRD had many discrepancies (wrong method signatures, dataclass vs Pydantic, aspirational features, wrong override format). Rewritten from 1320 to ~850 lines.
- **Notes**: Status changed from "Draft" to "Implemented".

### 2026-02-12 - Git Init and GitHub Push
- **Status**: Completed
- **Description**: Initialized git repo, created `.gitignore`, made initial commit (324 files, 16,671 insertions), created public GitHub repo, pushed.
- **URL**: https://github.com/PyGuy2000/cognitive-scaffolding

### 2026-02-12 - CI, Adapter Tests, Regeneration CLI, Topic-Aware Fallbacks
- **Status**: Completed
- **Description**: Added GitHub Actions CI (ruff + pytest), adapter unit tests (22 tests for ChatbotAdapter/RAGAdapter/ETLAdapter), regeneration tests (5 tests) + `--regenerate`/`--regen-threshold` CLI flags, and topic-aware fallback templates (all 7 operators use concept YAML data when available, 28 tests). Fixed all pre-existing ruff lint errors. Test count: 43 → 98.
- **URL**: https://github.com/PyGuy2000/cognitive-scaffolding

### 2026-02-12 - README and Project Notes Update
- **Status**: Completed
- **Description**: Created README.md with architecture overview, quickstart, CLI usage, and project structure. Updated key_facts.md and issues.md to reflect current state (98 tests, CI green, Phase 5 complete).

### 2026-02-12 - Audience-Aware Fallbacks, Domain-Aware Compilation, E2E AI Test
- **Status**: Completed
- **Description**: Three enhancements shipped in one commit (`51c3a51`):
  1. **Audience-aware fallbacks** — Added `ConfigDict(extra="allow")` to Audience model. Conductor loads audience YAML data and injects into all 7 operators. Each operator's `generate_fallback()` uses audience fields (preferred_analogies, core_skills, show_formulas, learning_assets, attention_span, preferred_domains, primary_tools, communication_style, complexity_preference) to personalize output.
  2. **Domain-aware compilation** — Added `ConfigDict(extra="allow")` to Domain model. Conductor accepts `domain_id` param with cascading selection (explicit → audience preferred_domains → "general"). Domain data (vocabulary, metaphor_types, examples) enriches metaphor, activation, and transfer operators. Added `--domain` CLI flag to demo.py.
  3. **E2E AI integration test** — Gated on `ANTHROPIC_API_KEY`, marked `@slow`. 4 tests: valid artifact, AI >= fallback score, richer content, concept-specific terms.
- **Test count**: 98 → 128 (21 audience + 9 domain + 4 AI integration, minus 4 skipped when no API key)
- **URL**: https://github.com/PyGuy2000/cognitive-scaffolding

### 2026-02-12 - Synthesis Operator + Dashboard Redesign
- **Status**: Completed
- **Description**: Added SynthesisOperator (Layer 8) that reads all 7 layer outputs and produces one unified response. Redesigned Streamlit chatbot dashboard with side-by-side comparison: scaffolded synthesis (left) vs raw LLM baseline (right). Layer details moved to expander. Removed old comparison toggle.
- **Files changed**: models.py (SYNTHESIS enum + slot), operators/synthesis.py (new), call_plan.py, chatbot_adapter.py, scripts/chatbot.py, 3 profile YAMLs, test_operators.py, test_adapters.py, test_regeneration.py
- **Test count**: 128 → 131 (3 new SynthesisOperator tests + 2 existing tests updated for 8th layer)
- **URL**: https://github.com/PyGuy2000/cognitive-scaffolding

### 2026-02-12 - MCP Engine Analysis: What's Missing
- **Status**: Analysis complete (no code changes)
- **Description**: Installed `mcp` package and ran the metaphor-mcp-server MetaphorEngine with live AI to compare output quality. Documented gaps between MCP engine capabilities and cognitive_scaffolding MetaphorOperator. See ADR-007 for recommendations.
- **Key findings**:
  - MCP engine has 29 domains, 215 concepts, 16 audiences, 14 explanation styles, audience inheritance, visual generation (Manim/D3/Mermaid), multi-domain comparison
  - Domain ranking is broken (flat scores, no differentiation) — bug in MCP server
  - AI-generated metaphor prose quality is comparable (same LLM), but MCP injects richer context
  - MCP has zero fallback when AI is unavailable; cognitive_scaffolding handles this better

### 2026-02-13 - Feature Strengthening: New Layers, ConceptGraph, Schema Confidence
- **Status**: Completed
- **Description**: Implemented the feature strengthening plan from the gap analysis. Three categories of improvements shipped in one commit (`b3113ef`):
  1. **Schema-based confidence (C1)** — Replaced length heuristic in BaseOperator.estimate_confidence() with schema-aware scoring. Each operator declares `expected_keys` list. Confidence = 40% keys present + 40% non-empty values + 20% content richness. Legacy fallback preserved for operators without expected_keys (GradingOperator).
  2. **Concept Prerequisite DAG (D1)** — New `core/concept_graph.py` with ConceptGraph class. Uses Python's `graphlib.TopologicalSorter` for topological ordering. Methods: get_prerequisites() (transitive DFS), get_learning_path() (topo sort), get_related_cluster() (BFS with max_depth), estimate_difficulty() (60% depth + 40% count), get_dependents() (reverse lookup), cycle detection.
  3. **Five new cognitive layers (A1-A5)** — DiagnosticOperator (pre-assessment with expertise mapping), ContextualizationOperator (big picture using evolution_rate/category/related_concepts), NarrativeOperator (story with audience-adapted characters), ChallengeOperator (Bloom's taxonomy calibrated by diagnostic gaps + cognitive_load), ElaborationOperator (deep-dive into subtopics selected by diagnostic gaps).
- **Cross-cutting updates**: LayerName enum (8→13), CognitiveArtifact (5 new slots), all 3 profile YAMLs (new layers default disabled except diagnostic in chatbot_tutor), SynthesisOperator (integrates all new layers), ChatbotAdapter (5 new format methods), GradingOperator (expected_layers list expanded), CallPlan (5 new operator mappings), all 7 existing operators (added expected_keys).
- **Test count**: 131 → 220 (89 new tests across 3 new test files: test_new_operators.py, test_concept_graph.py, test_new_fallback_enrichment.py)
- **Known issue**: 2 pre-existing AI pipeline test failures — test_ai_pipeline.py passes strings instead of LayerName enums to get_layer()
- **URL**: https://github.com/PyGuy2000/cognitive-scaffolding
