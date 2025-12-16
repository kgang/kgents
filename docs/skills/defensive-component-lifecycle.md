# Defensive Component Lifecycle

Patterns for robust React component error handling, loading states, and graceful degradation in the Agent Town webapp.

## Core Components

### Error Boundary

Catch render errors in the component tree with automatic reset on route changes.

```typescript
// src/components/error/ErrorBoundary.tsx

// Wrap at app level with route-based reset
import { useLocation } from 'react-router-dom';
import { ErrorBoundary } from '@/components/error/ErrorBoundary';

function App() {
  const location = useLocation();

  return (
    <ErrorBoundary resetKeys={[location.pathname]}>
      <Routes>...</Routes>
    </ErrorBoundary>
  );
}

// Wrap specific sections with custom fallback
<ErrorBoundary
  fallback={<CustomError />}
  onError={(error, info) => logToTelemetry(error)}
>
  <RiskyComponent />
</ErrorBoundary>
```

**Key Props:**
- `resetKeys`: Array of values that trigger reset when changed (e.g., route path)
- `fallback`: Custom fallback UI (defaults to ElasticPlaceholder)
- `onError`: Callback for logging/telemetry

### useAsyncState Hook

Eliminate loading/error/data boilerplate.

```typescript
// src/hooks/useAsyncState.ts

const { state, execute, setData, setError, reset } = useAsyncState<Town>({
  onSuccess: (data) => console.log('Loaded:', data),
  onError: (error) => showError('Load failed', error),
});

// Execute async operation
useEffect(() => {
  execute(townApi.get(townId));
}, [townId, execute]);

// Render based on state
if (state.isLoading) return <Loading />;
if (state.error) return <Error message={state.error} />;
if (state.data) return <Town data={state.data} />;
```

**State Shape:**
```typescript
interface AsyncState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  status: 'idle' | 'loading' | 'success' | 'error';
}
```

**Features:**
- Automatic request cancellation (stale requests ignored)
- Axios-style error extraction (`response.data.detail`)
- Callbacks for success/error
- Manual `setData`/`setError` for optimistic updates

### Toast Notifications

Non-blocking notifications using existing uiStore infrastructure.

```typescript
// Anywhere in app
import { showSuccess, showError, showInfo } from '@/stores/uiStore';

showSuccess('Town created!', 'Your new town is ready.');
showError('Connection lost', 'Check your internet');
showInfo('Tip', 'Click a citizen to see details');

// ToastContainer renders in Layout.tsx automatically
```

**Toast Types:**
| Type | Emoji | Duration | Use Case |
|------|-------|----------|----------|
| `info` | 💡 | 3s | Tips, hints |
| `success` | ✅ | 3s | Completed actions |
| `warning` | ⚠️ | 5s | Non-blocking issues |
| `error` | 🚫 | 5s | Failures, errors |

### useOnlineStatus Hook

Track browser connectivity with automatic toast notifications.

```typescript
// src/hooks/useOnlineStatus.ts

function Layout() {
  const isOnline = useOnlineStatus();

  return (
    <div>
      {!isOnline && <OfflineBanner />}
      <main>{children}</main>
    </div>
  );
}
```

Automatically shows:
- "Back Online" info toast when connectivity restored
- "Offline" error toast when connection lost

## Integration Points

### App.tsx

```typescript
import { ErrorBoundary } from './components/error/ErrorBoundary';
import { useLocation } from 'react-router-dom';

function App() {
  const location = useLocation();

  return (
    <ErrorBoundary resetKeys={[location.pathname]}>
      <Suspense fallback={<LoadingFallback />}>
        <Routes>
          {/* routes */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
}
```

### Layout.tsx

```typescript
import { ToastContainer } from '@/components/feedback/ToastContainer';
import { useOnlineStatus } from '@/hooks/useOnlineStatus';

function Layout() {
  useOnlineStatus(); // Shows toasts on connectivity changes

  return (
    <div>
      {/* layout content */}
      <ToastContainer />
    </div>
  );
}
```

