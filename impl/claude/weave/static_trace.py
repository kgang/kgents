"""
StaticCallGraph - AST-based call graph analysis without execution.

Part of the kgents trace architecture. Analyzes Python source code to build
a call graph showing which functions call which others.

Key features:
- Fast AST-based analysis (no execution required)
- Tracks method calls, nested functions, decorators
- Supports "ghost calls" for dynamic dispatch (inferred but uncertain)
- Returns DependencyGraph for caller/callee queries

Usage:
    graph = StaticCallGraph()
    graph.analyze("impl/claude/**/*.py")
    callers = graph.trace_callers("FluxAgent.start", depth=5)
"""

from __future__ import annotations

import ast
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from .dependency import DependencyGraph


@dataclass(frozen=True)
class CallSite:
    """A location where a function/method call occurs.

    Attributes:
        file: Path to the source file
        line: Line number (1-indexed)
        column: Column offset (0-indexed)
        caller: Fully qualified name of the calling function
        callee: Name of the called function (may be unqualified)
        is_dynamic: True if this is an inferred/uncertain call
    """

    file: Path
    line: int
    column: int
    caller: str
    callee: str
    is_dynamic: bool = False


@dataclass
class FunctionDef:
    """Information about a function/method definition.

    Attributes:
        name: Fully qualified name (e.g., "MyClass.my_method")
        file: Path to the source file
        line: Line number where defined
        is_method: True if defined inside a class
        is_async: True if async def
        is_class: True if this is a class definition (not a function)
    """

    name: str
    file: Path
    line: int
    is_method: bool = False
    is_async: bool = False
    is_class: bool = False


