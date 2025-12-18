# OS Shell: Unified Layout Wrapper and Router

**Status:** Canonical Specification
**Date:** 2025-12-17
**Prerequisites:** `projection.md`, `agentese.md`, AD-009 (Metaphysical Fullstack)
**Implementation:** `impl/claude/web/src/shell/`

---

## Epigraph

> *"The container is not chrome. It is context."*
>
> *"Navigation is not hierarchy. It is grasp."*
>
> *"The terminal never left. It just got a window."*

---

## Part I: Design Philosophy

The kgents web interface is not a collection of pages. It is an **operating system interface** for engaging in autopoiesis--the self-creating, self-maintaining process of the agent ecosystem.

### The Core Insight

Traditional web apps: Pages with routes, each designed independently.
OS Shell: A **unified container** with three persistent layers:

```
+----------------------------------------------------------------+
|  Observer Drawer (top-fixed, collapsible)                       |
|  Shows umwelt, expands to full devex richness                   |
+------------------+---------------------------------------------+
|  Navigation      |                                              |
|  Tree            |           Content Canvas                     |
|  (sidebar)       |           (route-determined)                 |
|                  |                                              |
|  - world.*       |                                              |
|  - self.*        |                                              |
|  - concept.*     |                                              |
|  - void.*        |                                              |
|  - time.*        |                                              |
+------------------+---------------------------------------------+
|  Terminal (bottom, collapsible or floating)                     |
|  Direct AGENTESE gateway interaction                            |
+----------------------------------------------------------------+
```

### What This Replaces

The current Layout.tsx is a minimal header-based navigation. OS Shell transforms it into:

1. **Tree-based semantic navigation** - Not flat links, but the AGENTESE ontology itself
2. **Observer context always visible** - Who is looking shapes what is seen
3. **Terminal integration** - CLI power in web form with persistence
4. **Projection-first rendering** - Minimal page logic, maximum delegation to primitives

---

## Part II: The Three Persistent Layers

### 2.1 Observer Drawer (Top-Fixed)

**Purpose:** Show who is observing, affecting all projections.

```
Collapsed State (40px):
+----------------------------------------------------------------+
| Observer: developer  |  Cap: [admin, write]  |  Tier: pro  | ^  |
+----------------------------------------------------------------+

Expanded State (200-400px):
+----------------------------------------------------------------+
| OBSERVER UMWELT                                             v   |
+----------------------------------------------------------------+
|  Archetype: developer     Session: abc123                       |
|  Tenant: kgents-dev       User: kent                           |
|                                                                 |
|  Capabilities                           Intent                  |
|  +------------+                         +------------------+    |
|  | admin      |                         | Exploring        |    |
|  | write      |                         | autopoiesis      |    |
|  | stream     |                         | mechanisms       |    |
|  +------------+                         +------------------+    |
|                                                                 |
|  Recent Traces                                                  |
|  +-------------------------------------------------------+     |
|  | 12:47:03 | self.memory.capture | 23ms | success      |     |
|  | 12:46:58 | world.town.manifest | 156ms | success     |     |
|  | 12:46:42 | concept.nphase.compile | 2.3s | success   |     |
|  +-------------------------------------------------------+     |
|                                                                 |
|  [ Edit Archetype ]  [ Switch Tenant ]  [ Export Session ]     |
+----------------------------------------------------------------+
```

**Key Properties:**
- Always present, never hidden
- Collapsed by default, expand on click
- Changes to observer immediately affect all projections
- Shows recent traces for devex visibility
- Provides controls to modify observer context

**Implementation:**
```typescript
interface ObserverDrawerProps {
  defaultExpanded?: boolean;
  showTraces?: boolean;
  traceLimit?: number;
}

// Observer context propagates to all children
<ObserverProvider observer={currentObserver}>
  <ObserverDrawer />
  {/* All projections receive observer from context */}
</ObserverProvider>
```

---

### 2.2 Navigation Tree (Sidebar)

**Purpose:** Navigate the AGENTESE ontology, not arbitrary routes.

