"""
Zero Seed LLM Budgets: Thermodynamic constraints for LLM operations.

Token budgets are the thermodynamic currency of LLM operations.
Spending 10x tokens to achieve 2x loss reduction is often worth it -
the human time saved in fixing semantic drift far exceeds API cost.

Three budget types:
- TokenBudget: Raw token consumption limits
- LatencyBudget: Interactive UX thresholds
- QualityBudget: Model selection by loss tolerance

See: spec/protocols/zero-seed1/llm.md Section 3
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------


class TokenBudgetExceeded(Exception):
    """Raised when token budget is exhausted."""

    def __init__(self, message: str, budget: TokenBudget):
        super().__init__(message)
        self.budget = budget


# -----------------------------------------------------------------------------
# Token Budget
# -----------------------------------------------------------------------------


@dataclass
class TokenBudget:
    """Energy budget for LLM operations.

    Philosophy: Tokens are the thermodynamic currency. Spending 10x tokens
    to achieve 2x loss reduction is often worth it - the human time saved
    in fixing semantic drift far exceeds API cost.

    The 10x Principle:
        Iterative refinement with liberal token budgets outperforms
        single-shot generation by 10x in semantic preservation.

    Attributes:
        max_input_per_call: Maximum input tokens per API call
        max_output_per_call: Maximum output tokens per API call
        max_session_cumulative: Hard stop for runaway loops
        cumulative_input: Running total of input tokens used
        cumulative_output: Running total of output tokens used
    """

    max_input_per_call: int = 100_000  # Claude context window
    max_output_per_call: int = 10_000  # Reasonable completion size
    max_session_cumulative: int = 1_000_000  # Hard stop

    cumulative_input: int = field(default=0, repr=False)
    cumulative_output: int = field(default=0, repr=False)

    def can_afford(self, estimated_input: int, estimated_output: int) -> bool:
        """Check if we have budget remaining.

        Args:
            estimated_input: Expected input tokens for next call
            estimated_output: Expected output tokens for next call

        Returns:
            True if operation would stay within budget
        """
        total_estimated = (
            self.cumulative_input
            + estimated_input
            + self.cumulative_output
            + estimated_output
        )
        return total_estimated < self.max_session_cumulative

    def check_and_reserve(
        self, estimated_input: int, estimated_output: int
    ) -> None:
        """Check budget and raise if insufficient.

        Args:
            estimated_input: Expected input tokens
            estimated_output: Expected output tokens

        Raises:
            TokenBudgetExceeded: If budget would be exceeded
        """
        if not self.can_afford(estimated_input, estimated_output):
            raise TokenBudgetExceeded(
                f"Token budget exceeded. Cumulative: {self.cumulative_input + self.cumulative_output}, "
                f"Requested: {estimated_input + estimated_output}, "
                f"Max: {self.max_session_cumulative}",
                budget=self,
            )

    def charge(self, actual_input: int, actual_output: int) -> None:
        """Deduct tokens after call.

        Args:
            actual_input: Actual input tokens used
            actual_output: Actual output tokens used
        """
        self.cumulative_input += actual_input
        self.cumulative_output += actual_output

    @property
    def remaining(self) -> int:
        """Remaining budget tokens."""
        return max(
            0,
            self.max_session_cumulative
            - self.cumulative_input
            - self.cumulative_output,
        )

    @property
    def usage_fraction(self) -> float:
        """Fraction of budget used (0.0 to 1.0)."""
        if self.max_session_cumulative == 0:
            return 1.0
        used = self.cumulative_input + self.cumulative_output
        return min(1.0, used / self.max_session_cumulative)

    def session_cost_usd(self) -> float:
        """Estimate cost at current pricing (as of 2025-01).

        Claude Sonnet 4.5 pricing:
            Input: $3 / 1M tokens
            Output: $15 / 1M tokens
        """
        input_cost = (self.cumulative_input / 1_000_000) * 3.0
        output_cost = (self.cumulative_output / 1_000_000) * 15.0
        return input_cost + output_cost

    def to_dict(self) -> dict[str, Any]:
        """Serialize budget state."""
        return {
            "max_input_per_call": self.max_input_per_call,
            "max_output_per_call": self.max_output_per_call,
            "max_session_cumulative": self.max_session_cumulative,
            "cumulative_input": self.cumulative_input,
            "cumulative_output": self.cumulative_output,
            "remaining": self.remaining,
            "usage_fraction": self.usage_fraction,
            "cost_usd": self.session_cost_usd(),
        }


# -----------------------------------------------------------------------------
# Latency Budget
# -----------------------------------------------------------------------------


@dataclass
class LatencyBudget:
    """Time budget for LLM operations.

    Philosophy:
        - 3s is the threshold for "feels instant"
        - 10s is acceptable for complex operations
        - 30s requires progress indication

    Used to select UX patterns based on expected operation time.
    """

    interactive_threshold: float = 3.0  # Must respond within 3s
    acceptable_threshold: float = 10.0  # Can take up to 10s
    progress_threshold: float = 30.0  # Show progress bar beyond 30s
    timeout: float = 60.0  # Hard timeout

    def select_strategy(self, estimated_time: float) -> str:
        """Choose UX pattern based on expected latency.

        Args:
            estimated_time: Expected operation time in seconds

        Returns:
            Strategy name: "synchronous", "spinner", "progress", or "background"
        """
        if estimated_time < self.interactive_threshold:
            return "synchronous"  # Inline, no spinner
        elif estimated_time < self.acceptable_threshold:
            return "spinner"  # Show spinner, block UI
        elif estimated_time < self.progress_threshold:
            return "progress"  # Show progress bar
        else:
            return "background"  # Run in background, notify when done

    def estimate_time(self, token_count: int, model_tier: str = "sonnet") -> float:
        """Estimate operation time from token count.

        Based on empirical measurements:
            - Opus: ~8s per 1K tokens
            - Sonnet: ~3s per 1K tokens
            - Haiku: ~1s per 1K tokens

        Args:
            token_count: Expected output tokens
            model_tier: "opus", "sonnet", or "haiku"

        Returns:
            Estimated time in seconds
        """
        tokens_per_second = {
            "opus": 125,  # ~1K tokens in 8s
            "sonnet": 333,  # ~1K tokens in 3s
            "haiku": 1000,  # ~1K tokens in 1s
        }

        tps = tokens_per_second.get(model_tier, 333)
        return token_count / tps


# -----------------------------------------------------------------------------
# Quality Budget
# -----------------------------------------------------------------------------


@dataclass
class QualityBudget:
    """Loss tolerance to model selection mapping.

    Philosophy: Use the fastest model that meets quality requirements.
    Don't use opus for tasks where haiku suffices.

    Model characteristics:
        - Opus: < 5% loss, ~8s/1K tokens, expensive
        - Sonnet: < 15% loss, ~3s/1K tokens, balanced
        - Haiku: < 30% loss, ~1s/1K tokens, fast

    Usage:
        budget = QualityBudget()
        model = budget.select_model("restructure", max_loss=0.05)
        # Returns "claude-opus-4-5-20251101" for axiom mining
    """

    # Model specifications with loss tolerances
    MODELS: dict[str, dict[str, Any]] = field(default_factory=lambda: {
        "opus": {
            "name": "claude-opus-4-5-20251101",
            "loss_tolerance": 0.05,  # < 5% loss
            "latency_estimate": 8.0,  # seconds per 1K tokens
            "cost_per_1M_input": 15.0,
            "cost_per_1M_output": 75.0,
        },
        "sonnet": {
            "name": "claude-sonnet-4-20250514",
            "loss_tolerance": 0.15,  # < 15% loss
            "latency_estimate": 3.0,
            "cost_per_1M_input": 3.0,
            "cost_per_1M_output": 15.0,
        },
        "haiku": {
            "name": "claude-3-5-haiku-20241022",
            "loss_tolerance": 0.30,  # < 30% loss
            "latency_estimate": 1.0,
            "cost_per_1M_input": 1.0,
            "cost_per_1M_output": 5.0,
        },
    })

    def select_model(self, task: str, max_loss: float) -> str:
        """Select cheapest model that meets loss tolerance.

        Args:
            task: Task name (for logging/debugging)
            max_loss: Maximum acceptable Galois loss

        Returns:
            Model name string for API calls

        Examples:
            - Axiom mining (max_loss=0.05) -> opus
            - Proof validation (max_loss=0.10) -> sonnet
            - Quick loss check (max_loss=0.30) -> haiku
        """
        # Check models from cheapest to most expensive
        for model_id in ["haiku", "sonnet", "opus"]:
            model = self.MODELS[model_id]
            if model["loss_tolerance"] >= max_loss:
                return model["name"]

        # Fallback: use opus if even haiku doesn't meet tolerance
        return self.MODELS["opus"]["name"]

    def get_model_tier(self, model_name: str) -> str:
        """Get tier name from model name.

        Args:
            model_name: Full model name

        Returns:
            Tier: "opus", "sonnet", or "haiku"
        """
        for tier, config in self.MODELS.items():
            if config["name"] == model_name:
                return tier
        return "sonnet"  # Default

    def estimate_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Estimate cost for an operation.

        Args:
            model: Model name or tier
            input_tokens: Expected input tokens
            output_tokens: Expected output tokens

        Returns:
            Estimated cost in USD
        """
        tier = self.get_model_tier(model) if "/" in model else model
        if tier not in self.MODELS:
            tier = "sonnet"

        config = self.MODELS[tier]
        input_cost = (input_tokens / 1_000_000) * config["cost_per_1M_input"]
        output_cost = (output_tokens / 1_000_000) * config["cost_per_1M_output"]
        return input_cost + output_cost


