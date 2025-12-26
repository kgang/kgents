"""
Tests for ChatPersistence: D-gent-backed session storage.

Tests:
- Session save/load roundtrip
- Turn persistence
- Session listing with filters
- Session deletion
- Crystal save/load
- Checkpoint persistence
- Fork/branch persistence

Testing Strategy:
- Use in-memory SQLite for fast, isolated tests
- Test persistence layer independently from API
- Verify all CRUD operations
- Test edge cases (missing sessions, invalid data)
"""

from datetime import datetime

import pytest

from infra.ground import Ground, InfrastructureConfig, ProviderConfig, XDGPaths
from services.chat import ChatSession
from services.chat.persistence import ChatPersistence


@pytest.fixture
async def persistence():
    """Create ChatPersistence with in-memory SQLite database."""
    import tempfile
    from pathlib import Path

    # Create temp database file (will be deleted after test)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_path = Path(temp_file.name)
    temp_file.close()

    # Create SQLite config with temp database
    config = InfrastructureConfig(
        relational=ProviderConfig(type="sqlite", connection=str(db_path)),
        vector=ProviderConfig(type="memory"),
        blob=ProviderConfig(type="memory"),
        telemetry=ProviderConfig(type="memory"),
    )

    # Create Ground with config
    ground = Ground(
        paths=XDGPaths.resolve(),
        config=config,
        platform="test",
        hostname="test-host",
        pid=1234,
        env={},
    )

    # Create persistence
    persistence = await ChatPersistence.create(ground)

    yield persistence

    # Cleanup
    await persistence.close()

    # Delete temp database
    try:
        db_path.unlink()
    except Exception:
        pass


@pytest.mark.asyncio
async def test_save_and_load_session(persistence: ChatPersistence):
    """Test basic save/load roundtrip."""
    # Create session
    session = ChatSession.create(project_id="test-project", branch_name="main")

    # Add turns
    session.add_turn(
        user_message="Hello, world!", assistant_response="Hi! How can I help you?"
    )
    session.add_turn(
        user_message="What is the weather?",
        assistant_response="I don't have access to weather data.",
    )

    # Save
    await persistence.save_session(session)

    # Load
    loaded = await persistence.load_session(session.id)

    # Verify
    assert loaded is not None
    assert loaded.id == session.id
    assert loaded.project_id == session.project_id
    assert loaded.node.branch_name == session.node.branch_name
    assert loaded.turn_count == 2
    assert len(loaded.turns) == 2
    assert loaded.turns[0].user_message == "Hello, world!"
    assert loaded.turns[1].assistant_response == "I don't have access to weather data."


@pytest.mark.asyncio
async def test_load_nonexistent_session(persistence: ChatPersistence):
    """Test loading a session that doesn't exist."""
    loaded = await persistence.load_session("nonexistent-id")
    assert loaded is None


@pytest.mark.asyncio
async def test_update_session(persistence: ChatPersistence):
    """Test updating an existing session."""
    # Create and save session
    session = ChatSession.create(project_id="test-project")
    await persistence.save_session(session)

    # Add turns
    session.add_turn(user_message="First message", assistant_response="First response")

    # Save again (update)
    await persistence.save_session(session)

    # Load
    loaded = await persistence.load_session(session.id)

    # Verify
    assert loaded is not None
    assert loaded.turn_count == 1
    assert len(loaded.turns) == 1


@pytest.mark.asyncio
async def test_list_sessions(persistence: ChatPersistence):
    """Test listing sessions with filters."""
    # Create multiple sessions
    session1 = ChatSession.create(project_id="project-a", branch_name="main")
    session2 = ChatSession.create(project_id="project-a", branch_name="feature")
    session3 = ChatSession.create(project_id="project-b", branch_name="main")

    await persistence.save_session(session1)
    await persistence.save_session(session2)
    await persistence.save_session(session3)

    # List all
    all_sessions = await persistence.list_sessions()
    assert len(all_sessions) == 3

    # Filter by project
    project_a_sessions = await persistence.list_sessions(project_id="project-a")
    assert len(project_a_sessions) == 2

    # Filter by branch
    main_sessions = await persistence.list_sessions(branch_name="main")
    assert len(main_sessions) == 2

    # Filter by both
    specific_sessions = await persistence.list_sessions(
        project_id="project-a", branch_name="main"
    )
    assert len(specific_sessions) == 1
    assert specific_sessions[0].id == session1.id


@pytest.mark.asyncio
async def test_delete_session(persistence: ChatPersistence):
    """Test session deletion."""
    # Create and save session
    session = ChatSession.create()
    await persistence.save_session(session)

    # Verify exists
    loaded = await persistence.load_session(session.id)
    assert loaded is not None

    # Delete
    deleted = await persistence.delete_session(session.id)
    assert deleted is True

    # Verify deleted
    loaded = await persistence.load_session(session.id)
    assert loaded is None

    # Delete again (should return False)
    deleted = await persistence.delete_session(session.id)
    assert deleted is False


@pytest.mark.asyncio
async def test_save_and_load_crystal(persistence: ChatPersistence):
    """Test crystal save/load."""
    # Create session
    session = ChatSession.create()
    session.add_turn(user_message="Test", assistant_response="Response")
    await persistence.save_session(session)

    # Save crystal
    await persistence.save_crystal(
        session_id=session.id,
        title="Test Session",
        summary="This was a test session",
        key_decisions=["Decision 1", "Decision 2"],
        artifacts=["artifact.txt"],
    )

    # Load crystal
    crystal = await persistence.load_crystal(session.id)

    # Verify
    assert crystal is not None
    assert crystal["session_id"] == session.id
    assert crystal["title"] == "Test Session"
    assert crystal["summary"] == "This was a test session"
    assert crystal["key_decisions"] == ["Decision 1", "Decision 2"]
    assert crystal["artifacts"] == ["artifact.txt"]
    assert crystal["final_turn_count"] == 1


