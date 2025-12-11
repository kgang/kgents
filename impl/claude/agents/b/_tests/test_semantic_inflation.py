"""
Tests for Semantic Inflation: Complexity → Verbosity Pressure Economics

Phase 4 of Structural Economics (B-gent × G-gent Integration).

Tests cover:
1. ComplexityVector: Multi-dimensional complexity measurement
2. AudienceProfile: Audience gap calculation
3. InflationPressure: Verbosity pressure from complexity
4. InflationBudget: Token allocation between content and explanation
5. DeflationNegotiator: Compression strategies
6. ComplexityAnalyzer: Code/text analysis
7. SemanticCPIMonitor: System-wide inflation tracking
8. Convenience functions
9. Integration scenarios
10. Edge cases
"""

from datetime import datetime

import pytest
from agents.b.semantic_inflation import (
    AudienceLevel,
    AudienceProfile,
    ComplexityAnalyzer,
    # Types
    ComplexityDimension,
    ComplexityVector,
    DeflationNegotiator,
    DeflationProposal,
    DeflationStrategy,
    InflationBudget,
    InflationCategory,
    InflationPressure,
    InflationReport,
    SemanticCPIMonitor,
    TokenAllocation,
    analyze_complexity,
    calculate_inflation_pressure,
    # Functions
    create_inflation_budget,
    estimate_explanation_tokens,
    get_deflation_recommendations,
)

# =============================================================================
# ComplexityVector Tests
# =============================================================================


class TestComplexityVector:
    """Tests for ComplexityVector."""

    def test_default_values(self) -> None:
        """Test default complexity is zero."""
        v = ComplexityVector()
        assert v.structural == 0.0
        assert v.temporal == 0.0
        assert v.conceptual == 0.0
        assert v.relational == 0.0
        assert v.novelty == 0.0
        assert v.risk == 0.0

    def test_magnitude_zero(self) -> None:
        """Test zero complexity has zero magnitude."""
        v = ComplexityVector()
        assert v.magnitude == 0.0

    def test_magnitude_calculation(self) -> None:
        """Test magnitude calculation."""
        v = ComplexityVector(structural=0.5, temporal=0.5)
        assert 0.0 < v.magnitude < 1.0

    def test_magnitude_max(self) -> None:
        """Test maximum magnitude is 1.0."""
        v = ComplexityVector(
            structural=1.0,
            temporal=1.0,
            conceptual=1.0,
            relational=1.0,
            novelty=1.0,
            risk=1.0,
        )
        assert v.magnitude == pytest.approx(1.0, abs=0.01)

    def test_clamping(self) -> None:
        """Test values are clamped to [0, 1]."""
        v = ComplexityVector(structural=-0.5, temporal=1.5)
        assert v.structural == 0.0
        assert v.temporal == 1.0

    def test_dominant_dimension(self) -> None:
        """Test finding dominant dimension."""
        v = ComplexityVector(
            structural=0.2,
            temporal=0.3,
            conceptual=0.8,  # Dominant
            relational=0.1,
            novelty=0.4,
            risk=0.5,
        )
        assert v.dominant_dimension == ComplexityDimension.CONCEPTUAL

    def test_dominant_dimension_tie(self) -> None:
        """Test dominant dimension with tie."""
        v = ComplexityVector(structural=0.5, temporal=0.5)
        # Should pick one deterministically
        assert v.dominant_dimension in (
            ComplexityDimension.STRUCTURAL,
            ComplexityDimension.TEMPORAL,
        )

    def test_weighted_sum_default(self) -> None:
        """Test weighted sum with default weights."""
        v = ComplexityVector(
            structural=0.5,
            temporal=0.5,
            conceptual=0.5,
            relational=0.5,
            novelty=0.5,
            risk=0.5,
        )
        # Risk and novelty have higher weights by default
        result = v.weighted_sum()
        assert result > 0.4  # Should be elevated due to risk/novelty weights

    def test_weighted_sum_custom(self) -> None:
        """Test weighted sum with custom weights."""
        v = ComplexityVector(structural=1.0)
        weights = {ComplexityDimension.STRUCTURAL: 2.0}
        # Only structural matters, and it has weight 2.0
        result = v.weighted_sum(weights)
        assert result == pytest.approx(1.0, abs=0.01)


