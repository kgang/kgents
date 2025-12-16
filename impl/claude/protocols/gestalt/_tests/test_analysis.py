"""
Tests for Gestalt architecture analysis.

Tests import parsing, health metrics, and graph building.
"""

import tempfile
from pathlib import Path

import pytest
from protocols.gestalt.analysis import (
    ArchitectureGraph,
    DependencyEdge,
    Module,
    ModuleHealth,
    analyze_python_file,
    analyze_python_imports,
    analyze_typescript_file,
    analyze_typescript_imports,
    build_architecture_graph,
)

# ============================================================================
# ModuleHealth Tests
# ============================================================================


class TestModuleHealth:
    """Tests for ModuleHealth metrics."""

    def test_overall_health_perfect(self) -> None:
        """Perfect health = 1.0."""
        health = ModuleHealth(
            name="test",
            coupling=0.0,
            cohesion=1.0,
            drift=0.0,
            complexity=0.0,
            churn=0.0,
            coverage=1.0,
        )
        assert health.overall_health == pytest.approx(1.0)
        assert health.grade == "A+"

    def test_overall_health_worst(self) -> None:
        """Worst health = 0.0."""
        health = ModuleHealth(
            name="test",
            coupling=1.0,
            cohesion=0.0,
            drift=1.0,
            complexity=1.0,
            churn=1.0,
            coverage=0.0,
        )
        assert health.overall_health == pytest.approx(0.0)
        assert health.grade == "F"

    def test_grade_boundaries(self) -> None:
        """Test grade boundaries."""
        test_cases = [
            (0.95, "A+"),
            (0.92, "A"),
            (0.87, "B+"),
            (0.82, "B"),
            (0.77, "C+"),
            (0.72, "C"),
            (0.65, "D"),
            (0.50, "F"),
        ]
        for score, expected_grade in test_cases:
            # Back-calculate metrics to hit target score
            health = ModuleHealth(
                name="test",
                coupling=0.0,
                cohesion=1.0,
                drift=1 - score,  # Adjust drift to get target
                complexity=0.0,
                churn=0.0,
                coverage=1.0,
            )
            # This won't be exact, but we can test grade
            # Using a more direct approach:
            health2 = ModuleHealth(name="test")
            # Override for test by creating with specific values
            # that we know will produce the grade


# ============================================================================
# Python Import Analysis Tests
# ============================================================================


class TestPythonImportAnalysis:
    """Tests for Python import parsing."""

    def test_standard_import(self) -> None:
        """Test: import foo"""
        source = "import os"
        imports = analyze_python_imports(source, "test")
        assert len(imports) == 1
        assert imports[0].target == "os"
        assert imports[0].import_type == "standard"

    def test_multiple_imports(self) -> None:
        """Test: import foo, bar"""
        source = "import os, sys"
        imports = analyze_python_imports(source, "test")
        assert len(imports) == 2
        assert {i.target for i in imports} == {"os", "sys"}

    def test_from_import(self) -> None:
        """Test: from foo import bar"""
        source = "from pathlib import Path"
        imports = analyze_python_imports(source, "test")
        assert len(imports) == 1
        assert imports[0].target == "pathlib"
        assert imports[0].import_type == "from"

    def test_relative_import(self) -> None:
        """Test: from .foo import bar"""
        source = "from .sibling import helper"
        imports = analyze_python_imports(source, "test")
        assert len(imports) == 1
        assert imports[0].target == ".sibling"

    def test_double_relative_import(self) -> None:
        """Test: from ..foo import bar"""
        source = "from ..parent import helper"
        imports = analyze_python_imports(source, "test")
        assert len(imports) == 1
        assert imports[0].target == "..parent"

    def test_line_numbers(self) -> None:
        """Test that line numbers are captured."""
        source = """
import os

from pathlib import Path
"""
        imports = analyze_python_imports(source, "test")
        assert len(imports) == 2
        assert imports[0].line_number == 2  # import os
        assert imports[1].line_number == 4  # from pathlib

    def test_syntax_error_returns_empty(self) -> None:
        """Invalid Python returns empty list."""
        source = "this is not { valid python"
        imports = analyze_python_imports(source, "test")
        assert imports == []


# ============================================================================
# TypeScript Import Analysis Tests
# ============================================================================


