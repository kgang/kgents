# U-gent Tooling Phase 1: Core Tools ✅ COMPLETE

> *"Reuse > rewrite. The simplest composition wins."*

## Status: COMPLETE (2025-12-20)

**Verification**: All 102 tooling tests pass, mypy clean.

```bash
uv run pytest services/tooling/ -v  # 102 passed
uv run mypy services/tooling/tools/ # Success: no issues found
```

---

## Reality Check

**Discovery**: Core file tools already exist in `services/conductor/`:
- `FileEditGuard` — read-before-edit enforcement ✓
- `world.file.*` AGENTESE node — exposed via @node ✓
- `services/conductor/contracts.py` — type-safe contracts ✓

**Phase 1's actual job**: Bridge these to `Tool[A,B]` for categorical composition.

---

## What Exists (DO NOT REWRITE)

| Component | Location | Status |
|-----------|----------|--------|
| FileEditGuard | `services/conductor/file_guard.py` | Complete |
| world.file node | `protocols/agentese/contexts/world_file.py` | Complete |
| File contracts | `services/conductor/contracts.py` | Complete |
| Tooling contracts | `services/tooling/contracts.py` | Complete |
| Tool[A,B] base | `services/tooling/base.py` | Complete |
| ToolExecutor | `services/tooling/executor.py` | Complete |

---

## Phase 1 Deliverables

```
services/tooling/tools/
    __init__.py
    file.py       # Thin Tool[A,B] wrappers around FileEditGuard
    search.py     # GlobTool, GrepTool (delegate to world.file)
```

### Pattern: Tool as Adapter

Tools wrap existing functionality, adding categorical composition:

```python
# services/tooling/tools/file.py

from services.conductor.file_guard import FileEditGuard, get_file_guard
from services.tooling.base import Tool, ToolCategory, ToolEffect
from services.tooling.contracts import ReadRequest, FileContent

class ReadTool(Tool[ReadRequest, FileContent]):
    """
    ReadTool: Adapter from FileEditGuard to Tool[A,B].

    Enables categorical composition:
        pipeline = read >> grep >> summarize
    """

    def __init__(self, guard: FileEditGuard | None = None):
        self._guard = guard or get_file_guard()

    @property
    def name(self) -> str:
        return "file.read"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CORE

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [ToolEffect.reads("filesystem")]

    @property
    def trust_required(self) -> int:
        return 0  # L0 - Read-only

    @property
    def cacheable(self) -> bool:
        return True  # Content cached by FileEditGuard

    async def invoke(self, request: ReadRequest) -> FileContent:
        from services.conductor.contracts import FileReadRequest

        # Adapt contracts
        guard_request = FileReadRequest(
            path=request.file_path,
            start_line=request.offset,
            end_line=(request.offset + request.limit) if request.offset and request.limit else None,
        )

        response = await self._guard.read_file(guard_request)

        return FileContent(
            path=response.path,
            content=response.content,
            line_count=response.lines,
            truncated=response.truncated,
            offset=request.offset or 0,
        )
```

### WriteTool with Causal Constraint

```python
class WriteTool(Tool[WriteRequest, WriteResponse]):
    """
    WriteTool: Adapter with causal constraint.

    The ReadProof requirement is enforced by FileEditGuard's cache.
    Files must be read before write to populate the cache.
    """

    @property
    def name(self) -> str:
        return "file.write"

    @property
    def trust_required(self) -> int:
        return 2  # L2 - Requires confirmation

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [ToolEffect.writes("filesystem")]

    async def invoke(self, request: WriteRequest) -> WriteResponse:
        from services.conductor.contracts import FileWriteRequest

        guard_request = FileWriteRequest(
            path=request.file_path,
            content=request.content,
        )

        response = await self._guard.write_file(guard_request)

        return WriteResponse(
            path=response.path,
            success=response.success,
            bytes_written=response.size,
            created=not Path(request.file_path).exists(),  # Before write
        )
```

### EditTool

```python
class EditTool(Tool[EditRequest, EditResponse]):
    """
    EditTool: Exact string replacement via FileEditGuard.

    Enforces:
    - File must be read first (NotReadError)
    - old_string must exist (StringNotFoundError)
    - old_string must be unique (StringNotUniqueError) unless replace_all
    - File unchanged since read (FileChangedError)
    """

    @property
    def name(self) -> str:
        return "file.edit"

    @property
    def trust_required(self) -> int:
        return 2  # L2 - Requires confirmation

    async def invoke(self, request: EditRequest) -> EditResponse:
        from services.conductor.contracts import FileEditRequest

        guard_request = FileEditRequest(
            path=request.file_path,
            old_string=request.old_string,
            new_string=request.new_string,
            replace_all=request.replace_all,
        )

        response = await self._guard.edit_file(guard_request)

        return EditResponse(
            path=response.path,
            success=response.success,
            replacements=response.replacements,
        )
```

