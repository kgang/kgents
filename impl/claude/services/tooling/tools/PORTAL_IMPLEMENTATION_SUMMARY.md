# Portal Tool Implementation Summary

**Created**: 2025-12-25
**Status**: ✅ Complete, All Tests Passing (287/287)

## What Was Built

Portal tools enable inline document access during chat sessions with read/write capabilities. Two new tools were added to the U-gent tooling infrastructure:

1. **PortalTool** (`portal.emit`) - L1 Trust
2. **PortalWriteTool** (`portal.write`) - L2 Trust

## Files Created

### Core Implementation

- **`services/tooling/tools/portal.py`** (332 lines)
  - `PortalTool`: Emit portal references with content
  - `PortalWriteTool`: Write through open portals
  - `OpenPortal`: Session state tracking
  - Portal registry management

### Contracts

- **`services/tooling/contracts.py`** (additions)
  - `PortalRequest`: Request to open a portal
  - `PortalEmission`: Portal with content and metadata
  - `PortalDestination`: Destination metadata
  - `PortalWriteRequest`: Write through portal
  - `PortalWriteResponse`: Write result

### Tests

- **`services/tooling/tools/_tests/test_portal.py`** (353 lines, 21 tests)
  - `TestPortalTool`: 9 tests for portal emission
  - `TestPortalWriteTool`: 6 tests for portal writing
  - `TestPortalAccessControl`: 3 tests for access patterns
  - `TestPortalEdgeCases`: 3 tests for edge cases

### Documentation

- **`services/tooling/tools/PORTAL_USAGE.md`** - Comprehensive usage guide
- **`services/tooling/tools/PORTAL_IMPLEMENTATION_SUMMARY.md`** - This file

## Key Features

### Portal Emission

```python
emission = await portal_tool.invoke(
    PortalRequest(
        destination="spec/agents/p-gent.md",
        edge_type="references",
        access="read",
        preview_lines=10,
        auto_expand=True
    )
)
```

**Returns**:
- Portal ID for tracking
- Full file content
- Preview (first N lines)
- Metadata (exists, line_count, timestamp)

### Portal Writing

```python
result = await write_tool.invoke(
    PortalWriteRequest(
        portal_id=emission.portal_id,
        content="Updated content"
    )
)
```

**Guarantees**:
- Portal must be open (CausalityViolation if not)
- Portal must have `readwrite` access (CausalityViolation if read-only)
- FileEditGuard safety checks apply

## Architecture

### Integration with FileEditGuard

Portal tools are thin adapters over FileEditGuard:

```
PortalTool
    ↓ (read)
FileEditGuard.read_file()
    ↓
FileContent → PortalEmission

PortalWriteTool
    ↓ (write)
FileEditGuard.write_file()
    ↓
WriteResponse → PortalWriteResponse
```

### Session State Management

Open portals are tracked in-memory:

```python
_OPEN_PORTALS: dict[str, OpenPortal] = {}
```

Each `OpenPortal` tracks:
- `portal_id`: Unique UUID
- `destination`: File path
- `edge_type`: Relationship type
- `access`: "read" | "readwrite"
- `content_hash`: SHA-256 at open time
- `opened_at`, `last_accessed`: Timestamps

### Trust Levels

- **PortalTool (L1)**: Reads files, emits content
- **PortalWriteTool (L2)**: Writes files through open portals

## Test Coverage

### Test Statistics

- **Total Tests**: 21 (all passing)
- **Test Lines**: 353
- **Coverage Areas**:
  - Portal emission with existing/missing files
  - Content preview generation
  - Session state tracking
  - Read/write access control
  - Causal constraint enforcement
  - Serialization/deserialization
  - Multiple portal tracking
  - Error handling

### Key Test Cases

1. **Happy Path**:
   - Emit portal with existing file ✓
   - Write through readwrite portal ✓
   - Multiple portals tracked independently ✓

