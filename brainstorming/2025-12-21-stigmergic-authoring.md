# Stigmergic Authoring: Agents Leave Traces, Humans Curate

> *"The document is a pheromone trail. Each agent that passes leaves a mark for the next."*

---

## The Vision

Documents become **coordination surfaces** where agents leave traces that influence future agent behavior. Humans curate, but don't micromanage. The document evolves through stigmergic accumulation.

```markdown
## Design Decision: Database Choice

We chose PostgreSQL over SQLite because:
- Concurrent writes from multiple agents     <!-- 🤖 d-gent: added 2025-12-20 -->
- Vector extension for embeddings            <!-- 🤖 m-gent: added 2025-12-21 -->

<!-- 💭 STIGMERGY TRACE -->
<!-- claude-opus-4 @ 2025-12-21T14:32:00Z -->
<!-- Consider: Read replicas for scaling. See also: services/brain/persistence.py:45 -->
<!-- Confidence: 0.7 | Relevance: database-architecture -->

<!-- 💭 STIGMERGY TRACE -->
<!-- haiku @ 2025-12-21T15:10:00Z -->
<!-- Agrees with read replica suggestion. Found prior art in services/town/persistence.py -->
<!-- Confidence: 0.8 | Supports: claude-opus-4@2025-12-21T14:32:00Z -->
```

---

## Synergies with Recent Work

### 1. Morning Coffee Stigmergy

**Location**: `services/liminal/coffee/stigmergy.py`, `plans/morning-coffee-implementation.md`

Morning Coffee Phase 2 already has:
- **VoiceStigmergy**: Agents leave voice-characteristic traces
- **StigmergyTrace**: Typed trace with confidence, relevance, decay
- **TraceAggregator**: Combines traces from multiple agents

**Synergy**: Coffee stigmergy is for session handoffs. Document stigmergy is for persistent knowledge. Same primitives, different substrate.

```python
# From services/liminal/coffee/stigmergy.py (exists)
@dataclass(frozen=True)
class StigmergyTrace:
    """A trace left by an agent for future coordination."""
    agent_id: str
    timestamp: datetime
    content: str
    confidence: float
    relevance_tags: frozenset[str]
    decay_rate: float = 0.1  # How fast this trace fades

# NEW: Document-specific trace
@dataclass(frozen=True)
class DocumentStigmergyTrace(StigmergyTrace):
    """A trace anchored to a document location."""
    document_path: Path
    line_range: tuple[int, int]
    trace_type: Literal["suggestion", "warning", "context", "reference"]
    supports: str | None = None  # ID of trace this supports
    contradicts: str | None = None  # ID of trace this contradicts
```

### 2. M-gent Memory Crystals

**Location**: `agents/m/`, `spec/agents/m-gent.md`

M-gent already has:
- **Memory Crystals**: Compressed, reusable knowledge units
- **Cartography**: Spatial organization of memories
- **Stigmergy context**: `void.stigmergy` in AGENTESE

**Synergy**: Document traces crystallize into M-gent memories. High-confidence, frequently-referenced traces become permanent knowledge.

```python
# Trace → Crystal promotion
async def crystallize_traces(document: Path) -> list[MemoryCrystal]:
    """Promote high-value traces to permanent crystals."""
    traces = await get_document_traces(document)

    # Traces with high confidence + multiple supporters → crystals
    promotable = [
        t for t in traces
        if t.confidence > 0.8 and len(t.supporters) >= 2
    ]

    return [
        MemoryCrystal(
            content=trace.content,
            source=f"stigmergy:{document}:{trace.id}",
            confidence=trace.confidence,
        )
        for trace in promotable
    ]
```

### 3. void.stigmergy AGENTESE Context

**Location**: `protocols/agentese/contexts/void.py`

The `void.*` context already handles:
- **Entropy**: Randomness, serendipity
- **Gratitude**: Acknowledgment traces
- **Accursed Share**: What must be given away

**Synergy**: `void.stigmergy` becomes the AGENTESE path for document traces.

```python
# AGENTESE paths for stigmergy
await logos.invoke("void.stigmergy.leave", umwelt,
    document="spec/design.md",
    line=42,
    content="Consider caching here",
    confidence=0.7,
)

await logos.invoke("void.stigmergy.read", umwelt,
    document="spec/design.md",
    line_range=(40, 50),
)  # Returns traces in range

await logos.invoke("void.stigmergy.support", umwelt,
    trace_id="trace-abc123",
    reason="Found confirming evidence in tests",
)
```

### 4. Interactive Text Token

**Location**: `services/interactive_text/`, tokens_to_scene.py

Interactive Text provides:
- Token rendering for any markdown pattern
- Affordances (hover, click) per token type

**Synergy**: New `STIGMERGY_TRACE` token type renders agent traces inline.

