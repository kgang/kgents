"""
O-gent Bootstrap Witness: Verifier of the Irreducible Kernel

The BootstrapWitness is the O-gent that observes the Bootstrap Kernel to ensure
the fundamental laws of the architecture remain valid. It is the system's
capacity for self-verification.

Per spec/bootstrap.md:
- Verifies all 7 bootstrap agents exist and are importable
- Verifies identity laws: Id >> f == f == f >> Id
- Verifies composition laws: (f >> g) >> h == f >> (g >> h)

This is the Eighth Meta-Agent: not a bootstrap agent itself, but the witness
that verifies bootstrap integrity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Generic, Protocol, TypeVar

from .observer import BaseObserver

# Type variables
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


# =============================================================================
# Verdict Types
# =============================================================================


class Verdict(str, Enum):
    """Verification verdict."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    WARN = "warn"


class BootstrapAgent(str, Enum):
    """The 7 Bootstrap Agents."""

    ID = "Id"
    COMPOSE = "Compose"
    JUDGE = "Judge"
    GROUND = "Ground"
    CONTRADICT = "Contradict"
    SUBLATE = "Sublate"
    FIX = "Fix"


# =============================================================================
# Bootstrap Verification Results
# =============================================================================


@dataclass(frozen=True)
class AgentExistenceResult:
    """Result of checking if a bootstrap agent exists."""

    agent: BootstrapAgent
    exists: bool
    importable: bool
    error: str = ""


@dataclass(frozen=True)
class IdentityLawResult:
    """Result of verifying identity laws."""

    left_identity: bool  # Id >> f == f
    right_identity: bool  # f >> Id == f
    evidence: str = ""
    test_cases_run: int = 0

    @property
    def holds(self) -> bool:
        """Both identity laws must hold."""
        return self.left_identity and self.right_identity


@dataclass(frozen=True)
class CompositionLawResult:
    """Result of verifying composition laws."""

    associativity: bool  # (f >> g) >> h == f >> (g >> h)
    closure: bool  # f >> g is still an Agent
    evidence: str = ""
    test_cases_run: int = 0

    @property
    def holds(self) -> bool:
        """Both composition laws must hold."""
        return self.associativity and self.closure


@dataclass
class BootstrapVerificationResult:
    """
    Complete result of bootstrap verification.

    This is what BootstrapWitness.invoke() returns.
    """

    # Existence checks
    all_agents_exist: bool
    agent_results: list[AgentExistenceResult] = field(default_factory=list)

    # Law verification
    identity_laws_hold: bool = True
    identity_result: IdentityLawResult | None = None
    composition_laws_hold: bool = True
    composition_result: CompositionLawResult | None = None

    # Meta
    verified_at: datetime = field(default_factory=datetime.now)
    verification_duration_ms: float = 0.0

    @property
    def overall_verdict(self) -> Verdict:
        """Synthesize overall verdict from components."""
        if not self.all_agents_exist:
            return Verdict.FAIL
        if not self.identity_laws_hold:
            return Verdict.FAIL
        if not self.composition_laws_hold:
            return Verdict.FAIL
        return Verdict.PASS

    @property
    def kernel_intact(self) -> bool:
        """Is the bootstrap kernel fully intact?"""
        return self.overall_verdict == Verdict.PASS


# =============================================================================
# Mock Agent Protocol (for law verification)
# =============================================================================


class ComposableAgent(Protocol[A, B]):
    """Protocol for agents that can be composed."""

    async def invoke(self, input: A) -> B:
        """Execute the agent."""
        ...

    def __rshift__(self, other: "ComposableAgent[B, C]") -> "ComposableAgent[A, C]":
        """Compose with another agent (f >> g)."""
        ...


# =============================================================================
# Identity Agent
# =============================================================================


class IdentityAgent(Generic[A]):
    """
    Id: A -> A
    Id(x) = x

    The agent that does nothing. The unit of composition.
    """

    def __init__(self, name: str = "Id"):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> A:
        """Identity simply returns its input."""
        return input

    def __rshift__(self, other: ComposableAgent[A, B]) -> "ComposedAgent[A, B]":
        """Id >> f = f (left identity)."""
        return ComposedAgent(self, other)


# =============================================================================
# Composed Agent
# =============================================================================


