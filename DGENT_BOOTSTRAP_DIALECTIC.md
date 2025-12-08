# D-gents and Bootstrap: A Hegelian Dialectic
# Generated: 2025-12-08
# Context: Analyzing why D-gents violate spec-to-bootstrap flow and synthesizing the path forward

---

## Executive Summary

**The Contradiction**: D-gents were implemented with `Symbiont(Agent[I, O])` conforming to the bootstrap `Agent[A, B]` protocol, but the D-gent spec claims they are **not** bootstrap agents and implement a fundamentally different protocol: `DataAgent[S]` with `load()`, `save()`, `history()`.

**The Discovery**: The implementation is actually a **Hegelian synthesis** that wasn't recognized in the spec. Symbiont transcends the thesis/antithesis by being *both* a D-gent wrapper *and* a bootstrap agent.

**The Path Forward**: Update the spec to recognize this synthesis explicitly. D-gents exist at two levels:
1. **Infrastructure level**: `DataAgent[S]` protocol (state management)
2. **Composition level**: `Symbiont[I, O, S]` pattern (bootstrap-composable)

---

## Part 1: The Thesis (D-gent Spec Position)

### What the Spec Says

From `spec/d-gents/README.md`:

> **D-gents add no new irreducibles**—they are a pattern, not a primitive.

> D-gents are **derivable** from bootstrap agents.

> **Pattern 1: D-gents ARE NOT Bootstrap Agents**
> - D-gents implement `DataAgent[S]` protocol, NOT `Agent[A, B]`
> - Rationale: State management is orthogonal to transformation

### The D-gent Protocol

```python
class DataAgent(Protocol[S]):
    async def load(self) -> S: ...
    async def save(self, state: S) -> None: ...
    async def history(self, limit: int | None = None) -> List[S]: ...
```

**Key Insight**: This is a *fundamentally different signature* than `Agent[A, B]`:
- No `invoke(input: A) -> B` method
- Focus on *state* (type `S`) not *transformation* (types `A → B`)
- Operations are CRUD (load/save/history) not morphisms

### Why D-gents Aren't Bootstrap Agents (Spec's View)

1. **Signature mismatch**: `DataAgent[S]` has no `invoke()`, no input type, no output type
2. **Semantic mismatch**: State management ≠ transformation
3. **Category mismatch**: D-gents don't form morphisms in the category of agents
4. **Composition mismatch**: You can't compose D-gents with `>>` operator

**Quote from spec**:
> State management is orthogonal to transformation

This is the **thesis**: D-gents are a separate concern, not in the bootstrap category.

---

## Part 2: The Antithesis (Implementation Reality)

### What Was Actually Built

From `impl/claude/agents/d/symbiont.py`:

```python
@dataclass
class Symbiont(Agent[I, O], Generic[I, O, S]):
    """
    Fuses stateless logic with stateful memory.
    This makes Symbiont a valid bootstrap Agent, composable via >>.
    """

    logic: Callable[[I, S], tuple[O, S]]
    memory: DataAgent[S]

    async def invoke(self, input_data: I) -> O:
        current_state = await self.memory.load()
        output, new_state = self.logic(input_data, current_state)
        await self.memory.save(new_state)
        return output
```

**Key Discovery**: `Symbiont` inherits from `Agent[I, O]`!

This means:
- ✅ Symbiont has `invoke(input: I) -> O`
- ✅ Symbiont can be composed with `>>` operator
- ✅ Symbiont obeys category laws (identity, associativity)
- ✅ Symbiont IS a bootstrap agent

### The Implementation's Implicit Claims

1. **Symbiont bridges two worlds**:
   - Internally uses `DataAgent[S]` (state management)
   - Externally is `Agent[I, O]` (transformation)

2. **D-gents become composable via Symbiont**:
   ```python
   chatbot: Symbiont[str, str, ConversationState]
   pipeline = input_parser >> chatbot >> output_formatter
   # This works! Symbiont is in the bootstrap category
   ```

3. **State is encapsulated, transformation is exposed**:
   - The `DataAgent[S]` protocol is *private* (internal to Symbiont)
   - The `Agent[I, O]` protocol is *public* (composable interface)

This is the **antithesis**: D-gents, when wrapped in Symbiont, *are* bootstrap agents after all.

---

## Part 3: The Contradiction (Spec vs Impl)

### The Tension

