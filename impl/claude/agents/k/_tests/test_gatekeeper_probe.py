"""
Tests for GatekeeperProbe (DP-Native Validation).

Tests the TruthFunctor-based refactor of SemanticGatekeeper.
Verifies:
1. State machine transitions
2. PolicyTrace emission
3. ConstitutionalScore computation
4. Violation detection parity with original
"""

from __future__ import annotations

import pytest

from agents.k.gatekeeper import Principle, Severity, Violation
from agents.k.gatekeeper_probe import (
    GatekeeperProbe,
    ValidationInput,
    ValidationState,
    validate_content_probe,
    validate_file_probe,
    violation_to_score,
)
from agents.t.truth_functor import ConstitutionalScore, ProbeAction

# =============================================================================
# Violation Mapping Tests
# =============================================================================


class TestViolationToScore:
    """Test violation → constitutional score mapping."""

    def test_critical_ethical_violation(self) -> None:
        """Test CRITICAL + ETHICAL → max ethical penalty."""
        violation = Violation(
            principle=Principle.ETHICAL,
            severity=Severity.CRITICAL,
            message="Hardcoded password",
        )
        score = violation_to_score(violation)

        assert score.ethical == -1.0
        assert score.tasteful == 0.0
        assert score.composable == 0.0

    def test_error_composable_violation(self) -> None:
        """Test ERROR + COMPOSABLE → composable penalty."""
        violation = Violation(
            principle=Principle.COMPOSABLE,
            severity=Severity.ERROR,
            message="Singleton detected",
        )
        score = violation_to_score(violation)

        assert score.composable == -0.7
        assert score.ethical == 0.0

    def test_warning_tasteful_violation(self) -> None:
        """Test WARNING + TASTEFUL → small tasteful penalty."""
        violation = Violation(
            principle=Principle.TASTEFUL,
            severity=Severity.WARNING,
            message="Manager class",
        )
        score = violation_to_score(violation)

        assert score.tasteful == -0.4
        assert score.composable == 0.0

    def test_info_joy_violation(self) -> None:
        """Test INFO + JOY → minimal penalty."""
        violation = Violation(
            principle=Principle.JOY_INDUCING,
            severity=Severity.INFO,
            message="Low gratitude",
        )
        score = violation_to_score(violation)

        assert score.joy_inducing == -0.1


# =============================================================================
# State Machine Tests
# =============================================================================


class TestStateMachine:
    """Test probe state transitions."""

    @pytest.fixture
    def probe(self) -> GatekeeperProbe:
        """Create a GatekeeperProbe."""
        return GatekeeperProbe()

    def test_valid_states(self, probe: GatekeeperProbe) -> None:
        """Test all states are defined."""
        assert "init" in probe.states
        assert "heuristic" in probe.states
        assert "semantic" in probe.states
        assert "synthesis" in probe.states
        assert "complete" in probe.states

    def test_init_to_heuristic_transition(self, probe: GatekeeperProbe) -> None:
        """Test init → heuristic transition."""
        state = ValidationState(phase="init")
        action = ProbeAction("start_heuristic")

        next_state = probe.transition(state, action)
        assert next_state.phase == "heuristic"

    def test_heuristic_to_semantic_transition(self, probe: GatekeeperProbe) -> None:
        """Test heuristic → semantic transition."""
        state = ValidationState(phase="heuristic")
        action = ProbeAction("advance_to_semantic")

        next_state = probe.transition(state, action)
        assert next_state.phase == "semantic"

    def test_semantic_stays_semantic(self, probe: GatekeeperProbe) -> None:
        """Test semantic → semantic (analyzing)."""
        state = ValidationState(phase="semantic")
        action = ProbeAction("run_tastefulness")

        next_state = probe.transition(state, action)
        assert next_state.phase == "semantic"

    def test_synthesis_to_complete(self, probe: GatekeeperProbe) -> None:
        """Test synthesis → complete transition."""
        state = ValidationState(phase="synthesis")
        action = ProbeAction("synthesize")

        next_state = probe.transition(state, action)
        assert next_state.phase == "complete"

    def test_complete_has_no_actions(self, probe: GatekeeperProbe) -> None:
        """Test complete state has no valid actions."""
        state = ValidationState(phase="complete")
        actions = probe.actions(state)

        assert len(actions) == 0


# =============================================================================
# Verification Tests
# =============================================================================


