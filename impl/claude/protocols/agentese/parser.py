"""
AGENTESE Path Parser

Track A (Syntax Architect): Parses AGENTESE paths with clause grammar support.

Grammar (BNF from spec/protocols/agentese.md):

    PATH        ::= CONTEXT "." HOLON "." ASPECT CLAUSE* ANNOTATION*
    CLAUSE      ::= "[" MODIFIER ("=" VALUE)? "]"
    ANNOTATION  ::= "@" MODIFIER "=" VALUE
    MODIFIER    ::= "phase" | "entropy" | "law_check" | "span" | "rollback" | "minimal_output"
    VALUE       ::= FLOAT | BOOL | STRING | PHASE_NAME
    PHASE_NAME  ::= "PLAN" | "RESEARCH" | "DEVELOP" | "STRATEGIZE" | "IMPLEMENT"
                  | "QA" | "TEST" | "EDUCATE" | "MEASURE" | "REFLECT"

Examples:
    - `concept.justice.refine[phase=DEVELOP]`
    - `void.entropy.sip[entropy=0.07]@span=dev_001`
    - `self.liturgy.simulate[rollback=true][law_check=true]`
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

from .contexts import VALID_CONTEXTS

# === Phase Names (N-Phase Cycle) ===


class Phase(str, Enum):
    """N-Phase cycle stages from AD-005."""

    PLAN = "PLAN"
    RESEARCH = "RESEARCH"
    DEVELOP = "DEVELOP"
    STRATEGIZE = "STRATEGIZE"
    CROSS_SYNERGIZE = "CROSS-SYNERGIZE"
    IMPLEMENT = "IMPLEMENT"
    QA = "QA"
    TEST = "TEST"
    EDUCATE = "EDUCATE"
    MEASURE = "MEASURE"
    REFLECT = "REFLECT"


PHASE_NAMES = frozenset(p.value for p in Phase)


# === Valid Modifiers ===


VALID_CLAUSE_MODIFIERS = frozenset(
    {
        "phase",
        "entropy",
        "law_check",
        "rollback",
        "minimal_output",
    }
)

VALID_ANNOTATION_MODIFIERS = frozenset(
    {
        "span",
        "phase",  # @phase=X is also valid
        "law_check",
        "dot",  # @dot=path.to.error for locus
    }
)


# === Parsed Path Components ===


@dataclass(frozen=True)
class Clause:
    """
    A parsed clause from an AGENTESE path.

    Clauses are inline modifiers in square brackets:
        [phase=DEVELOP]
        [entropy=0.07]
        [law_check=true]
    """

    modifier: str
    value: str | float | bool | None = None

    @property
    def as_dict(self) -> dict[str, Any]:
        """Return clause as dict for easy merging."""
        return {self.modifier: self.value}


@dataclass(frozen=True)
class Annotation:
    """
    A parsed annotation from an AGENTESE path.

    Annotations are span/metric markers with @ prefix:
        @span=research_001
        @phase=IMPLEMENT
        @dot=path.to.error
    """

    modifier: str
    value: str

    @property
    def as_dict(self) -> dict[str, str]:
        """Return annotation as dict for easy merging."""
        return {self.modifier: self.value}


@dataclass(frozen=True)
class ParsedPath:
    """
    A fully parsed AGENTESE path.

    Contains the core path (context.holon.aspect) plus
    any clauses and annotations.

    Track A (Syntax Architect) deliverable.
    """

    context: str
    holon: str
    aspect: str
    clauses: tuple[Clause, ...] = ()
    annotations: tuple[Annotation, ...] = ()

    @property
    def base_path(self) -> str:
        """The core path without modifiers."""
        return f"{self.context}.{self.holon}.{self.aspect}"

    @property
    def node_path(self) -> str:
        """The path to the node (context.holon)."""
        return f"{self.context}.{self.holon}"

    @property
    def full_path(self) -> str:
        """Reconstruct the full path with all modifiers."""
        parts = [self.base_path]

        for clause in self.clauses:
            if clause.value is None:
                parts.append(f"[{clause.modifier}]")
            elif isinstance(clause.value, bool):
                parts.append(
                    f"[{clause.modifier}={'true' if clause.value else 'false'}]"
                )
            elif isinstance(clause.value, float):
                parts.append(f"[{clause.modifier}={clause.value}]")
            else:
                parts.append(f"[{clause.modifier}={clause.value}]")

        for annotation in self.annotations:
            parts.append(f"@{annotation.modifier}={annotation.value}")

        return "".join(parts)

    def get_clause(self, modifier: str) -> Clause | None:
        """Get a clause by modifier name."""
        for clause in self.clauses:
            if clause.modifier == modifier:
                return clause
        return None

    def get_annotation(self, modifier: str) -> Annotation | None:
        """Get an annotation by modifier name."""
        for annotation in self.annotations:
            if annotation.modifier == modifier:
                return annotation
        return None

    @property
    def phase(self) -> Phase | None:
        """Get the phase if specified."""
        clause = self.get_clause("phase")
        if clause and isinstance(clause.value, str) and clause.value in PHASE_NAMES:
            return Phase(clause.value)
        annotation = self.get_annotation("phase")
        if annotation and annotation.value in PHASE_NAMES:
            return Phase(annotation.value)
        return None

    @property
    def entropy(self) -> float | None:
        """Get the entropy budget if specified."""
        clause = self.get_clause("entropy")
        if clause and isinstance(clause.value, float):
            return clause.value
        return None

    @property
    def span_id(self) -> str | None:
        """Get the span ID if specified."""
        annotation = self.get_annotation("span")
        if annotation:
            return annotation.value
        return None

    @property
    def locus(self) -> str | None:
        """Get the error locus if specified via @dot annotation."""
        annotation = self.get_annotation("dot")
        if annotation:
            return annotation.value
        return None

    def has_clause(self, modifier: str) -> bool:
        """Check if a clause is present."""
        return self.get_clause(modifier) is not None

    def has_annotation(self, modifier: str) -> bool:
        """Check if an annotation is present."""
        return self.get_annotation(modifier) is not None

    @property
    def law_check_enabled(self) -> bool:
        """Check if law checking is enabled."""
        clause = self.get_clause("law_check")
        if clause:
            return clause.value is True or clause.value == "true"
        return False

    @property
    def rollback_enabled(self) -> bool:
        """Check if rollback is enabled."""
        clause = self.get_clause("rollback")
        if clause:
            return clause.value is True or clause.value == "true"
        return False

    @property
    def minimal_output_enabled(self) -> bool:
        """Check if minimal output is enabled."""
        clause = self.get_clause("minimal_output")
        if clause:
            return clause.value is True or clause.value == "true"
        return False


# === Parse Errors ===


@dataclass
class ParseError:
    """
    A parsing error with locus information.

    Track A (Syntax Architect) deliverable: Errors include dot-level locus.
    """

    message: str
    path: str
    locus: str = ""  # Dot-path to error location
    position: int = 0  # Character position in path
    suggestion: str | None = None

    def __str__(self) -> str:
        if self.locus:
            return f"{self.message}@{self.locus}"
        return self.message


# === Parser ===


@dataclass
class PathParser:
    """
    AGENTESE path parser with clause grammar support.

    Track A (Syntax Architect) deliverable: A3 - Parser extension.

    Usage:
        parser = PathParser()
        result = parser.parse("concept.justice.refine[phase=DEVELOP]@span=dev_001")
        if result.success:
            parsed = result.parsed
        else:
            print(result.error)
    """

    # Whether to validate modifiers against known set
    strict_modifiers: bool = True

    # Whether to validate phase names
    strict_phases: bool = True

    # Whether to validate entropy bounds (0.05-0.10)
    validate_entropy_bounds: bool = True

    def parse(self, path: str) -> "ParseResult":
        """
        Parse an AGENTESE path.

        Args:
            path: The full path string to parse

        Returns:
            ParseResult with either parsed path or error
        """
        if not path:
            return ParseResult(
                success=False,
                error=ParseError(
                    message="Empty path",
                    path=path,
                    suggestion="Provide a path like: context.holon.aspect",
                ),
            )

        # Find where clauses/annotations start
        base_end = len(path)
        clause_start = path.find("[")
        annotation_start = path.find("@")

        if clause_start != -1 and (
            annotation_start == -1 or clause_start < annotation_start
        ):
            base_end = clause_start
        elif annotation_start != -1:
            base_end = annotation_start

        base_path = path[:base_end]
        modifiers = path[base_end:]

        # Parse base path
        base_result = self._parse_base(base_path)
        if not base_result.success:
            return base_result

        parsed = base_result.parsed
        assert parsed is not None

        # Parse clauses and annotations
        clauses: list[Clause] = []
        annotations: list[Annotation] = []

        if modifiers:
            mod_result = self._parse_modifiers(modifiers, path)
            if not mod_result.success:
                return ParseResult(success=False, error=mod_result.error)
            clauses = mod_result.clauses
            annotations = mod_result.annotations

        return ParseResult(
            success=True,
            parsed=ParsedPath(
                context=parsed.context,
                holon=parsed.holon,
                aspect=parsed.aspect,
                clauses=tuple(clauses),
                annotations=tuple(annotations),
            ),
        )

    def _parse_base(self, base_path: str) -> "ParseResult":
        """Parse the base path (context.holon.aspect)."""
        parts = base_path.split(".")

        if len(parts) < 2:
            return ParseResult(
                success=False,
                error=ParseError(
                    message=f"Path '{base_path}' incomplete",
                    path=base_path,
                    locus=base_path,
                    suggestion="AGENTESE requires at least: <context>.<holon>",
                ),
            )

        context = parts[0]
        holon = parts[1]
        aspect = parts[2] if len(parts) >= 3 else ""

        # Validate context
        if context not in VALID_CONTEXTS:
            return ParseResult(
                success=False,
                error=ParseError(
                    message=f"Unknown context: '{context}'",
                    path=base_path,
                    locus=context,
                    suggestion=f"Valid contexts: {', '.join(sorted(VALID_CONTEXTS))}",
                ),
            )

        # Validate holon (must be identifier)
        if not self._is_valid_identifier(holon):
            return ParseResult(
                success=False,
                error=ParseError(
                    message=f"Invalid holon: '{holon}'",
                    path=base_path,
                    locus=f"{context}.{holon}",
                    suggestion="Holon must be a valid identifier (lowercase, underscores allowed)",
                ),
            )

        # Validate aspect if present
        if aspect and not self._is_valid_identifier(aspect):
            return ParseResult(
                success=False,
                error=ParseError(
                    message=f"Invalid aspect: '{aspect}'",
                    path=base_path,
                    locus=f"{context}.{holon}.{aspect}",
                    suggestion="Aspect must be a valid identifier (lowercase, underscores allowed)",
                ),
            )

        return ParseResult(
            success=True,
            parsed=ParsedPath(
                context=context,
                holon=holon,
                aspect=aspect or "manifest",  # Default aspect
            ),
        )

    def _parse_modifiers(self, modifiers: str, full_path: str) -> "_ModifierResult":
        """Parse clause and annotation modifiers."""
        clauses: list[Clause] = []
        annotations: list[Annotation] = []
        pos = 0

        while pos < len(modifiers):
            char = modifiers[pos]

            if char == "[":
                # Parse clause
                end = modifiers.find("]", pos)
                if end == -1:
                    return _ModifierResult(
                        success=False,
                        error=ParseError(
                            message="Unclosed clause bracket",
                            path=full_path,
                            position=len(full_path) - len(modifiers) + pos,
                            locus=modifiers[pos:],
                            suggestion="Close the bracket: [modifier=value]",
                        ),
                    )

                clause_content = modifiers[pos + 1 : end]
                clause_result = self._parse_clause(clause_content, full_path, pos)
                if clause_result.error:
                    return _ModifierResult(success=False, error=clause_result.error)
                if clause_result.clause:
                    clauses.append(clause_result.clause)
                pos = end + 1

            elif char == "@":
                # Parse annotation
                # Find end of annotation (next [ or @ or end)
                next_pos = pos + 1
                while next_pos < len(modifiers) and modifiers[next_pos] not in "[@":
                    next_pos += 1

                annotation_content = modifiers[pos + 1 : next_pos]
                annotation_result = self._parse_annotation(
                    annotation_content, full_path, pos
                )
                if annotation_result.error:
                    return _ModifierResult(success=False, error=annotation_result.error)
                if annotation_result.annotation:
                    annotations.append(annotation_result.annotation)
                pos = next_pos

            else:
                # Unexpected character
                return _ModifierResult(
                    success=False,
                    error=ParseError(
                        message=f"Unexpected character: '{char}'",
                        path=full_path,
                        position=len(full_path) - len(modifiers) + pos,
                        locus=modifiers[pos:],
                        suggestion="Use [clause] or @annotation syntax",
                    ),
                )

        return _ModifierResult(success=True, clauses=clauses, annotations=annotations)

    def _parse_clause(self, content: str, full_path: str, pos: int) -> "_ClauseResult":
        """Parse a single clause content (without brackets)."""
        if "=" in content:
            modifier, value_str = content.split("=", 1)
        else:
            modifier = content
            value_str = ""

        modifier = modifier.strip()

        # Validate modifier
        if self.strict_modifiers and modifier not in VALID_CLAUSE_MODIFIERS:
            return _ClauseResult(
                error=ParseError(
                    message=f"Unknown clause modifier: '{modifier}'",
                    path=full_path,
                    locus=f"[{content}]",
                    suggestion=f"Valid modifiers: {', '.join(sorted(VALID_CLAUSE_MODIFIERS))}",
                )
            )

        # Parse value
        value: str | float | bool | None = None
        if value_str:
            value = self._parse_value(value_str.strip(), modifier)

            # Validate phase names
            if modifier == "phase" and self.strict_phases:
                if isinstance(value, str) and value not in PHASE_NAMES:
                    return _ClauseResult(
                        error=ParseError(
                            message=f"Unknown phase: '{value}'",
                            path=full_path,
                            locus=f"[phase={value}]",
                            suggestion=f"Valid phases: {', '.join(sorted(PHASE_NAMES))}",
                        )
                    )

            # Validate entropy bounds
            if modifier == "entropy" and self.validate_entropy_bounds:
                if isinstance(value, float):
                    if value < 0.0 or value > 1.0:
                        return _ClauseResult(
                            error=ParseError(
                                message=f"Entropy out of range: {value}",
                                path=full_path,
                                locus=f"[entropy={value}]",
                                suggestion="Entropy must be between 0.0 and 1.0 (typically 0.05-0.10)",
                            )
                        )

        return _ClauseResult(clause=Clause(modifier=modifier, value=value))

    def _parse_annotation(
        self, content: str, full_path: str, pos: int
    ) -> "_AnnotationResult":
        """Parse a single annotation content (without @)."""
        if "=" not in content:
            return _AnnotationResult(
                error=ParseError(
                    message=f"Annotation missing value: '@{content}'",
                    path=full_path,
                    locus=f"@{content}",
                    suggestion="Annotations require a value: @modifier=value",
                )
            )

        modifier, value = content.split("=", 1)
        modifier = modifier.strip()
        value = value.strip()

        # Validate modifier
        if self.strict_modifiers and modifier not in VALID_ANNOTATION_MODIFIERS:
            return _AnnotationResult(
                error=ParseError(
                    message=f"Unknown annotation modifier: '{modifier}'",
                    path=full_path,
                    locus=f"@{content}",
                    suggestion=f"Valid modifiers: {', '.join(sorted(VALID_ANNOTATION_MODIFIERS))}",
                )
            )

        return _AnnotationResult(annotation=Annotation(modifier=modifier, value=value))

    def _parse_value(self, value_str: str, modifier: str) -> str | float | bool:
        """Parse a value string into appropriate type."""
        # Boolean
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False

        # Float (for entropy)
        if modifier == "entropy":
            try:
                return float(value_str)
            except ValueError:
                pass

        # Default to string
        return value_str

    def _is_valid_identifier(self, s: str) -> bool:
        """Check if string is a valid identifier."""
        if not s:
            return False
        # Allow lowercase letters, digits, and underscores
        # Must start with letter
        return bool(re.match(r"^[a-z][a-z0-9_]*$", s))


@dataclass
class ParseResult:
    """Result of parsing an AGENTESE path."""

    success: bool
    parsed: ParsedPath | None = None
    error: ParseError | None = None

    def __bool__(self) -> bool:
        return self.success


@dataclass
class _ModifierResult:
    """Internal result for modifier parsing."""

    success: bool
    clauses: list[Clause] = field(default_factory=list)
    annotations: list[Annotation] = field(default_factory=list)
    error: ParseError | None = None


@dataclass
class _ClauseResult:
    """Internal result for clause parsing."""

    clause: Clause | None = None
    error: ParseError | None = None


@dataclass
class _AnnotationResult:
    """Internal result for annotation parsing."""

    annotation: Annotation | None = None
    error: ParseError | None = None


# === Factory Functions ===


def create_parser(
    strict: bool = True,
    validate_entropy: bool = True,
) -> PathParser:
    """
    Create a path parser.

    Args:
        strict: Whether to validate modifiers against known set
        validate_entropy: Whether to validate entropy bounds

    Returns:
        Configured PathParser instance
    """
    return PathParser(
        strict_modifiers=strict,
        strict_phases=strict,
        validate_entropy_bounds=validate_entropy,
    )


def parse_path(path: str) -> ParsedPath:
    """
    Parse an AGENTESE path.

    Raises PathSyntaxError on failure.

    Args:
        path: The path string to parse

    Returns:
        ParsedPath instance

    Raises:
        PathSyntaxError: If path is invalid
    """
    from .exceptions import PathSyntaxError

    parser = PathParser()
    result = parser.parse(path)

    if not result.success:
        error = result.error
        assert error is not None
        raise PathSyntaxError(
            error.message,
            path=error.path,
            why=f"Parse error at: {error.locus}" if error.locus else None,
            suggestion=error.suggestion,
        )

    assert result.parsed is not None
    return result.parsed


def try_parse_path(path: str) -> ParsedPath | None:
    """
    Try to parse an AGENTESE path, returning None on failure.

    Args:
        path: The path string to parse

    Returns:
        ParsedPath instance or None if invalid
    """
    parser = PathParser()
    result = parser.parse(path)
    return result.parsed if result.success else None
