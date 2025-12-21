# Monad Transformers in kgents

A pattern that unifies infrastructure primitives with bootstrap agent composition.

---

## Philosophy

> "Monad transformers lift computation into new contexts without changing its essence."

The **Monad Transformer Pattern** appears throughout kgents, enabling:
- Separation of infrastructure (primitives) from composition (bootstrap agents)
- Lifting pure agents into effectful contexts (state, errors, recursion)
- Composability via the bootstrap `>>` operator

This document formalizes the pattern discovered in D-gents and identifies it across all agent genera.

---

## The Pattern

### Structure

Every monad transformer in kgents follows this structure:

```
┌─────────────────────────────────────────┐
│  Composition Layer: Transformer[I, O]   │  ← Bootstrap Agent (composable)
│  Implements: Agent[I, O]                │
│  Operations: invoke(I) -> O             │
│  Category: 𝒞_Agent                      │
├─────────────────────────────────────────┤
│  Infrastructure Layer: Primitive[E]     │  ← Effect primitive (not composable as agent)
│  Operations: effect-specific methods    │
│  Category: 𝒞_Effect (distinct)          │
└─────────────────────────────────────────┘
```

**Key Properties**:
1. **Infrastructure layer** is NOT a bootstrap agent (different protocol)
2. **Composition layer** IS a bootstrap agent (implements `Agent[I, O]`)
3. **Transformer lifts** infrastructure effects into agent category
4. **Externally**, users see only `Agent[I, O]` (encapsulation)

---

## Identified Monad Transformers

### 1. Symbiont - State Monad Transformer (D-gents)

**Infrastructure**: `DataAgent[S]` protocol
- Methods: `load()`, `save()`, `history()`
- NOT a bootstrap agent (no `invoke` method)
- Category: $\mathcal{C}_{Data}$

**Composition**: `Symbiont[I, O, S]`
- Wraps: `(I, S) → (O, S)` logic + `DataAgent[S]` memory
- IS a bootstrap agent (implements `Agent[I, O]`)
- Category: $\mathcal{C}_{Agent}$

**Monad**: State Monad
```haskell
StateT s m a = s -> m (a, s)
```

**Effect**: Threads mutable state through computation

**Example**:
```python
memory = VolatileAgent[ConversationState](initial_state)
chatbot = Symbiont(chat_logic, memory)
# chatbot is Agent[str, str], composable via >>
```

---

### 2. Result - Error Monad Transformer (Bootstrap)

**Infrastructure**: `Ok[A]` / `Err[E]` types
- Algebraic data type representing success/failure
- NOT agents themselves (just data)
- Category: Sum type in type system

**Composition**: Agents returning `Result[O, E]`
- Any `Agent[I, Result[O, E]]` can use `>>` with error handling
- Error propagation is automatic via composition
- Category: $\mathcal{C}_{Agent}$

**Monad**: Either/Result Monad
```haskell
EitherT e m a = m (Either e a)
```

**Effect**: Short-circuits on error, propagates success

**Example**:
```python
validate: Agent[Input, Result[ValidInput, ValidationError]]
process: Agent[ValidInput, Result[Output, ProcessError]]
pipeline = validate >> process  # Errors propagate automatically
```

---

### 3. Fix - Fixed-Point Monad Transformer (Bootstrap)

**Infrastructure**: Iteration state + history
- Internal loop counter, value history
- NOT exposed as agent (internal to Fix)
- Category: Recursion primitive

**Composition**: `Fix[A]` wrapping `Agent[A, A]`
- Takes self-referential agent: `A → A`
- Returns fixed point: `A` where `f(A) = A`
- IS a bootstrap agent operation
- Category: $\mathcal{C}_{Agent}$

**Monad**: Fixed-Point Monad (μ)
```haskell
Fix f = f (Fix f)
```

**Effect**: Iterates until convergence

**Example**:
```python
result = await fix(
    transform=refine_solution,
    initial=draft,
    equality_check=lambda a, b: similarity(a, b) > 0.95
)
```

