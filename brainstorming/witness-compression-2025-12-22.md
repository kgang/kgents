# Witness Compression: From Marks to Meaning

> *"The proof IS the decision. The compression IS the wisdom."*

**Date**: 2025-12-22
**Status**: Brainstorm → Ready for Spec
**Catalyst**: Agent-Friendliness Audit revealed marks accumulate but don't crystallize

---

## The Problem

Marks accumulate. Today alone: 20+ marks. This week: 100+. This month: 500+.

Without compression:
- Marks become noise (the museum anti-pattern)
- Context windows overflow with raw marks
- Patterns hide in volume
- Agents can't "get up to speed" on what happened

**The garden thrives through pruning.** Marks need pruning too.

---

## The Vision: Witness Compression

### Core Insight

Marks are **observations**. Compression produces **insights**.

```
Observations (many)  →  LLM Compression  →  Insights (few)
     marks                                    crystals
```

A crystal is a compressed mark—denser, more meaningful, derived from many.

### The Compression Hierarchy

```
Level 0: Raw Marks
  └── "Started audit" "Found issue" "Fixed issue" "Found another" "Fixed" "Done"

Level 1: Session Crystals (hourly/session-end)
  └── "Completed security audit: 3 issues found and fixed"

Level 2: Day Crystals (daily)
  └── "2025-12-22: Extinction event cleanup + agent-friendliness audit"

Level 3: Week Crystals (weekly)
  └── "Week of 12/16: Major cleanup, 52K lines removed, witness system enhanced"

Level 4: Epoch Crystals (milestone-triggered)
  └── "Post-Extinction Epoch: kgents entered maintenance mode with 5 living jewels"
```

Each level compresses the level below. Crystals reference their source marks.

---

## Production-Grade Design

### 1. Crystal Data Model

```python
@dataclass
class WitnessCrystal:
    """A compressed insight derived from marks."""

    crystal_id: str                    # "crystal-abc123"
    level: CrystalLevel               # session | day | week | epoch
    content: str                       # The compressed insight
    source_marks: list[str]           # mark_ids that were compressed
    source_crystals: list[str]        # crystal_ids (for higher levels)
    timestamp: datetime
    time_range: tuple[datetime, datetime]  # What period this covers

    # Compression metadata
    compression_ratio: float          # len(sources) / 1
    confidence: float                 # LLM's confidence in the compression
    principles_extracted: list[str]   # Principles that emerged

    # Semantic embedding for search
    embedding_id: str | None          # D-gent datum for semantic search
```

### 2. Compression Triggers

| Trigger | Level | When |
|---------|-------|------|
| `kg witness compress` | Session | Manual invocation |
| Session end | Session | `/handoff` or session timeout |
| Midnight | Day | Cron or daemon scheduled |
| Sunday midnight | Week | Cron or daemon scheduled |
| Milestone tag | Epoch | When mark tagged `#milestone` |

### 3. CLI Interface

```bash
# Manual compression
kg witness compress                    # Compress uncompressed marks → session crystal
kg witness compress --level day        # Compress today's session crystals → day crystal
kg witness compress --since "2025-12-21" --level epoch "Post-Extinction"

# Query crystals
kg witness crystals                    # Show recent crystals
kg witness crystals --level week       # Show week crystals
kg witness crystals --json             # Machine-readable

# Expand crystal (see sources)
kg witness expand crystal-abc123       # Show marks that formed this crystal

# Crystal for context (agent use)
kg witness context                     # Get best crystals for current context
kg witness context --budget 1000       # Fit within token budget
```

### 4. The Compression Prompt

```python
COMPRESSION_PROMPT = """
You are compressing witness marks into a crystal—a dense insight.

MARKS TO COMPRESS:
{marks}

COMPRESSION RULES:
1. Capture WHAT happened (actions)
2. Capture WHY it matters (significance)
3. Capture WHAT CHANGED (before → after)
4. Extract any PRINCIPLES that emerged
5. Be concise but complete (1-3 sentences)

OUTPUT FORMAT:
{{
  "content": "The compressed insight",
  "significance": "Why this matters",
  "principles": ["principle1", "principle2"],
  "confidence": 0.85
}}

Compress now:
"""
```

### 5. Context Budget Management

Agents need context but have limited budgets. Crystals solve this:

```python
async def get_context_for_budget(
    budget_tokens: int = 2000,
    recency_weight: float = 0.7,
    relevance_weight: float = 0.3,
) -> list[WitnessCrystal]:
    """
    Get the best crystals that fit within token budget.

    Strategy:
    1. Start with highest-level crystals (most compressed)
    2. Add lower-level crystals if budget allows
    3. Prioritize by recency × relevance score
    4. Return ordered list fitting within budget
    """
```

This gives agents "executive summaries" instead of raw mark dumps.

---

## Compatible Enhancement: Mark Lineage

### The Insight

Marks don't exist in isolation. They form **causal chains**:

```
mark-aaa: "Started extinction audit"
  └── mark-bbb: "Found Gestalt is dead code" (caused by aaa)
  └── mark-ccc: "Found Park is dead code" (caused by aaa)
      └── mark-ddd: "Removed Park" (caused by ccc)
  └── mark-eee: "Extinction complete" (caused by aaa)
```

