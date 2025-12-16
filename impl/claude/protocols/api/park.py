"""
Park API Endpoints (Wave 3 Web UI).

Exposes Punchdrunk Park crisis practice scenarios via REST API:
- GET /api/park/scenario - Get current scenario state
- POST /api/park/scenario/start - Start a new scenario
- POST /api/park/scenario/tick - Advance timers
- POST /api/park/scenario/phase - Transition crisis phase
- POST /api/park/scenario/mask - Don/doff dialogue mask
- POST /api/park/scenario/force - Use force mechanic
- POST /api/park/scenario/complete - End scenario
- GET /api/park/masks - List available masks
- GET /api/park/masks/{name} - Get mask details

Based on CLI handler: protocols/cli/handlers/park.py
See: plans/_continuations/wave3-web-ui.md
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from fastapi import APIRouter

logger = logging.getLogger(__name__)

# Graceful FastAPI import
try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    BaseModel = object  # type: ignore

    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore[no-redef]
        return None

    class HTTPException(Exception):  # type: ignore[no-redef]
        """Stub HTTPException."""

        def __init__(self, status_code: int, detail: str) -> None:
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)


# --- Park Domain Imports ---

try:
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

    HAS_PARK = True
except ImportError:
    HAS_PARK = False


# --- State Management ---

_park_state: dict[str, Any] = {}

# Default player eigenvectors
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


def _ensure_scenario() -> Optional["IntegratedScenarioState"]:
    """Get current scenario if running."""
    return _park_state.get("scenario")


# --- Pydantic Models ---


class StartScenarioRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to start a new crisis scenario."""

    template: Optional[str] = Field(
        default=None,
        description="Scenario template: data-breach, service-outage",
        examples=["data-breach", "service-outage"],
    )
    timer_type: Optional[str] = Field(
        default="sla",
        description="Timer type: gdpr, sec, hipaa, sla, custom",
        examples=["gdpr", "sla"],
    )
    accelerated: bool = Field(
        default=True,
        description="Run timers in accelerated mode (60x speed)",
    )
    mask_name: Optional[str] = Field(
        default=None,
        description="Initial mask to don",
        examples=["trickster", "sage"],
    )


