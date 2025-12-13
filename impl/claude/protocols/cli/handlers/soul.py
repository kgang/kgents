"""
Soul Handler: K-gent Digital Soul CLI interface.

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
    kgents soul stream             # Ambient FLOWING mode (Phase 3)
    kgents soul starters           # Show starter prompts
    kgents soul manifest           # Show current soul state

Example:
    kgents soul challenge "I'm stuck on architecture"
    -> Response should feel like Kent on his best day, reminding
       Kent on his worst day what he actually believes.

    kgents soul stream
    -> K-gent runs in ambient FLOWING mode, emitting pulses
       and responding to user input from stdin.
"""

from __future__ import annotations

import asyncio
import signal
from typing import TYPE_CHECKING, Any, AsyncIterator

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for soul command."""
    print(__doc__)
    print()
    print("MODES:")
    print("  reflect             Mirror back for examination (default)")
    print("  advise              Offer preference-aligned suggestions")
    print("  challenge           Push back constructively, find weaknesses")
    print("  explore             Follow tangents, generate hypotheses")
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


def cmd_soul(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    K-gent Soul: The Middleware of Consciousness.

    kgents soul - Engage in self-dialogue with your digital simulacra.

    Reflector Integration:
    - If ctx is provided, outputs via dual-channel (human + semantic)
    - Human output goes to stdout
    - Semantic output goes to FD3 (for agent consumption)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("soul", args)
        except ImportError:
            pass

    # Parse args
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    json_mode = "--json" in args
    quick_mode = "--quick" in args
    deep_mode = "--deep" in args

    # Determine budget tier
    budget = "dialogue"  # Default
    if quick_mode:
        budget = "whisper"
    elif deep_mode:
        budget = "deep"

    # Get mode/subcommand and prompt
    mode = None
    prompt_parts: list[str] = []

    for arg in args:
        if arg.startswith("-"):
            continue
        if mode is None:
            mode = arg
        else:
            prompt_parts.append(arg)

    prompt = " ".join(prompt_parts) if prompt_parts else None

    # Default mode is reflect
    if mode is None:
        mode = "reflect"

    # Run async handler
    return asyncio.run(
        _async_soul(
            mode=mode,
            prompt=prompt,
            budget=budget,
            json_mode=json_mode,
            ctx=ctx,
            args=args,
        )
    )


async def _async_soul(
    mode: str,
    prompt: str | None,
    budget: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
    args: list[str],
) -> int:
    """Async implementation of soul command."""
    try:
        from agents.k import (
            BudgetTier,
            DialogueMode,
            KgentSoul,
        )

        # Get or create soul instance
        soul = _get_soul()

        # Parse audit options
        summary_mode = "--summary" in args
        limit = 10
        for i, arg in enumerate(args):
            if arg == "--limit" and i + 1 < len(args):
                try:
                    limit = int(args[i + 1])
                except ValueError:
                    pass

        # Parse stream-specific options
        pulse_interval = 30
        show_pulses = "--no-pulses" not in args
        for i, arg in enumerate(args):
            if arg == "--pulse-interval" and i + 1 < len(args):
                try:
                    pulse_interval = int(args[i + 1])
                except ValueError:
                    pass

        # Handle special commands
        # Parse watch-specific options
        watch_path = None
        for i, arg in enumerate(args):
            if arg == "--path" and i + 1 < len(args):
                watch_path = args[i + 1]
                break

        match mode.lower():
            case "stream":
                return await _handle_stream(
                    soul,
                    pulse_interval=pulse_interval,
                    show_pulses=show_pulses,
                    json_mode=json_mode,
                    ctx=ctx,
                )
            case "watch":
                return await _handle_watch(
                    soul,
                    watch_path=watch_path,
                    json_mode=json_mode,
                    ctx=ctx,
                )
            case "starters":
                return await _handle_starters(soul, json_mode, ctx)
            case "manifest":
                return await _handle_manifest(soul, json_mode, ctx)
            case "eigenvectors":
                return await _handle_eigenvectors(soul, json_mode, ctx)
            case "audit":
                return _handle_audit(soul, json_mode, summary_mode, limit, ctx)
            case "garden":
                sync_hypnagogia = "--sync" in args
                return await _handle_garden(soul, json_mode, sync_hypnagogia, ctx)
            case "validate":
                # Get file path from remaining args
                validate_path = None
                for arg in args:
                    if not arg.startswith("-") and arg != "validate":
                        validate_path = arg
                        break
                use_llm = "--deep" in args
                return await _handle_validate(
                    soul, validate_path, use_llm, json_mode, ctx
                )
            case "dream":
                dry_run = "--dry-run" in args
                return await _handle_dream(soul, dry_run, json_mode, ctx)
            case "history":
                return await _handle_history(limit, json_mode, ctx)
            case "propose":
                # Get description from remaining args
                desc_parts = [
                    a for a in args if not a.startswith("-") and a != "propose"
                ]
                description = " ".join(desc_parts) if desc_parts else None
                return await _handle_propose(description, json_mode, ctx)
            case "commit":
                # Get change ID from remaining args
                change_id = None
                for arg in args:
                    if not arg.startswith("-") and arg != "commit":
                        change_id = arg
                        break
                return await _handle_commit(change_id, json_mode, ctx)
            case "crystallize":
                # Get name from remaining args
                name_parts = [
                    a for a in args if not a.startswith("-") and a != "crystallize"
                ]
                name = " ".join(name_parts) if name_parts else None
                return await _handle_crystallize(name, json_mode, ctx)
            case "resume":
                # Get crystal ID from remaining args
                crystal_id = None
                for arg in args:
                    if not arg.startswith("-") and arg != "resume":
                        crystal_id = arg
                        break
                return await _handle_resume(crystal_id, json_mode, ctx)

        # Map mode string to DialogueMode
        mode_map = {
            "reflect": DialogueMode.REFLECT,
            "advise": DialogueMode.ADVISE,
            "challenge": DialogueMode.CHALLENGE,
            "explore": DialogueMode.EXPLORE,
        }

        dialogue_mode = mode_map.get(mode.lower())
        if dialogue_mode is None:
            _emit_output(
                f"[SOUL] X Unknown mode: {mode}",
                {"error": f"Unknown mode: {mode}"},
                ctx,
            )
            return 1

        # Map budget string to BudgetTier
        budget_map = {
            "whisper": BudgetTier.WHISPER,
            "dialogue": BudgetTier.DIALOGUE,
            "deep": BudgetTier.DEEP,
        }
        budget_tier = budget_map.get(budget, BudgetTier.DIALOGUE)

        # If no prompt, enter interactive mode or show starter
        if prompt is None:
            return await _handle_interactive(
                soul, dialogue_mode, budget_tier, json_mode, ctx
            )

        # Single dialogue turn
        return await _handle_dialogue(
            soul, dialogue_mode, prompt, budget_tier, json_mode, ctx
        )

    except ImportError as e:
        _emit_output(
            f"[SOUL] X K-gent module not available: {e}",
            {"error": f"K-gent module not available: {e}"},
            ctx,
        )
        return 1

    except Exception as e:
        _emit_output(
            f"[SOUL] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


# Module-level soul instance (singleton for CLI session)
_soul_instance: Any = None


def _get_soul() -> Any:
    """
    Get or create the K-gent Soul instance.

    Resolution order:
    1. Try to get from lifecycle state (shared across CLI session)
    2. Fall back to module-level singleton (in-memory)
    """
    from agents.k import KgentSoul

    global _soul_instance

    # Try to get from lifecycle state first
    try:
        from protocols.cli.hollow import get_lifecycle_state

        lifecycle_state = get_lifecycle_state()
        if lifecycle_state is not None:
            soul = getattr(lifecycle_state, "soul", None)
            if soul is not None:
                return soul
    except ImportError:
        pass

    # Fall back to module-level singleton
    if _soul_instance is None:
        _soul_instance = KgentSoul()
    return _soul_instance


def set_soul(soul: Any) -> None:
    """Set the module-level soul instance."""
    global _soul_instance
    _soul_instance = soul


async def _handle_dialogue(
    soul: Any,
    mode: Any,  # DialogueMode
    prompt: str,
    budget: Any,  # BudgetTier
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle a single dialogue turn."""
    output = await soul.dialogue(prompt, mode=mode, budget=budget)

    semantic = {
        "mode": output.mode.value,
        "response": output.response,
        "budget_tier": output.budget_tier.value,
        "tokens_used": output.tokens_used,
        "was_template": output.was_template,
        "referenced_preferences": output.referenced_preferences,
        "referenced_patterns": output.referenced_patterns,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(semantic, indent=2), semantic, ctx)
    else:
        # Human-friendly output
        mode_icons = {
            "reflect": "~",
            "advise": ">",
            "challenge": "!",
            "explore": "?",
        }
        icon = mode_icons.get(output.mode.value, "*")
        header = f"[{icon} SOUL:{output.mode.value.upper()}]"

        lines = [header, "", output.response]

        if output.referenced_preferences:
            lines.append("")
            lines.append(
                f"  Principles: {', '.join(output.referenced_preferences[:2])}"
            )

        if output.tokens_used > 0 and not output.was_template:
            lines.append(f"  [{output.tokens_used} tokens]")

        _emit_output("\n".join(lines), semantic, ctx)

    return 0


