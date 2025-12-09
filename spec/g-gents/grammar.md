# Grammar Synthesis

**Status**: Specification v1.0
**Purpose**: Define how G-gents synthesize grammars from domain intent

---

## The Three Grammar Levels

G-gents produce grammars at three levels of complexity:

### Level 1: Schema (Structured Output)

**Target**: JSON-Schema / Pydantic models
**Complexity**: O(1) parse (field validation)
**Use Case**: Structured data extraction

```python
@dataclass
class SchemaGrammar:
    """Level 1: Structured output constraints."""
    fields: dict[str, FieldSpec]
    required: list[str]
    validators: list[Validator]

    def to_pydantic(self) -> type[BaseModel]:
        """Generate Pydantic model from schema."""
        ...

    def to_json_schema(self) -> dict:
        """Generate JSON Schema."""
        ...

# Example synthesis
schema = await g_gent.synthesize_schema(
    domain="User Profile",
    constraints=[
        "Name is required string",
        "Age must be positive integer",
        "Email must be valid format"
    ]
)

# Output
class UserProfile(BaseModel):
    name: str
    age: int = Field(gt=0)
    email: EmailStr
```

**Constraint Encoding**:
- Type constraints → Pydantic field types
- Range constraints → Field validators
- Format constraints → Pydantic types (EmailStr, etc.)
- Required constraints → non-Optional fields

### Level 2: Command (Verb-Noun Imperative)

**Target**: Simple command language
**Complexity**: O(n) parse (linear scan)
**Use Case**: Safe operation interfaces

```python
@dataclass
class CommandGrammar:
    """Level 2: Verb-Noun command sequences."""
    verbs: set[str]           # Allowed operations
    nouns: set[str]           # Allowed targets
    modifiers: set[str]       # Optional modifiers
    syntax: str               # BNF specification

    def compile_parser(self) -> Callable[[str], Command]:
        """Generate command parser."""
        ...

# Example synthesis
command_grammar = await g_gent.synthesize_command(
    domain="File Operations",
    allowed_verbs=["READ", "LIST", "COPY"],
    forbidden_verbs=["DELETE", "MOVE", "MODIFY"],
    targets=["file", "directory"]
)

# Output BNF
"""
CMD ::= VERB TARGET MODIFIER*
VERB ::= "READ" | "LIST" | "COPY"
TARGET ::= "file" PATH | "directory" PATH
MODIFIER ::= "to" PATH | "recursive"
PATH ::= STRING
"""

# Valid: "READ file /tmp/data.txt"
# Valid: "COPY file /src to /dst"
# Invalid: "DELETE file /tmp/data.txt" (VERB 'DELETE' not in grammar)
```

**Constraint Encoding**:
- Operation constraints → VERB production (only allowed verbs)
- Target constraints → NOUN production
- Parameter constraints → MODIFIER rules

### Level 3: Recursive (S-Expression / AST)

**Target**: Full recursive grammar
**Complexity**: O(n log n) to O(n^2) parse (depending on grammar)
**Use Case**: Complex reasoning, query languages

```python
@dataclass
class RecursiveGrammar:
    """Level 3: Full recursive grammar with nesting."""
    productions: dict[str, Production]
    start_symbol: str
    terminals: set[str]
    operators: set[str]

    def compile_parser(self) -> Callable[[str], AST]:
        """Generate recursive descent or Lark parser."""
        ...

# Example synthesis
recursive_grammar = await g_gent.synthesize_recursive(
    domain="Data Transformation",
    operators=["filter", "map", "reduce", "compose", "project"],
    forbidden=["delete", "mutate", "drop"],
    recursion_limit=5
)

# Output BNF (S-expression style)
"""
EXPR ::= ATOM | "(" OP EXPR* ")"
OP ::= "filter" | "map" | "reduce" | "compose" | "project"
ATOM ::= STRING | NUMBER | SYMBOL | FIELD_REF
FIELD_REF ::= "$" IDENTIFIER
STRING ::= '"' [^"]* '"'
NUMBER ::= [0-9]+
SYMBOL ::= [a-z][a-z0-9_]*
IDENTIFIER ::= [A-Za-z_][A-Za-z0-9_]*
"""

# Valid: (filter (> $age 21) (map $name $users))
# Valid: (compose (filter active) (project name email))
# Invalid: (delete $user) (OP 'delete' not in grammar)
```

**Constraint Encoding**:
- Operator constraints → OP production
- Recursion constraints → depth limit in parser
- Type constraints → ATOM alternatives

---

