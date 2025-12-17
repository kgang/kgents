"""
Soul Handler: Thin routing shim to self.soul.* AGENTESE paths.

All business logic lives in agents/k/ (K-gent Soul). This file only routes.

AGENTESE Path Mapping:
    kg soul                -> self.soul.manifest
    kg soul reflect ...    -> self.soul.reflect
    kg soul challenge ...  -> self.soul.challenge
    kg soul advise ...     -> self.soul.dialogue[mode=advise]
    kg soul explore ...    -> self.soul.dialogue[mode=explore]
    kg soul chat           -> self.soul.chat (interactive)
    kg soul starters       -> self.soul.starters
    kg soul eigenvectors   -> self.soul.eigenvectors
    kg soul manifest       -> self.soul.manifest
    kg soul vibe           -> self.soul.manifest (quick)
    kg soul mode ...       -> self.soul.mode

See: docs/skills/metaphysical-fullstack.md, spec/protocols/cli.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from protocols.cli.projection import project_command, route_to_path

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# === Path Routing ===

SOUL_SUBCOMMAND_TO_PATH = {
    # Core dialogue modes
    "reflect": "self.soul.reflect",
    "challenge": "self.soul.challenge",
    "advise": "self.soul.dialogue",
    "explore": "self.soul.dialogue",
    # Chat (interactive via projection)
    "chat": "self.soul.chat",
    # Inspection
    "manifest": "self.soul.manifest",
    "starters": "self.soul.starters",
    "eigenvectors": "self.soul.eigenvectors",
    "mode": "self.soul.mode",
    # Quick commands (aliases)
    "vibe": "self.soul.manifest",
    "status": "self.soul.manifest",
}

DEFAULT_PATH = "self.soul.manifest"


# === Main Entry Point ===


def cmd_soul(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    K-gent Soul: Route to AGENTESE self.soul.* paths.

    All business logic is in agents/k/. This handler only routes.
    """
    # Parse help flag (special case - not routed)
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse subcommand
    subcommand = _parse_subcommand(args)

    # Route to AGENTESE path
    path = route_to_path(subcommand, SOUL_SUBCOMMAND_TO_PATH, DEFAULT_PATH)

    # Extract kwargs for specific subcommands
    kwargs = _extract_kwargs(subcommand, args)

    # Project through CLI functor
    return project_command(
        path,
        args,
        ctx,
        kwargs=kwargs,
        entity_name="K-gent",
    )


def _parse_subcommand(args: list[str]) -> str:
    """Extract subcommand from args, skipping flags."""
    for arg in args:
        if not arg.startswith("-"):
            return arg.lower()
    return "manifest"  # default


def _extract_kwargs(subcommand: str, args: list[str]) -> dict[str, Any]:
    """
    Extract kwargs from args based on subcommand.

    Handles:
    - Dialogue modes: message from positional args
    - Mode setting: set parameter from positional args
    """
    kwargs: dict[str, Any] = {}

    # Collect positional args after subcommand
    positional: list[str] = []
    skip_next = False
    found_subcommand = False

    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg.startswith("-"):
            # Check for --message flag
            if arg == "--message" and i + 1 < len(args):
                kwargs["message"] = args[i + 1]
                skip_next = True
            elif arg.startswith("--message="):
                kwargs["message"] = arg.split("=", 1)[1]
            continue
        if not found_subcommand:
            found_subcommand = True
            continue
        positional.append(arg)

    # Map positional to expected parameter
    if positional:
        message = " ".join(positional)
        if subcommand in ("reflect", "challenge", "advise", "explore"):
            kwargs["message"] = message
        elif subcommand == "mode":
            kwargs["set"] = message
        elif subcommand == "starters":
            kwargs["mode"] = message

    # Set mode for advise/explore
    if subcommand == "advise":
        kwargs["mode"] = "advise"
    elif subcommand == "explore":
        kwargs["mode"] = "explore"

    return kwargs


def _print_help() -> None:
    """Print soul command help (projected from AGENTESE affordances)."""
    from protocols.cli.handlers._help import show_projected_help
    show_projected_help("self.soul", _print_help_fallback)


def _print_help_fallback() -> None:
    """Fallback static help if help projection unavailable."""
    help_text = """
kg soul - K-gent Soul (Crown Jewel Digital Persona)

Commands:
  kg soul                      Show soul status
  kg soul reflect "prompt"     Introspective dialogue
  kg soul challenge "prompt"   Challenge assumptions
  kg soul chat                 Interactive chat REPL

Options:
  --help, -h                   Show this help message
  --json                       Output as JSON
  --trace                      Show AGENTESE path

AGENTESE Paths:
  self.soul.manifest           Soul state display
  self.soul.reflect            Reflective dialogue
  self.soul.chat.*             Interactive chat

Examples:
  kg soul reflect "What should I focus on?"
  kg soul challenge "AI will replace programmers"
  kg soul chat
"""
    print(help_text.strip())


__all__ = ["cmd_soul"]
