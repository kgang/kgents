# Implementation Status Matrix

> Last updated: 2025-12-11 (Phase 2.1 complete)

This document tracks implementation status against plans. Verified against actual codebase.

---

## Legend

| Symbol | Status |
|--------|--------|
| ✅ | Done - implemented and verified |
| 🚧 | In Progress - partially implemented |
| 📋 | Planned - not yet started |
| ⏸️ | Blocked - waiting on dependency |
| ❌ | Rejected - decided not to implement |

---

## CLI Hollowing (`self/cli.md`)

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| `logos.proto` | ✅ Done | `protocols/proto/logos.proto` | gRPC service definition |
| `kgents.proto` | ✅ Done | `protocols/proto/kgents.proto` | K8s message types |
| Generated stubs | ✅ Done | `protocols/proto/generated/` | Python gRPC stubs |
| `GlassClient` | ✅ Done | `protocols/cli/glass.py` | 631 lines, three-layer fallback |
| `GhostCache` | ✅ Done | `protocols/cli/glass.py` | Integrated in GlassClient |
| `CortexServicer` | ✅ Done | `infra/cortex/service.py` | 32KB, full Logos resolver |
| `Cortex daemon` | ✅ Done | `infra/cortex/daemon.py` | gRPC server lifecycle |
| K8s manifest (Cortex) | ✅ Done | `infra/k8s/manifests/cortex-daemon-deployment.yaml` | |
| K8s manifest (Ghost) | ✅ Done | `infra/k8s/manifests/ghost-daemon-deployment.yaml` | |
| Hollowed `status.py` | ✅ Done | `protocols/cli/handlers/status.py` | Uses `GetStatus` RPC |
| Hollowed `dream.py` | ✅ Done | `protocols/cli/handlers/dream.py` | Uses `Invoke` with `self.dreamer.*` |
| Hollowed `map.py` | ✅ Done | `protocols/cli/handlers/map.py` | Uses `GetMap` RPC |
| Hollowed `signal.py` | ✅ Done | `protocols/cli/handlers/signal.py` | Uses `Invoke` with `self.field.*` |
| Hollowed `ghost.py` | 📋 Planned | | Filesystem, may keep thick |
| Hollowed `flinch.py` | 📋 Planned | | Partial hollowing |
| `StreamDreams` bi-directional | 📋 Planned | | For interactive dreams |
| `@expose` pattern migration | 📋 Planned | | Convert handlers to Prism |
| `--web` visualization (map) | 📋 Planned | | Web-based map rendering |

---

## K8s Infrastructure (`world/k8-gents.md`)

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| Agent CRD | ✅ Done | `infra/k8s/crds/agent-crd.yaml` | 11KB |
| Pheromone CRD | ✅ Done | `infra/k8s/crds/pheromone-crd.yaml` | 4.6KB |
| Memory CRD | ✅ Done | `infra/k8s/crds/memory-crd.yaml` | 5KB |
| Umwelt CRD | ✅ Done | `infra/k8s/crds/umwelt-crd.yaml` | 6.3KB |
| Proposal CRD | ✅ Done | `infra/k8s/crds/proposal-crd.yaml` | 13.7KB |
| Agent Operator | ✅ Done | `infra/k8s/operators/agent_operator.py` | 700 lines, kopf handlers |
| Pheromone Operator | ✅ Done | `infra/k8s/operators/pheromone_operator.py` | 348 lines, decay loop |
| Proposal Operator | ✅ Done | `infra/k8s/operators/proposal_operator.py` | 795 lines, risk calc |
| T-gent Webhook | 📋 Planned | | ValidatingAdmissionWebhook |
| Cortex daemon deployment | ✅ Done | `infra/k8s/manifests/cortex-daemon-deployment.yaml` | |
| Tether Protocol | ✅ Done | `infra/k8s/tether.py` | Agent tethering |
| Cognitive Probes | 📋 Planned | `infra/cortex/probes.py` | LLM health checks |
| Durable Execution | 📋 Planned | | CRD state machine |
| Dream Cycle Operator | 📋 Planned | | Low-load self-optimization |
| Terrarium TUI | 🚧 In Progress | `agents/i/terrarium_tui.py` | Basic structure exists |
| Visual Stigmergy (heatmap) | 📋 Planned | | Pheromone visualization |
| Seance Mode | 📋 Planned | | Time-travel debugging |

