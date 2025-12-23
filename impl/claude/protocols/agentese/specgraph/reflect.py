"""
SpecGraph Reflect Functor: Impl -> Spec extraction.

The Reflect functor transforms ImplCat -> SpecCat:
- Input: Python module paths (polynomial.py, operad.py, node.py)
- Output: SpecNode with extracted metadata

This is used for:
1. Drift detection: compare Reflect(impl) vs spec
2. Autopoiesis verification: Reflect(Compile(S)) ≅ S
3. Generating specs for hand-written implementations

Reference: plans/autopoietic-architecture.md (AD-009)
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from .parser import generate_frontmatter
from .types import (
    AgentesePath,
    LawSpec,
    OperadSpec,
    OperationSpec,
    PolynomialSpec,
    ReflectResult,
    SpecDomain,
    SpecNode,
)

# === AST Extraction Helpers ===


def _extract_enum_members(node: ast.ClassDef) -> list[str]:
    """Extract member names from an Enum class definition."""
    members = []
    for item in node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    members.append(target.id.lower())
        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            members.append(item.target.id.lower())
    return members


def _find_polyagent_call(tree: ast.Module) -> tuple[str, list[str]] | None:
    """
    Find PolyAgent(...) instantiation and extract positions.

    Returns (polynomial_name, positions) or None.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and isinstance(node.value, ast.Call):
                    call = node.value
                    if isinstance(call.func, ast.Name) and call.func.id == "PolyAgent":
                        name = target.id
                        # Try to extract positions from keyword
                        for kw in call.keywords:
                            if kw.arg == "positions":
                                # Could be frozenset(EnumClass) or explicit set
                                pass
                        return name, []
    return None


def _find_enum_class(tree: ast.Module, suffix: str = "Phase") -> tuple[str, list[str]] | None:
    """Find an Enum class ending with suffix and extract members."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name.endswith(suffix):
                # Check if it inherits from Enum
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "Enum":
                        members = _extract_enum_members(node)
                        return node.name, members
    return None


def _find_function(tree: ast.Module, suffix: str) -> str | None:
    """Find a function name ending with suffix."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.endswith(suffix):
            return node.name
    return None


def _find_operad_creation(tree: ast.Module) -> tuple[str, list[str], list[str]] | None:
    """
    Find Operad creation and extract operations/laws.

    Returns (operad_name, operation_names, law_names) or None.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and "_OPERAD" in target.id:
                    # Found operad assignment, look for create function call
                    return target.id, [], []
    return None


def _extract_operation_from_dict(tree: ast.Module) -> list[tuple[str, int, str]]:
    """
    Extract operation specs from ops["name"] = Operation(...) patterns.

    Returns list of (name, arity, signature).
    """
    operations: list[tuple[str, int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # Look for ops["name"] = Operation(...)
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Subscript):
                subscript = node.targets[0]
                if isinstance(subscript.slice, ast.Constant):
                    raw_name = subscript.slice.value
                    # Validate op_name is a string
                    if not isinstance(raw_name, str):
                        continue
                    op_name: str = raw_name

                    if isinstance(node.value, ast.Call):
                        call = node.value
                        # Extract arity from keywords
                        arity: int = 1
                        signature: str = ""
                        for kw in call.keywords:
                            if kw.arg == "arity" and isinstance(kw.value, ast.Constant):
                                raw_arity = kw.value.value
                                if isinstance(raw_arity, int):
                                    arity = raw_arity
                            elif kw.arg == "signature" and isinstance(kw.value, ast.Constant):
                                raw_sig = kw.value.value
                                if isinstance(raw_sig, str):
                                    signature = raw_sig
                        operations.append((op_name, arity, signature))
    return operations


def _find_node_decorator(tree: ast.Module) -> tuple[str, list[str]] | None:
    """
    Find @node("path") decorator and extract path and aspects.

    Returns (path, aspects) or None.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    func = decorator.func
                    if isinstance(func, ast.Name) and func.id == "node":
                        # Extract path from first argument
                        if decorator.args and isinstance(decorator.args[0], ast.Constant):
                            raw_path = decorator.args[0].value
                            # Validate path is a string
                            if not isinstance(raw_path, str):
                                continue
                            path: str = raw_path
                            # Find aspects by looking for @aspect decorators
                            aspects: list[str] = []
                            for item in node.body:
                                if isinstance(item, ast.AsyncFunctionDef):
                                    for deco in item.decorator_list:
                                        if isinstance(deco, ast.Call):
                                            if (
                                                isinstance(deco.func, ast.Name)
                                                and deco.func.id == "aspect"
                                            ):
                                                aspects.append(item.name)
                            return path, aspects
    return None


