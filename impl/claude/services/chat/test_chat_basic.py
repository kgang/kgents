#!/usr/bin/env python3
"""
Basic test of chat service implementation.

Tests the ChatKBlock pattern with K-Block operations.
"""

from services.chat.session import ChatSession, ChatState, MergeStrategy
from services.chat.evidence import ChatEvidence, BetaPrior, TurnResult
from services.chat.context import WorkingContext, LinearityTag, Turn


def test_session_creation():
    """Test creating a chat session."""
    session = ChatSession.create()
    assert session.id.startswith("session-")
    assert session.state == ChatState.IDLE
    assert session.turn_count == 0
    print("✓ Session creation")


def test_adding_turns():
    """Test adding turns to session."""
    session = ChatSession.create()
    session.add_turn("Hello", "Hi there!")
    session.add_turn("How are you?", "I am doing well.")
    assert session.turn_count == 2
    print("✓ Adding turns")


def test_content_hash():
    """Test content hashing for equivalence."""
    session = ChatSession.create()
    session.add_turn("Hello", "Hi there!")
    hash1 = session.content_hash()

    # Same content = same hash
    session2 = ChatSession.create()
    session2.add_turn("Hello", "Hi there!")
    hash2 = session2.content_hash()

    assert hash1 == hash2
    print("✓ Content hashing")


def test_bayesian_evidence():
    """Test Bayesian evidence accumulation."""
    # Start with uniform prior
    prior = BetaPrior(1, 1)
    assert prior.mean() == 0.5

    # Update with success
    updated = prior.update(success=True)
    assert updated.alpha == 2
    assert updated.beta == 1
    assert updated.mean() > 0.5

    # Update with failure
    updated2 = updated.update(success=False)
    assert updated2.alpha == 2
    assert updated2.beta == 2
    assert updated2.mean() == 0.5

    print("✓ Bayesian evidence")


def test_chat_evidence():
    """Test ChatEvidence."""
    evidence = ChatEvidence()
    assert evidence.confidence == 0.5  # Uniform prior

    # Update with successful turn
    turn_result = TurnResult(tools_passed=True, user_corrected=False)
    updated = evidence.update(turn_result)
    assert updated.confidence > 0.5

    print("✓ Chat evidence")


def test_checkpoint_rewind():
    """Test checkpoint and rewind operations."""
    session = ChatSession.create()
    session.add_turn("Hello", "Hi")
    session.add_turn("How are you?", "Good")
    session.add_turn("Nice!", "Thanks")

    # Checkpoint
    ckpt_id = session.checkpoint()
    assert ckpt_id.startswith("ckpt-")
    assert len(session.checkpoints) == 1

    # Rewind
    rewound = session.rewind(1)
    assert rewound.turn_count == 2

    # Law: rewind(checkpoint(s)) ≡ s (approximately, since we don't restore from checkpoint)
    print("✓ Checkpoint and rewind")


def test_fork_merge():
    """Test fork and merge operations."""
    session = ChatSession.create()
    session.add_turn("Hello", "Hi")
    session.add_turn("How are you?", "Good")

    # Fork
    left, right = session.fork("explore-branch")
    assert left.id == session.id
    assert right.id != session.id
    assert right.node.branch_name == "explore-branch"
    assert right.turn_count == 2  # Forked from 2-turn session

    # Add to right branch
    right.add_turn("What's 2+2?", "4")

    # Merge
    merged = left.merge(right, MergeStrategy.SEQUENTIAL)
    # left has 2, right has 3 (2 base + 1 new)
    # Sequential merge: left.turns + right.turns = 2 + 3 = 5
    assert merged.turn_count == 5

    print("✓ Fork and merge")


def test_session_equivalence():
    """Test session equivalence relation."""
    session1 = ChatSession.create()
    session1.add_turn("Hello", "Hi")

    session2 = ChatSession.create()
    session2.add_turn("Hello", "Hi")

    # Reflexive
    assert session1.equivalent_to(session1)

    # Should be equivalent (same content)
    assert session1.equivalent_to(session2)

    # Symmetric
    assert session2.equivalent_to(session1)

    print("✓ Session equivalence")


def test_context_compression():
    """Test working context compression."""
    context = WorkingContext()
    assert context.context_usage == 0.0

    # Add turns
    for i in range(10):
        turn = Turn(
            turn_number=i,
            user_message=f"Message {i}",
            assistant_response=f"Response {i}",
        )
        context.turns.append(turn)

    # Check metrics
    assert context.token_count > 0
    assert len(context.turns) == 10

    # Test compression
    compressed = context.compress()
    # Should have fewer or equal turns after compression
    assert len(compressed.turns) <= len(context.turns)

    print("✓ Context compression")


def test_linearity_tags():
    """Test linearity tag priorities."""
    required = LinearityTag.REQUIRED
    preserved = LinearityTag.PRESERVED
    droppable = LinearityTag.DROPPABLE

    assert required.priority > preserved.priority
    assert preserved.priority > droppable.priority

    assert not required.can_drop
    assert not preserved.can_drop
    assert droppable.can_drop

    print("✓ Linearity tags")


def test_serialization():
    """Test to_dict and from_dict."""
    session = ChatSession.create()
    session.add_turn("Hello", "Hi there!")

    # Serialize
    data = session.to_dict()
    assert data["id"] == session.id
    assert len(data["context"]["turns"]) == 1

    # Deserialize
    restored = ChatSession.from_dict(data)
    assert restored.id == session.id
    assert restored.turn_count == 1
    assert restored.equivalent_to(session)

    print("✓ Serialization")


if __name__ == "__main__":
    print("Testing Chat Service Implementation")
    print("=" * 50)

    test_session_creation()
    test_adding_turns()
    test_content_hash()
    test_bayesian_evidence()
    test_chat_evidence()
    test_checkpoint_rewind()
    test_fork_merge()
    test_session_equivalence()
    test_context_compression()
    test_linearity_tags()
    test_serialization()

    print()
    print("✅ All tests passed!")