### K8s Operationalization (Phase A-F)

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| Cluster setup script | ✅ Done | `infra/k8s/scripts/setup-cluster.sh` | Phase A |
| Cluster verify script | ✅ Done | `infra/k8s/scripts/verify-cluster.sh` | Phase A |
| Cluster teardown script | ✅ Done | `infra/k8s/scripts/teardown-cluster.sh` | Phase A |
| Operator Dockerfile | ✅ Done | `infra/k8s/operators/Dockerfile` | Phase B |
| Operator deployment | ✅ Done | `infra/k8s/manifests/operators-deployment.yaml` | Phase B |
| Operator deploy script | ✅ Done | `infra/k8s/scripts/deploy-operators.sh` | Phase B |
| L-gent HTTP server | 📋 Planned | `agents/l/server.py` | Phase C |
| L-gent Dockerfile | 📋 Planned | `agents/l/Dockerfile` | Phase C |
| L-gent deploy script | 📋 Planned | `infra/k8s/scripts/deploy-lgent.sh` | Phase D |
| MCP resource provider | 📋 Planned | `protocols/cli/mcp/resources.py` | Phase E |
| Cortex LLM integration | 📋 Planned | `infra/cortex/service.py` | Phase F (uses runtime/cli.py) |

---

## Context Management (`self/stream.md`)

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| `ContextWindow` (Store Comonad) | ✅ Done | `agents/d/context_window.py` | extract/extend/duplicate (41 tests) |
| `LinearityMap` | ✅ Done | `agents/d/linearity.py` | Resource classes (38 tests) |
| `ContextProjector` (Galois Connection) | ✅ Done | `agents/d/projector.py` | Not a Lens (28 tests) |
| `AdaptiveThreshold` | ✅ Done | `agents/d/projector.py` | ACON-style thresholds |
| AGENTESE `self.stream.*` | ✅ Done | `protocols/agentese/contexts/stream.py` | Full path resolver (31 tests) |
| Comonad law tests | ✅ Done | `agents/d/_tests/test_context_window.py` | Left/Right identity verified |
| MDL Compression Quality | ✅ Done | `protocols/agentese/contexts/compression.py` | Ventura Fix (43 tests) |
| Observation masking | 📋 Planned | | JetBrains pattern (in projector) |
| Incremental summarization | 📋 Planned | `agents/r/incremental.py` | Differential updates |
| `Pulse` dataclass | 📋 Planned | `agents/o/pulse.py` | Fast-lane heartbeat |
| `FastChannel` | 📋 Planned | `infra/cortex/fast_channel.py` | Log-based vitality |
| `SlowChannel` | 📋 Planned | `infra/cortex/slow_channel.py` | CRD-based signals |
| `StateCrystal` | 📋 Planned | `agents/d/crystal.py` | State checkpoints |
| `CrystallizationEngine` | 📋 Planned | `agents/d/crystallize.py` | Focus-aware |
| `CrystalReaper` | 📋 Planned | `agents/d/reaper.py` | TTL-based composting |

---

