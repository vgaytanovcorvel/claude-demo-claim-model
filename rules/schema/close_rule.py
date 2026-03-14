from pydantic import BaseModel


class CloseRule(BaseModel):
    when: str
    detail: str | None = None
    applies_to: str | None = None