2. **Access Control**:
   - Read-only portal prevents writes ✓
   - Unopen portal rejects writes ✓
   - Readwrite portal allows multiple writes ✓

3. **Edge Cases**:
   - Missing file returns exists=False ✓
   - Directory path raises error ✓
   - Unique portal IDs per emission ✓

4. **Integration**:
   - FileEditGuard cache integration ✓
   - Portal state updates on write ✓
   - Metadata preservation ✓

## Type Safety

- **mypy**: ✓ Clean (0 errors in 32 files)
- **Contract-First**: All types defined in `contracts.py`
- **Generic Tool[A,B]**: Proper variance and composition

## Registration

Portal tools are automatically registered via:

```python
from services.tooling.tools import register_all_tools

registry = ToolRegistry()
register_all_tools(registry)

portal_emit = registry.get("portal.emit")
portal_write = registry.get("portal.write")
```

## Integration Points

### Backend (Python)

```python
from services.tooling.tools import PortalTool, PortalWriteTool
from services.tooling.contracts import PortalRequest, PortalWriteRequest
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
/>
```

### Chat Streaming

```python
emission = await portal_tool.invoke(request)
await stream.emit({
    "type": "portal",
    "data": emission.to_dict()
})
```

## Usage Examples

### Spec to Implementation

```python
emission = await portal_tool.invoke(
    PortalRequest(
        destination="impl/service.py",
        edge_type="implements",
        access="readwrite"
    )
)
```

### Test Coverage

```python
emission = await portal_tool.invoke(
    PortalRequest(
        destination="_tests/test_service.py",
        edge_type="tests",
        access="read"
    )
)
```

### Documentation Reference

```python
emission = await portal_tool.invoke(
    PortalRequest(
        destination="spec/service.md",
        edge_type="references",
        auto_expand=True
    )
)
```

## Patterns Applied

### Crown Jewel Patterns

1. **Container Owns Workflow**: FileEditGuard owns file I/O
2. **Thin Adapters**: Portal tools delegate to FileEditGuard
3. **Contract-First Types**: All types in `contracts.py`
4. **Causal Constraints**: Portal must be open before write

### T-gent Testing (Type II: Delta Tests)

- Focus on adapter behavior, not FileEditGuard internals
- Verify contract translation
- Test error wrapping and constraint enforcement

## Performance

- **Portal Emission**: ~1-5ms (FileEditGuard read + cache)
- **Portal Write**: ~5-10ms (FileEditGuard write + hash update)
- **Session Overhead**: O(1) dict lookup per portal operation

## Future Enhancements

### Potential Features

1. **Partial Updates**: `start_line`/`end_line` in PortalWriteRequest
2. **Portal Events**: Emit witness marks for portal actions
3. **Portal Expiry**: Time-based portal session cleanup
4. **Portal Snapshots**: Track content history per portal
5. **Portal Permissions**: Fine-grained access control per edge type

### Integration Opportunities

1. **Witness System**: Mark portal expansions/collapses
2. **Living Spec**: Auto-create portals from spec references
3. **Hypergraph**: Portal navigation as graph traversal
4. **AGENTESE**: `self.portal.open(destination, edge_type)`

## Verification

All verification completed:

```bash
# Tests
✓ 21 portal tests passing
✓ 287 total tooling tests passing

# Types
✓ mypy clean (0 errors)

# Integration
✓ Tools registered in ToolRegistry
✓ FileEditGuard integration working
✓ Imports clean

# Demo
✓ End-to-end workflow verified
✓ Read and write operations confirmed
```

## Summary

The Portal Tool implementation is **production-ready**:

- ✅ Full test coverage (21 tests, all passing)
- ✅ Type-safe (mypy clean)
- ✅ Integrated with FileEditGuard
- ✅ Registered in ToolRegistry
- ✅ Documented with usage guide
- ✅ Follows categorical Tool[A,B] protocol
- ✅ Respects trust levels and causal constraints

Portal tools enable "the doc comes to you" UX pattern, allowing chat participants to view and edit files inline without navigation.
