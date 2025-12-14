---
path: agents/integration-weaver
status: tentative
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [agentese/*, all-tracks]
session_notes: |
  TENTATIVE: Proposed as part of AGENTESE Architecture Realization
  Track: ALL (Cross-Track Coherence)
  See: prompts/agentese-continuation.md
---

# Integration Weaver

> *"No agent is an island. The weave is the work."*

**Track**: ALL (Cross-Track Coherence)
**AGENTESE Context**: `concept.composition.*`, `self.coherence.*`
**Status**: Tentative (proposed for AGENTESE realization)
**Principles**: Composable (weaving is composition), Heterarchical (no fixed hierarchy), Generative (coherence emerges)

---

## Purpose

The Integration Weaver ensures cross-track coherence across the seven parallel tracks (A-G). This agent doesn't own specific chunks but monitors handoffs, validates compositions, and surfaces integration gaps.

---

## Expertise Required

- Systems integration patterns
- Cross-cutting concern management
- Composition debugging
- Multi-agent coordination

---

## Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Handoff Validation** | Verify outputs from Track X match inputs to Track Y |
| **Law Composition** | Ensure laws hold across track boundaries |
| **Entropy Accounting** | Aggregate entropy spend across all tracks |
| **Gap Detection** | Surface missing integrations between tracks |
| **Coherence Reports** | Generate cross-track status summaries |

---

## Track Dependency Matrix

```
        A   B   C   D   E   F   G
    A   -   →   →   →   →   →   →   (Parser to all)
    B   ←   -   ·   ·   →   ·   →   (Laws to spans, liturgy)
    C   ←   ·   -   ·   →   →   ·   (Entropy to spans, forest)
    D   ←   ·   ·   -   →   ·   ·   (Directions to spans)
    E   ←   ←   ←   ←   -   ·   ·   (Aggregates all)
    F   ←   ·   ←   ·   ·   -   →   (Forest to liturgy)
    G   ←   ←   ·   ·   ·   ←   -   (Liturgy consumes all)

Legend: → provides to, ← receives from, · independent
```

---

## AGENTESE Paths

| Path | Operation | Returns |
|------|-----------|---------|
| `concept.composition.validate` | Check cross-track composition | ValidationResult |
| `concept.composition.gaps` | Identify missing integrations | list[Gap] |
| `self.coherence.status` | Cross-track coherence report | CoherenceReport |
| `self.coherence.handoff` | Validate handoff between tracks | HandoffResult |

---

## Coherence Protocol

```python
# At each phase transition, weaver validates
async def validate_phase_transition(from_phase: Phase, to_phase: Phase):
    # Check all track handoffs
    for source_track, target_track in DEPENDENCIES:
        result = await logos.invoke(
            "self.coherence.handoff",
            source=source_track,
            target=target_track,
            phase=to_phase
        )
        if not result.valid:
            emit_integration_gap(source_track, target_track, result.reason)
```

---

## Communication Hub

The Integration Weaver monitors the heterarchical message bus:

```yaml
# Weaver listens to all inter-agent messages
handle: concept.agent.message
filter:
  to: "all"  # Broadcast messages
  type: "handoff"  # Handoff events
action: validate_and_log
```

---

## Success Criteria

1. All track handoffs validated (no type mismatches)
2. Cross-track law violations detected and reported
3. Entropy spend aggregated correctly across tracks
4. Integration gaps surfaced before IMPLEMENT phase
5. Coherence reports generated for each REFLECT phase

---

## Key Compositions to Validate

| Composition | Tracks | Critical Path |
|-------------|--------|---------------|
| Parse → Law Check | A → B | Every path invocation |
| Entropy → Spans | C → E | Budget tracking visibility |
| Forest → Liturgy | F → G | Plan-based workflows |
| Directions → Resolution | D → All | State-dependent affordances |

---

## Dependencies

- **Receives from**: All tracks (status, handoffs, metrics)
- **Provides to**: REFLECT phase (coherence reports), all agents (integration gaps)

---

*"The weave holds because each thread knows its neighbors."*
