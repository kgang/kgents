concept.forest.manifest[phase=MEASURE][sprint=saas_phase11_external_backup]@span=saas_dr_foundation

/hydrate

handles:
  - skill: docs/skills/n-phase-cycle/saas-phase11-external-backup.md
  - runbook: docs/saas/runbook.md
  - alerting-rules: impl/claude/infra/k8s/manifests/observability/prometheus/alerting-rules.yaml
  - grafana-saas: impl/claude/infra/k8s/manifests/grafana/dashboard-saas.json
  - backup-cronjob: impl/claude/infra/k8s/manifests/nats/backup-cronjob.yaml
  - educate-epilogue: impl/claude/plans/_epilogues/2025-12-14-saas-phase11-educate.md

ledger: {PLAN:complete, RESEARCH:complete, DEVELOP:touched, STRATEGIZE:complete, IMPLEMENT:touched, QA:touched, TEST:touched, EDUCATE:touched}
entropy: 0.02 budget (0.005 remaining from EDUCATE)

## Context

EDUCATE phase complete. Runbook enhanced with:
- Quick reference card for backup components
- Troubleshooting section (5 scenarios)
- Degraded mode operations documentation
- S3 setup prerequisites for platform engineers

Backup infrastructure validated (local backup working, S3 deferred pending bucket).

## Your Mission

Instrument backup success/failure signals. Define leading indicators for backup health. Capture baselines for SLI tracking.

### Track A: Prometheus Metrics (50%)

Add backup-specific alerting rules to `alerting-rules.yaml`:

```yaml
- alert: NATSBackupFailed
  expr: kube_job_status_failed{job_name=~"nats-backup.*"} > 0
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: NATS backup job failed
    description: "NATS backup job {{ $labels.job_name }} has failed"

- alert: NATSBackupMissing
  expr: time() - kube_job_status_completion_time{job_name=~"nats-backup.*"} > 90000
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: NATS backup not completed in 25 hours
    description: "No successful NATS backup in the last 25 hours"

- alert: BackupPVCNearCapacity
  expr: kubelet_volume_stats_used_bytes{persistentvolumeclaim="nats-backup-pvc"} / kubelet_volume_stats_capacity_bytes{persistentvolumeclaim="nats-backup-pvc"} > 0.8
  for: 15m
  labels:
    severity: warning
  annotations:
    summary: Backup PVC approaching capacity
    description: "NATS backup PVC is {{ $value | humanizePercentage }} full"
```

### Track B: Grafana Dashboard Panel (30%)

Add backup status panel to `dashboard-saas.json`:

| Metric | Visualization | Purpose |
|--------|---------------|---------|
| Last backup time | Stat | Freshness indicator |
| Backup job success rate | Gauge | 7-day success % |
| PVC usage | Gauge | Capacity monitoring |
| S3 upload status | Stat | Off-site backup health |

### Track C: SLI Definition (20%)

Define Service Level Indicators for backup RPO:

| SLI | Target | Measurement |
|-----|--------|-------------|
| Backup freshness | < 25 hours | `time() - last_successful_backup_time` |
| Backup success rate | > 99% | `successful_backups / total_backups` over 30 days |
| Recovery time objective | < 15 min | Manual restore drill results |

## Exit Criteria

- [ ] Alerting rules added for backup failures
- [ ] Grafana panel shows backup status
- [ ] SLI targets documented
- [ ] Ledger: MEASURE=touched

## Non-Goals

- Implementing custom backup exporter (use kube-state-metrics)
- Creating separate backup dashboard (add panel to existing SaaS dashboard)
- Setting up PagerDuty/OpsGenie integration (future work)

## Entropy Budget

| Activity | Allocation |
|----------|------------|
| Alerting rules | 0.008 |
| Dashboard panel | 0.006 |
| SLI definition | 0.004 |
| Buffer | 0.002 |

Draw: `void.entropy.sip(amount=0.02)`

## Branch Candidates

- **Custom exporter needed**: Spawn `saas-backup-exporter.md` (if kube-state-metrics insufficient)
- **Alertmanager integration**: Spawn `saas-alerting-channels.md`

## Principles Alignment

| Principle | Application |
|-----------|-------------|
| **Tasteful** | Minimal metrics, maximum signal |
| **Composable** | Reuse existing kube-state-metrics |
| **Generative** | SLI targets compress to single freshness number |

---

This is the *MEASURE* for SaaS Phase 11: External Backup.

Instrument backup health signals from validated test results.

⟿[REFLECT]
/hydrate
handles: alerting=impl/claude/infra/k8s/manifests/observability/prometheus/alerting-rules.yaml; dashboard=impl/claude/infra/k8s/manifests/grafana/dashboard-saas.json; sli=documented; ledger={MEASURE:touched}; branches=none
mission: synthesize Phase 11 outcomes; distill learnings to meta.md; decide archive/upgrade/retain; generate next-cycle seeds.
actions: write epilogue; check archiving criteria; update forest; propose continuation (PLAN for Phase 12 or DETACH if blocked).
exit: epilogue written; archiving decision made; continuation → PLAN[phase12_dns_failover] or ⟂[DETACH:awaiting_budget].

⟂[BLOCKED:metrics_infrastructure] kube-state-metrics not deployed
⟂[ENTROPY_DEPLETED] Budget exhausted without completion
