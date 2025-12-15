"""
Town CLI Handler: Commands for Agent Town.

From Barad: The CLI is not neutral—it performs agential cuts.
`kgents town observe` doesn't read the town—it *constitutes* it.
The observer is part of the phenomenon.

Commands:
    kgents town start       Initialize a new simulation
    kgents town start2      Initialize Phase 2 simulation (7 citizens, 5 regions)
    kgents town step        Advance one phase
    kgents town observe     Show current state (MESA view)
    kgents town lens <name> Zoom into a citizen (LOD 0-5)
    kgents town metrics     Show emergence metrics
    kgents town budget      Show token budget status
    kgents town save <path> Save simulation state to YAML
    kgents town load <path> Load simulation state from YAML
    kgents town demo        Run the Micro-Experience Factory demo

    User Modes (Phase 2):
    kgents town whisper <citizen> "<msg>"  Whisper to a citizen
    kgents town inhabit <citizen>          See through a citizen's eyes
    kgents town intervene "<event>"        Inject a world event

    Notifications (Kent's Motivation Loop):
    kgents town telegram status   Show Telegram notifier status
    kgents town telegram test     Send a test notification
    kgents town telegram payment  Simulate a payment notification

See: spec/town/operad.md
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from agents.town.inhabit_session import InhabitSession
    from protocols.cli.reflector import InvocationContext


# =============================================================================
# TownSession: User Mode State
# =============================================================================


@dataclass
class TownSession:
    """
    Track user's mode in the town simulation.

    Modes:
    - observe: Default mode, watch the simulation unfold
    - whisper: Influence a specific citizen
    - inhabit: See through a citizen's eyes
    - intervene: Inject world events

    From Barad: The mode is an agential cut—it determines
    what phenomena are co-constituted.
    """

    mode: Literal["observe", "whisper", "inhabit", "intervene"] = "observe"
    target_citizen: str | None = None
    whisper_history: list[dict[str, Any]] = field(default_factory=list)
    intervention_history: list[str] = field(default_factory=list)


# Global simulation state (in-memory for MPP)
_simulation_state: dict[str, Any] = {}


def _print_help() -> None:
    """Print help for town command."""
    print(__doc__)


def cmd_town(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Agent Town CLI: Civilizational engine commands.

    To observe the town is to participate in its constitution.
    The town you see is the town you help create.
    """
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    if not args:
        return _show_status(ctx)

    subcommand = args[0].lower()

    if subcommand == "start":
        return _start_simulation(args[1:], ctx, phase2=False)
    elif subcommand == "start2":
        return _start_simulation(args[1:], ctx, phase2=True)
    elif subcommand == "step":
        return _step_simulation(ctx)
    elif subcommand == "observe":
        return _observe(ctx)
    elif subcommand == "lens":
        if len(args) < 2:
            _emit("[TOWN] Usage: kgents town lens <citizen_name> [lod]", {}, ctx)
            return 1
        lod = int(args[2]) if len(args) > 2 else 1
        return _lens_citizen(args[1], lod, ctx)
    elif subcommand == "metrics":
        return _show_metrics(ctx)
    elif subcommand == "budget":
        return _show_budget(ctx)
    elif subcommand == "status":
        return _show_status(ctx)
    elif subcommand == "save":
        if len(args) < 2:
            _emit("[TOWN] Usage: kgents town save <path>", {}, ctx)
            return 1
        return _save_simulation(args[1], ctx)
    elif subcommand == "load":
        if len(args) < 2:
            _emit("[TOWN] Usage: kgents town load <path>", {}, ctx)
            return 1
        return _load_simulation(args[1], ctx)
    elif subcommand == "whisper":
        if len(args) < 3:
            _emit('[TOWN] Usage: kgents town whisper <citizen> "<message>"', {}, ctx)
            return 1
        citizen_name = args[1]
        message = " ".join(args[2:]).strip('"')
        return _whisper_citizen(citizen_name, message, ctx)
    elif subcommand == "inhabit":
        if len(args) < 2:
            _emit("[TOWN] Usage: kgents town inhabit <citizen>", {}, ctx)
            return 1
        return _inhabit_citizen(args[1], ctx)
    elif subcommand == "intervene":
        if len(args) < 2:
            _emit('[TOWN] Usage: kgents town intervene "<event>"', {}, ctx)
            return 1
        event_desc = " ".join(args[1:]).strip('"')
        return _intervene_event(event_desc, ctx)
    elif subcommand == "demo":
        return _demo(args[1:], ctx)
    elif subcommand == "telegram":
        return _telegram_command(args[1:], ctx)
    elif subcommand == "help":
        _print_help()
        return 0
    else:
        _emit(f"[TOWN] Unknown command: {subcommand}", {"error": subcommand}, ctx)
        return 1


def _start_simulation(
    args: list[str], ctx: "InvocationContext | None", phase2: bool = False
) -> int:
    """Initialize a new Agent Town simulation."""
    from agents.town.environment import (
        create_mpp_environment,
        create_phase2_environment,
    )
    from agents.town.flux import TownFlux

    # Check if simulation already running
    if "flux" in _simulation_state:
        _emit(
            "[TOWN] Simulation already running. Use 'kgents town step' to advance.",
            {"status": "already_running"},
            ctx,
        )
        return 0

    # Create environment
    if phase2:
        env = create_phase2_environment()
    else:
        env = create_mpp_environment()

    # Create flux
    seed = None
    if args and args[0].isdigit():
        seed = int(args[0])
    flux = TownFlux(env, seed=seed)

    # Store state
    _simulation_state["environment"] = env
    _simulation_state["flux"] = flux
    _simulation_state["session"] = TownSession()

    _emit(
        f"[TOWN] Agent Town '{env.name}' initialized.",
        {"name": env.name, "citizens": len(env.citizens), "regions": len(env.regions)},
        ctx,
    )
    _emit(f"  Citizens: {', '.join(c.name for c in env.citizens.values())}", {}, ctx)
    _emit(f"  Regions: {', '.join(env.regions.keys())}", {}, ctx)
    _emit("\nUse 'kgents town step' to advance the simulation.", {}, ctx)

    return 0


