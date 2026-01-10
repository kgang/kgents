"""
Pilot Bootstrap Protocol Implementation.

This module enables bootstrapping arbitrary intellectual endeavors with:
- Axioms (L < 0.10) - immutable foundations
- Values (0.10 <= L < 0.38) - derived principles
- Specifications (0.38 <= L < 0.65) - implementation choices
- Tuning (L >= 0.65) - variable parameters
- Laws - domain-specific instantiations of Five Universal Schemas

Philosophy:
    "From axioms to laws in one day. From spec to witness in one session."

    The Pilot Bootstrap Protocol takes the kernel primitives (Galois loss,
    Five Law Schemas, Witness Protocol) and instantiates them for a specific
    domain. Each pilot starts with axioms, derives values, and registers laws.

The Stratification:
    ContentLayer maps Galois loss to mutability:
    - AXIOM: L < 0.10 - survives radical restructuring (immutable)
    - VALUE: L < 0.38 - stable under normal operations (rarely changes)
    - SPEC: L < 0.65 - implementation choices (changeable)
    - TUNING: L >= 0.65 - variable parameters (freely adjustable)

See: plans/pilot-bootstrap-protocol.md
See: spec/protocols/zero-seed1/galois.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Protocol, runtime_checkable
from uuid import uuid4

if TYPE_CHECKING:
    from collections.abc import Coroutine


# =============================================================================
# Content Layer Classification
# =============================================================================


class ContentLayer(Enum):
    """
    Content stratification layers (4-layer simplified from 5-tier evidence).

    Maps Galois loss to content mutability:
    - AXIOM: L < 0.10 - CATEGORICAL evidence tier, immutable foundations
    - VALUE: 0.10 <= L < 0.38 - EMPIRICAL evidence tier, derived principles
    - SPEC: 0.38 <= L < 0.65 - AESTHETIC/SOMATIC tiers, implementation choices
    - TUNING: L >= 0.65 - CHAOTIC tier, variable parameters

    The layer determines how resistant content should be to change:
    - Axiom changes require existential justification
    - Value changes require principled justification
    - Spec changes require practical justification
    - Tuning changes are free to adjust

    Kent calibration (2025-12-28): These thresholds were calibrated against
    the five pilots to match intuitions about what should be mutable.
    """

    AXIOM = auto()  # L < 0.10 - CATEGORICAL
    VALUE = auto()  # 0.10 <= L < 0.38 - EMPIRICAL
    SPEC = auto()  # 0.38 <= L < 0.65 - AESTHETIC/SOMATIC
    TUNING = auto()  # L >= 0.65 - CHAOTIC


def classify_content_layer(galois_loss: float) -> ContentLayer:
    """
    Classify content into stratification layer based on Galois loss.

    Uses Kent-calibrated thresholds (2025-12-28).

    The 4-layer stratification maps to content mutability:
    - AXIOM (L < 0.10): Fixed points, immutable foundations
    - VALUE (L < 0.38): Stable principles, rarely change
    - SPEC (L < 0.65): Implementation choices, changeable
    - TUNING (L >= 0.65): Parameters, freely adjustable

    Args:
        galois_loss: Galois loss value in [0, 1]

    Returns:
        ContentLayer indicating the appropriate stratification layer

    Example:
        >>> classify_content_layer(0.05)
        <ContentLayer.AXIOM: 1>
        >>> classify_content_layer(0.25)
        <ContentLayer.VALUE: 2>
        >>> classify_content_layer(0.50)
        <ContentLayer.SPEC: 3>
        >>> classify_content_layer(0.80)
        <ContentLayer.TUNING: 4>
    """
    if galois_loss < 0.10:
        return ContentLayer.AXIOM
    elif galois_loss < 0.38:
        return ContentLayer.VALUE
    elif galois_loss < 0.65:
        return ContentLayer.SPEC
    else:
        return ContentLayer.TUNING


# =============================================================================
# Foundation Building Blocks
# =============================================================================


@dataclass(frozen=True)
class Axiom:
    """
    An axiom (L < 0.10) - immutable foundation.

    Axioms are zero-loss fixed points under Galois restructuring.
    They survive radical restructuring with minimal semantic loss.

    Attributes:
        name: Identifier for the axiom
        statement: The axiom's content
        derivation: From which kernel primitive this derives
        test: How to verify if the axiom is being violated
        galois_loss: Computed Galois loss (must be < 0.10)

    Example:
        >>> axiom = Axiom(
        ...     name="witness_primacy",
        ...     statement="Every significant action must be witnessed",
        ...     derivation="from Coherence Gate schema",
        ...     test="check for unwitnessed significant actions",
        ...     galois_loss=0.05,
        ... )
    """

    name: str
    statement: str
    derivation: str  # From which kernel primitive
    test: str  # How to verify violation
    galois_loss: float

    def __post_init__(self) -> None:
        """Validate axiom constraints."""
        if self.galois_loss >= 0.10:
            raise ValueError(
                f"Axiom '{self.name}' has loss {self.galois_loss:.3f} >= 0.10. "
                "Content with loss >= 0.10 should be a Value, not an Axiom."
            )


@dataclass(frozen=True)
class Value:
    """
    A value (L < 0.38) - derived principle.

    Values derive from axioms and provide stable guiding principles.
    They have low-but-nonzero loss under restructuring.

    Attributes:
        name: Identifier for the value
        statement: The value's content
        derived_from: Tuple of axiom names this value derives from
        specification: How this value guides implementation
        galois_loss: Computed Galois loss (must be 0.10 <= L < 0.38)

    Example:
        >>> value = Value(
        ...     name="courage_protection",
        ...     statement="High-risk creative acts should not be penalized",
        ...     derived_from=("witness_primacy", "joy_induction"),
        ...     specification="Weight bold choices positively in scoring",
        ...     galois_loss=0.25,
        ... )
    """

    name: str
    statement: str
    derived_from: tuple[str, ...]  # Axiom names
    specification: str
    galois_loss: float

    def __post_init__(self) -> None:
        """Validate value constraints."""
        if self.galois_loss < 0.10:
            raise ValueError(
                f"Value '{self.name}' has loss {self.galois_loss:.3f} < 0.10. "
                "Content with loss < 0.10 should be an Axiom, not a Value."
            )
        if self.galois_loss >= 0.38:
            raise ValueError(
                f"Value '{self.name}' has loss {self.galois_loss:.3f} >= 0.38. "
                "Content with loss >= 0.38 should be a Spec, not a Value."
            )


@dataclass
class Law:
    """A categorical law that must hold in the foundation."""

    name: str
    statement: str
    verification: str = ""


@dataclass(frozen=True)
class PilotFoundation:
    """
    Complete foundation for a pilot.

    Contains all axioms, values, and law registrations for a domain.
    This is the output of the bootstrap process.

    Attributes:
        name: Pilot name
        axioms: Tuple of validated axioms
        values: Tuple of derived values
        laws: Tuple of law names registered in pilot_laws

    Example:
        >>> foundation = PilotFoundation(
        ...     name="rap-coach",
        ...     axioms=(axiom1, axiom2),
        ...     values=(value1, value2, value3),
        ...     laws=("L1 Intent Declaration Law", "L2 Feedback Grounding Law"),
        ... )
    """

    name: str
    axioms: tuple[Axiom, ...]
    values: tuple[Value, ...]
    laws: tuple[str, ...]  # Law names registered in pilot_laws

    def summary(self) -> str:
        """Generate a summary of the foundation."""
        lines = [
            f"Pilot: {self.name}",
            f"Axioms: {len(self.axioms)}",
            f"Values: {len(self.values)}",
            f"Laws: {len(self.laws)}",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "axioms": [
                {
                    "name": a.name,
                    "statement": a.statement,
                    "derivation": a.derivation,
                    "test": a.test,
                    "galois_loss": a.galois_loss,
                }
                for a in self.axioms
            ],
            "values": [
                {
                    "name": v.name,
                    "statement": v.statement,
                    "derived_from": list(v.derived_from),
                    "specification": v.specification,
                    "galois_loss": v.galois_loss,
                }
                for v in self.values
            ],
            "laws": list(self.laws),
        }


# =============================================================================
# Galois Loss Protocol
# =============================================================================


@runtime_checkable
class GaloisLossComputer(Protocol):
    """Protocol for Galois loss computation."""

    async def compute_loss(self, content: str) -> float:
        """Compute Galois loss for content."""
        ...


# =============================================================================
# Axiom Validation
# =============================================================================


async def validate_axiom_candidate(
    content: str,
    compute_loss_fn: Callable[..., Any],
) -> tuple[bool, float, str]:
    """
    Validate if content qualifies as an axiom.

    An axiom must have Galois loss < 0.10, indicating it survives
    radical restructuring with minimal semantic loss.

    Args:
        content: The content to evaluate as an axiom candidate
        compute_loss_fn: Async function that computes Galois loss.
            Should accept content and return a result with a .loss attribute
            or a float directly.

    Returns:
        Tuple of (is_axiom, loss, interpretation):
        - is_axiom: True if content qualifies as an axiom
        - loss: The computed Galois loss
        - interpretation: Human-readable explanation

    Example:
        >>> async def mock_loss(content):
        ...     return 0.05  # Low loss
        >>> is_valid, loss, msg = await validate_axiom_candidate("Test", mock_loss)
        >>> is_valid
        True
    """
    result = await compute_loss_fn(content)

    # Handle both result objects and raw floats
    if hasattr(result, "loss"):
        loss = result.loss
    else:
        loss = float(result)

    if loss < 0.10:
        return True, loss, "Fixed point: content survives radical restructuring"
    elif loss < 0.20:
        return False, loss, "Near-axiom: consider refining to reduce loss"
    else:
        return False, loss, "Not an axiom: too much information lost in restructuring"


# =============================================================================
# Pilot Bootstrapper
# =============================================================================


class PilotBootstrapper:
    """
    Bootstrap a new pilot with theoretical foundations.

    From axioms to laws in one day. From spec to witness in one session.

    The bootstrapper guides the creation of a new pilot domain by:
    1. Validating axiom candidates using Galois loss
    2. Deriving values from axioms
    3. Connecting to the Five Universal Law Schemas

    Usage:
        >>> bootstrapper = PilotBootstrapper("my-pilot")
        >>> accepted, msg = await bootstrapper.add_axiom_candidate(
        ...     name="core_principle",
        ...     statement="Every X must have Y",
        ...     derivation="from Coherence Gate",
        ...     test="check X has Y",
        ...     compute_loss_fn=galois_computer.compute_loss,
        ... )
        >>> if accepted:
        ...     bootstrapper.derive_value(...)
        >>> foundation = bootstrapper.build_foundation(laws=("L1 Law",))

    Attributes:
        pilot_name: Name of the pilot being bootstrapped
        axioms: List of validated axioms
        values: List of derived values
    """

    def __init__(self, pilot_name: str) -> None:
        """
        Initialize a new pilot bootstrapper.

        Args:
            pilot_name: Name for the new pilot domain
        """
        self.pilot_name = pilot_name
        self.axioms: list[Axiom] = []
        self.values: list[Value] = []

    async def add_axiom_candidate(
        self,
        name: str,
        statement: str,
        derivation: str,
        test: str,
        compute_loss_fn: Callable[..., Any],
    ) -> tuple[bool, str]:
        """
        Add an axiom candidate with Galois validation.

        The candidate will only be accepted if its Galois loss is < 0.10,
        indicating it is a fixed point under restructuring.

        Args:
            name: Identifier for the axiom
            statement: The axiom's content
            derivation: From which kernel primitive this derives
            test: How to verify if the axiom is being violated
            compute_loss_fn: Async function to compute Galois loss

        Returns:
            Tuple of (accepted, message):
            - accepted: True if the axiom was added
            - message: Explanation of the result

        Example:
            >>> accepted, msg = await bootstrapper.add_axiom_candidate(
            ...     name="witness_primacy",
            ...     statement="Every significant action must be witnessed",
            ...     derivation="from Coherence Gate schema",
            ...     test="check for unwitnessed actions",
            ...     compute_loss_fn=computer.compute_loss,
            ... )
        """
        is_valid, loss, interpretation = await validate_axiom_candidate(statement, compute_loss_fn)

        if is_valid:
            axiom = Axiom(
                name=name,
                statement=statement,
                derivation=derivation,
                test=test,
                galois_loss=loss,
            )
            self.axioms.append(axiom)
            return True, f"Axiom accepted: L={loss:.3f} ({interpretation})"
        else:
            return False, f"Axiom rejected: L={loss:.3f} ({interpretation})"

    def derive_value(
        self,
        name: str,
        statement: str,
        derived_from: tuple[str, ...],
        specification: str,
        galois_loss: float,
    ) -> Value:
        """
        Derive a value from axioms.

        Values must have Galois loss in [0.10, 0.38) to qualify.

        Args:
            name: Identifier for the value
            statement: The value's content
            derived_from: Tuple of axiom names this derives from
            specification: How this value guides implementation
            galois_loss: Pre-computed Galois loss

        Returns:
            The created Value object

        Raises:
            ValueError: If galois_loss is not in valid range

        Example:
            >>> value = bootstrapper.derive_value(
            ...     name="courage_protection",
            ...     statement="High-risk acts protected from penalty",
            ...     derived_from=("witness_primacy",),
            ...     specification="Use Courage Preservation schema",
            ...     galois_loss=0.25,
            ... )
        """
        value = Value(
            name=name,
            statement=statement,
            derived_from=derived_from,
            specification=specification,
            galois_loss=galois_loss,
        )
        self.values.append(value)
        return value

    def build_foundation(self, laws: tuple[str, ...]) -> PilotFoundation:
        """
        Build the complete pilot foundation.

        This finalizes the bootstrap process and creates an immutable
        PilotFoundation containing all axioms, values, and law registrations.

        Args:
            laws: Tuple of law names that should be registered for this pilot.
                  These should match entries in pilot_laws.PILOT_LAWS.

        Returns:
            PilotFoundation containing the complete pilot definition

        Example:
            >>> foundation = bootstrapper.build_foundation(
            ...     laws=(
            ...         "L1 Intent Declaration Law",
            ...         "L2 Feedback Grounding Law",
            ...     )
            ... )
            >>> print(foundation.summary())
        """
        return PilotFoundation(
            name=self.pilot_name,
            axioms=tuple(self.axioms),
            values=tuple(self.values),
            laws=laws,
        )

    def get_axiom_by_name(self, name: str) -> Axiom | None:
        """Get an axiom by name, or None if not found."""
        for axiom in self.axioms:
            if axiom.name == name:
                return axiom
        return None

    def get_value_by_name(self, name: str) -> Value | None:
        """Get a value by name, or None if not found."""
        for value in self.values:
            if value.name == name:
                return value
        return None

    def validate_derivation_chain(self) -> list[str]:
        """
        Validate that all values derive from known axioms.

        Returns:
            List of error messages (empty if valid)
        """
        errors: list[str] = []
        axiom_names = {axiom.name for axiom in self.axioms}

        for value in self.values:
            for parent_name in value.derived_from:
                if parent_name not in axiom_names:
                    errors.append(
                        f"Value '{value.name}' derives from unknown axiom '{parent_name}'"
                    )

        return errors


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Enums
    "ContentLayer",
    # Core types
    "Axiom",
    "Value",
    "Law",
    "PilotFoundation",
    # Classification
    "classify_content_layer",
    # Validation
    "validate_axiom_candidate",
    "GaloisLossComputer",
    # Bootstrapper
    "PilotBootstrapper",
]
