# Tongue: The Reified Language Artifact

**Status**: Specification v1.0
**Purpose**: Define the Tongue artifact structure and lifecycle

---

## Overview

A **Tongue** is a reified language—a first-class artifact containing everything needed to parse and execute a domain-specific language:

```
Tongue = Grammar + Parser + Interpreter + Metadata
```

Unlike traditional language implementations scattered across files, a Tongue is a **single, versioned, portable artifact**.

---

## Tongue Structure

```python
from dataclasses import dataclass, field
from typing import Callable, Protocol

@dataclass(frozen=True)
class Tongue:
    """
    A reified domain-specific language.

    The output of G-gent: a complete language artifact
    that can be used by P-gent (parsing) and J-gent (execution).
    """

    # Identity
    name: str                           # e.g., "CalendarTongue"
    version: str                        # Semantic version
    domain: str                         # Domain this tongue serves
    mime_type: str                      # e.g., "application/vnd.kgents.calendar"

    # Grammar
    grammar: str                        # BNF/EBNF/Lark specification
    grammar_format: GrammarFormat       # BNF, EBNF, LARK, PYDANTIC
    level: GrammarLevel                 # SCHEMA, COMMAND, RECURSIVE

    # Lexicon
    lexicon: frozenset[str]             # Allowed tokens
    reserved: frozenset[str]            # Reserved keywords
    forbidden: frozenset[str]           # Explicitly forbidden tokens

    # Integration
    parser_config: ParserConfig         # P-gent configuration
    interpreter_config: InterpreterConfig  # J-gent configuration

    # Constraints
    constraints: tuple[str, ...]        # Original constraint specifications
    constraint_proofs: tuple[ConstraintProof, ...]  # Verification proofs

    # Examples
    examples: tuple[Example, ...]       # Concrete usage examples
    counter_examples: tuple[CounterExample, ...]  # Invalid inputs

    # Provenance
    created_at: datetime
    created_by: str                     # G-gent instance or human
    lineage: TongueLineage | None       # Parent tongue if evolved

    def parse(self, text: str) -> ParseResult[AST]:
        """Parse text using this tongue's grammar."""
        parser = self._get_parser()
        return parser.parse(text)

    def execute(self, ast: AST, context: Context) -> Result:
        """Execute parsed AST using this tongue's interpreter."""
        interpreter = self._get_interpreter()
        return interpreter.execute(ast, context)

    def validate(self, text: str) -> ValidationResult:
        """Validate text against grammar without execution."""
        result = self.parse(text)
        return ValidationResult(
            valid=result.success,
            errors=[] if result.success else [result.error],
            confidence=result.confidence
        )

    def render(self, ast: AST) -> str:
        """Render AST back to text (round-trip support)."""
        return self._render(ast)
```

---

## Supporting Types

### Grammar Formats

```python
from enum import Enum

class GrammarFormat(Enum):
    """Supported grammar specification formats."""
    BNF = "bnf"           # Backus-Naur Form
    EBNF = "ebnf"         # Extended BNF
    LARK = "lark"         # Lark parser format
    PYDANTIC = "pydantic" # Pydantic model (schema level)
    REGEX = "regex"       # Simple regex (very simple DSLs)

class GrammarLevel(Enum):
    """Grammar complexity levels."""
    SCHEMA = 1      # Structured output (JSON/Pydantic)
    COMMAND = 2     # Verb-Noun imperative
    RECURSIVE = 3   # Full recursive grammar
```

### Parser Configuration

```python
@dataclass(frozen=True)
class ParserConfig:
    """Configuration for P-gent parsing."""
    parser_type: Literal["pydantic", "regex", "lark", "custom"]
    grammar_spec: str

    # Confidence
    base_confidence: float = 0.9
    repair_penalty: float = 0.2

    # Repair
    repair_enabled: bool = True
    repair_strategies: tuple[str, ...] = ()

    # Performance
    cache_enabled: bool = True
    timeout_ms: int = 5000
```

