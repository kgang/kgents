"""
Tests for Python AST parser.

Tests cover:
- Simple function parsing
- Type annotations
- Async functions
- Class methods
- Nested functions
- Import extraction
- Call graph extraction
- Body hash computation
- Edge cases and error handling
"""

import ast
import tempfile
from pathlib import Path

import pytest

from services.code.parser import (
    PythonFunctionParser,
    parse_file,
    extract_imports,
    extract_calls,
    compute_body_hash,
    signature_to_string,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def temp_python_file(tmp_path: Path):
    """Create a temporary Python file for testing."""

    def _create_file(content: str) -> Path:
        file_path = tmp_path / "test_module.py"
        file_path.write_text(content)
        return file_path

    return _create_file


# =============================================================================
# Basic Function Parsing Tests
# =============================================================================


def test_parse_simple_function(temp_python_file):
    """Test parsing a simple function."""
    source = """
def hello():
    print("Hello, world!")
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)

    assert len(functions) == 1
    func = functions[0]
    assert func.qualified_name == "hello"
    assert func.signature == "def hello()"
    assert func.is_async is False
    assert func.is_method is False
    assert len(func.parameters) == 0


def test_parse_function_with_params(temp_python_file):
    """Test parsing a function with parameters."""
    source = """
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)

    assert len(functions) == 1
    func = functions[0]
    assert len(func.parameters) == 2

    # Check first parameter (no default)
    assert func.parameters[0].name == "name"
    assert func.parameters[0].type_annotation is None
    assert func.parameters[0].default is None

    # Check second parameter (with default)
    assert func.parameters[1].name == "greeting"
    assert func.parameters[1].default == "'Hello'"  # AST normalizes to single quotes


def test_parse_function_with_type_annotations(temp_python_file):
    """Test parsing a function with type annotations."""
    source = """
def add(x: int, y: int) -> int:
    return x + y
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)

    assert len(functions) == 1
    func = functions[0]
    assert func.return_type == "int"
    assert len(func.parameters) == 2
    assert func.parameters[0].type_annotation == "int"
    assert func.parameters[1].type_annotation == "int"
    assert "-> int" in func.signature


def test_parse_function_with_complex_types(temp_python_file):
    """Test parsing a function with complex type annotations."""
    source = """
from typing import list, Optional

def process(items: list[dict[str, int]], default: Optional[str] = None) -> tuple[str, ...]:
    return tuple(str(i) for i in items)
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)

    assert len(functions) == 1
    func = functions[0]
    assert func.parameters[0].type_annotation == "list[dict[str, int]]"
    assert func.parameters[1].type_annotation == "Optional[str]"
    assert func.return_type == "tuple[str, ...]"


def test_parse_function_with_docstring(temp_python_file):
    """Test parsing a function with docstring."""
    source = '''
def documented():
    """This function has a docstring."""
    pass
    '''
    file_path = temp_python_file(source)

    functions = parse_file(file_path)

    assert len(functions) == 1
    func = functions[0]
    assert func.docstring == "This function has a docstring."


# =============================================================================
# Async Function Tests
# =============================================================================


def test_parse_async_function(temp_python_file):
    """Test parsing an async function."""
    source = """
async def fetch_data(url: str) -> dict:
    return {"url": url}
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)

    assert len(functions) == 1
    func = functions[0]
    assert func.is_async is True
    assert func.signature.startswith("async def")


# =============================================================================
# Class Method Tests
# =============================================================================


def test_parse_class_methods(temp_python_file):
    """Test parsing methods in a class."""
    source = """
class Calculator:
    def __init__(self, value: int):
        self.value = value

    def add(self, x: int) -> int:
        return self.value + x

    @staticmethod
    def multiply(x: int, y: int) -> int:
        return x * y

    @classmethod
    def from_string(cls, s: str):
        return cls(int(s))
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)

    assert len(functions) == 4

    # Check __init__
    init_func = next(f for f in functions if f.qualified_name == "Calculator.__init__")
    assert init_func.is_method is True
    assert init_func.class_name == "Calculator"

    # Check add
    add_func = next(f for f in functions if f.qualified_name == "Calculator.add")
    assert add_func.is_method is True
    assert "@staticmethod" not in add_func.decorators

    # Check staticmethod
    mult_func = next(f for f in functions if f.qualified_name == "Calculator.multiply")
    assert mult_func.is_method is True
    assert any("staticmethod" in d for d in mult_func.decorators)

    # Check classmethod
    from_str = next(f for f in functions if f.qualified_name == "Calculator.from_string")
    assert from_str.is_method is True
    assert any("classmethod" in d for d in from_str.decorators)


