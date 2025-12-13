# Navigation System

**Track D: Unified Navigation for Dashboard Screens**

## Overview

The navigation system provides seamless zoom in/out transitions across all dashboard screens, with state persistence and global keybindings.

## Architecture

### Components

1. **StateManager** (`state.py`)
   - Persists focus and selection state across screen transitions
   - Maintains navigation history (breadcrumb trail)
   - Provides working memory for the dashboard

2. **NavigationController** (`controller.py`)
   - Orchestrates LOD (Level of Detail) transitions
   - Manages screen stack and history
   - Implements zoom in/out semantics

### LOD Hierarchy

```
LOD -1: Observatory     (ecosystem view)
        ↕ zoom
LOD  0: Dashboard       (system health)
        ↕ zoom
LOD  1: Cockpit         (single agent)
        ↕ zoom
LOD  2: Debugger        (forensic analysis)

Special screens (accessible from any LOD):
  - Forge      (agent composition)
  - Debugger   (turn analysis)
```

## Global Keybindings

| Key | Action |
|-----|--------|
| `+` / `=` | Zoom in (more detail) |
| `-` / `_` | Zoom out (broader view) |
| `f` | Open Forge |
| `d` | Open Debugger |
| `?` | Show help |
| `q` | Quit |

## Usage

### In DashboardApp

```python
from agents.i.navigation import NavigationController, StateManager

# Initialize
state_mgr = StateManager()
nav_controller = NavigationController(app, state_mgr)

# Register screens
nav_controller.register_lod_screen(-1, create_observatory)
nav_controller.register_lod_screen(0, create_dashboard)
nav_controller.register_lod_screen(1, create_cockpit)
nav_controller.register_forge(create_forge)
nav_controller.register_debugger(create_debugger)

# Navigate
nav_controller.zoom_in(focus="agent-123")
nav_controller.zoom_out()
nav_controller.go_to_forge()
```

### Saving State

```python
# Save focus before transitioning
state_mgr.save_focus("observatory", "garden-123")

# Retrieve focus on return
focus = state_mgr.get_focus("observatory")  # → "garden-123"

# Navigation history
state_mgr.push_history("observatory", "garden-123")
prev = state_mgr.pop_history()  # → ("observatory", "garden-123")
```

## Testing

```bash
# Run navigation tests
python -m pytest agents/i/navigation/_tests/ -v

# Run full integration tests
python -m pytest agents/i/screens/ agents/i/navigation/ -v
```

## Design Principles

1. **State Persistence**: Focus and selection survive screen transitions
2. **Zoom Semantics**: +/- are semantic zoom, not just visual
3. **Graceful Degradation**: Unregistered screens fail silently
4. **Working Memory**: Navigation history provides breadcrumb trail
5. **Global Access**: Special screens (Forge, Debugger) accessible anywhere

## Implementation Status

- [x] StateManager with focus/selection persistence
- [x] NavigationController with zoom logic
- [x] DashboardApp integration
- [x] Global keybindings
- [x] Comprehensive test suite (35 tests)
- [x] Screen factories for all LODs

## Future Enhancements

- [ ] Breadcrumb UI component
- [ ] Persistent state to disk
- [ ] Screen transition animations
- [ ] Keyboard shortcuts overlay
- [ ] Multi-window support
