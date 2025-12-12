# Implementation Status Matrix

> Last updated: 2025-12-11

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
| Agent Operator | 📋 Planned | `infra/k8s/operators/agent_operator.py` | Use kopf |
| Proposal Operator | 📋 Planned | `infra/k8s/operators/proposal_operator.py` | Risk calculation |
| T-gent Webhook | 📋 Planned | | ValidatingAdmissionWebhook |
| Cortex daemon deployment | ✅ Done | `infra/k8s/manifests/cortex-daemon-deployment.yaml` | |
| Tether Protocol | ✅ Done | `infra/k8s/tether.py` | Agent tethering |
| Cognitive Probes | 📋 Planned | | LLM health checks |
| Durable Execution | 📋 Planned | | CRD state machine |
| Dream Cycle Operator | 📋 Planned | | Low-load self-optimization |
| Terrarium TUI | 🚧 In Progress | `agents/i/terrarium_tui.py` | Basic structure exists |
| Visual Stigmergy (heatmap) | 📋 Planned | | Pheromone visualization |
| Seance Mode | 📋 Planned | | Time-travel debugging |

---

## Context Management (`self/stream.md`)

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| `ContextWindow` (Store Comonad) | 📋 Planned | `agents/d/context_comonad.py` | extract/extend/duplicate |
| Comonad law tests | 📋 Planned | `agents/d/_tests/test_comonad_laws.py` | Property-based |
| `ContextProjector` (Galois Connection) | 📋 Planned | `agents/d/projector.py` | Not a Lens |
| `LinearityMap` | 📋 Planned | `agents/d/linearity.py` | Resource classes |
| Observation masking | 📋 Planned | | JetBrains pattern |
| Incremental summarization | 📋 Planned | `agents/r/incremental.py` | Differential updates |
| Adaptive thresholds | 📋 Planned | `agents/d/adaptive.py` | ACON-style |
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
| `CapitalLedger` | 📋 Planned | `shared/capital.py` | Social capital tracking |
| `TrustEvent` | 📋 Planned | `shared/capital.py` | Trust history |
| `BypassResult` | 📋 Planned | `shared/capital.py` | Fool's Bypass result |
| `fool_bypass()` | 📋 Planned | `shared/capital.py` | Spend capital to bypass |
| `TrustGate` (with Capital) | 📋 Planned | `infra/k8s/operators/trust_gate.py` | Integrated evaluation |
| `ResourceToken` | 📋 Planned | `shared/accounting.py` | Runtime accounting |
| `Ledger` | 📋 Planned | `shared/accounting.py` | Token ledger |
| `MetabolicEngine` | 📋 Planned | `protocols/agentese/metabolism/__init__.py` | Token thermometer |
| `FeverStream` | 📋 Planned | `protocols/agentese/metabolism/fever.py` | Background dreamer |
| `kgents tithe` command | 📋 Planned | `protocols/cli/handlers/tithe.py` | Voluntary discharge |
| `kgents capital balance` | 📋 Planned | | Query capital |
| `kgents capital history` | 📋 Planned | | Trust event history |

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

2. **Phase 1 (Grammar)** - 📋 NEXT
   - Resource Accounting (`shared/accounting.py`)
   - Capital Ledger (`shared/capital.py`)
   - AGENTESE path registry enhancement

3. **Phase 2 (Brain)** - 📋 PENDING
   - Store Comonad implementation
   - ContextProjector
   - Modal Scope via duplicate()

4. **Phase 3 (Body)** - 📋 PENDING
   - K8s Operators (Agent, Proposal)
   - Trust Gate with Capital
   - Cognitive Probes

5. **Phase 4 (Senses)** - 📋 PENDING
   - Dual-lane pheromones
   - Crystallization engine
   - Terrarium TUI polish

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

*Last verified against codebase: 2025-12-11*
