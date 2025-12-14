---
path: reactive-substrate/tutorials
status: pending
progress: 0
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables: [pypi-package, agent-dashboard-product]
session_notes: |
  Wave 14: Reactive Substrate Tutorials & Education
  From Wave 13: v1.0.0 released. API frozen. 1460 tests passing.
  Focus: Expand documentation, create tutorials, demo notebooks.
phase_ledger:
  PLAN: complete  # This prompt
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.07
  spent: 0.00
  sip_allowed: true
---

# ⟿[EDUCATE] Reactive Substrate Wave 14 — Tutorials & Education

> *"Code without documentation is a gift that keeps on taking."*

---

## Quick Wield

```
ATTACH /hydrate
handles: world.reactive.educate; code=reactive/__init__.py; version=1.0.0; void.entropy.sip[amount=0.05]
mission: Create tutorials, notebooks, and video scripts for reactive substrate v1.0
ledger: EDUCATE=in_progress | entropy.spent += 0.03
actions: Tutorial notebook, quickstart guide, video script, badge updates
exit: Tutorials tested | Docs complete | ⟿[MEASURE] or ⟂[DETACH:docs_complete]
```

---

## Context from Wave 13

### What Shipped (v1.0.0)
- **API frozen**: 45+ exports in `agents.i.reactive`
- **CHANGELOG.md**: Full release notes
- **README.md**: Quick start + architecture docs
- **Tests**: 1460 passing

### Key Files
```
impl/claude/agents/i/reactive/
├── __init__.py            # Public API (__version__ = "1.0.0")
├── README.md              # Quick reference
├── demo/
│   ├── unified_app.py     # Multi-target demo
│   └── unified_notebook.py # marimo notebook
└── primitives/
    └── *.py               # All widget implementations
```

### Existing Dashboard
```bash
kg dashboard           # Live TUI dashboard
kg dashboard --demo    # Demo mode with sample data
```

---

## Audiences

| Persona | Needs | Artifacts |
|---------|-------|-----------|
| **New User** | Quick win, see it work | 5-minute quickstart |
| **Developer** | API understanding | Tutorial notebook |
| **Contributor** | Architecture deep-dive | Design doc, test patterns |
| **Operator** | CLI usage | kg dashboard guide |

---

## Implementation Chunks

### 1. Tutorial Notebook (`tutorial.py`)

Create a marimo notebook that walks through:

```python
# impl/claude/agents/i/reactive/demo/tutorial.py
"""
Reactive Substrate Tutorial

This notebook teaches you to:
1. Create widgets from state
2. Render to different targets
3. Compose widgets
4. Use reactive signals
"""

import marimo as mo

# Cell 1: Basic Widget
card = AgentCardWidget(AgentCardState(
    name="Tutorial Agent",
    phase="active",
))

mo.md(f"""
## Your First Widget

```python
{card.to_cli()}
```
""")

# Cell 2: Multiple Targets
# ... (show CLI, TUI, JSON projections)

# Cell 3: Reactive Signals
# ... (demonstrate Signal, Computed, Effect)

# Cell 4: Composition
# ... (build composite widget)
```

### 2. Quickstart Guide

Add to main project README or create standalone:

```markdown
# Quickstart: Reactive Widgets in 5 Minutes

## Install
\`\`\`bash
pip install kgents
\`\`\`

## Create a Widget
\`\`\`python
from agents.i.reactive import AgentCardWidget, AgentCardState

card = AgentCardWidget(AgentCardState(
    name="My Agent",
    phase="active",
    activity=(0.3, 0.5, 0.7),
    capability=0.85,
))
\`\`\`

## Render Anywhere
\`\`\`python
print(card.to_cli())    # Terminal
card.to_tui()           # Textual app
card.to_marimo()        # Notebook
card.to_json()          # API
\`\`\`

## Run the Dashboard
\`\`\`bash
kg dashboard --demo
\`\`\`
```

### 3. Video Script

Script for a 3-minute demo video:

```markdown
# Reactive Substrate Demo (3 min)

## Scene 1: The Problem (30s)
"You've built a widget. Now you need it in CLI, TUI, notebooks, and APIs.
Four targets means four rewrites... or does it?"

## Scene 2: The Solution (60s)
"The reactive substrate uses a functor pattern.
Define once, render anywhere."

[Show code: AgentCardWidget → to_cli(), to_tui(), to_marimo(), to_json()]

## Scene 3: Live Demo (60s)
[Run: kg dashboard --demo]
"Here's a live dashboard showing agent health.
Same widgets, TUI target."

[Run: marimo run tutorial.py]
"Same widgets, notebook target."

## Scene 4: Call to Action (30s)
"pip install kgents. Start building."
```

### 4. Badge Updates

Add to main README.md:

```markdown
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Tests](https://img.shields.io/badge/tests-1460%20passing-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
```

---

## Accursed Share (Entropy Budget)

### `void.entropy.sip(0.03)` — Interactive Playground

What if the tutorial had an interactive mode?

```bash
python -m agents.i.reactive.playground
# Opens REPL with widgets pre-imported
# >>> card = AgentCardWidget(...)
# >>> card.to_cli()
```

