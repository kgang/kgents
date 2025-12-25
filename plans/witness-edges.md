# Witness Marks as Graph Edges

> *"The proof IS the decision. The mark IS the witness."*

**Created**: 2025-12-24
**Status**: Designed, Ready for Implementation
**Effort**: MVP 8-10h, Full 16-23h

---

## Vision

Witness marks (decisions, insights, gotchas) become **first-class edges** in the Zero Seed hypergraph, not side-effect POSTs. When Kent and Claude make a decision, that decision manifests as a navigable edge connecting the concepts involved.

```
Node: "Implement loss-native components"
  │
  ├──[DECIDES]─→ Mark: "Use viridis palette" (Kent + Claude, synthesis)
  │                  └── [BECAUSE]─→ Mark: "Colorblind accessible"
  │
  └──[WITNESSES]─→ Mark: "Completed 2025-12-24"
```

---

## The Problem

Currently:
- Witness marks live in `witness_marks` table (isolated)
- Zero Seed nodes live in hypergraph (isolated)
- No connection between decisions and the specs they affect
- Navigating from a spec to "why was this decided?" requires external search

---

## The Solution

### New Edge Kind: `witnessed`

Add `witnessed` to Zero Seed edge kinds:

| Property | Value |
|----------|-------|
| Kind | `"witnessed"` |
| Semantics | Edge created by a decision mark |
| Layer Range | L6-L7 (Reflection/Representation) |
| Target | Any layer (can point up or down) |
| Confidence | Derived from `Mark.proof.qualifier` |

### Example Edge

```json
{
  "id": "ze-witness-001",
  "source": "time.insight.decision-2025-12-24",
  "target": "concept.spec.architecture-choice",
  "kind": "witnessed",
  "context": "Decision: Use SSE instead of WebSockets. Reasoning: simpler ops.",
  "confidence": 0.9,
  "created_at": "2025-12-24T14:32:18Z",
  "mark_id": "mark-abc123def456",
  "proof": { /* Toulmin structure */ },
  "evidence_tier": "empirical"
}
```

---

## MVP Scope (8-10 hours)

### Goal
Marks visible as edges in hypergraph, readable proof on hover.

### Backend Changes

#### 1. Extend ZeroEdge Model (1h)
**File**: `protocols/api/zero_seed.py`

```python
class ZeroEdge(BaseModel):
    # ... existing fields ...

    # NEW: Witness integration
    mark_id: str | None = Field(
        None,
        description="Associated Mark ID (if created from Witness)"
    )
    proof: ToulminProof | None = Field(
        None,
        description="Toulmin proof from the decision"
    )
    evidence_tier: str | None = Field(
        None,
        description="Evidence tier: categorical, empirical, aesthetic, somatic"
    )
```

#### 2. Add Endpoint: Create Edge from Mark (2h)
**File**: `protocols/api/zero_seed.py`

```python
class CreateWitnessedEdgeRequest(BaseModel):
    mark_id: str
    source_node_id: str
    target_node_id: str
    context: str | None = None  # Auto-extract from mark if not provided

@router.post("/edges/from-mark", response_model=ZeroEdge)
async def create_witnessed_edge(request: CreateWitnessedEdgeRequest) -> ZeroEdge:
    """
    Create a Zero Seed edge from a Witness mark.

    1. Load Mark from witness service
    2. Extract Proof → ToulminProof
    3. Derive confidence from qualifier
    4. Create ZeroEdge with mark_id reference
    """
    pass
```

#### 3. Modify Node Detail Endpoint (1h)
**File**: `protocols/api/zero_seed.py`

Add to `NodeDetailResponse`:
```python
witnessed_edges: list[ZeroEdge] = Field(
    default_factory=list,
    description="Edges created by decisions that reference this node"
)
```

Query: `SELECT * FROM edges WHERE kind='witnessed' AND (source=node_id OR target=node_id)`

### Frontend Changes

#### 4. Edge Styling for "witnessed" (1h)
**File**: `web/src/hypergraph/EdgeRenderer.tsx` (or equivalent)

