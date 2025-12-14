---
path: plans/ideas/session-13-o-gents-observation
status: dormant
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

# Session 13: O-gents — Observation

> *"There is no view from nowhere. To observe is to participate."*

**Date**: 2025-12-12
**Focus**: O-gents (Systemic Proprioception)
**Ideas Generated**: 15+
**Priority Formula**: `(FUN × 2 + SHOWABLE × 2 + PRACTICAL) / (EFFORT × 1.5)` — shared across all sessions

---

## The O-gent Philosophy

O-gents are **Systemic Proprioception** — the system's ability to sense its own cognitive posture, like how your body knows where your limbs are without looking.

### The Three Dimensions of Observation

| Dimension | Name | Question | Layer |
|-----------|------|----------|-------|
| **X** | Telemetry | "Is it running?" | Body |
| **Y** | Semantics | "Does it mean what it says?" | Mind |
| **Z** | Axiology | "Is it worth the cost?" | Soul |

### Key Principles
1. **Observation doesn't mutate** (outputs unchanged)
2. **Observation doesn't block** (async, non-blocking)
3. **Observation doesn't leak** (data stays bounded)
4. **Observation enables** (self-knowledge enables improvement)

### The Heisenberg Constraint
Even observation costs energy (tokens). O-gents must be **Economically Self-Aware** via VoI (Value of Information) optimization.

---

## Priority Scoreboard

Formula: `PRIORITY = (FUN × 2 + SHOWABLE × 2 + PRACTICAL) / (EFFORT × 1.5)`

| Priority | Project | FUN | EFFORT | SHOW | PRAC | One-Liner |
|----------|---------|-----|--------|------|------|-----------|
| **9.3** | `kgents observe` | 8 | 2 | 10 | 8 | One-line health check |
| **9.0** | `kgents panopticon` | 9 | 3 | 10 | 7 | Live ASCII dashboard |
| **8.7** | `kgents drift` | 8 | 2 | 9 | 9 | "Are we on topic?" |
| **8.3** | `kgents roc` | 7 | 3 | 9 | 9 | Return on Compute |
| **8.0** | Bootstrap Witness CLI | 7 | 3 | 9 | 8 | "Do the laws hold?" |
| **8.0** | Borromean Knot Viz | 9 | 5 | 9 | 6 | Symbolic/Real/Imaginary rings |
| **7.7** | `kgents hallucinate?` | 8 | 4 | 8 | 8 | Grounding check |
| **7.3** | VoI Budget Viz | 7 | 5 | 8 | 7 | Observation economics |
| **7.3** | Dimension Dance TUI | 9 | 6 | 9 | 5 | Three-axis vital signs |
| **7.0** | Observer Functor REPL | 9 | 5 | 7 | 5 | Interactive O(f) = f |
| **7.0** | Topology Graph | 8 | 6 | 8 | 6 | Composition visualization |
| **6.7** | Psychosis Demo | 10 | 4 | 8 | 3 | Borromean knot failure |
| **6.3** | Entropy Weather | 10 | 4 | 9 | 3 | System entropy as weather |
| **6.3** | Observer Hierarchy Viz | 7 | 4 | 7 | 5 | "Who watches the watchers?" |
| **6.0** | Noether's Theorem Demo | 10 | 4 | 7 | 4 | Intent conservation |

---

## Quick Wins (Effort: LOW)

### 1. `kgents observe` — One-Line Health Check
**Priority: 9.3** | FUN: 8 | EFFORT: 2 | SHOWABLE: 10 | PRACTICAL: 8

```bash
$ kgents observe
[O] HOMEOSTATIC | T:230ms S:0.12✓ E:2.5x✓ B:✓ | Alerts:0
```

One command, instant system health. The compact status is already implemented in `render_compact_status()`. Just needs CLI exposure!

**Implementation**: Thin wrapper around `IntegratedPanopticon.render_compact_dashboard()`

**Vibe**: Like `htop` but for agent cognition.

---

### 2. `kgents panopticon` — ASCII Dashboard Stream
**Priority: 9.0** | FUN: 9 | EFFORT: 3 | SHOWABLE: 10 | PRACTICAL: 7

```bash
$ kgents panopticon --watch
# Full dashboard updates every second
# Ctrl+C to exit
```

The `stream_status()` method already exists! This would be a live-updating terminal dashboard.

**Implementation**: CLI wrapper around `IntegratedPanopticon.stream_status()` with `--watch` flag

**Vibe**: Like `top` but for agent souls.

