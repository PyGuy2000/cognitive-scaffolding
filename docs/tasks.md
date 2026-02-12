# Cognitive Scaffolding - Task List

## Phase 0: Foundation (Project Scaffold, Core Models, Scoring, Toggles) ✅

- [x] Create directory structure: `src/cognitive_scaffolding/{core,operators,orchestrator,schemas,adapters}`, `utils/`, `profiles/`, `data/`, `tests/{unit,integration}`
- [x] Write `pyproject.toml` with dependencies (pydantic, PyYAML, anthropic, openai, python-dotenv)
- [x] Copy data YAMLs from metaphor-mcp-server (218 concepts, 29 domains, 16 audiences, templates)
- [x] `core/models.py`: CognitiveArtifact, AudienceProfile, AudienceControlVector, LayerOutput, EvaluationResult, ArtifactRevision, ArtifactRecord
- [x] Migrate shared models from metaphor MCP: Audience → `core/audience.py`, Concept → `core/concept.py`, Domain → `core/domain.py`
- [x] Migrate shared utils: AIClient → `utils/ai_client.py`, cache → `utils/cache.py`, file_utils → `utils/yaml_utils.py`
- [x] Migrate AudienceInheritance → `core/audience_inheritance.py`
- [x] Build `core/scoring.py` - weighted scoring with penalty for missing required layers
- [x] Build `orchestrator/toggle_manager.py` - 3-level feature toggle system
- [x] Build `core/data_loader.py` - YAML loading for concepts, audiences, domains
- [x] Write profile YAMLs: `profiles/chatbot_tutor.yaml`, `profiles/rag_explainer.yaml`, `profiles/etl_explain.yaml`
- [x] Unit tests for models, scoring, toggles

**Exit criteria**: ✅ `pytest tests/unit/` passes — 30 unit tests green.

---

## Phase 1: Operator Framework + First 2 Operators ✅

- [x] `operators/base.py`: BaseOperator ABC with `execute(topic, audience, context, ai_client)`, `build_prompt(topic, audience, context)`, `parse_output(raw)`, `estimate_confidence(output)`, `generate_fallback(topic, audience, context)`
- [x] `operators/metaphor.py`: MetaphorOperator wrapping existing MetaphorEngine from metaphor-mcp-server via sys.path import
- [x] `operators/activation.py`: ActivationOperator generating hooks, curiosity gaps, stakes, emotional triggers via LLM
- [x] `orchestrator/call_plan.py`: CallPlan with `from_layer_configs()` - builds ordered operator steps
- [x] `orchestrator/provenance.py`: ProvenanceTracker - records operator, timestamps, model, token usage
- [x] Unit tests for both operators (mock AI client)

**Exit criteria**: ✅ Both operators produce valid LayerOutput independently.

---

## Phase 2: Remaining 6 Operators ✅

- [x] `operators/structure.py` - StructureOperator: definitions, taxonomies, diagrams, formal notation
- [x] `operators/interrogation.py` - InterrogationOperator: Socratic questions, counterexamples, misconception probes, edge cases
- [x] `operators/encoding.py` - EncodingOperator: mnemonics, spaced repetition, chunking, retrieval cues
- [x] `operators/transfer.py` - TransferOperator: worked examples, problem sets, simulations, real-world applications
- [x] `operators/reflection.py` - ReflectionOperator: calibration, metacognitive checks, misconception detection
- [x] `operators/grading.py` - GradingOperator: rubric scoring, diagnostics, gap analysis, revision planning
- [x] Unit tests for each operator (mock AI client)

**Exit criteria**: ✅ All 8 operators produce valid LayerOutput independently — 9 operator tests green.

---

## Phase 3: Conductor + End-to-End Pipeline ✅

- [x] `orchestrator/conductor.py`: CognitiveConductor with `compile(topic, audience_id, profile_name, overrides)` method
  - Loads profile → builds CallPlan → executes operators in sequence → accumulates context → scores result
  - Context dict grows with each operator's output, passed to next operator
  - Dynamic operator import via `_get_operator()` with caching
  - DEFAULT_VECTORS for child, general, data_scientist, phd audiences
- [x] `orchestrator/regeneration.py`: `regenerate_weak_layers()` with configurable threshold (default 0.5)
- [x] Integration test: full compile with mock AI client
  - Verified all enabled layers populated, score computed correctly, provenance tracked

**Exit criteria**: ✅ `compile()` produces a scored ArtifactRecord with all enabled layers populated — 4 integration tests green.

---

## Phase 4: Adapters + Integration Tests ✅

- [x] `adapters/base.py`: BaseAdapter ABC with `format(artifact, audience)` method
- [x] `adapters/chatbot_adapter.py`: ChatbotAdapter - formats as list of dicts with role, content, layer, confidence, metadata
- [x] `adapters/rag_adapter.py`: RAGAdapter - formats as list of document chunks with chunk_id, content, metadata
- [x] `adapters/etl_adapter.py`: ETLAdapter - formats as flat dict with cv_* fields, layer_*_populated, layer_*_confidence
- [x] Integration tests: chatbot, RAG, and ETL pipelines tested in `test_pipeline.py`

**Exit criteria**: ✅ All 3 adapter formats validated in integration tests.

---

## Phase 5: Toggle Experiments + Documentation 🔲 (Partial)

- [x] Experiment runner: compare scores with different toggle combinations
  - Same topic, same audience, different enabled layers → measure score delta
- [x] Log ADRs in `docs/project_notes/decisions.md` (ADR-001 through ADR-004)
- [x] Update `docs/project_notes/key_facts.md`
- [x] PRD written and aligned with implementation (`docs/PRD.md`)
- [ ] Usage documentation / README

**Exit criteria**: Can demonstrate measurable score impact from toggling layers on/off.

---

## Summary

| Phase | Status | Tests |
|-------|--------|-------|
| 0 - Foundation | ✅ Complete | 21 unit tests |
| 1 - Operator Framework | ✅ Complete | (included in operator tests) |
| 2 - Remaining Operators | ✅ Complete | 9 operator tests |
| 3 - Conductor Pipeline | ✅ Complete | 4 integration tests |
| 4 - Adapters | ✅ Complete | (included in integration tests) |
| 5 - Experiments & Docs | 🔲 Partial (runner done) | 5 experiment tests |
| **Total** | **Phases 0-4 complete, Phase 5 runner done** | **39 tests passing** |

---

## Key Architecture Invariants

1. Operators never communicate directly - conductor maintains shared context dict
2. MetaphorOperator wraps existing engine via import, not copy
3. Disabled layers excluded from scoring denominator
4. Required but empty layers trigger 0.7 penalty multiplier
5. Data lives in cognitive_scaffolding/data/ (copied from metaphor MCP)
