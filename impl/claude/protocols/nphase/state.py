"""
N-Phase State Management.

Updates project state with phase output.

Laws:
- State only grows (no information loss)
- Entropy budget decrements correctly
- Phase ledger updates correctly

Design Decision (B5): State is stored in separate file, not in
the original ProjectDefinition YAML. This is non-destructive.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .schema import (
    Blocker,
    EntropyBudget,
    PhaseStatus,
    ProjectDefinition,
)


@dataclass(frozen=True)
class Handle:
    """A created artifact."""

    name: str
    location: str
    phase: str


@dataclass(frozen=True)
class PhaseOutput:
    """Output from executing a phase."""

    phase: str
    handles: tuple[Handle, ...] = ()
    entropy_spent: float = 0.0
    notes: str | None = None
    blocker_resolutions: dict[str, str] | None = None  # blocker_id -> resolution

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "phase": self.phase,
            "handles": [
                {"name": h.name, "location": h.location, "phase": h.phase}
                for h in self.handles
            ],
            "entropy_spent": self.entropy_spent,
        }
        if self.notes:
            d["notes"] = self.notes
        if self.blocker_resolutions:
            d["blocker_resolutions"] = self.blocker_resolutions
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PhaseOutput:
        return cls(
            phase=data["phase"],
            handles=tuple(
                Handle(name=h["name"], location=h["location"], phase=h["phase"])
                for h in data.get("handles", [])
            ),
            entropy_spent=data.get("entropy_spent", 0.0),
            notes=data.get("notes"),
            blocker_resolutions=data.get("blocker_resolutions"),
        )


@dataclass
class CumulativeState:
    """
    Cumulative state across phase executions.

    Stored separately from ProjectDefinition for non-destructive persistence.
    """

    handles: list[Handle]
    entropy_spent: dict[str, float]  # phase -> amount
    phase_outputs: list[PhaseOutput]

    def to_dict(self) -> dict[str, Any]:
        return {
            "handles": [
                {"name": h.name, "location": h.location, "phase": h.phase}
                for h in self.handles
            ],
            "entropy_spent": self.entropy_spent,
            "phase_outputs": [o.to_dict() for o in self.phase_outputs],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CumulativeState:
        return cls(
            handles=[
                Handle(name=h["name"], location=h["location"], phase=h["phase"])
                for h in data.get("handles", [])
            ],
            entropy_spent=data.get("entropy_spent", {}),
            phase_outputs=[
                PhaseOutput.from_dict(o) for o in data.get("phase_outputs", [])
            ],
        )

    def save(self, path: str | Path) -> None:
        """Save state to JSON file."""
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> CumulativeState:
        """Load state from JSON file."""
        data = json.loads(Path(path).read_text())
        return cls.from_dict(data)

    @classmethod
    def empty(cls) -> CumulativeState:
        """Create empty initial state."""
        return cls(handles=[], entropy_spent={}, phase_outputs=[])


class NPhaseStateUpdater:
    """
    Updates project state with phase output.

    Laws:
    - State only grows (no information loss)
    - Entropy budget decrements correctly
    - Phase ledger updates correctly

    Design Decision (B5): State is stored in separate file, not in
    the original ProjectDefinition YAML. This is non-destructive.
    """

    def update(
        self,
        project: ProjectDefinition,
        state: CumulativeState,
        output: PhaseOutput,
    ) -> tuple[ProjectDefinition, CumulativeState]:
        """
        Update project and state with phase execution results.

        Updates:
        - Handles list (state)
        - Entropy spent (project + state)
        - Phase ledger (project)
        - Blocker resolutions (project)

        Returns:
            Updated (ProjectDefinition, CumulativeState) tuple
        """
        # Update state
        new_handles = list(state.handles) + list(output.handles)
        new_entropy_spent = dict(state.entropy_spent)
        new_entropy_spent[output.phase] = (
            new_entropy_spent.get(output.phase, 0) + output.entropy_spent
        )
        new_outputs = list(state.phase_outputs) + [output]

        new_state = CumulativeState(
            handles=new_handles,
            entropy_spent=new_entropy_spent,
            phase_outputs=new_outputs,
        )

        # Update project
        new_phase_ledger = dict(project.phase_ledger)
        new_phase_ledger[output.phase] = PhaseStatus.TOUCHED

        # Update entropy in project
        new_entropy = None
        if project.entropy:
            new_entropy_spent_proj = dict(project.entropy.spent)
            new_entropy_spent_proj[output.phase] = (
                new_entropy_spent_proj.get(output.phase, 0) + output.entropy_spent
            )
            new_entropy = EntropyBudget(
                total=project.entropy.total,
                allocation=project.entropy.allocation,
                spent=new_entropy_spent_proj,
            )

        # Update blocker resolutions
        new_blockers = list(project.blockers)
        if output.blocker_resolutions:
            new_blockers = []
            for b in project.blockers:
                if b.id in output.blocker_resolutions:
                    new_blockers.append(
                        Blocker(
                            id=b.id,
                            description=b.description,
                            evidence=b.evidence,
                            resolution=output.blocker_resolutions[b.id],
                            status="resolved",
                        )
                    )
                else:
                    new_blockers.append(b)

        # Create updated project (frozen, so we rebuild)
        new_project = ProjectDefinition(
            name=project.name,
            classification=project.classification,
            scope=project.scope,
            decisions=project.decisions,
            file_map=project.file_map,
            invariants=project.invariants,
            blockers=tuple(new_blockers),
            components=project.components,
            waves=project.waves,
            checkpoints=project.checkpoints,
            entropy=new_entropy,
            n_phases=project.n_phases,
            phase_overrides=project.phase_overrides,
            phase_ledger=new_phase_ledger,
            session_notes=project.session_notes,
        )

        return new_project, new_state


# Singleton for convenience
state_updater = NPhaseStateUpdater()
