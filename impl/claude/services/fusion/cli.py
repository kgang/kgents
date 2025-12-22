#!/usr/bin/env python3
"""
kg decide: Witness decisions through dialectical fusion.

"The proof IS the decision. The mark IS the witness."

This CLI captures reasoning traces for decisions as they happen.
It operationalizes the Symmetric Supersession protocol where
Kent and Claude are symmetric agents who sharpen each other.

USAGE:
  kg decide                        # Guided dialectical experience
  kg decide --fast "..." [opts]    # Quick capture for trivial decisions
  kg decide --propose "..."        # Start a proposal (async dialectic)

GUIDED EXPERIENCE (default):
  Each round of dialectic is a turn. You're guided through:
  1. What decision is being considered?
  2. Kent's proposal + reasoning
  3. Claude's proposal + reasoning
  4. Synthesis that transcends both
  5. Optional: veto if it feels wrong

FAST MODE (--fast):
  For trivial decisions that don't need full dialectic:

  kg decide --fast "Use tabs" --reasoning "Project convention"
  kg decide --kent "A" --claude "B" --synthesis "C" --why "Reasoning"

The fusion is recorded to the witness store for future reference.

See: spec/protocols/witness-supersession.md
"""

from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import dataclass
from typing import Any

# =============================================================================
# Rich Console Helpers
# =============================================================================


def _get_console() -> Any:
    """Get Rich console for pretty output."""
    try:
        from rich.console import Console

        return Console()
    except ImportError:
        return None


def _prompt(message: str, default: str = "") -> str:
    """Prompt for input with optional default."""
    console = _get_console()

    if default:
        prompt_text = f"{message} [{default}]: "
    else:
        prompt_text = f"{message}: "

    if console:
        try:
            from rich.prompt import Prompt

            return Prompt.ask(message, default=default) or default
        except ImportError:
            pass

    result = input(prompt_text).strip()
    return result if result else default


def _print_header(title: str) -> None:
    """Print a section header."""
    console = _get_console()
    if console:
        console.print(f"\n[bold cyan]{title}[/bold cyan]")
        console.print("[dim]" + "─" * 40 + "[/dim]")
    else:
        print(f"\n{title}")
        print("─" * 40)


