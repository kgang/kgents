# CLI Hollowing Plan: The Glass Terminal

**Status**: Tier 1 Complete, Tier 2 Complete
**Date**: 2025-12-11 (Updated)
**Philosophy**: "The CLI must be lobotomized." — The CLI should feel like glass: thin, transparent, resilient.
**Principles Applied**: Graceful Degradation, Transparent Infrastructure, Generative, Composable
**Refinements**: ResilientClient as LogosNode (v3.1)

---

## Critical Refinement (v3.1)

### GlassClient → ResilientClient (LogosNode)

**The original design** had `GlassClient` as a simple gRPC wrapper.

**The refinement**: The client IS a `LogosNode`—it participates in the AGENTESE graph. `ResilientClient.invoke()` IS `LogosNode.invoke()`. This makes the CLI a true AGENTESE interpreter.

```python
# protocols/cli/glass.py
class ResilientClient(LogosNode):
    """
    The CLI's Logos interface as a LogosNode.

    The client IS a node in the graph, not just a consumer.
    ResilientClient.invoke() IS LogosNode.invoke().

    handle: "self.cli"
    """
    handle: str = "self.cli"

    def affordances(self, observer: AgentMeta) -> list[str]:
        return ["invoke", "manifest", "ghost"]

    async def manifest(self, observer: Umwelt) -> Renderable:
        return CLIStatus(
            connected=self._is_connected(),
            ghost_available=self._ghost_exists(),
        )
```

See `plans/lattice-refinement.md` for full rationale.

---

## Implementation Status (2025-12-11)

### Completed Work

| Component | Status | Location |
|-----------|--------|----------|
| **Tier 1: gRPC Foundation** | ✅ Complete | |
| `logos.proto` | ✅ | `protocols/proto/logos.proto` |
| Generated stubs | ✅ | `protocols/proto/generated/` |
| `GlassClient` | ✅ | `protocols/cli/glass.py` |
| `GhostCache` | ✅ | `protocols/cli/glass.py` |
| `CortexServicer` | ✅ | `infra/cortex/service.py` |
| `Cortex daemon` | ✅ | `infra/cortex/daemon.py` |
| K8s manifests | ✅ | `infra/k8s/manifests/cortex-daemon-deployment.yaml` |
| **Tier 2: Hollowed Handlers** | ✅ Complete | |
| `status.py` | ✅ Hollowed | Uses `GetStatus` RPC |
| `dream.py` | ✅ Hollowed | Uses `Invoke` with `self.dreamer.*` paths |
| `map.py` | ✅ Hollowed | Uses `GetMap` RPC |
| `signal.py` | ✅ Hollowed | Uses `Invoke` with `self.field.*` paths |

### Architecture Verified Working

```
CLI Handler → asyncio.run(_async_handler())
                   ↓
           GlassClient.invoke(method, request, ghost_key)
                   ↓
     ┌─────────────┴─────────────┐
     │   Three-Layer Fallback    │
     │  1. gRPC (500ms timeout)  │
     │  2. Local CortexServicer  │
     │  3. Ghost Cache           │
     └─────────────┬─────────────┘
                   ↓
           GlassResponse(data, is_ghost, ghost_age)
                   ↓
           _extract_*_data() → render output
```

### Next Steps (Tier 3+)

- [ ] Hollow `ghost.py` (filesystem commands)
- [ ] Hollow `flinch.py` (partial)
- [ ] Implement `StreamDreams` bi-directional streaming
- [ ] Convert handlers to `@expose` pattern
- [ ] Add `--web` visualization to `map.py`

---

## Overview

This plan transforms the kgents CLI into a **Glass Terminal**—a hollow shell that:
1. Parses arguments
2. Makes gRPC calls to the Cortex daemon
3. Formats output
4. **Falls back gracefully when the daemon is unavailable** (Ghost Mode)

**The Test**: Can you rewrite `kgents status` in 20 lines of Go? If not, it's not hollow enough.

**The Resilience Test**: Does `kgents status` still show useful information when the cluster is down? If not, it violates Graceful Degradation.

---

