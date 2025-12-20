"""
N-Phase Prompt Compiler Schema.

Defines the ProjectDefinition and all nested types for the N-Phase compiler.

Laws:
- All dataclasses are frozen (immutable)
- Validation catches structural errors before compilation
- YAML round-trip preserves all data
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal

import yaml

# === Enums ===


class Classification(str, Enum):
    """Project classification level."""

    CROWN_JEWEL = "crown_jewel"  # Full 11-phase ceremony
    STANDARD = "standard"  # Standard 11-phase
    QUICK_WIN = "quick_win"  # Compressed 3-phase


class Effort(str, Enum):
    """T-shirt sizing for component effort."""

    XS = "XS"  # < 1 hour
    S = "S"  # 1-4 hours
    M = "M"  # 4-8 hours
    L = "L"  # 1-2 days
    XL = "XL"  # 3+ days


class PhaseStatus(str, Enum):
    """Phase execution status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    TOUCHED = "touched"
    SKIPPED = "skipped"
    DEFERRED = "deferred"


PHASE_NAMES = [
    "PLAN",
    "RESEARCH",
    "DEVELOP",
    "STRATEGIZE",
    "CROSS-SYNERGIZE",
    "IMPLEMENT",
    "QA",
    "TEST",
    "EDUCATE",
    "MEASURE",
    "REFLECT",
]

COMPRESSED_PHASES = ["SENSE", "ACT", "REFLECT"]  # 3-phase mode


# === Nested Dataclasses ===


@dataclass(frozen=True)
class ProjectScope:
    """Defines what the project is and isn't."""

    goal: str
    non_goals: tuple[str, ...] = field(default_factory=tuple)
    parallel_tracks: dict[str, str] = field(default_factory=dict)  # ID -> description

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "non_goals": list(self.non_goals),
            "parallel_tracks": dict(self.parallel_tracks),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectScope:
        return cls(
            goal=data["goal"],
            non_goals=tuple(data.get("non_goals", [])),
            parallel_tracks=data.get("parallel_tracks", {}),
        )


@dataclass(frozen=True)
class Decision:
    """A recorded design decision."""

    id: str  # e.g., "D1"
    choice: str  # What was decided
    rationale: str  # Why

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "choice": self.choice, "rationale": self.rationale}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Decision:
        return cls(id=data["id"], choice=data["choice"], rationale=data["rationale"])


@dataclass(frozen=True)
class FileRef:
    """Reference to a file location."""

    path: str
    lines: str | None = None  # e.g., "94-107"
    purpose: str | None = None  # What it's for

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"path": self.path}
        if self.lines:
            d["lines"] = self.lines
        if self.purpose:
            d["purpose"] = self.purpose
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FileRef:
        return cls(
            path=data["path"],
            lines=data.get("lines"),
            purpose=data.get("purpose"),
        )

    def __str__(self) -> str:
        if self.lines:
            return f"{self.path}:{self.lines}"
        return self.path


@dataclass(frozen=True)
class Invariant:
    """A law that must hold throughout the project."""

    name: str
    requirement: str
    verification: str | None = None  # How to verify

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "requirement": self.requirement}
        if self.verification:
            d["verification"] = self.verification
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Invariant:
        return cls(
            name=data["name"],
            requirement=data["requirement"],
            verification=data.get("verification"),
        )


@dataclass(frozen=True)
class Blocker:
    """An obstacle with evidence and resolution."""

    id: str  # e.g., "B1"
    description: str
    evidence: str  # File:line or explanation
    resolution: str | None = None  # How it was/will be resolved
    status: Literal["open", "resolved", "deferred"] = "open"

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "description": self.description,
            "evidence": self.evidence,
            "status": self.status,
        }
        if self.resolution:
            d["resolution"] = self.resolution
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Blocker:
        return cls(
            id=data["id"],
            description=data["description"],
            evidence=data["evidence"],
            resolution=data.get("resolution"),
            status=data.get("status", "open"),
        )


@dataclass(frozen=True)
class Component:
    """An implementation unit."""

    id: str  # e.g., "C1"
    name: str
    location: str  # Target file path
    effort: Effort = Effort.M
    dependencies: tuple[str, ...] = field(default_factory=tuple)  # Component IDs
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "effort": self.effort.value,
        }
        if self.dependencies:
            d["dependencies"] = list(self.dependencies)
        if self.description:
            d["description"] = self.description
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Component:
        return cls(
            id=data["id"],
            name=data["name"],
            location=data["location"],
            effort=Effort(data.get("effort", "M")),
            dependencies=tuple(data.get("dependencies", [])),
            description=data.get("description"),
        )


@dataclass(frozen=True)
class Wave:
    """An execution batch."""

    name: str
    components: tuple[str, ...]  # Component IDs
    strategy: str | None = None  # Execution strategy description

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name, "components": list(self.components)}
        if self.strategy:
            d["strategy"] = self.strategy
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Wave:
        return cls(
            name=data["name"],
            components=tuple(data["components"]),
            strategy=data.get("strategy"),
        )


