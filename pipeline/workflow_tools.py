import json
from collections.abc import Callable
from datetime import date, datetime, timezone

from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from models.entity import Entity
from models.entity_status import EntityStatus
from models.entity_type import EntityType
from models.owner import Owner
from models.todo_item import TodoItem
from models.todo_item_category import TodoItemCategory
from models.todo_item_status import TodoItemStatus
from models.urgency_type import UrgencyType
from pipeline.tool_context import ToolContext
from prompt_telemetry import log_tool_call


def make_add_open_item_tool(ctx: ToolContext) -> Callable:
    """Create an add_open_item tool closure."""

    def add_open_item(
        todo_item_id: str,
        description: str,
        owner: str,
        urgency_type: str,
        sub_category: str,
        due_on: str = "",
        context_entity_id: str = "",
    ) -> str:
        """Add a new open todo item. Provide a unique ID, description, owner (the party responsible for executing this item: adjuster, employer, provider, injured-worker, or other), urgency type (milestone-protecting, deadline-driven, or discretionary), sub_category (the sub-category from the matching branch), optionally a due_on date (YYYY-MM-DD), and optionally a context_entity_id linking this item to an entity."""
        item = TodoItem(
            todo_item_id=todo_item_id,
            created_at=datetime.now(timezone.utc),
            created_by_event_id=ctx.event_id,
            created_by_workflow_id=ctx.workflow_id,
            context_entity_id=context_entity_id or None,
            status=TodoItemStatus.OPEN,
            description=description,
            owner=Owner(owner),
            urgency_type=UrgencyType(urgency_type),
            category=ctx.category,
            sub_category=sub_category or None,
            due_on=date.fromisoformat(due_on) if due_on else None,
        )
        ctx.delta.open_items.add.append(item)
        result = f"Added open item '{todo_item_id}' in category '{ctx.category}'."
        log_tool_call(
            workflow_id=ctx.workflow_id,
            tool_name="add_open_item",
            args={
                "todo_item_id": todo_item_id,
                "description": description,
                "owner": owner,
                "urgency_type": urgency_type,
                "sub_category": sub_category,
                "due_on": due_on,
                "context_entity_id": context_entity_id,
            },
            result=result,
        )
        return result

    return add_open_item


def make_terminate_tool(ctx: ToolContext) -> Callable:
    """Create a terminate_todo_item tool closure (close or cancel)."""

    def terminate_todo_item(todo_item_id: str, reason: str) -> str:
        """Terminate an open todo item. reason must be 'closed' (work is done) or 'cancelled' (work is no longer needed). Sets the terminal status and records the timestamp."""
        if reason not in ("closed", "cancelled"):
            result = f"Error: reason must be 'closed' or 'cancelled', got '{reason}'."
            log_tool_call(
                workflow_id=ctx.workflow_id,
                tool_name="terminate_todo_item",
                args={"todo_item_id": todo_item_id, "reason": reason},
                result=result,
            )
            return result

        matching = [
            item
            for item in ctx.state.open_items
            if item.todo_item_id == todo_item_id and item.category == ctx.category
        ]
        if not matching:
            result = f"Error: todo item '{todo_item_id}' not found in open {ctx.category} items."
            log_tool_call(
                workflow_id=ctx.workflow_id,
                tool_name="terminate_todo_item",
                args={"todo_item_id": todo_item_id, "reason": reason},
                result=result,
            )
            return result

        status = (
            TodoItemStatus.CLOSED
            if reason == "closed"
            else TodoItemStatus.CANCELLED
        )
        terminated_item = matching[0].model_copy(
            update={
                "status": status,
                "terminal_at": datetime.now(timezone.utc),
                "terminated_by_event_id": ctx.event_id,
            }
        )
        ctx.delta.closed_items.add.append(terminated_item)
        ctx.delta.open_items.delete.append(todo_item_id)
        verb = "Closed" if reason == "closed" else "Cancelled"
        result = f"{verb} todo item '{todo_item_id}'."
        log_tool_call(
            workflow_id=ctx.workflow_id,
            tool_name="terminate_todo_item",
            args={"todo_item_id": todo_item_id, "reason": reason},
            result=result,
        )
        return result

    return terminate_todo_item


def _cancel_items_linked_to_entity(ctx: ToolContext, entity_id: str) -> list[str]:
    """Cancel all open items in this workflow's category that reference the given entity.

    Returns a list of cancelled item IDs.
    """
    cancelled_ids: list[str] = []
    for item in ctx.state.open_items:
        if item.context_entity_id == entity_id and item.category == ctx.category:
            cancelled = item.model_copy(
                update={
                    "status": TodoItemStatus.CANCELLED,
                    "terminal_at": datetime.now(timezone.utc),
                    "terminated_by_event_id": ctx.event_id,
                }
            )
            ctx.delta.closed_items.add.append(cancelled)
            ctx.delta.open_items.delete.append(item.todo_item_id)
            cancelled_ids.append(item.todo_item_id)
    return cancelled_ids


def make_create_entity_tool(ctx: ToolContext) -> Callable:
    """Create a create_entity tool closure."""

    def create_entity(
        entity_id: str,
        entity_type: str,
        description: str,
    ) -> str:
        """Create a new entity (diagnosis or treatment). Provide a unique entity_id, entity_type (diagnosis or treatment), and a description."""
        entity = Entity(
            entity_id=entity_id,
            entity_type=EntityType(entity_type),
            description=description,
            status=EntityStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            created_by_event_id=ctx.event_id,
            created_by_workflow_id=ctx.workflow_id,
        )
        ctx.delta.entities.add.append(entity)
        result = f"Created entity '{entity_id}' ({entity_type})."
        log_tool_call(
            workflow_id=ctx.workflow_id,
            tool_name="create_entity",
            args={
                "entity_id": entity_id,
                "entity_type": entity_type,
                "description": description,
            },
            result=result,
        )
        return result

    return create_entity


