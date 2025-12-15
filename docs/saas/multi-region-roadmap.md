# Multi-Region Migration Roadmap

> Phase 10 Deliverable: Sequenced migration path from single-region to disaster-ready infrastructure.

## Executive Summary

This roadmap outlines four phases to achieve multi-region disaster recovery capability for kgents SaaS. The recommended approach is **Active-Passive** with NATS stream mirroring, prioritizing simplicity and cost-effectiveness over full active-active redundancy.

**Target State:**
- RTO < 5 minutes (API), < 15 minutes (NATS)
- RPO < 5 minutes
- ~$340/month additional cost

## Current State (Phase 10)

| Aspect | Status |
|--------|--------|
| Single-region deployment | Complete |
| DR contracts defined | Complete |
| Research synthesis | Complete |
| Cost estimates | Complete |
| Migration roadmap | This document |

See: `docs/saas/architecture-current.md` for detailed topology.

---

## Phase 11: External Backup (Foundation)

> **Goal:** Establish cross-region backup foundation before deploying DR infrastructure.

### Objective

Move from local-only backups to cross-region durable storage, enabling point-in-time recovery even if primary region is destroyed.

### Deliverables

| Item | Description | Effort |
|------|-------------|--------|
| S3/GCS bucket | Cross-region backup destination | 1-2 hours |
| NATS backup to S3 | Modify CronJob to upload to S3 | 2-4 hours |
| Velero installation | Cluster state backup tool | 2-4 hours |
| Velero schedules | Daily cluster snapshots | 1-2 hours |
| Restore runbook | Document recovery procedures | 2-3 hours |

### Architecture

```
Primary Region                    Cross-Region Storage
┌─────────────────┐              ┌─────────────────┐
│  NATS Cluster   │──CronJob────►│  S3/GCS Bucket  │
│                 │              │  (nats-backups) │
└─────────────────┘              └─────────────────┘
                                         ▲
┌─────────────────┐                      │
│  Velero         │──────────────────────┘
│  (cluster state)│
└─────────────────┘
```

### Implementation Details

#### 1. Create Backup Bucket

```bash
# AWS S3
aws s3 mb s3://kgents-dr-backups --region us-west-2
aws s3api put-bucket-versioning \
  --bucket kgents-dr-backups \
  --versioning-configuration Status=Enabled

# GCS
gcloud storage buckets create gs://kgents-dr-backups \
  --location=us-west1 \
  --uniform-bucket-level-access
```

#### 2. Update NATS Backup CronJob

```yaml
# Add S3 upload step to backup-cronjob.yaml
containers:
  - name: backup
    image: nats:2.10-alpine
    command:
      - /bin/sh
      - -c
      - |
        nats stream backup AGENTESE /backups/$(date +%Y%m%d).tar.gz
        aws s3 cp /backups/$(date +%Y%m%d).tar.gz s3://kgents-dr-backups/nats/
```

#### 3. Install Velero

```bash
velero install \
  --provider aws \
  --bucket kgents-dr-backups \
  --backup-location-config region=us-west-2 \
  --snapshot-location-config region=us-west-2 \
  --plugins velero/velero-plugin-for-aws:v1.8.0

# Create daily schedule
velero schedule create daily-cluster-backup \
  --schedule="0 3 * * *" \
  --include-namespaces kgents-triad,kgents-agents
```

### Success Criteria

- [ ] NATS backups appear in S3/GCS within 24 hours
- [ ] Velero backup completes successfully
- [ ] Restore test from S3 to staging namespace succeeds
- [ ] Runbook reviewed and approved

### Dependencies

- AWS/GCP account with cross-region bucket access
- IAM credentials for backup service account

### Estimated Effort

**Total: 1-2 days**

---

## Phase 12: Cross-Region DNS Setup

> **Goal:** Establish DNS infrastructure for automated failover.

### Objective

Configure health-checked DNS routing that can automatically redirect traffic to DR region when primary fails.

### Deliverables

| Item | Description | Effort |
|------|-------------|--------|
| DNS provider selection | Route53 or CloudFlare | 1 hour |
| Health check endpoints | Configure health probes | 1-2 hours |
| Failover DNS records | Primary + failover configuration | 2-3 hours |
| TTL optimization | Reduce TTL for faster failover | 1 hour |
| Failover testing | Validate DNS cutover timing | 2-3 hours |

### Architecture

```
                CloudFlare / Route53
                ┌─────────────────┐
                │  api.kgents.io  │
                │                 │
                │  Health Check   │
                │  every 30s      │
                └────────┬────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼ (Primary)                     ▼ (Failover)
┌─────────────────┐             ┌─────────────────┐
│  us-east-1      │             │  us-west-2      │
│  (Active)       │             │  (Standby)      │
│                 │             │                 │
│  Health: /health│             │  Health: /health│
└─────────────────┘             └─────────────────┘
```

