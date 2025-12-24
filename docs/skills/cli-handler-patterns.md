---
path: docs/skills/cli-handler-patterns
status: active
progress: 100
last_touched: 2025-12-24
touched_by: claude-opus-4
blocking: []
enables: [metaphysical-fullstack, crown-jewel-patterns]
session_notes: |
  Deep audit of CLI architecture. Documents the complete handler lifecycle,
  integration patterns, and principled approach to building handlers that
  compose with AGENTESE, daemon, and the witness system.
phase_ledger:
  PLAN: complete
  REFLECT: complete
---

# Skill: CLI Handler Patterns

> *"The handler is a membrane between intent and action. It must be fast enough to feel like no interface at all."*

**Difficulty**: Intermediate
**Prerequisites**: `metaphysical-fullstack.md`, `agentese-path.md`, `crown-jewel-patterns.md`
**Source**: Deep audit of `protocols/cli/` architecture (2025-12-24)

---

## The Philosophy

CLI handlers in kgents are NOT traditional command parsers. They are **projection functors** that transform user intent into AGENTESE invocations and project results back to terminal surfaces.

```
User Intent → Handler (parse) → AGENTESE Path → Service → Result → Handler (format) → Terminal
```

**Key Insight**: The handler's job is UX, not logic. Business logic lives in services; handlers provide the human interface.

---

## The Handler Taxonomy

Every handler fits one of three patterns. Choose deliberately.

### Pattern A: Thin Delegation (Exemplar: `brain_thin.py`)

**When**: Simple subcommand routing with standard options.

**Structure**:
```python
from protocols.cli.handler_meta import handler
from protocols.cli.projection import project_command, route_to_path

# 1. Routing table maps subcommands → AGENTESE paths
SUBCOMMAND_TO_PATH = {
    "status": "self.service.manifest",
    "action": "self.service.action",
}
DEFAULT_PATH = "self.service.manifest"

# 2. Main handler decorated and async
@handler("mycommand", is_async=True, tier=1, description="My command")
async def cmd_mycommand(args: list[str], ctx: InvocationContext | None = None) -> int:
    # Handle help (fast path)
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse subcommand
    subcommand = _parse_subcommand(args)

    # Special cases (complex UX that can't delegate)
    if subcommand == "complex":
        return await _handle_complex(args, ctx)

    # Default: delegate to AGENTESE via projection
    path = route_to_path(subcommand, SUBCOMMAND_TO_PATH, DEFAULT_PATH)

    # Use async projection in daemon context
    in_daemon = os.environ.get("KGENTS_DAEMON_WORKER") is not None
    if in_daemon:
        return await project_command_async(path, args, ctx)
    return project_command(path, args, ctx)
```

**Key Characteristics**:
- Routing table is the source of truth
- Uses `project_command()` for delegation
- Only custom handlers for truly complex UX
- Minimal lines of code

**When to Use**:
- Service exposes clean AGENTESE aspects
- Subcommands map 1:1 to service methods
- No complex interactive flows

---

### Pattern B: Rich UX Layer (Exemplar: `witness/__init__.py`)

**When**: Complex interaction, rich formatting, extensive options.

**Structure**:
```python
from protocols.cli.handler_meta import handler

@handler("witness", is_async=True, tier=1, description="Everyday mark-making")
async def cmd_witness(args: list[str], ctx: InvocationContext | None = None) -> int:
    if not args or "--help" in args:
        _print_help()
        return 0

    subcommand = args[0].lower()
    sub_args = args[1:]

    # Route to specialized async handlers
    handlers = {
        "mark": cmd_mark_async,
        "show": cmd_show_async,
        "crystallize": cmd_crystallize_async,
        "tree": cmd_tree_async,
        # ...
    }

    if subcommand in handlers:
        return await handlers[subcommand](sub_args)

    # Unknown subcommand: treat as mark action
    if not subcommand.startswith("-"):
        return await cmd_mark_async(args)

    _print_help()
    return 1
```

**Key Characteristics**:
- Multiple specialized sub-handlers
- Complex argument parsing per subcommand
- Rich console formatting (Rich library)
- Both JSON and human-readable output
- Interactive flows (prompts, confirmations)

**When to Use**:
- Complex subcommand trees (sub-subcommands)
- Rich visualization (trees, tables, dashboards)
- Interactive capture flows
- Extensive option combinations

---

### Pattern C: Ritual Interface (Exemplar: `coffee.py`)

**When**: The command IS the experience, not just a tool.

**Structure**:
```python
@handler("coffee", is_async=False, tier=1, description="Morning Coffee ritual")
def cmd_coffee(args: list[str], ctx: InvocationContext | None = None) -> int:
    """
    This handler IS the ritual. Not just calling a service.
    """
    json_output = "--json" in args

    if "--full" in args:
        return _run_full_ritual()  # Interactive, multi-stage

    if "--quick" in args:
        return _run_quick_ritual()  # Abbreviated flow

    subcommand = _parse_subcommand(args)

    match subcommand:
        case "garden":
            return _run_garden(json_output)
        case "weather":
            return _run_weather(json_output)
        case "begin":
            return _run_begin(args, json_output)  # Complex with circadian context
        case _:
            return _run_manifest(json_output)
```

