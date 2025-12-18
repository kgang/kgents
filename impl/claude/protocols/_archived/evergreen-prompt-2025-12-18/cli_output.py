"""
Rich Output Formatting for Evergreen Prompt System CLI.

Wave 6 of the Evergreen Prompt System.

Provides beautiful, informative CLI output using Rich library:
- Compilation results with syntax highlighting
- Reasoning trace trees
- Habit influence tables
- History timelines
- Diff visualization

See: plans/_continuations/evergreen-wave6-living-cli-continuation.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.text import Text
    from rich.tree import Tree

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

if TYPE_CHECKING:
    from .compiler import CompiledPrompt
    from .habits.policy import PolicyVector
    from .rollback import CheckpointSummary


@dataclass
class PromptOutputFormatter:
    """
    Format prompt compilation output for CLI display.

    Uses Rich library for beautiful terminal output.
    Falls back to plain text if Rich is not available.
    """

    console: Any = None
    use_colors: bool = True

    def __post_init__(self) -> None:
        """Initialize console if not provided."""
        if self.console is None and HAS_RICH:
            self.console = Console()

    def format_compiled(
        self,
        prompt: "CompiledPrompt",
        show_reasoning: bool = False,
        show_habits: bool = False,
        policy: "PolicyVector | None" = None,
    ) -> str:
        """
        Format compiled prompt for display.

        Args:
            prompt: The compiled prompt
            show_reasoning: Include reasoning traces
            show_habits: Show habit influence
            policy: PolicyVector if show_habits is True

        Returns:
            Formatted string for display
        """
        lines: list[str] = []

        # Header
        lines.append("=" * 60)
        lines.append("EVERGREEN PROMPT COMPILATION")
        lines.append("=" * 60)
        lines.append("")

        # Stats
        lines.append(f"Sections: {len(prompt.sections)}")
        lines.append(f"Total tokens: ~{prompt.token_count}")
        lines.append(f"Total chars: {len(prompt.content)}")
        lines.append(f"Timestamp: {datetime.now().isoformat()}")
        lines.append("")

        # Section summary
        lines.append("-" * 40)
        lines.append("SECTIONS")
        lines.append("-" * 40)
        for section in prompt.sections:
            required_marker = "[REQ]" if section.required else "[OPT]"
            lines.append(f"  {required_marker} {section.name}: {section.token_cost} tokens")
        lines.append("")

        # Reasoning traces
        if show_reasoning:
            lines.append("-" * 40)
            lines.append("REASONING TRACES")
            lines.append("-" * 40)
            for section in prompt.sections:
                lines.append(f"\n{section.name}:")
                traces = getattr(section, "reasoning_trace", [])
                if traces:
                    for trace in traces:
                        lines.append(f"  - {trace}")
                else:
                    lines.append("  (no traces)")
            lines.append("")

        # Habit influence
        if show_habits and policy:
            lines.append("-" * 40)
            lines.append("HABIT INFLUENCE (PolicyVector)")
            lines.append("-" * 40)
            lines.append(f"  Verbosity: {policy.verbosity:.2f}")
            lines.append(f"  Formality: {policy.formality:.2f}")
            lines.append(f"  Risk Tolerance: {policy.risk_tolerance:.2f}")
            lines.append(f"  Confidence: {policy.confidence:.2f}")
            lines.append(f"  Learned from: {', '.join(policy.learned_from)}")

            if policy.domain_focus:
                lines.append("\n  Domain Focus:")
                for domain, focus in policy.domain_focus:
                    bar = "█" * int(focus * 10) + "░" * (10 - int(focus * 10))
                    lines.append(f"    {domain:<15} [{bar}] {focus:.2f}")

            if policy.section_weights:
                lines.append("\n  Section Weights:")
                for section, weight in policy.section_weights:
                    bar = "█" * int(weight * 10) + "░" * (10 - int(weight * 10))
                    lines.append(f"    {section:<15} [{bar}] {weight:.2f}")

            if policy.reasoning_trace:
                lines.append("\n  Policy Reasoning:")
                for trace in policy.reasoning_trace[-5:]:  # Last 5
                    lines.append(f"    - {trace}")
            lines.append("")

        # Content preview
        lines.append("-" * 40)
        lines.append("CONTENT PREVIEW (first 500 chars)")
        lines.append("-" * 40)
        lines.append(prompt.content[:500] + "...")
        lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    def format_reasoning_tree(self, traces: list[str]) -> str:
        """
        Format reasoning traces as an ASCII tree.

        Args:
            traces: List of reasoning trace strings

        Returns:
            ASCII tree representation
        """
        if not traces:
            return "No reasoning traces available."

        lines = ["REASONING TREE", ""]

        for i, trace in enumerate(traces):
            is_last = i == len(traces) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{connector}{trace}")

        return "\n".join(lines)

    def format_habit_table(self, policy: "PolicyVector") -> str:
        """
        Format habit influence as a table.

        Args:
            policy: PolicyVector with habit information

        Returns:
            ASCII table representation
        """
        lines = ["HABIT INFLUENCE TABLE", ""]

        # Style preferences
        lines.append("┌─────────────────┬───────────┬────────────┐")
        lines.append("│ Preference      │ Value     │ Visual     │")
        lines.append("├─────────────────┼───────────┼────────────┤")

        for name, value in [
            ("Verbosity", policy.verbosity),
            ("Formality", policy.formality),
            ("Risk Tolerance", policy.risk_tolerance),
        ]:
            bar = "█" * int(value * 8) + "░" * (8 - int(value * 8))
            lines.append(f"│ {name:<15} │ {value:>9.2f} │ {bar} │")

        lines.append("└─────────────────┴───────────┴────────────┘")
        lines.append("")

        # Confidence and sources
        lines.append(f"Confidence: {policy.confidence:.2f}")
        lines.append(f"Sources: {', '.join(policy.learned_from)}")

        return "\n".join(lines)

    def format_diff(self, diff_content: str) -> str:
        """
        Format diff with syntax highlighting.

        Args:
            diff_content: Unified diff string

        Returns:
            Colored diff output (or plain if Rich not available)
        """
        if not diff_content:
            return "No differences found."

        lines = ["DIFF OUTPUT", "=" * 40, ""]

        for line in diff_content.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                lines.append(f"[+] {line}")
            elif line.startswith("-") and not line.startswith("---"):
                lines.append(f"[-] {line}")
            elif line.startswith("@@"):
                lines.append(f"[~] {line}")
            else:
                lines.append(f"    {line}")

        return "\n".join(lines)

    def format_history_timeline(
        self,
        history: list["CheckpointSummary"],
    ) -> str:
        """
        Format history as a timeline.

        Args:
            history: List of checkpoint summaries

        Returns:
            ASCII timeline representation
        """
        if not history:
            return "No checkpoint history found."

        lines = [
            "PROMPT EVOLUTION TIMELINE",
            "=" * 60,
            "",
        ]

        for i, summary in enumerate(history):
            is_last = i == len(history) - 1
            connector = "└" if is_last else "├"
            pipe = " " if is_last else "│"

            # Format timestamp
            ts = summary.timestamp
            ts_str = ts.strftime("%Y-%m-%d %H:%M") if hasattr(ts, "strftime") else str(ts)

            # Short ID
            short_id = summary.id[:8] if len(summary.id) > 8 else summary.id

            lines.append(f"{connector}─ [{short_id}] {ts_str}")
            lines.append(f"{pipe}     Reason: {summary.reason}")
            # Handle different summary formats
            if hasattr(summary, "sections_after"):
                lines.append(
                    f"{pipe}     Sections: {len(summary.sections_after)} ({getattr(summary, 'section_delta', 0):+d})"
                )
                lines.append(
                    f"{pipe}     Characters: {summary.content_length_after} ({getattr(summary, 'content_delta', 0):+d})"
                )
            else:
                # CheckpointSummary format from rollback module
                delta = summary.after_token_count - summary.before_token_count
                lines.append(f"{pipe}     Tokens: {summary.after_token_count} ({delta:+d})")
                lines.append(f"{pipe}     Changed: {', '.join(summary.sections_changed[:3])}")
            lines.append(f"{pipe}")

        lines.append("")
        lines.append(f"Total checkpoints: {len(history)}")
        lines.append("Use 'rollback <id>' to restore a previous version.")

        return "\n".join(lines)

    def format_preview(
        self,
        current_content: str,
        new_content: str,
    ) -> str:
        """
        Format a preview of changes.

        Args:
            current_content: Current prompt content
            new_content: Proposed new content

        Returns:
            Preview with diff summary
        """
        import difflib

        lines = [
            "CHANGE PREVIEW",
            "=" * 60,
            "",
        ]

        # Stats
        current_lines = current_content.split("\n")
        new_lines = new_content.split("\n")

        lines.append(f"Current: {len(current_content)} chars, {len(current_lines)} lines")
        lines.append(f"Proposed: {len(new_content)} chars, {len(new_lines)} lines")
        lines.append(
            f"Delta: {len(new_content) - len(current_content):+d} chars, {len(new_lines) - len(current_lines):+d} lines"
        )
        lines.append("")

        # Unified diff
        diff = difflib.unified_diff(
            current_lines,
            new_lines,
            fromfile="current",
            tofile="proposed",
            lineterm="",
        )

        diff_lines = list(diff)
        if diff_lines:
            lines.append("-" * 40)
            lines.append("DIFF (first 50 lines)")
            lines.append("-" * 40)
            for line in diff_lines[:50]:
                if line.startswith("+") and not line.startswith("+++"):
                    lines.append(f"[+] {line}")
                elif line.startswith("-") and not line.startswith("---"):
                    lines.append(f"[-] {line}")
                else:
                    lines.append(f"    {line}")

            if len(diff_lines) > 50:
                lines.append(f"    ... ({len(diff_lines) - 50} more lines)")
        else:
            lines.append("No changes detected.")

        return "\n".join(lines)

    def format_improvement_result(
        self,
        original: str,
        improved: str,
        sections_modified: tuple[str, ...],
        reasoning_trace: tuple[str, ...],
        checkpoint_id: str | None = None,
    ) -> str:
        """
        Format TextGRAD improvement result.

        Args:
            original: Original content
            improved: Improved content
            sections_modified: Which sections were changed
            reasoning_trace: Reasoning traces from improvement
            checkpoint_id: Checkpoint ID if created

        Returns:
            Formatted improvement summary
        """
        lines = [
            "TEXTGRAD IMPROVEMENT RESULT",
            "=" * 60,
            "",
        ]

        # Stats
        lines.append(f"Original: {len(original)} chars")
        lines.append(f"Improved: {len(improved)} chars")
        lines.append(f"Delta: {len(improved) - len(original):+d} chars")
        lines.append(f"Sections modified: {', '.join(sections_modified) or 'none'}")

        if checkpoint_id:
            lines.append(f"Checkpoint: {checkpoint_id}")

        lines.append("")

        # Reasoning trace
        if reasoning_trace:
            lines.append("-" * 40)
            lines.append("REASONING TRACE")
            lines.append("-" * 40)
            for trace in reasoning_trace:
                lines.append(f"  - {trace}")
            lines.append("")

        # Preview
        if original != improved:
            lines.append("-" * 40)
            lines.append("CHANGE PREVIEW (first 300 chars)")
            lines.append("-" * 40)
            lines.append(improved[:300] + "...")
        else:
            lines.append("No changes made (identity).")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)


# Rich output helpers (if Rich is available)


def print_rich_panel(
    title: str,
    content: str,
    style: str = "blue",
) -> None:
    """Print content in a Rich panel if available."""
    if HAS_RICH:
        console = Console()
        panel = Panel(content, title=title, style=style)
        console.print(panel)
    else:
        print(f"\n{title}\n{'=' * len(title)}\n{content}\n")


def print_rich_table(
    title: str,
    headers: list[str],
    rows: list[list[str]],
) -> None:
    """Print a Rich table if available."""
    if HAS_RICH:
        console = Console()
        table = Table(title=title)
        for header in headers:
            table.add_column(header)
        for row in rows:
            table.add_row(*row)
        console.print(table)
    else:
        print(f"\n{title}")
        print("-" * 60)
        print(" | ".join(headers))
        print("-" * 60)
        for row in rows:
            print(" | ".join(row))


def print_rich_tree(
    root: str,
    children: list[tuple[str, list[str]]],
) -> None:
    """Print a Rich tree if available."""
    if HAS_RICH:
        console = Console()
        tree = Tree(root)
        for child, grandchildren in children:
            branch = tree.add(child)
            for gc in grandchildren:
                branch.add(gc)
        console.print(tree)
    else:
        print(f"\n{root}")
        for child, grandchildren in children:
            print(f"├── {child}")
            for gc in grandchildren:
                print(f"│   ├── {gc}")


__all__ = [
    "PromptOutputFormatter",
    "print_rich_panel",
    "print_rich_table",
    "print_rich_tree",
    "HAS_RICH",
]
