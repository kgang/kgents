"""
K-gent Polynomial: Eigenvector Contexts as Polynomial Positions.

The K-gent polynomial models the Kent soul as a state machine that
navigates eigenvector contexts:
- AESTHETIC: "Does this need to exist?"
- CATEGORICAL: "What's the morphism?"
- GRATITUDE: "What deserves more respect?"
- HETERARCHY: "Could this be peer-to-peer?"
- GENERATIVITY: "What can this generate?"
- JOY: "Where's the delight?"

The Insight:
    The soul is not a single perspective, but a sheaf of eigenvector contexts.
    Each context produces different judgments on the same input.
    The polynomial structure lets us compose contexts through SOUL_SHEAF.

Example:
    >>> agent = SoulPolynomialAgent()
    >>> response = await agent.query("Should I add this feature?")
    >>> print(response.context, response.judgment)

See: plans/architecture/polyfunctor.md (Phase 3: K-gent Migration)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent
from agents.sheaf.protocol import SOUL_SHEAF, Context

# =============================================================================
# Eigenvector State Machine
# =============================================================================


class EigenvectorContext(Enum):
    """
    Positions in the K-gent polynomial.

    These map directly to the SOUL_SHEAF contexts:
    - AESTHETIC → minimalism, "Does this need to exist?"
    - CATEGORICAL → abstraction, "What's the morphism?"
    - GRATITUDE → sacred/surplus, "What deserves more respect?"
    - HETERARCHY → peer-to-peer, "Could this be decentralized?"
    - GENERATIVITY → spec→impl, "What can this generate?"
    - JOY → playfulness, "Where's the delight?"

    The SYNTHESIZING state glues all contexts via SOUL_SHEAF.
    """

    AESTHETIC = auto()
    CATEGORICAL = auto()
    GRATITUDE = auto()
    HETERARCHY = auto()
    GENERATIVITY = auto()
    JOY = auto()
    SYNTHESIZING = auto()  # Meta-state: glue all contexts


@dataclass(frozen=True)
class SoulQuery:
    """Input to the K-gent polynomial."""

    message: str
    context_hint: EigenvectorContext | None = None
    depth: int = 1  # How many contexts to traverse


@dataclass(frozen=True)
class SoulJudgment:
    """Output from a single eigenvector context."""

    context: EigenvectorContext
    question: str
    judgment: str
    value: float  # Eigenvector coordinate value
    input_summary: str


@dataclass(frozen=True)
class SoulResponse:
    """Full response from K-gent polynomial."""

    query: SoulQuery
    judgments: list[SoulJudgment]
    synthesis: str | None
    primary_context: EigenvectorContext


# =============================================================================
# Eigenvector Values (from KentEigenvectors)
# =============================================================================

EIGENVECTOR_VALUES: dict[EigenvectorContext, float] = {
    EigenvectorContext.AESTHETIC: 0.15,  # Minimalist (low = minimal)
    EigenvectorContext.CATEGORICAL: 0.92,  # Abstract (high = abstract)
    EigenvectorContext.GRATITUDE: 0.78,  # Sacred (high = sacred)
    EigenvectorContext.HETERARCHY: 0.88,  # Peer (high = peer-to-peer)
    EigenvectorContext.GENERATIVITY: 0.90,  # Generative (high = generation)
    EigenvectorContext.JOY: 0.75,  # Playful (high = playful)
}

EIGENVECTOR_QUESTIONS: dict[EigenvectorContext, str] = {
    EigenvectorContext.AESTHETIC: "Does this need to exist?",
    EigenvectorContext.CATEGORICAL: "What's the morphism?",
    EigenvectorContext.GRATITUDE: "What deserves more respect?",
    EigenvectorContext.HETERARCHY: "Could this be peer-to-peer?",
    EigenvectorContext.GENERATIVITY: "What can this generate?",
    EigenvectorContext.JOY: "Where's the delight?",
    EigenvectorContext.SYNTHESIZING: "What does the whole soul say?",
}

EIGENVECTOR_JUDGMENTS: dict[EigenvectorContext, str] = {
    EigenvectorContext.AESTHETIC: "Consider what can be removed.",
    EigenvectorContext.CATEGORICAL: "Find the structure beneath the surface.",
    EigenvectorContext.GRATITUDE: "Honor the accursed share.",
    EigenvectorContext.HETERARCHY: "Forest over King.",
    EigenvectorContext.GENERATIVITY: "Spec compresses impl.",
    EigenvectorContext.JOY: "Being/having fun is free :)",
    EigenvectorContext.SYNTHESIZING: "Hold all tensions productively.",
}


# =============================================================================
# Direction Functions (Context-Dependent Valid Inputs)
# =============================================================================


def eigenvector_directions(state: EigenvectorContext) -> FrozenSet[Any]:
    """
    Valid inputs for each eigenvector state.

    All states accept SoulQuery, but SYNTHESIZING also accepts
    partial results from other contexts.
    """
    base_dirs: frozenset[Any] = frozenset({SoulQuery, type(SoulQuery), Any})
    if state == EigenvectorContext.SYNTHESIZING:
        return base_dirs | frozenset({list, tuple})
    return base_dirs


# =============================================================================
# Transition Function
# =============================================================================


def eigenvector_transition(state: EigenvectorContext, input: Any) -> tuple[EigenvectorContext, Any]:
    """
    Eigenvector state transition function.

    This is the polynomial core:
    transition: State × Input → (NewState, Output)

    Each eigenvector context produces a judgment, then
    optionally transitions to SYNTHESIZING to combine all judgments.
    """
    # Handle SoulQuery input
    if isinstance(input, SoulQuery):
        query = input
        if state == EigenvectorContext.SYNTHESIZING:
            # In synthesis mode, gather judgments from all contexts
            judgments: list[SoulJudgment] = []
            for ctx in EigenvectorContext:
                if ctx != EigenvectorContext.SYNTHESIZING:
                    judgments.append(_make_judgment(ctx, query))

            synthesis = _synthesize(judgments)
            response = SoulResponse(
                query=query,
                judgments=judgments,
                synthesis=synthesis,
                primary_context=_find_primary(judgments),
            )
            return EigenvectorContext.AESTHETIC, response
        else:
            # Single context judgment
            judgment = _make_judgment(state, query)

            if query.depth > 1:
                # Continue to next context
                next_state = _next_context(state)
                return next_state, (query, [judgment])
            else:
                # Return single judgment
                response = SoulResponse(
                    query=query,
                    judgments=[judgment],
                    synthesis=None,
                    primary_context=state,
                )
                return state, response

    # Handle partial results (continuing traversal)
    if isinstance(input, tuple) and len(input) == 2:
        query, judgments = input
        if isinstance(judgments, list):
            judgment = _make_judgment(state, query)
            judgments.append(judgment)

            if len(judgments) >= 6 or state == EigenvectorContext.JOY:
                # Done traversing, synthesize
                return EigenvectorContext.SYNTHESIZING, (query, judgments)
            else:
                # Continue to next context
                next_state = _next_context(state)
                return next_state, (query, judgments)

    # Handle synthesis input
    if isinstance(input, tuple) and state == EigenvectorContext.SYNTHESIZING and len(input) == 2:
        query, judgments = input
        synthesis = _synthesize(judgments)
        response = SoulResponse(
            query=query,
            judgments=judgments,
            synthesis=synthesis,
            primary_context=_find_primary(judgments),
        )
        return EigenvectorContext.AESTHETIC, response

    # Default: wrap in SoulQuery
    query = SoulQuery(message=str(input))
    judgment = _make_judgment(state, query)
    response = SoulResponse(
        query=query,
        judgments=[judgment],
        synthesis=None,
        primary_context=state,
    )
    return state, response


def _make_judgment(ctx: EigenvectorContext, query: SoulQuery) -> SoulJudgment:
    """Create a judgment from an eigenvector context."""
    return SoulJudgment(
        context=ctx,
        question=EIGENVECTOR_QUESTIONS.get(ctx, "?"),
        judgment=EIGENVECTOR_JUDGMENTS.get(ctx, ""),
        value=EIGENVECTOR_VALUES.get(ctx, 0.5),
        input_summary=query.message[:100],
    )


def _next_context(current: EigenvectorContext) -> EigenvectorContext:
    """Get the next context in traversal order."""
    order = [
        EigenvectorContext.AESTHETIC,
        EigenvectorContext.CATEGORICAL,
        EigenvectorContext.GRATITUDE,
        EigenvectorContext.HETERARCHY,
        EigenvectorContext.GENERATIVITY,
        EigenvectorContext.JOY,
        EigenvectorContext.SYNTHESIZING,
    ]
    try:
        idx = order.index(current)
        return order[(idx + 1) % len(order)]
    except ValueError:
        return EigenvectorContext.SYNTHESIZING


def _synthesize(judgments: list[SoulJudgment]) -> str:
    """Synthesize multiple judgments into a coherent response."""
    if not judgments:
        return "No judgments to synthesize."

    # Collect key insights
    insights = [j.judgment for j in judgments[:3]]  # Top 3

    return f"Synthesis: {' | '.join(insights)}"


def _find_primary(judgments: list[SoulJudgment]) -> EigenvectorContext:
    """Find the primary (strongest) context."""
    if not judgments:
        return EigenvectorContext.AESTHETIC

    # For now, return the most extreme value (furthest from 0.5)
    primary = max(judgments, key=lambda j: abs(j.value - 0.5))
    return primary.context


# =============================================================================
# Context Mapping (to SOUL_SHEAF)
# =============================================================================


def to_sheaf_context(ctx: EigenvectorContext) -> Context | None:
    """Map EigenvectorContext to SOUL_SHEAF Context."""
    from agents.sheaf.protocol import (
        AESTHETIC,
        CATEGORICAL,
        GENERATIVITY,
        GRATITUDE,
        HETERARCHY,
        JOY,
    )

    mapping = {
        EigenvectorContext.AESTHETIC: AESTHETIC,
        EigenvectorContext.CATEGORICAL: CATEGORICAL,
        EigenvectorContext.GRATITUDE: GRATITUDE,
        EigenvectorContext.HETERARCHY: HETERARCHY,
        EigenvectorContext.GENERATIVITY: GENERATIVITY,
        EigenvectorContext.JOY: JOY,
    }
    return mapping.get(ctx)


def from_sheaf_context(ctx: Context) -> EigenvectorContext | None:
    """Map SOUL_SHEAF Context to EigenvectorContext."""
    from agents.sheaf.protocol import (
        AESTHETIC,
        CATEGORICAL,
        GENERATIVITY,
        GRATITUDE,
        HETERARCHY,
        JOY,
    )

    mapping = {
        AESTHETIC: EigenvectorContext.AESTHETIC,
        CATEGORICAL: EigenvectorContext.CATEGORICAL,
        GRATITUDE: EigenvectorContext.GRATITUDE,
        HETERARCHY: EigenvectorContext.HETERARCHY,
        GENERATIVITY: EigenvectorContext.GENERATIVITY,
        JOY: EigenvectorContext.JOY,
    }
    return mapping.get(ctx)


# =============================================================================
# The Polynomial Agent
# =============================================================================


SOUL_POLYNOMIAL: PolyAgent[EigenvectorContext, Any, Any] = PolyAgent(
    name="SoulPolynomial",
    positions=frozenset(EigenvectorContext),
    _directions=eigenvector_directions,
    _transition=eigenvector_transition,
)
"""
The K-gent polynomial agent.

