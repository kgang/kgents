"""
R-gents Refinery - The core optimization engine.

This module implements the RefineryAgent: an endofunctor that transforms
agents into optimized versions via prompt refinement.

Architecture:
  RefineryAgent wraps optimization algorithms (Teleprompters) and
  provides a clean interface for the F-gent -> R-gent -> L-gent pipeline.

Category Theory:
  R: Agent[A, B] -> Agent'[A, B]
  where Loss(Agent') < Loss(Agent)

  R is an endofunctor that preserves morphism types while minimizing loss.

See spec/r-gents/README.md for full specification.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Generic, TypeVar

from .types import (
    Example,
    OptimizationBudget,
    OptimizationDecision,
    OptimizationTrace,
    ROIEstimate,
    Signature,
    TeleprompterStrategy,
    TextualGradient,
)

# Type variables
A = TypeVar("A")
B = TypeVar("B")


# --- Abstract Teleprompter Base ---


class BaseTeleprompter(ABC, Generic[A, B]):
    """
    Abstract base class for teleprompter implementations.

    Teleprompters are optimization algorithms that refine prompts
    by exploring the space of possible instructions and examples.
    """

    @property
    @abstractmethod
    def strategy(self) -> TeleprompterStrategy:
        """The optimization strategy this teleprompter implements."""
        pass

    @abstractmethod
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

        This is the core optimization loop.
        """
        pass

    def _compute_score(
        self,
        predictions: list[Any],
        labels: list[Any],
        metric: Callable[[Any, Any], float],
    ) -> float:
        """Compute average metric score over predictions."""
        if not predictions:
            return 0.0
        scores = [metric(pred, label) for pred, label in zip(predictions, labels)]
        return sum(scores) / len(scores)


# --- BootstrapFewShot Teleprompter ---


class BootstrapFewShotTeleprompter(BaseTeleprompter[A, B]):
    """
    Simplest teleprompter: select best examples as few-shot demos.

    Strategy:
    1. Run agent on training examples
    2. Score each example's output
    3. Select top-K scoring examples as demos
    4. Return signature with optimized demos

    Complexity: O(N) where N = number of examples
    Cost: ~$0.50-1.00 for typical dataset
    """

    def __init__(self, num_demos: int = 4):
        self.num_demos = num_demos

    @property
    def strategy(self) -> TeleprompterStrategy:
        return TeleprompterStrategy.BOOTSTRAP_FEWSHOT

    async def compile(
        self,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
        max_iterations: int = 10,
        budget_usd: float | None = None,
    ) -> OptimizationTrace:
        """Select best examples as few-shot demonstrations."""
        trace = OptimizationTrace(
            initial_prompt=signature.instructions,
            method=self.strategy.value,
        )
        trace.started_at = datetime.now()

        # Score baseline (no demos)
        baseline_score = 0.0  # Placeholder - real impl would run agent
        trace.add_iteration(signature.instructions, baseline_score)

        # Score each example
        scored_examples: list[tuple[Example, float]] = []
        for example in examples:
            # In real impl, we'd run the agent and score its output
            # For now, we assume examples have pre-computed scores
            score = example.metadata.get("score", 0.5)
            scored_examples.append((example, score))

        # Sort by score (descending) and take top-K
        scored_examples.sort(key=lambda x: x[1], reverse=True)
        best_examples = scored_examples[: self.num_demos]

        # Build demo tuples
        demos = tuple(
            {"inputs": ex.inputs, "outputs": ex.outputs} for ex, _ in best_examples
        )

        # Create optimized signature
        final_score = (
            sum(s for _, s in best_examples) / len(best_examples)
            if best_examples
            else 0.0
        )
        trace.add_iteration(signature.instructions, final_score)

        # Record final state
        trace.final_prompt = signature.instructions  # Same instructions, better demos
        trace.converged = True
        trace.convergence_reason = f"Selected top {len(demos)} demos"
        trace.completed_at = datetime.now()
        trace.total_examples = len(examples)

        return trace


# --- TextGrad Teleprompter ---


