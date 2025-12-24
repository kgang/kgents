# Document Proxy Implementation Plan

> Implementation roadmap for spec/protocols/document-proxy.md

## Phase Summary

| Phase | Scope | Effort | Dependencies |
|-------|-------|--------|--------------|
| 1 | DocumentCache + IndexedDB | Medium | None |
| 2 | Section Detection (Backend) | Medium | None |
| 3 | Section-aware SceneGraph | Small | Phase 2 |
| 4 | DocumentProxy Hook | Medium | Phase 1, 3 |
| 5 | Incremental Parse | Medium | Phase 2, 4 |
| 6 | UX Polish | Small | Phase 4 |

---

## Phase 1: DocumentCache with IndexedDB

### Goal
Create a persistent cache for parsed SceneGraphs that survives page refresh.

### Files to Create/Modify

```
web/src/services/
└── documentCache/
    ├── index.ts           # Barrel export
    ├── types.ts           # CachedDocument, CacheStats
    ├── memoryCache.ts     # LRU in-memory layer
    ├── indexedDBCache.ts  # Persistent layer
    └── documentCache.ts   # Combined cache service
```

### Key Types

```typescript
// types.ts
interface CachedDocument {
  path: string;
  contentHash: string;
  sceneGraph: SceneGraph;
  tokenCount: number;
  tokenTypes: Record<string, number>;
  cachedAt: number;
  ttlMs: number;
  parserVersion: string;
}

interface CacheStats {
  memoryHits: number;
  memoryMisses: number;
  indexedDBHits: number;
  indexedDBMisses: number;
  totalParses: number;
}
```

### Implementation Notes

1. **Content Hash**: SHA-256 via Web Crypto API
   ```typescript
   async function hashContent(content: string): Promise<string> {
     const encoder = new TextEncoder();
     const data = encoder.encode(content);
     const hashBuffer = await crypto.subtle.digest('SHA-256', data);
     return Array.from(new Uint8Array(hashBuffer))
       .map(b => b.toString(16).padStart(2, '0'))
       .join('')
       .slice(0, 16);
   }
   ```

2. **IndexedDB Schema**:
   - Database: `kgents-document-cache`
   - Object Store: `documents` with keyPath `path`
   - Indexes: `contentHash`, `cachedAt`

3. **TTL**: Default 24 hours, configurable per document

---

## Phase 2: Section Detection (Backend)

### Goal
Add section boundary detection to the document parsing pipeline.

### Files to Modify

```
protocols/agentese/projection/
├── tokens_to_scene.py     # Add section detection
└── scene.py               # Add Section dataclass
```

### Key Types

```python
# scene.py
@dataclass(frozen=True)
class Section:
    """A semantic section of a document."""
    index: int
    range_start: int
    range_end: int
    section_hash: str
    section_type: SectionType
    heading: str | None

@dataclass(frozen=True)
class SectionType:
    kind: Literal['heading', 'paragraph', 'code_block', 'list', 'table', 'blockquote', 'frontmatter']
    level: int | None = None  # For headings
    language: str | None = None  # For code blocks

# Extended SceneGraph
@dataclass(frozen=True)
class SceneGraph:
    # ... existing fields ...
    sections: list[Section] = field(default_factory=list)
    section_hashes: dict[int, str] = field(default_factory=dict)
```

### Algorithm: Section Detection

```python
def detect_sections(content: str) -> list[Section]:
    """Detect semantic sections in markdown content."""
    sections = []
    lines = content.split('\n')

    current_start = 0
    current_type = None
    in_code_block = False
    code_fence = None

    for i, line in enumerate(lines):
        # Handle code blocks (atomic sections)
        if line.startswith('```') or line.startswith('~~~'):
            if not in_code_block:
                in_code_block = True
                code_fence = line[:3]
                # Close previous section, start code section
            else:
                in_code_block = False
                # Close code section

        # Handle headings (always start new section)
        if not in_code_block and line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            if 1 <= level <= 6:
                # Close previous section, start heading section

        # Handle blank lines (potential section boundary)
        if not in_code_block and line.strip() == '':
            # Mark potential boundary

    return sections
