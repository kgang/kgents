# Continuation: Terrarium Phase 3 QA with Real Agent Deployment

## Context

Terrarium Phase 3 (Metrics Emission) is implemented:
- MetricsPanel widget with pressure/flow/temperature gauges
- LiveMetricsPanel in TerrariumTextualApp
- WebSocket integration for live metrics
- DensityField integration for temperature-based activity
- 637 I-gent tests passing

**Problem**: The TUI shows no data because no agents are deployed to the cluster.

## Current Cluster State

```bash
kgents infra status  # Cluster: kgents-local (RUNNING)
kubectl get pods -n kgents-agents  # No resources
```

## Deployment Readiness Audit

| Agent | Deployable | Missing |
|-------|-----------|---------|
| U-gent | YES | Nothing - full stack ready |
| D-gent | YES | Nothing - sidecar ready |
| L-gent | YES | PostgreSQL must be deployed first |
| Terrarium | YES | Nothing - gateway ready |
| K-gent | NO | Server, Dockerfile, Manifest |
| Ping Agent | YES | Minimal POC |

## Phase 3 QA Tasks

### Task 1: Deploy Ping Agent (POC)

Simplest test - verify basic deployment flow:

```bash
kubectl apply -f impl/claude/infra/k8s/manifests/ping-agent.yaml
kubectl get pods -n kgents-agents -w
```

Expected: Pod running, health check passing.

### Task 2: Deploy U-gent + D-gent

Full stack deployment with state sidecar:

```bash
# Build images
docker build -t kgents/ugent:latest -f impl/claude/infra/k8s/images/ugent/Dockerfile .
docker build -t kgents/dgent:latest -f impl/claude/infra/k8s/images/dgent/Dockerfile .

# Load into Kind
kind load docker-image kgents/ugent:latest --name kgents-local
kind load docker-image kgents/dgent:latest --name kgents-local

# Deploy
kubectl apply -f impl/claude/infra/k8s/manifests/agents/agent-state-pvc.yaml
kubectl apply -f impl/claude/infra/k8s/manifests/agents/ugent-deployment.yaml
kubectl apply -f impl/claude/infra/k8s/manifests/agents/ugent-service.yaml

# Verify
kubectl get pods -n kgents-agents
kubectl logs -n kgents-agents deployment/ugent -c ugent
```

### Task 3: Deploy Terrarium Gateway

The observability hub that feeds the TUI:

```bash
# Build Terrarium image
docker build -t kgents/terrarium:latest -f impl/claude/protocols/terrarium/Dockerfile .
kind load docker-image kgents/terrarium:latest --name kgents-local

# Apply AgentServer CRD and create Terrarium instance
kubectl apply -f impl/claude/infra/k8s/crds/agentserver-crd.yaml
# Create AgentServer CR (or use operator)
```

### Task 4: Verify TUI Shows Data

```bash
# Port-forward Terrarium
kubectl port-forward -n kgents-agents svc/terrarium 8080:8080 &

# Open TUI
kgents observe
```

Expected:
- Agents panel shows U-gent
- Metrics panel shows pressure/flow/temperature
- DensityField renders activity based on temperature

### Task 5: K-gent Deployment (Stretch Goal)

K-gent needs server wrapper before deployment:

1. Create `agents/k/server.py` (FastAPI wrapper for KgentAgent)
2. Create `infra/k8s/images/kgent/Dockerfile`
3. Create `manifests/agents/kgent-deployment.yaml`
4. Wire Morpheus for LLM-based dialogue

## Blocking Issues

### Issue 1: No Terrarium Server Entry Point

The Terrarium gateway needs a proper entry point. Check:
- `protocols/terrarium/server.py` - Does it exist and work?
- `protocols/terrarium/__main__.py` - For `python -m protocols.terrarium`

### Issue 2: Terrarium Manifest Missing

Need to create deployment manifest or use AgentServer CRD + operator.

### Issue 3: Image Build Context

Dockerfiles assume specific build context. Ensure building from repo root:
```bash
docker build -t kgents/ugent:latest -f impl/claude/infra/k8s/images/ugent/Dockerfile .
```

## Success Criteria

- [ ] Ping agent running in cluster
- [ ] U-gent + D-gent running with health checks passing
- [ ] Terrarium gateway running and accepting WebSocket connections
- [ ] `kgents observe` shows live agent data
- [ ] Metrics panel shows pressure/flow/temperature updating
- [ ] DensityField activity correlates with agent temperature

## Next Steps After QA

1. Fix any deployment issues discovered
2. Update skill doc with fixes
3. Proceed to K-gent server wrapper implementation
4. Document end-to-end deployment in README

## Files Modified in This Session

- `agents/i/widgets/metrics_panel.py` (NEW)
- `agents/i/widgets/_tests/test_metrics_panel.py` (NEW)
- `agents/i/widgets/__init__.py` (exports)
- `agents/i/terrarium_tui.py` (LiveMetricsPanel, WebSocket integration)
- `agents/a/_tests/test_functor.py` (registry isolation fix)
- `plans/skills/deploying-agent.md` (NEW)

## Test Commands

```bash
# Run all I-gent tests (should be 637 pass)
uv run pytest agents/i/ -v

# Run metrics panel tests
uv run pytest agents/i/widgets/_tests/test_metrics_panel.py -v

# Run terrarium source tests
uv run pytest agents/i/data/_tests/test_terrarium_source.py -v
```
