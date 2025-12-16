# Gestalt Live: Real Kubernetes Integration

**Plan**: `plans/gestalt-live-infrastructure.md`
**Phase**: Production K8s Integration
**Date**: 2025-12-16
**Prerequisite**: Phase 2 Complete (75 tests, streaming + animations)

---

## Progress Tracking

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Discovery | **COMPLETE** | Kind cluster running, 50 entities discovered |
| Phase 2: Collector Config | **COMPLETE** | `config.py` with env-aware configs (22 tests) |
| Phase 2: RBAC Resources | **COMPLETE** | `deploy/k8s/gestalt-rbac.yaml` deployed |
| Phase 2: API Endpoint | **COMPLETE** | Updated `infrastructure.py` |
| Phase 3: Local Dev Setup | **COMPLETE** | `scripts/test_k8s_connection.py` |
| Phase 4: Incremental Rollout | **IN PROGRESS** | API tested with real data |
| Phase 5: Production Deploy | **COMPLETE** | Manifests created |

### Live Test Results (2025-12-16)

**Cluster**: `kind-kgents-triad`

**Topology Collected**:
- **50 entities** (22 pods, 21 services, 7 deployments)
- **40 connections** (service→pod, deployment→pod relationships)
- **98.3% overall health** (A+ grade)

**Namespaces Monitored**:
- `kgents-triad` (21 entities) — Main services: kgent-api, postgres, qdrant, redis
- `kgents-observability` (16 entities) — Grafana, Loki, Prometheus, Tempo, OTEL
- `kgents-agents` (7 entities) — NATS cluster
- `kgents-gateway` (5 entities) — Kong gateway
- `default` (1 entity) — kubernetes service

**RBAC Verification**:
- ✅ Can list pods, services, deployments
- ✅ Can get pod metrics
- ❌ Cannot list secrets (correct - security)
- ❌ Cannot delete pods (correct - read-only)

**Files Created**:
- `impl/claude/agents/infra/collectors/config.py` — Environment-aware config classes
- `impl/claude/agents/infra/collectors/_tests/test_config.py` — 22 tests for config
- `deploy/k8s/namespace.yaml` — kgents namespace with pod security standards
- `deploy/k8s/gestalt-rbac.yaml` — ServiceAccount, ClusterRole, ClusterRoleBinding
- `deploy/k8s/gestalt-live.yaml` — Deployment, Service, PDB, HPA
- `scripts/test_k8s_connection.py` — Connection test script

**Files Modified**:
- `impl/claude/protocols/api/infrastructure.py` — Uses env-aware config
- `impl/claude/agents/infra/collectors/__init__.py` — Exports config module
- `impl/claude/agents/infra/collectors/kubernetes.py` — Fixed health_check and owner_refs

**Tests**: 114 passed (infra suite)

### Semantic Layout Implementation (2025-12-16)

**Problem**: Original layout was random with force-directed refinement—not informative.

**Solution**: Principled semantic layout following the Projection Protocol:

| Axis | Semantic Meaning | Implementation |
|------|------------------|----------------|
| **Y** | Abstraction layer | Services (top) → Deployments (mid) → Pods (bottom) |
| **X** | Namespace clustering | Entities grouped by namespace, spread horizontally |
| **Z** | Health/Attention | Unhealthy entities come forward (depth = information) |

**Live Test Results**:
```
Y-AXIS HIERARCHY:
  service         avg_y =  4.39 (21 entities)
  deployment      avg_y =  0.00 (7 entities)
  pod             avg_y = -4.39 (22 entities)

X-AXIS CLUSTERING:
  default                   avg_x = -25.00
  kgents-agents             avg_x = -16.23
  kgents-gateway            avg_x =  -7.45
  kgents-observability      avg_x =   1.32
  kgents-triad              avg_x =  10.09
```

**Files Added**:
- `impl/claude/agents/infra/layout.py` — Semantic layout algorithm
- `impl/claude/agents/infra/_tests/test_layout.py` — 17 tests for layout

**Key Principles Applied**:
- "Depth is not decoration—it is information" (spec/protocols/projection.md)
- Layout projection is structural isomorphism
- Semantic hierarchy is visually encoded

---

## Mission

Transition Gestalt Live from mock data to real Kubernetes cluster monitoring. This enables:
1. **Live infrastructure visibility** — See actual pods, services, deployments
2. **Real-time health monitoring** — Detect issues as they happen
3. **Production migration validation** — Verify deployments during rollout
4. **Incident response** — Visual debugging during outages

---

## Phase 1: Discovery & Architecture Analysis

### 1.1 Understand Current K8s Architecture

