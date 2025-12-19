"""
Domain to Brain Handler: Auto-capture drill results.

Wave 3 synergy handler - when Domain completes a drill,
automatically captures the results to Brain for:
- Historical compliance tracking
- Drill performance trends
- Training record documentation

This enables the "Domain drill results appear in Brain automatically"
success criterion from the Enlightened Crown plan.

See: plans/crown-jewels-enlightened.md (Wave 3)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..events import SynergyEvent, SynergyEventType, SynergyResult
from .base import BaseSynergyHandler


class DomainToBrainHandler(BaseSynergyHandler):
    """
    Handler that captures Domain drill results to Brain.

    When a Domain drill completes:
    1. Creates a comprehensive drill summary
    2. Captures it to Brain as a memory crystal
    3. Returns the crystal ID for reference

    The crystal content includes:
    - Drill type and difficulty
    - Team performance metrics
    - Timeline of key decisions
    - Compliance timer outcomes
    - Recommendations for improvement
    """

    def __init__(self, auto_capture: bool = True) -> None:
        """
        Initialize the handler.

        Args:
            auto_capture: If True, automatically captures to Brain.
                         If False, just logs (useful for testing).
        """
        super().__init__()
        self._auto_capture = auto_capture

    @property
    def name(self) -> str:
        return "DomainToBrainHandler"

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        """Handle a Domain drill complete event."""
        if event.event_type != SynergyEventType.DRILL_COMPLETE:
            return self.skip(f"Not handling {event.event_type.value}")

        payload = event.payload
        drill_type = payload.get("drill_type", "unknown")
        drill_name = payload.get("drill_name", "Unnamed Drill")
        difficulty = payload.get("difficulty", "medium")
        team_size = payload.get("team_size", 0)
        duration_seconds = payload.get("duration_seconds", 0)
        outcome = payload.get("outcome", "unknown")
        score = payload.get("score", 0)
        grade = payload.get("grade", "?")
        timer_outcomes = payload.get("timer_outcomes", {})
        decisions = payload.get("decisions", [])
        recommendations = payload.get("recommendations", [])

        # Create crystal content
        content = self._create_crystal_content(
            drill_type=drill_type,
            drill_name=drill_name,
            difficulty=difficulty,
            team_size=team_size,
            duration_seconds=duration_seconds,
            outcome=outcome,
            score=score,
            grade=grade,
            timer_outcomes=timer_outcomes,
            decisions=decisions,
            recommendations=recommendations,
            timestamp=event.timestamp,
        )

        if not self._auto_capture:
            self._logger.info(f"Would capture: {content[:100]}...")
            return self.success(
                message="Dry run - would capture drill results",
                metadata={
                    "content_preview": content[:100],
                    "drill_type": drill_type,
                    "outcome": outcome,
                    "grade": grade,
                },
            )

        # Actually capture to Brain
        try:
            crystal_id = await self._capture_to_brain(content, drill_type, drill_name, event)
            self._logger.info(f"Captured drill results: {crystal_id}")
            return self.success(
                message="Drill results captured to Brain",
                artifact_id=crystal_id,
                metadata={
                    "drill_type": drill_type,
                    "drill_name": drill_name,
                    "outcome": outcome,
                    "grade": grade,
                    "score": score,
                },
            )
        except Exception as e:
            self._logger.error(f"Failed to capture to Brain: {e}")
            return self.failure(f"Capture failed: {e}")

    def _create_crystal_content(
        self,
        drill_type: str,
        drill_name: str,
        difficulty: str,
        team_size: int,
        duration_seconds: float,
        outcome: str,
        score: int,
        grade: str,
        timer_outcomes: dict[str, Any],
        decisions: list[dict[str, Any]],
        recommendations: list[str],
        timestamp: datetime,
    ) -> str:
        """Create the content to capture as a crystal."""
        # Format duration
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        duration_str = f"{minutes}m {seconds}s"

        # Format timer outcomes
        timer_lines = []
        for timer_name, timer_data in timer_outcomes.items():
            status = timer_data.get("status", "unknown")
            elapsed = timer_data.get("elapsed_seconds", 0)
            timer_lines.append(f"  - {timer_name}: {status} ({int(elapsed)}s elapsed)")

        timer_section = "\n".join(timer_lines) if timer_lines else "  No compliance timers"

        # Format key decisions
        decision_lines = []
        for i, decision in enumerate(decisions[:10], 1):  # Limit to 10
            time_str = decision.get("time", "??:??")
            actor = decision.get("actor", "Unknown")
            action = decision.get("action", "Unknown action")
            decision_lines.append(f"  {i}. [{time_str}] {actor}: {action}")

        decision_section = (
            "\n".join(decision_lines) if decision_lines else "  No decisions recorded"
        )

        # Format recommendations
        rec_lines = [f"  • {rec}" for rec in recommendations[:5]]  # Limit to 5
        rec_section = "\n".join(rec_lines) if rec_lines else "  No recommendations"

        return f"""Domain Drill Results: {drill_name}

