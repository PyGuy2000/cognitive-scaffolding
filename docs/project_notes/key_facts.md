# Key Facts

## Project Structure
- **Name**: Cognitive Scaffolding Layer
- **Type**: Universal understanding middleware
- **Python**: >=3.10
- **Package path**: `src/cognitive_scaffolding/`
- **Tests**: `tests/unit/`, `tests/integration/`
- **Profiles**: `profiles/` (chatbot_tutor, rag_explainer, etl_explain)
- **Data**: `data/` (216 concepts, 29 domains, 16 audiences, 4 templates)
- **GitHub**: https://github.com/PyGuy2000/cognitive-scaffolding

## Implementation Status
- **Phases 0-5**: Complete (core code, operators, orchestrator, adapters, CI, README)
- **Phase 6**: Complete (audience-aware fallbacks, domain-aware compilation, E2E AI test)
- **Phase 7**: Complete (SynthesisOperator + dashboard redesign)
- **Phase 8**: Complete (5 new cognitive layers, ConceptGraph DAG, schema-based confidence)
- **CI**: GitHub Actions — ruff + pytest on Python 3.12 (`.github/workflows/ci.yml`)
- **Tests**: 220 passing (unit + integration; 2 pre-existing AI pipeline failures, 4 AI integration gated on API key)
- **Build**: Installed in `.venv/` via `pip install -e ".[dev]"`
- **Streamlit**: `python -m streamlit run scripts/chatbot.py` (installed in venv)
- **Topic-aware fallbacks**: Operators use concept YAML data when available, generic templates otherwise
- **Audience-aware fallbacks**: All 12 content operators use audience YAML data (preferred_analogies, core_skills, show_formulas, learning_assets, etc.)
- **Domain-aware fallbacks**: Metaphor, activation, transfer, contextualization operators use domain YAML data (vocabulary, metaphor_types, examples)
- **Schema-based confidence**: All operators declare expected_keys for semantic confidence scoring (replaces length heuristic)

## Architecture
- **Core IR**: CognitiveArtifact (Pydantic BaseModel) with 13 optional LayerOutput slots (12 content + synthesis)
- **Operators**: 14 total — diagnostic, activation, contextualization, metaphor, narrative, structure, interrogation, encoding, transfer, challenge, reflection, elaboration, synthesis, grading
- **ConceptGraph**: `core/concept_graph.py` — prerequisite DAG with transitive closure, learning paths, related-concept clustering, difficulty estimation
- **Orchestrator**: CognitiveConductor.compile() - loads profile → builds CallPlan → executes operators → scores
- **Adapters**: ChatbotAdapter (chat messages), RAGAdapter (document chunks), ETLAdapter (flat dict)
- **Toggle system**: Profile YAML → Runtime overrides → A/B experiments

## Key Files
- `src/cognitive_scaffolding/core/models.py` — All Pydantic data models (LayerName enum, CognitiveArtifact, AudienceProfile, etc.)
- `src/cognitive_scaffolding/core/scoring.py` — Weighted scoring formula
- `src/cognitive_scaffolding/core/data_loader.py` — YAML data loader for concepts, audiences, domains
- `src/cognitive_scaffolding/core/concept_graph.py` — ConceptGraph DAG (prerequisites, learning paths, difficulty estimation)
- `src/cognitive_scaffolding/operators/base.py` — BaseOperator ABC with schema-based confidence estimation
- `src/cognitive_scaffolding/operators/diagnostic.py` — Pre-assessment (knowledge gaps, recommended depth)
- `src/cognitive_scaffolding/operators/contextualization.py` — Big-picture context (field landscape, trends, adjacencies)
- `src/cognitive_scaffolding/operators/narrative.py` — Story-based explanation (characters, conflict, resolution)
- `src/cognitive_scaffolding/operators/challenge.py` — Bloom's taxonomy challenges (calibrated to expertise + cognitive_load)
- `src/cognitive_scaffolding/operators/elaboration.py` — Deep-dive subtopics (selected by diagnostic gaps)
- `src/cognitive_scaffolding/orchestrator/conductor.py` — Main compilation loop (loads concept/audience/domain data, injects into operators)
- `src/cognitive_scaffolding/orchestrator/toggle_manager.py` — Feature toggle system
- `src/cognitive_scaffolding/orchestrator/regeneration.py` — Targeted re-run of weak layers
- `scripts/demo.py` — CLI demo (compile, experiment, --regenerate, --domain)

## Dependencies
- pydantic>=2.0.0
- PyYAML>=6.0
- anthropic>=0.8.0
- openai>=1.0.0
- python-dotenv>=1.0.0

## Related Projects
- **metaphor-mcp-server**: `/home/robkacz/python/projects/metaphor-mcp-server/`
  - MetaphorEngine referenced via sys.path import in MetaphorOperator (currently fails — see ADR-007)
  - Models, utils, data copied (not linked) into cognitive_scaffolding
  - MCP has: 215 concepts, 29 domains, 16 audiences, 14 explanation styles, audience inheritance, Manim/D3/Mermaid visual generation, multi-domain metaphor comparison
  - `mcp` package now installed in cognitive_scaffolding venv (dependency resolved)
  - MetaphorEngine constructor requires `data_dir` param — the sys.path import in MetaphorOperator doesn't pass it
- **Backup**: `/home/robkacz/python/projects/metaphor-mcp-server-backup/`

## Scoring Formula
- Score = sum(w_k * x_k) / sum(w_k)
- Disabled layers excluded from denominator
- Required but empty layers: 0.7 penalty multiplier (REQUIRED_PENALTY constant)

## Audience Control Vector (7D)
- language_level, abstraction, rigor, math_density, domain_specificity, cognitive_load, transfer_distance
- Each dimension: 0.0 to 1.0
- DEFAULT_VECTORS in conductor.py: child, general, data_scientist, phd

## Build Notes
- pyproject.toml readme now points to README.md
- hatchling build backend, wheel packages = ["src/cognitive_scaffolding"]
- pytest configured with testpaths=["tests"], pythonpath=["src"]
