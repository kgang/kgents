# W-gents: Creative Exploration

**Date**: 2025-12-08
**Status**: Pre-specification exploration

---

## The Core Insight

I-gents render the **ecosystem** (how agents compose).
W-gents render the **process** (how an individual agent thinks).

### The Distinction

| Aspect | I-gents | W-gents |
|--------|---------|---------|
| **Scope** | Ecosystem-wide | Single-agent/process |
| **Aesthetic** | Archival, permanent, contemplative | Ephemeral, dynamic, instrumental |
| **Metaphor** | Zen garden / Library | Wire / Oscilloscope / Debug console |
| **Granularity** | Agent relationships & composition | Internal state & execution flow |
| **Persistence** | Markdown-first, paper-exportable | Transient, served over localhost |
| **Primary User** | Garden tender (orchestrator) | Debugger/developer (investigator) |

---

## The Metaphor: "The Wire"

W-gents act as **projection cables** between an agent's internal state and human observation.

```
┌─────────────────────┐
│   Working Agent     │ (thinking, processing)
│   (black box)       │
└──────────┬──────────┘
           │
           │ ← W-gent "taps" the stream
           ↓
    ┌──────────────┐
    │   W-gent     │ (wire/transformer)
    │  (observer)  │
    └──────┬───────┘
           │
           ↓
    ┌──────────────┐
    │  localhost   │ (browser/terminal view)
    │   :8000      │
    └──────────────┘
```

**Key**: W-gent does not control—it **observes and projects**.

---

## The Fidelity Spectrum

W-gents operate on a spectrum from minimal (raw text) to maximal (reactive UI).

### Mode 1: Teletype (Lowest Fidelity)
**Use case**: Debugging raw logic loops, simple execution traces

**Mechanism**:
- Append-only `.txt` log file
- Simple file watcher
- HTML page with auto-refresh/tail

**Visual**:
```
Matrix green text on black
Monospace, no formatting
Just the raw stream
```

**Tech**: Python watchdog + simple HTTP server

---

### Mode 2: Documentarian (Medium Fidelity)
**Use case**: Report generation, LLM reasoning traces, artifact summaries

**Mechanism**:
- Watch for `.md` changes
- On save → render to HTML or PDF
- Clean "reader mode" styling

**Visual**:
```
Clean typography
Paper-like background
Progressive disclosure (paragraphs appear as written)
```

**Tech**: Markdown → HTML (via markdown-it or similar), file watcher

---

### Mode 3: Live Wire (High Fidelity)
**Use case**: Complex orchestration, multi-step reasoning, interactive debugging

**Mechanism**:
- FastAPI + Jinja2 + HTMX
- Agent writes structured data to shared state
- W-gent serves dynamic HTML fragments
- HTMX swaps DOM elements without full reload

**Visual**:
```
Dashboard with cards
Each card = task/step
Visual state indicators
Timeline/progress bars
```

**Tech**: FastAPI, HTMX (no build step), Server-Sent Events (SSE) for real-time updates

---

## The Universal Adapter Pattern

W-gent doesn't dictate how agents communicate—it **adapts to what they provide**.

### Input Sources (What W-gent Can Observe)

1. **File System**:
   - Log files (`.log`, `.txt`)
   - Markdown documents (`.md`)
   - JSON state files (`.json`)
   - Structured output directories

2. **IPC (Inter-Process Communication)**:
   - Unix socket
   - Named pipes
   - Shared memory

3. **Network**:
   - Localhost TCP socket
   - HTTP API endpoint (agent exposes `/status`)
   - WebSocket stream

4. **Standard Streams**:
   - `stdout` / `stderr` from subprocess
   - Structured logging output

### Output Formats (What W-gent Can Serve)

1. **Terminal**: Plain text output (for SSH/tmux)
2. **Browser**: HTML (static or dynamic)
3. **Paper**: PDF export (via Weasyprint or similar)
4. **API**: JSON endpoint for programmatic access

---

## Relationship to I-gents

W-gents and I-gents are **complementary**, not competitive.

### I-gents Uses W-gents

When you "observe" an agent in I-gents:
```
[observe] button in I-gent Page view
    ↓
Spawns W-gent attached to that agent
    ↓
Opens browser to localhost:8000
    ↓
Shows internal execution stream
```

### Example: Observing robin (B-gent)

**I-gent view** (ecosystem level):
```
┌─ robin ──────────────┐
│ ● active             │
│ t: 01:23:00          │
│ joy: █████████░ 9/10 │
└──────────────────────┘
```

Click `[observe]` → Spawns W-gent