## Critical Design Constraint: The Bootstrap Paradox

> "If `kgents status` fails because the gRPC daemon is down, you have created a Bootstrap Paradox: You need the CLI to debug why the infrastructure is down, but the CLI won't work because the infrastructure is down."

**Resolution**: The **Ghost Protocol**—every CLI command has two modes:

| Mode | When | Behavior |
|------|------|----------|
| **Cortex Mode** | gRPC available | Full capability, live data |
| **Ghost Mode** | gRPC unavailable | Last-known-good from `.kgents/ghost/`, with `[GHOST]` prefix |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE GLASS TERMINAL                                   │
│                                                                              │
│   CLI invocation                                                            │
│        │                                                                     │
│        ▼                                                                     │
│   ┌─────────────────────────────────┐                                       │
│   │ Attempt gRPC (500ms timeout)    │                                       │
│   └──────────────┬──────────────────┘                                       │
│                  │                                                           │
│         ┌───────┴───────┐                                                   │
│         │               │                                                    │
│         ▼               ▼                                                    │
│   ┌──────────┐   ┌──────────────────┐                                       │
│   │ SUCCESS  │   │ FAILURE          │                                       │
│   │ Live data│   │ Read Ghost cache │                                       │
│   │ + update │   │ Show [GHOST]     │                                       │
│   │ cache    │   │ prefix           │                                       │
│   └──────────┘   └──────────────────┘                                       │
│                                                                              │
│   "Online Brain, Offline Reflexes"                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Current Architecture Analysis

### Two CLI Patterns Identified

#### Pattern A: `cmd_<name>` Handlers (handlers/*.py)
Traditional command handlers with `def cmd_<name>(args: list[str]) -> int` signature.

| Handler | File | Lines | Business Logic | Hollowness Score |
|---------|------|-------|----------------|------------------|
| status | status.py | 204 | High - imports CortexObserver, Dashboard, builds state | 2/10 |
| dream | dream.py | 215 | High - imports Dreamer, runs REM cycles | 2/10 |
| map | map.py | 308 | High - imports HoloMap, builds cartography | 1/10 |
| signal | signal.py | 270 | High - imports SemanticField, emits/senses | 2/10 |
| ghost | ghost.py | 328 | Medium - uses GhostDaemon, but daemon is external | 4/10 |
| infra | infra.py | 768 | Medium-High - cluster management, subprocess calls | 3/10 |
| tether | tether.py | 156 | **Good** - delegates to TetherProtocol | 7/10 |
| observe | observe.py | 185 | **Good** - delegates to TerrariumApp | 7/10 |
| dev | dev.py | 229 | **Good** - delegates to DevMode | 7/10 |
| exec | exec.py | 178 | **Good** - delegates to Quartermaster | 6/10 |
| flinch | flinch.py | 272 | Medium - uses FlinchCollector, but data-driven | 5/10 |
| membrane | membrane.py | 175 | **Good** - mostly stubs (deprecated) | 8/10 |
| init | init.py | 80 | **Good** - minimal, calls init_workspace | 7/10 |

#### Pattern B: `@expose` Decorator CLIs (agents/*/cli.py)
Prism-based CLIs implementing `CLICapable` protocol.

| CLI | File | Commands | @expose Usage | Pattern |
|-----|------|----------|---------------|---------|
| GrammarianCLI | g/cli.py | 7 | Full | Agent instantiation in methods |
| LibraryCLI | l/cli.py | 8 | Full | Agent instantiation in methods |
| JitCLI | j/cli.py | 6 | Full | Agent instantiation in methods |
| WitnessCLI | w/cli.py | 6 | Full | Agent instantiation in methods |

---

## Gap Analysis

### Problem 1: Handler Pattern Inconsistency

- handlers/*.py use manual arg parsing
- agents/*/cli.py use Prism/@expose auto-generation
- No unified approach

### Problem 2: Business Logic in CLI Layer

**Worst offenders** (need complete rewrite):
1. `status.py` - Instantiates CortexObserver, CortexDashboard
2. `dream.py` - Creates LucidDreamer, runs cycles
3. `map.py` - Builds HoloMap from scratch, generates embeddings
4. `signal.py` - Creates SemanticField, manages pheromones

