"""
Park CLI Handler: Commands for Punchdrunk Park crisis practice.

Wave 3 integration exposing ParkDomainBridge and DialogueMasks
for crisis practice scenarios with timed compliance pressure.

Commands:
    kgents park                 Show status or help
    kgents park start           Start a crisis practice scenario
    kgents park status          Show current scenario state
    kgents park tick            Advance timers and check transitions
    kgents park phase <phase>   Transition crisis phase
    kgents park mask <action>   Manage dialogue masks
    kgents park force           Use force mechanic
    kgents park complete        End scenario

Examples:
    kgents park start --timer=gdpr
    kgents park start --template=data-breach
    kgents park tick --count=10
    kgents park phase incident
    kgents park mask don trickster
    kgents park complete success

See: plans/crown-jewels-enlightened.md (Wave 3)
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from agents.domain.drills import (
    CrisisPhase,
    TimerStatus,
    TimerType,
    format_countdown,
)
from agents.park import (
    MASK_DECK,
    IntegratedScenarioState,
    IntegratedScenarioType,
    MaskedSessionState,
    ParkDomainBridge,
    create_data_breach_practice,
    create_masked_state,
    create_service_outage_practice,
    get_mask,
    list_masks,
)
from protocols.cli.path_display import display_path_header
from protocols.synergy.bus import get_synergy_bus
from protocols.synergy.events import (
    create_force_used_event,
    create_scenario_complete_event,
)

if TYPE_CHECKING:
    from agents.park import DialogueMask
    from protocols.cli.reflector import InvocationContext


# =============================================================================
# State Management
# =============================================================================

_park_state: dict[str, Any] = {}

# Default player eigenvectors (neutral starting point)
DEFAULT_EIGENVECTORS: dict[str, float] = {
    "creativity": 0.5,
    "trust": 0.5,
    "empathy": 0.5,
    "authority": 0.5,
    "playfulness": 0.5,
    "wisdom": 0.5,
    "directness": 0.5,
    "warmth": 0.5,
}


def _ensure_scenario() -> IntegratedScenarioState | None:
    """Get current scenario if running, None otherwise."""
    return _park_state.get("scenario")


def _require_scenario(ctx: "InvocationContext | None") -> IntegratedScenarioState | None:
    """Require active scenario, emit error if not running."""
    scenario = _ensure_scenario()
    if scenario is None:
        _emit(
            "[PARK] No scenario running. Use 'kgents park start' first.",
            {"error": "not_running"},
            ctx,
        )
        return None
    return scenario


# =============================================================================
# Main Handler
# =============================================================================


def _print_help() -> None:
    """Print help for park command."""
    print(__doc__)


def cmd_park(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Park CLI: Crisis practice and dialogue mask commands.

    Practice responding to compliance crises with time pressure,
    wear dialogue masks to transform your persona.
    """
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    if not args:
        return _show_status(ctx)

    subcommand = args[0].lower()

    if subcommand == "start":
        return _start_scenario(args[1:], ctx)
    elif subcommand == "status":
        return _show_status(ctx)
    elif subcommand == "tick":
        return _tick_scenario(args[1:], ctx)
    elif subcommand == "phase":
        return _transition_phase(args[1:], ctx)
    elif subcommand == "mask":
        return _mask_command(args[1:], ctx)
    elif subcommand == "force":
        return _force_action(ctx)
    elif subcommand == "complete":
        return _complete_scenario(args[1:], ctx)
    elif subcommand == "help":
        _print_help()
        return 0
    else:
        _emit(f"[PARK] Unknown command: {subcommand}", {"error": subcommand}, ctx)
        _emit("  Use 'kgents park help' for available commands.", {}, ctx)
        return 1


# =============================================================================
# Phase 1: Core Commands
# =============================================================================


