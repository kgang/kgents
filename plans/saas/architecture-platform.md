# kgents SaaS Platform Architecture

**Date**: December 14, 2025
**Phase**: DEVELOP
**Status**: Design Complete

---

## Executive Summary

This document defines the platform architecture for kgents SaaS, based on research in `research-architecture.md`. The architecture follows a hybrid tiered approach with shared control plane and tiered data planes, enabling cost-efficient pooled infrastructure for standard customers while providing isolated silos for enterprise tenants.

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EDGE LAYER                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ CloudFlare  │  │    WAF      │  │  DDoS       │  │    CDN      │        │
│  │   DNS       │  │  (OWASP)    │  │ Protection  │  │  (Static)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY (Kong)                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  JWT Auth   │  │ Rate Limit  │  │  Metering   │  │   Routing   │        │
│  │  Validation │  │ (Per-Tenant)│  │   Hooks     │  │   Rules     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│   CONTROL PLANE       │ │    AGENTESE PLANE     │ │    K-GENT PLANE       │
│  (Shared Services)    │ │  (Agent Execution)    │ │  (Persona Service)    │
├───────────────────────┤ ├───────────────────────┤ ├───────────────────────┤
│ • Auth Service        │ │ • AGENTESE Runtime    │ │ • K-gent Sessions     │
│ • Billing Service     │ │ • Logos Invoker       │ │ • Persona State       │
│ • Tenant Management   │ │ • Context Handlers    │ │ • Memory Service      │
│ • Usage Metering      │ │ • Tool Execution      │ │ • Witness/Trace       │
│ • Admin Dashboard     │ │ • LLM Orchestration   │ │ • Dialogue Manager    │
└───────────────────────┘ └───────────────────────┘ └───────────────────────┘
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA PLANE (Tiered)                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  POOL TIER (Standard/Pro)                                            │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  PostgreSQL 15+ with Row-Level Security                      │    │   │
│  │  │  • Shared database, tenant isolation via RLS                 │    │   │
│  │  │  • Connection pooling (PgBouncer)                            │    │   │
│  │  │  • Indexed on tenant_id                                      │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  SILO TIER (Enterprise)                                              │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐           │   │
│  │  │ Tenant A DB   │  │ Tenant B DB   │  │ Tenant N DB   │           │   │
│  │  │ (Isolated)    │  │ (Isolated)    │  │ (Isolated)    │           │   │
│  │  └───────────────┘  └───────────────┘  └───────────────┘           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tenant Isolation Strategy

### 2.1 Hybrid Tiered Model

| Tier | Isolation Model | Database | Use Case |
|------|-----------------|----------|----------|
| **Free/Starter** | Pool (Shared + RLS) | Shared PostgreSQL | Indie developers, prototypes |
| **Pro/Team** | Pool (Shared + RLS) | Shared PostgreSQL | Small teams, production workloads |
| **Enterprise** | Silo (Database-per-tenant) | Dedicated PostgreSQL | Regulated industries, large orgs |

### 2.2 Row-Level Security Implementation

```sql
-- Enable RLS on tenant-scoped tables
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_events ENABLE ROW LEVEL SECURITY;

-- Create tenant isolation policy
CREATE POLICY tenant_isolation ON agents
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- Session context setup (called on each connection)
CREATE OR REPLACE FUNCTION set_tenant_context(p_tenant_id uuid)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_tenant', p_tenant_id::text, true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 2.3 Tenant Context Flow

```
1. Request arrives at API Gateway
2. JWT validated → tenant_id extracted from claims
3. Request forwarded to service with X-Tenant-ID header
4. Service calls set_tenant_context(tenant_id) on DB connection
5. All queries automatically filtered by RLS policies
6. Response returned with tenant data only
```

**Security Rules:**
- NEVER trust client-provided tenant IDs
- Always derive tenant from authenticated JWT
- Validate tenant context at every boundary (API, DB, cache, jobs)

---

## 3. API Gateway Configuration (Kong)

### 3.1 Gateway Architecture

```yaml
# Kong Configuration Overview
services:
  - name: agentese-api
    url: http://agentese-service:8000
    plugins:
      - name: jwt
        config:
          claims_to_verify: [exp, iss]
      - name: rate-limiting
        config:
          policy: redis
          fault_tolerant: true
          redis_host: redis-cluster
      - name: request-transformer
        config:
          add:
            headers:
              - "X-Tenant-ID:$(jwt.claims.tenant_id)"

  - name: kgent-api
    url: http://kgent-service:8000
    plugins:
      - name: jwt
      - name: rate-limiting
      - name: opentelemetry

