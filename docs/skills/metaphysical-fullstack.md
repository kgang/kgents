# Skill: Metaphysical Fullstack Agent

> *"Every agent is a fullstack agent. The more fully defined, the more fully projected."*

## The Pattern

Every kgents agent follows a vertical slice architecture where **completeness of definition determines completeness of projection**:

```
┌─────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES                                          │
│     CLI  │  TUI  │  Web UI  │  marimo  │  JSON API  │  VR  │ ... │
└──────────┼───────┼──────────┼──────────┼────────────┼──────┼─────┘
           │       │          │          │            │      │
           ▼       ▼          ▼          ▼            ▼      ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. CONTAINER FUNCTOR (Main Website)                             │
│     Shallow passthrough for component projections                │
│     Elastic composition of underlying surfaces                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. AGENTESE UNIVERSAL PROTOCOL                                  │
│     The protocol IS the API. No explicit routes needed.          │
│     logos.invoke("self.memory.capture", observer, content=...)   │
│     → CLI, HTTP, WebSocket, gRPC all collapse to the same path   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. AGENTESE NODE                                                │
│     @node("self.memory")  ─or─  @node("world.town.citizen")      │
│     Semantic interface: aspects, effects, affordances            │
│     Makes service available to all projections                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. SERVICE MODULE (Crown Jewels)                                │
│     services/brain/  ─or─  services/town/  ─or─  services/park/  │
│     Business logic + Frontend components + D-gent integration    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. CATEGORICAL INFRASTRUCTURE                                   │
│     agents/poly/  │  agents/operad/  │  agents/sheaf/  │ ...     │
│     PolyAgent, Operad, Sheaf — generic categorical primitives    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. PERSISTENCE LAYER (D-gent)                                   │
│     StorageProvider: membrane.db, vectors.json, blobs/           │
│     XDG-compliant paths, graceful degradation, migrations        │
│     See: spec/agents/d-gent.md, docs/skills/unified-storage.md   │
└─────────────────────────────────────────────────────────────────┘
```

**Layer 1 (Persistence)** is the foundation. Every stateful agent ultimately persists through `StorageProvider`:

```python
from protocols.cli.instance_db import StorageProvider

storage = await StorageProvider.from_config()
await storage.relational.execute("INSERT INTO shapes ...")
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

<details>
<summary>🌫️ Ghost: Adapters in Infrastructure</summary>

The first implementation put `CrystalAdapter` in `models/` alongside SQLAlchemy tables. Clean separation of concerns, right?

Wrong. The adapter needed Brain-specific logic: *when* to crystallize, *how* to index for semantic search, *what* metadata to surface. Generic infrastructure can't know these things.

We tried injecting callbacks:
```python
# The path not taken
class CrystalAdapter:
    on_create: Callable[[Crystal], Awaitable[None]]  # Callback injection
```

This scattered domain logic across callback definitions. The adapter became a puppet with strings everywhere.

The ghost was laid to rest when we moved adapters to service modules. **Domain logic lives with domain knowledge.**

</details>

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

@node(
    "self.memory",
    dependencies=("brain_persistence",),  # ⚠️ MUST register in providers!
)
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

**✅ DI Contract (Enlightened Resolution)**: Every `dependencies=("foo",)` in `@node` MUST have a matching provider registered in `services/providers.py`. The container now **fails immediately** with actionable `DependencyNotFoundError` for required deps. Optional deps (with `| None = None` default) are skipped gracefully. See `agentese-node-registration.md` → "Enlightened Resolution".

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

<details>
<summary>🌫️ Ghost: The Express.js Pattern</summary>

The familiar path beckoned:

```python
# The ghost that haunted us
@router.post("/brain/capture")
async def capture_crystal(request: CaptureRequest):
    crystal = await brain_service.capture(request.content)
    return {"id": crystal.id}

@router.get("/brain/crystals/{id}")
async def get_crystal(id: str):
    ...
```

Every service would have a `routes.py`. We'd document endpoints in OpenAPI. The frontend would call explicit URLs.

The problem: **semantic paths and API paths would drift**. AGENTESE says `self.memory.capture`; the API says `/brain/crystals`. Two sources of truth, inevitable divergence.

The ghost was exorcised by AD-009: AGENTESE paths ARE the API. `logos.invoke("self.memory.capture", ...)` works over HTTP, WebSocket, CLI, gRPC—any transport. No routes to maintain because the protocol IS the route.

</details>

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

<details>
<summary>🌫️ Ghost: The Frontend/Backend Split</summary>

Convention said: `impl/claude/web/` for all frontend, `impl/claude/` for all backend. Clean. Familiar.

But then: where does `CrystalViewer` live? It's Brain-specific React code. Under the split:

```
impl/claude/web/components/brain/CrystalViewer.tsx  # Frontend location
impl/claude/services/brain/crystal.py               # Backend location
```

The component and its domain logic are separated by directory structure. Change the Brain domain model? Hunt through two trees.

The resolution: **frontend lives with its service**. `services/brain/web/` contains Brain's React components. The main website is a shallow container that imports and composes. When you need to understand Brain, everything is in `services/brain/`.

*"The persona is a garden, not a museum"* — and gardens keep related things together.

</details>

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

## Prompt Ownership: The Voice Lives with the Soul

**Agent prompts belong to the agent, not the service layer.**

The system prompt IS the agent's voice—it should live in the agent's directory, not in generic service code.

```python
# ❌ WRONG: Prompts in service layer
# services/chat/factory.py
SOUL_SYSTEM_PROMPT = """You are K-gent..."""  # Service doesn't own this!

# ✅ RIGHT: Prompts in agent directory
# agents/k/prompts.py
SOUL_SYSTEM_PROMPT = """You are K-gent..."""  # K-gent owns its own voice

# services/chat/factory.py
from agents.k.prompts import SOUL_SYSTEM_PROMPT  # Service imports from agent
```

### Why This Matters

1. **Cohesion**: The prompt defines personality, voice anchors, behavioral examples—all agent-specific
2. **Discoverability**: Looking for K-gent's prompt? It's in `agents/k/`
3. **Ownership**: Changes to K-gent's voice should happen in K-gent's code
4. **Consistency**: All K-gent-related prompts (modes, intercept, etc.) live together

### Prompt Directory Structure

```
agents/k/
├── prompts.py          # System prompts (SOUL_SYSTEM_PROMPT, etc.)
├── templates.py        # Zero-token template responses (DORMANT tier)
├── starters.py         # Mode-specific conversation starters
├── eigenvectors.py     # Personality coordinates (to_system_prompt_section())
├── persona.py          # Mode prompts (REFLECT, ADVISE, CHALLENGE, EXPLORE)
└── soul.py             # Intercept prompts (Semantic Gatekeeper)
```

---

## Checklist: Making an Agent Fullstack

- [ ] **Agent Directory** (`agents/<name>/`)
  - [ ] Core business logic
  - [ ] Prompts (system prompts, mode prompts)
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

# ❌ Agent prompts in service layer
# services/chat/factory.py
SOUL_SYSTEM_PROMPT = """..."""  # Wrong - K-gent owns its voice
                                # Move to agents/k/prompts.py
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
- `spec/agents/d-gent.md` - D-gent Persistence Layer Spec (Layer 1)
- `docs/skills/unified-storage.md` - Unified Storage Architecture
- `spec/protocols/projection.md` - Projection Protocol
- `spec/protocols/agentese.md` - AGENTESE Universal Protocol
- `docs/skills/building-agent.md` - Agent construction

---

*"The metaphysical fullstack agent is complete in definition, universal in projection."*
