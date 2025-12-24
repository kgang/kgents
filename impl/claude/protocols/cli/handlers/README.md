# CLI Thin Handlers

Thin handlers provide the CLI UX layer for kgents commands. They sit between the user and the AGENTESE protocol.

## Architecture Pattern

```
User Input → Thin Handler → AGENTESE Path → Service → Result → Formatted Output
              ├─ Parse args
              ├─ Route to path
              ├─ Format output
              └─ Handle special cases
```

## Two Patterns

### Pattern A: Simple Delegation (Exemplar: `brain_thin.py`)

**When to use**: Simple commands with standard subcommand routing.

**Structure**:
```python
# 1. Routing table
SUBCOMMAND_TO_PATH = {
    "status": "self.service.manifest",
    "list": "self.service.list",
}

# 2. Main handler
def cmd_handler(args, ctx):
    # Parse help
    if "--help" in args:
        _print_help()
        return 0

    # Parse subcommand
    subcommand = _parse_subcommand(args)

    # Special cases (if any)
    if subcommand == "special":
        return _handle_special(args, ctx)

    # Delegate to AGENTESE
    path = route_to_path(subcommand, SUBCOMMAND_TO_PATH, DEFAULT_PATH)
    return project_command(path, args, ctx)
```

**Key characteristics**:
- Routing table maps subcommands to AGENTESE paths
- Uses `project_command()` for delegation
- Keeps only complex special cases as custom handlers
- Minimal custom logic

**Examples**:
- `brain_thin.py` - Simple routing with extinct protocol special case
- `docs.py` - Simple routing with custom arg parsing

### Pattern B: Rich UX Layer (Exemplar: `witness_thin.py`)

**When to use**: Commands with complex interaction, rich formatting, or extensive options.

**Structure**:
```python
def cmd_handler(args, ctx):
    # Parse subcommand
    subcommand = args[0].lower()

    # Route to specialized handlers
    handlers = {
        "mark": cmd_mark,
        "show": cmd_show,
        "crystallize": cmd_crystallize,
        # ... many more
    }

    handler = handlers.get(subcommand)
    if handler:
        return handler(args[1:])

    # Fallback
    _print_help()
    return 1

def cmd_mark(args):
    # Complex arg parsing
    action, reasoning, principles = _parse_mark_args(args)

    # Service interaction
    result = _create_mark(action, reasoning, principles)

    # Rich formatting
    if "--json" in args:
        print(json.dumps(result))
    else:
        _print_rich_mark(result)

    return 0
```

**Key characteristics**:
- Multiple specialized sub-handlers
- Extensive argument parsing
- Rich console formatting (Rich library)
- Interactive flows (REPLs, prompts)
- Both JSON and human-readable output

**Examples**:
- `witness_thin.py` - Extensive mark/crystal operations with tree visualization
- `coffee.py` - Interactive ritual with rich formatting

## Why Not Full AGENTESE Router Delegation?

The AGENTESE router (`agentese_router.py`) is designed for **path invocation**, not **CLI UX**:

- AGENTESE router: `path + kwargs → invoke → result`
- Thin handlers: `args → parse → route → format → output`

Thin handlers provide:
1. **Argument parsing** - Convert CLI args to structured data
2. **Output formatting** - Rich console output vs JSON
3. **Interactive flows** - REPLs, prompts, confirmations
4. **Context handling** - Help text, error messages
5. **Special logic** - Complex subcommand routing

## Guidelines

### When to Add Custom Logic
- Complex argument parsing (multiple flags, combinations)
- Interactive flows (prompts, confirmations)
- Rich formatting (tables, trees, dashboards)
- Sub-subcommands (e.g., `kg brain extinct show <id>`)
- Special validation or error handling

### When to Delegate to AGENTESE
- Simple subcommand routing
- Standard flag parsing
- Pass-through to service methods
- When service already provides good output