def _step_simulation(ctx: "InvocationContext | None") -> int:
    """Advance the simulation by one phase."""
    if "flux" not in _simulation_state:
        _emit(
            "[TOWN] No simulation running. Use 'kgents town start' first.",
            {"error": "not_running"},
            ctx,
        )
        return 1

    flux = _simulation_state["flux"]

    # Run the step
    async def _run_step() -> list[Any]:
        events = []
        async for event in flux.step():
            events.append(event)
        return events

    events = asyncio.run(_run_step())

    # Display events
    status = flux.get_status()
    _emit(
        f"\n[TOWN] Day {status['day']} - {status['phase']}",
        {"day": status["day"], "phase": status["phase"]},
        ctx,
    )
    _emit("=" * 50, {}, ctx)

    for event in events:
        icon = "✓" if event.success else "✗"
        participants_str = ", ".join(event.participants)
        _emit(
            f"  {icon} [{event.operation.upper()}] {event.message}",
            event.to_dict(),
            ctx,
        )
        _emit(
            f"    Participants: {participants_str}",
            {},
            ctx,
        )
        _emit(
            f"    Tokens: {event.tokens_used}, Drama: {event.drama_contribution:.2f}",
            {},
            ctx,
        )

    _emit("\n[METRICS]", {}, ctx)
    _emit(f"  Tension Index: {status['tension_index']:.4f}", {}, ctx)
    _emit(f"  Cooperation Level: {status['cooperation_level']:.2f}", {}, ctx)
    _emit(f"  Total Tokens: {status['total_tokens']}", {}, ctx)

    return 0


def _observe(ctx: "InvocationContext | None") -> int:
    """Show the MESA view (town overview)."""
    if "environment" not in _simulation_state:
        _emit(
            "[TOWN] No simulation running. Use 'kgents town start' first.",
            {"error": "not_running"},
            ctx,
        )
        return 1

    env = _simulation_state["environment"]
    flux = _simulation_state.get("flux")

    # Render ASCII MESA view
    _emit("\n" + "=" * 60, {}, ctx)
    _emit(f"  AGENT TOWN: {env.name}", {"name": env.name}, ctx)
    if flux:
        status = flux.get_status()
        _emit(f"  Day {status['day']} / {status['phase']}", status, ctx)
    _emit("=" * 60, {}, ctx)

    # Render regions
    for region_name, region in env.regions.items():
        citizens_here = env.get_citizens_in_region(region_name)
        density = env.density_at(region_name)

        _emit(f"\n  [{region_name.upper()}] ({density:.0%} density)", {}, ctx)
        _emit(f"    {region.description}", {}, ctx)

        if citizens_here:
            for c in citizens_here:
                phase_icon = _phase_icon(c.phase.name)
                _emit(f"    {phase_icon} {c.name} ({c.archetype})", {}, ctx)
        else:
            _emit("    (empty)", {}, ctx)

    # Metrics bar
    _emit("\n" + "-" * 60, {}, ctx)
    tension = env.tension_index()
    coop = env.cooperation_level()
    tokens = env.total_token_spend

    tension_bar = _render_bar(tension, max_val=1.0, width=10)
    coop_bar = _render_bar(coop, max_val=5.0, width=10)

    _emit(
        f"  TENSION: {tension_bar} {tension:.2f}  "
        f"COOPERATION: {coop_bar} {coop:.2f}  "
        f"TOKENS: {tokens}",
        {"tension": tension, "cooperation": coop, "tokens": tokens},
        ctx,
    )
    _emit("=" * 60, {}, ctx)

    return 0


def _lens_citizen(name: str, lod: int, ctx: "InvocationContext | None") -> int:
    """Zoom into a citizen at a specific LOD."""
    if "environment" not in _simulation_state:
        _emit(
            "[TOWN] No simulation running. Use 'kgents town start' first.",
            {"error": "not_running"},
            ctx,
        )
        return 1

    env = _simulation_state["environment"]
    citizen = env.get_citizen_by_name(name)

    if not citizen:
        _emit(
            f"[TOWN] Unknown citizen: {name}",
            {"error": "unknown_citizen", "name": name},
            ctx,
        )
        _emit(
            f"  Available: {', '.join(c.name for c in env.citizens.values())}",
            {},
            ctx,
        )
        return 1

    # Clamp LOD
    lod = max(0, min(5, lod))

    # Get manifestation
    manifest = citizen.manifest(lod)

    _emit(f"\n[LENS] {citizen.name} (LOD {lod})", {"lod": lod}, ctx)
    _emit("=" * 50, {}, ctx)

    # LOD 0: Silhouette
    phase_icon = _phase_icon(manifest.get("phase", "IDLE"))
    _emit(f"  {phase_icon} {manifest['name']} @ {manifest['region']}", manifest, ctx)

    if lod >= 1:
        _emit(f"  Archetype: {manifest.get('archetype', 'unknown')}", {}, ctx)
        _emit(f"  Mood: {manifest.get('mood', 'unknown')}", {}, ctx)

    if lod >= 2:
        _emit(f"  Cosmotechnics: {manifest.get('cosmotechnics', 'unknown')}", {}, ctx)
        _emit(f'  Metaphor: "{manifest.get("metaphor", "")}"', {}, ctx)

    if lod >= 3:
        _emit("\n  Eigenvectors:", {}, ctx)
        for k, v in manifest.get("eigenvectors", {}).items():
            bar = _render_bar(v, max_val=1.0, width=10)
            _emit(f"    {k}: {bar} {v:.2f}", {}, ctx)

        _emit("\n  Relationships:", {}, ctx)
        rels = manifest.get("relationships", {})
        if rels:
            for cid, weight in rels.items():
                sign = "+" if weight > 0 else ""
                _emit(f"    {cid}: {sign}{weight:.2f}", {}, ctx)
        else:
            _emit("    (none yet)", {}, ctx)

    if lod >= 4:
        _emit(f"\n  ID: {manifest.get('id', 'unknown')}", {}, ctx)
        _emit(f"  Accursed Surplus: {manifest.get('accursed_surplus', 0):.2f}", {}, ctx)

    if lod >= 5:
        _emit("\n" + "-" * 50, {}, ctx)
        opacity = manifest.get("opacity", {})
        _emit("  [THE ABYSS]", {}, ctx)
        _emit(f'  "{opacity.get("statement", "")}"', {}, ctx)
        _emit(f"\n  {opacity.get('message', '')}", {}, ctx)

    _emit("=" * 50, {}, ctx)
    return 0


