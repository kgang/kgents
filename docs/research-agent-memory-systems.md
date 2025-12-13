# Research: Open Source Agent Memory Systems

> A deep analysis of memory architectures for AI agents, with implications for M-gents specification.

**Date**: 2025-12-13
**Status**: Research complete, ready for integration into spec

---

## Executive Summary

This document surveys the current landscape of open source agent memory systems, analyzing their architectures against kgents design principles. The key finding: **existing systems are fundamentally noun-based (storage-centric) while M-gents should be verb-based (reconstruction-centric)**.

### Key Systems Analyzed

| System | Architecture | Strengths | Limitations |
|--------|--------------|-----------|-------------|
| **Mem0** | Vector + Graph hybrid | Production-ready, graph relations | Storage-first, not generative |
| **Letta/MemGPT** | Self-editing memory hierarchy | Agent-controlled, OS metaphor | Wrapper-based, not composable |
| **Zep** | Temporal knowledge graph | Bi-temporal model, excellent recall | Complex infrastructure |
| **LangChain/LangMem** | Pluggable memory backends | Framework agnostic, flexible | Lacks coherent ontology |
| **LlamaIndex** | Index-based memory blocks | Good RAG integration | Traditional retrieval model |

---

## Part I: System-by-System Analysis

### 1. Mem0 (mem0.ai)