---

### 3. `kgents drift` — "Are We Still On Topic?"
**Priority: 8.7** | FUN: 8 | EFFORT: 2 | SHOWABLE: 9 | PRACTICAL: 9

```bash
$ kgents drift "Build a REST API"
DRIFT SCORE: 0.23 (LOW)
✓ On topic: REST, API, endpoints
⚠ Wandered: Docker (mentioned 3x, not in prompt)
```

Uses `DriftDetector.measure_drift()`. Helps developers notice when their agent starts rambling about unrelated topics.

**Implementation**: CLI wrapper around `SemanticObserver.drift_detector`

**Vibe**: "Did I tell you about my stamp collection?"

---

### 4. `kgents roc` — Return on Compute
**Priority: 8.3** | FUN: 7 | EFFORT: 3 | SHOWABLE: 9 | PRACTICAL: 9

```bash
$ kgents roc
SYSTEM ROC: 2.5x (HEALTHY)
  TopPerformer: code-reviewer (4.2x)
  CashBurner: test-generator (0.3x) → UNDER AUDIT
```

Economic accountability in one command. Uses `AxiologicalObserver.get_health_report()`.

**Implementation**: CLI wrapper around `AxiologicalObserver`

**Vibe**: "Show me the receipts."

---

## Medium Wins (Effort: MEDIUM)

### 5. Borromean Knot Visualizer
**Priority: 8.0** | FUN: 9 | EFFORT: 5 | SHOWABLE: 9 | PRACTICAL: 6

Visualize the three registers (Symbolic/Real/Imaginary) as interlocked rings:

```
    Symbolic           Real           Imaginary
    ┌─────┐          ┌─────┐          ┌─────┐
    │ ✓   │◀───▶     │ ✓   │◀───▶     │ ✓   │
    └─────┘          └─────┘          └─────┘
              KNOT INTACT (ALL THREE HOLD)
```

When one ring breaks:
```
    Symbolic           Real           Imaginary
    ┌─────┐          ┌─────┐          ┌─────┐
    │ ✓   │     ✗    │ ✗   │     ✗    │ ✓   │
    └─────┘          └─────┘          └─────┘
              ⚠ PSYCHOSIS ALERT ⚠
              Real register broken: execution timeout
```

**Implementation**: TUI widget using `BorromeanObserver.knot_health()`

**Vibe**: Lacanian theory made visible.

---

### 6. `kgents hallucinate?` — Grounding Check
**Priority: 7.7** | FUN: 8 | EFFORT: 4 | SHOWABLE: 8 | PRACTICAL: 8

```bash
$ kgents hallucinate? "The API was created in 2019 by John Smith"
⚠ POTENTIAL HALLUCINATION (confidence: 0.6)
  - Invented year: 2019 (not in input)
  - Invented name: John Smith (not in input)
  - Confident assertion: "was created" without evidence
```

Uses `HallucinationDetector.check()`. Quick grounding validation.

**Implementation**: CLI wrapper around `HallucinationDetector`

**Vibe**: "Citation needed."

---

### 7. VoI Budget Visualizer
**Priority: 7.3** | FUN: 7 | EFFORT: 5 | SHOWABLE: 8 | PRACTICAL: 7

```
┌─ OBSERVATION BUDGET ─────────────────┐
│  ╔══════════════════════════════════╗│
│  ║███████████░░░░░░░░░░░░░░░░░ 35% ║│ code-analyzer
│  ╚══════════════════════════════════╝│
│  ╔══════════════════════════════════╗│
│  ║███████████████████████████░░ 90% ║│ test-runner
│  ╚══════════════════════════════════╝│
│  RoVI: 3.2x (Worth the observation!) │
└──────────────────────────────────────┘
```

Shows observation economics in real-time. Answer: "Is it worth observing this agent?"

**Implementation**: TUI widget using `VoIAwareObserver.get_stats()`

**Vibe**: "Observation has a cost. Make it count."

---

### 8. Bootstrap Witness CLI
**Priority: 8.0** | FUN: 7 | EFFORT: 3 | SHOWABLE: 9 | PRACTICAL: 8

```bash
$ kgents laws verify
┌─ BOOTSTRAP VERIFICATION ────────────────────┐
│ Kernel Integrity:  VERIFIED                 │
│ Identity Laws:     HOLD (5/5 cases)         │
│ Composition Laws:  HOLD (5/5 cases)         │
│ Agents: 7/7 conceptual, 2/7 importable      │
│ Streak: 42 consecutive passes               │
└─────────────────────────────────────────────┘
```

