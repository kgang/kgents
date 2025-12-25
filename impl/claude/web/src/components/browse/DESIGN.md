# File Browser System Design

> "Tasteful > feature-complete" but also "Everything Must Be Real"

## Overview

Three-tier browsing system:

1. **FileSidebar** (Left sidebar) - Quick actions + file tree
2. **BrowseModal** (Ctrl+O) - Full exhaustive browser for all content types

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WORKSPACE                                       │
├────────────────────┬────────────────────────────────────────┬───────────────┤
│                    │                                        │               │
│   FileSidebar      │           HypergraphEditor             │  ChatSidebar  │
│   (Ctrl+B)         │           (THE APP)                    │  (Ctrl+J)     │
│                    │                                        │               │
│ ┌────────────────┐ │                                        │               │
│ │ Quick Actions  │ │                                        │               │
│ │ [Search] [+]   │ │                                        │               │
│ ├────────────────┤ │                                        │               │
│ │ Recent Files   │ │        ┌─────────────────────┐        │               │
│ │ · README.md    │ │        │                     │        │               │
│ │ · App.tsx      │ │        │    BrowseModal      │        │               │
│ ├────────────────┤ │        │    (Ctrl+O)         │        │               │
│ │ File Tree      │ │        │                     │        │               │
│ │ ▼ src/         │ │        │ [Files] [Docs] ...  │        │               │
│ │   ▶ components │ │        │                     │        │               │
│ │   ▶ hooks      │ │        └─────────────────────┘        │               │
│ │   App.tsx      │ │                                        │               │
│ └────────────────┘ │                                        │               │
│                    │                                        │               │
└────────────────────┴────────────────────────────────────────┴───────────────┘
```

## Component 1: FileSidebar

**Location**: `src/components/browse/FileSidebar.tsx`

### Layout
```
┌──────────────────────────────────┐
│ [🔍 Search...        ] [⬆️] [📂] │  ← Search + Upload + Browse modal
├──────────────────────────────────┤
│ RECENT                   [Clear] │
│ ┌──────────────────────────────┐ │
│ │ 📄 README.md              → │ │
│ │ 📄 App.tsx                → │ │
│ │ 📄 styles.css             → │ │
│ └──────────────────────────────┘ │
├──────────────────────────────────┤
│ FILES                            │
│ ┌──────────────────────────────┐ │
│ │ ▼ src/                       │ │
│ │   ▶ components/              │ │
│ │   ▶ hooks/                   │ │
│ │   📄 App.tsx                 │ │
│ │   📄 main.tsx                │ │
│ │ ▶ spec/                      │ │
│ │ ▶ docs/                      │ │
│ └──────────────────────────────┘ │
├──────────────────────────────────┤
│ <kbd>Ctrl+O</kbd> Browse all     │
└──────────────────────────────────┘
```

### Props
```typescript
interface FileSidebarProps {
  onOpenFile: (path: string) => void;
  onUploadFile?: (file: UploadedFile) => void;
  recentFiles?: string[];
  onClearRecent?: () => void;
  onOpenBrowseModal?: () => void;
}
```

## Component 2: FileTree

**Location**: `src/components/browse/FileTree.tsx`

### Features
- Lazy-loaded directory expansion
- File type icons (📄 doc, 📦 code, 📋 spec)
- Keyboard navigation (j/k, Enter to open, h/l to collapse/expand)
- Current file highlighting
- Filtered view based on search

### Props
```typescript
interface FileTreeProps {
  rootPath?: string;
  onSelectFile: (path: string) => void;
  currentFile?: string;
  searchQuery?: string;
  collapsed?: boolean;
}
```

### Data Structure
```typescript
interface TreeNode {
  path: string;
  name: string;
  type: 'file' | 'directory';
  children?: TreeNode[];
  expanded?: boolean;
  kind?: 'doc' | 'code' | 'spec' | 'unknown';
}
```

## Component 3: BrowseModal

**Location**: `src/components/browse/BrowseModal.tsx`

### Layout
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Browse All                                                           [×]    │
├─────────────────────────────────────────────────────────────────────────────┤
│ [🔍 Search everything...                                              ]     │
├────────────────────┬────────────────────────────────────────────────────────┤
│ CATEGORIES         │ RESULTS                                               │
│                    │                                                        │
│ [All]         234  │ ┌────────────────────────────────────────────────────┐ │
│ [Files]       156  │ │ 📄 README.md                          spec/       │ │
│ [Docs]         42  │ │    Project documentation and setup guide          │ │
│ [Specs]        18  │ ├────────────────────────────────────────────────────┤ │
│ [K-Blocks]     12  │ │ 📦 App.tsx                            src/        │ │
│ [Convos]        6  │ │    Main application component                     │ │
│                    │ ├────────────────────────────────────────────────────┤ │
│ FILTERS            │ │ 📋 witness.md                         spec/proto/ │ │
│ ☐ Modified today   │ │    Witness protocol specification                 │ │
│ ☐ Has annotations  │ └────────────────────────────────────────────────────┘ │
│ ☐ Unread           │                                                        │
│                    │ Showing 42 of 234 results                             │
└────────────────────┴────────────────────────────────────────────────────────┘
```

