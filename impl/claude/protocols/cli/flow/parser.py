"""
Flowfile Parser - YAML parsing with Jinja2 template support.

Parses flowfiles from YAML, validates structure, and renders
Jinja2 template variables.

From docs/cli-integration-plan.md Part 4.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .types import (
    Flowfile,
    FlowStep,
    FlowValidationError,
)

# =============================================================================
# Template Rendering
# =============================================================================


def render_template(template: str, variables: dict[str, Any]) -> str:
    """
    Render a Jinja2 template string with given variables.

    Uses simple regex-based rendering for common patterns to avoid
    requiring jinja2 as a hard dependency.

    Supports:
        {{ variable }}
        {{ variable | default('value') }}

    Args:
        template: Jinja2 template string
        variables: Variable values

    Returns:
        Rendered string
    """
    result = template

    # Pattern: {{ variable | default('value') }}
    default_pattern = (
        r"\{\{\s*(\w+)\s*\|\s*default\(['\"]([^'\"]*)['\"](?:\s*,\s*[^)]+)?\)\s*\}\}"
    )
    for match in re.finditer(default_pattern, template):
        var_name = match.group(1)
        default_value = match.group(2)
        value = variables.get(var_name, default_value)
        result = result.replace(match.group(0), str(value))

    # Pattern: {{ variable }}
    simple_pattern = r"\{\{\s*(\w+)\s*\}\}"
    for match in re.finditer(simple_pattern, result):
        var_name = match.group(1)
        value = variables.get(var_name, "")
        result = result.replace(match.group(0), str(value))

    return result


def render_flowfile(flowfile: Flowfile, variables: dict[str, Any]) -> Flowfile:
    """
    Render all template variables in a flowfile.

    Args:
        flowfile: Flowfile with template expressions
        variables: Variable values (merged with flowfile.variables)

    Returns:
        New Flowfile with templates rendered
    """
    # Merge provided variables with flowfile defaults
    merged_vars = {}

    # First, extract defaults from flowfile.variables
    for key, expr in flowfile.variables.items():
        # If the expression has a default, extract it
        if "default(" in expr:
            match = re.search(r"default\(['\"]([^'\"]*)['\"]", expr)
            if match:
                merged_vars[key] = match.group(1)

    # Override with provided variables
    merged_vars.update(variables)

    # Render step arguments
    rendered_steps = []
    for step in flowfile.steps:
        rendered_args = {}
        for key, value in step.args.items():
            if isinstance(value, str) and "{{" in value:
                rendered_args[key] = render_template(value, merged_vars)
            else:
                rendered_args[key] = value

        rendered_steps.append(
            FlowStep(
                id=step.id,
                genus=step.genus,
                operation=step.operation,
                input=step.input,
                args=rendered_args,
                condition=step.condition,
                on_error=step.on_error,
                timeout_ms=step.timeout_ms,
                debug=step.debug,
                snapshot=step.snapshot,
            )
        )

    # Create new flowfile with rendered values
    return Flowfile(
        version=flowfile.version,
        name=flowfile.name,
        description=flowfile.description,
        input=flowfile.input,
        output=flowfile.output,
        variables=flowfile.variables,
        steps=rendered_steps,
        hooks=flowfile.hooks,
        on_error=flowfile.on_error,
        source_path=flowfile.source_path,
    )


# =============================================================================
# YAML Parsing
# =============================================================================


def parse_flowfile(source: str | Path, content: str | None = None) -> Flowfile:
    """
    Parse a flowfile from YAML.

    Args:
        source: Path to flowfile or flow name
        content: Optional YAML content (if not provided, reads from source path)

    Returns:
        Parsed Flowfile

    Raises:
        FlowValidationError: If parsing fails
    """
    try:
        import yaml
    except ImportError:
        raise FlowValidationError(
            "PyYAML is required for flowfile parsing. Install with: pip install pyyaml"
        )

    source_path = str(source) if isinstance(source, Path) else source

    # Read content if not provided
    if content is None:
        path = Path(source_path)
        if not path.exists():
            raise FlowValidationError(f"Flowfile not found: {source_path}")
        if path.suffix not in (".yaml", ".yml", ".flow.yaml", ".flow.yml", ".flow"):
            raise FlowValidationError(
                f"Invalid flowfile extension: {path.suffix}. "
                "Expected .yaml, .yml, or .flow.yaml"
            )
        content = path.read_text()

    # Parse YAML
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise FlowValidationError(f"Invalid YAML: {e}")

    if not isinstance(data, dict):
        raise FlowValidationError("Flowfile must be a YAML mapping")

    # Parse into Flowfile
    try:
        return Flowfile.from_dict(data, source_path=source_path)
    except KeyError as e:
        raise FlowValidationError(f"Missing required field: {e}")
    except Exception as e:
        raise FlowValidationError(f"Failed to parse flowfile: {e}")


def parse_flowfile_string(content: str, name: str = "inline") -> Flowfile:
    """
    Parse a flowfile from a YAML string.

    Args:
        content: YAML content
        name: Flow name (for error messages)

    Returns:
        Parsed Flowfile
    """
    return parse_flowfile(name, content=content)


# =============================================================================
# Validation
# =============================================================================


def validate_flowfile(flowfile: Flowfile) -> list[str]:
    """
    Validate a flowfile for correctness.

    Returns list of validation errors (empty if valid).
    """
    errors: list[str] = []

    # Version check
    if flowfile.version not in ("1.0", "1.1"):
        errors.append(f"Unsupported version: {flowfile.version}")

    # Must have at least one step
    if not flowfile.steps:
        errors.append("Flowfile must have at least one step")

    # Check step IDs are unique
    step_ids = [step.id for step in flowfile.steps]
    seen = set()
    for step_id in step_ids:
        if step_id in seen:
            errors.append(f"Duplicate step ID: {step_id}")
        seen.add(step_id)

    # Check step references
    for step in flowfile.steps:
        if step.input and step.input.startswith("from:"):
            ref_id = step.input[5:]  # Strip "from:" prefix
            if ref_id not in step_ids:
                errors.append(f"Step '{step.id}' references unknown step: {ref_id}")

    # Check genus values
    valid_genera = {
        "P-gent",
        "J-gent",
        "G-gent",
        "L-gent",
        "W-gent",
        "T-gent",
        "A-gent",
        "B-gent",
        "C-gent",
        "D-gent",
        "F-gent",
        "H-gent",
        "I-gent",
        "K-gent",
        "R-gent",
        "Bootstrap",  # Also valid
    }
    for step in flowfile.steps:
        if step.genus not in valid_genera:
            errors.append(
                f"Step '{step.id}' has unknown genus: {step.genus}. "
                f"Valid genera: {', '.join(sorted(valid_genera))}"
            )

    # Check error handling strategy
    valid_strategies = {"halt", "continue", "retry", "skip"}
    if flowfile.on_error.strategy not in valid_strategies:
        errors.append(
            f"Invalid error handling strategy: {flowfile.on_error.strategy}. "
            f"Valid strategies: {', '.join(valid_strategies)}"
        )

    for step in flowfile.steps:
        if step.on_error not in valid_strategies:
            errors.append(f"Step '{step.id}' has invalid on_error: {step.on_error}")

    return errors


def validate_flowfile_strict(flowfile: Flowfile) -> None:
    """
    Validate a flowfile strictly, raising on first error.

    Raises:
        FlowValidationError: If validation fails
    """
    errors = validate_flowfile(flowfile)
    if errors:
        raise FlowValidationError(errors[0])


# =============================================================================
# Dependency Resolution
# =============================================================================


def build_dependency_graph(flowfile: Flowfile) -> dict[str, list[str]]:
    """
    Build a dependency graph for flow steps.

    Returns:
        Dict mapping step_id -> list of step_ids it depends on (unique)
    """
    import re

    graph: dict[str, list[str]] = {}

    for step in flowfile.steps:
        deps: set[str] = set()

        # Check input reference
        if step.input and step.input.startswith("from:"):
            ref_id = step.input[5:]
            deps.add(ref_id)

        # Check condition references (word boundary match to avoid false positives)
        # e.g., "parse.field" should match step "parse", but "should_refine" should not match "refine"
        if step.condition:
            for other_step in flowfile.steps:
                # Match step_id followed by . (dot) to indicate field access
                # e.g., "parse.success" matches "parse", but "should_refine" doesn't match "refine"
                pattern = r"\b" + re.escape(other_step.id) + r"\."
                if re.search(pattern, step.condition):
                    deps.add(other_step.id)

        graph[step.id] = list(deps)

    return graph


def topological_sort(flowfile: Flowfile) -> list[str]:
    """
    Compute execution order respecting dependencies.

    Returns:
        List of step IDs in execution order

    Raises:
        FlowValidationError: If circular dependency detected
    """
    # graph maps: step_id -> [list of step_ids this step depends on]
    graph = build_dependency_graph(flowfile)

    # in_degree: how many dependencies each step has (not how many depend on it)
    # A step with in_degree 0 has no dependencies and can run first
    in_degree = {step.id: len(graph.get(step.id, [])) for step in flowfile.steps}

    # Start with nodes that have no dependencies
    # Process in original order for tie-breaking
    queue = []
    for step in flowfile.steps:
        if in_degree[step.id] == 0:
            queue.append(step.id)

    result = []
    while queue:
        # Process first available (maintains original order when possible)
        node = queue.pop(0)
        result.append(node)

        # Find steps that depend on this node and decrement their in_degree
        for step_id, deps in graph.items():
            if node in deps:
                in_degree[step_id] -= 1
                if in_degree[step_id] == 0:
                    queue.append(step_id)

    if len(result) != len(flowfile.steps):
        # Circular dependency detected
        remaining = [s.id for s in flowfile.steps if s.id not in result]
        raise FlowValidationError(
            f"Circular dependency detected among steps: {', '.join(remaining)}"
        )

    return result


# =============================================================================
# Visualization
# =============================================================================


def visualize_flow(flowfile: Flowfile) -> str:
    """
    Generate ASCII visualization of flow pipeline.

    Example output:
        [parse] ──▶ [judge] ──▶ [refine]
                       │
                       └── condition: judge.verdict != 'APPROVED'
    """
    if not flowfile.steps:
        return "(empty flow)"

    lines = []

    # Build execution order
    try:
        order = topological_sort(flowfile)
    except FlowValidationError:
        order = [s.id for s in flowfile.steps]

    # Create step lookup
    step_lookup = {s.id: s for s in flowfile.steps}

    # Simple linear visualization
    step_boxes = []
    for step_id in order:
        step = step_lookup[step_id]
        box = f"[{step.id}]"
        if step.debug:
            box += "*"  # Debug marker
        step_boxes.append(box)

    # Main pipeline line
    lines.append(" ──▶ ".join(step_boxes))

    # Add condition annotations
    for step_id in order:
        step = step_lookup[step_id]
        if step.condition:
            lines.append(f"      └── {step.id}: condition: {step.condition}")
        if step.input and step.input.startswith("from:"):
            ref = step.input[5:]
            lines.append(f"      └── {step.id}: input from {ref}")

    return "\n".join(lines)


def explain_flow(flowfile: Flowfile) -> str:
    """
    Generate human-readable explanation of flow.

    Example output:
        Flow: Code Review Pipeline
        Description: Parse, judge, and refine code

        Steps:
          1. [parse] P-gent.extract
             → Extract structure from input

          2. [judge] Bootstrap.judge
             Input: from parse
             Args: principles=spec/principles.md, strictness=high

          3. [refine] R-gent.optimize
             Input: from judge
             Condition: judge.verdict != 'APPROVED'
    """
    lines = []

    # Header
    lines.append(f"Flow: {flowfile.name or '(unnamed)'}")
    if flowfile.description:
        lines.append(f"Description: {flowfile.description}")
    lines.append("")

    # Input
    lines.append(f"Input: {flowfile.input.type}")
    if flowfile.input.extensions:
        lines.append(f"  Extensions: {', '.join(flowfile.input.extensions)}")
    lines.append("")

    # Variables
    if flowfile.variables:
        lines.append("Variables:")
        for name, expr in flowfile.variables.items():
            lines.append(f"  {name}: {expr}")
        lines.append("")

    # Steps
    lines.append("Steps:")
    for i, step in enumerate(flowfile.steps, 1):
        lines.append(f"  {i}. [{step.id}] {step.genus}.{step.operation}")

        if step.input:
            lines.append(f"     Input: {step.input}")

        if step.args:
            args_str = ", ".join(f"{k}={v}" for k, v in step.args.items())
            lines.append(f"     Args: {args_str}")

        if step.condition:
            lines.append(f"     Condition: {step.condition}")

        if step.debug:
            lines.append("     Debug: enabled")

        lines.append("")

    # Error handling
    lines.append(f"On Error: {flowfile.on_error.strategy}")
    if flowfile.on_error.max_retries > 1:
        lines.append(f"  Max Retries: {flowfile.on_error.max_retries}")

    return "\n".join(lines)
