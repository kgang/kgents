"""
Tests for Garden Protocol Session Node.

Tests cover:
- Session lifecycle (begin, gesture, end)
- Session persistence
- Session → Plan propagation
- Edge cases (no active session, session already active)
"""

from __future__ import annotations

import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from protocols.garden.session import (
    SESSION_AFFORDANCES,
    ActiveSession,
    SessionNode,
    _detect_period,
    get_active_session,
    get_session_node,
    list_recent_sessions,
    load_session,
    propagate_session_to_plans,
    save_session,
    set_active_session,
)
from protocols.garden.types import (
    Gesture,
    GestureType,
    SessionHeader,
)

# =============================================================================
# Test Fixtures
# =============================================================================


class MockObserver:
    """Mock observer for testing."""

    name: str = "test-observer"
    archetype: str = "meta"
    capabilities: frozenset[str] = frozenset()


@pytest.fixture
def observer() -> MockObserver:
    """Create a mock observer."""
    return MockObserver()


@pytest.fixture
def clean_session():
    """Ensure no active session before/after test."""
    set_active_session(None)
    yield
    set_active_session(None)


@pytest.fixture
def active_session(clean_session) -> ActiveSession:
    """Create and set an active session."""
    session = ActiveSession(
        date=date.today(),
        period="morning",
        gardener="test-gardener",
    )
    set_active_session(session)
    return session


@pytest.fixture
def temp_sessions_dir(tmp_path: Path):
    """Create a temporary sessions directory."""
    sessions_dir = tmp_path / "_sessions"
    sessions_dir.mkdir()
    return sessions_dir


# =============================================================================
# Test ActiveSession
# =============================================================================


class TestActiveSession:
    """Tests for ActiveSession dataclass."""

    def test_create_session(self):
        """Test creating an active session."""
        session = ActiveSession(
            date=date.today(),
            period="morning",
            gardener="claude",
        )
        assert session.date == date.today()
        assert session.period == "morning"
        assert session.gardener == "claude"
        assert session.gestures == []
        assert session.plans_tended == {}
        assert session.entropy_spent == 0.0

    def test_add_gesture(self):
        """Test adding a gesture to session."""
        session = ActiveSession(
            date=date.today(),
            period="morning",
            gardener="claude",
        )

        gesture = Gesture(
            type=GestureType.CODE,
            plan="test-plan",
            summary="Added feature",
            files=["test.py"],
        )
        session.add_gesture(gesture)

        assert len(session.gestures) == 1
        assert "test-plan" in session.plans_tended
        assert session.plans_tended["test-plan"]["gesture_count"] == 1

    def test_add_multiple_gestures_same_plan(self):
        """Test adding multiple gestures to same plan."""
        session = ActiveSession(
            date=date.today(),
            period="afternoon",
            gardener="claude",
        )

        for i in range(3):
            session.add_gesture(
                Gesture(
                    type=GestureType.CODE,
                    plan="test-plan",
                    summary=f"Change {i}",
                )
            )

        assert len(session.gestures) == 3
        assert session.plans_tended["test-plan"]["gesture_count"] == 3

    def test_void_sip_tracks_entropy(self):
        """Test that void_sip gestures track entropy."""
        session = ActiveSession(
            date=date.today(),
            period="evening",
            gardener="claude",
        )

        session.add_gesture(
            Gesture(
                type=GestureType.VOID_SIP,
                plan="test-plan",
                summary="Explored tangent",
            )
        )

        assert session.entropy_spent == 0.02

    def test_to_session_header(self):
        """Test converting to SessionHeader."""
        session = ActiveSession(
            date=date.today(),
            period="night",
            gardener="claude",
        )
        session.add_gesture(
            Gesture(
                type=GestureType.CODE,
                plan="test-plan",
                summary="Test",
            )
        )

        header = session.to_session_header("Letter content")

        assert header.date == date.today()
        assert header.period == "night"
        assert header.gardener == "claude"
        assert len(header.plans_tended) == 1
        assert len(header.gestures) == 1
        assert header.letter == "Letter content"

    def test_duration_minutes(self):
        """Test duration calculation."""
        session = ActiveSession(
            date=date.today(),
            period="morning",
            gardener="claude",
        )
        # Just started, should be ~0 minutes
        assert session.duration_minutes() >= 0
        assert session.duration_minutes() < 1  # Should be less than 1 minute


# =============================================================================
# Test Session State Management
# =============================================================================


