from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from pipeline.run_tool_loop import run_tool_loop
from pipeline.workflow_tools import (
    build_user_message,
    make_add_open_item_tool,
    make_cancel_tool,
    make_close_tool,
    make_create_entity_tool,
    make_delete_entity_tool,
    make_start_workflow_tool,
    make_update_entity_tool,
)
from prompt_telemetry import log_workflow
from workflows.workflow import Workflow

MAX_DEPTH = 5


def run_workflow(
    event: ClaimEvent,
    state: ClaimState,
    delta: ClaimStateDelta,
    workflow: Workflow,
    depth: int = 0,
    max_depth: int = MAX_DEPTH,
) -> ClaimStateDelta:
    """Execute a single workflow: one LLM call with all 4 tools."""
    category = workflow.category
    wf_id = workflow.workflow_id
    evt_id = event.claim_event_id

    log_workflow(
        workflow_id=wf_id,
        category=category.value if category else None,
        depth=depth,
    )

    tools = [
        make_add_open_item_tool(delta, category, wf_id, evt_id),
        make_close_tool(state, delta, category, wf_id, evt_id),
        make_cancel_tool(state, delta, category, wf_id, evt_id),
        make_create_entity_tool(delta, evt_id, wf_id),
        make_update_entity_tool(state, delta, wf_id),
        make_delete_entity_tool(state, delta, evt_id, wf_id),
        make_start_workflow_tool(
            event, state, delta, depth, max_depth, parent_workflow_id=wf_id
        ),
    ]

    user_message = build_user_message(event, state, delta, category)

    return run_tool_loop(workflow.system_prompt, user_message, tools, delta)
