"""
Exploration Harness Types: Core data structures for navigation and evidence.

This module defines the types used across the exploration harness:
- Trail and TrailStep: Navigation history as replayable artifacts
- ContextNode and ContextGraph: Typed-hypergraph navigation
- Evidence types: Claims, evidence from exploration
- Result types: NavigationResult, LoopStatus, CommitmentResult

Design Note:
    The typed-hypergraph is the conceptual model (spec/protocols/typed-hypergraph.md).
    The exploration harness wraps it with safety and evidence (spec/protocols/exploration-harness.md).
    These types bridge both specs.

Teaching:
    gotcha: Trail is immutable—each step returns a new Trail.
            This enables trail sharing without mutation concerns.

    gotcha: ContextNode.content() is async because it's lazy-loaded.
            The graph is navigable without loading all content upfront.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    import numpy as np


# =============================================================================
# Enums
# =============================================================================


class LoopStatus(Enum):
    """Result of loop detection check."""

    OK = auto()  # No loop detected
    EXACT_LOOP = auto()  # Same node visited twice (hash match)
    SEMANTIC_LOOP = auto()  # Similar nodes (embedding similarity > 0.95)
    STRUCTURAL_LOOP = auto()  # Repeating navigation pattern (A->B->A->B)


class CommitmentLevel(str, Enum):
    """
    Levels of claim commitment based on evidence strength.

    Each level has requirements (see ASHCCommitment):
    - TENTATIVE: Any evidence
    - MODERATE: 3+ evidence, 1+ strong
    - STRONG: 5+ evidence, 2+ strong, no counter
    - DEFINITIVE: 10+ evidence, 5+ strong, all counter addressed
    """

    TENTATIVE = "tentative"
    MODERATE = "moderate"
    STRONG = "strong"
    DEFINITIVE = "definitive"


class CommitmentResult(str, Enum):
    """Result of attempting to commit a claim."""

    APPROVED = "approved"
    INSUFFICIENT_QUANTITY = "insufficient_quantity"
    INSUFFICIENT_QUALITY = "insufficient_quality"
    UNADDRESSED_COUNTEREVIDENCE = "unaddressed_counterevidence"
    TRAIL_DOES_NOT_SUPPORT = "trail_does_not_support"


class EvidenceStrength(str, Enum):
    """Strength classification of a piece of evidence."""

    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"


# =============================================================================
# Observer (Phenomenological Context)
# =============================================================================


@dataclass(frozen=True)
class Observer:
    """
    The observer determines what edges are visible in the hypergraph.

    Different observers see different affordances from the same node.
    This is the phenomenological insight: what exists depends on who's looking.
    """

    id: str
    archetype: str  # "developer", "security_auditor", "architect", "newcomer"
    capabilities: frozenset[str] = frozenset()  # What this observer can perceive
    metadata: dict[str, str] = field(default_factory=dict)


# =============================================================================
# Trail Types (Navigation History)
# =============================================================================


@dataclass(frozen=True)
class TrailStep:
    """A single step in a navigation trail."""

    node: str  # AGENTESE path of the node
    edge_taken: str | None  # The hyperedge followed to get here (None for start)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    annotation: str | None = None  # Optional annotation at this step


@dataclass(frozen=True)
class Trail:
    """
    Replayable path through the hypergraph.

    Inspired by Vannevar Bush's Memex trails.
    A trail IS evidence—every navigation creates proof.

    Laws:
        1. Immutability: Each step returns a new Trail
        2. Monotonicity: Steps can only be added, not removed
        3. Replayability: Any trail can be replayed from start
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    created_by: str = ""  # Observer ID
    steps: tuple[TrailStep, ...] = ()
    annotations: dict[int, str] = field(default_factory=dict)  # step_index -> text

    def add_step(
        self,
        node: str,
        edge_taken: str | None,
        annotation: str | None = None,
    ) -> Trail:
        """Add a step, returning new Trail (immutable)."""
        new_step = TrailStep(
            node=node,
            edge_taken=edge_taken,
            annotation=annotation,
        )
        return Trail(
            id=self.id,
            name=self.name,
            created_by=self.created_by,
            steps=self.steps + (new_step,),
            annotations=self.annotations,
        )

    def annotate(self, step_index: int, text: str) -> Trail:
        """Add annotation at a step, returning new Trail."""
        new_annotations = dict(self.annotations)
        new_annotations[step_index] = text
        return Trail(
            id=self.id,
            name=self.name,
            created_by=self.created_by,
            steps=self.steps,
            annotations=new_annotations,
        )

    @property
    def nodes_visited(self) -> set[str]:
        """Set of all nodes visited in this trail."""
        return {step.node for step in self.steps}

    @property
    def edges_followed(self) -> list[str]:
        """List of edges followed (in order)."""
        return [step.edge_taken for step in self.steps if step.edge_taken]

    def serialize(self) -> str:
        """Serialize trail for evidence storage."""
        lines = [f"Trail: {self.name or self.id}"]
        for i, step in enumerate(self.steps):
            edge_str = f" --[{step.edge_taken}]--> " if step.edge_taken else "(start) "
            lines.append(f"  {i}: {edge_str}{step.node}")
            if i in self.annotations:
                lines.append(f"      ^ {self.annotations[i]}")
        return "\n".join(lines)


