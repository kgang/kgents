# Functor Catalog: kgents Transformation Patterns

> A comprehensive survey of functors across the kgents ecosystem.

---

## What This Document Is

This catalog identifies and formalizes **functor patterns** found throughout kgents specifications. Many agent transformations follow functor laws but aren't explicitly documented as such. This document makes them explicit.

**Purpose**: Enable systematic reasoning about agent transformations across genera.

---

## Functor Quick Reference

| Functor | Signature | Genus | Status | Description |
|---------|-----------|-------|--------|-------------|
| **Promise** | `A → Promise[A]` | J, C | ✅ Documented | Lazy computation deferral |
| **View** | `Agent[A,B] → Widget` | I | 🔄 Implicit | Visual representation |
| **Metered** | `Agent[A,B] → Transaction[A,B]` | B | 🔄 Implicit | Economic wrapping |
| **Personalization** | `Agent[A,B] → Agent[A,B]` | K | 🔄 Implicit | Personality field application |
| **Lens** | `S → A` (bidirectional) | D | 🔄 Implicit | State focus/update |
| **Optimization** | `Agent[A,B] → Agent'[A,B]` | R | 🔄 Implicit | Prompt optimization (endofunctor) |
| **Spy** | `Agent[A,A] → Agent[A,A]` | T | 🔄 Implicit | Identity + tracing side effect |
| **Mock** | `Agent[A,B] → Agent[A,B]` | T | 🔄 Implicit | Replace with constant |
| **Parser** | `Text → ParseResult[A]` | P | 🔄 Implicit | Structured extraction |
| **Tool** | `Agent[A,B] → Tool[A,B]` | T+J | 🔄 Implicit | Tool-use wrapping |
| **Trace** | `Agent[A,B] → Agent[A,B]` | W | 🔄 Implicit | Observability wrapping |
| **Sandbox** | `Agent[A,B] → Agent[A,B]` | J | 🔄 Implicit | Safety isolation |

---

## 1. Promise Functor (J-gents, C-gents)

### Signature
```
Promise: Agent[A, B] → Agent[A, Promise[B]]
```

### Description
Defers computation until explicitly resolved. Enables lazy evaluation trees.

### Laws
```python
# Identity
Promise(Id[A]) ≅ Id[Promise[A]]

# Composition
Promise(f >> g) ≅ Promise(f) >> Promise(map(g))
```

### Status
✅ **Fully documented** in `spec/c-gents/functors.md` and `spec/j-gents/lazy.md`

### Implementation
`impl/claude/agents/j/promise.py`

---

## 2. View Functor (I-gents)

### Signature
```
View: Agent[A, B] → Widget[Agent[A, B]]
```

### Description
Maps agents to contextually adaptive UI components. Deterministic: same agent always produces same widget structure (content varies with state).

### Laws
```python
# Identity preservation (structural)
View(Id) produces GlyphWidget(Id)  # Minimal representation

# Composition visualization
View(f >> g) produces GraphWidget([View(f), View(g)])
```

### Key Insight
**Form reveals function**: The widget ontology (Glyph, Card, Stream, Graph, etc.) directly corresponds to agent behavioral patterns.

### Specification
`spec/i-gents/view-functor.md` (~380 lines)

### Status
🔄 **Implicit** - Fully specified but not formally added to functor catalog

### Formalization Opportunity
Add View Functor to `spec/c-gents/functors.md` with:
- Widget ontology mapping table
- Context adaptation laws
- Composition rendering rules

---

## 3. Metered Functor (B-gents)

### Signature
```
Metered: Agent[A, B] → Transaction[A, B]
```

Where `Transaction[A, B]` wraps execution with:
- Pre-execution: Token lease acquisition
- Execution: Actual agent invocation
- Post-execution: Cost settlement & receipt

### Description
Transforms any "free" agent into an "economic" agent operating within token budgets and rate limits.

### Laws
```python
# Cost preservation
cost(Metered(f).invoke(x)) == cost(f.invoke(x))  # No overhead beyond tracking

# Composition economics
Metered(f >> g) ≡ Metered(f) >> Metered(g)  # Costs are additive
```

