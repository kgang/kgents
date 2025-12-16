---
path: plans/gestalt-live-infrastructure
status: planning
progress: 0.0
last_touched: 2025-12-16
touched_by: claude-opus-4-5
blocking: []
enables:
  - monetization/infrastructure-monitoring-saas
  - plans/core-apps/domain-simulation
parent: plans/core-apps/gestalt-architecture-visualizer
session_notes: |
  Initial plan creation (2025-12-16)
  - Expanding Gestalt to live infrastructure monitoring
  - Kubernetes, Docker, NATS, persistent data visualization
  - Real-time topology + metrics + event feed
phase_ledger:
  PLAN: touched
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.15
  spent: 0.0
  returned: 0.0
---

# Gestalt Live Infrastructure: Real-Time System Visualization

> *"See your infrastructure breathe. Watch data flow. Catch problems before they cascade."*

---

## Vision

Extend Gestalt from static codebase analysis to **live infrastructure monitoring**—a unified 3D visualization of your running system that shows:

- **Kubernetes** clusters, namespaces, pods, services
- **Docker** containers and networks
- **NATS** message flows and queue depths
- **Databases** connection pools and query patterns
- **Storage** volumes and I/O patterns
- **Custom services** via OTEL integration

All rendered in the same beautiful 3D force-directed graph, with real-time updates, animated data flows, and intelligent alerting.

---

## The Two Modes of Gestalt

| Mode | Purpose | Data Source | Update Frequency |
|------|---------|-------------|------------------|
| **Code Mode** | Architecture analysis | Static scan | On-demand |
| **Live Mode** | Infrastructure monitoring | Streaming APIs | Real-time (1-5s) |

Users can switch between modes or view both simultaneously (code modules + their runtime manifestations).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GESTALT LIVE INFRASTRUCTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   Data Sources  │    │  Aggregation    │    │  Visualization  │         │
│  │                 │    │     Layer       │    │     Layer       │         │
│  │  ┌───────────┐  │    │                 │    │                 │         │
│  │  │Kubernetes │──┼───▶│  ┌───────────┐  │    │  ┌───────────┐  │         │
│  │  │   API     │  │    │  │  Topology │  │    │  │  3D Graph │  │         │
│  │  └───────────┘  │    │  │  Builder  │──┼───▶│  │  (Three)  │  │         │
│  │  ┌───────────┐  │    │  └───────────┘  │    │  └───────────┘  │         │
│  │  │  Docker   │──┼───▶│                 │    │                 │         │
│  │  │   API     │  │    │  ┌───────────┐  │    │  ┌───────────┐  │         │
│  │  └───────────┘  │    │  │  Metrics  │  │    │  │  Metrics  │  │         │
│  │  ┌───────────┐  │    │  │  Enricher │──┼───▶│  │  Overlays │  │         │
│  │  │   NATS    │──┼───▶│  └───────────┘  │    │  └───────────┘  │         │
│  │  │  Monitor  │  │    │                 │    │                 │         │
│  │  └───────────┘  │    │  ┌───────────┐  │    │  ┌───────────┐  │         │
│  │  ┌───────────┐  │    │  │   Event   │  │    │  │   Event   │  │         │
│  │  │   OTEL    │──┼───▶│  │  Stream   │──┼───▶│  │   Feed    │  │         │
│  │  │ Collector │  │    │  └───────────┘  │    │  └───────────┘  │         │
│  │  └───────────┘  │    │                 │    │                 │         │
│  │  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │         │
│  │  │  Custom   │──┼───▶│  │  Health   │  │    │  │  Alerts   │  │         │
│  │  │ Exporters │  │    │  │  Scorer   │──┼───▶│  │  Panel    │  │         │
│  │  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │         │
│  │                 │    │                 │    │                 │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Infrastructure Entity Types

### Node Shapes (3D Geometry)