def _show_metrics(ctx: "InvocationContext | None") -> int:
    """Show emergence metrics."""
    if "environment" not in _simulation_state:
        _emit(
            "[TOWN] No simulation running. Use 'kgents town start' first.",
            {"error": "not_running"},
            ctx,
        )
        return 1

    env = _simulation_state["environment"]
    flux = _simulation_state.get("flux")

    _emit("\n[METRICS] Agent Town Emergence Metrics", {}, ctx)
    _emit("=" * 50, {}, ctx)

    tension = env.tension_index()
    coop = env.cooperation_level()
    surplus = env.total_accursed_surplus()

    _emit(
        f"  Tension Index:     {tension:.4f}  {'(HIGH DRAMA!)' if tension > 0.7 else ''}",
        {"tension_index": tension},
        ctx,
    )
    _emit(
        f"  Cooperation Level: {coop:.2f}",
        {"cooperation_level": coop},
        ctx,
    )
    _emit(
        f"  Accursed Surplus:  {surplus:.2f}  {'(NEEDS EXPENDITURE!)' if surplus > 10 else ''}",
        {"accursed_surplus": surplus},
        ctx,
    )

    if flux:
        status = flux.get_status()
        _emit(f"\n  Total Events:      {status['total_events']}", {}, ctx)
        _emit(f"  Total Tokens:      {status['total_tokens']}", {}, ctx)

    _emit("=" * 50, {}, ctx)
    return 0


def _show_budget(ctx: "InvocationContext | None") -> int:
    """Show token budget status."""
    if "environment" not in _simulation_state:
        _emit(
            "[TOWN] No simulation running. Use 'kgents town start' first.",
            {"error": "not_running"},
            ctx,
        )
        return 1

    env = _simulation_state["environment"]
    flux = _simulation_state.get("flux")

    _emit("\n[BUDGET] Agent Town Token Budget", {}, ctx)
    _emit("=" * 50, {}, ctx)

    monthly_cap = 1_000_000  # MPP budget
    spent = env.total_token_spend

    pct = (spent / monthly_cap) * 100 if monthly_cap > 0 else 0

    _emit(f"  Monthly Cap:       {monthly_cap:,} tokens", {}, ctx)
    _emit(f"  Spent This Session: {spent:,} tokens ({pct:.1f}%)", {}, ctx)

    if flux:
        status = flux.get_status()
        daily_avg = spent / max(1, status["day"])
        projected = daily_avg * 30
        _emit(f"  Daily Average:     {daily_avg:,.0f} tokens", {}, ctx)
        _emit(f"  Projected Monthly: {projected:,.0f} tokens", {}, ctx)

        budget_status = "ON BUDGET" if projected < monthly_cap else "OVER BUDGET"
        _emit(f"\n  Status: {budget_status}", {"budget_status": budget_status}, ctx)

    _emit("=" * 50, {}, ctx)
    return 0


def _show_status(ctx: "InvocationContext | None") -> int:
    """Show simulation status."""
    if "flux" not in _simulation_state:
        _emit("[TOWN] No simulation running.", {}, ctx)
        _emit("  Use 'kgents town start' to begin.", {}, ctx)
        _emit("\nAvailable commands:", {}, ctx)
        _emit("  kgents town start       Initialize simulation", {}, ctx)
        _emit("  kgents town step        Advance one phase", {}, ctx)
        _emit("  kgents town observe     Show MESA view", {}, ctx)
        _emit("  kgents town lens <name> Zoom into citizen", {}, ctx)
        _emit("  kgents town metrics     Show metrics", {}, ctx)
        _emit("  kgents town budget      Show budget", {}, ctx)
        return 0

    flux = _simulation_state["flux"]
    status = flux.get_status()

    _emit(
        f"\n[TOWN] Simulation Status: Day {status['day']} - {status['phase']}",
        status,
        ctx,
    )
    _emit(
        f"  Events: {status['total_events']}  Tokens: {status['total_tokens']}", {}, ctx
    )

    return 0


