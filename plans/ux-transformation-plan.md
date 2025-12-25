# UX Radical Transformation Plan

> *"Hypergraph Editor IS the app. Everything else is a sidebar."*

**Date**: 2025-12-25
**Status**: READY FOR EXECUTION
**Authority**: Kent's UX interview decisions

---

## Executive Summary

Transform kgents from a multi-page app into a single unified editor experience.

| Metric | Before | After |
|--------|--------|-------|
| Pages | 8 | 1 (+ NotFound) |
| Routes | 12+ | 2 |
| Mock data files | 19 | 0 |
| Command palette | Yes | Deleted |
| ValueCompass | 6 files | Deleted |
| Zero-Seed | 15+ files | Deleted |

---

## Phase 1: The Purge (Day 1)

### 1.1 Delete Pages

```bash
# Delete these page files
rm impl/claude/web/src/pages/WelcomePage.tsx
rm impl/claude/web/src/pages/WelcomePage.css
rm impl/claude/web/src/pages/ZeroSeedPage.tsx
rm impl/claude/web/src/pages/ChartPage.tsx

# If ValueCompassTestPage exists
rm impl/claude/web/src/pages/ValueCompassTestPage.tsx
```

### 1.2 Delete Command Palette

```bash
rm impl/claude/web/src/hypergraph/CommandPalette.tsx
rm impl/claude/web/src/hypergraph/useCommandRegistry.ts
```

**Modify HypergraphEditor.tsx:**
- Remove import for CommandPalette
- Remove `commandPaletteOpen` state
- Remove `onOpenCommandPalette` callback
- Remove `<CommandPalette />` component

**Modify useKeyHandler.ts:**
- Remove `Cmd+K` binding (lines 105-110)
- Remove `OPEN_COMMAND_PALETTE` action type
- Remove `onOpenCommandPalette` from callbacks

### 1.3 Delete ValueCompass (Kent said delete)

```bash
rm -rf impl/claude/web/src/primitives/ValueCompass/
```

### 1.4 Delete Zero-Seed (Kent said delete entirely)

```bash
rm -rf impl/claude/web/src/components/zero-seed/
rm -rf impl/claude/web/src/constructions/ZeroSeedExplorer/
```

### 1.5 Delete Example Files

```bash
# In primitives/
rm impl/claude/web/src/primitives/Trail/TrailExample.tsx
rm impl/claude/web/src/primitives/Witness/WitnessExample.tsx

# In constructions/
rm impl/claude/web/src/constructions/ChatSession/EXAMPLE_USAGE.tsx
rm impl/claude/web/src/constructions/DirectorView/DirectorViewExample.tsx

# In components/
rm impl/claude/web/src/components/dp/example.tsx
rm impl/claude/web/src/components/welcome/WitnessStream.tsx  # Mock data generator
```

### 1.6 Update Router

**Modify AgenteseRouter.tsx:**

```typescript
// DELETE these route mappings
// 'void.telescope' → ZeroSeedPage
// 'world.chart' → ChartPage

// DELETE these lazy imports
// const ChartPage = React.lazy(...)
// const ZeroSeedPage = React.lazy(...)
// const WelcomePage = React.lazy(...)

// CHANGE root route
// FROM: '/' → WelcomePage
// TO: '/' → Navigate to '/world.document'

// Add redirect
<Route path="/" element={<Navigate to="/world.document" replace />} />
```

---

## Phase 2: The Layout Transformation (Day 2-3)

### 2.1 Add Right Sidebar for Chat

**Create new file: `impl/claude/web/src/hypergraph/ChatSidebar.tsx`**

```typescript
// Wrapper around ChatPanel with collapse/expand
// Position: right side of editor
// Toggle: keyboard shortcut or button
// State: controlled by parent HypergraphEditor
```

**Modify HypergraphEditor.tsx:**

```typescript
// Add state
const [chatSidebarOpen, setChatSidebarOpen] = useState(false);

// Add to layout (after proof panel)
{chatSidebarOpen && (
  <ChatSidebar
    onClose={() => setChatSidebarOpen(false)}
  />
)}
```

### 2.2 Transform FileExplorer to Persistent Left Sidebar

