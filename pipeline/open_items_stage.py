import json
from collections.abc import Callable
from datetime import datetime, timezone

from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from models.todo_item import TodoItem
from models.todo_item_status import TodoItemStatus
from models.urgency_type import UrgencyType
from pipeline.run_tool_loop import run_tool_loop


def _make_add_open_item_tool(
    delta: ClaimStateDelta,
) -> Callable[[str, str, str, str], str]:
    """Create an add_open_item tool closure capturing delta."""

    def add_open_item(
        todo_item_id: str, description: str, owner: str, urgency_type: str
    ) -> str:
        """Add a new open todo item. Provide a unique ID, description, owner, and urgency type (milestone-protecting, deadline-driven, or discretionary)."""
        item = TodoItem(
            todo_item_id=todo_item_id,
            created_at=datetime.now(timezone.utc),
            status=TodoItemStatus.OPEN,
            description=description,
            owner=owner,
            urgency_type=UrgencyType(urgency_type),
        )
        delta.open_items.add.append(item)
        return f"Added open item '{todo_item_id}'."

    return add_open_item


def open_items_stage(
    event: ClaimEvent, state: ClaimState, delta: ClaimStateDelta
) -> ClaimStateDelta:
    """LLM stage that creates new todo items based on the event."""
    system_prompt = (
        "You are a claim processing assistant. Based on the provided claim event, "
        "create new todo items that need to be done. Do not duplicate any existing "
        "open items. Use add_open_item to create each new item. "
        "Valid urgency types are: milestone-protecting, deadline-driven, discretionary."
    )
    user_message = json.dumps(
        {
            "event": event.model_dump(mode="json"),
            "open_items": [item.model_dump(mode="json") for item in state.open_items],
            "closed_items": [
                item.model_dump(mode="json") for item in state.closed_items
            ],
        }
    )
    tools = [_make_add_open_item_tool(delta)]
    return run_tool_loop(system_prompt, user_message, tools, delta)
