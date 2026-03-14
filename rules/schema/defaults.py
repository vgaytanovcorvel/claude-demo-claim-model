from pydantic import BaseModel


class Defaults(BaseModel):
    when_in_doubt: str = "leave_open"
    reason: str | None = None
    notes: list[str] | None = None
