# W-gent Wire Protocol

The wire protocol defines **how agents expose state** to W-gent for observation.

---

## Philosophy

> "The protocol is a handshake, not a handcuff."

W-gents adapt to what agents provide—there is **no mandatory format**. The wire protocol offers **conventions**, not requirements.

---

## Protocol Layers

### Layer 1: File System (Simplest)

Agent writes to conventional paths; W-gent watches.

#### Convention: `.wire/` Directory

```
.wire/
├── state.json      # Current state snapshot
├── stream.log      # Append-only event log
├── output/         # Generated artifacts
│   ├── draft.md
│   └── results.json
└── metrics.json    # Performance counters
```

#### state.json Schema

```json
{
  "agent_id": "robin",
  "phase": "active",          // Moon phase: dormant, waking, active, waning, empty
  "current_task": "Generating hypothesis v3",
  "progress": 0.67,           // 0.0 - 1.0
  "timestamp": "2025-12-08T14:32:05Z",
  "metadata": {
    "uptime_seconds": 4987,
    "memory_mb": 156
  }
}
```

**Optional fields**:
- `stage`: String describing current pipeline stage
- `error`: Error message if phase = "empty"
- `context`: Additional structured data

#### stream.log Format

Append-only text log with structured entries:

```
[2025-12-08T14:30:00Z] [INFO] [search] Querying PubMed for "protein folding"
[2025-12-08T14:30:05Z] [INFO] [parse] Found 15 relevant papers
[2025-12-08T14:30:10Z] [WARN] [filter] 2 papers missing abstracts
[2025-12-08T14:30:15Z] [INFO] [synthesize] Drafting hypothesis v3
```

**Format**: `[timestamp] [level] [stage] message`

**Levels**: `DEBUG`, `INFO`, `WARN`, `ERROR`

#### metrics.json Schema

```json
{
  "timestamp": "2025-12-08T14:32:05Z",
  "uptime_seconds": 4987,
  "memory_mb": 156,
  "api_calls": 42,
  "tokens_processed": 12450,
  "custom": {
    "hypotheses_generated": 8,
    "papers_analyzed": 15
  }
}
```

---

### Layer 2: IPC via Unix Socket (Intermediate)

Agent exposes Unix domain socket; W-gent connects and reads.

#### Convention: `/tmp/agent-{name}.sock`

```python
# Agent side (expose socket)
import socket
import json

sock_path = f"/tmp/agent-{agent_name}.sock"
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(sock_path)
server.listen(1)

while True:
    conn, _ = server.accept()
    state = get_current_state()
    conn.sendall(json.dumps(state).encode())
    conn.close()
```

```python
# W-gent side (read socket)
import socket
import json

sock_path = f"/tmp/agent-{agent_name}.sock"
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(sock_path)
data = client.recv(4096)
state = json.loads(data.decode())
```

**Advantages**:
- Lower latency than file watching
- No disk I/O
- Clean process isolation

**Disadvantages**:
- Unix-only (not Windows)
- Requires agent code changes

---

### Layer 3: HTTP API (Advanced)

Agent exposes localhost HTTP endpoint; W-gent polls.

#### Convention: `http://localhost:9000/state`

```python
# Agent side (FastAPI example)
from fastapi import FastAPI

app = FastAPI()

@app.get("/state")
def get_state():
    return {
        "agent_id": "robin",
        "phase": "active",
        "current_task": "Generating hypothesis v3",
        "progress": 0.67
    }

# Run on localhost:9000
uvicorn.run(app, host="127.0.0.1", port=9000)
```

```python
# W-gent side (polling)
import httpx

async def poll_agent_state(agent_name: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:9000/state")
        return response.json()
```

**Endpoints**:
- `GET /state` — Current state snapshot
- `GET /stream` — Event stream (Server-Sent Events)
- `GET /metrics` — Performance metrics

#### Server-Sent Events (SSE)

For real-time streaming:

```python
# Agent side
from fastapi.responses import StreamingResponse

@app.get("/stream")
async def stream_events():
    async def event_generator():
        while True:
            event = await get_next_event()
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

```javascript
// W-gent frontend (browser)
const eventSource = new EventSource('/stream');
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateUI(data);
};
```

---

### Layer 4: Standard Streams (Subprocess)

Agent runs as subprocess; W-gent captures `stdout`/`stderr`.

#### Convention: Structured Logging to stdout

```python
# Agent side (write structured logs)
import json
import sys

def log_event(level, stage, message):
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "stage": stage,
        "message": message
    }
    print(json.dumps(event), file=sys.stdout, flush=True)