### Interpreter Configuration

```python
@dataclass(frozen=True)
class InterpreterConfig:
    """Configuration for J-gent interpretation."""
    interpreter_type: Literal["builtin", "jit", "sandbox"]

    # Semantic bindings
    operation_bindings: dict[str, str]  # Operation name → handler reference

    # Safety
    sandbox_enabled: bool = True
    max_execution_time_ms: int = 10000
    entropy_budget: float = 1.0

    # Context
    required_context: tuple[str, ...] = ()  # Required context keys
```

### Constraint Proofs

```python
@dataclass(frozen=True)
class ConstraintProof:
    """Proof that a constraint is structurally encoded."""
    constraint: str                 # Original constraint text
    encoding: str                   # How it's encoded in grammar
    verification_method: str        # How it was verified
    test_inputs: tuple[str, ...]    # Inputs that would violate
    all_rejected: bool              # All violations caused parse failure
```

### Examples

```python
@dataclass(frozen=True)
class Example:
    """Positive example of valid DSL usage."""
    input: str                      # DSL text
    expected_ast: str | None        # Expected parse result (optional)
    expected_output: str | None     # Expected execution result (optional)
    description: str                # Human-readable explanation

@dataclass(frozen=True)
class CounterExample:
    """Negative example of invalid DSL usage."""
    input: str                      # Invalid DSL text
    expected_error: str             # Expected error type
    violated_constraint: str        # Which constraint this violates
    description: str                # Why this should fail
```

### Lineage

```python
@dataclass(frozen=True)
class TongueLineage:
    """Provenance tracking for tongue evolution."""
    parent_name: str
    parent_version: str
    evolution_type: Literal["extend", "restrict", "refactor", "merge"]
    changes: tuple[str, ...]        # Description of changes
```

---

## Tongue Lifecycle

### 1. Creation (via G-gent)

```python
# User intent
tongue = await g_gent.reify(
    domain="Calendar Management",
    constraints=["No deletes", "No overwrites"],
    examples=["CHECK 2024-12-15", "ADD 14:00 1h Meeting"]
)

# G-gent synthesizes:
# 1. Domain analysis
# 2. Grammar generation
# 3. Ambiguity verification
# 4. Constraint verification
# 5. Parser/interpreter configuration
# 6. Tongue crystallization
```

### 2. Registration (via L-gent)

```python
# Register with ecosystem
await l_gent.register(
    tongue,
    tags=["calendar", "safe-mutation", "command-level"],
    metadata={
        "author": "g-gent-01",
        "use_case": "Calendar management without destructive operations"
    }
)

# Now discoverable
found = await l_gent.find(domain="calendar", constraints=["no deletes"])
# Returns: [CalendarTongue_v1]
```

### 3. Usage (via P-gent + J-gent)

```python
# Parse
parse_result = tongue.parse("CHECK 2024-12-15")
# ParseResult(success=True, value=AST(...), confidence=0.95)

# Execute
context = CalendarContext(api_key="...")
result = tongue.execute(parse_result.value, context)
# Result(events=[...])

# Pipeline composition
pipeline = tongue.parse >> tongue.execute
result = await pipeline("ADD 14:00 1h Team Meeting")
```

### 4. Evolution

```python
# Extend existing tongue
calendar_v2 = await g_gent.evolve(
    parent=tongue,
    evolution_type="extend",
    changes=["Add MOVE operation (with confirmation)"]
)

# calendar_v2.lineage points to tongue v1
# calendar_v2.version = "2.0.0" (breaking: new operation)
```

### 5. Deprecation

```python
# Mark as deprecated
await l_gent.deprecate(
    tongue,
    reason="Replaced by CalendarTongue_v2",
    successor="CalendarTongue_v2"
)

# Queries return successor
found = await l_gent.find(domain="calendar")
# Returns: [CalendarTongue_v2] (with deprecation notice for v1)
```

---

## Serialization Format

Tongues serialize to JSON for storage and transmission:

```json
{
  "name": "CalendarTongue",
  "version": "1.0.0",
  "domain": "Calendar Management",
  "mime_type": "application/vnd.kgents.calendar",

  "grammar": "CMD ::= \"CHECK\" DATE | \"ADD\" EVENT\nEVENT ::= TIME DURATION TITLE\n...",
  "grammar_format": "bnf",
  "level": "command",

  "lexicon": ["CHECK", "ADD", "DATE", "TIME", "DURATION", "TITLE"],
  "reserved": ["CHECK", "ADD"],
  "forbidden": ["DELETE", "REMOVE", "CLEAR", "DROP"],

  "parser_config": {
    "parser_type": "regex",
    "base_confidence": 0.95,
    "repair_enabled": true
  },

  "interpreter_config": {
    "interpreter_type": "sandbox",
    "sandbox_enabled": true,
    "operation_bindings": {
      "CHECK": "calendar.check_date",
      "ADD": "calendar.add_event"
    }
  },

  "constraints": [
    "No deletes",
    "No overwrites"
  ],
  "constraint_proofs": [
    {
      "constraint": "No deletes",
      "encoding": "VERB excludes DELETE/REMOVE/CLEAR",
      "verification_method": "grammar_analysis",
      "test_inputs": ["DELETE meeting", "REMOVE 14:00", "CLEAR Friday"],
      "all_rejected": true
    }
  ],

  "examples": [
    {
      "input": "CHECK 2024-12-15",
      "expected_output": "List of events on 2024-12-15",
      "description": "Check events for a specific date"
    }
  ],
  "counter_examples": [
    {
      "input": "DELETE meeting",
      "expected_error": "ParseError",
      "violated_constraint": "No deletes",
      "description": "DELETE verb not in grammar"
    }
  ],

  "created_at": "2024-12-09T10:30:00Z",
  "created_by": "g-gent-01",
  "lineage": null
}
```

---

## Tongue Operations

### Composition

Two tongues can be composed if their domains are compatible:

```python
# Compose two tongues into one
combined = await g_gent.compose(
    TongueA,  # Calendar operations
    TongueB,  # Email operations
    name="CommunicationTongue"
)

# Grammar combines:
# CMD ::= CALENDAR_CMD | EMAIL_CMD
# CALENDAR_CMD ::= ... (from TongueA)
# EMAIL_CMD ::= ... (from TongueB)
```

### Restriction

Create a more constrained version:

```python
# Restrict existing tongue
readonly_calendar = await g_gent.restrict(
    tongue,
    additional_constraints=["No ADD operations"],
    name="ReadOnlyCalendarTongue"
)

# Grammar now only has CHECK
# CMD ::= "CHECK" DATE
```

### Extension

Add new capabilities:

```python
# Extend existing tongue
calendar_v2 = await g_gent.extend(
    tongue,
    new_operations=["RESCHEDULE"],
    name="CalendarTongue",
    version="2.0.0"
)

# Grammar adds RESCHEDULE
# CMD ::= "CHECK" DATE | "ADD" EVENT | "RESCHEDULE" EVENT_ID DATE
```

---

## Validation Requirements

A Tongue must pass validation before crystallization:

### 1. Grammar Validation

```python
async def validate_grammar(tongue: Tongue) -> ValidationResult:
    """Verify grammar is well-formed and unambiguous."""
    # Parse grammar specification
    if not is_valid_grammar(tongue.grammar, tongue.grammar_format):
        return ValidationResult(valid=False, errors=["Invalid grammar syntax"])

    # Check for ambiguity
    ambiguities = await find_ambiguities(tongue.grammar)
    if ambiguities:
        return ValidationResult(valid=False, errors=[
            f"Ambiguous grammar: {len(ambiguities)} cases found"
        ])

    return ValidationResult(valid=True)
```

### 2. Constraint Validation

