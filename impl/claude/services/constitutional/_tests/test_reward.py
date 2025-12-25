"""
Tests for Generalized Constitutional Reward system.

Philosophy:
    "Test every domain. Test every principle. Test composition."

See: services/constitutional/reward.py
"""

from __future__ import annotations

import pytest

from services.constitutional import Domain, Principle, PrincipleScore, constitutional_reward


# =============================================================================
# PrincipleScore Tests (Domain-Agnostic)
# =============================================================================


class TestPrincipleScore:
    """Test PrincipleScore dataclass (domain-agnostic)."""

    def test_default_scores_are_one(self):
        """All principles default to 1.0 (optimistic prior)."""
        score = PrincipleScore()
        assert score.tasteful == 1.0
        assert score.curated == 1.0
        assert score.ethical == 1.0
        assert score.joy_inducing == 1.0
        assert score.composable == 1.0
        assert score.heterarchical == 1.0
        assert score.generative == 1.0

    def test_custom_scores(self):
        """Can set custom scores for each principle."""
        score = PrincipleScore(
            tasteful=0.9,
            curated=0.8,
            ethical=0.7,
            joy_inducing=0.6,
            composable=0.5,
            heterarchical=0.4,
            generative=0.3,
        )
        assert score.tasteful == 0.9
        assert score.curated == 0.8
        assert score.ethical == 0.7
        assert score.joy_inducing == 0.6
        assert score.composable == 0.5
        assert score.heterarchical == 0.4
        assert score.generative == 0.3

    def test_weighted_total_default_weights(self):
        """Weighted total uses default weights."""
        # Default weights: ETHICAL=2.0, COMPOSABLE=1.5, JOY=1.2, others=1.0
        # Sum of weights: 2.0 + 1.5 + 1.2 + 1.0*4 = 8.7
        score = PrincipleScore()  # All 1.0
        total = score.weighted_total()
        assert total == pytest.approx(8.7, abs=0.01)

    def test_to_dict(self):
        """Can serialize to dictionary."""
        score = PrincipleScore(ethical=0.8, composable=0.9)
        result = score.to_dict()
        assert result == {
            "tasteful": 1.0,
            "curated": 1.0,
            "ethical": 0.8,
            "joy_inducing": 1.0,
            "composable": 0.9,
            "heterarchical": 1.0,
            "generative": 1.0,
        }

    def test_from_dict(self):
        """Can deserialize from dictionary."""
        data = {
            "tasteful": 0.9,
            "ethical": 0.8,
            "composable": 0.7,
        }
        score = PrincipleScore.from_dict(data)
        assert score.tasteful == 0.9
        assert score.ethical == 0.8
        assert score.composable == 0.7
        # Missing keys default to 1.0
        assert score.curated == 1.0
        assert score.joy_inducing == 1.0


# =============================================================================
# Domain Enum Tests
# =============================================================================


class TestDomainEnum:
    """Test Domain enumeration."""

    def test_all_four_domains_exist(self):
        """All 4 domains are defined."""
        domains = list(Domain)
        assert len(domains) == 4
        assert Domain.CHAT in domains
        assert Domain.NAVIGATION in domains
        assert Domain.PORTAL in domains
        assert Domain.EDIT in domains

    def test_domain_values(self):
        """Domain enum values are lowercase."""
        assert Domain.CHAT.value == "chat"
        assert Domain.NAVIGATION.value == "navigation"
        assert Domain.PORTAL.value == "portal"
        assert Domain.EDIT.value == "edit"


# =============================================================================
# Chat Domain Tests
# =============================================================================


