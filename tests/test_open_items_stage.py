from pathlib import Path
from unittest.mock import patch

from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from models.owner import Owner
from models.todo_item_category import TodoItemCategory
from models.todo_item_status import TodoItemStatus
from models.urgency_type import UrgencyType
from pipeline.open_items_stage import _make_add_open_item_tool, open_items_stage
from rules.yaml_loader import YamlRuleLoader

YAML_DIR = Path(__file__).resolve().parent.parent / "rules" / "yaml"
TREATMENT_RULES = YamlRuleLoader.load(YAML_DIR / "treatment.yaml")


def test_add_open_item_tool_mutates_delta():
    delta = ClaimStateDelta()
    add_tool = _make_add_open_item_tool(delta, TREATMENT_RULES)

    result = add_tool("todo-new", "Get repair estimate", "provider", "deadline-driven", "acute-care")

    assert "Added" in result
    assert len(delta.open_items.add) == 1
    item = delta.open_items.add[0]
    assert item.todo_item_id == "todo-new"
    assert item.description == "Get repair estimate"
    assert item.owner == Owner.PROVIDER
    assert item.urgency_type == UrgencyType.DEADLINE_DRIVEN
    assert item.status == TodoItemStatus.OPEN
    assert item.category == TodoItemCategory.TREATMENT
    assert item.sub_category == "acute-care"
    assert item.created_at is not None


def test_add_open_item_tool_with_sub_category():
    delta = ClaimStateDelta()
    add_tool = _make_add_open_item_tool(delta, TREATMENT_RULES)

    result = add_tool(
        "todo-sc",
        "Pre-surgical auth",
        "adjuster",
        "milestone-protecting",
        sub_category="pre-surgical-authorization",
    )

    assert "Added" in result
    item = delta.open_items.add[0]
    assert item.sub_category == "pre-surgical-authorization"


def test_add_open_item_tool_empty_sub_category_is_none():
    delta = ClaimStateDelta()
    add_tool = _make_add_open_item_tool(delta, TREATMENT_RULES)

    add_tool("todo-empty", "Test", "adjuster", "discretionary", sub_category="")

    item = delta.open_items.add[0]
    assert item.sub_category is None


@patch("pipeline.open_items_stage.run_tool_loop")
def test_open_items_stage_integration(
    mock_run_tool_loop,
    sample_claim_event: ClaimEvent,
    sample_claim_state: ClaimState,
):
    def side_effect(system_prompt, user_message, tools, delta):
        add_tool = tools[0]
        add_tool("todo-new", "Follow up on inspection", "adjuster", "discretionary", "acute-care")
        return delta

    mock_run_tool_loop.side_effect = side_effect
    delta = ClaimStateDelta()

    result = open_items_stage(
        sample_claim_event, sample_claim_state, delta, TREATMENT_RULES
    )

    assert len(result.open_items.add) == 1
    assert result.open_items.add[0].todo_item_id == "todo-new"
    assert result.open_items.add[0].category == TodoItemCategory.TREATMENT
    mock_run_tool_loop.assert_called_once()
