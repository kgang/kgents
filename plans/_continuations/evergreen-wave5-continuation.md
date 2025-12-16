# Wave 5 Continuation: Multi-Source Fusion

**Wave:** 5
**Status:** PENDING
**Predecessor:** Wave 4 (Habit Encoder + TextGRAD) ✅
**Tests baseline:** 284 passing

---

## Context

Wave 4 built the habit encoding pipeline:
- `HabitEncoder` aggregates signals from git, sessions, and code
- `PolicyVector` captures learned preferences
- `TextGRADImprover` applies feedback as textual gradients
- Simple weighted merging via `PolicyVector.merge_with()`

**The gap:** Current merging is naive weighted averaging. Wave 5 adds intelligent fusion.

---

## Wave 5 Mission: Multi-Source Fusion

Build semantic-aware merging that handles:
1. **Conflicting signals** — Git says terse, code says verbose
2. **Semantic similarity** — Merge related domains (cli ≈ commands)
3. **Temporal decay** — Recent patterns weighted higher
4. **Coherence checking** — Ensure merged policy makes sense

---

## Tasks

### P0: Conflict Detection

```python
class ConflictDetector:
    def detect(self, policies: list[PolicyVector]) -> list[Conflict]:
        """Find contradictory signals between sources."""
        # e.g., git.verbosity=0.3, code.verbosity=0.8 → conflict
```

**File:** `habits/fusion/conflict.py`

### P1: Semantic Similarity

```python
class DomainMatcher:
    def similarity(self, domain1: str, domain2: str) -> float:
        """Compute semantic similarity between domains."""
        # cli ≈ commands → 0.8
        # agentese ≈ protocols → 0.6
```

**File:** `habits/fusion/semantic.py`

### P2: Temporal Weighting

```python
class TemporalWeighter:
    def weight(self, pattern: GitPattern, now: datetime) -> float:
        """Weight pattern by recency (exponential decay)."""
        # Recent commits matter more than old ones
```

**File:** `habits/fusion/temporal.py`

### P3: Coherence Checker

```python
class CoherenceChecker:
    def check(self, policy: PolicyVector) -> list[Incoherence]:
        """Find internal inconsistencies in merged policy."""
        # e.g., high formality + high risk_tolerance → suspicious
```

**File:** `habits/fusion/coherence.py`

### P4: Smart Merger

```python
class SmartMerger:
    def merge(self, policies: list[PolicyVector]) -> PolicyVector:
        """
        Merge with conflict resolution and coherence.

        1. Detect conflicts
        2. Resolve via semantic similarity
        3. Apply temporal weighting
        4. Check coherence
        5. Return merged policy with full reasoning trace
        """
```

**File:** `habits/fusion/merger.py`

---

## Key Files to Read

| File | Purpose |
|------|---------|
| `habits/encoder.py` | Current simple merge logic |
| `habits/policy.py` | PolicyVector with `merge_with()` |
| `_epilogues/2025-12-16-evergreen-wave4-complete.md` | Wave 4 learnings |

---

## Success Criteria

- [ ] Conflicts detected between git/session/code signals
- [ ] Semantic similarity groups related domains
- [ ] Recent patterns weighted higher (configurable decay)
- [ ] Incoherent merges flagged with reasoning
- [ ] All 284+ tests still passing
- [ ] New fusion tests added

---

## Taste Decisions (Binding)

From reformation session:
- **Transparency:** Show reasoning for all fusion decisions
- **Conflict resolution:** Merge heuristically, not hard precedence
- **Autonomy:** Auto-resolve conflicts with full rollback capability

---

## Begin

```
Wave 5 starting. Focus: Multi-Source Fusion.

Reading:
1. habits/encoder.py (current merge logic)
2. habits/policy.py (PolicyVector)
3. Wave 4 epilogue (learnings)

Creating habits/fusion/ module...
```
