"""
DNA: Configuration as Genetic Code.

Configuration is not loaded. It is expressed. The agent IS its config.

This module implements the DNA model from spec/protocols/config.md:
- DNA Protocol: Base interface for agent configuration
- Germination: Validated construction pattern
- Trait Expression: Derived behavioral parameters
- Constraint Checking: G-gent tongue integration (semantic validation)

The key insight: DNA is validated at germination time using G-gent tongues,
not at runtime using schema validators.

Migration: 2025-12-16
- Original location: impl/claude/bootstrap/dna.py
- New location: impl/claude/protocols/config/dna.py
- The bootstrap module re-exports from here for backward compatibility.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import (
    Any,
    Callable,
    Protocol,
    Self,
    TypeVar,
    runtime_checkable,
)

# === Type Variables ===

D = TypeVar("D", bound="DNA")  # DNA type
T = TypeVar("T")  # Generic trait value


# === Errors ===


class DNAValidationError(Exception):
    """Raised when DNA fails validation during germination."""

    def __init__(
        self,
        dna_type: str,
        errors: list[str],
        message: str = "",
    ):
        self.dna_type = dna_type
        self.errors = errors
        self.message = message or f"DNA validation failed for {dna_type}"
        super().__init__(f"{self.message}: {errors}")


class TraitNotFoundError(Exception):
    """Raised when requesting an unknown trait."""

    pass


# === Constraint Type ===


@dataclass(frozen=True)
class Constraint:
    """
    A semantic constraint on DNA values.

    Beyond type checking, constraints enforce semantic invariants.
    Example: epistemic_humility constraint limits confidence_threshold to 0.8.
    """

    name: str
    check: Callable[[Any], bool]
    message: str

    def validate(self, dna: Any) -> tuple[bool, str]:
        """Check if DNA satisfies this constraint."""
        try:
            if self.check(dna):
                return (True, "")
            return (False, self.message)
        except Exception as e:
            return (False, f"{self.message}: {e}")


# === DNA Protocol ===


@runtime_checkable
class DNA(Protocol):
    """
    Base protocol for agent configuration.

    All agent configs implement this protocol. The key insight:
    DNA is validated at germination time using constraints,
    not at runtime using schema validators.

    Properties:
    - Immutable after germination (frozen=True)
    - Validated against semantic constraints
    - Expresses derived traits from base values
    """

    @classmethod
    def constraints(cls) -> list[Constraint]:
        """
        Return semantic constraints for this DNA type.

        Override to add domain-specific constraints beyond type checking.
        Default: no constraints (type checking only).
        """
        ...

    @classmethod
    def germinate(cls, **kwargs: Any) -> Self:
        """
        Create validated DNA from keyword arguments.

        Raises DNAValidationError if constraint validation fails.
        """
        ...

    def express(self, trait: str) -> Any:
        """
        Express a derived trait from the DNA.

        Traits are computed from base DNA. For example:
        - creativity=0.8 -> temperature=1.2
        - risk_tolerance=0.3 -> max_retries=5
        """
        ...


# === DNA Modifier ===


@dataclass(frozen=True)
class DNAModifier:
    """
    Modifier that adjusts trait expression contextually.

    Example: UrgencyModifier reduces max_retries under time pressure.
    """

    name: str

    def modify(self, trait: str, value: Any) -> Any:
        """
        Modify a trait value based on context.

        Default: return unchanged.
        """
        return value


# === Composed DNA ===


@dataclass(frozen=True)
class ComposedDNA:
    """
    DNA that combines traits from multiple sources.

    Modifiers are applied in order to base expressions.
    """

    base: Any  # Base DNA instance
    modifiers: tuple[DNAModifier, ...] = ()

    def express(self, trait: str) -> Any:
        """Express trait with modifiers applied."""
        # Start with base expression
        value = self.base.express(trait)

        # Apply modifiers in order
        for modifier in self.modifiers:
            value = modifier.modify(trait, value)

        return value

    def with_modifier(self, modifier: DNAModifier) -> "ComposedDNA":
        """Add a modifier, returning new ComposedDNA."""
        return ComposedDNA(
            base=self.base,
            modifiers=(*self.modifiers, modifier),
        )


# === Base DNA Implementation ===


@dataclass(frozen=True)
class BaseDNA:
    """
    Base class for concrete DNA implementations.

    Provides default implementations of DNA protocol methods.
    Subclass and add fields for specific agent DNA.

    Example:
        @dataclass(frozen=True)
        class KgentDNA(BaseDNA):
            personality: str = "curious"
            warmth: float = 0.7

            @classmethod
            def constraints(cls) -> list[Constraint]:
                return [
                    Constraint(
                        name="warmth_range",
                        check=lambda d: 0 <= d.warmth <= 1,
                        message="warmth must be 0-1",
                    ),
                ]
    """

    # The Accursed Share: exploration budget (Meta principle)
    exploration_budget: float = 0.1

    @classmethod
    def constraints(cls) -> list[Constraint]:
        """
        Return semantic constraints for this DNA type.

        Default includes positive exploration (Accursed Share).
        """
        return [
            Constraint(
                name="positive_exploration",
                check=lambda d: getattr(d, "exploration_budget", 0.1) > 0,
                message="Must allocate some budget for exploration (Accursed Share)",
            ),
            Constraint(
                name="bounded_exploration",
                check=lambda d: getattr(d, "exploration_budget", 0.1) <= 0.5,
                message="Exploration budget cannot exceed 50%",
            ),
        ]

    @classmethod
    def germinate(cls, **kwargs: Any) -> Self:
        """
        Create validated DNA from keyword arguments.

        Raises DNAValidationError if constraint validation fails.
        """
        # Construct instance
        instance = cls(**kwargs)

        # Validate against constraints
        errors = []
        for constraint in cls.constraints():
            valid, msg = constraint.validate(instance)
            if not valid:
                errors.append(f"{constraint.name}: {msg}")

        if errors:
            raise DNAValidationError(
                dna_type=cls.__name__,
                errors=errors,
            )

        return instance

    def express(self, trait: str) -> Any:
        """
        Express a derived trait from the DNA.

        Default: map standard traits. Override for custom expressions.
        """
        # Standard trait derivations
        expressions = self._standard_expressions()

        if trait in expressions:
            return expressions[trait]

        raise TraitNotFoundError(f"Unknown trait: {trait}")

    def _standard_expressions(self) -> dict[str, Any]:
        """
        Standard trait expressions derived from base DNA.

        Override to customize or extend.
        """
        exploration = getattr(self, "exploration_budget", 0.1)

        return {
            # Exploration derived from exploration_budget
            "exploration_probability": exploration,
            "exploit_probability": 1 - exploration,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert DNA to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create DNA from dictionary (via germinate for validation)."""
        return cls.germinate(**data)


