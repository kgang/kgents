# Unified Data Spine: The K-Block Convergence

> *"The proof IS the decision. The mark IS the witness. The K-Block IS the spine."*

**Status**: Canonical Specification
**Date**: 2025-12-25
**Principles**: Composable, Generative, Tasteful, Heterarchical
**Prerequisites**: `k-block.md`, `kblock-unification.md`, `zero-seed.md`, `witness-primitives.md`
**Derived From**: Analysis Operad (Four-Mode) + Zero Seed Derivation Framework

---

## Abstract

This specification unifies five previously independent data management systems into a single coherent architecture:

1. **K-Block** (transactional editing containers)
2. **Zero Seed** (epistemic holarchy with Galois loss)
3. **Witness** (marks, crystals, traces)
4. **Sovereign** (document upload and integration)
5. **Feed/Meta** (discovery and meta-cognition)

**The Core Insight**: All five systems operate on the same fundamental entity—the K-Block. The "Unified Data Spine" makes this explicit, eliminating redundant storage paths and enabling cross-system composition.

---

## Part I: The Convergence Theorem

### 1.1 The Isomorphism Extended

From `kblock-unification.md`:
```
KBlock ≅ Agent ≅ ZeroNode ≅ File ≅ Upload ≅ Crystal
```

**This spec extends to**:
```
KBlock ≅ Agent ≅ ZeroNode ≅ File ≅ Upload ≅ Crystal ≅ Mark(target)
```

Where `Mark(target)` indicates that every Mark references its target K-Block.

### 1.2 The Unified Kind Taxonomy (Finalized)

```python
class KBlockKind(Enum):
    """
    K-Block content taxonomy: Everything flows through the unified spine.
    """
    # Original kinds
    FILE = "file"              # Traditional filesystem content
    UPLOAD = "upload"          # User-uploaded content (sovereign)
    ZERO_NODE = "zero_node"    # Zero Seed node (L1-L7)
    AGENT_STATE = "agent_state"  # Serialized agent polynomial state

    # Crystal unification (NEW - from Kent's decision)
    CRYSTAL = "crystal"        # Crystallized memory (NOW STORED AS K-BLOCK)
    CRYSTAL_SESSION = "crystal_session"   # L0 session crystal
    CRYSTAL_DAY = "crystal_day"           # L1 day crystal
    CRYSTAL_WEEK = "crystal_week"         # L2 week crystal
    CRYSTAL_EPOCH = "crystal_epoch"       # L3 epoch crystal
```

### 1.3 Kind Properties (Extended)

| Kind | Is Sovereign | Is Structural | Requires Witnessing | Is Sealable | AGENTESE Context |
|------|--------------|---------------|---------------------|-------------|------------------|
| FILE | No | No | No | No | `world.*` |
| UPLOAD | Yes | No | Yes | No | `world.*` |
| ZERO_NODE | No | Yes | Yes | No | `void.*` / `concept.*` |
| AGENT_STATE | No | No | No | No | `self.*` |
| CRYSTAL | Yes | No | Yes | **Yes** | `time.*` |
| CRYSTAL_* | Yes | No | Yes | **Yes** | `time.*` |

**New Property: `is_sealable`**: Crystals can be sealed (made immutable) after creation. This replaces the `frozen=True` dataclass approach with K-Block isolation semantics.

---

## Part II: Crystal Unification

### 2.1 Crystal as K-Block

**Decision**: Crystals are K-Blocks with kind=CRYSTAL_*.

**Implementation**:

```python
@dataclass
class Crystal(KBlock):
    """
    Crystal = KBlock with additional crystallization semantics.

    Uses K-Block's isolation field for immutability:
    - PRISTINE: Crystal just created, not yet sealed
    - DIRTY: Crystal being refined before sealing
    - SEALED: Crystal is immutable (replaces frozen=True)
    """

    # Additional fields (stored in K-Block's metadata or dedicated columns)
    crystal_level: CrystalLevel  # SESSION, DAY, WEEK, EPOCH
    source_marks: list[MarkId]   # For SESSION level
    source_crystals: list[CrystalId]  # For DAY+ levels
    insight: str                 # Semantic compression
    significance: str            # Why this matters
    mood: MoodVector             # 7D affective signature
    compression_ratio: float     # sources / 1

    def seal(self) -> None:
        """Seal the crystal, making it immutable."""
        if self.isolation == IsolationState.SEALED:
            raise AlreadySealedError(f"Crystal {self.id} is already sealed")
        self.isolation = IsolationState.SEALED
```

