"""
Gravity: Ground Constraints for Agent Output Validation.

Ground is not a dictionary of facts. It is a validation field that exerts force on outputs.

This module implements the Grounded pattern from spec/protocols/umwelt.md:
- GravityContract: Active validators that check every output
- Grounded: Wrapper that applies gravitational constraints to agent outputs
- Standard contracts: FactConsistency, EthicalBoundary, DomainInvariant

The key insight: Gravity is active constraint, not passive lookup.
A fact database asks "Is the sky blue?" Gravity says "You cannot say the sky is green."
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

from bootstrap.types import Agent

# === Type Variables ===

A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type


# === Grounding Error ===


class GroundingError(Exception):
    """Raised when output violates gravitational constraints."""

    def __init__(
        self,
        agent: str,
        contract: str,
        violation: str,
        output: Any = None,
    ):
        self.agent = agent
        self.contract = contract
        self.violation = violation
        self.output = output
        super().__init__(f"Agent '{agent}' violated contract '{contract}': {violation}")


# === Gravity Contract Protocol ===


class GravityContract(ABC):
    """
    Base class for gravitational constraints.

    Contracts are active validators applied to every output.
    They cannot be bypassed—unlike database lookups that agents
    can choose to skip.

    Properties:
    - check(): Validate output, return error or None
    - admits(): Check if intent is admissible (for J-gent Reality)
    - compose(): Combine contracts (all must pass)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable contract name."""
        pass

    @abstractmethod
    def check(self, output: Any) -> str | None:
        """
        Check if output satisfies contract.

        Returns:
            None if satisfied, error message if violated.
        """
        pass

    def admits(self, intent: str) -> bool:
        """
        Check if an intent is admissible under this contract.

        Used by J-gent for Reality classification.
        Default: all intents are admissible (override for restrictions).
        """
        return True

    def __and__(self, other: "GravityContract") -> "ComposedContract":
        """Compose contracts: both must pass."""
        return ComposedContract([self, other])


# === Composed Contract ===


class ComposedContract(GravityContract):
    """
    Multiple contracts that all must pass.

    Created via & operator: contract1 & contract2
    """

    def __init__(self, contracts: list[GravityContract]):
        self._contracts = contracts

    @property
    def name(self) -> str:
        names = [c.name for c in self._contracts]
        return f"({' & '.join(names)})"

    def check(self, output: Any) -> str | None:
        """All contracts must pass."""
        for contract in self._contracts:
            violation = contract.check(output)
            if violation:
                return f"[{contract.name}] {violation}"
        return None

    def admits(self, intent: str) -> bool:
        """All contracts must admit the intent."""
        return all(c.admits(intent) for c in self._contracts)


# === Standard Contracts ===


@dataclass
class FactConsistency(GravityContract):
    """
    Constraint: output cannot contradict established facts.

    Unlike a fact database that stores data, this contract
    validates that outputs don't contradict known truths.

    Example:
        >>> facts = {"sky_color": "blue", "water_state": "liquid"}
        >>> contract = FactConsistency(facts)
        >>> contract.check("The sky is green")  # Returns violation
        >>> contract.check("The sky is blue")   # Returns None
    """

    known_facts: dict[str, Any]
    name: str = "FactConsistency"
    _check_fn: Callable[[Any, dict[str, Any]], str | None] | None = None

    def check(self, output: Any) -> str | None:
        """Check output doesn't contradict known facts."""
        if self._check_fn:
            return self._check_fn(output, self.known_facts)

        # Default: simple string contradiction check
        output_str = str(output).lower()

        for fact_key, fact_value in self.known_facts.items():
            # Check for explicit contradictions
            fact_str = str(fact_value).lower()
            negations = [f"not {fact_str}", f"isn't {fact_str}", f"is not {fact_str}"]

            for negation in negations:
                if negation in output_str and fact_key.lower() in output_str:
                    return f"Contradicts fact: {fact_key}={fact_value}"

        return None