# === LLM Agent DNA ===


@dataclass(frozen=True)
class LLMAgentDNA(BaseDNA):
    """
    DNA for agents that call LLMs.

    Adds creativity and verbosity traits with derived
    temperature and sampling parameters.
    """

    creativity: float = 0.5  # 0.0 to 1.0
    verbosity: str = "concise"  # "concise" | "detailed" | "verbose"

    @classmethod
    def constraints(cls) -> list[Constraint]:
        """LLM-specific constraints."""
        base = super().constraints()
        return base + [
            Constraint(
                name="creativity_range",
                check=lambda d: 0 <= d.creativity <= 1,
                message="creativity must be 0.0 to 1.0",
            ),
            Constraint(
                name="valid_verbosity",
                check=lambda d: d.verbosity in ("concise", "detailed", "verbose"),
                message="verbosity must be 'concise', 'detailed', or 'verbose'",
            ),
        ]

    def _standard_expressions(self) -> dict[str, Any]:
        """LLM trait expressions."""
        base = super()._standard_expressions()
        return {
            **base,
            # Temperature derived from creativity
            "temperature": 0.5 + (self.creativity * 0.7),
            "top_p": 0.7 + (self.creativity * 0.25),
            # Token limits derived from verbosity
            "max_tokens": {
                "concise": 256,
                "detailed": 1024,
                "verbose": 4096,
            }.get(self.verbosity, 512),
        }


