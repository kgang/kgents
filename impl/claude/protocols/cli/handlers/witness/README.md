# Witness CLI Handler - Modular Architecture

This directory contains the modularized witness CLI handler, previously a monolithic 2400+ line file (`witness_thin.py`).

## Directory Structure

```
witness/
├── __init__.py          # Main entry point, routes to submodules
├── base.py              # Shared utilities (console, async bootstrap)
├── marks.py             # Mark operations (create, show, session)
├── crystals.py          # Crystal operations (crystallize, list, details)
├── context.py           # Context retrieval (budget-aware)
├── tree.py              # Tree operations (causal tree, ancestry)
├── integration.py       # Integration (stream, NOW.md, Brain promotion)
└── dashboard.py         # Dashboard (TUI, graph visualization)
```

## Module Responsibilities

### `__init__.py`
- Main `cmd_witness()` handler (decorated with `@handler`)
- Routes subcommands to appropriate modules
- Exports public API (`cmd_mark`, `cmd_show`, etc.)
- Prints help text

### `base.py`
Shared utilities used across all modules:
- `_get_console()` - Rich console helper
- `_print_mark()` - Single mark formatting
- `_print_marks()` - Multiple mark formatting
- `_parse_timestamp()` - ISO timestamp parsing
- `_bootstrap_and_run()` - Service bootstrap wrapper
- `_run_async_factory()` - Sync wrapper for async functions

### `marks.py`
Mark creation and retrieval:
- `cmd_mark()` - Create a mark
- `cmd_show()` - Show recent marks with filtering
- `cmd_session()` - Show current session's marks
- `_cmd_mark_async()` - Async version for daemon mode
- `_cmd_show_async()` - Async version for daemon mode
- `_create_mark_async()` - Core mark persistence
- `_get_recent_marks_async()` - Core mark retrieval

### `crystals.py`
Crystal operations:
- `cmd_crystallize()` - Crystallize marks into insight
- `cmd_crystals()` - List recent crystals
- `cmd_crystal()` - Show crystal details
- `cmd_expand()` - Show crystal sources
- `_crystallize_async()` - Core crystallization
- `_get_crystals_async()` - Core crystal retrieval

### `context.py`
Context retrieval:
- `cmd_context()` - Budget-aware crystal context

### `tree.py`
Tree operations:
- `cmd_tree()` - Show causal tree or ancestry
- `_get_mark_tree_async()` - Core tree retrieval
- `_get_mark_ancestry_async()` - Core ancestry retrieval

### `integration.py`
Integration features:
- `cmd_stream()` - Stream crystal events
- `cmd_propose_now()` - Propose NOW.md updates
- `cmd_promote()` - Promote crystals to Brain

### `dashboard.py`
Visualization:
- `cmd_dashboard()` - Textual TUI crystal navigator
- `cmd_graph()` - Crystal graph as JSON

## Import Patterns

### External usage (from other modules):
```python
# Import commands directly
from protocols.cli.handlers.witness import cmd_mark, cmd_show, cmd_dashboard

# Import async functions for daemon mode
from protocols.cli.handlers.witness.marks import _create_mark_async

# Import the main handler
from protocols.cli.handlers.witness import cmd_witness
```

### Internal usage (within witness package):
```python
# Import from base module
from .base import _get_console, _print_marks, _run_async_factory

# Import from sibling modules
from .marks import cmd_mark
from .crystals import _get_crystals_async
```

## Migration from witness_thin.py

All imports from `witness_thin` have been updated:

| Old Import | New Import |
|------------|------------|
| `from protocols.cli.handlers.witness_thin import cmd_mark` | `from protocols.cli.handlers.witness import cmd_mark` |
| `from protocols.cli.handlers.witness_thin import cmd_dashboard` | `from protocols.cli.handlers.witness import cmd_dashboard` |
| `from protocols.cli.handlers.witness_thin import _create_mark_async` | `from protocols.cli.handlers.witness.marks import _create_mark_async` |

## Benefits of Modular Structure

1. **Maintainability**: Each module has a clear, focused purpose (~200-500 lines)
2. **Testability**: Modules can be tested independently
3. **Discoverability**: Easier to find specific functionality
4. **Import optimization**: Only import what you need
5. **Parallel development**: Multiple developers can work on different modules
6. **Code review**: Smaller, focused changes

## Preserved Functionality

All functionality from `witness_thin.py` has been preserved:
- All CLI commands work identically
- Async/sync handling for daemon mode unchanged
- Import compatibility maintained via `__all__` exports
- Help text unchanged
- All decorators and metadata preserved