The tree mirrors the five contexts. Each context expands to show registered paths:

```
AGENTESE Paths
+-------------------------------+
| world                      [-]|
|   town                        |
|     citizens                  |
|     coalitions                |
|   park                        |
|     scenarios                 |
|     masks                     |
|   garden                      |
|     plots                     |
|     seasons                   |
+-------------------------------+
| self                       [+]|
+-------------------------------+
| concept                    [+]|
+-------------------------------+
| void                       [+]|
+-------------------------------+
| time                       [+]|
+-------------------------------+

Crown Jewels (Shortcuts)
+-------------------------------+
| Brain           self.memory   |
| Gestalt         world.gestalt |
| Gardener        concept.garden|
| Atelier         world.atelier |
| Coalition       world.town    |
| Park            world.park    |
+-------------------------------+

Gallery
+-------------------------------+
| Projection Gallery            |
| Layout Gallery                |
+-------------------------------+
```

**Key Properties:**
- Tree is **auto-generated** from AGENTESE registry via `/agentese/discover`
- Crown Jewels provide shortcuts to key paths
- Current path is highlighted
- Clicking a path navigates AND invokes manifest

**Route Mapping:**
```
URL: /world/town/citizens
AGENTESE: world.town.citizens
Invokes: world.town.citizens.manifest
```

**Density Adaptation:**
- `spacious`: Full sidebar, always visible
- `comfortable`: Collapsible sidebar, toggle button
- `compact`: Hamburger menu, bottom drawer

---

### 2.3 Terminal Layer (Bottom)

**Purpose:** Direct AGENTESE gateway interaction with persistence.

```
+----------------------------------------------------------------+
| AGENTESE Terminal                                    [_][^][x] |
+----------------------------------------------------------------+
| kg> self.memory.manifest                                        |
| { "crystals": 12, "capacity": 0.67, ... }                      |
|                                                                 |
| kg> world.town.citizens | select name, phase                   |
| +----------+------------+                                       |
| | name     | phase      |                                       |
| +----------+------------+                                       |
| | Alpha    | ACTIVE     |                                       |
| | Beta     | IDLE       |                                       |
| +----------+------------+                                       |
|                                                                 |
| kg> void.entropy.sip 0.1                                        |
| [sip] Drew 0.1 from accursed share                             |
|                                                                 |
| kg> _                                                           |
+----------------------------------------------------------------+
```

**Key Features:**

1. **Full AGENTESE CLI in browser**
   - All CLI syntax supported: paths, composition (`>>`), queries (`?`), subscriptions
   - Tab completion from registry
   - History (persisted to localStorage or D-gent)

2. **Request Management**
   - History browser with search
   - Save/load request collections
   - Export session to shareable format

3. **Discovery Tools**
   - `?world.*` - Query available paths
   - `help <path>` - Show path documentation
   - `affordances <path>` - List available aspects

4. **Persistence** (web advantage over CLI)
   - Session history survives refresh
   - Collections persist across sessions
   - Sync across devices (when authenticated)

**Density Adaptation:**
- `spacious`: Docked at bottom, resizable height
- `comfortable`: Collapsed to single input line, expand on focus
- `compact`: Floating action button, full-screen modal on tap

---

## Part III: Projection-First Rendering

### The Principle

> *"Business logic in pages is debt. Projection is payment."*

Current pages contain significant rendering logic. OS Shell inverts this:

1. **Shell provides context** (observer, density, layout)
2. **Route determines path** (URL -> AGENTESE path)
3. **Gateway provides data** (invoke path.manifest)
4. **Primitives render** (Gallery components project data)

### Minimal Page Pattern

```typescript
// Before: Page with embedded logic
export default function TownPage() {
  const [citizens, setCitizens] = useState([]);
  const [loading, setLoading] = useState(true);
  // ... 200 lines of fetch, state, handlers ...
  return <ComplexTownLayout citizens={citizens} ... />;
}

// After: Projection passthrough
export default function TownPage() {
  return (
    <PathProjection path="world.town" aspect="manifest">
      {(data, { density, observer }) => (
        <TownVisualization data={data} density={density} />
      )}
    </PathProjection>
  );
}
```

