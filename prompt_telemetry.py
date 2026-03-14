import json
from datetime import datetime, timezone
from pathlib import Path

_LOG_DIR = Path(__file__).parent / "output" / "telemetry"

_RUN_TIMESTAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
_LOG_FILE = _LOG_DIR / f"run_{_RUN_TIMESTAMP}.jsonl"


def _append(entry: dict) -> None:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def log_prompt_request(
    *,
    system_prompt: str | None = None,
    user_message: str,
    model: str,
    tools: list[str] | None = None,
) -> None:
    _append(
        {
            "type": "llm_request",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "system_prompt": system_prompt,
            "user_message": user_message,
            "tools": tools,
        }
    )


def log_prompt_response(
    *,
    response_text: str | None = None,
    model: str,
) -> None:
    _append(
        {
            "type": "llm_response",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "response_text": response_text,
        }
    )


def log_workflow(
    *,
    workflow_id: str,
    category: str | None,
    depth: int,
) -> None:
    _append(
        {
            "type": "workflow_start",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "workflow_id": workflow_id,
            "category": category,
            "depth": depth,
        }
    )


def log_tool_call(
    *,
    workflow_id: str,
    tool_name: str,
    args: dict,
    result: str,
) -> None:
    _append(
        {
            "type": "tool_call",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "workflow_id": workflow_id,
            "tool_name": tool_name,
            "args": args,
            "result": result,
        }
    )
