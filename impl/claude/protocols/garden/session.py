"""
Garden Protocol Session Node: AGENTESE interface for session management.

This module implements the Session Node from spec/protocols/garden-protocol.md Part IV.

Key insight from spec:
> "The unit of planning is the session, not the plan file."
> "Plans are emergent patterns in session traces—like paths worn through a garden."

Registered paths:
- self.forest.session.manifest - View current session state
- self.forest.session.begin - Start a new session
- self.forest.session.gesture - Record work in session
- self.forest.session.end - Close session, propagate to plans

Sessions track:
- Date and period (morning/afternoon/evening/night)
- Gardener (who is working)
- Plans tended (with transitions)
- Gestures (atomic units of work)
- Entropy spent
- Letter to next session
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from protocols.agentese.affordances import AspectCategory, Effect, aspect
from protocols.agentese.node import BaseLogosNode, BasicRendering, Renderable
from protocols.agentese.registry import node

from .node import load_plan, save_plan
from .types import (
    Gesture,
    GestureType,
    Mood,
    Season,
    SessionHeader,
    Trajectory,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

import yaml

# =============================================================================
# Session Affordances
# =============================================================================


SESSION_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "begin",
    "gesture",
    "end",
)


# =============================================================================
# Project Root Detection
# =============================================================================

_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


def _get_sessions_dir() -> Path:
    """Get the _sessions directory."""
    return _PROJECT_ROOT / "_sessions"


def _get_plans_dir() -> Path:
    """Get the plans directory."""
    return _PROJECT_ROOT / "plans"


def _ensure_sessions_dir() -> Path:
    """Ensure _sessions directory exists."""
    sessions_dir = _get_sessions_dir()
    sessions_dir.mkdir(exist_ok=True)
    return sessions_dir


# =============================================================================
# Session State (In-Memory)
# =============================================================================


@dataclass
class ActiveSession:
    """
    Represents an active gardening session.

    Sessions are transient and exist only while work is being done.
    When a session ends, it's persisted to _sessions/ and propagated to plans.
    """

    date: date
    period: str  # morning | afternoon | evening | night
    gardener: str
    plans_tended: dict[str, dict[str, Any]] = field(
        default_factory=dict
    )  # plan_name -> {season_start, momentum_start, ...}
    gestures: list[Gesture] = field(default_factory=list)
    entropy_spent: float = 0.0
    started_at: datetime = field(default_factory=datetime.now)

    def add_gesture(self, gesture: Gesture) -> None:
        """Add a gesture to this session."""
        self.gestures.append(gesture)

        # Track which plans were tended
        if gesture.plan not in self.plans_tended:
            self.plans_tended[gesture.plan] = {
                "first_gesture_at": datetime.now().isoformat(),
                "gesture_count": 0,
            }
        self.plans_tended[gesture.plan]["gesture_count"] += 1

        # Track entropy for void gestures
        if gesture.type == GestureType.VOID_SIP:
            self.entropy_spent += 0.02

    def to_session_header(self, letter: str = "") -> SessionHeader:
        """Convert to SessionHeader for persistence."""
        plans_tended_list = [
            f"{name} ({info.get('gesture_count', 0)} gestures)"
            for name, info in self.plans_tended.items()
        ]

        return SessionHeader(
            date=self.date,
            period=self.period,
            gardener=self.gardener,
            plans_tended=plans_tended_list,
            gestures=self.gestures,
            entropy_spent=self.entropy_spent,
            letter=letter,
        )

    def duration_minutes(self) -> int:
        """Get session duration in minutes."""
        delta = datetime.now() - self.started_at
        return int(delta.total_seconds() / 60)


# Global active session (singleton pattern)
_active_session: ActiveSession | None = None


def get_active_session() -> ActiveSession | None:
    """Get the current active session, if any."""
    return _active_session


def set_active_session(session: ActiveSession | None) -> None:
    """Set or clear the active session."""
    global _active_session
    _active_session = session


# =============================================================================
# Session Persistence
# =============================================================================


def _get_session_filename(date_: date, period: str) -> str:
    """Generate session filename."""
    return f"{date_.isoformat()}-{period}.md"


async def load_session(date_: date, period: str) -> SessionHeader | None:
    """
    Load a session from disk.

    Args:
        date_: Session date
        period: Session period (morning/afternoon/evening/night)

    Returns:
        SessionHeader if found, None otherwise
    """
    sessions_dir = _get_sessions_dir()
    filename = _get_session_filename(date_, period)
    session_file = sessions_dir / filename

    if not session_file.exists():
        return None

    try:
        content = session_file.read_text()
        if not content.startswith("---"):
            return None

        # Find end of YAML block
        end_idx = content.find("\n---\n", 3)
        if end_idx < 0:
            return None

        yaml_content = content[3:end_idx]
        parsed = yaml.safe_load(yaml_content)

        if not parsed:
            return None

        # Parse date
        session_date = parsed.get("date", date_)
        if isinstance(session_date, str):
            session_date = datetime.strptime(session_date, "%Y-%m-%d").date()

        # Parse gestures
        gestures = []
        for g in parsed.get("gestures", []):
            try:
                gesture_type = GestureType(g.get("type", "code"))
            except ValueError:
                gesture_type = GestureType.CODE

            gestures.append(
                Gesture(
                    type=gesture_type,
                    plan=g.get("plan", "unknown"),
                    summary=g.get("summary", ""),
                    files=g.get("files", []),
                )
            )

        # Extract letter from markdown body
        body = content[end_idx + 5 :]
        letter = ""
        if "## Letter to Next Session" in body:
            letter_start = body.find("## Letter to Next Session")
            letter = body[letter_start + len("## Letter to Next Session") :].strip()

        return SessionHeader(
            date=session_date,
            period=parsed.get("period", period),
            gardener=parsed.get("gardener", "unknown"),
            plans_tended=parsed.get("plans_tended", []),
            gestures=gestures,
            entropy_spent=float(parsed.get("entropy_spent", 0.0)),
            letter=letter,
        )
    except Exception:
        return None


async def save_session(session: SessionHeader) -> bool:
    """
    Save a session to disk.

    Args:
        session: SessionHeader to save

    Returns:
        True if saved successfully, False otherwise
    """
    sessions_dir = _ensure_sessions_dir()
    filename = _get_session_filename(session.date, session.period)
    session_file = sessions_dir / filename

    # Build YAML header
    header = session.to_dict()
    yaml_content = yaml.dump(
        header,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )

    # Build markdown content
    lines = [
        "---",
        yaml_content.rstrip(),
        "---",
        "",
        "## Letter to Next Session",
        "",
        session.letter or "*No letter written.*",
    ]

    content = "\n".join(lines)
    session_file.write_text(content)
    return True


async def list_recent_sessions(limit: int = 10) -> list[dict[str, Any]]:
    """
    List recent sessions.

    Args:
        limit: Maximum number of sessions to return

    Returns:
        List of session summaries (date, period, gardener, gesture_count)
    """
    sessions_dir = _get_sessions_dir()
    if not sessions_dir.exists():
        return []

    sessions: list[dict[str, Any]] = []
    for session_file in sorted(sessions_dir.glob("*.md"), reverse=True):
        if len(sessions) >= limit:
            break

        # Parse filename: YYYY-MM-DD-period.md
        stem = session_file.stem
        parts = stem.rsplit("-", 1)
        if len(parts) != 2:
            continue

        date_str, period = parts
        try:
            session_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        # Quick parse for gardener
        content = session_file.read_text()
        gardener = "unknown"
        gesture_count = 0

        if "gardener:" in content:
            for line in content.split("\n"):
                if line.startswith("gardener:"):
                    gardener = line.split(":", 1)[1].strip()
                    break

        if "gestures:" in content:
            gesture_count = content.count("- type:")

        sessions.append(
            {
                "date": session_date.isoformat(),
                "period": period,
                "gardener": gardener,
                "gesture_count": gesture_count,
                "path": f"self.forest.session.{date_str}-{period}",
            }
        )

    return sessions


# =============================================================================
# Session → Plan Propagation
# =============================================================================


async def propagate_session_to_plans(session: ActiveSession, letter: str) -> list[str]:
    """
    Propagate session state to tended plans.

    Per spec section 4.3:
    1. Plans mentioned update their `last_gardened`
    2. Mood/momentum adjust based on gestures
    3. `resonates_with` updates from `connect` gestures
    4. `entropy.spent` increases from void draws
    5. Season may transition based on accumulated gestures

    Args:
        session: The active session to propagate
        letter: The letter to include in propagation context

    Returns:
        List of plan names that were updated
    """
    updated_plans = []

    for plan_name, info in session.plans_tended.items():
        plan = await load_plan(plan_name)
        if plan is None:
            continue

        # Update last_gardened
        plan.last_gardened = session.date
        plan.gardener = session.gardener

        # Count gesture types for this plan
        plan_gestures = [g for g in session.gestures if g.plan == plan_name]
        code_count = sum(1 for g in plan_gestures if g.type == GestureType.CODE)
        insight_count = sum(1 for g in plan_gestures if g.type == GestureType.INSIGHT)
        _connect_count = sum(1 for g in plan_gestures if g.type == GestureType.CONNECT)

        # Adjust momentum based on gesture activity
        # Note: _connect_count reserved for future resonance-based momentum
        if code_count >= 3:
            plan.momentum = min(1.0, plan.momentum + 0.1)
            plan.trajectory = Trajectory.ACCELERATING
        elif code_count >= 1:
            plan.momentum = min(1.0, plan.momentum + 0.05)
            plan.trajectory = Trajectory.CRUISING
        elif insight_count >= 2:
            plan.momentum = min(1.0, plan.momentum + 0.03)

        # Update resonates_with from connect gestures
        for gesture in plan_gestures:
            if gesture.type == GestureType.CONNECT:
                # Extract plan name from summary if present
                # Format: "Connected to <plan-name>: <reason>"
                if ":" in gesture.summary:
                    parts = gesture.summary.split(":", 1)
                    connected_plan = parts[0].replace("Connected to ", "").strip()
                    if connected_plan and connected_plan not in plan.resonates_with:
                        plan.resonates_with.append(connected_plan)

        # Update entropy
        void_sips = sum(1 for g in plan_gestures if g.type == GestureType.VOID_SIP)
        for _ in range(void_sips):
            plan.entropy.sip("Session entropy draw")

        # Suggest season transition based on activity patterns
        # (Don't force, just adjust mood to suggest)
        if plan.season == Season.DORMANT and code_count > 0:
            plan.mood = Mood.CURIOUS  # Waking up
        elif plan.season == Season.SPROUTING and code_count >= 5:
            plan.mood = Mood.EXCITED  # Ready to bloom
        elif plan.season == Season.BLOOMING and insight_count >= 3:
            plan.mood = Mood.FOCUSED  # Deep work

        # Save updated plan
        if await save_plan(plan):
            updated_plans.append(plan_name)

    return updated_plans


# =============================================================================
# Period Detection
# =============================================================================


def _detect_period() -> str:
    """Detect current period based on time of day."""
    hour = datetime.now().hour
    if hour < 12:
        return "morning"
    elif hour < 17:
        return "afternoon"
    elif hour < 21:
        return "evening"
    else:
        return "night"


# =============================================================================
# Session Node
# =============================================================================


@node("self.forest.session", description="Garden Protocol - Session management")
@dataclass
class SessionNode(BaseLogosNode):
    """
    AGENTESE node for session management.

    Sessions are the primary unit of planning in Garden Protocol.
    Plans emerge from session traces like paths worn through a garden.

    Handles paths:
    - self.forest.session.manifest - View current session
    - self.forest.session.begin - Start new session
    - self.forest.session.gesture - Record work
    - self.forest.session.end - Close session

    Sessions track:
    - Gestures (atomic work units)
    - Plans tended (with state transitions)
    - Entropy spent (void draws)
    - Letter to next session
    """

    _handle: str = "self.forest.session"

    @property
    def handle(self) -> str:
        """The AGENTESE path to this node."""
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return role-gated affordances for session operations."""
        # All roles can view session state
        if archetype == "guest":
            return ("manifest",)

        # Other roles can manage sessions
        return SESSION_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Collapse to observer-appropriate representation.

        Returns current session state or recent sessions list.
        """
        session = get_active_session()

        if session is not None:
            return BasicRendering(
                summary=f"Active Session: {session.period}",
                content=f"Session in progress since {session.started_at.strftime('%H:%M')}\n"
                f"Duration: {session.duration_minutes()} minutes\n"
                f"Gestures: {len(session.gestures)}\n"
                f"Plans tended: {', '.join(session.plans_tended.keys()) or 'none'}",
                metadata={
                    "status": "active",
                    "date": session.date.isoformat(),
                    "period": session.period,
                    "gardener": session.gardener,
                    "gesture_count": len(session.gestures),
                    "plans_tended": list(session.plans_tended.keys()),
                    "entropy_spent": session.entropy_spent,
                    "duration_minutes": session.duration_minutes(),
                },
            )
        else:
            recent = await list_recent_sessions(5)
            return BasicRendering(
                summary="Session Node",
                content="No active session.\n\n"
                "Use `self.forest.session.begin` to start a session.\n\n"
                f"Recent sessions: {len(recent)}",
                metadata={
                    "status": "idle",
                    "recent_sessions": recent,
                    "affordances": list(SESSION_AFFORDANCES),
                },
            )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to aspect-specific handlers."""
        match aspect:
            case "manifest":
                return await self._manifest_impl(observer, **kwargs)
            case "begin":
                return await self._begin(observer, **kwargs)
            case "gesture":
                return await self._gesture(observer, **kwargs)
            case "end":
                return await self._end(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # =========================================================================
    # Aspects
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("sessions")],
        help="View session state",
        long_help="View current session or list recent sessions.",
        examples=["kg session", "kg session manifest"],
        see_also=["begin", "gesture", "end"],
    )
    async def _manifest_impl(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        View current session state.

        AGENTESE: self.forest.session.manifest

        Shows:
        - Active session details (if one exists)
        - Recent sessions (if no active session)
        """
        session = get_active_session()

        if session is not None:
            # Build detailed view
            lines = [
                "# Active Session",
                "",
                f"**Date**: {session.date.isoformat()}",
                f"**Period**: {session.period}",
                f"**Gardener**: {session.gardener}",
                f"**Started**: {session.started_at.strftime('%H:%M')}",
                f"**Duration**: {session.duration_minutes()} minutes",
                "",
                "## Plans Tended",
                "",
            ]

            if session.plans_tended:
                for name, info in session.plans_tended.items():
                    lines.append(f"- **{name}**: {info.get('gesture_count', 0)} gestures")
            else:
                lines.append("*No plans tended yet*")

            lines.extend(
                [
                    "",
                    "## Gestures",
                    "",
                ]
            )

            if session.gestures:
                for g in session.gestures[-10:]:  # Last 10
                    lines.append(f"- [{g.type.value}] {g.plan}: {g.summary[:50]}")
            else:
                lines.append("*No gestures recorded yet*")

            lines.extend(
                [
                    "",
                    f"**Entropy Spent**: {session.entropy_spent:.2f}",
                ]
            )

            content = "\n".join(lines)

            return BasicRendering(
                summary=f"Active: {session.date.isoformat()} {session.period}",
                content=content,
                metadata={
                    "status": "active",
                    "date": session.date.isoformat(),
                    "period": session.period,
                    "gardener": session.gardener,
                    "gesture_count": len(session.gestures),
                    "plans_tended": list(session.plans_tended.keys()),
                    "entropy_spent": session.entropy_spent,
                    "duration_minutes": session.duration_minutes(),
                },
            )
        else:
            # Show recent sessions
            recent = await list_recent_sessions(10)

            lines = [
                "# Session Manager",
                "",
                "*No active session*",
                "",
                "## Start a Session",
                "",
                "```",
                "self.forest.session.begin",
                "```",
                "",
                "## Recent Sessions",
                "",
            ]

            if recent:
                for s in recent:
                    lines.append(
                        f"- **{s['date']} {s['period']}**: {s['gardener']} ({s['gesture_count']} gestures)"
                    )
            else:
                lines.append("*No previous sessions*")

            content = "\n".join(lines)

            return BasicRendering(
                summary="Session Manager (idle)",
                content=content,
                metadata={
                    "status": "idle",
                    "recent_sessions": recent,
                },
            )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("sessions")],
        help="Start new session",
        long_help="Begin a new gardening session. Only one session can be active at a time.",
        examples=["kg session begin", "kg session begin --gardener claude-opus-4-5"],
        see_also=["manifest", "gesture", "end"],
    )
    async def _begin(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Start a new gardening session.

        AGENTESE: self.forest.session.begin

        Accepts:
        - gardener: Who is gardening (default: observer name)
        - period: morning/afternoon/evening/night (default: auto-detected)

        Returns error if a session is already active.
        """
        existing = get_active_session()
        if existing is not None:
            return BasicRendering(
                summary="Session Already Active",
                content=f"A session is already active.\n\n"
                f"Started: {existing.started_at.strftime('%H:%M')}\n"
                f"Duration: {existing.duration_minutes()} minutes\n\n"
                "End the current session with `self.forest.session.end` first.",
                metadata={
                    "status": "error",
                    "error": "session_active",
                    "existing_session": {
                        "date": existing.date.isoformat(),
                        "period": existing.period,
                        "started_at": existing.started_at.isoformat(),
                    },
                },
            )

        # Create new session
        gardener = kwargs.get("gardener", getattr(observer, "name", "unknown"))
        period = kwargs.get("period", _detect_period())

        session = ActiveSession(
            date=date.today(),
            period=period,
            gardener=gardener,
        )
        set_active_session(session)

        return BasicRendering(
            summary=f"Session Started: {period}",
            content=f"# Session Started\n\n"
            f"**Date**: {session.date.isoformat()}\n"
            f"**Period**: {period}\n"
            f"**Gardener**: {gardener}\n\n"
            "Record work with `self.forest.session.gesture`\n"
            "End session with `self.forest.session.end`",
            metadata={
                "status": "started",
                "date": session.date.isoformat(),
                "period": period,
                "gardener": gardener,
                "started_at": session.started_at.isoformat(),
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("sessions"), Effect.WRITES("plans")],
        help="Record work gesture",
        long_help="Record a gesture (atomic work unit) in the current session.",
        examples=[
            "kg session gesture --type code --plan coalition-forge --summary 'Added events'",
            "kg session gesture --type insight --plan park --summary 'Masks enable threshold crossing'",
        ],
        see_also=["manifest", "begin", "end"],
    )
    async def _gesture(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Record a gesture in the current session.

        AGENTESE: self.forest.session.gesture

        Accepts:
        - type: code, insight, decision, void_sip, void_tithe, connect, prune
        - plan: Plan name affected
        - summary: Description of work
        - files: Optional list of files affected

        Returns error if no session is active.
        """
        session = get_active_session()
        if session is None:
            return BasicRendering(
                summary="No Active Session",
                content="No session is active.\n\n"
                "Start a session with `self.forest.session.begin` first.",
                metadata={
                    "status": "error",
                    "error": "no_session",
                },
            )

        # Parse gesture type
        gesture_type_str = kwargs.get("type", kwargs.get("gesture_type", "code"))
        try:
            gesture_type = GestureType(gesture_type_str)
        except ValueError:
            return BasicRendering(
                summary="Invalid Gesture Type",
                content=f"Unknown gesture type: {gesture_type_str}\n\n"
                f"Valid types: {[t.value for t in GestureType]}",
                metadata={
                    "status": "error",
                    "error": "invalid_gesture_type",
                    "valid_types": [t.value for t in GestureType],
                },
            )

        plan_name = kwargs.get("plan", "")
        if not plan_name:
            return BasicRendering(
                summary="Plan Required",
                content="A plan name is required for gestures.\n\nSpecify with `--plan <name>`",
                metadata={
                    "status": "error",
                    "error": "plan_required",
                },
            )

        summary = kwargs.get("summary", "")
        files = kwargs.get("files", [])

        # Create and record gesture
        gesture = Gesture(
            type=gesture_type,
            plan=plan_name,
            summary=summary,
            files=files if files else [],
        )
        session.add_gesture(gesture)

        return BasicRendering(
            summary=f"Gesture: {gesture_type.value} on {plan_name}",
            content=f"# Gesture Recorded\n\n"
            f"**Type**: {gesture_type.value}\n"
            f"**Plan**: {plan_name}\n"
            f"**Summary**: {summary}\n\n"
            f"Session gestures: {len(session.gestures)}\n"
            f"Plans tended: {', '.join(session.plans_tended.keys())}",
            metadata={
                "status": "recorded",
                "gesture": gesture.to_dict(),
                "session_gesture_count": len(session.gestures),
                "session_plans": list(session.plans_tended.keys()),
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("sessions"), Effect.WRITES("plans")],
        help="End session",
        long_help="End the current session, persist it, and propagate updates to plans.",
        examples=[
            "kg session end",
            "kg session end --letter 'Good progress on coalitions today...'",
        ],
        see_also=["manifest", "begin", "gesture"],
    )
    async def _end(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        End the current session.

        AGENTESE: self.forest.session.end

        Accepts:
        - letter: Letter to next session (optional but encouraged)

        This will:
        1. Persist session to _sessions/
        2. Propagate updates to tended plans
        3. Clear the active session

        Returns error if no session is active.
        """
        session = get_active_session()
        if session is None:
            return BasicRendering(
                summary="No Active Session",
                content="No session is active.\n\n"
                "Start a session with `self.forest.session.begin` first.",
                metadata={
                    "status": "error",
                    "error": "no_session",
                },
            )

        letter = kwargs.get("letter", "")

        # Propagate to plans
        updated_plans = await propagate_session_to_plans(session, letter)

        # Create session header for persistence
        session_header = session.to_session_header(letter)

        # Persist session
        await save_session(session_header)

        # Clear active session
        duration = session.duration_minutes()
        gesture_count = len(session.gestures)
        plans_count = len(session.plans_tended)

        set_active_session(None)

        # Build summary
        lines = [
            "# Session Ended",
            "",
            f"**Date**: {session_header.date.isoformat()}",
            f"**Period**: {session_header.period}",
            f"**Duration**: {duration} minutes",
            "",
            "## Summary",
            "",
            f"- **Gestures**: {gesture_count}",
            f"- **Plans Tended**: {plans_count}",
            f"- **Plans Updated**: {len(updated_plans)}",
            f"- **Entropy Spent**: {session_header.entropy_spent:.2f}",
            "",
        ]

        if updated_plans:
            lines.append("## Updated Plans")
            lines.append("")
            for p in updated_plans:
                lines.append(f"- {p}")
            lines.append("")

        if letter:
            lines.extend(
                [
                    "## Letter to Next Session",
                    "",
                    letter,
                ]
            )
        else:
            lines.extend(
                [
                    "*No letter written.*",
                    "",
                    "Consider leaving a letter for your next session!",
                ]
            )

        content = "\n".join(lines)

        return BasicRendering(
            summary=f"Session Ended: {gesture_count} gestures, {plans_count} plans",
            content=content,
            metadata={
                "status": "ended",
                "date": session_header.date.isoformat(),
                "period": session_header.period,
                "duration_minutes": duration,
                "gesture_count": gesture_count,
                "plans_tended": list(session.plans_tended.keys()),
                "plans_updated": updated_plans,
                "entropy_spent": session_header.entropy_spent,
                "letter_written": bool(letter),
            },
        )


# =============================================================================
# Factory Functions
# =============================================================================

_session_node: SessionNode | None = None


def get_session_node() -> SessionNode:
    """Get the singleton SessionNode instance."""
    global _session_node
    if _session_node is None:
        _session_node = SessionNode()
    return _session_node


__all__ = [
    # Affordances
    "SESSION_AFFORDANCES",
    # Node
    "SessionNode",
    "get_session_node",
    # Session State
    "ActiveSession",
    "get_active_session",
    "set_active_session",
    # Persistence
    "load_session",
    "save_session",
    "list_recent_sessions",
    # Propagation
    "propagate_session_to_plans",
]
