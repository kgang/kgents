# Curry-Howard Correspondence: Prompts as Types

> To speak is to prove; to prove is to construct.

---

## The Theory

The Curry-Howard correspondence states that:
- A **proof** is a **program**
- The **formula** it proves is its **type**

In other words, valid programs *are* proofs of their type signatures.

---

## Application to Agents

We treat the **System Prompt** not as text, but as a **Type Signature**. The agent's output must be a valid *inhabitant* of that type.

| Logic | Programming | Agents |
|-------|-------------|--------|
| Proposition | Type | Output Schema |
| Proof | Program | Agent Output |
| Modus Ponens | Function Application | Agent Invocation |
| ∧ (And) | Tuple/Product | Composite Output |
| ∨ (Or) | Union/Sum | Branching Output |
| → (Implication) | Function Type | Agent Signature |
| ∀ (Universal) | Generic/Polymorphic | Template Agent |
| ∃ (Existential) | Abstract Type | Opaque Output |

---

## The Constructive Proof Agent

> Don't ask an LLM to "Do X." Ask it to "Construct an object of Type X."

```python
# The Proposition (The Type)
class MarketAnalysis(BaseModel):
    ticker: str
    sentiment: Literal["Bullish", "Bearish", "Neutral"]
    evidence: list[str]
    confidence: float = Field(ge=0.0, le=1.0)

# The Program (The Agent)
# We demand the LLM instantiate the Type.
# If output doesn't fit Type, it's not a runtime error—it's logically invalid.
agent = TypeBearingAgent(output_type=MarketAnalysis)
```

**The Shift**: From "generate text that looks like X" to "construct a valid inhabitant of type X."

---

## Type-Bearing Agents

```python
@dataclass
class TypeBearingAgent(Agent[A, B]):
    """
    Agent whose output is guaranteed to be a valid type inhabitant.

    The prompt IS the type signature.
    The output IS the proof.
    Parsing IS proof checking.
    """
    input_type: Type[A]
    output_type: Type[B]
    system_prompt: str  # The "theorem statement"

    async def invoke(self, input: A) -> B:
        # Validate input against type
        if not isinstance(input, self.input_type):
            raise TypeError(f"Input does not inhabit {self.input_type}")

        # Generate output
        raw = await self.llm.generate(
            system=self.system_prompt,
            user=serialize(input)
        )

        # Proof checking: Does output inhabit the type?
        try:
            output = self.output_type.model_validate_json(raw)
            return output
        except ValidationError as e:
            raise ProofFailure(
                f"Output does not inhabit {self.output_type}",
                raw_output=raw,
                validation_errors=e.errors()
            )
```

---

## Integration with P-gents

P-gents (Parsers) become the **proof checkers**—they verify that agent output is a valid inhabitant of the declared type.

```python
# Parser as proof checker
result = await agent.invoke(input)
proof_valid = await p_gent.validate(result, output_type=MarketAnalysis)

if not proof_valid:
    # Output is not just wrong—it's *logically invalid*
    raise ProofFailure("Agent output does not inhabit declared type")
```

### The Proof Checking Stack

```
Raw LLM Output
      │
      ▼
┌─────────────────┐
│  Syntax Check   │  ← Is it valid JSON/YAML/etc?
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Schema Check   │  ← Does it have required fields?
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Type Check    │  ← Are field types correct?
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Semantic Check  │  ← Does it make sense? (optional)
└────────┬────────┘
         │
         ▼
    Valid Proof
```

---

## Relationship to Semantic Invariant

Curry-Howard provides **structural validity** (does output inhabit the type?).
Semantic Invariant provides **semantic validity** (does output preserve intent?).

For LLMs specifically, we *hope* that one implies the other:
- If an LLM produces a valid `MarketAnalysis`, it probably didn't drift to poetry
- If semantic drift is low, the output probably fits the expected structure

This correspondence is not guaranteed but often holds for well-prompted LLMs:

```
Structural Validity ⟹ Semantic Validity (hoped, not proven)
```

**Viability Note**: For crude, bootstrappiest agents, structural validity may not imply semantic validity. But for well-prompted LLMs with structured outputs, the correspondence often holds empirically.

