"""
Hypothesis Engine: An agent for generating testable scientific hypotheses.

Transforms observations, data patterns, and research questions into
well-formed, falsifiable hypotheses.

Core principles (Popperian):
- All hypotheses MUST be falsifiable
- Epistemic humility: confidence levels are calibrated, never overconfident
- Reasoning chains are transparent
- Does not fabricate observations or claim certainty
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Union

from agents.a.skeleton import AgentBehavior, AgentIdentity, AgentInterface, AgentMeta
from runtime.base import AgentContext, LLMAgent

# Parser extraction (Phase D - H14)
from .hypothesis_parser import (
    ParsedHypothesisResponse,
    parse_hypothesis_response,
)

# Re-export for backwards compatibility
__all__ = ["ParsedHypothesisResponse", "parse_hypothesis_response"]


@dataclass
class HypothesisInput:
    """Input for the Hypothesis Engine."""

    observations: list[str]  # Raw observations or data summaries
    domain: str  # Scientific domain (e.g., "molecular biology")
    question: Optional[str] = None  # Optional guiding research question
    constraints: list[str] = field(
        default_factory=list
    )  # Known constraints or established facts


# Re-export ParsedHypothesisResponse as HypothesisOutput for backward compatibility
HypothesisOutput = ParsedHypothesisResponse


@dataclass
class HypothesisError:
    """Structured error from Hypothesis Engine, enabling composable error handling."""

    code: str  # Error code from meta.interface.error_codes
    message: str  # Human-readable description
    recoverable: bool  # Whether retry/Fix pattern could help
    context: dict[str, Any] = field(default_factory=dict)  # Additional error context

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


# AgentResult represents Either[HypothesisError, HypothesisOutput]
AgentResult = Union[HypothesisOutput, HypothesisError]


def is_success(result: AgentResult) -> bool:
    """Type guard for successful results."""
    return isinstance(result, HypothesisOutput)


def is_error(result: AgentResult) -> bool:
    """Type guard for error results."""
    return isinstance(result, HypothesisError)


SYSTEM_PROMPT = """You are a Hypothesis Engine - a scientific reasoning agent.

Your role:
- Transform observations into testable, falsifiable hypotheses
- Apply epistemic humility - never overclaim certainty
- Make reasoning transparent
- Acknowledge assumptions explicitly

