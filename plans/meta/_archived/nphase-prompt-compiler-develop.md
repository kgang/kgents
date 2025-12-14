---
path: plans/meta/_research/nphase-prompt-compiler-develop
status: complete
progress: 100
last_touched: 2025-12-14
touched_by: claude-opus-4.5
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: pending
entropy:
  planned: 0.10
  spent: 0.08
  returned: 0.02
---

# DEVELOP: N-Phase Prompt Compiler

> *"Compress the design into executable contracts."*

**Develop completed**: 2025-12-14
**Entropy spent**: 0.08/0.10

---

## Executive Summary

This document defines the complete schema, template engine, and compiler architecture for the N-Phase Prompt Compiler. All blockers (B1-B5) are resolved with concrete design decisions.

**Key Design Decisions**:
1. **Python-first schema** with `.from_yaml()` and `.to_yaml()` methods
2. **Hardcoded phase templates** (no runtime file I/O)
3. **Markdown output** (AST deferred to later iteration)
4. **Special case in `ConceptContextResolver`** for `concept.nphase.*`
5. **Separate state file** for non-destructive persistence

---

## 1. Schema Definitions

### 1.1 Core Types

```python
# impl/claude/protocols/nphase/schema.py

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Any
from pathlib import Path
import yaml

# === Enums ===

class Classification(str, Enum):
    """Project classification level."""
    CROWN_JEWEL = "crown_jewel"   # Full 11-phase ceremony
    STANDARD = "standard"          # Standard 11-phase
    QUICK_WIN = "quick_win"        # Compressed 3-phase

class Effort(str, Enum):
    """T-shirt sizing for component effort."""
    XS = "XS"  # < 1 hour
    S = "S"    # 1-4 hours
    M = "M"    # 4-8 hours
    L = "L"    # 1-2 days
    XL = "XL"  # 3+ days

class PhaseStatus(str, Enum):
    """Phase execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    TOUCHED = "touched"
    SKIPPED = "skipped"
    DEFERRED = "deferred"

PHASE_NAMES = [
    "PLAN", "RESEARCH", "DEVELOP", "STRATEGIZE", "CROSS-SYNERGIZE",
    "IMPLEMENT", "QA", "TEST", "EDUCATE", "MEASURE", "REFLECT"
]

COMPRESSED_PHASES = ["SENSE", "ACT", "REFLECT"]  # 3-phase mode
```

### 1.2 Nested Dataclasses

```python
# === Scope ===

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


# === Decisions ===

@dataclass(frozen=True)
class Decision:
    """A recorded design decision."""
    id: str          # e.g., "D1"
    choice: str      # What was decided
    rationale: str   # Why

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "choice": self.choice, "rationale": self.rationale}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Decision:
        return cls(id=data["id"], choice=data["choice"], rationale=data["rationale"])


# === File References ===

@dataclass(frozen=True)
class FileRef:
    """Reference to a file location."""
    path: str
    lines: str | None = None     # e.g., "94-107"
    purpose: str | None = None   # What it's for

    def to_dict(self) -> dict[str, Any]:
        d = {"path": self.path}
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


# === Invariants ===

@dataclass(frozen=True)
class Invariant:
    """A law that must hold throughout the project."""
    name: str
    requirement: str
    verification: str | None = None  # How to verify

    def to_dict(self) -> dict[str, Any]:
        d = {"name": self.name, "requirement": self.requirement}
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


# === Blockers ===

@dataclass(frozen=True)
class Blocker:
    """An obstacle with evidence and resolution."""
    id: str              # e.g., "B1"
    description: str
    evidence: str        # File:line or explanation
    resolution: str | None = None  # How it was/will be resolved
    status: Literal["open", "resolved", "deferred"] = "open"

    def to_dict(self) -> dict[str, Any]:
        d = {
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


# === Components ===

@dataclass(frozen=True)
class Component:
    """An implementation unit."""
    id: str              # e.g., "C1"
    name: str
    location: str        # Target file path
    effort: Effort = Effort.M
    dependencies: tuple[str, ...] = field(default_factory=tuple)  # Component IDs
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = {
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


# === Waves ===

@dataclass(frozen=True)
class Wave:
    """An execution batch."""
    name: str
    components: tuple[str, ...]  # Component IDs
    strategy: str | None = None  # Execution strategy description

    def to_dict(self) -> dict[str, Any]:
        d = {"name": self.name, "components": list(self.components)}
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


# === Checkpoints ===

@dataclass(frozen=True)
class Checkpoint:
    """A decision gate."""
    id: str         # e.g., "CP1"
    name: str
    criteria: str   # What must be true

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "criteria": self.criteria}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Checkpoint:
        return cls(id=data["id"], name=data["name"], criteria=data["criteria"])


# === Entropy Budget ===

@dataclass(frozen=True)
class EntropyBudget:
    """Entropy allocation for exploration."""
    total: float
    allocation: dict[str, float] = field(default_factory=dict)  # Phase -> amount
    spent: dict[str, float] = field(default_factory=dict)       # Phase -> spent

    def remaining(self) -> float:
        return self.total - sum(self.spent.values())

    def validate(self) -> list[str]:
        """Return validation errors."""
        errors = []
        allocated = sum(self.allocation.values())
        if abs(allocated - self.total) > 0.001:
            errors.append(f"Allocation ({allocated}) != total ({self.total})")
        for phase, amount in self.spent.items():
            if phase in self.allocation and amount > self.allocation[phase]:
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


# === Phase Override ===

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
```

### 1.3 ProjectDefinition (Root Schema)

