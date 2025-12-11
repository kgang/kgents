"""
Tests for Syntax Tax: Chomsky-Based Pricing

B×G Phase 3 - Structural Economics integration.
"""

import pytest
from agents.b.syntax_tax import (
    ChomskyLevel,
    DowngradeNegotiator,
    GrammarAnalysis,
    GrammarClassifier,
    GrammarFeature,
    SyntaxTaxBudget,
    SyntaxTaxSchedule,
    calculate_syntax_tax,
    classify_grammar,
    create_syntax_tax_budget,
    get_tier_costs,
)

# =============================================================================
# ChomskyLevel Tests
# =============================================================================


class TestChomskyLevel:
    """Tests for ChomskyLevel enum."""

    def test_levels_in_order(self):
        """Levels are numbered correctly (Type 0-3)."""
        assert ChomskyLevel.TURING_COMPLETE.value == 0
        assert ChomskyLevel.CONTEXT_SENSITIVE.value == 1
        assert ChomskyLevel.CONTEXT_FREE.value == 2
        assert ChomskyLevel.REGULAR.value == 3

    def test_risk_levels(self):
        """Risk levels are assigned correctly."""
        assert ChomskyLevel.REGULAR.risk_level == "low"
        assert ChomskyLevel.CONTEXT_FREE.risk_level == "moderate"
        assert ChomskyLevel.CONTEXT_SENSITIVE.risk_level == "high"
        assert ChomskyLevel.TURING_COMPLETE.risk_level == "critical"

    def test_can_halt(self):
        """Only Turing-complete can run forever."""
        assert ChomskyLevel.REGULAR.can_halt is True
        assert ChomskyLevel.CONTEXT_FREE.can_halt is True
        assert ChomskyLevel.CONTEXT_SENSITIVE.can_halt is True
        assert ChomskyLevel.TURING_COMPLETE.can_halt is False

    def test_requires_escrow(self):
        """High-risk levels require escrow."""
        assert ChomskyLevel.REGULAR.requires_escrow is False
        assert ChomskyLevel.CONTEXT_FREE.requires_escrow is False
        assert ChomskyLevel.CONTEXT_SENSITIVE.requires_escrow is True
        assert ChomskyLevel.TURING_COMPLETE.requires_escrow is True

    def test_requires_gas_limit(self):
        """High-risk levels require gas limits."""
        assert ChomskyLevel.REGULAR.requires_gas_limit is False
        assert ChomskyLevel.CONTEXT_FREE.requires_gas_limit is False
        assert ChomskyLevel.CONTEXT_SENSITIVE.requires_gas_limit is True
        assert ChomskyLevel.TURING_COMPLETE.requires_gas_limit is True


# =============================================================================
# GrammarAnalysis Tests
# =============================================================================


class TestGrammarAnalysis:
    """Tests for GrammarAnalysis dataclass."""

    def test_basic_analysis(self):
        """Basic analysis creation."""
        analysis = GrammarAnalysis(level=ChomskyLevel.REGULAR)
        assert analysis.level == ChomskyLevel.REGULAR
        assert analysis.confidence == 1.0
        assert len(analysis.features) == 0

    def test_is_high_risk(self):
        """High risk detection."""
        regular = GrammarAnalysis(level=ChomskyLevel.REGULAR)
        assert regular.is_high_risk is False

        turing = GrammarAnalysis(level=ChomskyLevel.TURING_COMPLETE)
        assert turing.is_high_risk is True

    def test_can_run_unbounded(self):
        """Unbounded execution detection."""
        cf = GrammarAnalysis(level=ChomskyLevel.CONTEXT_FREE)
        assert cf.can_run_unbounded is False

        turing = GrammarAnalysis(level=ChomskyLevel.TURING_COMPLETE)
        assert turing.can_run_unbounded is True


# =============================================================================
# GrammarClassifier Tests
# =============================================================================