def _demo(args: list[str], ctx: "InvocationContext | None") -> int:
    """
    Run the Micro-Experience Factory demo.

    Boots an isometric lattice with citizens, runs through phases,
    and shows beautiful ASCII visualization with live updates.

    Crown Jewel: plans/micro-experience-factory.md

    Demo Beat Sequence:
    1. world.town init - Plaza manifests with glyph rain
    2. Run 4 phases automatically (MORNING -> AFTERNOON -> EVENING -> NIGHT)
    3. Show each event as it happens with ASCII update
    4. End with perturbation pad prompt
    5. Accept input for HITL interaction
    """
    from agents.town.environment import create_phase2_environment
    from agents.town.factory_bridge import FactoryBridge, FactoryBridgeConfig
    from agents.town.flux import TownFlux

    # Parse args
    num_phases = 4  # Default: one full day
    interactive = True
    seed = 42

    for arg in args:
        if arg.isdigit():
            num_phases = int(arg)
        elif arg == "--no-interactive":
            interactive = False
        elif arg.startswith("--seed="):
            seed = int(arg.split("=")[1])

    # Create Phase 2 environment (7 citizens, 5 regions)
    env = create_phase2_environment()
    flux = TownFlux(env, seed=seed)

    # Create factory bridge
    config = FactoryBridgeConfig(
        grid_width=12,
        grid_height=12,
        enable_pads=True,
        perturbation_cooldown_ms=1000,  # Faster for demo
    )
    bridge = FactoryBridge(flux, config)

    _emit("\n[DEMO] Micro-Experience Factory", {}, ctx)
    _emit("=" * 58, {}, ctx)
    _emit(f"  Environment: {env.name}", {"env_name": env.name}, ctx)
    _emit(f"  Citizens: {len(env.citizens)}", {"citizen_count": len(env.citizens)}, ctx)
    _emit(f"  Phases: {num_phases} (one phase = ~1/4 day)", {"phases": num_phases}, ctx)
    _emit("=" * 58, {}, ctx)
    _emit("", {}, ctx)

    # Run the demo
    async def _run_demo() -> list[str]:
        frames: list[str] = []
        async for frame in bridge.run(num_phases=num_phases):
            frames.append(frame)
        return frames

    frames = asyncio.run(_run_demo())

    # Show final frame
    if frames:
        _emit(frames[-1], {"frame_type": "final"}, ctx)

    # Show event summary
    status = flux.get_status()
    _emit("", {}, ctx)
    _emit("[SUMMARY]", {}, ctx)
    _emit(f"  Day: {status['day']}, Phase: {status['phase']}", status, ctx)
    _emit(f"  Events: {status['total_events']}", {}, ctx)
    _emit(f"  Tokens: {status['total_tokens']}", {}, ctx)
    _emit(f"  Tension: {status['tension_index']:.4f}", {}, ctx)
    _emit(f"  Cooperation: {status['cooperation_level']:.2f}", {}, ctx)

    # Show trace info
    trace_events = len(flux.trace.events)
    _emit(f"  Trace Events: {trace_events}", {"trace_events": trace_events}, ctx)

    # Interactive mode
    if interactive:
        _emit("", {}, ctx)
        _emit("[INTERACTIVE MODE]", {}, ctx)
        _emit("  Commands:", {}, ctx)
        _emit("    Enter/n = Advance one phase", {}, ctx)
        _emit("    g = Greet (50 tokens)", {}, ctx)
        _emit("    s = Gossip (150 tokens)", {}, ctx)
        _emit("    t = Trade (200 tokens)", {}, ctx)
        _emit("    o = Solo (75 tokens)", {}, ctx)
        _emit("    b = Toggle Bloom", {}, ctx)
        _emit("    ? = Help", {}, ctx)
        _emit("    q = Quit", {}, ctx)
        _emit("", {}, ctx)

        # Store simulation state for future interactions
        _simulation_state["environment"] = env
        _simulation_state["flux"] = flux
        _simulation_state["bridge"] = bridge
        _simulation_state["session"] = TownSession()

        # Interactive loop - keep going until 'q' or interrupt
        try:
            while True:
                user_input = input("  > ").strip().lower()

                if user_input == "q":
                    _emit("[DEMO] Exiting.", {}, ctx)
                    break
                elif user_input == "b":
                    bridge.toggle_bloom()
                    _emit(bridge.get_frame(), {"frame_type": "bloom_toggle"}, ctx)
                elif user_input == "n" or user_input == "":
                    # Advance one phase (empty enter = next)
                    async def _step() -> list[str]:
                        step_frames: list[str] = []
                        async for frame in bridge.run(num_phases=1):
                            step_frames.append(frame)
                        return step_frames

                    step_frames = asyncio.run(_step())
                    if step_frames:
                        _emit(step_frames[-1], {"frame_type": "step"}, ctx)
                    status = flux.get_status()
                    _emit(f"  Day {status['day']} - {status['phase']}", status, ctx)
                elif user_input in ("g", "s", "t", "o"):
                    pad_map = {"g": "greet", "s": "gossip", "t": "trade", "o": "solo"}
                    pad_id = pad_map[user_input]

                    async def _perturb() -> Any:
                        return await bridge.perturb(pad_id)

                    event = asyncio.run(_perturb())

                    if event:
                        _emit(
                            f"[PERTURB] {event.operation}: {event.message}",
                            event.to_dict(),
                            ctx,
                        )
                        _emit(bridge.get_frame(), {"frame_type": "perturbation"}, ctx)
                    else:
                        _emit("[PERTURB] Failed (cooldown or no participants)", {}, ctx)
                elif user_input == "?":
                    _emit(
                        "  Commands: g=greet, s=gossip, t=trade, o=solo, b=bloom, n/Enter=next phase, q=quit",
                        {},
                        ctx,
                    )
                else:
                    _emit(f"  Unknown: '{user_input}' (try '?' for help)", {}, ctx)

        except (EOFError, KeyboardInterrupt):
            _emit("\n[DEMO] Interrupted.", {}, ctx)

    _emit("", {}, ctx)
    _emit(
        "[DEMO] Complete. Use 'kgents town step' to continue the simulation.", {}, ctx
    )

    return 0


