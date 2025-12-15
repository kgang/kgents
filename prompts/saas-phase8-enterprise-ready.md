```markdown
concept.forest.manifest[phase=PLAN][sprint=saas_phase8_enterprise_ready]@span=saas_enterprise

/hydrate

handles:
  - phase7: impl/claude/plans/_epilogues/2025-12-14-saas-phase7-production-launch.md
  - checklist: docs/saas/production-checklist.md
  - baseline: docs/saas/load-test-baseline.md
  - runbook: docs/saas/runbook.md
  - nats-manifests: impl/claude/infra/k8s/manifests/nats/
  - api-code: impl/claude/protocols/api/
  - observability: impl/claude/infra/k8s/manifests/observability/

ledger: {PLAN:in_progress, RESEARCH:not_started, DEVELOP:not_started, STRATEGIZE:not_started, CROSS-SYNERGIZE:not_started, IMPLEMENT:not_started, QA:not_started, TEST:not_started, EDUCATE:not_started, MEASURE:not_started, REFLECT:not_started}
entropy: 0.10 budget (fresh cycle)

## Context

Phase 7 Production Launch COMPLETE. Key achievements:
- Network policies applied and verified (fixed kustomize selector pollution)
- PDB active: minAvailable=2, disruptionsAllowed=1
- Load test baseline: **478 req/s** (4.8x target), 0% errors, p95 6.95ms
- Log aggregation deferred with risk acceptance
- Launch announcement drafted

## Remaining Items (from docs/saas/production-checklist.md)

| Item | Category | Priority | Status |
|------|----------|----------|--------|
| Deploy API to K8s | Infrastructure | High | Blocking |
| Loki log aggregation | Observability | Medium | Deferred from Phase 7 |
| HPA for API | Scalability | Medium | Pending baseline |
| Security scans | Security | Medium | Pending |
| 24h soak test | Reliability | Low | Post-API deploy |
| Container image scan | Security | Low | Pending |

## Your Mission

Move from "launch ready" to "enterprise ready" by deploying the API to Kubernetes and completing operational hardening.

### Track A: API K8s Deployment (35%)
1. Create API deployment manifest (`infra/k8s/manifests/api/deployment.yaml`)
2. Configure resource limits based on load test (478 req/s baseline)
3. Create API Service manifest
4. Wire secrets (`kgents-api-secrets`) for OpenMeter, Stripe
5. Configure liveness/readiness probes (`/health`, `/health/saas`)
6. Apply and verify API accessible via Kong gateway
7. Verify `/health/saas` shows NATS and OpenMeter connected

### Track B: Loki Log Aggregation (25%)
1. Evaluate deployment: Helm vs manifest (recommend manifest for simplicity)
2. Create Loki StatefulSet manifest (`infra/k8s/manifests/observability/loki/`)
3. Configure retention (7 days default)
4. Create Promtail DaemonSet for log collection
5. Add Loki data source to Grafana
6. Create log panel in SaaS dashboard
7. Document in runbook

### Track C: HPA Configuration (20%)
1. Create HPA manifest (`infra/k8s/manifests/api/hpa.yaml`)
2. Target: 70% CPU, min 2 replicas, max 10
3. Validate with simulated load
4. Document scaling behavior

### Track D: Security Hardening (20%)
1. Run `uv run safety check` for dependency vulnerabilities
2. Run Trivy scan on container image (if built)
3. Review and resolve any HIGH/CRITICAL findings
4. Update production checklist with results
5. Document in security section of runbook

## Exit Criteria

- [ ] API deployed to `kgents-gateway` or `kgents-agents` namespace
- [ ] API accessible via Kong and returns healthy `/health/saas`
- [ ] Loki deployed and collecting logs from kgents namespaces
- [ ] Grafana shows logs in dashboard
- [ ] HPA configured and validated
- [ ] Security scans completed with no HIGH findings (or documented exceptions)

## Non-Goals

- Multi-region deployment (Phase 9+)
- Full 24h soak test (monitor post-deploy)
- Blue/green deployment (manual rollback first)
- API versioning (v2 endpoints)

## Attention Budget

```
Primary (60%): Tracks A + B (API deploy + Loki)
Secondary (25%): Track C (HPA)
Maintenance (15%): Track D (security)
```

## Branch Candidates

- **Container Registry**: If no image exists, may need to branch to build/push
- **Cert-Manager**: If HTTPS required, may spawn TLS track
- **NATS JetStream Backup**: For disaster recovery, defer to Phase 9

## Sequencing

```
Track A (API Deploy) ────────────┬──▶ Track C (HPA)
                                  │
Track B (Loki) ──────────────────┤
                                  │
Track D (Security) ──────────────┘
```

Tracks A, B, D can start in parallel. Track C depends on API being deployed.

## Entropy Budget

| Phase | Allocation | Notes |
|-------|------------|-------|
| PLAN | 0.01 | Scope definition (this prompt) |
| RESEARCH | 0.02 | Verify prerequisites, Loki patterns |
| IMPLEMENT | 0.05 | Main work (all 4 tracks) |
| Reserve | 0.02 | Unexpected issues |

---

This is the *PLAN* for SaaS Phase 8: Enterprise Ready.

⟿[RESEARCH]
```
