"""
Gestalt CLI Handler: Hypothesis-Driven Codebase Research.

concept.gestalt + self.jewel.gestalt.flow.research.* enables tree-of-thought
exploration of architectural questions.

Usage:
    kg gestalt                        # Show research state
    kg gestalt explore <question>     # Start exploring a question
    kg gestalt branch <hypothesis>    # Branch with new hypothesis
    kg gestalt tree                   # Show hypothesis tree
    kg gestalt synthesize             # Synthesize findings
    kg gestalt reset                  # Clear research state
    kg gestalt codebase               # Quick codebase overview

Phase 4: Crown Jewel + ResearchFlow Integration

AGENTESE Paths:
    self.jewel.gestalt.flow.research.manifest     # Research state
    self.jewel.gestalt.flow.research.explore      # Start exploration
    self.jewel.gestalt.flow.research.branch       # Add hypothesis
    self.jewel.gestalt.flow.research.tree         # Show tree
    self.jewel.gestalt.flow.research.synthesize   # Synthesize

See: spec/f-gents/research.md
"""

from __future__ import annotations

import asyncio
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# Rich imports for beautiful output (graceful degradation)
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.tree import Tree

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None  # type: ignore[assignment]

# Path display for Foundation 1
from protocols.cli.path_display import (
    apply_path_flags,
    display_path_header,
    parse_path_flags,
)

# =============================================================================
# Research State Management
# =============================================================================


@dataclass
class Hypothesis:
    """A single hypothesis in the research tree."""

    id: str
    content: str
    parent_id: str | None
    depth: int
    status: str  # "open", "confirmed", "refuted", "pending"
    evidence: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchState:
    """State for the current research exploration."""

    question: str | None = None
    hypotheses: list[Hypothesis] = field(default_factory=list)
    current_focus_id: str | None = None
    started_at: datetime | None = None
    synthesis: str | None = None


# Module-level state (thread-safe)
_research_state: ResearchState | None = None
_state_lock = threading.Lock()


def _get_state() -> ResearchState:
    """Get or create research state (thread-safe)."""
    global _research_state
    if _research_state is None:
        with _state_lock:
            if _research_state is None:
                _research_state = ResearchState()
    return _research_state


def _reset_state() -> None:
    """Reset research state."""
    global _research_state
    with _state_lock:
        _research_state = ResearchState()


# =============================================================================
# Async Helpers
# =============================================================================