class TestVerification:
    """Test full verification flow."""

    @pytest.mark.asyncio
    async def test_clean_code_passes(self) -> None:
        """Test that clean code produces passing trace."""
        content = """
def greet(name: str) -> str:
    \"\"\"Greet user by name.\"\"\"
    return f"Hello, {name}!"

class UserRepository:
    def __init__(self, db):
        self._db = db

    def get(self, user_id: str):
        return self._db.find_one(user_id)
"""
        trace = await validate_content_probe(content, "clean.py")

        assert trace.value.passed
        # May have INFO violations (e.g., low gratitude), but should pass
        critical_or_error = [
            v
            for v in trace.value.value
            if v.severity in [Severity.CRITICAL, Severity.ERROR]
        ]
        assert len(critical_or_error) == 0
        assert len(trace.entries) > 0  # Should have trace entries

    @pytest.mark.asyncio
    async def test_hardcoded_password_fails(self) -> None:
        """Test that hardcoded password is detected."""
        content = """
def connect():
    password = "super_secret_123"
    return db.connect(password)
"""
        trace = await validate_content_probe(content, "bad.py")

        assert not trace.value.passed
        violations = trace.value.value
        assert any(
            v.principle == Principle.ETHICAL and v.severity == Severity.CRITICAL
            for v in violations
        )

    @pytest.mark.asyncio
    async def test_singleton_detected(self) -> None:
        """Test singleton pattern detection."""
        content = """
class DatabaseSingleton:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
"""
        trace = await validate_content_probe(content, "singleton.py")

        violations = trace.value.value
        assert any(v.principle == Principle.COMPOSABLE for v in violations)

    @pytest.mark.asyncio
    async def test_mutable_default_detected(self) -> None:
        """Test mutable default argument detection."""
        content = """
def add_item(item, items=[]):
    items.append(item)
    return items
"""
        trace = await validate_content_probe(content, "mutable.py")

        violations = trace.value.value
        assert any(
            v.principle == Principle.COMPOSABLE and v.severity == Severity.ERROR
            for v in violations
        )

    @pytest.mark.asyncio
    async def test_kitchen_sink_class(self) -> None:
        """Test kitchen-sink class detection."""
        methods = "\n    ".join([f"def method_{i}(self): pass" for i in range(20)])
        content = f"""
class KitchenSink:
    {methods}
"""
        trace = await validate_content_probe(content, "bloat.py")

        violations = trace.value.value
        assert any("kitchen-sink" in v.message.lower() for v in violations)


# =============================================================================
# PolicyTrace Tests
# =============================================================================


class TestPolicyTrace:
    """Test PolicyTrace emission."""

    @pytest.mark.asyncio
    async def test_trace_has_entries(self) -> None:
        """Test that trace contains entries for each phase."""
        content = "def hello(): pass"
        trace = await validate_content_probe(content, "test.py")

        # Should have entries for:
        # 1. start_heuristic
        # 2. advance_to_semantic
        # 3. run_tastefulness
        # 4. run_composability
        # 5. run_gratitude
        # 6. advance_to_synthesis
        # 7. synthesize
        assert len(trace.entries) >= 7

    @pytest.mark.asyncio
    async def test_trace_has_reasoning(self) -> None:
        """Test that trace entries have reasoning."""
        content = "def hello(): pass"
        trace = await validate_content_probe(content, "test.py")

        for entry in trace.entries:
            assert entry.reasoning  # All entries should have reasoning

    @pytest.mark.asyncio
    async def test_total_reward_computed(self) -> None:
        """Test that total reward is accumulated."""
        content = '''
"""Module with gratitude."""
def hello() -> str:
    """Say hello."""
    return "hello"
'''
        trace = await validate_content_probe(content, "test.py")

        # Clean code should have positive total reward
        assert trace.total_reward > 0.0

    @pytest.mark.asyncio
    async def test_violations_penalize_reward(self) -> None:
        """Test that violations reduce reward."""
        clean_content = '''
"""Module with gratitude signals."""
def hello() -> str:
    """Say hello."""
    return "hello"
'''
        dirty_content = 'password = "secret"'

        clean_trace = await validate_content_probe(clean_content, "clean.py")
        dirty_trace = await validate_content_probe(dirty_content, "dirty.py")

        # Dirty code should have lower total reward
        assert dirty_trace.total_reward < clean_trace.total_reward


# =============================================================================
# Constitutional Score Tests
# =============================================================================


class TestConstitutionalScore:
    """Test constitutional scoring."""

    @pytest.mark.asyncio
    async def test_ethical_violations_impact_score(self) -> None:
        """Test that ethical violations have high impact."""
        content = """
password = "secret"
api_key = "key123"
"""
        trace = await validate_content_probe(content, "ethical.py")

        # Should have ethical violations detected
        ethical_violations = [
            v for v in trace.value.value if v.principle == Principle.ETHICAL
        ]
        assert len(ethical_violations) > 0

        # Should have lower total reward than clean code
        assert trace.total_reward < 1.0  # Less than perfect score

    @pytest.mark.asyncio
    async def test_composable_violations_impact_score(self) -> None:
        """Test that composability violations impact score."""
        content = """
def add_item(item, items=[]):
    items.append(item)
"""
        trace = await validate_content_probe(content, "composable.py")

        # Should have composability penalty
        comp_penalties = [
            e.reward.composable for e in trace.entries if e.reward.composable < 0
        ]
        assert len(comp_penalties) > 0

    @pytest.mark.asyncio
    async def test_weighted_total(self) -> None:
        """Test that weighted total is computed."""
        content = "def hello(): pass"
        trace = await validate_content_probe(content, "test.py")

        # Each entry should have weighted_total
        for entry in trace.entries:
            assert isinstance(entry.reward.weighted_total, float)


