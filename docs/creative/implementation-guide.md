# Implementation Guide

> *"A design system without implementation guidance is just a mood board."*

**Status**: Practical Reference
**Audience**: Developers building kgents UI
**Prerequisites**: All creative direction documents

---

## Quick Reference

### The Core Rule

**Every visual decision traces to meaning.** If you can't explain *why* something looks the way it does, it's probably wrong.

### The Implementation Stack

```
philosophy.md       → Why we make choices
visual-system.md    → What choices to make (tokens)
motion-language.md  → How things move
voice-and-tone.md   → What words to use
mood-board.md       → What it should feel like
THIS DOCUMENT       → How to apply it all
```

---

## Part I: Quick Start Checklist

When building a new component, verify:

### Visual Checklist
- [ ] **Colors from palette** — No raw hex values
- [ ] **Typography from scale** — `xs`, `sm`, `base`, `lg`, `xl`, `2xl`, `3xl`, `4xl`
- [ ] **Spacing from scale** — Multiples of 4px (1, 2, 3, 4, 5, 6, 8, 10, 12, 16)
- [ ] **Border radius from scale** — `sm`, `md`, `lg`, `xl`, `full`
- [ ] **Density adaptive** — Works at `compact`, `comfortable`, `spacious`

### Motion Checklist
- [ ] **Has appropriate motion** — Loading, success, error states
- [ ] **Respects reduced motion** — Uses `useMotionPreferences()`
- [ ] **Timing is fast** — Most transitions < 300ms
- [ ] **Easing is natural** — Not linear except for loops

### Voice Checklist
- [ ] **Errors are empathetic** — Uses `EmpathyError` or similar pattern
- [ ] **Loading has personality** — Uses jewel-specific messages
- [ ] **Labels are verbs** — For actions
- [ ] **Empty states invite** — Not "No data"

### Composition Checklist
- [ ] **Works in HStack** — Horizontal composition
- [ ] **Works in VStack** — Vertical composition
- [ ] **Looks right next to other components** — Visual harmony
- [ ] **Has consistent padding** — Internal spacing matches system

---

## Part II: Component Patterns

### The Card Pattern

Every card follows this structure:

```tsx
interface CardProps {
  // Required
  children: ReactNode;

  // Visual
  density?: 'compact' | 'comfortable' | 'spacious';
  variant?: 'default' | 'elevated' | 'outlined';

  // Interaction
  onClick?: () => void;
  selected?: boolean;
  disabled?: boolean;
}

function Card({ children, density = 'comfortable', variant = 'default', ...props }: CardProps) {
  const padding = {
    compact: 'p-3',
    comfortable: 'p-4',
    spacious: 'p-6',
  }[density];

  const background = {
    default: 'bg-gray-800',
    elevated: 'bg-gray-700',
    outlined: 'bg-transparent border border-gray-700',
  }[variant];

  return (
    <div className={`rounded-lg ${padding} ${background} ${className}`} {...props}>
      {children}
    </div>
  );
}
```

### The Loading Pattern

Always use personality loading:

```tsx
import { PersonalityLoading } from '@/components/joy/PersonalityLoading';

// Full page loading
function PageLoading({ jewel }: { jewel: CrownJewel }) {
  return (
    <div className="h-full flex items-center justify-center">
      <PersonalityLoading jewel={jewel} size="lg" />
    </div>
  );
}

// Inline loading
function InlineLoading({ jewel }: { jewel: CrownJewel }) {
  return <PersonalityLoading jewel={jewel} size="sm" />;
}

// With specific action
<PersonalityLoading jewel="brain" action="search" />
// → "Searching neural networks..."
```

### The Error Pattern

Always use empathetic errors:

```tsx
import { EmpathyError, InlineError } from '@/components/joy/EmpathyError';

// Full page error
<EmpathyError
  type="network"
  action="Reconnect"
  onAction={handleRetry}
/>

// Form field error
<InlineError
  message="Email format looks off"
  shake={hasError}
/>
```

### The Empty State Pattern

```tsx
function EmptyState({
  emoji,
  title,
  subtitle,
  action,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <Breathe intensity={0.3}>
        <span className="text-4xl mb-4">{emoji}</span>
      </Breathe>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400 mb-4 max-w-md">{subtitle}</p>
      {onAction && (
        <button
          onClick={onAction}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white"
        >
          {action}
        </button>
      )}
    </div>
  );
}

// Usage
<EmptyState
  emoji="🌱"
  title="Nothing here yet"
  subtitle="This is where your memories will appear. Ready when you are."
  action="Capture first memory"
  onAction={() => navigate('/capture')}
/>
```

