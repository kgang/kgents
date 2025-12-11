# L-Gent UX Implementation Plan (Cliff Dive Edition)

**Goal**: L-Gent as a distributed system from Day 1. No local fallbacks. No gentle ramps. The infrastructure *is* the application.

**Kent's Focus**: K8s/Helm as the *medium*, not the destination
**Approach**: Deep end first—stateful, distributed, observable from the start

---

## Implementation Status

| Phase | Component | Status | Files |
|-------|-----------|--------|-------|
| 1.1 | PostgreSQL + pgvector manifest | **Done** | `infra/k8s/manifests/l-gent-postgres.yaml` |
| 1.2 | L-Gent Deployment manifest | **Done** | `infra/k8s/manifests/l-gent-deployment.yaml` |
| 1.3 | PostgreSQL backend (Python) | Pending | `agents/l/postgres_backend.py` |
| 1.4 | CLI thin client | Pending | `agents/l/cli.py` modifications |
| 2.x | Helm chart | Pending | `charts/l-gent/` |
| 3.x | Prometheus metrics | Pending | `agents/l/metrics.py` |
| 4.x | Rich CLI rendering | Pending | `agents/l/cli_renderers.py` |

**Current**: Phase 1 manifests deployed as placeholders. Ready for Python backend implementation.

---

## The Inversion

> *"The tightest loop is when the infrastructure is the application."*

The original plan treated K8s as Level 5 of a video game. You grind through CLI polish (Level 1), TUI (Level 2), gRPC (Level 3) to *earn* the right to touch Kubernetes.

**That's backward.**

If your goal is K8s mastery, writing Rich CLI tables in Python is procrastination—"polishing the doorknob before opening the door."

### The Waterfall Fallacy (What We're Avoiding)

```
❌ OLD: Build Up to K8s
   CLI Polish → TUI → gRPC → Deploy → Helm → "Now I know K8s"

   Problem: 4 phases of procrastination before touching the real thing
```

### The Cliff Dive (What We're Doing)

```
✓ NEW: Descend Into K8s
   Day 1: Postgres + L-gent in Kind (no local mode)
   Day 2: Helm chart (automate the pain)
   Day 3: Observability (Prometheus + Grafana)
   Day 4+: UI is a thin client to the cluster

   Lesson: You can't run kgents without a cluster. Fix the infra, not the code.
```

---

## Philosophy: Summon the Demons

### Why Stateful First?

Stateless apps on K8s are easy. Stateful apps are where the demons live:
- PersistentVolumeClaims that won't bind
- Database initialization race conditions
- Connection pooling exhaustion
- Backup/restore nightmares

**The plan starts with PostgreSQL because it's hard.** Do the hard part first.

### Why No Local Fallback?

The current L-Gent has graceful degradation:
```python
# Current: Falls back to in-memory if no DB
if db_available:
    return PostgresRegistry()
else:
    return InMemoryRegistry()  # ← This is a lie
```

**We're removing the lie.** If the cluster is down, the CLI screams. You fix the infrastructure, not the code.

### Why Distributed from Day 1?

A single `LibraryService` pod is just a monolith in a container. It teaches deployment, but not *orchestration*.

We'll deploy L-Gent as interconnected microservices:
- **L-gent (Index)**: Catalog queries, semantic search
- **L-gent-db (PostgreSQL)**: Persistent storage with pgvector
- **L-gent-embedder (optional)**: Embedding computation sidecar

This forces you to learn:
- Service Discovery (CoreDNS)
- Traffic Management (ClusterIP vs Headless Services)
- Failure Domains (what happens when embedder is down?)

---

## Phase 1: Cluster in a Bottle (Day 1)

**Goal**: You cannot run `kgents library` without a cluster.

### 1.1 PostgreSQL + pgvector in Kind

