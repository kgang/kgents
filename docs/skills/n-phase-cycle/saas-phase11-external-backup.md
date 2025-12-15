---
path: docs/skills/n-phase-cycle/saas-phase11-external-backup
status: pending
progress: 0
last_touched: 2025-12-14
touched_by: claude-opus-4-5
blocking:
  - cost_approval  # ~$340/month for DR infrastructure
enables:
  - saas-phase12-dns-failover
  - saas-phase13-standby-cluster
session_notes: |
  Continuation from Phase 10 STRATEGIZE. Migration roadmap complete.
  Track C (documentation) delivered. Ready for Track A (implementation).
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: touched
  STRATEGIZE: complete
  CROSS-SYNERGIZE: skipped  # reason: single-track focus
  IMPLEMENT: touched
  QA: touched
  TEST: touched  # 2025-12-14: Local backup verified, S3 deferred
  EDUCATE: touched  # 2025-12-14: Runbook enhanced with troubleshooting, degraded modes, S3 setup guide
  MEASURE: deferred  # reason: post-DR metrics
  REFLECT: pending
entropy:
  planned: 0.05
  spent: 0.03
  returned: 0.02
---

# SaaS Phase 11: External Backup (IMPLEMENT)

> Establish cross-region backup foundation before deploying DR infrastructure.

**Sprint**: `saas_phase11_external_backup`
**Parent**: `saas_migration_roadmap`
**Estimated Effort**: 1-2 days
**Monthly Cost Delta**: +$20 (S3/GCS storage)

---

## Context from Phase 10

### Artifacts Created

| Artifact | Path | Purpose |
|----------|------|---------|
| Architecture Doc | `docs/saas/architecture-current.md` | Single-region baseline |
| Migration Roadmap | `docs/saas/multi-region-roadmap.md` | Phases 11-14 sequenced |
| DR Contracts | `docs/saas/dr-contracts.md` | Testable RPO/RTO assertions |
| Research | `docs/saas/multi-region-research.md` | Pattern evaluation |
| Checklist Update | `docs/saas/production-checklist.md` | Section 9 added |

### Decisions Made

1. **Active-Passive DR** (not Active-Active) - cost/complexity balance
2. **NATS Stream Mirroring** for data replication
3. **Velero** for cluster state backup
4. **S3/GCS** for cross-region durable storage

### Blockers

- [ ] Budget approval (~$340/month) - may gate full DR, not Phase 11
- [ ] AWS/GCP account access for cross-region bucket

---

## Your Mission

Implement cross-region backup infrastructure as foundation for DR:

### Track A: S3/GCS Backup Bucket

1. **Create backup bucket** with versioning enabled
2. **Configure IAM** for backup service account
3. **Test cross-region access** from primary cluster

### Track B: NATS Backup to S3

1. **Modify backup CronJob** (`manifests/nats/backup-cronjob.yaml`)
   - Add S3 upload step after local backup
   - Configure credentials via K8s Secret
2. **Verify backup appears** in S3 within 24h
3. **Test restore** from S3 to staging namespace

### Track C: Velero Installation

1. **Install Velero** with S3/GCS backend
2. **Create daily schedule** for cluster snapshots
3. **Document restore procedure** in runbook

---

## Implementation Chunks

```
[ ] 1. Create S3/GCS bucket with versioning
[ ] 2. Create IAM role/service account for backups
[ ] 3. Create K8s Secret for S3 credentials
[ ] 4. Modify NATS backup CronJob for S3 upload
[ ] 5. Install Velero CLI and server components
[ ] 6. Configure Velero backup location
[ ] 7. Create Velero daily schedule
[ ] 8. Test NATS restore from S3
[ ] 9. Test Velero restore to staging
[ ] 10. Update runbook with restore procedures
```

---

## Exit Criteria

- [ ] S3/GCS bucket exists with versioning enabled
- [ ] NATS backups appear in S3 within 24 hours
- [ ] Velero backup completes successfully
- [ ] Restore test from S3 to staging namespace succeeds
- [ ] Runbook updated with restore procedures
- [ ] Ledger: IMPLEMENT=touched

---

## Principles Alignment

| Principle | Application |
|-----------|-------------|
| **Tasteful** | Minimal infrastructure, no over-engineering |
| **Composable** | Backup foundation enables all subsequent DR phases |
| **Ethical** | DR protects user data from region-level failure |
| **Joy-Inducing** | Confidence in data durability |

---

## Entropy Budget

- **Planned**: 0.05 (5%)
- **Reserve for**: Velero configuration variations, IAM permission debugging
- **Draw**: `void.entropy.sip(amount=0.05)`

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `manifests/nats/backup-cronjob.yaml` | Modify | Add S3 upload |
| `manifests/nats/backup-secret.yaml` | Create | S3 credentials |
| `manifests/velero/` | Create | Velero manifests |
| `docs/saas/runbook.md` | Modify | Add S3 restore procedures |

---

## Continuation Generator

### Exit Signifier

```markdown
# Normal exit (auto-continue):
⟿[QA]
/hydrate
handles: bucket=${bucket_name}; cronjob=manifests/nats/backup-cronjob.yaml; velero=manifests/velero/; runbook=docs/saas/runbook.md; ledger={IMPLEMENT:touched}; branches=none
mission: verify backup infrastructure quality and security.
actions: kubectl apply --dry-run; verify IAM least-privilege; check secret rotation policy.
exit: QA checklist status + ledger.QA=touched; continuation → TEST.

# Halt conditions:
⟂[BLOCKED:cost_approval] Budget not approved for S3/GCS costs
⟂[BLOCKED:iam_access] Cannot create IAM role for backup service account
⟂[BLOCKED:velero_install] Velero installation fails
⟂[ENTROPY_DEPLETED] Budget exhausted without completion
```

