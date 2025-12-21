#!/usr/bin/env python3
"""
Red and Blue: An Interactive Color Experience

Uses the Agent Foundry to synthesize an agent based on the concept
"red and blue", then projects it to WASM for browser-based interaction.

Run:
    cd impl/claude
    uv run python demos/red_and_blue.py
    # Opens browser with interactive experience
"""

from __future__ import annotations

import asyncio
import webbrowser
from pathlib import Path
from tempfile import gettempdir

from agents.a.halo import Capability
from agents.poly.types import Agent
from system.projector import WASMProjector


@Capability.Stateful(schema=dict)
@Capability.Observable(metrics=True)
class RedAndBlueAgent(Agent[str, str]):
    """
    An interactive exploration of red and blue.

    This agent creates a meditative, generative experience
    exploring the interplay between red and blue:
    - Color mixing and gradients
    - Complementary tensions
    - Emotional associations
    - Visual poetry
    """

    @property
    def name(self) -> str:
        return "red-and-blue"

    async def invoke(self, input_text: str) -> str:
        """Generate a red and blue experience based on input."""
        import random

        # Parse input for mode hints
        text = input_text.lower().strip()

        if not text or text in ("start", "begin", "hello"):
            return self._welcome()
        elif "mix" in text or "blend" in text:
            return self._mix_colors()
        elif "poem" in text or "verse" in text:
            return self._color_poem()
        elif "mood" in text or "feel" in text:
            return self._emotional_spectrum()
        elif "gradient" in text or "fade" in text:
            return self._gradient_journey()
        elif "dance" in text or "move" in text:
            return self._color_dance()
        elif "help" in text:
            return self._help()
        else:
            # Interpret as a creative prompt
            return self._interpret(text)

    def _welcome(self) -> str:
        return """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🔴  R E D   A N D   B L U E  🔵                         ║
║                                                              ║
║     An interactive meditation on two colors                  ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Try these commands:                                         ║
║                                                              ║
║    mix      - Watch red and blue dance together              ║
║    poem     - Generate color verse                           ║
║    mood     - Explore emotional resonances                   ║
║    gradient - Journey through the spectrum                   ║
║    dance    - Colors in motion                               ║
║                                                              ║
║  Or type anything and I'll interpret it through              ║
║  the lens of red and blue...                                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

    def _help(self) -> str:
        return """
Commands:
  mix      - Blend red and blue in various ways
  poem     - Generate poetic verses about the colors
  mood     - Explore emotional associations
  gradient - See the transition spectrum
  dance    - Watch colors interact dynamically

