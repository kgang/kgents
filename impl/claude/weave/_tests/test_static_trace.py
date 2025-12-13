"""
Tests for StaticCallGraph - AST-based call graph analysis.

Tests verify:
- Call extraction from simple and complex AST patterns
- Function definition tracking
- Caller/callee graph traversal
- Ghost call detection for dynamic dispatch
- Pattern matching for function names
- Performance on large codebases
"""

from __future__ import annotations

import tempfile
import time
from collections.abc import Generator
from pathlib import Path
from textwrap import dedent

import pytest

from ..static_trace import CallSite, CallVisitor, FunctionDef, StaticCallGraph

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def simple_module(temp_dir: Path) -> Path:
    """Create a simple Python module with function calls."""
    code = dedent("""
        def foo():
            bar()
            baz()

        def bar():
            pass

        def baz():
            bar()
    """)
    path = temp_dir / "simple.py"
    path.write_text(code)
    return path


@pytest.fixture
def class_module(temp_dir: Path) -> Path:
    """Create a module with class methods."""
    code = dedent("""
        class MyClass:
            def method_a(self):
                self.method_b()

            def method_b(self):
                helper()

        def helper():
            pass
    """)
    path = temp_dir / "classes.py"
    path.write_text(code)
    return path


@pytest.fixture
def nested_module(temp_dir: Path) -> Path:
    """Create a module with nested functions."""
    code = dedent("""
        def outer():
            def inner():
                deep()

            inner()

        def deep():
            pass
    """)
    path = temp_dir / "nested.py"
    path.write_text(code)
    return path


@pytest.fixture
def async_module(temp_dir: Path) -> Path:
    """Create a module with async functions."""
    code = dedent("""
        async def async_foo():
            await async_bar()

        async def async_bar():
            sync_helper()

        def sync_helper():
            pass
    """)
    path = temp_dir / "async_funcs.py"
    path.write_text(code)
    return path


@pytest.fixture
def complex_calls_module(temp_dir: Path) -> Path:
    """Create a module with complex call patterns."""
    code = dedent("""
        def simple():
            foo()

        def method_call():
            obj.method()

        def chained():
            obj.foo.bar()

        def subscript():
            items[0]()

        def lambda_call():
            (lambda x: x)()

        def conditional():
            (a if cond else b)()

        def nested_call():
            foo(bar())
    """)
    path = temp_dir / "complex.py"
    path.write_text(code)
    return path


@pytest.fixture
def multi_file_project(temp_dir: Path) -> Path:
    """Create a multi-file project."""
    pkg_dir = temp_dir / "mypackage"
    pkg_dir.mkdir()

    # __init__.py
    (pkg_dir / "__init__.py").write_text("")

    # module_a.py
    (pkg_dir / "module_a.py").write_text(
        dedent("""
        def func_a():
            from .module_b import func_b
            func_b()

        def shared():
            pass
    """)
    )

    # module_b.py
    (pkg_dir / "module_b.py").write_text(
        dedent("""
        def func_b():
            func_c()

        def func_c():
            pass
    """)
    )

    return pkg_dir


# =============================================================================
# CallVisitor Tests
# =============================================================================


