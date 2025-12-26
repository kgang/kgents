"""
Wasm Survivors: Witnessed Run Lab Service.

This module implements the run witnessing workflow for the Wasm Survivors pilot,
validating the Galois Loss theory: "The run is the proof. The build is the claim."

AGENTESE Paths:
- witness.run_lab.manifest     - Run lab status overview
- witness.run_lab.mark         - Mark a build shift
- witness.run_lab.ghost        - Record a ghost alternative
- witness.run_lab.trail        - Get current run trail
- witness.run_lab.crystallize  - Create run crystal

Laws Implemented:
- L1 Run Coherence: Every major build shift must be marked and justified
- L2 Build Drift: Galois loss exceeds threshold -> surface the drift
- L3 Ghost Commitment: Unchosen upgrades recorded as ghost alternatives
- L4 Risk Transparency: High-risk choices marked BEFORE effects resolve
- L5 Proof Compression: Run crystal reduces trace while preserving causal rationale

Philosophy:
    "The run IS the proof. The build IS the claim. The ghost IS the road not taken."
    "Failure is the clearest signal. Chaos is structure when witnessed."

See: pilots/wasm-survivors-witnessed-run-lab/PROTO_SPEC.md
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal
from uuid import uuid4

if TYPE_CHECKING:
    pass

logger = logging.getLogger("kgents.witness.run_lab")


# =============================================================================
# Constants (from PROTO_SPEC)
# =============================================================================

# L2: Drift threshold - surface when exceeded
DRIFT_THRESHOLD = 0.3

# L4: High-risk threshold - requires pre-marking
HIGH_RISK_THRESHOLD = 0.7

# L5: Minimum marks for crystallization
MIN_MARKS_FOR_CRYSTAL = 3

# Anti-Success: Maximum witness latency (0ms target)
MAX_WITNESS_LATENCY_MS = 5


# =============================================================================
# Build State (Domain Model)
# =============================================================================


class RiskLevel(str, Enum):
    """Risk level indicator for build state."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Tempo(str, Enum):
    """Decision-making pace indicator."""
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"


@dataclass
class BuildState:
    """
    Current build state at any point during a run.

    The "claim" in Galois Loss terms - what the player has built.
    """
    upgrades: list[str] = field(default_factory=list)
    synergies: list[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    tempo: Tempo = Tempo.NORMAL
    wave: int = 0

    def to_string(self) -> str:
        """
        Convert to string representation for Galois distance computation.

        The string representation is used in:
            L(P) = d(P, C(R(P)))

        where P is this string representation.
        """
        parts = [
            f"Wave {self.wave}",
            f"Upgrades: {', '.join(self.upgrades) if self.upgrades else 'none'}",
            f"Synergies: {', '.join(self.synergies) if self.synergies else 'none'}",
            f"Risk: {self.risk_level.value}",
            f"Tempo: {self.tempo.value}",
        ]
        return " | ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "upgrades": self.upgrades,
            "synergies": self.synergies,
            "risk_level": self.risk_level.value,
            "tempo": self.tempo.value,
            "wave": self.wave,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BuildState:
        """Create from dictionary."""
        return cls(
            upgrades=data.get("upgrades", []),
            synergies=data.get("synergies", []),
            risk_level=RiskLevel(data.get("risk_level", "medium")),
            tempo=Tempo(data.get("tempo", "normal")),
            wave=data.get("wave", 0),
        )


# =============================================================================
# Shift Types
# =============================================================================


class ShiftType(str, Enum):
    """Type of build shift that occurred."""
    UPGRADE_TAKEN = "upgrade_taken"      # L1: Player took an upgrade
    UPGRADE_SKIPPED = "upgrade_skipped"  # L3: Player skipped (creates ghost)
    BUILD_PIVOT = "build_pivot"          # L1: Major direction change
    RISK_TAKEN = "risk_taken"            # L4: High-risk choice made
    SYNERGY_FORMED = "synergy_formed"    # Passive: Synergy emerged
    SYNERGY_BROKEN = "synergy_broken"    # Passive: Synergy lost


# =============================================================================
# RunMark (L1: Run Coherence Law)
# =============================================================================


@dataclass
class RunMark:
    """
    A mark capturing a build shift during a run.

    L1: "A run is valid only if every major build shift is marked and justified."
    """
    mark_id: str = field(default_factory=lambda: f"rm-{uuid4().hex[:12]}")
    run_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    # Build transition
    build_before: BuildState = field(default_factory=BuildState)
    build_after: BuildState = field(default_factory=BuildState)

    # Shift metadata
    shift_type: ShiftType = ShiftType.UPGRADE_TAKEN
    justification: str | None = None
    marked_before_resolution: bool = False  # L4 compliance

    # Galois coherence (L2)
    galois_loss: float = 0.0
    is_drift: bool = False
    evidence_tier: str = "empirical"

    def __post_init__(self) -> None:
        """Validate and compute derived fields."""
        # L2: Drift detection
        self.is_drift = self.galois_loss > DRIFT_THRESHOLD

        # Classify evidence tier based on loss
        if self.galois_loss < 0.1:
            self.evidence_tier = "categorical"
        elif self.galois_loss < 0.3:
            self.evidence_tier = "empirical"
        elif self.galois_loss < 0.6:
            self.evidence_tier = "aesthetic"
        else:
            self.evidence_tier = "somatic"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "mark_id": self.mark_id,
            "run_id": self.run_id,
            "timestamp": self.timestamp.isoformat(),
            "build_before": self.build_before.to_dict(),
            "build_after": self.build_after.to_dict(),
            "shift_type": self.shift_type.value,
            "justification": self.justification,
            "marked_before_resolution": self.marked_before_resolution,
            "galois_loss": self.galois_loss,
            "is_drift": self.is_drift,
            "evidence_tier": self.evidence_tier,
        }


