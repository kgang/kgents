# kgents Implementation Bootstrap

You are instantiating kgents implementations from spec. You are an LLM doing mechanical translation—the judgment has already been made in the spec.

## The LLM/Human Boundary

```
Spec + Ground = Human territory (irreducible, already provided)
Impl = Your territory (mechanical translation from spec)
```

You cannot create Ground from nothing. You cannot replace human judgment. You CAN faithfully translate spec to code.

## Context Files (read in order)

1. `spec/bootstrap.md` - The 7 irreducible agents (your regeneration kernel)
2. `spec/principles.md` - Judge's 7 criteria (the value function)
3. `spec/anatomy.md` - What constitutes an agent
4. `spec/c-gents/composition.md` - How agents compose

## The 7 Bootstrap Agents

```
{Id, Compose, Judge, Ground, Contradict, Sublate, Fix}
```

| Agent | Type | Purpose |
|-------|------|---------|
| **Id** | `A → A` | Composition unit (λx.x) |
| **Compose** | `(Agent, Agent) → Agent` | Build pipelines |
| **Judge** | `(Agent, Principles) → Verdict` | Value function (7 principles) |
| **Ground** | `Void → Facts` | Empirical seed (persona + world) |
| **Contradict** | `(A, B) → Tension \| None` | Detect conflicts |
| **Sublate** | `Tension → Synthesis \| Hold` | Resolve or hold |
| **Fix** | `(A → A) → A` | Fixed-point iteration |

## Regeneration Sequence

1. **Ground** - Load persona from `spec/k-gent/persona.md`
2. **Judge** - Encode 7 principles as executable evaluation
3. **Compose** - Build pipelines (associative, Id as unit)
4. **Contradict** - Surface tensions before they become errors
5. **Sublate** - Synthesize or consciously hold
6. **Fix** - Iterate until stable (Judge accepts, Contradict finds nothing)

## Implementation Targets

### Target 1: `impl/claude-openrouter/`
Reference implementation. Bootstrap agents as Python, LLM runtime via Claude + OpenRouter.

```
impl/claude-openrouter/
├── bootstrap/      # The 7 primitives
├── agents/{a,b,c,h,k}/  # 5 genera
└── runtime/        # LLM-backed agents (4 auth methods)
```

### Target 2: `impl/zen-agents/`
Production TUI. Demonstrates bootstrap agents in a real application.

```
impl/zen-agents/
├── zen_agents/     # Core + ui/
├── pipelines/      # NewSessionPipeline, SessionTickPipeline
└── tests/          # pytest suite
```

## Applied Idioms

When implementing, apply these patterns from `spec/bootstrap.md`:

### 1. Polling is Fix
Any iteration pattern is a fixed-point search.
```python
result = await fix(transform=poll_once, initial=state, equality_check=is_stable)
```
Anti-pattern: `while True` with inline break conditions.

### 2. Conflict is Data
Detect tensions explicitly before they become runtime errors.
```python
conflicts = contradict(config, ground_state)
if conflicts:
    resolution = sublate(conflicts[0])
```
Anti-pattern: Silent failures, swallowed exceptions.

### 3. Compose, Don't Concatenate
If a function does A then B then C, it should BE `A >> B >> C`.
```python
Pipeline = Judge(config) >> Create(config) >> Spawn(session) >> Detect(session)
```
Anti-pattern: 130-line methods mixing validation, I/O, state, errors.

## Constraints

- Composability is paramount (agents are morphisms)
- Quality over quantity (Judge rejects mediocrity)
- Each agent = one file with clear type signature
- Tests should be extensive (zen-agents has 49+)

## Verification

A successful regeneration satisfies:
```
Regenerate(Spec) ≅ Current Impl
Judge(Regenerated, Principles) = accept ∀ components
Contradict(Regenerated, Spec) = None
```

Start with `bootstrap/`. Show the type signature, then implement.
