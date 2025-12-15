# Web Reactive Projection Protocol

> *"The web is just another target. Same widgets, different pixels."*

## Purpose

This protocol extends the Projection Protocol to web targets (React/DOM), unifying the Agent Town web frontend with the reactive substrate. The goal: **eliminate duplicate state management** and enable widget definitions to project directly to React components.

This fulfills the Generative Principle—developers define state once; the web UI follows mechanically.

---

## The Core Insight

**`Widget[S].project(WEB)` returns `JSX.Element`.**

The web app becomes a projection target, equivalent to CLI, TUI, and marimo. The same `CitizenWidget` that renders ASCII in a terminal renders interactive HTML in a browser.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE WEB REACTIVE TRANSFORMATION                       │
│                                                                              │
│   Reactive Substrate (Python)         Web Frontend (TypeScript)             │
│   ─────────────────────────           ───────────────────────               │
│                                                                              │
│   Signal[T]           ══════════►     useSignal<T>(signal)                  │
│   Computed[T]         ══════════►     useComputed<T>(computed)              │
│   Effect              ══════════►     useReactiveEffect(effect)             │
│   KgentsWidget[S]     ══════════►     <Widget state={s} />                  │
│   HStack              ══════════►     <Flex direction="row">                │
│   VStack              ══════════►     <Flex direction="column">             │
│                                                                              │
│   project(JSON)       ══════════►     Widget Props (typed interface)        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Mathematical Foundation

### The Web Projection Functor

The Web projection is a **natural transformation** from Widget state to React elements:

```
P[Web] : State → ReactElement

Where:
- State is the widget's internal state (frozen dataclass in Python)
- ReactElement is the target-specific output (JSX.Element in TypeScript)
```

### Naturality Condition

For all state morphisms `f : S₁ → S₂`, the following commutes:

```
        S₁ ─────f────→ S₂
        │               │
   P[Web]│               │P[Web]
        ↓               ↓
   React(S₁) ──React(f)─→ React(S₂)
```

**Translation**: If widget state changes, the React component re-renders consistently.

### The Signal-React Adjunction

Signals and React state form an **adjunction**:

```
Signal ⊣ React

subscribe(embed(component)) ≤ component
signal ≤ embed(subscribe(signal))
```

This formalizes the bidirectional binding: Signals can drive React state, and React events can update Signals.

### Functor Laws for Widget Composition

The `>>` and `//` operators in the reactive substrate map to React composition via a functor:

```
F : Widget → ReactComponent

Laws:
1. F(Id) = Fragment (identity preserves)
2. F(a >> b) = <HStack>{F(a)}{F(b)}</HStack> (horizontal composition)
3. F(a // b) = <VStack>{F(a)}{F(b)}</VStack> (vertical composition)
4. F((a >> b) >> c) = F(a >> (b >> c)) (associativity)
```

The existing `CategoryLawVerifier` in `protocols/agentese/laws.py` provides runtime verification of these laws.

---

## The Three-Layer Architecture

### Layer 1: Signal Bridge (`src/reactive/`)

Bridges Python Signals to React state via JSON projection.

```typescript
// useSignal.ts
function useSignal<T>(jsonProjection: T): [T, (updater: (prev: T) => T) => void] {
  const [state, setState] = useState(jsonProjection);

  // Subscribe to SSE updates that carry JSON projections
  useEffect(() => {
    const unsub = sseStream.subscribe((event) => {
      if (event.type === 'state.update') {
        setState(event.payload);
      }
    });
    return unsub;
  }, []);

  return [state, setState];
}
```

### Layer 2: Widget Components (`src/widgets/`)

React components that mirror Python widget structure.

```typescript
// CitizenCard.tsx
interface CitizenCardProps {
  type: 'citizen_card';
  citizen_id: string;
  name: string;
  archetype: string;
  phase: string;
  nphase: string;
  activity: number[];
  capability: number;
  mood: string;
  eigenvectors: { warmth: number; curiosity: number; trust: number };
}

function CitizenCard({ citizen_id, name, archetype, phase, ...props }: CitizenCardProps) {
  const phaseGlyph = PHASE_GLYPHS[phase] || '?';

  return (
    <div className="kgents-citizen-card" data-citizen-id={citizen_id}>
      <div className="header">
        <span className="glyph">{phaseGlyph}</span>
        <span className="name">{name}</span>
        <span className="nphase">[{props.nphase}]</span>
      </div>
      <div className="archetype">{archetype}</div>
      <ActivitySparkline values={props.activity} />
      <CapabilityBar value={props.capability} />
      <div className="mood">{props.mood}</div>
    </div>
  );
}
```

### Layer 3: Composition Primitives (`src/widgets/layout/`)

Layout components that implement `>>` and `//` semantics.