### 2.2 IsolationState Extension

```python
class IsolationState(Enum):
    PRISTINE = "PRISTINE"       # No local changes
    DIRTY = "DIRTY"             # Local changes not committed
    STALE = "STALE"             # Cosmos has newer version
    CONFLICTING = "CONFLICTING" # Local + cosmos both changed
    ENTANGLED = "ENTANGLED"     # Quantum superposition (bidirectional edit)
    SEALED = "SEALED"           # NEW: Immutable (for crystals)
```

### 2.3 Crystal Storage Migration

**Before**:
- Crystals in `CrystalStore` (in-memory + JSONL)
- Separate from K-Block table

**After**:
- Crystals in `kblocks` table with `kind IN ('crystal', 'crystal_session', 'crystal_day', 'crystal_week', 'crystal_epoch')`
- Crystal-specific columns: `crystal_level`, `mood_vector`, `source_ids`
- `isolation = 'SEALED'` enforces immutability

**Migration Path**:
```python
async def migrate_crystals_to_kblocks(crystal_store: CrystalStore, kblock_store: KBlockStore):
    """One-time migration of existing crystals to K-Block table."""
    for crystal in crystal_store.all():
        kblock = KBlock(
            id=f"kb-{crystal.id}",
            path=f"time.crystal.{crystal.level.value}.{crystal.session_id}",
            kind=KBlockKind[f"CRYSTAL_{crystal.level.name}"],
            content=f"# {crystal.insight}\n\n{crystal.significance}",
            base_content=...,
            isolation=IsolationState.SEALED,  # Already crystallized = sealed
            metadata={
                "mood": crystal.mood.to_dict(),
                "source_marks": list(crystal.source_marks),
                "source_crystals": list(crystal.source_crystals),
                "compression_ratio": crystal.compression_ratio,
            }
        )
        await kblock_store.save(kblock)
```

---

## Part III: Upload Integration

### 3.1 Automatic Layer Assignment

**Decision**: Every upload gets Galois loss computed and layer assigned. User can review and edit the suggestion.

**Implementation**:

```python
async def ingest_with_layer(
    event: IngestEvent,
    galois: GaloisLossComputer,
    witness: WitnessService,
) -> KBlock:
    """
    Ingest document with automatic layer assignment.

    Flow:
    1. Create K-Block with kind=UPLOAD
    2. Compute Galois loss
    3. Derive layer from loss
    4. Create suggestion mark
    5. Return K-Block with pending layer
    """
    # Step 1: Create K-Block
    kblock = KBlock(
        id=generate_kblock_id(),
        path=event.claimed_path,
        kind=KBlockKind.UPLOAD,
        content=event.content.decode('utf-8'),
        base_content=event.content.decode('utf-8'),
        isolation=IsolationState.PRISTINE,
        # Layer fields start as pending
        zero_seed_layer=None,  # Pending assignment
        layer_suggestion=None,  # Will be filled
        layer_suggestion_confidence=None,
    )

    # Step 2: Compute Galois loss (async, may use LLM)
    loss_result = await galois.compute(kblock.content)

    # Step 3: Derive layer from loss
    suggested_layer = layer_from_loss(loss_result.total)

    # Step 4: Create suggestion mark (user can review)
    suggestion_mark = await witness.mark(
        action=f"Layer suggestion for {kblock.path}",
        reasoning=f"Galois loss {loss_result.total:.3f} → Layer {suggested_layer}",
        tags=["layer_suggestion", f"layer_{suggested_layer}"],
    )

    # Step 5: Store with pending layer
    kblock.metadata["layer_suggestion"] = suggested_layer
    kblock.metadata["layer_suggestion_confidence"] = 1.0 - loss_result.total
    kblock.metadata["layer_suggestion_mark_id"] = suggestion_mark.id
    kblock.galois_loss = loss_result.total

    return kblock
```

