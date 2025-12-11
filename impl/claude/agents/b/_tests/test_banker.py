"""
Tests for B-gent Phase 3: Banker Economics

Tests for:
- Value Tensor (multi-dimensional resource ontology)
- Metered Functor (economic transformation)
- Central Bank (token accounting)
- Universal Value Protocol (UVP)
- Value Ledger (transaction accounting)
"""

from datetime import datetime, timedelta

import pytest

# Metered Functor tests
from ..metered_functor import (
    Bid,
    CentralBank,
    Denial,
    DualBudget,
    EntropyBudget,
    Gas,
    Impact,
    InsufficientFundsError,
    Loan,
    SinkingFund,
    TokenBucket,
    TokenFuture,
    meter,
    priority_auction,
)

# Value Ledger tests
from ..value_ledger import (
    ComplexityOracle,
    EthicalRegulator,
    RoCMonitor,
    SimpleOutput,
    Treasury,
    ValueLedger,
    ValueOracle,
)

# Value Tensor tests
from ..value_tensor import (
    AntiDelusionChecker,
    EconomicDimension,
    EthicalDimension,
    ExchangeMatrix,
    ImpactTier,
    PhysicalDimension,
    SemanticDimension,
    TensorAlgebra,
    ValueTensor,
    create_standard_exchange_rates,
)

# =============================================================================
# Value Tensor Tests
# =============================================================================


class TestPhysicalDimension:
    """Tests for PhysicalDimension."""

    def test_creation(self):
        """Test basic creation."""
        phys = PhysicalDimension(
            input_tokens=100,
            output_tokens=200,
            wall_clock_ms=500.0,
            model_id="opus",
            cost_multiplier=15.0,
        )
        assert phys.total_tokens == 300
        assert phys.normalized_tokens == 4500.0  # 300 * 15

    def test_addition(self):
        """Test adding two physical dimensions."""
        a = PhysicalDimension(input_tokens=100, output_tokens=100)
        b = PhysicalDimension(input_tokens=50, output_tokens=50)
        c = a + b
        assert c.total_tokens == 300

    def test_default_values(self):
        """Test default initialization."""
        phys = PhysicalDimension()
        assert phys.total_tokens == 0
        assert phys.model_id == "unknown"
        assert phys.cost_multiplier == 1.0


class TestSemanticDimension:
    """Tests for SemanticDimension."""

    def test_quality_score(self):
        """Test quality score calculation."""
        sem = SemanticDimension(
            compression_ratio=0.3,
            input_alignment=0.8,
            domain_relevance=0.7,
            confidence=1.0,
        )
        # (1 - 0.3) * 0.3 + 0.8 * 0.4 + 0.7 * 0.3 = 0.21 + 0.32 + 0.21 = 0.74
        assert abs(sem.quality_score - 0.74) < 0.01

    def test_from_compression(self):
        """Test compression-based heuristic."""
        # Structured text compresses well
        structured = "def foo():\n    return 42\n" * 10
        sem = SemanticDimension.from_compression(structured)
        assert sem.compression_ratio < 0.5  # Should compress well
        assert sem.measurement_method == "compression_heuristic"

    def test_from_compression_empty(self):
        """Test empty text handling."""
        sem = SemanticDimension.from_compression("")
        assert sem.compression_ratio == 1.0
        assert sem.confidence == 0.1

    def test_from_validation(self):
        """Test validation-based heuristic."""
        validators = [
            lambda x: "def" in x,  # Has function
            lambda x: "return" in x,  # Has return
        ]
        code = "def foo():\n    return 42"
        sem = SemanticDimension.from_validation(code, validators)
        assert sem.kolmogorov_proxy == 1.0  # Both passed
        assert sem.confidence == 0.8


