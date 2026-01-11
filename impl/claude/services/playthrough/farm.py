"""
Parallel Playthrough Farm: Run N agents in parallel with ASHC evidence aggregation.

Categorical Structure:
    FarmFunctor = ∏_{p ∈ Personas} PlayAgent_p

    Where:
        FarmEvidence = colimit of PlaythroughEvidence across all personas

The farm runs multiple personas in parallel, each in its own browser context,
and aggregates evidence for ASHC integration.

Time Scale Principle:
    Wall time budget: 60 seconds
    At 4x scale: 240 seconds of game time
    This allows thorough testing in reasonable CI time
"""

from __future__ import annotations

import asyncio
import logging
import statistics
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

from .agent import AgentPersona, PlaythroughAgent
from .personas import CORE_PERSONAS, get_persona
from .witness import (
    BalanceObservation,
    EmergenceEvent,
    FunFloorViolation,
    PlaythroughEvidence,
)

if TYPE_CHECKING:
    from protocols.ashc.evidence import Evidence as ASHCEvidence

logger = logging.getLogger("kgents.playthrough.farm")


# =============================================================================
# Game Adapter Protocol
# =============================================================================


class GameAdapterFactory(Protocol):
    """
    Factory for creating game adapters with isolated browser contexts.

    Each agent runs in its own browser context to prevent state pollution.
    """

    async def create_context(
        self,
        time_scale: float = 1.0,
    ) -> "GameAdapter":
        """
        Create a new isolated game context.

        Args:
            time_scale: Game speed multiplier (e.g., 4.0 = 4x speed)

        Returns:
            GameAdapter with isolated browser context
        """
        ...


class GameAdapter(Protocol):
    """
    Protocol for game adapters that implement GameInterface.

    Adapters wrap browser automation (Playwright) and game communication.
    """

    async def capture_screen(self) -> bytes:
        """Capture current screen."""
        ...

    async def get_debug_state(self) -> dict[str, Any]:
        """Get debug API state."""
        ...

    async def get_audio_cues(self) -> list[dict[str, Any]]:
        """Get recent audio cues."""
        ...

    async def send_action(self, action: Any) -> None:
        """Send action to game."""
        ...

    async def start_game(self) -> None:
        """Initialize and start the game."""
        ...

    async def close(self) -> None:
        """Clean up resources."""
        ...


# =============================================================================
# Fun Floor Report
# =============================================================================


@dataclass(frozen=True)
class FunFloorReport:
    """
    Aggregate fun floor analysis across all personas.

    The fun floor is the minimum level of engagement expected for all player types.
    If any persona consistently violates the fun floor, the game has a problem.
    """

    total_violations: int
    violations_by_persona: dict[str, int]
    violation_types: dict[str, int]  # Type -> count
    total_violation_duration_ms: float
    worst_persona: str | None
    worst_violation_type: str | None
    fun_floor_passed: bool

    @property
    def violation_rate(self) -> float:
        """Violations per persona."""
        n_personas = len(self.violations_by_persona) or 1
        return self.total_violations / n_personas


# =============================================================================
# Balance Matrix
# =============================================================================


@dataclass(frozen=True)
class UpgradeStats:
    """Statistics for a single upgrade across all runs."""

    name: str
    times_selected: int
    avg_wave_when_selected: float
    win_rate_when_selected: float  # Survival to max waves
    avg_final_health: float
    synergies_discovered: list[str]


@dataclass(frozen=True)
class BalanceMatrix:
    """
    Matrix of upgrade performance across personas.

    Columns: Personas
    Rows: Upgrades
    Cells: Performance metrics
    """

    persona_stats: dict[str, dict[str, Any]]  # Persona -> upgrade -> stats
    upgrade_summaries: dict[str, UpgradeStats]
    overpowered_upgrades: list[str]  # Consistently dominant
    underpowered_upgrades: list[str]  # Consistently ignored
    persona_dependent_upgrades: list[str]  # Good for some, bad for others


# =============================================================================
# Farm Evidence
# =============================================================================


