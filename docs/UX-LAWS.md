# kgents UX Laws

> *"The file is a lie. There is only the graph."*
> *"Tasteful > feature-complete; Joy-inducing > merely functional"*

**Established**: 2025-12-25
**Status**: CONSTITUTIONAL — These laws govern all UX decisions

---

## The Three Absolutes

### 1. THE APP IS THE EDITOR

The Hypergraph Editor is not a page. It IS the application.

```
WRONG: "Open the editor page"
RIGHT: "Open kgents" → you're in the editor
```

**Implications**:
- No welcome page
- No landing page
- No onboarding flow
- App opens directly to graph/editor
- Everything else is a sidebar or panel

---

### 2. EVERYTHING MUST BE REAL

No mock data. No placeholders. No "coming soon." Wire to backend or delete.

```
WRONG: generateMockData(), await setTimeout(1000), "// TODO: Fetch from backend"
RIGHT: Fetch real data or show empty state with action
```

**Implications**:
- Example files belong in Storybook, not production
- Features that can't be wired don't ship
- Empty states are explicit, not fake-filled
- Errors surface to user, never swallowed

---

### 3. GRAPH-FIRST NAVIGATION

Navigate by clicking nodes and following edges. Not by text search.

```
WRONG: Cmd+K → search "witness" → select
RIGHT: gd (go definition), gj/gk (siblings), zo (open portal)
```

**Implications**:
- No command palette
- Help panel for discoverability (press ?)
- Edges are clickable paths
- Trail shows where you've been

---

## The Layout Law

```
┌────────────────────────────────────────────────────────────────┐
│                        HEADER                                   │
├──────────────┬─────────────────────────────┬───────────────────┤
│              │                             │                   │
│   LEFT       │         CENTER              │      RIGHT        │
│   FILES      │         GRAPH               │      CHAT         │
│   (Director) │         (Editor)            │      (Claude)     │
│              │                             │                   │
│  Collapsible │       Always visible        │    Collapsible    │
│              │                             │                   │
├──────────────┴─────────────────────────────┴───────────────────┤
│                        STATUS LINE                              │
└────────────────────────────────────────────────────────────────┘
```

- **Left sidebar**: Open files, recent nodes, document tree (like VS Code)
- **Center**: The hypergraph editor — always present
- **Right sidebar**: Chat with Claude — collapsible, context-aware

---

## The Deletion Laws

### Pages to DELETE

| Page | Reason |
|------|--------|
| `WelcomePage.tsx` | No welcome needed — app opens to editor |
| `ZeroSeedPage.tsx` | Telescope was overengineered — theory lives in specs |
| `ChartPage.tsx` | Placeholder with no real implementation |
| `ChatPage.tsx` | → Transform to right sidebar panel |
| `DirectorPage.tsx` | → Transform to left sidebar panel |
| `FeedPage.tsx` | → Optional sidebar in editor |

### Components to DELETE

| Component | Reason |
|-----------|--------|
| `CommandPalette.tsx` | Graph-first navigation, no text search |
| `useCommandRegistry.ts` | Supports deleted command palette |
| `ValueCompass/` | Theory visualization removed per Kent |
| All `*Example*.tsx` files | Examples belong in Storybook |
| All zero-seed components | Telescope deleted entirely |

### Routes to DELETE

```typescript
// DELETE these from AgenteseRouter.tsx
'void.telescope' → ZeroSeedPage  // DELETE
'world.chart' → ChartPage        // DELETE

// TRANSFORM these (remove route, embed in editor)
'self.chat' → ChatPage           // → Right sidebar
'self.director' → DirectorPage   // → Left sidebar

// KEEP
'world.document' → HypergraphEditorPage  // THE app
```

### Root Route Change

```typescript
// BEFORE
'/' → WelcomePage

// AFTER
'/' → Redirect to '/world.document' (the editor)
```

---

## The Glow Law

> "90% steel, 10% earned glow"

Glow is earned through:
- ✅ **Successful actions** (save, commit, mark created)
- ✅ **Focus states** (actively selected element)
- ✅ **Completed tasks** (checkbox checked, operation finished)

Glow is NOT earned through:
- ❌ Hover states (hover is acknowledgment, not celebration)
- ❌ Decoration (no gratuitous animation)
- ❌ Loading states (stillness, not pulse)

---

## The Realness Audit

