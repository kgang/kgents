# Portal Resolver Usage Guide

## Overview

The portal resolver API enables PortalToken components to resolve portal URIs on-demand and display expanded content.

## Basic Usage

```tsx
import { usePortalResolver } from '@/hooks/usePortalResolver';
import type { ResolvedResource } from './types';

function PortalToken({ uri }: { uri: string }) {
  const { resolvePortal, loading, error } = usePortalResolver();
  const [resource, setResource] = React.useState<ResolvedResource | null>(null);
  const [expanded, setExpanded] = React.useState(false);

  const handleExpand = async () => {
    if (!expanded) {
      const resolved = await resolvePortal(uri);
      setResource(resolved);
      setExpanded(true);
    } else {
      setExpanded(false);
    }
  };

  return (
    <div className="portal-token">
      <button onClick={handleExpand} disabled={loading}>
        {expanded ? '▼' : '▶'} {uri}
      </button>

      {loading && <span className="loading">Loading...</span>}
      {error && <span className="error">{error}</span>}

      {expanded && resource && (
        <div className="portal-content">
          <h4>{resource.title}</h4>
          <p className="preview">{resource.preview}</p>
          {resource.exists ? (
            <div className="content">{renderContent(resource)}</div>
          ) : (
            <div className="not-found">Resource not found</div>
          )}
        </div>
      )}
    </div>
  );
}

function renderContent(resource: ResolvedResource) {
  switch (resource.resource_type) {
    case 'file':
      return <pre>{resource.content}</pre>;
    case 'chat':
      return <ChatSession session={resource.content} />;
    case 'mark':
      return <MarkDisplay mark={resource.content} />;
    default:
      return <pre>{JSON.stringify(resource.content, null, 2)}</pre>;
  }
}
```

## With Auto-Expansion

```tsx
function PortalTokenWithAutoExpand({ uri, autoExpand = false }: {
  uri: string;
  autoExpand?: boolean;
}) {
  const { resolvePortal } = usePortalResolver();
  const [resource, setResource] = React.useState<ResolvedResource | null>(null);

  React.useEffect(() => {
    if (autoExpand) {
      resolvePortal(uri).then(setResource);
    }
  }, [uri, autoExpand]);

  return resource ? (
    <div className="portal-expanded">{renderContent(resource)}</div>
  ) : (
    <a href="#" onClick={() => resolvePortal(uri).then(setResource)}>
      {uri}
    </a>
  );
}
```

## One-Shot Resolution (No State)

```tsx
import { resolvePortalURI } from '@/hooks/usePortalResolver';

async function handlePortalClick(uri: string) {
  const resource = await resolvePortalURI(uri);
  if (resource) {
    console.log('Resolved:', resource);
    // Show modal, navigate, etc.
  } else {
    console.error('Failed to resolve:', uri);
  }
}
```

## Error Handling

```tsx
function RobustPortalToken({ uri }: { uri: string }) {
  const { resolvePortal, loading, error } = usePortalResolver();
  const [resource, setResource] = React.useState<ResolvedResource | null>(null);

  const handleExpand = async () => {
    const resolved = await resolvePortal(uri);

    if (resolved) {
      setResource(resolved);
    } else {
      // Handle error (already tracked in hook state)
      console.error('Resolution failed:', error);
    }
  };

  if (loading) {
    return <Spinner />;
  }

  if (error) {
    return (
      <div className="portal-error">
        <span className="error-icon">⚠️</span>
        <span className="error-message">{error}</span>
        <button onClick={handleExpand}>Retry</button>
      </div>
    );
  }

  return (
    <button onClick={handleExpand}>
      {resource ? '📂' : '📄'} {uri}
    </button>
  );
}
```

## Integration with PortalToken Component

The existing `PortalToken` component in `components/tokens/PortalToken.tsx` can be enhanced:

```tsx
// Before (static)
export function PortalToken({ uri, destinations }: PortalTokenProps) {
  return (
    <button className="portal-token">
      {uri} → {destinations.join(', ')}
    </button>
  );
}

// After (dynamic resolution)
export function PortalToken({ uri, destinations }: PortalTokenProps) {
  const { resolvePortal, loading } = usePortalResolver();
  const [expanded, setExpanded] = React.useState(false);
  const [resource, setResource] = React.useState<ResolvedResource | null>(null);

  const handleExpand = async () => {
    if (!expanded) {
      const resolved = await resolvePortal(uri);
      setResource(resolved);
      setExpanded(true);
    } else {
      setExpanded(false);
    }
  };

  return (
    <div className="portal-token">
      <button onClick={handleExpand} disabled={loading}>
        {expanded ? '▼' : '▶'} {uri}
      </button>

      {expanded && resource && (
        <PortalExpansion resource={resource} />
      )}
    </div>
  );
}
```

## API Reference

### `usePortalResolver()`

Returns:
- `resolvePortal: (uri: string) => Promise<ResolvedResource | null>` - Resolve a portal URI
- `loading: boolean` - Whether a resolution is in progress
- `error: string | null` - Error message if resolution failed

### `resolvePortalURI(uri: string): Promise<ResolvedResource | null>`

One-shot resolution without hook state. Returns `null` on error.

### `ResolvedResource`

```typescript
interface ResolvedResource {
  uri: string;                     // Original URI
  resource_type: string;           // "file", "chat", "mark", etc.
  exists: boolean;                 // Whether resource exists
  title: string;                   // Display title
  preview: string;                 // Short preview text
  content: unknown;                // Full content (type varies)
  actions: string[];               // Available actions
  metadata: Record<string, unknown>; // Resource-specific metadata
}
```

## Supported Resource Types

| Type | Example URI | Content Type |
|------|-------------|--------------|
| `file:` | `file:spec/protocols/witness.md` | `string` (file contents) |
| `chat:` | `chat:session-abc123` | `object` (session data) |
| `mark:` | `mark:mark-xyz` | `object` (mark data) |
| `trace:` | `trace:trace-456` | `object` (trace data) |
| `evidence:` | `evidence:evidence-789` | `object` (evidence bundle) |
| `constitutional:` | `constitutional:const-abc` | `object` (score data) |
| `crystal:` | `crystal:crystal-xyz` | `object` (crystal data) |

## Next Steps

1. Integrate `usePortalResolver` into existing `PortalToken` component
2. Add caching layer to avoid repeated API calls
3. Implement permission-aware resolution (pass observer context)
4. Add loading skeletons for better UX
5. Support batch resolution for multiple portals on a page

---

*Ready to use. Wire it into PortalToken and enjoy seamless resource expansion!*
