# Umwelt v2: Observer Reality Expansion

> *"The noun is a lie. There is only the rate of change."*
>
> *"Different observers don't just have different permissions—they have different perceptions."*

**Status**: 🌱 PLANNING
**Parent**: `plans/umwelt-visualization.md` (✅ COMPLETE)
**Last Updated**: 2025-12-19
**Priority**: P1 (Educational UX, AD-010 Layer 3)
**Aligned With**: AD-008 (Simplifying Isomorphisms), AD-010 (Habitat Guarantee), AD-012 (Aspect Projection Protocol)

---

## The Philosophical Deepening

### What We Built (v1)

Umwelt v1 answered: *"How do we visualize observer switches?"*

- Subtle ripple effect
- Aspect reveal/hide animations
- Toast notifications
- Density-aware behavior
- Reduced motion support

### What We're Expanding (v2)

Umwelt v2 asks deeper questions:

1. **Correctness**: Are we showing the *truth* about capabilities, or heuristics?
2. **Education**: Do users understand *why* they see what they see?
3. **Exploration**: Can users *discover* capabilities they don't have?
4. **Integration**: Does the observer system feel native to AGENTESE?

---

## Part I: Robustification (Correctness)

### 1A. Registry-Backed Capability Resolution

**The Problem**

Current capability checking uses heuristics:

```typescript
// Current: String pattern matching
function getRequiredCapability(aspect: string): string | null {
  if (['create', 'update', 'delete'].some((m) => aspect.includes(m))) {
    return 'write';
  }
  if (aspect.includes('admin') || aspect.includes('govern')) {
    return 'admin';
  }
  // ...
}
```

This creates **silent lies**:
- An aspect named `createIdea` requires write, but `creativeManifest` doesn't
- An aspect named `administrator` requires admin, but `governanceView` might not
- Edge cases multiply as the system grows

**The Solution**

Capabilities should come from the registry, not inference:

```python
# Backend: Declare capability requirements on @aspect
@aspect(
    category=AspectCategory.MUTATION,
    effects=[Effect.WRITES("citizens")],
    required_capability="write",  # NEW: Explicit declaration
)
async def create(self, observer: Observer, **kwargs):
    ...
```

```typescript
// Frontend: Use registry truth
interface AspectMetadata {
  name: string;
  category: string;
  requiredCapability: string | null;  // From registry
  effects: string[];
}

// Discovery endpoint enhancement
GET /agentese/discover?include_aspect_metadata=true

{
  "paths": [...],
  "metadata": {
    "world.town": {
      "aspects": ["manifest", "create", "polynomial"],
      "aspectMetadata": {
        "manifest": { "requiredCapability": null, "category": "perception" },
        "create": { "requiredCapability": "write", "category": "mutation" },
        "polynomial": { "requiredCapability": null, "category": "introspection" }
      }
    }
  }
}
```

**Tasks**

- [ ] Add `required_capability` to `@aspect` decorator
- [ ] Enhance `/agentese/discover` to return per-aspect metadata
- [ ] Update `useAgenteseDiscovery.ts` to parse aspect metadata
- [ ] Update `getRequiredCapability()` to use registry with heuristic fallback
- [ ] Add tests for edge cases (aspect names that fool heuristics)

**Open Questions**

1. **Should capability requirements cascade?** If a path requires `admin`, do all its aspects inherit that requirement?
2. **How do we handle compound capabilities?** e.g., `["write", "void"]` for an aspect that writes AND uses entropy?
3. **Migration path**: How do we update existing `@aspect` decorators without breaking changes?

---

### 1B. Contract-Aware Aspect Display

**The Problem**

`hasContract: false` is hardcoded in `getVisibleAspects()`:

```typescript
result.push({
  aspect,
  path,
  requiredCapability,
  hasContract: false,  // TODO: Always false!
  isStreaming: pathMeta.effects?.includes('streaming') ?? false,
});
```

This means ghost tooltips can't show schema previews, and users can't see what data shape they'd get if they upgraded.

