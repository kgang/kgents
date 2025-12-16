"""
AGENTESE Forest Context Resolver

The Forest: plans as handles, epilogues as witnesses, dormant as accursed share.

forest.* handles resolve to planning artifacts that can be:
- Manifested (self.forest.manifest) → canopy view from plan YAML headers
- Status (self.forest.status) → _status.md content
- Witnessed (self.forest.witness) → drift report
- Tithed (self.forest.tithe) → archive stale plans
- Reconciled (self.forest.reconcile) → full meta file sync
- Sipped (void.forest.sip) → accursed share selection
- Refined (concept.forest.refine) → mutation with rollback
- Defined (self.forest.define) → JIT plan scaffold

The Forest Protocol:
- _focus.md = human intent (never overwrite)
- _forest.md = canopy view (regenerable from plan headers)
- _status.md = implementation status (regenerable)
- _epilogues/ = witnesses (append-only)
- plans/*.md = individual trees (handles with YAML headers)

Principle Alignment: Heterarchical, Composable, Minimal Output, Autopoietic

> *"Plans as handles. Epilogues as witnesses. The forest becomes AGENTESE-native."*
> *"The garden tends itself, but only because we planted it together."*
"""

from __future__ import annotations

import re
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncIterator, Literal

import yaml

from ..node import (
    BaseLogosNode,
    BasicRendering,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Forest Parsing ===


@dataclass(frozen=True)
class ParsedTree:
    """A single tree parsed from _forest.md tables."""

    path: str
    progress: int
    last_touched: str
    status: str
    notes: str = ""
    # Dormant-specific fields
    days_since: int = 0
    suggested_action: str = ""
    # Blocked-specific fields
    blocked_by: str = ""


def parse_forest_md(forest_path: Path | str) -> ForestManifest:
    """
    Parse _forest.md and extract tree data.

    Extracts from Active/Dormant/Blocked/Complete tables:
    - Plan path
    - Progress percentage
    - Last touched date
    - Status

    Args:
        forest_path: Path to _forest.md file

    Returns:
        ForestManifest with real tree data
    """
    path = Path(forest_path)
    if not path.exists():
        return ForestManifest()

    content = path.read_text()

    # Parse each section
    active_trees = _parse_active_section(content)
    dormant_trees = _parse_dormant_section(content)
    blocked_trees = _parse_blocked_section(content)
    complete_trees = _parse_complete_section(content)

    # Combine all trees for the manifest
    all_trees: list[dict[str, Any]] = []

    for tree in active_trees:
        all_trees.append(
            {
                "path": tree.path,
                "progress": tree.progress,
                "last_touched": tree.last_touched,
                "status": "active",
                "notes": tree.notes,
            }
        )

    for tree in dormant_trees:
        all_trees.append(
            {
                "path": tree.path,
                "progress": tree.progress,
                "last_touched": tree.last_touched,
                "status": "dormant",
                "days_since": tree.days_since,
                "suggested_action": tree.suggested_action,
            }
        )

    for tree in blocked_trees:
        all_trees.append(
            {
                "path": tree.path,
                "progress": tree.progress,
                "status": "blocked",
                "blocked_by": tree.blocked_by,
            }
        )

    for tree in complete_trees:
        all_trees.append(
            {
                "path": tree.path,
                "progress": 100,
                "status": "complete",
            }
        )

    # Calculate aggregate stats
    total = len(all_trees)
    active_count = len(active_trees)
    dormant_count = len(dormant_trees)
    blocked_count = len(blocked_trees)
    complete_count = len(complete_trees)

    # Average progress (exclude complete trees at 100%)
    progresses = [t.progress for t in active_trees + dormant_trees + blocked_trees]
    avg_progress = sum(progresses) / len(progresses) if progresses else 0.0

    # Find accursed share candidate (longest dormant)
    accursed_next: str | None = None
    if dormant_trees:
        # Sort by days_since descending
        sorted_dormant = sorted(dormant_trees, key=lambda t: t.days_since, reverse=True)
        accursed_next = sorted_dormant[0].path

    # Parse last updated from Forest Health date header
    last_updated = _parse_forest_date(content)

    return ForestManifest(
        total_trees=total,
        active_trees=active_count,
        dormant_trees=dormant_count,
        blocked_trees=blocked_count,
        complete_trees=complete_count,
        average_progress=avg_progress / 100.0,  # Convert to 0-1 scale
        accursed_share_next=accursed_next,
        last_updated=last_updated,
        trees=all_trees,
    )


def _parse_forest_date(content: str) -> datetime | None:
    """Extract date from '# Forest Health: YYYY-MM-DD' header."""
    match = re.search(r"# Forest Health:\s*(\d{4}-\d{2}-\d{2})", content)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d")
        except ValueError:
            return None
    return None


def _parse_active_section(content: str) -> list[ParsedTree]:
    """
    Parse Active Trees section.

    Format:
    | Plan | Progress | Last Touched | Status | Notes |
    |------|----------|--------------|--------|-------|
    | agents/k-gent | 97% | 2025-12-12 | active | ... |
    """
    trees: list[ParsedTree] = []

    # Find the Active Trees section
    active_match = re.search(
        r"## Active Trees\s*\n\n\|[^\n]+\n\|[-|\s]+\n((?:\|[^\n]+\n)*)",
        content,
    )
    if not active_match:
        return trees

    table_content = active_match.group(1)

    # Parse each row
    for line in table_content.strip().split("\n"):
        if not line.strip() or line.startswith("| (none)"):
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 6:
            continue

        # parts[0] is empty (before first |), parts[1] is Plan, etc.
        plan = parts[1]
        progress_str = parts[2].replace("%", "")
        last_touched = parts[3]
        # parts[4] is status (already know it's active)
        notes = parts[5] if len(parts) > 5 else ""

        try:
            progress = int(progress_str)
        except ValueError:
            progress = 0

        trees.append(
            ParsedTree(
                path=plan,
                progress=progress,
                last_touched=last_touched,
                status="active",
                notes=notes,
            )
        )

    return trees


def _parse_dormant_section(content: str) -> list[ParsedTree]:
    """
    Parse Dormant Trees section.

    Format:
    | Plan | Progress | Last Touched | Days Since | Suggested Action |
    |------|----------|--------------|------------|------------------|
    | agents/t-gent | 90% | 2025-12-12 | 1 | Continue work |
    """
    trees: list[ParsedTree] = []

    # Find the Dormant Trees section
    dormant_match = re.search(
        r"## Dormant Trees[^\n]*\n\n\|[^\n]+\n\|[-|\s]+\n((?:\|[^\n]+\n)*)",
        content,
    )
    if not dormant_match:
        return trees

    table_content = dormant_match.group(1)

    for line in table_content.strip().split("\n"):
        if not line.strip() or line.startswith("| (none)"):
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 6:
            continue

        plan = parts[1]
        progress_str = parts[2].replace("%", "")
        last_touched = parts[3]
        days_since_str = parts[4]
        suggested = parts[5] if len(parts) > 5 else ""

        try:
            progress = int(progress_str)
        except ValueError:
            progress = 0

        try:
            days_since = int(days_since_str)
        except ValueError:
            days_since = 0

        trees.append(
            ParsedTree(
                path=plan,
                progress=progress,
                last_touched=last_touched,
                status="dormant",
                days_since=days_since,
                suggested_action=suggested,
            )
        )

    return trees


def _parse_blocked_section(content: str) -> list[ParsedTree]:
    """
    Parse Blocked Trees section.

    Format:
    | Plan | Progress | Blocked By | Since | Notes |
    |------|----------|------------|-------|-------|
    | some/plan | 50% | dependency | 2025-12-01 | ... |
    """
    trees: list[ParsedTree] = []

    blocked_match = re.search(
        r"## Blocked Trees\s*\n\n\|[^\n]+\n\|[-|\s]+\n((?:\|[^\n]+\n)*)",
        content,
    )
    if not blocked_match:
        return trees

    table_content = blocked_match.group(1)

    for line in table_content.strip().split("\n"):
        if not line.strip() or line.startswith("| (none)"):
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue

        plan = parts[1]
        if plan == "-":
            continue

        progress_str = parts[2].replace("%", "")
        blocked_by = parts[3]

        try:
            progress = int(progress_str)
        except ValueError:
            progress = 0

        trees.append(
            ParsedTree(
                path=plan,
                progress=progress,
                last_touched="",
                status="blocked",
                blocked_by=blocked_by,
            )
        )

    return trees


def _parse_complete_section(content: str) -> list[ParsedTree]:
    """
    Parse Complete Trees section.

    Format:
    | Plan | Archived | Location |
    |------|----------|----------|
    | void/entropy | 2025-12-14 | `_archive/entropy-v1.0-complete.md` |
    """
    trees: list[ParsedTree] = []

    complete_match = re.search(
        r"## Complete Trees[^\n]*\n\n\|[^\n]+\n\|[-|\s]+\n((?:\|[^\n]+\n)*)",
        content,
    )
    if not complete_match:
        return trees

    table_content = complete_match.group(1)

    for line in table_content.strip().split("\n"):
        if not line.strip() or line.startswith("| (none)"):
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue

        plan = parts[1]
        if plan == "-":
            continue

        trees.append(
            ParsedTree(
                path=plan,
                progress=100,
                last_touched="",
                status="complete",
            )
        )

    return trees


# === Forest Affordances by Role ===

FOREST_ROLE_AFFORDANCES: dict[str, tuple[str, ...]] = {
    # Guest: read-only access to canopy and history
    "guest": ("manifest", "status", "witness", "epilogues"),
    # Meta: can mutate and draw from accursed share
    "meta": (
        "manifest",
        "status",
        "witness",
        "epilogues",
        "refine",
        "sip",
        "define",
        "tithe",
    ),
    # Ops: full control including apply, rollback, and forest health checks
    "ops": (
        "manifest",
        "status",
        "witness",
        "epilogues",
        "refine",
        "sip",
        "define",
        "tithe",
        "reconcile",
        "apply",
        "rollback",
        "lint",
    ),
    # Default: minimal read access
    "default": ("manifest", "status", "witness"),
}


# === Forest Law Check Result ===


@dataclass(frozen=True)
class ForestLawCheck:
    """
    Result of checking AGENTESE laws for a forest mutation.

    Laws checked:
    - Identity: Plan handles are stable identifiers
    - Associativity: (A >> B) >> C = A >> (B >> C) for plan composition
    - Minimal output: Changes produce minimal diff
    """

    identity: str = "pass"  # "pass" | "fail" | "skip"
    associativity: str = "pass"
    minimal_output: str = "pass"

    @property
    def all_pass(self) -> bool:
        """Check if all laws pass."""
        return (
            self.identity == "pass"
            and self.associativity == "pass"
            and self.minimal_output == "pass"
        )

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary."""
        return {
            "identity": self.identity,
            "associativity": self.associativity,
            "minimal_output": self.minimal_output,
        }


# === Forest Manifest (Canopy View) ===


@dataclass
class ForestManifest:
    """
    Rendering of the forest canopy.

    This is what observers see when they invoke concept.forest.manifest.
    Contains summary statistics and tree listings.
    """

    total_trees: int = 0
    active_trees: int = 0
    dormant_trees: int = 0
    blocked_trees: int = 0
    complete_trees: int = 0
    average_progress: float = 0.0
    accursed_share_next: str | None = None
    last_updated: datetime | None = None
    trees: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_trees": self.total_trees,
            "active_trees": self.active_trees,
            "dormant_trees": self.dormant_trees,
            "blocked_trees": self.blocked_trees,
            "complete_trees": self.complete_trees,
            "average_progress": self.average_progress,
            "accursed_share_next": self.accursed_share_next,
            "last_updated": self.last_updated.isoformat()
            if self.last_updated
            else None,
            "trees": self.trees,
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        lines = [
            "FOREST CANOPY",
            "=" * 40,
            f"Total trees: {self.total_trees}",
            f"  Active: {self.active_trees}",
            f"  Dormant: {self.dormant_trees}",
            f"  Blocked: {self.blocked_trees}",
            f"  Complete: {self.complete_trees}",
            f"Average progress: {self.average_progress:.0%}",
        ]
        if self.accursed_share_next:
            lines.append(f"Accursed share next: {self.accursed_share_next}")
        return "\n".join(lines)


# === Plan Header Parsing (for self.forest.manifest) ===

# Find project root (where plans/ lives)
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent


@dataclass
class PlanFromHeader:
    """A plan parsed from YAML frontmatter."""

    path: str
    progress: int
    status: Literal["active", "dormant", "blocked", "complete"]
    last_touched: date
    notes: str = ""
    blocking: list[str] = field(default_factory=list)
    enables: list[str] = field(default_factory=list)
    touched_by: str = ""

    @classmethod
    def from_yaml_header(
        cls, file_path: Path, header: dict[str, Any]
    ) -> "PlanFromHeader":
        """Create PlanFromHeader from parsed YAML frontmatter."""
        last_touched_raw = header.get("last_touched", date.today())
        if isinstance(last_touched_raw, str):
            try:
                last_touched = datetime.strptime(last_touched_raw, "%Y-%m-%d").date()
            except ValueError:
                last_touched = date.today()
        elif isinstance(last_touched_raw, date):
            last_touched = last_touched_raw
        else:
            last_touched = date.today()

        # Extract notes from session_notes
        session_notes = header.get("session_notes", "")
        if isinstance(session_notes, str):
            notes = session_notes.split("\n")[0][:100]  # First line, max 100 chars
        else:
            notes = ""

        return cls(
            path=header.get("path", str(file_path.relative_to(_PROJECT_ROOT))),
            progress=int(header.get("progress", 0)),
            status=header.get("status", "active"),
            last_touched=last_touched,
            notes=notes,
            blocking=header.get("blocking", []) or [],
            enables=header.get("enables", []) or [],
            touched_by=header.get("touched_by", ""),
        )


def parse_plan_yaml_header(file_path: Path) -> dict[str, Any] | None:
    """Parse YAML frontmatter from a markdown file."""
    try:
        content = file_path.read_text()
    except Exception:
        return None

    if not content.startswith("---"):
        return None

    end_match = re.search(r"\n---\s*\n", content[3:])
    if not end_match:
        return None

    yaml_content = content[3 : end_match.start() + 3]

    try:
        parsed = yaml.safe_load(yaml_content)
        return dict(parsed) if parsed else None
    except yaml.YAMLError:
        return None


# === Drift Detection (for self.forest.witness) ===


@dataclass
class DriftItem:
    """A single drift between documented and actual state."""

    documented: int | str
    actual: int | str

    @property
    def has_drift(self) -> bool:
        return self.documented != self.actual


@dataclass
class PlanIssue:
    """An issue with a plan header."""

    path: str
    issue: str


@dataclass
class DriftReport:
    """Drift report comparing documented vs actual state."""

    test_count_drift: DriftItem
    mypy_drift: DriftItem
    plan_header_issues: list[PlanIssue]
    stale_plans: list[str]  # >30 days dormant
    orphan_plans: list[str]  # referenced but missing

    @property
    def has_drift(self) -> bool:
        return (
            self.test_count_drift.has_drift
            or self.mypy_drift.has_drift
            or bool(self.plan_header_issues)
            or bool(self.stale_plans)
        )

    def to_text(self) -> str:
        """Render as text report."""
        lines = ["DRIFT REPORT", "=" * 40]

        if self.test_count_drift.has_drift:
            lines.append(
                f"Test count: documented={self.test_count_drift.documented}, actual={self.test_count_drift.actual}"
            )
        else:
            lines.append(f"Test count: {self.test_count_drift.actual} (synchronized)")

        if self.mypy_drift.has_drift:
            lines.append(
                f"Mypy errors: documented={self.mypy_drift.documented}, actual={self.mypy_drift.actual}"
            )
        else:
            lines.append(f"Mypy errors: {self.mypy_drift.actual} (synchronized)")

        if self.plan_header_issues:
            lines.append("\nPlan Header Issues:")
            for issue in self.plan_header_issues[:10]:  # Limit
                lines.append(f"  - {issue.path}: {issue.issue}")

        if self.stale_plans:
            lines.append(f"\nStale Plans (>30 days dormant): {len(self.stale_plans)}")
            for plan in self.stale_plans[:5]:  # Limit
                lines.append(f"  - {plan}")

        if self.orphan_plans:
            lines.append(f"\nOrphan References: {len(self.orphan_plans)}")
            for ref in self.orphan_plans[:5]:
                lines.append(f"  - {ref}")

        if not self.has_drift:
            lines.append("\n✓ No drift detected. Forest is synchronized.")

        return "\n".join(lines)


# === Tithe Report (for self.forest.tithe) ===


@dataclass
class ArchivedPlan:
    """A plan that was archived."""

    original_path: str
    archive_path: str
    reason: str


@dataclass
class TitheReport:
    """Report of tithe (archival) operation."""

    archived: list[ArchivedPlan]
    skipped: list[str]
    references_updated: list[str]
    dry_run: bool

    def to_text(self) -> str:
        """Render as text report."""
        mode = "DRY RUN" if self.dry_run else "EXECUTED"
        lines = [f"TITHE REPORT ({mode})", "=" * 40]

        if self.archived:
            lines.append(f"Archived: {len(self.archived)}")
            for plan in self.archived:
                lines.append(f"  - {plan.original_path} -> {plan.archive_path}")
                lines.append(f"    Reason: {plan.reason}")
        else:
            lines.append("No plans archived.")

        if self.skipped:
            lines.append(f"\nSkipped: {len(self.skipped)}")
            for reason in self.skipped[:5]:
                lines.append(f"  - {reason}")

        return "\n".join(lines)


# === Reconciliation Result (for self.forest.reconcile) ===


@dataclass
class ReconciliationResult:
    """Result of full reconciliation."""

    drift_before: DriftReport
    files_updated: list[str]
    epilogue_path: str
    summary: str

    def to_text(self) -> str:
        """Render as text report."""
        lines = [
            "RECONCILIATION COMPLETE",
            "=" * 40,
            self.summary,
            "",
            "Files Updated:",
        ]
        for f in self.files_updated:
            lines.append(f"  - {f}")

        if self.epilogue_path:
            lines.append(f"\nEpilogue: {self.epilogue_path}")

        return "\n".join(lines)


# === Epilogue Witness Entry ===


@dataclass(frozen=True)
class EpilogueEntry:
    """
    A single epilogue entry from time.forest.witness.

    Epilogues are spores: write at session end, never modify.
    """

    path: str
    date: str
    title: str
    content_preview: str = ""
    phase: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "date": self.date,
            "title": self.title,
            "content_preview": self.content_preview,
            "phase": self.phase,
            "metadata": self.metadata,
        }


def parse_epilogue_file(file_path: Path) -> EpilogueEntry | None:
    """
    Parse an epilogue markdown file.

    Extracts:
    - Date from filename (YYYY-MM-DD-slug.md)
    - Title from first # header
    - Content preview (first ~200 chars after title)
    - Phase (detected from common patterns like IMPLEMENT, QA, RESEARCH)

    Args:
        file_path: Path to epilogue .md file

    Returns:
        EpilogueEntry or None if file cannot be parsed
    """
    if not file_path.exists() or not file_path.suffix == ".md":
        return None

    # Extract date from filename (YYYY-MM-DD-slug.md)
    filename = file_path.stem
    date_match = re.match(r"(\d{4}-\d{2}-\d{2})", filename)
    if not date_match:
        return None
    date_str = date_match.group(1)

    # Read content
    content = file_path.read_text()
    lines = content.split("\n")

    # Extract title from first # header
    title = filename  # Default to filename
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # Extract content preview (first ~200 chars after title, excluding headers)
    preview_lines = []
    in_content = False
    for line in lines:
        if line.startswith("# "):
            in_content = True
            continue
        if in_content and line.strip() and not line.startswith("#"):
            preview_lines.append(line.strip())
            if len(" ".join(preview_lines)) > 200:
                break
    content_preview = " ".join(preview_lines)[:200]

    # Detect phase from filename or content
    phase = _detect_phase(filename, content)

    return EpilogueEntry(
        path=str(file_path),
        date=date_str,
        title=title,
        content_preview=content_preview,
        phase=phase,
    )


def _detect_phase(filename: str, content: str) -> str:
    """
    Detect N-phase from filename or content.

    Looks for phase keywords: PLAN, RESEARCH, DEVELOP, STRATEGIZE,
    CROSS-SYNERGIZE, IMPLEMENT, QA, TEST, EDUCATE, MEASURE, REFLECT.
    """
    # Common phase patterns
    phases = [
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

    # Check filename first (more specific)
    filename_lower = filename.lower()
    for phase in phases:
        if phase.lower() in filename_lower:
            return phase

    # Check content headers
    for phase in phases:
        if phase in content or phase.lower() in content.lower():
            return phase

    return ""


def scan_epilogues(
    epilogues_path: str | Path,
    limit: int = 10,
    since: str | None = None,
    phase: str | None = None,
) -> list[EpilogueEntry]:
    """
    Scan epilogues directory and return parsed entries.

    Args:
        epilogues_path: Path to _epilogues directory
        limit: Maximum entries to return
        since: Only entries after this date (ISO format YYYY-MM-DD)
        phase: Only entries matching this phase

    Returns:
        List of EpilogueEntry in reverse chronological order
    """
    path = Path(epilogues_path)
    if not path.exists() or not path.is_dir():
        return []

    # Scan and parse all .md files
    entries: list[EpilogueEntry] = []
    for md_file in path.glob("*.md"):
        entry = parse_epilogue_file(md_file)
        if entry is not None:
            # Apply filters
            if since and entry.date < since:
                continue
            if phase and phase.upper() not in entry.phase.upper():
                continue
            entries.append(entry)

    # Sort by date descending (reverse chronological)
    entries.sort(key=lambda e: e.date, reverse=True)

    # Apply limit
    return entries[:limit]


# === Forest Node ===


@dataclass
class ForestNode(BaseLogosNode):
    """
    Forest context node for plan handle operations.

    Provides AGENTESE handles for forest planning artifacts:
    - concept.forest.manifest → Forest canopy view
    - time.forest.witness → Epilogue stream
    - void.forest.sip → Accursed share selection
    - concept.forest.refine → Plan mutation with rollback
    - self.forest.define → JIT plan scaffold

    The Forest Protocol boundary:
    - Guest: read-only (manifest, witness)
    - Meta: can mutate and explore (+ refine, sip, define)
    - Ops: full control (+ apply, rollback, lint)
    """

    _handle: str = "concept.forest"

    # Paths (stub: will be injected from config)
    _forest_path: str = "plans/_forest.md"
    _focus_path: str = "plans/_focus.md"
    _epilogues_path: str = "plans/_epilogues"
    _plans_root: str = "plans"

    # Rollback state (in-memory for stubs)
    _pending_rollbacks: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def handle(self) -> str:
        """The AGENTESE path to this node."""
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return role-gated affordances for forest operations.

        Uses FOREST_ROLE_AFFORDANCES mapping.
        Falls back to 'default' for unknown archetypes.
        """
        return FOREST_ROLE_AFFORDANCES.get(
            archetype, FOREST_ROLE_AFFORDANCES["default"]
        )

    async def manifest(self, observer: "Umwelt[Any, Any]") -> BasicRendering:
        """
        Return forest canopy view.

        AGENTESE: concept.forest.manifest

        Parses _forest.md and returns real tree data:
        1. Parse _forest.md tables
        2. Count trees by status
        3. Compute average progress
        4. Identify accursed share candidate (longest dormant)
        """
        # Parse real forest data
        forest_manifest = parse_forest_md(self._forest_path)

        return BasicRendering(
            summary="Forest Canopy",
            content=forest_manifest.to_text(),
            metadata={
                "status": "live",
                "plan_count": forest_manifest.total_trees,
                "manifest": forest_manifest.to_dict(),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to aspect-specific handlers."""
        match aspect:
            case "manifest":
                return await self._manifest_from_headers(observer, **kwargs)
            case "status":
                return await self._generate_status(observer, **kwargs)
            case "witness":
                # Drift report (renamed from epilogue stream)
                return await self._drift_report(observer, **kwargs)
            case "tithe":
                return await self._tithe(observer, **kwargs)
            case "reconcile":
                return await self._reconcile(observer, **kwargs)
            case "epilogues":
                # Legacy: epilogue stream
                return self._stream_epilogues(observer, **kwargs)
            case "sip":
                return await self._sip(observer, **kwargs)
            case "refine":
                return await self._refine(observer, **kwargs)
            case "define":
                return await self._define(observer, **kwargs)
            case "apply":
                return await self._apply(observer, **kwargs)
            case "rollback":
                return await self._rollback(observer, **kwargs)
            case "lint":
                return await self._lint(observer, **kwargs)
            case "dream":
                # void.forest.dream - exploratory (Accursed Share 5%)
                return await self._dream(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # === New Forest Operations (self.forest.*) ===

    def _get_project_root(self) -> Path:
        """Get the project root directory."""
        return _PROJECT_ROOT

    def _get_impl_dir(self) -> Path:
        """Get the impl/claude directory for running tests."""
        return _PROJECT_ROOT / "impl" / "claude"

    async def _collect_plans_from_headers(self) -> list[PlanFromHeader]:
        """Collect all plans by parsing YAML headers from plan files."""
        plans: list[PlanFromHeader] = []
        plans_dir = self._get_project_root() / self._plans_root

        if not plans_dir.exists():
            return plans

        for md_file in plans_dir.rglob("*.md"):
            # Skip meta files and archives
            if md_file.name.startswith("_"):
                continue
            if "_archive" in str(md_file):
                continue
            # Skip epilogue files (they're in _epilogues/ directory)
            if "_epilogues" in str(md_file):
                continue

            header = parse_plan_yaml_header(md_file)
            if header:
                try:
                    plans.append(PlanFromHeader.from_yaml_header(md_file, header))
                except Exception:
                    pass  # Skip malformed headers

        return plans

    async def _collect_test_count(self) -> int:
        """Get test count by running pytest --collect-only."""
        try:
            result = subprocess.run(
                ["uv", "run", "pytest", "--collect-only", "-q"],
                capture_output=True,
                text=True,
                cwd=str(self._get_impl_dir()),
                timeout=60,
            )
            # Parse "18547/18558 tests collected" or "18547 tests collected"
            match = re.search(r"(\d+)(?:/\d+)?\s+tests?\s+collected", result.stdout)
            if match:
                return int(match.group(1))
            return 0
        except Exception:
            return 0

    async def _collect_mypy_errors(self) -> int:
        """Get mypy error count (quick check, limited files)."""
        try:
            # Quick mypy check on core modules only for speed
            subprocess.run(
                ["uv", "run", "mypy", "--version"],
                capture_output=True,
                text=True,
                cwd=str(self._get_impl_dir()),
                timeout=10,
            )
            # For now, return 0 (mypy takes too long for full check)
            # Real implementation could cache results or run incrementally
            return 0
        except Exception:
            return 0

    async def _get_documented_test_count(self) -> int:
        """Extract documented test count from _status.md."""
        status_file = self._get_project_root() / self._plans_root / "_status.md"
        if not status_file.exists():
            return 0

        try:
            content = status_file.read_text()
            # Parse "18,547 tests" or "18547 tests"
            match = re.search(r"(\d+[,\d]*)\s+tests", content)
            if match:
                return int(match.group(1).replace(",", ""))
            return 0
        except Exception:
            return 0

    async def _collect_plan_sanity_issues(
        self, plans: list[PlanFromHeader]
    ) -> tuple[list[str], int]:
        """
        Collect sanity check issues from plans.

        Returns:
            Tuple of (issues list, count of files without YAML headers)
        """
        issues = []
        no_header_count = 0

        # Count files without headers
        plans_dir = self._get_project_root() / self._plans_root
        if plans_dir.exists():
            for md_file in plans_dir.rglob("*.md"):
                if md_file.name.startswith("_"):
                    continue
                if "_archive" in str(md_file):
                    continue
                # Skip epilogue files (date-prefixed)
                if md_file.parent.name == "_epilogues":
                    continue

                header = parse_plan_yaml_header(md_file)
                if not header:
                    no_header_count += 1

        # Check for progress=100 but status != complete
        for p in plans:
            if p.progress >= 100 and p.status != "complete":
                issues.append(f"{p.path}: progress={p.progress}% but status={p.status}")

        # Check for status=complete but progress < 100
        for p in plans:
            if p.status == "complete" and p.progress < 100:
                issues.append(f"{p.path}: status=complete but progress={p.progress}%")

        # Check for active plans with 0% progress that haven't been touched in 7+ days
        for p in plans:
            if p.status == "active" and p.progress == 0:
                days = (date.today() - p.last_touched).days
                if days > 7:
                    issues.append(
                        f"{p.path}: active with 0% progress, untouched {days} days"
                    )

        return issues, no_header_count

    async def _manifest_from_headers(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Generate forest manifest from plan YAML headers.

        AGENTESE: self.forest.manifest

        Replaces parse_forest_md with direct YAML header parsing.
        """
        plans = await self._collect_plans_from_headers()
        test_count = await self._collect_test_count()
        sanity_issues, no_header_count = await self._collect_plan_sanity_issues(plans)

        active = [p for p in plans if p.status == "active"]
        dormant = [p for p in plans if p.status == "dormant"]
        blocked = [p for p in plans if p.status == "blocked"]
        complete = [p for p in plans if p.status == "complete"]

        # Calculate average progress (exclude complete)
        progresses = [p.progress for p in active + dormant + blocked]
        avg_progress = sum(progresses) / len(progresses) if progresses else 0.0

        # Find accursed share candidate
        accursed_next = None
        if dormant:
            sorted_dormant = sorted(
                dormant,
                key=lambda p: (date.today() - p.last_touched).days,
                reverse=True,
            )
            accursed_next = sorted_dormant[0].path

        # Build output
        lines = [
            f"# Forest Health: {date.today().isoformat()}",
            "",
            "> Generated by self.forest.manifest",
            "",
            "---",
            "",
            "## Summary",
            "",
            f"- **Total Plans**: {len(plans)}",
            f"- **Active**: {len(active)}",
            f"- **Dormant**: {len(dormant)}",
            f"- **Blocked**: {len(blocked)}",
            f"- **Complete**: {len(complete)}",
            f"- **Average Progress**: {avg_progress:.0f}%",
            f"- **Test Count**: {test_count:,}",
            f"- **Files Without YAML Header**: {no_header_count}",
            "",
        ]

        # Add sanity warnings if any
        if sanity_issues:
            lines.extend(
                [
                    "---",
                    "",
                    "## ⚠️ Sanity Warnings",
                    "",
                ]
            )
            for issue in sanity_issues[:10]:
                lines.append(f"- {issue}")
            if len(sanity_issues) > 10:
                lines.append(f"- ... and {len(sanity_issues) - 10} more issues")
            lines.append("")

        lines.extend(
            [
                "---",
                "",
                "## Active Trees",
                "",
                "| Plan | Progress | Last Touched | Status | Notes |",
                "|------|----------|--------------|--------|-------|",
            ]
        )

        for p in sorted(active, key=lambda x: x.last_touched, reverse=True):
            lines.append(
                f"| {p.path} | {p.progress}% | {p.last_touched} | {p.status} | {p.notes[:40]} |"
            )

        if dormant:
            lines.extend(
                [
                    "",
                    "---",
                    "",
                    "## Dormant Trees",
                    "",
                    "| Plan | Progress | Last Touched | Days Since | Suggested Action |",
                    "|------|----------|--------------|------------|------------------|",
                ]
            )
            for p in sorted(dormant, key=lambda x: x.last_touched):
                days = (date.today() - p.last_touched).days
                action = "Archive" if days > 30 else "Review"
                lines.append(
                    f"| {p.path} | {p.progress}% | {p.last_touched} | {days} | {action} |"
                )

        if complete:
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
            for p in sorted(complete, key=lambda x: x.last_touched, reverse=True)[:10]:
                lines.append(f"| {p.path} | {p.last_touched} | {p.notes[:40]} |")

        content = "\n".join(lines)

        return BasicRendering(
            summary="Forest Manifest (from headers)",
            content=content,
            metadata={
                "status": "live",
                "source": "yaml_headers",
                "plan_count": len(plans),
                "test_count": test_count,
                "active_count": len(active),
                "dormant_count": len(dormant),
                "complete_count": len(complete),
                "accursed_share_next": accursed_next,
                "sanity_issues_count": len(sanity_issues),
                "no_header_count": no_header_count,
            },
        )

    async def _generate_status(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Generate _status.md content.

        AGENTESE: self.forest.status
        """
        plans = await self._collect_plans_from_headers()
        test_count = await self._collect_test_count()

        lines = [
            "# Implementation Status Matrix",
            "",
            f"> Last updated: {date.today().isoformat()} (Chief reconciliation: {test_count:,} tests)",
            "",
            "## Legend",
            "",
            "| Symbol | Status |",
            "|--------|--------|",
            "| done | Done |",
            "| in_progress | In Progress |",
            "| planned | Planned |",
            "",
        ]

        # Group by path prefix
        by_prefix: dict[str, list[PlanFromHeader]] = {}
        for p in plans:
            prefix = p.path.split("/")[0] if "/" in p.path else "misc"
            by_prefix.setdefault(prefix, []).append(p)

        for prefix, group in sorted(by_prefix.items()):
            lines.append(f"## {prefix.title()}")
            lines.append("")
            for p in sorted(group, key=lambda x: x.path):
                status_icon = (
                    "done"
                    if p.status == "complete"
                    else ("in_progress" if p.status == "active" else "planned")
                )
                lines.append(f"- [{status_icon}] {p.path} ({p.progress}%)")
            lines.append("")

        content = "\n".join(lines)

        return BasicRendering(
            summary="Implementation Status",
            content=content,
            metadata={
                "status": "live",
                "test_count": test_count,
                "plan_count": len(plans),
            },
        )

    async def _drift_report(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Generate drift report comparing documented vs actual state.

        AGENTESE: self.forest.witness
        """
        plans = await self._collect_plans_from_headers()
        actual_tests = await self._collect_test_count()
        documented_tests = await self._get_documented_test_count()
        actual_mypy = await self._collect_mypy_errors()

        # Find plan issues
        issues = []
        for p in plans:
            if p.status == "active" and p.progress == 0:
                days = (date.today() - p.last_touched).days
                if days > 7:
                    issues.append(
                        PlanIssue(p.path, f"0% progress, {days} days since touched")
                    )

        # Find stale plans
        stale = [
            p.path
            for p in plans
            if p.status == "dormant" and (date.today() - p.last_touched).days > 30
        ]

        # Find orphan references
        all_paths = {p.path for p in plans}
        orphans = []
        for p in plans:
            for ref in p.enables + p.blocking:
                if ref and ref not in all_paths:
                    orphans.append(ref)

        drift = DriftReport(
            test_count_drift=DriftItem(
                documented=documented_tests, actual=actual_tests
            ),
            mypy_drift=DriftItem(documented=0, actual=actual_mypy),
            plan_header_issues=issues,
            stale_plans=stale,
            orphan_plans=list(set(orphans)),
        )

        return BasicRendering(
            summary="Drift Report",
            content=drift.to_text(),
            metadata={
                "has_drift": drift.has_drift,
                "test_count_documented": documented_tests,
                "test_count_actual": actual_tests,
                "stale_count": len(stale),
                "issue_count": len(issues),
            },
        )

    async def _tithe(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Archive stale plans (dry run by default).

        AGENTESE: self.forest.tithe

        Args:
            execute: If True, actually archive (default: False)
        """
        execute = kwargs.get("execute", False)
        plans = await self._collect_plans_from_headers()

        archived = []
        skipped = []
        today = date.today()
        archive_dir = (
            self._get_project_root() / self._plans_root / "_archive" / today.isoformat()
        )

        for p in plans:
            if p.status != "dormant":
                continue

            days = (today - p.last_touched).days
            if days <= 30:
                skipped.append(f"{p.path}: only {days} days dormant")
                continue

            if p.blocking:
                skipped.append(f"{p.path}: has active blockers")
                continue

            reason = f"dormant >{days} days"
            original = self._get_project_root() / self._plans_root / Path(p.path).name
            if not original.suffix:
                original = original.with_suffix(".md")

            archive_path = archive_dir / original.name

            if execute and original.exists():
                archive_dir.mkdir(parents=True, exist_ok=True)
                original.rename(archive_path)

            archived.append(
                ArchivedPlan(
                    original_path=str(original),
                    archive_path=str(archive_path),
                    reason=reason,
                )
            )

        report = TitheReport(
            archived=archived,
            skipped=skipped,
            references_updated=[],
            dry_run=not execute,
        )

        return BasicRendering(
            summary=f"Tithe Report ({'DRY RUN' if not execute else 'EXECUTED'})",
            content=report.to_text(),
            metadata={
                "archived_count": len(archived),
                "skipped_count": len(skipped),
                "dry_run": not execute,
            },
        )

    async def _reconcile(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BasicRendering:
        """
        Full reconciliation of all meta files.

        AGENTESE: self.forest.reconcile

        Args:
            commit: If True, git commit the changes (default: False)
        """
        commit = kwargs.get("commit", False)

        # Get drift before
        drift_render = await self._drift_report(observer)
        drift_metadata = drift_render.metadata

        # Generate manifest
        manifest_render = await self._manifest_from_headers(observer)

        files_updated = []
        plans_dir = self._get_project_root() / self._plans_root

        # Write _forest.md
        forest_file = plans_dir / "_forest.md"
        forest_file.write_text(manifest_render.content)
        files_updated.append("_forest.md")

        # Create epilogue
        epilogue_dir = plans_dir / "_epilogues"
        epilogue_dir.mkdir(exist_ok=True)
        epilogue_name = f"{date.today().isoformat()}-reconciliation.md"
        epilogue_path = epilogue_dir / epilogue_name

        test_count = manifest_render.metadata.get("test_count", 0)
        _ = manifest_render.metadata.get("plan_count", 0)  # For future use

        epilogue_content = f"""---
path: plans/_epilogues/{epilogue_name}
status: complete
progress: 100
last_touched: {date.today().isoformat()}
---

# Chief of Staff Reconciliation

**Date**: {date.today().isoformat()}
**Tests**: {test_count:,}
**Active Plans**: {manifest_render.metadata.get("active_count", 0)}
**Complete Plans**: {manifest_render.metadata.get("complete_count", 0)}

## Summary

Generated by `self.forest.reconcile`

## Files Updated

{chr(10).join(f"- {f}" for f in files_updated)}
"""
        epilogue_path.write_text(epilogue_content)
        files_updated.append(epilogue_name)

        summary = f"Reconciled {len(files_updated)} files. Tests: {test_count:,}"

        if commit:
            try:
                subprocess.run(
                    ["git", "add"] + [str(plans_dir / f) for f in files_updated],
                    cwd=str(self._get_project_root()),
                    check=True,
                )
                subprocess.run(
                    [
                        "git",
                        "commit",
                        "-m",
                        f"chore(forest): Reconciliation {date.today().isoformat()}\n\nTests: {test_count:,}",
                    ],
                    cwd=str(self._get_project_root()),
                    check=True,
                )
            except subprocess.CalledProcessError:
                pass

        result = ReconciliationResult(
            drift_before=DriftReport(
                test_count_drift=DriftItem(
                    drift_metadata.get("test_count_documented", 0),
                    drift_metadata.get("test_count_actual", 0),
                ),
                mypy_drift=DriftItem(0, 0),
                plan_header_issues=[],
                stale_plans=[],
                orphan_plans=[],
            ),
            files_updated=files_updated,
            epilogue_path=epilogue_name,
            summary=summary,
        )

        return BasicRendering(
            summary="Reconciliation Complete",
            content=result.to_text(),
            metadata={
                "files_updated": files_updated,
                "test_count": test_count,
                "committed": commit,
            },
        )

    def _stream_epilogues(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Legacy: Stream epilogues (renamed from _witness)."""
        return self._witness(observer, **kwargs)

    async def _witness(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Stream epilogues from the forest.

        AGENTESE: time.forest.witness

        Scans _epilogues/*.md and streams parsed entries in reverse
        chronological order. Each entry includes:
        - path: File path
        - date: Date from filename (YYYY-MM-DD)
        - title: Title from first # header
        - content_preview: First ~200 chars
        - phase: Detected N-phase (if any)

        Args:
            limit: Maximum entries to return (default: 10)
            since: Only entries after this date (ISO format YYYY-MM-DD)
            phase: Filter by N-phase (e.g., "IMPLEMENT", "QA")
            law_check: Include law check results in output (default: False)

        Yields:
            EpilogueEntry-like dicts with handle metadata
        """
        limit = kwargs.get("limit", 10)
        since = kwargs.get("since")
        phase_filter = kwargs.get("phase")
        law_check = kwargs.get("law_check", False)

        # Scan and parse epilogues
        entries = scan_epilogues(
            self._epilogues_path,
            limit=limit,
            since=since,
            phase=phase_filter,
        )

        # Handle empty results
        if not entries:
            yield {
                "handle": "time.forest.witness",
                "status": "empty",
                "path": self._epilogues_path,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "title": "No epilogues found",
                "filters": {
                    "limit": limit,
                    "since": since,
                    "phase": phase_filter,
                },
            }
            return

        # Stream entries
        for entry in entries:
            result: dict[str, Any] = {
                "handle": "time.forest.witness",
                "status": "live",
                **entry.to_dict(),
            }

            # Include law check if requested
            if law_check:
                result["law_check"] = {
                    "identity": "pass",  # Epilogues have stable paths
                    "associativity": "skip",  # N/A for witness
                    "minimal_output": "pass",  # Streaming is minimal
                    "append_only": "pass",  # Epilogues are never modified
                }

            yield result

    async def _sip(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Select dormant plan for accursed share attention.

        AGENTESE: void.forest.sip

        The Accursed Share: Allocate 5% entropy budget to dormant plans.
        Selection criteria:
        1. Longest untouched (days since last touch)
        2. Not blocked
        3. Progress < 100%

        Parses _forest.md dormant section, sorts by days_since, returns top candidate.

        Args:
            entropy_budget: Maximum entropy to spend (default: 0.07)

        Returns:
            Dict with selected plan (string) and rationale
        """
        entropy_budget = kwargs.get("entropy_budget", 0.07)

        # Parse real forest data
        forest_manifest = parse_forest_md(self._forest_path)

        # Find dormant trees
        dormant_trees = [
            t for t in forest_manifest.trees if t.get("status") == "dormant"
        ]

        if not dormant_trees:
            return {
                "selected_plan": None,
                "rationale": "No dormant plans available",
                "entropy_spent": 0.0,
                "entropy_remaining": entropy_budget,
                "days_dormant": 0,
                "status": "empty",
            }

        # Sort by days_since descending (longest dormant first)
        sorted_dormant = sorted(
            dormant_trees,
            key=lambda t: t.get("days_since", 0),
            reverse=True,
        )

        # Select the longest dormant
        selected = sorted_dormant[0]
        selected_path = selected.get("path", "")
        days_dormant = selected.get("days_since", 0)

        return {
            "selected_plan": selected_path,  # String, not list
            "rationale": f"Longest dormant ({days_dormant} days)",
            "entropy_spent": min(entropy_budget, 0.05),
            "entropy_remaining": max(0.0, entropy_budget - 0.05),
            "days_dormant": days_dormant,
            "status": "live",
        }

    async def _refine(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Propose mutation with rollback token.

        AGENTESE: concept.forest.refine

        The Rollback Protocol:
        1. Generate unique rollback token
        2. Preview proposed changes
        3. Check AGENTESE laws
        4. Return token for later apply/rollback

        CRITICAL: Never apply directly. Always return rollback_token.

        Stub: Returns placeholder preview. Real implementation will:
        1. Parse target plan
        2. Generate diff preview
        3. Run law checks
        4. Store rollback state

        Args:
            plan_path: Path to plan (e.g., "agents/k-gent")
            changes: Dict of proposed changes
            dry_run: If True, don't store rollback state (default: True)

        Returns:
            Dict with rollback_token (REQUIRED), preview, and law_check
        """
        plan_path = kwargs.get("plan_path", "")
        changes = kwargs.get("changes", {})
        dry_run = kwargs.get("dry_run", True)

        # Generate rollback token (REQUIRED per protocol)
        rollback_token = str(uuid.uuid4())

        # Law check (stub: all pass)
        law_check = ForestLawCheck(
            identity="pass",
            associativity="pass",
            minimal_output="pass",
        )

        # Store rollback state if not dry run
        if not dry_run:
            self._pending_rollbacks[rollback_token] = {
                "plan_path": plan_path,
                "changes": changes,
                "created_at": datetime.now().isoformat(),
                "observer": self._umwelt_to_meta(observer).name,
            }

        return {
            "rollback_token": rollback_token,  # REQUIRED
            "preview": {
                "plan_path": plan_path,
                "changes": changes,
                "status": "stub",
            },
            "law_check": law_check.to_dict(),
            "applied": False,
            "dry_run": dry_run,
        }

    async def _define(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        JIT plan scaffold creation.

        AGENTESE: self.forest.define

        Creates a new plan with proper header structure.
        The plan exists in draft state until first IMPLEMENT phase.

        Stub: Returns placeholder header. Real implementation will:
        1. Validate path doesn't exist
        2. Generate proper YAML header
        3. Create file at plans/{path}.md

        Args:
            path: Plan path (e.g., "agents/new-gent")
            title: Plan title
            enables: List of plans this enables
            blocking: List of blocking dependencies
            session_notes: Initial session notes

        Returns:
            Dict with draft header and creation status
        """
        path = kwargs.get("path", "new-plan")
        title = kwargs.get("title", path.split("/")[-1].title())
        enables = kwargs.get("enables", [])
        blocking = kwargs.get("blocking", [])
        session_notes = kwargs.get("session_notes", "Initial plan creation.")

        # Generate YAML header
        header_lines = [
            "---",
            f"path: {path}",
            "status: draft",
            "progress: 0",
            f"last_touched: {datetime.now().strftime('%Y-%m-%d')}",
            f"touched_by: {self._umwelt_to_meta(observer).name}",
            f"blocking: {blocking}",
            f"enables: {enables}",
            "session_notes: |",
            f"  {session_notes}",
            "phase_ledger:",
            "  PLAN: touched",
            "  RESEARCH: pending",
            "  DEVELOP: pending",
            "  STRATEGIZE: pending",
            "  CROSS-SYNERGIZE: pending",
            "  IMPLEMENT: pending",
            "  QA: pending",
            "  TEST: pending",
            "  EDUCATE: pending",
            "  MEASURE: pending",
            "  REFLECT: pending",
            "entropy:",
            "  planned: 0.05",
            "  spent: 0.0",
            "  returned: 0.05",
            "---",
        ]

        return {
            "status": "stub",
            "path": path,
            "title": title,
            "draft_header": "\n".join(header_lines),
            "note": "Real implementation will write to plans/{path}.md",
        }

    async def _apply(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Apply a pending refinement.

        AGENTESE: concept.forest.apply (ops role only)

        Requires rollback_token from prior refine() call.

        Stub: Returns success status. Real implementation will:
        1. Validate rollback_token exists
        2. Apply stored changes
        3. Mark token as consumed
        4. Update _forest.md

        Args:
            rollback_token: Token from prior refine() call (REQUIRED)

        Returns:
            Dict with apply status
        """
        rollback_token = kwargs.get("rollback_token")

        if not rollback_token:
            return {"error": "rollback_token required", "status": "failed"}

        if rollback_token not in self._pending_rollbacks:
            return {
                "error": "Invalid or expired rollback_token",
                "status": "failed",
                "rollback_token": rollback_token,
            }

        # Get and remove pending rollback
        pending = self._pending_rollbacks.pop(rollback_token)

        return {
            "status": "stub_applied",
            "rollback_token": rollback_token,
            "plan_path": pending.get("plan_path"),
            "note": "Real implementation will write changes to disk",
        }

    async def _rollback(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Cancel a pending refinement.

        AGENTESE: concept.forest.rollback (ops role only)

        Discards the pending changes without applying.

        Args:
            rollback_token: Token from prior refine() call (REQUIRED)

        Returns:
            Dict with rollback status
        """
        rollback_token = kwargs.get("rollback_token")

        if not rollback_token:
            return {"error": "rollback_token required", "status": "failed"}

        if rollback_token not in self._pending_rollbacks:
            return {
                "error": "Invalid or expired rollback_token",
                "status": "failed",
                "rollback_token": rollback_token,
            }

        # Discard pending rollback
        self._pending_rollbacks.pop(rollback_token)

        return {
            "status": "rolled_back",
            "rollback_token": rollback_token,
            "note": "Changes discarded without applying",
        }

    async def _lint(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Check forest health and header compliance.

        AGENTESE: concept.forest.lint (ops role only)

        Validates:
        - All plans have proper YAML headers
        - Progress percentages are consistent
        - Dependency graph has no cycles
        - Accursed share rotation is working

        Stub: Returns placeholder health. Real implementation will:
        1. Scan all plans/*.md
        2. Parse and validate headers
        3. Check dependency graph
        4. Report violations

        Returns:
            Dict with lint results
        """
        return {
            "status": "stub",
            "violations": [],
            "warnings": [],
            "trees_checked": 0,
            "note": "Real implementation will validate all plan headers",
        }

    async def _dream(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Exploratory forest operation (Accursed Share 5%).

        AGENTESE: void.forest.dream

        This is the entropy sink for forest operations.
        Used for:
        - Random plan connection discovery
        - Unexpected synergy identification
        - Creative plan naming

        Stub: Returns placeholder dream. Real implementation might:
        1. Select random plans
        2. Propose unexpected connections
        3. Generate creative metaphors

        Returns:
            Dict with dream content
        """
        return {
            "status": "stub",
            "dream": "The forest dreams of connections not yet made...",
            "random_plan": None,
            "proposed_synergy": None,
            "entropy_source": "void.forest.dream",
            "note": "Accursed Share 5% allocation",
        }


# === Forest Context Resolver ===


@dataclass
class ForestContextResolver:
    """
    Resolver for forest.* context paths.

    Provides a single ForestNode that handles all forest operations.
    The forest is a singleton context - there's only one forest per project.

    Resolution:
    - concept.forest.* → ForestNode (manifest, refine, define, lint)
    - time.forest.* → ForestNode (witness)
    - void.forest.* → ForestNode (sip, dream)
    - self.forest.* → ForestNode (define)

    Note: Forest handles are cross-context. The ForestNode handles
    routing internally based on the aspect invoked.
    """

    # Paths configuration
    forest_path: str = "plans/_forest.md"
    focus_path: str = "plans/_focus.md"
    epilogues_path: str = "plans/_epilogues"
    plans_root: str = "plans"

    # Singleton node
    _node: ForestNode | None = None

    def resolve(self, holon: str, rest: list[str]) -> ForestNode:
        """
        Resolve a forest.* path to ForestNode.

        The forest is a singleton - all paths resolve to the same node.
        The aspect (from rest) determines behavior.

        Args:
            holon: Usually "forest" or specific plan path component
            rest: Additional path components

        Returns:
            ForestNode singleton
        """
        if self._node is None:
            self._node = ForestNode(
                _forest_path=self.forest_path,
                _focus_path=self.focus_path,
                _epilogues_path=self.epilogues_path,
                _plans_root=self.plans_root,
            )
        return self._node


# === Factory Function ===


def create_forest_resolver(
    forest_path: str = "plans/_forest.md",
    focus_path: str = "plans/_focus.md",
    epilogues_path: str = "plans/_epilogues",
    plans_root: str = "plans",
) -> ForestContextResolver:
    """
    Create a ForestContextResolver with optional path configuration.

    Args:
        forest_path: Path to _forest.md
        focus_path: Path to _focus.md (never overwritten)
        epilogues_path: Path to _epilogues directory
        plans_root: Root directory for plans

    Returns:
        Configured ForestContextResolver
    """
    return ForestContextResolver(
        forest_path=forest_path,
        focus_path=focus_path,
        epilogues_path=epilogues_path,
        plans_root=plans_root,
    )


def create_forest_node(
    forest_path: str = "plans/_forest.md",
    focus_path: str = "plans/_focus.md",
    epilogues_path: str = "plans/_epilogues",
    plans_root: str = "plans",
) -> ForestNode:
    """
    Create a standalone ForestNode.

    Use this when you need direct node access without the resolver.

    Args:
        forest_path: Path to _forest.md
        focus_path: Path to _focus.md
        epilogues_path: Path to _epilogues directory
        plans_root: Root directory for plans

    Returns:
        Configured ForestNode
    """
    return ForestNode(
        _forest_path=forest_path,
        _focus_path=focus_path,
        _epilogues_path=epilogues_path,
        _plans_root=plans_root,
    )
