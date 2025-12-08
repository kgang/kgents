# Contracts: Interface Synthesis

A **contract** is F-gent's specification of an agent's interface—the protocol defining how the agent composes with others.

---

## Philosophy

> "A contract is not documentation; it is the artifact's promise to the ecosystem."

Contracts are **first-class** in F-gent design:
- Synthesized *before* implementation
- Machine-readable and verifiable
- Enable type-safe composition
- Make behavioral guarantees explicit

---

## Contract Structure

```python
@dataclass
class Contract:
    """
    The complete interface specification for an agent.
    """
    # Identity
    agent_name: str              # Unique identifier
    version: str                 # Semantic version (1.0.0)

    # Type Signature
    input_type: Type             # What the agent accepts
    output_type: Type            # What the agent produces

    # Behavioral Guarantees
    invariants: list[Invariant]  # Properties that always hold
    preconditions: list[Condition]   # Input requirements
    postconditions: list[Condition]  # Output guarantees

    # Composition Protocol
    composition_rules: list[CompositionRule]  # How to combine with others
    category_laws: list[CategoryLaw]          # Functor/Monad laws (if applicable)

    # Semantics
    semantic_intent: str         # Human-readable "why"
    examples: list[Example]      # Concrete input/output pairs
```

---

## The Three Layers of Contracts

### Layer 1: Type Signatures (Structural)

**What**: The shape of data flowing through the agent.

```python
# Simple signature
Agent[str, int]  # String input → Integer output

# Complex signature
Agent[ParsedDocument, Summary]  # Document input → Summary output
```

**Type synthesis rules**:
1. Prefer existing types over new types (reuse ecosystem vocabulary)
2. If new type needed, define minimal structure
3. Use algebraic types for clarity:
   - Product types: `@dataclass` for combinations
   - Sum types: `Union[A, B]` for alternatives
   - Result types: `Result[T, E]` for failable operations

**Example**:
```python
# Intent: "Agent that fetches user data or returns error"
# Contract type signature:
Agent[UserId, Result[UserProfile, FetchError]]
```

### Layer 2: Invariants (Behavioral)

**What**: Guarantees that hold across all invocations.

**Categories of invariants**:

1. **Performance invariants**:
   - Latency: `response_time < 200ms`
   - Throughput: `handles > 1000 req/s`
   - Resource: `memory_usage < 512MB`

2. **Correctness invariants**:
   - Determinism: `f(x) == f(x)` (same input → same output)
   - Idempotency: `f(f(x)) == f(x)` (repeated application safe)
   - Purity: `no_side_effects(f)`

3. **Safety invariants**:
   - Error transparency: `errors_propagate_explicitly`
   - No data loss: `len(output) >= len(critical_input_fields)`
   - Authentication: `requires_valid_token`

4. **Domain invariants**:
   - "All citations exist in input" (summarization)
   - "Output is valid JSON" (formatters)
   - "No personally identifiable info" (anonymizers)

**Specification format**:
```python
@dataclass
class Invariant:
    name: str           # Human-readable label
    predicate: str      # Formal specification (Python expression or logic)
    severity: Severity  # MUST | SHOULD | MAY
    testable: bool      # Can this be verified automatically?
```

**Example**:
```python
Invariant(
    name="Idempotency",
    predicate="forall x: invoke(invoke(x)) == invoke(x)",
    severity=Severity.MUST,
    testable=True
)
```

### Layer 3: Composition Rules (Categorical)

**What**: How this agent combines with others.

**Composition types**:

1. **Sequential** (`>>`):
   ```python
   AgentA[I, M] >> AgentB[M, O]  →  AgentC[I, O]
   # Type M must align (A's output = B's input)
   ```

2. **Parallel** (product):
   ```python
   AgentA[I, A] × AgentB[I, B]  →  AgentC[I, (A, B)]
   # Both receive same input, outputs combined
   ```

3. **Alternative** (sum):
   ```python
   AgentA[I, O] | AgentB[I, O]  →  AgentC[I, O]
   # Try A, if fails try B (fallback pattern)
   ```

4. **Functor** (map):
   ```python
   fmap(AgentA[I, O], Container[I])  →  Container[O]
   # Apply agent to each element in container
   ```

**Composition rule specification**:
```python
@dataclass
class CompositionRule:
    pattern: str        # "sequential", "parallel", "alternative", "functor"
    left_type: Type     # Type signature of left component
    right_type: Type    # Type signature of right component
    result_type: Type   # Type signature of composition result
    constraints: list[str]  # Additional requirements
```

---

## Contract Synthesis Process

### Step 1: Extract Types from Intent

**Intent analysis**:
```
User: "Agent that parses CSV files and returns JSON"
```

**Type extraction**:
- Input: CSV file → `str | Path`
- Output: JSON → `dict | JSONData`

**Decision logic**:
- Is `str` sufficient or need `Path` for file handling?
- Is generic `dict` acceptable or define `JSONData` schema?

