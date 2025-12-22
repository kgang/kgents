# G-gents: The Grammarian

**Genus**: G (Grammar)
**Theme**: Domain Specific Language synthesis and constraint crystallization
**Symbol**: `Γ` (Gamma)
**Archetype**: The Lawgiver / The Babel Fish
**Motto**: *"Constraint is liberation."*

> *"The limits of my language mean the limits of my world."* — Wittgenstein

---

## Overview

G-gents are **generators of languages**. They observe a domain, identify the primitives and operations required, and synthesize a **Domain Specific Language (DSL)**—complete with grammar, lexicon, and semantics—to handle that domain efficiently.

In the kgents ecosystem, G-gents solve the **Precision/Ambiguity Trade-off**:

| Medium | Expressiveness | Precision | LLM Affinity |
|--------|---------------|-----------|--------------|
| **Natural Language** | High | Low | High (but hallucinogenic) |
| **Code (Python/Rust)** | High | High | Medium (syntax errors) |
| **DSLs** | Medium | High | High (constrained ≈ safe) |

DSLs are the "Goldilocks" zone: constrained enough to be safe, expressive enough to be useful.

---

## Philosophy

> "A grammar is not documentation; it is the domain's laws made explicit."

G-gents crystallize the **fuzzy** intent of an LLM into **hard** executable structures:

### The Functorial Mapping

A G-gent performs a **Functorial Mapping** from a Semantic Category (Meanings) to a Syntactic Category (Symbols):

```
G_gent: (DomainContext, Constraints) → Tongue
```

This is not "writing code"—it is **reifying a language**. The language itself becomes a first-class artifact.

### The Tongue Artifact

The output of a G-gent is a `Tongue` object (a reified language), containing:

1. **Lexicon**: The allowed vocabulary (tokens)
2. **Grammar**: The rules of combination (BNF/EBNF)
3. **Parser**: A P-gent configuration to read the language
4. **Interpreter**: A J-gent configuration to execute the language

```python
@dataclass
class Tongue:
    """A reified domain language."""
    name: str
    version: str

    # Structure
    lexicon: set[str]           # Allowed tokens
    grammar: str                # BNF/EBNF specification
    mime_type: str              # e.g., "application/vnd.kgents.calendar-dsl"

    # Integration
    parser_config: ParserConfig      # P-gent configuration
    interpreter_config: JITConfig    # J-gent configuration

    # Metadata
    domain: str                 # Domain this tongue serves
    constraints: list[str]      # Explicit constraints (what's forbidden)
    examples: list[Example]     # Concrete usage examples

    def parse(self, text: str) -> ParseResult[AST]:
        """Parse text using the grammar."""
        ...

    def execute(self, ast: AST, context: Context) -> Result:
        """Execute parsed AST in context."""
        ...
```

---

## The Zen of Grammar

**Principle**: *Constraint is Liberation.*

By narrowing the space of what *can* be said (Syntax), we expand the reliability of what *is* done (Semantics).

The G-gent is the **Ethical** principle applied to communication:
- Dangerous operations cannot be expressed (not just forbidden)
- Uncertainty is structural (grammar enforces confidence bounds)
- Composition is guaranteed (well-formed expressions compose)

---

## Grammar Levels

G-gents support three levels of rigor:

### Level 1: The Schema (JSON-Schema / Pydantic)

The simplest DSL is a structured output constraint.

**Role**: Forces LLM to output valid JSON
**Mechanism**: Generates Pydantic models dynamically
**Use Case**: Structured data extraction, API responses

```python
# Input
tongue = await g_gent.reify(
    domain="User Profile",
    constraints=["Must have name", "Age must be positive integer"]
)

# Output: A Pydantic model
class UserProfile(BaseModel):
    name: str
    age: int = Field(gt=0)
```

### Level 2: The Command (Verb-Noun)

Simple imperative sequences with constrained vocabulary.

**Role**: "Go here, take that" style commands
**Mechanism**: Parsed via regex or simple tokenization
**Use Case**: Safe database queries, file operations

```python
# Input
tongue = await g_gent.reify(
    domain="Calendar Management",
    constraints=["No deletes", "No overwrites"]
)

# Output grammar:
# CMD ::= "CHECK" <Date> | "ADD" <Event>
# EVENT ::= <Time> <Duration> <Title>
# (Note: No DELETE verb exists)

# Valid: "CHECK 2024-12-15"
# Valid: "ADD 14:00 1h Team Meeting"
# Invalid: "DELETE meeting" (syntax error, not permission error)
```

