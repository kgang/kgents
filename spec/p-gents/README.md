# P-gents: Parser Agents

**Status**: Specification v4.0 (Unified Vision)
**Session**: 2025-12-25 - The Parsing Renaissance
**Epigraph**: *"Every LLM whispers probabilities. P-gent translates that whisper into guarantees."*

---

## Purpose

P-gents bridge the **stochastic-structural gap**: LLMs produce probability distributions over token sequences. Compilers and renderers demand deterministic syntactic structures. Traditional parsers fail on LLM outputs because they expect deterministic programs. P-gents accept fuzzy text, return confidence-scored results, and compose into robust parsing pipelines.

**The Reliability Mandate**: P-gents exist to increase the reliability of agent outputs at three levels:
1. **Heuristic**: Battle-tested repair strategies that fix common LLM output errors
2. **Prompting**: Prompt-engineering patterns that prevent malformed outputs at generation time
3. **Theoretical**: Category-theoretic composition that guarantees type-safe transformations

---

## Core Insight

> **The Stochastic-Structural Gap**: LLMs don't "know" syntax—they sample from learned distributions. Standard parsers crash on unclosed brackets, trailing commas, malformed nesting, and format drift. P-gents operate across the **Prevention ← → Correction ← → Novel** spectrum to handle this gracefully.

### The Translation Function

P-gent IS translation. Every P-gent operation translates between domains:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE P-GENT TRANSLATION STACK                          │
│                                                                              │
│   Raw LLM Output  ────►  ParseResult[A]  ────►  Human-Understandable        │
│   (token stream)         (confidence +          OR                           │
│                          metadata)              Machine-Interpretable        │
│                                                                              │
│   "Parsing" = Translation with Transparency                                  │
│   Every translation records: what was repaired, confidence level, strategy  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Philosophy

**Fuzzy coercion without opinion**

- **Prevention**: Constrain generation (CFG masking, FIM sandwich)
- **Correction**: Repair outputs (stack-balancing, reflection loops)
- **Novel**: Reframe the problem (diff-based patching, anchor extraction)

**The dual nature**:
- Traditional: Exact syntax → AST (binary: success or exception)
- P-genting: Fuzzy text → ParseResult[A] (graduated: confidence ∈ [0.0, 1.0])

**The Accursed Share of Parsing**:
> Some LLM outputs are slop. P-gents cherish that slop—extracting value even from malformed chaos. Failed parses are composted into training data; partial parses are gratitude for the generative process.

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

## The Harness Pattern: P-gent + Tool Faceting

> *"P-gents trivially supercharge agents by faceting them into arbitrary harnesses or to use arbitrary tools."*

### The Faceting Insight

Any tool can be **faceted** through a P-gent to gain reliability guarantees:

```python
# Without P-gent faceting: fragile, breaks on malformed output
result = await tool.invoke(input)
data = json.loads(result)  # 💥 Crashes on invalid JSON

# With P-gent faceting: robust, graceful degradation
faceted_tool = FacetedTool(
    tool=tool,
    parser=FallbackParser(
        JsonParser(),           # Try strict first
        ReflectionParser(...),  # LLM fixes errors
        AnchorBasedParser(...), # Extract key-value pairs
    )
)
result = await faceted_tool.invoke(input)  # Always returns ParseResult[A]
```

### Harness Integration

P-gents integrate with the Exploration Harness (see `spec/protocols/exploration-harness.md`):

```python
class ParsedNavigationResult:
    """Navigation result parsed with confidence tracking."""
    graph: Optional[ContextGraph]
    parse_result: ParseResult[NavigationData]
    evidence_strength: str  # "weak", "moderate", "strong"

# The harness witnesses parsing attempts
async def navigate_with_parsing(
    harness: ExplorationHarness,
    edge: str,
    parser: Parser[NavigationData]
) -> ParsedNavigationResult:
    raw = await harness.navigate(edge)
    parsed = parser.parse(raw.data)

    # Trail records parsing as evidence
    harness.evidence_collector.record_parse(
        input=raw.data,
        output=parsed,
        confidence=parsed.confidence
    )

    return ParsedNavigationResult(
        graph=raw.graph if raw.success else None,
        parse_result=parsed,
        evidence_strength=harness.classify_evidence_strength(parsed.confidence)
    )
```

### U-gent Tool Integration (Parser-Tool Codesign)

Every U-gent tool is **co-designed with its parser** (see `spec/u-gents/tool-use.md` §Principle 2):

