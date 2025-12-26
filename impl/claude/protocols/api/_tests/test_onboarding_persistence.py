"""
Test onboarding session persistence.

Verifies that onboarding sessions are stored in Postgres and survive
server restarts.
"""

from datetime import datetime, timedelta

import pytest

from models import OnboardingSession
from models.base import get_async_session


@pytest.mark.asyncio
async def test_onboarding_session_persistence():
    """Test that onboarding sessions persist to database."""
    # Create a session
    session = OnboardingSession(
        id="test-session-1",
        user_id="test-user",
        current_step="started",
        completed=False,
    )

    async with get_async_session() as db:
        db.add(session)
        await db.commit()

    # Retrieve in new session (simulates server restart)
    async with get_async_session() as db:
        retrieved = await db.get(OnboardingSession, "test-session-1")
        assert retrieved is not None
        assert retrieved.id == "test-session-1"
        assert retrieved.user_id == "test-user"
        assert retrieved.current_step == "started"
        assert retrieved.completed is False
        assert retrieved.created_at is not None

        # Clean up
        await db.delete(retrieved)
        await db.commit()


@pytest.mark.asyncio
async def test_onboarding_session_update():
    """Test updating session with first declaration."""
    # Create a session
    session = OnboardingSession(
        id="test-session-2",
        user_id="test-user",
        current_step="started",
        completed=False,
    )

    async with get_async_session() as db:
        db.add(session)
        await db.commit()

    # Update with first declaration
    async with get_async_session() as db:
        session = await db.get(OnboardingSession, "test-session-2")
        session.first_declaration = "I want to build tasteful agents"
        session.first_kblock_id = "kblock-123"
        session.current_step = "first_declaration"
        session.completed = True
        session.completed_at = datetime.utcnow()
        await db.commit()

    # Verify update persisted
    async with get_async_session() as db:
        retrieved = await db.get(OnboardingSession, "test-session-2")
        assert retrieved.first_declaration == "I want to build tasteful agents"
        assert retrieved.first_kblock_id == "kblock-123"
        assert retrieved.current_step == "first_declaration"
        assert retrieved.completed is True
        assert retrieved.completed_at is not None

        # Clean up
        await db.delete(retrieved)
        await db.commit()


@pytest.mark.asyncio
async def test_onboarding_session_cleanup():
    """Test cleanup of old abandoned sessions."""
    from sqlalchemy import delete, select

    # Create old abandoned session
    old_session = OnboardingSession(
        id="test-session-old",
        user_id="test-user",
        current_step="started",
        completed=False,
    )

    # Create recent session
    recent_session = OnboardingSession(
        id="test-session-recent",
        user_id="test-user",
        current_step="started",
        completed=False,
    )

    # Create completed session (should not be deleted)
    completed_session = OnboardingSession(
        id="test-session-completed",
        user_id="test-user",
        current_step="completed",
        completed=True,
        completed_at=datetime.utcnow(),
    )

    async with get_async_session() as db:
        db.add(old_session)
        db.add(recent_session)
        db.add(completed_session)
        await db.commit()

        # Manually set old session's created_at to 25 hours ago
        old = await db.get(OnboardingSession, "test-session-old")
        old.created_at = datetime.utcnow() - timedelta(hours=25)
        await db.commit()

    # Run cleanup (delete sessions older than 24 hours that aren't completed)
    cutoff_time = datetime.utcnow() - timedelta(hours=24)

    async with get_async_session() as db:
        result = await db.execute(
            delete(OnboardingSession).where(
                OnboardingSession.completed == False,
                OnboardingSession.created_at < cutoff_time,
            )
        )
        await db.commit()
        deleted_count = result.rowcount

    # Verify only old abandoned session was deleted
    assert deleted_count == 1

    async with get_async_session() as db:
        # Old abandoned should be gone
        old = await db.get(OnboardingSession, "test-session-old")
        assert old is None

        # Recent should still exist
        recent = await db.get(OnboardingSession, "test-session-recent")
        assert recent is not None

        # Completed should still exist (not deleted even if old)
        completed = await db.get(OnboardingSession, "test-session-completed")
        assert completed is not None

        # Clean up
        if recent:
            await db.delete(recent)
        if completed:
            await db.delete(completed)
        await db.commit()


@pytest.mark.asyncio
async def test_onboarding_session_query():
    """Test querying for completed sessions."""
    from sqlalchemy import select

    # Create multiple sessions
    sessions = [
        OnboardingSession(
            id=f"test-session-{i}",
            user_id="test-user",
            current_step="completed" if i % 2 == 0 else "started",
            completed=i % 2 == 0,
            completed_at=datetime.utcnow() if i % 2 == 0 else None,
        )
        for i in range(5)
    ]

    async with get_async_session() as db:
        for session in sessions:
            db.add(session)
        await db.commit()

    # Query for completed sessions
    async with get_async_session() as db:
        result = await db.execute(
            select(OnboardingSession).where(OnboardingSession.completed == True)
        )
        completed = result.scalars().all()

        # Should have 3 completed (indices 0, 2, 4)
        assert len(completed) >= 3

        # Clean up
        for session in sessions:
            s = await db.get(OnboardingSession, session.id)
            if s:
                await db.delete(s)
        await db.commit()