@dataclass
class FarmEvidence:
    """
    Aggregated evidence from parallel playthrough farm.

    This is the colimit of PlaythroughEvidence across all personas,
    ready for ASHC integration.
    """

    # Identity
    farm_id: str
    started_at: float
    duration_ms: float

    # Per-persona results
    playthroughs: list[PlaythroughEvidence]

    # Aggregate metrics
    aggregate_galois_loss: float  # Average across personas
    aggregate_humanness_score: float

    # Balance analysis
    balance_matrix: BalanceMatrix

    # Emergence catalog
    emergence_catalog: list[EmergenceEvent]

    # Fun floor analysis
    fun_floor_report: FunFloorReport

    # Aggregate observations
    balance_observations: list[BalanceObservation]

    # Completion metrics
    personas_completed: int
    personas_failed: int
    errors: list[str] = field(default_factory=list)

    @property
    def galois_coherence(self) -> float:
        """Galois coherence = 1 - galois_loss."""
        return 1.0 - self.aggregate_galois_loss

    @property
    def is_valid(self) -> bool:
        """Check if farm produced valid evidence."""
        return (
            len(self.playthroughs) >= 3  # At least 3 personas completed
            and all(p.is_valid_evidence for p in self.playthroughs)
            and self.personas_failed < self.personas_completed
        )

    @property
    def evidence_tier(self) -> str:
        """Determine aggregate evidence tier."""
        if self.aggregate_galois_loss < 0.10:
            return "CATEGORICAL"
        if self.aggregate_galois_loss < 0.38:
            return "EMPIRICAL"
        if self.aggregate_galois_loss < 0.45:
            return "AESTHETIC"
        if self.aggregate_galois_loss < 0.65:
            return "SOMATIC"
        return "CHAOTIC"

    def to_ashc_evidence(self) -> "ASHCEvidence":
        """
        Convert to ASHC-compatible Evidence format.

        This bridges the playthrough evidence to the ASHC compiler's
        evidence accumulation system.
        """
        from protocols.ashc.evidence import Evidence, Run
        from protocols.ashc.verify import LintReport, TestReport, TypeReport

        # Convert each playthrough to an ASHC Run
        runs: list[Run] = []
        for pt in self.playthroughs:
            # Create test report from playthrough success metrics
            passed_decisions = int(pt.total_decisions * pt.humanness_score)
            failed_decisions = pt.total_decisions - passed_decisions
            test_report = TestReport(
                passed=passed_decisions,
                failed=failed_decisions,
                skipped=0,
                errors=(),
                duration_ms=pt.duration_ms,
                raw_output=f"Playthrough {pt.persona}: fun_floor_passed={pt.fun_floor_passed}",
            )

            # Type report (always passes for gameplay)
            type_report = TypeReport(
                passed=True,
                error_count=0,
                errors=(),
                raw_output="",
            )

            # Lint report based on balance observations
            lint_violations = tuple(
                f"{obs.type}: {obs.subject} - {obs.evidence}"
                for obs in pt.balance_observations
                if obs.type in ("overpowered", "underpowered")
            )
            lint_report = LintReport(
                passed=len(lint_violations) == 0,
                violation_count=len(lint_violations),
                violations=lint_violations,
                raw_output="",
            )

            run = Run(
                run_id=pt.playthrough_id,
                spec_hash=f"playthrough_{pt.persona}_{self.farm_id}",
                prompt_used=f"Persona: {pt.persona}",
                implementation=f"Waves: {pt.waves_survived}, Decisions: {pt.total_decisions}",
                test_results=test_report,
                type_results=type_report,
                lint_results=lint_report,
                witnesses=(),  # Would populate with actual witnesses
                duration_ms=pt.duration_ms,
                nudges=(),
            )
            runs.append(run)

        # Create Evidence with galois_loss
        evidence = Evidence(
            runs=tuple(runs),
            spec_content=f"Parallel playthrough farm with {len(self.playthroughs)} personas",
            best_impl_content=self._best_playthrough_summary(),
            galois_loss=self.aggregate_galois_loss,
        )

        return evidence

    def _best_playthrough_summary(self) -> str:
        """Generate summary of best performing playthrough."""
        if not self.playthroughs:
            return "No playthroughs completed"

        best = min(self.playthroughs, key=lambda p: p.galois_loss)
        return (
            f"Best: {best.persona} - "
            f"Waves: {best.waves_survived}, "
            f"Humanness: {best.humanness_score:.2f}, "
            f"Galois Loss: {best.galois_loss:.3f}"
        )