---

## Contract Alignment

The two contract sets need mapping:

| Tooling Contract | Conductor Contract | Notes |
|------------------|-------------------|-------|
| `ReadRequest` | `FileReadRequest` | Add offset → start_line |
| `FileContent` | `FileReadResponse` | Similar structure |
| `WriteRequest` | `FileWriteRequest` | Direct map |
| `WriteResponse` | `FileWriteResponse` | Direct map |
| `EditRequest` | `FileEditRequest` | Direct map |
| `EditResponse` | `FileEditResponse` | Direct map |
| `GlobQuery` | `FileGlobRequest` | Direct map |
| `GrepQuery` | `FileGrepRequest` | Direct map |

**Decision**: Keep both contract sets. Tooling contracts are the public API. Conductor contracts are internal. Tools adapt between them.

---

## Registry Integration

```python
# services/tooling/tools/__init__.py

from .file import ReadTool, WriteTool, EditTool
from .search import GlobTool, GrepTool

# Auto-register core tools
def register_core_tools(registry: ToolRegistry) -> None:
    """Register all core tools with the registry."""
    registry.register(ReadTool())
    registry.register(WriteTool())
    registry.register(EditTool())
    registry.register(GlobTool())
    registry.register(GrepTool())
```

```python
# services/providers.py - add to get_tool_registry()

async def get_tool_registry() -> ToolRegistry:
    from services.tooling import ToolRegistry
    from services.tooling.tools import register_core_tools

    registry = ToolRegistry()
    register_core_tools(registry)
    return registry
```

---

## Composition Example

With Phase 1 complete, tools compose categorically:

```python
# Read → Grep → Process pipeline
from services.tooling.tools import ReadTool, GrepTool

read = ReadTool()
grep = GrepTool()

# Compose via >>
pipeline = read >> grep

# Execute through ToolExecutor
result = await executor.execute(
    pipeline,
    request=ReadRequest(file_path="src/main.py"),
    observer=observer,
)
```

---

## Tests

```
services/tooling/tools/_tests/
    test_file.py      # ReadTool, WriteTool, EditTool
    test_search.py    # GlobTool, GrepTool
    test_composition.py  # Pipeline composition
```

### Test Pattern

```python
# services/tooling/tools/_tests/test_file.py

class TestReadTool:
    async def test_delegates_to_guard(self, tmp_path):
        """ReadTool delegates to FileEditGuard."""
        file = tmp_path / "test.txt"
        file.write_text("hello world")

        tool = ReadTool()
        result = await tool.invoke(ReadRequest(file_path=str(file)))

        assert result.content == "hello world"
        assert result.line_count == 1

    async def test_composes_with_grep(self, tmp_path):
        """ReadTool >> GrepTool composition works."""
        file = tmp_path / "test.py"
        file.write_text("def foo():\n    pass\ndef bar():\n    pass")

        pipeline = ReadTool() >> GrepTool()
        # ... test pipeline execution
```

---

## Success Criteria

- [x] `from services.tooling.tools import ReadTool, WriteTool, EditTool, GlobTool, GrepTool`
- [x] All tools delegate to `FileEditGuard` (no reimplementation)
- [x] `read >> grep` pipeline composes correctly
- [x] Trust gate respects tool.trust_required
- [x] Category laws verified (Identity, Associativity)
- [x] `uv run pytest services/tooling/tools/_tests/ -v` passes (44 tests)

---

## Verification

```bash
cd impl/claude
uv run pytest services/tooling/ -v       # All tooling tests
uv run pytest services/conductor/ -v     # Guard still works
uv run mypy services/tooling/            # Type check
```

---

## What NOT To Do

- **Don't reimplement FileEditGuard** — it's battle-tested
- **Don't merge contract sets** — separation enables evolution
- **Don't add features** — adapter pattern only
- **Don't change world.file node** — it works independently

*"Depth over breadth. The adapter is the entire contribution."*

---

## Phase 2 Handoff

With Phase 1 complete, the path forward:

1. **System Tools** (Phase 2): BashTool, KillShellTool
2. **Web Tools** (Phase 3): WebFetchTool, WebSearchTool
3. **Orchestration Tools** (Phase 4): TodoTool, ModeTool

The adapter pattern established here applies to all future tools:
- Wrap existing infrastructure (don't reimplement)
- Convert response failures to exceptions for categorical interface
- Trust levels declared via `trust_required` property
- Effects declared for capability checking

**Key Learning**: FileEditGuard catches errors and returns failure responses.
EditTool converts these to exceptions for clean Tool[A,B] semantics.
