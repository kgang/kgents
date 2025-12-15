# SaaS Deployment Checklist

> Step-by-step checklist for safe API deployments with zero downtime.

## Pre-Deployment

### 1. Code Verification

- [ ] All tests pass: `uv run pytest impl/claude`
- [ ] Security scan clean: `pip-audit`
- [ ] No HIGH/CRITICAL vulnerabilities: `trivy image kgents/api:latest`
- [ ] Code review approved

### 2. Infrastructure Check

```bash
# Verify cluster health
kubectl cluster-info
kubectl get nodes

# Check current deployment status
kubectl get pods -n kgents-triad -l app.kubernetes.io/name=kgent-api
kubectl get hpa -n kgents-triad

# Verify PDB is in place
kubectl get pdb -n kgents-triad
```

- [ ] All nodes healthy
- [ ] Current pods running (2/2)
- [ ] HPA responding
- [ ] PDB configured

### 3. Observability Ready

```bash
# Verify monitoring
kubectl get pods -n kgents-observability
```

- [ ] Prometheus scraping
- [ ] Grafana accessible
- [ ] Loki collecting logs
- [ ] Alerts configured

---

## Deployment Steps

### Step 1: Build New Image

```bash
# Build with explicit tag
docker build -t kgents/api:v1.x.x -f impl/claude/infra/k8s/images/api/Dockerfile impl/claude

# Also tag as latest
docker tag kgents/api:v1.x.x kgents/api:latest

# For Kind cluster
kind load docker-image kgents/api:v1.x.x --name kgents-triad
```

### Step 2: Update Deployment

```bash
# Option A: Update image tag in deployment.yaml
# Edit: spec.template.spec.containers[0].image: kgents/api:v1.x.x
kubectl apply -f impl/claude/infra/k8s/manifests/api/deployment.yaml

# Option B: Patch image directly
kubectl set image deployment/kgent-api \
  api=kgents/api:v1.x.x \
  -n kgents-triad
```

### Step 3: Monitor Rollout

```bash
# Watch rollout progress
kubectl rollout status deployment/kgent-api -n kgents-triad --timeout=300s

# Watch pods transition
watch kubectl get pods -n kgents-triad -l app.kubernetes.io/name=kgent-api

# Check events for issues
kubectl get events -n kgents-triad --sort-by='.lastTimestamp' | tail -20
```

**Expected Behavior:**
- New pod starts → passes startup probe
- Old pod marked for termination
- Traffic shifts to new pod
- Old pod terminates after grace period
- Repeat for each replica

### Step 4: Verify Health

```bash
# Check health endpoints
kubectl exec -n kgents-triad deploy/kgent-api -- curl -s localhost:8000/health
kubectl exec -n kgents-triad deploy/kgent-api -- curl -s localhost:8000/health/saas

# Check logs for errors
kubectl logs -n kgents-triad -l app.kubernetes.io/name=kgent-api --tail=50

# Verify version (if exposed)
curl -s http://localhost:8000/health | jq '.version'
```

- [ ] `/health` returns 200
- [ ] `/health/saas` returns expected status
- [ ] No error logs
- [ ] Correct version deployed

---

## Rollback Procedure

### Automatic Rollback (on failure)

```bash
# Kubernetes will automatically roll back if:
# - Startup probe fails
# - Liveness probe fails during rollout
# - Container crashes repeatedly
```

### Manual Rollback

```bash
# View rollout history
kubectl rollout history deployment/kgent-api -n kgents-triad

# Rollback to previous version
kubectl rollout undo deployment/kgent-api -n kgents-triad

# Rollback to specific revision
kubectl rollout undo deployment/kgent-api -n kgents-triad --to-revision=2

# Watch rollback progress
kubectl rollout status deployment/kgent-api -n kgents-triad
```

### Rollback Verification

```bash
# Confirm pods running correct image
kubectl get pods -n kgents-triad -l app.kubernetes.io/name=kgent-api -o jsonpath='{.items[*].spec.containers[0].image}'

# Verify health
kubectl exec -n kgents-triad deploy/kgent-api -- curl -s localhost:8000/health
```

---

## Post-Deployment

### 1. Monitor Metrics (15 minutes)

```bash
# Watch error rate
# In Grafana: kgents_api_request_errors_total

# Watch latency
# In Grafana: histogram_quantile(0.95, kgents_api_request_latency_seconds_bucket)
```

- [ ] Error rate stable
- [ ] Latency within SLA
- [ ] No circuit breaker activations
- [ ] Memory usage stable

### 2. Smoke Tests

```bash
# Run quick load test
k6 run --vus 10 --duration 30s impl/claude/tests/load/saas-health.js
```

- [ ] All thresholds pass
- [ ] No errors

### 3. Update Documentation

- [ ] Update changelog if needed
- [ ] Note any configuration changes
- [ ] Update runbook if procedures changed

---

## Emergency Procedures

### Complete Outage

```bash
# Scale to known good state
kubectl rollout undo deployment/kgent-api -n kgents-triad

# If rollback fails, scale down and investigate
kubectl scale deployment/kgent-api -n kgents-triad --replicas=0

# Check events and logs
kubectl describe deployment/kgent-api -n kgents-triad
kubectl logs -n kgents-triad -l app.kubernetes.io/name=kgent-api --previous
```

### Partial Degradation

```bash
# Scale up for capacity
kubectl scale deployment/kgent-api -n kgents-triad --replicas=4

# Check which pods are failing
kubectl get pods -n kgents-triad -l app.kubernetes.io/name=kgent-api -o wide

# Remove problematic pods
kubectl delete pod <pod-name> -n kgents-triad
```

---

## Deployment Strategy Reference

Current configuration (`deployment.yaml`):

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # Allow 1 extra pod during rollout
    maxUnavailable: 0  # Never reduce below desired count
```

This ensures:
- Zero downtime during deployments
- Gradual traffic shift to new pods
- Automatic rollback on probe failures

---

## Checklist Summary

### Pre-Deployment
- [ ] Tests passing
- [ ] Security scans clean
- [ ] Cluster healthy
- [ ] Monitoring ready

### During Deployment
- [ ] Image built and loaded
- [ ] Deployment updated
- [ ] Rollout successful
- [ ] Health verified

### Post-Deployment
- [ ] Metrics stable (15 min)
- [ ] Smoke tests pass
- [ ] Documentation updated

---

*Last Updated: 2025-12-14 | Phase 9: Production Hardening*
