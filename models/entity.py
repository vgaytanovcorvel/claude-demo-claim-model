from datetime import datetime

from pydantic import BaseModel

from models.entity_status import EntityStatus
from models.entity_type import EntityType


class Entity(BaseModel):
    entity_id: str
    entity_type: EntityType
    description: str
    status: EntityStatus
    created_at: datetime
    created_by_event_id: str
    created_by_workflow_id: str | None = None
    terminal_at: datetime | None = None
    terminated_by_event_id: str | None = None