def _start_scenario(args: list[str], ctx: "InvocationContext | None") -> int:
    """Start a new crisis practice scenario."""
    # Check if already running
    if _ensure_scenario() is not None:
        _emit(
            "[PARK] Scenario already running. Use 'kgents park complete' first.",
            {"error": "already_running"},
            ctx,
        )
        return 1

    # Parse arguments
    timer_type = TimerType.INTERNAL_SLA  # Default
    template = None
    accelerated = True
    mask_name = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--timer="):
            timer_str = arg.split("=")[1].lower()
            timer_map = {
                "gdpr": TimerType.GDPR_72H,
                "sec": TimerType.SEC_4DAY,
                "hipaa": TimerType.HIPAA_60DAY,
                "sla": TimerType.INTERNAL_SLA,
                "custom": TimerType.CUSTOM,
            }
            if timer_str in timer_map:
                timer_type = timer_map[timer_str]
            else:
                _emit(f"[PARK] Unknown timer: {timer_str}", {"error": timer_str}, ctx)
                _emit("  Valid timers: gdpr, sec, hipaa, sla, custom", {}, ctx)
                return 1
        elif arg.startswith("--template="):
            template = arg.split("=")[1].lower()
        elif arg == "--accelerated":
            accelerated = True
        elif arg == "--real-time":
            accelerated = False
        elif arg.startswith("--mask="):
            mask_name = arg.split("=")[1].lower()
        i += 1

    # Display AGENTESE path
    display_path_header(
        path="world.park.scenario.define",
        aspect="define",
        observer="crisis_coordinator",
        effects=["SCENARIO_CREATED", "TIMER_STARTED"],
    )

    # Create bridge and scenario
    bridge = ParkDomainBridge()

    if template == "data-breach":
        scenario = create_data_breach_practice(bridge, accelerated=accelerated)
    elif template == "service-outage":
        scenario = create_service_outage_practice(bridge, accelerated=accelerated)
    else:
        # Custom scenario
        scenario = bridge.create_crisis_scenario(
            scenario_type=IntegratedScenarioType.CRISIS_PRACTICE,
            name="Crisis Practice Session",
            description="Practice responding to a crisis with time pressure.",
            timer_type=timer_type,
            accelerated=accelerated,
        )

    # Start timers
    bridge.start_timers(scenario)

    # Store state
    _park_state["bridge"] = bridge
    _park_state["scenario"] = scenario
    _park_state["masked_state"] = None
    _park_state["base_eigenvectors"] = dict(DEFAULT_EIGENVECTORS)
    _park_state["started_at"] = datetime.now()

    # Apply mask if specified
    if mask_name:
        masked = create_masked_state(
            mask_name,
            _park_state["base_eigenvectors"],
            scenario.scenario_id,
        )
        if masked:
            _park_state["masked_state"] = masked

    # Display
    _emit("\n" + "=" * 60, {}, ctx)
    _emit(f"  PARK: {scenario.config.name}", {"name": scenario.config.name}, ctx)
    _emit(f"  Type: {scenario.config.scenario_type.name}", {}, ctx)
    _emit(f"  Mode: {'Accelerated (60x)' if accelerated else 'Real-time'}", {}, ctx)
    _emit("=" * 60, {}, ctx)

    # Show timers
    for timer in scenario.timers:
        status_emoji = _timer_emoji(timer.status)
        _emit(
            f"\n  {status_emoji} {timer.config.name}",
            {"timer": timer.config.name},
            ctx,
        )
        _emit(f"     Countdown: {format_countdown(timer)}", {}, ctx)

    # Show mask if applied
    if _park_state.get("masked_state"):
        masked = _park_state["masked_state"]
        _emit(f"\n  Mask: {masked.mask.name}", {"mask": masked.mask.name}, ctx)

    _emit("\n" + "=" * 60, {}, ctx)
    _emit("  Use 'kgents park tick' to advance time.", {}, ctx)
    _emit("  Use 'kgents park status' to see full state.", {}, ctx)
    _emit("=" * 60, {}, ctx)

    return 0


def _show_status(ctx: "InvocationContext | None") -> int:
    """Show current scenario status."""
    scenario = _ensure_scenario()

    if scenario is None:
        _emit("[PARK] No scenario running.", {}, ctx)
        _emit("\nAvailable commands:", {}, ctx)
        _emit("  kgents park start                Start a crisis practice", {}, ctx)
        _emit("  kgents park start --timer=gdpr   Start with GDPR 72h timer", {}, ctx)
        _emit("  kgents park start --template=data-breach  Use template", {}, ctx)
        _emit("\nTemplates: data-breach, service-outage", {}, ctx)
        _emit("Timers: gdpr, sec, hipaa, sla, custom", {}, ctx)
        return 0

    # Display AGENTESE path
    display_path_header(
        path="world.park.scenario.manifest",
        aspect="manifest",
        observer="crisis_coordinator",
    )

    # Render full status
    output = _render_scenario_status(scenario, _park_state.get("masked_state"))
    _emit(output, {"scenario_id": scenario.scenario_id}, ctx)

    return 0


