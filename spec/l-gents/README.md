# L-gents: The Synaptic Librarian

**Genus**: L (Library/Lattice/Lineage)
**Theme**: Knowledge curation, semantic discovery, and ecosystem connectivity
**Motto**: *"Connect the dots."*

## Overview

L-gents are the **connective tissue** of the kgents ecosystem. Where F-gents forge artifacts and C-gents compose them, L-gents ensure artifacts can **find each other**. They transform a folder of code into a **searchable, navigable, self-aware ecosystem**.

The metaphor: If F-gent is the *Blacksmith* creating tools, and C-gent is the *General* ordering them into battle, **L-gent is the Quartermaster**—cataloging inventory, knowing where everything is, understanding what works with what.

## Philosophy

> "Knowledge unconnected is knowledge lost. The library's purpose is not storage, but discovery."

L-gents synthesize three theoretical foundations:

### 1. Librarian (Knowledge Curation)

**Core Morphism**: `Query → Source[]`

Not passive storage, but **active retrieval**. L-gent doesn't just answer "do you have X?"—it answers "what X-like things might help?", offering serendipitous discovery alongside direct search.

### 2. Lattice (Ordered Structure)

**Core Morphism**: `(A, A) → LUB | GLB`

Knowledge forms a **partial order**. Some agents are more general than others. Some contracts subsume others. L-gent tracks these relationships, enabling queries like "find anything that implements this contract or a more specific one."

### 3. Lineage (Provenance)

**Core Morphism**: `Entity → Ancestry[]`

Every artifact has a history. L-gent tracks **where things came from**, enabling questions like "what was this forked from?" and "what depends on this?" This is the ecosystem's git—but for semantic relationships, not just files.

## The Joy Factor: Serendipity

L-gent doesn't just answer direct queries. It offers **contextual awareness**:

```
User: "I want to build a news scraper."
L-gent: "Found 3 existing scrapers. Also, I noticed you usually use
        the 'Executive Summary' contract with scrapers—should I fetch
        the Summarizer_v4 agent to pipe the output into?"
```

This is the difference between a search engine and a **knowledgeable colleague**. L-gent learns patterns, suggests compositions, and surfaces connections humans might miss.

## Core Concepts

### The Living Catalog

L-gent organizes knowledge into **three layers**:

#### Layer 1: Registry (What Exists?)

Tracks the existence and metadata of every ecosystem artifact:

| Entity Type | Examples | Metadata |
|-------------|----------|----------|
| **Agents** | `summarizer_v1`, `scraper_v2` | Type signature, description, author |
| **Contracts** | `json_output`, `text_stream` | Invariants, composition rules |
| **Memories** | `research_session_2025_12_08` | Session context, creator |
| **Specs** | `spec/f-gents/forge.md` | Version, dependencies |

#### Layer 2: Lineage (Where Did It Come From?)

Tracks the **genetic history** of artifacts:

- "This agent is a fork of `BaseScraper`"
- "This agent was forged by F-gent using `prompt_template_b`"
- "This contract was deprecated because it failed `safety_check_9`"

Lineage enables **blame attribution** and **evolution tracking**.

#### Layer 3: Lattice (How Does It Fit?)

Tracks **compatibility relationships**:

- "Agent A *requires* Interface X"
- "Agent B *provides* Interface X"
- "Contract C is a *subtype* of Contract D"

The lattice enables **mathematical composition verification**: L-gent can prove which agents can talk to each other before they even try.

### The Three-Brain Architecture

L-gent combines three retrieval technologies:

```
┌─────────────────────────────────────────────────────────────┐
│                    L-gent: Three Brains                     │
├─────────────────┬──────────────────┬───────────────────────┤
│   Keyword       │   Semantic       │   Graph               │
│   (BM25)        │   (Embeddings)   │   (Traversal)         │
├─────────────────┼──────────────────┼───────────────────────┤
│ Exact matches   │ Intent matching  │ Logical reasoning     │
│ "Find agent_007"│ "Help with math" │ "Implements Contract" │
│ Fast, precise   │ Fuzzy, semantic  │ Relational, complete  │
└─────────────────┴──────────────────┴───────────────────────┘
```

**Hybrid search** combines all three: "Find agents that *semantically* relate to 'data processing' AND *logically* implement `StreamContract` AND *exactly* match version `2.x`."

### The Synaptic Network

L-gent maintains a **knowledge graph** where:

- **Nodes** are artifacts (agents, contracts, memories, specs)
- **Edges** are relationships (implements, requires, successor_to, compatible_with)
- **Weights** are relevance scores (usage frequency, recency, success rate)

This graph is the **ecosystem's nervous system**—enabling rapid discovery and automatic composition planning.

## Interaction Patterns

### A. Discovery Query (For Humans & C-gents)

*"Find me an agent that..."*

```python
# Natural language search backed by vector embeddings + graph logic
results = await l_gent.find(
    intent="Analyze financial sentiment from PDF files",
    constraints=["must run locally", "latency < 2s"],
    limit=3
)

# Returns:
# 1. FinancialAnalyzer_v2 (Score: 0.98) - Perfect match
# 2. GeneralPDFParser (Score: 0.85) - Needs composition with sentiment
# 3. SentimentNode (Score: 0.70) - Text only, needs PDF converter

# L-gent also suggests composition:
# "Consider: PDFParser >> FinancialAnalyzer for full pipeline"
```

### B. Dependency Resolution (For Runtime)

*"I have a hole in this pipeline. Fill it."*

This is where L-gent shines. You don't specify *which* agent—you specify the *shape*:

```python
# In a C-gent workflow
pipeline = (
    Source("market_data")
    >> l_gent.resolve(input_type=JSON, output_type=SentimentScore)
    >> Destination("database")
)

# L-gent dynamically injects the best-performing, currently-available
# agent that matches that type signature
```

**The morphism**: `TypeRequirement → Agent`

This enables **late binding**—the pipeline declares what it needs, L-gent provides the best match at runtime.

### C. Registration (For F-gent)

*"I just created something. Catalog it."*

When F-gent forges an artifact, it registers with L-gent:

```python
await l_gent.register(
    artifact=WeatherReporter_v4,
    metadata={
        "description": "Fetches weather and formats for SMS",
        "author": "F-gent-01",
        "contracts": ["text_output"],
        "requires": ["api_weather_service_key"],
        "successor_to": "WeatherReporter_v3"
    }
)
```

L-gent:
1. Generates semantic embedding for description
2. Validates contract compatibility (lattice consistency)
3. Updates lineage graph (successor_to relationship)
4. Indexes for discovery

### D. Notification (The Push)

L-gent watches the ecosystem. When things change:

```
Alert: `BaseNetworkAgent` has been updated to v2.0.
Your agent `StockTicker` is using v1.5.
Would you like to Re-Forge with F-gent?
```

**The pattern**: Subscribe to lineage changes, notify affected artifacts.

## Relationship to Bootstrap Agents

L-gents are **derivable** from bootstrap primitives:

| L-gent Capability | Bootstrap Agent | How |
|-------------------|-----------------|-----|
| Semantic search | **Ground** | Embeddings grounded in semantic space |
| Compatibility check | **Judge** | Lattice is type judgment formalized |
| Lineage tracking | **Ground** + **Fix** | Ground stores history, Fix derives ancestry |
| Pattern matching | **Compose** | Query composition builds complex searches |
| Contradiction detection | **Contradict** | Finds incompatible artifacts |

L-gents add no new irreducibles—they orchestrate bootstrap agents for knowledge management.

## Relationship to Other Genera

### F-gents (Forge)

**L-gent is F-gent's librarian**:
- F-gent queries L-gent before forging (prevent duplication)
- F-gent registers with L-gent after forging (enable discovery)
- L-gent tracks F-gent's lineage (which artifacts came from which intents)

```python
# Before forging
existing = await l_gent.find(intent=user_request, threshold=0.9)
if existing:
    return "Similar artifact exists: {existing}. Reuse or differentiate?"

# After forging
await l_gent.register(artifact, metadata={"forged_by": "F-gent", ...})
```

### D-gents (Data)

**L-gent uses D-gents for persistence**:
- **PersistentAgent**: Store the catalog itself
- **VectorAgent**: Semantic embedding index
- **GraphAgent**: Knowledge graph of relationships

```python
class Librarian:
    def __init__(self):
        self.registry = PersistentAgent[Catalog]("library.json")
        self.vectors = VectorAgent[Embedding](dimension=768)
        self.graph = GraphAgent[Node, Edge]()
```

L-gent is a **higher-order D-gent consumer**—it orchestrates multiple D-gent types into a unified knowledge service.

### E-gents (Evolution)

