"""
Gestalt Architecture Analysis.

Static analysis for Python and TypeScript codebases.
Extracts import graphs and computes health metrics.

Key Types:
- Module: A code module (file or package)
- DependencyEdge: An import relationship
- ModuleHealth: Health metrics for a module
- ArchitectureGraph: The full dependency graph with health
- Analyzer: Protocol for language-specific analyzers (extensible)
- AnalyzerRegistry: Registry for managing analyzers

Extension Point:
To add a new language analyzer, implement the Analyzer protocol and
register it with the AnalyzerRegistry:

    class GoAnalyzer:
        def can_analyze(self, path: Path) -> bool:
            return path.suffix == ".go"

        def analyze_source(self, source: str, module_name: str) -> list[DependencyEdge]:
            # Parse Go imports...
            return edges

        def analyze_file(self, path: Path) -> Module:
            # Full analysis...
            return module

    registry = AnalyzerRegistry()
    registry.register("go", GoAnalyzer())
"""

from __future__ import annotations

import ast
import re
from abc import abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Protocol, runtime_checkable

if TYPE_CHECKING:
    pass

# ============================================================================
# Core Types
# ============================================================================


@dataclass(frozen=True)
class DependencyEdge:
    """An import relationship between modules."""

    source: str  # Importing module
    target: str  # Imported module
    import_type: str = "standard"  # standard, from, dynamic
    line_number: int = 0
    is_type_only: bool = False  # TypeScript type-only imports


@dataclass
class ModuleHealth:
    """
    Health metrics for a code module.

    All metrics are 0-1 normalized:
    - 0 = worst (high coupling, low cohesion, etc.)
    - 1 = best (low coupling, high cohesion, etc.)
    """

    name: str
    coupling: float = 0.0  # 0-1, lower = better (0 = low coupling)
    cohesion: float = 1.0  # 0-1, higher = better
    drift: float = 0.0  # 0-1, lower = better (0 = no drift)
    complexity: float = 0.0  # 0-1, lower = better (0 = simple)
    churn: float = 0.0  # 0-1, lower = better (0 = stable)
    coverage: float = 1.0  # 0-1, higher = better
    instability: float | None = None  # Martin metric (Ce / (Ca + Ce))

    @property
    def overall_health(self) -> float:
        """
        Compute overall health score (0-1, higher = better).

        Weights:
        - Drift: 25% (most critical - architectural violations)
        - Coupling: 20% (modularity)
        - Cohesion: 15% (single responsibility)
        - Complexity: 15% (maintainability)
        - Churn: 10% (stability)
        - Coverage: 15% (test confidence)
        """
        return (
            (1 - self.drift) * 0.25
            + (1 - self.coupling) * 0.20
            + self.cohesion * 0.15
            + (1 - self.complexity) * 0.15
            + (1 - self.churn) * 0.10
            + self.coverage * 0.15
        )

    @property
    def grade(self) -> str:
        """Letter grade for overall health."""
        score = self.overall_health
        if score >= 0.95:
            return "A+"
        elif score >= 0.90:
            return "A"
        elif score >= 0.85:
            return "B+"
        elif score >= 0.80:
            return "B"
        elif score >= 0.75:
            return "C+"
        elif score >= 0.70:
            return "C"
        elif score >= 0.60:
            return "D"
        else:
            return "F"


@dataclass
class Module:
    """A code module (file or package)."""

    name: str  # Module name (e.g., "agents.m.cartographer")
    path: Path | None = None  # File path if available
    is_package: bool = False
    lines_of_code: int = 0
    imports: list[DependencyEdge] = field(default_factory=list)
    exported_symbols: list[str] = field(default_factory=list)
    health: ModuleHealth | None = None
    layer: str | None = None  # Assigned architectural layer
    tags: set[str] = field(default_factory=set)


