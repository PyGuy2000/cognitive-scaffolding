# Product Requirements Document: Cognitive Scaffolding Layer

**Version:** 0.1.0
**Status:** Implemented
**Last Updated:** 2026-02-12

---

## Table of Contents

1. [Vision and Purpose](#1-vision-and-purpose)
2. [System Architecture](#2-system-architecture)
3. [Core Intermediate Representation: CognitiveArtifact](#3-core-intermediate-representation-cognitiveartifact)
4. [Operators](#4-operators)
5. [Orchestrator](#5-orchestrator)
6. [Feature Toggle System](#6-feature-toggle-system)
7. [Audience Control Vector](#7-audience-control-vector)
8. [Scoring Model](#8-scoring-model)
9. [Integration Profiles](#9-integration-profiles)
10. [Adapters](#10-adapters)
11. [Migration Strategy](#11-migration-strategy)
12. [Data Assets](#12-data-assets)
13. [Non-Goals (v0.1)](#13-non-goals-v01)
14. [Testing Strategy](#14-testing-strategy)

---

## 1. Vision and Purpose

### What This Is

Cognitive Scaffolding is **universal understanding middleware** -- a "cognitive compiler" that takes any concept combined with an audience profile and produces structured, multi-layer explanations. It is deliberately **not** an education product. The delivery channel changes, but the cognitive work is invariant.

### Core Thesis

Most "understanding" interactions across systems reduce to the same underlying job:

- Turn ambiguous intent into a coherent mental model
- Validate understanding (or detect misconceptions)
- Provide transfer and application
- Calibrate confidence

The 7-layer engine formalizes this job. The system operates as middleware that **plugs into** existing infrastructure:

- **Chatbots** -- interactive tutoring and progressive disclosure
- **RAG pipelines** -- retrieval + explanation + grounding
- **ETL systems** -- explain transformations, anomalies, schema semantics

### What This Builds On

The project extends an existing **metaphor MCP server** (`/home/robkacz/python/projects/metaphor-mcp-server/`) with:

- 16 tools
- 200+ concept YAMLs
- 18 audience profiles
- 25+ metaphor domains
- 14 explanation styles

The metaphor server becomes one operator (MetaphorOperator) within the larger cognitive architecture.

### Naming Convention

The central artifact is called `CognitiveArtifact`, **not** `LessonArtifact`. This is a deliberate choice -- the system produces more than lessons. It produces anomaly explanations, regulatory interpretations, model justifications, and RAG-grounded syntheses. The name must reflect this breadth.

---

## 2. System Architecture

### Three Layers of Abstraction

```
+--------------------------------------------------------------+
|                     ADAPTERS (Integration Surface)            |
|  ChatbotAdapter  |  RAGAdapter  |  ETLAdapter                |
+--------------------------------------------------------------+
                              |
+--------------------------------------------------------------+
|                    ORCHESTRATOR (Cognitive Compiler)           |
|  Conductor  |  Toggle Manager  |  Call Plan  |  Provenance    |
+--------------------------------------------------------------+
                              |
+--------------------------------------------------------------+
|                     OPERATORS (Atomic Cognitive Skills)        |
|  Activation | Metaphor | Structure | Interrogation            |
|  Encoding   | Transfer | Reflection | Grading                 |
+--------------------------------------------------------------+
                              |
+--------------------------------------------------------------+
|                      CORE (Models + Scoring + Data)           |
|  CognitiveArtifact  |  AudienceProfile  |  Scoring  |  YAML  |
+--------------------------------------------------------------+
```

### Directory Layout

```
cognitive_scaffolding/
|
+-- src/cognitive_scaffolding/
|   +-- __init__.py
|   +-- core/
|   |   +-- models.py              # CognitiveArtifact, LayerOutput, ArtifactRecord
|   |   +-- scoring.py             # LayerConfig, score_artifact()
|   |   +-- data_loader.py         # DataLoader for YAML concepts/audiences/domains
|   |   +-- audience.py            # Audience model (from metaphor MCP)
|   |   +-- concept.py             # Concept model (from metaphor MCP)
|   |   +-- domain.py              # Domain model (from metaphor MCP)
|   |   +-- audience_inheritance.py # 3-level audience inheritance tree
|   |
|   +-- orchestrator/
|   |   +-- conductor.py           # CognitiveConductor.compile() main loop
|   |   +-- toggle_manager.py      # ToggleManager: profile + runtime + experiment
|   |   +-- call_plan.py           # CallPlan, OperatorStep
|   |   +-- provenance.py          # ProvenanceTracker, ProvenanceEntry
|   |   +-- regeneration.py        # regenerate_weak_layers()
|   |
|   +-- operators/
|   |   +-- base.py                # BaseOperator ABC
|   |   +-- activation.py          # ActivationOperator
|   |   +-- metaphor.py            # MetaphorOperator (wraps MetaphorEngine)
|   |   +-- structure.py           # StructureOperator
|   |   +-- interrogation.py       # InterrogationOperator
|   |   +-- encoding.py            # EncodingOperator
|   |   +-- transfer.py            # TransferOperator
|   |   +-- reflection.py          # ReflectionOperator
|   |   +-- grading.py             # GradingOperator (rule-based, no LLM)
|   |
|   +-- schemas/                   # JSON schemas (future)
|   |
|   +-- adapters/
|       +-- base.py                # BaseAdapter ABC
|       +-- chatbot_adapter.py     # ChatbotAdapter
|       +-- rag_adapter.py         # RAGAdapter
|       +-- etl_adapter.py         # ETLAdapter
|
+-- profiles/
|   +-- chatbot_tutor.yaml
|   +-- rag_explainer.yaml
|   +-- etl_explain.yaml
|
+-- data/
|   +-- audiences/                 # 16 audience YAMLs
|   +-- concepts/                  # 218 concept YAMLs
|   +-- domains/                   # 29 metaphor domain YAMLs
|   +-- templates/                 # Explanation styles, diagram templates
|
+-- utils/
|   +-- ai_client.py               # AIClient (Anthropic + OpenAI)
|   +-- cache.py                   # ContentCache (TTL-based)
|   +-- yaml_utils.py              # safe_load_yaml, load_yaml_as_model
|
+-- tests/
|   +-- unit/                      # 30 tests
|   +-- integration/               # 4 tests
|
+-- pyproject.toml
```

### Design Principle

The orchestrator **never generates content directly**. It only:

- Plans (builds call sequences via CallPlan)
- Calls (dispatches to operators via dynamic import)
- Scores (evaluates artifact quality via score_artifact)
- Regenerates (re-runs weak layers via regenerate_weak_layers)

Content generation lives exclusively in operators.

---

## 3. Core Intermediate Representation: CognitiveArtifact

`CognitiveArtifact` is the system's Intermediate Representation (IR) -- analogous to an AST in compilers or a DAG in ETL.

### Properties

- **Channel-agnostic** -- does not assume chatbot, RAG, or ETL
- **Audience-conditioned** -- parameterized by a 7D control vector
- **Modular** -- layers are independently populated
- **Evaluatable** -- can be scored and diagnosed
- **Regenerable** -- weak layers can be individually re-run

### Structure

All models use Pydantic v2 `BaseModel`:

```python
class LayerOutput(BaseModel):
    """Output from a single cognitive operator."""
    layer: LayerName
    content: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CognitiveArtifact(BaseModel):
    """Core IR -- a multi-layer understanding artifact."""
    artifact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    audience: AudienceProfile

    # 7 optional layer slots
    activation: Optional[LayerOutput] = None
    metaphor: Optional[LayerOutput] = None
    structure: Optional[LayerOutput] = None
    interrogation: Optional[LayerOutput] = None
    encoding: Optional[LayerOutput] = None
    transfer: Optional[LayerOutput] = None
    reflection: Optional[LayerOutput] = None

    evaluation: Optional[EvaluationResult] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

Key methods on `CognitiveArtifact`:

- `get_layer(name: LayerName) -> Optional[LayerOutput]`
- `set_layer(name: LayerName, output: LayerOutput)` -- also updates `updated_at`
- `populated_layers() -> Dict[str, LayerOutput]` -- returns only non-None slots
- `context_dict() -> Dict[str, Any]` -- accumulated content from all populated layers

### Versioning: Mutable with Linear Revision History

The artifact is wrapped in an `ArtifactRecord` that tracks mutations:

```python
class ArtifactRevision(BaseModel):
    revision_id: int
    timestamp: datetime
    changed_layers: List[str]
    reason: str = ""
    score_before: Optional[float] = None
    score_after: Optional[float] = None

class ArtifactRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    artifact: CognitiveArtifact
    revision_history: List[ArtifactRevision] = Field(default_factory=list)
    current_revision: int = 0
    profile_name: str = ""
```

Each call to `record.add_revision(changed_layers, reason, score_before, score_after)` appends to the history. This provides a full audit trail without immutable snapshots.

---

## 4. Operators

The system defines **8 operators**. Seven implement cognitive layers; one (GradingOperator) evaluates the completed artifact.

### BaseOperator ABC

```python
class BaseOperator(ABC):
    layer_name: LayerName  # Subclasses must set this

    def __init__(self, ai_client=None):
        self.ai_client = ai_client

    def execute(self, topic, audience, context, config=None) -> LayerOutput:
        """Template method: build prompt -> call LLM or fallback -> parse -> score."""
        prompt = self.build_prompt(topic, audience, context, config or {})
        if self.ai_client and self.ai_client.is_available():
            raw = self.ai_client.generate(prompt)
        else:
            raw = self.generate_fallback(topic, audience, context, config or {})
        content = self.parse_output(raw)
        confidence = self.estimate_confidence(content)
        return LayerOutput(layer=self.layer_name, content=content, confidence=confidence, ...)

    @abstractmethod
    def build_prompt(self, topic, audience, context, config) -> str: ...

    def parse_output(self, raw: str) -> Dict[str, Any]:
        """Try JSON parse, fall back to {"text": raw}."""

    def estimate_confidence(self, content: Dict[str, Any]) -> float:
        """Heuristic: <50 chars=0.3, <200=0.5, <500=0.7, else 0.8."""

    def generate_fallback(self, topic, audience, context, config) -> str:
        """Deterministic fallback when AI unavailable. Subclasses override."""
```

### Communication Rule

Operators **never communicate directly**. The conductor passes a `context` dict that accumulates all prior `LayerOutput.content` dicts. Each operator reads from context but only writes its own `LayerOutput`.

### Operator Specifications

#### 1. ActivationOperator (Layer 1)

| Field | Description |
|---|---|
| **Cognitive Function** | Capture attention; allocate cognitive resources |
| **Outputs** | `hook`, `curiosity_gap`, `stakes`, `emotional_trigger`, `prior_knowledge_bridge` |
| **Failure Mode** | No engagement -- audience never invests attention |
| **Audience Scaling** | Uses `language_level` and `cognitive_load` from control vector |

#### 2. MetaphorOperator (Layer 2 -- Fat Operator)

Wraps the existing `MetaphorEngine` from metaphor-mcp-server via `sys.path` import. Falls back to LLM-based generation if the engine is unavailable.

| Field | Description |
|---|---|
| **Cognitive Function** | Reduce cognitive load by mapping unfamiliar onto familiar |
| **Outputs** | `metaphor`, `source_domain`, `mapping`, `limitations`, `extension` |
| **Failure Mode** | Cognitive overload (no anchor) or misconception (no boundary conditions) |
| **Engine Path** | `metaphor-mcp-server/src/core/engines/metaphor_engine.py` |

#### 3. StructureOperator (Layer 3)

| Field | Description |
|---|---|
| **Cognitive Function** | Replace intuition with precision |
| **Outputs** | `definition`, `taxonomy`, `key_terms`, `relationships`, `diagram_description`, `formal_notation` |
| **Failure Mode** | Illusion of understanding -- structurally hollow |
| **Context Use** | Builds on metaphor `mapping` from prior context |

#### 4. InterrogationOperator (Layer 4)

| Field | Description |
|---|---|
| **Cognitive Function** | Strengthen encoding via retrieval and elaboration |
| **Outputs** | `socratic_questions`, `counterexamples`, `edge_cases`, `misconception_probes`, `synthesis_prompt` |
| **Failure Mode** | Shallow familiarity -- recognizes but cannot reason |
| **Context Use** | Probes metaphor `limitations` and structure `key_terms` |

#### 5. EncodingOperator (Layer 5)

| Field | Description |
|---|---|
| **Cognitive Function** | Durable memory formation |
| **Outputs** | `mnemonic`, `chunks` (label+summary), `retrieval_cues`, `spaced_repetition` (Q&A), `visual_anchor` |
| **Failure Mode** | Rapid forgetting |
| **Context Use** | Encodes structure `key_terms` |

#### 6. TransferOperator (Layer 6)

| Field | Description |
|---|---|
| **Cognitive Function** | Validate model portability across contexts |
| **Outputs** | `worked_example` (problem+steps+solution), `practice_problems`, `real_world_applications`, `simulation_prompt`, `cross_domain_transfer` |
| **Failure Mode** | Context-bound knowledge |
| **Context Use** | Builds on structure `definition` |

#### 7. ReflectionOperator (Layer 7)

| Field | Description |
|---|---|
| **Cognitive Function** | Metacognitive calibration |
| **Outputs** | `calibration_questions`, `confidence_check`, `misconception_alerts`, `connection_prompts`, `next_steps` |
| **Failure Mode** | Persistent misconceptions go undetected |
| **Context Use** | References interrogation `misconception_probes` and encoding `chunks` |

#### 8. GradingOperator (Evaluation -- Rule-Based)

Operates on the accumulated context dict. Does **not** call an LLM -- entirely rule-based.

| Field | Description |
|---|---|
| **Cognitive Function** | Quality assurance and revision planning |
| **Outputs** | `layer_grades`, `gaps` (missing/empty layers), `revision_plan`, `overall_quality` |
| **Grading Logic** | Scores each layer by field count and content length |

---

## 5. Orchestrator

### Components

| Component | File | Responsibility |
|---|---|---|
| **CognitiveConductor** | `conductor.py` | Main compilation loop |
| **ToggleManager** | `toggle_manager.py` | Resolve toggle state from profile + overrides |
| **CallPlan** | `call_plan.py` | Ordered operator step sequence |
| **ProvenanceTracker** | `provenance.py` | Record operator timing, success/failure |
| **regenerate_weak_layers** | `regeneration.py` | Re-run layers below confidence threshold |

### Compilation Loop

```python
class CognitiveConductor:
    def compile(self, topic, audience_id, profile_name="chatbot_tutor",
                overrides=None, audience_vector=None) -> ArtifactRecord:
        # 1. Build AudienceProfile from audience_id + control vector
        vector = audience_vector or DEFAULT_VECTORS.get(audience_id, AudienceControlVector())
        audience = AudienceProfile(audience_id=audience_id, ...)

        # 2. Load profile and apply runtime overrides
        layer_configs = self.toggle_manager.load_profile(profile_name)
        if overrides:
            layer_configs = self.toggle_manager.apply_overrides(layer_configs, overrides)

        # 3. Build call plan from resolved configs
        call_plan = CallPlan.from_layer_configs(layer_configs, profile_name)

        # 4. Execute enabled operators in sequence, accumulating context
        artifact = CognitiveArtifact(topic=topic, audience=audience)
        context = {}
        for step in call_plan.enabled_steps():
            operator = self._get_operator(step.operator_class)  # dynamic import
            output = operator.execute(topic, audience, context, step.config)
            artifact.set_layer(step.layer, output)
            context[step.layer.value] = output.content

        # 5. Score the artifact
        artifact.evaluation = score_artifact(artifact, layer_configs)

        # 6. Return ArtifactRecord with revision history
        record = ArtifactRecord(artifact=artifact, profile_name=profile_name)
        record.add_revision(changed_layers=list(context.keys()), reason="Initial compilation")
        return record
```

Operators are resolved via dynamic import (`importlib.import_module`) and cached per session.

### Regeneration

`regenerate_weak_layers(record, layer_configs, conductor, threshold=0.5)` identifies layers with confidence below the threshold, re-runs those operators with enriched context, re-scores, and appends a revision entry.

---

## 6. Feature Toggle System

Toggles operate at **three levels**, with later levels overriding earlier ones.

### Level 1: Profile YAML Defaults

Each profile specifies per-layer `enabled`, `required`, and `weight`:

```yaml
# profiles/chatbot_tutor.yaml (excerpt)
layers:
  activation:
    enabled: true
    required: true
    weight: 1.2
  metaphor:
    enabled: true
    required: false
    weight: 1.5
```

### Level 2: Runtime Overrides

The API caller can override any toggle at call time. Overrides are a flat dict keyed by layer name:

```python
record = conductor.compile(
    topic="gradient descent",
    audience_id="data_scientist",
    profile_name="chatbot_tutor",
    overrides={
        "encoding": {"enabled": False},
        "metaphor": {"weight": 3.0},
    }
)
```

### Level 3: A/B Experiments

`ToggleManager.create_experiment_variants(base_configs, toggle_layer)` returns two config variants -- one with the layer enabled, one disabled -- for comparing scores:

```python
variant_a, variant_b = toggle_manager.create_experiment_variants(configs, "activation")
# variant_a: activation enabled
# variant_b: activation disabled
# Compile with each, compare scores
```

### Resolution Order

```
Profile YAML  -->  Runtime Overrides  =  Effective LayerConfig per layer
```

---

## 7. Audience Control Vector

The audience is modeled as a 7-dimensional `AudienceControlVector` (Pydantic model) that parameterizes every operator's output:

```python
class AudienceControlVector(BaseModel):
    language_level: float = Field(0.5, ge=0.0, le=1.0)
    abstraction: float = Field(0.5, ge=0.0, le=1.0)
    rigor: float = Field(0.5, ge=0.0, le=1.0)
    math_density: float = Field(0.0, ge=0.0, le=1.0)
    domain_specificity: float = Field(0.5, ge=0.0, le=1.0)
    cognitive_load: float = Field(0.5, ge=0.0, le=1.0)
    transfer_distance: float = Field(0.5, ge=0.0, le=1.0)
```

### Dimensions

| Field | Range | Low End | High End |
|---|---|---|---|
| `language_level` | 0.0 -- 1.0 | Simple vocabulary, short sentences | Advanced vocabulary, complex syntax |
| `abstraction` | 0.0 -- 1.0 | Concrete, tangible examples | Abstract, formal representations |
| `rigor` | 0.0 -- 1.0 | Informal, conversational | Formal, precise, theorem-style |
| `math_density` | 0.0 -- 1.0 | No math at all | Heavy notation, derivations |
| `domain_specificity` | 0.0 -- 1.0 | General, cross-domain language | Deep field-specific jargon |
| `cognitive_load` | 0.0 -- 1.0 | Minimal, low branching | Heavy, multi-branch, deep |
| `transfer_distance` | 0.0 -- 1.0 | Near transfer (same domain) | Far/novel transfer (cross-domain) |

### Default Vectors

Defined in `conductor.py`:

```python
DEFAULT_VECTORS = {
    "child": AudienceControlVector(
        language_level=0.1, abstraction=0.1, rigor=0.1, math_density=0.0,
        domain_specificity=0.0, cognitive_load=0.2, transfer_distance=0.2,
    ),
    "general": AudienceControlVector(),  # all 0.5 except math_density=0.0
    "data_scientist": AudienceControlVector(
        language_level=0.8, abstraction=0.7, rigor=0.8, math_density=0.7,
        domain_specificity=0.8, cognitive_load=0.8, transfer_distance=0.6,
    ),
    "phd": AudienceControlVector(
        language_level=0.9, abstraction=0.9, rigor=0.95, math_density=0.9,
        domain_specificity=0.9, cognitive_load=0.9, transfer_distance=0.8,
    ),
}
```

### How the Vector Gates Each Layer

| Layer | Low Vector | High Vector |
|---|---|---|
| Activation | Story hooks, relatable scenarios | Open research problems, quantitative stakes |
| Metaphor | Physical, everyday analogies | Formal mappings, dynamical systems |
| Structure | Plain-English definitions, simple lists | Formal notation, equations |
| Interrogation | Simple "why?" chains | Causal probes, edge cases, counterexamples |
| Encoding | Rhymes, mnemonics, visual chunking | Compact heuristics, retrieval derivations |
| Transfer | Toy examples, playground scenarios | Real-world cases, quantitative problems |
| Reflection | Simple teach-back | Calibration, error decomposition |

---

## 8. Scoring Model

### Formula

```
Score = sum(w_k * x_k) / sum(w_k)
```

Where:

- `w_k` = weight for layer `k` (from `LayerConfig.weight`)
- `x_k` = confidence score from layer `k`'s `LayerOutput` (0.0 to 1.0)

### Rules

1. **Disabled layers** are excluded from both numerator and denominator
2. **Enabled but empty layers** are included in the denominator (score 0.0), penalizing gaps
3. **Required layers** that are enabled but empty trigger a **penalty multiplier of 0.7** on the final score
4. **Score range:** 0.0 to 1.0

### Implementation

```python
REQUIRED_PENALTY = 0.7

class LayerConfig:
    def __init__(self, enabled=True, required=False, weight=1.0): ...

def score_artifact(artifact: CognitiveArtifact,
                   layer_configs: Dict[str, LayerConfig]) -> EvaluationResult:
    numerator, denominator = 0.0, 0.0
    for layer in LayerName:
        config = layer_configs.get(layer.value, LayerConfig(enabled=False))
        if not config.enabled:
            continue
        output = artifact.get_layer(layer)
        if output is not None:
            numerator += config.weight * output.confidence
        elif config.required:
            missing_required.append(layer.value)
        denominator += config.weight

    overall = numerator / denominator if denominator else 0.0
    if missing_required:
        overall *= REQUIRED_PENALTY

    return EvaluationResult(overall_score=round(overall, 4), ...)
```

### EvaluationResult

```python
class EvaluationResult(BaseModel):
    overall_score: float = Field(0.0, ge=0.0, le=1.0)
    layer_scores: Dict[str, float]       # per-layer confidence
    penalty_applied: bool = False
    penalty_reason: Optional[str] = None
    missing_required: List[str]           # layers that were required but empty
    weights_used: Dict[str, float]        # weights applied per layer
```

---

## 9. Integration Profiles

Three profiles ship with v0.1. Each is a YAML file in `profiles/`.

### Profile 1: `chatbot_tutor`

Full cognitive scaffolding for interactive tutoring. All 7 layers enabled.

| Layer | Enabled | Required | Weight |
|---|---|---|---|
| activation | yes | **yes** | 1.2 |
| metaphor | yes | no | 1.5 |
| structure | yes | **yes** | 1.3 |
| interrogation | yes | no | 1.0 |
| encoding | yes | **yes** | 1.2 |
| transfer | yes | no | 1.0 |
| reflection | yes | no | 0.8 |

Settings: `max_tokens_per_layer: 1500`, `progressive_disclosure: true`

### Profile 2: `rag_explainer`

Optimized for RAG pipeline document enrichment. Metaphor + Structure + Transfer enabled.

| Layer | Enabled | Required | Weight |
|---|---|---|---|
| activation | no | no | 0.5 |
| metaphor | yes | **yes** | 1.5 |
| structure | yes | **yes** | 1.5 |
| interrogation | no | no | 0.5 |
| encoding | no | no | 0.5 |
| transfer | yes | no | 1.2 |
| reflection | no | no | 0.3 |

Settings: `max_tokens_per_layer: 1000`, `progressive_disclosure: false`

### Profile 3: `etl_explain`

Structured output for ETL data pipelines. Structure-heavy, batch-friendly.

| Layer | Enabled | Required | Weight |
|---|---|---|---|
| activation | no | no | 0.3 |
| metaphor | yes | no | 1.0 |
| structure | yes | **yes** | 2.0 |
| interrogation | no | no | 0.3 |
| encoding | no | no | 0.3 |
| transfer | yes | no | 0.8 |
| reflection | yes | no | 1.0 |

Settings: `max_tokens_per_layer: 800`, `progressive_disclosure: false`, `batch_mode: true`

### Profile Comparison

| Feature | chatbot_tutor | rag_explainer | etl_explain |
|---|---|---|---|
| Layers enabled | 7 | 3 | 4 |
| Required layers | activation, structure, encoding | metaphor, structure | structure |
| Heaviest weight | metaphor (1.5) | metaphor, structure (1.5) | structure (2.0) |
| Progressive disclosure | yes | no | no |

---

## 10. Adapters

Adapters transform an `ArtifactRecord` into the format expected by the host system. They implement `BaseAdapter.format(record)`.

### ChatbotAdapter

Formats as a list of chat messages with progressive disclosure:

```python
class ChatbotAdapter(BaseAdapter):
    def format(self, record: ArtifactRecord) -> List[Dict[str, Any]]:
        """Returns list of dicts with 'role', 'content', 'layer', 'confidence', 'metadata'.
        Messages ordered: activation -> metaphor -> structure -> ... -> reflection.
        Includes evaluation summary as final system message."""
```

Per-layer formatting converts structured content into readable text (e.g., activation `hook` + `stakes`, metaphor `metaphor` + `mapping`, structure `definition` + `key_terms`).

### RAGAdapter

Formats as enriched document chunks for vector store ingestion:

```python
class RAGAdapter(BaseAdapter):
    def format(self, record: ArtifactRecord) -> List[Dict[str, Any]]:
        """Returns list of dicts with 'chunk_id', 'content', 'metadata'.
        One chunk per significant content field per layer.
        Metadata includes topic, audience, layer, field, confidence, score."""
```

### ETLAdapter

Formats as a single flat dictionary for data pipeline ingestion:

```python
class ETLAdapter(BaseAdapter):
    def format(self, record: ArtifactRecord) -> Dict[str, Any]:
        """Returns flat dict with: artifact_id, topic, audience_id,
        cv_* fields (control vector), score, penalty_*,
        layer_<name>_populated, layer_<name>_confidence for each layer,
        layers_populated list, num_layers count."""
```

---

## 11. Migration Strategy

### Approach: Fat Operator Wrapping (Option B)

The `MetaphorOperator` wraps the existing `MetaphorEngine` via `sys.path` import:

```python
# operators/metaphor.py
import sys
sys.path.insert(0, "/home/robkacz/python/projects/metaphor-mcp-server")
from src.core.engines.metaphor_engine import MetaphorEngine

class MetaphorOperator(BaseOperator):
    def __init__(self, ai_client=None, engine=None):
        super().__init__(ai_client)
        self.engine = engine or _metaphor_engine  # module-level singleton

    def execute(self, topic, audience, context, config=None):
        if self.engine is not None:
            return self._execute_via_engine(...)  # use existing engine
        return super().execute(...)  # fall back to LLM
```

### Shared Infrastructure

Copied from metaphor-mcp-server into cognitive_scaffolding (not linked):

| Source | Destination |
|---|---|
| `src/models/audience.py` | `core/audience.py` |
| `src/models/concept.py` | `core/concept.py` |
| `src/models/domain.py` | `core/domain.py` |
| `src/utils/ai_client.py` | `utils/ai_client.py` |
| `src/utils/cache.py` | `utils/cache.py` |
| `src/utils/file_utils.py` | `utils/yaml_utils.py` |
| `src/core/audience_inheritance.py` | `core/audience_inheritance.py` |
| `data/**` | `data/**` |

A backup of the original metaphor-mcp-server exists at `/home/robkacz/python/projects/metaphor-mcp-server-backup/`.

### Future Refactoring

Later iterations can extract shared code into a common package. Not a v0.1 requirement.

---

## 12. Data Assets

| Category | Location | Count | Source |
|---|---|---|---|
| Audiences | `data/audiences/` | 16 | Copied from metaphor-mcp-server |
| Concepts | `data/concepts/` | 218 | Copied from metaphor-mcp-server |
| Domains | `data/domains/` | 29 | Copied from metaphor-mcp-server |
| Templates | `data/templates/` | 4 files | Copied from metaphor-mcp-server |

Templates include 14 explanation styles (extended_metaphor, quick_analogy, progressive_revelation, interactive_dialogue, narrative_journey, visual_construction, problem_solution_cycle, misconception_decoder, ecosystem_perspective, hands_on_workshop, temporal_evolution, multi_perspective_lens, failure_recovery_cycle, comparative_metaphor).

---

## 13. Non-Goals (v0.1)

| Non-Goal | Rationale |
|---|---|
| Real-time streaming of partial artifacts | Adds complexity; not needed for validation |
| Multi-concept dependency graphs | Single-concept compilation proves the architecture |
| Persistent storage | All in-memory; no database |
| Authentication / authorization | Middleware is called by trusted host systems |
| UI / frontend | API-only |
| Multi-language support | English only |
| Concurrent operator execution | Sequential execution is simpler and sufficient |

---

## 14. Testing Strategy

### Unit Tests (30 tests in `tests/unit/`)

| Test File | Coverage |
|---|---|
| `test_models.py` | AudienceControlVector, LayerOutput, CognitiveArtifact, ArtifactRecord |
| `test_scoring.py` | Weighted scoring, penalty multiplier, disabled-layer exclusion, edge cases |
| `test_toggle_manager.py` | Profile loading, missing profiles, runtime overrides, experiment variants |
| `test_operators.py` | All 8 operators: fallback execution, prompt building, grading logic |

### Integration Tests (4 tests in `tests/integration/`)

| Test | What It Validates |
|---|---|
| `TestChatbotPipeline` | Full compile + ChatbotAdapter.format produces chat messages |
| `TestRAGPipeline` | Full compile + RAGAdapter.format produces document chunks |
| `TestETLPipeline` | Full compile + ETLAdapter.format produces flat dict |
| `TestOverrides` | Runtime overrides disable layers correctly |

### Running Tests

```bash
pytest tests/unit/       # 30 tests
pytest tests/integration/ # 4 tests
pytest tests/            # all 34 tests
```

### Dependencies

```toml
[project]
dependencies = [
    "pydantic>=2.0.0",
    "PyYAML>=6.0",
    "anthropic>=0.8.0",
    "openai>=1.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
```

---

## Appendix: Architectural Decision Summary

| Decision | Choice | Rationale |
|---|---|---|
| Core artifact name | `CognitiveArtifact` | Broader than education |
| Versioning | Mutable with linear revision history | Simplest model with audit trail |
| Operator communication | Via conductor context dict, never direct | Clean separation; independently testable |
| Migration strategy | Fat operator wrap via sys.path import | Reuses MetaphorEngine without duplication |
| Shared data | Copy into cognitive_scaffolding | Independence; unify later |
| Scoring | Weighted average with required-layer penalty | Simple, interpretable, toggleable |
| Profile format | YAML with `layers:` + `settings:` sections | Human-editable, consistent with data assets |
