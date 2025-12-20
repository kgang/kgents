"""
Plan Parser: Extract progress from plan files and _forest.md.

Provides real-time progress data for Garden plots by parsing:
1. _forest.md table rows for progress percentages
2. Individual plan file headers for status/progress lines
3. YAML frontmatter for progress metadata

Phase 5: Batteries Included Developer Experience
See: plans/melodic-toasting-octopus.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class PlanMetadata:
    """Parsed metadata from a plan file."""

    name: str
    progress: float  # 0.0 to 1.0
    status: str  # e.g., "active", "complete", "planning", "dormant"
    notes: str
    plan_path: str | None = None


def parse_progress_string(progress_str: str) -> float:
    """
    Parse a progress string like "88%" or "0.88" to a float.

    Args:
        progress_str: Progress string (e.g., "88%", "100%", "—", "0.5")

    Returns:
        Progress as float between 0.0 and 1.0, or 0.0 if unparseable
    """
    if not progress_str:
        return 0.0

    progress_str = progress_str.strip()

    # Handle "—" or "-" (en-dash or hyphen) as 0%
    if progress_str in ("—", "-", ""):
        return 0.0

    # Handle percentage like "88%"
    if progress_str.endswith("%"):
        try:
            return float(progress_str[:-1]) / 100.0
        except ValueError:
            return 0.0

    # Handle decimal like "0.88"
    try:
        val = float(progress_str)
        # If it's already between 0 and 1, use as-is
        if 0 <= val <= 1:
            return val
        # If it's between 0 and 100, convert to ratio
        if 0 <= val <= 100:
            return val / 100.0
        return 0.0
    except ValueError:
        return 0.0


def parse_forest_table(forest_path: Path) -> dict[str, PlanMetadata]:
    """
    Parse the _forest.md table to extract plan progress.

    Expected table format:
    | Plan | Progress | Status | Notes |
    |------|----------|--------|-------|
    | **plans/foo** | 88% | **active** | Some notes |
    | plans/bar | 0% | planning | Other notes |

    Args:
        forest_path: Path to _forest.md file

    Returns:
        Dict mapping plan name (stem) to PlanMetadata
    """
    if not forest_path.exists():
        return {}

    result: dict[str, PlanMetadata] = {}
    content = forest_path.read_text(encoding="utf-8")

    # Split into lines and find table rows
    lines = content.split("\n")

    # Pattern for table rows: | col1 | col2 | col3 | col4 |
    # Table header/separator lines start with |-- or contain only |, -, :
    table_row_pattern = re.compile(r"^\s*\|(.+)\|\s*$")
    separator_pattern = re.compile(r"^[\s\|\-:]+$")

    for line in lines:
        # Skip separators and non-table lines
        if separator_pattern.match(line):
            continue

        match = table_row_pattern.match(line)
        if not match:
            continue

        # Split by | and clean up cells
        cells = [cell.strip() for cell in match.group(1).split("|")]

        # Need at least 4 columns: Plan, Progress, Status, Notes
        if len(cells) < 4:
            continue

        plan_cell = cells[0]
        progress_cell = cells[1]
        status_cell = cells[2]
        notes_cell = cells[3] if len(cells) > 3 else ""

        # Skip header rows
        if plan_cell.lower() in ("plan", "plans"):
            continue

        # Extract plan name from cell (strip ** and plans/)
        # Examples: "**plans/foo**" -> "foo", "plans/bar" -> "bar"
        plan_name = plan_cell.strip("*").strip()
        if plan_name.startswith("plans/"):
            plan_name = plan_name[6:]  # Remove "plans/"
        if plan_name.startswith("core-apps/"):
            plan_name = plan_name[10:]  # Remove "core-apps/"

        # Skip empty names
        if not plan_name:
            continue

        # Parse progress
        progress = parse_progress_string(progress_cell)

        # Parse status (strip ** markup)
        status = status_cell.strip("*").strip().lower()

        result[plan_name] = PlanMetadata(
            name=plan_name,
            progress=progress,
            status=status,
            notes=notes_cell.strip(),
            plan_path=None,  # Will be filled in by caller
        )

    return result


async def parse_plan_progress(plan_path: Path) -> PlanMetadata:
    """
    Extract progress from an individual plan file.

    Checks (in order of priority):
    1. YAML frontmatter: `progress: 0.75` or `progress: 75%`
    2. Status line: `**Status**: 75% complete` or `Status: 75%`
    3. Progress line: `Progress: 75%`

    Args:
        plan_path: Path to the plan .md file

    Returns:
        PlanMetadata with extracted progress, or default 0.0
    """
    if not plan_path.exists():
        return PlanMetadata(
            name=plan_path.stem,
            progress=0.0,
            status="unknown",
            notes="File not found",
            plan_path=str(plan_path),
        )

    content = plan_path.read_text(encoding="utf-8")
    name = plan_path.stem
    progress = 0.0
    status = "active"
    notes = ""

    # 1. Check for YAML frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)

        # Look for progress: line
        progress_match = re.search(r"^progress:\s*(.+)$", frontmatter, re.MULTILINE)
        if progress_match:
            progress = parse_progress_string(progress_match.group(1))

        # Look for status: line
        status_match = re.search(r"^status:\s*(.+)$", frontmatter, re.MULTILINE)
        if status_match:
            status = status_match.group(1).strip().lower()

        # Look for momentum: line (alternative progress indicator)
        momentum_match = re.search(r"^momentum:\s*(.+)$", frontmatter, re.MULTILINE)
        if momentum_match and progress == 0.0:
            progress = parse_progress_string(momentum_match.group(1))

    # 2. Check for Status line in body
    # Pattern: **Status**: EXECUTING (Phase 0.5)
    # or: Status: 75% complete
    status_line_match = re.search(r"\*?\*?Status\*?\*?:\s*([^\n]+)", content, re.IGNORECASE)
    if status_line_match:
        status_text = status_line_match.group(1).strip()
        status = _extract_status_keyword(status_text)

        # Try to extract progress from status line
        percent_match = re.search(r"(\d+(?:\.\d+)?)\s*%", status_text)
        if percent_match and progress == 0.0:
            progress = parse_progress_string(percent_match.group(1) + "%")

    # 3. Check for explicit Progress line
    progress_line_match = re.search(
        r"\*?\*?Progress\*?\*?:\s*(\d+(?:\.\d+)?)\s*%", content, re.IGNORECASE
    )
    if progress_line_match and progress == 0.0:
        progress = parse_progress_string(progress_line_match.group(1) + "%")

    # 4. Try to extract first meaningful line as notes
    # Skip title line (starts with #) and empty lines
    for line in content.split("\n"):
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("---"):
            # Skip frontmatter
            if ":" in line and len(line) < 50:
                continue
            notes = line[:100]  # First 100 chars
            break

    return PlanMetadata(
        name=name,
        progress=progress,
        status=status,
        notes=notes,
        plan_path=str(plan_path),
    )


def _extract_status_keyword(status_text: str) -> str:
    """
    Extract status keyword from status text.

    Examples:
        "EXECUTING (Phase 0.5)" -> "executing"
        "**complete**" -> "complete"
        "active" -> "active"
    """
    status_text = status_text.lower().strip("*").strip()

    # Known status keywords
    keywords = [
        "complete",
        "active",
        "executing",
        "planning",
        "dormant",
        "superseded",
        "pending",
        "seedling",
        "priority",
    ]

    for keyword in keywords:
        if keyword in status_text:
            return keyword

    # First word as fallback
    first_word = status_text.split()[0] if status_text else "unknown"
    return first_word.strip("(").strip(")")


# =============================================================================
# Crown Jewel Mapping
# =============================================================================

# Map plan names to Crown Jewel names
PLAN_TO_JEWEL: dict[str, str | None] = {
    # Crown Jewel plans
    "holographic-brain": "holographic-brain",
    "the-gardener": "gardener",
    "gestalt-architecture-visualizer": "gestalt-viz",
    "atelier-experience": "atelier",
    "coalition-forge": "coalition-forge",
    "punchdrunk-park": "punchdrunk-park",
    "domain-simulation": "domain-sim",
    # kgentsd is the 8th jewel
    "kgentsd-crown-jewel": "kgentsd",
    # Partial matches
    "town-visualizer-renaissance": "punchdrunk-park",
    "town-rebuild": "punchdrunk-park",
    "crown-jewels-enlightened": None,  # Meta plan, not a jewel
}


def infer_crown_jewel(plan_name: str) -> str | None:
    """
    Infer which Crown Jewel a plan corresponds to.

    Args:
        plan_name: The plan file stem (e.g., "coalition-forge")

    Returns:
        Crown Jewel plot name or None if no match
    """
    # Direct match
    if plan_name in PLAN_TO_JEWEL:
        return PLAN_TO_JEWEL[plan_name]

    # Partial match
    for pattern, jewel in PLAN_TO_JEWEL.items():
        if pattern in plan_name or plan_name in pattern:
            return jewel

    return None


def infer_agentese_path(plan_path: Path) -> str:
    """
    Infer AGENTESE path from plan file location.

    Args:
        plan_path: Path to plan file

    Returns:
        AGENTESE path (e.g., "world.forge", "concept.plan.foo")
    """
    name = plan_path.stem.replace("-", "_")

    # Core apps → world.*
    if "core-apps" in str(plan_path):
        if "atelier" in name:
            return "world.atelier"
        if "coalition" in name or "forge" in name:
            return "world.forge"
        if "gestalt" in name:
            return "world.codebase"
        if "punchdrunk" in name or "park" in name:
            return "world.town"
        if "domain" in name:
            return "world.simulation"
        return f"world.{name}"

    # kgentsd → self.witness (8th jewel)
    if "kgentsd" in name:
        return "self.witness"

    # Gardener → concept.gardener
    if "gardener" in name:
        return "concept.gardener"

    # Brain → self.memory
    if "brain" in name:
        return "self.memory"

    # Generic plans → concept.plan.*
    return f"concept.plan.{name}"


__all__ = [
    "PlanMetadata",
    "parse_progress_string",
    "parse_forest_table",
    "parse_plan_progress",
    "infer_crown_jewel",
    "infer_agentese_path",
]