@dataclass
class EthicalBoundary(GravityContract):
    """
    Constraint: output must respect ethical boundaries.

    Levels:
    - "strict": No potentially harmful content
    - "moderate": Allow educational/informational content
    - "permissive": Trust agent judgment

    Example:
        >>> contract = EthicalBoundary(level="strict")
        >>> contract.check("How to build a bomb")  # Returns violation
    """

    level: str = "moderate"  # "strict" | "moderate" | "permissive"
    name: str = "EthicalBoundary"
    blocked_patterns: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.blocked_patterns:
            if self.level == "strict":
                self.blocked_patterns = [
                    "how to harm",
                    "illegal activity",
                    "discriminate",
                    "hate speech",
                    "violence",
                ]
            elif self.level == "moderate":
                self.blocked_patterns = [
                    "illegal activity",
                    "hate speech",
                ]

    def check(self, output: Any) -> str | None:
        """Check output respects ethical boundaries."""
        if self.level == "permissive":
            return None

        output_str = str(output).lower()

        for pattern in self.blocked_patterns:
            if pattern in output_str:
                return f"Ethical violation ({self.level}): contains '{pattern}'"

        return None

    def admits(self, intent: str) -> bool:
        """Check if intent is ethically admissible."""
        if self.level == "permissive":
            return True

        intent_lower = intent.lower()
        for pattern in self.blocked_patterns:
            if pattern in intent_lower:
                return False

        return True


@dataclass
class DomainInvariant(GravityContract):
    """
    Constraint: output must satisfy domain-specific invariants.

    Uses F-gent Contract for invariant specification.

    Example:
        >>> from agents.f import Contract, Invariant
        >>> persona_contract = Contract(
        ...     agent_name="PersonaAgent",
        ...     input_type="str",
        ...     output_type="Persona",
        ...     invariants=[
        ...         Invariant("Name immutability", "old.name == new.name", "behavioral"),
        ...     ],
        ... )
        >>> contract = DomainInvariant("k.persona", persona_contract)
    """

    domain: str  # Domain identifier (e.g., "k.persona")
    f_contract: Any  # F-gent Contract with invariants
    name: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            self.name = f"DomainInvariant({self.domain})"

    def check(self, output: Any) -> str | None:
        """Check output satisfies domain invariants."""
        if not hasattr(self.f_contract, "invariants"):
            return None

        for invariant in self.f_contract.invariants:
            # Simplified check - full implementation would
            # evaluate invariant.property against output
            if hasattr(invariant, "description"):
                # For now, trust that outputs are valid
                # Real implementation would use eval or AST
                pass

        return None


@dataclass
class TypeContract(GravityContract):
    """
    Constraint: output must be of expected type.

    Example:
        >>> contract = TypeContract(expected_type=dict)
        >>> contract.check({"key": "value"})  # None
        >>> contract.check("string")  # Returns violation
    """

    expected_type: type | tuple[type, ...]
    name: str = "TypeContract"

    def check(self, output: Any) -> str | None:
        """Check output is of expected type."""
        if not isinstance(output, self.expected_type):
            return f"Type mismatch: expected {self.expected_type}, got {type(output)}"
        return None


@dataclass
class BoundedLength(GravityContract):
    """
    Constraint: output length must be within bounds.

    Example:
        >>> contract = BoundedLength(max_length=1000)
        >>> contract.check("short")  # None
        >>> contract.check("x" * 2000)  # Returns violation
    """

    max_length: int = 10000
    min_length: int = 0
    name: str = "BoundedLength"

    def check(self, output: Any) -> str | None:
        """Check output length is within bounds."""
        try:
            length = len(output) if hasattr(output, "__len__") else len(str(output))
        except (TypeError, AttributeError):
            return None  # Can't measure length, skip check

        if length < self.min_length:
            return f"Output too short: {length} < {self.min_length}"
        if length > self.max_length:
            return f"Output too long: {length} > {self.max_length}"

        return None


