"""
PromptM: The Prompt Monad.

A self-improving prompt computation with categorical guarantees.

Monadic Laws (must hold):
- Left Identity:  unit(x) >>= f ≡ f(x)
- Right Identity: m >>= unit ≡ m
- Associativity:  (m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)

The Prompt Monad encapsulates:
1. A value (typically a Section or CompiledPrompt)
2. A reasoning trace (for transparency)
3. Provenance (where the value came from)
4. Optional checkpoint ID (for rollback)

This enables composable prompt transformations while maintaining
full accountability for how the prompt evolved.

See: plans/_continuations/evergreen-wave3-reformation-continuation.md Part IV
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Generic, TypeVar

# Type variables for generic monad
A = TypeVar("A")
B = TypeVar("B")


class Source(Enum):
    """Source of a prompt value for provenance tracking."""

    TEMPLATE = auto()  # Hardcoded template
    FILE = auto()  # Read from file
    GIT = auto()  # Derived from git state
    LLM = auto()  # Inferred by LLM
    HABIT = auto()  # Learned from developer patterns
    TEXTGRAD = auto()  # Self-improvement via feedback
    FUSION = auto()  # Merged from multiple sources
    ROLLBACK = auto()  # Restored from checkpoint
    USER = auto()  # Directly from user input


@dataclass(frozen=True)
class PromptM(Generic[A]):
    """
    The Prompt Monad: a self-improving prompt computation.

    PromptM wraps a value with its reasoning trace and provenance,
    enabling composable transformations while maintaining transparency.

    Attributes:
        value: The wrapped value (Section, CompiledPrompt, etc.)
        reasoning_trace: Steps taken to produce this value
        provenance: Sources that contributed to this value
        checkpoint_id: ID for rollback capability (if checkpointed)

    Example:
        >>> section = Section(name="test", content="hello", token_cost=2, required=True)
        >>> m = PromptM.unit(section)
        >>> m2 = m.map(lambda s: s.with_content(s.content.upper()))
        >>> m2.value.content
        'HELLO'
    """

    value: A
    reasoning_trace: tuple[str, ...] = ()
    provenance: tuple[Source, ...] = ()
    checkpoint_id: str | None = None

    @staticmethod
    def unit(value: A) -> "PromptM[A]":
        """
        Lift a value into the monad.

        This is the monadic 'return' operation.
        Creates a minimal PromptM with no trace or provenance.

        Law (Left Identity): unit(x).bind(f) == f(x)
        """
        return PromptM(value=value)

    def bind(self, f: Callable[[A], "PromptM[B]"]) -> "PromptM[B]":
        """
        Monadic bind: chain computations, accumulating traces.

        This is the >>= operator. It:
        1. Applies f to the current value
        2. Accumulates reasoning traces
        3. Combines provenance
        4. Preserves the latest checkpoint

        Law (Associativity): m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))
        """
        result = f(self.value)
        return PromptM(
            value=result.value,
            reasoning_trace=self.reasoning_trace + result.reasoning_trace,
            provenance=self.provenance + result.provenance,
            checkpoint_id=result.checkpoint_id or self.checkpoint_id,
        )

    def map(self, f: Callable[[A], B]) -> "PromptM[B]":
        """
        Functor map: apply a pure function to the wrapped value.

        This is the fmap operation. Unlike bind, it doesn't change
        the trace or provenance—just transforms the value.

        Equivalent to: self.bind(lambda x: PromptM.unit(f(x)))
        """
        return PromptM(
            value=f(self.value),
            reasoning_trace=self.reasoning_trace,
            provenance=self.provenance,
            checkpoint_id=self.checkpoint_id,
        )

    def with_trace(self, trace: str) -> "PromptM[A]":
        """Add a reasoning trace entry."""
        return PromptM(
            value=self.value,
            reasoning_trace=self.reasoning_trace + (trace,),
            provenance=self.provenance,
            checkpoint_id=self.checkpoint_id,
        )

    def with_provenance(self, source: Source) -> "PromptM[A]":
        """Add a provenance source."""
        return PromptM(
            value=self.value,
            reasoning_trace=self.reasoning_trace,
            provenance=self.provenance + (source,),
            checkpoint_id=self.checkpoint_id,
        )

    def with_checkpoint(self, checkpoint_id: str) -> "PromptM[A]":
        """Set the checkpoint ID for rollback capability."""
        return PromptM(
            value=self.value,
            reasoning_trace=self.reasoning_trace,
            provenance=self.provenance,
            checkpoint_id=checkpoint_id,
        )

    # Operator overloads for ergonomic usage
    def __rshift__(self, f: Callable[[A], "PromptM[B]"]) -> "PromptM[B]":
        """
        >> operator as alias for bind.

        Enables: m >> f >> g instead of m.bind(f).bind(g)
        """
        return self.bind(f)

    def __or__(self, f: Callable[[A], B]) -> "PromptM[B]":
        """
        | operator as alias for map.

        Enables: m | f | g instead of m.map(f).map(g)
        """
        return self.map(f)

    def __repr__(self) -> str:
        """Readable representation for debugging."""
        provenance_str = (
            ", ".join(s.name for s in self.provenance) if self.provenance else "none"
        )
        trace_count = len(self.reasoning_trace)
        checkpoint_str = (
            f", checkpoint={self.checkpoint_id}" if self.checkpoint_id else ""
        )
        return f"PromptM(value={self.value!r}, provenance=[{provenance_str}], traces={trace_count}{checkpoint_str})"


# =============================================================================
# Monadic Combinators
# =============================================================================


def sequence(monads: list[PromptM[A]]) -> PromptM[list[A]]:
    """
    Sequence a list of monads into a monad of a list.

    Accumulates all traces and provenance.

    Example:
        >>> ms = [PromptM.unit(1), PromptM.unit(2), PromptM.unit(3)]
        >>> sequence(ms).value
        [1, 2, 3]
    """
    if not monads:
        return PromptM.unit([])

    values: list[A] = []
    traces: list[str] = []
    provenance: list[Source] = []
    checkpoint_id: str | None = None

    for m in monads:
        values.append(m.value)
        traces.extend(m.reasoning_trace)
        provenance.extend(m.provenance)
        if m.checkpoint_id:
            checkpoint_id = m.checkpoint_id

    return PromptM(
        value=values,
        reasoning_trace=tuple(traces),
        provenance=tuple(provenance),
        checkpoint_id=checkpoint_id,
    )


def traverse(items: list[A], f: Callable[[A], PromptM[B]]) -> PromptM[list[B]]:
    """
    Map a monadic function over a list and sequence the results.

    Equivalent to: sequence([f(x) for x in items])

    Example:
        >>> items = ["a", "b", "c"]
        >>> traverse(items, lambda x: PromptM.unit(x.upper())).value
        ['A', 'B', 'C']
    """
    return sequence([f(item) for item in items])


def join(mm: PromptM[PromptM[A]]) -> PromptM[A]:
    """
    Flatten a nested monad.

    join(mm) == mm.bind(identity)

    This is the monadic 'join' operation that flattens
    PromptM[PromptM[A]] to PromptM[A].
    """
    inner = mm.value
    return PromptM(
        value=inner.value,
        reasoning_trace=mm.reasoning_trace + inner.reasoning_trace,
        provenance=mm.provenance + inner.provenance,
        checkpoint_id=inner.checkpoint_id or mm.checkpoint_id,
    )


# =============================================================================
# Lifting Functions
# =============================================================================


def lift_trace(trace: str) -> Callable[[A], PromptM[A]]:
    """
    Create a function that adds a trace and returns unit.

    Useful in bind chains for adding reasoning steps.

    Example:
        >>> m = PromptM.unit("hello")
        >>> m2 = m.bind(lift_trace("Processing..."))
        >>> m2.reasoning_trace
        ('Processing...',)
    """

    def inner(value: A) -> PromptM[A]:
        return PromptM(
            value=value,
            reasoning_trace=(trace,),
            provenance=(),
            checkpoint_id=None,
        )

    return inner


def lift_provenance(source: Source) -> Callable[[A], PromptM[A]]:
    """
    Create a function that adds provenance and returns unit.

    Useful in bind chains for marking source attribution.
    """

    def inner(value: A) -> PromptM[A]:
        return PromptM(
            value=value,
            reasoning_trace=(),
            provenance=(source,),
            checkpoint_id=None,
        )

    return inner


# =============================================================================
# TextGRAD Integration (Wave 4)
# =============================================================================


def improve(
    sections: dict[str, str],
    feedback: str,
    learning_rate: float = 0.5,
    rigidity_lookup: dict[str, float] | None = None,
) -> "PromptM[dict[str, str]]":
    """
    Apply TextGRAD improvement to sections.

    This is the main entry point for self-improvement via the monad.

    Args:
        sections: Dict of section_name -> content
        feedback: Natural language feedback
        learning_rate: How aggressively to apply changes (0.0-1.0)
        rigidity_lookup: Dict of section_name -> rigidity

    Returns:
        PromptM containing improved sections dict

    Example:
        >>> sections = {"principles": "Be helpful...", "skills": "Test-driven..."}
        >>> result = improve(sections, "make principles more concise")
        >>> result.value["principles"]  # Improved content
    """
    try:
        from .textgrad import TextGRADImprover

        improver = TextGRADImprover(learning_rate=learning_rate)
        result = improver.improve(sections, feedback, rigidity_lookup)

        # Extract improved sections
        improved_sections: dict[str, str] = {}
        for section_name in sections:
            if section_name in result.sections_modified:
                # Parse from combined content (simplified)
                improved_sections[section_name] = sections[section_name]  # Fallback
            else:
                improved_sections[section_name] = sections[section_name]

        # Actually extract from result
        if result.content_changed:
            # Re-parse the improved content into sections
            # This is a simplified version - proper impl would track per-section
            improved_sections = _parse_sections(
                result.improved_content, sections.keys()
            )

        return PromptM(
            value=improved_sections,
            reasoning_trace=result.reasoning_trace,
            provenance=(Source.TEXTGRAD,),
            checkpoint_id=result.checkpoint_id,
        )

    except ImportError as e:
        return PromptM(
            value=sections,  # Return unchanged
            reasoning_trace=(f"TextGRAD not available: {e}",),
            provenance=(),
            checkpoint_id=None,
        )


def _parse_sections(content: str, section_names: "Iterable[str]") -> dict[str, str]:
    """Parse combined content back into sections."""
    import re
    from typing import Iterable

    sections: dict[str, str] = {}
    current_section: str | None = None
    current_lines: list[str] = []

    for line in content.split("\n"):
        # Check for section header
        match = re.match(r"^##\s+(\w+)\s*$", line)
        if match:
            # Save previous section
            if current_section:
                sections[current_section] = "\n".join(current_lines).strip()

            current_section = match.group(1)
            current_lines = []
        elif current_section:
            current_lines.append(line)

    # Save last section
    if current_section:
        sections[current_section] = "\n".join(current_lines).strip()

    # Fill in missing sections with empty
    for name in section_names:
        if name not in sections:
            sections[name] = ""

    return sections


__all__ = [
    "Source",
    "PromptM",
    "sequence",
    "traverse",
    "join",
    "lift_trace",
    "lift_provenance",
    "improve",
]