# =============================================================================
# Analyzer Score Tests
# =============================================================================


class TestAnalyzerScores:
    """Test specialized analyzer scores."""

    @pytest.mark.asyncio
    async def test_tastefulness_score_in_verdict(self) -> None:
        """Test that tastefulness score is preserved."""
        content = "def hello(): pass"
        trace = await validate_content_probe(content, "test.py")

        # Final synthesis entry should mention scores
        synthesis_entry = [
            e for e in trace.entries if e.action.name == "synthesize"
        ][0]
        assert "Tastefulness=" in synthesis_entry.reasoning

    @pytest.mark.asyncio
    async def test_composability_score_in_verdict(self) -> None:
        """Test that composability score is preserved."""
        content = "def hello(): pass"
        trace = await validate_content_probe(content, "test.py")

        synthesis_entry = [
            e for e in trace.entries if e.action.name == "synthesize"
        ][0]
        assert "Composability=" in synthesis_entry.reasoning

    @pytest.mark.asyncio
    async def test_gratitude_score_in_verdict(self) -> None:
        """Test that gratitude score is preserved."""
        content = "def hello(): pass"
        trace = await validate_content_probe(content, "test.py")

        synthesis_entry = [
            e for e in trace.entries if e.action.name == "synthesize"
        ][0]
        assert "Gratitude=" in synthesis_entry.reasoning


# =============================================================================
# File Validation Tests
# =============================================================================


class TestFileValidation:
    """Test file validation."""

    @pytest.mark.asyncio
    async def test_nonexistent_file(self) -> None:
        """Test validating nonexistent file."""
        trace = await validate_file_probe("/nonexistent/file.py")

        assert not trace.value.passed
        assert any("not found" in v.message.lower() for v in trace.value.value)

    @pytest.mark.asyncio
    async def test_existing_file(self, tmp_path) -> None:
        """Test validating existing file."""
        file_path = tmp_path / "test.py"
        file_path.write_text("def hello(): pass")

        trace = await validate_file_probe(str(file_path))

        assert trace.value.passed


# =============================================================================
# Backward Compatibility Tests
# =============================================================================


class TestBackwardCompatibility:
    """Test that new probe matches old gatekeeper behavior."""

    @pytest.mark.asyncio
    async def test_same_violations_as_old(self) -> None:
        """Test that probe detects same violations as old gatekeeper."""
        from agents.k.gatekeeper import SemanticGatekeeper

        content = """
password = "secret"
class DatabaseSingleton:
    pass
"""

        # Old gatekeeper (ignore deprecation warning)
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            old = SemanticGatekeeper(use_llm=False)
            old_result = await old.validate_content(content, "test.py", use_analyzers=False)

        # New probe (using only heuristics for fair comparison)
        # The probe always runs analyzers, so we compare heuristic violations only
        new_trace = await validate_content_probe(content, "test.py")

        # Filter to heuristic violations (those without line-specific evidence from analyzers)
        # Both should detect: password + singleton
        old_critical_and_errors = {
            v.principle
            for v in old_result.violations
            if v.severity in [Severity.CRITICAL, Severity.ERROR]
        }
        new_critical_and_errors = {
            v.principle
            for v in new_trace.value.value
            if v.severity in [Severity.CRITICAL, Severity.ERROR]
        }

        # Both should detect ethical (password) and composable (singleton)
        assert Principle.ETHICAL in old_critical_and_errors
        assert Principle.ETHICAL in new_critical_and_errors
        assert Principle.COMPOSABLE in old_critical_and_errors
        assert Principle.COMPOSABLE in new_critical_and_errors

    @pytest.mark.asyncio
    async def test_same_pass_fail_as_old(self) -> None:
        """Test that pass/fail threshold matches."""
        from agents.k.gatekeeper import SemanticGatekeeper

        test_cases = [
            ("def hello(): pass", True),  # Should pass
            ('password = "secret"', False),  # Should fail
            ("class Manager: pass", True),  # Warning only, should pass
        ]

        for content, expected_pass in test_cases:
            # Old gatekeeper
            import warnings

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                old = SemanticGatekeeper(use_llm=False)
                old_result = await old.validate_content(content, "test.py")

            # New probe
            new_trace = await validate_content_probe(content, "test.py")

            assert old_result.passed == new_trace.value.passed == expected_pass