# =============================================================================
# Parallel Playthrough Farm
# =============================================================================


class PlaythroughFarm:
    """
    Parallel playthrough farm runner.

    Runs N agents in parallel (each with different persona),
    each in its own browser context (via Playwright),
    and aggregates evidence for ASHC integration.

    Categorical interpretation:
        Farm = ∏_{p ∈ Personas} PlayAgent_p
        Evidence = colim(PlaythroughEvidence_p)
    """

    def __init__(
        self,
        adapter_factory: GameAdapterFactory,
        llm_client: Any | None = None,
        max_concurrency: int = 6,
    ):
        """
        Initialize the farm.

        Args:
            adapter_factory: Factory for creating isolated game adapters
            llm_client: Optional LLM client for strategic decisions
            max_concurrency: Maximum parallel agents (default 6)
        """
        self.adapter_factory = adapter_factory
        self.llm_client = llm_client
        self.max_concurrency = max_concurrency

    async def run_farm(
        self,
        personas: list[str] | None = None,
        time_scale: float = 4.0,
        max_waves: int = 5,
        max_duration_ms: float = 60_000,
    ) -> FarmEvidence:
        """
        Run parallel playthrough farm.

        Args:
            personas: List of persona names to run (default: CORE_PERSONAS)
            time_scale: Game speed multiplier (4x for testing)
            max_waves: Maximum waves per playthrough
            max_duration_ms: Wall time budget (1 minute = 4 min game time at 4x)

        Returns:
            FarmEvidence with aggregated results
        """
        if personas is None:
            personas = CORE_PERSONAS

        farm_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        logger.info(
            f"Starting playthrough farm {farm_id} with {len(personas)} personas "
            f"(time_scale={time_scale}x, max_waves={max_waves})"
        )

        # Run personas in parallel with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrency)
        tasks = [
            self._run_persona_with_semaphore(
                semaphore=semaphore,
                persona_name=persona,
                time_scale=time_scale,
                max_waves=max_waves,
                max_duration_ms=max_duration_ms,
            )
            for persona in personas
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Separate successes and failures
        playthroughs: list[PlaythroughEvidence] = []
        errors: list[str] = []

        for persona, result in zip(personas, results):
            if isinstance(result, Exception):
                errors.append(f"{persona}: {result}")
                logger.error(f"Persona {persona} failed: {result}")
            elif isinstance(result, PlaythroughEvidence):
                playthroughs.append(result)
                logger.info(
                    f"Persona {persona} completed: "
                    f"waves={result.waves_survived}, "
                    f"humanness={result.humanness_score:.2f}"
                )

        # Aggregate evidence
        duration_ms = (time.time() - start_time) * 1000

        return self._aggregate_evidence(
            farm_id=farm_id,
            started_at=start_time,
            duration_ms=duration_ms,
            playthroughs=playthroughs,
            errors=errors,
        )

    async def _run_persona_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        persona_name: str,
        time_scale: float,
        max_waves: int,
        max_duration_ms: float,
    ) -> PlaythroughEvidence:
        """Run a single persona with concurrency control."""
        async with semaphore:
            return await self._run_persona(
                persona_name=persona_name,
                time_scale=time_scale,
                max_waves=max_waves,
                max_duration_ms=max_duration_ms,
            )

    async def _run_persona(
        self,
        persona_name: str,
        time_scale: float,
        max_waves: int,
        max_duration_ms: float,
    ) -> PlaythroughEvidence:
        """Run a single persona playthrough."""
        persona = get_persona(persona_name)
        agent = PlaythroughAgent(persona=persona, llm_client=self.llm_client)

        # Create isolated game context
        adapter = await self.adapter_factory.create_context(time_scale=time_scale)

        try:
            # Start the game
            await adapter.start_game()

            # Run the playthrough
            # Scale max_duration by time_scale since game runs faster
            scaled_duration = max_duration_ms * time_scale
            evidence: PlaythroughEvidence = await agent.run_playthrough(
                game=adapter,
                max_waves=max_waves,
                max_duration_ms=scaled_duration,
            )

            return evidence

        finally:
            # Always clean up
            await adapter.close()

    def _aggregate_evidence(
        self,
        farm_id: str,
        started_at: float,
        duration_ms: float,
        playthroughs: list[PlaythroughEvidence],
        errors: list[str],
    ) -> FarmEvidence:
        """Aggregate evidence from all playthroughs."""
        if not playthroughs:
            # Return empty evidence if all failed
            return FarmEvidence(
                farm_id=farm_id,
                started_at=started_at,
                duration_ms=duration_ms,
                playthroughs=[],
                aggregate_galois_loss=1.0,
                aggregate_humanness_score=0.0,
                balance_matrix=BalanceMatrix(
                    persona_stats={},
                    upgrade_summaries={},
                    overpowered_upgrades=[],
                    underpowered_upgrades=[],
                    persona_dependent_upgrades=[],
                ),
                emergence_catalog=[],
                fun_floor_report=FunFloorReport(
                    total_violations=0,
                    violations_by_persona={},
                    violation_types={},
                    total_violation_duration_ms=0,
                    worst_persona=None,
                    worst_violation_type=None,
                    fun_floor_passed=False,
                ),
                balance_observations=[],
                personas_completed=0,
                personas_failed=len(errors),
                errors=errors,
            )

        # Aggregate Galois metrics
        galois_losses = [p.galois_loss for p in playthroughs]
        humanness_scores = [p.humanness_score for p in playthroughs]

        aggregate_galois_loss = statistics.mean(galois_losses)
        aggregate_humanness_score = statistics.mean(humanness_scores)

        # Build balance matrix
        balance_matrix = self._build_balance_matrix(playthroughs)

        # Collect all emergence events
        emergence_catalog = []
        for pt in playthroughs:
            emergence_catalog.extend(pt.emergence_events)

        # Deduplicate by description
        seen_descriptions: set[str] = set()
        unique_emergence = []
        for event in emergence_catalog:
            if event.description not in seen_descriptions:
                seen_descriptions.add(event.description)
                unique_emergence.append(event)

        # Build fun floor report
        fun_floor_report = self._build_fun_floor_report(playthroughs)

        # Collect all balance observations
        all_balance_obs = []
        for pt in playthroughs:
            all_balance_obs.extend(pt.balance_observations)

        return FarmEvidence(
            farm_id=farm_id,
            started_at=started_at,
            duration_ms=duration_ms,
            playthroughs=playthroughs,
            aggregate_galois_loss=aggregate_galois_loss,
            aggregate_humanness_score=aggregate_humanness_score,
            balance_matrix=balance_matrix,
            emergence_catalog=unique_emergence,
            fun_floor_report=fun_floor_report,
            balance_observations=all_balance_obs,
            personas_completed=len(playthroughs),
            personas_failed=len(errors),
            errors=errors,
        )

    def _build_balance_matrix(
        self,
        playthroughs: list[PlaythroughEvidence],
    ) -> BalanceMatrix:
        """Build balance matrix from playthroughs."""
        # Collect stats per persona per upgrade
        persona_stats: dict[str, dict[str, Any]] = {}
        upgrade_counts: dict[str, int] = {}
        upgrade_wave_sums: dict[str, float] = {}
        upgrade_health_sums: dict[str, float] = {}
        upgrade_wins: dict[str, int] = {}

        for pt in playthroughs:
            persona_stats[pt.persona] = {}

            for upgrade in pt.upgrades_collected:
                # Track per-persona stats
                if upgrade not in persona_stats[pt.persona]:
                    persona_stats[pt.persona][upgrade] = {
                        "times_selected": 0,
                        "total_waves": 0,
                        "total_health": 0,
                    }
                persona_stats[pt.persona][upgrade]["times_selected"] += 1
                persona_stats[pt.persona][upgrade]["total_waves"] += pt.waves_survived
                persona_stats[pt.persona][upgrade]["total_health"] += pt.final_health

                # Track global stats
                upgrade_counts[upgrade] = upgrade_counts.get(upgrade, 0) + 1
                upgrade_wave_sums[upgrade] = upgrade_wave_sums.get(upgrade, 0) + pt.waves_survived
                upgrade_health_sums[upgrade] = upgrade_health_sums.get(upgrade, 0) + pt.final_health

                # Count "wins" (survived 5+ waves)
                if pt.waves_survived >= 5:
                    upgrade_wins[upgrade] = upgrade_wins.get(upgrade, 0) + 1

        # Build upgrade summaries
        upgrade_summaries: dict[str, UpgradeStats] = {}
        for upgrade, count in upgrade_counts.items():
            upgrade_summaries[upgrade] = UpgradeStats(
                name=upgrade,
                times_selected=count,
                avg_wave_when_selected=upgrade_wave_sums.get(upgrade, 0) / count,
                win_rate_when_selected=upgrade_wins.get(upgrade, 0) / count,
                avg_final_health=upgrade_health_sums.get(upgrade, 0) / count,
                synergies_discovered=[],  # Would extract from emergence events
            )

        # Identify balance issues
        overpowered: list[str] = []
        underpowered: list[str] = []
        persona_dependent: list[str] = []

        if upgrade_summaries:
            avg_win_rate = statistics.mean(
                s.win_rate_when_selected for s in upgrade_summaries.values()
            )
            avg_selection = statistics.mean(s.times_selected for s in upgrade_summaries.values())

            for name, stats in upgrade_summaries.items():
                # Overpowered: high win rate AND frequently selected
                if (
                    stats.win_rate_when_selected > avg_win_rate * 1.5
                    and stats.times_selected > avg_selection
                ):
                    overpowered.append(name)

                # Underpowered: low win rate OR rarely selected
                elif (
                    stats.win_rate_when_selected < avg_win_rate * 0.5
                    or stats.times_selected < avg_selection * 0.5
                ):
                    underpowered.append(name)

                # Persona-dependent: high variance across personas
                persona_rates = []
                for p_stats in persona_stats.values():
                    if name in p_stats:
                        persona_rates.append(p_stats[name]["times_selected"])

                if len(persona_rates) >= 2:
                    variance = statistics.variance(persona_rates) if len(persona_rates) > 1 else 0
                    if variance > avg_selection:
                        persona_dependent.append(name)

        return BalanceMatrix(
            persona_stats=persona_stats,
            upgrade_summaries=upgrade_summaries,
            overpowered_upgrades=overpowered,
            underpowered_upgrades=underpowered,
            persona_dependent_upgrades=persona_dependent,
        )

    def _build_fun_floor_report(
        self,
        playthroughs: list[PlaythroughEvidence],
    ) -> FunFloorReport:
        """Build fun floor report from playthroughs."""
        violations_by_persona: dict[str, int] = {}
        violation_types: dict[str, int] = {}
        total_duration_ms = 0.0

        for pt in playthroughs:
            violations_by_persona[pt.persona] = len(pt.fun_floor_violations)

            for v in pt.fun_floor_violations:
                violation_types[v.type] = violation_types.get(v.type, 0) + 1
                total_duration_ms += v.duration_ms

        total_violations = sum(violations_by_persona.values())

        # Find worst persona and type
        worst_persona = None
        worst_type = None

        if violations_by_persona:
            worst_persona = max(violations_by_persona, key=violations_by_persona.get)  # type: ignore[arg-type]

        if violation_types:
            worst_type = max(violation_types, key=violation_types.get)  # type: ignore[arg-type]

        # Fun floor passes if no persona has more than 10% violation time
        fun_floor_passed = all(pt.fun_floor_passed for pt in playthroughs)

        return FunFloorReport(
            total_violations=total_violations,
            violations_by_persona=violations_by_persona,
            violation_types=violation_types,
            total_violation_duration_ms=total_duration_ms,
            worst_persona=worst_persona,
            worst_violation_type=worst_type,
            fun_floor_passed=fun_floor_passed,
        )