**Tasks:**
```bash
# What namespaces exist?
kubectl get namespaces

# What's running in each namespace?
kubectl get all -A | head -100

# What services are exposed?
kubectl get svc -A

# What deployments exist?
kubectl get deployments -A

# Check if metrics-server is installed (needed for CPU/memory)
kubectl top pods -A 2>&1 | head -5

# What RBAC exists for service accounts?
kubectl get clusterroles | grep -i view
```

**Document:**
- [ ] List of namespaces and their purposes
- [ ] Key services and their dependencies
- [ ] Current monitoring setup (Prometheus? Grafana? Datadog?)
- [ ] RBAC model and service account structure

### 1.2 Define Scope

**Questions to answer:**
1. Which namespaces should Gestalt Live monitor?
   - `kgents` namespace only?
   - All application namespaces?
   - Exclude system namespaces (`kube-system`, `kube-public`)?

2. What resources matter most?
   - Pods (health, restarts, resource usage)
   - Services (endpoint availability)
   - Deployments (replica status)
   - ConfigMaps/Secrets (optional, security-sensitive)

3. Who should have access?
   - Dev team only?
   - All engineers?
   - Read-only or interactive?

---

## Phase 2: Collector Configuration

### 2.1 Create Production Config

```python
# impl/claude/agents/infra/collectors/config.py

from dataclasses import dataclass, field
from .kubernetes import KubernetesConfig

@dataclass
class ProductionK8sConfig(KubernetesConfig):
    """Production Kubernetes configuration for kgents cluster."""

    # Connection - use in-cluster config when deployed, kubeconfig locally
    kubeconfig: str | None = None  # Set via env var for local dev
    context: str | None = None     # Set via env var for multi-cluster

    # Namespaces to monitor (empty = all, but we want explicit)
    namespaces: list[str] = field(default_factory=lambda: [
        "kgents",           # Main application namespace
        "default",          # Default namespace
        # Add more as needed:
        # "staging",
        # "production",
    ])

    # Resource collection flags
    collect_pods: bool = True
    collect_services: bool = True
    collect_deployments: bool = True
    collect_configmaps: bool = False  # Usually too noisy
    collect_secrets: bool = False      # Security risk

    # Metrics (requires metrics-server)
    collect_metrics: bool = True

    # Polling
    poll_interval: float = 5.0  # 5 seconds for real-time feel

    # Layout
    calculate_positions: bool = True
    layout_iterations: int = 50


def get_collector_config() -> KubernetesConfig:
    """Get collector config based on environment."""
    import os

    env = os.getenv("KGENTS_ENV", "development")

    if env == "production":
        # In-cluster config
        return ProductionK8sConfig()
    else:
        # Local development with kubeconfig
        return ProductionK8sConfig(
            kubeconfig=os.getenv("KUBECONFIG", "~/.kube/config"),
            context=os.getenv("KUBE_CONTEXT"),
        )
```

### 2.2 Create RBAC Resources

```yaml
# deploy/k8s/gestalt-rbac.yaml
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: gestalt-live
  namespace: kgents
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: gestalt-live-reader
rules:
  # Core resources
  - apiGroups: [""]
    resources: ["pods", "services", "endpoints", "events", "namespaces"]
    verbs: ["get", "list", "watch"]
  # Apps resources
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets", "statefulsets", "daemonsets"]
    verbs: ["get", "list", "watch"]
  # Metrics (if metrics-server is available)
  - apiGroups: ["metrics.k8s.io"]
    resources: ["pods", "nodes"]
    verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: gestalt-live-reader-binding
subjects:
  - kind: ServiceAccount
    name: gestalt-live
    namespace: kgents
roleRef:
  kind: ClusterRole
  name: gestalt-live-reader
  apiGroup: rbac.authorization.k8s.io
```

### 2.3 Update API Infrastructure Endpoint

```python
# impl/claude/protocols/api/infrastructure.py

# Modify get_collector() to use real config
async def get_collector() -> BaseCollector:
    """Get the infrastructure collector."""
    global _collector

    if _collector is None:
        env = os.getenv("KGENTS_ENV", "development")
        use_mock = os.getenv("GESTALT_USE_MOCK", "false").lower() == "true"

        if use_mock or env == "test":
            from agents.infra.collectors.kubernetes import MockKubernetesCollector
            _collector = MockKubernetesCollector()
        else:
            from agents.infra.collectors.kubernetes import KubernetesCollector
            from agents.infra.collectors.config import get_collector_config
            _collector = KubernetesCollector(get_collector_config())

        await _collector.connect()

    return _collector
```

---

## Phase 3: Local Development Setup

### 3.1 Port-Forward for Local Testing