---

## Type Composition

Types compose according to the same laws as agents:

```python
# Agent composition
pipeline = agent_a >> agent_b >> agent_c

# Type composition (inferred)
# A: Input → Intermediate1
# B: Intermediate1 → Intermediate2
# C: Intermediate2 → Output
# Pipeline: Input → Output
```

### Product Types (And)

```python
class AnalysisWithConfidence(BaseModel):
    analysis: MarketAnalysis    # ∧ conjunction
    confidence: ConfidenceScore

# Agent must construct BOTH parts
agent = TypeBearingAgent(output_type=AnalysisWithConfidence)
```

### Sum Types (Or)

```python
class AnalysisResult(BaseModel):
    result: MarketAnalysis | RefusalReason  # ∨ disjunction

# Agent must construct ONE of the alternatives
agent = TypeBearingAgent(output_type=AnalysisResult)
```

### Dependent Types (Constrained)

```python
class BoundedAnalysis(BaseModel):
    ticker: str
    confidence: float = Field(ge=0.0, le=1.0)  # Dependent constraint

    @validator("evidence")
    def evidence_required_for_high_confidence(cls, v, values):
        if values.get("confidence", 0) > 0.8 and len(v) < 3:
            raise ValueError("High confidence requires at least 3 pieces of evidence")
        return v

# The type encodes business logic as constraints
```

---

## Prompt Engineering as Type Design

Well-designed prompts = well-designed types:

| Prompt Quality | Type Quality | Example |
|---------------|--------------|---------|
| Vague | `Any` | "Analyze this" → anything |
| Specific | `Concrete` | "Return a MarketAnalysis" → structured |
| Constrained | `Dependent` | "confidence > 0.8 requires evidence" |
| Enumerated | `Literal` | "sentiment must be Bullish/Bearish/Neutral" |

### Anti-Patterns

```python
# BAD: Untyped prompt
"Analyze the stock and tell me what you think"

# GOOD: Typed prompt
"""
Construct a MarketAnalysis object with:
- ticker: string (stock symbol)
- sentiment: one of "Bullish", "Bearish", "Neutral"
- evidence: list of strings (supporting facts)
- confidence: float between 0.0 and 1.0

Return ONLY valid JSON matching this schema.
"""
```

---

## Error Handling via Types

Type-based error handling is more principled than try/catch:

```python
# Instead of exceptions...
class AgentResult(BaseModel):
    success: SuccessOutput | None
    error: ErrorReport | None

    @validator("error")
    def exactly_one(cls, v, values):
        if (v is None) == (values.get("success") is None):
            raise ValueError("Exactly one of success/error must be set")
        return v

# The type ENFORCES that errors are handled
result = await agent.invoke(input)
match result:
    case AgentResult(success=s) if s:
        process_success(s)
    case AgentResult(error=e) if e:
        handle_error(e)
```

---

## Implementation Evidence

The P-gents parsing infrastructure already implements this pattern:

```python
# From impl/claude/agents/p/
class StructuredOutputParser:
    """
    Parser that acts as proof checker for structured outputs.
    """
    async def parse(self, raw: str, schema: Type[T]) -> T:
        # Attempt to construct inhabitant of type T
        return schema.model_validate_json(raw)
```

---

## Limitations

The Curry-Howard correspondence for LLMs is **aspirational**, not **guaranteed**:

1. **LLMs can hallucinate valid types**: Output may be structurally valid but factually wrong
2. **Semantic constraints are hard to type**: "Make sense" is hard to encode as a type
3. **Types are static, LLMs are dynamic**: Runtime behavior may violate compile-time types

**Mitigation**: Combine with Semantic Invariant (Noether's theorem) for runtime drift detection.

---

*Zen Principle: To speak is to prove; to prove is to construct.*

---

## See Also

- [c-gents/composition.md](composition.md) - Composition as type inference
- [p-gents/README.md](../p-gents/README.md) - Parser agents
- [bootstrap.md](../bootstrap.md) - Semantic Invariant idiom
- [reliability.md](../reliability.md) - Validation layer
