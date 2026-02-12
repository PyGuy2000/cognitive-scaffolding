# Key Facts

## Project Structure
- **Name**: Cognitive Scaffolding Layer
- **Type**: Universal understanding middleware
- **Python**: >=3.10
- **Package path**: `src/cognitive_scaffolding/`
- **Tests**: `tests/unit/`, `tests/integration/`
- **Profiles**: `profiles/` (chatbot_tutor, rag_explainer, etl_explain)
- **Data**: `data/` (218 concepts, 29 domains, 16 audiences)

## Architecture
- **Core IR**: CognitiveArtifact with 7 optional layer slots
- **Operators**: 8 total (activation, metaphor, structure, interrogation, encoding, transfer, reflection, grading)
- **Orchestrator**: CognitiveConductor compiles artifacts via call plans
- **Adapters**: ChatbotAdapter, RAGAdapter, ETLAdapter
- **Toggle system**: Profile YAML → Runtime overrides → A/B experiments

## Dependencies
- pydantic>=2.0.0
- PyYAML>=6.0
- anthropic>=0.8.0
- openai>=1.0.0
- python-dotenv>=1.0.0

## Related Projects
- **metaphor-mcp-server**: `/home/robkacz/python/projects/metaphor-mcp-server/`
  - MetaphorEngine referenced via import in MetaphorOperator
  - Models, utils, data copied (not linked) into cognitive_scaffolding
- **Backup**: `/home/robkacz/python/projects/metaphor-mcp-server-backup/`

## Scoring Formula
- Score = sum(w_k * x_k) / sum(w_k)
- Disabled layers excluded from denominator
- Required but empty layers: 0.7 penalty multiplier

## Audience Control Vector (7D)
- (l, a, r, m, d, k, t) = language_level, abstraction, rigor, math_density, domain_specificity, cognitive_load, transfer_distance
- Each dimension: 0.0 to 1.0
