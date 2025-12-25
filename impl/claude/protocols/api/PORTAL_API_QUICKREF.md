# Portal API Quick Reference

**For Frontend Developers**

## Endpoints

```typescript
// Emit a portal
POST /api/chat/portal/emit
Body: {
  destination: string;        // File path
  edge_type?: string;         // Default: "context"
  access?: "read" | "readwrite";  // Default: "read"
  auto_expand?: boolean;      // Default: true
}
Response: PortalEmission

// Write through portal
POST /api/chat/portal/write
Body: {
  portal_id: string;
  content: string;
}
Response: {
  success: boolean;
  portal_id: string;
  bytes_written: number;
  new_content_hash: string;
  error_message: string;
}
```

## TypeScript Types

```typescript
interface PortalEmission {
  portal_id: string;
  destination: string;
  edge_type: string;
  access: "read" | "readwrite";
  content_preview: string | null;
  content_full: string | null;
  line_count: number;
  exists: boolean;
  auto_expand: boolean;
  emitted_at: string;  // ISO datetime
}

interface Turn {
  turn_number: number;
  user_message: Message;
  assistant_response: Message;
  tools_used: ToolUse[];
  portal_emissions: PortalEmission[];  // NEW!
  evidence_delta: EvidenceDelta;
  confidence: number;
  started_at: string;
  completed_at: string;
}
```

## Usage Examples

### Emit a read-only portal

```typescript
const response = await fetch('/api/chat/portal/emit', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    destination: '/path/to/file.txt',
    access: 'read',
  }),
});

const emission: PortalEmission = await response.json();

// Display in UI
if (emission.exists) {
  console.log(`Portal to ${emission.destination}`);
  console.log(`Content: ${emission.content_preview || emission.content_full}`);
}
```

### Emit a readwrite portal

```typescript
const emission = await fetch('/api/chat/portal/emit', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    destination: '/path/to/file.txt',
    access: 'readwrite',
    edge_type: 'edits',
  }),
}).then(r => r.json());

// Store portal_id for later writes
const portalId = emission.portal_id;
```

### Write through portal

```typescript
const writeResult = await fetch('/api/chat/portal/write', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    portal_id: portalId,
    content: 'Updated content\n',
  }),
}).then(r => r.json());

if (writeResult.success) {
  console.log(`Wrote ${writeResult.bytes_written} bytes`);
} else {
  console.error(writeResult.error_message);
}
```

### React Component Example

```tsx
import { useState } from 'react';

function PortalViewer({ destination }: { destination: string }) {
  const [portal, setPortal] = useState<PortalEmission | null>(null);
  const [content, setContent] = useState('');

  const openPortal = async () => {
    const response = await fetch('/api/chat/portal/emit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        destination,
        access: 'readwrite',
      }),
    });
    const emission = await response.json();
    setPortal(emission);
    setContent(emission.content_full || '');
  };

  const savePortal = async () => {
    if (!portal) return;

    const response = await fetch('/api/chat/portal/write', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        portal_id: portal.portal_id,
        content,
      }),
    });
    const result = await response.json();

    if (!result.success) {
      alert(result.error_message);
    }
  };

  return (
    <div>
      {!portal ? (
        <button onClick={openPortal}>Open Portal</button>
      ) : (
        <div>
          <h3>Portal to {portal.destination}</h3>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            disabled={portal.access === 'read'}
          />
          {portal.access === 'readwrite' && (
            <button onClick={savePortal}>Save</button>
          )}
        </div>
      )}
    </div>
  );
}
```

## Error Handling

```typescript
try {
  const response = await fetch('/api/chat/portal/emit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ destination: '/path/to/file.txt' }),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('Portal emission failed:', error.detail);
    return;
  }

  const emission: PortalEmission = await response.json();

  if (!emission.exists) {
    console.warn('File does not exist:', emission.destination);
  }

} catch (err) {
  console.error('Network error:', err);
}
```

## SSE Streaming with Portals

When K-gent uses portals during chat, they appear in the turn's `portal_emissions`:

```typescript
const eventSource = new EventSource(`/api/chat/${sessionId}/send`);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'done') {
    const turn = data.turn as Turn;

    // Display any portal emissions
    turn.portal_emissions.forEach(emission => {
      console.log('Portal emitted:', emission.destination);
      // Render portal in UI
      renderPortal(emission);
    });
  }
};
```

## Best Practices

1. **Check `exists` before using content**: File may not exist
2. **Check `access` before writing**: Don't show edit UI for read-only portals
3. **Use `content_preview` for long files**: Avoid rendering huge files
4. **Handle errors gracefully**: Network errors, permission errors, etc.
5. **Store `portal_id`**: You'll need it for writes
6. **Debounce writes**: Don't write on every keystroke
7. **Show `emitted_at`**: Help users know when content was loaded

## Common Patterns

### Auto-save on edit
```typescript
const [content, setContent] = useState(portal.content_full);
const [saveTimer, setSaveTimer] = useState<number | null>(null);

const handleChange = (newContent: string) => {
  setContent(newContent);

  // Debounce save
  if (saveTimer) clearTimeout(saveTimer);
  const timer = setTimeout(() => savePortal(newContent), 1000);
  setSaveTimer(timer);
};
```

### Refresh portal content
```typescript
const refreshPortal = async () => {
  // Re-emit to get fresh content
  const response = await fetch('/api/chat/portal/emit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      destination: portal.destination,
      access: portal.access,
    }),
  });
  const fresh = await response.json();
  setPortal(fresh);
  setContent(fresh.content_full || '');
};
```

### Portal with diff view
```typescript
const [original, setOriginal] = useState(portal.content_full);
const [edited, setEdited] = useState(portal.content_full);

const showDiff = () => {
  // Use a diff library to show changes
  const diff = computeDiff(original, edited);
  renderDiff(diff);
};
```