### Implementation Details

#### Route53 Configuration

```yaml
# Primary record
Type: A
Name: api.kgents.io
RoutingPolicy: Failover
SetIdentifier: primary
FailoverRecordType: PRIMARY
HealthCheckId: $PRIMARY_HEALTH_CHECK
TTL: 60
Value: $PRIMARY_ALB_IP

# Failover record
Type: A
Name: api.kgents.io
RoutingPolicy: Failover
SetIdentifier: dr
FailoverRecordType: SECONDARY
TTL: 60
Value: $DR_ALB_IP
```

#### Health Check Configuration

```yaml
HealthCheck:
  Type: HTTPS
  FullyQualifiedDomainName: primary.api.kgents.io
  Port: 443
  ResourcePath: /health
  RequestInterval: 30
  FailureThreshold: 3
```

### Success Criteria

- [ ] Health checks active and passing
- [ ] Failover triggers within 90 seconds of primary failure
- [ ] DNS propagation completes within TTL window
- [ ] Failback tested and documented

### Dependencies

- Phase 11 complete (backup foundation)
- DR region cluster exists (Phase 13 dependency)

### Estimated Effort

**Total: 1 day**

---

## Phase 13: Standby Cluster Deployment

> **Goal:** Deploy warm standby cluster in DR region with NATS stream mirroring.

### Objective

Create a near-real-time replica of production infrastructure that can assume traffic within RTO targets.

### Deliverables

| Item | Description | Effort |
|------|-------------|--------|
| DR cluster provisioning | K8s cluster in secondary region | 2-4 hours |
| Namespace mirroring | ArgoCD ApplicationSet | 2-3 hours |
| NATS gateway setup | Cross-cluster gateway | 4-6 hours |
| Stream mirroring | Mirror critical streams | 2-3 hours |
| Secret sync | External Secrets cross-region | 2-3 hours |
| Failover testing | End-to-end DR drill | 4-6 hours |

### Architecture

```
Region 1 (Primary)                    Region 2 (DR)
┌─────────────────────────┐          ┌─────────────────────────┐
│                         │          │                         │
│  ┌─────────────────┐    │          │    ┌─────────────────┐  │
│  │   kgent-api     │    │          │    │   kgent-api     │  │
│  │   (active)      │    │          │    │   (standby)     │  │
│  └────────┬────────┘    │          │    └────────┬────────┘  │
│           │             │          │             │           │
│  ┌────────┴────────┐    │          │    ┌────────┴────────┐  │
│  │  NATS Cluster   │◄───┼──Gateway─┼───►│  NATS Cluster   │  │
│  │  (origin)       │    │          │    │  (mirror)       │  │
│  │                 │    │          │    │                 │  │
│  │  AGENTESE ──────┼────┼─Mirror───┼───►│  AGENTESE_MIR   │  │
│  │  EVENTS ────────┼────┼─Mirror───┼───►│  EVENTS_MIR     │  │
│  └─────────────────┘    │          │    └─────────────────┘  │
│                         │          │                         │
│  ┌─────────────────┐    │          │    ┌─────────────────┐  │
│  │    Redis        │    │          │    │    Redis        │  │
│  └─────────────────┘    │          │    └─────────────────┘  │
│                         │          │                         │
└─────────────────────────┘          └─────────────────────────┘
```

### Implementation Details

#### 1. Provision DR Cluster

```bash
# EKS example
eksctl create cluster \
  --name kgents-dr \
  --region us-west-2 \
  --nodegroup-name standard \
  --node-type t3.medium \
  --nodes 3

# Apply base manifests
kubectl --context=dr apply -f impl/claude/infra/k8s/manifests/namespace.yaml
```

#### 2. Configure NATS Gateway

```yaml
# nats-config in DR cluster
gateway:
  name: dr
  gateways:
    - name: primary
      urls:
        - nats://nats-0.nats-headless.kgents-agents.svc:7222
        - nats://nats-1.nats-headless.kgents-agents.svc:7222
        - nats://nats-2.nats-headless.kgents-agents.svc:7222
    - name: dr
      urls:
        - nats://nats-0.nats-headless.kgents-agents.svc:7222
```

#### 3. Create Stream Mirrors

```bash
# Connect to DR NATS cluster
nats --context=dr stream add AGENTESE_MIRROR \
  --mirror AGENTESE \
  --mirror-filter-subject "agentese.>" \
  --storage file \
  --retention limits \
  --max-msgs 1000000

nats --context=dr stream add EVENTS_MIRROR \
  --mirror EVENTS \
  --storage file
```