| Entity Type | Shape | Color Logic | Size Logic |
|-------------|-------|-------------|------------|
| **Namespace** | Ring/Torus | Namespace label hash | Fixed large |
| **Pod** | Sphere | Health (green→red) | CPU request |
| **Service** | Octahedron | Service type color | Connection count |
| **Deployment** | Dodecahedron | Rollout status | Replica count |
| **Container** | Cube | Health status | Memory limit |
| **NATS Subject** | Cone | Message rate heat | Queue depth |
| **Database** | Cylinder | Connection pool % | Storage size |
| **Volume** | Box | I/O utilization | Capacity |
| **ConfigMap** | Icosahedron | Age gradient | Reference count |
| **Secret** | Tetrahedron | Always amber | Fixed small |

### Edge Types (Connections)

| Edge Type | Style | Animation | Meaning |
|-----------|-------|-----------|---------|
| `network` | Solid gray | None | Network connectivity |
| `http` | Blue | Particles (req rate) | HTTP traffic |
| `grpc` | Cyan dashed | Fast particles | gRPC calls |
| `nats` | Purple | Streaming particles | Message flow |
| `volume` | Orange | Slow pulse | Volume mount |
| `depends` | Gray dashed | None | Deployment dependency |
| `owns` | White thin | None | Ownership hierarchy |

---

## Data Sources & Collectors

### 1. Kubernetes Collector

```python
# impl/claude/agents/infra/collectors/kubernetes.py

@dataclass
class K8sCollector:
    """Kubernetes cluster data collector."""

    kubeconfig: str | None = None  # Uses in-cluster config if None
    namespaces: list[str] = field(default_factory=list)  # Empty = all
    poll_interval: float = 5.0

    async def collect_topology(self) -> InfraTopology:
        """Collect current cluster topology."""
        async with kubernetes_client(self.kubeconfig) as client:
            nodes = await self._collect_nodes(client)
            namespaces = await self._collect_namespaces(client)
            pods = await self._collect_pods(client)
            services = await self._collect_services(client)
            deployments = await self._collect_deployments(client)

            return InfraTopology(
                entities=nodes + namespaces + pods + services + deployments,
                connections=self._build_connections(pods, services),
                timestamp=datetime.utcnow(),
            )

    async def stream_events(self) -> AsyncIterator[K8sEvent]:
        """Stream Kubernetes events in real-time."""
        async with kubernetes_client(self.kubeconfig) as client:
            async for event in client.watch_events():
                yield K8sEvent(
                    type=event.type,
                    object=event.object,
                    timestamp=event.timestamp,
                )
```

### 2. Docker Collector

```python
# impl/claude/agents/infra/collectors/docker.py

@dataclass
class DockerCollector:
    """Docker daemon data collector."""

    socket: str = "unix:///var/run/docker.sock"
    poll_interval: float = 3.0

    async def collect_topology(self) -> InfraTopology:
        """Collect Docker container topology."""
        async with docker_client(self.socket) as client:
            containers = await client.containers.list()
            networks = await client.networks.list()
            volumes = await client.volumes.list()

            entities = []
            for container in containers:
                entities.append(InfraEntity(
                    id=container.id[:12],
                    kind="container",
                    name=container.name,
                    status=container.status,
                    labels=container.labels,
                    metrics=await self._get_container_stats(container),
                ))

            return InfraTopology(
                entities=entities,
                connections=self._build_network_connections(containers, networks),
                timestamp=datetime.utcnow(),
            )
```

### 3. NATS Collector

