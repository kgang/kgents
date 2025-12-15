```markdown
concept.forest.manifest[phase=EDUCATE][sprint=saas_phase11_external_backup]@span=saas_dr_foundation

/hydrate

handles:
  - skill: docs/skills/n-phase-cycle/saas-phase11-external-backup.md
  - runbook: docs/saas/runbook.md
  - roadmap: docs/saas/multi-region-roadmap.md
  - nats-backup: impl/claude/infra/k8s/manifests/nats/backup-cronjob.yaml
  - nats-s3-secret: impl/claude/infra/k8s/manifests/nats/backup-s3-secret.yaml
  - velero-dir: impl/claude/infra/k8s/manifests/velero/
  - test-results: impl/claude/plans/_epilogues/2025-12-14-saas-phase11-test.md

ledger: {PLAN:complete, RESEARCH:complete, DEVELOP:touched, STRATEGIZE:complete, IMPLEMENT:touched, QA:touched, TEST:touched}
entropy: 0.05 budget (0.02 remaining from TEST)

## Context

TEST phase complete. Local backup verified working:
- Manual backup job completed (73s, 238 bytes)
- S3 upload gracefully skipped (no credentials)
- Restore script executed successfully
- Manifests pass dry-run and security audit
- Deferred tests documented for S3 integration

## Your Mission

Teach operators how to wield the backup infrastructure. Create accessible documentation that enables self-service without inside knowledge.

### Audience Map

| Persona | Context | Needs |
|---------|---------|-------|
| **Operator** | `world.gateway.nats.backup` | Daily monitoring, restore procedures |
| **On-call** | `time.incident.*` | Emergency restore steps, troubleshooting |
| **Platform Engineer** | `concept.infra.k8s` | S3 setup prerequisites, IAM policies |

### Track A: Runbook Enhancement (50%)

Verify runbook has all procedures an operator needs:

1. **Quick reference card**: Add summary table at start of Backup section
2. **Troubleshooting section**: Common issues with resolutions
3. **Verification commands**: One-liners to check backup health
4. **S3 setup prerequisites**: Step-by-step for platform engineers

### Track B: Quick-Start Guide (30%)

Create or update quick-start for first-time setup:

1. **Deploy backup CronJob**:
   ```bash
   kubectl apply -f impl/claude/infra/k8s/manifests/nats/backup-cronjob.yaml
   ```

2. **Verify backup runs**:
   ```bash
   kubectl create job --from=cronjob/nats-backup test-backup -n kgents-agents
   kubectl logs -f job/test-backup -n kgents-agents
   ```

3. **Enable S3 (when available)**:
   - Create bucket with versioning
   - Apply IAM policy
   - Create secret
   - Verify upload in logs

### Track C: Degraded Mode Documentation (20%)

Document what happens when things go wrong:

1. **S3 unavailable**: Backups continue locally, 7-day retention
2. **NATS unavailable**: Backup job fails gracefully, retries
3. **PVC full**: Retention cleanup may fail, manual intervention needed
4. **Restore fails**: Error messages and recovery steps

## Exit Criteria

- [ ] Runbook enhanced with troubleshooting section
- [ ] Quick-start guide verifiable by copy-paste
- [ ] Degraded paths documented
- [ ] Ledger: EDUCATE=touched

## Non-Goals

- Writing user-facing product docs (this is operator-focused)
- Creating video tutorials
- Translating to other languages

## Entropy Budget

| Activity | Allocation |
|----------|------------|
| Runbook enhancement | 0.01 |
| Quick-start guide | 0.01 |
| Alternative explanations | 0.005 (accursed share) |

Draw: `void.entropy.sip(amount=0.025)`

## Branch Candidates

- **S3 bucket approved**: Spawn `saas-phase11-s3-quick-start.md`
- **Monitoring gaps found**: Spawn `saas-backup-alerting.md`

---

This is the *EDUCATE* for SaaS Phase 11: External Backup.

Create operator-accessible documentation from validated test results.

⟿[MEASURE]
/hydrate
handles: runbook=docs/saas/runbook.md; quickstart=docs/saas/backup-quickstart.md; troubleshooting=added; degraded_paths=documented; ledger={EDUCATE:touched}; branches=none
mission: instrument backup success/failure signals; define leading indicators; capture baselines.
actions: add Prometheus metrics for backup job; create Grafana dashboard panel; define SLI for backup RPO.
exit: metrics defined + baselines captured; ledger.MEASURE=touched; continuation → REFLECT.

⟂[BLOCKED:missing_docs_infra] Required docs infrastructure missing
⟂[ENTROPY_DEPLETED] Budget exhausted without completion
```
