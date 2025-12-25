"""
Example tests for ASHC-Chat integration.

Shows how to use the bridge and integration helpers.

Run:
    uv run pytest services/chat/test_ashc_integration_example.py -v
"""

import pytest

from services.chat.ashc_bridge import ASHCBridge, is_spec_file
from services.chat.ashc_integration import (
    detect_spec_edit_in_message,
    infer_confidence_tier_from_message,
    integrate_ashc_into_chat_evidence,
)
from protocols.ashc.adaptive import ConfidenceTier


# =============================================================================
# Detection Tests
# =============================================================================


def test_detect_explicit_edit_command():
    """Should detect explicit edit commands."""
    message = "Edit spec/agents/new.md: Add @node decorator for registration"

    result = detect_spec_edit_in_message(message)

    assert result is not None
    spec_path, changes = result
    assert spec_path == "spec/agents/new.md"
    assert "Add @node decorator" in changes


def test_detect_file_with_code_block():
    """Should detect file path followed by code block."""
    message = """
    spec/agents/sentiment.md
    ```markdown
    ## New Section
    Add emotion detection
    ```
    """

    result = detect_spec_edit_in_message(message)

    assert result is not None
    spec_path, changes = result
    assert spec_path == "spec/agents/sentiment.md"
    assert "New Section" in changes


def test_detect_no_spec_edit():
    """Should return None for non-spec messages."""
    message = "How do I use ASHC?"

    result = detect_spec_edit_in_message(message)

    assert result is None


# =============================================================================
# Confidence Tier Inference Tests
# =============================================================================


def test_infer_trivially_easy():
    """Should infer TRIVIALLY_EASY from keywords."""
    message = "This is a trivial change to spec/agents/id.md"

    tier = infer_confidence_tier_from_message(message)

    assert tier == ConfidenceTier.TRIVIALLY_EASY


def test_infer_likely_works():
    """Should infer LIKELY_WORKS as default."""
    message = "Edit spec/agents/new.md to add a feature"

    tier = infer_confidence_tier_from_message(message)

    assert tier == ConfidenceTier.LIKELY_WORKS


def test_infer_uncertain():
    """Should infer UNCERTAIN from keywords."""
    message = "I'm not sure if this will work, but let's try editing spec/..."

    tier = infer_confidence_tier_from_message(message)

    assert tier == ConfidenceTier.UNCERTAIN


def test_infer_likely_fails():
    """Should infer LIKELY_FAILS from keywords."""
    message = "This might break things, but edit spec/protocols/zero_seed.md..."

    tier = infer_confidence_tier_from_message(message)

    assert tier == ConfidenceTier.LIKELY_FAILS


# =============================================================================
# Spec File Detection Tests
# =============================================================================


def test_is_spec_file_valid():
    """Should recognize valid spec files."""
    assert is_spec_file("spec/agents/new.md")
    assert is_spec_file("spec/protocols/chat.md")
    assert is_spec_file("spec/services/witness.md")


def test_is_spec_file_invalid():
    """Should reject non-spec files."""
    assert not is_spec_file("impl/claude/agents/k.py")
    assert not is_spec_file("README.md")
    assert not is_spec_file("spec/agents/new.py")  # Wrong extension


# =============================================================================
# Evidence Integration Tests
# =============================================================================


def test_integrate_ashc_verified():
    """Should boost confidence when ASHC verifies."""
    from services.chat.ashc_bridge import ASHCChatOutput

    chat_evidence = {
        "confidence": 0.5,
        "prior_alpha": 1.0,
        "prior_beta": 1.0,
    }

    ashc_output = ASHCChatOutput(
        equivalence_score=0.95,
        is_verified=True,
        runs_completed=10,
        runs_passed=10,
        runs_total=10,
        confidence=0.98,
        prior_alpha=11.0,
        prior_beta=1.0,
        stopping_decision="stop_success",
    )

    result = integrate_ashc_into_chat_evidence(chat_evidence, ashc_output)

    assert result["ashc_equivalence"] == 0.95
    assert result["confidence"] >= 0.9  # Boosted
    assert "ashc_data" in result