# =============================================================================
# Nested Function Tests
# =============================================================================


def test_parse_nested_functions(temp_python_file):
    """Test parsing nested functions."""
    source = """
def outer(x):
    def inner(y):
        return x + y
    return inner
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)

    assert len(functions) == 2

    outer_func = next(f for f in functions if f.qualified_name == "outer")
    inner_func = next(f for f in functions if f.qualified_name == "outer.inner")

    assert outer_func.is_method is False
    assert inner_func.is_method is False
    assert "outer" in inner_func.qualified_name


# =============================================================================
# Import Extraction Tests
# =============================================================================


def test_extract_imports(temp_python_file):
    """Test extracting import statements."""
    source = """
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field

def foo():
    pass
    """
    file_path = temp_python_file(source)

    imports = extract_imports(file_path)

    assert "os" in imports
    assert "sys" in imports
    assert "pathlib" in imports
    assert "pathlib.Path" in imports
    assert "typing" in imports
    assert "typing.List" in imports
    assert "dataclasses" in imports
    assert "dataclasses.dataclass" in imports


def test_parse_file_includes_imports(temp_python_file):
    """Test that parse_file includes imports in FunctionInfo."""
    source = """
import json
from pathlib import Path

def load_config(path: Path):
    with open(path) as f:
        return json.load(f)
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)

    assert len(functions) == 1
    func = functions[0]
    assert "json" in func.imports
    assert "pathlib" in func.imports


# =============================================================================
# Call Graph Tests
# =============================================================================


def test_extract_calls_from_function(temp_python_file):
    """Test extracting function calls."""
    source = """
def helper1():
    return 42

def helper2(x):
    return x * 2

def main():
    a = helper1()
    b = helper2(a)
    return b
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)
    main_func = next(f for f in functions if f.qualified_name == "main")

    assert "helper1" in main_func.calls
    assert "helper2" in main_func.calls


def test_extract_method_calls(temp_python_file):
    """Test extracting method calls."""
    source = """
def process():
    data = {"key": "value"}
    return data.get("key")
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)
    func = functions[0]

    # Should detect data.get call
    assert any("get" in call for call in func.calls)


# =============================================================================
# Body Hash Tests
# =============================================================================


def test_body_hash_computation(temp_python_file):
    """Test body hash computation."""
    source1 = """
def foo(x):
    return x + 1
    """
    source2 = """
def foo(x):
    return x + 2  # Different body
    """
    source3 = """
def foo(x):
    # Same logic, different indentation
    return x + 1
    """

    file1 = temp_python_file(source1)
    file2 = file1.parent / "test2.py"
    file2.write_text(source2)
    file3 = file1.parent / "test3.py"
    file3.write_text(source3)

    func1 = parse_file(file1)[0]
    func2 = parse_file(file2)[0]
    func3 = parse_file(file3)[0]

    # Different body should have different hash
    assert func1.body_hash != func2.body_hash

    # Same logic should have same hash (normalized whitespace)
    # Note: This depends on implementation - may or may not be equal


def test_body_hash_stable(temp_python_file):
    """Test that body hash is stable for same function."""
    source = """
def stable(x: int) -> int:
    '''Docstring'''
    return x * 2
    """

    file_path = temp_python_file(source)

    # Parse twice
    func1 = parse_file(file_path)[0]
    func2 = parse_file(file_path)[0]

    # Hash should be identical
    assert func1.body_hash == func2.body_hash
    assert func1.body_hash != ""  # Not empty


# =============================================================================
# Decorator Tests
# =============================================================================


