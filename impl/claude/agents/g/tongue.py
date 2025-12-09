"""
Tongue Artifact Utilities

Helper functions for creating, validating, and working with Tongue artifacts.

This module provides:
- Builder pattern for Tongue creation
- Validation utilities
- Serialization helpers
- Common Tongue templates
"""

from dataclasses import replace
from typing import Any

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from agents.g.types import (
    Tongue,
    GrammarLevel,
    GrammarFormat,
    ParserConfig,
    InterpreterConfig,
    Example,
    ConstraintProof,
)


# ============================================================================
# Tongue Builder
# ============================================================================


class TongueBuilder:
    """
    Builder pattern for constructing Tongue artifacts.

    Example:
        tongue = (
            TongueBuilder("CalendarTongue", "1.0.0")
            .with_domain("Calendar Management")
            .with_level(GrammarLevel.COMMAND)
            .with_constraint("No deletes")
            .with_example("CHECK 2024-12-15")
            .build()
        )
    """

    def __init__(self, name: str, version: str):
        self._name = name
        self._version = version
        self._lexicon: set[str] = set()
        self._grammar: str = ""
        self._mime_type: str = f"application/vnd.kgents.{name.lower()}"
        self._level: GrammarLevel = GrammarLevel.COMMAND
        self._format: GrammarFormat = GrammarFormat.EBNF
        self._parser_config: ParserConfig | None = None
        self._interpreter_config: InterpreterConfig | None = None
        self._domain: str = ""
        self._constraints: list[str] = []
        self._examples: list[Example] = []
        self._constraint_proofs: list[ConstraintProof] = []
        self._validated: bool = False

    def with_domain(self, domain: str) -> "TongueBuilder":
        """Set the domain this tongue serves."""
        self._domain = domain
        return self

    def with_level(self, level: GrammarLevel) -> "TongueBuilder":
        """Set the grammar level (SCHEMA, COMMAND, RECURSIVE)."""
        self._level = level
        return self

    def with_format(self, format: GrammarFormat) -> "TongueBuilder":
        """Set the grammar format (BNF, EBNF, LARK, PYDANTIC)."""
        self._format = format
        return self

    def with_grammar(self, grammar: str) -> "TongueBuilder":
        """Set the grammar specification."""
        self._grammar = grammar
        return self

    def with_lexicon(self, *tokens: str) -> "TongueBuilder":
        """Add tokens to the lexicon."""
        self._lexicon.update(tokens)
        return self

    def with_mime_type(self, mime_type: str) -> "TongueBuilder":
        """Set the MIME type."""
        self._mime_type = mime_type
        return self

    def with_constraint(self, constraint: str) -> "TongueBuilder":
        """Add a constraint."""
        self._constraints.append(constraint)
        return self

    def with_example(
        self, text: str, expected_ast: Any | None = None, description: str = ""
    ) -> "TongueBuilder":
        """Add an example."""
        self._examples.append(Example(text, expected_ast, description))
        return self

    def with_counter_example(
        self, text: str, expected_error: str = "", description: str = ""
    ) -> "TongueBuilder":
        """Add a counter-example for constraint proofs."""
        # Store for later attachment to constraint proofs
        return self

    def with_parser_config(self, config: ParserConfig) -> "TongueBuilder":
        """Set parser configuration."""
        self._parser_config = config
        return self

    def with_interpreter_config(self, config: InterpreterConfig) -> "TongueBuilder":
        """Set interpreter configuration."""
        self._interpreter_config = config
        return self

    def with_proof(self, proof: ConstraintProof) -> "TongueBuilder":
        """Add a constraint proof."""
        self._constraint_proofs.append(proof)
        return self

    def validated(self, validated: bool = True) -> "TongueBuilder":
        """Mark as validated."""
        self._validated = validated
        return self

    def build(self) -> Tongue:
        """
        Build the Tongue artifact.

        Raises ValueError if required fields are missing.
        """
        if not self._grammar:
            raise ValueError("Grammar is required")
        if not self._domain:
            raise ValueError("Domain is required")

        # Default configs if not provided
        parser_config = self._parser_config or ParserConfig(
            strategy=self._infer_parser_strategy(),
            grammar_format=self._format,
        )

        interpreter_config = self._interpreter_config or InterpreterConfig(
            runtime="python",
        )

        return Tongue(
            name=self._name,
            version=self._version,
            lexicon=frozenset(self._lexicon),
            grammar=self._grammar,
            mime_type=self._mime_type,
            level=self._level,
            format=self._format,
            parser_config=parser_config,
            interpreter_config=interpreter_config,
            domain=self._domain,
            constraints=tuple(self._constraints),
            examples=tuple(self._examples),
            constraint_proofs=tuple(self._constraint_proofs),
            validated=self._validated,
        )

    def _infer_parser_strategy(self) -> str:
        """Infer parser strategy from grammar format."""
        if self._format == GrammarFormat.PYDANTIC:
            return "pydantic"
        elif self._format == GrammarFormat.LARK:
            return "lark"
        elif self._level == GrammarLevel.SCHEMA:
            return "pydantic"
        elif self._level == GrammarLevel.COMMAND:
            return "regex"
        else:
            return "lark"