**The Solution**

Wire contract metadata through the diff:

```typescript
interface AspectInfo {
  aspect: string;
  path: string;
  requiredCapability: string | null;

  // Contract awareness
  hasContract: boolean;
  contractType: 'response' | 'request-response' | 'streaming' | null;
  schemaPreview?: {
    request?: JsonSchema;
    response?: JsonSchema;
  };

  isStreaming: boolean;
}

// In getVisibleAspects
function getVisibleAspects(
  observer: Observer,
  metadata: Record<string, PathMetadata>,
  schemas: Record<string, Record<string, AspectSchema>>
): AspectInfo[] {
  // ...
  const aspectSchema = schemas[path]?.[aspect];
  result.push({
    // ...
    hasContract: aspectSchema !== undefined,
    contractType: inferContractType(aspectSchema),
    schemaPreview: aspectSchema ? {
      request: aspectSchema.request?.schema,
      response: aspectSchema.response?.schema,
    } : undefined,
  });
}
```

**Tasks**

- [ ] Thread `schemas` through to `computeUmweltDiff()`
- [ ] Populate `hasContract`, `contractType`, `schemaPreview`
- [ ] Add schema badge to AspectPanel buttons
- [ ] Show schema preview in ghost tooltips

**Open Questions**

1. **Schema preview size**: Full JSON Schema can be huge. What's the right truncation?
2. **Example values**: Should ghost tooltips show example payloads from the schema?
3. **Streaming contracts**: How do we represent `AsyncIterator[Chunk]` in the preview?

---

### 1C. Observer Session Persistence

**The Problem**

Observer choice resets on page refresh. Users lose context.

**The Solution**

Persist to `sessionStorage` with graceful migration:

```typescript
// hooks/useObserverPersistence.ts
const STORAGE_KEY = 'umwelt:observer';
const STORAGE_VERSION = 1;

interface StoredObserver {
  version: number;
  observer: Observer;
  timestamp: number;
}

export function useObserverPersistence(defaultObserver: Observer) {
  const [observer, setObserverState] = useState<Observer>(() => {
    try {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed: StoredObserver = JSON.parse(stored);
        // Version migration
        if (parsed.version === STORAGE_VERSION) {
          return parsed.observer;
        }
        // Old version: clear and use default
        sessionStorage.removeItem(STORAGE_KEY);
      }
    } catch {
      // Corrupted: clear and use default
      sessionStorage.removeItem(STORAGE_KEY);
    }
    return defaultObserver;
  });

  const setObserver = useCallback((o: Observer) => {
    setObserverState(o);
    const toStore: StoredObserver = {
      version: STORAGE_VERSION,
      observer: o,
      timestamp: Date.now(),
    };
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(toStore));
  }, []);

  return [observer, setObserver] as const;
}
```

**Tasks**

- [ ] Create `useObserverPersistence.ts` hook
- [ ] Wire into `AgenteseDocs.tsx`
- [ ] Add version migration logic
- [ ] Test: corrupted storage, old version, fresh session

**Open Questions**

1. **Scope**: `sessionStorage` (per-tab) or `localStorage` (persistent)?
2. **Multi-tab**: Should switching observer in one tab affect others?
3. **Reset**: Should there be a "Reset to default" action?

---

## Part II: Educational Enhancements

### 2A. PathExplorer Accessibility Dimming

**The Insight**

Paths don't change visibility with observer, but their *utility* does. A guest looking at `world.admin` should see it dimmed because all its useful aspects require elevated capabilities.

**The Pattern**