async def _handle_interactive(
    soul: Any,
    mode: Any,  # DialogueMode
    budget: Any,  # BudgetTier
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle interactive dialogue mode."""
    # Enter mode and show a starter
    entry_message = soul.enter_mode(mode)
    starter = soul.get_starter(mode)

    semantic = {
        "mode": mode.value,
        "entry_message": entry_message,
        "starter": starter,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(semantic, indent=2), semantic, ctx)
    else:
        lines = [
            f"[SOUL] {entry_message}",
            "",
            f'Try: "{starter}"',
            "",
            "Enter your prompt (or 'q' to quit):",
        ]
        _emit_output("\n".join(lines), semantic, ctx)

        # Interactive loop
        try:
            while True:
                try:
                    user_input = input(f"\n[{mode.value}] > ").strip()
                except (KeyboardInterrupt, EOFError):
                    print("\n[SOUL] Goodbye.")
                    return 0

                if user_input.lower() in ("q", "quit", "exit", "bye"):
                    print("[SOUL] Until next time. The patterns will be here.")
                    return 0

                if not user_input:
                    continue

                # Process dialogue
                output = await soul.dialogue(user_input, mode=mode, budget=budget)
                print(f"\n{output.response}")

                if output.referenced_preferences:
                    print(
                        f"\n  Principles: {', '.join(output.referenced_preferences[:2])}"
                    )

        except Exception as e:
            print(f"[SOUL] Error: {e}")
            return 1

    return 0


async def _handle_starters(
    soul: Any,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle 'soul starters' command."""
    from agents.k import all_starters

    starters = all_starters()

    if json_mode:
        import json

        _emit_output(json.dumps(starters, indent=2), {"starters": starters}, ctx)
    else:
        from agents.k import format_all_starters_for_display

        formatted = format_all_starters_for_display()
        _emit_output(formatted, {"starters": starters}, ctx)

    return 0


async def _handle_manifest(
    soul: Any,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle 'soul manifest' command."""
    state = soul.manifest()
    brief = soul.manifest_brief()

    if json_mode:
        import json

        _emit_output(json.dumps(brief, indent=2), brief, ctx)
    else:
        lines = [
            "[SOUL] Manifest",
            "",
            f"  Mode: {state.active_mode.value}",
            f"  Session interactions: {state.interactions_count}",
            f"  Session tokens: {state.tokens_used_session}",
            "",
            "  Eigenvectors:",
        ]

        for name, value in brief["eigenvectors"].items():
            lines.append(f"    {name}: {value:.2f}")

        _emit_output("\n".join(lines), brief, ctx)

    return 0


async def _handle_eigenvectors(
    soul: Any,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle 'soul eigenvectors' command."""
    eigenvectors = soul.eigenvectors

    if json_mode:
        import json

        data = eigenvectors.to_dict()
        _emit_output(json.dumps(data, indent=2), {"eigenvectors": data}, ctx)
    else:
        prompt = eigenvectors.to_system_prompt_section()
        _emit_output(prompt, {"eigenvectors": eigenvectors.to_dict()}, ctx)

    return 0


def _handle_audit(
    soul: Any,
    json_mode: bool,
    summary_mode: bool,
    limit: int,
    ctx: "InvocationContext | None",
) -> int:
    """Handle 'soul audit' command."""
    audit_trail = soul.audit

    if summary_mode:
        # Show summary
        summary = audit_trail.summary()

        if json_mode:
            import json

            _emit_output(json.dumps(summary, indent=2), summary, ctx)
        else:
            formatted = audit_trail.format_summary()
            _emit_output(formatted, summary, ctx)
    else:
        # Show recent entries
        entries = audit_trail.recent(limit)
        entries_data = [e.to_dict() for e in entries]

        if json_mode:
            import json

            _emit_output(
                json.dumps(entries_data, indent=2), {"entries": entries_data}, ctx
            )
        else:
            formatted = audit_trail.format_recent(limit)
            _emit_output(formatted, {"entries": entries_data}, ctx)

    return 0


async def _handle_garden(
    soul: Any,
    json_mode: bool,
    sync_hypnagogia: bool,
    ctx: "InvocationContext | None",
) -> int:
    """
    Handle 'soul garden' command - view PersonaGarden state.

    Shows the current state of the persona garden including:
    - Entry counts by type and lifecycle
    - Established patterns (trees)
    - Recent seeds

    Args:
        soul: KgentSoul instance
        json_mode: Output as JSON
        sync_hypnagogia: Sync patterns from hypnagogia first
        ctx: Invocation context
    """
    from agents.k.garden import get_garden
    from agents.k.hypnagogia import get_hypnagogia

    garden = get_garden()

    # Optionally sync from hypnagogia
    if sync_hypnagogia:
        hypnagogia = get_hypnagogia()
        synced = await garden.sync_from_hypnagogia(hypnagogia)
        if synced > 0:
            _emit_output(
                f"[GARDEN] Synced {synced} pattern(s) from hypnagogia",
                {"synced": synced},
                ctx,
            )

    # Get stats
    stats = await garden.stats()

    if json_mode:
        import json

        data = {
            "total_entries": stats.total_entries,
            "by_type": stats.by_type,
            "by_lifecycle": stats.by_lifecycle,
            "average_confidence": stats.average_confidence,
            "total_evidence": stats.total_evidence,
            "entries": [e.to_dict() for e in garden.entries.values()],
        }
        _emit_output(json.dumps(data, indent=2), data, ctx)
    else:
        # Human-friendly output
        _emit_output(garden.format_summary(), {"stats": stats.__dict__}, ctx)

    return 0


async def _handle_validate(
    soul: Any,
    file_path: str | None,
    use_llm: bool,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """
    Handle 'soul validate' command - check code against principles.

    The Semantic Gatekeeper checks code for principle violations:
    - Heuristic pattern matching (fast, always available)
    - LLM semantic analysis (deeper, requires --deep flag)

    Args:
        soul: KgentSoul instance
        file_path: Path to file to validate
        use_llm: Whether to use LLM for deeper analysis
        json_mode: Output as JSON
        ctx: Invocation context
    """
    from agents.k.gatekeeper import SemanticGatekeeper

    if file_path is None:
        _emit_output(
            "[GATEKEEPER] Error: No file path provided\n"
            "Usage: kgents soul validate <file> [--deep] [--json]",
            {"error": "No file path provided"},
            ctx,
        )
        return 1

    # Create gatekeeper with soul's LLM if available and requested
    llm = soul._llm if use_llm and soul.has_llm else None
    gatekeeper = SemanticGatekeeper(llm=llm, use_llm=use_llm)

    _emit_output(
        f"[GATEKEEPER] Validating: {file_path}" + (" (deep)" if use_llm else ""),
        {"status": "validating", "file": file_path, "deep": use_llm},
        ctx,
    )

    result = await gatekeeper.validate_file(file_path)

    if json_mode:
        import json

        _emit_output(json.dumps(result.to_dict(), indent=2), result.to_dict(), ctx)
    else:
        _emit_output(result.format(), result.to_dict(), ctx)

    return 0 if result.passed else 1


async def _handle_dream(
    soul: Any,
    dry_run: bool,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """
    Handle 'soul dream' command - trigger hypnagogia manually.

    The dream cycle processes accumulated interactions and:
    - Extracts patterns from dialogue history
    - Promotes strong patterns (SEED -> TREE)
    - Adjusts eigenvector confidence based on evidence
    - Composts stale patterns

    Args:
        soul: KgentSoul instance
        dry_run: If True, don't apply changes
        json_mode: Output as JSON
        ctx: Invocation context
    """
    from agents.k.hypnagogia import get_hypnagogia

    hypnagogia = get_hypnagogia()

    # Check if LLM is available for deeper pattern analysis
    if soul.has_llm and hypnagogia._llm is None:
        # Share the soul's LLM client with hypnagogia
        hypnagogia._llm = soul._llm

    _emit_output(
        f"[SOUL:DREAM] Starting {'(dry run)' if dry_run else ''}...",
        {"status": "starting", "dry_run": dry_run},
        ctx,
    )

    # Execute dream cycle
    report = await hypnagogia.dream(soul, dry_run=dry_run)

    if json_mode:
        import json

        _emit_output(json.dumps(report.to_dict(), indent=2), report.to_dict(), ctx)
    else:
        # Human-friendly output
        _emit_output(report.summary, report.to_dict(), ctx)

        # Show additional details if interesting
        if report.patterns_discovered:
            _emit_output("\nPatterns discovered:", {}, ctx)
            for pattern in report.patterns_discovered[:5]:
                _emit_output(f"  - {pattern.content}", {}, ctx)

    return 0


async def _invoke_with_retry(
    flux: Any,
    event: Any,
    max_retries: int = 2,
    timeout_seconds: float = 60.0,
) -> Any:
    """
    Invoke flux with timeout and retry logic.

    Args:
        flux: KgentFlux instance
        event: SoulEvent to process
        max_retries: Number of retries on failure
        timeout_seconds: Timeout per attempt

    Returns:
        Result event from flux.invoke()

    Raises:
        Exception: If all retries exhausted
    """
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            return await asyncio.wait_for(
                flux.invoke(event),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            last_error = asyncio.TimeoutError(
                f"LLM response timeout after {timeout_seconds}s"
            )
            if attempt == max_retries:
                raise last_error
            await asyncio.sleep(0.5 * (attempt + 1))
        except asyncio.CancelledError:
            raise
        except Exception as e:
            last_error = e
            if attempt == max_retries:
                raise
            await asyncio.sleep(0.5 * (attempt + 1))
    # Should not reach here, but for type checker
    raise last_error or RuntimeError("Unexpected retry loop exit")


async def _handle_stream(
    soul: Any,
    pulse_interval: int,
    show_pulses: bool,
    json_mode: bool,
    ctx: "InvocationContext | None",
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

    This approach avoids the complexity of the FLOWING mode's nested
    timeouts while providing the same user experience.
    """
    import sys
    from datetime import timedelta

    from agents.k.events import (
        SoulEvent,
        SoulEventType,
        dialogue_turn_event,
        pulse_event,
    )
    from agents.k.flux import KgentFlux, KgentFluxConfig

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
    _emit_output(
        "[SOUL:STREAM] Starting (ambient mode)",
        {"status": "starting", "pulse_interval": pulse_interval},
        ctx,
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
                _format_pulse(event, json_mode, ctx)

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
                        _emit_output(
                            f"[SOUL:STREAM] Mode: {new_mode}",
                            {"mode": new_mode},
                            ctx,
                        )
                    else:
                        _emit_output(
                            f"[SOUL:STREAM] Invalid mode: {new_mode}. Valid: {', '.join(valid_modes)}",
                            {"error": f"Invalid mode: {new_mode}"},
                            ctx,
                        )
                    continue

                # Create dialogue event and process with retry/timeout
                event = dialogue_turn_event(
                    message=line,
                    mode=current_mode,
                    is_request=True,
                )
                try:
                    result = await _invoke_with_retry(flux, event)

                    # Display result
                    if result.event_type == SoulEventType.DIALOGUE_TURN:
                        _format_dialogue_turn(result, json_mode, ctx)
                    elif result.event_type == SoulEventType.ERROR:
                        _format_error(result, json_mode, ctx)
                except asyncio.TimeoutError as e:
                    _emit_output(
                        "[SOUL:STREAM] Response timeout",
                        {"error": "timeout", "message": str(e)},
                        ctx,
                    )
                except Exception as e:
                    _emit_output(
                        f"[SOUL:STREAM] Error after retries: {e}",
                        {"error": str(e), "retries_exhausted": True},
                        ctx,
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                _emit_output(
                    f"[SOUL:STREAM] Error: {e}",
                    {"error": str(e)},
                    ctx,
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
        _emit_output(
            f"[SOUL:STREAM] Stopped ({interactions} interactions)",
            {"status": "stopped", "interactions": interactions},
            ctx,
        )

    return 0


async def _handle_watch(
    soul: Any,
    watch_path: str | None,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """
    Handle 'soul watch' command: ambient file watching.

    Uses KgentWatcher to monitor codebase and emit suggestions
    based on heuristics (complexity, naming, patterns, tests, docs).

    Args:
        soul: KgentSoul instance (for personality-infused suggestions)
        watch_path: Directory to watch (default: cwd)
        json_mode: Output as JSON
        ctx: Invocation context
    """
    import signal
    from pathlib import Path

    from agents.k.watcher import KgentWatcher, WatcherConfig

    # Determine path to watch
    root = Path(watch_path) if watch_path else Path.cwd()
    if not root.exists():
        _emit_output(
            f"[SOUL:WATCH] Error: Path does not exist: {root}",
            {"error": f"Path does not exist: {root}"},
            ctx,
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

        if json_mode:
            import json

            data = {
                "timestamp": n.timestamp.isoformat(),
                "heuristic": n.heuristic,
                "message": n.message,
                "severity": n.severity,
                "file_path": n.file_path,
                "details": n.details,
            }
            _emit_output(json.dumps(data), data, ctx)
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

            _emit_output(
                f"  [{ts}] {icon} [{n.heuristic}] {relative_path}",
                {"notification": True},
                ctx,
            )
            _emit_output(f"      {n.message}", {}, ctx)

    watcher.subscribe(on_notification)

    # Print startup banner
    _emit_output(
        f"[SOUL:WATCH] Watching: {root}",
        {"status": "starting", "path": str(root)},
        ctx,
    )
    _emit_output(
        "  Press Ctrl+C to stop",
        {},
        ctx,
    )
    _emit_output(
        "  Heuristics: complexity, naming, patterns, tests, docs",
        {"heuristics": ["complexity", "naming", "patterns", "tests", "docs"]},
        ctx,
    )
    _emit_output("", {}, ctx)

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

        _emit_output(
            f"[SOUL:WATCH] Stopped ({notification_count} notifications)",
            {"status": "stopped", "notifications": notification_count},
            ctx,
        )

    return 0


def _format_pulse(
    event: Any,  # SoulEvent
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> None:
    """Format a pulse event for terminal output."""
    payload = event.payload
    timestamp = event.timestamp.strftime("%H:%M:%S")

    if json_mode:
        import json

        _emit_output(json.dumps(event.to_dict(), indent=2), event.to_dict(), ctx)
    else:
        mode = payload.get("active_mode", "reflect")
        interactions = payload.get("interactions_count", 0)
        _emit_output(
            f"  [{timestamp}] pulse | mode: {mode} | interactions: {interactions}",
            event.to_dict(),
            ctx,
        )


def _format_dialogue_turn(
    event: Any,  # SoulEvent
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> None:
    """Format a dialogue turn event for terminal output."""
    payload = event.payload

    if json_mode:
        import json

        _emit_output(json.dumps(event.to_dict(), indent=2), event.to_dict(), ctx)
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

            _emit_output("\n".join(lines), event.to_dict(), ctx)


def _format_error(
    event: Any,  # SoulEvent
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> None:
    """Format an error event for terminal output."""
    payload = event.payload

    if json_mode:
        import json

        _emit_output(json.dumps(event.to_dict(), indent=2), event.to_dict(), ctx)
    else:
        error = payload.get("error", "Unknown error")
        error_type = payload.get("error_type", "Error")
        _emit_output(f"[SOUL:ERROR] {error_type}: {error}", event.to_dict(), ctx)


def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """
    Emit output via dual-channel if ctx available, else print.

    This is the key integration point with the Reflector Protocol:
    - Human output goes to stdout (for humans)
    - Semantic output goes to FD3 (for agents consuming our output)
    """
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)


# =============================================================================
# Being Commands (Cross-Session Identity)
# =============================================================================


async def _handle_history(
    limit: int,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """
    Handle 'soul history' command - view soul change history.

    Shows the archaeology of self: who was I before each change?
    """
    from agents.k.session import SoulSession

    session = await SoulSession.load()
    changes = session.who_was_i(limit)

    if json_mode:
        import json

        _emit_output(json.dumps(changes, indent=2), {"changes": changes}, ctx)
    else:
        if not changes:
            _emit_output(
                "[SOUL:HISTORY] No changes yet. The soul is fresh.",
                {"changes": []},
                ctx,
            )
        else:
            lines = [
                "[SOUL:HISTORY] Who was I?",
                "",
            ]
            for change in changes:
                status_icon = {"committed": "+", "reverted": "-", "pending": "?"}
                icon = status_icon.get(change.get("status", ""), "*")
                lines.append(f"  [{icon}] {change['id']}: {change['description']}")
                if change.get("felt_sense"):
                    lines.append(f"      Felt: {change['felt_sense']}")
                lines.append(f"      ({change.get('aspect', 'unknown')})")
            _emit_output("\n".join(lines), {"changes": changes}, ctx)

    return 0


async def _handle_propose(
    description: str | None,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """
    Handle 'soul propose' command - K-gent proposes a change.

    Per Heterarchical principle: K-gent proposes, user approves.
    """
    from agents.k.session import SoulSession

    if not description:
        _emit_output(
            "[SOUL:PROPOSE] Error: No description provided\n"
            "Usage: kgents soul propose 'I want to be more concise'",
            {"error": "No description provided"},
            ctx,
        )
        return 1

    session = await SoulSession.load()
    change = await session.propose_change(description)

    if json_mode:
        import json

        _emit_output(json.dumps(change.to_dict(), indent=2), change.to_dict(), ctx)
    else:
        lines = [
            "[SOUL:PROPOSE] Change proposed",
            "",
            f"  ID: {change.id}",
            f"  Description: {change.description}",
            f"  Status: {change.status}",
            "",
            "To approve: kgents soul commit " + change.id,
        ]
        _emit_output("\n".join(lines), change.to_dict(), ctx)

    return 0


async def _handle_commit(
    change_id: str | None,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """
    Handle 'soul commit' command - approve and commit a change.

    This is where self-modification actually happens.
    """
    from agents.k.session import SoulSession

    if not change_id:
        # Show pending changes
        session = await SoulSession.load()
        pending = session.pending_changes

        if not pending:
            _emit_output(
                "[SOUL:COMMIT] No pending changes. Use 'soul propose' first.",
                {"pending": []},
                ctx,
            )
            return 1

        lines = [
            "[SOUL:COMMIT] Pending changes:",
            "",
        ]
        for change in pending:
            lines.append(f"  {change.id}: {change.description}")
        lines.append("")
        lines.append("Usage: kgents soul commit <id>")
        _emit_output("\n".join(lines), {"pending": [c.to_dict() for c in pending]}, ctx)
        return 1

    session = await SoulSession.load()
    success = await session.commit_change(change_id)

    if success:
        _emit_output(
            f"[SOUL:COMMIT] Change {change_id} committed. The soul has changed.",
            {"committed": change_id, "success": True},
            ctx,
        )
        return 0
    else:
        _emit_output(
            f"[SOUL:COMMIT] Change {change_id} not found.",
            {"error": f"Change {change_id} not found"},
            ctx,
        )
        return 1


async def _handle_crystallize(
    name: str | None,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """
    Handle 'soul crystallize' command - save a checkpoint.

    Creates a restore point you can resume from later.
    """
    from agents.k.session import SoulSession

    if not name:
        name = f"crystal-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    session = await SoulSession.load()
    crystal = await session.crystallize(name)

    if json_mode:
        import json

        _emit_output(json.dumps(crystal.to_dict(), indent=2), crystal.to_dict(), ctx)
    else:
        lines = [
            "[SOUL:CRYSTALLIZE] Soul state saved",
            "",
            f"  Crystal ID: {crystal.id}",
            f"  Name: {crystal.name}",
            f"  Created: {crystal.created_at.isoformat()}",
            "",
            f"To resume: kgents soul resume {crystal.id}",
        ]
        _emit_output("\n".join(lines), crystal.to_dict(), ctx)

    return 0


async def _handle_resume(
    crystal_id: str | None,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """
    Handle 'soul resume' command - resume from a crystal.

    Time travel to a previous soul state.
    """
    from agents.k.session import SoulPersistence, SoulSession

    if not crystal_id:
        # List available crystals
        persistence = SoulPersistence()
        crystals = persistence.list_crystals()

        if not crystals:
            _emit_output(
                "[SOUL:RESUME] No crystals found. Use 'soul crystallize' first.",
                {"crystals": []},
                ctx,
            )
            return 1

        lines = [
            "[SOUL:RESUME] Available crystals:",
            "",
        ]
        for cid in crystals:
            crystal = persistence.load_crystal(cid)
            if crystal:
                lines.append(f"  {cid}: {crystal.name} ({crystal.created_at.date()})")
        lines.append("")
        lines.append("Usage: kgents soul resume <id>")
        _emit_output("\n".join(lines), {"crystals": crystals}, ctx)
        return 1

    session = await SoulSession.load()
    success = await session.resume_crystal(crystal_id)

    if success:
        _emit_output(
            f"[SOUL:RESUME] Resumed from crystal {crystal_id}. The past is present.",
            {"resumed": crystal_id, "success": True},
            ctx,
        )
        return 0
    else:
        _emit_output(
            f"[SOUL:RESUME] Crystal {crystal_id} not found.",
            {"error": f"Crystal {crystal_id} not found"},
            ctx,
        )
        return 1


# Import datetime at top level for crystallize
from datetime import datetime

# --- Top-Level Mode Aliases ---
# These allow `kgents reflect "prompt"` instead of `kgents soul reflect "prompt"`


def cmd_reflect(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Alias: kgents reflect -> kgents soul reflect."""
    return cmd_soul(["reflect"] + args, ctx)


def cmd_advise(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Alias: kgents advise -> kgents soul advise."""
    return cmd_soul(["advise"] + args, ctx)


def cmd_challenge(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Alias: kgents challenge -> kgents soul challenge."""
    return cmd_soul(["challenge"] + args, ctx)


def cmd_explore(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Alias: kgents explore -> kgents soul explore."""
    return cmd_soul(["explore"] + args, ctx)