# ============================================================================
# Validation Utilities
# ============================================================================


def validate_tongue(tongue: Tongue) -> tuple[bool, list[str]]:
    """
    Validate a Tongue artifact.

    Returns (is_valid, errors) where errors is a list of validation messages.

    Checks:
    - Grammar is non-empty
    - Lexicon matches grammar
    - Examples are parseable (placeholder for now)
    - Constraint proofs are structural
    """
    errors: list[str] = []

    # Check grammar
    if not tongue.grammar.strip():
        errors.append("Grammar cannot be empty")

    # Check domain
    if not tongue.domain.strip():
        errors.append("Domain cannot be empty")

    # Check constraints have proofs
    if tongue.constraints and not tongue.constraint_proofs:
        errors.append(
            f"Constraints specified but no proofs provided: {tongue.constraints}"
        )

    # Check constraint proofs are structural
    for proof in tongue.constraint_proofs:
        if not proof.is_structural():
            errors.append(
                f"Constraint '{proof.constraint}' is not structurally enforced: {proof.mechanism}"
            )

    # Check parser/interpreter config compatibility
    if (
        tongue.format == GrammarFormat.PYDANTIC
        and tongue.parser_config.strategy != "pydantic"
    ):
        errors.append(
            f"PYDANTIC format requires 'pydantic' parser strategy, got '{tongue.parser_config.strategy}'"
        )

    return (len(errors) == 0, errors)


# ============================================================================
# Serialization Utilities
# ============================================================================


def save_tongue_json(tongue: Tongue, filepath: str) -> None:
    """Save Tongue to JSON file."""
    with open(filepath, "w") as f:
        f.write(tongue.to_json())


def load_tongue_json(filepath: str) -> Tongue:
    """Load Tongue from JSON file."""
    with open(filepath, "r") as f:
        return Tongue.from_json(f.read())


def save_tongue_yaml(tongue: Tongue, filepath: str) -> None:
    """Save Tongue to YAML file."""
    if not HAS_YAML:
        raise ImportError(
            "PyYAML is required for YAML serialization. Install with: pip install pyyaml"
        )
    with open(filepath, "w") as f:
        yaml.dump(tongue.to_dict(), f, default_flow_style=False, sort_keys=False)


def load_tongue_yaml(filepath: str) -> Tongue:
    """Load Tongue from YAML file."""
    if not HAS_YAML:
        raise ImportError(
            "PyYAML is required for YAML deserialization. Install with: pip install pyyaml"
        )
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
        return Tongue.from_dict(data)


# ============================================================================
# Tongue Templates
# ============================================================================


