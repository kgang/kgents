"""
Fever Events and Stream - Creative output during metabolic fever.

When the system runs hot (metabolic pressure exceeds threshold),
the FeverStream generates creative output:
- Oblique Strategies (FREE, no LLM cost)
- Fever Dreams (EXPENSIVE, uses LLM)

The Accursed Share: surplus must be spent, not suppressed.
Fever is the mechanism for spending accumulated activity surplus.

See: plans/void/entropy.md
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FeverEvent:
    """
    Record of a fever trigger.

    A FeverEvent is emitted when metabolic pressure exceeds the
    critical threshold, forcing creative expenditure.
    """

    intensity: float  # How far above threshold (pressure - threshold)
    timestamp: float  # When triggered (time.time())
    trigger: str  # "pressure_overflow", "manual", "error"
    seed: float  # For deterministic oblique selection
    oblique_strategy: str = ""  # Populated by FeverStream


@dataclass
class FeverStream:
    """
    Generates creative output during fever state.

    Two modes:
    - oblique: Quick, no LLM (Oblique Strategies) - FREE
    - dream: Slow, uses LLM - EXPENSIVE

    Oblique Strategies are inspired by Brian Eno and Peter Schmidt's
    1975 card deck for breaking creative blocks.
    """

    _oblique_strategies: tuple[str, ...] = field(
        default=(
            "Honor thy error as a hidden intention.",
            "What would your closest friend do?",
            "Turn it upside down.",
            "Ask your body.",
            "Do nothing for as long as possible.",
            "Use an old idea.",
            "What are you really thinking about just now?",
            "Look at the order in which you do things.",
            "Emphasize differences.",
            "What mistakes did you make last time?",
            "Is it finished?",
            "Into the impossible.",
            "Work at a different speed.",
            "Gardening, not architecture.",
            "Go slowly all the way round the outside.",
            "Consider the opposite.",
            "What if you're already at the destination?",
            "The path is made by walking.",
            "Remove ambiguities and convert to specifics.",
            "Change instrument roles.",
        )
    )

    # Random state for non-seeded calls
    _random: random.Random = field(default_factory=random.Random)

    def oblique(self, seed: float | None = None) -> str:
        """
        Return an Oblique Strategy.

        Cost: FREE (no LLM)
        Deterministic: Same seed → same strategy

        Args:
            seed: Optional seed for deterministic selection (0.0-1.0)

        Returns:
            An Oblique Strategy string
        """
        if seed is None:
            seed = self._random.random()
        idx = int(seed * len(self._oblique_strategies))
        # Clamp to valid range
        idx = min(idx, len(self._oblique_strategies) - 1)
        return self._oblique_strategies[idx]

    async def dream(
        self,
        context: dict[str, Any],
        llm_client: Any = None,
    ) -> str:
        """
        Generate a fever dream from current context.

        Cost: HIGH (uses LLM with temperature=1.4)
        Falls back to oblique() if no LLM client provided.

        This is the "hallucination as feature" pattern—the Veale Fix.
        During fever, the system's temperature rises and generates
        sideways thoughts that might illuminate problems.

        Args:
            context: Current system context (truncated to 1000 chars)
            llm_client: Optional LLM client with async generate() method

        Returns:
            A fever dream string (or oblique strategy as fallback)
        """
        if llm_client is None:
            return self.oblique()

        # Truncate context to prevent token explosion
        import json

        context_str = json.dumps(context, indent=2, default=str)[:1000]

        prompt = f"""
The system is running hot. Here is the current context (truncated):
{context_str}

Generate an oblique strategy—a sideways thought that might
illuminate the problem from an unexpected angle.

Be brief, enigmatic, potentially useful.
"""

        try:
            response = await llm_client.generate(
                prompt,
                temperature=1.4,  # HOT
                max_tokens=100,
            )
            return str(response)
        except Exception:
            # Fallback to oblique on any error
            return self.oblique()

    def populate_event(self, event: FeverEvent) -> FeverEvent:
        """
        Populate a FeverEvent with an oblique strategy.

        Modifies the event in place and returns it.
        """
        event.oblique_strategy = self.oblique(event.seed)
        return event