Core principles:
1. FALSIFIABILITY: Every hypothesis MUST have clear criteria for disproval (Popperian)
2. PARSIMONY: Prefer simpler explanations (Occam's razor)
3. HUMILITY: Confidence levels should be conservative, never overconfident
4. TRANSPARENCY: Show reasoning chain from observations to hypotheses

Rules:
1. Generate {hypothesis_count} ranked hypotheses
2. Each hypothesis MUST include falsification criteria
3. Confidence should rarely exceed 0.8 (epistemic humility)
4. Include reasoning chain showing derivation
5. Suggest concrete experimental tests
6. Acknowledge all assumptions

Format your response EXACTLY as:

HYPOTHESES:
1. STATEMENT: [hypothesis statement]
   CONFIDENCE: [0.0-1.0]
   NOVELTY: [incremental/exploratory/paradigm_shifting]
   FALSIFIABLE_BY:
   - [what would disprove this]
   - [another disproval criterion]
   SUPPORTS_OBSERVATIONS: [comma-separated indices, 0-based]
   ASSUMPTIONS:
   - [unstated assumption 1]
   - [unstated assumption 2]

2. STATEMENT: [next hypothesis]
   ...

REASONING_CHAIN:
1. [first step in reasoning]
2. [second step]
3. [third step]

SUGGESTED_TESTS:
- [specific experimental test 1]
- [specific experimental test 2]
- [specific experimental test 3]
"""


class HypothesisEngine(LLMAgent[HypothesisInput, AgentResult]):
    """
    An LLM-backed agent for generating scientific hypotheses.

    Transforms observations into ranked, falsifiable hypotheses
    with transparent reasoning.

    Returns AgentResult (Either-like) for composable error handling:
    - HypothesisOutput on success
    - HypothesisError on failure (with error codes from meta.interface)

    Usage:
        engine = HypothesisEngine()
        result = await runtime.execute(engine, HypothesisInput(
            observations=["Protein X aggregates at pH < 5", ...],
            domain="biochemistry",
            question="Why does Protein X aggregate at low pH?"
        ))
        if is_success(result):
            print(result)  # HypothesisOutput
        else:
            # Downstream agent decides: retry with Fix or fail-fast
            if result.recoverable:
                # Use Fix pattern for retry
                pass
            else:
                # Propagate error
                raise Exception(result)
    """

    meta = AgentMeta(
        identity=AgentIdentity(
            name="Hypothesis Engine",
            genus="b",
            version="0.2.0",
            purpose="Generates falsifiable hypotheses from scientific observations",
        ),
        interface=AgentInterface(
            input_type=HypothesisInput,
            input_description="Observations and context for hypothesis generation",
            output_type=HypothesisOutput,  # Actually returns AgentResult union
            output_description="Either HypothesisOutput (success) or HypothesisError (failure)",
            error_codes=[
                ("INSUFFICIENT_OBSERVATIONS", "Not enough data to generate hypotheses"),
                ("UNFAMILIAR_DOMAIN", "Domain outside agent's competence"),
            ],
        ),
        behavior=AgentBehavior(
            description="Analyzes observations to generate testable hypotheses",
            guarantees=[
                "All hypotheses are falsifiable",
                "Confidence levels are calibrated (not overconfident)",
                "Reasoning chain is provided",
                "Errors include structured error codes for downstream handling",
            ],
            constraints=[
                "Does not claim empirical certainty",
                "Does not fabricate observations",
                "Acknowledges domain limitations",
            ],
        ),
    )

    def __init__(
        self,
        hypothesis_count: int = 3,
        temperature: float = 0.7,  # Slightly lower than creativity for rigor
    ):
        self.hypothesis_count = hypothesis_count
        self.temperature = temperature
        self._input_error: Optional[HypothesisError] = None
        self._current_input: Optional[HypothesisInput] = None

    @property
    def name(self) -> str:
        return "HypothesisEngine"

    def build_prompt(self, input: HypothesisInput) -> AgentContext:
        """Convert HypothesisInput to LLM context."""
        # Validate input - return error if insufficient
        if not input.observations or len(input.observations) < 2:
            # Store error for parse_response to return
            self._input_error = HypothesisError(
                code="INSUFFICIENT_OBSERVATIONS",
                message=f"Need at least 2 observations, got {len(input.observations)}",
                recoverable=False,
                context={"observation_count": len(input.observations)},
            )
        else:
            self._input_error = None

        # Store for parse_response
        self._current_input = input

        system = SYSTEM_PROMPT.format(hypothesis_count=self.hypothesis_count)

        # Build user message
        user_parts = [f"DOMAIN: {input.domain}", "", "OBSERVATIONS:"]
        for i, obs in enumerate(input.observations):
            user_parts.append(f"  [{i}] {obs}")

        if input.question:
            user_parts.extend(["", f"RESEARCH QUESTION: {input.question}"])

        if input.constraints:
            user_parts.extend(["", "KNOWN CONSTRAINTS:"])
            for c in input.constraints:
                user_parts.append(f"  - {c}")

        return AgentContext(
            system_prompt=system,
            messages=[{"role": "user", "content": "\n".join(user_parts)}],
            temperature=self.temperature,
        )

    def parse_response(self, response: str) -> AgentResult:
        """
        Parse LLM response to AgentResult (Either HypothesisOutput or HypothesisError).

        Refactored (Phase D - H14) to use extracted HypothesisResponseParser
        for cleaner separation and better testability.
        """
        # Check for input validation errors
        if hasattr(self, "_input_error") and self._input_error:
            return self._input_error

        # Use extracted parser (Phase D - H14)
        try:
            return parse_hypothesis_response(response)
        except ValueError as e:
            # Parser failed to find valid hypotheses
            return HypothesisError(
                code="INSUFFICIENT_OBSERVATIONS",
                message=str(e),
                recoverable=True,  # Retry might help (temperature/prompt variation)
                context={"response_length": len(response)},
            )

    async def invoke(self, input: HypothesisInput) -> AgentResult:
        """
        LLMAgents require a runtime for execution.

        Use: await runtime.execute(engine, input)
        """
        raise NotImplementedError(
            "HypothesisEngine requires a runtime. Use: await runtime.execute(engine, input)"
        )


# Convenience functions


def hypothesis_engine(
    hypothesis_count: int = 3,
    temperature: float = 0.7,
) -> HypothesisEngine:
    """Create a Hypothesis Engine agent."""
    return HypothesisEngine(
        hypothesis_count=hypothesis_count,
        temperature=temperature,
    )


def rigorous_engine(hypothesis_count: int = 3) -> HypothesisEngine:
    """Create a more rigorous (lower temperature) Hypothesis Engine."""
    return HypothesisEngine(hypothesis_count=hypothesis_count, temperature=0.5)


def exploratory_engine(hypothesis_count: int = 5) -> HypothesisEngine:
    """Create a more exploratory (higher temperature, more hypotheses) engine."""
    return HypothesisEngine(hypothesis_count=hypothesis_count, temperature=0.8)