class CallVisitor(ast.NodeVisitor):
    """AST visitor that extracts function calls and definitions.

    Tracks current scope to build fully qualified names.
    """

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.calls: list[CallSite] = []
        self.definitions: list[FunctionDef] = []
        self._scope_stack: list[str] = []  # Current scope for qualified names
        self._in_class: bool = False

    @property
    def _current_scope(self) -> str:
        """Get current fully qualified scope name."""
        return ".".join(self._scope_stack) if self._scope_stack else "<module>"

    def _qualified_name(self, name: str) -> str:
        """Build fully qualified name from current scope."""
        if self._scope_stack:
            return f"{'.'.join(self._scope_stack)}.{name}"
        return name

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Record class definition and enter scope."""
        qualified_name = self._qualified_name(node.name)
        self.definitions.append(
            FunctionDef(
                name=qualified_name,
                file=self.file_path,
                line=node.lineno,
                is_method=False,
                is_async=False,
                is_class=True,
            )
        )

        old_in_class = self._in_class
        self._in_class = True
        self._scope_stack.append(node.name)
        self.generic_visit(node)
        self._scope_stack.pop()
        self._in_class = old_in_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Record function definition and enter scope."""
        qualified_name = self._qualified_name(node.name)
        self.definitions.append(
            FunctionDef(
                name=qualified_name,
                file=self.file_path,
                line=node.lineno,
                is_method=self._in_class,
                is_async=False,
            )
        )

        self._scope_stack.append(node.name)
        self.generic_visit(node)
        self._scope_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Record async function definition and enter scope."""
        qualified_name = self._qualified_name(node.name)
        self.definitions.append(
            FunctionDef(
                name=qualified_name,
                file=self.file_path,
                line=node.lineno,
                is_method=self._in_class,
                is_async=True,
            )
        )

        self._scope_stack.append(node.name)
        self.generic_visit(node)
        self._scope_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        """Record function call."""
        callee_name, is_dynamic = self._extract_callee(node.func)

        if callee_name:
            self.calls.append(
                CallSite(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    caller=self._current_scope,
                    callee=callee_name,
                    is_dynamic=is_dynamic,
                )
            )

        # Continue visiting arguments (may contain nested calls)
        self.generic_visit(node)

    def _extract_callee(self, node: ast.expr) -> tuple[str, bool]:
        """Extract callee name from call target.

        Returns:
            (callee_name, is_dynamic) tuple
        """
        if isinstance(node, ast.Name):
            # Simple call: foo()
            return node.id, False

        elif isinstance(node, ast.Attribute):
            # Method call: obj.method()
            # Try to get the full chain
            parts = self._extract_attribute_chain(node)
            if parts:
                return ".".join(parts), False
            # If chain extraction failed, just use the attribute name
            return node.attr, True

        elif isinstance(node, ast.Subscript):
            # Subscript call: items[0]()
            return "<subscript>", True

        elif isinstance(node, ast.Call):
            # Chained call: foo()()
            return "<chained>", True

        elif isinstance(node, ast.Lambda):
            # Lambda call: (lambda x: x)()
            return "<lambda>", True

        elif isinstance(node, ast.IfExp):
            # Conditional call: (a if cond else b)()
            return "<conditional>", True

        # Unknown pattern
        return "", True

    def _extract_attribute_chain(self, node: ast.Attribute) -> list[str]:
        """Extract attribute chain like a.b.c -> ['a', 'b', 'c']."""
        parts: list[str] = [node.attr]
        current = node.value

        while True:
            if isinstance(current, ast.Name):
                parts.append(current.id)
                break
            elif isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            else:
                # Chain broken by non-simple expression
                return []

        parts.reverse()
        return parts


class StaticCallGraph:
    """AST-based call graph for Python code.

    Analyzes Python source files to build a graph of function calls.
    Does not execute code - purely static analysis.

    Example:
        graph = StaticCallGraph()
        graph.analyze("impl/claude/**/*.py")

        # Who calls FluxAgent.start?
        callers = graph.trace_callers("FluxAgent.start", depth=5)

        # What does FluxAgent.start call?
        callees = graph.trace_callees("FluxAgent.start", depth=3)
    """

    def __init__(self, base_path: str | Path = ".") -> None:
        """Initialize call graph analyzer.

        Args:
            base_path: Base directory for relative patterns
        """
        self.base_path = Path(base_path).resolve()

        # All call sites found
        self._call_sites: list[CallSite] = []

        # All function definitions found
        self._definitions: dict[str, FunctionDef] = {}

        # caller -> set of callees
        self._calls: dict[str, set[str]] = {}

        # callee -> set of callers (reverse index)
        self._called_by: dict[str, set[str]] = {}

        # Files analyzed
        self._analyzed_files: set[Path] = set()

        # Caches (invalidated on analyze)
        self._transitive_callers: dict[str, set[str]] | None = None
        self._transitive_callees: dict[str, set[str]] | None = None

    def analyze(self, pattern: str = "**/*.py") -> None:
        """Analyze Python files matching pattern.

        Args:
            pattern: Glob pattern for files to analyze (relative to base_path)
        """
        # Invalidate caches
        self._transitive_callers = None
        self._transitive_callees = None

        files = list(self.base_path.glob(pattern))

        for file_path in files:
            if file_path in self._analyzed_files:
                continue
            self._analyze_file(file_path)

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file."""
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError):
            # Skip files that can't be parsed
            return

        visitor = CallVisitor(file_path)
        visitor.visit(tree)

        # Record definitions
        for func_def in visitor.definitions:
            self._definitions[func_def.name] = func_def

        # Record call sites and build graph
        for call_site in visitor.calls:
            self._call_sites.append(call_site)

            caller = call_site.caller
            callee = call_site.callee

            # Skip module-level calls for now (caller is <module>)
            if caller == "<module>":
                continue

            # Add to forward index
            if caller not in self._calls:
                self._calls[caller] = set()
            self._calls[caller].add(callee)

            # Add to reverse index
            if callee not in self._called_by:
                self._called_by[callee] = set()
            self._called_by[callee].add(caller)

        self._analyzed_files.add(file_path)

    def trace_callers(self, target: str, depth: int = 5) -> DependencyGraph:
        """Find all functions that call target (directly or transitively).

        Returns a DependencyGraph where edges point from caller to callee.

        Args:
            target: Function name to trace (supports partial matching)
            depth: Maximum depth to traverse

        Returns:
            DependencyGraph of caller relationships
        """
        graph = DependencyGraph()
        visited: set[str] = set()

        # Find matching targets
        targets = self._match_function(target)
        if not targets:
            return graph

        # BFS from each target
        for t in targets:
            self._trace_callers_bfs(t, depth, graph, visited)

        return graph

    def _trace_callers_bfs(
        self,
        target: str,
        depth: int,
        graph: DependencyGraph,
        visited: set[str],
    ) -> None:
        """BFS to find callers up to depth."""
        queue: deque[tuple[str, int]] = deque([(target, 0)])

        # Add root node
        if target not in visited:
            graph.add_node(target)
            visited.add(target)

        while queue:
            current, current_depth = queue.popleft()

            if current_depth >= depth:
                continue

            # Find all callers of current
            callers = self._called_by.get(current, set())

            # Also check partial matches for method calls
            for callee in self._called_by:
                if callee.endswith(f".{current}") or current.endswith(f".{callee}"):
                    callers = callers | self._called_by.get(callee, set())

            for caller in callers:
                # Add caller node with dependency on current
                if caller not in visited:
                    graph.add_node(caller, depends_on={current})
                    visited.add(caller)
                    queue.append((caller, current_depth + 1))
                elif current in graph:
                    # Just add the dependency edge
                    existing_deps = graph.get_dependencies(caller)
                    if current not in existing_deps:
                        # Can't modify existing, just note it
                        pass

    def trace_callees(self, target: str, depth: int = 5) -> DependencyGraph:
        """Find all functions that target calls (directly or transitively).

        Returns a DependencyGraph where edges point from caller to callee.

        Args:
            target: Function name to trace (supports partial matching)
            depth: Maximum depth to traverse

        Returns:
            DependencyGraph of callee relationships
        """
        graph = DependencyGraph()
        visited: set[str] = set()

        # Find matching targets
        targets = self._match_function(target)
        if not targets:
            return graph

        # BFS from each target
        for t in targets:
            self._trace_callees_bfs(t, depth, graph, visited)

        return graph

    def _trace_callees_bfs(
        self,
        target: str,
        depth: int,
        graph: DependencyGraph,
        visited: set[str],
    ) -> None:
        """BFS to find callees up to depth."""
        queue: deque[tuple[str, int]] = deque([(target, 0)])

        # Add root node
        if target not in visited:
            graph.add_node(target)
            visited.add(target)

        while queue:
            current, current_depth = queue.popleft()

            if current_depth >= depth:
                continue

            # Find all functions called by current
            callees = self._calls.get(current, set())

            for callee in callees:
                # Add callee with current depending on it
                if callee not in visited:
                    graph.add_node(callee)
                    visited.add(callee)
                    queue.append((callee, current_depth + 1))

                # Add dependency from current to callee
                try:
                    deps = graph.get_dependencies(current)
                    if callee not in deps:
                        # Need to re-add with new dependency
                        new_deps = deps | {callee}
                        graph._dependencies[current] = new_deps
                        graph._transitive_closure = None
                except KeyError:
                    pass

    def get_ghost_calls(self, target: str) -> list[CallSite]:
        """Get inferred/dynamic calls related to target.

        Ghost calls are calls that can't be statically resolved with
        certainty - like method calls on variables whose type is unknown.

        Args:
            target: Function name to find ghost calls for

        Returns:
            List of CallSite objects marked as dynamic
        """
        ghosts: list[CallSite] = []

        for call_site in self._call_sites:
            if not call_site.is_dynamic:
                continue

            # Check if this ghost call might be related to target
            if target in call_site.callee or call_site.callee in target:
                ghosts.append(call_site)
            elif target.split(".")[-1] == call_site.callee.split(".")[-1]:
                # Method name matches
                ghosts.append(call_site)

        return ghosts

    def _match_function(self, pattern: str) -> list[str]:
        """Find function names matching pattern.

        Supports:
        - Exact match: "MyClass.my_method"
        - Partial match: "my_method" matches "MyClass.my_method"
        - Suffix match: ".my_method"
        """
        matches: list[str] = []

        # Check definitions
        for name in self._definitions:
            if self._name_matches(name, pattern):
                matches.append(name)

        # Also check call graph keys (may include unresolved names)
        for name in self._calls:
            if name not in matches and self._name_matches(name, pattern):
                matches.append(name)

        for name in self._called_by:
            if name not in matches and self._name_matches(name, pattern):
                matches.append(name)

        return matches

    def _name_matches(self, name: str, pattern: str) -> bool:
        """Check if name matches pattern."""
        if name == pattern:
            return True
        if name.endswith(f".{pattern}"):
            return True
        if pattern.startswith(".") and name.endswith(pattern):
            return True
        # Partial match on last component
        name_parts = name.split(".")
        pattern_parts = pattern.split(".")
        if name_parts[-1] == pattern_parts[-1]:
            return True
        return False

    def get_definition(self, name: str) -> FunctionDef | None:
        """Get function definition by name."""
        # Try exact match first
        if name in self._definitions:
            return self._definitions[name]

        # Try partial match
        matches = self._match_function(name)
        for match in matches:
            if match in self._definitions:
                return self._definitions[match]

        return None

    def get_call_sites(
        self, caller: str | None = None, callee: str | None = None
    ) -> list[CallSite]:
        """Get call sites, optionally filtered.

        Args:
            caller: Filter by caller name (partial match)
            callee: Filter by callee name (partial match)

        Returns:
            List of matching CallSite objects
        """
        results: list[CallSite] = []

        for call_site in self._call_sites:
            if caller and not self._name_matches(call_site.caller, caller):
                continue
            if callee and not self._name_matches(call_site.callee, callee):
                continue
            results.append(call_site)

        return results

    def definitions(self) -> Iterator[FunctionDef]:
        """Iterate over all function definitions."""
        yield from self._definitions.values()

    def callers_of(self, target: str) -> set[str]:
        """Get direct callers of target."""
        result: set[str] = set()
        matches = self._match_function(target)
        for match in matches:
            result.update(self._called_by.get(match, set()))
        return result

    def callees_of(self, target: str) -> set[str]:
        """Get direct callees of target."""
        result: set[str] = set()
        matches = self._match_function(target)
        for match in matches:
            result.update(self._calls.get(match, set()))
        return result

    @property
    def num_files(self) -> int:
        """Number of files analyzed."""
        return len(self._analyzed_files)

    @property
    def num_definitions(self) -> int:
        """Number of function definitions found."""
        return len(self._definitions)

    @property
    def num_calls(self) -> int:
        """Number of call sites found."""
        return len(self._call_sites)

    def __len__(self) -> int:
        """Number of nodes in call graph."""
        all_nodes = set(self._calls.keys()) | set(self._called_by.keys())
        return len(all_nodes)

    def __contains__(self, name: str) -> bool:
        """Check if function is in call graph."""
        return bool(self._match_function(name))
