# Portal Resource System

> *"Every kgents concept is addressable. Every address is expandable."*

**Status:** Canonical Specification
**Date:** 2025-12-25
**Prerequisites:** `portal-token.md`, `chat-unified.md`, `witness-primitives.md`
**Implementation:** `services/portal/` (planned)

---

## Epigraph

> *"The portal is the universal reference. Chat, crystal, trace, file—all are expandable."*
>
> *"You don't navigate to the resource. The resource comes to you."*

---

## Part I: Purpose

Portal tokens (§15 of `portal-token.md`) currently reference file paths. This spec generalizes portals to reference **any kgents resource**:

- Chat sessions and individual turns
- Memory crystals
- Witness marks and policy traces
- Constitutional scores
- Evidence bundles
- AGENTESE nodes

This unification enables:
1. **Cross-referencing** between documents and conversations
2. **Inline expansion** of chat context within specs
3. **Evidence citation** with expandable proof
4. **Memory linking** across time and sessions

---

## Part II: Resource URIs

### 2.1 URI Grammar

```bnf
PortalURI     := ResourceType ":" ResourcePath Fragment?
ResourceType  := "file" | "chat" | "turn" | "mark" | "crystal"
               | "trace" | "evidence" | "constitutional"
               | "witness" | "node"
ResourcePath  := Identifier ("/" Identifier)*
Fragment      := "#" FragmentSpec
FragmentSpec  := "turn-" Number | "mark-" Identifier | Identifier
```

### 2.2 Resource Type Catalog

| Type | URI Pattern | Content Type | Example |
|------|-------------|--------------|---------|
| `file:` | `file:<path>` | File contents | `file:spec/protocols/witness.md` |
| `chat:` | `chat:<session_id>` | Session summary | `chat:session-abc123` |
| `turn:` | `chat:<session_id>#turn-<n>` | Specific turn | `chat:session-abc123#turn-5` |
| `mark:` | `mark:<session_id>#turn-<n>` | ChatMark + scores | `mark:session-abc123#turn-5` |
| `crystal:` | `crystal:<crystal_id>` | Memory crystal | `crystal:design-decisions-2025` |
| `trace:` | `trace:<session_id>` | PolicyTrace | `trace:session-abc123` |
| `evidence:` | `evidence:<session_id>` | Evidence bundle | `evidence:session-abc123` |
| `constitutional:` | `constitutional:<session_id>` | Constitutional radar | `constitutional:session-abc123` |
| `witness:` | `witness:<mark_id>` | Witness mark | `witness:mark-xyz123` |
| `node:` | `node:<agentese_path>` | AGENTESE node | `node:world.brain.status` |

### 2.3 Implicit File Prefix

For backward compatibility, URIs without a prefix are treated as files:

```markdown
@[tests -> services/brain/_tests/]
# Equivalent to:
@[tests -> file:services/brain/_tests/]
```

---

## Part III: Portal Syntax Integration

### 3.1 Typed Portals

```markdown
# File references (existing, with implicit file: prefix)
@[tests -> services/brain/_tests/]
@[implements -> spec/protocols/witness.md]

# Chat references
@[context -> chat:session-abc123]
@[decision -> chat:session-abc123#turn-5]
@[reasoning -> mark:session-abc123#turn-5]

# Evidence references
@[evidence -> evidence:session-abc123]
@[constitutional -> constitutional:session-abc123]
@[trace -> trace:session-abc123]

# Memory references
@[history -> crystal:design-decisions-2025]
@[witness -> witness:mark-xyz123]

# AGENTESE node references
@[status -> node:world.brain.status]
@[config -> node:self.editor.state]
```

### 3.2 Multi-Resource Portals

Reference multiple resources of potentially different types:

```markdown
@[context -> {
  chat:session-abc123,
  crystal:design-decisions-2025,
  file:spec/protocols/chat-unified.md
}]
```

### 3.3 Natural Language Curing

Unparsed portals can resolve to any resource type:

```markdown
@[what was the decision about auth?]
# LLM cure might resolve to:
# @[decision -> chat:session-def456#turn-12]
```

---

## Part IV: Resolver Architecture