## Grammar Synthesis Pipeline

### Step 1: Domain Analysis

Extract domain primitives from natural language intent:

```python
@dataclass
class DomainAnalysis:
    """Analysis of a domain for grammar synthesis."""
    entities: list[Entity]        # Nouns (data types)
    operations: list[Operation]   # Verbs (actions)
    relationships: list[Relation] # How entities connect
    constraints: list[Constraint] # What's forbidden/required
    lexicon: set[str]             # Token vocabulary

@dataclass
class Entity:
    name: str
    attributes: list[Attribute]
    cardinality: Cardinality  # ONE, MANY, OPTIONAL

@dataclass
class Operation:
    name: str
    input_types: list[str]
    output_type: str
    side_effects: list[str]  # Empty for pure operations
    allowed: bool            # False if forbidden

async def analyze_domain(
    intent: str,
    examples: list[str] | None,
    constraints: list[str]
) -> DomainAnalysis:
    """
    LLM-powered domain analysis.

    1. Extract entities from intent ("Calendar" → Event, Date, Time)
    2. Extract operations from intent ("manage" → Add, Remove, Check)
    3. Apply constraints (filter operations where allowed=False)
    4. Build lexicon from entity/operation names
    """
```

### Step 2: Grammar Generation

Generate BNF/EBNF from domain analysis:

```python
async def generate_grammar(
    analysis: DomainAnalysis,
    level: GrammarLevel
) -> str:
    """
    Generate grammar specification from domain analysis.

    Level 1 (Schema):
        - Each entity → Pydantic field
        - Constraints → validators

    Level 2 (Command):
        - Operations → VERB production
        - Entities → NOUN production
        - Simple linear syntax

    Level 3 (Recursive):
        - Operations → OP production
        - Entities → ATOM alternatives
        - Full recursive syntax with nesting
    """
    match level:
        case GrammarLevel.SCHEMA:
            return _generate_schema(analysis)
        case GrammarLevel.COMMAND:
            return _generate_command_bnf(analysis)
        case GrammarLevel.RECURSIVE:
            return _generate_recursive_bnf(analysis)

def _generate_command_bnf(analysis: DomainAnalysis) -> str:
    """Generate Level 2 command grammar."""
    allowed_ops = [op for op in analysis.operations if op.allowed]
    verb_alts = " | ".join(f'"{op.name.upper()}"' for op in allowed_ops)
    noun_alts = " | ".join(f'"{e.name.lower()}"' for e in analysis.entities)

    return f"""
CMD ::= VERB NOUN ARGS*
VERB ::= {verb_alts}
NOUN ::= {noun_alts}
ARGS ::= STRING | NUMBER | MODIFIER
MODIFIER ::= PREP NOUN
PREP ::= "to" | "from" | "with" | "by"
STRING ::= '"' [^"]* '"'
NUMBER ::= [0-9]+
"""
```

### Step 3: Ambiguity Verification

Use T-gent to verify grammar is unambiguous:

```python
async def verify_unambiguous(
    grammar: str,
    t_gent: TesterAgent
) -> tuple[bool, list[AmbiguityReport]]:
    """
    Verify grammar has no ambiguity.

    Ambiguity types:
    1. Lexical: Token can be classified multiple ways
    2. Syntactic: Multiple parse trees for same input
    3. Semantic: Same parse tree, multiple interpretations

    Uses T-gent to:
    1. Generate test inputs from grammar (fuzzing)
    2. Parse each input
    3. Detect multiple parse trees
    4. Report ambiguous cases
    """
    # Generate test inputs
    test_inputs = await t_gent.fuzz_grammar(grammar, n=1000)

    # Parse and check for ambiguity
    ambiguities = []
    for input_text in test_inputs:
        parses = parse_all(grammar, input_text)
        if len(parses) > 1:
            ambiguities.append(AmbiguityReport(
                input=input_text,
                parse_count=len(parses),
                parse_trees=parses
            ))

    return len(ambiguities) == 0, ambiguities
```

### Step 4: Grammar Refinement

If ambiguities found, refine grammar:

```python
async def refine_grammar(
    grammar: str,
    ambiguities: list[AmbiguityReport]
) -> str:
    """
    Refine grammar to eliminate ambiguities.

    Strategies:
    1. Priority rules: Earlier alternatives match first
    2. Lookahead: Add context requirements
    3. Factoring: Extract common prefixes
    4. Disambiguation tokens: Add explicit markers
    """
    # Use LLM with ambiguity examples
    refined = await llm.refine_grammar(
        grammar=grammar,
        ambiguities=ambiguities,
        instruction="Modify grammar to eliminate ambiguities while preserving semantics"
    )

    # Verify refinement worked
    is_unambiguous, remaining = await verify_unambiguous(refined)
    if not is_unambiguous:
        raise GrammarRefinementError(f"Could not eliminate {len(remaining)} ambiguities")

    return refined
```

