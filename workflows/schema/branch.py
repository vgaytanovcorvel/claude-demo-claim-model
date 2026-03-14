from pydantic import BaseModel


class Branch(BaseModel):
    name: str
    trigger: str
    instructions: str
