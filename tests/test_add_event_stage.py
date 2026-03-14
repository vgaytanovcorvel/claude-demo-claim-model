from models.claim_event import ClaimEvent
from models.claim_state_delta import ClaimStateDelta
from pipeline.add_event_stage import add_event_stage


def test_event_appended_to_delta(sample_claim_event: ClaimEvent):
    delta = ClaimStateDelta()

    result = add_event_stage(sample_claim_event, delta)

    assert len(result.events.add) == 1
    assert result.events.add[0] == sample_claim_event


def test_other_delta_fields_empty(sample_claim_event: ClaimEvent):
    delta = ClaimStateDelta()

    result = add_event_stage(sample_claim_event, delta)

    assert result.events.update == []
    assert result.events.delete == []
    assert result.open_items.add == []
    assert result.open_items.update == []
    assert result.open_items.delete == []
    assert result.closed_items.add == []
    assert result.closed_items.update == []
    assert result.closed_items.delete == []