---

## Constraint Crystallization

The key innovation: constraints become **structural**, not runtime.

### Forbidden Operation Encoding

```python
# Traditional (runtime): Check at execution
def execute(command: str):
    if "DELETE" in command:
        raise PermissionError("DELETE not allowed")

# G-gent (structural): Grammar excludes DELETE
# VERB ::= "READ" | "WRITE" | "LIST"  (no DELETE)
# Parser fails before execution is even considered
```

### Constraint Types

| Constraint | Structural Encoding |
|------------|---------------------|
| "No deletes" | Exclude DELETE from VERB production |
| "Read only" | Only include READ operations in grammar |
| "Positive integers" | NUMBER ::= [1-9][0-9]* (exclude 0 and negatives) |
| "Max 3 arguments" | ARGS ::= ARG ARG? ARG? (explicit limit) |
| "No recursion" | Remove self-referential productions |

### Verification Protocol

```python
async def verify_constraints(
    grammar: str,
    constraints: list[str],
    analysis: DomainAnalysis
) -> ConstraintVerification:
    """
    Verify all constraints are structurally encoded.

    For each constraint:
    1. Generate test inputs that would violate constraint
    2. Attempt to parse with generated grammar
    3. Verify parse failure (constraint is structural)

    If any violation parses successfully, constraint is NOT structural.
    """
    violations = []

    for constraint in constraints:
        # Generate violating inputs
        violation_inputs = await generate_violations(constraint, analysis)

        for input_text in violation_inputs:
            result = parse(grammar, input_text)
            if result.success:
                violations.append(ConstraintViolation(
                    constraint=constraint,
                    input=input_text,
                    parse_result=result
                ))

    return ConstraintVerification(
        all_encoded=len(violations) == 0,
        violations=violations
    )
```

---

## Grammar Representation Formats

### BNF (Backus-Naur Form)

Standard context-free grammar notation:

```bnf
<command> ::= <verb> <noun> <arguments>
<verb> ::= "READ" | "WRITE" | "LIST"
<noun> ::= "file" | "directory"
<arguments> ::= <arg> | <arg> <arguments>
<arg> ::= <string> | <number>
```

### EBNF (Extended BNF)

More expressive with repetition and optionality:

```ebnf
command = verb, noun, { argument };
verb = "READ" | "WRITE" | "LIST";
noun = "file" | "directory";
argument = string | number;
```

### Lark Grammar

Python-native grammar format (used by Lark parser):

```python
LARK_GRAMMAR = """
start: command

command: VERB NOUN argument*

VERB: "READ" | "WRITE" | "LIST"
NOUN: "file" | "directory"

argument: STRING | NUMBER

STRING: /"[^"]*"/
NUMBER: /[0-9]+/

%import common.WS
%ignore WS
"""
```

### Pydantic (Level 1)

For schema-level grammars:

```python
from pydantic import BaseModel, Field

class GeneratedModel(BaseModel):
    """Generated from G-gent schema grammar."""
    name: str = Field(min_length=1)
    count: int = Field(gt=0)
    active: bool = True
```

---

## Integration with P-gent

G-gent generates `ParserConfig` for P-gent:

```python
@dataclass
class ParserConfig:
    """Configuration for P-gent parsing."""
    grammar_format: Literal["bnf", "ebnf", "lark", "pydantic"]
    grammar_spec: str
    parser_type: Literal["regex", "lark", "pydantic", "custom"]

    # Confidence heuristics
    base_confidence: float = 0.9
    repair_penalty: float = 0.2

    # Repair strategies
    repair_enabled: bool = True
    repair_strategies: list[str] = field(default_factory=lambda: [
        "balance_brackets",
        "remove_trailing_comma",
        "fix_quotes"
    ])

def generate_parser_config(
    grammar: str,
    level: GrammarLevel
) -> ParserConfig:
    """Generate P-gent configuration from grammar."""
    match level:
        case GrammarLevel.SCHEMA:
            return ParserConfig(
                grammar_format="pydantic",
                grammar_spec=grammar,
                parser_type="pydantic",
                base_confidence=1.0,  # Schema validation is binary
                repair_enabled=False   # Pydantic has own validation
            )
        case GrammarLevel.COMMAND:
            return ParserConfig(
                grammar_format="bnf",
                grammar_spec=grammar,
                parser_type="regex",  # Simple enough for regex
                base_confidence=0.95,
                repair_enabled=True
            )
        case GrammarLevel.RECURSIVE:
            return ParserConfig(
                grammar_format="lark",
                grammar_spec=grammar,
                parser_type="lark",
                base_confidence=0.9,
                repair_enabled=True,
                repair_strategies=[
                    "balance_parentheses",
                    "balance_brackets",
                    "fix_quotes"
                ]
            )
```

