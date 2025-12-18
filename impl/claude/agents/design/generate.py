"""
Generative UI: Functor from DESIGN_OPERAD to JSX.

This module bridges the gap between categorical composition (Layer 2-3)
and actual React components (Layer 7).

The functor maps:
    DESIGN_OPERAD operation × ComponentSpec* → JSX string

This is the missing piece identified in the Honesty Audit (Session 5):
operads compose PolyAgent instances, but we need to generate actual UI.

Usage:
    from agents.design.generate import generate_component, ComponentSpec

    canvas = ComponentSpec(name="Canvas", type="div", props={"className": "canvas"})
    drawer = ComponentSpec(name="Drawer", type="BottomDrawer", props={"open": True})

    jsx = generate_component(LAYOUT_OPERAD, "split", canvas, drawer)
    # Returns: '<ElasticSplit primary={<Canvas />} secondary={<BottomDrawer open={true} />} />'

Limitations:
    - Generates string JSX, not actual React elements
    - No runtime validation of props
    - Component types must be valid React component names
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .operad import CONTENT_OPERAD, DESIGN_OPERAD, LAYOUT_OPERAD, MOTION_OPERAD, Operad
from .types import ContentLevel, Density, MotionType

# =============================================================================
# Component Specification
# =============================================================================


@dataclass(frozen=True)
class ComponentSpec:
    """
    Specification for a React component.

    This is the domain type that the generative functor operates on.
    It captures enough information to generate JSX.
    """

    name: str
    type: str  # React component type (e.g., "div", "Button", "Canvas")
    props: dict[str, Any] = field(default_factory=dict)
    children: tuple["ComponentSpec", ...] = ()

    def to_jsx(self, depth: int = 0) -> str:
        """
        Render this spec as JSX.

        Args:
            depth: Indentation depth for pretty printing

        Returns:
            JSX string representation
        """
        indent = "  " * depth

        # Format props
        prop_strs = []
        for key, value in self.props.items():
            prop_strs.append(_format_prop(key, value))
        props_str = " ".join(prop_strs)
        if props_str:
            props_str = " " + props_str

        # Self-closing if no children
        if not self.children:
            return f"{indent}<{self.type}{props_str} />"

        # With children
        child_strs = [child.to_jsx(depth + 1) for child in self.children]
        children_str = "\n".join(child_strs)

        return f"{indent}<{self.type}{props_str}>\n{children_str}\n{indent}</{self.type}>"


def _format_prop(key: str, value: Any) -> str:
    """Format a prop for JSX."""
    if isinstance(value, bool):
        return f"{key}={{{str(value).lower()}}}"
    if isinstance(value, str):
        return f'{key}="{value}"'
    if isinstance(value, (int, float)):
        return f"{key}={{{value}}}"
    if isinstance(value, ComponentSpec):
        # Render nested component
        return f"{key}={{<{value.type} />}}"
    # Default: JSON-like
    return f"{key}={{{value!r}}}"


# =============================================================================
# Operation to Component Mapping
# =============================================================================


# Map LAYOUT_OPERAD operations to React component types
LAYOUT_COMPONENT_MAP: dict[str, str] = {
    "split": "ElasticSplit",
    "stack": "ElasticContainer",
    "drawer": "BottomDrawer",
    "float": "FloatingActions",
}

# Map MOTION_OPERAD operations to animation wrappers
MOTION_COMPONENT_MAP: dict[str, str] = {
    "identity": "",  # No wrapper
    "breathe": "motion.div",  # framer-motion style
    "pop": "motion.div",
    "shake": "motion.div",
    "shimmer": "motion.div",
}


# =============================================================================
# Generation Functions
# =============================================================================


def generate_component(
    operad: Operad,
    operation: str,
    *children: ComponentSpec,
    density: Density | None = None,
    motion: MotionType | None = None,
) -> str:
    """
    Generate JSX from an operad operation and component specs.

    This is the core functor: DESIGN_OPERAD × ComponentSpec* → JSX

    Args:
        operad: The operad containing the operation
        operation: Name of the operation to apply
        *children: Component specs to compose
        density: Optional density context (affects layout)
        motion: Optional motion type (affects animation wrapper)

    Returns:
        JSX string for the composed component

    Raises:
        KeyError: If operation not found in operad
        ValueError: If wrong number of children for operation

    Example:
        >>> canvas = ComponentSpec("Canvas", "div", {"className": "canvas"})
        >>> drawer = ComponentSpec("Drawer", "BottomDrawer", {"open": True})
        >>> jsx = generate_component(LAYOUT_OPERAD, "split", canvas, drawer)
        >>> print(jsx)
        <ElasticSplit primary={<Canvas />} secondary={<BottomDrawer open={true} />} />
    """
    op = operad.get(operation)
    if op is None:
        raise KeyError(f"Unknown operation: {operation} in {operad.name}")

    # Validate arity (except for variadic operations with arity=-1)
    if op.arity >= 0 and len(children) != op.arity:
        raise ValueError(
            f"Operation '{operation}' requires {op.arity} children, got {len(children)}"
        )

    # Dispatch to appropriate generator based on operad
    if operad.name == "LAYOUT" or operation in LAYOUT_COMPONENT_MAP:
        return _generate_layout(operation, children, density)

    if operad.name == "CONTENT" or operation in ("degrade", "compose"):
        return _generate_content(operation, children)

    if operad.name == "MOTION" or operation in MOTION_COMPONENT_MAP:
        return _generate_motion(operation, children, motion)

    # For DESIGN_OPERAD, detect sub-operad by operation name
    if operation in LAYOUT_COMPONENT_MAP:
        return _generate_layout(operation, children, density)
    if operation in ("degrade", "compose"):
        return _generate_content(operation, children)
    if operation in MOTION_COMPONENT_MAP:
        return _generate_motion(operation, children, motion)

    # Fallback: generic composition
    return _generate_generic(operation, children)


def _generate_layout(
    operation: str,
    children: tuple[ComponentSpec, ...],
    density: Density | None = None,
) -> str:
    """Generate layout composition JSX."""
    component_type = LAYOUT_COMPONENT_MAP.get(operation, "div")

    match operation:
        case "split":
            if len(children) < 2:
                raise ValueError("split requires 2 children")
            primary, secondary = children[0], children[1]

            # At compact density, split collapses to drawer
            if density == Density.COMPACT:
                return _generate_layout_compact_split(primary, secondary)

            return (
                f"<{component_type}\n"
                f"  primary={{<{primary.type} />}}\n"
                f"  secondary={{<{secondary.type} />}}\n"
                f"/>"
            )

        case "stack":
            child_elements = " ".join(f"<{c.type} />" for c in children)
            direction = "column"  # Default, would be parameterized
            return f'<{component_type} direction="{direction}">{child_elements}</{component_type}>'

        case "drawer":
            if len(children) < 2:
                raise ValueError("drawer requires 2 children (trigger, content)")
            trigger, content = children[0], children[1]
            return (
                f"<{component_type}\n"
                f"  trigger={{<{trigger.type} />}}\n"
                f"  content={{<{content.type} />}}\n"
                f"/>"
            )

        case "float":
            action_elements = " ".join(f"<{c.type} />" for c in children)
            return f"<{component_type}>{action_elements}</{component_type}>"

        case _:
            return _generate_generic(operation, children)


def _generate_layout_compact_split(
    primary: ComponentSpec,
    secondary: ComponentSpec,
) -> str:
    """
    At compact density, split collapses to drawer pattern.

    This implements the law: split(a, b) ≅ drawer(a, b) at compact
    """
    return f"<BottomDrawer\n  main={{<{primary.type} />}}\n  drawer={{<{secondary.type} />}}\n/>"


def _generate_content(
    operation: str,
    children: tuple[ComponentSpec, ...],
) -> str:
    """Generate content operation JSX."""
    match operation:
        case "degrade":
            if len(children) < 2:
                raise ValueError("degrade requires 2 children (full, level)")
            full, level = children[0], children[1]
            # The level child is interpreted as content level indicator
            return f'<ContentWrapper level="{level.name}"><{full.type} /></ContentWrapper>'

        case "compose":
            child_elements = " ".join(f"<{c.type} />" for c in children)
            return f"<ContentComposition>{child_elements}</ContentComposition>"

        case _:
            return _generate_generic(operation, children)


def _generate_motion(
    operation: str,
    children: tuple[ComponentSpec, ...],
    motion_type: MotionType | None = None,
) -> str:
    """Generate motion-wrapped JSX."""
    if not children:
        raise ValueError(f"Motion operation '{operation}' requires at least 1 child")

    MOTION_COMPONENT_MAP.get(operation, "")

    match operation:
        case "identity":
            # No wrapper, just render children
            return children[0].to_jsx()

        case "breathe":
            return _wrap_with_motion(
                children[0],
                "breathe",
                {
                    "animate": {"scale": [1, 1.02, 1]},
                    "transition": {"duration": 2, "repeat": "Infinity"},
                },
            )

        case "pop":
            return _wrap_with_motion(
                children[0],
                "pop",
                {
                    "whileHover": {"scale": 1.05},
                    "whileTap": {"scale": 0.95},
                },
            )

        case "shake":
            return _wrap_with_motion(
                children[0],
                "shake",
                {
                    "animate": {"x": [-2, 2, -2, 0]},
                    "transition": {"duration": 0.3},
                },
            )

        case "shimmer":
            return _wrap_with_motion(
                children[0],
                "shimmer",
                {
                    "animate": {"backgroundPosition": ["0% 0%", "100% 100%"]},
                },
            )

        case "chain":
            if len(children) < 2:
                raise ValueError("chain requires 2 children")
            first, second = children[0], children[1]
            # Sequential animation: first then second
            return (
                f'<AnimatePresence mode="wait">\n'
                f"  {first.to_jsx(1)}\n"
                f"  {second.to_jsx(1)}\n"
                f"</AnimatePresence>"
            )

        case "parallel":
            if len(children) < 2:
                raise ValueError("parallel requires 2 children")
            # Both animate simultaneously
            child_strs = [c.to_jsx(1) for c in children]
            return "<motion.div layout>\n" + "\n".join(child_strs) + "\n</motion.div>"

        case _:
            return _generate_generic(operation, children)


def _wrap_with_motion(
    spec: ComponentSpec,
    effect: str,
    props: dict[str, Any],
) -> str:
    """Wrap a component with framer-motion animation."""
    prop_strs = []
    for key, value in props.items():
        prop_strs.append(f"{key}={{{value!r}}}")
    props_str = "\n    ".join(prop_strs)

    return (
        f"<motion.div\n"
        f'    data-motion="{effect}"\n'
        f"    {props_str}\n"
        f">\n"
        f"  {spec.to_jsx(1)}\n"
        f"</motion.div>"
    )


def _generate_generic(
    operation: str,
    children: tuple[ComponentSpec, ...],
) -> str:
    """Fallback generic composition."""
    child_strs = [c.to_jsx(1) for c in children]
    children_str = "\n".join(child_strs)

    return f'<ComposedElement operation="{operation}">\n{children_str}\n</ComposedElement>'


# =============================================================================
# Convenience Functions
# =============================================================================


def generate_split(
    primary: ComponentSpec,
    secondary: ComponentSpec,
    density: Density = Density.SPACIOUS,
) -> str:
    """
    Generate a split layout.

    Shorthand for generate_component(LAYOUT_OPERAD, "split", ...).

    At compact density, automatically degrades to drawer.
    """
    return generate_component(LAYOUT_OPERAD, "split", primary, secondary, density=density)


def generate_stack(*children: ComponentSpec) -> str:
    """Generate a stack layout."""
    return generate_component(LAYOUT_OPERAD, "stack", *children)


def generate_drawer(trigger: ComponentSpec, content: ComponentSpec) -> str:
    """Generate a drawer layout."""
    return generate_component(LAYOUT_OPERAD, "drawer", trigger, content)


def with_motion(spec: ComponentSpec, motion: MotionType) -> str:
    """Wrap a component with motion animation."""
    return generate_component(MOTION_OPERAD, motion.value, spec, motion=motion)


__all__ = [
    # Core types
    "ComponentSpec",
    # Main generator
    "generate_component",
    # Convenience functions
    "generate_split",
    "generate_stack",
    "generate_drawer",
    "with_motion",
    # Maps (for extension)
    "LAYOUT_COMPONENT_MAP",
    "MOTION_COMPONENT_MAP",
]
