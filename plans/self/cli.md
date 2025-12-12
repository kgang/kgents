# CLI Hollowing: self.cli.* Implementation

> *"The CLI must be lobotomized. It should feel like glass: thin, transparent, resilient."*

**AGENTESE Context**: `self.cli.*`
**Status**: Tier 1-2 Complete
**Principles**: Graceful Degradation, Transparent Infrastructure, Composable

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **ResilientClient as LogosNode** | The client IS a node in the AGENTESE graph, not just a consumer |
| **Three-layer fallback** | gRPC → Ghost → kubectl. Never blind. |
| **500ms gRPC timeout** | Fail fast to Ghost mode |
| **`[GHOST]` prefix** | Transparent Infrastructure—user knows data is stale |
| **20-line test** | "Can you rewrite this handler in 20 lines of Go?" |
| **`infra` stays thick** | Bootstrap tool must work when nothing else does |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: SHELL (Hollow CLI)                                 │
│   • 20 lines per command                                    │
│   • Parse args → invoke → format                            │
│   • No business logic                                       │
└────────────────────────────┬────────────────────────────────┘
                             │ gRPC / logos.invoke()
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: LOGOS (The Resolver)                               │
│   • String path → LogosNode resolution                      │
│   • Lens application (Optics layer)                         │
│   • Observer threading (Umwelt)                             │
└────────────────────────────┬────────────────────────────────┘
                             │ async invoke()
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: SUBSTRATE (Living System)                          │
│   • MetabolicEngine, D-gent, N-gent, L-gent                │
│   • All business logic lives HERE                           │
└─────────────────────────────────────────────────────────────┘
```

---

## ResilientClient (✅ DONE)

The client IS a `LogosNode`—it participates in the AGENTESE graph:

```python
class ResilientClient(LogosNode):
    """
    The CLI's Logos interface as a LogosNode.

    handle: "self.cli"
    affordances: ["invoke", "manifest", "ghost"]
    """

    handle: str = "self.cli"

    async def invoke(
        self,
        method: str,
        request: Any,
        ghost_key: str | None = None,
    ) -> GlassResponse:
        """
        Three-layer fallback invocation.

        1. Try gRPC (500ms timeout)
        2. Try Ghost cache
        3. Try raw kubectl
        """
        ...
```

**Location**: `protocols/cli/glass.py` (631 lines)

---

## Ghost Protocol (✅ DONE)

```
~/.kgents/ghost/
├── status.json         # Last known cortex status
├── map.json            # Last known holoMap
├── agents/             # Per-agent state snapshots
└── meta.json           # Timestamps, staleness info
```

**Staleness behavior**:
- Fresh: Show live data
- Stale: Show with `[GHOST]` prefix
- Very stale: Refuse (don't mislead)

---

## Hollowed Handlers (✅ DONE)

| Handler | Status | AGENTESE Path | Notes |
|---------|--------|---------------|-------|
| `status.py` | ✅ Hollowed | `self.cortex.manifest` | Uses `GetStatus` RPC |
| `dream.py` | ✅ Hollowed | `self.memory.consolidate` | Uses `Invoke` with `self.dreamer.*` |
| `map.py` | ✅ Hollowed | `world.project.manifest` | Uses `GetMap` RPC |
| `signal.py` | ✅ Hollowed | `void.pheromone.*` | Uses `Invoke` with `self.field.*` |
| `ghost.py` | 📋 Keep Thick | N/A | Filesystem, works offline |
| `infra.py` | 📋 Keep Thick | N/A | Bootstrap tool |
| `tether.py` | ✅ Already Hollow | | Delegates to TetherProtocol |
| `observe.py` | ✅ Already Hollow | | Delegates to TerrariumApp |
| `dev.py` | ✅ Already Hollow | | Delegates to DevMode |

---

## Handler Migration Pattern

**Before** (business logic in CLI):
```python
def cmd_status(args):
    observer = _get_or_create_observer(state)      # Business logic
    dashboard = _get_or_create_dashboard(observer)  # Business logic
    # 50+ lines of state management
```

**After** (hollow shell):
```python
def cmd_status(args):
    """kgents status - Show cortex health."""
    client = GlassClient()
    response = asyncio.run(client.invoke(
        "GetStatus",
        StatusRequest(verbose="--verbose" in args),
        ghost_key="status"  # Ghost-enabled!
    ))

    if response.is_ghost:
        print(f"[GHOST] Data from {response.ghost_age.seconds}s ago")

    print(response.render())
    return 0
```

---

## Command Tiers

| Tier | Commands | Strategy |
|------|----------|----------|
| **Tier 0: Bootstrap** | `infra`, `init` | Keep Thick (must work when nothing else does) |
| **Tier 1: Status** | `status` | Bulletproof Hollow (always works) |
| **Tier 2: Core** | `dream`, `map`, `signal` | Hollow with Ghost fallback |
| **Tier 3: Interactive** | `observe`, `tether` | Hollow (streaming) |
| **Tier 4: Offline** | `ghost` | Keep As-Is (by definition offline) |

---

## Next Steps (📋 PLANNED)

1. **Hollow `flinch.py`** (partial)
2. **Implement `StreamDreams`** bi-directional streaming
3. **Convert handlers to `@expose` pattern**
4. **Add `--web` visualization to `map.py`**

---

## Proto Definitions (✅ DONE)

```protobuf
// protocols/proto/logos.proto
service Logos {
    rpc Invoke(InvokeRequest) returns (InvokeResponse);
    rpc GetStatus(StatusRequest) returns (StatusResponse);
    rpc StreamDreams(stream DreamInput) returns (stream DreamOutput);
    rpc StreamObserve(ObserveRequest) returns (stream ObserveEvent);
    rpc GetMap(MapRequest) returns (HoloMap);
}
```

---

## Success Criteria

**Quantitative**:
| Metric | Current | Target |
|--------|---------|--------|
| Avg handler lines | ~50 | <50 ✅ |
| Business logic imports | 0 | 0 ✅ |
| gRPC coverage | 80% | 80% ✅ |
| @expose adoption | 4/17 | 15/17 |

**Qualitative**:
- [x] `kgents status` implementable in 20 lines of Go
- [x] CLI fails gracefully when daemon offline
- [x] All handlers testable without agent instantiation
- [ ] Type hints auto-generate argparse via Prism

---

## Cross-References

- **Plans**: `world/k8-gents.md` (Ghost Protocol), `self/stream.md` (Ghost = D-gent memory)
- **Impl**: `protocols/cli/glass.py`, `infra/cortex/service.py`, `protocols/proto/logos.proto`
- **Spec**: `spec/principles.md` (Graceful Degradation)

---

*"The CLI is hollow glass—a 20-line invocation that lets the living system shine through."*