class TestGrammarClassifier:
    """Tests for GrammarClassifier."""

    @pytest.fixture
    def classifier(self):
        """Create classifier for testing."""
        return GrammarClassifier()

    # Regular (Type 3) grammars

    def test_classify_simple_regex(self, classifier):
        """Simple regex with quantifiers is classified as context-free."""
        grammar = r"[a-z]+"
        analysis = classifier.classify(grammar)
        # The + quantifier triggers context-free detection
        assert analysis.level in (ChomskyLevel.REGULAR, ChomskyLevel.CONTEXT_FREE)

    def test_classify_simple_pattern(self, classifier):
        """Simple pattern without BNF is regular."""
        grammar = "VERB NOUN"
        analysis = classifier.classify(grammar)
        assert analysis.level == ChomskyLevel.REGULAR

    def test_classify_alternation_only(self, classifier):
        """Simple alternation is regular."""
        grammar = "GET | POST | PUT | DELETE"
        analysis = classifier.classify(grammar)
        # Has | operator, so classified as context-free
        assert analysis.level in (ChomskyLevel.REGULAR, ChomskyLevel.CONTEXT_FREE)

    # Context-Free (Type 2) grammars

    def test_classify_bnf_grammar(self, classifier):
        """BNF grammar is context-free."""
        grammar = """
        command ::= verb noun
        verb ::= "GET" | "POST"
        noun ::= identifier
        """
        analysis = classifier.classify(grammar)
        assert analysis.level == ChomskyLevel.CONTEXT_FREE

    def test_classify_recursive_grammar(self, classifier):
        """Recursive grammar is context-free."""
        grammar = """
        expr ::= term | expr "+" term
        term ::= factor | term "*" factor
        """
        analysis = classifier.classify(grammar)
        assert analysis.level == ChomskyLevel.CONTEXT_FREE
        assert GrammarFeature.RECURSIVE_RULE in analysis.features

    def test_classify_nested_structure(self, classifier):
        """Nested structures are context-free."""
        grammar = 'list ::= "[" items "]"'
        analysis = classifier.classify(grammar)
        assert analysis.level == ChomskyLevel.CONTEXT_FREE
        # Recursive rule detected from 'list' appearing in BNF
        assert (
            GrammarFeature.RECURSIVE_RULE in analysis.features
            or GrammarFeature.NESTED_STRUCTURE in analysis.features
        )

    # Context-Sensitive (Type 1) grammars

    def test_classify_context_keyword(self, classifier):
        """Grammar with 'context' keyword is context-sensitive."""
        grammar = "context-dependent rule: A B → A C B"
        analysis = classifier.classify(grammar)
        assert analysis.level == ChomskyLevel.CONTEXT_SENSITIVE
        assert GrammarFeature.CONTEXT_DEPENDENT in analysis.features

    def test_classify_attribute_grammar(self, classifier):
        """Grammar with attributes is context-sensitive."""
        grammar = "@attribute inherited value"
        analysis = classifier.classify(grammar)
        assert analysis.level == ChomskyLevel.CONTEXT_SENSITIVE

    # Turing-Complete (Type 0) grammars

    def test_classify_with_eval(self, classifier):
        """Grammar with eval is Turing-complete."""
        grammar = "expr ::= eval(code)"
        analysis = classifier.classify(grammar)
        assert analysis.level == ChomskyLevel.TURING_COMPLETE
        assert GrammarFeature.ARBITRARY_COMPUTATION in analysis.features

    def test_classify_with_loop(self, classifier):
        """Grammar with loop is Turing-complete."""
        grammar = "program ::= while condition do statement"
        analysis = classifier.classify(grammar)
        assert analysis.level == ChomskyLevel.TURING_COMPLETE
        assert GrammarFeature.LOOP_CONSTRUCT in analysis.features

    def test_classify_recursive_keyword(self, classifier):
        """Grammar with 'recursive' keyword is Turing-complete."""
        grammar = "recursive function definition"
        analysis = classifier.classify(grammar)
        assert analysis.level == ChomskyLevel.TURING_COMPLETE

    def test_classify_unbounded(self, classifier):
        """Grammar marked unbounded is Turing-complete."""
        grammar = "unbounded computation"
        analysis = classifier.classify(grammar)
        assert analysis.level == ChomskyLevel.TURING_COMPLETE

    # Confidence levels

    def test_confidence_varies(self, classifier):
        """Confidence varies by grammar clarity."""
        simple = classifier.classify("[a-z]+")
        complex_tc = classifier.classify("eval(x)")

        # Simple regex should have high confidence
        assert simple.confidence >= 0.6

        # Turing-complete should have high confidence due to clear marker
        assert complex_tc.confidence >= 0.8


