"""
Conceptual Weather Analyzer: What's shifting in the atmosphere?

Movement 2 of the Morning Coffee ritual. Non-demanding observation
of conceptual patterns — not code changes, but what's *moving*.

Weather Patterns:
- REFACTORING: Things being consolidated, renamed, migrated
- EMERGING: New patterns, principles, insights appearing
- SCAFFOLDING: Architecture being built
- TENSION: Competing concerns, unresolved decisions

Inputs:
- plans/*.md headers and status
- Git commit messages for semantic patterns
- Recent file activity patterns

Patterns Applied:
- Signal Aggregation (Pattern 4): detect patterns from multiple signals
- Bounded History (Pattern 8): limited lookback

See: spec/services/morning-coffee.md
"""

from __future__ import annotations

import asyncio
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator

from .types import (
    ConceptualWeather,
    WeatherPattern,
    WeatherType,
)

# =============================================================================
# Plan Parsing
# =============================================================================


def parse_plan_headers(
    plans_path: Path | str | None = None,
) -> list[dict[str, str]]:
    """
    Parse plan file headers for status and context.

    Returns list of {name, status, notes} dicts.
    """
    if plans_path is None:
        plans_path = Path.cwd() / "plans"

    path = Path(plans_path)
    if not path.exists():
        return []

    plans: list[dict[str, str]] = []

    for md_file in path.glob("*.md"):
        # Skip archive and meta files
        if md_file.name.startswith("_"):
            continue

        content = md_file.read_text()

        # Parse YAML frontmatter if present
        header = _parse_frontmatter(content)
        header["name"] = md_file.stem.replace("-", " ").title()
        header["filename"] = md_file.name

        plans.append(header)

    return plans


def _parse_frontmatter(content: str) -> dict[str, str]:
    """Parse YAML frontmatter from markdown."""
    result: dict[str, str] = {}

    if not content.startswith("---"):
        return result

    # Find closing ---
    end_idx = content.find("---", 3)
    if end_idx == -1:
        return result

    frontmatter = content[3:end_idx]

    # Simple key: value parsing
    for line in frontmatter.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()

    return result


# =============================================================================
# Commit Message Analysis
# =============================================================================


def analyze_commit_messages(
    since: datetime | None = None,
    repo_path: Path | str | None = None,
    max_commits: int = 50,
) -> list[str]:
    """
    Get recent commit messages for pattern analysis.

    Returns list of commit messages (subject lines only).
    """
    if since is None:
        since = datetime.now() - timedelta(days=3)

    since_str = since.strftime("%Y-%m-%d %H:%M:%S")

    cmd = [
        "git",
        "log",
        f"--since={since_str}",
        f"-n{max_commits}",
        "--format=%s",  # Subject line only
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=repo_path,
    )

    if result.returncode != 0:
        return []

    return [line.strip() for line in result.stdout.split("\n") if line.strip()]


# =============================================================================
# Pattern Detection
# =============================================================================


def detect_refactoring(
    commit_messages: list[str],
    plans: list[dict[str, str]],
) -> list[WeatherPattern]:
    """
    Detect refactoring patterns.

    Signals:
    - Commit messages with "refactor", "rename", "move", "consolidate"
    - Plans with status containing "refactor"
    - High file churn with low net change
    """
    patterns: list[WeatherPattern] = []

    # Check commit messages
    refactor_keywords = ["refactor", "rename", "move", "consolidate", "merge", "migrate"]

    refactor_commits = [
        msg for msg in commit_messages if any(kw in msg.lower() for kw in refactor_keywords)
    ]

    if refactor_commits:
        # Group similar commits
        patterns.append(
            WeatherPattern(
                type=WeatherType.REFACTORING,
                label=_extract_scope(refactor_commits[0]) or "Code cleanup",
                description=_summarize_commits(refactor_commits),
                source="commit",
            )
        )

    # Check plans
    for plan in plans:
        status = plan.get("status", "").lower()
        notes = plan.get("session_notes", "").lower()

        if "refactor" in status or "refactor" in notes or "consolidat" in notes:
            patterns.append(
                WeatherPattern(
                    type=WeatherType.REFACTORING,
                    label=plan["name"],
                    description=f"Plan status: {status}" if status else "Refactoring in progress",
                    source="plan",
                )
            )

    return patterns


def detect_emerging(
    commit_messages: list[str],
    plans: list[dict[str, str]],
) -> list[WeatherPattern]:
    """
    Detect emerging patterns and insights.

    Signals:
    - Commit messages with "add", "introduce", "new", "implement"
    - Plans with status "research" or "planning"
    - New concepts appearing in commit scopes
    """
    patterns: list[WeatherPattern] = []

    # Check commit messages
    emerging_keywords = ["add", "introduce", "new feature", "implement", "create", "design"]

    emerging_commits = [
        msg for msg in commit_messages if any(kw in msg.lower() for kw in emerging_keywords)
    ]

    if emerging_commits:
        scope = _extract_scope(emerging_commits[0])
        patterns.append(
            WeatherPattern(
                type=WeatherType.EMERGING,
                label=scope or "New capability",
                description=_summarize_commits(emerging_commits),
                source="commit",
            )
        )

    # Check plans in research/planning phase
    for plan in plans:
        status = plan.get("status", "").lower()

        if status in ("research", "planning", "fresh"):
            patterns.append(
                WeatherPattern(
                    type=WeatherType.EMERGING,
                    label=plan["name"],
                    description=f"In {status} phase",
                    source="plan",
                )
            )

    return patterns


