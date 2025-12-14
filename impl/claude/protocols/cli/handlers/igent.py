"""
I-gent CLI handlers for the Hollow Shell.

Commands:
  kgents whisper             Get status whisper for prompt
  kgents sparkline <nums>    Instant sparkline from numbers
  kgents weather             Agent activity density visualization
  kgents glitch <text>       Zalgo-style text corruption

NOTE: `kgents garden` has been removed. Use `kgents dashboard` instead
for the real-time system health TUI that shows K-gent, metabolism, flux,
and triad metrics.
"""

from __future__ import annotations

import asyncio
import json as json_module
from typing import Any, Sequence


def cmd_whisper(args: Sequence[str]) -> int:
    """Handle whisper command - status for prompt integration."""
    # Parse args
    fmt = "prompt"
    for arg in args:
        if arg in ("--raw", "-r"):
            fmt = "raw"
        elif arg in ("--help", "-h"):
            print("kgents whisper - Get status whisper for prompt")
            print()
            print("USAGE:")
            print("  kgents whisper [--raw]")
            print()
            print("OPTIONS:")
            print("  --raw, -r    Show raw whisper (not formatted for prompt)")
            print("  --help, -h   Show this help")
            return 0

    # Collect metrics and format whisper
    whisper = asyncio.run(_collect_whisper())

    if fmt == "prompt":
        print(whisper)
    else:
        print(f"[whisper] {whisper}")

    return 0


async def _collect_whisper() -> str:
    """Collect system state and format as a terse whisper."""
    try:
        from agents.i.data.dashboard_collectors import collect_metrics

        metrics = await collect_metrics()

        parts = []

        # K-gent mode
        if metrics.kgent.is_online:
            parts.append(f"K:{metrics.kgent.mode[:3]}")

        # Metabolism pressure (as percentage)
        if metrics.metabolism.is_online:
            pct = int(metrics.metabolism.pressure * 100)
            fever = "!" if metrics.metabolism.in_fever else ""
            parts.append(f"P:{pct}%{fever}")

        # Flux throughput
        if metrics.flux.is_online:
            eps = metrics.flux.events_per_second
            if eps > 0:
                parts.append(f"F:{eps:.1f}/s")

        # Triad health (overall as bar)
        if metrics.triad.is_online:
            overall = int(metrics.triad.overall * 100)
            parts.append(f"T:{overall}%")

        if not parts:
            return "◌"  # Empty circle = no services online

        return " ".join(parts)

    except Exception:
        return "◌"  # Graceful fallback


# =============================================================================
# Sparkline Command
# =============================================================================


def cmd_sparkline(args: Sequence[str]) -> int:
    """
    Handle sparkline command - instant mini-chart from numbers.

    Usage:
        kgents sparkline 0.1 0.3 0.5 0.8 0.6 0.4
        kgents sparkline --label "CPU" 0.2 0.4 0.6 0.8 0.9 0.7
        kgents sparkline --json 0.1 0.2 0.3

    The sparkline characters: ▁▂▃▄▅▆▇█
    """
    # Parse args
    json_mode = "--json" in args
    show_bounds = "--bounds" in args
    label = None
    values: list[float] = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--help" or arg == "-h":
            print("kgents sparkline - Instant sparkline from numbers")
            print()
            print("USAGE:")
            print("  kgents sparkline [OPTIONS] <numbers...>")
            print()
            print("EXAMPLES:")
            print("  kgents sparkline 0.1 0.3 0.5 0.8 0.6 0.4")
            print('  kgents sparkline --label "CPU" 0.2 0.4 0.6')
            print("  kgents sparkline --json 0.1 0.2 0.3")
            print()
            print("OPTIONS:")
            print("  --label <text>  Add a label prefix")
            print("  --bounds        Show min/max values")
            print("  --json          Output as JSON")
            print("  --help, -h      Show this help")
            print()
            print("NOTES:")
            print("  Values should be 0.0-1.0 (auto-normalized otherwise)")
            print("  Characters used: ▁▂▃▄▅▆▇█")
            return 0
        elif arg == "--label" and i + 1 < len(args):
            label = args[i + 1]
            i += 2
            continue
        elif arg.startswith("--"):
            i += 1
            continue
        else:
            # Try to parse as number
            try:
                values.append(float(arg))
            except ValueError:
                pass
        i += 1

    if not values:
        print("[SPARKLINE] Error: No numbers provided")
        print("Usage: kgents sparkline 0.1 0.3 0.5 0.8 0.6 0.4")
        return 1

    # Auto-normalize if values exceed 0-1 range
    max_val = max(values)
    min_val = min(values)
    if max_val > 1.0 or min_val < 0.0:
        # Normalize to 0-1
        range_val = max_val - min_val if max_val != min_val else 1.0
        values = [(v - min_val) / range_val for v in values]

    # Create sparkline using reactive primitives
    from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget
    from agents.i.reactive.widget import RenderTarget

    spark = SparklineWidget(
        SparklineState(
            values=tuple(values),
            max_length=len(values) + 10,
            label=label,
            show_bounds=show_bounds,
        )
    )

    if json_mode:
        result = spark.project(RenderTarget.JSON)
        print(json_module.dumps(result, indent=2))
    else:
        result = spark.project(RenderTarget.CLI)
        print(result)

    return 0


