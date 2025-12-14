---
path: docs/skills/handler-patterns
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: doc-only
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# Skill: Common Handler Patterns

> Write CLI handlers following established patterns for the Hollow Shell architecture.

**Difficulty**: Easy-Medium
**Prerequisites**: [cli-command](cli-command.md) skill, Python basics
**Files Touched**: `protocols/cli/handlers/<name>.py`, `protocols/cli/handlers/__init__.py`

---

## Overview

CLI handlers follow these key patterns:

| Pattern | Description |
|---------|-------------|
| **Signature** | `def cmd_<name>(args: list[str]) -> int` |
| **Subcommands** | Parse via `match` statement |
| **Dual-channel** | Human output (stdout) + Semantic output (FD3) |
| **Async bridging** | Sync entry → `asyncio.run()` → async logic |
| **Lazy imports** | Import dependencies inside function |
| **Help docstring** | Module docstring used for `--help` |

---

## Step-by-Step: Basic Handler

### Step 1: Create Handler File

**File**: `impl/claude/protocols/cli/handlers/<name>.py`

**Template**:
```python
"""
<Name> Handler: Short description.

Longer description of what this handler does.

Usage:
    kgents <name>           # Default action
    kgents <name> --flag    # With flag

Example:
    $ kgents <name>
    [NAME] Output here
"""

from __future__ import annotations


def _print_help() -> None:
    """Print help for command."""
    print(__doc__)


def cmd_<name>(args: list[str]) -> int:
    """
    Short description for inline help.

    Returns:
        0 on success, non-zero on error
    """
    # Parse flags
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Your logic here
    print("[NAME] Done")
    return 0
```

### Step 2: Register in __init__.py

**File**: `impl/claude/protocols/cli/handlers/__init__.py`

Add description comment:
```python
"""
CLI Handlers - Lazy-loaded command implementations.

...
- <name>.py: Description of your handler
"""
```

### Step 3: Register in hollow.py

**File**: `impl/claude/protocols/cli/hollow.py`

Add to lazy loader:
```python
if command == "<name>":
    from protocols.cli.handlers.<name> import cmd_<name>
    return cmd_<name>(args)
```

---

## Step-by-Step: Handler with Subcommands

### Step 1: Parse Subcommand

**Pattern**:
```python
def cmd_myhandler(args: list[str]) -> int:
    """Handle myhandler command with subcommands."""
    # Parse flags
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse subcommand
    subcommand = None
    subcommand_args: list[str] = []

    for arg in args:
        if arg.startswith("-"):
            continue
        if subcommand is None:
            subcommand = arg
        else:
            subcommand_args.append(arg)

    # Default subcommand
    if subcommand is None:
        subcommand = "status"  # or "list", etc.

    # Route to handler
    match subcommand:
        case "list":
            return _handle_list(subcommand_args)
        case "add":
            return _handle_add(subcommand_args)
        case "remove":
            return _handle_remove(subcommand_args)
        case _:
            print(f"[MYHANDLER] X Unknown subcommand: {subcommand}")
            return 1


def _handle_list(args: list[str]) -> int:
    """Handle 'myhandler list' subcommand."""
    # Implementation
    return 0


def _handle_add(args: list[str]) -> int:
    """Handle 'myhandler add' subcommand."""
    if not args:
        print("[MYHANDLER] X Missing argument")
        return 1
    # Implementation
    return 0
```

### Step 2: Add Subcommand Help

```python
def _print_help() -> None:
    """Print help for command."""
    print(__doc__)
    print()
    print("COMMANDS:")
    print("  list              List all items")
    print("  add <item>        Add an item")
    print("  remove <item>     Remove an item")
    print()
    print("OPTIONS:")
    print("  --json            Output as JSON")
    print("  --help, -h        Show this help")
```

---

## Step-by-Step: Async Handler

Many handlers need async (database, network, etc.). Bridge sync→async:

### Step 1: Sync Entry Point

```python
import asyncio

def cmd_myhandler(args: list[str]) -> int:
    """Entry point - sync."""
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Bridge to async
    return asyncio.run(_async_myhandler(args))
```

### Step 2: Async Implementation

```python
async def _async_myhandler(args: list[str]) -> int:
    """Async implementation."""
    try:
        # Parse subcommand
        subcommand = args[0] if args else "list"
        subcommand_args = args[1:] if len(args) > 1 else []

        match subcommand:
            case "list":
                return await _handle_list_async(subcommand_args)
            case "fetch":
                return await _handle_fetch_async(subcommand_args)
            case _:
                print(f"[MYHANDLER] X Unknown: {subcommand}")
                return 1

    except Exception as e:
        print(f"[MYHANDLER] X Error: {e}")
        return 1


async def _handle_list_async(args: list[str]) -> int:
    """Async list handler."""
    # Async operations here
    data = await some_async_fetch()
    print(f"[MYHANDLER] Found {len(data)} items")
    return 0
```

---

## Step-by-Step: Dual-Channel Output

The Reflector Protocol enables handlers to emit:
- **Human output** → stdout (for users)
- **Semantic output** → FD3 (for agents consuming CLI output)

### Step 1: Accept InvocationContext

```python
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def cmd_myhandler(
    args: list[str],
    ctx: "InvocationContext | None" = None,
) -> int:
    """Handler with dual-channel output."""
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context
            ctx = get_invocation_context("myhandler", args)
        except ImportError:
            pass

    # ... rest of handler
```

### Step 2: Create Output Helper

```python
def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """
    Emit output via dual-channel if ctx available, else print.

    Args:
        human: Human-readable string (goes to stdout)
        semantic: Structured data (goes to FD3 for agents)
        ctx: InvocationContext if available
    """
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)
```

