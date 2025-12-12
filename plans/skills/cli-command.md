# Skill: Adding a CLI Command

> Add a new command to the kgents CLI with proper lazy-loading, help text, and dual-channel output.

**Difficulty**: Easy
**Prerequisites**: Python basics, understanding of the Hollow Shell pattern
**Files Touched**: `protocols/cli/handlers/<name>.py`, `protocols/cli/hollow.py`
**Time**: ~15 minutes

---

## Overview

The kgents CLI uses the **Hollow Shell** pattern for fast startup:
- Commands are registered by module path (not imported at startup)
- Only the invoked command's module is imported
- Target: `kgents --help` < 50ms

When adding a new command, you need to:
1. Create a handler file in `protocols/cli/handlers/`
2. Register the command in `hollow.py`
3. Optionally add to the help text

---

## Step-by-Step

### Step 1: Create the Handler File

Create a new file at `impl/claude/protocols/cli/handlers/<command>.py`.

**File**: `impl/claude/protocols/cli/handlers/<command>.py`

**Template**:
```python
"""
<Command> Handler: Brief description.

Detailed description of what this command does and why.

Usage:
    kgents <command>              # Default action
    kgents <command> subcommand   # Specific action
    kgents <command> --help       # Show help

Example:
    kgents <command> action "some argument"
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for <command> command."""
    print(__doc__)
    print()
    print("SUBCOMMANDS:")
    print("  action1           Description of action1")
    print("  action2           Description of action2")
    print()
    print("OPTIONS:")
    print("  --flag            Description of flag")
    print("  --json            Output as JSON")
    print("  --help, -h        Show this help")


def cmd_<command>(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Main entry point for the <command> command.

    Args:
        args: Command-line arguments (after the command name)
        ctx: Optional InvocationContext for dual-channel output

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context
            ctx = get_invocation_context("<command>", args)
        except ImportError:
            pass

    # Handle --help flag
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    json_mode = "--json" in args

    # Get subcommand
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
        subcommand = "default"

    # Run async handler
    return asyncio.run(
        _async_<command>(
            subcommand=subcommand,
            subcommand_args=subcommand_args,
            json_mode=json_mode,
            ctx=ctx,
        )
    )


async def _async_<command>(
    subcommand: str,
    subcommand_args: list[str],
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of <command> command."""
    try:
        match subcommand:
            case "action1":
                return await _handle_action1(subcommand_args, json_mode, ctx)
            case "action2":
                return await _handle_action2(subcommand_args, json_mode, ctx)
            case "default":
                return await _handle_default(json_mode, ctx)
            case _:
                _emit_output(
                    f"[<COMMAND>] X Unknown subcommand: {subcommand}",
                    {"error": f"Unknown subcommand: {subcommand}"},
                    ctx,
                )
                return 1

    except ImportError as e:
        _emit_output(
            f"[<COMMAND>] X Module not available: {e}",
            {"error": f"Module not available: {e}"},
            ctx,
        )
        return 1

    except Exception as e:
        _emit_output(
            f"[<COMMAND>] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


async def _handle_default(
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle default action."""
    result = {"status": "ok", "message": "Default action completed"}

    if json_mode:
        import json
        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        _emit_output("[<COMMAND>] Default action completed", result, ctx)

    return 0


async def _handle_action1(
    args: list[str],
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle action1 subcommand."""
    # Implementation here
    return 0


async def _handle_action2(
    args: list[str],
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle action2 subcommand."""
    # Implementation here
    return 0


def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """
    Emit output via dual-channel if ctx available, else print.

    This is the key integration point with the Reflector Protocol:
    - Human output goes to stdout (for humans)
    - Semantic output goes to FD3 (for agents consuming our output)
    """
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)
```

### Step 2: Register in COMMAND_REGISTRY

Add the command to the registry in `hollow.py`.

**File**: `impl/claude/protocols/cli/hollow.py`

**Location**: Find the `COMMAND_REGISTRY` dict (around line 105)

**Pattern**:
```python
COMMAND_REGISTRY: dict[str, str] = {
    # ... existing commands ...

    # <Category> (Brief description)
    "<command>": "protocols.cli.handlers.<command>:cmd_<command>",
}
```

**Example** (adding `soul` command):
```python
COMMAND_REGISTRY: dict[str, str] = {
    # ... existing commands ...

    # K-gent Soul (Digital Simulacra)
    "soul": "protocols.cli.handlers.soul:cmd_soul",
}
```

### Step 3: Update HELP_TEXT (Optional but Recommended)

Add the command to the help text so users can discover it.

**File**: `impl/claude/protocols/cli/hollow.py`

