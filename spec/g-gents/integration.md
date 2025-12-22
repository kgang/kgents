# G-gent Integration Patterns

**Status**: Specification v1.0
**Purpose**: Define how G-gents integrate with the kgents ecosystem

---

## Overview

G-gents don't operate in isolation. They are a **hub** in the kgents ecosystem, connecting:

```
            ┌─────────────┐
            │   L-gent    │ (Discovery)
            │  Librarian  │
            └──────┬──────┘
                   │ register/find
                   │
                   │       ┌──────────┐
                   │◄──────│  W-gent  │
                   │       │ Witness  │
                   ▼       └──────────┘
            ┌─────────────┐
            │   G-gent    │
            │ Grammarian  │
            └──────┬──────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│  P-gent  │ │  J-gent  │ │  T-gent  │
│  Parser  │ │   JIT    │ │  Tester  │
└──────────┘ └──────────┘ └──────────┘
```

---

## P-gent Integration (Parsing)

### The Rosetta Stone Pattern

G-gent creates the language specification; P-gent executes the parsing.

```python
# G-gent creates Tongue with ParserConfig
tongue = await g_gent.reify(
    domain="Calendar",
    constraints=["No deletes"]
)

# P-gent uses the ParserConfig
parser = p_gent.create_parser(tongue.parser_config)
result = parser.parse("CHECK 2024-12-15")
```

### ParserConfig Generation

G-gent generates P-gent configuration based on grammar level:

```python
def generate_parser_config(
    grammar: str,
    level: GrammarLevel,
    constraints: list[str]
) -> ParserConfig:
    """Generate P-gent configuration from grammar."""

    match level:
        case GrammarLevel.SCHEMA:
            # Level 1: Pydantic validation
            return ParserConfig(
                grammar_format="pydantic",
                grammar_spec=grammar,
                parser_type="pydantic",
                base_confidence=1.0,  # Schema is binary
                repair_enabled=False,  # Pydantic handles validation
                repair_strategies=()
            )

        case GrammarLevel.COMMAND:
            # Level 2: Regex or simple tokenizer
            return ParserConfig(
                grammar_format="bnf",
                grammar_spec=grammar,
                parser_type="regex",
                base_confidence=0.95,
                repair_enabled=True,
                repair_strategies=(
                    "normalize_whitespace",
                    "fix_case",
                    "remove_trailing_punct"
                )
            )

        case GrammarLevel.RECURSIVE:
            # Level 3: Full Lark parser
            return ParserConfig(
                grammar_format="lark",
                grammar_spec=grammar,
                parser_type="lark",
                base_confidence=0.9,
                repair_enabled=True,
                repair_strategies=(
                    "balance_parentheses",
                    "balance_brackets",
                    "fix_quotes",
                    "remove_trailing_comma"
                )
            )
```

### Parsing Pipeline

```python
# Full parsing pipeline using G-gent + P-gent

async def parse_dsl(
    text: str,
    tongue: Tongue
) -> ParseResult[AST]:
    """
    Parse DSL text using tongue's parser configuration.

    Flow:
    1. P-gent receives ParserConfig from Tongue
    2. P-gent parses text according to grammar
    3. Returns ParseResult with AST and confidence
    """
    # Get P-gent parser for this tongue
    parser = await p_gent.create_parser(tongue.parser_config)

    # Parse with P-gent's fuzzy coercion
    result = parser.parse(text)

    # Apply tongue-specific post-processing
    if result.success:
        result.value = tongue.post_process(result.value)

    return result
```

---

## J-gent Integration (Execution)

### The Compiler Pattern

G-gent defines the language semantics; J-gent JIT-compiles the interpreter.

```python
# G-gent creates Tongue with InterpreterConfig
tongue = await g_gent.reify(
    domain="Calendar",
    constraints=["No deletes"],
    semantics={
        "CHECK": calendar_api.check,
        "ADD": calendar_api.add
    }
)

# J-gent compiles interpreter
interpreter = await j_gent.compile_interpreter(tongue.interpreter_config)
result = interpreter.execute(ast, context)
```