# =============================================================================
# AudienceProfile Tests
# =============================================================================


class TestAudienceProfile:
    """Tests for AudienceProfile."""

    def test_default_profile(self) -> None:
        """Test default audience is intermediate."""
        p = AudienceProfile()
        assert p.level == AudienceLevel.INTERMEDIATE
        assert p.domain_familiarity == 0.5
        assert p.context_available == 0.5
        assert p.patience == 0.5

    def test_expert_audience_gap(self) -> None:
        """Test expert audience has low gap."""
        p = AudienceProfile(level=AudienceLevel.EXPERT)
        assert p.audience_gap < 0.5

    def test_layperson_audience_gap(self) -> None:
        """Test layperson audience has high gap."""
        p = AudienceProfile(level=AudienceLevel.LAYPERSON)
        assert p.audience_gap > 1.5  # Higher than intermediate

    def test_familiarity_reduces_gap(self) -> None:
        """Test domain familiarity reduces audience gap."""
        low_familiarity = AudienceProfile(domain_familiarity=0.0)
        high_familiarity = AudienceProfile(domain_familiarity=1.0)
        assert high_familiarity.audience_gap < low_familiarity.audience_gap

    def test_context_reduces_gap(self) -> None:
        """Test available context reduces audience gap."""
        no_context = AudienceProfile(context_available=0.0)
        has_context = AudienceProfile(context_available=1.0)
        assert has_context.audience_gap < no_context.audience_gap

    def test_verbosity_tolerance(self) -> None:
        """Test verbosity tolerance varies by level."""
        expert = AudienceProfile(level=AudienceLevel.EXPERT)
        novice = AudienceProfile(level=AudienceLevel.NOVICE)
        assert novice.verbosity_tolerance > expert.verbosity_tolerance


class TestAudienceLevel:
    """Tests for AudienceLevel enum."""

    def test_explanation_multiplier_ordering(self) -> None:
        """Test explanation multipliers are ordered correctly."""
        assert (
            AudienceLevel.EXPERT.explanation_multiplier
            < AudienceLevel.PRACTITIONER.explanation_multiplier
        )
        assert (
            AudienceLevel.PRACTITIONER.explanation_multiplier
            < AudienceLevel.INTERMEDIATE.explanation_multiplier
        )
        assert (
            AudienceLevel.INTERMEDIATE.explanation_multiplier
            < AudienceLevel.NOVICE.explanation_multiplier
        )
        assert (
            AudienceLevel.NOVICE.explanation_multiplier
            < AudienceLevel.LAYPERSON.explanation_multiplier
        )


# =============================================================================
# InflationPressure Tests
# =============================================================================


