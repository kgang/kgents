# Umwelt Visualization: Observer Reality Shift

> *"The noun is a lie. There is only the rate of change."*
>
> *"When you switch observer, the UI should feel different"*

**Status**: ✅ COMPLETE (All 5 Phases Done)
**Last Updated**: 2025-12-19
**Implementation**: `impl/claude/web/src/components/docs/umwelt/`
**Design References**: Linear, Raycast, Aceternity UI, Motion.dev

---

## The Philosophical Core

**Umwelt** (German: "environment" / "surrounding world") is a concept from biosemiotics coined by Jakob von Uexküll. It describes how different organisms perceive and interact with the same physical world in fundamentally different ways.

A tick perceives the world as: butyric acid → warmth → tactile sensation → blood.
A human perceives: colors, sounds, abstract concepts, social relationships.

Same world. Different realities.

**This is the heart of AGENTESE.** Different observers don't just have different *permissions*—they have different *perceptions*. The `developer` doesn't just see more than `guest`—they see *differently*.

### Connection to AGENTESE Architecture

This feature directly embodies three architectural decisions:

| Decision | How Umwelt Embodies It |
|----------|------------------------|
| **AD-008** (Simplifying Isomorphisms) | Observer archetype IS the simplifying isomorphism—one dimension that replaces scattered capability checks |
| **AD-010** (Habitat Guarantee) | Umwelt diff affects the Habitat projection; ghost aspects show "what almost was" |
| **AD-012** (Aspect Projection Protocol) | Aspects are ACTIONS shown in the panel, not places; umwelt animates their availability |

### Integration with AGENTESE Universal Protocol

The Umwelt visualization hooks into the existing discovery endpoint:

```
/agentese/discover?include_metadata=true → PathMetadata[]
                                        ↓
                              Each path has:
                                - aspects: string[]
                                - description: string
                                - required_capabilities: string[]
                                        ↓
                              computeUmweltDiff(observer, path)
                                        ↓
                              { revealed, hidden, unchanged }
```

---

## Architectural Assessment: How This Uses the Skills

This feature demonstrates why the kgents architectural improvements matter:

### 1. AGENTESE Universal Protocol (metaphysical-fullstack.md)

**What it is**: The protocol IS the API. No explicit backend routes—AGENTESE paths expose everything.

**How umwelt uses it**:
- `/agentese/discover` provides all path metadata
- Observer capabilities filter aspects via the protocol's affordance system
- No custom backend endpoint needed—the discovery endpoint already returns capability requirements

```python
# The protocol already handles observer-dependent affordances:
await logos.invoke("world.town.manifest", developer_observer)  # Returns full data
await logos.invoke("world.town.manifest", guest_observer)      # Returns subset
```

### 2. AGENTESE Node Registration (agentese-node-registration.md)

**What it is**: `@node` decorator + `dependencies=()` + DI container.

**How umwelt uses it**:
- Each node already declares `required_capabilities` in its metadata
- The `@aspect` decorator includes capability requirements
- Discovery endpoint returns these, enabling client-side diff computation

**The key insight**: We don't need to add capability metadata—it's already there via the registration system. We just need to expose it in discovery response.

### 3. Projection Protocol (projection-target.md)

**What it is**: Same widget, different surfaces. Fidelity varies by target.

**How umwelt uses it**:
- The umwelt animation itself is a projection—different density modes project different animations
- Ghost aspects are a "low-fidelity" projection of inaccessible capabilities
- The diff algorithm works identically for CLI (text output), Web (animation), and marimo (widget)

| Target | Umwelt Projection |
|--------|-------------------|
| CLI | `"Switched to developer. +3 aspects (manifest, admin, void)"` |
| Web | Full animation with ripple, stagger, toast |
| marimo | Widget badge changes color, aspects re-render |
| JSON | `{ diff: { revealed: [...], hidden: [...] } }` |

---

## The Design Challenge

> *"Daring, bold, creative, opinionated but not gaudy"*

Most permission systems show a toast: "You now have admin access." Boring. Bureaucratic. Museum thinking.

We want **garden thinking**: when the observer shifts, the world *blooms* differently. The user should *feel* the shift in reality, not just read about it.

