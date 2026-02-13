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

## ADR-007: MCP Engine Integration — Gap Analysis and Recommendations
- **Date**: 2026-02-12
- **Status**: Proposed
- **Context**: The metaphor-mcp-server has substantial capabilities that are not used by the cognitive_scaffolding MetaphorOperator. A live comparison was performed with both systems running against the same LLM (Claude Sonnet). The `sys.path` import hack in MetaphorOperator (line 20) fails because MetaphorEngine now requires a `data_dir` argument, so the MCP engine path is dead code.

### Gap Analysis

**What the MCP engine has that cognitive_scaffolding does not use:**
1. **14 explanation styles** — extended_metaphor, progressive_revelation, misconception_decoder, narrative_journey, etc. with context-aware selection based on expertise, time, and learning objective. *High value.* No equivalent exists in any CS operator.
2. **Multi-domain metaphor comparison** — `compare_metaphor_approaches()` generates the same concept across N domains and ranks them. *High value.* Lets the system present the best metaphor, not just the first one.
3. **Audience inheritance hierarchy** — data_scientist inherits from technical_workers inherits from technical, cascading show_formulas, show_code, benchmark_focus, etc. *Medium value.* CS has flat audience profiles with extra fields, which works but doesn't scale well for specialized roles.
4. **Domain fitness scoring** — scores each domain against concept category, audience preferences, and complexity. *Medium value but currently broken* — ranking returns flat scores for all domains (bug in MCP server).
5. **Dynamic concept analysis** — LLM-based analysis of any concept for abstractness, complexity, field classification. *Low-medium value.* CS already passes concept YAML data to operators; dynamic analysis adds value only for concepts not in the YAML library.
6. **Visual generation** — Manim scripts, D3.js, Mermaid diagrams per domain. *Low priority for current use cases.* Would matter if building visual learning tools.

**What cognitive_scaffolding does better:**
- Template fallbacks — every operator produces useful output without AI. MCP returns empty fallback messages.
- Scoring and evaluation — weighted per-layer scoring with penalty system. MCP has no self-evaluation.
- Multi-layer integration — 7 content layers + synthesis + grading. MCP only covers metaphor.
- Revision tracking — ArtifactRecord with linear revision history.

### Recommendation: Selective Extraction (Not Full Integration)

Do **not** connect to the MCP server at runtime or fix the sys.path import. Instead, extract specific high-value logic into the cognitive_scaffolding operators as native Python:

1. **Style selection matrix** (HIGH priority) — Extract the 14-style selection logic from `metaphor-mcp-server/data/templates/` and `metaphor_engine.py`. This would benefit **all 7 operators**, not just metaphor. Each operator could vary its output structure based on style (e.g., progressive_revelation for activation, misconception_decoder for interrogation). Implement as a shared utility or a style parameter in BaseOperator.

2. **Multi-domain metaphor comparison** (HIGH priority) — Add a `compare_domains()` method to MetaphorOperator that generates metaphors for 2-3 top domains and picks the best. The domain selection logic itself is simple (concept category → suitable domains), and the comparison is just N parallel LLM calls. Can be implemented without any MCP dependency.

3. **Audience inheritance** (MEDIUM priority) — Add a parent field to audience YAMLs and a simple inheritance resolver in DataLoader. The MCP's `audience_inheritance.py` is ~200 lines and could be adapted. This would let the 16 audience profiles share base properties cleanly instead of repeating fields.

4. **Fix domain ranking** (MEDIUM priority) — The MCP's domain ranking is broken (flat scores), but the *concept* of scoring domains by (concept_category, audience_preferences, complexity_match) is sound. Implement a clean version in MetaphorOperator or DataLoader using the existing domain YAML metadata (suitable_for, metaphor_types).

5. **Dynamic concept analysis** (LOW priority) — Only matters for topics not in the 215 concept YAMLs. The SynthesisOperator and AI-backed operators already handle unknown topics via LLM prompts.