### InterpreterConfig Generation

```python
def generate_interpreter_config(
    grammar: str,
    semantics: dict[str, Callable],
    constraints: list[str]
) -> InterpreterConfig:
    """Generate J-gent configuration from grammar and semantics."""

    # Analyze operations in grammar
    operations = extract_operations(grammar)

    # Create bindings
    bindings = {}
    for op in operations:
        if op in semantics:
            bindings[op] = f"bindings.{op}"
        else:
            bindings[op] = f"default.{op}"

    return InterpreterConfig(
        interpreter_type="sandbox",  # Always sandbox by default
        operation_bindings=bindings,
        sandbox_enabled=True,
        max_execution_time_ms=10000,
        entropy_budget=1.0,
        required_context=extract_required_context(semantics)
    )
```

### Execution Pipeline

```python
async def execute_dsl(
    ast: AST,
    context: Context,
    tongue: Tongue
) -> Result:
    """
    Execute parsed AST using tongue's interpreter configuration.

    Flow:
    1. J-gent receives InterpreterConfig from Tongue
    2. J-gent classifies reality (DETERMINISTIC/PROBABILISTIC/CHAOTIC)
    3. J-gent executes with entropy budget
    4. Returns Result or collapses to Ground
    """
    # Get J-gent interpreter for this tongue
    interpreter = await j_gent.compile_interpreter(tongue.interpreter_config)

    # Reality classification
    reality = j_gent.classify_reality(ast)

    match reality:
        case Reality.DETERMINISTIC:
            # Direct execution
            return await interpreter.execute(ast, context)

        case Reality.PROBABILISTIC:
            # Execute with entropy budget
            return await interpreter.execute_with_budget(
                ast, context,
                budget=tongue.interpreter_config.entropy_budget
            )

        case Reality.CHAOTIC:
            # Collapse to Ground
            return Result.ground("Execution too complex for safety")
```

---

## L-gent Integration (Discovery)

### The Vocabulary Index Pattern

L-gent catalogs Tongues for ecosystem-wide discovery.

```python
# Register tongue with L-gent
await l_gent.register(
    entity=tongue,
    entity_type=EntityType.TONGUE,
    metadata={
        "domain": tongue.domain,
        "constraints": list(tongue.constraints),
        "level": tongue.level.name,
        "grammar_format": tongue.grammar_format.name
    },
    tags=["calendar", "safe-mutation", "command-level"]
)

# Discover tongues by domain
calendar_tongues = await l_gent.find(
    entity_type=EntityType.TONGUE,
    domain="calendar"
)

# Discover tongues by constraint
safe_tongues = await l_gent.find(
    entity_type=EntityType.TONGUE,
    constraints=["no deletes"]
)

# Check tongue compatibility
compatible = await l_gent.check_compatibility(
    TongueA,
    TongueB
)
# Returns: CompatibilityReport with composition suggestions
```

### Composition Discovery

L-gent helps find composable tongues:

```python
# Find tongues that can be composed
composable = await l_gent.find_composable(
    source_tongue=calendar_tongue,
    composition_type="sequential"
)

# Example: Calendar + Email = Communication workflow
# L-gent suggests: CalendarTongue >> EmailTongue composable
```

---

## W-gent Integration (Pattern Observation)

### The Cryptographer Pattern

W-gent observes unknown patterns; G-gent hypothesizes a grammar.

