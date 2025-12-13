# UI Walkthrough: Manual Testing Session

> A guided tour through kgents TUI implementations.

## Mission

Walk the developer through each UI screen, verifying functionality and identifying issues. This is a **manual testing session** - run commands, observe behavior, report findings.

## Prerequisites

```bash
cd /Users/kentgang/git/kgents/impl/claude
```

## Walkthrough Sequence

### 1. Dashboard (LOD 0)

```bash
kg dashboard --demo
```

**Verify:**
- [ ] 6 panels render (K-GENT, METABOLISM, FLUX, TRIAD, TRACES, CALL GRAPH)
- [ ] Metrics update in real-time (watch pressure bar, sparklines)
- [ ] Keys 1-4 focus panels (no notification spam)
- [ ] `r` refreshes, `d` toggles demo mode, `q` quits

**Navigation test:**
- [ ] `+` or `=` → zooms to Cockpit
- [ ] `-` or `_` → zooms to Observatory
- [ ] `?` → shows help overlay

---

### 2. Observatory (LOD -1)

From dashboard, press `-` to zoom out.

**Verify:**
- [ ] Shows garden clusters (agent groups)
- [ ] Breathing animation visible
- [ ] Can select gardens
- [ ] `+` returns to Dashboard

---

### 3. Cockpit (LOD 1)

From dashboard, press `+` to zoom in.

**Verify:**
- [ ] Shows single agent view with larger density field
- [ ] Metrics panel (pressure/flow/temp)
- [ ] Temperature slider works (`h`/`l` or arrow keys)
- [ ] Semaphores display
- [ ] Thoughts stream
- [ ] Polynomial state panel (if demo mode)
- [ ] **Yield Queue panel** - shows pending approvals
  - Keys 1-5 select yield
  - `a` approves, `x` rejects
- [ ] `+` → MRI view, `-` → back to Dashboard

---

### 4. Forge (Special Screen)

From any screen, press `f`.

**Verify:**
- [ ] Opens without MountError
- [ ] Left panel: Agent palette with AGENTS and PRIMITIVES sections
- [ ] Right panel: Pipeline builder (empty initially)
- [ ] Mode indicator shows: compose / simulate / refine / export
- [ ] `Tab` switches focus between panels
- [ ] Select component with arrow keys, `Enter` adds to pipeline
- [ ] `x` removes from pipeline
- [ ] `e` exports code (shows preview in notification)
- [ ] `Esc` returns to previous screen

---

### 5. Debugger (LOD 2)

From any screen, press `d`.

**Verify:**
- [ ] Opens DebuggerScreen
- [ ] Shows turn history (or empty state if no turns)
- [ ] `Esc` returns

---

### 6. Turn-gents CLI Commands

Exit the TUI and test CLI:

```bash
# Check turns (will be empty without running agents)
kg turns

# View turn DAG
kg dag

# List pending yields
kg pending

# Check flinch with turns panel
kg flinch --turns
```

---

## Issue Tracking

| Screen | Issue | Severity |
|--------|-------|----------|
| | | |

## Summary Template

After walkthrough, summarize:
1. **Working well**: [list features that work]
2. **Broken**: [list bugs found]
3. **Polish needed**: [list UX improvements]
4. **Missing**: [list expected features not present]
