"""
The Cortex Assurance System v2.0: Unified Cybernetic Immune System.

Philosophy: Tests are not chores - they are Adversarial Agents,
Economic Transactions, and Causal Investigators.

This module integrates all five pillars:
1. Oracle - Metamorphic Judge (fuzzy truth)
2. Topologist - Homotopic Testing (commutativity)
3. Analyst - Counterfactual Debugging (causation)
4. Market - Portfolio Optimization (economics)
5. Red Team - Adversarial Evolution (security)

Phase 8.5 - Integration:
- Cortex: Unified controller
- Night Watch: Scheduled deep testing
- Morning Briefing: Daily report
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from .analyst import (
    CausalAnalyst,
    TestWitness,
    WitnessStore,
)
from .market import (
    BudgetManager,
    TestAsset,
    TestCost,
)
from .oracle import Oracle, OracleValidation, format_validation_report
from .red_team import RedTeam, RedTeamReport, format_red_team_report
from .topologist import (
    Topologist,
    TopologistReport,
    TypeTopology,
    format_topologist_report,
)

# =============================================================================
# Morning Briefing Types
# =============================================================================


@dataclass
class TopologistSummary:
    """Summary of Topologist findings."""

    paths_tested: int
    commutativity_violations: int
    invariance_violations: int


@dataclass
class AnalystSummary:
    """Summary of Analyst findings."""

    new_failures: int
    root_causes_identified: int
    flaky_tests_diagnosed: int


@dataclass
class RedTeamSummary:
    """Summary of Red Team findings."""

    adversarial_inputs_evolved: int
    vulnerabilities_discovered: int
    mutation_score_average: float


@dataclass
class OracleSummary:
    """Summary of Oracle findings."""

    agents_validated: int
    metamorphic_violations: int
    recommendations: list[str]


@dataclass
class BriefingReport:
    """Morning Briefing report combining all pillars."""

    timestamp: datetime
    topologist: TopologistSummary
    analyst: AnalystSummary
    red_team: RedTeamSummary
    oracle: OracleSummary
    overall_health: str  # "GREEN", "YELLOW", "RED"

    def __repr__(self) -> str:
        return f"BriefingReport({self.timestamp.date()}, health={self.overall_health})"


# =============================================================================
# The Cortex
# =============================================================================


class Cortex:
    """Unified Cortex Assurance System.

    Coordinates all five pillars to provide comprehensive
    test intelligence.
    """

    def __init__(
        self,
        oracle: Oracle | None = None,
        topology: TypeTopology | None = None,
        witness_store: WitnessStore | None = None,
    ):
        """Initialize Cortex.

        Args:
            oracle: Oracle instance (created if None)
            topology: Type topology (created if None)
            witness_store: Witness store (created if None)
        """
        # Initialize pillars
        self.oracle = oracle or Oracle()
        self.topology = topology or TypeTopology()
        self.witness_store = witness_store or WitnessStore()

        self.topologist = Topologist(self.topology, self.oracle)
        self.analyst = CausalAnalyst(self.witness_store)
        self.budget_manager = BudgetManager()
        self.red_team = RedTeam(self.oracle)

        # State
        self._agents: dict[str, Any] = {}
        self._last_briefing: BriefingReport | None = None

    def register_agent(
        self,
        agent: Any,
        input_type: str = "Any",
        output_type: str = "Any",
    ) -> None:
        """Register an agent for testing.

        Args:
            agent: Agent instance
            input_type: Input type name
            output_type: Output type name
        """
        name = getattr(agent, "name", type(agent).__name__)
        self._agents[name] = agent

        # Update topology
        self.topology.add_agent(name, input_type, output_type)
        self.topologist.register_agent(name, agent)

    def register_test(
        self,
        test_id: str,
        cost_joules: float = 1.0,
        cost_time_ms: float = 100.0,
        dependency_centrality: float = 0.5,
    ) -> None:
        """Register a test for market allocation.

        Args:
            test_id: Unique test identifier
            cost_joules: Compute cost
            cost_time_ms: Expected duration
            dependency_centrality: How central in dependency graph
        """
        asset = TestAsset(
            test_id=test_id,
            cost=TestCost(joules=cost_joules, time_ms=cost_time_ms),
            dependency_centrality=dependency_centrality,
        )
        self.budget_manager.register_test(asset)

    def record_witness(
        self,
        test_id: str,
        agent_path: list[str],
        input_data: Any,
        outcome: str,
        duration_ms: float,
        error_trace: str | None = None,
    ) -> None:
        """Record a test witness for causal analysis.

        Args:
            test_id: Test identifier
            agent_path: Agents in composition chain
            input_data: Test input
            outcome: "pass", "fail", "skip", "error"
            duration_ms: Test duration
            error_trace: Error trace if failed
        """
        witness = TestWitness(
            test_id=test_id,
            agent_path=agent_path,
            input_data=input_data,
            outcome=outcome,  # type: ignore
            duration_ms=duration_ms,
            error_trace=error_trace,
        )
        self.witness_store.record(witness)

        # Update market statistics
        self.budget_manager.market.update_statistics(
            test_id, outcome == "pass", duration_ms
        )

    # =========================================================================
    # Daytime Operations
    # =========================================================================

    async def daytime_run(
        self,
        available_tests: list[str],
        changed_files: list[str] | None = None,
    ) -> list[str]:
        """Run lean, fast tests during development.

        Args:
            available_tests: All available test IDs
            changed_files: Changed files for impact-based selection

        Returns:
            List of test IDs that were selected
        """
        # Get test assets
        raw_assets = [
            self.budget_manager.market._assets.get(t)
            for t in available_tests
            if t in self.budget_manager.market._assets
        ]
        assets = [a for a in raw_assets if a is not None]

        if not assets:
            return available_tests[:10]  # Fallback

        # Select tests using market
        selected = await self.budget_manager.select_tests(
            assets,
            changed_files,
        )

        return selected

    # =========================================================================
    # Nighttime Operations (Deep Testing)
    # =========================================================================

    async def nighttime_watch(
        self,
        agents: list[Any] | None = None,
        seed_inputs: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Run comprehensive deep testing overnight.

        Args:
            agents: Agents to test (defaults to registered)
            seed_inputs: Inputs for adversarial evolution

        Returns:
            Dictionary of results from each pillar
        """
        if agents is None:
            agents = list(self._agents.values())

        if seed_inputs is None:
            seed_inputs = ["test input", "hello world", '{"key": "value"}']

        results: dict[str, Any] = {}

        # 1. Topologist: Test commutativity
        commutativity_results = await self.topologist.fuzz_equivalent_paths(count=100)
        invariance_results = []
        for agent in agents:
            inv_result = await self.topologist.test_contextual_invariance(agent)
            invariance_results.append(inv_result)

        results["topologist"] = TopologistReport(
            commutativity_results=commutativity_results,
            invariance_results=invariance_results,
        )

        # 2. Red Team: Evolve adversarial inputs
        red_team_results: list[RedTeamReport] = []
        for agent in agents:
            report = await self.red_team.run_adversarial_campaign(agent, seed_inputs)
            red_team_results.append(report)

        results["red_team"] = red_team_results

        # 3. Oracle: Validate agents
        oracle_results: list[OracleValidation] = []
        for agent in agents:
            validation = await self.oracle.validate_agent(agent, seed_inputs)
            oracle_results.append(validation)

        results["oracle"] = oracle_results

        # 4. Analyst: Analyze any failures
        analyst_results: dict[str, Any] = {}
        failures = await self.witness_store.query(outcome="fail", limit=50)
        for failure in failures[:10]:  # Analyze top 10
            graph = await self.analyst.root_cause_analysis(failure.test_id)
            analyst_results[failure.test_id] = graph

        results["analyst"] = analyst_results

        return results

    # =========================================================================
    # Morning Briefing
    # =========================================================================

    async def morning_briefing(
        self,
        nighttime_results: dict[str, Any] | None = None,
    ) -> BriefingReport:
        """Generate morning briefing report.

        Args:
            nighttime_results: Results from nighttime_watch (or fetch from store)

        Returns:
            BriefingReport summarizing overnight findings
        """
        # Topologist summary
        topo_report: TopologistReport | None = None
        if nighttime_results and "topologist" in nighttime_results:
            topo_report = nighttime_results["topologist"]

        topo_summary = TopologistSummary(
            paths_tested=len(topo_report.commutativity_results) if topo_report else 0,
            commutativity_violations=topo_report.commutativity_violations
            if topo_report
            else 0,
            invariance_violations=topo_report.invariance_violations
            if topo_report
            else 0,
        )

        # Analyst summary
        yesterday = datetime.now() - timedelta(days=1)
        new_failures = await self.witness_store.query(outcome="fail", since=yesterday)

        analyst_summary = AnalystSummary(
            new_failures=len(new_failures),
            root_causes_identified=len(nighttime_results.get("analyst", {}))
            if nighttime_results
            else 0,
            flaky_tests_diagnosed=0,  # Would come from flakiness analysis
        )

        # Red Team summary
        red_team_reports: list[RedTeamReport] = (
            nighttime_results.get("red_team", []) if nighttime_results else []
        )
        total_vulns = sum(len(r.vulnerabilities) for r in red_team_reports)
        total_evolved = sum(r.population_size * r.generations for r in red_team_reports)

        red_team_summary = RedTeamSummary(
            adversarial_inputs_evolved=total_evolved,
            vulnerabilities_discovered=total_vulns,
            mutation_score_average=0.0,  # Would come from mutation testing
        )

        # Oracle summary
        oracle_results: list[OracleValidation] = (
            nighttime_results.get("oracle", []) if nighttime_results else []
        )
        total_violations = sum(r.failed for r in oracle_results)
        recommendations = []
        for r in oracle_results:
            if r.validity_score < 0.8:
                recommendations.append(
                    f"Investigate {r.agent_name} metamorphic failures"
                )

        oracle_summary = OracleSummary(
            agents_validated=len(oracle_results),
            metamorphic_violations=total_violations,
            recommendations=recommendations,
        )

        # Overall health
        if (
            topo_summary.commutativity_violations > 5
            or total_vulns > 3
            or total_violations > 10
        ):
            health = "RED"
        elif (
            topo_summary.commutativity_violations > 0
            or total_vulns > 0
            or total_violations > 3
        ):
            health = "YELLOW"
        else:
            health = "GREEN"

        briefing = BriefingReport(
            timestamp=datetime.now(),
            topologist=topo_summary,
            analyst=analyst_summary,
            red_team=red_team_summary,
            oracle=oracle_summary,
            overall_health=health,
        )

        self._last_briefing = briefing
        return briefing


