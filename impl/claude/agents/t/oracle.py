"""
OracleAgent: Differential testing oracle.

Compares outputs from multiple agents on the same inputs to detect
inconsistencies, regressions, or unexpected behavior changes.

Category Theoretic Definition: O: A × Agent[A, B]^n → DiffResult
Maps (input, agents) to differential analysis results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar, List, Tuple, Callable, Optional

from runtime.base import Agent

A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type


@dataclass
class DiffResult(Generic[B]):
    """Result of differential testing."""
    input: Any                           # The input tested
    outputs: List[Tuple[str, B]]         # List of (agent_name, output) pairs
    all_agree: bool                      # Whether all outputs are equal
    majority_output: Optional[B] = None  # Most common output (if exists)
    deviants: List[str] = field(default_factory=list)  # Agents with differing outputs
    explanation: str = ""                # Optional explanation of differences

    @property
    def agreement_rate(self) -> float:
        """Proportion of agents that agree with majority."""
        if not self.outputs:
            return 0.0
        if self.all_agree:
            return 1.0

        # Count outputs matching majority
        if self.majority_output is None:
            return 0.0

        matching = sum(
            1 for _, output in self.outputs
            if output == self.majority_output
        )
        return matching / len(self.outputs)


class OracleAgent(Agent[Tuple[A, List[Agent[A, B]]], DiffResult[B]], Generic[A, B]):
    """
    Differential testing oracle.

    Morphism: (Input, [Agent]) → DiffResult

    Executes multiple agents on the same input and compares their outputs
    to detect inconsistencies. Useful for:
    - Regression testing (compare new vs old implementation)
    - Cross-validation (compare multiple models/approaches)
    - Consensus verification (detect outliers)

    Example:
        # Compare three different implementations
        agent_v1 = OldImplementation()
        agent_v2 = NewImplementation()
        agent_v3 = ReferenceImplementation()

        oracle = OracleAgent(
            agents=[agent_v1, agent_v2, agent_v3],
            equality_fn=lambda a, b: a == b,
        )

        result = await oracle.invoke((test_input, [agent_v1, agent_v2, agent_v3]))

        if not result.all_agree:
            print(f"Disagreement detected! Deviants: {result.deviants}")
            for name, output in result.outputs:
                print(f"  {name}: {output}")
    """

    def __init__(
        self,
        agents: List[Agent[A, B]],
        equality_fn: Optional[Callable[[B, B], bool]] = None,
        majority_threshold: float = 0.5,
    ):
        """
        Initialize OracleAgent.

        Args:
            agents: List of agents to compare
            equality_fn: Function to compare outputs (default: ==)
            majority_threshold: Proportion needed for majority (0.5-1.0)
        """
        if len(agents) < 2:
            raise ValueError("OracleAgent requires at least 2 agents to compare")

        self.agents = agents
        self.equality_fn = equality_fn or (lambda a, b: a == b)
        self.majority_threshold = majority_threshold
        self.__is_test__ = True  # T-gent marker

        if not (0.5 <= majority_threshold <= 1.0):
            raise ValueError("majority_threshold must be in [0.5, 1.0]")

    @property
    def name(self) -> str:
        """Return agent name."""
        agent_names = ", ".join(a.name for a in self.agents)
        return f"OracleAgent([{agent_names}])"

    async def invoke(self, input_data: Tuple[A, List[Agent[A, B]]]) -> DiffResult[B]:
        """
        Run differential testing.

        Args:
            input_data: Tuple of (input, agents)
                       Note: agents can override the ones from __init__

        Returns:
            DiffResult with comparison results
        """
        test_input, agents = input_data

        # Use provided agents or fall back to __init__ ones
        agents_to_test = agents if agents else self.agents

        # Execute all agents on the same input
        outputs: List[Tuple[str, B]] = []
        for agent in agents_to_test:
            try:
                output = await agent.invoke(test_input)
                outputs.append((agent.name, output))
            except Exception as e:
                # Record exception as output
                outputs.append((agent.name, f"ERROR: {e}"))

        # Check if all outputs agree
        if len(outputs) < 2:
            return DiffResult(
                input=test_input,
                outputs=outputs,
                all_agree=True,
                explanation="Only one agent to compare",
            )

        first_output = outputs[0][1]
        all_agree = all(
            self.equality_fn(first_output, output)
            for _, output in outputs
        )

        if all_agree:
            return DiffResult(
                input=test_input,
                outputs=outputs,
                all_agree=True,
                majority_output=first_output,
                explanation="All agents agree",
            )

        # Find majority output
        output_counts: dict[Any, int] = {}
        output_values: dict[Any, B] = {}

        for name, output in outputs:
            # Use string representation as key for hashability
            key = str(output)
            if key not in output_counts:
                output_counts[key] = 0
                output_values[key] = output
            output_counts[key] += 1

        # Find most common output
        max_count = max(output_counts.values())
        majority_key = max(output_counts, key=lambda k: output_counts[k])
        majority_output = output_values[majority_key]

        # Check if majority threshold is met
        majority_proportion = max_count / len(outputs)

        # Find deviants (agents not matching majority)
        deviants = [
            name
            for name, output in outputs
            if not self.equality_fn(output, majority_output)
        ]

        explanation = (
            f"Agreement: {majority_proportion:.1%} "
            f"({max_count}/{len(outputs)} agents agree)"
        )

        return DiffResult(
            input=test_input,
            outputs=outputs,
            all_agree=False,
            majority_output=majority_output if majority_proportion >= self.majority_threshold else None,
            deviants=deviants,
            explanation=explanation,
        )


class RegressionOracle(OracleAgent[A, B]):
    """
    Specialized oracle for regression testing.

    Compares a reference implementation (oracle) against a system under test (SUT).
    Reports when outputs diverge.
    """

    def __init__(
        self,
        reference: Agent[A, B],
        system_under_test: Agent[A, B],
        equality_fn: Optional[Callable[[B, B], bool]] = None,
    ):
        """
        Initialize RegressionOracle.

        Args:
            reference: The reference/oracle implementation
            system_under_test: The system being tested
            equality_fn: Function to compare outputs (default: ==)
        """
        super().__init__(
            agents=[reference, system_under_test],
            equality_fn=equality_fn,
            majority_threshold=1.0,  # Both must agree
        )
        self.reference = reference
        self.sut = system_under_test

    @property
    def name(self) -> str:
        """Return agent name."""
        return f"RegressionOracle({self.reference.name} vs {self.sut.name})"

    async def invoke(self, input_data: Tuple[A, List[Agent[A, B]]]) -> DiffResult[B]:
        """
        Run regression test.

        Args:
            input_data: Tuple of (input, agents)
                       Agents are ignored; uses reference and SUT from __init__

        Returns:
            DiffResult indicating if reference and SUT agree
        """
        test_input, _ = input_data
        return await super().invoke((test_input, [self.reference, self.sut]))


# Equality functions for common types
def semantic_equality(a: str, b: str) -> bool:
    """
    Semantic string equality (case-insensitive, whitespace-normalized).

    Useful for comparing text outputs where formatting may vary.
    """
    return a.lower().strip() == b.lower().strip()


def numeric_equality(a: float, b: float, epsilon: float = 1e-6) -> bool:
    """
    Numeric equality with epsilon tolerance.

    Useful for comparing floating-point outputs.
    """
    return abs(a - b) < epsilon


def structural_equality(a: Any, b: Any) -> bool:
    """
    Deep structural equality for complex objects.

    Compares dictionaries, lists, and nested structures.
    """
    if type(a) != type(b):
        return False

    if isinstance(a, dict) and isinstance(b, dict):
        if set(a.keys()) != set(b.keys()):
            return False
        return all(structural_equality(a[k], b[k]) for k in a.keys())

    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return False
        return all(structural_equality(x, y) for x, y in zip(a, b))

    return a == b