# -----------------------------------------------------------------------------
# Unified Budget Manager
# -----------------------------------------------------------------------------


@dataclass
class BudgetManager:
    """Unified budget management for LLM operations.

    Coordinates token, latency, and quality budgets.
    Provides single interface for operation planning.
    """

    token: TokenBudget = field(default_factory=TokenBudget)
    latency: LatencyBudget = field(default_factory=LatencyBudget)
    quality: QualityBudget = field(default_factory=QualityBudget)

    def plan_operation(
        self,
        task: str,
        estimated_input: int,
        estimated_output: int,
        max_loss: float = 0.15,
    ) -> dict[str, Any]:
        """Plan an LLM operation with budget constraints.

        Args:
            task: Task description
            estimated_input: Expected input tokens
            estimated_output: Expected output tokens
            max_loss: Maximum acceptable Galois loss

        Returns:
            Operation plan with model, strategy, and cost estimate

        Raises:
            TokenBudgetExceeded: If token budget insufficient
        """
        # Check token budget
        self.token.check_and_reserve(estimated_input, estimated_output)

        # Select model based on quality requirements
        model = self.quality.select_model(task, max_loss)
        model_tier = self.quality.get_model_tier(model)

        # Estimate latency
        estimated_time = self.latency.estimate_time(estimated_output, model_tier)
        strategy = self.latency.select_strategy(estimated_time)

        # Estimate cost
        cost = self.quality.estimate_cost(model, estimated_input, estimated_output)

        return {
            "task": task,
            "model": model,
            "model_tier": model_tier,
            "estimated_input": estimated_input,
            "estimated_output": estimated_output,
            "estimated_time": estimated_time,
            "strategy": strategy,
            "estimated_cost_usd": cost,
            "remaining_budget": self.token.remaining,
        }

    def record_usage(self, actual_input: int, actual_output: int) -> None:
        """Record actual token usage after operation.

        Args:
            actual_input: Actual input tokens used
            actual_output: Actual output tokens used
        """
        self.token.charge(actual_input, actual_output)

    def summary(self) -> dict[str, Any]:
        """Get budget summary."""
        return {
            "token": self.token.to_dict(),
            "session_cost_usd": self.token.session_cost_usd(),
        }


__all__ = [
    "TokenBudget",
    "TokenBudgetExceeded",
    "LatencyBudget",
    "QualityBudget",
    "BudgetManager",
]
