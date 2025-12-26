# Witness Primitives - Usage Guide

## Overview

The Witness primitives provide **structural witnessing** where witness marks are part of the state transition itself, not an afterthought.

"Every state change is a morphism that returns (newState, witnessMark)"

## The Anti-Pattern (Fire-and-Forget)

```typescript
// BAD: Fire-and-forget witnessing
const [expanded, setExpanded] = useState(false);

const handleToggle = () => {
  const newState = !expanded;
  setExpanded(newState); // State change

  // Separate, disconnected witnessing
  witnessPortal('toggle', 'portal', destination, depth); // Fire-and-forget
};
```

Problems:
- Witnessing is decoupled from state change
- Easy to forget to witness
- No guarantee that witness happens
- Witness doesn't capture the actual state transition

## The Pattern (Structural Witnessing)

### Option 1: useWitnessedState Hook

```typescript
import { useWitnessedState } from '@/primitives/Witness';

function PortalToken() {
  // State with automatic witnessing
  const [expanded, setExpanded] = useWitnessedState(false, {
    action: 'portal-expand',
    principles: ['joy_inducing', 'composable'],
    automatic: true,
  });

  const handleToggle = async () => {
    // State transition is a morphism that returns [newState, witnessMark]
    await setExpanded((prev) => [
      !prev, // New state
      {
        action: `Portal ${!prev ? 'expanded' : 'collapsed'}`,
        reasoning: 'User toggled portal expansion',
        principles: ['joy_inducing', 'composable'],
        metadata: { destination, depth },
      },
    ]);
  };

  return <button onClick={handleToggle}>Toggle</button>;
}
```

### Option 2: useWitness Hook (Manual)

```typescript
import { useWitness } from '@/primitives/Witness';

function PortalToken() {
  const [expanded, setExpanded] = useState(false);
  const { witness, isWitnessing } = useWitness();

  const handleToggle = async () => {
    const newState = !expanded;

    // Witness and state change together
    const markId = await witness(
      `Portal ${newState ? 'expanded' : 'collapsed'}`,
      {
        reasoning: 'User toggled expansion',
        principles: ['joy_inducing'],
        metadata: { destination, depth, previousState: expanded },
        fireAndForget: true, // Optional: don't wait for response
      }
    );

    setExpanded(newState);
  };

  return <button onClick={handleToggle}>Toggle</button>;
}
```

### Option 3: withWitness HOC

```typescript
import { withPortalWitness, type WitnessInjectedProps } from '@/primitives/Witness';

interface PortalTokenProps extends WitnessInjectedProps {
  destination: string;
  depth: number;
}

function PortalToken({ destination, depth, witness }: PortalTokenProps) {
  const [expanded, setExpanded] = useState(false);

  const handleToggle = async () => {
    const newState = !expanded;

    await witness(`Portal ${newState ? 'expanded' : 'collapsed'}`, {
      reasoning: 'User toggled expansion',
      metadata: { destination, depth },
      fireAndForget: true,
    });

    setExpanded(newState);
  };

  return <button onClick={handleToggle}>Toggle</button>;
}

// Wrap with automatic witnessing
export default withPortalWitness(PortalToken);
```

## Display Components

### WitnessMarkComponent

Display a single witness mark:

```typescript
import { WitnessMarkComponent } from '@/primitives/Witness';

function MarkDisplay({ mark }) {
  return (
    <WitnessMarkComponent
      mark={mark}
      variant="card" // 'card' | 'inline' | 'minimal' | 'badge'
      showPrinciples={true}
      showReasoning={true}
      onClick={() => console.log('Mark clicked:', mark.id)}
    />
  );
}
```

### WitnessTrailComponent

Display a sequence of marks as a causal trail:

```typescript
import { WitnessTrailComponent } from '@/primitives/Witness';

function TrailDisplay({ marks }) {
  return (
    <WitnessTrailComponent
      marks={marks}
      orientation="vertical" // 'vertical' | 'horizontal'
      showConnections={true}
      maxVisible={10}
      onMarkClick={(mark, index) => console.log('Clicked:', mark.id)}
    />
  );
}
```

## Real-World Example: PortalToken Refactor

### Before (Fire-and-Forget)

```typescript
const PortalToken = ({ destination, depth, edgeType }) => {
  const [expanded, setExpanded] = useState(false);
  const { witnessPortal } = useWitness();

  const handleToggle = () => {
    const newState = !expanded;
    setExpanded(newState);

    // Fire and forget - disconnected from state
    witnessPortal(
      newState ? 'expand' : 'collapse',
      edgeType,
      destination,
      depth
    );
  };

  return <button onClick={handleToggle}>Toggle</button>;
};
```

### After (Structural Witnessing)

```typescript
const PortalToken = ({ destination, depth, edgeType }) => {
  const [expanded, setExpanded] = useWitnessedState(false, {
    action: 'portal-toggle',
    principles: ['joy_inducing', 'composable'],
    automatic: true,
  });

  const handleToggle = async () => {
    await setExpanded((prev) => [
      !prev,
      {
        action: `Portal ${!prev ? 'expanded' : 'collapsed'}: ${edgeType} -> ${destination}`,
        reasoning: `User ${!prev ? 'expanded' : 'collapsed'} portal at depth ${depth}`,
        principles: ['joy_inducing', 'composable'],
        metadata: { destination, depth, edgeType },
      },
    ]);
  };

  return <button onClick={handleToggle}>Toggle</button>;
};
```

## Key Principles

1. **State transitions are morphisms**: `S -> (S, WitnessMark)`
2. **Witnessing is structural**: Built into the state change, not bolted on
3. **Witnessing is automatic**: Fire-and-forget by default (configurable)
4. **Marks capture context**: Previous state, new state, reasoning, principles
5. **Principles are first-class**: Every action honors specific principles

## Convenience HOCs

```typescript
import {
  withPortalWitness,    // For portal components
  withNavigationWitness, // For navigation
  withEditWitness,       // For editing
  withChatWitness,       // For chat
} from '@/primitives/Witness';

// Each HOC provides sensible defaults for its domain
```

## Types Reference

```typescript
// State morphism
type StateMorphism<S> = (state: S) => [S, Omit<WitnessMark, 'id' | 'timestamp' | 'author'>];

// Witnessed state setter
type WitnessedStateSetter<S> = (morphism: StateMorphism<S>) => Promise<void>;

// Witness mark
interface WitnessMark {
  id: string;
  action: string;
  reasoning?: string;
  principles: string[];
  author: 'kent' | 'claude' | 'system';
  timestamp: string;
  parent_mark_id?: string;
  automatic?: boolean;
  metadata?: Record<string, unknown>;
}
```

## Migration Strategy

1. **Identify fire-and-forget calls**: Search for `witnessPortal(`, `witnessNavigation(`
2. **Replace with useWitnessedState**: For components with simple state
3. **Replace with useWitness**: For complex state transitions
4. **Wrap with HOC**: For shared witnessing across multiple components

## Philosophy

Fire-and-forget witnessing is a code smell. It suggests that witnessing is optional, an afterthought.

Structural witnessing makes witnessing **necessary and sufficient**:
- **Necessary**: You can't change state without producing a witness mark
- **Sufficient**: The witness mark captures everything about the transition

"The proof IS the decision. The mark IS the witness."