class TestEconomicDimension:
    """Tests for EconomicDimension."""

    def test_profit_calculation(self):
        """Test profit/loss calculation."""
        econ = EconomicDimension(
            gas_cost_usd=1.0,
            impact_value=2.0,
        )
        assert econ.profit_usd == 1.0
        assert econ.roc == 2.0

    def test_loss_scenario(self):
        """Test loss scenario."""
        econ = EconomicDimension(
            gas_cost_usd=2.0,
            impact_value=1.0,
        )
        assert econ.profit_usd == -1.0
        assert econ.roc == 0.5

    def test_impact_tiers(self):
        """Test impact tier values."""
        assert ImpactTier.SYNTACTIC.value == "syntactic"
        assert ImpactTier.DEPLOYMENT.value == "deployment"


class TestEthicalDimension:
    """Tests for EthicalDimension."""

    def test_sin_tax_high_risk(self):
        """Test sin tax with high security risk."""
        eth = EthicalDimension(security_risk=0.8)
        assert eth.sin_tax_multiplier < 0.5  # Should be penalized

    def test_virtue_subsidy(self):
        """Test virtue subsidy bonus."""
        eth = EthicalDimension(
            maintainability_improvement=0.5,
            test_coverage_improvement=0.5,
        )
        assert eth.virtue_subsidy_multiplier > 1.0

    def test_net_multiplier(self):
        """Test combined ethical multiplier."""
        eth = EthicalDimension()  # Default: no risks, no virtues
        assert 0.9 < eth.net_ethical_multiplier <= 1.0

    def test_license_violation_penalty(self):
        """Test license violation penalty."""
        eth = EthicalDimension(license_compliant=False)
        assert eth.net_ethical_multiplier == pytest.approx(0.2, rel=0.1)


class TestExchangeMatrix:
    """Tests for ExchangeMatrix."""

    def test_standard_rates(self):
        """Test standard exchange rates."""
        matrix = create_standard_exchange_rates()
        rate = matrix.get_rate("physical.tokens", "economic.gas_cost_usd")
        assert rate.rate > 0
        assert rate.confidence > 0.9

    def test_conversion(self):
        """Test value conversion."""
        matrix = create_standard_exchange_rates()
        converted, loss = matrix.convert(
            1000, "physical.tokens", "economic.gas_cost_usd"
        )
        assert converted > 0
        assert loss == 0  # Direct conversion, no loss

    def test_undefined_rate(self):
        """Test undefined rate handling."""
        matrix = ExchangeMatrix()
        rate = matrix.get_rate("foo", "bar")
        assert rate.confidence == 0.0  # Undefined


class TestAntiDelusionChecker:
    """Tests for AntiDelusionChecker."""

    def test_impact_quality_mismatch(self):
        """Test detection of high impact with low quality."""
        tensor = ValueTensor(
            semantic=SemanticDimension(
                compression_ratio=0.8,
                input_alignment=0.3,
                domain_relevance=0.3,
                confidence=1.0,
            ),
            economic=EconomicDimension(impact_value=600),
        )
        checker = AntiDelusionChecker()
        anomalies = checker.check_consistency(tensor)
        assert any(a.type == "impact_quality_mismatch" for a in anomalies)

    def test_suspicious_roc(self):
        """Test detection of suspicious RoC."""
        tensor = ValueTensor(
            economic=EconomicDimension(
                gas_cost_usd=1.0,
                impact_value=15.0,  # 15x RoC
            ),
        )
        checker = AntiDelusionChecker()
        anomalies = checker.check_consistency(tensor)
        assert any(a.type == "suspicious_roc" for a in anomalies)

    def test_free_lunch(self):
        """Test detection of free lunch."""
        tensor = ValueTensor(
            economic=EconomicDimension(
                gas_cost_usd=0.0,
                impact_value=100.0,
            ),
        )
        checker = AntiDelusionChecker()
        anomalies = checker.check_consistency(tensor)
        assert any(a.type == "free_lunch_detected" for a in anomalies)


