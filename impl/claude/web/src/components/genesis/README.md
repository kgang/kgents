# Genesis Container Primitives

Container components that wrap existing elements with breathing/growing/unfurling animations.

Implements Crown Jewels Genesis Moodboard animation patterns.

## Components

### BreathingContainer

Wraps any element with subtle breathing animation for idle states.

```tsx
import { BreathingContainer } from '@/components/genesis';

// Basic usage (idle state)
<BreathingContainer>
  <CitizenCard citizen={sage} />
</BreathingContainer>

// Urgent breathing for consent debt
<BreathingContainer period="urgent" intensity="emphatic">
  <ConsentDebtMeter debt={0.85} />
</BreathingContainer>

// Staggered breathing in list
{citizens.map((citizen, i) => (
  <BreathingContainer key={citizen.id} phaseOffset={i * 0.1}>
    <CitizenNode citizen={citizen} />
  </BreathingContainer>
))}
```

**Props:**
- `intensity?: 'subtle' | 'normal' | 'emphatic'` - Breathing amplitude (default: 'normal')
- `period?: 'calm' | 'normal' | 'elevated' | 'urgent' | 'critical'` - Breathing speed (default: 'normal')
- `static?: boolean` - Disable animation (default: false)
- `phaseOffset?: number` - Phase offset for staggered animation (0-1, default: 0)

### GrowingContainer

Elements emerge with seed → sprout → bloom → full animation.

```tsx
import { GrowingContainer } from '@/components/genesis';

// Auto-grow on mount
<GrowingContainer autoTrigger>
  <TeachingCallout category="polynomial">
    Learn about state machines!
  </TeachingCallout>
</GrowingContainer>

// Delayed staggered growth
{items.map((item, i) => (
  <GrowingContainer key={item.id} autoTrigger delay={i * 50}>
    <ItemCard item={item} />
  </GrowingContainer>
))}

// Quick growth for responsive UI
<GrowingContainer autoTrigger duration="quick">
  <Tooltip>Helpful hint</Tooltip>
</GrowingContainer>
```

**Props:**
- `duration?: 'quick' | 'normal' | 'deliberate'` - Animation duration (default: 'normal')
- `delay?: number` - Delay before growing starts in ms (default: 0)
- `autoTrigger?: boolean` - Auto-trigger on mount (default: false)
- `startFull?: boolean` - Start at full state, skip animation (default: false)
- `onGrown?: () => void` - Callback when fully grown

### UnfurlingPanel

Leaf-like expansion for panels/modals.

```tsx
import { UnfurlingPanel } from '@/components/genesis';

// Dropdown panel
<UnfurlingPanel isOpen={isVisible} direction="down">
  <DropdownContent />
</UnfurlingPanel>

// Radial modal
<UnfurlingPanel
  isOpen={showModal}
  direction="radial"
  duration={400}
  onFolded={() => setShowModal(false)}
>
  <ModalContent />
</UnfurlingPanel>

// Side panel from right
<UnfurlingPanel
  isOpen={showDetails}
  direction="left"
  contentFadeDelay={0.2}
>
  <DetailsSidebar />
</UnfurlingPanel>
```

**Props:**
- `isOpen: boolean` - Panel is open/visible (required)
- `direction?: 'down' | 'up' | 'left' | 'right' | 'radial'` - Direction of unfurl (default: 'down')
- `duration?: number` - Duration in ms (default: 300)
- `contentFadeDelay?: number` - Delay before content fades in, 0-1 (default: 0.3)
- `onUnfurled?: () => void` - Callback when unfurled
- `onFolded?: () => void` - Callback when folded

### OrganicToast

Toast that grows from a seed point with Living Earth colors.

```tsx
import { OrganicToast } from '@/components/genesis';

// Info toast
<OrganicToast type="info" onDismiss={handleDismiss}>
  Citizen joined the town!
</OrganicToast>

// Success toast (no auto-dismiss)
<OrganicToast type="success" duration={0} origin="bottom">
  Coalition successfully formed.
</OrganicToast>

// Learning callout
<OrganicToast type="learning" origin="right" duration={8000}>
  💡 Tip: Use staggered breathing for visual rhythm in lists.
</OrganicToast>
```

**Props:**
- `type: 'info' | 'success' | 'warning' | 'learning'` - Toast type, determines color (required)
- `origin?: 'top' | 'bottom' | 'left' | 'right'` - Origin direction for growth (default: 'top')
- `duration?: number` - Auto-dismiss duration in ms, 0 = no auto-dismiss (default: 5000)
- `onDismiss?: () => void` - Callback when dismissed

## Design Principles

### Everything Breathes
All idle elements should subtly breathe. Use `BreathingContainer` with `intensity="subtle"` for ambient life.

### Organic Growth
New elements should grow rather than pop in. Use `GrowingContainer` with `autoTrigger` for entrance animations.

### Leaf-Like Unfurling
Panels unfurl like leaves, not slide mechanically. Use `UnfurlingPanel` for expandable content.

### Living Earth Colors
Toast notifications use the Living Earth palette for warmth and nature-inspired aesthetics.

## References

- [Crown Jewels Genesis](../../../../../plans/crown-jewels-genesis.md) - Phase 1: Foundation
- [Animation Hooks](../../hooks/) - useBreathing, useGrowing, useUnfurling
- [Constants](../../constants/) - BREATHING_ANIMATION, GROWING_ANIMATION, LIVING_EARTH
