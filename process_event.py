from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import reduce

from apply_delta import apply_delta
from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from models.process_event_result import ProcessEventResult
from pipeline.add_event_stage import add_event_stage
from pipeline.close_cancel_stage import close_cancel_stage
from pipeline.open_items_stage import open_items_stage
from rules.category_rules import CategoryRules
from rules.registry import ALL_CATEGORY_RULES


def _run_close_cancel(
    event: ClaimEvent, state: ClaimState, rules: CategoryRules
) -> ClaimStateDelta:
    delta = ClaimStateDelta()
    return close_cancel_stage(event, state, delta, rules)


def _run_open_items(
    event: ClaimEvent, state: ClaimState, rules: CategoryRules
) -> ClaimStateDelta:
    delta = ClaimStateDelta()
    return open_items_stage(event, state, delta, rules)


def _merge_deltas(deltas: list[ClaimStateDelta]) -> ClaimStateDelta:
    return reduce(lambda a, b: a.merge(b), deltas, ClaimStateDelta())


def process_event(state: ClaimState, event: ClaimEvent) -> ProcessEventResult:
    """Process a claim event through all pipeline stages and return updated state with delta."""
    event_delta = ClaimStateDelta()
    event_delta = add_event_stage(event, event_delta)

    with ThreadPoolExecutor() as executor:
        # Fan-out close/cancel across categories in parallel
        close_futures = {
            executor.submit(_run_close_cancel, event, state, rules): rules
            for rules in ALL_CATEGORY_RULES.values()
        }
        close_deltas = [f.result() for f in as_completed(close_futures)]

    delta = _merge_deltas([event_delta, *close_deltas])
    intermediate_state = apply_delta(state, delta)

    with ThreadPoolExecutor() as executor:
        # Fan-out open items across categories in parallel
        open_futures = {
            executor.submit(_run_open_items, event, intermediate_state, rules): rules
            for rules in ALL_CATEGORY_RULES.values()
        }
        open_deltas = [f.result() for f in as_completed(open_futures)]

    delta = _merge_deltas([delta, *open_deltas])
    return ProcessEventResult(state=apply_delta(state, delta), delta=delta)
