import type { Claim } from '../models/Claim'
import type { CareGap } from '../models/CareGap'
import './ClaimState.css'

interface ClaimStateProps {
  claim: Claim
}

function ClaimState({ claim }: ClaimStateProps) {
  const openItems = claim.outstandingItems.filter(i => i.status === 'open')
  const completedItems = claim.outstandingItems.filter(i => i.status === 'completed')
  const openGaps = claim.careGaps.filter(g => g.status !== 'resolved' && g.status !== 'accepted_risk')
  const resolvedGaps = claim.careGaps.filter(g => g.status === 'resolved' || g.status === 'accepted_risk')

  // Build a map: outstanding item id -> care gap(s) it addresses
  const itemGapMap = new Map<string, CareGap[]>()
  for (const gap of claim.careGaps) {
    for (const oiId of gap.outstandingItemIds) {
      const existing = itemGapMap.get(oiId) ?? []
      existing.push(gap)
      itemGapMap.set(oiId, existing)
    }
  }

  // Build a map: item id -> item, for care gap linked items lookup
  const itemById = new Map(claim.outstandingItems.map(i => [i.id, i]))

  function renderGapTag(itemId: string) {
    const gaps = itemGapMap.get(itemId)
    if (!gaps?.length) return null
    return gaps.map(g => (
      <span key={g.gapId} className={`oi-gap-tag ${g.status === 'resolved' ? 'resolved' : `severity-${g.severity}`}`}>
        {g.status === 'resolved' ? 'gap resolved' : `addresses gap`}
      </span>
    ))
  }

  return (
    <div className="claim-state">
      <section className="claim-section">
        <h2>Milestones</h2>
        <div className="milestone-list">
          {claim.milestones.map(m => (
            <div key={m.id} className={`milestone ${m.actualDays !== null ? 'reached' : 'pending'}`}>
              <span className="milestone-phase">{m.phase}</span>
              <span className="milestone-name">{m.name}</span>
              {m.actualDays !== null ? (
                <span className="milestone-days">
                  Day {m.actualDays}
                  {m.variation !== 0 && (
                    <span className={`variation ${m.variation < 0 ? 'early' : 'late'}`}>
                      {m.variation < 0 ? m.variation : `+${m.variation}`}d
                    </span>
                  )}
                </span>
              ) : (
                <span className="milestone-days pending-label">
                  est. day {m.estimatedDays}
                  {m.variation !== 0 && (
                    <span className={`variation ${m.variation < 0 ? 'early' : 'late'}`}>
                      {m.variation < 0 ? m.variation : `+${m.variation}`}d
                    </span>
                  )}
                </span>
              )}
            </div>
          ))}
        </div>
      </section>

      <section className="claim-section">
        <h2>
          Outstanding Items
          <span className="section-count">{openItems.length} open</span>
        </h2>
        {openItems.length > 0 && (
          <div className="oi-list">
            {openItems.map(item => (
              <div key={item.id} className={`oi-item urgency-${item.urgencyType}`}>
                <span className={`oi-owner-badge owner-${item.category.toLowerCase()}`}>{item.owner}</span>
                <span className="oi-desc">
                  {item.description}
                  {renderGapTag(item.id)}
                </span>
                <span className="oi-urgency">{item.urgencyType.replace('-', ' ')}</span>
              </div>
            ))}
          </div>
        )}
        {completedItems.length > 0 && (
          <details className="completed-details">
            <summary>{completedItems.length} completed</summary>
            <div className="oi-list">
              {completedItems.map(item => (
                <div key={item.id} className={`oi-item completed urgency-${item.urgencyType}`}>
                  <span className={`oi-owner-badge owner-${item.category.toLowerCase()}`}>{item.owner}</span>
                  <span className="oi-desc">
                    {item.description}
                    {renderGapTag(item.id)}
                  </span>
                  <span className="oi-urgency">{item.urgencyType.replace('-', ' ')}</span>
                </div>
              ))}
            </div>
          </details>
        )}
      </section>

      {claim.careGaps.length > 0 && (
        <section className="claim-section">
          <h2>
            Care Gaps
            {openGaps.length > 0 && <span className="section-count alert">{openGaps.length} active</span>}
            {openGaps.length === 0 && resolvedGaps.length > 0 && <span className="section-count resolved-count">all resolved</span>}
          </h2>
          {openGaps.map(g => {
            const linkedItems = g.outstandingItemIds.map(id => itemById.get(id)).filter(Boolean)
            return (
              <div key={g.gapId} className={`care-gap-block severity-${g.severity}`}>
                <div className="care-gap-header">
                  <span className="gap-severity">{g.severity}</span>
                  <span className="gap-desc">{g.description}</span>
                  <span className="gap-category">{g.gapCategory}</span>
                </div>
                {linkedItems.length > 0 && (
                  <div className="gap-linked-items">
                    {linkedItems.map(item => item && (
                      <div key={item.id} className="gap-linked-item">
                        <span className={`oi-owner-badge owner-${item.category.toLowerCase()}`}>{item.owner}</span>
                        <span className="gap-linked-desc">{item.description}</span>
                        <span className={`gap-linked-status ${item.status}`}>{item.status}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
          {resolvedGaps.map(g => {
            const linkedItems = g.outstandingItemIds.map(id => itemById.get(id)).filter(Boolean)
            return (
              <div key={g.gapId} className="care-gap-block resolved">
                <div className="care-gap-header">
                  <span className="gap-severity">resolved</span>
                  <span className="gap-desc">{g.description}</span>
                  <span className="gap-category">{g.gapCategory}</span>
                </div>
                {linkedItems.length > 0 && (
                  <div className="gap-linked-items">
                    {linkedItems.map(item => item && (
                      <div key={item.id} className="gap-linked-item">
                        <span className={`oi-owner-badge owner-${item.category.toLowerCase()}`}>{item.owner}</span>
                        <span className="gap-linked-desc">{item.description}</span>
                        <span className={`gap-linked-status ${item.status}`}>{item.status}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </section>
      )}
    </div>
  )
}

export default ClaimState
