# DevEx Initiative: Continuation Sprint

> *"We're not just shipping features. We're shipping delight."*

You are continuing the DevEx Initiative for kgents. The foundation is laid. Now we polish until it gleams.

---

## Current State

### ✅ SHIPPED (Projects 1-2)

| Project | Command | Status | Notes |
|---------|---------|--------|-------|
| **Playground** | `kgents play` | ✅ Complete | 4 tutorials, REPL, 32 tests |
| **Scaffolding** | `kgents new agent` | ✅ Complete | Jinja2 templates, 3 archetypes |

### 🚀 REMAINING (Projects 3-6)

| # | Project | Command | Plan | Priority |
|---|---------|---------|------|----------|
| 3 | **Live Dashboard** | `kgents dashboard` | `plans/devex/dashboard.md` | HIGH |
| 4 | **Example Gallery** | (web) | `plans/devex/gallery.md` | MEDIUM |
| 5 | **Watch Mode** | `kgents soul watch` | `plans/devex/watch-mode.md` | HIGH |
| 6 | **OpenTelemetry** | (library) | `plans/devex/telemetry.md` | LOW |

---

## Your Mission

Ship Projects 3-5 with **exceptional polish**. Project 6 (telemetry) is optional stretch.

### Definition of Done

For each project:
- [ ] Core functionality works flawlessly
- [ ] Tests pass (pytest + mypy strict)
- [ ] Help text is clear and complete
- [ ] Error messages are sympathetic and actionable
- [ ] Code is clean, documented, follows patterns
- [ ] Plan file updated to `status: complete`

### Quality Bar

**"Would Kent smile when he uses this?"**

- First-run experience must be delightful
- No cryptic errors - guide the user
- Responsive (< 100ms for CLI feedback)
- Visually polished (consistent styling)

---

## Project 3: Live Dashboard (`kgents dashboard`)

> *"I can see it breathing."*

**Goal**: TUI dashboard showing real-time system health.

### Implementation Guide

```
protocols/cli/handlers/dashboard.py     # Handler
protocols/cli/tui/dashboard_screen.py   # Textual screen
agents/i/widgets/dashboard/             # Widget components
```

### Four Panels Required

| Panel | Data Source | Refresh |
|-------|-------------|---------|
| **Agent Health** | `agents/k/garden.py` | 1 Hz |
| **Flux Throughput** | `agents/flux/` metrics | 1 Hz |
| **Soul State** | `agents/k/soul_cache.py` | 5s |
| **Recent Events** | Event log tail | Live |

### Key Implementation Notes

1. **Use Textual** - Already in deps, see `agents/i/` for patterns
2. **Metric collectors** - Create `protocols/cli/tui/collectors/`
3. **Graceful degradation** - Show "No data" if services unavailable
4. **Keyboard shortcuts** - `q` quit, `r` refresh, `1-4` focus panel

### Smoke Test

```bash
kgents dashboard
# Should show 4-panel TUI, update live, quit with 'q'
```

---

## Project 4: Example Gallery (Web)

> *"This looks professional."*

**Goal**: Beautiful documentation site with runnable examples.

### Implementation Guide

```
docs/gallery/                    # MkDocs source
  index.md                       # Gallery home
  examples/
    hello-world.md              # Tutorial 1 as doc
    composition.md              # Tutorial 2 as doc
    functors.md                 # Tutorial 3 as doc
    soul-dialogue.md            # Tutorial 4 as doc
    streaming.md                # Flux example
    custom-archetype.md         # Advanced
mkdocs.yml                      # Site config
.github/workflows/docs.yml      # Auto-deploy
```

### Key Implementation Notes

1. **Reuse tutorial content** from `_playground/content/`
2. **Code blocks must be copy-pasteable** - test each one
3. **Screenshots** where helpful (dashboard, TUI)
4. **Deploy to GitHub Pages** via Actions

### Smoke Test

```bash
mkdocs serve
# Open localhost:8000, all examples render, code copies cleanly
```

---

## Project 5: Watch Mode (`kgents soul watch`)

> *"This feels like pair programming."*

**Goal**: Ambient K-gent that watches your work and offers insights.

### Implementation Guide