class TestValueTensor:
    """Tests for ValueTensor."""

    def test_creation(self):
        """Test basic creation."""
        tensor = ValueTensor.initial()
        assert tensor.physical.total_tokens == 0
        assert tensor.economic.gas_cost_usd == 0.0

    def test_copy(self):
        """Test deep copy."""
        tensor = ValueTensor(
            physical=PhysicalDimension(input_tokens=100),
        )
        copied = tensor.copy()
        copied.physical.input_tokens = 200
        assert tensor.physical.input_tokens == 100

    def test_serialization(self):
        """Test to_dict/from_dict."""
        tensor = ValueTensor(
            physical=PhysicalDimension(input_tokens=100, output_tokens=200),
            economic=EconomicDimension(gas_cost_usd=0.5, impact_value=1.0),
        )
        data = tensor.to_dict()
        restored = ValueTensor.from_dict(data)
        assert restored.physical.input_tokens == 100
        assert restored.economic.gas_cost_usd == 0.5

    def test_validate(self):
        """Test validation."""
        tensor = ValueTensor.initial()
        anomalies = tensor.validate()
        assert isinstance(anomalies, list)

    def test_project_to_usd(self):
        """Test USD projection."""
        tensor = ValueTensor(
            economic=EconomicDimension(
                gas_cost_usd=1.0,
                impact_value=5.0,
            ),
            ethical=EthicalDimension(),  # Default multiplier ~1.0
        )
        usd = tensor.project_to_usd()
        assert usd > 0  # 5.0 * ~1.0 - 1.0 = ~4.0


class TestTensorAlgebra:
    """Tests for TensorAlgebra."""

    def test_add(self):
        """Test tensor addition."""
        a = ValueTensor(
            physical=PhysicalDimension(input_tokens=100),
            economic=EconomicDimension(gas_cost_usd=1.0),
        )
        b = ValueTensor(
            physical=PhysicalDimension(input_tokens=100),
            economic=EconomicDimension(gas_cost_usd=1.0),
        )
        c = TensorAlgebra.add(a, b)
        assert c.physical.input_tokens == 200
        assert c.economic.gas_cost_usd == 2.0

    def test_scale(self):
        """Test tensor scaling."""
        tensor = ValueTensor(
            physical=PhysicalDimension(input_tokens=100),
            economic=EconomicDimension(gas_cost_usd=1.0),
        )
        scaled = TensorAlgebra.scale(tensor, 2.0)
        assert scaled.physical.input_tokens == 200
        assert scaled.economic.gas_cost_usd == 2.0

    def test_project(self):
        """Test dimension projection."""
        tensor = ValueTensor(
            physical=PhysicalDimension(input_tokens=1000),
        )
        total, loss = TensorAlgebra.project(tensor, "physical.tokens")
        assert total > 0


# =============================================================================
# Metered Functor Tests
# =============================================================================


class TestGas:
    """Tests for Gas."""

    def test_cost_calculation(self):
        """Test cost calculation."""
        gas = Gas(tokens=1000, model_multiplier=1.0)
        assert gas.cost_usd == pytest.approx(0.01, rel=0.01)

    def test_addition(self):
        """Test gas addition."""
        a = Gas(tokens=100, time_ms=50)
        b = Gas(tokens=100, time_ms=50)
        c = a + b
        assert c.tokens == 200
        assert c.time_ms == 100


class TestImpact:
    """Tests for Impact."""

    def test_realized_value(self):
        """Test realized value with multipliers."""
        impact = Impact(
            base_value=100,
            multipliers={"bonus": 1.5, "penalty": 0.5},
        )
        assert impact.realized_value == 75.0  # 100 * 1.5 * 0.5


class TestTokenBucket:
    """Tests for TokenBucket."""

    def test_initial_balance(self):
        """Test initial balance."""
        bucket = TokenBucket(max_balance=1000, balance=1000)
        assert bucket.available == 1000

    def test_consume(self):
        """Test token consumption."""
        bucket = TokenBucket(max_balance=1000, balance=1000, refill_rate=0.0)
        assert bucket.consume(500)
        assert bucket.available == 500

    def test_insufficient_balance(self):
        """Test insufficient balance rejection."""
        bucket = TokenBucket(max_balance=100, balance=100, refill_rate=0.0)
        assert not bucket.consume(200)  # Should fail
        assert bucket.available == 100  # Balance unchanged

    def test_can_afford(self):
        """Test can_afford check."""
        bucket = TokenBucket(max_balance=100, balance=50, refill_rate=0.0)
        assert bucket.can_afford(50)
        assert not bucket.can_afford(51)