### 3.2 Layer Review UI Pattern

```typescript
interface LayerSuggestionProps {
  kblock: KBlock;
  suggestion: number;  // 1-7
  confidence: number;  // 0-1
  onAccept: () => void;
  onReject: () => void;
  onEdit: (newLayer: number) => void;
}

function LayerSuggestionCard({ kblock, suggestion, confidence, onAccept, onReject, onEdit }: LayerSuggestionProps) {
  return (
    <div className="layer-suggestion">
      <h3>Suggested Layer: L{suggestion}</h3>
      <p>Confidence: {(confidence * 100).toFixed(0)}%</p>
      <p>Based on Galois loss analysis</p>

      <div className="actions">
        <button onClick={onAccept}>Accept</button>
        <button onClick={onReject}>Reject</button>
        <select onChange={(e) => onEdit(parseInt(e.target.value))}>
          {[1,2,3,4,5,6,7].map(l => (
            <option key={l} value={l}>L{l}: {LAYER_NAMES[l]}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
```

---

## Part IV: Edge Storage Pattern

### 4.1 Dual Storage with Sync

**Decision**: Keep both normalized table and JSONB for performance. Implement synchronization.

**Rationale**:
- Normalized table: Enables cross-K-Block queries ("find all K-Blocks that link to X")
- JSONB in K-Block: Fast read for single K-Block ("get edges for X")
- Sync ensures consistency

**Implementation**:

```python
class EdgeSyncService:
    """
    Maintains consistency between normalized edges and K-Block JSONB.

    Write path: Create edge in normalized table → update K-Block JSONB
    Read path: Prefer K-Block JSONB (faster) → fallback to normalized
    """

    async def create_edge(self, edge: KBlockEdge) -> None:
        """Create edge with dual storage."""
        # Step 1: Insert into normalized table
        await self.edge_store.insert(edge)

        # Step 2: Update source K-Block's outgoing_edges
        source = await self.kblock_store.get(edge.source_id)
        source.outgoing_edges.append(edge.to_summary())
        await self.kblock_store.save(source)

        # Step 3: Update target K-Block's incoming_edges
        target = await self.kblock_store.get(edge.target_id)
        target.incoming_edges.append(edge.to_summary())
        await self.kblock_store.save(target)

    async def sync_kblock_edges(self, kblock_id: str) -> None:
        """Recompute K-Block JSONB from normalized table (repair)."""
        incoming = await self.edge_store.query(target_id=kblock_id)
        outgoing = await self.edge_store.query(source_id=kblock_id)

        kblock = await self.kblock_store.get(kblock_id)
        kblock.incoming_edges = [e.to_summary() for e in incoming]
        kblock.outgoing_edges = [e.to_summary() for e in outgoing]
        await self.kblock_store.save(kblock)
```

### 4.2 Edge Summary (JSONB Format)

```python
@dataclass
class EdgeSummary:
    """
    Lightweight edge representation stored in K-Block JSONB.
    Full edge data lives in normalized table.
    """
    edge_id: str
    other_kblock_id: str  # The "other" end of the edge
    kind: str             # Edge kind (derives_from, contradicts, etc.)
    direction: str        # "incoming" or "outgoing"
    label: str | None     # Optional label
```

---

## Part V: Feed and Meta Layer Integration

### 5.1 Layers as Optional Filter

**Decision**: Layers available as advanced filter, not prominent by default.

**Implementation**:

```python
@dataclass
class FeedFilter:
    """
    Feed filtering with optional layer awareness.
    """
    # Original filters
    layer_filter: set[int] | None = None  # Filter by Zero Seed layer (1-7)
    min_loss: float | None = None
    max_loss: float | None = None
    author: str | None = None
    principle: str | None = None
    time_range: tuple[datetime, datetime] | None = None

    # NEW: Layer awareness (optional)
    include_layers: set[int] | None = None  # Show only these layers
    exclude_layers: set[int] | None = None  # Hide these layers
    layer_ordering: bool = False            # Sort by layer (L1→L7)

    def matches(self, kblock: KBlock) -> bool:
        """Check if K-Block matches filter."""
        # ... existing logic ...

        # Layer filtering (only if specified)
        if self.include_layers and kblock.zero_seed_layer not in self.include_layers:
            return False
        if self.exclude_layers and kblock.zero_seed_layer in self.exclude_layers:
            return False

        return True
```

