"""
I-gent CLI handlers for the Hollow Shell.

Commands:
  kgents whisper             Get status whisper for prompt

NOTE: `kgents garden` has been removed. Use `kgents dashboard` instead
for the real-time system health TUI that shows K-gent, metabolism, flux,
and triad metrics.
"""

from __future__ import annotations

import asyncio
from typing import Sequence


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
