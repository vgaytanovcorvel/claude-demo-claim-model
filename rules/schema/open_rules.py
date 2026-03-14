from pydantic import BaseModel

from rules.schema.duplication_rule_set import DuplicationRuleSet
from rules.schema.trigger import Trigger


class OpenRules(BaseModel):
    triggers: list[Trigger]
    exclusions: list[str]
    duplication_rules: dict[str, DuplicationRuleSet] | None = None
    preamble: str | None = None