routes:
  - name: agentese-route
    paths: ["/v1/agentese"]
    service: agentese-api

  - name: kgent-route
    paths: ["/v1/kgent"]
    service: kgent-api
```

### 3.2 Rate Limiting Configuration

| Tier | Requests/Minute | Requests/Hour | Burst Allowance |
|------|-----------------|---------------|-----------------|
| **Free** | 60 | 1,000 | 10 |
| **Starter** | 300 | 10,000 | 50 |
| **Pro** | 1,000 | 50,000 | 200 |
| **Enterprise** | Custom | Custom | Custom |

**Algorithm:** Token Bucket (allows controlled bursts)

```yaml
# Per-tenant rate limiting
plugins:
  - name: rate-limiting
    config:
      minute: 300
      hour: 10000
      policy: redis
      fault_tolerant: true
      hide_client_headers: false
      redis_host: redis-cluster
      identifier: consumer  # Uses JWT consumer ID
```

### 3.3 Metering Integration

```yaml
# Usage metering plugin (custom)
plugins:
  - name: kgents-metering
    config:
      openmeter_endpoint: http://openmeter:8080
      event_type: api_request
      dimensions:
        - tenant_id
        - endpoint
        - method
        - response_status
```

---

## 4. Kubernetes Deployment Topology

### 4.1 Cluster Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES CLUSTER (EKS/GKE)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────┐  ┌─────────────────────────────┐  │
│  │        SYSTEM NAMESPACE              │  │     OBSERVABILITY NS        │  │
│  │  ┌─────────┐  ┌─────────┐           │  │  ┌─────────┐  ┌─────────┐  │  │
│  │  │  Kong   │  │ Cert-   │           │  │  │Prometheus│ │ Grafana │  │  │
│  │  │ Ingress │  │ Manager │           │  │  └─────────┘  └─────────┘  │  │
│  │  └─────────┘  └─────────┘           │  │  ┌─────────┐  ┌─────────┐  │  │
│  │  ┌─────────┐  ┌─────────┐           │  │  │  Tempo  │  │  Loki   │  │  │
│  │  │ External│  │  Keda   │           │  │  └─────────┘  └─────────┘  │  │
│  │  │ Secrets │  │         │           │  └─────────────────────────────┘  │
│  │  └─────────┘  └─────────┘           │                                    │
│  └─────────────────────────────────────┘                                    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    KGENTS NAMESPACE (per-environment)                │   │
│  │                                                                       │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │   │
│  │  │ Control Plane   │  │ AGENTESE Plane  │  │  K-Gent Plane   │      │   │
│  │  │    Services     │  │    Services     │  │    Services     │      │   │
│  │  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │      │   │
│  │  │  │ auth-svc  │  │  │  │ agentese  │  │  │  │ kgent-svc │  │      │   │
│  │  │  │ (3 pods)  │  │  │  │ (5 pods)  │  │  │  │ (3 pods)  │  │      │   │
│  │  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │      │   │
│  │  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │      │   │
│  │  │  │billing-svc│  │  │  │ logos-svc │  │  │  │memory-svc │  │      │   │
│  │  │  │ (2 pods)  │  │  │  │ (3 pods)  │  │  │  │ (2 pods)  │  │      │   │
│  │  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │      │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │   │
│  │                                                                       │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │                     GPU NODE POOL (AI Workloads)               │  │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │  │   │
│  │  │  │ LLM Worker  │  │ LLM Worker  │  │ LLM Worker  │            │  │   │
│  │  │  │ (T4/A10G)   │  │ (T4/A10G)   │  │ (T4/A10G)   │            │  │   │
│  │  │  │ Time-sliced │  │ Time-sliced │  │ Time-sliced │            │  │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘            │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Node Pool Configuration

| Node Pool | Instance Type | Purpose | Autoscaling |
|-----------|---------------|---------|-------------|
| **system** | m6i.large | Kong, cert-manager, KEDA | 2-4 nodes |
| **control** | m6i.xlarge | Auth, billing, admin | 2-6 nodes |
| **agentese** | c6i.2xlarge | AGENTESE runtime, logos | 3-20 nodes |
| **gpu** | g5.xlarge (T4) | LLM inference | 0-10 nodes (scale-to-zero) |
| **gpu-training** | p4d.24xlarge (A100) | Fine-tuning (spot) | 0-4 nodes |

### 4.3 GPU Scheduling with Kueue

```yaml
# Kueue ClusterQueue for GPU workloads
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: gpu-queue
spec:
  namespaceSelector: {}
  resourceGroups:
    - coveredResources: ["cpu", "memory", "nvidia.com/gpu"]
      flavors:
        - name: t4-flavor
          resources:
            - name: "nvidia.com/gpu"
              nominalQuota: 8
            - name: "cpu"
              nominalQuota: 32
            - name: "memory"
              nominalQuota: 128Gi
  queueingStrategy: StrictFIFO
