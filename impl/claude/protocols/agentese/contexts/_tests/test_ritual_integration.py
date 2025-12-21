"""
Integration tests for Playbook AGENTESE node with real stores.

Tests the self.playbook.* AGENTESE paths using the actual
GrantStore, ScopeStore, and PlaybookStore.

See: protocols/agentese/contexts/self_playbook.py
See: services/witness/playbook.py
"""

from __future__ import annotations

import asyncio

import pytest

from services.witness.grant import (
    Grant,
    GrantStatus,
    get_grant_store,
    reset_grant_store,
)
from services.witness.playbook import get_playbook_store, reset_playbook_store
from services.witness.scope import (
    Budget,
    Scope,
    get_scope_store,
    reset_scope_store,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_stores() -> None:
    """Reset all global stores before each test."""
    reset_grant_store()
    reset_scope_store()
    reset_playbook_store()


@pytest.fixture
def playbook_node():
    """Create a fresh PlaybookNode instance."""
    from protocols.agentese.contexts.self_playbook import PlaybookNode

    return PlaybookNode()


@pytest.fixture
def granted_covenant():
    """Create a granted covenant in the store."""
    store = get_grant_store()
    covenant = Grant.propose(
        permissions=frozenset({"file_read", "file_write"}),
        reason="Test ritual",
    ).grant(granted_by="test")
    store.add(covenant)
    return covenant


@pytest.fixture
def valid_offering():
    """Create a valid offering in the store."""
    store = get_scope_store()
    offering = Scope.create(
        description="Test offering",
        budget=Budget(tokens=10000, operations=100),
    )
    store.add(offering)
    return offering


# =============================================================================
# Begin Playbook Tests
# =============================================================================


class TestBeginPlaybookWithStores:
    """Tests for self.playbook.begin using real stores."""

    def test_begin_with_existing_covenant_and_offering(
        self,
        playbook_node,
        granted_covenant,
        valid_offering,
    ) -> None:
        """Begin ritual with pre-existing Grant and Scope from stores."""
        result = playbook_node._begin_playbook(
            name="Test Playbook",
            grant_id=str(granted_covenant.id),
            scope_id=str(valid_offering.id),
        )

        assert "error" not in result
        assert result["name"] == "Test Playbook"
        assert result["status"] == "ACTIVE"
        assert result["phase"] == "SENSE"
        assert result["grant_id"] == str(granted_covenant.id)
        assert result["scope_id"] == str(valid_offering.id)

    def test_begin_with_ungranted_covenant_fails(
        self,
        playbook_node,
        valid_offering,
    ) -> None:
        """Begin fails if Grant is not GRANTED."""
        # Create a PROPOSED covenant (not granted)
        store = get_grant_store()
        proposed = Grant.propose(
            permissions=frozenset({"read"}),
            reason="Not granted yet",
        )
        store.add(proposed)

        result = playbook_node._begin_playbook(
            name="Test",
            grant_id=str(proposed.id),
            scope_id=str(valid_offering.id),
        )

        assert "error" in result
        assert "not granted" in result["error"]

    def test_begin_creates_ritual_in_store(
        self,
        playbook_node,
        granted_covenant,
        valid_offering,
    ) -> None:
        """Begin adds ritual to PlaybookStore."""
        result = playbook_node._begin_playbook(
            name="Stored Playbook",
            grant_id=str(granted_covenant.id),
            scope_id=str(valid_offering.id),
        )

        assert "error" not in result

        # Verify ritual is in store
        from services.witness.playbook import PlaybookId

        store = get_playbook_store()
        ritual = store.get(PlaybookId(result["id"]))

        assert ritual is not None
        assert ritual.name == "Stored Playbook"

    def test_begin_with_unknown_ids_creates_stubs(self, playbook_node) -> None:
        """Begin creates stub Grant/Scope if not found (for testing)."""
        result = playbook_node._begin_playbook(
            name="Stub Test",
            grant_id="unknown-covenant-123",
            scope_id="unknown-offering-456",
        )

        # Should succeed with auto-created stubs
        assert "error" not in result
        assert result["status"] == "ACTIVE"


# =============================================================================
# Advance Phase Tests
# =============================================================================


class TestAdvancePlaybookWithStores:
    """Tests for self.playbook.advance using real stores."""

    def test_advance_phase_sense_to_act(
        self,
        playbook_node,
        granted_covenant,
        valid_offering,
    ) -> None:
        """Advance from SENSE to ACT phase."""
        # Create ritual
        create_result = playbook_node._begin_playbook(
            name="Advance Test",
            grant_id=str(granted_covenant.id),
            scope_id=str(valid_offering.id),
        )
        playbook_id = create_result["id"]

        # Advance to ACT
        result = playbook_node._advance_playbook(
            playbook_id=playbook_id,
            target_phase="ACT",
        )

        assert "error" not in result
        assert result["from_phase"] == "SENSE"
        assert result["to_phase"] == "ACT"
        assert result["success"] is True

    def test_advance_nonexistent_ritual_fails(self, playbook_node) -> None:
        """Advance fails for unknown ritual ID."""
        result = playbook_node._advance_playbook(
            playbook_id="nonexistent-ritual",
            target_phase="ACT",
        )

        assert "error" in result
        assert "not found" in result["error"]

    def test_advance_invalid_phase_fails(
        self,
        playbook_node,
        granted_covenant,
        valid_offering,
    ) -> None:
        """Advance fails for invalid phase name."""
        create_result = playbook_node._begin_playbook(
            name="Phase Test",
            grant_id=str(granted_covenant.id),
            scope_id=str(valid_offering.id),
        )

        result = playbook_node._advance_playbook(
            playbook_id=create_result["id"],
            target_phase="INVALID_PHASE",
        )

        assert "error" in result
        assert "Invalid phase" in result["error"]


# =============================================================================
# Complete Playbook Tests
# =============================================================================


class TestCompletePlaybookWithStores:
    """Tests for self.playbook.complete using real stores."""

    def test_complete_active_ritual(
        self,
        playbook_node,
        granted_covenant,
        valid_offering,
    ) -> None:
        """Complete an active ritual."""
        create_result = playbook_node._begin_playbook(
            name="Complete Test",
            grant_id=str(granted_covenant.id),
            scope_id=str(valid_offering.id),
        )
        playbook_id = create_result["id"]

        result = playbook_node._complete_playbook(playbook_id=playbook_id)

        assert "error" not in result
        assert result["status"] == "COMPLETE"
        assert result["ended_at"] is not None

    def test_complete_nonexistent_fails(self, playbook_node) -> None:
        """Complete fails for unknown ritual ID."""
        result = playbook_node._complete_playbook(playbook_id="nonexistent")

        assert "error" in result
        assert "not found" in result["error"]


# =============================================================================
# Manifest Tests
# =============================================================================


class TestManifestWithStores:
    """Tests for self.playbook.manifest using real stores."""

    def test_manifest_empty_store(self, playbook_node) -> None:
        """Manifest shows empty state when no rituals exist."""
        result = asyncio.get_event_loop().run_until_complete(
            playbook_node.manifest(None)  # type: ignore[arg-type]
        )

        assert result.metadata["total_playbooks"] == 0
        assert result.metadata["active_count"] == 0
        assert result.metadata["recent"] == []

    def test_manifest_shows_rituals(
        self,
        playbook_node,
        granted_covenant,
        valid_offering,
    ) -> None:
        """Manifest shows active rituals."""
        # Create a ritual
        playbook_node._begin_playbook(
            name="Visible Playbook",
            grant_id=str(granted_covenant.id),
            scope_id=str(valid_offering.id),
        )

        result = asyncio.get_event_loop().run_until_complete(
            playbook_node.manifest(None)  # type: ignore[arg-type]
        )

        assert result.metadata["total_playbooks"] == 1
        assert result.metadata["active_count"] == 1
        assert len(result.metadata["recent"]) == 1
        assert result.metadata["recent"][0]["name"] == "Visible Playbook"


# =============================================================================
# Guard Evaluation Tests
# =============================================================================


class TestGuardEvaluationWithStores:
    """Tests for self.playbook.guard using real stores."""

    def test_evaluate_guard(
        self,
        playbook_node,
        granted_covenant,
        valid_offering,
    ) -> None:
        """Evaluate a guard on a ritual."""
        create_result = playbook_node._begin_playbook(
            name="Guard Test",
            grant_id=str(granted_covenant.id),
            scope_id=str(valid_offering.id),
        )
        playbook_id = create_result["id"]

        result = playbook_node._evaluate_guard(
            playbook_id=playbook_id,
            guard_id="test-guard",
        )

        assert "error" not in result
        assert result["status"] == "evaluated"
        assert result["phase"] == "SENSE"


# =============================================================================
# Full Workflow Tests
# =============================================================================


class TestFullWorkflowWithStores:
    """End-to-end workflow tests."""

    def test_complete_playbook_lifecycle(
        self,
        playbook_node,
        granted_covenant,
        valid_offering,
    ) -> None:
        """Test full ritual lifecycle: begin → advance → complete."""
        # 1. Begin ritual
        begin_result = playbook_node._begin_playbook(
            name="Lifecycle Test",
            grant_id=str(granted_covenant.id),
            scope_id=str(valid_offering.id),
        )
        assert begin_result["phase"] == "SENSE"
        playbook_id = begin_result["id"]

        # 2. Advance to ACT
        act_result = playbook_node._advance_playbook(
            playbook_id=playbook_id,
            target_phase="ACT",
        )
        assert act_result["success"] is True

        # 3. Advance to REFLECT
        reflect_result = playbook_node._advance_playbook(
            playbook_id=playbook_id,
            target_phase="REFLECT",
        )
        assert reflect_result["success"] is True

        # 4. Complete
        complete_result = playbook_node._complete_playbook(playbook_id=playbook_id)
        assert complete_result["status"] == "COMPLETE"

        # 5. Verify in store
        from services.witness.playbook import PlaybookId, PlaybookStatus

        store = get_playbook_store()
        ritual = store.get(PlaybookId(playbook_id))

        assert ritual is not None
        assert ritual.status == PlaybookStatus.COMPLETE
        assert len(ritual.phase_history) == 3  # SENSE → ACT → REFLECT
