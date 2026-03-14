from pydantic import BaseModel

from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta


class ProcessEventResult(BaseModel):
    state: ClaimState
    delta: ClaimStateDelta