def _save_simulation(path: str, ctx: "InvocationContext | None") -> int:
    """Save simulation state to YAML."""
    if "environment" not in _simulation_state:
        _emit(
            "[TOWN] No simulation running. Use 'kgents town start' first.",
            {"error": "not_running"},
            ctx,
        )
        return 1

    env = _simulation_state["environment"]
    flux = _simulation_state.get("flux")

    try:
        # Save environment state
        env.to_yaml(path)

        _emit(f"[TOWN] Saved simulation to {path}", {"path": path}, ctx)
        _emit(f"  Citizens: {len(env.citizens)}", {}, ctx)
        _emit(f"  Regions: {len(env.regions)}", {}, ctx)
        if flux:
            status = flux.get_status()
            _emit(f"  Day: {status['day']}, Phase: {status['phase']}", {}, ctx)
            _emit(f"  Total Events: {status['total_events']}", {}, ctx)

        return 0
    except Exception as e:
        _emit(f"[TOWN] Error saving: {e}", {"error": str(e)}, ctx)
        return 1


def _load_simulation(path: str, ctx: "InvocationContext | None") -> int:
    """Load simulation state from YAML."""
    from agents.town.environment import TownEnvironment
    from agents.town.flux import TownFlux

    try:
        # Load environment
        env = TownEnvironment.from_yaml(path)

        # Create flux with loaded environment
        flux = TownFlux(env)

        # Store in simulation state
        _simulation_state["environment"] = env
        _simulation_state["flux"] = flux
        _simulation_state["session"] = TownSession()

        _emit(f"[TOWN] Loaded simulation from {path}", {"path": path}, ctx)
        _emit(f"  Name: {env.name}", {}, ctx)
        _emit(f"  Citizens: {len(env.citizens)}", {}, ctx)
        _emit(f"  Regions: {len(env.regions)}", {}, ctx)
        _emit("\nUse 'kgents town step' to advance the simulation.", {}, ctx)

        return 0
    except FileNotFoundError:
        _emit(f"[TOWN] File not found: {path}", {"error": "not_found"}, ctx)
        return 1
    except Exception as e:
        _emit(f"[TOWN] Error loading: {e}", {"error": str(e)}, ctx)
        return 1


# =============================================================================
# User Modes (Phase 2)
# =============================================================================


def _whisper_citizen(
    citizen_name: str, message: str, ctx: "InvocationContext | None"
) -> int:
    """
    Whisper to a citizen, influencing their thoughts.

    From Barad: The whisper is an intra-action—it co-constitutes
    both the whisperer and the citizen.
    """
    if "environment" not in _simulation_state:
        _emit(
            "[TOWN] No simulation running. Use 'kgents town start' first.",
            {"error": "not_running"},
            ctx,
        )
        return 1

    env = _simulation_state["environment"]
    session: TownSession = _simulation_state.get("session", TownSession())
    citizen = env.get_citizen_by_name(citizen_name)

    if not citizen:
        _emit(
            f"[TOWN] Unknown citizen: {citizen_name}",
            {"error": "unknown_citizen", "name": citizen_name},
            ctx,
        )
        _emit(
            f"  Available: {', '.join(c.name for c in env.citizens.values())}",
            {},
            ctx,
        )
        return 1

    # Check if citizen is resting (respect Right to Rest)
    if citizen.is_resting:
        _emit(
            f"[TOWN] {citizen_name} is resting. Respect the Right to Rest.",
            {"error": "citizen_resting", "name": citizen_name},
            ctx,
        )
        return 1

    # Update session
    session.mode = "whisper"
    session.target_citizen = citizen_name
    session.whisper_history.append(
        {"citizen": citizen_name, "message": message, "day": _get_current_day()}
    )
    _simulation_state["session"] = session

    # Store the whisper in citizen's memory
    async def _store_whisper() -> None:
        await citizen.remember(
            {
                "type": "whisper",
                "message": message,
                "from": "observer",
                "day": _get_current_day(),
            },
            key=f"whisper_{_get_current_day()}_{citizen.id}",
        )

    asyncio.run(_store_whisper())

    # Subtle influence on eigenvectors based on message sentiment
    # (simplified: positive words increase warmth, questions increase curiosity)
    if any(w in message.lower() for w in ["love", "kind", "friend", "thank", "good"]):
        citizen.eigenvectors.warmth = min(1.0, citizen.eigenvectors.warmth + 0.05)
        _emit("  (warmth +0.05)", {}, ctx)
    if "?" in message:
        citizen.eigenvectors.curiosity = min(1.0, citizen.eigenvectors.curiosity + 0.05)
        _emit("  (curiosity +0.05)", {}, ctx)

    _emit(f"\n[WHISPER] You whisper to {citizen_name}:", {"target": citizen_name}, ctx)
    _emit(f'  "{message}"', {"message": message}, ctx)
    _emit(f"\n{citizen_name} seems to have heard... something.", {}, ctx)
    _emit("The whisper enters their memory like a half-remembered dream.", {}, ctx)

    return 0