Or just type anything — I'll interpret it through red and blue.
"""

    def _mix_colors(self) -> str:
        import random

        mixes = [
            ("50/50", "🟣 Purple — The perfect balance"),
            ("70/30 Red", "🔴🟣 Magenta leaning — Passion with depth"),
            ("30/70 Blue", "🔵🟣 Violet leaning — Mystery with warmth"),
            ("Swirl", "🔴🔵🟣🔵🔴 — Chaos before harmony"),
            ("Layers", "🔴 over 🔵 — Warmth floating on cool depths"),
        ]

        results = []
        results.append("═══ COLOR MIXING LABORATORY ═══\n")

        for name, description in random.sample(mixes, 3):
            results.append(f"  {name}: {description}")

        results.append("\n" + "─" * 40)

        # Generate a random "formula"
        r = random.randint(0, 255)
        b = random.randint(0, 255)
        purple = (r, 0, b)
        results.append(f"\n  Today's Mix: RGB({r}, 0, {b})")
        results.append(f"  Hex: #{r:02x}00{b:02x}")

        # Poetic interpretation
        if r > b:
            results.append("  → Warm-dominant: energy, action, desire")
        elif b > r:
            results.append("  → Cool-dominant: calm, depth, infinity")
        else:
            results.append("  → Perfect balance: harmony, completion")

        return "\n".join(results)

    def _color_poem(self) -> str:
        import random

        poems = [
            """
    Red is the heartbeat
    Blue is the breath between
    Together: alive
            """,
            """
    In the space where
    fire meets ocean,
    we find purple —
    the color of
    transformation.
            """,
            """
    🔴 Passion speaks in crimson tongues
    🔵 Wisdom waits in sapphire depths
    🟣 Where they meet, magic is born
            """,
            """
    Red: the first color we learn to fear and love
    Blue: the last color we see before sleep

    Between them, the whole of human experience.
            """,
            """
    I asked red what it wanted.
    It said: everything, now.

    I asked blue what it wanted.
    It said: forever will do.
            """,
            """
    The sunset doesn't choose
    between red and blue —
    it holds both
    in a single breath
    of sky.
            """,
        ]

        poem = random.choice(poems)
        return f"═══ COLOR VERSE ═══\n{poem}\n{'─' * 30}"

    def _emotional_spectrum(self) -> str:
        import random

        red_moods = [
            "🔴 Passion — the fire that moves us",
            "🔴 Anger — energy seeking direction",
            "🔴 Love — warmth given form",
            "🔴 Courage — fear transformed",
            "🔴 Urgency — time made visible",
        ]

        blue_moods = [
            "🔵 Calm — the still point",
            "🔵 Sadness — depth acknowledged",
            "🔵 Trust — the color of clear skies",
            "🔵 Wisdom — time distilled",
            "🔵 Infinity — what lies beyond",
        ]

        purple_moods = [
            "🟣 Mystery — questions worth asking",
            "🟣 Royalty — red's passion with blue's depth",
            "🟣 Creativity — where opposites dance",
            "🟣 Spirituality — beyond the material",
            "🟣 Transformation — neither and both",
        ]

        result = ["═══ EMOTIONAL SPECTRUM ═══\n"]
        result.append(random.choice(red_moods))
        result.append(random.choice(blue_moods))
        result.append(random.choice(purple_moods))
        result.append("\n" + "─" * 40)
        result.append("\nWhat are you feeling today?")
        result.append("Type a word and I'll find its color...")

        return "\n".join(result)

    def _gradient_journey(self) -> str:
        # Create ASCII gradient from red to blue
        steps = [
            "🔴🔴🔴🔴🔴  Pure Red — Origin",
            "🔴🔴🔴🔴🟠  First warmth fading",
            "🔴🔴🔴🟠🟣  Magenta emerges",
            "🔴🔴🟣🟣🟣  The turning point",
            "🟣🟣🟣🟣🟣  Perfect Purple — Balance",
            "🟣🟣🟣🔵🔵  Cooling begins",
            "🟣🔵🔵🔵🔵  Violet deepens",
            "🔵🔵🔵🔵🔵  Pure Blue — Destination",
        ]

        result = ["═══ GRADIENT JOURNEY ═══\n"]
        result.append("From warmth to cool, passion to peace:\n")
        for step in steps:
            result.append(f"  {step}")
        result.append("\n" + "─" * 40)
        result.append("\nThe journey is the destination.")

        return "\n".join(result)

    def _color_dance(self) -> str:
        import random

        frames = []
        for i in range(5):
            # Create a "frame" of the dance
            width = 20
            positions = sorted(random.sample(range(width), 2))

            frame = list("·" * width)
            frame[positions[0]] = "🔴"
            frame[positions[1]] = "🔵"

            # Add purple where they're close
            if abs(positions[1] - positions[0]) <= 2:
                mid = (positions[0] + positions[1]) // 2
                if 0 <= mid < width and frame[mid] == "·":
                    frame[mid] = "🟣"

            frames.append("".join(frame))

        result = ["═══ COLOR DANCE ═══\n"]
        result.append("Watch red and blue move through space:\n")
        for i, f in enumerate(frames):
            result.append(f"  {i + 1}. [{f}]")
        result.append("\n" + "─" * 40)
        result.append("\nWhen they meet: 🟣")
        result.append("Run 'dance' again to see new movements.")

        return "\n".join(result)

    def _interpret(self, text: str) -> str:
        """Interpret arbitrary input through the red/blue lens."""
        import random

        # Map common concepts to red or blue associations
        red_words = {
            "fire",
            "hot",
            "warm",
            "passion",
            "love",
            "anger",
            "energy",
            "fast",
            "loud",
            "bold",
            "heart",
            "blood",
            "sun",
            "day",
            "action",
            "yes",
            "go",
            "start",
            "create",
            "build",
        }

        blue_words = {
            "water",
            "cold",
            "cool",
            "calm",
            "peace",
            "sad",
            "still",
            "slow",
            "quiet",
            "subtle",
            "mind",
            "sky",
            "moon",
            "night",
            "thought",
            "no",
            "stop",
            "wait",
            "reflect",
            "dream",
        }

        words = set(text.lower().split())

        red_score = len(words & red_words)
        blue_score = len(words & blue_words)

        result = [f"═══ INTERPRETING: '{text}' ═══\n"]

        if red_score > blue_score:
            result.append("🔴 This resonates with RED:")
            result.append("   Energy, passion, urgency, warmth")
            result.append(
                f"\n   Red words found: {words & red_words or 'none (but the feeling is there)'}"
            )
        elif blue_score > red_score:
            result.append("🔵 This resonates with BLUE:")
            result.append("   Calm, depth, reflection, coolness")
            result.append(
                f"\n   Blue words found: {words & blue_words or 'none (but the feeling is there)'}"
            )
        else:
            result.append("🟣 This holds BOTH red and blue:")
            result.append("   Balance, tension, transformation")
            result.append("   Perhaps this is where the magic lives.")

        result.append("\n" + "─" * 40)

        # Add a random reflection
        reflections = [
            "Everything contains both colors, in different proportions.",
            "What we see depends on how we look.",
            "Red and blue are not opposites — they are dance partners.",
            "The absence of one makes the other more vivid.",
        ]
        result.append(f"\n💭 {random.choice(reflections)}")

        return "\n".join(result)


async def main() -> None:
    """Forge the agent and open in browser."""
    print("🎨 Forging Red and Blue experience...")
    print()

    # Use WASMProjector directly for this creative agent
    projector = WASMProjector()
    html = projector.compile(RedAndBlueAgent)

    # Custom styling injection for red/blue theme
    custom_css = """
    <style>
        :root {
            --red: #e63946;
            --blue: #457b9d;
            --purple: #7b2cbf;
        }
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
        }
        .container {
            background: rgba(20, 20, 40, 0.9);
            border: 2px solid var(--purple);
            box-shadow: 0 0 30px rgba(123, 44, 191, 0.3);
        }
        h1 {
            background: linear-gradient(90deg, var(--red), var(--purple), var(--blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        textarea {
            background: rgba(10, 10, 30, 0.8);
            border-color: var(--purple);
            color: #f1faee;
        }
        textarea:focus {
            border-color: var(--blue);
            box-shadow: 0 0 10px rgba(69, 123, 157, 0.5);
        }
        button {
            background: linear-gradient(135deg, var(--red), var(--purple));
            border: none;
        }
        button:hover {
            background: linear-gradient(135deg, var(--purple), var(--blue));
            transform: scale(1.02);
        }
        #output {
            background: rgba(10, 10, 30, 0.9);
            border-color: var(--blue);
            color: #a8dadc;
            white-space: pre-wrap;
            font-family: monospace;
        }
        .badge {
            background: var(--purple);
        }
    </style>
    """

    # Inject custom CSS
    html = html.replace("</head>", f"{custom_css}</head>")

    # Update title
    html = html.replace("<title>WASM Agent Sandbox</title>", "<title>🔴 Red and Blue 🔵</title>")

    # Save and open
    output_path = Path(gettempdir()) / "red_and_blue.html"
    output_path.write_text(html)

    print(f"✅ Generated: {output_path}")
    print(f"📦 Bundle size: {len(html):,} bytes")
    print()
    print("═" * 50)
    print("  🔴 RED AND BLUE 🔵")
    print("  An interactive color meditation")
    print("═" * 50)
    print()
    print("Try these in the browser:")
    print("  • Type 'start' to begin")
    print("  • Type 'mix' to blend colors")
    print("  • Type 'poem' for color verse")
    print("  • Type 'mood' for emotional spectrum")
    print("  • Type 'gradient' for a journey")
    print("  • Type 'dance' to watch colors move")
    print("  • Or type anything and see its color...")
    print()

    webbrowser.open(f"file://{output_path}")


if __name__ == "__main__":
    asyncio.run(main())