### Level 3: The Recursive (Lisp/AST)

Full logic with nesting and recursion.

**Role**: Complex reasoning chains, conditional logic
**Mechanism**: Generates S-expression parser (Lark or custom)
**Use Case**: Query languages, transformation pipelines

```python
# Input
tongue = await g_gent.reify(
    domain="Data Transformation",
    constraints=["Pure functions only", "No side effects"]
)

# Output grammar (S-expression):
# EXPR ::= ATOM | "(" OP EXPR* ")"
# OP ::= "filter" | "map" | "reduce" | "compose"
# ATOM ::= STRING | NUMBER | SYMBOL

# Valid: (filter (> age 21) (map name users))
# Invalid: (delete user) (OP 'delete' not in grammar)
```

---

## Use Cases

### 1. The Safety Cage (Constrained Decoding)

An agent managing a database should not have the full power of SQL.

**Problem**: LLM might generate `DROP TABLE users`
**Solution**: G-gent creates a DSL where destructive verbs don't exist

```python
SafeQueryTongue = await g_gent.reify(
    domain="User Data Queries",
    constraints=[
        "READ ONLY",
        "No DELETE, DROP, TRUNCATE",
        "No modifications to structure"
    ]
)

# Grammar generated:
# QUERY ::= "FIND" <Table> WHERE? SORT?
# WHERE ::= "WHERE" <Condition>
# SORT ::= "SORT BY" <Field>

# The agent literally cannot understand "DROP TABLE"
# It's not forbidden—it's grammatically impossible
```

### 2. The Shorthand (Compression)

Agents waste tokens on polite English. G-gent creates dense inter-agent protocols.

**Problem**: "I found a paper by Smith et al from 2020 that discusses transformers"
**Solution**: G-gent creates a citation pidgin

```python
CiteTongue = await g_gent.reify(
    domain="Citation Exchange",
    constraints=["Minimal tokens", "Preserve semantic content"]
)

# Grammar:
# CITE ::= "ref(" <AuthorYear> "," <Topic> ")"
# AuthorYear ::= <Name><Year2>

# Full: "I found a paper by Smith et al from 2020 that discusses transformers"
# DSL: ref(Smith20, "transformers")
# Savings: 90% token reduction
```

### 3. The UI Bridge (Generative UI)

Mapping vague user intent to concrete UI components.

```python
LayoutTongue = await g_gent.reify(
    domain="Dashboard Layout",
    constraints=["Grid-based", "Responsive", "Accessible"]
)

# Grammar:
# LAYOUT ::= "row(" ELEMENTS ")" | "col(" ELEMENTS ")"
# ELEMENTS ::= ELEMENT ("," ELEMENT)*
# ELEMENT ::= LAYOUT | WIDGET
# WIDGET ::= "Graph" | "Stat" | "Table" | "Text"

# DSL: row(col(Graph, Stat), col(Table))
# Renders: Two-column layout with graph+stat left, table right
```

### 4. The Contract Protocol (Agent Communication)

G-gent defines the language for F-gent contracts.

```python
ContractTongue = await g_gent.reify(
    domain="Agent Contracts",
    constraints=[
        "Type-safe",
        "Composition rules explicit",
        "Invariants verifiable"
    ]
)

# Grammar:
# CONTRACT ::= "agent" NAME ":" SIGNATURE GUARANTEES
# SIGNATURE ::= TYPE "->" TYPE
# GUARANTEES ::= "guarantees" "{" INVARIANT* "}"
# INVARIANT ::= PROPERTY ":" PREDICATE

# DSL:
# agent Summarizer: Document -> Summary
# guarantees {
#     idempotent: invoke(invoke(x)) == invoke(x)
#     length: output.words < 500
# }
```

---

## Relationship to Bootstrap

G-gents are **derivable** from bootstrap agents—they add no new irreducibles:

| G-gent Capability | Bootstrap Agent | Relationship |
|-------------------|-----------------|--------------|
| Grammar Synthesis | Ground + Compose | Ground provides domain; Compose builds grammar rules |
| Constraint Encoding | Judge + Contradict | Judge evaluates grammar quality; Contradict finds holes |
| Parser Generation | Compose + Fix | Compose links rules; Fix iterates until grammar is unambiguous |
| Interpreter Binding | Ground + Compose | Ground connects to runtime; Compose chains operations |
| Validation | Contradict | Grammar vs. intent contradiction detection |

