---
path: plans/gestalt-infrastructure-expansion
status: dormant
progress: 0.0
last_touched: 2025-12-16
touched_by: claude-opus-4-5
blocking:
  - plans/core-apps/gestalt-architecture-visualizer  # Must maintain API compatibility
enables:
  - monetization/grand-initiative-monetization  # Infra visualization = enterprise upsell
session_notes: |
  Initial creation. Comprehensive expansion plan for Gestalt to include
  infrastructure elements (databases, queues, APIs) as first-class nodes.
  Extends the code-focused visualizer into a unified system topology.
  Key insight: "The architecture is not just code—it is code + infrastructure + their relationships."
phase_ledger:
  PLAN: touched
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending  # Connects to all 7 Crown Jewels
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.15  # Significant scope expansion
  spent: 0.0
  returned: 0.0
---

# Gestalt Infrastructure Expansion: Unified Architecture Topology

> *"The architecture is not just code—it is code + infrastructure + their relationships."*

**Master Plan**: `plans/core-apps/gestalt-architecture-visualizer.md`
**AGENTESE Context**: `world.codebase.*`, `world.infra.*`
**Categorical Foundation**: Sheaf (global coherence from local views), PolyAgent (state-dependent scanning)

---

## Overview

| Aspect | Detail |
|--------|--------|
| **Frame** | Unified system topology visualization |
| **Core Insight** | Code modules and infrastructure elements are **equal-class nodes** in the same 3D space |
| **Revenue Impact** | Enterprise tier ($199/seat) — infra visibility is a key upsell |
| **Status** | Dormant (dependent on Gestalt Phase 5 completion) |
| **Prerequisites** | `plans/core-apps/gestalt-architecture-visualizer.md` Phases 1-4 |

---

## The Problem

Current Gestalt visualizes **code dependencies** beautifully, but real systems are more than code:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  WHAT GESTALT SEES TODAY                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌──────────┐       ┌──────────┐       ┌──────────┐                      │
│    │ api.py   │──────▶│ brain.py │──────▶│models.py │                      │
│    └──────────┘       └──────────┘       └──────────┘                      │
│          │                                                                  │
│          │  (invisible: psycopg2.connect(...))                             │
│          ▼                                                                  │
│       ???                                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  WHAT GESTALT SHOULD SEE                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌──────────┐       ┌──────────┐       ┌──────────┐                      │
│    │ api.py   │──────▶│ brain.py │──────▶│models.py │                      │
│    └──────────┘       └──────────┘       └──────────┘                      │
│          │                  │                                               │
│          │ reads            │ writes                                        │
│          ▼                  ▼                                               │
│    ┌─────────────────────────────┐                                         │
│    │  🐘 PostgreSQL (main)       │◀──── infra:postgresql:main              │
│    │  Health: B+ | v15.2         │                                         │
│    └─────────────────────────────┘                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Design Principles

### 1. Categorical Unification (Sheaf Coherence)

All elements are `ArchNode` instances with a discriminated `kind` field. Local views (code-only, infra-only, data-flow) glue into a coherent global topology:

```python
class NodeKind(Enum):
    """Discriminated union of architecture node types."""
    MODULE = "module"           # Python/JS module (current)
    DATABASE = "database"       # PostgreSQL, SQLite, Redis
    QUEUE = "queue"             # RabbitMQ, Kafka, SQS
    API = "api"                 # External REST/GraphQL endpoints
    STORAGE = "storage"         # S3, GCS, local filesystem
    SERVICE = "service"         # Docker container, K8s pod, Lambda
    CONFIG = "config"           # .env, secrets, feature flags
    PIPELINE = "pipeline"       # CI/CD, data pipelines
    NETWORK = "network"         # Load balancers, CDN, DNS
```

### 2. Edge Semantics (Operad Composition)

Edges gain semantic types that compose meaningfully:

```python
class EdgeKind(Enum):
    """Relationship types between architecture nodes."""
    IMPORTS = "imports"         # Code imports code
    READS = "reads"             # Code reads from data store
    WRITES = "writes"           # Code writes to data store
    CALLS = "calls"             # Code calls API/service
    PUBLISHES = "publishes"     # Code publishes to queue
    SUBSCRIBES = "subscribes"   # Code subscribes to queue
    CONFIGURES = "configures"   # Config influences code/infra
    DEPLOYS = "deploys"         # Pipeline deploys service
    ROUTES = "routes"           # Network routes to service
```

### 3. Multi-Source Discovery (PolyAgent Pattern)

Infrastructure scanners behave as polynomial agents with mode-dependent inputs:

| Source File | NodeKind Yielded | EdgeKind Inferred |
|-------------|------------------|-------------------|
| `docker-compose.yml` | service, database, queue | routes |
| `kubernetes/*.yaml` | service, config | configures, routes |
| `.env`, `.env.*` | config | configures |
| `terraform/*.tf` | database, storage, service | deploys |
| Code AST (`psycopg2.connect`) | database | reads/writes |
| OpenAPI specs | api | calls |
| GitHub Actions | pipeline | deploys |

### 4. Observer-Dependent Perception (AGENTESE v3)

Different observers see different projections of the same topology:

```python
# Security engineer sees attack surface
await logos("world.codebase.manifest", security_umwelt)
# → SecurityView(vulnerable_deps, access_paths, external_apis)

# Platform engineer sees infrastructure health
await logos("world.codebase.manifest", platform_umwelt)
# → InfraView(services, databases, queues, health_scores)

# Tech lead sees governance
await logos("world.codebase.manifest", tech_lead_umwelt)
# → GovernanceView(health_grades, drift_alerts, layer_violations)
```

---

## UX Patterns Applied

### Semantic Zoom (from ux-reference-patterns.md §4.1)

| Zoom Level | Code Visibility | Infra Visibility |
|------------|-----------------|------------------|
| **System** | Agent boundaries only | External APIs, cloud regions |
| **Container** | Major modules | Databases, queues, services |
| **Component** | Individual files | Connection details, configs |
| **Code** | Function signatures | Connection strings (redacted) |

### Live Sync (from ux-reference-patterns.md §2.2)

- File watcher detects `docker-compose.yml` changes → Signal update → 3D graph re-renders
- No "refresh" button—topology is always current
- Optimistic updates with rollback on scan failure

### Governance Dashboards (from ux-reference-patterns.md §7.3)

- Health scores per node (code and infra)
- Drift alerts with actionable triage: `[Declare] [Suppress] [View Source]`
- Infrastructure governance rules (no direct DB access from API layer)

---

## Implementation Phases

### Phase 1: Data Model Extension (Chunk 1)

**Goal**: Extend existing types to support infrastructure nodes.

**Files**:
```
impl/claude/protocols/gestalt/models.py      # New: unified ArchNode
impl/claude/protocols/gestalt/analysis.py    # Extend: NodeKind, EdgeKind
impl/claude/protocols/api/models.py          # Extend: API response types
```

**Key Types**:

```python
@dataclass(frozen=True)
class ArchNode:
    """Unified architecture node—code or infrastructure."""
    id: str                          # Unique identifier
    kind: NodeKind                   # Module, database, queue, etc.
    label: str                       # Display name
    layer: str | None                # Architectural layer
    health_grade: str                # A+ to F
    health_score: float              # 0.0 to 1.0

    # Kind-specific metadata (validated by kind)
    metadata: dict[str, Any] = field(default_factory=dict)
    # MODULE: lines_of_code, coupling, cohesion
    # DATABASE: engine, version, connection_count
    # QUEUE: message_count, consumer_count
    # API: endpoint_count, auth_method
    # SERVICE: image, replicas, memory_limit

    # Position in 3D space (computed by layout algorithm)
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass(frozen=True)
class ArchEdge:
    """Relationship between architecture nodes."""
    source: str
    target: str
    kind: EdgeKind
    weight: float = 1.0              # Strength of relationship
    is_violation: bool = False       # Architectural drift
    metadata: dict[str, Any] = field(default_factory=dict)
```

**Exit Criteria**:
- [ ] `ArchNode` and `ArchEdge` types defined
- [ ] `NodeKind` and `EdgeKind` enums complete
- [ ] Existing `Module` and `DependencyEdge` migrate cleanly
- [ ] 20+ tests (type validation, serialization)

