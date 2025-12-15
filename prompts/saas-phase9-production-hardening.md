```markdown
concept.forest.manifest[phase=PLAN][sprint=saas_phase9_production_hardening]@span=saas_hardening

/hydrate

handles:
  - phase8: impl/claude/plans/_epilogues/2025-12-14-saas-phase8-enterprise-ready.md
  - checklist: docs/saas/production-checklist.md
  - runbook: docs/saas/runbook.md
  - api-manifests: impl/claude/infra/k8s/manifests/api/
  - nats-manifests: impl/claude/infra/k8s/manifests/nats/
  - observability: impl/claude/infra/k8s/manifests/observability/
  - load-baseline: docs/saas/load-test-baseline.md

ledger: {PLAN:in_progress, RESEARCH:not_started, DEVELOP:not_started, STRATEGIZE:not_started, CROSS-SYNERGIZE:not_started, IMPLEMENT:not_started, QA:not_started, TEST:not_started, EDUCATE:not_started, MEASURE:not_started, REFLECT:not_started}
entropy: 0.10 budget (fresh cycle)

## Context

Phase 8 Enterprise Ready COMPLETE. Key achievements:
- API deployed to K8s (2 replicas, HPA 2-10)
- Loki + Promtail log aggregation operational
- Grafana datasource configured with trace correlation
- Security scans: 0 HIGH/CRITICAL (pip-audit, Trivy)
- Production checklist: All blocking items resolved

Current infrastructure state:
- **API**: `kgents/api:latest` running in `kgents-triad` (2 pods)
- **NATS**: 3-node cluster in `kgents-agents`
- **Observability**: Prometheus, Grafana, Tempo, Loki, OTEL-Collector
- **Gateway**: Kong with API key auth + rate limiting

## Remaining Hardening Items

| Item | Category | Priority | Status |
|------|----------|----------|--------|
| 24h soak test | Reliability | High | Not started |
| Blue/green deployment | Release | Medium | Not started |
| NATS JetStream backup | DR | Medium | Not started |
| API PodDisruptionBudget | HA | Medium | Not started |
| Chaos engineering baseline | Reliability | Low | Not started |
| Rollback runbook | Operations | Low | Not started |

## Your Mission

Achieve production hardening by validating long-running stability, implementing safe deployment patterns, and establishing disaster recovery procedures.

### Track A: 24h Soak Test (35%)
1. Create k6 soak test script (`impl/claude/tests/load/saas-soak.js`)
   - Duration: 24h (or 4h accelerated with higher load)
   - VUs: 10 constant (simulating sustained production traffic)
   - Endpoints: `/health/saas`, `/v1/agentese/resolve` (mixed)
   - Thresholds: p95 < 200ms, error rate < 0.1%, no memory growth
2. Execute soak test against local cluster
3. Monitor and capture metrics:
   - Memory usage over time (watch for leaks)
   - Latency percentiles stability
   - Error patterns
   - NATS circuit breaker activations
4. Document baseline in `docs/saas/soak-test-baseline.md`
5. Create Grafana panel for memory trend visualization

### Track B: Blue/Green Deployment (25%)
1. Create deployment strategy documentation
2. Add `strategy.type: RollingUpdate` with maxSurge/maxUnavailable config
3. Create API PodDisruptionBudget (`minAvailable: 1`)
4. Test rollout with image tag change
5. Verify zero-downtime during deployment
6. Add rollback procedure to runbook
7. Create deployment checklist (`docs/saas/deployment-checklist.md`)

### Track C: NATS JetStream Backup (25%)
1. Research NATS backup strategies:
   - JetStream snapshot API
   - Volume snapshot (PVC)
   - Cross-cluster replication
2. Create backup CronJob (`infra/k8s/manifests/nats/backup-cronjob.yaml`)
3. Configure backup retention (7 days)
4. Test restore procedure
5. Document in runbook (backup/restore section)
6. Add backup monitoring alert

### Track D: Chaos Engineering Baseline (15%)
1. Document failure scenarios:
   - API pod kill → HPA responds
   - NATS leader election → circuit breaker triggers
   - Network partition → fallback queue activates
2. Create simple chaos script (pod deletion)
3. Verify recovery within SLA (< 30s for API, < 60s for NATS)
4. Document observed behavior

## Exit Criteria

- [ ] Soak test completed (4h+ minimum) with stable metrics
- [ ] No memory leaks detected (< 10% growth over baseline)
- [ ] Blue/green rollout tested with zero downtime
- [ ] PDB configured for API
- [ ] NATS backup CronJob running
- [ ] Restore procedure tested and documented
- [ ] Chaos baseline documented

## Non-Goals

- Multi-region deployment (Phase 10+)
- Automated canary releases (future enhancement)
- Full chaos engineering suite (Litmus, Chaos Mesh)
- External backup storage (S3/GCS) — use local PVC first
- Production traffic testing (staging only)

## Attention Budget

```
Primary (60%): Tracks A + B (soak test + blue/green)
Secondary (25%): Track C (NATS backup)
Exploration (15%): Track D (chaos baseline)
```

## Branch Candidates

- **Memory leak found**: Branch to profiling/fix before proceeding
- **NATS backup complexity**: May defer to Phase 10 if JetStream API insufficient
- **Multi-cluster NATS**: If backup requires replication, spawn separate track

## Sequencing

```
Track A (Soak Test) ────────────────────────▶ Baseline doc
         │
         ├──▶ If memory leak found ──▶ ⟂[BLOCKED:memory_leak]
         │
Track B (Blue/Green) ──────────────────────▶ Deployment checklist
         │
Track C (NATS Backup) ─────────────────────▶ Backup CronJob
         │
Track D (Chaos) ───────────────────────────▶ Chaos baseline doc
```

All tracks can proceed in parallel. Track A may block if issues found.

## Entropy Budget

| Phase | Allocation | Notes |
|-------|------------|-------|
| PLAN | 0.01 | Scope definition (this prompt) |
| RESEARCH | 0.02 | NATS backup patterns, chaos tools |
| DEVELOP | 0.01 | Test scripts, backup strategy |
| IMPLEMENT | 0.04 | Main work (all 4 tracks) |
| QA | 0.01 | Verify soak metrics |
| Reserve | 0.01 | Unexpected issues |

## Phase-Specific Guidance

### For RESEARCH
- Check NATS documentation for JetStream backup API
- Review k6 soak test examples
- Verify current memory baseline in Grafana

### For IMPLEMENT
- Run soak test in background while working on other tracks
- Use `kubectl rollout status` to verify blue/green
- Test NATS restore on fresh namespace first

### For QA
- Verify soak test thresholds pass
- Confirm PDB prevents all-pod eviction
- Test backup restore with data verification

### For REFLECT
- Capture p95 latency trend over soak duration
- Document recovery times for chaos scenarios
- Note any architectural improvements needed

---

This is the *PLAN* for SaaS Phase 9: Production Hardening.

⟿[RESEARCH]
```