class TimerInfo(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Timer state information."""

    name: str = Field(..., description="Timer name")
    countdown: str = Field(..., description="Formatted countdown")
    status: str = Field(..., description="Timer status")
    progress: float = Field(..., description="Progress 0.0-1.0")
    remaining_seconds: float = Field(..., description="Remaining seconds")


class MaskInfo(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Mask information."""

    name: str = Field(..., description="Mask name")
    archetype: str = Field(..., description="Archetype")
    description: str = Field(..., description="Effect description")
    flavor_text: Optional[str] = Field(None, description="Flavor text")
    intensity: float = Field(0.5, description="Transform intensity")
    transform: dict[str, float] = Field(default_factory=dict, description="Eigenvector deltas")
    special_abilities: list[str] = Field(default_factory=list, description="Special abilities")
    restrictions: list[str] = Field(default_factory=list, description="Restrictions")


class EigenvectorState(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Eigenvector state with transform."""

    base: dict[str, float] = Field(..., description="Base eigenvectors")
    transformed: dict[str, float] = Field(..., description="Transformed eigenvectors")
    mask_applied: Optional[str] = Field(None, description="Applied mask name")


class ScenarioState(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Full scenario state response."""

    scenario_id: str = Field(..., description="Scenario ID")
    name: str = Field(..., description="Scenario name")
    scenario_type: str = Field(..., description="Scenario type")
    is_active: bool = Field(..., description="Whether scenario is active")

    # Timers
    timers: list[TimerInfo] = Field(default_factory=list, description="Timer states")
    any_timer_critical: bool = Field(False, description="Any timer critical")
    any_timer_expired: bool = Field(False, description="Any timer expired")

    # Crisis phase
    crisis_phase: str = Field("NORMAL", description="Current crisis phase")
    available_transitions: list[str] = Field(default_factory=list, description="Valid transitions")
    phase_transitions: list[dict[str, Any]] = Field(default_factory=list, description="Transition history")

    # Consent mechanics
    consent_debt: float = Field(0.0, description="Consent debt 0.0-1.0")
    forces_used: int = Field(0, description="Forces used")
    forces_remaining: int = Field(3, description="Forces remaining")

    # Mask state
    mask: Optional[MaskInfo] = Field(None, description="Current mask if worn")
    eigenvectors: Optional[EigenvectorState] = Field(None, description="Eigenvector state")

    # Timing
    started_at: Optional[str] = Field(None, description="Start timestamp")
    accelerated: bool = Field(True, description="Accelerated mode")


class TransitionPhaseRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to transition crisis phase."""

    phase: str = Field(..., description="Target phase: normal, incident, response, recovery")


class MaskActionRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request for mask action."""

    action: str = Field(..., description="Action: don, doff")
    mask_name: Optional[str] = Field(None, description="Mask name for don action")


class TickRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to tick timers."""

    count: int = Field(default=1, description="Number of ticks", ge=1, le=100)


class CompleteRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to complete scenario."""

    outcome: str = Field(
        default="success",
        description="Outcome: success, failure, abandon",
    )


class ScenarioSummary(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Scenario completion summary."""

    scenario_id: str = Field(..., description="Scenario ID")
    name: str = Field(..., description="Scenario name")
    scenario_type: str = Field(..., description="Scenario type")
    outcome: str = Field(..., description="Outcome")
    duration_seconds: float = Field(..., description="Duration in seconds")
    consent_debt_final: float = Field(..., description="Final consent debt")
    forces_used: int = Field(..., description="Total forces used")
    timer_outcomes: dict[str, dict[str, Any]] = Field(..., description="Timer outcomes")
    phase_transitions: list[dict[str, Any]] = Field(..., description="Phase transition history")
    injections_count: int = Field(0, description="Serendipity injections")


# --- Helper Functions ---


def _get_timer_type(timer_str: str) -> "TimerType":
    """Convert timer string to TimerType."""
    timer_map = {
        "gdpr": TimerType.GDPR_72H,
        "sec": TimerType.SEC_4DAY,
        "hipaa": TimerType.HIPAA_60DAY,
        "sla": TimerType.INTERNAL_SLA,
        "custom": TimerType.CUSTOM,
    }
    return timer_map.get(timer_str.lower(), TimerType.INTERNAL_SLA)


def _get_phase(phase_str: str) -> "CrisisPhase":
    """Convert phase string to CrisisPhase."""
    phase_map = {
        "normal": CrisisPhase.NORMAL,
        "incident": CrisisPhase.INCIDENT,
        "response": CrisisPhase.RESPONSE,
        "recovery": CrisisPhase.RECOVERY,
    }
    return phase_map.get(phase_str.lower(), CrisisPhase.NORMAL)


def _build_scenario_state() -> ScenarioState:
    """Build current scenario state response."""
    scenario = _ensure_scenario()

    if scenario is None:
        raise HTTPException(status_code=404, detail="No scenario running")

    bridge: ParkDomainBridge = _park_state["bridge"]
    masked_state: Optional[MaskedSessionState] = _park_state.get("masked_state")

    # Build timer info
    timers = []
    for timer in scenario.timers:
        timers.append(
            TimerInfo(
                name=timer.config.name,
                countdown=format_countdown(timer),
                status=timer.status.name,
                progress=timer.progress,
                remaining_seconds=timer.remaining.total_seconds(),
            )
        )

    # Get polynomial display for valid transitions
    poly_display = bridge.get_polynomial_display(scenario)
    available_transitions = poly_display.get("available_transitions", []) if poly_display.get("enabled") else []

    # Build mask info if wearing
    mask_info = None
    eigenvector_state = None

    if masked_state:
        mask = masked_state.mask
        mask_info = MaskInfo(
            name=mask.name,
            archetype=mask.archetype.name,
            description=mask.description,
            flavor_text=mask.flavor_text,
            intensity=mask.intensity,
            transform=mask.transform.to_dict(),
            special_abilities=mask.special_abilities,
            restrictions=mask.restrictions,
        )
        eigenvector_state = EigenvectorState(
            base=masked_state.base_eigenvectors,
            transformed=masked_state.transformed_eigenvectors,
            mask_applied=mask.name,
        )
    elif "base_eigenvectors" in _park_state:
        eigenvector_state = EigenvectorState(
            base=_park_state["base_eigenvectors"],
            transformed=_park_state["base_eigenvectors"],
            mask_applied=None,
        )

    return ScenarioState(
        scenario_id=scenario.scenario_id,
        name=scenario.config.name,
        scenario_type=scenario.config.scenario_type.name,
        is_active=scenario.is_active,
        timers=timers,
        any_timer_critical=scenario.any_timer_critical,
        any_timer_expired=scenario.any_timer_expired,
        crisis_phase=scenario.crisis_phase.name,
        available_transitions=available_transitions,
        phase_transitions=scenario.phase_transitions,
        consent_debt=scenario.consent_debt,
        forces_used=scenario.forces_used,
        forces_remaining=3 - scenario.forces_used,
        mask=mask_info,
        eigenvectors=eigenvector_state,
        started_at=_park_state.get("started_at", datetime.now()).isoformat() if _park_state.get("started_at") else None,
        accelerated=_park_state.get("accelerated", True),
    )


# --- Router Factory ---


def create_park_router() -> Optional["APIRouter"]:
    """
    Create Park API router.

    Returns None if FastAPI or Park modules not available.
    """
    if not HAS_FASTAPI:
        logger.warning("FastAPI not available, Park router disabled")
        return None

    if not HAS_PARK:
        logger.warning("Park domain not available, Park router disabled")
        return None

    router = APIRouter(prefix="/api/park", tags=["park"])

    # --- Scenario Endpoints ---

    @router.get("/scenario", response_model=ScenarioState)
    async def get_scenario() -> ScenarioState:
        """
        Get current scenario state.

        Returns the full state of the running scenario including
        timers, phase, consent mechanics, and mask state.
        """
        return _build_scenario_state()

    @router.post("/scenario/start", response_model=ScenarioState)
    async def start_scenario(request: StartScenarioRequest) -> ScenarioState:
        """
        Start a new crisis practice scenario.

        Creates a new scenario with the specified template or timer type.
        Returns the initial scenario state.
        """
        # Check if already running
        if _ensure_scenario() is not None:
            raise HTTPException(
                status_code=409,
                detail="Scenario already running. Complete it first.",
            )

        # Create bridge
        bridge = ParkDomainBridge()

        # Create scenario based on template or custom
        if request.template == "data-breach":
            scenario = create_data_breach_practice(bridge, accelerated=request.accelerated)
        elif request.template == "service-outage":
            scenario = create_service_outage_practice(bridge, accelerated=request.accelerated)
        else:
            timer_type = _get_timer_type(request.timer_type or "sla")
            scenario = bridge.create_crisis_scenario(
                scenario_type=IntegratedScenarioType.CRISIS_PRACTICE,
                name="Crisis Practice Session",
                description="Practice responding to a crisis with time pressure.",
                timer_type=timer_type,
                accelerated=request.accelerated,
            )

        # Start timers
        bridge.start_timers(scenario)

        # Store state
        _park_state["bridge"] = bridge
        _park_state["scenario"] = scenario
        _park_state["masked_state"] = None
        _park_state["base_eigenvectors"] = dict(DEFAULT_EIGENVECTORS)
        _park_state["started_at"] = datetime.now()
        _park_state["accelerated"] = request.accelerated

        # Apply mask if specified
        if request.mask_name:
            masked = create_masked_state(
                request.mask_name,
                _park_state["base_eigenvectors"],
                scenario.scenario_id,
            )
            if masked:
                _park_state["masked_state"] = masked

        return _build_scenario_state()

    @router.post("/scenario/tick", response_model=ScenarioState)
    async def tick_scenario(request: TickRequest) -> ScenarioState:
        """
        Advance scenario timers.

        Ticks the timers forward and returns updated state.
        Includes any status changes that occurred.
        """
        scenario = _ensure_scenario()
        if scenario is None:
            raise HTTPException(status_code=404, detail="No scenario running")

        bridge: ParkDomainBridge = _park_state["bridge"]

        # Tick specified number of times
        for _ in range(request.count):
            bridge.tick(scenario)

        return _build_scenario_state()

    @router.post("/scenario/phase", response_model=ScenarioState)
    async def transition_phase(request: TransitionPhaseRequest) -> ScenarioState:
        """
        Transition to a new crisis phase.

        Valid transitions:
        - NORMAL -> INCIDENT
        - INCIDENT -> RESPONSE
        - RESPONSE -> RECOVERY
        - RECOVERY -> NORMAL
        """
        scenario = _ensure_scenario()
        if scenario is None:
            raise HTTPException(status_code=404, detail="No scenario running")

        bridge: ParkDomainBridge = _park_state["bridge"]
        target_phase = _get_phase(request.phase)

        result = bridge.transition_crisis_phase(scenario, target_phase)

        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Invalid transition"),
            )

        return _build_scenario_state()

    @router.post("/scenario/mask", response_model=ScenarioState)
    async def mask_action(request: MaskActionRequest) -> ScenarioState:
        """
        Don or doff a dialogue mask.

        Actions:
        - don: Put on a mask (requires mask_name)
        - doff: Remove current mask
        """
        scenario = _ensure_scenario()
        if scenario is None:
            raise HTTPException(status_code=404, detail="No scenario running")

        if request.action == "don":
            if not request.mask_name:
                raise HTTPException(status_code=400, detail="Mask name required for don action")

            # Check if already wearing
            if _park_state.get("masked_state"):
                raise HTTPException(
                    status_code=409,
                    detail=f"Already wearing {_park_state['masked_state'].mask.name}. Doff first.",
                )

            mask = get_mask(request.mask_name)
            if mask is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Unknown mask: {request.mask_name}",
                )

            base = _park_state.get("base_eigenvectors", DEFAULT_EIGENVECTORS)
            masked = create_masked_state(request.mask_name, base, scenario.scenario_id)
            _park_state["masked_state"] = masked

        elif request.action == "doff":
            if not _park_state.get("masked_state"):
                raise HTTPException(status_code=400, detail="Not wearing a mask")
            _park_state["masked_state"] = None

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown action: {request.action}. Use 'don' or 'doff'.",
            )

        return _build_scenario_state()

    @router.post("/scenario/force", response_model=ScenarioState)
    async def use_force() -> ScenarioState:
        """
        Use a force mechanic.

        Force increases consent debt significantly but can break deadlocks.
        Limited to 3 uses per scenario.
        """
        scenario = _ensure_scenario()
        if scenario is None:
            raise HTTPException(status_code=404, detail="No scenario running")

        bridge: ParkDomainBridge = _park_state["bridge"]

        success = bridge.use_force(scenario)

        if not success:
            raise HTTPException(
                status_code=400,
                detail="Cannot force: limit reached (3/3 used)",
            )

        return _build_scenario_state()

    @router.post("/scenario/complete", response_model=ScenarioSummary)
    async def complete_scenario(request: CompleteRequest) -> ScenarioSummary:
        """
        Complete the current scenario.

        Stops all timers and returns final summary.
        Valid outcomes: success, failure, abandon
        """
        scenario = _ensure_scenario()
        if scenario is None:
            raise HTTPException(status_code=404, detail="No scenario running")

        bridge: ParkDomainBridge = _park_state["bridge"]

        if request.outcome not in ("success", "failure", "abandon"):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid outcome: {request.outcome}. Use success, failure, or abandon.",
            )

        summary = bridge.complete_scenario(scenario, request.outcome)

        # Clear state
        _park_state.clear()

        return ScenarioSummary(
            scenario_id=summary["scenario_id"],
            name=summary["name"],
            scenario_type=summary["scenario_type"],
            outcome=summary["outcome"],
            duration_seconds=summary["duration_seconds"],
            consent_debt_final=summary["consent_debt_final"],
            forces_used=summary["forces_used"],
            timer_outcomes=summary["timer_outcomes"],
            phase_transitions=summary["phase_transitions"],
            injections_count=summary.get("injections_count", 0),
        )

    # --- Mask Endpoints ---

    @router.get("/masks", response_model=list[MaskInfo])
    async def list_all_masks() -> list[MaskInfo]:
        """
        List all available dialogue masks.

        Returns basic info for all masks in the deck.
        """
        masks = []
        for name, mask in MASK_DECK.items():
            masks.append(
                MaskInfo(
                    name=mask.name,
                    archetype=mask.archetype.name,
                    description=mask.description,
                    flavor_text=mask.flavor_text,
                    intensity=mask.intensity,
                    transform=mask.transform.to_dict(),
                    special_abilities=mask.special_abilities,
                    restrictions=mask.restrictions,
                )
            )
        return masks

    @router.get("/masks/{name}", response_model=MaskInfo)
    async def get_mask_detail(name: str) -> MaskInfo:
        """
        Get detailed mask information.

        Returns full details for a specific mask.
        """
        mask = get_mask(name)
        if mask is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown mask: {name}. Available: {', '.join(MASK_DECK.keys())}",
            )

        return MaskInfo(
            name=mask.name,
            archetype=mask.archetype.name,
            description=mask.description,
            flavor_text=mask.flavor_text,
            intensity=mask.intensity,
            transform=mask.transform.to_dict(),
            special_abilities=mask.special_abilities,
            restrictions=mask.restrictions,
        )

    # --- Status Endpoint ---

    @router.get("/status")
    async def get_status() -> dict[str, Any]:
        """
        Get Park system status.

        Returns whether a scenario is running and basic info.
        """
        scenario = _ensure_scenario()

        return {
            "running": scenario is not None,
            "scenario_id": scenario.scenario_id if scenario else None,
            "scenario_name": scenario.config.name if scenario else None,
            "masks_available": len(MASK_DECK),
        }

    return router


# --- Exports ---

__all__ = [
    "create_park_router",
    "StartScenarioRequest",
    "ScenarioState",
    "MaskInfo",
    "TimerInfo",
    "ScenarioSummary",
]