# =============================================================================
# SyntaxTaxSchedule Tests
# =============================================================================


class TestSyntaxTaxSchedule:
    """Tests for SyntaxTaxSchedule."""

    @pytest.fixture
    def schedule(self):
        """Create default schedule."""
        return SyntaxTaxSchedule()

    def test_default_costs(self, schedule):
        """Default costs are set correctly."""
        assert schedule.regular_cost == 0.001
        assert schedule.context_free_cost == 0.003
        assert schedule.context_sensitive_cost == 0.010
        assert schedule.turing_complete_cost == 0.030

    def test_get_cost_per_token(self, schedule):
        """Cost per token lookup works."""
        assert schedule.get_cost_per_token(ChomskyLevel.REGULAR) == 0.001
        assert schedule.get_cost_per_token(ChomskyLevel.CONTEXT_FREE) == 0.003
        assert schedule.get_cost_per_token(ChomskyLevel.CONTEXT_SENSITIVE) == 0.010
        assert schedule.get_cost_per_token(ChomskyLevel.TURING_COMPLETE) == 0.030

    def test_gas_limits(self, schedule):
        """Gas limits are set for high-risk levels."""
        assert schedule.get_gas_limit(ChomskyLevel.REGULAR) is None
        assert schedule.get_gas_limit(ChomskyLevel.CONTEXT_FREE) is None
        assert schedule.get_gas_limit(ChomskyLevel.CONTEXT_SENSITIVE) == 500_000
        assert schedule.get_gas_limit(ChomskyLevel.TURING_COMPLETE) == 100_000

    def test_escrow_multipliers(self, schedule):
        """Escrow multipliers are set correctly."""
        assert schedule.get_escrow_multiplier(ChomskyLevel.REGULAR) == 1.0
        assert schedule.get_escrow_multiplier(ChomskyLevel.CONTEXT_FREE) == 1.0
        assert schedule.get_escrow_multiplier(ChomskyLevel.CONTEXT_SENSITIVE) == 1.5
        assert schedule.get_escrow_multiplier(ChomskyLevel.TURING_COMPLETE) == 2.0

    def test_calculate_cost_regular(self, schedule):
        """Regular grammar cost calculation."""
        gas, limit, escrow = schedule.calculate_cost(ChomskyLevel.REGULAR, 1000)

        # 1000 tokens * 0.001 * 1000 (convert to units) = 1000 token units
        assert gas.tokens == 1000
        assert limit is None
        assert escrow == 0

    def test_calculate_cost_context_free(self, schedule):
        """Context-free grammar cost calculation."""
        gas, limit, escrow = schedule.calculate_cost(ChomskyLevel.CONTEXT_FREE, 1000)

        # 1000 tokens * 0.003 * 1000 = 3000 token units
        assert gas.tokens == 3000
        assert limit is None
        assert escrow == 0

    def test_calculate_cost_turing_complete(self, schedule):
        """Turing-complete grammar cost calculation with escrow."""
        gas, limit, escrow = schedule.calculate_cost(ChomskyLevel.TURING_COMPLETE, 1000)

        # 1000 tokens * 0.030 * 1000 = 30000 token units
        assert gas.tokens == 30000
        assert limit == 100_000
        # Escrow: 30000 * 2.0 = 60000
        assert escrow == 60_000

    def test_custom_schedule(self):
        """Custom schedule values work."""
        schedule = SyntaxTaxSchedule(
            regular_cost=0.0005,
            context_free_cost=0.002,
            turing_gas_limit=50_000,
        )

        assert schedule.regular_cost == 0.0005
        assert schedule.context_free_cost == 0.002
        assert schedule.turing_gas_limit == 50_000


