from pydantic import BaseModel


class DuplicationRuleSet(BaseModel):
    rules: list[str]
    description_format: str | None = None
