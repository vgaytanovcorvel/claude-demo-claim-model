from apply_delta import apply_delta
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from models.entity_status import EntityStatus
from tests.conftest import sample_entity, sample_todo_item


def test_add_items(sample_claim_state: ClaimState):
    new_item = sample_todo_item(
        {
            "todo_item_id": "todo-new",
            "description": "New task",
        }
    )
    delta = ClaimStateDelta()
    delta.open_items.add.append(new_item)

    result = apply_delta(sample_claim_state, delta)

    ids = [item.todo_item_id for item in result.open_items]
    assert "todo-new" in ids
    assert len(result.open_items) == len(sample_claim_state.open_items) + 1


def test_delete_items(sample_claim_state: ClaimState):
    delta = ClaimStateDelta()
    delta.open_items.delete.append("todo-001")

    result = apply_delta(sample_claim_state, delta)

    ids = [item.todo_item_id for item in result.open_items]
    assert "todo-001" not in ids
    assert len(result.open_items) == len(sample_claim_state.open_items) - 1


def test_update_items(sample_claim_state: ClaimState):
    updated = sample_todo_item(
        {
            "todo_item_id": "todo-001",
            "description": "Updated description",
        }
    )
    delta = ClaimStateDelta()
    delta.open_items.update.append(updated)

    result = apply_delta(sample_claim_state, delta)

    item = next(i for i in result.open_items if i.todo_item_id == "todo-001")
    assert item.description == "Updated description"
    assert len(result.open_items) == len(sample_claim_state.open_items)


def test_idempotency(sample_claim_state: ClaimState):
    new_item = sample_todo_item(
        {
            "todo_item_id": "todo-new",
            "description": "New task",
        }
    )
    delta = ClaimStateDelta()
    delta.open_items.add.append(new_item)
    delta.open_items.delete.append("todo-001")

    result1 = apply_delta(sample_claim_state, delta)
    result2 = apply_delta(result1, delta)

    assert result1 == result2


def test_empty_delta_noop(sample_claim_state: ClaimState):
    delta = ClaimStateDelta()

    result = apply_delta(sample_claim_state, delta)

    assert result == sample_claim_state


def test_delete_nonexistent_id(sample_claim_state: ClaimState):
    delta = ClaimStateDelta()
    delta.open_items.delete.append("nonexistent-id")

    result = apply_delta(sample_claim_state, delta)

    assert len(result.open_items) == len(sample_claim_state.open_items)


def test_update_nonexistent_id(sample_claim_state: ClaimState):
    updated = sample_todo_item(
        {
            "todo_item_id": "nonexistent-id",
            "description": "Ghost update",
        }
    )
    delta = ClaimStateDelta()
    delta.open_items.update.append(updated)

    result = apply_delta(sample_claim_state, delta)

    assert result == sample_claim_state


# --- Entity delta tests ---


def test_add_entity():
    state = ClaimState()
    entity = sample_entity()
    delta = ClaimStateDelta()
    delta.entities.add.append(entity)

    result = apply_delta(state, delta)

    assert len(result.entities) == 1
    assert result.entities[0].entity_id == "diagnosis-001"


def test_update_entity():
    entity = sample_entity()
    state = ClaimState(entities=[entity])
    updated = entity.model_copy(update={"description": "Updated diagnosis"})
    delta = ClaimStateDelta()
    delta.entities.update.append(updated)

    result = apply_delta(state, delta)

    assert result.entities[0].description == "Updated diagnosis"
    assert len(result.entities) == 1


def test_delete_entity_via_update_superseded():
    """Logical delete: update entity status to superseded (not physical delete)."""
    entity = sample_entity()
    state = ClaimState(entities=[entity])
    superseded = entity.model_copy(update={"status": EntityStatus.SUPERSEDED})
    delta = ClaimStateDelta()
    delta.entities.update.append(superseded)

    result = apply_delta(state, delta)

    assert len(result.entities) == 1
    assert result.entities[0].status == EntityStatus.SUPERSEDED


def test_entity_add_idempotency():
    entity = sample_entity()
    state = ClaimState(entities=[entity])
    delta = ClaimStateDelta()
    delta.entities.add.append(entity)

    result = apply_delta(state, delta)

    assert len(result.entities) == 1
