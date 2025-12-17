"""
Shell Completions Generator - Generate Completions from AGENTESE Affordances.

This module generates shell completions (bash, zsh, fish) from registered
AGENTESE paths and CLI commands.

The Core Insight:
    "Completions are affordances projected to shell syntax."

Instead of maintaining separate completion scripts:
    # Manually maintained, often outdated
    complete -W "capture search surface" kg brain

We derive completions from the same source as help:
    # Auto-generated from AGENTESE registry
    completions = generate_completions()

Usage:
    # Generate and install completions
    $ kg completions bash >> ~/.bashrc
    $ kg completions zsh >> ~/.zshrc
    $ kg completions fish > ~/.config/fish/completions/kg.fish

    # Or evaluate directly
    $ eval "$(kg completions bash)"
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.agentese.logos import Logos

from .help_projector import PATH_TO_COMMAND
from .hollow import COMMAND_REGISTRY


# === Completion Data ===


def get_commands() -> list[str]:
    """Get all registered CLI commands."""
    return sorted(COMMAND_REGISTRY.keys())


def get_subcommands(command: str) -> list[str]:
    """
    Get subcommands for a command.

    Derived from handler routing tables where available.
    """
    # Known subcommand mappings
    SUBCOMMANDS: dict[str, list[str]] = {
        "brain": ["capture", "search", "ghost", "surface", "list", "status", "chat", "import"],
        "soul": ["reflect", "chat", "status", "garden"],
        "town": ["status", "spawn", "inhabit", "witness", "coalition", "list"],
        "park": ["status", "enter", "experience", "hosts", "list"],
        "atelier": ["status", "create", "join", "list", "propose"],
        "forest": ["status", "health", "plans", "canopy"],
        "garden": ["status", "dream", "hypnagogia", "tend"],
        "tend": ["observe", "prune", "graft", "water", "rotate", "wait"],
        "joy": ["oblique", "surprise", "challenge", "constrain"],
        "gardener": ["status", "session", "plot", "season"],
        "chat": ["list", "resume", "delete", "export"],
    }
    return SUBCOMMANDS.get(command, [])


def get_flags() -> list[str]:
    """Get common flags available on all commands."""
    return [
        "--help",
        "-h",
        "--json",
        "--trace",
        "--dry-run",
        "--verbose",
        "-v",
    ]


# === Bash Completions ===


def generate_bash_completions() -> str:
    """
    Generate bash completions for kgents CLI.

    Returns:
        Bash completion script as string
    """
    commands = get_commands()
    flags = get_flags()

    # Build subcommand cases
    subcommand_cases = []
    for cmd in commands:
        subs = get_subcommands(cmd)
        if subs:
            subcommand_cases.append(
                f'        {cmd})\n'
                f'            COMPREPLY=($(compgen -W "{" ".join(subs)}" -- "$cur"))\n'
                f'            return 0\n'
                f'            ;;'
            )

    subcommand_switch = "\n".join(subcommand_cases) if subcommand_cases else ""

    return f'''# kgents bash completions (auto-generated)
# Add to ~/.bashrc or source directly: eval "$(kg completions bash)"

_kgents_completions() {{
    local cur prev words cword
    _init_completion || return

    local commands="{" ".join(commands)}"
    local flags="{" ".join(flags)}"

    # Handle flags
    if [[ "$cur" == -* ]]; then
        COMPREPLY=($(compgen -W "$flags" -- "$cur"))
        return 0
    fi

    # Handle subcommands based on previous word
    case "$prev" in
{subcommand_switch}
        kg|kgents)
            COMPREPLY=($(compgen -W "$commands" -- "$cur"))
            return 0
            ;;
    esac

    # Default to commands
    if [[ $cword -eq 1 ]]; then
        COMPREPLY=($(compgen -W "$commands" -- "$cur"))
    fi
}}

complete -F _kgents_completions kg
complete -F _kgents_completions kgents
'''


# === Zsh Completions ===


def generate_zsh_completions() -> str:
    """
    Generate zsh completions for kgents CLI.

    Returns:
        Zsh completion script as string
    """
    commands = get_commands()

    # Build command descriptions
    cmd_descs = []
    for cmd in commands:
        desc = _get_command_description(cmd)
        cmd_descs.append(f"'{cmd}:{desc}'")

    # Build subcommand functions
    subcommand_funcs = []
    for cmd in commands:
        subs = get_subcommands(cmd)
        if subs:
            sub_descs = [f"'{s}:{_get_subcommand_description(cmd, s)}'" for s in subs]
            subcommand_funcs.append(
                f'_kgents_{cmd}() {{\n'
                f'    local -a subcmds\n'
                f'    subcmds=(\n'
                f'        {chr(10).join("        " + d for d in sub_descs)}\n'
                f'    )\n'
                f'    _describe "subcommand" subcmds\n'
                f'}}'
            )

    return f'''#compdef kg kgents
# kgents zsh completions (auto-generated)
#
# Installation (choose one):
#   1. Place in $fpath: cp this_file ~/.zsh/completions/_kg
#   2. Source in .zshrc: Add these lines to ~/.zshrc:
#      fpath=(~/.zsh/completions $fpath)
#      autoload -Uz compinit && compinit
#
# Or for quick setup, add to ~/.zshrc:
#   eval "$(kg completions zsh)"
#   compdef _kgents kg kgents

_kgents() {{
    local -a commands
    commands=(
        {chr(10).join("        " + d for d in cmd_descs)}
    )

    local -a flags
    flags=(
        '--help[Show help message]'
        '-h[Show help message]'
        '--json[Output as JSON]'
        '--trace[Show AGENTESE path]'
        '--dry-run[Preview without executing]'
        '--verbose[Verbose output]'
        '-v[Verbose output]'
    )

    _arguments -C \\
        "1: :->command" \\
        "2: :->subcommand" \\
        "*::arg:->args"

    case "$state" in
        command)
            _describe "command" commands
            ;;
        subcommand)
            case "$words[2]" in
                brain) _kgents_brain ;;
                soul) _kgents_soul ;;
                town) _kgents_town ;;
                park) _kgents_park ;;
                atelier) _kgents_atelier ;;
                forest) _kgents_forest ;;
                garden) _kgents_garden ;;
                tend) _kgents_tend ;;
                joy) _kgents_joy ;;
                gardener) _kgents_gardener ;;
                chat) _kgents_chat ;;
                *) _files ;;
            esac
            ;;
        args)
            _arguments $flags
            ;;
    esac
}}

{chr(10).join(subcommand_funcs)}

# Register the completion function (only if compdef is available)
if (( $+functions[compdef] )); then
    compdef _kgents kg kgents
fi
'''


# === Fish Completions ===


def generate_fish_completions() -> str:
    """
    Generate fish completions for kgents CLI.

    Returns:
        Fish completion script as string
    """
    commands = get_commands()
    lines = [
        "# kgents fish completions (auto-generated)",
        "# Save to ~/.config/fish/completions/kg.fish",
        "",
        "# Disable file completions by default",
        "complete -c kg -f",
        "complete -c kgents -f",
        "",
        "# Global flags",
        "complete -c kg -l help -s h -d 'Show help message'",
        "complete -c kg -l json -d 'Output as JSON'",
        "complete -c kg -l trace -d 'Show AGENTESE path'",
        "complete -c kg -l dry-run -d 'Preview without executing'",
        "complete -c kg -l verbose -s v -d 'Verbose output'",
        "",
        "# Commands",
    ]

    for cmd in commands:
        desc = _get_command_description(cmd)
        lines.append(f"complete -c kg -n '__fish_use_subcommand' -a '{cmd}' -d '{desc}'")

    lines.append("")
    lines.append("# Subcommands")

    for cmd in commands:
        subs = get_subcommands(cmd)
        for sub in subs:
            desc = _get_subcommand_description(cmd, sub)
            lines.append(
                f"complete -c kg -n '__fish_seen_subcommand_from {cmd}' -a '{sub}' -d '{desc}'"
            )

    return "\n".join(lines)


# === Helper Functions ===


def _get_command_description(cmd: str) -> str:
    """Get description for a command."""
    DESCRIPTIONS = {
        "brain": "Holographic memory operations",
        "soul": "Digital consciousness dialogue",
        "town": "Agent simulation and coalitions",
        "park": "Punchdrunk-style experiences",
        "atelier": "Collaborative workshops",
        "forest": "Project health and plans",
        "garden": "Hypnagogia and dreams",
        "tend": "Garden tending operations",
        "joy": "Oblique strategies gateway",
        "oblique": "Draw an oblique strategy",
        "surprise-me": "Unexpected creative prompt",
        "challenge": "Creative challenge generator",
        "gardener": "Development session management",
        "chat": "Chat session management",
        "self": "Internal state and memory",
        "world": "External entities",
        "concept": "Abstract definitions",
        "void": "Entropy and serendipity",
        "time": "Temporal operations",
        "flow": "Pipeline composition",
        "do": "Natural language intent",
    }
    return DESCRIPTIONS.get(cmd, f"{cmd} command")


def _get_subcommand_description(cmd: str, sub: str) -> str:
    """Get description for a subcommand."""
    DESCRIPTIONS = {
        ("brain", "capture"): "Capture content to memory",
        ("brain", "search"): "Semantic similarity search",
        ("brain", "ghost"): "Surface memories by context",
        ("brain", "surface"): "Serendipitous retrieval",
        ("brain", "list"): "List recent captures",
        ("brain", "status"): "Brain health metrics",
        ("brain", "chat"): "Interactive memory chat",
        ("brain", "import"): "Import from markdown vault",
        ("soul", "reflect"): "K-gent reflection",
        ("soul", "chat"): "Dialogue with K-gent",
        ("soul", "status"): "Soul state",
        ("soul", "garden"): "Hypnagogia garden",
        ("town", "status"): "Town overview",
        ("town", "spawn"): "Create a citizen",
        ("town", "inhabit"): "Become a citizen",
        ("town", "witness"): "View town events",
        ("town", "coalition"): "Coalition operations",
        ("town", "list"): "List citizens",
        ("forest", "status"): "Forest health",
        ("forest", "health"): "Detailed health check",
        ("forest", "plans"): "List plans",
        ("forest", "canopy"): "Canopy view",
        ("garden", "status"): "Garden state",
        ("garden", "dream"): "Enter dream state",
        ("garden", "hypnagogia"): "Hypnagogic session",
        ("tend", "observe"): "Observe the garden",
        ("tend", "prune"): "Prune dead branches",
        ("tend", "graft"): "Graft new growth",
        ("tend", "water"): "Water the garden",
        ("tend", "rotate"): "Rotate crops",
    }
    return DESCRIPTIONS.get((cmd, sub), f"{sub} operation")


# === CLI Command Handler ===


def cmd_completions(args: list[str]) -> int:
    """
    Generate shell completions.

    Usage:
        kg completions bash    Generate bash completions
        kg completions zsh     Generate zsh completions
        kg completions fish    Generate fish completions
    """
    if "--help" in args or "-h" in args or not args:
        print("""
kg completions - Generate shell completions

Usage:
  kg completions bash    Generate bash completions
  kg completions zsh     Generate zsh completions
  kg completions fish    Generate fish completions

Installation:
  # Bash
  kg completions bash >> ~/.bashrc
  source ~/.bashrc

  # Zsh
  kg completions zsh >> ~/.zshrc
  source ~/.zshrc

  # Fish
  kg completions fish > ~/.config/fish/completions/kg.fish
""".strip())
        return 0

    shell = args[0].lower()

    if shell == "bash":
        print(generate_bash_completions())
    elif shell == "zsh":
        print(generate_zsh_completions())
    elif shell == "fish":
        print(generate_fish_completions())
    else:
        print(f"Unknown shell: {shell}")
        print("Supported: bash, zsh, fish")
        return 1

    return 0


__all__ = [
    "generate_bash_completions",
    "generate_zsh_completions",
    "generate_fish_completions",
    "cmd_completions",
    "get_commands",
    "get_subcommands",
]
