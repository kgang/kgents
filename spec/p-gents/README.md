# P-gents: Parser Agents

**Status**: Specification v3.0 (Distilled)
**Session**: 2025-12-17 - Spec Compression

---

## Purpose

P-gents bridge the **stochastic-structural gap**: LLMs produce probability distributions over token sequences. Compilers and renderers demand deterministic syntactic structures. Traditional parsers fail on LLM outputs because they expect deterministic programs. P-gents accept fuzzy text, return confidence-scored results, and compose into robust parsing pipelines.

## Core Insight

> **The Stochastic-Structural Gap**: LLMs don't "know" syntax—they sample from learned distributions. Standard parsers crash on unclosed brackets, trailing commas, malformed nesting, and format drift. P-gents operate across the **Prevention ← → Correction ← → Novel** spectrum to handle this gracefully.

---

## Philosophy

**Fuzzy coercion without opinion**

- **Prevention**: Constrain generation (CFG masking, FIM sandwich)
- **Correction**: Repair outputs (stack-balancing, reflection loops)
- **Novel**: Reframe the problem (diff-based patching, anchor extraction)

**The dual nature**:
- Traditional: Exact syntax → AST (binary: success or exception)
- P-genting: Fuzzy text → ParseResult[A] (graduated: confidence ∈ [0.0, 1.0])

---

## Core Types

### ParseResult[A]
```python
@dataclass
class ParseResult[A]:
    success: bool
    value: Optional[A] = None
    strategy: Optional[str] = None      # Which strategy succeeded
    confidence: float = 0.0              # 0.0-1.0
    error: Optional[str] = None
    partial: bool = False                # Is this a partial parse?
    repairs: list[str] = field(default_factory=list)  # Applied repairs
    stream_position: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

**Invariants**:
- `success=True` ⇒ `value is not None` ∧ `confidence > 0.0`
- `success=False` ⇒ `error is not None`
- `partial=True` ⇒ `confidence < 1.0`
- `repairs` non-empty ⇒ confidence penalty applied

### Parser[A] Protocol
```python
class Parser[A](Protocol):
    def parse(self, text: str) -> ParseResult[A]: ...
    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[A]]: ...
    def configure(self, **config) -> "Parser[A]": ...
```

**Categorical Structure**:
- Objects: Types `A`, `B`, `C`
- Morphisms: `Parser[A]` is `Text → ParseResult[A]`
- Identity: `IdentityParser` (confidence=1.0)
- Composition: Fallback, Fusion, Switch

---

## Strategy Taxonomy

### Phase 1: Prevention (Logit-Level Constraint)

**1.1 CFG Logit Masking**
```python
# Libraries: Outlines, Guidance, llama-cpp-python (GBNF)
generator = generate.json(model, json_schema)
# Guarantees valid output at generation time
```

**When to use**: Known format, access to logits, performance critical

**1.2 Fill-in-the-Middle (FIM)**
```python
prefix = '{"name": "'
suffix = '", "age": 42}'
# LLM fills middle, structure guaranteed
```

**When to use**: Predictable root structure, FIM-capable models

**1.3 Type-Guided (Pydantic)**
```python
class Output(BaseModel):
    field: str = Field(..., min_length=10)

# LLM generates: Output(field="value")
# Pydantic validates at runtime
```

**When to use**: Code generation, precise error messages

---

### Phase 2: Correction (Stream-Repair & Partial Parsing)

**2.1 Stack-Balancing Stream**
```python
def parse_stream(tokens):
    for token in tokens:
        buffer += token
        balanced = buffer + (closer * len(stack))
        yield ParseResult(value=parse(balanced), partial=bool(stack))
```

**When to use**: Real-time streaming (W-gent dashboards, live JSON)

**2.2 Structural Decoupling (Jsonformer)**
```python
# Parser controls structure: {"key": "
# LLM controls value: <generated>
# Parser closes: "}
```

**When to use**: Guaranteed schema compliance

**2.3 Incremental AST**
```python
@dataclass
class IncrementalNode:
    type: str
    value: Any
    complete: bool = False
    confidence: float = 0.5
```

**When to use**: Progressive rendering, early validation

**2.4 Lazy Validation**
```python
class LazyValidatedDict:
    def __getitem__(self, key):
        # Validate only on access