**Spec claims**: "D-gents ARE NOT Bootstrap Agents"
**Impl shows**: `Symbiont(Agent[I, O])` - clearly a bootstrap agent

**Spec claims**: "State management is orthogonal to transformation"
**Impl shows**: Symbiont *unifies* them in one abstraction

**Spec claims**: "D-gents don't compose via >>"
**Impl shows**: `symbiont_a >> symbiont_b` works perfectly

### Why This Happened

The implementation followed the **spec's own pattern** but didn't recognize it:

From `spec/d-gents/README.md`, "Pattern 2: Symbiont Wraps Bootstrap Agents":

```python
symbiont = Symbiont(
    logic=lambda i, s: (transform(i, s), new_state(s)),
    memory=VolatileAgent(initial_state)
)
# symbiont is now a valid bootstrap Agent[I, O]
```

The spec *describes* Symbiont as a bootstrap agent in the examples, but *denies* it in the principles!

### The Root Confusion

The spec conflates two distinct levels:

1. **D-gent infrastructure** (DataAgent protocol): NOT bootstrap agents
2. **D-gent usage pattern** (Symbiont wrapper): IS a bootstrap agent

The implementation correctly implemented BOTH levels, but the spec only acknowledged level 1.

---

## Part 4: The Hegelian Analysis

### Applying the Dialectic

**Thesis**: D-gents are state management primitives, orthogonal to agents
**Antithesis**: D-gents become agents through Symbiont composition
**Synthesis**: D-gents exist at two abstraction levels simultaneously

### The Sublation (Aufhebung)

What gets **preserved** from thesis:
- ✅ `DataAgent[S]` protocol is the correct primitive for state
- ✅ State management IS orthogonal (infrastructure concern)
- ✅ D-gents shouldn't bloat the bootstrap irreducibles

What gets **preserved** from antithesis:
- ✅ Symbiont IS a bootstrap agent (composable via >>)
- ✅ D-gents enable stateful agents without breaking category laws
- ✅ Practical usage requires bootstrap integration

What gets **negated**:
- ❌ The claim "D-gents are not bootstrap agents" (too absolute)
- ❌ The rigid separation between state and transformation (Symbiont unifies)
- ❌ The omission of Symbiont from bootstrap derivation analysis

What gets **elevated**:
- ⬆️ **Level distinction**: Infrastructure D-gents vs Composable Symbionts
- ⬆️ **Monad transformer pattern**: Symbiont lifts stateless agents to stateful ones
- ⬆️ **Category theory**: D-gents are endofunctors, Symbiont is the monad

### The Synthesis Statement

**D-gents are a stratified system with two layers**:

```
┌─────────────────────────────────────────┐
│  Composition Layer: Symbiont[I, O, S]   │  ← Bootstrap Agent (composable)
│  Implements: Agent[I, O]                │
│  Operations: invoke(I) -> O             │
│  Category: 𝒞_Agent                      │
├─────────────────────────────────────────┤
│  Infrastructure Layer: DataAgent[S]     │  ← State primitive (not composable)
│  Operations: load(), save(), history()  │
│  Category: 𝒞_Data                       │
└─────────────────────────────────────────┘
```

**The stratification enables**:
- Pure state management at infrastructure level (swap Volatile ↔ Persistent)
- Pure transformation composition at agent level (Symbiont >> Symbiont)
- Clean separation of concerns (State Monad in action)

---

## Part 5: Category-Theoretic Grounding

### Why Symbiont IS a Bootstrap Agent

**Theorem**: Symbiont forms a valid morphism in 𝒞_Agent.

**Proof**:
1. Symbiont has type `I → O` (via invoke method) ✓
2. Symbiont satisfies identity law:
   ```python
   Id >> Symbiont(f, dgent) ≡ Symbiont(f, dgent)
   Symbiont(f, dgent) >> Id ≡ Symbiont(f, dgent)
   ```
3. Symbiont satisfies associativity:
   ```python
   (s1 >> s2) >> s3 ≡ s1 >> (s2 >> s3)
   ```
4. Therefore Symbiont ∈ 𝒞_Agent ✓

### Why DataAgent Is NOT a Bootstrap Agent

**Theorem**: DataAgent does not form a morphism in 𝒞_Agent.