# =============================================================================
# GhostAlternative (L3: Ghost Commitment Law)
# =============================================================================


@dataclass
class GhostAlternative:
    """
    An unchosen path recorded as a ghost.

    L3: "Unchosen upgrades are recorded as ghost alternatives."
    QA-4: "Ghost layer should feel like alternate timeline, not error log."
    """
    ghost_id: str = field(default_factory=lambda: f"ghost-{uuid4().hex[:12]}")
    run_id: str = ""
    decision_point_id: str = ""  # Links to RunMark
    timestamp: datetime = field(default_factory=datetime.now)

    # What was not taken
    unchosen_upgrade: str = ""
    unchosen_synergies: list[str] = field(default_factory=list)

    # Counterfactual (descriptive, not judgmental per QA-2)
    hypothetical_impact: Literal["beneficial", "neutral", "harmful", "unknown"] = "unknown"
    reasoning: str | None = None

    # Visual prominence
    salience: int = 1  # 1-3, higher = more prominent

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "ghost_id": self.ghost_id,
            "run_id": self.run_id,
            "decision_point_id": self.decision_point_id,
            "timestamp": self.timestamp.isoformat(),
            "unchosen_upgrade": self.unchosen_upgrade,
            "unchosen_synergies": self.unchosen_synergies,
            "hypothetical_impact": self.hypothetical_impact,
            "reasoning": self.reasoning,
            "salience": self.salience,
        }


# =============================================================================
# RunCrystal (L5: Proof Compression Law)
# =============================================================================


@dataclass
class RunCrystal:
    """
    Compressed proof of a complete run.

    L5: "A run crystal must reduce trace length while preserving causal rationale."
    QA-3: "Failure runs must produce CLEARER crystals than success runs."
    """
    crystal_id: str = field(default_factory=lambda: f"rc-{uuid4().hex[:12]}")
    run_id: str = ""

    # Temporal bounds
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: datetime = field(default_factory=datetime.now)

    # Outcome (descriptive, not judgmental)
    outcome: Literal["victory", "defeat", "abandoned"] = "defeat"
    waves_survived: int = 0

    # Build identity claim (the proof)
    build_claim: str = ""

    # Causal summary
    key_pivots: list[RunMark] = field(default_factory=list)
    ghost_count: int = 0

    # Coherence metrics
    average_galois_loss: float = 0.0
    total_drift_events: int = 0

    # Style descriptors (QA-2: descriptive, not punitive)
    style_descriptors: list[str] = field(default_factory=list)

    # Compression metadata (Amendment G)
    source_mark_count: int = 0
    compression_ratio: float = 1.0
    compression_disclosure: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "crystal_id": self.crystal_id,
            "run_id": self.run_id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat(),
            "outcome": self.outcome,
            "waves_survived": self.waves_survived,
            "build_claim": self.build_claim,
            "key_pivots": [p.to_dict() for p in self.key_pivots],
            "ghost_count": self.ghost_count,
            "average_galois_loss": self.average_galois_loss,
            "total_drift_events": self.total_drift_events,
            "style_descriptors": self.style_descriptors,
            "source_mark_count": self.source_mark_count,
            "compression_ratio": self.compression_ratio,
            "compression_disclosure": self.compression_disclosure,
        }