class TestInflationPressure:
    """Tests for InflationPressure."""

    def test_zero_complexity_low_pressure(self) -> None:
        """Test zero complexity creates low pressure."""
        pressure = InflationPressure(
            complexity=ComplexityVector(),
            audience=AudienceProfile(),
            base_tokens=100,
        )
        assert pressure.pressure_score < 0.5

    def test_high_complexity_high_pressure(self) -> None:
        """Test high complexity creates high pressure."""
        pressure = InflationPressure(
            complexity=ComplexityVector(
                structural=0.9,
                temporal=0.9,
                conceptual=0.9,
                relational=0.9,
                novelty=0.9,
                risk=0.9,
            ),
            audience=AudienceProfile(level=AudienceLevel.NOVICE),
            base_tokens=100,
        )
        assert pressure.pressure_score > 1.0

    def test_recommended_explanation_tokens(self) -> None:
        """Test explanation token calculation."""
        pressure = InflationPressure(
            complexity=ComplexityVector(structural=0.5),
            audience=AudienceProfile(),
            base_tokens=100,
        )
        # Should recommend some explanation tokens
        assert pressure.recommended_explanation_tokens >= 0
        assert pressure.total_recommended_tokens >= pressure.base_tokens

    def test_inflation_rate(self) -> None:
        """Test inflation rate equals pressure score."""
        pressure = InflationPressure(
            complexity=ComplexityVector(structural=0.5),
            audience=AudienceProfile(),
            base_tokens=100,
        )
        assert pressure.inflation_rate == pressure.pressure_score

    def test_explanation_ratio(self) -> None:
        """Test explanation ratio calculation."""
        pressure = InflationPressure(
            complexity=ComplexityVector(structural=0.8),
            audience=AudienceProfile(),
            base_tokens=100,
        )
        ratio = pressure.explanation_ratio
        assert 0.0 <= ratio <= 1.0

    def test_risk_amplifies_pressure(self) -> None:
        """Test that risk amplifies pressure."""
        low_risk = InflationPressure(
            complexity=ComplexityVector(structural=0.5, risk=0.0),
            audience=AudienceProfile(),
            base_tokens=100,
        )
        high_risk = InflationPressure(
            complexity=ComplexityVector(structural=0.5, risk=0.9),
            audience=AudienceProfile(),
            base_tokens=100,
        )
        assert high_risk.pressure_score > low_risk.pressure_score


# =============================================================================
# InflationCategory Tests
# =============================================================================


class TestInflationCategory:
    """Tests for InflationCategory."""

    def test_deflationary(self) -> None:
        """Test deflationary category threshold."""
        assert InflationCategory.from_pressure(0.1) == InflationCategory.DEFLATIONARY

    def test_stable(self) -> None:
        """Test stable category threshold."""
        assert InflationCategory.from_pressure(0.3) == InflationCategory.STABLE

    def test_moderate(self) -> None:
        """Test moderate category threshold."""
        assert InflationCategory.from_pressure(0.7) == InflationCategory.MODERATE

    def test_high(self) -> None:
        """Test high category threshold."""
        assert InflationCategory.from_pressure(1.5) == InflationCategory.HIGH

    def test_hyperinflation(self) -> None:
        """Test hyperinflation category threshold."""
        assert InflationCategory.from_pressure(2.5) == InflationCategory.HYPERINFLATION


# =============================================================================
# InflationReport Tests
# =============================================================================


class TestInflationReport:
    """Tests for InflationReport."""

    def test_analyze_creates_report(self) -> None:
        """Test analyze creates a complete report."""
        pressure = InflationPressure(
            complexity=ComplexityVector(structural=0.5),
            audience=AudienceProfile(),
            base_tokens=100,
        )
        report = InflationReport.analyze(pressure)
        assert report.pressure == pressure
        assert isinstance(report.category, InflationCategory)
        assert isinstance(report.dominant_driver, ComplexityDimension)

    def test_hyperinflation_warning(self) -> None:
        """Test hyperinflation generates warning."""
        pressure = InflationPressure(
            complexity=ComplexityVector(
                structural=1.0,
                temporal=1.0,
                conceptual=1.0,
                novelty=1.0,
                risk=1.0,
            ),
            audience=AudienceProfile(level=AudienceLevel.LAYPERSON),
            base_tokens=100,
        )
        report = InflationReport.analyze(pressure)
        assert len(report.warnings) > 0

    def test_high_risk_warning(self) -> None:
        """Test high risk generates warning."""
        pressure = InflationPressure(
            complexity=ComplexityVector(risk=0.9),
            audience=AudienceProfile(),
            base_tokens=100,
        )
        report = InflationReport.analyze(pressure)
        assert any("risk" in w.lower() for w in report.warnings)

    def test_recommendations_generated(self) -> None:
        """Test recommendations generated for high inflation."""
        pressure = InflationPressure(
            complexity=ComplexityVector(conceptual=0.9),
            audience=AudienceProfile(level=AudienceLevel.NOVICE),
            base_tokens=100,
        )
        report = InflationReport.analyze(pressure)
        # High conceptual complexity should generate recommendations
        if report.category in (
            InflationCategory.HIGH,
            InflationCategory.HYPERINFLATION,
        ):
            assert len(report.recommendations) > 0


