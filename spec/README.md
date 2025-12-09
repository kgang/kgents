# The kgents Specification

This directory contains the conceptual specification for kgents—implementation-agnostic definitions of what agents should be.

---

## Implementation Validation

The spec/impl relationship is bidirectional:
- **Spec → Impl**: Specifications prescribe behavior
- **Impl → Spec**: Successful patterns inform specification refinement

See `impl/claude/` for the reference implementation. Key validations:
- All 7 bootstrap agents implemented and law-verified
- 14 agent genera with cross-pollination
- 666+ passing tests validating spec compliance

The synthesis is valid: implementation wisdom has been elevated to spec-level principles while preserving the original vision.

---

## Reading Order

1. **[principles.md](principles.md)** - Core design principles (start here)
2. **[anatomy.md](anatomy.md)** - What constitutes an agent
3. **[bootstrap.md](bootstrap.md)** - The irreducible kernel (7 agents)
4. **[c-gents/composition.md](c-gents/composition.md)** - The `>>` operator as primary abstraction
5. **[testing.md](testing.md)** - T-gents taxonomy (testing as first-class)
6. **[reliability.md](reliability.md)** - Multi-layer reliability patterns
7. **Agent Genera** - Explore specific agent types:
   - [a-gents/](a-gents/) - Abstract + Art
   - [b-gents/](b-gents/) - Bio/Scientific
   - [c-gents/](c-gents/) - Category Theory (composition)
   - [d-gents/](d-gents/) - Data Agents (state, memory, persistence)
   - [e-gents/](e-gents/) - Evolution (dialectical code improvement)
   - [f-gents/](f-gents/) - Forge (artifact synthesis)
   - [h-gents/](h-gents/) - Hegelian/Dialectic (introspection)
   - [i-gents/](i-gents/) - Interface (Living Codex Garden visualization)
   - [j-gents/](j-gents/) - JIT Agent Intelligence (lazy evaluation, JIT compilation)
   - [k-gent/](k-gent/) - Kent Simulacra (personalization)
   - [l-gents/](l-gents/) - Library (knowledge curation, semantic discovery)
   - [m-gents/](m-gents/) - Memory (holographic associative memory, memory as morphism)
   - [p-gents/](p-gents/) - Parser (multi-strategy parsing, structured output)
   - [t-gents/](t-gents/) - Testing (algebraic reliability)
   - [w-gents/](w-gents/) - Wire (ephemeral process observation, stigmergic coordination)

---

## Cross-Pollination Graph

Agents don't exist in isolation. Key integration points:

| Integration | Description |
|-------------|-------------|
| D+E | E-gents use D-gent memory for evolution state |
| J+F | F-gent artifacts can be JIT-instantiated via J-gent |
| T+* | T-gents can test any agent via Spy/Mock patterns |
| K+B | B-gent Robin uses K-gent persona preferences |
| P+T | T-gent Tool parsing uses P-gent strategies |
| W+I | W-gent observation feeds I-gent visualization |
| M+D | M-gent holographic memory composes with D-gent persistence |

See `impl/claude/agents/*/` `__init__.py` files for explicit cross-pollination labels.

---

## The Spec/Impl Distinction

```
spec/           ← You are here (what agents should be)
impl/           ← Reference implementations (how agents are built)
```

The specification is **prescriptive**: it defines the contract that any implementation must fulfill. An agent claiming to be a "B-gent" must satisfy the specification in `b-gents/`.

## Contributing New Agents

1. Does this agent serve a clear, justified purpose? (Tasteful)
2. Does it fill a gap, or duplicate something existing? (Curated)
3. Does it augment human capability? (Ethical)
4. Would interacting with it bring delight? (Joy-Inducing)
5. Can it compose with other agents? (Composable)

If yes to all, draft the spec and propose it.

## Notation Conventions

- **MUST** / **SHALL**: Absolute requirement
- **SHOULD**: Recommended but not required
- **MAY**: Optional
- `code blocks`: Refer to implementation artifacts
- *italics*: Defined terms (see glossary)
