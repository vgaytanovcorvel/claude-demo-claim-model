from __future__ import annotations

from pydantic import BaseModel

from models.event_delta import EventDelta
from models.todo_item_delta import TodoItemDelta


class ClaimStateDelta(BaseModel):
    events: EventDelta = EventDelta()
    open_items: TodoItemDelta = TodoItemDelta()
    closed_items: TodoItemDelta = TodoItemDelta()

    def merge(self, other: ClaimStateDelta) -> ClaimStateDelta:
        return ClaimStateDelta(
            events=self.events.merge(other.events),
            open_items=self.open_items.merge(other.open_items),
            closed_items=self.closed_items.merge(other.closed_items),
        )