### 5.2 Feed UI with Layer Badges

```typescript
interface FeedItemProps {
  kblock: KBlock;
  showLayerBadge?: boolean;  // Optional, default false
}

function FeedItem({ kblock, showLayerBadge = false }: FeedItemProps) {
  return (
    <div className="feed-item">
      <h3>{kblock.title}</h3>

      {/* Layer badge only shown if opted in */}
      {showLayerBadge && kblock.zero_seed_layer && (
        <span className={`layer-badge layer-${kblock.zero_seed_layer}`}>
          L{kblock.zero_seed_layer}
        </span>
      )}

      <p className="preview">{kblock.preview}</p>
      <footer>
        <span className="loss-indicator" style={{
          backgroundColor: lossToColor(kblock.galois_loss)
        }} />
        <span>{formatDate(kblock.created_at)}</span>
      </footer>
    </div>
  );
}
```

### 5.3 Meta Coherence from K-Block

**Decision**: Meta reads pre-computed galois_loss from K-Block, not recomputing.

```python
class TimelineService:
    """
    Meta timeline service using K-Block's galois_loss.
    """

    async def compute_coherence(self) -> float:
        """
        Compute overall coherence from K-Block losses.

        Coherence = 1 - average(galois_loss) across all K-Blocks
        """
        kblocks = await self.kblock_store.query(kind=KBlockKind.ZERO_NODE)

        if not kblocks:
            return 1.0  # Perfect coherence (nothing to measure)

        total_loss = sum(kb.galois_loss or 0.0 for kb in kblocks)
        avg_loss = total_loss / len(kblocks)

        return 1.0 - avg_loss
```

---

## Part VI: Mark → K-Block Linkage

### 6.1 Mark Structure Extension

```python
@dataclass(frozen=True)
class Mark:
    """
    Mark with explicit K-Block linkage.
    """
    # Existing fields...
    id: MarkId
    origin: str
    domain: WitnessDomain
    stimulus: Stimulus
    response: Response
    timestamp: datetime

    # NEW: K-Block linkage
    target_kblock_id: str | None = None  # The K-Block this mark is about
    source_kblock_ids: tuple[str, ...] = ()  # K-Blocks involved in creating this mark
```

### 6.2 Mark Query by K-Block

```python
class MarkStore:
    """
    Mark store with K-Block-aware queries.
    """

    async def marks_for_kblock(self, kblock_id: str) -> list[Mark]:
        """Get all marks related to a K-Block."""
        return await self.query(
            lambda m: m.target_kblock_id == kblock_id or kblock_id in m.source_kblock_ids
        )

    async def kblock_history(self, kblock_id: str) -> list[Mark]:
        """Get chronological history of a K-Block via marks."""
        marks = await self.marks_for_kblock(kblock_id)
        return sorted(marks, key=lambda m: m.timestamp)
```

---

## Part VII: The Unified Schema

### 7.1 PostgreSQL Schema (Extended)

