"""
MetabolicEngine: The thermodynamic heart of the system.

Tracks activity-based pressure (not token budget) and triggers
creative "fever" events when the system runs hot.

The Accursed Share: surplus must be spent, not suppressed.

Key Insight: There are TWO distinct pressures:
- Context Pressure (self.stream.pressure): Token accumulation → compression
- Metabolic Pressure (void.entropy.pressure): Activity accumulation → fever

This engine tracks metabolic pressure. Don't confuse it with context pressure.

See: plans/void/entropy.md
"""

from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .fever import FeverEvent, FeverStream

if TYPE_CHECKING:
    from protocols.agentese.contexts.void import EntropyPool

    # Forward declare GlitchController to avoid circular import
    GlitchController = Any


@dataclass
class MetabolicEngine:
    """
    The thermodynamic heart of the system.

    Tracks activity-based pressure (not token budget).
    Triggers fever when surplus accumulates beyond threshold.

    Pressure Dynamics:
    - tick(): Adds pressure based on LLM activity
    - decay: Natural 1% decay per tick
    - fever: Forced discharge at threshold (50% reduction)
    - tithe: Voluntary discharge

    Integration Points:
    - EntropyPool: Draw entropy during fever
    - GlitchController: Trigger visual effects during fever
    """

    # Pressure state
    pressure: float = 0.0
    critical_threshold: float = 1.0
    decay_rate: float = 0.01  # Natural decay per tick

    # Token thermometer (temperature signal)
    input_tokens: int = 0
    output_tokens: int = 0

    # Fever state
    in_fever: bool = False
    fever_start: float | None = None

    # Fever stream for oblique strategies
    _fever_stream: FeverStream = field(default_factory=FeverStream)

    # Integration (injected)
    _entropy_pool: "EntropyPool | None" = field(default=None)
    _glitch_controller: "GlitchController | None" = field(default=None)

    # Random state for fallback entropy
    _random: random.Random = field(default_factory=random.Random)

    @property
    def temperature(self) -> float:
        """
        Token-based temperature.

        High input:output = cold (receiving more than giving)
        Low input:output = hot (giving more than receiving)

        Returns:
            Temperature ratio (0.0-2.0, capped)
        """
        if self.output_tokens == 0:
            return 0.0
        return min(2.0, self.input_tokens / self.output_tokens)

    def tick(self, input_count: int, output_count: int) -> FeverEvent | None:
        """
        Called per LLM invocation (not static resolutions).

        Accumulates pressure based on activity, applies natural decay,
        and checks for fever trigger/recovery.

        Args:
            input_count: Input tokens from this LLM call
            output_count: Output tokens from this LLM call

        Returns:
            FeverEvent if pressure exceeds threshold, None otherwise
        """
        # Track token counts
        self.input_tokens += input_count
        self.output_tokens += output_count

        # Pressure accumulates based on activity
        # Scale: 1000 tokens = 1.0 pressure unit
        activity = (input_count + output_count) * 0.001
        self.pressure += activity

        # Natural decay (prevents infinite accumulation)
        self.pressure *= 1.0 - self.decay_rate

        # Ensure pressure stays non-negative
        self.pressure = max(0.0, self.pressure)

        # Check fever trigger
        if self.pressure > self.critical_threshold and not self.in_fever:
            return self._trigger_fever()

        # Check fever recovery (end fever at 50% of threshold)
        if self.in_fever and self.pressure < self.critical_threshold * 0.5:
            self._end_fever()

        return None

    def _trigger_fever(self) -> FeverEvent:
        """
        Forced creative expenditure.

        Called when pressure exceeds critical threshold.
        Sets fever state, draws from entropy pool, and discharges pressure.

        Returns:
            FeverEvent describing the fever trigger
        """
        self.in_fever = True
        self.fever_start = time.time()

        intensity = self.pressure - self.critical_threshold

        # Draw from entropy pool if available
        seed = self._random.random()
        if self._entropy_pool is not None:
            try:
                grant = self._entropy_pool.sip(min(intensity * 0.5, 1.0))
                seed = grant.get("seed", seed)
            except Exception:
                # BudgetExhaustedError or other - use random seed
                pass

        # Discharge pressure (50% reduction)
        self.pressure *= 0.5

        # Create event
        event = FeverEvent(
            intensity=intensity,
            timestamp=time.time(),
            trigger="pressure_overflow",
            seed=seed,
        )

        # Populate oblique strategy
        self._fever_stream.populate_event(event)

        # Trigger glitch if controller available
        if self._glitch_controller is not None:
            asyncio.create_task(
                self._glitch_controller.trigger_global_glitch(
                    intensity=min(event.intensity * 0.5, 1.0),
                    duration_ms=int(200 + event.intensity * 100),
                    source="fever",
                )
            )

        return event

    def _end_fever(self) -> None:
        """End fever state when pressure drops below 50% of threshold."""
        self.in_fever = False
        self.fever_start = None

    def tithe(self, amount: float = 0.1) -> dict[str, Any]:
        """
        Voluntary pressure discharge.

        The Accursed Share: surplus must be spent.
        Use this to discharge pressure before fever triggers.

        Args:
            amount: Amount of pressure to discharge

        Returns:
            Dict with discharged amount, remaining pressure, and gratitude message
        """
        discharged = min(amount, self.pressure)
        self.pressure = max(0.0, self.pressure - amount)

        # Also tithe to entropy pool if available
        if self._entropy_pool is not None:
            try:
                self._entropy_pool.tithe()
            except Exception:
                pass

        return {
            "discharged": discharged,
            "remaining_pressure": self.pressure,
            "gratitude": "The river flows.",
        }

    def trigger_manual_fever(self) -> FeverEvent | None:
        """
        Manually trigger a fever event.

        Used for testing or intentional creative generation.

        Returns:
            FeverEvent if triggered, None if already in fever
        """
        if self.in_fever:
            return None

        # Temporarily set pressure above threshold
        self.pressure = self.critical_threshold + 0.5

        event = self._trigger_fever()
        event.trigger = "manual"

        return event

    def status(self) -> dict[str, Any]:
        """
        Get current metabolic status.

        Returns:
            Dict with pressure, fever state, temperature, and thresholds
        """
        return {
            "pressure": self.pressure,
            "critical_threshold": self.critical_threshold,
            "in_fever": self.in_fever,
            "fever_start": self.fever_start,
            "temperature": self.temperature,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
        }

    def set_entropy_pool(self, pool: "EntropyPool") -> None:
        """Set the entropy pool for fever entropy draws."""
        self._entropy_pool = pool

    def set_glitch_controller(self, controller: "GlitchController") -> None:
        """Set the glitch controller for TUI integration."""
        self._glitch_controller = controller