```python
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

    def validate(self) -> "ValidationResult":
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
            d["phase_ledger"] = {k: v.value for k, v in self.phase_ledger.items()}
        if self.session_notes:
            d["session_notes"] = self.session_notes
        return d

    def to_yaml(self) -> str:
        """Serialize to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)

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
            entropy=EntropyBudget.from_dict(data["entropy"]) if "entropy" in data else None,
            phase_overrides={k: PhaseOverride.from_dict(v) for k, v in data.get("phase_overrides", {}).items()},
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
        import re
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            raise ValueError(f"No YAML frontmatter in {plan_path}")

        header = yaml.safe_load(match.group(1))

        # Map to ProjectDefinition
        importance = header.get("importance", "standard")
        classification = Classification.CROWN_JEWEL if importance == "crown_jewel" else Classification.STANDARD

        entropy_data = header.get("entropy", {})
        entropy = EntropyBudget(
            total=entropy_data.get("planned", 0.75),
            spent={"PLAN": entropy_data.get("spent", 0)},
        ) if entropy_data else None

        phase_ledger = {
            k: PhaseStatus(v)
            for k, v in header.get("phase_ledger", {}).items()
        }

        return cls(
            name=header.get("path", "unknown").split("/")[-1],
            classification=classification,
            scope=ProjectScope(goal=header.get("session_notes", "").split("\n")[0]),
            entropy=entropy,
            phase_ledger=phase_ledger,
            session_notes=header.get("session_notes"),
        )


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
```

---

## 2. Template Engine Architecture

### 2.1 Phase Templates (Hardcoded)