```bash
# Option A: Run API locally, connect to remote cluster
export KUBECONFIG=~/.kube/config
export KUBE_CONTEXT=your-cluster-context
export GESTALT_USE_MOCK=false

cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Option B: Port-forward to in-cluster API
kubectl port-forward -n kgents svc/kgents-api 8000:8000
```

### 3.2 Test Connection

```python
# Quick test script
import asyncio
from agents.infra.collectors.kubernetes import KubernetesCollector
from agents.infra.collectors.config import get_collector_config

async def test_connection():
    config = get_collector_config()
    print(f"Connecting with namespaces: {config.namespaces}")

    collector = KubernetesCollector(config)
    await collector.connect()

    if await collector.health_check():
        print("✅ Connected to Kubernetes!")

        topology = await collector.collect_topology()
        print(f"Found {len(topology.entities)} entities:")
        for kind in set(e.kind.value for e in topology.entities):
            count = sum(1 for e in topology.entities if e.kind.value == kind)
            print(f"  - {kind}: {count}")
    else:
        print("❌ Connection failed")

    await collector.disconnect()

asyncio.run(test_connection())
```

---

## Phase 4: Incremental Rollout

### 4.1 Stage 1: Read-Only Monitoring (Week 1)

**Scope:**
- Single namespace (`kgents`)
- Pods, services, deployments only
- No metrics collection initially

**Validation:**
- [ ] Entities appear in Gestalt Live UI
- [ ] Health grades match `kubectl get pods` status
- [ ] Events stream correctly
- [ ] No errors in API logs

### 4.2 Stage 2: Metrics Integration (Week 2)

**Prerequisites:**
- metrics-server installed (`kubectl top pods` works)

**Scope:**
- Enable `collect_metrics: true`
- CPU and memory percentages populate

**Validation:**
- [ ] CPU/memory bars show real values
- [ ] High-resource pods pulse appropriately
- [ ] Memory limits respected in health calculation

### 4.3 Stage 3: Multi-Namespace (Week 3)

**Scope:**
- Add additional namespaces (`staging`, `production`, etc.)
- Cross-namespace connections visible

**Validation:**
- [ ] Namespaces visually grouped
- [ ] Service-to-pod connections span namespaces correctly
- [ ] Performance acceptable with more entities

### 4.4 Stage 4: Event-Driven Updates (Week 4)

**Scope:**
- Switch from polling to Kubernetes watch API
- Instant updates on pod state changes

**Validation:**
- [ ] Pod creation appears immediately
- [ ] Pod termination fades out in real-time
- [ ] Deployment scaling visible live

---

## Phase 5: Production Deployment

### 5.1 Deployment Manifest

```yaml
# deploy/k8s/gestalt-live.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kgents-api
  namespace: kgents
spec:
  replicas: 2
  selector:
    matchLabels:
      app: kgents-api
  template:
    metadata:
      labels:
        app: kgents-api
    spec:
      serviceAccountName: gestalt-live
      containers:
        - name: api
          image: kgents/api:latest
          ports:
            - containerPort: 8000
          env:
            - name: KGENTS_ENV
              value: "production"
            - name: GESTALT_USE_MOCK
              value: "false"
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
```

### 5.2 Ingress/Service

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: kgents-api
  namespace: kgents
spec:
  selector:
    app: kgents-api
  ports:
    - port: 8000
      targetPort: 8000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kgents-api
  namespace: kgents
  annotations:
    # Add your ingress annotations (cert-manager, etc.)
spec:
  rules:
    - host: api.kgents.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: kgents-api
                port:
                  number: 8000
```

---

## Security Considerations

### Access Control
- [ ] RBAC uses least-privilege (read-only)
- [ ] No secret access by default
- [ ] Service account scoped to specific namespaces if possible

### Data Sensitivity
- [ ] Pod names may reveal business logic — consider access controls
- [ ] Environment variables NOT exposed (source_data filtering)
- [ ] Events may contain sensitive info — audit what's shown

### Network Security
- [ ] API behind authentication (existing auth middleware)
- [ ] SSE streams require valid session
- [ ] No direct kubectl proxy exposure

---

## Success Criteria

### Functional
- [ ] Real pods/services/deployments visible in 3D scene
- [ ] Health grades match actual pod status
- [ ] Events stream from real cluster
- [ ] Positions stable (no jumping on updates)

### Performance
- [ ] < 2s initial topology load
- [ ] < 500ms incremental update latency
- [ ] < 100MB memory usage for collector

### Reliability
- [ ] Auto-reconnect on cluster disconnect
- [ ] Graceful degradation if metrics-server unavailable
- [ ] No crash on transient API errors

---

## Testing Commands

```bash
# Verify RBAC
kubectl auth can-i list pods --as=system:serviceaccount:kgents:gestalt-live -A

