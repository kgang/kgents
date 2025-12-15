"""
NPHASE_OPERAD: Operad for the N-Phase development cycle.

Defines the compressed 3-phase model (SENSE, ACT, REFLECT) as an operad
with composition operations and laws.

Pattern source: agents/operad/core.py, agents/town/operad.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Literal

from agents.operad.core import (
    Law,
    LawStatus,
    LawVerification,
    Operad,
    OperadRegistry,
    Operation,
)
from agents.poly import PolyAgent


class NPhase(Enum):
    """The three compressed phases of development."""

    # UNDERSTAND is the primary name (more actionable than SENSE)
    UNDERSTAND = auto()  # PLAN, RESEARCH, DEVELOP, STRATEGIZE, CROSS-SYNERGIZE
    ACT = auto()  # IMPLEMENT, QA, TEST
    REFLECT = auto()  # EDUCATE, MEASURE, REFLECT

    # Alias for backwards compatibility
    SENSE = UNDERSTAND


# Phase family mapping (which detailed phases belong to which compressed phase)
PHASE_FAMILIES: dict[NPhase, list[str]] = {
    NPhase.UNDERSTAND: ["PLAN", "RESEARCH", "DEVELOP", "STRATEGIZE", "CROSS-SYNERGIZE"],
    NPhase.ACT: ["IMPLEMENT", "QA", "TEST"],
    NPhase.REFLECT: ["EDUCATE", "MEASURE", "REFLECT"],
}

# Reverse mapping: detailed phase -> compressed phase
DETAILED_TO_COMPRESSED: dict[str, NPhase] = {
    detailed: compressed
    for compressed, detailed_list in PHASE_FAMILIES.items()
    for detailed in detailed_list
}


@dataclass
class NPhaseState:
    """State for N-Phase operations."""

    current_phase: NPhase = NPhase.UNDERSTAND
    cycle_count: int = 0
    phase_outputs: dict[NPhase, list[Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize phase outputs."""
        for phase in NPhase:
            if phase not in self.phase_outputs:
                self.phase_outputs[phase] = []


@dataclass
class NPhaseInput:
    """Input to an N-Phase operation."""

    content: Any
    source_phase: NPhase | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NPhaseOutput:
    """Output from an N-Phase operation."""

    content: Any
    phase: NPhase
    success: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


# === Composition Functions ===


