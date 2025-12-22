"""
Exploration Harness: Safety and evidence wrapper for hypergraph navigation.

The harness wraps the typed-hypergraph with:
1. Navigation budget (bounded exploration)
2. Loop detection (prevent spinning)
3. Evidence collection (exploration creates proof)
4. Commitment protocol (claims require evidence)

The harness doesn't constrain—it witnesses. Every trail is evidence.
Every exploration creates proof obligations.

Usage:
    graph = ContextGraph(focus={start_node}, observer=observer)
    harness = ExplorationHarness(graph)

    # Navigate with safety
    result = await harness.navigate("tests")
    if result.success:
        # Continue exploration
        ...

    # Commit a claim based on exploration
    claim = Claim(statement="Auth middleware validates tokens correctly")
    commitment = await harness.commit(claim)
    if commitment.approved:
        # Claim is now committed at the given level
        ...

Teaching:
    gotcha: The harness is stateful—it tracks budget, loops, and evidence
            across navigation steps. Create a new harness for each exploration.

    gotcha: navigate() returns NavigationResult, not ContextGraph directly.
            Check result.success before accessing result.graph.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.file_operad.portal import PortalNode, PortalTree

from .budget import (
    BudgetExhausted,
    ExhaustionReason,
    NavigationBudget,
    standard_budget,
)
from .commitment import ASHCCommitment, CommitmentCheckResult
from .evidence import EvidenceCollector, EvidenceScope, EvidenceSummary, TrailAsEvidence
from .loops import LoopDetector, LoopResponse, LoopEvent
from .types import (
    Claim,
    CommitmentLevel,
    ContextGraph,
    ContextNode,
    Counterevidence,
    Evidence,
    EvidenceStrength,
    LoopStatus,
    NavigationResult,
    Observer,
    PortalExpansionResult,
    Trail,
)


# =============================================================================
# Exploration State
# =============================================================================


@dataclass
class ExplorationState:
    """Snapshot of exploration state for debugging/logging."""

    steps_taken: int
    nodes_visited: int
    current_depth: int
    evidence_count: int
    strong_evidence_count: int
    budget_remaining: dict[str, int | float]
    loop_warnings: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# =============================================================================
# Exploration Harness
# =============================================================================


@dataclass
class ExplorationHarness:
    """
    Wraps hypergraph navigation with safety and evidence.

    The harness is the main integration point for the exploration protocol.
    It combines:
    - ContextGraph: The navigable typed-hypergraph
    - NavigationBudget: Bounded exploration resources
    - LoopDetector: Prevent trivially bad loops
    - EvidenceCollector: Gather evidence during exploration
    - ASHCCommitment: Commit claims based on evidence

    Guarantees:
    - Termination: Navigation budget (steps, time)
    - Progress: Loop detection prevents spinning
    - Evidence: Every navigation creates evidence
    - Scope: Only relevant evidence accessible
    - Commitment: Claims require trail-based evidence
    """

    graph: ContextGraph
    budget: NavigationBudget = field(default_factory=standard_budget)
    loop_detector: LoopDetector = field(default_factory=LoopDetector)
    evidence_collector: EvidenceCollector = field(default_factory=EvidenceCollector)
    commitment: ASHCCommitment = field(default_factory=ASHCCommitment)
    trail_evidence: TrailAsEvidence = field(default_factory=TrailAsEvidence)

    # State
    _loop_warnings: int = 0
    _halted: bool = False
    _halt_reason: str | None = None

    async def navigate(self, edge: str) -> NavigationResult:
        """
        Navigate the hypergraph via an edge, with safety checks.

        Steps:
        1. Check budget
        2. Navigate graph
        3. Check for loops
        4. Record evidence
        5. Consume budget
        6. Update graph

        Returns:
            NavigationResult with success/failure and new graph state
        """
        # 0. Check if halted
        if self._halted:
            return NavigationResult(
                success=False,
                error_message=f"Exploration halted: {self._halt_reason}",
            )

        # 1. Check budget
        if not self.budget.can_navigate():
            reason = self.budget.exhaustion_reason()
            return NavigationResult.budget_exhausted_result(
                reason.value if reason else "unknown"
            )

        # 2. Navigate
        new_graph = await self.graph.navigate(edge)

        # 3. Check for loops on each new focus node
        for node in new_graph.focus:
            loop_status = self.loop_detector.check(node, edge)

            if loop_status != LoopStatus.OK:
                response = self.loop_detector.get_response(node, loop_status)

                if response == LoopResponse.CONTINUE:
                    self._loop_warnings += 1
                    # Continue but warn

                elif response == LoopResponse.BACKTRACK:
                    self._loop_warnings += 1
                    # Auto-backtrack
                    new_graph = new_graph.backtrack()
                    return NavigationResult(
                        success=True,
                        graph=new_graph,
                        loop_detected=loop_status,
                        error_message=f"Loop detected, auto-backtracked: {loop_status.name}",
                    )

                elif response == LoopResponse.HALT:
                    self._halted = True
                    self._halt_reason = f"Repeated {loop_status.name} loop"
                    return NavigationResult.loop_detected_result(loop_status)

        # 4. Record evidence
        await self.evidence_collector.record_navigation(
            source=self.graph.focus,
            edge=edge,
            destinations=new_graph.focus,
        )

        # 5. Consume budget
        depth = len(new_graph.trail.steps)
        for node in new_graph.focus:
            self.budget = self.budget.consume(node.path, depth)

        # 6. Update graph
        self.graph = new_graph

        return NavigationResult.ok(new_graph)

    async def expand_portal(
        self,
        portal_path: list[str],
        tree: "PortalTree",
    ) -> PortalExpansionResult:
        """
        Expand portal with budget, loop, and evidence safety.

        This is the harness-wrapped version of portal expansion that provides:
        1. Budget checking and consumption
        2. Loop detection for repeated expansions
        3. Evidence recording for expansion events
        4. Context event emission

        Args:
            portal_path: Path segments to the portal (e.g., ["tests", "covers"])
            tree: The PortalTree to expand

        Returns:
            PortalExpansionResult with success/failure and any evidence created

        Spec: spec/protocols/portal-token.md section 10 (Integration Points)
        """
        from protocols.file_operad.portal import PortalOpenSignal

        # 0. Check if halted
        if self._halted:
            return PortalExpansionResult.expansion_failed_result(
                "/".join(portal_path),
                f"Exploration halted: {self._halt_reason}",
            )

        # 1. Check budget
        if not self.budget.can_navigate():
            reason = self.budget.exhaustion_reason()
            return PortalExpansionResult.budget_exhausted_result(
                "/".join(portal_path),
                reason.value if reason else "unknown",
            )

        # 2. Check for loop (repeated expansion)
        portal_key = "/".join(portal_path)
        loop_status = self.loop_detector.check_portal(portal_key)

        if loop_status != LoopStatus.OK:
            response = self.loop_detector.get_portal_response(portal_key, loop_status)

            if response == LoopResponse.CONTINUE:
                self._loop_warnings += 1
                # Continue but warn - fall through to expansion
            elif response == LoopResponse.BACKTRACK:
                self._loop_warnings += 1
                # Skip this expansion
                return PortalExpansionResult.loop_detected_result(portal_key, loop_status)
            elif response == LoopResponse.HALT:
                self._halted = True
                self._halt_reason = f"Repeated portal expansion: {portal_key}"
                return PortalExpansionResult.loop_detected_result(portal_key, loop_status)

        # 3. Perform expansion
        success = tree.expand(portal_path)
        if not success:
            return PortalExpansionResult.expansion_failed_result(
                portal_key,
                "Portal expansion failed (path not found, depth limit, or file missing)",
            )

        # 4. Record evidence (weak - exploration fact)
        # Find the expanded node and get files opened
        node = tree._find_node(portal_path)
        files_opened: list[str] = []
        if node:
            # Get the token to find the file path
            token_key = portal_key
            if token_key in tree.tokens:
                token = tree.tokens[token_key]
                if token.link.file_path:
                    files_opened.append(str(token.link.file_path))

        evidence = self._record_portal_expansion(portal_key, node, files_opened)

        # 5. Consume budget
        depth = len(portal_path)
        self.budget = self.budget.consume(portal_key, depth)

        # 6. Emit context event to SynergyBus (fire-and-forget)
        if files_opened and node:
            signal = PortalOpenSignal(
                paths_opened=files_opened,
                edge_type=node.edge_type or "unknown",
                parent_path=tree.root.path,
                depth=depth,
            )
            context_event = signal.to_context_event()

            # Emit to synergy bus (non-blocking, fire-and-forget)
            # Uses local import to avoid circular dependency
            try:
                from protocols.synergy import get_synergy_bus
                from protocols.synergy.events import create_context_files_opened_event

                synergy_event = create_context_files_opened_event(
                    paths=context_event.paths,
                    reason=context_event.reason,
                    depth=context_event.depth,
                    parent_path=context_event.parent_path,
                    edge_type=context_event.edge_type,
                )
                asyncio.create_task(get_synergy_bus().emit(synergy_event))
            except ImportError:
                # Synergy bus not available (e.g., minimal test environment)
                pass

        return PortalExpansionResult.ok(portal_key, files_opened, evidence)

    def _record_portal_expansion(
        self,
        portal_key: str,
        node: "PortalNode | None",
        files_opened: list[str],
    ) -> Evidence:
        """
        Record portal expansion as weak evidence.

        Portal expansion is an exploration fact, not a conclusion.
        It creates weak evidence that can contribute to claims.
        """
        content = f"Expanded portal [{portal_key}]"
        if files_opened:
            content += f", opened: {', '.join(files_opened)}"

        # Use a synthetic node for the evidence
        synthetic_node = ContextNode(
            path=f"portal:{portal_key}",
            holon=portal_key.split("/")[-1] if portal_key else "unknown",
        )

        return self.evidence_collector.record_observation(
            node=synthetic_node,
            observation=content,
            strength=EvidenceStrength.WEAK,  # Exploration is weak evidence
        )

    async def commit_claim(
        self,
        claim: Claim,
        level: CommitmentLevel = CommitmentLevel.MODERATE,
        counterevidence: list[Counterevidence] | None = None,
    ) -> CommitmentCheckResult:
        """
        Attempt to commit a claim based on exploration evidence.

        Uses:
        - Trail from current graph
        - Evidence collected during exploration
        - Trail-as-evidence conversion
        """
        trail = self.graph.trail

        # Get evidence from collector
        collected_evidence = await self.evidence_collector.for_claim(claim.statement)

        # Convert trail to evidence
        trail_evidence = self.trail_evidence.to_evidence(trail, claim.statement)
        all_evidence = collected_evidence + [trail_evidence]

        # Check commitment
        return self.commitment.commit(
            claim=claim,
            level=level,
            trail=trail,
            evidence=all_evidence,
            counterevidence=counterevidence,
        )

    async def can_commit(
        self,
        claim: Claim,
        level: CommitmentLevel = CommitmentLevel.MODERATE,
    ) -> CommitmentCheckResult:
        """Check if a claim could be committed (without actually committing)."""
        trail = self.graph.trail
        collected_evidence = await self.evidence_collector.for_claim(claim.statement)
        trail_evidence = self.trail_evidence.to_evidence(trail, claim.statement)
        all_evidence = collected_evidence + [trail_evidence]

        return self.commitment.can_commit(
            claim=claim,
            trail=trail,
            evidence=all_evidence,
            target_level=level,
        )

    def record_observation(
        self,
        observation: str,
        strength: EvidenceStrength = EvidenceStrength.MODERATE,
    ) -> Evidence:
        """Record an observation at current focus as evidence."""
        # Use first focus node, or create synthetic one
        if self.graph.focus:
            node = next(iter(self.graph.focus))
        else:
            node = ContextNode(path="unknown", holon="unknown")

        return self.evidence_collector.record_observation(node, observation, strength)

    def get_state(self) -> ExplorationState:
        """Get current exploration state snapshot."""
        return ExplorationState(
            steps_taken=self.budget.steps_taken,
            nodes_visited=len(self.budget.nodes_visited),
            current_depth=self.budget.current_depth,
            evidence_count=self.evidence_collector.evidence_count,
            strong_evidence_count=self.evidence_collector.strong_count,
            budget_remaining=self.budget.remaining(),
            loop_warnings=self._loop_warnings,
        )

    def get_evidence_summary(self) -> EvidenceSummary:
        """Get summary of collected evidence."""
        # Synchronous access to evidence (collector has internal list)
        evidence = self.evidence_collector._evidence
        return EvidenceSummary.from_evidence(evidence)

    def get_evidence_scope(self) -> EvidenceScope:
        """Get evidence scope based on current trail."""
        scope = EvidenceScope(
            trail=self.graph.trail,
            observer=self.graph.observer,
        )
        # Add collected evidence to scope
        for e in self.evidence_collector._evidence:
            scope.add_evidence(e)
        return scope

    @property
    def trail(self) -> Trail:
        """Current exploration trail."""
        return self.graph.trail

    @property
    def focus(self) -> set[ContextNode]:
        """Current focus nodes."""
        return self.graph.focus

    @property
    def observer(self) -> Observer:
        """Current observer."""
        return self.graph.observer

    @property
    def is_halted(self) -> bool:
        """Whether exploration has been halted."""
        return self._halted

    @property
    def budget_exhausted(self) -> bool:
        """Whether budget is exhausted."""
        return not self.budget.can_navigate()

    def extend_budget(
        self,
        steps: int = 0,
        depth: int = 0,
        nodes: int = 0,
        time_ms: int = 0,
    ) -> None:
        """Extend the exploration budget."""
        self.budget = self.budget.extend(steps, depth, nodes, time_ms)

    def reset_loop_detector(self) -> None:
        """Reset loop detection (for intentional revisits)."""
        self.loop_detector.reset()
        self._loop_warnings = 0

    def unhalt(self) -> None:
        """Unhalt exploration (use with caution)."""
        self._halted = False
        self._halt_reason = None


# =============================================================================
# Factory Functions
# =============================================================================


def create_harness(
    start_node: ContextNode,
    observer: Observer | None = None,
    budget: NavigationBudget | None = None,
) -> ExplorationHarness:
    """Create an exploration harness starting at a node."""
    if observer is None:
        observer = Observer(id="default", archetype="developer")

    graph = ContextGraph(
        focus={start_node},
        trail=Trail(created_by=observer.id).add_step(start_node.path, None),
        observer=observer,
    )

    return ExplorationHarness(
        graph=graph,
        budget=budget or standard_budget(),
    )


def quick_harness(start_path: str) -> ExplorationHarness:
    """Create a quick exploration harness with minimal setup."""
    from .budget import quick_budget

    node = ContextNode(path=start_path, holon=start_path.split(".")[-1])
    return create_harness(node, budget=quick_budget())


def thorough_harness(start_path: str) -> ExplorationHarness:
    """Create a thorough exploration harness with generous budget."""
    from .budget import thorough_budget

    node = ContextNode(path=start_path, holon=start_path.split(".")[-1])
    return create_harness(node, budget=thorough_budget())


__all__ = [
    "ExplorationHarness",
    "ExplorationState",
    # Factories
    "create_harness",
    "quick_harness",
    "thorough_harness",
]
