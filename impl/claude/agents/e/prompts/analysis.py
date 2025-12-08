"""
Code analysis utilities for prompt context building.

This module contains extraction functions for:
- Type annotations
- Imports
- Dataclass fields
- Enum values
- API signatures
- Pre-existing errors (mypy)
- Similar patterns
- Relevant principles
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path
from typing import Optional

from ..ast_analyzer import CodeStructure


def extract_type_annotations(code: str) -> dict[str, str]:
    """
    Extract type annotations from Python code.

    Returns a mapping of symbol names to their type signatures.
    Example: {"invoke": "async def invoke(self, input: A) -> B"}
    """
    annotations: dict[str, str] = {}

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return annotations

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            try:
                sig = ast.unparse(node).split(":", 1)[0]
                if node.returns:
                    sig += f" -> {ast.unparse(node.returns)}"
                annotations[node.name] = sig
            except Exception:
                pass

        elif isinstance(node, ast.ClassDef):
            try:
                bases_str = ""
                if node.bases:
                    bases_str = f"({', '.join(ast.unparse(b) for b in node.bases)})"
                annotations[node.name] = f"class {node.name}{bases_str}"
            except Exception:
                pass

    return annotations


def extract_imports(code: str) -> list[str]:
    """Extract import statements from code."""
    imports: list[str] = []

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_line = f"import {alias.name}"
                if alias.asname:
                    import_line += f" as {alias.asname}"
                imports.append(import_line)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            level = "." * node.level
            for alias in node.names:
                import_line = f"from {level}{module} import {alias.name}"
                if alias.asname:
                    import_line += f" as {alias.asname}"
                imports.append(import_line)

    return imports


def extract_dataclass_fields(code: str) -> dict[str, list[tuple[str, str]]]:
    """
    Extract dataclass field definitions from code.

    Returns mapping of class name to list of (field_name, field_type) tuples.
    Example: {"CodeModule": [("name", "str"), ("path", "Path")]}
    """
    fields_map: dict[str, list[tuple[str, str]]] = {}

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return fields_map

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if it's a dataclass
            is_dataclass = any(
                (isinstance(dec, ast.Name) and dec.id == "dataclass") or
                (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name) and dec.func.id == "dataclass")
                for dec in node.decorator_list
            )

            if is_dataclass:
                fields: list[tuple[str, str]] = []
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        field_name = item.target.id
                        field_type = ast.unparse(item.annotation) if item.annotation else "Any"
                        fields.append((field_name, field_type))

                if fields:
                    fields_map[node.name] = fields

    return fields_map


def extract_enum_values(code: str) -> dict[str, list[str]]:
    """
    Extract enum member names from code.

    Returns mapping of enum class name to list of member names.
    Example: {"ExperimentStatus": ["PENDING", "RUNNING", "PASSED", "FAILED", "HELD"]}
    """
    enum_map: dict[str, list[str]] = {}

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return enum_map

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if it inherits from Enum
            is_enum = any(
                (isinstance(base, ast.Name) and base.id == "Enum") or
                (isinstance(base, ast.Attribute) and base.attr == "Enum")
                for base in node.bases
            )

            if is_enum:
                members: list[str] = []
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                members.append(target.id)

                if members:
                    enum_map[node.name] = members

    return enum_map


def extract_api_signatures(imports: list[str], base_path: Path) -> dict[str, str]:
    """
    Extract API signatures from imported modules.

    Resolves local imports and extracts key signatures like Agent.invoke(),
    dataclass constructors, etc.

    Returns mapping of API name to signature string.
    Example: {"Agent.invoke": "async def invoke(self, input: A) -> B"}
    """
    api_sigs: dict[str, str] = {}

    # Try to find the project root (where impl/claude is)
    project_root = base_path
    while project_root.name != "claude" and project_root.parent != project_root:
        project_root = project_root.parent

    for import_line in imports:
        # Parse local imports (multiple patterns)
        try:
            if "from" not in import_line or "import" not in import_line:
                continue

            parts = import_line.split("import")
            if len(parts) != 2:
                continue

            module_part = parts[0].replace("from", "").strip()
            module_file: Optional[Path] = None

            # Resolve path for different import patterns
            if module_part.startswith("."):
                # Relative import - look in same directory
                module_file = base_path / f"{module_part[1:]}.py"
            elif module_part == "bootstrap.types":
                # Bootstrap module
                module_file = project_root / "bootstrap" / "types.py"
            elif module_part.startswith("agents.e"):
                # agents.e package (could be from agents.e.experiment, agents.e.judge, etc.)
                submodule = module_part.replace("agents.e", "").strip(".")
                if submodule:
                    module_file = project_root / "agents" / "e" / f"{submodule}.py"
                else:
                    # from agents.e import - look in __init__.py or common modules
                    for common_module in ["experiment", "judge", "evolution"]:
                        candidate = project_root / "agents" / "e" / f"{common_module}.py"
                        if candidate.exists():
                            _extract_sigs_from_file(candidate, api_sigs)
                    continue
            elif module_part.startswith("runtime."):
                # Runtime module
                submodule = module_part.replace("runtime.", "")
                module_file = project_root / "runtime" / f"{submodule}.py"
            else:
                continue

            if module_file and module_file.exists():
                _extract_sigs_from_file(module_file, api_sigs)

        except Exception:
            pass

    return api_sigs


def _extract_sigs_from_file(module_file: Path, api_sigs: dict[str, str]) -> None:
    """Helper to extract signatures from a single file."""
    try:
        module_code = module_file.read_text()
        tree = ast.parse(module_code)

        for node in ast.walk(tree):
            # Look for Agent base class and its invoke method
            if isinstance(node, ast.ClassDef) and node.name == "Agent":
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "invoke":
                        sig = ast.unparse(item).split(":", 1)[0]
                        if item.returns:
                            sig += f" -> {ast.unparse(item.returns)}"
                        api_sigs["Agent.invoke"] = sig.strip()

            # Extract dataclass fields for commonly imported types
            if isinstance(node, ast.ClassDef) and node.name in [
                "CodeModule", "TestInput", "JudgeInput", "AgentContext",
                "ExperimentInput", "CodeImprovement", "HypothesisInput"
            ]:
                is_dataclass = any(
                    (isinstance(dec, ast.Name) and dec.id == "dataclass") or
                    (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name) and dec.func.id == "dataclass")
                    for dec in node.decorator_list
                )
                if is_dataclass:
                    field_sigs = []
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            field_name = item.target.id
                            field_type = ast.unparse(item.annotation) if item.annotation else "Any"
                            field_sigs.append(f"{field_name}: {field_type}")

                    if field_sigs:
                        api_sigs[f"{node.name} fields"] = ", ".join(field_sigs[:8])  # First 8 fields

            # Extract enum values for commonly imported enums
            if isinstance(node, ast.ClassDef) and node.name in ["ExperimentStatus", "VerdictType"]:
                is_enum = any(
                    (isinstance(base, ast.Name) and base.id == "Enum") or
                    (isinstance(base, ast.Attribute) and base.attr == "Enum")
                    for base in node.bases
                )
                if is_enum:
                    members: list[str] = []
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    members.append(target.id)

                    if members:
                        api_sigs[f"{node.name} values"] = ", ".join(members)

    except (SyntaxError, Exception):
        pass


def check_existing_errors(path: Path) -> list[str]:
    """
    Check for pre-existing type/syntax errors in a module.

    Runs mypy in strict mode and captures errors.
    Returns list of error messages.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy", str(path), "--strict", "--no-error-summary"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            # Parse errors from mypy output
            errors = []
            for line in result.stdout.split("\n"):
                if line.strip() and path.name in line:
                    # Extract just the error message
                    if "error:" in line:
                        error_msg = line.split("error:", 1)[1].strip()
                        errors.append(error_msg)

            return errors[:10]  # Limit to first 10 errors

        return []

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def find_similar_patterns(structure: CodeStructure, base_path: Path) -> list[str]:
    """
    Find similar code patterns from successful modules.

    Searches the codebase for examples of similar classes/functions
    that can serve as scaffolding examples.
    """
    patterns = []

    # Look for similar class patterns
    for cls in structure.classes[:2]:  # Just first 2 classes
        cls_name = cls["name"]
        bases = cls.get("bases", [])

        if bases:
            # Search for other classes with same base
            try:
                import subprocess
                result = subprocess.run(
                    ["grep", "-r", "-n", "--include=*.py", f"class.*({bases[0]})", str(base_path)],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )

                if result.returncode == 0:
                    # Get first few matches
                    matches = result.stdout.split("\n")[:3]
                    for match in matches:
                        if match.strip() and structure.module_name not in match:
                            patterns.append(f"Similar class pattern: {match.split(':', 2)[-1].strip()}")

            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

    return patterns


def get_relevant_principles(module_category: str) -> list[str]:
    """
    Get relevant kgents principles for a module category.

    Different categories emphasize different principles:
    - bootstrap: Composability, minimalism
    - agents: Domain-specific guidance
    - runtime: Performance, reliability
    """
    core_principles = [
        "Composable: Agents are morphisms; composition is primary",
        "Tasteful: Quality over quantity",
        "Type-safe: Use strict type annotations (A -> B morphisms)",
    ]

    category_principles = {
        "bootstrap": [
            "Minimal: Bootstrap agents should be simple and foundational",
            "Generic: Work with any type parameters A, B",
        ],
        "agents": [
            "Domain-specific: Embody a clear domain concept",
            "Curated: Intentional, not comprehensive",
        ],
        "runtime": [
            "Reliable: Handle errors gracefully",
            "Efficient: Minimize LLM calls",
        ],
    }

    return core_principles + category_principles.get(module_category, [])