```

```python
# W-gent side (capture subprocess)
import subprocess
import json

process = subprocess.Popen(
    ["python", "agent.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

for line in process.stdout:
    event = json.loads(line)
    process_event(event)
```

**Advantages**:
- No agent modifications (works with print statements)
- Natural for CLI tools
- Compatible with Docker/containerized agents

---

## Auto-Detection Strategy

W-gent tries protocols in order:

```python
def detect_protocol(agent_name: str) -> Protocol:
    # Try HTTP API
    if is_http_available(agent_name):
        return HTTPProtocol(agent_name)

    # Try Unix socket
    sock_path = f"/tmp/agent-{agent_name}.sock"
    if os.path.exists(sock_path):
        return SocketProtocol(sock_path)

    # Try .wire/ directory
    wire_dir = f".wire/{agent_name}/"
    if os.path.isdir(wire_dir):
        return FileProtocol(wire_dir)

    # Fallback: Subprocess stdout
    return SubprocessProtocol(agent_name)
```

---

## Minimal Compliance

**Minimum to be W-gent observable**:
- Write text to `stdout` OR
- Write to `.wire/stream.log`

That's it. Everything else is optional enhancement.

---

## Progressive Enhancement

Agents can add capabilities incrementally:

### Level 0: Basic Logging
```python
print("[INFO] Starting task")
print("[INFO] Task completed")
```
W-gent renders as **Teletype** (raw text).

### Level 1: Structured Logs
```python
log_event("INFO", "search", "Querying database")
log_event("INFO", "parse", "Found 15 results")
```
W-gent renders as **Teletype** with parsing.

### Level 2: State File
```python
with open(".wire/state.json", "w") as f:
    json.dump({"phase": "active", "progress": 0.5}, f)
```
W-gent can render **progress bars**.

### Level 3: Full API
```python
@app.get("/state")
def state():
    return full_state_object
```
W-gent renders as **Live Wire** dashboard.

---

## Security Considerations

### Localhost-Only Binding
Agents exposing HTTP APIs must bind to `127.0.0.1`:

```python
# ✓ Correct
uvicorn.run(app, host="127.0.0.1", port=9000)

# ✗ Dangerous (exposes to network)
uvicorn.run(app, host="0.0.0.0", port=9000)
```

### File Permissions
`.wire/` directory should have restricted permissions:

```bash
chmod 700 .wire/           # Owner-only access
```

### Socket Permissions
Unix sockets should be owner-only:

```python
import os
import stat

os.chmod(sock_path, stat.S_IRUSR | stat.S_IWUSR)  # 0600
```

### No Secrets in State
**Never expose**:
- API keys
- Credentials
- Personal data
- Internal URLs

Use placeholders:
```json
{
  "api_key": "sk-***hidden***",
  "database_url": "***redacted***"
}
```

---

## Reference Implementation

### Python Agent Mixin

```python
from pathlib import Path
import json
from datetime import datetime

class WireObservable:
    """Mixin to make agent W-gent observable."""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.wire_dir = Path(f".wire/{agent_name}")
        self.wire_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.wire_dir / "state.json"
        self.stream_file = self.wire_dir / "stream.log"

    def update_state(self, **kwargs):
        """Update state.json with new data."""
        state = {
            "agent_id": self.agent_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            **kwargs
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def log_event(self, level: str, stage: str, message: str):
        """Append to stream.log."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        entry = f"[{timestamp}] [{level}] [{stage}] {message}\n"
        with open(self.stream_file, "a") as f:
            f.write(entry)
```

### Usage Example

```python
class ResearchAgent(WireObservable):
    def __init__(self):
        super().__init__("robin")

    def run_hypothesis_generation(self):
        self.update_state(
            phase="active",
            current_task="Generating hypothesis",
            progress=0.0
        )

        self.log_event("INFO", "search", "Querying PubMed")
        papers = self.search_pubmed()

        self.update_state(progress=0.33)
        self.log_event("INFO", "parse", f"Found {len(papers)} papers")

        # ... continue work
```

---

## Versioning

### Protocol Version Header

All state files should include version:

```json
{
  "_protocol_version": "1.0",
  "agent_id": "robin",
  "phase": "active"
}
```

### Forward Compatibility

W-gent must:
- Ignore unknown fields
- Provide defaults for missing optional fields
- Warn on major version mismatch

---

## See Also

- [README.md](README.md) - W-gent overview
- [fidelity.md](fidelity.md) - How W-gent renders different data formats
- [integration.md](integration.md) - Ecosystem integration
- [../i-gents/export.md](../i-gents/export.md) - I-gent export format (complementary)
