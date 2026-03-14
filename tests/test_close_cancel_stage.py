from unittest.mock import patch

from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from models.todo_item_status import TodoItemStatus
from pipeline.close_cancel_stage import (
    _make_cancel_tool,
    _make_close_tool,
    close_cancel_stage,
)
from rules.treatment_rules import TREATMENT_RULES


def test_close_tool_mutates_delta(
    sample_claim_state: ClaimState,
):
    delta = ClaimStateDelta()
    close_tool = _make_close_tool(sample_claim_state, delta, TREATMENT_RULES)

    result = close_tool("todo-001")

    assert "Closed" in result
    assert len(delta.closed_items.add) == 1
    assert delta.closed_items.add[0].todo_item_id == "todo-001"
    assert delta.closed_items.add[0].status == TodoItemStatus.CLOSED
    assert delta.closed_items.add[0].terminal_at is not None
    assert "todo-001" in delta.open_items.delete


def test_cancel_tool_mutates_delta(
    sample_claim_state: ClaimState,
):
    delta = ClaimStateDelta()
    cancel_tool = _make_cancel_tool(sample_claim_state, delta, TREATMENT_RULES)

    # todo-001 is treatment category, so it should be found
    result = cancel_tool("todo-001")

    assert "Cancelled" in result
    assert len(delta.closed_items.add) == 1
    assert delta.closed_items.add[0].todo_item_id == "todo-001"
    assert delta.closed_items.add[0].status == TodoItemStatus.CANCELLED
    assert delta.closed_items.add[0].terminal_at is not None
    assert "todo-001" in delta.open_items.delete


def test_close_tool_wrong_category(
    sample_claim_state: ClaimState,
):
    """Tool should reject items from a different category."""
    delta = ClaimStateDelta()
    close_tool = _make_close_tool(sample_claim_state, delta, TREATMENT_RULES)

    # todo-002 is financial category, not treatment
    result = close_tool("todo-002")

    assert "Error" in result
    assert len(delta.closed_items.add) == 0
    assert len(delta.open_items.delete) == 0


def test_close_tool_nonexistent_id(
    sample_claim_state: ClaimState,
):
    delta = ClaimStateDelta()
    close_tool = _make_close_tool(sample_claim_state, delta, TREATMENT_RULES)

    result = close_tool("nonexistent")

    assert "Error" in result
    assert len(delta.closed_items.add) == 0
    assert len(delta.open_items.delete) == 0


def test_cancel_tool_nonexistent_id(
    sample_claim_state: ClaimState,
):
    delta = ClaimStateDelta()
    cancel_tool = _make_cancel_tool(sample_claim_state, delta, TREATMENT_RULES)

    result = cancel_tool("nonexistent")

    assert "Error" in result
    assert len(delta.closed_items.add) == 0
    assert len(delta.open_items.delete) == 0


def test_skips_when_no_category_items(
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    """Stage should return delta unchanged when no open items match the category."""
    from rules.litigation_rules import LITIGATION_RULES

    delta = ClaimStateDelta()

    result = close_cancel_stage(
        sample_claim_event, sample_claim_state, delta, LITIGATION_RULES
    )

    # No litigation items exist, so delta should be unchanged
    assert result == delta


@patch("pipeline.close_cancel_stage.run_tool_loop")
def test_close_cancel_stage_integration(
    mock_run_tool_loop,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    def side_effect(system_prompt, user_message, tools, delta):
        # Simulate LLM calling close_todo_item
        close_tool = tools[0]
        close_tool("todo-001")
        return delta

    mock_run_tool_loop.side_effect = side_effect
    delta = ClaimStateDelta()

    result = close_cancel_stage(
        sample_claim_event, sample_claim_state, delta, TREATMENT_RULES
    )

    assert len(result.closed_items.add) == 1
    assert result.closed_items.add[0].todo_item_id == "todo-001"
    assert "todo-001" in result.open_items.delete
    mock_run_tool_loop.assert_called_once()
