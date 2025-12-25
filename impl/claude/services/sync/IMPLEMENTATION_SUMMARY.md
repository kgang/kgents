# SyncFlow Service Implementation Summary

## Overview

The SyncFlow service provides explicit user-driven upload and sync of code artifacts to the Universe. Following Kent's directive: **"Explicit flows, NOT magic. User decides what enters the Universe."**

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  SyncFlow (User-Facing API)                                         │
│  - upload_file()           Upload single file                       │
│  - sync_directory()        Sync directory tree                      │
│  - bootstrap_spec_impl()   Bootstrap spec+impl pair                 │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ delegates to
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  CodeService (Implementation Layer)                                 │
│  - SimplePythonParser      AST parsing                              │
│  - Ghost detection         Find undefined calls                     │
│  - Crystal creation        Store FunctionCrystals                   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ uses
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Dependencies                                                       │
│  - Universe               Persistence                               │
│  - BoundaryDetector       K-block suggestions                       │
│  - DerivationService      Spec→impl linking (future)                │
└─────────────────────────────────────────────────────────────────────┘
```

## Files Created

### `/services/sync/__init__.py` (35 lines)
Module exports:
- `SyncFlow` - Main service class
- `UploadResult` - Single file upload result
- `SyncResult` - Directory sync result
- `BootstrapResult` - Spec+impl bootstrap result

### `/services/sync/flow.py` (489 lines)
Main implementation:
- `SyncFlow` class with three core flows
- `ParsedFunction` helper type
- Comprehensive docstrings with teaching gotchas
- Delegation to existing CodeService

## Three Core Flows

### 1. `upload_file(file_path, spec_id, auto_extract_functions)`

**Purpose**: Upload a single file to the Universe

**Steps**:
1. Parse file into FunctionCrystals using AST parser
2. Create ghost placeholders for undefined references
3. Link to spec if provided (via derivation edges)
4. Suggest K-block boundary using BoundaryDetector

**Returns**: `UploadResult`
- `file_path: str` - Path that was uploaded
- `functions_created: list[str]` - FunctionCrystal IDs
- `ghosts_created: list[str]` - GhostFunctionCrystal IDs
- `kblock_id: str | None` - Suggested K-block ID
- `errors: list[str]` - Error messages if any

**Example**:
```python
flow = SyncFlow(universe, boundary_detector)
result = await flow.upload_file("services/witness/store.py")
print(f"Created {len(result.functions_created)} functions")
print(f"Found {len(result.ghosts_created)} ghost placeholders")
if result.kblock_id:
    print(f"Suggested K-block: {result.kblock_id}")
