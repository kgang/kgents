# Document Proxy Protocol

> *"Loading a document should feel like opening a book you've already read."*

## Status

**AD-015** | Draft | 2025-12-24

## Problem Statement

The current document rendering system has three critical UX problems:

1. **Loading Latency**: Documents must be parsed on every view, causing visible delay
2. **Screen Violence**: The UI swaps from raw to parsed format mid-read
3. **Full Re-parse**: Any edit triggers complete document re-parsing

## Design Principles

### The "Watertight Bulkheads" Principle

> *"A submarine doesn't flood entirely when one compartment is breached."*

Documents are partitioned into **sections** (semantic boundaries). Each section:
- Has its own content hash
- Caches independently
- Re-parses independently

When content changes, only affected sections are invalidated.

### The "Newspaper on the Doorstep" Principle

> *"The paper is already printed when you pick it up."*

Parsed documents are cached **before** the user requests them. When a document is opened:
1. **If cached**: Display immediately
2. **If not cached**: Display raw with subtle "parsing..." indicator
3. **Never**: Swap formats after the user starts reading

### The "Gentle Pull" Principle

> *"Don't push changes onto a reading user; let them pull when ready."*

If the user is viewing a stale cached version and a new parse completes:
- Show a subtle "Updated content available" indicator
- Let the user choose when to refresh
- Animate the transition smoothly

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DOCUMENT PROXY LAYER                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐                │
│  │ ContentPane │◄───│ DocumentProxy│◄───│ SectionCache    │                │
│  │             │    │              │    │                 │                │
│  │ "What to    │    │ "When to     │    │ "What's stored" │                │
│  │  render"    │    │  re-parse"   │    │                 │                │
│  └─────────────┘    └──────────────┘    └─────────────────┘                │
│         │                  │                    │                           │
│         ▼                  ▼                    ▼                           │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐                │
│  │Interactive  │    │ SectionDiff  │    │ IndexedDB       │                │
│  │Document     │    │ Algorithm    │    │ (persistent)    │                │
│  └─────────────┘    └──────────────┘    └─────────────────┘                │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                           K-BLOCK INTEGRATION                                │
│                                                                              │
│  K-Block tracks:                                                            │
│  - workingContent (what user is editing)                                    │
│  - baseContent (last saved version)                                         │
│  - sectionBoundaries[] (NEW: section offsets)                               │
│  - dirtyRanges[] (NEW: which sections changed)                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Structures

### SectionedDocument

```typescript
interface SectionedDocument {
  /** Document path */
  path: string;

  /** Full content hash (for cache key) */
  contentHash: string;

  /** Sections with individual hashes */
  sections: Section[];

  /** Parsed SceneGraph (full document) */
  sceneGraph: SceneGraph;

  /** Timestamp of last parse */
  parsedAt: number;

  /** Version for cache invalidation */
  version: number;
}

interface Section {
  /** Section index */
  index: number;

  /** Byte range in source [start, end) */
  range: [number, number];

  /** Content hash of this section */
  hash: string;

  /** Section type (heading level, paragraph, code block, etc.) */
  type: SectionType;

  /** Parsed nodes for this section */
  nodes: SceneNode[];
}

type SectionType =
  | { kind: 'heading'; level: 1 | 2 | 3 | 4 | 5 | 6 }
  | { kind: 'paragraph' }
  | { kind: 'code_block'; language: string }
  | { kind: 'list' }
  | { kind: 'table' }
  | { kind: 'blockquote' }
  | { kind: 'horizontal_rule' }
  | { kind: 'frontmatter' };
```

### DocumentProxyState

```typescript
type DocumentProxyState =
  | { status: 'idle' }
  | { status: 'loading'; path: string }
  | { status: 'cached'; doc: SectionedDocument }
  | { status: 'stale'; doc: SectionedDocument; pendingUpdate: SectionedDocument }
  | { status: 'parsing'; doc: SectionedDocument | null; content: string }
  | { status: 'error'; error: string; fallbackContent: string };
```

## Section Boundary Detection

Sections are delimited by **blank lines** with additional rules:

