# Web Refactor Phase 5 Continuation Prompt

> **STATUS: COMPLETE** (2025-12-15)

## Context from Previous Sessions

**Phase 1 (Elastic Primitives)**: **COMPLETE**
**Phase 2 (Interaction Patterns)**: **COMPLETE**
**Phase 3 (User Flows)**: **COMPLETE**
**Phase 4 (Performance)**: **COMPLETE**
**Phase 5 (Polish & Delight)**: **COMPLETE**

### What Was Built in Phase 5

Polish & Delight infrastructure for joy-inducing UX:

```
src/styles/animations.css                 # Micro-interactions (spawn, phase, confetti, shimmer)
src/components/feedback/LoadingStates.tsx # Contextual loaders with rotating messages
src/components/feedback/EmptyStates.tsx   # Personality-filled empty states
src/components/feedback/ShortcutCheatsheet.tsx # '?' triggered keyboard reference
src/components/error/FriendlyError.tsx    # Empathetic error messages
src/components/onboarding/OnboardingHints.tsx # First-run hints (localStorage)
src/lib/easterEggs.ts                     # Konami code, secret words, celebrations
src/styles/globals.css                    # Accessibility: skip links, focus states, sr-only
```

**Tests**: 631 passed (37 files)
**Build**: Successful (CSS ~11.5KB gzipped)

### What Was Built in Phase 4

Performance infrastructure is now in place:

```
src/hooks/useBatchedEvents.ts       # Generic event batching (50ms default)
src/lib/reportWebVitals.ts          # Core Web Vitals tracking (FCP, LCP, CLS, INP, TTFB)
src/components/town/VirtualizedCitizenList.tsx  # @tanstack/react-virtual for 100+ citizens
vite.config.ts                      # rollup-plugin-visualizer for bundle analysis
```

**Bundle Sizes (gzipped):**
- Critical path: ~96KB (vendor 51KB + index 35KB + page ~10KB)
- Pixi: 189KB (lazy-loaded only on Town/Workshop)
- Route code splitting: All pages lazy-loaded with Suspense

### Available Infrastructure from Phases 1-3

```
src/components/elastic/             # Elastic primitives (Container, Card, Split, Placeholder)
src/components/dnd/                 # Drag and drop (DndProvider, DraggableAgent, PipelineSlot)
src/components/pipeline/            # Pipeline building (Canvas, Node, Edge, ContextMenu)
src/components/timeline/            # Historical mode (TimelineScrubber)
src/components/creation/            # Agent creation wizard
src/components/chat/                # INHABIT chat interface
src/components/details/             # Agent details tabs
src/components/orchestration/       # Pipeline orchestration
src/components/error/               # ErrorBoundary
src/components/feedback/            # Toast notifications
src/hooks/                          # Full hook suite (streaming, gestures, shortcuts, layout)
```

---

## Phase 5: Polish & Delight

**Goal**: Transform functional UI into a joy-inducing experience that embodies Kent's vision.

**Guiding Principles** (from `_focus.md`):
- "Create a shockingly delightful consumer, prosumer, and professional experience"
- Builder metaphors: Chefs in a kitchen, Gardeners in a garden, Kids on a playground
- "Easter eggs hidden > announced: discovery is the delight, not the feature list" (meta.md)

---

## Implementation Tasks

### Task 1: Micro-Interactions & Animations

Add subtle animations that bring the UI to life without being distracting.

**File to Create**: `src/styles/animations.css`

```css
/* Citizen card hover */
.citizen-card-hover {
  transition: transform 0.2s ease-out, box-shadow 0.2s ease-out;
}
.citizen-card-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Phase transition pulse */
@keyframes phase-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
.phase-transitioning {
  animation: phase-pulse 1s ease-in-out infinite;
}

/* New citizen spawn */
@keyframes citizen-spawn {
  0% { transform: scale(0.8); opacity: 0; }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); opacity: 1; }
}
.citizen-spawning {
  animation: citizen-spawn 0.4s ease-out;
}

/* Event feed item slide-in */
@keyframes slide-in-right {
  from { transform: translateX(20px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
.event-item-new {
  animation: slide-in-right 0.2s ease-out;
}

/* Builder archetype glow */
@keyframes archetype-glow {
  0%, 100% { box-shadow: 0 0 5px var(--glow-color); }
  50% { box-shadow: 0 0 15px var(--glow-color); }
}
.builder-active {
  animation: archetype-glow 2s ease-in-out infinite;
}

/* Completion celebration */
@keyframes confetti-burst {
  0% { transform: scale(0) rotate(0deg); opacity: 1; }
  100% { transform: scale(1.5) rotate(180deg); opacity: 0; }
}
```