def make_update_entity_tool(ctx: ToolContext) -> Callable:
    """Create an update_entity tool closure."""

    def update_entity(entity_id: str, description: str) -> str:
        """Update an existing entity's description. Provide the entity_id and the new description."""
        matching = [e for e in ctx.state.entities if e.entity_id == entity_id]
        if not matching:
            result = f"Error: entity '{entity_id}' not found."
            log_tool_call(
                workflow_id=ctx.workflow_id,
                tool_name="update_entity",
                args={"entity_id": entity_id, "description": description},
                result=result,
            )
            return result
        updated = matching[0].model_copy(update={"description": description})
        ctx.delta.entities.update.append(updated)
        result = f"Updated entity '{entity_id}'."
        log_tool_call(
            workflow_id=ctx.workflow_id,
            tool_name="update_entity",
            args={"entity_id": entity_id, "description": description},
            result=result,
        )
        return result

    return update_entity


def make_delete_entity_tool(ctx: ToolContext) -> Callable:
    """Create a delete_entity tool closure (logical delete via superseded status).

    Automatically cancels all open items in this workflow's category
    that reference the superseded entity via context_entity_id.
    """

    def delete_entity(entity_id: str) -> str:
        """Delete (supersede) an entity by its ID. The entity remains in state with status superseded. All open items linked to this entity via context_entity_id are automatically cancelled."""
        matching = [e for e in ctx.state.entities if e.entity_id == entity_id]
        if not matching:
            result = f"Error: entity '{entity_id}' not found."
            log_tool_call(
                workflow_id=ctx.workflow_id,
                tool_name="delete_entity",
                args={"entity_id": entity_id},
                result=result,
            )
            return result
        superseded = matching[0].model_copy(
            update={
                "status": EntityStatus.SUPERSEDED,
                "terminal_at": datetime.now(timezone.utc),
                "terminated_by_event_id": ctx.event_id,
            }
        )
        ctx.delta.entities.update.append(superseded)

        cancelled_ids = _cancel_items_linked_to_entity(ctx, entity_id)

        parts = [f"Superseded entity '{entity_id}'."]
        if cancelled_ids:
            parts.append(
                f"Auto-cancelled {len(cancelled_ids)} linked item(s): "
                + ", ".join(cancelled_ids)
                + "."
            )
        result = " ".join(parts)
        log_tool_call(
            workflow_id=ctx.workflow_id,
            tool_name="delete_entity",
            args={"entity_id": entity_id},
            result=result,
        )
        return result

    return delete_entity


def make_start_workflow_tool(
    event: ClaimEvent,
    ctx: ToolContext,
    depth: int,
    max_depth: int,
) -> Callable:
    """Create a start_workflow tool that recursively calls run_workflow."""

    def start_workflow(workflow_id: str) -> str:
        """Start a sub-workflow by its workflow_id. Use this to invoke another workflow when the current branch instructions call for it."""
        from workflows.registry import WORKFLOW_INDEX

        if depth >= max_depth:
            result = f"Error: max workflow depth ({max_depth}) reached. Cannot start '{workflow_id}'."
            log_tool_call(
                workflow_id=ctx.workflow_id,
                tool_name="start_workflow",
                args={"workflow_id": workflow_id},
                result=result,
            )
            return result
        workflow = WORKFLOW_INDEX.get(workflow_id)
        if not workflow:
            available = ", ".join(sorted(WORKFLOW_INDEX.keys()))
            result = (
                f"Error: workflow '{workflow_id}' not found. Available: {available}"
            )
            log_tool_call(
                workflow_id=ctx.workflow_id,
                tool_name="start_workflow",
                args={"workflow_id": workflow_id},
                result=result,
            )
            return result

        from pipeline.run_workflow import run_workflow

        run_workflow(event, ctx.state, ctx.delta, workflow, depth + 1, max_depth)
        result = f"Completed sub-workflow '{workflow_id}'."
        log_tool_call(
            workflow_id=ctx.workflow_id,
            tool_name="start_workflow",
            args={"workflow_id": workflow_id},
            result=result,
        )
        return result

    return start_workflow


def build_user_message(
    event: ClaimEvent,
    state: ClaimState,
    delta: ClaimStateDelta,
    category: TodoItemCategory | None,
) -> str:
    """Build the user message for a workflow LLM call."""
    category_open_items = (
        [item for item in state.open_items if item.category == category]
        if category
        else state.open_items
    )
    category_closed_items = (
        [item for item in state.closed_items if item.category == category]
        if category
        else state.closed_items
    )

    return json.dumps(
        {
            "event": event.model_dump(mode="json"),
            "entities": [entity.model_dump(mode="json") for entity in state.entities],
            "open_items": [
                item.model_dump(mode="json") for item in category_open_items
            ],
            "closed_items": [
                item.model_dump(mode="json") for item in category_closed_items
            ],
            "accumulated_delta": {
                "description": (
                    "This is the accumulated delta so far. "
                    "It shows items already added, closed, or cancelled. "
                    "Use this to understand the full picture and avoid "
                    "duplicating work."
                ),
                "entities_delta": delta.entities.model_dump(mode="json"),
                "open_items_delta": delta.open_items.model_dump(mode="json"),
                "closed_items_delta": delta.closed_items.model_dump(mode="json"),
            },
        }
    )
