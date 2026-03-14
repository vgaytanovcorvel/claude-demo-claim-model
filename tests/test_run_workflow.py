from unittest.mock import patch

from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from pipeline.run_workflow import run_workflow, MAX_DEPTH
from workflows.registry import ALL_WORKFLOWS
from models.todo_item_category import TodoItemCategory


@patch("pipeline.run_workflow.log_workflow")
@patch("pipeline.workflow_tools.log_tool_call")
@patch("pipeline.run_workflow.run_tool_loop")
def test_run_workflow_calls_tool_loop(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    mock_tool_loop.side_effect = lambda system_prompt, user_message, tools, delta: delta

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    run_workflow(sample_claim_event, sample_claim_state, delta, workflow)

    assert mock_tool_loop.call_count == 1
    args = mock_tool_loop.call_args
    assert "TREATMENT" in args[0][0]  # system prompt
    # 4 tools: add_open_item, close_todo_item, cancel_todo_item, start_workflow
    assert len(args[0][2]) == 4


@patch("pipeline.run_workflow.log_workflow")
@patch("pipeline.workflow_tools.log_tool_call")
@patch("pipeline.run_workflow.run_tool_loop")
def test_run_workflow_tools_work(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    def side_effect(system_prompt, user_message, tools, delta):
        if "TREATMENT" in system_prompt:
            # tools[0] = add_open_item, tools[1] = close, tools[2] = cancel
            close_tool = tools[1]
            close_tool("todo-001")
            add_tool = tools[0]
            add_tool(
                "todo-new", "New item", "adjuster", "deadline-driven", "acute-care"
            )
        return delta

    mock_tool_loop.side_effect = side_effect

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    result = run_workflow(sample_claim_event, sample_claim_state, delta, workflow)

    assert len(result.open_items.add) == 1
    assert result.open_items.add[0].todo_item_id == "todo-new"
    assert result.open_items.add[0].created_by_event_id == "evt-001"
    assert len(result.open_items.delete) == 1
    assert "todo-001" in result.open_items.delete
    assert len(result.closed_items.add) == 1
    assert result.closed_items.add[0].terminated_by_event_id == "evt-001"


@patch("pipeline.run_workflow.log_workflow")
@patch("pipeline.workflow_tools.log_tool_call")
@patch("pipeline.run_workflow.run_tool_loop")
def test_start_workflow_tool_invokes_sub_workflow(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    call_count = {"value": 0}

    def side_effect(system_prompt, user_message, tools, delta):
        call_count["value"] += 1
        if call_count["value"] == 1:
            # First call: treatment workflow starts financial sub-workflow
            start_wf_tool = tools[3]
            result = start_wf_tool("financial")
            assert "Completed sub-workflow" in result
        return delta

    mock_tool_loop.side_effect = side_effect

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    run_workflow(sample_claim_event, sample_claim_state, delta, workflow)

    # Treatment workflow call + financial sub-workflow call
    assert call_count["value"] == 2


@patch("pipeline.run_workflow.log_workflow")
@patch("pipeline.workflow_tools.log_tool_call")
@patch("pipeline.run_workflow.run_tool_loop")
def test_start_workflow_depth_guard(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    def side_effect(system_prompt, user_message, tools, delta):
        start_wf_tool = tools[3]
        result = start_wf_tool("treatment")
        assert "max workflow depth" in result
        return delta

    mock_tool_loop.side_effect = side_effect

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    # Start at max_depth so the start_workflow tool immediately hits the limit
    run_workflow(
        sample_claim_event,
        sample_claim_state,
        delta,
        workflow,
        depth=MAX_DEPTH,
        max_depth=MAX_DEPTH,
    )


@patch("pipeline.run_workflow.log_workflow")
@patch("pipeline.workflow_tools.log_tool_call")
@patch("pipeline.run_workflow.run_tool_loop")
def test_start_workflow_invalid_id(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    def side_effect(system_prompt, user_message, tools, delta):
        start_wf_tool = tools[3]
        result = start_wf_tool("nonexistent-workflow")
        assert "not found" in result
        return delta

    mock_tool_loop.side_effect = side_effect

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    run_workflow(sample_claim_event, sample_claim_state, delta, workflow)
