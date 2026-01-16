"""
CheckpointAgent: Enforces CGP Grey's 66-checkpoint discipline.

From muse-part-vi.md:
    "66 checkpoints is not bureaucracy. It's the difference between
    hoping for quality and guaranteeing it."

Each checkpoint:
1. Asks a specific question
2. Locks a specific element upon passing
3. Uses appropriate co-creative mode (amplify, contradict, mirror)
4. Requires explicit unlock with justification to modify

See: spec/c-gent/muse-part-vi.md
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from ..checkpoints import (
    LITTLE_KANT_CHECKPOINTS,
    YOUTUBE_CHECKPOINTS,
    Checkpoint,
    CheckpointResult,
    CoCreativeMode,
    LockedElement,
    UnlockedElement,
    get_checkpoint_by_name,
    get_checkpoints,
    get_checkpoints_by_phase,
)
from ..models import ResonanceLevel, SessionState

# =============================================================================
# Progress Tracking
# =============================================================================


@dataclass
class CheckpointProgress:
    """Progress through a checkpoint template."""

    domain: str
    current_checkpoint: int = 0
    passed: list[int] = field(default_factory=list)
    failed: list[int] = field(default_factory=list)
    locked_elements: dict[str, LockedElement] = field(default_factory=dict)
    unlocks: list[UnlockedElement] = field(default_factory=list)

    @property
    def completion_percentage(self) -> float:
        """Percentage of checkpoints completed."""
        total = len(get_checkpoints(self.domain))
        return len(self.passed) / total * 100 if total > 0 else 0

    @property
    def current_phase(self) -> str:
        """Get the current phase based on checkpoint."""
        checkpoints = get_checkpoints(self.domain)
        if self.current_checkpoint < len(checkpoints):
            return checkpoints[self.current_checkpoint].phase
        return "complete"


@dataclass
class PhaseProgress:
    """Progress within a specific phase."""

    phase: str
    checkpoints: list[Checkpoint]
    completed: list[int]
    current: int | None

    @property
    def completion_percentage(self) -> float:
        """Percentage of phase completed."""
        return len(self.completed) / len(self.checkpoints) * 100 if self.checkpoints else 0


# =============================================================================
# CheckpointAgent
# =============================================================================


class CheckpointAgent:
    """
    Enforces checkpoint discipline.

    The agent:
    1. Tracks progress through domain-specific checkpoint templates
    2. Enforces lock/unlock protocol (no regression without justification)
    3. Determines appropriate co-creative mode at each checkpoint
    4. Blocks shipping before minimum quality gates met
    """

    def __init__(self, domain: str):
        """
        Initialize checkpoint agent for a domain.

        Args:
            domain: The checkpoint template domain ("youtube", "little_kant")
        """
        self.domain = domain
        self.checkpoints = get_checkpoints(domain)
        self.progress = CheckpointProgress(domain=domain)

        # Verification functions (can be customized)
        self.verifiers: dict[str, Callable[[Any], bool]] = {}

    # -------------------------------------------------------------------------
    # Core Operations
    # -------------------------------------------------------------------------

    def get_current_checkpoint(self) -> Checkpoint | None:
        """Get the current checkpoint to work on."""
        if self.progress.current_checkpoint >= len(self.checkpoints):
            return None
        return self.checkpoints[self.progress.current_checkpoint]

    def get_next_checkpoint(self) -> Checkpoint | None:
        """Get the next checkpoint after current."""
        next_idx = self.progress.current_checkpoint + 1
        if next_idx >= len(self.checkpoints):
            return None
        return self.checkpoints[next_idx]

    def verify_checkpoint(
        self,
        checkpoint: Checkpoint,
        work: Any,
        resonance: ResonanceLevel | None = None,
    ) -> CheckpointResult:
        """
        Verify if work passes a checkpoint.

        Args:
            checkpoint: The checkpoint to verify
            work: The creative work
            resonance: Optional resonance level from taste agent

        Returns:
            CheckpointResult with pass/fail and details
        """
        failures = []

        # Check must_pass requirements
        for requirement in checkpoint.must_pass:
            if requirement in self.verifiers:
                if not self.verifiers[requirement](work):
                    failures.append(f"Failed requirement: {requirement}")
            # If no verifier, assume passed (would be configured per project)

        # For mirror mode, require at least RESONANT
        if checkpoint.co_creative_mode == CoCreativeMode.MIRROR:
            if resonance and resonance < ResonanceLevel.RESONANT:
                failures.append(f"Mirror Test failed: resonance is {resonance.description}")

        passed = len(failures) == 0

        return CheckpointResult(
            checkpoint=checkpoint,
            passed=passed,
            failures=failures,
            resonance=resonance,
        )

    def execute_checkpoint(
        self,
        work: Any,
        resonance: ResonanceLevel | None = None,
    ) -> tuple[CheckpointResult, CoCreativeMode]:
        """
        Execute the current checkpoint.

        Args:
            work: The creative work
            resonance: Resonance level from taste agent

        Returns:
            Tuple of (result, recommended co-creative mode)
        """
        checkpoint = self.get_current_checkpoint()
        if checkpoint is None:
            raise ValueError("No more checkpoints to execute")

        result = self.verify_checkpoint(checkpoint, work, resonance)
        return result, checkpoint.co_creative_mode

    def pass_checkpoint(self, checkpoint: Checkpoint, work: Any) -> LockedElement:
        """
        Mark a checkpoint as passed and lock its element.

        Args:
            checkpoint: The checkpoint that passed
            work: The work containing the element to lock

        Returns:
            LockedElement representing the lock
        """
        # Calculate content hash (simplified)
        content_hash = hashlib.sha256(str(work).encode()).hexdigest()[:16]

        locked = LockedElement(
            checkpoint=checkpoint,
            content_hash=content_hash,
            can_unlock_if=checkpoint.unlock_condition,
        )

        # Update progress
        if checkpoint.number not in self.progress.passed:
            self.progress.passed.append(checkpoint.number)

        self.progress.locked_elements[checkpoint.name] = locked
        self.progress.current_checkpoint = checkpoint.number  # Advance

        return locked

    def fail_checkpoint(self, checkpoint: Checkpoint, failures: list[str]) -> None:
        """Record a checkpoint failure."""
        if checkpoint.number not in self.progress.failed:
            self.progress.failed.append(checkpoint.number)

    def advance(self) -> Checkpoint | None:
        """Advance to the next checkpoint."""
        self.progress.current_checkpoint += 1
        return self.get_current_checkpoint()

    # -------------------------------------------------------------------------
    # Lock/Unlock Protocol
    # -------------------------------------------------------------------------

    def is_locked(self, checkpoint_name: str) -> bool:
        """Check if an element is locked."""
        return checkpoint_name in self.progress.locked_elements

    def unlock(
        self,
        checkpoint_name: str,
        justification: str,
    ) -> UnlockedElement:
        """
        Unlock a locked element for modification.

        Unlocking triggers re-verification of dependent checkpoints.

        Args:
            checkpoint_name: Name of checkpoint to unlock
            justification: Why unlocking is necessary

        Returns:
            UnlockedElement with required re-passes
        """
        if checkpoint_name not in self.progress.locked_elements:
            raise ValueError(f"Checkpoint '{checkpoint_name}' is not locked")

        locked = self.progress.locked_elements[checkpoint_name]

        # Find checkpoints that depend on this one (all after it)
        must_repass = []
        unlocked_number = locked.checkpoint.number
        for ckpt in self.checkpoints:
            if ckpt.number > unlocked_number and ckpt.number in self.progress.passed:
                must_repass.append(ckpt)
                self.progress.passed.remove(ckpt.number)

        unlocked = UnlockedElement(
            original=locked,
            justification=justification,
            must_repass=must_repass,
        )

        # Remove from locked
        del self.progress.locked_elements[checkpoint_name]
        self.progress.unlocks.append(unlocked)

        # Reset current checkpoint to the unlocked one
        self.progress.current_checkpoint = unlocked_number - 1

        return unlocked

    # -------------------------------------------------------------------------
    # Progress Queries
    # -------------------------------------------------------------------------

    def get_progress(self) -> CheckpointProgress:
        """Get current progress."""
        return self.progress

    def get_phase_progress(self, phase: str) -> PhaseProgress:
        """Get progress within a specific phase."""
        phase_checkpoints = list(get_checkpoints_by_phase(self.domain, phase))

        completed = [
            ckpt.number for ckpt in phase_checkpoints if ckpt.number in self.progress.passed
        ]

        current = None
        for ckpt in phase_checkpoints:
            if ckpt.number not in self.progress.passed:
                current = ckpt.number
                break

        return PhaseProgress(
            phase=phase,
            checkpoints=phase_checkpoints,
            completed=completed,
            current=current,
        )

    def can_ship(self) -> tuple[bool, list[str]]:
        """
        Check if work can be shipped.

        Returns:
            Tuple of (can_ship, blocking_reasons)
        """
        blockers = []

        # Must complete all checkpoints
        if len(self.progress.passed) < len(self.checkpoints):
            remaining = len(self.checkpoints) - len(self.progress.passed)
            blockers.append(f"{remaining} checkpoints remaining")

        # Check for any failures
        if self.progress.failed:
            blockers.append(f"{len(self.progress.failed)} failed checkpoints")

        return len(blockers) == 0, blockers

    # -------------------------------------------------------------------------
    # Verifier Management
    # -------------------------------------------------------------------------

    def register_verifier(
        self,
        requirement: str,
        verifier: Callable[[Any], bool],
    ) -> None:
        """Register a verification function for a requirement."""
        self.verifiers[requirement] = verifier

    def get_co_creative_mode(self, checkpoint: Checkpoint | None = None) -> CoCreativeMode:
        """Get the co-creative mode for a checkpoint."""
        if checkpoint is None:
            checkpoint = self.get_current_checkpoint()
        if checkpoint is None:
            return CoCreativeMode.NONE
        return checkpoint.co_creative_mode


# =============================================================================
# Factory Functions
# =============================================================================


def create_checkpoint_agent(domain: str) -> CheckpointAgent:
    """Create a checkpoint agent for a domain."""
    return CheckpointAgent(domain)


def create_youtube_checkpoint_agent() -> CheckpointAgent:
    """Create a checkpoint agent for YouTube videos."""
    return CheckpointAgent("youtube")


def create_little_kant_checkpoint_agent() -> CheckpointAgent:
    """Create a checkpoint agent for Little Kant episodes."""
    return CheckpointAgent("little_kant")


# =============================================================================
# Module Exports
# =============================================================================


__all__ = [
    # Types
    "CheckpointProgress",
    "PhaseProgress",
    # Agent
    "CheckpointAgent",
    # Functions
    "create_checkpoint_agent",
    "create_youtube_checkpoint_agent",
    "create_little_kant_checkpoint_agent",
]