### Step 3: Use in Handlers

```python
async def _handle_list(ctx: "InvocationContext | None") -> int:
    """List handler with dual output."""
    items = await fetch_items()

    if not items:
        _emit_output(
            "[MYHANDLER] No items found",
            {"count": 0, "items": []},
            ctx,
        )
    else:
        lines = [f"[MYHANDLER] {len(items)} items"]
        for item in items:
            lines.append(f"  {item.id}: {item.name}")

        _emit_output(
            "\n".join(lines),
            {"count": len(items), "items": [i.to_dict() for i in items]},
            ctx,
        )

    return 0
```

---

## Step-by-Step: JSON Mode

Most handlers support `--json` for machine-readable output:

### Step 1: Parse JSON Flag

```python
def cmd_myhandler(args: list[str]) -> int:
    json_mode = "--json" in args

    # ... rest of parsing
    return asyncio.run(_async_myhandler(json_mode=json_mode, ...))
```

### Step 2: Output Based on Mode

```python
async def _handle_list(json_mode: bool, ctx: "InvocationContext | None") -> int:
    items = await fetch_items()

    if json_mode:
        import json
        result = {"items": [i.to_dict() for i in items]}
        _emit_output(
            json.dumps(result, indent=2),
            result,
            ctx,
        )
    else:
        # Human-friendly format
        for item in items:
            print(f"  {item.id}: {item.name}")

    return 0
```

---

## Step-by-Step: Error Handling

### Pattern 1: Return Error Codes

```python
def cmd_myhandler(args: list[str]) -> int:
    try:
        # ... logic
        return 0  # Success
    except ValueError as e:
        print(f"[MYHANDLER] X Invalid: {e}")
        return 1
    except FileNotFoundError:
        print("[MYHANDLER] X File not found")
        return 1
    except Exception as e:
        print(f"[MYHANDLER] X Error: {e}")
        return 1
```

### Pattern 2: Consistent Error Format

```python
def _emit_error(
    message: str,
    ctx: "InvocationContext | None",
    **extra: Any,
) -> None:
    """Emit error with consistent format."""
    _emit_output(
        f"[MYHANDLER] X {message}",
        {"error": message, **extra},
        ctx,
    )
```

Usage:
```python
if not token_id:
    _emit_error("Missing token ID", ctx)
    return 1
```

---

## Step-by-Step: Lazy Imports

Import heavy dependencies inside functions to keep CLI startup fast:

### Pattern

```python
def cmd_myhandler(args: list[str]) -> int:
    """Handler with lazy imports."""
    # Parse args first (no imports)
    if "--help" in args:
        _print_help()
        return 0

    # Import only when needed
    from agents.flux.semaphore import Purgatory
    from protocols.agentese import create_logos

    # Use imported modules
    purgatory = Purgatory()
    ...
```

---

## Verification

### Test 1: Handler runs

```bash
cd impl/claude
uv run python -c "
from protocols.cli.handlers.myhandler import cmd_myhandler
exit_code = cmd_myhandler(['--help'])
assert exit_code == 0
print('OK')
"
```

### Test 2: Via hollow.py

```bash
cd impl/claude
uv run python -m protocols.cli.hollow myhandler --help
```

### Test 3: Run handler tests

```bash
uv run pytest protocols/cli/handlers/_tests/test_myhandler.py -v
```

---

## Common Pitfalls

### 1. Forgetting return codes

**Wrong**:
```python
def cmd_handler(args):
    print("Done")
    # Missing return!
```

**Right**:
```python
def cmd_handler(args) -> int:
    print("Done")
    return 0
```

### 2. Heavy imports at module level

**Wrong**:
```python
from heavy_module import HeavyClass  # Slows CLI startup

def cmd_handler(args):
    ...
```

**Right**:
```python
def cmd_handler(args):
    from heavy_module import HeavyClass  # Lazy load
    ...
```

### 3. Not handling missing subcommand args

**Wrong**:
```python
case "add":
    item = subcommand_args[0]  # IndexError if empty!
```

**Right**:
```python
case "add":
    if not subcommand_args:
        _emit_error("Missing item", ctx)
        return 1
    item = subcommand_args[0]
```

### 4. Printing instead of dual-channel

**Wrong**:
```python
print(json.dumps(result))  # Agents can't consume this
```

**Right**:
```python
_emit_output(
    json.dumps(result, indent=2),
    result,
    ctx,
)
```

### 5. Not registering in hollow.py

**Symptom**: "Unknown command: myhandler"

**Fix**: Add lazy loader in `hollow.py`:
```python
if command == "myhandler":
    from protocols.cli.handlers.myhandler import cmd_myhandler
    return cmd_myhandler(args)
```

---

## Real Example: Semaphore Handler

The semaphore handler demonstrates all patterns:

1. **Subcommand routing**: `list`, `resolve`, `cancel`, `inspect`, `void`
2. **Async bridging**: `cmd_semaphore()` → `asyncio.run()` → `_async_semaphore()`
3. **Dual-channel**: `_emit_output(human, semantic, ctx)`
4. **JSON mode**: `--json` flag support
5. **Error handling**: Consistent `[SEMAPHORE] X` prefix
6. **Lazy imports**: `from agents.flux.semaphore import Purgatory` inside function

See `impl/claude/protocols/cli/handlers/semaphore.py` for the complete example.

---

## Related Skills

- [cli-command](cli-command.md) - Adding CLI commands (full end-to-end)
- [test-patterns](test-patterns.md) - Testing handlers

---

## Changelog

- 2025-12-12: Initial version based on semaphore and ghost handlers
