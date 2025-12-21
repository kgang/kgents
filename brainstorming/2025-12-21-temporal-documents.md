# Temporal Documents: Time as a First-Class Dimension

> *"A document is not a snapshot. It's a trajectory through possibility space."*

---

## The Vision

Documents exist in **time**, not just space. You can view any document at any point in its history, compare versions semantically (not just textually), forecast its future state, and see the rhythm of its evolution.

```markdown
## Project Status

<!-- time.witness: This section has been edited 47 times across 12 sessions -->
<!-- Velocity: 3.2 edits/day | Trend: accelerating -->

Current: Phase 4 complete (2025-12-21)

### Timeline View [Toggle]
┌─────────────────────────────────────────────────────────────────┐
│ Dec 10        Dec 15        Dec 18        Dec 21                │
│    │             │             │             │                  │
│    ▼             ▼             ▼             ▼                  │
│ [Phase 1]    [Phase 2]    [Phase 3]    [Phase 4]               │
│  ████░░░░     ████████░    ████████████  ████████████████      │
│                                                                 │
│ 📝 3 edits    📝 12 edits   📝 8 edits    📝 24 edits          │
│ 👤 kent       👤 kent       👤 claude     👤 kent, claude      │
└─────────────────────────────────────────────────────────────────┘

### Forecast [Based on velocity]
- Phase 5 estimated: 2025-12-24 (±2 days)
- Confidence: 0.7 (based on 4 prior phases)

[View at Dec 15] [Compare to yesterday] [Show semantic diff]
```

---

## Synergies with Recent Work

### 1. Witness Service (Walk & Mark)

**Location**: `services/witness/`, `spec/agents/witness.md`

Witness already has:
- **Mark**: Atomic timestamped action (origin, payload, status)
- **Walk**: Session trace anchored to Forest plans
- **time.witness**: AGENTESE context for temporal queries

**Synergy**: Document edits are Marks. Document history is a Walk. `time.witness` becomes the query interface.

```python
# Every document edit creates a Mark
@node("time.document.edit")
async def record_edit(document: Path, edit: DocumentEdit) -> Mark:
    return Mark.create(
        origin="time.document.edit",
        payload={
            "document": str(document),
            "before_hash": edit.before_hash,
            "after_hash": edit.after_hash,
            "delta_lines": edit.delta_lines,
            "section": edit.affected_section,
        },
    )

# Document history is queryable as a Walk
@node("time.document.history")
async def get_history(document: Path, since: datetime | None = None) -> Walk:
    marks = await Mark.query(
        origin="time.document.edit",
        filter={"document": str(document)},
        since=since,
    )
    return Walk.from_marks(marks, plan_ref=f"document:{document}")
```

### 2. time.* AGENTESE Context

**Location**: `protocols/agentese/contexts/time.py`

The `time.*` context already handles:
- **time.walk**: Session traces
- **time.forecast**: Predictions (placeholder)
- **time.witness**: Crystallization events

**Synergy**: Extend `time.*` for document-specific temporal queries.

```python
# New time.document.* paths
await logos.invoke("time.document.at", umwelt,
    document="CLAUDE.md",
    timestamp="2025-12-15T12:00:00Z",
)  # Returns document as it was at that time

await logos.invoke("time.document.diff", umwelt,
    document="CLAUDE.md",
    from_time="2025-12-15",
    to_time="2025-12-21",
    semantic=True,  # Semantic diff, not line-by-line
)

await logos.invoke("time.document.velocity", umwelt,
    document="CLAUDE.md",
    window="7d",
)  # Returns edit frequency, contributor count, trend
```

### 3. Git Integration

**Location**: Everywhere (kgents is git-native)

Git already provides:
- Full history of every file
- Blame for line-by-line attribution
- Diff between any two commits

**Synergy**: Git is the storage layer. Witness Marks reference commits. Semantic diff layers on top.

```python
# Git-backed temporal queries
async def document_at(document: Path, timestamp: datetime) -> str:
    """Get document content at a specific time."""
    commit = await git_commit_at(timestamp)
    return await git_show(commit, document)

async def semantic_diff(document: Path, from_time: datetime, to_time: datetime) -> SemanticDiff:
    """Semantic diff: what changed in meaning, not just lines."""
    old_content = await document_at(document, from_time)
    new_content = await document_at(document, to_time)

    old_tokens = parse_markdown(old_content).tokens
    new_tokens = parse_markdown(new_content).tokens

    return SemanticDiff(
        added_tokens=[t for t in new_tokens if t not in old_tokens],
        removed_tokens=[t for t in old_tokens if t not in new_tokens],
        changed_sections=detect_section_changes(old_content, new_content),
    )
```

### 4. Interactive Text Tokens

**Location**: `services/interactive_text/`

Interactive Text provides:
- Token-level parsing
- Affordances per token

**Synergy**: Temporal affordances on any token.

```python
# Every token can show its history
Affordance(
    name="view_history",
    action=AffordanceAction.HOVER,  # Long hover
    handler="time.token.history",
    description="View this token's evolution",
),
Affordance(
    name="time_travel",
    action=AffordanceAction.RIGHT_CLICK,
    handler="time.document.at",
    description="View document when this was added",
),
```

### 5. Brain Temporal Indexing

**Location**: `services/brain/`, `spec/agents/brain.md`

Brain already has:
- Vector embeddings for semantic search
- Memory crystals with timestamps

**Synergy**: Brain indexes document versions. "Find when we first discussed caching" becomes a temporal query.