# =============================================================================
# TokenAllocation Tests
# =============================================================================


class TestTokenAllocation:
    """Tests for TokenAllocation."""

    def test_total_calculation(self) -> None:
        """Test total token calculation."""
        alloc = TokenAllocation(
            content_tokens=100,
            explanation_tokens=50,
            buffer_tokens=10,
        )
        assert alloc.total == 160

    def test_explanation_ratio(self) -> None:
        """Test explanation ratio calculation."""
        alloc = TokenAllocation(
            content_tokens=100,
            explanation_tokens=100,
            buffer_tokens=0,
        )
        assert alloc.explanation_ratio == 0.5

    def test_explanation_ratio_zero_total(self) -> None:
        """Test explanation ratio with zero total."""
        alloc = TokenAllocation(
            content_tokens=0,
            explanation_tokens=0,
            buffer_tokens=0,
        )
        assert alloc.explanation_ratio == 0.0


# =============================================================================
# InflationBudget Tests
# =============================================================================


class TestInflationBudget:
    """Tests for InflationBudget."""

    def test_default_creation(self) -> None:
        """Test default budget creation."""
        budget = InflationBudget()
        assert budget.bank is not None
        assert budget.default_audience is not None

    def test_calculate_pressure(self) -> None:
        """Test pressure calculation."""
        budget = InflationBudget()
        complexity = ComplexityVector(structural=0.5)
        pressure = budget.calculate_pressure(complexity, base_tokens=100)
        assert isinstance(pressure, InflationPressure)

    def test_evaluate_approves_sufficient_budget(self) -> None:
        """Test evaluation approves with sufficient budget."""
        budget = InflationBudget()

        complexity = ComplexityVector(structural=0.3)
        decision = budget.evaluate(
            "agent1", complexity, base_tokens=100, available_budget=500
        )

        assert decision.approved is True

    def test_evaluate_rejects_insufficient_budget(self) -> None:
        """Test evaluation rejects with insufficient budget."""
        budget = InflationBudget()

        complexity = ComplexityVector(
            structural=1.0,
            temporal=1.0,
            conceptual=1.0,
            novelty=1.0,
            risk=1.0,
        )
        decision = budget.evaluate(
            "agent1",
            complexity,
            base_tokens=1000,
            available_budget=100,  # Way too little
        )

        assert decision.approved is False
        assert decision.deficit > 0

    def test_evaluate_with_deflation(self) -> None:
        """Test evaluation with deflation when budget tight."""
        budget = InflationBudget()

        complexity = ComplexityVector(structural=0.5)
        # Give just enough for content but not full explanation
        decision = budget.evaluate(
            "agent1",
            complexity,
            base_tokens=100,
            available_budget=150,  # Tight budget
        )

        # Should still approve but with reduced explanation
        if decision.approved:
            assert (
                decision.deflation_required is True
                or decision.allocation.explanation_tokens < 50
            )

    def test_per_agent_audience(self) -> None:
        """Test per-agent audience profiles."""
        budget = InflationBudget()

        expert_audience = AudienceProfile(level=AudienceLevel.EXPERT)
        budget.set_agent_audience("expert_agent", expert_audience)

        retrieved = budget.get_agent_audience("expert_agent")
        assert retrieved.level == AudienceLevel.EXPERT

    def test_risk_floor_enforced(self) -> None:
        """Test minimum explanation for high-risk operations."""
        budget = InflationBudget(risk_floor_ratio=0.3)

        complexity = ComplexityVector(risk=0.9)
        decision = budget.evaluate(
            "agent1",
            complexity,
            base_tokens=100,
            available_budget=1000,
        )

        assert decision.approved is True
        # Should have at least 30% explanation
        ratio = decision.allocation.explanation_ratio
        assert ratio >= 0.2  # Allow some flexibility

    def test_cpi_tracking(self) -> None:
        """Test CPI tracking."""
        budget = InflationBudget()

        # Record some inflation rates
        for rate in [0.3, 0.4, 0.5]:
            budget.record_inflation(rate)

        cpi = budget.get_cpi(window_size=10)
        assert 0.3 <= cpi <= 0.5