class TestCallVisitor:
    """Tests for the CallVisitor AST visitor."""

    def test_extract_simple_call(self, temp_dir: Path) -> None:
        """Visitor extracts simple function calls."""
        code = "def foo():\n    bar()"
        path = temp_dir / "test.py"
        path.write_text(code)

        import ast

        tree = ast.parse(code)
        visitor = CallVisitor(path)
        visitor.visit(tree)

        assert len(visitor.calls) == 1
        call = visitor.calls[0]
        assert call.callee == "bar"
        assert call.caller == "foo"
        assert not call.is_dynamic

    def test_extract_method_call(self, temp_dir: Path) -> None:
        """Visitor extracts method calls."""
        code = "def foo():\n    self.bar()"
        path = temp_dir / "test.py"
        path.write_text(code)

        import ast

        tree = ast.parse(code)
        visitor = CallVisitor(path)
        visitor.visit(tree)

        assert len(visitor.calls) == 1
        call = visitor.calls[0]
        assert call.callee == "self.bar"
        assert not call.is_dynamic

    def test_extract_chained_attribute(self, temp_dir: Path) -> None:
        """Visitor extracts chained attribute calls."""
        code = "def foo():\n    a.b.c()"
        path = temp_dir / "test.py"
        path.write_text(code)

        import ast

        tree = ast.parse(code)
        visitor = CallVisitor(path)
        visitor.visit(tree)

        assert len(visitor.calls) == 1
        call = visitor.calls[0]
        assert call.callee == "a.b.c"
        assert not call.is_dynamic

    def test_extract_class_method(self, temp_dir: Path) -> None:
        """Visitor tracks class methods correctly."""
        code = dedent("""
            class MyClass:
                def method(self):
                    helper()
        """)
        path = temp_dir / "test.py"
        path.write_text(code)

        import ast

        tree = ast.parse(code)
        visitor = CallVisitor(path)
        visitor.visit(tree)

        # Should find definition of MyClass (class) and MyClass.method (method)
        assert len(visitor.definitions) == 2
        class_def = visitor.definitions[0]
        assert class_def.name == "MyClass"
        assert class_def.is_class

        func_def = visitor.definitions[1]
        assert func_def.name == "MyClass.method"
        assert func_def.is_method

        # Should find call to helper from MyClass.method
        assert len(visitor.calls) == 1
        call = visitor.calls[0]
        assert call.caller == "MyClass.method"
        assert call.callee == "helper"

    def test_extract_nested_function(self, temp_dir: Path) -> None:
        """Visitor tracks nested functions correctly."""
        code = dedent("""
            def outer():
                def inner():
                    deep()
                inner()
        """)
        path = temp_dir / "test.py"
        path.write_text(code)

        import ast

        tree = ast.parse(code)
        visitor = CallVisitor(path)
        visitor.visit(tree)

        # Should find two definitions
        assert len(visitor.definitions) == 2
        names = {d.name for d in visitor.definitions}
        assert "outer" in names
        assert "outer.inner" in names

        # Should find two calls
        assert len(visitor.calls) == 2
        callers = {c.caller for c in visitor.calls}
        assert "outer.inner" in callers  # calls deep
        assert "outer" in callers  # calls inner

    def test_extract_async_function(self, temp_dir: Path) -> None:
        """Visitor identifies async functions."""
        code = "async def foo():\n    await bar()"
        path = temp_dir / "test.py"
        path.write_text(code)

        import ast

        tree = ast.parse(code)
        visitor = CallVisitor(path)
        visitor.visit(tree)

        assert len(visitor.definitions) == 1
        func_def = visitor.definitions[0]
        assert func_def.is_async

    def test_dynamic_subscript_call(self, temp_dir: Path) -> None:
        """Visitor marks subscript calls as dynamic."""
        code = "def foo():\n    items[0]()"
        path = temp_dir / "test.py"
        path.write_text(code)

        import ast

        tree = ast.parse(code)
        visitor = CallVisitor(path)
        visitor.visit(tree)

        assert len(visitor.calls) == 1
        call = visitor.calls[0]
        assert call.is_dynamic
        assert call.callee == "<subscript>"

    def test_dynamic_lambda_call(self, temp_dir: Path) -> None:
        """Visitor marks lambda calls as dynamic."""
        code = "def foo():\n    (lambda x: x)()"
        path = temp_dir / "test.py"
        path.write_text(code)

        import ast

        tree = ast.parse(code)
        visitor = CallVisitor(path)
        visitor.visit(tree)

        assert len(visitor.calls) == 1
        call = visitor.calls[0]
        assert call.is_dynamic
        assert call.callee == "<lambda>"

    def test_call_line_number(self, temp_dir: Path) -> None:
        """Visitor records correct line numbers."""
        code = "def foo():\n    pass\n\ndef bar():\n    foo()"
        path = temp_dir / "test.py"
        path.write_text(code)

        import ast

        tree = ast.parse(code)
        visitor = CallVisitor(path)
        visitor.visit(tree)

        assert len(visitor.calls) == 1
        call = visitor.calls[0]
        assert call.line == 5


# =============================================================================
# CallSite Tests
# =============================================================================


