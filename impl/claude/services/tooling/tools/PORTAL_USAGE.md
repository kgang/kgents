# Portal Tools Usage Guide

Portal tools enable inline document access during chat sessions. Instead of navigating away, portals bring content directly into the conversation with read/write access.

## Quick Start

```python
from services.tooling.tools import PortalTool, PortalWriteTool
from services.tooling.contracts import PortalRequest, PortalWriteRequest

# Open a portal with read access
portal_tool = PortalTool()
emission = await portal_tool.invoke(
    PortalRequest(
        destination="spec/agents/p-gent.md",
        edge_type="references",
        access="read",
        preview_lines=10,
        auto_expand=True
    )
)

# Portal content is now available
print(emission.content_preview)  # First 10 lines
print(emission.content_full)     # Full content
```

## Portal Emission

When a portal is opened, it returns a `PortalEmission` with:

- `portal_id`: Unique identifier for this portal session
- `destination`: Path to the file/resource
- `edge_type`: Type of relationship (context, implements, tests, etc.)
- `access`: "read" or "readwrite"
- `content_preview`: First N lines (if file > preview_lines)
- `content_full`: Complete file content
- `line_count`: Total lines in file
- `exists`: Whether destination was found
- `auto_expand`: Should UI auto-expand this portal?
- `emitted_at`: ISO timestamp

## Writing Through Portals

Portals opened with `access="readwrite"` allow modifications:

```python
# Open portal with write access
emission = await portal_tool.invoke(
    PortalRequest(
        destination="impl/service.py",
        edge_type="implements",
        access="readwrite"
    )
)

# Write through the portal
write_tool = PortalWriteTool()
result = await write_tool.invoke(
    PortalWriteRequest(
        portal_id=emission.portal_id,
        content="# Updated implementation\n..."
    )
)

print(result.success)           # True
print(result.bytes_written)     # 123
print(result.new_content_hash)  # SHA-256 of new content
```

## Access Control

### Read-Only Portals (L1 Trust)

```python
emission = await portal_tool.invoke(
    PortalRequest(destination="file.txt", access="read")
)
# Can view content, cannot modify
```

### Read/Write Portals (L2 Trust for writes)

```python
emission = await portal_tool.invoke(
    PortalRequest(destination="file.txt", access="readwrite")
)
# Can view AND modify through PortalWriteTool
```

### Causal Constraints

1. **Portal must be open** before writing:
   ```python
   # This raises CausalityViolation
   await write_tool.invoke(
       PortalWriteRequest(portal_id="nonexistent", content="...")
   )
   ```

2. **Portal must have write access**:
   ```python
   # Read-only portal
   emission = await portal_tool.invoke(
       PortalRequest(destination="file.txt", access="read")
   )

   # This raises CausalityViolation
   await write_tool.invoke(
       PortalWriteRequest(portal_id=emission.portal_id, content="...")
   )
   ```

## Edge Types

Common edge types (customize as needed):

- `context`: General context/background
- `implements`: Implementation of a spec
- `tests`: Test coverage
- `references`: External references
- `extends`: Inheritance/extension
- `imports`: Code dependencies

## Session State

Portals are tracked in session state:

```python
from services.tooling.tools import get_open_portals, reset_open_portals

# Get all open portals
portals = get_open_portals()
for portal_id, portal in portals.items():
    print(f"{portal_id}: {portal.destination} ({portal.access})")

# Clear portal registry (testing)
reset_open_portals()
```

## File System Integration

Portal tools use `FileEditGuard` for all file operations:

- Read operations populate FileEditGuard cache
- Write operations respect cache constraints
- All safety checks from FileEditGuard apply

## Error Handling

### File Not Found

```python
emission = await portal_tool.invoke(
    PortalRequest(destination="/nonexistent/file.txt")
)
# emission.exists == False
# emission.content_full == None
```

### Permission Denied

```python
# Raises ToolError
await portal_tool.invoke(
    PortalRequest(destination="/root/forbidden.txt")
)
```

### Directory Path

```python
# Raises ToolError (portals are for files, not directories)
await portal_tool.invoke(
    PortalRequest(destination="/some/directory")
)
```

## Integration Points

### Chat Sessions

Portal emissions are designed for chat streaming:

```python
# Emit portal in chat
emission = await portal_tool.invoke(request)

# Stream to client
await stream.emit({
    "type": "portal",
    "data": emission.to_dict()
})
```

### Frontend (React)

```tsx
import { PortalToken } from '@/components/tokens/PortalToken';

<PortalToken
  edgeType={emission.edge_type}
  destinations={[{
    path: emission.destination,
    preview: emission.content_preview,
    exists: emission.exists
  }]}
  onNavigate={(path) => console.log('Navigate to:', path)}
  defaultExpanded={emission.auto_expand}
/>
```

## Best Practices

1. **Use descriptive edge types**: `implements` > `context` when linking spec to code
2. **Set appropriate preview_lines**: 5-10 for inline, 20+ for detailed
3. **Default to read access**: Only use `readwrite` when modification is intended
4. **Track portal IDs**: Store portal_id in conversation context for later writes
5. **Clean up portals**: Call `reset_open_portals()` between sessions (testing)

## Examples

### Spec to Implementation Portal

```python
emission = await portal_tool.invoke(
    PortalRequest(
        destination="impl/claude/services/brain/cortex.py",
        edge_type="implements",
        access="read",
        preview_lines=15
    )
)
```

### Test Coverage Portal

```python
emission = await portal_tool.invoke(
    PortalRequest(
        destination="impl/claude/services/brain/_tests/test_cortex.py",
        edge_type="tests",
        access="readwrite",  # May need to add tests
        preview_lines=20
    )
)
```

### Documentation Portal

```python
emission = await portal_tool.invoke(
    PortalRequest(
        destination="spec/services/brain.md",
        edge_type="references",
        access="read",
        auto_expand=True
    )
)
```

## See Also

- `/Users/kentgang/git/kgents/impl/claude/services/tooling/tools/portal.py` - Implementation
- `/Users/kentgang/git/kgents/impl/claude/services/tooling/contracts.py` - Type definitions
- `/Users/kentgang/git/kgents/impl/claude/web/src/components/tokens/PortalToken.tsx` - Frontend component
- `spec/protocols/portal-token.md` - Portal token specification