```python
async def infer_grammar_from_observations(
    observations: list[str],
    w_gent: WitnessAgent,
    g_gent: GrammarianAgent
) -> Tongue:
    """
    Infer a grammar from observed patterns.

    Flow:
    1. W-gent observes patterns in data
    2. G-gent hypothesizes grammar from patterns
    3. T-gent validates grammar
    4. Return inferred Tongue
    """
    # 1. W-gent pattern extraction
    patterns = await w_gent.observe_patterns(observations)
    # patterns = [
    #   Pattern("ref(Author, Year)", frequency=0.8),
    #   Pattern("cite(Author et al, Year)", frequency=0.2)
    # ]

    # 2. G-gent grammar hypothesis
    hypothesized_grammar = await g_gent.hypothesize_grammar(patterns)
    # CITE ::= "ref(" AUTHOR "," YEAR ")" | "cite(" AUTHOR "," YEAR ")"

    # 3. Validation against observations
    validation = await t_gent.validate_grammar(
        hypothesized_grammar,
        test_inputs=observations
    )

    if not validation.all_parse:
        # Refine grammar
        hypothesized_grammar = await g_gent.refine_grammar(
            hypothesized_grammar,
            failed_inputs=validation.failed_inputs
        )

    # 4. Return inferred tongue
    return await g_gent.crystallize(
        grammar=hypothesized_grammar,
        domain="Inferred from observations",
        constraints=[],  # Inferred tongues have no a priori constraints
        source="w-gent-inference"
    )
```

---

## T-gent Integration (Testing)

### The Fuzzer Pattern

T-gent uses grammars for systematic testing.

```python
async def fuzz_tongue(
    tongue: Tongue,
    t_gent: TesterAgent,
    n: int = 1000
) -> FuzzReport:
    """
    Fuzz-test a tongue for robustness.

    T-gent uses grammar to generate:
    1. Valid inputs (should parse)
    2. Invalid inputs (should fail)
    3. Boundary inputs (edge cases)
    4. Constraint violations (should fail structurally)
    """
    # Generate test inputs from grammar
    valid_inputs = await t_gent.generate_valid(tongue.grammar, n=n//2)
    invalid_inputs = await t_gent.generate_invalid(tongue.grammar, n=n//4)
    boundary_inputs = await t_gent.generate_boundary(tongue.grammar, n=n//4)

    results = []

    # Test valid inputs (should parse)
    for input_text in valid_inputs:
        result = tongue.parse(input_text)
        results.append(FuzzResult(
            input=input_text,
            expected="success",
            actual="success" if result.success else "failure",
            passed=result.success
        ))

    # Test invalid inputs (should fail)
    for input_text in invalid_inputs:
        result = tongue.parse(input_text)
        results.append(FuzzResult(
            input=input_text,
            expected="failure",
            actual="success" if result.success else "failure",
            passed=not result.success
        ))

    return FuzzReport(
        total=len(results),
        passed=sum(1 for r in results if r.passed),
        failed=[r for r in results if not r.passed]
    )
```

### Property Testing

```python
async def property_test_tongue(
    tongue: Tongue,
    t_gent: TesterAgent
) -> PropertyTestReport:
    """
    Property-based testing for tongue invariants.

    Properties:
    1. Round-trip: parse(render(ast)) == ast
    2. Idempotence: parse(text) == parse(parse_then_render(text))
    3. Constraint encoding: forbidden inputs don't parse
    """
    # Property 1: Round-trip
    @t_gent.property_test
    async def round_trip(input_text: str):
        result = tongue.parse(input_text)
        if result.success:
            rendered = tongue.render(result.value)
            result2 = tongue.parse(rendered)
            assert result.value == result2.value

    # Property 2: Constraint encoding
    @t_gent.property_test
    async def constraints_structural(constraint: str):
        violations = await generate_violations(constraint, tongue.domain)
        for violation in violations:
            result = tongue.parse(violation)
            assert not result.success, f"Constraint '{constraint}' not structural"

    return await t_gent.run_properties([round_trip, constraints_structural])
```

---

## H-gent Integration (Dialectic)

### The Dialect Synthesizer Pattern

When tongues conflict, H-gent synthesizes.

