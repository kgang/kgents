# Motion Language

> *"Animation is not decoration—it is communication. Movement tells the story that static cannot."*

**Status**: Foundation Document
**Prerequisites**: `philosophy.md`, `visual-system.md`
**Implementation**: `impl/claude/web/src/components/joy/`

---

## The Motion Philosophy

In kgents, motion serves three purposes:

1. **Feedback** — Tell users what's happening
2. **Guidance** — Direct attention where it's needed
3. **Delight** — Reward attention with joy

Motion is **never gratuitous**. Every animation earns its place.

---

## Part I: Core Motion Primitives

kgents defines six **canonical motion primitives**:

### 1. Breathe

**Purpose:** Living, ambient presence
**Use when:** Showing something is alive, active, waiting
**Character:** Calm, meditative, organic

```tsx
<Breathe intensity={0.4} speed="slow">
  <Glyph char="◉" />
</Breathe>
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `intensity` | 0-1 | 0.4 | Scale magnitude |
| `speed` | slow/medium/fast | medium | Breath cycle duration |

**Timing:**
- Slow: 4s cycle
- Medium: 2s cycle
- Fast: 1s cycle

**Physics:** Sinusoidal easing, gentle scale oscillation

---

### 2. Pulse

**Purpose:** Attention, urgency, heartbeat
**Use when:** Something needs attention, processing, waiting for input
**Character:** Alert but not aggressive

```tsx
<Pulse intensity={0.3} speed="medium">
  <span>Notification</span>
</Pulse>
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `intensity` | 0-1 | 0.3 | Opacity/scale variance |
| `speed` | slow/medium/fast | medium | Pulse rate |

**Timing:**
- Slow: 2s cycle
- Medium: 1s cycle
- Fast: 0.5s cycle

**Physics:** Sharp attack, soft decay (like heartbeat)

---

### 3. Shake

**Purpose:** Error, rejection, invalid action
**Use when:** User attempts something invalid, form validation fails
**Character:** Playful denial, not punishing

```tsx
<Shake trigger={hasError} intensity="gentle">
  <InputField />
</Shake>
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `trigger` | boolean | - | When true, plays shake |
| `intensity` | gentle/medium/strong | gentle | Shake magnitude |

**Timing:** 400ms total duration

**Physics:** Spring oscillation with damping

---

### 4. Pop

**Purpose:** Celebration, success, arrival
**Use when:** Task completed, achievement unlocked, element appears
**Character:** Joyful, satisfying, earned

```tsx
<Pop trigger={showSuccess}>
  <Badge>Complete!</Badge>
</Pop>
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `trigger` | boolean | - | When true, plays pop |
| `scale` | number | 1.1 | Max scale during pop |

**Timing:** 300ms total (fast in, bounce out)

**Physics:** Overshoot spring, quick settle

---

### 5. Shimmer

**Purpose:** Loading, skeleton, placeholder
**Use when:** Content is loading, showing placeholder state
**Character:** Patient, hopeful, temporal

```tsx
<Shimmer>
  <div className="h-4 w-32 bg-gray-700 rounded" />
</Shimmer>
```

**Timing:** 1.5s cycle, continuous

**Physics:** Linear gradient sweep

---

### 6. Fade

**Purpose:** Enter/exit, appear/disappear
**Use when:** Elements mount/unmount, transitions between states
**Character:** Smooth, invisible, respectful

```tsx
<motion.div
  initial={{ opacity: 0, y: 4 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -4 }}
/>
```

**Timing:**
- Enter: 200ms
- Exit: 150ms (faster out)

**Physics:** Ease-out for enter, ease-in for exit

---

## Part II: Timing Principles

### The 2025 Speed Mandate

> *"Speed is king in 2025. Users crave instant feedback with lightning-fast animations."*

**Core timing rules:**

| Duration | Use Case |
|----------|----------|
| **0-100ms** | Instant feedback (hover, focus) |
| **100-200ms** | Quick transitions (tabs, toggles) |
| **200-400ms** | Standard animations (cards, modals) |
| **400-700ms** | Elaborate sequences (celebrations, page transitions) |
| **1000ms+** | Ambient loops only (breathing, shimmer) |