**These should**: Call gRPC endpoints, receive pre-formatted data

### Problem 3: gRPC Service Not Implemented

`protocols/proto/kgents.proto` defines the service contract but there's no:
- gRPC server implementation (Cortex daemon)
- Generated Python stubs being used
- Client wrapper for CLI handlers

---

## Hollowing Strategy

### The Command Tiers (What Gets Hollowed, What Stays Thick)

Not all commands should be hollowed equally. The critique identifies a critical exception:

| Tier | Commands | Strategy | Rationale |
|------|----------|----------|-----------|
| **Tier 0: Bootstrap** | `infra`, `init` | **Keep Thick** | Must work when nothing else does |
| **Tier 1: Status** | `status` | **Bulletproof Hollow** | Always works (gRPC or Ghost) |
| **Tier 2: Core** | `dream`, `map`, `signal` | **Hollow with Ghost fallback** | Graceful degradation |
| **Tier 3: Interactive** | `observe`, `tether` | **Hollow (streaming)** | gRPC streams, graceful disconnect |
| **Tier 4: Offline** | `ghost` | **Keep As-Is** | By definition works offline |

### Phase 0: The Ghost Protocol Foundation (NEW - Blocking All Else)

Before hollowing, implement the resilience layer.

#### 0.1 Ghost Cache Structure
Location: `.kgents/ghost/`

```
.kgents/ghost/
├── status.json         # Last known cortex status
├── map.json            # Last known holoMap
├── agents/             # Per-agent state snapshots
│   ├── d-gent.json
│   └── l-gent.json
└── meta.json           # Timestamps, staleness info
```

#### 0.2 The Glass Client (Not Just CortexClient)
Location: `impl/claude/protocols/cli/glass.py`

```python
# protocols/cli/glass.py
"""
The Glass Client: A resilient gRPC wrapper with Ghost fallback.

Principle: Graceful Degradation - never fail completely.
"""
from pathlib import Path
import json
import grpc
from datetime import datetime, timedelta

GHOST_DIR = Path.home() / ".kgents" / "ghost"
GRPC_TIMEOUT = 0.5  # 500ms - fail fast to Ghost

@dataclass
class GlassResponse:
    """Response that knows whether it came from live or ghost."""
    data: Any
    is_ghost: bool = False
    ghost_age: timedelta | None = None

    def render(self, format: str = "text") -> str:
        prefix = "[GHOST] " if self.is_ghost else ""
        age_suffix = f" (data from {self.ghost_age.seconds}s ago)" if self.ghost_age else ""
        # ... render logic

class GlassClient:
    """
    The CLI's view of the world—resilient, never blind.

    Always returns data: live if possible, ghost if not.
    The user is never left wondering "what happened?"
    """

    def __init__(self, address: str = "localhost:50051"):
        self.address = address
        self._stub: CortexStub | None = None

    async def invoke(
        self,
        method: str,
        request: Any,
        ghost_key: str | None = None,
    ) -> GlassResponse:
        """
        Invoke a gRPC method with Ghost fallback.

        Args:
            method: The gRPC method name (e.g., "GetStatus")
            request: The protobuf request
            ghost_key: Key for ghost cache (e.g., "status")
        """
        try:
            # Attempt live connection
            channel = grpc.aio.insecure_channel(self.address)
            stub = CortexStub(channel)

            response = await asyncio.wait_for(
                getattr(stub, method)(request),
                timeout=GRPC_TIMEOUT
            )

            # Success! Update ghost cache
            if ghost_key:
                self._update_ghost(ghost_key, response)

            return GlassResponse(data=response, is_ghost=False)

        except (grpc.RpcError, asyncio.TimeoutError, ConnectionError) as e:
            # Ghost mode: read from cache
            if ghost_key:
                ghost_data, age = self._read_ghost(ghost_key)
                if ghost_data:
                    return GlassResponse(
                        data=ghost_data,
                        is_ghost=True,
                        ghost_age=age
                    )

            # No ghost available - transparent failure
            raise ConnectionError(
                f"Cortex daemon unavailable at {self.address}. "
                f"No cached data for '{ghost_key}'. "
                f"Run 'kgents infra init' to start the daemon, "
                f"or 'kgents infra status' to check infrastructure."
            )

    def _update_ghost(self, key: str, response: Any) -> None:
        """Write to ghost cache."""
        GHOST_DIR.mkdir(parents=True, exist_ok=True)
        ghost_file = GHOST_DIR / f"{key}.json"
        ghost_file.write_text(json.dumps({
            "data": response.to_dict(),
            "timestamp": datetime.now().isoformat(),
        }))

    def _read_ghost(self, key: str) -> tuple[Any, timedelta | None]:
        """Read from ghost cache."""
        ghost_file = GHOST_DIR / f"{key}.json"
        if not ghost_file.exists():
            return None, None

        cached = json.loads(ghost_file.read_text())
        timestamp = datetime.fromisoformat(cached["timestamp"])
        age = datetime.now() - timestamp

        return cached["data"], age
```