# =============================================================================
# Convenience Functions
# =============================================================================


async def run_farm(
    adapter_factory: GameAdapterFactory,
    personas: list[str] | None = None,
    time_scale: float = 4.0,
    max_waves: int = 5,
    max_duration_ms: float = 60_000,
    llm_client: Any | None = None,
) -> FarmEvidence:
    """
    Convenience function to run a parallel playthrough farm.

    Args:
        adapter_factory: Factory for creating isolated game adapters
        personas: List of persona names (default: CORE_PERSONAS)
        time_scale: Game speed multiplier (4x for testing)
        max_waves: Maximum waves per playthrough
        max_duration_ms: Wall time budget in milliseconds
        llm_client: Optional LLM client for strategic decisions

    Returns:
        FarmEvidence with aggregated results
    """
    farm = PlaythroughFarm(
        adapter_factory=adapter_factory,
        llm_client=llm_client,
    )
    return await farm.run_farm(
        personas=personas,
        time_scale=time_scale,
        max_waves=max_waves,
        max_duration_ms=max_duration_ms,
    )


# =============================================================================
# Mock Adapter for Testing
# =============================================================================


class MockGameAdapter:
    """Mock game adapter for testing the farm without a real game."""

    def __init__(self, time_scale: float = 1.0):
        self.time_scale = time_scale
        self._wave = 1
        self._health = 100.0
        self._upgrades: list[str] = []
        self._enemies: list[dict[str, Any]] = []
        self._tick = 0

    async def capture_screen(self) -> bytes:
        return b"mock_screen"

    async def get_debug_state(self) -> dict[str, Any]:
        # Simulate game progression
        self._tick += 1

        # Spawn enemies periodically
        if self._tick % 10 == 0:
            self._enemies.append(
                {
                    "id": f"enemy_{self._tick}",
                    "type": "basic",
                    "position": {"x": 500, "y": 300},
                    "health": 50,
                    "damage": 10,
                }
            )

        # Wave progression
        if self._tick % 100 == 0 and self._wave < 10:
            self._wave += 1

        # Offer upgrades at wave boundaries
        upgrades = []
        if self._tick % 100 < 10:
            upgrades = [
                {"name": "damage_up", "effect": "+10% damage"},
                {"name": "speed_up", "effect": "+10% speed"},
                {"name": "health_up", "effect": "+20 max health"},
            ]

        return {
            "player": {
                "position": {"x": 400, "y": 300},
                "health": self._health,
                "upgrades": self._upgrades,
            },
            "enemies": self._enemies,
            "projectiles": [],
            "pickups": [],
            "upgrades": upgrades,
            "wave": {"number": self._wave},
        }

    async def get_audio_cues(self) -> list[dict[str, Any]]:
        return []

    async def send_action(self, action: Any) -> None:
        # Simulate action effects
        if hasattr(action, "type"):
            if action.type == "attack" and self._enemies:
                # Remove first enemy
                self._enemies.pop(0)
            elif action.type == "select_upgrade":
                upgrade_name = action.parameters.get("upgrade", "")
                if upgrade_name:
                    self._upgrades.append(upgrade_name)

        # Simulate damage from enemies
        import random

        if self._enemies and random.random() < 0.1:
            self._health -= 5

    async def start_game(self) -> None:
        self._wave = 1
        self._health = 100.0
        self._upgrades = []
        self._enemies = []
        self._tick = 0

    async def close(self) -> None:
        pass


class MockAdapterFactory:
    """Factory for creating mock game adapters."""

    async def create_context(self, time_scale: float = 1.0) -> MockGameAdapter:
        return MockGameAdapter(time_scale=time_scale)


async def run_mock_farm(
    personas: list[str] | None = None,
    max_waves: int = 3,
    max_duration_ms: float = 5_000,
) -> FarmEvidence:
    """
    Run a mock farm for testing without a real game.

    Useful for testing the farm infrastructure itself.
    """
    factory = MockAdapterFactory()
    return await run_farm(
        adapter_factory=factory,
        personas=personas or ["aggressive", "defensive", "novice"],
        time_scale=1.0,  # No scaling for mock
        max_waves=max_waves,
        max_duration_ms=max_duration_ms,
    )