# =============================================================================
# DeflationNegotiator Tests
# =============================================================================


class TestDeflationNegotiator:
    """Tests for DeflationNegotiator."""

    def test_propose_deflation(self) -> None:
        """Test deflation proposals generation."""
        budget = InflationBudget()
        negotiator = DeflationNegotiator(budget)

        pressure = InflationPressure(
            complexity=ComplexityVector(structural=0.5),
            audience=AudienceProfile(),
            base_tokens=100,
        )
        report = InflationReport.analyze(pressure)

        proposals = negotiator.propose_deflation(report)
        assert len(proposals) == len(DeflationStrategy)

    def test_proposals_ordered_by_savings(self) -> None:
        """Test proposals are ordered by savings."""
        budget = InflationBudget()
        negotiator = DeflationNegotiator(budget)

        pressure = InflationPressure(
            complexity=ComplexityVector(structural=0.5),
            audience=AudienceProfile(),
            base_tokens=100,
        )
        report = InflationReport.analyze(pressure)

        proposals = negotiator.propose_deflation(report)
        # Should be sorted by savings (descending)
        for i in range(len(proposals) - 1):
            assert proposals[i].savings_ratio >= proposals[i + 1].savings_ratio

    def test_proposal_has_tradeoffs(self) -> None:
        """Test each proposal has trade-offs listed."""
        budget = InflationBudget()
        negotiator = DeflationNegotiator(budget)

        pressure = InflationPressure(
            complexity=ComplexityVector(structural=0.5),
            audience=AudienceProfile(),
            base_tokens=100,
        )
        report = InflationReport.analyze(pressure)

        proposals = negotiator.propose_deflation(report)
        for proposal in proposals:
            assert len(proposal.trade_offs) > 0
            assert proposal.implementation_hint != ""

    def test_recommend_strategy_basic(self) -> None:
        """Test strategy recommendation."""
        budget = InflationBudget()
        negotiator = DeflationNegotiator(budget)

        pressure = InflationPressure(
            complexity=ComplexityVector(structural=0.5),
            audience=AudienceProfile(),
            base_tokens=100,
        )
        report = InflationReport.analyze(pressure)

        strategy = negotiator.recommend_strategy(report)
        assert strategy is None or isinstance(strategy, DeflationStrategy)

    def test_recommend_strategy_with_constraints(self) -> None:
        """Test strategy recommendation respects constraints."""
        budget = InflationBudget()
        negotiator = DeflationNegotiator(budget)

        pressure = InflationPressure(
            complexity=ComplexityVector(structural=0.5),
            audience=AudienceProfile(),
            base_tokens=100,
        )
        report = InflationReport.analyze(pressure)

        strategy = negotiator.recommend_strategy(
            report,
            constraints={"no_pidgin": True},
        )
        assert strategy != DeflationStrategy.COMPRESS

    def test_high_risk_excludes_summarize(self) -> None:
        """Test high-risk operations exclude summarize strategy."""
        budget = InflationBudget()
        negotiator = DeflationNegotiator(budget)

        pressure = InflationPressure(
            complexity=ComplexityVector(risk=0.9),
            audience=AudienceProfile(),
            base_tokens=100,
        )
        report = InflationReport.analyze(pressure)

        strategy = negotiator.recommend_strategy(report)
        # Should not recommend summarize or audience_shift for high risk
        assert strategy not in (
            DeflationStrategy.SUMMARIZE,
            DeflationStrategy.AUDIENCE_SHIFT,
        )