---

### Phase 2: Infrastructure Scanners (Chunk 2)

**Goal**: Discover infrastructure from config files.

**Files**:
```
impl/claude/protocols/gestalt/scanners/
├── __init__.py
├── base.py              # InfraScanner protocol
├── docker.py            # Docker Compose scanner
├── kubernetes.py        # K8s manifest scanner
├── terraform.py         # Terraform state/config scanner
├── environment.py       # .env file scanner
└── cicd.py              # GitHub Actions / GitLab CI scanner
```

**Scanner Protocol**:

```python
class InfraScanner(Protocol):
    """Protocol for infrastructure discovery."""

    def can_scan(self, root: Path) -> bool:
        """Check if this scanner applies to the project."""
        ...

    def scan(self, root: Path) -> tuple[list[ArchNode], list[ArchEdge]]:
        """Discover infrastructure nodes and edges."""
        ...

    def health_check(self, node: ArchNode) -> HealthReport:
        """Assess health of an infrastructure node."""
        ...
```

**Priority Order**:
1. **docker.py** — Most common, covers 80% of dev setups
2. **environment.py** — Universal, reveals connection strings
3. **kubernetes.py** — Production configs
4. **terraform.py** — Cloud resources
5. **cicd.py** — Pipeline dependencies

**Exit Criteria**:
- [ ] Docker Compose scanner discovers services, networks, volumes
- [ ] Environment scanner discovers connection strings (redacted)
- [ ] At least 3 scanners production-ready
- [ ] 40+ tests (golden configs, edge cases)

---

### Phase 3: Code-to-Infrastructure Edge Discovery (Chunk 3)

**Goal**: Trace code usage of infrastructure via AST scanning.

**Files**:
```
impl/claude/protocols/gestalt/scanners/code_usage.py
impl/claude/protocols/gestalt/analysis.py  # Extend import parsing
```

**Pattern Library**:

```python
# Patterns: (module, function/class) → (NodeKind, engine hint)
INFRA_PATTERNS = {
    # PostgreSQL
    ("psycopg2", "connect"): (NodeKind.DATABASE, "postgresql"),
    ("asyncpg", "connect"): (NodeKind.DATABASE, "postgresql"),
    ("sqlalchemy", "create_engine"): (NodeKind.DATABASE, "sql"),

    # Redis
    ("redis", "Redis"): (NodeKind.DATABASE, "redis"),
    ("aioredis", "from_url"): (NodeKind.DATABASE, "redis"),

    # Message queues
    ("pika", "BlockingConnection"): (NodeKind.QUEUE, "rabbitmq"),
    ("aiokafka", "AIOKafkaProducer"): (NodeKind.QUEUE, "kafka"),
    ("boto3.client", "sqs"): (NodeKind.QUEUE, "sqs"),

    # Cloud storage
    ("boto3.client", "s3"): (NodeKind.STORAGE, "s3"),
    ("google.cloud.storage", "Client"): (NodeKind.STORAGE, "gcs"),

    # HTTP clients (external APIs)
    ("httpx", "AsyncClient"): (NodeKind.API, "http"),
    ("aiohttp", "ClientSession"): (NodeKind.API, "http"),
    ("requests", "Session"): (NodeKind.API, "http"),
}
```

**Edge Inference Rules**:

| Pattern Context | Inferred EdgeKind |
|-----------------|-------------------|
| Function named `get_*`, `fetch_*`, `read_*` | READS |
| Function named `save_*`, `write_*`, `insert_*` | WRITES |
| `SELECT` in SQL string | READS |
| `INSERT`/`UPDATE`/`DELETE` in SQL string | WRITES |
| `publish` method call | PUBLISHES |
| `subscribe`/`consume` method call | SUBSCRIBES |

**Exit Criteria**:
- [ ] AST scanner detects 10+ infra usage patterns
- [ ] Edge direction (reads/writes) inferred from context
- [ ] Integration with existing Python/TS import parsing
- [ ] 30+ tests (Python + TypeScript patterns)

---

