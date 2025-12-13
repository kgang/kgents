# Plan: Categorical Consolidation

```yaml
status: complete
progress: 100%
priority: primary
blocks: []
enables: [k-gent-phase-3, flux-composition, effect-stacks]
```

> *"The system is beginning to buckle. Consolidate the algebra before adding more agents."*

---

## Problem Statement

kgents has 27+ agent types with sophisticated categorical foundations, but three structural problems limit composability:

1. **Asymmetric Lifting**: C-gent functors lift but can't unlift - agents enter monadic domains but can't escape
2. **Fragmented Observation**: O-gent, N-gent, T-gent each implement observation independently
3. **Hidden State**: D-gent protocol hides stateful computation instead of exposing it as a composable monad

These force hand-written transformers instead of declarative composition.

---

## Success Criteria

- `MaybeFunctor.unlift(maybe_agent)` works
- `ObserverFunctor.lift(any_agent)` unifies all observation
- `StateMonad.lift(agent)` enables `Flux(State(agent))`
- `FunctorRegistry.compose(Soul, Flux)` returns valid functor
- Cross-functor law tests pass in composition matrix

---

## Phases

### Phase 1: Symmetric Lifting (Foundation) ✓ COMPLETE

**Goal**: Every functor has both `lift()` and `unlift()`.

**Work**:
1. ✓ Added `unlift()` to MaybeFunctor, EitherFunctor, ListFunctor in `c/functor.py`
2. ✓ Added `unlift()` to AsyncFunctor, LoggedFunctor, FixFunctor
3. ✓ Verified round-trip: `unlift(lift(agent)) ≅ agent`
4. ✓ Added `UnliftError` exception for type safety
5. ✓ Updated `UniversalFunctor` base class with `unlift()` protocol

**Files**:
- `impl/claude/agents/c/functor.py` - 6 unlift functions + functor methods
- `impl/claude/agents/a/functor.py` - UniversalFunctor protocol
- `impl/claude/agents/c/_tests/test_functor_laws.py` - 7 new symmetric lifting tests

**Exit**: All 6 C-gent functors have symmetric lift/unlift with 44 passing tests.

---

### Phase 2: Observer Unification ✓ COMPLETE

**Goal**: Single `ObserverFunctor` replaces three parallel systems.

**Work**:
1. ✓ Defined `UnifiedObserverFunctor` in `o/observer_functor.py`
2. ✓ Created `ObservationSink` protocol (universal interface)
3. ✓ Created `ObservationEvent` (universal record type)
4. ✓ Created sink adapters: `ObserverSinkAdapter`, `HistorianSinkAdapter`, `MetricsSinkAdapter`
5. ✓ Created `ListSink` for simple observation
6. ✓ Implemented symmetric `lift()`/`unlift()` with round-trip law
7. ✓ Added convenience functions: `observe()`, `unobserve()`
8. ✓ Registered with `FunctorRegistry`

**Files**:
- New: `impl/claude/agents/o/observer_functor.py` - Unified functor + sinks
- New: `impl/claude/agents/o/_tests/test_unified_observer_functor.py` - 16 tests

**Exit**: `UnifiedObserverFunctor.lift(agent, sink=X)` works with O/N/T adapters. 60 total functor tests pass.

---

### Phase 3: State as Monad ✓ COMPLETE

**Goal**: D-gent protocol exposed as `StateMonad` functor.

**Work**:
1. ✓ Defined `StateMonadFunctor` in `d/state_monad.py`
2. ✓ Created `StatefulAgent` wrapper (threads state through computation)
3. ✓ Implemented `state_accessor` (inject state into input)
4. ✓ Implemented `state_extractor` (update state from output)
5. ✓ Implemented symmetric `lift()`/`unlift()` with round-trip law
6. ✓ Added convenience functions: `stateful()`, `unstateful()`
7. ✓ Registered with `FunctorRegistry` as "State"
8. ✓ Reuses existing `VolatileAgent` for default memory

**Files**:
- New: `impl/claude/agents/d/state_monad.py` - StateMonad functor
- New: `impl/claude/agents/d/_tests/test_state_monad.py` - 16 tests

**Exit**: `StateMonadFunctor.lift(agent, memory=X)` works. 76 total functor tests pass.

---

### Phase 4: Registry Activation ✓ COMPLETE

**Goal**: All functors registered, enabling declarative composition.

