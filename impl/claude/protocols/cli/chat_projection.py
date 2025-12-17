"""
Chat Projection: Interactive REPL for AGENTESE chat affordances.

This module implements the CLI chat interface from spec/protocols/chat.md Part VI.
When a user invokes a path with Interactivity.INTERACTIVE dimension, this projection
provides a dedicated REPL experience for conversational interaction.

The ChatProjection:
- Wraps ChatSession from protocols.agentese.chat
- Provides interactive input loop with streaming output
- Supports in-chat commands (/history, /metrics, /reset, etc.)
- Displays context utilization and cost indicators
- Handles graceful entropy depletion

Usage:
    # Called by CLIProjection when routing INTERACTIVE paths
    projection = ChatProjection(session, renderer)
    await projection.run()

    # Or from CLI handlers
    from protocols.cli.chat_projection import run_chat_repl
    run_chat_repl("self.soul", observer)
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from services.chat import ChatSession
    from protocols.agentese.node import Observer

# Rich imports for beautiful output (graceful degradation)
try:
    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None  # type: ignore[misc, assignment]
    Live = None  # type: ignore[misc, assignment]
    Panel = None  # type: ignore[misc, assignment]
    Text = None  # type: ignore[misc, assignment]


# =============================================================================
# Constants
# =============================================================================

# Chat commands (in-REPL)
CHAT_COMMANDS = frozenset({
    "/exit", "/quit", "/q",
    "/history", "/h",
    "/context", "/c",
    "/metrics", "/m",
    "/reset", "/r",
    "/save", "/s",
    "/load", "/l",
    "/persona", "/p",
    "/help", "/?",
})

# Visual indicators
INDICATORS = {
    "streaming": "...",
    "thinking": "...",
    "done": "",
    "error": "!",
}


# =============================================================================
# ChatRenderer: Message and streaming UI
# =============================================================================


@dataclass
class ChatRenderer:
    """
    Renders chat messages and streaming responses.

    Provides:
    - Message bubble styling (user/assistant)
    - Streaming progress indicator
    - Context utilization gauge
    - Cost display
    """

    entity_name: str = "K-gent"
    user_name: str = "You"
    show_metrics: bool = True
    use_rich: bool = RICH_AVAILABLE

    _console: Any = field(default=None, init=False)

    def __post_init__(self) -> None:
        if self.use_rich and Console is not None:
            self._console = Console()

    def render_welcome(
        self,
        node_path: str,
        session_id: str,
    ) -> str:
        """Render welcome message."""
        lines = [
            "",
            f"  {self.entity_name}",
            "  " + "=" * 60,
            f"  Session: {session_id[:8]}...",
            f"  Path: {node_path}",
            "",
            "  Commands: /help | /history | /metrics | /exit",
            "  " + "-" * 60,
            "",
        ]
        return "\n".join(lines)

    def render_user_message(self, message: str) -> str:
        """Render user message."""
        return f"\n  [{self.user_name}] {message}\n"

    def render_assistant_start(self) -> str:
        """Render start of assistant response."""
        return f"\n  [{self.entity_name}] "

    def render_streaming_token(self, token: str) -> str:
        """Render a streaming token."""
        return token

    def render_assistant_end(self) -> str:
        """Render end of assistant response."""
        return "\n"

    def render_status_bar(
        self,
        turn: int,
        context_util: float,
        cost_usd: float,
        entropy: float,
    ) -> str:
        """Render status bar with metrics."""
        # Context gauge
        ctx_pct = int(context_util * 100)
        ctx_bar = self._render_gauge(context_util)

        # Entropy gauge
        entropy_bar = self._render_gauge(entropy)

        return (
            f"\n  [Turn: {turn} | Context: {ctx_bar} {ctx_pct}% | "
            f"Cost: ${cost_usd:.4f} | Entropy: {entropy_bar}]\n"
        )

    def render_history(self, turns: list[dict[str, Any]], limit: int = 5) -> str:
        """Render conversation history."""
        if not turns:
            return "\n  [No conversation history yet]\n"

        lines = ["\n  [History]", "  " + "-" * 40]
        for turn in turns[-limit:]:
            user_msg = turn.get("user_message", "")[:50]
            asst_msg = turn.get("assistant_response", "")[:50]
            lines.append(f"  #{turn.get('turn_number', '?')}:")
            lines.append(f"    You: {user_msg}...")
            lines.append(f"    {self.entity_name}: {asst_msg}...")
        lines.append("  " + "-" * 40 + "\n")
        return "\n".join(lines)

    def render_metrics(self, metrics: dict[str, Any]) -> str:
        """Render session metrics."""
        lines = [
            "\n  [Metrics]",
            "  " + "-" * 40,
            f"  Session: {metrics.get('session_id', 'unknown')}",
            f"  State: {metrics.get('state', 'unknown')}",
            f"  Turns: {metrics.get('turns_completed', 0)}",
            f"  Tokens In: {metrics.get('tokens_in', 0):,}",
            f"  Tokens Out: {metrics.get('tokens_out', 0):,}",
            f"  Avg Latency: {metrics.get('average_turn_latency', 0):.2f}s",
            f"  Context Util: {metrics.get('context_utilization', 0):.1%}",
            f"  Entropy: {metrics.get('entropy', 0):.3f}",
            f"  Est. Cost: ${metrics.get('estimated_cost_usd', 0):.6f}",
            "  " + "-" * 40 + "\n",
        ]
        return "\n".join(lines)

    def render_context(self, context: dict[str, Any]) -> str:
        """Render context window info."""
        lines = [
            "\n  [Context Window]",
            "  " + "-" * 40,
            f"  Utilization: {context.get('utilization', 0):.1%}",
            f"  Window Size: {context.get('window_size', 0):,} tokens",
            f"  Strategy: {context.get('strategy', 'unknown')}",
            "  " + "-" * 40 + "\n",
        ]
        return "\n".join(lines)

    def render_help(self) -> str:
        """Render help message."""
        lines = [
            "\n  [Chat Commands]",
            "  " + "-" * 40,
            "  /exit, /quit, /q   Exit chat",
            "  /history, /h [n]   Show last n turns",
            "  /context, /c       Show context window",
            "  /metrics, /m       Show session metrics",
            "  /reset, /r         Reset conversation",
            "  /save, /s [name]   Save session",
            "  /load, /l <name>   Load saved session",
            "  /persona, /p       Show entity personality",
            "  /help, /?          Show this help",
            "  " + "-" * 40,
            "",
            "  Just type to chat!",
            "\n",
        ]
        return "\n".join(lines)

    def render_error(self, error: str) -> str:
        """Render error message."""
        return f"\n  [!] Error: {error}\n"

    def render_info(self, info: str) -> str:
        """Render info message."""
        return f"\n  [i] {info}\n"

    def render_goodbye(self, metrics: dict[str, Any]) -> str:
        """Render goodbye message with summary."""
        return (
            f"\n  Session ended. "
            f"Turns: {metrics.get('turns_completed', 0)}, "
            f"Cost: ${metrics.get('estimated_cost_usd', 0):.4f}\n"
        )

    def _render_gauge(self, value: float, width: int = 8) -> str:
        """Render a mini gauge bar."""
        filled = int(value * width)
        filled = max(0, min(width, filled))
        # Use ASCII-safe characters for gauge
        return "#" * filled + "-" * (width - filled)


# =============================================================================
# ChatProjection: The Interactive REPL
# =============================================================================


@dataclass
class ChatProjection:
    """
    Interactive REPL for chat sessions.

    This is the main projection for AGENTESE paths with
    Interactivity.INTERACTIVE dimension.

    The projection:
    1. Displays welcome message with entity info
    2. Enters interactive input loop
    3. Streams responses as tokens arrive
    4. Shows metrics bar after each turn
    5. Handles in-chat commands
    6. Gracefully handles entropy depletion
    """

    session: "ChatSession"
    renderer: ChatRenderer
    node_path: str = ""

    # State
    _running: bool = field(default=False, init=False)

    async def run(self) -> int:
        """
        Run the chat REPL.

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        self._running = True

        # Show welcome
        welcome = self.renderer.render_welcome(
            self.node_path or self.session.node_path,
            self.session.session_id,
        )
        print(welcome)

        # Main loop
        while self._running:
            try:
                # Check if session is collapsed
                if self.session.is_collapsed:
                    print(self.renderer.render_info(
                        f"Session ended: {self.session.state.value}"
                    ))
                    break

                # Get user input
                try:
                    user_input = input(f"  [{self.renderer.user_name}] ").strip()
                except (EOFError, KeyboardInterrupt):
                    # Ctrl+C or EOF exits gracefully
                    print()  # Newline after ^C
                    break

                if not user_input:
                    continue

                # Handle exit commands (bare words)
                if user_input.lower() in ("q", "quit", "exit", "bye"):
                    break

                # Handle commands
                if user_input.startswith("/"):
                    result = await self._handle_command(user_input)
                    if result == "exit":
                        break
                    continue

                # Send message and stream response
                await self._send_and_stream(user_input)

            except KeyboardInterrupt:
                # Ctrl+C during streaming - exit gracefully
                print("\n")
                print(self.renderer.render_info("Interrupted"))
                break

        # Show goodbye
        metrics = self.session.get_metrics()
        print(self.renderer.render_goodbye(metrics))

        return 0

    async def _send_and_stream(self, message: str) -> None:
        """Send message and stream the response."""
        # Show user message echo (already typed, so just marker)
        print(self.renderer.render_user_message(message))

        # Start assistant response
        sys.stdout.write(self.renderer.render_assistant_start())
        sys.stdout.flush()

        try:
            # Stream response
            async for token in self.session.stream(message):
                sys.stdout.write(self.renderer.render_streaming_token(token))
                sys.stdout.flush()

            # End response
            print(self.renderer.render_assistant_end())

            # Show metrics bar
            if self.renderer.show_metrics:
                metrics = self.session.get_metrics()
                status = self.renderer.render_status_bar(
                    turn=metrics.get("turns_completed", 0),
                    context_util=metrics.get("context_utilization", 0),
                    cost_usd=metrics.get("estimated_cost_usd", 0),
                    entropy=metrics.get("entropy", 1.0),
                )
                print(status)

        except RuntimeError as e:
            print(self.renderer.render_error(str(e)))

    async def _handle_command(self, command: str) -> str | None:
        """
        Handle in-chat commands.

        Returns:
            "exit" to exit the REPL, None otherwise
        """
        parts = command.lower().split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        match cmd:
            case "/exit" | "/quit" | "/q":
                return "exit"

            case "/history" | "/h":
                limit = int(args[0]) if args else 5
                turns = self.session.get_history(limit=limit)
                turn_dicts = [t.to_dict() for t in turns]
                print(self.renderer.render_history(turn_dicts, limit))

            case "/context" | "/c":
                context = {
                    "utilization": self.session.get_context_utilization(),
                    "window_size": self.session.config.context_window,
                    "strategy": self.session.config.context_strategy.value,
                }
                print(self.renderer.render_context(context))

            case "/metrics" | "/m":
                metrics = self.session.get_metrics()
                print(self.renderer.render_metrics(metrics))

            case "/reset" | "/r":
                self.session.reset()
                print(self.renderer.render_info("Session reset"))

            case "/save" | "/s":
                # Phase 4: Save session to D-gent
                name = args[0] if args else None
                await self._save_session(name)

            case "/load" | "/l":
                # Phase 4: Load session from D-gent
                name = args[0] if args else None
                if not name:
                    print(self.renderer.render_error("Please provide a session name or ID"))
                else:
                    await self._load_session(name)

            case "/persona" | "/p":
                # Show entity personality/config
                config_info = {
                    "context_window": self.session.config.context_window,
                    "context_strategy": self.session.config.context_strategy.value,
                    "max_turns": self.session.config.max_turns,
                    "entropy_budget": self.session.config.entropy_budget,
                }
                lines = [
                    "\n  [Persona Configuration]",
                    "  " + "-" * 40,
                ]
                for k, v in config_info.items():
                    lines.append(f"  {k}: {v}")
                lines.append("  " + "-" * 40 + "\n")
                print("\n".join(lines))

            case "/help" | "/?":
                print(self.renderer.render_help())

            case _:
                print(self.renderer.render_error(f"Unknown command: {cmd}"))

        return None

    async def _save_session(self, name: str | None) -> None:
        """Save the current session to D-gent storage."""
        try:
            from services.chat import get_persistence

            persistence = get_persistence()

            # Set name on session if provided
            if name:
                self.session.set_name(name)

            # Save
            datum_id = await persistence.save_session(self.session, name=name)

            # Feedback
            display_name = name or self.session.session_id[:12]
            print(self.renderer.render_info(f"Session saved as '{display_name}'"))
            print(self.renderer.render_info(f"Resume with: kg chat resume {display_name}"))

        except ImportError:
            print(self.renderer.render_error("Persistence module not available"))
        except Exception as e:
            print(self.renderer.render_error(f"Failed to save: {e}"))

    async def _load_session(self, identifier: str) -> None:
        """Load a saved session from D-gent storage."""
        try:
            from services.chat import get_persistence, Turn, Message
            from datetime import datetime

            persistence = get_persistence()

            # Try to find session by name first
            persisted = await persistence.load_by_name(identifier)

            # If not found by name, try by ID
            if persisted is None:
                persisted = await persistence.load_session(identifier)

            if persisted is None:
                print(self.renderer.render_error(f"Session not found: {identifier}"))
                print(self.renderer.render_info("List sessions with: kg chat sessions"))
                return

            # Restore session state
            self.session.reset()
            self.session._turns.clear()

            for turn_data in persisted.turns:
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
                    started_at=datetime.fromisoformat(
                        turn_data.get("started_at", datetime.now().isoformat())
                    ),
                    completed_at=datetime.fromisoformat(
                        turn_data.get("completed_at", datetime.now().isoformat())
                    ),
                    tokens_in=turn_data.get("tokens_in", 0),
                    tokens_out=turn_data.get("tokens_out", 0),
                    context_before=0,
                    context_after=0,
                )
                self.session._turns.append(turn)

            self.session._current_turn = len(self.session._turns)
            self.session._entropy = persisted.entropy
            if persisted.name:
                self.session._name = persisted.name

            # Feedback
            display_name = persisted.name or persisted.session_id[:12]
            print(self.renderer.render_info(f"Loaded session '{display_name}'"))
            print(self.renderer.render_info(f"Turns: {persisted.turn_count}"))

            # Show recent history
            if persisted.turns:
                print(self.renderer.render_history(persisted.turns, limit=3))

        except ImportError:
            print(self.renderer.render_error("Persistence module not available"))
        except Exception as e:
            print(self.renderer.render_error(f"Failed to load: {e}"))