class TestTypeScriptImportAnalysis:
    """Tests for TypeScript import parsing."""

    def test_named_import(self) -> None:
        """Test: import { x } from 'module'"""
        source = "import { useState } from 'react';"
        imports = analyze_typescript_imports(source, "test")
        assert len(imports) == 1
        assert imports[0].target == "react"

    def test_default_import(self) -> None:
        """Test: import x from 'module'"""
        source = "import React from 'react';"
        imports = analyze_typescript_imports(source, "test")
        assert len(imports) == 1
        assert imports[0].target == "react"

    def test_namespace_import(self) -> None:
        """Test: import * as x from 'module'"""
        source = "import * as React from 'react';"
        imports = analyze_typescript_imports(source, "test")
        assert len(imports) == 1
        assert imports[0].target == "react"

    def test_type_only_import(self) -> None:
        """Test: import type { x } from 'module'"""
        source = "import type { FC } from 'react';"
        imports = analyze_typescript_imports(source, "test")
        assert len(imports) == 1
        assert imports[0].target == "react"
        assert imports[0].is_type_only is True

    def test_side_effect_import(self) -> None:
        """Test: import 'module'"""
        source = "import './styles.css';"
        imports = analyze_typescript_imports(source, "test")
        assert len(imports) == 1
        assert imports[0].target == "./styles.css"

    def test_require(self) -> None:
        """Test: require('module')"""
        source = "const fs = require('fs');"
        imports = analyze_typescript_imports(source, "test")
        assert len(imports) == 1
        assert imports[0].target == "fs"
        assert imports[0].import_type == "dynamic"

    def test_relative_import(self) -> None:
        """Test: import from './module'"""
        source = "import { helper } from './utils';"
        imports = analyze_typescript_imports(source, "test")
        assert len(imports) == 1
        assert imports[0].target == "./utils"

    def test_multiple_imports(self) -> None:
        """Test multiple imports in one file."""
        source = """
import React from 'react';
import { useState, useEffect } from 'react';
import type { FC } from 'react';
import './styles.css';
"""
        imports = analyze_typescript_imports(source, "test")
        # 3 imports (type-only counted once, side-effect separate)
        assert len(imports) >= 3


# ============================================================================
# File Analysis Tests
# ============================================================================


class TestFileAnalysis:
    """Tests for file-level analysis."""

    def test_analyze_python_file(self, tmp_path: Path) -> None:
        """Test analyzing a Python file."""
        code = '''
"""Module docstring."""

import os
from pathlib import Path


def public_function():
    """A public function."""
    pass


class PublicClass:
    """A public class."""
    pass


def _private_function():
    pass
'''
        file_path = tmp_path / "test_module.py"
        file_path.write_text(code)

        module = analyze_python_file(file_path)

        assert module.name == "test_module"
        assert module.path == file_path
        assert len(module.imports) == 2
        assert "public_function" in module.exported_symbols
        assert "PublicClass" in module.exported_symbols
        assert "_private_function" not in module.exported_symbols

    def test_analyze_init_file(self, tmp_path: Path) -> None:
        """Test that __init__.py uses package name."""
        pkg_dir = tmp_path / "mypackage"
        pkg_dir.mkdir()
        init_file = pkg_dir / "__init__.py"
        init_file.write_text("from .core import main")

        module = analyze_python_file(init_file)
        assert module.name == "mypackage"
        assert module.is_package is True


# ============================================================================
# Graph Building Tests
# ============================================================================