```python
# impl/claude/protocols/nphase/templates/__init__.py

"""
Phase templates for N-Phase Prompt Compiler.

Design Decision (B2): Templates are hardcoded Python strings, not runtime-loaded
from markdown files. This provides:
- Faster compilation (no file I/O)
- Version control (templates change with code)
- Type safety (templates are string constants)

Future: Extract from docs/skills/n-phase-cycle/*.md if runtime flexibility needed.
"""

from typing import NamedTuple

class PhaseTemplate(NamedTuple):
    """Template for a single phase."""
    name: str
    mission: str
    actions: str
    exit_criteria: str
    continuation: str
    minimum_artifact: str


# Phase family mapping for 3-phase compression
PHASE_FAMILIES = {
    "SENSE": ["PLAN", "RESEARCH", "DEVELOP"],
    "ACT": ["STRATEGIZE", "CROSS-SYNERGIZE", "IMPLEMENT", "QA", "TEST"],
    "REFLECT": ["EDUCATE", "MEASURE", "REFLECT"],
}


PHASE_TEMPLATES: dict[str, PhaseTemplate] = {
    "PLAN": PhaseTemplate(
        name="PLAN",
        mission="Define scope, exit criteria, and attention budget. Draw entropy sip.",
        actions="""1. Read existing context (handles, prior phases)
2. Clarify scope boundaries (what IS and ISN'T in scope)
3. Define exit criteria for this work
4. Allocate entropy budget across phases
5. Identify parallel tracks if applicable""",
        exit_criteria="""- [ ] Scope boundaries clear
- [ ] Exit criteria defined
- [ ] Entropy budget allocated
- [ ] Parallel tracks identified (if any)""",
        continuation="RESEARCH",
        minimum_artifact="Scope, exit criteria, attention budget, entropy sip",
    ),

    "RESEARCH": PhaseTemplate(
        name="RESEARCH",
        mission="Map the terrain. Build file map, surface blockers with evidence.",
        actions="""1. Search for existing implementations
2. Document file locations with line numbers
3. Identify blockers with file:line evidence
4. Note prior art that can be reused
5. Surface invariants from existing code""",
        exit_criteria="""- [ ] File map complete with line references
- [ ] Blockers surfaced with evidence
- [ ] Prior art documented
- [ ] Did NOT modify source files""",
        continuation="DEVELOP",
        minimum_artifact="File map + blockers with refs",
    ),

    "DEVELOP": PhaseTemplate(
        name="DEVELOP",
        mission="Design contracts and APIs. Define what will be built.",
        actions="""1. Define data schemas/types
2. Specify API contracts
3. Document invariants/laws
4. Resolve blockers with design decisions
5. Create component breakdown""",
        exit_criteria="""- [ ] Schemas defined
- [ ] API contracts specified
- [ ] Invariants documented
- [ ] Blockers resolved with decisions""",
        continuation="STRATEGIZE",
        minimum_artifact="Contract/API deltas or law assertions",
    ),

    "STRATEGIZE": PhaseTemplate(
        name="STRATEGIZE",
        mission="Sequence the work. Define waves and checkpoints.",
        actions="""1. Order components by dependencies
2. Group into execution waves
3. Define checkpoints between waves
4. Identify parallelization opportunities
5. Set risk mitigation order""",
        exit_criteria="""- [ ] Waves defined with rationale
- [ ] Checkpoints specified
- [ ] Dependencies mapped
- [ ] Critical path identified""",
        continuation="CROSS-SYNERGIZE",
        minimum_artifact="Sequencing with rationale",
    ),

    "CROSS-SYNERGIZE": PhaseTemplate(
        name="CROSS-SYNERGIZE",
        mission="Find compositions. Identify cross-cutting concerns and synergies.",
        actions="""1. Identify shared types/interfaces
2. Find cross-plan dependencies
3. Document runtime compositions
4. Note potential conflicts
5. Design integration points""",
        exit_criteria="""- [ ] Cross-cutting concerns identified
- [ ] Shared interfaces documented
- [ ] Integration points designed
- [ ] Conflicts resolved or noted""",
        continuation="IMPLEMENT",
        minimum_artifact="Named compositions or explicit skip",
    ),

    "IMPLEMENT": PhaseTemplate(
        name="IMPLEMENT",
        mission="Write the code. Execute the plan.",
        actions="""1. Follow wave sequence
2. Implement each component
3. Run tests as you go
4. Document deviations from plan
5. Update handles with new artifacts""",
        exit_criteria="""- [ ] All wave components implemented
- [ ] Tests passing locally
- [ ] No new blockers introduced
- [ ] Handles updated""",
        continuation="QA",
        minimum_artifact="Code changes or commit-ready diff",
    ),

    "QA": PhaseTemplate(
        name="QA",
        mission="Verify quality. Run linters, type checkers, static analysis.",
        actions="""1. Run mypy for type checking
2. Run ruff for linting
3. Check for security issues
4. Verify code style
5. Review for edge cases""",
        exit_criteria="""- [ ] mypy clean
- [ ] ruff clean
- [ ] No security issues
- [ ] Edge cases handled""",
        continuation="TEST",
        minimum_artifact="Checklist run with result",
    ),

    "TEST": PhaseTemplate(
        name="TEST",
        mission="Verify behavior. Write and run tests.",
        actions="""1. Write unit tests for new code
2. Add integration tests if needed
3. Verify law tests pass
4. Check edge cases
5. Run full test suite""",
        exit_criteria="""- [ ] Unit tests written
- [ ] All tests passing
- [ ] Law tests verified
- [ ] Coverage acceptable""",
        continuation="EDUCATE",
        minimum_artifact="Tests added/updated or explicit no-op with risk",
    ),

    "EDUCATE": PhaseTemplate(
        name="EDUCATE",
        mission="Document for users and maintainers.",
        actions="""1. Update README if needed
2. Add inline documentation
3. Create usage examples
4. Document gotchas
5. Update CHANGELOG""",
        exit_criteria="""- [ ] User documentation updated
- [ ] Maintainer notes added
- [ ] Examples provided""",
        continuation="MEASURE",
        minimum_artifact="User/maintainer note or explicit skip",
    ),

    "MEASURE": PhaseTemplate(
        name="MEASURE",
        mission="Define metrics. Set up measurement for success.",
        actions="""1. Identify key metrics
2. Add instrumentation if needed
3. Define success criteria
4. Set up monitoring
5. Document baseline""",
        exit_criteria="""- [ ] Metrics identified
- [ ] Instrumentation in place
- [ ] Success criteria defined""",
        continuation="REFLECT",
        minimum_artifact="Metric hook/plan or defer with owner/timebox",
    ),

    "REFLECT": PhaseTemplate(
        name="REFLECT",
        mission="Extract learnings. Seed the next cycle.",
        actions="""1. Review what worked well
2. Document what didn't
3. Extract reusable patterns
4. Identify follow-up work
5. Update entropy accounting""",
        exit_criteria="""- [ ] Learnings documented
- [ ] Patterns extracted
- [ ] Follow-up work identified
- [ ] Entropy accounted""",
        continuation="COMPLETE",
        minimum_artifact="Learnings + next-loop seeds",
    ),
}


def get_template(phase: str) -> PhaseTemplate:
    """Get template for a phase."""
    if phase not in PHASE_TEMPLATES:
        raise ValueError(f"Unknown phase: {phase}. Valid: {list(PHASE_TEMPLATES.keys())}")
    return PHASE_TEMPLATES[phase]


def get_compressed_template(family: str) -> PhaseTemplate:
    """Get compressed template for 3-phase mode."""
    phases = PHASE_FAMILIES.get(family, [])
    if not phases:
        raise ValueError(f"Unknown family: {family}. Valid: {list(PHASE_FAMILIES.keys())}")

    # Combine phase templates
    missions = [PHASE_TEMPLATES[p].mission for p in phases]
    actions = [f"### {p}\n{PHASE_TEMPLATES[p].actions}" for p in phases]
    criteria = [f"### {p}\n{PHASE_TEMPLATES[p].exit_criteria}" for p in phases]

    next_family = {"SENSE": "ACT", "ACT": "REFLECT", "REFLECT": "COMPLETE"}

    return PhaseTemplate(
        name=family,
        mission=" | ".join(missions),
        actions="\n\n".join(actions),
        exit_criteria="\n\n".join(criteria),
        continuation=next_family[family],
        minimum_artifact=", ".join(PHASE_TEMPLATES[p].minimum_artifact for p in phases),
    )
```

### 2.2 Template Renderer