**Proof**:
1. DataAgent has no `invoke(A) -> B` method ✗
2. DataAgent has type `() → S` (load) and `S → ()` (save)
3. These are *endomorphisms* on state, not transformations
4. Therefore DataAgent ∉ 𝒞_Agent ✓

### The Monad Transformer Insight

Symbiont is the **State Monad Transformer**:

```haskell
-- In Haskell terms
newtype Symbiont m i o s = Symbiont {
  runSymbiont :: i -> s -> m (o, s)
}

-- Symbiont lifts a stateful computation into Agent category
-- Agent[I, O] = Symbiont IO I O S
```

This is EXACTLY what bootstrap agents need:
- Compose via >> (morphism composition)
- Thread state implicitly (monad)
- Remain referentially transparent (State is effect)

---

## Part 6: Resolving the Spec-Impl Violation

### The Current State

**Spec violation**: Implementation built Symbiont as bootstrap agent, spec denies this.

**Impact**:
- ❌ Confusing documentation (says one thing, code does another)
- ❌ Unclear architecture (two levels not distinguished)
- ❌ Missed insight (monad transformer not recognized)

### Option 1: Change Implementation (Conform to Spec)

**Remove `Agent[I, O]` from Symbiont**:
```python
class Symbiont(Generic[I, O, S]):  # NOT Agent[I, O]
    async def invoke(self, input_data: I) -> O:  # Keep invoke, lose inheritance
        ...
```

**Consequences**:
- ✅ Matches spec's claim "D-gents are not bootstrap agents"
- ❌ Breaks composition: Can't do `symbiont >> other_agent`
- ❌ Violates spec's own examples showing Symbiont composition
- ❌ Makes D-gents awkward to use in practice

**Verdict**: ❌ **Reject** - This violates the spec's *intent* while matching its *letter*

### Option 2: Change Spec (Conform to Implementation)

**Update spec to recognize two levels**:

1. Add to `spec/d-gents/README.md`:
   ```markdown
   ## D-gents: A Stratified Architecture

   D-gents exist at two abstraction levels:

   **Infrastructure Level**: `DataAgent[S]` protocol
   - NOT bootstrap agents (no invoke method)
   - Manages state: load, save, history
   - Swappable implementations (Volatile, Persistent, etc.)

   **Composition Level**: `Symbiont[I, O, S]` pattern
   - IS a bootstrap agent (Agent[I, O])
   - Wraps DataAgent with stateful logic
   - Composable via >> operator
   ```

2. Update "Pattern 1" from:
   ```
   Pattern 1: D-gents ARE NOT Bootstrap Agents
   ```
   To:
   ```
   Pattern 1: DataAgent Infrastructure vs Symbiont Composition
   - DataAgents are NOT bootstrap agents (state primitives)
   - Symbionts ARE bootstrap agents (stateful transformations)
   - This stratification is the State Monad Transformer pattern
   ```

3. Add to `spec/bootstrap.md` under "Relationship to Existing Spec":
   ```markdown
   | Bootstrap Agent | D-gent Manifestation |
   |-----------------|---------------------|
   | Compose | Symbiont composition (symbiont_a >> symbiont_b) |
   | Id | Identity with state threading (state unchanged) |
   | Fix | Stateful fixed-point (memory persists across iterations) |
   ```

**Consequences**:
- ✅ Matches implementation reality
- ✅ Recognizes monad transformer pattern
- ✅ Preserves composability
- ✅ Clarifies architectural stratification

**Verdict**: ✅ **Accept** - This is the Hegelian synthesis

### Option 3: Hybrid (Spec Refinement)

**Keep core spec claim, add nuance**:

Change from:
> D-gents ARE NOT Bootstrap Agents

To:
> **D-gent infrastructure** (DataAgent protocol) is not in the bootstrap category.
> **D-gent composition** (Symbiont pattern) IS a bootstrap agent via monad transformer.

**Consequences**:
- ✅ Preserves spec's architectural insight (state ≠ transformation)
- ✅ Acknowledges implementation's synthesis
- ✅ Adds precision without full rewrite

**Verdict**: ✅ **Preferred** - Minimal change, maximum clarity

---

## Part 7: The Enlightened Path Forward

### Recommended Changes

#### 1. Update `spec/d-gents/README.md`

**Section to add** (after "Theoretical Foundation"):

