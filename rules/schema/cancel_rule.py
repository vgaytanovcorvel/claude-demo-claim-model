from pydantic import BaseModel


class CancelRule(BaseModel):
    when: str | None = None
    never: str | None = None
    applies_to: str | None = None
    example: str | None = None
