# Portal Tool API Integration

**Status**: Complete
**Date**: 2025-12-25

## Overview

The Portal Tool has been integrated into the chat REST API, providing endpoints for emitting portals and writing through them during chat sessions.

## Endpoints

### POST /api/chat/portal/emit

Emit a portal to a file/resource for inline access in chat.

**Request**:
```json
{
  "destination": "/path/to/file.txt",
  "edge_type": "context",
  "access": "read",
  "auto_expand": true
}
```

**Response** (`PortalEmissionAPI`):
```json
{
  "portal_id": "uuid",
  "destination": "/path/to/file.txt",
  "edge_type": "context",
  "access": "read",
  "content_preview": "first 10 lines...",
  "content_full": "full file content",
  "line_count": 42,
  "exists": true,
  "auto_expand": true,
  "emitted_at": "2025-12-25T10:30:00Z"
}
```

**Status Codes**:
- `200 OK`: Portal emitted successfully
- `422 Unprocessable Entity`: Invalid request parameters
- `500 Internal Server Error`: Portal emission failed

### POST /api/chat/portal/write

Write content through an open portal.

**Request**:
```json
{
  "portal_id": "uuid-from-emit",
  "content": "new file content"
}
```

**Response**:
```json
{
  "success": true,
  "portal_id": "uuid",
  "bytes_written": 16,
  "new_content_hash": "sha256...",
  "error_message": ""
}
```

**Status Codes**:
- `200 OK`: Write successful
- `422 Unprocessable Entity`: Invalid request parameters
- `500 Internal Server Error`: Write failed (portal not open, read-only, etc.)

## Turn Integration

The `Turn` model has been updated to include `portal_emissions`:

```python
class Turn(BaseModel):
    turn_number: int
    user_message: Message
    assistant_response: Message
    tools_used: list[ToolUse] = []
    portal_emissions: list[PortalEmissionAPI] = []  # NEW
    evidence_delta: EvidenceDelta
    confidence: float
    started_at: str
    completed_at: str
```

When K-gent uses the portal tool during a chat turn, the emissions are collected and included in the turn response.

## Implementation Details

### Type Safety

The API layer uses `Literal["read", "readwrite"]` for type safety, while the tool layer uses `str`. The emit endpoint handles the casting:

```python
access_typed: Literal["read", "readwrite"] = (
    "readwrite" if result.access == "readwrite" else "read"
)
```

### Error Handling

- **Missing destination**: Returns 422 validation error
- **Nonexistent file**: Returns 200 with `exists=false` and empty content
- **Portal not found**: Returns 500 with "Portal not open" message
- **Read-only portal**: Returns 500 with "Portal is read-only" message
- **Permission denied**: Returns 500 with "Permission denied" message

### Portal Session State

Portals are tracked in-memory using the `_OPEN_PORTALS` registry in `services/tooling/tools/portal.py`. Each portal stores:
- `portal_id`: Unique identifier
- `destination`: File path
- `edge_type`: Edge type (context, edits, etc.)
- `access`: Access level (read/readwrite)
- `content_hash`: SHA-256 of content at open time
- `opened_at`: Timestamp
- `last_accessed`: Last access timestamp

## Testing

Comprehensive tests are provided in `protocols/api/_tests/test_portal_api.py`:

- **TestPortalEmitEndpoint**: Portal emission tests
  - Existing files
  - Nonexistent files
  - Access levels (read/readwrite)
  - Default values

- **TestPortalWriteEndpoint**: Portal write tests
  - Successful writes
  - Read-only portal failures
  - Portal not open failures

- **TestPortalInTurns**: Turn integration tests
  - Portal emissions in turn responses

- **TestPortalErrorHandling**: Error cases
  - Missing parameters
  - Invalid access levels

- **TestPortalContentPreview**: Preview behavior
  - Short files
  - Long files

- **TestPortalWorkflow**: End-to-end workflows
  - Emit → Read → Write cycle
  - Multiple portals to same file

## Usage Examples

### Emit a read-only portal
```bash
curl -X POST http://localhost:8000/api/chat/portal/emit \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "/path/to/file.txt",
    "access": "read"
  }'
```

### Emit a readwrite portal
```bash
curl -X POST http://localhost:8000/api/chat/portal/emit \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "/path/to/file.txt",
    "access": "readwrite",
    "edge_type": "edits"
  }'
```

### Write through a portal
```bash
curl -X POST http://localhost:8000/api/chat/portal/write \
  -H "Content-Type: application/json" \
  -d '{
    "portal_id": "uuid-from-emit",
    "content": "Updated file content\n"
  }'
```

## Integration with K-gent Bridge

The K-gent bridge can emit portals during chat sessions by using the PortalTool. Portal emissions are automatically collected and included in the turn response's `portal_emissions` field.

Example SSE stream with portal:
```
data: {"type": "content", "content": "Opening portal..."}

data: {"type": "done", "turn": {..., "portal_emissions": [...]}}
```

## Future Enhancements

1. **Portal lifecycle management**: Auto-close portals after session ends
2. **Portal permissions**: Integrate with trust levels
3. **Portal notifications**: SSE events when portal content changes
4. **Portal history**: Track all writes through a portal
5. **Multi-user portals**: Sync portal state across sessions

## Related Files

- `services/tooling/tools/portal.py` - PortalTool and PortalWriteTool
- `services/tooling/contracts.py` - PortalRequest, PortalEmission, etc.
- `protocols/api/chat.py` - Chat REST API with portal endpoints
- `protocols/api/_tests/test_portal_api.py` - API tests
- `spec/protocols/portal-token.md` - Portal specification

## Checklist

- [x] Add PortalEmissionAPI model to chat.py
- [x] Add portal_emissions field to Turn model
- [x] Add PortalEmitRequest and PortalWriteRequest models
- [x] Implement POST /api/chat/portal/emit endpoint
- [x] Implement POST /api/chat/portal/write endpoint
- [x] Handle type casting for Literal types
- [x] Add error handling for all failure cases
- [x] Create comprehensive test suite
- [x] Verify imports work correctly
- [x] Pass mypy type checking
- [x] Document integration
