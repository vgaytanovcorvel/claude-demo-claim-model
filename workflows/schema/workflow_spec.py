from pydantic import BaseModel

from models.todo_item_category import TodoItemCategory
from rules.schema.defaults import Defaults
from rules.schema.owner_rule import OwnerRule
from workflows.schema.branch import Branch


class WorkflowSpec(BaseModel):
    workflow_id: str
    category: TodoItemCategory | None = None
    description: str
    branches: list[Branch]
    exclusions: list[str] = []
    owner_guidance: list[OwnerRule] = []
    defaults: Defaults = Defaults()