```

---

## Phase 3: Section-aware SceneGraph

### Goal
Include section metadata in SceneGraph nodes for frontend section tracking.

### Changes

1. **SceneNode Extension**:
   ```python
   @dataclass(frozen=True)
   class SceneNode:
       # ... existing fields ...
       section_index: int | None = None
   ```

2. **API Response**:
   ```python
   # Include sections in parse response
   return {
       "scene_graph": scene_graph.to_dict(),
       "sections": [s.to_dict() for s in sections],
       "section_hashes": section_hashes,
   }
   ```

---

## Phase 4: DocumentProxy Hook

### Goal
Create the main orchestration hook that implements the caching strategy.

### Files to Create

```
web/src/hypergraph/
└── useDocumentProxy.ts    # Main hook (replaces useDocumentParser)
```

### State Machine

```typescript
type DocumentProxyState =
  | { status: 'idle' }
  | { status: 'loading'; path: string }
  | { status: 'cached'; doc: CachedDocument; fresh: boolean }
  | { status: 'parsing'; fallback: string; cachedDoc: CachedDocument | null }
  | { status: 'stale'; doc: CachedDocument; pendingDoc: CachedDocument }
  | { status: 'error'; error: string; fallback: string };
```

### Hook Interface

```typescript
interface UseDocumentProxyOptions {
  path: string;
  content: string;
  mode: 'NORMAL' | 'INSERT';
  onNavigate?: (path: string) => void;
}

interface UseDocumentProxyReturn {
  // Rendering
  sceneGraph: SceneGraph | null;
  renderMode: 'interactive' | 'raw';

  // Status
  status: DocumentProxyState['status'];
  isLoading: boolean;
  hasPendingUpdate: boolean;

  // Actions
  pullUpdate: () => void;
  forceReparse: () => void;

  // Stats
  cacheHit: boolean;
  parseTimeMs: number;
}
```

### Key Behaviors

1. **Cache-First Loading**:
   ```typescript
   useEffect(() => {
     if (mode === 'INSERT') return; // Skip in edit mode

     const cached = await cache.get(path, contentHash);
     if (cached) {
       setState({ status: 'cached', doc: cached, fresh: true });
       return;
     }

     // No cache: show raw, parse in background
     setState({ status: 'parsing', fallback: content, cachedDoc: null });
     const parsed = await documentApi.parse(content);
     await cache.set(path, contentHash, parsed);
     setState({ status: 'cached', doc: parsed, fresh: true });
   }, [path, contentHash, mode]);
   ```

2. **No Screen Violence**:
   ```typescript
   // If already showing interactive, don't swap to raw
   if (state.status === 'cached' && !state.fresh) {
     // User is reading stale cache
     // Parse in background, show "Update available" when ready
   }
   ```

3. **Pull-to-Update**:
   ```typescript
   const pullUpdate = useCallback(() => {
     if (state.status === 'stale') {
       setState({ status: 'cached', doc: state.pendingDoc, fresh: true });
     }
   }, [state]);
   ```

---

## Phase 5: Incremental Parse

### Goal
Re-parse only changed sections when exiting INSERT mode.

### K-Block Extension

```typescript
// Extended K-Block state
interface KBlockState {
  // ... existing ...
  sectionBoundaries: SectionBoundary[];
  dirtySections: Set<number>;
  lastEditPosition: number;
}