**Files to Modify**:
- `src/widgets/cards/CitizenCard.tsx` — Add hover animation class
- `src/components/town/Mesa.tsx` — Add spawn animation for new citizens
- `src/pages/Town.tsx` — Add phase transition animation
- `src/components/workshop/CompletionSummary.tsx` — Add celebration animation

### Task 2: Loading States with Personality

Replace generic spinners with contextual, delightful loading states.

**File to Create**: `src/components/feedback/LoadingStates.tsx`

```typescript
// Contextual loading messages that rotate
const TOWN_LOADING_MESSAGES = [
  { emoji: '🏘️', text: 'Waking up the citizens...' },
  { emoji: '☕', text: 'Brewing morning coffee...' },
  { emoji: '🌅', text: 'The sun is rising over Agent Town...' },
  { emoji: '🐓', text: 'The rooster crows...' },
];

const WORKSHOP_LOADING_MESSAGES = [
  { emoji: '🔧', text: 'Sharpening the tools...' },
  { emoji: '📐', text: 'Measuring twice...' },
  { emoji: '🎨', text: 'Mixing the paints...' },
  { emoji: '🔨', text: 'Setting up the workbench...' },
];

const INHABIT_LOADING_MESSAGES = [
  { emoji: '🧘', text: 'Establishing connection...' },
  { emoji: '💭', text: 'Synchronizing thoughts...' },
  { emoji: '🤝', text: 'Building rapport...' },
];

export function ContextualLoader({ context }: { context: 'town' | 'workshop' | 'inhabit' }) {
  const [messageIndex, setMessageIndex] = useState(0);
  const messages = context === 'town' ? TOWN_LOADING_MESSAGES
    : context === 'workshop' ? WORKSHOP_LOADING_MESSAGES
    : INHABIT_LOADING_MESSAGES;

  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((i) => (i + 1) % messages.length);
    }, 2000);
    return () => clearInterval(interval);
  }, [messages.length]);

  const { emoji, text } = messages[messageIndex];

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <div className="text-5xl animate-bounce">{emoji}</div>
      <p className="text-gray-400 animate-pulse">{text}</p>
    </div>
  );
}
```

### Task 3: Error States with Empathy

Make errors feel less like failures and more like helpful guidance.

**File to Create**: `src/components/error/FriendlyError.tsx`

```typescript
interface FriendlyErrorProps {
  type: 'network' | 'notFound' | 'permission' | 'unknown';
  message?: string;
  onRetry?: () => void;
  onGoHome?: () => void;
}

const ERROR_CONTENT = {
  network: {
    emoji: '📡',
    title: "Lost in the Ether",
    subtitle: "The connection wandered off. It happens to the best of us.",
    suggestion: "Check your internet connection and try again.",
  },
  notFound: {
    emoji: '🗺️',
    title: "Uncharted Territory",
    subtitle: "This place doesn't exist... yet.",
    suggestion: "Perhaps it was moved, or maybe it's waiting to be created.",
  },
  permission: {
    emoji: '🔐',
    title: "Members Only",
    subtitle: "You'll need the right key to enter here.",
    suggestion: "Check your permissions or contact an administrator.",
  },
  unknown: {
    emoji: '🌀',
    title: "Something Unexpected",
    subtitle: "Even the wisest agents encounter mysteries.",
    suggestion: "Try refreshing, or come back in a moment.",
  },
};
```

### Task 4: First-Run Experience & Onboarding

Guide new users with contextual hints that feel helpful, not intrusive.

**File to Create**: `src/components/onboarding/OnboardingHints.tsx`

```typescript
// Hints that appear once per user, stored in localStorage
const HINT_KEYS = {
  TOWN_FIRST_VISIT: 'hint_town_first',
  WORKSHOP_FIRST_TASK: 'hint_workshop_task',
  INHABIT_FIRST_SESSION: 'hint_inhabit_session',
  PIPELINE_FIRST_BUILD: 'hint_pipeline_build',
};

interface HintProps {
  hintKey: string;
  position: 'top' | 'bottom' | 'left' | 'right';
  children: React.ReactNode;
  content: React.ReactNode;
}

export function OnboardingHint({ hintKey, position, children, content }: HintProps) {
  const [dismissed, setDismissed] = useState(() =>
    localStorage.getItem(hintKey) === 'true'
  );

  const dismiss = () => {
    localStorage.setItem(hintKey, 'true');
    setDismissed(true);
  };

  if (dismissed) return <>{children}</>;

  return (
    <div className="relative">
      {children}
      <HintBubble position={position} onDismiss={dismiss}>
        {content}
      </HintBubble>
    </div>
  );
}
```