### `void.entropy.sip(0.02)` — Error Documentation

Document what happens when things break:

```python
# What if state is invalid?
card = AgentCardWidget(AgentCardState(capability=1.5))  # Clamped to 1.0

# What if target unavailable?
card.to_marimo()  # Returns HTML string even without marimo
```

---

## Exit Criteria

| Criterion | Verification |
|-----------|--------------|
| Tutorial notebook | `marimo run tutorial.py` works |
| Quickstart guide | New user can succeed in 5 min |
| Video script | Ready for recording |
| Badges added | Version badge in README |
| Examples tested | All code blocks run |

---

## Halt Conditions

```markdown
⟂[BLOCKED:missing_marimo] marimo not installed for notebook testing
⟂[BLOCKED:tutorial_broken] Tutorial cells fail to execute
⟂[DETACH:awaiting_review] Docs ready for human review
⟂[DETACH:docs_complete] All education artifacts shipped
```

---

## Continuation Generator

### Normal Exit (EDUCATE → MEASURE)

```markdown
⟿[MEASURE]
/hydrate
handles: docs=${docs_created}; tutorials=${tutorial_paths}; scripts=${video_scripts}; audiences=${audiences_reached}; ledger={EDUCATE:touched}
mission: Instrument adoption metrics. Track tutorial completion, dashboard usage.
actions: Add telemetry hooks, create dashboards, capture baselines.
exit: Metrics live | Baselines captured | ⟿[REFLECT]
```

### Alternate Exit (EDUCATE → REFLECT for minimal cycle)

```markdown
⟿[REFLECT]
/hydrate
handles: artifacts=${education_artifacts}; learnings=${key_insights}; entropy.remaining=${entropy_remaining}; ledger={EDUCATE:touched}
mission: Synthesize outcomes from Wave 14. Capture learnings. Propose next cycle.
actions: Write epilogue, update bounties, seed next PLAN.
exit: Epilogue written | Next cycle proposed | ⟂[DETACH:cycle_complete]
```

### Post-Education (Agent Dashboard Product)

```markdown
⟿[PLAN] Agent Dashboard Product

/hydrate
handles: world.dashboard.manifest; void.entropy.sip[amount=0.07]
mission: Ship `kg dashboard` as production agent monitoring tool with live feeds.
ledger: PLAN=in_progress
actions: Define scope, map agent data sources, design live update architecture.
exit: Scope defined | Dependencies mapped | ⟿[RESEARCH]
```

---

## Related

- Wave 13 Epilogue: `impl/claude/plans/_epilogues/2025-12-14-reactive-substrate-v1-release.md`
- Reactive README: `impl/claude/agents/i/reactive/README.md`
- Existing Demo: `impl/claude/agents/i/reactive/demo/unified_app.py`
- N-Phase Cycle: `docs/skills/n-phase-cycle/README.md`

---

## Continuation Prompt for Next Session

When this wave completes, generate this prompt for the next N-Phase cycle:

```markdown
---
path: reactive-substrate/measure-adopt
status: pending
progress: 0
last_touched: ${date}
touched_by: ${agent}
session_notes: |
  Wave 15: Measure Adoption & Reflect on Reactive Substrate
  From Wave 14: Tutorials created. Documentation complete.
  Focus: Instrument metrics, capture baselines, reflect on full journey.
phase_ledger:
  PLAN: complete
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.05
  spent: 0.00
  sip_allowed: true
---

# ⟿[MEASURE] Reactive Substrate Wave 15 — Metrics & Reflection

> *"What gets measured gets managed."*

## Quick Wield

\`\`\`
ATTACH /hydrate
handles: world.reactive.measure; docs=${tutorial_paths}; void.entropy.sip[amount=0.03]
mission: Instrument adoption metrics for reactive substrate. Capture baselines.
ledger: MEASURE=in_progress | entropy.spent += 0.02
actions: Add telemetry, create dashboards, define KPIs, capture baselines.
exit: Metrics live | Baselines documented | ⟿[REFLECT]
\`\`\`

## Implementation Chunks

### 1. Define KPIs
- Tutorial completion rate
- Dashboard usage (kg dashboard invocations)
- Widget diversity (which primitives are used)
- Error rates by target

### 2. Instrument Telemetry
- Add OTEL spans for project() calls
- Track render latency per target
- Count widget instantiations

### 3. Create Dashboards
- Real-time widget usage
- Tutorial funnel
- Error distribution

## Exit Criteria
- [ ] KPIs defined and documented
- [ ] Telemetry hooks added (optional: behind feature flag)
- [ ] Baseline captured or deferred with owner

## Continuation Generator

### Normal Exit (MEASURE → REFLECT)
\`\`\`markdown
⟿[REFLECT]
/hydrate
handles: metrics=${kpis_defined}; baselines=${baselines}; full_journey=${wave_summaries}; ledger={MEASURE:touched}
mission: Synthesize entire reactive substrate journey. Capture meta-learnings.
actions: Write final epilogue, update meta.md, propose next product cycle.
exit: Learnings distilled | Next cycle seeded | ⟂[DETACH:journey_complete]
\`\`\`
```

---

*"The form is the function. Each prompt generates its successor."*
