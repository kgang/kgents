# Code Crown Jewel - AGENTESE Node Implementation

## Summary

Successfully implemented AGENTESE nodes for the `world.code.*` namespace, exposing function-level code artifact tracking through the universal protocol.

## Files Created/Modified

### Created Files

1. **`services/code/node.py`** (18KB)
   - `CodeNode` class with `@node("world.code")` decorator
   - 12 aspect paths registered
   - Full request/response contracts defined
   - Integration with `CodeService`

### Modified Files

1. **`services/providers.py`**
   - Added `get_code_service()` provider function
   - Registered `code_service` in container
   - Added `CodeNode` import in `setup_providers()`
   - Added to `__all__` exports

2. **`protocols/agentese/gateway.py`**
   - Added `services.code` to `_import_node_modules()`
   - Ensures node registration at gateway mount

## AGENTESE Paths Registered

All paths under `world.code.*`:

### Manifest & Sync
- `world.code.manifest` - Code layer status
- `world.code.upload` - Upload single file
- `world.code.sync` - Sync directory
- `world.code.bootstrap` - Bootstrap spec+impl pair

### Function Operations
- `world.code.function.list` - List functions
- `world.code.function.get` - Get function by ID
- `world.code.function.graph` - Get call graph

### K-Block Operations
- `world.code.kblock.list` - List K-blocks
- `world.code.kblock.get` - Get K-block with contents
- `world.code.kblock.suggest` - Suggest boundary changes

### Ghost Operations
- `world.code.ghost.list` - List ghost placeholders
- `world.code.ghost.resolve` - Mark ghost as resolved

## Request/Response Contracts

All aspects have strongly-typed contracts defined:

```python
@node(
    "world.code",
    description="Code artifact tracking - function-level crystals",
    dependencies=("universe", "code_service"),
    contracts={
        "manifest": Response(CodeManifestResponse),
        "upload": Contract(UploadRequest, UploadResponse),
        "sync": Contract(SyncRequest, SyncResponse),
        # ... 9 more contracts
    },
)
```

## Dependency Injection

The node declares two required dependencies:

1. **`universe`** - D-gent Universe for storage
2. **`code_service`** - CodeService business logic

Both are resolved by the ServiceContainer at instantiation:

```python
def __init__(self, universe: Universe, code_service: CodeService) -> None:
    self._universe = universe
    self._code_service = code_service
```

## Observer Gradation

Affordances vary by archetype:

- **Developer/Operator**: Full access to all 12 aspects
- **Architect/Researcher**: Read-only (6 aspects: list, get, graph operations)
- **Guest**: Manifest only

## Integration Points

### Service Layer
- `CodeService` in `services/code/service.py`
- AST-based Python parsing
- Function extraction, ghost detection
- K-Block boundary management

### Provider Registration
- `get_code_service()` creates service with Universe injection
- Registered as singleton in container
- Auto-wired to `CodeNode` via `@node(dependencies=("code_service",))`

### Gateway Auto-Discovery
- Module imported in `_import_node_modules()`
- `@node` decorator triggers registration at import time
- All 12 paths auto-exposed via `/agentese/world/code/*`

## Examples

### Via HTTP (FastAPI)
```bash
# Manifest
GET /agentese/world/code/manifest

# Upload file
POST /agentese/world/code/upload
{
  "file_path": "impl/claude/agents/d/node.py",
  "spec_id": "spec_dgent_node",
  "auto_extract": true
}

# List functions
POST /agentese/world/code/function/list
{
  "prefix": "agents.d",
  "limit": 50
}
```

### Via Logos (Programmatic)
```python
from protocols.agentese import create_logos
from protocols.agentese.node import Observer

logos = create_logos()
observer = Observer.from_archetype("developer")

# Upload file
result = await logos.invoke(
    "world.code.upload",
    observer,
    file_path="impl/claude/agents/d/node.py",
)

# List functions
functions = await logos.invoke(
    "world.code.function.list",
    observer,
    prefix="agents.d",
    limit=10,
)
```

### Via CLI (When wired)
```bash
# Manifest
kg code manifest

# Upload file
kg code upload impl/claude/agents/d/node.py

# Sync directory
kg code sync impl/claude/agents --pattern "**/*.py"
```

## Teaching Points

From the implementation:

```python
gotcha: CodeNode REQUIRES universe and code_service dependencies.
        Without them, instantiation fails with TypeError—this is intentional!
        It enables Logos fallback when DI isn't configured.

gotcha: Every CodeNode invocation emits a Mark (WARP Law 3). Don't add
        manual tracing—the gateway handles it at _invoke_path().

gotcha: Observer gradation is enforced at _get_affordances_for_archetype().
        Guest observers have minimal affordances—be explicit about archetype
        for non-trivial operations.
```

## Success Criteria

All criteria met:

- ✅ All 12 paths registered and discoverable
- ✅ Request/Response contracts defined for all aspects
- ✅ Node follows pattern from `d/node.py`
- ✅ Gateway imports the module via `_import_node_modules()`
- ✅ Provider registered in `services/providers.py`
- ✅ Container wires `universe` and `code_service` dependencies
- ✅ Observer gradation implemented
- ✅ Aspect metadata with help and examples

## Next Steps (Future Work)

The node is fully wired but some aspects return placeholder data:

1. **Phase 2: Full Implementation**
   - Wire `function.list` to Universe queries
   - Wire `function.get` to retrieve stored functions
   - Implement `function.graph` with AST call analysis

2. **Phase 3: K-Block Integration**
   - Wire `kblock.list` and `kblock.get`
   - Implement `kblock.suggest` with boundary analysis

3. **Phase 4: Ghost Management**
   - Wire `ghost.list` to detect undefined calls
   - Implement `ghost.resolve` to mark as implemented

4. **Phase 5: Frontend Integration**
   - Add Code panel to React UI
   - Function browser with call graph visualization
   - Ghost detection dashboard

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  AGENTESE Gateway (HTTP/WebSocket/CLI)                          │
├─────────────────────────────────────────────────────────────────┤
│  POST /agentese/world/code/upload                               │
│  POST /agentese/world/code/function/list                        │
│  ... (12 paths total)                                           │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  CodeNode (@node("world.code"))                                 │
│  - manifest() → CodeManifestRendering                           │
│  - _invoke_aspect() → routes to CodeService                     │
│  - Observer gradation: developer/architect/guest                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  CodeService (services/code/service.py)                         │
│  - upload_file() → AST parse → extract functions                │
│  - sync_directory() → batch upload                              │
│  - bootstrap_spec_impl_pair() → QA testing                      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Universe (D-gent persistence)                                  │
│  - store() → save function crystals                             │
│  - query() → retrieve functions by prefix                       │
│  - get() → fetch function by ID                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Related Files

- **Spec**: `spec/crown-jewels/code.md` (to be created)
- **Service**: `services/code/service.py` (existing)
- **Parser**: `services/code/parser.py` (existing)
- **Boundary**: `services/code/boundary.py` (existing)
- **Tests**: `services/code/_tests/` (existing)

---

Implementation completed: 2025-12-25
Pattern followed: `agents/d/node.py` (D-gent AGENTESE node)
Contract style: Phase 7 (strongly-typed BE/FE sync)
