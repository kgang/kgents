"""
Pass Core Types

The foundational types for the Pass Operad.

Design decisions:
- PassProtocol is a Protocol, not an ABC (structural typing)
- ProofCarryingIR is frozen (immutable IR with proofs)
- VerificationGraph tracks proof dependencies
- LawResult aggregates law verification outcomes
- Compatible with existing TraceWitnessResult from primitives
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from .composition import ComposedPass


# =============================================================================
# Type Variables
# =============================================================================

IR = TypeVar("IR")
# Use invariant type variables for the Protocol
# (contravariant/covariant cause issues with structural typing)
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


# =============================================================================
# Verification Graph
# =============================================================================


@dataclass(frozen=True)
class VerificationNode:
    """A node in the verification graph."""

    pass_name: str
    witness_id: str
    timestamp: datetime
    status: str = "success"


@dataclass(frozen=True)
class VerificationEdge:
    """An edge in the verification graph (data dependency)."""

    source: str  # witness_id
    target: str  # witness_id
    relation: str = "produces"


@dataclass(frozen=True)
class VerificationGraph:
    """
    Graph of proof dependencies.

    Tracks how witnesses connect and enables proof inspection.
    """

    nodes: tuple[VerificationNode, ...] = ()
    edges: tuple[VerificationEdge, ...] = ()

    @classmethod
    def empty(cls) -> "VerificationGraph":
        """Create an empty verification graph."""
        return cls(nodes=(), edges=())

    @classmethod
    def from_witness(
        cls,
        pass_name: str,
        witness_id: str,
        timestamp: datetime | None = None,
    ) -> "VerificationGraph":
        """Create a graph with a single node from a witness."""
        node = VerificationNode(
            pass_name=pass_name,
            witness_id=witness_id,
            timestamp=timestamp or datetime.now(),
        )
        return cls(nodes=(node,), edges=())

    def add_node(self, node: VerificationNode) -> "VerificationGraph":
        """Add a node to the graph."""
        return VerificationGraph(
            nodes=self.nodes + (node,),
            edges=self.edges,
        )

    def add_edge(self, edge: VerificationEdge) -> "VerificationGraph":
        """Add an edge to the graph."""
        return VerificationGraph(
            nodes=self.nodes,
            edges=self.edges + (edge,),
        )


def merge_graphs(g1: VerificationGraph, g2: VerificationGraph) -> VerificationGraph:
    """
    Merge two verification graphs.

    Preserves all nodes and edges from both.
    """
    # Combine nodes (dedupe by witness_id)
    seen_ids: set[str] = set()
    merged_nodes: list[VerificationNode] = []
    for node in g1.nodes + g2.nodes:
        if node.witness_id not in seen_ids:
            merged_nodes.append(node)
            seen_ids.add(node.witness_id)

    # Combine edges (dedupe by source+target)
    seen_edges: set[tuple[str, str]] = set()
    merged_edges: list[VerificationEdge] = []
    for edge in g1.edges + g2.edges:
        key = (edge.source, edge.target)
        if key not in seen_edges:
            merged_edges.append(edge)
            seen_edges.add(key)

    return VerificationGraph(
        nodes=tuple(merged_nodes),
        edges=tuple(merged_edges),
    )


# =============================================================================
# Proof-Carrying IR
# =============================================================================


@dataclass(frozen=True)
class ProofCarryingIR:
    """
    Intermediate Representation with attached proofs.

    Every pass produces ProofCarryingIR, which includes:
    - The IR itself (the data)
    - Witnesses (proofs of correct execution)
    - Verification graph (proof dependencies)

    This is the fundamental output type of all passes.
    """

    ir: Any
    witnesses: tuple[Any, ...]  # TraceWitnessResult from primitives
    verification_graph: VerificationGraph

    @classmethod
    def from_output(
        cls,
        output: Any,
        witness: Any,
        pass_name: str,
    ) -> "ProofCarryingIR":
        """Create ProofCarryingIR from a pass output and witness."""
        graph = VerificationGraph.from_witness(
            pass_name=pass_name,
            witness_id=getattr(witness, "witness_id", str(id(witness))),
        )
        return cls(
            ir=output,
            witnesses=(witness,),
            verification_graph=graph,
        )

    def chain(self, other: "ProofCarryingIR") -> "ProofCarryingIR":
        """
        Chain two ProofCarryingIRs together.

        Used when composing passes: (f >> g)(x) chains f's result with g's.
        """
        return ProofCarryingIR(
            ir=other.ir,
            witnesses=self.witnesses + other.witnesses,
            verification_graph=merge_graphs(
                self.verification_graph,
                other.verification_graph,
            ),
        )


# =============================================================================
# Pass Protocol
# =============================================================================


@runtime_checkable
class PassProtocol(Protocol):
    """
    Protocol for compiler passes.

    A pass is a morphism in the compiler category:
    - Input type (described by input_type string)
    - Output type (described by output_type string)
    - Composition via >>
    - Always produces witnesses

    This is structural typing: any class with these methods is a pass.
    """

    @property
    def name(self) -> str:
        """The pass name (for identification)."""
        ...

    @property
    def input_type(self) -> str:
        """String representation of input type."""
        ...

    @property
    def output_type(self) -> str:
        """String representation of output type."""
        ...

    async def invoke(self, input: Any) -> ProofCarryingIR:
        """
        Execute the pass.

        Args:
            input: The input IR (or None for nullary passes like Ground)

        Returns:
            ProofCarryingIR with output and witnesses
        """
        ...

    def __rshift__(self, other: Any) -> Any:
        """
        Compose with another pass.

        (f >> g)(x) = g(f(x).ir)

        Returns a new pass that chains the two.
        """
        ...


# =============================================================================
# Law Types
# =============================================================================


class LawStatus(str, Enum):
    """Status of a law verification."""

    HOLDS = "holds"
    VIOLATED = "violated"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class LawResult:
    """
    Result of verifying a single composition law.

    Laws are the equations that must hold in the operad.
    """

    law: str
    status: LawStatus
    evidence: str = ""
    left_result: Any = None
    right_result: Any = None

    @property
    def holds(self) -> bool:
        """True if the law holds."""
        return self.status == LawStatus.HOLDS

    @classmethod
    def passed(cls, law: str, evidence: str = "") -> "LawResult":
        """Create a passing result."""
        return cls(law=law, status=LawStatus.HOLDS, evidence=evidence or "verified")

    @classmethod
    def failed(
        cls,
        law: str,
        evidence: str,
        left: Any = None,
        right: Any = None,
    ) -> "LawResult":
        """Create a failing result."""
        return cls(
            law=law,
            status=LawStatus.VIOLATED,
            evidence=evidence,
            left_result=left,
            right_result=right,
        )

    @classmethod
    def error(cls, law: str, message: str) -> "LawResult":
        """Create an error result."""
        return cls(law=law, status=LawStatus.ERROR, evidence=message)

    @classmethod
    def aggregate(cls, results: list["LawResult"]) -> "LawResult":
        """
        Aggregate multiple law results.

        Returns HOLDS only if all hold.
        """
        if not results:
            return cls(law="aggregate", status=LawStatus.SKIPPED, evidence="no laws")

        # Check if any failed
        failed = [r for r in results if not r.holds]
        if failed:
            laws = ", ".join(r.law for r in failed)
            return cls(
                law="aggregate",
                status=LawStatus.VIOLATED,
                evidence=f"Failed laws: {laws}",
            )

        return cls(
            law="aggregate",
            status=LawStatus.HOLDS,
            evidence=f"All {len(results)} laws verified",
        )


# =============================================================================
# Composition Law Protocol
# =============================================================================


class CompositionLaw(ABC):
    """
    Abstract base for composition laws.

    Laws are equations that must hold for valid compositions.
    The Pass Operad verifies these laws at composition time.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The law name."""
        ...

    @property
    @abstractmethod
    def equation(self) -> str:
        """The equation (for display)."""
        ...

    @abstractmethod
    async def verify(self, *passes: PassProtocol) -> LawResult:
        """
        Verify the law holds for given passes.

        Args:
            passes: Passes to verify the law against

        Returns:
            LawResult indicating whether the law holds
        """
        ...


__all__ = [
    # Verification graph
    "VerificationNode",
    "VerificationEdge",
    "VerificationGraph",
    "merge_graphs",
    # Proof-carrying IR
    "ProofCarryingIR",
    # Pass protocol
    "PassProtocol",
    # Law types
    "LawStatus",
    "LawResult",
    "CompositionLaw",
]
