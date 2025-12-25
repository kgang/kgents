"""
Tests for LLM Invocation Mark schema.
"""

from datetime import datetime, UTC

import pytest

from ..invocation import StateChange, LLMInvocationMark


def test_state_change_creation():
    """Test creating a state change."""
    change = StateChange(
        entity_type="crystal",
        entity_id="c123",
        change_type="created",
        before_hash=None,
        after_hash="abc123"
    )

    assert change.entity_type == "crystal"
    assert change.change_type == "created"
    assert change.before_hash is None
    assert change.after_hash == "abc123"


def test_state_change_serialization():
    """Test state change to_dict and from_dict."""
    change = StateChange(
        entity_type="kblock",
        entity_id="kb456",
        change_type="updated",
        before_hash="old123",
        after_hash="new456"
    )

    # Serialize
    data = change.to_dict()
    assert data["entity_type"] == "kblock"
    assert data["change_type"] == "updated"

    # Deserialize
    change2 = StateChange.from_dict(data)
    assert change2.entity_type == change.entity_type
    assert change2.before_hash == change.before_hash


def test_llm_invocation_mark_creation():
    """Test creating an LLM invocation mark."""
    mark = LLMInvocationMark(
        id="inv_001",
        action="Generate analysis",
        reasoning="User requested analysis",
        model="claude-opus-4-5",
        prompt_tokens=1000,
        completion_tokens=500,
        latency_ms=2500,
        temperature=0.7,
        system_prompt_hash="hash123",
        user_prompt="Analyze this code",
        response="Here is the analysis...",
        causal_parent_id=None,
        triggered_by="user_input",
        state_changes=(),
        crystals_created=(),
        crystals_modified=(),
        galois_loss=0.1,
        invocation_type="analysis"
    )

    assert mark.id == "inv_001"
    assert mark.action == "Generate analysis"
    assert mark.model == "claude-opus-4-5"
    assert mark.total_tokens == 1500
    assert mark.coherence == 0.9
    assert mark.is_root is True
    assert mark.is_cascade is False


def test_llm_invocation_mark_with_ripples():
    """Test LLM invocation with state changes and crystal modifications."""
    changes = (
        StateChange(
            entity_type="crystal",
            entity_id="c1",
            change_type="created",
            before_hash=None,
            after_hash="hash1"
        ),
        StateChange(
            entity_type="kblock",
            entity_id="kb1",
            change_type="updated",
            before_hash="old",
            after_hash="new"
        ),
    )

    mark = LLMInvocationMark(
        id="inv_002",
        action="Generate code",
        reasoning="Implementation needed",
        model="claude-opus-4-5",
        prompt_tokens=2000,
        completion_tokens=1000,
        latency_ms=5000,
        temperature=0.5,
        system_prompt_hash="hash456",
        user_prompt="Write a function",
        response="def example(): ...",
        causal_parent_id="inv_001",
        triggered_by="cascade",
        state_changes=changes,
        crystals_created=("c1", "c2"),
        crystals_modified=("c3",),
        galois_loss=0.05,
        invocation_type="generation",
        tags=frozenset(["cascade", "high-quality"])
    )

    assert mark.ripple_magnitude == 5  # 2 changes + 2 created + 1 modified
    assert mark.is_cascade is True
    assert mark.is_root is False
    assert len(mark.state_changes) == 2
    assert "cascade" in mark.tags


def test_llm_invocation_mark_serialization():
    """Test invocation mark to_dict and from_dict."""
    changes = (
        StateChange(
            entity_type="mark",
            entity_id="m1",
            change_type="created",
            before_hash=None,
            after_hash="h1"
        ),
    )

    mark = LLMInvocationMark(
        id="inv_003",
        action="Classify intent",
        reasoning="Route user request",
        model="claude-haiku-3",
        prompt_tokens=500,
        completion_tokens=100,
        latency_ms=800,
        temperature=0.0,
        system_prompt_hash="hash789",
        user_prompt="What does the user want?",
        response="User wants analysis",
        causal_parent_id=None,
        triggered_by="agent_decision",
        state_changes=changes,
        crystals_created=(),
        crystals_modified=(),
        galois_loss=0.02,
        invocation_type="classification",
        tags=frozenset(["fast", "routing"])
    )

    # Serialize
    data = mark.to_dict()

    # Verify structure
    assert data["id"] == "inv_003"
    assert data["model"] == "claude-haiku-3"
    assert data["invocation_type"] == "classification"
    assert isinstance(data["state_changes"], list)
    assert isinstance(data["tags"], list)
    assert isinstance(data["timestamp"], str)

    # Deserialize
    mark2 = LLMInvocationMark.from_dict(data)

    assert mark2.id == mark.id
    assert mark2.action == mark.action
    assert mark2.model == mark.model
    assert mark2.total_tokens == mark.total_tokens
    assert mark2.coherence == mark.coherence
    assert len(mark2.state_changes) == len(mark.state_changes)
    assert mark2.tags == mark.tags


def test_llm_invocation_computed_properties():
    """Test computed properties on LLM invocation mark."""
    mark = LLMInvocationMark(
        id="inv_004",
        action="Test",
        reasoning="Test",
        model="test",
        prompt_tokens=1000,
        completion_tokens=500,
        latency_ms=2000,
        temperature=1.0,
        system_prompt_hash="h",
        user_prompt="p",
        response="r",
        causal_parent_id=None,
        triggered_by="user_input",
        state_changes=(),
        crystals_created=("c1", "c2", "c3"),
        crystals_modified=("c4",),
        galois_loss=0.15,
        invocation_type="generation"
    )

    # Total tokens
    assert mark.total_tokens == 1500

    # Tokens per second
    assert mark.tokens_per_second == 250.0  # 500 / 2.0

    # Coherence
    assert mark.coherence == 0.85

    # Ripple magnitude
    assert mark.ripple_magnitude == 4  # 0 changes + 3 created + 1 modified

    # Is root / is cascade
    assert mark.is_root is True
    assert mark.is_cascade is False


def test_llm_invocation_trigger_types():
    """Test different trigger types."""
    triggers = ["user_input", "agent_decision", "scheduled", "cascade"]

    for trigger in triggers:
        mark = LLMInvocationMark(
            id=f"inv_{trigger}",
            action="Test",
            reasoning="Test",
            model="test",
            prompt_tokens=100,
            completion_tokens=50,
            latency_ms=1000,
            temperature=0.5,
            system_prompt_hash="h",
            user_prompt="p",
            response="r",
            causal_parent_id="parent" if trigger == "cascade" else None,
            triggered_by=trigger,
            state_changes=(),
            crystals_created=(),
            crystals_modified=(),
            galois_loss=0.0,
            invocation_type="generation"
        )

        assert mark.triggered_by == trigger


def test_llm_invocation_types():
    """Test different invocation types."""
    types = ["generation", "analysis", "classification", "embedding"]

    for itype in types:
        mark = LLMInvocationMark(
            id=f"inv_{itype}",
            action="Test",
            reasoning="Test",
            model="test",
            prompt_tokens=100,
            completion_tokens=50,
            latency_ms=1000,
            temperature=0.5,
            system_prompt_hash="h",
            user_prompt="p",
            response="r",
            causal_parent_id=None,
            triggered_by="user_input",
            state_changes=(),
            crystals_created=(),
            crystals_modified=(),
            galois_loss=0.0,
            invocation_type=itype
        )

        assert mark.invocation_type == itype
