from datetime import datetime

from pydantic import BaseModel

from models.todo_item_category import TodoItemCategory
from models.todo_item_status import TodoItemStatus
from models.urgency_type import UrgencyType


class TodoItem(BaseModel):
    todo_item_id: str
    created_at: datetime
    terminal_at: datetime | None = None
    status: TodoItemStatus
    description: str
    owner: str
    urgency_type: UrgencyType
    category: TodoItemCategory
