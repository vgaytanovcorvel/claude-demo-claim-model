from pydantic import BaseModel

from rules.schema.cancel_rule import CancelRule
from rules.schema.close_rule import CloseRule


class SubCategorySpec(BaseModel):
    name: str
    close_rules: list[CloseRule] = []
    cancel_rules: list[CancelRule] = []