class TextGradTeleprompter(BaseTeleprompter[A, B]):
    """
    TextGrad: Gradient descent in prompt space using textual feedback.

    Strategy:
    1. Evaluate current prompt on examples
    2. For failures, generate textual gradients (critique)
    3. Aggregate gradients into update direction
    4. Apply textual gradient to prompt
    5. Repeat until convergence

    Complexity: O(N^2) - N iterations, N examples each
    Cost: ~$5-15 depending on dataset size
    """

    def __init__(
        self,
        learning_rate: float = 1.0,
        convergence_threshold: float = 0.01,
    ):
        self.learning_rate = learning_rate
        self.convergence_threshold = convergence_threshold

    @property
    def strategy(self) -> TeleprompterStrategy:
        return TeleprompterStrategy.TEXTGRAD

    async def compile(
        self,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
        max_iterations: int = 10,
        budget_usd: float | None = None,
    ) -> OptimizationTrace:
        """Optimize via textual gradient descent."""
        trace = OptimizationTrace(
            initial_prompt=signature.instructions,
            method=self.strategy.value,
        )
        trace.started_at = datetime.now()

        current_prompt = signature.instructions
        prev_score = 0.0

        for iteration in range(max_iterations):
            # 1. Evaluate current prompt (placeholder)
            current_score = self._evaluate_prompt(current_prompt, examples, metric)
            trace.add_iteration(current_prompt, current_score)

            # 2. Check convergence
            if abs(current_score - prev_score) < self.convergence_threshold:
                trace.converged = True
                trace.convergence_reason = (
                    f"Score change {abs(current_score - prev_score):.4f} "
                    f"< threshold {self.convergence_threshold}"
                )
                break

            # 3. Compute textual gradients (placeholder for LLM call)
            gradients = self._compute_gradients(current_prompt, examples, metric)

            # 4. Apply gradient update (placeholder for LLM call)
            current_prompt = await self._apply_gradients(current_prompt, gradients)
            prev_score = current_score

        trace.final_prompt = current_prompt
        trace.completed_at = datetime.now()
        trace.total_examples = len(examples)

        return trace

    def _evaluate_prompt(
        self,
        prompt: str,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
    ) -> float:
        """Evaluate prompt on examples. Placeholder - real impl uses LLM."""
        # This would run the agent with the prompt and score outputs
        return 0.5  # Placeholder

    def _compute_gradients(
        self,
        prompt: str,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
    ) -> list[TextualGradient]:
        """Compute textual gradients for failed examples. Placeholder."""
        # Real implementation:
        # 1. Run agent on each example
        # 2. For failures, ask LLM to critique the output
        # 3. Return list of TextualGradient objects
        return []

    async def _apply_gradients(
        self,
        prompt: str,
        gradients: list[TextualGradient],
    ) -> str:
        """Apply textual gradients to prompt. Placeholder."""
        # Real implementation:
        # Ask LLM: "Given this prompt and these critiques, generate improved prompt"
        return prompt


# --- MIPROv2 Teleprompter (Stub) ---


class MIPROv2Teleprompter(BaseTeleprompter[A, B]):
    """
    MIPROv2: Multi-stage Instruction Proposal and Refinement.

    Bayesian optimization over instructions and examples.
    Most sophisticated teleprompter, best quality.

    Strategy:
    1. Generate candidate instructions via LLM
    2. Use Bayesian surrogate to select promising candidates
    3. Evaluate on subset of examples
    4. Update surrogate model
    5. Repeat until budget exhausted

    Complexity: O(N) iterations with smart sampling
    Cost: ~$5-20 depending on configuration

    NOTE: Full implementation requires DSPy backend.
    This is a stub for the interface.
    """

    @property
    def strategy(self) -> TeleprompterStrategy:
        return TeleprompterStrategy.MIPRO_V2

    async def compile(
        self,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
        max_iterations: int = 10,
        budget_usd: float | None = None,
    ) -> OptimizationTrace:
        """Optimize via Bayesian instruction refinement."""
        # Stub - real implementation uses DSPy MIPROv2
        trace = OptimizationTrace(
            initial_prompt=signature.instructions,
            method=self.strategy.value,
        )
        trace.started_at = datetime.now()
        trace.add_iteration(signature.instructions, 0.5)
        trace.final_prompt = signature.instructions
        trace.converged = False
        trace.convergence_reason = "MIPROv2 requires DSPy backend (not yet integrated)"
        trace.completed_at = datetime.now()
        return trace


# --- OPRO Teleprompter (Stub) ---