### Key Insight
**Linear Types**: Tokens cannot be copied, only spent. The functor enforces this via the CentralBank.

### Specification
`spec/b-gents/banker.md` (Section: "The Core Abstraction: The Metered Functor")

### Status
🔄 **Implicit** - Described as "core abstraction" but not formally cataloged as functor

### Formalization Opportunity
Add to functor catalog with:
- Token lease algebra
- Rate limiting as functor constraint
- Auction mechanism as resource allocation

---

## 4. Personalization Functor (K-gent)

### Signature
```
K: Agent[A, B] → Agent[A, B]  (same signature, personalized behavior)
```

### Description
Lifts agents into "personalized space" - behavior is colored by the personality field without changing interface.

### Laws
```python
# Identity preservation
K(Id) ≅ Id  # Identity remains identity (but with personality)

# Composition preservation
K(f >> g) ≅ K(f) >> K(g)  # Personality pervades composition
```

### Key Insight
**Personality as Field**: Not stored preferences, but the shape of the space itself. K-gent is the fixed point of system-developer mutual adaptation.

```
K = Fix(λsystem. developer_adapts(system))
```

### Specification
`spec/k-gent/README.md` (Section: "The Functor Perspective")

### Status
🔄 **Implicit** - Described as functor but not in formal catalog

### Formalization Opportunity
Add to functor catalog with:
- Personality field equations
- Fixed-point characterization
- Unity of developer-system

---

## 5. Lens Functor (D-gents)

### Signature
```
Lens[S, A]: (get: S → A, set: (S, A) → S)
```

Lenses are **bidirectional functors** - they both extract and update.

### Description
Compositional state access. Lenses focus on sub-parts of larger structures while preserving the ability to update.

### Laws
```python
# GetPut: Reading then writing is identity
lens.set(state, lens.get(state)) == state

# PutGet: Writing then reading returns what was written
lens.get(lens.set(state, value)) == value

# PutPut: Last write wins
lens.set(lens.set(state, v1), v2) == lens.set(state, v2)
```

### Composition
```python
# Lens composition
(lens1 >> lens2).get(state) == lens2.get(lens1.get(state))
(lens1 >> lens2).set(state, val) == lens1.set(state, lens2.set(lens1.get(state), val))
```

### Specification
`spec/d-gents/lenses.md`

### Status
🔄 **Implicit** - Documented as lenses, but functor properties not emphasized

### Formalization Opportunity
Add to functor catalog emphasizing:
- Bidirectional functor nature
- Lens laws as functor constraints
- Composition algebra

---

## 6. Optimization Endofunctor (R-gents)

### Signature
```
R: Agent[A, B] → Agent'[A, B]  (same signature, optimized prompts)
```

**Key property**: This is an **endofunctor** - it maps Agent category to itself.

### Description
Transforms agents by optimizing their prompts via teleprompters (DSPy, TextGrad, MIPROv2, OPRO). The optimized agent has identical interface but improved performance.

### Laws
```python
# Identity (trivial optimization)
R(Id) ≅ Id  # Optimizing identity is still identity

# Composition (optimization distributes)
R(f >> g) ≅ R(f) >> R(g)  # OR optimize pipeline as unit

# Monotonicity (optimization doesn't degrade)
Loss(R(agent)) ≤ Loss(agent)  # By definition of optimization
```

### Key Insight
**Optimization as Endofunctor**: Unlike other functors that change structure, R changes *implementation* while preserving *interface*.

### Specification
`spec/r-gents/README.md` (Section: "The Endofunctor")

### Status
🔄 **Implicit** - Explicitly called "endofunctor" but not in formal catalog

### Formalization Opportunity
Add to functor catalog with:
- Loss function monotonicity
- Teleprompter algebra
- ROI-guided optimization

---

## 7. Spy Functor (T-gents)

### Signature
```
Spy: Agent[A, A] → Agent[A, A]  (identity with logging side effect)
```

### Description
Wraps an identity agent with observation - records all inputs/outputs to history while passing data through unchanged.

### Laws
```python
# Identity preservation (ignoring side effects)
Spy(label).invoke(x) == x  # Value unchanged

# Composition transparency
(f >> Spy(label) >> g) ≡ (f >> g)  # Semantically equivalent

# History accumulation
len(Spy.history) increases with each invocation
```