**Result**:
```python
input_type = Union[str, Path]
output_type = JSONData  # Define new type with schema
```

### Step 2: Synthesize Invariants from Constraints

**Intent constraints**:
```
User: "Must handle malformed CSV gracefully, no crashes"
```

**Invariant synthesis**:
```python
Invariant(
    name="Error transparency",
    predicate="malformed_input → Result.Err (never raises exception)",
    severity=Severity.MUST,
    testable=True
)
```

### Step 3: Determine Composition Protocol

**Dependency analysis**:
- Does this agent depend on other agents? (No)
- Will this agent be composed with others? (Yes—likely CSV >> Parser >> Processor)

**Composition rules**:
```python
CompositionRule(
    pattern="sequential",
    left_type=Agent[Path, str],      # CSV reader
    right_type=Agent[str, JSONData], # This agent (Parser)
    result_type=Agent[Path, JSONData],
    constraints=["left output must be valid string"]
)
```

### Step 4: Validate Against Category Laws

If agent claims to be a **Functor**, verify laws:
```python
# Identity law
fmap(identity, container) == container

# Composition law
fmap(f >> g, container) == fmap(f, fmap(g, container))
```

If agent claims to be a **Monad**, verify laws:
```python
# Left identity
bind(return(a), f) == f(a)

# Right identity
bind(m, return) == m

# Associativity
bind(bind(m, f), g) == bind(m, lambda x: bind(f(x), g))
```

F-gent uses T-gent property testing to verify these.

---

## Ontology Alignment: The Core Challenge

**Problem**: Two agents want to compose, but their types don't align.

### Scenario 1: Direct Mismatch

```python
AgentA: str → Document
AgentB: ParsedDoc → Summary

# Type mismatch: Document ≠ ParsedDoc
```

**Solution strategies**:

1. **Adapter synthesis**:
   ```python
   Adapter: Document → ParsedDoc
   AgentA >> Adapter >> AgentB  # Now composable
   ```

2. **Type unification** (if semantically equivalent):
   ```python
   # Realize Document and ParsedDoc are same concept
   # Alias: ParsedDoc = Document
   AgentA >> AgentB  # Direct composition
   ```

3. **Request clarification**:
   ```python
   F-gent: "AgentB expects ParsedDoc, but AgentA produces Document.
            Are these the same? Or do you need parsing step?"
   ```

### Scenario 2: Implicit Assumptions

```python
AgentA: str → WeatherData
AgentB: WeatherData → Report

# But WeatherData has two variants:
#   - WeatherData_Celsius
#   - WeatherData_Fahrenheit
# AgentA produces Celsius, AgentB expects Fahrenheit
```

**Solution**:
- **Make assumptions explicit in contract**:
  ```python
  AgentA:
    output_type: WeatherData
    postconditions: ["temperature_unit == Celsius"]

  AgentB:
    input_type: WeatherData
    preconditions: ["temperature_unit == Fahrenheit"]
  ```

- **Synthesize converter**:
  ```python
  Converter: WeatherData[Celsius] → WeatherData[Fahrenheit]
  AgentA >> Converter >> AgentB
  ```

### Scenario 3: Semantic Mismatch

```python
AgentA: UserId → UserProfile
AgentB: CustomerProfile → Invoice

# UserProfile and CustomerProfile are conceptually related but structurally different
```

**Solution**:
- **Ontology mapping**:
  ```python
  Mapper: UserProfile → CustomerProfile
  # Explicit mapping of fields:
  #   UserProfile.name → CustomerProfile.customer_name
  #   UserProfile.email → CustomerProfile.billing_email
  #   (etc.)
  ```

- **F-gent generates mapping based on field names + semantics**

---

## Contract Versioning

Contracts evolve. Versioning prevents breakage.

### Semantic Versioning for Contracts

- **Patch** (`1.0.0 → 1.0.1`):
  - Invariant clarified (no functional change)
  - Example refined (same behavior)
  - **Compatible**: All consumers unaffected

- **Minor** (`1.0.0 → 1.1.0`):
  - New optional postcondition added
  - Invariant strengthened (agent does more than before)
  - **Backward compatible**: Old consumers still work

- **Major** (`1.0.0 → 2.0.0`):
  - Input/output type changed
  - Invariant weakened (agent guarantees less)
  - Composition rule changed
  - **Breaking change**: Consumers may break

### Compatibility Checking

When re-forging, F-gent checks:
```python
def is_compatible(old_contract: Contract, new_contract: Contract) -> bool:
    # Input type covariance
    if not is_subtype(new_contract.input_type, old_contract.input_type):
        return False  # Breaking: now accepts less

    # Output type contravariance
    if not is_subtype(old_contract.output_type, new_contract.output_type):
        return False  # Breaking: now produces less

    # Invariant preservation
    if not all(inv in new_contract.invariants for inv in old_contract.invariants):
        return False  # Breaking: removed guarantee

    return True  # Compatible
```

---

## Testing Contracts