```typescript
const edgeStyleMap: Record<string, EdgeStyle> = {
  witnessed: {
    stroke: '#8B4513',        // Brown (earthy, decision)
    strokeDasharray: '5,5',   // Dashed to distinguish
    width: 2.5,
    label: 'Mark',
    arrowColor: '#8B4513',
  },
  // ... existing ...
};
```

#### 5. Mark Preview on Hover (2h)
**File**: `web/src/hypergraph/EdgeMarkPreview.tsx` (new)

```typescript
interface EdgeMarkPreviewProps {
  edge: ZeroEdge;
}

export function EdgeMarkPreview({ edge }: EdgeMarkPreviewProps) {
  if (!edge.mark_id) return null;

  return (
    <div className="edge-mark-preview">
      <h4>Decision Mark</h4>
      {edge.proof && (
        <div className="proof-summary">
          <p><strong>Claim:</strong> {edge.proof.claim}</p>
          <p><strong>Warrant:</strong> {edge.proof.warrant}</p>
          <p><strong>Tier:</strong> {edge.proof.tier}</p>
        </div>
      )}
      <p className="context">{edge.context}</p>
    </div>
  );
}
```

#### 6. Wire Hover to Preview (1h)
**File**: `web/src/hypergraph/HypergraphEditor.tsx`

Add hover handler for edges with `kind === 'witnessed'` to show `EdgeMarkPreview`.

### Testing (1h)

- Create a test mark via `km "Test decision" --tag decide`
- Call `POST /api/zero-seed/edges/from-mark` with mark_id
- Verify edge appears in hypergraph
- Verify hover shows proof

---

## Full Scope (16-23 hours)

Includes MVP plus:

### Backend Additions

#### 7. Database Schema (2h)
**File**: `migrations/xxx_witness_edges.py`

```sql
CREATE TABLE zero_seed_witnessed_edges (
    edge_id VARCHAR(32) PRIMARY KEY,
    source_node_id VARCHAR(255) NOT NULL,
    target_node_id VARCHAR(255) NOT NULL,
    kind VARCHAR(32) NOT NULL,
    context TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL,

    -- Witness integration
    mark_id VARCHAR(32),
    proof_data JSON,
    evidence_tier VARCHAR(32),
    synthesis_phase VARCHAR(32),

    -- Audit
    created_by VARCHAR(64),
    created_via VARCHAR(32),

    FOREIGN KEY (mark_id) REFERENCES witness_marks(id) ON DELETE SET NULL
);

CREATE INDEX idx_witnessed_edges_mark_id ON zero_seed_witnessed_edges(mark_id);
CREATE INDEX idx_witnessed_edges_source ON zero_seed_witnessed_edges(source_node_id);
CREATE INDEX idx_witnessed_edges_target ON zero_seed_witnessed_edges(target_node_id);
```

#### 8. D-gent Integration (3h)
**File**: `agents/d/zero_seed.py` (new or extend)

- Store witnessed edges in PostgreSQL
- Query edges by node_id
- Handle orphaned edges (mark deleted)
- Sync with witness service

#### 9. Witness Service Hook (2h)
**File**: `services/witness/mark.py`

Add optional hook when mark is created:
```python
async def on_mark_created(mark: Mark):
    """Optionally create Zero Seed edge if mark references nodes."""
    if mark.metadata.get("zero_seed_source") and mark.metadata.get("zero_seed_target"):
        await create_witnessed_edge(mark)
```

### Frontend Additions

#### 10. Right-Click Context Menu (2h)
**File**: `web/src/hypergraph/ContextMenu.tsx`

When edge with `kind === 'witnessed'` is selected:
```typescript
menuItems.push(
  { label: 'View Mark', action: () => navigateToMark(edge.mark_id) },
  { label: 'View Proof', action: () => showProofModal(edge.proof) },
  { label: 'Trace Decision', action: () => openWitnessTracer(edge.mark_id) },
);
```

#### 11. Navigation Commands (2h)
**File**: `web/src/hypergraph/useKeyHandler.ts`

