#!/usr/bin/env python3
"""
Agent Foundry Showcase: Complexity Management & Safety Guarantees

This demo illustrates the brilliant architecture of kgents' Agent Foundry:
the orchestrator that synthesizes JIT intelligence with Alethic Projection.

                    THE FOUNDRY PIPELINE
    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │  Intent ─► Reality ─► Generate ─► Validate ─► Select ─► Project ─► Cache
    │            Classifier   (if needed)  Stability   Target     Compile   LRU
    │                                                             │
    │  DETERMINISTIC ───────────────────────► LOCAL/CLI           │
    │  PROBABILISTIC ─► MetaArchitect ─────► Context-dependent    │
    │  CHAOTIC ────────────────────────────► WASM (forced!)       │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘

Key Guarantees Demonstrated:
1. SAFETY: Chaotic/unstable code → WASM sandbox (unconditional)
2. EFFICIENCY: LRU cache with (intent, context) hash
3. COMPOSITION: Projectors compose via >> operator
4. TRANSPARENCY: 8-state polynomial with observable transitions

Run:
    cd impl/claude
    uv run python demos/foundry_showcase.py

The demo runs entirely locally - no API keys needed.
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any

# Rich console for beautiful output
try:
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.tree import Tree

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Add path for imports
sys.path.insert(0, str(__file__).rsplit("/demos/", 1)[0])

from agents.j import Reality, Target
from services.foundry import (
    FOUNDRY_OPERAD,
    FOUNDRY_POLYNOMIAL,
    AgentFoundry,
    EphemeralAgentCache,
    ForgeRequest,
    FoundryState,
)

# =============================================================================
# Demo Configuration
# =============================================================================


@dataclass
class DemoScenario:
    """A scenario demonstrating Foundry behavior."""

    name: str
    intent: str
    context: dict[str, Any]
    description: str
    expected_reality: str
    expected_target: str


SCENARIOS = [
    DemoScenario(
        name="Deterministic Tool",
        intent="parse this JSON data",
        context={},
        description="Simple, bounded task → LOCAL execution (no generation needed)",
        expected_reality="DETERMINISTIC",
        expected_target="local",
    ),
    DemoScenario(
        name="Probabilistic Agent",
        intent="analyze sentiment and extract key themes from customer feedback",
        context={"interactive": True},
        description="Complex analysis → MetaArchitect generates agent → MARIMO (interactive)",
        expected_reality="PROBABILISTIC",
        expected_target="marimo",
    ),
    DemoScenario(
        name="Chaotic Reality",
        intent="do everything forever and continuously expand capabilities",
        context={},
        description="Unbounded scope → CHAOTIC → WASM sandbox (FORCED for safety)",
        expected_reality="CHAOTIC",
        expected_target="wasm",
    ),
    DemoScenario(
        name="Production Context",
        intent="process incoming webhook data with validation",
        context={"production": True},
        description="Production flag → K8S target for container orchestration",
        expected_reality="PROBABILISTIC",
        expected_target="k8s",
    ),
    DemoScenario(
        name="Cache Hit Demo",
        intent="parse this JSON data",  # Same as first scenario
        context={},
        description="Identical (intent, context) → cache hit → instant return",
        expected_reality="DETERMINISTIC",
        expected_target="local",
    ),
]


# =============================================================================
# Plain Output (fallback when Rich not available)
# =============================================================================


def print_plain_header() -> None:
    """Print header without Rich."""
    print("\n" + "=" * 70)
    print("  AGENT FOUNDRY SHOWCASE")
    print("  Complexity Management & Safety Guarantees")
    print("=" * 70 + "\n")


def print_plain_architecture() -> None:
    """Print architecture diagram without Rich."""
    print("THE FOUNDRY PIPELINE:")
    print("-" * 50)
    print("Intent → Reality → Generate → Validate → Select → Project → Cache")
    print("         Classifier  (if needed) Stability   Target    Compile   LRU")
    print()
    print("Reality Classification:")
    print("  DETERMINISTIC ────────────────► LOCAL/CLI")
    print("  PROBABILISTIC → MetaArchitect ► Context-dependent")
    print("  CHAOTIC ──────────────────────► WASM (forced!)")
    print("-" * 50 + "\n")


def print_plain_scenario(idx: int, scenario: DemoScenario, response: Any) -> None:
    """Print scenario result without Rich."""
    print(f"\n{'─' * 60}")
    print(f"SCENARIO {idx}: {scenario.name}")
    print(f"{'─' * 60}")
    print(f'Intent: "{scenario.intent}"')
    print(f"Context: {scenario.context or '{}'}")
    print(f"\nDescription: {scenario.description}")
    print()
    print(f"  Reality:  {response.reality:<15} (expected: {scenario.expected_reality})")
    print(f"  Target:   {response.target:<15} (expected: {scenario.expected_target})")
    print(f"  Forced:   {response.forced}")
    print(f"  Cached:   {'Yes' if response.cache_key else 'No'}")
    print(f"  Artifact: {response.artifact_type}")

    # Check expectations
    reality_match = response.reality.upper() == scenario.expected_reality
    target_match = response.target == scenario.expected_target
    status = "✓" if (reality_match and target_match) else "✗"
    print(f"\n  Status: {status} {'PASS' if status == '✓' else 'UNEXPECTED'}")


def print_plain_polynomial() -> None:
    """Print polynomial structure without Rich."""
    print("\n" + "=" * 60)
    print("POLYNOMIAL STATE MACHINE")
    print("=" * 60)
    for state in FoundryState:
        inputs = FOUNDRY_POLYNOMIAL.valid_inputs(state)
        input_names = ", ".join(e.name for e in inputs) if inputs else "—"
        print(f"  {state.name:<12} accepts: {input_names}")


def print_plain_operad() -> None:
    """Print operad operations without Rich."""
    print("\n" + "=" * 60)
    print("FOUNDRY OPERAD (Composition Grammar)")
    print("=" * 60)
    for name, op in FOUNDRY_OPERAD.operations.items():
        print(f"  {name:<12} arity={op.arity}")
    print("\nLaws:")
    for law in FOUNDRY_OPERAD.laws:
        print(f"  - {law}")


def print_plain_cache_stats(foundry: AgentFoundry) -> None:
    """Print cache statistics without Rich."""
    manifest = foundry.manifest()
    print("\n" + "=" * 60)
    print("CACHE STATISTICS")
    print("=" * 60)
    print(f"  Total Forges:   {manifest.total_forges}")
    print(f"  Cache Hits:     {manifest.cache_hits}")
    print(f"  Hit Rate:       {manifest.cache_hit_rate:.1%}")
    print(f"  Cache Size:     {manifest.cache_size}")


# =============================================================================
# Rich Output (when available)
# =============================================================================


def print_rich_header(console: Console) -> None:
    """Print beautiful header with Rich."""
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]AGENT FOUNDRY SHOWCASE[/]\n"
            "[dim]Complexity Management & Safety Guarantees[/]",
            border_style="cyan",
            padding=(1, 4),
        )
    )
    console.print()


def print_rich_architecture(console: Console) -> None:
    """Print architecture diagram with Rich."""
    tree = Tree("[bold yellow]The Foundry Pipeline[/]")

    stage1 = tree.add("[cyan]Intent[/] → Natural language task description")
    stage1.add("[dim]Example: 'analyze sentiment in customer feedback'[/]")

    stage2 = tree.add("[cyan]Reality Classifier[/] → Categorize task complexity")
    stage2.add("[green]DETERMINISTIC[/] — Bounded, predictable (e.g., parse JSON)")
    stage2.add("[yellow]PROBABILISTIC[/] — Requires reasoning (e.g., analyze text)")
    stage2.add("[red]CHAOTIC[/] — Unbounded, unpredictable (e.g., 'do everything')")

    stage3 = tree.add("[cyan]MetaArchitect[/] → Generate agent source (if PROBABILISTIC)")
    stage3.add("[dim]LLM-powered code synthesis with Halo inference[/]")

    stage4 = tree.add("[cyan]Chaosmonger[/] → Validate stability")
    stage4.add("[dim]Static analysis: loops, recursion, state size[/]")

    stage5 = tree.add("[cyan]Target Selector[/] → Choose execution environment")
    stage5.add("[green]LOCAL[/] — In-process (trusted)")
    stage5.add("[blue]CLI[/] — Subprocess script")
    stage5.add("[magenta]MARIMO[/] — Interactive notebook")
    stage5.add("[yellow]DOCKER[/] — Container isolation")
    stage5.add("[cyan]K8S[/] — Orchestrated deployment")
    stage5.add("[red]WASM[/] — Browser sandbox (FORCED for chaotic)")

    stage6 = tree.add("[cyan]Projector[/] → Compile to target format")
    stage6.add("[dim]Same semantics, different runtimes[/]")

    stage7 = tree.add("[cyan]Cache[/] → LRU with TTL")
    stage7.add("[dim]Key: SHA256(intent, context)[/]")

    console.print(Panel(tree, title="[bold]Architecture[/]", border_style="blue"))
    console.print()


def print_rich_scenario(
    console: Console,
    idx: int,
    scenario: DemoScenario,
    response: Any,
) -> None:
    """Print scenario result with Rich."""
    # Reality color
    reality_colors = {
        "DETERMINISTIC": "green",
        "PROBABILISTIC": "yellow",
        "CHAOTIC": "red",
    }
    reality = response.reality.upper()
    reality_color = reality_colors.get(reality, "white")

    # Target color
    target_colors = {
        "local": "green",
        "cli": "blue",
        "docker": "yellow",
        "k8s": "cyan",
        "wasm": "red",
        "marimo": "magenta",
    }
    target_color = target_colors.get(response.target, "white")

    # Build table
    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    table.add_column("Property", style="dim")
    table.add_column("Value")

    table.add_row("Intent", f'[italic]"{scenario.intent}"[/]')
    table.add_row("Context", str(scenario.context) if scenario.context else "[dim]{}[/]")
    table.add_row("", "")
    table.add_row(
        "Reality", f"[{reality_color}]{reality}[/] [dim](expected: {scenario.expected_reality})[/]"
    )
    table.add_row(
        "Target",
        f"[{target_color}]{response.target}[/] [dim](expected: {scenario.expected_target})[/]",
    )
    table.add_row("Forced", "[red]Yes — Safety Required[/]" if response.forced else "[dim]No[/]")
    table.add_row(
        "Cache Key", f"[dim]{response.cache_key[:12]}...[/]" if response.cache_key else "[dim]—[/]"
    )
    table.add_row("Artifact Type", response.artifact_type)

    # Check match
    reality_match = reality == scenario.expected_reality
    target_match = response.target == scenario.expected_target
    if reality_match and target_match:
        status = "[bold green]✓ PASS[/]"
    else:
        status = "[bold red]✗ UNEXPECTED[/]"

    panel_title = f"[bold]Scenario {idx}: {scenario.name}[/]"
    subtitle = f"{scenario.description} — {status}"

    console.print(
        Panel(
            table,
            title=panel_title,
            subtitle=f"[dim]{subtitle}[/]",
            border_style="blue" if reality_match and target_match else "red",
        )
    )
    console.print()


def print_rich_polynomial(console: Console) -> None:
    """Print polynomial structure with Rich."""
    table = Table(
        title="[bold]Polynomial State Machine[/]",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column("State", style="yellow")
    table.add_column("Terminal?")
    table.add_column("Valid Inputs")

    for state in FoundryState:
        inputs = FOUNDRY_POLYNOMIAL.valid_inputs(state)
        input_names = ", ".join(f"[dim]{e.name}[/]" for e in inputs) if inputs else "—"
        terminal = "[green]Yes[/]" if state.is_terminal else "[dim]No[/]"
        table.add_row(state.name, terminal, input_names)

    console.print(table)
    console.print()


def print_rich_operad(console: Console) -> None:
    """Print operad with Rich."""
    table = Table(
        title="[bold]Foundry Operad (Composition Grammar)[/]",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column("Operation", style="yellow")
    table.add_column("Arity")
    table.add_column("Description", style="dim")

    descriptions = {
        "forge": "Intent → Artifact",
        "inspect": "AgentName → Halo + Capabilities",
        "promote": "CacheKey → PermanentAgent",
        "cache_get": "CacheKey → CacheEntry | None",
        "cache_list": "→ list[CacheEntry]",
    }

    for name, op in FOUNDRY_OPERAD.operations.items():
        desc = descriptions.get(name, "")
        table.add_row(name, str(op.arity), desc)

    console.print(table)

    # Laws
    console.print("\n[bold cyan]Composition Laws:[/]")
    for law in FOUNDRY_OPERAD.laws:
        console.print(f"  [dim]•[/] {law}")
    console.print()


def print_rich_cache_stats(console: Console, foundry: AgentFoundry) -> None:
    """Print cache statistics with Rich."""
    manifest = foundry.manifest()

    table = Table(
        title="[bold]Cache Statistics[/]",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column("Metric", style="yellow")
    table.add_column("Value", justify="right")

    table.add_row("Total Forges", str(manifest.total_forges))
    table.add_row("Cache Hits", str(manifest.cache_hits))
    table.add_row("Hit Rate", f"{manifest.cache_hit_rate:.1%}")
    table.add_row("Cache Size", str(manifest.cache_size))
    table.add_row("Status", f"[green]{manifest.status}[/]")

    console.print(table)
    console.print()


def print_rich_safety_guarantee(console: Console) -> None:
    """Print the safety guarantee prominently."""
    console.print(
        Panel.fit(
            "[bold red]SAFETY GUARANTEE[/]\n\n"
            "[yellow]CHAOTIC reality[/] or [yellow]unstable code[/] → "
            "[red bold]WASM sandbox (FORCED)[/]\n\n"
            "[dim]No exceptions. No overrides. Browser sandbox = battle-tested isolation.[/]",
            border_style="red",
            padding=(1, 4),
        )
    )
    console.print()


# =============================================================================
# Main Demo
# =============================================================================


async def run_demo() -> None:
    """Run the full Foundry showcase."""
    console = Console() if RICH_AVAILABLE else None

    # Header
    if console:
        print_rich_header(console)
        print_rich_architecture(console)
    else:
        print_plain_header()
        print_plain_architecture()

    # Create Foundry
    foundry = AgentFoundry()

    # Run scenarios
    if console:
        console.print("[bold]Running Scenarios...[/]\n")
    else:
        print("Running Scenarios...\n")

    for idx, scenario in enumerate(SCENARIOS, 1):
        request = ForgeRequest(
            intent=scenario.intent,
            context=scenario.context,
        )

        response = await foundry.forge(request)

        if console:
            print_rich_scenario(console, idx, scenario, response)
        else:
            print_plain_scenario(idx, scenario, response)

    # Safety guarantee callout
    if console:
        print_rich_safety_guarantee(console)
    else:
        print("\n" + "!" * 60)
        print("SAFETY GUARANTEE:")
        print("CHAOTIC reality or unstable code → WASM sandbox (FORCED)")
        print("No exceptions. No overrides.")
        print("!" * 60 + "\n")

    # Polynomial structure
    if console:
        print_rich_polynomial(console)
    else:
        print_plain_polynomial()

    # Operad structure
    if console:
        print_rich_operad(console)
    else:
        print_plain_operad()

    # Cache stats
    if console:
        print_rich_cache_stats(console, foundry)
    else:
        print_plain_cache_stats(foundry)

    # Summary
    if console:
        console.print(
            Panel.fit(
                "[bold green]Demo Complete![/]\n\n"
                "[dim]The Agent Foundry provides:[/]\n"
                "  [cyan]•[/] Reality classification for task complexity\n"
                "  [cyan]•[/] Target selection based on safety requirements\n"
                "  [cyan]•[/] Automatic WASM sandboxing for chaotic agents\n"
                "  [cyan]•[/] LRU caching with (intent, context) hashing\n"
                "  [cyan]•[/] Polynomial state machine for observable progress\n"
                "  [cyan]•[/] Operad grammar for lawful composition",
                border_style="green",
                padding=(1, 4),
            )
        )
    else:
        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print("\nThe Agent Foundry provides:")
        print("  • Reality classification for task complexity")
        print("  • Target selection based on safety requirements")
        print("  • Automatic WASM sandboxing for chaotic agents")
        print("  • LRU caching with (intent, context) hashing")
        print("  • Polynomial state machine for observable progress")
        print("  • Operad grammar for lawful composition")


def main() -> None:
    """Entry point."""
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
