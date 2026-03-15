from datetime import datetime, timezone

import pytest

from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.entity import Entity
from models.entity_status import EntityStatus
from models.entity_type import EntityType
from models.owner import Owner
from models.todo_item import TodoItem
from models.todo_item_category import TodoItemCategory
from models.todo_item_status import TodoItemStatus
from models.urgency_type import UrgencyType


@pytest.fixture
def sample_claim_event() -> ClaimEvent:
    return ClaimEvent(
        claim_event_id="evt-001",
        timestamp=datetime(2026, 3, 13, 10, 0, 0, tzinfo=timezone.utc),
        content="Adjuster completed on-site inspection. Roof damage confirmed.",
    )


def sample_todo_item(overrides: dict | None = None) -> TodoItem:
    """Factory function for creating TodoItem instances with optional overrides."""
    defaults = {
        "todo_item_id": "todo-001",
        "created_at": datetime(2026, 3, 10, 8, 0, 0, tzinfo=timezone.utc),
        "status": TodoItemStatus.OPEN,
        "description": "Schedule adjuster visit",
        "owner": Owner.ADJUSTER,
        "urgency_type": UrgencyType.MILESTONE_PROTECTING,
        "category": TodoItemCategory.TREATMENT,
    }
    if overrides:
        defaults.update(overrides)
    return TodoItem(**defaults)


def sample_entity(overrides: dict | None = None) -> Entity:
    """Factory function for creating Entity instances with optional overrides."""
    defaults = {
        "entity_id": "diagnosis-001",
        "entity_type": EntityType.DIAGNOSIS,
        "description": "Lumbar strain",
        "status": EntityStatus.ACTIVE,
        "created_at": datetime(2026, 3, 10, 8, 0, 0, tzinfo=timezone.utc),
        "created_by_event_id": "evt-000",
    }
    if overrides:
        defaults.update(overrides)
    return Entity(**defaults)


@pytest.fixture
def sample_claim_state() -> ClaimState:
    return ClaimState(
        events=[
            ClaimEvent(
                claim_event_id="evt-000",
                timestamp=datetime(2026, 3, 9, 12, 0, 0, tzinfo=timezone.utc),
                content="Claim filed for roof damage after storm.",
            ),
        ],
        open_items=[
            sample_todo_item(),
            sample_todo_item(
                {
                    "todo_item_id": "todo-002",
                    "description": "Request contractor estimate",
                    "owner": Owner.ADJUSTER,
                    "urgency_type": UrgencyType.DEADLINE_DRIVEN,
                    "category": TodoItemCategory.FINANCIAL,
                }
            ),
        ],
        closed_items=[
            sample_todo_item(
                {
                    "todo_item_id": "todo-closed-001",
                    "status": TodoItemStatus.CLOSED,
                    "description": "Verify policy coverage",
                    "owner": Owner.ADJUSTER,
                    "urgency_type": UrgencyType.DISCRETIONARY,
                    "category": TodoItemCategory.COMPLIANCE,
                    "terminal_at": datetime(2026, 3, 10, 14, 0, 0, tzinfo=timezone.utc),
                }
            ),
        ],
    )
