# WARP + Servo Integration: Session 5 Handoff

> *"Law 3: Every AGENTESE invocation emits exactly one TraceNode."*

**Date**: 2025-12-20
**Previous Session**: Session 4 (TraceNode Coverage Enforcement at Gateway)
**This Session**: C1.1 Brain → TraceNode Integration (COMPLETE)

---

## Session 5 Accomplishments

### C1.1: Brain → TraceNode Integration (COMPLETE)

**Verified**: All Brain operations emit TraceNodes via gateway instrumentation from Session 4.

**Tests Added** (`services/brain/_tests/test_node.py`):
- `TestBrainWARPIntegration` class with 4 tests:
  - `test_brain_terrace_manifest_emits_trace_node`
  - `test_brain_terrace_create_emits_trace_node`
  - `test_brain_terrace_search_emits_trace_node`
  - `test_multiple_operations_emit_multiple_traces`

**Key Learning**:
```
Registry + pytest fixture timing: After reset_registry(), call repopulate_registry()
to re-register @node classes from already-imported modules.
```

**Test Count**: 28 Brain tests passing, 890+ Witness tests passing

---

## Remaining Work

### C1.2: Brain → VoiceGate Integration (45 min) — NEXT

Wire VoiceGate into Brain's synthesis flow for trust-gated output.

**Files**:
- `services/brain/node.py` (or new `services/brain/synthesis.py`)
- `services/witness/voice_gate.py`

**Tasks**:
- [ ] Inject VoiceGate into Brain's output generation
- [ ] Trust L0-L1: Template-only synthesis (no LLM)
- [ ] Trust L2-L3: LLM-assisted synthesis
- [ ] Add tests: trust level affects synthesis quality/richness

**Design**:
```python
# VoiceGate determines output expressiveness
voice_gate = VoiceGate(trust_level=observer.trust_level)
output = voice_gate.filter(raw_output)  # Trust gates the response
```

### C1.3: Terrace → Brain Crystal Wiring (45 min)

**Files**:
- `services/witness/terrace.py`
- `services/brain/crystal.py` (if exists)

**Tasks**:
- [ ] Terrace pulls from Brain's ExperienceCrystal storage
- [ ] Observer determines which crystals are visible
- [ ] Add tests: different observers see different projections

### C1.4: `brain.terrace.curate` Aspect (30 min)

**Files**:
- `protocols/agentese/contexts/brain_terrace.py`

**Tasks**:
- [ ] Create `brain.terrace.curate` aspect for human-curated knowledge
- [ ] Human override = trust L3 on that crystal
- [ ] Register in gateway
- [ ] Add tests: curate elevates trust

---

## Alternative: C2 Gardener + Walk Integration (1 hour)

If Brain integration feels heavy, this path provides immediate value:

**Files**:
- `services/gardener/`
- `services/witness/walk.py`

**Tasks**:
- [ ] Every CLI session creates a Walk
- [ ] Walk binds to current plan (Forest-aware)
- [ ] Gardener operations advance the Walk
- [ ] Walk pauses/resumes with session lifecycle

**Advantage**: Makes Claude Code sessions *observable* through WARP traces.

---

## Quick Start

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Run Brain WARP tests (should all pass)
uv run pytest services/brain/_tests/test_node.py::TestBrainWARPIntegration -v

# Run all Witness tests
uv run pytest services/witness/_tests/ -v --tb=short

# Check VoiceGate implementation
cat services/witness/voice_gate.py | head -100
```

---

## Key Files

| File | Purpose |
|------|---------|
| `services/brain/node.py` | BrainNode AGENTESE interface |
| `protocols/agentese/contexts/brain_terrace.py` | Terrace AGENTESE node |
| `services/witness/voice_gate.py` | Trust-gated output filtering |
| `services/witness/terrace.py` | Curated knowledge with versioning |
| `protocols/agentese/gateway.py` | TraceNode emission (lines 838-917) |

---

## Anti-Sausage Check

- ❓ Did I smooth anything that should stay rough? **No**
- ❓ Did I add words Kent wouldn't use? **No**
- ❓ Did I lose any opinionated stances? **No - Law 3 enforcement is bold**
- ❓ Is this still daring, bold, creative? **Yes - 4 new integration tests document WARP**

---

*"The persona is a garden, not a museum"* — Session 5 verified Brain is observable through WARP traces