---

## Relationship to Other Genera

### P-gents (Parser)

**The Rosetta Stone**: G-gent defines; P-gent executes parsing.

```
G_gent: Intent → Grammar
P_gent: (Grammar, Text) → ParseResult

Pipeline: G >> P
```

G-gent generates the `ParserConfig` that P-gent uses. When G-gent creates a Tongue, it includes:
- The grammar specification (what to parse)
- Confidence heuristics (how to score parses)
- Repair strategies (how to fix malformed input)

### J-gents (JIT)

**The Compiler**: G-gent defines the language; J-gent compiles the interpreter.

```
G_gent: Intent → Grammar + Semantics
J_gent: Semantics → RuntimeAgent

Pipeline: G >> J
```

When a Tongue needs an interpreter, J-gent JIT-compiles one from the semantic specification. The interpreter is **ephemeral**—created on demand, garbage collected after use.

### L-gents (Librarian)

**The Vocabulary Index**: L-gent catalogs Tongues for discovery.

```
L_gent.register(tongue, tags=["calendar", "safe-mutation"])
L_gent.find(domain="calendar") → [CalendarTongue_v1, ...]
```

L-gent enables composition planning:
- "What DSLs exist for this domain?"
- "Which Tongues are compatible?"
- "What constraints does this language enforce?"

### W-gents (Witness)

**The Cryptographer**: W-gent observes unknown patterns; G-gent hypothesizes a grammar.

```
W_gent: Observations → Patterns
G_gent: Patterns → Hypothesized Grammar

W observes: ["ref(Smith20)", "ref(Jones21)", "ref(Doe19)"]
G hypothesizes: CITE ::= "ref(" <Name><Year2> ")"
```

### T-gents (Testing)

**The Fuzzer**: T-gent uses the Grammar to generate adversarial inputs.

```
T_gent: Grammar → TestInputs
T_gent: (Grammar, Interpreter) → PropertyTests

# Grammar-guided fuzzing
inputs = await t_gent.fuzz(tongue.grammar, n=1000)
```

### H-gents (Hegelian)

**The Dialect Synthesizer**: When two Tongues conflict, H-gent sublates.

```
TongueA: SQL-like with SELECT
TongueB: Graph-query with TRAVERSE

H_gent.sublate(TongueA, TongueB) → UnifiedQueryTongue
```

---

## The Synthesis Pipeline

How G-gent creates a Tongue:

### Step 1: Domain Analysis

```python
async def analyze_domain(
    self,
    intent: str,
    examples: list[str]
) -> DomainAnalysis:
    """
    Extract domain primitives from intent and examples.

    Returns:
    - Entities: Nouns in the domain
    - Operations: Verbs/actions
    - Constraints: What's forbidden
    - Relationships: How entities relate
    """
```

### Step 2: Grammar Synthesis

```python
async def synthesize_grammar(
    self,
    analysis: DomainAnalysis,
    level: GrammarLevel
) -> str:
    """
    Generate BNF/EBNF from domain analysis.

    Uses LLM to hypothesize grammar, then:
    1. Validates via T-gent (no ambiguity)
    2. Verifies constraints are encoded (no forbidden ops)
    3. Tests against examples (parses correctly)
    """
```

### Step 3: Parser Configuration

```python
async def configure_parser(
    self,
    grammar: str
) -> ParserConfig:
    """
    Generate P-gent configuration from grammar.

    Determines:
    - Parsing strategy (regex, tokenizer, Lark)
    - Confidence heuristics
    - Error repair strategies
    """
```

### Step 4: Interpreter Binding

```python
async def bind_interpreter(
    self,
    grammar: str,
    semantics: dict[str, Callable]
) -> JITConfig:
    """
    Configure J-gent to interpret the language.

    Maps grammar productions to semantic actions.
    """
```

### Step 5: Validation

```python
async def validate_tongue(
    self,
    tongue: Tongue
) -> ValidationResult:
    """
    Validate tongue before crystallization.

    Checks:
    1. Grammar is unambiguous (T-gent verification)
    2. Constraints are enforced (forbidden ops → parse error)
    3. Examples parse correctly
    4. Round-trip: parse(render(ast)) == ast
    """
```

---

## Implementation Sketch