class TestSessionState:
    """Tests for session state management."""

    def test_get_active_session_none(self, clean_session):
        """Test getting session when none active."""
        assert get_active_session() is None

    def test_set_and_get_session(self, clean_session):
        """Test setting and getting active session."""
        session = ActiveSession(
            date=date.today(),
            period="morning",
            gardener="test",
        )
        set_active_session(session)
        assert get_active_session() is session

    def test_clear_session(self, active_session):
        """Test clearing active session."""
        assert get_active_session() is not None
        set_active_session(None)
        assert get_active_session() is None


# =============================================================================
# Test Period Detection
# =============================================================================


class TestPeriodDetection:
    """Tests for automatic period detection."""

    def test_detect_period_morning(self):
        """Test morning detection."""
        with patch("protocols.garden.session.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 9, 0)
            assert _detect_period() == "morning"

    def test_detect_period_afternoon(self):
        """Test afternoon detection."""
        with patch("protocols.garden.session.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 14, 0)
            assert _detect_period() == "afternoon"

    def test_detect_period_evening(self):
        """Test evening detection."""
        with patch("protocols.garden.session.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 19, 0)
            assert _detect_period() == "evening"

    def test_detect_period_night(self):
        """Test night detection."""
        with patch("protocols.garden.session.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 22, 0)
            assert _detect_period() == "night"


# =============================================================================
# Test Session Persistence
# =============================================================================


class TestSessionPersistence:
    """Tests for session persistence."""

    @pytest.mark.asyncio
    async def test_save_and_load_session(self, temp_sessions_dir: Path):
        """Test saving and loading a session."""
        header = SessionHeader(
            date=date(2025, 12, 18),
            period="morning",
            gardener="claude",
            plans_tended=["test-plan (5 gestures)"],
            gestures=[
                Gesture(
                    type=GestureType.CODE,
                    plan="test-plan",
                    summary="Test change",
                    files=["test.py"],
                )
            ],
            entropy_spent=0.02,
            letter="Test letter content",
        )

        # Patch to use temp directory
        with patch(
            "protocols.garden.session._get_sessions_dir", return_value=temp_sessions_dir
        ):
            with patch(
                "protocols.garden.session._ensure_sessions_dir",
                return_value=temp_sessions_dir,
            ):
                # Save
                result = await save_session(header)
                assert result is True

                # Verify file exists
                session_file = temp_sessions_dir / "2025-12-18-morning.md"
                assert session_file.exists()

                # Load
                loaded = await load_session(date(2025, 12, 18), "morning")
                assert loaded is not None
                assert loaded.date == date(2025, 12, 18)
                assert loaded.period == "morning"
                assert loaded.gardener == "claude"
                assert len(loaded.gestures) == 1
                assert "Test letter content" in loaded.letter

    @pytest.mark.asyncio
    async def test_load_nonexistent_session(self, temp_sessions_dir: Path):
        """Test loading a session that doesn't exist."""
        with patch(
            "protocols.garden.session._get_sessions_dir", return_value=temp_sessions_dir
        ):
            loaded = await load_session(date(2025, 1, 1), "morning")
            assert loaded is None

    @pytest.mark.asyncio
    async def test_list_recent_sessions(self, temp_sessions_dir: Path):
        """Test listing recent sessions."""
        # Create some test sessions
        for i, period in enumerate(["morning", "afternoon", "evening"]):
            session_file = temp_sessions_dir / f"2025-12-{18 + i:02d}-{period}.md"
            session_file.write_text(f"""---
date: 2025-12-{18 + i:02d}
period: {period}
gardener: claude
gestures:
  - type: code
    plan: test
    summary: test
---
""")

        with patch(
            "protocols.garden.session._get_sessions_dir", return_value=temp_sessions_dir
        ):
            sessions = await list_recent_sessions(10)
            assert len(sessions) == 3
            # Should be sorted by date, most recent first
            assert sessions[0]["period"] == "evening"


# =============================================================================
# Test Session Node
# =============================================================================


class TestSessionNodeRegistration:
    """Tests for SessionNode registration."""

    def test_node_exists(self):
        """Test that SessionNode exists."""
        assert SessionNode is not None

    def test_node_handle(self):
        """Test node handle."""
        node = SessionNode()
        assert node.handle == "self.forest.session"

    def test_affordances_defined(self):
        """Test that affordances are defined."""
        assert len(SESSION_AFFORDANCES) == 4
        assert "manifest" in SESSION_AFFORDANCES
        assert "begin" in SESSION_AFFORDANCES
        assert "gesture" in SESSION_AFFORDANCES
        assert "end" in SESSION_AFFORDANCES

    def test_singleton_factory(self):
        """Test singleton factory function."""
        node1 = get_session_node()
        node2 = get_session_node()
        assert node1 is node2


class TestSessionNodeAffordances:
    """Tests for affordances by role."""

    def test_guest_affordances(self):
        """Test guest gets limited affordances."""
        node = SessionNode()
        affordances = node._get_affordances_for_archetype("guest")
        assert affordances == ("manifest",)

    def test_meta_affordances(self):
        """Test meta gets full affordances."""
        node = SessionNode()
        affordances = node._get_affordances_for_archetype("meta")
        assert affordances == SESSION_AFFORDANCES

    def test_ops_affordances(self):
        """Test ops gets full affordances."""
        node = SessionNode()
        affordances = node._get_affordances_for_archetype("ops")
        assert affordances == SESSION_AFFORDANCES


# =============================================================================
# Test Session Node Aspects
# =============================================================================


class TestManifestAspect:
    """Tests for manifest aspect."""

    @pytest.mark.asyncio
    async def test_manifest_no_session(self, observer: MockObserver, clean_session):
        """Test manifest when no session active."""
        node = SessionNode()
        result = await node._manifest_impl(observer)

        assert "No active session" in result.content
        assert result.metadata["status"] == "idle"

    @pytest.mark.asyncio
    async def test_manifest_with_session(
        self, observer: MockObserver, active_session: ActiveSession
    ):
        """Test manifest with active session."""
        node = SessionNode()
        result = await node._manifest_impl(observer)

        assert "Active Session" in result.content
        assert result.metadata["status"] == "active"
        assert result.metadata["period"] == "morning"


class TestBeginAspect:
    """Tests for begin aspect."""

    @pytest.mark.asyncio
    async def test_begin_creates_session(self, observer: MockObserver, clean_session):
        """Test beginning a new session."""
        node = SessionNode()
        result = await node._begin(observer, gardener="test-gardener", period="morning")

        assert result.metadata["status"] == "started"
        assert result.metadata["gardener"] == "test-gardener"
        assert result.metadata["period"] == "morning"

        # Verify session was created
        session = get_active_session()
        assert session is not None
        assert session.gardener == "test-gardener"

    @pytest.mark.asyncio
    async def test_begin_with_active_session(
        self, observer: MockObserver, active_session: ActiveSession
    ):
        """Test beginning when session already active."""
        node = SessionNode()
        result = await node._begin(observer)

        assert result.metadata["status"] == "error"
        assert result.metadata["error"] == "session_active"


class TestGestureAspect:
    """Tests for gesture aspect."""

    @pytest.mark.asyncio
    async def test_gesture_no_session(self, observer: MockObserver, clean_session):
        """Test gesture when no session active."""
        node = SessionNode()
        result = await node._gesture(
            observer,
            type="code",
            plan="test-plan",
            summary="Test",
        )

        assert result.metadata["status"] == "error"
        assert result.metadata["error"] == "no_session"

    @pytest.mark.asyncio
    async def test_gesture_records(
        self, observer: MockObserver, active_session: ActiveSession
    ):
        """Test recording a gesture."""
        node = SessionNode()
        result = await node._gesture(
            observer,
            type="code",
            plan="test-plan",
            summary="Added feature",
            files=["test.py"],
        )

        assert result.metadata["status"] == "recorded"
        assert len(active_session.gestures) == 1
        assert "test-plan" in active_session.plans_tended

    @pytest.mark.asyncio
    async def test_gesture_invalid_type(
        self, observer: MockObserver, active_session: ActiveSession
    ):
        """Test gesture with invalid type."""
        node = SessionNode()
        result = await node._gesture(
            observer,
            type="invalid",
            plan="test-plan",
            summary="Test",
        )

        assert result.metadata["status"] == "error"
        assert result.metadata["error"] == "invalid_gesture_type"

    @pytest.mark.asyncio
    async def test_gesture_missing_plan(
        self, observer: MockObserver, active_session: ActiveSession
    ):
        """Test gesture without plan."""
        node = SessionNode()
        result = await node._gesture(
            observer,
            type="code",
            summary="Test",
        )

        assert result.metadata["status"] == "error"
        assert result.metadata["error"] == "plan_required"


class TestEndAspect:
    """Tests for end aspect."""

    @pytest.mark.asyncio
    async def test_end_no_session(self, observer: MockObserver, clean_session):
        """Test ending when no session active."""
        node = SessionNode()
        result = await node._end(observer)

        assert result.metadata["status"] == "error"
        assert result.metadata["error"] == "no_session"

    @pytest.mark.asyncio
    async def test_end_session(
        self,
        observer: MockObserver,
        active_session: ActiveSession,
        temp_sessions_dir: Path,
    ):
        """Test ending an active session."""
        # Add a gesture first
        active_session.add_gesture(
            Gesture(
                type=GestureType.CODE,
                plan="test-plan",
                summary="Test change",
            )
        )

        node = SessionNode()

        # Mock persistence
        with patch(
            "protocols.garden.session._ensure_sessions_dir",
            return_value=temp_sessions_dir,
        ):
            with patch(
                "protocols.garden.session._get_sessions_dir",
                return_value=temp_sessions_dir,
            ):
                with patch(
                    "protocols.garden.session.propagate_session_to_plans",
                    new_callable=AsyncMock,
                ) as mock_prop:
                    mock_prop.return_value = ["test-plan"]

                    result = await node._end(observer, letter="Test letter")

        assert result.metadata["status"] == "ended"
        assert result.metadata["gesture_count"] == 1
        assert result.metadata["letter_written"] is True

        # Session should be cleared
        assert get_active_session() is None


# =============================================================================
# Test Integration
# =============================================================================


class TestIntegration:
    """Integration tests for session lifecycle."""

    @pytest.mark.asyncio
    async def test_full_session_lifecycle(
        self, observer: MockObserver, clean_session, temp_sessions_dir: Path
    ):
        """Test a complete session lifecycle."""
        node = SessionNode()

        # 1. Begin session
        result = await node._begin(observer, gardener="test", period="morning")
        assert result.metadata["status"] == "started"

        # 2. Record some gestures
        for i in range(3):
            await node._gesture(
                observer,
                type="code",
                plan="test-plan",
                summary=f"Change {i}",
            )

        # 3. Check manifest
        result = await node._manifest_impl(observer)
        assert result.metadata["gesture_count"] == 3

        # 4. End session
        with patch(
            "protocols.garden.session._ensure_sessions_dir",
            return_value=temp_sessions_dir,
        ):
            with patch(
                "protocols.garden.session._get_sessions_dir",
                return_value=temp_sessions_dir,
            ):
                with patch(
                    "protocols.garden.session.propagate_session_to_plans",
                    new_callable=AsyncMock,
                ) as mock_prop:
                    mock_prop.return_value = []
                    result = await node._end(observer, letter="Good session")

        assert result.metadata["status"] == "ended"
        assert result.metadata["gesture_count"] == 3

    @pytest.mark.asyncio
    async def test_node_in_registry(self):
        """Test that SessionNode is registered."""
        from protocols.agentese.gateway import _import_node_modules
        from protocols.agentese.registry import get_registry

        _import_node_modules()
        registry = get_registry()
        paths = registry.list_paths()

        assert "self.forest.session" in paths


# =============================================================================
# Test Session → Plan Propagation
# =============================================================================


class TestPlanPropagation:
    """Tests for session to plan propagation."""

    @pytest.mark.asyncio
    async def test_propagation_updates_last_gardened(
        self, active_session: ActiveSession
    ):
        """Test that propagation updates plan's last_gardened."""
        active_session.add_gesture(
            Gesture(
                type=GestureType.CODE,
                plan="test-plan",
                summary="Test",
            )
        )

        # Mock load_plan and save_plan
        from protocols.garden.types import (
            EntropyBudget,
            GardenPlanHeader,
            Mood,
            Season,
            Trajectory,
        )

        mock_plan = GardenPlanHeader(
            path="self.forest.plan.test-plan",
            mood=Mood.FOCUSED,
            momentum=0.5,
            trajectory=Trajectory.CRUISING,
            season=Season.BLOOMING,
            last_gardened=date(2020, 1, 1),  # Old date
            gardener="old-gardener",
            letter="",
        )

        with patch(
            "protocols.garden.session.load_plan", new_callable=AsyncMock
        ) as mock_load:
            with patch(
                "protocols.garden.session.save_plan", new_callable=AsyncMock
            ) as mock_save:
                mock_load.return_value = mock_plan
                mock_save.return_value = True

                updated = await propagate_session_to_plans(
                    active_session, "Test letter"
                )

                assert "test-plan" in updated
                assert mock_plan.last_gardened == date.today()
                assert mock_plan.gardener == "test-gardener"
