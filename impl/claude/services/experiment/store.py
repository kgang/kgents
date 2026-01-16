"""
Experiment Store: Persistence for Experiments.

Provides CRUD operations for experiments with async SQLAlchemy.

Philosophy:
    "Every experiment is a mark in the ledger of knowledge."

Teaching:
    gotcha: Experiments are stored with JSON serialization. Complex types
            (datetime, Enum) must be converted to/from serializable formats.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import get_async_session
from models.experiment import ExperimentModel

if TYPE_CHECKING:
    from .types import Experiment

logger = logging.getLogger("kgents.experiment.store")


class ExperimentStore:
    """
    Store for experiment persistence.

    Provides:
    - save: Save or update experiment
    - get: Retrieve experiment by ID
    - list_recent: List recent experiments
    - list_by_type: List experiments by type
    - list_today: List experiments from today
    """

    async def save(self, experiment: Experiment) -> None:
        """
        Save or update experiment.

        Args:
            experiment: Experiment to save
        """
        async with get_async_session() as session:
            # Check if exists
            stmt = select(ExperimentModel).where(ExperimentModel.id == experiment.id)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing
                await self._update_model(existing, experiment)
            else:
                # Create new
                model = await self._to_model(experiment)
                session.add(model)

            await session.commit()
            logger.debug(f"Saved experiment {experiment.id}")

    async def get(self, experiment_id: str) -> Experiment | None:
        """
        Retrieve experiment by ID.

        Args:
            experiment_id: Experiment ID

        Returns:
            Experiment if found, None otherwise
        """
        async with get_async_session() as session:
            stmt = select(ExperimentModel).where(ExperimentModel.id == experiment_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return await self._from_model(model)
            return None

    async def list_recent(self, limit: int = 20) -> list[Experiment]:
        """
        List recent experiments.

        Args:
            limit: Maximum number of experiments to return

        Returns:
            List of experiments, most recent first
        """
        async with get_async_session() as session:
            stmt = select(ExperimentModel).order_by(ExperimentModel.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            models = result.scalars().all()

            return [await self._from_model(m) for m in models]

    async def list_by_type(self, exp_type: str, limit: int = 20) -> list[Experiment]:
        """
        List experiments by type.

        Args:
            exp_type: Experiment type (generate, parse, laws, etc.)
            limit: Maximum number to return

        Returns:
            List of experiments of specified type
        """
        async with get_async_session() as session:
            stmt = (
                select(ExperimentModel)
                .where(ExperimentModel.type == exp_type)
                .order_by(ExperimentModel.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            models = result.scalars().all()

            return [await self._from_model(m) for m in models]

    async def list_today(self) -> list[Experiment]:
        """
        List experiments from today.

        Returns:
            List of experiments created today
        """
        async with get_async_session() as session:
            from datetime import UTC

            today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

            stmt = (
                select(ExperimentModel)
                .where(ExperimentModel.created_at >= today_start)
                .order_by(ExperimentModel.created_at.desc())
            )
            result = await session.execute(stmt)
            models = result.scalars().all()

            return [await self._from_model(m) for m in models]

    async def _to_model(self, experiment: Experiment) -> ExperimentModel:
        """Convert Experiment to ExperimentModel."""
        # Compute summary stats
        trials_total = len(experiment.trials)
        trials_success = sum(1 for t in experiment.trials if t.success)
        success_rate = trials_success / trials_total if trials_total > 0 else 0.0

        return ExperimentModel(
            id=experiment.id,
            type=experiment.config.type.value,
            status=experiment.status.value,
            config=experiment.config.to_dict(),
            trials=[t.to_dict() for t in experiment.trials],
            evidence=experiment.evidence.to_dict() if experiment.evidence else None,
            mark_ids=experiment.mark_ids,
            started_at=experiment.started_at,
            completed_at=experiment.completed_at,
            created_at=experiment.created_at,
            trials_total=trials_total,
            trials_success=trials_success,
            success_rate=success_rate,
        )

    async def _update_model(
        self,
        model: ExperimentModel,
        experiment: Experiment,
    ) -> None:
        """Update existing model with experiment data."""
        # Compute summary stats
        trials_total = len(experiment.trials)
        trials_success = sum(1 for t in experiment.trials if t.success)
        success_rate = trials_success / trials_total if trials_total > 0 else 0.0

        model.status = experiment.status.value
        model.config = experiment.config.to_dict()
        model.trials = [t.to_dict() for t in experiment.trials]
        model.evidence = experiment.evidence.to_dict() if experiment.evidence else None
        model.mark_ids = experiment.mark_ids
        model.started_at = experiment.started_at
        model.completed_at = experiment.completed_at
        model.trials_total = trials_total
        model.trials_success = trials_success
        model.success_rate = success_rate

    async def _from_model(self, model: ExperimentModel) -> Experiment:
        """Convert ExperimentModel to Experiment."""
        from .types import Experiment

        return Experiment.from_dict(
            {
                "id": model.id,
                "config": model.config,
                "status": model.status,
                "trials": model.trials,
                "evidence": model.evidence,
                "mark_ids": model.mark_ids,
                "started_at": model.started_at.isoformat() if model.started_at else None,
                "completed_at": model.completed_at.isoformat() if model.completed_at else None,
                "created_at": model.created_at.isoformat(),
            }
        )


# Global instance
_store: ExperimentStore | None = None


def get_experiment_store() -> ExperimentStore:
    """Get global ExperimentStore instance."""
    global _store
    if _store is None:
        _store = ExperimentStore()
    return _store


__all__ = [
    "ExperimentStore",
    "get_experiment_store",
]
