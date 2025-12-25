# DirectorView

**Telescope + Trail composition for document management**

> "Navigate the document graph. The loss IS the readiness."

Replaces `DirectorDashboard.tsx` (961 LOC) with focused composition (~250 LOC).

## Philosophy

Documents are nodes in a proof landscape. Processing status maps to loss:

- `uploaded` → High loss (0.8) — not analyzed yet
- `processing` → Mid loss (0.5) — working on it
- `ready` → Low loss (0.2) — ready to use
- `executed` → Very low loss (0.1) — completed
- `stale` → Mid-high loss (0.6) — needs refresh
- `failed` → Max loss (1.0) — broken
- `ghost` → Very high loss (0.9) — doesn't exist

## Layout

```
┌─────────────────────────────────────────────────────────┐
│ Trail (document ancestry)                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Telescope (documents as nodes)                          │
│  - Documents colored by processing status                │
│  - Relationships shown as gradients                      │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ [Upload Zone] (drag & drop)                              │
└─────────────────────────────────────────────────────────┘
```

## Usage

```tsx
import { DirectorView, documentToNode } from '@/constructions/DirectorView';

function DocumentManager() {
  const [documents, setDocuments] = useState<DocumentEntry[]>([]);
  const [trail, setTrail] = useState<string[]>([]);
  const [selected, setSelected] = useState<string>();

  // Transform documents to telescope nodes
  const nodes = documents.map(documentToNode);

  // Build relationships from document references
  const relationships = new Map<string, GradientVector>();
  // ... derive from document.impl_count, document.claim_count, etc.

  return (
    <DirectorView
      documents={nodes}
      relationships={relationships}
      trail={trail}
      selectedDocument={selected}
      onDocumentClick={(docId) => setSelected(docId)}
      onTrailClick={(index, id) => setTrail(trail.slice(0, index + 1))}
      onUpload={(files) => uploadDocuments(files)}
    />
  );
}
```

## Props

| Prop | Type | Description |
|------|------|-------------|
| `documents` | `NodeProjection[]` | Documents as telescope nodes |
| `relationships` | `Map<string, GradientVector>` | Document relationships as gradients |
| `trail` | `string[]` | Current navigation trail (document ancestry) |
| `selectedDocument` | `string?` | Selected document ID |
| `onDocumentClick` | `(docId: string) => void` | Document click handler |
| `onTrailClick` | `(index: number, id: string) => void` | Trail navigation handler |
| `onUpload` | `(files: File[]) => void` | Upload handler |
| `width` | `number?` | Canvas width (default: 1200) |
| `height` | `number?` | Canvas height (default: 700) |

## Composition Pattern

DirectorView is a **construction** — a composition of two primitives:

1. **Telescope** — Spatial viewer with loss-based coloring
2. **Trail** — Breadcrumb navigation showing derivation path

This demonstrates the fundamental pattern:

```
Construction = Primitive ∘ Primitive
DirectorView = Telescope ∘ Trail
```

## Status Color Mapping

| Status | Color | Loss | Meaning |
|--------|-------|------|---------|
| `uploaded` | Steel gray | 0.8 | Waiting for analysis |
| `processing` | Amber | 0.5 | Being processed |
| `ready` | Green | 0.2 | Ready to use |
| `executed` | Purple | 0.1 | Successfully executed |
| `stale` | Light steel | 0.6 | Needs update |
| `failed` | Red | 1.0 | Error state |
| `ghost` | Dark steel | 0.9 | Referenced but missing |

## Keyboard Navigation

Inherited from Telescope primitive:

- `l` — Navigate to lowest loss (most ready document)
- `h` — Navigate to highest loss (most problematic document)
- `Shift+G` — Follow gradient from current document
- `+/-` — Zoom in/out

## Empty State

Shows centered message with upload button when no documents exist.

## Drag & Drop

Upload zone at bottom supports:
- Drag files over zone (highlights in purple)
- Drop to upload
- Click "browse" to select files

## Integration Points

### API Transform

```tsx
import { listDocuments } from '@/api/director';
import { documentToNode } from '@/constructions/DirectorView';

const { documents } = await listDocuments();
const nodes = documents.map(documentToNode);
```

### Relationship Building

```tsx
// Derive gradients from document metadata
const relationships = new Map<string, GradientVector>();

for (const doc of documents) {
  if (doc.impl_count && doc.impl_count > 0) {
    // Document has implementations — gradient points toward completion
    relationships.set(doc.path, {
      x: 0.5,
      y: -0.8, // Upward (toward lower layers)
      magnitude: doc.impl_count / 10,
    });
  }
}
```

## File Size

- **DirectorView.tsx**: ~250 LOC
- **DirectorView.css**: ~180 LOC
- **Total**: ~430 LOC

Compare to `DirectorDashboard.tsx`: 961 LOC (55% reduction).

## Anti-Pattern

❌ **Don't** embed document list logic in DirectorView
✅ **Do** use Telescope + Trail as pure presentation

DirectorView is a **view construction**, not a data manager. Keep it thin.