### Easing Functions

```typescript
const EASINGS = {
  // Standard transitions
  standard: 'cubic-bezier(0.4, 0.0, 0.2, 1)',    // Material standard

  // Enter animations
  enter: 'cubic-bezier(0.0, 0.0, 0.2, 1)',       // Decelerate

  // Exit animations
  exit: 'cubic-bezier(0.4, 0.0, 1, 1)',          // Accelerate

  // Emphasis (overshoot)
  bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',

  // Organic (breathing)
  organic: 'cubic-bezier(0.45, 0.05, 0.55, 0.95)', // Sine
} as const;
```

### Stagger Patterns

When animating lists:

```typescript
const STAGGER = {
  fast: 0.03,    // 30ms between items
  medium: 0.05,  // 50ms between items
  slow: 0.08,    // 80ms between items
} as const;

// Usage with Framer Motion
<motion.div
  initial="hidden"
  animate="visible"
  variants={{
    visible: {
      transition: { staggerChildren: STAGGER.medium }
    }
  }}
>
  {items.map(item => <motion.div variants={itemVariants} />)}
</motion.div>
```

---

## Part III: Motion Semantics

### State → Motion Mapping

Each UI state has associated motion:

| State | Motion | Intensity | Speed |
|-------|--------|-----------|-------|
| **Idle** | None or subtle breathe | 0.1 | slow |
| **Hover** | Scale up | 1.02x | 100ms |
| **Active** | Breathe | 0.3 | medium |
| **Processing** | Pulse + shimmer | 0.4 | medium |
| **Success** | Pop | 1.1x | 300ms |
| **Error** | Shake | gentle | 400ms |
| **Loading** | Shimmer | - | 1.5s |
| **Disabled** | None | - | - |

### Jewel-Specific Motion

Each Crown Jewel has motion personality:

| Jewel | Characteristic Motion | Reason |
|-------|----------------------|--------|
| **Brain** | Slow breathe, subtle pulse | Contemplative, neural |
| **Gestalt** | Precise transitions, minimal | Analytical, systematic |
| **Gardener** | Organic growth, unfurling | Natural, nurturing |
| **Atelier** | Playful pop, flourishes | Creative, expressive |
| **Coalition** | Coordinated, synchronized | Collaborative, unified |
| **Park** | Dramatic entrances, spotlights | Theatrical, immersive |
| **Domain** | Urgent pulse, sharp transitions | Crisis, authority |

---

## Part IV: Implementation Patterns

### The Joy Components

kgents provides ready-to-use motion components:

```tsx
// Breathing presence
import { Breathe } from '@/components/joy/Breathe';

// Success celebration
import { Pop } from '@/components/joy/Pop';

// Error feedback
import { Shake } from '@/components/joy/Shake';

// Loading shimmer
import { Shimmer } from '@/components/joy/Shimmer';
```

### Motion Preferences

**Always respect user preferences:**

```tsx
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';

function AnimatedComponent() {
  const { shouldAnimate, reducedMotion } = useMotionPreferences();

  if (!shouldAnimate) {
    return <StaticVersion />;
  }

  return <AnimatedVersion />;
}
```

**The `prefers-reduced-motion` query:**
- Users with vestibular disorders can disable motion
- All animations must have static fallbacks
- Never animate content position rapidly

### Framer Motion Patterns

```tsx
// Standard fade-in
const fadeIn = {
  initial: { opacity: 0, y: 4 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -4 },
  transition: { duration: 0.2 },
};

// Card hover
const cardHover = {
  whileHover: { scale: 1.02 },
  transition: { duration: 0.1 },
};

// List stagger
const listContainer = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const listItem = {
  hidden: { opacity: 0, x: -10 },
  show: { opacity: 1, x: 0 },
};
```

---

## Part V: Micro-interactions

### The Delight Budget

> *"Real delight is subtle. It's the tiny moments that make a product feel alive."*

**Micro-interaction inventory:**