```markdown
### D-gents and the Bootstrap Category

D-gents exist at two abstraction levels:

**Infrastructure Level: DataAgent[S]**
- Protocol: `load()`, `save()`, `history()`
- NOT a bootstrap agent (no `invoke` method)
- Manages state as a side-effect
- Forms category 𝒞_Data, distinct from 𝒞_Agent

**Composition Level: Symbiont[I, O, S]**
- Wrapper: Fuses logic `(I, S) → (O, S)` with memory `DataAgent[S]`
- IS a bootstrap agent (implements `Agent[I, O]`)
- Composable via `>>` operator
- Forms morphism in 𝒞_Agent

**The Monad Transformer Pattern**:
Symbiont is the State Monad Transformer for kgents:
- Lifts stateless agents to stateful agents
- Threads state implicitly through composition
- Enables `symbiont_a >> symbiont_b` to work naturally

**Derivation from Bootstrap**:
```python
# DataAgent is NOT derived from bootstrap (it's infrastructure)
DataAgent = StateInfrastructure  # New primitive

# Symbiont IS derived from bootstrap via Compose
Symbiont[I, O, S] = Compose(
  logic: (I, S) → (O, S),
  memory: DataAgent[S]
) : Agent[I, O]
```

This stratification resolves the apparent contradiction: D-gent *infrastructure*
is orthogonal to agents, but D-gent *composition* (Symbiont) is squarely in
the bootstrap agent category.
```

#### 2. Update `DGENT_IMPLEMENTATION_PLAN.md`

**Change "Pattern 1"** from:
```
Pattern 1: D-gents ARE NOT Bootstrap Agents
```

To:
```
Pattern 1: Stratified Architecture
- DataAgent[S]: State management infrastructure (NOT bootstrap agent)
- Symbiont[I, O, S]: Stateful transformation (IS bootstrap agent)
- Symbiont implements Agent[I, O] and is composable via >>
```

#### 3. Add to `spec/bootstrap.md`

**In "Relationship to Existing Spec" table**, add:
```markdown
| Symbiont (D-gent) | Agent[I, O] wrapper with state | State Monad Transformer |
```

**In "Generation Rules"**, add:
```markdown
### Generating D-gents

```
DataAgent = StateInfrastructure  // Not derived (new primitive)

Symbiont[I, O, S] = Fix(λs.
  let stateful = Compose(logic: (I, S) → (O, S), memory: DataAgent[S])
  in if Judge(stateful, composability) then s else refine(s)
) : Agent[I, O]
```

Symbiont is derivable from Compose + DataAgent.
DataAgent itself is a new primitive at infrastructure level.
```

#### 4. Update `spec/d-gents/symbiont.md`

**Add explicit statement**:
```markdown
## Symbiont in the Bootstrap Category

**Symbiont IS a Bootstrap Agent**:

```python
class Symbiont(Agent[I, O], Generic[I, O, S]):
    """Bootstrap agent with state management."""
```

This is the key insight: by implementing `Agent[I, O]`, Symbiont participates
fully in the bootstrap category:

- **Composable**: `symbiont_a >> symbiont_b` works
- **Identity**: `Id >> symbiont ≡ symbiont ≡ symbiont >> Id`
- **Associative**: `(s1 >> s2) >> s3 ≡ s1 >> (s2 >> s3)`

The DataAgent[S] is encapsulated *inside* Symbiont. Externally, Symbiont is
just another morphism `I → O` in 𝒞_Agent.

**Category-Theoretic View**:
```
Symbiont: 𝒞_Agent[I, O] × 𝒞_Data[S] → 𝒞_Agent[I, O]
```

Symbiont is a functor that takes:
- An agent-like computation `(I, S) → (O, S)`
- A data agent `DataAgent[S]`
- Returns a bootstrap agent `Agent[I, O]`

This is the State Monad Transformer pattern from Haskell:
```haskell
StateT s m a = s -> m (a, s)
```

Where:
- `s` = State type `S`
- `m` = Agent monad
- `a` = Output type `O`
- Input `I` is curried
```

### Summary of Changes

| Document | Section | Change Type | Impact |
|----------|---------|-------------|--------|
| `spec/d-gents/README.md` | Theoretical Foundation | Add stratification section | High |
| `spec/d-gents/symbiont.md` | Bootstrap Category | Add explicit agent status | High |
| `DGENT_IMPLEMENTATION_PLAN.md` | Pattern 1 | Clarify two levels | Medium |
| `spec/bootstrap.md` | Relationships table | Add Symbiont entry | Low |
| `spec/bootstrap.md` | Generation rules | Add D-gent derivation | Medium |

