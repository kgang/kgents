"""
Chat Resume: Resume a saved chat session.

Provides the kg chat resume command for continuing conversations.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.shared import InvocationContext


async def execute_resume(
    ctx: "InvocationContext",
    identifier: str | None,
) -> int:
    """
    Execute 'kg chat resume <name|id>' - resume a saved session.

    The identifier can be:
    - A session name (user-assigned)
    - A session ID (or prefix)

    Args:
        ctx: CLI invocation context
        identifier: Session name or ID to resume

    Returns:
        Exit code (0 for success)
    """
    from protocols.agentese.chat import get_persistence
    from protocols.cli.shared import OutputFormatter

    output = OutputFormatter(ctx)

    if not identifier:
        output.emit_error("Please specify a session name or ID to resume.")
        output.emit("")
        output.emit("Usage: kg chat resume <name|id>")
        output.emit("")
        output.emit("List available sessions with: kg chat sessions")
        return 1

    try:
        persistence = get_persistence()

        # Try to find session by name first
        session = await persistence.load_by_name(identifier)

        # If not found by name, try by ID
        if session is None:
            session = await persistence.load_session(identifier)

        # If still not found, try as ID prefix
        if session is None:
            sessions = await persistence.list_sessions(limit=100)
            matches = [
                s
                for s in sessions
                if s.session_id.startswith(identifier)
                or (s.name and identifier.lower() in s.name.lower())
            ]

            if len(matches) == 1:
                session = matches[0]
            elif len(matches) > 1:
                output.emit_error(f"Ambiguous identifier '{identifier}'")
                output.emit("")
                output.emit("Matching sessions:")
                for s in matches[:5]:
                    name = s.name or s.session_id[:12]
                    output.emit(f"  - {name} ({s.node_path})")
                return 1

        if session is None:
            output.emit_error(f"No session found: '{identifier}'")
            output.emit("")
            output.emit("List available sessions with: kg chat sessions")
            return 1

        # Session found - now resume it
        if ctx.json_mode:
            # JSON output - return session data
            data = {
                "session": session.to_dict(),
                "status": "loaded",
            }
            output.emit(json.dumps(data, indent=2, default=str))
            return 0

        # Human output - enter chat with loaded session
        output.emit(f"Resuming session: {session.name or session.session_id[:12]}")
        output.emit(f"  Path: {session.node_path}")
        output.emit(f"  Turns: {session.turn_count}")
        output.emit("")

        # Show last few turns for context
        if session.turns:
            output.emit("Recent conversation:")
            output.emit("-" * 40)
            for turn in session.turns[-3:]:
                user_msg = turn.get("user_message", "")[:80]
                assistant_msg = turn.get("assistant_response", "")[:80]
                output.emit(f"  You: {user_msg}...")
                output.emit(f"  AI:  {assistant_msg}...")
            output.emit("-" * 40)
            output.emit("")

        # Now route to the chat projection with the session
        return await _enter_chat_with_session(ctx, session)

    except Exception as e:
        output.emit_error(f"Failed to resume session: {e}")
        return 1


async def _enter_chat_with_session(
    ctx: "InvocationContext",
    session: Any,  # PersistedSession
) -> int:
    """
    Enter interactive chat with a loaded session.

    This restores the session state and enters the chat REPL.
    """
    from protocols.cli.chat_projection import ChatProjection
    from protocols.cli.shared import OutputFormatter
    from protocols.agentese.chat import ChatSession, ChatConfig

    output = OutputFormatter(ctx)

    try:
        # Create a ChatSession from the persisted data
        from bootstrap.umwelt import Umwelt

        # Create minimal umwelt for the observer
        umwelt = Umwelt(
            archetype="human",
            id=session.observer_id,
        )

        # Create session with restored config
        config = ChatConfig(
            context_window=8000,
            max_turns=None,
        )

        chat_session = ChatSession(
            session_id=session.session_id,
            node_path=session.node_path,
            observer=umwelt,
            config=config,
        )

        # Restore turns
        from protocols.agentese.chat.session import Turn, Message
        from datetime import datetime

        for turn_data in session.turns:
            # Reconstruct turns
            user_msg = Message(
                role="user",
                content=turn_data.get("user_message", ""),
            )
            assistant_msg = Message(
                role="assistant",
                content=turn_data.get("assistant_response", ""),
            )

            turn = Turn(
                turn_number=turn_data.get("turn_number", 0),
                user_message=user_msg,
                assistant_response=assistant_msg,
                started_at=datetime.fromisoformat(turn_data.get("started_at", datetime.now().isoformat())),
                completed_at=datetime.fromisoformat(turn_data.get("completed_at", datetime.now().isoformat())),
                tokens_in=turn_data.get("tokens_in", 0),
                tokens_out=turn_data.get("tokens_out", 0),
                context_before=0,
                context_after=0,
            )
            chat_session._turns.append(turn)

        chat_session._current_turn = len(chat_session._turns)
        chat_session._entropy = session.entropy

        # Activate if needed
        if chat_session.state.value == "dormant":
            chat_session.activate()

        # Determine entity name
        if "soul" in session.node_path:
            entity_name = "K-gent"
        elif "citizen" in session.node_path:
            parts = session.node_path.split(".")
            entity_name = parts[-2] if len(parts) >= 2 else "Citizen"
        else:
            entity_name = "Agent"

        # Enter chat projection
        projection = ChatProjection(
            session=chat_session,
            entity_name=entity_name,
            json_output=ctx.json_mode,
        )

        return await projection.run()

    except ImportError as e:
        output.emit_error(f"Chat module not available: {e}")
        output.emit("")
        output.emit("Install chat dependencies or check imports.")
        return 1
    except Exception as e:
        output.emit_error(f"Failed to enter chat: {e}")
        return 1


__all__ = ["execute_resume"]
