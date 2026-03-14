from pydantic import BaseModel

from models.todo_item_category import TodoItemCategory
from rules.schema.cancel_rule import CancelRule
from rules.schema.close_rule import CloseRule
from rules.schema.defaults import Defaults
from rules.schema.open_rules import OpenRules
from rules.schema.owner_rule import OwnerRule


class CategoryRuleSpec(BaseModel):
    category: TodoItemCategory
    description: str
    close_rules: list[CloseRule]
    cancel_rules: list[CancelRule]
    open_rules: OpenRules
    owner_guidance: list[OwnerRule]
    defaults: Defaults = Defaults()
