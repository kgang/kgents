# Dashboard Demo Consolidation

> *"The dashboard IS the demo. There is no separate showcase."*

**Principle**: AD-004 (Pre-Computed Richness) + AD-005 (Demo kgents ARE kgents)
**Prerequisites**: HotData infrastructure (`shared/hotdata/`), existing dashboard (`kg dashboard`)

---

## The Problem

We have fragmented demo infrastructure:
- `agents/i/demo_all_screens.py` - Standalone script with menu navigation
- `kg dashboard --demo` - Dashboard with demo metrics
- Various `create_demo_*()` functions scattered across modules

This violates the principle: **Demo kgents ARE kgents**. The demo should not be a separate artifact - it should be the dashboard running in demo mode.

---

## The Vision

```bash
# The ONE command to showcase kgents
kg dashboard --demo

# Which shows:
# - All screens accessible via keybindings (1-9, Tab, etc.)
# - Rich HotData fixtures loaded automatically
# - Same UI as production, just with pre-computed data
```

---

## Part 1: Dashboard as Universal Demo Container

**Goal**: Make `kg dashboard` the single entry point for all visualization demos.

### Tasks

1. **Add screen navigation to DashboardScreen**:
   - `1` → FluxScreen (LOD 0: ORBIT)
   - `2` → CockpitScreen (LOD 1: SURFACE)
   - `3` → MRIScreen (LOD 2: INTERNAL)
   - `4` → LoomScreen (Cognitive Loom)
   - `5` → ObservatoryScreen (LOD -1: Gardens)
   - `6` → ForgeScreen (Compose mode)
   - `Tab` → Cycle through screens
   - `Esc` → Return to main dashboard

2. **Update `protocols/cli/handlers/dashboard.py`**:
   ```python
   def cmd_dashboard(args: list[str]) -> int:
       demo_mode = "--demo" in args
       # In demo mode, pre-load all HotData fixtures
       if demo_mode:
           _load_all_demo_fixtures()
       # ...
   ```

3. **Add help overlay** (`?` key):
   - Show available screens and keybindings
   - Explain demo mode vs live mode
   - List fixture sources

### Exit Criteria
- `kg dashboard --demo` shows all screens via keybindings
- Same experience as `demo_all_screens.py` but within dashboard

---

## Part 2: HotData Auto-Registration

**Goal**: Fixtures self-register when their modules are imported.

### Tasks

1. **Create `fixtures/__init__.py`** that imports and registers all fixtures:
   ```python
   """Auto-register all demo fixtures."""
   from agents.i.data.state import DEMO_FLUX_STATE_HOTDATA
   from agents.i.data.garden import DEMO_POLYNOMIAL_STATE_HOTDATA
   # ... all fixtures

   def load_all_fixtures() -> None:
       """Force-load all fixtures (call in demo mode)."""
       # Triggers all registrations via imports
       pass
   ```

2. **Update demo functions** to use consistent pattern:
   ```python
   # At module level - registers automatically on import
   DEMO_FOO_HOTDATA = HotData(
       path=FIXTURES_DIR / "foo" / "demo.json",
       schema=Foo,
   )
   register_hotdata("demo_foo", DEMO_FOO_HOTDATA)

   def create_demo_foo() -> Foo:
       return DEMO_FOO_HOTDATA.load_or_default(_create_fallback_foo())
   ```

3. **Wire `kg fixture list`** to show all registered fixtures:
   ```bash
   $ kg fixture list
   [FIXTURES] 12 registered | 10 fresh | 2 stale

   demo_flux_state         FRESH    fixtures/flux_states/demo.json
   demo_cognitive_tree     FRESH    fixtures/cognitive_trees/demo.json
   ...
   ```

### Exit Criteria
- `kg fixture list` shows all 10+ demo fixtures
- `kg dashboard --demo` loads all fixtures automatically

---

## Part 3: Remove Standalone Demo Script

**Goal**: Delete `demo_all_screens.py` once dashboard subsumes its functionality.

### Tasks

1. **Verify parity**: Ensure `kg dashboard --demo` can show everything `demo_all_screens.py` showed

2. **Delete the file**:
   ```bash
   rm agents/i/demo_all_screens.py
   ```

3. **Update any references**:
   - `README.md` or docs that mention `demo_all_screens.py`
   - CI scripts that might run it
   - plans/ files that reference it

### Exit Criteria
- `demo_all_screens.py` is deleted
- `kg dashboard --demo` is the documented demo command

---

## Part 4: Documentation Updates

**Goal**: Establish the pattern that demos live in dashboard, not standalone scripts.

### Tasks

1. **Update `plans/skills/hotdata-pattern.md`**:
   - Add "Demos belong in Dashboard" section
   - Show how to add a new demo screen

2. **Update `HYDRATE.md`**:
   - Change demo command from `uv run python agents/i/demo_all_screens.py` to `kg dashboard --demo`

3. **Add to `CLAUDE.md`**:
   ```markdown
   ## Demo Philosophy

   **The dashboard IS the demo.** Never create standalone demo scripts.

   To showcase a new feature:
   1. Add a HotData fixture to `fixtures/`
   2. Create a demo function using `load_or_default()`
   3. Add keybinding to dashboard for the new screen
   4. Document in `kg dashboard --help`
   ```

### Exit Criteria
- All documentation points to `kg dashboard --demo`
- Pattern is clear for future contributors

---

## Integration Checklist

After all parts complete:

- [ ] `kg dashboard --demo` launches with all screens accessible
- [ ] Screen navigation via number keys (1-6) and Tab
- [ ] Help overlay shows all keybindings (`?` key)
- [ ] `demo_all_screens.py` is deleted
- [ ] `kg fixture list` shows all registered fixtures
- [ ] Documentation updated (CLAUDE.md, HYDRATE.md, plans/)
- [ ] All tests pass

---

## The Mantra

> *"If you want to demo something, add it to the dashboard. If you're tempted to write a standalone demo script, you're doing it wrong."*

---

## Command to Start

```bash
# First, verify current demo works
kg dashboard --demo

# Then read the dashboard handler
cat impl/claude/protocols/cli/handlers/dashboard.py
```

---

*Execute /hydrate before each session to maintain context.*
