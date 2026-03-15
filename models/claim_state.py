from pydantic import BaseModel

from models.claim_event import ClaimEvent
from models.entity import Entity
from models.todo_item import TodoItem


class ClaimState(BaseModel):
    events: list[ClaimEvent] = []
    entities: list[Entity] = []
    open_items: list[TodoItem] = []
    closed_items: list[TodoItem] = []
