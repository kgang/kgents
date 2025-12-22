# Witness Crystallization

> *"The garden thrives through pruning. Marks become crystals. Crystals become wisdom."*

**Status:** Proposal
**Category:** `time.*`
**Heritage:** [Zep Temporal Knowledge Graph](https://blog.getzep.com/content/files/2025/01/ZEP__USING_KNOWLEDGE_GRAPHS_TO_POWER_LLM_AGENT_MEMORY_2025011700.pdf), [Hierarchical Summarization](https://pieces.app/blog/hierarchical-summarization)

---

## Purpose

Marks accumulate. Without crystallization, they become noise—the museum anti-pattern where everything is preserved but nothing is accessible. Crystallization transforms the Witness from a **log** into a **memory system**.

**The Problem:** 20 marks/day × 30 days = 600 marks/month. Context windows overflow. Patterns hide in volume. Agents can't "get up to speed."

**The Solution:** Hierarchical crystallization. Marks compress into crystals. Crystals compress into higher crystals. The compression IS the understanding.

---

## Core Insight

**Marks are observations. Crystals are insights.**

```
Observations (many)  →  Crystallization  →  Insights (few, dense)
     marks                                      crystals
```

A crystal is not a summary—it's a **semantic compression** that preserves causal structure while reducing volume. The raw marks remain accessible (immutability law), but crystals become the primary retrieval interface.

---

## The Unified Crystal

There is one crystal type. Not `ExperienceCrystal` vs `WitnessCrystal`. Just `Crystal`.

```python
@dataclass(frozen=True)
class Crystal:
    """
    The atomic unit of compressed witness memory.

    A Crystal exists at a level in the compression hierarchy:
    - Level 0: Direct crystallization from marks (session boundary)
    - Level 1: Compression of level-0 crystals (day boundary)
    - Level 2: Compression of level-1 crystals (week boundary)
    - Level 3: Compression of level-2 crystals (epoch/milestone)

    Higher levels are denser, broader, and more abstract.
    Lower levels are richer, narrower, and more concrete.
    """

    # Identity
    id: CrystalId                           # "crystal-abc123"
    level: int                              # 0, 1, 2, 3

    # Content
    insight: str                            # The compressed meaning
    significance: str                       # Why this matters
    principles: tuple[str, ...]             # Principles that emerged

    # Provenance (never broken)
    source_marks: tuple[MarkId, ...]        # Direct mark sources (level 0)
    source_crystals: tuple[CrystalId, ...]  # Crystal sources (level 1+)

    # Temporal bounds
    time_range: tuple[datetime, datetime]   # What period this covers
    crystallized_at: datetime               # When compression happened

    # Semantic handles
    topics: frozenset[str]                  # For retrieval
    mood: MoodVector                        # Affective signature

    # Metrics
    compression_ratio: float                # sources / 1
    confidence: float                       # Crystallizer's confidence
    token_estimate: int                     # For budget calculations
```

### The Level Hierarchy

| Level | Name | Boundary | Typical Sources | Compression Ratio |
|-------|------|----------|-----------------|-------------------|
| 0 | Session | Session end / manual | 5-50 marks | 10:1 - 50:1 |
| 1 | Day | Midnight / manual | 2-10 level-0 crystals | 5:1 - 20:1 |
| 2 | Week | Sunday / manual | 5-7 level-1 crystals | 5:1 - 10:1 |
| 3 | Epoch | Milestone tag | Variable level-2 crystals | Variable |

**Key Property:** Level N crystals reference level N-1 crystals (or marks for level 0). This maintains a clean DAG structure.

---

## Crystallization Operations

### The Crystallizer

```python
class Crystallizer:
    """
    Transforms marks/crystals into higher-level crystals.

    Not a fallback system. The right tool for the job:
    - LLM when semantic compression adds value
    - Algorithmic when structure suffices
    - Never a crutch in either direction
    """

    async def crystallize_marks(
        self,
        marks: list[Mark],
        session_id: str | None = None,
    ) -> Crystal:
        """
        Level 0: Marks → Session Crystal.

        Uses LLM to extract:
        - What happened (actions)
        - Why it matters (significance)
        - What changed (delta)
        - What emerged (principles)
        """

    async def crystallize_crystals(
        self,
        crystals: list[Crystal],
        level: int,
        label: str | None = None,
    ) -> Crystal:
        """
        Level N: Crystals → Higher Crystal.

        Compresses multiple crystals into one denser insight.
        Label is optional name for epoch crystals.
        """

    async def auto_crystallize(
        self,
        since: datetime | None = None,
        level: int = 0,
    ) -> list[Crystal]:
        """
        Automatic crystallization based on boundaries.

        Finds uncrystallized marks/crystals and compresses them.
        """
```

### Compression Prompt

The crystallization prompt is precise, not a template fallback:

```python
CRYSTALLIZATION_PROMPT = """
You are crystallizing witness marks into dense insight.

MARKS:
{marks_formatted}

CRYSTALLIZE by answering:
1. WHAT happened? (concrete actions, not abstractions)
2. WHY does it matter? (significance to the project/person)
3. WHAT changed? (before state → after state)
4. WHAT emerged? (principles, patterns, learnings)

OUTPUT (JSON):
{
  "insight": "1-3 sentences capturing the essence",
  "significance": "Why this matters going forward",
  "principles": ["principle1", "principle2"],
  "confidence": 0.0-1.0
}

Be concrete. Be dense. Preserve causality.
"""
```

### Crystallization Triggers

| Trigger | Level | When | Automation |
|---------|-------|------|------------|
| `kg witness crystallize` | 0 | Manual | N/A |
| Session end | 0 | `/handoff`, session timeout | Automatic |
| `kg witness crystallize --level day` | 1 | Manual | N/A |
| Midnight | 1 | Cron/daemon | Optional |
| `kg witness crystallize --level week` | 2 | Manual | N/A |
| Sunday midnight | 2 | Cron/daemon | Optional |
| Milestone marker | 3 | Mark tagged `#milestone` | Semi-auto |

---

## Mark Lineage Ergonomics

The existing `MarkLink` system IS lineage. It needs better ergonomics.

### Current State

```python
# Existing: Verbose, requires knowing link types
mark = Mark.from_thought(...).with_link(
    MarkLink(source=parent_id, target=mark.id, relation=LinkRelation.CAUSES)
)
```

### Ergonomic Enhancement

```bash
# CLI: Simple parent flag
km "Found Gestalt is dead code" --parent mark-aaa
km "Removed Gestalt" --parent mark-bbb

# Query: Tree view
kg witness tree mark-aaa
# Output:
# mark-aaa: "Started extinction audit"
#   ├── mark-bbb: "Found Gestalt is dead code" (CAUSES)
#   │   └── mark-ccc: "Removed Gestalt" (CAUSES)
#   └── mark-ddd: "Found Park is dead code" (CAUSES)
#       └── mark-eee: "Removed Park" (CAUSES)

# Tree-aware crystallization
kg witness crystallize --tree mark-aaa
# Compresses entire causal tree into one crystal
```

### Python API Enhancement

```python
# New: Fluent parent syntax
mark = await witness.mark(
    "Found Gestalt is dead code",
    parent="mark-aaa",  # Sugar for CAUSES link
)

# New: Tree query
tree = await witness.tree(root_id="mark-aaa")
for node in tree.walk():
    print(f"{'  ' * node.depth}{node.mark.id}: {node.mark.response.content}")

# New: Tree crystallization
crystal = await crystallizer.crystallize_tree(root_id="mark-aaa")
```

---

## Context Budget System

Agents need context but have limited budgets. Crystals solve this.

### The Budget Query

```python
async def get_context(
    budget_tokens: int = 2000,
    recency_weight: float = 0.7,
    relevance_query: str | None = None,
) -> list[Crystal]:
    """
    Get the best crystals that fit within token budget.

    Strategy:
    1. Start with highest-level crystals (most compressed)
    2. Score by recency × relevance
    3. Fill budget greedily by score
    4. Return ordered list

    This gives agents "executive summaries" instead of raw marks.
    """
```

### CLI Interface

```bash
# Get context for current budget
kg witness context                     # Default 2000 tokens
kg witness context --budget 1000       # Tighter budget
kg witness context --query "extinction" # Relevance-weighted

# Output (JSON for agents)
kg witness context --json
# [
#   {"id": "crystal-abc", "level": 2, "insight": "...", "tokens": 150},
#   {"id": "crystal-def", "level": 1, "insight": "...", "tokens": 200},
#   ...
# ]
```

### Agent Protocol

Subagents use context budget for situational awareness:

```python
# Subagent startup protocol
context = await witness.get_context(budget_tokens=1500)
for crystal in context:
    # Inject into prompt as grounding
    prompt += f"\n[Context] {crystal.insight}"
```

---

## Integration Points

### 1. Handoff Integration

`/handoff` automatically crystallizes before generating:

```python
async def handoff_with_crystallization():
    # 1. Crystallize uncrystallized marks
    crystal = await crystallizer.auto_crystallize(level=0)

    # 2. Include crystal in handoff context
    # Next Claude gets crystal, not raw marks

    # 3. Generate handoff document
    return await generate_handoff(recent_crystals=[crystal])
```

### 2. NOW.md Auto-Update

Day crystals can update NOW.md's "What Just Happened" section:

```python
async def update_now_from_crystals():
    """
    Use today's crystals to update NOW.md.

    Not automatic overwrite—proposes changes for review.
    """
    today_crystals = await get_crystals(level=1, since=today())
    proposed_update = format_for_now_md(today_crystals)
    return proposed_update  # Human reviews before commit
```

### 3. Brain Promotion

Significant crystals can be promoted to Brain teachings:

```python
async def promote_to_brain(crystal: Crystal):
    """
    Promote a witness crystal to a Brain teaching.

    Witness observes → Crystal compresses → Brain remembers.
    """
    teaching = Teaching(
        content=crystal.insight,
        principles=crystal.principles,
        source=f"witness:crystal:{crystal.id}",
    )
    await brain.capture(teaching)
```

### 4. Crystal Streaming

Real-time crystal stream for dashboards and coordination:

```python
async def crystal_stream(
    level: int | None = None,
) -> AsyncGenerator[Crystal, None]:
    """
    Stream crystals as they form.

    Agents can subscribe for real-time situational awareness.
    """
```

```bash
# CLI streaming
kg witness stream --crystals
# [15:27] [L0] Agent-friendliness audit complete
# [15:05] [L1] Day crystal: Extinction + audit
# ...
```

---

## Visual Projection

### CLI Dashboard

```
╔════════════════════════════════════════════════════════════════════╗
║  🔮 WITNESS CRYSTALLIZATION                              2025-12-22 ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌─ HIERARCHY ──────────────────────────────────────────────────┐   ║
║  │                                                               │   ║
║  │  L3 Epoch    ○─────────────────────────────────────────○     │   ║
║  │              │ "Post-Extinction: 5 jewels, focused"    │     │   ║
║  │              └─────────────────────────────────────────┘     │   ║
║  │                            │                                  │   ║
║  │  L2 Week     ┌─────────────┴─────────────┐                   │   ║
║  │              │  Week 51: Cleanup + Audit │                   │   ║
║  │              └───────────────────────────┘                   │   ║
║  │                            │                                  │   ║
║  │  L1 Day      ┌──────┬──────┼──────┬──────┐                   │   ║
║  │              │ 12/20│ 12/21│ 12/22│      │                   │   ║
║  │              └──────┴──────┴──────┴──────┘                   │   ║
║  │                                  │                            │   ║
║  │  L0 Session  ○ ○ ○ ● ←─ current session (47 marks)           │   ║
║  │                                                               │   ║
║  └───────────────────────────────────────────────────────────────┘   ║
║                                                                      ║
║  ┌─ RECENT CRYSTALS ────────────────────────────────────────────┐   ║
║  │  [L1] 12/22: Extinction complete, agent audit in progress    │   ║
║  │  [L0] Session: Context Perception shipped, Portal started    │   ║
║  └───────────────────────────────────────────────────────────────┘   ║
║                                                                      ║
║   [C]rystallize now  [T]ree view  [E]xpand crystal  [Q]uery         ║
╚════════════════════════════════════════════════════════════════════╝
```

### Web Component

```typescript
// services/witness/web/CrystalHierarchy.tsx
// Visualizes the compression hierarchy as an interactive tree
// Click to expand, see source marks/crystals
// Real-time updates via SSE subscription
```

---

## Laws

| # | Law | Description |
|---|-----|-------------|
| 1 | Mark Immutability | Marks are never deleted, even after crystallization |
| 2 | Provenance Chain | Every crystal references its sources (marks or crystals) |
| 3 | Level Consistency | Level N crystals only source from level N-1 (or marks for N=0) |
| 4 | Temporal Containment | Crystal time_range contains all source time_ranges |
| 5 | Compression Monotonicity | Higher levels are always denser (fewer, broader) |

---

## Anti-Patterns

- **Eager deletion**: Removing marks after crystallization (violates Law 1)
- **Level skipping**: Compressing marks directly to level 2 (violates Law 3)
- **Template crutch**: Using templates when LLM would produce better results
- **LLM crutch**: Using LLM when simple aggregation suffices
- **Unbounded accumulation**: Never crystallizing (the museum anti-pattern)
- **Over-crystallization**: Crystallizing every few marks (noise, not signal)

---

## AGENTESE Interface

```python
@node(
    path="time.witness.crystal",
    description="Hierarchical compression of witness marks into crystals",
    contracts={
        "manifest": Response(CrystalManifestResponse),
        "crystallize": Contract(CrystallizeRequest, Crystal),
        "query": Contract(CrystalQuery, list[Crystal]),
        "context": Contract(ContextRequest, list[Crystal]),
        "tree": Contract(TreeRequest, MarkTree),
        "expand": Contract(ExpandRequest, CrystalExpansion),
        "stream": Stream(Crystal),
    },
    effects=["reads:marks", "writes:crystals", "invokes:llm"],
)
```

---

## Migration from ExperienceCrystal

The existing `ExperienceCrystal` becomes a level-0 `Crystal`:

```python
# Existing ExperienceCrystal usage
crystal = ExperienceCrystal.from_thoughts(thoughts, session_id="abc")

# Migrates to
crystal = await crystallizer.crystallize_marks(marks, session_id="abc")
# Returns Crystal with level=0

# The MoodVector, TopologySnapshot, Narrative components
# are preserved but become optional enrichments on Crystal
```

**Backwards compatibility**: `ExperienceCrystal` remains as a type alias during migration.

---

## The Transformative Vision

Crystallization transforms the witness from a passive observer into an active memory system:

**Before**: Marks accumulate → Context overflows → Patterns lost → Agents start fresh

**After**: Marks crystallize → Context budgeted → Patterns preserved → Agents inherit wisdom

The hierarchy creates **temporal zoom**:
- Level 3: "What happened this quarter?" → One crystal
- Level 2: "What happened this week?" → One crystal
- Level 1: "What happened today?" → One crystal
- Level 0: "What happened this session?" → One crystal
- Raw: "What exactly happened?" → Source marks (always available)

This is not summarization. It's **semantic compression with provenance**. The wisdom accumulates. The garden thrives.

---

*"Marks are the observations. Crystals are the understanding. The hierarchy IS the memory."*

*Synthesized: 2025-12-22 | Inspired by: [Zep Memory Architecture](https://blog.getzep.com/), [Pieces Hierarchical Summarization](https://pieces.app/blog/hierarchical-summarization)*