```

### 2. `sync_directory(directory, pattern, incremental)`

**Purpose**: Sync a directory tree

**Steps**:
1. Find all matching files using glob pattern
2. For incremental sync: compare body_hash to detect changes
3. Create new FunctionCrystals for new files
4. Update changed FunctionCrystals (new body_hash)
5. Detect new ghost placeholders
6. Recompute K-block boundaries using BoundaryDetector

**Returns**: `SyncResult`
- `files_processed: int` - Number of files processed
- `functions_created: int` - Number of new FunctionCrystals
- `functions_updated: int` - Number of updated FunctionCrystals
- `functions_unchanged: int` - Number of unchanged functions
- `ghosts_created: int` - Number of new ghost placeholders
- `kblocks_suggested: int` - Number of K-block boundaries suggested
- `errors: list[str]` - Error messages if any

**Example**:
```python
result = await flow.sync_directory("services/witness")
print(f"Processed {result.files_processed} files")
print(f"Created {result.functions_created} new functions")
print(f"Updated {result.functions_updated} changed functions")
```

### 3. `bootstrap_spec_impl_pair(spec_content, impl_content, name)`

**Purpose**: Bootstrap spec+impl pair for QA

**Steps**:
1. Create SpecCrystal from spec_content (L4)
2. Parse impl_content into FunctionCrystals (L5)
3. Create derivation edges from functions to spec
4. Create K-block for the implementation
5. Validate the derivation chain (spec → impl)
6. Create proofs for each crystal

**Returns**: `BootstrapResult`
- `spec_id: str` - SpecCrystal ID
- `impl_functions: list[str]` - FunctionCrystal IDs
- `kblock_id: str` - K-block ID for implementation
- `derivation_edges: list[str]` - Edge IDs linking spec → impl

**Example**:
```python
spec = "# Add Function\\n\\nAdd two numbers."
impl = "def add(x: int, y: int) -> int:\\n    return x + y"
result = await flow.bootstrap_spec_impl_pair(spec, impl, "add")
print(f"Created spec: {result.spec_id}")
print(f"Created {len(result.impl_functions)} functions")
print(f"Created {len(result.derivation_edges)} derivation edges")
```

## Teaching Gotchas

### 1. Explicit, Not Automatic
```python
gotcha: SyncFlow is EXPLICIT, not automatic. No file watchers,
        no auto-sync, no magic. Every operation is user-triggered.
        (Evidence: Kent's directive - "explicit flows, NOT magic")
```

### 2. Ghosts Are Placeholders
```python
gotcha: Ghosts are PLACEHOLDERS, not errors. A ghost marks an
        implied function (called but not defined). This is normal
        during incremental development.
        (Evidence: agents/d/schemas/kblock.py::GhostFunctionCrystal)
```

### 3. K-Block Suggestions Are Suggestions
```python
gotcha: K-block suggestions are SUGGESTIONS. BoundaryDetector
        proposes boundaries with confidence scores. User can accept,
        reject, or modify. The system never forces a boundary.
        (Evidence: services/code/boundary.py::KBlockCandidate)
```

### 4. Incremental Sync Uses Body Hash
```python
gotcha: Incremental sync uses body_hash for change detection.
        Only functions with different body_hash get updated.
        This avoids recomputing proofs for unchanged functions.
        (Evidence: agents/d/schemas/code.py::FunctionCrystal.body_hash)
```

### 5. Derivation Edges Flow Downward
```python
gotcha: Derivation edges flow DOWNWARD in layer numbers.
        L4 (spec) → L5 (code). Parent layer < child layer.
        This is enforced at edge creation time.
        (Evidence: k_block/core/derivation.py::validate_derivation)
```

## Dependencies

### Imports
```python
from agents.d.universe.universe import Universe
from services.code.boundary import BoundaryDetector
from services.code.service import CodeService, UploadResult, SyncResult, BootstrapResult
```

### Schemas Used
```python
from agents.d.schemas.code import FunctionCrystal, ParamInfo
from agents.d.schemas.kblock import KBlockCrystal, GhostFunctionCrystal
from agents.d.schemas.spec import SpecCrystal
from agents.d.schemas.proof import GaloisWitnessedProof
```

## Delegation Pattern

SyncFlow is a **facade** over CodeService:

```python
class SyncFlow:
    def __init__(self, universe: Universe, boundary_detector: BoundaryDetector | None = None):
        self._universe = universe
        self._boundary = boundary_detector
        self._code_service = CodeService(universe=universe)

    async def upload_file(self, file_path, spec_id, auto_extract_functions):
        # Delegate to CodeService
        return await self._code_service.upload_file(
            file_path=str(file_path),
            spec_id=spec_id,
            auto_extract_functions=auto_extract_functions,
            create_kblock=True,
        )
```

**Why?**
- SyncFlow provides the user-facing API with explicit naming
- CodeService handles implementation details
- Clear separation of concerns: interface vs. implementation

## Philosophy

> "The user uploads. We parse. We suggest. They decide."

Three principles:
1. **User Control** - Every operation is explicit, user-triggered
2. **Transparency** - Full visibility into what was created (IDs, counts, errors)
3. **Suggestion, Not Enforcement** - K-block boundaries and ghosts are suggestions

## Kent's Workflow

Kent will use this service to:
1. **Insert trivial toy specs** - Minimal markdown specs for QA
2. **Insert trivial toy implementations** - Simple Python functions
3. **Bootstrap and QA the user journey** - Test full derivation chain
4. **Validate coherence** - Check Galois loss, derivation validation

Example QA session:
```python
# 1. Create trivial spec
spec = """
# Add Function

Adds two numbers and returns the result.

## Signature
add(x: int, y: int) -> int

## Examples
- add(2, 3) → 5
- add(-1, 1) → 0
"""

# 2. Create trivial implementation
impl = """
def add(x: int, y: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return x + y
"""

# 3. Bootstrap the pair
flow = SyncFlow(universe)
result = await flow.bootstrap_spec_impl_pair(spec, impl, "add_example")

# 4. Verify results
assert result.spec_id
assert len(result.impl_functions) == 1
assert len(result.derivation_edges) == 1
print("QA passed!")
```

## Next Steps

1. **Wire to AGENTESE** - Expose via `world.code.upload`, `world.code.sync`
2. **Add UI** - Web interface for file upload, directory selection
3. **Enhance parser** - Full support for classes, decorators, type annotations
4. **Add tests** - Property-based tests for parser, sync logic
5. **Galois integration** - Compute loss for uploaded functions
6. **Derivation tracking** - Link to DerivationService for spec→impl edges

## Related Files

- `/services/code/service.py` - CodeService implementation (463 lines)
- `/services/code/parser.py` - AST parser for Python functions
- `/services/code/boundary.py` - BoundaryDetector for K-block suggestions
- `/agents/d/schemas/code.py` - FunctionCrystal schema
- `/agents/d/schemas/kblock.py` - KBlockCrystal, GhostFunctionCrystal schemas
- `/agents/d/universe/universe.py` - Universe persistence layer

## Summary

Created 2 files, 524 total lines:
- `services/sync/__init__.py` (35 lines) - Module exports
- `services/sync/flow.py` (489 lines) - SyncFlow implementation

The SyncFlow service provides explicit user-driven upload and sync of code artifacts, following Kent's directive for explicit flows over magic. It delegates to the existing CodeService while providing a clean, well-documented user-facing API.