# === Stateful Agent DNA ===


@dataclass(frozen=True)
class StatefulAgentDNA(BaseDNA):
    """
    DNA for agents with persistent state (D-gent integration).

    Adds history depth and auto-save preferences.
    """

    history_depth: int = 100
    auto_save: bool = True

    @classmethod
    def constraints(cls) -> list[Constraint]:
        """Stateful agent constraints."""
        base = super().constraints()
        return base + [
            Constraint(
                name="positive_history",
                check=lambda d: d.history_depth > 0,
                message="history_depth must be positive",
            ),
            Constraint(
                name="bounded_history",
                check=lambda d: d.history_depth <= 10000,
                message="history_depth cannot exceed 10000",
            ),
        ]

    def _standard_expressions(self) -> dict[str, Any]:
        """Stateful agent expressions."""
        base = super()._standard_expressions()
        return {
            **base,
            # Save frequency derived from history_depth
            "save_interval": max(1, self.history_depth // 10),
            "prune_threshold": self.history_depth * 2,
        }


# === Risk-Aware Agent DNA ===


@dataclass(frozen=True)
class RiskAwareAgentDNA(BaseDNA):
    """
    DNA for agents that handle uncertainty.

    Adds risk_tolerance with derived retry and fallback behavior.
    """

    risk_tolerance: float = 0.5  # 0.0 (cautious) to 1.0 (bold)

    @classmethod
    def constraints(cls) -> list[Constraint]:
        """Risk-aware constraints."""
        base = super().constraints()
        return base + [
            Constraint(
                name="risk_range",
                check=lambda d: 0 <= d.risk_tolerance <= 1,
                message="risk_tolerance must be 0.0 to 1.0",
            ),
        ]

    def _standard_expressions(self) -> dict[str, Any]:
        """Risk-aware expressions."""
        base = super()._standard_expressions()
        return {
            **base,
            # Retry behavior derived from risk tolerance
            "max_retries": int(5 - (self.risk_tolerance * 4)),
            "retry_delay": 1.0 + (2.0 * (1 - self.risk_tolerance)),
            # Fallback aggressiveness
            "fallback_threshold": 0.3 + (0.5 * self.risk_tolerance),
        }


# === Hypothesis Agent DNA (B-gent) ===


@dataclass(frozen=True)
class HypothesisDNA(BaseDNA):
    """
    DNA for B-gent hypothesis agents.

    Enforces epistemic humility and Popperian falsificationism.
    """

    confidence_threshold: float = 0.7
    falsification_required: bool = True
    max_hypotheses: int = 5

    @classmethod
    def constraints(cls) -> list[Constraint]:
        """Epistemic constraints for hypothesis agents."""
        base = super().constraints()
        return base + [
            # Epistemic humility: confidence cannot exceed 0.8
            Constraint(
                name="epistemic_humility",
                check=lambda d: d.confidence_threshold <= 0.8,
                message="Confidence threshold must not exceed 0.8 (Popperian)",
            ),
            # Falsification is non-negotiable for science
            Constraint(
                name="popperian_principle",
                check=lambda d: d.falsification_required is True,
                message="Falsification must be required (Popper)",
            ),
            # Resource bounds
            Constraint(
                name="hypothesis_budget",
                check=lambda d: 1 <= d.max_hypotheses <= 10,
                message="Hypothesis count must be 1-10",
            ),
        ]

    def _standard_expressions(self) -> dict[str, Any]:
        """Hypothesis agent expressions."""
        base = super()._standard_expressions()
        return {
            **base,
            # Prior probability ceiling
            "prior_ceiling": min(0.5, self.confidence_threshold),
            # Evidence required for acceptance
            "evidence_threshold": 1 - self.confidence_threshold,
            # Pruning aggressiveness
            "prune_below": self.confidence_threshold * 0.5,
        }


# === J-gent DNA ===


@dataclass(frozen=True)
class JGentDNA(BaseDNA):
    """
    DNA for J-gent judgment agents.

    Controls recursion depth and entropy budget.
    """

    max_depth: int = 5
    entropy_budget: float = 1.0  # Initial entropy budget
    decay_factor: float = 0.5  # Budget decay per depth

    @classmethod
    def constraints(cls) -> list[Constraint]:
        """J-gent constraints."""
        base = super().constraints()
        return base + [
            Constraint(
                name="bounded_depth",
                check=lambda d: 1 <= d.max_depth <= 20,
                message="max_depth must be 1-20",
            ),
            Constraint(
                name="positive_entropy",
                check=lambda d: d.entropy_budget > 0,
                message="entropy_budget must be positive",
            ),
            Constraint(
                name="valid_decay",
                check=lambda d: 0 < d.decay_factor < 1,
                message="decay_factor must be (0, 1)",
            ),
        ]

    def _standard_expressions(self) -> dict[str, Any]:
        """J-gent expressions."""
        base = super()._standard_expressions()
        return {
            **base,
            # Effective budget at max depth
            "min_budget": self.entropy_budget * (self.decay_factor**self.max_depth),
            # Recommended sub-promise count
            "max_branches": min(5, int(1 / self.decay_factor)),
        }


# === Urgency Modifier ===


@dataclass(frozen=True)
class UrgencyModifier(DNAModifier):
    """
    Modify traits based on urgency level.

    High urgency reduces retries and timeouts.
    """

    name: str = "urgency"
    urgency: float = 0.5  # 0.0 (relaxed) to 1.0 (critical)

    def modify(self, trait: str, value: Any) -> Any:
        """Apply urgency adjustments."""
        if trait == "max_retries":
            return max(1, int(value * (1 - self.urgency * 0.5)))
        if trait == "retry_delay":
            return value * (1 - self.urgency * 0.5)
        if trait == "max_tokens":
            return int(value * (1 - self.urgency * 0.3))
        return value


# === Context Modifier ===


@dataclass(frozen=True)
class ContextModifier(DNAModifier):
    """
    Modify traits based on runtime context.

    Example: production vs development modes.
    """

    name: str = "context"
    is_production: bool = False

    def modify(self, trait: str, value: Any) -> Any:
        """Apply context adjustments."""
        if self.is_production:
            # More conservative in production
            if trait == "temperature":
                return min(value, 0.7)
            if trait == "exploration_probability":
                return min(value, 0.05)
        return value


# === Standard Constraints Library ===

EPISTEMIC_HUMILITY = Constraint(
    name="epistemic_humility",
    check=lambda d: getattr(d, "confidence_threshold", 0.5) <= 0.8,
    message="Confidence threshold must not exceed 0.8",
)

POSITIVE_EXPLORATION = Constraint(
    name="positive_exploration",
    check=lambda d: getattr(d, "exploration_budget", 0.1) > 0,
    message="Must allocate some budget for exploration (Accursed Share)",
)

BOUNDED_DEPTH = Constraint(
    name="bounded_depth",
    check=lambda d: getattr(d, "max_depth", 5) <= 20,
    message="Recursion depth must be bounded",
)

POPPERIAN_PRINCIPLE = Constraint(
    name="popperian_principle",
    check=lambda d: getattr(d, "falsification_required", True) is True,
    message="Falsification must be required (Popper)",
)


__all__ = [
    # Errors
    "DNAValidationError",
    "TraitNotFoundError",
    # Core Types
    "Constraint",
    "DNA",
    "DNAModifier",
    "ComposedDNA",
    # Base Implementation
    "BaseDNA",
    # Specialized DNA
    "LLMAgentDNA",
    "StatefulAgentDNA",
    "RiskAwareAgentDNA",
    "HypothesisDNA",
    "JGentDNA",
    # Modifiers
    "UrgencyModifier",
    "ContextModifier",
    # Standard Constraints
    "EPISTEMIC_HUMILITY",
    "POSITIVE_EXPLORATION",
    "BOUNDED_DEPTH",
    "POPPERIAN_PRINCIPLE",
]