def _inhabit_citizen(citizen_name: str, ctx: "InvocationContext | None") -> int:
    """
    Inhabit a citizen—see the world through their eyes.

    Track A: INHABIT mode with consent tracking, force mechanic,
    and session caps. Respects citizen autonomy.

    From Glissant: To inhabit is not to possess. The opacity remains.
    You see what they see, but not how they see it.
    """
    from agents.town.inhabit_session import InhabitSession, SubscriptionTier

    if "environment" not in _simulation_state:
        _emit(
            "[TOWN] No simulation running. Use 'kgents town start' first.",
            {"error": "not_running"},
            ctx,
        )
        return 1

    env = _simulation_state["environment"]
    citizen = env.get_citizen_by_name(citizen_name)

    if not citizen:
        _emit(
            f"[TOWN] Unknown citizen: {citizen_name}",
            {"error": "unknown_citizen", "name": citizen_name},
            ctx,
        )
        _emit(
            f"  Available: {', '.join(c.name for c in env.citizens.values())}",
            {},
            ctx,
        )
        return 1

    # Create INHABIT session (for MPP demo, use CITIZEN tier)
    user_tier = SubscriptionTier.CITIZEN  # Full INHABIT with force
    inhabit = InhabitSession(citizen=citizen, user_tier=user_tier)
    inhabit.force_enabled = True  # Enable Advanced INHABIT (opt-in)

    # Store in simulation state
    _simulation_state["inhabit_session"] = inhabit
    session: TownSession = _simulation_state.get("session", TownSession())
    session.mode = "inhabit"
    session.target_citizen = citizen_name
    _simulation_state["session"] = session

    # Show initial view
    _show_inhabit_view(inhabit, ctx)

    # Interactive INHABIT loop
    _emit("\n[INHABIT MODE]", {}, ctx)
    _emit("  Commands:", {}, ctx)
    _emit("    s <action>  = Suggest action to citizen", {}, ctx)
    _emit("    f <action>  = Force action (expensive, limited)", {}, ctx)
    _emit("    a           = Apologize (reduce consent debt)", {}, ctx)
    _emit("    v           = View current state", {}, ctx)
    _emit("    c           = Check consent status", {}, ctx)
    _emit("    ?           = Help", {}, ctx)
    _emit("    q           = Exit INHABIT mode", {}, ctx)
    _emit("", {}, ctx)

    # Interactive loop
    try:
        while True:
            # Update session (track time, decay debt)
            inhabit.update()

            # Check if session expired
            if inhabit.is_expired():
                _emit(
                    "\n[INHABIT] Session time limit reached. Exiting.",
                    {"reason": "time_limit"},
                    ctx,
                )
                break

            # Get user input
            user_input = input("  inhabit> ").strip()

            if not user_input:
                continue

            if user_input == "q":
                _emit("[INHABIT] Exiting.", {}, ctx)
                break

            elif user_input == "v":
                _show_inhabit_view(inhabit, ctx)

            elif user_input == "c":
                _show_consent_status(inhabit, ctx)

            elif user_input == "a":
                result = inhabit.apologize()
                _emit(f"[APOLOGIZE] {result['message']}", result, ctx)

            elif user_input.startswith("s "):
                action = user_input[2:].strip()
                result = inhabit.suggest_action(action)
                if result["success"]:
                    _emit(f"[SUGGEST] {result['message']}", result, ctx)
                else:
                    _emit(f"[SUGGEST] {result['message']}", result, ctx)

            elif user_input.startswith("f "):
                action = user_input[2:].strip()
                try:
                    result = inhabit.force_action(action)
                    _emit(f"[FORCE] {result['message']}", result, ctx)
                    _emit(
                        f"  Forces remaining: {result['forces_remaining']}/{inhabit.max_forces}",
                        {},
                        ctx,
                    )
                    _emit(
                        f"  Consent debt: {result['debt']:.2f}/1.0",
                        {},
                        ctx,
                    )
                except ValueError as e:
                    _emit(f"[FORCE] Cannot force: {e}", {"error": str(e)}, ctx)

            elif user_input == "?":
                _emit(
                    "  Commands: s=suggest, f=force, a=apologize, v=view, c=consent, q=quit",
                    {},
                    ctx,
                )

            else:
                _emit(f"  Unknown command: '{user_input}' (try '?' for help)", {}, ctx)

    except (EOFError, KeyboardInterrupt):
        _emit("\n[INHABIT] Interrupted.", {}, ctx)

    # Show session summary
    status = inhabit.get_status()
    _emit("\n[SESSION SUMMARY]", {}, ctx)
    _emit(f"  Duration: {status['duration']:.0f}s", {}, ctx)
    _emit(f"  Actions: {status['actions_count']}", {}, ctx)
    _emit(
        f"  Forces used: {status['force']['used']}/{status['force']['limit']}", {}, ctx
    )
    _emit(f"  Final consent debt: {status['consent']['debt']:.2f}", {}, ctx)
    _emit(f"  Status: {status['consent']['status']}", {}, ctx)

    return 0


def _show_inhabit_view(
    inhabit: "InhabitSession", ctx: "InvocationContext | None"
) -> None:
    """Show the citizen's current view of the world."""
    from agents.town.inhabit_session import InhabitSession

    citizen = inhabit.citizen
    manifest = citizen.manifest(lod=4)

    _emit(f"\n[VIEW] You are {citizen.name}", {"citizen": citizen.name}, ctx)
    _emit("=" * 50, {}, ctx)

    # Current state
    phase_icon = _phase_icon(manifest.get("phase", "IDLE"))
    _emit(f"\n  {phase_icon} You are {manifest.get('phase', 'IDLE').lower()}.", {}, ctx)
    _emit(f"  You are at the {citizen.region}.", {}, ctx)

    # Inner world (cosmotechnics)
    _emit(f'\n  Your truth: "{manifest.get("metaphor", "")}"', {}, ctx)

    # Relationships from their perspective
    _emit("\n  You think about others:", {}, ctx)
    rels = manifest.get("relationships", {})
    if rels:
        # Get environment for name lookup
        env = _simulation_state.get("environment")
        for other_id, weight in list(rels.items())[:5]:  # Limit to 5
            if env:
                other_citizen = env.get_citizen_by_id(other_id)
                other_name = other_citizen.name if other_citizen else other_id[:6]
            else:
                other_name = other_id[:6]

            if weight > 0.5:
                _emit(f"    {other_name}: You feel warmly toward them.", {}, ctx)
            elif weight > 0:
                _emit(f"    {other_name}: An acquaintance.", {}, ctx)
            elif weight < -0.3:
                _emit(f"    {other_name}: Something bothers you about them.", {}, ctx)
            else:
                _emit(f"    {other_name}: Neutral.", {}, ctx)
    else:
        _emit("    (You haven't formed strong opinions yet.)", {}, ctx)

    # Consent status
    status = inhabit.consent.status_message()
    _emit(f"\n  Consent: {status} (debt: {inhabit.consent.debt:.2f})", {}, ctx)

    # Hint at opacity
    _emit(f"\n  {citizen.cosmotechnics.opacity_statement}", {}, ctx)
    _emit("=" * 50, {}, ctx)