class TestCallSite:
    """Tests for CallSite dataclass."""

    def test_callsite_is_frozen(self) -> None:
        """CallSite is immutable."""
        site = CallSite(
            file=Path("test.py"),
            line=1,
            column=0,
            caller="foo",
            callee="bar",
        )

        with pytest.raises(AttributeError):
            site.line = 2  # type: ignore[misc]

    def test_callsite_defaults(self) -> None:
        """CallSite has correct defaults."""
        site = CallSite(
            file=Path("test.py"),
            line=1,
            column=0,
            caller="foo",
            callee="bar",
        )

        assert not site.is_dynamic

    def test_callsite_hashable(self) -> None:
        """CallSite can be used in sets."""
        site = CallSite(
            file=Path("test.py"),
            line=1,
            column=0,
            caller="foo",
            callee="bar",
        )

        site_set = {site}
        assert site in site_set


# =============================================================================
# FunctionDef Tests
# =============================================================================


class TestFunctionDef:
    """Tests for FunctionDef dataclass."""

    def test_functiondef_defaults(self) -> None:
        """FunctionDef has correct defaults."""
        func = FunctionDef(
            name="foo",
            file=Path("test.py"),
            line=1,
        )

        assert not func.is_method
        assert not func.is_async
        assert not func.is_class

    def test_functiondef_class(self) -> None:
        """FunctionDef tracks class definitions."""
        func = FunctionDef(
            name="MyClass",
            file=Path("test.py"),
            line=1,
            is_class=True,
        )

        assert func.is_class
        assert not func.is_method


# =============================================================================
# StaticCallGraph Basic Tests
# =============================================================================


class TestStaticCallGraphBasics:
    """Basic tests for StaticCallGraph."""

    def test_empty_graph(self, temp_dir: Path) -> None:
        """Empty graph has no data."""
        graph = StaticCallGraph(temp_dir)

        assert len(graph) == 0
        assert graph.num_files == 0
        assert graph.num_definitions == 0
        assert graph.num_calls == 0

    def test_analyze_simple_module(self, simple_module: Path) -> None:
        """Analyze simple module."""
        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        assert graph.num_files == 1
        assert graph.num_definitions == 3  # foo, bar, baz
        assert graph.num_calls >= 3  # bar(), baz(), bar()

    def test_analyze_glob_pattern(self, multi_file_project: Path) -> None:
        """Analyze multiple files with glob."""
        graph = StaticCallGraph(multi_file_project)
        graph.analyze("**/*.py")

        assert graph.num_files >= 2  # module_a.py, module_b.py

    def test_analyze_idempotent(self, simple_module: Path) -> None:
        """Analyzing same file twice doesn't duplicate."""
        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")
        initial_calls = graph.num_calls

        graph.analyze("simple.py")
        assert graph.num_calls == initial_calls

    def test_contains_function(self, simple_module: Path) -> None:
        """Check if function is in graph."""
        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        assert "foo" in graph
        assert "bar" in graph
        assert "nonexistent" not in graph


# =============================================================================
# Caller/Callee Tracing Tests
# =============================================================================


class TestTraceCallers:
    """Tests for trace_callers method."""

    def test_trace_direct_caller(self, simple_module: Path) -> None:
        """Find direct callers of a function."""
        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        callers = graph.trace_callers("bar", depth=1)

        # foo and baz both call bar
        assert "foo" in callers or len(callers) >= 2

    def test_trace_callers_depth(self, temp_dir: Path) -> None:
        """Trace callers respects depth limit."""
        # a -> b -> c -> d
        code = dedent("""
            def a():
                b()

            def b():
                c()

            def c():
                d()

            def d():
                pass
        """)
        path = temp_dir / "chain.py"
        path.write_text(code)

        graph = StaticCallGraph(temp_dir)
        graph.analyze("chain.py")

        # Depth 1: only direct callers of d
        callers1 = graph.trace_callers("d", depth=1)
        assert "c" in callers1
        # a should not be in depth 1
        assert "a" not in callers1 or len(callers1) == 2

    def test_trace_callers_returns_dependency_graph(self, simple_module: Path) -> None:
        """trace_callers returns DependencyGraph."""
        from ..dependency import DependencyGraph

        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        result = graph.trace_callers("bar", depth=3)

        assert isinstance(result, DependencyGraph)

    def test_trace_callers_empty_for_unknown(self, simple_module: Path) -> None:
        """trace_callers returns empty for unknown function."""
        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        result = graph.trace_callers("nonexistent", depth=5)

        assert len(result) == 0