```typescript
type PathAccessibility = 'full' | 'partial' | 'ghost';

function computePathAccessibility(
  path: string,
  metadata: PathMetadata,
  observer: Observer
): PathAccessibility {
  const aspects = metadata.aspects || ['manifest'];
  const accessible = aspects.filter(
    a => isAspectAvailable(a, observer).available
  );

  if (accessible.length === 0) return 'ghost';
  if (accessible.length < aspects.length) return 'partial';
  return 'full';
}

// In PathExplorer
<PathItem
  className={clsx(
    'transition-opacity duration-200',
    {
      'opacity-100': accessibility === 'full',
      'opacity-70 border-l-yellow-500/30': accessibility === 'partial',
      'opacity-40 italic': accessibility === 'ghost',
    }
  )}
>
  {accessibility === 'partial' && (
    <Tooltip content={`${accessibleCount}/${totalCount} aspects available`}>
      <PartialBadge />
    </Tooltip>
  )}
</PathItem>
```

**The Animation**

When observer changes, paths should subtly shift opacity with stagger:

```typescript
// Stagger by path depth in the tree
const staggerDelay = pathDepth * 20; // ms
```

**Tasks**

- [ ] Add `computePathAccessibility()` to `useUmweltDiff.ts`
- [ ] Pass observer to `PathExplorer.tsx`
- [ ] Add opacity + border styling for partial/ghost
- [ ] Add staggered animation on observer change
- [ ] Add tooltip showing accessible aspect count

**Open Questions**

1. **Partial threshold**: At what point is a path "partial" vs "ghost"? 50%? Any inaccessible?
2. **Ghost interaction**: Should ghost paths still be clickable (revealing ghost aspects)?
3. **Visual weight**: Does dimming make the tree feel broken? Test with real users.

---

### 2B. Capability Radar Visualization (Spacious Mode)

**The Vision**

A radial chart showing the capability *shape* of an observer:

```
              admin ●───●───●
             ╱              ╲
       govern ●              ● void
             │               │
        write ●───────────────● collaborate
             ╲              ╱
               read ●───●
                    ▲
                current observer (developer)
```

**Implementation Sketch**

```typescript
// components/docs/umwelt/CapabilityRadar.tsx
import { ResponsiveRadar } from '@nivo/radar';

const CAPABILITY_AXES = [
  { key: 'read', label: 'Read' },
  { key: 'write', label: 'Write' },
  { key: 'admin', label: 'Admin' },
  { key: 'govern', label: 'Govern' },
  { key: 'void', label: 'Void' },
  { key: 'collaborate', label: 'Collaborate' },
];

export function CapabilityRadar({ observer, pathRequirements }: Props) {
  const observerData = CAPABILITY_AXES.map(axis => ({
    axis: axis.label,
    value: observer.capabilities.includes(axis.key) ? 1 : 0,
  }));

  const requiredData = CAPABILITY_AXES.map(axis => ({
    axis: axis.label,
    value: pathRequirements.includes(axis.key) ? 1 : 0,
  }));

  return (
    <ResponsiveRadar
      data={[
        { id: 'You', ...observerData },
        { id: 'Required', ...requiredData },
      ]}
      colors={[observerColor, 'rgba(255,100,100,0.3)']}
      borderWidth={2}
      dotSize={8}
    />
  );
}
```

**When to Show**

- Only in `spacious` density mode
- When a path is selected AND has capability-gated aspects
- In the AspectPanel header or as a toggle

**Tasks**

- [ ] Install `@nivo/radar` or build custom SVG radar
- [ ] Create `CapabilityRadar.tsx` component
- [ ] Integrate into AspectPanel for spacious mode
- [ ] Add toggle for users who find it distracting
- [ ] Animate capability fill on observer change

**Open Questions**

1. **Information density**: Is this too much for the panel? Maybe a modal?
2. **Path-specific vs global**: Show overall observer shape, or shape relative to current path?
3. **Teaching mode only?** Maybe this is only for `TeachingMode: enabled`?

---

### 2C. Ghost Aspect Interaction (AD-010 Layer 3)

**The Philosophy**

> *"The paths not taken are as important as the path taken."*

Ghost aspects shouldn't just be grayed—they should be **explorable**. This is Différance made visible: presence defined by absence.

**Interaction Design**