**W-gent view** (process level):
```
┌─ robin internal stream ──────────────────────────┐
│ 01:22:45 — [hypothesis] Exploring protein folding
│ 01:22:50 — [search] Querying PubMed for papers
│ 01:22:55 — [parse] Found 15 relevant abstracts
│ 01:23:00 — [synthesize] Drafting hypothesis...
│ 01:23:00 — [active] Writing hypothesis to file
│                                       [streaming]
└───────────────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. Agent-Agnostic
W-gents work with **any agent**, not just kgents.
- Can observe Python scripts
- Can observe CLI tools
- Can observe LLM API calls
- Universal via shared interface (files, sockets, etc.)

### 2. Zero-Build Frontend
No npm, no Webpack, no React.
- Pure HTML + CSS
- HTMX for interactivity (HTML-over-the-wire)
- Jinja2 templates (server-side rendering)
- Minimal JavaScript (if any)

**Why**: Simplicity, portability, longevity

### 3. Ephemeral by Design
W-gents are **not persistent**.
- Start when observation begins
- Stop when observation ends
- No database, no state accumulation
- If you need history → export to I-gent margin notes

### 4. Privacy-First
W-gents **never send data externally**.
- Localhost-only by default
- No telemetry, no analytics
- Explicit user consent for network binding
- Data is transient (not stored)

---

## Anti-Patterns to Avoid

### ❌ Don't Make W-gent a Full IDE
W-gent is **not** a code editor, debugger, or execution environment.
- No code editing
- No breakpoints
- No REPL
- Just observation

### ❌ Don't Make W-gent Stateful
W-gent should not maintain long-term state.
- No database
- No "save session" (export to I-gent instead)
- No user accounts or persistence

### ❌ Don't Add Heavy Dependencies
Keep W-gent lightweight.
- No React, Vue, Angular
- No heavy Python libraries
- Should work on minimal systems

### ❌ Don't Couple to Kgents
W-gent should be **generic**.
- Works with non-kgents processes
- Doesn't assume kgents structure
- Adapts to what it finds

---

## The Name: "Wire"

**W** = Wire, Watch, Window, Weave

The metaphor stack:
1. **Wire**: HDMI cable, transmits signal without modification
2. **Watch**: Observes without intervening
3. **Window**: Provides view into otherwise invisible process
4. **Weave**: Transforms raw data into structured visualization

All fit the W-gent philosophy.

---

## Composability with Other Gents

### With J-gents (JIT)
W-gent can render promise trees:
- Visualize lazy promise expansion
- Show entropy budget consumption
- Track reality classification
- Display collapse events

### With T-gents (Testing)
W-gent can observe test execution:
- Show test pipeline progress
- Display assertion results
- Render failure traces
- Track commutative diagram verification

### With F-gents (Foundry)
W-gent can monitor agent compilation:
- Visualize foundry process stages
- Show contract synthesis
- Display validation results
- Render artifact lineage

---

## The Bootstrap Question

**Is W-gent derivable from bootstrap agents?**

| W-gent Capability | Bootstrap Derivation |
|-------------------|---------------------|
| Observation (tapping stream) | **Ground** (grounding in real data source) |
| Transformation (data → HTML) | **Fix** (iterative rendering) |
| Serving (localhost) | **Compose** (HTTP server composed with watcher) |
| Fidelity selection | **Judge** (choosing appropriate format) |

**Answer**: Yes, W-gents are bootstrap-derivable. They add no new irreducibles.

---

## Success Criteria

A W-gent is well-designed if:

- ✓ **Transparent**: Shows agent internals without distortion
- ✓ **Non-intrusive**: Zero performance impact on observed agent
- ✓ **Ephemeral**: Starts quickly, stops cleanly, leaves no trace
- ✓ **Portable**: Works on Linux, macOS, minimal systems
- ✓ **Composable**: Integrates with I-gents and other ecosystem tools
- ✓ **Private**: No external data transmission
- ✓ **Tasteful**: Clean, focused UI (not feature-bloated dashboard)

---

## Refined Vision

W-gents transform agent observation from **log parsing** to **live projection**:

**Traditional debugging**:
- `tail -f agent.log`
- Parse JSON manually
- Grep for errors
- Context lost in walls of text

**W-gents**:
- `kgents wire attach robin`
- Browser opens to `localhost:8000`
- Structured, live view of agent thinking
- Contextual, visual, immediate

---

## Next Steps

1. **Refine I-gent spec** to clarify `[observe]` action → W-gent integration
2. **Write W-gent spec** following kgents patterns
3. **Prototype Mode 1** (Teletype) as proof-of-concept
4. **Define wire protocol** (how agents expose state to W-gent)

---

## Open Questions

1. **Wire Protocol**: Should we standardize how agents expose state?
   - Option A: File convention (`.wire/state.json`)
   - Option B: Localhost HTTP endpoint (`:9000/state`)
   - Option C: Unix socket (`.wire.sock`)

2. **Fidelity Auto-Detection**: How does W-gent choose mode?
   - Based on data structure (text → teletype, JSON → live wire)?
   - User configuration?
   - Agent declaration?

3. **Multi-Agent Wire**: Can one W-gent observe multiple agents?
   - Probably not (violates single-responsibility)
   - Multiple W-gents can run concurrently (different ports)

4. **Security**: How to prevent unauthorized access to localhost:8000?
   - Token-based auth?
   - Firewall defaults?
   - Just document best practices?

---

*This exploration document will inform the formal W-gent specification.*
