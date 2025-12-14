# QA Continuation: Marimo-Native UI/UX Crown Jewel

> *"The field does not display state; it is state made visible."*

## Context

We've implemented Wave 0-3 of the marimo-native kgents visualization system. The implementation creates anywidget-based components that work in marimo notebooks.

## What Was Built

### Files Created

```
impl/claude/agents/i/marimo/
├── __init__.py                    # Package exports
├── logos_bridge.py                # AGENTESE-marimo bridge (LogosCell, ObserverState)
└── widgets/
    ├── __init__.py
    ├── base.py                    # KgentsWidget base class
    ├── stigmergic_field.py        # StigmergicFieldWidget
    ├── dialectic.py               # DialecticWidget
    ├── timeline.py                # TimelineWidget
    └── js/
        ├── stigmergic_field.js    # Canvas-based entity/pheromone rendering
        ├── dialectic.js           # Three-panel thesis/antithesis/synthesis
        └── timeline.js            # Horizontal scrollable timeline

notebooks/
├── kgents_demo.py                 # Full demonstration notebook
└── simple_test.py                 # Minimal anywidget test
```

### Key Implementation Details

1. **anywidgets use external JS files** via `pathlib.Path`:
   ```python
   _esm = _JS_DIR / "stigmergic_field.js"
   ```

2. **Widgets must be wrapped with `mo.ui.anywidget()`** for marimo:
   ```python
   raw_widget = StigmergicFieldWidget.from_field_state(field_state)
   field_widget = mo.ui.anywidget(raw_widget)
   ```

3. **Raw widget references needed for method calls**:
   ```python
   # To call methods like .set_synthesis(), use raw_dialectic not dialectic
   raw_dialectic.set_synthesis("...", confidence=0.85)
   ```

## QA Tasks

### 1. Basic Functionality Test
```bash
cd /Users/kentgang/git/kgents
marimo run notebooks/kgents_demo.py
# Open http://localhost:2718 (or whatever port)
```

**Verify:**
- [ ] Page loads without console errors (F12 → Console)
- [ ] StigmergicFieldWidget renders (dark canvas with colored entity symbols)
- [ ] DialecticWidget renders (three-panel layout with thesis/antithesis/synthesis)
- [ ] TimelineWidget renders (horizontal track with event markers)

### 2. Widget Interactivity Test

**StigmergicFieldWidget:**
- [ ] Entities display with correct symbols (I, C, G, J, X, S, F, *, ◊)
- [ ] Status bar shows tick count, entropy %, heat, phase
- [ ] Entropy slider changes visual noise level
- [ ] "Advance Tick" button triggers simulation step
- [ ] Clicking an entity highlights it (scale + background change)

**DialecticWidget:**
- [ ] Three panels show with colored headers (amber/rose/sage)
- [ ] Progress bar at bottom
- [ ] "Synthesize" button fills synthesis panel
- [ ] "New Dialectic" button resets all panels

**TimelineWidget:**
- [ ] Event markers display on track
- [ ] Hover shows preview popup with event details
- [ ] Play/pause button works
- [ ] Zoom +/- buttons adjust scale
- [ ] Clicking marker updates current_tick

### 3. Error Scenarios to Check

- [ ] No "Module does not appear to be a valid anywidget" error
- [ ] No JavaScript console errors
- [ ] No Python tracebacks in terminal

### 4. Type Safety (Optional)
```bash
cd /Users/kentgang/git/kgents
uv run mypy impl/claude/agents/i/marimo/ --ignore-missing-imports
```

### 5. Existing Tests Still Pass
```bash
uv run pytest impl/claude/agents/i/_tests/ -q --tb=no
# Should see: 566 passed
```

## Known Issues / Observations

1. The `mo.ui.anywidget()` wrapper is required - direct anywidget display fails
2. JS files use external Path references, not inline strings (marimo serving issue)
3. Method calls (`.set_synthesis()`, `.update_from_field_state()`) must use raw widget

## If Issues Found

Document:
1. Exact error message (console or terminal)
2. Which widget/cell caused it
3. Browser used (Chrome/Firefox/Safari)
4. Steps to reproduce

## Exit Criteria

- [ ] All three widgets render correctly
- [ ] All interactive controls function
- [ ] No JavaScript or Python errors
- [ ] 566 existing I-gent tests still pass

---

## Commands Reference

```bash
# Run demo notebook
marimo run notebooks/kgents_demo.py

# Run simple test
marimo run notebooks/simple_test.py

# Edit notebook (interactive mode)
marimo edit notebooks/kgents_demo.py

# Run tests
uv run pytest impl/claude/agents/i/_tests/ -q

# Type check
uv run mypy impl/claude/agents/i/marimo/ --ignore-missing-imports
```

---

*"The noun is a lie. There is only the rate of change. And now, the rate of change is visible."*
