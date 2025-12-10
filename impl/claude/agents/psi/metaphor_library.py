"""
Psi-gent MetaphorLibrary: The catalog of familiar metaphor spaces.

The "puppet store" of semantic spaces - archetypal metaphors
that novel problems can be projected into.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .types import Metaphor, MetaphorOperation, Novel


# =============================================================================
# MetaphorLibrary Protocol
# =============================================================================


@runtime_checkable
class MetaphorLibrary(Protocol):
    """
    Protocol for metaphor storage and retrieval.

    Implementations may be:
    - StaticMetaphorLibrary: Fixed dictionary (Phase 2)
    - HolographicMetaphorLibrary: M-gent fuzzy recall (Phase 7)
    """

    def fetch_candidates(
        self, problem: Novel, limit: int = 5
    ) -> list[WeightedMetaphor]:
        """Fetch candidate metaphors for a problem."""
        ...

    def get(self, metaphor_id: str) -> Metaphor | None:
        """Get a specific metaphor by ID."""
        ...

    def register(self, metaphor: Metaphor) -> None:
        """Register a new metaphor."""
        ...

    def update_usage(self, metaphor_id: str, success: bool) -> None:
        """Update usage statistics for a metaphor."""
        ...


# =============================================================================
# Weighted Metaphor (for ranking)
# =============================================================================


@dataclass(frozen=True)
class WeightedMetaphor:
    """A metaphor with a relevance weight."""

    metaphor: Metaphor
    weight: float  # 0.0 to 1.0, higher = more relevant

    def __lt__(self, other: WeightedMetaphor) -> bool:
        return self.weight < other.weight


# =============================================================================
# Static MetaphorLibrary (Phase 2)
# =============================================================================


class StaticMetaphorLibrary:
    """
    Static dictionary-based metaphor library.

    This is the simple Phase 2 implementation.
    Later phases add holographic memory for fuzzy matching.
    """

    def __init__(self, metaphors: dict[str, Metaphor] | None = None):
        self._metaphors: dict[str, Metaphor] = metaphors or {}
        self._domain_index: dict[str, list[str]] = {}  # domain -> metaphor_ids
        self._rebuild_indices()

    def _rebuild_indices(self) -> None:
        """Rebuild the domain index."""
        self._domain_index.clear()
        for m in self._metaphors.values():
            if m.domain not in self._domain_index:
                self._domain_index[m.domain] = []
            self._domain_index[m.domain].append(m.metaphor_id)

    def fetch_candidates(
        self, problem: Novel, limit: int = 5
    ) -> list[WeightedMetaphor]:
        """
        Fetch candidate metaphors for a problem.

        Strategy:
        1. Prefer metaphors from same domain
        2. Score by tractability * generality * success_rate
        3. Return top N by score
        """
        candidates: list[WeightedMetaphor] = []

        for metaphor in self._metaphors.values():
            weight = self._score_metaphor(problem, metaphor)
            candidates.append(WeightedMetaphor(metaphor=metaphor, weight=weight))

        # Sort by weight descending
        candidates.sort(reverse=True)

        return candidates[:limit]

    def _score_metaphor(self, problem: Novel, metaphor: Metaphor) -> float:
        """
        Score a metaphor's fit for a problem.

        Higher score = better fit.
        """
        score = 0.5  # Base score

        # Domain match bonus
        if metaphor.domain == problem.domain:
            score += 0.3
        elif problem.domain in metaphor.related_metaphors:
            score += 0.1

        # Tractability for complex problems
        if problem.complexity > 0.7:
            score += metaphor.tractability * 0.2

        # Generality for novel problems
        if problem.entropy > 0.7:
            score += metaphor.generality * 0.2

        # Success rate
        score += metaphor.success_rate * 0.2

        # Normalize to 0-1
        return min(1.0, max(0.0, score))

    def get(self, metaphor_id: str) -> Metaphor | None:
        """Get a specific metaphor by ID."""
        return self._metaphors.get(metaphor_id)

    def register(self, metaphor: Metaphor) -> None:
        """Register a new metaphor."""
        self._metaphors[metaphor.metaphor_id] = metaphor
        self._rebuild_indices()

    def update_usage(self, metaphor_id: str, success: bool) -> None:
        """Update usage statistics for a metaphor."""
        if metaphor_id in self._metaphors:
            old = self._metaphors[metaphor_id]
            self._metaphors[metaphor_id] = old.increment_usage(success)

    def get_by_domain(self, domain: str) -> list[Metaphor]:
        """Get all metaphors in a domain."""
        ids = self._domain_index.get(domain, [])
        return [self._metaphors[mid] for mid in ids if mid in self._metaphors]

    def all_metaphors(self) -> list[Metaphor]:
        """Get all registered metaphors."""
        return list(self._metaphors.values())

    def __len__(self) -> int:
        return len(self._metaphors)


# =============================================================================
# Standard Metaphor Catalog
# =============================================================================


def create_standard_library() -> StaticMetaphorLibrary:
    """
    Create a library with standard metaphors.

    These are the archetypes that problems are projected into.
    """
    metaphors = {
        # Strategy metaphors
        "military_strategy": Metaphor(
            metaphor_id="military_strategy",
            name="MilitaryStrategy",
            domain="strategy",
            description="Problems as military campaigns with positions, forces, and objectives",
            operations=(
                MetaphorOperation(
                    name="flank",
                    description="Approach from unexpected angle",
                    signature="Position -> Position",
                ),
                MetaphorOperation(
                    name="siege",
                    description="Sustained pressure on fortified position",
                    signature="Target -> Weakened",
                ),
                MetaphorOperation(
                    name="retreat",
                    description="Strategic withdrawal to better position",
                    signature="Position -> SaferPosition",
                ),
                MetaphorOperation(
                    name="concentrate_force",
                    description="Focus resources on single point",
                    signature="Distributed -> Concentrated",
                ),
            ),
            tractability=0.8,
            generality=0.6,
            related_metaphors=("game_theory", "economics"),
        ),
        # Scientific metaphors
        "thermodynamics": Metaphor(
            metaphor_id="thermodynamics",
            name="Thermodynamics",
            domain="physics",
            description="Problems as energy flows and entropy changes",
            operations=(
                MetaphorOperation(
                    name="heat_flow",
                    description="Energy flows from hot to cold",
                    signature="(Hot, Cold) -> Equilibrium",
                ),
                MetaphorOperation(
                    name="entropy_increase",
                    description="Disorder naturally increases",
                    signature="Ordered -> Disordered",
                ),
                MetaphorOperation(
                    name="equilibrium",
                    description="System reaches stable state",
                    signature="Dynamic -> Stable",
                ),
                MetaphorOperation(
                    name="phase_transition",
                    description="Qualitative change at threshold",
                    signature="State -> DifferentState",
                ),
            ),
            tractability=0.9,
            generality=0.7,
            related_metaphors=("economics", "biological_system"),
        ),
        # Biological metaphors
        "biological_system": Metaphor(
            metaphor_id="biological_system",
            name="BiologicalSystem",
            domain="biology",
            description="Problems as living systems with growth, adaptation, and homeostasis",
            operations=(
                MetaphorOperation(
                    name="growth",
                    description="Organic increase in complexity",
                    signature="Simple -> Complex",
                ),
                MetaphorOperation(
                    name="apoptosis",
                    description="Programmed death of components",
                    signature="Component -> Removed",
                ),
                MetaphorOperation(
                    name="immunity",
                    description="Defense against foreign elements",
                    signature="Threat -> Neutralized",
                ),
                MetaphorOperation(
                    name="adaptation",
                    description="Change in response to environment",
                    signature="(Organism, Environment) -> AdaptedOrganism",
                ),
                MetaphorOperation(
                    name="symbiosis",
                    description="Mutually beneficial relationship",
                    signature="(A, B) -> BenefitsBoth",
                ),
            ),
            tractability=0.75,
            generality=0.8,
            related_metaphors=("thermodynamics", "ecosystem"),
        ),
        # Game theory metaphors
        "game_theory": Metaphor(
            metaphor_id="game_theory",
            name="GameTheory",
            domain="mathematics",
            description="Problems as strategic games between rational agents",
            operations=(
                MetaphorOperation(
                    name="nash_equilibrium",
                    description="Stable point where no player gains by changing",
                    signature="Game -> EquilibriumState",
                ),
                MetaphorOperation(
                    name="pareto_optimal",
                    description="No improvement without hurting someone",
                    signature="State -> ParetoFrontier",
                ),
                MetaphorOperation(
                    name="minimax",
                    description="Minimize maximum possible loss",
                    signature="RiskyState -> SaferState",
                ),
                MetaphorOperation(
                    name="dominant_strategy",
                    description="Find always-best action",
                    signature="Options -> BestOption",
                ),
            ),
            tractability=0.95,
            generality=0.5,
            related_metaphors=("military_strategy", "economics"),
        ),
        # Narrative metaphors
        "hero_journey": Metaphor(
            metaphor_id="hero_journey",
            name="HeroJourney",
            domain="narrative",
            description="Problems as hero's journey with call, ordeal, and return",
            operations=(
                MetaphorOperation(
                    name="call",
                    description="Initial challenge/invitation",
                    signature="OrdinaryWorld -> CallToAdventure",
                ),
                MetaphorOperation(
                    name="threshold",
                    description="Crossing into unknown territory",
                    signature="Known -> Unknown",
                ),
                MetaphorOperation(
                    name="abyss",
                    description="Confronting deepest fear",
                    signature="Hero -> TransformedHero",
                ),
                MetaphorOperation(
                    name="return",
                    description="Bringing gift back to ordinary world",
                    signature="TransformedHero -> IntegratedHero",
                ),
            ),
            tractability=0.7,
            generality=0.9,
            related_metaphors=("biological_system",),
        ),
        # Economics metaphors
        "economics": Metaphor(
            metaphor_id="economics",
            name="Economics",
            domain="economics",
            description="Problems as resource allocation with scarcity and trade-offs",
            operations=(
                MetaphorOperation(
                    name="trade",
                    description="Exchange resources for mutual benefit",
                    signature="(A, B) -> (A', B')",
                ),
                MetaphorOperation(
                    name="invest",
                    description="Sacrifice now for future return",
                    signature="Resource -> FutureValue",
                ),
                MetaphorOperation(
                    name="arbitrage",
                    description="Exploit price differences",
                    signature="Difference -> Profit",
                ),
                MetaphorOperation(
                    name="diversify",
                    description="Spread risk across options",
                    signature="Concentrated -> Distributed",
                ),
            ),
            tractability=0.85,
            generality=0.75,
            related_metaphors=("game_theory", "thermodynamics"),
        ),
        # Architecture metaphors
        "architecture": Metaphor(
            metaphor_id="architecture",
            name="Architecture",
            domain="engineering",
            description="Problems as structures with foundations, load-bearing elements, and facades",
            operations=(
                MetaphorOperation(
                    name="foundation",
                    description="Establish stable base",
                    signature="Ground -> Foundation",
                ),
                MetaphorOperation(
                    name="scaffold",
                    description="Temporary support for construction",
                    signature="Incomplete -> Scaffolded",
                ),
                MetaphorOperation(
                    name="load_distribute",
                    description="Spread weight across supports",
                    signature="ConcentratedLoad -> DistributedLoad",
                ),
                MetaphorOperation(
                    name="modularize",
                    description="Separate into independent units",
                    signature="Monolithic -> Modular",
                ),
            ),
            tractability=0.85,
            generality=0.6,
            related_metaphors=("biological_system",),
        ),
        # Ecosystem metaphors
        "ecosystem": Metaphor(
            metaphor_id="ecosystem",
            name="Ecosystem",
            domain="ecology",
            description="Problems as ecosystems with niches, competition, and balance",
            operations=(
                MetaphorOperation(
                    name="niche",
                    description="Find unique role in system",
                    signature="Generic -> Specialized",
                ),
                MetaphorOperation(
                    name="compete",
                    description="Struggle for limited resources",
                    signature="(A, B, Resource) -> Winner",
                ),
                MetaphorOperation(
                    name="balance",
                    description="Achieve sustainable equilibrium",
                    signature="Imbalanced -> Balanced",
                ),
                MetaphorOperation(
                    name="cascade",
                    description="Changes propagate through system",
                    signature="LocalChange -> SystemChange",
                ),
            ),
            tractability=0.7,
            generality=0.85,
            related_metaphors=("biological_system", "economics"),
        ),
    }

    return StaticMetaphorLibrary(metaphors)
