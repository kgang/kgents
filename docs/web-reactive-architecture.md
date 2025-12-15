# Web Reactive Architecture

> Unifying the Agent Town web frontend with the kgents reactive substrate.

## Quick Summary

The web frontend should consume **JSON projections** from Python widgets rather than maintaining separate state management. Same widget definitions, different rendering targets.

```
Python Widget → .to_json() → SSE → React Component
```

---

## The Problem

Currently, the web frontend duplicates state management:

| Layer | Current | Target |
|-------|---------|--------|
| State | Zustand stores | Signal bridges |
| Widgets | Custom React | JSON projection consumers |
| Composition | Manual JSX | HStack/VStack primitives |
| Types | Manual interfaces | Generated from Python |

**Cost of duplication**: Every state change requires updates in two places. Bug fixes don't propagate. Test coverage doubles.

---

## The Solution

### 1. JSON Projection as Contract

Python widgets already have `to_json()` methods:

```python
# impl/claude/agents/i/reactive/primitives/citizen_card.py
class CitizenWidget:
    def to_json(self) -> dict:
        return {
            "type": "citizen_card",
            "citizen_id": self.state.value.citizen_id,
            "name": self.state.value.name,
            ...
        }
```

TypeScript consumes this directly:

```typescript
// impl/claude/web/src/widgets/CitizenCard.tsx
interface CitizenCardProps {
  type: 'citizen_card';
  citizen_id: string;
  name: string;
  ...
}

function CitizenCard(props: CitizenCardProps) {
  return <div>{props.name}</div>;
}
```

### 2. SSE Delivers State

The backend streams JSON projections:

```python
# Backend
yield sse_event('live.state', ColonyDashboard(state).to_json())
```

```typescript
// Frontend
eventSource.addEventListener('live.state', (e) => {
  setDashboard(JSON.parse(e.data));
});
```

### 3. Composition Preserves Laws

The `>>` and `//` operators map to React:

| Python | TypeScript |
|--------|------------|
| `a >> b` | `<HStack>{a}{b}</HStack>` |
| `a // b` | `<VStack>{a}{b}</VStack>` |

Both satisfy associativity: `(a >> b) >> c ≡ a >> (b >> c)`

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (Python)                             │
│                                                                 │
│  ┌─────────────┐     ┌──────────────┐     ┌─────────────────┐  │
│  │ TownFlux    │────►│ ColonyState  │────►│ ColonyDashboard │  │
│  │ (events)    │     │ (frozen)     │     │ .to_json()      │  │
│  └─────────────┘     └──────────────┘     └────────┬────────┘  │
│                                                     │          │
└─────────────────────────────────────────────────────│──────────┘
                                                      │
                                              SSE: live.state
                                                      │
                                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (TypeScript)                        │
│                                                                 │
│  ┌─────────────────┐     ┌─────────────────────────────────┐   │
│  │ useTownStream() │────►│ <ColonyDashboard {...json} />   │   │
│  │ (hook)          │     │                                 │   │
│  └─────────────────┘     │   ┌─────────────────────────┐   │   │
│                          │   │ <HStack>                │   │   │
│                          │   │   <CitizenCard />       │   │   │
│                          │   │   <CitizenCard />       │   │   │
│                          │   │ </HStack>               │   │   │
│                          │   └─────────────────────────┘   │   │
│                          └─────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Files

### Python (Existing)

| File | Purpose |
|------|---------|
| `agents/i/reactive/signal.py` | Signal[T] primitive |
| `agents/i/reactive/composable.py` | HStack/VStack composition |
| `agents/i/reactive/widget.py` | KgentsWidget base class |
| `agents/i/reactive/primitives/citizen_card.py` | CitizenWidget |
| `agents/i/reactive/colony_dashboard.py` | ColonyDashboard |

### TypeScript (New)

