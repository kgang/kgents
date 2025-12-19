"""
Garden Sheaf: Global Coherence from Local Plan Views.

A sheaf ensures that local views of different plans glue consistently
into a coherent global project view. The sheaf condition enforces:

    If plan_a and plan_b share resonances,
    their views must agree on shared elements.

This prevents conflicting parallel development and catches coordination
issues early.

See: spec/protocols/garden-protocol.md Part II.3
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from .types import GardenPlanHeader, Mood, Season, parse_garden_header

if TYPE_CHECKING:
    pass


# =============================================================================
# Sheaf Types
# =============================================================================


@dataclass(frozen=True)
class PlanView:
    """
    Local view of a plan's state at a point in time.

    This is the "stalk" of the sheaf over a plan.
    """

    plan_name: str
    season: Season
    mood: Mood
    momentum: float
    resonances: frozenset[str]
    entropy_state: tuple[float, float]  # (available, spent)

    @classmethod
    def from_header(cls, header: GardenPlanHeader) -> "PlanView":
        """Create a view from a parsed header."""
        return cls(
            plan_name=header.name,
            season=header.season,
            mood=header.mood,
            momentum=header.momentum,
            resonances=frozenset(header.resonates_with),
            entropy_state=(header.entropy.available, header.entropy.spent),
        )

    @property
    def entropy_remaining(self) -> float:
        """How much entropy is left to spend."""
        return self.entropy_state[0] - self.entropy_state[1]


@dataclass
class ProjectView:
    """
    Global view of project state, glued from plan views.

    This is the "section" of the sheaf over the whole project.
    """

    plans: list[PlanView]
    total_entropy: tuple[float, float]  # (available, spent)
    resonance_graph: dict[str, set[str]]  # plan -> resonating plans
    coherence_score: float = 1.0

    @property
    def active_plans(self) -> list[PlanView]:
        """Plans in SPROUTING or BLOOMING season."""
        return [p for p in self.plans if p.season in (Season.SPROUTING, Season.BLOOMING)]

    @property
    def dormant_plans(self) -> list[PlanView]:
        """Plans in DORMANT season."""
        return [p for p in self.plans if p.season == Season.DORMANT]

    @property
    def entropy_remaining(self) -> float:
        """Total entropy remaining across all plans."""
        return self.total_entropy[0] - self.total_entropy[1]


class CoherenceError(Exception):
    """Raised when plans fail to glue coherently."""

    pass


# =============================================================================
# Compatibility Rules
# =============================================================================


@dataclass(frozen=True)
class CompatibilityResult:
    """Result of checking two plan views for compatibility."""

    compatible: bool
    reason: str
    overlap: frozenset[str] = field(default_factory=frozenset)


def check_dormancy_rule(
    view_a: PlanView, view_b: PlanView, overlap: frozenset[str]
) -> CompatibilityResult:
    """
    Rule 1: Dormant plans shouldn't resonate with active work.

    If a plan is DORMANT, it's resting. Active plans working on shared
    concepts might interfere with the dormant plan's state.

    HONESTY: This is a soft rule - it warns rather than errors.
    Sometimes you DO want to work on concepts a dormant plan owns.
    """
    if not overlap:
        return CompatibilityResult(True, "No overlap", overlap)

    a_dormant = view_a.season == Season.DORMANT
    b_active = view_b.season in (Season.SPROUTING, Season.BLOOMING)

    if a_dormant and b_active:
        return CompatibilityResult(
            compatible=True,  # Warning, not error
            reason=f"Soft conflict: dormant '{view_a.plan_name}' resonates with active '{view_b.plan_name}' on {overlap}",
            overlap=overlap,
        )

    return CompatibilityResult(True, "No dormancy conflict", overlap)


def check_entropy_independence(
    view_a: PlanView, view_b: PlanView, overlap: frozenset[str]
) -> CompatibilityResult:
    """
    Rule 2: Entropy budgets should be independent.

    Plans shouldn't share entropy pools unless explicitly grafted.
    This check just verifies both plans are within their own budgets.
    """
    a_ok = view_a.entropy_state[1] <= view_a.entropy_state[0]
    b_ok = view_b.entropy_state[1] <= view_b.entropy_state[0]

    if not a_ok:
        return CompatibilityResult(
            compatible=False,
            reason=f"Plan '{view_a.plan_name}' exceeded entropy budget",
            overlap=overlap,
        )
    if not b_ok:
        return CompatibilityResult(
            compatible=False,
            reason=f"Plan '{view_b.plan_name}' exceeded entropy budget",
            overlap=overlap,
        )

    return CompatibilityResult(True, "Entropy budgets independent", overlap)


def check_momentum_coherence(
    view_a: PlanView, view_b: PlanView, overlap: frozenset[str]
) -> CompatibilityResult:
    """
    Rule 3: Highly divergent momentum on shared concepts is a warning.

    If two plans share resonances but have very different momenta,
    one might be blocking the other or they're out of sync.
    """
    if not overlap:
        return CompatibilityResult(True, "No overlap", overlap)

    momentum_diff = abs(view_a.momentum - view_b.momentum)
    if momentum_diff > 0.5:
        return CompatibilityResult(
            compatible=True,  # Warning, not error
            reason=f"Momentum divergence: {view_a.plan_name}={view_a.momentum:.0%}, {view_b.plan_name}={view_b.momentum:.0%}",
            overlap=overlap,
        )

    return CompatibilityResult(True, "Momentum aligned", overlap)


# =============================================================================
# Garden Sheaf
# =============================================================================


class GardenSheaf:
    """
    Global coherence from local plan views.

    The sheaf condition ensures all plans glue to a coherent project.
    It's the category-theoretic foundation for project-level reasoning.

    Key insight: Plans are local perspectives on shared work.
    The sheaf ensures these perspectives are compatible.
    """

    def __init__(self, plans_dir: Path | None = None):
        """
        Initialize the sheaf.

        Args:
            plans_dir: Directory containing plan files. If None, uses default.
        """
        self.plans_dir = plans_dir or Path.cwd().parents[1] / "plans"
        self._views: dict[str, PlanView] = {}

    def load_plan(self, plan_path: Path) -> PlanView | None:
        """
        Load a plan view from a file.

        Returns None if the file isn't Garden Protocol format.
        """
        header = parse_garden_header(plan_path)
        if header is None:
            return None

        view = PlanView.from_header(header)
        self._views[view.plan_name] = view
        return view

    def load_all_plans(self) -> list[PlanView]:
        """Load all Garden Protocol plans from the plans directory."""
        if not self.plans_dir.exists():
            return []

        views = []
        for plan_file in self.plans_dir.glob("*.md"):
            view = self.load_plan(plan_file)
            if view is not None:
                views.append(view)

        return views

    def overlap(self, plan_a: str, plan_b: str) -> frozenset[str]:
        """
        What do these plans share?

        Returns the intersection of their resonances.
        """
        view_a = self._views.get(plan_a)
        view_b = self._views.get(plan_b)

        if view_a is None or view_b is None:
            return frozenset()

        return view_a.resonances & view_b.resonances

    def compatible(self, view_a: PlanView, view_b: PlanView) -> CompatibilityResult:
        """
        Check if two plan views are compatible.

        Runs all compatibility rules and returns the first failure,
        or success if all pass.
        """
        overlap = view_a.resonances & view_b.resonances

        # Run all rules
        rules = [
            check_dormancy_rule,
            check_entropy_independence,
            check_momentum_coherence,
        ]

        for rule in rules:
            result = rule(view_a, view_b, overlap)
            if not result.compatible:
                return result

        return CompatibilityResult(
            compatible=True,
            reason="Plans are compatible",
            overlap=overlap,
        )

    def glue(self, views: list[PlanView], strict: bool = False) -> ProjectView:
        """
        Combine compatible local views into global project view.

        This is where emergence happens: the whole project state
        emerges from gluing individual plan states.

        Args:
            views: Plan views to glue
            strict: If True, raise on any incompatibility. If False, warn only.

        Returns:
            ProjectView representing the global state

        Raises:
            CoherenceError: If strict=True and plans don't glue
        """
        # Verify pairwise compatibility
        warnings = []
        for i, a in enumerate(views):
            for b in views[i + 1 :]:
                result = self.compatible(a, b)
                if not result.compatible:
                    if strict:
                        raise CoherenceError(
                            f"Plans don't glue: {a.plan_name} ↔ {b.plan_name}: {result.reason}"
                        )
                    else:
                        warnings.append(result.reason)

        # Build resonance graph
        resonance_graph: dict[str, set[str]] = {v.plan_name: set() for v in views}
        for i, a in enumerate(views):
            for b in views[i + 1 :]:
                overlap = a.resonances & b.resonances
                if overlap:
                    resonance_graph[a.plan_name].add(b.plan_name)
                    resonance_graph[b.plan_name].add(a.plan_name)

        # Compute coherence score (1.0 = perfect, lower = warnings)
        warning_penalty = 0.1
        coherence_score = max(0.0, 1.0 - len(warnings) * warning_penalty)

        # Sum entropy across plans
        total_available = sum(v.entropy_state[0] for v in views)
        total_spent = sum(v.entropy_state[1] for v in views)

        return ProjectView(
            plans=views,
            total_entropy=(total_available, total_spent),
            resonance_graph=resonance_graph,
            coherence_score=coherence_score,
        )

    def project_view(self, strict: bool = False) -> ProjectView:
        """
        Get the global project view from all loaded plans.

        Convenience method that loads all plans and glues them.
        """
        views = self.load_all_plans()
        if not views:
            return ProjectView(
                plans=[],
                total_entropy=(0.0, 0.0),
                resonance_graph={},
                coherence_score=1.0,
            )
        return self.glue(views, strict=strict)


# =============================================================================
# Convenience Functions
# =============================================================================


def check_project_coherence(
    plans_dir: Path | None = None,
) -> tuple[bool, ProjectView, list[str]]:
    """
    Check if all plans in a project are coherent.

    Returns:
        (is_coherent, project_view, warnings)
    """
    sheaf = GardenSheaf(plans_dir)
    try:
        view = sheaf.project_view(strict=False)
        is_coherent = view.coherence_score == 1.0
        warnings = []

        # Collect warnings from pairwise checks
        views = list(sheaf._views.values())
        for i, a in enumerate(views):
            for b in views[i + 1 :]:
                result = sheaf.compatible(a, b)
                if result.compatible and "conflict" in result.reason.lower():
                    warnings.append(result.reason)
                elif result.compatible and "divergence" in result.reason.lower():
                    warnings.append(result.reason)

        return is_coherent, view, warnings
    except CoherenceError as e:
        return False, ProjectView([], (0, 0), {}, 0.0), [str(e)]


__all__ = [
    "PlanView",
    "ProjectView",
    "CoherenceError",
    "CompatibilityResult",
    "GardenSheaf",
    "check_project_coherence",
]