class TestSinkingFund:
    """Tests for SinkingFund."""

    def test_tax_collection(self):
        """Test tax collection."""
        fund = SinkingFund(tax_rate=0.01)
        remaining = fund.tax(1000)
        assert remaining == 990
        assert fund.reserve == 10

    def test_emergency_loan(self):
        """Test emergency loan."""
        fund = SinkingFund(reserve=100.0)
        result = fund.emergency_loan("agent1", 50)
        assert isinstance(result, Loan)
        assert result.amount == 50
        assert fund.reserve == 50.0

    def test_loan_denial(self):
        """Test loan denial."""
        fund = SinkingFund(reserve=10.0)
        result = fund.emergency_loan("agent1", 100)
        assert isinstance(result, Denial)

    def test_loan_repayment(self):
        """Test loan repayment."""
        fund = SinkingFund(reserve=100.0)
        loan = fund.emergency_loan("agent1", 50)
        assert isinstance(loan, Loan)
        remaining = fund.repay_loan(loan, 50)
        assert remaining == 0
        assert loan.repaid


class TestTokenFuture:
    """Tests for TokenFuture."""

    def test_validity(self):
        """Test validity check."""
        future = TokenFuture(
            reserved_tokens=1000,
            holder="agent1",
            expires_at=datetime.now() + timedelta(hours=1),
        )
        assert future.is_valid

    def test_expired(self):
        """Test expired future."""
        future = TokenFuture(
            reserved_tokens=1000,
            holder="agent1",
            expires_at=datetime.now() - timedelta(hours=1),
        )
        assert not future.is_valid


class TestPriorityAuction:
    """Tests for priority auction."""

    @pytest.mark.asyncio
    async def test_single_bidder(self):
        """Test auction with single bidder."""
        bids = [
            Bid(agent_id="a1", requested_tokens=100, confidence=0.8, criticality=0.9)
        ]
        allocations = await priority_auction(bids, 1000)
        assert len(allocations) == 1
        assert allocations[0].winner == "a1"
        assert allocations[0].clearing_price == 0.0  # No runner-up

    @pytest.mark.asyncio
    async def test_vickrey_pricing(self):
        """Test Vickrey (second-price) rule."""
        bids = [
            Bid(agent_id="a1", requested_tokens=100, confidence=0.9, criticality=0.9),
            Bid(agent_id="a2", requested_tokens=100, confidence=0.5, criticality=0.5),
        ]
        allocations = await priority_auction(bids, 1000)
        assert allocations[0].winner == "a1"
        assert allocations[0].clearing_price == 0.25  # a2's bid value

    @pytest.mark.asyncio
    async def test_limited_capacity(self):
        """Test limited capacity allocation."""
        bids = [
            Bid(agent_id="a1", requested_tokens=600, confidence=0.9, criticality=0.9),
            Bid(agent_id="a2", requested_tokens=600, confidence=0.5, criticality=0.5),
        ]
        allocations = await priority_auction(bids, 1000)
        # a1 gets 600, a2 gets 400 (remaining)
        assert allocations[0].tokens == 600
        assert allocations[1].tokens == 400


class TestCentralBank:
    """Tests for CentralBank."""

    @pytest.mark.asyncio
    async def test_authorize_and_settle(self):
        """Test authorization and settlement flow."""
        bank = CentralBank(max_balance=10000, refill_rate=0.0)
        lease = await bank.authorize("agent1", 1000)
        assert not lease.settled
        gas = await bank.settle(lease, 1000)
        assert lease.settled
        assert gas.tokens == 1000

    @pytest.mark.asyncio
    async def test_void_on_failure(self):
        """Test voiding on failure."""
        bank = CentralBank(max_balance=10000, refill_rate=0.0)
        lease = await bank.authorize("agent1", 1000)
        after_auth = bank.get_balance()
        await bank.void(lease)
        after_void = bank.get_balance()
        assert after_void > after_auth  # Tokens returned

    @pytest.mark.asyncio
    async def test_insufficient_funds(self):
        """Test insufficient funds error."""
        bank = CentralBank(max_balance=100, refill_rate=0.0)
        with pytest.raises(InsufficientFundsError):
            await bank.authorize("agent1", 200)


