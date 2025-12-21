"""
Garden View Generator: What grew while I slept?

Movement 1 of the Morning Coffee ritual. Non-demanding observation
of yesterday's changes — lets the eye wander, doesn't demand focus.

Inputs:
- git diff --stat (yesterday's file changes)
- NOW.md parsing (progress percentages)
- Recent brainstorming files (seeds of new ideas)

Patterns Applied:
- Signal Aggregation (Pattern 4): categorize changes by type
- Dual-Channel Output (Pattern 7): CLI + semantic

See: spec/services/morning-coffee.md
"""

from __future__ import annotations

import asyncio
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .types import (
    GardenCategory,
    GardenItem,
    GardenView,
)

# =============================================================================
# Git Operations
# =============================================================================


def parse_git_stat(
    since: datetime | None = None,
    repo_path: Path | str | None = None,
) -> list[GardenItem]:
    """
    Parse git diff --stat since a given time.

    Returns GardenItem for each file changed, categorized as HARVEST.
    Files that no longer exist are filtered out.

    Args:
        since: Starting time for diff (defaults to yesterday)
        repo_path: Path to repository (defaults to cwd)

    Returns:
        List of GardenItem representing yesterday's harvest
    """
    if since is None:
        # Default: yesterday at midnight
        now = datetime.now()
        since = datetime(now.year, now.month, now.day) - timedelta(days=1)

    since_str = since.strftime("%Y-%m-%d %H:%M:%S")

    cmd = [
        "git",
        "log",
        f"--since={since_str}",
        "--format=",  # No commit message, just stats
        "--numstat",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=repo_path,
    )

    if result.returncode != 0:
        # Graceful degradation: empty harvest if git fails
        return []

    return _parse_numstat(result.stdout)


def _parse_numstat(output: str) -> list[GardenItem]:
    """Parse git numstat output into GardenItems."""
    # Aggregate by file
    file_stats: dict[str, dict[str, int]] = {}

    for line in output.strip().split("\n"):
        if not line.strip():
            continue

        parts = line.split("\t")
        if len(parts) < 3:
            continue

        try:
            insertions = int(parts[0]) if parts[0] != "-" else 0
            deletions = int(parts[1]) if parts[1] != "-" else 0
            filepath = parts[2]

            if filepath not in file_stats:
                file_stats[filepath] = {"insertions": 0, "deletions": 0}

            file_stats[filepath]["insertions"] += insertions
            file_stats[filepath]["deletions"] += deletions

        except ValueError:
            continue

    # Convert to GardenItems
    items: list[GardenItem] = []
    for filepath, stats in file_stats.items():
        total_changes = stats["insertions"] + stats["deletions"]
        if total_changes == 0:
            continue

        # Create description based on change type
        if stats["deletions"] > stats["insertions"] * 2:
            verb = "cleaned up"
        elif stats["insertions"] > stats["deletions"] * 2:
            verb = "expanded"
        else:
            verb = "refined"

        # Simplify path for display
        display_path = _simplify_path(filepath)

        items.append(
            GardenItem(
                description=f"{verb} {display_path}",
                category=GardenCategory.HARVEST,
                files_changed=1,
                source="git",
            )
        )

    return items


def _simplify_path(filepath: str) -> str:
    """Simplify a file path for display."""
    # Remove common prefixes
    prefixes = ["impl/claude/", "impl/", "spec/", "docs/"]
    for prefix in prefixes:
        if filepath.startswith(prefix):
            filepath = filepath[len(prefix) :]
            break

    # Shorten if still too long
    if len(filepath) > 50:
        parts = filepath.split("/")
        if len(parts) > 2:
            filepath = f"{parts[0]}/.../{parts[-1]}"

    return filepath


# =============================================================================
# NOW.md Parsing
# =============================================================================


def parse_now_md(
    now_md_path: Path | str | None = None,
) -> dict[str, float]:
    """
    Parse NOW.md to extract jewel progress percentages.

    Returns dict of jewel_name → percentage (0.0-1.0)

    The NOW.md format expected:
    - Lines like "Brain 100%" or "**Brain** 100%"
    - Patterns: name followed by percentage
    """
    if now_md_path is None:
        now_md_path = Path.cwd() / "NOW.md"

    path = Path(now_md_path)
    if not path.exists():
        return {}

    content = path.read_text()

    # Pattern: "JewelName XX%" or "**JewelName** XX%"
    pattern = r"\*{0,2}(\w+)\*{0,2}\s*[:=]?\s*(\d+)%"

    jewels: dict[str, float] = {}
    for match in re.finditer(pattern, content):
        name = match.group(1).lower()
        percentage = int(match.group(2)) / 100.0

        # Only include likely jewel names
        known_jewels = {
            "brain",
            "gardener",
            "gestalt",
            "atelier",
            "town",
            "park",
            "witness",
            "conductor",
            "ashc",
            "liminal",
            "forge",
            "muse",
        }
        if name in known_jewels:
            jewels[name] = percentage

    return jewels