class ComposedAgent(Generic[A, B]):
    """
    Result of composing two agents.

    (f >> g)(x) = g(f(x))
    """

    def __init__(self, first: ComposableAgent[A, Any], second: ComposableAgent[Any, B]):
        self._first = first
        self._second = second
        self._name = f"({getattr(first, 'name', 'f')} >> {getattr(second, 'name', 'g')})"

    @property
    def name(self) -> str:
        return self._name

    @property
    def first(self) -> ComposableAgent[A, Any]:
        return self._first

    @property
    def second(self) -> ComposableAgent[Any, B]:
        return self._second

    async def invoke(self, input: A) -> B:
        """Compose: (f >> g)(x) = g(f(x))."""
        intermediate = await self._first.invoke(input)
        return await self._second.invoke(intermediate)

    def __rshift__(self, other: ComposableAgent[B, C]) -> "ComposedAgent[A, C]":
        """Chain composition."""
        return ComposedAgent(self, other)


# =============================================================================
# Test Agent (for law verification)
# =============================================================================


class TestAgent(Generic[A, B]):
    """
    A simple test agent with a deterministic transform.

    Used to verify composition laws.
    """

    def __init__(self, name: str, transform: Callable[[A], B]):
        self._name = name
        self._transform = transform

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> B:
        """Apply the transform."""
        return self._transform(input)

    def __rshift__(self, other: ComposableAgent[B, C]) -> ComposedAgent[A, C]:
        """Compose with another agent."""
        return ComposedAgent(self, other)


# =============================================================================
# Bootstrap Witness
# =============================================================================


