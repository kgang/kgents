# W-gent Integration with Ecosystem

W-gents compose with other kgents genera to provide observability.

---

## Integration with I-gents

W-gents are the **observation backend** for I-gents.

### The [observe] Action

When user clicks `[observe]` in I-gent Page view:

```
┌─ I-gent Page ──────────────────────────────────────┐
│ ╔══ robin ═════════════════════════════════════╗   │
│ ║ ● active                    t: 01:23:00      ║   │
│ ║ joy: █████████░ 9/10                         ║   │
│ ╚══════════════════════════════════════════════╝   │
│                                                    │
│ [observe] ← User clicks here                       │
└─────────────────────────────────────────────────────┘
```

**What happens**:

1. I-gent spawns W-gent subprocess:
   ```bash
   kgents wire attach robin --port 8000 --detach
   ```

2. W-gent starts HTTP server on localhost:8000

3. I-gent opens browser to `http://localhost:8000`

4. Browser displays W-gent visualization

5. W-gent runs until:
   - User stops observation (clicks `[stop]` in I-gent)
   - Agent stops/crashes
   - W-gent times out (configurable, default: 1 hour)

### State Synchronization

I-gent and W-gent share state via `.wire/` directory:

```
.wire/
└── robin/
    ├── state.json       ← Both read this
    ├── stream.log       ← W-gent writes, I-gent reads for margin notes
    └── i-gent.lock      ← Indicates I-gent is active
```

### Exporting to Margin Notes

W-gent can export observations back to I-gent:

**W-gent UI**:
```
┌─ live wire :: robin ──────────────────────────────┐
│ [export to I-gent notes] ← User clicks             │
└────────────────────────────────────────────────────┘
```

**Effect**: Appends to `.wire/robin/margin-notes.jsonl`:

```jsonl
{"time": "01:23:07", "source": "w-gent", "note": "robin synthesizing hypothesis v3 (67% complete)"}
{"time": "01:23:07", "source": "w-gent", "note": "Metrics: 42 API calls, 12,450 tokens processed"}
```

**I-gent** reads this file and displays in margin notes:

```
┌─ margin notes ────────────────────────────────────┐
│ 01:23:07 — [w-gent] robin synthesizing v3 (67%)   │
│ 01:23:07 — [w-gent] Metrics: 42 calls, 12.4k tok  │
└────────────────────────────────────────────────────┘
```

---

## Integration with J-gents (JIT)

W-gents visualize promise trees and JIT compilation.

### Use Case: Observing JIT Agent Compilation

J-gent compiles ephemeral sub-agent:

```python
# J-gent compiles specialized agent on demand
meta_architect.compile(intent="Parse Kubernetes logs")
```

**W-gent Dashboard**:

```
┌─ jit :: meta-architect ───────────────────────────┐
│                                                   │
│ ┌─ Promise Tree ─────────────────────────────┐   │
│ │                                            │   │
│ │   Root: "Fix crashing Pod X"              │   │
│ │     ├─ ✓ Child A: Fetch logs              │   │
│ │     ├─ ⏳ Child B: Analyze stack trace     │   │
│ │     │     └─ JIT compiling LogParser...   │   │
│ │     └─ ⏸ Child C: Apply remediation       │   │
│ │                                            │   │
│ └───────────────────────────────────────────┘   │
│                                                   │
│ ┌─ Entropy Budget ───────────────────────────┐   │
│ │ Depth: 2                                   │   │
│ │ Budget: 0.33 (33% freedom remaining)       │   │
│ │ ████░░░░░░░░░░░░                           │   │
│ └───────────────────────────────────────────┘   │
│                                                   │
│ ┌─ Chaosmonger Safety Check ─────────────────┐   │
│ │ ✓ Cyclomatic complexity: 8 (< 10)          │   │
│ │ ✓ Branching factor: 3 (< 5)                │   │
│ │ ✓ No unbounded recursion                   │   │
│ │ Verdict: SAFE to compile                   │   │
│ └───────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
```

### J-gent Wire Protocol

```json
{
  "promise_tree": {
    "root": "Fix crashing Pod X",
    "children": [
      {"id": "A", "status": "completed", "task": "Fetch logs"},
      {"id": "B", "status": "active", "task": "Analyze stack trace", "jit_compiling": "LogParser"},
      {"id": "C", "status": "pending", "task": "Apply remediation"}
    ]
  },
  "entropy_budget": {
    "depth": 2,
    "budget": 0.33,
    "threshold": 0.25
  },
  "chaosmonger": {
    "complexity": 8,
    "max_complexity": 10,
    "verdict": "SAFE"
  }
}
```

---

## Integration with T-gents (Testing)

W-gents visualize test execution and algebraic verification.

### Use Case: Observing Test Pipeline

Running test suite with observation:

```bash
pytest tests/ --kgents-observe
```

**W-gent Dashboard**:

```
┌─ test :: evolution_pipeline ─────────────────────┐
│                                                   │
│ ┌─ Test Results ─────────────────────────────┐   │
│ │ ✓ test_associativity       0.12s           │   │
│ │ ✓ test_identity            0.08s           │   │
│ │ ⏳ test_retry_recovery      ...             │   │
│ │ ⏸ test_convergence_detection               │   │
│ └───────────────────────────────────────────┘   │
│                                                   │
│ ┌─ Current Test: test_retry_recovery ────────┐   │
│ │ Testing RetryWrapper with FailingAgent     │   │
│ │                                            │   │
│ │ Attempt 1: FAIL (expected)                 │   │
│ │ Attempt 2: FAIL (expected)                 │   │
│ │ Attempt 3: ⏳ Running...                    │   │
│ └───────────────────────────────────────────┘   │
│                                                   │
│ ┌─ Commutative Diagram ──────────────────────┐   │
│ │   FailingAgent(fail=2) ──> Error           │   │
│ │         │                    ↑              │   │
│ │         ↓                    │              │   │
│ │   RetryWrapper(max=3) ────> Success        │   │
│ │                                            │   │
│ │ Verification: PENDING                      │   │
│ └───────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
```