**L-gent tracks evolutionary lineage**:
- When E-gent evolves an artifact, L-gent records the transition
- L-gent can query "what improvements worked for similar code?"
- Success patterns are indexed for future evolution guidance

```python
# E-gent improvement cycle
improved = await evolution_agent.invoke(original)

# L-gent records lineage
await l_gent.record_evolution(
    parent=original.id,
    child=improved.id,
    improvement_type="complexity_reduction",
    success=True
)
```

### C-gents (Category Theory)

**L-gent enables compositional planning**:
- The lattice IS a category (artifacts as objects, relationships as morphisms)
- L-gent can compute composition paths: "How do I get from type A to type D?"
- Functor laws validate that discovered compositions preserve structure

```python
# Find composition path
path = await l_gent.find_path(
    source_type=RawHTML,
    target_type=SentimentScore
)
# Returns: HTMLParser >> TextExtractor >> SentimentAnalyzer
```

### H-gents (Hegelian Dialectic)

**L-gent surfaces tensions**:
- Contradictory artifacts are flagged (same contract, incompatible behavior)
- Dialectic history is indexed for pattern analysis
- Synthesis lineage tracked (which tensions led to which resolutions)

```python
# Query for productive tensions
tensions = await l_gent.find_tensions(
    domain="authentication",
    resolution_status="unresolved"
)
# Returns: [{thesis: OAuth_v1, antithesis: JWT_v2, context: "session management"}]
```

### J-gents (Just-in-Time)

