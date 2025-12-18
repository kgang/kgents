"""
Session Handler: Thin routing to self.forest.session.* AGENTESE paths.

This handler routes CLI commands to SessionNode aspects via the projection functor.
The SessionNode is the AGENTESE interface for Garden Protocol sessions.

Usage:
    kg session                # Show session status (active or recent)
    kg session manifest       # View current session details
    kg session begin          # Start a new gardening session
    kg session begin --gardener claude-opus-4-5  # Start with specified gardener
    kg session gesture --type code --plan meta --summary "Fixed bug"
    kg session end            # End session without letter
    kg session end --letter "Good progress today..."  # End with letter

AGENTESE Paths:
    self.forest.session.manifest   - View current session or recent sessions
    self.forest.session.begin      - Start a new session
    self.forest.session.gesture    - Record a gesture (atomic work unit)
    self.forest.session.end        - End session and propagate to plans

Gesture Types:
    code      - Code changes (increases momentum)
    insight   - Realizations or discoveries
    decision  - Design choices
    connect   - Cross-plan resonance
    prune     - Removal or simplification
    void_sip  - Entropy draw (exploration)
    void_tithe - Entropy return (gratitude)

Garden Protocol Reference:
    Sessions are the primary unit of planning. Plans emerge from session traces
    like paths worn through a garden. Each session tracks:
    - Gestures (atomic work units)
    - Plans tended (with state transitions)
    - Entropy spent (void draws)
    - Letter to next session (conversation with future self)

> "The garden tends itself, but only because we planted it together."
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# Subcommand -> AGENTESE path mapping
# SessionNode is registered at "self.forest.session"
SESSION_SUBCOMMAND_MAP: dict[str, str] = {
    "manifest": "self.forest.session.manifest",
    "begin": "self.forest.session.begin",
    "start": "self.forest.session.begin",  # Alias
    "gesture": "self.forest.session.gesture",
    "record": "self.forest.session.gesture",  # Alias
    "end": "self.forest.session.end",
    "close": "self.forest.session.end",  # Alias
}

# Valid gesture types (for validation hint)
GESTURE_TYPES = (
    "code",
    "insight",
    "decision",
    "connect",
    "prune",
    "void_sip",
    "void_tithe",
)


def cmd_session(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    AGENTESE-native session management operations.

    Routes CLI invocations to self.forest.session.* paths via the projection functor.

    This is the entry point for Garden Protocol session commands.
    """
    # Help
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    # Parse subcommand (default: manifest)
    subcommand = "manifest"
    for i, arg in enumerate(args):
        if arg in SESSION_SUBCOMMAND_MAP:
            subcommand = arg
            break

    # Route to AGENTESE path
    path = SESSION_SUBCOMMAND_MAP.get(subcommand, "self.forest.session.manifest")

    # Parse kwargs from remaining args
    kwargs: dict[str, str | bool] = {}

    # Handle json output
    if "--json" in args:
        kwargs["json_output"] = True

    # Handle begin-specific args
    if subcommand in ("begin", "start"):
        # --gardener <name>
        if "--gardener" in args:
            idx = args.index("--gardener")
            if idx + 1 < len(args):
                kwargs["gardener"] = args[idx + 1]
        # --period <morning|afternoon|evening|night>
        if "--period" in args:
            idx = args.index("--period")
            if idx + 1 < len(args):
                kwargs["period"] = args[idx + 1]

    # Handle gesture-specific args
    if subcommand in ("gesture", "record"):
        # --type <gesture_type>
        if "--type" in args:
            idx = args.index("--type")
            if idx + 1 < len(args):
                kwargs["type"] = args[idx + 1]
        # --plan <plan_name>
        if "--plan" in args:
            idx = args.index("--plan")
            if idx + 1 < len(args):
                kwargs["plan"] = args[idx + 1]
        # --summary <text> (can also be positional after flags)
        if "--summary" in args:
            idx = args.index("--summary")
            if idx + 1 < len(args):
                # Collect all args after --summary until next flag
                summary_parts = []
                for j in range(idx + 1, len(args)):
                    if args[j].startswith("--"):
                        break
                    summary_parts.append(args[j])
                kwargs["summary"] = " ".join(summary_parts)
        # --files <file1,file2,...>
        if "--files" in args:
            idx = args.index("--files")
            if idx + 1 < len(args):
                kwargs["files"] = args[idx + 1].split(",")

    # Handle end-specific args
    if subcommand in ("end", "close"):
        # --letter <text>
        if "--letter" in args:
            idx = args.index("--letter")
            if idx + 1 < len(args):
                # Collect all args after --letter until next flag
                letter_parts = []
                for j in range(idx + 1, len(args)):
                    if args[j].startswith("--"):
                        break
                    letter_parts.append(args[j])
                kwargs["letter"] = " ".join(letter_parts)

    # Collect positional args (after subcommand, excluding flags)
    positional = []
    skip_next = False
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg in SESSION_SUBCOMMAND_MAP:
            continue
        if arg.startswith("--"):
            # Skip flag and its value if applicable
            if arg in (
                "--gardener",
                "--period",
                "--type",
                "--plan",
                "--summary",
                "--letter",
                "--files",
            ):
                skip_next = True
            continue
        positional.append(arg)

    # Use positional as summary for gesture if not already set
    if subcommand in ("gesture", "record") and positional and "summary" not in kwargs:
        kwargs["summary"] = " ".join(positional)

    # Use positional as letter for end if not already set
    if subcommand in ("end", "close") and positional and "letter" not in kwargs:
        kwargs["letter"] = " ".join(positional)

    # Project through CLI functor
    from protocols.cli.projection import project_command

    return project_command(
        path=path,
        args=args,
        ctx=ctx,
        kwargs=kwargs,
    )


__all__ = [
    "cmd_session",
    "SESSION_SUBCOMMAND_MAP",
    "GESTURE_TYPES",
]