### Key Insight
**Writer Monad**: Spy is the Writer monad specialized to identity - it accumulates a log while passing values through.

### Specification
`spec/t-gents/taxonomy.md` (Section: "SpyAgent: The Writer Monad")

### Status
🔄 **Implicit** - Described as Writer monad but not in functor catalog

### Formalization Opportunity
Add to functor catalog with:
- Writer monad connection
- Trace semantics
- Integration with W-gent observability

---

## 8. Mock Functor (T-gents)

### Signature
```
Mock: Agent[A, B] → Agent[A, B]  (constant output, ignores input)
```

### Description
Replaces any agent with one that returns a fixed output, optionally with simulated latency.

### Laws
```python
# Constancy
Mock(b).invoke(a1) == Mock(b).invoke(a2)  # ∀ a1, a2 ∈ A

# Identity absorption
Mock(b) >> f ≠ f  # Unless f is also constant

# Delay simulation
time(Mock(b, delay=t).invoke(x)) ≈ t
```

### Key Insight
**Constant Morphism**: Mock is the categorical constant - it collapses all inputs to a single output.

### Specification
`spec/t-gents/taxonomy.md` (Section: "MockAgent: The Constant Morphism")

### Status
🔄 **Implicit** - Described as constant morphism but not in functor catalog

### Formalization Opportunity
Add to functor catalog with:
- Constant functor properties
- Testing algebra (mock composition)
- Latency simulation semantics

---

## 9. Parser Functor (P-gents)

### Signature
```
Parser: Text → ParseResult[A]

where ParseResult[A] = Success(value: A, confidence: float) | Failure(error)
```

### Description
Extracts structured data from unstructured text. Handles LLM output variability via confidence scores and repair strategies.

### Laws
```python
# Determinism (for same strategy)
Parser(strategy).parse(text) == Parser(strategy).parse(text)

# Composition (fallback chain)
(p1 | p2 | p3).parse(text) returns first successful parse

# Fusion (parallel merge)
Fuse(p1, p2).parse(text) merges results from both parsers
```

### Key Insight
**Stochastic-Structural Gap**: Traditional parsers assume deterministic syntax; P-gents handle LLM sampling distributions.

### Specification
`spec/p-gents/README.md`

### Status
🔄 **Implicit** - Described as morphisms but not formalized as functor

### Formalization Opportunity
Add to functor catalog with:
- ParseResult functor laws
- Fallback/Fusion algebra
- Confidence propagation

---

## 10. Tool Functor (T-gents Phase 2 + J-gents)

### Signature
```
Tool: Agent[A, B] → Tool[A, B]

where Tool[A, B] adds:
- MCP protocol integration
- Capability constraints (network, filesystem, etc.)
- Sandboxed execution
- Error handling via Result[B, ToolError]
```

### Description
Wraps agents as MCP-compatible tools with safety constraints and standardized error handling.

### Laws
```python
# Interface preservation
Tool(agent).invoke(x) has same semantics as agent.invoke(x)
# (but wrapped in Result[B, ToolError])

# Composition preservation
Tool(f >> g) ≅ Tool(f) >> Tool(g)

# Capability enforcement
If Tool requires network and disabled → returns ToolError
```

### Key Insight
**Tool-Use Bridge**: Enables agents to be invoked via MCP, Claude Desktop, or other tool-use protocols.

### Specification
- `spec/t-gents/tool-use.md` (Phase 2)
- `impl/claude/agents/j/t_integration.py` (JIT tool generation)

### Status
🔄 **Implicit** - Phase 2 implementation exists but not formalized as functor

### Formalization Opportunity
Add to functor catalog with:
- MCP protocol mapping
- Capability algebra
- J-gent JIT tool generation

---

## 11. Trace Functor (W-gents)

### Signature
```
Trace: Agent[A, B] → Agent[A, B]  (with observability side effects)
```

### Description
Wraps agent execution with real-time observability - emits events to Wire protocol without changing agent behavior.