Timestamp: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}

Overview:
- Type: {drill_type}
- Difficulty: {difficulty}
- Team Size: {team_size}
- Duration: {duration_str}

Results:
- Outcome: {outcome}
- Score: {score}/100
- Grade: {grade}

Compliance Timers:
{timer_section}

Key Decisions:
{decision_section}

Recommendations:
{rec_section}

---
This drill result was automatically captured by the Domain → Brain synergy.
Use this for compliance reporting, training records, and performance tracking.
"""

    async def _capture_to_brain(
        self,
        content: str,
        drill_type: str,
        drill_name: str,
        event: SynergyEvent,
    ) -> str:
        """Capture content to Brain and return crystal ID."""
        # Import here to avoid circular imports
        from protocols.agentese import create_brain_logos
        from protocols.agentese.node import Observer

        # Create a minimal logos for capture
        logos = create_brain_logos(embedder_type="auto")
        observer = Observer.guest()

        # Create concept ID based on drill and date
        date_str = event.timestamp.strftime("%Y-%m-%d")
        # Clean drill name for ID
        clean_name = drill_type.lower().replace(" ", "-").replace("_", "-")
        concept_id = f"drill-{clean_name}-{date_str}"

        result = await logos.invoke(
            "self.memory.capture",
            observer,
            content=content,
            concept_id=concept_id,
        )

        # Return the concept ID
        returned_id: str = str(result.get("concept_id", concept_id))
        return returned_id


class ParkToBrainHandler(BaseSynergyHandler):
    """
    Handler that captures Park session outcomes to Brain.

    When a Park scenario session completes:
    1. Creates a session summary with consent metrics
    2. Captures K-gent feedback analysis
    3. Returns the crystal ID for reference

    The crystal content includes:
    - Scenario name and type
    - Consent debt history
    - Key moments and choices
    - K-gent feedback analysis
    - Skill progression
    """

    def __init__(self, auto_capture: bool = True) -> None:
        super().__init__()
        self._auto_capture = auto_capture

    @property
    def name(self) -> str:
        return "ParkToBrainHandler"

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        """Handle a Park scenario complete event."""
        if event.event_type != SynergyEventType.SCENARIO_COMPLETE:
            return self.skip(f"Not handling {event.event_type.value}")

        payload = event.payload
        scenario_name = payload.get("scenario_name", "Unknown Scenario")
        scenario_type = payload.get("scenario_type", "unknown")
        duration_seconds = payload.get("duration_seconds", 0)
        consent_debt_final = payload.get("consent_debt_final", 0)
        forces_used = payload.get("forces_used", 0)
        key_moments = payload.get("key_moments", [])
        feedback = payload.get("feedback", {})
        skill_changes = payload.get("skill_changes", {})

        # Create crystal content
        content = self._create_crystal_content(
            scenario_name=scenario_name,
            scenario_type=scenario_type,
            duration_seconds=duration_seconds,
            consent_debt_final=consent_debt_final,
            forces_used=forces_used,
            key_moments=key_moments,
            feedback=feedback,
            skill_changes=skill_changes,
            timestamp=event.timestamp,
        )

        if not self._auto_capture:
            self._logger.info(f"Would capture: {content[:100]}...")
            return self.success(
                message="Dry run - would capture scenario results",
                metadata={
                    "content_preview": content[:100],
                    "scenario_name": scenario_name,
                    "consent_debt_final": consent_debt_final,
                },
            )

        try:
            crystal_id = await self._capture_to_brain(content, scenario_name, event)
            self._logger.info(f"Captured scenario results: {crystal_id}")
            return self.success(
                message="Scenario results captured to Brain",
                artifact_id=crystal_id,
                metadata={
                    "scenario_name": scenario_name,
                    "scenario_type": scenario_type,
                    "consent_debt_final": consent_debt_final,
                },
            )
        except Exception as e:
            self._logger.error(f"Failed to capture to Brain: {e}")
            return self.failure(f"Capture failed: {e}")

    def _create_crystal_content(
        self,
        scenario_name: str,
        scenario_type: str,
        duration_seconds: float,
        consent_debt_final: float,
        forces_used: int,
        key_moments: list[dict[str, Any]],
        feedback: dict[str, Any],
        skill_changes: dict[str, Any],
        timestamp: datetime,
    ) -> str:
        """Create the content to capture as a crystal."""
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        duration_str = f"{minutes}m {seconds}s"

        # Format key moments
        moment_lines = []
        for moment in key_moments[:8]:  # Limit to 8
            time_str = moment.get("time", "??:??")
            desc = moment.get("description", "Unknown moment")
            marker = moment.get("marker", "")
            moment_lines.append(f"  [{time_str}] {desc} {marker}")

        moment_section = "\n".join(moment_lines) if moment_lines else "  No key moments recorded"

        # Format feedback
        strengths = feedback.get("strengths", [])
        growth_areas = feedback.get("growth_areas", [])
        suggestions = feedback.get("suggestions", [])

        strength_section = (
            "\n".join([f"  ✓ {s}" for s in strengths[:3]]) if strengths else "  No strengths noted"
        )
        growth_section = (
            "\n".join([f"  △ {g}" for g in growth_areas[:3]])
            if growth_areas
            else "  No growth areas noted"
        )
        suggestion_section = (
            "\n".join([f"  → {s}" for s in suggestions[:3]]) if suggestions else "  No suggestions"
        )

        # Format skill changes
        skill_lines = []
        for skill, change in skill_changes.items():
            before = change.get("before", "?")
            after = change.get("after", "?")
            if before != after:
                skill_lines.append(f"  {skill}: {before} → {after}")

        skill_section = "\n".join(skill_lines) if skill_lines else "  No skill changes"

        return f"""Park Scenario Results: {scenario_name}

