from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import reduce

from apply_delta import apply_delta
from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from models.process_event_result import ProcessEventResult
from pipeline.add_event_stage import add_event_stage
from pipeline.run_workflow import run_workflow
from models.todo_item_category import TodoItemCategory
from workflows.registry import ALL_WORKFLOWS

# Temporarily limit to treatment only
_ENABLED_CATEGORIES = {TodoItemCategory.TREATMENT}
_ACTIVE_WORKFLOWS = {
    k: v for k, v in ALL_WORKFLOWS.items() if k in _ENABLED_CATEGORIES
}
from workflows.workflow import Workflow


def _run_workflow(
    event: ClaimEvent, state: ClaimState, workflow: Workflow
) -> ClaimStateDelta:
    delta = ClaimStateDelta()
    return run_workflow(event, state, delta, workflow)


def _merge_deltas(deltas: list[ClaimStateDelta]) -> ClaimStateDelta:
    return reduce(lambda a, b: a.merge(b), deltas, ClaimStateDelta())


def process_event(state: ClaimState, event: ClaimEvent) -> ProcessEventResult:
    """Process a claim event through all workflow stages and return updated state with delta."""
    event_delta = ClaimStateDelta()
    event_delta = add_event_stage(event, event_delta)

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(_run_workflow, event, state, wf): wf
            for wf in _ACTIVE_WORKFLOWS.values()
        }
        workflow_deltas = [f.result() for f in as_completed(futures)]

    delta = _merge_deltas([event_delta, *workflow_deltas])
    return ProcessEventResult(state=apply_delta(state, delta), delta=delta)
