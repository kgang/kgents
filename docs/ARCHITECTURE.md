# kgents Architecture

> *"Every agent is a fullstack agent. The more fully defined, the more fully projected."*

This document provides visual architecture diagrams for the kgents system using the Metaphysical Fullstack pattern.

---

## Table of Contents

1. [Main System Architecture](#1-main-system-architecture)
2. [The 7-Layer Stack](#2-the-7-layer-stack)
3. [Request Lifecycle](#3-request-lifecycle)
4. [Crown Jewels Ecosystem](#4-crown-jewels-ecosystem)
5. [Categorical Foundation](#5-categorical-foundation)
6. [Event-Driven Architecture](#6-event-driven-architecture)
7. [AGENTESE Path Resolution](#7-agentese-path-resolution)

---

## 1. Main System Architecture

The complete kgents system showing all major subsystems and their relationships.

```mermaid
graph TB
    subgraph Projection["Layer 7: Projection Surfaces"]
        CLI[CLI / kg command]
        Web[Web UI<br/>React + TypeScript]
        API[JSON API<br/>REST + SSE]
        WS[WebSocket<br/>Real-time]
        Marimo[marimo<br/>Notebooks]
    end

    subgraph Protocol["Layer 6: AGENTESE Protocol"]
        Logos[Logos<br/>logos.invoke path, observer, kwargs]
        Router[Router<br/>Path Resolution]
        Validator[Validator<br/>Effect Enforcement]
    end

    subgraph Node["Layer 5: AGENTESE Node"]
        NodeDec["@node decorator"]
        Aspects[Aspects<br/>manifest, capture, search...]
        Effects[Effects<br/>READS, WRITES, CALLS...]
        Affordances[Affordances<br/>Observer-Dependent]
    end

    subgraph Service["Layer 4: Service Modules - Crown Jewels"]
        Brain[Brain<br/>Memory Cathedral]
        Witness[Witness<br/>Decision Traces]
        ZeroSeed[Zero Seed<br/>Galois Loss]
        Constitutional[Constitutional<br/>Principles]
        Morpheus[Morpheus<br/>LLM Gateway]
        Chat[Chat<br/>Sessions]
        KBlock[K-Block<br/>Knowledge Units]
    end

    subgraph Operad["Layer 3: Operad Grammar"]
        AgentOperad[AGENT_OPERAD<br/>Universal Composition]
        ProbeOperad[PROBE_OPERAD<br/>Verification]
        AnalysisOperad[ANALYSIS_OPERAD<br/>Four Modes of Inquiry]
    end

    subgraph Poly["Layer 2: Polynomial Agent"]
        PolyAgent["PolyAgent[S, A, B]<br/>state x input → output"]
        Primitives[17 Primitives<br/>GROUND, JUDGE, FIX...]
    end

    subgraph Sheaf["Layer 1: Sheaf Coherence"]
        LocalSections[Local Sections<br/>Context-Specific Behavior]
        Gluing[Gluing<br/>Compatible Locals → Global]
    end

    subgraph Persistence["Layer 0: Persistence"]
        DGent[D-gent<br/>Semantic Storage]
        Postgres[(PostgreSQL)]
        SQLite[(SQLite)]
        Memory[(In-Memory)]
        Vectors[(Vector Store)]
    end

    %% Connections
    CLI --> Logos
    Web --> Logos
    API --> Logos
    WS --> Logos
    Marimo --> Logos

    Logos --> Router
    Router --> Validator
    Validator --> NodeDec

    NodeDec --> Aspects
    Aspects --> Effects
    Effects --> Affordances

    Affordances --> Brain
    Affordances --> Witness
    Affordances --> ZeroSeed
    Affordances --> Constitutional
    Affordances --> Morpheus
    Affordances --> Chat
    Affordances --> KBlock

    Brain --> AgentOperad
    Witness --> AgentOperad
    ZeroSeed --> AgentOperad

    AgentOperad --> PolyAgent
    PolyAgent --> Primitives

    Primitives --> LocalSections
    LocalSections --> Gluing

    Gluing --> DGent
    DGent --> Postgres
    DGent --> SQLite
    DGent --> Memory
    DGent --> Vectors

    classDef projection fill:#e1f5fe,stroke:#01579b
    classDef protocol fill:#f3e5f5,stroke:#4a148c
    classDef node fill:#fff3e0,stroke:#e65100
    classDef service fill:#e8f5e9,stroke:#1b5e20
    classDef operad fill:#fce4ec,stroke:#880e4f
    classDef poly fill:#fff8e1,stroke:#ff6f00
    classDef sheaf fill:#e0f2f1,stroke:#004d40
    classDef persistence fill:#eceff1,stroke:#37474f

    class CLI,Web,API,WS,Marimo projection
    class Logos,Router,Validator protocol
    class NodeDec,Aspects,Effects,Affordances node
    class Brain,Witness,ZeroSeed,Constitutional,Morpheus,Chat,KBlock service
    class AgentOperad,ProbeOperad,AnalysisOperad operad
    class PolyAgent,Primitives poly
    class LocalSections,Gluing sheaf
    class DGent,Postgres,SQLite,Memory,Vectors persistence
```

---

## 2. The 7-Layer Stack

A detailed view of each layer in the Metaphysical Fullstack pattern.

```mermaid
graph LR
    subgraph L7["7. Projection Surfaces"]
        direction TB
        L7a[CLI]
        L7b[TUI]
        L7c[Web]
        L7d[marimo]
        L7e[JSON]
        L7f[SSE]
    end

    subgraph L6["6. AGENTESE Protocol"]
        direction TB
        L6a["logos.invoke(path, observer, **kwargs)"]
        L6b[Envelope: tenant, trace, capability]
    end

    subgraph L5["5. AGENTESE Node"]
        direction TB
        L5a["@node decorator"]
        L5b[Aspects: verbs]
        L5c[Effects: side-effects]
        L5d[Affordances: what observer can do]
    end

    subgraph L4["4. Service Module"]
        direction TB
        L4a["services/name/"]
        L4b[Crown Jewel Logic]
        L4c[Persistence Adapter]
        L4d[Frontend Components]
    end

    subgraph L3["3. Operad Grammar"]
        direction TB
        L3a[Composition Laws]
        L3b[Valid Operations]
        L3c[Associativity]
    end

    subgraph L2["2. Polynomial Agent"]
        direction TB
        L2a["PolyAgent[S, A, B]"]
        L2b["state x input → output"]
        L2c[Mode-Dependent Behavior]
    end

    subgraph L1["1. Sheaf Coherence"]
        direction TB
        L1a[Local Views]
        L1b[Gluing Condition]
        L1c[Global Consistency]
    end

    subgraph L0["0. Persistence Layer"]
        direction TB
        L0a[StorageProvider]
        L0b[membrane.db]
        L0c[vectors]
        L0d[blobs]
    end

    L7 --> L6
    L6 --> L5
    L5 --> L4
    L4 --> L3
    L3 --> L2
    L2 --> L1
    L1 --> L0

    classDef layer7 fill:#e3f2fd,stroke:#1565c0
    classDef layer6 fill:#f3e5f5,stroke:#7b1fa2
    classDef layer5 fill:#fff3e0,stroke:#ef6c00
    classDef layer4 fill:#e8f5e9,stroke:#2e7d32
    classDef layer3 fill:#fce4ec,stroke:#c2185b
    classDef layer2 fill:#fff8e1,stroke:#f9a825
    classDef layer1 fill:#e0f2f1,stroke:#00695c
    classDef layer0 fill:#eceff1,stroke:#546e7a

    class L7,L7a,L7b,L7c,L7d,L7e,L7f layer7
    class L6,L6a,L6b layer6
    class L5,L5a,L5b,L5c,L5d layer5
    class L4,L4a,L4b,L4c,L4d layer4
    class L3,L3a,L3b,L3c layer3
    class L2,L2a,L2b,L2c layer2
    class L1,L1a,L1b,L1c layer1
    class L0,L0a,L0b,L0c,L0d layer0
```

---

## 3. Request Lifecycle

How a request flows through the kgents system from user input to response.

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant CLI as CLI/Web/API
    participant Gateway as AGENTESE Gateway
    participant Registry as Node Registry
    participant Container as DI Container
    participant Node as AGENTESE Node
    participant Service as Crown Jewel Service
    participant Persistence as D-gent
    participant Witness as Witness Service
    participant DB as Database

    User->>CLI: kg brain capture "thought"

    Note over CLI: Parse command to AGENTESE path

    CLI->>Gateway: POST /agentese/self/memory/capture
    Gateway->>Gateway: Build Observer from context

    Note over Gateway: Envelope: tenant_id, trace_id, capability

    Gateway->>Registry: Lookup "self.memory"
    Registry-->>Gateway: MemoryNode class

    Gateway->>Container: Resolve dependencies
    Container-->>Gateway: BrainPersistence instance

    Gateway->>Node: Instantiate MemoryNode
    Node->>Node: Validate effects + capabilities

    Note over Node: Effect: WRITES(crystals)

    Node->>Service: capture(content)
    Service->>Persistence: dgent.put(Datum)
    Persistence->>DB: INSERT into crystals

    DB-->>Persistence: crystal_id
    Persistence-->>Service: Datum

    Service->>Witness: Create Mark
    Witness->>DB: INSERT into marks

    Note over Witness: Mark: "Captured crystal {id}"

    Witness-->>Service: Mark ID
    Service-->>Node: CaptureResult

    Node-->>Gateway: Response + Mark ID
    Gateway-->>CLI: JSON Response

    Note over CLI: Project to CLI format

    CLI-->>User: Crystal captured with ID xyz
```

---

## 4. Crown Jewels Ecosystem

The major services (Crown Jewels) and how they interact.

```mermaid
graph TB
    subgraph Core["Core Crown Jewels"]
        Brain["Brain<br/>Memory Cathedral<br/>self.memory.*"]
        Witness["Witness<br/>Decision Traces<br/>self.witness.*"]
        ZeroSeed["Zero Seed<br/>Galois Loss<br/>void.axiom.*, concept.goal.*"]
        Constitutional["Constitutional<br/>Principles Enforcement<br/>concept.principles.*"]
    end

    subgraph Intelligence["Intelligence Layer"]
        Morpheus["Morpheus<br/>LLM Gateway<br/>world.morpheus.*"]
        KGent["K-gent Soul<br/>Middleware of Consciousness<br/>self.soul.*"]
        Chat["Chat<br/>Session Management<br/>self.kgent.*"]
    end

    subgraph Knowledge["Knowledge Layer"]
        KBlock["K-Block<br/>Knowledge Units<br/>self.kblock.*"]
        LivingDocs["Living Docs<br/>Document Lifecycle<br/>concept.docs.*"]
        Sovereign["Sovereign<br/>Document Store<br/>world.sovereign.*"]
    end

    subgraph Experience["Experience Layer"]
        Explorer["Explorer<br/>Unified Query<br/>self.explorer.*"]
        Hypergraph["Hypergraph Editor<br/>Six-Mode Modal<br/>self.hypergraph.*"]
        Dawn["Dawn Cockpit<br/>Morning Ritual<br/>time.dawn.*"]
    end

    %% Core interactions
    Brain -->|crystals| KBlock
    Brain -->|memory access| KGent
    Witness -->|marks| ZeroSeed
    Witness -->|trails| Constitutional
    ZeroSeed -->|loss computation| Constitutional
    Constitutional -->|validation| Witness

    %% Intelligence layer
    Morpheus -->|LLM calls| KGent
    Morpheus -->|completions| Chat
    KGent -->|dialogue| Chat
    Chat -->|context| Brain

    %% Knowledge layer
    KBlock -->|units| LivingDocs
    LivingDocs -->|documents| Sovereign
    Sovereign -->|storage| KBlock

    %% Experience layer
    Explorer -->|queries| Brain
    Explorer -->|queries| KBlock
    Hypergraph -->|edits| KBlock
    Dawn -->|rituals| Witness

    %% Cross-layer
    Witness -.->|observes| Brain
    Witness -.->|observes| Chat
    Constitutional -.->|enforces| Morpheus

    classDef core fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef intel fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef knowledge fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef experience fill:#f3e5f5,stroke:#4a148c,stroke-width:2px

    class Brain,Witness,ZeroSeed,Constitutional core
    class Morpheus,KGent,Chat intel
    class KBlock,LivingDocs,Sovereign knowledge
    class Explorer,Hypergraph,Dawn experience
```

---

## 5. Categorical Foundation

The three-layer categorical pattern that all kgents domains instantiate.

```mermaid
graph TB
    subgraph Pattern["The Unified Categorical Pattern"]
        direction TB
        P1["PolyAgent<br/>State machine with mode-dependent inputs"]
        P2["Operad<br/>Composition grammar with laws"]
        P3["Sheaf<br/>Global coherence from local views"]
    end

    subgraph Town["Agent Town Instantiation"]
        T1["CitizenPolynomial<br/>IDLE → SPEAKING → REFLECTING"]
        T2["TOWN_OPERAD<br/>greet >> converse >> remember"]
        T3["TownSheaf<br/>Citizens + Environment = Emergence"]
    end

    subgraph Soul["K-gent Soul Instantiation"]
        S1["SOUL_POLYNOMIAL<br/>DORMANT → AWAKE → REFLECTING"]
        S2["SOUL_OPERAD<br/>sense >> challenge >> reflect"]
        S3["SOUL_SHEAF<br/>Aesthetic + Categorical + Joy = Kent"]
    end

    subgraph Design["Design System Instantiation"]
        D1["DesignPolynomial<br/>DRAFT → REVIEW → FINALIZED"]
        D2["DESIGN_OPERAD<br/>sketch >> refine >> crystallize"]
        D3["DesignSheaf<br/>Local styles = Global coherence"]
    end

    P1 -->|instance| T1
    P1 -->|instance| S1
    P1 -->|instance| D1

    P2 -->|instance| T2
    P2 -->|instance| S2
    P2 -->|instance| D2

    P3 -->|instance| T3
    P3 -->|instance| S3
    P3 -->|instance| D3

    classDef pattern fill:#fff8e1,stroke:#f57f17,stroke-width:3px
    classDef town fill:#e8f5e9,stroke:#2e7d32
    classDef soul fill:#e3f2fd,stroke:#1565c0
    classDef design fill:#fce4ec,stroke:#c2185b

    class P1,P2,P3 pattern
    class T1,T2,T3 town
    class S1,S2,S3 soul
    class D1,D2,D3 design
```

### The 17 Polynomial Primitives

```mermaid
graph LR
    subgraph Bootstrap["Bootstrap Primitives (7)"]
        ID[ID<br/>Identity]
        GROUND[GROUND<br/>Epistemic grounding]
        JUDGE[JUDGE<br/>Evaluation]
        CONTRADICT[CONTRADICT<br/>Tension detection]
        SUBLATE[SUBLATE<br/>Synthesis]
        COMPOSE[COMPOSE<br/>Sequential composition]
        FIX[FIX<br/>Fixed point iteration]
    end

    subgraph Perception["Perception Primitives (3)"]
        MANIFEST[MANIFEST<br/>Reveal essence]
        WITNESS[WITNESS<br/>Create trace]
        LENS[LENS<br/>Focused view]
    end

    subgraph Entropy["Entropy Primitives (3)"]
        SIP[SIP<br/>Draw randomness]
        TITHE[TITHE<br/>Pay for order]
        DEFINE[DEFINE<br/>Fix meaning]
    end

    subgraph Memory["Memory Primitives (2)"]
        REMEMBER[REMEMBER<br/>Store]
        FORGET[FORGET<br/>Release]
    end

    subgraph Teleological["Teleological Primitives (2)"]
        EVOLVE[EVOLVE<br/>Transform toward goal]
        NARRATE[NARRATE<br/>Tell the story]
    end

    classDef bootstrap fill:#e8f5e9,stroke:#1b5e20
    classDef perception fill:#e3f2fd,stroke:#1565c0
    classDef entropy fill:#f3e5f5,stroke:#7b1fa2
    classDef memory fill:#fff3e0,stroke:#e65100
    classDef teleological fill:#fce4ec,stroke:#c2185b

    class ID,GROUND,JUDGE,CONTRADICT,SUBLATE,COMPOSE,FIX bootstrap
    class MANIFEST,WITNESS,LENS perception
    class SIP,TITHE,DEFINE entropy
    class REMEMBER,FORGET memory
    class EVOLVE,NARRATE teleological
```

---

## 6. Event-Driven Architecture

The three-bus event architecture for reactive data flow.

```mermaid
graph TB
    subgraph Storage["Storage Layer"]
        DGent[D-gent<br/>Semantic Storage]
    end

    subgraph DataBus["DataBus (Single Process)"]
        DB[DataBus]
        DBE1[PUT Event]
        DBE2[DELETE Event]
        DBE3[UPGRADE Event]
        DBE4[DEGRADE Event]
    end

    subgraph DataListeners["DataBus Listeners"]
        ML[M-gent Listener<br/>Memory updates]
        TL[Trace Listener<br/>Provenance]
        BL[Bridge<br/>→ SynergyBus]
    end

    subgraph SynergyBus["SynergyBus (Cross-Jewel)"]
        SB[SynergyBus]
        SBE1[CRYSTAL_CAPTURED]
        SBE2[MARK_CREATED]
        SBE3[ANALYSIS_COMPLETE]
    end

    subgraph SynergyListeners["SynergyBus Listeners"]
        B2A[Brain → Atelier]
        A2B[Atelier → Brain]
        W2Z[Witness → ZeroSeed]
    end

    subgraph EventBus["EventBus[T] (Fan-out)"]
        EB["EventBus[TownEvent]"]
        EBE1[CITIZEN_SPOKE]
        EBE2[COALITION_FORMED]
        EBE3[DIALOGUE_ENDED]
    end

    subgraph EventListeners["EventBus Listeners"]
        SSE[SSE Endpoint<br/>Browser streaming]
        NATS[NATS Bridge<br/>Distributed]
        Widget[Widget Renderer<br/>UI updates]
    end

    %% DataBus flow
    DGent --> DB
    DB --> DBE1
    DB --> DBE2
    DB --> DBE3
    DB --> DBE4

    DBE1 --> ML
    DBE1 --> TL
    DBE1 --> BL

    %% SynergyBus flow
    BL --> SB
    SB --> SBE1
    SB --> SBE2
    SB --> SBE3

    SBE1 --> B2A
    SBE2 --> W2Z
    SBE3 --> A2B

    %% EventBus flow
    B2A --> EB
    EB --> EBE1
    EB --> EBE2
    EB --> EBE3

    EBE1 --> SSE
    EBE1 --> NATS
    EBE2 --> Widget

    classDef storage fill:#eceff1,stroke:#546e7a
    classDef databus fill:#e3f2fd,stroke:#1565c0
    classDef synergy fill:#e8f5e9,stroke:#2e7d32
    classDef eventbus fill:#fff3e0,stroke:#e65100
    classDef listener fill:#f5f5f5,stroke:#424242

    class DGent storage
    class DB,DBE1,DBE2,DBE3,DBE4 databus
    class SB,SBE1,SBE2,SBE3 synergy
    class EB,EBE1,EBE2,EBE3 eventbus
    class ML,TL,BL,B2A,A2B,W2Z,SSE,NATS,Widget listener
```

### Event Flow Summary

| Bus | Scope | Delivery | Use Case |
|-----|-------|----------|----------|
| **DataBus** | Single process | At-least-once, causal ordering | D-gent storage events |
| **SynergyBus** | Cross-jewel | Fire-and-forget, handler isolation | Crown Jewel coordination |
| **EventBus** | Fan-out | Backpressure, bounded queues | UI/streaming distribution |

---

## 7. AGENTESE Path Resolution

How AGENTESE paths are parsed, resolved, and invoked.

```mermaid
graph TB
    subgraph Input["User Input"]
        CLI["kg self.memory.capture 'thought'"]
        HTTP["POST /agentese/self/memory/capture"]
        WS["WS: {path: 'self.memory.capture'}"]
    end

    subgraph Parse["Path Parsing"]
        Parser[AGENTESE Parser]
        Context[Context: self]
        Holon[Holon: memory]
        Aspect[Aspect: capture]
    end

    subgraph Contexts["The Five Contexts"]
        World["world.*<br/>The External"]
        Self["self.*<br/>The Internal"]
        Concept["concept.*<br/>The Abstract"]
        Void["void.*<br/>The Accursed Share"]
        Time["time.*<br/>The Temporal"]
    end

    subgraph Resolution["Path Resolution"]
        Registry[Node Registry]
        AliasExpand[Alias Expansion<br/>me → self.soul]
        NodeLookup[Node Lookup]
    end

    subgraph Validation["Validation"]
        CapCheck[Capability Check<br/>Does observer have scope?]
        EffectCheck[Effect Validation<br/>READS, WRITES, CALLS]
        CategoryCheck[Category Enforcement<br/>PERCEPTION vs MUTATION]
    end

    subgraph Invocation["Invocation"]
        DIResolve[DI Resolution<br/>Get dependencies]
        NodeInstantiate[Instantiate Node]
        AspectInvoke[Invoke Aspect]
    end

    subgraph Response["Response"]
        Result[Result / Error / Refusal]
        WitnessMark[Create Witness Mark]
        Projection[Project to Surface]
    end

    %% Input to Parse
    CLI --> Parser
    HTTP --> Parser
    WS --> Parser

    Parser --> Context
    Parser --> Holon
    Parser --> Aspect

    %% Context classification
    Context --> World
    Context --> Self
    Context --> Concept
    Context --> Void
    Context --> Time

    %% Parse to Resolution
    Self --> AliasExpand
    AliasExpand --> NodeLookup
    NodeLookup --> Registry

    %% Resolution to Validation
    Registry --> CapCheck
    CapCheck --> EffectCheck
    EffectCheck --> CategoryCheck

    %% Validation to Invocation
    CategoryCheck --> DIResolve
    DIResolve --> NodeInstantiate
    NodeInstantiate --> AspectInvoke

    %% Invocation to Response
    AspectInvoke --> Result
    Result --> WitnessMark
    WitnessMark --> Projection

    classDef input fill:#e3f2fd,stroke:#1565c0
    classDef parse fill:#f3e5f5,stroke:#7b1fa2
    classDef context fill:#e8f5e9,stroke:#2e7d32
    classDef resolve fill:#fff3e0,stroke:#e65100
    classDef validate fill:#fce4ec,stroke:#c2185b
    classDef invoke fill:#fff8e1,stroke:#f9a825
    classDef response fill:#e0f2f1,stroke:#00695c

    class CLI,HTTP,WS input
    class Parser,Context,Holon,Aspect parse
    class World,Self,Concept,Void,Time context
    class Registry,AliasExpand,NodeLookup resolve
    class CapCheck,EffectCheck,CategoryCheck validate
    class DIResolve,NodeInstantiate,AspectInvoke invoke
    class Result,WitnessMark,Projection response
```

### AGENTESE Path Grammar

```
Path     := Context "." Holon "." Aspect
Context  := "world" | "self" | "concept" | "void" | "time"
Holon    := Identifier ("." Identifier)*
Aspect   := Identifier

Examples:
  self.memory.capture     → Brain capture
  world.morpheus.complete → LLM completion
  void.entropy.sip        → Draw randomness
  time.dawn.ritual        → Morning routine
  concept.principles.validate → Constitutional check
```

---

## Directory Structure

```
impl/claude/
├── agents/               # Categorical primitives (infrastructure)
│   ├── poly/             # PolyAgent[S, A, B] - polynomial functors
│   ├── operad/           # Composition grammar and laws
│   ├── sheaf/            # Global coherence from local views
│   ├── flux/             # Stream processing (discrete → continuous)
│   ├── d/                # D-gent (generic persistence)
│   ├── k/                # K-gent (soul, dialogue, governance)
│   └── ...               # Other algebraic agents (a-z taxonomy)
│
├── services/             # Crown Jewels (consumers of agents/)
│   ├── brain/            # Memory cathedral
│   ├── witness/          # Decision traces
│   ├── zero_seed/        # Galois loss computation
│   ├── constitutional/   # Principles enforcement
│   ├── morpheus/         # LLM gateway
│   ├── chat/             # Session management
│   ├── k_block/          # Knowledge units
│   └── ...               # 50+ services
│
├── protocols/            # Infrastructure protocols
│   ├── agentese/         # AGENTESE universal protocol
│   │   ├── gateway.py    # HTTP/WS router
│   │   ├── registry.py   # Node registration
│   │   ├── logos.py      # Path resolution
│   │   └── contexts/     # Node implementations
│   ├── api/              # FastAPI app
│   └── cli/              # CLI projection
│
├── models/               # SQLAlchemy models (generic)
└── web/                  # Container functor (React frontend)
```

---

## Key Insights

### 1. The Protocol IS the API

```python
# All transports collapse to the same invocation:
await logos.invoke("self.memory.capture", observer, content="thought")

# CLI:       kg brain capture "thought"
# HTTP:      POST /agentese/self/memory/capture
# WebSocket: {"path": "self.memory.capture", ...}
# gRPC:      Same pattern
```

### 2. Observer-Dependent Affordances

```python
# Same path, different observers, different results:
await logos("world.house.manifest", architect)  # → Blueprint
await logos("world.house.manifest", poet)       # → Metaphor
await logos("world.house.manifest", economist)  # → Appraisal
```

### 3. Categorical Universality

Understanding one domain teaches you the others:

| Layer | Purpose | Examples |
|-------|---------|----------|
| **PolyAgent** | State machine with mode-dependent inputs | CitizenPolynomial, SOUL_POLYNOMIAL |
| **Operad** | Composition grammar with laws | TOWN_OPERAD, DESIGN_OPERAD |
| **Sheaf** | Global coherence from local views | TownSheaf, ProjectSheaf |

### 4. Services Own Their Adapters

```python
# Services know their domain semantics
class BrainPersistence:
    def __init__(self, table_adapter: TableAdapter, dgent: DgentProtocol):
        self.table = table_adapter  # Queryable metadata
        self.dgent = dgent          # Semantic content

    async def capture(self, content: str) -> CaptureResult:
        # Dual-track storage with service awareness
        datum = await self.dgent.put(Datum(...))
        crystal = Crystal(datum_id=datum.id, ...)
        await self.table.put(crystal)
```

---

## Related Documentation

- `CLAUDE.md` - Project instructions and philosophy
- `spec/protocols/agentese.md` - AGENTESE specification
- `docs/skills/metaphysical-fullstack.md` - Fullstack pattern skill
- `docs/skills/agentese-node-registration.md` - Node registration skill
- `docs/skills/data-bus-integration.md` - Event bus skill
- `docs/systems-reference.md` - Complete systems inventory

---

*"Every agent is a fullstack agent. The more fully defined, the more fully projected."*
