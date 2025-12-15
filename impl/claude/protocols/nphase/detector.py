"""
Phase Detection from LLM Output.

Detects phase transitions using:
1. Explicit signifiers (⟿/⟂/⤳) from spec/protocols/auto-inducer.md
2. Heuristic patterns (file operations, test runs, etc.)

Design Decision D2: Support both explicit signifiers and heuristic detection.
Priority: Explicit signifiers > Heuristic patterns > No signal.

Signifiers:
- ⟿[PHASE] - Continue to PHASE (advance)
- ⟂[REASON] - Halt, await human input
- ⤳[OP:args] - Elastic operation (compress, expand, etc.)

See: spec/protocols/auto-inducer.md, plans/nphase-native-integration.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from protocols.nphase.operad import NPhase


class SignalAction(Enum):
    """Type of phase signal detected."""

    CONTINUE = auto()  # ⟿[PHASE] - advance to phase
    HALT = auto()  # ⟂[REASON] - stop, await human
    ELASTIC = auto()  # ⤳[OP:args] - elastic operation
    HEURISTIC = auto()  # Detected from patterns
    NONE = auto()  # No signal detected


@dataclass
class PhaseSignal:
    """
    Signal detected from LLM output.

    Represents a potential phase transition detected either explicitly
    via signifiers or heuristically via activity patterns.

    Attributes:
        action: Type of signal detected.
        target_phase: Phase to transition to (if CONTINUE or HEURISTIC).
        reason: Reason for halt (if HALT).
        elastic_op: Operation name (if ELASTIC).
        elastic_args: Arguments for elastic op (if ELASTIC).
        confidence: 1.0 for explicit signifiers, <1.0 for heuristic.
        source_text: The text that triggered the signal.
    """

    action: SignalAction
    target_phase: NPhase | None = None
    reason: str | None = None
    elastic_op: str | None = None
    elastic_args: str | None = None
    confidence: float = 1.0  # 1.0 for explicit, <1.0 for heuristic
    source_text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        result: dict[str, Any] = {
            "action": self.action.name,
            "confidence": self.confidence,
        }

        if self.target_phase is not None:
            result["target_phase"] = self.target_phase.name
        if self.reason is not None:
            result["reason"] = self.reason
        if self.elastic_op is not None:
            result["elastic_op"] = self.elastic_op
            result["elastic_args"] = self.elastic_args
        if self.source_text is not None:
            result["source_text"] = self.source_text

        return result

    @property
    def is_transition(self) -> bool:
        """Check if this signal indicates a phase transition."""
        return self.action in (SignalAction.CONTINUE, SignalAction.HEURISTIC)

    @property
    def should_auto_advance(self) -> bool:
        """Check if auto-advance is recommended (high confidence transition)."""
        return self.is_transition and self.confidence >= 0.8


class PhaseDetector:
    """
    Detect phase transitions from LLM output.

    Uses a two-tier detection system:
    1. Explicit signifiers (highest priority, confidence=1.0)
    2. Heuristic patterns (fallback, confidence<1.0)

    Example:
        detector = PhaseDetector()
        signal = detector.detect("⟿[ACT]", NPhase.UNDERSTAND)
        if signal.action == SignalAction.CONTINUE:
            session.advance_phase(signal.target_phase)
    """

    # Signifier patterns (from spec/protocols/auto-inducer.md)
    CONTINUE_PATTERN = re.compile(r"⟿\[(\w+)\]")
    HALT_PATTERN = re.compile(r"⟂\[([^\]]+)\]")
    ELASTIC_PATTERN = re.compile(r"⤳\[(\w+):([^\]]+)\]")

    # Heuristic patterns for phase detection
    UNDERSTAND_PATTERNS = [
        re.compile(r"reading.*file", re.I),
        re.compile(r"exploring.*codebase", re.I),
        re.compile(r"searching.*for", re.I),
        re.compile(r"planning", re.I),
        re.compile(r"researching", re.I),
        re.compile(r"let me.*understand", re.I),
        re.compile(r"analyzing", re.I),
        re.compile(r"reviewing.*code", re.I),
        re.compile(r"mapping.*structure", re.I),
        re.compile(r"identifying.*patterns", re.I),
    ]

    ACT_PATTERNS = [
        re.compile(r"writing.*to.*file", re.I),
        re.compile(r"creating.*file", re.I),
        re.compile(r"editing.*file", re.I),
        re.compile(r"running.*test", re.I),
        re.compile(r"implementing", re.I),
        re.compile(r"git commit", re.I),
        re.compile(r"adding.*code", re.I),
        re.compile(r"modifying", re.I),
        re.compile(r"executing", re.I),
        re.compile(r"building", re.I),
        re.compile(r"fixing.*bug", re.I),
    ]

    REFLECT_PATTERNS = [
        re.compile(r"all.*tests.*pass", re.I),
        re.compile(r"implementation.*complete", re.I),
        re.compile(r"documenting", re.I),
        re.compile(r"writing.*epilogue", re.I),
        re.compile(r"learnings?:", re.I),
        re.compile(r"summary:", re.I),
        re.compile(r"what.*worked", re.I),
        re.compile(r"retrospective", re.I),
        re.compile(r"next.*steps", re.I),
        re.compile(r"task.*complete", re.I),
    ]

    # Phase name mapping (canonical + aliases)
    PHASE_NAMES: dict[str, NPhase] = {
        "UNDERSTAND": NPhase.UNDERSTAND,
        "SENSE": NPhase.UNDERSTAND,  # Alias for backwards compatibility
        "ACT": NPhase.ACT,
        "REFLECT": NPhase.REFLECT,
    }

    def __init__(
        self,
        heuristic_threshold: float = 0.2,
        auto_advance_threshold: float = 0.8,
    ) -> None:
        """
        Initialize detector.

        Args:
            heuristic_threshold: Minimum confidence for heuristic detection.
            auto_advance_threshold: Minimum confidence for auto-advance.
        """
        self.heuristic_threshold = heuristic_threshold
        self.auto_advance_threshold = auto_advance_threshold

    def detect(self, output: str, current_phase: NPhase) -> PhaseSignal:
        """
        Detect phase signal from LLM output.

        Priority:
        1. Explicit signifiers (highest confidence)
        2. Heuristic patterns (lower confidence)
        3. No signal

        Args:
            output: LLM output text to analyze.
            current_phase: Current session phase.

        Returns:
            PhaseSignal describing detected transition (or NONE).
        """
        # Check explicit signifiers first
        if signal := self._detect_continue(output):
            return signal
        if signal := self._detect_halt(output):
            return signal
        if signal := self._detect_elastic(output):
            return signal

        # Fall back to heuristic detection
        return self._detect_heuristic(output, current_phase)

    def detect_all(self, output: str, current_phase: NPhase) -> list[PhaseSignal]:
        """
        Detect all signals in output (useful for analysis).

        Returns:
            List of all signals found, ordered by confidence.
        """
        signals: list[PhaseSignal] = []

        # Collect all explicit signals
        for match in self.CONTINUE_PATTERN.finditer(output):
            phase_name = match.group(1).upper()
            target = self.PHASE_NAMES.get(phase_name)
            if target:
                signals.append(
                    PhaseSignal(
                        action=SignalAction.CONTINUE,
                        target_phase=target,
                        confidence=1.0,
                        source_text=match.group(0),
                    )
                )

        for match in self.HALT_PATTERN.finditer(output):
            signals.append(
                PhaseSignal(
                    action=SignalAction.HALT,
                    reason=match.group(1),
                    confidence=1.0,
                    source_text=match.group(0),
                )
            )

        for match in self.ELASTIC_PATTERN.finditer(output):
            signals.append(
                PhaseSignal(
                    action=SignalAction.ELASTIC,
                    elastic_op=match.group(1),
                    elastic_args=match.group(2),
                    confidence=1.0,
                    source_text=match.group(0),
                )
            )

        # Add heuristic signal if above threshold
        heuristic = self._detect_heuristic(output, current_phase)
        if heuristic.action != SignalAction.NONE:
            signals.append(heuristic)

        # Sort by confidence (highest first)
        signals.sort(key=lambda s: s.confidence, reverse=True)
        return signals

    def _detect_continue(self, output: str) -> PhaseSignal | None:
        """Detect ⟿[PHASE] continuation signifier."""
        match = self.CONTINUE_PATTERN.search(output)
        if match:
            phase_name = match.group(1).upper()
            target = self.PHASE_NAMES.get(phase_name)
            if target:
                return PhaseSignal(
                    action=SignalAction.CONTINUE,
                    target_phase=target,
                    confidence=1.0,
                    source_text=match.group(0),
                )
        return None

    def _detect_halt(self, output: str) -> PhaseSignal | None:
        """Detect ⟂[REASON] halt signifier."""
        match = self.HALT_PATTERN.search(output)
        if match:
            return PhaseSignal(
                action=SignalAction.HALT,
                reason=match.group(1),
                confidence=1.0,
                source_text=match.group(0),
            )
        return None

    def _detect_elastic(self, output: str) -> PhaseSignal | None:
        """Detect ⤳[OP:args] elastic signifier."""
        match = self.ELASTIC_PATTERN.search(output)
        if match:
            return PhaseSignal(
                action=SignalAction.ELASTIC,
                elastic_op=match.group(1),
                elastic_args=match.group(2),
                confidence=1.0,
                source_text=match.group(0),
            )
        return None

    def _detect_heuristic(
        self, output: str, current_phase: NPhase
    ) -> PhaseSignal:
        """
        Detect phase from activity patterns.

        Uses pattern matching to infer phase from output content.
        Only suggests transition if different from current phase.

        Args:
            output: Text to analyze.
            current_phase: Current session phase.

        Returns:
            PhaseSignal with HEURISTIC action or NONE.
        """
        # Count pattern matches for each phase
        scores: dict[NPhase, int] = {
            NPhase.UNDERSTAND: sum(
                1 for p in self.UNDERSTAND_PATTERNS if p.search(output)
            ),
            NPhase.ACT: sum(1 for p in self.ACT_PATTERNS if p.search(output)),
            NPhase.REFLECT: sum(1 for p in self.REFLECT_PATTERNS if p.search(output)),
        }

        # Find phase with highest score
        max_score = max(scores.values())

        if max_score == 0:
            return PhaseSignal(action=SignalAction.NONE)

        # Get all phases with max score (handle ties)
        suggested_phases = [p for p, s in scores.items() if s == max_score]
        suggested = suggested_phases[0]  # Take first if tied

        # Only suggest transition if different from current
        if suggested != current_phase:
            # Confidence scales with match count, capped at 0.8 for heuristics
            confidence = min(0.8, max_score * self.heuristic_threshold)
            if confidence >= self.heuristic_threshold:
                return PhaseSignal(
                    action=SignalAction.HEURISTIC,
                    target_phase=suggested,
                    confidence=confidence,
                    source_text=f"Matched {max_score} {suggested.name} patterns",
                )

        return PhaseSignal(action=SignalAction.NONE)

    def should_auto_advance(self, signal: PhaseSignal) -> bool:
        """Check if signal confidence warrants auto-advance."""
        return signal.is_transition and signal.confidence >= self.auto_advance_threshold


# Singleton instance with default configuration
detector = PhaseDetector()


def detect_phase(output: str, current_phase: NPhase) -> PhaseSignal:
    """
    Detect phase signal from output (convenience function).

    Uses the global detector instance.
    """
    return detector.detect(output, current_phase)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "SignalAction",
    # Data classes
    "PhaseSignal",
    # Detector
    "PhaseDetector",
    "detector",
    # Convenience functions
    "detect_phase",
]
