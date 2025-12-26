# Workspace Construction

> *"The Hypergraph Editor IS the app. Everything else is a sidebar."*

## Overview

The Workspace is a three-panel IDE-like layout that unifies the kgents experience:

```
┌────────────┬─────────────────────────┬────────────────┐
│            │                         │                │
│   FILES    │         GRAPH           │      CHAT      │
│   (Left)   │         (Center)        │      (Right)   │
│            │                         │                │
│  Ctrl+B    │       THE EDITOR        │     Ctrl+J     │
│  to toggle │       always visible    │     to toggle  │
│            │                         │                │
└────────────┴─────────────────────────┴────────────────┘
```

## UX Transformation (2025-12-25)

This construction implements the decisions from `docs/UX-LAWS.md`:

| Decision | Implementation |
|----------|---------------|
| "Hypergraph Editor IS the app" | Workspace is THE page |
| "Chat is a sidebar" | ChatPanel embedded in right sidebar |
| "Director is open files" | DirectorDashboard/FileExplorer in left sidebar |
| "No welcome page" | / redirects to /world.document |
| "Graph-first navigation" | No command palette, use ? for help |

## Components

### Workspace.tsx

Main container that manages:
- Left sidebar state (Files/Director)
- Right sidebar state (Chat)
- Keyboard shortcuts (Ctrl+B, Ctrl+J)
- State persistence via `useSidebarState`

### useSidebarState Hook

Persists sidebar state to localStorage:
```typescript
interface SidebarState {
  leftOpen: boolean;     // Files sidebar
  rightOpen: boolean;    // Chat sidebar
  leftWidth: number;     // For future resize support
  rightWidth: number;    // For future resize support
}
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+B | Toggle left sidebar (Files) |
| Ctrl+J | Toggle right sidebar (Chat) |
| ? | Open help panel |

## Routes After Transformation

All these routes now redirect to `/world.document`:
- `/chat` → Workspace (use Ctrl+J for chat)
- `/director` → Workspace (use Ctrl+B for files)
- `/self.chat` → Workspace
- `/self.director` → Workspace
- `/brain`, `/feed`, `/chart`, `/zero-seed` → Workspace

## Backend Contract Gaps

Features that need backend implementation:

| Feature | Status | Endpoint Needed |
|---------|--------|-----------------|
| Chat merge | UI exists, no backend | `POST /api/chat/{id}/merge` |
| Mention resolution (7 types) | Returns mocks | `POST /api/chat/mention/resolve` |
| Symbol search | Stubbed | `POST /api/chat/mention/search/symbols` |
| File search | Stubbed | `POST /api/chat/mention/search/files` |
| Session restore | Not implemented | `POST /api/chat/{id}/restore` |
| Session compress | Not implemented | `POST /api/chat/{id}/compress` |
| Session crystallize | Not implemented | `POST /api/chat/{id}/crystallize` |

See the full contract analysis in the agent exploration output.

## File Structure

```
constructions/Workspace/
├── Workspace.tsx      # Main component
├── Workspace.css      # Three-panel layout styles
├── index.ts           # Exports
└── README.md          # This file

hooks/
└── useSidebarState.ts # Sidebar state persistence
```

## Usage

```tsx
import { Workspace } from '../constructions/Workspace';

<Workspace
  currentPath={currentPath}
  recentFiles={recentFiles}
  onNavigate={handleNavigate}
  onUploadFile={handleUpload}
  onClearRecent={handleClearRecent}
  loadNode={loadNode}
/>
```

---

*"The file is a lie. There is only the graph."*

**Filed**: 2025-12-25
