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

### Pattern E: Duplicate Keys from SSE/WebSocket Streams

**Symptom**: React warning about duplicate keys in lists displaying streamed data

**Signal**:
```
Warning: Encountered two children with the same key, `uuid-here`.
Keys should be unique so that components maintain their identity across updates.
```

**Cause**: Real-time streams can deliver duplicate items (reconnections, server retries, at-least-once delivery):

```typescript
// BAD: Blindly prepending events allows duplicates
source.onmessage = (event) => {
  const item = JSON.parse(event.data);
  setItems((prev) => [item, ...prev].slice(0, maxItems)); // Duplicate IDs!
};
```

**Fix**: Deduplicate at the data layer, not render layer:

```typescript
// GOOD: Check for existing ID before adding
source.onmessage = (event) => {
  const item = JSON.parse(event.data);
  setItems((prev) => {
    const seen = new Set(prev.map((e) => e.id));
    if (seen.has(item.id)) {
      return prev; // Skip duplicate
    }
    return [item, ...prev].slice(0, maxItems);
  });
};
```

**Alternative**: If duplicates are semantically valid (same ID, different payload), use composite keys:

```typescript
// When same ID can have multiple valid entries
<div key={`${item.id}-${item.timestamp}`}>
```

**Prevention**: When building SSE/WebSocket consumers, always assume duplicates are possible.

### Pattern F: Effect Dependency Array Issues

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

### Pattern G: WebSocket + React StrictMode Connect/Disconnect Loops

**Symptom**: WebSocket connects then immediately disconnects, rapid open/close cycles in backend logs

**Signal**: Backend shows:
```
INFO: connection open
INFO: connection closed
INFO: connection open
INFO: connection closed
```

**Cause**: React StrictMode double-mounts components in dev, AND unstable callback references cause effect re-runs:

```typescript
// BAD: connect/disconnect recreated every render, effect re-runs
const connect = useCallback(() => { ... }, [config, handler]); // New ref each render!
const disconnect = useCallback(() => { ... }, [maxAttempts]);

useEffect(() => {
  if (autoConnect) connect();
  return () => disconnect();
}, [autoConnect, connect, disconnect]); // Triggers cleanup → reconnect loop
```

**Fix**: Three-part solution:

1. **Refs for callbacks**: Store handlers and config in refs to avoid recreating functions:
```typescript
const handlersRef = useRef({ onMessage, onError });
handlersRef.current = { onMessage, onError }; // Update ref, not identity

const connect = useCallback(() => {
  ws.onmessage = (e) => handlersRef.current.onMessage(e); // Fresh handler
}, []); // Stable: no callback deps
```

2. **Guard against double-connect**: Use ref to track connection state:
```typescript
const hasAutoConnected = useRef(false);
const isDisconnecting = useRef(false);

const connect = useCallback(() => {
  if (wsRef.current?.readyState === WebSocket.OPEN) return; // Already connected
  if (wsRef.current?.readyState === WebSocket.CONNECTING) return; // Connecting
  isDisconnecting.current = false;
  // ... connect logic
}, []);
```

3. **Intentional disconnect tracking**: Prevent auto-reconnect on cleanup:
```typescript
const disconnect = useCallback(() => {
  isDisconnecting.current = true; // Mark intentional
  wsRef.current?.close(1000, 'User disconnect');
}, []);

// In onclose handler:
ws.onclose = (event) => {
  if (isDisconnecting.current) return; // Don't auto-reconnect
  // ... exponential backoff reconnect
};
```

4. **StrictMode-safe effect**: Only depend on primitive config, not functions:
```typescript
useEffect(() => {
  if (autoConnect && !hasAutoConnected.current) {
    hasAutoConnected.current = true;
    connect();
  }
  return () => {
    disconnect();
    hasAutoConnected.current = false; // Allow reconnect on true remount
  };
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, [autoConnect]); // Intentionally omit stable functions
```

**Prevention**: When building WebSocket hooks:
- Store all dynamic config in refs, not useCallback deps
- Always check connection state before connecting
- Track intentional vs unintentional disconnects
- Use a `hasConnected` ref for StrictMode protection

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
[ ] No duplicate keys? (deduplicate streamed data by ID)
[ ] No connect/disconnect loops? (StrictMode + stable refs)
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
- **Don't assume stream data is unique**: Always deduplicate at the hook/store layer, not in render
- **Don't ignore StrictMode**: Dev-mode double-mount exposes real bugs; fix the root cause, don't disable StrictMode
- **Don't put connect/disconnect in effect deps**: Store config in refs, make functions stable with `[]` deps