```python
# New token definition
TokenDefinition(
    name="stigmergy_trace",
    pattern=TokenPattern(
        name="stigmergy_trace",
        regex=re.compile(r"<!-- 💭 STIGMERGY TRACE -->\n<!-- (.+?) -->", re.DOTALL),
        priority=5,
    ),
    affordances=(
        Affordance(
            name="view_trace",
            action=AffordanceAction.HOVER,
            handler="void.stigmergy.view",
            description="View full trace with confidence and supporters",
        ),
        Affordance(
            name="support_trace",
            action=AffordanceAction.CLICK,
            handler="void.stigmergy.support",
            description="Add your support to this trace",
        ),
        Affordance(
            name="contradict_trace",
            action=AffordanceAction.RIGHT_CLICK,
            handler="void.stigmergy.contradict",
            description="Register disagreement with reason",
        ),
    ),
)
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STIGMERGIC DOCUMENT                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Agent A reads document                                                      │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  void.stigmergy.leave                                                │    │
│  │  - content: "Consider caching here"                                  │    │
│  │  - confidence: 0.7                                                   │    │
│  │  - relevance: ["performance", "database"]                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│       │                                                                      │
│       ▼                                                                      │
│  Document updated with trace (HTML comment, invisible to humans by default) │
│       │                                                                      │
│       ▼                                                                      │
│  Agent B reads document                                                      │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  void.stigmergy.read                                                 │    │
│  │  → Returns Agent A's trace                                           │    │
│  │  → Agent B considers in its reasoning                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│       │                                                                      │
│       ├── Agrees? → void.stigmergy.support (confidence increases)           │
│       │                                                                      │
│       └── Disagrees? → void.stigmergy.contradict (records dissent)          │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  TRACE LIFECYCLE                                                     │    │
│  │                                                                      │    │
│  │  New trace → Accumulates support/contradiction → Decay over time    │    │
│  │       │              │                                │              │    │
│  │       │              ▼                                ▼              │    │
│  │       │     High confidence?              Low relevance?             │    │
│  │       │              │                                │              │    │
│  │       │              ▼                                ▼              │    │
│  │       │     Crystallize to M-gent           Fade and archive        │    │
│  │       │                                                              │    │
│  │       └──────── Human curates: accept/reject/edit ───────────────▶  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Trace Infrastructure
- Define `DocumentStigmergyTrace` dataclass
- Create `void.stigmergy` AGENTESE nodes (leave, read, support, contradict)
- Store traces in document as HTML comments (invisible by default)

### Phase 2: Trace Rendering
- Add `stigmergy_trace` token to Interactive Text
- Render traces as subtle inline annotations
- Toggle visibility: "Show agent traces" checkbox

### Phase 3: Trace Aggregation
- Aggregate traces by topic/location
- Compute confidence from support/contradiction
- Surface high-confidence traces prominently

### Phase 4: Crystallization
- Promote stable traces to M-gent crystals
- Archive faded traces (available but not shown)
- Human curation interface

### Phase 5: Agent Integration
- Claude Code leaves traces during work
- Traces inform future Claude sessions (via /hydrate)
- Cross-session coordination without explicit handoff

---

## Open Questions

1. **Trace Format**: HTML comments? YAML frontmatter? Separate sidecar file?

2. **Visibility**: Always show traces? Toggle? Show only high-confidence?

3. **Decay Function**: Linear? Exponential? Based on document activity?

4. **Contradiction Handling**: What happens when agents disagree? Vote? Human decides?

5. **Trace Spam**: How to prevent low-value traces from accumulating?

6. **Privacy**: Should trace author be visible? Anonymized? Aggregated?

---

## Research Cues

### Swarm Intelligence
- **Ant Colony Optimization**: Pheromone trails for pathfinding
- **Stigmergy (original)**: Grassé's termite studies
- **Swarm robotics**: Coordination without central control
- 🔍 *Search: "stigmergy software engineering applications"*

### Collaborative Knowledge
- **Wikipedia Talk Pages**: Discussion attached to articles
- **Google Docs Comments**: Inline collaboration
- **Roam Research**: Bidirectional linking, block references
- 🔍 *Search: "collaborative annotation systems research"*

### Reputation Systems
- **Stack Overflow**: Votes affect visibility
- **Reddit**: Karma-weighted comments
- **PageRank**: Link-based authority
- 🔍 *Search: "reputation systems decentralized knowledge"*

### Multi-Agent Coordination
- **Blackboard Architecture**: Shared workspace for agents
- **Linda Tuple Spaces**: Coordination via shared data
- **Actor Model**: Message-passing coordination
- 🔍 *Search: "multi-agent coordination without central controller"*

---

## Maximum Value Opportunities

### 1. Self-Improving Documentation
Documents accumulate wisdom from every agent that reads them. The 100th agent benefits from 99 prior agents' insights.

### 2. Implicit Knowledge Transfer
No explicit handoff needed. Agent A's traces coordinate Agent B's behavior automatically.

### 3. Collective Intelligence Emergence
Individual low-confidence traces combine into high-confidence collective knowledge.

### 4. Audit Trail
Every suggestion has provenance. "Why was this added?" has an answer.

### 5. Human-AI Symbiosis
Agents propose, humans curate. Neither alone achieves what they do together.

---

## Voice Anchors

> *"Stigmergic surface: agents append, humans curate"* — Already in meta.md. This makes it real.

> *"The persona is a garden, not a museum"* — Traces are organic. They grow, decay, get pruned.

> *"Heterarchical"* — No boss agent. Traces coordinate through the document itself.

---

## Connection to Constitution

From Principle 6 (Heterarchical):
> "Entanglement: Agents may share state without ownership; mutual influence without control."

Stigmergic authoring IS entanglement. Agents influence each other through the document, not through direct communication.

---

*Created: 2025-12-21 | Building on: Morning Coffee, M-gent, void.stigmergy, Interactive Text*
*Next: Research Wikipedia talk pages, prototype void.stigmergy.leave node*