---

## Part III: Joy Components

### Available Components

```tsx
// Breathing presence (for living things)
import { Breathe } from '@/components/joy/Breathe';

// Success celebration
import { Pop } from '@/components/joy/Pop';

// Error feedback
import { Shake } from '@/components/joy/Shake';

// Loading placeholder
import { Shimmer } from '@/components/joy/Shimmer';

// Personality loading
import { PersonalityLoading } from '@/components/joy/PersonalityLoading';

// Empathy error
import { EmpathyError } from '@/components/joy/EmpathyError';
```

### Using Motion Preferences

**Always check user preferences:**

```tsx
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';

function AnimatedThing() {
  const { shouldAnimate } = useMotionPreferences();

  if (!shouldAnimate) {
    return <StaticVersion />;
  }

  return (
    <motion.div
      animate={{ opacity: 1 }}
      transition={{ duration: 0.2 }}
    >
      <AnimatedContent />
    </motion.div>
  );
}
```

### Animation Timing Reference

```typescript
// Standard durations
const TIMING = {
  instant: 100,    // Hover, focus
  quick: 200,      // Toggles, tabs
  standard: 300,   // Cards, modals
  elaborate: 500,  // Celebrations
} as const;

// Easing curves
const EASING = {
  standard: [0.4, 0.0, 0.2, 1],
  enter: [0.0, 0.0, 0.2, 1],
  exit: [0.4, 0.0, 1, 1],
  bounce: [0.68, -0.55, 0.265, 1.55],
} as const;
```

---

## Part IV: Density Adaptation

### Using Layout Context

```tsx
import { useLayoutContext } from '@/hooks/useLayoutContext';

function AdaptiveComponent() {
  const { density } = useLayoutContext();

  const fontSize = {
    compact: 'text-sm',
    comfortable: 'text-base',
    spacious: 'text-lg',
  }[density];

  const padding = {
    compact: 'p-2',
    comfortable: 'p-4',
    spacious: 'p-6',
  }[density];

  return (
    <div className={`${padding} ${fontSize}`}>
      Content adapts to density
    </div>
  );
}
```

### Density Breakpoints

```typescript
const BREAKPOINTS = {
  compact: 768,     // < 768px
  comfortable: 1024, // 768-1024px
  spacious: Infinity, // > 1024px
} as const;

// Hook implementation
function useDensity(): Density {
  const [width] = useWindowSize();

  if (width < BREAKPOINTS.compact) return 'compact';
  if (width < BREAKPOINTS.comfortable) return 'comfortable';
  return 'spacious';
}
```

### Layout Patterns by Density

```tsx
// Elastic Split - adapts panel to drawer
import { ElasticSplit } from '@/components/elastic/ElasticSplit';

<ElasticSplit
  primary={<Canvas />}
  secondary={<ControlPanel />}
/>
// compact: Canvas fills, panel becomes drawer
// comfortable: Fixed split
// spacious: Resizable split with divider
```

---

## Part V: Jewel Theming

### Jewel Colors

```typescript
import { JEWEL_COLORS } from '@/constants/jewels';

// Use in components
<div style={{ color: JEWEL_COLORS.brain.primary }}>
  Brain content
</div>

// Or with Tailwind classes
<div className="text-jewel-brain">
  Brain content
</div>
```

### Jewel-Specific Components

```tsx
// Personality loading already knows jewels
<PersonalityLoading jewel="gestalt" />

// Create jewel-aware wrapper
function JewelCard({ jewel, children }: { jewel: CrownJewel; children: ReactNode }) {
  const color = JEWEL_COLORS[jewel].primary;

  return (
    <Card>
      <div
        className="w-1 h-full absolute left-0 top-0 rounded-l-lg"
        style={{ backgroundColor: color }}
      />
      {children}
    </Card>
  );
}
```

---

## Part VI: Glyph System

### Using Glyphs

```tsx
import { Glyph } from '@/widgets/primitives/Glyph';

// Basic glyph
<Glyph char="◉" phase="active" />

// Animated glyph
<Glyph char="◉" phase="active" animate="breathe" fg="#06B6D4" />

// Glyph with distortion (for entropy visualization)
<Glyph
  char="◉"
  phase="active"
  distortion={{ blur: 0.5, skew: 2, jitter_x: 1, jitter_y: 0 }}
/>
```

### Glyph Character Reference

