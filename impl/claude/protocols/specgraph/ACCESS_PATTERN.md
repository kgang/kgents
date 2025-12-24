# SpecGraph Access Pattern — Quick Reference

> "Every spec is a node. Every reference is an edge. The graph IS the system."

**THE RULE**: Frontend ONLY calls `concept.specgraph.*` via AGENTESE.

---

## For Frontend Developers

### React Hooks (Correct Pattern)

```typescript
// ✅ CORRECT - Import from hypergraph
import { useSpecGraph, useSpecQuery } from '@/hypergraph/useSpecNavigation';

function MyComponent() {
  const { discover, stats } = useSpecGraph();
  const { query } = useSpecQuery();

  useEffect(() => {
    discover(); // Calls concept.specgraph.discover via AGENTESE
  }, []);

  const handleClick = (path: string) => {
    query(path); // Calls concept.specgraph.query via AGENTESE
  };
}
```

```typescript
// ❌ WRONG - Don't import Python types directly
import { SpecNode } from '../../protocols/specgraph/types'; // NO!

// ❌ WRONG - Don't call internal APIs
import { compile } from '../../protocols/agentese/specgraph/compile'; // NO!
```

### Available Hooks

```typescript
// All hooks call concept.specgraph.* under the hood
import {
  useSpecGraph,      // Graph stats and discovery
  useSpecQuery,      // Query specific spec
  useSpecEdges,      // Fetch edges from spec
  useSpecNavigate,   // Navigate hypergraph
} from '@/hypergraph/useSpecNavigation';
```

### Hook Details

#### `useSpecGraph()`

```typescript
const { discovered, stats, loading, error, discover, refresh } = useSpecGraph();

// Stats structure:
interface SpecGraphStats {
  specs: number;
  edges: number;
  tokens: number;
  by_tier: Record<string, number>;
  by_edge_type: Record<string, number>;
}
```

#### `useSpecQuery()`

```typescript
const { spec, loading, error, query, clear } = useSpecQuery();

await query('spec/agents/flux.md');

// spec structure:
interface SpecQueryResult {
  node: SpecNode;
  edges: Record<string, string[]>;  // by type
  tokens: Record<string, number>;   // by type
}
```

#### `useSpecEdges()`

```typescript
const { edges, loading, error, fetchEdges } = useSpecEdges();

await fetchEdges('spec/agents/flux.md', 'extends');

// edges structure:
interface SpecEdge {
  type: EdgeType;
  target: string;
  line?: number;
}
```

#### `useSpecNavigate()`

```typescript
const { current, targets, edge, loading, error, navigate, setEdge } = useSpecNavigate();

await navigate('spec/agents/flux.md', 'extends');

// current: SpecNode
// targets: SpecNode[]
```

---

## For CLI Users

```bash
# Discover all specs
kg concept.specgraph discover

# View graph stats
kg concept.specgraph manifest

# Query specific spec
kg concept.specgraph query path=spec/agents/flux.md

# Get edges
kg concept.specgraph edges path=spec/agents/flux.md edge_type=extends

# Navigate
kg concept.specgraph navigate path=spec/agents/flux.md edge=extends

# Summary
kg concept.specgraph summary
```

---

## For marimo Users

```python
import logos

# Discover all specs
await logos.invoke("concept.specgraph.discover", umwelt)

# Query specific spec
result = await logos.invoke(
    "concept.specgraph.query",
    umwelt,
    path="spec/agents/flux.md"
)

# Navigate
result = await logos.invoke(
    "concept.specgraph.navigate",
    umwelt,
    path="spec/agents/flux.md",
    edge="extends"
)
```

---

## Backend Architecture (For Reference)

```
concept.specgraph.* (AGENTESE Interface)
    ↓
concept_specgraph.py (@node decorator)
    ↓
    ├─→ protocols/specgraph/registry.py (core graph operations)
    │   ↓
    │   └─→ protocols/specgraph/parser.py (markdown parsing)
    │       ↓
    │       └─→ protocols/specgraph/types.py (SpecNode, SpecEdge, SpecToken)
    │
    └─→ agentese/specgraph/ (autopoiesis, CI/CD only)
        ├─ compile.py (spec → code)
        ├─ reflect.py (code → spec)
        └─ drift.py (spec vs impl)
```

**Key Points**:
1. Frontend NEVER imports from `protocols/specgraph/` directly
2. Frontend NEVER imports from `agentese/specgraph/`
3. All access goes through `concept.specgraph.*` AGENTESE paths
4. Hooks in `hypergraph/useSpecNavigation.ts` are the canonical interface

---

## Edge Types

```typescript
type EdgeType =
  | 'extends'        // Conceptual extension
  | 'implements'     // Code realization
  | 'tests'          // Test coverage
  | 'extended_by'    // Inverse of extends
  | 'references'     // General mentions
  | 'cross_pollinates' // Cross-domain insights
  | 'contradicts'    // Conflicts
  | 'heritage';      // External sources
```

---

## Token Types

```typescript
type TokenType =
  | 'agentese_path'  // AGENTESE paths (clickable)
  | 'ad_reference'   // AD decision references
  | 'principle_ref'  // Principle references
  | 'impl_ref'       // Implementation file refs
  | 'test_ref'       // Test file refs
  | 'type_ref'       // Type references
  | 'code_block'     // Code blocks (executable)
  | 'heritage_ref';  // External source refs
```

---

## Migration from Old Pattern

### Before (WRONG)

```typescript
// Old membrane pattern (deprecated)
import { useSpecQuery } from '@/membrane/useSpecNavigation';
```

### After (CORRECT)

```typescript
// New hypergraph pattern (canonical)
import { useSpecQuery } from '@/hypergraph/useSpecNavigation';
```

**Status**: Migration complete as of 2025-12-20.
- `membrane/index.ts` re-exports from `hypergraph/` for backward compat
- `membrane/views/SpecView.tsx` updated to import from `hypergraph/`
- `membrane/FocusPane.tsx` updated to import from `hypergraph/`

---

## Why This Pattern?

1. **AGENTESE is the API boundary**
   - Clean separation between frontend and backend
   - Projections handle format conversion
   - Type safety through generated interfaces

2. **Single source of truth**
   - All SpecGraph access flows through one node
   - Easier to track usage and make changes
   - Consistent behavior across CLI/TUI/Web/marimo

3. **No direct coupling**
   - Frontend doesn't depend on Python implementation
   - Can swap backend without breaking frontend
   - Testable in isolation

4. **Future-proof**
   - WitnessedGraph (concept.graph) is the new standard
   - SpecGraph may become specialized for spec-only browsing
   - This pattern supports both

---

*Last updated: 2025-12-20 | Phase 1.3 Hypergraph Simplification*