# =============================================================================
# Entry Points
# =============================================================================


def run_chat_repl(
    node_path: str,
    observer: "Observer | Umwelt[Any, Any]",
    entity_name: str | None = None,
    one_shot_message: str | None = None,
) -> int:
    """
    Run the chat REPL for an AGENTESE node path.

    This is the main entry point for CLI handlers.

    Args:
        node_path: AGENTESE path (e.g., "self.soul", "world.town.citizen.elara")
        observer: Observer or Umwelt
        entity_name: Display name for the entity (default: derived from path)
        one_shot_message: If provided, send one message and exit

    Returns:
        Exit code
    """
    # Derive entity name from path if not provided
    if entity_name is None:
        parts = node_path.split(".")
        if "soul" in parts:
            entity_name = "K-gent"
        elif "citizen" in parts and len(parts) > 3:
            entity_name = parts[3].title()  # world.town.citizen.<name>
        else:
            entity_name = parts[-1].title()

    # Create session via chat resolver
    from protocols.agentese.contexts.chat_resolver import get_chat_resolver

    resolver = get_chat_resolver()
    chat_node = resolver.resolve(node_path)

    async def _run() -> int:
        # Get or create session
        session = await chat_node._get_or_create_session(observer)

        # One-shot mode
        if one_shot_message:
            try:
                response = await session.send(one_shot_message)
                print(response)
                return 0
            except RuntimeError as e:
                print(f"Error: {e}")
                return 1

        # Interactive REPL
        renderer = ChatRenderer(entity_name=entity_name)
        projection = ChatProjection(
            session=session,
            renderer=renderer,
            node_path=node_path,
        )
        return await projection.run()

    # Handle case where we're already inside an event loop
    # (e.g., called from async cmd_soul handler)
    try:
        loop = asyncio.get_running_loop()
        # Already in an event loop - run in a new thread to avoid nested asyncio.run
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, _run())
            return future.result()
    except RuntimeError:
        # No running event loop - safe to use asyncio.run directly
        return asyncio.run(_run())


