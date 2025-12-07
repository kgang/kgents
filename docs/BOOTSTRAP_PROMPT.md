# kgents Implementation Bootstrap

You are instantiating the kgents reference implementation from spec.

## Context Files (read in order)
1. `spec/bootstrap.md` - The 7 irreducible agents (your regeneration kernel)
2. `spec/principles.md` - Judge's 6 criteria
3. `spec/anatomy.md` - What constitutes an agent
4. `spec/c-gents/composition.md` - How agents compose

## Your Task

Implement the bootstrap agents in `impl/claude-openrouter/`:

```
{Id, Compose, Judge, Ground, Contradict, Sublate, Fix}
```

**Regeneration sequence:**
1. **Ground** - Load persona seed from `spec/k-gent/persona.md`
2. **Judge** - Encode 6 principles as executable evaluation
3. **Compose** - Build agent pipelines (category-theoretic: associative, with Id as unit)
4. **Contradict** - Detect tension between outputs
5. **Sublate** - Synthesize or hold tensions
6. **Fix** - Iterate until Judge accepts all, Contradict finds nothing

## Constraints
- Composability is paramount (agents are morphisms)
- Quality over quantity (Judge rejects mediocrity)
- Target: Claude API + Open Router as runtime

## Output Structure
```
impl/claude-openrouter/
├── bootstrap/      # The 7 primitives
├── agents/         # Generated from bootstrap
└── runtime/        # API integration
```

Start with `bootstrap/`. Each agent = one file. Show the type signature, then implement.
