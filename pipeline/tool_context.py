from dataclasses import dataclass

from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from models.todo_item_category import TodoItemCategory


@dataclass
class ToolContext:
    """Bundles the shared state every workflow tool closure needs."""

    state: ClaimState
    delta: ClaimStateDelta
    category: TodoItemCategory
    workflow_id: str
    event_id: str
