"""
E-gent Polynomial: Evolution Phases as State Machine.

The E-gent polynomial models the thermodynamic evolution cycle:
- IDLE: Ready for new cycle
- SUN: Acquiring energy (grants)
- MUTATE: Generating mutations
- SELECT: Demon selection (5-layer filter)
- WAGER: Placing bets/stakes
- INFECT: Applying mutations
- PAYOFF: Settling economics
- COMPLETE: Cycle finished

The Insight:
    Evolution is not random mutation, but a thermodynamic state machine.
    The Gibbs Free Energy guides transitions between phases.
    The polynomial structure enables composable evolution operators.

Example:
    >>> agent = EvolutionPolynomialAgent()
    >>> result = await agent.evolve(code, intent="Improve performance")
    >>> print(result.mutations_succeeded, result.temperature)

See: plans/architecture/polyfunctor.md (Phase 3: E-gent Migration)
See: spec/e-gents/thermodynamics.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, FrozenSet
from uuid import uuid4

from agents.poly.protocol import PolyAgent

# =============================================================================
# Evolution State Machine
# =============================================================================


class EvolutionPhase(Enum):
    """
    Positions in the E-gent polynomial.

    These model the thermodynamic cycle:
    - IDLE: Ready for new cycle
    - SUN: Acquiring energy from grants
    - MUTATE: Generating mutations via schemas
    - SELECT: Filtering via Teleological Demon
    - WAGER: Placing economic stakes
    - INFECT: Applying mutations with rollback
    - PAYOFF: Settling economics
    - COMPLETE: Cycle finished

    The cycle is a heat engine with a teleological field.
    """

    IDLE = auto()
    SUN = auto()
    MUTATE = auto()
    SELECT = auto()
    WAGER = auto()
    INFECT = auto()
    PAYOFF = auto()
    COMPLETE = auto()


@dataclass(frozen=True)
class EvolutionIntent:
    """Intent for guiding evolution."""

    description: str
    embedding: tuple[float, ...] = ()
    confidence: float = 0.5


@dataclass(frozen=True)
class Mutation:
    """A single mutation (simplified Phage)."""

    id: str
    schema_signature: str
    original_code: str
    mutated_code: str
    gibbs_free_energy: float = 0.0
    intent_alignment: float = 0.5


@dataclass
class EvolutionState:
    """State tracked through evolution cycle."""

    cycle_id: str = field(default_factory=lambda: f"cycle_{uuid4().hex[:8]}")
    phase: EvolutionPhase = EvolutionPhase.IDLE
    temperature: float = 1.0
    intent: EvolutionIntent | None = None
    mutations: list[Mutation] = field(default_factory=list)
    selected: list[Mutation] = field(default_factory=list)
    succeeded: list[Mutation] = field(default_factory=list)
    failed: list[Mutation] = field(default_factory=list)
    tokens_staked: int = 0
    tokens_won: int = 0
    tokens_lost: int = 0
    started_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class StartCycleCommand:
    """Command to start a new evolution cycle."""

    code: str
    intent: EvolutionIntent | None = None
    temperature: float = 1.0
    grant_id: str | None = None


@dataclass(frozen=True)
class MutateCommand:
    """Command to generate mutations."""

    code: str
    max_mutations: int = 10


@dataclass(frozen=True)
class SelectCommand:
    """Command to select mutations via Demon."""

    mutations: tuple[Mutation, ...]
    min_intent_alignment: float = 0.3


@dataclass(frozen=True)
class WagerCommand:
    """Command to place stakes."""

    mutations: tuple[Mutation, ...]
    stake_per_mutation: int = 100


@dataclass(frozen=True)
class InfectCommand:
    """Command to apply mutations."""

    mutations: tuple[Mutation, ...]
    run_tests: bool = True


@dataclass(frozen=True)
class PayoffCommand:
    """Command to settle economics."""

    succeeded: tuple[Mutation, ...]
    failed: tuple[Mutation, ...]


@dataclass
class EvolutionResult:
    """Result of evolution cycle."""

    cycle_id: str
    success: bool
    phase: EvolutionPhase
    mutations_generated: int = 0
    mutations_selected: int = 0
    mutations_succeeded: int = 0
    mutations_failed: int = 0
    temperature: float = 1.0
    gibbs_change: float = 0.0
    duration_ms: float = 0.0
    error: str | None = None


# =============================================================================
# Direction Functions (Phase-Dependent Valid Inputs)
# =============================================================================


def evolution_directions(phase: EvolutionPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each evolution phase.

    This encodes the thermodynamic cycle structure.
    """
    match phase:
        case EvolutionPhase.IDLE:
            return frozenset({StartCycleCommand, type(StartCycleCommand), Any})
        case EvolutionPhase.SUN:
            return frozenset({str, type(None), Any})  # Grant ID or None
        case EvolutionPhase.MUTATE:
            return frozenset({MutateCommand, str, Any})  # Code or command
        case EvolutionPhase.SELECT:
            return frozenset({SelectCommand, list, tuple, Any})  # Mutations
        case EvolutionPhase.WAGER:
            return frozenset({WagerCommand, list, tuple, Any})  # Selected
        case EvolutionPhase.INFECT:
            return frozenset({InfectCommand, list, tuple, Any})  # Staked
        case EvolutionPhase.PAYOFF:
            return frozenset({PayoffCommand, tuple, Any})  # Results
        case EvolutionPhase.COMPLETE:
            return frozenset({Any})  # Anything returns result
        case _:
            return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