```python
# Temporal semantic search
await logos.invoke("self.brain.surface", umwelt,
    query="when did we add PostgreSQL?",
    temporal=True,  # Search across time, not just current
)
# Returns: "First mentioned in commit abc123 on 2025-12-10"
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TEMPORAL DOCUMENT LAYER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Git Repository (Storage Layer)                                      │    │
│  │  - Full history of all documents                                     │    │
│  │  - Commits as immutable snapshots                                    │    │
│  │  - Blame for attribution                                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Witness Layer (Mark/Walk)                                           │    │
│  │  - Every edit creates a Mark                                         │    │
│  │  - Document history as Walk                                          │    │
│  │  - Session context preserved                                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Semantic Layer (Interactive Text + Brain)                           │    │
│  │  - Parse each version into tokens                                    │    │
│  │  - Compute semantic diff (not line diff)                            │    │
│  │  - Index versions for temporal search                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Query Layer (time.document.* AGENTESE)                              │    │
│  │  - time.document.at(timestamp)                                       │    │
│  │  - time.document.diff(from, to, semantic=True)                      │    │
│  │  - time.document.velocity(window)                                    │    │
│  │  - time.document.forecast(horizon)                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Projection Layer (Servo + Interactive Text)                         │    │
│  │  - Timeline visualization                                            │    │
│  │  - Version comparison view                                           │    │
│  │  - Temporal token affordances                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Mark-per-Edit
- Hook into file edit events (already have FILE_EDITED synergy event)
- Create Mark for each edit with before/after hash
- Store in Witness system

### Phase 2: time.document.* Nodes
- `time.document.at`: Retrieve content at timestamp
- `time.document.history`: List of edits (Marks)
- `time.document.diff`: Compare two versions

### Phase 3: Semantic Diff
- Parse both versions into tokens
- Compare token sets (not line-by-line)
- Identify section-level changes

### Phase 4: Timeline Visualization
- React component for timeline view
- Scrubber to navigate through time
- Thumbnail previews of each version

### Phase 5: Velocity & Forecasting
- Compute edit frequency, trend
- Predict future completion dates
- Confidence intervals based on history

---

## Open Questions

1. **Granularity**: Every keystroke? Every save? Every commit?

2. **Storage**: Store full snapshots or diffs? (Git handles this, but query perf?)

3. **Semantic Diff Algorithm**: How to detect "same meaning, different words"?

4. **Forecasting Model**: Linear extrapolation? ML? Based on what features?

5. **Performance**: Parsing every historical version is expensive. Cache strategy?

6. **Branch Handling**: What happens with git branches? Multiple timelines?

---

## Research Cues

### Event Sourcing
- **CQRS/Event Sourcing**: State as sequence of events
- **Datomic**: Immutable database with time as dimension
- **EventStoreDB**: Purpose-built event sourcing database
- 🔍 *Search: "event sourcing document management systems"*

### Temporal Databases
- **Bi-temporal modeling**: Valid time vs transaction time
- **SQL:2011 temporal features**: SYSTEM_TIME, PERIOD FOR
- **TerminusDB**: Git for data
- 🔍 *Search: "temporal databases git-like versioning"*

### Semantic Diff
- **SemanticDiff**: Tree-based diff for code
- **diffsitter**: Syntax-aware diff
- **Prose diff**: Word-level diff for text
- 🔍 *Search: "semantic diff markdown documents"*

### Time Series Forecasting
- **Prophet**: Facebook's forecasting library
- **ARIMA**: Classical time series
- **Velocity tracking in Agile**: Burndown charts, velocity estimation
- 🔍 *Search: "document completion time estimation"*

### Version Control Research
- **Darcs**: Patch theory (commutative patches)
- **Pijul**: Sound patch theory implementation
- **Operational Transformation**: Google Docs approach
- 🔍 *Search: "version control theory beyond git"*

---

## Maximum Value Opportunities

### 1. "When Did We Decide This?"
Instant answer to "when was X added and why?" — with full context.

### 2. Onboarding Time Travel
New team member can watch spec evolve from v1 to current. Understands the "why" behind decisions.

### 3. Regression Detection
"This section hasn't been updated since implementation changed." Automatic staleness detection.

### 4. Predictive Planning
"Based on Phase 1-4 velocity, Phase 5 will complete by Dec 24." Confidence intervals, not guesses.

### 5. Blame Without Shame
See who contributed what, when. Attribution for credit, not blame. Celebrate contributions.

### 6. Semantic Changelog
Auto-generated: "In the last week: Added 3 requirements, completed 5 tasks, removed 2 deprecated sections."

---

## Voice Anchors

> *"The noun is a lie. There is only the rate of change."* — Documents are trajectories, not states.

> *"Heterarchical"* — Time is one dimension among many. Don't privilege the present.

> *"Generative"* — History should generate insights, not just be archived.

---

## Connection to Constitution

From Principle 6 (Heterarchical):
> "Temporal composition: Agents compose across time, not just sequential pipelines."

Temporal documents ARE composition across time. Today's agent builds on yesterday's agent's work, mediated by the document.

From Principle 7 (Generative):
> "Regenerability over documentation: A generative spec beats extensive docs."

Temporal view GENERATES understanding. Watch the spec evolve → understand the design rationale.

---

*Created: 2025-12-21 | Building on: Witness, time.*, Git, Brain, Interactive Text*
*Next: Research event sourcing patterns, prototype time.document.at node*
