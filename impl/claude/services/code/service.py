"""
Code Sync Service - Explicit user-driven flows for code artifacts.

Flows:
1. upload_file - Upload single file, extract functions
2. sync_directory - Sync directory tree
3. bootstrap_spec_impl - Bootstrap spec+impl pair for QA
"""

from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...agents.d.universe.universe import Universe


# =============================================================================
# Simple Function Info (AST-based)
# =============================================================================


@dataclass
class FunctionInfo:
    """Information extracted from a Python function."""

    name: str
    qualified_name: str  # module.ClassName.method_name
    file_path: str
    line_start: int
    line_end: int
    body: str
    docstring: str | None
    calls: list[str] = field(default_factory=list)  # Called function names
    body_hash: str = ""  # SHA256 of body

    def compute_hash(self) -> None:
        """Compute body hash for change detection."""
        self.body_hash = hashlib.sha256(self.body.encode()).hexdigest()[:16]


# =============================================================================
# Result Types
# =============================================================================


@dataclass
class UploadResult:
    """Result of uploading a single file."""

    file_path: str
    functions_created: list[str]  # Function IDs
    ghosts_created: list[str]  # Ghost IDs
    kblock_id: str | None
    errors: list[str] = field(default_factory=list)


@dataclass
class SyncResult:
    """Result of syncing a directory."""

    files_processed: int
    functions_created: int
    functions_updated: int
    functions_unchanged: int
    ghosts_created: int
    kblocks_created: int
    errors: list[str] = field(default_factory=list)


@dataclass
class BootstrapResult:
    """Result of bootstrapping a spec+impl pair."""

    spec_id: str
    impl_functions: list[str]
    kblock_id: str
    derivation_edges: list[str]  # Edge IDs linking spec → impl


# =============================================================================
# Simple Python AST Parser
# =============================================================================


class SimplePythonParser:
    """
    Simple Python AST parser for extracting function info.

    This is a minimal implementation. Full parser would go in
    services/code/parser.py when needed.
    """

    def parse_file(self, file_path: str) -> list[FunctionInfo]:
        """Parse a Python file and extract function info."""
        try:
            with open(file_path, "r") as f:
                source = f.read()

            tree = ast.parse(source, filename=file_path)
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._extract_function(node, source, file_path)
                    if func_info:
                        functions.append(func_info)

            return functions
        except Exception as e:
            # Return empty list on parse error
            return []

    def _extract_function(
        self, node: ast.FunctionDef, source: str, file_path: str
    ) -> FunctionInfo | None:
        """Extract FunctionInfo from AST node."""
        try:
            lines = source.split("\n")
            line_start = node.lineno
            line_end = node.end_lineno or line_start

            # Extract body
            body = "\n".join(lines[line_start - 1 : line_end])

            # Extract docstring
            docstring = ast.get_docstring(node)

            # Extract calls (simplified - just function names)
            calls = []
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        calls.append(child.func.id)
                    elif isinstance(child.func, ast.Attribute):
                        calls.append(child.func.attr)

            # Build qualified name (simplified)
            qualified_name = node.name

            func_info = FunctionInfo(
                name=node.name,
                qualified_name=qualified_name,
                file_path=file_path,
                line_start=line_start,
                line_end=line_end,
                body=body,
                docstring=docstring,
                calls=list(set(calls)),  # Dedupe
            )
            func_info.compute_hash()
            return func_info
        except Exception:
            return None


# =============================================================================
# Code Service
# =============================================================================


