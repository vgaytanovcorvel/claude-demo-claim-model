import json
from collections.abc import Callable
from datetime import date, datetime, timezone

from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from models.todo_item import TodoItem
from models.owner import Owner
from models.todo_item_status import TodoItemStatus
from models.urgency_type import UrgencyType
from pipeline.run_tool_loop import run_tool_loop
from rules.category_rules import CategoryRules


def _make_add_open_item_tool(
    delta: ClaimStateDelta, rules: CategoryRules
) -> Callable[[str, str, str, str], str]:
    """Create an add_open_item tool closure capturing delta and category."""

    def add_open_item(
        todo_item_id: str,
        description: str,
        owner: str,
        urgency_type: str,
        sub_category: str,
        due_on: str = "",
    ) -> str:
        """Add a new open todo item. Provide a unique ID, description, owner (the party responsible for executing this item: adjuster, employer, provider, injured-worker, or other), urgency type (milestone-protecting, deadline-driven, or discretionary), sub_category (the sub-category from the matching trigger), and optionally a due_on date (YYYY-MM-DD)."""
        item = TodoItem(
            todo_item_id=todo_item_id,
            created_at=datetime.now(timezone.utc),
            status=TodoItemStatus.OPEN,
            description=description,
            owner=Owner(owner),
            urgency_type=UrgencyType(urgency_type),
            category=rules.category,
            sub_category=sub_category or None,
            due_on=date.fromisoformat(due_on) if due_on else None,
        )
        delta.open_items.add.append(item)
        return f"Added open item '{todo_item_id}' in category '{rules.category}'."

    return add_open_item


def open_items_stage(
    event: ClaimEvent, state: ClaimState, delta: ClaimStateDelta, rules: CategoryRules
) -> ClaimStateDelta:
    """LLM stage that creates new todo items based on the event for a category."""
    category_open_items = [
        item for item in state.open_items if item.category == rules.category
    ]
    category_closed_items = [
        item for item in state.closed_items if item.category == rules.category
    ]

    user_message = json.dumps(
        {
            "event": event.model_dump(mode="json"),
            "open_items": [
                item.model_dump(mode="json") for item in category_open_items
            ],
            "closed_items": [
                item.model_dump(mode="json") for item in category_closed_items
            ],
            "accumulated_delta": {
                "description": (
                    "This is the accumulated delta so far for this category. "
                    "It shows items already added, closed, or cancelled by prior "
                    "stages in this pipeline run. Use this to understand the full "
                    "picture and avoid duplicating work."
                ),
                "open_items_delta": delta.open_items.model_dump(mode="json"),
                "closed_items_delta": delta.closed_items.model_dump(mode="json"),
            },
        }
    )
    tools = [_make_add_open_item_tool(delta, rules)]
    return run_tool_loop(rules.open_items_system_prompt, user_message, tools, delta)