class TestDualBudget:
    """Tests for DualBudget."""

    def test_can_proceed(self):
        """Test can_proceed check."""
        budget = DualBudget(
            entropy=EntropyBudget(remaining=1.0),
            economic=TokenBucket(balance=1000, refill_rate=0.0),
        )
        assert budget.can_proceed(0.5, 500)
        assert not budget.can_proceed(2.0, 500)  # Entropy exceeded
        assert not budget.can_proceed(0.5, 2000)  # Economic exceeded

    def test_spend(self):
        """Test spending from both budgets."""
        budget = DualBudget(
            entropy=EntropyBudget(remaining=1.0),
            economic=TokenBucket(balance=1000, refill_rate=0.0),
        )
        assert budget.spend(0.5, 500)
        assert budget.entropy.remaining == 0.5
        assert budget.economic.available == 500


class TestMeteredFunctor:
    """Tests for Metered functor."""

    @pytest.mark.asyncio
    async def test_metered_invoke(self):
        """Test metered invocation."""

        class SimpleAgent:
            async def invoke(self, x: int) -> int:
                return x * 2

            def estimate_cost(self, x: int) -> int:
                return 100

        agent = SimpleAgent()
        bank = CentralBank(max_balance=10000, refill_rate=0.0)
        metered_agent = meter(agent, bank, "test_agent")

        receipt = await metered_agent.invoke(5)
        assert receipt.value == 10
        assert receipt.gas.tokens == 100

    @pytest.mark.asyncio
    async def test_metered_failure_rollback(self):
        """Test rollback on failure."""

        class FailingAgent:
            async def invoke(self, x: int) -> int:
                raise ValueError("Intentional failure")

            def estimate_cost(self, x: int) -> int:
                return 100

        agent = FailingAgent()
        bank = CentralBank(max_balance=10000, refill_rate=0.0)
        initial = bank.get_balance()
        metered_agent = meter(agent, bank, "test_agent")

        with pytest.raises(ValueError):
            await metered_agent.invoke(5)

        # Tokens should be returned
        final = bank.get_balance()
        assert final > initial - 100  # Some refund occurred


# =============================================================================
# Value Ledger Tests
# =============================================================================


class TestComplexityOracle:
    """Tests for ComplexityOracle."""

    def test_structured_text(self):
        """Test structured text assessment."""
        oracle = ComplexityOracle()
        # Repetitive, structured code
        code = "def foo():\n    return 42\n" * 20
        complexity = oracle.assess(code)
        assert complexity > 0.3  # Should detect structure

    def test_random_text(self):
        """Test random text assessment."""
        oracle = ComplexityOracle()
        import random
        import string

        random_text = "".join(random.choices(string.ascii_letters, k=500))
        complexity = oracle.assess(random_text)
        assert complexity < 0.3  # Random = low complexity (0.2-0.25 typical)

    def test_information_joule(self):
        """Test information joule calculation."""
        oracle = ComplexityOracle()
        code = "def foo():\n    return 42\n" * 10
        j_inf = oracle.information_joule(code, tokens_consumed=100)
        assert j_inf > 0


class TestValueOracle:
    """Tests for ValueOracle."""

    def test_syntactic_tier(self):
        """Test syntactic tier assignment."""
        oracle = ValueOracle()
        output = SimpleOutput(content="def foo(): pass", _valid_syntax=True)
        impact = oracle.calculate_impact(output)
        assert impact.base_value >= 10
        assert impact.tier == "syntactic"

    def test_functional_tier(self):
        """Test functional tier assignment."""
        oracle = ValueOracle()
        output = SimpleOutput(
            content="def foo(): pass",
            _valid_syntax=True,
            _tests_passed=True,
        )
        impact = oracle.calculate_impact(output)
        assert impact.base_value >= 100
        assert impact.tier == "functional"

    def test_sin_tax(self):
        """Test sin tax application."""
        oracle = ValueOracle()
        output = SimpleOutput(
            content="def foo(): pass",
            _valid_syntax=True,
            _has_vulns=True,
        )
        impact = oracle.calculate_impact(output)
        assert "sin_tax" in impact.multipliers
        assert impact.multipliers["sin_tax"] < 1.0


