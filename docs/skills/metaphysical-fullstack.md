# Skill: Metaphysical Fullstack Agent

> *"Every agent is a fullstack agent. The more fully defined, the more fully projected."*

## The Pattern

Every kgents agent follows a vertical slice architecture where **completeness of definition determines completeness of projection**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROJECTION SURFACES                          │
│   CLI  │  TUI  │  Web UI  │  marimo  │  JSON API  │  VR  │ ... │
└────────┼───────┼──────────┼──────────┼────────────┼──────┼─────┘
         │       │          │          │            │      │
         ▼       ▼          ▼          ▼            ▼      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CONTAINER FUNCTOR (Main Website)               │
│           Shallow passthrough for component projections          │
│           Elastic composition of underlying surfaces             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              AGENTESE UNIVERSAL PROTOCOL                        │
│   The protocol IS the API. No explicit routes needed.            │
│   logos.invoke("self.memory.capture", observer, content=...)     │
│   → CLI, HTTP, WebSocket, gRPC all collapse to the same path     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENTESE NODE                              │
│   @node("self.memory")  ─or─  @node("world.town.citizen")       │
│   Semantic interface: aspects, effects, affordances              │
│   Makes service available to all projections                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE MODULE                             │
│   services/brain/  ─or─  services/town/  ─or─  services/park/   │
│   Business logic + TableAdapters + D-gent integration            │
│   Frontend components live here (if any)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                         │
│   models/  │  agents/d/  │  agents/poly/  │  LLM clients  │ ... │
│   Generic, reusable categorical primitives                       │
└─────────────────────────────────────────────────────────────────┘
```

## The Insight: Why Adapters Live in Service Modules

**Infrastructure doesn't know:**
- What tables are for
- Why they're needed
- When to use them
- Business context

**Service modules know:**
- Domain semantics
- When to persist what
- Business rules
- How to compose adapters

```python
# ❌ WRONG: Adapter in infrastructure
# models/brain.py or agents/d/adapters/
class CrystalAdapter:
    """Generic adapter - doesn't know Brain semantics"""

# ✅ RIGHT: Adapter in service module
# services/brain/persistence.py
class BrainPersistence:
    """Knows Brain domain: when to crystal, how to index, what to surface"""

    def __init__(self, table_adapter: TableAdapter[Crystal], dgent: DgentProtocol):
        self.table = table_adapter  # For queryable metadata
        self.dgent = dgent          # For semantic content

    async def capture(self, content: str, tags: list[str]) -> CaptureResult:
        """Business logic: dual-track storage with domain awareness"""
        # 1. Store semantic content in D-gent (for associations)
        datum = await self.dgent.put(Datum(...))

        # 2. Store queryable metadata in table (for fast queries)
        crystal = Crystal(datum_id=datum.id, tags=tags, ...)
        await self.table.put(crystal)

        return CaptureResult(...)
```

## The Fullstack Flow

### 1. Service Module (Foundation)

```
services/brain/
├── __init__.py           # Public API
├── crystal.py            # Core Brain logic
├── persistence.py        # TableAdapter + D-gent integration
├── search.py             # Semantic search
├── web/                  # Frontend components (if any)
│   ├── components/       # React/Svelte components
│   └── hooks/            # Frontend hooks
└── _tests/
```

### 2. AGENTESE Node (Semantic Interface)

```python
# protocols/agentese/contexts/self_memory.py

@dataclass
class MemoryNode:
    """AGENTESE node wrapping Brain service."""

    persistence: BrainPersistence  # Injected from service module

    @aspect(category=AspectCategory.MUTATION, effects=[Effect.WRITES("crystals")])
    async def capture(self, observer: Observer, content: str) -> CaptureResult:
        return await self.persistence.capture(content)

    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer) -> BrainStatus:
        return await self.persistence.status()
```

### 3. AGENTESE Universal Protocol (The API IS the Protocol)

```python
# No explicit routes needed! The protocol IS the API.
# All transports collapse to the same invocation:

# CLI
kg brain capture "content"
# → logos.invoke("self.memory.capture", cli_observer, content="content")

# HTTP (auto-generated from AGENTESE registration)
POST /agentese/self.memory.capture
# → logos.invoke("self.memory.capture", http_observer, content=body.content)

# WebSocket
{"path": "self.memory.capture", "args": {"content": "..."}}
# → logos.invoke("self.memory.capture", ws_observer, content=msg.content)

# gRPC, GraphQL, etc. - all the same pattern
```

**Key Insight**: Backend routes are NOT declared. The AGENTESE protocol auto-exposes all registered nodes through a universal gateway. Transport is an implementation detail.

### 4. Frontend (Lives with Service)

```typescript
// services/brain/web/components/CrystalViewer.tsx
// Frontend component for Brain - lives in service module
export function CrystalViewer({ crystalId }: Props) {
    // Calls AGENTESE universal protocol
    const { data } = useAgentese("self.memory.crystal", { id: crystalId });
    return <CrystalCard crystal={data} />;
}
```

### 5. Main Website (Container Functor)

```typescript
// impl/claude/web/app/brain/page.tsx
// Main website is shallow passthrough - just composes projections
import { CrystalViewer } from '@kgents/services/brain/web';  // From service module

