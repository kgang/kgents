# Continuation: Gardener-Logos Phase 8 - Auto-Inducer

> *"The garden that knows when to change seasons."*

**Previous Session:** Phase 7 (Web Visualization) completed
**Status:** ✅ **PHASE 8 COMPLETE**
**Completed:** 2025-12-16
**Plan:** `plans/gardener-logos-enactment.md` (100% complete)

---

## Summary

Phase 8 is fully implemented with:
- `seasons.py` module with TransitionSignals, SeasonTransition, and evaluation logic
- Five transition rules (DORMANT→SPROUTING→BLOOMING→HARVEST→COMPOSTING→DORMANT)
- TendingResult extended with `suggested_transition` field
- Auto-inducer hooked into `apply_gesture()` function
- API endpoints: `POST /garden/transition/accept` and `POST /garden/transition/dismiss`
- Web UI: TransitionSuggestionBanner component with accept/dismiss actions
- 25 comprehensive tests covering signals, rules, dismissals, and integration

### Files Created/Modified

1. **Created:** `impl/claude/protocols/gardener_logos/seasons.py` - Core transition logic
2. **Modified:** `impl/claude/protocols/gardener_logos/tending.py` - Added suggested_transition to TendingResult
3. **Modified:** `impl/claude/protocols/api/gardener.py` - Accept/dismiss endpoints
4. **Modified:** `impl/claude/protocols/api/models.py` - API model types
5. **Created:** `impl/claude/web/src/components/garden/TransitionSuggestionBanner.tsx` - UI component
6. **Modified:** `impl/claude/web/src/components/garden/GardenVisualization.tsx` - Integration
7. **Modified:** `impl/claude/web/src/pages/Garden.tsx` - State management
8. **Modified:** `impl/claude/web/src/api/client.ts` - API client methods
9. **Modified:** `impl/claude/web/src/reactive/types.ts` - TypeScript types
10. **Created:** `impl/claude/protocols/gardener_logos/_tests/test_seasons.py` - 25 tests

---

## Context

The Gardener-Logos system is now complete. All 8 phases are done:

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | AGENTESE Wiring | ✅ Complete |
| 2 | CLI Integration | ✅ Complete |
| 3 | Persistence | ✅ Complete |
| 4 | Session Unification | ✅ Complete |
| 5 | Prompt Logos Delegation | ✅ Complete |
| 6 | Synergy Bus | ✅ Complete |
| 7 | Web Visualization | ✅ Complete |
| **8** | **Auto-Inducer** | **✅ Complete** |

---

## What Was Just Completed (Phase 7)

### Components Created
- `impl/claude/web/src/components/garden/GardenVisualization.tsx`
- `impl/claude/web/src/components/garden/SeasonIndicator.tsx`
- `impl/claude/web/src/components/garden/PlotCard.tsx`
- `impl/claude/web/src/components/garden/GestureHistory.tsx`

### API Endpoints Added
- `GET /v1/gardener/garden` - Get garden state
- `POST /v1/gardener/garden/tend` - Apply tending gesture
- `POST /v1/gardener/garden/season` - Transition season (manual)
- `POST /v1/gardener/garden/plot/{name}/focus` - Focus plot

### Types Added
- `GardenJSON`, `PlotJSON`, `GestureJSON` in `reactive/types.ts`
- API models in `protocols/api/models.py`

### Page
- `/garden` route with full visualization

---

## Task: Implement Phase 8 - Auto-Inducer

### Goal
The garden should automatically suggest or apply season transitions based on activity signals. This makes the garden feel alive and responsive.

### Key Files to Create/Modify

1. **New: `impl/claude/protocols/gardener_logos/seasons.py`**
   - `TransitionSignals` dataclass
   - `SeasonTransition` dataclass
   - `evaluate_season_transition()` function
   - Signal gathering from garden state

2. **Modify: `impl/claude/protocols/gardener_logos/tending.py`**
   - Add auto-inducer hook in `apply_gesture()`
   - Return `suggested_transition` in `TendingResult`

3. **Modify: `impl/claude/protocols/api/gardener.py`**
   - Return transition suggestions in tend response
   - Add endpoint for accepting/rejecting suggestions