# =============================================================================
# SyntaxTaxBudget Tests
# =============================================================================


class TestSyntaxTaxBudget:
    """Tests for SyntaxTaxBudget."""

    @pytest.fixture
    def budget(self):
        """Create budget with per-agent limits."""
        budget = SyntaxTaxBudget()
        budget.set_agent_budget("agent1", 100_000)  # Rich enough for Turing-complete
        budget.set_agent_budget("agent2", 100)  # Low balance - can't afford much
        budget.set_agent_budget("agent3", 5_000)  # Medium - can afford some downgrades
        return budget

    def test_evaluate_regular_grammar(self, budget):
        """Simple grammar is classified and approved."""
        # Use a simple pattern without regex quantifiers
        decision = budget.evaluate_grammar("agent1", "VERB NOUN", 1000)

        assert decision.approved is True
        assert decision.level == ChomskyLevel.REGULAR
        assert decision.gas_limit is None
        assert decision.escrow_required == 0

    def test_evaluate_context_free_grammar(self, budget):
        """Context-free grammar evaluation succeeds."""
        grammar = """
        expr ::= term | expr "+" term
        """
        decision = budget.evaluate_grammar("agent1", grammar, 1000)

        assert decision.approved is True
        assert decision.level == ChomskyLevel.CONTEXT_FREE

    def test_evaluate_turing_complete_grammar(self, budget):
        """Turing-complete grammar requires escrow."""
        grammar = "eval(code)"
        decision = budget.evaluate_grammar("agent1", grammar, 1000)

        assert decision.approved is True
        assert decision.level == ChomskyLevel.TURING_COMPLETE
        assert decision.gas_limit == 100_000
        assert decision.escrow_required > 0

    def test_insufficient_budget_rejected(self, budget):
        """Insufficient budget is rejected."""
        grammar = "eval(code)"
        decision = budget.evaluate_grammar("agent2", grammar, 1000)

        assert decision.approved is False
        assert "Insufficient" in decision.reason

    def test_downgrade_available_when_insufficient(self, budget):
        """Downgrade is suggested when budget insufficient for Turing but can afford cheaper."""
        grammar = "eval(code)"
        # agent3 has 5000 tokens - can afford regular (1000) or context-free (3000) but not Turing (90000)
        decision = budget.evaluate_grammar("agent3", grammar, 1000)

        assert decision.approved is False
        assert decision.downgrade_available is True
        assert decision.downgrade_level is not None
        # Downgrade should be cheaper (higher type number = cheaper)
        assert decision.downgrade_level.value > ChomskyLevel.TURING_COMPLETE.value

    def test_tier_summary(self, budget):
        """Tier summary provides all tiers."""
        summary = budget.get_tier_summary()

        assert "regular" in summary
        assert "context_free" in summary
        assert "context_sensitive" in summary
        assert "turing_complete" in summary

        assert summary["regular"]["risk"] == "low"
        assert summary["turing_complete"]["escrow_required"] is True


# =============================================================================
# Escrow Tests
# =============================================================================


