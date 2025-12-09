"""
R-gents Types - Foundation types for the Refinery.

This module defines core abstractions for prompt optimization:
- Signature: Declarative task specification (inputs/outputs + instructions)
- Teleprompter: Protocol for optimization algorithms
- OptimizationTrace: History of optimization iterations
- TextualGradient: Natural language feedback as gradient vector

The R-gent treats prompt engineering as formal optimization,
implementing an endofunctor R: Agent[A,B] -> Agent'[A,B] where
Loss(Agent') < Loss(Agent).

See spec/r-gents/README.md for full specification.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Any,
    Callable,
    Protocol,
    TypeVar,
)

# Type variables
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type


# --- Signature: Declarative Task Specification ---


@dataclass(frozen=True)
class FieldSpec:
    """Specification for a single input or output field."""

    name: str
    field_type: type
    description: str = ""
    required: bool = True
    default: Any = None


@dataclass(frozen=True)
class Signature:
    """
    Declarative task specification (DSPy-style).

    A Signature is the type signature of an agent morphism enriched
    with semantic intent. It declares:
    - What inputs the agent expects
    - What outputs it produces
    - High-level instructions describing the task

    Category Theory:
      A Signature is the enriched hom-object Hom_C(A, B) where
      the enrichment carries semantic metadata.
    """

    # Named typed inputs
    input_fields: tuple[FieldSpec, ...]

    # Named typed outputs
    output_fields: tuple[FieldSpec, ...]

    # High-level task description
    instructions: str

    # Optional: few-shot examples (will be optimized by R-gent)
    demos: tuple[dict[str, Any], ...] = ()

    # Optional: version for tracking optimization
    version: str = "1.0.0"

    # Metadata
    name: str = ""
    description: str = ""

    @classmethod
    def simple(
        cls,
        input_name: str,
        input_type: type,
        output_name: str,
        output_type: type,
        instructions: str,
    ) -> Signature:
        """Factory for simple single-input, single-output signatures."""
        return cls(
            input_fields=(FieldSpec(name=input_name, field_type=input_type),),
            output_fields=(FieldSpec(name=output_name, field_type=output_type),),
            instructions=instructions,
        )

    @property
    def input_names(self) -> tuple[str, ...]:
        """Names of all input fields."""
        return tuple(f.name for f in self.input_fields)

    @property
    def output_names(self) -> tuple[str, ...]:
        """Names of all output fields."""
        return tuple(f.name for f in self.output_fields)


# --- Example: Training Data Unit ---


@dataclass(frozen=True)
class Example:
    """
    A single training example for optimization.

    Contains input-output pairs for supervised optimization.
    """

    inputs: dict[str, Any]
    outputs: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def simple(cls, input_value: Any, output_value: Any) -> Example:
        """Factory for simple single-field examples."""
        return cls(inputs={"input": input_value}, outputs={"output": output_value})


# --- Textual Gradient: NL Feedback as Gradient ---


@dataclass(frozen=True)
class TextualGradient:
    """
    Natural language feedback acting as a gradient vector.

    The core insight of TextGrad: criticism points toward improvement.

    Formula:
      Prompt_{t+1} = Prompt_t - alpha * gradient_text(Error)

    Category Theory:
      A morphism in the tangent category T(Prompt) pointing
      toward the optimum.
    """

    # The critique/feedback text
    feedback: str

    # Which example triggered this gradient
    source_example: Example | None = None

    # Severity/magnitude (0.0 to 1.0)
    magnitude: float = 1.0

    # Which aspect to improve
    aspect: str = "general"  # "accuracy", "style", "format", etc.


# --- Optimization Iteration: Single Step Record ---


@dataclass(frozen=True)
class OptimizationIteration:
    """Record of a single optimization iteration."""

    iteration: int
    prompt_hash: str
    score: float
    timestamp: datetime = field(default_factory=datetime.now)

    # Optional details
    prompt_text: str = ""
    gradients: tuple[TextualGradient, ...] = ()
    examples_evaluated: int = 0


# --- Optimization Trace: Full History ---


@dataclass
class OptimizationTrace:
    """
    Complete history of an optimization run.

    Records the journey from initial prompt to optimized prompt,
    including all iterations, scores, and convergence info.
    """

    # The starting prompt
    initial_prompt: str

    # Method used
    method: str = "unknown"

    # Iteration history
    iterations: list[OptimizationIteration] = field(default_factory=list)

    # Final state
    final_prompt: str = ""
    converged: bool = False
    convergence_reason: str = ""

    # Economics
    cost_usd: float = 0.0
    total_examples: int = 0
    total_llm_calls: int = 0

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def add_iteration(
        self,
        prompt: str,
        score: float,
        gradients: tuple[TextualGradient, ...] = (),
    ) -> None:
        """Record a new iteration."""
        import hashlib

        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:8]

        self.iterations.append(
            OptimizationIteration(
                iteration=len(self.iterations) + 1,
                prompt_hash=prompt_hash,
                score=score,
                prompt_text=prompt,
                gradients=gradients,
            )
        )

    @property
    def baseline_score(self) -> float | None:
        """Score of the initial prompt."""
        return self.iterations[0].score if self.iterations else None

    @property
    def final_score(self) -> float | None:
        """Score of the final prompt."""
        return self.iterations[-1].score if self.iterations else None

    @property
    def improvement(self) -> float | None:
        """Absolute improvement from baseline to final."""
        if self.baseline_score is not None and self.final_score is not None:
            return self.final_score - self.baseline_score
        return None

    @property
    def improvement_percentage(self) -> float | None:
        """Relative improvement as percentage."""
        if (
            self.baseline_score is not None
            and self.final_score is not None
            and self.baseline_score != 0
        ):
            return (
                (self.final_score - self.baseline_score) / abs(self.baseline_score)
            ) * 100
        return None

    @property
    def duration_seconds(self) -> float | None:
        """Total optimization duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


