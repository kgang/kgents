"""
Tests for SoulSession N-Phase Bridge (Wave 4, Task 4.3).

Verifies:
- SoulSession accepts optional nphase_session parameter
- nphase_session property getter/setter work
- get_nphase_context() returns correct info
- advance_nphase() transitions phases correctly

See: plans/nphase-native-integration-wave4-prompt.md
"""

from __future__ import annotations

from pathlib import Path

import pytest
from agents.k.session import SoulHistory, SoulPersistence, SoulSession
from agents.k.soul import KgentSoul
from protocols.nphase.operad import NPhase
from protocols.nphase.session import NPhaseSession, create_session, reset_session_store

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def nphase_session() -> NPhaseSession:
    """Create an N-Phase session for testing."""
    reset_session_store()
    return create_session("K-gent Test Session")


@pytest.fixture
def soul_session(tmp_path: Path) -> SoulSession:
    """Create a SoulSession for testing."""
    soul = KgentSoul()
    persistence = SoulPersistence(tmp_path)
    history = persistence.load_history()
    return SoulSession(
        soul=soul,
        persistence=persistence,
        history=history,
    )


# =============================================================================
# Basic Integration Tests
# =============================================================================


class TestSoulSessionNPhaseBasics:
    """Test basic N-Phase integration with SoulSession."""

    def test_soul_session_accepts_nphase_session(
        self, tmp_path: Path, nphase_session: NPhaseSession
    ) -> None:
        """SoulSession accepts optional nphase_session parameter."""
        soul = KgentSoul()
        persistence = SoulPersistence(tmp_path)
        history = persistence.load_history()

        session = SoulSession(
            soul=soul,
            persistence=persistence,
            history=history,
            nphase_session=nphase_session,
        )

        assert session.nphase_session is nphase_session

    def test_nphase_session_property_setter(
        self, soul_session: SoulSession, nphase_session: NPhaseSession
    ) -> None:
        """nphase_session property setter works."""
        assert soul_session.nphase_session is None
        soul_session.nphase_session = nphase_session
        assert soul_session.nphase_session is nphase_session

    def test_nphase_session_without_session(self, soul_session: SoulSession) -> None:
        """SoulSession works without N-Phase session."""
        assert soul_session.nphase_session is None
        assert soul_session.get_nphase_context() == {}


# =============================================================================
# Context and Advance Tests
# =============================================================================


class TestNPhaseContext:
    """Test N-Phase context retrieval and advancement."""

    def test_get_nphase_context(
        self, soul_session: SoulSession, nphase_session: NPhaseSession
    ) -> None:
        """get_nphase_context() returns correct info."""
        soul_session.nphase_session = nphase_session

        ctx = soul_session.get_nphase_context()
        assert ctx["session_id"] == nphase_session.id
        assert ctx["current_phase"] == "UNDERSTAND"
        assert ctx["cycle_count"] == 0
        assert "checkpoint_count" in ctx

    def test_advance_nphase_success(
        self, soul_session: SoulSession, nphase_session: NPhaseSession
    ) -> None:
        """advance_nphase() transitions phases correctly."""
        soul_session.nphase_session = nphase_session

        # UNDERSTAND → ACT
        result = soul_session.advance_nphase("ACT")
        assert result is True
        assert nphase_session.current_phase == NPhase.ACT

        # ACT → REFLECT
        result = soul_session.advance_nphase("REFLECT")
        assert result is True
        # mypy doesn't track that advance_nphase() changes current_phase
        assert nphase_session.current_phase == NPhase.REFLECT  # type: ignore[comparison-overlap]

    def test_advance_nphase_with_payload(
        self, soul_session: SoulSession, nphase_session: NPhaseSession
    ) -> None:
        """advance_nphase() includes payload in ledger."""
        soul_session.nphase_session = nphase_session

        result = soul_session.advance_nphase("ACT", payload={"mode": "generative"})
        assert result is True

        # Check ledger has entry with payload
        assert len(nphase_session.ledger) > 0
        latest = nphase_session.ledger[-1]
        assert latest.payload.get("source") == "soul_session"
        assert latest.payload.get("mode") == "generative"

    def test_advance_nphase_invalid_target(
        self, soul_session: SoulSession, nphase_session: NPhaseSession
    ) -> None:
        """advance_nphase() returns False for invalid target."""
        soul_session.nphase_session = nphase_session

        result = soul_session.advance_nphase("INVALID")
        assert result is False

    def test_advance_nphase_same_phase(
        self, soul_session: SoulSession, nphase_session: NPhaseSession
    ) -> None:
        """advance_nphase() returns False when already in target phase."""
        soul_session.nphase_session = nphase_session

        # Already in UNDERSTAND
        result = soul_session.advance_nphase("UNDERSTAND")
        assert result is False

    def test_advance_nphase_without_session(self, soul_session: SoulSession) -> None:
        """advance_nphase() returns False without N-Phase session."""
        result = soul_session.advance_nphase("ACT")
        assert result is False


# =============================================================================
# Load Method Tests
# =============================================================================


class TestLoadWithNPhase:
    """Test SoulSession.load() with N-Phase session."""

    @pytest.mark.asyncio
    async def test_load_with_nphase_session(
        self, tmp_path: Path, nphase_session: NPhaseSession
    ) -> None:
        """SoulSession.load() accepts nphase_session parameter."""
        session = await SoulSession.load(
            soul_dir=tmp_path, nphase_session=nphase_session
        )

        assert session.nphase_session is nphase_session

    @pytest.mark.asyncio
    async def test_load_without_nphase_session(self, tmp_path: Path) -> None:
        """SoulSession.load() works without nphase_session."""
        session = await SoulSession.load(soul_dir=tmp_path)

        assert session.nphase_session is None
