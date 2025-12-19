# AD-001: Universal Functor Mandate

**Date**: 2025-12-12

> All agent transformations SHALL derive from the Universal Functor Protocol.

---

## Context

The synergy analysis revealed an isomorphism crisis — C-gent, Flux, K-gent, O-gent, and B-gent all implement functors independently without a unifying structure.

## Decision

Every functor-like pattern in kgents derives from `UniversalFunctor`:

```python
class UniversalFunctor(Generic[F]):
    @staticmethod
    def lift(agent: Agent[A, B]) -> Agent[F[A], F[B]]: ...
```

## Consequences

- All existing functors (`MaybeAgent`, `EitherAgent`, etc.) wrapped in `UniversalFunctor` subclasses
- Law verification centralized in `FunctorRegistry.verify_all()`
- K-gent's `intercept()` becomes a functor (`SoulFunctor`) enabling uniform governance
- Halo capabilities compile to functor composition

## Anti-patterns

- Independent functor implementations without UniversalFunctor base
- Law verification scattered across modules
- Functor-like transformations that don't implement the protocol

## Implementation

See `docs/architecture/alethic-algebra-tactics.md`