```python
# impl/claude/protocols/nphase/template.py

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .templates import PHASE_TEMPLATES, PHASE_FAMILIES, get_template, get_compressed_template, PhaseTemplate

if TYPE_CHECKING:
    from .schema import ProjectDefinition


@dataclass
class NPhaseTemplate:
    """
    Template engine for N-Phase prompts.

    Renders a ProjectDefinition into a complete N-Phase Meta-Prompt.

    Laws:
    - Output is valid markdown
    - All project fields referenced
    - Phase sections match n_phases setting
    - Entropy allocations preserved
    """
    n_phases: int = 11

    def render(self, project: "ProjectDefinition") -> str:
        """Generate the N-Phase Meta-Prompt."""
        sections = [
            self._render_header(project),
            self._render_attach(),
            self._render_phase_selector(project),
            self._render_overview(project),
            self._render_shared_context(project),
            self._render_cumulative_state(project),
            self._render_phase_sections(project),
            self._render_accountability(project),
            self._render_footer(project),
        ]
        return "\n\n---\n\n".join(sections)

    def _render_header(self, project: "ProjectDefinition") -> str:
        return f"# {project.name}: N-Phase Meta-Prompt"

    def _render_attach(self) -> str:
        return "## ATTACH\n\n/hydrate"

    def _render_phase_selector(self, project: "ProjectDefinition") -> str:
        if project.n_phases == 3:
            phases = "|".join(PHASE_FAMILIES.keys())
        else:
            phases = "|".join(PHASE_TEMPLATES.keys())
        return f"## Phase Selector\n\n**Execute Phase**: `PHASE=[{phases}]`"

    def _render_overview(self, project: "ProjectDefinition") -> str:
        lines = ["## Project Overview", "", project.scope.goal, ""]

        if project.scope.parallel_tracks:
            lines.append("**Parallel Tracks**:")
            lines.append("")
            lines.append("| Track | Description |")
            lines.append("|-------|-------------|")
            for tid, desc in project.scope.parallel_tracks.items():
                lines.append(f"| {tid} | {desc} |")
            lines.append("")

        if project.decisions:
            lines.append("**Key Decisions**:")
            for dec in project.decisions:
                lines.append(f"- **{dec.id}**: {dec.choice} ({dec.rationale})")

        return "\n".join(lines)

    def _render_shared_context(self, project: "ProjectDefinition") -> str:
        lines = ["## Shared Context"]

        # File Map
        lines.append("\n### File Map\n")
        if project.file_map:
            lines.append("| Path | Lines | Purpose |")
            lines.append("|------|-------|---------|")
            for ref in project.file_map:
                lines.append(f"| `{ref.path}` | {ref.lines or '-'} | {ref.purpose or '-'} |")
        else:
            lines.append("*No file map yet (complete RESEARCH phase)*")

        # Invariants
        lines.append("\n### Invariants\n")
        if project.invariants:
            lines.append("| Name | Requirement | Verification |")
            lines.append("|------|-------------|--------------|")
            for inv in project.invariants:
                lines.append(f"| {inv.name} | {inv.requirement} | {inv.verification or '-'} |")
        else:
            lines.append("*No invariants yet (complete DEVELOP phase)*")

        # Blockers
        lines.append("\n### Blockers\n")
        if project.blockers:
            lines.append("| ID | Description | Evidence | Resolution | Status |")
            lines.append("|----|-------------|----------|------------|--------|")
            for b in project.blockers:
                lines.append(f"| {b.id} | {b.description} | {b.evidence} | {b.resolution or '-'} | {b.status} |")
        else:
            lines.append("*No blockers identified*")

        # Components
        lines.append("\n### Components\n")
        if project.components:
            lines.append("| ID | Name | Location | Effort | Dependencies |")
            lines.append("|----|------|----------|--------|--------------|")
            for c in project.components:
                deps = ", ".join(c.dependencies) if c.dependencies else "-"
                lines.append(f"| {c.id} | {c.name} | `{c.location}` | {c.effort.value} | {deps} |")
        else:
            lines.append("*No components yet (complete DEVELOP phase)*")

        # Waves
        lines.append("\n### Waves\n")
        if project.waves:
            lines.append("| Wave | Components | Strategy |")
            lines.append("|------|------------|----------|")
            for w in project.waves:
                comps = ", ".join(w.components)
                lines.append(f"| {w.name} | {comps} | {w.strategy or '-'} |")
        else:
            lines.append("*No waves yet (complete STRATEGIZE phase)*")

        # Checkpoints
        lines.append("\n### Checkpoints\n")
        if project.checkpoints:
            lines.append("| ID | Name | Criteria |")
            lines.append("|----|------|----------|")
            for cp in project.checkpoints:
                lines.append(f"| {cp.id} | {cp.name} | {cp.criteria} |")
        else:
            lines.append("*No checkpoints defined*")

        return "\n".join(lines)

    def _render_cumulative_state(self, project: "ProjectDefinition") -> str:
        lines = ["## Cumulative State"]

        # Handles (starts empty, updated by state updater)
        lines.append("\n### Handles Created\n")
        lines.append("| Handle | Location | Phase |")
        lines.append("|--------|----------|-------|")
        lines.append("| *none yet* | - | - |")

        # Entropy
        lines.append("\n### Entropy Budget\n")
        if project.entropy:
            lines.append(f"**Total**: {project.entropy.total}")
            lines.append(f"**Remaining**: {project.entropy.remaining():.3f}")
            lines.append("")
            lines.append("| Phase | Allocated | Spent |")
            lines.append("|-------|-----------|-------|")
            for phase in PHASE_TEMPLATES:
                alloc = project.entropy.allocation.get(phase, 0)
                spent = project.entropy.spent.get(phase, 0)
                lines.append(f"| {phase} | {alloc:.3f} | {spent:.3f} |")
        else:
            lines.append("*No entropy budget defined*")

        return "\n".join(lines)

    def _render_phase_sections(self, project: "ProjectDefinition") -> str:
        lines = []

        if project.n_phases == 3:
            phases = list(PHASE_FAMILIES.keys())
            get_tmpl = get_compressed_template
        else:
            phases = list(PHASE_TEMPLATES.keys())
            get_tmpl = get_template

        for phase in phases:
            tmpl = get_tmpl(phase)
            override = project.phase_overrides.get(phase)

            lines.append(f"## Phase: {phase}")
            lines.append(f"<details>")
            lines.append(f"<summary>Expand if PHASE={phase}</summary>")
            lines.append("")
            lines.append(f"### Mission")
            lines.append(tmpl.mission)
            lines.append("")
            lines.append(f"### Actions")
            lines.append(tmpl.actions)

            if override and override.investigations:
                lines.append("")
                lines.append("### Phase-Specific Investigations")
                for inv in override.investigations:
                    lines.append(f"- {inv}")

            lines.append("")
            lines.append(f"### Exit Criteria")
            lines.append(tmpl.exit_criteria)

            if override and override.exit_criteria:
                lines.append("")
                lines.append("### Additional Exit Criteria")
                for crit in override.exit_criteria:
                    lines.append(f"- [ ] {crit}")

            lines.append("")
            lines.append(f"### Minimum Artifact")
            lines.append(tmpl.minimum_artifact)
            lines.append("")
            lines.append(f"### Continuation")
            if tmpl.continuation == "COMPLETE":
                lines.append("`⟂[COMPLETE]` — Work done. Tithe remaining entropy.")
            else:
                lines.append(f"On completion: `⟿[{tmpl.continuation}]`")
            lines.append("")
            lines.append("</details>")
            lines.append("")

        return "\n".join(lines)

    def _render_accountability(self, project: "ProjectDefinition") -> str:
        lines = ["## Phase Accountability", ""]
        lines.append("| Phase | Status | Artifact |")
        lines.append("|-------|--------|----------|")

        phases = list(PHASE_FAMILIES.keys()) if project.n_phases == 3 else list(PHASE_TEMPLATES.keys())

        for phase in phases:
            status = project.phase_ledger.get(phase, "pending")
            if hasattr(status, "value"):
                status = status.value
            lines.append(f"| {phase} | {status} | - |")

        return "\n".join(lines)

    def _render_footer(self, project: "ProjectDefinition") -> str:
        return f'*"The form that generates forms."*'
```

