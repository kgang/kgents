"""
Witness Accumulator: Every decision leaves a trace.

Categorical Structure:
    Witness : Decision × Percept → WitnessMark
    Accumulate : list[WitnessMark] → PlaythroughEvidence

The witness accumulator implements the kgents principle:
    "The proof IS the decision. The mark IS the witness."
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import AgentPersona, DecisionResult
    from .perception import UnifiedPercept


@dataclass
class DecisionTrace:
    """A witness mark for a single decision."""

    timestamp_ms: float
    mode: str
    percept_hash: str
    reasoning: str
    action_chosen: str
    alternatives_considered: list[str]
    confidence: float
    reaction_time_ms: float
    human_likeness_score: float

    # Context at decision time
    player_health: float = 100.0
    wave_number: int = 1
    enemy_count: int = 0
    threat_level: float = 0.0


@dataclass
class FlowSample:
    """A sample of flow state at a point in time."""

    timestamp_ms: float
    engagement: float  # 0-1: how engaged is the player?
    challenge: float  # 0-1: how challenging is the situation?
    frustration: float  # 0-1: how frustrated is the player?

    @property
    def flow_state(self) -> str:
        """Determine flow state from metrics."""
        if self.engagement > 0.7 and 0.3 < self.challenge < 0.7:
            return "FLOW"
        if self.challenge > 0.8:
            return "ANXIETY"
        if self.challenge < 0.2:
            return "BOREDOM"
        if self.frustration > 0.7:
            return "FRUSTRATION"
        return "NEUTRAL"


@dataclass
class EmergenceEvent:
    """An emergent gameplay event."""

    timestamp_ms: float
    type: str  # "synergy", "strategy", "exploit", "unexpected"
    description: str
    components: list[str]
    strength: float  # 0-1: how significant?
    evidence: str


@dataclass
class BalanceObservation:
    """An observation about game balance."""

    timestamp_ms: float
    type: str  # "overpowered", "underpowered", "well_balanced"
    subject: str  # What is being observed (upgrade, enemy, etc.)
    evidence: str
    severity: float  # 0-1: how severe is the imbalance?


@dataclass
class FunFloorViolation:
    """A violation of the fun floor (minimum engagement)."""

    timestamp_ms: float
    duration_ms: float
    type: str  # "boring", "frustrating", "confusing"
    evidence: str
    severity: float


@dataclass
class PlaythroughEvidence:
    """
    Complete evidence from a playthrough.

    This is the output of the WitnessAccumulator, ready for
    integration with ASHC.
    """

    # Identity
    playthrough_id: str
    persona: str
    started_at: float
    duration_ms: float

    # Outcome
    waves_survived: int
    final_health: float
    upgrades_collected: list[str]
    enemies_killed: int

    # Decision traces
    traces: list[DecisionTrace]
    total_decisions: int

    # Quality metrics
    flow_timeline: list[FlowSample]
    emergence_events: list[EmergenceEvent]
    balance_observations: list[BalanceObservation]
    fun_floor_violations: list[FunFloorViolation]

    # Galois metrics
    galois_loss: float  # Human-likeness loss
    humanness_score: float  # Average humanness across decisions

    @property
    def is_valid_evidence(self) -> bool:
        """Check if playthrough provides valid evidence."""
        return (
            self.duration_ms > 10_000  # At least 10 seconds
            and self.total_decisions > 10  # At least 10 decisions
            and self.waves_survived >= 1  # Survived at least one wave
        )

    @property
    def fun_floor_passed(self) -> bool:
        """Check if fun floor was maintained."""
        if not self.fun_floor_violations:
            return True
        # Allow some minor violations
        total_violation_time = sum(v.duration_ms for v in self.fun_floor_violations)
        return total_violation_time < self.duration_ms * 0.1  # Less than 10% violation

    @property
    def evidence_tier(self) -> str:
        """Determine evidence tier based on Galois loss."""
        if self.galois_loss < 0.10:
            return "CATEGORICAL"
        if self.galois_loss < 0.38:
            return "EMPIRICAL"
        if self.galois_loss < 0.45:
            return "AESTHETIC"
        if self.galois_loss < 0.65:
            return "SOMATIC"
        return "CHAOTIC"


class WitnessAccumulator:
    """
    Accumulates witness marks during a playthrough.

    Implements: Witness : Decision × Percept → WitnessMark
    """

    def __init__(self) -> None:
        self.traces: list[DecisionTrace] = []
        self.flow_samples: list[FlowSample] = []
        self.emergence_events: list[EmergenceEvent] = []
        self.balance_observations: list[BalanceObservation] = []
        self.fun_floor_violations: list[FunFloorViolation] = []

        self._last_flow_sample_time: float = 0
        self._engagement_window: list[float] = []
        self._frustration_window: list[float] = []

    def mark_decision(self, result: DecisionResult, percept: UnifiedPercept) -> None:
        """
        Record a witness mark for a decision.

        Every decision leaves a trace that can be analyzed later.
        """
        trace = DecisionTrace(
            timestamp_ms=time.time() * 1000,
            mode=result.mode.value,
            percept_hash=str(hash(str(percept))),
            reasoning=result.reasoning,
            action_chosen=str(result.action),
            alternatives_considered=result.alternatives,
            confidence=result.confidence,
            reaction_time_ms=result.reaction_time_ms,
            human_likeness_score=self._compute_humanness(result),
            player_health=percept.player.get("health", 100),
            wave_number=percept.wave.get("number", 1),
            enemy_count=len(percept.enemies),
            threat_level=percept.threat_level,
        )
        self.traces.append(trace)

        # Update flow state periodically
        self._maybe_sample_flow(percept, result)

        # Check for emergence
        self._check_emergence(percept, result)

        # Check for fun floor violations
        self._check_fun_floor(percept, result)

    def _compute_humanness(self, result: DecisionResult) -> float:
        """Compute humanness score for a decision."""
        # Reaction time component
        rt = result.reaction_time_ms
        if rt < 100:
            rt_score = 0.3
        elif rt > 1000:
            rt_score = 0.5
        elif 150 <= rt <= 400:
            rt_score = 1.0
        else:
            rt_score = 0.8

        # Confidence component (humans often uncertain)
        conf = result.confidence
        if 0.3 <= conf <= 0.8:
            conf_score = 1.0  # Healthy uncertainty
        else:
            conf_score = 0.7  # Too confident or too uncertain

        return rt_score * 0.7 + conf_score * 0.3

    def _maybe_sample_flow(self, percept: UnifiedPercept, result: DecisionResult) -> None:
        """Sample flow state every few seconds."""
        now = time.time() * 1000

        if now - self._last_flow_sample_time < 5000:  # Every 5 seconds
            return

        self._last_flow_sample_time = now

        # Compute engagement (based on action frequency and variety)
        recent_traces = self.traces[-30:] if len(self.traces) >= 30 else self.traces
        if recent_traces:
            action_variety = len(set(t.action_chosen for t in recent_traces)) / len(recent_traces)
            confidence_avg = sum(t.confidence for t in recent_traces) / len(recent_traces)
            engagement = (action_variety + confidence_avg) / 2
        else:
            engagement = 0.5

        # Compute challenge (based on threat level and deaths/damage)
        challenge = percept.threat_level

        # Compute frustration (based on repeated failures or lack of progress)
        recent_health = [t.player_health for t in recent_traces[-10:]] if recent_traces else [100]
        health_trend = recent_health[-1] - recent_health[0] if len(recent_health) > 1 else 0
        frustration = max(0, -health_trend / 100)  # Losing health = frustration

        self.flow_samples.append(
            FlowSample(
                timestamp_ms=now,
                engagement=engagement,
                challenge=challenge,
                frustration=frustration,
            )
        )

    def _check_emergence(self, percept: UnifiedPercept, result: DecisionResult) -> None:
        """Check for emergent gameplay patterns."""
        # Check for upgrade synergies
        upgrades = percept.player.get("upgrades", [])
        if len(upgrades) >= 2:
            # Simple synergy detection based on upgrade combinations
            synergy_combos = [
                (["pierce", "multishot"], "Shotgun Drill"),
                (["orbit", "damage"], "Orbital Strike"),
                (["speed", "rapid"], "Gun Kata"),
                (["health", "regen"], "Immortal"),
            ]

            for combo, name in synergy_combos:
                if all(c in str(upgrades).lower() for c in combo):
                    # Check if we already recorded this synergy
                    if not any(e.description == name for e in self.emergence_events):
                        self.emergence_events.append(
                            EmergenceEvent(
                                timestamp_ms=time.time() * 1000,
                                type="synergy",
                                description=name,
                                components=combo,
                                strength=0.8,
                                evidence=f"Achieved {name} synergy with {upgrades}",
                            )
                        )

    def _check_fun_floor(self, percept: UnifiedPercept, result: DecisionResult) -> None:
        """Check for fun floor violations."""
        # Boredom: Low threat, low engagement for extended period
        if len(self.flow_samples) >= 3:
            recent = self.flow_samples[-3:]
            avg_engagement = sum(s.engagement for s in recent) / 3
            avg_challenge = sum(s.challenge for s in recent) / 3

            if avg_engagement < 0.3 and avg_challenge < 0.2:
                self.fun_floor_violations.append(
                    FunFloorViolation(
                        timestamp_ms=time.time() * 1000,
                        duration_ms=15000,  # Assumes 3 samples * 5 seconds
                        type="boring",
                        evidence=f"Low engagement ({avg_engagement:.2f}) and challenge ({avg_challenge:.2f})",
                        severity=0.5,
                    )
                )

            # Frustration: High challenge, low confidence, health dropping
            if avg_challenge > 0.8 and result.confidence < 0.3:
                self.fun_floor_violations.append(
                    FunFloorViolation(
                        timestamp_ms=time.time() * 1000,
                        duration_ms=15000,
                        type="frustrating",
                        evidence=f"High challenge ({avg_challenge:.2f}) with low confidence ({result.confidence:.2f})",
                        severity=0.6,
                    )
                )

    def generate_evidence(
        self,
        persona: AgentPersona,
        decisions: list[DecisionResult],
        duration_ms: float,
    ) -> PlaythroughEvidence:
        """
        Generate final evidence from accumulated data.

        This is called at the end of a playthrough to produce
        ASHC-compatible evidence.
        """
        import uuid

        # Compute Galois loss (human-likeness)
        humanness_scores = [t.human_likeness_score for t in self.traces]
        avg_humanness = sum(humanness_scores) / len(humanness_scores) if humanness_scores else 0.5
        galois_loss = 1.0 - avg_humanness

        # Extract final state from last trace
        final_trace = self.traces[-1] if self.traces else None
        waves_survived = final_trace.wave_number if final_trace else 0
        final_health = final_trace.player_health if final_trace else 0

        return PlaythroughEvidence(
            playthrough_id=str(uuid.uuid4())[:8],
            persona=persona.name,
            started_at=time.time() * 1000 - duration_ms,
            duration_ms=duration_ms,
            waves_survived=waves_survived,
            final_health=final_health,
            upgrades_collected=[],  # Would extract from traces
            enemies_killed=0,  # Would extract from traces
            traces=self.traces,
            total_decisions=len(decisions),
            flow_timeline=self.flow_samples,
            emergence_events=self.emergence_events,
            balance_observations=self.balance_observations,
            fun_floor_violations=self.fun_floor_violations,
            galois_loss=galois_loss,
            humanness_score=avg_humanness,
        )

    def reset(self) -> None:
        """Reset accumulator for new playthrough."""
        self.traces.clear()
        self.flow_samples.clear()
        self.emergence_events.clear()
        self.balance_observations.clear()
        self.fun_floor_violations.clear()
        self._last_flow_sample_time = 0
        self._engagement_window.clear()
        self._frustration_window.clear()
