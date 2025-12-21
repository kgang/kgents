# Handoff: Metabolic Development Phase Continuation

## Session Context

**Date**: 2025-12-21
**Branch**: `main`
**Plan**: `plans/metabolic.md`

---

## What Was Accomplished

### Phase 0: Foundation Wiring ✅
| Checkpoint | File | Tests |
|------------|------|-------|
| 0.1 Stigmergy→Coffee | `services/liminal/coffee/stigmergy.py` | 8 |
| 0.2 Hydrator→Brain | `services/living_docs/brain_adapter.py` | 12 |
| 0.3 Session Polynomial | `services/metabolism/polynomial.py` | 4 |

### Phase 1: Morning Start Journey (Partial)
| Checkpoint | Status | File |
|------------|--------|------|
| 1.1 Circadian Resonance | ✅ Complete | `services/liminal/coffee/circadian.py` |
| 1.2 Serendipity (10%) | ✅ Complete | (same file) |
| 1.3 Full Morning Flow | ⏳ **NEXT** | Wire to CLI |

### Phase 2: Evidence Pipeline (Partial)
| Checkpoint | Status | File |
|------------|--------|------|
| 2.1 ASHC Continuous Mode | ✅ Complete | `services/metabolism/evidencing.py` |
| 2.2 Interactive Text | ❌ Not started | - |
| 2.3 Verification Graph | ❌ Not started | - |

### D-gent Persistence ✅
- `services/metabolism/persistence.py` - MetabolismPersistence implemented
- Wired to BackgroundEvidencing and VoiceStigmergy

---

## What's Next

### Priority 1: Checkpoint 1.3 - Full Morning Start Flow

**User Journey**:
```
$ kg coffee begin

☕ Good morning

💫 This morning echoes December 14th...
   Then, you said: "I want to feel like I'm exploring, not completing."
   That morning, you chose 🎲 SERENDIPITOUS and discovered sheaf coherence.

📍 FROM YOUR PATTERNS
   "Ship something" appears in 7 of last 10 mornings
   "Depth over breadth" — recurring voice anchor

🎲 FROM THE VOID (10% serendipity)
   Three weeks ago: "The constraint is the freedom"

[What brings you here today?]
> finish the verification integration and make it feel magical

✨ Intent captured. Hydrating context...

🚨 CRITICAL (2)
  - ASHC Compiler: Evidence requires 10+ runs (test_evidence.py)
  - Verification: Trace witnesses must link to requirements

📁 FILES YOU'LL LIKELY TOUCH
  - services/verification/core.py
  - protocols/ashc/evidence.py

🎯 VOICE ANCHORS (preserve these)
  "Tasteful > feature-complete"
  "The Mirror Test"

Context compiled. Good morning, Kent.
```

**Deliverables**:
1. Update `kg coffee begin` CLI handler to use `CircadianResonance.get_context()`
2. Integrate with `Hydrator` for gotchas/files
3. Generate `HYDRATE.md` for Claude Code context injection
4. Session polynomial transition: DORMANT → GREETING → HYDRATING → FLOWING

**Key Files**:
- `protocols/cli/handlers/coffee.py` - CLI entry point
- `services/liminal/coffee/core.py` - CoffeeService orchestrator
- `services/liminal/coffee/circadian.py` - CircadianResonance (ready)
- `services/living_docs/hydrator.py` - Context compilation

---

### Priority 2: Checkpoint 2.2 - Interactive Text

**User Journey**: Specs are live control surfaces
```
- [x] Implement verification integration
    ↓ (click)
TraceWitness captured
    ↓
Linked to requirement 7.1
    ↓
Evidence attached to derivation chain
```

**Deliverables**:
1. Create `services/interactive_text/` Crown Jewel structure
2. Token parser: AGENTESE paths, task checkboxes, images, code blocks
3. `TaskCheckboxToken.on_toggle()` → TraceWitness capture
4. Roundtrip fidelity: `parse(render(parse(doc))) ≡ parse(doc)`

**Spec**: `plans/interactive-text-implementation.md`

---

### Priority 3: Checkpoint 2.3 - Verification Graph