**Source**: [GitHub](https://github.com/mem0ai/mem0) | [Research Paper](https://arxiv.org/abs/2504.19413)

#### Architecture

Mem0 implements a **two-phase memory pipeline**:

1. **Extraction Phase**:
   - Ingests conversation context (latest exchange + rolling summary + recent messages)
   - LLM extracts candidate memories as structured facts
   - Background module maintains long-term summary asynchronously

2. **Update Phase**:
   - Each new fact compared against top-s similar entries in vector database
   - Conflict resolution via LLM judgment
   - Deduplication and consolidation

#### Memory Types

- **Episodic**: Specific events and interactions
- **Semantic**: General knowledge and facts
- **Procedural**: How-to knowledge (emerging)
- **Associative**: Relationships between entities

#### Graph Memory Enhancement (Mem0g)

Memories represented as directed labeled graph `G=(V,E,L)`:
- Nodes (V): Entities (people, locations, objects)
- Edges (E): Relationships between entities
- Labels (L): Semantic types

Two-stage extraction:
1. Entity extractor identifies key information elements
2. Relationship generator establishes connections as triplets

#### Performance (LOCOMO Benchmark)

- 26% improvement over OpenAI baseline on LLM-as-Judge metric
- 91% lower p95 latency
- 90%+ token cost reduction

#### Alignment with kgents Principles

| Principle | Score | Analysis |
|-----------|-------|----------|
| Tasteful | 7/10 | Clear purpose, but feature-heavy |
| Curated | 6/10 | Has decay mechanisms, but sprawl risk |
| Composable | 5/10 | Framework-specific integrations |
| Generative | 4/10 | Storage-first, not reconstruction-first |

**Key Insight**: Mem0's graph memory aligns with our L-gent lattice concept but lacks the holographic graceful degradation property central to M-gents.

---

### 2. Letta (MemGPT)

**Source**: [GitHub](https://github.com/letta-ai/letta) | [Docs](https://docs.letta.com/concepts/memgpt/)

#### The LLM OS Metaphor

Letta's core insight: treat memory management like an operating system, where the LLM manages its own virtual memory through tool calls.

#### Memory Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                     LETTA MEMORY TIERS                       │
├─────────────────────────────────────────────────────────────┤
│  IN-CONTEXT MEMORY (Working Memory)                         │
│  ├── persona block (agent's self-description)               │
│  ├── human block (user information)                         │
│  └── custom memory blocks                                   │
│  [Character limit: ~2k per block]                           │
├─────────────────────────────────────────────────────────────┤
│  OUT-OF-CONTEXT MEMORY (External Storage)                   │
│  ├── Archival Memory (vector DB for long-term storage)      │
│  └── Recall Memory (conversation history log)               │
└─────────────────────────────────────────────────────────────┘
```

#### Self-Editing Memory Tools

**In-context editing**:
- `memory_insert`: Add new content to a block
- `memory_replace`: Update existing entries
- `memory_rethink`: Revise stored information
- `memory_finish_edits`: Finalize changes

**External memory access**:
- `archival_memory_insert`: Store to vector DB
- `archival_memory_search`: Query vector DB
- `conversation_search`: Text-based history retrieval
- `conversation_search_date`: Temporal queries

#### Sleep-Time Agents

Letta's innovative "subconscious" pattern:
- Sleep-time agents share memory with primary agents
- Run in background during idle periods
- Enable memory consolidation without blocking main loop

This aligns perfectly with our **Hypnagogic Symbiont** concept!

#### Skill Learning (2025)

Recent addition: agents learn skills through experience:
- Past experience improves rather than degrades performance
- Dynamic skill acquisition without retraining

#### Alignment with kgents Principles

| Principle | Score | Analysis |
|-----------|-------|----------|
| Tasteful | 8/10 | Clean OS metaphor, clear purpose |
| Curated | 7/10 | Self-curation via agent control |
| Composable | 4/10 | Monolithic agent design, hard to compose |
| Generative | 6/10 | Self-editing is generative, but retrieval is not |
| Heterarchical | 5/10 | Agent controls memory, but fixed hierarchy |

**Key Insight**: The self-editing memory pattern is powerful but violates our Symbiont separation principle. Memory editing should be orthogonal to logic.

---

### 3. Zep (getzep.com)

**Source**: [GitHub](https://github.com/getzep/zep) | [Paper](https://arxiv.org/abs/2501.13956)

#### Temporal Knowledge Graph (Graphiti)

Zep's core innovation: **bi-temporal modeling**.

```
Timeline T:  Event occurrence time (when did this happen in the world?)
Timeline T': Ingestion time (when did we learn about this?)

Timestamps:
- t_created, t_expired (T'): System audit
- t_valid, t_invalid (T): Semantic validity range
```

This enables queries like:
- "What did the user believe on December 1st?"
- "When did we learn that X was no longer true?"

#### Dual Memory Structure

Mirrors psychological models:
- **Episodic Memory**: Distinct events stored as graph episodes
- **Semantic Memory**: Entity relationships and meanings

Hierarchical organization:
```
Episodes → Facts → Entities → Communities
```

#### Retrieval System

Multi-modal search with sophisticated reranking:
1. **Initial Recall**: Vector similarity + BM25 + graph traversal
2. **Reranking**:
   - Reciprocal Rank Fusion (RRF)
   - Maximal Marginal Relevance (MMR)
   - Graph-based episode-mentions reranker
   - Node distance reranker
   - Cross-encoder relevance scoring

#### Performance (DMR Benchmark)

- 94.8% accuracy (vs MemGPT's 93.4%)
- Up to 18.5% accuracy improvement over baselines
- 90% latency reduction
- <100ms query latency

#### Alignment with kgents Principles

| Principle | Score | Analysis |
|-----------|-------|----------|
| Tasteful | 7/10 | Complex but justified |
| Curated | 8/10 | Temporal decay built in |
| Composable | 6/10 | Clean APIs but infrastructure-heavy |
| Generative | 5/10 | Sophisticated retrieval, but still retrieval |
| Heterarchical | 7/10 | Graph enables flexible relationships |

**Key Insight**: The bi-temporal model is profound. M-gents should track both "when it happened" and "when we learned it"—this enables the N-gent integration for witness/trace.

---

### 4. LangChain / LangMem SDK

**Source**: [Blog](https://blog.langchain.com/memory-for-agents/) | [Docs](https://docs.langchain.com/oss/python/concepts/memory)

#### Memory Architecture

LangChain treats memory as pluggable components:

**Short-term**: FIFO queue of ChatMessage objects
- Configurable token limit (default: 30000)
- Auto-flush to long-term when exceeding ratio threshold

**Long-term**: Memory Block objects
- Process flushed messages to extract information
- Merged with short-term at retrieval time

#### Memory Block Types

- **StaticMemoryBlock**: Fixed information
- **FactExtractionMemoryBlock**: LLM-extracted facts from history
- **VectorMemoryBlock**: Vector DB storage for message batches

#### Memory Update Patterns

1. **Hot Path**: Agent explicitly decides to remember via tool calls
   - Lower latency for retrieval
   - Agent-controlled curation

2. **Background**: Separate task for memory formation
   - Eliminates latency in primary application
   - Separates concerns

#### Integration with LangGraph

LangGraph provides:
- Persistent conversation state (MemorySaver → SqliteSaver/PostgresSaver for production)
- Built-in cross-session context

#### Alignment with kgents Principles

| Principle | Score | Analysis |
|-----------|-------|----------|
| Tasteful | 5/10 | Kitchen-sink approach |
| Curated | 4/10 | Manual curation burden |
| Composable | 8/10 | Highly pluggable |
| Generative | 3/10 | Traditional RAG model |
| Heterarchical | 6/10 | Flexible but no clear hierarchy |

**Key Insight**: LangChain's pluggability is valuable but lacks a coherent ontology. M-gents need both flexibility AND a clear mental model.

---

### 5. LlamaIndex Memory

**Source**: [Blog](https://www.llamaindex.ai/blog/improved-long-and-short-term-memory-for-llamaindex-agents) | [Docs](https://docs.llamaindex.ai/en/stable/module_guides/deploying/agents/memory/)

#### Memory Component

Similar to LangChain but more structured:

**Short-term**:
- FIFO queue with configurable flush behavior
- `chat_history_token_ratio` controls when to flush (default: 0.7)

**Long-term**:
- Memory Blocks receive flushed messages
- Can optionally process/extract information
- Merged at retrieval time

#### Composable Memory

`SimpleComposableMemory`:
- Primary memory as main chat buffer
- Secondary memory sources inject into system prompt
- Enables sophisticated context composition

#### Key Configuration

```python
Memory(
    token_limit=30000,           # Total budget
    chat_history_token_ratio=0.7  # When to flush
)
```

#### Alignment with kgents Principles

| Principle | Score | Analysis |
|-----------|-------|----------|
| Tasteful | 6/10 | Clean design, focused |
| Curated | 5/10 | Automatic but not intelligent |
| Composable | 7/10 | Good composition primitives |
| Generative | 4/10 | Index-based, not generative |
| Heterarchical | 5/10 | Fixed primary/secondary hierarchy |

---

## Part II: Comparative Analysis

### Memory Model Comparison

```
                    RETRIEVAL ←───────────────────→ RECONSTRUCTION
                    (Storage-first)                 (Generation-first)
                         │                                │
    LangChain ──────────┼─────── Mem0 ────── Letta ─────┼──── M-gent Vision
                         │                                │
                    "What do I         "What can I    "What pattern
                     have?"           find that       will resonate?"
                                      relates?"
```

### Feature Matrix

| Feature | Mem0 | Letta | Zep | LangChain | LlamaIndex | M-gent Spec |
|---------|------|-------|-----|-----------|------------|-------------|
| Vector storage | Yes | Yes | Yes | Yes | Yes | Via D-gent |
| Graph relations | Yes | No | Yes | Plugin | No | Via L-gent |
| Self-editing | No | Yes | No | No | No | Via Symbiont |
| Temporal tracking | Limited | Yes | Yes (bi-temporal) | No | No | Yes |
| Graceful degradation | No | No | No | No | No | **Core** |
| Holographic compression | No | No | No | No | No | **Core** |
| Sleep consolidation | No | Yes | No | Background | No | Yes (Hypnagogic) |
| Forgetting curves | Decay | No | Temporal | No | No | **Core** |
| Composable | Limited | No | Limited | Yes | Yes | **Core** |

---

## Part III: Implications for M-gent Specification

### What M-gents Should Adopt

#### 1. From Mem0: Graph Memory Structure

The entity-relationship extraction pipeline is valuable:
```python
# Mem0 pattern worth adopting
class GraphMemoryIntegration:
    """
    M-gent should integrate with L-gent's graph for relations.
    NOT replace holographic memory, but augment it.
    """
    async def extract_entities(self, memory: Memory) -> list[Entity]:
        """Extract entities for L-gent indexing."""
        pass

    async def extract_relations(self, memory: Memory) -> list[Relation]:
        """Extract relations for L-gent graph."""
        pass
```

#### 2. From Letta: Sleep-Time Processing

The sleep agent pattern aligns perfectly with Hypnagogic Symbiont:
```python
# Letta pattern worth adopting
class SleepTimeConsolidation:
    """
    Background consolidation during idle periods.
    This is our HypnagogicSymbiont pattern!
    """
    async def consolidate_during_idle(
        self,
        primary_memory: HolographicMemory,
        consolidator: ConsolidationAgent
    ) -> HolographicMemory:
        """Run consolidation when system is idle."""
        pass
```

#### 3. From Zep: Bi-Temporal Model

This is profound and should be adopted:
```python
@dataclass(frozen=True)
class BiTemporalMemory:
    """
    Memory with two time dimensions.

    t_event: When did this happen in the world?
    t_known: When did we learn about it?

    This enables:
    - "What did I believe on date X?"
    - "When did my understanding change?"
    - Integration with N-gent witness/trace
    """
    content: Memory
    t_event: datetime      # Timeline T
    t_known: datetime      # Timeline T'
    t_invalidated: datetime | None = None  # When superseded
```

#### 4. From All: Token Budget Awareness

Every system respects token limits. M-gent should too:
```python
class TokenBudgetedRecall:
    """
    Recall that respects context budget.

    This is our Foveation principle!
    """
    async def recall_within_budget(
        self,
        cue: Concept,
        budget: int
    ) -> FoveatedRecollection:
        """
        Return memories that fit within token budget.
        High-resolution at focal point, blur at periphery.
        """
        pass
```

### What M-gents Should Reject

#### 1. Storage-First Ontology

All existing systems are fundamentally about **storing and retrieving**. M-gents are about **reconstruction**.

```python
# ANTI-PATTERN from existing systems
memory.store(key, value)  # Treating memory as database
result = memory.retrieve(key)  # Exact lookup

# M-GENT PATTERN
memory.encode(concept, experience)  # Holographic encoding
recollection = await memory.reconstruct(cue)  # Generative recall
```

#### 2. Wrapper-Based Architecture

Letta's self-editing memory requires agents to be wrapped in the memory system. This violates composability.

```python
# ANTI-PATTERN: Letta's approach
class MemGPTAgent:
    """Agent that manages its own memory via tools."""
    # Memory editing is entangled with agent logic

# M-GENT PATTERN: Symbiont separation
class MemoryAwareAgent:
    """
    Memory is ORTHOGONAL to agent logic.
    The Symbiont wrapper handles state, agent is pure.
    """
    def __init__(self, logic: Agent[I, O], memory: DataAgent[S]):
        self.logic = logic  # Pure
        self.memory = memory  # Injected
```

#### 3. Fixed Memory Hierarchies

Existing systems impose fixed tiers (working → short-term → long-term). M-gents should have **fluid resolution**.

```python
# ANTI-PATTERN: Fixed tiers
class ThreeTierMemory:
    working: Memory      # Always full resolution
    short_term: Memory   # Medium resolution
    long_term: Memory    # Low resolution

# M-GENT PATTERN: Continuous resolution gradient
class HolographicMemory:
    """
    Resolution is continuous, not tiered.
    Compression doesn't move memories between tiers;
    it reduces resolution uniformly.
    """
    def compress(self, ratio: float) -> HolographicMemory:
        """All memories become ratio% fuzzier."""
        pass
```

---

## Part IV: Specification Enhancement Proposals

Based on this research, here are proposed enhancements to the M-gent specification:

### Proposal 1: Bi-Temporal Memory Model

Add to `spec/m-gents/holographic.md`:

```python
@dataclass
class TemporalCoordinates:
    """
    Bi-temporal coordinates for memory.

    Adopted from Zep's research, this enables:
    1. Historical reconstruction ("what did I think on date X?")
    2. Learning tracking ("when did my understanding change?")
    3. N-gent integration (witness/trace alignment)
    """
    t_event: datetime       # When the remembered event occurred
    t_encoded: datetime     # When memory was formed
    t_accessed: datetime    # Last retrieval (for forgetting curves)
    t_invalidated: datetime | None = None  # When superseded
```

### Proposal 2: Graph-Holographic Duality

Add to `spec/m-gents/README.md`:

```python
class DualMemoryRepresentation:
    """
    Memory exists in two complementary forms:

    1. HOLOGRAPHIC: Distributed, content-addressable, graceful degradation
       - For: Generative recall, compression, fuzzy matching
       - Stored: Interference pattern

    2. GRAPH: Structured, relational, precise
       - For: Entity relations, lineage, exact queries
       - Stored: Via L-gent lattice

    Neither is primary. They are dual views of the same information.
    """
    holographic: HolographicMemory  # M-gent core
    graph: GraphHandle  # L-gent integration

    async def sync(self):
        """
        Bidirectional sync between representations.
        Graph changes → holographic re-encoding
        Holographic consolidation → graph updates
        """
        pass
```

### Proposal 3: Foveated Context Injection Protocol

Add to `spec/m-gents/primitives.md`:

```python
@dataclass
class FoveatedContext:
    """
    Context injection following foveation principle.

    Adopted from LlamaIndex's composable memory but with
    holographic resolution gradients instead of fixed tiers.
    """
    # Focal zone: Full resolution
    focal: list[Memory]
    focal_tokens: int

    # Blur zone: Summarized
    peripheral: list[MemorySummary]
    peripheral_tokens: int

    # Horizon: Just landmarks
    horizon: list[Landmark]
    horizon_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.focal_tokens + self.peripheral_tokens + self.horizon_tokens

    @classmethod
    async def from_budget(
        cls,
        memory: HolographicMemory,
        focus: Concept,
        budget: int
    ) -> "FoveatedContext":
        """
        Generate optimal context within token budget.
        This is the answer to: "What is the most perfect
        context injection for any given turn?"
        """
        pass
```

### Proposal 4: Sleep-Time Consolidation Protocol

Add to `spec/m-gents/primitives.md`:

```python
@dataclass
class ConsolidationProtocol:
    """
    Background memory processing during idle periods.

    Adopted from Letta's sleep-time agents but integrated
    with our Hypnagogic Symbiont pattern.
    """
    # Triggers
    idle_threshold: timedelta = timedelta(minutes=5)
    memory_pressure_threshold: float = 0.8  # % of budget

    # Operations
    operations: list[ConsolidationOp] = field(default_factory=lambda: [
        ConsolidationOp.COMPRESS_COLD,
        ConsolidationOp.STRENGTHEN_HOT,
        ConsolidationOp.MERGE_SIMILAR,
        ConsolidationOp.UPDATE_GRAPH
    ])

    # Constraints
    max_duration: timedelta = timedelta(minutes=2)
    max_tokens_consumed: int = 1000

class ConsolidationOp(Enum):
    COMPRESS_COLD = "compress_cold"       # Reduce resolution of cold memories
    STRENGTHEN_HOT = "strengthen_hot"     # Increase resolution of hot memories
    MERGE_SIMILAR = "merge_similar"       # Combine near-duplicate memories
    UPDATE_GRAPH = "update_graph"         # Sync to L-gent graph
    DECAY = "decay"                       # Apply forgetting curves
```

---

## Part V: Integration Architecture

### M-gent in the kgents Ecosystem

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEMORY ECOSYSTEM INTEGRATION                  │
│                                                                  │
│  ┌─────────────┐        ┌─────────────┐       ┌─────────────┐  │
│  │   L-gent    │◄──────►│   M-gent    │◄─────►│   N-gent    │  │
│  │  (Lattice)  │ graph  │(Holographic)│ trace │  (Witness)  │  │
│  │  relations  │ sync   │   memory    │ sync  │   traces    │  │
│  └──────┬──────┘        └──────┬──────┘       └──────┬──────┘  │
│         │                      │                      │         │
│         │                      │                      │         │
│         ▼                      ▼                      ▼         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      D-gent (Persistence)                │   │
│  │   VectorAgent | GraphAgent | StreamAgent | PersistentAgent│   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### AGENTESE Paths for Memory

| Path | Aspect | Returns |
|------|--------|---------|
| `self.memory.recall` | Perception | FoveatedContext |
| `self.memory.encode` | Generation | EncodingConfirmation |
| `self.memory.consolidate` | Maintenance | ConsolidationReport |
| `self.memory.forget` | Maintenance | ForgettingReport |
| `self.memory.timeline` | Temporal | MemoryTimeline |
| `self.memory.lens` | Composition | FocusedMemory |

---

## Appendix A: Benchmark Considerations

### Proposed M-gent Benchmarks

Based on existing benchmarks (LOCOMO, DMR), M-gent should be evaluated on:

1. **Graceful Degradation**: Does 50% compression preserve 100% of memories at 50% resolution?
2. **Reconstruction Quality**: How accurate is generative recall vs exact retrieval?
3. **Temporal Coherence**: Can the system answer "what did I believe at time T?"
4. **Composition Integrity**: Does memory survive Symbiont composition?
5. **Consolidation Efficiency**: How much does sleep-time processing improve recall?

### Comparison Targets

| Metric | Mem0 | Zep | M-gent Target |
|--------|------|-----|---------------|
| DMR Accuracy | 93.4% | 94.8% | 95%+ |
| Latency p95 | ~500ms | ~100ms | <100ms |
| Token Efficiency | 90% reduction | 90% reduction | 95% reduction |
| Graceful Degradation | N/A | N/A | **Yes** (unique) |

---

## Appendix B: Research Sources

### Primary Sources

- [Mem0 GitHub Repository](https://github.com/mem0ai/mem0)
- [Mem0 Research Paper](https://arxiv.org/abs/2504.19413)
- [Letta GitHub Repository](https://github.com/letta-ai/letta)
- [MemGPT Documentation](https://docs.letta.com/concepts/memgpt/)
- [Letta Memory Management](https://docs.letta.com/advanced/memory_management)
- [Zep GitHub Repository](https://github.com/getzep/zep)
- [Zep Research Paper](https://arxiv.org/abs/2501.13956)
- [Graphiti Knowledge Graph](https://github.com/getzep/graphiti)
- [LangChain Memory Concepts](https://docs.langchain.com/oss/python/concepts/memory)
- [LangMem SDK Announcement](https://blog.langchain.com/langmem-sdk-launch/)
- [LlamaIndex Memory Documentation](https://docs.llamaindex.ai/en/stable/module_guides/deploying/agents/memory/)

### Secondary Sources

- [Mem0 AI Agent Memory Overview](https://mem0.ai/blog/memory-in-agents-what-why-and-how)
- [AWS Mem0 Integration](https://aws.amazon.com/blogs/database/build-persistent-memory-for-agentic-ai-applications-with-mem0-open-source-amazon-elasticache-for-valkey-and-amazon-neptune-analytics/)
- [MongoDB LangGraph Integration](https://www.mongodb.com/company/blog/product-release-announcements/powering-long-term-memory-for-agents-langgraph)
- [Letta v1 Agent Architecture](https://www.letta.com/blog/letta-v1-agent)

---

## Conclusion

The open source agent memory landscape is maturing rapidly, with sophisticated solutions for vector storage, graph relations, and temporal tracking. However, **no existing system implements the holographic memory model** that is central to M-gents.

M-gents should:
1. **Adopt** bi-temporal modeling (from Zep)
2. **Adopt** sleep-time consolidation (from Letta)
3. **Adopt** graph integration for relations (from Mem0)
4. **Reject** storage-first ontology (from all)
5. **Reject** wrapper-based architecture (from Letta)
6. **Maintain** holographic graceful degradation as the core differentiator

The holographic principle—"cutting memory in half doesn't lose half the data, it lowers the resolution of the whole"—remains unique to kgents and should be preserved as the foundational insight.

---

*"The mind that forgets nothing remembers nothing; the hologram holds all in each part."*