def _run_async(coro: Any) -> Any:
    """Run an async coroutine synchronously."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# =============================================================================
# Output Helpers
# =============================================================================


def _emit(message: str, data: dict[str, Any], ctx: "InvocationContext | None") -> None:
    """Emit output to console and optional context."""
    if ctx is not None:
        ctx.output(message, data)
    else:
        print(message)


def _print_help() -> None:
    """Print help for gestalt command."""
    print(__doc__)


# =============================================================================
# Research Commands
# =============================================================================


async def _show_status(ctx: "InvocationContext | None", json_output: bool = False) -> int:
    """Show current research status."""
    display_path_header(
        path="self.jewel.gestalt.flow.research.manifest",
        aspect="manifest",
        effects=["RESEARCH_STATE_DISPLAYED"],
    )

    state = _get_state()

    if json_output:
        import json

        print(
            json.dumps(
                {
                    "question": state.question,
                    "hypothesis_count": len(state.hypotheses),
                    "current_focus": state.current_focus_id,
                    "has_synthesis": state.synthesis is not None,
                    "started_at": state.started_at.isoformat() if state.started_at else None,
                },
                indent=2,
            )
        )
        return 0

    if not state.question:
        if RICH_AVAILABLE:
            console.print(
                Panel(
                    "[dim]No active research exploration.[/]\n\n"
                    'Start one with: [cyan]kg gestalt explore "your question here"[/]',
                    title="Gestalt Research",
                    border_style="dim",
                )
            )
        else:
            _emit(
                'No active research. Start with: kg gestalt explore "<question>"',
                {},
                ctx,
            )
        return 0

    if RICH_AVAILABLE:
        console.print(f"\n[bold green]Research:[/] {state.question}")
        console.print(f"[dim]Hypotheses: {len(state.hypotheses)}[/]")
        if state.current_focus_id:
            focus = next((h for h in state.hypotheses if h.id == state.current_focus_id), None)
            if focus:
                console.print(f"[bold]Focus:[/] {focus.content[:60]}...")
        console.print("\n[dim]Use 'kg gestalt tree' to see hypothesis tree[/]")
    else:
        _emit(f"Research: {state.question}", {"question": state.question}, ctx)
        _emit(
            f"Hypotheses: {len(state.hypotheses)}",
            {"count": len(state.hypotheses)},
            ctx,
        )

    return 0


async def _explore(
    args: list[str], ctx: "InvocationContext | None", json_output: bool = False
) -> int:
    """Start exploring a new question."""
    display_path_header(
        path="self.jewel.gestalt.flow.research.explore",
        aspect="define",
        effects=["EXPLORATION_STARTED", "ROOT_HYPOTHESIS_CREATED"],
    )

    if not args:
        _emit("Error: question is required", {"error": "missing_question"}, ctx)
        print('Usage: kg gestalt explore "What patterns exist in the codebase?"')
        return 1

    question = " ".join(args).strip()
    if not question:
        _emit("Error: question cannot be empty", {"error": "empty_question"}, ctx)
        return 1

    state = _get_state()

    # Create root hypothesis
    root_id = str(uuid4())[:8]
    root = Hypothesis(
        id=root_id,
        content=f"Initial hypothesis for: {question}",
        parent_id=None,
        depth=0,
        status="open",
    )

    # Update state
    state.question = question
    state.hypotheses = [root]
    state.current_focus_id = root_id
    state.started_at = datetime.now()
    state.synthesis = None

    if json_output:
        import json

        print(
            json.dumps(
                {
                    "status": "exploring",
                    "question": question,
                    "root_hypothesis_id": root_id,
                },
                indent=2,
            )
        )
    else:
        if RICH_AVAILABLE:
            console.print(
                Panel(
                    f"[bold]Question:[/] {question}\n\n"
                    f"[dim]Root hypothesis created. Use:[/]\n"
                    f'  [cyan]kg gestalt branch "Your hypothesis"[/] - add a branch\n'
                    f"  [cyan]kg gestalt tree[/] - see the hypothesis tree\n"
                    f"  [cyan]kg gestalt synthesize[/] - synthesize findings",
                    title="Research Started",
                    border_style="green",
                )
            )
        else:
            _emit(f"Exploring: {question}", {"question": question}, ctx)
            _emit(f"Root hypothesis created: {root_id}", {"root_id": root_id}, ctx)

    return 0


async def _branch(
    args: list[str], ctx: "InvocationContext | None", json_output: bool = False
) -> int:
    """Add a new hypothesis branch."""
    display_path_header(
        path="self.jewel.gestalt.flow.research.branch",
        aspect="define",
        effects=["HYPOTHESIS_BRANCHED"],
    )

    state = _get_state()

    if not state.question:
        _emit("Error: no active exploration", {"error": "no_exploration"}, ctx)
        print('Start one with: kg gestalt explore "<question>"')
        return 1

    if not args:
        _emit("Error: hypothesis is required", {"error": "missing_hypothesis"}, ctx)
        print('Usage: kg gestalt branch "The architecture uses layered patterns"')
        return 1

    hypothesis_text = " ".join(args).strip()
    if not hypothesis_text:
        _emit("Error: hypothesis cannot be empty", {"error": "empty_hypothesis"}, ctx)
        return 1

    # Find parent (current focus or root)
    parent_id = state.current_focus_id
    if parent_id:
        parent = next((h for h in state.hypotheses if h.id == parent_id), None)
        parent_depth = parent.depth if parent else 0
    else:
        parent_depth = 0
        parent_id = state.hypotheses[0].id if state.hypotheses else None

    # Create new hypothesis
    new_id = str(uuid4())[:8]
    new_hypothesis = Hypothesis(
        id=new_id,
        content=hypothesis_text,
        parent_id=parent_id,
        depth=parent_depth + 1,
        status="open",
    )

    state.hypotheses.append(new_hypothesis)
    state.current_focus_id = new_id

    if json_output:
        import json

        print(
            json.dumps(
                {
                    "status": "branched",
                    "hypothesis_id": new_id,
                    "content": hypothesis_text,
                    "depth": new_hypothesis.depth,
                    "parent_id": parent_id,
                },
                indent=2,
            )
        )
    else:
        if RICH_AVAILABLE:
            indent = "  " * new_hypothesis.depth
            console.print(f"\n{indent}[cyan]└─[/] [bold]{hypothesis_text}[/]")
            console.print(f"[dim]   ID: {new_id} | Depth: {new_hypothesis.depth}[/]")
        else:
            _emit(f"Branched: {hypothesis_text}", {"id": new_id}, ctx)

    return 0


async def _show_tree(ctx: "InvocationContext | None", json_output: bool = False) -> int:
    """Show the hypothesis tree."""
    display_path_header(
        path="self.jewel.gestalt.flow.research.tree",
        aspect="witness",
        effects=["TREE_DISPLAYED"],
    )

    state = _get_state()

    if not state.question:
        _emit("No active research.", {}, ctx)
        return 0

    if json_output:
        import json

        print(
            json.dumps(
                {
                    "question": state.question,
                    "hypotheses": [
                        {
                            "id": h.id,
                            "content": h.content,
                            "parent_id": h.parent_id,
                            "depth": h.depth,
                            "status": h.status,
                            "evidence_count": len(h.evidence),
                        }
                        for h in state.hypotheses
                    ],
                },
                indent=2,
            )
        )
        return 0

    if RICH_AVAILABLE:
        tree = Tree(f"[bold]{state.question}[/]")

        # Build tree structure
        node_map: dict[str, Any] = {}

        for h in state.hypotheses:
            status_icon = {
                "open": "⬜",
                "confirmed": "✅",
                "refuted": "❌",
                "pending": "🔄",
            }.get(h.status, "⬜")
            label = f"{status_icon} {h.content[:50]}{'...' if len(h.content) > 50 else ''}"

            if h.parent_id is None:
                # Root node
                node_map[h.id] = tree.add(f"[cyan]{label}[/]")
            elif h.parent_id in node_map:
                # Child node
                node_map[h.id] = node_map[h.parent_id].add(f"[dim]{label}[/]")
            else:
                # Orphan (shouldn't happen, but handle gracefully)
                node_map[h.id] = tree.add(f"[yellow]{label}[/]")

        console.print(tree)
        console.print(f"\n[dim]{len(state.hypotheses)} hypotheses total[/]")
    else:
        _emit(f"Question: {state.question}", {"question": state.question}, ctx)
        for h in state.hypotheses:
            indent = "  " * h.depth
            _emit(f"{indent}└─ [{h.status}] {h.content[:50]}", {"id": h.id}, ctx)

    return 0


async def _synthesize(ctx: "InvocationContext | None", json_output: bool = False) -> int:
    """Synthesize research findings."""
    display_path_header(
        path="self.jewel.gestalt.flow.research.synthesize",
        aspect="define",
        effects=["SYNTHESIS_GENERATED"],
    )

    state = _get_state()

    if not state.question:
        _emit("Error: no active exploration", {"error": "no_exploration"}, ctx)
        return 1

    if len(state.hypotheses) < 2:
        _emit(
            "Error: need at least 2 hypotheses to synthesize",
            {"error": "insufficient_hypotheses"},
            ctx,
        )
        print('Add more hypotheses with: kg gestalt branch "<hypothesis>"')
        return 1

    # Generate synthesis (in real impl, this would use LLM)
    confirmed = [h for h in state.hypotheses if h.status == "confirmed"]
    open_hypotheses = [h for h in state.hypotheses if h.status == "open"]

    synthesis_parts = [
        f"Research Question: {state.question}",
        f"\nExplored {len(state.hypotheses)} hypotheses:",
    ]

    for h in state.hypotheses[:5]:
        synthesis_parts.append(f"  • {h.content[:60]}...")

    if confirmed:
        synthesis_parts.append(f"\nConfirmed ({len(confirmed)}):")
        for h in confirmed[:3]:
            synthesis_parts.append(f"  ✅ {h.content[:50]}")

    if open_hypotheses:
        synthesis_parts.append(f"\nOpen for investigation ({len(open_hypotheses)}):")
        for h in open_hypotheses[:3]:
            synthesis_parts.append(f"  ⬜ {h.content[:50]}")

    synthesis = "\n".join(synthesis_parts)
    state.synthesis = synthesis

    if json_output:
        import json

        print(
            json.dumps(
                {
                    "status": "synthesized",
                    "question": state.question,
                    "total_hypotheses": len(state.hypotheses),
                    "confirmed_count": len(confirmed),
                    "open_count": len(open_hypotheses),
                    "synthesis": synthesis,
                },
                indent=2,
            )
        )
    else:
        if RICH_AVAILABLE:
            console.print(
                Panel(
                    synthesis,
                    title="Research Synthesis",
                    border_style="green",
                )
            )
        else:
            _emit(synthesis, {"synthesis": synthesis}, ctx)

    return 0


async def _reset(ctx: "InvocationContext | None") -> int:
    """Reset research state."""
    display_path_header(
        path="self.jewel.gestalt.flow.research.reset",
        aspect="define",
        effects=["RESEARCH_RESET"],
    )

    _reset_state()

    if RICH_AVAILABLE:
        console.print("[green]Research state cleared.[/]")
    else:
        _emit("Research state cleared.", {}, ctx)

    return 0


async def _codebase_overview(ctx: "InvocationContext | None", json_output: bool = False) -> int:
    """Quick codebase overview using Gestalt analysis."""
    from protocols.gestalt.handler import (
        _ensure_scanned_sync,
        _get_store,
        handle_codebase_manifest,
    )

    store = _get_store()
    _ensure_scanned_sync(store)
    result = handle_codebase_manifest([], json_output, store)

    if isinstance(result, str):
        print(result)
    return 0


# =============================================================================
# Main Entry Point
# =============================================================================


def cmd_gestalt(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    concept.gestalt: Hypothesis-Driven Codebase Research.

    Explore architectural questions using tree-of-thought research flow.
    """
    # Parse path visibility flags (Wave 0 Foundation 1)
    args_list = list(args)
    args_list, show_paths, trace_mode = parse_path_flags(args_list)
    apply_path_flags(show_paths, trace_mode)

    # Parse JSON flag
    json_output = "--json" in args_list
    args_list = [a for a in args_list if a != "--json"]

    if "--help" in args_list or "-h" in args_list:
        _print_help()
        return 0

    if not args_list:
        return _run_async(_show_status(ctx, json_output))

    subcommand = args_list[0].lower()

    match subcommand:
        case "status" | "manifest":
            return _run_async(_show_status(ctx, json_output))

        case "explore":
            return _run_async(_explore(args_list[1:], ctx, json_output))

        case "branch" | "hypothesis":
            return _run_async(_branch(args_list[1:], ctx, json_output))

        case "tree":
            return _run_async(_show_tree(ctx, json_output))

        case "synthesize" | "synth":
            return _run_async(_synthesize(ctx, json_output))

        case "reset" | "clear":
            return _run_async(_reset(ctx))

        case "codebase" | "arch" | "architecture":
            return _run_async(_codebase_overview(ctx, json_output))

        case "help":
            _print_help()
            return 0

        case _:
            _emit(f"Unknown command: {subcommand}", {"error": subcommand}, ctx)
            _emit("Use 'kg gestalt --help' for available commands.", {}, ctx)
            return 1


# Export for testing
__all__ = ["cmd_gestalt", "_reset_state", "_get_state", "ResearchState", "Hypothesis"]