---

## Integration with F-gents (Foundry)

W-gents monitor agent compilation through foundry process.

### Use Case: Compiling New Agent

```bash
kgents foundry forge --intent "Summarize papers for executives" --observe
```

**W-gent Dashboard**:

```
┌─ foundry :: summarizer ───────────────────────────┐
│                                                   │
│ ┌─ Foundry Process ──────────────────────────┐   │
│ │ ✓ 1. Understand (intent analysis)    2.1s  │   │
│ │ ✓ 2. Contract (interface synthesis)  1.8s  │   │
│ │ ⏳ 3. Prototype (code generation)     ...   │   │
│ │ ⏸ 4. Validate (test execution)             │   │
│ │ ⏸ 5. Crystallize (agent finalization)      │   │
│ └───────────────────────────────────────────┘   │
│                                                   │
│ ┌─ Generated Contract ───────────────────────┐   │
│ │ class SummarizerAgent(Agent[str, Summary]) │   │
│ │   """Summarize papers for executives."""  │   │
│ │                                            │   │
│ │   Input: str (paper text/PDF)              │   │
│ │   Output: Summary (title, findings, conf)  │   │
│ │                                            │   │
│ │   Guarantees:                              │   │
│ │   - Output < 500 words                     │   │
│ │   - No hallucinations                      │   │
│ └───────────────────────────────────────────┘   │
│                                                   │
│ ┌─ Code Generation ──────────────────────────┐   │
│ │ LLM: Generating implementation...          │   │
│ │ Progress: 73%                              │   │
│ │ ███████████████░░░░░                       │   │
│ └───────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
```

---

## Integration with D-gents (Data)

W-gents visualize state persistence and retrieval.

### Use Case: Observing State Snapshots

D-gent creating snapshots:

```
┌─ data :: state-manager ───────────────────────────┐
│                                                   │
│ ┌─ Snapshot History ─────────────────────────┐   │
│ │ ✓ v1.0.0  2025-12-08T12:00:00Z  (125 KB)   │   │
│ │ ✓ v1.0.1  2025-12-08T13:00:00Z  (126 KB)   │   │
│ │ ⏳ v1.0.2  Creating...                      │   │
│ └───────────────────────────────────────────┘   │
│                                                   │
│ ┌─ Current Snapshot ─────────────────────────┐   │
│ │ Version: v1.0.2                            │   │
│ │ Size: 127 KB (delta: +1 KB from v1.0.1)    │   │
│ │ Files: 12 changed, 3 added, 1 deleted      │   │
│ │                                            │   │
│ │ Compressing... 89%                         │   │
│ │ ██████████████████░░                       │   │
│ └───────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
```

---

## CLI Integration

W-gent integrates with kgents CLI:

### Automatic Attachment

```bash
# Any command with --observe flag spawns W-gent
kgents evolve preflight.py --observe
kgents forge --intent "..." --observe
kgents invoke robin --input data.json --observe
```

### Manual Attachment

```bash
# Attach to running agent
kgents wire attach robin

# Attach with custom port
kgents wire attach robin --port 8080

# Force fidelity level
kgents wire attach robin --mode live-wire

# Attach to subprocess (W-gent launches agent)
kgents wire exec python agent.py
```

### Listing Active W-gents

```bash
$ kgents wire list
Active W-gents:
- robin (PID 12345, localhost:8000, live-wire)
- preflight (PID 12346, localhost:8001, teletype)
```

### Detaching

```bash
# Stop specific W-gent
kgents wire detach robin

# Stop all W-gents
kgents wire detach --all
```

---

## Configuration

W-gent settings in `~/.kgents/config.toml`:

```toml
[wire]
default_port = 8000
default_fidelity = "auto"  # auto, teletype, documentarian, live-wire
auto_open_browser = true
localhost_only = true      # Security: never bind to 0.0.0.0
timeout_minutes = 60       # Auto-shutdown after inactivity

[wire.teletype]
color_scheme = "matrix"    # matrix, solarized, monokai

[wire.documentarian]
theme = "paper"            # paper, github, minimal

[wire.live-wire]
refresh_interval_ms = 1000
enable_metrics = true
```

---

## Security Considerations

### Localhost-Only Binding

W-gent **always** binds to `127.0.0.1` by default:

```python
# Enforced by default
uvicorn.run(app, host="127.0.0.1", port=8000)
```

To allow network access (for remote observation):

```bash
# Explicit opt-in required
kgents wire attach robin --host 0.0.0.0 --confirm-network-bind
```

User must confirm:
```
⚠ WARNING: Binding to 0.0.0.0 exposes agent state to network.
Continue? [y/N]: _
```

### No Authentication by Default

W-gent does not implement authentication (relies on localhost security).

For networked access, use SSH tunneling:

```bash
# On remote server
kgents wire attach robin --port 8000

# On local machine
ssh -L 8000:localhost:8000 user@remote-server

# Access via http://localhost:8000
```

### Data Redaction

W-gent respects redaction markers in wire protocol:

```json
{
  "api_key": "***redacted***",
  "database_url": "***redacted***"
}
```

---

## See Also

- [README.md](README.md) - W-gent overview
- [wire-protocol.md](wire-protocol.md) - How agents expose state
- [fidelity.md](fidelity.md) - Fidelity levels
- [../i-gents/](../i-gents/) - Ecosystem visualization (complementary)
- [../j-gents/](../j-gents/) - JIT agents (W-gent visualizes promise trees)