**Current state:** FileExplorer shows as fullscreen overlay when no file open

**Target state:** FileExplorer is always-visible left sidebar (like VS Code)

**Modify HypergraphEditorPage.tsx:**
- Wrap HypergraphEditor in a flex container
- Add FileExplorer as left panel (collapsible)

**Modify HypergraphEditor.css:**
```css
.hypergraph-editor__layout {
  display: flex;
  height: 100%;
}

.hypergraph-editor__files-sidebar {
  width: 240px;
  flex-shrink: 0;
  border-right: 1px solid var(--steel-gunmetal);
}

.hypergraph-editor__files-sidebar--collapsed {
  width: 0;
  overflow: hidden;
}

.hypergraph-editor__main {
  flex: 1;
  min-width: 0;
}

.hypergraph-editor__chat-sidebar {
  width: 320px;
  flex-shrink: 0;
  border-left: 1px solid var(--steel-gunmetal);
}
```

### 2.3 Add Keybindings for Sidebars

**Add to useKeyHandler.ts NORMAL_BINDINGS:**

```typescript
{
  keys: ['b'],
  modifiers: { ctrl: true },
  action: 'TOGGLE_FILES_SIDEBAR',
  description: 'Toggle files sidebar',
},
{
  keys: ['j'],
  modifiers: { ctrl: true },
  action: 'TOGGLE_CHAT_SIDEBAR',
  description: 'Toggle chat sidebar',
},
```

---

## Phase 3: Make Everything Real (Day 4-5)

### 3.1 Wire Chat Branching (CRITICAL)

**File:** `impl/claude/web/src/components/chat/useBranching.ts`
**Also:** `impl/claude/web/src/primitives/Conversation/useBranching.ts`

**Current:** Returns stub implementations with TODO comments

**Required endpoints:**
- `POST /api/chat/{session_id}/fork`
- `POST /api/chat/{session_id}/merge`

**Action:** Either implement backend endpoints OR remove branching UI

### 3.2 Wire Mention Resolution (CRITICAL)

**File:** `impl/claude/web/src/components/chat/useMentions.ts`

**Current:** 7 mention types return `"// TODO: Fetch from backend"`

**Required endpoint:**
- `GET /api/mentions/resolve/{type}/{value}`

**Types to wire:** file, symbol, spec, witness, web, terminal, project

**Action:** Implement backend OR simplify to only file/spec mentions

### 3.3 Wire Director Upload

**File:** `impl/claude/web/src/constructions/DirectorView/DirectorViewExample.tsx`

**Current:** `console.log(files)` only

**Required endpoint:**
- `POST /api/director/upload`

**Action:** Implement backend endpoint

### 3.4 Surface Silent Errors

**Files with silent catch blocks:**
- `impl/claude/web/src/components/director/DocumentDetail.tsx`
- `impl/claude/web/src/hooks/useLoss.ts`
- `impl/claude/web/src/services/documentCache/documentCache.ts`

**Pattern to fix:**
```typescript
// BEFORE
.catch((err) => { console.error(err); })

// AFTER
.catch((err) => {
  setError(err.message);
  // Or use toast notification
})
```

### 3.5 Remove Remaining Mock Data

**Files to audit:**
- `impl/claude/web/src/constants/messages.ts` - EMPTY_STATE_MESSAGES
- Any remaining `generateMock*` functions
- Any `setTimeout` used to fake API latency

---

## Phase 4: Help Discoverability (Day 6)

### 4.1 Add Help Hint to StatusLine

**Modify StatusLine.tsx:**

```typescript
// Add to status display
<span className="status-line__help-hint">
  Press ? for help
</span>
```

### 4.2 Add Pending Sequence Display

**Modify StatusLine.tsx:**

When user presses `g` and is waiting for next key, show `g_` in status.

```typescript
{pendingSequence && (
  <span className="status-line__pending">
    {pendingSequence.join('')}_
  </span>
)}
```

### 4.3 Add Keyboard Shortcuts Button to Sidebar

**Modify NavigationSidebar.tsx:**

```typescript
<button onClick={() => setHelpOpen(true)}>
  Keyboard Shortcuts
</button>
```