# Test collector locally
cd impl/claude
uv run python -c "
import asyncio
from agents.infra.collectors.kubernetes import KubernetesCollector
from agents.infra.collectors.config import get_collector_config

async def test():
    c = KubernetesCollector(get_collector_config())
    await c.connect()
    t = await c.collect_topology()
    print(f'{len(t.entities)} entities found')
    await c.disconnect()

asyncio.run(test())
"

# Run API with real collector
GESTALT_USE_MOCK=false uv run uvicorn protocols.api.app:create_app --factory --port 8000

# Run frontend
cd impl/claude/web && npm run dev
# Visit http://localhost:3000/gestalt/live
```

---

## Questions to Resolve

1. **Cluster Access**: How do we authenticate locally? kubeconfig? OIDC? Service account token?

2. **Namespaces**: Which namespaces should be monitored initially?

3. **Metrics**: Is metrics-server installed? If not, should we install it?

4. **Existing Monitoring**: Is there Prometheus/Grafana? Should Gestalt complement or replace?

5. **Multi-Cluster**: Do we need to support multiple clusters eventually?

6. **Alerting**: Should Gestalt Live trigger alerts, or just visualize?

---

*"The map becomes the territory. Let's make it real."*

---

## Audit Synthesis (Principles-Aligned)

- **Namespace + identity drift**: Manifests mix `kgents`, `kgents-triad`, `kgents-agents`; API uses `default` SA. Align to a triad (`kgents-system` for operators, `kgents-app` for services, `kgents-obs` for telemetry) with namespace-scoped Roles/RoleBindings; prohibit `default` SA via policy.
- **RBAC tightening**: Use aggregated `ClusterRole` for read-only Gestalt Live, namespace-scoped by default; operators get precise CRD verbs; enforce via Kyverno/OPA (deny `:latest`, require probes/resources, require non-default SA).
- **Supply-chain hygiene**: Pin digests, sign with Cosign/SLSA provenance; admission rejects unsigned/`:latest`; tag immutability in registry. Add kustomize overlays per env with Argo/Flux GitOps and Argo Rollouts for canary/blue-green.
- **Network + MTLS**: Default deny ingress + egress per namespace; Service mesh (Linkerd/Cilium Hubble + SPIFFE) for identity and MTLS between services/collector/API.
- **Secrets**: External Secrets/Sealed Secrets with KMS; rotate tokens; redact envs in logs; disable kubectl in pods except dedicated infra collector SA with tight verbs.
- **Observability/SLOs**: Explicit kube-state-metrics + metrics-server; OTel spans/metrics for collector ingest lag; SLOs for latency/error budget; alerts via Prometheus/Alertmanager; richer readiness (/health/saas); dashboards for topology size/lag.
- **Resilience**: HPAs + PDBs for all stateless services; topology spread constraints; Velero backups for stateful bits (D-gent, ghost, L-gent DB) with tested restores; graceful shutdown hooks and retry budgets.
- **Deployment workflow**: SaaS checklist gates in CI (auth-can-i, Trivy, policy conformance); staged rollouts with automatic rollback on probe/metric regression; runbooks for SLO breaches.

## Gestalt Live Collector Upgrades

- **Watch-first architecture**: Use Kubernetes watch/informers with cached listers; fallback polling with exponential backoff/jitter. Dedup + backpressure for SSE/WS streams.
- **Scoping**: Namespace allowlist default; cluster-wide only when explicit. Resource toggles (pods/services/deployments) per env config.
- **Metrics path**: Prefer kube-state-metrics for usage; metrics-server required. Future: PromQL bridge for richer signals.
- **Layout stability**: Cache positions server-side keyed by UID+generation; recompute on diff; avoid jitter.
- **Multi-cluster**: Configurable contexts/kubeconfigs; shard collectors per context; future Envoy/gRPC xDS for federation.
- **AGENTESE surface**: Expose `world.k8s.*` paths to keep composability with other agents (e.g., governance, memory).

## Concrete Next Steps

1) Author kustomize overlays (dev/stage/prod) with unified namespaces and service accounts; swap deployments to digests.
2) Add Kyverno/OPA policies: no `:latest`, require non-default SA, require liveness/readiness + resource requests.
3) Implement watch-based Kubernetes collector with kube-state-metrics integration and cached layouts; env-driven namespace/resource filters.
4) Add HPAs/PDBs for Town, Morpheus, U-gent, Gestalt Live API; add topology spread constraints.
5) Wire External Secrets/Sealed Secrets for API keys; document rotation; add log redaction hooks.
6) Integrate SLOs/alerts/dashboards for collector ingest lag, topology size, and API latency; gate deployments with SaaS checklist in CI.