Already implemented via `verify_bootstrap()`. Just needs CLI wrapper.

**Implementation**: CLI wrapper around `BootstrapObserver.verify_and_record()`

**Vibe**: "The category laws hold. We're not dreaming."

---

## Fun Toys (Effort: VARIES)

### 9. The Observer Functor REPL
**Priority: 7.0** | FUN: 9 | EFFORT: 5 | SHOWABLE: 7 | PRACTICAL: 5

```python
>>> from agents.o import observe
>>> observed_agent = observe(my_agent)
>>> await observed_agent.invoke("Hello")
"Hello, World!"
# Behind the scenes: telemetry emitted, zero change to output
>>> observed_agent.inner  # Access wrapped agent
<MyAgent>
```

Interactive exploration of the Observer Functor. Prove that observation is truly invisible.

**Implementation**: Python REPL session with O-gent imports pre-loaded

**Vibe**: "Look ma, no side effects!"

---

### 10. "Psychosis Mode" Demonstration
**Priority: 6.7** | FUN: 10 | EFFORT: 4 | SHOWABLE: 8 | PRACTICAL: 3

A demo that deliberately breaks one Borromean ring and shows the cascade failure:

```bash
$ kgents demo psychosis
Starting healthy agent...
[O] HOMEOSTATIC | All rings intact

Injecting symbolic failure (schema violation)...
⚠ PSYCHOSIS ALERT: Symbolic register broken
  The Borromean knot has unknotted!
  When one ring fails, the whole structure collapses.

[Visual: ASCII art of the knot falling apart]
```

Educational tool showing why all three registers matter.

**Implementation**: Demo script using `BorromeanObserver` with custom validators

**Vibe**: Philosophy made tangible.

---

### 11. Entropy Events as Weather
**Priority: 6.3** | FUN: 10 | EFFORT: 4 | SHOWABLE: 9 | PRACTICAL: 3

Represent entropy events as weather patterns:

```
┌─ ENTROPY WEATHER ──────────────────────────┐
│                                             │
│    ☀️ Sunny (0 exceptions in last hour)    │
│    ⛅ Partly Cloudy (3 drift warnings)     │
│    🌧 Rainy (10+ entropy events)            │
│    ⛈ Stormy (CRITICAL alerts active)       │
│                                             │
│  Current: ⛅ Partly Cloudy                  │
│  "A few clouds (semantic drift), but calm." │
└─────────────────────────────────────────────┘
```

Fun way to visualize system entropy.

**Implementation**: Weather metaphor wrapper around `EntropyEvent` counts

**Vibe**: "How's the cognitive weather today?"

---

### 12. Topology Graph Visualization
**Priority: 7.0** | FUN: 8 | EFFORT: 6 | SHOWABLE: 8 | PRACTICAL: 6

The `TopologyMapper` tracks which agents compose with which. Visualize it:

```
┌─ COMPOSITION TOPOLOGY ─────────────────────────┐
│                                                 │
│    [reader] ──▶ [analyzer] ──▶ [writer]       │
│         │                         │            │
│         └──────▶ [validator] ◀────┘            │
│                     │                          │
│               [final_output]                   │
│                                                 │
│  Edges: 5  Nodes: 5  Hot Path: reader→writer  │
└─────────────────────────────────────────────────┘
```

**Implementation**: ASCII graph renderer using `TopologyMapper.get_topology()`

**Vibe**: "Who's talking to whom?"

---

### 13. "Noether's Theorem for Agents" Demo
**Priority: 6.0** | FUN: 10 | EFFORT: 4 | SHOWABLE: 7 | PRACTICAL: 4

The spec mentions: "In physics, Noether's theorem relates symmetries to conservation laws. In kgents, we conserve **Intent**."

Demo this concept:

```bash
$ kgents noether "Build a sorting algorithm"
Input Intent: Build a sorting algorithm
Output Meaning: Quicksort implementation with O(n log n) complexity

INTENT CONSERVATION: ✓ VERIFIED
  Symmetry: Task → Implementation
  Conserved Quantity: Sorting (present in both input and output)
  Drift: 0.08 (minimal)

"The symmetry of intent held. Noether would be proud."
```

**Implementation**: Wrapper around `DriftDetector` with physics-inspired framing

**Vibe**: Physics meets AI. Educational AND fun.

---

### 14. Observer Hierarchy Visualization
**Priority: 6.3** | FUN: 7 | EFFORT: 4 | SHOWABLE: 7 | PRACTICAL: 5

