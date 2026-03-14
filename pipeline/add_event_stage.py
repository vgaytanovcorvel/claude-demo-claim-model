from models.claim_event import ClaimEvent
from models.claim_state_delta import ClaimStateDelta


def add_event_stage(event: ClaimEvent, delta: ClaimStateDelta) -> ClaimStateDelta:
    """Append the event to delta.events.add. Pure Python, no LLM."""
    delta.events.add.append(event)
    return delta
