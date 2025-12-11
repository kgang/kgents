# HYDRATE.md - kgents Session Context

**Status**: 6,945+ tests | Branch: `main`

## Current: K-Terrarium Phase 4 (Live Reload Dev Mode)

Kubernetes-native agent isolation with live reload development experience.

**K-Terrarium CLI** (working):
```bash
kgents infra init            # Create Kind cluster (idempotent) ~45s
kgents infra status          # Show cluster state + pods
kgents infra stop            # Pause cluster (docker pause)
kgents infra start           # Resume cluster
kgents infra destroy         # Remove cluster (--force to skip confirm)
kgents infra deploy          # Deploy ping-agent POC
kgents infra crd             # Install Agent CRD
kgents infra apply <agent>   # Deploy agent via CRD
kgents infra cleanup         # Auto-cleanup failed deployments
kgents exec --code "..."     # Q-gent disposable execution
kgents dev <agent>           # Live reload development mode
kgents dev <agent> --attach  # Attach for interactive debugging
kgents dev --status          # Show dev mode status
kgents dev --stop            # Stop all dev pods
```

**Phase 4: Live Reload Dev Mode** (NEW - 23 tests):
- `infra/k8s/dev_mode.py` - DevMode, DevPodSpec, file watcher integration
- `protocols/cli/handlers/dev.py` - `kgents dev` CLI handler
- Volume mounting source code into containers
- Automatic reload on file changes
- Streaming logs to terminal
- Interactive debugging with `--attach`

**Phase 3: Agent Operator** (33 tests):
- `infra/k8s/manifests/agent-crd.yaml` - Agent CRD (kgents.io/v1)
- `infra/k8s/operator.py` - Reconciliation loop (AgentSpec → Deployment + Service)
- `infra/k8s/spec_to_crd.py` - Spec-to-CRD generator + git hook support
- `protocols/cli/handlers/infra.py` - Extended with `apply` and `crd` commands

**Agent CRD Features**:
- **Spec-Driven**: Define agents in `spec/agents/*.md` with YAML frontmatter
- **Auto-Deploy**: `kgents infra apply b-gent` creates Deployment + Service
- **D-gent Sidecar**: Optional sidecar container for state management
- **NetworkPolicy**: Configurable peer-to-peer communication
- **In-Cluster Operator**: Mirrors K8s control plane pattern
- **Pre-Deploy Validation**: Image existence + entrypoint checks (prevents CrashLoopBackOff)
- **Auto-Cleanup**: `kgents infra cleanup` removes failed deployments

```bash
# Deploy single agent (PLACEHOLDER mode - safe, no image needed)
kgents infra apply b-gent

# Preview manifests without deploying
kgents infra apply b-gent --dry-run

# Deploy with real agent code (requires built image)
kgents infra apply b-gent --full

# Cleanup failed deployments (CrashLoopBackOff, ImagePullBackOff)
kgents infra cleanup

# Deploy from YAML file
kgents infra apply my-agent.yaml

# Deploy all agents from spec/
kgents infra apply --all

# Install git hook for auto-generation
python -m impl.claude.infra.k8s.spec_to_crd --install-hook
```

**Spec Frontmatter Format** (`spec/agents/b-gent.md`):
```yaml
---
genus: B
name: B-gent
resources:
  cpu: 100m
  memory: 256Mi
sidecar: true
entrypoint: agents.b.main
networkPolicy:
  allowedPeers: [L, F]
---
```

**K-Terrarium Phases**:
| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Foundation (Kind bootstrap, CLI, POC agent) | Complete |
| 2 | Q-gent (disposable execution) | Complete |
| 3 | Agent Operator (CRD-driven deploy) | Complete |
| 4 | Live Reload Dev Mode | **Complete** |
| 5 | Conversation Loop (chat with agents) | Pending |
| 6 | Feedback Loop (O-gent observation) | Pending |

**Quick Demo**:
```bash
kgents infra init          # Create cluster
kgents infra crd           # Install Agent CRD
kgents infra apply b-gent  # Deploy B-gent (placeholder mode)
kgents dev b-gent          # Start B-gent with live reload
# Edit impl/claude/agents/b/main.py -> changes auto-reload
kgents dev --stop          # Stop dev mode
```

---

## DevEx V4 (Complete through Phase 2)

**CLI Commands**:
```bash
# Phase 1: Foundation
kgents status           # Cortex health at a glance
kgents dream            # LucidDreamer morning briefing
kgents map              # M-gent HoloMap visualization
kgents signal           # SemanticField state

# Phase 2: Sensorium
kgents ghost            # Project to .kgents/ghost/
kgents ghost --daemon   # Background projection
```

**DevEx V4 Phases**:
| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Foundation (CLI entry points) | Complete |
| 2 | Sensorium (.kgents/ghost/) | Complete |
| 3 | Neural Link (keystroke dynamics) | Pending |
| 4 | Shadow (speculative execution) | Pending |
| 5 | Rituals (calibration/confessional) | Pending |

**Phase 1 Files** (CLI handlers):
- `protocols/cli/handlers/status.py` - CortexDashboard CLI
- `protocols/cli/handlers/dream.py` - LucidDreamer CLI
- `protocols/cli/handlers/map.py` - HoloMap CLI
- `protocols/cli/handlers/signal.py` - SemanticField CLI

**Phase 2 Files** (Sensorium):
- `protocols/cli/devex/ghost_writer.py` - Living Filesystem projection
- `protocols/cli/handlers/ghost.py` - Ghost CLI handler

