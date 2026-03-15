from unittest.mock import patch

from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from process_event import process_event


@patch("pipeline.run_workflow.log_workflow")
@patch("pipeline.workflow_tools.log_tool_call")
@patch("pipeline.run_workflow.run_tool_loop")
def test_full_orchestration(
    mock_tool_loop,
    _mock_tool_log,
    _mock_wf_log,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    def side_effect(system_prompt, user_message, tools, delta):
        if "TREATMENT" in system_prompt:
            # tools: [add_open_item, terminate, create_entity, update_entity, delete_entity, start_workflow]
            terminate_tool = tools[1]
            terminate_tool("todo-001", "closed")
            add_tool = tools[0]
            add_tool(
                "todo-003",
                "Order materials for repair",
                "adjuster",
                "deadline-driven",
                "acute-care",
            )
        return delta

    mock_tool_loop.side_effect = side_effect

    result = process_event(sample_claim_state, sample_claim_event)
    state = result.state

    # Event should be added
    event_ids = [e.claim_event_id for e in state.events]
    assert "evt-000" in event_ids  # original
    assert "evt-001" in event_ids  # new

    # todo-001 should be removed from open items
    open_ids = [i.todo_item_id for i in state.open_items]
    assert "todo-001" not in open_ids

    # todo-002 should remain open
    assert "todo-002" in open_ids

    # New item should be in open items
    assert "todo-003" in open_ids

    # todo-001 should be in closed items
    closed_ids = [i.todo_item_id for i in state.closed_items]
    assert "todo-001" in closed_ids
    assert "todo-closed-001" in closed_ids  # original closed item preserved

    # Delta should capture what changed
    assert len(result.delta.events.add) == 1
    assert len(result.delta.open_items.add) == 1
    assert len(result.delta.open_items.delete) == 1

    # Workflow called for enabled categories only (treatment)
    assert mock_tool_loop.call_count == 1