Timestamp: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}

Overview:
- Type: {scenario_type}
- Duration: {duration_str}
- Final Consent Debt: {int(consent_debt_final * 100)}%
- Forces Used: {forces_used}/3

Key Moments:
{moment_section}

K-gent Feedback:
Strengths:
{strength_section}

Growth Areas:
{growth_section}

Suggestions:
{suggestion_section}

Skill Progression:
{skill_section}

---
This scenario result was automatically captured by the Park → Brain synergy.
Use this for tracking your practice progress and reviewing key learning moments.
"""

    async def _capture_to_brain(
        self,
        content: str,
        scenario_name: str,
        event: SynergyEvent,
    ) -> str:
        """Capture content to Brain and return crystal ID."""
        from protocols.agentese import create_brain_logos
        from protocols.agentese.node import Observer

        logos = create_brain_logos(embedder_type="auto")
        observer = Observer.guest()

        date_str = event.timestamp.strftime("%Y-%m-%d")
        clean_name = scenario_name.lower().replace(" ", "-")[:30]
        concept_id = f"park-{clean_name}-{date_str}"

        result = await logos.invoke(
            "self.memory.capture",
            observer,
            content=content,
            concept_id=concept_id,
        )

        returned_id: str = str(result.get("concept_id", concept_id))
        return returned_id


__all__ = ["DomainToBrainHandler", "ParkToBrainHandler"]