---
# LocalQueue for tenant workloads
apiVersion: kueue.x-k8s.io/v1beta1
kind: LocalQueue
metadata:
  name: tenant-gpu-queue
  namespace: kgents
spec:
  clusterQueue: gpu-queue
```

### 4.4 Autoscaling Configuration

```yaml
# KEDA ScaledObject for AGENTESE service
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: agentese-scaler
  namespace: kgents
spec:
  scaleTargetRef:
    name: agentese-deployment
  minReplicaCount: 3
  maxReplicaCount: 20
  triggers:
    - type: prometheus
      metadata:
        serverAddress: http://prometheus:9090
        metricName: agentese_requests_in_flight
        threshold: "100"
        query: |
          sum(agentese_requests_in_flight{namespace="kgents"})
---
# HPA for GPU workers
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-worker-hpa
  namespace: kgents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-worker
  minReplicas: 0
  maxReplicas: 10
  metrics:
    - type: External
      external:
        metric:
          name: inference_queue_depth
        target:
          type: AverageValue
          averageValue: "5"
```

---

## 5. Service Architecture

### 5.1 Control Plane Services

| Service | Responsibility | Scaling | Dependencies |
|---------|---------------|---------|--------------|
| **auth-service** | JWT validation, tenant auth, SSO | 3-6 pods | PostgreSQL, Redis |
| **billing-service** | Subscription management, invoices | 2-4 pods | PostgreSQL, Stripe, Lago |
| **tenant-service** | Tenant CRUD, provisioning | 2-4 pods | PostgreSQL |
| **admin-service** | Admin dashboard API | 2 pods | All services |
| **metering-service** | Usage aggregation, quotas | 3-6 pods | OpenMeter, Redis |

### 5.2 AGENTESE Plane Services

| Service | Responsibility | Scaling | Dependencies |
|---------|---------------|---------|--------------|
| **agentese-api** | API gateway for AGENTESE | 5-20 pods | logos-service |
| **logos-service** | AGENTESE path invocation | 3-10 pods | Context handlers |
| **world-handler** | world.* context | 3-6 pods | External tools |
| **self-handler** | self.* context | 2-4 pods | PostgreSQL, Redis |
| **void-handler** | void.* entropy/gratitude | 2-4 pods | None |
| **time-handler** | time.* temporal | 2-4 pods | PostgreSQL |
| **concept-handler** | concept.* abstractions | 2-4 pods | Vector DB |

### 5.3 K-Gent Plane Services

| Service | Responsibility | Scaling | Dependencies |
|---------|---------------|---------|--------------|
| **kgent-api** | K-gent session API | 3-6 pods | kgent-session |
| **kgent-session** | Persona state, dialogue | 3-10 pods | memory-service |
| **memory-service** | D-gent memory persistence | 2-6 pods | PostgreSQL, Redis |
| **witness-service** | N-gent trace/narrative | 2-4 pods | ClickHouse |

---

## 6. Security Architecture

### 6.1 Authentication & Authorization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AUTHENTICATION FLOW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   User ──▶ Auth0/Clerk ──▶ JWT (tenant_id, roles) ──▶ API Gateway           │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    JWT CLAIMS STRUCTURE                              │   │
│   │  {                                                                   │   │
│   │    "sub": "user_123",                                                │   │
│   │    "tenant_id": "tenant_abc",                                        │   │
│   │    "org_id": "org_xyz",                                              │   │
│   │    "roles": ["admin", "developer"],                                  │   │
│   │    "permissions": ["agentese:invoke", "kgent:create"],               │   │
│   │    "tier": "pro",                                                    │   │
│   │    "exp": 1702598400,                                                │   │
│   │    "iss": "https://auth.kgents.io"                                   │   │
│   │  }                                                                   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 RBAC Model

| Role | Permissions | Scope |
|------|-------------|-------|
| **viewer** | Read agents, sessions | Tenant |
| **developer** | CRUD agents, invoke AGENTESE | Tenant |
| **admin** | Manage users, billing, settings | Tenant |
| **super_admin** | All operations | Platform |

### 6.3 Network Security

```yaml
# Network Policy: AGENTESE service isolation
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: agentese-isolation
  namespace: kgents
