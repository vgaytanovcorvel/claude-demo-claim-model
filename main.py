import os
import sys

import yaml

from models.claim_event import ClaimEvent
from models.claim_state import ClaimState
from models.claim_state_delta import ClaimStateDelta
from process_event import process_event
from render_html import render_html


def load_events(path: str) -> list[ClaimEvent]:
    with open(path) as f:
        data = yaml.safe_load(f)
    return [ClaimEvent(**item) for item in data]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "assets/sample_events.yaml"
    events = load_events(path)
    state = ClaimState()

    processed_events: list[ClaimEvent] = []
    deltas: list[ClaimStateDelta] = []
    states: list[ClaimState] = []

    for event in events:
        print(f"Processing event: {event.claim_event_id}")
        result = process_event(state, event)
        state = result.state
        processed_events.append(event)
        deltas.append(result.delta)
        states.append(state)

    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "report.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(render_html(processed_events, deltas, states))

    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