# =============================================================================
# Context Node and Graph (Typed-Hypergraph)
# =============================================================================


@dataclass(eq=True)
class ContextNode:
    """
    A node in the typed-hypergraph.

    Content is lazy-loaded—the graph is navigable without loading everything.
    Identity is based on path only (for use in sets).
    """

    path: str  # AGENTESE path (e.g., "world.auth_middleware")
    holon: str  # Entity name
    _content: str | None = field(default=None, repr=False, compare=False)
    _content_loader: Callable[[], Awaitable[str]] | None = field(
        default=None, repr=False, compare=False
    )

    def __hash__(self) -> int:
        """Hash based on path for use in sets."""
        return hash(self.path)

    async def content(self) -> str:
        """Load content only when needed (lazy)."""
        if self._content is None and self._content_loader:
            self._content = await self._content_loader()
        return self._content or ""

    def edges(self, observer: Observer) -> dict[str, list[ContextNode]]:
        """
        Available hyperedges from this node.

        Observer-dependent: different observers see different edges.
        Delegates to hyperedge_resolvers for actual edge computation.

        Teaching:
            gotcha: This returns edge TYPES that are available, not resolved edges.
                    Call follow() to get actual destinations.
        """
        # Import here to avoid circular dependency
        try:
            from protocols.agentese.contexts.hyperedge_resolvers import (
                get_resolver_registry,
            )

            registry = get_resolver_registry()
            edge_types = registry.list_edge_types()

            # Return empty lists for each edge type
            # The actual resolution happens in follow()
            return {edge_type: [] for edge_type in edge_types}
        except ImportError:
            # Fallback if resolvers not available
            return {}

    async def follow(self, aspect: str, observer: Observer) -> list[ContextNode]:
        """
        Traverse a hyperedge using AGENTESE resolvers.

        Equivalent to: logos(f"{self.path}.{aspect}", observer)

        Teaching:
            gotcha: This now uses real hyperedge_resolvers! Navigation is live.
                    (Evidence: test_state.py::test_navigate_follows_real_edges)
        """
        try:
            from protocols.agentese.contexts.hyperedge_resolvers import (
                _get_project_root,
                resolve_hyperedge,
            )
            from protocols.agentese.contexts.self_context import (
                ContextNode as AgentContextNode,
            )

            # Create an AgentContextNode to use the resolver
            agent_node = AgentContextNode(path=self.path, holon=self.holon)

            # Resolve the hyperedge
            root = _get_project_root()
            agent_results = await resolve_hyperedge(agent_node, aspect, root)

            # Convert back to exploration ContextNode
            return [ContextNode(path=n.path, holon=n.holon) for n in agent_results]
        except ImportError:
            # Fallback to placeholder if resolvers not available
            return []


@dataclass
class ContextGraph:
    """
    The navigable typed-hypergraph.

    Not a pre-loaded structure—a navigation protocol.
    """

    focus: set[ContextNode] = field(default_factory=set)  # Current position(s)
    trail: Trail = field(default_factory=Trail)  # Navigation history
    observer: Observer = field(
        default_factory=lambda: Observer(id="default", archetype="developer")
    )

    async def navigate(self, aspect: str) -> ContextGraph:
        """Follow a hyperedge from all focused nodes."""
        new_focus: set[ContextNode] = set()

        for node in self.focus:
            destinations = await node.follow(aspect, self.observer)
            new_focus.update(destinations)

        # Record the navigation in trail
        new_trail = self.trail
        for node in new_focus:
            new_trail = new_trail.add_step(node.path, aspect)

        return ContextGraph(
            focus=new_focus,
            trail=new_trail,
            observer=self.observer,
        )

    async def affordances(self) -> dict[str, int]:
        """What hyperedges can we follow? {aspect: destination_count}"""
        result: dict[str, int] = {}
        for node in self.focus:
            edges = node.edges(self.observer)
            for aspect, destinations in edges.items():
                result[aspect] = result.get(aspect, 0) + len(destinations)
        return result

    def backtrack(self) -> ContextGraph:
        """Go back along the trail."""
        if len(self.trail.steps) < 2:
            return self

        # Remove last step and restore previous focus
        new_steps = self.trail.steps[:-1]
        new_trail = Trail(
            id=self.trail.id,
            name=self.trail.name,
            created_by=self.trail.created_by,
            steps=new_steps,
            annotations=self.trail.annotations,
        )

        # Reconstruct focus from previous step
        # (Simplified: in real impl would need to track focus history)
        return ContextGraph(
            focus=self.focus,  # Would need proper focus restoration
            trail=new_trail,
            observer=self.observer,
        )


