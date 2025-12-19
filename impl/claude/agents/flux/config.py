"""
Flux configuration.

FluxConfig controls three key concerns:
1. Entropy (J-gent physics) — bounds computation
2. Backpressure — handles slow consumers
3. Feedback (Ouroboros) — enables recurrence

The configuration is immutable after creation, ensuring consistent
behavior throughout a flux's lifecycle.
"""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class FluxConfig:
    """
    Configuration for FluxAgent behavior.

    Three concerns:
    1. Entropy (J-gent physics) — bounds computation
    2. Backpressure — handles slow consumers
    3. Feedback (Ouroboros) — enables recurrence

    Immutable to prevent mid-execution configuration changes.
    """

    # ─────────────────────────────────────────────────────────────
    # Entropy (J-gent physics)
    # ─────────────────────────────────────────────────────────────

    entropy_budget: float = 1.0
    """
    Initial entropy budget. Flux collapses when exhausted.

    Entropy represents the computational "fuel" available to the flux.
    Each event processed consumes some entropy. When entropy reaches
    zero, the flux transitions to COLLAPSED state.

    Default: 1.0 (can process ~100 events with default decay)
    """

    entropy_decay: float = 0.01
    """
    Entropy consumed per event processed.

    Lower values allow more events before collapse.
    Set to 0.0 for infinite execution (bounded only by max_events).

    Default: 0.01 (100 events before collapse with budget of 1.0)
    """

    max_events: int | None = None
    """
    Hard cap on events. None = unlimited (bounded by entropy).

    When set, the flux will stop after processing this many events,
    regardless of remaining entropy budget.

    Default: None (no hard cap)
    """

    # ─────────────────────────────────────────────────────────────
    # Backpressure
    # ─────────────────────────────────────────────────────────────

    buffer_size: int = 100
    """
    Maximum items in output buffer.

    When the output buffer is full, the drop_policy determines
    what happens to new outputs.

    Default: 100 items
    """

    drop_policy: str = "block"
    """
    How to handle full buffer:
    - "block": Wait for space (preserves all, may stall)
    - "drop_oldest": Discard oldest (real-time priority)
    - "drop_newest": Discard newest (historical priority)

    Default: "block" (no data loss)
    """

    # ─────────────────────────────────────────────────────────────
    # Feedback (Ouroboros)
    # ─────────────────────────────────────────────────────────────

    feedback_fraction: float = 0.0
    """
    Fraction of outputs routed back to input.

    The Ouroboros: Output feeds back to input, creating recurrence.

    Values:
    - 0.0 = pure reactive (no feedback)
    - 0.1-0.3 = light context accumulation
    - 0.5 = equal external/internal influence
    - 1.0 = full ouroboros (solipsism risk!)

    Default: 0.0 (no feedback)
    """

    feedback_transform: Callable[[Any], Any] | None = None
    """
    Transform B → A for feedback.

    Required if output type B is not compatible with input type A.
    If None and feedback_fraction > 0, assumes B can be cast to A.

    Example:
        feedback_transform=lambda result: result.as_context()

    Default: None (identity transform assumed)
    """

    feedback_queue_size: int = 50
    """
    Maximum items in feedback queue.

    Prevents runaway feedback loops from consuming memory.
    When full, new feedback items are dropped.

    Default: 50 items
    """

    # ─────────────────────────────────────────────────────────────
    # Observability
    # ─────────────────────────────────────────────────────────────

    emit_pheromones: bool = True
    """
    Emit stigmergic signals during processing.

    When True, the flux emits pheromone signals that can be
    sensed by other agents or monitoring systems.

    Default: True
    """

    trace_enabled: bool = True
    """
    Enable W-gent tracing.

    When True, flux operations are traced for observability.

    Default: True
    """

    agent_id: str | None = None
    """
    Identifier for observability. Auto-generated if None.

    Used to identify this flux in logs, traces, and pheromone signals.

    Default: None (auto-generated as flux-{uuid})
    """

    # ─────────────────────────────────────────────────────────────
    # Perturbation
    # ─────────────────────────────────────────────────────────────

    perturbation_timeout: float | None = None
    """
    Timeout for perturbation processing in seconds.

    If set, perturbation requests will timeout after this duration.
    None means no timeout (wait indefinitely).

    Default: None (no timeout)
    """

    perturbation_priority: int = 100
    """
    Default priority for perturbations.

    Higher values = processed sooner. Regular events have priority 0.

    Default: 100 (high priority)
    """

    def __post_init__(self) -> None:
        """Validate configuration values."""
        errors: list[str] = []

        if self.entropy_budget <= 0:
            errors.append(f"entropy_budget must be > 0, got {self.entropy_budget}")
        if self.entropy_decay < 0:
            errors.append(f"entropy_decay must be >= 0, got {self.entropy_decay}")
        if self.buffer_size <= 0:
            errors.append(f"buffer_size must be > 0, got {self.buffer_size}")
        if self.drop_policy not in ("block", "drop_oldest", "drop_newest"):
            errors.append(
                f"drop_policy must be block|drop_oldest|drop_newest, got {self.drop_policy}"
            )
        if not 0.0 <= self.feedback_fraction <= 1.0:
            errors.append(f"feedback_fraction must be in [0.0, 1.0], got {self.feedback_fraction}")
        if self.feedback_queue_size <= 0:
            errors.append(f"feedback_queue_size must be > 0, got {self.feedback_queue_size}")
        if self.max_events is not None and self.max_events <= 0:
            errors.append(f"max_events must be > 0 or None, got {self.max_events}")
        if self.perturbation_timeout is not None and self.perturbation_timeout <= 0:
            errors.append(
                f"perturbation_timeout must be > 0 or None, got {self.perturbation_timeout}"
            )

        if errors:
            raise ValueError("; ".join(errors))

    def with_entropy(
        self,
        budget: float | None = None,
        decay: float | None = None,
        max_events: int | None = None,
    ) -> "FluxConfig":
        """Create a new config with modified entropy settings."""
        return FluxConfig(
            entropy_budget=budget if budget is not None else self.entropy_budget,
            entropy_decay=decay if decay is not None else self.entropy_decay,
            max_events=max_events if max_events is not None else self.max_events,
            buffer_size=self.buffer_size,
            drop_policy=self.drop_policy,
            feedback_fraction=self.feedback_fraction,
            feedback_transform=self.feedback_transform,
            feedback_queue_size=self.feedback_queue_size,
            emit_pheromones=self.emit_pheromones,
            trace_enabled=self.trace_enabled,
            agent_id=self.agent_id,
            perturbation_timeout=self.perturbation_timeout,
            perturbation_priority=self.perturbation_priority,
        )

    def with_backpressure(
        self,
        buffer_size: int | None = None,
        drop_policy: str | None = None,
    ) -> "FluxConfig":
        """Create a new config with modified backpressure settings."""
        return FluxConfig(
            entropy_budget=self.entropy_budget,
            entropy_decay=self.entropy_decay,
            max_events=self.max_events,
            buffer_size=buffer_size if buffer_size is not None else self.buffer_size,
            drop_policy=drop_policy if drop_policy is not None else self.drop_policy,
            feedback_fraction=self.feedback_fraction,
            feedback_transform=self.feedback_transform,
            feedback_queue_size=self.feedback_queue_size,
            emit_pheromones=self.emit_pheromones,
            trace_enabled=self.trace_enabled,
            agent_id=self.agent_id,
            perturbation_timeout=self.perturbation_timeout,
            perturbation_priority=self.perturbation_priority,
        )

    def with_feedback(
        self,
        fraction: float | None = None,
        transform: Callable[[Any], Any] | None = None,
        queue_size: int | None = None,
    ) -> "FluxConfig":
        """Create a new config with modified feedback settings."""
        return FluxConfig(
            entropy_budget=self.entropy_budget,
            entropy_decay=self.entropy_decay,
            max_events=self.max_events,
            buffer_size=self.buffer_size,
            drop_policy=self.drop_policy,
            feedback_fraction=fraction if fraction is not None else self.feedback_fraction,
            feedback_transform=transform if transform is not None else self.feedback_transform,
            feedback_queue_size=queue_size if queue_size is not None else self.feedback_queue_size,
            emit_pheromones=self.emit_pheromones,
            trace_enabled=self.trace_enabled,
            agent_id=self.agent_id,
            perturbation_timeout=self.perturbation_timeout,
            perturbation_priority=self.perturbation_priority,
        )

    @classmethod
    def infinite(cls) -> "FluxConfig":
        """Create a config with no entropy limit (runs until source exhausts)."""
        return cls(entropy_budget=float("inf"), entropy_decay=0.0)

    @classmethod
    def bounded(cls, max_events: int) -> "FluxConfig":
        """Create a config that processes exactly max_events events."""
        return cls(max_events=max_events, entropy_budget=float("inf"), entropy_decay=0.0)

    @classmethod
    def ouroboric(cls, feedback_fraction: float = 0.5) -> "FluxConfig":
        """Create a config with ouroboric feedback enabled."""
        return cls(feedback_fraction=feedback_fraction)