spec:
  podSelector:
    matchLabels:
      app: agentese
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: kong
      ports:
        - port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: logos
        - podSelector:
            matchLabels:
              app: postgresql
```

### 6.4 Data Security

| Layer | Protection | Implementation |
|-------|------------|----------------|
| **At Rest** | AES-256 encryption | PostgreSQL TDE, S3 SSE-KMS |
| **In Transit** | TLS 1.3 | Cert-manager, Istio mTLS |
| **Application** | Row-Level Security | PostgreSQL RLS policies |
| **Secrets** | External Secrets Operator | AWS Secrets Manager |
| **Enterprise** | Tenant-specific keys | KMS per-tenant keys |

---

## 7. Observability Stack

### 7.1 Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OBSERVABILITY ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Prometheus  │  │   Grafana   │  │   Tempo     │  │    Loki     │        │
│  │  (Metrics)  │  │   (Viz)     │  │  (Traces)   │  │   (Logs)    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│        │                │                │                │                 │
│        └────────────────┴────────────────┴────────────────┘                 │
│                                   │                                          │
│                    ┌──────────────┴──────────────┐                          │
│                    │      OpenTelemetry          │                          │
│                    │        Collector            │                          │
│                    └──────────────┬──────────────┘                          │
│                                   │                                          │
│        ┌──────────────────────────┼──────────────────────────┐              │
│        │                          │                          │              │
│        ▼                          ▼                          ▼              │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐       │
│  │  AGENTESE   │           │   K-Gent    │           │   Control   │       │
│  │  Services   │           │  Services   │           │   Plane     │       │
│  └─────────────┘           └─────────────┘           └─────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Key Metrics

| Category | Metrics | Alert Threshold |
|----------|---------|-----------------|
| **API** | request_latency_p99, error_rate | p99 > 500ms, error > 1% |
| **AGENTESE** | invoke_duration, path_errors | duration > 2s, errors > 0.5% |
| **K-Gent** | session_duration, memory_size | session > 30min |
| **GPU** | gpu_utilization, inference_queue | util < 20%, queue > 100 |
| **Billing** | metering_lag, usage_discrepancy | lag > 5min |

### 7.3 AI-Specific Observability

```yaml
# Grafana AI Observability Dashboard Config
dashboards:
  - name: AGENTESE Performance
    panels:
      - title: Token Consumption by Tenant
        query: sum(agentese_tokens_total) by (tenant_id)
      - title: LLM Latency Distribution
        query: histogram_quantile(0.95, llm_request_duration_seconds_bucket)
      - title: Cost per Tenant (USD)
        query: sum(agentese_cost_usd) by (tenant_id)
      - title: Witness/Manifest Operations
        query: rate(agentese_operations_total{aspect=~"witness|manifest"}[5m])
