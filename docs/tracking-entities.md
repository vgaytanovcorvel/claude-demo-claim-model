## Problem

When a diagnosis changes, downstream open items (e.g., treatment-monitoring created days later via authorization-approved event) have no structural link back to the originating diagnosis. The LLM must infer provenance from context, which is fragile.

**Multi-hop chain example:**
- Day 1: FNOL → acute-care item
- Day 5: Diagnosis → acute-care closed, authorization item created
- Day 10: Auth-approved → authorization closed, treatment-monitoring created
- Day 15: New diagnosis → need to cancel treatment-monitoring, but it only links to Day 10 event, not Day 5 diagnosis

## Proposed Solution: Entities on ClaimState

Add lightweight entity refs (e.g., `diagnosis_refs[]`) to ClaimState. TodoItem gains `diagnosis_ref: str | None`. The active diagnosis ref acts as **ambient context** — workflows stamp new items with the current ref without needing to trace lineage.

## Entity-by-Entity Assessment

- **Diagnosis: Strong yes.** Multi-hop provenance, real supersession, concrete cancellation needs.
- **Treatment plan: Conditional.** Useful if treatment plans change independently of diagnosis often enough. Could add later.
- **FNOL: No.** Doesn't get superseded. The claim itself serves as root grouping.

## Key Design Decisions

### 1. Lightweight refs, not clinical records
```python
class DiagnosisRef(BaseModel):
    ref_id: str
    created_by_event_id: str
    status: Literal["active", "superseded"]
```
Clinical details stay in events. Entity is just a grouping key.

### 2. Pipeline must change to two phases
Current parallel execution means workflows can't see entities created by sibling workflows in the same event cycle. Proposed:
- **Phase 1**: Classify event, create/supersede entity refs (sequential, possibly rule-based)
- **Phase 2**: Run category workflows in parallel against updated state (as today)

### 3. Cancellation still requires judgment
Not all items with an old `diagnosis_ref` should be auto-cancelled:
- Authorization, treatment-monitoring: YES cancel
- Reserve-review (financial): NO, still needed
- Compliance filing: MAYBE, depends on jurisdiction
- RTW assessment: MAYBE, depends on diagnosis impact

Entities make **finding** relevant items deterministic. The **decision** to cancel still needs per-category reasoning in workflow instructions.

### 4. origin_key was considered and rejected
A simple `origin_key: str` field on TodoItem works for single-hop (diagnosis → authorization) but breaks for multi-hop (diagnosis → authorization → treatment-monitoring) because each hop would need to propagate the key. The ambient-context pattern (reading active ref from ClaimState) eliminates this.

## Proposed ClaimState Shape
```
ClaimState
├── events[]
├── open_items[]          (TodoItem gains diagnosis_ref: str | None)
├── closed_items[]
└── diagnosis_refs[]      (lightweight: ref_id, event_id, status)
```

## Open Questions
- Is the current LLM approach failing often enough in practice to justify this?
- Should Phase 1 be LLM-driven or rule-based?
- When to add treatment_plan_ref (if ever)?
