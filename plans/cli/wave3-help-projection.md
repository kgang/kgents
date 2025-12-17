# Wave 3: Help/Affordances Projection

**Status**: Complete
**Priority**: Medium
**Progress**: 100%
**Parent**: `plans/cli-isomorphic-migration.md`
**Depends On**: Waves 0-2 (Dimension System, Crown Jewels, Forest+Joy)
**Last Updated**: 2025-12-17

## Implementation Status

### Completed
- [x] HelpProjector (`protocols/cli/help_projector.py`) - ~350 lines
- [x] HelpRenderer (`protocols/cli/help_renderer.py`) - ~200 lines
- [x] Global Help (`protocols/cli/help_global.py`) - ~200 lines
- [x] Integration with `hollow.py` (global --help, command --help)
- [x] Shell completions generator (`protocols/cli/completions.py`) - ~350 lines (bash/zsh/fish)
- [x] Query help formatter (`protocols/cli/query_help.py`) - ~200 lines
- [x] Handler helper (`protocols/cli/handlers/_help.py`) - ~80 lines
- [x] Crown Jewel handler migration (brain, soul, town, park, atelier, gardener)
- [x] Tests (17 tests in `test_help_projection.py`)

---

## Objective

Implement Help as Affordance Projection from `spec/protocols/cli.md` §9. Instead of maintaining separate help text, all help is derived from aspect metadata. This ensures help is always accurate and complete.

---

## The Core Insight

> *"Help is not documentation bolted on. Help is the affordances aspect of the CLI projected onto human-readable text."*

Traditional help systems require maintaining separate strings:
```python
def print_help():
    """Hand-maintained, often outdated."""
    print("Usage: kg brain capture <content>")
    print("  Stores content to memory")
```

Isomorphic help derives from metadata:
```python
# All this information already exists in @aspect
help_text = project_affordances_to_help(path)
# Auto-generates accurate, complete help
```

---

## Help Projection Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  kg brain --help                                                  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  HelpProjector.project("self.memory")                     │    │
│  │                                                           │    │
│  │  1. Query: ?self.memory.?  (list affordances)             │    │
│  │  2. For each aspect:                                      │    │
│  │     - Extract @aspect metadata                            │    │
│  │     - Format as CLI usage                                 │    │
│  │  3. Add dimension-derived hints                           │    │
│  │  4. Render to terminal                                    │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  🧠 Brain - Holographic Memory (self.memory.*)            │    │
│  │                                                           │    │
│  │  Commands:                                                 │    │
│  │    kg brain capture <content>    Store to holographic mem │    │
│  │    kg brain search <query>       Semantic similarity search│    │
│  │    kg brain surface [context]    Serendipitous retrieval   │    │
│  │    kg brain status               Brain health metrics      │    │
│  │                                                           │    │
│  │  Flags:                                                    │    │
│  │    --json         Output as JSON                          │    │
│  │    --limit N      Limit results (default: 10)             │    │
│  │                                                           │    │
│  │  💰 LLM-backed commands show budget indicator              │    │
│  │                                                           │    │
│  │  See also: kg soul, kg town                               │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: HelpProjector Implementation (Day 1)

### Step 1.1: Create HelpProjector

**File**: `impl/claude/protocols/cli/help_projector.py`