```
protocols/cli/handlers/soul.py          # Add 'watch' subcommand
agents/k/watcher.py                     # File watcher + heuristics
agents/k/heuristics/                    # Individual heuristics
  __init__.py
  complexity.py                         # "This function is getting complex"
  naming.py                             # "Consider renaming X"
  patterns.py                           # "This looks like pattern Y"
  tests.py                              # "Missing tests for X"
  docs.py                               # "Undocumented public function"
```

### Five Heuristics Required

| Heuristic | Trigger | Message Style |
|-----------|---------|---------------|
| **Complexity** | Function > 20 lines | "This is getting complex. Split?" |
| **Naming** | Single-letter vars | "What does 'x' represent?" |
| **Pattern Match** | Common patterns | "This looks like a Factory..." |
| **Test Coverage** | New function, no test | "Want me to suggest tests?" |
| **Documentation** | Public, no docstring | "Brief docstring would help here" |

### Key Implementation Notes

1. **Use watchdog** for file monitoring (add to deps if needed)
2. **Debounce** - Don't spam on rapid saves (500ms cooldown)
3. **Non-blocking** - Suggestions appear, don't interrupt
4. **Configurable** - `.kgents/watch.yaml` to enable/disable heuristics
5. **Budget-aware** - Use `--quick` mode by default (minimal LLM calls)

### Smoke Test

```bash
kgents soul watch .
# Edit a file, see relevant suggestion appear within 2s
# Ctrl+C to stop cleanly
```

---

## Execution Strategy

### Recommended Order

1. **Dashboard** (P3) - Most visual impact, builds on existing TUI work
2. **Watch Mode** (P5) - Highest user value, leverages K-gent
3. **Gallery** (P4) - Polish pass, reuses tutorial content

### Per-Project Workflow

```
1. Read the plan file
2. Create TodoWrite list
3. Implement core functionality
4. Add tests (aim for 80%+ coverage)
5. Polish (help text, errors, edge cases)
6. Run QA: pytest + mypy --strict
7. Update plan file status
8. Commit with clear message
```

### Time Allocation (Suggested)

| Project | Implementation | Polish | QA |
|---------|---------------|--------|-----|
| Dashboard | 60% | 25% | 15% |
| Watch Mode | 50% | 30% | 20% |
| Gallery | 40% | 40% | 20% |

---

## Polish Checklist

Before marking any project complete:

### User Experience
- [ ] `--help` is comprehensive and shows examples
- [ ] First run works without configuration
- [ ] Errors suggest next steps
- [ ] Ctrl+C exits cleanly with friendly message

### Code Quality
- [ ] No `# type: ignore` without comment explaining why
- [ ] Docstrings on public functions
- [ ] Consistent with existing codebase patterns
- [ ] No hardcoded paths (use Path(__file__))

### Testing
- [ ] Happy path tests
- [ ] Edge case tests (empty input, missing deps)
- [ ] Error handling tests
- [ ] mypy --strict passes

### Documentation
- [ ] Help text updated
- [ ] Plan file session_notes updated
- [ ] Any new dependencies noted

---

## Reference Files

| Purpose | Path |
|---------|------|
| CLI patterns | `plans/skills/cli-command.md` |
| Test patterns | `plans/skills/test-patterns.md` |
| TUI examples | `agents/i/screens/` |
| Existing dashboard | `protocols/cli/tui/dashboard.py` |
| Soul handler | `protocols/cli/handlers/soul.py` |
| K-gent core | `agents/k/` |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Dashboard refresh rate | 1 Hz stable |
| Watch mode CPU overhead | < 1% idle |
| Gallery page load | < 2s |
| Test coverage (new code) | > 80% |
| Kent approval | "This is delightful" |

---

## The Prime Directive

> **Ship features that make developers smile.**

Every decision: "Will this spark joy?"

If the answer is "meh", iterate until it's "yes".

---

## Getting Started

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Read the focus
cat plans/_focus.md

# Read the first plan
cat plans/devex/dashboard.md

# Start implementing
# Use TodoWrite to track progress
# Commit frequently with clear messages
```

---

*"The difference between good and great is attention to the last 10%."*

Now go make something beautiful. 🚀