```python
@tool(
    name="hypothesis_generator",
    parser=FallbackParser(
        PydanticParser(HypothesisOutput),
        AnchorBasedParser(anchor="###HYPOTHESIS:"),
        ReflectionParser(...)
    )
)
class HypothesisGeneratorTool(Tool[HypothesisRequest, HypothesisOutput]):
    async def invoke(self, input: HypothesisRequest) -> ParseResult[HypothesisOutput]:
        response = await self.llm.generate(prompt=build_prompt(input))
        return await self.parser.parse(response)  # Always returns ParseResult
```

**Four Parsing Boundaries in Tool Use**:
1. **Schema Parsing**: Tool definitions → Structured schemas
2. **Input Parsing**: Natural language → Tool parameters
3. **Output Parsing**: Tool response → Structured data (P-gent core)
4. **Error Parsing**: Tool errors → Recoverable/Fatal classification

---

## Visual Experience Design

> *"Steward the experience of delight"*

### The P-gent Visual Metaphor: The Translation Lens

P-gent visualization should feel like looking through a **lens** that reveals hidden structure:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE TRANSLATION LENS                                 │
│                                                                              │
│   ┌──────────────┐                                ┌──────────────┐          │
│   │ Raw Output   │    ╔══════════════════╗       │ Parsed Value │          │
│   │              │───►║  P-GENT LENS     ║──────►│              │          │
│   │ {"name: ...  │    ║                  ║       │ {name: "ok"} │          │
│   │  malformed   │    ║  Confidence: 87% ║       │ ✓ validated  │          │
│   └──────────────┘    ╚══════════════════╝       └──────────────┘          │
│                              │                                              │
│                              ▼                                              │
│                     ┌─────────────────┐                                     │
│                     │ Repair Trace:   │                                     │
│                     │ • Added quote   │                                     │
│                     │ • Fixed bracket │                                     │
│                     └─────────────────┘                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Visual States

| State | Visual | Meaning |
|-------|--------|---------|
| **Parsing** | Pulsing lens animation | Active translation in progress |
| **High Confidence** (>0.8) | Green glow, solid lens | Reliable parse, trust result |
| **Medium Confidence** (0.5-0.8) | Amber glow, translucent lens | Usable with caution |
| **Low Confidence** (<0.5) | Red glow, fractured lens | Review carefully |
| **Streaming** | Flowing particles through lens | Real-time translation |
| **Repair Applied** | Sparkle effect + repair badge | Automatic fix was applied |

### Three-Mode Responsive Pattern

Following the elastic-ui-patterns (see `docs/skills/elastic-ui-patterns.md`):

**Compact Mode** (CLI, Mobile):
```
Parsed: ✓ 87% | Repairs: 2 | Strategy: fallback[1]:anchor
```

**Comfortable Mode** (Web Dashboard):
```
┌─────────────────────────────────────────────────────────────────┐
│ 🔍 Parse Result                                    Confidence: 87% │
│─────────────────────────────────────────────────────────────────│
│ Strategy: fallback[1]:anchor-based                               │
│ Repairs:  ✓ Added missing quote (line 3)                         │
│           ✓ Closed unclosed bracket (line 7)                     │
│ Partial:  No                                                     │
│ Stream:   Position 1,247                                         │
│─────────────────────────────────────────────────────────────────│
│ Value: {"name": "hypothesis", "confidence": 0.92}                │
└─────────────────────────────────────────────────────────────────┘
```

**Spacious Mode** (Studio):
Full translation lens visualization with:
- Side-by-side raw/parsed comparison
- Confidence heat map over parsed fields
- Strategy waterfall (which strategies tried, why they failed/succeeded)
- Repair animation (replay the repair steps)
- Streaming progress indicator
- Probabilistic AST tree view (per-node confidence)

### Joy-Inducing Moments

**1. The "Save" Counter**
Track how many errors P-gent caught and fixed:
```
💫 P-gent has saved 1,247 parse failures today
```

**2. Confidence Celebration**
When confidence > 0.95, brief confetti effect:
```
🎉 Perfect parse! (99% confidence, no repairs needed)
```

**3. The Repair Story**
Show repairs as a narrative, not a list:
```
"Found malformed JSON → Added 2 missing brackets → Quoted 3 keys → Result valid!"
```

**4. Strategy Waterfall**
Visualize fallback chain as a cascade:
```
╔═══════════════════════════════════════════════════════════════╗
║ Strategy Waterfall                                             ║
║                                                                ║
║ strict_json ─✗─▶ stack_balance ─✗─▶ reflection ─✓─▶ Success!  ║
║     │                 │                 │            87%       ║
║     ▼                 ▼                 ▼                      ║
║ "Expected }     "Unclosed [        "Fixed via                  ║
║  at line 3"      at line 7"         LLM reflection"            ║
╚═══════════════════════════════════════════════════════════════╝
```

### Portal Token Integration

P-gent results can be represented as Portal Tokens (see `spec/protocols/portal-token.md`):

```tsx
// ParseResultToken: collapsed view of parse result
<PortalToken
    icon="🔍"
    label="Parse Result"
    summary="87% | 2 repairs"
    expandedContent={<ParseResultDetail result={result} />}
    contextType="parse_result"
    expandable={true}
/>
```

When expanded, the token reveals:
- Full strategy trace
- Repair list with line numbers
- Before/after diff
- Confidence explanation
- Re-parse action button

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

## AGENTESE Integration

P-gents expose parsing capabilities via AGENTESE paths:

### Context: `self.parse.*`

| Path | Aspect | Description |
|------|--------|-------------|
| `self.parse.manifest` | GET | Current parser configuration and stats |
| `self.parse.invoke` | POST | Parse text with configured strategy |
| `self.parse.stream` | STREAM | Parse token stream with live results |
| `self.parse.configure` | PATCH | Update parser configuration |
| `self.parse.history` | GET | Recent parse attempts with results |
| `self.parse.strategies` | GET | Available parsing strategies |

### Context: `concept.parse.*`

| Path | Aspect | Description |
|------|--------|-------------|
| `concept.parse.json` | GET | JSON parsing strategy catalog |
| `concept.parse.html` | GET | HTML parsing strategy catalog |
| `concept.parse.code` | GET | Code parsing strategy catalog |
| `concept.parse.compose` | POST | Compose strategies into pipeline |

### Usage Example

```python
# Via AGENTESE
parse_result = await logos.invoke(
    "self.parse.invoke",
    observer=agent_umwelt,
    text=llm_output,
    strategy="fallback:json,anchor,reflection"
)

# The observer sees what they need
# Developer sees: full trace, confidence breakdown, repair details
# End user sees: clean result or human-readable error
```

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

### ❌ Parsing Without Witness
```python
# BAD: No trace of what happened
result = parse(text)

# GOOD: Witnessed parsing with evidence
result = parser.parse(text)
await witness.mark(
    action="parsed_llm_output",
    result=result.success,
    confidence=result.confidence,
    repairs=result.repairs
)
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

### T-gent (Probe Integration)
```python
# P-gent parsing tested via T-gent patterns
flaky_parser = FlakyParser(wrapped=json_parser, probability=0.1)
chaos_result = await flaky_parser.parse(test_input)
# Verify graceful degradation under chaos
```

---

## Laws & Invariants

1. **Graceful Degradation**: P-gents NEVER throw exceptions on malformed input
2. **Transparency**: All repairs tracked in `ParseResult.repairs`
3. **Confidence Monotonicity**: Sequential operations reduce confidence (multiply)
4. **Minimal Output**: Parser extracts ONE `A`, not `[A]` (compose at pipeline level)
5. **Heterarchical Duality**: Parsers support both functional (`parse`) and autonomous (`parse_stream`) modes
6. **Witness Integration**: All parsing operations can emit witness marks

---

## PolyAgent Formalization

P-gent as a PolyAgent (see `spec/agents/primitives.md`):

```python
PARSE: PolyAgent[ParseState, (str, ParserConfig), ParseResult[A]]
    positions: {IDLE, PARSING, REFLECTING, SUCCEEDED, FAILED}
    directions: λs → {(str, ParserConfig)} if s in {IDLE, REFLECTING} else {}
    transition: λ(s, (text, config)) → (new_state, ParseResult[A])
```

**State Machine**:
```
IDLE --[text]--> PARSING
PARSING --[success]--> SUCCEEDED
PARSING --[failure, retries < max]--> REFLECTING
PARSING --[failure, retries >= max]--> FAILED
REFLECTING --[fix attempt]--> PARSING
```

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
8. **Visual delight** (translation lens metaphor implemented)
9. **Harness integration** (works with exploration-harness.md)
10. **Tool faceting** (U-gent tools can be faceted through P-gent)

---

## References

### Empirical Sources (kgents)
- `impl/claude/agents/p/`: Reference implementation
- `impl/claude/agents/shared/ast_utils.py`: AST utilities
- `impl/claude/runtime/json_utils.py`: Robust JSON parsing
- `spec/protocols/exploration-harness.md`: Harness integration
- `spec/u-gents/tool-use.md`: Tool use parsing patterns

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

**End of P-gents Specification v4.0**

*Evolved from 426 lines to 600 lines (new: visual experience, harness integration, AGENTESE paths, tool faceting). Implementation regenerates from this spec.*