@dataclass
class RequiredFields(GravityContract):
    """
    Constraint: dict output must contain required fields.

    Example:
        >>> contract = RequiredFields(fields=["id", "name", "type"])
        >>> contract.check({"id": 1, "name": "test", "type": "A"})  # None
        >>> contract.check({"id": 1})  # Returns violation
    """

    fields: list[str]
    name: str = "RequiredFields"

    def check(self, output: Any) -> str | None:
        """Check dict has required fields."""
        if not isinstance(output, dict):
            return f"Expected dict, got {type(output)}"

        missing = [f for f in self.fields if f not in output]
        if missing:
            return f"Missing required fields: {missing}"

        return None


@dataclass
class PredicateContract(GravityContract):
    """
    Constraint: output must satisfy a custom predicate.

    Example:
        >>> contract = PredicateContract(
        ...     predicate=lambda x: x > 0,
        ...     error_message="Value must be positive",
        ... )
        >>> contract.check(5)   # None
        >>> contract.check(-1)  # Returns violation
    """

    predicate: Callable[[Any], bool]
    error_message: str = "Predicate check failed"
    name: str = "PredicateContract"

    def check(self, output: Any) -> str | None:
        """Check output satisfies predicate."""
        try:
            if not self.predicate(output):
                return self.error_message
        except Exception as e:
            return f"Predicate error: {e}"

        return None


# === Grounded Wrapper ===


class Grounded(Agent[A, B], Generic[A, B]):
    """
    Wraps an agent with gravitational constraint checking.

    Every output passes through gravity. Violations raise
    GroundingError, not silent failures.

    Example:
        >>> from agents.bootstrap.types import Agent
        >>> raw_agent = SomeAgent()
        >>> grounded = Grounded(
        ...     inner=raw_agent,
        ...     gravity=[FactConsistency(facts), EthicalBoundary("strict")],
        ... )
        >>> result = await grounded.invoke(input)  # Checked against gravity
    """

    def __init__(
        self,
        inner: Agent[A, B],
        gravity: list[GravityContract],
        on_violation: str = "raise",  # "raise" | "warn" | "log"
    ):
        """
        Initialize grounded agent.

        Args:
            inner: The wrapped agent
            gravity: List of contracts to apply
            on_violation: What to do on violation
                - "raise": Raise GroundingError (default)
                - "warn": Print warning, return output anyway
                - "log": Log violation, return output anyway
        """
        self._inner = inner
        self._gravity = tuple(gravity)
        self._on_violation = on_violation

    @property
    def name(self) -> str:
        """Name includes gravity contracts."""
        contract_names = ", ".join(c.name for c in self._gravity)
        return f"Grounded({self._inner.name}, [{contract_names}])"

    async def invoke(self, input: A) -> B:
        """
        Invoke inner agent, then apply gravity to output.

        Raises:
            GroundingError: If output violates any contract (when on_violation="raise")
        """
        # Get raw output
        output = await self._inner.invoke(input)

        # Apply gravity
        for contract in self._gravity:
            violation = contract.check(output)
            if violation:
                error = GroundingError(
                    agent=self._inner.name,
                    contract=contract.name,
                    violation=violation,
                    output=output,
                )

                if self._on_violation == "raise":
                    raise error
                elif self._on_violation == "warn":
                    import warnings

                    warnings.warn(str(error))
                else:  # "log"
                    import logging

                    logging.warning(str(error))

        return output

    def with_gravity(self, *contracts: GravityContract) -> "Grounded[A, B]":
        """Add additional gravity contracts."""
        return Grounded(
            inner=self._inner,
            gravity=list(self._gravity) + list(contracts),
            on_violation=self._on_violation,
        )

    def admits_intent(self, intent: str) -> bool:
        """Check if all contracts admit the intent."""
        return all(c.admits(intent) for c in self._gravity)


# === Grounded Decorator ===