```yaml
# infra/k8s/manifests/l-gent-postgres.yaml

apiVersion: v1
kind: Secret
metadata:
  name: l-gent-postgres
  namespace: kgents-system
type: Opaque
stringData:
  POSTGRES_USER: lgent
  POSTGRES_PASSWORD: lgent-dev-password  # rotated in prod
  POSTGRES_DB: lgent

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: l-gent-postgres
  namespace: kgents-system
spec:
  serviceName: l-gent-postgres
  replicas: 1
  selector:
    matchLabels:
      app: l-gent-postgres
  template:
    metadata:
      labels:
        app: l-gent-postgres
    spec:
      containers:
      - name: postgres
        image: pgvector/pgvector:pg16
        ports:
        - containerPort: 5432
          name: postgres
        envFrom:
        - secretRef:
            name: l-gent-postgres
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          exec:
            command: ["pg_isready", "-U", "lgent"]
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi

---
apiVersion: v1
kind: Service
metadata:
  name: l-gent-postgres
  namespace: kgents-system
spec:
  type: ClusterIP
  ports:
  - port: 5432
    targetPort: 5432
  selector:
    app: l-gent-postgres
```

**What you'll hit immediately:**
- PVC won't bind (storage class missing in Kind)
- Pod stuck in Pending (resource limits)
- Connection refused (service not ready)

**These are the lessons.** Not the errors.

### 1.2 L-Gent Deployment (No Local Mode)

```yaml
# infra/k8s/manifests/l-gent-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: l-gent
  namespace: kgents-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: l-gent
  template:
    metadata:
      labels:
        app: l-gent
    spec:
      initContainers:
      - name: wait-for-db
        image: busybox
        command: ['sh', '-c', 'until nc -z l-gent-postgres 5432; do sleep 1; done']
      - name: migrate
        image: kgents/l-gent:latest
        command: ['python', '-m', 'alembic', 'upgrade', 'head']
        envFrom:
        - secretRef:
            name: l-gent-postgres
        env:
        - name: DATABASE_URL
          value: "postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@l-gent-postgres:5432/$(POSTGRES_DB)"
      containers:
      - name: l-gent
        image: kgents/l-gent:latest
        ports:
        - containerPort: 50051
          name: grpc
        - containerPort: 8080
          name: http
        envFrom:
        - secretRef:
            name: l-gent-postgres
        env:
        - name: DATABASE_URL
          value: "postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@l-gent-postgres:5432/$(POSTGRES_DB)"
        - name: LGENT_MODE
          value: "cluster"  # No fallback to local
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

### 1.3 The PostgreSQL Backend (Python)

```python
# impl/claude/agents/l/postgres_backend.py

"""
PostgreSQL backend for L-Gent. No fallbacks.

If DATABASE_URL is not set or connection fails, we crash.
Fix the infrastructure, not the code.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

import asyncpg
from pgvector.asyncpg import register_vector

from .types import CatalogEntry, EntityType, Status


class PostgresRegistry:
    """
    L-Gent registry backed by PostgreSQL + pgvector.

    Crash-only design: no graceful degradation to in-memory.
    """

    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    @classmethod
    async def connect(cls) -> "PostgresRegistry":
        """Connect to PostgreSQL or die trying."""
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise RuntimeError(
                "DATABASE_URL not set. "
                "L-Gent requires a PostgreSQL cluster. "
                "Run: kgents infra init && kgents infra apply l-gent"
            )

        pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10,
            setup=register_vector,  # Enable pgvector
        )
        return cls(pool)

    async def close(self):
        await self._pool.close()

    async def register(self, entry: CatalogEntry) -> str:
        """Register artifact in catalog."""
        async with self._pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO catalog_entries (
                    id, name, entity_type, status, description,
                    version, input_type, output_type, embedding,
                    created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    entity_type = EXCLUDED.entity_type,
                    status = EXCLUDED.status,
                    description = EXCLUDED.description,
                    version = EXCLUDED.version,
                    input_type = EXCLUDED.input_type,
                    output_type = EXCLUDED.output_type,
                    embedding = EXCLUDED.embedding,
                    updated_at = NOW()
            """, entry.id, entry.name, entry.entity_type.value,
                entry.status.value, entry.description, entry.version,
                entry.input_type, entry.output_type, entry.embedding)
        return entry.id

    async def get(self, id: str) -> CatalogEntry | None:
        """Get artifact by ID."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM catalog_entries WHERE id = $1", id
            )
            if row:
                return self._row_to_entry(row)
            return None

    async def find_semantic(
        self,
        query_embedding: list[float],
        limit: int = 10,
        threshold: float = 0.5
    ) -> list[tuple[CatalogEntry, float]]:
        """Semantic search using pgvector cosine similarity."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT *,
                       1 - (embedding <=> $1::vector) as similarity
                FROM catalog_entries
                WHERE embedding IS NOT NULL
                  AND 1 - (embedding <=> $1::vector) > $2
                ORDER BY embedding <=> $1::vector
                LIMIT $3
            """, query_embedding, threshold, limit)

            return [
                (self._row_to_entry(row), row['similarity'])
                for row in rows
            ]

    def _row_to_entry(self, row) -> CatalogEntry:
        return CatalogEntry(
            id=row['id'],
            name=row['name'],
            entity_type=EntityType(row['entity_type']),
            status=Status(row['status']),
            description=row['description'],
            version=row['version'],
            input_type=row['input_type'],
            output_type=row['output_type'],
            embedding=list(row['embedding']) if row['embedding'] else None,
        )


# The factory function - no fallbacks
async def create_registry() -> PostgresRegistry:
    """
    Create L-Gent registry. Requires PostgreSQL.

    If you see this error, your cluster is down:
        RuntimeError: DATABASE_URL not set

    Fix it:
        kgents infra init
        kgents infra apply l-gent
    """
    return await PostgresRegistry.connect()
```

### 1.4 CLI as Thin Client

```python
# impl/claude/agents/l/cli.py (modified)

"""
L-Gent CLI - Thin client to cluster.

