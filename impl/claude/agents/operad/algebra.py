"""
CLI Algebra: Operad → CLI Commands.

The CLIAlgebra functor transforms operad operations into CLI handlers.
This enables automatic CLI generation from operads.

Key insight:
    CLI commands are O-algebras - specific instantiations of the
    operad grammar in the CLI domain.

    F: Operad → CLI
    F(operation) = CLI handler
    F(law) = test that verifies the law

See: plans/ideas/impl/meta-construction.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Protocol

from .core import Operad, Operation

if TYPE_CHECKING:
    from agents.poly import PolyAgent


class CLIHandler(Protocol):
    """Protocol for CLI handlers."""

    async def __call__(self, args: list[str]) -> int:
        """Execute the CLI command."""
        ...


@dataclass
class CLICommand:
    """A CLI command generated from an operad operation."""

    name: str
    operation: Operation
    handler: Callable[[list[str]], int]
    help_text: str

    def __call__(self, args: list[str]) -> int:
        return self.handler(args)


class CLIAlgebra:
    """
    Functor: Operad → CLI Commands.

    Transforms operad operations into CLI handlers.
    Each operation becomes a command that:
    1. Parses agent names from args
    2. Resolves agents from registry
    3. Applies operad composition
    4. Executes and displays result
    """

    def __init__(
        self,
        operad: Operad,
        agent_resolver: Callable[[str], PolyAgent[Any, Any, Any] | None] | None = None,
        prefix: str = "kg",
    ):
        """
        Initialize CLI algebra.

        Args:
            operad: The operad to transform
            agent_resolver: Function to resolve agent names to agents
            prefix: CLI command prefix (default: "kg")
        """
        self.operad = operad
        self.agent_resolver = agent_resolver or self._default_resolver
        self.prefix = prefix
        self._commands: dict[str, CLICommand] = {}

    def _default_resolver(self, name: str) -> PolyAgent[Any, Any, Any] | None:
        """Default agent resolver using poly primitives."""
        from agents.poly import get_primitive

        return get_primitive(name)

    def to_cli(self, op_name: str) -> CLICommand:
        """
        Convert an operad operation to a CLI command.

        Args:
            op_name: Name of the operation

        Returns:
            CLICommand that wraps the operation
        """
        if op_name not in self.operad.operations:
            raise KeyError(f"Unknown operation: {op_name}")

        op = self.operad.operations[op_name]

        def handler(args: list[str]) -> int:
            """CLI handler for this operation."""
            # Parse agent names from args
            agent_names = [a for a in args if not a.startswith("-")]

            if len(agent_names) != op.arity:
                print(f"Error: {op.name} requires {op.arity} agent(s), got {len(agent_names)}")
                return 1

            # Resolve agents
            agents = []
            for name in agent_names:
                agent = self.agent_resolver(name)
                if agent is None:
                    print(f"Error: Unknown agent '{name}'")
                    return 1
                agents.append(agent)

            try:
                # Compose using operad
                composed = self.operad.compose(op_name, *agents)
                print(f"Composed: {composed.name}")
                print(f"  Positions: {len(composed.positions)}")
                print(f"  Signature: {op.signature}")
                return 0
            except Exception as e:
                print(f"Error composing agents: {e}")
                return 1

        # Generate command name
        operad_prefix = self.operad.name.lower().replace("operad", "")
        cmd_name = f"{self.prefix} {operad_prefix} {op_name}"

        return CLICommand(
            name=cmd_name,
            operation=op,
            handler=handler,
            help_text=f"{op.description}\n\nSignature: {op.signature}",
        )

    def generate_all(self) -> dict[str, CLICommand]:
        """
        Generate CLI commands for all operations.

        Returns:
            Dict mapping command names to CLICommands
        """
        for op_name in self.operad.operations:
            cmd = self.to_cli(op_name)
            self._commands[cmd.name] = cmd
        return self._commands

    def register_all(
        self,
        registry: dict[str, Callable[[list[str]], int]],
    ) -> None:
        """
        Register all commands with a CLI registry.

        Args:
            registry: Dict to register handlers in
        """
        commands = self.generate_all()
        for name, cmd in commands.items():
            registry[name] = cmd.handler

    def help(self) -> str:
        """Generate help text for all commands."""
        lines = [
            f"# {self.operad.name} CLI Commands",
            "",
            f"{self.operad.description}",
            "",
            "## Operations",
            "",
        ]

        for op_name, op in self.operad.operations.items():
            operad_prefix = self.operad.name.lower().replace("operad", "")
            cmd = f"{self.prefix} {operad_prefix} {op_name}"
            lines.append(f"### `{cmd}`")
            lines.append("")
            lines.append(f"**Signature:** `{op.signature}`")
            lines.append("")
            lines.append(op.description)
            lines.append("")

        lines.append("## Laws")
        lines.append("")
        for law in self.operad.laws:
            lines.append(f"- `{law.equation}` ({law.name})")

        return "\n".join(lines)


class TestAlgebra:
    """
    Functor: Operad Laws → Test Cases.

    Transforms operad laws into pytest test cases.
    """

    def __init__(self, operad: Operad):
        self.operad = operad

    def generate_law_tests(self) -> str:
        """Generate pytest code for all operad laws."""
        lines = [
            '"""Auto-generated tests for operad laws."""',
            "",
            "import pytest",
            f"from agents.operad import {self.operad.name.upper()}",
            "from agents.poly import identity, from_function",
            "",
            "",
        ]

        for law in self.operad.laws:
            # Generate test function
            test_name = f"test_{law.name}"
            lines.append(f"def {test_name}():")
            lines.append(f'    """Verify: {law.equation}"""')
            lines.append("    # Create test agents")
            lines.append("    a = from_function('A', lambda x: x + 1)")
            lines.append("    b = from_function('B', lambda x: x * 2)")
            lines.append("    c = from_function('C', lambda x: x - 1)")
            lines.append("")
            lines.append(f"    result = {self.operad.name.upper()}.verify_law(")
            lines.append(f'        "{law.name}", a, b, c')
            lines.append("    )")
            lines.append("    assert result.passed, result.message")
            lines.append("")
            lines.append("")

        return "\n".join(lines)

    def generate_composition_tests(self, depth: int = 2) -> str:
        """Generate property tests for random compositions."""
        lines = [
            '"""Auto-generated property tests for compositions."""',
            "",
            "import pytest",
            "from hypothesis import given, strategies as st",
            f"from agents.operad import {self.operad.name.upper()}",
            "from agents.poly import all_primitives",
            "",
            "",
            "@given(st.integers(min_value=0, max_value=5))",
            "def test_random_composition_valid(seed: int):",
            '    """Any composition from operad is valid."""',
            "    primitives = all_primitives()",
            f"    compositions = {self.operad.name.upper()}.enumerate(",
            f"        primitives, depth={depth}",
            "    )",
            "    assert len(compositions) >= len(primitives)",
            "",
        ]

        return "\n".join(lines)


__all__ = [
    "CLIAlgebra",
    "CLICommand",
    "CLIHandler",
    "TestAlgebra",
]