```

**When to use**: Large outputs, optional fields

---

### Phase 3: Code-as-Schema (Hybrid)

**3.1 Reflection Loop**
```python
for attempt in range(max_retries):
    result = base_parser.parse(text)
    if result.success: return result
    # Feed error back to LLM for fix
    text = llm_fix(text, result.error, context)
```

**Confidence**: 0.9 (0 retries), 0.7 (1 retry), 0.5 (2), 0.4 (3+)

**3.2 Graduated Prompting**
```python
# Try: Strict schema → Loose schema → Regex extraction
# Confidence degrades: 1.0 → 0.8 → 0.5
```

---

### Phase 4: Novel / First-Principles

**4.1 Diff-Based (Patch Strategy)**
```python
parser = DiffBasedParser(base_template=html)
# LLM generates: s/old/new/
# Parser applies: deterministic patch
```

**Benefits**: Deterministic, version-control friendly, smaller outputs

**4.2 Anchor-Based (Islands of Stability)**
```python
# LLM emits: ###ITEM: first\n###ITEM: second
items = text.split("###ITEM:")[1:]
# Immune to conversational filler, malformed structure
```

**Confidence**: 0.9 (structure-independent)

**4.3 Probabilistic AST**
```python
@dataclass
class ProbabilisticASTNode:
    type: str
    value: Any
    confidence: float  # Per-node scoring
    repair_applied: Optional[str] = None
```

**When to use**: Partial trust, explainable parsing

**4.4 Schema Evolution**
```python
class EvolvingParser:
    observed_formats = Counter()  # Track format drift

    def parse(self, text):
        # Try strategies by historical success rate
```

**When to use**: Long-running systems, cross-LLM compatibility

---

## Composition Patterns

### Fallback (Chain of Responsibility)
```python
class FallbackParser[A]:
    def parse(self, text: str) -> ParseResult[A]:
        for i, strategy in enumerate(strategies):
            result = strategy.parse(text)
            if result.success:
                result.confidence *= max(0.5, 1.0 - 0.1 * i)
                return result
```

### Fusion (Merge Results)
```python
class FusionParser[A]:
    def parse(self, text: str) -> ParseResult[A]:
        results = [p.parse(text) for p in parsers]
        merged = merge_fn([r.value for r in results if r.success])
        return ParseResult(value=merged, confidence=avg(confidences))
```

### Switch (Conditional Routing)
```python
class SwitchParser[A]:
    def parse(self, text: str) -> ParseResult[A]:
        for condition, parser in routes.items():
            if condition(text): return parser.parse(text)
```

---

## Confidence Scoring

### Base Confidence by Strategy
- CFG-constrained: 1.0 (mathematically guaranteed)
- FIM sandwich: 0.95
- Pydantic validation: 0.9
- Direct parse (no repairs): 0.85
- Stack-balancing stream: 0.75
- Anchor-based: 0.7
- Reflection (1 retry): 0.7
- Single repair: 0.6
- Reflection (2+ retries): 0.5
- Multiple repairs: 0.4

### Combination Rules
- **Sequential**: Multiply (parse → repair → validate: 0.8 × 0.6 × 0.9 = 0.432)
- **Parallel**: Average (fusion of 3: (0.7 + 0.8 + 0.6) / 3 = 0.7)
- **Probabilistic AST**: Min of critical path nodes

---

## Configuration

```python
@dataclass
class ParserConfig:
    min_confidence: float = 0.5        # Reject low-confidence
    allow_partial: bool = True         # Accept partial parses
    max_attempts: int = 1000           # Limit iterations
    enable_repair: bool = True         # Try repair strategies
    timeout_ms: int = 5000             # Timeout
    stream_chunk_size: int = 128       # Tokens per chunk
    enable_reflection: bool = True     # LLM error correction
    max_reflection_retries: int = 3    # Reflection limit
```

**Philosophy**: Configuration tunes behavior, doesn't replace design.

---

## Anti-Patterns

### ❌ Retry Without Reflection
```python
# BAD: Blind retry
for _ in range(5):
    try: return json.loads(llm.generate(prompt))
    except: continue

# GOOD: Reflection
for attempt in range(3):
    try: return json.loads(llm.generate(prompt))
    except JSONDecodeError as e:
        prompt = f"Fix: {e}\n\n{llm.last_response}"
