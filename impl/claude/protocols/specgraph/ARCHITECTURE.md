# SpecGraph Architecture

> "Every spec is a node. Every reference is an edge. The graph IS the system."

This document clarifies the TWO SpecGraph backends and the ONE correct access pattern for UI/frontend code.

---

## The Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND / UI                            │
│                  (React, CLI, marimo, JSON)                      │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         │ ONLY call this AGENTESE path:
                         │ concept.specgraph.*
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│         protocols/agentese/contexts/concept_specgraph.py         │
│                                                                  │
│  @node("concept.specgraph") — THE interface for UI              │
│  Aspects: manifest, query, edges, tokens, navigate, discover... │
└────────────────────────┬─────────────────────────────────────────┘
                         │
           ┌─────────────┴───────────────┐
           │                             │
           ▼                             ▼
┌───────────────────────┐   ┌─────────────────────────────┐
│ protocols/specgraph/  │   │ agentese/specgraph/         │
│ (Core Hypergraph)     │   │ (Autopoiesis Machinery)     │
├───────────────────────┤   ├─────────────────────────────┤
│ - types.py            │   │ - compile.py                │
│ - parser.py           │   │ - reflect.py                │
│ - registry.py         │   │ - drift.py                  │
│ - (pure data)         │   │ - discovery.py              │
└───────────────────────┘   │ (internal only)             │
                            └─────────────────────────────┘
```

---

## Clear Separation

### 1. **protocols/specgraph/** — Core Hypergraph Data Structures

**Purpose**: Navigable hypergraph of specs

**What it contains**:
- `types.py` — SpecNode, SpecEdge, SpecToken (dataclasses)
- `parser.py` — Markdown edge/token discovery (regex-based)
- `registry.py` — Singleton registry (graph storage, queries)

**Who uses it**:
- `concept_specgraph.py` (the AGENTESE node)
- Autopoiesis infrastructure (compile, reflect, drift)

**Access pattern**: Internal only. Do NOT import directly from frontend.

---

### 2. **agentese/specgraph/** — Autopoiesis Infrastructure

**Purpose**: Spec → Code compilation and drift detection

**What it contains**:
- `compile.py` — Spec → Python scaffolding
- `reflect.py` — Python → Spec extraction
- `drift.py` — Compare spec vs impl
- `discovery.py` — Hybrid discovery (file system + Python imports)

**Who uses it**:
- CI/CD pipelines (spec drift checks)
- Build tools (code generation from specs)
- Internal consistency verification

**Access pattern**: Internal only. Frontend NEVER calls this.

---

### 3. **concept_specgraph.py** — THE Interface for UI

**Purpose**: AGENTESE node exposing SpecGraph to frontend

**What it exposes**:
```python
@node("concept.specgraph")
class SpecGraphNode:
    # Aspects (the public API)
    manifest()   # View graph structure and statistics
    query()      # Query a specific spec node
    edges()      # Get edges from a spec
    tokens()     # Get interactive tokens
    navigate()   # Navigate the spec hypergraph
    discover()   # Discover and register all specs
    summary()    # Human-readable summary