```python
"""
Help Projection Functor

Transforms AGENTESE affordances into CLI help text.

HelpProject : (Path) → HelpText[Terminal]
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.agentese import Logos

@dataclass
class HelpSection:
    """A section of help text."""
    title: str
    content: str
    emoji: str = ""

@dataclass
class CommandHelp:
    """Complete help for a command."""
    path: str
    title: str
    description: str
    usage: list[str]
    flags: list[tuple[str, str]]
    examples: list[str]
    see_also: list[str]
    budget_hint: str | None
    dimension_hints: list[str]

class HelpProjector:
    """Projects AGENTESE affordances to CLI help text."""

    def __init__(self, logos: "Logos"):
        self.logos = logos

    def project(self, path: str) -> CommandHelp:
        """
        Project help for an AGENTESE path.

        If path ends with an aspect (e.g., self.memory.capture),
        shows help for that specific aspect.

        If path is a node (e.g., self.memory), shows help for
        all aspects of that node.
        """
        parts = path.split(".")

        if len(parts) >= 3:
            # Specific aspect help
            return self._aspect_help(path)
        else:
            # Node overview help
            return self._node_help(path)

    def _node_help(self, node_path: str) -> CommandHelp:
        """Generate help for all aspects of a node."""
        # Query affordances
        result = self.logos.query(f"?{node_path}.?")

        # Collect aspect metadata
        aspects = []
        for match in result.matches:
            meta = self.logos.get_aspect_meta(match.path)
            aspects.append((match.path, meta))

        # Build help
        return CommandHelp(
            path=node_path,
            title=self._derive_title(node_path),
            description=self._derive_description(node_path),
            usage=self._build_usage_lines(aspects),
            flags=self._common_flags(),
            examples=self._collect_examples(aspects),
            see_also=self._derive_see_also(node_path),
            budget_hint=self._derive_budget_hint(aspects),
            dimension_hints=self._derive_dimension_hints(aspects),
        )

    def _aspect_help(self, aspect_path: str) -> CommandHelp:
        """Generate help for a specific aspect."""
        meta = self.logos.get_aspect_meta(aspect_path)
        dims = derive_dimensions(aspect_path, meta)

        return CommandHelp(
            path=aspect_path,
            title=f"{aspect_path.split('.')[-1]}",
            description=meta.help or meta.description or "No description",
            usage=[self._aspect_to_usage(aspect_path, meta)],
            flags=self._aspect_flags(meta),
            examples=meta.examples or [],
            see_also=meta.see_also or [],
            budget_hint=meta.budget_estimate,
            dimension_hints=self._format_dimension_hints(dims),
        )

    def _derive_title(self, node_path: str) -> str:
        """Derive display title from path."""
        TITLES = {
            "self.memory": "Brain - Holographic Memory",
            "self.soul": "Soul - Middleware of Consciousness",
            "self.forest": "Forest - Project Health Protocol",
            "world.town": "Town - Agent Simulation",
            "world.atelier": "Atelier - Collaborative Workshops",
            "void.joy": "Joy - Oblique Strategies",
        }
        return TITLES.get(node_path, node_path)

    def _build_usage_lines(self, aspects: list) -> list[str]:
        """Build usage lines from aspects."""
        lines = []
        for path, meta in aspects:
            aspect_name = path.split(".")[-1]
            short_help = (meta.help or "")[:40]
            lines.append(f"kg {self._path_to_command(path):25} {short_help}")
        return lines

    def _path_to_command(self, path: str) -> str:
        """Convert AGENTESE path to CLI command."""
        # self.memory.capture → brain capture
        PATH_TO_CMD = {
            "self.memory": "brain",
            "self.soul": "soul",
            "self.forest": "forest",
            "world.town": "town",
            "world.atelier": "atelier",
            "void.joy": "oblique",
        }

        parts = path.split(".")
        node_path = ".".join(parts[:-1])
        aspect = parts[-1]

        base = PATH_TO_CMD.get(node_path, node_path.replace(".", " "))
        return f"{base} {aspect}"

    def _derive_budget_hint(self, aspects: list) -> str | None:
        """Derive budget hint if any aspect uses LLM."""
        llm_aspects = [
            (p, m) for p, m in aspects
            if any(
                hasattr(e, "effect") and e.effect.name == "CALLS"
                for e in (m.effects or [])
            )
        ]
        if llm_aspects:
            return "💰 Some commands use LLM and incur API costs"
        return None

    def _derive_dimension_hints(self, aspects: list) -> list[str]:
        """Derive UX hints from dimensions."""
        hints = []

        # Check for streaming aspects
        if any(getattr(m, "streaming", False) for _, m in aspects):
            hints.append("🌊 Some commands support streaming output")

        # Check for interactive aspects
        if any(getattr(m, "interactive", False) for _, m in aspects):
            hints.append("💬 Some commands support interactive mode")

        # Check for sensitive operations
        sensitive = [
            (p, m) for p, m in aspects
            if any(
                hasattr(e, "effect") and e.effect.name == "FORCES"
                for e in (m.effects or [])
            )
        ]
        if sensitive:
            hints.append("⚠️ Some commands require confirmation")

        return hints

    def _common_flags(self) -> list[tuple[str, str]]:
        """Standard flags available on all commands."""
        return [
            ("--json", "Output as JSON"),
            ("--help, -h", "Show this help message"),
            ("--trace", "Show trace ID for debugging"),
            ("--dry-run", "Show what would happen without executing"),
        ]

    def _format_dimension_hints(self, dims: "CommandDimensions") -> list[str]:
        """Format dimension-specific hints."""
        hints = []
        if dims.backend == Backend.LLM:
            hints.append("💰 This command uses LLM and incurs API costs")
        if dims.seriousness == Seriousness.SENSITIVE:
            hints.append("⚠️ This is a sensitive operation")
        if dims.interactivity == Interactivity.STREAMING:
            hints.append("🌊 Output streams in real-time")
        return hints
```

### Step 1.2: Help Renderer

**File**: `impl/claude/protocols/cli/help_renderer.py`