Lineage enables **structural compression**—the LLM can see the tree, not just a list.

### Implementation

```python
@dataclass
class MarkResult:
    # ... existing fields ...
    parent_id: str | None = None      # Causal parent
    children: list[str] = field(default_factory=list)  # Filled on query
```

```bash
# Create with lineage
km "Found issue" --parent mark-aaa --json

# Query lineage
kg witness tree mark-aaa              # Show mark family tree
kg witness tree mark-aaa --json       # Machine-readable tree

# Compress with lineage awareness
kg witness compress --tree mark-aaa   # Compress entire tree into crystal
```

### Why This Matters for Compression

Tree-aware compression produces better crystals:

```
WITHOUT LINEAGE:
"Started audit. Found issue. Fixed issue. Found another. Fixed. Done."

WITH LINEAGE:
"Extinction audit (mark-aaa) discovered 5 dead jewels (Gestalt, Park,
Emergence, Coalition, Drills) and removed them, resulting in 52K lines
deleted and a green test suite."
```

The tree IS the narrative structure. Compression preserves it.

---

## Compatible Enhancement: Crystal Streams

### The Insight

If marks can stream (SSE), crystals should too. Real-time compression.

```bash
kg witness stream --crystals          # Stream crystals as they form
kg witness stream --level session     # Stream session crystals only
```

### Use Case: Agent Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  🔮 Witness Stream                                          │
├─────────────────────────────────────────────────────────────┤
│  15:27  [crystal] Agent-friendliness audit complete         │
│  15:05  [crystal] Extinction event: 52K lines removed       │
│  14:30  [crystal] Context Perception Phase 3 shipped        │
│  ...                                                        │
└─────────────────────────────────────────────────────────────┘
```

Agents can subscribe to crystal streams for real-time situational awareness.

### Implementation

```python
async def crystal_stream(
    level: CrystalLevel | None = None,
    poll_interval: float = 30.0,
) -> AsyncGenerator[WitnessCrystal, None]:
    """
    Stream crystals as they are created.

    Yields new crystals, optionally filtered by level.
    Useful for dashboards and agent coordination.
    """
```

---

## Integration with Existing Systems

### 1. HYDRATE.md Integration

Crystals could auto-update HYDRATE.md's "Crown Jewels" section:

```python
async def update_hydrate_from_crystals():
    """
    Use recent epoch crystals to update HYDRATE.md status.

    Example: Extinction crystal → Update Crown Jewels table
    """
```

### 2. NOW.md Integration

Day crystals could auto-populate NOW.md:

```python
async def update_now_from_crystals():
    """
    Use today's crystals to update NOW.md "What Just Happened" section.
    """
```

### 3. Session Handoff Integration

`/handoff` could auto-compress before generating handoff:

```python
async def handoff_with_compression():
    """
    1. Compress uncompressed marks → session crystal
    2. Include crystal in handoff context
    3. Next Claude gets crystal, not raw marks
    """
```

### 4. Brain Integration

Crystals could be stored in Brain as teaching crystals:

```python
async def crystallize_to_brain(crystal: WitnessCrystal):
    """
    Promote a witness crystal to a brain teaching crystal.

    Witness observes → Brain remembers.
    """
```

---

## The Transformative Insight

**Marks are write-heavy. Crystals are read-heavy.**

The current witness system optimizes for writing observations. Compression optimizes for reading insights.

```
WRITE PATH (current):
  km "action" → mark → storage → done

READ PATH (with compression):
  kg witness context → crystals → best context for budget → agent

COMPRESSION PATH (new):
  marks → LLM → crystal → storage
  crystals → LLM → higher crystal → storage
```

This transforms witness from a **log** into a **memory system**.

---

## Implementation Phases

### Phase 1: Core Compression (MVP)
- [ ] `WitnessCrystal` model
- [ ] `kg witness compress` command
- [ ] Session-level compression
- [ ] `kg witness crystals` query

### Phase 2: Automatic Triggers
- [ ] Session-end compression hook
- [ ] Daily compression daemon job
- [ ] `/handoff` integration

### Phase 3: Lineage
- [ ] `--parent` flag for `km`
- [ ] `kg witness tree` command
- [ ] Tree-aware compression

### Phase 4: Context Budget
- [ ] `kg witness context --budget N`
- [ ] Token estimation for crystals
- [ ] Relevance scoring

### Phase 5: Streams & Integration
- [ ] Crystal SSE stream
- [ ] NOW.md auto-update
- [ ] Brain promotion

---

## Open Questions

1. **Compression frequency**: Too frequent = noise. Too rare = stale. What's the rhythm?

2. **Crystal editing**: Can you edit a crystal? Or are they immutable like marks?

3. **Compression reversibility**: Can you "unpack" a crystal back to marks? (Yes, via `source_marks`)

4. **Multi-agent compression**: If multiple agents are marking, how do we compress coherently?

5. **Compression quality**: How do we evaluate if a crystal is "good"? Human review? Self-critique?

---

## The One-Liner

> **Witness Compression transforms the witness system from a log into a memory—marks become crystals, observations become insights, and agents get context that fits.**

---

*"The garden thrives through pruning. Crystals are the pruned wisdom."*