```sql
-- K-Block table (the unified spine)
CREATE TABLE kblocks (
    id VARCHAR(64) PRIMARY KEY,
    path VARCHAR(512) NOT NULL,
    kind VARCHAR(32) NOT NULL DEFAULT 'file',

    -- Content
    content TEXT NOT NULL,
    base_content TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,

    -- State
    isolation VARCHAR(32) NOT NULL DEFAULT 'PRISTINE',

    -- Zero Seed fields
    zero_seed_layer INTEGER,
    zero_seed_kind VARCHAR(64),
    lineage JSONB DEFAULT '[]',
    has_proof BOOLEAN DEFAULT FALSE,
    toulmin_proof JSONB,
    confidence FLOAT DEFAULT 1.0,
    galois_loss FLOAT DEFAULT 0.0,

    -- Crystal fields (NEW)
    crystal_level VARCHAR(32),  -- SESSION, DAY, WEEK, EPOCH
    mood_vector JSONB,          -- 7D affective signature
    source_ids JSONB,           -- Mark IDs (L0) or Crystal IDs (L1+)
    compression_ratio FLOAT,
    insight TEXT,
    significance TEXT,

    -- Layer suggestion (for uploads)
    layer_suggestion INTEGER,
    layer_suggestion_confidence FLOAT,
    layer_suggestion_mark_id VARCHAR(64),

    -- Edges (JSONB for fast read)
    incoming_edges JSONB DEFAULT '[]',
    outgoing_edges JSONB DEFAULT '[]',

    -- Metadata
    tags JSONB DEFAULT '[]',
    created_by VARCHAR(128) DEFAULT 'system',
    metadata JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Edge table (normalized for cross-K-Block queries)
CREATE TABLE kblock_edges (
    id VARCHAR(64) PRIMARY KEY,
    source_id VARCHAR(64) NOT NULL REFERENCES kblocks(id),
    target_id VARCHAR(64) NOT NULL REFERENCES kblocks(id),
    kind VARCHAR(64) NOT NULL,
    label VARCHAR(256),
    context TEXT,
    confidence FLOAT DEFAULT 1.0,
    galois_loss FLOAT DEFAULT 0.0,
    mark_id VARCHAR(64),  -- Witness mark for this edge
    edge_metadata JSONB DEFAULT '{}',
    created_by VARCHAR(128) DEFAULT 'system',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Mark table (with K-Block linkage)
CREATE TABLE witness_marks (
    id VARCHAR(64) PRIMARY KEY,
    origin VARCHAR(128) NOT NULL,
    domain VARCHAR(32) NOT NULL,
    action TEXT NOT NULL,
    reasoning TEXT,

    -- K-Block linkage (NEW)
    target_kblock_id VARCHAR(64) REFERENCES kblocks(id),
    source_kblock_ids JSONB DEFAULT '[]',

    -- Proof structure
    proof JSONB,
    constitutional_alignment JSONB,

    -- Metadata
    tags JSONB DEFAULT '[]',
    author VARCHAR(128) DEFAULT 'system',
    session_id VARCHAR(64),
    parent_mark_id VARCHAR(64),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Indexes
CREATE INDEX idx_kblocks_kind ON kblocks(kind);
CREATE INDEX idx_kblocks_layer ON kblocks(zero_seed_layer);
CREATE INDEX idx_kblocks_isolation ON kblocks(isolation);
CREATE INDEX idx_kblocks_crystal_level ON kblocks(crystal_level);
CREATE INDEX idx_edges_source ON kblock_edges(source_id);
CREATE INDEX idx_edges_target ON kblock_edges(target_id);
CREATE INDEX idx_marks_target_kblock ON witness_marks(target_kblock_id);
CREATE INDEX idx_marks_source_kblocks ON witness_marks USING GIN(source_kblock_ids);
```

---

## Part VIII: Laws & Verification

### 8.1 The Unified Laws

| # | Law | Statement | Enforcement |
|---|-----|-----------|-------------|
| 1 | **Single Source** | K-Block table is truth for all content | No content outside K-Block |
| 2 | **Kind Integrity** | kind determines semantics | Type constraints |
| 3 | **Edge Consistency** | Normalized = JSONB (eventual) | EdgeSyncService |
| 4 | **Seal Immutability** | SEALED K-Blocks cannot change | Write constraint |
| 5 | **Layer Grounding** | All ZERO_NODE K-Blocks have layer | NOT NULL constraint |
| 6 | **Upload Assignment** | All UPLOAD K-Blocks get layer suggestion | ingest_with_layer() |
| 7 | **Mark Linkage** | Marks reference K-Blocks by ID | Foreign key |

### 8.2 Verification Tests