```python
"""
Help Renderer

Formats CommandHelp for terminal output.
Supports plain text and Rich formatting.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .help_projector import CommandHelp

def render_help(help: "CommandHelp", use_rich: bool = True) -> str:
    """Render help to terminal output."""
    if use_rich:
        return _render_rich(help)
    return _render_plain(help)

def _render_rich(help: "CommandHelp") -> str:
    """Render with Rich formatting."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from io import StringIO

    console = Console(file=StringIO(), force_terminal=True)

    # Title
    console.print(f"\n[bold cyan]{help.title}[/] ({help.path})\n")

    # Description
    if help.description:
        console.print(f"  {help.description}\n")

    # Usage
    console.print("[bold]Commands:[/]")
    for line in help.usage:
        console.print(f"  {line}")
    console.print()

    # Flags
    console.print("[bold]Flags:[/]")
    for flag, desc in help.flags:
        console.print(f"  [green]{flag:20}[/] {desc}")
    console.print()

    # Examples
    if help.examples:
        console.print("[bold]Examples:[/]")
        for ex in help.examples:
            console.print(f"  [dim]$[/] {ex}")
        console.print()

    # Hints
    if help.dimension_hints:
        for hint in help.dimension_hints:
            console.print(f"  {hint}")
        console.print()

    # Budget
    if help.budget_hint:
        console.print(f"  {help.budget_hint}")
        console.print()

    # See also
    if help.see_also:
        console.print(f"[dim]See also:[/] {', '.join(help.see_also)}")

    return console.file.getvalue()

def _render_plain(help: "CommandHelp") -> str:
    """Render as plain text."""
    lines = [
        f"\n{help.title} ({help.path})",
        "",
        f"  {help.description}",
        "",
        "Commands:",
    ]
    for line in help.usage:
        lines.append(f"  {line}")

    lines.extend(["", "Flags:"])
    for flag, desc in help.flags:
        lines.append(f"  {flag:20} {desc}")

    if help.examples:
        lines.extend(["", "Examples:"])
        for ex in help.examples:
            lines.append(f"  $ {ex}")

    if help.see_also:
        lines.extend(["", f"See also: {', '.join(help.see_also)}"])

    return "\n".join(lines)
```

---

## Phase 2: Integration with Handlers (Day 1)

### Step 2.1: Replace print_help() Functions

Update each handler to use HelpProjector:

**Pattern**:
```python
# Before
def print_help():
    help_text = """
    kg brain ...
    """
    print(help_text.strip())

# After
def print_help():
    from protocols.cli.help_projector import HelpProjector
    from protocols.cli.help_renderer import render_help
    from protocols.agentese import create_logos

    logos = create_logos()
    projector = HelpProjector(logos)
    help = projector.project("self.memory")
    print(render_help(help))
```

### Step 2.2: Global --help Handler

**File**: `impl/claude/protocols/cli/hollow.py`

Add global help handling:

```python
def main(args: list[str]) -> int:
    if "--help" in args or "-h" in args:
        # Check if this is for a specific command
        command_args = [a for a in args if not a.startswith("-")]
        if command_args:
            path = resolve_to_path(command_args)
            return show_help(path)
        else:
            return show_global_help()
    ...
```

### Step 2.3: Global Help Output

**File**: `impl/claude/protocols/cli/help_global.py`

```python
"""
Global Help

Shows overview of all available command families.
"""

def show_global_help() -> int:
    """Display global kgents help."""
    FAMILIES = [
        ("Crown Jewels", [
            ("brain", "self.memory", "Holographic memory operations"),
            ("soul", "self.soul", "Digital consciousness dialogue"),
            ("town", "world.town", "Agent simulation"),
            ("atelier", "world.atelier", "Collaborative workshops"),
        ]),
        ("Forest Protocol", [
            ("forest", "self.forest", "Project health and plans"),
            ("garden", "self.forest.garden", "Hypnagogia and dreams"),
        ]),
        ("Joy Commands", [
            ("oblique", "void.joy.oblique", "Oblique Strategies"),
            ("surprise", "void.joy.surprise", "Serendipity"),
        ]),
    ]

    print("\n[bold]kgents[/] - Tasteful, curated, ethical agents\n")

    for family_name, commands in FAMILIES:
        print(f"\n[bold cyan]{family_name}[/]")
        for cmd, path, desc in commands:
            print(f"  kg {cmd:15} {desc}")

    print("\n[dim]Use 'kg <command> --help' for detailed help[/]")
    print("[dim]Use 'kg ?<pattern>' to query available paths[/]\n")

    return 0
```

---

## Phase 3: Query Integration (Day 2)

### Step 3.1: Interactive Discovery

Allow users to discover affordances interactively:

```bash
# List all available paths
kg ?*

# List all self.* paths
kg ?self.*

# List all aspects of brain
kg ?self.memory.?

# Search by description
kg ?*:capture*
```

### Step 3.2: Completions Integration

**File**: `impl/claude/protocols/cli/completions.py`

Generate shell completions from affordances:

