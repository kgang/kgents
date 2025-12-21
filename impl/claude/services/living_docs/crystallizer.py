"""
Teaching Crystallizer: Persist teaching moments to Brain.

Bridges the Living Docs extraction with Brain persistence,
implementing the Memory-First Documentation protocol.

The Persistence Law: Teaching moments extracted from code
MUST be crystallized in Brain.

AGENTESE: self.memory.crystallize_teaching

Usage:
    from services.living_docs import crystallize_all_teaching

    # Crystallize all current teaching moments
    stats = await crystallize_all_teaching()

    # Crystallize from specific modules
    stats = await crystallize_all_teaching(module_pattern="services.brain")

Teaching:
    gotcha: Crystallization is idempotent due to deterministic ID generation.
            Same (module, symbol, insight hash) → same teaching_id.
            (Evidence: test_crystallization.py::test_idempotent)

    gotcha: BrainPersistence requires async session; crystallize functions are async.
            Use asyncio.run() for CLI or await in async context.
            (Evidence: test_crystallization.py::test_async_crystallize)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .teaching import TeachingCollector, TeachingResult

if TYPE_CHECKING:
    from services.brain.persistence import BrainPersistence, CrystallizeResult


logger = logging.getLogger(__name__)


@dataclass
class CrystallizationStats:
    """
    Statistics from a crystallization run.

    Tracks how many teaching moments were processed and their outcomes.
    """

    total_found: int = 0
    newly_crystallized: int = 0
    already_existed: int = 0
    with_evidence: int = 0
    by_severity: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_found": self.total_found,
            "newly_crystallized": self.newly_crystallized,
            "already_existed": self.already_existed,
            "with_evidence": self.with_evidence,
            "by_severity": self.by_severity,
            "errors": self.errors,
        }


class TeachingCrystallizer:
    """
    Crystallize teaching moments from Living Docs extraction to Brain persistence.

    The core workflow:
    1. Collect teaching moments from codebase (via TeachingCollector)
    2. For each moment, call BrainPersistence.crystallize_teaching()
    3. Track statistics and report results

    This enables teaching moments to persist beyond code deletion,
    forming the Memory-First Documentation layer.
    """

    def __init__(
        self,
        brain: "BrainPersistence",
        collector: TeachingCollector | None = None,
    ):
        self.brain = brain
        self.collector = collector or TeachingCollector()

    async def crystallize_all(
        self,
        module_pattern: str | None = None,
        severity: str | None = None,
    ) -> CrystallizationStats:
        """
        Crystallize all teaching moments matching filters.

        Args:
            module_pattern: Filter by module pattern (substring match)
            severity: Filter by severity ("critical", "warning", "info")

        Returns:
            CrystallizationStats with counts and outcomes
        """
        stats = CrystallizationStats()
        stats.by_severity = {"critical": 0, "warning": 0, "info": 0}

        for result in self.collector.collect_all():
            # Apply filters
            if module_pattern and module_pattern not in result.module:
                continue
            if severity and result.moment.severity != severity:
                continue

            stats.total_found += 1
            stats.by_severity[result.moment.severity] = (
                stats.by_severity.get(result.moment.severity, 0) + 1
            )

            try:
                crystallize_result = await self._crystallize_one(result)

                if crystallize_result.is_new:
                    stats.newly_crystallized += 1
                else:
                    stats.already_existed += 1

                if crystallize_result.evidence_verified:
                    stats.with_evidence += 1

            except Exception as e:
                stats.errors.append(f"{result.module}.{result.symbol}: {e}")
                logger.warning(f"Failed to crystallize {result.symbol}: {e}")

        return stats

    async def _crystallize_one(self, result: TeachingResult) -> "CrystallizeResult":
        """Crystallize a single teaching moment."""
        return await self.brain.crystallize_teaching(
            insight=result.moment.insight,
            severity=result.moment.severity,  # type: ignore[arg-type]
            source_module=result.module,
            source_symbol=result.symbol,
            evidence=result.moment.evidence,
            source_commit=result.moment.commit,
        )


# =============================================================================
# Convenience Functions (Preferred API)
# =============================================================================


async def crystallize_all_teaching(
    brain: "BrainPersistence | None" = None,
    module_pattern: str | None = None,
    severity: str | None = None,
) -> CrystallizationStats:
    """
    Crystallize all teaching moments to Brain.

    This is the main entry point for the Memory-First Documentation workflow.

    Args:
        brain: BrainPersistence instance (will use global if None)
        module_pattern: Filter by module pattern
        severity: Filter by severity level

    Returns:
        CrystallizationStats with counts

    Usage:
        import asyncio

        # Crystallize all teaching
        stats = asyncio.run(crystallize_all_teaching())

        # Crystallize only critical
        stats = asyncio.run(crystallize_all_teaching(severity="critical"))
    """
    if brain is None:
        # Try to get from DI container or create
        try:
            from protocols.agentese.container import get_container

            container = get_container()
            brain = container.resolve("brain_persistence")
        except Exception as e:
            raise RuntimeError(
                f"No BrainPersistence provided and couldn't resolve from container: {e}"
            )

    crystallizer = TeachingCrystallizer(brain)
    return await crystallizer.crystallize_all(
        module_pattern=module_pattern,
        severity=severity,
    )


def crystallize_all_teaching_sync(
    brain: "BrainPersistence | None" = None,
    module_pattern: str | None = None,
    severity: str | None = None,
) -> CrystallizationStats:
    """
    Synchronous wrapper for crystallize_all_teaching.

    For CLI usage where asyncio.run() is appropriate.
    """
    return asyncio.run(
        crystallize_all_teaching(
            brain=brain,
            module_pattern=module_pattern,
            severity=severity,
        )
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "CrystallizationStats",
    "TeachingCrystallizer",
    "crystallize_all_teaching",
    "crystallize_all_teaching_sync",
]
