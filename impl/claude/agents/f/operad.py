"""
Flow Operad: Composition grammar for flow operations.

The FLOW_OPERAD defines valid composition patterns for flow operations,
with laws ensuring coherent behavior.

See: spec/f-gents/README.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class Operation:
    """A single operad operation."""

    name: str
    arity: int
    signature: str
    compose: Callable[..., Any] | None = None
    description: str = ""


@dataclass(frozen=True)
class OpLaw:
    """An operad law (equation that must hold)."""

    name: str
    equation: str
    description: str = ""


@dataclass
class Operad:
    """
    Operad structure for flow operations.

    An operad is an algebraic structure for describing composition patterns.
    Operations have arities, and composition must satisfy laws.
    """

    name: str
    operations: dict[str, Operation] = field(default_factory=dict)
    laws: list[OpLaw] = field(default_factory=list)

    def get_operation(self, name: str) -> Operation:
        """Get an operation by name."""
        if name not in self.operations:
            msg = f"Unknown operation: {name}"
            raise KeyError(msg)
        return self.operations[name]

    def validate_composition(self, outer: str, inners: list[str]) -> bool:
        """
        Validate that a composition is well-formed.

        The outer operation must have arity equal to len(inners).
        """
        op = self.get_operation(outer)
        if op.arity != len(inners):
            return False
        # All inner operations must exist
        return all(inner in self.operations for inner in inners)


# ============================================================================
# Compose Functions (stubs - implementations come with modalities)
# ============================================================================


def start_compose(*args: Any) -> Any:
    """Compose start operations."""
    return args


def stop_compose(*args: Any) -> Any:
    """Compose stop operations."""
    return args


def perturb_compose(*args: Any) -> Any:
    """Compose perturb operations."""
    return args


def turn_compose(*args: Any) -> Any:
    """Compose turn operations."""
    return args


def summarize_compose(*args: Any) -> Any:
    """Compose summarize operations."""
    return args


def inject_compose(*args: Any) -> Any:
    """Compose inject_context operations."""
    return args


def branch_compose(*args: Any) -> Any:
    """Compose branch operations."""
    return args


def merge_compose(*args: Any) -> Any:
    """Compose merge operations."""
    return args


def prune_compose(*args: Any) -> Any:
    """Compose prune operations."""
    return args


def evaluate_compose(*args: Any) -> Any:
    """Compose evaluate operations."""
    return args


def post_compose(*args: Any) -> Any:
    """Compose post operations."""
    return args


def read_compose(*args: Any) -> Any:
    """Compose read operations."""
    return args


def vote_compose(*args: Any) -> Any:
    """Compose vote operations."""
    return args


def moderate_compose(*args: Any) -> Any:
    """Compose moderate operations."""
    return args


# ============================================================================
# FLOW_OPERAD Definition
# ============================================================================

FLOW_OPERAD = Operad(
    name="FLOW_OPERAD",
    operations={
        # === Universal Operations ===
        "start": Operation(
            name="start",
            arity=1,
            signature="Agent[A,B] -> Flow[A] -> Flow[B]",
            compose=start_compose,
            description="Start a flow from an agent and input source.",
        ),
        "stop": Operation(
            name="stop",
            arity=0,
            signature="Flow[_] -> ()",
            compose=stop_compose,
            description="Stop a running flow.",
        ),
        "perturb": Operation(
            name="perturb",
            arity=1,
            signature="(Flow[A], A) -> B",
            compose=perturb_compose,
            description="Inject input into a streaming flow.",
        ),
        # === Chat Operations ===
        "turn": Operation(
            name="turn",
            arity=1,
            signature="Message -> Response",
            compose=turn_compose,
            description="Execute one conversation turn.",
        ),
        "summarize": Operation(
            name="summarize",
            arity=1,
            signature="Context -> CompressedContext",
            compose=summarize_compose,
            description="Compress context window.",
        ),
        "inject_context": Operation(
            name="inject_context",
            arity=1,
            signature="Context -> Flow[_]",
            compose=inject_compose,
            description="Inject context into flow.",
        ),
        # === Research Operations ===
        "branch": Operation(
            name="branch",
            arity=1,
            signature="Hypothesis -> [Hypothesis]",
            compose=branch_compose,
            description="Generate alternative hypotheses.",
        ),
        "merge": Operation(
            name="merge",
            arity=2,
            signature="(Hypothesis, Hypothesis) -> Synthesis",
            compose=merge_compose,
            description="Combine hypotheses into synthesis.",
        ),
        "prune": Operation(
            name="prune",
            arity=1,
            signature="[Hypothesis] -> [Hypothesis]",
            compose=prune_compose,
            description="Eliminate low-promise hypotheses.",
        ),
        "evaluate": Operation(
            name="evaluate",
            arity=1,
            signature="Hypothesis -> Score",
            compose=evaluate_compose,
            description="Score a hypothesis.",
        ),
        # === Collaboration Operations ===
        "post": Operation(
            name="post",
            arity=1,
            signature="Contribution -> Blackboard",
            compose=post_compose,
            description="Post contribution to blackboard.",
        ),
        "read": Operation(
            name="read",
            arity=1,
            signature="Query -> [Contribution]",
            compose=read_compose,
            description="Read contributions from blackboard.",
        ),
        "vote": Operation(
            name="vote",
            arity=2,
            signature="(Proposal, Agents) -> Decision",
            compose=vote_compose,
            description="Vote on a proposal.",
        ),
        "moderate": Operation(
            name="moderate",
            arity=1,
            signature="[Contribution] -> Resolution",
            compose=moderate_compose,
            description="Moderate conflict.",
        ),
    },
    laws=[
        # === Universal Laws ===
        OpLaw(
            name="start_identity",
            equation="start(Id) = Id_Flow",
            description="Starting with identity agent yields identity flow.",
        ),
        OpLaw(
            name="start_composition",
            equation="start(f >> g) = start(f) >> start(g)",
            description="Start distributes over composition.",
        ),
        OpLaw(
            name="perturbation_integrity",
            equation="perturb(flowing, x) = inject_priority(x)",
            description="Perturbation injects with priority, never bypasses.",
        ),
        # === Research Laws ===
        OpLaw(
            name="branch_merge",
            equation="merge(branch(h)) >= essence(h)",
            description="Merging branches preserves semantic essence.",
        ),
        OpLaw(
            name="prune_idempotent",
            equation="prune(prune(hs)) = prune(hs)",
            description="Pruning is idempotent.",
        ),
        # === Collaboration Laws ===
        OpLaw(
            name="post_read",
            equation="read(all, post(c, board)) = [c] ++ read(all, board)",
            description="Posted contributions are immediately readable.",
        ),
        OpLaw(
            name="consensus_threshold",
            equation="vote(p, agents) = decide if votes >= threshold",
            description="Consensus requires threshold agreement.",
        ),
    ],
)


# Modality-specific operads (subsets of FLOW_OPERAD)
CHAT_OPERAD = Operad(
    name="CHAT_OPERAD",
    operations={
        k: v
        for k, v in FLOW_OPERAD.operations.items()
        if k in {"start", "stop", "perturb", "turn", "summarize", "inject_context"}
    },
    laws=[
        law for law in FLOW_OPERAD.laws if "start" in law.name or "perturb" in law.name
    ],
)

RESEARCH_OPERAD = Operad(
    name="RESEARCH_OPERAD",
    operations={
        k: v
        for k, v in FLOW_OPERAD.operations.items()
        if k in {"start", "stop", "perturb", "branch", "merge", "prune", "evaluate"}
    },
    laws=[
        law
        for law in FLOW_OPERAD.laws
        if any(x in law.name for x in ["start", "branch", "prune"])
    ],
)

COLLABORATION_OPERAD = Operad(
    name="COLLABORATION_OPERAD",
    operations={
        k: v
        for k, v in FLOW_OPERAD.operations.items()
        if k in {"start", "stop", "perturb", "post", "read", "vote", "moderate"}
    },
    laws=[
        law
        for law in FLOW_OPERAD.laws
        if any(x in law.name for x in ["start", "post", "consensus"])
    ],
)


def get_operad(modality: str) -> Operad:
    """Get the operad for a modality."""
    operads = {
        "chat": CHAT_OPERAD,
        "research": RESEARCH_OPERAD,
        "collaboration": COLLABORATION_OPERAD,
        "flow": FLOW_OPERAD,
    }
    if modality not in operads:
        msg = f"Unknown modality: {modality}"
        raise ValueError(msg)
    return operads[modality]


__all__ = [
    "Operation",
    "OpLaw",
    "Operad",
    "FLOW_OPERAD",
    "CHAT_OPERAD",
    "RESEARCH_OPERAD",
    "COLLABORATION_OPERAD",
    "get_operad",
]