### Phase 1: Establish gRPC Foundation

#### 1.1 Proto-First Design (Generative Principle)
> "The Proto file should BE the definition. The CLI code should be generated or generic."

Location: `impl/claude/protocols/proto/logos.proto`

```protobuf
// logos.proto - The Protocol Authority
//
// This file IS the spec. CLI handlers are derived from it.
// Principle: Generative - spec is compression.

syntax = "proto3";
package kgents;

service Logos {
    // Core resolution - maps to logos.invoke()
    rpc Invoke(InvokeRequest) returns (InvokeResponse);

    // Status with Ghost support
    rpc GetStatus(StatusRequest) returns (StatusResponse);

    // Streaming for interactive commands
    rpc StreamDreams(stream DreamInput) returns (stream DreamOutput);
    rpc StreamObserve(ObserveRequest) returns (stream ObserveEvent);

    // Map retrieval (pre-rendered)
    rpc GetMap(MapRequest) returns (HoloMap);
}

message InvokeRequest {
    string path = 1;              // AGENTESE path
    bytes observer_dna = 2;       // Serialized Umwelt
    string lens = 3;              // Optional lens override
    map<string, string> kwargs = 4;
}

message StatusResponse {
    string health = 1;
    repeated AgentStatus agents = 2;
    map<string, float> pheromone_levels = 3;
    float metabolic_pressure = 4;  // For tithe display
    string instance_id = 5;
}
```

#### 1.2 Cortex Service Implementation
Location: `impl/claude/infra/cortex/service.py`

```python
# impl/claude/infra/cortex/service.py
class CortexServicer(LogosServicer):
    """
    gRPC implementation of Logos service.

    This IS the living system. The CLI is just glass in front of it.
    Business logic lives HERE, not in CLI handlers.
    """

    async def GetStatus(self, request, context):
        observer = create_cortex_observer(...)
        dashboard = create_cortex_dashboard(observer)
        return StatusResponse(
            health=dashboard.health,
            agents=[...],
            pheromone_levels={...},
            metabolic_pressure=self.metabolism.pressure,
        )

    async def Invoke(self, request, context):
        """Universal AGENTESE invocation endpoint."""
        return await self.logos.invoke(
            request.path,
            observer=Umwelt.from_proto(request.observer_dna),
            lens=request.lens or "optics.identity",
            **dict(request.kwargs),
        )
```

---

### Phase 2: Hollow the Handlers (Priority Order)

#### 2.1 status.py (HIGHEST priority - The Litmus Test)

**The `status` command must be bulletproof.** It is the debugger. It must never fail completely.

**Before** (204 lines, business logic):
```python
def cmd_status(args):
    # 50+ lines of state management
    observer = _get_or_create_observer(state)
    dashboard = _get_or_create_dashboard(observer)
    # rendering logic
```

