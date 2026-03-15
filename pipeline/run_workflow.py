from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from pipeline.run_tool_loop import run_tool_loop
from pipeline.tool_context import ToolContext
from pipeline.workflow_tools import (
    build_user_message,
    make_add_open_item_tool,
    make_create_entity_tool,
    make_delete_entity_tool,
    make_start_workflow_tool,
    make_terminate_tool,
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
    """Execute a single workflow: one LLM call with all tools."""
    category = workflow.category
    wf_id = workflow.workflow_id
    evt_id = event.claim_event_id

    log_workflow(
        workflow_id=wf_id,
        category=category.value if category else None,
        depth=depth,
    )

    ctx = ToolContext(
        state=state,
        delta=delta,
        category=category,
        workflow_id=wf_id,
        event_id=evt_id,
    )

    tools = [
        make_add_open_item_tool(ctx),
        make_terminate_tool(ctx),
        make_create_entity_tool(ctx),
        make_update_entity_tool(ctx),
        make_delete_entity_tool(ctx),
        make_start_workflow_tool(event, ctx, depth, max_depth),
    ]

    user_message = build_user_message(event, state, delta, category)

    return run_tool_loop(workflow.system_prompt, user_message, tools, delta)