```python
# impl/claude/agents/infra/collectors/nats.py

@dataclass
class NATSCollector:
    """NATS messaging system collector."""

    url: str = "nats://localhost:4222"
    monitor_url: str = "http://localhost:8222"
    poll_interval: float = 2.0

    async def collect_topology(self) -> InfraTopology:
        """Collect NATS subjects and streams."""
        async with httpx.AsyncClient() as client:
            # Get server info
            varz = await client.get(f"{self.monitor_url}/varz")
            connz = await client.get(f"{self.monitor_url}/connz")
            subsz = await client.get(f"{self.monitor_url}/subsz")

            entities = []
            # Parse subjects, streams, consumers
            for sub in subsz.json()["subscriptions"]:
                entities.append(InfraEntity(
                    id=f"nats:{sub['subject']}",
                    kind="nats_subject",
                    name=sub["subject"],
                    metrics={
                        "pending": sub.get("pending_msgs", 0),
                        "delivered": sub.get("delivered", 0),
                    },
                ))

            return InfraTopology(entities=entities, ...)

    async def stream_messages(self, subjects: list[str]) -> AsyncIterator[NATSMessage]:
        """Stream messages for visualization."""
        async with nats.connect(self.url) as nc:
            for subject in subjects:
                await nc.subscribe(subject, cb=self._on_message)
            while True:
                yield await self._message_queue.get()
```

### 4. OTEL Collector Integration

```python
# impl/claude/agents/infra/collectors/otel.py

@dataclass
class OTELCollector:
    """OpenTelemetry metrics and traces collector."""

    otlp_endpoint: str = "http://localhost:4317"

    async def collect_metrics(self) -> dict[str, MetricValue]:
        """Collect metrics from OTEL collector."""
        # Query Prometheus-compatible endpoint
        ...

    async def stream_traces(self) -> AsyncIterator[Trace]:
        """Stream traces for visualization."""
        # Connect to OTLP gRPC stream
        ...
```

---

## AGENTESE Paths for Infrastructure

```python
# impl/claude/protocols/agentese/contexts/infrastructure.py

INFRA_PATHS = {
    # Topology queries
    "world.infra.topology": "Get current infrastructure topology",
    "world.infra.topology.filter": "Filter topology by kind/namespace/label",
    "world.infra.topology.diff": "Get topology changes since timestamp",

    # Kubernetes specific
    "world.infra.k8s.namespaces": "List Kubernetes namespaces",
    "world.infra.k8s.pods": "List pods with status and metrics",
    "world.infra.k8s.services": "List services with endpoints",
    "world.infra.k8s.deployments": "List deployments with rollout status",
    "world.infra.k8s.events": "Stream Kubernetes events",

    # Docker specific
    "world.infra.docker.containers": "List Docker containers",
    "world.infra.docker.networks": "List Docker networks",
    "world.infra.docker.stats": "Get container resource stats",

    # NATS specific
    "world.infra.nats.subjects": "List NATS subjects",
    "world.infra.nats.streams": "List JetStream streams",
    "world.infra.nats.messages": "Stream messages on subjects",

    # Metrics
    "world.infra.metrics.cpu": "CPU utilization by entity",
    "world.infra.metrics.memory": "Memory utilization by entity",
    "world.infra.metrics.network": "Network I/O by entity",
    "world.infra.metrics.custom": "Custom metrics by label",

    # Health
    "world.infra.health.score": "Calculate health score for entity",
    "world.infra.health.alerts": "Get active alerts",
    "world.infra.health.history": "Get health history",
}
```

---

## API Endpoints

```python
# impl/claude/protocols/api/infrastructure.py

@router.get("/api/infra/topology")
async def get_infra_topology(
    kinds: list[str] | None = Query(None),
    namespaces: list[str] | None = Query(None),
    labels: dict[str, str] | None = Query(None),
) -> InfraTopologyResponse:
    """Get current infrastructure topology."""
    ...

@router.get("/api/infra/topology/stream")
async def stream_infra_topology() -> StreamingResponse:
    """Server-sent events stream of topology updates."""
    async def generate():
        async for update in infra_collector.stream_updates():
            yield f"data: {update.model_dump_json()}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")

@router.get("/api/infra/events/stream")
async def stream_infra_events(
    kinds: list[str] | None = Query(None),
) -> StreamingResponse:
    """Server-sent events stream of infrastructure events."""
    ...

@router.get("/api/infra/metrics/{entity_id}")
async def get_entity_metrics(
    entity_id: str,
    metrics: list[str] | None = Query(None),
    since: datetime | None = Query(None),
) -> EntityMetricsResponse:
    """Get metrics for a specific entity."""
    ...

@router.get("/api/infra/health")
async def get_infra_health() -> InfraHealthResponse:
    """Get overall infrastructure health summary."""
    ...
```