## Capital & Entropy (`void/capital.md`, `void/entropy.md`)

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| `EventSourcedLedger` | ✅ Done | `shared/capital.py` | Event-sourced capital tracking (83 tests) |
| `LedgerEvent` | ✅ Done | `shared/capital.py` | Immutable events (CREDIT, DEBIT, BYPASS, etc.) |
| `BypassToken` | ✅ Done | `shared/capital.py` | OCap capability token |
| `mint_bypass()` | ✅ Done | `shared/capital.py` | Mint bypass token |
| `CostFactor` | ✅ Done | `shared/costs.py` | Algebraic cost composition |
| `CostContext` | ✅ Done | `shared/costs.py` | Context for cost calculation |
| `ResourceBudget` | ✅ Done | `shared/budget.py` | Context manager for budgets |
| `CapitalNode` | ✅ Done | `protocols/agentese/contexts/void.py` | void.capital.* AGENTESE paths |
| `TrustGate` | ✅ Done | `agents/t/trustgate.py` | Capital-backed gate with bypass (23 tests) |
| `Proposal` | ✅ Done | `agents/t/trustgate.py` | Action to be evaluated |
| `TrustDecision` | ✅ Done | `agents/t/trustgate.py` | Gate evaluation result |
| `MetabolicEngine` | 📋 Planned | `protocols/agentese/metabolism/__init__.py` | Token thermometer |
| `FeverStream` | 📋 Planned | `protocols/agentese/metabolism/fever.py` | Background dreamer |
| `kgents capital balance` | ✅ Done | `protocols/cli/genus/c_gent.py` | Query capital (24 tests) |
| `kgents capital history` | ✅ Done | `protocols/cli/genus/c_gent.py` | Trust event history |
| `kgents capital tithe` | ✅ Done | `protocols/cli/genus/c_gent.py` | Voluntary discharge (potlatch) |
| Store Comonad persistence | ✅ Done | `agents/d/context_comonad.py` | D-gent event persistence (26 tests) |
| JudgeAgent → TrustGate | ✅ Done | `agents/t/trustgate.py` | LLM-based semantic evaluation |

---

## Optics & Modal (`self/stream.md`)

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| `Lens` protocol | 📋 Planned | `protocols/agentese/optics/__init__.py` | Bidirectional |
| `optics.structure` | 📋 Planned | `protocols/agentese/optics/standard.py` | AST/schema lens |
| `optics.surface` | 📋 Planned | `protocols/agentese/optics/standard.py` | UI lens |
| `optics.essence` | 📋 Planned | `protocols/agentese/optics/standard.py` | Embedding lens |
| Category law verification | 📋 Planned | `protocols/agentese/optics/laws.py` | Tests |
| `modal_scope` (Git-backed) | 📋 Planned | `protocols/agentese/modal/scope.py` | Branch forking |
| `ModalLogos` wrapper | 📋 Planned | `protocols/agentese/modal/logos.py` | Branch-isolated |
| `could_*`, `must_*` aspects | 📋 Planned | `protocols/agentese/modal/aspects.py` | Modal operators |
| D-gent fork (non-Git state) | 📋 Planned | `agents/d/fork.py` | Copy-on-write |

---

## I-gent v2.5: Semantic Flux (`self/interface.md`)

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| Textual app skeleton | 📋 Planned | `agents/i/app.py` | Main application |
| FluxScreen (default) | 📋 Planned | `agents/i/screens/flux.py` | Agent density field |
| WIRE overlay | 📋 Planned | `agents/i/screens/overlays/wire.py` | Hold `w` for overlay |
| BODY overlay | 📋 Planned | `agents/i/screens/overlays/body.py` | Omega proprioception |
| DensityField widget | 📋 Planned | `agents/i/widgets/density_field.py` | Block element rendering |
| FlowArrow widget | 📋 Planned | `agents/i/widgets/flow_arrow.py` | Throughput visualization |
| Waveform widget | 📋 Planned | `agents/i/widgets/waveform.py` | Processing texture |
| XYZMeter widget | 📋 Planned | `agents/i/widgets/xyz_meter.py` | O-gent health bars |
| Glitch renderer | 📋 Planned | `agents/i/widgets/glitch.py` | Zalgo/corruption effect |
| AGENTESE HUD | 📋 Planned | `agents/i/widgets/agentese_hud.py` | Path completion with arrows |
| MemoryGarden widget | 📋 Planned | `agents/i/widgets/memory_garden.py` | D-gent visualization |
| AgentObservable protocol | 📋 Planned | `shared/observable.py` | Universal agent interface |
| Registry data source | 📋 Planned | `agents/i/data/registry.py` | Agent mesh connection |
| O-gent data source | 📋 Planned | `agents/i/data/ogent.py` | Polling with ~2.2s jitter |
| State persistence | 📋 Planned | `agents/i/data/state.py` | Session cursor/layout |
| Earth theme | 📋 Planned | `agents/i/theme/earth.py` | Deep earth + pink/purple |
| Web deployment | 📋 Planned | | `textual serve` integration |
| Terrarium TUI (legacy) | 🚧 In Progress | `agents/i/terrarium_tui.py` | Will be replaced by v2.5 |

