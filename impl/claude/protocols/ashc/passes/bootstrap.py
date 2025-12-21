"""
Bootstrap Passes

The 7 bootstrap agents wrapped as compiler passes.

Per the Constitution: "The bootstrap stops being manual foundation
and becomes verified output."

Each pass:
- Has a clear input/output type
- Produces witnesses (TraceWitnessResult)
- Composes via >>
- Satisfies categorical laws

| Bootstrap Agent | Compiler Pass Role |
|-----------------|-------------------|
| Id              | Identity pass (no-op) |
| Compose         | Pass composition operator (implicit in >>) |
| Judge           | Validation/acceptance pass |
| Ground          | Empirical data injection pass |
| Contradict      | Inconsistency detection pass |
| Sublate         | Synthesis/resolution pass |
| Fix             | Fixed-point iteration pass |
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..primitives import L0Primitives, get_primitives
from ..stubs import (
    contradict_stub,
    ground_manifest_stub,
    identity_stub,
    judge_spec_stub,
    sublate_stub,
)
from .core import ProofCarryingIR, VerificationGraph

if TYPE_CHECKING:
    from .composition import ComposedPass


# =============================================================================
# Base Pass Class
# =============================================================================


@dataclass
class BasePass:
    """
    Base class for bootstrap passes.

    Provides common functionality:
    - Witness generation via L0 primitives
    - >> composition operator
    - Type information
    """

    _primitives: L0Primitives | None = None

    @property
    def name(self) -> str:
        """The pass name. Override in subclasses."""
        return "base"

    @property
    def input_type(self) -> str:
        """The input type. Override in subclasses."""
        return "Any"

    @property
    def output_type(self) -> str:
        """The output type. Override in subclasses."""
        return "Any"

    @property
    def primitives(self) -> L0Primitives:
        """Get or create primitives instance."""
        if self._primitives is None:
            self._primitives = get_primitives()
        return self._primitives

    def __rshift__(self, other: "BasePass") -> "ComposedPass[Any, Any]":
        """Compose with another pass."""
        from .composition import ComposedPass

        return ComposedPass(first=self, second=other)

    def _create_witness(
        self,
        input_data: Any,
        output_data: Any,
    ) -> Any:
        """Create a TraceWitnessResult for this pass."""
        return self.primitives.witness(
            pass_name=self.name,
            input_data=input_data,
            output_data=output_data,
        )


# =============================================================================
# Identity Pass
# =============================================================================


@dataclass
class IdentityPass(BasePass):
    """
    Id: A -> A

    The identity pass. Does nothing. The unit of composition.

    Id >> f = f = f >> Id
    """

    @property
    def name(self) -> str:
        return "id"

    @property
    def input_type(self) -> str:
        return "A"

    @property
    def output_type(self) -> str:
        return "A"

    async def invoke(self, input: Any) -> ProofCarryingIR:
        """Identity simply returns its input with a witness."""
        # Apply identity (just returns input)
        output = await identity_stub(input)

        # Create witness
        witness = self._create_witness(input, output)

        return ProofCarryingIR.from_output(
            output=output,
            witness=witness,
            pass_name=self.name,
        )


# =============================================================================
# Ground Pass
# =============================================================================


@dataclass
class GroundPass(BasePass):
    """
    Ground: Void -> Facts

    Injects empirical data into the compiler.
    This is the "grounding" in reality.

    Source can be:
    - Persona manifest (preferences, voice)
    - Context (session, phase)
    - External facts
    """

    source: str = "manifest"  # "manifest" | "context"

    @property
    def name(self) -> str:
        return "ground"

    @property
    def input_type(self) -> str:
        return "Void"

    @property
    def output_type(self) -> str:
        return "Facts"

    async def invoke(self, _: None = None) -> ProofCarryingIR:
        """Ground produces facts from the source."""
        # Get facts from stub (will use Logos when available)
        facts = await ground_manifest_stub()

        # Create witness
        witness = self._create_witness(None, facts)

        return ProofCarryingIR.from_output(
            output=facts,
            witness=witness,
            pass_name=self.name,
        )


# =============================================================================
# Judge Pass
# =============================================================================


@dataclass
class JudgePass(BasePass):
    """
    Judge: (Spec, Principles) -> Verdict

    Validates against principles. The arbiter of acceptability.

    Returns verdict with:
    - pass/fail status
    - reason (why accepted or rejected)
    - evidence (what was checked)
    """

    @property
    def name(self) -> str:
        return "judge"

    @property
    def input_type(self) -> str:
        return "Spec"

    @property
    def output_type(self) -> str:
        return "Verdict"

    async def invoke(self, input: Any) -> ProofCarryingIR:
        """Judge validates input against principles."""
        # Convert input to dict if needed
        if not isinstance(input, dict):
            if hasattr(input, "__dict__"):
                spec = vars(input)
            else:
                spec = {"value": input}
        else:
            spec = input

        # Get verdict from stub
        verdict = await judge_spec_stub(spec)

        # Create witness
        witness = self._create_witness(spec, verdict)

        return ProofCarryingIR.from_output(
            output=verdict,
            witness=witness,
            pass_name=self.name,
        )


# =============================================================================
# Contradict Pass
# =============================================================================


@dataclass
class ContradictPass(BasePass):
    """
    Contradict: (A, B) -> Tension | None

    Detects inconsistencies between two inputs.
    Returns None if no contradiction found.

    The dialectical engine for finding tensions.
    """

    @property
    def name(self) -> str:
        return "contradict"

    @property
    def input_type(self) -> str:
        return "(A, B)"

    @property
    def output_type(self) -> str:
        return "Tension | None"

    async def invoke(self, input: tuple[Any, Any]) -> ProofCarryingIR:
        """Contradict checks for tensions between two inputs."""
        # Unpack inputs
        if isinstance(input, tuple) and len(input) == 2:
            a, b = input
        else:
            # Single input: compare against empty
            a, b = input, {}

        # Convert to dicts if needed
        a_dict = a if isinstance(a, dict) else {"value": a}
        b_dict = b if isinstance(b, dict) else {"value": b}

        # Check for contradiction
        tension = await contradict_stub(a_dict, b_dict)

        # Create witness
        witness = self._create_witness({"a": a_dict, "b": b_dict}, tension)

        return ProofCarryingIR.from_output(
            output=tension,
            witness=witness,
            pass_name=self.name,
        )


# =============================================================================
# Sublate Pass
# =============================================================================


@dataclass
class SublatePass(BasePass):
    """
    Sublate: Tension -> Synthesis

    Resolves tensions through synthesis.
    The Hegelian "aufheben" - preserve and transcend.

    Takes a contradiction and produces a synthesis that:
    - Preserves the valid aspects of both sides
    - Transcends the contradiction
    - Moves the dialectic forward
    """

    @property
    def name(self) -> str:
        return "sublate"

    @property
    def input_type(self) -> str:
        return "Tension"

    @property
    def output_type(self) -> str:
        return "Synthesis"

    async def invoke(self, input: Any) -> ProofCarryingIR:
        """Sublate synthesizes from tension."""
        # Convert input to dict if needed
        if not isinstance(input, dict):
            tension = {"tension": input}
        else:
            tension = input

        # Synthesize
        synthesis = await sublate_stub(tension)

        # Create witness
        witness = self._create_witness(tension, synthesis)

        return ProofCarryingIR.from_output(
            output=synthesis,
            witness=witness,
            pass_name=self.name,
        )


# =============================================================================
# Fix Pass
# =============================================================================


@dataclass
class FixPass(BasePass):
    """
    Fix: (A -> A) -> A

    Fixed-point iteration. Repeats until stable.

    Takes a self-referential transform and finds its fixed point.
    Used for:
    - Iterative refinement
    - Convergence to stable state
    - Self-consistent solutions
    """

    max_iterations: int = 10
    convergence_threshold: float = 0.0001

    @property
    def name(self) -> str:
        return "fix"

    @property
    def input_type(self) -> str:
        return "(A -> A)"

    @property
    def output_type(self) -> str:
        return "A"

    async def invoke(self, input: Any) -> ProofCarryingIR:
        """
        Fix finds the fixed point of the input.

        If input is a callable, iterate until stable.
        If input is a value, return it (trivial fixed point).
        """
        # If input is a ProofCarryingIR, extract the IR
        if isinstance(input, ProofCarryingIR):
            current = input.ir
        else:
            current = input

        iterations = 0
        history: list[Any] = [current]

        # If it's callable, iterate to fixed point
        if callable(current):
            transform = current
            current = None  # Start with None

            for i in range(self.max_iterations):
                iterations = i + 1
                try:
                    next_val = transform(current)
                    if hasattr(next_val, "__await__"):
                        next_val = await next_val

                    # Check for convergence
                    if next_val == current:
                        break

                    current = next_val
                    history.append(current)
                except Exception:
                    break

        # Create witness with iteration history
        result = {
            "fixed_point": current,
            "iterations": iterations,
            "converged": iterations < self.max_iterations,
        }
        witness = self._create_witness(
            {"input": str(input), "max_iterations": self.max_iterations},
            result,
        )

        return ProofCarryingIR.from_output(
            output=current,
            witness=witness,
            pass_name=self.name,
        )


# =============================================================================
# Factory Functions
# =============================================================================


def create_identity_pass() -> IdentityPass:
    """Create an identity pass."""
    return IdentityPass()


def create_ground_pass(source: str = "manifest") -> GroundPass:
    """Create a ground pass with specified source."""
    return GroundPass(source=source)


def create_judge_pass() -> JudgePass:
    """Create a judge pass."""
    return JudgePass()


def create_contradict_pass() -> ContradictPass:
    """Create a contradict pass."""
    return ContradictPass()


def create_sublate_pass() -> SublatePass:
    """Create a sublate pass."""
    return SublatePass()


def create_fix_pass(max_iterations: int = 10) -> FixPass:
    """Create a fix pass with specified max iterations."""
    return FixPass(max_iterations=max_iterations)


__all__ = [
    # Passes
    "BasePass",
    "IdentityPass",
    "GroundPass",
    "JudgePass",
    "ContradictPass",
    "SublatePass",
    "FixPass",
    # Factories
    "create_identity_pass",
    "create_ground_pass",
    "create_judge_pass",
    "create_contradict_pass",
    "create_sublate_pass",
    "create_fix_pass",
]