```

**Who calls it**:
- Frontend hooks: `useSpecNavigation.ts` (React)
- CLI commands: `kg concept.specgraph.*`
- marimo notebooks: `logos.invoke("concept.specgraph.*")`
- JSON projections: `/agentese/concept.specgraph/*`

**Access pattern**: This is the ONLY way frontend should access SpecGraph.

---

## Frontend Access Pattern

### Current State (needs cleanup)

**Old membrane hooks** (TO BE MIGRATED):
- `/web/src/membrane/useSpecNavigation.ts` — React hooks for concept.specgraph
  - `useSpecGraph()` — Graph stats and discovery
  - `useSpecQuery()` — Query specific spec
  - `useSpecEdges()` — Fetch edges
  - `useSpecNavigate()` — Navigation

**Usage**:
- `membrane/views/SpecView.tsx` — Uses `useSpecQuery()`
- `membrane/FocusPane.tsx` — Uses `EdgeType` from useSpecNavigation

**Problem**: These are in `membrane/` which is being archived. Need to move to `hypergraph/`.

---

### Target State (Phase 2)

**New hypergraph hooks**:
- Move `useSpecNavigation.ts` → `/web/src/hypergraph/useSpecNavigation.ts`
- Wire into `HypergraphEditor.tsx` for spec navigation
- `HypergraphEditor` currently uses `useGraphNode()` (WitnessedGraph API)
- Need to decide: SpecGraph or WitnessedGraph?

**Architectural decision needed**:

1. **Option A**: HypergraphEditor uses WitnessedGraph only
   - `concept.graph.neighbors` (witnessed edges, marks, confidence)
   - `useSpecNavigation` only for Membrane (deprecated soon)
   - Simpler, unified access pattern

2. **Option B**: HypergraphEditor supports BOTH
   - WitnessedGraph for runtime navigation (witnessed edges, live updates)
   - SpecGraph for static spec browsing (tier hierarchy, tokens)
   - More complex, but supports both use cases

**Current implementation**: HypergraphEditor uses WitnessedGraph (Option A)

---

## Do NOT

### Frontend Anti-Patterns (Avoid These)

1. **Direct imports from protocols/specgraph/**
   ```typescript
   // WRONG - breaks encapsulation
   import { SpecNode } from '../../protocols/specgraph/types';
   ```

2. **Direct imports from agentese/specgraph/**
   ```typescript
   // WRONG - autopoiesis is internal only
   import { compile } from '../../protocols/agentese/specgraph/compile';
   ```

3. **Mixing UI concerns with autopoiesis**
   ```typescript
   // WRONG - compile is for CI/CD, not UI
   await compile('spec/agents/flux.md');
   ```

---

## Correct Pattern (Follow This)

### Frontend Hook

```typescript
// web/src/hypergraph/useSpecNavigation.ts
export function useSpecGraph() {
  const discover = async () => {
    // Call AGENTESE path
    const response = await fetch('/agentese/concept.specgraph/discover', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    return response.json();
  };

  return { discover };
}
```

### React Component

```tsx
// web/src/hypergraph/HypergraphEditor.tsx
import { useSpecGraph } from './useSpecNavigation';

function HypergraphEditor() {
  const { discover } = useSpecGraph();

  useEffect(() => {
    discover(); // Calls concept.specgraph.discover
  }, []);
}
```

### CLI Command

```bash
kg concept.specgraph discover
kg concept.specgraph query path=spec/agents/flux.md
kg concept.specgraph navigate path=spec/agents/flux.md edge=extends
```

---

## Migration Path

### Phase 1.3 (Current)
- [x] Document architecture (this file)
- [ ] Move useSpecNavigation to hypergraph/
- [ ] Update import paths in SpecView.tsx, FocusPane.tsx

### Phase 2 (Future)
- [ ] Decide: WitnessedGraph only or support both?
- [ ] Wire useSpecNavigation into HypergraphEditor (if needed)
- [ ] Archive membrane/ directory
- [ ] Remove duplicate hooks

---

## Key Insights

1. **AGENTESE is the API boundary**
   - Frontend NEVER imports Python types directly
   - All access goes through AGENTESE paths
   - Projections handle format conversion (React, CLI, marimo, JSON)

2. **Two backends, one interface**
   - `protocols/specgraph/` = core data structures
   - `agentese/specgraph/` = autopoiesis machinery
   - `concept_specgraph.py` = unified interface

3. **No direct coupling**
   - Frontend doesn't know about registry.py internals
   - Frontend doesn't know about compile.py
   - Frontend only knows AGENTESE aspects

4. **WitnessedGraph is winning**
   - HypergraphEditor uses WitnessedGraph (concept.graph)
   - Witnessed edges, marks, confidence, live updates
   - SpecGraph may become specialized for spec-only browsing

---

*Compiled: 2025-12-20 | Hypergraph Simplification Phase 1.3*