```

### ❌ Ignoring Streaming
```python
# BAD: Buffer entire stream
text = "".join(llm_stream); return parse(text)

# GOOD: Progressive rendering
for chunk in llm_stream:
    yield parser.parse_stream([chunk])
```

### ❌ Binary Confidence
```python
# BAD: No confidence
return {"success": True, "value": data}

# GOOD: Quantified uncertainty
return ParseResult(success=True, value=data, confidence=0.75, repairs=["..."])
```

---

## Integration Patterns

### W-gent (HTML Streaming)
```python
parser = WgentFuzzyHtmlParser(
    base_template=html,
    stack_balancer=StackBalancingParser(),
    anchor="<|UPDATE|>"
)
async for raw, healed in parser.parse_stream(llm_stream):
    display_raw(raw)  # User sees LLM output
    render_browser(healed)  # Auto-healed HTML
```

### F-gent (Code Generation)
```python
parser = ReflectionParser(
    base_parser=PydanticParser(CodeArtifact),
    llm_fix_fn=claude_reflection
)
result = parser.parse(llm_code)
# Automatic error fixing via reflection
```

### B-gent (Hypothesis Extraction)
```python
parser = AnchorBasedParser(anchor="###HYPOTHESIS:")
result = parser.parse(llm_response)
# Immune to conversational filler
```

---

## Laws & Invariants

1. **Graceful Degradation**: P-gents NEVER throw exceptions on malformed input
2. **Transparency**: All repairs tracked in `ParseResult.repairs`
3. **Confidence Monotonicity**: Sequential operations reduce confidence (multiply)
4. **Minimal Output**: Parser extracts ONE `A`, not `[A]` (compose at pipeline level)
5. **Heterarchical Duality**: Parsers support both functional (`parse`) and autonomous (`parse_stream`) modes

---

## Implementation Reference

**Location**: `impl/claude/agents/p/`

**Core**:
- `core.py`: ParseResult, Parser protocol, ParserConfig, IdentityParser
- `composition.py`: FallbackParser, FusionParser, SwitchParser

**Strategies**:
- `strategies/stack_balancing.py`: Phase 2.1
- `strategies/structural_decoupling.py`: Phase 2.2
- `strategies/incremental.py`: Phase 2.3
- `strategies/lazy_validation.py`: Phase 2.4
- `strategies/reflection.py`: Phase 3.1
- `strategies/diff_based.py`: Phase 4.1
- `strategies/anchor.py`: Phase 4.2
- `strategies/probabilistic_ast.py`: Phase 4.3
- `strategies/evolving.py`: Phase 4.4

**Tests**: `_tests/test_*.py` (integration, composition, laws)

---

## Success Criteria

1. Zero regressions (all existing tests pass)
2. Confidence scoring (all parsers return meaningful confidence)
3. Composition works (Fallback/Fusion/Switch demonstrated)
4. Streaming support (parse_stream implemented)
5. Graceful degradation (no exceptions on malformed input)
6. Transparency (repairs tracked)
7. Bootstrappable (regenerate from spec)

---

## References

### Empirical Sources (kgents)
- `impl/claude/agents/p/`: Reference implementation
- `impl/claude/agents/shared/ast_utils.py`: AST utilities
- `impl/claude/runtime/json_utils.py`: Robust JSON parsing

### Theoretical Foundations
- **Stochastic-Structural Gap**: LLM probability distributions vs deterministic parsers
- **Prevention → Correction → Novel**: Architectural spectrum
- **Probabilistic parsing**: Treat output as distribution, not program
- **Graceful degradation**: Partial correctness with confidence

### Frontier Research
- **CFG Logit Masking**: [Outlines](https://github.com/outlines-dev/outlines), [Guidance](https://github.com/guidance-ai/guidance)
- **Fill-in-the-Middle**: [CodeLlama](https://arxiv.org/abs/2308.12950)
- **Jsonformer**: [Structured Generation](https://github.com/1rgs/jsonformer)
- **Reflection**: [Self-Refine](https://arxiv.org/abs/2303.17651), [ReAct](https://arxiv.org/abs/2210.03629)

---

**End of P-gents Specification v3.0**

*Compressed from 1,568 lines to 300 lines (81% compression). Implementation regenerates from this spec.*
