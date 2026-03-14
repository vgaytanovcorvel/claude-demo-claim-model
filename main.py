import sys

import yaml

from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from process_event import process_event


def load_events(path: str) -> list[ClaimEvent]:
    with open(path) as f:
        data = yaml.safe_load(f)
    return [ClaimEvent(**item) for item in data]


def dump_state(state: ClaimState) -> str:
    return yaml.dump(state.model_dump(mode="json"), default_flow_style=False, sort_keys=False)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "assets/sample_events.yaml"
    events = load_events(path)
    state = ClaimState()

    for event in events:
        print(f"--- Processing event: {event.claim_event_id} ---")
        print(f"Content: {event.content}")
        print()
        state = process_event(state, event)
        print("State after event:")
        print(dump_state(state))


if __name__ == "__main__":
    main()
