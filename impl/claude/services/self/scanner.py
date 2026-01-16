"""
CodebaseScanner: Scan Python codebase and generate K-Block representations.

Uses Python's ast module to extract structure from source files:
- Module docstrings
- Class and function definitions
- Import statements (for derivation edges)

Enhanced with spec/ scanning (Phase 2):
- Scan spec/ directory for markdown files
- Link spec files to implementation files
- Extract metadata (line count, last modified, etc.)

Philosophy:
    "The system that knows itself can refine itself."

Usage:
    scanner = CodebaseScanner(project_root=Path("/path/to/project"))

    # Scan a single module
    kblock = await scanner.scan_module(Path("services/brain/__init__.py"))

    # Scan a directory
    kblocks = await scanner.scan_directory(Path("services"))

    # Infer import edges
    edges = scanner.infer_import_edges(kblocks)

    # Get full graph
    graph = await scanner.scan_to_graph(Path("services"))

    # Scan spec directory (NEW)
    specs = await scanner.scan_spec_directory()

    # Link spec to impl (NEW)
    pairs = await scanner.link_spec_to_impl()
"""

from __future__ import annotations

import ast
import hashlib
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import (
    ClassInfo,
    DerivationChain,
    Edge,
    FunctionInfo,
    KBlockGraph,
    KBlockInspection,
    ModuleKBlock,
)

# =============================================================================
# Spec Scanning Data Models
# =============================================================================


@dataclass(frozen=True)
class SpecFile:
    """
    K-Block representation of a specification file.

    Attributes:
        id: Unique K-Block ID
        path: File path relative to project root
        title: Spec title (from first H1 or filename)
        summary: First paragraph or abstract
        sections: H2 section headings
        references: Referenced files and specs
        tags: Extracted tags
        line_count: Number of lines
        last_modified: Last modification time
        galois_loss: Coherence metric
    """

    id: str
    path: str
    title: str
    summary: str
    sections: tuple[str, ...]
    references: tuple[str, ...]
    tags: tuple[str, ...]
    line_count: int
    last_modified: datetime
    galois_loss: float = 0.3  # L2-L3 spec layer default

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "path": self.path,
            "title": self.title,
            "summary": self.summary,
            "sections": list(self.sections),
            "references": list(self.references),
            "tags": list(self.tags),
            "line_count": self.line_count,
            "last_modified": self.last_modified.isoformat(),
            "galois_loss": self.galois_loss,
        }

    @classmethod
    def generate_id(cls, path: str) -> str:
        """Generate a deterministic ID from path."""
        hash_str = hashlib.sha256(path.encode()).hexdigest()[:12]
        return f"spec_{hash_str}"


@dataclass(frozen=True)
class SpecImplLink:
    """
    Link between a spec file and implementation files.

    Attributes:
        spec_path: Path to spec file
        impl_paths: Paths to implementation files
        confidence: Link confidence [0.0, 1.0]
        link_type: How the link was determined
        evidence: Evidence supporting the link
    """

    spec_path: str
    impl_paths: tuple[str, ...]
    confidence: float
    link_type: str  # "naming", "reference", "content"
    evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "spec_path": self.spec_path,
            "impl_paths": list(self.impl_paths),
            "confidence": self.confidence,
            "link_type": self.link_type,
            "evidence": list(self.evidence),
        }


@dataclass(frozen=True)
class FileMetadata:
    """
    Metadata for any file.

    Attributes:
        path: File path
        line_count: Number of lines
        char_count: Character count
        last_modified: Last modification time
        size_bytes: File size
        file_type: Detected file type
    """

    path: str
    line_count: int
    char_count: int
    last_modified: datetime
    size_bytes: int
    file_type: str  # "python", "markdown", "yaml", etc.

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "path": self.path,
            "line_count": self.line_count,
            "char_count": self.char_count,
            "last_modified": self.last_modified.isoformat(),
            "size_bytes": self.size_bytes,
            "file_type": self.file_type,
        }


logger = logging.getLogger(__name__)