#### 4. ArgoCD ApplicationSet

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: kgents-multiregion
spec:
  generators:
    - list:
        elements:
          - cluster: primary
            url: https://primary.k8s.kgents.io
          - cluster: dr
            url: https://dr.k8s.kgents.io
  template:
    metadata:
      name: 'kgents-{{cluster}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/kgents/kgents
        path: impl/claude/infra/k8s/manifests
      destination:
        server: '{{url}}'
```

### Success Criteria

- [ ] DR cluster operational
- [ ] NATS gateway connected between regions
- [ ] Stream mirrors lag < 3 minutes under load
- [ ] Secrets sync validated
- [ ] Full DR drill completes within RTO targets

### Dependencies

- Phase 11 complete (backup infrastructure)
- Phase 12 complete (DNS failover ready)
- Budget approved (~$200/month for DR cluster)

### Estimated Effort

**Total: 3-5 days**

---

## Phase 14: Active-Active (Optional)

> **Goal:** Enable simultaneous traffic serving from both regions for latency optimization.

### Objective

Upgrade from Active-Passive to Active-Active for global latency optimization and zero-downtime failover. **Only pursue if business requirements justify additional complexity.**

### Prerequisites

- [ ] Phase 13 complete and stable for 30+ days
- [ ] Confirmed need for < 100ms global latency
- [ ] Budget approved (~$340/month additional)
- [ ] Engineering capacity for ongoing maintenance

### Deliverables

| Item | Description | Effort |
|------|-------------|--------|
| Global load balancer | CloudFlare/AWS Global Accelerator | 2-3 days |
| NATS Virtual Streams | Active-active message routing | 3-5 days |
| Conflict resolution | Idempotency key strategy | 2-3 days |
| Consistency testing | Validate no data loss | 2-3 days |
| Runbook updates | Multi-region operations | 1-2 days |

### Architecture

```
                 Global Load Balancer
                 ┌─────────────────┐
                 │  CloudFlare     │
                 │  Anycast        │
                 └────────┬────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
┌─────────────────────┐       ┌─────────────────────┐
│  Region 1           │       │  Region 2           │
│  (Active)           │       │  (Active)           │
│                     │       │                     │
│  API ───────────────┼───────┼──► API              │
│       │             │       │       │             │
│  NATS ◄─────────────┼───────┼─────► NATS          │
│  (Virtual Streams)  │       │  (Virtual Streams)  │
│                     │       │                     │
└─────────────────────┘       └─────────────────────┘
```

### Key Considerations

#### Consistency Model

Active-Active requires accepting eventual consistency:

| Operation | Consistency | Strategy |
|-----------|-------------|----------|
| Read | Local | Serve from nearest region |
| Write | Eventual | Conflict resolution via timestamps |
| Idempotency | Global | Distributed idempotency store |

#### When NOT to Pursue Active-Active

- Current traffic < 1000 req/min (single region sufficient)
- P99 latency acceptable at < 500ms globally
- Team lacks distributed systems expertise
- Budget constraints

### Estimated Effort

**Total: 2-3 weeks** (if pursued)

---

## Cost Summary

| Phase | One-Time | Monthly | Cumulative Monthly |
|-------|----------|---------|-------------------|
| Phase 10 (Current) | - | ~$340 | $340 |
| Phase 11: External Backup | $0 | +$20 (S3) | $360 |
| Phase 12: DNS Failover | $0 | +$5 (health checks) | $365 |
| Phase 13: Standby Cluster | $0 | +$200 (EKS) | $565 |
| Phase 14: Active-Active | $0 | +$200 (upgrade) | $765 |

**Recommended stopping point:** Phase 13 (~$565/month total)

---

## Dependency Graph

```
Phase 10 (Current)
    │
    ▼
Phase 11: External Backup
    │
    ├──────────────────┐
    ▼                  ▼
Phase 12: DNS      Phase 13: Standby
    │                  │
    └──────────────────┘
              │
              ▼
    Phase 14: Active-Active
         (Optional)
```

## Decision Points

| After Phase | Decision | Criteria |
|-------------|----------|----------|
| 11 | Proceed to 12-13? | Budget approved, RTO < 15min required |
| 13 | Proceed to 14? | Global latency requirements, > 10k daily users |

---

## References

- Current Architecture: `docs/saas/architecture-current.md`
- DR Contracts: `docs/saas/dr-contracts.md`
- Research Findings: `docs/saas/multi-region-research.md`
- Runbook: `docs/saas/runbook.md`

---

*Last Updated: 2025-12-14 | Phase 10: STRATEGIZE*