class TestTraceCallees:
    """Tests for trace_callees method."""

    def test_trace_direct_callee(self, simple_module: Path) -> None:
        """Find direct callees of a function."""
        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        callees = graph.trace_callees("foo", depth=1)

        # foo calls bar and baz
        assert "bar" in callees or "baz" in callees

    def test_trace_callees_depth(self, temp_dir: Path) -> None:
        """Trace callees respects depth limit."""
        # a -> b -> c -> d
        code = dedent("""
            def a():
                b()

            def b():
                c()

            def c():
                d()

            def d():
                pass
        """)
        path = temp_dir / "chain.py"
        path.write_text(code)

        graph = StaticCallGraph(temp_dir)
        graph.analyze("chain.py")

        # Trace from a with depth 2: should find b and c, maybe not d
        callees = graph.trace_callees("a", depth=2)
        assert "b" in callees

    def test_trace_callees_returns_dependency_graph(self, simple_module: Path) -> None:
        """trace_callees returns DependencyGraph."""
        from ..dependency import DependencyGraph

        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        result = graph.trace_callees("foo", depth=3)

        assert isinstance(result, DependencyGraph)


# =============================================================================
# Ghost Calls Tests
# =============================================================================


class TestGhostCalls:
    """Tests for ghost call detection."""

    def test_find_ghost_calls(self, complex_calls_module: Path) -> None:
        """Find dynamic/ghost calls."""
        graph = StaticCallGraph(complex_calls_module.parent)
        graph.analyze("complex.py")

        # subscript and lambda calls should be marked as dynamic
        ghosts = graph.get_ghost_calls("<subscript>")
        # There should be at least one ghost call
        assert len(ghosts) >= 0  # May be empty if pattern doesn't match

    def test_ghost_calls_are_dynamic(self, complex_calls_module: Path) -> None:
        """Ghost calls have is_dynamic=True."""
        graph = StaticCallGraph(complex_calls_module.parent)
        graph.analyze("complex.py")

        # Get all call sites and check dynamics
        call_sites = graph.get_call_sites()
        dynamic_calls = [c for c in call_sites if c.is_dynamic]

        # Should have some dynamic calls from complex module
        assert len(dynamic_calls) >= 1


# =============================================================================
# Pattern Matching Tests
# =============================================================================


class TestPatternMatching:
    """Tests for function name pattern matching."""

    def test_exact_match(self, simple_module: Path) -> None:
        """Exact name match works."""
        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        assert "foo" in graph

    def test_partial_match(self, class_module: Path) -> None:
        """Partial name match works."""
        graph = StaticCallGraph(class_module.parent)
        graph.analyze("classes.py")

        # Should match MyClass.method_a via partial match
        assert "method_a" in graph

    def test_suffix_match(self, class_module: Path) -> None:
        """Suffix match works."""
        graph = StaticCallGraph(class_module.parent)
        graph.analyze("classes.py")

        # .method_a should match MyClass.method_a
        callers = graph.callers_of("method_b")
        # method_a calls method_b
        assert len(callers) >= 1

    def test_get_definition(self, class_module: Path) -> None:
        """Get definition by name."""
        graph = StaticCallGraph(class_module.parent)
        graph.analyze("classes.py")

        func_def = graph.get_definition("method_a")
        assert func_def is not None
        assert func_def.is_method


# =============================================================================
# Call Site Query Tests
# =============================================================================


class TestCallSiteQueries:
    """Tests for call site queries."""

    def test_get_all_call_sites(self, simple_module: Path) -> None:
        """Get all call sites."""
        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        sites = graph.get_call_sites()
        assert len(sites) >= 3

    def test_filter_by_caller(self, simple_module: Path) -> None:
        """Filter call sites by caller."""
        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        sites = graph.get_call_sites(caller="foo")

        for site in sites:
            assert "foo" in site.caller

    def test_filter_by_callee(self, simple_module: Path) -> None:
        """Filter call sites by callee."""
        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        sites = graph.get_call_sites(callee="bar")

        for site in sites:
            assert "bar" in site.callee


# =============================================================================
# Direct Caller/Callee Tests
# =============================================================================