# === File Reflectors ===


def reflect_polynomial(path: Path) -> PolynomialSpec | None:
    """
    Reflect polynomial spec from polynomial.py file.

    Extracts:
    - positions from Enum class
    - transition function name
    - directions function name
    """
    if not path.exists():
        return None

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return None

    # Find phase enum
    enum_result = _find_enum_class(tree, "Phase")
    if not enum_result:
        return None

    enum_name, positions = enum_result

    # Find transition and directions functions
    transition_fn = _find_function(tree, "_transition")
    directions_fn = _find_function(tree, "_directions")

    return PolynomialSpec(
        positions=tuple(positions),
        transition_fn=transition_fn or "transition",
        directions_fn=directions_fn,
    )


def reflect_operad(path: Path) -> OperadSpec | None:
    """
    Reflect operad spec from operad.py file.

    Extracts:
    - operations from ops[...] assignments
    - laws from Law(...) instantiations
    - extends from base operad reference
    """
    if not path.exists():
        return None

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return None

    # Extract operations
    op_tuples = _extract_operation_from_dict(tree)
    operations = tuple(
        OperationSpec(name=name, arity=arity, signature=sig) for name, arity, sig in op_tuples
    )

    # Look for Law instantiations
    laws: list[LawSpec] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "Law":
                law_name: str = ""
                equation: str = ""
                for kw in node.keywords:
                    if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                        raw_name = kw.value.value
                        if isinstance(raw_name, str):
                            law_name = raw_name
                    elif kw.arg == "equation" and isinstance(kw.value, ast.Constant):
                        raw_eq = kw.value.value
                        if isinstance(raw_eq, str):
                            equation = raw_eq
                if law_name:
                    laws.append(LawSpec(name=law_name, equation=equation))

    # Check for AGENT_OPERAD extension
    extends = None
    if "AGENT_OPERAD" in source:
        extends = "AGENT_OPERAD"

    if not operations and not laws:
        return None

    return OperadSpec(
        operations=operations,
        laws=tuple(laws),
        extends=extends,
    )


def reflect_node(path: Path) -> AgentesePath | None:
    """
    Reflect AGENTESE path from node.py file.

    Extracts:
    - path from @node decorator
    - aspects from @aspect decorated methods
    """
    if not path.exists():
        return None

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return None

    result = _find_node_decorator(tree)
    if not result:
        return None

    path_str, aspects = result
    return AgentesePath(
        path=path_str,
        aspects=tuple(aspects),
    )


# === Domain Inference ===

# Known Crown Jewel mappings (holon name -> domain)
_CROWN_JEWEL_DOMAINS: dict[str, SpecDomain] = {
    "brain": SpecDomain.SELF,  # self.memory
    "f": SpecDomain.SELF,  # self.chat (Flow)
    "town": SpecDomain.WORLD,  # world.town
    "atelier": SpecDomain.WORLD,  # world.atelier
    "park": SpecDomain.WORLD,  # world.park
    # "gestalt": removed 2025-12-21
    "gardener": SpecDomain.CONCEPT,  # concept.gardener
    "design": SpecDomain.CONCEPT,  # concept.design
}


def _infer_domain(
    impl_path: Path,
    node_spec: AgentesePath | None,
    holon: str,
) -> SpecDomain:
    """
    Infer the AGENTESE domain for an implementation.

    Priority:
    1. Extract from @node path if available (most accurate)
    2. Use Crown Jewel mapping if known
    3. Infer from directory structure (fallback)
    """
    # Priority 1: Extract from AGENTESE path
    if node_spec and node_spec.path:
        path_parts = node_spec.path.split(".")
        if path_parts:
            try:
                return SpecDomain(path_parts[0])
            except ValueError:
                pass

    # Priority 2: Known Crown Jewel mapping
    if holon in _CROWN_JEWEL_DOMAINS:
        return _CROWN_JEWEL_DOMAINS[holon]

    # Priority 3: Directory structure inference
    parts = impl_path.parts
    if "services" in parts:
        return SpecDomain.SELF
    elif "contexts" in parts:
        return SpecDomain.CONCEPT
    else:
        return SpecDomain.WORLD


