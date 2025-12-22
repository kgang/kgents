# Witness Crystallization: Implementation Plan

> *"The proof IS the decision. The compression IS the wisdom."*

**Status:** ✅ Phase 4 Complete (2025-12-22)
**Spec:** `spec/protocols/witness-crystallization.md`
**Priority:** MEDIUM
**Filed:** 2025-12-22

---

## Completion Status

| Phase | Status | Tests |
|-------|--------|-------|
| Phase 1: Core Crystal Infrastructure | ✅ Complete | 200+ tests |
| Phase 2: Lineage Ergonomics | ✅ Complete | 50+ tests |
| Phase 3: Context Budget System | ✅ Complete | 34 tests |
| Phase 4: Integration & Streaming | ✅ Complete | 26 tests |
| Phase 5: Visual Projection | 🔮 Future | - |

**Total Tests:** 678 passing in witness suite

---

## Phase 4 Implementation Summary (2025-12-22)

### What Was Built

**1. Handoff Integration** (`services/witness/integration.py`)
- `prepare_handoff_context()` — Auto-crystallize marks before session transfer
- `HandoffContext` — Data structure with new crystal, recent crystals, tokens used
- `format_for_handoff()` — Markdown formatting for handoff prompts

**2. NOW.md Proposal Generation** (`services/witness/integration.py`)
- `propose_now_update()` — Generate section updates from day crystals
- `NowMdProposal` — Proposal dataclass with section, content, source crystals
- `apply_now_proposal()` — Apply proposals with automatic backup
- `_extract_section()` — Markdown section extraction

**3. Brain Promotion** (`services/witness/integration.py`)
- `identify_promotion_candidates()` — Score crystals for promotion
- `PromotionCandidate` — Candidate with score and reasons
- `promote_to_brain()` — Promote crystal to Brain TeachingCrystal
- `auto_promote_crystals()` — Auto-promote top candidates

**4. Crystal Streaming** (`services/witness/stream.py`)
- `crystal_stream()` — Async generator for SSE events
- `CrystalEvent` — Event dataclass with SSE formatting
- `CrystalEventType` — CREATED, BATCH, HEARTBEAT, ERROR
- `publish_crystal_created()` — Publish to WitnessSynergyBus
- `create_crystal_sse_response()` — FastAPI/Starlette helper

### CLI Commands Added

```bash
kg witness stream                    # Real-time crystal events
kg witness stream --level 0          # Filter by level

kg witness propose-now               # Show NOW.md proposals
kg witness propose-now --apply       # Apply with backup
kg witness propose-now --json        # Machine output

kg witness promote <crystal_id>      # Promote specific crystal
kg witness promote --auto            # Auto-promote top 3
kg witness promote --candidates      # List promotion candidates
kg witness promote --json            # Machine output
```

### Files Created

```
impl/claude/services/witness/integration.py    # Handoff, NOW.md, Brain
impl/claude/services/witness/stream.py         # SSE streaming
impl/claude/services/witness/_tests/test_phase4.py  # 26 tests
```

### Files Modified

```
impl/claude/protocols/cli/handlers/witness_thin.py  # New commands
impl/claude/services/witness/__init__.py            # Exports
HYDRATE.md                                          # Documentation
```

---

## Phase 5: Visual Projection (Future)

When ready to implement:

1. **CLI Dashboard** — Rich terminal UI for crystal hierarchy
2. **Web Components** — CrystalHierarchy.tsx, CrystalExpander.tsx
3. **SSE Integration** — Real-time web updates

---

## API Summary

```python
# Handoff (call before /handoff)
from services.witness import prepare_handoff_context
ctx = await prepare_handoff_context(soul, session_id="abc")
handoff_text += ctx.format_for_handoff()

# NOW.md proposals
from services.witness import propose_now_update, apply_now_proposal
proposals = await propose_now_update()
for p in proposals:
    apply_now_proposal(p, Path("NOW.md"))

# Brain promotion
from services.witness import identify_promotion_candidates, promote_to_brain
candidates = identify_promotion_candidates(min_confidence=0.85)
await promote_to_brain(candidates[0].crystal.id)

# Crystal streaming
from services.witness import crystal_stream
async for event in crystal_stream(level_filter=CrystalLevel.SESSION):
    print(event)  # SSE-formatted string
```

---

*"Crystallization happens at boundaries. The handoff IS the moment of compression."*
