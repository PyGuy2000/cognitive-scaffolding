# Product Requirements Document: Cognitive Scaffolding Layer

**Version:** 0.1.0
**Status:** Draft
**Last Updated:** 2026-02-12

---

## Table of Contents

1. [Vision and Purpose](#1-vision-and-purpose)
2. [System Architecture](#2-system-architecture)
3. [Core Intermediate Representation: CognitiveArtifact](#3-core-intermediate-representation-cognitiveartifact)
4. [Operators (8)](#4-operators)
5. [Orchestrator (Conductor)](#5-orchestrator-conductor)
6. [Feature Toggle System](#6-feature-toggle-system)
7. [Audience Control Vector](#7-audience-control-vector)
8. [Scoring Model](#8-scoring-model)
9. [Integration Profiles](#9-integration-profiles)
10. [Adapters](#10-adapters)
11. [Migration Strategy](#11-migration-strategy)
12. [Non-Goals (v0.1)](#12-non-goals-v01)
13. [Data Assets](#13-data-assets)
14. [Key Interfaces and Types](#14-key-interfaces-and-types)
15. [Testing Strategy](#15-testing-strategy)

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
- **RAG pipelines** -- retrieval + explanation + grounding with citation
- **ETL systems** -- explain transformations, anomalies, schema semantics, KPIs
- **Knowledge graphs** -- concept maps, causal relations, taxonomy enforcement
- **Decision support** -- explain recommendations, sensitivity, tradeoffs

### What This Builds On

The project extends an existing **metaphor MCP server** with:

- 16 tools
- 200+ concept YAMLs
- 18 audience profiles
- 25+ metaphor domains
- 14 explanation styles

The metaphor server becomes one operator within a larger cognitive architecture.

### Naming Convention

The central artifact is called `CognitiveArtifact`, **not** `LessonArtifact`. This is a deliberate choice -- the system produces more than lessons. It produces anomaly explanations, regulatory interpretations, model justifications, debugging runbooks, and RAG-grounded syntheses. The name must reflect this breadth.

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
|  Conductor  |  Toggle Manager  |  Call Planner  |  Provenance |
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
|   +-- core/                    # Core models, scoring, data loading
|   |   +-- __init__.py
|   |   +-- artifact.py          # CognitiveArtifact, LayerOutput
|   |   +-- audience.py          # AudienceProfile, control vector
|   |   +-- scoring.py           # Weighted scoring engine
|   |   +-- data_loader.py       # YAML loading utilities
|   |
|   +-- orchestrator/            # Conductor (compilation loop)
|   |   +-- __init__.py
|   |   +-- conductor.py         # Main compilation loop
|   |   +-- toggle_manager.py    # Feature toggle resolution
|   |   +-- call_planner.py      # Operator call sequencing
|   |   +-- provenance.py        # Input hashing, audit trail
|   |
|   +-- operators/               # 8 operators, one per cognitive layer
|   |   +-- __init__.py
|   |   +-- base.py              # BaseOperator ABC
|   |   +-- activation.py        # ActivationOperator
|   |   +-- metaphor.py          # MetaphorOperator (wraps MetaphorEngine)
|   |   +-- structure.py         # StructureOperator
|   |   +-- interrogation.py     # InterrogationOperator
|   |   +-- encoding.py          # EncodingOperator
|   |   +-- transfer.py          # TransferOperator
|   |   +-- reflection.py        # ReflectionOperator
|   |   +-- grading.py           # GradingOperator
|   |
|   +-- schemas/                 # JSON schemas for operator I/O validation
|   |   +-- __init__.py
|   |   +-- cognitive_artifact.schema.json
|   |   +-- operator_contracts/
|   |   +-- integration_profiles/
|   |
|   +-- adapters/                # Integration adapters
|       +-- __init__.py
|       +-- chatbot.py           # ChatbotAdapter
|       +-- rag.py               # RAGAdapter
|       +-- etl.py               # ETLAdapter
|
+-- profiles/                    # YAML integration profiles
|   +-- chatbot_tutor.yaml
|   +-- rag_explainer.yaml
|   +-- etl_explain.yaml
|
+-- data/                        # Copied YAML data from metaphor-mcp-server
|   +-- audiences/               # 18 audience profile YAMLs
|   +-- concepts/                # 200+ concept YAMLs
|   +-- domains/                 # 25+ metaphor domain YAMLs
|   +-- templates/               # Explanation styles, diagram templates, etc.
|
+-- utils/                       # Shared utilities
|   +-- __init__.py
|   +-- ai_client.py             # LLM client abstraction
|   +-- cache.py                 # Caching layer
|   +-- yaml_utils.py            # YAML loading/validation helpers
|
+-- tests/
|   +-- unit/
|   +-- integration/
|
+-- pyproject.toml
```

### Design Principle

The orchestrator must **never generate content directly**. It only:

- Plans (builds call sequences)
- Calls (dispatches to operators)
- Validates (checks operator output against schemas)
- Scores (evaluates artifact quality)
- Regenerates (re-runs weak layers)

Content generation lives exclusively in operators.

---

## 3. Core Intermediate Representation: CognitiveArtifact

`CognitiveArtifact` is the system's Intermediate Representation (IR) -- analogous to an AST in compilers or a DAG in ETL. It represents a structured representation of understanding generated by the Cognitive Scaffolding Layer.

### Properties

- **Channel-agnostic** -- does not assume chatbot, RAG, or ETL
- **Host-system-agnostic** -- no coupling to any specific platform
- **Audience-conditioned** -- parameterized by a control vector
- **Modular** -- layers are independently populated
- **Evaluatable** -- can be scored and diagnosed
- **Regenerable** -- weak layers can be individually re-run

### Structure

```python
@dataclass
class LayerOutput:
    """Output from a single operator."""
    content: dict[str, Any]        # Operator-specific structured output
    confidence: float              # 0.0 to 1.0 self-assessed quality
    provenance: ProvenanceRecord   # Inputs hash, timestamp, model version

@dataclass
class CognitiveArtifact:
    """Core intermediate representation for the scaffolding layer."""
    topic: str
    audience_profile: AudienceProfile

    # 7 optional layer slots (populated by operators)
    activation: LayerOutput | None = None
    metaphor: LayerOutput | None = None
    structure: LayerOutput | None = None
    interrogation: LayerOutput | None = None
    encoding: LayerOutput | None = None
    transfer: LayerOutput | None = None
    reflection: LayerOutput | None = None

    # Evaluation (populated by GradingOperator)
    evaluation: EvaluationResult | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    revision_history: list[RevisionRecord] = field(default_factory=list)
```

### Versioning Strategy: Mutable with Linear Revision History (Option 2)

The artifact is mutable. Each time an operator writes to a layer slot, a `RevisionRecord` is appended to `revision_history`:

```python
@dataclass
class RevisionRecord:
    """Tracks a single mutation to the artifact."""
    timestamp_utc: str
    layer: str                     # Which layer was written
    operator: str                  # Which operator wrote it
    reason: str                    # "initial" | "regeneration" | "override"
    previous_confidence: float | None
    new_confidence: float
```

This provides a full audit trail without the complexity of immutable snapshots or branching histories.

---

## 4. Operators

The system defines **8 operators**, each implementing one cognitive layer. Each operator extends a common abstract base class.

### BaseOperator ABC

```python
from abc import ABC, abstractmethod

class BaseOperator(ABC):
    """Abstract base for all cognitive operators."""

    @abstractmethod
    def execute(
        self,
        topic: str,
        audience: AudienceProfile,
        context: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> LayerOutput:
        """Run the operator and return a LayerOutput."""
        ...

    @abstractmethod
    def build_prompt(
        self,
        topic: str,
        audience: AudienceProfile,
        context: dict[str, Any],
    ) -> str:
        """Construct the LLM prompt for this operator."""
        ...

    @abstractmethod
    def validate_output(self, output: dict[str, Any]) -> bool:
        """Validate operator output against its JSON schema contract."""
        ...
```

### Communication Rule

Operators **never communicate directly** with each other. The conductor passes a `context` dict to each operator that accumulates all prior `LayerOutput.content` dicts. This maintains clean separation of concerns.

### Operator Specifications

#### 1. ActivationOperator

Captures attention before any learning occurs. Without activation, nothing downstream matters.

| Field | Description |
|---|---|
| **Layer** | Activation (Layer 1) |
| **Cognitive Function** | Activate the salience network; allocate cognitive resources |
| **Outputs** | Attention hooks, curiosity gaps, stakes framing, emotional triggers |
| **Failure Mode** | No learning occurs -- audience never engages |
| **Scaling by Audience** | Child: story hooks. PhD: open research problems. Executive: dollar stakes. |

**Output schema (key fields):**

```json
{
  "hook": "string",
  "curiosity_question": "string",
  "stakes": "string",
  "emotional_trigger": "string | null"
}
```

#### 2. MetaphorOperator (Fat Operator)

Wraps the existing `MetaphorEngine` from the metaphor-mcp-server via import (not copy). This is the "fat operator" pattern -- it carries significant internal logic.

| Field | Description |
|---|---|
| **Layer** | Metaphor / Anchoring (Layer 2) |
| **Cognitive Function** | Reduce cognitive load by mapping unfamiliar structure onto familiar structure |
| **Outputs** | Analogies, schema mappings, boundary conditions ("where it breaks") |
| **Failure Mode** | Cognitive overload if metaphor is missing; misconception if boundaries are missing |
| **Critical Rule** | Must always return boundary conditions |

**Output schema (key fields):**

```json
{
  "metaphors": [
    {
      "name": "string",
      "source_domain": "string",
      "target_domain": "string",
      "correspondences": ["string"],
      "where_it_breaks": ["string"],
      "audience_fit": { "label": "number 0-1" }
    }
  ],
  "selection": {
    "recommended_name": "string",
    "rationale": "string"
  }
}
```

#### 3. StructureOperator

Replaces fuzzy intuitive grasp with structured representation.

| Field | Description |
|---|---|
| **Layer** | Structure (Layer 3) |
| **Cognitive Function** | Replace intuition with precision |
| **Outputs** | Definitions, taxonomies, hierarchies, diagram descriptions, formal notation |
| **Failure Mode** | Illusion of understanding -- feels correct but structurally hollow |
| **Scaling by Audience** | Plain-English definitions at low rigor; formal notation + equations at high rigor |

**Output schema (key fields):**

```json
{
  "definition": "string",
  "taxonomy": "object | array",
  "diagram_description": "string | null",
  "formal_notation": "string | null",
  "key_claims": ["string"]
}
```

#### 4. InterrogationOperator

Moves from passive understanding to active reasoning.

| Field | Description |
|---|---|
| **Layer** | Interrogation (Layer 4) |
| **Cognitive Function** | Strengthen encoding via retrieval and elaboration |
| **Outputs** | Socratic questions, counterexamples, edge cases, misconception probes |
| **Failure Mode** | Shallow familiarity -- recognizes concept but cannot reason about it |
| **Scaling by Audience** | Simple "why?" chains at low abstraction; causal probes at high abstraction |

**Output schema (key fields):**

```json
{
  "socratic_questions": ["string"],
  "counterexamples": ["string"],
  "edge_cases": ["string"],
  "misconception_probes": ["string"]
}
```

#### 5. EncodingOperator

Memory consolidation -- transfer from working memory to long-term storage.

| Field | Description |
|---|---|
| **Layer** | Encoding (Layer 5) |
| **Cognitive Function** | Durable memory formation |
| **Outputs** | Mnemonics, spaced repetition prompts, chunking strategies, retrieval cues |
| **Failure Mode** | Rapid forgetting |
| **Scaling by Audience** | Rhymes and mnemonics at low complexity; compact heuristics + retrieval problems at high |

**Output schema (key fields):**

```json
{
  "mnemonic": "string | null",
  "spaced_repetition_prompts": ["string"],
  "chunking_strategy": "string | null",
  "retrieval_cues": ["string"]
}
```

#### 6. TransferOperator

Tests whether a concept is internalized or merely recognized.

| Field | Description |
|---|---|
| **Layer** | Transfer (Layer 6) |
| **Cognitive Function** | Validate model portability across contexts |
| **Outputs** | Worked examples, problem sets, simulations, real-world applications |
| **Failure Mode** | Context-bound knowledge -- cannot apply in new situations |
| **Scaling by Audience** | Toy examples at low transfer distance; real-world cases + quantitative scenarios at high |

**Output schema (key fields):**

```json
{
  "worked_example": "string",
  "problem_set": ["string"],
  "simulation_prompt": "string | null",
  "real_world_application": "string | null"
}
```

#### 7. ReflectionOperator

The highest cognitive level: awareness of how one is learning.

| Field | Description |
|---|---|
| **Layer** | Reflection / Meta-Cognition (Layer 7) |
| **Cognitive Function** | Improve learning efficiency over time |
| **Outputs** | Calibration prompts, metacognitive checks, misconception detection, confidence assessment |
| **Failure Mode** | Persistent misconceptions go undetected |
| **Scaling by Audience** | Simple teach-back at low abstraction; calibration + error decomposition at high |

**Output schema (key fields):**

```json
{
  "calibration_prompt": "string",
  "metacognitive_check": "string",
  "misconception_flags": ["string"],
  "confidence_assessment": "string"
}
```

#### 8. GradingOperator

Evaluates the complete artifact and produces actionable diagnostics.

| Field | Description |
|---|---|
| **Layer** | Evaluation (post-pipeline) |
| **Cognitive Function** | Quality assurance and revision planning |
| **Outputs** | Rubric-based scores, diagnostic flags, gap analysis, revision plan |
| **Critical Diagnostic Rules** | See table below |

**Diagnostic Risk Rules:**

| Condition | Flag |
|---|---|
| Metaphor present without Structure | High misconception risk |
| Structure present without Transfer | Likely inert knowledge |
| Encoding present without Interrogation | Memorization without understanding |
| No Activation at all | Attention/engagement risk |

**Output schema (key fields):**

```json
{
  "layer_scores": { "activation": 0.85, "metaphor": 0.92, "...": "..." },
  "overall_score": 0.87,
  "diagnostics": ["string"],
  "missing_critical": ["string"],
  "revision_plan": {
    "layers_to_regenerate": ["string"],
    "reason": "string"
  }
}
```

---

## 5. Orchestrator (Conductor)

The orchestrator is the only component that knows all operators. It is the "cognitive compiler."

### Responsibilities

| Component | Responsibility |
|---|---|
| **Conductor** (`conductor.py`) | Main compilation loop: load profile, resolve toggles, call operators in sequence, run grading, trigger regeneration |
| **Toggle Manager** (`toggle_manager.py`) | Resolve effective toggle state from profile defaults + runtime overrides + A/B experiments |
| **Call Planner** (`call_planner.py`) | Build ordered operator call sequence from resolved toggles, respecting dependencies |
| **Provenance Tracker** (`provenance.py`) | Record input hashes, timestamps, and model versions for every operator call |

### Compilation Loop (Pseudocode)

```python
def compile(topic: str, audience: AudienceProfile, profile: str, overrides: dict = None):
    # 1. Load profile YAML
    profile_config = load_profile(profile)

    # 2. Resolve toggles (profile defaults + runtime overrides)
    toggles = toggle_manager.resolve(profile_config, overrides)

    # 3. Build call plan
    call_plan = call_planner.build(toggles)

    # 4. Initialize artifact
    artifact = CognitiveArtifact(topic=topic, audience_profile=audience)

    # 5. Execute operators in sequence
    context = {}
    for step in call_plan:
        if step.layer == "grading":
            continue  # grading runs after all content operators
        operator = registry.get(step.operator_name)
        output = operator.execute(topic, audience, context, step.config)
        setattr(artifact, step.layer, output)
        context[step.layer] = output.content

    # 6. Run GradingOperator
    artifact.evaluation = grading_operator.execute(topic, audience, context)

    # 7. Regeneration loop (if needed)
    if artifact.evaluation and artifact.evaluation.content.get("revision_plan"):
        for layer in artifact.evaluation.content["revision_plan"]["layers_to_regenerate"]:
            operator = registry.get(layer)
            output = operator.execute(topic, audience, context)
            setattr(artifact, layer, output)
            context[layer] = output.content
            artifact.revision_history.append(...)

    return artifact
```

### Regeneration Policy

Regeneration is **targeted**, not full-rewrite. If the grader identifies weak layers or misconception risk exceeds a threshold, only the specific layers are re-run. The regeneration threshold and target layers are configurable per profile.

---

## 6. Feature Toggle System

Toggles operate at **three levels**, with later levels overriding earlier ones.

### Level 1: Profile YAML Defaults

Each integration profile specifies per-layer configuration:

```yaml
# profiles/chatbot_tutor.yaml (excerpt)
layers:
  activation:
    enabled: true
    required: true
    weight: 1.0
  metaphor:
    enabled: true
    required: false
    weight: 2.0
  structure:
    enabled: true
    required: true
    weight: 2.0
  # ...
```

### Level 2: Runtime Overrides

The API caller can override any toggle at call time:

```python
artifact = compile(
    topic="gradient descent",
    audience=audience,
    profile="chatbot_tutor",
    overrides={
        "layers": {
            "encoding": {"enabled": False},
            "metaphor": {"weight": 3.0}
        }
    }
)
```

### Level 3: A/B Experiments

Compare artifact scores with different toggle combinations:

```python
experiment = ABExperiment(
    base_profile="chatbot_tutor",
    variants={
        "control": {},
        "no_encoding": {"layers": {"encoding": {"enabled": False}}},
        "heavy_metaphor": {"layers": {"metaphor": {"weight": 4.0}}},
    }
)
results = experiment.run(topic, audience, n_trials=50)
```

### Toggle Resolution Order

```
Profile YAML  --->  Runtime Overrides  --->  A/B Variant  =  Effective Toggles
```

---

## 7. Audience Control Vector

The audience is modeled as a 7-dimensional control vector that parameterizes every operator's output:

$$
\mathbf{a} = (\ell,\ \alpha,\ \rho,\ \mu,\ \delta,\ \kappa,\ \tau)
$$

### Dimensions

| Symbol | Name | Range | Low End | High End |
|---|---|---|---|---|
| `l` | `language_level` | 0.0 -- 1.0 | Simple vocabulary, short sentences | Advanced vocabulary, complex syntax |
| `a` | `abstraction` | 0.0 -- 1.0 | Concrete, tangible examples | Abstract, formal representations |
| `r` | `rigor` | 0.0 -- 1.0 | Informal, conversational | Formal, precise, theorem-style |
| `m` | `math_density` | 0.0 -- 1.0 | No math at all | Heavy notation, derivations |
| `d` | `domain_specificity` | 0.0 -- 1.0 | General, cross-domain language | Deep field-specific jargon |
| `k` | `cognitive_load` | 0.0 -- 1.0 | Minimal, low branching | Heavy, multi-branch, deep |
| `t` | `transfer_distance` | 0.0 -- 1.0 | Near transfer (same domain) | Far/novel transfer (cross-domain) |

### Example Audience Vectors

```python
# Child (~10 years old)
child = AudienceProfile(
    label="child",
    control_vector={"l": 0.2, "a": 0.2, "r": 0.1, "m": 0.0, "d": 0.1, "k": 0.3, "t": 0.3}
)

# PhD Researcher
phd = AudienceProfile(
    label="phd",
    control_vector={"l": 0.9, "a": 0.9, "r": 0.9, "m": 0.8, "d": 0.9, "k": 0.9, "t": 0.8}
)

# Business Executive
executive = AudienceProfile(
    label="executive",
    control_vector={"l": 0.7, "a": 0.5, "r": 0.4, "m": 0.1, "d": 0.6, "k": 0.5, "t": 0.6}
)
```

### How the Vector Gates Each Layer

| Layer | Low Vector | High Vector |
|---|---|---|
| Activation | Story hooks, relatable scenarios | Open research problems, quantitative stakes |
| Metaphor | Physical, everyday analogies (pub, kitchen) | Dynamical systems, formal mappings |
| Structure | Plain-English definitions, simple lists | Formal notation, equations, proofs |
| Interrogation | Simple "why?" chains, 2-3 questions | Causal probes, edge cases, counterexamples |
| Encoding | Rhymes, mnemonics, visual chunking | Compact heuristics, retrieval derivations |
| Transfer | Toy examples, playground scenarios | Real-world cases, quantitative problems |
| Reflection | Simple teach-back ("explain to a friend") | Calibration, error decomposition, model revision |

---

## 8. Scoring Model

The scoring model produces a single quality metric for an artifact.

### Formula

```
Score = sum(w_k * x_k) / sum(w_k)
```

Where:

- `w_k` = weight for layer `k` (from profile or runtime override)
- `x_k` = confidence score from operator `k`'s `LayerOutput` (0.0 to 1.0)

### Rules

1. **Disabled layers** are excluded from both numerator and denominator
2. **Required layers** that are enabled but have empty/null output trigger a **penalty multiplier of 0.7** applied to the final score
3. **Score range:** 0.0 to 1.0

### Implementation

```python
def score_artifact(artifact: CognitiveArtifact, toggles: dict) -> float:
    """Compute weighted quality score for a CognitiveArtifact."""
    LAYER_NAMES = [
        "activation", "metaphor", "structure", "interrogation",
        "encoding", "transfer", "reflection"
    ]

    numerator = 0.0
    denominator = 0.0
    penalty_triggered = False

    for layer_name in LAYER_NAMES:
        toggle = toggles.get(layer_name, {})

        if not toggle.get("enabled", False):
            continue  # Disabled: skip entirely

        weight = toggle.get("weight", 1.0)
        layer_output: LayerOutput | None = getattr(artifact, layer_name)

        if layer_output is not None:
            numerator += weight * layer_output.confidence
            denominator += weight
        else:
            # Enabled but empty
            denominator += weight
            if toggle.get("required", False):
                penalty_triggered = True

    if denominator == 0:
        return 0.0

    score = numerator / denominator

    if penalty_triggered:
        score *= 0.7  # Required-layer-missing penalty

    return round(score, 4)
```

### Diagnostic Flags

Beyond the numeric score, the `GradingOperator` also produces qualitative diagnostic flags:

| Condition | Diagnostic |
|---|---|
| Metaphor present, Structure absent | "Metaphor without Structure: high misconception risk" |
| Structure present, Transfer absent | "Structure without Transfer: likely inert knowledge" |
| Encoding present, Interrogation absent | "Encoding without Interrogation: memorization without understanding" |
| No Activation | "No Activation: attention/engagement risk" |

---

## 9. Integration Profiles

Three integration profiles ship with v0.1. Each profile is a YAML file in `profiles/` that configures which layers are enabled, which are required, and their weights.

### Profile 1: `chatbot_tutor`

**Purpose:** Interactive learning with turn-by-turn scaffolding. Optimizes for engagement and comprehension checks.

```yaml
profile: chatbot_tutor
version: "0.1"
description: "Full cognitive scaffolding for interactive tutoring"

layers:
  activation:
    enabled: true
    required: true
    weight: 1.0
  metaphor:
    enabled: true
    required: false
    weight: 2.0
  structure:
    enabled: true
    required: true
    weight: 2.0
  interrogation:
    enabled: true
    required: true
    weight: 2.0
  encoding:
    enabled: true
    required: true
    weight: 1.0
  transfer:
    enabled: true
    required: true
    weight: 2.0
  reflection:
    enabled: true
    required: true
    weight: 1.0

evaluation:
  grading_enabled: true
  misconception_probes: true
  regeneration_threshold: 0.35

output:
  format: conversational
  include_provenance: false
```

**Key characteristics:**
- All 7 layers enabled
- Activation and Encoding are required (guaranteed engagement and retention)
- Heavy weight on Structure, Interrogation, Transfer (comprehension core)

### Profile 2: `rag_explainer`

**Purpose:** Grounded explanations based on retrieved documents. Optimizes for accuracy, citation, and boundary conditions.

```yaml
profile: rag_explainer
version: "0.1"
description: "Retrieval-grounded explanation with citation"

layers:
  activation:
    enabled: false
    required: false
    weight: 0.0
  metaphor:
    enabled: true
    required: false
    weight: 1.5
  structure:
    enabled: true
    required: true
    weight: 2.5
  interrogation:
    enabled: false
    required: false
    weight: 0.0
  encoding:
    enabled: false
    required: false
    weight: 0.0
  transfer:
    enabled: true
    required: false
    weight: 2.0
  reflection:
    enabled: false
    required: false
    weight: 0.0

evaluation:
  grading_enabled: true
  misconception_probes: false
  regeneration_threshold: 0.25

output:
  format: structured_answer
  include_provenance: true
  include_citations: true
  fast_mode: true
```

**Key characteristics:**
- Metaphor + Structure + Transfer enabled; others disabled
- Structure is required and heavily weighted (accuracy focus)
- Fast mode for low-latency retrieval contexts
- Provenance and citations mandatory

### Profile 3: `etl_explain`

**Purpose:** Explain ETL transformations, anomalies, schema semantics. Outputs actionable runbooks.

```yaml
profile: etl_explain
version: "0.1"
description: "ETL pipeline explanation and diagnostics"

layers:
  activation:
    enabled: false
    required: false
    weight: 0.0
  metaphor:
    enabled: false
    required: false
    weight: 0.0
  structure:
    enabled: true
    required: true
    weight: 3.0
  interrogation:
    enabled: false
    required: false
    weight: 0.0
  encoding:
    enabled: false
    required: false
    weight: 0.0
  transfer:
    enabled: false
    required: false
    weight: 0.0
  reflection:
    enabled: false
    required: false
    weight: 0.0

evaluation:
  grading_enabled: true
  misconception_probes: false
  regeneration_threshold: 0.20

output:
  format: structured_record
  include_provenance: true
  metadata_heavy: true
  batch_friendly: true
```

**Key characteristics:**
- Structure + Grading are the primary enabled layers
- Metadata-heavy output for data pipeline integration
- Batch-friendly design for processing multiple explanations
- Provenance mandatory for lineage tracking

### Profile Comparison Matrix

| Feature | chatbot_tutor | rag_explainer | etl_explain |
|---|---|---|---|
| Activation | Required | Disabled | Disabled |
| Metaphor | Enabled | Enabled (optional) | Disabled |
| Structure | Required | Required | Required |
| Interrogation | Required | Disabled | Disabled |
| Encoding | Required | Disabled | Disabled |
| Transfer | Required | Enabled (optional) | Disabled |
| Reflection | Required | Disabled | Disabled |
| Grading | Enabled | Enabled | Enabled |
| Provenance | No | Yes | Yes |
| Citations | No | Yes | No |
| Output Format | Conversational | Structured answer | Structured record |

---

## 10. Adapters

Adapters transform a `CognitiveArtifact` into the format expected by the host system. They sit at the integration boundary and have no knowledge of how the artifact was produced.

### Adapter 1: ChatbotAdapter

**Purpose:** Format `CognitiveArtifact` as streaming chat messages with progressive disclosure.

```python
class ChatbotAdapter:
    """Transforms CognitiveArtifact into conversational chat messages."""

    def format(self, artifact: CognitiveArtifact) -> list[ChatMessage]:
        """
        Returns ordered chat messages that progressively reveal layers:
        1. Activation hook (attention grabber)
        2. Metaphor (conceptual anchor)
        3. Structure (precision)
        4. Interrogation (interactive questions, one at a time)
        5. Encoding (memory aids)
        6. Transfer (practice)
        7. Reflection (metacognition check)
        """
        ...

    def format_streaming(self, artifact: CognitiveArtifact) -> Iterator[ChatMessage]:
        """Yield messages one at a time for streaming interfaces."""
        ...
```

**Key behaviors:**
- Progressive disclosure -- layers presented sequentially as conversation turns
- Interactive interrogation -- questions delivered one at a time, awaiting response
- Warm tone adapted from the audience control vector

### Adapter 2: RAGAdapter

**Purpose:** Format `CognitiveArtifact` as enriched document chunks with metadata for vector stores.

```python
class RAGAdapter:
    """Transforms CognitiveArtifact into vector-store-ready chunks."""

    def format(self, artifact: CognitiveArtifact) -> list[EnrichedChunk]:
        """
        Returns enriched chunks suitable for vector store ingestion:
        - Each layer becomes a chunk with metadata tags
        - Citations and provenance embedded per chunk
        - Metaphor boundary conditions included as metadata
        """
        ...
```

**Key behaviors:**
- Each populated layer maps to one or more document chunks
- Metadata includes: layer name, confidence score, audience vector, provenance
- Metaphor boundary conditions surfaced as explicit metadata (prevents false grounding)
- Citation links preserved from source retrieval

### Adapter 3: ETLAdapter

**Purpose:** Format `CognitiveArtifact` as structured records for data pipelines.

```python
class ETLAdapter:
    """Transforms CognitiveArtifact into structured data pipeline records."""

    def format(self, artifact: CognitiveArtifact) -> dict[str, Any]:
        """
        Returns a flat or nested dict/JSON suitable for:
        - Database insertion
        - Data pipeline message queues
        - Batch processing systems
        """
        ...

    def format_batch(self, artifacts: list[CognitiveArtifact]) -> list[dict[str, Any]]:
        """Format multiple artifacts for batch processing."""
        ...
```

**Key behaviors:**
- Output is JSON/dict, not conversational text
- Metadata-heavy: includes provenance, scores, diagnostic flags
- Batch-friendly: `format_batch()` processes lists efficiently
- Schema-stable: output structure does not change between calls

---

## 11. Migration Strategy

### Approach: Option B -- Fat Operator Wrapping

The `MetaphorOperator` wraps the existing `MetaphorEngine` from the `metaphor-mcp-server` project as a **"fat operator" via import**, not code copy.

```python
# src/cognitive_scaffolding/operators/metaphor.py

from metaphor_mcp_server.engine import MetaphorEngine  # import, not copy

class MetaphorOperator(BaseOperator):
    def __init__(self):
        self.engine = MetaphorEngine()  # Existing engine, fully reused

    def execute(self, topic, audience, context, config=None):
        # Delegate to existing engine
        result = self.engine.generate_metaphors(
            concept=topic,
            audience=audience.label,
            domain=config.get("domain") if config else None,
        )
        return LayerOutput(
            content=result,
            confidence=self._assess_confidence(result),
            provenance=self._record_provenance(topic, audience),
        )
```

### Shared Infrastructure

Resources that are common between the metaphor-mcp-server and cognitive_scaffolding are **copied** into `cognitive_scaffolding`:

- **Models** -- audience profiles, concept definitions (copied to `data/`)
- **Utils** -- YAML loading utilities, AI client abstraction (copied to `utils/`)
- **Data** -- concept YAMLs, audience YAMLs, domain YAMLs, template YAMLs (copied to `data/`)

### Future Refactoring

Later iterations can extract shared code into a common package (e.g., `cognitive-common`) that both projects depend on. This is not a v0.1 requirement.

---

## 12. Non-Goals (v0.1)

The following are explicitly out of scope for the initial release:

| Non-Goal | Rationale |
|---|---|
| Real-time streaming of partial artifacts | Adds complexity to the conductor loop; not needed for initial validation |
| Multi-concept dependency graphs | Single-concept compilation is sufficient to prove the architecture |
| Persistent storage | All artifacts are in-memory; no database, no file persistence |
| Authentication / authorization | Middleware is called by trusted host systems in v0.1 |
| UI / frontend | No Streamlit, no web interface; API-only |
| Multi-language support | English only for v0.1 |
| Concurrent operator execution | Operators run sequentially; parallel execution is a future optimization |

---

## 13. Data Assets

### Audiences (18 profiles)

Located in `data/audiences/`. Each YAML defines:

- `audience_id`, `name`, `description`
- `characteristics`, `preferred_metaphors`, `language_style`
- Optional: `parent`, `age_range`, `show_formulas`, `show_code`, `complexity_preference`

**Current audiences include:** academics, business, business_analyst, communications, data_analyst, data_scientist, financial_analyst, genai_engineer, general, geospatial_professional, investor_relations, marketing_professional, ml_engineer, policy_maker, technical, technical_workers

### Concepts (200+)

Located in `data/concepts/`. Each YAML defines a concept with metadata including domain, prerequisites, and related concepts. Coverage spans AI/ML, data engineering, ethics, tooling, and domain applications.

### Domains (25+)

Located in `data/domains/`. Each YAML defines a metaphor domain with:

- Domain name and description
- Available metaphor mappings
- Source-target correspondences

**Current domains include:** city_map, city_power_grid, construction_architecture, cooking_culinary, dog_man_walking, ecosystem_biology, educational_progression, factory_assembly_line, farmers_market, filing_cabinet, financial_economics, garden_ecosystem, general, highway_system, library_catalog, manufacturing_production, medical_healthcare, navigation_movement, orchestra_conductor, research_collaboration, restaurant, restaurant_kitchen, service_coordination, signal_transformation, social_interaction, sports_athletics, storytelling_narrative, symphony_tuning, transport_logistics

### Templates (14 explanation styles)

Located in `data/templates/`. Includes:

- **explanation_styles.yaml** -- 14 styles: extended_metaphor, comparative_metaphor, quick_analogy, progressive_revelation, interactive_dialogue, narrative_journey, visual_construction, problem_solution_cycle, misconception_decoder, ecosystem_perspective, hands_on_workshop, temporal_evolution, multi_perspective_lens, failure_recovery_cycle
- **diagram_templates.yaml** -- Diagram generation templates
- **manim_components.yaml** -- Animation component definitions
- **basic_explanation.yaml** -- Simple explanation template

---

## 14. Key Interfaces and Types

### Core Types

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class AudienceProfile:
    """7-dimensional control vector for audience adaptation."""
    label: str
    control_vector: dict[str, float]  # keys: l, a, r, m, d, k, t

    def validate(self) -> bool:
        required_keys = {"l", "a", "r", "m", "d", "k", "t"}
        return (
            set(self.control_vector.keys()) == required_keys
            and all(0.0 <= v <= 1.0 for v in self.control_vector.values())
        )

@dataclass
class ProvenanceRecord:
    """Tracks a single operator invocation."""
    operator: str
    timestamp_utc: str
    inputs_hash: str
    model_version: str | None = None
    output_keys: list[str] = field(default_factory=list)

@dataclass
class LayerOutput:
    """Output from a single operator."""
    content: dict[str, Any]
    confidence: float
    provenance: ProvenanceRecord

@dataclass
class RevisionRecord:
    """Tracks a single mutation to the artifact."""
    timestamp_utc: str
    layer: str
    operator: str
    reason: str  # "initial" | "regeneration" | "override"
    previous_confidence: float | None
    new_confidence: float

@dataclass
class EvaluationResult:
    """Output from the GradingOperator."""
    layer_scores: dict[str, float]
    overall_score: float
    diagnostics: list[str]
    missing_critical: list[str]
    revision_plan: dict[str, Any] | None

@dataclass
class CognitiveArtifact:
    """Core intermediate representation."""
    topic: str
    audience_profile: AudienceProfile

    activation: LayerOutput | None = None
    metaphor: LayerOutput | None = None
    structure: LayerOutput | None = None
    interrogation: LayerOutput | None = None
    encoding: LayerOutput | None = None
    transfer: LayerOutput | None = None
    reflection: LayerOutput | None = None

    evaluation: EvaluationResult | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    revision_history: list[RevisionRecord] = field(default_factory=list)
```

### Formal Relationships

The system can be expressed as:

```
CognitiveArtifact = Orchestrator(Input, Profile, Audience)
```

Where:

```
Artifact = ( Product over m in Profile ) Operator_m (Input)
```

The profile determines the set of active operators:

```
Profile_chatbot  = {A, M, S, I, E, T, R, G}
Profile_rag      = {M, S, T, G}
Profile_etl      = {S, G}
```

---

## 15. Testing Strategy

### Unit Tests

Located in `tests/unit/`. Each operator and core component gets dedicated test coverage:

- **Operator tests** -- Each operator's `execute()`, `build_prompt()`, and `validate_output()` are tested independently with mock context
- **Scoring tests** -- Verify weighted scoring formula, penalty multiplier, disabled-layer exclusion
- **Audience tests** -- Validate control vector ranges, audience profile loading
- **Toggle tests** -- Verify three-level resolution (profile -> override -> experiment)

### Integration Tests

Located in `tests/integration/`. End-to-end compilation flows:

- **Profile compilation** -- Run full compilation loop for each profile with a known topic/audience pair
- **Schema validation** -- Verify all operator outputs conform to JSON schema contracts
- **Regeneration** -- Verify that targeted regeneration produces improved scores
- **Adapter output** -- Verify each adapter produces well-formed output from a completed artifact

### Dependencies

Specified in `pyproject.toml`:

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

## Appendix A: Architectural Decision Summary

| Decision | Choice | Rationale |
|---|---|---|
| Core artifact name | `CognitiveArtifact` (not `LessonArtifact`) | Broader than education -- covers explanation, debugging, synthesis |
| Versioning | Mutable with linear revision history | Simplest model that provides audit trail; no branching needed for v0.1 |
| Operator communication | Via conductor context dict, never direct | Clean separation; operators remain independently testable |
| Migration strategy | Fat operator wrap via import | Reuses MetaphorEngine without code duplication; clean boundary |
| Shared data | Copy into cognitive_scaffolding | Independence from metaphor-mcp-server; later unify via common package |
| Operator naming | `operators/` (not `mcps/`) | More abstract; does not assume MCP transport in v0.1 |
| Profile format | YAML | Consistent with existing data assets; human-editable |

## Appendix B: Cognitive Architecture Diagram

```
[Activation]
      |
[Metaphor / Anchoring]
      |
[Structure]
      |
[Interrogation]
      |
[Encoding]
      |
[Transfer]
      |
[Reflection]
      |  (loops back if grading detects weakness)
      v
[Grading] ---> if weak ---> targeted regeneration
```

Learning is not linear -- it is a state machine with recursive entry points:

- Failed Transfer -> return to Structure
- Weak Encoding -> return to Interrogation
- High misconception risk -> regenerate Metaphor + Structure + Interrogation

The state evolves iteratively: `S(n+1) = f(S(n), Feedback)`
