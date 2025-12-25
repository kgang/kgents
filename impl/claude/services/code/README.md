# Code Service

Explicit user-driven sync flows for code artifacts.

## Philosophy

**This is NOT magic auto-sync. Users explicitly trigger sync operations.**

The Code Service implements Kent's vision:
> "We should create explicit flows for the user to upload or sync their data. I'll be inserting trivial toy specs and implementations to bootstrap and QA the entire user journey."

## Architecture

```
CodeService (Business Logic)
    ↓
SimplePythonParser (AST extraction)
    ↓
Universe (D-gent storage)
```

## Three Core Flows

### 1. Upload File

Upload a single Python file and extract functions:

```python
from services.code import CodeService

service = CodeService()

result = await service.upload_file(
    file_path="src/math_utils.py",
    spec_id="spec_math",  # Optional link to spec
    auto_extract_functions=True,
    create_kblock=True,
)

print(f"Created {len(result.functions_created)} functions")
print(f"Detected {len(result.ghosts_created)} ghosts")
print(f"K-Block: {result.kblock_id}")
```

**What happens:**
1. Parse file with AST parser
2. Create FunctionCrystal for each function
3. Detect ghost placeholders (undefined calls)
4. Create K-block for file boundary
5. Store everything in Universe

### 2. Sync Directory

Sync an entire directory tree:

```python
result = await service.sync_directory(
    directory="src/",
    pattern="**/*.py",
    incremental=True,  # Skip unchanged files
)

print(f"Processed {result.files_processed} files")
print(f"Created {result.functions_created} functions")
print(f"Updated {result.functions_updated} functions")
print(f"Created {result.kblocks_created} K-blocks")
```

**What happens:**
1. Find all matching files (`**/*.py`)
2. For incremental: compare body_hash to detect changes
3. Create/update FunctionCrystals
4. Detect new ghost placeholders
5. Recompute K-block boundaries

### 3. Bootstrap Spec+Impl Pair

Bootstrap a spec+impl pair for QA (Kent's workflow):

```python
spec_content = """
# Math Operations

## add
Adds two numbers.

## multiply
Multiplies two numbers.
"""

impl_content = """
def add(a, b):
    return a + b

def multiply(x, y):
    return x * y
"""

result = await service.bootstrap_spec_impl_pair(
    spec_content=spec_content,
    impl_content=impl_content,
    name="math_ops",
)

print(f"Spec: {result.spec_id}")
print(f"Functions: {result.impl_functions}")
print(f"K-Block: {result.kblock_id}")
print(f"Derivation edges: {result.derivation_edges}")
```

**What happens:**
1. Create SpecCrystal from spec_content
2. Parse impl_content, create FunctionCrystals
3. Link functions to spec (derivation edges)
4. Create K-block for the impl
5. Create proofs for each crystal

## Ghost Detection

Ghosts are functions that are **called but not defined** in the current set.

Example:
```python
def foo():
    bar()  # bar() is a ghost (not defined)

def baz():
    qux()  # qux() is a ghost
```

The service automatically detects ghosts and creates placeholders.

## K-Block Boundaries

K-blocks group related functions. Default boundary is **file-level**:

```
file.py
  ├─ function_a
  ├─ function_b
  └─ function_c

→ Creates one K-block containing all three functions
```

## Data Flow

```
Python File
    ↓
SimplePythonParser (AST)
    ↓
FunctionInfo (name, body, calls, hash)
    ↓
FunctionCrystal (stored in Universe)
    ↓
K-Block (file-level grouping)
```

## Testing

Run tests:
```bash
uv run pytest services/code/_tests/test_service.py -v
```

All 16 tests pass:
- Parser extraction (functions, calls, docstrings)
- Upload flow (functions, ghosts, K-blocks)
- Sync flow (directory tree, incremental)
- Bootstrap flow (spec+impl pair)
- Ghost detection (undefined calls)
- Integration tests (full flows)

## Future Work

This is a **minimal bootstrap implementation**. Future enhancements:

1. **Full schemas** - Create proper D-gent schemas:
   - `FunctionCrystal` (replaces dict storage)
   - `GhostFunctionCrystal` (ghost placeholders)
   - `KBlockCrystal` (code boundaries)

2. **Advanced parser** - Extract more metadata:
   - Type hints
   - Decorators
   - Class context
   - Import graph

3. **Boundary detector** - Smart K-block boundaries:
   - Semantic clustering
   - Dependency analysis
   - User-defined boundaries

4. **Witness integration** - Emit marks for traceability:
   - Sync operations
   - Ghost detection
   - K-block creation

5. **AGENTESE exposure** - Expose via `world.code.*`:
   - `world.code.upload`
   - `world.code.sync`
   - `world.code.function.list`
   - `world.code.ghost.list`

## Example Session

```python
from services.code import CodeService

service = CodeService()

# Upload single file
result = await service.upload_file("utils.py")
# → 3 functions, 1 ghost, 1 K-block

# Sync entire directory
result = await service.sync_directory("src/")
# → 15 files, 42 functions, 5 ghosts, 15 K-blocks

# Bootstrap for QA
result = await service.bootstrap_spec_impl_pair(
    spec_content=open("spec/math.md").read(),
    impl_content=open("impl/math.py").read(),
    name="math",
)
# → Full derivation chain: spec → functions → K-block
```

## Success Criteria

- [x] upload_file creates FunctionCrystals
- [x] sync_directory handles incremental updates
- [x] bootstrap_spec_impl_pair creates full derivation chain
- [x] Ghost detection finds undefined calls
- [x] K-blocks created with correct boundaries
- [ ] Witness marks emitted (future)
- [x] Tests pass (16/16)