@dataclass
class ArchitectureGraph:
    """
    The full architecture graph for a codebase.

    Contains modules, dependencies, and computed metrics.
    """

    modules: dict[str, Module] = field(default_factory=dict)
    edges: list[DependencyEdge] = field(default_factory=list)
    root_path: Path | None = None
    language: str = "python"

    @property
    def module_count(self) -> int:
        """Number of modules."""
        return len(self.modules)

    @property
    def edge_count(self) -> int:
        """Number of dependency edges."""
        return len(self.edges)

    @property
    def average_health(self) -> float:
        """Average health score across all modules."""
        healths = [m.health.overall_health for m in self.modules.values() if m.health]
        return sum(healths) / len(healths) if healths else 0.0

    @property
    def overall_grade(self) -> str:
        """Overall architecture grade."""
        score = self.average_health
        if score >= 0.95:
            return "A+"
        elif score >= 0.90:
            return "A"
        elif score >= 0.85:
            return "B+"
        elif score >= 0.80:
            return "B"
        elif score >= 0.75:
            return "C+"
        elif score >= 0.70:
            return "C"
        elif score >= 0.60:
            return "D"
        else:
            return "F"

    def get_dependents(self, module_name: str) -> list[str]:
        """Get modules that depend on the given module."""
        return [e.source for e in self.edges if e.target == module_name]

    def get_dependencies(self, module_name: str) -> list[str]:
        """Get modules that the given module depends on."""
        return [e.target for e in self.edges if e.source == module_name]

    def compute_instability(self, module_name: str) -> float | None:
        """
        Compute Martin's instability metric for a module.

        I = Ce / (Ca + Ce)
        - Ce = efferent coupling (outgoing dependencies)
        - Ca = afferent coupling (incoming dependencies)

        I = 0: Maximally stable (depended upon, no dependencies)
        I = 1: Maximally unstable (depends on others, not depended upon)
        """
        ce = len(self.get_dependencies(module_name))
        ca = len(self.get_dependents(module_name))
        total = ca + ce
        return ce / total if total > 0 else None


# ============================================================================
# Analyzer Protocol (Extensibility Point)
# ============================================================================


@runtime_checkable
class Analyzer(Protocol):
    """
    Protocol for language-specific code analyzers.

    Implement this protocol to add support for new languages.
    Each analyzer handles:
    1. Source code parsing (analyze_source)
    2. Full file analysis (analyze_file)
    3. File discovery (discover)

    Example:
        class RustAnalyzer:
            def can_analyze(self, path: Path) -> bool:
                return path.suffix == ".rs"

            def analyze_source(self, source: str, module_name: str) -> list[DependencyEdge]:
                # Parse Rust `use` statements...
                return edges

            def analyze_file(self, path: Path) -> Module:
                source = path.read_text()
                imports = self.analyze_source(source, path.stem)
                return Module(name=path.stem, path=path, imports=imports)

            def discover(self, root: Path) -> Iterator[Path]:
                return root.rglob("*.rs")
    """

    @abstractmethod
    def can_analyze(self, path: Path) -> bool:
        """Check if this analyzer can handle the given file."""
        ...

    @abstractmethod
    def analyze_source(self, source: str, module_name: str = "unknown") -> list[DependencyEdge]:
        """
        Extract imports from source code string.

        This is the core parsing method - useful for:
        - In-memory analysis (IDE integrations)
        - Testing without file system
        - Streaming analysis

        Args:
            source: Source code as string
            module_name: Name to use for the source module

        Returns:
            List of DependencyEdge objects
        """
        ...

    @abstractmethod
    def analyze_file(self, path: Path) -> Module:
        """
        Analyze a single file and return a Module.

        This handles file I/O and full analysis including:
        - Line counting
        - Export extraction
        - Import parsing

        Args:
            path: Path to the file

        Returns:
            Module with imports and metadata
        """
        ...

    @abstractmethod
    def discover(self, root: Path) -> Iterator[Path]:
        """
        Discover analyzable files in a directory tree.

        Should filter out:
        - Build directories (dist, build, node_modules)
        - Cache directories (__pycache__, .git)
        - Test files (if appropriate for the language)

        Args:
            root: Root directory to scan

        Returns:
            Iterator of file paths
        """
        ...


