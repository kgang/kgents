"""Tests for conflict detection and resolution agents"""

import pytest
from zen_agents.types import SessionConfig, SessionType, SessionState, Session
from zen_agents.conflicts import (
    SessionContradict,
    SessionSublate,
    SessionConflictPipeline,
    SessionContradictInput,
    SessionSublateInput,
    ConflictType,
    detect_conflicts,
    resolve_conflicts,
)


@pytest.mark.asyncio
class TestSessionContradict:
    async def test_no_conflicts(self, sample_config, empty_ground_state):
        contradict = SessionContradict()
        conflicts = await contradict.invoke(SessionContradictInput(
            config=sample_config,
            ground_state=empty_ground_state,
        ))
        assert len(conflicts) == 0

    async def test_name_collision(self, sample_session, sample_ground_state):
        contradict = SessionContradict()
        # Config with same name as existing session
        config = SessionConfig(
            name=sample_session.config.name,
            session_type=SessionType.SHELL,
        )
        conflicts = await contradict.invoke(SessionContradictInput(
            config=config,
            ground_state=sample_ground_state,
        ))
        assert len(conflicts) > 0
        assert any(c.conflict_type == ConflictType.NAME_COLLISION for c in conflicts)

    async def test_resource_limit(self, sample_config, sample_ground_state):
        # Set max to current count
        sample_ground_state.max_sessions = len(sample_ground_state.sessions)
        contradict = SessionContradict()

        config = SessionConfig(name="new-session", session_type=SessionType.SHELL)
        conflicts = await contradict.invoke(SessionContradictInput(
            config=config,
            ground_state=sample_ground_state,
        ))
        assert len(conflicts) > 0
        assert any(c.conflict_type == ConflictType.RESOURCE_LIMIT for c in conflicts)
        # Resource limit should not be resolvable
        resource_conflict = next(c for c in conflicts if c.conflict_type == ConflictType.RESOURCE_LIMIT)
        assert resource_conflict.resolvable is False


@pytest.mark.asyncio
class TestSessionSublate:
    async def test_resolve_name_collision(self, sample_session, sample_ground_state):
        # First detect the conflict
        contradict = SessionContradict()
        config = SessionConfig(
            name=sample_session.config.name,
            session_type=SessionType.SHELL,
        )
        conflicts = await contradict.invoke(SessionContradictInput(
            config=config,
            ground_state=sample_ground_state,
        ))

        # Now try to resolve
        sublate = SessionSublate()
        name_conflict = next(c for c in conflicts if c.conflict_type == ConflictType.NAME_COLLISION)
        resolution = await sublate.invoke(SessionSublateInput(
            conflict=name_conflict,
            auto_resolve=True,
        ))

        assert resolution.resolved is True
        assert resolution.resolution_type == "renamed"
        assert resolution.result is not None
        assert resolution.result.name != sample_session.config.name

    async def test_cannot_resolve_resource_limit(self, sample_ground_state):
        sample_ground_state.max_sessions = len(sample_ground_state.sessions)
        contradict = SessionContradict()

        config = SessionConfig(name="new-session", session_type=SessionType.SHELL)
        conflicts = await contradict.invoke(SessionContradictInput(
            config=config,
            ground_state=sample_ground_state,
        ))

        sublate = SessionSublate()
        resource_conflict = next(c for c in conflicts if c.conflict_type == ConflictType.RESOURCE_LIMIT)
        resolution = await sublate.invoke(SessionSublateInput(
            conflict=resource_conflict,
            auto_resolve=True,
        ))

        assert resolution.resolved is False
        assert resolution.resolution_type == "held"


@pytest.mark.asyncio
class TestConflictPipeline:
    async def test_pipeline_no_conflicts(self, sample_config, empty_ground_state):
        result = await resolve_conflicts(
            config=sample_config,
            ground_state=empty_ground_state,
        )
        assert result.has_conflicts is False
        assert result.can_proceed is True
        assert result.final_config == sample_config

    async def test_pipeline_resolves_name_collision(self, sample_session, sample_ground_state):
        config = SessionConfig(
            name=sample_session.config.name,
            session_type=SessionType.SHELL,
        )
        result = await resolve_conflicts(
            config=config,
            ground_state=sample_ground_state,
            auto_resolve=True,
        )
        assert result.has_conflicts is True
        assert result.can_proceed is True
        assert result.final_config is not None
        assert result.final_config.name != sample_session.config.name
