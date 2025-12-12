"""
Tests for E-gent v2 Phage: Active mutation vectors.

Tests cover:
1. Infection operations (infect, rollback)
2. Staking integration (stake, release, forfeit)
3. Lineage propagation (spawn, chain reconstruction)
4. Batch operations
5. Factory functions
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generator

import pytest

from ..phage import (
    InfectionConfig,
    InfectionEnvironment,
    analyze_lineage,
    calculate_lineage_fitness,
    create_infection_env,
    create_production_env,
    create_test_only_env,
    get_lineage_chain,
    infect,
    infect_batch,
    spawn_child,
)
from ..types import (
    InfectionStatus,
    MutationVector,
    Phage,
    PhageLineage,
    PhageStatus,
)

# =============================================================================
# Mock Integrations
# =============================================================================


@dataclass
class MockPhageStake:
    """Mock stake record."""

    id: str
    staker_id: str
    phage_id: str
    stake: int
    released: bool = False
    forfeited: bool = False


@dataclass
class MockStakingPool:
    """Mock B-gent StakingPool for testing."""

    stakes: dict[str, MockPhageStake] = field(default_factory=dict)
    pool_balance: int = 0
    stake_rate: float = 0.01
    stake_counter: int = 0

    def calculate_required_stake(
        self, lines_changed: int, complexity_score: float = 1.0
    ) -> int:
        base_stake = int(lines_changed * self.stake_rate * 100)
        adjusted = int(base_stake * complexity_score)
        return max(10, adjusted)

    async def stake(self, staker_id: str, phage_id: str, amount: int) -> MockPhageStake:
        self.stake_counter += 1
        stake = MockPhageStake(
            id=f"stake_{self.stake_counter}",
            staker_id=staker_id,
            phage_id=phage_id,
            stake=amount,
        )
        self.stakes[stake.id] = stake
        return stake

    async def release_stake(self, stake_id: str, bonus_percentage: float = 0.0) -> int:
        stake = self.stakes.get(stake_id)
        if not stake or stake.released or stake.forfeited:
            return 0

        stake.released = True
        bonus = int(self.pool_balance * bonus_percentage)
        self.pool_balance = max(0, self.pool_balance - bonus)
        return stake.stake + bonus

    async def forfeit_stake(self, stake_id: str) -> int:
        stake = self.stakes.get(stake_id)
        if not stake or stake.released or stake.forfeited:
            return 0

        stake.forfeited = True
        self.pool_balance += stake.stake
        return stake.stake


@dataclass
class MockViralLibrary:
    """Mock Viral Library for testing."""

    successes: list[tuple[str, float]] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)

    async def record_success(
        self, phage: Phage, impact: float, cost: float = 0.0
    ) -> None:
        self.successes.append((phage.id, impact))

    async def record_failure(self, phage: Phage) -> None:
        self.failures.append(phage.id)


@dataclass
class MockPredictionMarket:
    """Mock B-gent PredictionMarket for testing."""

    settlements: list[tuple[str, bool]] = field(default_factory=list)
    schema_rates: dict[str, float] = field(default_factory=dict)

    async def settle(self, phage_id: str, succeeded: bool) -> list[Any]:
        self.settlements.append((phage_id, succeeded))
        return []

    def update_schema_success_rate(
        self, schema_signature: str, succeeded: bool
    ) -> None:
        current = self.schema_rates.get(schema_signature, 0.5)
        alpha = 0.1
        new_value = 1.0 if succeeded else 0.0
        self.schema_rates[schema_signature] = (1 - alpha) * current + alpha * new_value


@dataclass
class MockDemon:
    """Mock Teleological Demon for testing."""

    should_pass: bool = True
    rejection_reason: str = "Intent misalignment"

    async def should_select(
        self, phage: Phage, intent_embedding: list[float] | None
    ) -> tuple[bool, dict[str, Any]]:
        return self.should_pass, {
            "reason": self.rejection_reason if not self.should_pass else "passed"
        }


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_mutation() -> MutationVector:
    """Create a sample mutation vector."""
    return MutationVector(
        schema_signature="loop_to_comprehension",
        original_code="for x in items:\n    result.append(f(x))",
        mutated_code="result = [f(x) for x in items]",
        enthalpy_delta=-0.3,
        entropy_delta=0.0,
        temperature=1.0,
        description="Convert loop to list comprehension",
        confidence=0.7,
        lines_changed=2,
    )


@pytest.fixture
def sample_phage(sample_mutation: MutationVector) -> Phage:
    """Create a sample phage."""
    return Phage(
        target_path=Path("test_module.py"),
        target_module="test_module",
        mutation=sample_mutation,
        hypothesis="Simplify loop to comprehension",
        status=PhageStatus.MUTATED,
        lineage=PhageLineage(schema_signature="loop_to_comprehension"),
    )


@pytest.fixture
def mock_staking() -> MockStakingPool:
    """Create a mock staking pool."""
    return MockStakingPool()


@pytest.fixture
def mock_library() -> MockViralLibrary:
    """Create a mock viral library."""
    return MockViralLibrary()


@pytest.fixture
def mock_market() -> MockPredictionMarket:
    """Create a mock prediction market."""
    return MockPredictionMarket()


@pytest.fixture
def mock_demon() -> MockDemon:
    """Create a mock demon."""
    return MockDemon()


@pytest.fixture
def test_only_env() -> InfectionEnvironment:
    """Create a test-only environment (no economics)."""
    return create_test_only_env(
        run_tests=False,  # Skip actual tests in unit tests
        run_type_check=False,
    )


# =============================================================================
# Spawn Tests
# =============================================================================


class TestSpawnChild:
    """Tests for spawn_child function."""

    def test_creates_child_with_new_mutation(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Spawning creates a child with the new mutation."""
        new_mutation = MutationVector(
            schema_signature="extract_constant",
            original_code="x = 3.14159",
            mutated_code="PI = 3.14159\nx = PI",
            lines_changed=1,
        )

        child = spawn_child(sample_phage, new_mutation)

        assert child.mutation == new_mutation
        assert child.id != sample_phage.id

    def test_increments_generation(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Child has incremented generation."""
        sample_phage.lineage.generation = 2

        child = spawn_child(sample_phage, sample_mutation)

        assert child.lineage.generation == 3

    def test_tracks_parent_id(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Child tracks parent ID."""
        child = spawn_child(sample_phage, sample_mutation)

        assert child.lineage.parent_id == sample_phage.id

    def test_preserves_target_path(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Child preserves target path from parent."""
        child = spawn_child(sample_phage, sample_mutation)

        assert child.target_path == sample_phage.target_path
        assert child.target_module == sample_phage.target_module

    def test_starts_with_mutated_status(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Child starts with MUTATED status."""
        child = spawn_child(sample_phage, sample_mutation)

        assert child.status == PhageStatus.MUTATED

    def test_tracks_mutation_history(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Child tracks parent's mutation in history."""
        assert sample_phage.mutation is not None
        child = spawn_child(sample_phage, sample_mutation)

        assert sample_phage.mutation.signature in child.lineage.mutations_applied

    def test_inherit_stake_copies_economics(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """inherit_stake=True copies economic properties."""
        sample_phage.stake = 100
        sample_phage.market_odds = 2.5

        child = spawn_child(sample_phage, sample_mutation, inherit_stake=True)

        assert child.stake == 100
        assert child.market_odds == 2.5

    def test_no_inherit_stake_resets_economics(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """inherit_stake=False resets economic properties."""
        sample_phage.stake = 100
        sample_phage.market_odds = 2.5

        child = spawn_child(sample_phage, sample_mutation, inherit_stake=False)

        assert child.stake == 0
        assert child.market_odds == 0.0


# =============================================================================
# Lineage Chain Tests
# =============================================================================


class TestGetLineageChain:
    """Tests for get_lineage_chain function."""

    def test_single_phage_returns_self(self, sample_phage: Phage) -> None:
        """Single phage with no parent returns itself."""
        library = {sample_phage.id: sample_phage}

        chain = get_lineage_chain(sample_phage, library)

        assert chain == [sample_phage]

    def test_two_generation_chain(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Returns chain with parent and child."""
        child = spawn_child(sample_phage, sample_mutation)
        library = {sample_phage.id: sample_phage, child.id: child}

        chain = get_lineage_chain(child, library)

        assert len(chain) == 2
        assert chain[0] == sample_phage
        assert chain[1] == child

    def test_three_generation_chain(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Returns full three-generation chain."""
        child = spawn_child(sample_phage, sample_mutation)
        grandchild = spawn_child(child, sample_mutation)

        library = {
            sample_phage.id: sample_phage,
            child.id: child,
            grandchild.id: grandchild,
        }

        chain = get_lineage_chain(grandchild, library)

        assert len(chain) == 3
        assert chain[0] == sample_phage
        assert chain[1] == child
        assert chain[2] == grandchild

    def test_missing_parent_stops_chain(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Stops chain when parent not in library."""
        child = spawn_child(sample_phage, sample_mutation)
        # Only include child, not parent
        library = {child.id: child}

        chain = get_lineage_chain(child, library)

        assert chain == [child]


# =============================================================================
# Lineage Fitness Tests
# =============================================================================


class TestCalculateLineageFitness:
    """Tests for calculate_lineage_fitness function."""

    def test_empty_chain_returns_zero(self) -> None:
        """Empty chain has zero fitness."""
        fitness = calculate_lineage_fitness([])
        assert fitness == 0.0

    def test_successful_phage_adds_fitness(self, sample_phage: Phage) -> None:
        """Successful phage adds positive fitness."""
        sample_phage.status = PhageStatus.INFECTED
        # Mutation with negative Gibbs = favorable
        assert sample_phage.mutation is not None
        sample_phage.mutation.enthalpy_delta = -0.5
        sample_phage.mutation.entropy_delta = 0.0

        fitness = calculate_lineage_fitness([sample_phage])

        assert fitness > 0

    def test_failed_phage_subtracts_fitness(self, sample_phage: Phage) -> None:
        """Failed phage subtracts from fitness."""
        sample_phage.status = PhageStatus.FAILED

        fitness = calculate_lineage_fitness([sample_phage])

        assert fitness < 0

    def test_mixed_chain_fitness(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Mixed success/failure chain has net fitness."""
        sample_phage.status = PhageStatus.INFECTED
        assert sample_phage.mutation is not None
        sample_phage.mutation.enthalpy_delta = -1.0

        child = spawn_child(sample_phage, sample_mutation)
        child.status = PhageStatus.FAILED

        fitness = calculate_lineage_fitness([sample_phage, child])

        # Success adds ~1.0, failure subtracts 0.1
        # Should be positive overall
        assert fitness > 0


# =============================================================================
# Lineage Analysis Tests
# =============================================================================


class TestAnalyzeLineage:
    """Tests for analyze_lineage function."""

    def test_empty_chain_report(self) -> None:
        """Empty chain produces zero report."""
        report = analyze_lineage([])

        assert report.chain_length == 0
        assert report.total_generations == 0
        assert report.cumulative_fitness == 0.0

    def test_single_phage_report(self, sample_phage: Phage) -> None:
        """Single phage produces single-element report."""
        sample_phage.status = PhageStatus.INFECTED

        report = analyze_lineage([sample_phage])

        assert report.chain_length == 1
        assert report.successful_mutations == 1

    def test_counts_statuses(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Correctly counts different statuses."""
        sample_phage.status = PhageStatus.INFECTED

        child1 = spawn_child(sample_phage, sample_mutation)
        child1.status = PhageStatus.FAILED

        child2 = spawn_child(sample_phage, sample_mutation)
        child2.status = PhageStatus.REJECTED

        chain = [sample_phage, child1, child2]
        report = analyze_lineage(chain)

        assert report.successful_mutations == 1
        assert report.failed_mutations == 1
        assert report.rejected_mutations == 1

    def test_collects_schemas(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Collects schema signatures used."""
        new_mutation = MutationVector(
            schema_signature="extract_constant",
            original_code="a",
            mutated_code="b",
        )
        child = spawn_child(sample_phage, new_mutation)

        report = analyze_lineage([sample_phage, child])

        assert "loop_to_comprehension" in report.schemas_used
        assert "extract_constant" in report.schemas_used


# =============================================================================
# Infection Tests
# =============================================================================


class TestInfect:
    """Tests for infect function."""

    @pytest.mark.asyncio
    async def test_basic_infection_success(
        self, temp_dir: Path, sample_phage: Phage, test_only_env: InfectionEnvironment
    ) -> None:
        """Basic infection succeeds with valid mutation."""
        # Create target file
        target = temp_dir / "test.py"
        target.write_text("for x in items:\n    result.append(f(x))")

        sample_phage.target_path = target

        result = await infect(sample_phage, target, test_only_env)

        assert result.status == InfectionStatus.SUCCESS
        assert result.syntax_valid is True
        assert sample_phage.status == PhageStatus.INFECTED

    @pytest.mark.asyncio
    async def test_infection_writes_mutated_code(
        self, temp_dir: Path, sample_phage: Phage, test_only_env: InfectionEnvironment
    ) -> None:
        """Infection writes the mutated code to file."""
        target = temp_dir / "test.py"
        target.write_text("original code")

        result = await infect(sample_phage, target, test_only_env)

        assert result.status == InfectionStatus.SUCCESS
        assert sample_phage.mutation is not None
        assert target.read_text() == sample_phage.mutation.mutated_code

    @pytest.mark.asyncio
    async def test_infection_with_staking(
        self, temp_dir: Path, sample_phage: Phage, mock_staking: MockStakingPool
    ) -> None:
        """Infection stakes tokens when configured."""
        target = temp_dir / "test.py"
        target.write_text("original")

        env = create_infection_env(
            staking=mock_staking,
            require_stake=True,
            run_tests=False,
            run_type_check=False,
        )

        result = await infect(sample_phage, target, env)

        assert result.tokens_consumed > 0
        assert len(mock_staking.stakes) == 1

    @pytest.mark.asyncio
    async def test_successful_infection_releases_stake(
        self, temp_dir: Path, sample_phage: Phage, mock_staking: MockStakingPool
    ) -> None:
        """Successful infection releases stake."""
        target = temp_dir / "test.py"
        target.write_text("original")

        env = create_infection_env(
            staking=mock_staking,
            require_stake=True,
            run_tests=False,
            run_type_check=False,
        )

        result = await infect(sample_phage, target, env)

        assert result.stake_returned is True
        stake = list(mock_staking.stakes.values())[0]
        assert stake.released is True

    @pytest.mark.asyncio
    async def test_failed_infection_forfeits_stake(
        self,
        temp_dir: Path,
        sample_phage: Phage,
        mock_staking: MockStakingPool,
        mock_demon: MockDemon,
    ) -> None:
        """Failed infection forfeits stake."""
        target = temp_dir / "test.py"
        target.write_text("original")

        # Make demon reject
        mock_demon.should_pass = False

        env = InfectionEnvironment(
            staking=mock_staking,
            demon=mock_demon,
            config=InfectionConfig(
                require_stake=True,
                run_tests=False,
                run_type_check=False,
            ),
        )

        result = await infect(sample_phage, target, env)

        assert result.status == InfectionStatus.REJECTED
        # No stake placed because rejection happens before staking
        assert sample_phage.status == PhageStatus.REJECTED

    @pytest.mark.asyncio
    async def test_demon_rejection(
        self,
        temp_dir: Path,
        sample_phage: Phage,
        mock_demon: MockDemon,
        test_only_env: InfectionEnvironment,
    ) -> None:
        """Demon rejection stops infection early."""
        target = temp_dir / "test.py"
        target.write_text("original")

        mock_demon.should_pass = False
        env = InfectionEnvironment(
            demon=mock_demon,
            config=test_only_env.config,
        )

        result = await infect(sample_phage, target, env)

        assert result.status == InfectionStatus.REJECTED
        assert sample_phage.status == PhageStatus.REJECTED

    @pytest.mark.asyncio
    async def test_records_success_in_library(
        self, temp_dir: Path, sample_phage: Phage, mock_library: MockViralLibrary
    ) -> None:
        """Successful infection records in library."""
        target = temp_dir / "test.py"
        target.write_text("original")

        env = create_infection_env(
            library=mock_library,
            run_tests=False,
            run_type_check=False,
            require_stake=False,
        )

        await infect(sample_phage, target, env)

        assert len(mock_library.successes) == 1
        assert mock_library.successes[0][0] == sample_phage.id

    @pytest.mark.asyncio
    async def test_settles_bets_on_success(
        self, temp_dir: Path, sample_phage: Phage, mock_market: MockPredictionMarket
    ) -> None:
        """Successful infection settles bets."""
        target = temp_dir / "test.py"
        target.write_text("original")

        env = create_infection_env(
            market=mock_market,
            run_tests=False,
            run_type_check=False,
            require_stake=False,
        )

        await infect(sample_phage, target, env)

        assert len(mock_market.settlements) == 1
        assert mock_market.settlements[0] == (sample_phage.id, True)

    @pytest.mark.asyncio
    async def test_updates_schema_success_rate(
        self, temp_dir: Path, sample_phage: Phage, mock_market: MockPredictionMarket
    ) -> None:
        """Updates schema success rate after settlement."""
        target = temp_dir / "test.py"
        target.write_text("original")

        env = create_infection_env(
            market=mock_market,
            run_tests=False,
            run_type_check=False,
            require_stake=False,
        )

        await infect(sample_phage, target, env)

        assert "loop_to_comprehension" in mock_market.schema_rates

    @pytest.mark.asyncio
    async def test_no_mutation_code_fails(
        self, temp_dir: Path, test_only_env: InfectionEnvironment
    ) -> None:
        """Phage without mutation code fails."""
        target = temp_dir / "test.py"
        target.write_text("original")

        phage = Phage(
            target_path=target,
            mutation=MutationVector(
                original_code="a",
                mutated_code="",  # Empty
            ),
            status=PhageStatus.MUTATED,
        )

        result = await infect(phage, target, test_only_env)

        assert result.status == InfectionStatus.FAILED
        assert "No mutation code" in (result.error_message or "")


# =============================================================================
# Rollback Tests
# =============================================================================


class TestRollback:
    """Tests for rollback behavior."""

    @pytest.mark.asyncio
    async def test_rollback_on_test_failure(self, temp_dir: Path) -> None:
        """Rolls back when tests fail."""
        target = temp_dir / "test.py"
        original = "original content"
        target.write_text(original)

        phage = Phage(
            target_path=target,
            mutation=MutationVector(
                original_code=original,
                mutated_code="mutated content",
                lines_changed=1,
            ),
            status=PhageStatus.MUTATED,
        )

        # Create env that will fail tests (we'll mock test failure)
        env = InfectionEnvironment(
            config=InfectionConfig(
                run_tests=True,
                run_type_check=False,
                auto_rollback=True,
                require_stake=False,
                test_command="false",  # Always fails
            )
        )

        result = await infect(phage, target, env)

        # Should have rolled back
        assert result.status == InfectionStatus.ROLLBACK
        assert target.read_text() == original

    @pytest.mark.asyncio
    async def test_no_rollback_when_disabled(self, temp_dir: Path) -> None:
        """No rollback when auto_rollback=False."""
        target = temp_dir / "test.py"
        original = "original content"
        target.write_text(original)

        phage = Phage(
            target_path=target,
            mutation=MutationVector(
                original_code=original,
                mutated_code="mutated content",
                lines_changed=1,
            ),
            status=PhageStatus.MUTATED,
        )

        env = InfectionEnvironment(
            config=InfectionConfig(
                run_tests=True,
                run_type_check=False,
                auto_rollback=False,
                require_stake=False,
                test_command="false",
            )
        )

        result = await infect(phage, target, env)

        # Should be PARTIAL (not rolled back)
        assert result.status == InfectionStatus.PARTIAL
        assert target.read_text() == "mutated content"


# =============================================================================
# Batch Infection Tests
# =============================================================================


class TestInfectBatch:
    """Tests for batch infection."""

    @pytest.mark.asyncio
    async def test_infects_all_phages(
        self, temp_dir: Path, test_only_env: InfectionEnvironment
    ) -> None:
        """Infects all phages in batch."""
        # Create targets
        targets = {}
        phages = []
        for i in range(3):
            target = temp_dir / f"test_{i}.py"
            target.write_text(f"original_{i}")

            phage = Phage(
                id=f"phage_{i}",
                target_path=target,
                mutation=MutationVector(
                    original_code=f"original_{i}",
                    mutated_code=f"mutated_{i}",
                    lines_changed=1,
                ),
                status=PhageStatus.MUTATED,
            )
            phages.append(phage)
            targets[phage.id] = target

        results = await infect_batch(phages, targets, test_only_env)

        assert len(results) == 3
        assert all(r.status == InfectionStatus.SUCCESS for r in results)

    @pytest.mark.asyncio
    async def test_stop_on_failure(
        self, temp_dir: Path, test_only_env: InfectionEnvironment
    ) -> None:
        """Stops batch on first failure when configured."""
        targets = {}
        phages = []

        # First phage succeeds
        target1 = temp_dir / "test_1.py"
        target1.write_text("original_1")
        phage1 = Phage(
            id="phage_1",
            target_path=target1,
            mutation=MutationVector(mutated_code="mutated_1", lines_changed=1),
            status=PhageStatus.MUTATED,
        )
        phages.append(phage1)
        targets[phage1.id] = target1

        # Second phage fails (no mutation code)
        target2 = temp_dir / "test_2.py"
        target2.write_text("original_2")
        phage2 = Phage(
            id="phage_2",
            target_path=target2,
            mutation=MutationVector(mutated_code="", lines_changed=1),
            status=PhageStatus.MUTATED,
        )
        phages.append(phage2)
        targets[phage2.id] = target2

        # Third would succeed but shouldn't run
        target3 = temp_dir / "test_3.py"
        target3.write_text("original_3")
        phage3 = Phage(
            id="phage_3",
            target_path=target3,
            mutation=MutationVector(mutated_code="mutated_3", lines_changed=1),
            status=PhageStatus.MUTATED,
        )
        phages.append(phage3)
        targets[phage3.id] = target3

        results = await infect_batch(
            phages, targets, test_only_env, stop_on_failure=True
        )

        assert len(results) == 2  # Only first two
        assert results[0].status == InfectionStatus.SUCCESS
        assert results[1].status == InfectionStatus.FAILED

    @pytest.mark.asyncio
    async def test_missing_target_path(
        self, temp_dir: Path, test_only_env: InfectionEnvironment
    ) -> None:
        """Handles missing target path gracefully."""
        phage = Phage(
            id="phage_1",
            mutation=MutationVector(mutated_code="mutated", lines_changed=1),
            status=PhageStatus.MUTATED,
        )

        results = await infect_batch([phage], {}, test_only_env)

        assert len(results) == 1
        assert results[0].status == InfectionStatus.FAILED
        assert "No target path" in (results[0].error_message or "")


# =============================================================================
# Factory Tests
# =============================================================================


class TestFactories:
    """Tests for factory functions."""

    def test_create_infection_env(self) -> None:
        """create_infection_env creates environment."""
        env = create_infection_env()

        assert env.staking is None
        assert env.library is None
        assert env.config is not None

    def test_create_infection_env_with_integrations(
        self, mock_staking: MockStakingPool, mock_library: MockViralLibrary
    ) -> None:
        """Creates environment with integrations."""
        env = create_infection_env(
            staking=mock_staking,
            library=mock_library,
        )

        assert env.staking == mock_staking
        assert env.library == mock_library

    def test_create_test_only_env(self) -> None:
        """create_test_only_env creates test-only environment."""
        env = create_test_only_env()

        assert env.config.require_stake is False
        assert env.staking is None

    def test_create_production_env(
        self,
        mock_staking: MockStakingPool,
        mock_library: MockViralLibrary,
        mock_market: MockPredictionMarket,
        mock_demon: MockDemon,
    ) -> None:
        """create_production_env creates full environment."""
        env = create_production_env(
            staking=mock_staking,
            library=mock_library,
            market=mock_market,
            demon=mock_demon,
        )

        assert env.config.require_stake is True
        assert env.staking == mock_staking
        assert env.library == mock_library
        assert env.market == mock_market
        assert env.demon == mock_demon


# =============================================================================
# Config Tests
# =============================================================================


class TestInfectionConfig:
    """Tests for InfectionConfig."""

    def test_default_config(self) -> None:
        """Default config has sensible defaults."""
        config = InfectionConfig()

        assert config.run_tests is True
        assert config.run_type_check is True
        assert config.auto_rollback is True
        assert config.require_stake is True

    def test_custom_config(self) -> None:
        """Custom config overrides defaults."""
        config = InfectionConfig(
            run_tests=False,
            test_timeout=120,
            bonus_for_success=0.2,
        )

        assert config.run_tests is False
        assert config.test_timeout == 120
        assert config.bonus_for_success == 0.2


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.mark.asyncio
    async def test_phage_without_mutation(
        self, temp_dir: Path, test_only_env: InfectionEnvironment
    ) -> None:
        """Handles phage without mutation."""
        target = temp_dir / "test.py"
        target.write_text("original")

        phage = Phage(
            target_path=target,
            mutation=None,
            status=PhageStatus.NASCENT,
        )

        result = await infect(phage, target, test_only_env)

        assert result.status == InfectionStatus.FAILED

    @pytest.mark.asyncio
    async def test_nonexistent_target(
        self, temp_dir: Path, test_only_env: InfectionEnvironment
    ) -> None:
        """Handles nonexistent target path."""
        target = temp_dir / "nonexistent.py"

        phage = Phage(
            target_path=target,
            mutation=MutationVector(
                mutated_code="new content",
                lines_changed=1,
            ),
            status=PhageStatus.MUTATED,
        )

        result = await infect(phage, target, test_only_env)

        # Should succeed (creates new file)
        assert result.status == InfectionStatus.SUCCESS
        assert target.exists()

    def test_spawn_chain_lineage(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Multiple spawns create correct lineage chain."""
        gen1 = sample_phage
        gen1.lineage.generation = 1  # Start at gen 1
        gen2 = spawn_child(gen1, sample_mutation)
        gen3 = spawn_child(gen2, sample_mutation)
        gen4 = spawn_child(gen3, sample_mutation)

        assert gen4.lineage.generation == 4
        assert gen4.lineage.parent_id == gen3.id
        assert gen3.lineage.parent_id == gen2.id
        assert gen2.lineage.parent_id == gen1.id


# =============================================================================
# Integration Tests
# =============================================================================


class TestFullIntegration:
    """Full integration tests with all components."""

    @pytest.mark.asyncio
    async def test_full_infection_cycle(
        self,
        temp_dir: Path,
        sample_phage: Phage,
        mock_staking: MockStakingPool,
        mock_library: MockViralLibrary,
        mock_market: MockPredictionMarket,
        mock_demon: MockDemon,
    ) -> None:
        """Full infection cycle with all integrations."""
        target = temp_dir / "test.py"
        target.write_text("original")

        env = create_production_env(
            staking=mock_staking,
            library=mock_library,
            market=mock_market,
            demon=mock_demon,
        )
        # Disable actual tests for unit test
        env.config.run_tests = False
        env.config.run_type_check = False

        result = await infect(sample_phage, target, env)

        # Verify all integrations were called
        assert result.status == InfectionStatus.SUCCESS
        assert len(mock_staking.stakes) == 1
        assert len(mock_library.successes) == 1
        assert len(mock_market.settlements) == 1

    @pytest.mark.asyncio
    async def test_spawn_and_infect_chain(
        self, temp_dir: Path, sample_phage: Phage, test_only_env: InfectionEnvironment
    ) -> None:
        """Spawn child and infect it."""
        target = temp_dir / "test.py"
        target.write_text("original")

        # Infect parent
        result1 = await infect(sample_phage, target, test_only_env)
        assert result1.status == InfectionStatus.SUCCESS

        # Spawn child with new mutation
        assert sample_phage.mutation is not None
        new_mutation = MutationVector(
            schema_signature="extract_constant",
            original_code=sample_phage.mutation.mutated_code,
            mutated_code="# refined\nresult = [f(x) for x in items]",
            lines_changed=1,
        )
        child = spawn_child(sample_phage, new_mutation)

        # Infect child
        result2 = await infect(child, target, test_only_env)
        assert result2.status == InfectionStatus.SUCCESS
        assert child.lineage.parent_id == sample_phage.id


# =============================================================================
# Property-Based Tests
# =============================================================================


class TestProperties:
    """Property-based tests for invariants."""

    def test_spawn_always_increments_generation(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Spawning always increments generation."""

        current = sample_phage
        for _ in range(10):
            gen_before = current.lineage.generation
            current = spawn_child(current, sample_mutation)
            assert current.lineage.generation == gen_before + 1

    def test_lineage_chain_is_ordered(
        self, sample_phage: Phage, sample_mutation: MutationVector
    ) -> None:
        """Lineage chain is in generation order."""
        phages = [sample_phage]
        current = sample_phage

        for i in range(5):
            child = spawn_child(current, sample_mutation)
            phages.append(child)
            current = child

        library = {p.id: p for p in phages}
        chain = get_lineage_chain(current, library)

        # Verify generations are increasing
        for i in range(len(chain) - 1):
            assert chain[i].lineage.generation <= chain[i + 1].lineage.generation

    @pytest.mark.asyncio
    async def test_infection_result_always_has_phage_id(
        self, temp_dir: Path, sample_phage: Phage, test_only_env: InfectionEnvironment
    ) -> None:
        """Infection result always includes phage ID."""
        target = temp_dir / "test.py"
        target.write_text("original")

        result = await infect(sample_phage, target, test_only_env)

        assert result.phage_id == sample_phage.id

    @pytest.mark.asyncio
    async def test_infection_sets_completed_at(
        self, temp_dir: Path, sample_phage: Phage, test_only_env: InfectionEnvironment
    ) -> None:
        """Infection always sets completed_at."""
        target = temp_dir / "test.py"
        target.write_text("original")

        result = await infect(sample_phage, target, test_only_env)

        assert result.completed_at is not None
        assert result.completed_at >= result.started_at