### 4.1 Resolver Protocol

```python
@dataclass(frozen=True)
class ResolvedResource:
    """Result of resolving a portal URI."""

    uri: str                          # Original URI
    resource_type: str                # "chat", "file", etc.
    exists: bool                      # Whether resource exists
    title: str                        # Display title
    preview: str                      # Short preview text
    content: Any                      # Full content (type varies)
    actions: list[str]                # Available actions
    metadata: dict[str, Any]          # Resource-specific metadata


class PortalResolver(Protocol):
    """Resolver for a specific resource type."""

    @property
    def resource_type(self) -> str:
        """The resource type this resolver handles."""
        ...

    def can_resolve(self, uri: str) -> bool:
        """Check if this resolver handles the given URI."""
        ...

    async def resolve(
        self, uri: str, observer: Observer
    ) -> ResolvedResource:
        """Resolve URI to resource metadata (for portal preview)."""
        ...

    async def expand(
        self, uri: str, observer: Observer
    ) -> ExpandedContent:
        """Expand URI to full content (for inline display)."""
        ...
```

### 4.2 Resolver Registry

```python
class PortalResolverRegistry:
    """Registry of portal resolvers by resource type."""

    resolvers: dict[str, PortalResolver]

    def register(self, resolver: PortalResolver) -> None:
        """Register a resolver for a resource type."""
        self.resolvers[resolver.resource_type] = resolver

    def get_resolver(self, uri: str) -> PortalResolver | None:
        """Get resolver for a URI."""
        resource_type = self._parse_resource_type(uri)
        return self.resolvers.get(resource_type)

    async def resolve(
        self, uri: str, observer: Observer
    ) -> ResolvedResource:
        """Resolve any URI through appropriate resolver."""
        resolver = self.get_resolver(uri)
        if resolver is None:
            raise UnknownResourceType(uri)
        return await resolver.resolve(uri, observer)
```

---

## Part V: Resource Resolvers

### 5.1 ChatResolver

Resolves chat sessions and turns.

```python
class ChatResolver(PortalResolver):
    """Resolver for chat: and turn: resources."""

    resource_type = "chat"

    async def resolve(
        self, uri: str, observer: Observer
    ) -> ResolvedResource:
        """
        Resolve chat session or turn.

        URI patterns:
        - chat:session-abc123           → Full session
        - chat:session-abc123#turn-5    → Specific turn
        """
        session_id, turn_number = self._parse_uri(uri)
        session = await self.session_store.get(session_id)

        if turn_number is not None:
            # Specific turn
            turn = session.turns[turn_number]
            return ResolvedResource(
                uri=uri,
                resource_type="turn",
                exists=True,
                title=f"Turn {turn_number}",
                preview=turn.user_message[:100],
                content={
                    "user_message": turn.user_message,
                    "assistant_response": turn.assistant_response,
                },
                actions=["expand", "fork_from", "cite"],
                metadata={
                    "session_id": session_id,
                    "turn_number": turn_number,
                    "timestamp": turn.started_at.isoformat(),
                },
            )
        else:
            # Full session
            return ResolvedResource(
                uri=uri,
                resource_type="chat",
                exists=True,
                title=f"Chat: {session.node.branch_name}",
                preview=f"{session.turn_count} turns",
                content=session.to_dict(),
                actions=["expand", "fork", "resume"],
                metadata={
                    "session_id": session_id,
                    "turn_count": session.turn_count,
                    "flow_state": session.flow_state.value,
                },
            )
```

### 5.2 MarkResolver

Resolves ChatMarks with constitutional scores.