class AnalyzerRegistry:
    """
    Registry for language analyzers.

    Manages multiple analyzers and routes analysis requests
    to the appropriate one.

    Usage:
        registry = AnalyzerRegistry()
        registry.register("python", PythonAnalyzer())
        registry.register("typescript", TypeScriptAnalyzer())
        registry.register("go", GoAnalyzer())

        # Analyze a file
        module = registry.analyze_file(Path("main.go"))

        # Analyze source directly
        edges = registry.analyze_source("go", source, "main")

        # Discover all files
        for path in registry.discover(Path("./project"), language="python"):
            print(path)
    """

    def __init__(self) -> None:
        self._analyzers: dict[str, Analyzer] = {}

    def register(self, language: str, analyzer: Analyzer) -> None:
        """
        Register an analyzer for a language.

        Args:
            language: Language identifier (e.g., "python", "go")
            analyzer: Analyzer instance
        """
        self._analyzers[language] = analyzer

    def get(self, language: str) -> Analyzer | None:
        """Get analyzer by language name."""
        return self._analyzers.get(language)

    def get_for_path(self, path: Path) -> Analyzer | None:
        """Find analyzer that can handle the given path."""
        for analyzer in self._analyzers.values():
            if analyzer.can_analyze(path):
                return analyzer
        return None

    def analyze_file(self, path: Path) -> Module | None:
        """
        Analyze a file using the appropriate analyzer.

        Returns None if no analyzer can handle the file.
        """
        analyzer = self.get_for_path(path)
        if analyzer is None:
            return None
        return analyzer.analyze_file(path)

    def analyze_source(
        self, language: str, source: str, module_name: str = "unknown"
    ) -> list[DependencyEdge]:
        """
        Analyze source code using the specified language analyzer.

        Args:
            language: Language identifier
            source: Source code string
            module_name: Name for the module

        Returns:
            List of DependencyEdge, empty if language not registered
        """
        analyzer = self._analyzers.get(language)
        if analyzer is None:
            return []
        return analyzer.analyze_source(source, module_name)

    def discover(self, root: Path, language: str | None = None) -> Iterator[Path]:
        """
        Discover files using registered analyzers.

        Args:
            root: Root directory to scan
            language: If specified, only use that analyzer.
                      If None, discover files for all languages.

        Yields:
            File paths
        """
        if language is not None:
            analyzer = self._analyzers.get(language)
            if analyzer is not None:
                yield from analyzer.discover(root)
        else:
            # Discover for all registered analyzers
            seen: set[Path] = set()
            for analyzer in self._analyzers.values():
                for path in analyzer.discover(root):
                    if path not in seen:
                        seen.add(path)
                        yield path

    @property
    def languages(self) -> list[str]:
        """List of registered language names."""
        return list(self._analyzers.keys())


# ============================================================================
# Python Import Analysis
# ============================================================================


class PythonImportVisitor(ast.NodeVisitor):
    """AST visitor that extracts imports from Python code."""

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.imports: list[DependencyEdge] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Handle: import foo, bar"""
        for alias in node.names:
            self.imports.append(
                DependencyEdge(
                    source=self.module_name,
                    target=alias.name,
                    import_type="standard",
                    line_number=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Handle: from foo import bar"""
        if node.module:
            # Handle relative imports
            if node.level > 0:
                # Relative import - would need package context
                target = "." * node.level + (node.module or "")
            else:
                target = node.module

            self.imports.append(
                DependencyEdge(
                    source=self.module_name,
                    target=target,
                    import_type="from",
                    line_number=node.lineno,
                )
            )
        self.generic_visit(node)


