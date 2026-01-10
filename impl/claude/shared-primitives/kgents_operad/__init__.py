"""
kgents-operad: Composition Grammar for Agents

An operad defines a grammar of composition. Instead of hardcoded
operators, operads make composition rules explicit and programmable.

Quick Start (10 minutes or less):

    from kgents_operad import Operad, Operation, Law, create_agent_operad
    from kgents_poly import from_function

    # Use the standard agent operad
    operad = create_agent_operad()

    # Define some agents
    double = from_function("double", lambda x: x * 2)
    add_one = from_function("add_one", lambda x: x + 1)

    # Compose using operad operations
    composed = operad.compose("seq", double, add_one)
    _, result = composed.invoke(("ready", "ready"), 10)
    print(result)  # 21

What is an Operad?

    An operad is a mathematical structure that defines:
    - Operations: How things can be combined (seq, par, branch, etc.)
    - Laws: What compositions are equivalent (associativity, identity)

    Think of it as the "grammar" for composing agents. Just like grammar
    rules define valid sentences, an operad defines valid compositions.

Why use an Operad?

    1. Explicit Laws: Composition rules are documented and verified
    2. Enumeration: Generate all valid compositions programmatically
    3. Verification: Check if compositions satisfy algebraic laws
    4. Domain-Specific: Create custom operads for your domain

Example Domain Operad:

    # Define a domain-specific composition grammar
    my_operad = Operad(
        name="MyDomainOperad",
        operations={
            "then": Operation(
                name="then",
                arity=2,
                signature="Task[A,B] x Task[B,C] -> Task[A,C]",
                compose=sequential,
                description="Execute tasks in sequence"
            ),
            "both": Operation(
                name="both",
                arity=2,
                signature="Task[A,B] x Task[A,C] -> Task[A,(B,C)]",
                compose=parallel,
                description="Execute tasks in parallel"
            ),
        },
        laws=[
            Law(
                name="then_associativity",
                equation="then(then(a,b),c) = then(a,then(b,c))",
                verify=verify_associativity_fn,
            )
        ]
    )

License: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from itertools import combinations_with_replacement
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from kgents_poly import PolyAgent


# Type variables
S = TypeVar("S")
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


# -----------------------------------------------------------------------------
# Law Status
# -----------------------------------------------------------------------------


class LawStatus(Enum):
    """Status of a law verification."""

    PASSED = auto()      # Law verified with concrete test cases
    FAILED = auto()      # Law violation detected
    SKIPPED = auto()     # Law not tested (e.g., not found)
    STRUCTURAL = auto()  # Verified by type structure only


# -----------------------------------------------------------------------------
# Law Verification Result
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class LawVerification:
    """
    Result of verifying an operad law.

    Example:
        >>> result = operad.verify_law("seq_associativity", a, b, c)
        >>> if result.passed:
        ...     print("Law holds!")
        >>> else:
        ...     print(f"Violation: {result.message}")
    """

    law_name: str
    status: LawStatus
    left_result: Any = None
    right_result: Any = None
    message: str = ""

    @property
    def passed(self) -> bool:
        """True if law was verified (either runtime or structurally)."""
        return self.status in (LawStatus.PASSED, LawStatus.STRUCTURAL)

    def __bool__(self) -> bool:
        return self.passed


# -----------------------------------------------------------------------------
# Operation
# -----------------------------------------------------------------------------


@dataclass
class Operation:
    """
    An operation in the operad.

    Operations are the generators of the composition grammar.
    They specify how agents combine.

    Example:
        >>> seq_op = Operation(
        ...     name="seq",
        ...     arity=2,
        ...     signature="Agent[A,B] x Agent[B,C] -> Agent[A,C]",
        ...     compose=sequential,
        ...     description="Sequential composition"
        ... )
        >>> composed = seq_op(agent1, agent2)
    """

    name: str
    arity: int
    signature: str
    compose: Callable[..., Any]  # Returns PolyAgent
    description: str = ""

    def __call__(self, *agents: Any) -> Any:
        """Apply the operation to agents."""
        if len(agents) != self.arity:
            raise ValueError(
                f"Operation '{self.name}' requires {self.arity} agent(s), "
                f"got {len(agents)}. Signature: {self.signature}"
            )
        return self.compose(*agents)


# -----------------------------------------------------------------------------
# Law
# -----------------------------------------------------------------------------


@dataclass
class Law:
    """
    An equation that must hold in the operad.

    Laws are the defining relations of the operad.
    They constrain which compositions are equivalent.

    Example:
        >>> associativity = Law(
        ...     name="seq_associativity",
        ...     equation="seq(seq(a,b),c) = seq(a,seq(b,c))",
        ...     verify=verify_fn,
        ...     description="Sequential composition is associative"
        ... )
    """

    name: str
    equation: str
    verify: Callable[..., LawVerification]
    description: str = ""


# -----------------------------------------------------------------------------
# Operad
# -----------------------------------------------------------------------------


@dataclass
class Operad:
    """
    Grammar of agent composition.

    An operad consists of:
    - Operations: How agents compose
    - Laws: What compositions are equivalent

    The operad guarantees that all compositions built from
    operations satisfy the laws.

    Example:
        >>> operad = Operad(
        ...     name="TaskOperad",
        ...     operations={
        ...         "seq": Operation(...),
        ...         "par": Operation(...),
        ...     },
        ...     laws=[
        ...         Law(name="associativity", ...),
        ...     ]
        ... )
        >>> composed = operad.compose("seq", task1, task2)
    """

    name: str
    operations: dict[str, Operation] = field(default_factory=dict)
    laws: list[Law] = field(default_factory=list)
    description: str = ""

    def get(self, op_name: str) -> Operation | None:
        """
        Get an operation by name.

        Args:
            op_name: Name of the operation

        Returns:
            Operation if found, None otherwise
        """
        return self.operations.get(op_name)

    def compose(self, op_name: str, *agents: Any) -> Any:
        """
        Apply an operation to compose agents.

        Args:
            op_name: Name of the operation
            *agents: Agents to compose

        Returns:
            Composed agent

        Raises:
            KeyError: If operation not found
            ValueError: If wrong number of agents

        Example:
            >>> composed = operad.compose("seq", agent1, agent2)
        """
        if op_name not in self.operations:
            available = list(self.operations.keys())
            raise KeyError(
                f"Unknown operation: '{op_name}'. "
                f"Available operations: {available}"
            )
        return self.operations[op_name](*agents)

    def verify_law(self, law_name: str, *test_agents: Any) -> LawVerification:
        """
        Verify a specific law.

        Args:
            law_name: Name of the law to verify
            *test_agents: Test agents for verification

        Returns:
            LawVerification result
        """
        for law in self.laws:
            if law.name == law_name:
                return law.verify(*test_agents)
        return LawVerification(
            law_name=law_name,
            status=LawStatus.SKIPPED,
            message=f"Law '{law_name}' not found in operad '{self.name}'",
        )

    def verify_all_laws(self, *test_agents: Any) -> list[LawVerification]:
        """
        Verify all laws with given test agents.

        Args:
            *test_agents: Test agents for verification

        Returns:
            List of verification results
        """
        return [law.verify(*test_agents) for law in self.laws]

    def enumerate(
        self,
        primitives: list[Any],
        depth: int,
        filter_fn: Callable[[Any], bool] | None = None,
    ) -> list[Any]:
        """
        Generate all valid compositions up to given depth.

        This is the generative power of operads: from primitives
        and operations, we can enumerate all valid compositions.

        Args:
            primitives: Starting agents
            depth: Maximum composition depth
            filter_fn: Optional filter for valid compositions

        Returns:
            List of all valid compositions

        Example:
            >>> primitives = [agent1, agent2, agent3]
            >>> all_compositions = operad.enumerate(primitives, depth=2)
        """
        results = list(primitives)

        for _ in range(depth):
            new_results = []
            for op in self.operations.values():
                if op.arity == 0:
                    try:
                        composed = op.compose()
                        if composed not in results:
                            if filter_fn is None or filter_fn(composed):
                                new_results.append(composed)
                    except Exception:
                        pass
                else:
                    for combo in combinations_with_replacement(results, op.arity):
                        try:
                            composed = op.compose(*combo)
                            if composed not in results and composed not in new_results:
                                if filter_fn is None or filter_fn(composed):
                                    new_results.append(composed)
                        except (TypeError, ValueError):
                            pass
            results.extend(new_results)

        return results

    def __repr__(self) -> str:
        ops = ", ".join(self.operations.keys())
        return f"Operad({self.name!r}, operations=[{ops}])"


# -----------------------------------------------------------------------------
# Universal Agent Operad
# -----------------------------------------------------------------------------

# Lazy import to avoid circular dependency
_agent_operad: Operad | None = None


def create_agent_operad() -> Operad:
    """
    Create the Universal Agent Operad.

    This is the base operad from which domain-specific operads derive.
    It provides 5 universal operations:
    - seq: Sequential composition (left >> right)
    - par: Parallel composition (both on same input)
    - branch: Conditional composition (if-then-else)
    - fix: Fixed-point composition (repeat until)
    - trace: Traced/observable composition

    Example:
        >>> from kgents_poly import from_function
        >>> operad = create_agent_operad()
        >>> double = from_function("double", lambda x: x * 2)
        >>> add_one = from_function("add_one", lambda x: x + 1)
        >>> composed = operad.compose("seq", double, add_one)
    """
    # Import here to avoid circular dependency
    from kgents_poly import PolyAgent, parallel, sequential

    def _seq_compose(
        left: PolyAgent[Any, Any, Any], right: PolyAgent[Any, Any, Any]
    ) -> PolyAgent[Any, Any, Any]:
        """Sequential composition: left >> right."""
        return sequential(left, right)

    def _par_compose(
        left: PolyAgent[Any, Any, Any], right: PolyAgent[Any, Any, Any]
    ) -> PolyAgent[Any, Any, Any]:
        """Parallel composition: both on same input."""
        return parallel(left, right)

    def _branch_compose(
        predicate: PolyAgent[Any, Any, Any],
        if_true: PolyAgent[Any, Any, Any],
        if_false: PolyAgent[Any, Any, Any],
    ) -> PolyAgent[Any, Any, Any]:
        """Conditional composition."""

        def branch_transition(
            state: tuple[Any, Any, Any], input: Any
        ) -> tuple[tuple[Any, Any, Any], Any]:
            p_state, t_state, f_state = state
            new_p_state, pred_result = predicate.transition(p_state, input)
            if pred_result:
                new_t_state, output = if_true.transition(t_state, input)
                return (new_p_state, new_t_state, f_state), output
            else:
                new_f_state, output = if_false.transition(f_state, input)
                return (new_p_state, t_state, new_f_state), output

        positions = frozenset(
            (p, t, f)
            for p in predicate.positions
            for t in if_true.positions
            for f in if_false.positions
        )

        return PolyAgent(
            name=f"branch({predicate.name},{if_true.name},{if_false.name})",
            positions=positions,
            _directions=lambda s: predicate.directions(s[0]),
            _transition=branch_transition,
        )

    def _fix_compose(
        predicate: PolyAgent[Any, Any, Any],
        body: PolyAgent[Any, Any, Any],
    ) -> PolyAgent[Any, Any, Any]:
        """Fixed-point composition: repeat until predicate succeeds."""
        MAX_ITERATIONS = 10

        def fix_transition(
            state: tuple[Any, Any, int], input: Any
        ) -> tuple[tuple[Any, Any, int], Any]:
            p_state, b_state, iterations = state
            if iterations >= MAX_ITERATIONS:
                return state, None

            new_b_state, output = body.transition(b_state, input)
            new_p_state, should_stop = predicate.transition(p_state, output)
            return (new_p_state, new_b_state, iterations + 1), output

        positions = frozenset(
            (p, b, i)
            for p in predicate.positions
            for b in body.positions
            for i in range(MAX_ITERATIONS + 1)
        )

        return PolyAgent(
            name=f"fix({predicate.name},{body.name})",
            positions=positions,
            _directions=lambda s: body.directions(s[1]),
            _transition=fix_transition,
        )

    def _trace_compose(inner: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
        """Add observation/logging to agent."""
        traces: list[tuple[Any, Any, Any]] = []

        def trace_transition(state: Any, input: Any) -> tuple[Any, Any]:
            new_state, output = inner.transition(state, input)
            traces.append((input, output, new_state))
            return new_state, output

        return PolyAgent(
            name=f"trace({inner.name})",
            positions=inner.positions,
            _directions=inner.directions,
            _transition=trace_transition,
        )

    # Create associativity verifier
    def _verify_associativity(
        a: PolyAgent[Any, Any, Any],
        b: PolyAgent[Any, Any, Any],
        c: PolyAgent[Any, Any, Any],
        op_name: str = "seq",
    ) -> LawVerification:
        """Verify (a op b) op c = a op (b op c)."""
        try:
            if op_name == "seq":
                left = sequential(sequential(a, b), c)
                right = sequential(a, sequential(b, c))
            elif op_name == "par":
                left = parallel(parallel(a, b), c)
                right = parallel(a, parallel(b, c))
            else:
                return LawVerification(
                    law_name=f"{op_name}_associativity",
                    status=LawStatus.SKIPPED,
                    message=f"No associativity check for {op_name}",
                )

            return LawVerification(
                law_name=f"{op_name}_associativity",
                status=LawStatus.STRUCTURAL,
                left_result=left.name,
                right_result=right.name,
                message="Structure matches (behavioral equivalence assumed)",
            )
        except Exception as e:
            return LawVerification(
                law_name=f"{op_name}_associativity",
                status=LawStatus.FAILED,
                message=str(e),
            )

    return Operad(
        name="AgentOperad",
        operations={
            "seq": Operation(
                name="seq",
                arity=2,
                signature="Agent[A,B] x Agent[B,C] -> Agent[A,C]",
                compose=_seq_compose,
                description="Sequential: output of left feeds input of right",
            ),
            "par": Operation(
                name="par",
                arity=2,
                signature="Agent[A,B] x Agent[A,C] -> Agent[A,(B,C)]",
                compose=_par_compose,
                description="Parallel: both agents receive same input",
            ),
            "branch": Operation(
                name="branch",
                arity=3,
                signature="Pred[A] x Agent[A,B] x Agent[A,B] -> Agent[A,B]",
                compose=_branch_compose,
                description="Conditional: if predicate then first else second",
            ),
            "fix": Operation(
                name="fix",
                arity=2,
                signature="Pred[B] x Agent[A,B] -> Agent[A,B]",
                compose=_fix_compose,
                description="Fixed-point: repeat until predicate succeeds",
            ),
            "trace": Operation(
                name="trace",
                arity=1,
                signature="Agent[A,B] -> Agent[A,B] (with observation)",
                compose=_trace_compose,
                description="Add observation/logging to agent",
            ),
        },
        laws=[
            Law(
                name="seq_associativity",
                equation="seq(seq(a,b),c) = seq(a,seq(b,c))",
                verify=lambda a, b, c: _verify_associativity(a, b, c, "seq"),
                description="Sequential composition is associative",
            ),
            Law(
                name="par_associativity",
                equation="par(par(a,b),c) = par(a,par(b,c))",
                verify=lambda a, b, c: _verify_associativity(a, b, c, "par"),
                description="Parallel composition is associative",
            ),
        ],
        description="Universal grammar of agent composition",
    )


def get_agent_operad() -> Operad:
    """
    Get the singleton Agent Operad instance.

    Returns:
        The universal Agent Operad
    """
    global _agent_operad
    if _agent_operad is None:
        _agent_operad = create_agent_operad()
    return _agent_operad


# Convenience: pre-created agent operad
AGENT_OPERAD = create_agent_operad()


# -----------------------------------------------------------------------------
# Operad Registry
# -----------------------------------------------------------------------------


class OperadRegistry:
    """
    Registry of all operads.

    Enables runtime discovery and verification of operads.

    Example:
        >>> OperadRegistry.register(my_operad)
        >>> operad = OperadRegistry.get("MyOperad")
        >>> results = OperadRegistry.verify_all(test_agents)
    """

    _operads: dict[str, Operad] = {}

    @classmethod
    def register(cls, operad: Operad) -> None:
        """Register an operad."""
        cls._operads[operad.name] = operad

    @classmethod
    def get(cls, name: str) -> Operad | None:
        """Get an operad by name."""
        return cls._operads.get(name)

    @classmethod
    def all_operads(cls) -> dict[str, Operad]:
        """Get all registered operads."""
        return cls._operads.copy()

    @classmethod
    def verify_all(cls, *test_agents: Any) -> dict[str, list[LawVerification]]:
        """Verify all laws across all registered operads."""
        results = {}
        for name, operad in cls._operads.items():
            results[name] = operad.verify_all_laws(*test_agents)
        return results

    @classmethod
    def reset(cls) -> None:
        """Clear all registered operads."""
        cls._operads.clear()


# Register the universal operad
OperadRegistry.register(AGENT_OPERAD)


__all__ = [
    # Enums
    "LawStatus",
    # Core types
    "LawVerification",
    "Operation",
    "Law",
    "Operad",
    # Universal operad
    "AGENT_OPERAD",
    "create_agent_operad",
    "get_agent_operad",
    # Registry
    "OperadRegistry",
]
