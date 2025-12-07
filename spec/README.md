# The kgents Specification

This directory contains the conceptual specification for kgents—implementation-agnostic definitions of what agents should be.

## Reading Order

1. **[principles.md](principles.md)** - Core design principles (start here)
2. **[anatomy.md](anatomy.md)** - What constitutes an agent
3. **Agent Genera** - Explore specific agent types:
   - [a-agents/](a-agents/) - Abstract + Art
   - [b-gents/](b-gents/) - Bio/Scientific
   - [c-gents/](c-gents/) - Category Theory
   - [k-gent/](k-gent/) - Kent Simulacra

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