### The PathProjection Component

```typescript
interface PathProjectionProps {
  path: string;                    // AGENTESE path
  aspect?: string;                 // Default: "manifest"
  children: (
    data: unknown,
    context: ProjectionContext
  ) => ReactNode;
}

interface ProjectionContext {
  density: Density;
  observer: Observer;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
  stream: boolean;                 // Whether streaming is active
}
```

### Content Canvas Routing

The canvas area routes based on AGENTESE paths:

```typescript
// Route structure maps to AGENTESE
<Routes>
  {/* Dynamic AGENTESE routing */}
  <Route path="/:context/:holon/*" element={<DynamicProjection />} />

  {/* Gallery routes (special cases) */}
  <Route path="/gallery" element={<GalleryPage />} />
  <Route path="/gallery/layout" element={<LayoutGallery />} />

  {/* Fallback */}
  <Route path="*" element={<NotFound />} />
</Routes>
```

---

## Part IV: Gallery Primitive Reliance

### The Mandate

> *"If it renders, it should be in the Gallery."*

All visualization components must:
1. Exist in `/gallery` primitives first
2. Be demonstrated with Pilots
3. Accept density and render appropriately
4. Project from widget state, not page logic

### Crown Jewel Projections

Each Crown Jewel's visualization is a composition of Gallery primitives:

| Jewel | Primary Primitive | Supporting Primitives |
|-------|-------------------|----------------------|
| Brain | CrystalVine, OrganicCrystal | GraphWidget, TableWidget |
| Gestalt | OrganicNode, VineEdge | GraphWidget, FilterPanel |
| Gardener | GardenVisualization | SeasonIndicator, PlotCard |
| Atelier | ArtisanGrid, PieceCard | StreamWidget, LineageTree |
| Coalition | Mesa, CitizenPanel | TableWidget, GraphWidget |
| Park | PhaseTransition, MaskSelector | ConsentMeter, TimerDisplay |

### Procedural Enhancement

Additional styling (colors, animations) for consumer-facing versions follow specs:

```typescript
// Base primitive (from Gallery)
<OrganicNode data={node} density={density} />

// Enhanced for production (procedural from spec)
<OrganicNode
  data={node}
  density={density}
  colorMap={JEWEL_COLORS.gestalt}    // From visual-system.md
  animation={breathing}               // From motion-language.md
  personality={gestalt.personality}   // From philosophy.md
/>
```

---

## Part V: Observer Umwelt Integration

### Observer-Dependent Projections

The Observer Drawer doesn't just display context--it **shapes all projections**:

```typescript
// Different observers see different content
const { observer } = useObserver();

// Developer sees debug information
if (observer.archetype === 'developer') {
  return <DebugProjection data={data} />;
}

// Operator sees operational metrics
if (observer.archetype === 'operator') {
  return <OpsProjection data={data} />;
}

// Guest sees simplified view
return <GuestProjection data={data} />;
```

### Capability-Based Affordances

Observer capabilities determine available actions:

```typescript
const { capabilities } = useObserver();

// Only show edit button if observer can write
{capabilities.has('write') && (
  <Button onClick={handleEdit}>Edit</Button>
)}

// Only show admin panel if observer is admin
{capabilities.has('admin') && (
  <AdminPanel />
)}
```

### Trace Visibility

The Observer Drawer shows recent AGENTESE invocations:

```typescript
interface Trace {
  timestamp: Date;
  path: string;
  aspect: string;
  duration: number;
  status: 'success' | 'error' | 'refused';
  result?: unknown;
  error?: string;
}

// Traces are collected from all PathProjection invocations
const { traces } = useTraces({ limit: 50 });
```

---

## Part VI: Terminal Service

### Architecture

The terminal is not just a UI--it's a **service** with web architecture benefits:

