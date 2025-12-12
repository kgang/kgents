"""
Forest Protocol Handler - Manages plan forest health and generation.

Commands:
- kgents forest status  → Show forest health summary
- kgents forest update  → Regenerate _forest.md from plan headers

The Forest Protocol ensures heterarchical attention across all plans,
preventing "king projects" from dominating sessions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PlanHeader:
    """Parsed YAML header from a plan file."""

    path: str
    status: str  # dormant | blocked | active | complete
    progress: int  # 0-100
    last_touched: str
    touched_by: str
    blocking: list[str] = field(default_factory=list)
    enables: list[str] = field(default_factory=list)
    session_notes: str = ""
    file_path: Path = field(default_factory=lambda: Path("."))

    @property
    def days_since_touched(self) -> int:
        """Days since last touched."""
        try:
            touched = datetime.strptime(self.last_touched, "%Y-%m-%d")
            return (datetime.now() - touched).days
        except (ValueError, TypeError):
            return 999


def find_kgents_root() -> Path:
    """Find the kgents project root."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "CLAUDE.md").exists() and (current / "plans").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find kgents project root")


def parse_yaml_header(file_path: Path) -> PlanHeader | None:
    """Parse YAML frontmatter from a plan file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    # Match YAML frontmatter
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    try:
        data: dict[str, Any] = yaml.safe_load(match.group(1))
        if not isinstance(data, dict):
            return None
    except yaml.YAMLError:
        return None

    # Required fields
    if "path" not in data or "status" not in data:
        return None

    return PlanHeader(
        path=data.get("path", ""),
        status=data.get("status", "dormant"),
        progress=int(data.get("progress", 0)),
        last_touched=str(data.get("last_touched", "")),
        touched_by=data.get("touched_by", "unknown"),
        blocking=data.get("blocking", []) or [],
        enables=data.get("enables", []) or [],
        session_notes=data.get("session_notes", ""),
        file_path=file_path,
    )


def scan_plans(plans_dir: Path) -> list[PlanHeader]:
    """Scan all plans and parse their headers."""
    plans: list[PlanHeader] = []

    # Skip meta files and archive
    skip_patterns = {"_forest.md", "_status.md", "README.md", "principles.md"}

    for md_file in plans_dir.rglob("*.md"):
        # Skip archive and meta files
        if "_archive" in str(md_file):
            continue
        if md_file.name in skip_patterns:
            continue
        if md_file.name.startswith("_"):
            continue

        header = parse_yaml_header(md_file)
        if header:
            plans.append(header)

    return plans


def generate_forest_md(plans: list[PlanHeader]) -> str:
    """Generate _forest.md content from plan headers."""
    today = date.today().isoformat()

    # Categorize plans
    active = [p for p in plans if p.status == "active"]
    blocked = [p for p in plans if p.status == "blocked"]
    dormant = [p for p in plans if p.status == "dormant"]
    complete = [p for p in plans if p.status == "complete"]

    # Sort by progress (descending) then path
    active.sort(key=lambda p: (-p.progress, p.path))
    dormant.sort(key=lambda p: (-p.days_since_touched, p.path))

    # Calculate metrics
    total = len(plans)
    avg_progress = sum(p.progress for p in plans) // max(total, 1)
    longest_untouched = max(dormant, key=lambda p: p.days_since_touched) if dormant else None

    # Find next accursed share candidate (oldest dormant)
    accursed_next = dormant[0].path if dormant else "none"

    lines = [
        f"# Forest Health: {today}",
        "",
        '> *"A single mighty oak casts too much shadow. We cultivate a forest where many trees grow."*',
        "",
        "This file provides a canopy view of all active plans. Read this at session start.",
        "",
        "---",
        "",
        "## Active Trees",
        "",
        "| Plan | Progress | Last Touched | Status | Notes |",
        "|------|----------|--------------|--------|-------|",
    ]

    for p in active:
        notes = p.session_notes.split("\n")[0][:50] if p.session_notes else ""
        lines.append(f"| {p.path} | {p.progress}% | {p.last_touched} | {p.status} | {notes} |")

    if not active:
        lines.append("| (none) | - | - | - | - |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Blocked Trees",
            "",
            "| Plan | Progress | Blocked By | Since | Notes |",
            "|------|----------|------------|-------|-------|",
        ]
    )

    for p in blocked:
        blockers = ", ".join(p.blocking) if p.blocking else "unknown"
        notes = p.session_notes.split("\n")[0][:40] if p.session_notes else ""
        lines.append(f"| {p.path} | {p.progress}% | {blockers} | {p.last_touched} | {notes} |")

    if not blocked:
        lines.append("| (none) | - | - | - | - |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Dormant Trees (Awaiting Accursed Share)",
            "",
            "| Plan | Progress | Last Touched | Days Since | Suggested Action |",
            "|------|----------|--------------|------------|------------------|",
        ]
    )

    for p in dormant:
        if p.days_since_touched > 7:
            action = "Needs attention"
        elif p.progress > 0:
            action = "Continue work"
        else:
            action = "Read spec, draft approach"
        lines.append(f"| {p.path} | {p.progress}% | {p.last_touched} | {p.days_since_touched} | {action} |")

    if not dormant:
        lines.append("| (none) | - | - | - | - |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Complete Trees",
            "",
            "| Plan | Completed | Notes |",
            "|------|-----------|-------|",
        ]
    )

    for p in complete:
        notes = p.session_notes.split("\n")[0][:60] if p.session_notes else "Done"
        lines.append(f"| {p.path} | {p.last_touched} | {notes} |")

    if not complete:
        lines.append("| (none) | - | - |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Session Attention Budget (Suggested)",
            "",
            "Per `plans/principles.md` §3:",
            "",
            "```",
            "Primary Focus (60%):    [your choice from Active Trees]",
            "Secondary (25%):        [another Active Tree]",
            "Maintenance (10%):      [check in on Blocked/Dormant]",
            f"Accursed Share (5%):    {accursed_next} (rotation)",
            "```",
            "",
            "---",
            "",
            "## Forest Metrics",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total trees | {total} |",
            f"| Active | {len(active)} ({len(active)*100//max(total,1)}%) |",
            f"| Dormant | {len(dormant)} ({len(dormant)*100//max(total,1)}%) |",
            f"| Blocked | {len(blocked)} ({len(blocked)*100//max(total,1)}%) |",
            f"| Complete | {len(complete)} ({len(complete)*100//max(total,1)}%) |",
            f"| Average progress | {avg_progress}% |",
        ]
    )

    if longest_untouched:
        lines.append(f"| Longest untouched | {longest_untouched.path} ({longest_untouched.days_since_touched} days) |")

    lines.append(f"| Accursed share next | {accursed_next} |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Dependency Graph",
            "",
            "```",
        ]
    )

    # Build dependency graph
    for p in plans:
        if p.enables:
            for enabled in p.enables:
                lines.append(f"{p.path} ({p.progress}%) ──enables──▶ {enabled}")
        if p.blocking and p.status == "blocked":
            for blocker in p.blocking:
                lines.append(f"{p.path} ({p.progress}%) ◀── blocked by ── {blocker}")

    # Show dormant trees needing attention
    for p in dormant:
        if p.days_since_touched > 5:
            lines.append(f"{p.path} ({p.progress}%) ◀── needs attention ── [{p.days_since_touched} days dormant]")

    lines.extend(
        [
            "```",
            "",
            "---",
            "",
            "## Quick Reference",
            "",
            "```bash",
            "# Read session principles",
            "cat plans/principles.md",
            "",
            "# Read specific plan",
            "cat plans/<path>.md",
            "",
            "# Check detailed status",
            "cat plans/_status.md",
            "",
            "# Read last epilogue",
            "ls -la plans/_epilogues/",
            "",
            "# After session: write epilogue",
            "# plans/_epilogues/YYYY-MM-DD-<session>.md",
            "```",
            "",
            "---",
            "",
            "## Last Session Epilogue",
            "",
        ]
    )

    # Find most recent epilogue
    root = find_kgents_root()
    epilogues_dir = root / "plans" / "_epilogues"
    if epilogues_dir.exists():
        epilogues = sorted(epilogues_dir.glob("*.md"), reverse=True)
        if epilogues:
            latest = epilogues[0]
            lines.append(f"*Latest: `{latest.name}`*")
        else:
            lines.append("*No epilogues yet.*")
    else:
        lines.append("*Epilogues directory not found.*")

    lines.extend(
        [
            "",
            "---",
            "",
            '*"Plans are worthless, but planning is everything." — Eisenhower*',
            "",
        ]
    )

    return "\n".join(lines)


def forest_status() -> str:
    """Get forest health summary."""
    root = find_kgents_root()
    plans_dir = root / "plans"
    plans = scan_plans(plans_dir)

    active = [p for p in plans if p.status == "active"]
    blocked = [p for p in plans if p.status == "blocked"]
    dormant = [p for p in plans if p.status == "dormant"]
    complete = [p for p in plans if p.status == "complete"]

    lines = [
        "Forest Health Summary",
        "=" * 40,
        f"Active:   {len(active):>3} trees",
        f"Dormant:  {len(dormant):>3} trees",
        f"Blocked:  {len(blocked):>3} trees",
        f"Complete: {len(complete):>3} trees",
        "-" * 40,
    ]

    if active:
        lines.append("\nActive Trees:")
        for p in active:
            lines.append(f"  • {p.path} ({p.progress}%)")

    if blocked:
        lines.append("\nBlocked Trees:")
        for p in blocked:
            blockers = ", ".join(p.blocking) if p.blocking else "unknown"
            lines.append(f"  • {p.path} (by {blockers})")

    if dormant:
        oldest = max(dormant, key=lambda p: p.days_since_touched)
        lines.append(f"\nAccursed Share Candidate: {oldest.path} ({oldest.days_since_touched} days)")

    return "\n".join(lines)


def forest_update() -> str:
    """Update _forest.md from plan headers."""
    root = find_kgents_root()
    plans_dir = root / "plans"
    plans = scan_plans(plans_dir)

    if not plans:
        return "No plans with YAML headers found."

    content = generate_forest_md(plans)
    forest_path = plans_dir / "_forest.md"
    forest_path.write_text(content, encoding="utf-8")

    return f"Updated {forest_path} with {len(plans)} plans."


def forest_check() -> tuple[bool, str]:
    """Check if _forest.md is up-to-date. Returns (is_current, message)."""
    root = find_kgents_root()
    plans_dir = root / "plans"
    plans = scan_plans(plans_dir)

    if not plans:
        return False, "No plans with YAML headers found."

    # Check for plans without headers
    all_plan_files = list(plans_dir.rglob("*.md"))
    skip_patterns = {"_forest.md", "_status.md", "README.md", "principles.md"}
    missing_headers: list[str] = []

    for md_file in all_plan_files:
        if "_archive" in str(md_file):
            continue
        if "_epilogues" in str(md_file):
            continue  # Epilogues are session notes, not plans
        if md_file.name in skip_patterns:
            continue
        if md_file.name.startswith("_"):
            continue
        header = parse_yaml_header(md_file)
        if not header:
            missing_headers.append(str(md_file.relative_to(root)))

    if missing_headers:
        return False, f"Plans missing YAML headers: {', '.join(missing_headers)}"

    # Check if _forest.md would change
    new_content = generate_forest_md(plans)
    forest_path = plans_dir / "_forest.md"

    if not forest_path.exists():
        return False, "_forest.md does not exist. Run 'forest update' to create it."

    current_content = forest_path.read_text(encoding="utf-8")

    # Compare ignoring the date line (first line changes daily)
    new_lines = new_content.split("\n")[1:]  # Skip "# Forest Health: YYYY-MM-DD"
    current_lines = current_content.split("\n")[1:]

    if new_lines != current_lines:
        return False, "_forest.md is stale. Run 'forest update' to refresh it."

    # Check for stale plans (>7 days untouched)
    stale_plans = [p for p in plans if p.days_since_touched > 7 and p.status != "complete"]
    if stale_plans:
        stale_list = ", ".join(f"{p.path} ({p.days_since_touched}d)" for p in stale_plans)
        return True, f"WARNING: Stale plans need attention: {stale_list}"

    return True, f"Forest is healthy. {len(plans)} plans tracked."


def forest_lint() -> tuple[bool, str]:
    """Lint all plan headers for required fields."""
    root = find_kgents_root()
    plans_dir = root / "plans"
    plans = scan_plans(plans_dir)

    required_fields = ["path", "status", "progress", "last_touched"]
    issues: list[str] = []

    for plan in plans:
        if not plan.path:
            issues.append(f"{plan.file_path}: missing 'path' field")
        if plan.status not in ("dormant", "blocked", "active", "complete"):
            issues.append(f"{plan.path}: invalid status '{plan.status}'")
        if not (0 <= plan.progress <= 100):
            issues.append(f"{plan.path}: progress {plan.progress} out of range [0-100]")

    if issues:
        return False, "Header lint failures:\n  " + "\n  ".join(issues)

    return True, f"All {len(plans)} plan headers valid."


def cmd_forest(args: list[str] | None = None) -> int:
    """
    Forest Protocol CLI command.

    Usage:
        kgents forest           Show forest health summary
        kgents forest update    Regenerate _forest.md from plan headers
        kgents forest check     Check for missing headers or stale _forest.md (CI)
        kgents forest lint      Validate all plan header fields

    The Forest Protocol ensures heterarchical attention across all plans,
    preventing "king projects" from dominating sessions.
    """
    args = args or []

    if not args or args[0] in ("status", ""):
        print(forest_status())
        return 0
    elif args[0] == "update":
        print(forest_update())
        return 0
    elif args[0] == "check":
        ok, msg = forest_check()
        print(msg)
        return 0 if ok else 1
    elif args[0] == "lint":
        ok, msg = forest_lint()
        print(msg)
        return 0 if ok else 1
    elif args[0] in ("--help", "-h", "help"):
        print(cmd_forest.__doc__)
        return 0
    else:
        print(f"Unknown subcommand: {args[0]}")
        print("Usage: kgents forest [status|update|check|lint]")
        return 1


if __name__ == "__main__":
    import sys

    exit_code = cmd_forest(sys.argv[1:])
    sys.exit(exit_code)