4. **Modify: `impl/claude/web/src/components/garden/GardenVisualization.tsx`**
   - Display transition suggestions
   - UI for accepting/dismissing

### Transition Logic

```
DORMANT → SPROUTING
  When: gesture_frequency > 2/hour AND entropy_spent_ratio < 0.5
  Why: Activity detected after rest

SPROUTING → BLOOMING
  When: plot_progress_delta > 0.2 AND time_in_season > 2 hours
  Why: Ideas are crystallizing

BLOOMING → HARVEST
  When: session.reflect_count >= 3 OR artifacts_created > 5
  Why: Time to gather results

HARVEST → COMPOSTING
  When: time_in_season > 4 hours AND gesture_frequency < 1/hour
  Why: Gathering complete, time to break down

COMPOSTING → DORMANT
  When: entropy_spent_ratio > 0.8 OR time_in_season > 6 hours
  Why: Decomposition complete, rest needed
```

### Implementation Steps

1. Create `TransitionSignals` class that gathers:
   - Gesture frequency (gestures per hour)
   - Gesture diversity (unique verbs used)
   - Plot progress delta (change since season start)
   - Artifacts created (session artifacts)
   - Time in season
   - Entropy spent ratio

2. Create `evaluate_season_transition()` that:
   - Gathers signals
   - Checks each transition rule
   - Returns `SeasonTransition` with confidence score

3. Hook into `apply_gesture()`:
   - After applying gesture, evaluate transition
   - If confidence > 0.7, suggest (don't auto-apply)
   - Add `suggested_transition` to `TendingResult`

4. Update API:
   - Include suggestions in tend response
   - Add `POST /v1/gardener/garden/transition/accept` endpoint
   - Add `POST /v1/gardener/garden/transition/dismiss` endpoint

5. Update Web UI:
   - Toast/modal for transition suggestions
   - Accept/dismiss buttons
   - Visual preview of new season

### Tests to Write

- `test_transition_signals.py` - Signal gathering
- `test_season_transitions.py` - Each transition path
- `test_auto_inducer.py` - Integration with gesture application

---

## Key Design Decisions

1. **Suggest, Don't Auto-Apply**: Transitions should be suggested with confidence scores, not automatically applied. User confirms.

2. **Confidence Threshold**: Only suggest when confidence > 0.7 to avoid noise.

3. **Dismissal Memory**: If user dismisses, don't suggest same transition for N hours.

4. **Session Integration**: Session phase changes can trigger garden season changes (already wired in Phase 4).

---

## Success Criteria

- [x] `kg tend observe concept.gardener` can trigger DORMANT → SPROUTING suggestion
- [x] Transition suggestions appear in Web UI
- [x] User can accept or dismiss suggestions
- [x] Each transition path has tests
- [x] Dismissed suggestions don't reappear immediately

---

## Relevant Existing Code

```python
# Garden seasons and their properties (garden.py)
class GardenSeason(Enum):
    DORMANT = auto()      # plasticity: 0.1, entropy_mult: 0.5
    SPROUTING = auto()    # plasticity: 0.9, entropy_mult: 1.5
    BLOOMING = auto()     # plasticity: 0.3, entropy_mult: 1.0
    HARVEST = auto()      # plasticity: 0.2, entropy_mult: 0.8
    COMPOSTING = auto()   # plasticity: 0.8, entropy_mult: 2.0

# Existing transition method (garden.py)
def transition_season(self, new_season: GardenSeason, reason: str = "") -> None:
    """Transition to a new season, recording a ROTATE gesture."""
    ...

# TendingResult already has synergies_triggered (tending.py)
@dataclass
class TendingResult:
    gesture: TendingGesture
    accepted: bool
    state_changed: bool
    changes: list[str]
    synergies_triggered: list[str]  # Add suggested_transition here
    reasoning_trace: tuple[str, ...]
    error: str | None = None
```

---

## Command to Start

```bash
# Read the full plan first
cat plans/gardener-logos-enactment.md | head -200

# Then start implementing
# 1. Create seasons.py with TransitionSignals
# 2. Add evaluate_season_transition
# 3. Hook into apply_gesture
# 4. Update API
# 5. Update Web UI
# 6. Write tests
```

---

*Created: 2024-12-16 | Phase 7 Complete | Phase 8 Ready*