class TestEthicalRegulator:
    """Tests for EthicalRegulator."""

    def test_sin_tax_application(self):
        """Test sin tax application."""
        regulator = EthicalRegulator()
        base = Impact(base_value=100)
        adjusted = regulator.apply_adjustments(
            base, sins=["security_vulnerability"], virtues=[]
        )
        assert "sin:security_vulnerability" in adjusted.multipliers

    def test_virtue_subsidy_application(self):
        """Test virtue subsidy application."""
        regulator = EthicalRegulator()
        base = Impact(base_value=100)
        adjusted = regulator.apply_adjustments(base, sins=[], virtues=["added_tests"])
        assert "virtue:added_tests" in adjusted.multipliers
        assert adjusted.multipliers["virtue:added_tests"] > 1.0


class TestTreasury:
    """Tests for Treasury."""

    def test_gas_tracking(self):
        """Test gas tracking."""
        treasury = Treasury()
        treasury.deduct_gas("agent1", Gas(tokens=1000))
        assert treasury.get_gas_consumed("agent1") > 0
        assert treasury.get_transaction_count("agent1") == 1

    def test_impact_minting(self):
        """Test impact minting."""
        treasury = Treasury()
        treasury.mint_impact("agent1", 100.0)
        assert treasury.get_impact("agent1") == 100.0

    def test_debt_recording(self):
        """Test debt recording."""
        treasury = Treasury()
        treasury.record_debt("agent1", 50.0)
        assert treasury.get_debt("agent1") == 50.0


class TestValueLedger:
    """Tests for ValueLedger."""

    def test_log_profitable_transaction(self):
        """Test logging a profitable transaction."""
        ledger = ValueLedger()
        output = SimpleOutput(
            content="def foo(): pass" * 10,
            _valid_syntax=True,
            _tests_passed=True,
        )
        gas = Gas(tokens=100)  # Small cost
        receipt = ledger.log_transaction("agent1", gas, output)

        assert receipt.status == "profitable"
        assert receipt.roc > 1.0

    def test_log_debt_transaction(self):
        """Test logging a debt-incurring transaction."""
        ledger = ValueLedger()
        output = SimpleOutput(
            content="x",  # Tiny, low-value output
            _valid_syntax=False,
        )
        gas = Gas(tokens=10000, model_multiplier=15.0)  # High cost
        receipt = ledger.log_transaction("agent1", gas, output)

        assert receipt.status == "debt"

    def test_balance_sheet(self):
        """Test balance sheet generation."""
        ledger = ValueLedger()
        output = SimpleOutput(content="def foo(): pass", _valid_syntax=True)
        gas = Gas(tokens=100)
        ledger.log_transaction("agent1", gas, output)

        sheet = ledger.get_agent_balance_sheet("agent1")
        assert sheet.transaction_count == 1

    def test_system_stats(self):
        """Test system statistics."""
        ledger = ValueLedger()
        output = SimpleOutput(content="def foo(): pass", _valid_syntax=True)
        gas = Gas(tokens=100)
        ledger.log_transaction("agent1", gas, output)

        stats = ledger.get_system_stats()
        assert stats["total_transactions"] == 1


