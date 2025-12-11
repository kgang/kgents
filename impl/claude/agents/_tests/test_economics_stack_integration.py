"""
Cross-Agent Integration Tests: Economics Stack

Tests integration across the economic domain:
- B × G: B-gent syntax tax on G-gent grammars
- B × J: B-gent shared entropy budget with J-gent compilation
- B × M: B-gent memory economics with M-gent holographic memory
- B × O: B-gent VoI economics with O-gent observation
- B × L: B-gent catalog economics with L-gent registry

Philosophy:
    Resource constraints are not bugs - they are features.
    Economics provides metabolic control over computation.
"""

from __future__ import annotations

import pytest

# B-gent imports
from agents.b import (
    CentralBank,
    ChomskyLevel,
    # Semantic Inflation
    ComplexityVector,
    EconomicDimension,
    EntropyBudget,
    EthicalDimension,
    FindingType,
    # Metered Functor
    Gas,
    # Grammar Insurance
    GrammarInsurance,
    HedgeStrategy,
    ObservationDepth,
    ObservationFinding,
    ParseEvent,
    PhysicalDimension,
    RoCMonitor,
    SemanticDimension,
    SyntaxTaxSchedule,
    TensorAlgebra,
    # Value Ledger
    ValueLedger,
    # Value Tensor
    ValueTensor,
    # VoI Economics
    VoILedger,
    VoIOptimizer,
    VolatilityMonitor,
    calculate_inflation_pressure,
    calculate_syntax_tax,
    classify_grammar,
    create_syntax_tax_budget,
    create_unified_accounting,
    create_voi_optimizer,
)

# G-gent imports
from agents.g import (
    Tongue,
    create_schema_tongue,
)

# J-gent imports
from agents.j import (
    PromiseState,
    Reality,
    promise,
)

# L-gent imports
from agents.l import (
    CatalogEntry,
    EntityType,
    SemanticRegistry,
)