```python
def test_crystal_stored_as_kblock():
    """Verify crystals are K-Blocks."""
    crystal = crystallize(marks=[...])

    assert crystal.kind in [
        KBlockKind.CRYSTAL_SESSION,
        KBlockKind.CRYSTAL_DAY,
        KBlockKind.CRYSTAL_WEEK,
        KBlockKind.CRYSTAL_EPOCH,
    ]
    assert crystal.isolation == IsolationState.SEALED


def test_upload_gets_layer_suggestion():
    """Verify uploads get layer suggestions."""
    kblock = await ingest_with_layer(event)

    assert kblock.kind == KBlockKind.UPLOAD
    assert kblock.metadata["layer_suggestion"] is not None
    assert 1 <= kblock.metadata["layer_suggestion"] <= 7


def test_edge_sync_consistency():
    """Verify edge sync maintains consistency."""
    edge = await edge_sync.create_edge(...)

    source = await kblock_store.get(edge.source_id)
    target = await kblock_store.get(edge.target_id)

    assert any(e["edge_id"] == edge.id for e in source.outgoing_edges)
    assert any(e["edge_id"] == edge.id for e in target.incoming_edges)


def test_mark_links_to_kblock():
    """Verify marks reference K-Blocks."""
    kblock = await kblock_store.create(...)
    mark = await witness.mark(action="...", target_kblock_id=kblock.id)

    assert mark.target_kblock_id == kblock.id

    # Can query marks by K-Block
    marks = await mark_store.marks_for_kblock(kblock.id)
    assert mark in marks
```

---

## Part IX: Migration Roadmap

### Phase 1: Schema Extension (Week 1)
```
- Add crystal_* columns to kblocks table
- Add layer_suggestion_* columns to kblocks table
- Add target_kblock_id, source_kblock_ids to witness_marks table
- Create indexes
```

### Phase 2: Crystal Migration (Week 2)
```
- Migrate existing crystals from CrystalStore to kblocks table
- Update crystallization to create K-Blocks
- Update crystal queries to use K-Block store
- Deprecate CrystalStore (keep for read-only historical access)
```

### Phase 3: Upload Integration (Week 3)
```
- Implement ingest_with_layer()
- Add layer suggestion UI component
- Wire upload endpoint to use new flow
- Add "reviewing" state for pending layer decisions
```

### Phase 4: Edge Sync (Week 4)
```
- Implement EdgeSyncService
- Add edge creation trigger
- Add repair command for existing inconsistencies
- Monitor for drift
```

### Phase 5: Feed/Meta Layer Awareness (Week 5)
```
- Add layer filter to FeedFilter
- Add layer badges to Feed UI (optional display)
- Update Meta to read galois_loss from K-Block
- Add layer distribution to Meta timeline
```

---

## Part X: Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Pattern |
|--------------|----------------|-----------------|
| Creating Crystal without K-Block | Breaks unified spine | Use crystallize() which creates K-Block |
| Storing edges in JSONB only | Loses query capability | Use EdgeSyncService for dual storage |
| Ignoring layer suggestion | Loses epistemic grounding | Always show suggestion, allow override |
| Querying CrystalStore directly | Uses deprecated store | Query K-Blocks with kind=CRYSTAL_* |
| Modifying SEALED K-Block | Violates immutability | Check isolation before write |

---

## Closing Meditation

The Unified Data Spine is not a refactor. It is the recognition that **all data in kgents is fundamentally K-Blocks** viewed through different lenses.

A file is a K-Block.
An upload is a K-Block with sovereign provenance.
A Zero Seed node is a K-Block with layer and proof.
A crystal is a K-Block that cannot be unsealed.
A mark references its K-Block.

The spine is the truth. Everything else is projection.

> *"The noun is a lie. There is only the K-Block and its rate of change."*

---

## Cross-References

**Specifications**:
- `spec/protocols/k-block.md` — K-Block primitives
- `spec/protocols/kblock-unification.md` — Original unification (AD-010)
- `spec/protocols/zero-seed.md` — Epistemic holarchy
- `spec/protocols/witness-primitives.md` — Mark and Crystal structures

**Implementation**:
- `impl/claude/services/k_block/core/kblock.py` — K-Block domain model
- `impl/claude/services/witness/crystal.py` — Crystal (to be migrated)
- `impl/claude/services/sovereign/integration.py` — Upload integration
- `impl/claude/services/feed/service.py` — Feed service

**Skills**:
- `docs/skills/metaphysical-fullstack.md` — Architecture pattern
- `docs/skills/analysis-operad.md` — Four-mode analysis
- `docs/skills/crown-jewel-patterns.md` — Service patterns

---

*Canonical specification written: 2025-12-25*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
*Derived from: Four-Mode Analysis + Kent's Design Decisions*