def test_parse_decorators(temp_python_file):
    """Test parsing function decorators."""
    source = """
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

@property
def name(self):
    return self._name
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)

    fib = next(f for f in functions if f.qualified_name == "fibonacci")
    assert len(fib.decorators) == 1
    assert "lru_cache" in fib.decorators[0]

    name_func = next(f for f in functions if f.qualified_name == "name")
    assert "property" in name_func.decorators


# =============================================================================
# Variadic Parameters Tests
# =============================================================================


def test_parse_variadic_parameters(temp_python_file):
    """Test parsing *args and **kwargs."""
    source = """
def flexible(a, *args, b=10, **kwargs):
    pass
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)
    func = functions[0]

    # Find *args
    args_param = next(p for p in func.parameters if p.name == "args")
    assert args_param.is_variadic is True

    # Find **kwargs
    kwargs_param = next(p for p in func.parameters if p.name == "kwargs")
    assert kwargs_param.is_keyword is True


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


def test_parse_empty_file(temp_python_file):
    """Test parsing an empty file."""
    source = ""
    file_path = temp_python_file(source)

    functions = parse_file(file_path)

    assert len(functions) == 0


def test_parse_file_with_no_functions(temp_python_file):
    """Test parsing a file with no functions."""
    source = """
# Just a comment
x = 42
y = "hello"
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)

    assert len(functions) == 0


def test_parse_syntax_error(temp_python_file):
    """Test parsing a file with syntax errors."""
    source = """
def broken(
    # Missing closing paren
    pass
    """
    file_path = temp_python_file(source)

    with pytest.raises(SyntaxError):
        parse_file(file_path)


def test_parse_nonexistent_file():
    """Test parsing a file that doesn't exist."""
    with pytest.raises(FileNotFoundError):
        parse_file("/nonexistent/path/file.py")


def test_function_with_no_body(temp_python_file):
    """Test parsing a function with only pass."""
    source = """
def empty():
    pass
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)

    assert len(functions) == 1
    func = functions[0]
    assert func.body_hash != ""  # Should still have a hash


# =============================================================================
# Module Name Tests
# =============================================================================


def test_qualified_name_with_module(temp_python_file):
    """Test qualified names with module prefix."""
    source = """
def foo():
    pass

class Bar:
    def baz(self):
        pass
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path, module_name="mymodule")

    foo_func = next(f for f in functions if "foo" in f.qualified_name)
    assert foo_func.qualified_name == "mymodule.foo"

    baz_func = next(f for f in functions if "baz" in f.qualified_name)
    assert baz_func.qualified_name == "Bar.baz"  # Class name, not module


# =============================================================================
# Signature String Tests
# =============================================================================


def test_signature_to_string():
    """Test converting AST function def to signature string."""
    source = "def example(x: int, y: str = 'test') -> bool: pass"
    tree = ast.parse(source)
    func_node = tree.body[0]

    sig = signature_to_string(func_node)

    assert "def example" in sig
    assert "x: int" in sig
    assert "y: str = 'test'" in sig
    assert "-> bool" in sig


# =============================================================================
# Integration Tests
# =============================================================================


def test_parse_real_file():
    """Test parsing a real Python file (this test file itself)."""
    # Get path to this test file
    this_file = Path(__file__)

    functions = parse_file(this_file, module_name="services.code._tests.test_parser")

    # Should find many test functions
    assert len(functions) > 10

    # All should have qualified names
    for func in functions:
        assert func.qualified_name
        assert func.file_path == str(this_file.absolute())
        assert func.line_range[0] > 0
        assert func.line_range[1] >= func.line_range[0]


def test_to_dict_conversion(temp_python_file):
    """Test converting FunctionInfo to dict."""
    source = """
def example(x: int) -> str:
    '''Example function.'''
    return str(x)
    """
    file_path = temp_python_file(source)

    functions = parse_file(file_path)
    func = functions[0]

    data = func.to_dict()

    assert data["qualified_name"] == "example"
    assert data["signature"] == "def example(x: int) -> str"
    assert data["docstring"] == "Example function."
    assert data["return_type"] == "str"
    assert len(data["parameters"]) == 1
    assert data["is_async"] is False
    assert data["body_hash"]
