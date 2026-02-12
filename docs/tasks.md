# Cognitive Scaffolding - Task List

## Phase 0: Foundation (Project Scaffold, Core Models, Scoring, Toggles)

### Completed
- [x] Create directory structure: `src/cognitive_scaffolding/{core,operators,orchestrator,schemas,adapters}`, `utils/`, `profiles/`, `data/`, `tests/{unit,integration}`
- [x] Write `pyproject.toml` with dependencies (pydantic, PyYAML, anthropic, openai, python-dotenv)
- [x] Copy data YAMLs from metaphor-mcp-server (218 concepts, 29 domains, 16 audiences, templates)

### In Progress
- [ ] `core/models.py`: CognitiveArtifact, AudienceProfile, AudienceControlVector, LayerOutput, EvaluationResult, ArtifactRevision, ArtifactRecord
- [ ] Migrate shared models from metaphor MCP: Audience → `core/audience.py`, Concept → `core/concept.py`, Domain → `core/domain.py`
- [ ] Migrate shared utils: AIClient → `utils/ai_client.py`, cache → `utils/cache.py`, file_utils → `utils/yaml_utils.py`
- [ ] Migrate AudienceInheritance → `core/audience_inheritance.py`
- [ ] Build `core/scoring.py` - weighted scoring with penalty for missing required layers
- [ ] Build `orchestrator/toggle_manager.py` - 3-level feature toggle system
- [ ] Build `core/data_loader.py` - YAML loading for concepts, audiences, domains
- [ ] Write profile YAMLs: `profiles/chatbot_tutor.yaml`, `profiles/rag_explainer.yaml`, `profiles/etl_explain.yaml`
- [ ] Unit tests for models, scoring, toggles

**Exit criteria**: `pytest tests/unit/` passes with core model, scoring, and toggle tests green.

---

## Phase 1: Operator Framework + First 2 Operators

- [ ] `operators/base.py`: BaseOperator ABC with `execute(topic, audience, context, config)`, `build_prompt(topic, audience, context)`, `validate_output(raw_output)`
- [ ] `operators/metaphor.py`: MetaphorOperator wrapping existing MetaphorEngine from metaphor-mcp-server via import
- [ ] `operators/activation.py`: ActivationOperator generating hooks, curiosity gaps, stakes, emotional triggers via LLM
- [ ] JSON schemas for activation and metaphor operator outputs in `schemas/`
- [ ] `orchestrator/call_plan.py`: CallPlan model - ordered list of operators to execute with configs
- [ ] `orchestrator/provenance.py`: ProvenanceTracker - records which operator produced what, with timestamps
- [ ] Unit tests for both operators (mock AI client)

**Exit criteria**: Both operators produce valid LayerOutput independently when tested with mock AI.

---

## Phase 2: Remaining 6 Operators

- [ ] `operators/structure.py` - StructureOperator: definitions, taxonomies, diagrams, formal notation
- [ ] `operators/interrogation.py` - InterrogationOperator: Socratic questions, counterexamples, misconception probes, edge cases
- [ ] `operators/encoding.py` - EncodingOperator: mnemonics, spaced repetition, chunking, retrieval cues
- [ ] `operators/transfer.py` - TransferOperator: worked examples, problem sets, simulations, real-world applications
- [ ] `operators/reflection.py` - ReflectionOperator: calibration, metacognitive checks, misconception detection
- [ ] `operators/grading.py` - GradingOperator: rubric scoring, diagnostics, gap analysis, revision planning
- [ ] JSON schemas for all 6 operators in `schemas/`
- [ ] Unit tests for each operator (mock AI client)

**Exit criteria**: All 8 operators produce valid LayerOutput independently.

---

## Phase 3: Conductor + End-to-End Pipeline

- [ ] `orchestrator/conductor.py`: CognitiveConductor with `compile(topic, audience_id, profile_name, overrides)` method
  - Loads profile → builds CallPlan → executes operators in sequence → accumulates context → scores result
  - Context dict grows with each operator's output, passed to next operator
- [ ] `orchestrator/regeneration.py`: targeted re-run of weak layers (below threshold)
- [ ] Integration test: full compile with mock AI client
  - Test: `compile("ancillary services", "child", "chatbot_tutor")` produces scored ArtifactRecord
  - Verify all enabled layers populated, score computed correctly, provenance tracked

**Exit criteria**: `compile("ancillary services", child, "chatbot_tutor")` produces a scored ArtifactRecord with all enabled layers populated.

---

## Phase 4: Adapters + Integration Tests

- [ ] `adapters/base.py`: BaseAdapter ABC with `format(artifact)` method
- [ ] `adapters/chatbot_adapter.py`: ChatbotAdapter - formats as streaming chat messages with progressive disclosure
- [ ] `adapters/rag_adapter.py`: RAGAdapter - formats as enriched document chunks with metadata for vector stores
- [ ] `adapters/etl_adapter.py`: ETLAdapter - formats as structured records for data pipelines
- [ ] Integration test: chatbot pipeline (compile + ChatbotAdapter.format → chat messages)
- [ ] Integration test: RAG pipeline (compile + RAGAdapter.format → document chunks)
- [ ] Integration test: ETL pipeline (compile + ETLAdapter.format → structured records)

**Exit criteria**: All 3 integration suites pass with correct output formats.

---

## Phase 5: Toggle Experiments + Documentation

- [ ] Experiment runner: compare scores with different toggle combinations
  - Same topic, same audience, different enabled layers → measure score delta
- [ ] Log ADRs in `docs/project_notes/decisions.md`
  - ADR-001: CognitiveArtifact as core IR
  - ADR-002: Option B migration (fat operator wrapping metaphor engine)
  - ADR-003: Option 2 versioning (mutable with linear revision history)
  - ADR-004: Feature toggle system (3 levels)
- [ ] Update `docs/project_notes/key_facts.md`
- [ ] Usage documentation in README or docs/

**Exit criteria**: Can demonstrate measurable score impact from toggling layers on/off.

---

## Dependency Graph

```
Phase 0 ──→ Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 4 ──→ Phase 5
(foundation)  (framework)  (operators)  (conductor)  (adapters)  (experiments)
```

## Key Architecture Invariants

1. Operators never communicate directly - conductor maintains shared context dict
2. MetaphorOperator wraps existing engine via import, not copy
3. Disabled layers excluded from scoring denominator
4. Required but empty layers trigger 0.7 penalty multiplier
5. Data lives in cognitive_scaffolding/data/ (copied from metaphor MCP)
