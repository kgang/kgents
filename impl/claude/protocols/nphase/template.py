"""
N-Phase Template Renderer.

Renders a ProjectDefinition into a complete N-Phase Meta-Prompt.

Laws:
- Output is valid markdown
- All project fields referenced
- Phase sections match n_phases setting
- Entropy allocations preserved
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .templates import (
    PHASE_FAMILIES,
    PHASE_TEMPLATES,
    get_compressed_template,
    get_template,
)

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

    def render(self, project: ProjectDefinition) -> str:
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

    def _render_header(self, project: ProjectDefinition) -> str:
        return f"# {project.name}: N-Phase Meta-Prompt"

    def _render_attach(self) -> str:
        return "## ATTACH\n\n/hydrate"

    def _render_phase_selector(self, project: ProjectDefinition) -> str:
        if project.n_phases == 3:
            phases = "|".join(PHASE_FAMILIES.keys())
        else:
            phases = "|".join(PHASE_TEMPLATES.keys())
        return f"## Phase Selector\n\n**Execute Phase**: `PHASE=[{phases}]`"

    def _render_overview(self, project: ProjectDefinition) -> str:
        lines = ["## Project Overview", "", project.scope.goal, ""]

        if project.scope.non_goals:
            lines.append("**Non-Goals**:")
            for ng in project.scope.non_goals:
                lines.append(f"- {ng}")
            lines.append("")

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

    def _render_shared_context(self, project: ProjectDefinition) -> str:
        lines = ["## Shared Context"]

        # File Map
        lines.append("\n### File Map\n")
        if project.file_map:
            lines.append("| Path | Lines | Purpose |")
            lines.append("|------|-------|---------|")
            for ref in project.file_map:
                lines.append(
                    f"| `{ref.path}` | {ref.lines or '-'} | {ref.purpose or '-'} |"
                )
        else:
            lines.append("*No file map yet (complete RESEARCH phase)*")

        # Invariants
        lines.append("\n### Invariants\n")
        if project.invariants:
            lines.append("| Name | Requirement | Verification |")
            lines.append("|------|-------------|--------------|")
            for inv in project.invariants:
                lines.append(
                    f"| {inv.name} | {inv.requirement} | {inv.verification or '-'} |"
                )
        else:
            lines.append("*No invariants yet (complete DEVELOP phase)*")

        # Blockers
        lines.append("\n### Blockers\n")
        if project.blockers:
            lines.append("| ID | Description | Evidence | Resolution | Status |")
            lines.append("|----|-------------|----------|------------|--------|")
            for b in project.blockers:
                lines.append(
                    f"| {b.id} | {b.description} | {b.evidence} | "
                    f"{b.resolution or '-'} | {b.status} |"
                )
        else:
            lines.append("*No blockers identified*")

        # Components
        lines.append("\n### Components\n")
        if project.components:
            lines.append("| ID | Name | Location | Effort | Dependencies |")
            lines.append("|----|------|----------|--------|--------------|")
            for c in project.components:
                deps = ", ".join(c.dependencies) if c.dependencies else "-"
                lines.append(
                    f"| {c.id} | {c.name} | `{c.location}` | {c.effort.value} | {deps} |"
                )
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

    def _render_cumulative_state(self, project: ProjectDefinition) -> str:
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

    def _render_phase_sections(self, project: ProjectDefinition) -> str:
        from typing import Callable

        from .templates import PhaseTemplate

        lines: list[str] = []

        get_tmpl: Callable[[str], PhaseTemplate]
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
            lines.append("<details>")
            lines.append(f"<summary>Expand if PHASE={phase}</summary>")
            lines.append("")
            lines.append("### Mission")
            lines.append(tmpl.mission)
            lines.append("")
            lines.append("### Actions")
            lines.append(tmpl.actions)

            if override and override.investigations:
                lines.append("")
                lines.append("### Phase-Specific Investigations")
                for inv in override.investigations:
                    lines.append(f"- {inv}")

            lines.append("")
            lines.append("### Exit Criteria")
            lines.append(tmpl.exit_criteria)

            if override and override.exit_criteria:
                lines.append("")
                lines.append("### Additional Exit Criteria")
                for crit in override.exit_criteria:
                    lines.append(f"- [ ] {crit}")

            lines.append("")
            lines.append("### Minimum Artifact")
            lines.append(tmpl.minimum_artifact)
            lines.append("")
            lines.append("### Continuation")
            if tmpl.continuation == "COMPLETE":
                lines.append("`[COMPLETE]` - Work done. Tithe remaining entropy.")
            else:
                lines.append(f"On completion: `[{tmpl.continuation}]`")
            lines.append("")
            lines.append("</details>")
            lines.append("")

        return "\n".join(lines)

    def _render_accountability(self, project: ProjectDefinition) -> str:
        lines = ["## Phase Accountability", ""]
        lines.append("| Phase | Status | Artifact |")
        lines.append("|-------|--------|----------|")

        phases = (
            list(PHASE_FAMILIES.keys())
            if project.n_phases == 3
            else list(PHASE_TEMPLATES.keys())
        )

        for phase in phases:
            status = project.phase_ledger.get(phase, "pending")
            if hasattr(status, "value"):
                status = status.value
            lines.append(f"| {phase} | {status} | - |")

        return "\n".join(lines)

    def _render_footer(self, project: ProjectDefinition) -> str:
        return '*"The form that generates forms."*'