6. **Visual generation** (DEFER) — Manim/D3/Mermaid generation is useful but orthogonal to the core scaffolding pipeline. Add only if building a visual learning product.

### Rationale for extraction over integration
- The MCP server has a different AI client, different models, different error handling. Bridging them adds coupling.
- The valuable logic (style selection, domain scoring, audience inheritance) is algorithmic — it doesn't need the MCP protocol or server infrastructure.
- Extraction lets us add proper fallbacks (which the MCP lacks) and integrate with the existing scoring system.
- The sys.path hack is fragile and creates namespace collisions (both projects have `utils.ai_client`).

### Consequence
- Remove the dead sys.path import from MetaphorOperator (lines 17-27) and the engine parameter
- Extract style selection, domain comparison, and audience inheritance as native features over subsequent sessions
- The metaphor-mcp-server remains a standalone tool for Claude Desktop use — it doesn't need to be coupled to this project

## ADR-008: Schema-Based Confidence Estimation (C1)
- **Date**: 2026-02-13
- **Status**: Accepted
- **Context**: `estimate_confidence()` in BaseOperator used a crude length heuristic — a 500-character nonsense string scored 0.8. This was the single biggest quality weakness.
- **Decision**: Each operator declares `expected_keys: List[str]`. Confidence is a weighted combination of: keys present (40%), non-empty values (40%), and content richness (20%). Operators without `expected_keys` fall back to the legacy length heuristic for backward compatibility.
- **Consequences**: Confidence scores are now semantically meaningful. All 7 existing operators + 5 new operators declare expected_keys. GradingOperator intentionally uses legacy heuristic (no structured output schema).

## ADR-009: Concept Prerequisite DAG (D1)
- **Date**: 2026-02-13
- **Status**: Accepted
- **Context**: 216 concept YAMLs have `prerequisite_concepts` and `related_concepts` fields forming an implicit DAG that was never materialized. DiagnosticOperator needs transitive prerequisite resolution.
- **Decision**: New `core/concept_graph.py` with `ConceptGraph` class using Python's `graphlib.TopologicalSorter`. Provides transitive prerequisite closure, topologically sorted learning paths, related-concept BFS clustering, difficulty estimation (60% depth + 40% count), and cycle detection.
- **Consequences**: No new dependencies (graphlib is stdlib since Python 3.9). Enables prerequisite gap detection for DiagnosticOperator and learning path generation. Difficulty estimation available for future conditional layer activation.

## ADR-010: Five New Cognitive Layers (A1-A5)
- **Date**: 2026-02-13
- **Status**: Accepted
- **Context**: The pipeline had 7 content layers + synthesis but gaps in pre-assessment, big-picture context, narrative pedagogy, structured challenges, and deep-dive elaboration.
- **Decision**: Add 5 new operators following the existing BaseOperator pattern:
  1. **DiagnosticOperator** (pre-assessment) — runs before Activation, produces knowledge_assessment, prerequisite_gaps, recommended_depth, skip_basics, estimated_familiarity
  2. **ContextualizationOperator** (big picture) — between Activation and Metaphor, uses concept category/evolution_rate/related_concepts
  3. **NarrativeOperator** (story-based) — between Contextualization and Structure, embeds concepts in temporal narrative with characters, conflict, resolution
  4. **ChallengeOperator** (Bloom's taxonomy) — between Transfer and Reflection, calibrates challenges using expertise level, diagnostic gaps, and cognitive_load
  5. **ElaborationOperator** (deep-dive) — between Reflection and Synthesis, selects most relevant subtopic based on diagnostic gaps or default ordering
- **Consequences**: LayerName enum grows from 8 to 13. CognitiveArtifact gets 5 new slots. All 3 profiles updated with new layers defaulting to `enabled: false` (except diagnostic in chatbot_tutor). SynthesisOperator integrates all new layers. ChatbotAdapter formats all new layers. Backward compatible — existing behavior unchanged unless new layers are explicitly enabled.