interface SectionBoundary {
  index: number;
  startOffset: number;
  endOffset: number;
  hash: string;
}
```

### Incremental Parse Algorithm

```typescript
async function incrementalParse(
  oldDoc: CachedDocument,
  newContent: string,
  dirtySections: Set<number>
): Promise<CachedDocument> {
  // 1. Detect sections in new content
  const newSections = detectSections(newContent);

  // 2. For each section, check if it changed
  const sectionsToReparse: number[] = [];
  for (const section of newSections) {
    if (dirtySections.has(section.index)) {
      sectionsToReparse.push(section.index);
    } else if (section.hash !== oldDoc.sectionHashes[section.index]) {
      sectionsToReparse.push(section.index);
    }
  }

  // 3. Parse only dirty sections
  const parsedSections = await documentApi.parseSections(
    newContent,
    sectionsToReparse
  );

  // 4. Splice into cached SceneGraph
  const newNodes = spliceNodes(oldDoc.sceneGraph.nodes, parsedSections);

  return {
    ...oldDoc,
    contentHash: await hashContent(newContent),
    sceneGraph: { ...oldDoc.sceneGraph, nodes: newNodes },
    sectionHashes: newSections.reduce((acc, s) => {
      acc[s.index] = s.hash;
      return acc;
    }, {}),
  };
}
```

### Backend Endpoint

```python
# POST /agentese/self/document/parse_sections
async def parse_sections(
    text: str,
    section_indices: list[int],
    layout_mode: str = "COMFORTABLE"
) -> dict:
    """Parse only specified sections of a document."""
    sections = detect_sections(text)
    nodes = []

    for section in sections:
        if section.index in section_indices:
            # Parse this section
            section_content = text[section.range_start:section.range_end]
            section_nodes = tokens_to_nodes(section_content)
            nodes.extend(section_nodes)
        # Sections not in indices will be spliced from cache client-side

    return {
        "sections": section_indices,
        "nodes": [n.to_dict() for n in nodes],
    }
```

---

## Phase 6: UX Polish

### Goal
Implement the visual indicators and transitions.

### Components

1. **ParseStatusBadge**:
   ```tsx
   function ParseStatusBadge({ status }: { status: string }) {
     if (status === 'parsing') {
       return <div className="parse-badge parse-badge--parsing">Parsing...</div>;
     }
     if (status === 'stale') {
       return (
         <button className="parse-badge parse-badge--stale" onClick={pullUpdate}>
           Update available
         </button>
       );
     }
     return null;
   }
   ```

2. **Transitions**:
   - Fade-in when switching from raw to parsed
   - Section-level highlight when section updates
   - No jarring swaps

### CSS

```css
.parse-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.25rem 0.5rem;
  font-size: 0.65rem;
  border-radius: 3px;
  transition: opacity 0.2s ease;
}

.parse-badge--parsing {
  background: var(--steel-800);
  color: var(--steel-400);
  animation: pulse 1.5s infinite;
}

.parse-badge--stale {
  background: var(--life-900);
  color: var(--life-300);
  cursor: pointer;
}

.parse-badge--stale:hover {
  background: var(--life-800);
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
```

---

## Testing Strategy

### Unit Tests

1. **DocumentCache**:
   - Memory LRU eviction
   - IndexedDB persistence
   - TTL expiration
   - Hash collision handling

2. **Section Detection**:
   - Heading boundaries
   - Code block atomicity
   - Frontmatter handling
   - Edge cases (empty sections, nested lists)

3. **Incremental Parse**:
   - Single section change
   - Multiple section changes
   - Section addition/deletion
   - Section reordering

### Integration Tests

1. **Cache Hit Flow**: Open cached doc → instant render
2. **Cache Miss Flow**: Open new doc → raw → parse → interactive
3. **Edit Flow**: INSERT → edit → EXIT → incremental update
4. **Stale Flow**: Background change → stale badge → pull update

---

## Rollout Plan

1. **Phase 1-2**: Ship behind feature flag `DOCUMENT_PROXY_CACHE`
2. **Phase 3-4**: Enable for power users, collect metrics
3. **Phase 5**: Full rollout after cache hit rate > 80%
4. **Phase 6**: Polish based on user feedback

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cache hit rate | > 90% | `cacheHits / (cacheHits + cacheMisses)` |
| First paint (cached) | < 16ms | Performance.mark |
| First paint (uncached) | < 100ms | Performance.mark |
| Screen violence incidents | 0 | User reports |
| Section re-parse time | < 50ms | Per-section timing |

---

*"The best parse is the one that already happened."*