**After** (~25 lines, hollow with Ghost):
```python
def cmd_status(args):
    """
    kgents status - Show cortex health.

    Principle: Graceful Degradation - always shows something useful.
    """
    client = GlassClient()
    response = asyncio.run(client.invoke(
        "GetStatus",
        StatusRequest(verbose="--verbose" in args),
        ghost_key="status"  # Ghost-enabled!
    ))

    # The response knows if it's ghost data
    if response.is_ghost:
        print(f"[GHOST] Data from {response.ghost_age.seconds}s ago")
        print(f"        Cortex daemon not responding.")
        print(f"        Run 'kgents infra status' to diagnose.")

    if "--json" in args:
        print(json.dumps(response.data.to_dict()))
    else:
        print(f"[CORTEX] {response.data.health} | {len(response.data.agents)} agents")
        print(f"         Pressure: {response.data.metabolic_pressure:.0%}")

    return 0
```

**Special Case**: If both gRPC AND Ghost fail, `status` has one more fallback:
```python
# Ultimate fallback: raw infrastructure check
if response is None:
    # Check if K8s cluster exists
    k8s_status = subprocess.run(["kubectl", "get", "pods", "-n", "kgents-agents"])
    if k8s_status.returncode != 0:
        print("[OFFLINE] K-Terrarium not running.")
        print("          Run 'kgents infra init' to bootstrap.")
    else:
        print("[DEGRADED] Cortex pods exist but not responding.")
        print("           Run 'kubectl logs -n kgents-agents deploy/cortex'")
```

#### 2.2 dream.py (HIGH priority)

**Before**: Creates Dreamer, runs REM cycles locally
**After**: Bi-directional streaming for interactive dreams

```python
async def cmd_dream(args):
    """
    kgents dream - Interactive dream session.

    Uses bi-directional gRPC streaming:
    - CLI sends stdin → gRPC stream
    - Daemon processes → gRPC stream → CLI stdout
    """
    client = GlassClient()

    # Non-interactive: just get briefing
    if "--brief" in args:
        response = await client.invoke("GetDreamBriefing", {}, ghost_key="dream")
        print(response.data.briefing)
        return 0

    # Interactive: bi-directional stream
    async with client.stream("StreamDreams") as stream:
        async for dream_chunk in stream:
            print(dream_chunk.text, end="", flush=True)

            if dream_chunk.awaiting_input:
                user_input = input("> ")
                await stream.send(DreamInput(text=user_input))
```

#### 2.3 map.py (HIGH priority)

**Before**: Builds HoloMap from scratch with embeddings
**After**: `client.get_map()` returns pre-rendered visualization

```python
def cmd_map(args):
    """kgents map - Show holographic map."""
    client = GlassClient()
    response = asyncio.run(client.invoke(
        "GetMap",
        MapRequest(format=args.get("--format", "text")),
        ghost_key="map"
    ))

    # Awesome feature: web visualization
    if "--web" in args:
        # Spin up temporary localhost server
        serve_map_visualization(response.data)
    else:
        print(response.render())
```

#### 2.4 signal.py (MEDIUM priority)

**Before**: Creates SemanticField, manages pheromones
**After**: Simple gRPC calls to pheromone endpoints

#### 2.5 infra.py (EXCEPTION - Keep Thick)

**DO NOT HOLLOW `infra`.** It is the tool used to BUILD the Cortex.

```python
# infra.py stays thick because:
# 1. It must work when Cortex doesn't exist yet
# 2. It wraps subprocess calls (docker, kubectl, kind)
# 3. It IS the bootstrap mechanism

# The only change: infra WRITES to ghost cache after successful operations
def cmd_infra_init(args):
    """Bootstrap K-Terrarium."""
    # ... existing subprocess logic ...

    # After successful init, seed the ghost cache
    seed_ghost_cache({
        "status": {"health": "INITIALIZING", "agents": []},
        "meta": {"initialized_at": datetime.now().isoformat()}
    })
```

---

### Phase 3: Unify with @expose Pattern

#### 3.1 Convert handlers to Prism CLIs

Create `protocols/cli/handlers/status_cli.py`:
```python
class StatusCLI(CLICapable):
    @property
    def genus_name(self) -> str:
        return "status"

    @expose(help="Show cortex status")
    async def show(self, verbose: bool = False) -> dict:
        client = CortexClient()
        response = await client.get_status(verbose)
        return response.to_dict()
```