---

## Agent Separation (`agents/t-gent.md`, `agents/u-gent.md`)

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| T-gent module (testing) | ✅ Done | `agents/t/` | Types I-IV implemented |
| U-gent module (utility) | 📋 Planned | `agents/u/` | Directory doesn't exist yet |
| T/U deprecation bridge | 📋 Planned | | `__getattr__` for backwards compat |
| Tool migration (T → U) | 📋 Planned | | Move tool.py, mcp_client.py, etc. |
| Type V Adversarial (T-gent) | 📋 Planned | `agents/t/adversarial.py` | AdversarialGym |

---

## Next Actions (Priority Order)

1. **Phase 0 (Hollow Bone)** - ✅ COMPLETE
   - ResilientClient, Ghost cache, hollowed handlers, gRPC service

2. **Phase 1 (Grammar)** - ✅ COMPLETE (Phase 1.7)
   - ✅ Capital Ledger (`shared/capital.py`) - Event-sourced, 83 tests
   - ✅ Cost Functions (`shared/costs.py`) - Algebraic composition
   - ✅ Budget Manager (`shared/budget.py`) - Context manager pattern
   - ✅ AGENTESE void.capital.* paths - Wired to ledger
   - ✅ TrustGate (`agents/t/trustgate.py`) - BypassToken + JudgeAgent, 28 tests
   - ✅ CLI Commands (`protocols/cli/genus/c_gent.py`) - balance/history/tithe, 24 tests
   - ✅ Store Comonad (`agents/d/context_comonad.py`) - D-gent event persistence, 26 tests

3. **Phase 2 (Brain)** - ✅ COMPLETE (Phase 2.1)
   - ✅ LinearityMap (`agents/d/linearity.py`) - Resource classes, 38 tests
   - ✅ ContextWindow (`agents/d/context_window.py`) - Turn-level Store Comonad, 41 tests
   - ✅ ContextProjector (`agents/d/projector.py`) - Galois Connection, 28 tests
   - ✅ AdaptiveThreshold - ACON-style compression thresholds
   - ✅ AGENTESE `self.stream.*` (`protocols/agentese/contexts/stream.py`) - 31 tests
   - 📋 Modal Scope via duplicate() - Git-backed branching (Phase 2.2)
   - 📋 StateCrystal / Crystallization (Phase 2.4)

4. **Phase 3 (Body)** - 📋 PENDING
   - K8s Operators (Agent, Proposal)
   - Trust Gate with Capital
   - Cognitive Probes

5. **Phase 4 (Senses)** - 📋 PENDING
   - Dual-lane pheromones
   - Crystallization engine
   - ~~Terrarium TUI polish~~ → **I-gent v2.5 Semantic Flux**

6. **Phase 5 (Interface Renaissance)** - 📋 PENDING
   - I-gent v2.5 Core Flux (density fields, block elements)
   - WIRE/BODY overlays
   - Glitch mechanic + AGENTESE HUD
   - Web deployment via `textual serve`

---

## Verification Commands

```bash
# Check CLI hollowing
ls -la impl/claude/protocols/cli/glass.py
ls -la impl/claude/infra/cortex/

# Check K8s CRDs
ls -la impl/claude/infra/k8s/crds/

# Check proto files
ls -la impl/claude/protocols/proto/

# Run tests
cd impl/claude && pytest -q --tb=short

# Check mypy
cd impl/claude && uv run mypy --strict --explicit-package-bases .
```

---

*Last verified against codebase: 2025-12-11 (MDL Compression + 7,707 tests)*