**Key Characteristics**:
- Multi-stage flows with user interaction
- Ceremonial structure (movements, stages)
- Context gathering across stages
- Service is thin; UX is the value

**When to Use**:
- The CLI experience IS the product
- Multi-stage workflows
- User-guided processes
- Liminal/transition protocols

---

## The Handler Contract

Every handler MUST follow this contract.

### 1. Registration (Two Places)

```python
# 1. In handler file: @handler decorator
from protocols.cli.handler_meta import handler

@handler(
    "mycommand",              # Name (matches hollow.py key)
    is_async=True,            # Async handlers preferred
    tier=1,                   # Always tier 1 now
    description="Short desc"  # For help generation
)
async def cmd_mycommand(args: list[str], ctx: InvocationContext | None = None) -> int:
    ...
```

```python
# 2. In hollow.py COMMAND_REGISTRY
COMMAND_REGISTRY = {
    "mycommand": "protocols.cli.handlers.mycommand:cmd_mycommand",
    ...
}
```

**Both are required**. The decorator provides metadata; the registry provides routing.

### 2. Signature

```python
async def cmd_mycommand(
    args: list[str],                          # Raw CLI args (after command name)
    ctx: InvocationContext | None = None      # Optional daemon context
) -> int:                                      # Exit code: 0=success, non-zero=failure
```

### 3. Help (Fast Path)

```python
if "--help" in args or "-h" in args:
    _print_help()
    return 0
```

Help MUST be checked first. No heavy imports before help check.

### 4. Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General failure |
| 2 | Invalid usage |
| 130 | Interrupted (Ctrl+C) |

---

## Daemon Integration

All commands route through `kgentsd` daemon. Handlers must be daemon-aware.

### Detecting Daemon Context

```python
import os

in_daemon = os.environ.get("KGENTS_DAEMON_WORKER") is not None

if in_daemon:
    # Use async projection (shares daemon event loop)
    return await project_command_async(path, args, ctx)
else:
    # Running locally (fallback mode)
    return project_command(path, args, ctx)
```

### Async vs Sync Handlers

**Prefer async handlers** (`is_async=True`). They:
- Run directly on daemon event loop
- Share database sessions properly
- Avoid nested event loop issues

**Sync handlers** are acceptable for:
- Pure computation (no I/O)
- Delegating to subprocess (TUI apps)

### TUI Commands (Exception)

TUI apps (`dawn`, `coffee --full`) bypass daemon:

```python
# In hollow.py main()
TUI_COMMANDS = {"dawn", "coffee"}
if command in TUI_COMMANDS:
    # Run locally, not through daemon
    handler = resolve_command(command)
    return handler(command_args)
```

Why: Textual TUI requires main thread + terminal access.

---

## AGENTESE Integration

Handlers project to AGENTESE paths. The projection functor handles:
- Observer creation
- Dimension derivation
- Result formatting

### Route → Path → Project

```python
# 1. Define routing table
SUBCOMMAND_TO_PATH = {
    "capture": "self.memory.capture",
    "search": "self.memory.recall",
}

# 2. Route subcommand to path
path = route_to_path(subcommand, SUBCOMMAND_TO_PATH, DEFAULT_PATH)

# 3. Project command
return project_command(path, args, ctx)
```

### Kwargs Extraction

```python
# project_command extracts kwargs from args:
# --key=value  → kwargs["key"] = value
# --key value  → kwargs["key"] = value
# --flag       → kwargs["flag"] = True
# positional   → mapped by path heuristics

# For custom extraction:
kwargs = {"content": " ".join(positionals)}
return project_command(path, args, ctx, kwargs=kwargs)
```

---

## Dual-Channel Output (Pattern 7)

Every handler should support both humans and agents.

```python
def _emit_output(
    human: str,
    semantic: dict,
    json_output: bool,
) -> None:
    """Emit both human-readable and machine-readable output."""
    if json_output:
        print(json.dumps(semantic, indent=2, default=str))
    else:
        print(human)
```

**Usage**:
```python
json_output = "--json" in args

# ... do work ...

if json_output:
    print(json.dumps(result_dict, indent=2, default=str))
else:
    from services.my.formatting import format_rich
    print(format_rich(result_dict))
```

---

## Witness Integration

Handlers should emit marks for significant actions.

### On Failure (Probes)

```python
from services.witness.mark import Mark
from services.witness.trace_store import get_mark_store

if result.failed:
    mark = Mark.from_thought(
        content=f"Probe {result.name} FAILED",
        source="probe",
        tags=("probe", "failure"),
        origin="probe_cli",
    )
    store = get_mark_store()
    store.append(mark)
```

### On Significant Action