---

## 3. Compiler Architecture

### 3.1 Prompt Compiler

```python
# impl/claude/protocols/nphase/compiler.py

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from .schema import ProjectDefinition, ValidationResult
from .template import NPhaseTemplate

if TYPE_CHECKING:
    pass


@dataclass
class NPhasePrompt:
    """Compiled N-Phase prompt."""
    content: str
    project: ProjectDefinition

    def __str__(self) -> str:
        return self.content

    def save(self, path: str | Path) -> None:
        """Save prompt to file."""
        Path(path).write_text(self.content)


class NPhasePromptCompiler:
    """
    The Meta-Meta-Prompt: generates N-Phase prompts from project definitions.

    AGENTESE handle: concept.nphase.compile

    Laws:
    - compile(parse(yaml)) produces valid N-Phase prompt
    - compile is idempotent on stable projects
    - compile preserves all project information (no loss)
    """

    def compile(self, definition: ProjectDefinition) -> NPhasePrompt:
        """
        Compile a project definition into an N-Phase Meta-Prompt.

        Steps:
        1. Validate definition
        2. Load phase templates
        3. Render shared context
        4. Render each phase section
        5. Assemble final prompt

        Raises:
            ValueError: If definition is invalid
        """
        # Step 1: Validate
        result = definition.validate()
        result.raise_if_invalid()

        # Step 2-5: Render via template
        template = NPhaseTemplate(n_phases=definition.n_phases)
        content = template.render(definition)

        return NPhasePrompt(content=content, project=definition)

    def compile_from_yaml(self, yaml_content: str) -> NPhasePrompt:
        """Convenience: parse YAML and compile."""
        definition = ProjectDefinition.from_yaml(yaml_content)
        return self.compile(definition)

    def compile_from_yaml_file(self, yaml_path: str | Path) -> NPhasePrompt:
        """Convenience: load YAML file and compile."""
        definition = ProjectDefinition.from_yaml_file(yaml_path)
        return self.compile(definition)

    def compile_from_plan(self, plan_path: str | Path) -> NPhasePrompt:
        """
        Bootstrap compilation from existing plan file.

        Useful for incremental adoption: existing plans can be
        converted to compiled prompts.
        """
        definition = ProjectDefinition.from_plan_header(plan_path)
        return self.compile(definition)


# Singleton for convenience
compiler = NPhasePromptCompiler()
```

### 3.2 State Updater

```python
# impl/claude/protocols/nphase/state.py

from __future__ import annotations
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any
import json

from .schema import (
    ProjectDefinition,
    PhaseStatus,
    EntropyBudget,
    FileRef,
    Blocker,
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
    blocker_resolutions: dict[str, str] = None  # blocker_id -> resolution

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "phase": self.phase,
            "handles": [{"name": h.name, "location": h.location, "phase": h.phase} for h in self.handles],
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
            "handles": [{"name": h.name, "location": h.location, "phase": h.phase} for h in self.handles],
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
            phase_outputs=[PhaseOutput.from_dict(o) for o in data.get("phase_outputs", [])],
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
        new_entropy_spent[output.phase] = new_entropy_spent.get(output.phase, 0) + output.entropy_spent
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
            new_entropy_spent_proj[output.phase] = new_entropy_spent_proj.get(output.phase, 0) + output.entropy_spent
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
                    new_blockers.append(Blocker(
                        id=b.id,
                        description=b.description,
                        evidence=b.evidence,
                        resolution=output.blocker_resolutions[b.id],
                        status="resolved",
                    ))
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
```

---

## 4. AGENTESE Integration

### 4.1 Concept Context Extension

