"""
Tests for CLI Phase 7: TUI Dashboard.

Tests cover:
- Types and data structures
- EventStore (SQLite persistence)
- DashboardController
- Playback/DVR features
- Session management
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from ..types import (
    DashboardEvent,
    EventType,
    AgentStatus,
    AgentEntry,
    ArtifactEntry,
    Session,
    SessionState,
    ThoughtEntry,
    DashboardLayout,
    PlaybackState,
)
from ..event_store import EventStore
from ..dashboard import DashboardController, cmd_dash


# =============================================================================
# Types Tests
# =============================================================================


class TestEventType:
    """Tests for EventType enum."""

    def test_all_event_types_exist(self):
        """Verify all expected event types exist."""
        assert EventType.SESSION_START
        assert EventType.SESSION_END
        assert EventType.AGENT_START
        assert EventType.AGENT_COMPLETE
        assert EventType.AGENT_FAIL
        assert EventType.THOUGHT
        assert EventType.ARTIFACT_CREATE
        assert EventType.SNAPSHOT
        assert EventType.USER_COMMAND

    def test_event_type_values(self):
        """Event type values should be snake_case strings."""
        assert EventType.SESSION_START.value == "session_start"
        assert EventType.AGENT_COMPLETE.value == "agent_complete"


class TestAgentStatus:
    """Tests for AgentStatus enum."""

    def test_all_statuses_exist(self):
        """Verify all expected statuses exist."""
        assert AgentStatus.PENDING
        assert AgentStatus.RUNNING
        assert AgentStatus.COMPLETE
        assert AgentStatus.FAILED
        assert AgentStatus.SKIPPED


class TestSessionState:
    """Tests for SessionState enum."""

    def test_all_states_exist(self):
        """Verify all expected states exist."""
        assert SessionState.LIVE
        assert SessionState.PAUSED
        assert SessionState.REPLAY
        assert SessionState.ENDED


class TestDashboardEvent:
    """Tests for DashboardEvent dataclass."""

    def test_create_event(self):
        """Can create a dashboard event."""
        event = DashboardEvent(
            id="evt_test123",
            timestamp=datetime.now(),
            event_type=EventType.THOUGHT,
            source="parse",
            message="Extracting structure",
            data={"lines": 42},
        )

        assert event.id == "evt_test123"
        assert event.event_type == EventType.THOUGHT
        assert event.source == "parse"
        assert event.data["lines"] == 42

    def test_event_to_dict(self):
        """Event can be serialized to dict."""
        event = DashboardEvent(
            id="evt_test123",
            timestamp=datetime(2025, 1, 1, 12, 0, 0),
            event_type=EventType.THOUGHT,
            source="parse",
            message="Test message",
        )

        d = event.to_dict()
        assert d["id"] == "evt_test123"
        assert d["event_type"] == "thought"
        assert d["timestamp"] == "2025-01-01T12:00:00"

    def test_event_from_dict(self):
        """Event can be deserialized from dict."""
        d = {
            "id": "evt_test123",
            "timestamp": "2025-01-01T12:00:00",
            "event_type": "thought",
            "source": "parse",
            "message": "Test message",
            "data": {"key": "value"},
            "session_id": "sess_abc",
        }

        event = DashboardEvent.from_dict(d)
        assert event.id == "evt_test123"
        assert event.event_type == EventType.THOUGHT
        assert event.data["key"] == "value"

    def test_event_immutability(self):
        """Events should be immutable (frozen dataclass)."""
        event = DashboardEvent(
            id="evt_test",
            timestamp=datetime.now(),
            event_type=EventType.THOUGHT,
            source="test",
            message="test",
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            event.id = "changed"


class TestThoughtEntry:
    """Tests for ThoughtEntry."""

    def test_create_thought(self):
        """Can create a thought entry."""
        thought = ThoughtEntry(
            timestamp=datetime.now(),
            source="parse",
            content="Found 3 functions",
            level="info",
        )

        assert thought.source == "parse"
        assert thought.content == "Found 3 functions"

    def test_render_thought(self):
        """Thought renders correctly."""
        thought = ThoughtEntry(
            timestamp=datetime(2025, 1, 1, 12, 30, 45),
            source="judge",
            content="Checking TASTEFUL",
        )

        rendered = thought.render()
        assert "[12:30:45]" in rendered
        assert "[judge]" in rendered
        assert "Checking TASTEFUL" in rendered

    def test_render_without_timestamp(self):
        """Thought renders without timestamp."""
        thought = ThoughtEntry(
            timestamp=datetime.now(),
            source="parse",
            content="Test",
        )

        rendered = thought.render(show_timestamp=False)
        assert "[parse]" in rendered
        assert "Test" in rendered

    def test_thought_indentation(self):
        """Thought renders with indentation."""
        thought = ThoughtEntry(
            timestamp=datetime.now(),
            source="judge",
            content="Sub-item",
            indent=2,
        )

        rendered = thought.render(show_timestamp=False)
        assert rendered.startswith("    ")  # 2 * 2 spaces


class TestAgentEntry:
    """Tests for AgentEntry."""

    def test_create_agent(self):
        """Can create an agent entry."""
        agent = AgentEntry(
            id="step_parse",
            name="parse",
            genus="P-gent",
        )

        assert agent.id == "step_parse"
        assert agent.status == AgentStatus.PENDING

    def test_agent_render(self):
        """Agent renders with status indicator."""
        agent = AgentEntry(
            id="step_parse",
            name="parse",
            genus="P-gent",
            status=AgentStatus.COMPLETE,
        )

        rendered = agent.render()
        assert "●" in rendered  # Complete symbol
        assert "parse" in rendered
        assert "[done]" in rendered

    def test_agent_status_symbols(self):
        """Each status has correct symbol."""
        symbols = {
            AgentStatus.PENDING: "○",
            AgentStatus.RUNNING: "◐",
            AgentStatus.COMPLETE: "●",
            AgentStatus.FAILED: "✗",
            AgentStatus.SKIPPED: "-",
        }

        for status, symbol in symbols.items():
            agent = AgentEntry(id="test", name="test", genus="test", status=status)
            assert symbol in agent.render()


class TestArtifactEntry:
    """Tests for ArtifactEntry."""

    def test_create_artifact(self):
        """Can create an artifact entry."""
        artifact = ArtifactEntry(
            id="art_123",
            name="output.json",
            path=Path("/tmp/output.json"),
            artifact_type="json",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            size_bytes=1024,
        )

        assert artifact.name == "output.json"
        assert artifact.artifact_type == "json"

    def test_artifact_render(self):
        """Artifact renders correctly."""
        artifact = ArtifactEntry(
            id="art_123",
            name="report.md",
            path=None,
            artifact_type="markdown",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            size_bytes=2048,
        )

        rendered = artifact.render()
        assert "report.md" in rendered
        assert "markdown" in rendered
        assert "2KB" in rendered

    def test_artifact_size_formatting(self):
        """Artifact sizes format correctly."""
        sizes = [
            (100, "100B"),
            (1024, "1KB"),
            (1024 * 1024, "1MB"),
        ]

        for size, expected in sizes:
            artifact = ArtifactEntry(
                id="test",
                name="test",
                path=None,
                artifact_type="test",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                size_bytes=size,
            )
            assert expected in artifact.render()


class TestSession:
    """Tests for Session."""

    def test_create_session(self):
        """Can create a session."""
        session = Session(
            id="sess_test123",
            name="Test Session",
        )

        assert session.id == "sess_test123"
        assert session.state == SessionState.LIVE

    def test_session_to_dict(self):
        """Session can be serialized."""
        session = Session(
            id="sess_test",
            name="Test",
            flow_name="review",
        )

        d = session.to_dict()
        assert d["id"] == "sess_test"
        assert d["flow_name"] == "review"
        assert "events" in d

    def test_session_from_dict(self):
        """Session can be deserialized."""
        d = {
            "id": "sess_test",
            "name": "Test",
            "state": "ended",
            "started_at": "2025-01-01T12:00:00",
            "ended_at": "2025-01-01T12:30:00",
            "events": [],
        }

        session = Session.from_dict(d)
        assert session.id == "sess_test"
        assert session.state == SessionState.ENDED

    def test_session_duration(self):
        """Session duration is calculated correctly."""
        session = Session(
            id="sess_test",
            name="Test",
            started_at=datetime(2025, 1, 1, 12, 0, 0),
            ended_at=datetime(2025, 1, 1, 12, 30, 0),
        )

        assert session.duration_seconds == 1800  # 30 minutes

    def test_add_event_to_session(self):
        """Can add events to session."""
        session = Session(id="sess_test", name="Test")

        event = DashboardEvent(
            id="evt_test",
            timestamp=datetime.now(),
            event_type=EventType.THOUGHT,
            source="test",
            message="test",
        )

        session.add_event(event)
        assert len(session.events) == 1
        assert session.event_count == 1

    def test_get_event_at(self):
        """Can get event at index."""
        session = Session(id="sess_test", name="Test")

        for i in range(5):
            event = DashboardEvent(
                id=f"evt_{i}",
                timestamp=datetime.now(),
                event_type=EventType.THOUGHT,
                source="test",
                message=f"Event {i}",
            )
            session.add_event(event)

        assert session.get_event_at(0).message == "Event 0"
        assert session.get_event_at(4).message == "Event 4"
        assert session.get_event_at(10) is None


class TestDashboardLayout:
    """Tests for DashboardLayout."""

    def test_default_layout(self):
        """Default layout shows all panels."""
        layout = DashboardLayout()

        assert layout.show_agents is True
        assert layout.show_thoughts is True
        assert layout.show_artifacts is True
        assert layout.show_command_bar is True

    def test_custom_layout(self):
        """Can customize layout."""
        layout = DashboardLayout(
            show_artifacts=False,
            agents_width=25,
        )

        assert layout.show_artifacts is False
        assert layout.agents_width == 25


class TestPlaybackState:
    """Tests for PlaybackState."""

    def test_create_playback_state(self):
        """Can create playback state."""
        session = Session(id="sess_test", name="Test")
        for i in range(10):
            session.add_event(
                DashboardEvent(
                    id=f"evt_{i}",
                    timestamp=datetime.now(),
                    event_type=EventType.THOUGHT,
                    source="test",
                    message=f"Event {i}",
                )
            )

        playback = PlaybackState(session=session)

        assert playback.current_index == 0
        assert playback.speed == 1.0
        assert not playback.paused

    def test_playback_progress(self):
        """Playback progress is calculated correctly."""
        session = Session(id="sess_test", name="Test")
        for i in range(10):
            session.add_event(
                DashboardEvent(
                    id=f"evt_{i}",
                    timestamp=datetime.now(),
                    event_type=EventType.THOUGHT,
                    source="test",
                    message=f"Event {i}",
                )
            )

        playback = PlaybackState(session=session)

        assert playback.progress == 0.0

        playback.seek(5)
        assert playback.progress == 0.5

    def test_playback_step_forward(self):
        """Can step forward through playback."""
        session = Session(id="sess_test", name="Test")
        for i in range(3):
            session.add_event(
                DashboardEvent(
                    id=f"evt_{i}",
                    timestamp=datetime.now(),
                    event_type=EventType.THOUGHT,
                    source="test",
                    message=f"Event {i}",
                )
            )

        playback = PlaybackState(session=session)

        event = playback.step_forward()
        assert event.message == "Event 1"
        assert playback.current_index == 1

        event = playback.step_forward()
        assert event.message == "Event 2"

        # At end, returns None
        event = playback.step_forward()
        assert event is None

    def test_playback_step_backward(self):
        """Can step backward through playback."""
        session = Session(id="sess_test", name="Test")
        for i in range(3):
            session.add_event(
                DashboardEvent(
                    id=f"evt_{i}",
                    timestamp=datetime.now(),
                    event_type=EventType.THOUGHT,
                    source="test",
                    message=f"Event {i}",
                )
            )

        playback = PlaybackState(session=session)
        playback.seek(2)

        event = playback.step_backward()
        assert event.message == "Event 1"

        event = playback.step_backward()
        assert event.message == "Event 0"

        # At start, returns None
        event = playback.step_backward()
        assert event is None

    def test_playback_seek_bounds(self):
        """Seek respects bounds."""
        session = Session(id="sess_test", name="Test")
        for i in range(5):
            session.add_event(
                DashboardEvent(
                    id=f"evt_{i}",
                    timestamp=datetime.now(),
                    event_type=EventType.THOUGHT,
                    source="test",
                    message=f"Event {i}",
                )
            )

        playback = PlaybackState(session=session)

        playback.seek(-10)
        assert playback.current_index == 0

        playback.seek(100)
        assert playback.current_index == 4


# =============================================================================
# EventStore Tests
# =============================================================================


class TestEventStore:
    """Tests for EventStore (SQLite persistence)."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create a temporary event store."""
        db_path = tmp_path / "test.db"
        return EventStore(db_path)

    def test_create_store(self, store):
        """Can create an event store."""
        assert store.db_path.exists()

    def test_generate_id(self, store):
        """IDs are generated with prefixes."""
        evt_id = store.generate_id("evt")
        assert evt_id.startswith("evt_")
        assert len(evt_id) == 16  # evt_ + 12 chars

        sess_id = store.generate_id("sess")
        assert sess_id.startswith("sess_")

    def test_create_session(self, store):
        """Can create a session."""
        session = store.create_session(
            name="Test Session",
            flow_name="review",
        )

        assert session.id.startswith("sess_")
        assert session.name == "Test Session"
        assert session.state == SessionState.LIVE
        assert session.flow_name == "review"

    def test_get_session(self, store):
        """Can retrieve a session."""
        created = store.create_session(name="Test")
        retrieved = store.get_session(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test"

    def test_get_session_not_found(self, store):
        """Getting non-existent session returns None."""
        result = store.get_session("sess_notexist")
        assert result is None

    def test_end_session(self, store):
        """Can end a session."""
        session = store.create_session(name="Test")
        store.end_session(session.id)

        retrieved = store.get_session(session.id)
        assert retrieved.state == SessionState.ENDED
        assert retrieved.ended_at is not None

    def test_list_sessions(self, store):
        """Can list sessions."""
        store.create_session(name="Session 1")
        store.create_session(name="Session 2")
        store.create_session(name="Session 3")

        sessions = store.list_sessions()
        assert len(sessions) == 3

    def test_list_sessions_by_state(self, store):
        """Can filter sessions by state."""
        s1 = store.create_session(name="Live 1")
        s2 = store.create_session(name="Live 2")
        s3 = store.create_session(name="Ended")
        store.end_session(s3.id)

        live_sessions = store.list_sessions(state=SessionState.LIVE)
        assert len(live_sessions) == 2

        ended_sessions = store.list_sessions(state=SessionState.ENDED)
        assert len(ended_sessions) == 1

    def test_list_sessions_limit(self, store):
        """Can limit session list."""
        for i in range(10):
            store.create_session(name=f"Session {i}")

        sessions = store.list_sessions(limit=5)
        assert len(sessions) == 5

    def test_delete_session(self, store):
        """Can delete a session."""
        session = store.create_session(name="To Delete")
        store.add_event(
            session.id,
            EventType.THOUGHT,
            "test",
            "Test event",
        )

        result = store.delete_session(session.id)
        assert result is True

        retrieved = store.get_session(session.id)
        assert retrieved is None

    def test_add_event(self, store):
        """Can add events to a session."""
        session = store.create_session(name="Test")

        event = store.add_event(
            session.id,
            EventType.THOUGHT,
            "parse",
            "Extracting structure",
            {"lines": 42},
        )

        assert event.id.startswith("evt_")
        assert event.event_type == EventType.THOUGHT
        assert event.data["lines"] == 42

    def test_get_events(self, store):
        """Can retrieve events for a session."""
        session = store.create_session(name="Test")

        store.add_event(session.id, EventType.THOUGHT, "parse", "Event 1")
        store.add_event(session.id, EventType.THOUGHT, "judge", "Event 2")
        store.add_event(session.id, EventType.AGENT_START, "parse", "Event 3")

        events = store.get_events(session.id)
        # +1 for SESSION_START
        assert len(events) == 4

    def test_get_events_by_type(self, store):
        """Can filter events by type."""
        session = store.create_session(name="Test")

        store.add_event(session.id, EventType.THOUGHT, "parse", "Thought 1")
        store.add_event(session.id, EventType.THOUGHT, "parse", "Thought 2")
        store.add_event(session.id, EventType.AGENT_START, "parse", "Agent start")

        thought_events = store.get_events(session.id, event_type=EventType.THOUGHT)
        assert len(thought_events) == 2

    def test_register_agent(self, store):
        """Can register an agent."""
        session = store.create_session(name="Test")

        agent = store.register_agent(
            session.id,
            "step_parse",
            "parse",
            "P-gent",
        )

        assert agent.id == "step_parse"
        assert agent.status == AgentStatus.PENDING

    def test_update_agent_status(self, store):
        """Can update agent status."""
        session = store.create_session(name="Test")
        store.register_agent(session.id, "step_parse", "parse", "P-gent")

        store.update_agent_status(session.id, "step_parse", AgentStatus.RUNNING)
        store.update_agent_status(session.id, "step_parse", AgentStatus.COMPLETE)

        retrieved = store.get_session(session.id)
        agent = retrieved.agents.get("step_parse")
        assert agent is not None
        assert agent.status == AgentStatus.COMPLETE

    def test_register_artifact(self, store):
        """Can register an artifact."""
        session = store.create_session(name="Test")

        artifact = store.register_artifact(
            session.id,
            "output.json",
            "json",
            size_bytes=1024,
            content_preview='{"result": "success"}',
        )

        assert artifact.name == "output.json"
        assert artifact.size_bytes == 1024

    def test_session_loads_with_events(self, store):
        """Session loads with all events."""
        session = store.create_session(name="Test")
        store.add_event(session.id, EventType.THOUGHT, "parse", "Event 1")
        store.add_event(session.id, EventType.THOUGHT, "parse", "Event 2")

        retrieved = store.get_session(session.id)
        # +1 for SESSION_START
        assert len(retrieved.events) == 3

    def test_session_loads_with_agents(self, store):
        """Session loads with all agents."""
        session = store.create_session(name="Test")
        store.register_agent(session.id, "parse", "parse", "P-gent")
        store.register_agent(session.id, "judge", "judge", "Bootstrap")

        retrieved = store.get_session(session.id)
        assert len(retrieved.agents) == 2

    def test_session_loads_with_artifacts(self, store):
        """Session loads with all artifacts."""
        session = store.create_session(name="Test")
        store.register_artifact(session.id, "output.json", "json")
        store.register_artifact(session.id, "report.md", "markdown")

        retrieved = store.get_session(session.id)
        assert len(retrieved.artifacts) == 2

    def test_cleanup_old_sessions(self, store):
        """Can cleanup old sessions."""
        # Create and end a session
        session = store.create_session(name="Old Session")
        store.end_session(session.id)

        # With 0 retention, should delete it
        deleted = store.cleanup_old_sessions(retention=timedelta(seconds=0))
        assert deleted == 1

        assert store.get_session(session.id) is None

    def test_get_statistics(self, store):
        """Can get store statistics."""
        session = store.create_session(name="Test")
        store.add_event(session.id, EventType.THOUGHT, "test", "Test")
        store.register_agent(session.id, "test", "test", "test")

        stats = store.get_statistics()
        assert stats["total_sessions"] >= 1
        assert stats["live_sessions"] >= 1
        assert stats["total_events"] >= 1


# =============================================================================
# DashboardController Tests
# =============================================================================


class TestDashboardController:
    """Tests for DashboardController."""

    @pytest.fixture
    def controller(self, tmp_path):
        """Create a controller with temporary store."""
        db_path = tmp_path / "test.db"
        store = EventStore(db_path)
        return DashboardController(store)

    def test_create_controller(self, controller):
        """Can create a controller."""
        assert controller.current_session is None
        assert controller.playback is None

    def test_start_session(self, controller):
        """Can start a session."""
        session = controller.start_session(
            name="Test Session",
            flow_name="review",
        )

        assert session is not None
        assert controller.current_session == session
        assert session.state == SessionState.LIVE

    def test_end_session(self, controller):
        """Can end a session."""
        controller.start_session(name="Test")
        controller.end_session()

        assert controller.current_session.state == SessionState.ENDED

    def test_load_session(self, controller):
        """Can load a historical session."""
        # Create and end a session
        session = controller.start_session(name="Historical")
        session_id = session.id
        controller.end_session()

        # Clear current
        controller.current_session = None

        # Load it back
        loaded = controller.load_session(session_id)
        assert loaded is not None
        assert loaded.id == session_id
        assert controller.playback is not None

    def test_add_event(self, controller):
        """Can add events."""
        controller.start_session(name="Test")

        event = controller.add_event(
            EventType.THOUGHT,
            "parse",
            "Extracting structure",
        )

        assert event is not None
        assert len(controller.current_session.events) >= 1

    def test_add_thought(self, controller):
        """Can add thoughts."""
        controller.start_session(name="Test")

        thought = controller.add_thought(
            "parse",
            "Found 3 functions",
        )

        assert thought.content == "Found 3 functions"
        assert len(controller.current_session.thoughts) == 1

    def test_register_agent(self, controller):
        """Can register agents."""
        controller.start_session(name="Test")

        agent = controller.register_agent("step_parse", "parse", "P-gent")

        assert agent.id == "step_parse"
        assert "step_parse" in controller.current_session.agents

    def test_update_agent(self, controller):
        """Can update agent status."""
        controller.start_session(name="Test")
        controller.register_agent("step_parse", "parse", "P-gent")

        controller.update_agent("step_parse", AgentStatus.RUNNING)
        agent = controller.current_session.agents["step_parse"]
        assert agent.status == AgentStatus.RUNNING
        assert agent.started_at is not None

        controller.update_agent("step_parse", AgentStatus.COMPLETE)
        assert agent.status == AgentStatus.COMPLETE
        assert agent.completed_at is not None

    def test_register_artifact(self, controller):
        """Can register artifacts."""
        controller.start_session(name="Test")

        artifact = controller.register_artifact(
            "output.json",
            "json",
            content_preview='{"result": true}',
        )

        assert artifact is not None
        assert artifact.id in controller.current_session.artifacts

    def test_event_callbacks(self, controller):
        """Event callbacks are called."""
        received_events = []

        def callback(event):
            received_events.append(event)

        controller.on_event(callback)
        controller.start_session(name="Test")
        controller.add_event(EventType.THOUGHT, "test", "Test event")

        assert len(received_events) >= 1

    def test_playback_seek(self, controller):
        """Can seek in playback mode."""
        controller.start_session(name="Test")
        for i in range(5):
            controller.add_event(EventType.THOUGHT, "test", f"Event {i}")
        controller.end_session()

        controller.load_session(controller.current_session.id)

        event = controller.seek(3)
        assert controller.playback.current_index == 3

    def test_playback_step(self, controller):
        """Can step through playback."""
        controller.start_session(name="Test")
        for i in range(3):
            controller.add_event(EventType.THOUGHT, "test", f"Event {i}")
        controller.end_session()

        controller.load_session(controller.current_session.id)

        controller.step_forward()
        assert controller.playback.current_index == 1

        controller.step_backward()
        assert controller.playback.current_index == 0

    def test_toggle_pause(self, controller):
        """Can toggle pause."""
        controller.start_session(name="Test")
        controller.add_event(EventType.THOUGHT, "test", "Event")
        controller.end_session()

        controller.load_session(controller.current_session.id)

        is_paused = controller.toggle_pause()
        assert is_paused is True

        is_paused = controller.toggle_pause()
        assert is_paused is False


# =============================================================================
# Command Entry Point Tests
# =============================================================================


class TestCmdDash:
    """Tests for cmd_dash entry point."""

    def test_dash_help(self, capsys):
        """--help shows usage."""
        with pytest.raises(SystemExit) as exc_info:
            cmd_dash(["--help"])
        # argparse exits with 0 on --help
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "TUI Dashboard" in captured.out

    def test_dash_list_empty(self, tmp_path, capsys, monkeypatch):
        """--list with no sessions shows message."""
        # Use temp db
        monkeypatch.chdir(tmp_path)
        result = cmd_dash(["--list"])
        assert result == 0

        captured = capsys.readouterr()
        assert "No sessions" in captured.out or "Available sessions" in captured.out

    def test_dash_replay_not_found(self, tmp_path, capsys, monkeypatch):
        """--replay with invalid session shows error."""
        monkeypatch.chdir(tmp_path)
        result = cmd_dash(["--replay=sess_notexist"])
        assert result == 1

        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_dash_flow_not_found(self, tmp_path, capsys, monkeypatch):
        """--flow with missing file shows error."""
        monkeypatch.chdir(tmp_path)
        result = cmd_dash(["--flow=notexist.yaml"])
        assert result == 1

        captured = capsys.readouterr()
        assert "not found" in captured.out


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for the full TUI system."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create a temporary event store."""
        return EventStore(tmp_path / "test.db")

    def test_full_session_lifecycle(self, store):
        """Test complete session lifecycle."""
        controller = DashboardController(store)

        # Start session
        session = controller.start_session(name="Integration Test")
        assert session.state == SessionState.LIVE

        # Register agents
        controller.register_agent("parse", "parse", "P-gent")
        controller.register_agent("judge", "judge", "Bootstrap")
        controller.register_agent("refine", "refine", "R-gent")

        # Run agents
        controller.update_agent("parse", AgentStatus.RUNNING)
        controller.add_thought("parse", "Extracting structure...")
        controller.add_thought("parse", "Found 3 functions")
        controller.update_agent("parse", AgentStatus.COMPLETE)

        controller.update_agent("judge", AgentStatus.RUNNING)
        controller.add_thought("judge", "Checking TASTEFUL")
        controller.add_thought("judge", "TASTEFUL: PASS", "info")
        controller.update_agent("judge", AgentStatus.COMPLETE)

        controller.update_agent("refine", AgentStatus.SKIPPED)

        # Register artifact
        controller.register_artifact(
            "report.json", "json", content_preview='{"pass": true}'
        )

        # End session
        controller.end_session()

        # Verify persistence
        loaded = store.get_session(session.id)
        assert loaded.state == SessionState.ENDED
        assert len(loaded.agents) == 3
        assert len(loaded.artifacts) == 1
        assert loaded.agents["parse"].status == AgentStatus.COMPLETE
        assert loaded.agents["refine"].status == AgentStatus.SKIPPED

    def test_session_replay(self, store):
        """Test session replay functionality."""
        controller = DashboardController(store)

        # Create a session with events
        session = controller.start_session(name="Replay Test")
        controller.add_event(EventType.THOUGHT, "test", "Event 1")
        controller.add_event(EventType.THOUGHT, "test", "Event 2")
        controller.add_event(EventType.THOUGHT, "test", "Event 3")
        controller.end_session()

        session_id = session.id

        # Create new controller and load session
        controller2 = DashboardController(store)
        loaded = controller2.load_session(session_id)

        assert loaded is not None
        assert controller2.playback is not None

        # Test playback
        assert controller2.playback.current_index == 0

        controller2.step_forward()
        assert controller2.playback.current_index == 1

        controller2.step_forward()
        assert controller2.playback.current_index == 2

        controller2.seek(0)
        assert controller2.playback.current_index == 0

    def test_multiple_sessions(self, store):
        """Test multiple concurrent sessions."""
        # Create multiple sessions
        s1 = store.create_session(name="Session 1")
        s2 = store.create_session(name="Session 2")
        s3 = store.create_session(name="Session 3")

        # Add events to each
        store.add_event(s1.id, EventType.THOUGHT, "test", "S1 Event")
        store.add_event(s2.id, EventType.THOUGHT, "test", "S2 Event")
        store.add_event(s3.id, EventType.THOUGHT, "test", "S3 Event")

        # End some
        store.end_session(s1.id)

        # List
        all_sessions = store.list_sessions()
        assert len(all_sessions) == 3

        live = store.list_sessions(state=SessionState.LIVE)
        assert len(live) == 2

        ended = store.list_sessions(state=SessionState.ENDED)
        assert len(ended) == 1

    def test_cleanup(self, store):
        """Test session cleanup."""
        # Create sessions
        s1 = store.create_session(name="Keep")
        s2 = store.create_session(name="Delete")

        store.end_session(s2.id)

        # Cleanup with 0 retention
        deleted = store.cleanup_old_sessions(retention=timedelta(seconds=0))
        assert deleted == 1

        # s1 should still exist (not ended)
        assert store.get_session(s1.id) is not None
        assert store.get_session(s2.id) is None
