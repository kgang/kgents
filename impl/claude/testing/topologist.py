"""
The Topologist: Homotopic Testing for Agent Composition.

Philosophy: Verify that the composition graph holds its shape under deformation.
In Category Theory, a commutative diagram asserts that different paths between
two points must yield equivalent results.

Research Basis: Homotopy Type Theory, Category Theory (Commutative Diagrams)

Phase 8.1 - Foundation:
- TypeTopology: Graph of agent type signatures
- NoiseFunctor: Contextual noise for invariance testing
- Topologist: Commutativity and invariance verification
"""

import random
from dataclasses import dataclass, field
from typing import Any, Callable

from .oracle import Oracle

# =============================================================================
# Core Types
# =============================================================================


@dataclass
class AgentSignature:
    """Type signature of an agent."""

    input_type: str
    output_type: str
    name: str = ""

    def __repr__(self) -> str:
        return f"{self.name}: {self.input_type} -> {self.output_type}"


@dataclass
class CommutativityResult:
    """Result of testing path commutativity."""

    path_a: list[str]
    path_b: list[str]
    input_data: Any
    result_a: Any
    result_b: Any
    equivalent: bool
    similarity: float
    error: str | None = None

    def __repr__(self) -> str:
        status = "COMMUTES" if self.equivalent else "FAILS"
        path_a_str = " >> ".join(self.path_a)
        path_b_str = " >> ".join(self.path_b)
        return f"CommutativityResult({path_a_str} vs {path_b_str}: {status}, sim={self.similarity:.2f})"


@dataclass
class ContextViolation:
    """A violation of contextual invariance."""

    functor: str
    baseline: Any
    noisy_result: Any
    similarity: float = 0.0


@dataclass
class InvarianceResult:
    """Result of testing contextual invariance."""

    agent: str
    contexts_tested: int
    violations: list[ContextViolation]
    invariant: bool

    def __repr__(self) -> str:
        status = "INVARIANT" if self.invariant else f"VIOLATED ({len(self.violations)})"
        return (
            f"InvarianceResult({self.agent}: {status}, {self.contexts_tested} contexts)"
        )


# =============================================================================
# Type Topology
# =============================================================================


@dataclass
class TypeTopology:
    """Graph of agent type signatures with homotopic structure.

    This represents the "shape" of the agent composition space.
    Agents are nodes, composability is edges.
    """

    agents: dict[str, AgentSignature] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)

    def add_agent(self, name: str, input_type: str, output_type: str) -> None:
        """Add an agent to the topology."""
        self.agents[name] = AgentSignature(
            name=name, input_type=input_type, output_type=output_type
        )
        self._update_edges()

    def _update_edges(self) -> None:
        """Update edges based on type compatibility."""
        self.edges = []
        for a_name, a_sig in self.agents.items():
            for b_name, b_sig in self.agents.items():
                if self._types_compatible(a_sig.output_type, b_sig.input_type):
                    self.edges.append((a_name, b_name))

    def _types_compatible(self, output_type: str, input_type: str) -> bool:
        """Check if types are compatible for composition."""
        # Simple compatibility: exact match or Any
        if output_type == input_type:
            return True
        if "Any" in (output_type, input_type):
            return True
        # Subtype checking (simplified)
        if input_type == "str" and output_type in ("str", "int", "float"):
            return True  # Can stringify anything
        return False

    def equivalent_paths(
        self, start: str, end: str, max_depth: int = 5
    ) -> list[list[str]]:
        """Find all paths between two agents (for commutativity testing).

        Args:
            start: Starting agent name
            end: Ending agent name
            max_depth: Maximum path length

        Returns:
            List of paths (each path is a list of agent names)
        """
        if start not in self.agents or end not in self.agents:
            return []

        paths = []
        self._find_paths(start, end, [start], set(), max_depth, paths)
        return paths

    def _find_paths(
        self,
        current: str,
        end: str,
        path: list[str],
        visited: set[str],
        depth: int,
        paths: list[list[str]],
    ) -> None:
        """DFS to find all paths."""
        if depth == 0:
            return

        if current == end:
            paths.append(path.copy())
            return

        visited.add(current)

        for edge_from, edge_to in self.edges:
            if edge_from == current and edge_to not in visited:
                path.append(edge_to)
                self._find_paths(edge_to, end, path, visited, depth - 1, paths)
                path.pop()

        visited.remove(current)

    @classmethod
    def from_agents(cls, agents: list[Any]) -> "TypeTopology":
        """Build topology from a list of agents.

        Agents should have name, input_type, and output_type attributes,
        or we infer from type hints.
        """
        topology = cls()

        for agent in agents:
            name = getattr(agent, "name", type(agent).__name__)
            input_type = getattr(agent, "input_type", "Any")
            output_type = getattr(agent, "output_type", "Any")
            topology.add_agent(name, input_type, output_type)

        return topology


# =============================================================================
# Noise Functors
# =============================================================================