**User Journey**: See the derivation chain
```
Principle (Composable)
    └── Requirement 5.1: Agents compose via >>
        └── Task: Implement composition operator
            └── Trace: test_compose.py::test_pipeline passed
                └── Evidence: 47 runs, 94% pass rate
```

**Deliverables**:
1. `VerificationGraph`: Principle → Requirement → Task → Trace → Evidence
2. AGENTESE path: `concept.docs.derivation`
3. CLI: `kg docs derivation spec/agents/poly.md`

---

## Key Patterns Already Established

### CircadianResonance Usage
```python
from services.liminal.coffee import CircadianResonance, load_recent_voices

resonance = CircadianResonance()
voices = load_recent_voices(limit=30)
context = resonance.get_context(voices)

# context.resonances - similar past mornings
# context.patterns - recurring themes
# context.serendipity - optional FOSSIL wisdom (10% chance)
```

### BackgroundEvidencing Usage
```python
from services.metabolism import get_background_evidencing

accumulator = get_background_evidencing()

# Fire-and-forget verification
run_id = await accumulator.schedule_verification(
    task_pattern="verification integration",
    file_content=code,
    test_files=["test_core.py"],
)

# Query accumulated evidence
evidence = accumulator.get_evidence("verification")
# evidence.run_count, evidence.pass_rate, evidence.diversity_score
```

### HydrationBrainAdapter Usage
```python
from services.living_docs.brain_adapter import HydrationBrainAdapter

adapter = HydrationBrainAdapter()

# Get prior ASHC evidence for task
evidence_list = await adapter.find_prior_evidence("verification")

# Get semantic teaching moments (requires Brain)
teaching = await adapter.find_semantic_teaching("verification tests")
```

---

## Test Commands

```bash
# Run all metabolic tests
cd impl/claude && uv run pytest services/metabolism/ -v

# Run circadian tests
uv run pytest services/liminal/coffee/_tests/test_circadian.py -v

# Run evidencing tests
uv run pytest services/metabolism/_tests/test_evidencing.py -v

# Type check
uv run mypy services/metabolism/ services/liminal/coffee/circadian.py
```

---

## Voice Anchors (Preserve These)

> "Daring, bold, creative, opinionated but not gaudy"
> "The Mirror Test: Does K-gent feel like me on my best day?"
> "Tasteful > feature-complete"
> "The persona is a garden, not a museum"
> "Depth over breadth"

---

## Architecture Reference

```
impl/claude/services/
├── metabolism/                    # Metabolic core
│   ├── __init__.py
│   ├── polynomial.py              # SESSION_POLYNOMIAL ✅
│   ├── evidencing.py              # BackgroundEvidencing ✅
│   ├── persistence.py             # MetabolismPersistence ✅
│   └── _tests/
├── liminal/coffee/                # Morning Coffee
│   ├── circadian.py               # CircadianResonance ✅
│   ├── stigmergy.py               # VoiceStigmergy ✅
│   ├── capture.py                 # Voice capture
│   ├── core.py                    # CoffeeService
│   └── _tests/
├── living_docs/                   # Context compilation
│   ├── hydrator.py                # Keyword matching
│   ├── brain_adapter.py           # Semantic + ASHC evidence ✅
│   └── _tests/
└── interactive_text/              # NEW (Phase 2.2)
    ├── __init__.py
    ├── parser.py                  # Markdown → AST
    ├── tokens/                    # Token implementations
    └── _tests/
```

---

## Suggested Session Start

```
/hydrate Execute Phase 1.3 of kgents/plans/metabolic.md

Phase 0-2.1 complete. Now wire the full morning start flow.

Start by reading:
- plans/metabolic.md (Checkpoint 1.3)
- services/liminal/coffee/core.py (CoffeeService)
- protocols/cli/handlers/coffee.py (CLI entry point)

Wire CircadianResonance.get_context() into kg coffee begin.
Generate HYDRATE.md with voice anchors, gotchas, and likely files.
```

---

*Generated: 2025-12-21 | Metabolic Development Phase 0-2.1 Complete*
