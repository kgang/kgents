"""
Test chat evidence calculation with Bayesian posteriors.

Verifies:
- Evidence delta extraction from tool results
- Confidence computation from Beta posterior
- Tool success/failure tracking
"""

import pytest

from protocols.api.chat import ChatEvidence, EvidenceDelta, _update_evidence


def test_evidence_update_no_tools():
    """Test evidence update with no tools (neutral turn)."""
    # Start with uniform prior
    evidence = ChatEvidence(
        prior_alpha=1.0,
        prior_beta=1.0,
        confidence=0.5,
        tools_succeeded=0,
        tools_failed=0,
    )

    # No tools executed
    delta = EvidenceDelta(
        tools_executed=0,
        tools_succeeded=0,
        confidence_change=0.05,
    )

    updated = _update_evidence(evidence, delta, 0.0)  # confidence param ignored

    # No change in counts
    assert updated.tools_succeeded == 0
    assert updated.tools_failed == 0

    # Posterior still uniform
    assert updated.prior_alpha == 1.0
    assert updated.prior_beta == 1.0

    # Confidence is posterior mean: 1 / (1 + 1) = 0.5
    assert updated.confidence == 0.5


def test_evidence_update_all_success():
    """Test evidence update with all tools succeeding."""
    evidence = ChatEvidence(
        prior_alpha=1.0,
        prior_beta=1.0,
        confidence=0.5,
        tools_succeeded=0,
        tools_failed=0,
    )

    # 3 tools executed, all succeeded
    delta = EvidenceDelta(
        tools_executed=3,
        tools_succeeded=3,
        confidence_change=0.5,
    )

    updated = _update_evidence(evidence, delta, 0.0)

    # Counts updated
    assert updated.tools_succeeded == 3
    assert updated.tools_failed == 0

    # Posterior: Beta(4, 1) = (3+1, 0+1)
    assert updated.prior_alpha == 4.0
    assert updated.prior_beta == 1.0

    # Confidence is posterior mean: 4 / (4 + 1) = 0.8
    assert updated.confidence == 0.8


def test_evidence_update_mixed_results():
    """Test evidence update with mixed tool results."""
    evidence = ChatEvidence(
        prior_alpha=1.0,
        prior_beta=1.0,
        confidence=0.5,
        tools_succeeded=0,
        tools_failed=0,
    )

    # 4 tools executed, 2 succeeded, 2 failed
    delta = EvidenceDelta(
        tools_executed=4,
        tools_succeeded=2,
        confidence_change=0.0,
    )

    updated = _update_evidence(evidence, delta, 0.0)

    # Counts updated
    assert updated.tools_succeeded == 2
    assert updated.tools_failed == 2

    # Posterior: Beta(3, 3) = (2+1, 2+1)
    assert updated.prior_alpha == 3.0
    assert updated.prior_beta == 3.0

    # Confidence is posterior mean: 3 / (3 + 3) = 0.5
    assert updated.confidence == 0.5


def test_evidence_update_all_failure():
    """Test evidence update with all tools failing."""
    evidence = ChatEvidence(
        prior_alpha=1.0,
        prior_beta=1.0,
        confidence=0.5,
        tools_succeeded=0,
        tools_failed=0,
    )

    # 2 tools executed, 0 succeeded (all failed)
    delta = EvidenceDelta(
        tools_executed=2,
        tools_succeeded=0,
        confidence_change=-0.5,
    )

    updated = _update_evidence(evidence, delta, 0.0)

    # Counts updated
    assert updated.tools_succeeded == 0
    assert updated.tools_failed == 2

    # Posterior: Beta(1, 3) = (0+1, 2+1)
    assert updated.prior_alpha == 1.0
    assert updated.prior_beta == 3.0

    # Confidence is posterior mean: 1 / (1 + 3) = 0.25
    assert updated.confidence == 0.25


def test_evidence_accumulation():
    """Test evidence accumulates across multiple turns."""
    evidence = ChatEvidence()  # Start with uniform prior

    # Turn 1: 1 tool, success
    delta1 = EvidenceDelta(tools_executed=1, tools_succeeded=1, confidence_change=0.1)
    evidence = _update_evidence(evidence, delta1, 0.0)

    assert evidence.tools_succeeded == 1
    assert evidence.tools_failed == 0
    assert evidence.prior_alpha == 2.0
    assert evidence.prior_beta == 1.0
    assert evidence.confidence == pytest.approx(2.0 / 3.0)

    # Turn 2: 2 tools, 1 success, 1 failure
    delta2 = EvidenceDelta(tools_executed=2, tools_succeeded=1, confidence_change=0.0)
    evidence = _update_evidence(evidence, delta2, 0.0)

    assert evidence.tools_succeeded == 2
    assert evidence.tools_failed == 1
    assert evidence.prior_alpha == 3.0
    assert evidence.prior_beta == 2.0
    assert evidence.confidence == pytest.approx(3.0 / 5.0)

    # Turn 3: 3 tools, all success
    delta3 = EvidenceDelta(tools_executed=3, tools_succeeded=3, confidence_change=0.3)
    evidence = _update_evidence(evidence, delta3, 0.0)

    assert evidence.tools_succeeded == 5
    assert evidence.tools_failed == 1
    assert evidence.prior_alpha == 6.0
    assert evidence.prior_beta == 2.0
    assert evidence.confidence == pytest.approx(6.0 / 8.0)


def test_evidence_should_stop_threshold():
    """Test should_stop flag when confidence exceeds threshold."""
    evidence = ChatEvidence(
        prior_alpha=1.0,
        prior_beta=1.0,
        confidence=0.5,
    )

    # Add enough successes to reach 0.95+ confidence
    # Need: alpha / (alpha + beta) > 0.95
    # With beta=1: alpha / (alpha + 1) > 0.95
    # alpha > 0.95(alpha + 1) => alpha > 0.95alpha + 0.95 => 0.05alpha > 0.95 => alpha > 19
    delta = EvidenceDelta(tools_executed=19, tools_succeeded=19, confidence_change=0.9)
    updated = _update_evidence(evidence, delta, 0.0)

    assert updated.tools_succeeded == 19
    assert updated.tools_failed == 0
    assert updated.prior_alpha == 20.0
    assert updated.prior_beta == 1.0
    assert updated.confidence == pytest.approx(20.0 / 21.0)
    assert updated.confidence > 0.95
    assert updated.should_stop is True
