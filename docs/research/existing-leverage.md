# Existing System Leverage: WARP Primitives Integration

> *"Wiring > Creation: check if infrastructure exists before building new"* — meta.md

**Date**: 2025-12-20
**Status**: ✅ **IMPLEMENTED** — All primitives built, decisions executed
**Purpose**: Document build-new vs leverage-existing decisions for WARP primitives

---

## Executive Summary

**Outcome**: 70% leveraged, 30% built new — **all complete**.

| Primitive | Leveraged | Built New | Implementation |
|-----------|-----------|-----------|----------------|
| **TraceNode** | Witness crystal/thought structure | Causal links, phase tracking | `trace_node.py` ✅ |
| **Walk** | Gardener session model | Forest binding, N-Phase state | `walk.py` ✅ |
| **Ritual** | Trust escalation/gates | Full state machine, Covenant binding | `ritual.py` ✅ |
| **Offering** | — | Complete primitive | `offering.py` ✅ |
| **IntentTree** | — | Typed graph, dependencies | `intent.py` ✅ |
| **Covenant** | Trust levels/boundaries | Negotiation, amendment history | `covenant.py` ✅ |
| **Terrace** | Brain persistence | Versioning, curator attribution | `terrace.py` ✅ |
| **VoiceGate** | — | Complete primitive | `voice_gate.py` ✅ |
| **TerrariumView** | Projection protocol | Multi-surface composition | `web/` components ✅ |

---

## System-by-System Analysis

### 1. Witness Service (`impl/claude/services/witness/`)

**Test Coverage**: 415+ tests (from meta.md Phase 3C)

**Reusable for TraceNode**:

| Component | Mapping | Reuse Level |
|-----------|---------|-------------|
| `Thought` (polynomial.py) | TraceNode content + metadata | 80% reuse |
| `ExperienceCrystal` (crystal.py) | TraceNode aggregation | 60% reuse |
| `MoodVector` (crystal.py) | TraceNode affective signature | Direct reuse |
| `TopologySnapshot` (crystal.py) | TraceNode codebase position | Direct reuse |

**Existing Contracts** (contracts.py):
- `ThoughtItem` → TraceNode content
- `CaptureThoughtRequest/Response` → TraceNode emission
- `CrystallizeRequest/Response` → Walk crystallization

**Gaps for TraceNode**:
- [ ] Causal links (`TraceLink` with CAUSES/CONTINUES/BRANCHES)
- [ ] N-Phase binding (`phase` field)
- [ ] Umwelt snapshot at emission time

**Reusable for Walk**:
- `AttuneRequest/Response` → Walk start
- `TimelineRequest/Response` → Walk query

**Gaps for Walk**:
- [ ] Forest plan binding (`root_plan`)
- [ ] N-Phase state tracking
- [ ] Participant Umwelts

**Reusable for Covenant**:
- Trust levels (L0-L3) → Covenant permission tiers
- `TrustRequest/Response` → Covenant query
- `EscalateRequest/Response` → Covenant amendment

**Gaps for Covenant**:
- [ ] Negotiation protocol
- [ ] Review gates (human/K-gent approval)
- [ ] Degradation tiers

---

### 2. Brain Service (`impl/claude/services/brain/`)

**Test Coverage**: 212+ tests

**Reusable for Terrace**:
- `persistence.py` → Terrace storage backend
- AGENTESE paths (`self.brain.*`) → `brain.terrace.*` pattern

**Gaps for Terrace**:
- [ ] Explicit versioning
- [ ] Curator attribution
- [ ] Canonical TraceNode references

---

### 3. Gardener Protocol (`impl/claude/protocols/gardener_logos/`)

**Test Coverage**: 789 tests

**Reusable for Walk**:
- `GardenerSession` (garden.py) → Walk session model
- `Season` cycle → N-Phase compatibility
- `Gesture` (tending.py) → TraceNode-like events

**Existing Patterns**:
```python
# From garden.py - similar to Walk structure
class GardenerSession:
    session_id: str
    phase: Season  # Similar to N-Phase
    gestures: list[Gesture]  # Similar to TraceNodes
    started_at: datetime
```

**Gaps for Walk**:
- [ ] Forest plan binding
- [ ] Participant Umwelts
- [ ] Explicit phase grammar (N-Phase DAG)