def _tick_scenario(args: list[str], ctx: "InvocationContext | None") -> int:
    """Advance scenario timers."""
    scenario = _require_scenario(ctx)
    if scenario is None:
        return 1

    bridge: ParkDomainBridge = _park_state["bridge"]

    # Parse count
    count = 1
    for arg in args:
        if arg.startswith("--count="):
            count = int(arg.split("=")[1])

    # Display AGENTESE path
    display_path_header(
        path="world.park.scenario.tick",
        aspect="manifest",
        observer="crisis_coordinator",
        effects=["TIMER_TICK", "PHASE_TRANSITION"],
    )

    _emit(f"\n[PARK] Ticking {count} time(s)...", {"count": count}, ctx)

    changed_timers = []
    for _ in range(count):
        changed = bridge.tick(scenario)
        changed_timers.extend(changed)

    # Report changes
    if changed_timers:
        _emit("\n  Timer status changed:", {}, ctx)
        for timer in changed_timers:
            emoji = _timer_emoji(timer.status)
            _emit(f"    {emoji} {timer.config.name} -> {timer.status.name}", {}, ctx)

    # Show current timer states
    _emit("\n  Current timers:", {}, ctx)
    for timer in scenario.timers:
        emoji = _timer_emoji(timer.status)
        progress_bar = _render_bar(timer.progress, 1.0, width=20)
        _emit(
            f"    {emoji} {timer.config.name}: {format_countdown(timer)}  {progress_bar}",
            {},
            ctx,
        )

    # Suggest phase transition if appropriate
    if scenario.any_timer_critical and scenario.crisis_phase == CrisisPhase.NORMAL:
        _emit("\n  [!] Timer critical! Consider: kgents park phase incident", {}, ctx)
    elif scenario.any_timer_expired:
        _emit("\n  [!] Timer EXPIRED! Scenario pressure at maximum.", {}, ctx)

    return 0


def _complete_scenario(args: list[str], ctx: "InvocationContext | None") -> int:
    """Complete the current scenario."""
    scenario = _require_scenario(ctx)
    if scenario is None:
        return 1

    bridge: ParkDomainBridge = _park_state["bridge"]

    # Parse outcome
    outcome = "success"
    if args:
        outcome = args[0].lower()
        if outcome not in ("success", "failure", "abandon"):
            _emit(
                f"[PARK] Unknown outcome: {outcome}. Use success, failure, or abandon.",
                {"error": outcome},
                ctx,
            )
            return 1

    # Display AGENTESE path
    display_path_header(
        path="world.park.scenario.complete",
        aspect="define",
        observer="crisis_coordinator",
        effects=["SCENARIO_COMPLETE", "BRAIN_CAPTURE"],
    )

    # Complete scenario
    summary = bridge.complete_scenario(scenario, outcome)

    # Emit synergy event for Brain capture
    try:
        import asyncio

        bus = get_synergy_bus()
        event = create_scenario_complete_event(
            session_id=scenario.scenario_id,
            scenario_name=scenario.config.name,
            scenario_type=scenario.config.scenario_type.name,
            duration_seconds=summary["duration_seconds"],
            consent_debt_final=summary["consent_debt_final"],
            forces_used=summary["forces_used"],
        )
        asyncio.run(bus.emit(event))
        _emit("\n  [Synergy] Scenario captured to Brain.", {"synergy": True}, ctx)
    except Exception:
        pass  # Synergy is best-effort

    # Display summary
    _emit("\n" + "=" * 60, {}, ctx)
    _emit(f"  SCENARIO COMPLETE: {outcome.upper()}", {"outcome": outcome}, ctx)
    _emit("=" * 60, {}, ctx)
    _emit(f"\n  Name: {summary['name']}", {}, ctx)
    _emit(f"  Duration: {summary['duration_seconds']:.0f} seconds", {}, ctx)
    _emit(f"  Final consent debt: {summary['consent_debt_final']:.2f}", {}, ctx)
    _emit(f"  Forces used: {summary['forces_used']}/3", {}, ctx)

    # Timer outcomes
    _emit("\n  Timer outcomes:", {}, ctx)
    for name, data in summary["timer_outcomes"].items():
        status_icon = "x" if data["expired"] else "o"
        _emit(f"    [{status_icon}] {name}: {data['status']}", {}, ctx)

    # Phase transitions
    if summary["phase_transitions"]:
        _emit(f"\n  Phase transitions: {len(summary['phase_transitions'])}", {}, ctx)

    _emit("\n" + "=" * 60, {}, ctx)

    # Clear state
    _park_state.clear()

    return 0


