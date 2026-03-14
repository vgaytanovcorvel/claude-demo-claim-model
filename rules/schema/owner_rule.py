from pydantic import BaseModel

from models.owner import Owner


class OwnerRule(BaseModel):
    owner: Owner
    when: str