def _show_consent_status(
    inhabit: "InhabitSession", ctx: "InvocationContext | None"
) -> None:
    """Show detailed consent and session status."""
    from agents.town.inhabit_session import InhabitSession

    status = inhabit.get_status()

    _emit("\n[CONSENT STATUS]", {}, ctx)
    _emit("=" * 50, {}, ctx)

    # Consent meter
    debt = status["consent"]["debt"]
    debt_bar = _render_bar(debt, max_val=1.0, width=20)
    _emit(f"  Debt: {debt_bar} {debt:.2f}/1.0", {}, ctx)
    _emit(f"  Status: {status['consent']['status']}", {}, ctx)

    if status["consent"]["cooldown"] > 0:
        _emit(
            f"  Cooldown: {status['consent']['cooldown']:.0f}s until next force",
            {},
            ctx,
        )

    # Force usage
    _emit(f"\n  Forces: {status['force']['used']}/{status['force']['limit']}", {}, ctx)
    if status["force"]["enabled"]:
        if status["consent"]["can_force"]:
            _emit("  Force available: YES", {}, ctx)
        else:
            _emit("  Force available: NO", {}, ctx)
    else:
        _emit("  Force: DISABLED (opt-in required)", {}, ctx)

    # Time
    time_remaining = status["time_remaining"]
    mins = int(time_remaining / 60)
    secs = int(time_remaining % 60)
    _emit(f"\n  Time remaining: {mins}m {secs}s", {}, ctx)

    _emit("=" * 50, {}, ctx)


def _intervene_event(event_desc: str, ctx: "InvocationContext | None") -> int:
    """
    Inject a world event into the simulation.

    From Morton: You become part of the hyperobject.
    Your intervention is entangled with the town's becoming.
    """
    if "environment" not in _simulation_state:
        _emit(
            "[TOWN] No simulation running. Use 'kgents town start' first.",
            {"error": "not_running"},
            ctx,
        )
        return 1

    env = _simulation_state["environment"]
    session: TownSession = _simulation_state.get("session", TownSession())

    # Update session
    session.mode = "intervene"
    session.intervention_history.append(event_desc)
    _simulation_state["session"] = session

    _emit(f'\n[INTERVENE] You declare: "{event_desc}"', {"event": event_desc}, ctx)
    _emit("=" * 50, {}, ctx)

    # Parse event type and apply effects
    event_lower = event_desc.lower()

    effects: list[str] = []

    if any(w in event_lower for w in ["storm", "rain", "weather", "flood"]):
        # Weather event: citizens move to shelter
        _emit("  A storm sweeps through the town...", {}, ctx)
        for citizen in env.citizens.values():
            if citizen.region not in ["inn", "library"]:
                citizen.move_to("inn")
                effects.append(f"{citizen.name} seeks shelter at the inn")

    elif any(w in event_lower for w in ["festival", "celebration", "party"]):
        # Social event: increase warmth, gather citizens
        _emit("  A festival atmosphere spreads...", {}, ctx)
        for citizen in env.citizens.values():
            citizen.eigenvectors.warmth = min(1.0, citizen.eigenvectors.warmth + 0.1)
            citizen.move_to("square")
            effects.append(f"{citizen.name}'s warmth increases")

    elif any(w in event_lower for w in ["rumor", "news", "gossip"]):
        # Information event: affect trust
        _emit("  A rumor spreads through the town...", {}, ctx)
        for citizen in env.citizens.values():
            # Random trust impact
            delta = -0.1 if "bad" in event_lower else 0.05
            citizen.eigenvectors.trust = max(
                0.0, min(1.0, citizen.eigenvectors.trust + delta)
            )
            effects.append(f"{citizen.name}'s trust shifts")

    elif any(w in event_lower for w in ["gift", "windfall", "treasure"]):
        # Resource event: increase surplus
        _emit("  Unexpected fortune arrives...", {}, ctx)
        for citizen in env.citizens.values():
            citizen.accumulate_surplus(5.0)
            effects.append(f"{citizen.name} gains surplus")

    elif any(w in event_lower for w in ["quiet", "peace", "rest"]):
        # Rest event: citizens rest
        _emit("  A peaceful quiet descends...", {}, ctx)
        for citizen in env.citizens.values():
            if citizen.is_available:
                citizen.rest()
                effects.append(f"{citizen.name} rests")

    else:
        # Generic event: store in all citizen memories
        _emit("  The town takes note...", {}, ctx)

        async def _store_intervention() -> None:
            for citizen in env.citizens.values():
                await citizen.remember(
                    {
                        "type": "intervention",
                        "event": event_desc,
                        "day": _get_current_day(),
                    },
                    key=f"intervention_{_get_current_day()}_{citizen.id}",
                )

        asyncio.run(_store_intervention())
        effects.append("Event stored in all citizen memories")

    # Report effects
    if effects:
        _emit("\n  Effects:", {}, ctx)
        for effect in effects[:5]:  # Limit display
            _emit(f"    - {effect}", {}, ctx)
        if len(effects) > 5:
            _emit(f"    ... and {len(effects) - 5} more", {}, ctx)

    _emit("\n  Your intervention ripples through the simulation.", {}, ctx)
    _emit("=" * 50, {}, ctx)

    return 0


