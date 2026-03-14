from pydantic import BaseModel, model_validator

from models.todo_item_category import TodoItemCategory
from rules.schema.cancel_rule import CancelRule
from rules.schema.close_rule import CloseRule
from rules.schema.defaults import Defaults
from rules.schema.open_rules import OpenRules
from rules.schema.owner_rule import OwnerRule
from rules.schema.sub_category_spec import SubCategorySpec


class CategoryRuleSpec(BaseModel):
    category: TodoItemCategory
    description: str
    close_rules: list[CloseRule]
    cancel_rules: list[CancelRule]
    open_rules: OpenRules
    owner_guidance: list[OwnerRule]
    defaults: Defaults = Defaults()
    sub_categories: list[SubCategorySpec] = []

    @model_validator(mode="after")
    def validate_trigger_sub_categories(self) -> "CategoryRuleSpec":
        valid_names = {sc.name for sc in self.sub_categories}
        for trigger in self.open_rules.triggers:
            if (
                trigger.sub_category is not None
                and trigger.sub_category not in valid_names
            ):
                raise ValueError(
                    f"Trigger sub_category '{trigger.sub_category}' "
                    f"not found in sub_categories: {valid_names}"
                )
        return self
