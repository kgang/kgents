# Velero Cluster State Backup

Kubernetes cluster state backup using Velero with S3/GCS backend.

Part of Phase 11: External Backup foundation for multi-region DR.

## Prerequisites

1. S3/GCS bucket with versioning enabled
2. IAM credentials with S3 write access
3. Velero CLI installed locally

## Installation

### Option A: Helm (Recommended)

```bash
# Add Velero Helm repo
helm repo add vmware-tanzu https://vmware-tanzu.github.io/helm-charts
helm repo update

# Install Velero with AWS/S3 provider
helm install velero vmware-tanzu/velero \
  --namespace velero \
  --create-namespace \
  --set-file credentials.secretContents.cloud=./credentials-velero \
  --set configuration.backupStorageLocation[0].name=default \
  --set configuration.backupStorageLocation[0].provider=aws \
  --set configuration.backupStorageLocation[0].bucket=kgents-dr-backups \
  --set configuration.backupStorageLocation[0].config.region=us-west-2 \
  --set configuration.backupStorageLocation[0].config.s3ForcePathStyle=false \
  --set configuration.volumeSnapshotLocation[0].name=default \
  --set configuration.volumeSnapshotLocation[0].provider=aws \
  --set configuration.volumeSnapshotLocation[0].config.region=us-west-2 \
  --set initContainers[0].name=velero-plugin-for-aws \
  --set initContainers[0].image=velero/velero-plugin-for-aws:v1.8.0 \
  --set initContainers[0].volumeMounts[0].mountPath=/target \
  --set initContainers[0].volumeMounts[0].name=plugins
```

### Option B: Velero CLI

```bash
# Create credentials file
cat > credentials-velero << EOF
[default]
aws_access_key_id=<AWS_ACCESS_KEY_ID>
aws_secret_access_key=<AWS_SECRET_ACCESS_KEY>
EOF

# Install Velero
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.8.0 \
  --bucket kgents-dr-backups \
  --backup-location-config region=us-west-2 \
  --snapshot-location-config region=us-west-2 \
  --secret-file ./credentials-velero

# Clean up credentials file
rm credentials-velero
```

## Daily Backup Schedule

After installation, create the daily backup schedule:

```bash
kubectl apply -f schedule.yaml
```

Or via CLI:

```bash
velero schedule create daily-kgents-backup \
  --schedule="0 3 * * *" \
  --include-namespaces kgents-triad,kgents-agents \
  --ttl 720h
```

## Verification

```bash
# Check Velero pods
kubectl get pods -n velero

# Check backup location
velero backup-location get

# List backups
velero backup get

# List schedules
velero schedule get
```

## Restore Procedure

See `docs/saas/runbook.md` Section 4 for full restore procedures.

Quick restore to staging:

```bash
# List available backups
velero backup get

# Restore to a different namespace (staging)
velero restore create --from-backup daily-kgents-backup-YYYYMMDD \
  --namespace-mappings kgents-agents:kgents-agents-staging,kgents-triad:kgents-triad-staging
```

## Files

- `credentials-secret.yaml` - IAM credentials for S3 access (template)
- `schedule.yaml` - Daily backup schedule for kgents namespaces (requires Velero CRDs)
- `kustomization.yaml` - Kustomize manifest

**Note:** `schedule.yaml` requires Velero to be installed first (CRDs must exist).
The Schedule, BackupStorageLocation, and VolumeSnapshotLocation resources are
Velero custom resources that are created during Velero installation.

## AGENTESE

`world.gateway.velero.backup`
