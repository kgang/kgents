"""
E-gent v2 Thermodynamic Cycle: The composed evolution pipeline.

The ThermodynamicCycle composes all E-gent v2 components into a coherent
evolution loop:

    ☀️ SUN → MUTATE → SELECT → WAGER → INFECT → PAYOFF
         ↑                                      |
         └──────────────────────────────────────┘

From spec/e-gents/thermodynamics.md:
> The cycle is a heat engine with a teleological field.
> The Sun provides energy, the Demon selects, the Phage adapts.
> Without the Sun, the Demon starves. Without the Demon, the Sun burns.

Key principles:
1. THERMODYNAMIC: Gibbs Free Energy guides selection
2. TELEOLOGICAL: Intent prevents parasitic evolution
3. ECONOMIC: Market-driven resource allocation
4. EVOLUTIONARY: Fitness-based pattern propagation

Spec Reference: spec/e-gents/thermodynamics.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Protocol, Any
from uuid import uuid4

from .types import (
    Phage,
    PhageStatus,
    Intent,
    GibbsEnergy,
    ThermodynamicState,
    InfectionResult,
    InfectionStatus,
)
from .demon import (
    TeleologicalDemon,
    DemonConfig,
)
from .mutator import (
    Mutator,
    MutatorConfig,
)
from .library import (
    ViralLibrary,
    ViralLibraryConfig,
)
from .phage import (
    infect,
    InfectionEnvironment,
    InfectionConfig,
)


# =============================================================================
# Protocols for External Integration
# =============================================================================


class SunProtocol(Protocol):
    """Protocol for B-gent Sun (Grant system) integration."""

    def has_active_grant(self, grantee_id: str) -> bool:
        """Check if agent has an active grant."""
        ...

    def get_total_grant_budget(self, grantee_id: str) -> int:
        """Get total remaining grant budget."""
        ...

    async def consume_grant(self, grant_id: str, phage_id: str, tokens: int) -> Any:
        """Consume tokens from a grant."""
        ...


class PredictionMarketProtocol(Protocol):
    """Protocol for B-gent PredictionMarket integration."""

    def quote(
        self,
        phage_id: str,
        schema_signature: str,
        schema_confidence: float,
    ) -> Any:
        """Get market quote for a phage."""
        ...

    async def place_bet(
        self,
        bettor_id: str,
        phage_id: str,
        stake: int,
        predicted_success: bool,
    ) -> Any:
        """Place a bet on a phage."""
        ...

    async def settle(self, phage_id: str, succeeded: bool) -> list[Any]:
        """Settle bets for a phage."""
        ...

    def update_schema_success_rate(
        self, schema_signature: str, succeeded: bool
    ) -> None:
        """Update schema success rate."""
        ...


class StakingPoolProtocol(Protocol):
    """Protocol for B-gent StakingPool integration."""

    def calculate_required_stake(
        self, lines_changed: int, complexity_score: float
    ) -> int:
        """Calculate required stake for a mutation."""
        ...

    async def stake(self, staker_id: str, phage_id: str, amount: int) -> Any:
        """Stake tokens for a phage."""
        ...

    async def release_stake(self, stake_id: str, bonus_percentage: float) -> int:
        """Release stake after success."""
        ...

    async def forfeit_stake(self, stake_id: str) -> int:
        """Forfeit stake after failure."""
        ...


class SemanticRegistryProtocol(Protocol):
    """Protocol for L-gent SemanticRegistry integration."""

    async def embed_text(self, text: str) -> list[float]:
        """Embed text into a vector."""
        ...


# =============================================================================
# Cycle Configuration
# =============================================================================


class CyclePhase(Enum):
    """Phases of the thermodynamic cycle."""

    IDLE = "idle"
    SUN = "sun"  # Acquire energy/grants
    MUTATE = "mutate"  # Generate mutations
    SELECT = "select"  # Demon selection
    WAGER = "wager"  # Place bets
    INFECT = "infect"  # Apply mutations
    PAYOFF = "payoff"  # Settle economics
    COMPLETE = "complete"


@dataclass
class CycleConfig:
    """Configuration for the thermodynamic cycle."""

    # Identity
    agent_id: str = "e-gent"

    # Temperature control
    initial_temperature: float = 1.0
    cooling_rate: float = 0.05
    heating_rate: float = 0.1
    min_temperature: float = 0.1
    max_temperature: float = 5.0

    # Mutation limits
    max_mutations_per_cycle: int = 10
    min_mutations_to_proceed: int = 1

    # Selection thresholds
    min_intent_alignment: float = 0.3
    require_gibbs_viable: bool = True

    # Wagering
    default_stake_fraction: float = 0.1  # Fraction of budget to stake
    max_stake_per_phage: int = 1000
    require_market_quote: bool = False  # Skip market if not available

    # Infection
    run_tests: bool = True
    run_type_check: bool = True
    auto_rollback: bool = True

    # Evolution
    record_in_library: bool = True
    prune_library_after_cycle: bool = True

    # Timing
    max_cycle_duration_seconds: float = 300.0

    # Debugging
    verbose: bool = False


# =============================================================================
# Cycle Results
# =============================================================================


@dataclass
class PhaseResult:
    """Result of a single cycle phase."""

    phase: CyclePhase
    success: bool
    duration_ms: float
    phages_in: int = 0
    phages_out: int = 0
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class CycleResult:
    """Complete result of a thermodynamic cycle."""

    cycle_id: str
    success: bool
    started_at: datetime
    completed_at: datetime
    duration_ms: float

    # Phase results
    phase_results: list[PhaseResult] = field(default_factory=list)

    # Metrics
    mutations_generated: int = 0
    mutations_selected: int = 0
    mutations_succeeded: int = 0
    mutations_failed: int = 0

    # Economics
    tokens_staked: int = 0
    tokens_won: int = 0
    tokens_lost: int = 0
    grant_tokens_consumed: int = 0

    # Thermodynamics
    initial_temperature: float = 1.0
    final_temperature: float = 1.0
    total_gibbs_change: float = 0.0

    # Library updates
    patterns_added: int = 0
    patterns_reinforced: int = 0
    patterns_weakened: int = 0
    patterns_pruned: int = 0

    # Successful phages
    successful_phages: list[Phage] = field(default_factory=list)
    failed_phages: list[Phage] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Fraction of mutations that succeeded."""
        total = self.mutations_succeeded + self.mutations_failed
        if total == 0:
            return 0.0
        return self.mutations_succeeded / total

    @property
    def roi(self) -> float:
        """Return on investment (tokens won vs staked)."""
        if self.tokens_staked == 0:
            return 0.0
        return (self.tokens_won - self.tokens_lost) / self.tokens_staked


