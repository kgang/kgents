"""
Soul Demo: K-gent Soul on the Dashboard.

This demonstrates P5 of the k-terrarium-llm-agents plan:
Wire SoulAdapter into Terrarium dashboard.

The demo shows a live K-gent soul card that updates based on actual soul state.

Usage:
    python -m agents.i.reactive.demo.soul_demo

    # With streaming dialogue
    python -m agents.i.reactive.demo.soul_demo --dialogue "What should I focus on?"
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime
from typing import Any

from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget
from agents.i.reactive.widget import RenderTarget
from agents.i.reactive.wiring.adapters import SoulAdapter


def create_soul_card_from_manifest(
    manifest: dict[str, Any],
    adapter: SoulAdapter | None = None,
) -> AgentCardWidget:
    """
    Create an AgentCardWidget from K-gent soul manifest.

    This is the bridge: SoulAdapter transforms soul state into AgentCardState.

    Args:
        manifest: Output from KgentSoul.manifest_brief()
        adapter: Optional SoulAdapter instance (creates one if not provided)

    Returns:
        AgentCardWidget ready for rendering to any target
    """
    adapter = adapter or SoulAdapter()
    card_state = adapter.adapt_brief(manifest)
    return AgentCardWidget(card_state)


def render_soul_card_cli(
    manifest: dict[str, Any],
    adapter: SoulAdapter | None = None,
) -> str:
    """
    Render K-gent soul as CLI text.

    Args:
        manifest: Output from KgentSoul.manifest_brief()
        adapter: Optional SoulAdapter instance

    Returns:
        CLI-formatted string representation of soul state
    """
    widget = create_soul_card_from_manifest(manifest, adapter)
    return widget.project(RenderTarget.CLI)


async def run_soul_demo(dialogue_prompt: str | None = None) -> None:
    """
    Run the soul demo.

    If a dialogue prompt is provided, it will stream the response.
    Otherwise, it shows the current soul state.
    """
    try:
        from agents.k.soul import KgentSoul
    except ImportError as e:
        print(f"Error: Could not import K-gent Soul: {e}")
        sys.exit(1)

    print("=" * 60)
    print("  K-GENT SOUL DASHBOARD DEMO")
    print("  Wiring SoulAdapter → AgentCardWidget")
    print("=" * 60)
    print()

    # Create soul and adapter
    soul = KgentSoul()
    adapter = SoulAdapter()

    # Get current state
    manifest = soul.manifest_brief()
    print("CURRENT SOUL STATE")
    print("-" * 40)
    print(render_soul_card_cli(manifest, adapter))
    print()

    # Show eigenvectors if available
    if hasattr(soul, "eigenvectors"):
        evs = soul.eigenvectors
        print("EIGENVECTOR COORDINATES")
        print("-" * 40)
        # Iterate over eigenvector attributes
        for attr_name in [
            "aesthetic",
            "categorical",
            "gratitude",
            "whimsy",
            "rigor",
            "velocity",
        ]:
            if hasattr(evs, attr_name):
                coord = getattr(evs, attr_name)
                value = coord.value if hasattr(coord, "value") else 0.5
                name = coord.name if hasattr(coord, "name") else attr_name
                bar_len = int(value * 20)
                bar = "█" * bar_len + "░" * (20 - bar_len)
                print(f"  {name:<20} {bar} {value:.2f}")
        print()

    # Stream dialogue if requested
    if dialogue_prompt:
        print("STREAMING DIALOGUE")
        print("-" * 40)
        print(f"Prompt: {dialogue_prompt}")
        print()

        # Get time of day greeting (P7 preview)
        hour = datetime.now().hour
        greeting = _time_greeting(hour)
        if greeting:
            print(f"  [{greeting}]")
            print()

        # Stream response
        from agents.k.persona import DialogueMode

        token_count = 0
        async for event in soul.dialogue_flux(
            dialogue_prompt, mode=DialogueMode.REFLECT
        ):
            if event.is_data:
                sys.stdout.write(event.value)
                sys.stdout.flush()
            elif event.is_metadata:
                token_count = event.value.tokens_used

        print()
        print()
        print(f"  [{token_count} tokens]")

        # Show updated state after dialogue
        print()
        print("UPDATED SOUL STATE")
        print("-" * 40)
        manifest = soul.manifest_brief()
        print(render_soul_card_cli(manifest, adapter))

    print()
    print("=" * 60)


def _time_greeting(hour: int) -> str:
    """Get a time-of-day greeting (P7 minimal)."""
    if 5 <= hour < 12:
        return "Good morning, Kent"
    elif 12 <= hour < 17:
        return "Good afternoon, Kent"
    elif 17 <= hour < 21:
        return "Good evening, Kent"
    else:
        return "Late night thinking, Kent"


def main() -> None:
    """Run the demo."""
    parser = argparse.ArgumentParser(description="K-gent Soul Dashboard Demo")
    parser.add_argument(
        "--dialogue",
        "-d",
        type=str,
        default=None,
        help="Optional dialogue prompt to stream",
    )
    args = parser.parse_args()

    asyncio.run(run_soul_demo(args.dialogue))


if __name__ == "__main__":
    main()
