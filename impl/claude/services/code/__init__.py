"""
Code Crown Jewel: Function-level artifact tracking.

The Code Crown Jewel tracks Python code at function granularity:
- Functions as atomic crystals
- K-Blocks as file-level boundaries
- Ghosts as spec placeholders
- Call graphs as semantic edges

Architecture:
- CodeService: Core business logic for artifact tracking
- CodeNode: AGENTESE exposure (world.code.*)
- CodePersistence: D-gent storage layer

AGENTESE Paths:
- world.code.manifest      - Code layer status
- world.code.upload        - Upload single file
- world.code.sync          - Sync directory
- world.code.bootstrap     - Bootstrap spec+impl pair
- world.code.function.list - List functions
- world.code.function.get  - Get function by ID
- world.code.function.graph - Get call graph
- world.code.kblock.list   - List K-blocks
- world.code.kblock.get    - Get K-block with contents
- world.code.kblock.suggest - Suggest boundary changes
- world.code.ghost.list    - List ghost placeholders
- world.code.ghost.resolve - Mark ghost as resolved

See: spec/crown-jewels/code.md (when created)
"""

from __future__ import annotations

__all__ = [
    "CodeService",
    "UploadResult",
    "SyncResult",
    "BootstrapResult",
    "FunctionInfo",
    # Parser
    "PythonFunctionParser",
    "parse_file",
    "extract_imports",
    "extract_calls",
    "compute_body_hash",
    "signature_to_string",
    # Boundary Detection
    "BoundaryDetector",
    "BoundaryStrategy",
    "FunctionCrystal",
    "KBlockCandidate",
    "MergeSuggestion",
    "SplitSuggestion",
]

from .service import (
    CodeService,
    UploadResult,
    SyncResult,
    BootstrapResult,
    FunctionInfo,
)
from .parser import (
    PythonFunctionParser,
    parse_file,
    extract_imports,
    extract_calls,
    compute_body_hash,
    signature_to_string,
)
from .boundary import (
    BoundaryDetector,
    BoundaryStrategy,
    FunctionCrystal,
    KBlockCandidate,
    MergeSuggestion,
    SplitSuggestion,
)