# =============================================================================
# Weather Command
# =============================================================================


def cmd_weather(args: Sequence[str]) -> int:
    """
    Handle weather command - agent activity density visualization.

    Shows a visual representation of agent activity using density field.

    Usage:
        kgents weather
        kgents weather --size 60x20
        kgents weather --entropy 0.3
    """
    # Parse args
    json_mode = "--json" in args
    width = 60
    height = 15
    entropy = 0.1

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--help" or arg == "-h":
            print("kgents weather - Agent activity density visualization")
            print()
            print("USAGE:")
            print("  kgents weather [OPTIONS]")
            print()
            print("OPTIONS:")
            print("  --size WxH       Field size (default: 60x15)")
            print("  --entropy N      Base entropy 0.0-1.0 (default: 0.1)")
            print("  --json           Output as JSON")
            print("  --help, -h       Show this help")
            print()
            print("Entities are placed based on system state (if available).")
            return 0
        elif arg == "--size" and i + 1 < len(args):
            try:
                w, h = args[i + 1].split("x")
                width = int(w)
                height = int(h)
            except ValueError:
                pass
            i += 2
            continue
        elif arg == "--entropy" and i + 1 < len(args):
            try:
                entropy = float(args[i + 1])
            except ValueError:
                pass
            i += 2
            continue
        i += 1

    # Create density field with mock entities
    from agents.i.reactive.primitives.density_field import (
        DensityFieldState,
        DensityFieldWidget,
        Entity,
        Wind,
    )
    from agents.i.reactive.widget import RenderTarget

    # Try to get real system state for entities
    entities: list[Entity] = []
    try:
        metrics = asyncio.run(_collect_weather_metrics())
        entities = metrics
    except Exception:
        # Default entities if metrics unavailable
        entities = [
            Entity(
                id="soul",
                x=width // 4,
                y=height // 2,
                char="◉",
                phase="active",
                heat=0.4,
            ),
            Entity(
                id="flux",
                x=width // 2,
                y=height // 3,
                char="○",
                phase="waiting",
                heat=0.2,
            ),
            Entity(
                id="meta",
                x=3 * width // 4,
                y=height // 2,
                char="◌",
                phase="idle",
                heat=0.1,
            ),
        ]

    field = DensityFieldWidget(
        DensityFieldState(
            width=width,
            height=height,
            base_entropy=entropy,
            entities=tuple(entities),
            wind=Wind(dx=0.3, dy=0.1, strength=0.2),
        )
    )

    if json_mode:
        result = field.project(RenderTarget.JSON)
        print(json_module.dumps(result, indent=2))
    else:
        print("[WEATHER] Agent Activity Density")
        print()
        result = field.project(RenderTarget.CLI)
        print(result)
        print()
        # Legend
        print(f"  ◉ = Soul  ○ = Flux  ◌ = Meta  (entropy: {entropy:.1f})")

    return 0


