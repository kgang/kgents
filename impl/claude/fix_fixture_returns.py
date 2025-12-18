#!/usr/bin/env python3
"""Fix fixtures that have -> None but return values."""

from __future__ import annotations

import re
from pathlib import Path


def fix_file(path: Path) -> int:
    """Fix fixtures in a file that have -> None but return values."""
    try:
        content = path.read_text()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return 0

    lines = content.split("\n")
    fixes = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is a fixture with -> None
        if "@pytest.fixture" in line or (i > 0 and "@pytest.fixture" in lines[i - 1]):
            # Look for def line with -> None
            j = i
            while j < len(lines) and not lines[j].strip().startswith("def "):
                j += 1
            if j < len(lines) and "-> None:" in lines[j]:
                # Check if function body has a return statement with value
                indent = len(lines[j]) - len(lines[j].lstrip())
                k = j + 1
                has_return_value = False
                while k < len(lines):
                    body_line = lines[k]
                    if body_line.strip() and not body_line.strip().startswith("#"):
                        body_indent = len(body_line) - len(body_line.lstrip())
                        if body_indent <= indent and body_line.strip():
                            break  # End of function
                        if (
                            "return " in body_line
                            and body_line.strip() != "return"
                            and body_line.strip() != "return None"
                        ):
                            has_return_value = True
                            break
                    k += 1

                if has_return_value:
                    lines[j] = lines[j].replace("-> None:", "-> Any:")
                    fixes += 1
        i += 1

    if fixes > 0:
        content = "\n".join(lines)
        # Ensure Any is imported
        if "from typing import" in content and "Any" not in content:
            content = re.sub(r"(from typing import )([^)]+)", r"\1Any, \2", content, count=1)
        elif "from typing import" not in content:
            # Add typing import at top after other imports
            lines = content.split("\n")
            for idx, ln in enumerate(lines):
                if ln.startswith("import ") or ln.startswith("from "):
                    continue
                if ln.strip() == "" and idx > 0:
                    lines.insert(idx, "from typing import Any")
                    break
            content = "\n".join(lines)

        path.write_text(content)
        print(f"Fixed {fixes} fixtures in {path}")
        return fixes

    return 0


def main() -> None:
    base = Path(".")
    total = 0

    # Find all test files and conftest files
    for pattern in ["_tests/*.py", "test_*.py", "conftest.py"]:
        for path in base.rglob(pattern):
            if ".venv" in str(path):
                continue
            total += fix_file(path)

    print(f"\nTotal fixtures fixed: {total}")


if __name__ == "__main__":
    main()