```

---

## 8. Deployment Environments

### 8.1 Environment Matrix

| Environment | Purpose | Cluster | Database | LLM Backend |
|-------------|---------|---------|----------|-------------|
| **dev** | Development | Local (kind) | PostgreSQL (Docker) | Ollama |
| **staging** | Pre-production | EKS (1 node pool) | RDS (shared) | OpenRouter |
| **production** | Live | EKS (multi-AZ) | RDS (per-tier) | Multi-provider |
| **enterprise** | Dedicated | Customer VPC | Dedicated RDS | Customer choice |

### 8.2 CI/CD Pipeline

```yaml
# GitHub Actions Workflow
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build & Push Images
        run: |
          docker build -t ghcr.io/kgents/agentese:$SHA .
          docker push ghcr.io/kgents/agentese:$SHA
      - name: Deploy to Staging
        run: |
          kubectl apply -k k8s/overlays/staging
          kubectl rollout status deployment/agentese -n kgents-staging

  deploy-production:
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Canary Deployment
        run: |
          kubectl apply -k k8s/overlays/production
          # 10% traffic to new version
          kubectl patch virtualservice agentese --type=merge \
            -p '{"spec":{"http":[{"route":[{"destination":{"subset":"canary"},"weight":10}]}]}}'
```

---

## 9. Implementation Phases

### Phase 1: Foundation (Weeks 1-4)
- [ ] Kubernetes cluster setup (EKS)
- [ ] Kong API Gateway deployment
- [ ] PostgreSQL with RLS
- [ ] Auth0 integration
- [ ] Basic observability (Prometheus/Grafana)

### Phase 2: Core Services (Weeks 5-8)
- [ ] AGENTESE runtime deployment
- [ ] Logos service implementation
- [ ] K-gent session service
- [ ] Memory/persistence layer
- [ ] OpenMeter integration

### Phase 3: Scale & Security (Weeks 9-12)
- [ ] GPU node pool + Kueue
- [ ] KEDA autoscaling
- [ ] Network policies
- [ ] mTLS with Istio
- [ ] Enterprise tenant provisioning

### Phase 4: Production Hardening (Weeks 13-16)
- [ ] Multi-AZ deployment
- [ ] Disaster recovery
- [ ] SOC 2 preparation
- [ ] Performance testing
- [ ] Security audit

---

## 10. Technology Stack Summary

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **API Gateway** | Kong | Apache 2.0, mature, per-tenant rate limiting |
| **Database** | PostgreSQL 15+ | RLS, battle-tested, great ecosystem |
| **Cache** | Redis Cluster | Rate limiting, session state |
| **Message Queue** | NATS | Low latency, lightweight |
| **Container Platform** | EKS | Managed K8s, GPU support |
| **GPU Scheduling** | Kueue + NVIDIA Operator | Gang scheduling, time-slicing |
| **Observability** | Prometheus/Grafana/Tempo/Loki | Open source, unified stack |
| **Auth** | Auth0/Clerk | Multi-tenant SSO, RBAC |
| **Secrets** | AWS Secrets Manager + ESO | External secrets, rotation |
| **CI/CD** | GitHub Actions | Native integration |

---

## References

- [research-architecture.md](./research-architecture.md) - Technical research
- [spec/protocols/agentese.md](../../spec/protocols/agentese.md) - AGENTESE specification
- [plans/skills/handler-patterns.md](../skills/handler-patterns.md) - CLI handler patterns

---

**Document Status**: Design Complete
**Next Phase**: BUILD
**Owner**: Platform Architecture Team
