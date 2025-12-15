# Current Architecture: Single-Region Deployment

> Phase 10 Documentation: Baseline for multi-region evaluation.

## Overview

kgents SaaS operates in a **single-region Kubernetes cluster** with the following topology:

```
                            Internet
                               │
                               ▼
                      ┌────────────────┐
                      │   Kong/Ingress │
                      │   (Gateway)    │
                      └───────┬────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
     ┌─────────────────┐             ┌─────────────────┐
     │   kgent-api     │             │   kgent-api     │
     │   (Replica 1)   │             │   (Replica 2)   │
     │   :8000         │             │   :8000         │
     └───────┬─────────┘             └────────┬────────┘
             │                                │
     ┌───────┴────────────────────────────────┴───────┐
     │                                                │
     ▼                                                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    NATS      │  │    Redis     │  │  Prometheus  │  │    Loki      │
│   Cluster    │  │   (Cache)    │  │   (Metrics)  │  │   (Logs)     │
│  (3 nodes)   │  │  (1 node)    │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

## Namespaces

| Namespace | Purpose | Components |
|-----------|---------|------------|
| `kgents-triad` | Core data services | API, Redis, Postgres, Kong |
| `kgents-agents` | Agent runtime | NATS cluster |
| `kgents-observability` | Monitoring | Prometheus, Grafana, Loki, Tempo, OTEL |

## Component Inventory

### 1. API Service (`kgent-api`)

**Location:** `kgents-triad` namespace

| Property | Value |
|----------|-------|
| Replicas | 2 |
| Image | `kgents/api:latest` |
| Port | 8000 |
| CPU Request/Limit | 100m / 500m |
| Memory Request/Limit | 256Mi / 512Mi |
| HPA | 2-10 replicas, CPU target 70% |
| PDB | minAvailable: 1 |

**Dependencies:**
- NATS (`nats.kgents-agents.svc:4222`)
- Redis (`triad-redis.kgents-triad.svc:6379`)
- OpenMeter (external SaaS)
- Stripe (external SaaS)

**Endpoints:**
- `/health` - Basic health check
- `/health/saas` - SaaS infrastructure status (NATS, OpenMeter)
- `/metrics` - Prometheus metrics
- `/webhooks/stripe` - Stripe webhook receiver

### 2. NATS Cluster

**Location:** `kgents-agents` namespace

| Property | Value |
|----------|-------|
| Replicas | 3 (StatefulSet) |
| Image | `nats:2.10-alpine` |
| Ports | 4222 (client), 6222 (cluster), 8222 (monitor) |
| CPU Request/Limit | 100m / 500m |
| Memory Request/Limit | 256Mi / 1Gi |
| Storage | 10Gi per node (PVC) |
| PDB | minAvailable: 2 |

**JetStream Streams:**
- `AGENTESE` - Agent-world interaction events
- `EVENTS` - System event bus

**Backup:**
- Daily CronJob at 02:00 UTC
- Retention: 7 days
- Storage: `nats-backup-pvc`

### 3. Redis Cache

**Location:** `kgents-triad` namespace

| Property | Value |
|----------|-------|
| Replicas | 1 |
| Image | `redis:7-alpine` |
| Port | 6379 |
| Memory | 128MB max (allkeys-lru) |
| CPU Request/Limit | 50m / 200m |
| Memory Request/Limit | 64Mi / 256Mi |

**Purpose:**
- Idempotency key store (Stripe webhooks)
- Rate limiting counters
- Session cache

**Note:** No persistence configured. Data loss acceptable (short TTL keys).

### 4. Observability Stack

**Location:** `kgents-observability` namespace

| Component | Purpose | Retention |
|-----------|---------|-----------|
| Prometheus | Metrics collection | 15 days |
| Grafana | Dashboards | N/A |
| Loki | Log aggregation | 7 days |
| Tempo | Distributed tracing | 7 days |
| OTEL Collector | Telemetry gateway | N/A |

**Alert Rules:** 8 configured (see `production-checklist.md`)

### 5. Network Policies

| Policy | Effect |
|--------|--------|
| `default-deny` | Block all inter-namespace traffic by default |
| `nats-policy` | Allow API → NATS on port 4222 |
| `redis-policy` | Allow API → Redis on port 6379 |

## External Dependencies

| Service | Purpose | Recovery |
|---------|---------|----------|
| OpenMeter | Usage metering | Buffer locally, retry with backoff |
| Stripe | Billing webhooks | Stripe retries for 72h |
| CloudFlare/Route53 | DNS | Manual failover |

## Current Backup/Recovery State

### What's Backed Up

| Component | Method | Frequency | Location |
|-----------|--------|-----------|----------|
| NATS streams | CronJob | Daily | Local PVC |
| K8s manifests | GitOps | On commit | GitHub |
| Secrets | External Secrets Operator | 5min sync | Cloud Secret Manager |

### What's NOT Backed Up

| Component | Risk | Mitigation |
|-----------|------|------------|
| Redis data | Short-TTL keys | Acceptable loss |
| In-flight NATS messages | Up to 5 min | Circuit breaker fallback |
| Grafana dashboards | Manual recreation | JSON in git repo |

### Recovery Targets (Current State)

| Component | RTO | RPO | Achievable? |
|-----------|-----|-----|-------------|
| API | < 5 min | N/A | Yes (HPA + PDB) |
| NATS | < 15 min | < 5 min | Partial (no DR region) |
| Secrets | < 30 min | < 1 hour | Yes (ESO sync) |

## Single Points of Failure

| SPOF | Impact | Phase 11+ Mitigation |
|------|--------|----------------------|
| Single region | Total outage | DR region |
| Redis (1 replica) | Cache miss | Redis Cluster or Sentinel |
| NATS backup PVC | Backup loss | Cross-region S3/GCS |

## Network Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ kgents-triad                                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │  API x2  │──│  Redis   │  │ Postgres │              │   │
│  │  └────┬─────┘  └──────────┘  └──────────┘              │   │
│  └───────┼──────────────────────────────────────────────────┘   │
│          │ NetworkPolicy: nats-policy                           │
│  ┌───────┼──────────────────────────────────────────────────┐   │
│  │ kgents-agents                                            │   │
│  │       ▼                                                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │  NATS-0  │──│  NATS-1  │──│  NATS-2  │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ kgents-observability                                     │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │Prometheus│ │ Grafana  │ │   Loki   │ │  Tempo   │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Resource Summary

| Component | vCPU (request) | Memory (request) | Storage |
|-----------|----------------|------------------|---------|
| API x2 | 200m | 512Mi | - |
| NATS x3 | 300m | 768Mi | 30Gi |
| Redis x1 | 50m | 64Mi | - |
| Prometheus | 100m | 512Mi | 50Gi |
| Grafana | 100m | 256Mi | 1Gi |
| Loki | 100m | 256Mi | 10Gi |
| Tempo | 100m | 256Mi | 10Gi |
| **Total** | **~1 vCPU** | **~2.5Gi** | **~100Gi** |

## Configuration References

- API Deployment: `impl/claude/infra/k8s/manifests/api/deployment.yaml`
- NATS StatefulSet: `impl/claude/infra/k8s/manifests/nats/statefulset.yaml`
- Redis: `impl/claude/infra/k8s/manifests/triad/03-redis.yaml`
- Network Policies: `impl/claude/infra/k8s/manifests/network-policies/`
- Observability: `impl/claude/infra/k8s/manifests/observability/`

---

*Last Updated: 2025-12-14 | Phase 10: STRATEGIZE*