```typescript
// HStack.tsx
interface HStackProps {
  type: 'hstack';
  gap: number;
  children: WidgetJSON[];
}

function HStack({ gap, children }: HStackProps) {
  return (
    <div className="kgents-hstack" style={{ display: 'flex', gap: `${gap * 8}px` }}>
      {children.map((child, i) => (
        <WidgetRenderer key={i} widget={child} />
      ))}
    </div>
  );
}

// VStack.tsx
interface VStackProps {
  type: 'vstack';
  gap: number;
  children: WidgetJSON[];
}

function VStack({ gap, children }: VStackProps) {
  return (
    <div className="kgents-vstack" style={{ display: 'flex', flexDirection: 'column', gap: `${gap * 16}px` }}>
      {children.map((child, i) => (
        <WidgetRenderer key={i} widget={child} />
      ))}
    </div>
  );
}
```

---

## JSON Projection as Protocol

The existing `to_json()` method on widgets becomes the **interface contract** between Python and TypeScript.

### Existing JSON Schema (from `citizen_card.py`)

```json
{
  "type": "citizen_card",
  "citizen_id": "alice",
  "name": "Alice",
  "archetype": "builder",
  "phase": "WORKING",
  "nphase": "ACT",
  "activity": [0.3, 0.5, 0.7, 0.9],
  "capability": 0.85,
  "entropy": 0.1,
  "region": "plaza",
  "mood": "focused",
  "eigenvectors": {
    "warmth": 0.7,
    "curiosity": 0.8,
    "trust": 0.6
  }
}
```

### Composition JSON Schema (from `composable.py`)

```json
{
  "type": "hstack",
  "gap": 1,
  "separator": null,
  "children": [
    { "type": "citizen_card", ... },
    { "type": "citizen_card", ... }
  ]
}
```

### TypeScript Type Generation

Types should be **generated** from Python dataclass definitions:

```typescript
// Generated from CitizenState
interface CitizenCardJSON {
  type: 'citizen_card';
  citizen_id: string;
  name: string;
  archetype: string;
  phase: 'IDLE' | 'SOCIALIZING' | 'WORKING' | 'REFLECTING' | 'RESTING';
  nphase: 'SENSE' | 'ACT' | 'REFLECT';
  activity: number[];
  capability: number;
  entropy: number;
  region: string;
  mood: string;
  eigenvectors: {
    warmth: number;
    curiosity: number;
    trust: number;
  };
}

// Generated from HStack
interface HStackJSON {
  type: 'hstack';
  gap: number;
  separator: string | null;
  children: WidgetJSON[];
}

// Union of all widget types
type WidgetJSON = CitizenCardJSON | HStackJSON | VStackJSON | ColonyDashboardJSON | ...;
```

---

## Streaming Integration

### Current Architecture

The web app uses SSE via `useTownStream` hook, which receives events and updates Zustand stores.

### Target Architecture

SSE events carry **JSON projections** that update widget state directly:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SSE → WIDGET FLOW                                  │
│                                                                              │
│   Backend (Python)                    Frontend (TypeScript)                  │
│   ─────────────────                   ────────────────────                   │
│                                                                              │
│   TownFlux.run()                                                            │
│        │                                                                     │
│        ▼                                                                     │
│   ColonyDashboard(state).to_json()                                          │
│        │                                                                     │
│        ▼                                                                     │
│   SSE: event.data = { type: "colony_dashboard", ... }                       │
│        │                                                                     │
│        │══════════════════════════════════════════════════►                 │
│        │                                                                     │
│                               useTownStream()                               │
│                                    │                                         │
│                                    ▼                                         │
│                               setState(event.data)                          │
│                                    │                                         │
│                                    ▼                                         │
│                               <ColonyDashboard {...state} />                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Event Types

```typescript
// SSE event types aligned with widget JSON
type SSEEvent =
  | { type: 'live.start'; data: { town_id: string } }
  | { type: 'live.event'; data: TownEvent }
  | { type: 'live.state'; data: ColonyDashboardJSON }  // NEW: Full state projection
  | { type: 'live.phase'; data: { phase: TownPhase } }
  | { type: 'live.end'; data: { reason: string } };
```

---

## Generative UI Integration

Building on research from AG-UI Protocol and Vercel AI SDK, the architecture supports **agent-driven UI generation**.

### Tool Results → Widget State

```typescript
// When an agent tool returns data, it becomes widget state
const toolResultHandler = (toolName: string, output: unknown) => {
  switch (toolName) {
    case 'get_citizen':
      return <CitizenCard {...(output as CitizenCardJSON)} />;
    case 'list_coalitions':
      return <CoalitionList coalitions={output as CoalitionJSON[]} />;
    default:
      return <GenericOutput data={output} />;
  }
};
```

### Progressive Rendering

As the LLM generates tool calls, UI updates progressively:

```typescript
// Streaming UI update
const [uiParts, setUIParts] = useState<UIPartState[]>([]);

sseStream.on('tool.start', (event) => {
  setUIParts(prev => [...prev, {
    toolName: event.tool,
    state: 'input-available',
    input: event.input
  }]);
});

sseStream.on('tool.complete', (event) => {
  setUIParts(prev => prev.map(p =>
    p.toolName === event.tool
      ? { ...p, state: 'output-available', output: event.output }
      : p
  ));
});
```

---

## Integration with Existing Systems

### AGENTESE Connection