**The Mirror Test**: Does this feel like discovering that you've put on new glasses that reveal hidden wavelengths? Or does it feel like getting a new badge on your profile?

---

## Design Explorations

### Exploration 1: The Aperture

**Metaphor**: Camera aperture opening/closing to let in more/less light.

When switching from `guest` → `developer`:
- Brief "opening" animation radiating from the observer picker
- Previously-hidden aspects "fade in" from low opacity
- Newly-hidden aspects "fade out" to ghosted state
- Color temperature shifts (cooler for more technical observers)

**Pros**: Intuitive, feels like revelation
**Cons**: Could be too literal, "gaudy" risk

```
┌─────────────────────────────────────────┐
│  Observer: [Developer ▼]                │
│                                         │
│  ┌─────┐                                │
│  │ ╱▔▔╲ │  ←─ Aperture opens            │
│  │▕    ▏│     aspects bloom outward     │
│  │ ╲__╱ │                               │
│  └─────┘                                │
└─────────────────────────────────────────┘
```

---

### Exploration 2: The Tide

**Metaphor**: Ocean tide revealing/hiding tide pools.

When capabilities change:
- Aspects that become visible "surface" like objects emerging from receding water
- Aspects that become hidden "submerge" with a gentle sink
- A subtle "water level" indicator could show capability "depth"

**Pros**: Organic, non-technical, peaceful
**Cons**: May be too abstract for first-time users

---

### Exploration 3: The Spectrum (RECOMMENDED)

**Metaphor**: Visible light spectrum—some observers see infrared, others ultraviolet.

When switching observers:
1. **Immediate**: Observer picker color shifts to new archetype color
2. **0-300ms**: "Spectrum shift" ripple emanates from picker
3. **300-600ms**: AspectPanel buttons animate:
   - Newly visible: Fade in with gentle scale from 0.8 → 1.0, slight glow in observer color
   - Newly hidden: Fade to ghost state with scale 1.0 → 0.95, desaturate
   - Unchanged: Subtle pulse acknowledging the shift
4. **600-800ms**: Optional toast showing delta ("3 aspects revealed, 2 hidden")

**Why this wins**:
- Rooted in AGENTESE philosophy (observers perceive different "spectra")
- Technically implementable with existing joy primitives
- Density-aware: can scale down for compact mode
- Not gaudy—it's brief, purposeful, educational

---

## Industry Design References

### Successful Products with Observer/Role UX

