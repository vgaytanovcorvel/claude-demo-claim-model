from pydantic import BaseModel


class Trigger(BaseModel):
    when: str
    mandatory: bool = False
    action: str | None = None
