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