class OPROTeleprompter(BaseTeleprompter[A, B]):
    """
    OPRO: Optimization by PROmpting.

    Uses a meta-prompt to ask the LLM to propose better prompts.

    Strategy:
    1. Show LLM the current prompt and its score
    2. Ask LLM to propose an improved prompt
    3. Evaluate new prompt
    4. Repeat, keeping track of best-so-far

    Complexity: O(N) iterations
    Cost: ~$2-5, efficient exploration

    NOTE: Full implementation requires LLM backend.
    This is a stub for the interface.
    """

    @property
    def strategy(self) -> TeleprompterStrategy:
        return TeleprompterStrategy.OPRO

    async def compile(
        self,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
        max_iterations: int = 10,
        budget_usd: float | None = None,
    ) -> OptimizationTrace:
        """Optimize via meta-prompt optimization."""
        # Stub - real implementation uses LLM to propose prompts
        trace = OptimizationTrace(
            initial_prompt=signature.instructions,
            method=self.strategy.value,
        )
        trace.started_at = datetime.now()
        trace.add_iteration(signature.instructions, 0.5)
        trace.final_prompt = signature.instructions
        trace.converged = False
        trace.convergence_reason = "OPRO requires LLM backend (not yet integrated)"
        trace.completed_at = datetime.now()
        return trace


# --- Teleprompter Factory ---


class TeleprompterFactory:
    """Factory for creating teleprompter instances."""

    _registry: dict[TeleprompterStrategy, type[BaseTeleprompter[Any, Any]]] = {
        TeleprompterStrategy.BOOTSTRAP_FEWSHOT: BootstrapFewShotTeleprompter,
        TeleprompterStrategy.TEXTGRAD: TextGradTeleprompter,
        TeleprompterStrategy.MIPRO_V2: MIPROv2Teleprompter,
        TeleprompterStrategy.OPRO: OPROTeleprompter,
    }

    @classmethod
    def get(cls, strategy: TeleprompterStrategy | str) -> BaseTeleprompter[Any, Any]:
        """Get a teleprompter instance by strategy."""
        if isinstance(strategy, str):
            strategy = TeleprompterStrategy(strategy)

        teleprompter_cls = cls._registry.get(strategy)
        if teleprompter_cls is None:
            raise ValueError(f"Unknown teleprompter strategy: {strategy}")

        return teleprompter_cls()

    @classmethod
    def register(
        cls,
        strategy: TeleprompterStrategy,
        teleprompter_cls: type[BaseTeleprompter[Any, Any]],
    ) -> None:
        """Register a custom teleprompter implementation."""
        cls._registry[strategy] = teleprompter_cls


# --- ROI Optimizer (B-gent Integration) ---


class ROIOptimizer:
    """
    Ensures optimization cost doesn't exceed agent value.

    Integrates with B-gent economic constraints.
    """

    def __init__(
        self,
        default_value_per_call: float = 0.10,
        default_improvement_estimate: float = 0.20,
    ):
        self.default_value_per_call = default_value_per_call
        self.default_improvement_estimate = default_improvement_estimate

    def estimate_cost(
        self,
        strategy: TeleprompterStrategy,
        num_examples: int,
    ) -> float:
        """Estimate optimization cost in USD."""
        # Cost estimates per strategy
        cost_map = {
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT: 0.50,
            TeleprompterStrategy.BOOTSTRAP_FEWSHOT_RANDOM: 1.00,
            TeleprompterStrategy.MIPRO_V2: 5.00 + num_examples * 0.05,
            TeleprompterStrategy.TEXTGRAD: 5.00 + num_examples * 0.10,
            TeleprompterStrategy.OPRO: 2.00 + num_examples * 0.02,
            TeleprompterStrategy.BOOTSTRAP_FINETUNE: 50.00 + num_examples * 0.01,
        }
        return cost_map.get(strategy, 5.00)

    def should_optimize(
        self,
        usage_per_month: int,
        current_performance: float,
        strategy: TeleprompterStrategy,
        num_examples: int,
        value_per_call: float | None = None,
        expected_improvement: float | None = None,
    ) -> OptimizationDecision:
        """
        Decide whether to proceed with optimization.

        Uses ROI analysis to ensure economic viability.
        """
        value_per_call = value_per_call or self.default_value_per_call
        expected_improvement = expected_improvement or self.default_improvement_estimate

        # Estimate ROI
        cost = self.estimate_cost(strategy, num_examples)
        roi_estimate = ROIEstimate(
            expected_improvement=expected_improvement,
            estimated_cost_usd=cost,
            projected_calls_per_month=usage_per_month,
            value_per_call_usd=value_per_call,
        )

        # Decision logic
        if not roi_estimate.is_positive:
            return OptimizationDecision(
                proceed=False,
                reason=f"Negative ROI: projected value ${roi_estimate.projected_value:.2f} "
                f"< cost ${cost:.2f}",
                roi_estimate=roi_estimate,
            )

        # Recommend cheaper method if ROI is marginal
        if roi_estimate.roi < 2.0 and strategy in (
            TeleprompterStrategy.MIPRO_V2,
            TeleprompterStrategy.TEXTGRAD,
        ):
            return OptimizationDecision(
                proceed=True,
                reason=f"Marginal ROI ({roi_estimate.roi:.2f}x), recommending cheaper method",
                recommended_method=TeleprompterStrategy.BOOTSTRAP_FEWSHOT,
                budget=OptimizationBudget(
                    max_cost_usd=min(cost, 2.0),
                    max_iterations=5,
                ),
                roi_estimate=roi_estimate,
            )

        return OptimizationDecision(
            proceed=True,
            reason=f"Positive ROI ({roi_estimate.roi:.2f}x)",
            recommended_method=strategy,
            budget=OptimizationBudget(
                max_cost_usd=min(roi_estimate.projected_value * 0.5, 20.0),
                max_iterations=50,
            ),
            roi_estimate=roi_estimate,
        )


