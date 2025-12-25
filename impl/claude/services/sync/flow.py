"""
SyncFlow: Explicit user-driven upload and sync of code artifacts.

Context: Kent's guidance - explicit flows, NOT magic. User decides what enters the Universe.

This service provides three core flows:
1. upload_file() - Upload single file, extract functions, create ghosts
2. sync_directory() - Sync directory tree, detect changes, update functions
3. bootstrap_spec_impl_pair() - Bootstrap spec+impl for QA testing

Kent will insert trivial toy specs and implementations to bootstrap and QA
the user journey.

Architecture:
    SyncFlow wraps CodeService to provide explicit user-facing API.
    It delegates to:
    - CodeService for parsing and storage
    - BoundaryDetector for K-block suggestions
    - Universe for persistence
    - DerivationService for spec→impl linking (future)

Philosophy:
    "The user uploads. We parse. We suggest. They decide."

Teaching:
    gotcha: SyncFlow is EXPLICIT, not automatic. No file watchers,
            no auto-sync, no magic. Every operation is user-triggered.
            (Evidence: Kent's directive - "explicit flows, NOT magic")

    gotcha: Ghosts are PLACEHOLDERS, not errors. A ghost marks an
            implied function (called but not defined). This is normal
            during incremental development.
            (Evidence: agents/d/schemas/kblock.py::GhostFunctionCrystal)

    gotcha: K-block suggestions are SUGGESTIONS. BoundaryDetector
            proposes boundaries with confidence scores. User can accept,
            reject, or modify. The system never forces a boundary.
            (Evidence: services/code/boundary.py::KBlockCandidate)

See: spec/protocols/zero-seed.md
See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...agents.d.universe.universe import Universe
    from ..code.boundary import BoundaryDetector

# Re-export result types from CodeService for backward compatibility
from ..code.service import (
    BootstrapResult,
    CodeService,
    SyncResult,
    UploadResult,
)

# =============================================================================
# Additional Helper Types
# =============================================================================


@dataclass
class ParsedFunction:
    """
    Intermediate representation of parsed function.

    This is the output of parsing before crystallization.
    It contains all metadata needed to create a FunctionCrystal.
    """

    name: str
    """Function name (e.g., 'compute_loss')."""

    qualified_name: str
    """Fully qualified name (e.g., 'agents.d.galois.compute_loss')."""

    signature: str
    """Full signature (def compute_loss(x: float) -> float:)."""

    docstring: str | None
    """Docstring if present."""

    body: str
    """Function body as source code."""

    line_start: int
    """Starting line number (1-indexed)."""

    line_end: int
    """Ending line number (inclusive)."""

    parameters: list[tuple[str, str | None, str | None]]
    """List of (name, type_annotation, default) tuples."""

    return_type: str | None
    """Return type annotation as string."""

    calls: set[str]
    """Set of function names called by this function."""

    imports: set[str]
    """Set of imports used by this function."""

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of function body for change detection."""
        return hashlib.sha256(self.body.encode("utf-8")).hexdigest()[:16]


# =============================================================================
# SyncFlow: Explicit User-Driven Upload & Sync
# =============================================================================


