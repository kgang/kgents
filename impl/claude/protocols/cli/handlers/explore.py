"""
Explore Handler: Exploration Harness CLI Interface

A thin routing shim for the exploration harness, providing CLI access to:
- Budget management (bounded exploration)
- Loop detection (prevent spinning)
- Evidence collection (exploration creates proof)
- Commitment protocol (claims require evidence)

AGENTESE Path Mapping:
    kg explore               -> self.explore.manifest  (current state)
    kg explore start <path>  -> self.explore.start     (new exploration)
    kg explore navigate <e>  -> self.explore.navigate  (follow edge)
    kg explore budget        -> self.explore.budget    (budget status)
    kg explore evidence      -> self.explore.evidence  (collected evidence)
    kg explore trail         -> self.explore.trail     (navigation trail)
    kg explore commit <c>    -> self.explore.commit    (commit claim)
    kg explore loops         -> self.explore.loops     (loop status)
    kg explore reset         -> self.explore.reset     (fresh start)

Usage:
    kg explore                           # Where am I? What's the state?
    kg explore start world.brain.core    # Start exploration at path
    kg explore navigate tests            # Follow [tests] hyperedge
    kg explore budget                    # Show budget breakdown
    kg explore evidence                  # Show collected evidence
    kg explore trail                     # Show navigation history
    kg explore commit "claim" --level moderate  # Commit a claim
    kg explore reset                     # Start fresh

Philosophy:
    "The harness doesn't constrain—it witnesses.
     Every trail is evidence. Every exploration creates proof obligations."

See: spec/protocols/exploration-harness.md
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from protocols.cli.handler_meta import handler

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# =============================================================================
# Help Text
# =============================================================================

HELP_TEXT = """\
\033[1mkg explore\033[0m - Exploration Harness CLI

\033[1mUSAGE:\033[0m
  kg explore                          Show current exploration state
  kg explore start <path>             Start new exploration at path
  kg explore navigate <edge>          Navigate via hyperedge
  kg explore budget                   Show budget breakdown
  kg explore evidence                 Show collected evidence
  kg explore trail                    Show navigation trail
  kg explore commit "<claim>"         Commit a claim based on evidence
  kg explore loops                    Show loop detection status
  kg explore reset                    Reset to fresh state

\033[1mOPTIONS:\033[0m
  --preset <name>                     Budget preset: quick, standard, thorough
  --level <level>                     Commitment level: tentative, moderate, strong
  --json                              Output as JSON (for agent consumption)

\033[1mBUDGET PRESETS:\033[0m
  quick       10 steps, depth 3, 5s timeout (fast exploration)
  standard    50 steps, depth 10, 30s timeout (default)
  thorough    200 steps, depth 20, 120s timeout (deep exploration)

\033[1mCOMMITMENT LEVELS:\033[0m
  tentative   1+ evidence → "I observed X"
  moderate    3+ evidence, 1+ strong → "Evidence suggests X"
  strong      5+ evidence, 2+ strong, no counter → "X is likely true"

\033[1mEXAMPLES:\033[0m
  $ kg explore start world.brain.core       # Begin at brain.core
  $ kg explore navigate tests               # Find test files
  $ kg explore evidence                     # What have we found?
  $ kg explore commit "core implements PolyAgent" --level moderate
  $ kg explore --json                       # Machine-readable output

\033[1mPRINCIPLE:\033[0m
  "The harness doesn't constrain—it witnesses.
   Every trail is evidence. Every exploration creates proof obligations."
"""


# =============================================================================
# State Management (Singleton)
# =============================================================================

# Module-level singleton for session persistence
_active_harness: Any = None


def get_or_create_harness(start_path: str | None = None, preset: str = "standard") -> Any:
    """Get existing harness or create a new one."""
    global _active_harness

    if _active_harness is None or start_path:
        from protocols.exploration import create_harness
        from protocols.exploration.budget import quick_budget, standard_budget, thorough_budget
        from protocols.exploration.types import ContextNode

        # Select budget preset
        budget_fn = {
            "quick": quick_budget,
            "standard": standard_budget,
            "thorough": thorough_budget,
        }.get(preset, standard_budget)

        # Create start node
        path = start_path or "root"
        holon = path.split(".")[-1] if "." in path else path
        node = ContextNode(path=path, holon=holon)

        _active_harness = create_harness(node, budget=budget_fn())

    return _active_harness


def reset_harness() -> None:
    """Clear the active harness."""
    global _active_harness
    _active_harness = None


def has_active_harness() -> bool:
    """Check if there's an active exploration."""
    return _active_harness is not None


# =============================================================================
# Console Helpers
# =============================================================================


def _get_console() -> Any:
    """Get Rich console for pretty output."""
    try:
        from rich.console import Console

        return Console()
    except ImportError:
        return None


def _print_header(text: str) -> None:
    """Print a styled header."""
    console = _get_console()
    if console:
        console.print(f"\n[bold]{text}[/bold]")
        console.print("[dim]" + "─" * 50 + "[/dim]")
    else:
        print(f"\n{text}")
        print("─" * 50)


def _progress_bar(current: int | float, total: int | float, width: int = 10) -> str:
    """Create a simple ASCII progress bar."""
    if total == 0:
        pct = 0.0
    else:
        pct = current / total
    filled = int(pct * width)
    empty = width - filled
    return "[" + "█" * filled + "░" * empty + "]"


def _run_async(coro: Any) -> Any:
    """Run async coroutine synchronously."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# =============================================================================
# Subcommand Handlers
# =============================================================================


def _handle_status(args: list[str], json_output: bool = False) -> int:
    """Show current exploration state."""
    console = _get_console()

    if not has_active_harness():
        if json_output:
            print(
                json.dumps(
                    {"status": "no_exploration", "hint": "Use 'kg explore start <path>'"}, indent=2
                )
            )
        else:
            _print_header("🔍 Exploration State")
            msg = "No active exploration. Start one with: kg explore start <path>"
            if console:
                console.print(f"[dim]{msg}[/dim]")
            else:
                print(msg)
        return 0

    harness = get_or_create_harness()
    state = harness.get_state()

    if json_output:
        output = {
            "focus": [n.path for n in harness.focus],
            "trail_steps": state.steps_taken,
            "evidence_count": state.evidence_count,
            "strong_evidence": state.strong_evidence_count,
            "budget_remaining": state.budget_remaining,
            "loop_warnings": state.loop_warnings,
            "halted": harness.is_halted,
        }
        print(json.dumps(output, indent=2))
        return 0

    _print_header("🔍 Exploration State")

    # Focus
    focus_paths = [n.path for n in harness.focus]
    focus_str = ", ".join(focus_paths) if focus_paths else "(none)"

    # Trail summary
    trail = harness.trail
    trail_str = f"{len(trail.steps)} steps"
    if len(trail.steps) > 1:
        first = trail.steps[0].node_path
        last = trail.steps[-1].node_path
        trail_str += f" ({first} → ... → {last})"

    # Evidence summary
    evidence_str = f"{state.evidence_count} items"
    if state.strong_evidence_count > 0:
        weak = state.evidence_count - state.strong_evidence_count
        evidence_str = (
            f"{state.evidence_count} items ({state.strong_evidence_count} strong, {weak} weak)"
        )

    # Budget summary
    remaining = state.budget_remaining
    budget_pct = 100 - int(remaining.get("used_pct", 0) * 100) if "used_pct" in remaining else 100

    if console:
        console.print(f"  [bold]Focus:[/bold]       {focus_str}")
        console.print(f"  [bold]Trail:[/bold]       {trail_str}")
        console.print(f"  [bold]Evidence:[/bold]    {evidence_str}")
        console.print(f"  [bold]Budget:[/bold]      ~{budget_pct}% remaining")
        console.print(f"  [bold]Loops:[/bold]       {state.loop_warnings} warnings")
        if harness.is_halted:
            console.print("  [bold red]HALTED[/bold red]")
    else:
        print(f"  Focus:       {focus_str}")
        print(f"  Trail:       {trail_str}")
        print(f"  Evidence:    {evidence_str}")
        print(f"  Budget:      ~{budget_pct}% remaining")
        print(f"  Loops:       {state.loop_warnings} warnings")
        if harness.is_halted:
            print("  [HALTED]")

    print()
    return 0


def _handle_start(args: list[str], preset: str = "standard") -> int:
    """Start a new exploration at given path."""
    console = _get_console()

    # Extract path from args
    path = None
    for arg in args:
        if not arg.startswith("-") and arg != "start":
            path = arg
            break

    if not path:
        print("Usage: kg explore start <path>")
        print("Example: kg explore start world.brain.core")
        return 1

    # Reset and create new harness
    reset_harness()
    harness = get_or_create_harness(path, preset=preset)

    _print_header("🚀 Exploration Started")

    if console:
        console.print(f"  [bold]Path:[/bold]    {path}")
        console.print(f"  [bold]Preset:[/bold]  {preset}")
        console.print()
        console.print("[dim]Commands:[/dim]")
        console.print("  kg explore navigate <edge>   Follow a hyperedge")
        console.print("  kg explore budget            Show budget status")
        console.print("  kg explore evidence          Show evidence collected")
    else:
        print(f"  Path:    {path}")
        print(f"  Preset:  {preset}")
        print()
        print("Commands:")
        print("  kg explore navigate <edge>   Follow a hyperedge")
        print("  kg explore budget            Show budget status")
        print("  kg explore evidence          Show evidence collected")

    print()
    return 0


def _handle_navigate(args: list[str]) -> int:
    """Navigate via hyperedge."""
    console = _get_console()

    if not has_active_harness():
        print("No active exploration. Start one with: kg explore start <path>")
        return 1

    # Extract edge from args
    edge = None
    for arg in args:
        if not arg.startswith("-") and arg != "navigate":
            edge = arg
            break

    if not edge:
        print("Usage: kg explore navigate <edge>")
        print("Common edges: tests, imports, contains, parent, related")
        return 1

    harness = get_or_create_harness()
    result = _run_async(harness.navigate(edge))

    if result.success:
        _print_header(f"🧭 Navigated: [{edge}]")

        focus_paths = [n.path for n in harness.focus]
        focus_str = ", ".join(focus_paths) if focus_paths else "(none)"

        if console:
            console.print(f"  [bold]New focus:[/bold] {focus_str}")
            if result.loop_detected:
                console.print(f"  [yellow]⚠ Loop detected: {result.loop_detected.name}[/yellow]")
                console.print(f"  [dim]{result.error_message}[/dim]")
        else:
            print(f"  New focus: {focus_str}")
            if result.loop_detected:
                print(f"  ⚠ Loop detected: {result.loop_detected.name}")
                print(f"  {result.error_message}")
    else:
        if console:
            console.print(f"[red]✗ Navigation failed: {result.error_message}[/red]")
        else:
            print(f"✗ Navigation failed: {result.error_message}")
        return 1

    print()
    return 0


def _handle_budget(args: list[str], json_output: bool = False) -> int:
    """Show detailed budget breakdown."""
    console = _get_console()

    if not has_active_harness():
        if json_output:
            print(json.dumps({"error": "no_exploration"}, indent=2))
        else:
            print("No active exploration. Start one with: kg explore start <path>")
        return 1

    harness = get_or_create_harness()
    budget = harness.budget
    remaining = budget.remaining()

    if json_output:
        output = {
            "steps": {"used": budget.steps_taken, "max": budget.max_steps},
            "nodes": {"visited": len(budget.nodes_visited), "max": budget.max_nodes},
            "depth": {"current": budget.current_depth, "max": budget.max_depth},
            "time_ms": {"elapsed": budget._elapsed_ms(), "max": budget.time_budget_ms},
            "can_navigate": budget.can_navigate(),
            "exhaustion_reason": budget.exhaustion_reason().value
            if budget.exhaustion_reason()
            else None,
        }
        print(json.dumps(output, indent=2))
        return 0

    _print_header("📊 Navigation Budget")

    # Steps
    steps_pct = budget.steps_taken / budget.max_steps if budget.max_steps > 0 else 0
    bar = _progress_bar(budget.steps_taken, budget.max_steps)

    # Nodes
    nodes_visited = len(budget.nodes_visited)
    nodes_pct = nodes_visited / budget.max_nodes if budget.max_nodes > 0 else 0
    nodes_bar = _progress_bar(nodes_visited, budget.max_nodes)

    # Depth
    depth_pct = budget.current_depth / budget.max_depth if budget.max_depth > 0 else 0
    depth_bar = _progress_bar(budget.current_depth, budget.max_depth)

    # Time
    elapsed = budget._elapsed_ms()
    time_pct = elapsed / budget.time_budget_ms if budget.time_budget_ms > 0 else 0
    time_bar = _progress_bar(elapsed, budget.time_budget_ms)

    if console:
        console.print(
            f"  Steps:       {budget.steps_taken:3d} / {budget.max_steps:3d}      {bar} {int(steps_pct * 100):3d}%"
        )
        console.print(
            f"  Nodes:       {nodes_visited:3d} / {budget.max_nodes:3d}      {nodes_bar} {int(nodes_pct * 100):3d}%"
        )
        console.print(
            f"  Depth:       {budget.current_depth:3d} / {budget.max_depth:3d}      {depth_bar} {int(depth_pct * 100):3d}%"
        )
        console.print(
            f"  Time (ms):   {int(elapsed):5d} / {budget.time_budget_ms:5d}  {time_bar} {int(time_pct * 100):3d}%"
        )
        console.print()

        # Exhaustion warning
        if not budget.can_navigate():
            reason = budget.exhaustion_reason()
            console.print(
                f"  [red bold]⚠ BUDGET EXHAUSTED: {reason.value if reason else 'unknown'}[/red bold]"
            )
        else:
            # Risk assessment
            max_pct = max(steps_pct, nodes_pct, depth_pct, time_pct)
            if max_pct > 0.8:
                console.print("  [yellow]Exhaustion Risk: HIGH[/yellow]")
            elif max_pct > 0.5:
                console.print("  [dim]Exhaustion Risk: MEDIUM[/dim]")
            else:
                console.print("  [green]Exhaustion Risk: LOW[/green]")
    else:
        print(
            f"  Steps:       {budget.steps_taken:3d} / {budget.max_steps:3d}      {bar} {int(steps_pct * 100):3d}%"
        )
        print(
            f"  Nodes:       {nodes_visited:3d} / {budget.max_nodes:3d}      {nodes_bar} {int(nodes_pct * 100):3d}%"
        )
        print(
            f"  Depth:       {budget.current_depth:3d} / {budget.max_depth:3d}      {depth_bar} {int(depth_pct * 100):3d}%"
        )
        print(
            f"  Time (ms):   {int(elapsed):5d} / {budget.time_budget_ms:5d}  {time_bar} {int(time_pct * 100):3d}%"
        )

    print()
    return 0


def _handle_evidence(args: list[str], json_output: bool = False) -> int:
    """Show collected evidence."""
    console = _get_console()

    if not has_active_harness():
        if json_output:
            print(json.dumps({"error": "no_exploration"}, indent=2))
        else:
            print("No active exploration. Start one with: kg explore start <path>")
        return 1

    harness = get_or_create_harness()
    summary = harness.get_evidence_summary()

    if json_output:
        # Access the internal evidence list
        evidence_list = harness.evidence_collector._evidence
        output = {
            "total": summary.total_count,
            "strong": summary.strong_count,
            "moderate": summary.moderate_count,
            "weak": summary.weak_count,
            "evidence": [
                {
                    "content": e.content,
                    "strength": e.strength.value,
                    "node_path": e.metadata.get("node_path", "unknown"),
                }
                for e in evidence_list
            ],
        }
        print(json.dumps(output, indent=2))
        return 0

    _print_header(f"📋 Evidence ({summary.total_count} items)")

    if summary.total_count == 0:
        if console:
            console.print("[dim]No evidence collected yet. Navigate to gather evidence.[/dim]")
        else:
            print("No evidence collected yet. Navigate to gather evidence.")
        print()
        return 0

    # Group by strength
    evidence_list = harness.evidence_collector._evidence

    from protocols.exploration.types import EvidenceStrength

    strong = [e for e in evidence_list if e.strength == EvidenceStrength.STRONG]
    moderate = [e for e in evidence_list if e.strength == EvidenceStrength.MODERATE]
    weak = [e for e in evidence_list if e.strength == EvidenceStrength.WEAK]

    if console:
        if strong:
            console.print(f"\n  [bold green]STRONG ({len(strong)}):[/bold green]")
            for e in strong[:5]:  # Limit display
                console.print(f"    ✓ {e.content[:60]}...")
                node = e.metadata.get("node_path", "unknown")
                console.print(f"      [dim]└─ from {node}[/dim]")

        if moderate:
            console.print(f"\n  [bold yellow]MODERATE ({len(moderate)}):[/bold yellow]")
            for e in moderate[:5]:
                console.print(f"    ○ {e.content[:60]}...")

        if weak:
            console.print(f"\n  [dim]WEAK ({len(weak)}):[/dim]")
            for e in weak[:3]:
                console.print(f"    · {e.content[:50]}...")

        # Commitment potential
        console.print("\n  [bold]Commitment Potential:[/bold]")
        console.print(f"    TENTATIVE:  {'✓' if summary.total_count >= 1 else '✗'} (1+ evidence)")
        console.print(
            f"    MODERATE:   {'✓' if summary.total_count >= 3 and summary.strong_count >= 1 else '✗'} (3+ evidence, 1+ strong)"
        )
        console.print(
            f"    STRONG:     {'✓' if summary.total_count >= 5 and summary.strong_count >= 2 else '✗'} (5+ evidence, 2+ strong)"
        )
    else:
        print(f"\n  STRONG ({len(strong)}): {len(strong)} items")
        print(f"  MODERATE ({len(moderate)}): {len(moderate)} items")
        print(f"  WEAK ({len(weak)}): {len(weak)} items")

    print()
    return 0


def _handle_trail(args: list[str], json_output: bool = False) -> int:
    """Show navigation trail."""
    console = _get_console()

    if not has_active_harness():
        if json_output:
            print(json.dumps({"error": "no_exploration"}, indent=2))
        else:
            print("No active exploration. Start one with: kg explore start <path>")
        return 1

    harness = get_or_create_harness()
    trail = harness.trail

    if json_output:
        output = {
            "id": trail.id,
            "created_by": trail.created_by,
            "steps": [
                {"node": s.node, "edge_taken": s.edge_taken, "timestamp": s.timestamp.isoformat()}
                for s in trail.steps
            ],
        }
        print(json.dumps(output, indent=2))
        return 0

    _print_header(f"📍 Navigation Trail ({len(trail.steps)} steps)")

    if not trail.steps:
        if console:
            console.print("[dim]No steps yet.[/dim]")
        else:
            print("No steps yet.")
        print()
        return 0

    for i, step in enumerate(trail.steps):
        edge_str = f" ─[{step.edge_taken}]→" if step.edge_taken else ""
        prefix = "└─" if i == len(trail.steps) - 1 else "├─"

        if console:
            if i == len(trail.steps) - 1:
                console.print(f"  {prefix} [bold]{step.node}[/bold] [dim](current)[/dim]")
            else:
                console.print(f"  {prefix} {step.node}{edge_str}")
        else:
            marker = " (current)" if i == len(trail.steps) - 1 else ""
            print(f"  {prefix} {step.node}{edge_str}{marker}")

    print()
    return 0


def _handle_commit(args: list[str], level: str = "moderate") -> int:
    """Attempt to commit a claim."""
    console = _get_console()

    if not has_active_harness():
        print("No active exploration. Start one with: kg explore start <path>")
        return 1

    # Extract claim from args (everything after 'commit' that's not a flag)
    claim_parts = []
    for arg in args:
        if arg == "commit":
            continue
        if arg.startswith("-"):
            break
        claim_parts.append(arg)

    claim_text = " ".join(claim_parts)
    if not claim_text:
        print('Usage: kg explore commit "<claim>" [--level tentative|moderate|strong]')
        print('Example: kg explore commit "brain.core implements PolyAgent pattern"')
        return 1

    # Remove quotes if present
    claim_text = claim_text.strip("'\"")

    # Map level string to enum
    from protocols.exploration.types import Claim, CommitmentLevel

    level_map = {
        "tentative": CommitmentLevel.TENTATIVE,
        "moderate": CommitmentLevel.MODERATE,
        "strong": CommitmentLevel.STRONG,
        "definitive": CommitmentLevel.DEFINITIVE,
    }
    commitment_level = level_map.get(level.lower(), CommitmentLevel.MODERATE)

    harness = get_or_create_harness()
    claim = Claim(statement=claim_text)
    result = _run_async(harness.commit_claim(claim, commitment_level))

    if result.approved:
        _print_header("✓ Claim Committed")

        if console:
            console.print(f'  [bold]Claim:[/bold]    "{claim_text}"')
            console.print(f"  [bold]Level:[/bold]    {commitment_level.value.upper()}")
            console.print(
                f"  [bold]Evidence:[/bold] {result.evidence_count} items ({result.strong_count} strong)"
            )
            console.print()
            console.print("[green]The claim is now recorded with commitment level.[/green]")
        else:
            print(f'  Claim:    "{claim_text}"')
            print(f"  Level:    {commitment_level.value.upper()}")
            print(f"  Evidence: {result.evidence_count} items ({result.strong_count} strong)")
    else:
        if console:
            console.print(f"[red]✗ Commitment Failed: {result.message}[/red]")
            console.print()
            console.print(f"  [bold]Requested level:[/bold] {commitment_level.value}")
            console.print(
                f"  [bold]Evidence:[/bold]        {result.evidence_count} items ({result.strong_count} strong)"
            )
            console.print()
            console.print("[dim]Gather more evidence or try a lower commitment level.[/dim]")
        else:
            print(f"✗ Commitment Failed: {result.message}")
            print(f"  Requested level: {commitment_level.value}")
            print(f"  Evidence: {result.evidence_count} items ({result.strong_count} strong)")
        return 1

    print()
    return 0


def _handle_loops(args: list[str], json_output: bool = False) -> int:
    """Show loop detection status."""
    console = _get_console()

    if not has_active_harness():
        if json_output:
            print(json.dumps({"error": "no_exploration"}, indent=2))
        else:
            print("No active exploration. Start one with: kg explore start <path>")
        return 1

    harness = get_or_create_harness()
    detector = harness.loop_detector
    state = harness.get_state()

    if json_output:
        output = {
            "warnings": state.loop_warnings,
            "halted": harness.is_halted,
            "halt_reason": harness._halt_reason,
            "path_history_size": len(detector._path_history),
            "loop_counts": len(detector._loop_counts),
        }
        print(json.dumps(output, indent=2))
        return 0

    _print_header("🔄 Loop Detection Status")

    if console:
        console.print(f"  [bold]Warnings:[/bold]        {state.loop_warnings}")
        console.print(f"  [bold]Halted:[/bold]          {'Yes' if harness.is_halted else 'No'}")
        if harness.is_halted:
            console.print(f"  [bold red]Halt reason:[/bold red]    {harness._halt_reason}")
        console.print(f"  [bold]Path history:[/bold]    {len(detector._path_history)} entries")
        console.print(f"  [bold]Loop occurrences:[/bold] {len(detector._loop_counts)} tracked")
    else:
        print(f"  Warnings:        {state.loop_warnings}")
        print(f"  Halted:          {'Yes' if harness.is_halted else 'No'}")
        if harness.is_halted:
            print(f"  Halt reason:     {harness._halt_reason}")
        print(f"  Path history:    {len(detector._path_history)} entries")
        print(f"  Loop occurrences: {len(detector._loop_counts)} tracked")

    print()
    return 0


def _handle_reset(args: list[str]) -> int:
    """Reset exploration state."""
    console = _get_console()

    reset_harness()

    _print_header("🔄 Exploration Reset")

    if console:
        console.print("[green]✓[/green] Exploration state cleared.")
        console.print("[dim]Start a new exploration with: kg explore start <path>[/dim]")
    else:
        print("✓ Exploration state cleared.")
        print("Start a new exploration with: kg explore start <path>")

    print()
    return 0


# =============================================================================
# Main Entry Point
# =============================================================================


@handler("explore", is_async=False, tier=1, description="Exploration harness")
def cmd_explore(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Exploration harness CLI interface.

    Routes to appropriate subcommand handler based on first argument.
    """
    # Parse help flag
    if "--help" in args or "-h" in args:
        print(HELP_TEXT)
        return 0

    # Parse global flags
    json_output = "--json" in args
    args = [a for a in args if a != "--json"]

    preset = "standard"
    for i, arg in enumerate(args):
        if arg == "--preset" and i + 1 < len(args):
            preset = args[i + 1]
            args = args[:i] + args[i + 2 :]
            break
        elif arg.startswith("--preset="):
            preset = arg.split("=", 1)[1]
            args = [a for a in args if not a.startswith("--preset=")]
            break

    level = "moderate"
    for i, arg in enumerate(args):
        if arg == "--level" and i + 1 < len(args):
            level = args[i + 1]
            args = args[:i] + args[i + 2 :]
            break
        elif arg.startswith("--level="):
            level = arg.split("=", 1)[1]
            args = [a for a in args if not a.startswith("--level=")]
            break

    # Parse subcommand
    subcommand = "status"
    if args:
        first_arg = args[0].lower()
        if first_arg in (
            "start",
            "navigate",
            "budget",
            "evidence",
            "trail",
            "commit",
            "loops",
            "reset",
        ):
            subcommand = first_arg

    # Route to handler
    handlers: dict[str, Callable[[], int]] = {
        "status": lambda: _handle_status(args, json_output),
        "start": lambda: _handle_start(args, preset),
        "navigate": lambda: _handle_navigate(args),
        "budget": lambda: _handle_budget(args, json_output),
        "evidence": lambda: _handle_evidence(args, json_output),
        "trail": lambda: _handle_trail(args, json_output),
        "commit": lambda: _handle_commit(args, level),
        "loops": lambda: _handle_loops(args, json_output),
        "reset": lambda: _handle_reset(args),
    }

    handler = handlers.get(subcommand, lambda: _handle_status(args, json_output))
    return handler()


__all__ = ["cmd_explore"]