# Global state for the polynomial agent
_evolution_state: EvolutionState = EvolutionState()


def evolution_transition(
    phase: EvolutionPhase, input: Any
) -> tuple[EvolutionPhase, Any]:
    """
    Evolution state transition function.

    This is the polynomial core:
    transition: Phase × Command → (NewPhase, Result)

    Follows the thermodynamic cycle:
    IDLE → SUN → MUTATE → SELECT → WAGER → INFECT → PAYOFF → COMPLETE → IDLE
    """
    global _evolution_state

    match phase:
        case EvolutionPhase.IDLE:
            # Start a new cycle
            if isinstance(input, StartCycleCommand):
                cmd = input
            else:
                cmd = StartCycleCommand(code=str(input) if input else "")

            _evolution_state = EvolutionState(
                phase=EvolutionPhase.SUN,
                temperature=cmd.temperature,
                intent=cmd.intent,
            )
            return EvolutionPhase.SUN, cmd

        case EvolutionPhase.SUN:
            # Acquire energy (grants)
            # In a full implementation, this would check B-gent grants
            # For now, just boost temperature if "grant" mentioned
            if isinstance(input, StartCycleCommand):
                code = input.code
                if input.grant_id:
                    _evolution_state.temperature *= 1.2
            else:
                code = str(input) if input else ""

            return EvolutionPhase.MUTATE, MutateCommand(code=code)

        case EvolutionPhase.MUTATE:
            # Generate mutations
            if isinstance(input, MutateCommand):
                code = input.code
                max_mutations = input.max_mutations
            else:
                code = str(input) if input else ""
                max_mutations = 10

            # Generate mock mutations (in real impl, use Mutator)
            mutations = _generate_mock_mutations(code, max_mutations)
            _evolution_state.mutations = list(mutations)

            return EvolutionPhase.SELECT, SelectCommand(mutations=tuple(mutations))

        case EvolutionPhase.SELECT:
            # Filter via Teleological Demon
            if isinstance(input, SelectCommand):
                mutations = list(input.mutations)
                min_alignment = input.min_intent_alignment
            elif isinstance(input, (list, tuple)):
                mutations = list(input)
                min_alignment = 0.3
            else:
                mutations = _evolution_state.mutations
                min_alignment = 0.3

            # Simple selection: filter by intent alignment
            selected = [m for m in mutations if m.intent_alignment >= min_alignment]
            _evolution_state.selected = selected

            return EvolutionPhase.WAGER, WagerCommand(mutations=tuple(selected))

        case EvolutionPhase.WAGER:
            # Place stakes
            if isinstance(input, WagerCommand):
                mutations = list(input.mutations)
                stake = input.stake_per_mutation
            elif isinstance(input, (list, tuple)):
                mutations = list(input)
                stake = 100
            else:
                mutations = _evolution_state.selected
                stake = 100

            total_stake = len(mutations) * stake
            _evolution_state.tokens_staked = total_stake

            return EvolutionPhase.INFECT, InfectCommand(mutations=tuple(mutations))

        case EvolutionPhase.INFECT:
            # Apply mutations
            if isinstance(input, InfectCommand):
                mutations = list(input.mutations)
                # run_tests flag used for simulation control (future feature)
                _ = input.run_tests  # noqa: F841
            elif isinstance(input, (list, tuple)):
                mutations = list(input)
            else:
                mutations = _evolution_state.selected

            # Simulate infection results based on Gibbs free energy
            succeeded = []
            failed = []
            for m in mutations:
                # Negative Gibbs = favorable = more likely to succeed
                if m.gibbs_free_energy < 0 or m.intent_alignment > 0.7:
                    succeeded.append(m)
                else:
                    failed.append(m)

            _evolution_state.succeeded = succeeded
            _evolution_state.failed = failed

            return EvolutionPhase.PAYOFF, PayoffCommand(
                succeeded=tuple(succeeded), failed=tuple(failed)
            )

        case EvolutionPhase.PAYOFF:
            # Settle economics
            if isinstance(input, PayoffCommand):
                succeeded = list(input.succeeded)
                failed = list(input.failed)
            else:
                succeeded = _evolution_state.succeeded
                failed = _evolution_state.failed

            # Calculate payoffs
            stake_per = 100
            _evolution_state.tokens_won = len(succeeded) * int(stake_per * 1.2)
            _evolution_state.tokens_lost = len(failed) * stake_per

            # Adjust temperature
            success_rate = len(succeeded) / max(1, len(succeeded) + len(failed))
            if success_rate > 0.7:
                _evolution_state.temperature *= 0.95  # Cool (exploit)
            elif success_rate < 0.3:
                _evolution_state.temperature *= 1.1  # Heat (explore)

            return EvolutionPhase.COMPLETE, _make_result()

        case EvolutionPhase.COMPLETE:
            # Return final result and reset
            result = _make_result()
            _evolution_state = EvolutionState()
            return EvolutionPhase.IDLE, result

        case _:
            return EvolutionPhase.IDLE, EvolutionResult(
                cycle_id="error",
                success=False,
                phase=phase,
                error=f"Unknown phase: {phase}",
            )