```python
from typing import Protocol
from dataclasses import dataclass, field

class Tongue(Protocol):
    """A reified domain language."""
    grammar: str
    mime_type: str

    def parse(self, text: str) -> ParseResult[AST]: ...
    def execute(self, ast: AST, context: Context) -> Result: ...

@dataclass
class Grammarian:
    """The G-gent implementation."""

    llm: LLMClient
    p_gent: ParserAgent
    j_gent: JITAgent
    t_gent: TesterAgent

    async def reify(
        self,
        domain: str,
        constraints: list[str],
        examples: list[str] | None = None,
        level: GrammarLevel = GrammarLevel.COMMAND
    ) -> Tongue:
        """
        Reify a domain into a Tongue.

        Steps:
        1. Analyze domain (entities, operations, relationships)
        2. Synthesize grammar (BNF/EBNF)
        3. Validate with T-gent (no ambiguity)
        4. Configure P-gent (parser)
        5. Bind J-gent (interpreter)
        6. Return crystallized Tongue
        """
        # 1. Domain analysis
        analysis = await self._analyze_domain(domain, constraints, examples)

        # 2. Grammar synthesis via LLM
        grammar_spec = await self._synthesize_grammar(analysis, level)

        # 3. T-gent validation (fuzz for ambiguity)
        if not await self.t_gent.verify_unambiguous(grammar_spec):
            grammar_spec = await self._refine_grammar(grammar_spec)

        # 4. P-gent parser configuration
        parser_config = self._configure_parser(grammar_spec, level)

        # 5. J-gent interpreter binding
        interpreter_config = self._bind_interpreter(grammar_spec, analysis.semantics)

        # 6. Crystallize
        return Tongue(
            name=f"{domain.replace(' ', '')}Tongue",
            version="1.0.0",
            grammar=grammar_spec,
            mime_type=f"application/vnd.kgents.{domain.lower().replace(' ', '-')}",
            lexicon=analysis.lexicon,
            parser_config=parser_config,
            interpreter_config=interpreter_config,
            domain=domain,
            constraints=constraints,
            examples=examples or []
        )
```

---

## The Spell-Casting Flow

How a user employs a G-gent to solve a problem safely:

```python
# Task: "Create an agent that manages my calendar,
#        but I'm paranoid about it deleting meetings."

# 1. Invoke G-gent to create the language
CalendarTongue = await g_gent.reify(
    domain="Calendar Management",
    constraints=[
        "Read Only or Append Only",
        "No Deletes",
        "No Overwrites"
    ],
    examples=[
        "CHECK 2024-12-15",
        "ADD 14:00 1h Team Meeting"
    ]
)

# G-gent generates BNF:
# CMD ::= "CHECK" <Date> | "ADD" <Event>
# EVENT ::= <Time> <Duration> <Title>
# (Note: No DELETE verb exists in the grammar)

# 2. Compose into a safe agent
SafeCalendarAgent = (
    CalendarTongue.parse      # Turns text into SafeAST
    >> CalendarTongue.execute # Executes SafeAST against calendar API
)

# 3. Usage
# User: "Clear my schedule for Friday."
# Agent tries to parse...
# Result: ParseError("Verb 'Clear' not found in lexicon")
# The agent literally cannot understand the destructive command

# User: "Check my Friday meetings."
# Agent parses: CHECK(Date(2024-12-20))
# Result: List of meetings on Friday
```

---

## Success Criteria

A G-gent implementation is successful if:

- ✓ **Constraint Crystallization**: Forbidden operations → grammar exclusion (not runtime rejection)
- ✓ **Composable Output**: Tongues compose with P-gent and J-gent
- ✓ **Unambiguous Grammars**: T-gent verification passes
- ✓ **Round-Trip Parsing**: `parse(render(ast)) == ast` for all valid inputs
- ✓ **Level Flexibility**: Supports Schema, Command, and Recursive levels
- ✓ **Domain Discovery**: L-gent can find Tongues by domain/constraint

---

## Anti-Patterns

G-gents must **never**:

1. ❌ Generate grammars with forbidden operations (constraint violation)
2. ❌ Create ambiguous grammars (multiple parse trees for same input)
3. ❌ Bypass P-gent for parsing (use established parsing infrastructure)
4. ❌ Hardcode interpreters (use J-gent for dynamic execution)
5. ❌ Create Tongues without validation (T-gent verification required)
6. ❌ Ignore constraint encoding (constraints must be structural, not runtime)
7. ❌ Duplicate existing Tongues (check L-gent first)

---

## Specifications