New keybindings:
- `gm` — Go to marks (show witness trail for current node)
- `gw` — Go to warrant (show justification)
- `gd` — Go to decision (show dialectical synthesis)

#### 12. Reverse Flow: Mark → Graph (3h)
**File**: `web/src/witness/MarkDetail.tsx` (extend)

From Witness UI:
1. View a Mark
2. Click "Connect to Graph"
3. Search for source and target nodes
4. Create edge via `POST /edges/from-mark`

#### 13. Search and Filter (2h)
**File**: `web/src/hypergraph/FilterPanel.tsx`

Add filter toggle:
```typescript
<FilterChip
  label="Witness Decisions"
  icon="triangle-alert"
  color="#8B4513"
  edgeKind="witnessed"
/>
```

#### 14. Documentation (1h)
- Update `docs/skills/witness-for-agents.md`
- Add section on edge creation
- Document navigation commands

---

## Edge Cases

| Case | Handling |
|------|----------|
| Mark deleted but edge exists | `edge.mark_id` becomes null, edge labeled "(orphaned)" |
| Target node deleted | Preserve edge as dangling reference |
| Source node not in Zero Seed | Allow creation (cross-silo reference) |
| Two marks create same edge | Deduplicate by `(source, target, mark_id)` |
| Mark proof changes | Edge.proof becomes stale; decide on cache policy |
| Circular witnessed edges | Allowed (dialectical loops are OK) |

---

## Files to Modify

### Backend
| File | Change |
|------|--------|
| `protocols/api/zero_seed.py` | Extend ZeroEdge, add endpoints |
| `services/witness/mark.py` | Add creation hook (optional) |
| `agents/d/zero_seed.py` | D-gent storage integration |
| `migrations/xxx_witness_edges.py` | Database schema |

### Frontend
| File | Change |
|------|--------|
| `hypergraph/EdgeRenderer.tsx` | Style for "witnessed" edges |
| `hypergraph/EdgeMarkPreview.tsx` | New component |
| `hypergraph/HypergraphEditor.tsx` | Hover handler, keybindings |
| `hypergraph/ContextMenu.tsx` | Right-click menu items |
| `hypergraph/useKeyHandler.ts` | gm/gw/gd commands |
| `hypergraph/FilterPanel.tsx` | Filter toggle |
| `witness/MarkDetail.tsx` | "Connect to Graph" flow |

---

## Success Criteria

### MVP
- [ ] `POST /api/zero-seed/edges/from-mark` works
- [ ] Witnessed edges render as dashed brown lines
- [ ] Hovering shows proof summary
- [ ] TypeScript + Python type checks pass

### Full
- [ ] All MVP criteria
- [ ] Database schema deployed
- [ ] `gm`/`gw`/`gd` keybindings work
- [ ] Right-click context menu shows mark options
- [ ] Can create edge from Witness UI
- [ ] Filter panel includes witness toggle
- [ ] Documentation updated

---

## Philosophical Alignment

This design honors Kent's vision:

**"The proof IS the decision. The mark IS the witness."**

- Marks don't just live in isolation; they *manifest as edges*
- Proofs become navigable in the hypergraph
- Decisions trace back to architectural reasoning
- The graph becomes a *decision history*, not just a content map

**Tasteful Implementation**:
- New edge kind is visually distinct (dashed, brown)
- No UI clutter; edges are quiet until hovered
- Two-way navigation: graph ↔ mark
- Proof embedded; no extra clicks needed

---

## Next Steps

1. **Start with MVP** (8-10h)
   - Extend ZeroEdge model
   - Add POST endpoint
   - Add edge styling
   - Add hover preview

2. **Test with real marks**
   - `km "Test decision" --tag decide`
   - Create edge via API
   - Verify visualization

3. **Iterate on UX**
   - Get Kent's feedback
   - Adjust styling if needed
   - Consider keybinding additions

4. **Full scope if validated**
   - Add database persistence
   - Add navigation commands
   - Add reverse flow

---

*"Every decision traces. Every mark witnesses. The graph tells the story."*
