from pydantic import BaseModel, model_validator


class Trigger(BaseModel):
    when: str
    mandatory: bool = False
    action: str

    @model_validator(mode="after")
    def requires_action(self) -> "Trigger":
        if not self.action:
            raise ValueError("Triggers must have an 'action' field.")
        return self