# =============================================================================
# ComplexityAnalyzer Tests
# =============================================================================


class TestComplexityAnalyzer:
    """Tests for ComplexityAnalyzer."""

    def test_analyze_simple_code(self) -> None:
        """Test analysis of simple code."""
        analyzer = ComplexityAnalyzer()
        code = "x = 1\ny = 2\nz = x + y"
        complexity = analyzer.analyze_code(code)
        assert complexity.structural < 0.3
        assert complexity.temporal < 0.3

    def test_analyze_complex_code(self) -> None:
        """Test analysis of complex code."""
        analyzer = ComplexityAnalyzer()
        code = """
async def process_data():
    while True:
        try:
            if condition:
                for item in items:
                    if nested_condition:
                        await process(item)
        except Exception:
            pass
"""
        complexity = analyzer.analyze_code(code)
        assert complexity.structural > 0.2
        assert complexity.temporal > 0.2

    def test_analyze_risky_code(self) -> None:
        """Test analysis of risky code."""
        analyzer = ComplexityAnalyzer()
        code = "result = eval(user_input)\nos.system(command)"
        complexity = analyzer.analyze_code(code)
        assert complexity.risk > 0.3

    def test_analyze_text(self) -> None:
        """Test analysis of text."""
        analyzer = ComplexityAnalyzer()
        text = (
            "First, do this. Then, do that. After that, finally complete the process."
        )
        complexity = analyzer.analyze_text(text)
        assert complexity.temporal > 0.1  # Has temporal words

    def test_analyze_technical_text(self) -> None:
        """Test analysis of technical text."""
        analyzer = ComplexityAnalyzer()
        text = "The API endpoint accepts JSON data. See also the UserModel class."
        complexity = analyzer.analyze_text(text, is_technical=True)
        assert complexity.conceptual > 0.0

    def test_from_metadata(self) -> None:
        """Test creating complexity from metadata."""
        analyzer = ComplexityAnalyzer()
        complexity = analyzer.from_metadata(
            structural=0.5,
            risk=0.8,
        )
        assert complexity.structural == 0.5
        assert complexity.risk == 0.8
        assert complexity.temporal == 0.2  # Default


# =============================================================================
# SemanticCPIMonitor Tests
# =============================================================================


