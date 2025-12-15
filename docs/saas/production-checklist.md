# SaaS Production Readiness Checklist

> Pre-launch verification for kgents SaaS infrastructure.

## Overview

This checklist ensures all critical systems are properly configured and secured before production launch.

**Legend:**
- `[x]` Complete
- `[ ]` Pending
- `[!]` Blocking (must fix before launch)
- `[-]` N/A or deferred

---

## 1. Secrets Management

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| All secrets in K8s Secrets (not ConfigMaps) | [x] | ops | `kgents-api-secrets` |
| OPENMETER_API_KEY stored securely | [x] | ops | K8s Secret |
| STRIPE_API_KEY stored securely | [x] | ops | K8s Secret |
| STRIPE_WEBHOOK_SECRET stored securely | [x] | ops | K8s Secret |
| No secrets in git history | [x] | dev | Verified |
| Secrets rotated within 90 days | [ ] | ops | Schedule rotation |
| Rotation policy documented | [x] | ops | See runbook.md |

### Required Environment Variables

```bash
# In kgents-api-secrets
OPENMETER_API_KEY=om_live_xxx
STRIPE_API_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Optional (with defaults)
REDIS_URL=redis://triad-redis.kgents-triad.svc.cluster.local:6379
NATS_SERVERS=nats://nats.kgents-agents.svc.cluster.local:4222
NATS_ENABLED=true
```

---

## 2. Network Policies

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| NATS cluster isolated | [x] | ops | `manifests/network-policies/nats-policy.yaml` |
| Redis isolated to triad namespace | [x] | ops | `manifests/network-policies/redis-policy.yaml` |
| API ingress rules defined | [ ] | ops | Kong gateway in place |
| Default deny policies | [x] | ops | `manifests/network-policies/default-deny.yaml` |

### Recommended Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nats-access
  namespace: kgents-agents
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: nats
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kgents.io/tier: gateway
      ports:
        - port: 4222
```

---

## 3. Resource Limits

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| CPU/memory limits on NATS pods | [x] | ops | See statefulset.yaml |
| CPU/memory limits on API pods | [x] | ops | 100m-500m CPU, 256Mi-512Mi memory |
| PodDisruptionBudget for NATS | [x] | ops | `manifests/nats/pdb.yaml` minAvailable: 2 |
| HPA for API | [x] | ops | Scale on CPU 70%, 2-10 replicas |
| LimitRange in kgents-agents | [x] | ops | default 256Mi/100m |

### Current NATS Resources

```yaml
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 1Gi
```

### Recommended PDB

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: nats-pdb
  namespace: kgents-agents
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: nats
```

---

## 4. Observability

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Metrics endpoint exposed | [x] | dev | `/metrics` on API |
| Prometheus scraping | [x] | ops | OTEL collector + direct |
| Alerting rules deployed | [x] | ops | 8 alerts configured |
| Grafana dashboard imported | [x] | ops | dashboard-saas.json |
| Log aggregation | [x] | ops | Loki + Promtail deployed (Phase 8). Grafana datasource configured. |
| Distributed tracing | [x] | ops | Tempo + OTEL |

### Active Alerts

| Alert | Severity | Condition |
|-------|----------|-----------|
| NATSCircuitOpen | warning | Circuit open 5m |
| NATSCircuitOpenCritical | critical | Circuit open 15m |
| NATSPodNotReady | critical | Pod not ready 5m |
| OpenMeterFlushErrors | warning | Error rate > 0.1/5m |
| OpenMeterBufferFull | warning | Buffer > 1000 events |
| StripeWebhookErrors | warning | Error rate > 0.1/5m |
| HighAPILatency | warning | p95 > 2s for 5m |

---

## 5. Disaster Recovery

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| NATS data backup strategy | [x] | ops | Daily CronJob backup (Phase 9) |
| Circuit breaker recovery | [x] | dev | Auto-recover after 30s |
| Fallback queue strategy | [x] | dev | In-memory queue during outage |
| Idempotency store redundancy | [x] | dev | Redis + in-memory fallback |
| Runbook documented | [x] | ops | docs/saas/runbook.md |
| Rollback procedures | [x] | ops | Blue/green with instant rollback |
| Chaos baseline documented | [x] | dev | docs/saas/chaos-baseline.md |

### Recovery Procedures

1. **NATS Failure**: Circuit breaker opens, fallback queue buffers events (max 1000)
2. **Redis Failure**: Automatic fallback to in-memory idempotency store
3. **OpenMeter Failure**: Buffer continues, flush retries with exponential backoff
4. **Stripe Webhook Failure**: Events redelivered by Stripe for 72h

---