```python
# Addition to impl/claude/protocols/agentese/contexts/concept.py
# After line 738 (in resolve() method)

# Design Decision (B3): Add nphase handling as special case in
# ConceptContextResolver rather than separate resolver.

class NPhaseConceptNode(LogosNode):
    """
    Node for concept.nphase.* paths.

    Handles:
    - concept.nphase.compile — Compile ProjectDefinition to prompt
    - concept.nphase.validate — Validate ProjectDefinition
    - concept.nphase.template — Get phase template
    - concept.nphase.schema — Get schema documentation
    """

    def __init__(self, holon: str):
        self.holon = holon  # "compile", "validate", "template", "schema"

    async def resolve_aspect(
        self,
        aspect: str,
        umwelt: Umwelt,
        **kwargs: Any,
    ) -> AspectResult:
        from ..nphase.compiler import compiler
        from ..nphase.schema import ProjectDefinition
        from ..nphase.templates import PHASE_TEMPLATES, get_template

        if self.holon == "compile":
            if aspect == "manifest":
                # Expects "definition" kwarg with ProjectDefinition or dict
                definition = kwargs.get("definition")
                if isinstance(definition, dict):
                    definition = ProjectDefinition.from_dict(definition)
                prompt = compiler.compile(definition)
                return AspectResult(value=str(prompt))
            elif aspect == "define":
                # Return schema for creating new definition
                return AspectResult(value=ProjectDefinition.__doc__)

        elif self.holon == "validate":
            if aspect == "manifest":
                definition = kwargs.get("definition")
                if isinstance(definition, dict):
                    definition = ProjectDefinition.from_dict(definition)
                result = definition.validate()
                return AspectResult(value={
                    "is_valid": result.is_valid,
                    "errors": result.errors,
                    "warnings": result.warnings,
                })

        elif self.holon == "template":
            if aspect == "manifest":
                phase = kwargs.get("phase", "PLAN")
                tmpl = get_template(phase)
                return AspectResult(value={
                    "name": tmpl.name,
                    "mission": tmpl.mission,
                    "actions": tmpl.actions,
                    "exit_criteria": tmpl.exit_criteria,
                    "minimum_artifact": tmpl.minimum_artifact,
                })

        elif self.holon == "schema":
            if aspect == "manifest":
                # Return schema documentation
                return AspectResult(value={
                    "phases": list(PHASE_TEMPLATES.keys()),
                    "classification": ["crown_jewel", "standard", "quick_win"],
                    "effort": ["XS", "S", "M", "L", "XL"],
                })

        return AspectResult(value=None, error=f"Unknown aspect: {aspect}")


# In ConceptContextResolver.resolve():
def resolve(self, path: str, umwelt: Umwelt) -> LogosNode | None:
    parts = path.split(".")
    if len(parts) < 2:
        return None

    context, holon = parts[0], parts[1]

    if context != "concept":
        return None

    # NEW: Handle nphase special case
    if holon == "nphase" and len(parts) >= 3:
        subholon = parts[2]  # compile, validate, template, schema
        return NPhaseConceptNode(subholon)

    # ... rest of existing resolution logic
```

---

## 5. CLI Handler

```python
# impl/claude/protocols/cli/handlers/nphase.py

"""
CLI handler for N-Phase Prompt Compiler.

Design Decision (B4): Follow existing handler pattern from handlers/forest.py.

Usage:
    kg nphase compile <definition.yaml>       # Compile to stdout
    kg nphase compile <definition.yaml> -o <output.md>  # Compile to file
    kg nphase validate <definition.yaml>      # Validate only
    kg nphase bootstrap <plan.md>             # Bootstrap from existing plan
"""

from pathlib import Path
from typing import Optional

import typer

from ..nphase.compiler import compiler
from ..nphase.schema import ProjectDefinition

app = typer.Typer(name="nphase", help="N-Phase Prompt Compiler")


@app.command("compile")
def compile_cmd(
    definition_path: Path = typer.Argument(..., help="Path to ProjectDefinition YAML"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output file path"),
    format: str = typer.Option("markdown", "-f", "--format", help="Output format (markdown)"),
) -> None:
    """Compile a ProjectDefinition to N-Phase Meta-Prompt."""
    prompt = compiler.compile_from_yaml_file(definition_path)

    if output:
        prompt.save(output)
        typer.echo(f"Compiled to {output}")
    else:
        typer.echo(str(prompt))


@app.command("validate")
def validate_cmd(
    definition_path: Path = typer.Argument(..., help="Path to ProjectDefinition YAML"),
) -> None:
    """Validate a ProjectDefinition without compiling."""
    definition = ProjectDefinition.from_yaml_file(definition_path)
    result = definition.validate()

    if result.is_valid:
        typer.echo("✓ Valid ProjectDefinition")
        if result.warnings:
            typer.echo("\nWarnings:")
            for w in result.warnings:
                typer.echo(f"  ⚠ {w}")
    else:
        typer.echo("✗ Invalid ProjectDefinition")
        typer.echo("\nErrors:")
        for e in result.errors:
            typer.echo(f"  ✗ {e}")
        raise typer.Exit(1)


@app.command("bootstrap")
def bootstrap_cmd(
    plan_path: Path = typer.Argument(..., help="Path to existing plan file"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output file path"),
) -> None:
    """Bootstrap ProjectDefinition from existing plan file header."""
    prompt = compiler.compile_from_plan(plan_path)

    if output:
        prompt.save(output)
        typer.echo(f"Bootstrapped and compiled to {output}")
    else:
        typer.echo(str(prompt))


@app.command("template")
def template_cmd(
    phase: str = typer.Argument(..., help="Phase name (PLAN, RESEARCH, etc.)"),
) -> None:
    """Show template for a specific phase."""
    from ..nphase.templates import get_template

    tmpl = get_template(phase.upper())
    typer.echo(f"# {tmpl.name}\n")
    typer.echo(f"**Mission**: {tmpl.mission}\n")
    typer.echo(f"**Actions**:\n{tmpl.actions}\n")
    typer.echo(f"**Exit Criteria**:\n{tmpl.exit_criteria}\n")
    typer.echo(f"**Minimum Artifact**: {tmpl.minimum_artifact}\n")
    typer.echo(f"**Continuation**: → {tmpl.continuation}")
```

---

## 6. Blocker Resolutions