def _print_result(result: dict[str, Any]) -> None:
    """Print fusion result in a nice panel."""
    console = _get_console()

    if console:
        from rich.panel import Panel
        from rich.text import Text

        status = result.get("status", "unknown")
        fusion_id = result.get("fusion_id", "???")
        is_genuine = result.get("is_genuine_fusion", False)
        synthesis = result.get("synthesis_content", "")

        status_color = {
            "synthesized": "green",
            "vetoed": "red",
            "impasse": "yellow",
        }.get(status, "white")

        lines = [
            f"[{status_color}]Status: {status.upper()}[/{status_color}]",
            f"Fusion ID: [dim]{fusion_id}[/dim]",
            f"Genuine Fusion: {'Yes' if is_genuine else 'No'}",
        ]

        if synthesis:
            lines.append("")
            lines.append(f"[bold]Synthesis:[/bold] {synthesis}")

        lines.append("")
        lines.append('[dim]"The proof IS the decision."[/dim]')

        panel = Panel(
            Text.from_markup("\n".join(lines)),
            title="[bold green]Decision Witnessed[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
        console.print(panel)
    else:
        print("\n" + "=" * 40)
        print("DECISION WITNESSED")
        print("=" * 40)
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Fusion ID: {result.get('fusion_id', '???')}")
        print(f"Synthesis: {result.get('synthesis_content', '')}")
        print()
        print('"The proof IS the decision."')


# =============================================================================
# Core Decision Logic
# =============================================================================


@dataclass
class DecisionInput:
    """Collected input for a decision."""

    topic: str = ""
    kent_content: str = ""
    kent_reasoning: str = ""
    kent_principles: list[str] | None = None
    claude_content: str = ""
    claude_reasoning: str = ""
    claude_principles: list[str] | None = None
    synthesis_content: str = ""
    synthesis_reasoning: str = ""
    incorporates_kent: str = ""
    incorporates_claude: str = ""
    transcends: str = ""


async def _run_fusion(decision: DecisionInput) -> dict[str, Any]:
    """Run the fusion service with collected decision input."""
    from services.fusion import FusionService

    # Get witness persistence if available
    try:
        from services.providers import get_witness_persistence

        witness = await get_witness_persistence()
    except Exception:
        witness = None

    fusion = FusionService(witness=witness)

    # Create proposals
    kent = fusion.propose(
        agent="kent",
        content=decision.kent_content,
        reasoning=decision.kent_reasoning,
        principles=decision.kent_principles,
    )

    claude = fusion.propose(
        agent="claude",
        content=decision.claude_content,
        reasoning=decision.claude_reasoning,
        principles=decision.claude_principles,
    )

    # Run fusion
    result = await fusion.simple_fuse(
        kent,
        claude,
        synthesis_content=decision.synthesis_content,
        synthesis_reasoning=decision.synthesis_reasoning,
        incorporates_from_a=decision.incorporates_kent or None,
        incorporates_from_b=decision.incorporates_claude or None,
        transcends=decision.transcends or None,
    )

    return {
        "fusion_id": result.id,
        "status": result.status.value,
        "synthesis_content": result.synthesis.content if result.synthesis else None,
        "synthesis_reasoning": result.synthesis.reasoning if result.synthesis else None,
        "is_genuine_fusion": result.is_genuine_fusion,
        "kent_proposal_id": kent.id,
        "claude_proposal_id": claude.id,
    }


# =============================================================================
# Guided Experience
# =============================================================================


def _guided_experience() -> DecisionInput:
    """
    Run the guided dialectical experience.

    Each step is a "turn" in the dialectic. The experience guides
    you through the full fusion process.
    """
    console = _get_console()

    if console:
        from rich.panel import Panel

        console.print(
            Panel(
                "[bold]DECISION WITNESS[/bold]\n\n"
                "I'll guide you through capturing this decision.\n"
                "Each step sharpens the reasoning.\n\n"
                '[dim]"Iron sharpens iron."[/dim]',
                border_style="magenta",
                padding=(1, 2),
            )
        )
    else:
        print("\n" + "=" * 50)
        print("DECISION WITNESS")
        print("=" * 50)
        print("I'll guide you through capturing this decision.")
        print()

    decision = DecisionInput()

    # Step 1: Topic
    _print_header("Step 1: The Question")
    decision.topic = _prompt("What decision is being considered?")

    # Step 2: Kent's proposal
    _print_header("Step 2: Kent's Proposal")
    if console:
        console.print("[dim]What does Kent (or the human perspective) propose?[/dim]")
    decision.kent_content = _prompt("Kent proposes")
    decision.kent_reasoning = _prompt("Kent's reasoning")

    # Step 3: Claude's proposal
    _print_header("Step 3: Claude's Proposal")
    if console:
        console.print("[dim]What does Claude (or the AI perspective) propose?[/dim]")
    decision.claude_content = _prompt("Claude proposes")
    decision.claude_reasoning = _prompt("Claude's reasoning")

    # Step 4: Synthesis
    _print_header("Step 4: Synthesis")
    if console:
        console.print("[dim]What emerges from both proposals?[/dim]")
        console.print("[dim]True synthesis transcends both—it's not just A or B.[/dim]")
    decision.synthesis_content = _prompt("The synthesis")
    decision.synthesis_reasoning = _prompt("Why this synthesis works")

    # Optional: what was incorporated
    _print_header("Step 5: Integration (optional)")
    decision.incorporates_kent = _prompt("What was taken from Kent's view?", "")
    decision.incorporates_claude = _prompt("What was taken from Claude's view?", "")
    decision.transcends = _prompt("What's NEW beyond both?", "")

    return decision


# =============================================================================
# Fast Mode
# =============================================================================


def _fast_mode(args: list[str]) -> DecisionInput:
    """
    Parse fast-mode arguments for quick decisions.

    Supports:
      --fast "content" --reasoning "why"
      --kent "A" --claude "B" --synthesis "C" --why "reasoning"
    """
    decision = DecisionInput()

    i = 0
    while i < len(args):
        arg = args[i]

        if arg == "--fast" and i + 1 < len(args):
            # Fast mode: single decision, same for both agents
            decision.kent_content = args[i + 1]
            decision.claude_content = args[i + 1]
            decision.synthesis_content = args[i + 1]
            i += 2
        elif arg == "--reasoning" and i + 1 < len(args):
            decision.kent_reasoning = args[i + 1]
            decision.claude_reasoning = args[i + 1]
            decision.synthesis_reasoning = args[i + 1]
            i += 2
        elif arg == "--kent" and i + 1 < len(args):
            decision.kent_content = args[i + 1]
            i += 2
        elif arg == "--kent-reasoning" and i + 1 < len(args):
            decision.kent_reasoning = args[i + 1]
            i += 2
        elif arg == "--claude" and i + 1 < len(args):
            decision.claude_content = args[i + 1]
            i += 2
        elif arg == "--claude-reasoning" and i + 1 < len(args):
            decision.claude_reasoning = args[i + 1]
            i += 2
        elif arg == "--synthesis" and i + 1 < len(args):
            decision.synthesis_content = args[i + 1]
            i += 2
        elif arg == "--why" and i + 1 < len(args):
            decision.synthesis_reasoning = args[i + 1]
            i += 2
        elif arg == "--transcends" and i + 1 < len(args):
            decision.transcends = args[i + 1]
            i += 2
        else:
            i += 1

    # Fill in defaults if not provided
    if not decision.kent_reasoning:
        decision.kent_reasoning = decision.kent_content
    if not decision.claude_reasoning:
        decision.claude_reasoning = decision.claude_content
    if not decision.synthesis_reasoning:
        decision.synthesis_reasoning = "Quick decision capture"

    return decision


# =============================================================================
# Help Text
# =============================================================================

HELP_TEXT = """\
kg decide - Witness decisions through dialectical fusion

USAGE:
  kg decide                              Guided dialectical experience
  kg decide --fast "..." [options]       Quick capture for trivial decisions

GUIDED MODE (default):
  Interactive experience that guides you through:
  1. The question being decided
  2. Kent's proposal + reasoning
  3. Claude's proposal + reasoning
  4. Synthesis that transcends both

FAST MODE OPTIONS:
  --fast "content"           Quick decision (same content for all)
  --reasoning "why"          Reasoning for quick decision
  --json                     Machine-readable JSON output (fast mode only)

  --kent "content"           Kent's proposal
  --kent-reasoning "why"     Kent's reasoning
  --claude "content"         Claude's proposal
  --claude-reasoning "why"   Claude's reasoning
  --synthesis "content"      The synthesis
  --why "reasoning"          Why the synthesis works
  --transcends "what"        What's new beyond both proposals

EXAMPLES:
  # Full guided experience
  kg decide

  # Quick trivial decision
  kg decide --fast "Use Python 3.12" --reasoning "Latest stable"

  # Full dialectic in fast mode
  kg decide --kent "Use LangChain" --claude "Build kgents" \\
            --synthesis "Build minimal kernel, validate, then decide" \\
            --why "Avoids both risks"

AGENT-FRIENDLY EXAMPLES:
  kg decide --fast "Choice" --reasoning "Why" --json
  # Returns: {"fusion_id": "...", "status": "synthesized", ...}

PHILOSOPHY:
  Kent and Claude are symmetric agents. Either can propose.
  Either can be superseded. Fusion emerges from dialectic.
  The disgust veto is absolute.

  "The proof IS the decision."

See: spec/protocols/witness-supersession.md
See: docs/skills/witness-for-agents.md
"""


# =============================================================================
# Main Entry Point
# =============================================================================


def main(argv: list[str] | None = None) -> int:
    """Main entry point for kg decide CLI."""
    if argv is None:
        argv = sys.argv[1:]

    args = list(argv)
    json_output = "--json" in args

    # Help
    if "--help" in args or "-h" in args:
        print(HELP_TEXT)
        return 0

    # Determine mode
    is_fast_mode = "--fast" in args or "--kent" in args or "--claude" in args

    try:
        if is_fast_mode:
            decision = _fast_mode(args)

            # Validate fast mode has required fields
            if not decision.kent_content and not decision.synthesis_content:
                if json_output:
                    print(json.dumps({"error": "--fast requires content"}))
                else:
                    print("Error: --fast requires content")
                    print('Usage: kg decide --fast "content" --reasoning "why"')
                return 1
        else:
            if json_output:
                # Can't do guided mode with JSON output
                print(json.dumps({"error": "Guided mode not supported with --json. Use --fast."}))
                return 1
            decision = _guided_experience()

        # Validate we have what we need
        if not decision.synthesis_content:
            if json_output:
                print(json.dumps({"error": "No synthesis provided"}))
            else:
                print("Error: No synthesis provided")
            return 1

        # Run the fusion
        result = asyncio.run(_run_fusion(decision))

        # Output result
        if json_output:
            print(json.dumps(result))
        else:
            _print_result(result)

        return 0

    except KeyboardInterrupt:
        if not json_output:
            print("\n\nDecision cancelled.")
        return 0
    except Exception as e:
        if json_output:
            print(json.dumps({"error": str(e)}))
        else:
            console = _get_console()
            if console:
                console.print(f"[red]Error: {e}[/red]")
            else:
                print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