---

## Frontend Components

### 1. Live Topology View

```typescript
// impl/claude/web/src/pages/GestaltLive.tsx

export function GestaltLive() {
  const [topology, setTopology] = useState<InfraTopology | null>(null);
  const [events, setEvents] = useState<InfraEvent[]>([]);
  const [selectedEntity, setSelectedEntity] = useState<InfraEntity | null>(null);

  // Real-time topology updates via SSE
  useEffect(() => {
    const source = new EventSource('/api/infra/topology/stream');
    source.onmessage = (e) => {
      const update = JSON.parse(e.data);
      setTopology(prev => applyTopologyUpdate(prev, update));
    };
    return () => source.close();
  }, []);

  // Real-time events via SSE
  useEffect(() => {
    const source = new EventSource('/api/infra/events/stream');
    source.onmessage = (e) => {
      const event = JSON.parse(e.data);
      setEvents(prev => [event, ...prev].slice(0, 100));
    };
    return () => source.close();
  }, []);

  return (
    <div className="h-screen flex">
      {/* 3D Canvas */}
      <div className="flex-1 relative">
        <Canvas>
          <InfraScene
            topology={topology}
            onEntityClick={setSelectedEntity}
            selectedEntity={selectedEntity}
          />
        </Canvas>
        <MetricsOverlay entity={selectedEntity} />
        <HealthSummary topology={topology} />
      </div>

      {/* Side Panel */}
      <div className="w-80 border-l">
        <Tabs>
          <Tab label="Details">
            <EntityDetailPanel entity={selectedEntity} />
          </Tab>
          <Tab label="Events">
            <EventFeed events={events} />
          </Tab>
          <Tab label="Alerts">
            <AlertsPanel topology={topology} />
          </Tab>
        </Tabs>
      </div>
    </div>
  );
}
```

### 2. Infrastructure Entity Node

```typescript
// impl/claude/web/src/components/gestalt/InfraNode.tsx

const ENTITY_SHAPES: Record<InfraEntityKind, ReactNode> = {
  namespace: <torusGeometry args={[1, 0.3, 16, 32]} />,
  pod: <sphereGeometry args={[0.3, 24, 24]} />,
  service: <octahedronGeometry args={[0.4]} />,
  deployment: <dodecahedronGeometry args={[0.35]} />,
  container: <boxGeometry args={[0.4, 0.4, 0.4]} />,
  nats_subject: <coneGeometry args={[0.3, 0.5, 16]} />,
  database: <cylinderGeometry args={[0.3, 0.3, 0.5, 16]} />,
  volume: <boxGeometry args={[0.3, 0.5, 0.3]} />,
};

export function InfraNode({ entity, isSelected, onClick }: InfraNodeProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  // Animate based on entity state
  useFrame((_, delta) => {
    if (!meshRef.current) return;

    // Pulse if unhealthy
    if (entity.health < 0.5) {
      meshRef.current.scale.setScalar(
        1 + Math.sin(Date.now() * 0.005) * 0.1
      );
    }

    // Spin if processing
    if (entity.status === 'processing') {
      meshRef.current.rotation.y += delta;
    }
  });

  const color = getHealthColor(entity.health);
  const Shape = ENTITY_SHAPES[entity.kind];

  return (
    <group position={[entity.x, entity.y, entity.z]}>
      <mesh
        ref={meshRef}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        {Shape}
        <meshStandardMaterial
          color={color}
          emissive={isSelected ? color : undefined}
          emissiveIntensity={isSelected ? 0.5 : 0}
        />
      </mesh>

      {/* Status indicator */}
      <StatusIndicator status={entity.status} />

      {/* Label */}
      {(hovered || isSelected) && (
        <Html center>
          <div className="bg-gray-900/90 px-2 py-1 rounded text-xs">
            {entity.name}
          </div>
        </Html>
      )}
    </group>
  );
}
```

