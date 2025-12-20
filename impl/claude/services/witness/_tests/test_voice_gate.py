"""
Tests for VoiceGate: Anti-Sausage Runtime Enforcement.

VoiceGate Laws:
- Law 1 (Output Gating): All external outputs should pass VoiceGate
- Law 2 (Denylist Blocking): Corporate-speak patterns block or warn
- Law 3 (Anchor Tracking): Voice anchor references are tracked
- Law 4 (Transformable): Violations can suggest transformations
"""

import pytest

from ..voice_gate import (
    DENYLIST_PATTERNS,
    HEDGE_PATTERNS,
    VOICE_ANCHORS,
    VoiceAction,
    VoiceCheckResult,
    VoiceGate,
    VoiceRule,
    VoiceViolation,
    get_voice_gate,
    reset_voice_gate,
    set_voice_gate,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_global_gate():
    """Reset global voice gate before each test."""
    reset_voice_gate()
    yield
    reset_voice_gate()


@pytest.fixture
def gate() -> VoiceGate:
    """Create a fresh VoiceGate."""
    return VoiceGate()


@pytest.fixture
def strict_gate() -> VoiceGate:
    """Create a strict VoiceGate that blocks."""
    return VoiceGate.strict()


# =============================================================================
# Basic Voice Gate Tests
# =============================================================================


class TestVoiceGateBasics:
    """Test basic VoiceGate functionality."""

    def test_create_default(self, gate: VoiceGate):
        """Default gate has anchors and denylist."""
        assert gate.anchors == VOICE_ANCHORS
        assert gate.denylist == DENYLIST_PATTERNS
        assert gate.hedge_patterns == HEDGE_PATTERNS

    def test_create_strict(self, strict_gate: VoiceGate):
        """Strict gate blocks denylist matches."""
        assert strict_gate.block_denylist is True
        assert strict_gate.block_hedges is True

    def test_create_permissive(self):
        """Permissive gate only warns."""
        gate = VoiceGate.permissive()
        assert gate.block_denylist is False
        assert gate.block_hedges is False

    def test_clean_text_passes(self, gate: VoiceGate):
        """Clean text passes the gate."""
        result = gate.check("This is authentic, opinionated writing.")
        assert result.passed is True
        assert len(result.violations) == 0

    def test_is_clean_convenience(self, gate: VoiceGate):
        """is_clean convenience method works."""
        assert gate.is_clean("Good writing here.")
        # Default gate warns but passes (is_clean = passed, not violation-free)
        # Use strict gate to actually block
        strict = VoiceGate.strict()
        assert not strict.is_clean("We need to leverage this.")


# =============================================================================
# Law 2: Denylist Blocking
# =============================================================================


class TestDenylistBlocking:
    """Test Law 2: Corporate-speak patterns block or warn."""

    def test_leverage_detected(self, gate: VoiceGate):
        """'leverage' is detected as corporate speak."""
        result = gate.check("We need to leverage this opportunity.")
        assert result.has_violations
        assert any("leverage" in v.match.lower() for v in result.violations)

    def test_synergy_detected(self, gate: VoiceGate):
        """'synergy' and 'synergies' are detected as corporate speak."""
        result1 = gate.check("Let's create synergy between teams.")
        result2 = gate.check("Let's leverage synergies between teams.")
        assert result1.has_violations, "synergy not detected"
        assert result2.has_violations, "synergies not detected"
        assert any("synerg" in v.match.lower() for v in result1.violations)

    def test_multiple_violations(self, gate: VoiceGate):
        """Multiple violations are captured."""
        text = "We need to leverage synergies and actionable insights."
        result = gate.check(text)
        # Should catch: leverage, synergy, actionable
        assert len(result.violations) >= 3

    def test_default_gate_warns_not_blocks(self, gate: VoiceGate):
        """Default gate warns but still passes."""
        result = gate.check("Let's leverage this.")
        assert result.passed is True  # Warns, doesn't block
        assert result.has_warnings

    def test_strict_gate_blocks(self, strict_gate: VoiceGate):
        """Strict gate blocks denylist matches."""
        result = strict_gate.check("Let's leverage this.")
        assert result.passed is False  # Blocked
        assert result.blocking_count > 0

    def test_case_insensitive(self, gate: VoiceGate):
        """Pattern matching is case insensitive."""
        result1 = gate.check("LEVERAGE this!")
        result2 = gate.check("Leverage this!")
        result3 = gate.check("leverage this!")
        assert all(r.has_violations for r in [result1, result2, result3])

    def test_has_corporate_speak_convenience(self, gate: VoiceGate):
        """has_corporate_speak convenience method works."""
        assert gate.has_corporate_speak("Let's leverage synergies")
        assert not gate.has_corporate_speak("Let's use good tools")

    @pytest.mark.parametrize(
        "pattern_word",
        [
            "leverage",
            "synergy",  # Will be detected by synergies? pattern
            "synergies",  # Plural form
            "actionable",
            "moving forward",
            "holistic",
            "paradigm shift",
            "drilling down",
            "circle back",
            "low-hanging fruit",
            "best practices",
            "stakeholders",
            "impactful",
            "touch base",
        ],
    )
    def test_all_denylist_patterns_work(self, gate: VoiceGate, pattern_word: str):
        """All denylist patterns are detected."""
        # Note: some patterns need specific phrasing to match word boundaries
        text = f"We need to create {pattern_word} on this project."
        result = gate.check(text)
        assert result.has_violations, f"Pattern '{pattern_word}' not detected"


# =============================================================================
# Hedge Pattern Tests
# =============================================================================


class TestHedgePatterns:
    """Test hedge pattern detection."""

    def test_hedge_detected(self, gate: VoiceGate):
        """Hedging language is detected."""
        result = gate.check("Perhaps this could potentially work.")
        assert result.has_violations
        # Should catch: perhaps, could potentially
        assert any("perhaps" in v.match.lower() for v in result.violations)

    def test_strict_gate_blocks_hedges(self, strict_gate: VoiceGate):
        """Strict gate blocks hedge patterns."""
        result = strict_gate.check("Maybe we should try this.")
        assert result.passed is False

    def test_has_hedging_convenience(self, gate: VoiceGate):
        """has_hedging convenience method works."""
        assert gate.has_hedging("Perhaps we could try")
        assert not gate.has_hedging("Let's try this now")

    @pytest.mark.parametrize(
        "hedge_phrase",
        [
            "perhaps",
            "maybe",
            "could potentially",
            "might be able to",
            "it seems like",
            "one might argue",
        ],
    )
    def test_all_hedge_patterns_work(self, gate: VoiceGate, hedge_phrase: str):
        """All hedge patterns are detected."""
        text = f"I think {hedge_phrase} we should do this."
        result = gate.check(text)
        assert result.has_violations, f"Hedge '{hedge_phrase}' not detected"


# =============================================================================
# Law 3: Anchor Tracking
# =============================================================================


class TestAnchorTracking:
    """Test Law 3: Voice anchor references are tracked."""

    def test_anchor_detected(self, gate: VoiceGate):
        """Voice anchors are detected when referenced."""
        result = gate.check("As we say, 'Tasteful > feature-complete'.")
        assert len(result.anchors_referenced) > 0
        assert "Tasteful > feature-complete" in result.anchors_referenced

    def test_mirror_test_anchor(self, gate: VoiceGate):
        """The Mirror Test anchor is detected."""
        result = gate.check("Does this pass The Mirror Test?")
        assert len(result.anchors_referenced) > 0

    def test_daring_anchor(self, gate: VoiceGate):
        """Daring, bold, creative anchor is detected."""
        result = gate.check("This should be Daring, bold, creative.")
        assert len(result.anchors_referenced) > 0

    def test_references_anchor_convenience(self, gate: VoiceGate):
        """references_anchor convenience method works."""
        anchor = gate.references_anchor("Tasteful > feature-complete is key")
        assert anchor is not None
        assert "Tasteful" in anchor

        no_anchor = gate.references_anchor("Just some random text")
        assert no_anchor is None

    def test_anchor_count_in_result(self, gate: VoiceGate):
        """anchor_count property works."""
        result = gate.check("The Mirror Test and Depth over breadth matter.")
        assert result.anchor_count >= 1

    def test_anchor_tracking_disabled(self):
        """Anchor tracking can be disabled."""
        gate = VoiceGate(track_anchors=False)
        result = gate.check("The Mirror Test is important.")
        assert len(result.anchors_referenced) == 0


# =============================================================================
# Law 4: Transformable
# =============================================================================


class TestTransformable:
    """Test Law 4: Violations can suggest transformations."""

    def test_rule_with_suggestion(self, gate: VoiceGate):
        """Rules can have transformation suggestions."""
        rule = VoiceRule(
            pattern=r"\boptimize\b",
            action=VoiceAction.WARN,
            reason="Vague without context",
            suggestion="Use 'make faster', 'reduce memory', etc.",
        )
        gate.add_rule(rule)

        result = gate.check("We need to optimize this code.")
        assert result.has_violations

        transforms = gate.suggest_transforms("We need to optimize this code.")
        assert len(transforms) > 0
        original, suggestion, reason = transforms[0]
        assert original.lower() == "optimize"
        assert suggestion  # Has suggestion

    def test_no_suggestions_without_rules(self, gate: VoiceGate):
        """No suggestions if rules don't have them."""
        transforms = gate.suggest_transforms("Let's leverage this.")
        # Default denylist rules don't have suggestions
        assert len(transforms) == 0


# =============================================================================
# VoiceRule Tests
# =============================================================================


class TestVoiceRule:
    """Test VoiceRule dataclass."""

    def test_create_rule(self):
        """Rules can be created."""
        rule = VoiceRule(
            pattern=r"\btest\b",
            action=VoiceAction.WARN,
            reason="Test reason",
        )
        assert rule.pattern == r"\btest\b"
        assert rule.action == VoiceAction.WARN

    def test_rule_matches(self):
        """Rules find matches in text."""
        rule = VoiceRule(pattern=r"\bfoo\b", action=VoiceAction.WARN)
        matches = rule.matches("foo bar foo baz")
        assert len(matches) == 2

    def test_rule_no_matches(self):
        """Rules return empty list when no matches."""
        rule = VoiceRule(pattern=r"\bxyz\b", action=VoiceAction.WARN)
        matches = rule.matches("foo bar baz")
        assert len(matches) == 0

    def test_rule_serialization(self):
        """Rules can be serialized and deserialized."""
        rule = VoiceRule(
            pattern=r"\btest\b",
            action=VoiceAction.BLOCK,
            reason="Test reason",
            suggestion="Use 'verify' instead",
            category="custom",
        )
        data = rule.to_dict()
        restored = VoiceRule.from_dict(data)

        assert restored.pattern == rule.pattern
        assert restored.action == rule.action
        assert restored.reason == rule.reason
        assert restored.suggestion == rule.suggestion
        assert restored.category == rule.category


# =============================================================================
# VoiceViolation Tests
# =============================================================================


class TestVoiceViolation:
    """Test VoiceViolation dataclass."""

    def test_violation_properties(self):
        """Violation properties work correctly."""
        rule = VoiceRule(pattern=r"\btest\b", action=VoiceAction.BLOCK)
        violation = VoiceViolation(rule=rule, match="test", context="a test here")

        assert violation.action == VoiceAction.BLOCK
        assert violation.is_blocking is True
        assert violation.is_warning is False

    def test_warning_violation(self):
        """Warning violation properties."""
        rule = VoiceRule(pattern=r"\btest\b", action=VoiceAction.WARN)
        violation = VoiceViolation(rule=rule, match="test")

        assert violation.is_blocking is False
        assert violation.is_warning is True

    def test_violation_serialization(self):
        """Violations can be serialized."""
        rule = VoiceRule(pattern=r"\btest\b", action=VoiceAction.WARN)
        violation = VoiceViolation(rule=rule, match="test", context="the test")
        data = violation.to_dict()

        assert data["match"] == "test"
        assert data["context"] == "the test"


# =============================================================================
# VoiceCheckResult Tests
# =============================================================================


class TestVoiceCheckResult:
    """Test VoiceCheckResult dataclass."""

    def test_passed_result(self):
        """Passed result properties."""
        result = VoiceCheckResult(passed=True)
        assert result.passed is True
        assert result.has_violations is False
        assert result.has_warnings is False

    def test_failed_result(self):
        """Failed result with violations."""
        rule = VoiceRule(pattern=r"\btest\b", action=VoiceAction.BLOCK)
        violation = VoiceViolation(rule=rule, match="test")

        result = VoiceCheckResult(passed=False, violations=(violation,))
        assert result.passed is False
        assert result.has_violations is True
        assert result.blocking_count == 1

    def test_result_serialization(self):
        """Results can be serialized."""
        result = VoiceCheckResult(
            passed=True,
            anchors_referenced=("The Mirror Test",),
        )
        data = result.to_dict()

        assert data["passed"] is True
        assert "The Mirror Test" in data["anchors_referenced"]


# =============================================================================
# Custom Rules
# =============================================================================


class TestCustomRules:
    """Test adding custom rules."""

    def test_add_rule(self, gate: VoiceGate):
        """Custom rules can be added."""
        rule = VoiceRule(
            pattern=r"\bcustom_pattern\b",
            action=VoiceAction.WARN,
            reason="Custom reason",
        )
        gate.add_rule(rule)

        result = gate.check("This has custom_pattern in it.")
        assert result.has_violations

    def test_add_denylist_pattern(self, gate: VoiceGate):
        """Denylist patterns can be added via helper."""
        gate.add_denylist_pattern(r"\bjargon\b", "Custom jargon")

        result = gate.check("Let's avoid jargon here.")
        assert result.has_violations

    def test_with_custom_rules_factory(self):
        """Factory method creates gate with rules."""
        rules = [
            VoiceRule(pattern=r"\bfoo\b", action=VoiceAction.WARN),
            VoiceRule(pattern=r"\bbar\b", action=VoiceAction.BLOCK),
        ]
        gate = VoiceGate.with_custom_rules(rules)

        assert len(gate.rules) == 2


# =============================================================================
# Context Window
# =============================================================================


class TestContextWindow:
    """Test context extraction around matches."""

    def test_context_extracted(self, gate: VoiceGate):
        """Context is extracted around violations."""
        text = "This is some text. We need to leverage more opportunities here."
        result = gate.check(text)

        assert result.has_violations
        # The violation should have context
        violation = result.violations[0]
        assert len(violation.context) > 0
        assert "leverage" in violation.context.lower()

    def test_context_window_configurable(self):
        """Context window size is configurable."""
        gate = VoiceGate(context_window=10)
        text = "x" * 50 + " leverage " + "x" * 50
        result = gate.check(text)

        violation = result.violations[0]
        # Context should be limited
        assert len(violation.context) < len(text)


# =============================================================================
# Statistics
# =============================================================================


class TestStatistics:
    """Test check statistics."""

    def test_stats_tracked(self, gate: VoiceGate):
        """Statistics are tracked."""
        gate.check("Let's leverage this.")
        gate.check("The Mirror Test is key.")
        gate.check("Clean text here.")

        stats = gate.stats
        assert stats["check_count"] == 3
        assert stats["violation_count"] >= 1
        assert stats["anchor_count"] >= 1

    def test_stats_reset(self, gate: VoiceGate):
        """Statistics can be reset."""
        gate.check("Let's leverage synergies.")
        assert gate.stats["check_count"] > 0

        gate.reset_stats()
        assert gate.stats["check_count"] == 0
        assert gate.stats["violation_count"] == 0


# =============================================================================
# Serialization
# =============================================================================


class TestSerialization:
    """Test VoiceGate serialization."""

    def test_to_dict(self, gate: VoiceGate):
        """Gate can be converted to dict."""
        data = gate.to_dict()

        assert "anchors" in data
        assert "denylist" in data
        assert "block_denylist" in data

    def test_from_dict(self, gate: VoiceGate):
        """Gate can be restored from dict."""
        gate.add_rule(VoiceRule(pattern=r"\btest\b", action=VoiceAction.WARN))
        data = gate.to_dict()

        restored = VoiceGate.from_dict(data)
        assert len(restored.rules) == 1
        assert restored.block_denylist == gate.block_denylist

    def test_round_trip(self):
        """Serialization round-trips correctly."""
        gate = VoiceGate.strict()
        gate.add_rule(
            VoiceRule(
                pattern=r"\bcustom\b",
                action=VoiceAction.BLOCK,
                reason="Custom reason",
                suggestion="Avoid this",
            )
        )

        data = gate.to_dict()
        restored = VoiceGate.from_dict(data)

        # Check same behavior
        result1 = gate.check("This is custom and leverage")
        result2 = restored.check("This is custom and leverage")

        assert result1.passed == result2.passed
        assert len(result1.violations) == len(result2.violations)


# =============================================================================
# Global Instance
# =============================================================================


class TestGlobalInstance:
    """Test global voice gate instance."""

    def test_get_global(self):
        """Global gate can be retrieved."""
        gate = get_voice_gate()
        assert isinstance(gate, VoiceGate)

    def test_global_is_singleton(self):
        """Global gate is a singleton."""
        gate1 = get_voice_gate()
        gate2 = get_voice_gate()
        assert gate1 is gate2

    def test_set_global(self):
        """Global gate can be set."""
        custom = VoiceGate.strict()
        set_voice_gate(custom)

        assert get_voice_gate() is custom

    def test_reset_global(self):
        """Global gate can be reset."""
        gate1 = get_voice_gate()
        reset_voice_gate()
        gate2 = get_voice_gate()

        assert gate1 is not gate2


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_text(self, gate: VoiceGate):
        """Empty text passes."""
        result = gate.check("")
        assert result.passed is True

    def test_whitespace_only(self, gate: VoiceGate):
        """Whitespace-only text passes."""
        result = gate.check("   \n\t  ")
        assert result.passed is True

    def test_very_long_text(self, gate: VoiceGate):
        """Very long text is handled."""
        text = "good word " * 10000 + " leverage " + " good word " * 10000
        result = gate.check(text)
        assert result.has_violations

    def test_unicode_text(self, gate: VoiceGate):
        """Unicode text is handled."""
        result = gate.check("Let's leverage some nice text.")
        assert result.has_violations

    def test_special_characters(self, gate: VoiceGate):
        """Special characters don't break patterns."""
        text = "We need to... leverage! This @#$% thing."
        result = gate.check(text)
        assert result.has_violations