# =============================================================================
# Evidence Types (Exploration-Specific)
# =============================================================================


@dataclass(frozen=True)
class Claim:
    """A claim that requires evidence to commit."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    statement: str = ""  # The claim text
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    commitment_level: CommitmentLevel | None = None
    addressed_counter: frozenset[str] = frozenset()  # IDs of addressed counterevidence


@dataclass(frozen=True)
class Evidence:
    """
    A piece of evidence from exploration.

    Distinguished from ashc/evidence.py which is about compilation evidence.
    This is about trail-based exploration evidence.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    claim: str = ""  # What claim this evidence supports
    source: str = "exploration_trail"  # Where this evidence came from
    content: str = ""  # The evidence content (serialized trail, observation, etc.)
    strength: EvidenceStrength = EvidenceStrength.MODERATE
    metadata: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class Counterevidence:
    """Evidence that contradicts a claim."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    claim_id: str = ""  # The claim this contradicts
    content: str = ""
    addressed: bool = False  # Has this been addressed?
    addressed_by: str | None = None  # What addressed it


# =============================================================================
# Navigation Result
# =============================================================================


@dataclass
class NavigationResult:
    """Result of a navigation attempt."""

    success: bool
    graph: ContextGraph | None = None
    budget_exhausted: bool = False
    loop_detected: LoopStatus | None = None
    error_message: str | None = None

    @classmethod
    def ok(cls, graph: ContextGraph) -> NavigationResult:
        """Successful navigation."""
        return cls(success=True, graph=graph)

    @classmethod
    def budget_exhausted_result(cls, reason: str) -> NavigationResult:
        """Navigation blocked by budget."""
        return cls(
            success=False,
            budget_exhausted=True,
            error_message=f"Budget exhausted: {reason}",
        )

    @classmethod
    def loop_detected_result(cls, status: LoopStatus) -> NavigationResult:
        """Navigation blocked by loop detection."""
        return cls(
            success=False,
            loop_detected=status,
            error_message=f"Loop detected: {status.name}",
        )


# =============================================================================
# Portal Expansion Result
# =============================================================================


@dataclass
class PortalExpansionResult:
    """
    Result of a portal expansion attempt.

    Used by ExplorationHarness.expand_portal() to return expansion status
    along with any evidence, loop detection, or budget info.
    """

    success: bool
    portal_path: str = ""
    files_opened: tuple[str, ...] = ()
    budget_exhausted: bool = False
    loop_detected: LoopStatus | None = None
    evidence_created: "Evidence | None" = None
    error_message: str | None = None

    @classmethod
    def ok(
        cls,
        portal_path: str,
        files_opened: list[str] | tuple[str, ...],
        evidence: "Evidence | None" = None,
    ) -> "PortalExpansionResult":
        """Successful portal expansion."""
        return cls(
            success=True,
            portal_path=portal_path,
            files_opened=tuple(files_opened) if isinstance(files_opened, list) else files_opened,
            evidence_created=evidence,
        )

    @classmethod
    def budget_exhausted_result(cls, portal_path: str, reason: str) -> "PortalExpansionResult":
        """Expansion blocked by budget."""
        return cls(
            success=False,
            portal_path=portal_path,
            budget_exhausted=True,
            error_message=f"Budget exhausted: {reason}",
        )

    @classmethod
    def loop_detected_result(cls, portal_path: str, status: LoopStatus) -> "PortalExpansionResult":
        """Expansion blocked by loop detection."""
        return cls(
            success=False,
            portal_path=portal_path,
            loop_detected=status,
            error_message=f"Loop detected: {status.name}",
        )

    @classmethod
    def expansion_failed_result(cls, portal_path: str, reason: str) -> "PortalExpansionResult":
        """Expansion failed for other reasons."""
        return cls(
            success=False,
            portal_path=portal_path,
            error_message=reason,
        )


__all__ = [
    # Enums
    "LoopStatus",
    "CommitmentLevel",
    "CommitmentResult",
    "EvidenceStrength",
    # Observer
    "Observer",
    # Trail
    "TrailStep",
    "Trail",
    # Context
    "ContextNode",
    "ContextGraph",
    # Evidence
    "Claim",
    "Evidence",
    "Counterevidence",
    # Results
    "NavigationResult",
    "PortalExpansionResult",
]