#### 3.2 Update Main Router

The hollow shell in `hollow.py` should:
1. Detect if genus is CLICapable
2. Use Prism for @expose commands
3. Fall back to legacy handlers during migration

---

### Phase 4: Cortex Daemon Deployment

#### 4.1 Kubernetes Deployment
Location: `infra/k8s/manifests/cortex-daemon-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cortex-daemon
  namespace: kgents-agents
spec:
  template:
    spec:
      containers:
      - name: cortex
        image: kgents/cortex:latest
        ports:
        - containerPort: 50051  # gRPC
        - containerPort: 8080   # health
```

#### 4.2 Fallback Mode
When cluster unavailable, CLI should:
- Detect: `if cluster.status() != RUNNING`
- Message: "K-Terrarium not running. Run 'kgents infra init'"
- Exception: `ghost` command still works (reads cached files)

---

## Implementation Order

### Tier 0: Ghost Protocol (NEW - Blocking All Else)
1. Create `.kgents/ghost/` structure and `GlassResponse` dataclass
2. Implement `GlassClient` with Ghost fallback
3. Add ghost cache write to existing handlers (prep for migration)

### Tier 1: Foundation
4. Write `logos.proto` (Proto-First Design)
5. Generate gRPC stubs with `buf` or `protoc`
6. Implement `CortexServicer` with `GetStatus` + `Invoke` endpoints
7. Hollow `status.py` as proof-of-concept (**with all three fallback layers**)

### Tier 2: Core Handlers
8. Hollow `dream.py` with bi-directional streaming
9. Hollow `map.py` with `--web` visualization option
10. Hollow `signal.py`
11. Add `StreamObserve` endpoint for `observe.py`

### Tier 3: Unification
12. Convert hollow handlers to `@expose` pattern
13. Merge Prism integration into main router
14. Create migration compatibility layer

### Tier 4: Infrastructure Integration
15. Deploy Cortex daemon to K-Terrarium
16. Update `kgents infra init` to deploy daemon + seed ghost cache
17. Wire TUI/observe to use gRPC streams

---

## Cross-Reference: AGENTESE Synthesis

This plan is **isomorphic** to the AGENTESE evolution (see `plans/agentese-synthesis.md`).

| CLI Hollowing Concept | AGENTESE Equivalent |
|----------------------|---------------------|
| `GlassClient` | Logos resolver |
| `ghost_key` parameter | `self.memory.manifest` (cached state) |
| gRPC `Invoke()` | `logos.invoke(path, observer)` |
| Ghost fallback | Graceful degradation to D-gent memory |
| `[GHOST]` prefix | Transparent Infrastructure principle |

**The Core Isomorphism**:
```
CLI Command  →  GlassClient.invoke()  →  gRPC  →  Logos.invoke()  →  Living System
                     ↓                                                      ↓
               Ghost fallback                               AGENTESE path resolution
```

**Unified Implementation Strategy**:
- Phase 0 (Ghost) enables Tier 0 of AGENTESE synthesis (CLI Hollowing Foundation)
- Phase 1 (gRPC) implements the Logos resolver's gRPC boundary
- Every `ghost_key` maps to an AGENTESE `self.*` path for cached state

---

## @expose Decorator Adoption Plan

### Current State
- 4 agent CLIs use @expose: G, L, J, W
- 13 handlers use cmd_* pattern
- Prism infrastructure exists and works

### Target State
All commands should be @expose-able with:
```python
@expose(
    help="Short description",
    examples=["kgents cmd example"],
    aliases=["alias"],
)
async def command(self, arg: str, flag: bool = False) -> dict:
    ...
```

### Migration Matrix

