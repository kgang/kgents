"""
Status Agents - Composable status reporting morphisms.

Refactored from show_status() to demonstrate morphism principle:
- Separate querying (State → Data) from presentation (Data → Output)
- Each agent is a morphism with clear input/output types
- Composable via >> operator

Architecture:
    StatusReporter = GitStatusAgent >> EvolutionLogAgent >> HydrateStatusAgent >> StatusPresenter

Each query agent is State → PartialData, presenter is Data → Output.
"""

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from runtime.base import Agent


# ============================================================================
# Types
# ============================================================================


@dataclass
class GitStatus:
    """Git repository status."""

    uncommitted: bool


@dataclass
class EvolutionLogData:
    """Evolution log metrics."""

    timestamp: str
    target: str
    experiments: int
    passed: int
    failed: int
    held: int
    incorporated: int
    failed_experiments: list[dict[str, Any]]


@dataclass
class HydrateStatus:
    """HYDRATE.md TL;DR section."""

    tldr_lines: list[str]


@dataclass
class StatusData:
    """Complete status data from all sources."""

    base_path: Path
    git: GitStatus | None = None
    evolution: EvolutionLogData | None = None
    hydrate: HydrateStatus | None = None


# ============================================================================
# Query Agents (State → Data morphisms)
# ============================================================================


class GitStatusAgent(Agent[Path, StatusData]):
    """Query git status: Path → StatusData with git field populated."""

    @property
    def name(self) -> str:
        return "GitStatusAgent"

    async def invoke(self, base_path: Path) -> StatusData:
        """Query git for uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
                cwd=base_path,
            )
            uncommitted = bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            uncommitted = False

        return StatusData(
            base_path=base_path,
            git=GitStatus(uncommitted=uncommitted),
        )


class EvolutionLogAgent(Agent[StatusData, StatusData]):
    """Query evolution logs: StatusData → StatusData with evolution field populated."""

    @property
    def name(self) -> str:
        return "EvolutionLogAgent"

    async def invoke(self, status: StatusData) -> StatusData:
        """Query most recent evolution log."""
        log_dir = status.base_path / ".evolve_logs"

        if not log_dir.exists():
            return status

        recent_logs = sorted(
            log_dir.glob("evolve_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if not recent_logs:
            return status

        latest = recent_logs[0]
        with open(latest) as f:
            data = json.load(f)

        summary = data.get("summary", {})
        status.evolution = EvolutionLogData(
            timestamp=data.get("timestamp", "unknown"),
            target=data.get("config", {}).get("target", "unknown"),
            experiments=summary.get("total_experiments", 0),
            passed=summary.get("passed", 0),
            failed=summary.get("failed", 0),
            held=summary.get("held", 0),
            incorporated=summary.get("incorporated", 0),
            failed_experiments=data.get("failed_experiments", []),
        )

        return status


class HydrateStatusAgent(Agent[StatusData, StatusData]):
    """Query HYDRATE.md: StatusData → StatusData with hydrate field populated."""

    @property
    def name(self) -> str:
        return "HydrateStatusAgent"

    async def invoke(self, status: StatusData) -> StatusData:
        """Extract TL;DR section from HYDRATE.md."""
        hydrate_path = status.base_path.parent.parent / "HYDRATE.md"

        if not hydrate_path.exists():
            return status

        content = hydrate_path.read_text()
        lines = content.split("\n")

        tldr_lines = []
        in_tldr = False
        for line in lines:
            if "## TL;DR" in line:
                in_tldr = True
                continue
            if in_tldr:
                if line.startswith("##"):
                    break
                if line.strip() and not line.startswith("---"):
                    tldr_lines.append(line)

        status.hydrate = HydrateStatus(tldr_lines=tldr_lines)
        return status


# ============================================================================
# Presenter Agent (Data → Output morphism with side effects)
# ============================================================================


class StatusPresenterAgent(Agent[StatusData, None]):
    """Present status data: StatusData → None (side effect: logging)."""

    @property
    def name(self) -> str:
        return "StatusPresenterAgent"

    async def invoke(self, status: StatusData) -> None:
        """Format and log status data."""
        print("=" * 60)
        print("KGENTS EVOLUTION STATUS")
        print("=" * 60)

        # Git status
        if status.git:
            git_msg = (
                "⚠️  Uncommitted changes" if status.git.uncommitted else "✓ Clean"
            )
            print(f"Git Status: {git_msg}")

        # Evolution logs
        if status.evolution:
            evo = status.evolution
            print(f"\nLast Run: {evo.timestamp}")
            print(f"  Target: {evo.target}")
            print(f"  Experiments: {evo.experiments}")
            print(f"    ✓ Passed: {evo.passed}")
            print(f"    ✗ Failed: {evo.failed}")
            print(f"    ⏸ Held: {evo.held}")
            print(f"    ✅ Incorporated: {evo.incorporated}")

            # Show failed experiments
            if evo.failed_experiments:
                failed_count = len(evo.failed_experiments)
                print(f"\n  Recent Failures ({failed_count} total):")
                for exp in evo.failed_experiments[:3]:
                    module = exp.get("module", "unknown")
                    error = exp.get("error", "no error")[:60]
                    print(f"    - {module}: {error}")
                if failed_count > 3:
                    print(f"    ... and {failed_count - 3} more")
        else:
            print("\nNo evolution logs found")

        # HYDRATE.md status
        if status.hydrate:
            print("\nHYDRATE.md Status:")
            for line in status.hydrate.tldr_lines:
                print(f"  {line}")

        # Recommendations
        print(f"\n{'=' * 60}")
        print("RECOMMENDED ACTIONS FOR AI AGENTS")
        print(f"{'=' * 60}")
        print("1. Run 'python evolve.py suggest' to see improvement suggestions")
        print("2. Run 'python evolve.py test' to test evolve.py improvements (fast)")
        print("3. Run 'python evolve.py meta --auto-apply' to apply meta improvements")
        print("4. Run 'python evolve.py full --auto-apply' for full codebase evolution")
        print("5. Update HYDRATE.md after significant changes")
        print("")

        return None


# ============================================================================
# Composed Status Reporter
# ============================================================================


def create_status_reporter() -> Agent[Path, None]:
    """
    Create composed status reporter agent.

    Composition: Path → StatusData → StatusData → StatusData → None
    """
    return (
        GitStatusAgent()
        >> EvolutionLogAgent()
        >> HydrateStatusAgent()
        >> StatusPresenterAgent()
    )
