from pydantic import BaseModel

from models.claim_event import ClaimEvent


class EventDelta(BaseModel):
    add: list[ClaimEvent] = []
    update: list[ClaimEvent] = []
    delete: list[str] = []  # claim_event_id