# --- RefineryAgent: The Main Interface ---


@dataclass
class RefineryAgent(Generic[A, B]):
    """
    The R-gent: Optimizes other agents via prompt refinement.

    This is an endofunctor R: Agent[A,B] -> Agent'[A,B] that:
    - Preserves the morphism type signature
    - Minimizes loss via systematic optimization
    - Respects economic constraints (B-gent integration)

    Usage:
        refinery = RefineryAgent(strategy="mipro_v2")
        trace = await refinery.refine(signature, examples, metric)
    """

    strategy: TeleprompterStrategy = TeleprompterStrategy.BOOTSTRAP_FEWSHOT
    roi_optimizer: ROIOptimizer | None = None

    def __post_init__(self) -> None:
        if self.roi_optimizer is None:
            self.roi_optimizer = ROIOptimizer()

    async def refine(
        self,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
        max_iterations: int = 10,
        budget_usd: float | None = None,
        check_roi: bool = True,
        usage_per_month: int = 100,
    ) -> OptimizationTrace:
        """
        Optimize a signature using training examples.

        Args:
            signature: The task specification to optimize
            examples: Training data (input-output pairs)
            metric: Scoring function(prediction, label) -> float
            max_iterations: Maximum optimization steps
            budget_usd: Optional cost limit
            check_roi: Whether to check ROI before optimization
            usage_per_month: Expected monthly usage (for ROI)

        Returns:
            OptimizationTrace with full history and results

        Raises:
            ValueError: If ROI check fails and check_roi=True
        """
        # ROI check (B-gent integration)
        if check_roi and self.roi_optimizer:
            decision = self.roi_optimizer.should_optimize(
                usage_per_month=usage_per_month,
                current_performance=0.5,  # Assume 50% baseline
                strategy=self.strategy,
                num_examples=len(examples),
            )

            if not decision.proceed:
                # Return early with explanation
                trace = OptimizationTrace(
                    initial_prompt=signature.instructions,
                    method="skipped",
                )
                trace.converged = False
                trace.convergence_reason = f"Optimization skipped: {decision.reason}"
                return trace

            # Use recommended method if different
            if (
                decision.recommended_method
                and decision.recommended_method != self.strategy
            ):
                self.strategy = decision.recommended_method

            # Apply budget constraints
            if decision.budget:
                budget_usd = (
                    min(budget_usd, decision.budget.max_cost_usd)
                    if budget_usd
                    else decision.budget.max_cost_usd
                )
                max_iterations = min(max_iterations, decision.budget.max_iterations)

        # Get teleprompter and run optimization
        teleprompter = TeleprompterFactory.get(self.strategy)
        trace = await teleprompter.compile(
            signature=signature,
            examples=examples,
            metric=metric,
            max_iterations=max_iterations,
            budget_usd=budget_usd,
        )

        return trace

    def select_strategy(
        self,
        task_complexity: str,
        dataset_size: int,
        budget_usd: float,
    ) -> TeleprompterStrategy:
        """
        Heuristic teleprompter selection.

        Based on task complexity, dataset size, and budget.
        """
        if task_complexity == "simple" and dataset_size < 20:
            return TeleprompterStrategy.BOOTSTRAP_FEWSHOT

        if task_complexity == "simple":
            return TeleprompterStrategy.BOOTSTRAP_FEWSHOT_RANDOM

        if budget_usd < 5.0:
            return TeleprompterStrategy.OPRO

        if task_complexity == "complex":
            return TeleprompterStrategy.MIPRO_V2

        if dataset_size > 100 and budget_usd > 50:
            return TeleprompterStrategy.BOOTSTRAP_FINETUNE

        return TeleprompterStrategy.MIPRO_V2