```
+------------------+     +------------------+     +------------------+
|  Terminal UI     | --> |  Terminal        | --> |  AGENTESE        |
|  (React)         |     |  Service         |     |  Gateway         |
+------------------+     +------------------+     +------------------+
                               |
                               v
                         +------------------+
                         |  Persistence     |
                         |  (localStorage/  |
                         |   IndexedDB/     |
                         |   D-gent)        |
                         +------------------+
```

### Terminal Service API

```typescript
interface TerminalService {
  // Execution
  execute(input: string): Promise<ExecutionResult>;
  stream(input: string): AsyncIterator<ExecutionChunk>;

  // History
  history: HistoryEntry[];
  searchHistory(query: string): HistoryEntry[];
  clearHistory(): void;

  // Collections
  collections: Collection[];
  saveToCollection(name: string, entries: HistoryEntry[]): void;
  loadCollection(name: string): HistoryEntry[];

  // Discovery
  discover(context?: string): Promise<PathInfo[]>;
  affordances(path: string): Promise<string[]>;
  help(path: string): Promise<HelpInfo>;

  // Completion
  complete(partial: string): Promise<string[]>;
}
```

### Input Grammar

Full AGENTESE CLI grammar in browser:

```
# Invocation
self.memory.manifest
world.town.citizens

# Composition
world.doc.manifest >> concept.summary.refine >> self.memory.engram

# Query
?world.*
?self.memory.?

# Subscription
subscribe self.forest.*

# Aliases
alias me self.soul
me.challenge

# Flags
self.forest.manifest --json
world.town.manifest --trace

# Pipeline operators (future)
world.town.citizens | select name, phase | sort phase
```

### Persistence Layers

```typescript
// Layer 1: Session (survives refresh)
sessionStorage.setItem('terminal-history', JSON.stringify(history));

// Layer 2: Local (survives close)
localStorage.setItem('terminal-collections', JSON.stringify(collections));

// Layer 3: Remote (survives device)
await dgent.store('terminal', { history, collections, aliases });
```

---

## Part VII: Density Adaptation

### The Three Modes

Following AD-008 (Simplifying Isomorphisms), OS Shell adapts to three densities:

#### Spacious (>1024px)

```
+----------------------------------------------------------------+
| Observer Drawer (collapsed, 40px)                               |
+------------------+---------------------------------------------+
| Navigation Tree  |                                              |
| (280px, fixed)   |          Content Canvas                     |
|                  |                                              |
+------------------+---------------------------------------------+
| Terminal (docked, 200px, resizable)                             |
+----------------------------------------------------------------+
```

#### Comfortable (768-1024px)

```
+----------------------------------------------------------------+
| Observer Drawer (collapsed, 40px)                               |
+--+-------------------------------------------------------------+
|  |                                                              |
|  |                    Content Canvas                            |
|  |                                                              |
+--+-------------------------------------------------------------+
| Terminal (collapsed to input line)                              |
+----------------------------------------------------------------+

[Sidebar toggle floats at left edge]
```

#### Compact (<768px)

```
+----------------------------------------------------------------+
| Observer (icon only)                              [nav] [term]  |
+----------------------------------------------------------------+
|                                                                 |
|                                                                 |
|                     Content Canvas                              |
|                     (full viewport)                             |
|                                                                 |
|                                                                 |
+----------------------------------------------------------------+

[nav] -> Bottom drawer with navigation tree
[term] -> Full-screen terminal modal
```

---

## Part VIII: No Emojis Policy

### The Rule

> *"Emojis in copy are garnish. kgents is the main course."*

All text content in kgents web interfaces excludes emojis:

```typescript
// Before
<NavLink icon="🧠" label="Brain" />

// After
<NavLink icon={<BrainIcon />} label="Brain" />
```

**Exceptions:**
1. User-generated content (users may use emojis)
2. Explicit personality moments (loading states, celebrations)
3. Data display where emojis are part of the data

**Implementation:**
- Replace JEWEL_EMOJI with JEWEL_ICONS (Lucide icons)
- Update PersonalityLoading to use icons or glyphs
- Audit all components for emoji usage