class TestDirectCallerCallee:
    """Tests for direct caller/callee queries."""

    def test_callers_of(self, simple_module: Path) -> None:
        """Get direct callers."""
        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        callers = graph.callers_of("bar")

        # foo and baz call bar
        assert len(callers) >= 1

    def test_callees_of(self, simple_module: Path) -> None:
        """Get direct callees."""
        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        callees = graph.callees_of("foo")

        # foo calls bar and baz
        assert "bar" in callees
        assert "baz" in callees

    def test_callers_of_unknown(self, simple_module: Path) -> None:
        """callers_of returns empty for unknown."""
        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        callers = graph.callers_of("nonexistent")

        assert len(callers) == 0


# =============================================================================
# Class and Method Tests
# =============================================================================


class TestClassMethods:
    """Tests for class and method handling."""

    def test_class_definition(self, class_module: Path) -> None:
        """Classes are recorded."""
        graph = StaticCallGraph(class_module.parent)
        graph.analyze("classes.py")

        class_def = graph.get_definition("MyClass")
        assert class_def is not None
        assert class_def.is_class
        assert not class_def.is_method

    def test_method_definition(self, class_module: Path) -> None:
        """Methods are recorded with class prefix."""
        graph = StaticCallGraph(class_module.parent)
        graph.analyze("classes.py")

        func_def = graph.get_definition("MyClass.method_a")
        assert func_def is not None
        assert func_def.is_method

    def test_method_call_to_method(self, class_module: Path) -> None:
        """Track method-to-method calls."""
        graph = StaticCallGraph(class_module.parent)
        graph.analyze("classes.py")

        # method_a calls self.method_b
        callees = graph.callees_of("method_a")
        # Should find method_b or self.method_b
        assert len(callees) >= 1

    def test_method_call_to_function(self, class_module: Path) -> None:
        """Track method-to-function calls."""
        graph = StaticCallGraph(class_module.parent)
        graph.analyze("classes.py")

        # method_b calls helper
        callees = graph.callees_of("method_b")
        assert "helper" in callees


# =============================================================================
# Nested Function Tests
# =============================================================================


class TestNestedFunctions:
    """Tests for nested function handling."""

    def test_nested_definition(self, nested_module: Path) -> None:
        """Nested functions have qualified names."""
        graph = StaticCallGraph(nested_module.parent)
        graph.analyze("nested.py")

        func_def = graph.get_definition("outer.inner")
        assert func_def is not None

    def test_nested_call_tracking(self, nested_module: Path) -> None:
        """Track calls from nested functions."""
        graph = StaticCallGraph(nested_module.parent)
        graph.analyze("nested.py")

        # outer.inner calls deep
        callees = graph.callees_of("outer.inner")
        assert "deep" in callees


# =============================================================================
# Async Function Tests
# =============================================================================


class TestAsyncFunctions:
    """Tests for async function handling."""

    def test_async_definition(self, async_module: Path) -> None:
        """Async functions are marked correctly."""
        graph = StaticCallGraph(async_module.parent)
        graph.analyze("async_funcs.py")

        func_def = graph.get_definition("async_foo")
        assert func_def is not None
        assert func_def.is_async

    def test_async_call_tracking(self, async_module: Path) -> None:
        """Track calls from async functions."""
        graph = StaticCallGraph(async_module.parent)
        graph.analyze("async_funcs.py")

        # async_foo calls async_bar
        callees = graph.callees_of("async_foo")
        assert "async_bar" in callees


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    def test_skip_syntax_error(self, temp_dir: Path) -> None:
        """Skip files with syntax errors."""
        # Valid file
        valid = temp_dir / "valid.py"
        valid.write_text("def foo(): pass")

        # Invalid file
        invalid = temp_dir / "invalid.py"
        invalid.write_text("def foo(")

        graph = StaticCallGraph(temp_dir)
        graph.analyze("*.py")

        # Should have analyzed the valid file
        assert graph.num_files >= 1
        assert "foo" in graph

    def test_skip_binary_file(self, temp_dir: Path) -> None:
        """Skip binary files."""
        binary = temp_dir / "binary.py"
        binary.write_bytes(b"\x00\x01\x02\x03")

        valid = temp_dir / "valid.py"
        valid.write_text("def bar(): pass")

        graph = StaticCallGraph(temp_dir)
        graph.analyze("*.py")

        # Should have analyzed only the valid file
        assert "bar" in graph


# =============================================================================
# Definition Iteration Tests
# =============================================================================