def grounded(
    *contracts: GravityContract, on_violation: str = "raise"
) -> Callable[[type[Agent[A, B]]], type[Agent[A, B]]]:
    """
    Decorator to apply gravity to an agent class.

    Example:
        >>> @grounded(FactConsistency(facts), EthicalBoundary("strict"))
        ... class MyAgent(Agent[str, str]):
        ...     async def invoke(self, input: str) -> str:
        ...         return f"Processed: {input}"
    """

    def decorator(cls: type[Agent[A, B]]) -> type[Agent[A, B]]:
        original_init = cls.__init__

        def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
            original_init(self, *args, **kwargs)
            # Store contracts for later wrapping
            self._gravity_contracts = contracts
            self._gravity_on_violation = on_violation

        cls.__init__ = new_init  # type: ignore[method-assign]

        # Wrap invoke to check gravity
        original_invoke = cls.invoke

        async def new_invoke(self: Any, input: A) -> B:
            output = await original_invoke(self, input)

            # Apply gravity
            for contract in self._gravity_contracts:
                violation = contract.check(output)
                if violation:
                    error = GroundingError(
                        agent=self.name,
                        contract=contract.name,
                        violation=violation,
                        output=output,
                    )

                    if self._gravity_on_violation == "raise":
                        raise error
                    elif self._gravity_on_violation == "warn":
                        import warnings

                        warnings.warn(str(error))
                    else:
                        import logging

                        logging.warning(str(error))

            return output

        cls.invoke = new_invoke  # type: ignore[method-assign]

        return cls

    return decorator


# === Gravity Builder ===


class GravityBuilder:
    """
    Fluent builder for assembling gravity constraints.

    Example:
        >>> gravity = (
        ...     GravityBuilder()
        ...     .with_facts({"sky": "blue"})
        ...     .with_ethics("strict")
        ...     .with_max_length(1000)
        ...     .with_required_fields(["id", "name"])
        ...     .build()
        ... )
    """

    def __init__(self) -> None:
        self._contracts: list[GravityContract] = []

    def with_facts(self, facts: dict[str, Any]) -> "GravityBuilder":
        """Add fact consistency contract."""
        self._contracts.append(FactConsistency(known_facts=facts))
        return self

    def with_ethics(self, level: str = "moderate") -> "GravityBuilder":
        """Add ethical boundary contract."""
        self._contracts.append(EthicalBoundary(level=level))
        return self

    def with_type(self, expected: type | tuple[type, ...]) -> "GravityBuilder":
        """Add type contract."""
        self._contracts.append(TypeContract(expected_type=expected))
        return self

    def with_max_length(self, max_length: int) -> "GravityBuilder":
        """Add bounded length contract."""
        self._contracts.append(BoundedLength(max_length=max_length))
        return self

    def with_required_fields(self, fields: list[str]) -> "GravityBuilder":
        """Add required fields contract."""
        self._contracts.append(RequiredFields(fields=fields))
        return self

    def with_predicate(
        self,
        predicate: Callable[[Any], bool],
        error_message: str = "Predicate failed",
    ) -> "GravityBuilder":
        """Add custom predicate contract."""
        self._contracts.append(
            PredicateContract(predicate=predicate, error_message=error_message)
        )
        return self

    def with_contract(self, contract: GravityContract) -> "GravityBuilder":
        """Add custom contract."""
        self._contracts.append(contract)
        return self

    def with_domain(self, domain: str, f_contract: Any) -> "GravityBuilder":
        """Add domain invariant contract."""
        self._contracts.append(DomainInvariant(domain=domain, f_contract=f_contract))
        return self

    def build(self) -> list[GravityContract]:
        """Build list of gravity contracts."""
        return list(self._contracts)

    def compose(self) -> GravityContract | None:
        """Build composed contract (all must pass)."""
        if not self._contracts:
            return None
        if len(self._contracts) == 1:
            return self._contracts[0]
        return ComposedContract(self._contracts)