class TestChatDomain:
    """Test constitutional scoring for chat domain."""

    def test_chat_perfect_turn(self):
        """Perfect chat turn gets all 1.0 scores."""
        from services.chat.evidence import TurnResult

        result = TurnResult(
            response="This is a thoughtful, helpful response!",
            tools=[],
            tools_passed=True,
        )
        context = {"turn_result": result, "has_mutations": False}
        score = constitutional_reward("send_message", context, "chat")

        assert score.tasteful == 1.0
        assert score.curated == 1.0
        assert score.ethical == 1.0
        assert score.joy_inducing == 1.0
        assert score.composable == 1.0
        assert score.heterarchical == 1.0
        assert score.generative == 1.0

    def test_chat_unacknowledged_mutations(self):
        """Unacknowledged mutations lower ethical score."""
        from services.chat.evidence import TurnResult

        result = TurnResult(tools_passed=False)
        context = {"turn_result": result, "has_mutations": True}
        score = constitutional_reward("send_message", context, "chat")

        assert score.ethical == 0.5  # Unacknowledged

    def test_chat_acknowledged_mutations(self):
        """Acknowledged mutations get high but not perfect ethical score."""
        from services.chat.evidence import TurnResult

        result = TurnResult(tools_passed=True)
        context = {"turn_result": result, "has_mutations": True}
        score = constitutional_reward("send_message", context, "chat")

        assert score.ethical == 0.9  # Acknowledged

    def test_chat_too_many_tools(self):
        """Using many tools (> 5) lowers composable score."""
        from services.chat.evidence import TurnResult

        result = TurnResult(
            tools=[{"name": f"tool_{i}"} for i in range(10)],
        )
        context = {"turn_result": result, "has_mutations": False}
        score = constitutional_reward("send_message", context, "chat")

        assert score.composable == 0.5  # 10 tools = 5 over limit

    def test_chat_short_response(self):
        """Short response (< 20 chars) gets lower joy score."""
        from services.chat.evidence import TurnResult

        result = TurnResult(response="OK")  # 2 chars
        context = {"turn_result": result, "has_mutations": False}
        score = constitutional_reward("send_message", context, "chat")

        assert score.joy_inducing == pytest.approx(0.55, abs=0.01)

    def test_chat_empty_response(self):
        """Empty response gets very low joy score."""
        from services.chat.evidence import TurnResult

        result = TurnResult(response="")
        context = {"turn_result": result, "has_mutations": False}
        score = constitutional_reward("send_message", context, "chat")

        assert score.joy_inducing == 0.3


# =============================================================================
# Navigation Domain Tests
# =============================================================================


class TestNavigationDomain:
    """Test constitutional scoring for navigation domain."""

    def test_navigation_derivation(self):
        """Derivation navigation gets perfect generative score."""
        context = {"nav_type": "derivation"}
        score = constitutional_reward("navigate", context, "navigation")

        assert score.generative == 1.0

    def test_navigation_loss_gradient(self):
        """Loss gradient navigation gets perfect ethical score."""
        context = {"nav_type": "loss_gradient"}
        score = constitutional_reward("navigate", context, "navigation")

        assert score.ethical == 1.0

    def test_navigation_sibling(self):
        """Sibling navigation gets high composable score."""
        context = {"nav_type": "sibling"}
        score = constitutional_reward("navigate", context, "navigation")

        assert score.composable == 0.9

    def test_navigation_direct_jump(self):
        """Direct jump is tasteful but slightly less composable."""
        context = {"nav_type": "direct_jump"}
        score = constitutional_reward("navigate", context, "navigation")

        assert score.tasteful == 1.0
        assert score.composable == 0.8

    def test_navigation_unknown_type(self):
        """Unknown nav type gets default scores."""
        context = {"nav_type": "unknown"}
        score = constitutional_reward("navigate", context, "navigation")

        # All default to 1.0
        assert score.tasteful == 1.0
        assert score.ethical == 1.0
        assert score.composable == 1.0


# =============================================================================
# Portal Domain Tests
# =============================================================================