| File | Purpose |
|------|---------|
| `web/src/reactive/types.ts` | WidgetJSON type definitions |
| `web/src/reactive/WidgetRenderer.tsx` | Dynamic widget renderer |
| `web/src/widgets/CitizenCard.tsx` | CitizenCard component |
| `web/src/widgets/layout/HStack.tsx` | HStack layout |
| `web/src/widgets/layout/VStack.tsx` | VStack layout |

---

## Migration Path

### Phase 1: Add Bridge (Non-Breaking)

Create `src/reactive/` module alongside existing code.

### Phase 2: Create Widgets (Non-Breaking)

Create `src/widgets/` consuming JSON projections.

### Phase 3: Integrate SSE (Non-Breaking)

Add `live.state` event type to SSE stream.

### Phase 4: Migrate Pages (Breaking)

Replace Zustand usage with hook-based state.

### Phase 5: Cleanup (Breaking)

Remove Zustand, deprecated code.

---

## Category Theory Foundation

The refactoring is justified by categorical principles:

### Functor Laws

The Web projection is a functor `F : Widget → ReactComponent`:

1. **Identity**: `F(Id) = <Fragment>` (identity widget maps to fragment)
2. **Composition**: `F(a >> b) = <HStack>{F(a)}{F(b)}</HStack>`

### Natural Transformation

State updates commute with projection:

```
        State₁ ─────update─────► State₂
           │                       │
      to_json()               to_json()
           │                       │
           ▼                       ▼
        JSON₁ ──────render──────► JSON₂
```

### Verification

Use `CategoryLawVerifier` from `protocols/agentese/laws.py` to verify composition laws hold for new React components.

---

## External Research Integration

This architecture aligns with industry patterns from 2025:

| Pattern | Source | Our Implementation |
|---------|--------|-------------------|
| AG-UI Protocol | Microsoft | SSE event types for state sync |
| Generative UI | Vercel AI SDK | Tool results → widget state |
| Signals | SolidJS | Signal bridge hooks |
| MCP-UI | Block | JSON projection as interface |

See spec references for full citations.

---

## Spec & Plan References

- **Specification**: `spec/protocols/web-reactive.md`
- **Implementation Plan**: `plans/agent-town/web-reactive-refactor.md`
- **Projection Protocol**: `spec/protocols/projection.md`
- **Category Laws**: `protocols/agentese/laws.py`

---

## Quick Start

### Consuming a Widget

```typescript
import { WidgetRenderer } from '@/reactive';
import type { ColonyDashboardJSON } from '@/reactive/types';

function TownPage() {
  const { dashboard } = useTownStream({ townId: 'my-town' });

  if (!dashboard) return <Loading />;

  return <WidgetRenderer widget={dashboard} />;
}
```

### Creating a Widget Component

```typescript
import type { MyWidgetJSON } from '@/reactive/types';

interface MyWidgetProps extends Omit<MyWidgetJSON, 'type'> {
  onSelect?: (id: string) => void;
}

export function MyWidget({ field1, field2, onSelect }: MyWidgetProps) {
  return (
    <div onClick={() => onSelect?.(field1)}>
      {field2}
    </div>
  );
}
```

### Registering in WidgetRenderer

```typescript
// src/reactive/WidgetRenderer.tsx
case 'my_widget':
  return <MyWidget {...widget} onSelect={onSelect} />;
```

---

## FAQ

**Q: Why not use React Server Components?**

A: RSC requires a Node.js backend. Our backend is Python. JSON projection is the bridge.

**Q: What about real-time updates?**

A: SSE handles streaming. The `live.state` event delivers complete projections. Delta updates can be added later.

**Q: How do we handle user interactions?**

A: Events flow up via callbacks (`onSelect`), state flows down via projections. Same as React.

**Q: What about Mesa/PixiJS?**

A: Mesa continues using PixiJS, but consumes citizen positions from JSON projections rather than Zustand.

---

*"The web is just another terminal. Define once, project everywhere."*