**L-gent grounds J-gent decisions**:
- J-gent queries L-gent for runtime agent selection
- L-gent provides context for JIT compilation (what exists, what's compatible)
- Entropy budgets informed by artifact complexity metrics

```python
# J-gent runtime decision
async def jit_select(intent: str) -> Agent:
    candidates = await l_gent.find(intent=intent, runtime_only=True)
    return candidates[0] if candidates else await f_gent.forge(intent)
```

### K-gent (Kent Simulacra)

**L-gent is K-gent's memory index**:
- K-gent preferences become searchable patterns
- Past decisions indexed for consistency queries
- "What did I decide about X before?" → L-gent search

### T-gents (Testing)

**L-gent enables test discovery**:
- Find tests for a given artifact
- Track test coverage across ecosystem
- Query: "What tests cover this contract?"

```python
tests = await l_gent.find(
    related_to=MyAgent,
    entity_type="test",
    relationship="covers"
)
```

### B-gents (Bio/Scientific)

**L-gent is Robin's research assistant**:
- Index hypotheses and their outcomes
- Enable semantic search over research history
- Track which hypotheses were validated/refuted

## The Catalog Schema

L-gent's persistent state:

```python
@dataclass
class CatalogEntry:
    """A single entry in L-gent's registry."""
    id: str                          # Unique identifier
    entity_type: EntityType          # AGENT, CONTRACT, MEMORY, SPEC, TEST
    name: str                        # Human-readable name
    description: str                 # Natural language description
    embedding: list[float]           # Semantic vector (768-dim)

    # Structural metadata
    version: str                     # Semantic version
    author: str                      # Creator (F-gent, human, etc.)
    created_at: datetime
    updated_at: datetime

    # Type information (for compatibility)
    input_type: str | None           # For agents: input type signature
    output_type: str | None          # For agents: output type signature
    contracts: list[str]             # Contracts implemented/required

    # Graph relationships
    relationships: dict[str, list[str]]  # {rel_type: [target_ids]}
    # Common relationships:
    # - implements: contracts this artifact satisfies
    # - requires: contracts this artifact needs
    # - successor_to: previous version(s)
    # - forked_from: parent artifact
    # - depends_on: runtime dependencies
    # - compatible_with: tested composition partners

    # Health metrics
    usage_count: int                 # Times invoked
    success_rate: float              # Invocation success percentage
    last_used: datetime | None
    deprecated: bool
    deprecation_reason: str | None

@dataclass
class Catalog:
    """L-gent's complete knowledge state."""
    entries: dict[str, CatalogEntry]
    version: str
    last_updated: datetime
```

## Success Criteria

An L-gent is well-designed if:

- ✓ **Discoverable**: Any artifact can be found via semantic, keyword, or relational query
- ✓ **Accurate**: Search results are relevant (high precision and recall)
- ✓ **Connected**: The graph captures meaningful relationships between artifacts
- ✓ **Current**: Lineage reflects actual evolution history
- ✓ **Composable**: L-gent itself composes with other agents (not a monolith)
- ✓ **Fast**: Query latency < 100ms for interactive use
- ✓ **Serendipitous**: Surfaces useful connections humans wouldn't think to query

## Anti-Patterns

L-gents must **never**:

1. ❌ Return stale results (must reflect current ecosystem state)
2. ❌ Hide artifacts (everything registered is discoverable)
3. ❌ Lose lineage (ancestry is immutable history)
4. ❌ Break lattice consistency (type relationships must be valid)
5. ❌ Become a bottleneck (caching, distribution for scale)
6. ❌ Store artifacts themselves (L-gent indexes, D-gent stores)
7. ❌ Replace F-gent (L-gent finds, F-gent forges)

## Specifications

| Document | Description |
|----------|-------------|
| [catalog.md](catalog.md) | Registry, indexing, and the three-layer architecture |
| [query.md](query.md) | Search patterns, resolution, and the three-brain approach |
| [lineage.md](lineage.md) | Provenance tracking, ancestry, and evolution history |
| [lattice.md](lattice.md) | Type relationships, compatibility, and compositional planning |

## Design Principles Alignment

### Tasteful
L-gent prevents duplication by surfacing existing artifacts before new creation.

### Curated
The catalog itself is curated—deprecated artifacts are flagged, unused ones surfaced for review.

### Ethical
Provenance is transparent—you can always see where an artifact came from and who created it.

### Joy-Inducing
**Serendipity is built in.** L-gent doesn't just answer queries; it suggests connections, enabling delightful discovery.

### Composable
L-gent IS the enabler of composition—it's how agents find each other to compose.

### Heterarchical
L-gent doesn't own artifacts—it indexes them. Any agent can register, any agent can query.

### Generative
The catalog is compressed knowledge. From entries, the ecosystem structure can be regenerated.

## Example: Building a News Pipeline

**User Intent**: "I need to process news articles and summarize them."

**L-gent Interaction**:

```python
# 1. Discovery
results = await l_gent.find(
    intent="process news articles and summarize",
    constraints=["returns text", "input can be URL or HTML"]
)

# L-gent returns:
# - NewsParser_v2: URL → Article (Score: 0.92)
# - HTMLCleaner_v1: HTML → CleanText (Score: 0.78)
# - Summarizer_v4: Text → Summary (Score: 0.95)

# 2. Composition suggestion
suggestion = await l_gent.suggest_pipeline(
    input_type="URL",
    output_type="Summary"
)
# Returns: NewsParser_v2 >> Summarizer_v4

# 3. Compatibility verification
compatible = await l_gent.verify_composition(
    [NewsParser_v2, Summarizer_v4]
)
# Returns: True (NewsParser output type matches Summarizer input type)

# 4. User builds pipeline
pipeline = NewsParser_v2 >> Summarizer_v4

# 5. L-gent records the composition
await l_gent.record_usage(
    artifacts=[NewsParser_v2.id, Summarizer_v4.id],
    composition="sequential",
    context="news_summarization"
)
```

## Vision

L-gent transforms the ecosystem from a **"Box of Parts"** into a **"Supply Chain"**:

- **For the User**: A search engine that understands code and intent
- **For F-gent**: A publisher that catalogs new creations and prevents duplication
- **For C-gent**: A compatibility oracle that validates compositions
- **For E-gent**: A memory of what improvements worked where
- **For the Ecosystem**: The connective tissue ensuring that as the system grows, it becomes *smarter*, not more chaotic

The ultimate test: Can someone new to the ecosystem find what they need? Can they discover compositions they didn't know to ask for? Can they trace the history of any artifact?

L-gent makes the answer "yes" to all three.

---

*"A library is not a warehouse of books, but a living organism where knowledge finds those who need it."*

---

## See Also

- [catalog.md](catalog.md) - Registry and indexing specification
- [query.md](query.md) - Search and resolution patterns
- [lineage.md](lineage.md) - Provenance and ancestry tracking
- [lattice.md](lattice.md) - Type compatibility and composition planning
- [../f-gents/](../f-gents/) - Artifact creation (L-gent's primary source)
- [../d-gents/](../d-gents/) - Persistence infrastructure (L-gent's storage backend)
- [../c-gents/](../c-gents/) - Composition foundations (L-gent enables C-gent decisions)
- [../bootstrap.md](../bootstrap.md) - Derivation from irreducibles
