# Architectural Decision Records

## ADR-001: CognitiveArtifact as Core IR
- **Date**: 2026-02-12
- **Status**: Accepted
- **Context**: Need a core intermediate representation for multi-layer understanding artifacts. Originally called LessonArtifact, but that implies education-only scope.
- **Decision**: Use `CognitiveArtifact` as the core IR with 7 optional layer slots (activation, metaphor, structure, interrogation, encoding, transfer, reflection). Each slot holds a `LayerOutput` with content dict, confidence float, and provenance metadata.
- **Consequences**: Broader applicability beyond education. Can serve chatbots, RAG pipelines, and ETL systems. More abstract naming may require more documentation.

## ADR-002: Option B Migration - Fat Operator Pattern
- **Date**: 2026-02-12
- **Status**: Accepted
- **Context**: Existing metaphor-mcp-server has a mature MetaphorEngine (844 lines, 200+ concepts, 18 audiences). Need to integrate without rewriting.
- **Decision**: MetaphorOperator wraps existing MetaphorEngine via import (not copy). Shared infrastructure (models, utils, data) copied into cognitive_scaffolding. Later refactoring can unify shared code into a common package.
- **Consequences**: Avoids code duplication for the engine. Requires sys.path manipulation for import. Data is duplicated (concepts, audiences, domains YAMLs). Clear migration path to common package later.
- **Backup**: Original metaphor-mcp-server backed up at `/home/robkacz/python/projects/metaphor-mcp-server-backup/`

## ADR-003: Mutable Versioning with Linear Revision History
- **Date**: 2026-02-12
- **Status**: Accepted
- **Context**: Need to track artifact changes when layers are regenerated or improved.
- **Decision**: Option 2 - Mutable artifacts with linear revision history. ArtifactRecord contains the artifact plus a list of ArtifactRevision entries tracking which layers changed, why, and score before/after.
- **Consequences**: Simple to implement. No branching complexity. Supports regeneration tracking. Cannot compare arbitrary historical states without snapshots.

## ADR-004: Feature Toggle System (3 Levels)
- **Date**: 2026-02-12
- **Status**: Accepted
- **Context**: Different integration scenarios need different layer combinations. Need flexibility without complexity.
- **Decision**: 3-level toggle system:
  1. Profile YAML defaults (per-layer enabled/required/weight)
  2. Runtime overrides (API caller can override any toggle)
  3. A/B experiments (compare scores with different toggle combinations)
- **Consequences**: Profiles cover 80% of use cases. Runtime overrides handle edge cases. Experiment system enables data-driven optimization. Toggle state must be tracked in provenance.

## ADR-005: Audience/Domain Data Injection via ConfigDict(extra="allow")
- **Date**: 2026-02-12
- **Status**: Accepted
- **Context**: Audience and domain YAMLs have many fields beyond the Pydantic model definitions (preferred_metaphors, communication_style, show_formulas, vocabulary, examples, etc.). These were silently dropped during loading, making fallback templates audience/domain-agnostic.
- **Decision**: Add `model_config = ConfigDict(extra="allow")` to Audience and Domain models. Conductor loads YAML data via DataLoader.get_audience()/get_domain(), serializes with model_dump(), and injects as `audience_data`/`domain` keys in each operator's step_config. Operators read these dicts in generate_fallback() — this augments existing concept-aware and generic branches rather than adding a third branch.
- **Consequences**: Extra YAML fields preserved without schema changes. Operators can progressively adopt audience/domain fields. No breaking changes to existing behavior (empty config still produces generic output). Domain selection cascades: explicit domain_id → audience preferred_domains → "general" fallback.

## ADR-006: Gated E2E AI Integration Tests
- **Date**: 2026-02-12
- **Status**: Accepted
- **Context**: No test validated the pipeline with a real AI client. Need to ensure AI output is valid JSON, scores higher than fallbacks, and references concept-specific content.
- **Decision**: Tests gated with `@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"))` and `@pytest.mark.slow`. Tests skip in CI and local runs without credentials. AIClient import deferred to function body to avoid import errors.
- **Consequences**: CI stays fast (tests skip). Developers with API keys can run full validation. No flaky tests from network issues in CI.