@pytest.mark.asyncio
async def test_load_nonexistent_crystal(persistence: ChatPersistence):
    """Test loading a crystal that doesn't exist."""
    crystal = await persistence.load_crystal("nonexistent-id")
    assert crystal is None


@pytest.mark.asyncio
async def test_save_crystal_for_nonexistent_session(persistence: ChatPersistence):
    """Test saving crystal for session that doesn't exist."""
    with pytest.raises(ValueError, match="Session .* not found"):
        await persistence.save_crystal(
            session_id="nonexistent-id",
            title="Test",
            summary="Test",
        )


@pytest.mark.asyncio
async def test_persist_checkpoints(persistence: ChatPersistence):
    """Test checkpoint persistence."""
    # Create session with checkpoint
    session = ChatSession.create()
    session.add_turn(user_message="Turn 1", assistant_response="Response 1")

    # Create checkpoint
    checkpoint_id = session.checkpoint()

    # Add more turns
    session.add_turn(user_message="Turn 2", assistant_response="Response 2")

    # Save
    await persistence.save_session(session)

    # Load
    loaded = await persistence.load_session(session.id)

    # Verify checkpoint persisted
    assert loaded is not None
    assert len(loaded.checkpoints) == 1
    assert loaded.checkpoints[0]["id"] == checkpoint_id
    assert loaded.checkpoints[0]["turn_count"] == 1


@pytest.mark.asyncio
async def test_persist_fork_metadata(persistence: ChatPersistence):
    """Test fork metadata persistence."""
    # Create parent session
    parent = ChatSession.create(branch_name="main")
    parent.add_turn(user_message="Parent turn", assistant_response="Parent response")
    await persistence.save_session(parent)

    # Fork
    _, child = parent.fork(branch_name="feature-branch")

    # Save child
    await persistence.save_session(child)

    # Load child
    loaded = await persistence.load_session(child.id)

    # Verify fork metadata
    assert loaded is not None
    assert loaded.node.parent_id == parent.id
    assert loaded.node.fork_point == 1
    assert loaded.node.branch_name == "feature-branch"


@pytest.mark.asyncio
async def test_count_sessions(persistence: ChatPersistence):
    """Test session counting."""
    # Create sessions
    session1 = ChatSession.create(project_id="project-a")
    session2 = ChatSession.create(project_id="project-a")
    session3 = ChatSession.create(project_id="project-b")

    await persistence.save_session(session1)
    await persistence.save_session(session2)
    await persistence.save_session(session3)

    # Count all
    total = await persistence.count_sessions()
    assert total == 3

    # Count by project
    count_a = await persistence.count_sessions(project_id="project-a")
    assert count_a == 2

    count_b = await persistence.count_sessions(project_id="project-b")
    assert count_b == 1


@pytest.mark.asyncio
async def test_pagination(persistence: ChatPersistence):
    """Test session listing pagination."""
    # Create many sessions
    for i in range(10):
        session = ChatSession.create(project_id="test-project")
        await persistence.save_session(session)

    # Page 1
    page1 = await persistence.list_sessions(limit=5, offset=0)
    assert len(page1) == 5

    # Page 2
    page2 = await persistence.list_sessions(limit=5, offset=5)
    assert len(page2) == 5

    # Verify no overlap
    page1_ids = {s.id for s in page1}
    page2_ids = {s.id for s in page2}
    assert page1_ids.isdisjoint(page2_ids)


@pytest.mark.asyncio
async def test_session_state_persistence(persistence: ChatPersistence):
    """Test that session state is persisted correctly."""
    from services.chat.session import ChatState

    # Create session
    session = ChatSession.create()
    session.state = ChatState.PROCESSING

    # Save
    await persistence.save_session(session)

    # Load
    loaded = await persistence.load_session(session.id)

    # Verify state
    assert loaded is not None
    assert loaded.state == ChatState.PROCESSING


@pytest.mark.asyncio
async def test_evidence_persistence(persistence: ChatPersistence):
    """Test that evidence is persisted correctly."""
    from services.chat.evidence import BetaPrior

    # Create session with evidence
    session = ChatSession.create()
    # BetaPrior is frozen, so create a new one
    session.evidence.prior = BetaPrior(alpha=5.0, beta=3.0)

    # Save
    await persistence.save_session(session)

    # Load
    loaded = await persistence.load_session(session.id)

    # Verify evidence
    assert loaded is not None
    assert loaded.evidence.prior.alpha == 5.0
    assert loaded.evidence.prior.beta == 3.0


@pytest.mark.asyncio
async def test_cascade_delete_turns(persistence: ChatPersistence):
    """Test that deleting a session cascades to turns."""
    # Enable foreign keys for SQLite (required for CASCADE to work)
    await persistence.storage.relational.execute("PRAGMA foreign_keys = ON")

    # Create session with turns
    session = ChatSession.create()
    session.add_turn(user_message="Test", assistant_response="Response")
    await persistence.save_session(session)

    # Verify turns exist (check database directly)
    turns = await persistence.storage.relational.fetch_all(
        "SELECT * FROM chat_turns WHERE session_id = :session_id",
        {"session_id": session.id},
    )
    assert len(turns) == 1

    # Delete session
    await persistence.delete_session(session.id)

    # Verify turns deleted
    turns = await persistence.storage.relational.fetch_all(
        "SELECT * FROM chat_turns WHERE session_id = :session_id",
        {"session_id": session.id},
    )
    assert len(turns) == 0
