from unittest.mock import patch

from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from process_event import process_event


@patch("pipeline.open_items_stage.run_tool_loop")
@patch("pipeline.close_cancel_stage.run_tool_loop")
def test_full_orchestration(
    mock_close_cancel_loop,
    mock_open_items_loop,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    def close_side_effect(system_prompt, user_message, tools, delta):
        # Identify treatment category by system prompt content
        if "TREATMENT" in system_prompt:
            close_tool = tools[0]
            close_tool("todo-001")
        return delta

    def open_side_effect(system_prompt, user_message, tools, delta):
        # Identify treatment category by system prompt content
        if "TREATMENT" in system_prompt:
            add_tool = tools[0]
            add_tool(
                "todo-003",
                "Order materials for repair",
                "adjuster",
                "deadline-driven",
                "acute-care",
            )
        return delta

    mock_close_cancel_loop.side_effect = close_side_effect
    mock_open_items_loop.side_effect = open_side_effect

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

    # Close/cancel stage called for categories that have open items
    # (treatment has todo-001, financial has todo-002 => 2 calls)
    assert mock_close_cancel_loop.call_count == 2

    # Open items stage called for all 5 categories
    assert mock_open_items_loop.call_count == 5
