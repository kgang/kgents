# Chaos Engineering Baseline

> Documented failure scenarios and recovery behaviors for kgents SaaS infrastructure.

## Overview

This document captures the baseline chaos engineering scenarios and expected recovery times. These scenarios validate that the system degrades gracefully and recovers automatically.

**Scope:** Staging/development environments only. Production chaos requires explicit approval.

---

## Failure Scenarios

### Scenario 1: API Pod Termination

**Description:** Simulate pod failure by deleting an API pod.

**Expected Behavior:**
- HPA detects reduced replica count
- New pod scheduled immediately
- Traffic routed to remaining healthy pod(s)
- PDB prevents all pods from being disrupted simultaneously

**Recovery SLA:** < 30 seconds

**Test Command:**
```bash
# Get a pod name
POD=$(kubectl get pods -n kgents-triad -l app.kubernetes.io/name=kgent-api -o jsonpath='{.items[0].metadata.name}')

# Delete the pod
kubectl delete pod $POD -n kgents-triad

# Watch recovery
watch kubectl get pods -n kgents-triad -l app.kubernetes.io/name=kgent-api
```

**Expected Output:**
```
NAME                         READY   STATUS    AGE
kgent-api-xxx-abc123         1/1     Running   2s    # New pod starting
kgent-api-xxx-def456         1/1     Running   10m   # Existing pod
```

**Observed Results:**
- [ ] Recovery time: ___ seconds
- [ ] Traffic continuity: [ ] Yes [ ] No
- [ ] Errors during recovery: ___

---

### Scenario 2: NATS Leader Election

**Description:** Simulate NATS cluster leader failure to trigger leader election.

**Expected Behavior:**
- NATS cluster elects new leader (Raft consensus)
- API circuit breaker may trigger briefly
- Fallback queue buffers messages during transition
- Auto-recovery after leader election completes

**Recovery SLA:** < 60 seconds

**Test Command:**
```bash
# Find current leader (usually nats-0)
kubectl exec -n kgents-agents nats-0 -- nats-server --version

# Kill leader pod
kubectl delete pod nats-0 -n kgents-agents

# Watch cluster recovery
watch kubectl get pods -n kgents-agents -l app.kubernetes.io/name=nats
```

**Expected Output:**
```
NAME    READY   STATUS    AGE
nats-0  0/1     Init      5s    # Restarting
nats-1  1/1     Running   24h   # New leader
nats-2  1/1     Running   24h   # Follower
```

**Observed Results:**
- [ ] Recovery time: ___ seconds
- [ ] Circuit breaker activated: [ ] Yes [ ] No
- [ ] Messages lost: ___
- [ ] Fallback queue depth: ___

---

### Scenario 3: Network Partition (NATS Unreachable)

**Description:** Simulate network partition between API and NATS.

**Expected Behavior:**
- Circuit breaker opens after 3 consecutive failures
- Health endpoint shows `nats.status: circuit_open`
- Fallback queue activates, buffers up to 1000 messages
- Auto-recovery when network restored (30s recovery window)

**Recovery SLA:** < 90 seconds (after network restored)

**Test Command:**
```bash
# Apply network policy to block NATS traffic
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: chaos-block-nats
  namespace: kgents-triad
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: kgent-api
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: kgents-observability
    # NATS blocked by omission
EOF

# Monitor circuit breaker
watch 'kubectl exec -n kgents-triad deploy/kgent-api -- curl -s localhost:8000/health/saas | jq .nats'

# Remove policy to restore connectivity
kubectl delete networkpolicy chaos-block-nats -n kgents-triad
```

**Expected Output (during partition):**
```json
{
  "status": "circuit_open",
  "fallback_queue_depth": 42,
  "mode": "fallback"
}
```

**Observed Results:**
- [ ] Circuit opened after: ___ failures
- [ ] Fallback queue activated: [ ] Yes [ ] No
- [ ] Recovery time after restore: ___ seconds
- [ ] Messages in fallback queue processed: [ ] Yes [ ] No

---

### Scenario 4: Resource Exhaustion (Memory Pressure)

**Description:** Simulate memory pressure by consuming memory in the pod.