# =============================================================================
# Phase 2: Crisis Phase Commands
# =============================================================================


def _transition_phase(args: list[str], ctx: "InvocationContext | None") -> int:
    """Transition to a new crisis phase."""
    scenario = _require_scenario(ctx)
    if scenario is None:
        return 1

    if not args:
        _emit("[PARK] Usage: kgents park phase <phase>", {}, ctx)
        _emit("  Phases: normal, incident, response, recovery", {}, ctx)
        _emit(f"  Current: {scenario.crisis_phase.name}", {}, ctx)
        return 1

    bridge: ParkDomainBridge = _park_state["bridge"]

    # Parse target phase
    phase_str = args[0].lower()
    phase_map = {
        "normal": CrisisPhase.NORMAL,
        "incident": CrisisPhase.INCIDENT,
        "response": CrisisPhase.RESPONSE,
        "recovery": CrisisPhase.RECOVERY,
    }

    if phase_str not in phase_map:
        _emit(f"[PARK] Unknown phase: {phase_str}", {"error": phase_str}, ctx)
        _emit("  Valid phases: normal, incident, response, recovery", {}, ctx)
        return 1

    target_phase = phase_map[phase_str]

    # Display AGENTESE path
    display_path_header(
        path="world.park.crisis.transition",
        aspect="define",
        observer="crisis_coordinator",
        effects=["PHASE_TRANSITION"],
    )

    # Attempt transition
    result = bridge.transition_crisis_phase(scenario, target_phase)

    if result["success"]:
        _emit(
            f"\n[PARK] Phase transition: {result['from_phase']} -> {result['to_phase']}",
            result,
            ctx,
        )

        # Show updated phase diagram
        _emit("\n" + _render_phase_indicator(scenario), {}, ctx)

        # Show any triggered events
        if result.get("triggered_events"):
            _emit("\n  [!] Serendipity injected during transition!", {}, ctx)
            for event in result["triggered_events"]:
                _emit(f"      {event.injection_type}: {event.description}", {}, ctx)

        return 0
    else:
        _emit(f"\n[PARK] Invalid transition: {result['error']}", result, ctx)
        valid = result.get("valid_transitions", [])
        if valid:
            _emit(f"  Valid transitions from {scenario.crisis_phase.name}: {valid}", {}, ctx)
        return 1


# =============================================================================
# Phase 3: Mask Commands
# =============================================================================


def _mask_command(args: list[str], ctx: "InvocationContext | None") -> int:
    """Handle mask subcommands."""
    if not args:
        args = ["list"]

    action = args[0].lower()

    if action == "list":
        return _mask_list(ctx)
    elif action == "show":
        if len(args) < 2:
            _emit("[PARK] Usage: kgents park mask show <name>", {}, ctx)
            return 1
        return _mask_show(args[1], ctx)
    elif action == "don":
        if len(args) < 2:
            _emit("[PARK] Usage: kgents park mask don <name>", {}, ctx)
            return 1
        return _mask_don(args[1], ctx)
    elif action == "doff":
        return _mask_doff(ctx)
    elif action == "transform":
        return _mask_transform(ctx)
    else:
        _emit(f"[PARK] Unknown mask action: {action}", {"error": action}, ctx)
        _emit("  Actions: list, show, don, doff, transform", {}, ctx)
        return 1


