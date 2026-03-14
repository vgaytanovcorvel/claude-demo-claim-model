# Claim State Delta

LLM-powered claim event processing pipeline. Processes insurance claim events through sequential stages using Google Gemini, building delta objects that are applied to claim state.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Google Cloud service account with Vertex AI User role

## Configuration

1. Place your GCP service account key JSON file somewhere accessible (e.g. `C:\vertex-ai\`).

2. Create a `.env` file in the project root:

```env
GOOGLE_APPLICATION_CREDENTIALS=C:\vertex-ai\your-key-file.json
VERTEX_PROJECT=your-gcp-project-id
VERTEX_LOCATION=us-central1
```

## Install

```bash
uv sync
```

## Run

Process the sample events:

```bash
uv run python main.py
```

Process a custom events file:

```bash
uv run python main.py path/to/events.yaml
```

### Events file format

YAML list of claim events:

```yaml
- claim_event_id: evt-001
  timestamp: "2026-03-10T09:00:00Z"
  content: "Description of the claim event."

- claim_event_id: evt-002
  timestamp: "2026-03-11T14:30:00Z"
  content: "Another event in the claim timeline."
```

## Prompt Telemetry

Every Gemini API call is logged to `output/telemetry/prompts.jsonl`. Each line is a JSON object with:

- `timestamp` — UTC ISO format
- `model` — model used (e.g. `gemini-2.5-pro`)
- `system_prompt` — system instruction, if any
- `user_message` — the full prompt sent to the model
- `response_text` — the model's response
- `tools` — list of tool function names (for tool-calling requests)

The log file is created automatically on the first run. To review captured prompts:

```bash
# Pretty-print all entries
cat output/telemetry/prompts.jsonl | python -m json.tool

# Show just the user messages (first 200 chars each)
python -c "import json; [print(json.loads(l)['user_message'][:200]) for l in open('output/telemetry/prompts.jsonl')]"
```

## Test

```bash
uv run pytest -v
```

## Lint / Format

```bash
uv run ruff check .
uv run ruff format .
```