---

## TEST Phase Results (2025-12-14)

### Local Backup Verification (Track A) ✓

| Test | Status | Notes |
|------|--------|-------|
| CronJob creation | ✓ PASS | Resources created successfully |
| Manual job trigger | ✓ PASS | `nats-backup-test-1765759837` completed in 73s |
| Backup archive created | ✓ PASS | `20251215-005148.tar.gz` (238 bytes) |
| S3 upload gracefully skipped | ✓ PASS | "NOTE: S3/GCS upload skipped (credentials not configured)" |
| Restore script execution | ✓ PASS | Extracted and processed successfully |
| Retention cleanup | ✓ PASS | `find` with `-mtime +7` in script |

### Manifest Validation (Track B) ✓

| Test | Status | Notes |
|------|--------|-------|
| NATS kustomize dry-run | ✓ PASS | All resources validated by server |
| Velero YAML syntax | ✓ PASS | Valid YAML, CRDs not installed (expected) |
| Security audit: placeholders | ✓ PASS | All secrets use `REPLACE_WITH_*` markers |
| Security audit: no real keys | ✓ PASS | No `AKIA*` patterns found |
| IAM policies: least privilege | ✓ PASS | Path-scoped, prefix-conditioned |

### Deferred Tests (Track C) - S3 Bucket Required

The following tests are blocked until S3 bucket is provisioned (~$20/month for storage):

#### S3 Upload Test
```bash
# Prerequisites
# 1. Create S3 bucket: kgents-dr-backups with versioning enabled
# 2. Apply IAM policy: impl/claude/infra/k8s/manifests/nats/iam-policy.json
# 3. Create secret with real credentials:
kubectl create secret generic nats-backup-s3 \
  -n kgents-agents \
  --from-literal=AWS_ACCESS_KEY_ID=<key> \
  --from-literal=AWS_SECRET_ACCESS_KEY=<secret> \
  --from-literal=AWS_DEFAULT_REGION=us-west-2 \
  --from-literal=S3_BUCKET=kgents-dr-backups

# Test
kubectl create job --from=cronjob/nats-backup nats-backup-s3-test -n kgents-agents
kubectl logs -f job/nats-backup-s3-test -n kgents-agents

# Verify
aws s3 ls s3://kgents-dr-backups/nats/ --human-readable
```

#### S3 Restore Test
```bash
# Download backup from S3 to staging
kubectl run s3-restore-test --image=amazon/aws-cli:latest --rm -it \
  --env="AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" \
  --env="AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" \
  -- sh -c "aws s3 cp s3://kgents-dr-backups/nats/<backup>.tar.gz /tmp/"

# Restore to staging namespace (see runbook for full procedure)
```

#### Velero End-to-End Test
```bash
# Prerequisites: Install Velero CLI, create S3 bucket
velero install \
  --provider aws \
  --bucket kgents-dr-backups \
  --prefix velero \
  --secret-file ./credentials-velero \
  --backup-location-config region=us-west-2

# Apply schedules
kubectl apply -k impl/claude/infra/k8s/manifests/velero/

# Trigger manual backup
velero backup create manual-test --include-namespaces kgents-agents

# Verify
velero backup describe manual-test --details
```

### Exit Signifiers

- **S3 bucket approved**: Continue with S3 integration tests
- **All tests pass**: `⟿[EDUCATE]`
- **Backup failures found**: `⟂[BLOCKED:backup_failure]`

---

## Related

- Parent: `docs/saas/multi-region-roadmap.md`
- DR Contracts: `docs/saas/dr-contracts.md`
- Runbook: `docs/saas/runbook.md`
- Velero Docs: https://velero.io/docs/

---

*Phase 11 of SaaS Multi-Region Migration. Foundation for DR capability.*

---

⟿[IMPLEMENT]

  concept.forest.manifest[phase=IMPLEMENT][sprint=saas_phase11_external_backup]@span=saas_migration_roadmap

  /hydrate

  handles:
    - roadmap: docs/saas/multi-region-roadmap.md
    - architecture: docs/saas/architecture-current.md
    - runbook: docs/saas/runbook.md
    - nats-backup: impl/claude/infra/k8s/manifests/nats/backup-cronjob.yaml

  ledger: {PLAN:complete, RESEARCH:complete, DEVELOP:touched, STRATEGIZE:complete, IMPLEMENT:in_progress}
  entropy: 0.05 budget

  ## Your Mission

  Implement cross-region backup infrastructure (Phase 11 of multi-region roadmap).

  ### Deliverables

  1. **S3/GCS Bucket** with versioning enabled
  2. **Modified NATS CronJob** uploading to S3
  3. **Velero installation** with daily schedules
  4. **Runbook updates** with restore procedures

  ### Exit Criteria

  - [ ] Bucket created with versioning
  - [ ] NATS backup CronJob modified for S3
  - [ ] Velero installed and scheduled
  - [ ] Restore procedure tested
  - [ ] Runbook updated
  - [ ] Ledger: IMPLEMENT=touched

  ---

  This is the *IMPLEMENT* for SaaS Phase 11: External Backup.

  ⟿[QA] on success | ⟂[BLOCKED:cost_approval] if budget review needed