**Feedback Loops (Meta-Bootstrap)**:
| Loop | Signal | Storage |
|------|--------|---------|
| Test Flinch | pytest failures | `FlinchStore` → ITelemetryStore + JSONL |
| CI Signals | GitHub Actions | `.kgents/ghost/ci_signals.jsonl` |
| Git Crystal | git log/diff | Native git |

**Quick Commands**:
```bash
git log --oneline --since="8 hours ago"  # Session narrative
git diff --stat HEAD~10                   # Churn map
cat .kgents/ghost/test_flinches.jsonl | tail -5  # Recent flinches
```

---

## Completed Systems

### Instance DB - Bicameral Engine (532 tests)

| Phase | Component | Key Files |
|-------|-----------|-----------|
| 1-2 | Core + Synapse + Hippocampus | `instance_db/{synapse,hippocampus}.py` |
| 3 | D-gent Adapters + Bicameral | `agents/d/{bicameral,infra_backends}.py` |
| 4 | Composting + Lethe | `instance_db/{compost,lethe}.py` |
| 5 | Lucid Dreaming + Neurogenesis | `instance_db/{dreamer,neurogenesis}.py` |
| 6 | Observability + Dashboard | `agents/o/cortex_observer.py`, `agents/w/cortex_dashboard.py` |

**Quick Start**:
```python
# Bicameral Memory (Left=relational, Right=vector)
bicameral = create_bicameral_memory(relational, vector, embedder, auto_heal_ghosts=True)
results = await bicameral.recall("query")  # Ghost memories auto-healed

# Synapse (Active Inference)
synapse = Synapse(store, SynapseConfig(surprise_threshold=0.5, flashbulb_threshold=0.9))
await synapse.fire(signal)  # Routes: flashbulb (>0.9), fast (>0.5), batch (<0.5)

# LucidDreamer (Interruptible maintenance)
dreamer = create_lucid_dreamer(synapse, hippocampus)
report = await dreamer.rem_cycle()
```

### Semantic Field (71 tests)

Stigmergic coordination via pheromones - agents emit/sense signals without direct imports.

| Agent | Emits | Senses |
|-------|-------|--------|
| Psi | METAPHOR | - |
| F | INTENT | METAPHOR |
| J | WARNING | - |
| B | OPPORTUNITY, SCARCITY | - |
| M | MEMORY | MEMORY |
| N | NARRATIVE | NARRATIVE |
| L | CAPABILITY | CAPABILITY |
| O | - | All types |

```python
field = create_semantic_field()
emitter = create_psi_emitter(field)
emitter.emit_metaphor("source", "target", strength=0.85, position=pos)
```

### M-gent Cartography (157 tests)

Memory-as-Orientation: HoloMap, Attractors, Desire Lines, Voids, Foveation.

```python
cartographer = create_cartographer(vector_search, trace_store)
holo_map = await cartographer.invoke(context_vector, Resolution.ADAPTIVE)
# → landmarks, desire_lines, voids, horizon
```

### W-gent Interceptors (125 tests)

Pipeline: Safety(50) → Metering(100) → Telemetry(200) → Persona(300)

---

## Agent Quick Reference

| Agent | Purpose | Key File |
|-------|---------|----------|
| B | Token economics | `agents/b/metered_functor.py` |
| D | State/Memory | `agents/d/bicameral.py` |
| E | Thermodynamic evolution | `agents/e/cycle.py` |
| I | Interface/TUI | `agents/i/semantic_field.py` |
| K | Kent simulacra | `agents/k/persona.py` |
| L | Semantic search | `agents/l/semantic_registry.py` |
| M | Context cartography | `agents/m/cartographer.py` |
| N | Narrative traces | `agents/n/chronicle.py` |
| O | Observation | `agents/o/observer.py` |
| Psi | Metaphor solving | `agents/psi/engine.py` |
| Q | Quartermaster (K8s exec) | `agents/q/quartermaster.py` |
| W | Wire protocol | `agents/w/bus.py` |

---

## Commands

```bash
pytest -m "not slow" -q              # Fast tests, quiet
pytest impl/claude/agents/d/ -v      # Specific agent
kgents check .                       # Validate
cd impl/claude && uv run mypy .      # Type check (~766 errors, gradual cleanup)
```

---

## Coding Gotchas

| Issue | Fix |
|-------|-----|
| Python 3.12 syntax | Use `Generic[A]` + `TypeVar`, not `class Foo[A]:` |
| Cross-agent imports | Use `*_integration.py` files or SemanticField |
| Forward refs | `from __future__ import annotations` + `TYPE_CHECKING` |

**Foundational agents** (can be imported anywhere): `shared`, `a`, `d`, `l`, `c`

---

## Tech Debt Inventory

**Mypy**: ~766 type errors (run `cd impl/claude && uv run mypy .`). Most are annotation issues, not runtime bugs. Critical fixes done:
- None access in `redis_agent.py` - added `_require_client` property
- Operator error in `breath.py` - fixed Optional handling
- Wrong parameter names in `infra/providers/__init__.py`

**74 TODOs** across 33 files. Key clusters:

| Area | Count | Notes |
|------|-------|-------|
| J-gent templates | 8 | `templates.py` - placeholder implementations |
| T-gent MCP | 6 | `mcp_client.py`, `permissions.py` - HTTP transport, D/W-gent integration |
| CLI membrane | 3 | `membrane_cli.py` - history/persistence TODO |
| Concept context | 1 | `concept.py:452` - core ops unimplemented |

**56 skipped tests** (graceful): Redis/SQL backends, DSPy, external LLM deps.

**Low-priority**:
- ~289 `NotImplementedError`/`pass` stubs (many are intentional protocol placeholders)
- J-gent `templates.py` generates TODOs by design (JIT compilation markers)
