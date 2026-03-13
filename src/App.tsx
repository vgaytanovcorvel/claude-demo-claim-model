import { useState } from 'react'
import claimEvents from './data/claim-events.json'
import claimStates from './data/claim-states.json'
import type { ClaimEvent } from './models/ClaimEvent'
import type { Claim } from './models/Claim'
import ClaimState from './components/ClaimState'
import './App.css'

const events: ClaimEvent[] = claimEvents;
const states = claimStates as unknown as Record<string, Claim>;

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function formatTime(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
}

function App() {
  const [activeIndex, setActiveIndex] = useState(0);
  const active = events[activeIndex];
  const activeClaim = states[active.id];

  return (
    <div className="app">
      <nav className="timeline">
        <div className="timeline-track" />
        {events.map((event, i) => (
          <button
            key={event.id}
            className={`timeline-step ${i === activeIndex ? 'active' : ''} ${i < activeIndex ? 'past' : ''}`}
            onClick={() => setActiveIndex(i)}
          >
            <span className="step-dot" />
            <span className="step-label">{event.name}</span>
            <span className="step-date">{formatDate(event.date)}</span>
          </button>
        ))}
      </nav>

      <div className="content">
        <main className="event-detail">
          <h1>{active.name}</h1>
          <p className="event-datetime">
            {formatDate(active.date)} at {formatTime(active.date)}
          </p>
          <p className="event-description">{active.description}</p>
          {activeClaim && <ClaimState claim={activeClaim} />}
        </main>

        <footer className="nav-buttons">
          <button
            disabled={activeIndex === 0}
            onClick={() => setActiveIndex(i => i - 1)}
          >
            ← Previous
          </button>
          <span className="step-counter">{activeIndex + 1} / {events.length}</span>
          <button
            disabled={activeIndex === events.length - 1}
            onClick={() => setActiveIndex(i => i + 1)}
          >
            Next →
          </button>
        </footer>
      </div>
    </div>
  )
}

export default App