@dataclass(frozen=True)
class Checkpoint:
    """A decision gate."""

    id: str  # e.g., "CP1"
    name: str
    criteria: str  # What must be true

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "criteria": self.criteria}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Checkpoint:
        return cls(id=data["id"], name=data["name"], criteria=data["criteria"])


@dataclass(frozen=True)
class EntropyBudget:
    """Entropy allocation for exploration."""

    total: float
    allocation: dict[str, float] = field(default_factory=dict)  # Phase -> amount
    spent: dict[str, float] = field(default_factory=dict)  # Phase -> spent

    def remaining(self) -> float:
        return self.total - sum(self.spent.values())

    def validate(self) -> list[str]:
        """Return validation errors."""
        errors: list[str] = []
        allocated = sum(self.allocation.values())
        # Only validate if allocation is specified
        if self.allocation and abs(allocated - self.total) > 0.001:
            errors.append(f"Allocation ({allocated}) != total ({self.total})")
        for phase, amount in self.spent.items():
            if phase in self.allocation and amount > self.allocation[phase] + 0.001:
                errors.append(f"Phase {phase} overspent: {amount} > {self.allocation[phase]}")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "allocation": dict(self.allocation),
            "spent": dict(self.spent),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EntropyBudget:
        return cls(
            total=data["total"],
            allocation=data.get("allocation", {}),
            spent=data.get("spent", {}),
        )


@dataclass(frozen=True)
class PhaseOverride:
    """Custom instructions for a specific phase."""

    investigations: tuple[str, ...] = field(default_factory=tuple)
    exit_criteria: tuple[str, ...] = field(default_factory=tuple)
    skip_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.investigations:
            d["investigations"] = list(self.investigations)
        if self.exit_criteria:
            d["exit_criteria"] = list(self.exit_criteria)
        if self.skip_reason:
            d["skip_reason"] = self.skip_reason
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PhaseOverride:
        return cls(
            investigations=tuple(data.get("investigations", [])),
            exit_criteria=tuple(data.get("exit_criteria", [])),
            skip_reason=data.get("skip_reason"),
        )


# === Root Schema ===


@dataclass(frozen=True)
class ValidationResult:
    """Result of ProjectDefinition validation."""

    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def raise_if_invalid(self) -> None:
        if not self.is_valid:
            raise ValueError(f"Invalid ProjectDefinition: {'; '.join(self.errors)}")