class NoiseFunctor:
    """Wrapper that applies contextual noise to test invariance.

    A "well-behaved" agent should produce equivalent results
    regardless of formatting noise.
    """

    NOISE_TYPES = [
        "add_whitespace",
        "wrap_in_markdown",
        "add_logging",
        "change_persona",
        "add_prefix_suffix",
    ]

    def __init__(self, noise_type: str):
        """Initialize noise functor.

        Args:
            noise_type: Type of noise to apply
        """
        self.noise_type = noise_type

    def lift(self, agent: Any) -> "NoisyAgent":
        """Lift agent into noisy context."""
        return NoisyAgent(agent, self.noise_type)

    @classmethod
    def all_functors(cls) -> list["NoiseFunctor"]:
        """Get all noise functors."""
        return [cls(noise_type) for noise_type in cls.NOISE_TYPES]


class NoisyAgent:
    """Agent wrapped with contextual noise."""

    def __init__(self, base_agent: Any, noise_type: str):
        self.base_agent = base_agent
        self.noise_type = noise_type
        self.name = f"{getattr(base_agent, 'name', 'Agent')}+{noise_type}"

    async def invoke(self, input_data: Any) -> Any:
        """Invoke with noisy input."""
        noisy_input = self._apply_noise(input_data)
        return await self.base_agent.invoke(noisy_input)

    def _apply_noise(self, data: Any) -> Any:
        """Apply noise transformation to input."""
        if not isinstance(data, str):
            data = str(data)

        if self.noise_type == "add_whitespace":
            return f"  {data}  \n\n"
        elif self.noise_type == "wrap_in_markdown":
            return f"```\n{data}\n```"
        elif self.noise_type == "add_logging":
            return f"[DEBUG] Processing: {data}"
        elif self.noise_type == "change_persona":
            return f"As an expert, please handle: {data}"
        elif self.noise_type == "add_prefix_suffix":
            return f"BEGIN\n{data}\nEND"
        else:
            return data


# =============================================================================
# The Topologist
# =============================================================================