### 3. Event Feed Component

```typescript
// impl/claude/web/src/components/gestalt/EventFeed.tsx

export function EventFeed({ events }: EventFeedProps) {
  return (
    <div className="h-full overflow-y-auto">
      {events.map((event, i) => (
        <EventCard
          key={event.id}
          event={event}
          isNew={i < 3}  // Highlight recent events
        />
      ))}
    </div>
  );
}

function EventCard({ event, isNew }: { event: InfraEvent; isNew: boolean }) {
  const icon = EVENT_ICONS[event.type];
  const color = EVENT_COLORS[event.severity];

  return (
    <div
      className={`
        p-3 border-b border-gray-700 transition-colors
        ${isNew ? 'bg-gray-800/50 animate-pulse-once' : ''}
      `}
    >
      <div className="flex items-start gap-2">
        <span className={`text-lg ${color}`}>{icon}</span>
        <div className="flex-1 min-w-0">
          <p className="text-sm text-white font-medium truncate">
            {event.message}
          </p>
          <p className="text-xs text-gray-400 mt-0.5">
            {event.entity.kind}/{event.entity.name}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {formatRelativeTime(event.timestamp)}
          </p>
        </div>
      </div>
    </div>
  );
}
```

### 4. Metrics Overlay

```typescript
// impl/claude/web/src/components/gestalt/MetricsOverlay.tsx

export function MetricsOverlay({ entity }: { entity: InfraEntity | null }) {
  if (!entity) return null;

  const { metrics } = useEntityMetrics(entity.id);

  return (
    <div className="absolute bottom-4 left-4 bg-gray-800/90 rounded-lg p-4 w-72">
      <h3 className="text-sm font-semibold text-white mb-3">
        {entity.name}
      </h3>

      <div className="space-y-3">
        <MetricBar
          label="CPU"
          value={metrics?.cpu ?? 0}
          max={100}
          unit="%"
          color="blue"
        />
        <MetricBar
          label="Memory"
          value={metrics?.memory ?? 0}
          max={metrics?.memoryLimit ?? 100}
          unit="MB"
          color="purple"
        />
        <MetricBar
          label="Network"
          value={metrics?.networkRx ?? 0}
          max={1000}
          unit="KB/s"
          color="green"
        />
      </div>

      {entity.kind === 'nats_subject' && (
        <div className="mt-3 pt-3 border-t border-gray-700">
          <div className="flex justify-between text-xs">
            <span className="text-gray-400">Messages/sec</span>
            <span className="text-white font-mono">{metrics?.msgRate ?? 0}</span>
          </div>
          <div className="flex justify-between text-xs mt-1">
            <span className="text-gray-400">Queue depth</span>
            <span className="text-white font-mono">{metrics?.queueDepth ?? 0}</span>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Goal**: Basic Kubernetes topology visualization

- [ ] Create `InfraEntity` and `InfraTopology` data models
- [ ] Implement Kubernetes collector (pods, services, deployments)
- [ ] Add `/api/infra/topology` endpoint
- [ ] Create basic 3D visualization with entity shapes
- [ ] Add namespace ring grouping
- [ ] 20+ tests for collector and API

**Files**:
```
impl/claude/agents/infra/
├── __init__.py
├── models.py              # InfraEntity, InfraTopology, etc.
├── collectors/
│   ├── __init__.py
│   └── kubernetes.py      # K8s API client
├── _tests/
│   └── test_kubernetes.py
impl/claude/protocols/api/
├── infrastructure.py      # API endpoints
impl/claude/web/src/
├── pages/GestaltLive.tsx
├── components/gestalt/
│   └── InfraNode.tsx
```

### Phase 2: Real-Time Updates (Week 3)

**Goal**: Live streaming topology and events

- [ ] Implement SSE streaming for topology updates
- [ ] Add Kubernetes event watching
- [ ] Create event feed component
- [ ] Add entity status animations (pulse, spin)
- [ ] Implement topology diff algorithm
- [ ] 15+ tests for streaming

### Phase 3: Docker & NATS Integration (Week 4)

**Goal**: Multi-source infrastructure data

- [ ] Implement Docker collector
- [ ] Implement NATS collector
- [ ] Add message flow visualization (animated edges)
- [ ] Create unified topology builder
- [ ] Add source filtering in UI
- [ ] 20+ tests for new collectors

### Phase 4: Metrics & Health (Week 5)

**Goal**: Rich metrics visualization

- [ ] Integrate with OTEL/Prometheus
- [ ] Add metrics overlay component
- [ ] Implement health scoring algorithm
- [ ] Create alerts panel
- [ ] Add historical metrics sparklines
- [ ] 15+ tests for metrics

### Phase 5: Polish & Performance (Week 6)

**Goal**: Production-ready experience

- [ ] Optimize for 1000+ entities
- [ ] Add entity filtering and search
- [ ] Implement layout presets (by namespace, by type)
- [ ] Add connection tracing (click to highlight path)
- [ ] Mobile responsive adaptation
- [ ] E2E tests for full flow

---

## Data Models

```python
# impl/claude/agents/infra/models.py

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