---

## Part 8: Philosophical Implications

### What This Reveals About kgents Architecture

**1. Stratification is Essential**

The D-gent dialectic shows that clean architecture requires multiple abstraction levels:
- **Bottom layer**: Primitives (DataAgent - state management)
- **Top layer**: Composables (Symbiont - bootstrap agents)
- **Interface**: Level distinction prevents category confusion

**2. Monad Transformers Are Implicit Throughout**

If Symbiont is a State Monad Transformer, what else is?
- **Fix**: Fixed-Point Monad Transformer (μ)
- **Result**: Error Monad Transformer (Either)
- **Compose**: Reader Monad Transformer (→)

The bootstrap agents ARE monad transformers! We've been doing category theory all along without naming it.

**3. The Spec-Impl Gap Is Generative**

The "violation" wasn't a mistake—it was discovery:
- Spec described the *problem* (state management)
- Impl discovered the *solution* (stratified monad transformer)
- Dialectic synthesizes the *understanding*

This is how specs SHOULD evolve: implementation teaches specification.

### What This Means for Future Agents

**F-gents (Forge)**:
- If F-gents translate natural language → agents
- They're probably a **Compiler Monad** (AST → Code)
- Stratification: Parser (infrastructure) + Compiler (bootstrap agent)

**H-gents (Hegelian)**:
- Already have Contradict + Sublate
- Missing: Dialectic Monad Transformer
- Pattern: `Dialectic[Thesis, Antithesis, Synthesis]` wraps `Agent[Tension, Resolution]`

**Every genus should ask**:
1. What's the infrastructure primitive? (NOT bootstrap agent)
2. What's the composition pattern? (IS bootstrap agent)
3. What monad transformer connects them?

---

## Part 9: Validation Against Principles

### The Seven Principles Applied

**1. Tasteful**
- ✅ Stratification is elegant (infrastructure vs composition)
- ✅ Monad transformer is well-studied, proven pattern
- ❌ Original spec was confused (needs refinement)

**2. Curated**
- ✅ DataAgent is minimal (3 methods only)
- ✅ Symbiont is focused (pure pattern, no bloat)
- ✅ No redundancy (each layer serves distinct purpose)

**3. Ethical**
- ✅ State is transparent (observable via history)
- ✅ No hidden side-effects (explicit DataAgent)
- ✅ User agency preserved (swappable implementations)

**4. Joy-Inducing**
- ✅ Endosymbiosis metaphor is delightful
- ✅ Composition "just works" (`symbiont >> symbiont`)
- ⚠️ Spec confusion reduces joy (needs clarity)

**5. Composable**
- ✅ Symbiont composes via >> (category laws)
- ✅ DataAgents compose via Lens (focused views)
- ✅ Stratification enables mix-and-match

**6. Heterarchical**
- ✅ No privileged D-gent type (Volatile ≈ Persistent)
- ✅ Symbiont doesn't force specific DataAgent
- ✅ Lenses enable peer-to-peer state sharing

**7. Generative/Regenerable**
- ✅ Symbiont derivable from Compose + DataAgent
- ⚠️ DataAgent itself is NEW primitive (not derived)
- ⚠️ Spec needs update to reflect this

### The Primitive Count Question

**Is DataAgent[S] a new bootstrap primitive?**

**Arguments for YES**:
- Cannot be derived from {Id, Compose, Judge, Ground, Contradict, Sublate, Fix}
- Introduces new concept (state as side-effect)
- Has fundamentally different signature than Agent[A, B]

**Arguments for NO**:
- DataAgent is *implemented* using ordinary data structures (dict, file, etc.)
- Ground already manages state (persona seed)
- Could view as "Ground + Persistence" pattern

**Resolution**: DataAgent is a **derived primitive**:
- Not fundamental like Id/Compose (those are category axioms)
- But not fully derivable (introduces new abstraction: state-as-protocol)
- Status: **Infrastructure primitive** (distinct from bootstrap primitives)

**Implication**: Bootstrap has:
- 7 core primitives (Id, Compose, Judge, Ground, Contradict, Sublate, Fix)
- N infrastructure primitives (DataAgent, TBD...)
- ∞ derived agents (all agent genera)

