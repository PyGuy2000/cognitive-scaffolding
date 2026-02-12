# Cognitive Scaffolding

**Universal understanding middleware** -- a cognitive compiler that takes any concept + audience profile and produces structured, multi-layer explanations.

## What It Does

Cognitive Scaffolding formalizes the job of "making something understood" into a 7-layer pipeline. Give it a topic and an audience, and it produces a `CognitiveArtifact` -- a channel-agnostic intermediate representation that adapters transform into chatbot messages, RAG document chunks, or flat ETL records. Each layer is independently toggleable, scorable, and regenerable.

## Architecture

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

## Quick Start

```bash
# Clone and install
git clone <repo-url> && cd cognitive_scaffolding
pip install -e ".[dev]"

# Configure AI (optional -- the pipeline works without it via template fallbacks)
cp .env.example .env
# Add your ANTHROPIC_API_KEY or OPENAI_API_KEY to .env

# Run the demo
python scripts/demo.py compile --topic "neural networks" --audience child --no-ai
```

## CLI Usage

### `compile` -- Compile a topic into structured output

```bash
# Default: chatbot format
python scripts/demo.py compile --topic "neural networks" --audience child

# RAG document chunks
python scripts/demo.py compile --topic "gradient descent" --audience data_scientist --format rag

# Flat ETL record
python scripts/demo.py compile --topic "transformers" --audience general --format etl

# Template fallbacks (no API key needed)
python scripts/demo.py compile --topic "neural networks" --audience child --no-ai
```

Options:
- `--topic` (required) -- concept to explain
- `--audience` -- audience ID: `child`, `general`, `data_scientist`, `phd` (default: `general`)
- `--format` -- output format: `chatbot`, `rag`, `etl` (default: `chatbot`)
- `--profile` -- override the default profile for the format
- `--no-ai` -- disable AI, use deterministic template fallbacks
- `--provider` / `--model` -- override AI provider and model

### `experiment` -- A/B test layer contributions

```bash
python scripts/demo.py experiment --topic "neural networks" --audience general --layers metaphor encoding
```

## Project Structure

```
cognitive_scaffolding/
  src/cognitive_scaffolding/
    core/           # Models, scoring, data loader, audience inheritance
    operators/      # 7 cognitive operators + grading operator
    orchestrator/   # Conductor, toggle manager, call plan, provenance
    adapters/       # Chatbot, RAG, ETL adapters
  profiles/         # YAML integration profiles
  data/             # 218 concepts, 16 audiences, 29 domains, templates
  utils/            # AI client, cache, YAML utilities
  scripts/          # CLI demo
  tests/            # Unit + integration tests
```

## Profiles

| Profile | Layers Enabled | Required Layers | Use Case |
|---------|---------------|-----------------|----------|
| `chatbot_tutor` | 7 | activation, structure, encoding | Interactive tutoring |
| `rag_explainer` | 3 | metaphor, structure | RAG document enrichment |
| `etl_explain` | 4 | structure | ETL pipeline explanations |

## Running Tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```
