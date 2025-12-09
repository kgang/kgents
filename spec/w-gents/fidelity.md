# W-gent Fidelity Levels

W-gents render agent state at three fidelity levels, chosen automatically or manually.

---

## The Fidelity Spectrum

```
Teletype ────────── Documentarian ────────── Live Wire
  │                      │                       │
  │                      │                       │
Raw text           Rendered docs          Interactive UI
Lowest CPU         Medium CPU              Higher CPU
Zero config        Minimal config          Auto-detected
Works always       Works with .md          Needs structured data
```

---

## Level 1: Teletype

### When Used

- Agent outputs **plain text logs**
- No structured data available
- Minimal resource usage required
- Fallback mode (always works)

### Visual Style

**Aesthetic**: Matrix terminal (green on black, monospace)

```
╔══ teletype :: robin ═══════════════════════════════╗
║                                                    ║
║  01:22:45 [INFO] [search] Querying PubMed          ║
║  01:22:50 [INFO] [parse] Found 15 papers           ║
║  01:22:55 [WARN] [filter] 2 missing abstracts      ║
║  01:23:00 [INFO] [synthesize] Drafting hypothesis  ║
║  01:23:05 [INFO] [validate] Checking citations     ║
║  _                                                  ║
║                                     [auto-scroll ✓] ║
║  localhost:8000                     [copy log]      ║
╚════════════════════════════════════════════════════╝
```

### Features

- **Auto-scroll**: Follows latest output
- **Search**: `/` to search within output
- **Copy**: Select and copy text
- **Timestamp highlighting**: Different colors for log levels