# =============================================================================
# Telegram Notifier Commands
# =============================================================================


def _telegram_command(args: list[str], ctx: "InvocationContext | None") -> int:
    """
    Telegram notification management.

    Subcommands:
        kgents town telegram status   Show Telegram notifier status
        kgents town telegram test     Send a test notification
        kgents town telegram payment  Simulate a payment notification

    Kent's Motivation Loop: Get notified when revenue flows!
    """
    if not args:
        args = ["status"]

    subcommand = args[0].lower()

    if subcommand == "status":
        return _telegram_status(ctx)
    elif subcommand == "test":
        return _telegram_test(ctx)
    elif subcommand == "payment":
        amount = float(args[1]) if len(args) > 1 else 9.99
        tier = args[2] if len(args) > 2 else "RESIDENT"
        return _telegram_payment(amount, tier, ctx)
    elif subcommand == "help":
        _emit(_telegram_command.__doc__ or "", {}, ctx)
        return 0
    else:
        _emit(f"[TELEGRAM] Unknown: {subcommand}. Try: status, test, payment", {}, ctx)
        return 1


def _telegram_status(ctx: "InvocationContext | None") -> int:
    """Show Telegram notifier status."""
    try:
        from agents.town.telegram_notifier import TelegramNotifier

        notifier = TelegramNotifier.from_env()
        status = notifier.get_status()

        _emit("\n[TELEGRAM] Notifier Status", status, ctx)
        _emit(f"  Enabled: {status['enabled']}", {}, ctx)
        _emit(f"  Configured: {status['configured']}", {}, ctx)
        _emit(f"  Bot token set: {status['bot_token_set']}", {}, ctx)
        _emit(f"  Chat ID set: {status['chat_id_set']}", {}, ctx)

        if not status["configured"]:
            _emit("\n  To configure:", {}, ctx)
            _emit("    export TELEGRAM_BOT_TOKEN=<from @BotFather>", {}, ctx)
            _emit("    export TELEGRAM_CHAT_ID=<your chat id>", {}, ctx)
            _emit("    export TELEGRAM_ENABLED=true", {}, ctx)

        return 0
    except ImportError as e:
        _emit(f"[TELEGRAM] Import error: {e}", {"error": str(e)}, ctx)
        return 1


def _telegram_test(ctx: "InvocationContext | None") -> int:
    """Send a test notification to Telegram."""
    try:
        from agents.town.telegram_notifier import TelegramNotifier

        notifier = TelegramNotifier.from_env()

        if not notifier.is_enabled:
            _emit("[TELEGRAM] Not enabled. Set TELEGRAM_ENABLED=true", {}, ctx)
            _emit("  Status:", notifier.get_status(), ctx)
            return 1

        _emit("[TELEGRAM] Sending test notification...", {}, ctx)

        async def _send() -> bool:
            return await notifier.send_test()

        result = asyncio.run(_send())

        if result:
            _emit("[TELEGRAM] Test notification sent!", {"success": True}, ctx)
            return 0
        else:
            _emit("[TELEGRAM] Failed to send. Check logs.", {"success": False}, ctx)
            return 1
    except Exception as e:
        _emit(f"[TELEGRAM] Error: {e}", {"error": str(e)}, ctx)
        return 1


def _telegram_payment(amount: float, tier: str, ctx: "InvocationContext | None") -> int:
    """Simulate a payment notification (for testing)."""
    try:
        from agents.town.telegram_notifier import TelegramNotifier

        notifier = TelegramNotifier.from_env()

        if not notifier.is_enabled:
            _emit("[TELEGRAM] Not enabled. Set TELEGRAM_ENABLED=true", {}, ctx)
            return 1

        _emit(f"[TELEGRAM] Simulating ${amount:.2f} {tier} payment...", {}, ctx)

        async def _send() -> bool:
            return await notifier.notify_payment(
                user_id="test_user_123",
                amount=amount,
                tier=tier,
            )

        result = asyncio.run(_send())

        if result:
            _emit("[TELEGRAM] Payment notification sent!", {"success": True}, ctx)
            return 0
        else:
            _emit("[TELEGRAM] Failed to send. Check logs.", {"success": False}, ctx)
            return 1
    except Exception as e:
        _emit(f"[TELEGRAM] Error: {e}", {"error": str(e)}, ctx)
        return 1


def _get_current_day() -> int:
    """Get current simulation day."""
    flux = _simulation_state.get("flux")
    if flux:
        day: int = flux.day
        return day
    return 1


# =============================================================================
# Helpers
# =============================================================================


def _emit(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """Emit output via dual-channel if ctx available, else print."""
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)


def _phase_icon(phase: str) -> str:
    """Get an icon for a citizen phase."""
    icons = {
        "IDLE": "🧍",
        "SOCIALIZING": "💬",
        "WORKING": "🔨",
        "REFLECTING": "💭",
        "RESTING": "😴",
    }
    return icons.get(phase, "❓")


def _render_bar(value: float, max_val: float, width: int = 10) -> str:
    """Render a progress bar."""
    filled = int((value / max_val) * width) if max_val > 0 else 0
    filled = max(0, min(width, filled))
    return "▓" * filled + "░" * (width - filled)