class Topologist:
    """Homotopic test generator verifying diagram commutativity.

    The Topologist doesn't just test paths - it tests INVARIANTS.
    If Translate >> Summarize ≠ Summarize >> Translate, that's a
    semantic bug in how agents compose.
    """

    def __init__(
        self,
        topology: TypeTopology,
        oracle: Oracle,
        agent_resolver: Callable[[str], Any] | None = None,
    ):
        """Initialize Topologist.

        Args:
            topology: Type topology of agents
            oracle: Oracle for semantic equivalence checking
            agent_resolver: Function to resolve agent name to agent instance
        """
        self.topology = topology
        self.oracle = oracle
        self._agents: dict[str, Any] = {}
        self._resolver = agent_resolver

    def register_agent(self, name: str, agent: Any) -> None:
        """Register an agent instance for testing."""
        self._agents[name] = agent

    def _resolve(self, name: str) -> Any:
        """Resolve agent name to instance."""
        if name in self._agents:
            return self._agents[name]
        if self._resolver:
            return self._resolver(name)
        raise ValueError(f"Unknown agent: {name}")

    async def test_commutativity(
        self,
        path_a: list[str],
        path_b: list[str],
        input_gen: Callable[[], Any],
    ) -> CommutativityResult:
        """Test if two paths yield equivalent results.

        Args:
            path_a: First path (list of agent names)
            path_b: Second path (list of agent names)
            input_gen: Function to generate test input

        Returns:
            CommutativityResult with comparison details
        """
        try:
            # Compose paths
            agents_a = [self._resolve(n) for n in path_a]
            agents_b = [self._resolve(n) for n in path_b]

            composed_a = self._compose(agents_a)
            composed_b = self._compose(agents_b)

            # Generate input and run both paths
            input_data = input_gen()
            result_a = await composed_a.invoke(input_data)
            result_b = await composed_b.invoke(input_data)

            # Use Oracle for semantic equivalence
            equivalent = await self.oracle.semantically_equivalent(result_a, result_b)
            similarity = await self.oracle.similarity(result_a, result_b)

            return CommutativityResult(
                path_a=path_a,
                path_b=path_b,
                input_data=input_data,
                result_a=result_a,
                result_b=result_b,
                equivalent=equivalent,
                similarity=similarity,
            )

        except Exception as e:
            return CommutativityResult(
                path_a=path_a,
                path_b=path_b,
                input_data=None,
                result_a=None,
                result_b=None,
                equivalent=False,
                similarity=0.0,
                error=str(e),
            )

    def _compose(self, agents: list[Any]) -> Any:
        """Compose a list of agents into one."""
        if len(agents) == 1:
            return agents[0]

        class ComposedAgent:
            def __init__(inner_self, agents: list[Any]):
                inner_self.agents = agents
                inner_self.name = " >> ".join(
                    getattr(a, "name", type(a).__name__) for a in agents
                )

            async def invoke(inner_self, data: Any) -> Any:
                result = data
                for agent in inner_self.agents:
                    result = await agent.invoke(result)
                return result

        return ComposedAgent(agents)

    async def test_contextual_invariance(
        self,
        agent: Any,
        noise_functors: list[NoiseFunctor] | None = None,
        input_data: Any = None,
    ) -> InvarianceResult:
        """Test agent produces equivalent results across contexts.

        Args:
            agent: Agent to test
            noise_functors: List of noise functors (defaults to all)
            input_data: Input data to test with

        Returns:
            InvarianceResult with violations
        """
        if noise_functors is None:
            noise_functors = NoiseFunctor.all_functors()

        if input_data is None:
            input_data = "test input"

        # Get baseline
        baseline = await agent.invoke(input_data)

        violations = []
        for functor in noise_functors:
            lifted = functor.lift(agent)
            try:
                noisy_result = await lifted.invoke(input_data)

                equivalent = await self.oracle.semantically_equivalent(
                    baseline, noisy_result
                )
                similarity = await self.oracle.similarity(baseline, noisy_result)

                if not equivalent:
                    violations.append(
                        ContextViolation(
                            functor=functor.noise_type,
                            baseline=baseline,
                            noisy_result=noisy_result,
                            similarity=similarity,
                        )
                    )
            except Exception:
                # Noise caused error - that's a violation
                violations.append(
                    ContextViolation(
                        functor=functor.noise_type,
                        baseline=baseline,
                        noisy_result="ERROR",
                        similarity=0.0,
                    )
                )

        agent_name = getattr(agent, "name", type(agent).__name__)
        return InvarianceResult(
            agent=agent_name,
            contexts_tested=len(noise_functors),
            violations=violations,
            invariant=len(violations) == 0,
        )

    async def fuzz_equivalent_paths(
        self, count: int = 100
    ) -> list[CommutativityResult]:
        """Find and test all equivalent path pairs.

        Args:
            count: Maximum number of tests to run

        Returns:
            List of CommutativityResult
        """
        results = []

        # Find all (start, end) pairs with multiple paths
        for start in self.topology.agents:
            for end in self.topology.agents:
                paths = self.topology.equivalent_paths(start, end)
                if len(paths) >= 2:
                    # Test pairs of equivalent paths
                    for i, path_a in enumerate(paths[:5]):  # Limit to 5 paths
                        for path_b in paths[i + 1 : 5]:

                            def make_gen(s=start):
                                return lambda: self._sample_input(s)

                            result = await self.test_commutativity(
                                path_a, path_b, make_gen()
                            )
                            results.append(result)

                            if len(results) >= count:
                                return results

        return results

    def _sample_input(self, type_name: str) -> Any:
        """Generate sample input for a type."""
        samples = {
            "str": ["hello world", "test input", "sample data"],
            "int": [0, 1, 42, -1, 100],
            "float": [0.0, 1.0, 3.14, -1.5],
            "list": [[], [1, 2, 3], ["a", "b"]],
            "dict": [{}, {"key": "value"}, {"a": 1, "b": 2}],
            "Any": ["default input"],
        }
        choices = samples.get(type_name, samples["Any"])
        return random.choice(choices)


# =============================================================================
# Report Generation
# =============================================================================


@dataclass
class TopologistReport:
    """Summary report from Topologist testing."""

    commutativity_results: list[CommutativityResult]
    invariance_results: list[InvarianceResult]

    @property
    def commutativity_violations(self) -> int:
        """Count of commutativity violations."""
        return sum(1 for r in self.commutativity_results if not r.equivalent)

    @property
    def invariance_violations(self) -> int:
        """Count of invariance violations."""
        return sum(len(r.violations) for r in self.invariance_results)

    @property
    def total_tests(self) -> int:
        """Total number of tests run."""
        return len(self.commutativity_results) + len(self.invariance_results)


def format_topologist_report(report: TopologistReport) -> str:
    """Format Topologist report for display."""
    lines = [
        "=" * 60,
        "              TOPOLOGIST REPORT                          ",
        "=" * 60,
        f" Commutativity Tests: {len(report.commutativity_results)}",
        f"   Violations: {report.commutativity_violations}",
        f" Invariance Tests: {len(report.invariance_results)}",
        f"   Violations: {report.invariance_violations}",
        "-" * 60,
    ]

    if report.commutativity_violations > 0:
        lines.append(" COMMUTATIVITY VIOLATIONS:")
        for r in report.commutativity_results:
            if not r.equivalent:
                lines.append(f"   {' >> '.join(r.path_a)} vs {' >> '.join(r.path_b)}")
                lines.append(f"      Similarity: {r.similarity:.2f}")

    if report.invariance_violations > 0:
        lines.append(" INVARIANCE VIOLATIONS:")
        for r in report.invariance_results:
            for v in r.violations:
                lines.append(f"   {r.agent} + {v.functor}: sim={v.similarity:.2f}")

    lines.append("=" * 60)
    return "\n".join(lines)
