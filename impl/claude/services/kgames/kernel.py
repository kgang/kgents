"""
KGames Kernel: The Four Axioms of Game Experience Quality.

The GameKernel operationalizes the four axioms discovered through wasm-survivors:
- A1: AGENCY (L=0.02) - Player choices determine outcomes
- A2: ATTRIBUTION (L=0.05) - Outcomes trace to identifiable causes
- A3: MASTERY (L=0.08) - Skill development is externally observable
- A4: COMPOSITION (L=0.03) - Moments compose algebraically into arcs

These axioms are constitutional - violations mean Quality = 0.

Philosophy:
    "The axioms are not design guidelines - they are categorical constraints.
     Violate one, and the game ceases to be a game."

The Witness Integration (Mark -> Trace -> Crystal):
    - Marks capture decision points for A1 (agency) and A2 (attribution)
    - Traces accumulate skill metrics for A3 (mastery)
    - Crystals compose moments into arcs for A4 (composition)

See: pilots/wasm-survivors-game/systems/axiom-guards.ts
See: spec/agents/kgames-kernel.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Protocol, runtime_checkable

# =============================================================================
# Axiom Result Types
# =============================================================================


class AxiomSeverity(Enum):
    """Severity of an axiom violation."""

    CRITICAL = "critical"  # Quality = 0, game is broken
    WARNING = "warning"  # Quality reduced, needs attention
    INFO = "info"  # Advisory, not a violation


@dataclass(frozen=True)
class AxiomViolation:
    """
    A specific violation of an axiom.

    Violations have severity levels:
    - CRITICAL: Game is fundamentally broken (Q = 0)
    - WARNING: Quality degraded, needs attention
    - INFO: Advisory information

    Example:
        AxiomViolation(
            axiom="A1",
            severity=AxiomSeverity.CRITICAL,
            message="Death has no causal chain",
            details="Player died without any traceable decisions",
            context={"deathTime": 12.5, "wave": 3},
        )
    """

    axiom: str  # A1, A2, A3, A4
    severity: AxiomSeverity
    message: str
    details: str
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "axiom": self.axiom,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "context": self.context,
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        prefix = "[CRITICAL]" if self.severity == AxiomSeverity.CRITICAL else "[WARNING]"
        return f"{prefix} {self.axiom}: {self.message}\n  {self.details}"


@dataclass(frozen=True)
class AxiomResult:
    """
    Result of validating an axiom against an implementation.

    A passing result has no violations.
    A failing result has one or more violations.

    Quality formula:
    - CRITICAL violations: Q = 0
    - WARNING violations: Q = 1 - (0.1 * warning_count)
    - INFO violations: No quality impact
    """

    axiom: str
    passed: bool
    violations: tuple[AxiomViolation, ...] = field(default_factory=tuple)
    quality_score: float = 1.0  # 0.0 to 1.0, 0 if critical violation

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "axiom": self.axiom,
            "passed": self.passed,
            "violations": [v.to_dict() for v in self.violations],
            "quality_score": self.quality_score,
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        status = "PASS" if self.passed else "FAIL"
        lines = [f"{self.axiom}: {status} (Q={self.quality_score:.2f})"]
        for v in self.violations:
            lines.append(f"  - {v.message}")
        return "\n".join(lines)


# =============================================================================
# Implementation Protocol
# =============================================================================


@runtime_checkable
class GameImplementation(Protocol):
    """
    Protocol for game implementations that can be validated against axioms.

    Implementations must provide evidence for each axiom:
    - death_contexts: For A1 (agency) and A2 (attribution)
    - skill_metrics: For A3 (mastery)
    - arc_history: For A4 (composition)
    """

    def get_death_contexts(self) -> list[dict[str, Any]]:
        """
        Get death contexts for A1/A2 validation.

        Each context must include:
        - causalChain: list of decisions leading to death
        - specificCause: human-readable cause (<50 chars)
        - killerType: what killed the player (for combat deaths)
        """
        ...

    def get_skill_metrics(self) -> list[dict[str, Any]]:
        """
        Get skill metrics for A3 validation.

        Each metric snapshot must include:
        - attacksEncountered: total attacks directed at player
        - attacksEvaded: attacks player successfully dodged
        - dodgeRate: attacksEvaded / attacksEncountered
        - survivalTime: how long the player survived
        """
        ...

    def get_arc_history(self) -> dict[str, Any]:
        """
        Get arc history for A4 validation.

        Must include:
        - phases: list of arc phases visited
        - hasDefiniteClosure: whether the run ended definitively
        - closureType: 'dignity' (earned) or 'arbitrary' (unfair)
        """
        ...


# =============================================================================
# A1: AGENCY AXIOM
# =============================================================================


@dataclass(frozen=True)
class AgencyAxiom:
    """
    A1: Player choices determine outcomes.

    The Agency Axiom ensures that every significant outcome (especially death)
    can be traced back to player decisions. Without agency, the game is just
    watching a random number generator.

    Galois Loss: L = 0.02 (near-lossless, fundamental)

    Validation Rules:
    1. Every death must have a causal chain
    2. Causal chain must contain at least one player decision
    3. Player must have had time to react (>500ms from threat to death)

    Example violation:
        Player spawns and dies immediately to an off-screen enemy.
        There was no decision to trace - the death was arbitrary.

    Evidence required:
        - causalChain: list of {actor, action, consequence, gameTime}
        - gameTime: when the death occurred

    Philosophy:
        "The player is the author of their fate, not the audience."
    """

    galois_loss: float = 0.02

    def validate(self, implementation: GameImplementation) -> AxiomResult:
        """
        Validate A1: Every death traces to player decisions.

        Checks:
        1. Death has a causal chain (not empty)
        2. At least one player decision in chain
        3. Sufficient reaction time (>500ms)
        """
        violations: list[AxiomViolation] = []

        death_contexts = implementation.get_death_contexts()

        for ctx in death_contexts:
            causal_chain = ctx.get("causalChain", [])
            game_time = ctx.get("gameTime", 0)

            # Check 1: Causal chain exists
            if not causal_chain:
                violations.append(
                    AxiomViolation(
                        axiom="A1",
                        severity=AxiomSeverity.CRITICAL,
                        message="Death has no causal chain",
                        details="Every death must trace to a sequence of decisions.",
                        context=ctx,
                    )
                )
                continue

            # Check 2: Player decisions in chain
            player_decisions = [d for d in causal_chain if d.get("actor") == "player"]
            if not player_decisions:
                violations.append(
                    AxiomViolation(
                        axiom="A1",
                        severity=AxiomSeverity.CRITICAL,
                        message="No player decisions in causal chain",
                        details="Death occurred without any player input.",
                        context={"chain": causal_chain},
                    )
                )
                continue

            # Check 3: Reaction time
            first_threat_time = causal_chain[0].get("gameTime", 0)
            reaction_time = game_time - first_threat_time
            if reaction_time < 500:  # Less than 500ms
                violations.append(
                    AxiomViolation(
                        axiom="A1",
                        severity=AxiomSeverity.WARNING,
                        message="Reaction time may be insufficient",
                        details=f"Only {reaction_time}ms from first threat to death.",
                        context={"reactionTimeMs": reaction_time},
                    )
                )

        return self._compute_result(violations)

    def _compute_result(self, violations: list[AxiomViolation]) -> AxiomResult:
        """Compute result from violations."""
        has_critical = any(v.severity == AxiomSeverity.CRITICAL for v in violations)
        warning_count = sum(1 for v in violations if v.severity == AxiomSeverity.WARNING)

        if has_critical:
            quality = 0.0
        else:
            quality = max(0.0, 1.0 - (warning_count * 0.1))

        return AxiomResult(
            axiom="A1",
            passed=not has_critical,
            violations=tuple(violations),
            quality_score=quality,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": "A1",
            "name": "Agency",
            "description": "Player choices determine outcomes",
            "galois_loss": self.galois_loss,
            "equation": "death -> causal_chain -> player_decisions",
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        return (
            "A1: AGENCY (L=0.02)\n"
            "Player choices determine outcomes.\n"
            "Every death must trace to player decisions."
        )


# =============================================================================
# A2: ATTRIBUTION AXIOM
# =============================================================================


@dataclass(frozen=True)
class AttributionAxiom:
    """
    A2: Every outcome traces to an identifiable cause.

    The Attribution Axiom ensures that players can always articulate
    WHY they died (or succeeded). Without attribution, learning is impossible.

    Galois Loss: L = 0.05 (very low loss, near-fundamental)

    Validation Rules:
    1. Death cause must be specified (not empty)
    2. Death cause must be concise (<50 chars for quick comprehension)
    3. Death cause must be specific (not generic like "you died")
    4. For combat deaths, killer type must be identified

    Example violation:
        Death screen shows "Game Over" with no explanation.
        Player cannot learn because they don't know what killed them.

    Evidence required:
        - specificCause: human-readable cause string
        - killerType: what killed the player (for combat deaths)
        - cause: category (combat, ball, overwhelmed)

    Philosophy:
        "If you can't name it, you can't learn from it."
    """

    galois_loss: float = 0.05

    def validate(self, implementation: GameImplementation) -> AxiomResult:
        """
        Validate A2: Every death has identifiable cause.

        Checks:
        1. Specific cause exists
        2. Cause is concise (<50 chars)
        3. Cause is specific (not generic)
        4. Killer identified for combat deaths
        """
        violations: list[AxiomViolation] = []
        generic_causes = frozenset({"you died", "game over", "combat", "damage", "dead"})

        death_contexts = implementation.get_death_contexts()

        for ctx in death_contexts:
            specific_cause = ctx.get("specificCause", "")
            cause = ctx.get("cause", "")
            killer_type = ctx.get("killerType")

            # Check 1: Cause exists
            if not specific_cause or not specific_cause.strip():
                violations.append(
                    AxiomViolation(
                        axiom="A2",
                        severity=AxiomSeverity.CRITICAL,
                        message="Death cause not specified",
                        details="Player cannot articulate why they died.",
                        context={"cause": cause},
                    )
                )
                continue

            # Check 2: Cause is concise
            if len(specific_cause) > 50:
                violations.append(
                    AxiomViolation(
                        axiom="A2",
                        severity=AxiomSeverity.WARNING,
                        message="Death cause too verbose",
                        details=f"Cause is {len(specific_cause)} chars. Should be <50.",
                        context={"specificCause": specific_cause},
                    )
                )

            # Check 3: Cause is specific
            if specific_cause.lower() in generic_causes:
                violations.append(
                    AxiomViolation(
                        axiom="A2",
                        severity=AxiomSeverity.CRITICAL,
                        message="Death cause is too generic",
                        details=f'"{specific_cause}" tells the player nothing.',
                        context={"genericCause": specific_cause},
                    )
                )

            # Check 4: Killer identified for combat
            if cause == "combat" and not killer_type:
                violations.append(
                    AxiomViolation(
                        axiom="A2",
                        severity=AxiomSeverity.CRITICAL,
                        message="Killer not identified",
                        details="Combat death but no killer type specified.",
                        context={"cause": cause, "killerType": killer_type},
                    )
                )

        return self._compute_result(violations)

    def _compute_result(self, violations: list[AxiomViolation]) -> AxiomResult:
        """Compute result from violations."""
        has_critical = any(v.severity == AxiomSeverity.CRITICAL for v in violations)
        warning_count = sum(1 for v in violations if v.severity == AxiomSeverity.WARNING)

        if has_critical:
            quality = 0.0
        else:
            quality = max(0.0, 1.0 - (warning_count * 0.1))

        return AxiomResult(
            axiom="A2",
            passed=not has_critical,
            violations=tuple(violations),
            quality_score=quality,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": "A2",
            "name": "Attribution",
            "description": "Outcomes trace to identifiable causes",
            "galois_loss": self.galois_loss,
            "equation": "outcome -> cause.articulate() in 2s",
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        return (
            "A2: ATTRIBUTION (L=0.05)\n"
            "Outcomes trace to identifiable causes.\n"
            "Player can articulate cause within 2 seconds."
        )


# =============================================================================
# A3: MASTERY AXIOM
# =============================================================================


@dataclass(frozen=True)
class MasteryAxiom:
    """
    A3: Skill development is externally observable.

    The Mastery Axiom ensures that player improvement is measurable
    and visible. Run 10 must look different from Run 1.

    Galois Loss: L = 0.08 (low loss, empirically verifiable)

    Validation Rules:
    1. Skill metrics must be measurements, not estimates
    2. Dodge rate must be mathematically possible
    3. Metrics must be consistent (computed matches provided)
    4. Improvement must be visible across runs

    Example violation:
        Game tracks "estimated skill" but never measures actual dodges.
        Without measurement, A3 is just a guess.

    Evidence required:
        - attacksEncountered: actual count of attacks
        - attacksEvaded: actual count of successful dodges
        - dodgeRate: attacksEvaded / attacksEncountered

    Philosophy:
        "You improve what you measure. Measure real actions."
    """

    galois_loss: float = 0.08

    def validate(self, implementation: GameImplementation) -> AxiomResult:
        """
        Validate A3: Skill metrics are real measurements.

        Checks:
        1. Required metrics exist
        2. Dodge rate is mathematically possible
        3. Computed values match provided values
        """
        violations: list[AxiomViolation] = []

        skill_metrics = implementation.get_skill_metrics()

        for metrics in skill_metrics:
            attacks_encountered = metrics.get("attacksEncountered")
            attacks_evaded = metrics.get("attacksEvaded")
            dodge_rate = metrics.get("dodgeRate", 0)

            # Check 1: Required metrics exist
            if attacks_encountered is None or attacks_evaded is None:
                violations.append(
                    AxiomViolation(
                        axiom="A3",
                        severity=AxiomSeverity.CRITICAL,
                        message="Skill metrics not measured",
                        details="attacksEncountered and attacksEvaded must be tracked.",
                        context=metrics,
                    )
                )
                continue

            # Check 2: Dodge rate is possible
            if attacks_evaded > attacks_encountered:
                violations.append(
                    AxiomViolation(
                        axiom="A3",
                        severity=AxiomSeverity.CRITICAL,
                        message="Impossible dodge rate",
                        details=f"Evaded {attacks_evaded} > encountered {attacks_encountered}.",
                        context={"evaded": attacks_evaded, "encountered": attacks_encountered},
                    )
                )
                continue

            # Check 3: Consistency
            computed_rate = attacks_evaded / attacks_encountered if attacks_encountered > 0 else 0
            if abs(computed_rate - dodge_rate) > 0.01:
                violations.append(
                    AxiomViolation(
                        axiom="A3",
                        severity=AxiomSeverity.WARNING,
                        message="Dodge rate inconsistency",
                        details=f"Provided {dodge_rate:.3f} differs from computed {computed_rate:.3f}.",
                        context={"provided": dodge_rate, "computed": computed_rate},
                    )
                )

        return self._compute_result(violations)

    def _compute_result(self, violations: list[AxiomViolation]) -> AxiomResult:
        """Compute result from violations."""
        has_critical = any(v.severity == AxiomSeverity.CRITICAL for v in violations)
        warning_count = sum(1 for v in violations if v.severity == AxiomSeverity.WARNING)

        if has_critical:
            quality = 0.0
        else:
            quality = max(0.0, 1.0 - (warning_count * 0.1))

        return AxiomResult(
            axiom="A3",
            passed=not has_critical,
            violations=tuple(violations),
            quality_score=quality,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": "A3",
            "name": "Mastery",
            "description": "Skill development is externally observable",
            "galois_loss": self.galois_loss,
            "equation": "run_10.metrics != run_1.metrics",
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        return (
            "A3: MASTERY (L=0.08)\n"
            "Skill development is externally observable.\n"
            "Run 10 must look different from Run 1."
        )


# =============================================================================
# A4: COMPOSITION AXIOM
# =============================================================================


@dataclass(frozen=True)
class CompositionAxiom:
    """
    A4: Moments compose algebraically into arcs.

    The Composition Axiom ensures that individual moments combine into
    meaningful narrative arcs. A run is not just "stuff happened" but
    a coherent journey with peaks, valleys, and closure.

    Galois Loss: L = 0.03 (very low loss, structural)

    Validation Rules:
    1. Run must visit at least 3 arc phases
    2. Arc must have both peak (flow/power) and valley (crisis/tragedy)
    3. Closure must be definite (not fade-out)
    4. Closure must be dignified (earned, not arbitrary)

    Example violation:
        Game ends abruptly with no sense of closure.
        Player feels cheated rather than satisfied.

    Evidence required:
        - phases: list of arc phases visited
        - hasDefiniteClosure: boolean
        - closureType: 'dignity' or 'arbitrary'

    Philosophy:
        "The whole is greater than the sum of its parts.
         Moments compose; they don't just accumulate."
    """

    galois_loss: float = 0.03

    def validate(self, implementation: GameImplementation) -> AxiomResult:
        """
        Validate A4: Moments compose into arcs.

        Checks:
        1. At least 3 unique phases visited
        2. Has both peak and valley phases
        3. Definite closure exists
        4. Closure is dignified (not arbitrary)
        """
        violations: list[AxiomViolation] = []

        arc_history = implementation.get_arc_history()
        phases = arc_history.get("phases", [])
        has_closure = arc_history.get("hasDefiniteClosure", False)
        closure_type = arc_history.get("closureType")

        # Check 1: Phase coverage
        unique_phases = set(phases)
        if len(unique_phases) < 3:
            violations.append(
                AxiomViolation(
                    axiom="A4",
                    severity=AxiomSeverity.WARNING,
                    message="Insufficient arc phase coverage",
                    details=f"Only {len(unique_phases)} unique phases. Need at least 3.",
                    context={"phases": list(unique_phases)},
                )
            )

        # Check 2: Peak and valley
        peak_phases = {"FLOW", "POWER"}
        valley_phases = {"CRISIS", "TRAGEDY"}
        has_peak = bool(unique_phases & peak_phases)
        has_valley = bool(unique_phases & valley_phases)

        if not has_peak or not has_valley:
            violations.append(
                AxiomViolation(
                    axiom="A4",
                    severity=AxiomSeverity.WARNING,
                    message="Arc missing peak or valley",
                    details=f"Peak: {has_peak}, Valley: {has_valley}. Need both.",
                    context={"hasPeak": has_peak, "hasValley": has_valley},
                )
            )

        # Check 3: Definite closure
        if not has_closure:
            violations.append(
                AxiomViolation(
                    axiom="A4",
                    severity=AxiomSeverity.WARNING,
                    message="Arc has no definite closure",
                    details="The arc faded out instead of ending definitively.",
                    context={},
                )
            )

        # Check 4: Dignified closure
        if closure_type == "arbitrary":
            violations.append(
                AxiomViolation(
                    axiom="A4",
                    severity=AxiomSeverity.CRITICAL,
                    message="Arbitrary closure",
                    details="Death felt random/unfair rather than earned.",
                    context={"closureType": closure_type},
                )
            )

        return self._compute_result(violations)

    def _compute_result(self, violations: list[AxiomViolation]) -> AxiomResult:
        """Compute result from violations."""
        has_critical = any(v.severity == AxiomSeverity.CRITICAL for v in violations)
        warning_count = sum(1 for v in violations if v.severity == AxiomSeverity.WARNING)

        if has_critical:
            quality = 0.0
        else:
            quality = max(0.0, 1.0 - (warning_count * 0.1))

        return AxiomResult(
            axiom="A4",
            passed=not has_critical,
            violations=tuple(violations),
            quality_score=quality,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": "A4",
            "name": "Composition",
            "description": "Moments compose algebraically into arcs",
            "galois_loss": self.galois_loss,
            "equation": "quality(arc) = compose(moment_1, moment_2, ...)",
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        return (
            "A4: COMPOSITION (L=0.03)\n"
            "Moments compose algebraically into arcs.\n"
            "Runs have peaks, valleys, and dignified closure."
        )


# =============================================================================
# VALIDATION RESULT
# =============================================================================


@dataclass(frozen=True)
class ValidationResult:
    """
    Complete validation result for all four axioms.

    Quality score formula:
    - If any axiom has critical violation: Q = 0
    - Otherwise: Q = min(A1.quality, A2.quality, A3.quality, A4.quality)

    The minimum ensures that ALL axioms must pass for quality.
    """

    agency: AxiomResult
    attribution: AxiomResult
    mastery: AxiomResult
    composition: AxiomResult
    overall_quality: float
    is_valid: bool  # True if all axioms passed (no critical violations)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "agency": self.agency.to_dict(),
            "attribution": self.attribution.to_dict(),
            "mastery": self.mastery.to_dict(),
            "composition": self.composition.to_dict(),
            "overall_quality": self.overall_quality,
            "is_valid": self.is_valid,
            "passed_axioms": [
                a.axiom
                for a in [self.agency, self.attribution, self.mastery, self.composition]
                if a.passed
            ],
            "failed_axioms": [
                a.axiom
                for a in [self.agency, self.attribution, self.mastery, self.composition]
                if not a.passed
            ],
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        status = "VALID" if self.is_valid else "INVALID"
        lines = [
            "=== GAME KERNEL VALIDATION ===",
            f"Status: {status}",
            f"Quality: {self.overall_quality:.1%}",
            "",
            self.agency.to_text(),
            self.attribution.to_text(),
            self.mastery.to_text(),
            self.composition.to_text(),
            "==============================",
        ]
        return "\n".join(lines)


# =============================================================================
# GAME KERNEL
# =============================================================================


@dataclass
class GameKernel:
    """
    The GameKernel: Four Axioms for Game Experience Quality.

    The kernel holds the four axioms that define what makes a game
    worth playing. Implementations are validated against these axioms.

    Usage:
        kernel = GameKernel()

        # View axioms
        print(kernel.agency.to_text())

        # Validate implementation
        result = kernel.validate_implementation(my_game)
        if result.is_valid:
            print("Game passes all axioms!")
        else:
            print(f"Quality: {result.overall_quality:.1%}")

    The Witness Integration:
        The kernel integrates with the Witness system (Mark -> Trace -> Crystal):
        - A1/A2: Death contexts from Marks (who decided what, what caused death)
        - A3: Skill metrics from Traces (accumulated measurements)
        - A4: Arc phases from Crystal segments (composed narrative)

    Philosophy:
        "The kernel is not a style guide. It is a theorem prover.
         Either your game satisfies the axioms, or it doesn't."
    """

    agency: AgencyAxiom = field(default_factory=AgencyAxiom)
    attribution: AttributionAxiom = field(default_factory=AttributionAxiom)
    mastery: MasteryAxiom = field(default_factory=MasteryAxiom)
    composition: CompositionAxiom = field(default_factory=CompositionAxiom)

    def validate_implementation(self, impl: GameImplementation) -> ValidationResult:
        """
        Validate a game implementation against all four axioms.

        Returns a ValidationResult with per-axiom results and overall quality.

        The quality score is the minimum of all axiom scores, ensuring that
        ALL axioms must pass for high quality. A single critical violation
        in any axiom sets quality to 0.
        """
        agency_result = self.agency.validate(impl)
        attribution_result = self.attribution.validate(impl)
        mastery_result = self.mastery.validate(impl)
        composition_result = self.composition.validate(impl)

        # Overall validity: all axioms must pass
        is_valid = all(
            r.passed
            for r in [agency_result, attribution_result, mastery_result, composition_result]
        )

        # Quality: minimum of all axiom scores
        overall_quality = min(
            agency_result.quality_score,
            attribution_result.quality_score,
            mastery_result.quality_score,
            composition_result.quality_score,
        )

        return ValidationResult(
            agency=agency_result,
            attribution=attribution_result,
            mastery=mastery_result,
            composition=composition_result,
            overall_quality=overall_quality,
            is_valid=is_valid,
        )

    def get_axiom(
        self, axiom_id: str
    ) -> AgencyAxiom | AttributionAxiom | MasteryAxiom | CompositionAxiom | None:
        """Get an axiom by its ID (A1, A2, A3, A4)."""
        axiom_map: dict[str, AgencyAxiom | AttributionAxiom | MasteryAxiom | CompositionAxiom] = {
            "A1": self.agency,
            "A2": self.attribution,
            "A3": self.mastery,
            "A4": self.composition,
        }
        return axiom_map.get(axiom_id.upper())

    def list_axioms(self) -> list[dict[str, Any]]:
        """List all axioms as dictionaries."""
        return [
            self.agency.to_dict(),
            self.attribution.to_dict(),
            self.mastery.to_dict(),
            self.composition.to_dict(),
        ]

    def to_dict(self) -> dict[str, Any]:
        """Convert kernel to dictionary for JSON serialization."""
        return {
            "axioms": self.list_axioms(),
            "total_galois_loss": sum(a["galois_loss"] for a in self.list_axioms()),
        }

    def to_text(self) -> str:
        """Convert kernel to human-readable text."""
        lines = [
            "=== GAME KERNEL ===",
            "The Four Axioms of Game Experience Quality",
            "",
            self.agency.to_text(),
            "",
            self.attribution.to_text(),
            "",
            self.mastery.to_text(),
            "",
            self.composition.to_text(),
            "",
            f"Total Galois Loss: {sum(a['galois_loss'] for a in self.list_axioms()):.2f}",
            "===================",
        ]
        return "\n".join(lines)


# =============================================================================
# Factory Function
# =============================================================================


def create_kernel() -> GameKernel:
    """
    Create a GameKernel instance with the four axioms.

    Returns:
        A configured GameKernel
    """
    return GameKernel()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "AxiomSeverity",
    # Types
    "AxiomViolation",
    "AxiomResult",
    "ValidationResult",
    "GameImplementation",
    # Axioms
    "AgencyAxiom",
    "AttributionAxiom",
    "MasteryAxiom",
    "CompositionAxiom",
    # Kernel
    "GameKernel",
    "create_kernel",
]