class TestRoCMonitor:
    """Tests for RoCMonitor."""

    def test_new_agent(self):
        """Test assessment of new agent."""
        ledger = ValueLedger()
        monitor = RoCMonitor(ledger)
        assessment = monitor.assess_agent("new_agent")
        assert assessment.status == "new"

    def test_profitable_agent(self):
        """Test assessment of profitable agent."""
        ledger = ValueLedger()
        output = SimpleOutput(
            content="def foo(): pass" * 10,
            _valid_syntax=True,
            _tests_passed=True,
        )
        gas = Gas(tokens=100)
        ledger.log_transaction("agent1", gas, output)

        monitor = RoCMonitor(ledger)
        assessment = monitor.assess_agent("agent1")
        assert assessment.status in ["profitable", "high_yield"]

    def test_leaderboard(self):
        """Test leaderboard generation."""
        ledger = ValueLedger()
        # Create some transactions
        for i in range(3):
            output = SimpleOutput(
                content=f"def foo{i}(): pass" * 10,
                _valid_syntax=True,
            )
            gas = Gas(tokens=100)
            ledger.log_transaction(f"agent{i}", gas, output)

        monitor = RoCMonitor(ledger)
        leaderboard = monitor.get_leaderboard(limit=10)
        assert len(leaderboard) == 3


# =============================================================================
# Integration Tests
# =============================================================================


class TestBankerIntegration:
    """Integration tests for the Banker economics system."""

    @pytest.mark.asyncio
    async def test_full_metered_workflow(self):
        """Test complete metered workflow with value tracking."""

        class ProductiveAgent:
            async def invoke(self, x: str) -> str:
                return f"def {x}():\n    return 42\n" * 10

            def estimate_cost(self, x: str) -> int:
                return 500

        agent = ProductiveAgent()
        bank = CentralBank(max_balance=100000, refill_rate=0.0)
        ledger = ValueLedger()

        metered_agent = meter(agent, bank, "productive_agent")
        receipt = await metered_agent.invoke("foo")

        # Log to ledger
        output = SimpleOutput(content=receipt.value, _valid_syntax=True)
        tx = ledger.log_transaction("productive_agent", receipt.gas, output)

        assert tx.tensor is not None
        assert tx.roc > 0

    @pytest.mark.asyncio
    async def test_budget_exhaustion(self):
        """Test behavior when budget is exhausted."""
        bank = CentralBank(max_balance=100, refill_rate=0.0)

        class ExpensiveAgent:
            async def invoke(self, x: int) -> int:
                return x

            def estimate_cost(self, x: int) -> int:
                return 200

        agent = ExpensiveAgent()
        metered_agent = meter(agent, bank, "expensive_agent")

        with pytest.raises(InsufficientFundsError):
            await metered_agent.invoke(1)

    def test_tensor_conservation_laws(self):
        """Test conservation law enforcement."""
        before = ValueTensor(
            physical=PhysicalDimension(input_tokens=100, wall_clock_ms=100),
            economic=EconomicDimension(gas_cost_usd=1.0),
        )

        # Valid transition
        after = ValueTensor(
            physical=PhysicalDimension(input_tokens=200, wall_clock_ms=200),
            economic=EconomicDimension(gas_cost_usd=2.0),
        )

        checker = AntiDelusionChecker()
        anomalies = checker.validate_transition(before, after)
        # Should have no critical violations
        critical = [a for a in anomalies if a.severity == "critical"]
        assert len(critical) == 0

    def test_ethical_multiplier_chain(self):
        """Test ethical multiplier through the full chain."""
        ledger = ValueLedger()

        # Good output with virtues
        output = SimpleOutput(
            content="def foo():\n    '''Documented function.'''\n    return 42\n" * 10,
            _valid_syntax=True,
            _tests_passed=True,
            _improved_maintainability=True,
        )
        gas = Gas(tokens=100)

        tx = ledger.log_transaction(
            "virtuous_agent",
            gas,
            output,
            virtues=["improved_readability", "added_tests"],
        )

        assert tx.tensor.ethical.net_ethical_multiplier > 1.0
        assert "virtue:improved_readability" in tx.impact.multipliers

    def test_dual_budget_enforcement(self):
        """Test dual budget (entropy + economic) enforcement."""
        budget = DualBudget(
            entropy=EntropyBudget(remaining=0.5),
            economic=TokenBucket(balance=1000, refill_rate=0.0),
        )

        # First operation: should succeed
        assert budget.spend(0.3, 300)

        # Second operation: entropy exhausted
        assert not budget.spend(0.3, 300)  # 0.3 > 0.2 remaining