This maps the Kent soul to a polynomial state machine:
- positions: 6 eigenvector contexts + SYNTHESIZING
- directions: SoulQuery inputs
- transition: context traversal and synthesis
"""


# =============================================================================
# Backwards-Compatible Wrapper
# =============================================================================


class SoulPolynomialAgent:
    """
    Backwards-compatible K-gent polynomial wrapper.

    Provides async interface while using PolyAgent internally.
    Integrates with SOUL_SHEAF for global queries.

    Example:
        >>> agent = SoulPolynomialAgent()
        >>> response = await agent.query("Should I add this feature?")
        >>> print(response.primary_context.name, response.synthesis)
    """

    def __init__(self, initial_context: EigenvectorContext | None = None) -> None:
        self._poly = SOUL_POLYNOMIAL
        self._state = initial_context or EigenvectorContext.AESTHETIC

    @property
    def name(self) -> str:
        return "SoulPolynomialAgent"

    @property
    def state(self) -> EigenvectorContext:
        """Current eigenvector context."""
        return self._state

    def set_context(self, ctx: EigenvectorContext) -> None:
        """Set the current context."""
        self._state = ctx

    async def query(
        self,
        message: str,
        context: EigenvectorContext | None = None,
        depth: int = 1,
    ) -> SoulResponse:
        """
        Query the soul polynomial.

        Args:
            message: The query message
            context: Optional context to start from
            depth: How many contexts to traverse (1 = single, 6 = all)

        Returns:
            SoulResponse with judgments and optional synthesis
        """
        if context:
            self._state = context

        query = SoulQuery(message=message, context_hint=context, depth=depth)
        self._state, result = self._poly.transition(self._state, query)

        if isinstance(result, SoulResponse):
            return result

        # Handle partial results by continuing
        while not isinstance(result, SoulResponse):
            self._state, result = self._poly.transition(self._state, result)

        return result

    async def query_all(self, message: str) -> SoulResponse:
        """
        Query all eigenvector contexts and synthesize.

        This is the full K-gent polynomial cycle:
        traverses all 6 contexts then synthesizes.

        Args:
            message: The query message

        Returns:
            SoulResponse with all 6 judgments and synthesis
        """
        self._state = EigenvectorContext.SYNTHESIZING
        query = SoulQuery(message=message, depth=6)
        self._state, result = self._poly.transition(self._state, query)

        if isinstance(result, SoulResponse):
            return result

        # Should not happen, but handle gracefully
        return SoulResponse(
            query=query,
            judgments=[],
            synthesis="Error: synthesis incomplete",
            primary_context=EigenvectorContext.AESTHETIC,
        )

    async def query_sheaf(self, message: str) -> dict[str, Any]:
        """
        Query via SOUL_SHEAF for full emergent response.

        Uses the existing sheaf infrastructure for gluing.

        Args:
            message: The query message

        Returns:
            Dict with context-specific responses
        """
        from agents.sheaf.emergence import query_soul

        # Query the emergent soul
        return query_soul(message)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # State Machine
    "EigenvectorContext",
    # Types
    "SoulQuery",
    "SoulJudgment",
    "SoulResponse",
    # Values
    "EIGENVECTOR_VALUES",
    "EIGENVECTOR_QUESTIONS",
    "EIGENVECTOR_JUDGMENTS",
    # Polynomial Agent
    "SOUL_POLYNOMIAL",
    "eigenvector_directions",
    "eigenvector_transition",
    # Context Mapping
    "to_sheaf_context",
    "from_sheaf_context",
    # Wrapper
    "SoulPolynomialAgent",
]