def _generate_mock_mutations(code: str, max_mutations: int) -> list[Mutation]:
    """Generate mock mutations for testing."""
    mutations = []
    for i in range(min(max_mutations, 3)):  # Generate up to 3
        mutations.append(
            Mutation(
                id=f"mut_{uuid4().hex[:8]}",
                schema_signature=f"schema_{i}",
                original_code=code[:100],
                mutated_code=f"{code[:100]}_mutated_{i}",
                gibbs_free_energy=-0.5 if i < 2 else 0.5,  # First 2 favorable
                intent_alignment=0.8 - i * 0.2,  # Decreasing alignment
            )
        )
    return mutations


def _make_result() -> EvolutionResult:
    """Create result from current state."""
    duration = (datetime.now() - _evolution_state.started_at).total_seconds() * 1000
    gibbs_change = sum(m.gibbs_free_energy for m in _evolution_state.succeeded)

    return EvolutionResult(
        cycle_id=_evolution_state.cycle_id,
        success=len(_evolution_state.succeeded) > 0,
        phase=EvolutionPhase.COMPLETE,
        mutations_generated=len(_evolution_state.mutations),
        mutations_selected=len(_evolution_state.selected),
        mutations_succeeded=len(_evolution_state.succeeded),
        mutations_failed=len(_evolution_state.failed),
        temperature=_evolution_state.temperature,
        gibbs_change=gibbs_change,
        duration_ms=duration,
    )


# =============================================================================
# The Polynomial Agent
# =============================================================================


EVOLUTION_POLYNOMIAL: PolyAgent[EvolutionPhase, Any, Any] = PolyAgent(
    name="EvolutionPolynomial",
    positions=frozenset(EvolutionPhase),
    _directions=evolution_directions,
    _transition=evolution_transition,
)
"""
The E-gent polynomial agent.

This models evolution as a thermodynamic polynomial:
- positions: 8 cycle phases
- directions: phase-dependent commands
- transition: thermodynamic cycle with Gibbs guidance
"""


# =============================================================================
# Backwards-Compatible Wrapper
# =============================================================================