### Laws
```python
# Transparency (ignoring wire emissions)
Trace(agent).invoke(x) == agent.invoke(x)  # Value unchanged

# Composition preservation
Trace(f >> g) ≅ Trace(f) >> Trace(g)  # Each stage traced

# Ephemerality
Wire stops → all traces vanish (no persistence)
```

### Key Insight
**Ephemeral Observability**: Unlike Spy (which persists history), Trace emits to external observer and leaves no internal trace.

### Specification
`spec/w-gents/README.md`

### Status
🔄 **Implicit** - W-gents implement wrapping but not formalized as functor

### Formalization Opportunity
Add to functor catalog with:
- Wire protocol event algebra
- Ephemer ality guarantees
- Integration with Spy functor

---

## 12. Sandbox Functor (J-gents)

### Signature
```
Sandbox: Agent[A, B] → Agent[A, B]  (isolated execution)
```

### Description
Executes JIT-compiled agents in restricted namespace - prevents dangerous operations while maintaining interface.

### Laws
```python
# Safety (forbidden operations fail)
Sandbox(agent, forbidden=["os", "sys"]).invoke(x)
# → Error if agent attempts os/sys access

# Transparency (for safe agents)
If agent doesn't violate constraints:
  Sandbox(agent).invoke(x) == agent.invoke(x)

# Composition isolation
Each Sandbox(agent) executes in fresh namespace
```

### Key Insight
**Safety as Functor Constraint**: Sandboxing is a functor transformation with additional safety invariants.

### Specification
`spec/j-gents/jit.md` (Sandbox section)

### Status
🔄 **Implicit** - Implemented but not formalized as functor

### Formalization Opportunity
Add to functor catalog with:
- Safety constraint algebra
- Namespace isolation semantics
- Composition with other functors (e.g., Trace(Sandbox(agent)))

---

## Functor Composition Patterns

### Sequential Wrapping
```python
agent = base_agent
agent = K(agent)          # Personalize
agent = Metered(agent)    # Add economics
agent = Trace(agent)      # Add observability
agent = Sandbox(agent)    # Add safety
```

### Parallel Application
```python
# View and Trace simultaneously
widget = View(agent, context)
traced = Trace(agent)

# Different functors for different concerns
```

### Conditional Functor Selection
```python
def wrap_agent(agent, mode):
    match mode:
        case "dev": return Trace(agent)
        case "test": return Mock(agent, test_output)
        case "prod": return Metered(Trace(agent))
```

---

## Formalization Roadmap

### Priority 1: Update functor catalog
- Add all 12 functors to `spec/c-gents/functors.md`
- Include laws, examples, cross-references

### Priority 2: Cross-genus integration
- Document functor composition patterns
- Show how functors interact (e.g., Metered(Trace(agent)))
- Identify functor anti-patterns

### Priority 3: Implementation alignment
- Ensure all implementations satisfy functor laws
- Add property-based tests for functor laws
- Create functor composition utilities

---

## Anti-Patterns

### 1. Breaking Functor Laws
```python
# BAD: Optimization that degrades performance
R(agent) where Loss(R(agent)) > Loss(agent)  # Violates monotonicity

# BAD: Spy that modifies data
Spy(agent).invoke(x) != x  # Violates transparency
```

### 2. Implicit Functor Stacking
```python
# BAD: Hidden wrapping
def run_agent(agent):
    # Implicitly wraps without documenting
    return Metered(Trace(Personalize(agent)))

# GOOD: Explicit composition
agent = K(agent)
agent = Trace(agent)
agent = Metered(agent)
```

### 3. Non-Commuting Functors
```python
# Order matters!
Metered(Trace(agent)) != Trace(Metered(agent))
# First: Measures traced execution cost
# Second: Traces metering overhead

# Document order dependencies
```

---

## See Also

- [functors.md](functors.md) - Core functor theory
- [monads.md](monads.md) - Functors with structure
- [anatomy.md](../anatomy.md) - Agent lifecycle & wrapping
- Individual genus specs for detailed functor descriptions

---

**Status**: This catalog identifies 12 functors across kgents. 1 is fully documented (Promise), 11 are implicit. Formalizing these would enable systematic reasoning about agent transformations and composition patterns across the entire ecosystem.