```python
class MarkResolver(PortalResolver):
    """Resolver for mark: resources."""

    resource_type = "mark"

    async def resolve(
        self, uri: str, observer: Observer
    ) -> ResolvedResource:
        """
        Resolve ChatMark.

        URI pattern: mark:session-abc123#turn-5
        """
        session_id, turn_number = self._parse_uri(uri)
        session = await self.session_store.get(session_id)
        mark = session.policy_trace.get_mark(turn_number)

        return ResolvedResource(
            uri=uri,
            resource_type="mark",
            exists=mark is not None,
            title=f"Mark: Turn {turn_number}",
            preview=mark.summary if mark else "Mark not found",
            content={
                "user_message": mark.user_message,
                "assistant_response": mark.assistant_response,
                "constitutional_scores": (
                    mark.constitutional_scores.to_dict()
                    if mark.constitutional_scores else None
                ),
                "tools_used": list(mark.tools_used),
                "reasoning": mark.reasoning,
            },
            actions=["expand", "view_constitutional"],
            metadata={
                "session_id": session_id,
                "turn_number": turn_number,
                "timestamp": mark.timestamp.isoformat() if mark else None,
            },
        )
```

### 5.3 ConstitutionalResolver

Resolves constitutional scores with radar visualization data.

```python
class ConstitutionalResolver(PortalResolver):
    """Resolver for constitutional: resources."""

    resource_type = "constitutional"

    async def resolve(
        self, uri: str, observer: Observer
    ) -> ResolvedResource:
        """
        Resolve constitutional scores.

        URI patterns:
        - constitutional:session-abc123           → Session aggregate
        - constitutional:session-abc123#turn-5    → Turn scores
        """
        session_id, turn_number = self._parse_uri(uri)
        session = await self.session_store.get(session_id)

        if turn_number is not None:
            # Specific turn's scores
            mark = session.policy_trace.get_mark(turn_number)
            scores = mark.constitutional_scores if mark else None
        else:
            # Aggregate session scores
            history = session.get_constitutional_history()
            scores = self._aggregate_scores(history)

        return ResolvedResource(
            uri=uri,
            resource_type="constitutional",
            exists=scores is not None,
            title="Constitutional Scores",
            preview=f"Score: {scores.weighted_total():.1f}" if scores else "No scores",
            content={
                "scores": scores.to_dict() if scores else None,
                "radar_data": self._to_radar_data(scores) if scores else None,
            },
            actions=["expand", "view_radar"],
            metadata={
                "session_id": session_id,
                "turn_number": turn_number,
                "weighted_total": scores.weighted_total() if scores else None,
            },
        )

    def _to_radar_data(self, scores: PrincipleScore) -> list[dict]:
        """Convert scores to radar chart data format."""
        return [
            {"axis": "Tasteful", "value": scores.tasteful},
            {"axis": "Curated", "value": scores.curated},
            {"axis": "Ethical", "value": scores.ethical},
            {"axis": "Joy-Inducing", "value": scores.joy_inducing},
            {"axis": "Composable", "value": scores.composable},
            {"axis": "Heterarchical", "value": scores.heterarchical},
            {"axis": "Generative", "value": scores.generative},
        ]
```

### 5.4 CrystalResolver

Resolves memory crystals.

```python
class CrystalResolver(PortalResolver):
    """Resolver for crystal: resources."""

    resource_type = "crystal"

    async def resolve(
        self, uri: str, observer: Observer
    ) -> ResolvedResource:
        """
        Resolve memory crystal.

        URI pattern: crystal:<crystal_id>
        """
        crystal_id = self._parse_uri(uri)
        crystal = await self.crystal_store.get(crystal_id)

        return ResolvedResource(
            uri=uri,
            resource_type="crystal",
            exists=crystal is not None,
            title=crystal.title if crystal else f"Crystal: {crystal_id}",
            preview=crystal.summary[:200] if crystal else "Crystal not found",
            content={
                "content": crystal.content,
                "tags": crystal.tags,
                "created_at": crystal.created_at.isoformat(),
                "source_session": crystal.source_session_id,
            },
            actions=["expand", "edit", "link"],
            metadata={
                "crystal_id": crystal_id,
                "tag_count": len(crystal.tags) if crystal else 0,
            },
        )
```

### 5.5 TraceResolver

Resolves PolicyTraces.