Every command connects to the L-Gent service in the cluster.
If the cluster is down, we fail fast with helpful diagnostics.
"""

import os
import sys

import grpc

from .grpc import library_pb2, library_pb2_grpc


def get_service_address() -> str:
    """
    Get L-Gent service address.

    Priority:
    1. LGENT_SERVICE env var (explicit override)
    2. Port-forward to cluster (kgents infra port-forward l-gent)
    3. In-cluster DNS (when running inside cluster)
    """
    if addr := os.environ.get("LGENT_SERVICE"):
        return addr

    # Default: assume port-forward is running
    return "localhost:50051"


def require_cluster():
    """
    Decorator that ensures cluster connectivity.
    Fails fast with actionable error message.
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            addr = get_service_address()
            try:
                async with grpc.aio.insecure_channel(addr) as channel:
                    stub = library_pb2_grpc.LibraryServiceStub(channel)
                    # Health check
                    await stub.Health(library_pb2.HealthRequest())
                    return await func(stub, *args, **kwargs)
            except grpc.aio.AioRpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    print(f"""
╭─ L-Gent Cluster Unavailable ──────────────────────────────╮
│                                                           │
│  Cannot connect to L-Gent service at {addr}
│                                                           │
│  Quick fixes:                                             │
│  1. Start port-forward:                                   │
│     kgents infra port-forward l-gent                      │
│                                                           │
│  2. Or check cluster status:                              │
│     kgents infra status                                   │
│                                                           │
│  3. Or deploy L-Gent:                                     │
│     kgents infra apply l-gent                             │
│                                                           │
╰───────────────────────────────────────────────────────────╯
""", file=sys.stderr)
                    sys.exit(1)
                raise
        return wrapper
    return decorator


class LibraryCLI:
    """L-Gent CLI - all commands require cluster."""

    @require_cluster()
    async def catalog(stub, type: str | None = None):
        """List catalog entries from cluster."""
        request = library_pb2.ListRequest(
            entity_type=type if type else ""
        )
        response = await stub.ListArtifacts(request)

        # Rich rendering here (Phase 4)
        for artifact in response.artifacts:
            print(f"{artifact.id}\t{artifact.name}\t{artifact.entity_type}")

    @require_cluster()
    async def discover(stub, query: str, limit: int = 10):
        """Semantic search - streams results as found."""
        request = library_pb2.DiscoverRequest(query=query, limit=limit)

        async for result in stub.Discover(request):
            print(f"{result.score:.2f}\t{result.artifact.name}")
```

### 1.5 Day 1 Checkpoint

At the end of Day 1, you should have:

```bash
# This works
kgents infra init                    # Kind cluster running
kgents infra apply l-gent            # PostgreSQL + L-Gent deployed
kgents infra port-forward l-gent     # In another terminal
kgents library catalog               # Lists artifacts from Postgres