| Interaction | Animation | Purpose |
|-------------|-----------|---------|
| Button click | Scale 0.98 → 1.0 | Tactile feedback |
| Toggle switch | Spring slide | Satisfying state change |
| Checkbox | Pop check | Confirmation |
| Dropdown open | Fade + slide | Spatial relationship |
| Toast enter | Slide + fade | Attention grab |
| Toast exit | Fade out fast | Get out of way |
| Card select | Ring + scale | Selection clarity |
| Tab switch | Underline slide | Context preservation |

### Premium Micro-interactions

From [research on premium feel](https://medium.com/@ryan.almeida86/5-micro-interactions-to-make-any-product-feel-premium-68e3b3eae3bf):

1. **Elastic scrolling** — Content bounces at edges
2. **Haptic-like feedback** — Visual "click" on interactions
3. **Magnetic snap** — Elements find their position
4. **Anticipation cues** — Hint at what's coming
5. **Particle celebrations** — Earned rewards feel earned

---

## Part VI: 3D Motion

### Three.js Scene Animation

For WebGL/3D visualizations:

```typescript
// Standard camera orbit
const CAMERA_ANIMATION = {
  duration: 1000,  // ms
  easing: 'cubic-bezier(0.4, 0.0, 0.2, 1)',
};

// Node appearance
const NODE_ENTER = {
  initial: { scale: 0, opacity: 0 },
  final: { scale: 1, opacity: 1 },
  duration: 300,
  delay: (index: number) => index * 30,
};

// Connection drawing
const EDGE_DRAW = {
  duration: 500,
  easing: 'ease-out',
};
```

### Lighting Animation

```typescript
// Subtle sun movement (ambient)
useFrame((state) => {
  const t = state.clock.elapsedTime;
  sunLight.current.position.x = 15 + Math.sin(t * 0.1) * 0.5;
});

// Focus spotlight
const focusLight = {
  transition: { duration: 400, ease: 'easeOut' },
};
```

---

## Part VII: Performance Guidelines

### Animation Performance Checklist

- [ ] Use `transform` and `opacity` only (GPU-accelerated)
- [ ] Avoid animating `width`, `height`, `margin`, `padding`
- [ ] Use `will-change` sparingly
- [ ] Test at 60fps target
- [ ] Profile on low-end devices

### When to Avoid Animation

- **Data updates** — Don't animate rapid data changes
- **Large lists** — Virtualize, don't animate all
- **Mobile battery** — Reduce ambient animations
- **User preference** — Respect reduced-motion

---

## Part VIII: Testing Motion

### Visual Regression for Animation

```typescript
// Test animation states
describe('Breathe component', () => {
  it('renders without crashing', () => {
    render(<Breathe><span>Test</span></Breathe>);
  });

  it('respects reduced motion preference', () => {
    mockReducedMotion(true);
    const { container } = render(<Breathe><span>Test</span></Breathe>);
    expect(container).not.toHaveStyle('animation');
  });
});
```

### Animation Timing Verification

Use Storybook for motion documentation:

```tsx
// stories/Breathe.stories.tsx
export default {
  title: 'Joy/Breathe',
  component: Breathe,
};

export const Slow = () => <Breathe speed="slow"><Glyph /></Breathe>;
export const Medium = () => <Breathe speed="medium"><Glyph /></Breathe>;
export const Fast = () => <Breathe speed="fast"><Glyph /></Breathe>;
```

---

## Sources

- [UI Animation Trends 2025](https://medium.com/@naim.softx/ui-animation-trends-to-watch-in-2025-designing-for-delight-speed-intent-90cb5ff3d9ad) — Speed and intent in modern animation
- [Micro Animation Examples 2025](https://bricxlabs.com/blogs/micro-interactions-2025-examples) — Practical micro-interaction patterns
- [Designing for Delight](https://www.influentialsoftware.com/designing-for-delight-microinteractions-and-animation-in-2025/) — Animation that converts
- [5 Premium Micro-interactions](https://medium.com/@ryan.almeida86/5-micro-interactions-to-make-any-product-feel-premium-68e3b3eae3bf) — The details that matter
- [Micro-interactions in UX](https://www.interaction-design.org/literature/article/micro-interactions-ux) — IxDF comprehensive guide

---

*"The motion is the meaning. What moves tells what matters."*
