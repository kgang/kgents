# WARP Phase 1 Continuation Prompt: Chunks 7-8

**Status**: ✅ COMPLETE (2025-12-20)

---

## Context

**What's Done** (258 tests passing):
- ✅ Chunk 1: TraceNode Foundation
- ✅ Chunk 2: Walk Session
- ✅ Chunk 3: Offering (34 tests) - `services/witness/offering.py`
- ✅ Chunk 4: Covenant (34 tests) - `services/witness/covenant.py`
- ✅ Chunk 5: Ritual (29 tests) - `services/witness/ritual.py`
- ✅ Chunk 6: IntentTree (31 tests) - `services/witness/intent.py`
- ✅ Chunk 7: VoiceGate (72 tests) - `services/witness/voice_gate.py`
- ✅ Chunk 8: Terrace (58 tests) - `services/witness/terrace.py`

**All exports added to** `services/witness/__init__.py`

**Key Files**:
```
impl/claude/services/witness/offering.py    — Budget, Offering, handle scopes
impl/claude/services/witness/covenant.py    — Covenant, ReviewGate, CovenantEnforcer
impl/claude/services/witness/ritual.py      — Ritual, SentinelGuard, phase management
impl/claude/services/witness/intent.py      — Intent, IntentTree, status propagation
impl/claude/services/witness/voice_gate.py  — VoiceGate, denylist, anchor tracking
impl/claude/services/witness/terrace.py     — Terrace, versioning, topic history
```

---

## Reflection & Open Questions

See: `plans/warp-phase1-reflection.md` for detailed analysis.

**Key Concerns**:
1. **Spec Drift** - Terrace implementation simpler than spec vision
2. **Missing AGENTESE nodes** - `self.voice.gate.*` and `brain.terrace.*` not wired
3. **No Persistence** - In-memory only
4. **Missing TerrariumView** - Spec includes it, continuation didn't

**Decision Needed**:
- Update spec to match implementation? OR
- Update implementation to match spec?

---

## Next Steps (If Continuing)

1. **AGENTESE Nodes** (required for protocol access):
   - `protocols/agentese/contexts/self_voice.py` → `self.voice.gate.*`
   - `protocols/agentese/contexts/brain_terrace.py` → `brain.terrace.*`

2. **Composition Stories** (how primitives work together):
   - Ritual + VoiceGate: Check outputs during workflow
   - Offering + Terrace: Scope knowledge access by budget

3. **Persistence** (for durability):
   - Integrate with WitnessPersistence or add file backing

---

*"Tasteful > feature-complete"* — Reflection captured concerns honestly.