**Hints to Add**:
- Town: "Click any citizen to see their thoughts and history"
- Workshop: "Describe a task and watch the builders collaborate"
- Inhabit: "Suggest actions, or gently force them if needed"
- Pipeline: "Drag agents here to compose them into workflows"

### Task 5: Keyboard Shortcuts Polish

Enhance the existing keyboard shortcuts with discoverability.

**File to Create**: `src/components/feedback/ShortcutHint.tsx`

```typescript
// Shows keyboard shortcut on hover after delay
export function ShortcutHint({
  shortcut,
  children,
  position = 'bottom'
}: {
  shortcut: string;
  children: React.ReactNode;
  position?: 'top' | 'bottom';
}) {
  return (
    <Tooltip content={<kbd className="px-1.5 py-0.5 bg-gray-800 rounded text-xs">{shortcut}</kbd>}>
      {children}
    </Tooltip>
  );
}
```

**File to Create**: `src/components/feedback/ShortcutCheatsheet.tsx`

```typescript
// Modal showing all shortcuts, triggered by '?'
const SHORTCUTS = [
  { category: 'Navigation', items: [
    { key: 'g t', description: 'Go to Town' },
    { key: 'g w', description: 'Go to Workshop' },
    { key: 'g d', description: 'Go to Dashboard' },
  ]},
  { category: 'Town', items: [
    { key: 'Space', description: 'Play/Pause simulation' },
    { key: '1-4', description: 'Set speed (0.5x-4x)' },
    { key: 'n', description: 'Toggle N-Phase view' },
    { key: 'Esc', description: 'Deselect citizen' },
  ]},
  { category: 'Workshop', items: [
    { key: 'Enter', description: 'Submit task' },
    { key: 'r', description: 'Reset workshop' },
  ]},
  { category: 'General', items: [
    { key: '?', description: 'Show this cheatsheet' },
    { key: 'Cmd+K', description: 'Command palette (future)' },
  ]},
];
```

### Task 6: Sound Design (Optional, Progressive Enhancement)

Add subtle audio feedback for key interactions (user-controllable).

**File to Create**: `src/lib/sounds.ts`

```typescript
// Tiny audio sprites for UI feedback
// Only plays if user has enabled sounds
const SOUNDS = {
  click: '/sounds/click.mp3',      // Soft click
  success: '/sounds/success.mp3',  // Gentle chime
  error: '/sounds/error.mp3',      // Soft thud
  spawn: '/sounds/spawn.mp3',      // Ethereal whoosh
  phase: '/sounds/phase.mp3',      // Ambient transition
};

class SoundManager {
  private enabled = false;
  private volume = 0.3;

  enable() { this.enabled = true; }
  disable() { this.enabled = false; }
  setVolume(v: number) { this.volume = Math.max(0, Math.min(1, v)); }

  play(sound: keyof typeof SOUNDS) {
    if (!this.enabled) return;
    const audio = new Audio(SOUNDS[sound]);
    audio.volume = this.volume;
    audio.play().catch(() => {}); // Ignore autoplay errors
  }
}

export const sounds = new SoundManager();
```

**Note**: Sound files should be small (<10KB each). Can use Web Audio API for programmatic sounds as alternative.

### Task 7: Easter Eggs

Hidden delights that reward exploration (per meta.md: "discovery is the delight").

**Ideas** (implement 2-3):

1. **Konami Code**: On Town page, entering ↑↑↓↓←→←→BA triggers a brief celebration animation
2. **Secret Citizen**: Clicking a citizen 7 times reveals a hidden "philosopher mode" with deeper thoughts
3. **Night Mode**: Double-clicking the moon icon during NIGHT phase triggers a shooting star
4. **Builder Handshake**: When two builders meet during a task, they do a secret handshake animation
5. **Coffee Break**: Typing "coffee" in Workshop input shows a brief ☕ animation

**File to Create**: `src/lib/easterEggs.ts`

