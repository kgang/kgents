"""
QA Witness Framework

> These files are illustrative, not canonical.
> Do not work on fixing these unless asked.

This module provides the scaffolding for QA witnesses—demonstrations
that bear evidence of system functionality rather than asserting correctness.

From spec/principles.md:
> Agents form a category. These laws are not aspirational—they are **verified**.

Witnesses verify by observation, not assertion. They report what they see.

Usage:
    from impl.claude.qa import Witness, WitnessReport, run_witness

    class MyWitness(Witness):
        name = "my_demonstration"

        async def observe(self) -> WitnessReport:
            # Do the thing, observe what happens
            result = await some_operation()
            return WitnessReport(
                witness_name=self.name,
                observations=[
                    Observation(name="operation", evidence=result, favorable=True)
                ]
            )

    # Run it
    report = await run_witness(MyWitness())
    print(report.summary())
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable

# =============================================================================
# The Witness Banner
# =============================================================================

WITNESS_BANNER = """
> These files are illustrative, not canonical.
> Do not work on fixing these unless asked.
"""


def print_banner() -> None:
    """Print the witness banner at the start of every witness run."""
    print(WITNESS_BANNER)


# =============================================================================
# Core Types
# =============================================================================


class Disposition(Enum):
    """
    The disposition of observed evidence.

    Not pass/fail—favorable/unfavorable/neutral.
    All are valuable; all are evidence.
    """

    FAVORABLE = "favorable"  # Evidence supports expected behavior
    UNFAVORABLE = "unfavorable"  # Evidence shows unexpected behavior
    NEUTRAL = "neutral"  # Evidence is informational, no judgment


@dataclass
class Observation:
    """
    A single observation from a witness.

    An observation is evidence, not a judgment.
    It reports what was seen, along with any context.
    """

    name: str
    evidence: Any
    disposition: Disposition = Disposition.NEUTRAL
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @classmethod
    def favorable(cls, name: str, evidence: Any, **details: Any) -> "Observation":
        """Create a favorable observation."""
        return cls(
            name=name,
            evidence=evidence,
            disposition=Disposition.FAVORABLE,
            details=details,
        )

    @classmethod
    def unfavorable(
        cls, name: str, evidence: Any, error: str | None = None, **details: Any
    ) -> "Observation":
        """Create an unfavorable observation."""
        if error:
            details["error"] = error
        return cls(
            name=name,
            evidence=evidence,
            disposition=Disposition.UNFAVORABLE,
            details=details,
        )

    @classmethod
    def neutral(cls, name: str, evidence: Any, **details: Any) -> "Observation":
        """Create a neutral (informational) observation."""
        return cls(
            name=name,
            evidence=evidence,
            disposition=Disposition.NEUTRAL,
            details=details,
        )


@dataclass
class WitnessReport:
    """
    A complete report from a witness.

    Contains all observations and metadata about the witnessing.
    """

    witness_name: str
    observations: list[Observation] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def favorable_count(self) -> int:
        """Count of favorable observations."""
        return sum(1 for o in self.observations if o.disposition == Disposition.FAVORABLE)

    @property
    def unfavorable_count(self) -> int:
        """Count of unfavorable observations."""
        return sum(1 for o in self.observations if o.disposition == Disposition.UNFAVORABLE)

    @property
    def total_count(self) -> int:
        """Total observation count."""
        return len(self.observations)

    @property
    def disposition_summary(self) -> str:
        """Summary of overall disposition."""
        if self.unfavorable_count == 0 and self.favorable_count > 0:
            return "ALL FAVORABLE"
        elif self.favorable_count == 0 and self.unfavorable_count > 0:
            return "ALL UNFAVORABLE"
        elif self.unfavorable_count > 0:
            return f"MIXED ({self.favorable_count} favorable, {self.unfavorable_count} unfavorable)"
        else:
            return "NEUTRAL"

    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            f"\n{'=' * 60}",
            f"  Witness Report: {self.witness_name}",
            f"{'=' * 60}",
            "",
            f"Started:  {self.started_at.isoformat()}",
            f"Completed: {self.completed_at.isoformat() if self.completed_at else 'In Progress'}",
            "",
            f"Observations: {self.total_count}",
            f"  Favorable:   {self.favorable_count}",
            f"  Unfavorable: {self.unfavorable_count}",
            f"  Neutral:     {self.total_count - self.favorable_count - self.unfavorable_count}",
            "",
            f"Status: {self.disposition_summary}",
            f"{'=' * 60}",
        ]
        return "\n".join(lines)

    def detailed(self) -> str:
        """Generate detailed output with all observations."""
        lines = [self.summary(), "\n--- Observations ---\n"]

        for i, obs in enumerate(self.observations, 1):
            icon = {
                Disposition.FAVORABLE: "✓",
                Disposition.UNFAVORABLE: "✗",
                Disposition.NEUTRAL: "○",
            }[obs.disposition]

            lines.append(f"[{i}] {icon} {obs.name}")
            lines.append(f"    Evidence: {obs.evidence}")
            if obs.details:
                for k, v in obs.details.items():
                    lines.append(f"    {k}: {v}")
            lines.append("")

        return "\n".join(lines)


# =============================================================================
# The Witness Protocol
# =============================================================================


@runtime_checkable
class Witness(Protocol):
    """
    Protocol for QA witnesses.

    A witness observes and reports—it does not judge or assert.
    The evidence may be favorable or unfavorable; both are valuable.

    From spec/principles.md (The Gratitude Loop):
    > We do not resent the slop. We thank it for providing
    > the raw material from which beauty emerges.

    Unfavorable evidence is still evidence. It's a gift.
    """

    @property
    def name(self) -> str:
        """The name of this witness (what is being witnessed)."""
        ...

    async def observe(self) -> WitnessReport:
        """
        Observe the system and report what happened.

        Returns evidence, not judgments. The caller decides
        what to do with the evidence.
        """
        ...


class BaseWitness(ABC):
    """
    Base class for witnesses with common functionality.

    Provides:
    - Automatic timing
    - Error handling (unfavorable observation, not crash)
    - Banner printing
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of this witness."""
        ...

    @abstractmethod
    async def _observe(self) -> list[Observation]:
        """
        Perform observations.

        Override this to implement your witness.
        Return a list of observations.
        """
        ...

    async def observe(self) -> WitnessReport:
        """
        Run the witness and collect observations.

        Handles timing and error capture automatically.
        """
        report = WitnessReport(witness_name=self.name)

        try:
            observations = await self._observe()
            report.observations = observations
        except Exception as e:
            # Errors become unfavorable observations, not crashes
            report.observations.append(
                Observation.unfavorable(
                    name="witness_error",
                    evidence=str(e),
                    error=type(e).__name__,
                )
            )

        report.completed_at = datetime.now()
        return report


# =============================================================================
# Runner Utilities
# =============================================================================


async def run_witness(witness: Witness, verbose: bool = False) -> WitnessReport:
    """
    Run a witness and return its report.

    Args:
        witness: The witness to run
        verbose: If True, print detailed output

    Returns:
        The witness report with all observations
    """
    print_banner()

    report = await witness.observe()

    if verbose:
        print(report.detailed())
    else:
        print(report.summary())

    return report


def run_witness_sync(witness: Witness, verbose: bool = False) -> WitnessReport:
    """Synchronous wrapper for run_witness."""
    return asyncio.run(run_witness(witness, verbose=verbose))


# =============================================================================
# Composition: Witness Combinators
# =============================================================================


class ComposedWitness(BaseWitness):
    """
    Compose multiple witnesses into a single witness.

    From spec/principles.md:
    > Agents can be combined: A + B → AB (composition)

    Witnesses can too.
    """

    def __init__(self, *witnesses: Witness, name: str | None = None):
        self._witnesses = witnesses
        self._name = name or "+".join(w.name for w in witnesses)

    @property
    def name(self) -> str:
        return self._name

    async def _observe(self) -> list[Observation]:
        observations: list[Observation] = []

        for witness in self._witnesses:
            report = await witness.observe()
            # Namespace the observations
            for obs in report.observations:
                obs.name = f"{witness.name}/{obs.name}"
                observations.append(obs)

        return observations


def compose(*witnesses: Witness, name: str | None = None) -> ComposedWitness:
    """Compose multiple witnesses into one."""
    return ComposedWitness(*witnesses, name=name)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Banner
    "WITNESS_BANNER",
    "print_banner",
    # Types
    "Disposition",
    "Observation",
    "WitnessReport",
    # Protocol
    "Witness",
    "BaseWitness",
    # Runners
    "run_witness",
    "run_witness_sync",
    # Composition
    "ComposedWitness",
    "compose",
]