| Phase | Char | Meaning |
|-------|------|---------|
| idle | ○ | Inactive |
| active | ◉ | Running |
| processing | ◐ | Working |
| success | ● | Complete |
| error | ◌ | Failed |
| pending | ◯ | Waiting |

---

## Part VII: 3D Scenes

### Using Scene Lighting

```tsx
import { SceneLighting } from '@/components/three/SceneLighting';
import { useIlluminationQuality } from '@/hooks/useIlluminationQuality';

function My3DScene() {
  const quality = useIlluminationQuality();

  return (
    <Canvas shadows={quality !== 'minimal'}>
      <SceneLighting quality={quality} />
      {/* Your scene content */}
    </Canvas>
  );
}
```

### Shadow Casting Rules

```tsx
// Nodes cast shadows
<mesh castShadow>
  <sphereGeometry />
  <meshStandardMaterial />
</mesh>

// Ground receives shadows
<mesh receiveShadow>
  <planeGeometry />
  <meshStandardMaterial />
</mesh>

// Lines NEVER cast/receive shadows
<Line points={points} />
```

---

## Part VIII: Testing

### Visual Regression

```tsx
// Story for each state
export default {
  title: 'Components/MyComponent',
  component: MyComponent,
};

export const Default = () => <MyComponent />;
export const Loading = () => <MyComponent loading />;
export const Error = () => <MyComponent error="Something went wrong" />;
export const Empty = () => <MyComponent data={[]} />;
```

### Motion Testing

```tsx
describe('MyComponent motion', () => {
  it('respects reduced motion', () => {
    mockReducedMotion(true);
    const { container } = render(<MyComponent />);
    expect(container.querySelector('[data-animated]')).toBeNull();
  });
});
```

### Density Testing

```tsx
describe('MyComponent density', () => {
  it('adapts to compact', () => {
    mockViewport(500); // Mobile width
    const { container } = render(<MyComponent />);
    expect(container).toHaveClass('p-2'); // Compact padding
  });
});
```

---

## Part IX: Common Mistakes

### Color Mistakes

```tsx
// ❌ Raw hex
<div style={{ color: '#06B6D4' }}>

// ✅ Semantic color
<div className="text-cyan-500">

// ✅ Jewel color
<div style={{ color: JEWEL_COLORS.brain.primary }}>
```

### Spacing Mistakes

```tsx
// ❌ Arbitrary value
<div style={{ padding: '13px' }}>

// ✅ Scale value
<div className="p-3">  // 12px
```

### Motion Mistakes

```tsx
// ❌ No motion preference check
<motion.div animate={{ opacity: 1 }}>

// ✅ With preference check
const { shouldAnimate } = useMotionPreferences();
{shouldAnimate && <motion.div animate={{ opacity: 1 }}>}
```

### Error Mistakes

```tsx
// ❌ Technical error
<div>Error: ECONNREFUSED</div>

// ✅ Empathetic error
<EmpathyError type="network" />
```

---

## Part X: Contribution Guidelines

### When Adding New Components

1. **Check if it exists** — Search `impl/claude/web/src/`
2. **Follow patterns** — Use existing component as template
3. **Add to Storybook** — Document all states
4. **Test density** — Verify at all three breakpoints
5. **Test motion** — Verify with reduced motion
6. **Document** — Add JSDoc comments

### When Modifying Design Tokens

1. **Update `visual-system.md`** — Document the change
2. **Update Tailwind config** — If adding new values
3. **Check all usages** — Search for affected components
4. **Test thoroughly** — Visual regression

---

## Quick Reference Cards

### Color Quick Reference

```
Gray scale: 50 → 100 → 200 → 300 → 400 → 500 → 600 → 700 → 800 → 900 → 950
Jewels: brain(cyan) | gestalt(green) | gardener(lime) | atelier(amber) | coalition(violet) | park(pink) | domain(red)
States: success(green) | warning(amber) | error(red) | info(cyan) | pending(slate)
```

### Spacing Quick Reference

```
1=4px | 2=8px | 3=12px | 4=16px | 5=20px | 6=24px | 8=32px | 10=40px | 12=48px | 16=64px
```

### Typography Quick Reference

```
xs=12px | sm=14px | base=16px | lg=18px | xl=20px | 2xl=24px | 3xl=30px | 4xl=36px
```

### Border Radius Quick Reference

```
sm=4px | md=8px | lg=12px | xl=16px | full=9999px
```

---

*"The implementation is the truth. If it doesn't match the spec, one of them is wrong."*