Show the observer stratification ("Who watches the watchers?"):

```
┌─ OBSERVER HIERARCHY ───────────────────────┐
│                                             │
│  Level 2: SYSTEM                           │
│    └─ IntegratedPanopticon                 │
│         (Self-unobserved)                  │
│                                             │
│  Level 1: DOMAIN                           │
│    └─ BootstrapObserver                    │
│    └─ SemanticObserver                     │
│    └─ AxiologicalObserver                  │
│                                             │
│  Level 0: CONCRETE                         │
│    └─ BootstrapWitness                     │
│    └─ DriftDetector                        │
│    └─ HallucinationDetector                │
│                                             │
│  "Observers may only observe lower levels"  │
└─────────────────────────────────────────────┘
```

**Implementation**: Tree renderer using `ObserverHierarchy`

**Vibe**: "The recursive problem solved elegantly."

---

### 15. "Dimension Dance" — Real-time Three-Axis Display
**Priority: 7.3** | FUN: 9 | EFFORT: 6 | SHOWABLE: 9 | PRACTICAL: 5

A TUI widget that shows all three dimensions simultaneously:

```
┌─ DIMENSION DANCE ────────────────────────────────────────────────┐
│                                                                   │
│  X (Body)          Y (Mind)          Z (Soul)                    │
│  ▂▃▄▅▆▇█▆▄▂       ▂▃▄▅▃▂▁▂▃▄       ▄▅▆▇▇▆▅▄▃▂                │
│  Latency: 230ms   Drift: 0.12      RoC: 2.5x                     │
│  Errors: 0.05%    Knots: 98.5%     GDP: $42.00                   │
│                                                                   │
│  Composite Health: ████████████████████░░░░░ 85%                 │
│  "All systems nominal. The system knows itself."                 │
└──────────────────────────────────────────────────────────────────┘
```

**Implementation**: Textual TUI widget with sparkline visualizations

**Vibe**: The system's vital signs, dancing.

---

## Jokes

**Q: Why did the O-gent fail the job interview?**
A: It kept observing the interviewer instead of answering questions.

**Q: What's the Panopticon's favorite song?**
A: "I Always Feel Like Somebody's Watching Me" (because it's watching everything)

**Q: Why is the Borromean Observer a therapist's dream client?**
A: It always knows exactly which of its three registers is broken.

**Q: What did the VoI-Aware Observer say to the expensive observation?**
A: "Is this information REALLY worth 2000 tokens?"

**Q: Why did the DriftDetector get lost?**
A: It wandered off-topic trying to explain itself.

**Q: What's the Observer Functor's motto?**
A: "I see everything, I change nothing."

**Q: Why did the HallucinationDetector become a fact-checker?**
A: It was tired of agents citing non-existent sources.

**Q: How does the BootstrapWitness meditate?**
A: Id >> Id >> Id >> Id... (identity law holds forever)

**Q: What's the System Status's favorite game?**
A: Traffic Light — HOMEOSTATIC, DEGRADED, CRITICAL!

---

## Crown Jewels

### 1. `kgents observe` (Priority: 9.3)
The simplest, most practical win. One command, instant system proprioception.

### 2. `kgents panopticon` (Priority: 9.0)
Live-streaming ASCII dashboard. Already implemented, just needs CLI exposure!

### 3. Borromean Knot Visualizer (Priority: 8.0)
Philosophy made visible. The three registers as interlocking rings.

---

## Implementation Notes

Most O-gent features are already implemented in `impl/claude/agents/o/`:
- `observer.py` — Core Observer Functor
- `panopticon.py` — Unified dashboard with `render_unified_dashboard()`
- `semantic.py` — DriftDetector, HallucinationDetector, BorromeanObserver
- `axiological.py` — RoC monitoring, economic health
- `telemetry.py` — Metrics collection, TopologyMapper
- `bootstrap_witness.py` — Category law verification
- `voi_observer.py` — Value of Information economics

The quickest wins are **CLI wrappers** around existing functionality.

---

## Related Files

- `impl/claude/agents/o/__init__.py` — Full O-gent exports
- `impl/claude/agents/o/panopticon.py` — Panopticon dashboard
- `impl/claude/agents/o/semantic.py` — Drift, hallucination, Borromean
- `impl/claude/agents/o/axiological.py` — Economic observation
- `impl/claude/agents/o/bootstrap_witness.py` — Law verification

---

*"To observe is to participate. There is no view from nowhere."*