```python
async def validate_constraints(tongue: Tongue) -> ValidationResult:
    """Verify all constraints are structurally encoded."""
    for constraint, proof in zip(tongue.constraints, tongue.constraint_proofs):
        # Generate violating inputs
        violations = generate_violations(constraint)

        # All must fail to parse
        for violation in violations:
            result = tongue.parse(violation)
            if result.success:
                return ValidationResult(valid=False, errors=[
                    f"Constraint '{constraint}' not structural: '{violation}' parses"
                ])

    return ValidationResult(valid=True)
```

### 3. Round-Trip Validation

```python
async def validate_round_trip(tongue: Tongue) -> ValidationResult:
    """Verify parse → render → parse produces same AST."""
    for example in tongue.examples:
        # Parse
        result1 = tongue.parse(example.input)
        if not result1.success:
            return ValidationResult(valid=False, errors=[
                f"Example fails to parse: {example.input}"
            ])

        # Render
        rendered = tongue.render(result1.value)

        # Parse again
        result2 = tongue.parse(rendered)
        if not result2.success or result1.value != result2.value:
            return ValidationResult(valid=False, errors=[
                f"Round-trip failed: {example.input} → {rendered}"
            ])

    return ValidationResult(valid=True)
```

### 4. Integration Validation

```python
async def validate_integration(tongue: Tongue) -> ValidationResult:
    """Verify parser and interpreter configs are valid."""
    # P-gent can use parser config
    try:
        parser = p_gent.create_parser(tongue.parser_config)
    except Exception as e:
        return ValidationResult(valid=False, errors=[
            f"Invalid parser config: {e}"
        ])

    # J-gent can use interpreter config
    try:
        interpreter = j_gent.create_interpreter(tongue.interpreter_config)
    except Exception as e:
        return ValidationResult(valid=False, errors=[
            f"Invalid interpreter config: {e}"
        ])

    return ValidationResult(valid=True)
```

---

## Security Considerations

### Forbidden Token Enforcement

The `forbidden` set ensures certain tokens never appear in valid DSL:

```python
# Grammar synthesis must exclude forbidden tokens
def synthesize_grammar(analysis: DomainAnalysis) -> str:
    for operation in analysis.operations:
        if operation.name.upper() in FORBIDDEN_DEFAULTS:
            raise SecurityError(f"Cannot include forbidden operation: {operation.name}")

    # Forbidden tokens: DELETE, DROP, TRUNCATE, EXEC, EVAL, IMPORT, __
```

### Sandbox Execution

All tongue execution runs in sandbox by default:

```python
# Interpreter config enforces sandbox
InterpreterConfig(
    sandbox_enabled=True,  # Required for untrusted input
    max_execution_time_ms=10000,
    entropy_budget=1.0  # J-gent entropy limit
)
```

### Provenance Tracking

All tongues track creation and evolution:

```python
# Every tongue knows its origin
tongue.created_by  # Who/what created it
tongue.created_at  # When
tongue.lineage     # Parent if evolved
```

---

## Performance Considerations

### Caching

```python
# Parser caching (enabled by default)
ParserConfig(cache_enabled=True)

# Parsed results cached by input hash
# Grammar compilation cached by grammar hash
```

### Lazy Loading

```python
# Parser/interpreter instantiated on first use
def _get_parser(self) -> Parser:
    if self._parser is None:
        self._parser = create_parser(self.parser_config)
    return self._parser
```

### Complexity Bounds

```python
# Grammar complexity limits
MAX_PRODUCTIONS = 50
MAX_RECURSION_DEPTH = 5
MAX_ALTERNATIVES = 10

# Validation enforces limits
if count_productions(grammar) > MAX_PRODUCTIONS:
    raise ComplexityError("Grammar too complex")
```

---

## See Also

- [README.md](README.md) - G-gent overview
- [grammar.md](grammar.md) - Grammar synthesis
- [integration.md](integration.md) - P-gent/J-gent integration
- [../l-gents/catalog.md](../l-gents/catalog.md) - Tongue registration

---

*"A Tongue is not just a parser—it is a complete, portable, verifiable language artifact."*
