"""
AGENTESE Node: self.memory.archaeology

Archaeology service exposed via AGENTESE.

AGENTESE Paths:
- self.memory.archaeology.manifest    - Status and feature counts
- self.memory.archaeology.mine        - Parse git history
- self.memory.archaeology.teaching    - Extract teachings from commits
- self.memory.archaeology.crystallize - Persist teachings to Witness
- self.memory.archaeology.trajectories - Feature trajectory analysis

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

Philosophy:
    "The past is not dead. It is not even past." - Faulkner
    "The artifact remembers so the agent can forget." - Stigmergy

See: plans/git-archaeology-backfill.md
See: spec/protocols/repo-archaeology.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, aspect
from ..contract import Contract, Response
from ..node import BaseLogosNode, BasicRendering, Observer, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from services.witness.persistence import WitnessPersistence


# =============================================================================
# Request/Response Contracts
# =============================================================================


@dataclass(frozen=True)
class ArchaeologyManifestResponse:
    """Response for archaeology manifest."""

    total_commits: int
    features_by_status: dict[str, int]


@dataclass(frozen=True)
class MineRequest:
    """Request for mining git history."""

    max_commits: int = 500


@dataclass(frozen=True)
class MineResponse:
    """Response for mining git history."""

    commits_parsed: int
    total_commits: int
    commit_types: dict[str, int]
    authors: dict[str, int]


@dataclass(frozen=True)
class TeachingRequest:
    """Request for extracting teachings."""

    max_commits: int = 200
    category: str | None = None  # gotcha, warning, critical, decision, pattern


@dataclass(frozen=True)
class TeachingResponse:
    """Response for teaching extraction."""

    total_teachings: int
    by_category: dict[str, int]
    teachings: list[dict[str, Any]]  # Limited to first 20


@dataclass(frozen=True)
class CrystallizeRequest:
    """Request for crystallizing teachings to Witness."""

    max_commits: int = 200
    dry_run: bool = False


@dataclass(frozen=True)
class CrystallizeResponse:
    """Response for crystallization."""

    mode: str  # "dry_run" or "crystallize"
    total_teachings: int
    marks_created: int
    marks_skipped: int
    errors: list[str]


@dataclass(frozen=True)
class TrajectoriesRequest:
    """Request for feature trajectories."""

    active_only: bool = True
    max_commits: int = 500


@dataclass(frozen=True)
class TrajectoriesResponse:
    """Response for feature trajectories."""

    features: int
    commits_analyzed: int
    trajectories: list[dict[str, Any]]


# =============================================================================
# Renderings
# =============================================================================


@dataclass(frozen=True)
class ArchaeologyManifestRendering:
    """Rendering for archaeology manifest."""

    total_commits: int
    features_by_status: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "archaeology_manifest",
            "total_commits": self.total_commits,
            "features_by_status": self.features_by_status,
        }

    def to_text(self) -> str:
        lines = [
            "Git Archaeology Status",
            "=" * 30,
            f"Total commits: {self.total_commits}",
            "",
            "Features by Status:",
        ]
        for status, count in sorted(self.features_by_status.items()):
            lines.append(f"  {status}: {count}")
        return "\n".join(lines)


@dataclass(frozen=True)
class TeachingRendering:
    """Rendering for teaching extraction."""

    total: int
    by_category: dict[str, int]
    teachings: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "teaching_extraction",
            "total": self.total,
            "by_category": self.by_category,
            "teachings": self.teachings,
        }

    def to_text(self) -> str:
        lines = [
            f"Teachings Extracted: {self.total}",
            "",
            "By Category:",
        ]
        for cat, count in sorted(self.by_category.items(), key=lambda x: -x[1]):
            lines.append(f"  {cat}: {count}")
        if self.teachings:
            lines.extend(["", "Recent Teachings:"])
            for t in self.teachings[:5]:
                lines.append(f"  - {t.get('insight', '')[:60]}...")
        return "\n".join(lines)


@dataclass
class MineRendering:
    """Rendering for mine results."""

    commits_parsed: int
    total_commits: int
    commit_types: dict[str, int]
    authors: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "mine_result",
            "commits_parsed": self.commits_parsed,
            "total_commits": self.total_commits,
            "commit_types": self.commit_types,
            "authors": self.authors,
        }

    def to_text(self) -> str:
        lines = [
            f"Parsed: {self.commits_parsed} / {self.total_commits} commits",
            "",
            "Commit Types:",
        ]
        for ctype, count in sorted(self.commit_types.items(), key=lambda x: -x[1])[:8]:
            lines.append(f"  {ctype}: {count}")
        lines.extend(["", "Top Authors:"])
        for author, count in sorted(self.authors.items(), key=lambda x: -x[1])[:5]:
            lines.append(f"  {author}: {count}")
        return "\n".join(lines)


@dataclass
class CrystallizeRendering:
    """Rendering for crystallization results."""

    mode: str
    total_teachings: int
    marks_created: int
    marks_skipped: int
    errors: list[str] = field(default_factory=list)
    by_category: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "crystallize_result",
            "mode": self.mode,
            "total_teachings": self.total_teachings,
            "marks_created": self.marks_created,
            "marks_skipped": self.marks_skipped,
            "errors": self.errors,
            "by_category": self.by_category,
        }

    def to_text(self) -> str:
        lines = [
            f"Crystallization ({self.mode})",
            "=" * 30,
            f"Total teachings: {self.total_teachings}",
            f"Marks created: {self.marks_created}",
            f"Marks skipped: {self.marks_skipped}",
        ]
        if self.by_category:
            lines.extend(["", "By Category:"])
            for cat, count in sorted(self.by_category.items(), key=lambda x: -x[1]):
                lines.append(f"  {cat}: {count}")
        if self.errors:
            lines.extend(["", "Errors:"])
            for err in self.errors[:5]:
                lines.append(f"  - {err}")
        return "\n".join(lines)


@dataclass
class TrajectoriesRendering:
    """Rendering for trajectory results."""

    features: int
    commits_analyzed: int
    trajectories: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "trajectories_result",
            "features": self.features,
            "commits_analyzed": self.commits_analyzed,
            "trajectories": self.trajectories,
        }

    def to_text(self) -> str:
        lines = [
            f"Feature Trajectories ({self.features} features)",
            "=" * 40,
            f"Commits analyzed: {self.commits_analyzed}",
            "",
            "Trajectories (by velocity):",
        ]
        for t in self.trajectories[:10]:
            health = t.get("health", "unknown")
            velocity = t.get("velocity", 0)
            lines.append(f"  {t['name']}: {health} (v={velocity})")
        return "\n".join(lines)


# =============================================================================
# ArchaeologyNode
# =============================================================================


@node(
    "self.memory.archaeology",
    description="Git Archaeology - Mine git history for priors and teachings",
    dependencies=("witness_persistence",),
    contracts={
        "manifest": Response(ArchaeologyManifestResponse),
        "mine": Contract(MineRequest, MineResponse),
        "teaching": Contract(TeachingRequest, TeachingResponse),
        "crystallize": Contract(CrystallizeRequest, CrystallizeResponse),
        "trajectories": Contract(TrajectoriesRequest, TrajectoriesResponse),
    },
    examples=[
        ("manifest", {}, "Show archaeology status"),
        ("mine", {"max_commits": 500}, "Parse git history"),
        ("teaching", {"category": "gotcha"}, "Extract gotchas from commits"),
        ("crystallize", {"dry_run": True}, "Preview crystallization"),
        ("trajectories", {"active_only": True}, "Get active feature trajectories"),
    ],
)
class ArchaeologyNode(BaseLogosNode):
    """
    AGENTESE node for Git Archaeology.

    Exposes the archaeology service through the universal protocol.

    Example:
        # Via AGENTESE gateway
        POST /agentese/self/memory/archaeology/teaching
        {"category": "gotcha", "max_commits": 100}

        # Via Logos directly
        await logos.invoke("self.memory.archaeology.mine", observer, max_commits=500)

        # Via CLI
        kg archaeology teaching --category gotcha
    """

    def __init__(
        self,
        witness_persistence: "WitnessPersistence | None" = None,
    ) -> None:
        """
        Initialize ArchaeologyNode.

        Args:
            witness_persistence: Optional persistence for crystallize aspect
        """
        self._persistence = witness_persistence

    @property
    def handle(self) -> str:
        return "self.memory.archaeology"

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Route aspect invocations to appropriate methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if aspect == "mine":
            return await self.mine(observer, **kwargs)
        elif aspect == "teaching":
            return await self.teaching(observer, **kwargs)
        elif aspect == "crystallize":
            return await self.crystallize(observer, **kwargs)
        elif aspect == "trajectories":
            return await self.trajectories(observer, **kwargs)
        else:
            return BasicRendering(summary=f"Unknown aspect: {aspect}")

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        # Archaeology is read-heavy, all archetypes can read
        base = ("manifest", "mine", "teaching", "trajectories")

        # Only developers+ can crystallize
        if archetype in ("developer", "tech_lead", "architect"):
            return base + ("crystallize",)

        return base

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Show archaeology status",
    )
    async def manifest(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Get archaeology status."""
        from services.archaeology import get_commit_count, get_patterns_by_status

        total_commits = get_commit_count()
        patterns_by_status = get_patterns_by_status()

        features_by_status = {
            status: len(patterns) for status, patterns in patterns_by_status.items()
        }

        return ArchaeologyManifestRendering(
            total_commits=total_commits,
            features_by_status=features_by_status,
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Parse git history",
    )
    async def mine(
        self,
        observer: "Umwelt[Any, Any]",
        max_commits: int = 500,
        **kwargs: Any,
    ) -> Renderable:
        """Parse git history and return summary statistics."""
        from services.archaeology import get_authors, get_commit_count, parse_git_log

        commits = parse_git_log(max_commits=max_commits)
        total_commits = get_commit_count()
        authors = get_authors()

        commit_types: dict[str, int] = {}
        for c in commits:
            ctype = c.commit_type
            commit_types[ctype] = commit_types.get(ctype, 0) + 1

        return MineRendering(
            commits_parsed=len(commits),
            total_commits=total_commits,
            commit_types=commit_types,
            authors=dict(sorted(authors.items(), key=lambda x: -x[1])[:10]),
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Extract teachings from commits",
    )
    async def teaching(
        self,
        observer: "Umwelt[Any, Any]",
        max_commits: int = 200,
        category: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Extract teachings from commit history."""
        from services.archaeology import extract_teachings_from_commits, parse_git_log

        commits = parse_git_log(max_commits=max_commits)
        teachings = extract_teachings_from_commits(commits)

        # Filter by category if specified
        if category:
            teachings = [t for t in teachings if t.category == category]

        # Count by category
        by_category: dict[str, int] = {}
        for t in teachings:
            by_category[t.category] = by_category.get(t.category, 0) + 1

        # Build response with limited teachings
        teachings_list = [
            {
                "insight": t.teaching.insight,
                "severity": t.teaching.severity,
                "category": t.category,
                "features": list(t.features[:3]),
                "commit": t.commit.sha[:8],
            }
            for t in teachings[:20]
        ]

        return TeachingRendering(
            total=len(teachings),
            by_category=by_category,
            teachings=teachings_list,
        )

    @aspect(
        category=AspectCategory.MUTATION,
        description="Crystallize teachings to Witness marks",
    )
    async def crystallize(
        self,
        observer: "Umwelt[Any, Any]",
        max_commits: int = 200,
        dry_run: bool = False,
        **kwargs: Any,
    ) -> Renderable:
        """Crystallize commit teachings as Witness marks."""
        from services.archaeology import (
            crystallize_teachings_to_witness,
            extract_teachings_from_commits,
            parse_git_log,
        )

        commits = parse_git_log(max_commits=max_commits)
        teachings = extract_teachings_from_commits(commits)

        if dry_run or self._persistence is None:
            # Dry run - just count
            by_category: dict[str, int] = {}
            for t in teachings:
                by_category[t.category] = by_category.get(t.category, 0) + 1

            errors: list[str] = [] if self._persistence else ["No persistence configured"]

            return CrystallizeRendering(
                mode="dry_run",
                total_teachings=len(teachings),
                marks_created=0,
                marks_skipped=0,
                errors=errors,
                by_category=by_category,
            )

        # Actual crystallization
        result = await crystallize_teachings_to_witness(teachings, self._persistence, dry_run=False)

        return CrystallizeRendering(
            mode="crystallize",
            total_teachings=result.total_teachings,
            marks_created=result.marks_created,
            marks_skipped=result.marks_skipped,
            errors=result.errors[:10],
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Get feature trajectories",
    )
    async def trajectories(
        self,
        observer: "Umwelt[Any, Any]",
        active_only: bool = True,
        max_commits: int = 500,
        **kwargs: Any,
    ) -> Renderable:
        """Get feature trajectory analysis."""
        from services.archaeology import (
            ACTIVE_FEATURES,
            FEATURE_PATTERNS,
            classify_all_features,
            parse_git_log,
        )

        patterns = ACTIVE_FEATURES if active_only else FEATURE_PATTERNS
        commits = parse_git_log(max_commits=max_commits)
        trajectories = classify_all_features(patterns, commits)

        trajectories_list = [
            {
                "name": t.name,
                "status": t.status.value,
                "velocity": round(t.velocity, 2),
                "commit_count": len(t.commits),
                "health": "healthy"
                if t.velocity > 0.1
                else "stable"
                if t.velocity > 0
                else "dormant",
            }
            for t in trajectories.values()
        ]

        return TrajectoriesRendering(
            features=len(trajectories),
            commits_analyzed=len(commits),
            trajectories=sorted(
                trajectories_list, key=lambda x: float(x["velocity"]), reverse=True
            ),
        )


__all__ = [
    "ArchaeologyNode",
    "ArchaeologyManifestResponse",
    "MineRequest",
    "MineResponse",
    "TeachingRequest",
    "TeachingResponse",
    "CrystallizeRequest",
    "CrystallizeResponse",
    "TrajectoriesRequest",
    "TrajectoriesResponse",
]