def _mask_list(ctx: "InvocationContext | None") -> int:
    """List available masks."""
    display_path_header(
        path="world.park.masks.manifest",
        aspect="manifest",
        observer="mask_curator",
    )

    masks = list_masks()

    _emit("\n" + "=" * 60, {}, ctx)
    _emit("  DIALOGUE MASKS", {}, ctx)
    _emit("=" * 60, {}, ctx)

    for m in masks:
        _emit(f"\n  {m['name']}", {"mask": m["name"]}, ctx)
        _emit(f"    Archetype: {m['archetype']}", {}, ctx)
        _emit(f"    Effect: {m['description']}", {}, ctx)

    _emit("\n" + "=" * 60, {}, ctx)
    _emit("  Use 'kgents park mask show <name>' for details.", {}, ctx)
    _emit("  Use 'kgents park mask don <name>' to wear a mask.", {}, ctx)
    _emit("=" * 60, {}, ctx)

    return 0


def _mask_show(name: str, ctx: "InvocationContext | None") -> int:
    """Show detailed mask information."""
    mask = get_mask(name)
    if mask is None:
        _emit(f"[PARK] Unknown mask: {name}", {"error": name}, ctx)
        _emit(f"  Available: {', '.join(MASK_DECK.keys())}", {}, ctx)
        return 1

    display_path_header(
        path=f"world.park.mask.{name}.manifest",
        aspect="manifest",
        observer="mask_curator",
    )

    _emit("\n" + _render_mask_panel(mask), {"mask": name}, ctx)

    return 0


def _mask_don(name: str, ctx: "InvocationContext | None") -> int:
    """Don a dialogue mask."""
    scenario = _require_scenario(ctx)
    if scenario is None:
        return 1

    mask = get_mask(name)
    if mask is None:
        _emit(f"[PARK] Unknown mask: {name}", {"error": name}, ctx)
        _emit(f"  Available: {', '.join(MASK_DECK.keys())}", {}, ctx)
        return 1

    # Check if already wearing
    current = _park_state.get("masked_state")
    if current:
        _emit(
            f"[PARK] Already wearing {current.mask.name}. Use 'doff' first.",
            {"current_mask": current.mask.name},
            ctx,
        )
        return 1

    display_path_header(
        path=f"world.park.mask.{name}.don",
        aspect="define",
        observer="mask_wearer",
        effects=["MASK_DONNED", "EIGENVECTOR_TRANSFORM"],
    )

    # Create masked state
    base = _park_state.get("base_eigenvectors", DEFAULT_EIGENVECTORS)
    masked = create_masked_state(name, base, scenario.scenario_id)

    if masked is None:
        _emit(f"[PARK] Failed to create masked state for {name}", {}, ctx)
        return 1

    _park_state["masked_state"] = masked

    _emit(f"\n[PARK] You don {mask.name}.", {"mask": name}, ctx)
    _emit(f'  "{mask.flavor_text}"', {}, ctx)

    # Show transform
    _emit("\n  Eigenvector transform:", {}, ctx)
    transform = mask.transform.to_dict()
    for key, delta in transform.items():
        if delta != 0:
            arrow = "^" if delta > 0 else "v"
            sign = "+" if delta > 0 else ""
            _emit(f"    {key}: {sign}{delta:.2f} {arrow}", {}, ctx)

    # Show abilities
    if mask.special_abilities:
        _emit(f"\n  Abilities unlocked: {', '.join(mask.special_abilities)}", {}, ctx)
    if mask.restrictions:
        _emit(f"  Restricted: {', '.join(mask.restrictions)}", {}, ctx)

    return 0


def _mask_doff(ctx: "InvocationContext | None") -> int:
    """Remove current mask."""
    current = _park_state.get("masked_state")

    if current is None:
        _emit("[PARK] Not wearing a mask.", {}, ctx)
        return 0

    display_path_header(
        path="world.park.mask.doff",
        aspect="define",
        observer="mask_wearer",
        effects=["MASK_REMOVED"],
    )

    mask_name = current.mask.name
    _park_state["masked_state"] = None

    _emit(f"\n[PARK] You remove {mask_name}.", {"mask": mask_name}, ctx)
    _emit("  Your eigenvectors return to baseline.", {}, ctx)

    return 0