def detect_scaffolding(
    commit_messages: list[str],
    plans: list[dict[str, str]],
) -> list[WeatherPattern]:
    """
    Detect scaffolding/architecture patterns.

    Signals:
    - Commit messages with "arch", "structure", "foundation", "scaffold"
    - Plans with status "implement" or "active"
    - Multi-file changes with consistent patterns
    """
    patterns: list[WeatherPattern] = []

    # Check commit messages
    scaffold_keywords = ["arch", "structure", "foundation", "scaffold", "infra", "bootstrap"]

    scaffold_commits = [
        msg for msg in commit_messages if any(kw in msg.lower() for kw in scaffold_keywords)
    ]

    if scaffold_commits:
        scope = _extract_scope(scaffold_commits[0])
        patterns.append(
            WeatherPattern(
                type=WeatherType.SCAFFOLDING,
                label=scope or "Architecture",
                description=_summarize_commits(scaffold_commits),
                source="commit",
            )
        )

    # Check active/implement plans
    for plan in plans:
        status = plan.get("status", "").lower()

        if status in ("implement", "active", "in_progress"):
            patterns.append(
                WeatherPattern(
                    type=WeatherType.SCAFFOLDING,
                    label=plan["name"],
                    description=f"Actively building ({status})",
                    source="plan",
                )
            )

    return patterns


def detect_tension(
    commit_messages: list[str],
    plans: list[dict[str, str]],
) -> list[WeatherPattern]:
    """
    Detect tensions and competing concerns.

    Signals:
    - Commit messages with "fix", "revert", "workaround"
    - Plans with blocking dependencies
    - Back-and-forth changes to same files
    """
    patterns: list[WeatherPattern] = []

    # Check commit messages for fixes/reverts
    tension_keywords = ["fix", "revert", "workaround", "hotfix", "rollback", "temp"]

    tension_commits = [
        msg for msg in commit_messages if any(kw in msg.lower() for kw in tension_keywords)
    ]

    if len(tension_commits) > 2:  # Multiple fixes = tension
        scope = _extract_scope(tension_commits[0])
        patterns.append(
            WeatherPattern(
                type=WeatherType.TENSION,
                label=scope or "Stability concerns",
                description=f"{len(tension_commits)} fixes/reverts recently",
                source="commit",
            )
        )

    # Check plans with blocking dependencies
    for plan in plans:
        blocking = plan.get("blocking", "")
        if blocking and blocking not in ("[]", ""):
            patterns.append(
                WeatherPattern(
                    type=WeatherType.TENSION,
                    label=plan["name"],
                    description=f"Blocked by: {blocking}",
                    source="plan",
                )
            )

    return patterns


# =============================================================================
# Helper Functions
# =============================================================================


def _extract_scope(commit_message: str) -> str | None:
    """Extract scope from conventional commit message."""
    # Pattern: type(scope): message
    match = re.match(r"\w+\(([^)]+)\):", commit_message)
    if match:
        return match.group(1).title()

    # Pattern: type: message
    if ": " in commit_message:
        prefix = commit_message.split(": ")[0]
        if len(prefix) < 20:  # Reasonable type length
            return prefix.title()

    return None


def _summarize_commits(commits: list[str], max_show: int = 3) -> str:
    """Summarize a list of commits into a brief description."""
    if not commits:
        return ""

    if len(commits) == 1:
        return commits[0][:60]

    if len(commits) <= max_show:
        return "; ".join(c[:40] for c in commits)

    shown = "; ".join(c[:30] for c in commits[:max_show])
    return f"{shown}; +{len(commits) - max_show} more"


# =============================================================================
# Main Generator
# =============================================================================


def generate_weather(
    repo_path: Path | str | None = None,
    plans_path: Path | str | None = None,
    since: datetime | None = None,
) -> ConceptualWeather:
    """
    Generate the Conceptual Weather for Morning Coffee.

    Combines signals from:
    1. Git commit messages (semantic patterns)
    2. Plan file statuses (project direction)

    Returns non-demanding observation of what's shifting.
    """
    if since is None:
        since = datetime.now() - timedelta(days=3)

    # Collect signals
    commits = analyze_commit_messages(since=since, repo_path=repo_path)
    plans = parse_plan_headers(plans_path=plans_path)

    # Detect each weather type
    refactoring = detect_refactoring(commits, plans)
    emerging = detect_emerging(commits, plans)
    scaffolding = detect_scaffolding(commits, plans)
    tension = detect_tension(commits, plans)

    return ConceptualWeather(
        refactoring=tuple(refactoring),
        emerging=tuple(emerging),
        scaffolding=tuple(scaffolding),
        tension=tuple(tension),
        generated_at=datetime.now(),
    )


# =============================================================================
# Async Variant
# =============================================================================


async def generate_weather_async(
    repo_path: Path | str | None = None,
    plans_path: Path | str | None = None,
    since: datetime | None = None,
) -> ConceptualWeather:
    """
    Async version of generate_weather.

    Runs sync operations in thread pool for non-blocking IO.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: generate_weather(
            repo_path=repo_path,
            plans_path=plans_path,
            since=since,
        ),
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "parse_plan_headers",
    "analyze_commit_messages",
    "detect_refactoring",
    "detect_emerging",
    "detect_scaffolding",
    "detect_tension",
    "generate_weather",
    "generate_weather_async",
]
