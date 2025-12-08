"""Shared test fixtures for zen-agents.

Provides common fixtures for session models, mocked services, and test utilities.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime
from pathlib import Path
import tempfile
import sys

# Add zen_agents to path for imports
ZEN_AGENTS_ROOT = Path(__file__).parent.parent
if str(ZEN_AGENTS_ROOT) not in sys.path:
    sys.path.insert(0, str(ZEN_AGENTS_ROOT))


# --- Model Fixtures ---

@pytest.fixture
def session_id():
    """Generate a fresh session ID."""
    return uuid4()


@pytest.fixture
def mock_session(session_id):
    """Create a mock session."""
    from zen_agents.models.session import Session, SessionState, SessionType

    return Session(
        id=session_id,
        name="test-session",
        session_type=SessionType.SHELL,
        state=SessionState.RUNNING,
        tmux_name="zen-test-abc123",
        working_dir="/tmp",
        created_at=datetime.now(),
    )


@pytest.fixture
def mock_session_config():
    """Create a mock session config."""
    from zen_agents.models.session import NewSessionConfig, SessionType

    return NewSessionConfig(
        name="test-session",
        session_type=SessionType.SHELL,
        working_dir="/tmp",
    )


@pytest.fixture
def mock_sessions_list():
    """Create a list of mock sessions for conflict testing."""
    from zen_agents.models.session import Session, SessionState, SessionType

    sessions = []
    for i, name in enumerate(["alpha", "beta", "gamma"]):
        sessions.append(Session(
            id=uuid4(),
            name=name,
            session_type=SessionType.SHELL,
            state=SessionState.RUNNING,
            tmux_name=f"zen-{name}-{uuid4().hex[:8]}",
            working_dir=f"/tmp/{name}",
            created_at=datetime.now(),
        ))
    return sessions


# --- ZenConfig Fixture ---

@pytest.fixture
def zen_config():
    """Create a default ZenConfig."""
    from zen_agents.agents.config import ZenConfig

    return ZenConfig(
        poll_interval=0.5,
        grace_period=2.0,
        max_sessions=10,
        scrollback_lines=10000,
        default_shell="/bin/bash",
        tmux_prefix="zen-test",
    )


# --- Mock Service Fixtures ---

@pytest.fixture
def mock_tmux():
    """Mock TmuxService with common responses."""
    tmux = AsyncMock()
    tmux.session_exists.return_value = True
    tmux.is_session_alive.return_value = True
    tmux.create_session.return_value = True
    tmux.kill_session.return_value = True
    tmux.capture_pane.return_value = "test output from tmux"
    tmux.get_exit_code.return_value = 0
    tmux.list_sessions.return_value = ["zen-test-1", "zen-test-2"]
    return tmux


@pytest.fixture
def mock_tmux_dead():
    """Mock TmuxService for dead session scenarios."""
    tmux = AsyncMock()
    tmux.session_exists.return_value = True
    tmux.is_session_alive.return_value = False
    tmux.get_exit_code.return_value = 1
    return tmux


# --- Runtime Mock Fixtures ---

@pytest.fixture
def mock_runtime():
    """Mock ClaudeCLIRuntime for agent orchestrator tests."""
    runtime = AsyncMock()

    # Default mock result with properly structured output
    default_result = MagicMock()
    default_output = MagicMock()

    # Set up all the possible output attributes
    default_output.hypotheses = [
        MagicMock(statement="Test hypothesis 1", falsifiable_by="Test A"),
        MagicMock(statement="Test hypothesis 2", falsifiable_by="Test B"),
    ]
    default_output.suggested_tests = ["Run test A", "Run test B"]
    default_output.reasoning_chain = ["Step 1: observe", "Step 2: analyze"]
    default_output.responses = ["Expanded idea 1", "Expanded idea 2"]
    default_output.follow_ups = ["Follow up 1", "Follow up 2"]
    default_output.response = "This is a thoughtful response."
    default_output.synthesis = "The synthesis of thesis and antithesis"
    default_output.sublation_notes = "Key insights preserved"
    default_output.productive_tension = True
    default_output.next_thesis = "New thesis emerges"
    default_output.preferences = ["preference 1", "preference 2"]
    default_output.patterns = ["pattern 1"]
    default_output.suggested_style = ["be direct", "use examples"]

    default_result.output = default_output

    # Use return_value for simpler mocking
    runtime.execute = AsyncMock(return_value=default_result)
    return runtime


@pytest.fixture
def mock_robin_result():
    """Mock RobinAgent result."""
    result = MagicMock()
    result.synthesis_narrative = "Scientific synthesis narrative"
    result.hypotheses = [
        MagicMock(statement="Hypothesis from Robin"),
    ]
    result.dialectic = {"thesis": "t", "antithesis": "a", "synthesis": "s"}
    result.next_questions = ["What about X?", "Consider Y?"]
    result.personalization = {"style": "exploratory"}
    return result


# --- AgentOrchestrator Fixture ---

@pytest.fixture
def orchestrator(mock_runtime):
    """AgentOrchestrator with mock runtime."""
    from zen_agents.services.agent_orchestrator import AgentOrchestrator

    orch = AgentOrchestrator(runtime=mock_runtime)
    orch._available = True  # Bypass CLI check
    return orch


# --- Persistence Fixtures ---

@pytest.fixture
def temp_sessions_file():
    """Create a temporary file for session persistence tests."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        path = Path(f.name)
    yield path
    # Cleanup
    if path.exists():
        path.unlink()


@pytest.fixture
def persistence(temp_sessions_file):
    """SessionPersistence with temporary file."""
    from zen_agents.services.persistence import SessionPersistence

    return SessionPersistence(sessions_file=temp_sessions_file)


# --- Pipeline Context Fixture ---

@pytest.fixture
def create_context(mock_session_config, zen_config, mock_sessions_list, mock_tmux):
    """Create a CreateContext for pipeline tests."""
    from zen_agents.agents.pipelines.create import CreateContext

    return CreateContext(
        config=mock_session_config,
        zen_config=zen_config,
        existing_sessions=mock_sessions_list,
        tmux=mock_tmux,
    )


# --- Detection Fixtures ---

@pytest.fixture
def detection_state_initial():
    """Initial detection state."""
    from zen_agents.agents.detection import DetectionState

    return DetectionState.initial()


@pytest.fixture
def detection_state_stable():
    """Stable detection state."""
    from zen_agents.agents.detection import DetectionState
    from zen_agents.models.session import SessionState

    return DetectionState(
        session_state=SessionState.RUNNING,
        confidence=0.8,
    )