### HTML Template

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background: #000;
            color: #0f0;
            font-family: 'Courier New', monospace;
            padding: 20px;
        }
        .log-line {
            margin: 2px 0;
        }
        .level-INFO { color: #0f0; }
        .level-WARN { color: #ff0; }
        .level-ERROR { color: #f00; }
        .timestamp { color: #0a0; }
    </style>
</head>
<body>
    <div id="log-output">
        <!-- Lines appended here via SSE -->
    </div>
    <script>
        const eventSource = new EventSource('/stream');
        eventSource.onmessage = (e) => {
            const line = document.createElement('div');
            line.className = 'log-line';
            line.textContent = e.data;
            document.getElementById('log-output').appendChild(line);
            window.scrollTo(0, document.body.scrollHeight);
        };
    </script>
</body>
</html>
```

### Backend (FastAPI)

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/")
async def root():
    with open("templates/teletype.html") as f:
        return HTMLResponse(f.read())

@app.get("/stream")
async def stream_logs():
    async def log_generator():
        with open(".wire/robin/stream.log") as f:
            # Tail -f behavior
            f.seek(0, 2)  # Go to end
            while True:
                line = f.readline()
                if line:
                    yield f"data: {line}\n\n"
                await asyncio.sleep(0.1)

    return StreamingResponse(log_generator(), media_type="text/event-stream")
```

---

## Level 2: Documentarian

### When Used

- Agent outputs **markdown files**
- Content is rendered artifacts (reports, essays, code)
- Medium resource usage acceptable
- Agent generates readable content

### Visual Style

**Aesthetic**: Reader mode (paper background, clean typography)

```
┌─ documentarian :: robin ──────────────────────────┐
│                                                   │
│  ╔══════════════════════════════════════════════╗ │
│  ║                                              ║ │
│  ║  # Research Hypothesis v3                   ║ │
│  ║                                              ║ │
│  ║  ## Abstract                                 ║ │
│  ║  Protein folding patterns may be            ║ │
│  ║  predictable through secondary structure    ║ │
│  ║  analysis of conserved domains.             ║ │
│  ║                                              ║ │
│  ║  ## Evidence Base                           ║ │
│  ║  - 15 papers reviewed                       ║ │
│  ║  - 3 converging patterns identified         ║ │
│  ║  - High confidence in alpha-helix stability ║ │
│  ║                                              ║ │
│  ╚══════════════════════════════════════════════╝ │
│                                                   │
│  Last updated: 01:23:05            [auto-refresh] │
│  localhost:8000                    [export PDF]   │
└────────────────────────────────────────────────────┘
```

### Features

- **Markdown rendering**: Full GFM support
- **Syntax highlighting**: Code blocks with Pygments
- **Live reload**: Auto-refresh on file change
- **PDF export**: Print-friendly format
- **Math rendering**: LaTeX via KaTeX (optional)

### HTML Template

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background: #fdfbf7;
            color: #1a1918;
            font-family: 'Georgia', serif;
            line-height: 1.6;
        }
        h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; }
        code {
            background: #f5f2f0;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre {
            background: #f5f2f0;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
    <div id="content"></div>
    <script>
        async function refresh() {
            const response = await fetch('/markdown');
            const markdown = await response.text();
            document.getElementById('content').innerHTML = marked.parse(markdown);
        }

        refresh();
        setInterval(refresh, 1000);  // Refresh every second
    </script>
</body>
</html>
```

### Backend (FastAPI)

```python
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/")
async def root():
    with open("templates/documentarian.html") as f:
        return HTMLResponse(f.read())

@app.get("/markdown")
async def get_markdown():
    markdown_file = ".wire/robin/output/hypothesis.md"
    with open(markdown_file) as f:
        return PlainTextResponse(f.read())
```

---

## Level 3: Live Wire

### When Used

- Agent exposes **structured state** (JSON, API)
- Real-time updates needed
- Interactive observation desired
- Agent has distinct stages/tasks

### Visual Style

**Aesthetic**: Card-based dashboard (clean, functional)

```
┌─ live wire :: robin ──────────────────────────────┐
│                                                   │
│  ┌─ Current Task ────────────────────────────┐   │
│  │ Stage: Hypothesis Synthesis               │   │
│  │ Progress: 67%                             │   │
│  │ ████████████████░░░░░░░░                  │   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ┌─ Event Stream ────────────────────────────┐   │
│  │ ✓ 01:22:45 Queried PubMed (2.1s)          │   │
│  │ ✓ 01:22:50 Parsed 15 abstracts (0.8s)     │   │
│  │ ✓ 01:22:55 Filtered high-relevance (0.2s) │   │
│  │ ⏳ 01:23:00 Synthesizing patterns...       │   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ┌─ Metrics ──────────────────────────────────┐  │
│  │ Uptime: 01:23:07     Memory: 156 MB       │  │
│  │ API calls: 42        Tokens: 12,450       │  │
│  └───────────────────────────────────────────┘  │
│                                                   │
│  localhost:8000          [export] [pause stream] │
└────────────────────────────────────────────────────┘
```

### Features

- **Real-time updates**: SSE or WebSocket
- **Progress bars**: Visual task completion
- **Status badges**: ✓ (done), ⏳ (active), ⏸ (paused), ✗ (error)
- **Interactive controls**: Pause/resume stream
- **Export**: Save snapshot to I-gent notes

### HTML Template (with HTMX)

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 900px;
            margin: 20px auto;
            background: #f8f9fa;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .progress-bar {
            background: #e9ecef;
            border-radius: 4px;
            height: 24px;
            overflow: hidden;
        }
        .progress-fill {
            background: #0d6efd;
            height: 100%;
            transition: width 0.3s ease;
        }
        .event { padding: 8px 0; border-bottom: 1px solid #e9ecef; }
        .event:last-child { border-bottom: none; }
        .status-done { color: #28a745; }
        .status-active { color: #ffc107; }
        .status-error { color: #dc3545; }
    </style>
</head>
<body>
    <h1>robin :: live wire</h1>

    <div class="card" hx-get="/state" hx-trigger="every 1s" hx-swap="innerHTML">
        <!-- State updated via HTMX -->
    </div>

    <div class="card">
        <h3>Event Stream</h3>
        <div id="events" hx-get="/events" hx-trigger="every 1s" hx-swap="beforeend">
            <!-- Events appended here -->
        </div>
    </div>

    <div class="card">
        <h3>Metrics</h3>
        <div hx-get="/metrics" hx-trigger="every 2s" hx-swap="innerHTML">
            <!-- Metrics updated here -->
        </div>
    </div>
</body>
</html>
```

### Backend (FastAPI + HTMX)

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

@app.get("/state")
async def get_state():
    with open(".wire/robin/state.json") as f:
        state = json.load(f)

    progress_pct = int(state['progress'] * 100)

    return HTMLResponse(f"""
        <h3>Current Task</h3>
        <p>{state['current_task']}</p>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress_pct}%"></div>
        </div>
        <p>{progress_pct}% complete</p>
    """)

@app.get("/events")
async def get_events():
    # Read last N lines from stream.log
    events = read_recent_events(n=5)

    html = ""
    for event in events:
        status_class = "status-done" if "✓" in event else "status-active"
        html += f'<div class="event {status_class}">{event}</div>'

    return HTMLResponse(html)

@app.get("/metrics")
async def get_metrics():
    with open(".wire/robin/metrics.json") as f:
        metrics = json.load(f)

    return HTMLResponse(f"""
        <p>Uptime: {format_uptime(metrics['uptime_seconds'])}</p>
        <p>Memory: {metrics['memory_mb']} MB</p>
        <p>API calls: {metrics['api_calls']}</p>
        <p>Tokens: {metrics['tokens_processed']:,}</p>
    """)
```

---

## Fidelity Auto-Detection

```python
def detect_fidelity(agent_name: str) -> FidelityLevel:
    wire_dir = Path(f".wire/{agent_name}")

    # Check for structured state (Live Wire)
    state_file = wire_dir / "state.json"
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
            if "progress" in state or "current_task" in state:
                return FidelityLevel.LIVE_WIRE

    # Check for markdown output (Documentarian)
    output_dir = wire_dir / "output"
    if output_dir.exists():
        md_files = list(output_dir.glob("*.md"))
        if md_files:
            return FidelityLevel.DOCUMENTARIAN

    # Fallback to raw logs (Teletype)
    return FidelityLevel.TELETYPE
```

---

## Manual Override

User can force fidelity level:

```bash
# Force teletype (even if structured data available)
kgents wire attach robin --mode teletype

# Force live wire (will error if no structured data)
kgents wire attach robin --mode live-wire
```

---

## Performance Considerations

| Fidelity | CPU Usage | Memory | Latency | Browser Load |
|----------|-----------|--------|---------|--------------|
| Teletype | ~1% | ~10 MB | <10ms | Minimal |
| Documentarian | ~3% | ~20 MB | ~50ms | Low |
| Live Wire | ~5% | ~50 MB | ~100ms | Medium |

**Note**: Impact on **observed agent** is negligible (file I/O is async).

---

## See Also

- [README.md](README.md) - W-gent overview
- [wire-protocol.md](wire-protocol.md) - How agents expose state
- [rendering.md](rendering.md) - Visual design details
- [integration.md](integration.md) - I-gent integration
