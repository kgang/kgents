# T-gents Algebra: Category Theory Foundations

This document formalizes the mathematical foundations of T-gents through Category Theory, establishing testing as the verification of algebraic laws.

---

## The Category $\mathcal{C}_{Agent}$

All agents operate within the category $\mathcal{C}_{Agent}$:

**Definition**: $\mathcal{C}_{Agent} = (Obj, Hom, \circ, id)$

| Component | Definition | Interpretation |
|-----------|------------|----------------|
| $Obj(\mathcal{C})$ | Types/Schemas | Input type $A$, output type $B$ |
| $Hom(A, B)$ | Agent morphisms | Functions $f: A \to B$ |
| $\circ$ | Composition | Pipeline operator `>>` |
| $id_A$ | Identity morphism | `Identity: A → A` |

---

## The Three Categorical Laws

### Law 1: Associativity

**Formal Statement**:
```
∀ f ∈ Hom(A, B), g ∈ Hom(B, C), h ∈ Hom(C, D):
  (f ∘ g) ∘ h = f ∘ (g ∘ h)
```

**Interpretation**: Pipeline composition order doesn't affect the result.

**T-gent Verification**:
```python
async def verify_associativity(f: Agent[A, B], g: Agent[B, C], h: Agent[C, D]):
    """Prove associativity through execution."""
    test_input: A = generate_test_input()

    # Left association
    left = await ((f >> g) >> h).invoke(test_input)

    # Right association
    right = await (f >> (g >> h)).invoke(test_input)

    # Law must hold
    assert left == right, "Associativity violated!"
```

### Law 2: Identity

**Formal Statement**:
```
∀ f ∈ Hom(A, B):
  f ∘ id_A = f = id_B ∘ f
```

**Interpretation**: Composing with identity doesn't change behavior.

**T-gent Verification**:
```python
async def verify_identity(f: Agent[A, B]):
    """Prove identity law through execution."""
    test_input: A = generate_test_input()

    # Original function
    original = await f.invoke(test_input)

    # Left identity
    left_id = await (Identity() >> f).invoke(test_input)

    # Right identity
    right_id = await (f >> Identity()).invoke(test_input)

    # Laws must hold
    assert original == left_id == right_id, "Identity law violated!"
```

### Law 3: Closure

**Formal Statement**:
```
∀ f ∈ Hom(A, B), g ∈ Hom(B, C):
  (f ∘ g) ∈ Hom(A, C)
```

**Interpretation**: Composing two agents produces a valid agent.

**T-gent Verification**:
```python
async def verify_closure(f: Agent[A, B], g: Agent[B, C]):
    """Prove closure through type checking."""
    # Composition should be well-typed
    composed: Agent[A, C] = f >> g

    # Should be invokable
    result = await composed.invoke(test_input)

    assert isinstance(result, C), "Closure violated!"
```

---

## Commutative Diagrams: The Heart of T-gent Testing

T-gents enable **commutative diagram verification**—proving that different paths through a system are equivalent.

### Definition

A diagram **commutes** if all paths between the same start and end points yield the same result.

### Example 1: Retry Equivalence

**Claim**: `RetryAgent >> FailingAgent(fail_count=2)` ≡ `SuccessAgent`

```
Input ─────────────────> Success (direct)
  │
  │  RetryAgent >> FailingAgent(fails=2, then success)
  └──────────────────────> Success (recovered)
```

**Verification**:
```python
async def test_retry_commutes():
    # Path 1: Direct success
    success_path = MockAgent(output="Success")

    # Path 2: Retry after failures
    failing = FailingAgent(FailingConfig(fail_count=2, recovery_token="Success"))
    retry_path = RetryAgent(max_retries=3) >> failing

    # Both paths should reach the same output
    input_data = "Test"
    assert await success_path.invoke(input_data) == await retry_path.invoke(input_data)
```

### Example 2: Spy Transparency

**Claim**: `SpyAgent` is transparent—it doesn't affect data flow.

```
A ──────f──────> B   (without spy)
  \              ↑
   \─spy─f──────/     (with spy)
```

**Verification**:
```python
async def test_spy_commutes():
    f = ProductionAgent()
    spy = SpyAgent(label="Test")

    test_input: A = generate_test_input()

    # Path without spy
    without_spy = await f.invoke(test_input)

    # Path with spy
    with_spy = await (spy >> f).invoke(test_input)

    # Outputs must be identical
    assert without_spy == with_spy

    # Spy recorded the data
    assert spy.history[0] == test_input
```

---

## Functors: Structure-Preserving Transformations

T-gents often act as **endofunctors** on $\mathcal{C}_{Agent}$.

### Definition

A functor $F: \mathcal{C} \to \mathcal{C}$ maps:
- Objects to objects: $A \mapsto F(A)$
- Morphisms to morphisms: $(f: A \to B) \mapsto (F(f): F(A) \to F(B))$

**Laws**:
1. $F(id_A) = id_{F(A)}$ (preserves identity)
2. $F(g \circ f) = F(g) \circ F(f)$ (preserves composition)

### Example: RetryAgent as Functor

`RetryAgent` wraps any agent $f: A \to B$ with retry logic:

```python
class RetryAgent:
    """Endofunctor adding retry capability."""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    def wrap(self, f: Agent[A, B]) -> Agent[A, B]:
        """F(f) = RetryWrapper(f)"""
        async def retry_invoke(input_data: A) -> B:
            for attempt in range(self.max_retries):
                try:
                    return await f.invoke(input_data)
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise
            raise RuntimeError("Retry exhausted")

        return Agent(name=f"Retry({f.name})", invoke=retry_invoke)
```