```
┌────────────────────────────────────────┐
│ [🔒 create]  Ghost Aspect              │
├────────────────────────────────────────┤
│ This aspect requires WRITE capability. │
│                                        │
│ Available to:                          │
│   • User (write)                       │
│   • Developer (write, admin)           │
│   • Mayor (write, admin, govern)       │
│                                        │
│ [Preview as Developer]                 │
│                                        │
│ Schema preview:                        │
│ ┌──────────────────────────────────┐   │
│ │ request: { name: string }        │   │
│ │ response: { id: string, ... }    │   │
│ └──────────────────────────────────┘   │
└────────────────────────────────────────┘
```

**"Preview As" Feature**

Temporarily view the UI as if you had a different observer:

```typescript
interface UmweltContextValue {
  // ... existing

  // NEW: Preview mode
  previewObserver: Observer | null;
  setPreviewObserver: (o: Observer | null) => void;

  // Effective observer (preview || actual)
  effectiveObserver: Observer;
}

// Usage in components
const { effectiveObserver, previewObserver } = useUmwelt();

// Show preview banner
{previewObserver && (
  <PreviewBanner>
    Previewing as {previewObserver.archetype}
    <button onClick={() => setPreviewObserver(null)}>Exit Preview</button>
  </PreviewBanner>
)}
```

**Tasks**

- [ ] Design ghost tooltip component with capability pathway
- [ ] Add `previewObserver` to UmweltContext
- [ ] Implement "Preview As" button in ghost tooltips
- [ ] Add preview banner component
- [ ] Show schema preview in ghost tooltips
- [ ] Track preview usage for analytics

**Open Questions**