**Location**: Find the `HELP_TEXT` string (around line 40)

**Pattern**:
```python
HELP_TEXT = """\
kgents - Kent's Agents CLI

USAGE:
  kgents <command> [args...]

# ... existing sections ...

<SECTION NAME>:
  <command>   Brief description of what it does

# ... rest of help ...
"""
```

**Example**:
```python
SOUL (Digital Simulacra):
  soul      K-gent self-dialogue (reflect|advise|challenge|explore)
```

### Step 4: Add Aliases (Optional)

For frequently-used subcommands, you can add top-level aliases.

**In the handler file**, add alias functions:
```python
def cmd_alias1(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Alias: kgents alias1 -> kgents <command> subcommand."""
    return cmd_<command>(["subcommand"] + args, ctx)
```

**In hollow.py**, register the aliases:
```python
COMMAND_REGISTRY: dict[str, str] = {
    # ... main command ...
    "<command>": "protocols.cli.handlers.<command>:cmd_<command>",

    # Aliases (top-level shortcuts)
    "alias1": "protocols.cli.handlers.<command>:cmd_alias1",
}
```

### Step 5: Update handlers/__init__.py (Optional)

Document the new handler in the package docstring.

**File**: `impl/claude/protocols/cli/handlers/__init__.py`

**Pattern**:
```python
"""
CLI Handlers - Lazy-loaded command implementations.

Structure:
- ... existing handlers ...
- <command>.py: Brief description
"""
```

---

## Verification

### Test 1: Help displays correctly

```bash
uv run python -m protocols.cli.hollow <command> --help
```

Expected: Your command's help text appears.

### Test 2: Command executes

```bash
uv run python -m protocols.cli.hollow <command>
```

Expected: Default action runs without error.

### Test 3: JSON output works

```bash
uv run python -m protocols.cli.hollow <command> --json
```

Expected: JSON output appears.

### Test 4: Appears in main help

```bash
uv run python -m protocols.cli.hollow --help | grep <command>
```

Expected: Your command appears in the help listing.

---

## Common Pitfalls

### 1. Importing at module level

**Wrong**:
```python
from agents.heavy_module import SomeThing  # Imported at load time!

def cmd_foo(args):
    ...
```

**Right**:
```python
def cmd_foo(args):
    from agents.heavy_module import SomeThing  # Imported only when called
    ...
```

The Hollow Shell pattern requires lazy imports. Module-level imports slow down `kgents --help`.

### 2. Forgetting the ctx parameter

**Wrong**:
```python
def cmd_foo(args: list[str]) -> int:
    ...
```

**Right**:
```python
def cmd_foo(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    ...
```

The `ctx` parameter enables dual-channel output for agent consumption.

### 3. Not using _emit_output

**Wrong**:
```python
print(f"[FOO] Done")
```

**Right**:
```python
_emit_output(
    "[FOO] Done",
    {"status": "done"},
    ctx,
)
```

`_emit_output` sends both human-readable and machine-readable output.

### 4. Blocking the event loop

**Wrong**:
```python
def cmd_foo(args):
    result = await some_async_function()  # Can't await in sync function!
```

**Right**:
```python
def cmd_foo(args):
    return asyncio.run(_async_foo(args))

async def _async_foo(args):
    result = await some_async_function()
```

Use `asyncio.run()` to bridge sync entry point to async implementation.

### 5. Hardcoding error messages

**Wrong**:
```python
print("Error: Something went wrong")
return 1
```

**Right**:
```python
_emit_output(
    "[FOO] X Something went wrong",
    {"error": "Something went wrong"},
    ctx,
)
return 1
```

The `X` prefix and semantic error dict enable proper error handling.

---

## Real Example: The `soul` Command

Here's how the `soul` command was implemented:

1. **Handler**: `impl/claude/protocols/cli/handlers/soul.py` (503 lines)
2. **Registration** in `hollow.py`:
   ```python
   "soul": "protocols.cli.handlers.soul:cmd_soul",
   "reflect": "protocols.cli.handlers.soul:cmd_reflect",
   "advise": "protocols.cli.handlers.soul:cmd_advise",
   "challenge": "protocols.cli.handlers.soul:cmd_challenge",
   "explore": "protocols.cli.handlers.soul:cmd_explore",
   ```
3. **Help text**:
   ```
   SOUL (Digital Simulacra):
     soul      K-gent self-dialogue (reflect|advise|challenge|explore)
   ```

---

## Related Skills

- [agentese-path](agentese-path.md) - Adding AGENTESE paths (future)
- [handler-patterns](handler-patterns.md) - Common handler patterns (future)

---

## Changelog

- 2025-12-12: Initial version based on `soul` command implementation