def run_chat_one_shot(
    node_path: str,
    message: str,
    observer: "Observer | Umwelt[Any, Any]",
    json_output: bool = False,
) -> int:
    """
    Send a single message and exit.

    Args:
        node_path: AGENTESE path
        message: Message to send
        observer: Observer or Umwelt
        json_output: If True, output as JSON

    Returns:
        Exit code
    """
    import json as json_lib

    from protocols.agentese.contexts.chat_resolver import get_chat_resolver

    resolver = get_chat_resolver()
    chat_node = resolver.resolve(node_path)

    async def _run() -> int:
        session = await chat_node._get_or_create_session(observer)
        try:
            response = await session.send(message)
            if json_output:
                output = {
                    "response": response,
                    "turn": session.turn_count,
                    "metrics": session.get_metrics(),
                }
                print(json_lib.dumps(output, indent=2, default=str))
            else:
                print(response)
            return 0
        except RuntimeError as e:
            if json_output:
                print(json_lib.dumps({"error": str(e)}))
            else:
                print(f"Error: {e}")
            return 1

    # Handle case where we're already inside an event loop
    try:
        loop = asyncio.get_running_loop()
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, _run())
            return future.result()
    except RuntimeError:
        return asyncio.run(_run())


__all__ = [
    "ChatRenderer",
    "ChatProjection",
    "run_chat_repl",
    "run_chat_one_shot",
    "CHAT_COMMANDS",
]