def analyze_python_imports(
    source: str,
    module_name: str = "unknown",
) -> list[DependencyEdge]:
    """
    Extract imports from Python source code.

    Args:
        source: Python source code as string
        module_name: Name of the module being analyzed

    Returns:
        List of DependencyEdge objects
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    visitor = PythonImportVisitor(module_name)
    visitor.visit(tree)
    return visitor.imports


def analyze_python_file(path: Path) -> Module:
    """
    Analyze a single Python file.

    Returns a Module with imports and basic metrics.
    """
    module_name = path.stem
    if path.name == "__init__.py":
        module_name = path.parent.name

    try:
        source = path.read_text(encoding="utf-8")
    except Exception:
        return Module(name=module_name, path=path)

    # Count lines
    lines = source.splitlines()
    loc = len([l for l in lines if l.strip() and not l.strip().startswith("#")])

    # Extract imports
    imports = analyze_python_imports(source, module_name)

    # Extract exported symbols (basic: functions and classes at module level)
    exports: list[str] = []
    try:
        tree = ast.parse(source)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if not node.name.startswith("_"):
                    exports.append(node.name)
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):
                    exports.append(node.name)
    except SyntaxError:
        pass

    return Module(
        name=module_name,
        path=path,
        is_package=path.name == "__init__.py",
        lines_of_code=loc,
        imports=imports,
        exported_symbols=exports,
    )


# ============================================================================
# TypeScript Import Analysis
# ============================================================================

# Regex patterns for TypeScript imports
TS_IMPORT_STANDARD = re.compile(
    r"import\s+(?:\*\s+as\s+\w+|\{[^}]+\}|\w+)\s+from\s+['\"]([^'\"]+)['\"]"
)
TS_IMPORT_SIDE_EFFECT = re.compile(r"import\s+['\"]([^'\"]+)['\"]")
TS_IMPORT_TYPE = re.compile(r"import\s+type\s+(?:\{[^}]+\}|\w+)\s+from\s+['\"]([^'\"]+)['\"]")
TS_REQUIRE = re.compile(r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")


def analyze_typescript_imports(
    source: str,
    module_name: str = "unknown",
) -> list[DependencyEdge]:
    """
    Extract imports from TypeScript source code.

    Handles:
    - import { x } from 'module'
    - import * as x from 'module'
    - import x from 'module'
    - import 'module' (side effects)
    - import type { x } from 'module'
    - require('module')

    Args:
        source: TypeScript source code as string
        module_name: Name of the module being analyzed

    Returns:
        List of DependencyEdge objects
    """
    imports: list[DependencyEdge] = []
    lines = source.splitlines()

    for line_no, line in enumerate(lines, start=1):
        # Type-only imports
        for match in TS_IMPORT_TYPE.finditer(line):
            imports.append(
                DependencyEdge(
                    source=module_name,
                    target=match.group(1),
                    import_type="from",
                    line_number=line_no,
                    is_type_only=True,
                )
            )

        # Standard imports (not type-only)
        if "import type" not in line:
            for match in TS_IMPORT_STANDARD.finditer(line):
                imports.append(
                    DependencyEdge(
                        source=module_name,
                        target=match.group(1),
                        import_type="from",
                        line_number=line_no,
                    )
                )

        # Side-effect imports
        for match in TS_IMPORT_SIDE_EFFECT.finditer(line):
            # Avoid matching standard imports
            if "from" not in line:
                imports.append(
                    DependencyEdge(
                        source=module_name,
                        target=match.group(1),
                        import_type="standard",
                        line_number=line_no,
                    )
                )

        # require() calls
        for match in TS_REQUIRE.finditer(line):
            imports.append(
                DependencyEdge(
                    source=module_name,
                    target=match.group(1),
                    import_type="dynamic",
                    line_number=line_no,
                )
            )

    return imports


def analyze_typescript_file(path: Path) -> Module:
    """
    Analyze a single TypeScript file.

    Returns a Module with imports and basic metrics.
    """
    module_name = path.stem

    try:
        source = path.read_text(encoding="utf-8")
    except Exception:
        return Module(name=module_name, path=path)

    # Count lines (excluding comments and blanks)
    lines = source.splitlines()
    loc = len(
        [
            l
            for l in lines
            if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("/*")
        ]
    )

    # Extract imports
    imports = analyze_typescript_imports(source, module_name)

    # Extract exports (basic: export declarations)
    exports: list[str] = []
    export_pattern = re.compile(
        r"export\s+(?:default\s+)?(?:function|class|const|let|var|interface|type|enum)\s+(\w+)"
    )
    for match in export_pattern.finditer(source):
        exports.append(match.group(1))

    return Module(
        name=module_name,
        path=path,
        lines_of_code=loc,
        imports=imports,
        exported_symbols=exports,
    )


# ============================================================================
# Concrete Analyzer Implementations
# ============================================================================


class PythonAnalyzer:
    """
    Analyzer implementation for Python source files.

    Implements the Analyzer protocol for Python:
    - AST-based import parsing
    - __init__.py package detection
    - Function/class export extraction
    """

    def can_analyze(self, path: Path) -> bool:
        """Check if this analyzer can handle the file."""
        return path.suffix == ".py"

    def analyze_source(self, source: str, module_name: str = "unknown") -> list[DependencyEdge]:
        """Extract imports from Python source code."""
        return analyze_python_imports(source, module_name)

    def analyze_file(self, path: Path) -> Module:
        """Analyze a single Python file."""
        return analyze_python_file(path)

    def discover(self, root: Path) -> Iterator[Path]:
        """Discover Python files in directory tree."""
        return discover_python_modules(root)


class TypeScriptAnalyzer:
    """
    Analyzer implementation for TypeScript source files.

    Implements the Analyzer protocol for TypeScript:
    - Regex-based import parsing (ES6 imports, require())
    - Type-only import detection
    - Export declaration extraction
    """

    def can_analyze(self, path: Path) -> bool:
        """Check if this analyzer can handle the file."""
        return path.suffix in (".ts", ".tsx") and not path.name.endswith(".d.ts")

    def analyze_source(self, source: str, module_name: str = "unknown") -> list[DependencyEdge]:
        """Extract imports from TypeScript source code."""
        return analyze_typescript_imports(source, module_name)

    def analyze_file(self, path: Path) -> Module:
        """Analyze a single TypeScript file."""
        return analyze_typescript_file(path)

    def discover(self, root: Path) -> Iterator[Path]:
        """Discover TypeScript files in directory tree."""
        return discover_typescript_modules(root)


def create_default_registry() -> AnalyzerRegistry:
    """
    Create an AnalyzerRegistry with default language analyzers.

    Returns a registry with Python and TypeScript analyzers pre-registered.

    Usage:
        registry = create_default_registry()
        registry.register("go", GoAnalyzer())  # Add custom
    """
    registry = AnalyzerRegistry()
    registry.register("python", PythonAnalyzer())
    registry.register("typescript", TypeScriptAnalyzer())
    return registry


# Default registry instance (for convenience)
_default_registry: AnalyzerRegistry | None = None


def get_default_registry() -> AnalyzerRegistry:
    """Get or create the default analyzer registry."""
    global _default_registry
    if _default_registry is None:
        _default_registry = create_default_registry()
    return _default_registry


# ============================================================================
# Graph Building
# ============================================================================


def discover_python_modules(root: Path) -> Iterator[Path]:
    """Discover Python modules in a directory tree."""
    for path in root.rglob("*.py"):
        # Skip common non-source directories
        parts = path.parts
        if any(
            p in parts
            for p in [
                "__pycache__",
                ".venv",
                "venv",
                "node_modules",
                ".git",
                "dist",
                "build",
            ]
        ):
            continue
        yield path


def discover_typescript_modules(root: Path) -> Iterator[Path]:
    """Discover TypeScript modules in a directory tree."""
    for pattern in ["*.ts", "*.tsx"]:
        for path in root.rglob(pattern):
            parts = path.parts
            if any(p in parts for p in ["node_modules", ".git", "dist", "build", "__pycache__"]):
                continue
            # Skip declaration files
            if path.name.endswith(".d.ts"):
                continue
            yield path


def build_architecture_graph(
    root: Path,
    language: str = "python",
) -> ArchitectureGraph:
    """
    Build an architecture graph for a codebase.

    Args:
        root: Root directory of the codebase
        language: "python" or "typescript"

    Returns:
        ArchitectureGraph with modules and edges (deduplicated by source->target)
    """
    graph = ArchitectureGraph(root_path=root, language=language)

    # Track unique edges by (source, target) to avoid inflating coupling metrics
    # Multiple imports of the same target from the same source are counted once
    seen_edges: set[tuple[str, str]] = set()

    def add_unique_edges(module: Module) -> None:
        """Add module's imports as unique edges (deduplicated)."""
        for edge in module.imports:
            edge_key = (edge.source, edge.target)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                graph.edges.append(edge)

    # Discover and analyze modules
    if language == "python":
        for path in discover_python_modules(root):
            module = analyze_python_file(path)
            # Use relative path as module name
            try:
                rel_path = path.relative_to(root)
                module.name = str(rel_path.with_suffix("")).replace("/", ".")
            except ValueError:
                pass
            # Update source in imports to use normalized name
            for edge in module.imports:
                # Create new edge with correct source name (module.imports has old name)
                object.__setattr__(edge, "source", module.name)
            graph.modules[module.name] = module
            add_unique_edges(module)

    elif language == "typescript":
        for path in discover_typescript_modules(root):
            module = analyze_typescript_file(path)
            try:
                rel_path = path.relative_to(root)
                module.name = str(rel_path.with_suffix("")).replace("/", ".")
            except ValueError:
                pass
            # Update source in imports to use normalized name
            for edge in module.imports:
                object.__setattr__(edge, "source", module.name)
            graph.modules[module.name] = module
            add_unique_edges(module)

    # Compute health metrics for each module
    for name, module in graph.modules.items():
        # Coupling: normalized by max possible
        out_deps = len(graph.get_dependencies(name))
        in_deps = len(graph.get_dependents(name))
        max_deps = max(graph.module_count - 1, 1)
        coupling = min(1.0, (out_deps + in_deps) / (2 * max_deps))

        # Cohesion: exports / LOC ratio (simplified)
        loc = max(module.lines_of_code, 1)
        export_count = len(module.exported_symbols)
        # Higher exports/LOC = potentially lower cohesion
        cohesion = 1.0 - min(1.0, export_count / (loc / 20))

        # Complexity: LOC-based (simplified)
        complexity = min(1.0, loc / 500)  # 500+ LOC = max complexity

        # Instability
        instability = graph.compute_instability(name)

        module.health = ModuleHealth(
            name=name,
            coupling=coupling,
            cohesion=max(0.0, cohesion),
            complexity=complexity,
            instability=instability,
            # drift, churn, coverage need external data
        )

    return graph