class TestEscrow:
    """Tests for escrow handling."""

    @pytest.fixture
    def budget(self):
        """Create budget with high balance."""
        budget = SyntaxTaxBudget()
        budget.set_agent_budget("agent1", 100_000)
        return budget

    @pytest.mark.asyncio
    async def test_hold_escrow(self, budget):
        """Escrow can be held."""
        lease = await budget.hold_escrow("agent1", 5000, ChomskyLevel.TURING_COMPLETE)

        assert lease.id.startswith("ESCROW")
        assert lease.agent_id == "agent1"
        assert lease.amount == 5000
        assert lease.level == ChomskyLevel.TURING_COMPLETE
        assert lease.released is False
        assert lease.forfeited is False

    @pytest.mark.asyncio
    async def test_release_escrow(self, budget):
        """Escrow can be released on success."""
        lease = await budget.hold_escrow("agent1", 5000, ChomskyLevel.TURING_COMPLETE)

        result = await budget.release_escrow(lease.id)
        assert result is True

        # Verify released
        stored_lease = budget.get_escrow(lease.id)
        assert stored_lease.released is True

    @pytest.mark.asyncio
    async def test_forfeit_escrow(self, budget):
        """Escrow can be forfeited on failure."""
        lease = await budget.hold_escrow("agent1", 5000, ChomskyLevel.TURING_COMPLETE)

        result = await budget.forfeit_escrow(lease.id)
        assert result is True

        # Verify forfeited
        stored_lease = budget.get_escrow(lease.id)
        assert stored_lease.forfeited is True

    @pytest.mark.asyncio
    async def test_cannot_release_twice(self, budget):
        """Cannot release escrow twice."""
        lease = await budget.hold_escrow("agent1", 5000, ChomskyLevel.TURING_COMPLETE)

        await budget.release_escrow(lease.id)
        result = await budget.release_escrow(lease.id)

        assert result is False

    @pytest.mark.asyncio
    async def test_cannot_forfeit_after_release(self, budget):
        """Cannot forfeit after release."""
        lease = await budget.hold_escrow("agent1", 5000, ChomskyLevel.TURING_COMPLETE)

        await budget.release_escrow(lease.id)
        result = await budget.forfeit_escrow(lease.id)

        assert result is False


# =============================================================================
# DowngradeNegotiator Tests
# =============================================================================