```python
class TraceResolver(PortalResolver):
    """Resolver for trace: resources."""

    resource_type = "trace"

    async def resolve(
        self, uri: str, observer: Observer
    ) -> ResolvedResource:
        """
        Resolve PolicyTrace.

        URI pattern: trace:session-abc123
        """
        session_id = self._parse_uri(uri)
        session = await self.session_store.get(session_id)
        trace = session.policy_trace

        return ResolvedResource(
            uri=uri,
            resource_type="trace",
            exists=True,
            title=f"Trace: {session_id}",
            preview=f"{trace.turn_count} marks",
            content={
                "marks": [m.to_dict() for m in trace.get_marks()],
                "turn_count": trace.turn_count,
            },
            actions=["expand", "export", "replay"],
            metadata={
                "session_id": session_id,
                "turn_count": trace.turn_count,
                "latest_timestamp": (
                    trace.latest_mark.timestamp.isoformat()
                    if trace.latest_mark else None
                ),
            },
        )
```

### 5.6 EvidenceResolver

Resolves Evidence bundles.

```python
class EvidenceResolver(PortalResolver):
    """Resolver for evidence: resources."""

    resource_type = "evidence"

    async def resolve(
        self, uri: str, observer: Observer
    ) -> ResolvedResource:
        """
        Resolve Evidence bundle.

        URI pattern: evidence:session-abc123
        """
        session_id = self._parse_uri(uri)
        session = await self.session_store.get(session_id)
        evidence = session.evidence

        return ResolvedResource(
            uri=uri,
            resource_type="evidence",
            exists=True,
            title=f"Evidence: {session_id}",
            preview=f"Confidence: {evidence.confidence:.0%}",
            content={
                "prior": {
                    "alpha": evidence.prior.alpha,
                    "beta": evidence.prior.beta,
                },
                "confidence": evidence.confidence,
                "observations": evidence.prior.alpha + evidence.prior.beta,
            },
            actions=["expand", "view_posterior"],
            metadata={
                "session_id": session_id,
                "confidence": evidence.confidence,
            },
        )
```

---

## Part VI: Expanded Content Rendering

### 6.1 Content Types

Each resource type has a specific expanded rendering:

| Resource | Expanded Content |
|----------|------------------|
| `file:` | Syntax-highlighted file content |
| `chat:` | Turn list with messages |
| `turn:` | User/Assistant message pair |
| `mark:` | Turn + constitutional scores |
| `crystal:` | Crystal content + tags |
| `trace:` | Timeline of marks |
| `evidence:` | Confidence + prior visualization |
| `constitutional:` | Radar chart |
| `witness:` | Mark details |
| `node:` | AGENTESE node manifest |

### 6.2 Frontend Components

```tsx
// Resource-aware portal rendering
function PortalContent({ resource }: { resource: ResolvedResource }) {
  switch (resource.resource_type) {
    case 'file':
      return <FileContent content={resource.content} />;
    case 'chat':
      return <ChatSessionPreview session={resource.content} />;
    case 'turn':
      return <TurnPreview turn={resource.content} />;
    case 'mark':
      return <MarkPreview mark={resource.content} />;
    case 'constitutional':
      return <ConstitutionalRadar data={resource.content.radar_data} />;
    case 'crystal':
      return <CrystalPreview crystal={resource.content} />;
    case 'trace':
      return <TraceTimeline trace={resource.content} />;
    case 'evidence':
      return <EvidencePreview evidence={resource.content} />;
    default:
      return <GenericContent content={resource.content} />;
  }
}
```

---

## Part VII: Typeahead for Resource Types

### 7.1 Resource Type Selection

When creating a portal, typeahead shows resource types:

```
User types: @[
┌─────────────────────────────────────────┐
│ 📂 file      Files and paths            │
│ 💬 chat      Chat sessions              │
│ 🎯 turn      Specific turns             │
│ 📝 mark      Marks with scores          │
│ 💎 crystal   Memory crystals            │
│ 📊 evidence  Evidence bundles           │
│ 🌈 constitutional  Principle scores     │
│ 🔗 node      AGENTESE nodes             │
│ ➕ Custom edge type...                  │
└─────────────────────────────────────────┘
```

### 7.2 Resource-Specific Search

After selecting type, search shows relevant resources:

```
User types: @[chat ->
┌─────────────────────────────────────────┐
│ 🔍 Search chat sessions...              │
├─────────────────────────────────────────┤
│ 💬 session-abc123    Design discussion  │
│    12 turns, 2h ago                     │
│ 💬 session-def456    Auth implementation│
│    8 turns, yesterday                   │
│ 💬 session-ghi789    Bug fix review     │
│    3 turns, 3d ago                      │
└─────────────────────────────────────────┘
```

### 7.3 Fragment Selection

For resources with fragments, offer sub-selection:

```
User types: @[turn -> chat:session-abc123#
┌─────────────────────────────────────────┐
│ Select turn:                            │
├─────────────────────────────────────────┤
│ 📍 turn-1   "How should we handle..."   │
│ 📍 turn-2   "I think we should..."      │
│ 📍 turn-3   "Let's use the adapter..."  │
│ 📍 turn-4   "Good idea, here's the..."  │
└─────────────────────────────────────────┘
```

---

## Part VIII: Laws

### 8.1 URI Parsing Roundtrip

```
render(parse(uri)) ≡ uri
```

### 8.2 Resolver Composition

Resolvers compose—resolving a nested reference works:

```
resolve("chat:session-abc123#turn-5") ≡
    resolve("chat:session-abc123").turns[5]
```

### 8.3 Resource Type Completeness

Every registered resource type has a resolver:

```
∀ type ∈ ResourceType, ∃ resolver ∈ Registry : resolver.resource_type = type
```

### 8.4 Observer-Dependent Expansion

Same resource, different observers → different expansions:

```
expand(uri, developer_observer) ≠ expand(uri, guest_observer)
```

---

## Part IX: AGENTESE Integration

### 9.1 Portal Node

```python
@node(
    "self.portal.resolve",
    dependencies=("portal_registry",),
    description="Resolve portal URIs to expandable content"
)
@dataclass
class PortalResolveNode:
    registry: PortalResolverRegistry

    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(
        self, observer: Observer, uri: str
    ) -> ResolvedResource:
        """Resolve a portal URI."""
        return await self.registry.resolve(uri, observer)

    @aspect(category=AspectCategory.MUTATION)
    async def create(
        self, observer: Observer, edge_type: str, destination: str
    ) -> str:
        """Create a portal and return markdown syntax."""
        return f"@[{edge_type} -> {destination}]"
```

### 9.2 Portal Paths

```
self.portal.resolve      → Resolve URI to content
self.portal.create       → Create portal syntax
self.portal.types        → List available resource types
self.portal.search       → Search for resources by type
```

---

## Part X: Implementation Phases

| Phase | Focus | Components |
|-------|-------|------------|
| **1** | URI Parser | `PortalURI` dataclass, parser |
| **2** | Resolver Registry | `PortalResolverRegistry`, protocol |
| **3** | Chat Resolvers | `ChatResolver`, `MarkResolver`, `TraceResolver` |
| **4** | Evidence Resolvers | `EvidenceResolver`, `ConstitutionalResolver` |
| **5** | Crystal Resolver | `CrystalResolver` |
| **6** | Frontend | Resource-aware `PortalToken`, type renderers |
| **7** | Typeahead | Resource-type selection, resource search |

---

## Part XI: Anti-Patterns

- **Deep nesting** — Limit fragment depth to 2 levels
- **Circular references** — Detect and prevent `A -> B -> A`
- **Stale references** — Resources may be deleted; show "missing" state
- **Over-resolution** — Don't auto-expand all portals; lazy load
- **Type proliferation** — Keep resource types curated (10 max)

---

## Part XII: Connection to Principles

| Principle | How Portal Resources Embody It |
|-----------|-------------------------------|
| **Tasteful** | Limited resource types; each justified |
| **Curated** | 10 types, not 100; quality over quantity |
| **Ethical** | Resources respect access control |
| **Joy-Inducing** | Inline expansion delights; discovery is treasure |
| **Composable** | Resolvers compose; URIs compose |
| **Heterarchical** | Any resource can reference any other |
| **Generative** | This spec generates the implementation |

---

*"Every kgents concept is addressable. Every address is expandable."*

*"The portal is the universal reference. The resource comes to you."*

---

**Filed:** 2025-12-25
**Status:** Canonical