**Functor Laws**:
```python
# Law 1: F(id) = id
retry = RetryAgent()
assert retry.wrap(Identity()) ≈ Identity()

# Law 2: F(g ∘ f) = F(g) ∘ F(f)
composed = f >> g
assert retry.wrap(composed) ≈ retry.wrap(f) >> retry.wrap(g)
```

---

## Monads: Handling Effects and Context

T-gents introducing side effects (logging, metrics) are monadic.

### The Agent Monad

**Definition**:
```python
class AgentMonad(Generic[A]):
    """Monad capturing agent computation context."""

    def __init__(self, value: A, context: Dict[str, Any] = None):
        self.value = value
        self.context = context or {}

    def bind(self, f: Callable[[A], 'AgentMonad[B]']) -> 'AgentMonad[B]':
        """Monadic bind (>>=)."""
        result = f(self.value)
        # Merge contexts
        result.context.update(self.context)
        return result

    @staticmethod
    def unit(value: A) -> 'AgentMonad[A]':
        """Monadic return."""
        return AgentMonad(value)
```

**Monad Laws**:
```python
# Left identity: unit(a) >>= f ≡ f(a)
assert AgentMonad.unit(a).bind(f) == f(a)

# Right identity: m >>= unit ≡ m
assert m.bind(AgentMonad.unit) == m

# Associativity: (m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)
assert m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))
```

### Example: SpyAgent as Monadic Writer

```python
class SpyAgent(Generic[A]):
    """Writer monad tracking computation history."""

    def __init__(self, label: str):
        self.name = f"Spy({label})"
        self.history: List[A] = []

    async def invoke(self, input_data: A) -> A:
        # Write to log (monadic effect)
        self.history.append(input_data)
        # Return value unchanged (identity transformation)
        return input_data
```

---

## Resilience: Topological Stability

Beyond discrete laws, T-gents verify **topological properties**—stability under perturbation.

### Definition: ε-Resilience

An agent $f: A \to B$ is **ε-resilient** if:
```
∀ a ∈ A, ∀ δ ∈ Perturbations where ||δ|| < ε:
  d(f(a), f(a + δ)) < ε
```

Where $d$ is a distance metric on $B$.

### Example: Semantic Stability Test

```python
async def test_semantic_resilience(f: Agent[str, str], epsilon: float = 0.1):
    """Verify agent is stable under semantic noise."""
    test_input = "Fix the authentication bug"

    # Generate semantic perturbations
    perturbations = [
        "Fix the auth bug",  # Abbreviation
        "Fix the Authentication bug",  # Capitalization
        "Fix  the  authentication  bug",  # Whitespace
        "Fix the authentication bug.",  # Punctuation
    ]

    # Original output
    original = await f.invoke(test_input)

    # All perturbed outputs should be semantically similar
    for perturbed_input in perturbations:
        perturbed = await f.invoke(perturbed_input)
        similarity = semantic_similarity(original, perturbed)
        assert similarity > (1 - epsilon), f"Unstable: {similarity} < {1-epsilon}"
```

---

## Property-Based Testing via QuickCheck

T-gents enable **property-based testing**—verifying laws for all inputs, not just examples.

### Concept

Instead of writing:
```python
assert f(1) == 2
assert f(2) == 4
```

Write:
```python
@property
def test_doubling(x: int):
    assert f(x) == 2 * x
```

### T-gent Integration

```python
from hypothesis import given, strategies as st

@given(st.text())
async def test_identity_law(input_text: str):
    """Identity law holds for all text inputs."""
    agent = MyAgent()
    identity = Identity()

    result1 = await agent.invoke(input_text)
    result2 = await (agent >> identity).invoke(input_text)

    assert result1 == result2
```

---

## The Algebraic Testing Framework

Combining these concepts, T-gents provide a complete algebraic testing framework:

| Property | Verification Method | T-gent |
|----------|---------------------|--------|
| Associativity | Commutative diagram | MockAgent |
| Identity | Law verification | SpyAgent |
| Closure | Type checking | All agents |
| Resilience | ε-perturbation | NoiseAgent |
| Idempotence | $f \circ f = f$ | CounterAgent |
| Commutativity | $f \circ g = g \circ f$ | SpyAgent |
| Distributivity | $f \circ (g + h) = f \circ g + f \circ h$ | PredicateAgent |

---

## Success Metrics

A test suite using T-gents should achieve:

1. **Completeness**: All categorical laws verified
2. **Soundness**: No false positives
3. **Coverage**: Property tests over input space
4. **Efficiency**: Minimal redundant testing
5. **Clarity**: Failed tests reveal exact law violation

---

## See Also

- [README.md](README.md) - T-gents overview
- [taxonomy.md](taxonomy.md) - Specific T-gent implementations
- [../c-gents/composition.md](../c-gents/composition.md) - Composition rules
- [../c-gents/functors.md](../c-gents/functors.md) - Functor specifications
- [../c-gents/monads.md](../c-gents/monads.md) - Monadic patterns

---

## References

- Bartosz Milewski, *Category Theory for Programmers*
- Saunders Mac Lane, *Categories for the Working Mathematician*
- QuickCheck (Haskell) - Property-based testing
- Hypothesis (Python) - Property-based testing framework