Contracts are **executable specifications**—they can be tested.

### Invariant Testing

```python
# Given contract:
contract = Contract(
    invariants=[
        Invariant(name="Idempotency", predicate="f(f(x)) == f(x)"),
        Invariant(name="Latency", predicate="response_time < 200ms")
    ]
)

# T-gent property test:
@property_test
def test_idempotency(agent: Agent, input: I):
    result1 = agent.invoke(input)
    result2 = agent.invoke(result1)
    assert result1 == result2  # Idempotency

@property_test
def test_latency(agent: Agent, input: I):
    start = time.now()
    result = agent.invoke(input)
    duration = time.now() - start
    assert duration < 0.2  # 200ms
```

### Composition Testing

```python
# Given composition:
pipeline = agent_a >> agent_b >> agent_c

# Test category laws:
@property_test
def test_associativity():
    # (a >> b) >> c == a >> (b >> c)
    left_assoc = (agent_a >> agent_b) >> agent_c
    right_assoc = agent_a >> (agent_b >> agent_c)
    assert left_assoc.invoke(input) == right_assoc.invoke(input)
```

---

## Contract Registry (via L-gent)

When F-gent crystallizes an artifact, the contract is registered:

```python
l_gent.register_contract(
    contract=contract,
    artifact_id="agent_summarizer_v1",
    tags=["summarization", "NLP", "text"],
    hash=compute_hash(contract)
)
```

**Benefits**:
- **Discovery**: Find agents by input/output type
- **Composition planning**: L-gent can suggest composition chains
- **Compatibility checking**: Detect breaking changes across versions

**Query examples**:
```python
# Find agents that produce WeatherData
l_gent.find_producers(output_type=WeatherData)

# Find agents that can compose with AgentA
l_gent.find_composable_with(agent_a, direction="downstream")
```

---

## Human-in-the-Loop: Contract Review

Before crystallizing, F-gent can request contract review:

```
F-gent: "I've synthesized this contract for your summarizer agent:

  Input: str (paper text)
  Output: SummaryJSON
  Invariants:
    - Output length < 500 words
    - No hallucinations (all citations exist in input)
    - Confidence score in [0.0, 1.0]

  Does this match your intent?"

User: "Yes, but add: response time < 5s"

F-gent: [Updates contract with latency invariant, proceeds to Prototype]
```

---

## Example: Full Contract Synthesis

**User Intent**:
> "Agent that translates English to Spanish, preserves formatting, handles errors gracefully"

### Synthesized Contract

```python
Contract(
    agent_name="EnglishToSpanishTranslator",
    version="1.0.0",

    # Type Signature
    input_type=str,
    output_type=Result[str, TranslationError],

    # Invariants
    invariants=[
        Invariant(
            name="Formatting preservation",
            predicate="preserves_whitespace_and_newlines(input, output)",
            severity=Severity.MUST,
            testable=True
        ),
        Invariant(
            name="Language correctness",
            predicate="output_language == Spanish",
            severity=Severity.MUST,
            testable=True
        ),
        Invariant(
            name="Length preservation",
            predicate="0.8 * len(input) < len(output) < 1.5 * len(input)",
            severity=Severity.SHOULD,
            testable=True
        )
    ],

    # Preconditions
    preconditions=[
        Condition("Input is valid UTF-8 string"),
        Condition("Input length < 10,000 characters")
    ],

    # Postconditions
    postconditions=[
        Condition("Output is valid UTF-8 string OR TranslationError"),
        Condition("If Result.Ok, output is Spanish text"),
        Condition("If Result.Err, error explains failure")
    ],

    # Composition
    composition_rules=[
        CompositionRule(
            pattern="sequential",
            left_type=Agent[Document, str],
            right_type=Agent[str, Result[str, TranslationError]],  # This agent
            result_type=Agent[Document, Result[str, TranslationError]],
            constraints=["Left must produce English text"]
        )
    ],

    semantic_intent="Translate English text to Spanish while preserving formatting",

    examples=[
        Example(
            input="Hello, world!\n\nHow are you?",
            expected_output=Result.Ok("¡Hola, mundo!\n\n¿Cómo estás?")
        ),
        Example(
            input="",
            expected_output=Result.Ok("")
        )
    ]
)
```

---

## Contracts as Morphisms

In C-gent category theory, a contract IS a morphism specification:

```
Contract ≅ Morphism in Category C_Agent
```

**Category laws embedded in contract**:
- **Identity**: There exists a contract for Identity agent: `Agent[A, A]`
- **Associativity**: Composition rules preserve associativity
- **Type safety**: Input/output types ensure well-typed composition

---

## See Also

- [forge.md](forge.md) - How contracts are synthesized in Forge Loop
- [artifacts.md](artifacts.md) - How contracts are stored in artifacts
- [README.md](README.md) - F-gent philosophy
- [../c-gents/](../c-gents/) - Category theory foundations
- [../t-gents/property.md](../t-gents/property.md) - Testing contracts
