"""
SpecGraph Parser: Parse YAML frontmatter from spec/*.md files.

Extracts structured metadata from specification files:
- polynomial: positions, transition function
- operad: operations, laws
- sheaf: sections, gluing function
- agentese: path, aspects

The parser is forgiving - partial specs are valid during architecture redesign.

Reference: plans/autopoietic-architecture.md (AD-009)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .types import (
    AgentesePath,
    AspectCategory,
    AspectSpec,
    LawSpec,
    OperadSpec,
    OperationSpec,
    PolynomialSpec,
    ServiceSpec,
    SheafSpec,
    SpecDomain,
    SpecGraph,
    SpecNode,
)

# === Parser Errors ===


class ParseError(Exception):
    """Error parsing a spec file."""

    def __init__(self, message: str, path: Path | None = None) -> None:
        self.path = path
        super().__init__(f"{path}: {message}" if path else message)


# === YAML Frontmatter Parser ===


FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n",
    re.DOTALL,
)


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """
    Extract YAML frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter_dict, remaining_content)
        Returns empty dict if no frontmatter found.

    Raises:
        ParseError: If YAML is invalid or frontmatter is malformed.

    Notes:
        - Handles encoding issues gracefully
        - Validates that frontmatter is a dict (not a list or scalar)
        - Returns empty dict for empty frontmatter blocks
    """
    if not content:
        return {}, ""

    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}, content

    yaml_content = match.group(1)
    remaining = content[match.end() :]

    try:
        frontmatter = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        raise ParseError(f"Invalid YAML frontmatter: {e}")

    # Handle edge cases
    if frontmatter is None:
        return {}, remaining
    if not isinstance(frontmatter, dict):
        raise ParseError(
            f"Frontmatter must be a YAML mapping, got {type(frontmatter).__name__}"
        )

    return frontmatter, remaining


# === Component Parsers ===


def parse_polynomial(data: dict[str, Any] | None) -> PolynomialSpec | None:
    """Parse polynomial specification from frontmatter."""
    if not data:
        return None

    positions = data.get("positions", [])
    if isinstance(positions, str):
        positions = [p.strip() for p in positions.split(",")]

    transition_fn = data.get("transition", "")
    directions_fn = data.get("directions")

    if not positions or not transition_fn:
        return None

    return PolynomialSpec(
        positions=tuple(positions),
        transition_fn=transition_fn,
        directions_fn=directions_fn,
    )


def parse_operation(name: str, data: dict[str, Any]) -> OperationSpec:
    """Parse a single operation spec."""
    arity = data.get("arity", 1)
    variadic = data.get("variadic", False)

    # Infer variadic from arity if not explicitly set
    if arity <= 0 and not variadic:
        variadic = True

    return OperationSpec(
        name=name,
        arity=arity,
        signature=data.get("signature", ""),
        description=data.get("description", ""),
        variadic=variadic,
    )


def parse_law(name: str, data: dict[str, Any] | str) -> LawSpec:
    """Parse a single law spec."""
    if isinstance(data, str):
        return LawSpec(name=name, equation=data)
    return LawSpec(
        name=name,
        equation=data.get("equation", ""),
        description=data.get("description", ""),
    )


def parse_operad(data: dict[str, Any] | None) -> OperadSpec | None:
    """Parse operad specification from frontmatter."""
    if not data:
        return None

    operations_data = data.get("operations", {})
    if not operations_data:
        return None

    operations = tuple(
        parse_operation(name, op_data) for name, op_data in operations_data.items()
    )

    laws_data = data.get("laws", {})
    laws = tuple(parse_law(name, law_data) for name, law_data in laws_data.items())

    extends = data.get("extends")

    return OperadSpec(
        operations=operations,
        laws=laws,
        extends=extends,
    )


def parse_sheaf(data: dict[str, Any] | None) -> SheafSpec | None:
    """Parse sheaf specification from frontmatter."""
    if not data:
        return None

    sections = data.get("sections", [])
    if isinstance(sections, str):
        sections = [s.strip() for s in sections.split(",")]

    gluing_fn = data.get("gluing", "")

    if not sections or not gluing_fn:
        return None

    return SheafSpec(
        sections=tuple(sections),
        gluing_fn=gluing_fn,
    )


def parse_aspect(data: dict[str, Any] | str) -> AspectSpec | str:
    """Parse a single aspect spec (can be simple string or rich dict)."""
    if isinstance(data, str):
        return data  # Simple string format

    name = data.get("name", "")
    if not name:
        # Return a default string if no name found
        fallback = data.get("name")
        return str(fallback) if fallback is not None else "unknown"

    category_str = data.get("category", "perception")
    try:
        category = AspectCategory(category_str.lower())
    except ValueError:
        category = AspectCategory.PERCEPTION

    effects = data.get("effects", [])
    if isinstance(effects, str):
        effects = [e.strip() for e in effects.split(",")]

    return AspectSpec(
        name=name,
        category=category,
        effects=tuple(effects),
        help=data.get("help", ""),
    )


def parse_agentese(data: dict[str, Any] | None) -> AgentesePath | None:
    """Parse AGENTESE path specification from frontmatter.

    Supports two formats:
    1. Simple: aspects: [manifest, witness]
    2. Rich: aspects: [{name: manifest, category: perception}, ...]
    """
    if not data:
        return None

    path = data.get("path", "")
    if not path:
        return None

    raw_aspects = data.get("aspects", [])
    if isinstance(raw_aspects, str):
        raw_aspects = [a.strip() for a in raw_aspects.split(",")]

    # Parse aspects (may be simple strings or rich dicts)
    simple_aspects: list[str] = []
    rich_aspects: list[AspectSpec] = []

    for aspect in raw_aspects:
        parsed = parse_aspect(aspect)
        if isinstance(parsed, str):
            simple_aspects.append(parsed)
        else:
            rich_aspects.append(parsed)

    return AgentesePath(
        path=path,
        aspects=tuple(simple_aspects) if simple_aspects else (),
        aspect_specs=tuple(rich_aspects) if rich_aspects else (),
    )


def parse_service(data: dict[str, Any] | None) -> ServiceSpec | None:
    """Parse service specification from frontmatter."""
    if not data:
        return None

    adapters = data.get("adapters", [])
    if isinstance(adapters, str):
        adapters = [a.strip() for a in adapters.split(",")]

    return ServiceSpec(
        crown_jewel=data.get("crown_jewel", True),
        adapters=tuple(adapters),
        frontend=data.get("frontend", False),
        persistence=data.get("persistence", ""),
    )


# === File Parser ===


def parse_spec_file(path: Path) -> SpecNode:
    """
    Parse a spec file into a SpecNode.

    Args:
        path: Path to the spec markdown file

    Returns:
        SpecNode with parsed metadata

    Raises:
        ParseError: If the file cannot be parsed

    Notes:
        - Handles encoding issues with UTF-8 fallback
        - Infers domain and holon from path if not in frontmatter
        - Returns partial SpecNode for incomplete specs (forgiving mode)
    """
    if not path.exists():
        raise ParseError(f"File not found: {path}", path)

    # Read with encoding error handling
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            # Fallback to latin-1 which accepts any byte sequence
            content = path.read_text(encoding="latin-1")
        except Exception as e:
            raise ParseError(f"Cannot read file (encoding error): {e}", path)
    except OSError as e:
        raise ParseError(f"Cannot read file: {e}", path)

    try:
        frontmatter, remaining = parse_frontmatter(content)
    except ParseError as e:
        # Re-raise with path context
        raise ParseError(str(e), path)

    # Extract domain and holon from frontmatter or path
    domain_str = frontmatter.get("domain", "")
    holon = frontmatter.get("holon", "")

    # Fallback: infer from path structure (spec/<domain>/<holon>.md)
    if not domain_str or not holon:
        parts = path.parts
        try:
            spec_idx = parts.index("spec")
            if len(parts) > spec_idx + 2:
                domain_str = domain_str or parts[spec_idx + 1]
                holon = holon or path.stem
        except ValueError:
            pass

    # Validate domain
    try:
        domain = SpecDomain(domain_str) if domain_str else SpecDomain.WORLD
    except ValueError:
        domain = SpecDomain.WORLD

    # Use filename as holon if not specified
    holon = holon or path.stem

    # Parse components
    polynomial = parse_polynomial(frontmatter.get("polynomial"))
    operad = parse_operad(frontmatter.get("operad"))
    sheaf = parse_sheaf(frontmatter.get("sheaf"))
    agentese = parse_agentese(frontmatter.get("agentese"))
    service = parse_service(frontmatter.get("service"))

    # Parse dependencies
    dependencies = frontmatter.get("dependencies", [])
    if isinstance(dependencies, str):
        dependencies = [d.strip() for d in dependencies.split(",")]

    return SpecNode(
        domain=domain,
        holon=holon,
        source_path=path,
        polynomial=polynomial,
        operad=operad,
        sheaf=sheaf,
        agentese=agentese,
        service=service,
        dependencies=dependencies,
        raw_content=remaining.strip(),
    )


# === Directory Parser ===


def parse_spec_directory(spec_root: Path) -> SpecGraph:
    """
    Parse all spec files in a directory into a SpecGraph.

    Args:
        spec_root: Root of the spec directory (e.g., kgents/spec/)

    Returns:
        SpecGraph containing all parsed specs
    """
    graph = SpecGraph()

    if not spec_root.exists():
        return graph

    # Find all markdown files
    for md_file in spec_root.rglob("*.md"):
        # Skip READMEs and index files
        if md_file.stem.lower() in ("readme", "index", "_index"):
            continue

        try:
            node = parse_spec_file(md_file)
            graph.add(node)
        except ParseError:
            # Skip unparseable files during development
            continue

    return graph


# === Spec Writer ===


def generate_frontmatter(node: SpecNode) -> str:
    """
    Generate YAML frontmatter from a SpecNode.

    This is the inverse of parse_frontmatter - used by Reflect functor.
    """
    data: dict[str, Any] = {
        "domain": node.domain.value,
        "holon": node.holon,
    }

    if node.polynomial:
        data["polynomial"] = {
            "positions": list(node.polynomial.positions),
            "transition": node.polynomial.transition_fn,
        }
        if node.polynomial.directions_fn:
            data["polynomial"]["directions"] = node.polynomial.directions_fn

    if node.operad:
        ops: dict[str, dict[str, Any]] = {}
        for op in node.operad.operations:
            op_data: dict[str, Any] = {"arity": op.arity}
            if op.signature:
                op_data["signature"] = op.signature
            if op.description:
                op_data["description"] = op.description
            if op.variadic:
                op_data["variadic"] = op.variadic
            ops[op.name] = op_data
        data["operad"] = {"operations": ops}

        if node.operad.laws:
            laws = {}
            for law in node.operad.laws:
                laws[law.name] = law.equation
            data["operad"]["laws"] = laws

        if node.operad.extends:
            data["operad"]["extends"] = node.operad.extends

    if node.sheaf:
        data["sheaf"] = {
            "sections": list(node.sheaf.sections),
            "gluing": node.sheaf.gluing_fn,
        }

    if node.agentese:
        agentese_data: dict[str, Any] = {"path": node.agentese.path}

        # Handle rich aspect specs if present
        if node.agentese.aspect_specs:
            aspects_list: list[Any] = []
            for aspect in node.agentese.aspect_specs:
                aspect_data: dict[str, Any] = {"name": aspect.name}
                if aspect.category != AspectCategory.PERCEPTION:
                    aspect_data["category"] = aspect.category.value
                if aspect.effects:
                    aspect_data["effects"] = list(aspect.effects)
                if aspect.help:
                    aspect_data["help"] = aspect.help
                aspects_list.append(aspect_data)
            agentese_data["aspects"] = aspects_list
        elif node.agentese.aspects:
            agentese_data["aspects"] = list(node.agentese.aspects)

        data["agentese"] = agentese_data

    if node.service:
        service_data: dict[str, Any] = {}
        if node.service.crown_jewel:
            service_data["crown_jewel"] = node.service.crown_jewel
        if node.service.adapters:
            service_data["adapters"] = list(node.service.adapters)
        if node.service.frontend:
            service_data["frontend"] = node.service.frontend
        if node.service.persistence:
            service_data["persistence"] = node.service.persistence
        if service_data:
            data["service"] = service_data

    if node.dependencies:
        data["dependencies"] = node.dependencies

    yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)
    return f"---\n{yaml_str}---\n"


# === Exports ===

__all__ = [
    # Errors
    "ParseError",
    # Parsers
    "parse_frontmatter",
    "parse_spec_file",
    "parse_spec_directory",
    # Writers
    "generate_frontmatter",
]
