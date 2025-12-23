# AD-017: Typed AGENTESE

**Date**: 2025-12-21

> AGENTESE paths SHALL have categorical types. Composition errors become type errors.

---

## Context

AGENTESE currently relies on runtime validation. Path composition (`path_a >> path_b`) can fail at invocation time if types don't match. This is a symptom of insufficient formalization—the categorical type system should catch composition errors at registration time, not runtime.

## Heritage Connection

The Polynomial Functors paper (§10) provides the mathematical foundation. AGENTESE paths are typed morphisms in the category of polynomial functors. Path composition is polynomial substitution. Invalid wiring diagrams are type errors.

## Decision

AGENTESE paths are typed morphisms:

```python
# Current (informal, runtime validation)
world.tools.bash.invoke(umwelt, command="ls")

# Typed (categorical, static validation)
invoke : (observer : Umwelt) → BashRequest → Witness[BashResult]
# Where Witness[A] is a type that proves the operation happened
```

## Type Rules

1. **Path composition requires type compatibility**: `path_a >> path_b` valid iff output type of `a` matches input type of `b`
2. **Aspect invocation has typed effects**: Effects declared in `@node` decorator are part of the type signature
3. **Observer determines valid inputs**: Mode-dependent typing via polynomial positions (AD-002)

## Connection to Polynomial Functors

| Poly Concept | AGENTESE Typing |
|--------------|-----------------|
| Path type | Polynomial functor signature |
| Composition | Polynomial substitution |
| Type error | Invalid wiring diagram |
| Positions | Observer modes |
| Directions | Valid inputs per mode |

## First Step

Define `AGENTESEType` as a Protocol with `compose` method. Add type annotations to `@node` decorator:

```python
@node(
    path="world.tools.bash",
    input_type=BashRequest,
    output_type=Witness[BashResult],
    effects=["filesystem", "subprocess"],
)
async def bash_invoke(observer: Umwelt, request: BashRequest) -> Witness[BashResult]:
    ...
```

## Consequences

1. **Composition errors surface at import time**, not runtime—malformed pipelines fail fast
2. **Type annotations serve as documentation**—the signature IS the spec
3. **IDE autocomplete becomes meaningful**—editors know valid compositions
4. **Prepares for proof-generating ASHC**—composition validity is provable (see `spec/protocols/proof-generation.md`)
5. **Aligns with heritage**—we're implementing what Spivak & Niu formalized

## Anti-patterns

- Untyped paths that bypass the type system (defeats the purpose)
- Runtime type checks that duplicate static analysis (redundant, slow)
- Overly complex types that obscure intent (types should clarify, not confuse)
- Types without heritage justification (category theory is the ground, not Java generics)

## Implementation

See `docs/skills/agentese-node-registration.md` (to be updated)

*Zen Principle: The type that generates composition errors at import time prevents runtime failures.*