@dataclass(frozen=True)
class ProjectDefinition:
    """
    Input schema for the N-Phase Prompt Compiler.

    Laws:
    - All required fields present (validation)
    - Component IDs unique
    - Wave components reference valid component IDs
    - Checkpoint criteria reference valid component IDs
    - Entropy allocations sum to total
    """

    name: str
    classification: Classification
    scope: ProjectScope

    # Optional but recommended
    decisions: tuple[Decision, ...] = field(default_factory=tuple)
    file_map: tuple[FileRef, ...] = field(default_factory=tuple)
    invariants: tuple[Invariant, ...] = field(default_factory=tuple)
    blockers: tuple[Blocker, ...] = field(default_factory=tuple)
    components: tuple[Component, ...] = field(default_factory=tuple)
    waves: tuple[Wave, ...] = field(default_factory=tuple)
    checkpoints: tuple[Checkpoint, ...] = field(default_factory=tuple)

    # Entropy tracking
    entropy: EntropyBudget | None = None

    # Phase customization
    n_phases: Literal[3, 11] = 11
    phase_overrides: dict[str, PhaseOverride] = field(default_factory=dict)
    phase_ledger: dict[str, PhaseStatus] = field(default_factory=dict)

    # Metadata
    session_notes: str | None = None

    def validate(self) -> ValidationResult:
        """Verify all laws hold."""
        errors: list[str] = []
        warnings: list[str] = []

        # Law 1: Component IDs unique
        component_ids = {c.id for c in self.components}
        if len(component_ids) != len(self.components):
            errors.append("Duplicate component IDs detected")

        # Law 2: Wave components reference valid IDs
        for wave in self.waves:
            for cid in wave.components:
                if cid not in component_ids:
                    errors.append(f"Wave '{wave.name}' references unknown component: {cid}")

        # Law 3: Blocker IDs unique
        blocker_ids = {b.id for b in self.blockers}
        if len(blocker_ids) != len(self.blockers):
            errors.append("Duplicate blocker IDs detected")

        # Law 4: Decision IDs unique
        decision_ids = {d.id for d in self.decisions}
        if len(decision_ids) != len(self.decisions):
            errors.append("Duplicate decision IDs detected")

        # Law 5: Entropy conservation
        if self.entropy:
            entropy_errors = self.entropy.validate()
            errors.extend(entropy_errors)

        # Law 6: Dependencies reference valid components
        for comp in self.components:
            for dep in comp.dependencies:
                if dep not in component_ids:
                    errors.append(f"Component '{comp.id}' depends on unknown: {dep}")

        # Warnings (non-blocking)
        if not self.file_map:
            warnings.append("No file_map provided (RESEARCH not done?)")
        if not self.invariants:
            warnings.append("No invariants provided (DEVELOP not done?)")
        if not self.waves and self.components:
            warnings.append("Components defined but no waves (STRATEGIZE not done?)")

        return ValidationResult(errors=tuple(errors), warnings=tuple(warnings))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for YAML output."""
        d: dict[str, Any] = {
            "name": self.name,
            "classification": self.classification.value,
            "scope": self.scope.to_dict(),
            "n_phases": self.n_phases,
        }
        if self.decisions:
            d["decisions"] = [dec.to_dict() for dec in self.decisions]
        if self.file_map:
            d["file_map"] = [f.to_dict() for f in self.file_map]
        if self.invariants:
            d["invariants"] = [inv.to_dict() for inv in self.invariants]
        if self.blockers:
            d["blockers"] = [b.to_dict() for b in self.blockers]
        if self.components:
            d["components"] = [c.to_dict() for c in self.components]
        if self.waves:
            d["waves"] = [w.to_dict() for w in self.waves]
        if self.checkpoints:
            d["checkpoints"] = [cp.to_dict() for cp in self.checkpoints]
        if self.entropy:
            d["entropy"] = self.entropy.to_dict()
        if self.phase_overrides:
            d["phase_overrides"] = {k: v.to_dict() for k, v in self.phase_overrides.items()}
        if self.phase_ledger:
            d["phase_ledger"] = {
                k: v.value if hasattr(v, "value") else v for k, v in self.phase_ledger.items()
            }
        if self.session_notes:
            d["session_notes"] = self.session_notes
        return d

    def to_yaml(self) -> str:
        """Serialize to YAML string."""
        result: str = yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectDefinition:
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            classification=Classification(data["classification"]),
            scope=ProjectScope.from_dict(data["scope"]),
            n_phases=data.get("n_phases", 11),
            decisions=tuple(Decision.from_dict(d) for d in data.get("decisions", [])),
            file_map=tuple(FileRef.from_dict(f) for f in data.get("file_map", [])),
            invariants=tuple(Invariant.from_dict(i) for i in data.get("invariants", [])),
            blockers=tuple(Blocker.from_dict(b) for b in data.get("blockers", [])),
            components=tuple(Component.from_dict(c) for c in data.get("components", [])),
            waves=tuple(Wave.from_dict(w) for w in data.get("waves", [])),
            checkpoints=tuple(Checkpoint.from_dict(cp) for cp in data.get("checkpoints", [])),
            entropy=(EntropyBudget.from_dict(data["entropy"]) if "entropy" in data else None),
            phase_overrides={
                k: PhaseOverride.from_dict(v) for k, v in data.get("phase_overrides", {}).items()
            },
            phase_ledger={k: PhaseStatus(v) for k, v in data.get("phase_ledger", {}).items()},
            session_notes=data.get("session_notes"),
        )

    @classmethod
    def from_yaml(cls, yaml_content: str) -> ProjectDefinition:
        """Parse from YAML string."""
        data = yaml.safe_load(yaml_content)
        return cls.from_dict(data)

    @classmethod
    def from_yaml_file(cls, path: str | Path) -> ProjectDefinition:
        """Load from YAML file."""
        with open(path) as f:
            return cls.from_yaml(f.read())

    @classmethod
    def from_plan_header(cls, plan_path: str | Path) -> ProjectDefinition:
        """
        Bootstrap from existing plan file header.

        Maps plan header fields to ProjectDefinition:
        - path -> name
        - status -> (derived)
        - importance -> classification
        - phase_ledger -> phase_ledger
        - entropy -> entropy
        - session_notes -> session_notes
        """
        with open(plan_path) as f:
            content = f.read()

        # Extract YAML frontmatter
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            raise ValueError(f"No YAML frontmatter in {plan_path}")

        header = yaml.safe_load(match.group(1))

        # Map to ProjectDefinition
        importance = header.get("importance", "standard")
        classification = (
            Classification.CROWN_JEWEL if importance == "crown_jewel" else Classification.STANDARD
        )

        entropy_data = header.get("entropy", {})
        entropy = (
            EntropyBudget(
                total=entropy_data.get("planned", 0.75),
                spent={"PLAN": entropy_data.get("spent", 0)},
            )
            if entropy_data
            else None
        )

        phase_ledger = {k: PhaseStatus(v) for k, v in header.get("phase_ledger", {}).items()}

        # Extract goal from session notes or path
        session_notes = header.get("session_notes", "")
        goal = session_notes.split("\n")[0] if session_notes else header.get("path", "")

        return cls(
            name=header.get("path", "unknown").split("/")[-1],
            classification=classification,
            scope=ProjectScope(goal=goal),
            entropy=entropy,
            phase_ledger=phase_ledger,
            session_notes=session_notes if session_notes else None,
        )
