# SyncFlow Quick Reference

## Import

```python
from services.sync import SyncFlow, UploadResult, SyncResult, BootstrapResult
from agents.d.universe import get_universe
from services.code.boundary import BoundaryDetector
```

## Initialization

```python
# Get Universe (singleton)
universe = get_universe()
await universe._ensure_initialized()

# Optional: Create boundary detector for K-block suggestions
boundary_detector = BoundaryDetector(
    min_tokens=500,
    max_tokens=5000,
    target_tokens=2000,
)

# Initialize SyncFlow
flow = SyncFlow(universe, boundary_detector)
```

## Upload Single File

```python
result: UploadResult = await flow.upload_file(
    file_path="services/witness/store.py",
    spec_id=None,  # Optional: link to spec
    auto_extract_functions=True,
)

# Check results
print(f"Functions: {len(result.functions_created)}")
print(f"Ghosts: {len(result.ghosts_created)}")
print(f"K-block: {result.kblock_id}")
print(f"Errors: {result.errors}")
```

## Sync Directory

```python
result: SyncResult = await flow.sync_directory(
    directory="services/witness",
    pattern="**/*.py",  # Default: all Python files
    incremental=True,   # Default: skip unchanged files
)

# Check results
print(f"Files processed: {result.files_processed}")
print(f"Functions created: {result.functions_created}")
print(f"Functions updated: {result.functions_updated}")
print(f"Ghosts created: {result.ghosts_created}")
print(f"K-blocks suggested: {result.kblocks_suggested}")
```

## Bootstrap Spec+Impl Pair (QA)

```python
# Minimal spec (markdown)
spec = """
# Add Function

Adds two numbers and returns the result.

## Signature
add(x: int, y: int) -> int

## Examples
- add(2, 3) → 5
- add(-1, 1) → 0
"""

# Minimal implementation (Python)
impl = """
def add(x: int, y: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return x + y
"""

# Bootstrap the pair
result: BootstrapResult = await flow.bootstrap_spec_impl_pair(
    spec_content=spec,
    impl_content=impl,
    name="add_example",
)

# Check results
print(f"Spec ID: {result.spec_id}")
print(f"Impl functions: {result.impl_functions}")
print(f"K-block: {result.kblock_id}")
print(f"Derivation edges: {result.derivation_edges}")
```

## Result Types

### UploadResult
```python
@dataclass
class UploadResult:
    file_path: str
    functions_created: list[str]  # FunctionCrystal IDs
    ghosts_created: list[str]     # GhostFunctionCrystal IDs
    kblock_id: str | None         # Suggested K-block
    errors: list[str]
```

### SyncResult
```python
@dataclass
class SyncResult:
    files_processed: int
    functions_created: int
    functions_updated: int
    functions_unchanged: int
    ghosts_created: int
    kblocks_suggested: int
    errors: list[str]
```

### BootstrapResult
```python
@dataclass
class BootstrapResult:
    spec_id: str
    impl_functions: list[str]
    kblock_id: str
    derivation_edges: list[str]  # Edge IDs linking spec → impl
```

## Common Patterns

### Upload and Inspect

```python
result = await flow.upload_file("my_module.py")

# Inspect functions
for func_id in result.functions_created:
    func = await universe.get(func_id)
    print(f"{func.qualified_name}: {func.signature}")

# Inspect ghosts
for ghost_id in result.ghosts_created:
    ghost = await universe.get(ghost_id)
    print(f"Undefined: {ghost.name} (called from {ghost.called_from})")
```

### Incremental Sync

```python
# First sync: creates all functions
result1 = await flow.sync_directory("services/witness")
print(f"Created {result1.functions_created} functions")

# Modify a file...

# Second sync: only updates changed functions
result2 = await flow.sync_directory("services/witness", incremental=True)
print(f"Updated {result2.functions_updated} functions")
print(f"Unchanged {result2.functions_unchanged} functions")
```

### QA Workflow

```python
# 1. Bootstrap minimal pair
result = await flow.bootstrap_spec_impl_pair(spec, impl, "example")

# 2. Verify spec exists
spec = await universe.get(result.spec_id)
assert spec.content == spec_content

# 3. Verify functions exist
for func_id in result.impl_functions:
    func = await universe.get(func_id)
    assert func.spec_id == result.spec_id  # Linked to spec

# 4. Verify derivation edges
for edge_id in result.derivation_edges:
    edge = await universe.get(edge_id)
    assert edge.parent_layer < edge.child_layer  # L4 → L5
```

## Troubleshooting

### No functions found
```python
result = await flow.upload_file("my_file.py")
if not result.functions_created:
    print("Errors:", result.errors)
    # Common causes:
    # - File is not valid Python
    # - File contains only classes/imports, no top-level functions
    # - Parse error in AST
```

### Ghosts are not errors
```python
result = await flow.upload_file("my_file.py")
if result.ghosts_created:
    print(f"Found {len(result.ghosts_created)} undefined calls")
    # This is NORMAL during incremental development
    # Upload the missing files to resolve ghosts
```

### K-block suggestions
```python
result = await flow.upload_file("my_file.py")
if result.kblock_id:
    kblock = await universe.get(result.kblock_id)
    print(f"Suggested K-block: {kblock.name}")
    print(f"Boundary type: {kblock.boundary_type}")
    print(f"Confidence: {kblock.boundary_confidence}")
    # User can accept, reject, or modify
```

## Philosophy

- **User Control**: Every operation is explicit, user-triggered
- **Transparency**: Full visibility into what was created
- **Suggestion, Not Enforcement**: K-blocks and ghosts are suggestions

## See Also

- `IMPLEMENTATION_SUMMARY.md` - Full implementation details
- `services/code/service.py` - CodeService implementation
- `services/code/parser.py` - AST parser
- `services/code/boundary.py` - BoundaryDetector
- `agents/d/schemas/code.py` - FunctionCrystal schema