def _mask_transform(ctx: "InvocationContext | None") -> int:
    """Show before/after eigenvector comparison."""
    masked = _park_state.get("masked_state")

    if masked is None:
        _emit("[PARK] Not wearing a mask. Nothing to compare.", {}, ctx)
        return 0

    base = masked.base_eigenvectors
    transformed = masked.transformed_eigenvectors

    _emit("\n" + "=" * 60, {}, ctx)
    _emit(f"  EIGENVECTOR TRANSFORM ({masked.mask.name})", {}, ctx)
    _emit("=" * 60, {}, ctx)
    _emit("\n  Attribute       Base    Now     Delta", {}, ctx)
    _emit("  " + "-" * 40, {}, ctx)

    for key in sorted(base.keys()):
        b = base.get(key, 0.5)
        t = transformed.get(key, 0.5)
        delta = t - b
        arrow = "^" if delta > 0 else ("v" if delta < 0 else " ")
        _emit(f"  {key:14} {b:6.2f}  {t:6.2f}  {delta:+.2f} {arrow}", {}, ctx)

    _emit("\n" + "=" * 60, {}, ctx)

    return 0


# =============================================================================
# Phase 4: Force and Integration
# =============================================================================


def _force_action(ctx: "InvocationContext | None") -> int:
    """Use a force mechanic."""
    scenario = _require_scenario(ctx)
    if scenario is None:
        return 1

    bridge: ParkDomainBridge = _park_state["bridge"]

    display_path_header(
        path="world.park.force.use",
        aspect="define",
        observer="crisis_coordinator",
        effects=["FORCE_USED", "CONSENT_DEBT_INCREASE"],
    )

    old_debt = scenario.consent_debt

    success = bridge.use_force(scenario)

    if success:
        _emit("\n[PARK] Force used.", {"success": True}, ctx)
        _emit(f"  Consent debt: {old_debt:.2f} -> {scenario.consent_debt:.2f}", {}, ctx)
        _emit(f"  Forces remaining: {3 - scenario.forces_used}/3", {}, ctx)

        # Emit synergy event
        try:
            import asyncio

            bus = get_synergy_bus()
            event = create_force_used_event(
                force_id=str(uuid.uuid4()),
                session_id=scenario.scenario_id,
                target_citizen="scenario_target",
                request="force_action",
                consent_debt_before=old_debt,
                consent_debt_after=scenario.consent_debt,
                forces_remaining=3 - scenario.forces_used,
            )
            asyncio.run(bus.emit(event))
        except Exception:
            pass

        return 0
    else:
        _emit("\n[PARK] Cannot force: limit reached (3/3 used).", {"success": False}, ctx)
        return 1


# =============================================================================
# Display Functions
# =============================================================================


def _render_scenario_status(
    scenario: IntegratedScenarioState,
    masked_state: MaskedSessionState | None,
    width: int = 60,
) -> str:
    """Render full scenario status."""
    lines = []
    border = "=" * width

    # Header
    lines.append(border)
    lines.append(f"  PARK: {scenario.config.name}")
    lines.append(f"  Type: {scenario.config.scenario_type.name}")
    lines.append(border)

    # Timers
    lines.append("\n  [TIMERS]")
    for timer in scenario.timers:
        emoji = _timer_emoji(timer.status)
        progress = _render_bar(timer.progress, 1.0, width=20)
        lines.append(f"    {emoji} {timer.config.name}")
        lines.append(f"       {format_countdown(timer)}  {progress}  {timer.progress:.0%}")

    # Phase
    lines.append("\n  [PHASE]")
    lines.append("    " + _render_phase_inline(scenario.crisis_phase))

    # Consent
    lines.append("\n  [CONSENT]")
    debt_bar = _render_bar(scenario.consent_debt, 1.0, width=10)
    forces_display = "o" * scenario.forces_used + "." * (3 - scenario.forces_used)
    lines.append(f"    Debt: {debt_bar} {scenario.consent_debt:.0%}")
    lines.append(f"    Forces: [{forces_display}] ({scenario.forces_used}/3)")

    # Mask
    if masked_state:
        lines.append(f"\n  [MASK: {masked_state.mask.name.upper()}]")
        lines.append(f"    {masked_state.mask.description}")
        # Show key deltas
        deltas = []
        transform = masked_state.mask.transform.to_dict()
        for k, v in transform.items():
            if v != 0:
                sign = "+" if v > 0 else ""
                deltas.append(f"{k} {sign}{v:.2f}")
        if deltas:
            lines.append(f"    {' | '.join(deltas[:4])}")

    lines.append("\n" + border)

    return "\n".join(lines)


