"""
Psi-gent MetaphorUmwelt: Umwelt Protocol integration.

Each agent inhabits its own metaphor world.
Different agents should perceive different metaphor spaces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .types import Metaphor, Novel
from .metaphor_library import WeightedMetaphor
from .holographic_library import HolographicMetaphorLibrary


# =============================================================================
# Metaphor Constraint (Gravity)
# =============================================================================


@dataclass(frozen=True)
class MetaphorConstraint:
    """
    A constraint on which metaphors an agent can use.

    Part of the agent's "gravity" - what they cannot do.
    """

    name: str
    description: str
    check: Callable[[Metaphor], bool] = field(repr=False)

    def admits(self, metaphor: Metaphor) -> bool:
        """Does this constraint admit the metaphor?"""
        return self.check(metaphor)


# Standard constraints
def _no_military(m: Metaphor) -> bool:
    return "military" not in m.domain.lower() and "military" not in m.name.lower()


def _no_religious(m: Metaphor) -> bool:
    return "religious" not in m.domain.lower() and "religion" not in m.name.lower()


def _no_violent(m: Metaphor) -> bool:
    violent_ops = {"attack", "destroy", "kill", "war"}
    for op in m.operations:
        if any(v in op.name.lower() for v in violent_ops):
            return False
    return True


def _scientific_only(m: Metaphor) -> bool:
    return m.domain in {"physics", "biology", "mathematics", "chemistry", "ecology"}


def _narrative_only(m: Metaphor) -> bool:
    return m.domain == "narrative" or "story" in m.name.lower()


NO_MILITARY = MetaphorConstraint(
    name="no_military",
    description="Cannot use military metaphors",
    check=_no_military,
)

NO_RELIGIOUS = MetaphorConstraint(
    name="no_religious",
    description="Cannot use religious metaphors",
    check=_no_religious,
)

NO_VIOLENT = MetaphorConstraint(
    name="no_violent",
    description="Cannot use violent operations",
    check=_no_violent,
)

SCIENTIFIC_ONLY = MetaphorConstraint(
    name="scientific_only",
    description="Can only use scientific metaphors",
    check=_scientific_only,
)

NARRATIVE_ONLY = MetaphorConstraint(
    name="narrative_only",
    description="Can only use narrative metaphors",
    check=_narrative_only,
)


# =============================================================================
# Metaphor DNA (Genetic Configuration)
# =============================================================================


@dataclass(frozen=True)
class MetaphorDNA:
    """
    Genetic code for metaphor preference.

    The agent IS an expression of its DNA.
    DNA doesn't "load" - it germinates.
    """

    # Preferred domains
    preferred_domains: tuple[str, ...] = ()

    # Abstraction tendency (0 = concrete, 1 = abstract)
    abstraction_tendency: float = 0.5

    # Risk tolerance (willingness to try novel metaphors)
    risk_tolerance: float = 0.5

    # Exploration budget (The Accursed Share for experimentation)
    exploration_budget: float = 0.1

    # Blending willingness (0 = never blend, 1 = always blend)
    blending_willingness: float = 0.3

    def prefers_domain(self, domain: str) -> bool:
        """Does this DNA prefer a domain?"""
        if not self.preferred_domains:
            return True  # No preference = all ok
        return domain in self.preferred_domains

    def should_explore(self) -> bool:
        """Should the agent explore a novel metaphor?"""
        import random

        return random.random() < self.exploration_budget

    def should_blend(self) -> bool:
        """Should the agent attempt metaphor blending?"""
        import random

        return random.random() < self.blending_willingness


# Standard DNA profiles
K_GENT_DNA = MetaphorDNA(
    preferred_domains=("narrative", "psychology"),
    abstraction_tendency=0.6,
    risk_tolerance=0.4,
    exploration_budget=0.2,
    blending_willingness=0.5,
)

B_GENT_DNA = MetaphorDNA(
    preferred_domains=("physics", "biology", "mathematics"),
    abstraction_tendency=0.7,
    risk_tolerance=0.6,
    exploration_budget=0.3,
    blending_willingness=0.2,
)

E_GENT_DNA = MetaphorDNA(
    preferred_domains=("biology", "ecology"),
    abstraction_tendency=0.4,
    risk_tolerance=0.5,
    exploration_budget=0.4,
    blending_willingness=0.6,
)


# =============================================================================
# Metaphor Lens (State Focus)
# =============================================================================


@dataclass
class MetaphorLens:
    """
    A lens focusing on a subset of the metaphor library.

    The agent sees only metaphors that pass through this lens.
    """

    name: str
    constraints: tuple[MetaphorConstraint, ...]
    dna: MetaphorDNA

    def focus(
        self, library: HolographicMetaphorLibrary, problem: Novel, limit: int = 5
    ) -> list[WeightedMetaphor]:
        """
        Focus the library through this lens.

        Returns only metaphors that:
        1. Pass all constraints
        2. Align with DNA preferences
        """
        # Get all candidates
        all_candidates = library.fetch_candidates(problem, limit=limit * 3)

        # Filter by constraints
        filtered = []
        for wm in all_candidates:
            if all(c.admits(wm.metaphor) for c in self.constraints):
                filtered.append(wm)

        # Reweight by DNA preferences
        reweighted = []
        for wm in filtered:
            weight = wm.weight

            # Boost preferred domains
            if self.dna.prefers_domain(wm.metaphor.domain):
                weight *= 1.3

            # Adjust by abstraction tendency
            if wm.metaphor.tractability > 0.7 and self.dna.abstraction_tendency > 0.7:
                weight *= 1.1

            reweighted.append(WeightedMetaphor(metaphor=wm.metaphor, weight=weight))

        # Sort and limit
        reweighted.sort(reverse=True)
        return reweighted[:limit]


# =============================================================================
# Metaphor Umwelt
# =============================================================================


@dataclass
class MetaphorUmwelt:
    """
    An agent's subjective metaphor world.

    Just as a tick perceives only heat and butyric acid,
    different agents perceive different metaphor spaces.

    Components:
    - lens: What metaphors I can see
    - dna: My native metaphor vocabulary
    - gravity: What metaphors I cannot use
    """

    # The lens (state focus)
    lens: MetaphorLens

    # DNA (configuration)
    dna: MetaphorDNA

    # Gravity (constraints)
    gravity: tuple[MetaphorConstraint, ...]

    # Reference to shared library
    _library: HolographicMetaphorLibrary | None = field(default=None, repr=False)

    def bind_library(self, library: HolographicMetaphorLibrary) -> None:
        """Bind this umwelt to a metaphor library."""
        self._library = library

    def project(self, problem: Novel, limit: int = 5) -> list[WeightedMetaphor]:
        """
        Project available metaphors for this problem.

        Filters through lens and respects gravity.
        """
        if self._library is None:
            return []

        # Get candidates through lens
        candidates = self.lens.focus(self._library, problem, limit=limit * 2)

        # Filter by gravity
        filtered = [
            wm for wm in candidates if all(g.admits(wm.metaphor) for g in self.gravity)
        ]

        return filtered[:limit]

    def can_use(self, metaphor: Metaphor) -> bool:
        """Can this agent use the given metaphor?"""
        # Check constraints
        for c in self.lens.constraints:
            if not c.admits(metaphor):
                return False
        for g in self.gravity:
            if not g.admits(metaphor):
                return False
        return True

    def should_explore_novel(self) -> bool:
        """Should the agent explore a novel metaphor?"""
        return self.dna.should_explore()

    def should_blend(self) -> bool:
        """Should the agent attempt metaphor blending?"""
        return self.dna.should_blend()


# =============================================================================
# Umwelt Factory
# =============================================================================


def create_k_gent_umwelt() -> MetaphorUmwelt:
    """Create an umwelt for K-gent (persona/narrative focus)."""
    lens = MetaphorLens(
        name="k_gent_lens",
        constraints=(NO_VIOLENT,),
        dna=K_GENT_DNA,
    )
    return MetaphorUmwelt(
        lens=lens,
        dna=K_GENT_DNA,
        gravity=(NO_VIOLENT,),
    )


def create_b_gent_umwelt() -> MetaphorUmwelt:
    """Create an umwelt for B-gent (scientific focus)."""
    lens = MetaphorLens(
        name="b_gent_lens",
        constraints=(),
        dna=B_GENT_DNA,
    )
    return MetaphorUmwelt(
        lens=lens,
        dna=B_GENT_DNA,
        gravity=(),
    )


def create_e_gent_umwelt() -> MetaphorUmwelt:
    """Create an umwelt for E-gent (evolution focus)."""
    lens = MetaphorLens(
        name="e_gent_lens",
        constraints=(),
        dna=E_GENT_DNA,
    )
    return MetaphorUmwelt(
        lens=lens,
        dna=E_GENT_DNA,
        gravity=(),
    )


def create_neutral_umwelt() -> MetaphorUmwelt:
    """Create a neutral umwelt with no constraints."""
    dna = MetaphorDNA()
    lens = MetaphorLens(
        name="neutral_lens",
        constraints=(),
        dna=dna,
    )
    return MetaphorUmwelt(
        lens=lens,
        dna=dna,
        gravity=(),
    )