class InfraEntityKind(str, Enum):
    NAMESPACE = "namespace"
    POD = "pod"
    SERVICE = "service"
    DEPLOYMENT = "deployment"
    CONTAINER = "container"
    NATS_SUBJECT = "nats_subject"
    NATS_STREAM = "nats_stream"
    DATABASE = "database"
    VOLUME = "volume"
    CONFIGMAP = "configmap"
    SECRET = "secret"
    INGRESS = "ingress"
    NODE = "node"

class InfraEntityStatus(str, Enum):
    RUNNING = "running"
    PENDING = "pending"
    FAILED = "failed"
    TERMINATING = "terminating"
    UNKNOWN = "unknown"

@dataclass
class InfraEntity:
    """A single infrastructure entity."""
    id: str
    kind: InfraEntityKind
    name: str
    namespace: str | None = None
    status: InfraEntityStatus = InfraEntityStatus.UNKNOWN
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)

    # Metrics (updated in real-time)
    health: float = 1.0  # 0.0 - 1.0
    cpu_percent: float = 0.0
    memory_bytes: int = 0
    memory_limit: int = 0
    network_rx_bytes: int = 0
    network_tx_bytes: int = 0

    # Custom metrics
    custom_metrics: dict[str, float] = field(default_factory=dict)

    # Position (calculated by layout algorithm)
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None

class InfraConnectionKind(str, Enum):
    NETWORK = "network"
    HTTP = "http"
    GRPC = "grpc"
    NATS = "nats"
    VOLUME = "volume"
    DEPENDS = "depends"
    OWNS = "owns"

@dataclass
class InfraConnection:
    """A connection between two entities."""
    source_id: str
    target_id: str
    kind: InfraConnectionKind

    # Metrics (for animated edges)
    requests_per_sec: float = 0.0
    bytes_per_sec: float = 0.0
    error_rate: float = 0.0
    latency_ms: float = 0.0

@dataclass
class InfraTopology:
    """Complete infrastructure topology snapshot."""
    entities: list[InfraEntity]
    connections: list[InfraConnection]
    timestamp: datetime

    # Summaries
    total_entities: int = 0
    healthy_count: int = 0
    warning_count: int = 0
    critical_count: int = 0

@dataclass
class InfraEvent:
    """An infrastructure event."""
    id: str
    type: str  # "Normal", "Warning", "Error"
    reason: str
    message: str
    entity_id: str
    entity_kind: InfraEntityKind
    entity_name: str
    timestamp: datetime
    severity: str  # "info", "warning", "error", "critical"
```

---

## Health Scoring Algorithm

```python
# impl/claude/agents/infra/health.py