**Expected Behavior:**
- OOMKilled if limits exceeded
- Pod restarted by kubelet
- Liveness probe detects unhealthy state
- HPA may scale up if sustained

**Recovery SLA:** < 45 seconds

**Test Command:**
```bash
# This is informational - don't run in production
# Use a stress tool or allocate memory in application

# Monitor memory
kubectl top pods -n kgents-triad -l app.kubernetes.io/name=kgent-api

# Watch for OOM events
kubectl get events -n kgents-triad --field-selector reason=OOMKilled
```

**Note:** Memory exhaustion testing should be done carefully. Consider using a dedicated test pod.

**Observed Results:**
- [ ] OOMKilled at: ___ Mi
- [ ] Restart time: ___ seconds
- [ ] Traffic impact: ___

---

### Scenario 5: Observability Stack Failure

**Description:** Verify API continues operating if Prometheus/Grafana fail.

**Expected Behavior:**
- API continues serving requests
- Metrics endpoint may timeout but doesn't crash
- No impact on core functionality

**Recovery SLA:** N/A (graceful degradation)

**Test Command:**
```bash
# Scale down observability
kubectl scale deployment prometheus -n kgents-observability --replicas=0

# Verify API health
curl localhost:8000/health
curl localhost:8000/health/saas

# Restore observability
kubectl scale deployment prometheus -n kgents-observability --replicas=1
```

**Observed Results:**
- [ ] API continued operating: [ ] Yes [ ] No
- [ ] Any errors logged: ___

---

## Recovery Time Summary

| Scenario | SLA | Baseline | Status |
|----------|-----|----------|--------|
| API Pod Kill | < 30s | ___ s | [ ] Pass |
| NATS Leader Election | < 60s | ___ s | [ ] Pass |
| Network Partition | < 90s | ___ s | [ ] Pass |
| Memory Pressure | < 45s | ___ s | [ ] Pass |
| Observability Failure | N/A | N/A | [ ] Pass |

---

## Chaos Test Script

A simple script to run basic chaos scenarios:

```bash
#!/bin/bash
# chaos-test.sh - Basic chaos engineering tests
# Usage: ./chaos-test.sh <scenario>

set -e

NAMESPACE_API="kgents-triad"
NAMESPACE_NATS="kgents-agents"

case "$1" in
  api-kill)
    echo "=== Scenario: API Pod Kill ==="
    POD=$(kubectl get pods -n $NAMESPACE_API -l app.kubernetes.io/name=kgent-api -o jsonpath='{.items[0].metadata.name}')
    echo "Killing pod: $POD"
    START=$(date +%s)
    kubectl delete pod $POD -n $NAMESPACE_API

    # Wait for new pod
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kgent-api -n $NAMESPACE_API --timeout=60s
    END=$(date +%s)
    echo "Recovery time: $((END-START)) seconds"
    ;;

  nats-kill)
    echo "=== Scenario: NATS Leader Kill ==="
    echo "Killing nats-0"
    START=$(date +%s)
    kubectl delete pod nats-0 -n $NAMESPACE_NATS

    # Wait for pod ready
    kubectl wait --for=condition=ready pod/nats-0 -n $NAMESPACE_NATS --timeout=120s
    END=$(date +%s)
    echo "Recovery time: $((END-START)) seconds"
    ;;

  health-check)
    echo "=== Health Check ==="
    kubectl exec -n $NAMESPACE_API deploy/kgent-api -- curl -s localhost:8000/health/saas | jq .
    ;;

  *)
    echo "Usage: $0 {api-kill|nats-kill|health-check}"
    exit 1
    ;;
esac
```

---

## Recommendations

### Immediate
1. Run all scenarios in staging environment
2. Document baseline recovery times
3. Add chaos metrics to Grafana dashboard

### Future (Phase 10+)
1. Implement automated chaos testing in CI
2. Consider Litmus Chaos or Chaos Mesh for advanced scenarios
3. Add multi-region failover testing
4. Implement game days for production readiness

---

## References

- [NATS Clustering](https://docs.nats.io/running-a-nats-service/configuration/clustering)
- [Kubernetes Pod Disruption Budgets](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)
- [Circuit Breaker Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)

---

*Last Updated: 2025-12-14 | Phase 9: Production Hardening*