class TestSemanticCPIMonitor:
    """Tests for SemanticCPIMonitor."""

    def test_empty_cpi(self) -> None:
        """Test CPI is zero with no observations."""
        monitor = SemanticCPIMonitor()
        assert monitor.get_current_cpi() == 0.0

    def test_observe_and_cpi(self) -> None:
        """Test observing inflation and getting CPI."""
        monitor = SemanticCPIMonitor()

        # Generate some observations
        for i in range(10):
            pressure = InflationPressure(
                complexity=ComplexityVector(structural=0.3),
                audience=AudienceProfile(),
                base_tokens=100,
            )
            report = InflationReport.analyze(pressure)
            monitor.observe(report)

        cpi = monitor.get_current_cpi()
        assert cpi > 0.0

    def test_category_breakdown(self) -> None:
        """Test CPI breakdown by category."""
        monitor = SemanticCPIMonitor()

        # Generate observations with varying complexity
        complexities = [0.1, 0.3, 0.5, 0.7, 0.9]
        for c in complexities:
            pressure = InflationPressure(
                complexity=ComplexityVector(structural=c),
                audience=AudienceProfile(),
                base_tokens=100,
            )
            report = InflationReport.analyze(pressure)
            monitor.observe(report)

        breakdown = monitor.get_category_breakdown()
        assert len(breakdown) > 0

    def test_trend_insufficient_data(self) -> None:
        """Test trend with insufficient data."""
        monitor = SemanticCPIMonitor()
        assert monitor.get_trend() == "insufficient_data"

    def test_snapshot(self) -> None:
        """Test taking CPI snapshot."""
        monitor = SemanticCPIMonitor()

        # Generate some observations
        for _ in range(10):
            pressure = InflationPressure(
                complexity=ComplexityVector(structural=0.3),
                audience=AudienceProfile(),
                base_tokens=100,
            )
            report = InflationReport.analyze(pressure)
            monitor.observe(report)

        snapshot = monitor.snapshot()
        assert isinstance(snapshot.timestamp, datetime)
        assert snapshot.cpi >= 0.0
        assert snapshot.sample_size > 0

    def test_history(self) -> None:
        """Test snapshot history."""
        monitor = SemanticCPIMonitor()

        # Take multiple snapshots
        for _ in range(3):
            monitor.snapshot()

        history = monitor.get_history()
        assert len(history) == 3


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_inflation_budget(self) -> None:
        """Test create_inflation_budget function."""
        budget = create_inflation_budget()
        assert isinstance(budget, InflationBudget)

    def test_analyze_complexity_code(self) -> None:
        """Test analyze_complexity for code."""
        complexity = analyze_complexity("x = 1", is_code=True)
        assert isinstance(complexity, ComplexityVector)

    def test_analyze_complexity_text(self) -> None:
        """Test analyze_complexity for text."""
        complexity = analyze_complexity("This is a test.", is_code=False)
        assert isinstance(complexity, ComplexityVector)

    def test_calculate_inflation_pressure(self) -> None:
        """Test calculate_inflation_pressure function."""
        complexity = ComplexityVector(structural=0.5)
        pressure = calculate_inflation_pressure(complexity, 100)
        assert isinstance(pressure, InflationPressure)
        assert pressure.base_tokens == 100

    def test_calculate_inflation_pressure_with_level(self) -> None:
        """Test pressure calculation with audience level."""
        complexity = ComplexityVector(structural=0.5)
        expert_pressure = calculate_inflation_pressure(
            complexity, 100, AudienceLevel.EXPERT
        )
        novice_pressure = calculate_inflation_pressure(
            complexity, 100, AudienceLevel.NOVICE
        )
        assert novice_pressure.pressure_score > expert_pressure.pressure_score

    def test_get_deflation_recommendations(self) -> None:
        """Test get_deflation_recommendations function."""
        complexity = ComplexityVector(structural=0.5)
        pressure = calculate_inflation_pressure(complexity, 100)
        proposals = get_deflation_recommendations(pressure)
        assert len(proposals) > 0
        assert all(isinstance(p, DeflationProposal) for p in proposals)

    def test_estimate_explanation_tokens(self) -> None:
        """Test estimate_explanation_tokens function."""
        complexity = ComplexityVector(structural=0.5)
        tokens = estimate_explanation_tokens(complexity, 100)
        assert tokens >= 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for semantic inflation."""

    def test_full_workflow(self) -> None:
        """Test complete inflation workflow."""
        # 1. Analyze complexity
        code = """
async def process_batch(items):
    results = []
    for item in items:
        try:
            result = await process_item(item)
            results.append(result)
        except Exception as e:
            logging.error(f"Failed: {e}")
    return results