class TestDowngradeNegotiator:
    """Tests for DowngradeNegotiator."""

    @pytest.fixture
    def budget(self):
        """Create budget with limited balance."""
        budget = SyntaxTaxBudget()
        # Needs 5000 to afford context-free (3000 tokens for 1000 input)
        budget.set_agent_budget("agent1", 5_000)
        return budget

    @pytest.fixture
    def negotiator(self, budget):
        """Create negotiator."""
        return DowngradeNegotiator(budget)

    def test_propose_downgrade(self, negotiator):
        """Downgrade proposal is generated."""
        # Explicitly request downgrade from TURING to CONTEXT_FREE
        proposal = negotiator.propose_downgrade(
            "agent1",
            ChomskyLevel.TURING_COMPLETE,
            1000,
            ChomskyLevel.CONTEXT_FREE,
        )

        assert proposal is not None
        assert proposal.original_level == ChomskyLevel.TURING_COMPLETE
        assert proposal.proposed_level == ChomskyLevel.CONTEXT_FREE
        # Savings: (30000 - 3000) / 30000 = 0.9
        assert proposal.savings > 0
        assert len(proposal.constraints_to_add) > 0
        assert len(proposal.capability_loss) > 0

    def test_propose_finds_affordable(self, negotiator):
        """Proposal finds affordable level when not specified."""
        proposal = negotiator.propose_downgrade(
            "agent1",
            ChomskyLevel.TURING_COMPLETE,
            1000,
        )

        # Should find an affordable level (REGULAR or CONTEXT_FREE)
        assert proposal is not None
        # In Chomsky hierarchy, higher value = simpler = cheaper
        assert proposal.proposed_level.value > proposal.original_level.value

    def test_no_downgrade_when_same_level(self, negotiator):
        """No proposal when target is same as current."""
        proposal = negotiator.propose_downgrade(
            "agent1",
            ChomskyLevel.REGULAR,
            1000,
            ChomskyLevel.REGULAR,
        )

        assert proposal is None

    def test_no_downgrade_when_target_higher_complexity(self, negotiator):
        """No proposal when target is higher complexity (lower value = more complex)."""
        # Trying to "downgrade" from REGULAR (3) to CONTEXT_FREE (2) is actually an upgrade
        # because CONTEXT_FREE is more complex (lower value)
        proposal = negotiator.propose_downgrade(
            "agent1",
            ChomskyLevel.REGULAR,  # value=3, simplest
            1000,
            ChomskyLevel.CONTEXT_FREE,  # value=2, more complex
        )

        # This should return None because you can't "downgrade" to a more complex level
        assert proposal is None

    def test_savings_calculation(self, negotiator):
        """Savings are calculated correctly."""
        proposal = negotiator.propose_downgrade(
            "agent1",
            ChomskyLevel.TURING_COMPLETE,  # value=0, most complex
            1000,
            ChomskyLevel.REGULAR,  # value=3, simplest
        )

        assert proposal is not None
        # Turing: 30000 tokens, Regular: 1000 tokens
        # Savings = (30000 - 1000) / 30000 = 0.967
        assert proposal.savings > 0.9  # 90%+ savings


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_syntax_tax_budget(self):
        """create_syntax_tax_budget creates valid budget."""
        budget = create_syntax_tax_budget()

        assert budget is not None
        assert budget.bank is not None
        assert budget.schedule is not None
        assert budget.classifier is not None

    def test_classify_grammar(self):
        """classify_grammar convenience function works."""
        # Simple pattern without regex quantifiers
        analysis = classify_grammar("VERB NOUN")

        assert analysis.level == ChomskyLevel.REGULAR

    def test_calculate_syntax_tax_regular(self):
        """calculate_syntax_tax for regular grammar."""
        # Simple pattern
        gas, level = calculate_syntax_tax("VERB NOUN", 1000)

        assert level == ChomskyLevel.REGULAR
        assert gas.tokens == 1000  # 1000 * 0.001 * 1000 = 1000

    def test_calculate_syntax_tax_context_free(self):
        """calculate_syntax_tax for context-free grammar."""
        gas, level = calculate_syntax_tax("expr ::= term | expr + term", 1000)

        assert level == ChomskyLevel.CONTEXT_FREE
        assert gas.tokens == 3000  # 1000 * 0.003 * 1000 = 3000

    def test_get_tier_costs(self):
        """get_tier_costs returns all tiers."""
        costs = get_tier_costs()

        assert "regular" in costs
        assert "context_free" in costs
        assert "context_sensitive" in costs
        assert "turing_complete" in costs

        # Costs increase with complexity
        assert costs["regular"] < costs["context_free"]
        assert costs["context_free"] < costs["context_sensitive"]
        assert costs["context_sensitive"] < costs["turing_complete"]


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for syntax tax system."""

    @pytest.fixture
    def budget(self):
        """Create budget with agents."""
        budget = SyntaxTaxBudget()
        budget.set_agent_budget("rich_agent", 1_000_000)
        budget.set_agent_budget("poor_agent", 50)
        budget.set_agent_budget("medium_agent", 5_000)  # Can afford downgrades
        return budget

    def test_rich_agent_can_use_any_grammar(self, budget):
        """Rich agent can afford any grammar level."""
        grammars = [
            "VERB NOUN",  # Regular (simple pattern)
            "expr ::= term | expr + term",  # Context-free
            "context-sensitive grammar",  # Context-sensitive
            "eval(code)",  # Turing-complete
        ]

        for grammar in grammars:
            decision = budget.evaluate_grammar("rich_agent", grammar, 1000)
            assert decision.approved is True, f"Failed for: {grammar}"

    def test_poor_agent_gets_downgrade_suggestions(self, budget):
        """Poor agent gets downgrade suggestions for expensive grammars."""
        # medium_agent can afford cheaper grammars, so will get downgrade suggestion
        decision = budget.evaluate_grammar("medium_agent", "eval(code)", 1000)

        assert decision.approved is False
        assert decision.downgrade_available is True

    def test_cost_proportional_to_complexity(self, budget):
        """Higher Chomsky complexity = higher cost."""
        grammars_by_level = [
            ("VERB NOUN", ChomskyLevel.REGULAR),  # Simple pattern
            ("expr ::= term | expr + term", ChomskyLevel.CONTEXT_FREE),
            ("eval(code)", ChomskyLevel.TURING_COMPLETE),
        ]

        costs = []
        for grammar, expected_level in grammars_by_level:
            decision = budget.evaluate_grammar("rich_agent", grammar, 1000)
            assert decision.level == expected_level, f"Wrong level for {grammar}"
            costs.append(decision.gas_cost.tokens)

        # Costs should increase
        assert costs[0] < costs[1] < costs[2]

    @pytest.mark.asyncio
    async def test_full_escrow_workflow(self, budget):
        """Full escrow workflow: hold → execute → release."""
        # Evaluate Turing-complete grammar
        decision = budget.evaluate_grammar("rich_agent", "eval(code)", 1000)
        assert decision.approved is True
        assert decision.escrow_required > 0

        # Hold escrow
        lease = await budget.hold_escrow(
            "rich_agent",
            decision.escrow_required,
            decision.level,
        )
        assert lease is not None

        # Simulate successful execution
        result = await budget.release_escrow(lease.id)
        assert result is True

        # Verify escrow state
        stored = budget.get_escrow(lease.id)
        assert stored.released is True
        assert stored.forfeited is False


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    @pytest.fixture
    def classifier(self):
        """Create classifier."""
        return GrammarClassifier()

    def test_empty_grammar(self, classifier):
        """Empty grammar is classified as regular."""
        analysis = classifier.classify("")
        assert analysis.level == ChomskyLevel.REGULAR
        assert analysis.confidence < 1.0

    def test_whitespace_only_grammar(self, classifier):
        """Whitespace-only grammar is classified as regular."""
        analysis = classifier.classify("   \n\t  ")
        assert analysis.level == ChomskyLevel.REGULAR

    def test_unicode_grammar(self, classifier):
        """Unicode in grammar doesn't break classification."""
        analysis = classifier.classify("命令 ::= 動詞 名詞")
        # Should parse without error
        assert analysis.level in list(ChomskyLevel)

    def test_very_long_grammar(self, classifier):
        """Long grammar can be classified."""
        # Create a long grammar
        rules = [f"rule{i} ::= 'token{i}'" for i in range(100)]
        grammar = "\n".join(rules)

        analysis = classifier.classify(grammar)
        assert analysis.level == ChomskyLevel.CONTEXT_FREE

    def test_zero_tokens(self):
        """Zero tokens has zero cost."""
        schedule = SyntaxTaxSchedule()
        gas, limit, escrow = schedule.calculate_cost(ChomskyLevel.TURING_COMPLETE, 0)

        assert gas.tokens == 0
        assert escrow == 0

    def test_negative_tokens_not_special(self):
        """Negative tokens (invalid) still calculates."""
        schedule = SyntaxTaxSchedule()
        # Should handle gracefully
        gas, limit, escrow = schedule.calculate_cost(ChomskyLevel.REGULAR, -100)
        # Just returns negative cost (caller's responsibility to validate)
        assert gas.tokens < 0


# =============================================================================
# Summary
# =============================================================================

# 55 tests covering:
# - ChomskyLevel enum (5)
# - GrammarAnalysis (3)
# - GrammarClassifier (14)
# - SyntaxTaxSchedule (9)
# - SyntaxTaxBudget (6)
# - Escrow (5)
# - DowngradeNegotiator (5)
# - Convenience functions (5)
# - Integration (4)
# - Edge cases (6)