# =============================================================================
# Report Generation
# =============================================================================


def format_briefing_report(briefing: BriefingReport) -> str:
    """Format morning briefing for display."""
    health_emoji = {
        "GREEN": "[OK]",
        "YELLOW": "[WARN]",
        "RED": "[ALERT]",
    }

    lines = [
        "=" * 60,
        "            CORTEX MORNING BRIEFING                     ",
        "=" * 60,
        f" Date: {briefing.timestamp.strftime('%Y-%m-%d %H:%M')}",
        f" Overall Health: {health_emoji.get(briefing.overall_health, '')} {briefing.overall_health}",
        "-" * 60,
        " TOPOLOGIST:",
        f"   Paths Tested: {briefing.topologist.paths_tested}",
        f"   Commutativity Violations: {briefing.topologist.commutativity_violations}",
        f"   Invariance Violations: {briefing.topologist.invariance_violations}",
        "",
        " ANALYST:",
        f"   New Failures: {briefing.analyst.new_failures}",
        f"   Root Causes Identified: {briefing.analyst.root_causes_identified}",
        f"   Flaky Tests Diagnosed: {briefing.analyst.flaky_tests_diagnosed}",
        "",
        " RED TEAM:",
        f"   Adversarial Inputs Evolved: {briefing.red_team.adversarial_inputs_evolved}",
        f"   Vulnerabilities Discovered: {briefing.red_team.vulnerabilities_discovered}",
        f"   Mutation Score Avg: {briefing.red_team.mutation_score_average:.1%}",
        "",
        " ORACLE:",
        f"   Agents Validated: {briefing.oracle.agents_validated}",
        f"   Metamorphic Violations: {briefing.oracle.metamorphic_violations}",
    ]

    if briefing.oracle.recommendations:
        lines.append("   Recommendations:")
        for rec in briefing.oracle.recommendations:
            lines.append(f"     - {rec}")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_full_report(
    briefing: BriefingReport,
    topo_report: TopologistReport | None = None,
    oracle_results: list[OracleValidation] | None = None,
    red_team_results: list[RedTeamReport] | None = None,
) -> str:
    """Format comprehensive report combining all pillars."""
    sections = [format_briefing_report(briefing)]

    if topo_report:
        sections.append(format_topologist_report(topo_report))

    if oracle_results:
        for result in oracle_results:
            sections.append(format_validation_report(result))

    if red_team_results:
        for red_team_result in red_team_results:
            sections.append(format_red_team_report(red_team_result))

    return "\n\n".join(sections)