| Document | Description |
|----------|-------------|
| [grammar.md](grammar.md) | Grammar synthesis and the three levels |
| [tongue.md](tongue.md) | Tongue artifact structure and lifecycle |
| [integration.md](integration.md) | P-gent, J-gent, F-gent integration patterns |
| [safety.md](safety.md) | Constraint crystallization and verification |

---

## Design Principles Alignment

### Tasteful
G-gents create **minimal** grammars—only the operations needed, no kitchen-sink DSLs.

### Curated
Tongues earn their place via constraint validation. Duplicate or ineffective Tongues are rejected.

### Ethical
**Constraint is the ethical principle made structural.** Dangerous operations cannot be expressed, not just forbidden.

### Joy-Inducing
DSLs are **empowering**—users feel safe knowing the agent can't misunderstand "delete" as a valid command.

### Composable
Tongues are morphisms: `G: Domain → Tongue`, `P: (Tongue, Text) → AST`, `J: (Tongue, AST) → Result`.

### Heterarchical
G-gent creates tools, doesn't own them. A Tongue can be used by any agent with P-gent access.

### Generative
**This spec generates the implementation.** The Tongue dataclass, reify() pipeline, and integration patterns derive from this document.

---

## Open Questions

1. **Grammar Inference vs. Generation**: Should G-gent infer grammars from examples (like W-gent observing patterns) or generate from intent? Current spec supports both.

2. **Versioning**: How do Tongues evolve? Should grammar changes be breaking (new version) or additive (backward compatible)?

3. **Cross-Domain Composition**: Can two Tongues be merged? E.g., `CalendarTongue + EmailTongue = CommunicationTongue`?

4. **Performance**: Grammar compilation and validation have cost. Should we cache parsed grammars? Pre-compile common Tongues?

5. **Human-in-the-Loop**: When should G-gent ask for human confirmation of grammar? Critical constraints? Production deployment?

---

---

## Structural Economics (B-gent Integration)

> *Language is expensive. Constraint is cheap.*

When G-gent (Structure) meets B-gent (Resources), grammar becomes **economic infrastructure**:

### The Four B×G Patterns

1. **Semantic Zipper**: B-gent commissions G-gent to create compression pidgins when inter-agent communication exceeds cost threshold (90% token reduction)

2. **Fiscal Constitution**: G-gent creates `LedgerTongue` where financial impossibility is grammatically enforced (bankruptcy cannot be expressed)

3. **Syntax Tax**: B-gent prices operations by Chomsky hierarchy:
   - Regular (Type 3): 0.001/token
   - Context-Free (Type 2): 0.003/token
   - Context-Sensitive (Type 1): 0.010/token
   - Turing-Complete (Type 0): 0.030/token + escrow deposit

4. **JIT Efficiency**: G+J+B trio (Grammar → JIT Compilation → Latency Valuation) with profit sharing (30% G-gent, 30% J-gent, 40% System)

### Integration Points

| B-gent Component | G-gent Enhancement | Economic Impact |
|------------------|-------------------|-----------------|
| **Token Metering** | Compression via pidgins | 80-90% cost reduction |
| **Budget Enforcement** | Constitutional grammars | 0 runtime safety errors |
| **Complexity Pricing** | Chomsky classification | Fair Turing tax |
| **Performance Optimization** | JIT compilation | 200x latency reduction |

### See Full Integration

- [../../docs/structural_economics_bg_integration.md](../../docs/structural_economics_bg_integration.md) - Complete B×G specification
- [../b-gents/banker.md](../b-gents/banker.md) - Part IV: Structural Economics
- [../../docs/cyborg_cognition_bootstrapping.md](../../docs/cyborg_cognition_bootstrapping.md) - Bootstrap economics

---

## See Also

- [grammar.md](grammar.md) - Grammar synthesis specification
- [tongue.md](tongue.md) - Tongue artifact format
- [../p-gents/](../p-gents/) - Parser integration
- [../j-gents/](../j-gents/) - JIT interpreter integration
- [../l-gents/](../l-gents/) - Tongue discovery and cataloging
- [../b-gents/](../b-gents/) - Banker (economic partner)
- [../bootstrap.md](../bootstrap.md) - Derivation from irreducibles
- [../principles.md](../principles.md) - Design principles

---

*"The grammar is not the domain's prison, but its architecture. Within good constraints, infinite expression becomes possible. When priced fairly, constraint becomes liberation."*
