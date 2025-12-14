"""
AGENTESE Forest Context Resolver

The Forest: plans as handles, epilogues as witnesses, dormant as accursed share.

forest.* handles resolve to planning artifacts that can be:
- Manifested (concept.forest.manifest) → canopy view
- Witnessed (time.forest.witness) → epilogue stream
- Sipped (void.forest.sip) → accursed share selection
- Refined (concept.forest.refine) → mutation with rollback
- Defined (self.forest.define) → JIT plan scaffold

The Forest Protocol:
- _focus.md = human intent (never overwrite)
- _forest.md = canopy view (regenerable)
- _epilogues/ = witnesses (append-only)
- plans/*.md = individual trees (handles)

Principle Alignment: Heterarchical, Composable, Minimal Output

> *"Plans as handles. Epilogues as witnesses. The forest becomes AGENTESE-native."*
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncIterator

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
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
    "guest": ("manifest", "witness"),
    # Meta: can mutate and draw from accursed share
    "meta": ("manifest", "witness", "refine", "sip", "define"),
    # Ops: full control including apply, rollback, and forest health checks
    "ops": (
        "manifest",
        "witness",
        "refine",
        "sip",
        "define",
        "apply",
        "rollback",
        "lint",
    ),
    # Default: minimal read access
    "default": ("manifest",),
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

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
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
                return await self.manifest(observer)
            case "witness":
                # Returns AsyncIterator - caller handles streaming
                return self._witness(observer, **kwargs)
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