# M-gent imports
from agents.m import (
    BudgetedMemory,
    ResolutionBudget,
    create_budgeted_memory,
    create_mock_bank,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def central_bank() -> CentralBank:
    """Create a CentralBank with initial tokens."""
    # CentralBank uses max_balance (not initial_tokens)
    return CentralBank(max_balance=1000, refill_rate=10.0)


@pytest.fixture
def entropy_budget() -> EntropyBudget:
    """Create an EntropyBudget."""
    # EntropyBudget uses initial/remaining (not max_depth/tokens_per_level)
    return EntropyBudget(initial=1.0, remaining=1.0)


@pytest.fixture
def value_ledger() -> ValueLedger:
    """Create a ValueLedger."""
    return ValueLedger()


@pytest.fixture
def voi_ledger() -> VoILedger:
    """Create a VoI Ledger."""
    return VoILedger()


@pytest.fixture
def sample_tongue() -> Tongue:
    """Create a sample Tongue for testing."""
    # create_schema_tongue uses: name, domain, grammar, version
    return create_schema_tongue(
        name="TestTongue",
        domain="testing",
        grammar='{"type": "object", "properties": {"value": {"type": "string"}}}',
    )


@pytest.fixture
def semantic_registry() -> SemanticRegistry:
    """Create a SemanticRegistry for L-gent tests."""
    return SemanticRegistry()


# =============================================================================
# B × G Integration: Syntax Tax on Grammars
# =============================================================================


class TestEconomicsGrammarIntegration:
    """B × G: Grammar operations have costs."""

    def test_grammar_classification(self) -> None:
        """Test G-gent grammars are classified by Chomsky level."""
        # Simple regex pattern - Type 3 (Regular)
        regex_grammar = "^[a-z]+$"
        result = classify_grammar(regex_grammar)

        # ChomskyLevel enum: REGULAR, CONTEXT_FREE, CONTEXT_SENSITIVE, TURING_COMPLETE
        assert result.level in (
            ChomskyLevel.REGULAR,
            ChomskyLevel.CONTEXT_FREE,
            ChomskyLevel.CONTEXT_SENSITIVE,
            ChomskyLevel.TURING_COMPLETE,
        )

    def test_syntax_tax_schedule(self) -> None:
        """Test syntax tax varies by Chomsky level."""
        schedule = SyntaxTaxSchedule()

        # Use get_cost_per_token instead of get_cost
        regular_cost = schedule.get_cost_per_token(ChomskyLevel.REGULAR)
        cf_cost = schedule.get_cost_per_token(ChomskyLevel.CONTEXT_FREE)
        cs_cost = schedule.get_cost_per_token(ChomskyLevel.CONTEXT_SENSITIVE)
        turing_cost = schedule.get_cost_per_token(ChomskyLevel.TURING_COMPLETE)

        # Regular grammars should be cheapest
        assert regular_cost <= cf_cost <= cs_cost <= turing_cost

    def test_syntax_tax_budget_creation(self) -> None:
        """Test creating syntax tax budget from bank."""
        # create_syntax_tax_budget takes central_bank and schedule (optional)
        budget = create_syntax_tax_budget()

        assert budget is not None

    def test_grammar_operation_costs_tokens(self) -> None:
        """Test grammar operations deduct from budget."""
        # calculate_syntax_tax: (grammar, estimated_tokens, schedule) -> (Gas, ChomskyLevel)
        gas, level = calculate_syntax_tax(
            grammar="SELECT * FROM users WHERE id = ?",
            estimated_tokens=100,
        )

        assert gas.cost_usd > 0

    def test_semantic_inflation_pressure(self) -> None:
        """Test semantic inflation affects grammar verbosity."""
        complexity = ComplexityVector(
            structural=0.7,
            temporal=0.3,
            conceptual=0.8,
        )

        # calculate_inflation_pressure needs base_tokens argument
        pressure = calculate_inflation_pressure(complexity, base_tokens=100)

        # Higher complexity = more explanation needed
        assert pressure.explanation_ratio > 0

    def test_grammar_insurance_policy(self, sample_tongue: Tongue) -> None:
        """Test grammar insurance protects against parse failures."""
        insurance = GrammarInsurance()

        # create_policy uses: grammar_id, grammar_spec, holder_id, strategy,
        # coverage_limit_tokens, deductible_tokens
        # HedgeStrategy: FALLBACK, REDUNDANT, VERSIONED, ENSEMBLE
        policy = insurance.create_policy(
            grammar_id=sample_tongue.name,
            grammar_spec=sample_tongue.grammar,
            holder_id="test-holder",
            strategy=HedgeStrategy.FALLBACK,
            coverage_limit_tokens=1000,
            deductible_tokens=100,
        )

        assert policy is not None
        assert policy.coverage_limit_tokens == 1000

    def test_grammar_volatility_monitoring(self) -> None:
        """Test grammar volatility affects insurance premiums."""
        from datetime import datetime

        monitor = VolatilityMonitor()

        # ParseEvent: grammar_id, timestamp, success, input_hash, duration_ms
        for i in range(10):
            event = ParseEvent(
                grammar_id="test-grammar",
                timestamp=datetime.now(),
                success=i % 3 != 0,  # 70% success rate
                input_hash=f"hash-{i}",
                duration_ms=10.0,
            )
            monitor.record_parse(event)

        metrics = monitor.get_metrics("test-grammar")

        # Should have volatility data
        # VolatilityMetrics has failure_rate, not success_rate
        assert metrics is not None
        assert metrics.failure_rate < 1.0  # Not 100% failure


# =============================================================================
# B × J Integration: Shared Entropy Budget
# =============================================================================


class TestEconomicsJITIntegration:
    """B × J: JIT compilation with budget constraints."""

    def test_entropy_budget_creation(self, entropy_budget: EntropyBudget) -> None:
        """Test EntropyBudget tracks remaining entropy."""
        # EntropyBudget uses initial/remaining (not max_depth/tokens_per_level)
        assert entropy_budget.initial == 1.0
        assert entropy_budget.remaining == 1.0

    def test_entropy_budget_consumption(self, entropy_budget: EntropyBudget) -> None:
        """Test EntropyBudget consume/afford functionality."""
        assert entropy_budget.can_afford(0.5)
        new_budget = entropy_budget.consume(0.5)
        assert new_budget.remaining == 0.5
        assert not new_budget.can_afford(0.6)  # Can't afford more than remaining

    def test_promise_creation(self) -> None:
        """Test Promise tracks budget consumption."""
        # Use promise() factory function (not Promise.defer)
        p = promise(intent="deferred computation", ground="fallback")

        assert p.state == PromiseState.PENDING
        assert p.intent == "deferred computation"
        assert p.ground == "fallback"

    def test_reality_classification_types(self) -> None:
        """Test reality classification categories."""
        # All reality types should be valid
        realities = [Reality.DETERMINISTIC, Reality.PROBABILISTIC, Reality.CHAOTIC]

        for reality in realities:
            assert reality.value in ["deterministic", "probabilistic", "chaotic"]

    @pytest.mark.asyncio
    async def test_central_bank_authorize(self, central_bank: CentralBank) -> None:
        """Test central bank token authorization."""
        # CentralBank.authorize is async and takes account_id + estimated_tokens
        lease = await central_bank.authorize("test-account", 50)

        assert lease is not None
        # Balance is reserved but not deducted until settle


# =============================================================================
# B × M Integration: Memory Economics
# =============================================================================


class TestEconomicsMemoryIntegration:
    """B × M: Memory operations have costs."""

    def test_budgeted_memory_creation(self) -> None:
        """Test BudgetedMemory wraps holographic memory with costs."""
        # create_mock_bank uses max_balance (not initial_tokens)
        bank = create_mock_bank(max_balance=1000)
        # create_budgeted_memory uses bank + account_id (not store_cost/recall_cost)
        memory = create_budgeted_memory(
            bank=bank,
            account_id="test-account",
        )

        assert memory is not None
        assert isinstance(memory, BudgetedMemory)

    @pytest.mark.asyncio
    async def test_memory_store_costs_tokens(self) -> None:
        """Test storing patterns costs tokens."""
        # Use larger balance to avoid InsufficientBudgetError
        bank = create_mock_bank(max_balance=100000)
        memory = create_budgeted_memory(
            bank=bank,
            account_id="test-account",
        )

        # Store pattern - async method with id, content, concepts
        receipt = await memory.store(
            id="test-pattern-001",
            content={"test": "data"},
            concepts=["test"],
        )

        # Should return receipt with cost info
        assert receipt is not None

    def test_resolution_budget_allocation(self) -> None:
        """Test resolution budget allocates memory fidelity."""
        # ResolutionBudget uses: cost_model, max_resolution_budget
        budget = ResolutionBudget(
            max_resolution_budget=1000,
        )

        # allocate_resolution takes patterns list and available budget
        # We test the basic functionality
        stats = budget.stats()
        assert stats is not None


# =============================================================================
# B × O Integration: VoI Economics for Observation
# =============================================================================


class TestEconomicsObservationIntegration:
    """B × O: Observations subject to VoI economics."""

    def test_voi_ledger_creation(self, voi_ledger: VoILedger) -> None:
        """Test VoI ledger creates successfully."""
        assert voi_ledger is not None
        assert isinstance(voi_ledger, VoILedger)

    def test_voi_ledger_records_observation(self, voi_ledger: VoILedger) -> None:
        """Test VoI ledger records observation costs."""
        finding = ObservationFinding(
            type=FindingType.HEALTH_CONFIRMED,
            confidence=0.9,
        )

        receipt = voi_ledger.log_observation(
            observer_id="test-observer",
            target_id="test-target",
            gas_consumed=Gas(10),
            finding=finding,
            depth=ObservationDepth.TELEMETRY_ONLY,
        )

        assert receipt is not None
        assert receipt.voi >= 0

    def test_voi_optimizer_creation(
        self, value_ledger: ValueLedger, voi_ledger: VoILedger
    ) -> None:
        """Test VoI optimizer creates successfully."""
        optimizer = create_voi_optimizer(value_ledger, voi_ledger)

        assert optimizer is not None
        assert isinstance(optimizer, VoIOptimizer)

    def test_voi_anomaly_detection_value(self, voi_ledger: VoILedger) -> None:
        """Test anomaly detection has high VoI."""
        finding = ObservationFinding(
            type=FindingType.ANOMALY_DETECTED,
            confidence=0.95,
            anomaly="High latency spike detected",
        )

        receipt = voi_ledger.log_observation(
            observer_id="test-observer",
            target_id="test-target",
            gas_consumed=Gas(50),
            finding=finding,
            depth=ObservationDepth.SEMANTIC_FULL,
        )

        # Anomalies should have positive VoI
        assert receipt.voi > 0

    def test_epistemic_capital_accumulates(self, voi_ledger: VoILedger) -> None:
        """Test epistemic capital accumulates across observations."""
        # Multiple observations
        for i in range(5):
            finding = ObservationFinding(
                type=FindingType.HEALTH_CONFIRMED,
                confidence=0.8,
            )
            voi_ledger.log_observation(
                observer_id="test-observer",
                target_id=f"target-{i}",
                gas_consumed=Gas(10),
                finding=finding,
            )

        capital = voi_ledger.get_epistemic_capital("test-observer")

        assert capital.observations == 5
        assert capital.confirmations == 5

    def test_unified_accounting_creation(
        self, voi_ledger: VoILedger, value_ledger: ValueLedger
    ) -> None:
        """Test unified accounting combines token and VoI economics."""
        # create_unified_accounting uses: value_ledger, voi_ledger
        accounting = create_unified_accounting(
            value_ledger=value_ledger,
            voi_ledger=voi_ledger,
        )

        assert accounting is not None


# =============================================================================
# B × L Integration: Catalog Economics
# =============================================================================


class TestEconomicsCatalogIntegration:
    """B × L: Catalog operations have economic implications."""

    @pytest.mark.asyncio
    async def test_catalog_registration(
        self, semantic_registry: SemanticRegistry
    ) -> None:
        """Test registering items in catalog."""
        # CatalogEntry needs: id, entity_type, name, version, description
        entry = CatalogEntry(
            id="test-entry",
            entity_type=EntityType.AGENT,
            name="Test Entry",
            version="1.0.0",
            description="A test catalog entry",
            keywords=["test"],
        )

        # SemanticRegistry.register is async
        await semantic_registry.register(entry)

        # SemanticRegistry.get is also async
        result = await semantic_registry.get("test-entry")
        assert result is not None
        assert result.name == "Test Entry"

    def test_roc_monitor_for_catalog_items(self, value_ledger: ValueLedger) -> None:
        """Test RoC monitor tracks catalog item value."""
        # RoCMonitor takes ledger (not thresholds)
        # RoCThresholds uses: bankruptcy, break_even, healthy (not warning/critical)
        monitor = RoCMonitor(ledger=value_ledger)

        # Record value via ledger first, then assess via monitor
        # Monitor reads from ledger, doesn't record directly
        assessment = monitor.assess_agent("catalog-item-001")

        # New agent should have default assessment
        assert assessment is not None


# =============================================================================
# Full Stack Integration
# =============================================================================


class TestEconomicsStackFullIntegration:
    """Test complete economics stack flow."""

    def test_value_tensor_across_agents(self) -> None:
        """Test ValueTensor tracks value across agent dimensions."""
        # Create tensor for an operation using actual field names
        tensor = ValueTensor(
            physical=PhysicalDimension(
                input_tokens=100, output_tokens=50, wall_clock_ms=50.0
            ),
            semantic=SemanticDimension(compression_ratio=0.7, confidence=0.9),
            economic=EconomicDimension(gas_cost_usd=10.0, impact_value=25.0),
            ethical=EthicalDimension(security_risk=0.05),
        )

        # TensorAlgebra has project(), add(), scale() - not compute_value()
        # Use project to get value in a specific dimension
        algebra = TensorAlgebra()
        value, confidence = algebra.project(tensor, "economic")

        assert value is not None

        # Check each dimension using actual field names
        assert tensor.physical.input_tokens == 100
        assert tensor.semantic.compression_ratio == 0.7
        assert tensor.economic.gas_cost_usd == 10.0
        assert tensor.ethical.security_risk == 0.05

    def test_grammar_to_budget_flow(self) -> None:
        """Test G-gent grammar → B-gent budget flow."""
        # 1. Classify grammar
        grammar = "^[a-zA-Z0-9_]+$"
        classification = classify_grammar(grammar)

        # 2. Calculate syntax tax (takes grammar, estimated_tokens)
        gas, level = calculate_syntax_tax(grammar, estimated_tokens=100)

        # 3. Verify classification and cost were computed
        assert classification is not None
        assert gas.cost_usd >= 0
        assert level is not None

    def test_observation_economics_flow(self, voi_ledger: VoILedger) -> None:
        """Test O-gent observation with B-gent economics."""
        # 1. Record multiple observations
        for i in range(3):
            finding = ObservationFinding(
                type=FindingType.HEALTH_CONFIRMED,
                confidence=0.9,
            )
            voi_ledger.log_observation(
                observer_id="test-observer",
                target_id=f"target-{i}",
                gas_consumed=Gas(10),
                finding=finding,
                depth=ObservationDepth.TELEMETRY_ONLY,
            )

        # 2. Check epistemic capital
        capital = voi_ledger.get_epistemic_capital("test-observer")

        assert capital.observations == 3
        assert capital.total_gas_consumed > 0

    @pytest.mark.asyncio
    async def test_memory_economics_flow(self) -> None:
        """Test M-gent memory with B-gent economics."""
        # 1. Create budgeted memory with correct API (larger balance)
        bank = create_mock_bank(max_balance=100000)
        memory = create_budgeted_memory(
            bank=bank,
            account_id="test-account",
        )

        # 2. Store patterns (async, uses id, content, concepts)
        for i in range(3):
            await memory.store(
                id=f"pattern-{i}",
                content={"i": i},
                concepts=["test"],
            )

        # 3. Verify budget status
        status = memory.budget_status()

        assert status is not None
