#!/usr/bin/env python3
"""Add type annotations to test functions and fixtures missing them."""

from __future__ import annotations

import re
from pathlib import Path

# Common pytest fixture types
FIXTURE_TYPES: dict[str, str] = {
    "tmp_path": "Path",
    "tmp_path_factory": "pytest.TempPathFactory",
    "monkeypatch": "pytest.MonkeyPatch",
    "capsys": "pytest.CaptureFixture[str]",
    "capfd": "pytest.CaptureFixture[str]",
    "caplog": "pytest.LogCaptureFixture",
    "request": "pytest.FixtureRequest",
    "pytestconfig": "pytest.Config",
    "cache": "pytest.Cache",
    "recwarn": "pytest.WarningsRecorder",
}

# Import line to add
PYTEST_IMPORT = "import pytest"
PATH_IMPORT = "from pathlib import Path"


def needs_path_import(content: str) -> bool:
    """Check if Path import is needed."""
    return (
        "tmp_path" in content
        and "from pathlib import Path" not in content
        and "import pathlib" not in content
    )


def needs_pytest_import(content: str) -> bool:
    """Check if pytest import is needed for type annotations."""
    for fixture in [
        "monkeypatch",
        "capsys",
        "capfd",
        "caplog",
        "request",
        "pytestconfig",
        "cache",
        "recwarn",
        "tmp_path_factory",
    ]:
        if fixture in content:
            # Check if pytest is imported
            if "import pytest" not in content:
                return True
    return False


def add_imports(content: str) -> str:
    """Add necessary imports for type annotations."""
    lines = content.split("\n")
    new_lines = []
    imports_added = False

    need_path = needs_path_import(content)
    need_pytest = needs_pytest_import(content)

    for i, line in enumerate(lines):
        new_lines.append(line)
        # Add imports after the first import or from line
        if not imports_added and (
            line.startswith("import ") or line.startswith("from ")
        ):
            # Check if next line is also an import
            if i + 1 < len(lines) and (
                lines[i + 1].startswith("import ")
                or lines[i + 1].startswith("from ")
                or lines[i + 1].strip() == ""
            ):
                continue
            # Add our imports
            if need_path and "from pathlib import Path" not in content:
                new_lines.append(PATH_IMPORT)
            if need_pytest and "import pytest" not in content:
                new_lines.append(PYTEST_IMPORT)
            imports_added = True

    return "\n".join(new_lines)


def fix_parameter(param: str) -> str:
    """Add type annotation to a parameter if it's a known fixture."""
    param = param.strip()
    if not param or param == "self" or ":" in param or "=" in param:
        return param

    # Check if it's a known fixture
    if param in FIXTURE_TYPES:
        return f"{param}: {FIXTURE_TYPES[param]}"

    return param


def fix_function_signature(match: re.Match[str]) -> str:
    """Fix a function signature by adding type annotations."""
    prefix = match.group(1)  # 'def ' or 'async def '
    name = match.group(2)  # function name
    params = match.group(3)  # parameters
    suffix = match.group(4)  # rest including -> and :

    # Parse parameters
    param_list = []
    depth = 0
    current = ""

    for char in params:
        if char in "([{":
            depth += 1
            current += char
        elif char in ")]}":
            depth -= 1
            current += char
        elif char == "," and depth == 0:
            param_list.append(current.strip())
            current = ""
        else:
            current += char

    if current.strip():
        param_list.append(current.strip())

    # Fix each parameter
    fixed_params = [fix_parameter(p) for p in param_list]

    # Check if any parameter was actually fixed
    new_params = ", ".join(fixed_params)

    # Add -> None if missing
    if "->" not in suffix:
        suffix = " -> None" + suffix

    return f"{prefix}{name}({new_params}){suffix}"


def fix_test_file(path: Path) -> int:
    """Fix test functions in a file. Returns count of fixes made."""
    try:
        content = path.read_text()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return 0

    original = content

    # Pattern to match function definitions
    # Captures: (def/async def)(name)(params)(rest including ->? and :)
    pattern = r"((?:async )?def )(\w+)\(([^)]*)\)(\s*(?:->[^:]+)?:)"

    content = re.sub(pattern, fix_function_signature, content)

    # Add imports if needed
    if content != original:
        content = add_imports(content)

    if content != original:
        path.write_text(content)
        # Count how many fixes
        fixes = sum(
            1
            for m in re.finditer(pattern, original)
            if re.sub(pattern, fix_function_signature, m.group(0)) != m.group(0)
        )
        print(f"Fixed {path}")
        return 1
    return 0


def main() -> None:
    base = Path(".")
    total_fixes = 0

    # Find all test files
    test_files: list[Path] = []

    # Files in _tests directories
    test_files.extend(base.rglob("_tests/*.py"))

    # Files named test_*.py
    for p in base.rglob("test_*.py"):
        if p not in test_files:
            test_files.append(p)

    # Files named conftest.py (fixtures)
    test_files.extend(base.rglob("conftest.py"))

    print(f"Found {len(test_files)} test files")

    for path in sorted(set(test_files)):
        fixes = fix_test_file(path)
        total_fixes += fixes

    print(f"\nTotal files fixed: {total_fixes}")


if __name__ == "__main__":
    main()