async def _collect_weather_metrics() -> list[Any]:
    """Collect system metrics to place entities on weather map."""
    from agents.i.reactive.primitives.density_field import Entity

    entities: list[Entity] = []

    try:
        from agents.i.data.dashboard_collectors import collect_metrics

        metrics = await collect_metrics()

        # K-gent soul
        if metrics.kgent.is_online:
            entities.append(
                Entity(
                    id="soul",
                    x=15,
                    y=7,
                    char="◉",
                    phase="active" if metrics.kgent.mode != "dormant" else "idle",
                    heat=0.5,
                )
            )

        # Metabolism
        if metrics.metabolism.is_online:
            heat = metrics.metabolism.pressure
            entities.append(
                Entity(
                    id="metabolism",
                    x=30,
                    y=5,
                    char="⚡" if metrics.metabolism.in_fever else "○",
                    phase="active" if metrics.metabolism.in_fever else "waiting",
                    heat=heat,
                )
            )

        # Flux
        if metrics.flux.is_online:
            heat = min(1.0, metrics.flux.events_per_second / 10.0)
            entities.append(
                Entity(
                    id="flux",
                    x=45,
                    y=7,
                    char="◌",
                    phase="active" if metrics.flux.events_per_second > 0 else "idle",
                    heat=heat,
                )
            )

    except Exception:
        pass

    return entities


# =============================================================================
# Glitch Command
# =============================================================================


def cmd_glitch(args: Sequence[str]) -> int:
    """
    Handle glitch command - text corruption for visual effect.

    Usage:
        kgents glitch "Hello World"
        kgents glitch --entropy 0.8 "Warning: System error"
        kgents glitch --json "Test"
    """
    # Parse args
    json_mode = "--json" in args
    entropy = 0.5
    text_parts: list[str] = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--help" or arg == "-h":
            print("kgents glitch - Text corruption for visual effect")
            print()
            print("USAGE:")
            print('  kgents glitch [OPTIONS] "text to glitch"')
            print()
            print("OPTIONS:")
            print("  --entropy N   Corruption level 0.0-1.0 (default: 0.5)")
            print("  --json        Output as JSON")
            print("  --help, -h    Show this help")
            print()
            print("EXAMPLE:")
            print('  kgents glitch --entropy 0.8 "System Error"')
            return 0
        elif arg == "--entropy" and i + 1 < len(args):
            try:
                entropy = float(args[i + 1])
            except ValueError:
                pass
            i += 2
            continue
        elif arg.startswith("--"):
            i += 1
            continue
        else:
            text_parts.append(arg)
        i += 1

    text = " ".join(text_parts)
    if not text:
        print("[GLITCH] Error: No text provided")
        print('Usage: kgents glitch "Hello World"')
        return 1

    # Create glitched text using GlyphWidget
    import time

    from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
    from agents.i.reactive.widget import RenderTarget

    t = time.time() * 1000  # Current time in ms

    glitched_chars: list[str] = []
    glyph_data: list[dict[str, Any]] = []

    for idx, char in enumerate(text):
        glyph = GlyphWidget(
            GlyphState(
                char=char,
                entropy=entropy,
                seed=idx * 17 + 42,  # Deterministic seed per character
                t=t,
            )
        )

        if json_mode:
            glyph_data.append(glyph.project(RenderTarget.JSON))
        else:
            glitched_chars.append(glyph.project(RenderTarget.CLI))

    if json_mode:
        result = {
            "original": text,
            "entropy": entropy,
            "glyphs": glyph_data,
        }
        print(json_module.dumps(result, indent=2))
    else:
        # Add zalgo-style combining characters for high entropy
        if entropy > 0.3:
            import random

            from agents.i.reactive.entropy import ZALGO_ABOVE, ZALGO_BELOW, ZALGO_MID

            random.seed(int(t) + len(text))

            output_chars: list[str] = []
            for idx, char in enumerate(glitched_chars):
                output_chars.append(char)

                # Add zalgo based on entropy
                intensity = int(entropy * 3) + 1
                if entropy > 0.3:
                    for _ in range(intensity):
                        if random.random() < entropy:
                            output_chars.append(random.choice(ZALGO_ABOVE))
                        if random.random() < entropy:
                            output_chars.append(random.choice(ZALGO_MID))
                        if random.random() < entropy:
                            output_chars.append(random.choice(ZALGO_BELOW))

            print("".join(output_chars))
        else:
            print("".join(glitched_chars))

    return 0