class SyncFlow:
    """
    Explicit user-driven sync flows for code artifacts.

    NOT magic. User decides what enters the Universe.

    Three core flows:
    1. upload_file - Single file upload with function extraction
    2. sync_directory - Directory tree sync with change detection
    3. bootstrap_spec_impl_pair - Spec+impl QA bootstrapping

    Architecture:
        SyncFlow delegates to CodeService for implementation.
        It provides the explicit user-facing API while CodeService
        handles parsing, storage, and crystal creation.

    Philosophy:
        "The user uploads. We parse. We suggest. They decide."

    Usage:
        >>> flow = SyncFlow(universe, boundary_detector)
        >>> result = await flow.upload_file("path/to/file.py")
        >>> print(f"Created {len(result.functions_created)} functions")
        >>> print(f"Found {len(result.ghosts_created)} ghost placeholders")
        >>> if result.kblock_id:
        ...     print(f"Suggested K-block: {result.kblock_id}")
    """

    def __init__(
        self,
        universe: Universe,
        boundary_detector: BoundaryDetector | None = None,
    ):
        """
        Initialize SyncFlow.

        Args:
            universe: Universe for persistence
            boundary_detector: Optional boundary detector for K-block suggestions
        """
        self._universe = universe
        self._boundary = boundary_detector
        self._code_service = CodeService(universe=universe)

    async def upload_file(
        self,
        file_path: str | Path,
        spec_id: str | None = None,
        auto_extract_functions: bool = True,
    ) -> UploadResult:
        """
        Upload a single file to the Universe.

        Steps:
        1. Parse file into FunctionCrystals using AST parser
        2. Create ghost placeholders for undefined references
        3. Link to spec if provided (via derivation edges)
        4. Suggest K-block boundary using BoundaryDetector

        This is the atomic unit of sync. User uploads one file,
        we parse it, extract functions, and suggest organization.

        Args:
            file_path: Path to Python file to upload
            spec_id: Optional spec ID to link functions to
            auto_extract_functions: Whether to extract functions (default: True)

        Returns:
            UploadResult containing:
            - file_path: Path that was uploaded
            - functions_created: List of FunctionCrystal IDs
            - ghosts_created: List of GhostFunctionCrystal IDs
            - kblock_id: Suggested K-block ID (or None)
            - errors: List of error messages if any

        Teaching:
            gotcha: This creates FunctionCrystals, not just metadata.
                    Each function gets a proof, a body_hash, and full
                    parameter/call graph information.
                    (Evidence: agents/d/schemas/code.py::FunctionCrystal)

            gotcha: Ghosts are NOT errors. They mark called-but-undefined
                    functions. This is normal during incremental development.
                    User can upload the missing file later, and ghosts resolve.
                    (Evidence: agents/d/schemas/kblock.py::GhostFunctionCrystal)

        Example:
            >>> result = await flow.upload_file("services/witness/store.py")
            >>> print(f"Created {len(result.functions_created)} functions")
            >>> if result.ghosts_created:
            ...     print(f"Found {len(result.ghosts_created)} undefined calls")
            >>> if result.kblock_id:
            ...     print(f"Suggested K-block: {result.kblock_id}")
        """
        # Delegate to CodeService
        return await self._code_service.upload_file(
            file_path=str(file_path),
            spec_id=spec_id,
            auto_extract_functions=auto_extract_functions,
            create_kblock=True,
        )

    async def sync_directory(
        self,
        directory: str | Path,
        pattern: str = "**/*.py",
        incremental: bool = True,
    ) -> SyncResult:
        """
        Sync a directory tree.

        Steps:
        1. Find all matching files using glob pattern
        2. For incremental sync: compare body_hash to detect changes
        3. Create new FunctionCrystals for new files
        4. Update changed FunctionCrystals (new body_hash)
        5. Detect new ghost placeholders
        6. Recompute K-block boundaries using BoundaryDetector

        This is the batch operation. User syncs a whole directory,
        we process all files, track changes, and suggest organization.

        Args:
            directory: Directory to sync
            pattern: Glob pattern for files (default: **/*.py)
            incremental: Whether to skip unchanged files (default: True)

        Returns:
            SyncResult containing:
            - files_processed: Number of files processed
            - files_changed: Number of files that changed (incremental only)
            - functions_created: Number of new FunctionCrystals
            - functions_updated: Number of updated FunctionCrystals
            - ghosts_created: Number of new ghost placeholders
            - kblocks_suggested: Number of K-block boundaries suggested
            - errors: List of error messages if any

        Teaching:
            gotcha: Incremental sync uses body_hash for change detection.
                    Only functions with different body_hash get updated.
                    This avoids recomputing proofs for unchanged functions.
                    (Evidence: agents/d/schemas/code.py::FunctionCrystal.body_hash)

            gotcha: K-block recomputation happens AFTER all files sync.
                    BoundaryDetector analyzes the full set of functions
                    and proposes boundaries. Old boundaries may be invalidated.
                    (Evidence: services/code/boundary.py::BoundaryDetector)

        Example:
            >>> result = await flow.sync_directory("services/witness")
            >>> print(f"Processed {result.files_processed} files")
            >>> print(f"Created {result.functions_created} new functions")
            >>> print(f"Updated {result.functions_updated} changed functions")
            >>> print(f"Suggested {result.kblocks_suggested} K-block boundaries")
        """
        # Delegate to CodeService
        return await self._code_service.sync_directory(
            directory=str(directory),
            pattern=pattern,
            incremental=incremental,
        )

    async def bootstrap_spec_impl_pair(
        self,
        spec_content: str,
        impl_content: str,
        name: str,
    ) -> BootstrapResult:
        """
        Bootstrap a spec+impl pair for QA.

        Kent's workflow: Insert trivial toy specs and implementations
        to test the full user journey. This creates the complete derivation
        chain from spec (L4) to implementation (L5).

        Steps:
        1. Create SpecCrystal from spec_content (L4)
        2. Parse impl_content into FunctionCrystals (L5)
        3. Create derivation edges from functions to spec
        4. Create K-block for the implementation
        5. Validate the derivation chain (spec → impl)
        6. Create proofs for each crystal

        This is the QA flow. User provides a minimal spec+impl pair,
        we create the full crystal taxonomy and validate coherence.

        Args:
            spec_content: Markdown specification content
            impl_content: Python implementation content
            name: Name for the spec+impl pair

        Returns:
            BootstrapResult containing:
            - spec_id: SpecCrystal ID
            - impl_ids: List of FunctionCrystal IDs
            - kblock_id: K-block ID for implementation
            - derivation_edges: List of edge IDs linking spec → impl
            - validation_passed: Whether derivation validation passed
            - errors: List of validation errors if any

        Teaching:
            gotcha: Derivation edges flow DOWNWARD in layer numbers.
                    L4 (spec) → L5 (code). Parent layer < child layer.
                    This is enforced at edge creation time.
                    (Evidence: k_block/core/derivation.py::validate_derivation)

            gotcha: SpecCrystal requires a goal_prompt_id (L3 parent).
                    For bootstrap, we create a trivial GoalPromptCrystal
                    to satisfy the derivation chain requirement.
                    (Evidence: agents/d/schemas/spec.py::SpecCrystal)

            gotcha: Validation computes Galois loss for the derivation chain.
                    High loss = spec/impl drift = needs attention.
                    validation_passed = True only if loss below threshold.
                    (Evidence: agents/d/galois.py::GaloisLossComputer)

        Example:
            >>> spec = "# Add Function\\n\\nAdd two numbers."
            >>> impl = "def add(x: int, y: int) -> int:\\n    return x + y"
            >>> result = await flow.bootstrap_spec_impl_pair(spec, impl, "add")
            >>> print(f"Created spec: {result.spec_id}")
            >>> print(f"Created {len(result.impl_ids)} functions")
            >>> print(f"Created {len(result.derivation_edges)} derivation edges")
            >>> if result.validation_passed:
            ...     print("Derivation chain validated!")
        """
        # Delegate to CodeService
        return await self._code_service.bootstrap_spec_impl_pair(
            spec_content=spec_content,
            impl_content=impl_content,
            name=name,
        )

    # -------------------------------------------------------------------------
    # Helper Methods (Internal)
    # -------------------------------------------------------------------------

    def _parse_python_file(self, content: str) -> list[ParsedFunction]:
        """
        Parse Python file into function definitions.

        Uses AST parser to extract function metadata.
        This is a thin wrapper around CodeService's parser.

        Args:
            content: Python source code content

        Returns:
            List of ParsedFunction objects

        Note:
            This is for internal use. External callers should use
            upload_file() or sync_directory() instead.
        """
        # This is handled by CodeService's SimplePythonParser
        # We expose it here for completeness, but it's rarely called directly
        import ast
        import tempfile

        # Write to temp file for parser
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            functions = self._code_service._parser.parse_file(temp_path)

            # Convert to ParsedFunction
            return [
                ParsedFunction(
                    name=f.name,
                    qualified_name=f.qualified_name,
                    signature="",  # Simplified
                    docstring=f.docstring,
                    body=f.body,
                    line_start=f.line_start,
                    line_end=f.line_end,
                    parameters=[],  # Simplified
                    return_type=None,
                    calls=set(f.calls),
                    imports=set(),
                )
                for f in functions
            ]
        finally:
            import os

            os.unlink(temp_path)

    def _create_function_crystal(
        self, parsed: ParsedFunction, file_path: str
    ) -> str:
        """
        Create FunctionCrystal from parsed function.

        This is handled by CodeService internally.
        Exposed here for documentation purposes.

        Args:
            parsed: ParsedFunction metadata
            file_path: Source file path

        Returns:
            FunctionCrystal ID

        Note:
            This is for internal use. External callers should use
            upload_file() which handles crystal creation automatically.
        """
        # This is handled by CodeService.upload_file()
        # We expose it here for completeness
        raise NotImplementedError(
            "Use upload_file() instead - it handles crystal creation automatically"
        )

    def _detect_undefined_calls(self, functions: list[ParsedFunction]) -> list[str]:
        """
        Find calls to undefined functions (ghost candidates).

        Ghosts are functions that are:
        - Called by defined functions
        - But not defined in the current file/directory

        Args:
            functions: List of parsed functions

        Returns:
            List of undefined function names (ghost candidates)

        Note:
            This is for internal use. External callers get ghosts
            automatically in UploadResult.ghosts_created.
        """
        # This is handled by CodeService._detect_ghosts()
        all_defined = {f.name for f in functions}
        all_calls = set()
        for func in functions:
            all_calls.update(func.calls)

        # Ghosts = calls - defined
        ghosts = all_calls - all_defined
        return list(ghosts)

    def _compute_file_hash(self, path: Path) -> str:
        """
        Compute hash for change detection.

        Used for incremental sync to detect file changes.

        Args:
            path: File path

        Returns:
            SHA-256 hash (truncated to 16 chars)
        """
        content = path.read_bytes()
        return hashlib.sha256(content).hexdigest()[:16]


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "SyncFlow",
    "UploadResult",
    "SyncResult",
    "BootstrapResult",
    "ParsedFunction",
]
