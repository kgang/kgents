"""
E-gent v2 Phage: Active mutation vectors with infection behavior.

The Phage class is elevated from a passive data object to an ACTIVE agent that:
1. infect(codebase): Apply mutation, run tests, rollback on failure
2. Staking integration: Use B-gent StakingPool for skin-in-the-game
3. Lineage propagation: Track evolutionary chains
4. spawn(): Create child phages from successful mutations

From spec/e-gents/thermodynamics.md:
> A Phage is NOT a passive experiment envelope.
> A Phage is an active mutation vector that can infect code,
> spawn offspring, and propagate its DNA through the library.

Spec Reference: spec/e-gents/thermodynamics.md
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

from .types import (
    InfectionResult,
    InfectionStatus,
    MutationVector,
    Phage,
    PhageStatus,
)

# =============================================================================
# Protocols for Integration
# =============================================================================


class StakingPoolProtocol(Protocol):
    """Protocol for B-gent StakingPool integration."""

    def calculate_required_stake(
        self, lines_changed: int, complexity_score: float
    ) -> int:
        """Calculate required stake for a mutation."""
        ...

    async def stake(self, staker_id: str, phage_id: str, amount: int) -> Any:
        """Stake tokens for a phage operation."""
        ...

    async def release_stake(self, stake_id: str, bonus_percentage: float) -> int:
        """Release stake after successful mutation."""
        ...

    async def forfeit_stake(self, stake_id: str) -> int:
        """Forfeit stake after failed mutation."""
        ...


class ViralLibraryProtocol(Protocol):
    """Protocol for Viral Library integration."""

    async def record_success(self, phage: Phage, impact: float, cost: float) -> Any:
        """Record a successful phage."""
        ...

    async def record_failure(self, phage: Phage) -> Any:
        """Record a failed phage."""
        ...


class PredictionMarketProtocol(Protocol):
    """Protocol for B-gent PredictionMarket integration."""

    async def settle(self, phage_id: str, succeeded: bool) -> list[Any]:
        """Settle all bets for a phage."""
        ...

    def update_schema_success_rate(
        self, schema_signature: str, succeeded: bool
    ) -> None:
        """Update historical success rate for a schema."""
        ...


class TeleologicalDemonProtocol(Protocol):
    """Protocol for Teleological Demon integration."""

    async def should_select(
        self, phage: Phage, intent_embedding: list[float] | None
    ) -> tuple[bool, dict[str, Any]]:
        """Check if phage should be selected."""
        ...


# =============================================================================
# Infection Configuration
# =============================================================================


@dataclass
class InfectionConfig:
    """Configuration for phage infection operations."""

    # Testing behavior
    run_tests: bool = True
    test_command: str = "pytest"
    test_timeout: int = 60  # seconds
    test_args: list[str] = field(default_factory=list)

    # Type checking behavior
    run_type_check: bool = True
    type_check_command: str = "mypy"
    type_check_args: list[str] = field(default_factory=list)

    # Rollback behavior
    auto_rollback: bool = True
    backup_before_infect: bool = True

    # Economics
    require_stake: bool = True
    bonus_for_success: float = 0.1  # 10% bonus from pool

    # Staker identity (who is staking for this infection)
    default_staker_id: str = "e-gent"


@dataclass
class InfectionEnvironment:
    """
    Environment for phage infection.

    Contains all the integrations needed for infection:
    - staking: B-gent StakingPool
    - library: Viral Library for recording outcomes
    - market: B-gent PredictionMarket for bet settlement
    - demon: Teleological Demon for pre-selection
    """

    staking: StakingPoolProtocol | None = None
    library: ViralLibraryProtocol | None = None
    market: PredictionMarketProtocol | None = None
    demon: TeleologicalDemonProtocol | None = None
    config: InfectionConfig = field(default_factory=InfectionConfig)


# =============================================================================
# Active Phage Operations
# =============================================================================


@dataclass
class StakeRecord:
    """Record of a stake placed for an infection."""

    stake_id: str
    phage_id: str
    amount: int
    staker_id: str


async def infect(
    phage: Phage,
    target_path: Path,
    env: InfectionEnvironment,
    intent_embedding: list[float] | None = None,
    staker_id: str | None = None,
) -> InfectionResult:
    """
    Apply a phage's mutation to a codebase.

    This is the core infection operation:
    1. Pre-selection check (Demon)
    2. Stake tokens (economics)
    3. Backup original code
    4. Apply mutation
    5. Run tests + type checks
    6. On success: keep mutation, release stake, record success
    7. On failure: rollback, forfeit stake, record failure
    8. Settle bets

    From spec:
    > infect() is the "moment of truth" for a phage.
    > Unlike dry-run experiments, infect() actually modifies code
    > and has economic consequences (stake at risk).

    Args:
        phage: The phage to infect with
        target_path: Path to the file to infect
        env: Infection environment (integrations)
        intent_embedding: Optional intent for demon check
        staker_id: ID of the staker (defaults to config)

    Returns:
        InfectionResult with full details
    """
    config = env.config
    staker = staker_id or config.default_staker_id
    start_time = datetime.now()

    result = InfectionResult(
        phage_id=phage.id,
        status=InfectionStatus.FAILED,
        started_at=start_time,
    )

    # Update phage status
    phage.status = PhageStatus.INFECTING

    # ---------------------------------------------------------------------
    # Phase 1: Pre-selection (Demon check)
    # ---------------------------------------------------------------------
    if env.demon:
        should_proceed, demon_report = await env.demon.should_select(
            phage, intent_embedding
        )
        if not should_proceed:
            phage.status = PhageStatus.REJECTED
            result.status = InfectionStatus.REJECTED
            result.error_message = f"Rejected by Demon: {demon_report}"
            result.completed_at = datetime.now()
            result.duration_ms = _elapsed_ms(start_time)
            return result

    # ---------------------------------------------------------------------
    # Phase 2: Stake tokens (economics)
    # ---------------------------------------------------------------------
    stake_record: StakeRecord | None = None

    if config.require_stake and env.staking and phage.mutation:
        try:
            required = env.staking.calculate_required_stake(
                lines_changed=phage.mutation.lines_changed,
                complexity_score=1.0,
            )

            stake = await env.staking.stake(
                staker_id=staker,
                phage_id=phage.id,
                amount=required,
            )

            stake_record = StakeRecord(
                stake_id=stake.id,
                phage_id=phage.id,
                amount=required,
                staker_id=staker,
            )

            phage.stake = required
            phage.status = PhageStatus.STAKED
            result.tokens_consumed = required

        except Exception as e:
            # Can't stake - abort
            phage.status = PhageStatus.FAILED
            phage.error = f"Staking failed: {e}"
            result.error_message = str(e)
            result.completed_at = datetime.now()
            result.duration_ms = _elapsed_ms(start_time)
            return result

    # ---------------------------------------------------------------------
    # Phase 3: Backup original code
    # ---------------------------------------------------------------------
    original_content: str | None = None
    backup_path: Path | None = None

    if config.backup_before_infect and target_path.exists():
        original_content = target_path.read_text()
        if config.auto_rollback:
            backup_path = target_path.with_suffix(target_path.suffix + ".bak")
            backup_path.write_text(original_content)

    # ---------------------------------------------------------------------
    # Phase 4: Apply mutation
    # ---------------------------------------------------------------------
    try:
        if phage.mutation and phage.mutation.mutated_code:
            target_path.write_text(phage.mutation.mutated_code)
            result.syntax_valid = True
        else:
            result.error_message = "No mutation code to apply"
            phage.status = PhageStatus.FAILED
            result.completed_at = datetime.now()
            result.duration_ms = _elapsed_ms(start_time)

            # Forfeit stake
            if stake_record and env.staking:
                await env.staking.forfeit_stake(stake_record.stake_id)
                result.stake_returned = False

            return result

    except Exception as e:
        result.error_message = f"Mutation application failed: {e}"
        phage.status = PhageStatus.FAILED
        result.completed_at = datetime.now()
        result.duration_ms = _elapsed_ms(start_time)

        # Forfeit stake
        if stake_record and env.staking:
            await env.staking.forfeit_stake(stake_record.stake_id)
            result.stake_returned = False

        return result

    # ---------------------------------------------------------------------
    # Phase 5: Run validation (tests + type checks)
    # ---------------------------------------------------------------------
    tests_passed = True
    types_valid = True

    # Run tests
    if config.run_tests:
        test_result = _run_tests(target_path, config)
        tests_passed = test_result["passed"]
        result.tests_passed = tests_passed
        result.test_count = test_result.get("total", 0)
        result.test_failures = test_result.get("failures", 0)

    # Run type check
    if config.run_type_check:
        type_result = _run_type_check(target_path, config)
        types_valid = type_result["valid"]
        result.types_valid = types_valid
        result.type_errors = type_result.get("errors", 0)

    # ---------------------------------------------------------------------
    # Phase 6: Handle outcome
    # ---------------------------------------------------------------------
    success = tests_passed and types_valid

    if success:
        # SUCCESS: Keep mutation, release stake, record success
        phage.status = PhageStatus.INFECTED
        phage.test_passed = True
        phage.type_check_passed = True
        result.status = InfectionStatus.SUCCESS

        # Release stake with bonus
        if stake_record and env.staking:
            await env.staking.release_stake(
                stake_record.stake_id,
                bonus_percentage=config.bonus_for_success,
            )
            result.stake_returned = True
            result.bet_won = True

        # Record success in library
        if env.library:
            # Calculate impact (simplified: based on test count and complexity reduction)
            impact = _calculate_impact(phage, result)
            await env.library.record_success(
                phage,
                impact=impact,
                cost=result.tokens_consumed,
            )

        # Clean up backup
        if backup_path and backup_path.exists():
            backup_path.unlink()

    else:
        # FAILURE: Rollback, forfeit stake, record failure
        if config.auto_rollback and original_content is not None:
            target_path.write_text(original_content)
            result.status = InfectionStatus.ROLLBACK
            result.rollback_reason = (
                "Tests failed" if not tests_passed else "Type check failed"
            )
        else:
            result.status = InfectionStatus.PARTIAL

        phage.status = PhageStatus.FAILED
        phage.test_passed = tests_passed
        phage.type_check_passed = types_valid

        # Forfeit stake
        if stake_record and env.staking:
            await env.staking.forfeit_stake(stake_record.stake_id)
            result.stake_returned = False
            result.bet_won = False

        # Record failure in library
        if env.library:
            await env.library.record_failure(phage)

        # Clean up backup
        if backup_path and backup_path.exists():
            backup_path.unlink()

    # ---------------------------------------------------------------------
    # Phase 7: Settle bets
    # ---------------------------------------------------------------------
    if env.market:
        await env.market.settle(phage.id, success)

        # Update schema success rate
        if phage.mutation:
            env.market.update_schema_success_rate(
                phage.mutation.schema_signature,
                success,
            )

    # Finalize
    phage.completed_at = datetime.now()
    phage.infection_result = result
    result.completed_at = datetime.now()
    result.duration_ms = _elapsed_ms(start_time)

    return result


def spawn_child(
    parent: Phage,
    mutation: MutationVector,
    inherit_stake: bool = False,
) -> Phage:
    """
    Spawn a child phage from a successful parent.

    Used for evolutionary chains where successful mutations
    lead to further refinements.

    From spec:
    > spawn() creates a child with:
    > - Parent's lineage (incremented generation)
    > - New mutation
    > - Fresh status (MUTATED)
    > - Optionally inherited economic properties

    Args:
        parent: The parent phage (should be successful)
        mutation: The new mutation for the child
        inherit_stake: Whether to inherit parent's stake level

    Returns:
        New child Phage with lineage tracking
    """
    child_lineage = parent.lineage.spawn_child(mutation.schema_signature)
    child_lineage.parent_id = parent.id

    # Track mutation history
    if parent.mutation:
        child_lineage.mutations_applied.append(parent.mutation.signature)

    child = Phage(
        target_path=parent.target_path,
        target_module=parent.target_module,
        mutation=mutation,
        hypothesis=f"Refinement of {parent.hypothesis}",
        status=PhageStatus.MUTATED,
        lineage=child_lineage,
    )

    # Optionally inherit economic properties
    if inherit_stake:
        child.market_odds = parent.market_odds
        child.stake = parent.stake

    return child


def get_lineage_chain(phage: Phage, library: dict[str, Phage]) -> list[Phage]:
    """
    Reconstruct the full lineage chain for a phage.

    Args:
        phage: The phage to trace lineage for
        library: Dictionary of phage_id → Phage for lookup

    Returns:
        List of phages from oldest ancestor to current
    """
    chain = [phage]
    current = phage

    while current.lineage.parent_id:
        parent_id = current.lineage.parent_id
        parent = library.get(parent_id)

        if parent is None:
            break  # Parent not in library

        chain.insert(0, parent)
        current = parent

    return chain


def calculate_lineage_fitness(chain: list[Phage]) -> float:
    """
    Calculate cumulative fitness across a lineage chain.

    Useful for evaluating evolutionary trajectories.

    Args:
        chain: List of phages in lineage order

    Returns:
        Cumulative fitness score
    """
    if not chain:
        return 0.0

    total_fitness = 0.0
    for phage in chain:
        if phage.status == PhageStatus.INFECTED:
            # Successful mutation adds fitness
            if phage.mutation:
                # Use Gibbs free energy as fitness proxy
                gibbs = phage.mutation.gibbs_free_energy
                # Negative Gibbs = favorable = positive fitness
                fitness = max(0, -gibbs)
                total_fitness += fitness
        elif phage.status in (PhageStatus.REJECTED, PhageStatus.FAILED):
            # Failed mutations subtract (penalty for dead ends)
            total_fitness -= 0.1

    return total_fitness


# =============================================================================
# Batch Operations
# =============================================================================


async def infect_batch(
    phages: list[Phage],
    target_paths: dict[str, Path],
    env: InfectionEnvironment,
    intent_embedding: list[float] | None = None,
    stop_on_failure: bool = False,
) -> list[InfectionResult]:
    """
    Infect multiple phages in sequence.

    Args:
        phages: List of phages to infect
        target_paths: Mapping of phage_id → target path
        env: Infection environment
        intent_embedding: Optional shared intent
        stop_on_failure: Stop batch on first failure

    Returns:
        List of InfectionResults
    """
    results = []

    for phage in phages:
        target = target_paths.get(phage.id)
        if target is None:
            # Skip if no target path
            results.append(
                InfectionResult(
                    phage_id=phage.id,
                    status=InfectionStatus.FAILED,
                    error_message="No target path provided",
                )
            )
            continue

        result = await infect(
            phage=phage,
            target_path=target,
            env=env,
            intent_embedding=intent_embedding,
        )
        results.append(result)

        if stop_on_failure and result.status != InfectionStatus.SUCCESS:
            break

    return results


# =============================================================================
# Lineage Analysis
# =============================================================================


@dataclass
class LineageReport:
    """Report on a phage lineage."""

    chain_length: int
    total_generations: int
    successful_mutations: int
    failed_mutations: int
    rejected_mutations: int
    cumulative_fitness: float
    schemas_used: list[str]
    oldest_ancestor_id: str | None
    youngest_descendant_id: str | None


def analyze_lineage(chain: list[Phage]) -> LineageReport:
    """
    Analyze a lineage chain.

    Args:
        chain: List of phages in lineage order

    Returns:
        LineageReport with statistics
    """
    if not chain:
        return LineageReport(
            chain_length=0,
            total_generations=0,
            successful_mutations=0,
            failed_mutations=0,
            rejected_mutations=0,
            cumulative_fitness=0.0,
            schemas_used=[],
            oldest_ancestor_id=None,
            youngest_descendant_id=None,
        )

    successful = sum(1 for p in chain if p.status == PhageStatus.INFECTED)
    failed = sum(1 for p in chain if p.status == PhageStatus.FAILED)
    rejected = sum(1 for p in chain if p.status == PhageStatus.REJECTED)

    schemas = []
    for p in chain:
        if p.mutation and p.mutation.schema_signature:
            schemas.append(p.mutation.schema_signature)

    max_gen = max(p.lineage.generation for p in chain)

    return LineageReport(
        chain_length=len(chain),
        total_generations=max_gen,
        successful_mutations=successful,
        failed_mutations=failed,
        rejected_mutations=rejected,
        cumulative_fitness=calculate_lineage_fitness(chain),
        schemas_used=schemas,
        oldest_ancestor_id=chain[0].id if chain else None,
        youngest_descendant_id=chain[-1].id if chain else None,
    )


# =============================================================================
# Internal Helpers
# =============================================================================


def _elapsed_ms(start: datetime) -> float:
    """Calculate elapsed milliseconds since start."""
    return (datetime.now() - start).total_seconds() * 1000


def _run_tests(target_path: Path, config: InfectionConfig) -> dict[str, Any]:
    """
    Run tests for a target path.

    Returns:
        Dict with 'passed', 'total', 'failures'
    """
    try:
        cmd = [config.test_command]
        cmd.extend(config.test_args)
        cmd.append(str(target_path.parent))

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config.test_timeout,
            cwd=target_path.parent,
        )

        # Parse pytest output (simplified)
        passed = result.returncode == 0
        total = 0
        failures = 0

        # Try to extract counts from output
        for line in result.stdout.split("\n"):
            if "passed" in line.lower():
                try:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p == "passed":
                            total += int(parts[i - 1])
                        if p == "failed":
                            failures += int(parts[i - 1])
                except (ValueError, IndexError):
                    pass

        return {
            "passed": passed,
            "total": max(total, 1 if passed else 0),
            "failures": failures,
            "output": result.stdout[:1000],
        }

    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "total": 0,
            "failures": 1,
            "output": "Test timeout",
        }
    except Exception as e:
        return {
            "passed": False,
            "total": 0,
            "failures": 1,
            "output": str(e),
        }


def _run_type_check(target_path: Path, config: InfectionConfig) -> dict[str, Any]:
    """
    Run type checking for a target path.

    Returns:
        Dict with 'valid', 'errors'
    """
    try:
        cmd = [config.type_check_command]
        cmd.extend(config.type_check_args)
        cmd.append(str(target_path))

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=target_path.parent,
        )

        valid = result.returncode == 0

        # Count errors (simplified)
        errors = 0
        for line in result.stdout.split("\n"):
            if "error:" in line.lower():
                errors += 1

        return {
            "valid": valid,
            "errors": errors,
            "output": result.stdout[:1000],
        }

    except subprocess.TimeoutExpired:
        return {"valid": False, "errors": 1, "output": "Type check timeout"}
    except FileNotFoundError:
        # Type checker not installed - pass
        return {"valid": True, "errors": 0, "output": "Type checker not found"}
    except Exception as e:
        return {"valid": False, "errors": 1, "output": str(e)}


def _calculate_impact(phage: Phage, result: InfectionResult) -> float:
    """
    Calculate the impact of a successful mutation.

    Impact is a measure of how beneficial the mutation was.
    Higher impact = better pattern for the library.

    From spec:
    > impact = test_improvement + complexity_reduction + intent_alignment
    """
    impact = 0.0

    # Base impact from test success
    if result.tests_passed:
        impact += 0.5

    # Bonus for test count (mutation affects more code)
    if result.test_count > 0:
        impact += min(0.3, result.test_count * 0.01)

    # Bonus for type safety
    if result.types_valid:
        impact += 0.2

    # Bonus from Gibbs free energy (favorable thermodynamics)
    if phage.mutation:
        gibbs = phage.mutation.gibbs_free_energy
        if gibbs < 0:
            # More negative = more favorable
            impact += min(0.5, abs(gibbs) * 0.5)

    # Bonus for intent alignment
    if phage.intent_alignment > 0.7:
        impact += 0.3 * phage.intent_alignment

    return impact


# =============================================================================
# Factory Functions
# =============================================================================


def create_infection_env(
    staking: StakingPoolProtocol | None = None,
    library: ViralLibraryProtocol | None = None,
    market: PredictionMarketProtocol | None = None,
    demon: TeleologicalDemonProtocol | None = None,
    **config_kwargs: Any,
) -> InfectionEnvironment:
    """
    Create an infection environment with the given integrations.

    Args:
        staking: B-gent StakingPool
        library: Viral Library
        market: B-gent PredictionMarket
        demon: Teleological Demon
        **config_kwargs: Additional config options

    Returns:
        InfectionEnvironment
    """
    config = InfectionConfig(**config_kwargs) if config_kwargs else InfectionConfig()

    return InfectionEnvironment(
        staking=staking,
        library=library,
        market=market,
        demon=demon,
        config=config,
    )


def create_test_only_env(**config_kwargs: Any) -> InfectionEnvironment:
    """
    Create an environment for test-only infections (no economics).

    Useful for dry-run testing without staking.
    """
    # Set defaults that can be overridden
    defaults: dict[str, Any] = {
        "require_stake": False,
        "run_tests": True,
        "run_type_check": True,
        "auto_rollback": True,
    }
    # Override defaults with provided kwargs
    defaults.update(config_kwargs)
    config = InfectionConfig(**defaults)
    return InfectionEnvironment(config=config)


def create_production_env(
    staking: StakingPoolProtocol,
    library: ViralLibraryProtocol,
    market: PredictionMarketProtocol,
    demon: TeleologicalDemonProtocol,
) -> InfectionEnvironment:
    """
    Create a full production environment with all integrations.

    This is the "real" environment where:
    - Stakes are required
    - Tests must pass
    - Bets are settled
    - Library is updated
    """
    config = InfectionConfig(
        require_stake=True,
        run_tests=True,
        run_type_check=True,
        auto_rollback=True,
        bonus_for_success=0.1,
    )

    return InfectionEnvironment(
        staking=staking,
        library=library,
        market=market,
        demon=demon,
        config=config,
    )