# This fails (correctly)
kgents infra destroy
kgents library catalog               # → "Cluster Unavailable" error
```

**You cannot use L-Gent without the cluster.** That's the lesson.

---

## Phase 2: The Operator Mindset (Day 2-3)

**Goal**: Automate the pain of Phase 1.

### 2.1 Helm Chart Structure

```
charts/l-gent/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── namespace.yaml
│   ├── secrets.yaml
│   ├── postgres-statefulset.yaml
│   ├── postgres-service.yaml
│   ├── l-gent-deployment.yaml
│   ├── l-gent-service.yaml
│   ├── l-gent-configmap.yaml
│   └── NOTES.txt
└── migrations/
    ├── 001_initial.sql
    └── 002_pgvector.sql
```

### 2.2 values.yaml (Your Configuration Interface)

```yaml
# charts/l-gent/values.yaml

# Namespace
namespace: kgents-system

# L-Gent Application
lgent:
  replicaCount: 1
  image:
    repository: kgents/l-gent
    tag: latest
    pullPolicy: IfNotPresent

  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"

  # gRPC and HTTP ports
  service:
    type: ClusterIP
    grpcPort: 50051
    httpPort: 8080

# PostgreSQL
postgresql:
  enabled: true
  image: pgvector/pgvector:pg16

  auth:
    username: lgent
    password: ""  # Auto-generated if empty
    database: lgent
    existingSecret: ""  # Use existing secret

  persistence:
    enabled: true
    size: 1Gi
    storageClass: ""  # Use default

  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"

# Embedder sidecar (optional)
embedder:
  enabled: false
  type: simple  # simple | sentence-transformer | openai
  openai:
    apiKey: ""
    model: text-embedding-3-small

# Observability (Phase 3)
metrics:
  enabled: false
  serviceMonitor: false  # Requires prometheus-operator
```

### 2.3 Environment Variations

```yaml
# charts/l-gent/values-dev.yaml

lgent:
  replicaCount: 1
  image:
    pullPolicy: Always  # Always pull in dev

postgresql:
  persistence:
    size: 1Gi

metrics:
  enabled: true
```

```yaml
# charts/l-gent/values-prod.yaml

lgent:
  replicaCount: 3

  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

postgresql:
  persistence:
    size: 10Gi
    storageClass: fast-ssd

  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"

metrics:
  enabled: true
  serviceMonitor: true
```

### 2.4 Helm Commands (Your New Interface)

```bash
# Install L-Gent stack (dev mode)
helm upgrade --install l-gent ./charts/l-gent \
  -n kgents-system --create-namespace \
  -f charts/l-gent/values-dev.yaml

# Check status
helm status l-gent -n kgents-system

# Upgrade with new values
helm upgrade l-gent ./charts/l-gent \
  -n kgents-system \
  --set lgent.replicaCount=2

# Rollback if broken
helm rollback l-gent -n kgents-system

# Uninstall
helm uninstall l-gent -n kgents-system
```

### 2.5 Day 2-3 Checkpoint

```bash
# One command to rule them all
helm upgrade --install l-gent ./charts/l-gent -n kgents-system --create-namespace

# See what was created
kubectl get all -n kgents-system

# Expected output:
# NAME                         READY   STATUS    RESTARTS   AGE
# pod/l-gent-xxx               1/1     Running   0          30s
# pod/l-gent-postgres-0        1/1     Running   0          45s
#
# NAME                        TYPE        CLUSTER-IP       PORT(S)
# service/l-gent              ClusterIP   10.96.xxx.xxx    50051/TCP,8080/TCP
# service/l-gent-postgres     ClusterIP   10.96.xxx.xxx    5432/TCP
```

**The Helm chart is now your configuration interface.** Not Python files. Not environment variables scattered everywhere.

---

## Phase 3: The Broken Window (Day 4)

**Goal**: Observability is not a luxury; it is eyes.

> *"You don't use `print()`. You look at the Dashboard."*

### 3.1 Prometheus + Grafana (via Helm)

```bash
# Add prometheus-community repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack (Prometheus + Grafana + Alertmanager)
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  --set grafana.adminPassword=admin \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

### 3.2 Instrument L-Gent

