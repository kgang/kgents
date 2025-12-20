"""
ObliqueStrategy Overlay - Brian Eno's creative prompts.

Appears during high-entropy moments (entropy > 0.8) to offer
lateral thinking prompts.

Philosophy: "In moments of uncertainty, seek oblique wisdom."
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from ...theme.dashboard import THEME

if TYPE_CHECKING:
    pass


# Brian Eno & Peter Schmidt's Oblique Strategies
# A curated selection relevant to agent development
OBLIQUE_STRATEGIES = [
    "What would your closest friend do?",
    "Honor thy error as a hidden intention",
    "Look closely at the most embarrassing details and amplify them",
    "What wouldn't you do?",
    "Try faking it",
    "State the problem in words as clearly as possible",
    "Only one element of each kind",
    "What is the simplest solution?",
    "Emphasize differences",
    "Ask your body",
    "Work at a different speed",
    "Accept advice",
    "Is there something missing?",
    "Not building a wall but making a brick",
    "Use an old idea",
    "Water",
    "Breathe more deeply",
    "Courage!",
    "Do the washing up",
    "Listen to the quiet voice",
    "Take a break",
    "Look at the order in which you do things",
    "What are you really thinking about just now?",
    "Incorporate randomness",
    "Go slowly all the way round the outside",
    "Define an area as 'safe' and use it as an anchor",
    "Abandon normal instruments",
    "Fill every beat with something",
    "Get your neck massaged",
    "How would you have done it?",
    "Simple subtraction",
    "Are there sections? Consider transitions",
    "Turn it upside down",
    "Think of the radio",
    "Put in earplugs",
    "Make a blank valuable by putting it in an exquisite frame",
    "Emphasize the flaws",
    "Remember those quiet evenings",
    "Don't be frightened of clichés",
    "You are an engineer",
    "Make it more sensual",
    "Trust in the you of now",
    "What mistakes did you make last time?",
    "Consult other sources - promising - unpromising",
    "Convert a melodic element into a rhythmic element",
    "Faced with a choice, do both",
    "Give way to your worst impulse",
    "Ask people to work against their better judgement",
    "Simply a matter of work",
]


class ObliqueStrategyOverlay(ModalScreen[None]):
    """
    Oblique Strategy overlay for creative guidance.

    Shows a random strategy from Brian Eno's deck.
    Auto-appears during high-entropy moments.
    """

    CSS = f"""
    ObliqueStrategyOverlay {{
        align: center middle;
    }}

    ObliqueStrategyOverlay #oblique-container {{
        width: 60;
        height: auto;
        border: double {THEME.oblique};
        background: {THEME.background};
        padding: 3;
    }}

    ObliqueStrategyOverlay #oblique-header {{
        height: 1;
        text-align: center;
        color: {THEME.oblique};
        text-style: bold;
        margin-bottom: 2;
    }}

    ObliqueStrategyOverlay #strategy {{
        height: auto;
        text-align: center;
        color: {THEME.text_primary};
        text-style: italic;
        padding: 2;
        margin-bottom: 2;
    }}

    ObliqueStrategyOverlay #oblique-footer {{
        height: auto;
        text-align: center;
        color: {THEME.text_muted};
        border-top: solid {THEME.border};
        padding-top: 1;
    }}

    ObliqueStrategyOverlay .citation {{
        color: {THEME.text_muted};
        text-style: italic;
    }}
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close", show=True),
        Binding("enter", "dismiss", "Close", show=False),
        Binding("space", "new_strategy", "Another", show=True),
    ]

    def __init__(
        self,
        strategy: str | None = None,
        name: str | None = None,
    ) -> None:
        """
        Initialize the oblique strategy overlay.

        Args:
            strategy: Specific strategy to show (or None for random)
            name: Widget name
        """
        super().__init__(name=name)
        self.strategy_text = strategy or self._get_random_strategy()

    def compose(self) -> ComposeResult:
        """Compose the overlay."""
        with Container(id="oblique-container"):
            with Vertical():
                # Header
                yield Static("OBLIQUE STRATEGY", id="oblique-header")

                # Strategy text
                yield Static(
                    f'"{self.strategy_text}"',
                    id="strategy",
                )

                # Footer with citation
                footer_text = (
                    "— Brian Eno & Peter Schmidt\n\n[Space] for another • [Escape] to close"
                )
                yield Static(footer_text, id="oblique-footer")

    def _get_random_strategy(self) -> str:
        """Get a random oblique strategy."""
        return random.choice(OBLIQUE_STRATEGIES)

    async def action_new_strategy(self) -> None:
        """Show a new random strategy."""
        self.strategy_text = self._get_random_strategy()

        # Update the strategy widget
        strategy_widget = self.query_one("#strategy", Static)
        strategy_widget.update(f'"{self.strategy_text}"')

    async def action_dismiss(self, result: None = None) -> None:
        """Dismiss the overlay."""
        self.dismiss()


def should_show_oblique_strategy(entropy: float, threshold: float = 0.8) -> bool:
    """
    Determine if an oblique strategy should appear.

    Args:
        entropy: Current entropy level (0.0-1.0)
        threshold: Entropy threshold for triggering (default 0.8)

    Returns:
        True if entropy exceeds threshold
    """
    return entropy >= threshold


__all__ = [
    "ObliqueStrategyOverlay",
    "should_show_oblique_strategy",
    "OBLIQUE_STRATEGIES",
]
