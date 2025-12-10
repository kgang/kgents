# The Prism Protocol

**Status:** Specification v1.0
**Theme:** From Switchboard to Mycelium
**Philosophy:** Commands emerge from capabilities; the CLI is a projection, not a definition.

---

## Core Insight

Traditional CLI architecture is a **Switchboard**: explicit wiring connects command names to handler functions. Adding a capability requires editing multiple files.

The Prism inverts this relationship:

```
┌─────────────────────────────────────────────────────────────┐
│                    THE PRISM INVERSION                       │
│                                                              │
│   Switchboard:  CLI ──defines──▶ Agent Commands             │
│                                                              │
│   Prism:        Agent ──exposes──▶ CLI (auto-generated)     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

> **The Isomorphism Principle:** The structure of the CLI is homomorphic to the structure of the Agent. If the Agent changes, the CLI changes instantly.

---

## The CLICapable Protocol

Agents that wish to expose CLI commands implement this protocol:

```python
@runtime_checkable
class CLICapable(Protocol):
    """
    Protocol for agents that project a CLI surface.

    This is structural typing - agents don't inherit from CLICapable,
    they simply implement the required properties and methods.
    """

    @property
    def genus_name(self) -> str:
        """
        Single-word genus identifier for CLI namespace.
        Examples: "grammar", "witness", "library", "jit", "parse", "garden"
        """
        ...

    @property
    def cli_description(self) -> str:
        """One-line description for help text."""
        ...

    def get_exposed_commands(self) -> dict[str, Callable]:
        """
        Return mapping of command names to methods.
        Only methods decorated with @expose should be included.
        """
        ...
```

**Key Properties:**
- `@runtime_checkable` enables `isinstance(agent, CLICapable)` checks
- No inheritance required - structural typing
- Agents can add CLI capability without changing core class hierarchy

---

## The @expose Decorator

Instead of writing argument parsers, methods are annotated:

```python
@expose(
    help="Reify domain into Tongue artifact",
    examples=[
        'kgents grammar reify "Calendar Management"',
        'kgents grammar reify "File Ops" --constraints="No deletes"',
    ],
)
async def reify(
    self,
    domain: str,
    level: GrammarLevel = GrammarLevel.COMMAND,
    constraints: list[str] | None = None,
    name: str | None = None,
) -> Tongue:
    """
    Transform a domain description into a formal Tongue.

    The domain string describes the conceptual space. Level controls
    grammar complexity. Constraints are semantic boundaries.
    """
    ...
```

### ExposeMetadata

```python
@dataclass
class ExposeMetadata:
    """Metadata attached to @expose decorated methods."""
    help: str                              # Short description (required)
    examples: list[str] = field(default_factory=list)  # Usage examples
    aliases: list[str] = field(default_factory=list)   # Alternative names
    hidden: bool = False                   # Exclude from help listings
```

### Introspection Functions

```python
def is_exposed(fn: Any) -> bool:
    """Check if function has @expose decorator."""
    return hasattr(fn, '_expose_meta')

def get_expose_meta(fn: Any) -> ExposeMetadata | None:
    """Retrieve ExposeMetadata from decorated function."""
    return getattr(fn, '_expose_meta', None)
```

---

## The Prism Class

The Prism auto-constructs CLI from agent introspection:

```python
class Prism:
    """
    Auto-construct argparse from CLICapable agents.

    The Prism reflects an agent's exposed methods into a CLI parser,
    using type hints to generate argument specifications.
    """

    def __init__(self, agent: CLICapable):
        self.agent = agent
        self._parser: argparse.ArgumentParser | None = None

    def build_parser(self) -> argparse.ArgumentParser:
        """
        Generate argparse.ArgumentParser from agent introspection.

        For each exposed command:
        1. Create subparser with help from @expose
        2. Analyze method signature for parameters
        3. Map type hints to argparse argument types
        4. Handle defaults, optionality, and collections
        """
        ...

    async def dispatch(self, args: list[str]) -> int:
        """
        Parse arguments and invoke appropriate method.

        Automatically handles:
        - Sync vs async method detection
        - Result serialization (JSON or rich output)
        - Error handling with sympathetic messages

        Returns exit code (0 for success).
        """
        ...

    def dispatch_sync(self, args: list[str]) -> int:
        """Synchronous wrapper for CLI entry points."""
        import asyncio
        return asyncio.run(self.dispatch(args))
```

---

## Type-to-Argparse Mapping

Python type hints map to argparse configurations:

| Python Type | Argparse Config | Notes |
|-------------|-----------------|-------|
| `str` | `type=str` | Default for untyped |
| `int` | `type=int` | |
| `float` | `type=float` | |
| `bool` | `action='store_true'` | Flag without value |
| `Path` | `type=Path` | From pathlib |
| `Enum` | `choices=[...]` | Enum values as choices |
| `list[T]` | `nargs='*', type=T` | Multiple values |
| `T \| None` | `required=False` | Optional argument |
| `T = default` | `default=default` | Has default value |

### Extensibility

Custom types can be registered:

```python
class TypeRegistry:
    """Extensible type → argparse mapping."""

    @classmethod
    def register(cls, python_type: type, mapper: Callable[[type], dict]) -> None:
        """Register custom type mapping."""
        ...

    @classmethod
    def map(cls, python_type: type) -> dict:
        """Get argparse kwargs for type."""
        ...

# Example: Register custom Enum handling
TypeRegistry.register(GrammarLevel, lambda t: {
    "choices": [e.value for e in t],
    "type": str,
})
```

---

## Laws

### Law 1: Emergence

CLI commands emerge from decorated methods. No explicit command registration required.

```python
# Adding a command is just adding an @expose method
@expose(help="New capability")
async def new_command(self, arg: str) -> Result:
    ...
