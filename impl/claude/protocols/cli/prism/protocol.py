"""
CLICapable Protocol - Structural typing for CLI-exposable agents.

Agents that wish to expose CLI commands implement this protocol.
This is structural typing - agents don't inherit from CLICapable,
they simply implement the required properties and methods.

See: spec/protocols/prism.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Protocol, runtime_checkable

if TYPE_CHECKING:
    from typing import Any


@runtime_checkable
class CLICapable(Protocol):
    """
    Protocol for agents that project a CLI surface.

    This uses structural typing via @runtime_checkable, enabling
    isinstance() checks without requiring inheritance.

    Example:
        class GrammarianCLI:
            @property
            def genus_name(self) -> str:
                return "grammar"

            @property
            def cli_description(self) -> str:
                return "G-gent Grammar/DSL operations"

            def get_exposed_commands(self) -> dict[str, Callable]:
                return {"reify": self.reify, "parse": self.parse}

        # Duck typing check
        assert isinstance(GrammarianCLI(), CLICapable)
    """

    @property
    def genus_name(self) -> str:
        """
        Single-word genus identifier for CLI namespace.

        This becomes the subcommand name: `kgents <genus_name> ...`

        Examples: "grammar", "witness", "library", "jit", "parse", "garden"
        """
        ...

    @property
    def cli_description(self) -> str:
        """
        One-line description for help text.

        Shown in `kgents --help` and `kgents <genus> --help`.
        """
        ...

    def get_exposed_commands(self) -> dict[str, Callable[..., Any]]:
        """
        Return mapping of command names to methods.

        Only methods decorated with @expose should be included.
        The Prism uses this to build subcommand parsers.

        Returns:
            Dict mapping command names (str) to method callables.
            Methods should be decorated with @expose for full functionality.
        """
        ...