## 6. Load Testing

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Baseline throughput documented | [x] | dev | 478 req/s achieved (target 100). See docs/saas/load-test-baseline.md |
| OpenMeter rate limits known | [ ] | ops | Check account limits |
| NATS message rate tested | [ ] | dev | Target: 1000 msg/s |
| Memory leak testing | [x] | dev | Soak test script ready (Phase 9). See docs/saas/soak-test-baseline.md |
| Circuit breaker stress test | [x] | dev | Chaos test script (Phase 9). See docs/saas/chaos-baseline.md |

### Recommended Tests

```bash
# k6 load test for /health/saas
k6 run --vus 50 --duration 5m impl/claude/tests/load/saas-health.js

# With custom API URL
API_BASE_URL=https://api.kgents.io k6 run impl/claude/tests/load/saas-health.js

# NATS benchmark
nats bench test --pub 10 --sub 10 --size 1024 --msgs 10000
```

---

## 7. Security Review

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Stripe webhook signature verification | [x] | dev | Implemented |
| Rate limiting on webhook endpoint | [x] | dev | 100 req/min |
| Input validation | [x] | dev | Pydantic models |
| No SQL injection risks | [x] | dev | ORM only |
| Dependency vulnerability scan | [x] | sec | pip-audit: 1 LOW (pip CVE-2025-8869), no HIGH/CRITICAL |
| Container image scan | [x] | sec | Trivy: 0 HIGH/CRITICAL vulnerabilities in kgents/api:latest |

---

## 8. Documentation

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| API documentation | [x] | dev | OpenAPI spec |
| Environment variables | [x] | docs | environment-variables.md |
| Health endpoints | [x] | docs | health-endpoints.md |
| Runbook | [x] | ops | runbook.md |
| Production checklist | [x] | ops | This file |

---

## Blocking Items Summary

| Item | Category | Priority | Status |
|------|----------|----------|--------|
| ~~Network policies for NATS~~ | Security | ~~High~~ | RESOLVED |
| ~~PodDisruptionBudget~~ | Reliability | ~~Medium~~ | RESOLVED |
| ~~Load testing baseline~~ | Performance | ~~Medium~~ | RESOLVED |
| ~~Log aggregation~~ | Observability | ~~Low~~ | RESOLVED - Loki + Promtail deployed in Phase 8 |

---

## 9. Multi-Region Readiness (Phase 10)

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| Current architecture documented | [x] | docs | `docs/saas/architecture-current.md` |
| DR contracts defined | [x] | ops | `docs/saas/dr-contracts.md` |
| Multi-region research complete | [x] | dev | `docs/saas/multi-region-research.md` |
| Migration roadmap created | [x] | ops | `docs/saas/multi-region-roadmap.md` |
| Cost estimates approved | [ ] | finance | ~$340/month for Active-Passive DR |
| Phase 11 prerequisites | [ ] | ops | S3/GCS bucket, Velero install |

### Multi-Region Prerequisites (for Phase 11+)

Before proceeding to multi-region implementation:

- [ ] Budget approval for ~$340/month additional infrastructure
- [ ] AWS/GCP cross-region access configured
- [ ] Velero backup location credentials provisioned
- [ ] ArgoCD multi-cluster configuration planned
- [ ] DR drill schedule approved (monthly staging, quarterly prod)

### Recommended Migration Path

| Phase | Description | Effort | Monthly Cost |
|-------|-------------|--------|--------------|
| 11 | External Backup (S3/Velero) | 1-2 days | +$20 |
| 12 | Cross-Region DNS Failover | 1 day | +$5 |
| 13 | Standby Cluster + NATS Mirror | 3-5 days | +$200 |
| 14 | Active-Active (optional) | 2-3 weeks | +$200 |

See: `docs/saas/multi-region-roadmap.md` for detailed implementation plans.

---

## Launch Approval

- [x] All HIGH priority blocking items resolved
- [ ] Security review sign-off
- [ ] Operations team sign-off
- [ ] Development team sign-off

**Target Launch Date**: _TBD_

---

## Changelog

- 2025-12-14: Phase 10 Multi-Region Evaluation - Architecture documented, DR contracts, migration roadmap (Phases 11-14)
- 2025-12-14: Phase 9 Production Hardening - Soak test script, blue/green deployment, API PDB, NATS backup CronJob, chaos baseline
- 2025-12-14: Phase 8 Enterprise Ready - API deployed to K8s (2 replicas, HPA), Loki log aggregation, security scans complete (0 HIGH/CRITICAL)
- 2025-12-14: Phase 7 Production Launch - Policies applied/verified, load test baseline (478 req/s), log aggregation deferred
- 2025-12-14: Phase 6 Launch Prep - Network policies, PDB, and load tests created
- 2025-12-14: Initial checklist created (Phase 5 Operate)