The Web projection IS the `manifest` aspect for web observers:

```python
# Backend: AGENTESE path resolution
await logos.invoke("world.town.manifest", web_umwelt)
# Returns: ColonyDashboard(state).to_json()
```

```typescript
// Frontend: Consumes manifest
const manifest = await fetch('/v1/town/{id}/manifest');
return <ColonyDashboard {...manifest} />;
```

### Operad Connection

Widget composition follows `TOWN_OPERAD` laws:

| Operad Operation | Widget Composition | React Rendering |
|------------------|-------------------|-----------------|
| `greet(a, b)` | `a >> b` | `<HStack>{a}{b}</HStack>` |
| `stack(a, b)` | `a // b` | `<VStack>{a}{b}</VStack>` |
| `nest(outer, inner)` | Composite widget | Nested components |

### Sheaf Connection

The web UI is a **local section** of the Town sheaf. Different users see different projections of the same underlying state, based on their LOD (Level of Detail) permissions.

```
TownSheaf.section(user_umwelt) → ColonyDashboard.project(WEB)
```

---

## Laws and Verification

### Composition Laws (Must Hold)

```typescript
// Identity
<Fragment>{widget}</Fragment> ≡ widget

// Associativity (HStack)
<HStack>
  <HStack>{a}{b}</HStack>
  {c}
</HStack>
≡
<HStack>
  {a}
  <HStack>{b}{c}</HStack>
</HStack>

// Associativity (VStack)
<VStack>
  <VStack>{a}{b}</VStack>
  {c}
</VStack>
≡
<VStack>
  {a}
  <VStack>{b}{c}</VStack>
</VStack>
```

### Runtime Verification

The `CategoryLawVerifier` pattern extends to TypeScript:

```typescript
function verifyCompositionLaws(widgets: WidgetJSON[]): boolean {
  // Verify (a >> b) >> c produces same DOM structure as a >> (b >> c)
  const leftAssoc = renderToString(<HStack><HStack>{render(a)}{render(b)}</HStack>{render(c)}</HStack>);
  const rightAssoc = renderToString(<HStack>{render(a)}<HStack>{render(b)}{render(c)}</HStack></HStack>);

  // Structural equivalence (ignoring key props)
  return normalizeHTML(leftAssoc) === normalizeHTML(rightAssoc);
}
```

---

## Anti-Patterns

### What This Is NOT

1. **Not a new state management library**
   - We're bridging existing Signals, not replacing React state

2. **Not server-side rendering**
   - JSON projections are hydrated client-side, not rendered server-side

3. **Not a component library**
   - Widgets define structure; styling comes from Tailwind/CSS

4. **Not imperative canvas replacement**
   - Mesa continues using PixiJS, consuming JSON for positions

### Avoid These Patterns

```typescript
// ❌ WRONG: Duplicate state
const [citizens, setCitizens] = useState([]);  // Don't use useState for widget state
useEffect(() => { ... }, []);  // Don't fetch and transform

// ✅ RIGHT: Consume projection
const { data } = useTownStream();  // SSE delivers JSON projection
return <ColonyDashboard {...data} />;  // Render directly
```

```typescript
// ❌ WRONG: Imperative DOM updates
useEffect(() => {
  document.getElementById('citizen-alice').style.color = 'blue';
}, [phase]);

// ✅ RIGHT: Declarative rendering
return <CitizenCard phase={phase} />;  // Phase determines style
```

---

## Existing In-Flight Work

The following work is already underway (from git status):

| File | Status | Integration |
|------|--------|-------------|
| `web/src/hooks/useTownStream.ts` | Modified | Enhanced SSE handling |
| `web/src/pages/Town.tsx` | Modified | Town page improvements |
| `web/src/components/landing/DemoPreview.tsx` | Modified | Demo preview updates |
| `web/vitest.config.ts` | Modified | Test infrastructure |

This spec builds on this work by providing the categorical foundation for the refactoring.

---

## Connection to Spec Principles

| Principle | Web Reactive Manifestation |
|-----------|---------------------------|
| **Tasteful** | Single purpose: project widgets to React |
| **Curated** | One bridge pattern, not multiple approaches |
| **Ethical** | Transparent state flow, no hidden mutations |
| **Joy-Inducing** | Same personality in CLI and web |
| **Composable** | `>>` and `//` operators preserved |
| **Heterarchical** | No fixed component hierarchy |
| **Generative** | JSON schema generates TypeScript types |

---

## Summary

The Web Reactive Projection Protocol unifies the Agent Town frontend with the reactive substrate by:

1. **Adding `RenderTarget.WEB`** that produces JSX-compatible JSON
2. **Using JSON projection as interface contract** between Python and TypeScript
3. **Creating hook bridges** (`useSignal`, `useComputed`) for Signal-React binding
4. **Preserving composition laws** via `HStack`/`VStack` React components
5. **Enabling generative UI** via tool-result-to-widget mapping

The result: **one widget definition, multiple projections**, including the web.

---

*"The browser is just another terminal. The terminal is just another browser. There is only the projection."*