```typescript
// Updated JEWEL_INFO
const JEWEL_INFO = {
  brain:     { icon: Brain,     color: 'text-cyan-500' },
  gestalt:   { icon: Network,   color: 'text-green-500' },
  gardener:  { icon: Leaf,      color: 'text-lime-500' },
  atelier:   { icon: Palette,   color: 'text-amber-500' },
  coalition: { icon: Users,     color: 'text-violet-500' },
  park:      { icon: Theater,   color: 'text-pink-500' },
  domain:    { icon: Building,  color: 'text-red-500' },
} as const;
```

---

## Part IX: Implementation Plan

### Phase 1: Shell Foundation

1. Create `shell/` directory structure
2. Implement ShellProvider (density, observer context)
3. Build ObserverDrawer component
4. Build NavigationTree component (auto-discovery)

### Phase 2: Terminal Integration

1. Implement TerminalService
2. Build Terminal UI component
3. Add history persistence
4. Add tab completion

### Phase 3: Projection Refactor

1. Create PathProjection component
2. Refactor existing pages to use PathProjection
3. Ensure all visualizations are Gallery-sourced
4. Remove page-level business logic

### Phase 4: Polish

1. Density adaptation testing
2. Emoji audit and removal
3. Observer drawer devex features
4. Terminal collections and export

---

## Part X: Anti-Patterns

| Anti-Pattern | Why Bad | Correct Pattern |
|--------------|---------|-----------------|
| Page with fetch logic | Business logic in presentation | PathProjection with gateway |
| Custom visualization not in Gallery | Breaks primitive reliance | Add to Gallery first |
| Hardcoded navigation | Doesn't reflect registry | Auto-discover from gateway |
| Emojis in copy | Violates style policy | Icons or text only |
| Observer hidden in headers | Not visible, not interactive | Persistent drawer |
| Terminal as afterthought | Loses power user capability | First-class citizen |

---

## Part XI: Success Criteria

### Quantitative

| Metric | Target |
|--------|--------|
| Page LOC (average) | <50 lines |
| Gallery primitive coverage | 100% of visualizations |
| Navigation paths auto-discovered | 100% |
| Terminal commands working | All AGENTESE grammar |

### Qualitative

- [ ] Opening any route shows Observer Drawer context
- [ ] Navigation tree reflects actual registry state
- [ ] Terminal works offline (cached discovery)
- [ ] Density adaptation feels natural, not broken
- [ ] No emojis in kgents-authored copy
- [ ] Power users feel "at home" in terminal
- [ ] New users can discover features via navigation tree

---

## Appendix A: Directory Structure

```
impl/claude/web/src/
  shell/
    ShellProvider.tsx       # Context for density, observer
    ObserverDrawer.tsx      # Top-fixed observer context
    NavigationTree.tsx      # Sidebar tree navigation
    Terminal.tsx            # Bottom terminal UI
    TerminalService.ts      # Terminal logic and persistence
    PathProjection.tsx      # Generic path->projection wrapper
    DynamicProjection.tsx   # Route-based projection
    index.ts                # Exports
  components/
    elastic/                # Existing elastic primitives
    gallery/                # Existing gallery components
    ...
  pages/
    ...                     # Simplified projection passthroughs
```

---

## Appendix B: Migration from Current Layout

### Before (Layout.tsx)

```tsx
export function Layout() {
  return (
    <div>
      <header>
        {/* Flat navigation links */}
        <NavLink to="/brain" ... />
        <NavLink to="/gestalt" ... />
        ...
      </header>
      <main><Outlet /></main>
      <footer>...</footer>
    </div>
  );
}
```

### After (Shell.tsx)

```tsx
export function Shell() {
  return (
    <ShellProvider>
      <div className="h-screen flex flex-col">
        <ObserverDrawer />
        <div className="flex-1 flex">
          <NavigationTree />
          <main className="flex-1">
            <Outlet />
          </main>
        </div>
        <Terminal />
      </div>
    </ShellProvider>
  );
}
```

---

*"The shell is not a frame. It is the ground from which the garden grows."*

*Last updated: 2025-12-17*
