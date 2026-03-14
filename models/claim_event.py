from datetime import datetime

from pydantic import BaseModel


class ClaimEvent(BaseModel):
    claim_event_id: str
    timestamp: datetime
    content: str