### Don't Over-Abstract
Resist the urge to create a "universal handler abstraction". Each command has unique UX needs:
- Brain has extinct protocol
- Witness has mark trees and crystals
- Coffee has ritual movements
- Docs has lint validation

**Better**: Clear, readable handlers that do one thing well.

## Future Evolution

As legacy expansions are added to `protocols/cli/legacy.py`:

```python
# legacy.py
LEGACY_COMMANDS = {
    "brain status": "self.memory.manifest",
    "brain capture": "self.memory.capture",
    # ...
}
```

Users can invoke via:
- Direct: `kg self.memory.manifest`
- Shortcut: `kg /brain`
- Legacy: `kg brain status`
- Handler: `kg brain` (uses thin handler)

All routes converge on the same AGENTESE path, with thin handlers providing rich UX.

## Handler Registration (Required)

Every handler MUST be:
1. **Decorated** with `@handler()` for metadata
2. **Registered** in `hollow.py` COMMAND_REGISTRY

```python
# In your handler file
from protocols.cli.handler_meta import handler

@handler("mycommand", is_async=True, tier=1, description="My command description")
async def cmd_mycommand(args: list[str], ctx: InvocationContext | None = None) -> int:
    ...
```

```python
# In hollow.py COMMAND_REGISTRY
COMMAND_REGISTRY = {
    "mycommand": "protocols.cli.handlers.mycommand_thin:cmd_mycommand",
    ...
}
```

### Handler Metadata

| Field | Default | Description |
|-------|---------|-------------|
| `is_async` | False | If True, handler is awaited |
| `tier` | 1 | Execution tier (1 = async, 2/3 deprecated) |
| `needs_pty` | False | DEPRECATED - always False |
| `cpu_bound` | False | Routes to process pool |
| `io_bound` | True | Routes to thread pool |
| `description` | "" | Short help text |

**Note**: Tier 2 and Tier 3 (PTY modes) were deprecated on 2025-12-24.
All handlers now use Tier 1 (async in daemon event loop or sync in thread pool).

**Exception**: TUI commands (`dawn`, `coffee`) bypass the daemon entirely and run locally.
They require main thread + terminal access for Textual to work properly.

## Daemon Integration

All CLI commands route through the kgentsd daemon. The daemon provides:
- Persistent state across commands
- Trust-gated execution
- Audit logging

### Daemon-Aware Dispatch

Handlers can detect if they're running in the daemon:

```python
import os

in_daemon = os.environ.get("KGENTS_DAEMON_WORKER") is not None

if in_daemon:
    # Use daemon's event loop - handlers called directly
    # ctx.daemon provides access to daemon state
    pass
else:
    # Running locally (KGENTS_NO_DAEMON=1) - bootstrap fresh
    pass
```

### Accessing Daemon Context

```python
@handler("mycommand", is_async=True, tier=1)
async def cmd_mycommand(args: list[str], ctx: InvocationContext | None = None) -> int:
    if ctx and ctx.daemon:
        # Access daemon state
        storage = ctx.daemon.storage_provider
        trust = ctx.daemon.trust_level
    ...
```

## Fallback Mode

Users can run commands without the daemon:

```bash
KGENTS_NO_DAEMON=1 kg mycommand
```

This runs the command locally (with a warning). Useful for:
- Development without daemon infrastructure
- Quick commands when daemon is not started
- Debugging handler code

## Testing

Thin handlers should be testable via:
1. Unit tests for parsing logic
2. Integration tests with mock services
3. Smoke tests via real CLI invocation

Currently most handlers lack tests. Future work: Add comprehensive CLI handler tests.

---

*See also*:
- `protocols/cli/agentese_router.py` - The AGENTESE router
- `protocols/cli/legacy.py` - Legacy command mappings
- `protocols/cli/projection.py` - CLI projection utilities
- `spec/protocols/agentese-v3.md` - AGENTESE protocol spec