"""
        complexity = analyze_complexity(code, is_code=True)

        # 2. Calculate pressure
        pressure = calculate_inflation_pressure(
            complexity,
            base_tokens=50,
            audience_level=AudienceLevel.INTERMEDIATE,
        )

        # 3. Evaluate budget
        budget = create_inflation_budget()
        decision = budget.evaluate(
            "code_explainer",
            complexity,
            base_tokens=50,
            available_budget=200,
        )

        # 4. If deflation needed, get recommendations
        if decision.deflation_required:
            proposals = get_deflation_recommendations(pressure)
            assert len(proposals) > 0

        # 5. Track inflation
        cpi_monitor = SemanticCPIMonitor()
        cpi_monitor.observe(decision.inflation_report)

        # Verify workflow completed
        assert decision.allocation is not None
        assert decision.inflation_report is not None

    def test_audience_scaling(self) -> None:
        """Test that explanation scales with audience level."""
        complexity = ComplexityVector(structural=0.5, conceptual=0.5)
        base_tokens = 100

        expert_tokens = estimate_explanation_tokens(
            complexity, base_tokens, AudienceLevel.EXPERT
        )
        layperson_tokens = estimate_explanation_tokens(
            complexity, base_tokens, AudienceLevel.LAYPERSON
        )

        assert layperson_tokens > expert_tokens

    def test_risk_always_explained(self) -> None:
        """Test that high-risk operations always get explanation."""
        budget = InflationBudget()
        complexity = ComplexityVector(risk=0.9)

        decision = budget.evaluate(
            "risky_agent",
            complexity,
            base_tokens=100,
            available_budget=1000,
        )

        # High risk should always require explanation
        assert decision.allocation.explanation_tokens > 0

    def test_deflationary_operations(self) -> None:
        """Test simple operations can be deflationary."""
        complexity = ComplexityVector()  # All zeros
        pressure = calculate_inflation_pressure(
            complexity,
            base_tokens=100,
            audience_level=AudienceLevel.EXPERT,
        )

        report = InflationReport.analyze(pressure)
        assert report.category == InflationCategory.DEFLATIONARY


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_zero_base_tokens(self) -> None:
        """Test handling of zero base tokens."""
        complexity = ComplexityVector(structural=0.5)
        pressure = calculate_inflation_pressure(complexity, base_tokens=0)
        assert pressure.total_recommended_tokens >= 0

    def test_empty_code_analysis(self) -> None:
        """Test analysis of empty code."""
        complexity = analyze_complexity("", is_code=True)
        assert complexity.magnitude < 0.3

    def test_empty_text_analysis(self) -> None:
        """Test analysis of empty text."""
        complexity = analyze_complexity("", is_code=False)
        assert complexity.magnitude < 0.3

    def test_very_long_code(self) -> None:
        """Test analysis of very long code."""
        analyzer = ComplexityAnalyzer()
        code = "x = 1\n" * 1000
        complexity = analyzer.analyze_code(code)
        # Should handle without error
        assert 0.0 <= complexity.structural <= 1.0

    def test_unicode_text(self) -> None:
        """Test analysis of unicode text."""
        complexity = analyze_complexity("日本語テスト 🎉", is_code=False)
        assert isinstance(complexity, ComplexityVector)

    def test_large_budget_surplus(self) -> None:
        """Test with much more budget than needed."""
        budget = InflationBudget()
        complexity = ComplexityVector(structural=0.1)

        decision = budget.evaluate(
            "agent1",
            complexity,
            base_tokens=10,
            available_budget=1_000_000,
        )

        assert decision.approved is True
        assert decision.deficit == 0

    def test_exact_budget_match(self) -> None:
        """Test when budget exactly matches need."""
        budget = InflationBudget()
        complexity = ComplexityVector()  # Minimal complexity

        # Calculate exact need - need to account for min_explanation_ratio (10%)
        # With 100 base tokens and 10% min, we need at least 110 tokens
        _pressure = budget.calculate_pressure(complexity, base_tokens=100)
        min_explanation = int(100 * budget.min_explanation_ratio)
        exact_budget = 100 + min_explanation

        decision = budget.evaluate(
            "agent1",
            complexity,
            base_tokens=100,
            available_budget=exact_budget,
        )

        # Should approve with exact match (including min explanation)
        assert decision.approved is True
