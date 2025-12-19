"""
Alethic Agent: Polynomial Agent for Truth-Seeking.

The Alethic Agent models truth-seeking as a polynomial state machine:
- GROUNDING: Validating claims against reality
- DELIBERATING: Weighing evidence
- JUDGING: Producing verdicts
- SYNTHESIZING: Creating coherent responses

This module bridges the polynomial agent framework (PolyAgent[S, A, B]) with
the A-gent's alethic reasoning patterns.

The Insight:
    Alethic reasoning is not a function A → B, but a state machine that
    progresses through modes: ground → deliberate → judge → synthesize.
    Different inputs are valid at different stages.

Example:
    >>> agent = AlethicAgent()
    >>> state, response = await agent.reason(
    ...     Query(claim="The sky is blue", context={"source": "observation"})
    ... )
    >>> print(response.verdict)

See: plans/architecture/polyfunctor.md (Phase 3: Agent Genus Migration)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, FrozenSet, Sequence

from agents.poly.primitives import (
    GROUND,
    JUDGE,
    SUBLATE,
    Claim,
    GroundState,
    JudgeState,
    SublateState,
    Synthesis,
    Thesis,
    Verdict,
)
from agents.poly.protocol import PolyAgent

# =============================================================================
# Alethic State Machine
# =============================================================================


class AlethicState(Enum):
    """
    Positions in the alethic polynomial.

    The alethic agent progresses through these states:
    1. GROUNDING: Initial validation against facts
    2. DELIBERATING: Weighing evidence and arguments
    3. JUDGING: Reaching a verdict
    4. SYNTHESIZING: Producing coherent response

    Each state accepts different inputs (directions):
    - GROUNDING accepts Queries
    - DELIBERATING accepts Evidence
    - JUDGING accepts DeliberationResults
    - SYNTHESIZING accepts Verdicts
    """

    GROUNDING = auto()
    DELIBERATING = auto()
    JUDGING = auto()
    SYNTHESIZING = auto()


@dataclass(frozen=True)
class Query:
    """Input query to the alethic agent."""

    claim: str
    context: dict[str, Any] | None = None
    confidence_threshold: float = 0.5


@dataclass(frozen=True)
class Evidence:
    """Evidence for deliberation phase."""

    supporting: Sequence[str]
    contradicting: Sequence[str]
    neutral: Sequence[str] | None = None


@dataclass(frozen=True)
class DeliberationResult:
    """Result of evidence deliberation."""

    query: Query
    evidence: Evidence
    weighted_confidence: float
    reasoning: str


@dataclass(frozen=True)
class AlethicResponse:
    """Final response from alethic agent."""

    query: Query
    verdict: Verdict
    synthesis: Synthesis | None
    reasoning_trace: list[str]
    final_confidence: float


# =============================================================================
# Direction Functions (State-Dependent Valid Inputs)
# =============================================================================


def alethic_directions(state: AlethicState) -> FrozenSet[Any]:
    """
    Valid inputs for each alethic state.

    This encodes the polynomial functor structure:
    P(y) = Σ_{s ∈ AlethicState} y^{Directions(s)}
    """
    match state:
        case AlethicState.GROUNDING:
            return frozenset({Query, type(Query), Any})
        case AlethicState.DELIBERATING:
            return frozenset({Evidence, type(Evidence), Any})
        case AlethicState.JUDGING:
            return frozenset({DeliberationResult, type(DeliberationResult), Any})
        case AlethicState.SYNTHESIZING:
            return frozenset({Verdict, type(Verdict), Any})


# =============================================================================
# Transition Function
# =============================================================================


def _validate_query(input: Any) -> Query:
    """
    Validate and normalize input to a Query.

    Handles edge cases:
    - None input → empty claim query
    - Empty string → normalized to "empty"
    - Very long strings → truncated with warning
    """
    if input is None:
        return Query(claim="<empty>", confidence_threshold=0.5)

    if isinstance(input, Query):
        # Validate existing query
        claim = input.claim.strip() if input.claim else "<empty>"
        if len(claim) > 10000:
            claim = claim[:10000] + "... [truncated]"
        return Query(
            claim=claim,
            context=input.context,
            confidence_threshold=input.confidence_threshold,
        )

    # Convert to string
    claim = str(input).strip()
    if not claim:
        claim = "<empty>"
    if len(claim) > 10000:
        claim = claim[:10000] + "... [truncated]"

    return Query(claim=claim)


def _compute_confidence(n_supporting: int, n_contradicting: int, prior: float = 0.5) -> float:
    """
    Compute confidence with Bayesian-style propagation.

    Edge cases:
    - Empty evidence (0, 0) → return prior (default 0.5)
    - All supporting → high confidence (0.95 max)
    - All contradicting → low confidence (0.05 min)

    The prior acts as a regularizer to prevent extreme confidences.
    """
    total = n_supporting + n_contradicting
    if total == 0:
        return prior

    # Bayesian-style update with prior
    # Uses Laplace smoothing to prevent extreme values
    alpha = 1.0  # Smoothing parameter
    confidence = (n_supporting + alpha * prior) / (total + alpha)

    # Clamp to reasonable bounds
    return max(0.05, min(0.95, confidence))


def alethic_transition(state: AlethicState, input: Any) -> tuple[AlethicState, Any]:
    """
    Alethic state transition function.

    This is the core of the polynomial agent:
    transition: State × Input → (NewState, Output)

    The transition composes the primitive polynomial agents:
    - GROUND: Validates claims
    - JUDGE: Produces verdicts
    - SUBLATE: Synthesizes contradictions

    Edge cases handled:
    - Malformed queries: validated and normalized
    - Empty evidence: defaults to prior confidence
    - All contradicting: low confidence with synthesis
    """
    match state:
        case AlethicState.GROUNDING:
            # Validate and normalize query
            query = _validate_query(input)
            _, grounded = GROUND.invoke(GroundState.FLOATING, query.claim)
            # Transition to DELIBERATING with grounded result
            evidence = Evidence(
                supporting=[query.claim] if grounded.get("grounded") else [],
                contradicting=[] if grounded.get("grounded") else [query.claim],
            )
            return AlethicState.DELIBERATING, (query, evidence)

        case AlethicState.DELIBERATING:
            # Weight evidence and compute confidence
            if isinstance(input, tuple) and len(input) == 2:
                query, evidence = input
            elif isinstance(input, Evidence):
                query = Query(claim="unknown")
                evidence = input
            else:
                query = Query(claim=str(input))
                evidence = Evidence(supporting=[], contradicting=[])

            # Compute confidence using Bayesian propagation
            n_supporting = len(evidence.supporting)
            n_contradicting = len(evidence.contradicting)
            prior = query.confidence_threshold
            confidence = _compute_confidence(n_supporting, n_contradicting, prior)

            # Build reasoning string based on evidence state
            if n_supporting == 0 and n_contradicting == 0:
                reasoning = "No evidence; using prior confidence"
            elif n_contradicting == 0:
                reasoning = f"All {n_supporting} evidence supporting"
            elif n_supporting == 0:
                reasoning = f"All {n_contradicting} evidence contradicting"
            else:
                reasoning = f"Weighed {n_supporting} supporting vs {n_contradicting} contradicting"

            result = DeliberationResult(
                query=query,
                evidence=evidence,
                weighted_confidence=confidence,
                reasoning=reasoning,
            )
            return AlethicState.JUDGING, result

        case AlethicState.JUDGING:
            # Use JUDGE primitive
            if isinstance(input, DeliberationResult):
                result = input
                claim = Claim(
                    content=result.query.claim,
                    confidence=result.weighted_confidence,
                )
            else:
                claim = Claim(content=str(input), confidence=0.5)
                result = DeliberationResult(
                    query=Query(claim=claim.content),
                    evidence=Evidence(supporting=[], contradicting=[]),
                    weighted_confidence=0.5,
                    reasoning="Default deliberation",
                )

            _, verdict = JUDGE.invoke(JudgeState.DELIBERATING, claim)
            return AlethicState.SYNTHESIZING, (result, verdict)

        case AlethicState.SYNTHESIZING:
            # Produce final response
            if isinstance(input, tuple) and len(input) == 2:
                result, verdict = input
            elif isinstance(input, Verdict):
                verdict = input
                result = DeliberationResult(
                    query=Query(claim=verdict.claim.content),
                    evidence=Evidence(supporting=[], contradicting=[]),
                    weighted_confidence=verdict.claim.confidence,
                    reasoning="Direct verdict",
                )
            else:
                # Default case
                verdict = Verdict(
                    claim=Claim(content=str(input)),
                    accepted=False,
                    reasoning="Unknown input",
                )
                result = DeliberationResult(
                    query=Query(claim=str(input)),
                    evidence=Evidence(supporting=[], contradicting=[]),
                    weighted_confidence=0.5,
                    reasoning="Default",
                )

            # Synthesize if there were contradictions
            synthesis = None
            if isinstance(result, DeliberationResult) and result.evidence.contradicting:
                thesis = Thesis(content=result.query.claim)

                # Handle edge case: all evidence contradicts
                n_contradicting = len(result.evidence.contradicting)
                n_supporting = len(result.evidence.supporting)

                if n_supporting == 0 and n_contradicting > 0:
                    # All evidence contradicts - synthesize with strongest contradiction
                    antithesis_content = result.evidence.contradicting[0]
                else:
                    # Mixed evidence - synthesize with first contradiction
                    antithesis_content = result.evidence.contradicting[0]

                from agents.poly.primitives import Antithesis

                antithesis = Antithesis(thesis=thesis, contradiction=antithesis_content)
                try:
                    _, synthesis = SUBLATE.invoke(SublateState.ANALYZING, (thesis, antithesis))
                except Exception:
                    # Synthesis failed - create a fallback synthesis
                    synthesis = Synthesis(
                        thesis=thesis,
                        antithesis=antithesis,
                        resolution=f"Unable to synthesize: {thesis.content} vs {antithesis_content}",
                    )

            # Build reasoning trace with confidence propagation
            reasoning_trace = [
                f"Grounded: {result.query.claim}",
                f"Deliberated: {result.reasoning}",
                f"Judged: {verdict.reasoning}",
            ]

            # Add synthesis reasoning if present
            if synthesis is not None:
                reasoning_trace.append(f"Synthesized: {synthesis.resolution}")

            response = AlethicResponse(
                query=result.query,
                verdict=verdict,
                synthesis=synthesis,
                reasoning_trace=reasoning_trace,
                final_confidence=result.weighted_confidence,
            )
            # Return to GROUNDING for next query
            return AlethicState.GROUNDING, response


# =============================================================================
# The Polynomial Agent
# =============================================================================


ALETHIC_AGENT: PolyAgent[AlethicState, Any, Any] = PolyAgent(
    name="Alethic",
    positions=frozenset(AlethicState),
    _directions=alethic_directions,
    _transition=alethic_transition,
)
"""
The alethic polynomial agent.