class EvolutionPolynomialAgent:
    """
    Backwards-compatible E-gent polynomial wrapper.

    Provides async interface while using PolyAgent internally.

    Example:
        >>> agent = EvolutionPolynomialAgent()
        >>> result = await agent.evolve("def foo(): pass", intent="Optimize")
        >>> print(result.mutations_succeeded)
    """

    def __init__(self, temperature: float = 1.0) -> None:
        self._poly = EVOLUTION_POLYNOMIAL
        self._phase = EvolutionPhase.IDLE
        self._temperature = temperature

    @property
    def name(self) -> str:
        return "EvolutionPolynomialAgent"

    @property
    def phase(self) -> EvolutionPhase:
        """Current evolution phase."""
        return self._phase

    @property
    def temperature(self) -> float:
        """Current system temperature."""
        return self._temperature

    def reset(self) -> None:
        """Reset to IDLE phase."""
        global _evolution_state
        self._phase = EvolutionPhase.IDLE
        _evolution_state = EvolutionState()

    async def evolve(
        self,
        code: str,
        intent: str | EvolutionIntent | None = None,
        temperature: float | None = None,
        grant_id: str | None = None,
    ) -> EvolutionResult:
        """
        Run a full evolution cycle.

        Args:
            code: Source code to evolve
            intent: Optional intent description
            temperature: Optional temperature override
            grant_id: Optional grant ID for funding

        Returns:
            EvolutionResult with cycle metrics
        """
        self.reset()

        # Create intent
        intent_obj: EvolutionIntent | None = None
        if isinstance(intent, str):
            intent_obj = EvolutionIntent(description=intent)
        elif isinstance(intent, EvolutionIntent):
            intent_obj = intent

        # Start cycle
        cmd = StartCycleCommand(
            code=code,
            intent=intent_obj,
            temperature=temperature or self._temperature,
            grant_id=grant_id,
        )

        # Run through all phases
        current_input: Any = cmd
        for _ in range(10):  # Max 10 transitions
            self._phase, current_input = self._poly.transition(
                self._phase, current_input
            )
            if isinstance(current_input, EvolutionResult):
                self._temperature = current_input.temperature
                return current_input

        # Should not reach here
        return EvolutionResult(
            cycle_id="error",
            success=False,
            phase=self._phase,
            error="Cycle did not complete",
        )

    async def step(self, input: Any) -> tuple[EvolutionPhase, Any]:
        """
        Execute a single phase transition.

        For fine-grained control over the evolution cycle.

        Args:
            input: Input for current phase

        Returns:
            Tuple of (new_phase, output)
        """
        self._phase, output = self._poly.transition(self._phase, input)
        return self._phase, output

    async def suggest(
        self,
        code: str,
        intent: str | None = None,
    ) -> list[Mutation]:
        """
        Get mutation suggestions without applying.

        Runs MUTATE and SELECT phases only.

        Args:
            code: Source code to analyze
            intent: Optional intent description

        Returns:
            List of selected mutations
        """
        self.reset()

        # Start and go through SUN
        cmd = StartCycleCommand(
            code=code,
            intent=EvolutionIntent(description=intent or ""),
        )
        self._phase, _ = self._poly.transition(EvolutionPhase.IDLE, cmd)
        self._phase, _ = self._poly.transition(self._phase, cmd)

        # MUTATE
        self._phase, select_cmd = self._poly.transition(
            self._phase, MutateCommand(code=code)
        )

        # SELECT
        if isinstance(select_cmd, SelectCommand):
            self._phase, wager_cmd = self._poly.transition(self._phase, select_cmd)
            if isinstance(wager_cmd, WagerCommand):
                return list(wager_cmd.mutations)

        return []


# =============================================================================
# Utility Functions
# =============================================================================


def reset_evolution() -> None:
    """Reset global evolution state (for testing)."""
    global _evolution_state
    _evolution_state = EvolutionState()


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # State Machine
    "EvolutionPhase",
    # Types
    "EvolutionIntent",
    "Mutation",
    "EvolutionState",
    # Commands
    "StartCycleCommand",
    "MutateCommand",
    "SelectCommand",
    "WagerCommand",
    "InfectCommand",
    "PayoffCommand",
    # Result
    "EvolutionResult",
    # Polynomial Agent
    "EVOLUTION_POLYNOMIAL",
    "evolution_directions",
    "evolution_transition",
    # Wrapper
    "EvolutionPolynomialAgent",
    # Utilities
    "reset_evolution",
]