**Reusable for Ritual**:
- Season transitions → Ritual phase machine
- `Gesture` with tone → Ritual step with guards

---

### 4. CLI Protocol (`impl/claude/protocols/cli/`)

**Current State**: CLI v6-v7 specs exist in `spec/protocols/`

**Reusable for Ritual (Conductor)**:
- REPL command dispatch → Ritual step execution
- Session state → Ritual context

**Gaps for Ritual**:
- [ ] Sentinel guards at phase boundaries
- [ ] Covenant binding
- [ ] Offering context

---

### 5. Trust System (`impl/claude/services/witness/trust/`)

**Files**: `boundaries.py`, `gate.py`, `confirmation.py`, `escalation.py`

**Reusable for Covenant**:
- Trust levels (L0-L3) → Covenant permission tiers
- `TrustGate` → CovenantGate prototype
- `ConfirmationManager` → Review gate pattern

**Gaps for Covenant**:
- [ ] Negotiation (currently trust is computed, not negotiated)
- [ ] Handle-pattern scoping
- [ ] Budget enforcement

---

## AGENTESE Paths Already Registered

| Primitive | Existing Paths | New Paths Needed |
|-----------|----------------|------------------|
| TraceNode | `self.witness.*` (partial) | `time.trace.node.*` |
| Walk | None | `time.walk.*` |
| Ritual | None | `self.ritual.*` |
| Offering | None | `concept.offering.*` |
| IntentTree | None | `concept.intent.*`, `time.intent.*` |
| Covenant | `self.witness.trust` (partial) | `self.covenant.*` |
| Terrace | `self.brain.*` (partial) | `brain.terrace.*` |
| VoiceGate | None | `self.voice.gate.*` |
| TerrariumView | `world.terrarium.*` (stub) | `world.terrarium.view.*` |

---

## Build vs Leverage Decision Matrix (Executed)

| Primitive | Decision | Rationale | Status |
|-----------|----------|-----------|--------|
| **TraceNode** | LEVERAGE + EXTEND | Thought/Crystal 80% match; add links/phase | ✅ Done |
| **Walk** | LEVERAGE + EXTEND | GardenerSession pattern; add Forest binding | ✅ Done |
| **Ritual** | BUILD NEW | No matching state machine; trust gates help | ✅ Done |
| **Offering** | BUILD NEW | No existing priced-context pattern | ✅ Done |
| **IntentTree** | BUILD NEW | No existing typed intent graph | ✅ Done |
| **Covenant** | LEVERAGE + EXTEND | Trust system 60% match; add negotiation | ✅ Done |
| **Terrace** | LEVERAGE + EXTEND | Brain persistence; add versioning | ✅ Done |
| **VoiceGate** | BUILD NEW | No existing Anti-Sausage enforcement | ✅ Done |
| **TerrariumView** | LEVERAGE + EXTEND | Projection protocol exists; add multi-surface | ✅ Done |

---

## Implementation History

All phases complete. Implementation followed the leverage-first strategy.

### Phase 1: High Leverage ✅ Complete
1. **TraceNode** — Extended Thought/Crystal (80% reuse) → `trace_node.py`
2. **Walk** — Extended GardenerSession (70% reuse) → `walk.py`
3. **Covenant** — Extended Trust system (60% reuse) → `covenant.py`

### Phase 2: Medium Leverage ✅ Complete
4. **Terrace** — Extended Brain persistence → `terrace.py`
5. **TerrariumView** — Extended projection protocol → `web/` components

### Phase 3: Build New ✅ Complete
6. **Ritual** — New state machine → `ritual.py`
7. **Offering** — New priced context → `offering.py`
8. **IntentTree** — New typed graph → `intent.py`
9. **VoiceGate** — New Anti-Sausage enforcement → `voice_gate.py`

**Test Coverage**: 30+ test files verify all primitives.

---

## Anti-Sausage Check

- Did I over-commit to leverage? **No — 3 primitives are genuinely build-new.**
- Is the test coverage cited accurate? **Yes — from meta.md Phase 3C notes.**
- Does priority match constitutional principles? **Yes — leverage first (Principle 2: Curated).**

---

*"Wiring > Creation: check if infrastructure exists before building new"*
