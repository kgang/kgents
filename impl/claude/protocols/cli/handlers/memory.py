"""
Memory Handler: Four Pillars Memory System CLI.

Shows memory health and status from the Four Pillars architecture:
- Memory Crystal: Holographic patterns with resolution levels
- Pheromone Field: Stigmergic traces and gradients
- Active Inference: Free energy budgets and beliefs
- Language Games: Wittgensteinian memory access

Usage:
    kg memory status      # Show Four Pillars health summary
    kg memory detail      # Detailed breakdown of each pillar
    kg memory --ghost     # Read from ghost cache (if available)

Example:
    $ kg memory status
    [MEMORY] Four Pillars Health

    Status:  HEALTHY (85%)
    Crystal: 90% (6 concepts, 2 hot)
    Field:   75% (9 traces, decay 10%/hr)
    Inference: 80% (precision 1.2, entropy 1.4)

    Run 'kg memory detail' for full breakdown.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path


def cmd_memory(args: list[str]) -> int:
    """
    Show Four Pillars memory health status.

    Connects to MemoryDataProvider (demo mode by default).
    """
    # Parse args
    help_mode = "--help" in args or "-h" in args
    ghost_mode = "--ghost" in args
    detail_mode = "detail" in args

    if help_mode:
        print(__doc__)
        return 0

    if ghost_mode:
        return _show_from_ghost()
    elif detail_mode:
        return asyncio.run(_show_detail())
    else:
        return asyncio.run(_show_status())


async def _show_status() -> int:
    """Show summary status of Four Pillars."""
    try:
        from agents.i.data.memory_provider import create_memory_provider_async

        provider = await create_memory_provider_async(demo_mode=True)

        crystal = provider.get_crystal_stats()
        field = await provider.get_field_stats()
        inference = provider.get_inference_stats()
        health = provider.compute_health()

        # Status colors (ANSI)
        status_colors = {
            "HEALTHY": "\033[32m",  # Green
            "DEGRADED": "\033[33m",  # Yellow
            "CRITICAL": "\033[31m",  # Red
        }
        reset = "\033[0m"
        status = health["status"]
        color = status_colors.get(status, "")

        print("[MEMORY] Four Pillars Health")
        print()
        print(f"Status:    {color}{status}{reset} ({health['health_score']:.0%})")

        if crystal:
            print(
                f"Crystal:   {health['crystal_health']:.0%} "
                f"({crystal['concept_count']} concepts, {crystal['hot_count']} hot)"
            )

        if field:
            print(
                f"Field:     {health['field_health']:.0%} "
                f"({field['trace_count']} traces, decay {field['decay_rate']:.0%}/hr)"
            )

        if inference:
            print(
                f"Inference: {health['inference_health']:.0%} "
                f"(precision {inference['precision']:.1f}, "
                f"entropy {inference['entropy']:.1f})"
            )

        print()
        print("Run 'kg memory detail' for full breakdown.")

        return 0

    except ImportError as e:
        print(f"[MEMORY] M-gent not available: {e}")
        print("  The Four Pillars memory system requires M-gent agents.")
        return 1
    except Exception as e:
        print(f"[MEMORY] Error: {e}")
        return 1


async def _show_detail() -> int:
    """Show detailed breakdown of each pillar."""
    try:
        from agents.i.data.memory_provider import create_memory_provider_async

        provider = await create_memory_provider_async(demo_mode=True)

        crystal = provider.get_crystal_stats()
        field = await provider.get_field_stats()
        inference = provider.get_inference_stats()
        health = provider.compute_health()

        print("[MEMORY] Four Pillars Detail")
        print()

        # Overall health
        print("╭─ Overall Health ─────────────────────────────╮")
        status = health["status"]
        score = health["health_score"]
        bar_len = int(score * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        print(f"│ Status: {status:<12} Score: {bar} {score:.0%} │")
        print("╰──────────────────────────────────────────────╯")
        print()

        # Crystal detail
        if crystal:
            print("╭─ Memory Crystal ─────────────────────────────╮")
            print(f"│ Dimension:      {crystal['dimension']:<28} │")
            print(f"│ Concepts:       {crystal['concept_count']:<28} │")
            print(f"│ Hot Patterns:   {crystal['hot_count']:<28} │")
            print(f"│ Avg Resolution: {crystal['avg_resolution']:<28.2f} │")
            print(f"│ Min Resolution: {crystal['min_resolution']:<28.2f} │")
            print(f"│ Max Resolution: {crystal['max_resolution']:<28.2f} │")
            print("╰──────────────────────────────────────────────╯")
            print()

        # Field detail
        if field:
            print("╭─ Pheromone Field ────────────────────────────╮")
            print(f"│ Concept Count:  {field['concept_count']:<28} │")
            print(f"│ Trace Count:    {field['trace_count']:<28} │")
            print(f"│ Deposit Count:  {field['deposit_count']:<28} │")
            print(f"│ Evaporations:   {field['evaporation_count']:<28} │")
            print(f"│ Avg Intensity:  {field['avg_intensity']:<28.2f} │")
            print(f"│ Decay Rate:     {field['decay_rate']:<28.1%} │")
            print("╰──────────────────────────────────────────────╯")
            print()

        # Inference detail
        if inference:
            print("╭─ Active Inference ───────────────────────────╮")
            print(f"│ Precision:      {inference['precision']:<28.2f} │")
            print(f"│ Entropy:        {inference['entropy']:<28.2f} │")
            print(f"│ Concept Count:  {inference['concept_count']:<28} │")
            print(f"│ Memory Budgets: {inference['memory_count']:<28} │")
            print("╰──────────────────────────────────────────────╯")

        return 0

    except ImportError as e:
        print(f"[MEMORY] M-gent not available: {e}")
        return 1
    except Exception as e:
        print(f"[MEMORY] Error: {e}")
        return 1


def _show_from_ghost() -> int:
    """Read memory status from ghost cache."""
    from protocols.cli.hollow import find_kgents_root

    project_root = find_kgents_root()
    if project_root is None:
        project_root = Path.cwd()

    ghost_dir = project_root / ".kgents" / "ghost"
    memory_path = ghost_dir / "memory_summary.json"

    if not memory_path.exists():
        print("[MEMORY] No ghost cache found")
        print("  Run 'kg ghost' first to project memory state.")
        return 1

    try:
        data = json.loads(memory_path.read_text())

        print("[MEMORY] Four Pillars (from ghost cache)")
        print()

        # Health
        health = data.get("health", {})
        if health:
            status = health.get("status", "UNKNOWN")
            score = health.get("health_score", 0)
            print(f"Status:    {status} ({score:.0%})")
            print(f"Crystal:   {health.get('crystal_health', 0):.0%}")
            print(f"Field:     {health.get('field_health', 0):.0%}")
            print(f"Inference: {health.get('inference_health', 0):.0%}")

        # Crystal
        crystal = data.get("crystal", {})
        if crystal:
            print()
            print(
                f"Crystal: {crystal.get('concept_count', 0)} concepts, "
                f"{crystal.get('hot_count', 0)} hot"
            )

        # Field
        field = data.get("field", {})
        if field:
            print(
                f"Field: {field.get('trace_count', 0)} traces, "
                f"decay {field.get('decay_rate', 0):.0%}/hr"
            )

        # Inference
        inference = data.get("inference", {})
        if inference:
            print(
                f"Inference: precision {inference.get('precision', 0):.1f}, "
                f"entropy {inference.get('entropy', 0):.1f}"
            )

        return 0

    except json.JSONDecodeError as e:
        print(f"[MEMORY] Invalid ghost cache: {e}")
        return 1
    except Exception as e:
        print(f"[MEMORY] Error reading ghost cache: {e}")
        return 1
