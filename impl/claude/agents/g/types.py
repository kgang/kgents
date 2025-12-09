"""
G-gent Core Types

Foundational types for Domain Specific Language synthesis:
- Tongue: The reified domain language artifact
- GrammarLevel: Levels of rigor (SCHEMA, COMMAND, RECURSIVE)
- GrammarFormat: Output formats (BNF, EBNF, LARK, PYDANTIC)
- Configs: Parser and Interpreter integration
- Proofs: Constraint verification tracking
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Protocol, TypeVar
import hashlib
import json


# ============================================================================
# Grammar Levels & Formats
# ============================================================================


class GrammarLevel(Enum):
    """
    The three levels of grammar rigor.

    SCHEMA: JSON-Schema/Pydantic structured output (simplest)
    COMMAND: Verb-Noun imperative sequences (medium)
    RECURSIVE: Full logic with nesting (Lisp/AST, most expressive)
    """

    SCHEMA = "schema"
    COMMAND = "command"
    RECURSIVE = "recursive"


class GrammarFormat(Enum):
    """
    Output format for the grammar specification.

    PYDANTIC: Python Pydantic model (for SCHEMA level)
    BNF: Backus-Naur Form (classic)
    EBNF: Extended BNF (with *, +, ?)
    LARK: Lark parser grammar (for complex recursive grammars)
    """

    PYDANTIC = "pydantic"
    BNF = "bnf"
    EBNF = "ebnf"
    LARK = "lark"


# ============================================================================
# AST and Parse Result Types
# ============================================================================


T = TypeVar("T")


@dataclass(frozen=True)
class ParseResult:
    """
    Result of parsing text with a Tongue.

    success: Whether parsing succeeded
    ast: The parsed abstract syntax tree (if successful)
    error: Error message (if failed)
    confidence: Confidence score [0.0, 1.0]
    """

    success: bool
    ast: Any | None = None
    error: str | None = None
    confidence: float = 1.0

    def __bool__(self) -> bool:
        return self.success


@dataclass(frozen=True)
class ExecutionResult:
    """
    Result of executing an AST with a Tongue interpreter.

    success: Whether execution succeeded
    value: The execution result value
    error: Error message (if failed)
    side_effects: List of side effects performed
    """

    success: bool
    value: Any | None = None
    error: str | None = None
    side_effects: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.success


# ============================================================================
# Configuration Types
# ============================================================================


@dataclass(frozen=True)
class ParserConfig:
    """
    Configuration for P-gent parser integration.

    strategy: Parsing strategy (regex, tokenizer, lark)
    grammar_format: The format of the grammar
    grammar_spec: The grammar specification text
    confidence_threshold: Minimum confidence to accept parse [0.0, 1.0]
    repair_strategy: How to handle malformed input
    case_sensitive: Whether parsing is case-sensitive
    """

    strategy: str  # "regex" | "tokenizer" | "lark" | "pydantic"
    grammar_format: GrammarFormat
    grammar_spec: str = ""  # The actual grammar text
    confidence_threshold: float = 0.8
    repair_strategy: str = "fail"  # "fail" | "best_effort" | "interactive"
    case_sensitive: bool = True

    # Alias for backward compatibility
    @property
    def format(self) -> GrammarFormat:
        """Alias for grammar_format."""
        return self.grammar_format

    @property
    def parser_strategy(self) -> str | None:
        """Alias for strategy."""
        return self.strategy

    def __post_init__(self):
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError(
                f"confidence_threshold must be in [0.0, 1.0], got {self.confidence_threshold}"
            )


@dataclass(frozen=True)
class InterpreterConfig:
    """
    Configuration for J-gent interpreter integration.

    runtime: Runtime environment (python, isolated, sandboxed)
    semantics: Mapping from grammar productions to semantic actions
    pure_functions_only: Whether to enforce purity (no side effects)
    timeout_ms: Execution timeout in milliseconds
    """

    runtime: str  # "python" | "isolated" | "sandboxed"
    semantics: dict[str, str] = field(
        default_factory=dict
    )  # production -> action mapping
    pure_functions_only: bool = False
    timeout_ms: int = 5000

    def __post_init__(self):
        if self.timeout_ms <= 0:
            raise ValueError(f"timeout_ms must be positive, got {self.timeout_ms}")


# ============================================================================
# Example and CounterExample Types
# ============================================================================


@dataclass(frozen=True)
class Example:
    """
    An example of valid input for a Tongue.

    text: The example text
    expected_ast: Expected AST (for validation)
    description: Human-readable description
    """

    text: str
    expected_ast: Any | None = None
    description: str = ""

    @property
    def input(self) -> str:
        """Alias for text (for API convenience)."""
        return self.text


@dataclass(frozen=True)
class CounterExample:
    """
    An example of invalid input that should fail parsing.

    text: The counter-example text
    expected_error: Expected error pattern
    description: Why this should be invalid
    """

    text: str
    expected_error: str = ""
    description: str = ""


# ============================================================================
# Constraint Proof Type
# ============================================================================


@dataclass(frozen=True)
class ConstraintProof:
    """
    Proof that a constraint is enforced by the grammar.

    constraint: The constraint statement
    mechanism: How it's enforced (structural/grammatical)
    verified_by: Which agent verified (usually T-gent)
    counter_examples: Examples that should fail
    verified_at: Timestamp of verification
    """

    constraint: str
    mechanism: str  # How the constraint is enforced
    verified_by: str = "T-gent"
    counter_examples: list[CounterExample] = field(default_factory=list)
    verified_at: str = ""

    @property
    def description(self) -> str:
        """Alias for constraint (for API convenience)."""
        return self.constraint

    def is_structural(self) -> bool:
        """Check if constraint is structurally enforced (not runtime)."""
        structural_keywords = [
            "grammatically impossible",
            "not in lexicon",
            "no verb",
            "syntax error",
        ]
        return any(keyword in self.mechanism.lower() for keyword in structural_keywords)


# ============================================================================
# Domain Analysis Type
# ============================================================================


@dataclass(frozen=True)
class DomainAnalysis:
    """
    Analysis of a domain extracted from intent and examples.

    entities: Nouns/objects in the domain
    operations: Verbs/actions available
    constraints: What's forbidden or restricted
    relationships: How entities relate
    lexicon: The allowed vocabulary
    semantics: Semantic actions for operations
    """

    entities: set[str] = field(default_factory=set)
    operations: set[str] = field(default_factory=set)
    constraints: list[str] = field(default_factory=list)
    relationships: dict[str, list[str]] = field(default_factory=dict)
    lexicon: set[str] = field(default_factory=set)
    semantics: dict[str, Callable] = field(default_factory=dict)


# ============================================================================
# Tongue Protocol
# ============================================================================


class TongueProtocol(Protocol):
    """
    Protocol for Tongue implementations.

    A Tongue is a reified domain language with:
    - Grammar specification
    - Parser configuration
    - Interpreter configuration
    - Constraint proofs
    """

    name: str
    version: str
    grammar: str
    mime_type: str

    def parse(self, text: str) -> ParseResult:
        """Parse text using the grammar."""
        ...

    def execute(
        self, ast: Any, context: dict[str, Any] | None = None
    ) -> ExecutionResult:
        """Execute parsed AST in context."""
        ...

    def validate(self) -> bool:
        """Validate the tongue (unambiguous, constraints enforced)."""
        ...

    def render(self, ast: Any) -> str:
        """Render AST back to text (inverse of parse)."""
        ...


# ============================================================================
# Tongue Dataclass (Core Artifact)
# ============================================================================


@dataclass(frozen=True)
class Tongue:
    """
    A reified domain language.

    The Tongue is the primary artifact of G-gent synthesis. It contains:
    - Structural definition (grammar, lexicon)
    - Integration configs (parser, interpreter)
    - Metadata (domain, constraints, examples)
    - Proofs (constraint verification)

    Immutable (frozen) to ensure integrity.
    Hashable to enable cataloging by L-gent.
    """

    # Identity
    name: str
    version: str

    # Structure
    lexicon: frozenset[str]  # Allowed tokens
    grammar: str  # BNF/EBNF/Lark specification
    mime_type: str  # e.g., "application/vnd.kgents.calendar-dsl"

    # Configuration
    level: GrammarLevel
    format: GrammarFormat
    parser_config: ParserConfig
    interpreter_config: InterpreterConfig

    # Metadata
    domain: str  # Domain this tongue serves
    constraints: tuple[str, ...]  # Explicit constraints (what's forbidden)
    examples: tuple[Example, ...] = field(default_factory=tuple)

    # Verification
    constraint_proofs: tuple[ConstraintProof, ...] = field(default_factory=tuple)
    validated: bool = False

    @property
    def grammar_format(self) -> GrammarFormat:
        """Alias for format (for API convenience)."""
        return self.format

    def __hash__(self) -> int:
        """Hash based on name, version, and grammar content."""
        content = f"{self.name}:{self.version}:{self.grammar}"
        return int(hashlib.sha256(content.encode()).hexdigest()[:16], 16)

    def parse(self, text: str) -> ParseResult:
        """
        Parse text using the grammar.

        Delegates to P-gent configured with parser_config.
        """
        # Import here to avoid circular dependency
        from agents.g.parser import parse_with_tongue

        return parse_with_tongue(text, self.parser_config)

    def execute(
        self,
        ast: Any,
        context: dict[str, Any] | None = None,
        handlers: dict[str, Any] | None = None,
    ) -> ExecutionResult:
        """
        Execute parsed AST in context.

        Delegates to J-gent configured with interpreter_config.

        Args:
            ast: Parsed abstract syntax tree from parse()
            context: Optional execution context (variables, state, etc.)
            handlers: Optional command handlers for Level 2 commands
        """
        # Import here to avoid circular dependency
        from agents.g.interpreter import execute_with_tongue

        return execute_with_tongue(ast, self.interpreter_config, context, handlers)

    def validate(self) -> bool:
        """
        Validate the tongue.

        Checks:
        1. Grammar is unambiguous (T-gent verification)
        2. Constraints are enforced (forbidden ops → parse error)
        3. Examples parse correctly
        4. Round-trip: parse(render(ast)) == ast

        Returns True if all checks pass.
        """
        # Placeholder - will be implemented in Phase 2
        return self.validated

    def render(self, ast: Any) -> str:
        """
        Render AST back to text (inverse of parse).

        For round-trip validation: parse(render(ast)) == ast

        Args:
            ast: Abstract syntax tree (from parse() or execute())

        Returns:
            Text representation that can be re-parsed
        """
        # Import here to avoid circular dependency
        from agents.g.renderer import render_ast

        return render_ast(ast, self.format, self.level)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize to dictionary for JSON/YAML export.
        """
        return {
            "name": self.name,
            "version": self.version,
            "lexicon": list(self.lexicon),
            "grammar": self.grammar,
            "mime_type": self.mime_type,
            "level": self.level.value,
            "format": self.format.value,
            "domain": self.domain,
            "constraints": list(self.constraints),
            "examples": [
                {
                    "text": ex.text,
                    "expected_ast": ex.expected_ast,
                    "description": ex.description,
                }
                for ex in self.examples
            ],
            "constraint_proofs": [
                {
                    "constraint": proof.constraint,
                    "mechanism": proof.mechanism,
                    "verified_by": proof.verified_by,
                    "counter_examples": [
                        {
                            "text": ce.text,
                            "expected_error": ce.expected_error,
                            "description": ce.description,
                        }
                        for ce in proof.counter_examples
                    ],
                    "verified_at": proof.verified_at,
                }
                for proof in self.constraint_proofs
            ],
            "validated": self.validated,
            "parser_config": {
                "strategy": self.parser_config.strategy,
                "grammar_format": self.parser_config.grammar_format.value,
                "confidence_threshold": self.parser_config.confidence_threshold,
                "repair_strategy": self.parser_config.repair_strategy,
                "case_sensitive": self.parser_config.case_sensitive,
            },
            "interpreter_config": {
                "runtime": self.interpreter_config.runtime,
                "semantics": self.interpreter_config.semantics,
                "pure_functions_only": self.interpreter_config.pure_functions_only,
                "timeout_ms": self.interpreter_config.timeout_ms,
            },
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Tongue":
        """
        Deserialize from dictionary.
        """
        return cls(
            name=data["name"],
            version=data["version"],
            lexicon=frozenset(data["lexicon"]),
            grammar=data["grammar"],
            mime_type=data["mime_type"],
            level=GrammarLevel(data["level"]),
            format=GrammarFormat(data["format"]),
            domain=data["domain"],
            constraints=tuple(data["constraints"]),
            examples=tuple(
                Example(
                    text=ex["text"],
                    expected_ast=ex.get("expected_ast"),
                    description=ex.get("description", ""),
                )
                for ex in data.get("examples", [])
            ),
            constraint_proofs=tuple(
                ConstraintProof(
                    constraint=proof["constraint"],
                    mechanism=proof["mechanism"],
                    verified_by=proof.get("verified_by", "T-gent"),
                    counter_examples=[
                        CounterExample(
                            text=ce["text"],
                            expected_error=ce.get("expected_error", ""),
                            description=ce.get("description", ""),
                        )
                        for ce in proof.get("counter_examples", [])
                    ],
                    verified_at=proof.get("verified_at", ""),
                )
                for proof in data.get("constraint_proofs", [])
            ),
            validated=data.get("validated", False),
            parser_config=ParserConfig(
                strategy=data["parser_config"]["strategy"],
                grammar_format=GrammarFormat(data["parser_config"]["grammar_format"]),
                confidence_threshold=data["parser_config"].get(
                    "confidence_threshold", 0.8
                ),
                repair_strategy=data["parser_config"].get("repair_strategy", "fail"),
                case_sensitive=data["parser_config"].get("case_sensitive", True),
            ),
            interpreter_config=InterpreterConfig(
                runtime=data["interpreter_config"]["runtime"],
                semantics=data["interpreter_config"].get("semantics", {}),
                pure_functions_only=data["interpreter_config"].get(
                    "pure_functions_only", False
                ),
                timeout_ms=data["interpreter_config"].get("timeout_ms", 5000),
            ),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Tongue":
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))
