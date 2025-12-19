"""
AGENTESE Park Context: Punchdrunk Westworld Where Hosts Can Say No.

The world.park context provides access to Punchdrunk Park:
- world.park.manifest - Show park status
- world.park.scenario.* - Crisis practice scenarios (existing feature)
- world.park.host.<name>.* - Host interactions (consent-first)
- world.park.episode.* - Session lifecycle
- world.park.mask.* - Dialogue masks

This module defines ParkNode which handles park-level operations.

AGENTESE: world.park.*

Principle Alignment:
- Ethical: Hosts can refuse interaction (Right to Rest)
- Consent-first: Boundaries are respected
- Observer-dependent: What you see depends on who you are
- Joy-Inducing: Immersive, narrative-driven experiences
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from agents.domain.drills import CrisisPhase, TimerType
    from agents.park import IntegratedScenarioState, ParkDomainBridge
    from bootstrap.umwelt import Umwelt


# Park affordances available at world.park.*
PARK_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "scenario",
    "host",
    "episode",
    "mask",
    "force",
)


# =============================================================================
# Module-level state (for scenarios)
# =============================================================================

_park_state: dict[str, Any] = {}

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


def _build_scenario_state() -> dict[str, Any]:
    """Build full scenario state dict for frontend consumption."""
    scenario = _park_state.get("scenario")
    if scenario is None:
        return {"error": "not_running"}

    masked_state = _park_state.get("masked_state")
    started_at = _park_state.get("started_at")

    # Get valid transitions from current phase
    phase_transitions_map = {
        "NORMAL": ["INCIDENT"],
        "INCIDENT": ["RESPONSE"],
        "RESPONSE": ["RECOVERY"],
        "RECOVERY": [],
    }
    current_phase = scenario.crisis_phase.name if scenario.crisis_phase else "NORMAL"
    available = phase_transitions_map.get(current_phase, [])

    # Build timer info
    timers_info = []
    for t in scenario.timers:
        timers_info.append(
            {
                "name": t.config.name,
                "timer_type": t.config.timer_type.name
                if hasattr(t.config, "timer_type")
                else "SLA",
                "status": t.status.name if t.status else "PENDING",
                "progress": t.progress,
                "remaining_seconds": getattr(t, "remaining_seconds", 0),
                "total_seconds": getattr(t.config, "duration_seconds", 3600),
            }
        )

    # Build mask info
    mask_info = None
    eigenvectors = None
    if masked_state:
        mask_info = {
            "name": masked_state.mask.name,
            "description": masked_state.mask.description,
            "archetype": masked_state.mask.archetype.name
            if hasattr(masked_state.mask, "archetype")
            else "TRICKSTER",
        }
        eigenvectors = masked_state.transformed_eigenvectors

    # Build phase transitions list
    phase_transitions = []
    for pt in getattr(scenario, "phase_transitions", []):
        phase_transitions.append(
            {
                "timestamp": pt.timestamp.isoformat() if hasattr(pt, "timestamp") else None,
                "from": pt.from_phase.name if hasattr(pt, "from_phase") else "NORMAL",
                "to": pt.to_phase.name if hasattr(pt, "to_phase") else "INCIDENT",
                "consent_debt": getattr(pt, "consent_debt", 0.0),
                "forces_used": getattr(pt, "forces_used", 0),
            }
        )

    # Get accelerated from scenario config's timers (park TimerConfig, not drills TimerConfig)
    accelerated = False
    if hasattr(scenario.config, "timers") and scenario.config.timers:
        accelerated = getattr(scenario.config.timers[0], "accelerated", False)

    return {
        "scenario_id": scenario.scenario_id,
        "name": scenario.config.name,
        "scenario_type": scenario.config.scenario_type.name,
        "is_active": not getattr(scenario, "is_completed", False),
        "timers": timers_info,
        "any_timer_critical": scenario.any_timer_critical,
        "any_timer_expired": scenario.any_timer_expired,
        "crisis_phase": current_phase,
        "available_transitions": available,
        "phase_transitions": phase_transitions,
        "consent_debt": scenario.consent_debt,
        "forces_used": scenario.forces_used,
        "forces_remaining": 3 - scenario.forces_used,
        "mask": mask_info,
        "eigenvectors": eigenvectors,
        "started_at": started_at.isoformat() if started_at else None,
        "accelerated": accelerated,
    }


# =============================================================================
# ParkNode - world.park.*
# =============================================================================


@dataclass
class ParkNode(BaseLogosNode):
    """
    world.park - Punchdrunk Park Crown Jewel.

    The Park provides:
    - Crisis practice scenarios with time pressure
    - Host interactions with consent boundaries
    - Dialogue masks for persona transformation
    - Immersive narrative experiences

    Design DNA:
    - Consent-first: Hosts can refuse uncomfortable interactions
    - Observer-dependent: What you see depends on who you are
    - Visible process: State machines are legible

    Storage:
    - services/park/persistence.py for host/episode persistence
    - In-memory for active scenarios
    """

    _handle: str = "world.park"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Park affordances vary by archetype.

        Phase 8 Observer Consistency:
        - developer/operator: Full control including force mechanics
        - architect: View everything, limited force
        - newcomer: View scenarios, no mutation
        - guest: Manifest only

        Observer gradation: tourist sees wonder, admin sees machinery.
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: scenario control, force mechanics, masks
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return PARK_AFFORDANCES

        # Architects: view everything, can use masks but not force
        if archetype_lower == "architect":
            return ("manifest", "scenario", "host", "episode", "mask")

        # Newcomers/casual: observe scenarios, no control
        if archetype_lower in ("newcomer", "casual", "reviewer"):
            return ("manifest", "scenario")

        # Guest (default): park overview only
        return ("manifest",)

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("park_state")],
        help="Show park status (scenarios, hosts, consent metrics)",
        examples=["kg park", "kg park status"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show park status."""
        scenario = _park_state.get("scenario")

        if scenario is None:
            return BasicRendering(
                summary="Punchdrunk Park: No Scenario Running",
                content=(
                    "[PARK] No scenario running.\n\n"
                    "Available commands:\n"
                    "  kg park start                Start a crisis practice\n"
                    "  kg park start --timer=gdpr   Start with GDPR 72h timer\n"
                    "  kg park start --template=data-breach  Use template\n\n"
                    "Templates: data-breach, service-outage\n"
                    "Timers: gdpr, sec, hipaa, sla, custom"
                ),
                metadata={"status": "not_running"},
            )

        # Render scenario status
        return BasicRendering(
            summary=f"PARK: {scenario.config.name}",
            content=_render_scenario_status(scenario, _park_state.get("masked_state")),
            metadata={
                "status": "running",
                "scenario_id": scenario.scenario_id,
                "name": scenario.config.name,
                "phase": scenario.crisis_phase.name if scenario.crisis_phase else None,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """ParkNode routes to ScenarioNode for most operations."""
        return BasicRendering(
            summary=f"Unknown Aspect: {aspect}",
            content=f"Aspect '{aspect}' not implemented on ParkNode. Use world.park.scenario.* for scenario operations.",
            metadata={"error": "unknown_aspect", "aspect": aspect},
        )


# =============================================================================
# ScenarioNode - world.park.scenario.*
# =============================================================================


@node(
    "world.park.scenario",
    description="Crisis practice scenario management with compliance timers",
)
@dataclass
class ScenarioNode(BaseLogosNode):
    """
    world.park.scenario - Crisis practice scenario management.

    Provides crisis practice with time pressure:
    - Compliance timers (GDPR 72h, SEC 4-day, etc.)
    - Crisis phases (NORMAL → INCIDENT → RESPONSE → RECOVERY)
    - Force mechanics with consent debt
    """

    _handle: str = "world.park.scenario"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Scenario affordances vary by archetype.

        Phase 8 Observer Consistency:
        - developer/operator: Full control (start, tick, phase, complete)
        - architect: View and advance phases (no start)
        - reviewer: View and tick only
        - guest: View only

        Observer gradation: participant vs observer vs spectator.
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full control: start, tick, phase transitions, completion
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return ("manifest", "start", "tick", "phase", "complete")

        # Architects: can advance existing scenarios
        if archetype_lower == "architect":
            return ("manifest", "tick", "phase", "complete")

        # Reviewers: can advance time, not phases
        if archetype_lower in ("reviewer", "newcomer"):
            return ("manifest", "tick")

        # Guest: read-only observation
        return ("manifest",)

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show scenario status."""
        scenario = _park_state.get("scenario")

        if scenario is None:
            return BasicRendering(
                summary="No Scenario Running",
                content=(
                    "No crisis scenario is currently running.\n\n"
                    "Use 'kg park start' to start a scenario."
                ),
                metadata={"status": "not_running"},
            )

        return BasicRendering(
            summary=f"Scenario: {scenario.config.name}",
            content=_render_scenario_status(scenario, _park_state.get("masked_state")),
            metadata={
                "status": "running",
                "scenario_id": scenario.scenario_id,
                "phase": scenario.crisis_phase.name if scenario.crisis_phase else None,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("park_state")],
        help="Start a new crisis practice scenario",
        examples=[
            "kg park start",
            "kg park start --timer=gdpr",
            "kg park start --template=data-breach",
        ],
    )
    async def start(
        self,
        observer: "Umwelt[Any, Any]",
        timer: str = "sla",
        template: str | None = None,
        accelerated: bool = True,
        mask: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Start a new crisis practice scenario."""
        from agents.domain.drills import TimerType, format_countdown
        from agents.park import (
            IntegratedScenarioType,
            ParkDomainBridge,
            create_data_breach_practice,
            create_masked_state,
            create_service_outage_practice,
        )

        # Check if already running
        if _park_state.get("scenario") is not None:
            return BasicRendering(
                summary="Scenario Already Running",
                content="Scenario already running. Use 'kg park complete' first.",
                metadata={"error": "already_running"},
            )

        # Parse timer type
        timer_map = {
            "gdpr": TimerType.GDPR_72H,
            "sec": TimerType.SEC_4DAY,
            "hipaa": TimerType.HIPAA_60DAY,
            "sla": TimerType.INTERNAL_SLA,
            "custom": TimerType.CUSTOM,
        }
        timer_type = timer_map.get(timer.lower(), TimerType.INTERNAL_SLA)

        # Create bridge and scenario
        bridge = ParkDomainBridge()

        if template == "data-breach":
            scenario = create_data_breach_practice(bridge, accelerated=accelerated)
        elif template == "service-outage":
            scenario = create_service_outage_practice(bridge, accelerated=accelerated)
        else:
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
        if mask:
            masked = create_masked_state(
                mask,
                _park_state["base_eigenvectors"],
                scenario.scenario_id,
            )
            if masked:
                _park_state["masked_state"] = masked

        # Build output
        lines = [
            "=" * 60,
            f"  PARK: {scenario.config.name}",
            f"  Type: {scenario.config.scenario_type.name}",
            f"  Mode: {'Accelerated (60x)' if accelerated else 'Real-time'}",
            "=" * 60,
        ]

        for timer_obj in scenario.timers:
            status_emoji = _timer_emoji(timer_obj.status)
            lines.append(f"\n  {status_emoji} {timer_obj.config.name}")
            lines.append(f"     Countdown: {format_countdown(timer_obj)}")

        if _park_state.get("masked_state"):
            masked = _park_state["masked_state"]
            lines.append(f"\n  Mask: {masked.mask.name}")

        lines.extend(
            [
                "\n" + "=" * 60,
                "  Use 'kg park tick' to advance time.",
                "  Use 'kg park status' to see full state.",
                "=" * 60,
            ]
        )

        # Return full scenario state for frontend
        return BasicRendering(
            summary=f"Scenario Started: {scenario.config.name}",
            content="\n".join(lines),
            metadata=_build_scenario_state(),
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("park_state")],
        help="Advance scenario timers",
        examples=["kg park tick", "kg park tick --count=10"],
    )
    async def tick(
        self,
        observer: "Umwelt[Any, Any]",
        count: int = 1,
        **kwargs: Any,
    ) -> Renderable:
        """Advance scenario timers."""
        from agents.domain.drills import format_countdown

        scenario = _park_state.get("scenario")
        if scenario is None:
            return BasicRendering(
                summary="No Scenario Running",
                content="No scenario running. Use 'kg park start' first.",
                metadata={"error": "not_running"},
            )

        bridge = _park_state["bridge"]

        lines = [f"\n[PARK] Ticking {count} time(s)...", ""]

        changed_timers = []
        for _ in range(count):
            changed = bridge.tick(scenario)
            changed_timers.extend(changed)

        if changed_timers:
            lines.append("  Timer status changed:")
            for timer in changed_timers:
                emoji = _timer_emoji(timer.status)
                lines.append(f"    {emoji} {timer.config.name} -> {timer.status.name}")

        lines.append("\n  Current timers:")
        for timer in scenario.timers:
            emoji = _timer_emoji(timer.status)
            progress_bar = _render_bar(timer.progress, 1.0, width=20)
            lines.append(
                f"    {emoji} {timer.config.name}: {format_countdown(timer)}  {progress_bar}"
            )

        # Suggest phase transition if appropriate
        if scenario.any_timer_critical and scenario.crisis_phase.name == "NORMAL":
            lines.append("\n  [!] Timer critical! Consider: kg park phase incident")
        elif scenario.any_timer_expired:
            lines.append("\n  [!] Timer EXPIRED! Scenario pressure at maximum.")

        # Return full scenario state for frontend
        return BasicRendering(
            summary=f"Ticked {count}x",
            content="\n".join(lines),
            metadata=_build_scenario_state(),
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("park_state")],
        help="Transition to a new crisis phase",
        examples=["kg park phase incident", "kg park phase response"],
    )
    async def phase(
        self,
        observer: "Umwelt[Any, Any]",
        target: str | None = None,
        phase: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Transition to a new crisis phase."""
        from agents.domain.drills import CrisisPhase

        # Accept both 'target' and 'phase' parameter names (frontend uses 'phase')
        target_phase = target or phase
        if not target_phase:
            return BasicRendering(
                summary="Missing Phase",
                content="Please specify target phase: normal, incident, response, or recovery",
                metadata={"error": "missing_phase"},
            )

        scenario = _park_state.get("scenario")
        if scenario is None:
            return BasicRendering(
                summary="No Scenario Running",
                content="No scenario running. Use 'kg park start' first.",
                metadata={"error": "not_running"},
            )

        bridge = _park_state["bridge"]

        phase_map = {
            "normal": CrisisPhase.NORMAL,
            "incident": CrisisPhase.INCIDENT,
            "response": CrisisPhase.RESPONSE,
            "recovery": CrisisPhase.RECOVERY,
        }

        if target_phase.lower() not in phase_map:
            return BasicRendering(
                summary="Invalid Phase",
                content=f"Unknown phase: {target_phase}\nValid phases: normal, incident, response, recovery",
                metadata={"error": "invalid_phase"},
            )

        crisis_phase = phase_map[target_phase.lower()]
        result = bridge.transition_crisis_phase(scenario, crisis_phase)

        if result["success"]:
            lines = [
                f"\n[PARK] Phase transition: {result['from_phase']} -> {result['to_phase']}",
                "",
                _render_phase_indicator(scenario),
            ]

            if result.get("triggered_events"):
                lines.append("\n  [!] Serendipity injected during transition!")
                for event in result["triggered_events"]:
                    lines.append(f"      {event.injection_type}: {event.description}")

            # Return full scenario state for frontend
            return BasicRendering(
                summary=f"Transitioned to {result['to_phase']}",
                content="\n".join(lines),
                metadata=_build_scenario_state(),
            )
        else:
            valid = result.get("valid_transitions", [])
            return BasicRendering(
                summary="Invalid Transition",
                content=f"Invalid transition: {result['error']}\nValid from {scenario.crisis_phase.name}: {valid}",
                metadata=result,
            )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[
            Effect.WRITES("park_state"),
            Effect.WRITES("brain_crystals"),
        ],
        help="Complete the current scenario",
        examples=[
            "kg park complete",
            "kg park complete success",
            "kg park complete failure",
        ],
    )
    async def complete(
        self,
        observer: "Umwelt[Any, Any]",
        outcome: str = "success",
        **kwargs: Any,
    ) -> Renderable:
        """Complete the current scenario."""
        scenario = _park_state.get("scenario")
        if scenario is None:
            return BasicRendering(
                summary="No Scenario Running",
                content="No scenario running.",
                metadata={"error": "not_running"},
            )

        if outcome.lower() not in ("success", "failure", "abandon"):
            return BasicRendering(
                summary="Invalid Outcome",
                content=f"Unknown outcome: {outcome}. Use success, failure, or abandon.",
                metadata={"error": "invalid_outcome"},
            )

        bridge = _park_state["bridge"]
        summary = bridge.complete_scenario(scenario, outcome.lower())

        # Emit synergy event for Brain capture (best effort)
        try:
            import asyncio

            from protocols.synergy.bus import get_synergy_bus
            from protocols.synergy.events import create_scenario_complete_event

            bus = get_synergy_bus()
            event = create_scenario_complete_event(
                session_id=scenario.scenario_id,
                scenario_name=scenario.config.name,
                scenario_type=scenario.config.scenario_type.name,
                duration_seconds=summary["duration_seconds"],
                consent_debt_final=summary["consent_debt_final"],
                forces_used=summary["forces_used"],
            )
            asyncio.get_event_loop().run_until_complete(bus.emit(event))
        except Exception:
            pass

        lines = [
            "=" * 60,
            f"  SCENARIO COMPLETE: {outcome.upper()}",
            "=" * 60,
            f"\n  Name: {summary['name']}",
            f"  Duration: {summary['duration_seconds']:.0f} seconds",
            f"  Final consent debt: {summary['consent_debt_final']:.2f}",
            f"  Forces used: {summary['forces_used']}/3",
            "\n  Timer outcomes:",
        ]

        for name, data in summary["timer_outcomes"].items():
            status_icon = "x" if data["expired"] else "o"
            lines.append(f"    [{status_icon}] {name}: {data['status']}")

        if summary["phase_transitions"]:
            lines.append(f"\n  Phase transitions: {len(summary['phase_transitions'])}")

        lines.append("\n" + "=" * 60)

        # Clear state
        _park_state.clear()

        return BasicRendering(
            summary=f"Scenario Complete: {outcome.upper()}",
            content="\n".join(lines),
            metadata=summary,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to scenario-specific aspects."""
        match aspect:
            case "start":
                return await self.start(observer, **kwargs)
            case "tick":
                return await self.tick(observer, **kwargs)
            case "phase":
                return await self.phase(observer, **kwargs)
            case "complete":
                return await self.complete(observer, **kwargs)
            case _:
                return BasicRendering(
                    summary=f"Unknown Aspect: {aspect}",
                    content=f"Aspect '{aspect}' not implemented on ScenarioNode",
                    metadata={"error": "unknown_aspect", "aspect": aspect},
                )


# =============================================================================
# MaskNode - world.park.mask.*
# =============================================================================


@node(
    "world.park.mask",
    description="Dialogue mask management for persona transformation",
)
@dataclass
class MaskNode(BaseLogosNode):
    """
    world.park.mask - Dialogue mask management.

    Masks transform persona eigenvectors for roleplaying:
    - trickster: Playfulness, creativity
    - mentor: Wisdom, warmth
    - oracle: Trust, authority
    """

    _handle: str = "world.park.mask"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Mask affordances vary by archetype.

        Phase 8 Observer Consistency:
        - developer: Full mask control including transform
        - architect/creative: Can don/doff masks
        - newcomer: Can view masks only
        - guest: No access to masks

        Observer gradation: actors wear masks, audience watches.
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full control: all mask operations
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return ("manifest", "show", "don", "doff", "transform")

        # Creative/architect: can wear masks
        if archetype_lower in ("architect", "creative", "strategic"):
            return ("manifest", "show", "don", "doff")

        # Newcomers: can view available masks
        if archetype_lower in ("newcomer", "reviewer", "casual"):
            return ("manifest", "show")

        # Guest: no mask access
        return ()

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("mask_state")],
        help="List available dialogue masks",
        examples=["kg park mask list"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """List available masks."""
        from agents.park import list_masks

        masks = list_masks()

        lines = [
            "=" * 60,
            "  DIALOGUE MASKS",
            "=" * 60,
        ]

        for m in masks:
            lines.extend(
                [
                    f"\n  {m['name']}",
                    f"    Archetype: {m['archetype']}",
                    f"    Effect: {m['description']}",
                ]
            )

        lines.extend(
            [
                "\n" + "=" * 60,
                "  Use 'kg park mask show <name>' for details.",
                "  Use 'kg park mask don <name>' to wear a mask.",
                "=" * 60,
            ]
        )

        return BasicRendering(
            summary=f"Masks: {len(masks)} available",
            content="\n".join(lines),
            metadata={"masks": masks},
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("mask_state")],
        help="Don a dialogue mask",
        examples=["kg park mask don trickster"],
    )
    async def don(
        self,
        observer: "Umwelt[Any, Any]",
        name: str,
        **kwargs: Any,
    ) -> Renderable:
        """Don a dialogue mask."""
        from agents.park import MASK_DECK, create_masked_state, get_mask

        scenario = _park_state.get("scenario")
        if scenario is None:
            return BasicRendering(
                summary="No Scenario Running",
                content="No scenario running. Use 'kg park start' first.",
                metadata={"error": "not_running"},
            )

        mask = get_mask(name)
        if mask is None:
            return BasicRendering(
                summary="Unknown Mask",
                content=f"Unknown mask: {name}\nAvailable: {', '.join(MASK_DECK.keys())}",
                metadata={"error": "unknown_mask"},
            )

        current = _park_state.get("masked_state")
        if current:
            return BasicRendering(
                summary="Already Masked",
                content=f"Already wearing {current.mask.name}. Use 'kg park mask doff' first.",
                metadata={"current_mask": current.mask.name},
            )

        base = _park_state.get("base_eigenvectors", DEFAULT_EIGENVECTORS)
        masked = create_masked_state(name, base, scenario.scenario_id)

        if masked is None:
            return BasicRendering(
                summary="Mask Failed",
                content=f"Failed to create masked state for {name}",
                metadata={"error": "mask_failed"},
            )

        _park_state["masked_state"] = masked

        lines = [
            f"\n[PARK] You don {mask.name}.",
            f'  "{mask.flavor_text}"',
            "\n  Eigenvector transform:",
        ]

        transform = mask.transform.to_dict()
        for key, delta in transform.items():
            if delta != 0:
                arrow = "^" if delta > 0 else "v"
                sign = "+" if delta > 0 else ""
                lines.append(f"    {key}: {sign}{delta:.2f} {arrow}")

        if mask.special_abilities:
            lines.append(f"\n  Abilities unlocked: {', '.join(mask.special_abilities)}")
        if mask.restrictions:
            lines.append(f"  Restricted: {', '.join(mask.restrictions)}")

        # Return full scenario state for frontend
        return BasicRendering(
            summary=f"Donned: {mask.name}",
            content="\n".join(lines),
            metadata=_build_scenario_state(),
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("mask_state")],
        help="Remove current mask",
        examples=["kg park mask doff"],
    )
    async def doff(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Remove current mask."""
        current = _park_state.get("masked_state")

        if current is None:
            return BasicRendering(
                summary="Not Wearing Mask",
                content="Not wearing a mask.",
                metadata={},
            )

        mask_name = current.mask.name
        _park_state["masked_state"] = None

        # Return full scenario state for frontend
        return BasicRendering(
            summary=f"Removed: {mask_name}",
            content=f"\n[PARK] You remove {mask_name}.\n  Your eigenvectors return to baseline.",
            metadata=_build_scenario_state(),
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to mask-specific aspects."""
        match aspect:
            case "don":
                return await self.don(observer, **kwargs)
            case "doff":
                return await self.doff(observer, **kwargs)
            case _:
                return BasicRendering(
                    summary=f"Unknown Aspect: {aspect}",
                    content=f"Aspect '{aspect}' not implemented on MaskNode",
                    metadata={"error": "unknown_aspect", "aspect": aspect},
                )


# =============================================================================
# ForceNode - world.park.force.*
# =============================================================================


@node(
    "world.park.force",
    description="Force mechanic for consent debt management",
)
@dataclass
class ForceNode(BaseLogosNode):
    """
    world.park.force - Force mechanic for consent debt.

    Forces can be used when hosts refuse, but accumulate consent debt.
    Limited to 3 per scenario.
    """

    _handle: str = "world.park.force"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Force affordances vary by archetype.

        Phase 8 Observer Consistency:
        - developer/operator: Can use force (with consent debt)
        - architect: Can view force status, not use
        - others: No force access

        Observer gradation: only operators can break consent.
        Force is a privileged action that accumulates debt.
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Operators can use force (with consequences)
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return ("manifest", "use")

        # Architects: can see force status
        if archetype_lower == "architect":
            return ("manifest",)

        # Everyone else: no force access
        return ()

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show force mechanic status."""
        scenario = _park_state.get("scenario")

        if scenario is None:
            return BasicRendering(
                summary="No Scenario Running",
                content="No scenario running. Forces are only available during scenarios.",
                metadata={"status": "not_available"},
            )

        return BasicRendering(
            summary=f"Force Status: {scenario.forces_used}/3 used",
            content=(
                f"Force mechanics available: {3 - scenario.forces_used}/3\n"
                f"Consent debt: {scenario.consent_debt:.2%}\n\n"
                "Use 'kg park force use' to force an action (accumulates consent debt)."
            ),
            metadata={
                "forces_used": scenario.forces_used,
                "forces_remaining": 3 - scenario.forces_used,
                "consent_debt": scenario.consent_debt,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("park_state")],
        help="Use a force mechanic (accumulates consent debt)",
        examples=["kg park force"],
    )
    async def use(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Use a force mechanic."""
        scenario = _park_state.get("scenario")
        if scenario is None:
            return BasicRendering(
                summary="No Scenario Running",
                content="No scenario running. Use 'kg park start' first.",
                metadata={"error": "not_running"},
            )

        bridge = _park_state["bridge"]
        old_debt = scenario.consent_debt

        success = bridge.use_force(scenario)

        if success:
            # Emit synergy event (best effort)
            try:
                import asyncio
                import uuid

                from protocols.synergy.bus import get_synergy_bus
                from protocols.synergy.events import create_force_used_event

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
                asyncio.get_event_loop().run_until_complete(bus.emit(event))
            except Exception:
                pass

            # Return full scenario state for frontend
            return BasicRendering(
                summary="Force Used",
                content=(
                    f"\n[PARK] Force used.\n"
                    f"  Consent debt: {old_debt:.2f} -> {scenario.consent_debt:.2f}\n"
                    f"  Forces remaining: {3 - scenario.forces_used}/3"
                ),
                metadata=_build_scenario_state(),
            )
        else:
            return BasicRendering(
                summary="Force Limit Reached",
                content="\n[PARK] Cannot force: limit reached (3/3 used).",
                metadata={"success": False},
            )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to force-specific aspects."""
        match aspect:
            case "use":
                return await self.use(observer, **kwargs)
            case _:
                return BasicRendering(
                    summary=f"Unknown Aspect: {aspect}",
                    content=f"Aspect '{aspect}' not implemented on ForceNode",
                    metadata={"error": "unknown_aspect", "aspect": aspect},
                )


# =============================================================================
# Helpers
# =============================================================================


def _timer_emoji(status: Any) -> str:
    """Get emoji for timer status."""
    try:
        return {
            "PENDING": "[ ]",
            "ACTIVE": "[>]",
            "WARNING": "[!]",
            "CRITICAL": "[X]",
            "EXPIRED": "[x]",
            "COMPLETED": "[o]",
            "PAUSED": "[-]",
        }.get(status.name, "[?]")
    except Exception:
        return "[?]"


def _render_bar(value: float, max_val: float, width: int = 20) -> str:
    """Render a progress bar."""
    if max_val <= 0:
        return "." * width
    ratio = min(1.0, max(0.0, value / max_val))
    filled = int(ratio * width)
    return "#" * filled + "." * (width - filled)


def _render_scenario_status(
    scenario: "IntegratedScenarioState",
    masked_state: Any,
    width: int = 60,
) -> str:
    """Render full scenario status."""
    from agents.domain.drills import format_countdown

    lines = []
    border = "=" * width

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

    lines.append("\n" + border)

    return "\n".join(lines)


def _render_phase_indicator(scenario: "IntegratedScenarioState", width: int = 60) -> str:
    """Render crisis phase diagram."""
    current = scenario.crisis_phase

    lines = [
        "-" * width,
        "  CRISIS POLYNOMIAL",
        "-" * width,
    ]

    phases = ["NORMAL", "INCIDENT", "RESPONSE", "RECOVERY"]
    phase_strs = []
    for p in phases:
        if p == current.name:
            phase_strs.append(f"[{p}]")
        else:
            phase_strs.append(p)

    lines.append("  " + " -> ".join(phase_strs))
    lines.append("-" * width)

    return "\n".join(lines)


def _render_phase_inline(phase: "CrisisPhase") -> str:
    """Render phase as inline diagram."""
    phases = ["NORMAL", "INCIDENT", "RESPONSE", "RECOVERY"]
    result = []
    for p in phases:
        if p == phase.name:
            result.append(f"[{p}]")
        else:
            result.append(p)
    return " -> ".join(result)


# =============================================================================
# Factory Functions
# =============================================================================

_park_node: ParkNode | None = None
_scenario_node: ScenarioNode | None = None
_mask_node: MaskNode | None = None
_force_node: ForceNode | None = None


def get_park_node() -> ParkNode:
    """Get the global ParkNode singleton."""
    global _park_node
    if _park_node is None:
        _park_node = ParkNode()
    return _park_node


def get_scenario_node() -> ScenarioNode:
    """Get the global ScenarioNode singleton."""
    global _scenario_node
    if _scenario_node is None:
        _scenario_node = ScenarioNode()
    return _scenario_node


def get_mask_node() -> MaskNode:
    """Get the global MaskNode singleton."""
    global _mask_node
    if _mask_node is None:
        _mask_node = MaskNode()
    return _mask_node


def get_force_node() -> ForceNode:
    """Get the global ForceNode singleton."""
    global _force_node
    if _force_node is None:
        _force_node = ForceNode()
    return _force_node


__all__ = [
    # Constants
    "PARK_AFFORDANCES",
    # Nodes
    "ParkNode",
    "ScenarioNode",
    "MaskNode",
    "ForceNode",
    # Factory
    "get_park_node",
    "get_scenario_node",
    "get_mask_node",
    "get_force_node",
]
