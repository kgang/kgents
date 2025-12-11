# HYDRATE: K8s Phase 1 Ready

**Status**: K8s Phase 0 COMPLETE | **Date**: 2025-12-11

---

## Just Completed: K8s Phase 0 ("The Hollow Body")

### Phase 0 Tasks (ALL DONE)

| Task | Status | Deliverable |
|------|--------|-------------|
| CRD Definitions | COMPLETE | 5 CRDs: Agent, Pheromone, Memory, Umwelt, **Proposal** |
| Proposal CRD + Operator | COMPLETE | Risk-aware change governance with T-gent integration |
| Daemon Auto-Start | COMPLETE | `kgents daemon start|stop|status|install|logs`, Mac launchd |
| CRD Installer CLI | COMPLETE | `kgents infra crd [--apply|--list|--verify]` |

### Test Results

- **107 operator tests** pass (50 proposal + 34 agent + 23 pheromone)
- **26 daemon tests** pass

### New Files Created

```
protocols/cli/handlers/daemon.py           # Cortex daemon lifecycle (launchd)
protocols/cli/handlers/_tests/test_daemon.py  # 26 tests
infra/k8s/crds/proposal-crd.yaml           # 15 change types, cumulative risk
infra/k8s/operators/proposal_operator.py   # Risk calculation, velocity penalty
```

---

## Current Priority: K8s Phase 1 ("The Nervous System")

From `plans/k8-gents-implementation.md`:

### Phase 1 Tasks

| # | Task | Description | Deliverable |
|---|------|-------------|-------------|
| 1.1 | Ghost Protocol | Local file cache at `~/.kgents/ghost/` | `protocols/cli/ghost_cache.py` |
| 1.2 | Symbiont Injector | Auto-inject D-gent/K-gent sidecars | `infra/k8s/operators/symbiont_injector.py` |
| 1.3 | Logos Resolver | AGENTESE path → K8s operation | `infra/cortex/resolver.py` |
| 1.4 | Cognitive Probes | LLM-aware health checks | `infra/k8s/probes/cognitive.py` |

### Phase 1 Complete When:

- [ ] Ghost cache created on first successful connection
- [ ] `kgents status` shows `[GHOST]` when cluster unavailable
- [ ] Agents have D-gent memory sidecar auto-injected
- [ ] Cognitive probes detect "garbage output" as unhealthy

---

## Existing K8s Infrastructure

```
infra/k8s/
├── crds/
│   ├── agent-crd.yaml        # Agent deployment spec
│   ├── pheromone-crd.yaml    # Stigmergic coordination
│   ├── memory-crd.yaml       # D-gent persistence
│   ├── umwelt-crd.yaml       # Observer context
│   └── proposal-crd.yaml     # Risk-aware change governance (NEW)
├── operators/
│   ├── __init__.py           # Exports all operators
│   ├── agent_operator.py     # Agent CR → Deployment + Service
│   ├── pheromone_operator.py # Decay logic with half-life model
│   └── proposal_operator.py  # Risk calculation, T-gent integration (NEW)
├── tether.py                 # Agent attachment with signal forwarding
└── manifests/
    └── cortex-daemon-deployment.yaml
```

---

## Key Decisions (Resolved)

| Decision | Resolution |
|----------|------------|
| Composition over network | Durable Execution Engine (Temporal patterns) |
| T-gent (Immune System) | ValidatingAdmissionWebhook (K8s physics) |
| Ghost Staleness | Adaptive thresholds, REFUSE very stale data |
| Cortex Daemon | Auto-start on CLI use, Mac/launchd focus |
| CRD Count | 5 CRDs (Agent, Pheromone, Memory, Umwelt, Proposal) |

---

## Start Here

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Verify Phase 0 work
python3.11 -m pytest infra/k8s/operators/_tests/ -v  # 107 tests
python3.11 -m pytest protocols/cli/handlers/_tests/test_daemon.py -v  # 26 tests

# Test daemon (if not already running)
python3.11 -m infra.cortex.daemon --port 50051 &

# Check CRD files
ls infra/k8s/crds/

# Read full plan
cat /Users/kentgang/git/kgents/plans/k8-gents-implementation.md
```

---

## Next Session Prompt

```
K8s Phase 0 is COMPLETE. We have:
- 5 CRDs installed (Agent, Pheromone, Memory, Umwelt, Proposal)
- Daemon handler with Mac launchd integration
- 133 passing tests (107 operator + 26 daemon)

Phase 1 ("The Nervous System") is next. Choose where to start:

1. **Ghost Protocol** (1.1)
   - Create ~/.kgents/ghost/ local file cache
   - Implement 3-layer fallback: gRPC → Ghost → kubectl
   - Add staleness detection with adaptive thresholds
   - File: `protocols/cli/ghost_cache.py`

2. **Symbiont Injector** (1.2)
   - Auto-inject D-gent memory sidecar into agent pods
   - Use Mutating Admission Webhook pattern
   - File: `infra/k8s/operators/symbiont_injector.py`

3. **Logos Resolver** (1.3)
   - Map AGENTESE paths to K8s operations
   - Integrate with GlassClient for caching
   - File: `infra/cortex/resolver.py`

4. **Cognitive Probes** (1.4)
   - LLM-aware health checks (detect garbage output)
   - Standard Cognitive Unit (SCU) implementation
   - File: `infra/k8s/probes/cognitive.py`

RECOMMENDED: Start with Ghost Protocol (1.1) - it's foundational for offline resilience and the other components depend on it.

Key files:
- plans/k8-gents-implementation.md (full plan)
- protocols/cli/glass.py (GlassClient exists, needs Ghost integration)
- spec/principles.md (Graceful Degradation, Transparent Infrastructure)

Principles to follow:
- Transparent Infrastructure: Tell users what's happening
- Graceful Degradation: Never fail completely
- Joy-Inducing: Make offline mode feel natural

Work with relentless enthusiasm, attention to detail, mathematical rigor, and most importantly: joy.
```

---

## Mypy Status

**Current**: 209 strict errors baselined (97% reduction from initial 7,516)

```bash
# Check mypy status
cd /Users/kentgang/git/kgents/impl/claude
uv run mypy --strict --explicit-package-bases agents/ bootstrap/ runtime/ 2>&1 | uv run mypy-baseline filter
```

---

## Cross-References

- **Spec**: `spec/k8-gents/README.md`
- **Full Plan**: `plans/k8-gents-implementation.md`
- **Principles**: `spec/principles.md`
- **Glass Terminal**: `protocols/cli/glass.py`, `infra/cortex/service.py`
- **Existing Operators**: `infra/k8s/operators/`

---

*"The body is hollow. Now we connect the nerves."*