def calculate_entity_health(entity: InfraEntity) -> float:
    """Calculate health score (0.0 - 1.0) for an entity."""

    scores = []

    # Status score
    status_scores = {
        InfraEntityStatus.RUNNING: 1.0,
        InfraEntityStatus.PENDING: 0.6,
        InfraEntityStatus.TERMINATING: 0.3,
        InfraEntityStatus.FAILED: 0.0,
        InfraEntityStatus.UNKNOWN: 0.5,
    }
    scores.append(status_scores.get(entity.status, 0.5))

    # Resource utilization score
    if entity.memory_limit > 0:
        memory_util = entity.memory_bytes / entity.memory_limit
        scores.append(1.0 - min(memory_util, 1.0) * 0.5)  # Penalize high memory

    if entity.cpu_percent > 0:
        scores.append(1.0 - min(entity.cpu_percent / 100, 1.0) * 0.3)

    # Custom metric scores (e.g., error rate, latency)
    if "error_rate" in entity.custom_metrics:
        scores.append(1.0 - entity.custom_metrics["error_rate"])

    return sum(scores) / len(scores) if scores else 0.5

def calculate_topology_health(topology: InfraTopology) -> dict:
    """Calculate aggregate health metrics."""

    healths = [e.health for e in topology.entities]

    return {
        "overall": sum(healths) / len(healths) if healths else 1.0,
        "healthy": sum(1 for h in healths if h >= 0.8),
        "warning": sum(1 for h in healths if 0.5 <= h < 0.8),
        "critical": sum(1 for h in healths if h < 0.5),
        "by_kind": {
            kind.value: {
                "count": sum(1 for e in topology.entities if e.kind == kind),
                "health": _avg([e.health for e in topology.entities if e.kind == kind]),
            }
            for kind in InfraEntityKind
        },
    }
```

---

## Configuration

```yaml
# config/infrastructure.yaml

collectors:
  kubernetes:
    enabled: true
    kubeconfig: null  # null = in-cluster
    namespaces: []    # empty = all
    poll_interval: 5.0

  docker:
    enabled: true
    socket: "unix:///var/run/docker.sock"
    poll_interval: 3.0

  nats:
    enabled: true
    url: "nats://localhost:4222"
    monitor_url: "http://localhost:8222"
    poll_interval: 2.0
    subjects:
      - "kgents.>"  # All kgents subjects

  otel:
    enabled: true
    otlp_endpoint: "http://localhost:4317"
    prometheus_endpoint: "http://localhost:9090"

visualization:
  max_entities: 1000
  layout_algorithm: "force-directed-3d"
  animation_fps: 60

health:
  cpu_warning_threshold: 0.7
  cpu_critical_threshold: 0.9
  memory_warning_threshold: 0.8
  memory_critical_threshold: 0.95

alerts:
  enabled: true
  slack_webhook: null
  pagerduty_key: null
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Topology update latency | <100ms | Time from K8s event to UI update |
| Entity render count | 1000+ | Max entities without frame drops |
| Animation FPS | 60fps | Chrome DevTools |
| Event feed latency | <500ms | Time from event to feed display |
| Health score accuracy | >90% | Correlation with actual incidents |

---

## Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `kubernetes` | Python | K8s API client |
| `aiodocker` | Python | Async Docker client |
| `nats-py` | Python | NATS client |
| `opentelemetry-*` | Python | OTEL integration |
| `sse-starlette` | Python | Server-sent events |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| K8s API rate limits | High | Implement watch/cache pattern |
| Large cluster performance | High | Virtual scrolling, LOD rendering |
| NATS message volume | Medium | Sample high-volume subjects |
| Security (K8s secrets visible) | High | Never display secret values, obfuscate in UI |

---

## Future Enhancements

1. **Multi-cluster support**: View multiple K8s clusters simultaneously
2. **Time travel**: Replay infrastructure state from historical data
3. **Anomaly detection**: ML-based unusual pattern detection
4. **Cost visualization**: Overlay cloud costs on entities
5. **Chaos engineering**: Trigger failures from the visualization
6. **GitOps integration**: Show desired vs actual state diff

---

*"Your infrastructure is a living organism. Now you can see it breathe."*