---

### 4. Compose - Reader Monad Transformer (Bootstrap)

**Infrastructure**: Function composition operator
- Core category operation: `g ∘ f`
- NOT an agent itself (meta-operation)
- Category: Category axiom

**Composition**: `>>` operator on agents
- Sequential composition: `Agent[A, B] >> Agent[B, C] → Agent[A, C]`
- Category: $\mathcal{C}_{Agent}$

**Monad**: Reader Monad (environment passing)
```haskell
ReaderT r m a = r -> m a
```

**Effect**: Threads environment/context implicitly

**Example**:
```python
pipeline = parser >> classifier >> responder
# Each agent receives output of previous as input
```

---

### 5. Dialectic - Contradiction Monad Transformer (H-gents)

**Infrastructure**: Tension detection + resolution strategies
- `Contradict: (A, B) → Tension | None`
- `Sublate: Tension → Synthesis | HoldTension`
- NOT agents themselves (meta-operations)
- Category: $\mathcal{C}_{Dialectic}$

**Composition**: `DialecticAgent[Thesis, Antithesis, Synthesis]`
- Wraps contradiction detection + synthesis logic
- IS a bootstrap agent
- Category: $\mathcal{C}_{Agent}$

**Monad**: Continuation Monad (represents suspended synthesis)
```haskell
ContT r m a = (a -> m r) -> m r
```

**Effect**: Suspends computation until contradiction resolves

**Hypothesis** (to be validated):
```python
@dataclass
class DialecticAgent(Agent[Tension, Synthesis], Generic[T, A, S]):
    """
    Bootstrap agent that detects contradictions and synthesizes.

    Infrastructure: Contradict + Sublate operations
    Composition: Agent[Tension, Synthesis]
    """
    contradict: Callable[[T, A], Tension | None]
    sublate: Callable[[Tension], Synthesis | HoldTension]

    async def invoke(self, input_pair: tuple[T, A]) -> Synthesis:
        thesis, antithesis = input_pair
        tension = self.contradict(thesis, antithesis)

        if tension is None:
            return NoContradiction()

        return self.sublate(tension)
```

---

### 6. Promise - Async Monad Transformer (J-gents)

**Infrastructure**: Event loop, futures, coroutines
- Python's `asyncio` primitives
- NOT agents (runtime infrastructure)
- Category: Concurrency primitives

**Composition**: All agents are `async def invoke(...)`
- Every agent is implicitly lifted into async context
- Composable via `await` and `asyncio.gather`
- Category: $\mathcal{C}_{Agent}$

**Monad**: IO/Async Monad
```haskell
IO a = RealWorld -> (a, RealWorld)
```

**Effect**: Non-blocking I/O, concurrency

**Note**: This is ambient—all kgents agents are in the async monad.

---

## The General Pattern

### Stratification Checklist

For any agent genus, identify:

1. **What is the infrastructure primitive?**
   - What operations are NOT `Agent[A, B]`?
   - What category does it form?
   - Examples: `DataAgent[S]`, `Tension`, iteration state

2. **What is the composition wrapper?**
   - What agent type wraps the infrastructure?
   - Does it implement `Agent[I, O]`?
   - Examples: `Symbiont[I, O, S]`, `Fix[A]`

3. **What monad is being implemented?**
   - State, Error, Continuation, Fixed-Point, etc.
   - What effect does it add to pure computation?

4. **Is the infrastructure encapsulated?**
   - Can users compose the wrapper via `>>`?
   - Is the infrastructure hidden (internal implementation)?

---

## Application to Unspecified Genera

### F-gents (Forge) - Compiler Monad Transformer

**Hypothesis**: F-gents translate natural language → agents.

**Infrastructure Layer**: `Parser` + `AST`
- Parse natural language into abstract syntax tree
- NOT agents (language processing tools)
- Category: $\mathcal{C}_{Syntax}$

**Composition Layer**: `ForgeAgent[Intent, Agent]`
- Takes natural language intent
- Returns executable agent
- IS a bootstrap agent
- Category: $\mathcal{C}_{Agent}$

