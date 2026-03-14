from __future__ import annotations

from pydantic import BaseModel

from models.claim_event import ClaimEvent


class EventDelta(BaseModel):
    add: list[ClaimEvent] = []
    update: list[ClaimEvent] = []
    delete: list[str] = []  # claim_event_id

    def merge(self, other: EventDelta) -> EventDelta:
        return EventDelta(
            add=self.add + other.add,
            update=self.update + other.update,
            delete=self.delete + other.delete,
        )