---

## Phase 5: Cleanup & Polish (Day 7)

### 5.1 Remove Dead Imports

Run TypeScript to find broken imports after deletions:
```bash
cd impl/claude/web && npm run typecheck
```

Fix all errors.

### 5.2 Remove Unused Routes

Audit all legacy redirects in AgenteseRouter.tsx:
- `/brain` → Remove
- `/chat` → Remove (chat is sidebar now)
- `/director` → Remove (director is sidebar now)
- `/chart` → Remove
- `/proof-engine` → Remove
- `/zero-seed` → Remove

Keep only:
- `/` → `/world.document`
- `/world.document` → HypergraphEditorPage
- `/*` → NotFound

### 5.3 Final Type Check

```bash
cd impl/claude/web
npm run typecheck
npm run lint
npm run build
```

---

## File-by-File Deletion Checklist

### Pages (DELETE)
- [ ] `pages/WelcomePage.tsx`
- [ ] `pages/WelcomePage.css`
- [ ] `pages/ZeroSeedPage.tsx`
- [ ] `pages/ChartPage.tsx`
- [ ] `pages/ValueCompassTestPage.tsx` (if exists)

### Components (DELETE)
- [ ] `hypergraph/CommandPalette.tsx`
- [ ] `hypergraph/useCommandRegistry.ts`
- [ ] `components/zero-seed/*` (entire folder)
- [ ] `primitives/ValueCompass/*` (entire folder)
- [ ] `constructions/ZeroSeedExplorer/*` (entire folder)

### Examples (DELETE)
- [ ] `primitives/Trail/TrailExample.tsx`
- [ ] `primitives/Witness/WitnessExample.tsx`
- [ ] `constructions/ChatSession/EXAMPLE_USAGE.tsx`
- [ ] `constructions/DirectorView/DirectorViewExample.tsx`
- [ ] `components/dp/example.tsx`
- [ ] `components/welcome/WitnessStream.tsx`

### Router (MODIFY)
- [ ] Remove void.telescope mapping
- [ ] Remove world.chart mapping
- [ ] Remove WelcomePage lazy import
- [ ] Change `/` to redirect to `/world.document`
- [ ] Remove legacy redirects

### Editor (MODIFY)
- [ ] Remove CommandPalette import
- [ ] Remove commandPaletteOpen state
- [ ] Add ChatSidebar component
- [ ] Add sidebar toggle keybindings
- [ ] Update layout CSS for 3-panel

---

## Success Criteria

### Quantitative
- [ ] Only 2 routes exist (`/world.document`, `/*`)
- [ ] 0 mock data generators in production code
- [ ] 0 TODO comments for API wiring
- [ ] TypeScript compiles with 0 errors
- [ ] Build succeeds

### Qualitative
- [ ] App opens directly to editor (no welcome)
- [ ] Chat is a sidebar, not a page
- [ ] Files are a sidebar, not a page
- [ ] No command palette (? for help instead)
- [ ] All errors surface to user
- [ ] Graph-first navigation works smoothly

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking imports after deletion | Run typecheck after each phase |
| Chat sidebar breaks existing chat | Keep ChatPanel component, wrap in sidebar |
| FileExplorer layout issues | Test collapsible behavior thoroughly |
| Missing backend endpoints | Document which features are blocked |
| Losing useful functionality | Review each deletion before executing |

---

## Rollback Plan

Before starting, create a git branch:
```bash
git checkout -b ux-transformation-backup
git checkout main
git checkout -b ux-transformation
```

If transformation fails, reset:
```bash
git checkout main
git branch -D ux-transformation
```

---

## Execution Order

1. **Backup** (git branch)
2. **Phase 1** (deletions) → typecheck
3. **Phase 2** (layout) → typecheck
4. **Phase 3** (make real) → manual test
5. **Phase 4** (help) → typecheck
6. **Phase 5** (polish) → full test
7. **Commit** with message documenting transformation

---

*"The editor IS the app. Everything else is a sidebar. Everything is real."*

**Filed**: 2025-12-25
**Estimated Duration**: 7 days
**Dependencies**: Backend endpoints for chat fork/merge, mentions, upload
