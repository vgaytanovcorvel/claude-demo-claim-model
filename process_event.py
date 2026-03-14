from apply_delta import apply_delta
from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from pipeline.add_event_stage import add_event_stage
from pipeline.close_cancel_stage import close_cancel_stage
from pipeline.open_items_stage import open_items_stage


def process_event(state: ClaimState, event: ClaimEvent) -> ClaimState:
    """Process a claim event through all pipeline stages and return updated state."""
    delta = ClaimStateDelta()
    delta = add_event_stage(event, delta)
    delta = close_cancel_stage(event, state, delta)
    intermediate_state = apply_delta(state, delta)
    delta = open_items_stage(event, intermediate_state, delta)
    return apply_delta(state, delta)