# CLI automatically gains `kgents genus new_command <arg>`
```

### Law 2: Fidelity

Type hints are truth; the CLI is a projection. If the method signature changes, the CLI changes.

```python
# Changing a type changes the CLI
async def cmd(self, count: int) -> None:  # Accepts integer
async def cmd(self, count: str) -> None:  # Now accepts string
```

### Law 3: Graceful Degradation

Agents work without CLI exposure. CLICapable is an optional capability layer.

```python
# Agent works without implementing CLICapable
agent = Grammarian()
result = await agent.reify("domain")  # Direct invocation

# CLI is an additional projection
cli = GrammarianCLI()  # Implements CLICapable
prism = Prism(cli)
prism.dispatch_sync(["reify", "domain"])
```

### Law 4: Zero Overhead

If an agent doesn't implement CLICapable, there is no performance cost. The Prism infrastructure is lazy-loaded.

---

## Integration with Hollow Shell

The Prism integrates with the existing Hollow Shell pattern:

```python
# protocols/cli/genus/g_gent.py - Thin wrapper
def cmd_grammar(args: list[str]) -> int:
    """G-gent CLI handler - delegates to Prism."""
    from protocols.cli.prism import Prism
    from agents.g.cli import GrammarianCLI

    return Prism(GrammarianCLI()).dispatch_sync(args)
```

**Key Properties:**
- `COMMAND_REGISTRY` in hollow.py unchanged
- Lazy loading preserved (imports only when command invoked)
- Startup time unaffected (<50ms target maintained)

---

## Example: Complete Agent CLI

```python
# agents/g/cli.py
from __future__ import annotations
from typing import TYPE_CHECKING

from protocols.cli.prism import CLICapable, expose

if TYPE_CHECKING:
    from agents.g import Tongue, GrammarLevel

class GrammarianCLI(CLICapable):
    """CLI interface for G-gent (Grammarian)."""

    def __init__(self):
        from agents.g import Grammarian
        self._grammarian = Grammarian()

    @property
    def genus_name(self) -> str:
        return "grammar"

    @property
    def cli_description(self) -> str:
        return "G-gent Grammar/DSL operations"

    def get_exposed_commands(self) -> dict[str, Callable]:
        return {
            "reify": self.reify,
            "parse": self.parse,
            "list": self.list_tongues,
            "show": self.show,
            "validate": self.validate,
        }

    @expose(
        help="Reify domain into Tongue artifact",
        examples=['kgents grammar reify "Calendar"'],
    )
    async def reify(
        self,
        domain: str,
        level: str = "command",
        constraints: str | None = None,
        name: str | None = None,
        format: str = "rich",
    ) -> dict:
        """Reify a domain into a Tongue artifact."""
        from agents.g import GrammarLevel

        level_enum = GrammarLevel[level.upper()]
        constraint_list = constraints.split(",") if constraints else []

        tongue = await self._grammarian.reify(
            domain=domain,
            level=level_enum,
            constraints=constraint_list,
            name=name,
        )

        return {
            "name": tongue.name,
            "domain": tongue.domain,
            "level": tongue.level.value,
            "grammar": tongue.grammar,
        }
```

---

## Anti-Patterns

### What The Prism Eliminates

1. **Manual Subcommand Dispatch**
   ```python
   # BEFORE (anti-pattern)
   handlers = {"reify": _cmd_reify, "parse": _cmd_parse}
   if subcommand not in handlers:
       print(f"Unknown: {subcommand}")
   return handlers[subcommand](args)
   ```

2. **Duplicated Help Text**
   ```python
   # BEFORE (anti-pattern)
   HELP_TEXT = """\
   kgents grammar - G-gent Grammar/DSL operations

   USAGE:
     kgents grammar <subcommand> [args...]
   ...
   """  # 50+ lines per command
   ```

3. **Manual Argument Parsing**
   ```python
   # BEFORE (anti-pattern)
   for arg in args:
       if arg.startswith("--level="):
           level = arg.split("=", 1)[1]
       elif arg.startswith("--constraints="):
           constraints = [c.strip() for c in arg.split("=", 1)[1].split(",")]
   ```

4. **Separate CLI Files**
   ```
   # BEFORE (anti-pattern)
   protocols/cli/genus/g_gent.py   # 766 lines
   protocols/cli/genus/w_gent.py   # 648 lines
   protocols/cli/genus/p_gent.py   # 400 lines
   # Total: ~3000 lines of boilerplate
   ```

---

## Design Principles Applied

| Principle | How Prism Embodies It |
|-----------|----------------------|
| **Tasteful** | Single pattern replaces 6 variations; eliminates ~3000 lines |
| **Curated** | @expose is intentional selection of what to project |
| **Ethical** | CLI is transparent projection; no hidden behavior |
| **Joy-Inducing** | `@expose(help="...")` reads naturally; less code to maintain |
| **Composable** | CLICapable is a capability, not inheritance; agents compose freely |
| **Heterarchical** | Agents choose to expose CLI; no forced hierarchy |
| **Generative** | Type hints generate CLI; spec → impl compression >60% |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Lines of boilerplate eliminated | >2500 |
| Prism infrastructure lines | <500 |
| Startup time regression | 0ms |
| Commands with @expose | 100% of genus commands |
| Type coverage | All argparse types mapped |

---

## See Also

- `spec/protocols/cli.md` - Parent CLI specification
- `spec/principles.md` - Design principles
- `impl/claude/protocols/cli/prism/` - Reference implementation
