# Key Facts

## Project Structure
- **Name**: Cognitive Scaffolding Layer
- **Type**: Universal understanding middleware
- **Python**: >=3.10
- **Package path**: `src/cognitive_scaffolding/`
- **Tests**: `tests/unit/`, `tests/integration/`
- **Profiles**: `profiles/` (chatbot_tutor, rag_explainer, etl_explain)
- **Data**: `data/` (218 concepts, 29 domains, 16 audiences, 4 templates)
- **GitHub**: https://github.com/PyGuy2000/cognitive-scaffolding

## Implementation Status
- **Phases 0-4**: Complete (all core code, operators, orchestrator, adapters)
- **Phase 5**: Partial (ADRs done, experiment runner and README pending)
- **Tests**: 34/34 passing (30 unit + 4 integration)
- **Build**: Installed in `.venv/` via `pip install -e ".[dev]"`

## Architecture
- **Core IR**: CognitiveArtifact (Pydantic BaseModel) with 7 optional LayerOutput slots
- **Operators**: 8 total (activation, metaphor, structure, interrogation, encoding, transfer, reflection, grading)
- **Orchestrator**: CognitiveConductor.compile() - loads profile → builds CallPlan → executes operators → scores
- **Adapters**: ChatbotAdapter (chat messages), RAGAdapter (document chunks), ETLAdapter (flat dict)
- **Toggle system**: Profile YAML → Runtime overrides → A/B experiments

## Key Files
- `src/cognitive_scaffolding/core/models.py` — All Pydantic data models
- `src/cognitive_scaffolding/core/scoring.py` — Weighted scoring formula
- `src/cognitive_scaffolding/operators/base.py` — BaseOperator ABC
- `src/cognitive_scaffolding/orchestrator/conductor.py` — Main compilation loop
- `src/cognitive_scaffolding/orchestrator/toggle_manager.py` — Feature toggle system

## Dependencies
- pydantic>=2.0.0
- PyYAML>=6.0
- anthropic>=0.8.0
- openai>=1.0.0
- python-dotenv>=1.0.0

## Related Projects
- **metaphor-mcp-server**: `/home/robkacz/python/projects/metaphor-mcp-server/`
  - MetaphorEngine referenced via sys.path import in MetaphorOperator
  - Models, utils, data copied (not linked) into cognitive_scaffolding
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
- pyproject.toml uses inline readme text (not README.md file) to avoid build errors
- hatchling build backend, wheel packages = ["src/cognitive_scaffolding"]
- pytest configured with testpaths=["tests"], pythonpath=["src"]