```python
def generate_bash_completions() -> str:
    """Generate bash completions from registered affordances."""
    logos = create_logos()
    result = logos.query("?*.*")

    commands = set()
    for match in result.matches:
        parts = match.path.split(".")
        if len(parts) >= 2:
            commands.add(_path_to_command(match.path))

    return f"""
# kgents bash completions (auto-generated)
_kgents_completions() {{
    local commands="{' '.join(sorted(commands))}"
    COMPREPLY=($(compgen -W "$commands" -- "${{COMP_WORDS[COMP_CWORD]}}"))
}}
complete -F _kgents_completions kg
"""
```

---

## Phase 4: Validation (Day 2)

### Step 4.1: Help Coverage Check

**File**: `impl/claude/protocols/cli/_tests/test_help_coverage.py`

```python
"""Ensure all registered paths have help text."""

def test_all_paths_have_help():
    """Every registered AGENTESE path must have help."""
    logos = create_logos()
    result = logos.query("?*.*.*")

    missing = []
    for match in result.matches:
        meta = logos.get_aspect_meta(match.path)
        if not meta.help:
            missing.append(match.path)

    assert not missing, f"Paths missing help: {missing}"

def test_all_paths_have_examples():
    """Every path should have at least one example."""
    logos = create_logos()
    result = logos.query("?*.*.*")

    missing = []
    for match in result.matches:
        meta = logos.get_aspect_meta(match.path)
        if not meta.examples:
            missing.append(match.path)

    # Warning level, not failure
    if missing:
        warnings.warn(f"Paths missing examples: {missing}")
```

### Step 4.2: Help Accuracy Test

```python
def test_help_matches_behavior():
    """Verify help describes actual behavior."""
    # For each documented flag, verify it's actually handled
    logos = create_logos()
    projector = HelpProjector(logos)

    help = projector.project("self.memory")

    for flag, desc in help.flags:
        # --json should produce JSON output
        if "--json" in flag:
            result = cmd_brain(["status", "--json"])
            assert result == 0
            # Verify output is valid JSON
            ...
```

---

## Acceptance Criteria

1. [x] HelpProjector implemented and tested
2. [x] HelpRenderer with Rich and plain modes
3. [x] All Crown Jewel handlers use projected help
4. [x] Global help shows all command families
5. [x] Query integration (`kg ?pattern`) with formatted output
6. [x] Shell completions generated (bash/zsh/fish via `kg completions`)
7. [x] Handler helper module for easy migration
8. [x] Fallback mechanism ensures robustness

---

## Files Created/Modified

| File | Action | Lines |
|------|--------|-------|
| `protocols/cli/help_projector.py` | Create | ~350 |
| `protocols/cli/help_renderer.py` | Create | ~200 |
| `protocols/cli/help_global.py` | Create | ~200 |
| `protocols/cli/completions.py` | Create | ~350 |
| `protocols/cli/query_help.py` | Create | ~200 |
| `protocols/cli/handlers/_help.py` | Create | ~80 |
| `protocols/cli/_tests/test_help_projection.py` | Create | ~200 |
| `protocols/cli/hollow.py` | Modify | +50 |
| `protocols/cli/agentese_router.py` | Modify | +20 |
| `protocols/cli/handlers/brain_thin.py` | Modify | ~0 net |
| `protocols/cli/handlers/soul_thin.py` | Modify | ~0 net |
| `protocols/cli/handlers/town_thin.py` | Modify | ~0 net |
| `protocols/cli/handlers/park_thin.py` | Modify | ~0 net |
| `protocols/cli/handlers/atelier_thin.py` | Modify | ~0 net |
| `protocols/cli/handlers/gardener_thin.py` | Modify | ~0 net |
| `protocols/cli/_tests/test_hollow.py` | Modify | +10 |

**Total**: ~1500 new lines

---

## UX Examples

### Before
```
$ kg brain --help
kg brain - Holographic Brain CLI (D-gent Triad)

Commands:
  kg brain                      Show brain status
  kg brain capture "content"    Capture content to memory
  ... (manually maintained)
```

### After
```
$ kg brain --help

🧠 Brain - Holographic Memory (self.memory.*)

  High-level memory operations with D-gent Triad.

Commands:
  kg brain capture <content>        Store to holographic memory
  kg brain search <query>           Semantic similarity search
  kg brain surface [context]        Serendipitous retrieval
  kg brain status                   Brain health metrics

Flags:
  --json                 Output as JSON
  --help, -h             Show this help message
  --limit N              Limit results (default: 10)
  --trace                Show trace ID for debugging

Examples:
  $ kg brain capture "Python is great for data science"
  $ kg brain search "category theory"
  $ kg brain surface "agents"

  💰 Some commands use LLM and incur API costs
  🌊 Some commands support streaming output

See also: kg soul, kg town
```

---

*Next: Wave 4 - Observability Integration*
