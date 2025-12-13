"""
I-gent Export: Markdown serialization for vim/paper portability.

Every I-gent view has a canonical markdown representation.
This preserves the "paper trail" and enables:
- Vim editing (markdown headers for navigation)
- Mermaid diagrams for composition graphs
- Printing to actual paper
- Git versioning of garden state
"""

from datetime import datetime
from typing import List, Optional

from .core_types import (
    AgentState,
    GardenState,
    LibraryState,
    MarginNote,
)


class MarkdownExporter:
    """
    Exports I-gent views to markdown format.

    Example output:
        # robin

        > "A B-gent researching protein folding patterns."

        ## State
        - **phase**: ● active
        - **time**: 00:14:32
        - **joy**: 7/10
        - **ethics**: 9/10

        ## Composition
        ```mermaid
        graph TD
            robin((● robin)) --> analyze((◐ analyze))
            robin --> summarize((● summarize))
        ```

        ## Margin Notes
        - 00:12:00 — [system] phase transition: dormant → waking
        - 00:14:00 — [ai] stable now; proceeding
    """

    def __init__(self, include_mermaid: bool = True):
        """
        Initialize exporter.

        Args:
            include_mermaid: Whether to include Mermaid diagrams
        """
        self.include_mermaid = include_mermaid

    def export_agent(self, state: AgentState) -> str:
        """Export an agent state to markdown."""
        lines = []

        # Title
        lines.append(f"# {state.agent_id}")
        lines.append("")

        # Epigraph
        if state.epigraph:
            lines.append(f'> "{state.epigraph}"')
            lines.append("")

        # State section
        lines.append("## State")
        lines.append(f"- **phase**: {state.phase.symbol} {state.phase.value}")
        lines.append(f"- **time**: {state.elapsed_str}")

        if state.joy is not None:
            joy_val = int(state.joy * 10)
            lines.append(f"- **joy**: {joy_val}/10")

        if state.ethics is not None:
            eth_val = int(state.ethics * 10)
            lines.append(f"- **ethics**: {eth_val}/10")

        lines.append("")

        # Composition section (if has relationships)
        if state.composes_with or state.composed_by:
            lines.append("## Composition")

            if self.include_mermaid:
                lines.append("```mermaid")
                lines.append("graph TD")
                lines.append(
                    f"    {state.agent_id}(({state.phase.symbol} {state.agent_id}))"
                )

                for target in state.composes_with:
                    lines.append(f"    {state.agent_id} --> {target}")

                for source in state.composed_by:
                    lines.append(f"    {source} --> {state.agent_id}")

                lines.append("```")
            else:
                # Plain text fallback
                if state.composes_with:
                    lines.append(
                        f"- **composes with**: {', '.join(state.composes_with)}"
                    )
                if state.composed_by:
                    lines.append(f"- **composed by**: {', '.join(state.composed_by)}")

            lines.append("")

        # Margin notes section
        if state.margin_notes:
            lines.append("## Margin Notes")
            for note in state.margin_notes:
                lines.append(f"- {note.render()}")
            lines.append("")

        # Actions (as task list)
        lines.append("## Actions")
        lines.append("- [ ] observe")
        lines.append("- [ ] invoke")
        lines.append("- [ ] compose")
        lines.append("- [ ] rest")

        return "\n".join(lines)

    def export_garden(self, garden: GardenState) -> str:
        """Export a garden state to markdown."""
        lines = []

        # Title with time
        lines.append(f"# {garden.name}")
        lines.append("")
        lines.append(f"**Session time**: {garden.elapsed_str}")
        lines.append("")

        # Summary section
        lines.append("## Summary")
        lines.append(f"- **agents**: {len(garden.agents)}")
        lines.append(f"- **glyph summary**: {garden.glyph_summary()}")
        if garden.focus:
            lines.append(f"- **focus**: {garden.focus}")
        if garden.health is not None:
            lines.append(f"- **health**: {int(garden.health * 100)}%")
        lines.append("")

        # Composition graph
        if self.include_mermaid and garden.agents:
            lines.append("## Composition Graph")
            lines.append("```mermaid")
            lines.append("graph TD")

            # Add all agents as nodes
            for agent_id, agent in garden.agents.items():
                lines.append(f"    {agent_id}(({agent.phase.symbol} {agent_id}))")

            # Add edges
            for agent_id, agent in garden.agents.items():
                for target in agent.composes_with:
                    if target in garden.agents:
                        lines.append(f"    {agent_id} --> {target}")

            lines.append("```")
            lines.append("")

        # Agent summaries
        lines.append("## Agents")
        for agent_id in sorted(garden.agents.keys()):
            agent = garden.agents[agent_id]
            lines.append(f"### {agent.glyph.render()}")
            lines.append(f"- **time**: {agent.elapsed_str}")
            if agent.joy is not None:
                lines.append(f"- **joy**: {int(agent.joy * 10)}/10")
            if agent.ethics is not None:
                lines.append(f"- **ethics**: {int(agent.ethics * 10)}/10")
            if agent.epigraph:
                lines.append(f"- _{agent.epigraph}_")
            lines.append("")

        # Garden-wide margin notes
        if garden.margin_notes:
            lines.append("## Garden Notes")
            for note in garden.margin_notes:
                lines.append(f"- {note.render()}")
            lines.append("")

        return "\n".join(lines)

    def export_library(self, library: LibraryState) -> str:
        """Export a library state to markdown."""
        lines = []

        # Title
        lines.append(f"# {library.name}")
        lines.append("")

        # Calculate elapsed
        elapsed = library.current_time - library.system_start
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        lines.append(f"**System time**: {time_str}")
        lines.append(f"**Orchestration**: {library.orchestration_status}")
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append(f"- **total gardens**: {len(library.gardens)}")
        lines.append(f"- **total agents**: {library.total_agents}")
        if library.focus:
            lines.append(f"- **focus**: {library.focus}")
        lines.append("")

        # Garden summaries
        lines.append("## Gardens")
        for garden_name in sorted(library.gardens.keys()):
            garden = library.gardens[garden_name]
            health_str = f"{int(garden.health * 100)}%" if garden.health else "N/A"
            lines.append(f"### {garden_name}")
            lines.append(f"- **agents**: {len(garden.agents)}")
            lines.append(f"- **glyphs**: {garden.glyph_summary()}")
            lines.append(f"- **health**: {health_str}")
            lines.append("")

        return "\n".join(lines)

    def export_margin_notes(
        self, notes: List[MarginNote], title: str = "Margin Notes"
    ) -> str:
        """Export margin notes as a standalone document."""
        lines = []

        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"_Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
        lines.append("")

        if not notes:
            lines.append("_No notes recorded._")
            return "\n".join(lines)

        # Group by agent
        agent_notes: dict[Optional[str], List[MarginNote]] = {}
        for note in notes:
            key = note.agent_id
            if key not in agent_notes:
                agent_notes[key] = []
            agent_notes[key].append(note)

        # Garden-wide notes first
        if None in agent_notes:
            lines.append("## Garden-wide")
            for note in agent_notes[None]:
                lines.append(f"- {note.render()}")
            lines.append("")

        # Agent-specific notes
        for agent_id in sorted(k for k in agent_notes.keys() if k is not None):
            lines.append(f"## {agent_id}")
            for note in agent_notes[agent_id]:
                lines.append(f"- {note.render(show_agent=False)}")
            lines.append("")

        return "\n".join(lines)
