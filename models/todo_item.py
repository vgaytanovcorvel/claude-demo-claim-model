from datetime import date, datetime

from pydantic import BaseModel

from models.owner import Owner
from models.todo_item_category import TodoItemCategory
from models.todo_item_status import TodoItemStatus
from models.urgency_type import UrgencyType


class TodoItem(BaseModel):
    todo_item_id: str
    created_at: datetime
    created_by_event_id: str | None = None
    created_by_workflow_id: str | None = None
    terminal_at: datetime | None = None
    terminated_by_event_id: str | None = None
    context_entity_id: str | None = None
    status: TodoItemStatus
    description: str
    owner: Owner
    urgency_type: UrgencyType
    category: TodoItemCategory
    sub_category: str | None = None
    due_on: date | None = None
