# K-Terrarium Phase 3: Agent Operator

**Date**: 2025-12-10
**Status**: Complete
**Tests**: 33 passing

## What Was Built

Agent Operator - CRD-driven deployment of agents to Kubernetes.

### Core Components

| File | Purpose |
|------|---------|
| `infra/k8s/manifests/agent-crd.yaml` | Agent CRD definition (kgents.io/v1) |
| `infra/k8s/operator.py` | Reconciliation loop (AgentSpec → Deployment + Service) |
| `infra/k8s/spec_to_crd.py` | Spec-to-CRD generator + git hook support |
| `protocols/cli/handlers/infra.py` | `apply` and `crd` CLI commands |

### Key Design Decisions

1. **In-Cluster Operator**: Mirrors K8s control plane pattern (per user request)

2. **Git Hooks for Spec Changes**: Post-commit hook regenerates CRDs when `spec/agents/*.md` changes

3. **Simple CRD Versioning**: Direct `v1` (no alpha stages for solo dev project)

4. **Agent CRD Schema**:
   ```yaml
   apiVersion: kgents.io/v1
   kind: Agent
   spec:
     genus: B           # Required: single letter or "Psi"
     image: ...         # Container image
     replicas: 1        # Pod count
     resources:
       cpu: 100m
       memory: 256Mi
     sidecar:
       enabled: true    # D-gent sidecar for state
     entrypoint: ...    # Python module
     config: {}         # Agent-specific config
     networkPolicy:
       allowEgress: false
       allowedPeers: [L, F]
   ```

5. **Generated Resources**:
   - **Deployment**: Logic container + optional D-gent sidecar
   - **Service**: ClusterIP on port 8080
   - **NetworkPolicy**: Egress restrictions if configured

6. **Security Posture**:
   - runAsNonRoot: true
   - readOnlyRootFilesystem: true (except sidecar for state)
   - allowPrivilegeEscalation: false
   - capabilities.drop: ALL

### CLI Usage

```bash
# Install CRD
kgents infra crd

# Deploy single agent
kgents infra apply b-gent

# Deploy from file
kgents infra apply my-agent.yaml

# Deploy all from spec/
kgents infra apply --all

# Install git hook
python -m impl.claude.infra.k8s.spec_to_crd --install-hook
```

### Spec Frontmatter Format

`spec/agents/b-gent.md`:
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

# B-gent

The Banker agent for token economics.
```

### Test Coverage

- `test_operator.py`: 18 tests (AgentSpec, Deployment generation, operator)
- `test_spec_to_crd.py`: 15 tests (parsing, generation, git hook)

---

## Instructions for Next Session

### Phase 4: B-gent Economics Integration

The next phase connects B-gent's token budget to Kubernetes ResourceQuotas.

**Priority Tasks**:
1. Map B-gent `AgentBudget` to K8s `ResourceQuota`
2. Implement budget allocation API
3. Handle throttling/eviction events
4. Add `kgents resources` command for usage monitoring

**Key Files to Create/Modify**:
```
impl/claude/infra/k8s/
├── resources.py          # ResourceQuota helpers
└── budget_controller.py  # B-gent ↔ K8s bridge

impl/claude/agents/b/
└── k8s_integration.py    # B-gent K8s adapter
```

**Reference**: See `docs/k-terrarium-plan.md` Section 4 (B-gent Economics Integration)

### Quick Start Commands

```bash
# Verify cluster running
kgents infra status

# Install CRD
kgents infra crd

# Deploy an agent
kgents infra apply b-gent

# Check deployment
kubectl get agents -n kgents-agents
kubectl get pods -n kgents-agents

# Run Phase 3 tests
pytest impl/claude/infra/k8s/_tests/test_operator.py -v
pytest impl/claude/infra/k8s/_tests/test_spec_to_crd.py -v
```

### Open Questions for Phase 4

1. Should budget changes trigger pod restarts or live updates?
2. How to handle burst capacity (temporary over-budget)?
3. Budget inheritance for sidecar containers?
