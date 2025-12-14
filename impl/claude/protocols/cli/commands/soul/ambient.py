"""
Ambient commands: stream, watch.

These provide long-running ambient presence modes for K-gent Soul.
"""

from __future__ import annotations

import asyncio
import signal
from pathlib import Path
from typing import TYPE_CHECKING, Any

from protocols.cli.shared import InvocationContext, OutputFormatter
from protocols.cli.shared.streaming import invoke_with_retry

if TYPE_CHECKING:
    pass


async def execute_stream(
    ctx: InvocationContext,
    soul: Any,
    pulse_interval: int,
    show_pulses: bool,
) -> int:
    """
    Handle 'soul stream' command: ambient presence mode.

    Uses KgentFlux in DORMANT mode with manual event loop:
    - Pulse events emitted at regular intervals
    - User input from stdin processed via flux.invoke()
    - Graceful shutdown on Ctrl+C, SIGTERM, or EOF
    - Mode switching via /mode command
    - LLM timeout to prevent hangs
    - Retry logic for transient failures
    """
    import sys

    from agents.k.events import (
        SoulEventType,
        dialogue_turn_event,
        pulse_event,
    )
    from agents.k.flux import KgentFlux, KgentFluxConfig

    output = OutputFormatter(ctx)

    # Create flux with the existing soul (pulses handled manually)
    config = KgentFluxConfig(
        pulse_enabled=False,  # We handle pulses ourselves
        entropy_budget=float("inf"),
    )
    flux = KgentFlux(soul=soul, config=config)

    # Track current mode for /mode switching
    current_mode = "reflect"
    valid_modes = ("reflect", "advise", "challenge", "explore")

    # Print startup banner
    output.emit(
        "[SOUL:STREAM] Starting (ambient mode)",
        {"status": "starting", "pulse_interval": pulse_interval},
    )

    stop_event = asyncio.Event()

    # Signal handler for graceful shutdown
    def handle_signal(signum: int, frame: Any) -> None:
        stop_event.set()

    # Install signal handlers
    original_sigterm = signal.signal(signal.SIGTERM, handle_signal)
    original_sigint = signal.signal(signal.SIGINT, handle_signal)

    async def pulse_emitter() -> None:
        """Emit pulse events at regular intervals."""
        while not stop_event.is_set():
            await asyncio.sleep(pulse_interval)
            if stop_event.is_set():
                break

            state = flux.soul.manifest()
            event = pulse_event(
                interactions_count=state.interactions_count,
                tokens_used_session=state.tokens_used_session,
                active_mode=state.active_mode.value,
                is_healthy=True,
            )
            if show_pulses:
                _format_pulse(event, ctx)

    async def stdin_processor() -> None:
        """Read stdin and process via flux.invoke()."""
        nonlocal current_mode
        loop = asyncio.get_running_loop()
        while not stop_event.is_set():
            try:
                # Read line from stdin in thread pool
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:  # EOF
                    break
                line = line.strip()
                if not line:
                    continue

                # Handle /mode command
                if line.startswith("/mode "):
                    new_mode = line[6:].strip().lower()
                    if new_mode in valid_modes:
                        current_mode = new_mode
                        output.emit(
                            f"[SOUL:STREAM] Mode: {new_mode}",
                            {"mode": new_mode},
                        )
                    else:
                        output.emit(
                            f"[SOUL:STREAM] Invalid mode: {new_mode}. Valid: {', '.join(valid_modes)}",
                            {"error": f"Invalid mode: {new_mode}"},
                        )
                    continue

                # Create dialogue event and process with retry/timeout
                event = dialogue_turn_event(
                    message=line,
                    mode=current_mode,
                    is_request=True,
                )
                try:
                    result = await invoke_with_retry(flux, event)

                    # Display result
                    if result.event_type == SoulEventType.DIALOGUE_TURN:
                        _format_dialogue_turn(result, ctx)
                    elif result.event_type == SoulEventType.ERROR:
                        _format_error(result, ctx)
                except asyncio.TimeoutError as e:
                    output.emit(
                        "[SOUL:STREAM] Response timeout",
                        {"error": "timeout", "message": str(e)},
                    )
                except Exception as e:
                    output.emit(
                        f"[SOUL:STREAM] Error after retries: {e}",
                        {"error": str(e), "retries_exhausted": True},
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                output.emit(
                    f"[SOUL:STREAM] Error: {e}",
                    {"error": str(e)},
                )

    # Start background tasks
    pulse_task = asyncio.create_task(pulse_emitter(), name="pulse-emitter")
    stdin_task = asyncio.create_task(stdin_processor(), name="stdin-processor")

    try:
        # Wait for stdin processor to complete (EOF or error) or stop_event
        done, pending = await asyncio.wait(
            [stdin_task, asyncio.create_task(stop_event.wait())],
            return_when=asyncio.FIRST_COMPLETED,
        )
    except KeyboardInterrupt:
        pass
    finally:
        # Restore signal handlers
        signal.signal(signal.SIGTERM, original_sigterm)
        signal.signal(signal.SIGINT, original_sigint)

        # Cleanup
        stop_event.set()
        pulse_task.cancel()
        stdin_task.cancel()
        try:
            await pulse_task
        except asyncio.CancelledError:
            pass
        try:
            await stdin_task
        except asyncio.CancelledError:
            pass

        # Show stats on shutdown
        interactions = flux.soul.manifest().interactions_count
        output.emit(
            f"[SOUL:STREAM] Stopped ({interactions} interactions)",
            {"status": "stopped", "interactions": interactions},
        )

    return 0


async def execute_watch(
    ctx: InvocationContext,
    soul: Any,
    watch_path: str | None,
) -> int:
    """
    Handle 'soul watch' command: ambient file watching.

    Uses KgentWatcher to monitor codebase and emit suggestions
    based on heuristics (complexity, naming, patterns, tests, docs).
    """
    from agents.k.watcher import KgentWatcher, WatcherConfig

    output = OutputFormatter(ctx)

    # Determine path to watch
    root = Path(watch_path) if watch_path else Path.cwd()
    if not root.exists():
        output.emit(
            f"[SOUL:WATCH] Error: Path does not exist: {root}",
            {"error": f"Path does not exist: {root}"},
        )
        return 1

    # Create watcher
    config = WatcherConfig(project_root=root)
    watcher = KgentWatcher(config=config)

    # Track notifications for display
    notification_count = 0

    def on_notification(n: Any) -> None:
        nonlocal notification_count
        notification_count += 1

        if ctx.json_mode:
            import json

            data = {
                "timestamp": n.timestamp.isoformat(),
                "heuristic": n.heuristic,
                "message": n.message,
                "severity": n.severity,
                "file_path": n.file_path,
                "details": n.details,
            }
            output.emit(json.dumps(data), data)
        else:
            # Human-friendly output
            severity_icons = {
                "info": "ℹ",
                "warning": "⚠",
                "suggestion": "💡",
            }
            icon = severity_icons.get(n.severity, "•")
            ts = n.timestamp.strftime("%H:%M:%S")
            relative_path = Path(n.file_path).name

            output.emit(
                f"  [{ts}] {icon} [{n.heuristic}] {relative_path}",
                {"notification": True},
            )
            output.emit(f"      {n.message}", {})

    watcher.subscribe(on_notification)

    # Print startup banner
    output.emit(
        f"[SOUL:WATCH] Watching: {root}",
        {"status": "starting", "path": str(root)},
    )
    output.emit("  Press Ctrl+C to stop", {})
    output.emit(
        "  Heuristics: complexity, naming, patterns, tests, docs",
        {"heuristics": ["complexity", "naming", "patterns", "tests", "docs"]},
    )
    output.emit("", {})

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    # Use asyncio signal handlers for proper async integration
    def handle_signal() -> None:
        stop_event.set()

    # Track if we're using asyncio handlers or traditional
    using_asyncio_signals = True
    original_sigint: Any = None
    original_sigterm: Any = None

    # Install signal handlers using asyncio (works properly with event loop)
    try:
        loop.add_signal_handler(signal.SIGINT, handle_signal)
        loop.add_signal_handler(signal.SIGTERM, handle_signal)
    except NotImplementedError:
        # Windows doesn't support add_signal_handler, fall back to traditional
        using_asyncio_signals = False
        original_sigint = signal.signal(signal.SIGINT, lambda s, f: stop_event.set())
        original_sigterm = signal.signal(signal.SIGTERM, lambda s, f: stop_event.set())

    try:
        # Start watching
        await watcher.start()

        # Wait for stop signal
        await stop_event.wait()

    except KeyboardInterrupt:
        pass
    finally:
        # Remove signal handlers
        if using_asyncio_signals:
            try:
                loop.remove_signal_handler(signal.SIGINT)
                loop.remove_signal_handler(signal.SIGTERM)
            except (ValueError, RuntimeError):
                pass
        else:
            # Restore original handlers on Windows
            if original_sigint is not None:
                signal.signal(signal.SIGINT, original_sigint)
            if original_sigterm is not None:
                signal.signal(signal.SIGTERM, original_sigterm)

        # Stop watcher
        await watcher.stop()

        output.emit(
            f"[SOUL:WATCH] Stopped ({notification_count} notifications)",
            {"status": "stopped", "notifications": notification_count},
        )

    return 0


def _format_pulse(event: Any, ctx: InvocationContext) -> None:
    """Format a pulse event for terminal output."""
    import json

    output = OutputFormatter(ctx)
    payload = event.payload
    timestamp = event.timestamp.strftime("%H:%M:%S")

    if ctx.json_mode:
        output.emit(json.dumps(event.to_dict(), indent=2), event.to_dict())
    else:
        mode = payload.get("active_mode", "reflect")
        interactions = payload.get("interactions_count", 0)
        output.emit(
            f"  [{timestamp}] pulse | mode: {mode} | interactions: {interactions}",
            event.to_dict(),
        )


def _format_dialogue_turn(event: Any, ctx: InvocationContext) -> None:
    """Format a dialogue turn event for terminal output."""
    import json

    output = OutputFormatter(ctx)
    payload = event.payload

    if ctx.json_mode:
        output.emit(json.dumps(event.to_dict(), indent=2), event.to_dict())
    else:
        # Only format responses, not requests
        if not payload.get("is_request", True):
            mode = payload.get("mode", "reflect")
            response = payload.get("response", "")
            tokens = payload.get("tokens_used", 0)

            mode_icons = {
                "reflect": "~",
                "advise": ">",
                "challenge": "!",
                "explore": "?",
            }
            icon = mode_icons.get(mode, "*")

            lines = [
                f"\n[K-gent:{mode.upper()}] {icon}",
                response,
            ]

            if tokens > 0:
                lines.append(f"  [{tokens} tokens]")

            output.emit("\n".join(lines), event.to_dict())


def _format_error(event: Any, ctx: InvocationContext) -> None:
    """Format an error event for terminal output."""
    import json

    output = OutputFormatter(ctx)
    payload = event.payload

    if ctx.json_mode:
        output.emit(json.dumps(event.to_dict(), indent=2), event.to_dict())
    else:
        error = payload.get("error", "Unknown error")
        error_type = payload.get("error_type", "Error")
        output.emit(f"[SOUL:ERROR] {error_type}: {error}", event.to_dict())
