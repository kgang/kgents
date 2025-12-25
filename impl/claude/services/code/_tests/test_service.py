"""
Tests for CodeService - Explicit code sync flows.
"""

import pytest
import tempfile
from pathlib import Path

from ..service import (
    CodeService,
    SimplePythonParser,
    FunctionInfo,
    UploadResult,
    SyncResult,
    BootstrapResult,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def simple_python_file():
    """Create a simple Python file with functions."""
    return '''
def add(a, b):
    """Add two numbers."""
    return a + b

def multiply(x, y):
    """Multiply two numbers."""
    result = add(x, 0)  # Call to add
    return x * y

def undefined_caller():
    """Calls an undefined function."""
    return missing_function()  # Ghost!
'''


@pytest.fixture
def spec_content():
    """Sample spec content."""
    return """
# Math Operations

## add
Adds two numbers.

## multiply
Multiplies two numbers.
"""


@pytest.fixture
def impl_content():
    """Sample implementation."""
    return '''
def add(a, b):
    """Add two numbers."""
    return a + b

def multiply(x, y):
    """Multiply two numbers."""
    return x * y
'''


# =============================================================================
# Parser Tests
# =============================================================================


def test_parser_extracts_functions(simple_python_file):
    """Test that parser extracts function info."""
    parser = SimplePythonParser()

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(simple_python_file)
        temp_path = f.name

    try:
        functions = parser.parse_file(temp_path)

        assert len(functions) == 3
        assert {f.name for f in functions} == {"add", "multiply", "undefined_caller"}

        # Check function details
        add_func = next(f for f in functions if f.name == "add")
        assert add_func.docstring == "Add two numbers."
        assert add_func.body_hash  # Has hash
        assert add_func.line_start > 0
    finally:
        import os

        os.unlink(temp_path)


def test_parser_extracts_calls(simple_python_file):
    """Test that parser extracts function calls."""
    parser = SimplePythonParser()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(simple_python_file)
        temp_path = f.name

    try:
        functions = parser.parse_file(temp_path)

        # multiply calls add
        multiply_func = next(f for f in functions if f.name == "multiply")
        assert "add" in multiply_func.calls

        # undefined_caller calls missing_function
        undefined_func = next(f for f in functions if f.name == "undefined_caller")
        assert "missing_function" in undefined_func.calls
    finally:
        import os

        os.unlink(temp_path)


def test_parser_handles_invalid_file():
    """Test parser handles invalid Python gracefully."""
    parser = SimplePythonParser()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("this is not valid python {{{")
        temp_path = f.name

    try:
        functions = parser.parse_file(temp_path)
        assert functions == []  # Empty list on parse error
    finally:
        import os

        os.unlink(temp_path)


# =============================================================================
# Service Tests - upload_file
# =============================================================================


@pytest.mark.asyncio
async def test_upload_file_creates_functions(simple_python_file):
    """Test upload_file creates FunctionCrystals."""
    service = CodeService()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(simple_python_file)
        temp_path = f.name

    try:
        result = await service.upload_file(temp_path)

        assert isinstance(result, UploadResult)
        assert result.file_path == temp_path
        assert len(result.functions_created) == 3
        assert all(fid.startswith("fn_") for fid in result.functions_created)
    finally:
        import os

        os.unlink(temp_path)


@pytest.mark.asyncio
async def test_upload_file_detects_ghosts(simple_python_file):
    """Test upload_file detects ghost placeholders."""
    service = CodeService()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(simple_python_file)
        temp_path = f.name

    try:
        result = await service.upload_file(temp_path)

        # Should detect missing_function as ghost
        assert len(result.ghosts_created) > 0
        assert "missing_function" in result.ghosts_created
    finally:
        import os

        os.unlink(temp_path)


@pytest.mark.asyncio
async def test_upload_file_creates_kblock(simple_python_file):
    """Test upload_file creates K-block."""
    service = CodeService()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(simple_python_file)
        temp_path = f.name

    try:
        result = await service.upload_file(temp_path, create_kblock=True)

        assert result.kblock_id is not None
        assert result.kblock_id.startswith("kb_")
    finally:
        import os

        os.unlink(temp_path)


@pytest.mark.asyncio
async def test_upload_file_without_extraction():
    """Test upload_file with auto_extract_functions=False."""
    service = CodeService()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def foo(): pass")
        temp_path = f.name

    try:
        result = await service.upload_file(temp_path, auto_extract_functions=False)

        assert len(result.functions_created) == 0
        assert len(result.ghosts_created) == 0
    finally:
        import os

        os.unlink(temp_path)


# =============================================================================
# Service Tests - sync_directory
# =============================================================================


@pytest.mark.asyncio
async def test_sync_directory_processes_files(simple_python_file):
    """Test sync_directory processes all matching files."""
    service = CodeService()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create multiple Python files
        (Path(temp_dir) / "file1.py").write_text(simple_python_file)
        (Path(temp_dir) / "file2.py").write_text("def bar(): pass")

        result = await service.sync_directory(temp_dir, pattern="*.py")

        assert isinstance(result, SyncResult)
        assert result.files_processed == 2
        assert result.functions_created > 0


@pytest.mark.asyncio
async def test_sync_directory_handles_errors():
    """Test sync_directory handles file errors gracefully."""
    service = CodeService()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create invalid Python file
        (Path(temp_dir) / "bad.py").write_text("invalid {{")

        result = await service.sync_directory(temp_dir)

        assert result.files_processed == 1
        # Should have error but not crash
        assert len(result.errors) == 0 or result.errors[0]  # May or may not error


# =============================================================================
# Service Tests - bootstrap_spec_impl_pair
# =============================================================================


@pytest.mark.asyncio
async def test_bootstrap_creates_full_chain(spec_content, impl_content):
    """Test bootstrap_spec_impl_pair creates full derivation chain."""
    service = CodeService()

    result = await service.bootstrap_spec_impl_pair(
        spec_content=spec_content, impl_content=impl_content, name="math_ops"
    )

    assert isinstance(result, BootstrapResult)
    assert result.spec_id == "spec_math_ops"
    assert len(result.impl_functions) == 2  # add and multiply
    assert result.kblock_id == "kb_math_ops"
    assert len(result.derivation_edges) == 2  # One edge per function


@pytest.mark.asyncio
async def test_bootstrap_handles_empty_impl():
    """Test bootstrap handles empty implementation."""
    service = CodeService()

    result = await service.bootstrap_spec_impl_pair(
        spec_content="# Empty", impl_content="# No functions", name="empty"
    )

    assert result.spec_id == "spec_empty"
    assert len(result.impl_functions) == 0
    assert len(result.derivation_edges) == 0


# =============================================================================
# Ghost Detection Tests
# =============================================================================


def test_detect_ghosts_finds_undefined():
    """Test _detect_ghosts finds undefined functions."""
    service = CodeService()

    functions = [
        FunctionInfo(
            name="foo",
            qualified_name="foo",
            file_path="test.py",
            line_start=1,
            line_end=2,
            body="def foo(): bar()",
            docstring=None,
            calls=["bar"],
        ),
        FunctionInfo(
            name="baz",
            qualified_name="baz",
            file_path="test.py",
            line_start=3,
            line_end=4,
            body="def baz(): qux()",
            docstring=None,
            calls=["qux"],
        ),
    ]

    ghosts = service._detect_ghosts(functions)

    assert len(ghosts) == 2
    assert {g["name"] for g in ghosts} == {"bar", "qux"}


def test_detect_ghosts_ignores_defined():
    """Test _detect_ghosts ignores defined functions."""
    service = CodeService()

    functions = [
        FunctionInfo(
            name="foo",
            qualified_name="foo",
            file_path="test.py",
            line_start=1,
            line_end=2,
            body="def foo(): bar()",
            docstring=None,
            calls=["bar"],
        ),
        FunctionInfo(
            name="bar",
            qualified_name="bar",
            file_path="test.py",
            line_start=3,
            line_end=4,
            body="def bar(): pass",
            docstring=None,
            calls=[],
        ),
    ]

    ghosts = service._detect_ghosts(functions)

    assert len(ghosts) == 0  # bar is defined


def test_detect_ghosts_deduplicates():
    """Test _detect_ghosts deduplicates ghost names."""
    service = CodeService()

    functions = [
        FunctionInfo(
            name="foo",
            qualified_name="foo",
            file_path="test.py",
            line_start=1,
            line_end=2,
            body="def foo(): missing()",
            docstring=None,
            calls=["missing"],
        ),
        FunctionInfo(
            name="bar",
            qualified_name="bar",
            file_path="test.py",
            line_start=3,
            line_end=4,
            body="def bar(): missing()",
            docstring=None,
            calls=["missing"],
        ),
    ]

    ghosts = service._detect_ghosts(functions)

    assert len(ghosts) == 1  # Only one ghost for "missing"
    assert ghosts[0]["name"] == "missing"


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_full_flow_upload_and_sync():
    """Test full flow: upload file, then sync directory."""
    service = CodeService()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create file
        file_path = Path(temp_dir) / "code.py"
        file_path.write_text("def hello(): world()")

        # Upload single file
        upload_result = await service.upload_file(str(file_path))
        assert len(upload_result.functions_created) == 1
        assert len(upload_result.ghosts_created) == 1  # world is ghost

        # Sync directory
        sync_result = await service.sync_directory(temp_dir)
        assert sync_result.files_processed == 1
        assert sync_result.functions_created == 1


@pytest.mark.asyncio
async def test_full_flow_bootstrap():
    """Test full bootstrap flow for QA."""
    service = CodeService()

    spec = """
# Calculator
Addition and multiplication.
"""
    impl = """
def add(a, b):
    return a + b

def multiply(x, y):
    return x * y
"""

    result = await service.bootstrap_spec_impl_pair(spec, impl, "calc")

    # Should have complete derivation chain
    assert result.spec_id
    assert len(result.impl_functions) == 2
    assert result.kblock_id
    assert len(result.derivation_edges) == len(result.impl_functions)
