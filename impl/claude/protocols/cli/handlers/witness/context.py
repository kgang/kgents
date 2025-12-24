"""
Context operations: budget-aware crystal context retrieval.

Provides:
- cmd_context: Get budget-aware context from crystals
"""

from __future__ import annotations

import json
from typing import Any

from .base import _get_console


def cmd_context(args: list[str]) -> int:
    """
    Get budget-aware context from crystals.

    Usage:
        kg witness context                    # Default budget (2000 tokens)
        kg witness context --budget 1000      # Tighter budget
        kg witness context --query "topic"    # Relevance-weighted
        kg witness context --json             # For agents
    """
    budget = 2000
    query: str | None = None
    recency_weight = 0.7
    json_output = "--json" in args

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--json":
            i += 1
        elif arg in ("--budget", "-b") and i + 1 < len(args):
            try:
                budget = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif arg in ("--query", "-q") and i + 1 < len(args):
            query = args[i + 1]
            i += 2
        elif arg == "--recency-weight" and i + 1 < len(args):
            try:
                recency_weight = float(args[i + 1])
                recency_weight = max(0.0, min(1.0, recency_weight))
            except ValueError:
                pass
            i += 2
        else:
            i += 1

    console = _get_console()

    try:
        from services.witness.context import get_context_sync

        result = get_context_sync(
            budget_tokens=budget,
            recency_weight=recency_weight,
            relevance_query=query,
        )

        if json_output:
            print(json.dumps(result.to_dict()))
            return 0

        if not result.items:
            if console:
                console.print(
                    "[dim]No crystals found. Use 'kg witness crystallize' to create some.[/dim]"
                )
            else:
                print("No crystals found. Use 'kg witness crystallize' to create some.")
            return 0

        # Pretty print
        if console:
            console.print("\n[bold]Context Query[/bold]")
            console.print("[dim]" + "─" * 60 + "[/dim]")
            console.print(
                f"  Budget: {budget} tokens | Used: {result.total_tokens} | Remaining: {result.budget_remaining}"
            )
            if query:
                console.print(f'  Query: "{query}"')
            console.print(f"  Recency weight: {recency_weight:.1f}")
            console.print()
        else:
            print("\nContext Query")
            print("─" * 60)
            print(
                f"  Budget: {budget} tokens | Used: {result.total_tokens} | Remaining: {result.budget_remaining}"
            )
            if query:
                print(f'  Query: "{query}"')
            print()

        for item in result.items:
            crystal = item.crystal
            try:
                dt = crystal.crystallized_at
                if hasattr(dt, "strftime"):
                    ts_str = dt.strftime("%Y-%m-%d %H:%M")
                else:
                    ts_str = str(dt)
            except (ValueError, AttributeError):
                ts_str = "???"

            insight_short = (
                crystal.insight[:55] + "..." if len(crystal.insight) > 55 else crystal.insight
            )

            if console:
                score_str = f"[dim](score: {item.score:.2f})[/dim]"
                console.print(
                    f"  [cyan]{crystal.level.name}[/cyan] "
                    f"[dim]{ts_str}[/dim]  "
                    f"~{item.tokens} tok  "
                    f"{score_str}"
                )
                console.print(f"         {insight_short}")
            else:
                print(
                    f"  {crystal.level.name} {ts_str}  ~{item.tokens} tok  (score: {item.score:.2f})"
                )
                print(f"         {insight_short}")

        if console:
            console.print()
            console.print(
                f"[dim]Cumulative: {result.total_tokens}/{budget} tokens ({len(result.items)} crystals)[/dim]"
            )
            console.print()
        else:
            print()
            print(
                f"Cumulative: {result.total_tokens}/{budget} tokens ({len(result.items)} crystals)"
            )
            print()

        return 0
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
        return 1


async def cmd_context_async(args: list[str]) -> int:
    """
    Async version of cmd_context for use within async context.

    Usage:
        kg witness context                    # Default budget (2000 tokens)
        kg witness context --budget 1000      # Tighter budget
        kg witness context --query "topic"    # Relevance-weighted
        kg witness context --json             # For agents
    """
    budget = 2000
    query: str | None = None
    recency_weight = 0.7
    json_output = "--json" in args

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--json":
            i += 1
        elif arg in ("--budget", "-b") and i + 1 < len(args):
            try:
                budget = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif arg in ("--query", "-q") and i + 1 < len(args):
            query = args[i + 1]
            i += 2
        elif arg == "--recency-weight" and i + 1 < len(args):
            try:
                recency_weight = float(args[i + 1])
                recency_weight = max(0.0, min(1.0, recency_weight))
            except ValueError:
                pass
            i += 2
        else:
            i += 1

    console = _get_console()

    try:
        from services.witness.context import get_context

        result = await get_context(
            budget_tokens=budget,
            recency_weight=recency_weight,
            relevance_query=query,
        )

        if json_output:
            print(json.dumps(result.to_dict()))
            return 0

        if not result.items:
            if console:
                console.print(
                    "[dim]No crystals found. Use 'kg witness crystallize' to create some.[/dim]"
                )
            else:
                print("No crystals found. Use 'kg witness crystallize' to create some.")
            return 0

        # Pretty print
        if console:
            console.print("\n[bold]Context Query[/bold]")
            console.print("[dim]" + "─" * 60 + "[/dim]")
            console.print(
                f"  Budget: {budget} tokens | Used: {result.total_tokens} | Remaining: {result.budget_remaining}"
            )
            if query:
                console.print(f'  Query: "{query}"')
            console.print(f"  Recency weight: {recency_weight:.1f}")
            console.print()
        else:
            print("\nContext Query")
            print("─" * 60)
            print(
                f"  Budget: {budget} tokens | Used: {result.total_tokens} | Remaining: {result.budget_remaining}"
            )
            if query:
                print(f'  Query: "{query}"')
            print()

        for item in result.items:
            crystal = item.crystal
            try:
                dt = crystal.crystallized_at
                if hasattr(dt, "strftime"):
                    ts_str = dt.strftime("%Y-%m-%d %H:%M")
                else:
                    ts_str = str(dt)
            except (ValueError, AttributeError):
                ts_str = "???"

            insight_short = (
                crystal.insight[:55] + "..." if len(crystal.insight) > 55 else crystal.insight
            )

            if console:
                score_str = f"[dim](score: {item.score:.2f})[/dim]"
                console.print(
                    f"  [cyan]{crystal.level.name}[/cyan] "
                    f"[dim]{ts_str}[/dim]  "
                    f"~{item.tokens} tok  "
                    f"{score_str}"
                )
                console.print(f"         {insight_short}")
            else:
                print(
                    f"  {crystal.level.name} {ts_str}  ~{item.tokens} tok  (score: {item.score:.2f})"
                )
                print(f"         {insight_short}")

        if console:
            console.print()
            console.print(
                f"[dim]Cumulative: {result.total_tokens}/{budget} tokens ({len(result.items)} crystals)[/dim]"
            )
            console.print()
        else:
            print()
            print(
                f"Cumulative: {result.total_tokens}/{budget} tokens ({len(result.items)} crystals)"
            )
            print()

        return 0
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
        return 1


__all__ = ["cmd_context", "cmd_context_async"]
