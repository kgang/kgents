# K8-gents Interface: The Developer Surface

> *"The best debugger is a glass wall. The best interface is the one that disappears."*

Three layers for observing and interacting with the agent ecosystem.

---

## The Three Layers

```
┌─────────────────────────────────────────────────────────────┐
│                 LAYER 3: MCP (Live)                          │
│   Claude Code queries live state via MCP resources          │
│   kgents://agents, kgents://pheromones/*                    │
└─────────────────────────────────────────────────────────────┘
                          ▲ Real-time
┌─────────────────────────────────────────────────────────────┐
│                 LAYER 2: Terrarium TUI                       │
│   Glass box visualization: kgents observe                   │
│   Bidirectional debugging: kgents tether                    │
└─────────────────────────────────────────────────────────────┘
                          ▲ Streaming
┌─────────────────────────────────────────────────────────────┐
│                 LAYER 1: Ghost (File Cache)                  │
│   Filesystem projection: .kgents/ghost/                     │
│   Works offline, with grep, git, any tool                   │
└─────────────────────────────────────────────────────────────┘
```

**Why not FUSE?** FUSE is fragile on macOS. Ghost + MCP achieves the same goals without kernel extensions.

---

## Layer 1: Ghost Projection

Project cluster state to filesystem for offline tools.

### Directory Structure

```
.kgents/ghost/
├── agents/
│   ├── b-gent/
│   │   ├── status.json
│   │   └── metrics.json
│   └── ...
├── pheromones/
│   ├── active.json
│   └── by_type/
│       ├── WARNING.json
│       └── DREAM.json
├── proposals/
│   ├── pending.json
│   └── merged.json
├── cluster_status.json
└── _meta/
    └── last_sync.txt
```

### CLI

```bash
kgents ghost              # One-shot projection
kgents ghost --daemon     # Background refresh every 5s
kgents ghost --stop       # Stop daemon
kgents ghost --status     # Check daemon status
```

### Usage

```bash
# Search with standard tools
grep -r "WARNING" .kgents/ghost/pheromones/
jq '.surprise' .kgents/ghost/agents/*/metrics.json
cat .kgents/ghost/cluster_status.json
```

---

## Layer 2: Terrarium TUI

Visual glass box using Textual.

```
┌─────────────────────────────────────────────────────────────────┐
│ TERRARIUM                                              12:34 UTC │
├─────────────────────────────────────────────────────────────────┤
│  ┌─ AGENTS ──────────────────┐  ┌─ PHEROMONES ────────────────┐ │
│  │ B-gent  ████████░░  80%   │  │   ░░▒▒▓▓███[WARN]██▓▓▒▒░░   │ │
│  │ L-gent  ██████████ 100%   │  │                              │ │
│  │ Dreamer ████░░░░░░  40%   │  │                              │ │
│  └───────────────────────────┘  └──────────────────────────────┘ │
│  ┌─ PROPOSALS ──────────────────────────────────────────────────┐│
│  │ PENDING  b-gent-scale  Risk: 0.25  "High load"               ││
│  └──────────────────────────────────────────────────────────────┘│
│  ┌─ THOUGHT STREAM ─────────────────────────────────────────────┐│
│  │ 12:34:52 [B-gent] Processing invoice batch                   ││
│  │ 12:34:54 [M-gent] Attractor forming around protocols/cli/    ││
│  └──────────────────────────────────────────────────────────────┘│
│  [q]uit [r]efresh [t]ether [p]roposals                          │
└─────────────────────────────────────────────────────────────────┘
```

### CLI

```bash
kgents observe                     # Full TUI
kgents observe --compact           # Smaller terminal
kgents observe --simple            # ANSI fallback (SSH)
kgents observe --agents b-gent     # Filter agents
```

---

## Layer 2.5: Tether Protocol

Bidirectional debugging connection.

```
Terminal                                 Agent Pod
┌────────────────┐                      ┌────────────────┐
│  Ctrl+C ───────────▶ SIGTERM          │  Logic         │
│  stdout ◀──────────── stdout          │  Container     │
│  localhost:5678 ◀──── debugpy ────────│                │
└────────────────┘                      └────────────────┘
```

### CLI

```bash
kgents tether b-gent                # Attach to agent
# Ctrl+C forwards SIGTERM to pod

kgents tether b-gent --debug        # With debugpy
# Debugger listening on localhost:5678

kgents tether --list                # Active tethers
```

---

## Layer 3: MCP Server

Model Context Protocol for Claude Code integration.

### Resources (Read)

```
kgents://agents              # All agents and status
kgents://agents/{name}       # Specific agent
kgents://pheromones          # Active pheromones
kgents://pheromones/{type}   # By type
kgents://proposals           # All proposals
kgents://cluster_status      # Cluster health
```

### Tools (Write)

```python
@server.tool("kgents_emit_pheromone")
async def emit(type: str, intensity: float, payload: str): ...

@server.tool("kgents_propose")
async def propose(target: str, patch: str, reason: str): ...

@server.tool("kgents_call")
async def call(agent: str, payload: dict): ...
```

### Configuration

```json
// .mcp.json
{
  "servers": {
    "kgents": {
      "command": "kgents",
      "args": ["mcp", "serve"]
    }
  }
}
```

### Claude Code Usage

```
<resource>kgents://agents</resource>
<resource>kgents://pheromones/WARNING</resource>

<tool>kgents_call</tool>
{"agent": "b-gent", "payload": {"action": "check_balance"}}
```

---

## Graceful Degradation

| Command | Cluster Up | Cluster Down |
|---------|------------|--------------|
| `kgents observe` | Live TUI | "Cluster unavailable" |
| `kgents ghost` | Projects live | Shows cached |
| `kgents tether` | Attaches | "No pods" |
| MCP resources | Live | Cached or empty |
| `kgents status` | Live | "Offline. Last sync: 5m ago" |

---

## Principle Alignment

| Principle | Manifestation |
|-----------|---------------|
| **Transparent** | Three layers make invisible visible |
| **Graceful** | Ghost works offline |
| **Joy-Inducing** | TUI is a glass box you peer into |
| **Tasteful** | Three layers, not ten tools |
| **Ethical** | Tether shows exactly what agents do |

---

## Anti-Patterns

| Anti-Pattern | Why Wrong |
|--------------|-----------|
| FUSE-only | Fragile on macOS |
| No offline | Breaks when cluster down |
| Log-only debugging | No signal forwarding |
| Static dashboards | Agents are flow |

---

*"Infrastructure should communicate. Users should never wonder 'what just happened?'"*
