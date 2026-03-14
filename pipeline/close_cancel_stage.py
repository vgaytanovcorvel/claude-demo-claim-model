import json
from collections.abc import Callable
from datetime import datetime, timezone

from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from models.todo_item_status import TodoItemStatus
from pipeline.run_tool_loop import run_tool_loop
from rules.category_rules import CategoryRules


def _make_close_tool(
    state: ClaimState, delta: ClaimStateDelta, rules: CategoryRules
) -> Callable[[str], str]:
    """Create a close_todo_item tool closure capturing state and delta."""

    def close_todo_item(todo_item_id: str) -> str:
        """Close an open todo item by its ID. Sets status to closed and records terminal_at timestamp."""
        matching = [
            item
            for item in state.open_items
            if item.todo_item_id == todo_item_id and item.category == rules.category
        ]
        if not matching:
            return f"Error: todo item '{todo_item_id}' not found in open {rules.category} items."
        item = matching[0]
        closed_item = item.model_copy(
            update={
                "status": TodoItemStatus.CLOSED,
                "terminal_at": datetime.now(timezone.utc),
            }
        )
        delta.closed_items.add.append(closed_item)
        delta.open_items.delete.append(todo_item_id)
        return f"Closed todo item '{todo_item_id}'."

    return close_todo_item


def _make_cancel_tool(
    state: ClaimState, delta: ClaimStateDelta, rules: CategoryRules
) -> Callable[[str], str]:
    """Create a cancel_todo_item tool closure capturing state and delta."""

    def cancel_todo_item(todo_item_id: str) -> str:
        """Cancel an open todo item by its ID. Sets status to cancelled and records terminal_at timestamp."""
        matching = [
            item
            for item in state.open_items
            if item.todo_item_id == todo_item_id and item.category == rules.category
        ]
        if not matching:
            return f"Error: todo item '{todo_item_id}' not found in open {rules.category} items."
        item = matching[0]
        cancelled_item = item.model_copy(
            update={
                "status": TodoItemStatus.CANCELLED,
                "terminal_at": datetime.now(timezone.utc),
            }
        )
        delta.closed_items.add.append(cancelled_item)
        delta.open_items.delete.append(todo_item_id)
        return f"Cancelled todo item '{todo_item_id}'."

    return cancel_todo_item


def close_cancel_stage(
    event: ClaimEvent, state: ClaimState, delta: ClaimStateDelta, rules: CategoryRules
) -> ClaimStateDelta:
    """LLM stage that examines the event and decides which open items to close or cancel for a category."""
    category_open_items = [
        item for item in state.open_items if item.category == rules.category
    ]
    if not category_open_items:
        return delta

    user_message = json.dumps(
        {
            "event": event.model_dump(mode="json"),
            "open_items": [
                item.model_dump(mode="json") for item in category_open_items
            ],
            "accumulated_delta": {
                "description": (
                    "This is the accumulated delta so far for this category. "
                    "It shows items already marked for closing/cancellation or "
                    "addition by prior stages. Use this to avoid conflicts."
                ),
                "open_items_delta": delta.open_items.model_dump(mode="json"),
                "closed_items_delta": delta.closed_items.model_dump(mode="json"),
            },
        }
    )
    tools = [
        _make_close_tool(state, delta, rules),
        _make_cancel_tool(state, delta, rules),
    ]
    return run_tool_loop(rules.close_cancel_system_prompt, user_message, tools, delta)
