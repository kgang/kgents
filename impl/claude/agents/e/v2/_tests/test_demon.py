"""Tests for E-gent v2 Teleological Demon (5-layer selection)."""

import pytest

from agents.e.v2.demon import (
    # Main types
    TeleologicalDemon,
    DemonConfig,
    DemonStats,
    SelectionResult,
    RejectionReason,
    # Parasitic patterns
    ParasiticPattern,
    detect_hardcoding,
    detect_functionality_deletion,
    detect_pass_only_bodies,
    detect_test_gaming,
    # Factory functions
    create_demon,
    create_strict_demon,
    create_lenient_demon,
)
from agents.e.v2.types import (
    Phage,
    PhageStatus,
    MutationVector,
    Intent,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def simple_mutation() -> MutationVector:
    """A simple, valid mutation."""
    return MutationVector(
        schema_signature="loop_to_comprehension",
        original_code="""
def process_items(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result
""",
        mutated_code="""
def process_items(items):
    return [item * 2 for item in items]
""",
        enthalpy_delta=-0.3,
        entropy_delta=0.0,
        temperature=1.0,
        description="Convert append-loop to list comprehension",
        confidence=0.8,
        lines_changed=5,
    )


@pytest.fixture
def simple_phage(simple_mutation: MutationVector) -> Phage:
    """A simple phage with a valid mutation."""
    return Phage(
        target_module="test_module",
        mutation=simple_mutation,
        hypothesis="Simplify loop to comprehension",
    )


@pytest.fixture
def simple_intent() -> Intent:
    """A simple intent for testing."""
    return Intent(
        embedding=[0.5, 0.5, 0.5],
        source="user",
        description="Refactor code to be more Pythonic",
        confidence=1.0,
    )


@pytest.fixture
def demon() -> TeleologicalDemon:
    """A basic demon for testing."""
    return create_demon()


@pytest.fixture
def strict_demon(simple_intent: Intent) -> TeleologicalDemon:
    """A strict demon for testing."""
    return create_strict_demon(intent=simple_intent)


# =============================================================================
# SelectionResult Tests
# =============================================================================


class TestSelectionResult:
    """Tests for SelectionResult."""

    def test_rejected_creation(self) -> None:
        """Test creating a rejected result."""
        result = SelectionResult.rejected(
            layer=2,
            reason=RejectionReason.TYPE_MISMATCH,
            detail="Types don't match",
        )

        assert not result.passed
        assert result.layer_reached == 2
        assert result.rejection_reason == RejectionReason.TYPE_MISMATCH
        assert result.rejection_detail == "Types don't match"

    def test_accepted_creation(self) -> None:
        """Test creating an accepted result."""
        result = SelectionResult.accepted(
            syntax_valid=True,
            type_compatible=True,
            intent_alignment=0.8,
        )

        assert result.passed
        assert result.layer_reached == 5
        assert result.syntax_valid
        assert result.type_compatible
        assert result.intent_alignment == 0.8


# =============================================================================
# DemonStats Tests
# =============================================================================


class TestDemonStats:
    """Tests for DemonStats."""

    def test_initial_stats(self) -> None:
        """Test initial stats are zero."""
        stats = DemonStats()

        assert stats.total_checked == 0
        assert stats.passed == 0
        assert stats.rejection_rate == 0.0

    def test_record_passed(self) -> None:
        """Test recording passed selection."""
        stats = DemonStats()
        result = SelectionResult.accepted()

        stats.record(result)

        assert stats.total_checked == 1
        assert stats.passed == 1
        assert stats.rejection_rate == 0.0

    def test_record_rejected(self) -> None:
        """Test recording rejected selection."""
        stats = DemonStats()
        result = SelectionResult.rejected(
            layer=3,
            reason=RejectionReason.INTENT_DRIFT,
        )

        stats.record(result)

        assert stats.total_checked == 1
        assert stats.passed == 0
        assert stats.layer3_rejections == 1
        assert stats.rejection_rate == 1.0

    def test_layer_rejection_rates(self) -> None:
        """Test layer rejection rate calculation."""
        stats = DemonStats()

        # 10 mutations checked
        # 3 rejected at layer 1
        # 2 rejected at layer 2
        # 5 passed
        stats.total_checked = 10
        stats.layer1_rejections = 3
        stats.layer2_rejections = 2
        stats.passed = 5

        rates = stats.layer_rejection_rates

        # Layer 1: 3/10 = 0.3
        assert rates[1] == pytest.approx(0.3)
        # Layer 2: 2/7 (remaining) ≈ 0.286
        assert rates[2] == pytest.approx(0.286, rel=0.01)


# =============================================================================
# Parasitic Pattern Detection Tests
# =============================================================================


class TestParasiticPatterns:
    """Tests for parasitic pattern detection."""

    def test_detect_hardcoding_positive(self) -> None:
        """Test detecting hardcoded returns."""
        original = """
def calculate(x):
    return x * 2 + 1
"""
        mutated = """
def calculate(x):
    if x == 5:
        return 11
    if x == 10:
        return 21
    if x == 15:
        return 31
    return 0
"""
        assert detect_hardcoding(original, mutated)

    def test_detect_hardcoding_negative(self) -> None:
        """Test non-hardcoded code passes."""
        original = """
def calculate(x):
    result = []
    for i in range(x):
        result.append(i)
    return result
"""
        mutated = """
def calculate(x):
    return list(range(x))
"""
        assert not detect_hardcoding(original, mutated)

    def test_detect_functionality_deletion_positive(self) -> None:
        """Test detecting deleted functionality."""
        original = """
def process(data):
    validated = validate(data)
    transformed = transform(validated)
    enriched = enrich(transformed)
    return save(enriched)
"""
        mutated = """
def process(data):
    return data
"""
        assert detect_functionality_deletion(original, mutated)

    def test_detect_functionality_deletion_negative(self) -> None:
        """Test non-deleted functionality passes."""
        original = """
def process(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
"""
        mutated = """
def process(data):
    return [item * 2 for item in data]
"""
        assert not detect_functionality_deletion(original, mutated)

    def test_detect_pass_only_bodies_positive(self) -> None:
        """Test detecting pass-only function bodies."""
        original = """
def calculate(x):
    return x * 2
"""
        mutated = """
def calculate(x):
    pass
"""
        assert detect_pass_only_bodies(original, mutated)

    def test_detect_pass_only_bodies_negative(self) -> None:
        """Test non-empty functions pass."""
        original = """
def calculate(x):
    return x * 2
"""
        mutated = """
def calculate(x):
    return x + x
"""
        assert not detect_pass_only_bodies(original, mutated)

    def test_detect_test_gaming_positive(self) -> None:
        """Test detecting test gaming (many new conditionals)."""
        original = """
def process(x):
    return x * 2
"""
        mutated = """
def process(x):
    if x == 1:
        return 2
    if x == 2:
        return 4
    if x == 3:
        return 6
    if x == 4:
        return 8
    if x == 5:
        return 10
    return x * 2
"""
        assert detect_test_gaming(original, mutated)

    def test_detect_test_gaming_negative(self) -> None:
        """Test normal code passes."""
        original = """
def process(x):
    if x > 0:
        return x * 2
    return 0
"""
        mutated = """
def process(x):
    if x > 0:
        return x + x
    return 0
"""
        assert not detect_test_gaming(original, mutated)


# =============================================================================
# Layer 1: Syntactic Tests
# =============================================================================


class TestLayer1Syntax:
    """Tests for Layer 1: Syntactic viability."""

    def test_valid_syntax_passes(
        self, demon: TeleologicalDemon, simple_phage: Phage
    ) -> None:
        """Test valid syntax passes layer 1."""
        result = demon._check_layer1_syntax(simple_phage.mutation)
        assert result.passed
        assert result.syntax_valid

    def test_invalid_original_syntax_fails(self, demon: TeleologicalDemon) -> None:
        """Test invalid original syntax fails layer 1."""
        mutation = MutationVector(
            original_code="def broken(",
            mutated_code="def valid(): pass",
        )
        result = demon._check_layer1_syntax(mutation)

        assert not result.passed
        assert result.rejection_reason == RejectionReason.SYNTAX_ERROR
        assert "Original code" in result.rejection_detail

    def test_invalid_mutated_syntax_fails(self, demon: TeleologicalDemon) -> None:
        """Test invalid mutated syntax fails layer 1."""
        mutation = MutationVector(
            original_code="def valid(): pass",
            mutated_code="def broken(",
        )
        result = demon._check_layer1_syntax(mutation)

        assert not result.passed
        assert result.rejection_reason == RejectionReason.SYNTAX_ERROR
        assert "Mutated code" in result.rejection_detail

    def test_diff_too_large_fails(self, demon: TeleologicalDemon) -> None:
        """Test oversized diff fails layer 1."""
        mutation = MutationVector(
            original_code="def valid(): pass",
            mutated_code="def valid(): pass",
            lines_changed=1000,
        )
        demon.config.max_diff_lines = 500

        result = demon._check_layer1_syntax(mutation)

        assert not result.passed
        assert result.rejection_reason == RejectionReason.DIFF_TOO_LARGE


# =============================================================================
# Layer 2: Semantic Tests
# =============================================================================


class TestLayer2Semantic:
    """Tests for Layer 2: Semantic stability."""

    def test_preserving_public_names_passes(self, demon: TeleologicalDemon) -> None:
        """Test mutations preserving public names pass layer 2."""
        mutation = MutationVector(
            original_code="""
def public_func():
    pass

class PublicClass:
    pass
""",
            mutated_code="""
def public_func():
    return 42

class PublicClass:
    def method(self):
        pass
""",
        )

        result = demon._check_layer2_semantic(mutation)
        assert result.passed
        assert result.type_compatible

    def test_removing_public_name_fails(self, demon: TeleologicalDemon) -> None:
        """Test removing public names fails layer 2."""
        mutation = MutationVector(
            original_code="""
def public_func():
    pass

def another_func():
    pass
""",
            mutated_code="""
def another_func():
    pass
""",
        )

        result = demon._check_layer2_semantic(mutation)
        assert not result.passed
        assert result.rejection_reason == RejectionReason.TYPE_MISMATCH

    def test_removing_private_name_passes(self, demon: TeleologicalDemon) -> None:
        """Test removing private names passes layer 2."""
        mutation = MutationVector(
            original_code="""
def public_func():
    pass

def _private_func():
    pass
""",
            mutated_code="""
def public_func():
    pass
""",
        )

        result = demon._check_layer2_semantic(mutation)
        assert result.passed

    def test_type_check_disabled(self) -> None:
        """Test that type checking can be disabled."""
        config = DemonConfig(require_type_compatibility=False)
        demon = TeleologicalDemon(config=config)

        mutation = MutationVector(
            original_code="def func(): pass",
            mutated_code="# empty",
        )

        result = demon._check_layer2_semantic(mutation)
        assert result.passed

    def test_custom_type_checker(self) -> None:
        """Test custom type checker integration."""

        def strict_checker(orig: str, mut: str) -> bool:
            return False  # Always fail

        demon = TeleologicalDemon(type_checker=strict_checker)
        mutation = MutationVector(
            original_code="def func(): pass",
            mutated_code="def func(): pass",
        )

        result = demon._check_layer2_semantic(mutation)
        assert not result.passed


# =============================================================================
# Layer 3: Teleological Tests
# =============================================================================


class TestLayer3Teleological:
    """Tests for Layer 3: Teleological alignment."""

    def test_high_confidence_passes(self, demon: TeleologicalDemon) -> None:
        """Test high confidence mutation passes layer 3."""
        mutation = MutationVector(
            original_code="def func(): pass",
            mutated_code="def func(): return 1",
            confidence=0.8,
            description="Add return value",
        )

        result = demon._check_layer3_teleological(mutation)
        assert result.passed
        assert result.intent_alignment >= demon.config.min_intent_alignment

    def test_low_confidence_fails(self, demon: TeleologicalDemon) -> None:
        """Test low confidence mutation fails layer 3."""
        mutation = MutationVector(
            original_code="def func(): pass",
            mutated_code="def func(): return 1",
            confidence=0.1,
        )
        demon.config.min_intent_alignment = 0.3

        result = demon._check_layer3_teleological(mutation)
        assert not result.passed
        assert result.rejection_reason == RejectionReason.INTENT_DRIFT

    def test_parasitic_pattern_hardcoding_fails(self, demon: TeleologicalDemon) -> None:
        """Test parasitic pattern (hardcoding) fails layer 3."""
        mutation = MutationVector(
            original_code="""
def calculate(x):
    return x * 2 + 1
""",
            mutated_code="""
def calculate(x):
    if x == 5:
        return 11
    if x == 10:
        return 21
    if x == 15:
        return 31
    return 0
""",
            confidence=0.9,
        )

        result = demon._check_layer3_teleological(mutation)
        assert not result.passed
        assert result.rejection_reason == RejectionReason.PARASITIC_PATTERN
        assert "hardcoding" in result.rejection_detail

    def test_parasitic_pattern_pass_only_fails(self, demon: TeleologicalDemon) -> None:
        """Test parasitic pattern (pass-only) fails layer 3."""
        mutation = MutationVector(
            original_code="""
def calculate(x):
    return x * 2
""",
            mutated_code="""
def calculate(x):
    pass
""",
            confidence=0.9,
        )

        result = demon._check_layer3_teleological(mutation)
        assert not result.passed
        assert result.rejection_reason == RejectionReason.PARASITIC_PATTERN

    def test_parasitic_detection_disabled(self) -> None:
        """Test parasitic detection can be disabled."""
        config = DemonConfig(
            detect_parasitic_patterns=False,
            min_intent_alignment=0.0,
        )
        demon = TeleologicalDemon(config=config)

        mutation = MutationVector(
            original_code="def func(): return 1",
            mutated_code="def func(): pass",
            confidence=0.1,
        )

        result = demon._check_layer3_teleological(mutation)
        assert result.passed

    def test_with_intent_set(self, simple_intent: Intent) -> None:
        """Test layer 3 with Intent explicitly set."""
        demon = TeleologicalDemon(intent=simple_intent)
        mutation = MutationVector(
            original_code="def func(): pass",
            mutated_code="def func(): return 1",
            confidence=0.7,
            description="Refactor to be more Pythonic",
        )

        result = demon._check_layer3_teleological(mutation)
        assert result.passed


# =============================================================================
# Layer 4: Thermodynamic Tests
# =============================================================================


class TestLayer4Thermodynamic:
    """Tests for Layer 4: Thermodynamic viability."""

    def test_favorable_gibbs_passes(self, demon: TeleologicalDemon) -> None:
        """Test favorable Gibbs energy passes layer 4."""
        mutation = MutationVector(
            enthalpy_delta=-0.5,
            entropy_delta=0.1,
            temperature=1.0,
            original_code="x",
            mutated_code="y",
        )
        # ΔG = -0.5 - 1.0*0.1 = -0.6 (favorable)

        result = demon._check_layer4_thermodynamic(mutation)
        assert result.passed
        assert result.gibbs_favorable

    def test_unfavorable_gibbs_fails(self, demon: TeleologicalDemon) -> None:
        """Test unfavorable Gibbs energy fails layer 4."""
        mutation = MutationVector(
            enthalpy_delta=0.5,
            entropy_delta=0.0,
            temperature=1.0,
            original_code="x",
            mutated_code="y",
        )
        # ΔG = 0.5 - 1.0*0.0 = 0.5 (unfavorable)

        result = demon._check_layer4_thermodynamic(mutation)
        assert not result.passed
        assert result.rejection_reason == RejectionReason.UNFAVORABLE_GIBBS

    def test_complexity_explosion_fails(self, demon: TeleologicalDemon) -> None:
        """Test complexity explosion fails layer 4."""
        mutation = MutationVector(
            enthalpy_delta=2.0,  # High complexity increase
            entropy_delta=5.0,  # But also high entropy (still favorable)
            temperature=1.0,
            original_code="x",
            mutated_code="y",
        )
        # ΔG = 2.0 - 1.0*5.0 = -3.0 (favorable, but enthalpy too high)
        demon.config.max_enthalpy_increase = 1.0

        result = demon._check_layer4_thermodynamic(mutation)
        assert not result.passed
        assert result.rejection_reason == RejectionReason.COMPLEXITY_EXPLOSION

    def test_gibbs_check_disabled(self) -> None:
        """Test Gibbs check can be disabled."""
        config = DemonConfig(require_favorable_gibbs=False)
        demon = TeleologicalDemon(config=config)

        mutation = MutationVector(
            enthalpy_delta=1.0,
            entropy_delta=0.0,
            temperature=1.0,
            original_code="x",
            mutated_code="y",
        )

        result = demon._check_layer4_thermodynamic(mutation)
        assert result.passed


# =============================================================================
# Layer 5: Economic Tests
# =============================================================================


class TestLayer5Economic:
    """Tests for Layer 5: Economic viability."""

    def test_no_quoter_passes(self, demon: TeleologicalDemon) -> None:
        """Test without market quoter passes layer 5."""
        mutation = MutationVector(original_code="x", mutated_code="y")

        result = demon._check_layer5_economic(mutation)
        assert result.passed
        assert result.market_viable

    def test_good_odds_passes(self) -> None:
        """Test good market odds passes layer 5."""

        def quoter(m: MutationVector) -> tuple[float, bool]:
            return (0.5, True)  # 50% odds, has funds

        demon = TeleologicalDemon(market_quoter=quoter)
        mutation = MutationVector(original_code="x", mutated_code="y")

        result = demon._check_layer5_economic(mutation)
        assert result.passed

    def test_poor_odds_fails(self) -> None:
        """Test poor market odds fails layer 5."""

        def quoter(m: MutationVector) -> tuple[float, bool]:
            return (0.05, True)  # 5% odds

        demon = TeleologicalDemon(market_quoter=quoter)
        demon.config.min_market_odds = 0.1
        mutation = MutationVector(original_code="x", mutated_code="y")

        result = demon._check_layer5_economic(mutation)
        assert not result.passed
        assert result.rejection_reason == RejectionReason.ODDS_TOO_POOR

    def test_insufficient_funds_fails(self) -> None:
        """Test insufficient funds fails layer 5."""

        def quoter(m: MutationVector) -> tuple[float, bool]:
            return (0.5, False)  # Good odds, no funds

        demon = TeleologicalDemon(market_quoter=quoter)
        mutation = MutationVector(original_code="x", mutated_code="y")

        result = demon._check_layer5_economic(mutation)
        assert not result.passed
        assert result.rejection_reason == RejectionReason.INSUFFICIENT_FUNDS


# =============================================================================
# Full Selection Pipeline Tests
# =============================================================================


class TestFullSelection:
    """Tests for the full 5-layer selection pipeline."""

    def test_valid_phage_passes_all_layers(
        self,
        demon: TeleologicalDemon,
        simple_phage: Phage,
    ) -> None:
        """Test valid phage passes all layers."""
        result = demon.select(simple_phage)

        assert result.passed
        assert result.layer_reached == 5
        assert result.syntax_valid
        assert result.type_compatible
        assert result.gibbs_favorable
        assert result.market_viable
        assert simple_phage.status == PhageStatus.QUOTED

    def test_phage_without_mutation_fails(self, demon: TeleologicalDemon) -> None:
        """Test phage without mutation fails early."""
        phage = Phage()

        result = demon.select(phage)

        assert not result.passed
        assert result.layer_reached == 0

    def test_rejection_updates_phage_status(self, demon: TeleologicalDemon) -> None:
        """Test rejection updates phage status."""
        phage = Phage(
            mutation=MutationVector(
                original_code="def func(): pass",
                mutated_code="def (",  # Invalid syntax
            ),
        )

        result = demon.select(phage)

        assert not result.passed
        assert phage.status == PhageStatus.REJECTED
        assert phage.error is not None

    def test_stats_updated_on_selection(
        self,
        demon: TeleologicalDemon,
        simple_phage: Phage,
    ) -> None:
        """Test stats are updated on selection."""
        initial_total = demon.stats.total_checked

        demon.select(simple_phage)

        assert demon.stats.total_checked == initial_total + 1

    def test_batch_selection(self, demon: TeleologicalDemon) -> None:
        """Test batch selection."""
        phages = [
            Phage(
                mutation=MutationVector(
                    original_code="def f(): pass",
                    mutated_code="def f(): return 1",
                    enthalpy_delta=-0.1,
                    confidence=0.8,
                )
            ),
            Phage(
                mutation=MutationVector(
                    original_code="def g(): pass",
                    mutated_code="def g(",  # Invalid
                )
            ),
            Phage(
                mutation=MutationVector(
                    original_code="def h(): pass",
                    mutated_code="def h(): return 2",
                    enthalpy_delta=-0.1,
                    confidence=0.8,
                )
            ),
        ]

        results = demon.select_batch(phages)

        assert len(results) == 3
        assert results[0][1].passed
        assert not results[1][1].passed
        assert results[2][1].passed

    def test_filter_batch(self, demon: TeleologicalDemon) -> None:
        """Test filter_batch returns only passing phages."""
        phages = [
            Phage(
                mutation=MutationVector(
                    original_code="def f(): pass",
                    mutated_code="def f(): return 1",
                    enthalpy_delta=-0.1,
                    confidence=0.8,
                )
            ),
            Phage(
                mutation=MutationVector(
                    original_code="def g(): pass",
                    mutated_code="def g(",  # Invalid
                )
            ),
        ]

        passed = demon.filter_batch(phages)

        assert len(passed) == 1

    def test_skip_layers(self) -> None:
        """Test skipping specific layers."""
        config = DemonConfig(skip_layers={2, 3, 4, 5})
        demon = TeleologicalDemon(config=config)

        # This mutation would fail layer 2 normally
        phage = Phage(
            mutation=MutationVector(
                original_code="def public(): pass",
                mutated_code="def other(): pass",  # Public name removed
            )
        )

        result = demon.select(phage)

        # Should pass because layer 2 is skipped
        assert result.passed


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_demon(self) -> None:
        """Test create_demon factory."""
        demon = create_demon()
        assert isinstance(demon, TeleologicalDemon)
        assert demon.config.min_intent_alignment == 0.3

    def test_create_demon_with_intent(self, simple_intent: Intent) -> None:
        """Test create_demon with intent."""
        demon = create_demon(intent=simple_intent)
        assert demon.intent == simple_intent

    def test_create_strict_demon(self) -> None:
        """Test create_strict_demon factory."""
        demon = create_strict_demon()
        assert demon.config.min_intent_alignment == 0.5
        assert demon.config.detect_parasitic_patterns
        assert demon.config.require_favorable_gibbs

    def test_create_lenient_demon(self) -> None:
        """Test create_lenient_demon factory."""
        demon = create_lenient_demon()
        assert demon.config.min_intent_alignment == 0.1
        assert not demon.config.detect_parasitic_patterns
        assert not demon.config.require_favorable_gibbs


# =============================================================================
# Integration Tests
# =============================================================================


class TestDemonIntegration:
    """Integration tests for the Teleological Demon."""

    def test_set_intent(self, demon: TeleologicalDemon, simple_intent: Intent) -> None:
        """Test setting intent after creation."""
        assert demon.intent is None
        demon.set_intent(simple_intent)
        assert demon.intent == simple_intent

    def test_add_parasitic_pattern(self, demon: TeleologicalDemon) -> None:
        """Test adding custom parasitic pattern."""
        custom_pattern = ParasiticPattern(
            name="always_none",
            description="Returns None for everything",
            detector=lambda o, m: "return None" in m,
        )
        demon.add_parasitic_pattern(custom_pattern)

        mutation = MutationVector(
            original_code="def func(): return 1",
            mutated_code="def func(): return None",
            confidence=0.9,
        )

        result = demon._check_layer3_teleological(mutation)
        assert not result.passed
        assert "always_none" in result.rejection_detail

    def test_intent_alignment_recorded_on_phage(
        self,
        demon: TeleologicalDemon,
        simple_phage: Phage,
    ) -> None:
        """Test intent alignment is recorded on phage."""
        demon.select(simple_phage)

        assert simple_phage.intent_checked
        assert simple_phage.intent_alignment > 0

    def test_duration_recorded(
        self,
        demon: TeleologicalDemon,
        simple_phage: Phage,
    ) -> None:
        """Test selection duration is recorded."""
        result = demon.select(simple_phage)

        assert result.duration_ms > 0


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_code(self, demon: TeleologicalDemon) -> None:
        """Test empty code handling."""
        mutation = MutationVector(
            original_code="",
            mutated_code="",
        )
        phage = Phage(mutation=mutation)

        result = demon.select(phage)
        # Empty code is valid Python
        assert result.layer_reached >= 1

    def test_whitespace_only_code(self, demon: TeleologicalDemon) -> None:
        """Test whitespace-only code handling."""
        mutation = MutationVector(
            original_code="   \n\n   ",
            mutated_code="   \n\n   ",
        )
        phage = Phage(mutation=mutation)

        result = demon.select(phage)
        # Whitespace is valid Python
        assert result.layer_reached >= 1

    def test_unicode_in_code(self, demon: TeleologicalDemon) -> None:
        """Test Unicode in code handling."""
        mutation = MutationVector(
            original_code='def func(): return "hello 世界"',
            mutated_code='def func(): return "hello 世界!"',
            enthalpy_delta=-0.1,
            confidence=0.8,
        )
        phage = Phage(mutation=mutation)

        result = demon.select(phage)
        assert result.passed

    def test_very_large_diff(self, demon: TeleologicalDemon) -> None:
        """Test very large diff handling."""
        mutation = MutationVector(
            original_code="def f(): pass",
            mutated_code="def f(): pass",
            lines_changed=10000,
        )
        phage = Phage(mutation=mutation)

        result = demon.select(phage)
        assert not result.passed
        assert result.rejection_reason == RejectionReason.DIFF_TOO_LARGE
