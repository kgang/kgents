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

See: spec/town/operad.md
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


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
        yaml_content = env.to_yaml(path)

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