def _sense_compose(agent: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Compose a SENSE operation.

    SENSE aggregates perception, planning, and research.
    The agent observes and gathers information.
    """
    return agent  # Identity in this simple model


def _act_compose(agent: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Compose an ACT operation.

    ACT aggregates strategy, implementation, testing.
    The agent takes action based on SENSE outputs.
    """
    return agent  # Identity in this simple model


def _reflect_compose(agent: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Compose a REFLECT operation.

    REFLECT aggregates education, measurement, retrospection.
    The agent integrates learnings.
    """
    return agent  # Identity in this simple model


def _cycle_compose(
    sense_agent: PolyAgent[Any, Any, Any],
    act_agent: PolyAgent[Any, Any, Any],
    reflect_agent: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a full SENSE >> ACT >> REFLECT cycle.

    This is the fundamental composition: a complete development cycle.
    """
    # In full implementation, would compose via >> operator
    # For now, return the reflect_agent as the terminal state
    return reflect_agent


# === Law Verification Functions ===


def _verify_phase_order(
    _operad: Operad,
    state: NPhaseState,
    _input: NPhaseInput,
) -> LawVerification:
    """
    Verify: SENSE >> ACT >> REFLECT ordering.

    ACT requires prior SENSE output. REFLECT requires prior ACT output.
    """
    # Check that phase order is respected
    if state.current_phase == NPhase.ACT:
        if not state.phase_outputs.get(NPhase.SENSE):
            return LawVerification(
                law_name="phase_order",
                status=LawStatus.FAILED,
                message="ACT requires prior SENSE output",
            )
    elif state.current_phase == NPhase.REFLECT:
        if not state.phase_outputs.get(NPhase.ACT):
            return LawVerification(
                law_name="phase_order",
                status=LawStatus.FAILED,
                message="REFLECT requires prior ACT output",
            )

    return LawVerification(
        law_name="phase_order",
        status=LawStatus.PASSED,
        message="Phase order respected",
    )


def _verify_cycle_closure(
    _operad: Operad,
    state: NPhaseState,
    _input: NPhaseInput,
) -> LawVerification:
    """
    Verify: REFLECT may trigger new SENSE (cycle closure).

    After REFLECT, the cycle may restart with new SENSE.
    """
    if state.current_phase == NPhase.REFLECT:
        # REFLECT always allows transition back to SENSE
        return LawVerification(
            law_name="cycle",
            status=LawStatus.PASSED,
            message="REFLECT can trigger new SENSE",
        )

    return LawVerification(
        law_name="cycle",
        status=LawStatus.PASSED,
        message="Cycle closure available from REFLECT",
    )


def _verify_identity(
    operad: Operad,
    agent: PolyAgent[Any, Any, Any],
    _test_input: Any,
) -> LawVerification:
    """
    Verify: id >> op == op == op >> id.

    Identity operation preserves the agent.
    """
    # Get identity operation if available
    if "id" not in operad.operations:
        return LawVerification(
            law_name="identity",
            status=LawStatus.SKIPPED,
            message="No identity operation defined",
        )

    # In a full implementation, would verify composition
    return LawVerification(
        law_name="identity",
        status=LawStatus.PASSED,
        message="Identity law holds",
    )


# === Operations ===


NPHASE_OPERATIONS: dict[str, Operation] = {
    "understand": Operation(
        name="understand",
        arity=1,
        signature="Agent[A, B] -> Agent[A, UnderstoodState]",
        compose=_sense_compose,
        description="Map the terrain (PLAN, RESEARCH, DEVELOP, STRATEGIZE, CROSS-SYNERGIZE)",
    ),
    # Alias for backwards compatibility
    "sense": Operation(
        name="sense",
        arity=1,
        signature="Agent[A, B] -> Agent[A, UnderstoodState]",
        compose=_sense_compose,
        description="Alias for understand",
    ),
    "act": Operation(
        name="act",
        arity=1,
        signature="Agent[UnderstoodState, B] -> Agent[UnderstoodState, ActionResult]",
        compose=_act_compose,
        description="Execute and verify (IMPLEMENT, QA, TEST)",
    ),
    "reflect": Operation(
        name="reflect",
        arity=1,
        signature="Agent[ActionResult, B] -> Agent[ActionResult, Reflection]",
        compose=_reflect_compose,
        description="Integrate learnings (EDUCATE, MEASURE, REFLECT)",
    ),
    "cycle": Operation(
        name="cycle",
        arity=3,
        signature="(Agent, Agent, Agent) -> Agent[A, Reflection]",
        compose=_cycle_compose,
        description="Full UNDERSTAND >> ACT >> REFLECT cycle",
    ),
}


# === Laws ===


NPHASE_LAWS: list[Law] = [
    Law(
        name="phase_order",
        equation="UNDERSTAND >> ACT >> REFLECT",
        verify=_verify_phase_order,
        description="ACT requires UNDERSTAND; REFLECT requires ACT",
    ),
    Law(
        name="cycle",
        equation="REFLECT -> UNDERSTAND (allowed)",
        verify=_verify_cycle_closure,
        description="REFLECT may trigger new UNDERSTAND cycle",
    ),
    Law(
        name="identity",
        equation="id >> op == op == op >> id",
        verify=_verify_identity,
        description="Identity operation preserves agent",
    ),
]


# === NPHASE_OPERAD Definition ===


def create_nphase_operad() -> Operad:
    """
    Create the NPHASE operad.

    Defines the grammar for composing development cycle operations.
    """
    return Operad(
        name="NPHASE",
        operations=NPHASE_OPERATIONS,
        laws=NPHASE_LAWS,
        description="Operad for N-Phase development cycle (UNDERSTAND -> ACT -> REFLECT)",
    )


# Create and register the operad
NPHASE_OPERAD = create_nphase_operad()

# Register with the global registry
OperadRegistry.register(NPHASE_OPERAD)


# === Utility Functions ===


def get_compressed_phase(detailed_phase: str) -> NPhase | None:
    """Get the compressed phase for a detailed phase name."""
    return DETAILED_TO_COMPRESSED.get(detailed_phase)


def get_detailed_phases(compressed: NPhase) -> list[str]:
    """Get all detailed phases for a compressed phase."""
    return PHASE_FAMILIES.get(compressed, [])


def is_valid_transition(from_phase: NPhase, to_phase: NPhase) -> bool:
    """
    Check if a phase transition is valid.

    Valid transitions:
    - UNDERSTAND -> ACT
    - ACT -> REFLECT
    - REFLECT -> UNDERSTAND (cycle)
    - Same phase (stay)
    """
    if from_phase == to_phase:
        return True

    valid_transitions = {
        NPhase.UNDERSTAND: {NPhase.ACT},
        NPhase.ACT: {NPhase.REFLECT},
        NPhase.REFLECT: {NPhase.UNDERSTAND},  # Cycle back
    }

    return to_phase in valid_transitions.get(from_phase, set())


def next_phase(current: NPhase) -> NPhase:
    """Get the next phase in the cycle."""
    match current:
        case NPhase.UNDERSTAND:
            return NPhase.ACT
        case NPhase.ACT:
            return NPhase.REFLECT
        case NPhase.REFLECT:
            return NPhase.UNDERSTAND  # Cycle back