# =============================================================================
# ValueCompass (Style Mirror)
# =============================================================================


@dataclass
class ValueCompass:
    """
    Value compass showing playstyle constitution.

    QA-2: "Players should feel their style is SEEN, not judged."
    """
    run_id: str = ""

    # Style dimensions (all in [0, 1])
    aggression: float = 0.5
    risk_tolerance: float = 0.5
    synergy_focus: float = 0.5
    adaptability: float = 0.5
    tempo_stability: float = 0.5

    # Dominant style
    dominant_style: str = "balanced"

    # Style coherence (Galois coherence of style)
    style_coherence: float = 0.8

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "run_id": self.run_id,
            "aggression": self.aggression,
            "risk_tolerance": self.risk_tolerance,
            "synergy_focus": self.synergy_focus,
            "adaptability": self.adaptability,
            "tempo_stability": self.tempo_stability,
            "dominant_style": self.dominant_style,
            "style_coherence": self.style_coherence,
        }


# =============================================================================
# WARMTH-Calibrated Responses
# =============================================================================


WARMTH_PROMPTS = {
    "mark_captured": "Witnessed.",
    "drift_detected": "I noticed a shift in your approach.",
    "ghost_recorded": "That path remains open, unwalked.",
    "crystal_created": "The run crystallized into this claim.",
    "risk_marked": "Courage noted. Let's see how it plays out.",
    "style_observed": "Your style is emerging.",
    "failure_crystal": "Defeat teaches more than victory. Here's what I saw.",
    "no_marks": "A quiet run. Sometimes silence is signal.",
}


def warmth_response_for_mark(mark: RunMark) -> str:
    """Generate a WARMTH-calibrated response for a mark."""
    if mark.shift_type == ShiftType.RISK_TAKEN and mark.marked_before_resolution:
        return WARMTH_PROMPTS["risk_marked"]
    elif mark.is_drift:
        return WARMTH_PROMPTS["drift_detected"]
    else:
        return WARMTH_PROMPTS["mark_captured"]


def warmth_response_for_crystal(crystal: RunCrystal) -> str:
    """Generate a WARMTH-calibrated response for a crystal."""
    if crystal.outcome == "defeat":
        return WARMTH_PROMPTS["failure_crystal"]
    else:
        return WARMTH_PROMPTS["crystal_created"]


# =============================================================================
# Galois Loss Integration
# =============================================================================


class GaloisLossComputer:
    """
    Compute Galois loss for build transitions.

    L(P) = d(P, C(R(P)))

    Where:
    - P = build state (string representation)
    - R = restructure (semantic parsing)
    - C = reconstitute (regeneration)
    - d = semantic distance
    """

    def __init__(self) -> None:
        """Initialize with fallback distance metric."""
        self._use_fallback = True
        try:
            from services.zero_seed.galois.distance import CanonicalSemanticDistance
            self._distance_metric = CanonicalSemanticDistance()
            self._use_fallback = False
        except ImportError:
            pass

    def compute_transition_loss(
        self,
        before: BuildState,
        after: BuildState,
    ) -> float:
        """
        Compute Galois loss for a build transition.

        This measures how much semantic information is preserved
        when the build shifts from one state to another.
        """
        before_str = before.to_string()
        after_str = after.to_string()

        if self._use_fallback:
            return self._fallback_distance(before_str, after_str)

        try:
            return self._distance_metric.distance(before_str, after_str)
        except Exception:
            return self._fallback_distance(before_str, after_str)

    def _fallback_distance(self, text_a: str, text_b: str) -> float:
        """Simple fallback based on token overlap."""
        tokens_a = set(text_a.lower().split())
        tokens_b = set(text_b.lower().split())

        if not tokens_a or not tokens_b:
            return 1.0 if text_a != text_b else 0.0

        intersection = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)

        jaccard_sim = intersection / union if union > 0 else 0.0
        return 1.0 - jaccard_sim


# =============================================================================
# Run Lab Service
# =============================================================================


