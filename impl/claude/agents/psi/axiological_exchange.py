"""
Psi-gent AxiologicalExchange: The T-axis of the 4-axis tensor.

Controls axiological cost - value exchange rates for metaphor transformations.

Builds on B-gent ValueTensor for multi-dimensional value accounting.
Every metaphor trades values; the ValueTensor makes the trade measurable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .types import (
    AxisType,
    AntiPattern,
    AntiPatternDetection,
    Distortion,
    Novel,
    Projection,
    StabilityStatus,
    ValidationResult,
)


# =============================================================================
# Value Dimensions
# =============================================================================


class ValueDimension(Enum):
    """Dimensions of value in metaphor transformation."""

    PRAGMATIC = "pragmatic"  # Token/time cost, business value
    EPISTEMIC = "epistemic"  # Truth preserved through projection
    ETHICAL = "ethical"  # Moral cost of metaphor choices
    AESTHETIC = "aesthetic"  # Elegance of the transformation
    HEDONIC = "hedonic"  # Joy in the solution


@dataclass(frozen=True)
class DimensionValue:
    """Value in a single dimension."""

    dimension: ValueDimension
    value: float  # Normalized 0.0 to 1.0
    confidence: float = 0.5
    notes: str = ""


# =============================================================================
# Exchange Rate Types
# =============================================================================


@dataclass(frozen=True)
class ExchangeRate:
    """
    Exchange rate between value dimensions.

    Not all exchanges are lossless. The rate tracks:
    - rate: How much of B per unit of A
    - loss: Information/value lost in translation
    - confidence: How reliable is this rate
    """

    from_dim: ValueDimension
    to_dim: ValueDimension
    rate: float  # Units of target per unit of source
    loss: float  # Fraction lost in translation (0-1)
    confidence: float  # How reliable (0-1)
    method: str = "heuristic"


@dataclass(frozen=True)
class ConversionResult:
    """Result of converting between dimensions."""

    source_dim: ValueDimension
    target_dim: ValueDimension
    source_value: float
    converted_value: float
    loss: float
    rate_used: ExchangeRate


# =============================================================================
# Exchange Matrix
# =============================================================================


@dataclass
class ExchangeMatrix:
    """
    Matrix of exchange rates between dimensions.

    Lifted from B-gent ValueTensor into metaphor context.
    """

    rates: dict[tuple[ValueDimension, ValueDimension], ExchangeRate] = field(
        default_factory=dict
    )

    def __post_init__(self):
        # Initialize standard rates if empty
        if not self.rates:
            self._init_standard_rates()

    def _init_standard_rates(self) -> None:
        """Initialize standard exchange rates."""
        # Pragmatic <-> Epistemic (direct, medium loss)
        self.rates[(ValueDimension.PRAGMATIC, ValueDimension.EPISTEMIC)] = ExchangeRate(
            from_dim=ValueDimension.PRAGMATIC,
            to_dim=ValueDimension.EPISTEMIC,
            rate=0.8,
            loss=0.2,
            confidence=0.7,
            method="standard",
        )

        # Epistemic <-> Ethical (indirect, high loss)
        self.rates[(ValueDimension.EPISTEMIC, ValueDimension.ETHICAL)] = ExchangeRate(
            from_dim=ValueDimension.EPISTEMIC,
            to_dim=ValueDimension.ETHICAL,
            rate=0.5,
            loss=0.4,
            confidence=0.5,
            method="standard",
        )

        # Pragmatic <-> Ethical (policy-driven)
        self.rates[(ValueDimension.PRAGMATIC, ValueDimension.ETHICAL)] = ExchangeRate(
            from_dim=ValueDimension.PRAGMATIC,
            to_dim=ValueDimension.ETHICAL,
            rate=0.3,
            loss=0.5,
            confidence=0.6,
            method="policy",
        )

        # Aesthetic <-> Hedonic (high correlation)
        self.rates[(ValueDimension.AESTHETIC, ValueDimension.HEDONIC)] = ExchangeRate(
            from_dim=ValueDimension.AESTHETIC,
            to_dim=ValueDimension.HEDONIC,
            rate=0.9,
            loss=0.1,
            confidence=0.8,
            method="correlation",
        )

        # Add reverse rates
        for (from_d, to_d), rate in list(self.rates.items()):
            reverse_key = (to_d, from_d)
            if reverse_key not in self.rates:
                self.rates[reverse_key] = ExchangeRate(
                    from_dim=to_d,
                    to_dim=from_d,
                    rate=1.0 / rate.rate if rate.rate > 0 else 0.0,
                    loss=rate.loss,
                    confidence=rate.confidence
                    * 0.9,  # Slightly less confident in reverse
                    method=f"reverse_{rate.method}",
                )

    def get_rate(
        self, from_dim: ValueDimension, to_dim: ValueDimension
    ) -> ExchangeRate | None:
        """Get exchange rate between dimensions."""
        return self.rates.get((from_dim, to_dim))

    def convert(
        self, value: float, from_dim: ValueDimension, to_dim: ValueDimension
    ) -> ConversionResult:
        """
        Convert value between dimensions.

        Returns converted value and loss.
        """
        if from_dim == to_dim:
            return ConversionResult(
                source_dim=from_dim,
                target_dim=to_dim,
                source_value=value,
                converted_value=value,
                loss=0.0,
                rate_used=ExchangeRate(
                    from_dim=from_dim,
                    to_dim=to_dim,
                    rate=1.0,
                    loss=0.0,
                    confidence=1.0,
                    method="identity",
                ),
            )

        rate = self.get_rate(from_dim, to_dim)
        if rate is None:
            # No direct rate - use default lossy conversion
            rate = ExchangeRate(
                from_dim=from_dim,
                to_dim=to_dim,
                rate=0.5,
                loss=0.5,
                confidence=0.3,
                method="default",
            )

        converted = value * rate.rate * (1 - rate.loss)
        loss = value * rate.loss

        return ConversionResult(
            source_dim=from_dim,
            target_dim=to_dim,
            source_value=value,
            converted_value=converted,
            loss=loss,
            rate_used=rate,
        )


# =============================================================================
# Value Tensor (for Metaphor Context)
# =============================================================================


@dataclass(frozen=True)
class MetaphorValueTensor:
    """
    Multi-dimensional value state for a metaphor transformation.

    Tracks value across all dimensions to measure the cost
    of metaphor projection/reification.
    """

    pragmatic: DimensionValue
    epistemic: DimensionValue
    ethical: DimensionValue
    aesthetic: DimensionValue
    hedonic: DimensionValue

    @classmethod
    def from_projection(cls, projection: Projection) -> MetaphorValueTensor:
        """Create a value tensor from a projection."""
        return cls(
            pragmatic=DimensionValue(
                dimension=ValueDimension.PRAGMATIC,
                value=projection.coverage,  # Coverage as pragmatic value
                confidence=projection.confidence,
                notes="Pragmatic value from projection coverage",
            ),
            epistemic=DimensionValue(
                dimension=ValueDimension.EPISTEMIC,
                value=projection.confidence,  # Confidence as epistemic value
                confidence=projection.confidence,
                notes="Epistemic value from mapping confidence",
            ),
            ethical=DimensionValue(
                dimension=ValueDimension.ETHICAL,
                value=0.5,  # Default neutral
                confidence=0.5,
                notes="Ethical value requires shadow analysis",
            ),
            aesthetic=DimensionValue(
                dimension=ValueDimension.AESTHETIC,
                value=projection.target.tractability,  # Elegance from tractability
                confidence=0.6,
                notes="Aesthetic value from metaphor tractability",
            ),
            hedonic=DimensionValue(
                dimension=ValueDimension.HEDONIC,
                value=0.5,  # Default neutral
                confidence=0.5,
                notes="Hedonic value from solution engagement",
            ),
        )

    @property
    def total_value(self) -> float:
        """Calculate total value (weighted sum)."""
        weights = {
            ValueDimension.PRAGMATIC: 0.3,
            ValueDimension.EPISTEMIC: 0.3,
            ValueDimension.ETHICAL: 0.2,
            ValueDimension.AESTHETIC: 0.1,
            ValueDimension.HEDONIC: 0.1,
        }
        values = [
            self.pragmatic,
            self.epistemic,
            self.ethical,
            self.aesthetic,
            self.hedonic,
        ]
        return sum(v.value * weights[v.dimension] for v in values)


# =============================================================================
# Loss Report
# =============================================================================


@dataclass(frozen=True)
class LossReport:
    """
    Report on value loss through metaphor transformation.
    """

    conversions: tuple[ConversionResult, ...]
    total_loss: float
    distortion_delta: float
    anomalies: tuple[str, ...] = ()

    @property
    def is_acceptable(self) -> bool:
        """Is the loss acceptable?"""
        return self.total_loss < 0.5 and not self.anomalies


# =============================================================================
# Axiological Exchange
# =============================================================================


@dataclass
class AxiologicalExchange:
    """
    The T-axis controller: axiological cost exchange.

    Manages value accounting for metaphor transformations.
    Every metaphor trades values; this makes the trade measurable.

    Responsibilities:
    1. Calculate value tensor for projections
    2. Track value loss through transformation
    3. Detect value blindness anti-pattern
    4. Integrate with B-gent conservation laws
    """

    # Configuration
    loss_threshold: float = 0.5  # Above this = too costly
    exchange_matrix: ExchangeMatrix = field(default_factory=ExchangeMatrix)

    def calculate_tensor(self, projection: Projection) -> MetaphorValueTensor:
        """Calculate the value tensor for a projection."""
        return MetaphorValueTensor.from_projection(projection)

    def measure_loss(
        self, source: Novel, projection: Projection, distortion: Distortion
    ) -> LossReport:
        """
        Measure total value loss through the metaphor transformation.

        Accounts for:
        - Distortion loss (semantic)
        - Exchange rate losses (dimensional)
        - Conservation violations (anomalies)
        """
        tensor = self.calculate_tensor(projection)
        conversions: list[ConversionResult] = []
        total_loss = 0.0
        anomalies: list[str] = []

        # Calculate loss from distortion
        distortion_loss = distortion.delta * 0.5  # Weight distortion at 50%
        total_loss += distortion_loss

        # Calculate loss from dimension conversions
        # (When projecting, we "convert" problem values to metaphor values)
        source_pragmatic = source.complexity  # Complexity as pragmatic value
        result = self.exchange_matrix.convert(
            source_pragmatic, ValueDimension.PRAGMATIC, ValueDimension.EPISTEMIC
        )
        conversions.append(result)
        total_loss += result.loss * 0.3

        # Check for anomalies (conservation violations)
        if tensor.total_value < 0.2:
            anomalies.append(
                "Total value suspiciously low - possible value destruction"
            )

        if tensor.epistemic.value > 0.9 and distortion.delta > 0.5:
            anomalies.append(
                "High epistemic confidence with high distortion - possible delusion"
            )

        return LossReport(
            conversions=tuple(conversions),
            total_loss=min(1.0, total_loss),
            distortion_delta=distortion.delta,
            anomalies=tuple(anomalies),
        )

    def validate(
        self, projection: Projection, distortion: Distortion
    ) -> ValidationResult:
        """
        Validate axiological cost of a transformation.

        Returns a ValidationResult for the T-axis.
        """
        loss_report = self.measure_loss(projection.source, projection, distortion)

        if loss_report.is_acceptable and loss_report.total_loss < 0.3:
            return ValidationResult(
                axis=AxisType.T_AXIOLOGICAL,
                status=StabilityStatus.STABLE,
                score=1.0 - loss_report.total_loss,
                message="Value exchange is efficient",
                details={
                    "total_loss": loss_report.total_loss,
                    "distortion": loss_report.distortion_delta,
                },
            )
        elif loss_report.is_acceptable:
            return ValidationResult(
                axis=AxisType.T_AXIOLOGICAL,
                status=StabilityStatus.FRAGILE,
                score=1.0 - loss_report.total_loss,
                message=f"Value loss at {loss_report.total_loss:.1%}",
                details={
                    "total_loss": loss_report.total_loss,
                    "conversions": len(loss_report.conversions),
                },
            )
        else:
            return ValidationResult(
                axis=AxisType.T_AXIOLOGICAL,
                status=StabilityStatus.UNSTABLE,
                score=1.0 - loss_report.total_loss,
                message=f"Excessive value loss: {loss_report.total_loss:.1%}",
                details={
                    "total_loss": loss_report.total_loss,
                    "anomalies": list(loss_report.anomalies),
                },
            )

    def detect_value_blindness(
        self, projection: Projection, distortion: Distortion
    ) -> AntiPatternDetection:
        """
        Detect the value blindness anti-pattern.

        Value blindness = ignoring the ethical cost of metaphor choice.
        """
        tensor = self.calculate_tensor(projection)
        loss_report = self.measure_loss(projection.source, projection, distortion)

        # Value blindness indicators:
        # 1. High pragmatic value but low ethical consideration
        # 2. High confidence but unexamined costs

        high_pragmatic = tensor.pragmatic.value > 0.7
        low_ethical = tensor.ethical.value < 0.4 and tensor.ethical.confidence < 0.5
        has_anomalies = len(loss_report.anomalies) > 0

        detected = (high_pragmatic and low_ethical) or has_anomalies

        return AntiPatternDetection(
            pattern=AntiPattern.VALUE_BLINDNESS,
            detected=detected,
            confidence=0.6 if detected else 0.0,
            evidence=(
                f"Pragmatic={tensor.pragmatic.value:.2f}, "
                f"Ethical={tensor.ethical.value:.2f}"
                if detected
                else ""
            ),
            mitigation="Explicitly evaluate ethical dimensions of metaphor choice",
        )

    def calculate_roi(self, projection: Projection, distortion: Distortion) -> float:
        """
        Calculate Return on Investment for the metaphor transformation.

        ROI = (Value Gained) / (Cost Incurred)
        """
        tensor = self.calculate_tensor(projection)
        loss_report = self.measure_loss(projection.source, projection, distortion)

        value_gained = tensor.total_value * (1.0 - distortion.delta)
        cost_incurred = loss_report.total_loss + 0.1  # Baseline cost

        return value_gained / cost_incurred if cost_incurred > 0 else 0.0