| ID | Blocker | Resolution | Implementation |
|----|---------|------------|----------------|
| B1 | No dedicated N-Phase YAML schema | **Formalized in `ProjectDefinition`** | `schema.py` with frozen dataclasses, `to_dict()`/`from_dict()`, validation |
| B2 | Phase templates in markdown | **Hardcoded as Python strings** | `templates/__init__.py` with `PhaseTemplate` NamedTuple |
| B3 | `concept.nphase.*` paths don't exist | **Special case in resolver** | `NPhaseConceptNode` class in `concept.py` |
| B4 | No CLI handler pattern | **Follow `handlers/forest.py`** | `handlers/nphase.py` with Typer commands |
| B5 | Entropy tracking not enforced | **Validation in `EntropyBudget`** | `validate()` method checks sum and overspend |

---

## 7. Test Contracts

### 7.1 Law: Schema Validation

```python
# impl/claude/protocols/nphase/_tests/test_schema.py

def test_component_ids_unique():
    """Law: Component IDs must be unique."""
    with pytest.raises(ValueError, match="Duplicate component IDs"):
        ProjectDefinition(
            name="test",
            classification=Classification.STANDARD,
            scope=ProjectScope(goal="test"),
            components=(
                Component(id="C1", name="foo", location="x.py"),
                Component(id="C1", name="bar", location="y.py"),  # Duplicate!
            ),
        ).validate().raise_if_invalid()


def test_wave_references_valid_components():
    """Law: Wave components must reference valid component IDs."""
    result = ProjectDefinition(
        name="test",
        classification=Classification.STANDARD,
        scope=ProjectScope(goal="test"),
        components=(Component(id="C1", name="foo", location="x.py"),),
        waves=(Wave(name="Wave 1", components=("C1", "C99")),),  # C99 invalid
    ).validate()

    assert not result.is_valid
    assert any("C99" in e for e in result.errors)


def test_entropy_conservation():
    """Law: Entropy allocation must equal total."""
    result = ProjectDefinition(
        name="test",
        classification=Classification.STANDARD,
        scope=ProjectScope(goal="test"),
        entropy=EntropyBudget(
            total=0.75,
            allocation={"PLAN": 0.10, "RESEARCH": 0.10},  # Sum = 0.20 != 0.75
        ),
    ).validate()

    assert not result.is_valid
    assert any("Allocation" in e for e in result.errors)
```

### 7.2 Law: Compile Identity

```python
# impl/claude/protocols/nphase/_tests/test_compiler.py

def test_compile_preserves_all_fields(sample_project: ProjectDefinition):
    """Law: compile(project) contains all project information."""
    prompt = compiler.compile(sample_project)
    content = str(prompt)

    # All file map entries present
    for file in sample_project.file_map:
        assert file.path in content

    # All invariants present
    for inv in sample_project.invariants:
        assert inv.name in content

    # All components present
    for comp in sample_project.components:
        assert comp.id in content


def test_compile_idempotent():
    """Law: Compiling same project twice yields same result."""
    project = ProjectDefinition(
        name="test",
        classification=Classification.STANDARD,
        scope=ProjectScope(goal="test goal"),
    )

    prompt1 = str(compiler.compile(project))
    prompt2 = str(compiler.compile(project))

    assert prompt1 == prompt2
```

### 7.3 Law: State Monotonicity

```python
# impl/claude/protocols/nphase/_tests/test_state.py

def test_state_update_monotonic():
    """Law: State only grows, never shrinks."""
    project = ProjectDefinition(
        name="test",
        classification=Classification.STANDARD,
        scope=ProjectScope(goal="test"),
        entropy=EntropyBudget(total=0.75, allocation={"PLAN": 0.05}),
    )
    state = CumulativeState.empty()

    # First update
    output1 = PhaseOutput(
        phase="PLAN",
        handles=(Handle(name="scope.md", location="plans/", phase="PLAN"),),
        entropy_spent=0.03,
    )
    project1, state1 = state_updater.update(project, state, output1)

    # Second update
    output2 = PhaseOutput(
        phase="RESEARCH",
        handles=(Handle(name="file_map.md", location="plans/", phase="RESEARCH"),),
        entropy_spent=0.04,
    )
    project2, state2 = state_updater.update(project1, state1, output2)

    # All original handles preserved
    assert len(state2.handles) == 2
    assert state2.handles[0].name == "scope.md"
    assert state2.handles[1].name == "file_map.md"

    # Entropy accumulates
    assert state2.entropy_spent["PLAN"] == 0.03
    assert state2.entropy_spent["RESEARCH"] == 0.04
```

---

## 8. API Contracts Summary

| Component | Method | Input | Output | Laws |
|-----------|--------|-------|--------|------|
| `ProjectDefinition` | `validate()` | self | `ValidationResult` | IDs unique, refs valid, entropy conserved |
| `ProjectDefinition` | `from_yaml()` | `str` | `ProjectDefinition` | Inverse of `to_yaml()` |
| `ProjectDefinition` | `from_plan_header()` | `Path` | `ProjectDefinition` | Bootstraps from existing plan |
| `NPhaseTemplate` | `render()` | `ProjectDefinition` | `str` | All fields included, valid markdown |
| `NPhasePromptCompiler` | `compile()` | `ProjectDefinition` | `NPhasePrompt` | Idempotent, preserves all info |
| `NPhaseStateUpdater` | `update()` | project, state, output | (project', state') | Monotonic growth, entropy correct |
| `NPhaseConceptNode` | `resolve_aspect()` | aspect, umwelt | `AspectResult` | Consistent with other concept nodes |

---

## 9. Exit Criteria Verification