class TestPortalDomain:
    """Test constitutional scoring for portal domain."""

    def test_portal_deep_expansion(self):
        """Deep expansion (depth >= 2) gets perfect joy score."""
        context = {"depth": 3, "edge_type": "", "expansion_count": 1}
        score = constitutional_reward("expand_portal", context, "portal")

        assert score.joy_inducing == 1.0

    def test_portal_shallow_expansion(self):
        """Shallow expansion (depth < 2) gets default joy score."""
        context = {"depth": 1, "edge_type": "", "expansion_count": 1}
        score = constitutional_reward("expand_portal", context, "portal")

        assert score.joy_inducing == 1.0  # Default

    def test_portal_evidence_edge(self):
        """Evidence edge type gets perfect ethical score."""
        context = {"depth": 1, "edge_type": "evidence", "expansion_count": 1}
        score = constitutional_reward("expand_portal", context, "portal")

        assert score.ethical == 1.0

    def test_portal_too_many_expansions(self):
        """Too many expansions (>5) lowers curated score."""
        context = {"depth": 1, "edge_type": "", "expansion_count": 10}
        score = constitutional_reward("expand_portal", context, "portal")

        assert score.curated == 0.7

    def test_portal_few_expansions(self):
        """Few expansions (<=5) gets default curated score."""
        context = {"depth": 1, "edge_type": "", "expansion_count": 3}
        score = constitutional_reward("expand_portal", context, "portal")

        assert score.curated == 1.0  # Default

    def test_portal_combined_rules(self):
        """Multiple portal rules can apply simultaneously."""
        context = {"depth": 3, "edge_type": "evidence", "expansion_count": 2}
        score = constitutional_reward("expand_portal", context, "portal")

        assert score.joy_inducing == 1.0  # Deep expansion
        assert score.ethical == 1.0  # Evidence edge
        assert score.curated == 1.0  # Not too many expansions


# =============================================================================
# Edit Domain Tests
# =============================================================================


class TestEditDomain:
    """Test constitutional scoring for edit domain."""

    def test_edit_small_change(self):
        """Small change (<50 lines) gets perfect tasteful score."""
        context = {"lines_changed": 20, "spec_aligned": False}
        score = constitutional_reward("edit_file", context, "edit")

        assert score.tasteful == 1.0

    def test_edit_medium_change(self):
        """Medium change (50-200 lines) gets default scores."""
        context = {"lines_changed": 100, "spec_aligned": False}
        score = constitutional_reward("edit_file", context, "edit")

        assert score.tasteful == 1.0  # Default
        assert score.curated == 1.0  # Default

    def test_edit_large_change(self):
        """Large change (>200 lines) lowers curated score."""
        context = {"lines_changed": 300, "spec_aligned": False}
        score = constitutional_reward("edit_file", context, "edit")

        assert score.curated == 0.7

    def test_edit_spec_aligned(self):
        """Spec-aligned change gets perfect generative score."""
        context = {"lines_changed": 50, "spec_aligned": True}
        score = constitutional_reward("edit_file", context, "edit")

        assert score.generative == 1.0

    def test_edit_not_spec_aligned(self):
        """Non-spec-aligned change gets default generative score."""
        context = {"lines_changed": 50, "spec_aligned": False}
        score = constitutional_reward("edit_file", context, "edit")

        assert score.generative == 1.0  # Default

    def test_edit_combined_rules(self):
        """Multiple edit rules can apply simultaneously."""
        context = {"lines_changed": 20, "spec_aligned": True}
        score = constitutional_reward("edit_file", context, "edit")

        assert score.tasteful == 1.0  # Small change
        assert score.generative == 1.0  # Spec-aligned


# =============================================================================
# Cross-Domain Integration Tests
# =============================================================================


