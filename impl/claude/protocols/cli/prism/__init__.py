"""
The Prism: Auto-constructive CLI Architecture.

The Prism transforms CLI construction from manual dispatch ("Switchboard")
to reflection-based emergence. Agents expose their capabilities via the
@expose decorator, and the Prism auto-generates argparse from type hints.

Usage:
    from protocols.cli.prism import CLICapable, expose, Prism

    class MyAgentCLI(CLICapable):
        @property
        def genus_name(self) -> str:
            return "myagent"

        @property
        def cli_description(self) -> str:
            return "My agent operations"

        def get_exposed_commands(self) -> dict[str, Callable]:
            return {"cmd": self.cmd}

        @expose(help="Do something")
        async def cmd(self, arg: str) -> dict:
            ...

    # In CLI handler:
    prism = Prism(MyAgentCLI())
    exit_code = prism.dispatch_sync(args)

See: spec/protocols/prism.md
"""

from __future__ import annotations

from .decorator import ExposeMetadata, expose, get_expose_meta, is_exposed
from .prism import Prism
from .protocol import CLICapable
from .type_mapping import TypeRegistry

__all__ = [
    # Protocol
    "CLICapable",
    # Decorator
    "expose",
    "is_exposed",
    "get_expose_meta",
    "ExposeMetadata",
    # Core
    "Prism",
    # Type mapping
    "TypeRegistry",
]
