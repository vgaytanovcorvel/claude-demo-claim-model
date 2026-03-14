from pydantic import BaseModel

from models.claim_event import ClaimEvent
from models.todo_item import TodoItem


class ClaimState(BaseModel):
    events: list[ClaimEvent] = []
    open_items: list[TodoItem] = []
    closed_items: list[TodoItem] = []
