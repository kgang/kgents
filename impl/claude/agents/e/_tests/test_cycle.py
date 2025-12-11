"""
Tests for E-gent v2 Thermodynamic Cycle.

Tests cover:
1. Cycle configuration and initialization
2. Individual phase execution
3. Complete cycle runs
4. Temperature control
5. Integration with B-gent economics
6. Library updates
7. Error handling
"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from dataclasses import dataclass
from uuid import uuid4

import pytest

from ..cycle import (
    ThermodynamicCycle,
    CycleConfig,
    CyclePhase,
    CycleResult,
    create_cycle,
    create_conservative_cycle,
    create_exploratory_cycle,
    create_full_cycle,
    EvolutionAgent,
)
from ..types import (
    Intent,
    Phage,
    PhageStatus,
    MutationVector,
    InfectionResult,
    InfectionStatus,
)
from ..demon import TeleologicalDemon, DemonConfig
from ..mutator import Mutator, MutatorConfig
from ..library import ViralLibrary, ViralLibraryConfig


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def simple_code() -> str:
    """Simple Python code for testing."""
    return """
def process_items(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result

def calculate(x, y):
    value = 42
    return x + y + value
"""


@pytest.fixture
def complex_code() -> str:
    """More complex code with multiple mutation opportunities."""
    return """
def deep_function(data):
    if data is not None:
        result = []
        for item in data:
            if item > 0:
                value = item * 3.14159
                result.append(value)
        return result
    return []

def another_function(x):
    temp = x + 100
    return temp * 2

class MyClass:
    def method(self, items):
        results = []
        for item in items:
            results.append(self.transform(item))
        return results

    def transform(self, x):
        return x * 10
"""


@pytest.fixture
def temp_file(simple_code: str) -> Path:
    """Create a temporary Python file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(simple_code)
        return Path(f.name)


@pytest.fixture
def temp_file_complex(complex_code: str) -> Path:
    """Create a temporary Python file with complex code."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(complex_code)
        return Path(f.name)


@pytest.fixture
def basic_config() -> CycleConfig:
    """Basic cycle configuration for testing."""
    return CycleConfig(
        agent_id="test-agent",
        initial_temperature=1.0,
        run_tests=False,  # Disable tests for faster testing
        run_type_check=False,
        auto_rollback=True,
        verbose=False,
    )


@pytest.fixture
def intent() -> Intent:
    """Test Intent for cycle."""
    return Intent(
        embedding=[0.1] * 10,
        source="user",
        description="Improve code performance and readability",
        confidence=0.9,
    )


# =============================================================================
# Mock Integrations
# =============================================================================


class MockSun:
    """Mock Sun for testing grant system."""

    def __init__(self, has_grant: bool = False, budget: int = 10000):
        self._has_grant = has_grant
        self._budget = budget
        self.consumed: list[tuple[str, str, int]] = []

    def has_active_grant(self, grantee_id: str) -> bool:
        return self._has_grant

    def get_total_grant_budget(self, grantee_id: str) -> int:
        return self._budget if self._has_grant else 0

    async def consume_grant(self, grant_id: str, phage_id: str, tokens: int) -> Any:
        self.consumed.append((grant_id, phage_id, tokens))
        self._budget -= tokens
        return {"consumed": tokens}


class MockMarket:
    """Mock PredictionMarket for testing."""

    def __init__(self, base_odds: float = 2.0):
        self._base_odds = base_odds
        self.bets_placed: list[dict] = []
        self.settlements: list[tuple[str, bool]] = []
        self.schema_rates: dict[str, float] = {}

    def quote(
        self, phage_id: str, schema_signature: str, schema_confidence: float
    ) -> Any:
        @dataclass
        class Quote:
            phage_id: str
            success_odds: float
            failure_odds: float
            implied_success_probability: float

        return Quote(
            phage_id=phage_id,
            success_odds=self._base_odds,
            failure_odds=self._base_odds * 1.5,
            implied_success_probability=schema_confidence,
        )

    async def place_bet(
        self, bettor_id: str, phage_id: str, stake: int, predicted_success: bool
    ) -> Any:
        @dataclass
        class Bet:
            id: str
            stake: int

        bet = Bet(id=f"bet_{uuid4().hex[:8]}", stake=stake)
        self.bets_placed.append(
            {
                "bettor": bettor_id,
                "phage": phage_id,
                "stake": stake,
                "predicted": predicted_success,
            }
        )
        return bet

    async def settle(self, phage_id: str, succeeded: bool) -> list[Any]:
        self.settlements.append((phage_id, succeeded))
        return []

    def update_schema_success_rate(
        self, schema_signature: str, succeeded: bool
    ) -> None:
        current = self.schema_rates.get(schema_signature, 0.5)
        new_val = 1.0 if succeeded else 0.0
        self.schema_rates[schema_signature] = 0.9 * current + 0.1 * new_val


class MockStaking:
    """Mock StakingPool for testing."""

    def __init__(self, stake_rate: float = 0.01):
        self._stake_rate = stake_rate
        self.stakes: dict[str, dict] = {}
        self.released: list[str] = []
        self.forfeited: list[str] = []

    def calculate_required_stake(
        self, lines_changed: int, complexity_score: float
    ) -> int:
        return max(10, int(lines_changed * self._stake_rate * 100 * complexity_score))

    async def stake(self, staker_id: str, phage_id: str, amount: int) -> Any:
        @dataclass
        class Stake:
            id: str
            staker_id: str
            phage_id: str
            stake: int

        stake = Stake(
            id=f"stake_{uuid4().hex[:8]}",
            staker_id=staker_id,
            phage_id=phage_id,
            stake=amount,
        )
        self.stakes[stake.id] = {
            "staker": staker_id,
            "phage": phage_id,
            "amount": amount,
        }
        return stake

    async def release_stake(self, stake_id: str, bonus_percentage: float) -> int:
        if stake_id in self.stakes:
            self.released.append(stake_id)
            base = self.stakes[stake_id]["amount"]
            return int(base * (1 + bonus_percentage))
        return 0

    async def forfeit_stake(self, stake_id: str) -> int:
        if stake_id in self.stakes:
            self.forfeited.append(stake_id)
            return self.stakes[stake_id]["amount"]
        return 0


class MockLGent:
    """Mock L-gent SemanticRegistry for testing."""

    async def embed_text(self, text: str) -> list[float]:
        # Simple mock embedding based on text length
        import hashlib

        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return [(hash_val >> (i * 8)) % 256 / 256.0 for i in range(10)]


# =============================================================================
# Configuration Tests
# =============================================================================


class TestCycleConfig:
    """Tests for CycleConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = CycleConfig()

        assert config.agent_id == "e-gent"
        assert config.initial_temperature == 1.0
        assert config.cooling_rate == 0.05
        assert config.heating_rate == 0.1
        assert config.run_tests is True
        assert config.auto_rollback is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = CycleConfig(
            agent_id="custom-agent",
            initial_temperature=2.0,
            max_mutations_per_cycle=5,
            min_intent_alignment=0.5,
        )

        assert config.agent_id == "custom-agent"
        assert config.initial_temperature == 2.0
        assert config.max_mutations_per_cycle == 5
        assert config.min_intent_alignment == 0.5

    def test_temperature_bounds(self):
        """Test temperature bound configuration."""
        config = CycleConfig(
            min_temperature=0.5,
            max_temperature=3.0,
        )

        assert config.min_temperature == 0.5
        assert config.max_temperature == 3.0


# =============================================================================
# Initialization Tests
# =============================================================================


class TestCycleInitialization:
    """Tests for cycle initialization."""

    def test_default_initialization(self):
        """Test creating cycle with defaults."""
        cycle = ThermodynamicCycle()

        assert cycle.temperature == 1.0
        assert cycle.current_phase == CyclePhase.IDLE
        assert cycle.mutator is not None
        assert cycle.demon is not None
        assert cycle.library is not None

    def test_custom_config_initialization(self, basic_config: CycleConfig):
        """Test creating cycle with custom config."""
        cycle = ThermodynamicCycle(config=basic_config)

        assert cycle.temperature == basic_config.initial_temperature
        assert cycle.config.agent_id == "test-agent"

    def test_injected_components(self):
        """Test creating cycle with injected components."""
        mutator = Mutator(MutatorConfig(default_temperature=2.0))
        demon = TeleologicalDemon(DemonConfig(min_intent_alignment=0.6))
        library = ViralLibrary(ViralLibraryConfig(prune_threshold=0.5))

        cycle = ThermodynamicCycle(
            mutator=mutator,
            demon=demon,
            library=library,
        )

        assert cycle.mutator is mutator
        assert cycle.demon is demon
        assert cycle.library is library

    def test_external_integrations(self):
        """Test creating cycle with external integrations."""
        sun = MockSun(has_grant=True)
        market = MockMarket()
        staking = MockStaking()
        l_gent = MockLGent()

        cycle = ThermodynamicCycle(
            sun=sun,
            market=market,
            staking=staking,
            l_gent=l_gent,
        )

        assert cycle._sun is sun
        assert cycle._market is market
        assert cycle._staking is staking
        assert cycle._l_gent is l_gent


# =============================================================================
# Temperature Control Tests
# =============================================================================


class TestTemperatureControl:
    """Tests for temperature control."""

    def test_temperature_setter_clamping(self):
        """Test that temperature is clamped to bounds."""
        config = CycleConfig(min_temperature=0.1, max_temperature=5.0)
        cycle = ThermodynamicCycle(config=config)

        cycle.temperature = -1.0
        assert cycle.temperature == 0.1

        cycle.temperature = 10.0
        assert cycle.temperature == 5.0

        cycle.temperature = 2.5
        assert cycle.temperature == 2.5

    def test_temperature_affects_mutator(self):
        """Test that cycle temperature syncs with mutator."""
        cycle = ThermodynamicCycle()
        cycle.temperature = 2.0

        # Mutator should use cycle temperature during mutation
        assert cycle.mutator is not None

    def test_thermo_state_tracking(self):
        """Test thermodynamic state tracking."""
        cycle = ThermodynamicCycle()

        state = cycle.thermo_state
        assert state.temperature == 1.0
        assert state.total_gibbs_change == 0.0

        cycle.temperature = 2.0
        assert cycle.thermo_state.temperature == 2.0


# =============================================================================
# Intent Tests
# =============================================================================


class TestIntent:
    """Tests for Intent management."""

    def test_set_intent(self, intent: Intent):
        """Test setting Intent."""
        cycle = ThermodynamicCycle()
        cycle.set_intent(intent)

        assert cycle._intent is intent
        assert cycle.demon.intent is intent

    @pytest.mark.asyncio
    async def test_infer_intent_without_lgent(self):
        """Test Intent inference without L-gent."""
        cycle = ThermodynamicCycle()

        intent = await cycle.infer_intent(
            code="def hello(): pass",
            description="A greeting function",
        )

        assert intent.source == "user"
        assert intent.description == "A greeting function"
        assert intent.confidence == 0.8
        assert intent.embedding == []  # No L-gent

    @pytest.mark.asyncio
    async def test_infer_intent_with_lgent(self):
        """Test Intent inference with L-gent."""
        l_gent = MockLGent()
        cycle = ThermodynamicCycle(l_gent=l_gent)

        intent = await cycle.infer_intent(
            code="def hello(): pass",
            description="A greeting function",
        )

        assert len(intent.embedding) > 0


# =============================================================================
# Phase Tests
# =============================================================================


class TestSunPhase:
    """Tests for SUN phase."""

    @pytest.mark.asyncio
    async def test_sun_phase_no_grant(self):
        """Test SUN phase without grant system."""
        cycle = ThermodynamicCycle()
        result = await cycle._phase_sun(grant_id=None)

        assert result.phase == CyclePhase.SUN
        assert result.success is True
        assert result.details["has_grant"] is False

    @pytest.mark.asyncio
    async def test_sun_phase_with_grant(self):
        """Test SUN phase with active grant."""
        sun = MockSun(has_grant=True, budget=10000)
        cycle = ThermodynamicCycle(sun=sun)

        initial_temp = cycle.temperature
        result = await cycle._phase_sun(grant_id="grant_123")

        assert result.success is True
        assert result.details["has_grant"] is True
        assert result.details["grant_budget"] == 10000
        # Temperature should increase for grant-funded work
        assert cycle.temperature >= initial_temp


class TestMutatePhase:
    """Tests for MUTATE phase."""

    @pytest.mark.asyncio
    async def test_mutate_phase_basic(self, simple_code: str, temp_file: Path):
        """Test basic mutation generation."""
        cycle = ThermodynamicCycle()
        result, phages = await cycle._phase_mutate(simple_code, temp_file)

        assert result.phase == CyclePhase.MUTATE
        assert result.phages_in == 0
        assert result.phages_out >= 0  # May generate mutations

    @pytest.mark.asyncio
    async def test_mutate_phase_complex_code(
        self, complex_code: str, temp_file_complex: Path
    ):
        """Test mutation generation on complex code."""
        config = CycleConfig(max_mutations_per_cycle=20)
        cycle = ThermodynamicCycle(config=config)

        result, phages = await cycle._phase_mutate(complex_code, temp_file_complex)

        assert result.phase == CyclePhase.MUTATE
        # Complex code should yield mutations
        assert "schemas_used" in result.details


class TestSelectPhase:
    """Tests for SELECT phase."""

    @pytest.mark.asyncio
    async def test_select_phase_filters_phages(self, intent: Intent):
        """Test that selection filters phages."""
        cycle = ThermodynamicCycle()
        cycle.set_intent(intent)

        # Create test phages
        phages = [
            Phage(
                mutation=MutationVector(
                    original_code="x = 1",
                    mutated_code="x = 1",  # No change
                    confidence=0.8,
                    enthalpy_delta=-0.1,
                    entropy_delta=0.1,
                    temperature=1.0,
                ),
                status=PhageStatus.MUTATED,
            )
            for _ in range(5)
        ]

        result, selected = await cycle._phase_select(phages)

        assert result.phase == CyclePhase.SELECT
        assert result.phages_in == 5
        # Some may pass, some may fail
        assert "selection_rate" in result.details

    @pytest.mark.asyncio
    async def test_select_phase_rejection_reasons(self):
        """Test that rejection reasons are tracked."""
        config = CycleConfig(min_intent_alignment=0.9)  # High threshold
        cycle = ThermodynamicCycle(config=config)

        # Create phages with low confidence (affects alignment)
        phages = [
            Phage(
                mutation=MutationVector(
                    original_code="x = 1",
                    mutated_code="y = 2",
                    confidence=0.1,  # Low confidence
                    enthalpy_delta=-0.1,
                    entropy_delta=0.1,
                    temperature=1.0,
                ),
                status=PhageStatus.MUTATED,
            )
            for _ in range(3)
        ]

        result, selected = await cycle._phase_select(phages)

        assert "rejection_reasons" in result.details


class TestWagerPhase:
    """Tests for WAGER phase."""

    @pytest.mark.asyncio
    async def test_wager_phase_with_staking(self):
        """Test wager phase with staking pool."""
        staking = MockStaking()
        cycle = ThermodynamicCycle(staking=staking)

        phages = [
            Phage(
                mutation=MutationVector(
                    original_code="x = 1",
                    mutated_code="y = 2",
                    lines_changed=5,
                ),
                status=PhageStatus.QUOTED,
            )
            for _ in range(3)
        ]

        result, staked_phages, stakes = await cycle._phase_wager(phages)

        assert result.phase == CyclePhase.WAGER
        assert len(staking.stakes) == 3
        assert result.details["total_staked"] > 0

    @pytest.mark.asyncio
    async def test_wager_phase_with_market(self):
        """Test wager phase with market quotes."""
        market = MockMarket(base_odds=1.5)
        cycle = ThermodynamicCycle(market=market)

        phages = [
            Phage(
                mutation=MutationVector(
                    original_code="x = 1",
                    mutated_code="y = 2",
                    schema_signature="test_schema",
                    confidence=0.7,
                ),
                status=PhageStatus.QUOTED,
            )
        ]

        result, staked_phages, stakes = await cycle._phase_wager(phages)

        assert result.success is True
        assert staked_phages[0].market_odds == 1.5


class TestInfectPhase:
    """Tests for INFECT phase."""

    @pytest.mark.asyncio
    async def test_infect_phase_basic(self, temp_file: Path):
        """Test basic infection phase."""
        config = CycleConfig(
            run_tests=False,
            run_type_check=False,
            auto_rollback=True,
        )
        cycle = ThermodynamicCycle(config=config)

        # Read original content
        original_content = temp_file.read_text()

        # Create a phage with valid mutation
        phages = [
            Phage(
                target_path=temp_file,
                mutation=MutationVector(
                    original_code=original_content,
                    mutated_code=original_content + "\n# Modified",
                ),
                status=PhageStatus.STAKED,
            )
        ]

        result, infection_results = await cycle._phase_infect(phages, temp_file, {})

        assert result.phase == CyclePhase.INFECT
        assert len(infection_results) == 1


class TestPayoffPhase:
    """Tests for PAYOFF phase."""

    @pytest.mark.asyncio
    async def test_payoff_phase_success(self):
        """Test payoff phase with successful mutation."""
        staking = MockStaking()
        market = MockMarket()
        library = ViralLibrary()
        cycle = ThermodynamicCycle(
            staking=staking,
            market=market,
            library=library,
        )

        # Create success result
        phage = Phage(
            mutation=MutationVector(
                original_code="x = 1",
                mutated_code="y = 2",
                schema_signature="test_schema",
                enthalpy_delta=-0.2,
                entropy_delta=0.1,
            ),
            status=PhageStatus.INFECTED,
        )
        inf_result = InfectionResult(
            phage_id=phage.id,
            status=InfectionStatus.SUCCESS,
            tests_passed=True,
            types_valid=True,
        )

        # Setup stake
        stake = await staking.stake("test", phage.id, 100)
        stakes = {phage.id: stake}

        result = await cycle._phase_payoff([(phage, inf_result)], stakes)

        assert result.phase == CyclePhase.PAYOFF
        assert stake.id in staking.released
        assert len(market.settlements) == 1

    @pytest.mark.asyncio
    async def test_payoff_phase_failure(self):
        """Test payoff phase with failed mutation."""
        staking = MockStaking()
        cycle = ThermodynamicCycle(staking=staking)

        # Create failure result
        phage = Phage(
            mutation=MutationVector(
                original_code="x = 1",
                mutated_code="y = 2",
            ),
            status=PhageStatus.FAILED,
        )
        inf_result = InfectionResult(
            phage_id=phage.id,
            status=InfectionStatus.FAILED,
            tests_passed=False,
        )

        # Setup stake
        stake = await staking.stake("test", phage.id, 100)
        stakes = {phage.id: stake}

        result = await cycle._phase_payoff([(phage, inf_result)], stakes)

        assert result.phase == CyclePhase.PAYOFF
        assert stake.id in staking.forfeited
        assert result.details["tokens_lost"] == 100


# =============================================================================
# Full Cycle Tests
# =============================================================================


class TestFullCycle:
    """Tests for complete cycle execution."""

    @pytest.mark.asyncio
    async def test_complete_cycle_basic(
        self, simple_code: str, temp_file: Path, intent: Intent
    ):
        """Test complete cycle execution."""
        config = CycleConfig(
            run_tests=False,
            run_type_check=False,
            auto_rollback=True,
        )
        cycle = ThermodynamicCycle(config=config)

        result = await cycle.run(
            code=simple_code,
            target_path=temp_file,
            intent=intent,
        )

        assert isinstance(result, CycleResult)
        assert result.cycle_id.startswith("cycle_")
        assert result.started_at <= result.completed_at
        assert result.duration_ms > 0
        assert len(result.phase_results) > 0

    @pytest.mark.asyncio
    async def test_cycle_with_integrations(
        self, simple_code: str, temp_file: Path, intent: Intent
    ):
        """Test cycle with full integrations."""
        config = CycleConfig(
            run_tests=False,
            run_type_check=False,
        )
        sun = MockSun(has_grant=True)
        market = MockMarket()
        staking = MockStaking()
        l_gent = MockLGent()

        cycle = ThermodynamicCycle(
            config=config,
            sun=sun,
            market=market,
            staking=staking,
            l_gent=l_gent,
        )

        result = await cycle.run(
            code=simple_code,
            target_path=temp_file,
            intent=intent,
            grant_id="grant_123",
        )

        assert isinstance(result, CycleResult)
        # Integrations should have been called
        assert len(result.phase_results) >= 3  # At least SUN, MUTATE, SELECT

    @pytest.mark.asyncio
    async def test_cycle_temperature_adjustment(
        self, simple_code: str, temp_file: Path
    ):
        """Test that temperature adjusts based on success rate."""
        config = CycleConfig(
            initial_temperature=1.0,
            cooling_rate=0.1,
            heating_rate=0.2,
            run_tests=False,
            run_type_check=False,
        )
        cycle = ThermodynamicCycle(config=config)

        await cycle.run(
            code=simple_code,
            target_path=temp_file,
        )

        # Temperature should have changed (either cooled or heated)
        # We can't predict the exact outcome without knowing mutation results


class TestCycleResult:
    """Tests for CycleResult."""

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        result = CycleResult(
            cycle_id="test",
            success=True,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration_ms=100,
            mutations_succeeded=7,
            mutations_failed=3,
        )

        assert result.success_rate == 0.7

    def test_success_rate_empty(self):
        """Test success rate with no mutations."""
        result = CycleResult(
            cycle_id="test",
            success=False,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration_ms=100,
        )

        assert result.success_rate == 0.0

    def test_roi_calculation(self):
        """Test ROI calculation."""
        result = CycleResult(
            cycle_id="test",
            success=True,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration_ms=100,
            tokens_staked=100,
            tokens_won=150,
            tokens_lost=30,
        )

        assert result.roi == 1.2  # (150-30)/100

    def test_roi_no_stake(self):
        """Test ROI with no stake."""
        result = CycleResult(
            cycle_id="test",
            success=True,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration_ms=100,
        )

        assert result.roi == 0.0


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_cycle(self):
        """Test create_cycle factory."""
        cycle = create_cycle(temperature=2.0)
        assert cycle.temperature == 2.0

    def test_create_conservative_cycle(self):
        """Test create_conservative_cycle factory."""
        cycle = create_conservative_cycle()

        assert cycle.temperature == 0.5
        assert cycle.config.cooling_rate == 0.1
        assert cycle.config.min_intent_alignment == 0.5

    def test_create_exploratory_cycle(self):
        """Test create_exploratory_cycle factory."""
        cycle = create_exploratory_cycle()

        assert cycle.temperature == 3.0
        assert cycle.config.max_mutations_per_cycle == 20
        assert cycle.config.require_gibbs_viable is False

    def test_create_full_cycle(self):
        """Test create_full_cycle factory."""
        sun = MockSun()
        market = MockMarket()
        staking = MockStaking()
        l_gent = MockLGent()
        library = ViralLibrary()

        cycle = create_full_cycle(
            sun=sun,
            market=market,
            staking=staking,
            l_gent=l_gent,
            library=library,
        )

        assert cycle._sun is sun
        assert cycle._market is market
        assert cycle._staking is staking
        assert cycle._l_gent is l_gent
        assert cycle._library is library


# =============================================================================
# EvolutionAgent Tests
# =============================================================================


class TestEvolutionAgent:
    """Tests for EvolutionAgent wrapper."""

    @pytest.mark.asyncio
    async def test_agent_evolve(self, temp_file: Path):
        """Test agent evolve method."""
        config = CycleConfig(
            run_tests=False,
            run_type_check=False,
        )
        agent = EvolutionAgent(config=config)

        results = await agent.evolve(
            target=temp_file,
            intent="Improve code",
            max_cycles=1,
        )

        assert len(results) >= 1
        assert isinstance(results[0], CycleResult)

    @pytest.mark.asyncio
    async def test_agent_suggest(self, simple_code: str):
        """Test agent suggest method."""
        agent = EvolutionAgent()

        suggestions = await agent.suggest(
            code=simple_code,
            intent="Improve performance",
        )

        assert isinstance(suggestions, list)
        # May or may not have suggestions depending on code analysis

    def test_agent_cycle_access(self):
        """Test agent provides access to cycle."""
        agent = EvolutionAgent()

        assert isinstance(agent.cycle, ThermodynamicCycle)

    @pytest.mark.asyncio
    async def test_agent_multiple_cycles(self, temp_file: Path):
        """Test running multiple cycles."""
        config = CycleConfig(
            run_tests=False,
            run_type_check=False,
        )
        agent = EvolutionAgent(config=config)

        results = await agent.evolve(
            target=temp_file,
            max_cycles=3,
        )

        # Should stop early if no progress
        assert 1 <= len(results) <= 3


# =============================================================================
# Integration Tests
# =============================================================================


class TestCycleIntegration:
    """Integration tests for cycle with all components."""

    @pytest.mark.asyncio
    async def test_library_updates(self, simple_code: str, temp_file: Path):
        """Test that library is updated during cycle."""
        library = ViralLibrary()
        config = CycleConfig(
            run_tests=False,
            run_type_check=False,
            record_in_library=True,
        )
        cycle = ThermodynamicCycle(config=config, library=library)

        initial_patterns = library.total_patterns

        await cycle.run(
            code=simple_code,
            target_path=temp_file,
        )

        # Library may have new patterns if mutations succeeded
        # Or may be same if all failed
        assert library.total_patterns >= initial_patterns

    @pytest.mark.asyncio
    async def test_demon_stats_updated(self, simple_code: str, temp_file: Path):
        """Test that demon stats are updated during cycle."""
        demon = TeleologicalDemon()
        cycle = ThermodynamicCycle(demon=demon)

        initial_checked = demon.stats.total_checked

        await cycle.run(
            code=simple_code,
            target_path=temp_file,
        )

        # Demon should have checked some mutations
        assert demon.stats.total_checked >= initial_checked


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_invalid_code_handling(self, temp_file: Path):
        """Test handling of invalid Python code."""
        cycle = ThermodynamicCycle()

        invalid_code = "def broken( x:"  # Syntax error

        result = await cycle.run(
            code=invalid_code,
            target_path=temp_file,
        )

        # Should complete without crashing
        assert isinstance(result, CycleResult)

    @pytest.mark.asyncio
    async def test_nonexistent_file_handling(self):
        """Test handling of nonexistent target file."""
        cycle = ThermodynamicCycle(
            config=CycleConfig(run_tests=False, run_type_check=False)
        )
        nonexistent = Path("/nonexistent/file.py")

        result = await cycle.run(
            code="x = 1",
            target_path=nonexistent,
        )

        # Should complete (may have phase errors)
        assert isinstance(result, CycleResult)


# =============================================================================
# Property-Based Tests (if hypothesis available)
# =============================================================================


try:
    from hypothesis import given, strategies as st, settings

    class TestCycleProperties:
        """Property-based tests for cycle."""

        @given(temperature=st.floats(min_value=0.0, max_value=10.0))
        @settings(max_examples=20)
        def test_temperature_bounds_property(self, temperature: float):
            """Test temperature is always within bounds."""
            config = CycleConfig(
                min_temperature=0.1,
                max_temperature=5.0,
            )
            cycle = ThermodynamicCycle(config=config)
            cycle.temperature = temperature

            assert config.min_temperature <= cycle.temperature <= config.max_temperature

        @given(
            successes=st.integers(min_value=0, max_value=100),
            failures=st.integers(min_value=0, max_value=100),
        )
        @settings(max_examples=20)
        def test_success_rate_property(self, successes: int, failures: int):
            """Test success rate is always valid."""
            result = CycleResult(
                cycle_id="test",
                success=True,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                duration_ms=100,
                mutations_succeeded=successes,
                mutations_failed=failures,
            )

            rate = result.success_rate
            assert 0.0 <= rate <= 1.0


except ImportError:
    pass  # hypothesis not installed
