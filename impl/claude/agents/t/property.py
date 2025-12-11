"""
PropertyAgent: Property-based testing with generators.

Generates test cases based on properties and validates agent behavior
across a wide input space. Inspired by QuickCheck/Hypothesis.

Category Theoretic Definition: P_φ: Gen[A] × Agent[A, B] → TestResult
Maps (generator, agent) pairs to test results, verifying property φ holds.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, List, Optional, Tuple, TypeVar

from runtime.base import Agent

A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type


class Generator(ABC, Generic[A]):
    """
    Abstract base class for test data generators.

    A generator produces random test cases of type A.
    Generators are composable and can be combined.
    """

    @abstractmethod
    def generate(self, rng: random.Random) -> A:
        """Generate a single test case."""
        pass

    def many(self, count: int, seed: Optional[int] = None) -> List[A]:
        """
        Generate multiple test cases.

        Args:
            count: Number of test cases to generate
            seed: Random seed for reproducibility

        Returns:
            List of generated test cases
        """
        rng = random.Random(seed)
        return [self.generate(rng) for _ in range(count)]


class IntGenerator(Generator[int]):
    """Generate random integers in a range."""

    def __init__(self, min_val: int = 0, max_val: int = 100):
        self.min_val = min_val
        self.max_val = max_val

    def generate(self, rng: random.Random) -> int:
        return rng.randint(self.min_val, self.max_val)


class StringGenerator(Generator[str]):
    """Generate random strings."""

    def __init__(
        self,
        min_length: int = 1,
        max_length: int = 20,
        charset: str = "abcdefghijklmnopqrstuvwxyz",
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.charset = charset

    def generate(self, rng: random.Random) -> str:
        length = rng.randint(self.min_length, self.max_length)
        return "".join(rng.choice(self.charset) for _ in range(length))


class ListGenerator(Generator[List[A]], Generic[A]):
    """Generate random lists of elements."""

    def __init__(
        self,
        element_gen: Generator[A],
        min_length: int = 0,
        max_length: int = 10,
    ):
        self.element_gen = element_gen
        self.min_length = min_length
        self.max_length = max_length

    def generate(self, rng: random.Random) -> List[A]:
        length = rng.randint(self.min_length, self.max_length)
        return [self.element_gen.generate(rng) for _ in range(length)]


class ConstGenerator(Generator[A], Generic[A]):
    """Generator that always returns the same value."""

    def __init__(self, value: A):
        self.value = value

    def generate(self, rng: random.Random) -> A:
        return self.value


class ChoiceGenerator(Generator[A], Generic[A]):
    """Generator that randomly picks from a list of values."""

    def __init__(self, choices: List[A]):
        if not choices:
            raise ValueError("ChoiceGenerator requires at least one choice")
        self.choices = choices

    def generate(self, rng: random.Random) -> A:
        return rng.choice(self.choices)


@dataclass
class PropertyTestResult:
    """Result of property-based testing."""

    total_cases: int  # Total test cases run
    passed_cases: int  # Cases that passed
    failed_cases: int  # Cases that failed
    failures: List[Tuple[A, str]] = field(default_factory=list)  # (input, error) pairs
    property_name: str = ""  # Name of property being tested

    @property
    def success_rate(self) -> float:
        """Proportion of cases that passed."""
        if self.total_cases == 0:
            return 0.0
        return self.passed_cases / self.total_cases

    @property
    def passed(self) -> bool:
        """Whether all test cases passed."""
        return self.failed_cases == 0


class PropertyAgent(
    Agent[Tuple[Generator[A], Callable[[A, B], bool]], PropertyTestResult],
    Generic[A, B],
):
    """
    Property-based testing agent.

    Morphism: (Gen[A], Agent[A, B], Property[A, B]) → TestResult

    Generates test cases using a generator and verifies a property
    holds for all cases when passed through the target agent.

    Example:
        # Property: output length should match input length
        def length_preserved(input: str, output: str) -> bool:
            return len(input) == len(output)

        # Test with random strings
        gen = StringGenerator(min_length=1, max_length=50)
        agent = IdentityAgent()  # Simple identity agent

        prop_agent = PropertyAgent(
            agent=agent,
            property_fn=length_preserved,
            num_cases=100,
        )

        result = await prop_agent.invoke((gen, length_preserved))
        assert result.passed
    """

    def __init__(
        self,
        agent: Agent[A, B],
        property_fn: Callable[[A, B], bool],
        num_cases: int = 100,
        seed: Optional[int] = None,
        property_name: str = "property",
    ):
        """
        Initialize PropertyAgent.

        Args:
            agent: The agent to test
            property_fn: Function that checks property: (input, output) -> bool
            num_cases: Number of test cases to generate
            seed: Random seed for reproducibility
            property_name: Name of the property being tested
        """
        self.agent = agent
        self.property_fn = property_fn
        self.num_cases = num_cases
        self.seed = seed
        self.property_name = property_name
        self.__is_test__ = True  # T-gent marker

    @property
    def name(self) -> str:
        """Return agent name."""
        return f"PropertyAgent({self.property_name})"

    async def invoke(
        self, input_data: Tuple[Generator[A], Callable[[A, B], bool]]
    ) -> PropertyTestResult:
        """
        Run property-based tests.

        Args:
            input_data: Tuple of (generator, property_function)
                       Note: property_fn can override the one from __init__

        Returns:
            PropertyTestResult with pass/fail counts and failures
        """
        generator, property_fn = input_data

        # Use provided property_fn or fall back to __init__ one
        prop = property_fn if property_fn else self.property_fn

        rng = random.Random(self.seed)
        passed_cases = 0
        failed_cases = 0
        failures: List[Tuple[A, str]] = []

        # Generate and test cases
        for i in range(self.num_cases):
            try:
                # Generate test case
                test_input = generator.generate(rng)

                # Run through agent
                output = await self.agent.invoke(test_input)

                # Check property
                if prop(test_input, output):
                    passed_cases += 1
                else:
                    failed_cases += 1
                    failures.append(
                        (
                            test_input,
                            f"Property failed for input: {test_input}, output: {output}",
                        )
                    )

            except Exception as e:
                failed_cases += 1
                failures.append((test_input, f"Exception: {e}"))

        return PropertyTestResult(
            total_cases=self.num_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            failures=failures,
            property_name=self.property_name,
        )


# Common properties
def identity_property(input: A, output: B) -> bool:
    """Property: output should equal input."""
    return input == output


def not_none_property(input: A, output: B) -> bool:
    """Property: output should not be None."""
    return output is not None


def length_preserved_property(input: Any, output: Any) -> bool:
    """Property: output length should equal input length (for sequences)."""
    try:
        return len(input) == len(output)
    except TypeError:
        return True  # Not applicable to non-sequences


def type_preserved_property(input: A, output: B) -> bool:
    """Property: output type should match input type."""
    return type(input) is type(output)


# Common generators
integers = IntGenerator(0, 100)
small_integers = IntGenerator(0, 10)
positive_integers = IntGenerator(1, 1000)
strings = StringGenerator(1, 20)
short_strings = StringGenerator(1, 5)
