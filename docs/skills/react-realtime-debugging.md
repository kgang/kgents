# Skill: React Real-time UI Debugging

Patterns for debugging React applications with real-time features (SSE, WebSockets, live updates).

## When to Use

- UI loads but doesn't update in real-time
- SSE/WebSocket connections seem to fail silently
- State changes don't propagate to visual components
- "Works in curl but not in browser" scenarios

## The Debugging Stack

### 1. Verify Backend First

Always confirm the backend works before debugging frontend:

```bash
# Test SSE endpoint directly
curl -N "http://localhost:8000/v1/town/{id}/live?speed=2&phases=1" | head -20

# Test through Vite proxy (what browser actually uses)
curl -N "http://localhost:3000/v1/town/{id}/live?speed=2&phases=1" | head -20
```

If curl works but browser doesn't, the issue is frontend.

### 2. Check Browser Console

Add strategic logging at connection points:

```typescript
console.log('[SSE] Connecting to:', url);
console.log('[SSE] Effect deps - autoConnect:', autoConnect, 'isPlaying:', isPlaying);
console.log('[SSE] Event received:', event.type, event.data);
```

### 3. Trace the State Flow

For Zustand stores:
1. Does the action get called? (log in action)
2. Does state update? (React DevTools or log after set)
3. Does component re-render? (log in component body)
4. Does derived data update? (check selectors)

## Common Failure Patterns

### Pattern A: Immer MapSet Plugin Not Enabled

**Symptom**: Error about MapSet plugin when store uses `Map` or `Set`

**Signal**:
```
Error: [Immer] The plugin for 'MapSet' has not been loaded into Immer.
```

**Fix**: Enable at app entry point:
```typescript
// main.tsx
import { enableMapSet } from 'immer';
enableMapSet();
```

**Prevention**: When creating stores with Map/Set, immediately add the plugin.

### Pattern B: Stale Closures in Event Handlers

**Symptom**: SSE/WebSocket receives events but state doesn't update, or updates with stale values

**Signal**: Console shows events arriving, but UI frozen or showing old data

**Cause**: Event handlers capture callbacks at creation time, not invocation time:

```typescript
// BAD: handleEvent is stale when eventSource calls it
const connect = useCallback(() => {
  eventSource.addEventListener('event', (e) => {
    handleEvent(JSON.parse(e.data)); // Stale!
  });
}, [townId]); // handleEvent not in deps
```

**Fix**: Use a ref to always get fresh handlers:

```typescript
// GOOD: Ref always has current handlers
const handlersRef = useRef({ addEvent, updateState });
handlersRef.current = { addEvent, updateState }; // Update every render

const connect = useCallback(() => {
  eventSource.addEventListener('event', (e) => {
    handlersRef.current.addEvent(JSON.parse(e.data)); // Fresh!
  });
}, [townId]); // No closure dependency needed
```

### Pattern C: Silent API Failures

**Symptom**: Page shows nothing, no errors visible

**Signal**: Network tab shows 404/500, but UI just blank

**Cause**: Error caught but not surfaced:

```typescript
// BAD: Silent failure
try {
  const data = await api.get(id);
  setState(data);
} catch (err) {
  console.error(err); // Only in console
}
```

**Fix**: Always have explicit loading/error/success states:

```typescript
// GOOD: Explicit state machine
const [state, setState] = useState<'loading' | 'loaded' | 'error'>('loading');
const [error, setError] = useState<string | null>(null);

try {
  setState('loading');
  const data = await api.get(id);
  setState('loaded');
} catch (err) {
  setError(err.message);
  setState('error');
}

// Render different UI for each state
if (state === 'loading') return <Spinner />;
if (state === 'error') return <ErrorPage message={error} />;
return <Content />;
```

### Pattern D: React Navigation Timing Issues

**Symptom**: After `navigate()`, component shows stale data or re-fetches incorrectly

**Signal**: URL changes but data doesn't match, or unnecessary API calls

**Cause**: `navigate()` can cause component remount or effect re-runs with timing issues

**Fix**: For same-component URL updates, use `history.replaceState`:

```typescript
// When staying in same component but updating URL
window.history.replaceState(null, '', `/town/${newId}`);

// Then update state directly instead of relying on param change
setTownId(newId);
setCitizens(data.citizens);
```

### Pattern E: Effect Dependency Array Issues

**Symptom**: Effect doesn't run when expected, or runs too often

**Signal**: Console logs show effect not triggering on state change

**Cause**: Missing dependencies or callback identity changes:

```typescript
// BAD: townId changes won't trigger because connect has stale townId
useEffect(() => {
  if (isPlaying) connect();
}, [isPlaying, connect]); // connect depends on townId but effect doesn't see it

// GOOD: Include all relevant state
useEffect(() => {
  if (isPlaying && townId) connect();
}, [isPlaying, townId, connect]);
```

## Debugging Checklist

```
[ ] Backend endpoint works via curl?
[ ] Vite proxy forwards requests correctly?
[ ] Immer plugins enabled for Map/Set?
[ ] Loading/error states render visibly?
[ ] SSE/WS connection established? (check Network tab)
[ ] Events received? (console.log in handler)
[ ] State updates? (React DevTools or logs)
[ ] Component re-renders? (log in component body)
[ ] No stale closures? (use refs for event handlers)
[ ] Effect dependencies complete?
```

## Testing Real-time Features

```typescript
// Mock SSE for unit tests
class MockEventSource {
  listeners: Record<string, Function[]> = {};

  addEventListener(type: string, fn: Function) {
    this.listeners[type] = [...(this.listeners[type] || []), fn];
  }

  emit(type: string, data: unknown) {
    this.listeners[type]?.forEach(fn => fn({ data: JSON.stringify(data) }));
  }
}

// In test
const mockSSE = new MockEventSource();
vi.stubGlobal('EventSource', vi.fn(() => mockSSE));

// Trigger event
mockSSE.emit('live.event', { operation: 'greet', participants: ['A', 'B'] });

// Assert state updated
expect(store.getState().events).toHaveLength(1);
```

## Related Skills

- `test-patterns.md` - Testing conventions
- `agent-town-visualization.md` - Town UI specifics
- `handler-patterns.md` - Backend handler patterns

## Anti-Patterns

- **Don't ignore loading states**: "It works on my machine" often means slow network reveals race conditions
- **Don't trust silent catch blocks**: Every catch should surface to UI or logging
- **Don't use `navigate()` for same-component updates**: Use history API or state directly
- **Don't put callbacks in effect deps without understanding identity**: Wrap in useCallback or use refs