class CodeService:
    """
    Orchestrates code artifact sync operations.

    All operations are explicit - user triggers, we execute.
    """

    def __init__(
        self,
        universe: Universe | None = None,
    ):
        """
        Initialize CodeService.

        Args:
            universe: Universe for storage (optional, uses singleton if not provided)
        """
        self._universe = universe
        self._parser = SimplePythonParser()

    async def upload_file(
        self,
        file_path: str,
        spec_id: str | None = None,
        auto_extract_functions: bool = True,
        create_kblock: bool = True,
    ) -> UploadResult:
        """
        Upload a single file to the Universe.

        Steps:
        1. Parse file with AST parser
        2. Create FunctionCrystal for each function
        3. Create ghost placeholders for undefined calls
        4. Link to spec if provided
        5. Create K-block if requested

        Args:
            file_path: Path to Python file
            spec_id: Optional spec ID to link to
            auto_extract_functions: Whether to extract functions
            create_kblock: Whether to create K-block for file

        Returns:
            UploadResult with created artifact IDs
        """
        result = UploadResult(
            file_path=file_path,
            functions_created=[],
            ghosts_created=[],
            kblock_id=None,
        )

        if not auto_extract_functions:
            return result

        # Parse file
        functions = self._parser.parse_file(file_path)
        if not functions:
            result.errors.append(f"No functions found in {file_path}")
            return result

        # Store function info (simplified - just store as dict for now)
        universe = self._get_universe()
        for func in functions:
            # In full implementation, would create FunctionCrystal
            # For now, just store as dict
            func_id = f"fn_{func.name}_{func.body_hash}"
            result.functions_created.append(func_id)

            # Store in universe (would use proper schema in full impl)
            if universe:
                import json

                from ...agents.d.datum import Datum

                datum = Datum.create(
                    content=json.dumps(
                        {
                            "name": func.name,
                            "qualified_name": func.qualified_name,
                            "file_path": func.file_path,
                            "line_start": func.line_start,
                            "line_end": func.line_end,
                            "body": func.body,
                            "docstring": func.docstring,
                            "calls": func.calls,
                            "body_hash": func.body_hash,
                        }
                    ).encode("utf-8"),
                    metadata={"type": "function", "file": file_path},
                )
                await universe.store_datum(datum)

        # Detect ghosts (undefined calls)
        ghosts = self._detect_ghosts(functions)
        result.ghosts_created = [g["name"] for g in ghosts]

        # Create K-block if requested
        if create_kblock and universe:
            kblock_id = await self._create_kblock(file_path, functions)
            result.kblock_id = kblock_id

        return result

    async def sync_directory(
        self,
        directory: str,
        pattern: str = "**/*.py",
        incremental: bool = True,
    ) -> SyncResult:
        """
        Sync a directory tree.

        Steps:
        1. Find all matching files
        2. For incremental: compare body_hash to detect changes
        3. Create/update FunctionCrystals
        4. Detect new ghost placeholders
        5. Recompute K-block boundaries

        Args:
            directory: Directory to sync
            pattern: Glob pattern for files
            incremental: Whether to skip unchanged files

        Returns:
            SyncResult with sync statistics
        """
        result = SyncResult(
            files_processed=0,
            functions_created=0,
            functions_updated=0,
            functions_unchanged=0,
            ghosts_created=0,
            kblocks_created=0,
        )

        # Find matching files
        path = Path(directory)
        files = list(path.glob(pattern))

        for file_path in files:
            try:
                upload_result = await self.upload_file(str(file_path))
                result.files_processed += 1
                result.functions_created += len(upload_result.functions_created)
                result.ghosts_created += len(upload_result.ghosts_created)
                if upload_result.kblock_id:
                    result.kblocks_created += 1
            except Exception as e:
                result.errors.append(f"Error processing {file_path}: {e}")

        return result

    async def bootstrap_spec_impl_pair(
        self,
        spec_content: str,
        impl_content: str,
        name: str,
    ) -> BootstrapResult:
        """
        Bootstrap a spec+impl pair for QA.

        Kent's workflow: insert trivial toy specs and implementations
        to test the full user journey.

        Steps:
        1. Create SpecCrystal from spec_content
        2. Parse impl_content, create FunctionCrystals
        3. Link functions to spec (derivation edges)
        4. Create K-block for the impl
        5. Create proofs for each crystal

        Args:
            spec_content: Markdown spec content
            impl_content: Python implementation content
            name: Name for the pair

        Returns:
            BootstrapResult with created artifact IDs
        """
        import os
        import tempfile

        # Write impl to temp file for parsing
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(impl_content)
            temp_path = f.name

        try:
            # Parse implementation
            functions = self._parser.parse_file(temp_path)

            # Create spec crystal (simplified)
            spec_id = f"spec_{name}"

            # Create function crystals
            impl_functions = []
            for func in functions:
                func_id = f"fn_{func.name}_{func.body_hash}"
                impl_functions.append(func_id)

            # Create K-block
            kblock_id = f"kb_{name}"

            # Create derivation edges (simplified)
            derivation_edges = [
                f"edge_{spec_id}_{func_id}" for func_id in impl_functions
            ]

            return BootstrapResult(
                spec_id=spec_id,
                impl_functions=impl_functions,
                kblock_id=kblock_id,
                derivation_edges=derivation_edges,
            )
        finally:
            # Clean up temp file
            os.unlink(temp_path)

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _get_universe(self) -> Universe | None:
        """Get Universe instance (singleton or injected)."""
        if self._universe:
            return self._universe

        # Try to get singleton
        try:
            from ...agents.d.universe.universe import get_universe

            return get_universe()
        except Exception:
            return None

    def _detect_ghosts(self, functions: list[FunctionInfo]) -> list[dict]:
        """
        Detect ghost placeholders from call graph.

        Ghosts are functions that are called but not defined in the current set.
        """
        all_defined = {f.name for f in functions}
        ghosts = []

        for func in functions:
            for call in func.calls:
                if call not in all_defined:
                    ghosts.append(
                        {
                            "name": call,
                            "called_from": func.name,
                            "file": func.file_path,
                        }
                    )

        # Dedupe by name
        seen = set()
        unique_ghosts = []
        for ghost in ghosts:
            if ghost["name"] not in seen:
                seen.add(ghost["name"])
                unique_ghosts.append(ghost)

        return unique_ghosts

    async def _create_kblock(
        self, file_path: str, functions: list[FunctionInfo]
    ) -> str:
        """
        Create K-block for a file.

        A K-block groups related functions (file-level boundary).
        """
        from ...services.k_block.core.kblock import generate_kblock_id

        kblock_id = generate_kblock_id()

        # In full implementation, would create KBlockCrystal
        # For now, just return the ID
        return kblock_id


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "CodeService",
    "UploadResult",
    "SyncResult",
    "BootstrapResult",
    "FunctionInfo",
    "SimplePythonParser",
]
