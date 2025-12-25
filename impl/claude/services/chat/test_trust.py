"""
Test suite for trust escalation system.

Tests:
- Trust profile creation and persistence
- Tool trust state progression
- Escalation suggestion logic
- Trust manager API
"""

import tempfile
from pathlib import Path

import pytest

from .trust import TrustEvent, TrustLevel, TrustProfile, ToolTrustState
from .trust_manager import TrustManager, TrustStorage


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_storage_path():
    """Create a temporary directory for trust profiles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def trust_storage(temp_storage_path):
    """Create a trust storage instance."""
    return TrustStorage(base_path=temp_storage_path)


@pytest.fixture
def trust_manager(trust_storage):
    """Create a trust manager instance."""
    return TrustManager(storage=trust_storage)


# =============================================================================
# Trust Profile Tests
# =============================================================================


def test_trust_profile_creation():
    """Test creating a new trust profile."""
    profile = TrustProfile(user_id="test_user")

    assert profile.user_id == "test_user"
    assert len(profile.trusted_tools) == 0
    assert len(profile.trust_history) == 0
    assert profile.default_escalation_threshold == 5


def test_trust_profile_should_gate():
    """Test gating logic."""
    profile = TrustProfile(user_id="test_user")

    # New tool - should gate (ASK level)
    assert profile.should_gate("Edit") is True

    # Escalate to TRUSTED
    profile.escalate_trust("Edit")
    assert profile.should_gate("Edit") is False

    # Revoke trust
    profile.revoke_trust("Edit")
    assert profile.should_gate("Edit") is True

    # Set to NEVER
    profile.set_never_trust("Edit")
    assert profile.should_gate("Edit") is True


def test_trust_profile_record_approval():
    """Test recording approvals."""
    profile = TrustProfile(user_id="test_user")

    # Record 3 approvals
    for i in range(3):
        profile.record_approval("Edit", context=f"Approval {i+1}")

    state = profile.get_tool_state("Edit")
    assert state.approval_count == 3
    assert state.denial_count == 0
    assert len(profile.trust_history) == 3


def test_trust_profile_escalation_suggestion():
    """Test escalation suggestion logic."""
    profile = TrustProfile(user_id="test_user", default_escalation_threshold=3)

    # Before threshold - no suggestion
    profile.record_approval("Edit")
    profile.record_approval("Edit")
    assert profile.should_suggest_escalation("Edit") is False

    # At threshold - suggest
    profile.record_approval("Edit")
    assert profile.should_suggest_escalation("Edit") is True

    # Mark as suggested - don't suggest again
    profile.mark_escalation_suggested("Edit")
    assert profile.should_suggest_escalation("Edit") is False


def test_trust_profile_serialization():
    """Test profile serialization and deserialization."""
    profile = TrustProfile(user_id="test_user")
    profile.record_approval("Edit")
    profile.record_approval("Write")
    profile.escalate_trust("Edit")

    # Serialize
    data = profile.to_dict()
    assert data["user_id"] == "test_user"
    assert len(data["trusted_tools"]) == 2
    assert len(data["trust_history"]) == 3

    # Deserialize
    restored = TrustProfile.from_dict(data)
    assert restored.user_id == profile.user_id
    assert len(restored.trusted_tools) == 2
    assert len(restored.trust_history) == 3
    assert restored.get_tool_state("Edit").level == TrustLevel.TRUSTED


# =============================================================================
# Tool Trust State Tests
# =============================================================================


def test_tool_trust_state_progression():
    """Test trust state progression."""
    state = ToolTrustState(tool_name="Edit", escalation_threshold=3)

    # Initial state
    assert state.level == TrustLevel.ASK
    assert state.approval_count == 0

    # Record approvals
    state.record_approval()
    state.record_approval()
    state.record_approval()
    assert state.approval_count == 3

    # Should suggest escalation
    assert state.should_suggest_escalation() is True

    # Escalate
    state.escalate()
    assert state.level == TrustLevel.TRUSTED
    assert state.escalation_offered is True

    # Shouldn't suggest again
    assert state.should_suggest_escalation() is False


def test_tool_trust_state_never_level():
    """Test NEVER trust level."""
    state = ToolTrustState(tool_name="Bash")

    # Set to NEVER
    state.set_never()
    assert state.level == TrustLevel.NEVER
    assert state.escalation_offered is True

    # Should never suggest escalation
    for _ in range(10):
        state.record_approval()
    assert state.should_suggest_escalation() is False


# =============================================================================
# Trust Storage Tests
# =============================================================================


def test_trust_storage_persistence(trust_storage):
    """Test profile persistence to disk."""
    profile = TrustProfile(user_id="test_user")
    profile.record_approval("Edit")
    profile.escalate_trust("Edit")

    # Save
    trust_storage.save_profile(profile)

    # Clear cache and load
    trust_storage._profiles.clear()
    loaded = trust_storage.load_profile("test_user")

    assert loaded.user_id == "test_user"
    assert loaded.get_tool_state("Edit").level == TrustLevel.TRUSTED


def test_trust_storage_caching(trust_storage):
    """Test in-memory caching."""
    # Load profile (creates new one)
    profile1 = trust_storage.load_profile("test_user")
    profile1.record_approval("Edit")

    # Load again - should get cached version
    profile2 = trust_storage.load_profile("test_user")
    assert profile2 is profile1
    assert profile2.get_tool_state("Edit").approval_count == 1


# =============================================================================
# Trust Manager Tests
# =============================================================================


def test_trust_manager_should_gate(trust_manager):
    """Test gating logic through manager."""
    # New tool - should gate
    assert trust_manager.should_gate("test_user", "Edit") is True

    # Escalate
    trust_manager.escalate_trust("test_user", "Edit")
    assert trust_manager.should_gate("test_user", "Edit") is False

    # Revoke
    trust_manager.revoke_trust("test_user", "Edit")
    assert trust_manager.should_gate("test_user", "Edit") is True


def test_trust_manager_record_approval(trust_manager):
    """Test recording approvals."""
    trust_manager.record_approval("test_user", "Edit", approved=True)
    trust_manager.record_approval("test_user", "Edit", approved=True)
    trust_manager.record_approval("test_user", "Edit", approved=False)

    stats = trust_manager.get_tool_stats("test_user", "Edit")
    assert stats["approval_count"] == 2
    assert stats["denial_count"] == 1


def test_trust_manager_suggest_escalation(trust_manager):
    """Test escalation suggestion."""
    # Record approvals up to threshold
    for _ in range(5):
        trust_manager.record_approval("test_user", "Edit", approved=True)

    # Should suggest
    assert trust_manager.suggest_escalation("test_user", "Edit") is True

    # Mark as suggested
    trust_manager.mark_escalation_suggested("test_user", "Edit")

    # Should not suggest again
    assert trust_manager.suggest_escalation("test_user", "Edit") is False


def test_trust_manager_get_summary(trust_manager):
    """Test getting trust profile summary."""
    # Create some trusted tools
    trust_manager.record_approval("test_user", "Edit", approved=True)
    trust_manager.escalate_trust("test_user", "Edit")

    trust_manager.record_approval("test_user", "Write", approved=True)
    trust_manager.escalate_trust("test_user", "Write")

    trust_manager.record_approval("test_user", "Bash", approved=True)

    # Get summary
    summary = trust_manager.get_trust_summary("test_user")
    assert summary["user_id"] == "test_user"
    assert len(summary["trusted_tools"]) == 2  # Edit and Write
    assert summary["total_tools_used"] == 3  # Edit, Write, Bash


# =============================================================================
# Integration Tests
# =============================================================================


def test_full_trust_escalation_flow(trust_manager):
    """Test complete trust escalation flow."""
    user_id = "test_user"
    tool_name = "Edit"

    # 1. User uses tool for first time - should gate
    assert trust_manager.should_gate(user_id, tool_name) is True

    # 2. Record approvals
    for i in range(5):
        trust_manager.record_approval(
            user_id, tool_name, approved=True, context=f"Edit approval {i+1}"
        )

    # 3. Should suggest escalation
    assert trust_manager.suggest_escalation(user_id, tool_name) is True

    # 4. Mark as suggested (UI shows prompt)
    trust_manager.mark_escalation_suggested(user_id, tool_name)

    # 5. User chooses to trust
    trust_manager.escalate_trust(user_id, tool_name)

    # 6. Tool now auto-approved
    assert trust_manager.should_gate(user_id, tool_name) is False

    # 7. Verify stats
    stats = trust_manager.get_tool_stats(user_id, tool_name)
    assert stats["level"] == "trusted"
    assert stats["approval_count"] == 5

    # 8. User can revoke later
    trust_manager.revoke_trust(user_id, tool_name)
    assert trust_manager.should_gate(user_id, tool_name) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
