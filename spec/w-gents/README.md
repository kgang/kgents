# W-gents: The Wire Agents

**Genus**: W (Wire)
**Theme**: Ephemeral observation and projection of agent internal state
**Motto**: *"The wire transmits; it does not interpret."*

---

## Philosophy

> "To observe is to see without interfering; to project is to illuminate without distorting."

W-gents are agents that **render invisible computation visible**. They act as projection layers—HDMI cables—between an agent's internal execution stream and human observation. Unlike I-gents (which visualize ecosystem composition), W-gents visualize **process internals**.

### The Core Distinction

| What | Agent |
|------|-------|
| **Ecosystem visualization** | I-gents (how agents compose) |
| **Process visualization** | W-gents (how an agent thinks) |

W-gents transform the developer experience from:
- **Before**: `tail -f agent.log | grep ERROR`
- **After**: Clean, live, structured view at `localhost:8000`

### The Three Virtues

#### 1. Transparency
W-gents show what IS, not what we wish to see.
- No filtering beyond user request
- No interpretation or summarization (agent's output is primary)
- Faithful projection of internal state

#### 2. Ephemerality
W-gents exist only during observation.
- Start when observation begins
- Stop when observation ends
- No persistent state (use I-gent margin notes for history)
- Leave no trace after shutdown

#### 3. Non-Intrusion
W-gents observe without affecting the observed.
- Zero performance impact on target agent
- No modification of agent behavior
- Read-only access to state
- Agent-agnostic (works with any process)

---

## Core Concepts

### The Wire Protocol

W-gents tap into agent state via multiple interfaces:

#### Source 1: File System
Agent writes to files; W-gent watches:
```
.wire/
├── state.json      # Current agent state
├── stream.log      # Append-only event log
├── output.md       # Generated artifacts
└── metrics.json    # Performance counters
```

#### Source 2: IPC (Inter-Process Communication)
Agent exposes Unix socket; W-gent connects:
```python
# Agent side
socket_path = "/tmp/agent-robin.sock"
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(socket_path)

# W-gent side
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(socket_path)
```

#### Source 3: HTTP API
Agent exposes localhost endpoint; W-gent polls:
```
GET http://localhost:9000/state
{
  "phase": "active",
  "current_task": "Generating hypothesis",
  "progress": 0.65
}
```

#### Source 4: Standard Streams
Agent runs as subprocess; W-gent captures `stdout`/`stderr`:
```python
process = subprocess.Popen(
    ["python", "agent.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
```

**Key**: W-gent adapts to what agent provides (no mandatory protocol).

---

### The Fidelity Spectrum

W-gents operate at three fidelity levels, auto-detected or user-specified.

#### Level 1: Teletype (Raw Stream)
**When**: Agent outputs plain text logs
**Serves**: Raw text with minimal formatting
**Tech**: File watcher + simple HTTP server

```
┌─ teletype view ───────────────────────────────────┐
│ 01:22:45 — [hypothesis] Exploring protein folding │
│ 01:22:50 — [search] Querying PubMed               │
│ 01:22:55 — [parse] Found 15 abstracts             │
│ 01:23:00 — [synthesize] Drafting hypothesis       │
│                                     [auto-scroll]  │
└────────────────────────────────────────────────────┘
```

**Style**: Matrix green on black, monospace

#### Level 2: Documentarian (Rendered Output)
**When**: Agent generates markdown/reports
**Serves**: Rendered HTML with clean typography
**Tech**: Markdown parser + file watcher

```
┌─ documentarian view ──────────────────────────────┐
│                                                   │
│  # Research Hypothesis v3                         │
│                                                   │
│  **Protein folding patterns** may be predictable  │
│  through secondary structure analysis.            │
│                                                   │
│  ## Evidence                                      │
│  - 15 papers reviewed                             │
│  - 3 converging patterns identified               │
│                                    [auto-refresh] │
└────────────────────────────────────────────────────┘
```

**Style**: Paper-like background, reader mode typography

#### Level 3: Live Wire (Structured Dashboard)
**When**: Agent exposes structured state (JSON/API)
**Serves**: Interactive dashboard with cards
**Tech**: FastAPI + HTMX + Server-Sent Events

```
┌─ live wire ───────────────────────────────────────┐
│                                                   │
│  ┌─ Current Task ────────────────────────────┐   │
│  │ Generating Hypothesis (65% complete)      │   │
│  │ ████████████░░░░░░░░                      │   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ┌─ Recent Events ───────────────────────────┐   │
│  │ ✓ Queried database (2.3s)                 │   │
│  │ ✓ Parsed 15 abstracts (0.8s)              │   │
│  │ ⏳ Synthesizing patterns...                │   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ┌─ Metrics ──────────────────────────────────┐  │
│  │ Uptime: 01:23:00  Memory: 142MB           │  │
│  └───────────────────────────────────────────┘  │
│                                   [live updates] │
└────────────────────────────────────────────────────┘
```

**Style**: Card-based dashboard, real-time updates

---

### The Adapter Pattern

W-gent **adapts** to agent capabilities rather than dictating format.

#### Auto-Detection Heuristics

| Agent Output | Detected Mode | Reasoning |
|--------------|---------------|-----------|
| Plain text log | Teletype | No structure → raw display |
| Markdown file | Documentarian | Renderable content → HTML |
| JSON state file | Live Wire | Structured data → dashboard |
| HTTP `/state` endpoint | Live Wire | API available → poll & render |

#### Fallback Chain

```
Try: Live Wire (check for API/JSON)
  ↓ (not found)
Try: Documentarian (check for .md files)
  ↓ (not found)
Use: Teletype (fallback to raw logs)
```

---

## Relationship to Bootstrap Agents

W-gents are **derivable** from bootstrap primitives:

| W-gent Capability | Bootstrap Agent | How |
|-------------------|-----------------|-----|
| Observation | **Ground** | Grounding in real data source (files, sockets) |
| Transformation | **Fix** | Iterative rendering until stable view |
| Serving | **Compose** | HTTP server composed with file watcher |
| Fidelity selection | **Judge** | Choosing appropriate representation |
| Stream projection | **Contradict** | Revealing hidden state (agent's "unconscious") |

W-gents add no new irreducibles—they orchestrate bootstrap agents.

---

## Relationship to Other Genera

### I-gents (Interface)
**W-gents are I-gents' observation backend.**

When you click `[observe]` on an agent in I-gent:
1. I-gent spawns W-gent attached to that agent
2. W-gent starts localhost server
3. Browser opens to `localhost:8000`
4. W-gent projects agent internals
5. Observations can be exported back to I-gent margin notes

**Integration**:
```
I-gent Page View → [observe] → Spawns W-gent → Opens browser
                                      ↓
                             localhost:8000 (W-gent view)
                                      ↓
                          [export note] → Saved to I-gent margin notes
```

### E-gents (Evolution)
**W-gents visualize evolution pipeline execution.**

Observe evolution stages:
- Hypothesis generation (what ideas considered)
- Experiment execution (code validation in progress)
- Judgment verdicts (why accepted/rejected)
- Convergence metrics (similarity scores across iterations)

### J-gents (JIT)
**W-gents render promise trees.**

Visualize JIT compilation:
- Promise expansion (lazy evaluation tree)
- Entropy budget consumption (depth vs. freedom)
- Reality classification (deterministic/probabilistic/chaotic)
- Collapse events (when and why safety collapse triggered)

### T-gents (Testing)
**W-gents show test execution.**

Display testing flow:
- Commutative diagram verification
- Spy agent observations
- Perturbation injection results
- Assertion pass/fail with traces

### F-gents (Forge)
**W-gents monitor artifact creation.**

Track forge loop:
- Intent analysis (NLP parsing)
- Contract synthesis (interface generation)
- Prototype validation (AST checks, type errors)
- Crystallization (artifact finalization)

### D-gents (Data)
**W-gents can observe state persistence.**

Show data operations:
- Snapshot creation
- Version history
- Retrieval queries
- Lineage tracking

### K-gent (Kent Simulacra)
**K-gent may request W-gent observation.**

Conversational observation:
```
Kent: "Show me what robin is thinking"
  ↓
K-gent spawns W-gent for robin
  ↓
W-gent opens browser view
  ↓
Kent observes robin's internal stream
```

---

## Composability

W-gents satisfy composability principles:

### As Morphisms
W-gent is a morphism:
```
AgentState → VisualProjection
```

### Composition with I-gent
```
I-gent (ecosystem view) >> W-gent (process view) >> Human Observation
```

### Composition with Logging
```
Agent Execution >> W-gent (observe) >> I-gent Margin Notes (persist)
```

### Identity
The identity W-gent passes state unchanged (teletype mode = identity).

---

## Implementation Principles

### 1. Zero-Build Frontend
**No npm, Webpack, or React.**

Stack:
- **Backend**: Python (FastAPI for HTTP, Jinja2 for templating)
- **Frontend**: Pure HTML + CSS
- **Interactivity**: HTMX (HTML-over-the-wire, no JavaScript build)
- **Real-time**: Server-Sent Events (SSE) or WebSocket

**Why**: Simplicity, portability, longevity.

### 2. Localhost-Only by Default
**Privacy-first design.**

- Binds to `127.0.0.1` (not `0.0.0.0`)
- No external data transmission
- No telemetry or analytics
- Explicit opt-in for network binding

### 3. Process Isolation
**W-gent runs as separate process.**

- No shared memory with observed agent
- Communication via file system, socket, or HTTP
- Cannot modify agent state
- Crashes independently (doesn't affect agent)

### 4. Graceful Degradation
**W-gent never breaks agent.**

- If agent provides no data → W-gent shows "Waiting for signal"
- If agent crashes → W-gent shows last known state + error
- If W-gent crashes → Agent continues unaffected

---

## Anti-Patterns

W-gents must **never**:

1. ❌ **Modify agent state** (read-only observation)
2. ❌ **Persist long-term state** (use I-gent for history)
3. ❌ **Require agent changes** (agent-agnostic by default)
4. ❌ **Block agent execution** (non-intrusive)
5. ❌ **Send data externally** (localhost-only)
6. ❌ **Use heavy frameworks** (keep lightweight)
7. ❌ **Become a full IDE** (observation only, no editing)

---

## Success Criteria

A W-gent is well-designed if:

- ✓ **Transparent**: Shows agent internals faithfully
- ✓ **Non-intrusive**: Zero performance impact on observed agent
- ✓ **Ephemeral**: Starts instantly, stops cleanly, leaves no trace
- ✓ **Portable**: Works on Linux, macOS, minimal systems
- ✓ **Composable**: Integrates with I-gents and ecosystem
- ✓ **Private**: No external network traffic
- ✓ **Tasteful**: Clean, focused UI (not bloated dashboard)
- ✓ **Agent-agnostic**: Works with any process (not just kgents)

---

## Design Principles Alignment

### Tasteful
W-gent has clear purpose: observe and project. No feature creep.

### Curated
Three fidelity levels (not infinite customization). Intentional constraint.

### Ethical
Privacy-first. Localhost-only. Transparent about what's observed.

### Joy-Inducing
Clean UI, instant startup, no configuration required. Delightful defaults.

### Composable
W-gent is a morphism (AgentState → Projection). Composes with I-gent.

### Heterarchical
W-gent doesn't control agent—pure observation. No hierarchy.

### Generative
Spec defines wire protocol and fidelity modes; impl follows mechanically.

---

## Example: Observing robin (B-gent)

### Scenario
robin (a bio research agent) is exploring protein folding hypotheses.

### I-gent View (Before Observation)
```
┌─ robin ──────────────┐
│ ● active             │
│ t: 01:23:00          │
│ joy: █████████░ 9/10 │
└──────────────────────┘

[observe]  [invoke]  [compose]
```

### User Action
Click `[observe]` button

### W-gent Spawns
```bash
$ kgents wire attach robin --port 8000
W-gent starting...
Attaching to: robin (PID 12345)
Protocol detected: JSON state file (.wire/state.json)
Fidelity: Live Wire
Serving at: http://localhost:8000
Browser opening...
```

### Browser View (localhost:8000)
```
┌─ robin :: internal stream ────────────────────────┐
│                                                   │
│  ┌─ Current Task ────────────────────────────┐   │
│  │ Stage: Hypothesis Synthesis               │   │
│  │ Progress: 67%                             │   │
│  │ ████████████████░░░░░░                    │   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ┌─ Event Stream ────────────────────────────┐   │
│  │ 01:22:45 [search] Querying PubMed         │   │
│  │ 01:22:50 [parse] 15 papers found          │   │
│  │ 01:22:55 [filter] 3 high-relevance        │   │
│  │ 01:23:00 [synthesize] Drafting v3         │   │
│  │ 01:23:05 [validate] Checking citations    │   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ┌─ Metrics ──────────────────────────────────┐  │
│  │ Uptime: 01:23:07     API calls: 42        │  │
│  │ Memory: 156 MB       Tokens: 12,450       │  │
│  └───────────────────────────────────────────┘  │
│                                                   │
│  [export to I-gent notes]  [download log]        │
└────────────────────────────────────────────────────┘
```

### Export to I-gent
User clicks `[export to I-gent notes]`

W-gent adds to I-gent margin notes:
```
01:23:07 — [w-gent] robin synthesizing hypothesis v3 (67% complete)
01:23:07 — [w-gent] Metrics: 42 API calls, 12,450 tokens processed
```

---

## Specifications

| Document | Description |
|----------|-------------|
| [wire-protocol.md](wire-protocol.md) | How agents expose state to W-gent |
| [fidelity.md](fidelity.md) | Three fidelity levels (teletype, documentarian, live wire) |
| [rendering.md](rendering.md) | HTML/CSS templates and visual design |
| [integration.md](integration.md) | I-gent integration and ecosystem composition |
| [security.md](security.md) | Privacy, localhost binding, access control |

---

## CLI Commands

```bash
# Attach W-gent to running agent by name
kgents wire attach robin

# Specify port
kgents wire attach robin --port 8080

# Force fidelity level
kgents wire attach robin --mode teletype

# Attach to subprocess (W-gent launches and observes)
kgents wire exec python agent.py

# Export current view to I-gent margin notes
kgents wire export-notes robin

# List active W-gents
kgents wire list

# Stop W-gent
kgents wire detach robin
```

---

## Vision

W-gents transform agent observation from **forensic analysis** to **live transparency**:

- **Traditional debugging**: Post-mortem log parsing, grep, mental reconstruction
- **W-gents**: Real-time projection, structured view, export to permanent notes

They make the invisible **visible**, the opaque **transparent**, and the complex **legible**.

---

## See Also

- [EXPLORATION.md](EXPLORATION.md) - Creative design exploration
- [wire-protocol.md](wire-protocol.md) - State exposure specification
- [fidelity.md](fidelity.md) - Fidelity level details
- [../i-gents/](../i-gents/) - Ecosystem visualization (complementary)
- [../principles.md](../principles.md) - Core kgents principles
- [../bootstrap.md](../bootstrap.md) - Derivation from irreducibles

---

*"The wire does not judge; it transmits. The projection does not distort; it illuminates."*