# --- Teleprompter Strategy Enum ---


class TeleprompterStrategy(Enum):
    """
    Available optimization strategies.

    Ordered by complexity/cost: O(1) to O(N*M).
    """

    # Simple: Select best examples from history
    BOOTSTRAP_FEWSHOT = "bootstrap_fewshot"

    # Medium: Few-shot + random search
    BOOTSTRAP_FEWSHOT_RANDOM = "bootstrap_fewshot_random"

    # Complex: Bayesian optimization over instructions + examples
    MIPRO_V2 = "mipro_v2"

    # High precision: Iterative editing using criticism as gradient
    TEXTGRAD = "textgrad"

    # Exploration: Meta-prompt asks LLM to propose better prompts
    OPRO = "opro"

    # Production: Fine-tuning
    BOOTSTRAP_FINETUNE = "bootstrap_finetune"


# --- Teleprompter Protocol ---


class Teleprompter(Protocol[A, B]):
    """
    Protocol for prompt optimization algorithms.

    A Teleprompter is a natural transformation:
      eta: Agent => Agent'

    It transforms an agent into an optimized version while
    preserving the morphism type signature.
    """

    @property
    def strategy(self) -> TeleprompterStrategy:
        """The optimization strategy this teleprompter implements."""
        ...

    async def compile(
        self,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
        max_iterations: int = 10,
        budget_usd: float | None = None,
    ) -> OptimizationTrace:
        """
        Optimize a signature using training examples.

        Args:
            signature: The task specification to optimize
            examples: Training data (input-output pairs)
            metric: Scoring function(prediction, label) -> float
            max_iterations: Maximum optimization steps
            budget_usd: Optional cost limit

        Returns:
            OptimizationTrace with full history and optimized signature
        """
        ...


# --- Optimized Agent Wrapper ---


@dataclass
class OptimizedAgentMeta:
    """Metadata for an optimized agent."""

    # Original signature
    original_signature: Signature

    # Optimized signature (with refined instructions/demos)
    optimized_signature: Signature

    # Optimization details
    trace: OptimizationTrace

    # Performance metrics
    baseline_score: float
    final_score: float
    improvement: float

    # Economics
    optimization_cost_usd: float

    # Provenance
    optimized_at: datetime = field(default_factory=datetime.now)
    optimizer_version: str = "1.0.0"


# --- Budget/ROI Types (B-gent integration) ---


@dataclass(frozen=True)
class OptimizationBudget:
    """Budget constraints for optimization (from B-gent)."""

    max_cost_usd: float
    max_iterations: int
    max_duration_seconds: float = 3600.0  # 1 hour default
    min_improvement_threshold: float = 0.05  # 5% minimum improvement


@dataclass(frozen=True)
class ROIEstimate:
    """Estimated return on investment for optimization."""

    # Expected improvement
    expected_improvement: float

    # Cost estimate
    estimated_cost_usd: float

    # Usage projection
    projected_calls_per_month: int
    value_per_call_usd: float

    # ROI calculation
    @property
    def projected_value(self) -> float:
        """Total projected value of improvement."""
        return (
            self.projected_calls_per_month
            * self.value_per_call_usd
            * self.expected_improvement
        )

    @property
    def roi(self) -> float:
        """Return on investment ratio."""
        if self.estimated_cost_usd == 0:
            return float("inf") if self.projected_value > 0 else 0
        return self.projected_value / self.estimated_cost_usd

    @property
    def is_positive(self) -> bool:
        """Whether optimization has positive ROI."""
        return self.roi > 1.0


@dataclass(frozen=True)
class OptimizationDecision:
    """Decision on whether to proceed with optimization."""

    proceed: bool
    reason: str
    recommended_method: TeleprompterStrategy | None = None
    budget: OptimizationBudget | None = None
    roi_estimate: ROIEstimate | None = None