1. **Invocation in preview**: Should users be able to *actually* invoke in preview mode?
   - Option A: Preview is read-only (show what they'd see, not do)
   - Option B: Preview allows invocation with elevated privileges (risky?)
2. **Preview scope**: Just this path, or entire app?
3. **Preview timeout**: Auto-exit after 60s to prevent confusion?

---

## Part III: Integration Enhancements

### 3A. Observer History + Exploration Breadcrumbs

**The Vision**

Track observer switches as an exploration trace:

```
Session Timeline
────────────────────────────────────────────────
[Guest]  →  [Developer]  →  [Void Walker]
 14:32       14:35           14:41
             ↑ +5 aspects    ↑ -3 aspects, +void
```

**Implementation**

```typescript
interface UmweltTrace {
  id: string;
  timestamp: number;
  from: Observer;
  to: Observer;
  diff: {
    revealedCount: number;
    hiddenCount: number;
  };
  // Optional: which path was being viewed
  activePath?: string;
}

// In UmweltContext
const [history, setHistory] = useState<UmweltTrace[]>([]);
const MAX_HISTORY = 20;

const triggerTransition = useCallback((...) => {
  // ... existing logic

  // Record to history
  setHistory(prev => [
    ...prev.slice(-MAX_HISTORY + 1),
    {
      id: nanoid(),
      timestamp: Date.now(),
      from,
      to,
      diff: {
        revealedCount: diff.revealed.length,
        hiddenCount: diff.hidden.length,
      },
      activePath: currentPath,
    },
  ]);
}, [...]);

// Revert capability
const revertToHistoryEntry = useCallback((entryId: string) => {
  const entry = history.find(h => h.id === entryId);
  if (entry) {
    // This triggers a new transition, adding to history
    triggerTransition(currentObserver, entry.from, metadata, density);
  }
}, [history, ...]);
```

**UI: History Drawer**

```
┌───────────────────────────────────────┐
│ Exploration History          [Clear]  │
├───────────────────────────────────────┤
│ ● Void Walker (now)                   │
│   2 aspects, void context             │
│                                        │
│ ○ Developer                    [↩]    │
│   5 min ago at world.town             │
│   8 aspects                           │
│                                        │
│ ○ Guest                        [↩]    │
│   12 min ago                          │
│   3 aspects                           │
└───────────────────────────────────────┘
```

**Tasks**

- [ ] Add `history` state to UmweltContext
- [ ] Add `revertToHistoryEntry()` function
- [ ] Create `HistoryDrawer.tsx` component
- [ ] Add trigger button in ObserverPicker area
- [ ] Persist history to sessionStorage
- [ ] Add "Clear History" action

**Open Questions**

1. **History vs undo**: Is this a linear timeline or tree (branching)?
2. **Path context**: Should we track which path was active at each switch?
3. **Analytics**: Should exploration patterns be tracked for improving defaults?

---

### 3B. Multi-Observer Comparison Mode (Spacious Only)

**The Vision**

Side-by-side comparison of what different observers see:

```
┌────────────────────┬─────────────────────┐
│ Guest              │ Developer           │
├────────────────────┼─────────────────────┤
│ world.town         │ world.town          │
│ ├─ manifest ✓      │ ├─ manifest ✓       │
│ ├─ witness ✓       │ ├─ witness ✓        │
│ ├─ [create] 🔒     │ ├─ create ✓         │
│ └─ [admin] 🔒      │ ├─ admin ✓          │
│                    │ └─ polynomial ✓      │
├────────────────────┼─────────────────────┤
│ Capabilities: 1    │ Capabilities: 3     │
│ Visible: 2/5       │ Visible: 5/5        │
└────────────────────┴─────────────────────┘
```

**Implementation**

```typescript
// ComparisonMode.tsx
interface ComparisonModeProps {
  path: string;
  metadata: PathMetadata;
  leftObserver: Observer;
  rightObserver: Observer;
  onSwitch: (side: 'left' | 'right', observer: Observer) => void;
}

export function ComparisonMode({
  path,
  metadata,
  leftObserver,
  rightObserver,
  onSwitch,
}: ComparisonModeProps) {
  const leftVisible = getVisibleAspects(leftObserver, { [path]: metadata });
  const rightVisible = getVisibleAspects(rightObserver, { [path]: metadata });

  // All aspects from both sides (union)
  const allAspects = new Set([
    ...leftVisible.map(a => a.aspect),
    ...rightVisible.map(a => a.aspect),
  ]);

  return (
    <div className="grid grid-cols-2 gap-4">
      <ComparisonColumn
        observer={leftObserver}
        aspects={Array.from(allAspects)}
        visible={new Set(leftVisible.map(a => a.aspect))}
        onChangeObserver={(o) => onSwitch('left', o)}
      />
      <ComparisonColumn
        observer={rightObserver}
        aspects={Array.from(allAspects)}
        visible={new Set(rightVisible.map(a => a.aspect))}
        onChangeObserver={(o) => onSwitch('right', o)}
      />
    </div>
  );
}
```

**Entry Point**

Add a "Compare" button in the AspectPanel header (spacious only):

```typescript
{density === 'spacious' && (
  <button
    onClick={() => setComparisonMode(true)}
    className="text-xs text-gray-400 hover:text-cyan-400"
  >
    Compare observers
  </button>
)}
```

**Tasks**

- [ ] Create `ComparisonMode.tsx` component
- [ ] Add toggle state to AspectPanel
- [ ] Design compact comparison column layout
- [ ] Add observer picker to each column
- [ ] Highlight differences between columns
- [ ] Add "What am I missing?" summary

**Open Questions**

1. **Default comparison**: Current observer vs Guest? Or let user pick both?
2. **More than two**: Should we support 3+ way comparison?
3. **Export**: Should there be a "Copy comparison as Markdown" action?

---

## Part IV: Future Vision (Long-Term)

### 4A. Observer as Polynomial Agent

**The Paradigm Shift**

Currently, observers are static archetypes. But what if observer evolution was *dynamic*?

```
ObserverPolynomial[Engagement,Intent,Mode]

Positions:
  browsing    → Low commitment, read-only, casual
  exploring   → Medium commitment, learning, curious
  operating   → High commitment, action, focused
  mastering   → Expert mode, advanced affordances

Transitions (automatic):
  browsing → exploring:  After 3+ path visits
  exploring → operating: After first successful invoke
  operating → mastering: After configuring observer settings

Transitions (manual):
  Any → browsing:        "Reset to casual mode"
  Any → mastering:       Requires explicit unlock
```

**Implementation Sketch**

```typescript
interface ObserverPolynomial {
  position: 'browsing' | 'exploring' | 'operating' | 'mastering';
  directions: Map<string, () => void>;  // Valid transitions

  // Engagement tracking
  pathVisits: number;
  successfulInvokes: number;
  sessionDuration: number;
}

function computeObserverTransition(
  current: ObserverPolynomial,
  event: SessionEvent
): ObserverPolynomial | null {
  switch (current.position) {
    case 'browsing':
      if (current.pathVisits >= 3) {
        return { ...current, position: 'exploring' };
      }
      break;
    case 'exploring':
      if (current.successfulInvokes >= 1) {
        return { ...current, position: 'operating' };
      }
      break;
    // ...
  }
  return null; // No transition
}
```

**Why This Matters**

1. **Onboarding**: New users start in `browsing`, gradually unlocking power
2. **Teaching**: The UI literally grows with the user
3. **Safety**: Destructive actions require `operating` or higher
4. **Analytics**: Track funnel: how many reach `mastering`?

---

### 4B. AGENTESE-Native Observer Definition

**The Vision**

Observers should be discoverable and switchable via AGENTESE itself:

```
self.observer.manifest      → Current observer state
self.observer.available     → All valid archetypes for this user
self.observer.switch        → Change observer archetype
self.observer.history       → Exploration trace
self.observer.polynomial    → Position in observer polynomial
```

**Backend**

```python
@node("self.observer")
class ObserverNode:
    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer) -> dict:
        return {
            "archetype": observer.archetype,
            "capabilities": list(observer.capabilities),
            "session_id": observer.session_id,
        }

    @aspect(category=AspectCategory.PERCEPTION)
    async def available(self, observer: Observer) -> list[dict]:
        # Return archetypes available to this user based on their permissions
        return [
            {"id": "guest", "capabilities": ["read"]},
            {"id": "user", "capabilities": ["read", "write"]},
            # ... filtered by user's actual permissions
        ]

    @aspect(category=AspectCategory.MUTATION)
    async def switch(self, observer: Observer, to: str) -> dict:
        # Validate and return new observer state
        if to not in self._valid_archetypes(observer):
            raise AGENTESERefusal("Cannot switch to that archetype")
        return {"archetype": to, "capabilities": ARCHETYPE_CAPS[to]}
```

**Why This Matters**

1. **Self-describing**: The observer system documents itself
2. **Extensible**: Add new archetypes without frontend changes
3. **Consistent**: CLI and Web use the same discovery mechanism
4. **Auditable**: Observer switches become AGENTESE events

---

### 4C. Collaborative Umwelt (Multi-User)

**The Vision**

When two users observe the same path:

1. **Presence indicators** (like Figma cursors)
2. **Capability asymmetry**: "Alice sees 3 aspects you don't"
3. **Capability lending**: "Borrow admin for 5 minutes"

**Capability Lending Protocol**

```python
@node("self.capability")
class CapabilityNode:
    @aspect(category=AspectCategory.MUTATION)
    async def lend(
        self,
        observer: Observer,
        to_user: str,
        capability: str,
        duration_minutes: int = 5,
    ) -> dict:
        """
        Temporarily grant a capability to another user.

        - Creates time-limited capability token
        - Logged for audit
        - Revocable by lender
        """
        if capability not in observer.capabilities:
            raise AGENTESERefusal("Cannot lend capability you don't have")

        token = self._create_capability_token(
            from_user=observer.user_id,
            to_user=to_user,
            capability=capability,
            expires_at=datetime.now() + timedelta(minutes=duration_minutes),
        )

        return {"token": token, "expires_in": duration_minutes * 60}
```

**Why This Matters**

1. **Collaboration**: Pair programming with capability sharing
2. **Onboarding**: Senior devs lend capabilities to juniors
3. **Audit trail**: All capability loans are logged
4. **Trust building**: Gradual capability expansion

---

## Priority Matrix

| ID | Enhancement | Effort | Impact | Dependencies | Phase |
|----|-------------|--------|--------|--------------|-------|
| **1A** | Registry-backed capabilities | Medium | High | Backend `@aspect` changes | P0 |
| **1B** | Contract-aware aspects | Medium | Medium | 1A, schema threading | P0 |
| **1C** | Session persistence | Low | High | None | P0 |
| **2A** | PathExplorer dimming | Low | Medium | 1A (for accuracy) | P1 |
| **2B** | Capability Radar | Medium | Low | nivo or custom SVG | P2 |
| **2C** | Ghost interaction | Medium | High | 1B (for schema preview) | P1 |
| **3A** | History + breadcrumbs | Medium | Medium | None | P1 |
| **3B** | Multi-observer comparison | High | Low | 2A | P2 |
| **4A** | Observer Polynomial | High | High | Major architecture | Future |
| **4B** | AGENTESE-native observers | High | High | `self.observer` node | Future |
| **4C** | Collaborative Umwelt | Very High | Medium | WebSocket, multi-user | Future |

---

## Implementation Phases

### Phase 0: Foundation (P0 Tasks)

**Goal**: Correctness and persistence

1. Registry-backed capabilities (1A)
2. Session persistence (1C)
3. Contract-aware aspects (1B)

**Exit Criteria**:
- [ ] Capability requirements come from registry, not heuristics
- [ ] Observer persists across page refresh
- [ ] Ghost tooltips show contract schemas

**Estimated Effort**: 2-3 sessions

---

### Phase 1: Education (P1 Tasks)

**Goal**: Users understand the observer system

1. PathExplorer dimming (2A)
2. Ghost aspect interaction (2C)
3. History + breadcrumbs (3A)

**Exit Criteria**:
- [ ] Inaccessible paths are visually dimmed
- [ ] Ghost aspects explain how to unlock them
- [ ] Users can see and revert to previous observers

**Estimated Effort**: 3-4 sessions

---

### Phase 2: Advanced (P2 Tasks)

**Goal**: Power users get superpowers

1. Capability Radar (2B)
2. Multi-observer comparison (3B)

**Exit Criteria**:
- [ ] Spacious mode shows capability radar
- [ ] Users can compare two observers side-by-side

**Estimated Effort**: 2 sessions

---

### Phase 3: Future (Exploratory)

**Goal**: Paradigm evolution

1. Observer as Polynomial (4A)
2. AGENTESE-native observers (4B)
3. Collaborative Umwelt (4C)

**Exit Criteria**: TBD after Phase 2 learnings

---

## Open Questions (Unresolved)

### Philosophical

1. **Observer gradations**: Is the current archetype list sufficient? Should users define custom archetypes?
2. **Capability inheritance**: If a user has `admin`, do they implicitly have `write` and `read`?
3. **Negative capabilities**: Can an observer have "everything except X"?

### Technical

1. **Performance**: At what scale does `computeUmweltDiff` become slow? (100 paths × 10 aspects benchmark)
2. **Caching**: Should capability calculations be memoized? For how long?
3. **Server authority**: Should the frontend trust its own capability checks, or verify with server?

### UX

1. **Animation fatigue**: Do animations get annoying after 100 observer switches?
2. **Default archetype**: Should new users start as Guest, User, or Developer?
3. **Archetype names**: Are current names (Guest, Developer, Mayor, Void Walker) intuitive?

---

## Related

- `plans/umwelt-visualization.md` — Parent plan (Phase 1 complete)
- `spec/protocols/agentese.md` Part IV — Observer-Dependent Affordances
- `spec/principles.md` AD-010 — Habitat Guarantee
- `spec/principles.md` AD-008 — Simplifying Isomorphisms
- `docs/skills/elastic-ui-patterns.md` — Density adaptation patterns
- `impl/claude/web/src/components/docs/umwelt/` — Current implementation

---

*Plan created: 2025-12-19*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
*Design inspiration: Exploration rewards, not permission bureaucracy*