**Monad**: Compiler Monad (staged computation)
```haskell
Compiler ast a = ast -> Validation (Code a)
```

**Effect**: Translates high-level intent to executable code

**Pattern**:
```python
@dataclass
class ForgeAgent(Agent[str, Agent], Generic[I, O]):
    """
    Compiles natural language into agents.

    Infrastructure: Parser + CodeGen
    Composition: Agent[Intent, CompiledAgent]
    """
    parser: Callable[[str], AST]
    codegen: Callable[[AST], Agent[I, O]]

    async def invoke(self, intent: str) -> Agent[I, O]:
        ast = self.parser(intent)
        agent = self.codegen(ast)
        return agent
```

---

## Benefits of the Pattern

### 1. Separation of Concerns
- Infrastructure: Implementation details (storage, parsing, etc.)
- Composition: Agent interface (composable via `>>`)

### 2. Testability
- Test infrastructure in isolation (no agent protocol)
- Test composition with mocked infrastructure
- Test integration with real infrastructure

### 3. Composability
- All transformers expose `Agent[I, O]` interface
- Mix and match: `Symbiont >> ForgeAgent >> EvolutionAgent`
- Category laws guarantee correctness

### 4. Substitutability
- Swap infrastructure without changing composition
- Example: `VolatileAgent` ↔ `PersistentAgent` in Symbiont
- Example: Different parsers in ForgeAgent

### 5. Clarity
- Explicit about what effects are being added
- No "magic" - monad transformers are named and visible
- Easy to reason about composition chains

---

## Anti-patterns

### Anti-pattern 1: Infrastructure Leakage

```python
# BAD: Infrastructure exposed in agent interface
class LeakyAgent(Agent[I, O]):
    def invoke(self, input: I) -> O:
        ...

    # Don't expose these!
    def get_internal_state(self) -> S: ...
    def set_database_connection(self, conn): ...
```

**Fix**: Encapsulate infrastructure in composition layer.

---

### Anti-pattern 2: Missing Composition Layer

```python
# BAD: Infrastructure without bootstrap wrapper
class BareDataStore:
    def load(self): ...
    def save(self, state): ...
    # No Agent[I, O] interface - can't compose!
```

**Fix**: Provide `Symbiont` or equivalent wrapper.

---

### Anti-pattern 3: Composition Without Infrastructure

```python
# BAD: Stateful agent without DataAgent abstraction
class StatefulAgent(Agent[I, O]):
    def __init__(self):
        self.state = {}  # Hidden, un-swappable, un-testable

    def invoke(self, input: I) -> O:
        # Mutates self.state directly
        ...
```

**Fix**: Extract state management into `DataAgent`, wrap with `Symbiont`.

---

## Validation Checklist

For each monad transformer:

- [ ] Infrastructure layer has distinct protocol (not `Agent[A, B]`)
- [ ] Composition layer implements `Agent[I, O]`
- [ ] Infrastructure is encapsulated (not exposed in agent interface)
- [ ] Composition is category-lawful (identity, associativity)
- [ ] Monad operations are well-defined (return, bind)
- [ ] Effect is clearly described (what does the transformer add?)
- [ ] Tests cover both layers independently

---

## See Also

- [spec/bootstrap.md](../bootstrap.md) - Bootstrap agent foundations
- [spec/d-gents/README.md](../d-gents/README.md) - State Monad Transformer (reference implementation)
- [spec/d-gents/symbiont.md](../d-gents/symbiont.md) - Detailed Symbiont spec
- [spec/h-gents/hegel.md](../h-gents/hegel.md) - Dialectic operations
- [spec/c-gents/monads.md](../c-gents/monads.md) - Category theory foundations

---

## Future Work

1. Formalize remaining transformers (F-gents)
2. Prove category laws for each transformer
3. Implement property-based tests for monad laws
4. Document composition of multiple transformers (monad transformer stacks)
5. Explore transformer optimization (fusion, inlining)
