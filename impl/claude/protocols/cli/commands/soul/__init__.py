"""
Soul Commands: K-gent Digital Soul CLI interface.

K-gent Soul is the Middleware of Consciousness:
1. INTERCEPTS Semaphores from Purgatory (auto-resolves or annotates)
2. INHABITS Terrarium as ambient presence (not just CLI command)
3. DREAMS during Hypnagogia (async refinement at night)

Usage:
    kgents soul                    # Interactive (default: REFLECT)
    kgents soul reflect [prompt]   # Introspection
    kgents soul advise [prompt]    # Guidance
    kgents soul challenge [prompt] # Dialectics
    kgents soul explore [prompt]   # Discovery
    kgents soul vibe               # One-liner eigenvector summary
    kgents soul drift              # Compare vs previous session
    kgents soul tense              # Surface eigenvector tensions
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# Valid modes and subcommands
DIALOGUE_MODES = {"reflect", "advise", "challenge", "explore"}
QUICK_COMMANDS = {"vibe", "drift", "tense", "why"}
SPECIAL_COMMANDS = {
    "approve",
    "stream",
    "watch",
    "starters",
    "manifest",
    "eigenvectors",
    "audit",
    "garden",
    "validate",
    "dream",
}
BEING_COMMANDS = {"history", "propose", "commit", "crystallize", "resume"}

ALL_MODES = DIALOGUE_MODES | QUICK_COMMANDS | SPECIAL_COMMANDS | BEING_COMMANDS


def print_help() -> None:
    """Print help for soul command."""
    print(__doc__)
    print()
    print("MODES:")
    print("  reflect             Mirror back for examination (default)")
    print("  advise              Offer preference-aligned suggestions")
    print("  challenge           Push back constructively, find weaknesses")
    print("  explore             Follow tangents, generate hypotheses")
    print()
    print("QUICK COMMANDS:")
    print("  vibe                One-liner eigenvector summary with emoji")
    print("  drift               Compare soul vs previous session")
    print("  tense               Surface current eigenvector tensions")
    print("  why [prompt]        Quick CHALLENGE mode (alias for challenge)")
    print()
    print("PRO CROWN JEWELS:")
    print("  approve [action]    Would Kent approve this action?")
    print()
    print("COMMANDS:")
    print("  stream              Ambient FLOWING mode (pulses + dialogue)")
    print("  watch               Ambient file watcher (pair programming)")
    print("  starters            Show starter prompts for current mode")
    print("  manifest            Show current soul state (persistent)")
    print("  eigenvectors        Show personality coordinates")
    print("  audit               View recent mediations and audit trail")
    print("  garden              View PersonaGarden state (patterns, preferences)")
    print("  validate <file>     Check file against principles (Semantic Gatekeeper)")
    print("  dream               Trigger hypnagogia (dream cycle) manually")
    print()
    print("BEING COMMANDS (cross-session identity):")
    print("  history             View soul change history (who was I?)")
    print("  propose <desc>      K-gent proposes a change to itself")
    print("  commit <id>         Approve and commit a pending change")
    print("  crystallize <name>  Save soul checkpoint for later")
    print("  resume <id>         Resume from a crystallized state")
    print()
    print("OPTIONS:")
    print(
        "  --stream            Stream response character-by-character with token count"
    )
    print("  --pipe              JSON-line output (one chunk per line) for shell pipes")
    print("  --quick             WHISPER budget (~100 tokens)")
    print("  --deep              DEEP budget (~8000+ tokens, Council of Ghosts)")
    print("  --json              Output as JSON")
    print("  --summary           For 'audit': show summary instead of recent")
    print("  --limit N           For 'audit'/'history': show N entries (default 10)")
    print("  --pulse-interval N  For 'stream': seconds between pulses (default 30)")
    print("  --no-pulses         For 'stream': hide pulse output")
    print("  --dry-run           For 'dream': show what would change without applying")
    print("  --sync              For 'garden': sync patterns from hypnagogia first")
    print("  --path <dir>        For 'watch': directory to watch (default: cwd)")
    print("  --help, -h          Show this help")