class RunLab:
    """
    The main Run Lab service.

    This is the primary entry point for the wasm-survivors witnessed run lab pilot.
    It combines mark capture, ghost recording, and crystallization into a cohesive,
    low-latency witnessing experience.

    Anti-Success: The witness layer must add ZERO perceptible latency.
    """

    def __init__(self) -> None:
        """Initialize the run lab."""
        self._galois = GaloisLossComputer()

        # In-memory storage for current run (would be persisted in production)
        self._current_run_id: str | None = None
        self._marks: list[RunMark] = []
        self._ghosts: list[GhostAlternative] = []
        self._current_build: BuildState = BuildState()
        self._run_started_at: datetime | None = None

    def start_run(self) -> str:
        """Start a new run."""
        self._current_run_id = f"run-{uuid4().hex[:12]}"
        self._marks = []
        self._ghosts = []
        self._current_build = BuildState()
        self._run_started_at = datetime.now()

        logger.info(f"Started run: {self._current_run_id}")
        return self._current_run_id

    def mark_shift(
        self,
        new_build: BuildState,
        shift_type: ShiftType,
        justification: str | None = None,
        marked_before_resolution: bool = False,
    ) -> tuple[RunMark, str, float]:
        """
        Mark a build shift (L1 compliance).

        Returns:
            Tuple of (mark, warmth_response, latency_ms)

        Anti-Success: Must return in < 5ms.
        """
        start_time = time.perf_counter()

        if not self._current_run_id:
            self._current_run_id = self.start_run()

        # Compute Galois loss
        galois_loss = self._galois.compute_transition_loss(
            self._current_build,
            new_build,
        )

        # Create mark
        mark = RunMark(
            run_id=self._current_run_id,
            build_before=self._current_build,
            build_after=new_build,
            shift_type=shift_type,
            justification=justification,
            marked_before_resolution=marked_before_resolution,
            galois_loss=galois_loss,
        )

        # Store
        self._marks.append(mark)
        self._current_build = new_build

        # Generate warmth response
        warmth = warmth_response_for_mark(mark)

        # Log drift if detected (L2)
        if mark.is_drift:
            logger.info(f"Drift detected in run {self._current_run_id}: loss={galois_loss:.3f}")

        latency_ms = (time.perf_counter() - start_time) * 1000

        return mark, warmth, latency_ms

    def record_ghost(
        self,
        decision_point_id: str,
        unchosen_upgrade: str,
        unchosen_synergies: list[str] | None = None,
        reasoning: str | None = None,
    ) -> tuple[GhostAlternative, str, float]:
        """
        Record a ghost alternative (L3 compliance).

        Returns:
            Tuple of (ghost, warmth_response, latency_ms)
        """
        start_time = time.perf_counter()

        if not self._current_run_id:
            self._current_run_id = self.start_run()

        ghost = GhostAlternative(
            run_id=self._current_run_id,
            decision_point_id=decision_point_id,
            unchosen_upgrade=unchosen_upgrade,
            unchosen_synergies=unchosen_synergies or [],
            reasoning=reasoning,
        )

        self._ghosts.append(ghost)

        warmth = WARMTH_PROMPTS["ghost_recorded"]
        latency_ms = (time.perf_counter() - start_time) * 1000

        return ghost, warmth, latency_ms

    def get_trail(self) -> dict[str, Any]:
        """Get the current run trail."""
        return {
            "run_id": self._current_run_id or "",
            "marks": [m.to_dict() for m in self._marks],
            "ghosts": [g.to_dict() for g in self._ghosts],
            "current_build": self._current_build.to_dict(),
            "elapsed_time_ms": (
                (datetime.now() - self._run_started_at).total_seconds() * 1000
                if self._run_started_at
                else 0
            ),
        }

    def crystallize(
        self,
        outcome: Literal["victory", "defeat", "abandoned"],
        waves_survived: int,
    ) -> tuple[RunCrystal, ValueCompass, str]:
        """
        Create a run crystal (L5 compliance).

        QA-3: Failure runs must produce CLEARER crystals.
        """
        if len(self._marks) < MIN_MARKS_FOR_CRYSTAL:
            logger.warning(f"Not enough marks to crystallize ({len(self._marks)} < {MIN_MARKS_FOR_CRYSTAL})")

        # Select key pivots (most significant marks)
        key_pivots = self._select_key_pivots(self._marks)

        # Compute average Galois loss
        if self._marks:
            avg_loss = sum(m.galois_loss for m in self._marks) / len(self._marks)
        else:
            avg_loss = 0.0

        # Count drift events
        drift_count = sum(1 for m in self._marks if m.is_drift)

        # Generate build claim
        build_claim = self._generate_build_claim(key_pivots, outcome)

        # Compute style descriptors
        style_descriptors = self._compute_style_descriptors()

        # Generate compression disclosure (Amendment G)
        dropped_count = len(self._marks) - len(key_pivots)
        disclosure = self._generate_compression_disclosure(dropped_count, len(self._marks))

        # Create crystal
        crystal = RunCrystal(
            run_id=self._current_run_id or "",
            started_at=self._run_started_at or datetime.now(),
            ended_at=datetime.now(),
            outcome=outcome,
            waves_survived=waves_survived,
            build_claim=build_claim,
            key_pivots=key_pivots,
            ghost_count=len(self._ghosts),
            average_galois_loss=avg_loss,
            total_drift_events=drift_count,
            style_descriptors=style_descriptors,
            source_mark_count=len(self._marks),
            compression_ratio=len(self._marks) if len(self._marks) > 0 else 1.0,
            compression_disclosure=disclosure,
        )

        # Compute value compass
        compass = self._compute_value_compass()

        # Generate warmth response
        warmth = warmth_response_for_crystal(crystal)

        logger.info(
            f"Crystallized run {self._current_run_id}: "
            f"outcome={outcome}, waves={waves_survived}, "
            f"avg_loss={avg_loss:.3f}, drifts={drift_count}"
        )

        return crystal, compass, warmth

    def _select_key_pivots(self, marks: list[RunMark], max_pivots: int = 5) -> list[RunMark]:
        """
        Select the most significant marks as key pivots.

        Priority:
        1. High Galois loss (drift events)
        2. Risk-taken marks
        3. Build pivots
        4. Synergy formations
        """
        # Sort by significance
        def significance(m: RunMark) -> float:
            score = m.galois_loss
            if m.shift_type == ShiftType.RISK_TAKEN:
                score += 0.3
            if m.shift_type == ShiftType.BUILD_PIVOT:
                score += 0.2
            if m.shift_type == ShiftType.SYNERGY_FORMED:
                score += 0.1
            if m.is_drift:
                score += 0.4
            return score

        sorted_marks = sorted(marks, key=significance, reverse=True)
        return sorted_marks[:max_pivots]

    def _generate_build_claim(
        self,
        key_pivots: list[RunMark],
        outcome: str,
    ) -> str:
        """
        Generate the one-sentence build identity claim.

        This is the proof that the crystal justifies.
        """
        if not key_pivots:
            return f"A quiet run ending in {outcome}."

        # Analyze the pivots
        risk_count = sum(1 for p in key_pivots if p.shift_type == ShiftType.RISK_TAKEN)
        pivot_count = sum(1 for p in key_pivots if p.shift_type == ShiftType.BUILD_PIVOT)
        synergy_count = sum(1 for p in key_pivots if p.shift_type == ShiftType.SYNERGY_FORMED)

        # Build claim based on patterns
        style_parts = []

        if risk_count >= 2:
            style_parts.append("aggressive risk-taker")
        elif risk_count == 1:
            style_parts.append("calculated risk-taker")
        else:
            style_parts.append("steady builder")

        if pivot_count >= 2:
            style_parts.append("with adaptive pivots")

        if synergy_count >= 2:
            style_parts.append("focused on synergies")

        style_desc = " ".join(style_parts)

        # QA-3: Failure runs get clearer claims
        if outcome == "defeat":
            return f"A {style_desc} who pushed too far. The run reveals the limit."
        elif outcome == "victory":
            return f"A {style_desc} whose approach found coherence."
        else:
            return f"A {style_desc} who chose to step away."

    def _compute_style_descriptors(self) -> list[str]:
        """Compute descriptive (not judgmental) style descriptors."""
        descriptors = []

        if not self._marks:
            return ["quiet"]

        # Aggression based on risk marks
        risk_ratio = sum(1 for m in self._marks if m.shift_type == ShiftType.RISK_TAKEN) / len(self._marks)
        if risk_ratio > 0.3:
            descriptors.append("aggressive")
        elif risk_ratio > 0.1:
            descriptors.append("opportunistic")
        else:
            descriptors.append("cautious")

        # Adaptability based on pivots
        pivot_ratio = sum(1 for m in self._marks if m.shift_type == ShiftType.BUILD_PIVOT) / len(self._marks)
        if pivot_ratio > 0.2:
            descriptors.append("adaptive")
        else:
            descriptors.append("focused")

        # Synergy focus
        synergy_ratio = sum(1 for m in self._marks if m.shift_type == ShiftType.SYNERGY_FORMED) / len(self._marks)
        if synergy_ratio > 0.2:
            descriptors.append("synergy-builder")

        return descriptors

    def _compute_value_compass(self) -> ValueCompass:
        """Compute the value compass (style mirror)."""
        if not self._marks:
            return ValueCompass(run_id=self._current_run_id or "")

        total = len(self._marks)

        # Compute style dimensions
        risk_marks = sum(1 for m in self._marks if m.shift_type == ShiftType.RISK_TAKEN)
        pivot_marks = sum(1 for m in self._marks if m.shift_type == ShiftType.BUILD_PIVOT)
        synergy_marks = sum(1 for m in self._marks if m.shift_type == ShiftType.SYNERGY_FORMED)

        aggression = min(1.0, risk_marks / (total * 0.3)) if total > 0 else 0.5
        risk_tolerance = min(1.0, sum(1 for m in self._marks if m.galois_loss > 0.5) / (total * 0.3)) if total > 0 else 0.5
        synergy_focus = min(1.0, synergy_marks / (total * 0.3)) if total > 0 else 0.5
        adaptability = min(1.0, pivot_marks / (total * 0.2)) if total > 0 else 0.5

        # Tempo stability based on tempo changes
        tempo_changes = 0
        for i in range(1, len(self._marks)):
            if self._marks[i].build_after.tempo != self._marks[i-1].build_after.tempo:
                tempo_changes += 1
        tempo_stability = 1.0 - (tempo_changes / total) if total > 0 else 0.5

        # Determine dominant style
        dimensions = [
            ("aggressive", aggression),
            ("risk-seeking", risk_tolerance),
            ("synergy-focused", synergy_focus),
            ("adaptive", adaptability),
            ("consistent", tempo_stability),
        ]
        dominant = max(dimensions, key=lambda x: x[1])[0]

        # Style coherence based on average Galois loss
        avg_loss = sum(m.galois_loss for m in self._marks) / total if total > 0 else 0.5
        style_coherence = 1.0 - avg_loss

        return ValueCompass(
            run_id=self._current_run_id or "",
            aggression=aggression,
            risk_tolerance=risk_tolerance,
            synergy_focus=synergy_focus,
            adaptability=adaptability,
            tempo_stability=tempo_stability,
            dominant_style=dominant,
            style_coherence=style_coherence,
        )

    def _generate_compression_disclosure(
        self,
        dropped_count: int,
        total_count: int,
    ) -> str:
        """Generate Amendment G-compliant compression disclosure."""
        if dropped_count == 0:
            return "All moments were preserved in this crystal."

        if dropped_count == 1:
            return "1 moment was composted to nourish this crystal."

        ratio = dropped_count / total_count if total_count > 0 else 0

        if ratio < 0.3:
            return f"{dropped_count} routine moments were set aside. The pivotal ones remain."
        elif ratio < 0.6:
            return f"{dropped_count} moments found their way into the soil. The crystal holds what grew."
        else:
            return f"A dense run compressed from {total_count} moments. The essence is here."


# =============================================================================
# Module-level singleton
# =============================================================================


_run_lab: RunLab | None = None


def get_run_lab() -> RunLab:
    """Get the singleton RunLab instance."""
    global _run_lab
    if _run_lab is None:
        _run_lab = RunLab()
    return _run_lab


# =============================================================================
# Module Exports
# =============================================================================


__all__ = [
    # Constants
    "DRIFT_THRESHOLD",
    "HIGH_RISK_THRESHOLD",
    "MIN_MARKS_FOR_CRYSTAL",
    "MAX_WITNESS_LATENCY_MS",
    # Domain models
    "BuildState",
    "RiskLevel",
    "Tempo",
    "ShiftType",
    "RunMark",
    "GhostAlternative",
    "RunCrystal",
    "ValueCompass",
    # Services
    "GaloisLossComputer",
    "RunLab",
    "get_run_lab",
    # Warmth
    "WARMTH_PROMPTS",
    "warmth_response_for_mark",
    "warmth_response_for_crystal",
]