| Product | Pattern | What We Take |
|---------|---------|--------------|
| **[Linear](https://linear.app)** | Lamp effect on headers, smooth state transitions | The "subtle glow" language—color communicates mode without overwhelming |
| **[Raycast](https://raycast.com)** | Spotlight reveals, keyboard-driven focus | Quick micro-interactions; power users aren't slowed |
| **[Discord](https://discord.com)** | Role-based color theming, permission indicators | Color as identity—each role has its chromatic signature |
| **[Figma](https://figma.com)** | Cursor presence, shared selection | Real-time state visualization (not directly applicable but inspiration for "living" UI) |
| **[Notion](https://notion.so)** | Page permission badges, guest/member distinction | Subtle but clear capability indicators |

### Animation Libraries & Techniques

Based on [Motion.dev](https://motion.dev/), [Aceternity UI](https://www.aceternity.com/components), and [Motion Primitives](https://allshadcn.com/tools/motion-primitives/):

1. **Spotlight Effect** (Aceternity): Cursor-following dynamic light—could be adapted for observer picker glow
2. **Mask Reveal** (Aceternity): Hover to reveal hidden content—perfect for ghost aspects
3. **Stagger Children** (Motion.dev): `staggerChildren: 0.03` for aspect reveal cascade
4. **Color Shifting** ([Josh Comeau's technique](https://www.joshwcomeau.com/animation/color-shifting/)): HSL transition for observer color identity

### The 2025 Microinteraction Standard

From [Gartner research](https://www.betasofttechnology.com/motion-ui-trends-and-micro-interactions/): *"By end of 2025, 75% of customer-facing applications will incorporate micro-interactions as standard UI-UX practice."*

Our umwelt visualization is **exactly** this—a functional microinteraction that communicates state change.

### Design Tokens (Reference Linear)

```tsx
// Umwelt-specific tokens inspired by Linear's motion language
const UMWELT_MOTION = {
  // Transition durations (feel snappy but intentional)
  instant: 60,    // Color shift
  quick: 150,     // Ripple expand
  standard: 300,  // Aspect fade
  deliberate: 500, // Full cascade

  // Easing (responsive, not bouncy)
  enter: [0.22, 1, 0.36, 1],   // Quick start, gentle end
  exit: [0.55, 0.055, 0.675, 0.19], // Deliberate fade

  // Scale factors
  revealScale: [0.85, 1],      // Grow in
  hideScale: [1, 0.92],        // Shrink out

  // Opacity
  ghostOpacity: 0.35,          // Hidden but visible
  activeOpacity: 1,
} as const;
```

---

## The Diff Algorithm

Before we animate, we need to know what changed.

```typescript
interface UmweltDiff {
  revealed: AspectInfo[];   // Now visible, wasn't before
  hidden: AspectInfo[];     // Now hidden, was visible
  unchanged: AspectInfo[];  // Still visible
  observer: {
    from: Observer;
    to: Observer;
  };
}

interface AspectInfo {
  aspect: string;
  path: string;
  requiredCapability: string | null;
}

function computeUmweltDiff(
  prevObserver: Observer,
  nextObserver: Observer,
  metadata: Record<string, PathMetadata>
): UmweltDiff {
  const prevVisible = getVisibleAspects(prevObserver, metadata);
  const nextVisible = getVisibleAspects(nextObserver, metadata);

  return {
    revealed: nextVisible.filter(a => !prevVisible.includes(a)),
    hidden: prevVisible.filter(a => !nextVisible.includes(a)),
    unchanged: nextVisible.filter(a => prevVisible.includes(a)),
    observer: { from: prevObserver, to: nextObserver },
  };
}
```

---

## Animation Specification

### Phase 1: Color Shift (0-100ms)

The observer picker and header bar transition to new observer color.

```tsx
// Already implemented in ObserverPicker.tsx
// Just ensure transition duration is appropriate
style={{
  borderBottomColor: `color-mix(in srgb, ${archetype.color} 30%, transparent)`,
  transition: 'border-color 100ms ease-out',
}}
```

### Phase 2: Spectrum Ripple (100-300ms)

A subtle ring emanates from the observer picker.

```tsx
// New component: UmweltRipple
<motion.div
  className="absolute rounded-full pointer-events-none"
  style={{
    background: `radial-gradient(circle, ${observerColor}20 0%, transparent 70%)`,
  }}
  initial={{ scale: 0, opacity: 0.8 }}
  animate={{ scale: 3, opacity: 0 }}
  transition={{ duration: 0.3, ease: 'easeOut' }}
/>
```

### Phase 3: Aspect Animation (200-600ms)

Staggered animation of aspect buttons in the AspectPanel.

```tsx
// In AspectPanel, track animation state
const [animatingAspects, setAnimatingAspects] = useState<{
  revealed: Set<string>;
  hidden: Set<string>;
}>({ revealed: new Set(), hidden: new Set() });

// On umwelt diff, trigger animations
useEffect(() => {
  if (diff) {
    setAnimatingAspects({
      revealed: new Set(diff.revealed.map(a => a.aspect)),
      hidden: new Set(diff.hidden.map(a => a.aspect)),
    });

    // Clear after animation completes
    const timer = setTimeout(() => {
      setAnimatingAspects({ revealed: new Set(), hidden: new Set() });
    }, 600);

    return () => clearTimeout(timer);
  }
}, [diff]);

// Per-aspect animation variants
const aspectVariants = {
  revealed: {
    initial: { opacity: 0, scale: 0.8, filter: 'brightness(1.5)' },
    animate: { opacity: 1, scale: 1, filter: 'brightness(1)' },
    transition: { duration: 0.3, ease: 'easeOut' },
  },
  hidden: {
    initial: { opacity: 1, scale: 1 },
    animate: { opacity: 0.4, scale: 0.95, filter: 'grayscale(0.8)' },
    transition: { duration: 0.3, ease: 'easeIn' },
  },
  unchanged: {
    animate: { scale: [1, 1.02, 1] },
    transition: { duration: 0.2 },
  },
};
```

### Phase 4: Summary Toast (600-2000ms)

Brief, informative, optional.

```tsx
// Using OrganicToast from joy library
if (diff.revealed.length > 0 || diff.hidden.length > 0) {
  showToast({
    type: 'info',
    title: 'Reality Shifted',
    message: formatDiffMessage(diff),
    duration: 2000,
  });
}

function formatDiffMessage(diff: UmweltDiff): string {
  const parts: string[] = [];
  if (diff.revealed.length > 0) {
    parts.push(`${diff.revealed.length} aspect${diff.revealed.length > 1 ? 's' : ''} revealed`);
  }
  if (diff.hidden.length > 0) {
    parts.push(`${diff.hidden.length} faded from view`);
  }
  return parts.join(', ');
}
```

---

## Density Adaptation

Following the elastic-ui-patterns skill:

| Density | Animation Behavior |
|---------|-------------------|
| **Compact** | Ripple only (no stagger), toast at bottom |
| **Comfortable** | Full animation, compact toast |
| **Spacious** | Full animation with stagger, detailed toast |

```tsx
const UMWELT_CONFIG = {
  compact: {
    ripple: true,
    stagger: false,
    staggerDelay: 0,
    toast: 'minimal', // "3 revealed"
  },
  comfortable: {
    ripple: true,
    stagger: true,
    staggerDelay: 30, // 30ms between each aspect
    toast: 'standard', // "3 aspects revealed, 2 faded"
  },
  spacious: {
    ripple: true,
    stagger: true,
    staggerDelay: 50, // Slower, more deliberate
    toast: 'detailed', // "Revealed: manifest, invoke, admin. Hidden: govern, void."
  },
} as const;
```

---

## Accessibility

Per the motion preferences hook:

```tsx
const { shouldAnimate } = useMotionPreferences();

// If reduced motion, skip animations but still show toast
if (!shouldAnimate) {
  if (diff.revealed.length > 0 || diff.hidden.length > 0) {
    showToast({
      type: 'info',
      title: 'Observer Changed',
      message: formatDiffMessage(diff),
      duration: 3000, // Longer for reading
    });
  }
  return;
}
```

---

## State Management

### Option A: Context Provider (RECOMMENDED)

Create a dedicated context for umwelt transitions:

```tsx
// UmweltContext.tsx
interface UmweltContextValue {
  currentDiff: UmweltDiff | null;
  isTransitioning: boolean;
  triggerTransition: (from: Observer, to: Observer, metadata: PathMetadata) => void;
}

const UmweltContext = createContext<UmweltContextValue | null>(null);

export function UmweltProvider({ children }: { children: ReactNode }) {
  const [currentDiff, setCurrentDiff] = useState<UmweltDiff | null>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const { shouldAnimate } = useMotionPreferences();

  const triggerTransition = useCallback((from, to, metadata) => {
    const diff = computeUmweltDiff(from, to, metadata);

    if (diff.revealed.length === 0 && diff.hidden.length === 0) {
      return; // No perceptual change
    }

    setCurrentDiff(diff);
    setIsTransitioning(true);

    const duration = shouldAnimate ? 800 : 0;
    setTimeout(() => {
      setIsTransitioning(false);
      setCurrentDiff(null);
    }, duration);
  }, [shouldAnimate]);

  return (
    <UmweltContext.Provider value={{ currentDiff, isTransitioning, triggerTransition }}>
      {children}
    </UmweltContext.Provider>
  );
}
```

### Option B: Lifted State in AgenteseDocs

Simpler but less reusable:

```tsx
// In AgenteseDocs.tsx
const prevObserverRef = useRef(observer);
const [umweltDiff, setUmweltDiff] = useState<UmweltDiff | null>(null);

useEffect(() => {
  if (prevObserverRef.current.archetype !== observer.archetype) {
    const diff = computeUmweltDiff(prevObserverRef.current, observer, metadata);
    setUmweltDiff(diff);

    setTimeout(() => setUmweltDiff(null), 800);
  }
  prevObserverRef.current = observer;
}, [observer, metadata]);
```

---

## Component Structure

```
src/components/docs/
├── AgenteseDocs.tsx          # Main page (already exists)
├── PathExplorer.tsx          # Left panel (already exists)
├── ObserverPicker.tsx        # Observer selector (already exists)
├── AspectPanel.tsx           # Actions panel (modify for animations)
├── ResponseViewer.tsx        # JSON viewer (already exists)
├── GuidedTour.tsx            # First-load (already exists)
├── useAgenteseDiscovery.ts   # Data fetching (already exists)
│
├── umwelt/                   # NEW: Umwelt visualization
│   ├── UmweltContext.tsx     # Provider + context
│   ├── UmweltRipple.tsx      # Ripple animation component
│   ├── useUmweltDiff.ts      # Diff computation hook
│   └── umwelt.types.ts       # Type definitions
```

---

## Implementation Phases

### Phase 1: Foundation (1-2 hours) ✅ COMPLETE
- [x] Create `umwelt/` directory structure
- [x] Implement `computeUmweltDiff()` algorithm
- [x] Add `UmweltContext` provider
- [x] Wire into `AgenteseDocs.tsx`

### Phase 2: Ripple Effect (1 hour) ✅ COMPLETE
- [x] Create `UmweltRipple` component
- [x] Add to `ObserverPicker` on archetype change
- [x] Test across density modes (compact/comfortable/spacious)

### Phase 3: Aspect Animations (2 hours) ✅ COMPLETE
- [x] Modify `AspectPanel` to receive umwelt diff
- [x] Implement staggered fade-in for revealed aspects
- [x] Implement fade-to-ghost for hidden aspects
- [x] Add subtle pulse for unchanged aspects (via UMWELT_MOTION config)

### Phase 4: Toast Integration (30 min) ✅ COMPLETE
- [x] Create `formatDiffMessage()` helper (minimal/standard/detailed)
- [x] Wire to `simpleToast` system
- [x] Density-aware message variants implemented

### Phase 5: Polish (1 hour) ✅ COMPLETE
- [x] Accessibility audit (motion preferences - uses `useMotionPreferences`)
- [x] Animation toning (reduced scale, opacity, duration for subtlety)
- [x] Edge cases (rapid switching via `RAPID_SWITCH_THRESHOLD`, empty diffs skipped)
- [x] Documentation (README.md in umwelt/ directory)

---

## QA Prompt (Copy-Paste Ready)

```
QA: Umwelt Visualization (5 minutes)

SETUP:
1. cd impl/claude/web && npm run dev
2. Navigate to AGENTESE Docs (/agentese or docs page)

TEST OBSERVER SWITCHING:
3. Find Observer Picker (top bar: Guest/User/Developer/Mayor/Void)
4. Click each observer type and verify:
   - [ ] Very subtle ripple effect (comfortable/spacious modes only)
   - [ ] Aspects animate in/out (barely perceptible scale + opacity)
   - [ ] Brief toast shows "→ {observer}: {count} aspects revealed"
   - [ ] No animation when clicking same observer twice
   - [ ] Rapid clicking (3+ times per second) skips animations gracefully

TEST ACCESSIBILITY:
5. DevTools → Rendering → Emulate prefers-reduced-motion: reduce
   - [ ] All animations disabled, instant state changes

TEST DENSITY MODES:
6. Resize browser or use DevTools device mode:
   - Compact: No ripple, instant transitions, minimal toast
   - Comfortable: Ripple + stagger, standard toast
   - Spacious: Ripple + slower stagger, detailed toast

PASS CRITERIA:
✅ Animations are subtle (almost imperceptible)
✅ No dropped frames during transitions
✅ Works without animations for reduced-motion users
✅ No crashes on edge cases (empty metadata, same observer)
```

---

## Testing Strategy

### Unit Tests
```typescript
describe('computeUmweltDiff', () => {
  it('detects newly visible aspects', () => {
    const guestObserver = { archetype: 'guest', capabilities: ['read'] };
    const devObserver = { archetype: 'developer', capabilities: ['read', 'write', 'admin'] };

    const diff = computeUmweltDiff(guestObserver, devObserver, mockMetadata);

    expect(diff.revealed).toContainEqual(expect.objectContaining({ aspect: 'create' }));
    expect(diff.hidden).toHaveLength(0);
  });

  it('detects hidden aspects when downgrading', () => {
    const devObserver = { archetype: 'developer', capabilities: ['read', 'write', 'admin'] };
    const guestObserver = { archetype: 'guest', capabilities: ['read'] };

    const diff = computeUmweltDiff(devObserver, guestObserver, mockMetadata);

    expect(diff.hidden).toContainEqual(expect.objectContaining({ aspect: 'admin' }));
    expect(diff.revealed).toHaveLength(0);
  });

  it('handles no change gracefully', () => {
    const observer = { archetype: 'guest', capabilities: ['read'] };

    const diff = computeUmweltDiff(observer, observer, mockMetadata);

    expect(diff.revealed).toHaveLength(0);
    expect(diff.hidden).toHaveLength(0);
  });
});
```

### Visual Tests
- Storybook stories for each animation state
- Screenshot comparison across density modes
- Reduced motion behavior verification

---

## Joy Budget (Updated)

Following the "not gaudy" principle, this feature has a **joy budget**:

| Element | Allowed | Actual Value | Notes |
|---------|---------|--------------|-------|
| Ripple | Once per switch | 120ms, 15% opacity | Almost imperceptible |
| Aspect scale | 200ms max | 0.95 → 1.0 | Barely visible |
| Stagger delay | 20-30ms | Per density | Fast cascade |
| Toast | 1.5s display | Brief arrow notation | "→ developer: +3" |
| Sound | NO | - | Too intrusive |
| Confetti | NO | - | Reserved for achievements |

**Design principle**: If you notice the animation, it's too much. It should feel like the UI is *breathing*, not *dancing*.

---

## Success Criteria

1. **Educational**: First-time users understand that observers change perception
2. **Delightful**: Repeat users enjoy the micro-feedback
3. **Non-intrusive**: Power users can switch rapidly without being slowed down
4. **Accessible**: Works with reduced motion preferences
5. **Performant**: No dropped frames, no layout shifts

---

## Open Questions

1. **Should the PathExplorer also animate?** Paths don't change visibility based on observer (they're structural), but we could dim paths that have no accessible aspects for the current observer.

2. **Should we persist observer choice?** Currently resets on page load. Could store in sessionStorage for continuity.

3. **Voice line?** The void.* context could have a whispered audio cue ("*the void sees you*") but this risks "gaudy" territory.

4. **Capability Radar visualization?** A radial chart showing observer's capabilities vs. path requirements. Beautiful but might be scope creep.

---

## Enhanced: Ghost Aspect Interaction (Layer 3 Preview)

Per AD-010's Layer 3 (Ghost Integration), hidden aspects aren't just grayed—they're **explorable**:

### The Différance Pattern

When an observer switches and aspects become hidden, they don't disappear—they become **ghosts**:

```tsx
// Ghost aspects show "what could be"
<motion.button
  className={`
    ${isGhost ? 'opacity-35 grayscale' : ''}
    ${isGhost && isHovered ? 'opacity-60 cursor-help' : ''}
  `}
  title={isGhost ? `Requires ${requiredCapability}` : undefined}
  onClick={isGhost ? () => showCapabilityHint(requiredCapability) : onInvoke}
>
  {isGhost && <Lock className="w-3 h-3 absolute -top-1 -right-1" />}
  {/* ... rest of button */}
</motion.button>
```

### Ghost Tooltip Content

When hovering a ghost aspect:

```tsx
const GhostTooltip = ({ aspect, requiredCapability }: Props) => (
  <div className="p-3 max-w-xs">
    <p className="text-sm text-gray-300 mb-2">
      This aspect requires <strong>{requiredCapability}</strong> capability.
    </p>
    <p className="text-xs text-gray-500">
      Switch to <span className="text-cyan-400">{getArchetypeWithCapability(requiredCapability)}</span> to unlock.
    </p>
  </div>
);
```

### Why Ghosts Matter (Philosophical)

> *"The paths not taken are as important as the path taken."*

Ghost aspects teach users about the AGENTESE ontology. They see the **full space** of possibilities, not just their current slice. This is the Différance made visible—presence defined by absence.

---

## Contract Protocol Integration

The umwelt visualization benefits from the Contract Protocol (Appendix D of AGENTESE spec):

### Schema-Aware Aspect Display

When a path has contracts defined:

```python
@node(
    "world.town",
    contracts={
        "manifest": Response(ManifestResponse),
        "citizen.create": Contract(CreateRequest, CreateResponse),
    }
)
```

The AspectPanel can show:
- **Schema badge**: Small icon indicating "this aspect has a typed contract"
- **Parameter preview**: For mutations, show required fields
- **Response type**: "Returns: ManifestResponse"

### Enhanced Diff with Contract Awareness

```typescript
interface AspectInfo {
  aspect: string;
  path: string;
  requiredCapability: string | null;
  // NEW: Contract metadata
  hasContract: boolean;
  contractType: 'response' | 'request' | 'full' | null;
  isStreaming: boolean;
}
```

This enables the UI to show:
- 📄 Icon for aspects with full contracts
- 📡 Icon for streaming aspects
- Type hints in ghost tooltips

---

## Performance Considerations

### Animation Budget (16ms Frame Time)

Per [UXPin research](https://www.uxpin.com/studio/blog/ui-animation-examples/): *"Animations should harmonize with design to improve functionality."*

Our constraints:

| Animation | Max Duration | GPU Accelerated |
|-----------|--------------|-----------------|
| Color shift | 100ms | Yes (CSS filter) |
| Ripple expand | 200ms | Yes (transform) |
| Aspect fade | 300ms | Yes (opacity) |
| Stagger cascade | 50ms × N | Yes (layout isolated) |

### Batching Strategy

When switching observers rapidly (keyboard shortcuts), batch animations:

```tsx
const RAPID_SWITCH_THRESHOLD = 200; // ms

// If two switches happen within 200ms, skip intermediate animation
const lastSwitchRef = useRef(Date.now());

const handleObserverChange = useCallback((newObserver: Observer) => {
  const now = Date.now();
  const isRapidSwitch = now - lastSwitchRef.current < RAPID_SWITCH_THRESHOLD;

  if (isRapidSwitch) {
    // Skip to final state immediately
    setObserver(newObserver);
    setAnimating(false);
  } else {
    // Full animation
    triggerUmweltTransition(observer, newObserver);
  }

  lastSwitchRef.current = now;
}, [observer, triggerUmweltTransition]);
```

---

## Related

- `spec/protocols/agentese.md` — The full AGENTESE specification (Part IV: Observer-Dependent Affordances)
- `spec/protocols/projection.md` — Observer-dependent projections
- `docs/skills/elastic-ui-patterns.md` — Density adaptation
- `docs/skills/agentese-node-registration.md` — How nodes expose aspects
- `impl/claude/web/src/components/joy/` — Animation primitives
- `impl/claude/web/src/components/docs/ObserverPicker.tsx` — Observer selection UI

### External Resources

- [Motion.dev](https://motion.dev/) — Animation library documentation
- [Aceternity UI](https://www.aceternity.com/components) — Spotlight and reveal components
- [Josh Comeau: Color Shifting](https://www.joshwcomeau.com/animation/color-shifting/) — HSL animation technique
- [Motion Primitives](https://allshadcn.com/tools/motion-primitives/) — Pre-built animation components
- [Figma Roles & Permission Kit](https://www.figma.com/community/file/1314134675948312053) — Reference for RBAC UI patterns

---

## Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Should PathExplorer animate? | **No.** Paths are structural. Only aspects (actions) change per observer. |
| Should we persist observer choice? | **Yes.** Use `sessionStorage` for session continuity. |
| Voice line for void.*? | **No.** Risks "gaudy" territory. Keep it visual. |
| Capability Radar visualization? | **Future.** Nice-to-have for spacious mode, not MVP. |

---

*Plan created: 2025-12-19 | Quality Enhanced: 2025-12-19*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
*Design inspiration: Linear, Raycast, Discord, Motion.dev*