def _categorize_by_progress(name: str, percentage: float) -> GardenCategory:
    """Categorize a jewel by its progress percentage."""
    if percentage >= 0.95:
        return GardenCategory.HARVEST  # Mature, complete
    elif percentage >= 0.70:
        return GardenCategory.GROWING  # Active, high progress
    elif percentage >= 0.30:
        return GardenCategory.SPROUTING  # Recently started
    else:
        return GardenCategory.SEEDS  # Just planted


# =============================================================================
# Brainstorming Detection
# =============================================================================


def detect_recent_brainstorming(
    brainstorm_path: Path | str | None = None,
    since: datetime | None = None,
) -> list[GardenItem]:
    """
    Detect recent brainstorming files as seeds.

    Brainstorming files are ideas that haven't yet become implementation.
    """
    if brainstorm_path is None:
        brainstorm_path = Path.cwd() / "brainstorming"

    path = Path(brainstorm_path)
    if not path.exists():
        return []

    if since is None:
        since = datetime.now() - timedelta(days=2)

    items: list[GardenItem] = []
    for md_file in path.glob("*.md"):
        # Check modification time
        mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
        if mtime >= since:
            # Extract title from filename
            title = md_file.stem.replace("-", " ").title()
            # Remove date prefix if present
            if re.match(r"^\d{4} \d{2} \d{2}", title):
                title = title[11:].strip()

            items.append(
                GardenItem(
                    description=f"Idea: {title}",
                    category=GardenCategory.SEEDS,
                    source="brainstorming",
                )
            )

    return items


# =============================================================================
# Main Generator
# =============================================================================


def generate_garden_view(
    repo_path: Path | str | None = None,
    now_md_path: Path | str | None = None,
    brainstorm_path: Path | str | None = None,
    since: datetime | None = None,
) -> GardenView:
    """
    Generate the complete Garden View for Morning Coffee.

    Combines:
    1. Git changes (harvest)
    2. NOW.md progress (growing/sprouting)
    3. Recent brainstorming (seeds)

    Returns a non-demanding view for the eye to wander.
    """
    if since is None:
        # Yesterday at midnight
        now = datetime.now()
        since = datetime(now.year, now.month, now.day) - timedelta(days=1)

    # Collect from each source
    git_items = parse_git_stat(since=since, repo_path=repo_path)
    brainstorm_items = detect_recent_brainstorming(
        brainstorm_path=brainstorm_path,
        since=since,
    )

    # Parse NOW.md for progress items
    progress = parse_now_md(now_md_path=now_md_path)
    progress_items: list[GardenItem] = []
    for jewel, pct in progress.items():
        category = _categorize_by_progress(jewel, pct)
        if category != GardenCategory.HARVEST:  # Don't duplicate harvest
            progress_items.append(
                GardenItem(
                    description=f"{jewel.title()} {int(pct * 100)}%",
                    category=category,
                    source="now_md",
                    percentage=pct,
                )
            )

    # Categorize into view buckets
    harvest = tuple(item for item in git_items if item.category == GardenCategory.HARVEST)

    growing = tuple(item for item in progress_items if item.category == GardenCategory.GROWING)

    sprouting = tuple(item for item in progress_items if item.category == GardenCategory.SPROUTING)

    seeds = tuple(brainstorm_items)

    return GardenView(
        harvest=harvest,
        growing=growing,
        sprouting=sprouting,
        seeds=seeds,
        generated_at=datetime.now(),
    )


# =============================================================================
# Async Variant
# =============================================================================


async def generate_garden_view_async(
    repo_path: Path | str | None = None,
    now_md_path: Path | str | None = None,
    brainstorm_path: Path | str | None = None,
    since: datetime | None = None,
) -> GardenView:
    """
    Async version of generate_garden_view.

    Runs sync operations in thread pool for non-blocking IO.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: generate_garden_view(
            repo_path=repo_path,
            now_md_path=now_md_path,
            brainstorm_path=brainstorm_path,
            since=since,
        ),
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "parse_git_stat",
    "parse_now_md",
    "detect_recent_brainstorming",
    "generate_garden_view",
    "generate_garden_view_async",
]