## Critical Insights

### Error Boundary Placement

1. **App-level**: Wrap entire app with route-based reset
2. **Feature-level**: Wrap risky sections (dynamic imports, external data)
3. **Never in loops**: Each boundary is expensive

### Stale Closure Prevention

useAsyncState uses request ID tracking instead of AbortController:

```typescript
// Each execute() increments requestIdRef
// Results only applied if requestId matches current
const currentRequestId = ++requestIdRef.current;
// ... await promise ...
if (currentRequestId !== requestIdRef.current) {
  return null; // Stale request, ignore
}
```

### Toast vs Inline Errors

| Scenario | Use Toast | Use Inline |
|----------|-----------|------------|
| Background operation failed | ✓ | |
| Form validation error | | ✓ |
| API call failed (retryable) | ✓ | |
| Page load failed | | ✓ |
| Success confirmation | ✓ | |
| Missing required data | | ✓ |

### ElasticPlaceholder Integration

Error boundaries use ElasticPlaceholder for consistent error UI:

```typescript
// ErrorBoundary default fallback
<ElasticPlaceholder
  state="error"
  error={this.state.error?.message}
  onRetry={this.reset}
/>
```

ElasticPlaceholder recognizes error types:
- `NETWORK_ERROR` → 🌐 "Lost connection"
- `NOT_FOUND` / `404` → 🔍 "Nothing here"
- `RATE_LIMITED` / `429` → 🐢 "Slow down"
- `SERVER_ERROR` / `500` → 🔧 "Something went sideways"

## File Structure

```
src/
├── components/
│   ├── error/
│   │   ├── ErrorBoundary.tsx    # React error boundary
│   │   └── index.ts
│   ├── feedback/
│   │   ├── Toast.tsx            # Individual toast
│   │   ├── ToastContainer.tsx   # Renders from uiStore
│   │   └── index.ts
│   └── elastic/
│       └── ElasticPlaceholder.tsx  # Loading/empty/error states
├── hooks/
│   ├── useAsyncState.ts         # Async state management
│   └── useOnlineStatus.ts       # Connectivity tracking
├── pages/
│   └── NotFound.tsx             # 404 page
└── stores/
    └── uiStore.ts               # notifications[], showError(), etc.
```

## Testing Patterns

### Error Boundary Tests

```typescript
// Component that throws for testing
function ThrowingComponent({ shouldThrow }: { shouldThrow?: boolean }): ReactElement {
  if (shouldThrow) throw new Error('Test error');
  return <div>Content</div>;
}

// Suppress console.error in tests
beforeEach(() => {
  console.error = vi.fn();
});
```

### useAsyncState Tests

```typescript
// Test stale request handling
act(() => { result.current.execute(slowPromise1); });
act(() => { result.current.execute(slowPromise2); }); // Invalidates first
await act(async () => { resolve1('first'); }); // Ignored
expect(result.current.state.isLoading).toBe(true); // Still waiting for second
```

### Toast Tests

```typescript
// Test auto-dismiss
vi.useFakeTimers();
render(<Toast notification={{ duration: 3000, ... }} onDismiss={mock} />);
act(() => vi.advanceTimersByTime(3000));
expect(mock).toHaveBeenCalled();
```

## Anti-Patterns

```
❌ Swallowing errors silently
✓ Always surface to user or logs

❌ Missing loading states
✓ Show skeleton/spinner during async ops

❌ Error boundary inside render loop
✓ Place boundaries at route/feature level

❌ Toasts for everything
✓ Toast for non-blocking, inline for blocking

❌ Manual try/catch in every component
✓ Use useAsyncState or ErrorBoundary
```

## See Also

- `src/components/elastic/ElasticPlaceholder.tsx` - Loading/error states
- `src/stores/uiStore.ts` - Notification infrastructure
- `docs/skills/react-realtime-debugging.md` - Stale closure patterns
