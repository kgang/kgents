# A-gent Refactor: Art → Alethic Architecture Focus

> *"The noun is a lie. There is only truth-seeking architecture."*

**Status**: Ready to Execute
**Session**: 2025-12-21

---

## The Problem

A-gent is currently split between two unrelated concerns:
1. **Abstract**: Agent skeletons (good, foundational)
2. **Art**: Creativity coaching (doesn't belong here)

The "art" concept was well-intentioned but doesn't align with A-gent's true purpose: **Alethic Architecture**—the truth-preserving, categorical foundation for all agents.

---

## What is Alethic Architecture?

"Alethic" comes from Greek *aletheia* (truth/disclosure). In kgents, it means:

### The Nucleus-Halo-Projector Triad

```
┌─────────────────────────────────────────────────────────────────────┐
│  NUCLEUS         Pure Agent[A, B] logic (what it does)              │
├─────────────────────────────────────────────────────────────────────┤
│  HALO            @Capability.* decorators (what it could become)    │
├─────────────────────────────────────────────────────────────────────┤
│  PROJECTOR       Target-specific compilation (how it manifests)     │
└─────────────────────────────────────────────────────────────────────┘
```

### Why "Alethic"?

1. **Truth-Preserving**: Category laws (identity, associativity) are verified
2. **Self-Disclosing**: Agents describe themselves through Halos
3. **Ground Reality**: `GROUND`, `JUDGE`, `SUBLATE` primitives operate on claims

### Core Components (Already Implemented)

| Component | File | Purpose |
|-----------|------|---------|
| **AlethicAgent** | `alethic.py` | Polynomial state machine for truth-seeking |
| **Halo** | `halo.py` | Declarative capability metadata |
| **Archetypes** | `archetypes.py` | Pre-packaged patterns (Kappa, Lambda, Delta) |
| **Functor** | `functor.py` | Universal lifting with law verification |
| **Skeleton** | `skeleton.py` | Minimal agent contract |
| **Quick** | `quick.py` | `@agent` decorator for rapid creation |

---

## The Refactor

### Phase 1: Spec Surgery (spec/a-gents/)

| Action | File | Change |
|--------|------|--------|
| **Rewrite** | `README.md` | Remove art, focus on alethic architecture |
| **Delete** | `art/creativity-coach.md` | Doesn't belong in A-gent |
| **Delete** | `art/` directory | Clean up |
| **Create** | `alethic.md` | New spec for alethic architecture |
| **Rename** | `abstract/` → `core/` | Clearer naming |
| **Update** | `core/skeleton.md` | Link to alethic.md |

### Phase 2: Impl Cleanup (impl/claude/agents/a/)

| Action | File | Change |
|--------|------|--------|
| **Delete** | `creativity.py` | Move to graveyard or separate module |
| **Update** | `__init__.py` | Remove creativity exports |
| **Verify** | `_tests/` | Ensure tests still pass |

### Phase 3: Documentation Refresh

| Action | File | Change |
|--------|------|--------|
| **Update** | `docs/architecture-overview.md` | Emphasize alethic architecture |
| **Update** | `CLAUDE.md` references | Use "alethic" consistently |

---

## The New A-gent Narrative

After refactoring, A-gent becomes:

```markdown
# A-gents: Alethic Architecture

> "A" for Architecture. A for Aletheia. A for the foundation upon which all agents stand.

A-gents provide the **truth-preserving** foundation:
- The skeleton (what every agent MUST be)
- The Halo (declarative capabilities)
- The Archetypes (pre-packaged patterns)
- The Alethic Agent (polynomial truth-seeking)
- The Functor Protocol (categorical law verification)
```

---

## Why This Matters

### Before: Confused Identity
```
A-gent = Abstract (skeleton) + Art (creativity)
       = Foundational + Tangential
       = Cognitive dissonance
```

### After: Clear Purpose
```
A-gent = Alethic Architecture
       = Skeleton + Halo + Archetypes + Polynomial + Functor
       = Truth-preserving agent foundation
       = "The ground upon which all agents stand"
```

---

## The Creativity Coach: Where It Goes

The CreativityCoach is a legitimate agent—it just doesn't belong under A-gent.

**Options**:
1. **Move to services/muse/** — Makes sense thematically
2. **Move to agents/c/** — C for Creative (new genus)
3. **Archive** — If not actively used

Recommendation: Move to `services/muse/` since it's LLM-backed and fits the Muse service concept.

---

## Verification

```bash
# After changes
cd impl/claude
uv run pytest agents/a/ -v
uv run mypy agents/a/
```

---

## Voice Check (Anti-Sausage)

*"Daring, bold, creative, opinionated but not gaudy"*

This refactor is opinionated—we're saying "art doesn't belong here." That's bold.
We're advocating for a focused, categorical foundation. That's daring.
We're cleaning up conceptual clutter. That's tasteful.

---

*The Alethic Architecture: Where truth-seeking becomes structure.*