```python
# impl/claude/agents/l/metrics.py

"""
L-Gent Prometheus metrics.

Expose on /metrics endpoint. Scraped by Prometheus automatically
via ServiceMonitor.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Counters (things that only go up)
CATALOG_OPERATIONS = Counter(
    'lgent_catalog_operations_total',
    'Total catalog operations',
    ['operation', 'status']  # register, get, delete × success, error
)

SEARCH_QUERIES = Counter(
    'lgent_search_queries_total',
    'Total search queries',
    ['type']  # keyword, semantic, hybrid
)

# Histograms (distributions)
SEARCH_LATENCY = Histogram(
    'lgent_search_latency_seconds',
    'Search latency in seconds',
    ['type'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

DB_QUERY_LATENCY = Histogram(
    'lgent_db_query_latency_seconds',
    'Database query latency',
    ['query_type'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
)

# Gauges (things that go up and down)
CATALOG_SIZE = Gauge(
    'lgent_catalog_entries',
    'Current number of catalog entries',
    ['entity_type']
)

DB_POOL_SIZE = Gauge(
    'lgent_db_pool_connections',
    'Database connection pool size',
    ['state']  # idle, active
)


# Usage in registry
class PostgresRegistry:
    async def register(self, entry: CatalogEntry) -> str:
        with DB_QUERY_LATENCY.labels(query_type='insert').time():
            try:
                result = await self._do_register(entry)
                CATALOG_OPERATIONS.labels(operation='register', status='success').inc()
                return result
            except Exception:
                CATALOG_OPERATIONS.labels(operation='register', status='error').inc()
                raise

    async def find_semantic(self, query_embedding, limit=10, threshold=0.5):
        SEARCH_QUERIES.labels(type='semantic').inc()
        with SEARCH_LATENCY.labels(type='semantic').time():
            return await self._do_semantic_search(query_embedding, limit, threshold)
```

### 3.3 ServiceMonitor (Auto-Discovery)

```yaml
# charts/l-gent/templates/servicemonitor.yaml

{{- if .Values.metrics.serviceMonitor }}
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ .Release.Name }}-l-gent
  namespace: {{ .Values.namespace }}
  labels:
    release: monitoring  # Match prometheus-operator selector
spec:
  selector:
    matchLabels:
      app: l-gent
  endpoints:
  - port: http
    path: /metrics
    interval: 15s
{{- end }}
```

### 3.4 Grafana Dashboard

```json
{
  "title": "L-Gent Overview",
  "panels": [
    {
      "title": "Search Latency (p99)",
      "type": "graph",
      "targets": [{
        "expr": "histogram_quantile(0.99, rate(lgent_search_latency_seconds_bucket[5m]))",
        "legendFormat": "{{type}}"
      }]
    },
    {
      "title": "Operations/sec",
      "type": "graph",
      "targets": [{
        "expr": "rate(lgent_catalog_operations_total[1m])",
        "legendFormat": "{{operation}}"
      }]
    },
    {
      "title": "Catalog Size",
      "type": "stat",
      "targets": [{
        "expr": "sum(lgent_catalog_entries)"
      }]
    },
    {
      "title": "Error Rate",
      "type": "gauge",
      "targets": [{
        "expr": "rate(lgent_catalog_operations_total{status='error'}[5m]) / rate(lgent_catalog_operations_total[5m])"
      }]
    }
  ]
}
```

### 3.5 Day 4 Checkpoint

```bash
# Access Grafana
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring

# Open http://localhost:3000 (admin/admin)
# Import L-Gent dashboard
# See metrics flowing

# Now when you run:
kgents library discover "sentiment"

# You see the latency spike in the dashboard, not in print() statements
```

**From now on, you debug by looking at Grafana, not by adding print statements.**

---

## Phase 4: The UI (Day 5+)

**Goal**: Now that the engine is humming, build the dashboard.

### 4.1 Rich CLI Rendering

Now—and only now—do we polish the CLI output:

```python
# impl/claude/agents/l/cli_renderers.py

"""
Rich rendering for L-Gent CLI.

Only called after successful cluster communication.
The cluster does the work; we just paint the results.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

TYPE_ICONS = {
    "agent": "🤖",
    "tongue": "👅",
    "hypothesis": "🔬",
    "tool": "🔧",
    "artifact": "📦",
}

STATUS_ICONS = {
    "active": "[green]✓[/green]",
    "deprecated": "[red]✗[/red]",
    "testing": "[yellow]⚠[/yellow]",
}


def render_catalog(artifacts: list, total: int):
    """Render catalog as Rich table."""

    console.print(Panel(
        f"[bold]{total}[/bold] artifacts in cluster",
        title="L-Gent Catalog",
        border_style="blue"
    ))

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Name")
    table.add_column("Description", max_width=40)

    for a in artifacts:
        icon = TYPE_ICONS.get(a.entity_type, "📄")
        status = STATUS_ICONS.get(a.status, a.status)
        table.add_row(
            a.id,
            f"{icon} {a.entity_type}",
            status,
            a.name,
            a.description[:40] + "..." if len(a.description) > 40 else a.description
        )

    console.print(table)


def render_discover_stream(query: str):
    """
    Render streaming discover results.

    Usage:
        async with render_discover_stream("sentiment") as renderer:
            async for result in stub.Discover(request):
                renderer.add(result)
    """
    # Progress spinner while searching
    # Results appear as they stream in
    # Final summary when done
    pass  # Implementation uses Rich Live display


def render_lineage_graph(root_id: str, ancestors: list, descendants: list):
    """Render lineage as ASCII tree."""
    # Tree rendering implementation
    pass
```

### 4.2 Interactive TUI (Optional Branch)

If the CLI feels limiting, now's the time for a TUI:

```python
# impl/claude/agents/l/tui/browser.py

"""
L-Gent TUI Browser using Textual.

A thin client to the cluster with keyboard navigation.
"""

from textual.app import App
from textual.widgets import DataTable, Header, Footer
from textual.containers import Horizontal, Vertical


class LGentBrowser(App):
    """Full-screen catalog browser."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("/", "search", "Search"),
        ("l", "lineage", "Lineage"),
        ("c", "compose", "Compose"),
    ]

    async def on_mount(self):
        # Connect to cluster
        self.stub = await self.connect_to_cluster()
        # Load initial catalog
        await self.refresh_catalog()

    async def refresh_catalog(self):
        """Fetch catalog from cluster and populate table."""
        response = await self.stub.ListArtifacts(ListRequest())
        # Populate DataTable widget
```

### 4.3 Day 5+ Checkpoint

```bash
# Beautiful CLI output (backed by real cluster data)
kgents library catalog

╭─ L-Gent Catalog ─────────────────────────────────────────╮
│ 47 artifacts in cluster                                  │
╰──────────────────────────────────────────────────────────╯

┏━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ ID          ┃ Type     ┃ Status    ┃ Description         ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ parser-v2   │ 🤖 agent │ ✓ active  │ JSON document parser│
│ grammar-sql │ 👅 tongue│ ✓ active  │ SQL dialect grammar │
└─────────────┴──────────┴───────────┴─────────────────────┘

# Or launch TUI
kgents library browse
```

---

## The Daily Loop

Once set up, your daily workflow becomes:

```bash
# Morning: Ensure cluster is healthy
kgents infra status

# Check last night's metrics
open http://localhost:3000  # Grafana

# Develop with live reload
kgents dev l-gent

# Test changes
kgents library catalog
kgents library discover "sentiment"

# Deploy changes
helm upgrade l-gent ./charts/l-gent -n kgents-system

# Watch rollout
kubectl rollout status deployment/l-gent -n kgents-system
```

**The infrastructure is the application.** You're not "deploying to K8s"—you're developing *in* K8s.

---

## What This Teaches (Forced Learning)

| Day | Pain Point | What You Learn |
|-----|-----------|----------------|
| 1 | "PVC won't bind" | StorageClasses, dynamic provisioning |
| 1 | "Connection refused" | Service discovery, DNS, readiness probes |
| 1 | "Pod CrashLoopBackOff" | Init containers, migration ordering |
| 2 | "Values not applying" | Helm templating, `--set` vs `-f` |
| 2 | "Upgrade broke it" | `helm rollback`, immutable infrastructure |
| 3 | "Where are my logs?" | `kubectl logs`, log aggregation |
| 3 | "Why is it slow?" | Prometheus metrics, PromQL queries |
| 4+ | "CLI needs to handle errors" | gRPC error codes, graceful failure UX |

---

## Future Branches (When Ready)

### Branch A: Multi-Cluster
- Deploy to staging and prod clusters
- Federated Prometheus
- ArgoCD for GitOps

### Branch B: Service Mesh
- Istio/Linkerd for mTLS
- Traffic shifting (canary deploys)
- Distributed tracing (Jaeger)