### Phase 4: Unified Layout Algorithm (Chunk 4)

**Goal**: Position nodes in 3D space with semantic meaning.

**Files**:
```
impl/claude/protocols/gestalt/layout.py    # New: 3D positioning
impl/claude/web/src/pages/Gestalt.tsx      # Update: render new node types
```

**Layout Semantics**:

```
Y-axis (vertical): Architectural layer
    +Y: Presentation (APIs, frontends)
     0: Business logic (modules)
    -Y: Data (databases, queues, storage)

X-axis (horizontal): Functional grouping
    Cluster related nodes together (k-clique reuse from Agent Town)

Z-axis (depth): External vs Internal
    +Z: Internal systems (your code)
    -Z: External services/APIs (third-party)
```

**Exit Criteria**:
- [ ] Layout algorithm positions all node kinds meaningfully
- [ ] Clustering groups related nodes
- [ ] Performance: <100ms for 500 nodes
- [ ] 15+ tests (layout invariants)

---

### Phase 5: Visual Differentiation (Chunk 5)

**Goal**: Distinct visual treatment for each node kind.

**Node Shapes by Kind**:

| Kind | Shape | Color Palette | Rationale |
|------|-------|---------------|-----------|
| MODULE | Sphere | Health-based (green→red) | Current behavior |
| DATABASE | Cylinder | Blues (#3b82f6) | Database icon convention |
| QUEUE | Torus | Purples (#8b5cf6) | Ring = message buffer |
| API | Octahedron | Oranges (#f97316) | Sharp edges = external |
| STORAGE | Box | Teals (#14b8a6) | Box = container |
| SERVICE | Dodecahedron | Pinks (#ec4899) | Complex shape = runtime |
| CONFIG | Icosahedron | Yellows (#eab308) | Many facets = options |
| PIPELINE | Cone | Grays (#6b7280) | Arrow shape = flow |

**Edge Styling by Kind**:

```typescript
const EDGE_STYLES: Record<EdgeKind, EdgeStyle> = {
  imports: { color: '#6b7280', dash: false, width: 1 },
  reads: { color: '#3b82f6', dash: false, width: 2 },
  writes: { color: '#ef4444', dash: false, width: 2 },
  calls: { color: '#f97316', dash: true, width: 1.5 },
  publishes: { color: '#8b5cf6', dash: false, width: 1.5, animated: true },
  subscribes: { color: '#8b5cf6', dash: true, width: 1.5 },
  configures: { color: '#eab308', dash: true, width: 1 },
  deploys: { color: '#6b7280', dash: true, width: 1 },
  routes: { color: '#14b8a6', dash: false, width: 2 },
};
```

**Exit Criteria**:
- [ ] All 8 node shapes rendered in Three.js
- [ ] Edge styles applied correctly
- [ ] Legend component shows all types
- [ ] Responsive: mobile shows simplified shapes
- [ ] 10+ visual snapshot tests

---

### Phase 6: Infrastructure Health Scoring (Chunk 6)

**Goal**: Health assessment for infrastructure nodes.

**Files**:
```
impl/claude/protocols/gestalt/infra_health.py
impl/claude/protocols/gestalt/governance.py  # Extend with infra rules
```

**Health Criteria by Kind**:

```python
class InfraHealthAssessor:
    """Assess health of infrastructure nodes."""

    def assess_database(self, node: ArchNode) -> HealthReport:
        """
        - Has backup configuration? (+20%)
        - Connection pooling configured? (+15%)
        - Credentials in secrets (not .env)? (+25%)
        - Version not EOL? (+20%)
        - Replicas defined (HA)? (+20%)
        """

    def assess_queue(self, node: ArchNode) -> HealthReport:
        """
        - Dead letter queue configured? (+30%)
        - Message TTL set? (+20%)
        - Consumer groups defined? (+20%)
        - Persistence enabled? (+30%)
        """

    def assess_service(self, node: ArchNode) -> HealthReport:
        """
        - Health check endpoint? (+25%)
        - Resource limits set? (+20%)
        - Replicas > 1? (+25%)
        - Image pinned to specific version? (+30%)
        """

    def assess_api(self, node: ArchNode) -> HealthReport:
        """
        - Timeout configured? (+25%)
        - Retry policy? (+25%)
        - Circuit breaker? (+25%)
        - Rate limiting? (+25%)
        """
```

**Exit Criteria**:
- [ ] Health scoring for all infrastructure node kinds
- [ ] Weights configurable via governance config
- [ ] Integration with existing `ModuleHealth` pattern
- [ ] 25+ tests (health calculation edge cases)

---

### Phase 7: Infrastructure Governance Rules (Chunk 7)

**Goal**: Drift detection for infrastructure patterns.

**Files**:
```
impl/claude/protocols/gestalt/governance.py  # Extend
```

**Rules**:

```python
INFRA_GOVERNANCE_RULES = [
    # Database rules
    GovernanceRule(
        name="db-no-direct-access",
        description="API modules should not directly access databases; use repository layer",
        severity="warning",
        check=lambda e: not (
            e.source_kind == NodeKind.MODULE and
            e.target_kind == NodeKind.DATABASE and
            "repository" not in e.source.lower() and
            "api" in e.source.lower()
        )
    ),

    # Queue rules
    GovernanceRule(
        name="queue-dead-letter",
        description="Queues should have dead letter configuration",
        severity="error",
        check=lambda n: n.kind != NodeKind.QUEUE or n.metadata.get("has_dlq", False)
    ),

    # Service rules
    GovernanceRule(
        name="service-health-check",
        description="Services should define health check endpoints",
        severity="warning",
        check=lambda n: n.kind != NodeKind.SERVICE or n.metadata.get("has_health_check", False)
    ),

    # Config rules
    GovernanceRule(
        name="config-no-secrets-in-env",
        description="Secrets should come from secret manager, not .env files",
        severity="error",
        check=lambda n: n.kind != NodeKind.CONFIG or not n.metadata.get("contains_secrets", False)
    ),

    # External API rules
    GovernanceRule(
        name="api-retry-policy",
        description="External API calls should have retry policies",
        severity="warning",
        check=lambda e: e.kind != EdgeKind.CALLS or e.metadata.get("has_retry", False)
    ),
]
```

**Exit Criteria**:
- [ ] 10+ infrastructure governance rules
- [ ] Rules integrated with existing drift detection
- [ ] Suppression support for infrastructure violations
- [ ] 20+ tests (rule triggering)

---

### Phase 8: API & UI Integration (Chunk 8)

**Goal**: Extend API and web UI for infrastructure.

**API Extensions** (`GET /v1/world/codebase/topology`):

```json
{
  "nodes": [
    {
      "id": "protocols.api.brain",
      "kind": "module",
      "label": "brain.py",
      "layer": "api",
      "health_grade": "A",
      "health_score": 0.92,
      "metadata": { "lines_of_code": 245, "coupling": 0.3 },
      "x": 2.5, "y": 1.0, "z": 0.5
    },
    {
      "id": "infra:postgresql:main",
      "kind": "database",
      "label": "PostgreSQL (main)",
      "layer": "data",
      "health_grade": "B+",
      "health_score": 0.78,
      "metadata": { "engine": "postgresql", "version": "15.2" },
      "x": 0.0, "y": -2.0, "z": 0.0
    }
  ],
  "links": [
    {
      "source": "protocols.api.brain",
      "target": "infra:postgresql:main",
      "kind": "reads",
      "is_violation": false
    }
  ],
  "stats": {
    "node_count": 156,
    "module_count": 120,
    "infra_count": 12,
    "external_count": 8,
    "link_count": 423,
    "violation_count": 3,
    "overall_grade": "B+"
  }
}
```

**UI Filter Panel**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  GESTALT CONTROLS                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Node Types:                                                                │
│  [✓] Modules    [✓] Databases   [✓] Queues                                 │
│  [✓] APIs       [✓] Services    [✓] Config                                 │
│                                                                             │
│  Relationships:                                                             │
│  [✓] Imports    [✓] Data Flow   [✓] API Calls   [✓] Events                │
│                                                                             │
│  View Presets:                                                              │
│  [Code Only] [Data Flow] [External Deps] [Full System]                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Exit Criteria**:
- [ ] API returns unified topology
- [ ] Web UI renders all node shapes
- [ ] Filter panel controls visibility
- [ ] Detail panel shows kind-specific metadata
- [ ] 30+ tests (API + E2E)

---

## AGENTESE Path Registry

| Path | Aspect | Description |
|------|--------|-------------|
| `world.codebase.infra.manifest` | manifest | All infrastructure nodes |
| `world.codebase.infra.databases.manifest` | manifest | Database nodes only |
| `world.codebase.infra.queues.manifest` | manifest | Queue nodes only |
| `world.codebase.infra.apis.manifest` | manifest | External API nodes only |
| `world.codebase.infra[id].manifest` | manifest | Single infra node details |
| `world.codebase.infra[id].health` | manifest | Health report for node |
| `world.codebase.dataflow.manifest` | manifest | Data flow edges only |
| `world.codebase.dataflow.subscribe` | witness | Live data flow updates |
| `?world.codebase.infra.*` | query | Search infrastructure nodes |

---

## User Flows

### Flow 1: First Infrastructure Discovery ("The Revelation")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ENTRY: Developer opens Gestalt after infrastructure expansion enabled        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. INITIAL SCAN (0-3 seconds)                                               │
│     ├── Gestalt detects docker-compose.yml in project root                  │
│     ├── Toast: "Found infrastructure: 3 services, 2 databases"              │
│     └── 3D view updates with new node shapes                                │
│                                                                              │
│  2. UNIFIED VIEW APPEARS                                                     │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  GESTALT: UNIFIED TOPOLOGY                 [Scan] [Filter]  │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │           ┌──────────┐  ┌──────────┐                       │     │
│     │   │    Y+     │ api.py   │──│ brain.py │   (modules = spheres) │     │
│     │   │    │      └────┬─────┘  └────┬─────┘                       │     │
│     │   │    │           │ reads       │ writes                       │     │
│     │   │    │           ▼             ▼                              │     │
│     │   │    │      ╭─────────────────────────╮                       │     │
│     │   │    0      │   🐘 PostgreSQL (main)   │  (database = cylinder)│     │
│     │   │    │      ╰─────────────────────────╯                       │     │
│     │   │    │           │                                            │     │
│     │   │    │           │ configures                                 │     │
│     │   │    │           ▼                                            │     │
│     │   │   Y-      ╭─────────────╮                                   │     │
│     │   │           │  .env (db)  │  (config = icosahedron)          │     │
│     │   │           ╰─────────────╯                                   │     │
│     │   │                                                             │     │
│     │   │  Stats: 45 modules | 3 services | 2 databases | B+ overall │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Color legend appears showing all node types                          │
│                                                                              │
│  3. CLICK INFRASTRUCTURE NODE                                                │
│     ├── User clicks on PostgreSQL cylinder                                   │
│     ├── Detail panel slides in:                                              │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  🐘 PostgreSQL (main)                        Health: B+     │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  Engine:    PostgreSQL 15.2                                │     │
│     │   │  Source:    docker-compose.yml:12                          │     │
│     │   │  Accessed:  4 modules                                      │     │
│     │   │                                                             │     │
│     │   │  Health Checklist:                                          │     │
│     │   │  ✅ Connection pooling configured                           │     │
│     │   │  ✅ Version not EOL                                         │     │
│     │   │  ⚠️ Credentials in .env (should use secrets)               │     │
│     │   │  ⚠️ No backup configuration found                          │     │
│     │   │                                                             │     │
│     │   │  Accessing Modules:                                         │     │
│     │   │  • protocols.api.brain (reads/writes)                      │     │
│     │   │  • agents.m.cortex (reads/writes)                          │     │
│     │   │  • protocols.api.billing (reads)                           │     │
│     │   │                                                             │     │
│     │   │  [View Config] [Trace Data Flow] [Add Governance Rule]     │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Health warnings are actionable (click to view recommendation)        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 2: Data Flow Tracing ("The Path")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: Developer wants to understand how data moves through the system    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. SELECT DATA FLOW PRESET                                                  │
│     ├── User clicks [Data Flow] in view presets                             │
│     ├── Non-data edges fade to 20% opacity                                  │
│     └── Data edges (reads/writes/publishes) highlight with animation        │
│                                                                              │
│  2. TRACE FROM SOURCE                                                        │
│     ├── User right-clicks on api.py module                                  │
│     ├── Context menu: [Trace Data Flow →]                                   │
│     ├── Click triggers animated path highlight:                              │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  DATA FLOW FROM: api.py                                     │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │   ┌────────┐                                                │     │
│     │   │   │ api.py │ ════⚡════▶ writes ════⚡════▶               │     │
│     │   │   └────────┘                              │                 │     │
│     │   │                                           ▼                 │     │
│     │   │                                    ╭──────────────╮         │     │
│     │   │                                    │ PostgreSQL   │         │     │
│     │   │                                    ╰──────────────╯         │     │
│     │   │                                           │                 │     │
│     │   │                     ════⚡════▶ reads ════⚡════▶          │     │
│     │   │                     │                                       │     │
│     │   │              ┌──────────┐                                   │     │
│     │   │              │ brain.py │                                   │     │
│     │   │              └──────────┘                                   │     │
│     │   │                                                             │     │
│     │   │  Flow: api.py → PostgreSQL ← brain.py                      │     │
│     │   │                                                             │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Animated pulses show direction of data flow                          │
│                                                                              │
│  3. EXPORT DATA FLOW DIAGRAM                                                 │
│     ├── User clicks [Export] → [Data Flow (Mermaid)]                        │
│     └── Generates:                                                           │
│         ```mermaid                                                           │
│         flowchart TD                                                         │
│           api[api.py] -->|writes| pg[(PostgreSQL)]                          │
│           brain[brain.py] -->|reads| pg                                     │
│         ```                                                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Discovery coverage | 80%+ of common infra | Scan docker-compose, k8s, .env |
| False positive rate | <10% | Verified against golden repos |
| Render performance | <500ms for 200 nodes + 500 edges | Benchmark test |
| Health accuracy | 85%+ agreement with manual review | Sampled audit |
| Test count | 200+ | `pytest --collect-only` |

---

## Non-Goals (v1)

- Real-time infrastructure monitoring (Gestalt is architecture, not observability)
- Cost analysis or FinOps
- Auto-remediation
- Multi-cloud orchestration
- Secret scanning/security audit (use dedicated tools like Snyk, Trivy)
- Runtime metrics (CPU, memory, network) — static analysis only

---

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| `plans/core-apps/gestalt-architecture-visualizer.md` | Code | Base visualizer must be Phase 4+ |
| `impl/claude/agents/town/coalitions.py` | Code | k-clique clustering for layout |
| `impl/claude/agents/i/reactive/` | Code | Signal/Computed for live updates |
| `pyyaml` | Package | Docker Compose parsing |
| `python-hcl2` | Package | Terraform parsing (optional) |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Config format fragmentation | High | Start with docker-compose; add others incrementally |
| False positive edges | Medium | Configurable pattern library; suppression file |
| Performance at scale | High | Lazy loading; level-of-detail for distant nodes |
| Secret exposure in .env scanning | Critical | Never log/display actual values; redaction mandatory |
| Scope creep to monitoring | Medium | Strict boundary: architecture only, not runtime |

---

## Cross-Synergies

| Crown Jewel | Integration Point |
|-------------|-------------------|
| **Holographic Brain** | Infrastructure knowledge crystals (DB schemas, API contracts) |
| **Coalition Forge** | Coalitions can include infrastructure agents (monitoring bot) |
| **Domain Simulation** | Simulate infrastructure failures in crisis drills |
| **The Gardener** | "Show me our data flow" → Gestalt visualization |

---

## References

- Current Gestalt: `impl/claude/web/src/pages/Gestalt.tsx`
- Gestalt backend: `impl/claude/protocols/gestalt/`
- UX patterns: `docs/skills/ux-reference-patterns.md`
- User flow docs: `docs/skills/user-flow-documentation.md`
- Similar tools: Backstage, Structurizr, IcePanel, CodeSee

---

*Last updated: 2025-12-16*