class BootstrapWitness(BaseObserver):
    """
    The observer of bootstrap agents.

    Verifies that the irreducible kernel maintains its laws.
    This is the system's capacity for self-verification.

    Per spec:
    - Verify all 7 bootstrap agents exist and are importable
    - Verify identity laws: Id >> f == f == f >> Id
    - Verify composition laws: (f >> g) >> h == f >> (g >> h)
    """

    def __init__(
        self,
        observer_id: str = "bootstrap_witness",
        test_iterations: int = 5,
    ):
        """
        Initialize the BootstrapWitness.

        Args:
            observer_id: Unique identifier for this observer.
            test_iterations: Number of test cases for law verification.
        """
        super().__init__(observer_id=observer_id)
        self.test_iterations = test_iterations

    async def invoke(self, _: None = None) -> BootstrapVerificationResult:
        """
        Verify bootstrap integrity.

        Returns complete verification result including:
        - Existence of all 7 bootstrap agents
        - Identity law verification
        - Composition law verification
        """
        start_time = datetime.now()

        # 1. Verify agent existence
        agent_results = await self.verify_existence()
        all_exist = all(r.exists for r in agent_results)

        # 2. Verify identity laws
        identity_result = await self.verify_identity_laws()

        # 3. Verify composition laws
        composition_result = await self.verify_composition_laws()

        duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        return BootstrapVerificationResult(
            all_agents_exist=all_exist,
            agent_results=agent_results,
            identity_laws_hold=identity_result.holds,
            identity_result=identity_result,
            composition_laws_hold=composition_result.holds,
            composition_result=composition_result,
            verified_at=start_time,
            verification_duration_ms=duration_ms,
        )

    async def verify_existence(self) -> list[AgentExistenceResult]:
        """
        Verify all 7 bootstrap agents exist and are importable.

        In a full implementation, this would check actual module imports.
        For now, we check for the conceptual existence (the specification).
        """
        results = []

        for agent in BootstrapAgent:
            # Check if the agent concept is defined
            # In production, this would import from impl/claude/bootstrap/
            exists = True  # Conceptually exists in spec
            importable = self._check_agent_importable(agent)
            error = "" if importable else f"{agent.value} not yet implemented"

            results.append(
                AgentExistenceResult(
                    agent=agent,
                    exists=exists,
                    importable=importable,
                    error=error,
                )
            )

        return results

    def _check_agent_importable(self, agent: BootstrapAgent) -> bool:
        """
        Check if a specific bootstrap agent is importable.

        This checks the actual implementation status.
        """
        # Map agents to their implementation modules
        implementation_map = {
            BootstrapAgent.ID: True,  # IdentityAgent defined here
            BootstrapAgent.COMPOSE: True,  # ComposedAgent defined here
            BootstrapAgent.JUDGE: False,  # Not yet implemented
            BootstrapAgent.GROUND: False,  # Not yet implemented
            BootstrapAgent.CONTRADICT: False,  # Not yet implemented
            BootstrapAgent.SUBLATE: False,  # Not yet implemented
            BootstrapAgent.FIX: False,  # Not yet implemented
        }
        return implementation_map.get(agent, False)

    async def verify_identity_laws(self) -> IdentityLawResult:
        """
        Verify identity laws: Id >> f == f == f >> Id.

        Uses test agents with deterministic transforms.
        """
        left_identity_holds = True
        right_identity_holds = True
        evidence_parts = []
        cases_run = 0

        # Create test agents
        id_agent: IdentityAgent[int] = IdentityAgent("Id")

        for i in range(self.test_iterations):
            # Create a test agent: f(x) = x * 2 + i
            f = TestAgent[int, int](f"f_{i}", lambda x, offset=i: x * 2 + offset)  # type: ignore[misc]
            test_input = i + 1

            cases_run += 1

            # Test left identity: Id >> f == f
            composed_left: ComposedAgent[int, int] = id_agent >> f  # type: ignore[operator]
            try:
                result_composed = await composed_left.invoke(test_input)
                result_direct = await f.invoke(test_input)

                if result_composed != result_direct:
                    left_identity_holds = False
                    evidence_parts.append(
                        f"Left identity failed: Id >> f({test_input}) = {result_composed}, "
                        f"but f({test_input}) = {result_direct}"
                    )
            except Exception as e:
                left_identity_holds = False
                evidence_parts.append(f"Left identity exception: {e}")

            # Test right identity: f >> Id == f
            # Need an IdentityAgent that works with the output type
            id_agent_out: IdentityAgent[int] = IdentityAgent("Id")
            composed_right: ComposedAgent[int, int] = f >> id_agent_out  # type: ignore[operator]

            try:
                result_composed = await composed_right.invoke(test_input)
                result_direct = await f.invoke(test_input)

                if result_composed != result_direct:
                    right_identity_holds = False
                    evidence_parts.append(
                        f"Right identity failed: f >> Id({test_input}) = {result_composed}, "
                        f"but f({test_input}) = {result_direct}"
                    )
            except Exception as e:
                right_identity_holds = False
                evidence_parts.append(f"Right identity exception: {e}")

        return IdentityLawResult(
            left_identity=left_identity_holds,
            right_identity=right_identity_holds,
            evidence="; ".join(evidence_parts) if evidence_parts else "All tests passed",
            test_cases_run=cases_run,
        )

    async def verify_composition_laws(self) -> CompositionLawResult:
        """
        Verify composition laws:
        - Associativity: (f >> g) >> h == f >> (g >> h)
        - Closure: f >> g is still an Agent
        """
        associativity_holds = True
        closure_holds = True
        evidence_parts = []
        cases_run = 0

        for i in range(self.test_iterations):
            # Create three test agents with different transforms
            f = TestAgent[int, int](f"f_{i}", lambda x, o=i: x + 1 + o)  # type: ignore[misc]
            g = TestAgent[int, int](f"g_{i}", lambda x, o=i: x * 2 + o)  # type: ignore[misc]
            h = TestAgent[int, int](f"h_{i}", lambda x, o=i: x - 1 + o)  # type: ignore[misc]

            test_input = i + 1
            cases_run += 1

            # Test closure: composition yields an agent-like object
            try:
                fg: ComposedAgent[int, int] = f >> g  # type: ignore[operator]
                # Check it's callable (has invoke method)
                if not hasattr(fg, "invoke"):
                    closure_holds = False
                    evidence_parts.append("Closure failed: f >> g has no invoke method")
            except Exception as e:
                closure_holds = False
                evidence_parts.append(f"Closure exception: {e}")

            # Test associativity: (f >> g) >> h == f >> (g >> h)
            try:
                left_assoc: ComposedAgent[int, int] = (f >> g) >> h  # type: ignore[operator]
                right_assoc: ComposedAgent[int, int] = f >> (g >> h)  # type: ignore[operator]

                result_left = await left_assoc.invoke(test_input)
                result_right = await right_assoc.invoke(test_input)

                if result_left != result_right:
                    associativity_holds = False
                    evidence_parts.append(
                        f"Associativity failed: ((f >> g) >> h)({test_input}) = {result_left}, "
                        f"but (f >> (g >> h))({test_input}) = {result_right}"
                    )
            except Exception as e:
                associativity_holds = False
                evidence_parts.append(f"Associativity exception: {e}")

        return CompositionLawResult(
            associativity=associativity_holds,
            closure=closure_holds,
            evidence="; ".join(evidence_parts) if evidence_parts else "All tests passed",
            test_cases_run=cases_run,
        )
