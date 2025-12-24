"""
Integration operations: streaming, NOW.md updates, Brain promotion.

Provides:
- cmd_stream: Stream crystal events in real-time
- cmd_propose_now: Propose NOW.md updates from crystals
- cmd_promote: Promote crystals to Brain
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from .base import _bootstrap_and_run, _get_console


def cmd_stream(args: list[str]) -> int:
    """
    Stream crystal events in real-time.

    Usage:
        kg witness stream                    # Stream all crystals
        kg witness stream --level 0          # Only session crystals
        kg witness stream --level 1          # Only day crystals
    """
    level: int | None = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--level" and i + 1 < len(args):
            try:
                level = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            i += 1

    console = _get_console()

    if console:
        console.print("[bold]Crystal Stream[/bold] (Ctrl+C to stop)")
        console.print("[dim]" + "─" * 40 + "[/dim]")
    else:
        print("Crystal Stream (Ctrl+C to stop)")
        print("─" * 40)

    async def run_stream() -> None:
        from services.witness.stream import stream_crystals_cli

        try:
            async for event in stream_crystals_cli(level=level, include_initial=True):
                if console:
                    console.print(f"  {event}")
                else:
                    print(f"  {event}")
        except asyncio.CancelledError:
            pass

    try:
        asyncio.run(run_stream())
    except KeyboardInterrupt:
        if console:
            console.print("\n[dim]Stream stopped.[/dim]")
        else:
            print("\nStream stopped.")

    return 0


def cmd_propose_now(args: list[str]) -> int:
    """
    Propose updates to NOW.md based on recent crystals.

    Usage:
        kg witness propose-now               # Show proposals
        kg witness propose-now --apply       # Apply proposals (with backup)
        kg witness propose-now --json        # JSON output
    """
    json_output = "--json" in args
    apply = "--apply" in args
    console = _get_console()

    async def run_propose() -> dict[str, Any]:
        from pathlib import Path

        from services.witness.integration import apply_now_proposal, propose_now_update

        proposals = await propose_now_update()

        if not proposals:
            return {"message": "No proposals generated (no recent crystals)"}

        result = {
            "proposals": [p.to_dict() for p in proposals],
        }

        if apply:
            now_path = Path.cwd() / "NOW.md"
            applied = []
            for p in proposals:
                success = apply_now_proposal(p, now_path)
                applied.append({"section": p.section, "success": success})
            result["applied"] = applied

        return result

    try:
        result = asyncio.run(_bootstrap_and_run(run_propose))

        if json_output:
            print(json.dumps(result))
            return 0

        if "message" in result:
            if console:
                console.print(f"[dim]{result['message']}[/dim]")
            else:
                print(result["message"])
            return 0

        # Pretty print proposals
        from services.witness.integration import propose_now_update

        async def get_proposals_formatted() -> list[str]:
            proposals = await propose_now_update()
            return [p.format_diff() for p in proposals]

        formatted = asyncio.run(_bootstrap_and_run(get_proposals_formatted))

        for diff in formatted:
            if console:
                console.print(diff)
                console.print()
            else:
                print(diff)
                print()

        if "applied" in result:
            if console:
                console.print("[green]✓ Proposals applied[/green]")
            else:
                print("✓ Proposals applied")

        return 0

    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
        return 1


def cmd_promote(args: list[str]) -> int:
    """
    Promote a crystal to Brain as a TeachingCrystal.

    Usage:
        kg witness promote <crystal_id>      # Promote specific crystal
        kg witness promote --auto            # Auto-promote top candidates
        kg witness promote --candidates      # List promotion candidates
        kg witness promote --json            # JSON output
    """
    json_output = "--json" in args
    auto_mode = "--auto" in args
    show_candidates = "--candidates" in args
    console = _get_console()

    # Find crystal_id argument
    crystal_id = None
    for arg in args:
        if not arg.startswith("-"):
            crystal_id = arg
            break

    if show_candidates:
        # List promotion candidates
        from services.witness.integration import identify_promotion_candidates

        candidates = identify_promotion_candidates()

        if json_output:
            print(json.dumps([c.to_dict() for c in candidates[:10]]))
            return 0

        if not candidates:
            if console:
                console.print("[dim]No promotion candidates found.[/dim]")
            else:
                print("No promotion candidates found.")
            return 0

        if console:
            console.print("\n[bold]Promotion Candidates[/bold]")
            console.print("[dim]" + "─" * 60 + "[/dim]")
        else:
            print("\nPromotion Candidates")
            print("─" * 60)

        for i, c in enumerate(candidates[:10], 1):
            insight_short = (
                c.crystal.insight[:50] + "..." if len(c.crystal.insight) > 50 else c.crystal.insight
            )
            if console:
                console.print(f"  {i}. [cyan]{c.crystal.id[:12]}...[/cyan] (score: {c.score:.2f})")
                console.print(f"     {insight_short}")
                console.print(f"     [dim]{', '.join(c.reasons[:2])}[/dim]")
            else:
                print(f"  {i}. {c.crystal.id[:12]}... (score: {c.score:.2f})")
                print(f"     {insight_short}")

        return 0

    if auto_mode:
        # Auto-promote top candidates
        async def run_auto_promote() -> list[dict[str, Any]]:
            from services.witness.integration import auto_promote_crystals

            return await auto_promote_crystals(limit=3)

        try:
            results = asyncio.run(_bootstrap_and_run(run_auto_promote))

            if json_output:
                print(json.dumps(results))
                return 0

            for r in results:
                if r.get("success"):
                    if console:
                        console.print(f"[green]✓[/green] Promoted {r['crystal_id'][:12]}...")
                    else:
                        print(f"✓ Promoted {r['crystal_id'][:12]}...")
                else:
                    if console:
                        console.print(f"[red]✗[/red] Failed: {r.get('error', 'unknown')}")
                    else:
                        print(f"✗ Failed: {r.get('error', 'unknown')}")

            return 0
        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}))
            else:
                print(f"Error: {e}")
            return 1

    if not crystal_id:
        print("Usage: kg witness promote <crystal_id> [--json]")
        print("       kg witness promote --auto")
        print("       kg witness promote --candidates")
        return 1

    # Promote specific crystal
    async def run_promote() -> dict[str, Any]:
        from services.witness.crystal import CrystalId
        from services.witness.integration import promote_to_brain

        return await promote_to_brain(CrystalId(crystal_id))

    try:
        result = asyncio.run(_bootstrap_and_run(run_promote))

        if json_output:
            print(json.dumps(result))
        else:
            if result.get("success"):
                if console:
                    console.print("[green]✓ Crystal promoted to Brain[/green]")
                    console.print(f"  {result.get('message', '')}")
                else:
                    print("✓ Crystal promoted to Brain")
                    print(f"  {result.get('message', '')}")
            else:
                if console:
                    console.print(
                        f"[red]✗ Promotion failed: {result.get('error', 'unknown')}[/red]"
                    )
                else:
                    print(f"✗ Promotion failed: {result.get('error', 'unknown')}")

        return 0 if result.get("success") else 1
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")
        return 1


__all__ = [
    "cmd_stream",
    "cmd_propose_now",
    "cmd_promote",
]
