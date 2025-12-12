"""
FluxMetabolism: Bridge between Flux and Metabolic Engine.

Wires the Metabolic Engine (void.entropy.*) to FluxAgent, enabling:
- Metabolic pressure accumulation during event processing
- Fever triggers when pressure exceeds threshold
- Automatic entropy consumption from the Accursed Share

The Accursed Share: Surplus must be spent, not suppressed.

Key Insight:
    Flux entropy (J-gent) ≠ Metabolic entropy (void.entropy)

    - Flux entropy: Per-agent computational budget (local)
    - Metabolic entropy: System-wide activity pressure (global)

    They work together:
    - Flux entropy bounds individual agent computation
    - Metabolic entropy tracks overall system "heat"
    - Fever triggers creative expenditure when system runs hot
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from protocols.agentese.metabolism import FeverEvent, MetabolicEngine

    from .agent import FluxAgent


A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type


@dataclass
class FluxMetabolism(Generic[A, B]):
    """
    Adapter connecting FluxAgent to MetabolicEngine.

    Responsibilities:
    1. Call tick() on event processing (pressure accumulation)
    2. Handle FeverEvents (creative interruption)
    3. Report metabolic state to flux

    Usage:
        >>> from protocols.agentese.metabolism import get_metabolic_engine
        >>> from agents.flux.metabolism import FluxMetabolism
        >>>
        >>> metabolism = FluxMetabolism(engine=get_metabolic_engine())
        >>> flux_agent = Flux.lift(my_agent)
        >>> flux_agent.attach_metabolism(metabolism)

    The adapter is intentionally lightweight—it delegates all
    thermodynamic logic to the MetabolicEngine.
    """

    engine: "MetabolicEngine"

    # Token estimation (configurable per flux)
    input_tokens_per_event: int = 50
    output_tokens_per_event: int = 100

    # Fever handling
    on_fever: Any | None = field(default=None)
    """
    Optional callback when fever triggers.

    Signature: async def on_fever(event: FeverEvent) -> None

    If None, fever events are recorded but not acted upon.
    """

    # Statistics
    _events_metabolized: int = field(default=0, init=False)
    _fevers_triggered: int = field(default=0, init=False)
    _last_fever: "FeverEvent | None" = field(default=None, init=False)

    async def consume(self, _event: A) -> "FeverEvent | None":
        """
        Called when FluxAgent processes an event.

        Records metabolic activity and may trigger fever.

        Args:
            _event: The event being processed (not inspected, just counted)

        Returns:
            FeverEvent if fever was triggered, None otherwise
        """
        self._events_metabolized += 1

        # Tick the metabolic engine
        fever_event = self.engine.tick(
            input_count=self.input_tokens_per_event,
            output_count=self.output_tokens_per_event,
        )

        if fever_event is not None:
            self._fevers_triggered += 1
            self._last_fever = fever_event

            # Call fever callback if registered
            if self.on_fever is not None:
                try:
                    await self.on_fever(fever_event)
                except Exception:
                    # Don't let callback errors break processing
                    pass

        return fever_event

    def tithe(self, amount: float = 0.1) -> dict[str, Any]:
        """
        Voluntarily discharge metabolic pressure.

        Can be called by the flux when entering graceful shutdown,
        or by external code to preemptively reduce pressure.

        Returns:
            Dict with discharged amount and gratitude
        """
        return self.engine.tithe(amount)

    @property
    def pressure(self) -> float:
        """Current metabolic pressure."""
        return self.engine.pressure

    @property
    def in_fever(self) -> bool:
        """Whether the system is currently in fever state."""
        return self.engine.in_fever

    @property
    def temperature(self) -> float:
        """Token-based temperature (input/output ratio)."""
        return self.engine.temperature

    def status(self) -> dict[str, Any]:
        """
        Get combined flux-metabolism status.

        Returns:
            Dict with metabolic state and flux-specific counters
        """
        engine_status = self.engine.status()
        return {
            **engine_status,
            "events_metabolized": self._events_metabolized,
            "fevers_triggered": self._fevers_triggered,
            "last_fever_oblique": (
                self._last_fever.oblique_strategy if self._last_fever else None
            ),
        }


def create_flux_metabolism(
    engine: "MetabolicEngine | None" = None,
    input_tokens: int = 50,
    output_tokens: int = 100,
    on_fever: Any | None = None,
) -> FluxMetabolism[Any, Any]:
    """
    Factory function for FluxMetabolism.

    Args:
        engine: MetabolicEngine to use (gets global if None)
        input_tokens: Estimated input tokens per event
        output_tokens: Estimated output tokens per event
        on_fever: Optional callback for fever events

    Returns:
        Configured FluxMetabolism adapter
    """
    if engine is None:
        from protocols.agentese.metabolism import get_metabolic_engine

        engine = get_metabolic_engine()

    return FluxMetabolism(
        engine=engine,
        input_tokens_per_event=input_tokens,
        output_tokens_per_event=output_tokens,
        on_fever=on_fever,
    )