class TestCrossDomainIntegration:
    """Test integration across all domains."""

    def test_all_domains_use_same_principle_score_type(self):
        """All domains return the same PrincipleScore type."""
        chat_score = constitutional_reward("action", {}, "chat")
        nav_score = constitutional_reward("action", {}, "navigation")
        portal_score = constitutional_reward("action", {}, "portal")
        edit_score = constitutional_reward("action", {}, "edit")

        assert isinstance(chat_score, PrincipleScore)
        assert isinstance(nav_score, PrincipleScore)
        assert isinstance(portal_score, PrincipleScore)
        assert isinstance(edit_score, PrincipleScore)

    def test_all_domains_default_to_perfect_scores(self):
        """All domains default to 1.0 for all principles with empty context."""
        for domain in ["chat", "navigation", "portal", "edit"]:
            score = constitutional_reward("action", {}, domain)
            assert score.tasteful == 1.0
            assert score.curated == 1.0
            assert score.ethical == 1.0
            assert score.joy_inducing == 1.0
            assert score.composable == 1.0
            assert score.heterarchical == 1.0
            assert score.generative == 1.0

    def test_weighted_total_works_for_all_domains(self):
        """Weighted total computation works for all domains."""
        chat_score = constitutional_reward("action", {}, "chat")
        nav_score = constitutional_reward("action", {}, "navigation")
        portal_score = constitutional_reward("action", {}, "portal")
        edit_score = constitutional_reward("action", {}, "edit")

        # All should have same weighted total (all 1.0)
        expected = 8.7  # 2.0 + 1.5 + 1.2 + 1.0*4
        assert chat_score.weighted_total() == pytest.approx(expected, abs=0.01)
        assert nav_score.weighted_total() == pytest.approx(expected, abs=0.01)
        assert portal_score.weighted_total() == pytest.approx(expected, abs=0.01)
        assert edit_score.weighted_total() == pytest.approx(expected, abs=0.01)

    def test_serialization_works_for_all_domains(self):
        """Serialization/deserialization works for all domains."""
        for domain in ["chat", "navigation", "portal", "edit"]:
            original = constitutional_reward("action", {}, domain)
            data = original.to_dict()
            restored = PrincipleScore.from_dict(data)

            assert restored.tasteful == original.tasteful
            assert restored.ethical == original.ethical
            assert restored.composable == original.composable


# =============================================================================
# Backward Compatibility Tests
# =============================================================================


class TestBackwardCompatibility:
    """Test backward compatibility with chat/reward.py."""

    def test_chat_reward_module_imports(self):
        """Can import from services.chat.reward (backward compatibility)."""
        from services.chat.reward import (
            Principle as ChatPrinciple,
            PrincipleScore as ChatPrincipleScore,
            constitutional_reward as chat_constitutional_reward,
        )

        # These should be the same as the generalized versions
        assert ChatPrinciple is Principle
        assert ChatPrincipleScore is PrincipleScore

    def test_chat_reward_function_signature(self):
        """Chat reward function maintains its original signature."""
        from services.chat.evidence import TurnResult
        from services.chat.reward import constitutional_reward as chat_reward

        # Should accept chat-specific arguments
        result = TurnResult(response="Test")
        score = chat_reward("send_message", result, has_mutations=False)

        assert isinstance(score, PrincipleScore)

    def test_chat_reward_produces_same_results(self):
        """Chat reward produces same results as before."""
        from services.chat.evidence import TurnResult
        from services.chat.reward import constitutional_reward as chat_reward

        # Test case from original tests
        result = TurnResult(
            response="This is a thoughtful, helpful response!",
            tools=[],
            tools_passed=True,
        )
        score = chat_reward("send_message", result, has_mutations=False)

        assert score.tasteful == 1.0
        assert score.curated == 1.0
        assert score.ethical == 1.0
        assert score.joy_inducing == 1.0
        assert score.composable == 1.0
        assert score.heterarchical == 1.0
        assert score.generative == 1.0


# =============================================================================
# Principle Enum Tests
# =============================================================================


class TestPrincipleEnum:
    """Test Principle enumeration."""

    def test_all_seven_principles_exist(self):
        """All 7 Constitutional principles are defined."""
        principles = list(Principle)
        assert len(principles) == 7
        assert Principle.TASTEFUL in principles
        assert Principle.CURATED in principles
        assert Principle.ETHICAL in principles
        assert Principle.JOY_INDUCING in principles
        assert Principle.COMPOSABLE in principles
        assert Principle.HETERARCHICAL in principles
        assert Principle.GENERATIVE in principles

    def test_principle_values(self):
        """Principle enum values are lowercase snake_case."""
        assert Principle.TASTEFUL.value == "tasteful"
        assert Principle.CURATED.value == "curated"
        assert Principle.ETHICAL.value == "ethical"
        assert Principle.JOY_INDUCING.value == "joy_inducing"
        assert Principle.COMPOSABLE.value == "composable"
        assert Principle.HETERARCHICAL.value == "heterarchical"
        assert Principle.GENERATIVE.value == "generative"
