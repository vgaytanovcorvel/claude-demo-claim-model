from unittest.mock import patch

from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from models.entity_status import EntityStatus
from models.todo_item_status import TodoItemStatus
from pipeline.run_workflow import run_workflow, MAX_DEPTH
from workflows.registry import ALL_WORKFLOWS
from models.todo_item_category import TodoItemCategory
from tests.conftest import sample_entity, sample_todo_item


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
    # 6 tools: add_open_item, terminate, create_entity, update_entity, delete_entity, start_workflow
    assert len(args[0][2]) == 6


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
            # tools[0] = add_open_item, tools[1] = terminate
            terminate_tool = tools[1]
            terminate_tool("todo-001", "closed")
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
def test_terminate_cancel_reason(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    def side_effect(system_prompt, user_message, tools, delta):
        terminate_tool = tools[1]
        result = terminate_tool("todo-001", "cancelled")
        assert "Cancelled" in result
        return delta

    mock_tool_loop.side_effect = side_effect

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    run_workflow(sample_claim_event, sample_claim_state, delta, workflow)

    assert len(delta.closed_items.add) == 1
    assert delta.closed_items.add[0].status == TodoItemStatus.CANCELLED


@patch("pipeline.run_workflow.log_workflow")
@patch("pipeline.workflow_tools.log_tool_call")
@patch("pipeline.run_workflow.run_tool_loop")
def test_terminate_invalid_reason(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    def side_effect(system_prompt, user_message, tools, delta):
        terminate_tool = tools[1]
        result = terminate_tool("todo-001", "invalid")
        assert "Error" in result
        return delta

    mock_tool_loop.side_effect = side_effect

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    run_workflow(sample_claim_event, sample_claim_state, delta, workflow)

    assert len(delta.closed_items.add) == 0


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
            start_wf_tool = tools[5]
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
        start_wf_tool = tools[5]
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
        start_wf_tool = tools[5]
        result = start_wf_tool("nonexistent-workflow")
        assert "not found" in result
        return delta

    mock_tool_loop.side_effect = side_effect

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    run_workflow(sample_claim_event, sample_claim_state, delta, workflow)


@patch("pipeline.run_workflow.log_workflow")
@patch("pipeline.workflow_tools.log_tool_call")
@patch("pipeline.run_workflow.run_tool_loop")
def test_create_entity_tool(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    def side_effect(system_prompt, user_message, tools, delta):
        create_tool = tools[2]
        result = create_tool("diagnosis-010", "diagnosis", "Lumbar strain L4-L5")
        assert "Created entity" in result
        return delta

    mock_tool_loop.side_effect = side_effect

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    run_workflow(sample_claim_event, sample_claim_state, delta, workflow)

    assert len(delta.entities.add) == 1
    assert delta.entities.add[0].entity_id == "diagnosis-010"
    assert delta.entities.add[0].created_by_event_id == "evt-001"


@patch("pipeline.run_workflow.log_workflow")
@patch("pipeline.workflow_tools.log_tool_call")
@patch("pipeline.run_workflow.run_tool_loop")
def test_update_entity_tool(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    entity = sample_entity()
    sample_claim_state.entities.append(entity)

    def side_effect(system_prompt, user_message, tools, delta):
        update_tool = tools[3]
        result = update_tool("diagnosis-001", "Updated lumbar strain")
        assert "Updated entity" in result
        return delta

    mock_tool_loop.side_effect = side_effect

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    run_workflow(sample_claim_event, sample_claim_state, delta, workflow)

    assert len(delta.entities.update) == 1
    assert delta.entities.update[0].description == "Updated lumbar strain"


@patch("pipeline.run_workflow.log_workflow")
@patch("pipeline.workflow_tools.log_tool_call")
@patch("pipeline.run_workflow.run_tool_loop")
def test_delete_entity_tool(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    entity = sample_entity()
    sample_claim_state.entities.append(entity)

    def side_effect(system_prompt, user_message, tools, delta):
        delete_tool = tools[4]
        result = delete_tool("diagnosis-001")
        assert "Superseded entity" in result
        return delta

    mock_tool_loop.side_effect = side_effect

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    run_workflow(sample_claim_event, sample_claim_state, delta, workflow)

    assert len(delta.entities.update) == 1
    assert delta.entities.update[0].status == EntityStatus.SUPERSEDED
    assert delta.entities.update[0].terminated_by_event_id == "evt-001"


@patch("pipeline.run_workflow.log_workflow")
@patch("pipeline.workflow_tools.log_tool_call")
@patch("pipeline.run_workflow.run_tool_loop")
def test_delete_entity_auto_cancels_linked_items(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    """When an entity is superseded, open items linked to it should be auto-cancelled."""
    entity = sample_entity()
    sample_claim_state.entities.append(entity)

    # Add items linked to the entity
    linked_item_1 = sample_todo_item(
        {
            "todo_item_id": "auth-001",
            "description": "Authorization review",
            "context_entity_id": "diagnosis-001",
            "category": TodoItemCategory.TREATMENT,
        }
    )
    linked_item_2 = sample_todo_item(
        {
            "todo_item_id": "monitor-001",
            "description": "Treatment monitoring",
            "context_entity_id": "diagnosis-001",
            "category": TodoItemCategory.TREATMENT,
        }
    )
    # Unlinked item should NOT be cancelled
    unlinked_item = sample_todo_item(
        {
            "todo_item_id": "other-001",
            "description": "Other item",
            "category": TodoItemCategory.TREATMENT,
        }
    )
    sample_claim_state.open_items.extend([linked_item_1, linked_item_2, unlinked_item])

    def side_effect(system_prompt, user_message, tools, delta):
        delete_tool = tools[4]
        result = delete_tool("diagnosis-001")
        assert "Auto-cancelled 2 linked item(s)" in result
        assert "auth-001" in result
        assert "monitor-001" in result
        return delta

    mock_tool_loop.side_effect = side_effect

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    run_workflow(sample_claim_event, sample_claim_state, delta, workflow)

    # Entity superseded
    assert len(delta.entities.update) == 1
    assert delta.entities.update[0].status == EntityStatus.SUPERSEDED

    # 2 linked items auto-cancelled
    assert len(delta.closed_items.add) == 2
    cancelled_ids = {item.todo_item_id for item in delta.closed_items.add}
    assert cancelled_ids == {"auth-001", "monitor-001"}
    for item in delta.closed_items.add:
        assert item.status == TodoItemStatus.CANCELLED

    # 2 items removed from open
    assert set(delta.open_items.delete) == {"auth-001", "monitor-001"}


@patch("pipeline.run_workflow.log_workflow")
@patch("pipeline.workflow_tools.log_tool_call")
@patch("pipeline.run_workflow.run_tool_loop")
def test_delete_entity_skips_other_category_items(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    """Auto-cancel should only affect items in the same workflow category."""
    entity = sample_entity()
    sample_claim_state.entities.append(entity)

    # Item linked to entity but in FINANCIAL category — should NOT be cancelled
    financial_item = sample_todo_item(
        {
            "todo_item_id": "fin-001",
            "description": "Reserve review",
            "context_entity_id": "diagnosis-001",
            "category": TodoItemCategory.FINANCIAL,
        }
    )
    sample_claim_state.open_items.append(financial_item)

    def side_effect(system_prompt, user_message, tools, delta):
        delete_tool = tools[4]
        result = delete_tool("diagnosis-001")
        assert "Auto-cancelled" not in result
        return delta

    mock_tool_loop.side_effect = side_effect

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    run_workflow(sample_claim_event, sample_claim_state, delta, workflow)

    # Entity superseded but no items cancelled
    assert len(delta.entities.update) == 1
    assert len(delta.closed_items.add) == 0


@patch("pipeline.run_workflow.log_workflow")
@patch("pipeline.workflow_tools.log_tool_call")
@patch("pipeline.run_workflow.run_tool_loop")
def test_update_entity_not_found(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    def side_effect(system_prompt, user_message, tools, delta):
        update_tool = tools[3]
        result = update_tool("nonexistent", "desc")
        assert "Error" in result
        return delta

    mock_tool_loop.side_effect = side_effect

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    run_workflow(sample_claim_event, sample_claim_state, delta, workflow)

    assert len(delta.entities.update) == 0


@patch("pipeline.run_workflow.log_workflow")
@patch("pipeline.workflow_tools.log_tool_call")
@patch("pipeline.run_workflow.run_tool_loop")
def test_delete_entity_not_found(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    def side_effect(system_prompt, user_message, tools, delta):
        delete_tool = tools[4]
        result = delete_tool("nonexistent")
        assert "Error" in result
        return delta

    mock_tool_loop.side_effect = side_effect

    workflow = ALL_WORKFLOWS[TodoItemCategory.TREATMENT]
    delta = ClaimStateDelta()
    run_workflow(sample_claim_event, sample_claim_state, delta, workflow)

    assert len(delta.entities.update) == 0
