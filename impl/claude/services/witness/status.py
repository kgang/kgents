"""
Spec Status: Compute Witness Status of Specifications.

A specification can have one of five statuses:
- UNWITNESSED: No evidence at all
- IN_PROGRESS: Some evidence, but not complete
- WITNESSED: Full evidence chain (the goal)
- CONTESTED: Has refutation evidence
- SUPERSEDED: Replaced by a newer spec

WITNESSED Requirements:
- At least one L-1 TraceWitness OR L1 test artifact
- At least one L0 mark or decision
- At least one `implements` hyperedge to implementation
- (Future: At least one L-2 PromptAncestor for AI-generated code)

Philosophy:
    "The proof IS the decision. The mark IS the witness."

    A spec is not WITNESSED just because tests pass. It requires
    human attention (marks) AND runtime/test evidence AND an
    actual implementation. This prevents orphaned specs and
    undocumented implementations.

See: plans/witness-assurance-protocol.md
See: spec/protocols/witness-supersession.md

Teaching:
    gotcha: compute_status requires hypergraph (Kent's decision: fail-fast).
            This ensures callers always provide proper context for checking
            the `implements` edge. Use `compute_status_from_evidence_only`
            if you only have evidence without hypergraph access.
            (Evidence: test_evidence.py::test_compute_status_requires_hypergraph)

    gotcha: compute_status returns (status, reason) tuple. The reason string
            explains WHY that status was computed - this embodies Article III
            (Supersession Rights) where decisions require justification.
            (Evidence: test_evidence.py::test_status_includes_reason)
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Protocol

from .evidence import Evidence, EvidenceLevel

if TYPE_CHECKING:
    pass


# =============================================================================
# Hypergraph Protocol (for DI)
# =============================================================================


class ContextGraphProtocol(Protocol):
    """
    Protocol for hypergraph context access.

    This enables DI without importing the full hypergraph machinery.
    Implementations must provide `follow_edge` for querying edges.
    """

    async def follow_edge(self, node_path: str, edge_type: str) -> list[str]:
        """
        Follow an edge from a node and return connected paths.

        Args:
            node_path: The source node path (e.g., "world.spec.witness")
            edge_type: The edge type to follow (e.g., "implemented_by")

        Returns:
            List of connected node paths
        """
        ...


# =============================================================================
# SpecStatus Enum
# =============================================================================


class SpecStatus(Enum):
    """
    Witness status of a specification.

    States form a directed graph:
        UNWITNESSED → IN_PROGRESS → WITNESSED
                   ↘     ↓          ↓
                    CONTESTED ← ────┘
                         ↓
                    SUPERSEDED

    Properties:
    - UNWITNESSED: No evidence (starting state)
    - IN_PROGRESS: Some evidence, incomplete
    - WITNESSED: Full evidence chain (goal state)
    - CONTESTED: Has refutation evidence
    - SUPERSEDED: Replaced by newer spec (terminal)
    """

    UNWITNESSED = "unwitnessed"
    IN_PROGRESS = "in_progress"
    WITNESSED = "witnessed"
    CONTESTED = "contested"
    SUPERSEDED = "superseded"

    @property
    def emoji(self) -> str:
        """Emoji for display."""
        return {
            SpecStatus.UNWITNESSED: "🔲",
            SpecStatus.IN_PROGRESS: "🔶",
            SpecStatus.WITNESSED: "✅",
            SpecStatus.CONTESTED: "⚠️",
            SpecStatus.SUPERSEDED: "📦",
        }[self]

    @property
    def description(self) -> str:
        """Human-readable description."""
        return {
            SpecStatus.UNWITNESSED: "No evidence collected",
            SpecStatus.IN_PROGRESS: "Some evidence, incomplete",
            SpecStatus.WITNESSED: "Fully witnessed with evidence",
            SpecStatus.CONTESTED: "Has conflicting evidence",
            SpecStatus.SUPERSEDED: "Replaced by newer spec",
        }[self]

    @property
    def is_terminal(self) -> bool:
        """True if this is a terminal state."""
        return self == SpecStatus.SUPERSEDED

    @property
    def is_healthy(self) -> bool:
        """True if this is a healthy state (witnessed or in progress)."""
        return self in (SpecStatus.WITNESSED, SpecStatus.IN_PROGRESS)


# =============================================================================
# Status Computation
# =============================================================================


class WitnessedCriteria:
    """
    Encapsulates the criteria for WITNESSED status.

    WITNESSED requires ALL of:
    1. has_trace_or_test: At least one L-1 TraceWitness OR L1 Test
    2. has_mark: At least one L0 Mark or decision
    3. has_implementation: At least one `implements` hyperedge
    4. no_refutation: No evidence with relation="refutes"

    Future (Phase 3):
    5. has_prompt_lineage: For AI-generated code, L-2 PromptAncestor required
    """

    def __init__(
        self,
        has_trace_or_test: bool = False,
        has_mark: bool = False,
        has_implementation: bool = False,
        has_refutation: bool = False,
        has_prompt_lineage: bool = True,  # Default True until Phase 3
    ) -> None:
        self.has_trace_or_test = has_trace_or_test
        self.has_mark = has_mark
        self.has_implementation = has_implementation
        self.has_refutation = has_refutation
        self.has_prompt_lineage = has_prompt_lineage

    @property
    def is_witnessed(self) -> bool:
        """True if all WITNESSED criteria are met."""
        return (
            self.has_trace_or_test
            and self.has_mark
            and self.has_implementation
            and not self.has_refutation
            and self.has_prompt_lineage
        )

    @property
    def is_contested(self) -> bool:
        """True if there is refutation evidence."""
        return self.has_refutation

    @property
    def is_in_progress(self) -> bool:
        """True if some but not all criteria met."""
        return (self.has_mark or self.has_implementation) and not self.is_witnessed

    def missing_criteria(self) -> list[str]:
        """Return list of missing criteria for WITNESSED status."""
        missing = []
        if not self.has_trace_or_test:
            missing.append("L-1 TraceWitness or L1 Test")
        if not self.has_mark:
            missing.append("L0 Mark")
        if not self.has_implementation:
            missing.append("`implements` hyperedge")
        if not self.has_prompt_lineage:
            missing.append("L-2 PromptAncestor (for AI-generated code)")
        return missing

    def to_reason(self) -> str:
        """Generate reason string explaining the status."""
        if self.is_contested:
            return "Has refutation evidence"
        if self.is_witnessed:
            criteria_met = []
            if self.has_trace_or_test:
                criteria_met.append("trace/test")
            if self.has_mark:
                criteria_met.append("mark")
            if self.has_implementation:
                criteria_met.append("implementation")
            return f"All criteria met: {', '.join(criteria_met)}"
        if self.is_in_progress:
            missing = self.missing_criteria()
            return f"In progress; missing: {', '.join(missing)}"
        return "No evidence"


async def compute_status(
    spec_path: str,
    evidence: list[Evidence],
    hypergraph: ContextGraphProtocol,
) -> tuple[SpecStatus, str]:
    """
    Compute witness status of a spec.

    WITNESSED requires:
    - At least one L-1 TraceWitness OR L1 test artifact
    - At least one L0 mark or decision
    - At least one `implements` hyperedge to implementation
    - (Future: At least one L-2 PromptAncestor for AI-generated code)

    Args:
        spec_path: Path to the spec (e.g., "spec/protocols/witness.md")
        evidence: List of Evidence objects for this spec
        hypergraph: ContextGraph for following edges (REQUIRED - fail fast)

    Returns:
        (status, reason) tuple where reason explains the decision

    Raises:
        TypeError: If hypergraph is None

    Example:
        >>> status, reason = await compute_status(
        ...     "spec/protocols/witness.md",
        ...     [Evidence(level=EvidenceLevel.MARK, ...)],
        ...     hypergraph,
        ... )
        >>> print(f"{status.emoji} {reason}")
        🔶 In progress; missing: L-1 TraceWitness or L1 Test, `implements` hyperedge
    """
    if hypergraph is None:
        raise TypeError("hypergraph is required for compute_status (fail-fast)")

    # Classify evidence
    has_trace_or_test = any(e.level in (EvidenceLevel.TRACE, EvidenceLevel.TEST) for e in evidence)
    has_mark = any(e.level == EvidenceLevel.MARK for e in evidence)
    has_prompt_lineage = any(e.level == EvidenceLevel.PROMPT for e in evidence)
    has_refutation = any(e.metadata.get("relation") == "refutes" for e in evidence)

    # Check hypergraph for implementation edge
    # Convert spec path to AGENTESE-style path for node lookup
    agentese_path = _spec_path_to_agentese(spec_path)
    try:
        implementations = await hypergraph.follow_edge(agentese_path, "implemented_by")
        has_implementation = len(implementations) > 0
    except Exception:
        # If hypergraph query fails, assume no implementation
        has_implementation = False

    # Build criteria object
    criteria = WitnessedCriteria(
        has_trace_or_test=has_trace_or_test,
        has_mark=has_mark,
        has_implementation=has_implementation,
        has_refutation=has_refutation,
        has_prompt_lineage=True,  # Default True until Phase 3
    )

    # Determine status
    if criteria.is_contested:
        return SpecStatus.CONTESTED, criteria.to_reason()
    if criteria.is_witnessed:
        return SpecStatus.WITNESSED, criteria.to_reason()
    if criteria.is_in_progress:
        return SpecStatus.IN_PROGRESS, criteria.to_reason()
    return SpecStatus.UNWITNESSED, criteria.to_reason()


def compute_status_from_evidence_only(
    evidence: list[Evidence],
) -> tuple[SpecStatus, str]:
    """
    Compute status from evidence only (no hypergraph access).

    This is a simpler version that cannot check the `implements` edge.
    It will never return WITNESSED (only IN_PROGRESS at best).

    Use this when you only have evidence and don't need full WITNESSED
    status computation.

    Args:
        evidence: List of Evidence objects

    Returns:
        (status, reason) tuple
    """
    has_trace_or_test = any(e.level in (EvidenceLevel.TRACE, EvidenceLevel.TEST) for e in evidence)
    has_mark = any(e.level == EvidenceLevel.MARK for e in evidence)
    has_refutation = any(e.metadata.get("relation") == "refutes" for e in evidence)

    if has_refutation:
        return SpecStatus.CONTESTED, "Has refutation evidence"

    if has_trace_or_test and has_mark:
        # Best we can say without hypergraph is IN_PROGRESS
        return SpecStatus.IN_PROGRESS, "Has trace/test and mark; need hypergraph for WITNESSED"

    if has_mark or has_trace_or_test:
        missing = []
        if not has_trace_or_test:
            missing.append("L-1 TraceWitness or L1 Test")
        if not has_mark:
            missing.append("L0 Mark")
        return SpecStatus.IN_PROGRESS, f"In progress; missing: {', '.join(missing)}"

    return SpecStatus.UNWITNESSED, "No evidence"


def _spec_path_to_agentese(spec_path: str) -> str:
    """
    Convert a spec file path to an AGENTESE node path.

    Examples:
        "spec/protocols/witness.md" → "world.spec.protocols.witness"
        "spec/agents/d-gent.md" → "world.spec.agents.d-gent"
    """
    # Remove .md extension
    path = spec_path.replace(".md", "")

    # Replace / with .
    path = path.replace("/", ".")

    # Ensure world. prefix
    if not path.startswith("world."):
        path = f"world.{path}"

    return path


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Protocol
    "ContextGraphProtocol",
    # Enum
    "SpecStatus",
    # Helper class
    "WitnessedCriteria",
    # Functions
    "compute_status",
    "compute_status_from_evidence_only",
]