# Factory function for creating configured engines
def create_metabolic_engine(
    critical_threshold: float = 1.0,
    decay_rate: float = 0.01,
    entropy_pool: "EntropyPool | None" = None,
    glitch_controller: "GlitchController | None" = None,
) -> MetabolicEngine:
    """
    Create a MetabolicEngine with optional integrations.

    Args:
        critical_threshold: Pressure level that triggers fever (default 1.0)
        decay_rate: Natural pressure decay per tick (default 0.01 = 1%)
        entropy_pool: Optional EntropyPool for fever entropy draws
        glitch_controller: Optional GlitchController for TUI effects

    Returns:
        Configured MetabolicEngine
    """
    return MetabolicEngine(
        critical_threshold=critical_threshold,
        decay_rate=decay_rate,
        _entropy_pool=entropy_pool,
        _glitch_controller=glitch_controller,
    )


# Singleton for global metabolic engine
_global_engine: MetabolicEngine | None = None


def get_metabolic_engine() -> MetabolicEngine:
    """
    Get the global metabolic engine.

    Creates one if it doesn't exist.
    The Accursed Share is a system property, not an agent property.
    """
    global _global_engine
    if _global_engine is None:
        _global_engine = MetabolicEngine()
    return _global_engine


def set_global_engine(engine: MetabolicEngine) -> None:
    """Set the global metabolic engine (for testing)."""
    global _global_engine
    _global_engine = engine