---

## Examples

### Example 1: Safe Database Query Language

```python
# Intent
intent = "Query language for user database, read-only, no admin operations"

# Constraints
constraints = [
    "No DELETE, DROP, TRUNCATE",
    "No ALTER, CREATE",
    "No direct table modification",
    "Only SELECT with WHERE/ORDER/LIMIT"
]

# Synthesis
tongue = await g_gent.reify(
    domain="User Queries",
    constraints=constraints,
    level=GrammarLevel.COMMAND
)

# Generated Grammar
"""
QUERY ::= "SELECT" FIELDS "FROM" TABLE WHERE? ORDER? LIMIT?
FIELDS ::= FIELD ("," FIELD)*
FIELD ::= IDENTIFIER | "*"
TABLE ::= "users" | "profiles" | "settings"
WHERE ::= "WHERE" CONDITION
CONDITION ::= FIELD OP VALUE
OP ::= "=" | ">" | "<" | ">=" | "<=" | "LIKE"
VALUE ::= STRING | NUMBER
ORDER ::= "ORDER BY" FIELD ("ASC" | "DESC")?
LIMIT ::= "LIMIT" NUMBER
"""

# Valid:
#   SELECT name, email FROM users WHERE age > 21 ORDER BY name LIMIT 10
# Invalid:
#   DROP TABLE users  (not parseable)
#   DELETE FROM users WHERE id = 1  (VERB 'DELETE' doesn't exist)
```

### Example 2: Inter-Agent Protocol

```python
# Intent
intent = "Minimal protocol for agents exchanging research citations"

# Constraints
constraints = [
    "Minimal token usage",
    "Preserve author, year, topic",
    "Support confidence scoring"
]

# Synthesis (Level 1: Schema)
tongue = await g_gent.reify(
    domain="Citation Exchange",
    constraints=constraints,
    level=GrammarLevel.SCHEMA
)

# Generated Pydantic Schema
class Citation(BaseModel):
    author: str = Field(max_length=20)
    year: int = Field(ge=1900, le=2100)
    topic: str = Field(max_length=50)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)

# Usage
# Full English: "I found a paper by Smith et al from 2020 about transformers with high confidence"
# DSL: Citation(author="Smith", year=2020, topic="transformers", confidence=0.95)
# Token savings: ~80%
```

### Example 3: UI Layout DSL

```python
# Intent
intent = "Describe dashboard layouts with grid, widgets, and responsive behavior"

# Constraints
constraints = [
    "Grid-based layout only",
    "Predefined widget types",
    "Max 3 nesting levels"
]

# Synthesis (Level 3: Recursive)
tongue = await g_gent.reify(
    domain="Dashboard Layout",
    constraints=constraints,
    level=GrammarLevel.RECURSIVE
)

# Generated Grammar
"""
LAYOUT ::= CONTAINER | WIDGET
CONTAINER ::= "row(" ELEMENTS ")" | "col(" ELEMENTS ")"
ELEMENTS ::= ELEMENT ("," ELEMENT)*
ELEMENT ::= LAYOUT | WIDGET
WIDGET ::= "Graph" PARAMS? | "Stat" PARAMS? | "Table" PARAMS? | "Text" PARAMS?
PARAMS ::= "{" PARAM ("," PARAM)* "}"
PARAM ::= IDENTIFIER ":" VALUE
"""

# Usage
# row(col(Graph{type:"line"}, Stat{value:42}), col(Table{rows:10}))
# Renders: Two-column layout, left has graph+stat, right has table
```

---

## See Also

- [README.md](README.md) - G-gent overview
- [tongue.md](tongue.md) - Tongue artifact specification
- [safety.md](safety.md) - Constraint verification
- [../p-gents/](../p-gents/) - Parser integration
- [../t-gents/](../t-gents/) - Ambiguity testing

---

*"A grammar is the domain's constitution—it defines what can be said, and by exclusion, what cannot."*