### Must Wire to Real Backend

| Feature | Current State | Required Endpoint |
|---------|---------------|-------------------|
| Chat fork/merge | Stubbed TODO | `/api/chat/{id}/fork`, `/api/chat/{id}/merge` |
| Mention resolution | 7 types return placeholder | `/api/mentions/resolve/{type}/{value}` |
| Director upload | Console.log only | `/api/director/upload` |
| Witness stream | Random sample data | SSE from `/api/witness/stream` |

### Must Delete (No Backend)

| Feature | Reason |
|---------|--------|
| DP evaluation endpoints | Backend not implemented |
| Citizens API | SSE-only, REST stub returns empty |
| Ghost documents | UI commented out, incomplete |

---

## The Error Law

Errors must surface. Never swallow.

```typescript
// WRONG
.catch((err) => { console.error(err); })

// RIGHT
.catch((err) => {
  setError(err.message);
  toast.error('Operation failed: ' + err.message);
})
```

---

## The Magic

> "Breadth and richness of self-interfacing decision making data"

The ONE thing that must feel magical: **Every decision leaves a trace.**

- When you make a choice, it's witnessed
- When you explore, your trail is preserved
- When you edit, the derivation is tracked
- The graph KNOWS its own history

This is the soul of kgents. Everything else is frame.

---

## The Mode System

Six modes, vim-inspired:

| Mode | Entry | Purpose | Exit |
|------|-------|---------|------|
| NORMAL | Default, Esc | Read, navigate graph | — |
| INSERT | `i`, `a` | Edit content | Esc |
| COMMAND | `:` | Execute ex-commands | Enter, Esc |
| WITNESS | `gw` | Create marks | Esc |
| EDGE | `ge` | Create relationships | Esc |
| VISUAL | `v` (future) | Selection | Esc |

---

## The Help Discovery

No command palette. Help panel instead.

- Press `?` to see all keybindings
- StatusLine shows: "Press ? for help"
- NavigationSidebar has "Keyboard Shortcuts" button
- Contextual hints per mode

---

## The Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| Text search navigation | Violates graph-first | Click nodes, use g-prefix |
| Mock data in production | Violates "everything real" | Wire to backend or delete |
| Silent error handling | Users don't know failures | Surface all errors |
| Multiple pages | Violates "editor IS app" | Sidebars within editor |
| Hover glow | Glow is earned, not free | Focus/success glow only |
| Placeholder text | "Coming soon" is a lie | Empty state or nothing |

---

## Implementation Checklist

### Phase 1: Deletions (Immediate)
- [ ] Delete WelcomePage.tsx
- [ ] Delete ZeroSeedPage.tsx
- [ ] Delete ChartPage.tsx
- [ ] Delete CommandPalette.tsx
- [ ] Delete useCommandRegistry.ts
- [ ] Delete ValueCompass/ (all primitives)
- [ ] Delete all *Example*.tsx files
- [ ] Update routes: `/` → `/world.document`

### Phase 2: Transformations (This Week)
- [ ] ChatPage → Right sidebar panel in editor
- [ ] DirectorPage → Left sidebar panel in editor
- [ ] FileExplorer → Persistent left sidebar (not overlay)
- [ ] Update HypergraphEditor layout for 3-panel

### Phase 3: Make Real (Next Week)
- [ ] Wire chat fork/merge endpoints
- [ ] Wire mention resolution API
- [ ] Wire director upload
- [ ] Replace witness mock stream with real SSE
- [ ] Surface all silent errors to UI

### Phase 4: Polish (Following Week)
- [ ] Add "Press ? for help" to StatusLine
- [ ] Add keyboard shortcuts button to sidebar
- [ ] Add pending sequence display (g_, z_)
- [ ] Remove all TODO comments or implement them

---

## The Voice Test

Before any UX decision, ask:

1. **Mirror Test**: Does this feel like Kent on his best day?
2. **Graph Test**: Does this encourage graph navigation?
3. **Real Test**: Is this wired to real data?
4. **Glow Test**: Is this glow earned or decorative?
5. **Taste Test**: Is this tasteful or feature-bloat?

If any answer is "no," reconsider the decision.

---

*"The file is a lie. There is only the graph."*
*"And the graph is the app."*

---

**Filed**: 2025-12-25
**Authority**: Kent's decisions during UX interview