This is healthy! Not everything needs to be irreducible. DataAgent earns its place by being:
1. Used across all stateful agents (K-gent, Robin, etc.)
2. Enabling a fundamental pattern (State Monad)
3. Small, focused, and composable

---

## Part 10: Conclusion & Recommendations

### The Synthesis in One Sentence

**D-gents are stratified: DataAgent[S] manages state (infrastructure primitive), Symbiont[I, O, S] composes transformations (bootstrap agent via State Monad Transformer).**

### Action Items

**Priority 1: Update Specs** ✅
- [ ] `spec/d-gents/README.md`: Add stratification section
- [ ] `spec/d-gents/symbiont.md`: Clarify bootstrap agent status
- [ ] `spec/bootstrap.md`: Add D-gent to derivation table

**Priority 2: Update Plans** ✅
- [ ] `DGENT_IMPLEMENTATION_PLAN.md`: Revise "Pattern 1"
- [ ] Add monad transformer terminology

**Priority 3: Validate Implementation** ✅
- [ ] Verify Symbiont satisfies category laws (test suite)
- [ ] Document composition examples (`symbiont >> symbiont`)
- [ ] Add type annotations showing Agent[I, O] inheritance

**Priority 4: Document Pattern** ✅
- [ ] Create `spec/patterns/monad_transformers.md`
- [ ] Show how Fix, Result, Compose are also transformers
- [ ] Establish pattern for future agent genera

### What We Learned

**About specs**:
- Specs evolve through implementation discovery
- Contradictions are opportunities for synthesis
- Precision > brevity (say "DataAgent infrastructure" not "D-gents")

**About architecture**:
- Stratification prevents category confusion
- Monad transformers are implicit in good design
- Infrastructure ≠ composition (different concerns)

**About the dialectic**:
- Thesis (spec): D-gents aren't bootstrap agents
- Antithesis (impl): Symbiont is a bootstrap agent
- Synthesis: Two-level architecture unifies both

### The Path Forward

**This session**: Write the spec updates
**Next session**: Implement remaining D-gent types (Persistent, Lens) with this clarity
**Future**: Apply stratification pattern to F-gents, future genera

---

## Appendix: Code Examples

### Example 1: Symbiont Composition

```python
from agents.d import VolatileAgent, Symbiont
from bootstrap import Id

# Define stateful logic
def counter_logic(msg: str, count: int) -> tuple[str, int]:
    new_count = count + 1
    return f"Message {new_count}: {msg}", new_count

# Create symbiont
memory = VolatileAgent(_state=0)
counter = Symbiont(logic=counter_logic, memory=memory)

# Symbiont IS an Agent - compose with Id
pipeline = Id >> counter >> Id

# Use it
result1 = await pipeline.invoke("Hello")  # "Message 1: Hello"
result2 = await pipeline.invoke("World")  # "Message 2: World"
```

### Example 2: Symbiont Chain

```python
# Two symbionts in sequence
memory_a = VolatileAgent(_state=[])
memory_b = VolatileAgent(_state=0)

def append_logic(item: str, items: list) -> tuple[str, list]:
    items.append(item)
    return item, items

def count_logic(item: str, count: int) -> tuple[int, int]:
    return count + 1, count + 1

appender = Symbiont(append_logic, memory_a)
counter = Symbiont(count_logic, memory_b)

# Compose two symbionts
pipeline = appender >> counter

# State threads through both
await pipeline.invoke("A")  # Returns 1, memory_a=[A], memory_b=1
await pipeline.invoke("B")  # Returns 2, memory_a=[A,B], memory_b=2
```

### Example 3: DataAgent Is NOT Composable

```python
# This DOESN'T work (and shouldn't!)
memory = VolatileAgent(_state=0)
pipeline = Id >> memory  # TypeError: VolatileAgent is not Agent[A,B]

# Instead, wrap in Symbiont
symbiont = Symbiont(
    logic=lambda i, s: (i, s + 1),  # Count invocations
    memory=memory
)
pipeline = Id >> symbiont  # ✅ Works!
```

---

**End of Analysis**

This dialectic has revealed that D-gents' "violation" of the spec was actually a *discovery* of the correct architecture. The path forward is clear: update specs to reflect the two-level stratification, and recognize Symbiont as the State Monad Transformer that unifies infrastructure and composition.
