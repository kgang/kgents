"""
AGENTESE Sympathetic Error Types

All errors must explain WHY and suggest WHAT TO DO.

The Transparent Infrastructure principle demands that errors
help the user, not just report failure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class AgentesError(Exception):
    """
    Base class for all AGENTESE errors.

    Sympathetic errors:
    - Explain what went wrong (why)
    - Suggest what to do (fix)
    - Provide context (related)
    """

    def __init__(
        self,
        message: str,
        *,
        why: str | None = None,
        suggestion: str | None = None,
        related: list[str] | None = None,
    ) -> None:
        self.why = why
        self.suggestion = suggestion
        self.related = related or []
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        """Format error with sympathetic context."""
        parts = [message]

        if self.why:
            parts.append(f"\n\n    Why: {self.why}")

        if self.suggestion:
            parts.append(f"\n\n    Try: {self.suggestion}")

        if self.related:
            parts.append(f"\n\n    Related: {', '.join(self.related)}")

        return "".join(parts)


@dataclass
class PathNotFoundError(AgentesError):
    """
    Raised when an AGENTESE path cannot be resolved.

    Provides suggestions for:
    - Similar existing paths
    - How to create the path via spec
    - How to use define affordance
    """

    path: str = ""
    available: list[str] = field(default_factory=list)

    def __init__(
        self,
        message: str,
        *,
        path: str = "",
        available: list[str] | None = None,
        why: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        self.path = path
        self.available = available or []

        if not why and path:
            parts = path.split(".")
            if len(parts) >= 2:
                context, holon = parts[0], parts[1]
                why = f"No implementation in registry, no spec at spec/{context}/{holon}.md"

        if not suggestion and path:
            parts = path.split(".")
            if len(parts) >= 2:
                context, holon = parts[0], parts[1]
                suggestion = (
                    f"Create spec/{context}/{holon}.md for auto-generation, "
                    f"or use {context}.{holon}.define"
                )

        super().__init__(
            message,
            why=why,
            suggestion=suggestion,
            related=self.available[:5],  # Show top 5 similar paths
        )

    def __post_init__(self) -> None:
        """Dataclass post-init (for when used as dataclass)."""
        pass


class PathSyntaxError(AgentesError):
    """
    Raised when an AGENTESE path is malformed.

    Provides the correct syntax pattern:
    <context>.<holon>[.<aspect>][clause]*[@annotation]*

    Track A (Syntax Architect): Enhanced with locus support.
    """

    def __init__(
        self,
        message: str,
        *,
        path: str = "",
        locus: str = "",
        position: int = 0,
        why: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        self.path = path
        self.locus = locus
        self.position = position

        if not why:
            why = "AGENTESE paths require: <context>.<holon>[.<aspect>]"

        if not suggestion:
            suggestion = (
                "Valid contexts: world, self, concept, void, time\n"
                "    Examples: world.house.manifest, self.memory.consolidate"
            )

        # Include locus in related if provided
        related = [locus] if locus else None

        super().__init__(message, why=why, suggestion=suggestion, related=related)

    @property
    def locus_path(self) -> str:
        """
        Return the error formatted with locus.

        Track A (Syntax Architect) format: MissingAffordance@world.house.manifest
        """
        if self.locus:
            return f"{self.__class__.__name__}@{self.locus}"
        return self.__class__.__name__


class ClauseSyntaxError(PathSyntaxError):
    """
    Raised when a clause or annotation is malformed.

    Track A (Syntax Architect) deliverable: Clause-specific errors.

    Provides clause-level locus for precise error location:
        ClauseSyntaxError@[phase=INVALID]
    """

    def __init__(
        self,
        message: str,
        *,
        path: str = "",
        locus: str = "",
        clause: str = "",
        modifier: str = "",
        value: str = "",
        why: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        self.clause = clause
        self.modifier = modifier
        self.value = value

        # Build locus from clause if not provided
        if not locus and clause:
            locus = clause
        elif not locus and modifier:
            if value:
                locus = f"[{modifier}={value}]"
            else:
                locus = f"[{modifier}]"

        if not why and modifier:
            why = f"Invalid clause modifier: '{modifier}'"

        super().__init__(
            message,
            path=path,
            locus=locus,
            why=why,
            suggestion=suggestion,
        )


class AnnotationSyntaxError(PathSyntaxError):
    """
    Raised when an annotation is malformed.

    Track A (Syntax Architect) deliverable: Annotation-specific errors.

    Provides annotation-level locus:
        AnnotationSyntaxError@span=invalid_value
    """

    def __init__(
        self,
        message: str,
        *,
        path: str = "",
        locus: str = "",
        annotation: str = "",
        modifier: str = "",
        value: str = "",
        why: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        self.annotation = annotation
        self.modifier = modifier
        self.value = value

        # Build locus from annotation if not provided
        if not locus and annotation:
            locus = annotation
        elif not locus and modifier:
            locus = f"@{modifier}={value}" if value else f"@{modifier}"

        if not why and modifier:
            why = f"Invalid annotation: '@{modifier}'"

        super().__init__(
            message,
            path=path,
            locus=locus,
            why=why,
            suggestion=suggestion,
        )


class AffordanceError(AgentesError):
    """
    Raised when an observer lacks access to an affordance.

    Lists available affordances and suggests appropriate archetypes.
    """

    def __init__(
        self,
        message: str,
        *,
        aspect: str = "",
        observer_archetype: str = "",
        available: list[str] | None = None,
        why: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        self.aspect = aspect
        self.observer_archetype = observer_archetype
        self.available = available or []

        if not why and observer_archetype:
            why = f"The '{observer_archetype}' archetype does not have the '{aspect}' affordance"

        if not suggestion and available:
            suggestion = f"Your affordances: {', '.join(available)}"

        super().__init__(
            message,
            why=why,
            suggestion=suggestion,
            related=available,
        )


class ObserverRequiredError(AgentesError):
    """
    Raised when an operation requires an observer but none provided.

    AGENTESE Principle: There is no view from nowhere.
    """

    def __init__(
        self,
        message: str = "AGENTESE requires an observer. There is no view from nowhere.",
        *,
        why: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        if not why:
            why = "To observe is to disturb. Every interaction needs an Umwelt context."

        if not suggestion:
            suggestion = (
                "Pass an observer Umwelt to invoke():\n"
                "    logos.invoke('world.house.manifest', observer=my_umwelt)"
            )

        super().__init__(message, why=why, suggestion=suggestion)


class TastefulnessError(AgentesError):
    """
    Raised when a spec or creation fails the Tasteful principle.

    Principle #1: Quality over quantity.
    """

    def __init__(
        self,
        message: str,
        *,
        validation_errors: list[str] | None = None,
        why: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        self.validation_errors = validation_errors or []

        if not why:
            why = "The spec fails the Tasteful principle (quality over quantity)"

        if not suggestion:
            suggestion = (
                "Consider:\n"
                "    - Does this concept need to exist?\n"
                "    - What unique value does it add?\n"
                "    - Does it duplicate existing concepts?"
            )

        super().__init__(
            message,
            why=why,
            suggestion=suggestion,
            related=self.validation_errors,
        )


class BudgetExhaustedError(AgentesError):
    """
    Raised when the Accursed Share budget is depleted.

    The void.* context draws from a limited entropy pool.
    """

    def __init__(
        self,
        message: str = "Accursed Share depleted.",
        *,
        remaining: float = 0.0,
        requested: float = 0.0,
        why: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        self.remaining = remaining
        self.requested = requested

        if not why:
            why = f"Requested {requested:.2f} but only {remaining:.2f} remaining"

        if not suggestion:
            suggestion = (
                "Consider:\n"
                "    - void.entropy.pour to return unused randomness\n"
                "    - void.gratitude.tithe to reset the cycle"
            )

        super().__init__(message, why=why, suggestion=suggestion)


class CompositionViolationError(AgentesError):
    """
    Raised when an operation violates composition laws.

    Category laws must be preserved:
    - Identity: Id >> path == path == path >> Id
    - Associativity: (a >> b) >> c == a >> (b >> c)
    """

    def __init__(
        self,
        message: str,
        *,
        law_violated: str = "",
        why: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        self.law_violated = law_violated

        if not why and law_violated:
            why = f"The {law_violated} law was violated"

        if not suggestion:
            suggestion = (
                "Array returns break composition. Use:\n"
                "    - Iterators/streams for multiple results\n"
                "    - Single entities for direct returns"
            )

        super().__init__(message, why=why, suggestion=suggestion)


@dataclass
class LawCheckFailed(AgentesError):
    """
    Raised when a category law verification fails during composition.

    Category laws are VERIFIED, not aspirational (AD-005):
    - Identity: Id >> f ≡ f ≡ f >> Id
    - Associativity: (f >> g) >> h ≡ f >> (g >> h)

    Provides dot-level locus for precise error location:
        LawCheckFailed@concept.forest.manifest >> concept.forest.refine

    Track B (Law Enforcer) deliverable.
    """

    law: str = ""
    locus: str = ""
    left_result: object = None
    right_result: object = None

    def __init__(
        self,
        message: str,
        *,
        law: str = "",
        locus: str = "",
        left_result: object = None,
        right_result: object = None,
        why: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        self.law = law
        self.locus = locus
        self.left_result = left_result
        self.right_result = right_result

        if not why and law:
            match law:
                case "identity":
                    why = "Id >> f should equal f, but results differ"
                case "left_identity":
                    why = "Id >> f should equal f, but results differ"
                case "right_identity":
                    why = "f >> Id should equal f, but results differ"
                case "associativity":
                    why = "(f >> g) >> h should equal f >> (g >> h), but results differ"
                case _:
                    why = f"The {law} law was violated"

        if not suggestion:
            match law:
                case "identity" | "left_identity" | "right_identity":
                    suggestion = (
                        "Check that the morphism is pure (no hidden state).\n"
                        "    Identity composition should not alter behavior."
                    )
                case "associativity":
                    suggestion = (
                        "Check that output types match input types at each handoff.\n"
                        "    Ensure morphisms don't depend on composition order."
                    )
                case _:
                    suggestion = "Verify that the composition preserves category laws."

        super().__init__(
            message,
            why=why,
            suggestion=suggestion,
            related=[locus] if locus else None,
        )

    @classmethod
    def from_verification(
        cls,
        law: str,
        locus: str,
        left_result: object,
        right_result: object,
    ) -> "LawCheckFailed":
        """
        Create from a failed law verification result.

        Args:
            law: Which law failed (identity, associativity)
            locus: Dot-path of the composition (e.g., "f >> g >> h")
            left_result: Result from left-grouped composition
            right_result: Result from right-grouped composition

        Returns:
            LawCheckFailed with formatted message
        """
        return cls(
            f"Category law '{law}' failed at {locus}",
            law=law,
            locus=locus,
            left_result=left_result,
            right_result=right_result,
        )


# Convenience constructors for common error patterns


def path_not_found(
    path: str,
    *,
    similar: list[str] | None = None,
) -> PathNotFoundError:
    """Create a PathNotFoundError with standard formatting."""
    return PathNotFoundError(
        f"'{path}' not found",
        path=path,
        available=similar,
    )


def affordance_denied(
    aspect: str,
    observer_archetype: str,
    available: list[str],
) -> AffordanceError:
    """Create an AffordanceError with standard formatting."""
    return AffordanceError(
        f"Aspect '{aspect}' not available to {observer_archetype}",
        aspect=aspect,
        observer_archetype=observer_archetype,
        available=available,
    )


def invalid_path_syntax(path: str) -> PathSyntaxError:
    """Create a PathSyntaxError with standard formatting."""
    return PathSyntaxError(
        f"Path '{path}' is malformed",
        path=path,
    )