```python
async def reconcile_tongues(
    tongue_a: Tongue,
    tongue_b: Tongue,
    h_gent: HegelAgent,
    g_gent: GrammarianAgent
) -> Tongue:
    """
    Reconcile conflicting tongues through dialectic.

    When two tongues serve overlapping domains but have
    different grammars, H-gent identifies tensions and
    G-gent synthesizes a unified tongue.
    """
    # 1. Detect tensions
    tensions = await h_gent.contradict(tongue_a, tongue_b)
    # tensions = [
    #   Tension("TongueA uses SELECT, TongueB uses FIND"),
    #   Tension("TongueA has DELETE, TongueB forbids it")
    # ]

    # 2. For each tension, attempt sublation
    resolutions = []
    for tension in tensions:
        resolution = await h_gent.sublate(tension)

        if resolution.type == "synthesis":
            resolutions.append(resolution.synthesis)
        elif resolution.type == "hold":
            # Tension held—manual resolution needed
            raise TongueConflictError(f"Unresolvable tension: {tension}")

    # 3. G-gent synthesizes unified tongue
    unified = await g_gent.reify(
        domain=f"{tongue_a.domain} + {tongue_b.domain}",
        constraints=list(tongue_a.constraints) + list(tongue_b.constraints),
        resolutions=resolutions
    )

    return unified
```

---

## Cross-Ecosystem Patterns

### Pattern 1: W-gent Discovery → G-gent Formalization

```python
# Observe agent communication patterns, formalize into protocol

# 1. W-gent observes inter-agent messages
observations = await w_gent.observe_traffic(
    agent_a, agent_b,
    duration=timedelta(hours=1)
)
# observations = ["ref(Smith20)", "ack(citation)", "query(topic:ML)"]

# 2. G-gent infers protocol grammar
protocol_tongue = await infer_grammar_from_observations(
    observations, w_gent, g_gent
)

# 3. Formalize: Future communication uses the tongue
agent_a.set_protocol(protocol_tongue)
agent_b.set_protocol(protocol_tongue)

# 4. Now communication is type-safe
# Invalid messages → parse error
```

### Pattern 2: T-gent Adversarial Testing → G-gent Hardening

```python
# Adversarial testing reveals grammar weaknesses

# 1. T-gent generates adversarial inputs
adversarial = await t_gent.generate_adversarial(tongue.grammar)
# adversarial = [
#   "CHECK 9999-99-99",  # Invalid date
#   "ADD '; DROP TABLE;",  # Injection attempt
#   "CHECK " + "A" * 10000  # Buffer overflow
# ]

# 2. Test tongue robustness
for input_text in adversarial:
    result = tongue.parse(input_text)
    if result.success:
        # Grammar vulnerability found
        vulnerabilities.append(input_text)

# 3. G-gent hardens grammar
if vulnerabilities:
    hardened_tongue = await g_gent.harden(
        tongue,
        vulnerabilities=vulnerabilities
    )
    # Grammar now includes:
    # DATE ::= [0-9]{4}-[0-1][0-9]-[0-3][0-9]  # Bounded date
    # STRING ::= [^;'"]{1,100}  # Length-limited, no special chars
```

---

## Integration Summary Table

| Integration | G-gent Role | Other Agent Role | Output |
|-------------|-------------|------------------|--------|
| **G + P** | Generate grammar + ParserConfig | Execute parsing | ParseResult[AST] |
| **G + J** | Generate semantics + InterpreterConfig | JIT compile & execute | Result |
| **G + L** | Produce Tongue artifact | Catalog for discovery | Registered Tongue |
| **G + W** | Formalize observed patterns | Observe raw patterns | Inferred Tongue |
| **G + T** | Provide grammar for testing | Fuzz & property test | Test Report |
| **G + H** | Synthesize reconciled grammar | Detect & resolve tensions | Unified Tongue |

---

## See Also

- [README.md](README.md) - G-gent overview
- [tongue.md](tongue.md) - Tongue artifact
- [../p-gents/](../p-gents/) - Parser agents
- [../j-gents/](../j-gents/) - JIT agents
- [../l-gents/](../l-gents/) - Librarian agents

---

*"G-gent is the ecosystem's linguist—it doesn't just create languages, it integrates them into the fabric of agent communication."*
