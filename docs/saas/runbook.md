# SaaS Infrastructure Runbook

> Operational procedures for common scenarios and incidents.

## Table of Contents

1. [Startup Procedures](#startup-procedures)
2. [Shutdown Procedures](#shutdown-procedures)
3. [Deployment & Rollback](#deployment--rollback)
4. [Backup & Restore](#backup--restore)
5. [Disaster Recovery](#disaster-recovery)
6. [Incident Response](#incident-response)
7. [Common Issues](#common-issues)
8. [Monitoring Alerts](#monitoring-alerts)

---

## Startup Procedures

### Deploy NATS Cluster

```bash
# Check prerequisites
kubectl cluster-info
kubectl get ns kgents-agents || kubectl apply -f impl/claude/infra/k8s/manifests/namespace.yaml

# Deploy NATS
kubectl apply -k impl/claude/infra/k8s/manifests/nats/

# Wait for pods
kubectl rollout status statefulset/nats -n kgents-agents --timeout=120s

# Verify cluster
kubectl get pods -n kgents-agents -l app.kubernetes.io/name=nats
```

### Verify NATS Health

```bash
# Check pod status
kubectl get pods -n kgents-agents -l app.kubernetes.io/name=nats

# Check logs
kubectl logs -n kgents-agents nats-0 -c nats

# Check JetStream status
kubectl exec -n kgents-agents nats-0 -- nats-server --version
```

### Deploy API with SaaS Infrastructure

```bash
# Set secrets
kubectl create secret generic kgents-api-secrets \
  -n kgents-agents \
  --from-literal=OPENMETER_API_KEY=om_live_xxx \
  --from-literal=STRIPE_API_KEY=sk_live_xxx \
  --from-literal=STRIPE_WEBHOOK_SECRET=whsec_xxx

# Deploy API (assumes deployment manifest exists)
kubectl apply -f impl/claude/infra/k8s/manifests/api/deployment.yaml

# Verify SaaS health
curl https://api.kgents.io/health/saas
```

---

## Shutdown Procedures

### Graceful API Shutdown

The API automatically:
1. Stops accepting new requests
2. Flushes OpenMeter buffer
3. Closes NATS connection

```bash
# Scale down gracefully
kubectl scale deployment kgents-api -n kgents-agents --replicas=0

# Wait for pods to terminate
kubectl wait --for=delete pod -l app=kgents-api -n kgents-agents --timeout=60s
```

### NATS Cluster Shutdown

```bash
# Scale down (preserves data)
kubectl scale statefulset nats -n kgents-agents --replicas=0

# Or delete entirely (loses data)
kubectl delete -k impl/claude/infra/k8s/manifests/nats/
```

---

## Deployment & Rollback

### Blue/Green Deployment

The API uses a RollingUpdate strategy with zero-downtime guarantees:

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # Allow 1 extra pod during rollout
    maxUnavailable: 0  # Never reduce below desired count
```

### Deploy New Version

```bash
# Option 1: Update image tag in manifest
# Edit deployment.yaml: image: kgents/api:v1.x.x
kubectl apply -f impl/claude/infra/k8s/manifests/api/deployment.yaml

# Option 2: Direct image update
kubectl set image deployment/kgent-api \
  api=kgents/api:v1.x.x \
  -n kgents-triad

# Monitor rollout
kubectl rollout status deployment/kgent-api -n kgents-triad --timeout=300s
```

### Rollback Procedures

#### Immediate Rollback (to previous version)

```bash
# Rollback to previous revision
kubectl rollout undo deployment/kgent-api -n kgents-triad

# Verify rollback
kubectl rollout status deployment/kgent-api -n kgents-triad
```

#### Rollback to Specific Version

```bash
# View rollout history
kubectl rollout history deployment/kgent-api -n kgents-triad

# Rollback to specific revision (e.g., revision 2)
kubectl rollout undo deployment/kgent-api -n kgents-triad --to-revision=2

# Verify
kubectl get pods -n kgents-triad -l app.kubernetes.io/name=kgent-api -o jsonpath='{.items[*].spec.containers[0].image}'
```

#### Emergency Scale Down

```bash
# If rollback fails, scale down completely
kubectl scale deployment/kgent-api -n kgents-triad --replicas=0

# Investigate
kubectl describe deployment/kgent-api -n kgents-triad
kubectl logs -n kgents-triad -l app.kubernetes.io/name=kgent-api --previous
```

### Rollback Verification Checklist

- [ ] Pods running correct image version
- [ ] Health endpoints returning 200
- [ ] No error spikes in logs
- [ ] Metrics stable in Grafana

See also: `docs/saas/deployment-checklist.md`

---

## Backup & Restore

### Quick Reference

| Component | Schedule | Retention | Location | Restore Time |
|-----------|----------|-----------|----------|--------------|
| NATS JetStream | Daily 2 AM UTC | 7 days local, 30 days S3 | PVC + S3 | ~5 min |
| Velero (K8s state) | Daily 3 AM UTC | 30 days | S3 | ~15 min |
| Redis | Not backed up | N/A | N/A | Rebuild on deploy |

**One-liner health check:**
```bash
kubectl get cronjob,job -n kgents-agents -l app.kubernetes.io/name=nats-backup && aws s3 ls s3://kgents-dr-backups/nats/ 2>/dev/null | tail -1 || echo "S3 not configured"
```

### Service Level Indicators (SLIs)

| SLI | Target | Measurement | Alert Threshold |
|-----|--------|-------------|-----------------|
| **Backup Freshness** | < 25 hours | `time() - last_successful_backup_time` | Warning: 25h, Critical: 48h |
| **Backup Success Rate** | > 99% | `successful / total` over 30 days | Warning: < 99%, Critical: < 95% |
| **Recovery Time Objective (RTO)** | < 15 min | Manual restore drill results | N/A (drill-based) |
| **Recovery Point Objective (RPO)** | < 24 hours | Backup schedule (daily 2 AM UTC) | Alert on 2 missed backups |
| **Off-site Replication Lag** | < 48 hours | `time() - last_s3_upload` | Warning: 48h, Critical: 72h |

**Baseline Measurements (as of 2025-12-14):**
- Local backup time: ~30 seconds (empty JetStream)
- S3 upload time: Pending S3 bucket configuration
- Restore time: ~5 minutes (tested with manual restore)

**Dashboard:** `kgents SaaS Infrastructure` → `Backup Health` row

### NATS JetStream Backup

Backups run daily at 2 AM UTC via CronJob.

**Storage Locations:**
- Local: `nats-backup-pvc` in `kgents-agents` (7-day retention)
- Remote: S3 bucket `kgents-dr-backups/nats/` (30-day retention, if configured)

#### Manual Backup

```bash
# Trigger manual backup
kubectl create job --from=cronjob/nats-backup nats-backup-manual -n kgents-agents

# Watch progress
kubectl logs -f job/nats-backup-manual -n kgents-agents

# List local backups
kubectl exec -n kgents-agents deploy/nats -- ls -la /backups/

# List S3 backups (if configured)
aws s3 ls s3://kgents-dr-backups/nats/ --human-readable
```

#### Restore from Local Backup

```bash
# List available local backups
kubectl exec -n kgents-agents -it $(kubectl get pods -n kgents-agents -l app.kubernetes.io/name=nats -o jsonpath='{.items[0].metadata.name}') -- ls /backups/

# Run restore (replace with actual backup filename)
kubectl exec -n kgents-agents -it $(kubectl get pods -n kgents-agents -l app.kubernetes.io/name=nats -o jsonpath='{.items[0].metadata.name}') -- /scripts/restore.sh 20251214-020000.tar.gz
```

#### Restore from S3 Backup (Cross-Region DR)

Use this procedure when primary region is unavailable or for DR testing.

```bash
# 1. List available S3 backups
aws s3 ls s3://kgents-dr-backups/nats/ --human-readable

# 2. Download backup to local PVC
# (From inside a pod with S3 access)
kubectl run s3-restore --image=amazon/aws-cli:latest --rm -it \
  --env="AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" \
  --env="AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" \
  -- sh -c "
    aws s3 cp s3://kgents-dr-backups/nats/20251214-020000.tar.gz /tmp/
    ls -la /tmp/*.tar.gz
  "

# 3. Copy to NATS backup PVC
kubectl cp /tmp/20251214-020000.tar.gz kgents-agents/nats-0:/backups/

# 4. Run restore script
kubectl exec -n kgents-agents -it nats-0 -- /scripts/restore.sh 20251214-020000.tar.gz
```

**Alternative: Direct S3 restore with temporary pod**

```bash
# Create a restore job that downloads from S3 and restores
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: nats-restore-from-s3
  namespace: kgents-agents
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: restore
          image: natsio/nats-box:0.14.1
          command: ["/bin/sh", "-c"]
          args:
            - |
              # Download from S3
              apk add --no-cache python3 py3-pip
              pip3 install awscli
              aws s3 cp s3://kgents-dr-backups/nats/20251214-020000.tar.gz /backups/
              # Restore
              /scripts/restore.sh 20251214-020000.tar.gz
          env:
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: nats-backup-s3
                  key: AWS_ACCESS_KEY_ID
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: nats-backup-s3
                  key: AWS_SECRET_ACCESS_KEY
            - name: AWS_DEFAULT_REGION
              valueFrom:
                secretKeyRef:
                  name: nats-backup-s3
                  key: AWS_DEFAULT_REGION
          volumeMounts:
            - name: backup-storage
              mountPath: /backups
            - name: backup-scripts
              mountPath: /scripts
      volumes:
        - name: backup-storage
          persistentVolumeClaim:
            claimName: nats-backup-pvc
        - name: backup-scripts
          configMap:
            name: nats-backup-script
            defaultMode: 0755
EOF

# Watch progress
kubectl logs -f job/nats-restore-from-s3 -n kgents-agents
```

**Important Notes:**
- Restore only recovers stream/consumer **configuration**, not message data
- For full message recovery, use NATS native `nats stream restore` with filesystem backup
- Test restore in a non-production namespace first
- S3 backups have longer retention (30 days) than local (7 days)

#### Backup Verification

```bash
# Check backup CronJob status
kubectl get cronjob nats-backup -n kgents-agents

# View recent backup jobs
kubectl get jobs -n kgents-agents -l app.kubernetes.io/name=nats-backup

# Check local backup PVC usage
kubectl exec -n kgents-agents deploy/nats -- du -sh /backups/

# Verify S3 backup exists (most recent)
aws s3 ls s3://kgents-dr-backups/nats/ --human-readable | tail -1
```

### Velero Cluster State Backup

Velero backs up Kubernetes resources and PVCs daily at 3 AM UTC.

**Storage Location:** S3 bucket `kgents-dr-backups/velero/` (30-day retention)

#### Manual Backup

```bash
# Create manual backup
velero backup create manual-backup-$(date +%Y%m%d) \
  --include-namespaces kgents-triad,kgents-agents

# Watch progress
velero backup describe manual-backup-$(date +%Y%m%d) --details

# List all backups
velero backup get
```

#### Restore from Velero Backup

```bash
# List available backups
velero backup get

# Describe a specific backup
velero backup describe daily-kgents-backup-20251214 --details

# Full restore (to same namespaces)
velero restore create --from-backup daily-kgents-backup-20251214

# Restore to different namespaces (staging test)
velero restore create --from-backup daily-kgents-backup-20251214 \
  --namespace-mappings kgents-agents:kgents-agents-staging,kgents-triad:kgents-triad-staging

# Watch restore progress
velero restore describe <restore-name> --details
```

#### Restore Specific Resources

```bash
# Restore only ConfigMaps and Secrets
velero restore create --from-backup daily-kgents-backup-20251214 \
  --include-resources configmaps,secrets

# Restore only a specific namespace
velero restore create --from-backup daily-kgents-backup-20251214 \
  --include-namespaces kgents-agents
```

#### Velero Verification

```bash
# Check Velero pods
kubectl get pods -n velero

# Check backup storage location status
velero backup-location get

# Check schedule status
velero schedule get

# Check most recent backup
velero backup get | head -2
```

### Redis Backup (Future)

Redis backup is not currently configured. Data in Redis is primarily idempotency keys with short TTL. Loss of Redis data results in:
- Potential duplicate webhook processing (mitigated by Stripe idempotency)
- Need to rebuild rate limit counters

### Backup Troubleshooting

Common backup issues and resolutions:

#### CronJob Not Running

**Symptoms:** No recent jobs in `kubectl get jobs -n kgents-agents`

**Diagnosis:**
```bash
# Check CronJob status
kubectl get cronjob nats-backup -n kgents-agents -o yaml | grep -A5 "status:"

# Check for scheduling issues
kubectl describe cronjob nats-backup -n kgents-agents | grep -A10 "Events:"
```

**Resolution:**
```bash
# Verify CronJob exists
kubectl get cronjob nats-backup -n kgents-agents

# If missing, apply manifests
kubectl apply -k impl/claude/infra/k8s/manifests/nats/

# Trigger manual backup to verify
kubectl create job --from=cronjob/nats-backup test-backup -n kgents-agents
```

#### Backup Job Failing

**Symptoms:** Job status shows `Failed`, pods in `Error` state

**Diagnosis:**
```bash
# View job logs
kubectl logs -n kgents-agents -l job-name=nats-backup-xxxxx

# Check pod events
kubectl describe pod -n kgents-agents -l job-name=nats-backup-xxxxx
```

**Common Causes:**

| Error Message | Cause | Resolution |
|--------------|-------|------------|
| `PVC not found` | Backup PVC missing | `kubectl apply -k manifests/nats/` |
| `connection refused` | NATS not running | Check NATS StatefulSet health |
| `permission denied` | Script not executable | ConfigMap mode issue, reapply |
| `No space left` | PVC full | Increase PVC size or run cleanup |

#### S3 Upload Failing

**Symptoms:** Backup completes but no files in S3

**Diagnosis:**
```bash
# Check if S3 credentials configured
kubectl get secret nats-backup-s3 -n kgents-agents -o json | jq '.data | keys'

# Test S3 access
kubectl run s3-test --image=amazon/aws-cli:latest --rm -it \
  --env-from=secret/nats-backup-s3 \
  -- s3 ls s3://kgents-dr-backups/
```

**Common Causes:**

| Error Message | Cause | Resolution |
|--------------|-------|------------|
| `S3/GCS upload skipped` | Secret not configured | Apply `backup-s3-secret.yaml` |
| `AccessDenied` | IAM policy issue | Verify `iam-policy.json` applied |
| `NoSuchBucket` | Bucket doesn't exist | Create bucket in AWS/GCP console |
| `Timeout` | Network policy blocking | Check egress rules for S3 |

#### Restore Failing

**Symptoms:** Restore script errors, streams not recreated

**Diagnosis:**
```bash
# Check restore logs
kubectl logs -f job/nats-restore -n kgents-agents

# Verify backup integrity
kubectl exec -n kgents-agents nats-0 -- tar -tzf /backups/<backup>.tar.gz
```

**Common Causes:**

| Error Message | Cause | Resolution |
|--------------|-------|------------|
| `Archive corrupt` | Incomplete backup | Use older backup |
| `Stream already exists` | Partial restore | Delete existing streams first |
| `Invalid JSON` | Format incompatibility | Check NATS version match |

#### PVC Full / Cleanup Not Running

**Symptoms:** Backup fails with disk space error

**Diagnosis:**
```bash
# Check PVC usage
kubectl exec -n kgents-agents nats-0 -- df -h /backups

# List backups
kubectl exec -n kgents-agents nats-0 -- ls -la /backups/
```

**Resolution:**
```bash
# Manual cleanup (delete backups older than 3 days)
kubectl exec -n kgents-agents nats-0 -- \
  find /backups -name "*.tar.gz" -mtime +3 -delete

# Verify space freed
kubectl exec -n kgents-agents nats-0 -- df -h /backups
```

### Degraded Mode Operations

What happens when components are unavailable:

#### S3 Unavailable

**Impact:** Backups continue locally; no off-site copy
**Detection:** Check job logs for "S3/GCS upload skipped"
**Action:**
- Monitor local backup retention (7 days)
- Prioritize S3 connectivity fix if outage > 3 days
- Consider manual backup copy: `kubectl cp kgents-agents/nats-0:/backups ./local-backup/`

#### NATS Unavailable

**Impact:** Backup job fails; no new backups created
**Detection:** Job status `Failed`, logs show connection errors
**Action:**
- Fix NATS cluster first (see NATS section)
- Backups will resume automatically when NATS recovers
- If prolonged, verify last successful backup is recent

#### PVC Approaching Capacity

**Impact:** New backups may fail; retention cleanup may fail
**Detection:** `df -h /backups` shows > 80% usage
**Action:**
```bash
# Check current usage
kubectl exec -n kgents-agents nats-0 -- du -sh /backups/*

# Manual cleanup if needed
kubectl exec -n kgents-agents nats-0 -- \
  find /backups -name "*.tar.gz" -mtime +3 -delete

# Consider PVC resize if recurring
kubectl edit pvc nats-backup-pvc -n kgents-agents
```

#### Velero Unavailable

**Impact:** K8s resource backups stop; NATS data backups unaffected
**Detection:** `velero backup-location get` shows unavailable
**Action:**
- Check Velero pods: `kubectl get pods -n velero`
- Check S3 connectivity from Velero namespace
- NATS backup is independent; data still protected

### S3 Setup Prerequisites (Platform Engineers)

Complete these steps before enabling S3 backup integration:

#### Step 1: Create S3 Bucket

```bash
# Create bucket with versioning
aws s3api create-bucket \
  --bucket kgents-dr-backups \
  --region us-west-2 \
  --create-bucket-configuration LocationConstraint=us-west-2

aws s3api put-bucket-versioning \
  --bucket kgents-dr-backups \
  --versioning-configuration Status=Enabled

# Set lifecycle policy for 30-day retention
aws s3api put-bucket-lifecycle-configuration \
  --bucket kgents-dr-backups \
  --lifecycle-configuration file://lifecycle.json
```

`lifecycle.json`:
```json
{
  "Rules": [
    {
      "ID": "nats-backup-expiration",
      "Status": "Enabled",
      "Filter": {"Prefix": "nats/"},
      "Expiration": {"Days": 30}
    },
    {
      "ID": "velero-backup-expiration",
      "Status": "Enabled",
      "Filter": {"Prefix": "velero/"},
      "Expiration": {"Days": 30}
    }
  ]
}
```

#### Step 2: Create IAM Policy

Apply the least-privilege policy from `manifests/nats/iam-policy.json`:

```bash
# Create policy
aws iam create-policy \
  --policy-name kgents-backup-policy \
  --policy-document file://impl/claude/infra/k8s/manifests/nats/iam-policy.json

# Create user for backups
aws iam create-user --user-name kgents-backup-sa

# Attach policy
aws iam attach-user-policy \
  --user-name kgents-backup-sa \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/kgents-backup-policy

# Create access key
aws iam create-access-key --user-name kgents-backup-sa > credentials.json
```

#### Step 3: Create Kubernetes Secret

```bash
# Create secret from credentials
kubectl create secret generic nats-backup-s3 \
  -n kgents-agents \
  --from-literal=AWS_ACCESS_KEY_ID=$(jq -r '.AccessKey.AccessKeyId' credentials.json) \
  --from-literal=AWS_SECRET_ACCESS_KEY=$(jq -r '.AccessKey.SecretAccessKey' credentials.json) \
  --from-literal=AWS_DEFAULT_REGION=us-west-2 \
  --from-literal=S3_BUCKET=kgents-dr-backups

# Verify secret exists
kubectl get secret nats-backup-s3 -n kgents-agents
```

#### Step 4: Verify Integration

```bash
# Trigger manual backup
kubectl create job --from=cronjob/nats-backup nats-backup-s3-test -n kgents-agents

# Watch logs for S3 upload
kubectl logs -f job/nats-backup-s3-test -n kgents-agents

# Verify in S3
aws s3 ls s3://kgents-dr-backups/nats/ --human-readable
```

#### Checklist

- [ ] S3 bucket created with versioning enabled
- [ ] Lifecycle policy applied (30-day retention)
- [ ] IAM policy created from `iam-policy.json`
- [ ] IAM user created with policy attached
- [ ] Kubernetes secret created with credentials
- [ ] Manual backup test shows S3 upload successful
- [ ] S3 backup visible in bucket listing

---

## Disaster Recovery

> Cross-region failover procedures for major outages. See `docs/saas/dr-contracts.md` for RPO/RTO targets.

### Recovery Targets

| Component | RTO | RPO | Priority |
|-----------|-----|-----|----------|
| API | < 5 min | N/A | P0 |
| NATS Streams | < 15 min | < 5 min | P0 |
| Secrets/Config | < 30 min | < 1 hour | P0 |
| Observability | < 1 hour | N/A | P2 |

### Failover Decision Checklist

Before initiating failover, confirm:

- [ ] Primary region confirmed unreachable (not just degraded)
- [ ] Multiple health checks failing (not transient)
- [ ] Estimated recovery time in primary > RTO targets
- [ ] DR region verified healthy
- [ ] Stakeholders notified

### Failover Procedure

#### Step 1: Declare DR Event

```bash
# Notify team
echo "DR EVENT DECLARED: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> /tmp/dr-log.txt

# Record start time for RTO measurement
export DR_START=$(date +%s)
```

#### Step 2: DNS Failover

```bash
# Option A: Route53 (if using AWS)
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.kgents.io",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "$DR_ALB_ZONE",
          "DNSName": "$DR_ALB_DNS",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'

# Option B: CloudFlare
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"content": "$DR_IP"}'
```

#### Step 3: Verify DR Region Health

```bash
# Wait for DNS propagation (60s TTL)
sleep 60

# Verify API health in DR
curl -sf https://api.kgents.io/health || echo "WARN: Health check failed"
curl -sf https://api.kgents.io/health/saas || echo "WARN: SaaS health failed"

# Verify NATS mirror status
kubectl --context=dr exec -n kgents-agents nats-0 -- \
  nats stream info AGENTESE_MIRROR --json | jq '.mirror.lag'
```

#### Step 4: Verify State Sync

```bash
# Check secrets are current
kubectl --context=dr get externalsecret -n kgents-triad -o wide

# Check ArgoCD sync status
argocd --server $DR_ARGOCD app get kgents-saas --output json | jq '.status.sync.status'
```

#### Step 5: Record Recovery Time

```bash
DR_END=$(date +%s)
RTO_ACTUAL=$((DR_END - DR_START))

echo "RTO: ${RTO_ACTUAL}s (target: 300s)"

if [ $RTO_ACTUAL -lt 300 ]; then
  echo "PASS: Within RTO target"
else
  echo "FAIL: Exceeded RTO target"
fi
```

#### Step 6: Post-Failover Communication

- [ ] Update status page (status.kgents.io)
- [ ] Notify affected customers
- [ ] Alert internal stakeholders
- [ ] Log incident in incident tracker

### Failback Procedure

After primary region recovers:

#### Step 1: Verify Primary Health

```bash
# Check all pods healthy
kubectl --context=primary get pods -n kgents-triad
kubectl --context=primary get pods -n kgents-agents

# Verify NATS cluster
kubectl --context=primary exec -n kgents-agents nats-0 -- nats server check
```

#### Step 2: Resync State

```bash
# Trigger ArgoCD sync
argocd --server $PRIMARY_ARGOCD app sync kgents-saas

# Verify secrets synced
kubectl --context=primary get externalsecret -n kgents-triad -o wide
```

#### Step 3: Gradual Traffic Shift

```bash
# Route53: Enable weighted routing
# Start with 10% traffic to primary
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://weighted-10-primary.json

# Monitor error rates for 15 minutes
# If healthy, increase to 50%, then 100%
```

#### Step 4: Complete Failback

```bash
# Full traffic to primary
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://full-primary.json

# Verify
dig api.kgents.io +short
```

### Communication Templates

#### Status Page Update (Failover)

```
Title: Service Degradation - Failover in Progress
Status: Investigating → Identified → Monitoring

We are experiencing issues with our primary region and have initiated
failover to our disaster recovery site. Service may be briefly interrupted.

Expected resolution: Within 15 minutes
Impact: API requests may fail briefly during transition

Updates will be posted every 5 minutes.
```

#### Status Page Update (Recovered)

```
Title: Service Restored
Status: Resolved

Failover to DR region complete. All services operating normally.
We are monitoring for any residual issues.

Root cause analysis will be shared within 24 hours.
```

### DR Drill Schedule

| Frequency | Scope | Environment |
|-----------|-------|-------------|
| Monthly | DNS failover only | Staging |
| Quarterly | Full DR drill | Staging |
| Annually | Full DR drill | Production (planned maintenance) |

### DR Metrics to Track

After each DR event or drill:

- [ ] Time to detect (TTD)
- [ ] Time to failover (RTO actual)
- [ ] Data loss measured (RPO actual)
- [ ] Customer impact duration
- [ ] Lessons learned documented

See: `docs/saas/dr-contracts.md` for full contract specifications.

---

## Incident Response

### NATS Circuit Breaker Open

**Symptoms:**
- `/health/saas` shows `nats.status: circuit_open`
- Dashboard shows `kgents_nats_circuit_state = 1`
- Fallback queue depth increasing

**Response:**

1. Check NATS cluster health
   ```bash
   kubectl get pods -n kgents-agents -l app.kubernetes.io/name=nats
   kubectl logs -n kgents-agents nats-0 -c nats --tail=50
   ```

2. Check network connectivity
   ```bash
   kubectl exec -n kgents-agents deploy/kgents-api -- nc -zv nats.kgents-agents.svc 4222
   ```

3. If NATS is healthy, circuit will auto-recover in 30s

4. If NATS is down, restart cluster
   ```bash
   kubectl rollout restart statefulset/nats -n kgents-agents
   ```

### OpenMeter Flush Failures

**Symptoms:**
- `kgents_openmeter_flush_errors_total` increasing
- Buffer depth growing
- Events not appearing in OpenMeter dashboard

**Response:**

1. Check OpenMeter health
   ```bash
   curl -H "Authorization: Bearer $OPENMETER_API_KEY" \
     https://openmeter.cloud/api/v1/meters
   ```

2. Check API logs for errors
   ```bash
   kubectl logs -n kgents-agents deploy/kgents-api --tail=100 | grep -i openmeter
   ```

3. Verify API key is valid

4. If API key expired, rotate:
   ```bash
   kubectl create secret generic kgents-api-secrets \
     -n kgents-agents \
     --from-literal=OPENMETER_API_KEY=om_live_new_xxx \
     --dry-run=client -o yaml | kubectl apply -f -
   kubectl rollout restart deployment/kgents-api -n kgents-agents
   ```

### Stripe Webhook Failures

**Symptoms:**
- `kgents_stripe_webhooks_errors_total` increasing
- `/webhooks/stripe/health` shows errors
- Stripe dashboard shows failed deliveries

**Response:**

1. Check webhook secret
   ```bash
   kubectl get secret kgents-api-secrets -n kgents-agents -o jsonpath='{.data.STRIPE_WEBHOOK_SECRET}' | base64 -d
   ```

2. Verify in Stripe Dashboard → Developers → Webhooks

3. Check for signature verification errors in logs
   ```bash
   kubectl logs -n kgents-agents deploy/kgents-api --tail=100 | grep -i stripe
   ```

4. Rotate webhook secret if compromised:
   - Generate new secret in Stripe Dashboard
   - Update Kubernetes secret
   - Restart API

---

## Common Issues

### Issue: "SaaS infrastructure not available"

**Cause:** SaaS config module not imported

**Solution:**
- Ensure `protocols.config` module is accessible
- Check `PYTHONPATH` in deployment

### Issue: "NATS connection refused"

**Cause:** NATS not running or wrong address

**Solution:**
1. Check NATS pods are running
2. Verify `NATS_SERVERS` environment variable
3. Check network policies allow traffic

### Issue: "OpenMeter 401 Unauthorized"

**Cause:** Invalid or expired API key

**Solution:**
1. Verify API key in OpenMeter dashboard
2. Update secret and restart

### Issue: "Circuit breaker stuck open"

**Cause:** NATS failures not recovering

**Solution:**
1. Check NATS cluster health
2. Manually reset circuit (requires code change or restart)
3. Increase `failure_threshold` if false positives

### Issue: "Fallback queue full"

**Cause:** NATS down for extended period

**Solution:**
1. Fix NATS cluster
2. Events in fallback queue will be lost if API restarts
3. Consider increasing queue size in NATSBridge config

---

## Monitoring Alerts

### Recommended Alert Rules

```yaml
groups:
  - name: kgents-saas
    rules:
      - alert: NATSCircuitOpen
        expr: kgents_nats_circuit_state == 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: NATS circuit breaker is open
          description: NATS circuit breaker has been open for 5 minutes

      - alert: OpenMeterFlushErrors
        expr: rate(kgents_openmeter_flush_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: OpenMeter flush errors detected
          description: OpenMeter is experiencing flush errors

      - alert: StripeWebhookErrors
        expr: rate(kgents_stripe_webhooks_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: Stripe webhook errors detected
          description: Stripe webhooks are failing

      - alert: HighAPILatency
        expr: histogram_quantile(0.95, rate(kgents_api_request_latency_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High API latency detected
          description: 95th percentile API latency is above 2 seconds
```

---

## Contact

For escalation:
- Infrastructure: Check `impl/claude/infra/k8s/` for deployment details
- Billing: Check `impl/claude/protocols/billing/` for integration code
- API: Check `impl/claude/protocols/api/` for endpoint code