**Work**:
1. ✓ C-gent functors auto-registered: Maybe, Either, List, Async, Logged, Fix
2. ✓ SoulFunctor, FluxFunctor, UnifiedObserverFunctor, StateMonadFunctor registered
3. ✓ `compose_functors(F, G)` already implemented for transformer stacks
4. ✓ Registry contains 10 functors

**Registered Functors**:
- C-gent: Maybe, Either, List, Async, Logged, Fix
- K-gent: Soul
- Flux: Flux
- O-gent: Observer
- D-gent: State

**Files**:
- New: `impl/claude/agents/a/_tests/test_functor_registry.py` - 18 tests

**Exit**: `FunctorRegistry.all_functors()` returns 10 functors.

---

### Phase 5: Composition Matrix Tests ✓ COMPLETE

**Goal**: Systematic verification of cross-functor laws.

**Work**:
1. ✓ Created composition tests in `test_functor_registry.py`
2. ✓ Tested key pairs: Maybe.Logged, Either.List, Observer.Maybe, Flux.State, Observer.Logged, Maybe.Fix
3. ✓ Verified identity and composition laws via `compose_functors()`
4. ✓ All compositions work through standard functor interface

**Verified Compositions**:
- `Maybe . Logged` (optional + tracing)
- `Either . List` (error handling + collections)
- `Observer . Maybe` (observation + optional)
- `Flux . State` (streaming + state)
- `Observer . Logged` (observation + tracing)
- `Maybe . Fix` (optional + resilience)

**Files**:
- `impl/claude/agents/a/_tests/test_functor_registry.py` - includes composition matrix tests

**Exit**: 94 total functor tests pass.

---

## Summary

**Categorical Consolidation is COMPLETE.**

The kgents functor system has been transformed from ad-hoc patterns to a unified categorical framework:

| Before | After |
|--------|-------|
| 6 C-gent functors with lift() only | All functors have symmetric lift/unlift |
| 3 parallel observation systems (O/N/T) | Unified ObserverFunctor with pluggable sinks |
| D-gent state was opaque | StateMonad functor for composable state |
| No central registry | FunctorRegistry with 10 functors |
| No composition verification | 94 tests verifying laws and compositions |

**Key Artifacts Created**:
- `impl/claude/agents/c/functor.py` - 6 unlift functions + functor methods
- `impl/claude/agents/o/observer_functor.py` - Unified observation
- `impl/claude/agents/d/state_monad.py` - State monad functor
- `impl/claude/agents/a/_tests/test_functor_registry.py` - Composition tests

**Enables**:
- K-gent Phase 3: Soul functor composition
- Flux composition: `Flux.lift(StateMonad.lift(agent))`
- Effect stacks: Declarative `compose_functors(F, G)` for any pair

---

## Sequencing (Completed)

```
Phase 1 (Symmetric Lifting) ✓
    │
    ├──► Phase 2 (Observer Unification) ✓
    │
    └──► Phase 3 (State as Monad) ✓
              │
              └──► Phase 4 (Registry Activation) ✓
                        │
                        └──► Phase 5 (Composition Matrix) ✓
```

Phases 2 and 3 can run in parallel after Phase 1.

---

## Non-Goals

- **New agent types**: Consolidate existing, don't add more
- **AGENTESE expansion**: That's a separate plan (self.soul.* etc.)
- **Performance optimization**: Correctness first
- **Breaking changes to public API**: Deprecate, don't remove

---

## Risks

| Risk | Mitigation |
|------|------------|
| Unlift breaks existing code | Keep old patterns, add new ones |
| Observer unification too ambitious | Start with O-gent only, extend later |
| StateMonad too complex | Start minimal, grow |
| Registry composition edge cases | Document invalid combinations |

---

## Resources

- **Bounty Board**: 7 HIGH priority items from this plan
- **Exploration Doc**: `docs/exploration-categorical-consolidation.md`
- **Spec Reference**: `spec/c-gents/functors.md`, `spec/principles.md`

---

## Alignment

| Principle | How This Honors It |
|-----------|-------------------|
| **Composable** | Symmetric lift/unlift enables composition |
| **Generative** | Functor laws generate correct implementations |
| **Tasteful** | Consolidate, don't sprawl |
| **Heterarchical** | No fixed functor hierarchy |

---

*"The noun is a lie. There is only the rate of change."*
