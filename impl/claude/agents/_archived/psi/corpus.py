"""
Psi-gent v3.0 Metaphor Corpus.

Manages static + dynamic metaphor collection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from .types import Example, Metaphor, Operation, validate_metaphor

# =============================================================================
# Corpus Management
# =============================================================================


@dataclass
class MetaphorCorpus:
    """Manages the metaphor collection."""

    static: list[Metaphor] = field(default_factory=list)
    dynamic: list[Metaphor] = field(default_factory=list)
    embeddings: dict[str, tuple[float, ...]] = field(default_factory=dict)

    @property
    def all_ids(self) -> set[str]:
        """All metaphor IDs in the corpus."""
        return {m.id for m in self}

    def add(self, metaphor: Metaphor, source: str = "generated") -> None:
        """Add a new metaphor to the corpus."""
        if metaphor.id in self.all_ids:
            raise ValueError(f"Metaphor {metaphor.id} already exists")
        valid, issues = validate_generated_metaphor(metaphor)
        if not valid:
            raise ValueError(f"Invalid metaphor: {issues}")
        self.dynamic.append(metaphor)
        if metaphor.embedding:
            self.embeddings[metaphor.id] = metaphor.embedding

    def get(self, metaphor_id: str) -> Metaphor | None:
        """Get metaphor by ID."""
        for m in self:
            if m.id == metaphor_id:
                return m
        return None

    def remove(self, metaphor_id: str) -> bool:
        """Remove a dynamic metaphor. Returns True if removed."""
        for i, m in enumerate(self.dynamic):
            if m.id == metaphor_id:
                self.dynamic.pop(i)
                self.embeddings.pop(metaphor_id, None)
                return True
        return False

    def __iter__(self) -> Iterator[Metaphor]:
        yield from self.static
        yield from self.dynamic

    def __len__(self) -> int:
        return len(self.static) + len(self.dynamic)


def validate_generated_metaphor(metaphor: Metaphor) -> tuple[bool, list[str]]:
    """Check if a generated metaphor is usable."""
    issues = validate_metaphor(metaphor)

    # Additional checks for generated metaphors
    if len(metaphor.operations) < 2:
        issues.append("Too few operations (need at least 2)")

    valid = not any(
        "Too few" in i or "has no effects" in i or "has no operations" in i
        for i in issues
    )
    return valid, issues


# =============================================================================
# Standard Corpus
# =============================================================================


def create_standard_corpus() -> MetaphorCorpus:
    """Create the standard metaphor corpus."""
    return MetaphorCorpus(static=list(STANDARD_CORPUS))


# -----------------------------------------------------------------------------
# Plumbing Metaphor
# -----------------------------------------------------------------------------

PLUMBING = Metaphor(
    id="plumbing",
    name="Plumbing",
    domain="engineering",
    description="Systems of pipes, valves, and reservoirs that control flow. "
    "Flow moves from high pressure to low pressure. Constrictions reduce throughput. "
    "Reservoirs buffer demand spikes. Leaks waste resources.",
    operations=(
        Operation(
            name="locate_constriction",
            description="Find where flow is restricted in the system",
            signature="system with low flow -> location of restriction",
            preconditions=(
                "system exhibits reduced flow",
                "flow was previously higher or expected to be higher",
            ),
            effects=(
                "constriction location is identified",
                "flow pattern before/after constriction is known",
            ),
        ),
        Operation(
            name="widen_pipe",
            description="Increase capacity at a specific point",
            signature="location -> modified system",
            preconditions=(
                "constriction location is known",
                "widening is physically possible",
            ),
            effects=(
                "flow capacity at location increases",
                "potential upstream/downstream effects",
            ),
        ),
        Operation(
            name="add_reservoir",
            description="Add buffer storage to smooth demand spikes",
            signature="system -> system with reservoir",
            preconditions=("demand is spiky", "storage location exists"),
            effects=("demand spikes are buffered", "downstream flow is smoothed"),
        ),
        Operation(
            name="add_bypass",
            description="Create alternative flow path around blockage",
            signature="blocked location -> system with bypass",
            preconditions=("blockage location is known", "alternative route exists"),
            effects=(
                "flow can route around blockage",
                "total system capacity may increase",
            ),
        ),
        Operation(
            name="seal_leak",
            description="Stop unintended flow escape",
            signature="leak location -> sealed system",
            preconditions=("leak exists", "leak location is known"),
            effects=("resource waste stops", "downstream flow increases"),
        ),
    ),
    examples=(
        Example(
            situation="Website is slow under load",
            application="Traced requests through system, found database queries were the constriction",
            outcome="Added connection pooling (widened pipe) and response caching (reservoir)",
        ),
        Example(
            situation="Memory usage keeps growing",
            application="Profiled allocations, found unreleased connections (leak)",
            outcome="Fixed connection cleanup (sealed leak), memory stabilized",
        ),
    ),
)


# -----------------------------------------------------------------------------
# Ecosystem Metaphor
# -----------------------------------------------------------------------------

ECOSYSTEM = Metaphor(
    id="ecosystem",
    name="Ecosystem",
    domain="biology",
    description="Network of organisms interacting with environment. "
    "Organisms occupy niches. Symbiosis benefits multiple parties. "
    "Invasive species disrupt balance. Biodiversity provides resilience.",
    operations=(
        Operation(
            name="identify_niche",
            description="Find the role an entity plays in the system",
            signature="entity -> niche description",
            preconditions=("entity exists in system",),
            effects=("entity's relationships are mapped", "dependencies are known"),
        ),
        Operation(
            name="strengthen_symbiosis",
            description="Improve mutual benefit between cooperating entities",
            signature="entity pair -> strengthened relationship",
            preconditions=("two entities have cooperative relationship",),
            effects=("both entities benefit more", "relationship is more stable"),
        ),
        Operation(
            name="remove_invasive",
            description="Eliminate entity that disrupts balance",
            signature="invasive entity -> restored system",
            preconditions=(
                "invasive entity is identified",
                "removal is possible",
            ),
            effects=("native entities recover", "balance is restored"),
        ),
        Operation(
            name="increase_biodiversity",
            description="Add variety to improve resilience",
            signature="homogeneous system -> diverse system",
            preconditions=("system is too homogeneous", "alternatives exist"),
            effects=(
                "system becomes more resilient",
                "single points of failure reduced",
            ),
        ),
    ),
    examples=(
        Example(
            situation="Team depends entirely on one senior engineer",
            application="Identified single-species ecosystem (knowledge monopoly)",
            outcome="Cross-trained team members (increased biodiversity)",
        ),
        Example(
            situation="New tool causing conflicts with existing workflow",
            application="Recognized invasive species pattern",
            outcome="Removed tool and restored previous workflow (removed invasive)",
        ),
    ),
)


# -----------------------------------------------------------------------------
# Traffic Metaphor
# -----------------------------------------------------------------------------

TRAFFIC = Metaphor(
    id="traffic",
    name="Traffic",
    domain="transportation",
    description="Movement of vehicles through a network. "
    "Congestion occurs at bottlenecks. Traffic lights regulate flow. "
    "Route planning optimizes travel. Accidents block lanes.",
    operations=(
        Operation(
            name="identify_bottleneck",
            description="Find where traffic congests",
            signature="network -> congestion point",
            preconditions=("flow is slower than expected",),
            effects=("bottleneck location is known", "cause of slowdown identified"),
        ),
        Operation(
            name="add_lane",
            description="Increase capacity on a route",
            signature="route -> widened route",
            preconditions=("route is at capacity", "expansion is possible"),
            effects=("throughput increases", "congestion reduces"),
        ),
        Operation(
            name="install_signal",
            description="Add traffic control to regulate flow",
            signature="intersection -> regulated intersection",
            preconditions=("intersection has conflicting flows",),
            effects=("flows are coordinated", "conflicts are prevented"),
        ),
        Operation(
            name="reroute_traffic",
            description="Direct flow through alternative paths",
            signature="blocked route -> alternative route",
            preconditions=("primary route is blocked", "alternatives exist"),
            effects=("flow continues", "blocked route can recover"),
        ),
    ),
    examples=(
        Example(
            situation="API calls timing out during peak hours",
            application="Identified traffic jam at authentication service",
            outcome="Added rate limiting (signal) and horizontal scaling (more lanes)",
        ),
    ),
)


# -----------------------------------------------------------------------------
# Medicine Metaphor
# -----------------------------------------------------------------------------

MEDICINE = Metaphor(
    id="medicine",
    name="Medicine",
    domain="healthcare",
    description="Diagnosis and treatment of disease. "
    "Symptoms indicate underlying conditions. Treatment addresses root cause. "
    "Side effects must be managed. Prevention beats cure.",
    operations=(
        Operation(
            name="diagnose",
            description="Identify the underlying condition from symptoms",
            signature="symptoms -> diagnosis",
            preconditions=("symptoms are observed",),
            effects=("root cause is hypothesized", "treatment options emerge"),
        ),
        Operation(
            name="treat",
            description="Apply intervention to address condition",
            signature="diagnosis -> treatment plan",
            preconditions=("diagnosis exists", "treatment is available"),
            effects=("condition improves", "side effects may occur"),
        ),
        Operation(
            name="monitor",
            description="Track response to treatment",
            signature="treatment -> status update",
            preconditions=("treatment is ongoing",),
            effects=("progress is known", "adjustments can be made"),
        ),
        Operation(
            name="vaccinate",
            description="Prevent condition before it occurs",
            signature="healthy system -> protected system",
            preconditions=("vulnerability exists", "prevention is possible"),
            effects=("resistance to condition", "future infections prevented"),
        ),
    ),
    examples=(
        Example(
            situation="Intermittent errors in production",
            application="Treated symptoms (restarting) but needed diagnosis",
            outcome="Root cause analysis found race condition (diagnosed), fixed synchronization (treated)",
        ),
    ),
)


# -----------------------------------------------------------------------------
# Architecture Metaphor
# -----------------------------------------------------------------------------

ARCHITECTURE = Metaphor(
    id="architecture",
    name="Architecture",
    domain="construction",
    description="Design and construction of buildings. "
    "Foundations support everything above. Load-bearing elements cannot be removed. "
    "Renovation must respect structure. Form follows function.",
    operations=(
        Operation(
            name="assess_foundation",
            description="Evaluate the stability of underlying support",
            signature="structure -> foundation report",
            preconditions=("structure exists",),
            effects=(
                "foundation strength is known",
                "weight capacity is determined",
            ),
        ),
        Operation(
            name="identify_load_bearing",
            description="Find elements that cannot be safely removed",
            signature="structure -> critical elements",
            preconditions=("structure is built",),
            effects=("critical dependencies mapped", "safe changes identified"),
        ),
        Operation(
            name="renovate",
            description="Modify structure while maintaining integrity",
            signature="structure + plan -> modified structure",
            preconditions=(
                "load-bearing elements are known",
                "plan respects constraints",
            ),
            effects=("structure is updated", "integrity is maintained"),
        ),
        Operation(
            name="add_support",
            description="Reinforce structure to handle additional load",
            signature="location -> reinforced structure",
            preconditions=("additional load is planned", "reinforcement is possible"),
            effects=("capacity increases", "stability improves"),
        ),
    ),
    examples=(
        Example(
            situation="Need to refactor core authentication module",
            application="Identified auth as load-bearing (everything depends on it)",
            outcome="Planned renovation with temporary supports (feature flags)",
        ),
    ),
)


# -----------------------------------------------------------------------------
# Gardening Metaphor
# -----------------------------------------------------------------------------

GARDENING = Metaphor(
    id="gardening",
    name="Gardening",
    domain="horticulture",
    description="Cultivation of plants. "
    "Growth requires nurturing. Pruning encourages healthy development. "
    "Weeds compete for resources. Seasons affect what's possible.",
    operations=(
        Operation(
            name="plant",
            description="Establish new growth",
            signature="soil + seed -> planted area",
            preconditions=("soil is prepared", "conditions are suitable"),
            effects=("growth potential exists", "nurturing is required"),
        ),
        Operation(
            name="prune",
            description="Remove growth to improve health",
            signature="overgrown plant -> shaped plant",
            preconditions=("plant has excess growth",),
            effects=("energy redirected to productive growth", "shape improves"),
        ),
        Operation(
            name="weed",
            description="Remove competing growth",
            signature="garden with weeds -> clean garden",
            preconditions=("weeds exist",),
            effects=("resources freed", "main plants can thrive"),
        ),
        Operation(
            name="fertilize",
            description="Add nutrients to support growth",
            signature="depleted soil -> enriched soil",
            preconditions=("soil needs nutrients",),
            effects=("growth accelerates", "health improves"),
        ),
    ),
    examples=(
        Example(
            situation="Codebase has accumulated technical debt",
            application="Recognized need for pruning (dead code) and weeding (deprecated dependencies)",
            outcome="Removed unused modules, updated dependencies, growth resumed",
        ),
    ),
)


# -----------------------------------------------------------------------------
# Standard Corpus Collection
# -----------------------------------------------------------------------------

STANDARD_CORPUS: tuple[Metaphor, ...] = (
    PLUMBING,
    ECOSYSTEM,
    TRAFFIC,
    MEDICINE,
    ARCHITECTURE,
    GARDENING,
)