```typescript
// Konami code detector
export function useKonamiCode(callback: () => void) {
  const sequence = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown',
                    'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight',
                    'KeyB', 'KeyA'];
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.code === sequence[index]) {
        if (index === sequence.length - 1) {
          callback();
          setIndex(0);
        } else {
          setIndex(i => i + 1);
        }
      } else {
        setIndex(0);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [index, callback]);
}
```

### Task 8: Accessibility Polish

Ensure the experience is delightful for everyone.

**Checklist**:
- [ ] All interactive elements have focus states
- [ ] Color contrast meets WCAG AA (4.5:1 for text)
- [ ] Reduced motion preference respected
- [ ] Screen reader announcements for dynamic content
- [ ] Keyboard navigation for all features

**File to Modify**: `src/styles/globals.css`

```css
/* Respect reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Focus visible for keyboard users */
:focus-visible {
  outline: 2px solid var(--color-town-highlight);
  outline-offset: 2px;
}

/* Skip link for keyboard navigation */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  padding: 8px;
  background: var(--color-town-highlight);
  z-index: 100;
}
.skip-link:focus {
  top: 0;
}
```

### Task 9: Empty States with Character

Transform empty states from boring to inviting.

**Empty State Messages**:

| Location | Current | Delightful |
|----------|---------|------------|
| Town (no citizens) | "No citizens" | "A quiet town awaits its first inhabitants..." |
| Workshop (no task) | "No active task" | "The workshop is ready. What shall we build?" |
| Event Feed (empty) | "No events yet" | "All is peaceful... for now." |
| Pipeline (empty) | "Drag agents here" | "An empty canvas. Every masterpiece starts here." |
| Artifacts (empty) | "No artifacts" | "The builders haven't created anything yet." |

### Task 10: Final Typography & Spacing Pass

Ensure consistent visual rhythm throughout.

**Checklist**:
- [ ] Headings follow consistent scale (text-4xl → text-3xl → text-2xl → text-xl)
- [ ] Body text is readable (text-base with 1.5 line-height minimum)
- [ ] Spacing uses consistent scale (4px increments: p-1, p-2, p-4, p-6, p-8)
- [ ] Interactive elements have minimum 44x44px touch targets on mobile
- [ ] Icons are consistently sized (16px inline, 20px standalone, 24px featured)

---

## Implementation Strategy

Recommended order (impact vs. effort):

1. **Micro-Interactions** — Immediate visual improvement (2 hours)
2. **Loading States** — Better perceived performance (1 hour)
3. **Error States** — Friendlier failure experience (1 hour)
4. **Empty States** — Quick copy improvements (30 min)
5. **Keyboard Shortcuts Polish** — Discoverability (2 hours)
6. **Accessibility Polish** — Essential for all users (2 hours)
7. **Onboarding Hints** — Reduces friction for new users (2 hours)
8. **Easter Eggs** — Delightful surprises (1 hour)
9. **Typography Pass** — Visual refinement (1 hour)
10. **Sound Design** — Optional enhancement (2 hours)

---

## Key Files to Reference

```
plans/web-refactor/polish.md           # Detailed polish plan (if exists)
src/styles/globals.css                 # Global styles
src/components/feedback/               # Toast, error boundary
src/hooks/useKeyboardShortcuts.ts      # Existing shortcuts
_focus.md                              # Kent's wishes
meta.md                                # Learnings (easter eggs, etc.)
```

---

## Validation Commands

```bash
# Type check
npm run typecheck

# Run tests
npm run test:run

# Build and check bundle
npm run build

# Accessibility audit (if using axe)
npm run test:e2e -- --grep "accessibility"

# Visual regression (if set up)
npm run test:e2e -- --update-snapshots
```

---

## Success Criteria

- [ ] All loading states have contextual, rotating messages
- [ ] Error states feel helpful, not hostile
- [ ] At least 2 easter eggs hidden and working
- [ ] Keyboard shortcut cheatsheet accessible via '?'
- [ ] Micro-interactions on citizen cards, phase transitions, event feed
- [ ] Empty states have personality
- [ ] Reduced motion preference respected
- [ ] Focus states visible for keyboard navigation
- [ ] Onboarding hints appear once per feature
- [ ] TypeScript compilation passes
- [ ] All tests pass

---

## Exit Criteria for Phase 5

Upon completion:
- [ ] All success criteria met
- [ ] No console errors in production build
- [ ] Manual QA pass on Town, Workshop, Inhabit flows
- [ ] Lighthouse accessibility score >90

**Phase 5 completes the Web Refactor initiative.**

---

*"Joy-inducing > merely functional."* — Kent's Standing Intent
