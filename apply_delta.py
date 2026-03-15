from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta


def _apply_list_delta(current_list: list, delta, id_field: str) -> list:
    """Apply add/update/delete operations to a list of items.

    1. Copy current list
    2. Delete: remove items whose ID is in delta.delete
    3. Update: replace matching items by ID
    4. Add: append only if no item with that ID exists (idempotency)
    """
    result = list(current_list)

    # Delete
    delete_ids = set(delta.delete)
    result = [item for item in result if getattr(item, id_field) not in delete_ids]

    # Update
    for update_item in delta.update:
        update_id = getattr(update_item, id_field)
        for i, item in enumerate(result):
            if getattr(item, id_field) == update_id:
                result[i] = update_item
                break

    # Add (idempotent)
    existing_ids = {getattr(item, id_field) for item in result}
    for add_item in delta.add:
        add_id = getattr(add_item, id_field)
        if add_id not in existing_ids:
            result.append(add_item)
            existing_ids.add(add_id)

    return result


def apply_delta(state: ClaimState, delta: ClaimStateDelta) -> ClaimState:
    """Apply a ClaimStateDelta to a ClaimState, returning a new ClaimState."""
    return ClaimState(
        events=_apply_list_delta(state.events, delta.events, "claim_event_id"),
        entities=_apply_list_delta(state.entities, delta.entities, "entity_id"),
        open_items=_apply_list_delta(
            state.open_items, delta.open_items, "todo_item_id"
        ),
        closed_items=_apply_list_delta(
            state.closed_items, delta.closed_items, "todo_item_id"
        ),
    )