# === Main Reflect Function ===


def reflect_impl(impl_path: Path) -> ReflectResult:
    """
    Reflect specification from implementation directory.

    Args:
        impl_path: Path to impl directory (e.g., agents/town/)

    Returns:
        ReflectResult with extracted SpecNode and generated spec content
    """
    result = ReflectResult(
        impl_path=str(impl_path),
        errors=[],
    )

    if not impl_path.exists():
        result.errors.append(f"Directory not found: {impl_path}")
        return result

    # Determine holon name from path
    holon = impl_path.name

    # Reflect each component first (we need node path for domain inference)
    polynomial = reflect_polynomial(impl_path / "polynomial.py")
    operad = reflect_operad(impl_path / "operad.py")
    node_spec = reflect_node(impl_path / "node.py")

    # Infer domain from AGENTESE path if available
    domain = _infer_domain(impl_path, node_spec, holon)

    # Calculate confidence based on what we found
    found = sum(
        [
            polynomial is not None,
            operad is not None,
            node_spec is not None,
        ]
    )
    confidence = found / 3.0

    # Build SpecNode
    spec_node = SpecNode(
        domain=domain,
        holon=holon,
        source_path=impl_path,
        polynomial=polynomial,
        operad=operad,
        agentese=node_spec,
    )

    result.spec_node = spec_node
    result.confidence = confidence

    # Generate spec content (YAML frontmatter)
    result.spec_content = generate_frontmatter(spec_node)

    return result


def reflect_jewel(holon: str, impl_root: Path) -> ReflectResult:
    """
    Reflect a Crown Jewel across multiple directories.

    Crown Jewels can span both agents/<holon>/ and services/<holon>/.
    This function merges components found in both locations.

    Args:
        holon: The holon name (e.g., "town", "brain", "park")
        impl_root: Root of impl directory (e.g., impl/claude/)

    Returns:
        ReflectResult with merged components from all locations
    """
    candidates = [
        impl_root / "agents" / holon,
        impl_root / "services" / holon,
    ]

    # Collect components from all locations
    polynomial: PolynomialSpec | None = None
    operad: OperadSpec | None = None
    node_spec: AgentesePath | None = None
    errors: list[str] = []
    found_dirs: list[Path] = []

    for candidate in candidates:
        if not candidate.exists():
            continue
        found_dirs.append(candidate)

        # Try to extract each component (first found wins)
        if polynomial is None:
            polynomial = reflect_polynomial(candidate / "polynomial.py")

        if operad is None:
            operad = reflect_operad(candidate / "operad.py")

        if node_spec is None:
            node_spec = reflect_node(candidate / "node.py")

    # Build result
    if not found_dirs:
        return ReflectResult(
            impl_path=str(impl_root / "agents" / holon),
            errors=[f"No directory found for holon '{holon}'"],
        )

    # Infer domain from node path if available
    domain = _infer_domain(found_dirs[0], node_spec, holon)

    # Calculate confidence
    found = sum(
        [
            polynomial is not None,
            operad is not None,
            node_spec is not None,
        ]
    )
    confidence = found / 3.0

    # Build SpecNode
    spec_node = SpecNode(
        domain=domain,
        holon=holon,
        source_path=found_dirs[0],
        polynomial=polynomial,
        operad=operad,
        agentese=node_spec,
    )

    result = ReflectResult(
        impl_path=str(found_dirs[0]),
        errors=errors,
    )
    result.spec_node = spec_node
    result.confidence = confidence
    result.spec_content = generate_frontmatter(spec_node)

    return result


def reflect_crown_jewels(impl_root: Path) -> dict[str, ReflectResult]:
    """
    Reflect all Crown Jewels from impl directory.

    Uses reflect_jewel() to merge across agents/ and services/.

    Returns dict mapping jewel name to ReflectResult.
    """
    jewel_holons = ["brain", "atelier", "f"]  # town, park, gestalt removed 2025-12-21

    results = {}
    for holon in jewel_holons:
        result = reflect_jewel(holon, impl_root)
        if result.spec_node is not None:
            results[holon] = result

    return results


# === Exports ===

__all__ = [
    "reflect_polynomial",
    "reflect_operad",
    "reflect_node",
    "reflect_impl",
    "reflect_jewel",
    "reflect_crown_jewels",
]
