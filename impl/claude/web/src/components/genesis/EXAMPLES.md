# Genesis Container Examples

Comprehensive examples showing how to compose Genesis containers.

## Example 1: Breathing Citizen Cards

```tsx
import { BreathingContainer } from '@/components/genesis';

function CitizenGallery({ citizens }: { citizens: Citizen[] }) {
  return (
    <div className="grid grid-cols-3 gap-4">
      {citizens.map((citizen, i) => (
        <BreathingContainer
          key={citizen.id}
          phaseOffset={i * 0.15}
          intensity="subtle"
        >
          <CitizenCard citizen={citizen} />
        </BreathingContainer>
      ))}
    </div>
  );
}
```

## Example 2: Growing List with Staggered Entrance

```tsx
import { GrowingContainer } from '@/components/genesis';

function CoalitionList({ coalitions }: { coalitions: Coalition[] }) {
  return (
    <div className="space-y-3">
      {coalitions.map((coalition, i) => (
        <GrowingContainer
          key={coalition.id}
          autoTrigger
          delay={i * 80}
          duration="normal"
        >
          <CoalitionCard coalition={coalition} />
        </GrowingContainer>
      ))}
    </div>
  );
}
```

## Example 3: Unfurling Details Panel

```tsx
import { UnfurlingPanel, BreathingContainer } from '@/components/genesis';

function CitizenDetailsPanel({ isOpen, citizen }: Props) {
  return (
    <UnfurlingPanel
      isOpen={isOpen}
      direction="right"
      contentFadeDelay={0.3}
    >
      <div className="p-6 space-y-4">
        <h2>{citizen.name}</h2>

        {/* Breathing status indicator */}
        <BreathingContainer
          intensity={citizen.consent_debt > 0.7 ? 'emphatic' : 'subtle'}
          period={citizen.consent_debt > 0.7 ? 'urgent' : 'calm'}
        >
          <StatusIndicator status={citizen.phase} />
        </BreathingContainer>

        <p>{citizen.description}</p>
      </div>
    </UnfurlingPanel>
  );
}
```

## Example 4: Toast Notification System

```tsx
import { OrganicToast, GrowingContainer } from '@/components/genesis';

function ToastManager({ toasts }: { toasts: Toast[] }) {
  return (
    <div className="fixed top-4 right-4 space-y-2 z-50">
      {toasts.map((toast, i) => (
        <GrowingContainer
          key={toast.id}
          autoTrigger
          delay={i * 100}
          duration="quick"
        >
          <OrganicToast
            type={toast.type}
            origin="top"
            duration={toast.duration}
            onDismiss={() => dismissToast(toast.id)}
          >
            {toast.message}
          </OrganicToast>
        </GrowingContainer>
      ))}
    </div>
  );
}
```

## Example 5: Modal with Radial Unfurl

```tsx
import { UnfurlingPanel, GrowingContainer, BreathingContainer } from '@/components/genesis';

function CoalitionFormModal({ isOpen, onClose }: Props) {
  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40"
          onClick={onClose}
        />
      )}

      {/* Modal */}
      <div className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none">
        <UnfurlingPanel
          isOpen={isOpen}
          direction="radial"
          duration={400}
          onFolded={onClose}
        >
          <div className="bg-bark rounded-lg p-8 max-w-lg pointer-events-auto">
            <h2 className="text-xl mb-4">Form Coalition</h2>

            {/* Form fields grow in after modal unfurls */}
            <GrowingContainer autoTrigger delay={200}>
              <FormFields />
            </GrowingContainer>

            {/* Breathing submit button for emphasis */}
            <BreathingContainer intensity="normal" period="calm">
              <button className="mt-4 px-4 py-2 bg-amber rounded">
                Create Coalition
              </button>
            </BreathingContainer>
          </div>
        </UnfurlingPanel>
      </div>
    </>
  );
}
```

## Example 6: Accordion with Unfurling

```tsx
import { UnfurlingPanel } from '@/components/genesis';

function AccordionItem({ title, content, isOpen, onToggle }: Props) {
  return (
    <div className="border-b border-clay">
      <button
        className="w-full text-left py-3 px-4 hover:bg-bark/50"
        onClick={onToggle}
      >
        {title}
      </button>

      <UnfurlingPanel
        isOpen={isOpen}
        direction="down"
        duration={250}
        contentFadeDelay={0.2}
      >
        <div className="px-4 pb-4">
          {content}
        </div>
      </UnfurlingPanel>
    </div>
  );
}
```

## Example 7: Teaching Callout

```tsx
import { GrowingContainer, BreathingContainer } from '@/components/genesis';

function TeachingCallout({ category, children }: Props) {
  const [isDismissed, setIsDismissed] = useState(false);

  if (isDismissed) return null;

  return (
    <GrowingContainer autoTrigger duration="normal">
      <BreathingContainer intensity="subtle" period="calm">
        <div className="bg-honey/10 border-2 border-honey rounded-lg p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <span className="text-sm font-medium text-honey">
                Teaching: {category}
              </span>
              <p className="mt-1 text-sm">{children}</p>
            </div>
            <button
              onClick={() => setIsDismissed(true)}
              className="ml-4 text-honey/60 hover:text-honey"
            >
              ✕
            </button>
          </div>
        </div>
      </BreathingContainer>
    </GrowingContainer>
  );
}
```

## Example 8: Urgency States

```tsx
import { BreathingContainer } from '@/components/genesis';

function ConsentDebtMeter({ debt }: { debt: number }) {
  // Map debt level to breathing urgency
  const getUrgency = (debt: number) => {
    if (debt < 0.3) return { period: 'calm', intensity: 'subtle' };
    if (debt < 0.5) return { period: 'normal', intensity: 'normal' };
    if (debt < 0.7) return { period: 'elevated', intensity: 'normal' };
    if (debt < 0.85) return { period: 'urgent', intensity: 'emphatic' };
    return { period: 'critical', intensity: 'emphatic' };
  };

  const urgency = getUrgency(debt);

  return (
    <BreathingContainer
      period={urgency.period}
      intensity={urgency.intensity}
    >
      <div className="p-4 bg-copper/20 border-2 border-copper rounded">
        <h3>Consent Debt</h3>
        <div className="mt-2 h-2 bg-bark rounded-full overflow-hidden">
          <div
            className="h-full bg-copper transition-all"
            style={{ width: `${debt * 100}%` }}
          />
        </div>
        <p className="mt-1 text-sm">{(debt * 100).toFixed(0)}%</p>
      </div>
    </BreathingContainer>
  );
}
```

## Composition Patterns

### Nested Containers

Containers can be nested for layered effects:

```tsx
// Growing entrance + breathing idle
<GrowingContainer autoTrigger>
  <BreathingContainer intensity="subtle">
    <Card />
  </BreathingContainer>
</GrowingContainer>

// Unfurling panel with growing content
<UnfurlingPanel isOpen={isOpen}>
  <GrowingContainer autoTrigger delay={150}>
    <Content />
  </GrowingContainer>
</UnfurlingPanel>
```

### Conditional Animation

Use `static` prop to disable animation conditionally:

```tsx
<BreathingContainer static={prefersReducedMotion}>
  <Card />
</BreathingContainer>
```

### Staggered Lists

Combine delay and phaseOffset for rich stagger patterns:

```tsx
{items.map((item, i) => (
  <GrowingContainer
    key={item.id}
    autoTrigger
    delay={i * 60}
  >
    <BreathingContainer phaseOffset={i * 0.12}>
      <ItemCard item={item} />
    </BreathingContainer>
  </GrowingContainer>
))}
```