### Content Types
1. **Files** - All files in the codebase
2. **Docs** - Markdown documentation (*.md)
3. **Specs** - Specification files (spec/*.md)
4. **K-Blocks** - Knowledge blocks (structured content)
5. **Conversations** - Past chat sessions

### Props
```typescript
interface BrowseModalProps {
  open: boolean;
  onClose: () => void;
  onSelectItem: (item: BrowseItem) => void;
  initialCategory?: BrowseCategory;
  initialQuery?: string;
}

type BrowseCategory = 'all' | 'files' | 'docs' | 'specs' | 'kblocks' | 'convos';

interface BrowseItem {
  id: string;
  path: string;
  title: string;
  category: BrowseCategory;
  preview?: string;
  modifiedAt?: Date;
  annotations?: number;
}
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+B` | Toggle file sidebar |
| `Ctrl+O` | Open browse modal |
| `Ctrl+P` | Quick file search (like VSCode) |
| `/` | Focus search in sidebar |
| `j/k` | Navigate file tree |
| `Enter` | Open selected file |
| `h/l` | Collapse/expand directory |
| `Escape` | Close modal / clear search |

## API Integration

### File Tree Data
```typescript
// Uses existing graph API
const response = await graphApi.neighbors(path);
// Returns nodes with edges for directory structure
```

### Browse Modal Data
```typescript
// New endpoint needed for exhaustive listing
interface BrowseResponse {
  items: BrowseItem[];
  total: number;
  categories: Record<BrowseCategory, number>;
}

// API: POST /agentese/concept/browse
const response = await browseApi.search({
  query: string,
  category?: BrowseCategory,
  filters?: BrowseFilters,
  limit?: number,
  offset?: number,
});
```

## Implementation Order

1. **Phase 1**: FileSidebar + FileTree (sidebar complete)
2. **Phase 2**: BrowseModal (full browser)
3. **Phase 3**: API integration for exhaustive listing
4. **Phase 4**: Keyboard shortcuts and polish

## Design Tokens

Use existing design system:
- `--steel-*` for backgrounds and borders
- `--accent-gold` for focus states
- `--space-*` for spacing
- `.input-base`, `.btn-base` for form elements
- `.modal-*` classes for modal styling

## File Structure

```
src/components/browse/
├── DESIGN.md           # This file
├── index.ts            # Exports
├── FileSidebar.tsx     # Main sidebar component
├── FileSidebar.css
├── FileTree.tsx        # Tree view component
├── FileTree.css
├── BrowseModal.tsx     # Full browser modal
├── BrowseModal.css
├── types.ts            # Shared types
└── hooks/
    ├── useFileTree.ts  # Tree state management
    └── useBrowse.ts    # Browse modal state
```
