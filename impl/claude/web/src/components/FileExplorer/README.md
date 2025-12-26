# FileExplorer — Zero Seed Genesis File Manager

**Phase 2 deliverable** of the Zero Seed Genesis Grand Strategy.

## Philosophy

> "Sovereignty before integration. The staging area is sacred."

The FileExplorer implements the Zero Seed integration flow:
1. Files enter through `uploads/` (sovereign staging)
2. User drags FROM `uploads/` TO destination folder
3. IntegrationDialog shows layer assignment, edges, contradictions
4. User confirms → file integrated with K-Block creation

## Components

### FileExplorer (Main Component)

Tree view file explorer with drag-drop integration.

```tsx
import { FileExplorer } from '@/components/FileExplorer';

<FileExplorer
  rootPaths={['uploads', 'spec', 'impl', 'docs']}
  currentFile="/spec/protocols/witness.md"
  onSelectFile={(path) => console.log('Selected:', path)}
  onUploadComplete={(files) => console.log('Uploaded:', files)}
  loadTree={async (path) => {
    // Fetch directory contents
    return await sovereignApi.listDirectory(path);
  }}
/>
```

### UploadZone

Drag-drop upload zone for `uploads/` folder.

```tsx
import { UploadZone } from '@/components/FileExplorer';

<UploadZone
  onUploadComplete={(files) => console.log('Uploaded:', files)}
  maxSizeMB={10}
  allowedExtensions={['md', 'txt', 'json']}
/>
```

### IntegrationDialog

Confirmation dialog for file integration.

```tsx
import { IntegrationDialog } from '@/components/FileExplorer';

<IntegrationDialog
  metadata={{
    sourcePath: 'uploads/new-file.md',
    destinationPath: 'spec/protocols/',
    detectedLayer: 'L3',
    galoisLoss: 0.15,
    discoveredEdges: [
      { type: 'implements', target: 'spec/protocols/witness.md' },
    ],
    contradictions: [],
  }}
  onConfirm={() => console.log('Integrating...')}
  onCancel={() => console.log('Cancelled')}
/>
```

## Features

### Tree View
- Collapsible folders
- File type icons
- Current file highlighting
- Keyboard navigation (j/k, Enter, h/l)

### Upload Integration
- Drag-drop zone in `uploads/` folder
- Visual upload progress
- File validation (size, type)
- Click to browse fallback

### Integration Flow
- Drag FROM `uploads/` TO destination
- Shows detected layer (L1-L7)
- Displays Galois loss score
- Lists discovered edges
- Warns about contradictions
- User confirms to integrate

### K-Block Status
- Layer badge (L1-L7) with color coding
- Loss indicator (color-coded dot)
- Tooltips with full metadata

### Context Menu
- Open (files only)
- Move
- Split (files only)
- Delete

## Directory Structure

```
▼ uploads/      (drop zone, sovereign staging)
  [incoming files]
▼ spec/         (specifications L3-L4)
  ▼ protocols/
    witness.md (L3)
▼ impl/         (implementation L5)
  ▼ claude/
    services/
▼ docs/         (documentation L6-L7)
  ▼ skills/
```

## Layer Detection

The system automatically detects the Zero Seed layer based on destination path:

| Path Pattern | Layer | Description |
|--------------|-------|-------------|
| `spec/axioms/` | L1 | Axioms - Foundational truths |
| `spec/principles/` | L2 | Principles - Derived from axioms |
| `spec/protocols/` | L3 | Protocol Specs - Interface definitions |
| `spec/` (other) | L4 | Application Specs - Domain logic |
| `impl/` | L5 | Implementation - Concrete code |
| `docs/skills/` | L6 | Skills - How-to guides |
| `docs/` (other) | L7 | Documentation - Reference material |

## Integration Metadata

When dragging a file from `uploads/` to a destination, the system gathers:

```typescript
interface IntegrationMetadata {
  sourcePath: string;           // Source file in uploads/
  destinationPath: string;       // Target directory
  detectedLayer: string;         // L1-L7
  galoisLoss: number;            // 0-1 (information loss)
  discoveredEdges: Edge[];       // Related K-Blocks
  contradictions: string[];      // Detected conflicts
}
```

## Styling

Uses **STARK BIOME** design tokens from `design/tokens.css`:

- 90% steel (cool industrial frames)
- 10% earned glow (organic accents)
- Layer colors: L1-L2 red, L3-L4 orange, L5 yellow, L6-L7 green
- Loss colors: <20% green, <40% yellow, <60% orange, ≥60% red

## API Integration

To connect to backend, implement:

```typescript
// Load directory tree
async function loadTree(path: string): Promise<FileNode[]> {
  const response = await fetch(`/api/sovereign/tree?path=${path}`);
  return response.json();
}

// Upload file to uploads/
async function uploadFile(file: File): Promise<void> {
  const formData = new FormData();
  formData.append('file', file);
  await fetch('/api/sovereign/upload', {
    method: 'POST',
    body: formData,
  });
}

// Integrate file from uploads/ to destination
async function integrateFile(metadata: IntegrationMetadata): Promise<void> {
  await fetch('/api/sovereign/integrate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(metadata),
  });
}
```

## Example: Full Integration

```tsx
import { useState } from 'react';
import { FileExplorer } from '@/components/FileExplorer';
import { sovereignApi } from '@/api/client';

export function ZeroSeedPage() {
  const [currentFile, setCurrentFile] = useState<string | null>(null);

  return (
    <div className="zero-seed-page">
      <aside className="zero-seed-page__sidebar">
        <FileExplorer
          rootPaths={['uploads', 'spec', 'impl', 'docs']}
          currentFile={currentFile}
          onSelectFile={setCurrentFile}
          onUploadComplete={(files) => {
            console.log('Upload complete:', files);
            // Refresh tree
          }}
          loadTree={sovereignApi.listDirectory}
        />
      </aside>
      <main className="zero-seed-page__content">
        {currentFile && (
          <div>Viewing: {currentFile}</div>
        )}
      </main>
    </div>
  );
}
```

## Testing

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { FileExplorer } from './FileExplorer';

test('renders file tree', () => {
  render(<FileExplorer />);
  expect(screen.getByText('uploads')).toBeInTheDocument();
  expect(screen.getByText('spec')).toBeInTheDocument();
});

test('expands folder on click', () => {
  render(<FileExplorer />);
  const uploadsFolder = screen.getByText('uploads');
  fireEvent.click(uploadsFolder);
  // Assert expanded state
});

test('opens integration dialog on drop', () => {
  render(<FileExplorer />);
  // Simulate drag-drop from uploads/ to spec/
  // Assert IntegrationDialog opens
});
```

## Files

- `FileExplorer.tsx` (569 lines) - Main file explorer component
- `UploadZone.tsx` (296 lines) - Upload zone for uploads/ folder
- `IntegrationDialog.tsx` (228 lines) - Integration confirmation dialog
- `types.ts` (63 lines) - TypeScript type definitions
- `index.ts` (15 lines) - Public exports
- `FileExplorer.css` (841 lines) - STARK BIOME styling
- **Total: 2,012 lines**

## Next Steps (Phase 3)

1. Connect to backend API endpoints
2. Implement real file system operations
3. Add K-Block analysis during integration
4. Implement Move/Split/Delete actions
5. Add keyboard shortcuts (j/k navigation, etc.)
6. Add file search/filter
7. Add batch operations (multi-select)

---

*"The file waits in uploads/. When ready, it finds its layer."*
