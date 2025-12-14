"""
Agent Commands: Alethic Architecture CLI interface.

The Alethic Architecture provides "batteries included" agent deployment:
1. Nucleus: Pure Agent[A, B] logic
2. Halo: Declarative @Capability.* metadata
3. Projector: Target-specific compilation

Usage:
    kgents a                       # Show help
    kgents a inspect <agent>       # Show Halo + Nucleus details
    kgents a manifest <agent>      # K8sProjector -> YAML output
    kgents a run <agent>           # LocalProjector -> run agent
    kgents a list                  # List registered agents
    kgents a <dialogue-agent>      # Direct dialogue (e.g., 'kg a soul')

Examples:
    kgents a inspect MyKappaService
    -> Shows: capabilities, archetype, functor chain

    kgents a manifest MyKappaService > deployment.yaml
    -> Produces K8s manifests for kubectl apply

    kgents a run MyKappaService --input "hello"
    -> Compiles with LocalProjector and invokes
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# --- Dialogue Agent Registry ---
# Maps agent short names to module:class paths for dialogue-capable agents.
# Unlike archetypes (Kappa/Lambda/Delta), dialogue agents implement
# the dialogue(message: str) -> DialogueOutput protocol.

DIALOGUE_AGENTS: dict[str, str] = {
    "soul": "agents.k.soul:KgentSoul",
    "kgent": "agents.k.soul:KgentSoul",  # alias
    "session": "agents.k.session:SoulSession",  # cross-session identity
}

# Valid commands/modes
ARCHETYPE_COMMANDS = {"inspect", "manifest", "run", "list", "new"}
ALL_MODES = ARCHETYPE_COMMANDS | set(DIALOGUE_AGENTS.keys())


def print_help() -> None:
    """Print help for a command."""
    print(__doc__)
    print()
    print("COMMANDS:")
    print("  <agent> [prompt]    Direct dialogue (e.g., 'kg a soul \"hello\"')")
    print("  <agent>             Enter REPL mode (e.g., 'kg a soul')")
    print("  inspect <agent>     Show Halo (capabilities) and Nucleus details")
    print("  manifest <agent>    Generate K8s manifests (YAML)")
    print("  run <agent>         Compile and run agent locally")
    print("  list                List available agents")
    print("  new <name>          Scaffold a new agent (interactive)")
    print()
    print("DIALOGUE AGENTS:")
    for name, path in DIALOGUE_AGENTS.items():
        print(f"  {name:12}        -> {path}")
    print()
    print("OPTIONS:")
    print("  --namespace <ns>    K8s namespace for manifests (default: kgents-agents)")
    print("  --input <data>      Input data for 'run' command")
    print("  --validate          Validate generated manifests (for 'manifest' command)")
    print("  --json              Output as JSON")
    print(
        "  --archetype <type>  Archetype for 'new' command (kappa|lambda|delta|minimal)"
    )
    print("  --output <path>     Output path for 'new' command")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print('  kg a soul "What should I focus on today?"')
    print("  kg a soul                   # Enter REPL")
    print('  kg a session "Hello"        # Cross-session K-gent')


def _emit_output(
    human: str, semantic: dict[str, Any], ctx: "InvocationContext | None"
) -> None:
    """Emit output via dual-channel if ctx available, else print."""
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)