# =============================================================================
# Thermodynamic Cycle
# =============================================================================


class ThermodynamicCycle:
    """
    The composed evolution cycle.

    This is the main orchestrator that ties together all E-gent v2 components:
    - Mutator: Generate mutations from schemas
    - Demon: Select mutations via 5-layer filter
    - Library: Store and recall successful patterns
    - Phage.infect(): Apply mutations with rollback

    The cycle follows thermodynamic principles:
    - Temperature controls exploration vs exploitation
    - Gibbs Free Energy determines viability
    - The Sun provides exogenous energy for high-risk work

    From spec/e-gents/thermodynamics.md:
    > The cycle is a heat engine. Tokens are converted to work (code improvement)
    > or waste heat (failed mutations). The goal is to maximize work/heat ratio.
    """

    def __init__(
        self,
        config: CycleConfig | None = None,
        mutator: Mutator | None = None,
        demon: TeleologicalDemon | None = None,
        library: ViralLibrary | None = None,
        sun: SunProtocol | None = None,
        market: PredictionMarketProtocol | None = None,
        staking: StakingPoolProtocol | None = None,
        l_gent: SemanticRegistryProtocol | None = None,
    ) -> None:
        """
        Initialize the thermodynamic cycle.

        Args:
            config: Cycle configuration
            mutator: Mutation generator (created if not provided)
            demon: Teleological Demon (created if not provided)
            library: Viral Library (created if not provided)
            sun: B-gent Sun for grants
            market: B-gent PredictionMarket
            staking: B-gent StakingPool
            l_gent: L-gent SemanticRegistry
        """
        self.config = config or CycleConfig()

        # Core components (create defaults if not provided)
        self._mutator = mutator or Mutator(
            MutatorConfig(
                default_temperature=self.config.initial_temperature,
                require_gibbs_viable=self.config.require_gibbs_viable,
                max_mutations=self.config.max_mutations_per_cycle,
            )
        )
        self._demon = demon or TeleologicalDemon(
            DemonConfig(
                min_intent_alignment=self.config.min_intent_alignment,
                require_favorable_gibbs=self.config.require_gibbs_viable,
            )
        )
        self._library = library or ViralLibrary(ViralLibraryConfig())

        # External integrations (optional)
        self._sun = sun
        self._market = market
        self._staking = staking
        self._l_gent = l_gent

        # State
        self._temperature = self.config.initial_temperature
        self._thermo_state = ThermodynamicState(
            temperature=self._temperature,
            cooling_rate=self.config.cooling_rate,
            min_temperature=self.config.min_temperature,
            max_temperature=self.config.max_temperature,
        )
        self._current_phase = CyclePhase.IDLE
        self._intent: Intent | None = None

    # -------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------

    @property
    def temperature(self) -> float:
        """Current system temperature."""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set temperature (clamped to bounds)."""
        self._temperature = max(
            self.config.min_temperature,
            min(self.config.max_temperature, value),
        )
        self._thermo_state.temperature = self._temperature

    @property
    def current_phase(self) -> CyclePhase:
        """Current cycle phase."""
        return self._current_phase

    @property
    def mutator(self) -> Mutator:
        """Access to the Mutator."""
        return self._mutator

    @property
    def demon(self) -> TeleologicalDemon:
        """Access to the Demon."""
        return self._demon

    @property
    def library(self) -> ViralLibrary:
        """Access to the Viral Library."""
        return self._library

    @property
    def thermo_state(self) -> ThermodynamicState:
        """Thermodynamic state."""
        return self._thermo_state

    # -------------------------------------------------------------------
    # Intent Management
    # -------------------------------------------------------------------

    def set_intent(self, intent: Intent) -> None:
        """Set the teleological field (Intent) for this cycle."""
        self._intent = intent
        self._demon.set_intent(intent)

    async def infer_intent(self, code: str, description: str = "") -> Intent:
        """
        Infer Intent from code and optional description.

        Uses L-gent for embedding if available.
        """
        # Get embedding
        embedding: list[float] = []
        if self._l_gent:
            text = description or code[:500]
            embedding = await self._l_gent.embed_text(text)

        intent = Intent(
            embedding=embedding,
            source="structure" if not description else "user",
            description=description or "Inferred from code structure",
            confidence=0.8 if description else 0.5,
        )

        return intent

    # -------------------------------------------------------------------
    # Main Cycle Execution
    # -------------------------------------------------------------------

    async def run(
        self,
        code: str,
        target_path: Path,
        intent: Intent | None = None,
        grant_id: str | None = None,
    ) -> CycleResult:
        """
        Run a complete thermodynamic cycle.

        This is the main entry point. It executes:
        1. SUN: Check/consume grants
        2. MUTATE: Generate mutations
        3. SELECT: Filter via Demon
        4. WAGER: Place bets/stakes
        5. INFECT: Apply mutations
        6. PAYOFF: Settle economics

        Args:
            code: Source code to evolve
            target_path: Path to the file
            intent: Optional Intent (inferred if not provided)
            grant_id: Optional grant ID for high-risk work

        Returns:
            CycleResult with complete metrics
        """
        cycle_id = f"cycle_{uuid4().hex[:8]}"
        start_time = datetime.now()
        phase_results: list[PhaseResult] = []

        # Initialize result
        result = CycleResult(
            cycle_id=cycle_id,
            success=False,
            started_at=start_time,
            completed_at=start_time,
            duration_ms=0.0,
            initial_temperature=self._temperature,
        )

        try:
            # Set Intent
            if intent:
                self.set_intent(intent)
            elif not self._intent:
                self._intent = await self.infer_intent(code)
                self.set_intent(self._intent)

            # Phase 1: SUN - Acquire energy
            self._current_phase = CyclePhase.SUN
            sun_result = await self._phase_sun(grant_id)
            phase_results.append(sun_result)
            if not sun_result.success:
                # No grant, but continue with market economics
                pass
            result.grant_tokens_consumed = sun_result.details.get("tokens_consumed", 0)

            # Phase 2: MUTATE - Generate mutations
            self._current_phase = CyclePhase.MUTATE
            mutate_result, phages = await self._phase_mutate(code, target_path)
            phase_results.append(mutate_result)
            result.mutations_generated = mutate_result.phages_out

            if mutate_result.phages_out < self.config.min_mutations_to_proceed:
                result.phase_results = phase_results
                result.completed_at = datetime.now()
                result.duration_ms = (
                    result.completed_at - start_time
                ).total_seconds() * 1000
                return result

            # Phase 3: SELECT - Filter via Demon
            self._current_phase = CyclePhase.SELECT
            select_result, selected_phages = await self._phase_select(phages)
            phase_results.append(select_result)
            result.mutations_selected = select_result.phages_out

            if not selected_phages:
                result.phase_results = phase_results
                result.completed_at = datetime.now()
                result.duration_ms = (
                    result.completed_at - start_time
                ).total_seconds() * 1000
                return result

            # Phase 4: WAGER - Place bets/stakes
            self._current_phase = CyclePhase.WAGER
            wager_result, staked_phages, stakes = await self._phase_wager(
                selected_phages
            )
            phase_results.append(wager_result)
            result.tokens_staked = wager_result.details.get("total_staked", 0)

            # Phase 5: INFECT - Apply mutations
            self._current_phase = CyclePhase.INFECT
            infect_result, infection_results = await self._phase_infect(
                staked_phages, target_path, stakes
            )
            phase_results.append(infect_result)
            result.mutations_succeeded = infect_result.details.get("succeeded", 0)
            result.mutations_failed = infect_result.details.get("failed", 0)

            # Collect successful/failed phages
            for phage, inf_result in infection_results:
                if inf_result.status == InfectionStatus.SUCCESS:
                    result.successful_phages.append(phage)
                else:
                    result.failed_phages.append(phage)

            # Phase 6: PAYOFF - Settle economics
            self._current_phase = CyclePhase.PAYOFF
            payoff_result = await self._phase_payoff(infection_results, stakes)
            phase_results.append(payoff_result)
            result.tokens_won = payoff_result.details.get("tokens_won", 0)
            result.tokens_lost = payoff_result.details.get("tokens_lost", 0)
            result.patterns_added = payoff_result.details.get("patterns_added", 0)
            result.patterns_reinforced = payoff_result.details.get(
                "patterns_reinforced", 0
            )
            result.patterns_weakened = payoff_result.details.get("patterns_weakened", 0)

            # Apply temperature adjustment
            self._adjust_temperature(result.success_rate)

            # Complete
            self._current_phase = CyclePhase.COMPLETE
            result.success = result.mutations_succeeded > 0
            result.phase_results = phase_results
            result.final_temperature = self._temperature
            result.total_gibbs_change = sum(
                p.mutation.gibbs_free_energy
                for p in result.successful_phages
                if p.mutation
            )

        except Exception as e:
            result.phase_results = phase_results
            result.phase_results.append(
                PhaseResult(
                    phase=self._current_phase,
                    success=False,
                    duration_ms=0.0,
                    error=str(e),
                )
            )

        finally:
            self._current_phase = CyclePhase.IDLE
            result.completed_at = datetime.now()
            result.duration_ms = (
                result.completed_at - start_time
            ).total_seconds() * 1000

        return result

    # -------------------------------------------------------------------
    # Phase Implementations
    # -------------------------------------------------------------------

    async def _phase_sun(self, grant_id: str | None) -> PhaseResult:
        """
        Phase 1: SUN - Acquire energy from grants.

        Checks for active grants and records consumption.
        """
        start = datetime.now()
        details: dict[str, Any] = {}

        if self._sun and grant_id:
            has_grant = self._sun.has_active_grant(self.config.agent_id)
            budget = self._sun.get_total_grant_budget(self.config.agent_id)

            details["has_grant"] = has_grant
            details["grant_budget"] = budget

            if has_grant:
                # Increase temperature for grant-funded work
                self.temperature = min(
                    self.config.max_temperature,
                    self._temperature * (1 + self.config.heating_rate),
                )
                details["temperature_boost"] = True
        else:
            details["has_grant"] = False
            details["grant_budget"] = 0

        duration = (datetime.now() - start).total_seconds() * 1000
        return PhaseResult(
            phase=CyclePhase.SUN,
            success=True,
            duration_ms=duration,
            details=details,
        )

    async def _phase_mutate(
        self, code: str, target_path: Path
    ) -> tuple[PhaseResult, list[Phage]]:
        """
        Phase 2: MUTATE - Generate mutations using schemas.

        Uses the Mutator to generate Phages from the code.
        """
        start = datetime.now()

        # Generate mutations
        self._mutator.temperature = self._temperature
        phages = self._mutator.mutate_to_phages(
            code=code,
            module_name=str(target_path),
            temperature=self._temperature,
        )

        # Set target paths
        for phage in phages:
            phage.target_path = target_path

        duration = (datetime.now() - start).total_seconds() * 1000
        return (
            PhaseResult(
                phase=CyclePhase.MUTATE,
                success=len(phages) > 0,
                duration_ms=duration,
                phages_in=0,
                phages_out=len(phages),
                details={
                    "schemas_used": list(
                        set(p.mutation.schema_signature for p in phages if p.mutation)
                    )
                },
            ),
            phages,
        )

    async def _phase_select(
        self, phages: list[Phage]
    ) -> tuple[PhaseResult, list[Phage]]:
        """
        Phase 3: SELECT - Filter via Teleological Demon.

        Applies 5-layer selection to filter out non-viable mutations.
        """
        start = datetime.now()

        # Run selection
        results = self._demon.select_batch(phages)
        selected = [phage for phage, result in results if result.passed]

        # Collect rejection reasons
        rejections: dict[str, int] = {}
        for phage, result in results:
            if not result.passed and result.rejection_reason:
                reason = result.rejection_reason.value
                rejections[reason] = rejections.get(reason, 0) + 1

        duration = (datetime.now() - start).total_seconds() * 1000
        return (
            PhaseResult(
                phase=CyclePhase.SELECT,
                success=len(selected) > 0,
                duration_ms=duration,
                phages_in=len(phages),
                phages_out=len(selected),
                details={
                    "rejection_reasons": rejections,
                    "selection_rate": len(selected) / max(1, len(phages)),
                },
            ),
            selected,
        )

    async def _phase_wager(
        self, phages: list[Phage]
    ) -> tuple[PhaseResult, list[Phage], dict[str, Any]]:
        """
        Phase 4: WAGER - Place bets and stakes.

        Stakes tokens on each phage before infection.
        """
        start = datetime.now()
        stakes: dict[str, Any] = {}
        total_staked = 0
        staked_phages: list[Phage] = []

        for phage in phages:
            if self._staking and phage.mutation:
                try:
                    # Calculate and place stake
                    required = self._staking.calculate_required_stake(
                        lines_changed=phage.mutation.lines_changed,
                        complexity_score=1.0,
                    )
                    stake = min(required, self.config.max_stake_per_phage)

                    stake_record = await self._staking.stake(
                        staker_id=self.config.agent_id,
                        phage_id=phage.id,
                        amount=stake,
                    )
                    stakes[phage.id] = stake_record
                    phage.stake = stake
                    phage.status = PhageStatus.STAKED
                    total_staked += stake
                    staked_phages.append(phage)

                except Exception as e:
                    # Staking failed - skip this phage
                    phage.error = f"Staking failed: {e}"
                    if self.config.verbose:
                        print(f"Staking failed for {phage.id}: {e}")
            else:
                # No staking required
                phage.status = PhageStatus.STAKED
                staked_phages.append(phage)

            # Get market quote if available
            if self._market and phage.mutation:
                try:
                    quote = self._market.quote(
                        phage_id=phage.id,
                        schema_signature=phage.mutation.schema_signature,
                        schema_confidence=phage.mutation.confidence,
                    )
                    phage.market_odds = quote.success_odds
                except Exception:
                    pass

        duration = (datetime.now() - start).total_seconds() * 1000
        return (
            PhaseResult(
                phase=CyclePhase.WAGER,
                success=len(staked_phages) > 0,
                duration_ms=duration,
                phages_in=len(phages),
                phages_out=len(staked_phages),
                details={
                    "total_staked": total_staked,
                    "stakes_placed": len(stakes),
                },
            ),
            staked_phages,
            stakes,
        )

    async def _phase_infect(
        self,
        phages: list[Phage],
        target_path: Path,
        stakes: dict[str, Any],
    ) -> tuple[PhaseResult, list[tuple[Phage, InfectionResult]]]:
        """
        Phase 5: INFECT - Apply mutations to codebase.

        Runs the actual infection with tests and rollback.
        """
        start = datetime.now()
        results: list[tuple[Phage, InfectionResult]] = []
        succeeded = 0
        failed = 0

        # Create infection environment
        env = InfectionEnvironment(
            staking=self._staking,
            library=self._library,
            market=self._market,
            demon=self._demon,
            config=InfectionConfig(
                run_tests=self.config.run_tests,
                run_type_check=self.config.run_type_check,
                auto_rollback=self.config.auto_rollback,
                require_stake=False,  # Already staked
            ),
        )

        # Get intent embedding for infection
        intent_embedding = self._intent.embedding if self._intent else None

        for phage in phages:
            try:
                result = await infect(
                    phage=phage,
                    target_path=target_path,
                    env=env,
                    intent_embedding=intent_embedding,
                )
                results.append((phage, result))

                if result.status == InfectionStatus.SUCCESS:
                    succeeded += 1
                else:
                    failed += 1

            except Exception as e:
                # Infection error
                error_result = InfectionResult(
                    phage_id=phage.id,
                    status=InfectionStatus.FAILED,
                    error_message=str(e),
                )
                results.append((phage, error_result))
                failed += 1

        duration = (datetime.now() - start).total_seconds() * 1000
        return (
            PhaseResult(
                phase=CyclePhase.INFECT,
                success=succeeded > 0,
                duration_ms=duration,
                phages_in=len(phages),
                phages_out=succeeded,
                details={
                    "succeeded": succeeded,
                    "failed": failed,
                },
            ),
            results,
        )

    async def _phase_payoff(
        self,
        infection_results: list[tuple[Phage, InfectionResult]],
        stakes: dict[str, Any],
    ) -> PhaseResult:
        """
        Phase 6: PAYOFF - Settle economics and update library.

        Releases/forfeits stakes, settles bets, updates patterns.
        """
        start = datetime.now()
        tokens_won = 0
        tokens_lost = 0
        patterns_added = 0
        patterns_reinforced = 0
        patterns_weakened = 0

        for phage, result in infection_results:
            success = result.status == InfectionStatus.SUCCESS

            # Handle stakes
            stake_record = stakes.get(phage.id)
            if stake_record and self._staking:
                if success:
                    returned = await self._staking.release_stake(
                        stake_id=stake_record.id,
                        bonus_percentage=self.config.default_stake_fraction,
                    )
                    tokens_won += returned - phage.stake
                else:
                    forfeited = await self._staking.forfeit_stake(
                        stake_id=stake_record.id
                    )
                    tokens_lost += forfeited

            # Settle market bets
            if self._market:
                await self._market.settle(phage.id, success)
                if phage.mutation:
                    self._market.update_schema_success_rate(
                        phage.mutation.schema_signature, success
                    )

            # Update library
            if self.config.record_in_library and self._library:
                if success:
                    # Calculate impact
                    impact = self._calculate_impact(phage, result)

                    # Check if pattern exists
                    if phage.mutation:
                        existing = self._library.get_pattern(phage.mutation.signature)
                        if existing:
                            patterns_reinforced += 1
                        else:
                            patterns_added += 1

                    await self._library.record_success(
                        phage=phage,
                        impact=impact,
                        cost=result.tokens_consumed,
                    )
                else:
                    if phage.mutation:
                        existing = self._library.get_pattern(phage.mutation.signature)
                        if existing:
                            patterns_weakened += 1

                    await self._library.record_failure(phage)

            # Update thermodynamic state
            if phage.mutation:
                gibbs = GibbsEnergy(
                    enthalpy_delta=phage.mutation.enthalpy_delta,
                    entropy_delta=phage.mutation.entropy_delta,
                    temperature=self._temperature,
                )
                self._thermo_state.record_mutation(gibbs, success)

        # Prune library if configured
        patterns_pruned = 0
        if self.config.prune_library_after_cycle and self._library:
            prune_report = await self._library.prune()
            patterns_pruned = prune_report.pruned_count

        duration = (datetime.now() - start).total_seconds() * 1000
        return PhaseResult(
            phase=CyclePhase.PAYOFF,
            success=True,
            duration_ms=duration,
            details={
                "tokens_won": tokens_won,
                "tokens_lost": tokens_lost,
                "patterns_added": patterns_added,
                "patterns_reinforced": patterns_reinforced,
                "patterns_weakened": patterns_weakened,
                "patterns_pruned": patterns_pruned,
            },
        )

    # -------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------

    def _adjust_temperature(self, success_rate: float) -> None:
        """
        Adjust temperature based on cycle success rate.

        High success → cool (exploit)
        Low success → heat (explore)
        """
        if success_rate > 0.7:
            # Success! Cool down for exploitation
            self.temperature = self._temperature * (1 - self.config.cooling_rate)
        elif success_rate < 0.3:
            # Struggling, heat up for exploration
            self.temperature = self._temperature * (1 + self.config.heating_rate)
        # Else: maintain temperature

        self._thermo_state.cool()  # Always some cooling

    def _calculate_impact(self, phage: Phage, result: InfectionResult) -> float:
        """Calculate impact of a successful mutation for library."""
        impact = 0.0

        # Base impact from tests
        if result.tests_passed:
            impact += 0.5

        # Bonus from test count
        if result.test_count > 0:
            impact += min(0.3, result.test_count * 0.01)

        # Bonus from types
        if result.types_valid:
            impact += 0.2

        # Bonus from Gibbs
        if phage.mutation and phage.mutation.gibbs_free_energy < 0:
            impact += min(0.3, abs(phage.mutation.gibbs_free_energy) * 0.3)

        # Bonus from intent alignment
        if phage.intent_alignment > 0.7:
            impact += 0.2 * phage.intent_alignment

        return impact


# =============================================================================
# Factory Functions
# =============================================================================


def create_cycle(
    config: CycleConfig | None = None,
    temperature: float = 1.0,
) -> ThermodynamicCycle:
    """Create a thermodynamic cycle with default configuration."""
    cfg = config or CycleConfig(initial_temperature=temperature)
    return ThermodynamicCycle(config=cfg)


def create_conservative_cycle() -> ThermodynamicCycle:
    """Create a conservative cycle (low temperature, strict selection)."""
    config = CycleConfig(
        initial_temperature=0.5,
        cooling_rate=0.1,
        min_intent_alignment=0.5,
        require_gibbs_viable=True,
        max_mutations_per_cycle=5,
    )
    return ThermodynamicCycle(config=config)


def create_exploratory_cycle() -> ThermodynamicCycle:
    """Create an exploratory cycle (high temperature, loose selection)."""
    config = CycleConfig(
        initial_temperature=3.0,
        cooling_rate=0.02,
        heating_rate=0.2,
        min_intent_alignment=0.2,
        require_gibbs_viable=False,
        max_mutations_per_cycle=20,
    )
    return ThermodynamicCycle(config=config)


def create_grant_funded_cycle(sun: SunProtocol) -> ThermodynamicCycle:
    """Create a cycle funded by grants (higher risk tolerance)."""
    config = CycleConfig(
        initial_temperature=2.0,
        max_temperature=5.0,
        min_intent_alignment=0.4,
        require_gibbs_viable=True,
    )
    return ThermodynamicCycle(config=config, sun=sun)


def create_full_cycle(
    sun: SunProtocol | None = None,
    market: PredictionMarketProtocol | None = None,
    staking: StakingPoolProtocol | None = None,
    l_gent: SemanticRegistryProtocol | None = None,
    library: ViralLibrary | None = None,
) -> ThermodynamicCycle:
    """Create a cycle with full B-gent and L-gent integration."""
    return ThermodynamicCycle(
        sun=sun,
        market=market,
        staking=staking,
        l_gent=l_gent,
        library=library,
    )


# =============================================================================
# EvolutionAgent v2 (Wrapper)
# =============================================================================


class EvolutionAgent:
    """
    High-level evolution agent wrapping the thermodynamic cycle.

    This provides a simpler interface for common evolution tasks:
    - evolve(): Run evolution on a file
    - evolve_project(): Run evolution across multiple files
    - suggest(): Get mutation suggestions without applying
    """

    def __init__(
        self,
        cycle: ThermodynamicCycle | None = None,
        config: CycleConfig | None = None,
    ) -> None:
        """
        Initialize the evolution agent.

        Args:
            cycle: Pre-configured cycle (created if not provided)
            config: Configuration for new cycle
        """
        self._cycle = cycle or ThermodynamicCycle(config=config or CycleConfig())

    @property
    def cycle(self) -> ThermodynamicCycle:
        """Access the underlying cycle."""
        return self._cycle

    async def evolve(
        self,
        target: Path,
        intent: str | Intent | None = None,
        max_cycles: int = 1,
    ) -> list[CycleResult]:
        """
        Evolve a single file.

        Args:
            target: Path to the file to evolve
            intent: Optional Intent or description
            max_cycles: Maximum number of cycles to run

        Returns:
            List of CycleResults
        """
        results: list[CycleResult] = []

        # Read code
        code = target.read_text()

        # Create Intent if string
        if isinstance(intent, str):
            intent_obj = Intent(
                embedding=[],
                source="user",
                description=intent,
                confidence=1.0,
            )
        else:
            intent_obj = intent

        # Run cycles
        for _ in range(max_cycles):
            result = await self._cycle.run(
                code=code,
                target_path=target,
                intent=intent_obj,
            )
            results.append(result)

            # Update code if successful
            if result.success and target.exists():
                code = target.read_text()

            # Stop if no progress
            if result.mutations_succeeded == 0:
                break

        return results

    async def suggest(
        self,
        code: str,
        intent: str | Intent | None = None,
    ) -> list[Phage]:
        """
        Get mutation suggestions without applying.

        Args:
            code: Source code to analyze
            intent: Optional Intent or description

        Returns:
            List of suggested Phages (not applied)
        """
        # Set intent
        if isinstance(intent, str):
            intent_obj = Intent(
                embedding=[],
                source="user",
                description=intent,
                confidence=1.0,
            )
        elif intent:
            intent_obj = intent
        else:
            intent_obj = await self._cycle.infer_intent(code)

        self._cycle.set_intent(intent_obj)

        # Generate mutations
        phages = self._cycle.mutator.mutate_to_phages(code)

        # Filter via Demon
        selected = self._cycle.demon.filter_batch(phages)

        return selected