class CodebaseScanner:
    """
    Scan Python codebase and generate K-Block representations.

    The scanner uses Python's ast module to extract:
    - Module docstrings
    - Class definitions with methods and base classes
    - Function definitions with parameters
    - Import statements for edge inference

    Attributes:
        project_root: Root directory of the project
        exclude_patterns: Glob patterns to exclude from scanning

    Teaching:
        gotcha: The scanner only handles syntactically valid Python files.
                Files with syntax errors are logged and skipped.
                (Evidence: test_scanner.py::test_scan_handles_syntax_errors)

        gotcha: Import edge inference uses module paths, not file paths.
                "from services.brain import X" creates edge to "services.brain".
                (Evidence: test_scanner.py::test_infer_import_edges)

        gotcha: galois_loss is computed based on docstring presence and
                structural completeness. No docstring = higher loss.
                (Evidence: test_scanner.py::test_galois_loss_computation)
    """

    def __init__(
        self,
        project_root: Path | None = None,
        exclude_patterns: tuple[str, ...] = ("__pycache__", ".git", "*.pyc", "node_modules"),
    ) -> None:
        """
        Initialize the CodebaseScanner.

        Args:
            project_root: Root directory of the project. Defaults to cwd.
            exclude_patterns: Patterns to exclude from scanning.
        """
        self.project_root = project_root or Path.cwd()
        self.exclude_patterns = exclude_patterns
        self._module_cache: dict[str, ModuleKBlock] = {}

    async def scan_module(self, module_path: Path) -> ModuleKBlock:
        """
        Scan a single Python module and generate K-Block representation.

        Args:
            module_path: Path to the module (relative to project_root or absolute)

        Returns:
            ModuleKBlock representing the module

        Raises:
            FileNotFoundError: If the file doesn't exist
            SyntaxError: If the file has Python syntax errors
        """
        # Resolve path
        if not module_path.is_absolute():
            full_path = self.project_root / module_path
        else:
            full_path = module_path

        if not full_path.exists():
            raise FileNotFoundError(f"Module not found: {full_path}")

        # Read source
        source = full_path.read_text(encoding="utf-8")
        content_hash = hashlib.sha256(source.encode()).hexdigest()[:16]

        # Parse AST
        try:
            tree = ast.parse(source, filename=str(full_path))
        except SyntaxError as e:
            logger.warning(f"Syntax error in {full_path}: {e}")
            # Return a minimal K-Block for files with syntax errors
            relative_path = str(module_path)
            if module_path.is_absolute():
                try:
                    relative_path = str(module_path.relative_to(self.project_root))
                except ValueError:
                    relative_path = str(module_path)

            return ModuleKBlock(
                id=ModuleKBlock.generate_id(relative_path),
                path=relative_path,
                docstring=None,
                classes=(),
                functions=(),
                imports=(),
                galois_loss=1.0,  # Maximum loss for unparseable files
                content_hash=content_hash,
            )

        # Extract docstring
        docstring = ast.get_docstring(tree)

        # Extract classes
        classes: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)

        # Extract functions (top-level only)
        functions: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                functions.append(node.name)

        # Extract imports
        imports: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        # Calculate relative path
        relative_path = str(module_path)
        if module_path.is_absolute():
            try:
                relative_path = str(module_path.relative_to(self.project_root))
            except ValueError:
                relative_path = str(module_path)

        # Compute galois_loss
        galois_loss = self._compute_galois_loss(
            docstring=docstring,
            classes=classes,
            functions=functions,
            source_lines=len(source.splitlines()),
        )

        kblock = ModuleKBlock(
            id=ModuleKBlock.generate_id(relative_path),
            path=relative_path,
            docstring=docstring,
            classes=tuple(classes),
            functions=tuple(functions),
            imports=tuple(set(imports)),  # Deduplicate
            galois_loss=galois_loss,
            content_hash=content_hash,
        )

        # Cache for edge inference
        self._module_cache[relative_path] = kblock

        return kblock

    async def scan_directory(self, dir_path: Path) -> list[ModuleKBlock]:
        """
        Scan all Python files in a directory (recursively).

        Args:
            dir_path: Directory path (relative to project_root or absolute)

        Returns:
            List of ModuleKBlocks for all Python files found
        """
        # Resolve path
        if not dir_path.is_absolute():
            full_path = self.project_root / dir_path
        else:
            full_path = dir_path

        if not full_path.exists():
            raise FileNotFoundError(f"Directory not found: {full_path}")

        if not full_path.is_dir():
            raise ValueError(f"Not a directory: {full_path}")

        kblocks: list[ModuleKBlock] = []

        # Walk directory
        for py_file in full_path.rglob("*.py"):
            # Skip excluded patterns
            if self._should_exclude(py_file):
                continue

            try:
                kblock = await self.scan_module(py_file)
                kblocks.append(kblock)
            except Exception as e:
                logger.warning(f"Failed to scan {py_file}: {e}")
                continue

        return kblocks

    def infer_import_edges(self, kblocks: list[ModuleKBlock]) -> list[Edge]:
        """
        Infer edges from import statements in K-Blocks.

        Creates an edge from module A to module B if A imports from B.

        Args:
            kblocks: List of ModuleKBlocks to analyze

        Returns:
            List of Edge objects representing import relationships
        """
        edges: list[Edge] = []

        # Build path -> id mapping
        path_to_id: dict[str, str] = {}
        for kblock in kblocks:
            # Map by module path (e.g., "services/brain/__init__.py" -> "services.brain")
            module_path = self._path_to_module(kblock.path)
            path_to_id[module_path] = kblock.id
            # Also map by exact file path
            path_to_id[kblock.path] = kblock.id

        # Create edges for imports
        for kblock in kblocks:
            for import_path in kblock.imports:
                # Normalize import path
                normalized = import_path.replace("/", ".")

                # Look for matching target
                target_id = path_to_id.get(normalized)

                # Try partial matches (e.g., "services.brain" matches "services.brain.persistence")
                if target_id is None:
                    for path, id_ in path_to_id.items():
                        if path.startswith(normalized + ".") or path == normalized:
                            target_id = id_
                            break

                if target_id and target_id != kblock.id:  # Don't create self-loops
                    edge = Edge(
                        id=f"edge_{uuid.uuid4().hex[:12]}",
                        source_id=kblock.id,
                        target_id=target_id,
                        edge_type="imports",
                        context=f"imports {import_path}",
                        confidence=1.0,
                    )
                    edges.append(edge)

        return edges

    async def scan_to_graph(self, dir_path: Path) -> KBlockGraph:
        """
        Scan a directory and return a complete K-Block graph.

        Combines scan_directory with infer_import_edges.

        Args:
            dir_path: Directory to scan

        Returns:
            KBlockGraph with nodes and edges
        """
        kblocks = await self.scan_directory(dir_path)
        edges = self.infer_import_edges(kblocks)

        return KBlockGraph(
            nodes=tuple(kblocks),
            edges=tuple(edges),
            root_path=str(dir_path),
        )

    async def inspect_module(self, module_path: Path) -> KBlockInspection:
        """
        Deep inspect a single module.

        Returns detailed information about classes, functions, and dependencies.

        Args:
            module_path: Path to the module

        Returns:
            KBlockInspection with detailed module information
        """
        # Scan module first
        kblock = await self.scan_module(module_path)

        # Resolve path for full analysis
        if not module_path.is_absolute():
            full_path = self.project_root / module_path
        else:
            full_path = module_path

        source = full_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(full_path))

        # Extract detailed class info
        classes: list[ClassInfo] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append(item.name)

                base_classes = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_classes.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        base_classes.append(ast.unparse(base))

                classes.append(
                    ClassInfo(
                        name=node.name,
                        docstring=ast.get_docstring(node),
                        methods=tuple(methods),
                        base_classes=tuple(base_classes),
                    )
                )

        # Extract detailed function info
        functions: list[FunctionInfo] = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                params = []
                for arg in node.args.args:
                    if arg.arg != "self":
                        params.append(arg.arg)

                functions.append(
                    FunctionInfo(
                        name=node.name,
                        docstring=ast.get_docstring(node),
                        parameters=tuple(params),
                        is_async=isinstance(node, ast.AsyncFunctionDef),
                    )
                )

        # Compute complexity (simplified McCabe estimate)
        complexity = self._estimate_complexity(tree)

        return KBlockInspection(
            kblock=kblock,
            classes=tuple(classes),
            functions=tuple(functions),
            source_lines=len(source.splitlines()),
            complexity_score=complexity,
            incoming_deps=(),  # Populated by graph analysis
            outgoing_deps=tuple(kblock.imports),
        )

    async def derive_chain(
        self,
        module_path: Path,
        graph: KBlockGraph | None = None,
        max_depth: int = 10,
    ) -> DerivationChain:
        """
        Trace the derivation chain for a module.

        Follows import edges back to find all dependencies.

        Args:
            module_path: Module to trace
            graph: Optional pre-computed graph (scans if not provided)
            max_depth: Maximum depth to traverse

        Returns:
            DerivationChain showing the import ancestry
        """
        # Get or build graph
        if graph is None:
            dir_path = module_path.parent
            graph = await self.scan_to_graph(dir_path)

        # Find the target node
        target = graph.get_node_by_path(str(module_path))
        if target is None:
            # Try with relative path
            try:
                relative_path = str(module_path.relative_to(self.project_root))
                target = graph.get_node_by_path(relative_path)
            except ValueError:
                pass

        if target is None:
            return DerivationChain(
                target_id="",
                target_path=str(module_path),
                chain=(),
                depth=0,
            )

        # BFS to find all ancestors
        chain: list[tuple[str, str, str | None]] = []
        visited: set[str] = {target.id}
        current_level = [target.id]
        depth = 0

        while current_level and depth < max_depth:
            next_level = []
            for node_id in current_level:
                # Find incoming edges (modules that this one imports)
                outgoing = graph.get_outgoing_edges(node_id)
                for edge in outgoing:
                    if edge.target_id not in visited:
                        visited.add(edge.target_id)
                        next_level.append(edge.target_id)
                        chain.append((edge.target_id, edge.edge_type, edge.context))

            current_level = next_level
            if next_level:
                depth += 1

        return DerivationChain(
            target_id=target.id,
            target_path=target.path,
            chain=tuple(chain),
            depth=depth,
        )

    def _should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded from scanning."""
        path_str = str(path)
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return True
        return False

    def _path_to_module(self, file_path: str) -> str:
        """
        Convert file path to module path.

        Examples:
            "services/brain/__init__.py" -> "services.brain"
            "services/brain/persistence.py" -> "services.brain.persistence"
        """
        # Remove .py extension
        path = file_path.replace(".py", "")
        # Remove __init__
        path = path.replace("/__init__", "")
        path = path.replace("\\__init__", "")
        # Convert slashes to dots
        path = path.replace("/", ".").replace("\\", ".")
        return path

    def _compute_galois_loss(
        self,
        docstring: str | None,
        classes: list[str],
        functions: list[str],
        source_lines: int,
    ) -> float:
        """
        Compute galois_loss for a module.

        The loss represents how well the module is documented and structured.
        Lower is better (0.0 = perfect, 1.0 = poor).

        Factors:
        - No docstring: +0.3
        - No classes or functions: +0.2
        - Very short docstring: +0.1
        - High lines-to-entity ratio: +0.2
        """
        loss = 0.0

        # Docstring presence
        if docstring is None:
            loss += 0.3
        elif len(docstring) < 50:
            loss += 0.1

        # Has structure
        entity_count = len(classes) + len(functions)
        if entity_count == 0:
            loss += 0.2

        # Lines-to-entity ratio (complexity indicator)
        if entity_count > 0 and source_lines > 0:
            ratio = source_lines / entity_count
            if ratio > 100:  # Very long functions/classes
                loss += 0.2
            elif ratio > 50:
                loss += 0.1

        return min(loss, 1.0)

    def _estimate_complexity(self, tree: ast.AST) -> float:
        """
        Estimate McCabe complexity of an AST.

        Simplified: counts branches (if, for, while, try, with).
        """
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1  # and/or chains

        return float(complexity)

    # =========================================================================
    # Spec Scanning Methods (Phase 2)
    # =========================================================================

    async def scan_spec_directory(
        self,
        spec_dir: str = "spec",
    ) -> list[SpecFile]:
        """
        Scan the spec/ directory for markdown files.

        Args:
            spec_dir: Relative path to spec directory

        Returns:
            List of SpecFile K-Blocks
        """
        spec_path = self.project_root / spec_dir

        if not spec_path.exists():
            logger.warning(f"Spec directory not found: {spec_path}")
            return []

        specs: list[SpecFile] = []

        for md_file in spec_path.rglob("*.md"):
            if self._should_exclude(md_file):
                continue

            try:
                spec = await self._scan_spec_file(md_file)
                specs.append(spec)
            except Exception as e:
                logger.warning(f"Failed to scan spec {md_file}: {e}")
                continue

        return specs

    async def _scan_spec_file(self, file_path: Path) -> SpecFile:
        """
        Scan a single spec file.

        Args:
            file_path: Path to the markdown file

        Returns:
            SpecFile K-Block
        """
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()
        stat = file_path.stat()

        # Extract title (first H1)
        title = file_path.stem.replace("-", " ").replace("_", " ").title()
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # Extract summary (first paragraph after title)
        summary = ""
        in_paragraph = False
        for line in lines:
            if line.startswith("# "):
                in_paragraph = True
                continue
            if in_paragraph:
                if line.strip() and not line.startswith("#"):
                    summary = line.strip()
                    break

        # Extract H2 sections
        sections = []
        for line in lines:
            if line.startswith("## "):
                sections.append(line[3:].strip())

        # Extract references (links to other files)
        references = []
        ref_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        for match in ref_pattern.finditer(content):
            ref = match.group(2)
            if ref.startswith("../") or ref.endswith(".md") or ref.endswith(".py"):
                references.append(ref)

        # Extract tags (from frontmatter or inline)
        tags = []
        tag_pattern = re.compile(r"#(\w+)")
        for match in tag_pattern.finditer(content[:500]):  # Check first 500 chars
            tag = match.group(1).lower()
            if tag not in ("", "1", "2", "3"):  # Filter out heading artifacts
                tags.append(tag)

        # Compute relative path
        try:
            relative_path = str(file_path.relative_to(self.project_root))
        except ValueError:
            relative_path = str(file_path)

        # Compute galois_loss for spec
        galois_loss = self._compute_spec_galois_loss(
            title=title,
            summary=summary,
            sections=sections,
            line_count=len(lines),
        )

        return SpecFile(
            id=SpecFile.generate_id(relative_path),
            path=relative_path,
            title=title,
            summary=summary[:200] if summary else "",
            sections=tuple(sections),
            references=tuple(set(references)),
            tags=tuple(set(tags)),
            line_count=len(lines),
            last_modified=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            galois_loss=galois_loss,
        )

    def _compute_spec_galois_loss(
        self,
        title: str,
        summary: str,
        sections: list[str],
        line_count: int,
    ) -> float:
        """
        Compute galois_loss for a spec file.

        Lower is better (0.0 = well-structured, 1.0 = poor).

        Factors:
        - No summary: +0.2
        - No sections: +0.2
        - Very short: +0.2
        - No structure (< 3 sections): +0.1
        """
        loss = 0.0

        if not summary or len(summary) < 20:
            loss += 0.2

        if not sections:
            loss += 0.2
        elif len(sections) < 3:
            loss += 0.1

        if line_count < 20:
            loss += 0.2

        return min(loss, 1.0)

    async def link_spec_to_impl(
        self,
        spec_dir: str = "spec",
        impl_dir: str = ".",
    ) -> list[SpecImplLink]:
        """
        Find links between spec files and implementation files.

        Uses multiple heuristics:
        1. Naming convention (spec/agents/x.md -> agents/x/)
        2. See: references in Python files
        3. Content mentions

        Args:
            spec_dir: Relative path to spec directory
            impl_dir: Relative path to impl directory

        Returns:
            List of SpecImplLink pairs
        """
        links: list[SpecImplLink] = []

        spec_path = self.project_root / spec_dir
        impl_path = self.project_root / impl_dir

        if not spec_path.exists():
            return links

        # Scan all spec files
        specs = await self.scan_spec_directory(spec_dir)

        # Build a mapping of Python files to their content
        py_files: dict[str, str] = {}
        if impl_path.exists():
            for py_file in impl_path.rglob("*.py"):
                if self._should_exclude(py_file):
                    continue
                try:
                    relative = str(py_file.relative_to(self.project_root))
                    py_files[relative] = py_file.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue

        for spec in specs:
            impl_matches: list[str] = []
            evidence: list[str] = []

            # Strategy 1: Naming convention
            # spec/agents/d-gent.md -> look for services/d/, agents/d/
            spec_stem = Path(spec.path).stem.replace("-", "_").replace("_", "")
            spec_parts = Path(spec.path).parts

            for py_path in py_files:
                py_parts = Path(py_path).parts

                # Check if spec name appears in path
                if spec_stem in py_path.lower().replace("-", "").replace("_", ""):
                    impl_matches.append(py_path)
                    evidence.append(f"naming: {spec_stem} in {py_path}")

            # Strategy 2: See: references
            spec_relative = spec.path
            for py_path, content in py_files.items():
                if f"See: {spec_relative}" in content or f"See: ../{spec_relative}" in content:
                    if py_path not in impl_matches:
                        impl_matches.append(py_path)
                        evidence.append(f"reference: See: {spec_relative} in {py_path}")

            # Strategy 3: Title/content mentions
            spec_title_lower = spec.title.lower()
            for py_path, content in py_files.items():
                # Check docstrings for spec title
                if spec_title_lower in content.lower()[:2000]:  # First 2000 chars
                    if py_path not in impl_matches:
                        impl_matches.append(py_path)
                        evidence.append(f"content: {spec.title} mentioned in {py_path}")

            if impl_matches:
                # Compute confidence based on evidence quality
                confidence = min(0.5 + 0.1 * len(evidence), 0.95)
                link_type = (
                    "mixed"
                    if len(set(e.split(":")[0] for e in evidence)) > 1
                    else evidence[0].split(":")[0]
                )

                links.append(
                    SpecImplLink(
                        spec_path=spec.path,
                        impl_paths=tuple(sorted(set(impl_matches))[:10]),  # Limit to 10
                        confidence=confidence,
                        link_type=link_type,
                        evidence=tuple(evidence[:5]),  # Limit evidence
                    )
                )

        return links

    async def get_file_metadata(self, file_path: str | Path) -> FileMetadata:
        """
        Get metadata for any file.

        Args:
            file_path: Path to file (relative or absolute)

        Returns:
            FileMetadata with line count, size, etc.
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = self.project_root / path

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        content = path.read_text(encoding="utf-8", errors="ignore")
        stat = path.stat()

        # Determine file type
        suffix = path.suffix.lower()
        file_type_map = {
            ".py": "python",
            ".md": "markdown",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".toml": "toml",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".jsx": "javascript",
            ".css": "css",
            ".html": "html",
        }
        file_type = file_type_map.get(suffix, "text")

        # Compute relative path
        try:
            relative = str(path.relative_to(self.project_root))
        except ValueError:
            relative = str(path)

        return FileMetadata(
            path=relative,
            line_count=len(content.splitlines()),
            char_count=len(content),
            last_modified=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            size_bytes=stat.st_size,
            file_type=file_type,
        )

    async def scan_all(
        self,
        impl_dirs: list[str] | None = None,
        spec_dir: str = "spec",
    ) -> dict[str, Any]:
        """
        Scan both impl and spec directories.

        Args:
            impl_dirs: List of implementation directories to scan
            spec_dir: Spec directory path

        Returns:
            Dictionary with modules, specs, and links
        """
        impl_dirs = impl_dirs or ["services", "agents", "protocols"]

        all_modules: list[ModuleKBlock] = []
        for impl_dir in impl_dirs:
            try:
                modules = await self.scan_directory(Path(impl_dir))
                all_modules.extend(modules)
            except FileNotFoundError:
                continue

        specs = await self.scan_spec_directory(spec_dir)
        links = await self.link_spec_to_impl(spec_dir)

        return {
            "modules": [m.to_dict() for m in all_modules],
            "specs": [s.to_dict() for s in specs],
            "links": [l.to_dict() for l in links],
            "stats": {
                "module_count": len(all_modules),
                "spec_count": len(specs),
                "link_count": len(links),
                "avg_module_galois_loss": sum(m.galois_loss for m in all_modules) / len(all_modules)
                if all_modules
                else 0.0,
                "avg_spec_galois_loss": sum(s.galois_loss for s in specs) / len(specs)
                if specs
                else 0.0,
            },
        }


__all__ = [
    "CodebaseScanner",
    "SpecFile",
    "SpecImplLink",
    "FileMetadata",
]
