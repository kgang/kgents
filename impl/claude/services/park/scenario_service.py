"""
Scenario Service: Structured scenarios for Punchdrunk Park.

Migrated from agents/park/scenario.py to services/park/ per AD-009 pattern.

A scenario is a pre-designed situation with:
- Citizens with specific archetypes and eigenvectors
- A trigger condition that starts the action
- Success criteria that define completion

The Five Scenario Types:
- MYSTERY: Information asymmetry, deduction, revelation
- COLLABORATION: Joint problem-solving, resource pooling
- CONFLICT: Competing interests, negotiation, resolution
- EMERGENCE: Open-ended exploration, emergent behavior
- PRACTICE: Skill development, rehearsal, coaching

Design Philosophy:
    Scenarios are not scripts. They provide initial conditions
    and success criteria; what happens in between is emergent.
    Like Punchdrunk's Sleep No More, participants create meaning
    through movement and encounter.

AGENTESE Paths:
- world.park.scenario.list     - List available scenarios
- world.park.scenario.get      - Get scenario by ID
- world.park.scenario.start    - Start a scenario session
- world.park.scenario.tick     - Advance scenario
- world.park.scenario.end      - End/abandon scenario

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from agents.park.scenario import (
    # Enums
    ScenarioPhase,
    ScenarioType,
    # Data classes
    CitizenSpec,
    SuccessCriteria,
    SuccessCriterion,
    TriggerCondition,
    # Template and Session
    ScenarioRegistry,
    ScenarioSession,
    ScenarioTemplate,
    # Polynomial
    create_scenario_polynomial,
    # Validation
    ScenarioError,
    ScenarioStateError,
    ScenarioValidationError,
    validate_citizen_spec,
    validate_scenario_template,
)

if TYPE_CHECKING:
    from agents.park.director import DirectorAgent
    from agents.town.citizen import Citizen


# =============================================================================
# Service View Types
# =============================================================================


@dataclass(frozen=True)
class ScenarioView:
    """View of a scenario template for API/CLI rendering."""

    id: str
    name: str
    scenario_type: str
    description: str
    difficulty: str
    estimated_duration_minutes: int
    citizen_count: int
    region_count: int
    tags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.scenario_type,
            "description": self.description,
            "difficulty": self.difficulty,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "citizen_count": self.citizen_count,
            "region_count": self.region_count,
            "tags": self.tags,
        }

    def to_text(self) -> str:
        return "\n".join([
            f"{self.name} [{self.scenario_type}]",
            "=" * 40,
            f"Difficulty: {self.difficulty}",
            f"Duration: ~{self.estimated_duration_minutes} min",
            f"Citizens: {self.citizen_count}",
            f"Regions: {self.region_count}",
            "",
            self.description,
        ])


@dataclass(frozen=True)
class ScenarioDetailView:
    """Detailed view of a scenario template."""

    id: str
    name: str
    scenario_type: str
    description: str
    difficulty: str
    estimated_duration_minutes: int
    citizens: list[dict[str, Any]]
    regions: list[str]
    tags: list[str]
    trigger: dict[str, Any]
    success_criteria: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.scenario_type,
            "description": self.description,
            "difficulty": self.difficulty,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "citizens": self.citizens,
            "regions": self.regions,
            "tags": self.tags,
            "trigger": self.trigger,
            "success_criteria": self.success_criteria,
        }

    def to_text(self) -> str:
        lines = [
            f"{self.name} [{self.scenario_type}]",
            "=" * 40,
            f"Difficulty: {self.difficulty}",
            f"Duration: ~{self.estimated_duration_minutes} min",
            "",
            self.description,
            "",
            "Citizens:",
        ]
        for c in self.citizens:
            lines.append(f"  - {c['name']} [{c['archetype']}] @ {c['region']}")
        lines.append("")
        lines.append(f"Regions: {', '.join(self.regions)}")
        lines.append(f"Tags: {', '.join(self.tags)}")
        return "\n".join(lines)


@dataclass(frozen=True)
class SessionView:
    """View of an active scenario session."""

    id: str
    template_id: str
    template_name: str
    phase: str
    is_active: bool
    is_terminal: bool
    citizens: list[str]
    time_elapsed: float
    progress: dict[str, bool]
    started_at: str | None
    ended_at: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "template_id": self.template_id,
            "template_name": self.template_name,
            "phase": self.phase,
            "is_active": self.is_active,
            "is_terminal": self.is_terminal,
            "citizens": self.citizens,
            "time_elapsed": self.time_elapsed,
            "progress": self.progress,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
        }

    def to_text(self) -> str:
        lines = [
            f"Session: {self.id}",
            f"Scenario: {self.template_name}",
            "=" * 40,
            f"Phase: {self.phase}",
            f"Status: {'Active' if self.is_active else 'Complete' if self.is_terminal else 'Unknown'}",
            f"Time: {self.time_elapsed:.1f}s",
            "",
            "Progress:",
        ]
        for criterion, met in self.progress.items():
            icon = "x" if met else " "
            lines.append(f"  [{icon}] {criterion}")
        return "\n".join(lines)


@dataclass(frozen=True)
class TickResultView:
    """View of a scenario tick result."""

    phase: str
    time_elapsed: float
    progress: dict[str, bool]
    is_complete: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "time_elapsed": self.time_elapsed,
            "progress": self.progress,
            "is_complete": self.is_complete,
        }


# =============================================================================
# Scenario Service
# =============================================================================


class ScenarioService:
    """
    Service layer for Scenario operations.

    Wraps ScenarioRegistry and ScenarioSession with a service-friendly API.
    Follows the Metaphysical Fullstack pattern (AD-009).

    Example:
        service = ScenarioService()

        # Register a scenario template
        service.register_template(my_template)

        # List scenarios
        scenarios = await service.list_scenarios()

        # Start a session
        session = await service.start_session("mystery-001")

        # Advance the session
        result = await service.tick(session.id)

        # End the session
        await service.abandon_session(session.id)
    """

    def __init__(
        self,
        registry: ScenarioRegistry | None = None,
        director: "DirectorAgent | None" = None,
    ) -> None:
        """
        Initialize scenario service.

        Args:
            registry: Optional pre-configured registry. Creates default if None.
            director: Optional DirectorAgent for pacing integration.
        """
        self._registry = registry or ScenarioRegistry()
        self._director = director
        self._sessions: dict[str, ScenarioSession] = {}

    @property
    def registry(self) -> ScenarioRegistry:
        """Underlying scenario registry."""
        return self._registry

    # =========================================================================
    # Template Operations
    # =========================================================================

    def register_template(self, template: ScenarioTemplate) -> list[str]:
        """
        Register a scenario template.

        Args:
            template: ScenarioTemplate to register

        Returns:
            List of validation errors (empty if valid)
        """
        errors = validate_scenario_template(template)
        if not errors:
            self._registry.register(template)
        return errors

    async def list_scenarios(
        self,
        scenario_type: ScenarioType | None = None,
        tags: list[str] | None = None,
        difficulty: str | None = None,
        limit: int = 50,
    ) -> list[ScenarioView]:
        """
        List available scenario templates.

        AGENTESE: world.park.scenario.list

        Args:
            scenario_type: Filter by type
            tags: Filter by tags (any match)
            difficulty: Filter by difficulty
            limit: Maximum results

        Returns:
            List of ScenarioView
        """
        templates = self._registry.search(
            scenario_type=scenario_type,
            tags=tags,
            difficulty=difficulty,
        )[:limit]

        return [self._template_to_view(t) for t in templates]

    async def get_scenario(
        self,
        scenario_id: str,
        detail: bool = False,
    ) -> ScenarioView | ScenarioDetailView | None:
        """
        Get a scenario template by ID.

        AGENTESE: world.park.scenario.get

        Args:
            scenario_id: Template ID
            detail: If True, return detailed view

        Returns:
            ScenarioView/ScenarioDetailView or None if not found
        """
        template = self._registry.get(scenario_id)
        if template is None:
            return None

        if detail:
            return self._template_to_detail_view(template)
        return self._template_to_view(template)

    # =========================================================================
    # Session Operations
    # =========================================================================

    async def start_session(
        self,
        scenario_id: str,
    ) -> SessionView:
        """
        Start a new scenario session.

        AGENTESE: world.park.scenario.start

        Args:
            scenario_id: Template ID to start

        Returns:
            SessionView of the new session

        Raises:
            ValueError: If scenario not found
        """
        template = self._registry.get(scenario_id)
        if template is None:
            raise ValueError(f"Scenario not found: {scenario_id}")

        session = ScenarioSession(template=template)
        session.start()

        self._sessions[session.id] = session
        return self._session_to_view(session)

    async def get_session(self, session_id: str) -> SessionView | None:
        """
        Get a session by ID.

        Args:
            session_id: Session ID

        Returns:
            SessionView or None if not found
        """
        session = self._sessions.get(session_id)
        if session is None:
            return None
        return self._session_to_view(session)

    async def list_sessions(
        self,
        active_only: bool = True,
        limit: int = 20,
    ) -> list[SessionView]:
        """
        List scenario sessions.

        Args:
            active_only: If True, only return active sessions
            limit: Maximum results

        Returns:
            List of SessionView
        """
        sessions = list(self._sessions.values())
        if active_only:
            sessions = [s for s in sessions if s.is_active]
        sessions = sessions[:limit]
        return [self._session_to_view(s) for s in sessions]

    async def tick(
        self,
        session_id: str,
        elapsed_seconds: float = 1.0,
    ) -> TickResultView:
        """
        Advance a scenario session.

        AGENTESE: world.park.scenario.tick

        Args:
            session_id: Session ID
            elapsed_seconds: Time elapsed since last tick

        Returns:
            TickResultView with status

        Raises:
            ValueError: If session not found
        """
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")

        result = session.tick(elapsed_seconds)

        # Clean up completed sessions (optional)
        if session.is_terminal:
            # Keep for history but mark as complete
            pass

        return TickResultView(
            phase=result["phase"],
            time_elapsed=result["time_elapsed"],
            progress=result["progress"],
            is_complete=result["is_complete"],
        )

    async def record_interaction(
        self,
        session_id: str,
        from_citizen: str,
        to_citizen: str,
        interaction_type: str = "dialogue",
        content: str = "",
    ) -> dict[str, Any]:
        """
        Record an interaction in a session.

        Args:
            session_id: Session ID
            from_citizen: Source citizen name
            to_citizen: Target citizen name
            interaction_type: Type of interaction
            content: Interaction content

        Returns:
            Status dict

        Raises:
            ValueError: If session not found
        """
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")

        session.record_interaction(from_citizen, to_citizen, interaction_type, content)
        return {"status": "recorded", "interaction_count": len(session.interactions)}

    async def reveal_information(
        self,
        session_id: str,
        info_key: str,
    ) -> dict[str, Any]:
        """
        Reveal information in a session (mystery scenarios).

        Args:
            session_id: Session ID
            info_key: Information key to reveal

        Returns:
            Status dict

        Raises:
            ValueError: If session not found
        """
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")

        session.reveal_information(info_key)
        return {
            "status": "revealed",
            "revealed_info": list(session.context.get("revealed_info", set())),
        }

    async def abandon_session(
        self,
        session_id: str,
        reason: str = "",
    ) -> SessionView:
        """
        Abandon a scenario session.

        AGENTESE: world.park.scenario.end (with status=abandoned)

        Args:
            session_id: Session ID
            reason: Optional reason for abandonment

        Returns:
            SessionView of abandoned session

        Raises:
            ValueError: If session not found
        """
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")

        session.abandon(reason)
        return self._session_to_view(session)

    async def complete_session(
        self,
        session_id: str,
    ) -> SessionView:
        """
        Get the final state of a completed session.

        Args:
            session_id: Session ID

        Returns:
            SessionView of completed session

        Raises:
            ValueError: If session not found
        """
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")

        return self._session_to_view(session)

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _template_to_view(self, template: ScenarioTemplate) -> ScenarioView:
        """Convert ScenarioTemplate to ScenarioView."""
        return ScenarioView(
            id=template.id,
            name=template.name,
            scenario_type=template.scenario_type.name,
            description=template.description,
            difficulty=template.difficulty,
            estimated_duration_minutes=template.estimated_duration_minutes,
            citizen_count=len(template.citizens),
            region_count=len(template.regions),
            tags=template.tags,
        )

    def _template_to_detail_view(self, template: ScenarioTemplate) -> ScenarioDetailView:
        """Convert ScenarioTemplate to ScenarioDetailView."""
        return ScenarioDetailView(
            id=template.id,
            name=template.name,
            scenario_type=template.scenario_type.name,
            description=template.description,
            difficulty=template.difficulty,
            estimated_duration_minutes=template.estimated_duration_minutes,
            citizens=[
                {
                    "name": c.name,
                    "archetype": c.archetype,
                    "region": c.region,
                    "backstory": c.backstory,
                }
                for c in template.citizens
            ],
            regions=template.regions,
            tags=template.tags,
            trigger={
                "kind": template.trigger.kind,
                "params": template.trigger.params,
            },
            success_criteria={
                "require_all": template.success_criteria.require_all,
                "criteria": [
                    {"kind": c.kind, "description": c.description}
                    for c in template.success_criteria.criteria
                ],
            },
        )

    def _session_to_view(self, session: ScenarioSession) -> SessionView:
        """Convert ScenarioSession to SessionView."""
        return SessionView(
            id=session.id,
            template_id=session.template.id,
            template_name=session.template.name,
            phase=session.phase.name,
            is_active=session.is_active,
            is_terminal=session.is_terminal,
            citizens=[c.name for c in session.citizens],
            time_elapsed=session.context.get("time_elapsed", 0.0),
            progress=session.template.success_criteria.get_progress(session.context),
            started_at=session.started_at.isoformat() if session.started_at else None,
            ended_at=session.ended_at.isoformat() if session.ended_at else None,
        )


# =============================================================================
# Factory Functions
# =============================================================================


def create_scenario_service(
    registry: ScenarioRegistry | None = None,
    director: "DirectorAgent | None" = None,
) -> ScenarioService:
    """
    Create a configured ScenarioService.

    Args:
        registry: Optional pre-configured registry
        director: Optional DirectorAgent

    Returns:
        Configured ScenarioService
    """
    return ScenarioService(registry=registry, director=director)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Service
    "ScenarioService",
    "create_scenario_service",
    # Views
    "ScenarioView",
    "ScenarioDetailView",
    "SessionView",
    "TickResultView",
    # Re-exports from agents/park/scenario
    "ScenarioType",
    "ScenarioPhase",
    "CitizenSpec",
    "TriggerCondition",
    "SuccessCriterion",
    "SuccessCriteria",
    "ScenarioTemplate",
    "ScenarioRegistry",
    "ScenarioSession",
    "create_scenario_polynomial",
    "ScenarioError",
    "ScenarioStateError",
    "ScenarioValidationError",
    "validate_citizen_spec",
    "validate_scenario_template",
]