This is the core polynomial structure for alethic reasoning:
- positions: {GROUNDING, DELIBERATING, JUDGING, SYNTHESIZING}
- directions: State-dependent valid inputs
- transition: (state, input) → (new_state, output)
"""


# =============================================================================
# Backwards-Compatible Wrapper
# =============================================================================


class AlethicAgent:
    """
    Backwards-compatible alethic agent wrapper.

    Provides a simple async interface while using PolyAgent internally.

    Example:
        >>> agent = AlethicAgent()
        >>> response = await agent.reason(Query(claim="The sky is blue"))
        >>> print(response.verdict.accepted)
    """

    def __init__(self) -> None:
        self._poly = ALETHIC_AGENT
        self._state = AlethicState.GROUNDING

    @property
    def name(self) -> str:
        return "AlethicAgent"

    @property
    def state(self) -> AlethicState:
        """Current state of the agent."""
        return self._state

    def reset(self) -> None:
        """Reset agent to initial state."""
        self._state = AlethicState.GROUNDING

    async def reason(self, query: Query) -> AlethicResponse:
        """
        Perform full alethic reasoning on a query.

        Runs the polynomial state machine through all four phases:
        GROUNDING → DELIBERATING → JUDGING → SYNTHESIZING

        Args:
            query: The query to reason about

        Returns:
            AlethicResponse with verdict, synthesis, and trace
        """
        self.reset()
        current_input: Any = query

        # Run through all states until we get back to GROUNDING
        for _ in range(4):  # Max 4 transitions
            self._state, current_input = self._poly.transition(self._state, current_input)
            if isinstance(current_input, AlethicResponse):
                return current_input

        # Should not reach here, but handle gracefully
        if isinstance(current_input, AlethicResponse):
            return current_input

        return AlethicResponse(
            query=query,
            verdict=Verdict(
                claim=Claim(content=query.claim),
                accepted=False,
                reasoning="Failed to complete reasoning",
            ),
            synthesis=None,
            reasoning_trace=["Error: Reasoning incomplete"],
            final_confidence=0.0,
        )

    async def step(self, input: Any) -> tuple[AlethicState, Any]:
        """
        Execute a single step of the polynomial state machine.

        For fine-grained control over the reasoning process.

        Args:
            input: Input appropriate for current state

        Returns:
            Tuple of (new_state, output)
        """
        self._state, output = self._poly.transition(self._state, input)
        return self._state, output


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # State Machine
    "AlethicState",
    # Types
    "Query",
    "Evidence",
    "DeliberationResult",
    "AlethicResponse",
    # Polynomial Agent
    "ALETHIC_AGENT",
    "alethic_directions",
    "alethic_transition",
    # Wrapper
    "AlethicAgent",
]