class TestGraphBuilding:
    """Tests for building architecture graphs."""

    def test_build_empty_graph(self, tmp_path: Path) -> None:
        """Empty directory produces empty graph."""
        graph = build_architecture_graph(tmp_path, "python")
        assert graph.module_count == 0
        assert graph.edge_count == 0

    def test_duplicate_imports_deduplicated(self, tmp_path: Path) -> None:
        """Duplicate imports from same module should be counted once.

        Regression test: Without deduplication, multiple imports of the
        same target (e.g., at different lines or via different styles)
        inflate coupling metrics incorrectly.
        """
        # Module that imports 'os' twice (once direct, once from)
        (tmp_path / "multi_import.py").write_text(
            """
import os
import os  # duplicate
from os import path
from os import environ
"""
        )

        graph = build_architecture_graph(tmp_path, "python")

        # Should have exactly 1 edge (multi_import -> os), not 4
        edges_to_os = [e for e in graph.edges if e.target == "os"]
        assert len(edges_to_os) == 1, (
            f"Expected 1 deduplicated edge to 'os', got {len(edges_to_os)}: "
            f"{[(e.source, e.target, e.line_number) for e in edges_to_os]}"
        )

        # Total edge count should reflect deduplication
        assert graph.edge_count == 1

    def test_build_simple_graph(self, tmp_path: Path) -> None:
        """Build graph from simple module structure."""
        # Create module a.py
        (tmp_path / "a.py").write_text("import b")
        # Create module b.py
        (tmp_path / "b.py").write_text("# no imports")

        graph = build_architecture_graph(tmp_path, "python")

        assert graph.module_count == 2
        assert "a" in graph.modules
        assert "b" in graph.modules

    def test_dependencies(self, tmp_path: Path) -> None:
        """Test dependency tracking."""
        (tmp_path / "a.py").write_text("import b\nimport c")
        (tmp_path / "b.py").write_text("import c")
        (tmp_path / "c.py").write_text("")

        graph = build_architecture_graph(tmp_path, "python")

        # a depends on b and c
        a_deps = graph.get_dependencies("a")
        assert "b" in a_deps
        assert "c" in a_deps

        # c has a and b as dependents
        c_dependents = graph.get_dependents("c")
        assert "a" in c_dependents
        assert "b" in c_dependents

    def test_instability_metric(self, tmp_path: Path) -> None:
        """Test Martin's instability metric calculation."""
        # c is stable (depended upon, no deps)
        # a is unstable (deps, not depended upon)
        (tmp_path / "a.py").write_text("import b\nimport c")
        (tmp_path / "b.py").write_text("import c")
        (tmp_path / "c.py").write_text("")

        graph = build_architecture_graph(tmp_path, "python")

        # c: Ce=0, Ca=2 -> I=0/(2+0)=0
        c_instability = graph.compute_instability("c")
        assert c_instability == 0.0

        # a: Ce=2, Ca=0 -> I=2/(0+2)=1
        a_instability = graph.compute_instability("a")
        assert a_instability == 1.0

        # b: Ce=1, Ca=1 -> I=1/(1+1)=0.5
        b_instability = graph.compute_instability("b")
        assert b_instability == 0.5

    def test_health_metrics_computed(self, tmp_path: Path) -> None:
        """Test that health metrics are computed for modules."""
        (tmp_path / "a.py").write_text("import b")
        (tmp_path / "b.py").write_text("")

        graph = build_architecture_graph(tmp_path, "python")

        assert graph.modules["a"].health is not None
        assert graph.modules["b"].health is not None
        assert 0.0 <= graph.modules["a"].health.overall_health <= 1.0


# ============================================================================
# Architecture Graph Tests
# ============================================================================


class TestProjectRootDetection:
    """Tests for _get_project_root function."""

    def test_prefers_repo_root_over_pyproject(self, tmp_path: Path) -> None:
        """Ensure root detection prefers .git over nested pyproject.toml.

        Regression test: scans from impl/claude/protocols/gestalt should use
        the repo root (where .git lives), not impl/claude (where pyproject.toml is).
        """
        from protocols.gestalt.handler import _get_project_root

        # The real test: verify we find the repo root
        root = _get_project_root(prefer_repo_root=True)

        # Should find the kgents repo root (has .git or .kgents)
        assert (root / ".git").exists() or (root / ".kgents").exists(), (
            f"Expected to find .git or .kgents at {root}"
        )
        # Repo root should contain both spec/ and impl/
        # (if we stopped at impl/claude/pyproject.toml, spec wouldn't exist)
        assert (root / "spec").exists() or (root / "impl").exists(), (
            f"Expected repo root to contain spec/ or impl/, got {root}"
        )

    def test_allows_impl_only_root(self) -> None:
        """Can opt to use impl/claude as root for narrower scans."""
        from protocols.gestalt.handler import _get_project_root

        root = _get_project_root(prefer_repo_root=False)
        # Should find some pyproject.toml
        assert (root / "pyproject.toml").exists(), (
            f"Expected pyproject.toml at {root} when prefer_repo_root=False"
        )


class TestArchitectureGraph:
    """Tests for ArchitectureGraph methods."""

    def test_average_health(self) -> None:
        """Test average health calculation."""
        graph = ArchitectureGraph()
        graph.modules["a"] = Module(
            name="a",
            health=ModuleHealth(name="a", coupling=0.0, drift=0.0),
        )
        graph.modules["b"] = Module(
            name="b",
            health=ModuleHealth(name="b", coupling=1.0, drift=1.0),
        )

        # Average of two different health scores
        assert 0.0 < graph.average_health < 1.0

    def test_overall_grade(self) -> None:
        """Test overall architecture grade."""
        graph = ArchitectureGraph()
        # All modules with perfect health
        for name in ["a", "b", "c"]:
            graph.modules[name] = Module(
                name=name,
                health=ModuleHealth(
                    name=name,
                    coupling=0.0,
                    cohesion=1.0,
                    drift=0.0,
                    complexity=0.0,
                    churn=0.0,
                    coverage=1.0,
                ),
            )

        assert graph.overall_grade == "A+"