def test_integrate_ashc_failed():
    """Should not boost confidence when ASHC fails."""
    from services.chat.ashc_bridge import ASHCChatOutput

    chat_evidence = {
        "confidence": 0.5,
        "prior_alpha": 1.0,
        "prior_beta": 1.0,
    }

    ashc_output = ASHCChatOutput(
        equivalence_score=0.20,
        is_verified=False,
        runs_completed=5,
        runs_passed=1,
        runs_total=5,
        confidence=0.25,
        prior_alpha=2.0,
        prior_beta=5.0,
        stopping_decision="stop_failure",
    )

    result = integrate_ashc_into_chat_evidence(chat_evidence, ashc_output)

    assert result["ashc_equivalence"] == 0.20
    assert result["confidence"] == 0.5  # Not boosted
    assert "ashc_data" in result


# =============================================================================
# ASHCBridge Tests (without actual compilation)
# =============================================================================


@pytest.mark.asyncio
async def test_ashc_bridge_disabled():
    """Should return mock output when compilation disabled."""
    bridge = ASHCBridge(enable_compilation=False)

    output = await bridge.compile_spec(
        spec_path="spec/agents/test.md",
        proposed_changes="Add feature...",
        tier=ConfidenceTier.LIKELY_WORKS,
    )

    assert output.equivalence_score > 0.0
    assert output.runs_completed == 0  # No actual runs
    assert output.stopping_decision == "continue"


@pytest.mark.asyncio
async def test_ashc_bridge_cache():
    """Should cache results for same spec+changes."""
    bridge = ASHCBridge(enable_compilation=False)

    # First call
    output1 = await bridge.compile_spec(
        spec_path="spec/agents/test.md",
        proposed_changes="Add feature...",
    )

    # Second call (should hit cache)
    output2 = await bridge.compile_spec(
        spec_path="spec/agents/test.md",
        proposed_changes="Add feature...",
        use_cache=True,
    )

    # Should be the same object (cached)
    assert output1 == output2


@pytest.mark.asyncio
async def test_ashc_bridge_clear_cache():
    """Should clear cache when requested."""
    bridge = ASHCBridge(enable_compilation=False)

    # Compile and cache
    await bridge.compile_spec(
        spec_path="spec/agents/test.md",
        proposed_changes="Add feature...",
    )

    # Verify cached
    cached = bridge.get_cached_evidence("spec/agents/test.md")
    assert cached is not None

    # Clear cache
    bridge.clear_cache("spec/agents/test.md")

    # Verify cleared
    cached = bridge.get_cached_evidence("spec/agents/test.md")
    assert cached is None


# =============================================================================
# ASHCChatOutput Tests
# =============================================================================


def test_ashc_chat_output_pass_rate():
    """Should calculate pass rate correctly."""
    from services.chat.ashc_bridge import ASHCChatOutput

    output = ASHCChatOutput(
        equivalence_score=0.75,
        is_verified=False,
        runs_completed=8,
        runs_passed=6,
        runs_total=10,
        confidence=0.80,
        prior_alpha=7.0,
        prior_beta=3.0,
        stopping_decision="stop_success",
    )

    assert output.pass_rate == 0.75  # 6/8


def test_ashc_chat_output_to_dict():
    """Should serialize to dict correctly."""
    from services.chat.ashc_bridge import ASHCChatOutput

    output = ASHCChatOutput(
        equivalence_score=0.87,
        is_verified=True,
        runs_completed=10,
        runs_passed=9,
        runs_total=10,
        confidence=0.92,
        prior_alpha=10.0,
        prior_beta=2.0,
        stopping_decision="stop_success",
        chaos_stability=0.95,
    )

    data = output.to_dict()

    assert data["equivalence_score"] == 0.87
    assert data["is_verified"] is True
    assert data["runs_completed"] == 10
    assert data["runs_passed"] == 9
    assert data["pass_rate"] == 0.9
    assert data["confidence"] == 0.92
    assert data["stopping_decision"] == "stop_success"
    assert data["chaos_stability"] == 0.95