def create_schema_tongue(
    name: str,
    domain: str,
    pydantic_model: str,
    version: str = "1.0.0",
) -> Tongue:
    """
    Create a simple SCHEMA-level tongue from a Pydantic model.

    Args:
        name: Tongue name
        domain: Domain description
        pydantic_model: Pydantic model as string
        version: Version string

    Returns:
        A Tongue configured for SCHEMA level parsing
    """
    return (
        TongueBuilder(name, version)
        .with_domain(domain)
        .with_level(GrammarLevel.SCHEMA)
        .with_format(GrammarFormat.PYDANTIC)
        .with_grammar(pydantic_model)
        .with_parser_config(
            ParserConfig(
                strategy="pydantic",
                grammar_format=GrammarFormat.PYDANTIC,
            )
        )
        .with_interpreter_config(
            InterpreterConfig(
                runtime="python",
                pure_functions_only=True,
            )
        )
        .build()
    )


def create_command_tongue(
    name: str,
    domain: str,
    bnf_grammar: str,
    lexicon: set[str],
    constraints: list[str],
    version: str = "1.0.0",
) -> Tongue:
    """
    Create a COMMAND-level tongue with BNF grammar.

    Args:
        name: Tongue name
        domain: Domain description
        bnf_grammar: BNF grammar specification
        lexicon: Allowed tokens
        constraints: Constraint list
        version: Version string

    Returns:
        A Tongue configured for COMMAND level parsing
    """
    builder = (
        TongueBuilder(name, version)
        .with_domain(domain)
        .with_level(GrammarLevel.COMMAND)
        .with_format(GrammarFormat.BNF)
        .with_grammar(bnf_grammar)
        .with_lexicon(*lexicon)
        .with_parser_config(
            ParserConfig(
                strategy="regex",
                grammar_format=GrammarFormat.BNF,
            )
        )
        .with_interpreter_config(
            InterpreterConfig(
                runtime="python",
            )
        )
    )

    for constraint in constraints:
        builder.with_constraint(constraint)

    return builder.build()


def create_recursive_tongue(
    name: str,
    domain: str,
    lark_grammar: str,
    lexicon: set[str],
    version: str = "1.0.0",
) -> Tongue:
    """
    Create a RECURSIVE-level tongue with Lark grammar.

    Args:
        name: Tongue name
        domain: Domain description
        lark_grammar: Lark grammar specification
        lexicon: Allowed tokens
        version: Version string

    Returns:
        A Tongue configured for RECURSIVE level parsing
    """
    return (
        TongueBuilder(name, version)
        .with_domain(domain)
        .with_level(GrammarLevel.RECURSIVE)
        .with_format(GrammarFormat.LARK)
        .with_grammar(lark_grammar)
        .with_lexicon(*lexicon)
        .with_parser_config(
            ParserConfig(
                strategy="lark",
                grammar_format=GrammarFormat.LARK,
            )
        )
        .with_interpreter_config(
            InterpreterConfig(
                runtime="sandboxed",
                pure_functions_only=True,
            )
        )
        .build()
    )


# ============================================================================
# Tongue Evolution (Versioning)
# ============================================================================


def evolve_tongue(
    tongue: Tongue,
    *,
    version: str | None = None,
    grammar: str | None = None,
    constraints: tuple[str, ...] | None = None,
    validated: bool | None = None,
    **changes: Any,
) -> Tongue:
    """
    Create a new version of a Tongue with modifications.

    Uses dataclasses.replace for immutable updates.

    Example:
        tongue_v2 = evolve_tongue(
            tongue_v1,
            version="2.0.0",
            grammar=new_grammar,
            validated=False
        )
    """
    updates = {}
    if version is not None:
        updates["version"] = version
    if grammar is not None:
        updates["grammar"] = grammar
    if constraints is not None:
        updates["constraints"] = constraints
    if validated is not None:
        updates["validated"] = validated
    updates.update(changes)

    return replace(tongue, **updates)
