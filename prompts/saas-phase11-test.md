```markdown
concept.forest.manifest[phase=TEST][sprint=saas_phase11_external_backup]@span=saas_dr_foundation

/hydrate

handles:
  - skill: docs/skills/n-phase-cycle/saas-phase11-external-backup.md
  - roadmap: docs/saas/multi-region-roadmap.md
  - runbook: docs/saas/runbook.md
  - nats-backup: impl/claude/infra/k8s/manifests/nats/backup-cronjob.yaml
  - nats-s3-secret: impl/claude/infra/k8s/manifests/nats/backup-s3-secret.yaml
  - nats-iam: impl/claude/infra/k8s/manifests/nats/iam-policy.json
  - velero-dir: impl/claude/infra/k8s/manifests/velero/
  - velero-iam: impl/claude/infra/k8s/manifests/velero/iam-policy.json

ledger: {PLAN:complete, RESEARCH:complete, DEVELOP:touched, STRATEGIZE:complete, IMPLEMENT:touched, QA:touched, TEST:in_progress}
entropy: 0.05 budget (0.03 remaining)

## Context

Phase 11 IMPLEMENT and QA complete. Artifacts created:
- NATS backup CronJob modified with S3 upload capability
- S3 credentials Secret template (placeholder values)
- Velero manifests (schedule, credentials, storage locations)
- IAM least-privilege policies for NATS and Velero
- Runbook updated with S3 restore procedures
- Security context added to backup containers

**Constraint**: Live cluster available, but NO S3 bucket provisioned yet.

## Your Mission

Test backup infrastructure within current constraints. Validate what's testable locally, document S3-dependent tests as deferred.

### Track A: Local Backup Verification (60%)

Test NATS backup WITHOUT S3 (graceful degradation path):

1. **Trigger manual backup**:
   ```bash
   kubectl create job --from=cronjob/nats-backup nats-backup-test-$(date +%s) -n kgents-agents
   ```

2. **Verify backup completes**:
   - Check job logs for "Backup Complete"
   - Verify tar.gz created in PVC
   - Confirm S3 upload skipped gracefully (not errored)

3. **Test local restore**:
   - List backups in PVC
   - Run restore script against test backup
   - Verify stream/consumer configs restored

4. **Validate retention cleanup**:
   - Check old backups (>7 days) are cleaned

### Track B: Manifest Validation (25%)

Verify all manifests are production-ready:

1. **Dry-run full kustomization**:
   ```bash
   kubectl kustomize impl/claude/infra/k8s/manifests/nats/ | kubectl apply --dry-run=server -f -
   ```

2. **Validate Velero CRD compatibility**:
   - Note: Velero CRDs not installed (expected)
   - Document what happens when Velero IS installed

3. **Security audit**:
   - Verify no real credentials in manifests
   - Confirm placeholder markers are clear
   - Check security context is applied

### Track C: Deferred Tests (Document Only) (15%)

Create test plan for S3-dependent tests (to run after bucket provisioned):

1. **S3 Upload Test**:
   - Trigger backup with real S3 credentials
   - Verify object appears in bucket
   - Check versioning is working

2. **S3 Restore Test**:
   - Download backup from S3
   - Restore to staging namespace
   - Verify data integrity

3. **Velero End-to-End**:
   - Install Velero with S3 backend
   - Trigger manual backup
   - Restore to staging namespace

## Exit Criteria

- [ ] Manual NATS backup job completes successfully
- [ ] Local restore verified working
- [ ] S3 upload gracefully skipped (no errors)
- [ ] Manifests pass dry-run validation
- [ ] Security audit passed (no leaked credentials)
- [ ] Deferred test plan documented
- [ ] Ledger: TEST=touched

## Non-Goals

- Provisioning S3 bucket (blocked on cost approval)
- Installing Velero (requires S3 bucket)
- Full DR drill (Phase 12-13)
- Cross-region restore testing

## Test Strata

| Stratum | Scope | Status |
|---------|-------|--------|
| Unit | Manifest YAML validity | ✅ Testable |
| Integration | Local backup/restore | ✅ Testable |
| Integration | S3 upload | ⏸️ Deferred (no bucket) |
| Integration | Velero backup | ⏸️ Deferred (no Velero) |
| E2E | Cross-region restore | ⏸️ Deferred (Phase 12+) |

## Entropy Budget

| Activity | Allocation |
|----------|------------|
| Local backup test | 0.01 |
| Restore verification | 0.01 |
| Manifest validation | 0.005 |
| Documentation | 0.005 |

Draw: `void.entropy.sip(amount=0.03)`

## Branch Candidates

- **S3 bucket approved**: Spawn `saas-phase11-s3-integration-test`
- **Backup failures found**: May require IMPLEMENT rework
- **Velero complexity**: May spawn `velero-installation-guide` track

---

This is the *TEST* for SaaS Phase 11: External Backup.

Execute Track A and B now. Document Track C for future execution.

⟿[EDUCATE]
/hydrate
handles: test-results=${local_backup_results}; deferred=${s3_test_plan}; manifests=validated; security=passed; ledger={TEST:touched}; branches=none
mission: document backup procedures for operators; update runbook with test findings; create quick-start for DR setup.
actions: update runbook with verified commands; add troubleshooting section; document S3 setup prerequisites.
exit: runbook enhanced; quick-start created; ledger.EDUCATE=touched; continuation → MEASURE.

⟂[BLOCKED:s3_bucket] S3 bucket not provisioned—full backup test deferred
⟂[BLOCKED:backup_failure] Local backup job failed—requires IMPLEMENT rework
⟂[BLOCKED:restore_failure] Restore script broken—requires debugging
```