def _render_phase_indicator(scenario: IntegratedScenarioState, width: int = 60) -> str:
    """Render crisis phase diagram."""
    current = scenario.crisis_phase
    phases = [CrisisPhase.NORMAL, CrisisPhase.INCIDENT, CrisisPhase.RESPONSE, CrisisPhase.RECOVERY]

    lines = []
    lines.append("-" * width)
    lines.append("  CRISIS POLYNOMIAL")
    lines.append("-" * width)

    # Phase line
    phase_strs = []
    for p in phases:
        if p == current:
            phase_strs.append(f"[{p.name}]")
        else:
            phase_strs.append(p.name)

    lines.append("  " + " -> ".join(phase_strs))

    # Valid transitions
    bridge: ParkDomainBridge = _park_state.get("bridge")
    if bridge:
        poly_display = bridge.get_polynomial_display(scenario)
        if poly_display.get("enabled"):
            valid = poly_display.get("available_transitions", [])
            if valid:
                lines.append(f"\n  Valid transitions: {', '.join(valid)}")

    lines.append("-" * width)

    return "\n".join(lines)


def _render_phase_inline(phase: CrisisPhase) -> str:
    """Render phase as inline diagram."""
    phases = ["NORMAL", "INCIDENT", "RESPONSE", "RECOVERY"]
    result = []
    for p in phases:
        if p == phase.name:
            result.append(f"[{p}]")
        else:
            result.append(p)
    return " -> ".join(result)


def _render_mask_panel(mask: "DialogueMask") -> str:
    """Render detailed mask panel."""
    from agents.park import DialogueMask

    lines = []
    width = 60
    border = "-" * width

    lines.append(border)
    lines.append(f"  {mask.name.upper()}")
    lines.append(f'  "{mask.description}"')
    lines.append(border)

    # Flavor text
    lines.append(f"\n  {mask.flavor_text}")

    # Transform
    lines.append("\n  EIGENVECTOR TRANSFORM")
    transform = mask.transform.to_dict()
    positives = [(k, v) for k, v in transform.items() if v > 0]
    negatives = [(k, v) for k, v in transform.items() if v < 0]

    for k, v in positives:
        lines.append(f"    {k}: +{v:.2f} ^")
    for k, v in negatives:
        lines.append(f"    {k}: {v:.2f} v")

    # Abilities
    if mask.special_abilities:
        lines.append("\n  SPECIAL ABILITIES")
        for ability in mask.special_abilities:
            lines.append(f"    * {ability}")

    # Restrictions
    if mask.restrictions:
        lines.append("\n  RESTRICTIONS")
        for restriction in mask.restrictions:
            lines.append(f"    x {restriction}")

    lines.append(f"\n  Intensity: {mask.intensity:.0%}")
    lines.append(border)

    return "\n".join(lines)


def _render_bar(value: float, max_val: float, width: int = 20) -> str:
    """Render a progress bar."""
    if max_val <= 0:
        return "." * width
    ratio = min(1.0, max(0.0, value / max_val))
    filled = int(ratio * width)
    return "#" * filled + "." * (width - filled)


def _timer_emoji(status: TimerStatus) -> str:
    """Get emoji for timer status."""
    return {
        TimerStatus.PENDING: "[ ]",
        TimerStatus.ACTIVE: "[>]",
        TimerStatus.WARNING: "[!]",
        TimerStatus.CRITICAL: "[X]",
        TimerStatus.EXPIRED: "[x]",
        TimerStatus.COMPLETED: "[o]",
        TimerStatus.PAUSED: "[-]",
    }.get(status, "[?]")


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
