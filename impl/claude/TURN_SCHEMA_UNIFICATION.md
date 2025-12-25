# Turn Schema Unification

**Status**: ✅ Complete
**Date**: 2025-12-24

## Problem

There were TWO incompatible `Turn` definitions in the codebase:

1. **API Turn** (`protocols/api/chat.py` lines 129-150):
   - Rich Pydantic model with `Message` objects
   - Contains `role`, `content`, `mentions`, `linearity_tag`
   - Used for API serialization and frontend communication
   - Includes `ToolUse` objects with full metadata

2. **Service Turn** (`services/chat/context.py` lines 70-256):
   - Simple dataclass with string fields
   - Direct `user_message: str` and `assistant_response: str`
   - Used internally by `ChatSession`, `WorkingContext`, `ChatPersistence`
   - Tracks tool names as `list[str]`, not objects

## Resolution Strategy

**Keep both models** but add conversion functions at the API boundary.

### Rationale

- **Service Turn** is simpler and better for internal operations (persistence, compression, K-Block operations)
- **API Turn** is richer and better for client communication (frontend needs structured messages)
- Clear separation of concerns: service layer owns domain logic, API layer owns serialization
- Follows metaphysical fullstack pattern: layers have distinct representations

## Implementation

### 1. Conversion Functions

Added two methods to `services/chat/context.Turn`:

```python
def to_api_turn(self) -> ApiTurn:
    """Convert service Turn to API Turn for serialization."""
    # Creates Message objects from strings
    # Converts tool names to ToolUse objects
    # Builds EvidenceDelta from metadata
    ...

@classmethod
def from_api_turn(cls, api_turn: ApiTurn) -> Turn:
    """Convert API Turn to service Turn for internal operations."""
    # Extracts content from Message objects
    # Extracts tool names from ToolUse objects
    # Preserves linearity tags and confidence
    ...
```

### 2. Documentation

- Added docstrings to both Turn classes explaining their roles
- Updated module docstrings to explain the relationship
- Created comprehensive test suite (`test_turn_conversion.py`)

### 3. Type Hints

- Used `TYPE_CHECKING` import guard to avoid circular imports
- Service layer imports API types only for type hints
- API layer is independent

## Usage

### Service → API (for HTTP responses)

```python
from services.chat.context import Turn as ServiceTurn

service_turn = ServiceTurn(
    user_message="Hello",
    assistant_response="Hi there!",
    tools_used=["Read", "Write"],
)

# Convert for API response
api_turn = service_turn.to_api_turn()
# Returns Turn with Message objects, ToolUse objects
```

### API → Service (for persistence)

```python
from protocols.api.chat import Turn as ApiTurn, Message

api_turn = ApiTurn(
    turn_number=1,
    user_message=Message(role="user", content="Hello"),
    assistant_response=Message(role="assistant", content="Hi!"),
    ...
)

# Convert for service layer
from services.chat.context import Turn as ServiceTurn
service_turn = ServiceTurn.from_api_turn(api_turn)
# Returns Turn with string fields
```

## Frontend Compatibility

The frontend `Turn` interface (`web/src/components/chat/store.ts` lines 32-41) matches the **API Turn** model:

```typescript
export interface Turn {
  turn_number: number;
  user_message: Message;      // Matches API Turn
  assistant_response: Message; // Matches API Turn
  tools_used: ToolUse[];
  evidence_delta: EvidenceDelta;
  confidence: number;
  started_at: string;
  completed_at: string;
}
```

No frontend changes needed.

## Testing

Created comprehensive test suite in `services/chat/_tests/test_turn_conversion.py`:

- ✅ Service → API conversion
- ✅ API → Service conversion
- ✅ Round-trip conversion preserves data
- ✅ Linearity tag conversion
- ✅ Empty tools handling
- ✅ Missing `completed_at` handling

All tests pass:

```
$ uv run pytest services/chat/_tests/test_turn_conversion.py -v
======================== 6 passed in 3.89s =========================
```

## Benefits

1. **Clear separation**: Service owns domain logic, API owns serialization
2. **Type safety**: Both models are fully typed with proper hints
3. **Testable**: Conversion functions are pure and testable
4. **Maintainable**: Changes to one layer don't affect the other
5. **Performance**: No unnecessary conversions in hot paths

## Migration Notes

- **Existing API routes**: Already use API Turn, no changes needed
- **Service layer**: Uses service Turn internally, no changes needed
- **Persistence**: ChatPersistence uses service Turn, no changes needed
- **Frontend**: Uses API Turn shape, no changes needed

The conversion happens transparently at the API boundary.

## Future Work

- [ ] Add `mentions` support to service Turn (currently empty list in API conversion)
- [ ] Track full `ToolUse` metadata in service layer (currently just names)
- [ ] Add evidence delta tracking to service Turn (currently computed on conversion)

## References

- API Turn: `/impl/claude/protocols/api/chat.py` lines 129-150
- Service Turn: `/impl/claude/services/chat/context.py` lines 70-256
- Frontend Turn: `/impl/claude/web/src/components/chat/store.ts` lines 32-41
- Tests: `/impl/claude/services/chat/_tests/test_turn_conversion.py`
- Spec: `spec/protocols/chat-web.md`