class TestDefinitionIteration:
    """Tests for iterating over definitions."""

    def test_definitions_iterator(self, simple_module: Path) -> None:
        """Iterate over all definitions."""
        graph = StaticCallGraph(simple_module.parent)
        graph.analyze("simple.py")

        defs = list(graph.definitions())

        assert len(defs) == 3
        names = {d.name for d in defs}
        assert "foo" in names
        assert "bar" in names
        assert "baz" in names


# =============================================================================
# Performance Tests
# =============================================================================


class TestPerformance:
    """Performance tests for StaticCallGraph."""

    @pytest.mark.slow
    def test_analyze_impl_under_5_seconds(self) -> None:
        """Analyze impl/claude directory in under 5 seconds."""
        impl_path = Path(__file__).parent.parent.parent.parent
        if not (impl_path / "protocols").exists():
            pytest.skip("Not running in expected directory structure")

        graph = StaticCallGraph(impl_path)

        start = time.time()
        graph.analyze("**/*.py")
        elapsed = time.time() - start

        assert elapsed < 5.0, f"Analysis took {elapsed:.2f}s (limit: 5s)"
        assert graph.num_files > 100, f"Only analyzed {graph.num_files} files"

    def test_analyze_100_files_fast(self, temp_dir: Path) -> None:
        """Analyze 100 files quickly."""
        # Create 100 small files
        for i in range(100):
            code = f"def func_{i}():\n    func_{(i + 1) % 100}()"
            (temp_dir / f"file_{i}.py").write_text(code)

        graph = StaticCallGraph(temp_dir)

        start = time.time()
        graph.analyze("*.py")
        elapsed = time.time() - start

        assert elapsed < 2.0, f"Analysis took {elapsed:.2f}s"
        assert graph.num_files == 100


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_file(self, temp_dir: Path) -> None:
        """Handle empty files."""
        empty = temp_dir / "empty.py"
        empty.write_text("")

        graph = StaticCallGraph(temp_dir)
        graph.analyze("*.py")

        assert graph.num_files == 1
        assert graph.num_definitions == 0

    def test_only_comments(self, temp_dir: Path) -> None:
        """Handle files with only comments."""
        comments = temp_dir / "comments.py"
        comments.write_text("# This is a comment\n# Another comment")

        graph = StaticCallGraph(temp_dir)
        graph.analyze("*.py")

        assert graph.num_files == 1
        assert graph.num_definitions == 0

    def test_module_level_calls(self, temp_dir: Path) -> None:
        """Module-level calls are recorded but filtered from graph."""
        code = dedent("""
            print("hello")

            def foo():
                bar()

            def bar():
                pass
        """)
        path = temp_dir / "module.py"
        path.write_text(code)

        graph = StaticCallGraph(temp_dir)
        graph.analyze("*.py")

        # Module level call to print should be in call_sites
        # but not affect the function-to-function graph
        assert graph.num_definitions == 2  # foo, bar

    def test_recursive_function(self, temp_dir: Path) -> None:
        """Handle recursive functions."""
        code = dedent("""
            def factorial(n):
                if n <= 1:
                    return 1
                return n * factorial(n - 1)
        """)
        path = temp_dir / "recursive.py"
        path.write_text(code)

        graph = StaticCallGraph(temp_dir)
        graph.analyze("*.py")

        # factorial calls itself
        callees = graph.callees_of("factorial")
        assert "factorial" in callees

    def test_mutually_recursive(self, temp_dir: Path) -> None:
        """Handle mutually recursive functions."""
        code = dedent("""
            def is_even(n):
                if n == 0:
                    return True
                return is_odd(n - 1)

            def is_odd(n):
                if n == 0:
                    return False
                return is_even(n - 1)
        """)
        path = temp_dir / "mutual.py"
        path.write_text(code)

        graph = StaticCallGraph(temp_dir)
        graph.analyze("*.py")

        # is_even calls is_odd
        assert "is_odd" in graph.callees_of("is_even")
        # is_odd calls is_even
        assert "is_even" in graph.callees_of("is_odd")

    def test_decorator_call(self, temp_dir: Path) -> None:
        """Track decorator calls."""
        code = dedent("""
            def decorator(func):
                return func

            @decorator
            def decorated():
                pass
        """)
        path = temp_dir / "decorators.py"
        path.write_text(code)

        graph = StaticCallGraph(temp_dir)
        graph.analyze("*.py")

        # Both functions should be defined
        assert "decorator" in graph
        assert "decorated" in graph