1. **Headings** (`# Title`) always start a new section
2. **Code blocks** (```) are atomic sections
3. **Lists** continue until a blank line followed by non-list content
4. **Tables** are atomic sections
5. **Frontmatter** (`---`) is its own section

### Algorithm: `detectSections(content: string): SectionBoundary[]`

```
Input: Raw markdown content
Output: Array of section boundaries with types

1. Split content into lines
2. For each line:
   a. If in code block, continue until closing fence
   b. If heading pattern, start new section
   c. If blank line after non-blank, mark potential boundary
   d. If frontmatter delimiter, handle specially
3. Return section boundaries with byte offsets
```

## Incremental Parsing

### Algorithm: `incrementalParse(oldDoc, newContent): SectionedDocument`

```
Input: Previous SectionedDocument, new raw content
Output: Updated SectionedDocument with minimal re-parsing

1. Detect sections in new content
2. For each new section:
   a. Compute content hash
   b. If hash matches old section at same index → reuse nodes
   c. If hash differs or index shifted → mark for re-parse
3. Batch-parse only dirty sections
4. Assemble new SectionedDocument from cached + fresh nodes
```

### Optimization: Edit Locality

Most edits are local (user types in one paragraph). Track:
- Cursor position during edit
- Affected line range
- Only re-detect sections in affected range

## Cache Strategy

### Two-Tier Cache

1. **Memory Cache** (LRU, 50 documents)
   - Fastest access
   - Lost on page refresh

2. **IndexedDB Cache** (persistent, 500 documents)
   - Survives page refresh
   - Async access (~5ms)

### Cache Key

```typescript
function cacheKey(path: string, contentHash: string): string {
  return `doc:${path}:${contentHash}`;
}
```

### Cache Invalidation

A cached document is valid if:
1. Path matches
2. Content hash matches
3. Parser version matches (stored in metadata)

## K-Block Integration

### Extended K-Block State

```typescript
interface KBlockState {
  // Existing fields
  blockId: string;
  isolation: IsolationLevel;
  isDirty: boolean;
  baseContent: string;
  workingContent: string;
  checkpoints: Checkpoint[];

  // NEW: Section tracking
  sectionBoundaries: SectionBoundary[];
  dirtyRanges: Range[];
  lastEditPosition: number;
}

interface SectionBoundary {
  offset: number;
  type: SectionType;
  hash: string;
}

interface Range {
  start: number;
  end: number;
}
```

### Edit Tracking

When user edits content:
1. Record cursor position
2. Compute diff from previous content
3. Expand dirty range to section boundaries
4. Only these sections will re-parse on mode exit

## UI/UX Flows

### Flow 1: Open Cached Document

```
User: :e spec/protocols/witness.md
System:
  1. Check memory cache → MISS
  2. Check IndexedDB cache → HIT (hash matches)
  3. Display cached SceneGraph immediately
  4. Background: verify cache still valid
```

**User sees**: Instant render, no loading state

### Flow 2: Open Uncached Document

```
User: :e spec/protocols/new-doc.md
System:
  1. Check caches → MISS
  2. Display: Raw content with subtle "Parsing..." badge
  3. Background: Parse document
  4. When ready: Show "Parsed view available" pill
  5. User clicks or waits 2s → Animate to parsed view
```

**User sees**: Raw content immediately, optional upgrade

### Flow 3: Edit and Return to View

```
User: Press 'i', edit paragraph 3, press Escape
System:
  1. Detect edit in section 3 (lines 45-52)
  2. Mark section 3 as dirty
  3. Exit INSERT mode
  4. Re-parse ONLY section 3
  5. Splice new nodes into cached SceneGraph
  6. Render immediately
```

**User sees**: Instant transition, section 3 updated

### Flow 4: Stale Cache with New Parse Ready

```
User: Reading document (parsed view)
System: Background parse completed (external change)
UI:
  - Subtle indicator: "Updated content available" (top-right)
  - User can click to refresh
  - Or continue reading stale version
```

**User sees**: No interruption, pull-to-update option

## Implementation Plan

### Phase 1: Section Detection (Backend)
- [ ] Add section boundary detection to `tokens_to_scene.py`
- [ ] Include section hashes in SceneGraph response
- [ ] Add `/agentese/self/document/parse_sections` endpoint

### Phase 2: Cache Layer (Frontend)
- [ ] Create `DocumentCache` service with memory + IndexedDB tiers
- [ ] Implement cache key strategy
- [ ] Add cache hit/miss logging

### Phase 3: DocumentProxy Hook
- [ ] Create `useDocumentProxy` hook
- [ ] Implement state machine for loading states
- [ ] Handle cache-first rendering

### Phase 4: K-Block Section Tracking
- [ ] Extend K-Block state with section boundaries
- [ ] Track dirty ranges during edits
- [ ] Expose dirty sections for incremental parse

### Phase 5: Incremental Parse
- [ ] Implement section diffing algorithm
- [ ] Create incremental parse endpoint or client-side assembly
- [ ] Test with various edit patterns

### Phase 6: UX Polish
- [ ] Add "Parsing..." badge for uncached docs
- [ ] Add "Update available" pill for stale cache
- [ ] Implement smooth transitions

## Categorical Properties

### Identity Law
```
parse(doc) >> cache >> retrieve ≡ parse(doc)
```
Caching preserves parse semantics.

### Composition Law
```
parseSection(s1) >> parseSection(s2) ≡ parseSections([s1, s2])
```
Section parsing is composable.

### Idempotence
```
cache(doc) >> cache(doc) ≡ cache(doc)
```
Multiple caches of same content converge.

## Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cache hit rate | > 90% | Log cache hits/misses |
| First paint (cached) | < 16ms | Performance.mark |
| First paint (uncached) | < 100ms | Performance.mark |
| Section re-parse | < 50ms | Per-section timing |
| Full re-parse (avoided) | < 5% of views | Counter |

## Open Questions

1. **Section granularity**: Are paragraphs the right size, or should we go finer (sentences)?
2. **Cross-section tokens**: What if a token spans sections (e.g., multi-paragraph blockquote)?
3. **Concurrent edits**: How do we handle collaborative editing with sections?

## References

- [K-Block Protocol](k-block.md)
- [Interactive Text Spec](interactive-text.md)
- [AGENTESE Projection](agentese-projection.md)

---

*"The best parse is the one that already happened."*
