# Plan: Consolidate S-gent into D-gent

> *"State threading and persistence are two sides of the same coin. The separation was premature."*

**Status**: ACTIVE
**Created**: 2025-12-21

---

## The Problem

S-gent (State Agents) and D-gent (Data Agents) represent an artificial split:

| S-gent | D-gent |
|--------|--------|
| HOW state threads through computation | WHERE state lives (persistence) |
| State Monad as functor | Projection lattice (memory → postgres) |
| StateFunctor, StatefulAgent | DgentProtocol, Datum, backends |

**The insight**: The S-gent spec itself admits this is the Symbiont pattern:
> "Symbiont is the canonical composition of S-gent (state threading) and D-gent (persistence)."

But wait—Symbiont *already lives in D-gent* (`spec/d-gents/symbiont.md`)! The S-gent genus exists to document what is essentially a functor pattern that belongs in `c-gents/functor-catalog.md` and ergonomic usage patterns that belong in D-gent.

---

## Analysis: What S-gent Contains

### 1. `spec/s-gents/README.md` (~238 lines)
- Philosophy: "State is orthogonal to persistence" — **true but overstated**
- StateFunctor type definition
- Quick start patterns
- Relationship to D-gent/Flux/PolyAgent

**Verdict**: Core insight absorbed into D-gent; StateFunctor stays in functor-catalog.

### 2. `spec/s-gents/state-functor.md` (~420 lines)
- Formal functor definition: `StateFunctor[S]: C_Agent → C_Agent`
- Core operations: `lift()`, `lift_logic()`
- StatefulAgent wrapper
- `compose_flux()` for Flux composition
- Integration with TableAdapter

**Verdict**: This IS the State Functor in functor-catalog (§14). Move formal content there.

### 3. `spec/s-gents/composition.md` (~420 lines)
- Composition hierarchy: Flux ∘ State ∘ D-gent
- Pattern 1: State ∘ D-gent (Symbiont) — already in D-gent
- Pattern 2: Flux ∘ State — streaming stateful
- Pattern 3: Full stack composition
- Pattern 4: TableAdapter integration

**Verdict**: These are D-gent usage patterns. Move to `spec/d-gents/symbiont.md` or create `spec/d-gents/flux-composition.md`.

### 4. `spec/s-gents/laws.md` (~347 lines)
- Identity law: `StateFunctor.lift(Id) ≅ Id`
- Composition law: `lift(f >> g) ≅ lift(f) >> lift(g)`
- Verification strategies
- Property-based tests

**Verdict**: These are functor laws for State functor. Belongs in functor-catalog §14.

---

## What Gets Absorbed Where

| S-gent Content | Destination | Rationale |
|----------------|-------------|-----------|
| StateFunctor formal definition | `c-gents/functor-catalog.md` §14 | It's a functor |
| StateFunctor laws | `c-gents/functor-catalog.md` §14 | Functor laws |
| Symbiont patterns | Already in `d-gents/symbiont.md` | No change |
| Flux ∘ State composition | `d-gents/symbiont.md` | D-gent concern |
| TableAdapter integration | `d-gents/dual-track.md` | D-gent concern |
| Philosophy (state ≠ persistence) | D-gent README | D-gent framing |

---

## Implementation Plan

### Phase 1: Update Functor Catalog (§14)
Expand §14 to include the formal StateFunctor spec content that was in s-gents/state-functor.md.

### Phase 2: Update D-gent README
- Add section explaining that D-gent now owns state threading (via Symbiont)
- Clarify the StateFunctor is the formal name for what Symbiont implements
- Add Flux composition to Symbiont patterns

### Phase 3: Update D-gent Symbiont
- Add Flux ∘ State patterns from s-gents/composition.md
- Ensure complete coverage of state threading use cases

### Phase 4: Delete S-gent Genus
- Remove `spec/s-gents/` directory
- Update `spec/README.md` to not list S-gent (it wasn't listed anyway!)
- Update any cross-references

### Phase 5: Update Implementation References
- Update `impl/claude/agents/d/symbiont.py` docstrings
- Remove references to `spec/s-gents/`

---

## Why This Simplifies kgents

### Before (22+ agent genera)
```
a-gents, b-gents, c-gents, d-gents, f-gents, g-gents, h-gents, i-gents,
j-gents, k-gent, k8-gents, l-gents, m-gents, n-gents, o-gents, omega-gents,
p-gents, psi-gents, r-gents, s-gents, t-gents, u-gents, v-gents, w-gents
```

### After (21 agent genera)
S-gent was always an implementation detail masquerading as a genus. State threading is:
1. A **functor** (documented in c-gents/functor-catalog.md)
2. An **ergonomic pattern** (documented in d-gents/symbiont.md)

No new concepts. Just better organization.

---

## Principle Alignment

| Principle | How This Change Embodies It |
|-----------|----------------------------|
| **Tasteful** | Removes unnecessary abstraction layer |
| **Curated** | 21 genera > 22 genera when 22nd adds nothing new |
| **Composable** | StateFunctor stays composable; just better located |
| **Generative** | Simpler spec = easier regeneration |

---

## Backwards Compatibility

**Breaking changes**: None at implementation level.
- `Symbiont` class unchanged
- `StateFunctor` (if it existed) would be deprecated anyway
- Implementation lives in `agents/d/`, not `agents/s/`

**Documentation changes**:
- Links to `spec/s-gents/*` will 404
- Update any cross-references

---

## Files to Modify

1. **DELETE**: `spec/s-gents/` (entire directory)
2. **UPDATE**: `spec/c-gents/functor-catalog.md` (expand §14)
3. **UPDATE**: `spec/d-gents/README.md` (add state threading clarity)
4. **UPDATE**: `spec/d-gents/symbiont.md` (add Flux composition)
5. **UPDATE**: `impl/claude/agents/d/symbiont.py` (update docstrings)
6. **UPDATE**: Any files with cross-references to s-gents

---

## Success Criteria

- [ ] S-gent genus fully absorbed
- [ ] No loss of specification content
- [ ] Cleaner taxonomy (21 vs 22 genera)
- [ ] All cross-references updated
- [ ] Implementation unchanged (just docs)

---

*"The river and the riverbed were always one system. We just gave them different names."*
