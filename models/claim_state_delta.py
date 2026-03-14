from pydantic import BaseModel

from models.event_delta import EventDelta
from models.todo_item_delta import TodoItemDelta


class ClaimStateDelta(BaseModel):
    events: EventDelta = EventDelta()
    open_items: TodoItemDelta = TodoItemDelta()
    closed_items: TodoItemDelta = TodoItemDelta()