export default function BrainPage() {
    return (
        <PageShell>
            <CrystalViewer />  {/* Projection from service module */}
        </PageShell>
    );
}
```

## Intelligent Resolution

When parts are defined but others aren't, the system provides:

### Fallbacks

| Missing | Fallback |
|---------|----------|
| Frontend component | Auto-generated from AGENTESE metadata |
| CLI projection | Default table/JSON rendering |
| Help text | Generated from aspect docstrings |
| Error messages | Sympathetic defaults |

### Guardrails

| Check | Behavior |
|-------|----------|
| No service module | Error: "Agent X has no implementation" |
| No AGENTESE node | Warning: "Agent X not semantically registered" |
| No persistence | Works in-memory only, warns on restart |
| No effects declared | Validation error at registration |

### Progressive Enhancement

```python
# Agent with minimal definition
@node("self.minimal")
class MinimalAgent:
    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(self) -> dict:
        return {"status": "minimal"}
# → CLI works, API works, Web shows JSON

# Agent with full definition
@node("self.rich")
class RichAgent:
    persistence: RichPersistence       # Full dual-track
    frontend: "RichViewer"             # Custom component

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("rich_data"), Effect.CALLS("llm")],
        help="Do something rich",
        examples=["kg rich do 'something'"],
        budget_estimate="medium",
        streaming=True,
    )
    async def do(self, ...) -> RichResult:
        ...
# → Full CLI, full API, rich Web UI, streaming, budget tracking
```

## Checklist: Making an Agent Fullstack

- [ ] **Service Module** (`agents/<name>/`)
  - [ ] Core business logic
  - [ ] Persistence layer (TableAdapter + D-gent)
  - [ ] Frontend components (if needed)
  - [ ] Tests

- [ ] **AGENTESE Node** (`protocols/agentese/contexts/`)
  - [ ] `@node` decorator with path
  - [ ] `@aspect` decorators with metadata
  - [ ] Effects declared
  - [ ] Help text and examples

- [ ] **Projections** (automatic once node exists)
  - [ ] CLI via projection functor
  - [ ] API via AGENTESE router
  - [ ] Web via container composition

## Anti-Patterns

```python
# ❌ Adapter in CLI handler
def cmd_brain(args):
    adapter = TableAdapter(Crystal, session_factory)  # Wrong place!
    ...

# ❌ Explicit backend routes (routes should not exist!)
@router.post("/brain/capture")
async def capture(request):
    ...  # Wrong - AGENTESE universal protocol handles this

# ❌ Business logic in any route
@router.post("/anything")
async def anything(request):
    crystal = Crystal(...)  # Wrong - should go through AGENTESE node
    session.add(crystal)

# ❌ Frontend bypassing AGENTESE
const crystal = await fetch('/db/crystals/123');  // Direct DB access!

# ❌ Main website with embedded logic
export default function BrainPage() {
    const [crystals, setCrystals] = useState([]);
    useEffect(() => { loadCrystals(); }, []);  // Logic should be in service
}

# ❌ Service in agents/ directory
agents/brain/  # Wrong - services/ is for Crown Jewels
               # agents/ is for categorical primitives (PolyAgent, Operad, etc.)
```

## Directory Structure

```
impl/claude/
├── agents/           # Categorical primitives (infrastructure)
│   ├── poly/         # PolyAgent[S, A, B]
│   ├── operad/       # Composition grammar
│   ├── sheaf/        # Global coherence
│   ├── flux/         # Stream processing
│   ├── d/            # D-gent (generic persistence)
│   └── ...           # Other algebraic agents
│
├── services/         # Crown Jewels (consumers of agents/)
│   ├── brain/        # Memory cathedral
│   ├── gardener/     # Cultivation practice
│   ├── town/         # Agent simulation
│   ├── park/         # Westworld hosts
│   ├── atelier/      # Creative workshop
│   ├── coalition/    # Agent collaboration
│   └── gestalt/      # Living code garden
│
├── models/           # SQLAlchemy models (generic)
├── protocols/        # AGENTESE, CLI projection, API gateway
└── web/              # Container functor (shallow passthrough)
```

## Related

- `spec/principles.md` §AD-009 - Metaphysical Fullstack Agent
- `spec/protocols/projection.md` - Projection Protocol
- `spec/protocols/agentese.md` - AGENTESE Universal Protocol
- `docs/skills/building-agent.md` - Agent construction
- `plans/d-gent-dual-track-architecture.md` - Persistence architecture

---

*"The metaphysical fullstack agent is complete in definition, universal in projection."*
