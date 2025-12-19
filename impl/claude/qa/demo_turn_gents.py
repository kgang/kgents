#!/usr/bin/env python3
"""
Demo script for Turn-gents Protocol.

Showcases:
1. Turn types (SPEECH, ACTION, THOUGHT, YIELD, SILENCE)
2. Causal cones and context projection
3. Yield governance and approval flow
4. Turn economics (order/surplus budgets)
5. TurnDAGRenderer visualization

Run with:
    uv run python qa/demo_turn_gents.py

Or in TUI mode:
    uv run python qa/demo_turn_gents.py --tui
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from weave import (
    ApprovalStrategy,
    CausalCone,
    TheWeave,
    Turn,
    TurnBudgetTracker,
    TurnType,
    YieldHandler,
    YieldTurn,
    compute_cone_stats,
)
from weave.economics import BudgetPolicy

console = Console()


def demo_turn_types() -> None:
    """Demonstrate the five turn types."""
    console.print("\n[bold cyan]1. The Five Turn Types[/bold cyan]")
    console.print("=" * 60)

    weave = TheWeave()

    # Create one of each turn type
    turns = [
        Turn.create_turn(
            content="Hello, I'm ready to help you analyze the codebase.",
            source="k-gent",
            turn_type=TurnType.SPEECH,
            confidence=0.95,
        ),
        Turn.create_turn(
            content="world.grep.invoke('TODO', path='src/')",
            source="k-gent",
            turn_type=TurnType.ACTION,
            confidence=0.88,
            entropy_cost=0.05,
        ),
        Turn.create_turn(
            content="The user might want me to focus on high-priority TODOs first...",
            source="k-gent",
            turn_type=TurnType.THOUGHT,
            confidence=0.72,
        ),
        Turn.create_turn(
            content="Silence while awaiting user response",
            source="k-gent",
            turn_type=TurnType.SILENCE,
            confidence=1.0,
        ),
    ]

    # Add to weave with dependencies
    prev_id = None
    for turn in turns:
        deps = {prev_id} if prev_id else None
        weave.monoid.append_mut(turn, deps)
        prev_id = turn.id

    # Display table
    table = Table(title="Turn Types in the Weave")
    table.add_column("Type", style="cyan")
    table.add_column("Content", style="white")
    table.add_column("Confidence", justify="right")
    table.add_column("Observable", justify="center")

    for turn in turns:
        observable = "[green]Yes[/]" if turn.is_observable() else "[dim]No[/]"
        content = (
            str(turn.content)[:40] + "..." if len(str(turn.content)) > 40 else str(turn.content)
        )
        table.add_row(
            turn.turn_type.name,
            content,
            f"{turn.confidence:.0%}",
            observable,
        )

    console.print(table)
    console.print(f"\n[dim]Total turns in weave: {len(weave)}[/dim]")


def demo_causal_cones() -> None:
    """Demonstrate causal cone projection."""
    console.print("\n[bold cyan]2. Causal Cones: Context is a Light Cone[/bold cyan]")
    console.print("=" * 60)

    weave = TheWeave()

    # Create two independent threads (agent-a and agent-b)
    # that later merge

    # Agent A's thread
    a1 = Turn.create_turn(
        content="Starting analysis...",
        source="agent-a",
        turn_type=TurnType.SPEECH,
    )
    a2 = Turn.create_turn(
        content="Found interesting pattern",
        source="agent-a",
        turn_type=TurnType.SPEECH,
    )

    # Agent B's independent thread
    b1 = Turn.create_turn(
        content="Checking documentation...",
        source="agent-b",
        turn_type=TurnType.SPEECH,
    )
    b2 = Turn.create_turn(
        content="Docs confirm the approach",
        source="agent-b",
        turn_type=TurnType.SPEECH,
    )

    # Add to weave
    weave.monoid.append_mut(a1, None)
    weave.monoid.append_mut(a2, {a1.id})
    weave.monoid.append_mut(b1, None)  # Independent!
    weave.monoid.append_mut(b2, {b1.id})

    # Merge point: agent-a sees both threads
    merge = Turn.create_turn(
        content="Combining analysis and docs...",
        source="agent-a",
        turn_type=TurnType.ACTION,
    )
    weave.monoid.append_mut(merge, {a2.id, b2.id})

    # Create cone
    cone = CausalCone(weave)

    # Show cones for each agent
    console.print("\n[yellow]Agent A's causal cone:[/yellow]")
    context_a = cone.project_context("agent-a")
    for event in context_a:
        if isinstance(event, Turn):
            console.print(
                f"  [{event.source}] {event.turn_type.name}: {str(event.content)[:40]}..."
            )

    console.print("\n[yellow]Agent B's causal cone:[/yellow]")
    context_b = cone.project_context("agent-b")
    for event in context_b:
        if isinstance(event, Turn):
            console.print(
                f"  [{event.source}] {event.turn_type.name}: {str(event.content)[:40]}..."
            )

    # Show statistics
    stats_a = compute_cone_stats(cone, "agent-a")
    stats_b = compute_cone_stats(cone, "agent-b")

    console.print(
        f"\n[dim]Agent A cone size: {stats_a.cone_size} (compression: {stats_a.compression_ratio:.0%})[/dim]"
    )
    console.print(
        f"[dim]Agent B cone size: {stats_b.cone_size} (compression: {stats_b.compression_ratio:.0%})[/dim]"
    )
    console.print(f"[dim]Total weave size: {len(weave)}[/dim]")


async def demo_yield_governance() -> None:
    """Demonstrate YIELD turn approval flow."""
    console.print("\n[bold cyan]3. Yield Governance: Preserving Human Agency[/bold cyan]")
    console.print("=" * 60)

    handler = YieldHandler(default_strategy=ApprovalStrategy.ALL)

    # Create a yield turn requesting approval
    yield_turn = YieldTurn.create_yield(
        content="rm -rf /tmp/test_data",
        source="file-agent",
        yield_reason="Destructive operation requires approval",
        required_approvers={"k-gent", "human"},
        confidence=0.6,
        entropy_cost=0.2,
    )

    console.print("\n[yellow]Yield Turn Created:[/yellow]")
    console.print(f"  Content: {yield_turn.content}")
    console.print(f"  Reason: {yield_turn.yield_reason}")
    console.print(f"  Required approvers: {set(yield_turn.required_approvers)}")
    console.print(f"  Confidence: {yield_turn.confidence:.0%}")

    # Simulate approval flow
    async def approval_flow():
        # Start the approval request (don't await - we'll simulate approvals)
        task = asyncio.create_task(handler.request_approval(yield_turn, timeout=5.0))

        # Simulate k-gent approving after 0.5s
        await asyncio.sleep(0.5)
        console.print("\n[green]k-gent approves...[/green]")
        await handler.approve(yield_turn.id, "k-gent")

        # Show pending state
        pending = handler.get_pending(yield_turn.id)
        if pending:
            console.print(f"  Approved by: {set(pending.approved_by)}")
            console.print(f"  Pending: {set(pending.pending_approvers())}")

        # Simulate human approving after another 0.5s
        await asyncio.sleep(0.5)
        console.print("\n[green]human approves...[/green]")
        await handler.approve(yield_turn.id, "human")

        # Get result
        result = await task
        return result

    result = await approval_flow()

    console.print(f"\n[bold]Result: {result.status.name}[/bold]")
    if result.is_approved:
        console.print("[green]Action may proceed.[/green]")


def demo_turn_economics() -> None:
    """Demonstrate the two-budget system."""
    console.print("\n[bold cyan]4. Turn Economics: The Accursed Share[/bold cyan]")
    console.print("=" * 60)

    # Create tracker with default 10% surplus
    tracker = TurnBudgetTracker(order_budget=1.0, surplus_fraction=0.1)

    console.print("\n[yellow]Initial budgets:[/yellow]")
    stats = tracker.stats()
    console.print(f"  Order budget: {stats.order_total:.2f}")
    console.print(f"  Surplus budget: {stats.surplus_total:.2f} (10% of order)")

    # Simulate production turns
    console.print("\n[yellow]Production turns (order budget):[/yellow]")
    for i in range(5):
        cost = 0.15
        success = tracker.consume(cost, reason=f"Production turn {i + 1}")
        status = "[green]OK[/]" if success else "[red]OVER BUDGET[/]"
        console.print(f"  Turn {i + 1}: cost {cost:.2f} - {status}")

    # Show remaining
    stats = tracker.stats()
    console.print(f"\n  Order remaining: {stats.order_remaining:.2f}")

    # Simulate exploration turns
    console.print("\n[yellow]Exploration turns (surplus budget):[/yellow]")
    for i in range(3):
        cost = 0.03
        success = tracker.consume(cost, is_oblique=True, reason=f"Exploration {i + 1}")
        status = "[green]OK[/]" if success else "[red]OVER BUDGET[/]"
        console.print(f"  Oblique turn {i + 1}: cost {cost:.2f} - {status}")

    # Final stats
    stats = tracker.stats()
    console.print("\n[yellow]Final state:[/yellow]")
    console.print(f"  Order spent: {stats.order_spent:.2f} / {stats.order_total:.2f}")
    console.print(f"  Surplus spent: {stats.surplus_spent:.2f} / {stats.surplus_total:.2f}")
    console.print(f"  Exploration ratio: {stats.exploration_ratio:.0%}")

    # Check policy
    policy = BudgetPolicy(minimum_exploration_ratio=0.05)
    if policy.should_encourage_exploration(stats):
        console.print("\n[yellow]Policy suggests: more exploration needed![/yellow]")
    else:
        console.print("\n[green]Exploration ratio is healthy.[/green]")


def demo_turn_dag_rendering() -> None:
    """Demonstrate TurnDAGRenderer visualization."""
    console.print("\n[bold cyan]5. Turn DAG Visualization[/bold cyan]")
    console.print("=" * 60)

    from agents.i.screens.turn_dag import TurnDAGConfig, TurnDAGRenderer

    weave = TheWeave()

    # Create a multi-agent conversation
    turns = [
        Turn.create_turn(
            content="Let me analyze this file...",
            source="k-gent",
            turn_type=TurnType.SPEECH,
            confidence=0.9,
        ),
        Turn.create_turn(
            content="world.grep.invoke('pattern')",
            source="k-gent",
            turn_type=TurnType.ACTION,
            confidence=0.85,
            entropy_cost=0.02,
        ),
        Turn.create_turn(
            content="Hmm, this pattern appears 47 times...",
            source="k-gent",
            turn_type=TurnType.THOUGHT,
            confidence=0.7,
        ),
        Turn.create_turn(
            content="Found 47 matches across 12 files.",
            source="k-gent",
            turn_type=TurnType.SPEECH,
            confidence=0.88,
        ),
    ]

    prev_id = None
    for turn in turns:
        deps = {prev_id} if prev_id else None
        weave.monoid.append_mut(turn, deps)
        prev_id = turn.id

    # Render with thoughts collapsed (default)
    config = TurnDAGConfig(show_thoughts=False)
    renderer = TurnDAGRenderer(weave=weave, config=config)

    console.print("\n[yellow]Turn DAG (thoughts collapsed):[/yellow]")
    panel = renderer.render(agent_id="k-gent")
    console.print(panel)

    # Render stats
    console.print("\n[yellow]Statistics:[/yellow]")
    stats = renderer.render_stats()
    console.print(stats)

    # Demonstrate fork capability
    console.print("\n[yellow]Fork Capability:[/yellow]")
    console.print(f"  Original weave size: {len(weave)}")
    forked = renderer.fork_from(turns[1].id)
    console.print(f"  Forked from turn 2, new weave size: {len(forked)}")


def demo_integration_synergies() -> None:
    """Show integration opportunities with other systems."""
    console.print("\n[bold cyan]6. Integration Synergies[/bold cyan]")
    console.print("=" * 60)

    tree = Tree("[bold]Turn-gents Integration Points[/bold]")

    # Memory integration
    memory = tree.add("[cyan]self/memory (M-gent)[/cyan]")
    memory.add("Phase 7: Causal Weave Integration")
    memory.add("CausalConeAgent for memory access patterns")
    memory.add("Stigmergic traces as SPEECH turns")

    # Dashboard integration
    dashboard = tree.add("[cyan]interfaces/dashboard-overhaul[/cyan]")
    dashboard.add("Debugger Screen (LOD 2) uses TurnDAGRenderer")
    dashboard.add("Causal cone visualization in Cockpit")
    dashboard.add("YIELD queue panel for approval workflow")

    # Polynomial agents
    poly = tree.add("[cyan]polynomial-agent[/cyan]")
    poly.add("Polynomial state changes emit Turns")
    poly.add("State hashes link Turn pre/post states")
    poly.add("Valid inputs drive SPEECH/ACTION types")

    # K-gent integration
    kgent = tree.add("[cyan]agents/k-gent[/cyan]")
    kgent.add("Soul intercept generates YIELD turns")
    kgent.add("Governance via TurnBasedCapability Halo")
    kgent.add("Context projection via CausalCone")

    console.print(tree)


async def main():
    """Run all demos."""
    console.print(
        Panel.fit(
            "[bold magenta]Turn-gents Protocol Demo[/bold magenta]\n"
            "[dim]The Chronos-Kairos Protocol for Agent Governance[/dim]",
            border_style="magenta",
        )
    )

    demo_turn_types()
    demo_causal_cones()
    await demo_yield_governance()
    demo_turn_economics()
    demo_turn_dag_rendering()
    demo_integration_synergies()

    console.print("\n" + "=" * 60)
    console.print("[bold green]Demo complete![/bold green]")
    console.print("\nTotal Turn-gents tests: 187")
    console.print("Files: weave/turn.py, weave/causal_cone.py, weave/yield_handler.py,")
    console.print("       weave/economics.py, agents/i/screens/turn_dag.py")


if __name__ == "__main__":
    asyncio.run(main())