### Branch C: Operator Pattern
- L-Gent as a K8s operator
- CRDs for catalog entries
- Reconciliation loops

---

## Success Criteria (Revised)

### Operational Confidence
- Can diagnose "why is the cluster unhealthy?" in < 2 minutes
- Can rollback a bad deploy in < 30 seconds
- Can explain what every pod is doing

### Infrastructure as Instinct
- Think in Services, not scripts
- Think in Resources (CPU/memory), not "my laptop"
- Think in Releases, not "I'll just edit this file"

### The Tightest Loop
- Edit code → See change in cluster → See metrics in Grafana
- Total latency: < 30 seconds

---

## Getting Started: Day 1, Hour 1

Ready? Here's literally the first hour:

```bash
# 0:00 - Ensure Kind is running
kgents infra init

# 0:05 - Apply PostgreSQL manifest
kubectl apply -f infra/k8s/manifests/l-gent-postgres.yaml

# 0:10 - Debug why PVC is pending
kubectl describe pvc -n kgents-system
# → Learn about StorageClasses

# 0:20 - Fix StorageClass, PVC binds
kubectl get pvc -n kgents-system  # → Bound

# 0:25 - Apply L-Gent deployment
kubectl apply -f infra/k8s/manifests/l-gent-deployment.yaml

# 0:30 - Debug why init container is failing
kubectl logs -n kgents-system deploy/l-gent -c wait-for-db
# → Learn about service discovery

# 0:40 - Fix service name, pod starts
kubectl get pods -n kgents-system  # → Running

# 0:50 - Port-forward and test
kubectl port-forward svc/l-gent 50051:50051 -n kgents-system &
kgents library catalog
# → Empty list (but from Postgres!)

# 1:00 - Register first artifact
kgents library register ./impl/claude/agents/l/cli.py --type=agent
kgents library catalog
# → Shows cli.py in catalog (persisted in Postgres)
```

**You just learned more about K8s in 1 hour than 4 phases of CLI polish would have taught you.**

---

## Next Steps: From Plan to Reality

The manifests are done. Here's the bridge to working code:

### Immediate (Phase 1.3-1.4)

**1. Create the PostgresRegistry backend**

```bash
# File: impl/claude/agents/l/postgres_backend.py
# Dependencies: asyncpg, pgvector
cd impl/claude && uv add asyncpg pgvector
```

The code is in Section 1.3 above. Key points:
- No fallback to in-memory (crash-only design)
- Uses `asyncpg.Pool` with pgvector extension
- `create_registry()` factory that dies if `DATABASE_URL` not set

**2. Add CLI handler for library command**

```bash
# File: impl/claude/protocols/cli/handlers/library.py
# Pattern: Same as existing handlers (status.py, dream.py)
```

Wire up: `catalog`, `discover`, `register` subcommands.

**3. Test the stack end-to-end**

```bash
# Start cluster (already have K-Terrarium)
kgents infra init
kgents infra status

# Deploy L-Gent stack
kubectl apply -f impl/claude/infra/k8s/manifests/l-gent-postgres.yaml
kubectl apply -f impl/claude/infra/k8s/manifests/l-gent-deployment.yaml

# Watch pods come up
kubectl get pods -n kgents-agents -w

# Port-forward to test
kubectl port-forward svc/l-gent-postgres 5432:5432 -n kgents-agents &
psql postgresql://lgent:lgent-dev-password@localhost:5432/lgent -c '\dt'
```

### Then (Phase 2)

**4. Create Helm chart skeleton**

```bash
mkdir -p charts/l-gent/templates
# Move manifests into templates/
# Create values.yaml, Chart.yaml
```

### Deferred

- Phase 3 (Prometheus metrics) - after basic flow works
- Phase 4 (Rich CLI) - after metrics prove the system works

---

## Quick Reference: Existing Files

| File | Purpose |
|------|---------|
| `infra/k8s/manifests/l-gent-postgres.yaml` | StatefulSet + Secret + init scripts |
| `infra/k8s/manifests/l-gent-deployment.yaml` | Deployment + ConfigMap + Service (placeholder image) |
| `agents/l/catalog.py` | Existing in-memory catalog (to be replaced) |
| `agents/l/semantic_registry.py` | Existing registry (add Postgres backend) |

---

Say **"let's start Day 1"** when ready.