| Handler | Current Pattern | Target | Notes |
|---------|-----------------|--------|-------|
| status | cmd_* | @expose + gRPC | High priority |
| dream | cmd_* | @expose + gRPC | High priority |
| map | cmd_* | @expose + gRPC | High priority |
| signal | cmd_* | @expose + gRPC | Medium priority |
| ghost | cmd_* | Keep (filesystem) | Works offline |
| infra | cmd_* | Partial @expose | Keep subprocess |
| tether | cmd_* | @expose | Already hollow |
| observe | cmd_* | @expose | Already hollow |
| dev | cmd_* | @expose | Already hollow |
| exec | cmd_* | @expose | Already hollow |
| flinch | cmd_* | @expose + gRPC | Data-driven |
| membrane | cmd_* | Deprecate | Already stubs |
| init | cmd_* | Keep | Bootstrap |

---

## Success Criteria

### Quantitative
| Metric | Current | Target |
|--------|---------|--------|
| Avg handler lines | 220 | <50 |
| Business logic imports | 47 | 0 |
| gRPC coverage | 0% | 80% |
| @expose adoption | 4/17 | 15/17 |

### Qualitative
- [ ] `kgents status` implementable in 20 lines of Go
- [ ] CLI fails gracefully when daemon offline
- [ ] All handlers testable without agent instantiation
- [ ] Type hints auto-generate argparse via Prism

### Anti-Patterns to Eliminate
- [ ] No agent imports in handlers
- [ ] No `asyncio.run()` to execute business logic
- [ ] No state management in CLI layer
- [ ] No data processing/transformation

---

## File Inventory

### Files to Modify
```
protocols/cli/handlers/status.py     # Hollow
protocols/cli/handlers/dream.py      # Hollow
protocols/cli/handlers/map.py        # Hollow
protocols/cli/handlers/signal.py     # Hollow
protocols/cli/handlers/flinch.py     # Hollow (partial)
protocols/cli/hollow.py              # Add gRPC client integration
```

### Files to Create
```
protocols/proto/generated/           # gRPC stubs
protocols/cli/cortex_client.py       # gRPC client wrapper
infra/cortex/service.py              # Cortex gRPC server
infra/cortex/__init__.py
infra/k8s/manifests/cortex-daemon-deployment.yaml
```

### Files to Keep As-Is
```
protocols/cli/handlers/init.py       # Bootstrap, minimal
protocols/cli/handlers/ghost.py      # Filesystem, offline capable
protocols/cli/handlers/membrane.py   # Deprecated stubs
protocols/cli/handlers/tether.py     # Already hollow
protocols/cli/handlers/observe.py    # Already hollow
protocols/cli/handlers/dev.py        # Already hollow
protocols/cli/handlers/exec.py       # Already hollow
```

---

## Risk Assessment

### Risk 1: Breaking Changes During Migration
**Mitigation**:
- Compatibility layer that detects old vs new handlers
- Feature flag `KGENTS_GRPC_ENABLED=1`
- Gradual rollout per handler

### Risk 2: Daemon Not Running
**Mitigation**:
- Clear error messages: "K-Terrarium not running"
- `ghost` command works offline (reads .kgents/ghost/)
- `infra init` always works

### Risk 3: Performance Overhead
**Mitigation**:
- gRPC is fast (sub-ms local, <10ms network)
- Streaming for observe/tether already proven
- Pre-serialized responses avoid CLI-side processing

---

## Appendix: Handler Audit Details

### status.py Deep Dive
**Imports business logic**: CortexObserver, CortexDashboard, create_* functions
**Creates state**: Calls _get_or_create_observer(), _get_or_create_dashboard()
**Data transformation**: Builds JSON from dashboard.get_wire_state()
**Should become**: Simple gRPC call + JSON dump

### map.py Deep Dive
**Imports**: HoloMap, Attractor, WeightedEdge, Void, Horizon, ContextVector
**Creates embeddings**: _path_to_embedding() generates pseudo-embeddings
**Builds data structures**: Creates Attractor, WeightedEdge manually
**Should become**: gRPC call returns pre-built HoloMap protobuf

### dream.py Deep Dive
**Imports**: create_lucid_dreamer, DreamPhase
**Runs async**: asyncio.run(_run_rem_cycle(dreamer))
**Interactive**: _answer_questions() with input() loop
**Should become**: gRPC GetDream + StreamDreams for interactive