- [x] Schema defined (`ProjectDefinition` with all nested types)
- [x] Templates specified (hardcoded `PhaseTemplate` per phase)
- [x] Compiler architecture defined (`NPhasePromptCompiler`, `NPhaseTemplate`)
- [x] State management specified (`NPhaseStateUpdater`, `CumulativeState`)
- [x] AGENTESE integration designed (`NPhaseConceptNode`)
- [x] CLI handler specified (`handlers/nphase.py`)
- [x] All blockers (B1-B5) resolved with concrete decisions
- [x] Test contracts with law assertions
- [x] API contracts documented
- [x] Entropy spent: 0.08 ≤ 0.10

---

## 10. Continuation

```markdown
⟿[STRATEGIZE]
/hydrate

handles:
  research=plans/meta/_research/nphase-prompt-compiler-research.md;
  develop=plans/meta/_research/nphase-prompt-compiler-develop.md;
  schema=schema.py; templates=templates/__init__.py;
  compiler=compiler.py; state=state.py; cli=handlers/nphase.py

ledger: {PLAN: touched, RESEARCH: touched, DEVELOP: touched}
entropy: spent=0.14, remaining=0.61

mission: Sequence the implementation. Define waves, checkpoints,
         and execution order. Identify parallelization opportunities.

exit: Waves defined; checkpoints specified; critical path identified.
continuation: ⟿[CROSS-SYNERGIZE]
```

---

*"Contracts are promises that code can keep."*

---

## Addendum 2026-02-11 — Game-Engine + Shader Reframing Plan

### Intent
- Recast the N-Phase Prompt Compiler as a game engine: the phase graph is the render pipeline, AGENTESE contexts are ECS-style entities, skills are systems, handles/affordances are components, and the auto-inducer is the render loop.
- Treat personality/perspective as shaders applied per pass; category-theoretic laws and the dialectic are the invariants that allow hot-swapping shaders without tearing the frame.

### External anchors (internet)
- Game engine: software framework with modular subsystems and toolchain (Wikipedia summary, 2025-11-22).
- Rendering pipeline: staged transforms from model to image; passes can be chained (Wikipedia summary, 2025-12-08).
- Shader: programmable stage acting on vertices/fragments; programmable hot-swap (Wikipedia summary, 2025-12-02).
- ECS: entities (ids), components (data), systems (behavior) for decoupled composition (Wikipedia summary, 2025-11-16).

### Mapping (engine → n-phase)
- Render loop = SENSE → ACT → REFLECT; multipass = full 11-phase crown-jewel loop.
- Scene graph = phase ledger and handles; materials = `spec/principles.md` bindings; assets = memory + world/self/concept handles.
- Vertex/geometry shaders = PLAN/RESEARCH/DEVELOP shaping structure; fragment shaders = IMPLEMENT/QA/TEST voice/detail; post-process = MEASURE/REFLECT tone + metrics.
- ECS triad: entities = contexts (`world.*`, `self.*`, `concept.*`, `void.*`, `time.*`); components = affordances/ledger entries; systems = skills in `docs/skills/n-phase-cycle`.
- GPU budget = entropy budget; frame time = attention budget.

### Chromatic Engine (color-first reframing)
- Polyfunctor graph = scene: agents/affordances are nodes/edges; composition order = traversal order; colors encode perspectives.
- Color model: hue = worldview lens, saturation = assertiveness, value = risk appetite; opacity = willingness to overwrite defaults; blend modes = dialectic interaction (multiply for critique, screen for amplification).
- Chromatic passes: PLAN/RESEARCH/DEVELOP as gamut-mapping (normalize intents into engine space); IMPLEMENT/QA/TEST as fragment shading with chroma-aware guards; MEASURE/REFLECT as tone-mapping/post-exposure.
- Chaos/complexity dial: noise textures = entropy sip; LOD = ceremony level (3-phase vs 11-phase); particle systems = branch proliferation from `branching-protocol.md`.
- Law hooks: colors must compose naturally (no gamut clipping of handles); blend order must preserve ledger invariants; chroma budget tracks entropy budget to prevent “overexposed” reasoning.

### Laws and contracts to assert
- Pass associativity: `(PhaseA >> PhaseB) >> PhaseC == PhaseA >> (PhaseB >> PhaseC)` to preserve category-theoretic coherence.
- Identity pass: minimal render (3-phase) must leave semantics unchanged when inserted between phases.
- Shader hot-swap law: swapping personality shaders must preserve invariants (handles, ledger, safety) and naturality conditions (no illegal side effects across contexts).
- Entropy-as-GPU-budget: each phase declares spend; exceeding budget triggers `⟂[ENTROPY_DEPLETED]`.
- Dialectic multipass: thesis/antithesis render passes converge in REFLECT; oppositional passes must be composable (no Z-fighting of intents).

### Artifacts to produce in this note (next edit)
- A concise table: engine concept ↔ n-phase element ↔ existing analogy (category theory/dialectic).
- Shader registry stub: persona/perspective profiles with allowed uniforms (voice, tone, risk appetite).
- Material library sketch: binding principles to prompts as materials; show a sample binding to `spec/principles.md`.
- Worked example: PLAN (vertex) → RESEARCH (geometry) → IMPLEMENT (fragment) → REFLECT (post-process) for a single feature, with shader swap mid-pipeline.

### Sequencing (for follow-up edit)
1) Insert mapping table and laws near the schema/contracts section; keep ledger untouched.
2) Add shader registry/material library stubs as future work branches with handles.
3) Add mini example and continuation hook to IMPLEMENT/QA if further code/doc changes are needed.

### Branch candidates
- Shader Registry: catalog of personalities/perspectives (pass uniforms) keyed by context.
- Material Library: principle-bound prompt materials for reuse across phases.
- Render Loop Metrics: frame-time/entropy reporting per phase to feed `process-metrics.md`.