```python
async def _emit_analysis_marks(report, target: str, mode: str) -> None:
    """Emit witness marks for analysis results."""
    from protocols.cli.handlers.witness.marks import _create_mark_async

    await _create_mark_async(
        action=f"Analyzed {target} ({mode})",
        reasoning=f"Results: {summary}",
        principles=["generative"],
        tags=["analysis", mode],
        author="analysis_operad",
    )
```

---

## Anti-Patterns

### ❌ Business Logic in Handler

```python
# WRONG: Handler doing service work
def cmd_brain(args):
    adapter = TableAdapter(Crystal, session_factory)  # Service layer!
    crystal = Crystal(...)  # Domain model!
    adapter.put(crystal)  # Persistence!
```

### ❌ Sync Wrappers in Async Handlers

```python
# WRONG: Breaks event loop sharing
@handler("x", is_async=True, tier=1)
async def cmd_x(args, ctx):
    # This creates nested event loops!
    result = asyncio.run(some_async_work())
```

### ❌ Heavy Imports Before Help

```python
# WRONG: Slow startup even for --help
from services.heavy import HeavyService  # 500ms import

@handler("x", is_async=True, tier=1)
async def cmd_x(args, ctx):
    if "--help" in args:
        _print_help()  # Already waited for import!
        return 0
```

```python
# RIGHT: Lazy import after help check
@handler("x", is_async=True, tier=1)
async def cmd_x(args, ctx):
    if "--help" in args:
        _print_help()
        return 0

    from services.heavy import HeavyService  # Only if needed
```

### ❌ Swallowing Errors

```python
# WRONG: User sees nothing
try:
    result = await do_work()
except Exception:
    pass  # Silent failure
```

```python
# RIGHT: Surface errors
try:
    result = await do_work()
except Exception as e:
    print(f"Error: {e}")
    return 1
```

### ❌ Direct Database Access

```python
# WRONG: Bypass service layer
def cmd_brain(args):
    session = get_session()
    crystals = session.query(Crystal).all()  # Direct DB!
```

---

## The Complete Checklist

Before merging a new handler:

- [ ] **Registered** in `hollow.py` COMMAND_REGISTRY
- [ ] **Decorated** with `@handler()` and correct metadata
- [ ] **Async preferred** (`is_async=True`) unless TUI
- [ ] **Help fast path** before any heavy imports
- [ ] **Subcommand routing** via table or match statement
- [ ] **AGENTESE delegation** where applicable
- [ ] **Daemon-aware** (`KGENTS_DAEMON_WORKER` check)
- [ ] **Dual-channel output** (`--json` flag support)
- [ ] **Witness integration** for significant actions
- [ ] **Error surfacing** (no silent failures)
- [ ] **Exit codes** (0 success, 1+ failure)

---

## Examples

### Minimal Handler (Pattern A)

```python
"""Minimal handler that delegates everything to AGENTESE."""
from protocols.cli.handler_meta import handler
from protocols.cli.projection import project_command, route_to_path

SUBCOMMAND_TO_PATH = {
    "status": "self.service.manifest",
    "do": "self.service.action",
}

@handler("minimal", is_async=True, tier=1, description="Minimal example")
async def cmd_minimal(args: list[str], ctx=None) -> int:
    if "--help" in args:
        print("kg minimal [status|do]")
        return 0

    subcommand = args[0] if args and not args[0].startswith("-") else "status"
    path = route_to_path(subcommand, SUBCOMMAND_TO_PATH, "self.service.manifest")
    return project_command(path, args, ctx)
```

### Rich Handler (Pattern B)

```python
"""Rich handler with complex formatting."""
from protocols.cli.handler_meta import handler

@handler("rich", is_async=True, tier=1, description="Rich example")
async def cmd_rich(args: list[str], ctx=None) -> int:
    if "--help" in args:
        _print_help()
        return 0

    json_output = "--json" in args
    subcommand = _parse_subcommand(args)

    if subcommand == "tree":
        return await _cmd_tree(args[1:], json_output)
    elif subcommand == "stats":
        return await _cmd_stats(args[1:], json_output)
    else:
        return await _cmd_default(json_output)

async def _cmd_tree(args: list[str], json_output: bool) -> int:
    # Complex tree visualization
    from services.my.tree import build_tree

    tree = await build_tree()

    if json_output:
        print(json.dumps(tree.to_dict(), indent=2))
    else:
        from rich.tree import Tree
        from rich import print as rprint
        rprint(_build_rich_tree(tree))

    return 0
```

---

## Related

- [metaphysical-fullstack](metaphysical-fullstack.md) — The vertical slice architecture
- [agentese-path](agentese-path.md) — AGENTESE path structure
- [crown-jewel-patterns](crown-jewel-patterns.md) — Service patterns (Pattern 7: Dual-Channel)
- [witness-for-agents](witness-for-agents.md) — Witness integration for agents

---

*"The handler is invisible when done right. The user sees the action, not the membrane."*
