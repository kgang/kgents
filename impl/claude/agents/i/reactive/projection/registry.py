"""
ProjectionRegistry: Central registry for target-specific projectors.

The registry enables:
1. Decorator-based registration of new targets
2. Lookup with graceful degradation
3. Capability querying
4. Extension without modifying core widget code

Design Principles:
    - Singleton pattern for global registry (with test isolation support)
    - Decorator syntax for ergonomic registration
    - Graceful degradation: unknown targets fall back to JSON
    - Type-safe projector signatures

Example:
    # Register a new target
    @ProjectionRegistry.register("webgl")
    def webgl_projector(widget: KgentsWidget, **opts) -> ThreeScene:
        return convert_to_threejs(widget.state.value)

    # Use the target
    result = ProjectionRegistry.project(my_widget, "webgl")

    # Graceful degradation
    result = ProjectionRegistry.project(my_widget, "unknown_target")
    # Falls back to JSON projection
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from agents.i.reactive.projection.targets import (
    ExtendedTarget,
    FidelityLevel,
    TargetCapability,
    target_capabilities,
)

if TYPE_CHECKING:
    from agents.i.reactive.widget import KgentsWidget

W = TypeVar("W", bound="KgentsWidget[Any]")

# Type alias for projector functions
ProjectorFn = Callable[["KgentsWidget[Any]"], Any]


@dataclass(frozen=True)
class Projector:
    """
    A registered projector with metadata.

    Attributes:
        name: Target name (e.g., "webgl", "audio")
        fn: The projection function
        target: ExtendedTarget enum value (if standard target)
        fidelity: Information preservation level (0.0-1.0)
        description: Human-readable description
    """

    name: str
    fn: ProjectorFn
    target: ExtendedTarget | None = None
    fidelity: float = 0.5
    description: str = ""


@dataclass
class ProjectionRegistry:
    """
    Central registry for projection targets.

    The registry is a singleton accessed via class methods.
    For testing, use `reset()` to clear custom registrations.

    Class Methods:
        register(name, **opts) - Decorator to register a projector
        project(widget, target) - Project widget to target
        get(name) - Get projector by name
        all_targets() - List all registered targets
        supports(name) - Check if target is registered
        reset() - Clear custom registrations (for testing)

    Thread Safety:
        The registry is NOT thread-safe. For concurrent use, ensure
        all registrations happen at import time before concurrent access.
    """

    # Class-level registry (singleton)
    _projectors: dict[str, Projector] = field(default_factory=dict)
    _instance: "ProjectionRegistry | None" = None

    @classmethod
    def _get_instance(cls) -> "ProjectionRegistry":
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls(_projectors={}, _instance=None)
            cls._register_builtins()
        return cls._instance

    @classmethod
    def _register_builtins(cls) -> None:
        """Register the built-in targets from ExtendedTarget."""
        instance = cls._instance
        if instance is None:
            return

        # Built-in targets use widget.project() directly
        for target in [
            ExtendedTarget.CLI,
            ExtendedTarget.TUI,
            ExtendedTarget.MARIMO,
            ExtendedTarget.JSON,
        ]:
            caps = target_capabilities(target)
            instance._projectors[target.name.lower()] = Projector(
                name=target.name.lower(),
                fn=cls._make_builtin_projector(target),
                target=target,
                fidelity=caps.fidelity,
                description=f"Built-in {target.name} projection",
            )

        # SSE is a special case - widgets must implement to_sse()
        sse_caps = target_capabilities(ExtendedTarget.SSE)
        instance._projectors["sse"] = Projector(
            name="sse",
            fn=cls._make_sse_projector(),
            target=ExtendedTarget.SSE,
            fidelity=sse_caps.fidelity,
            description="Server-Sent Events streaming projection",
        )

    @classmethod
    def _make_builtin_projector(cls, target: ExtendedTarget) -> ProjectorFn:
        """Create a projector that delegates to widget.project()."""
        from agents.i.reactive.widget import RenderTarget

        # Map ExtendedTarget back to RenderTarget for built-ins
        render_target_map = {
            ExtendedTarget.CLI: RenderTarget.CLI,
            ExtendedTarget.TUI: RenderTarget.TUI,
            ExtendedTarget.MARIMO: RenderTarget.MARIMO,
            ExtendedTarget.JSON: RenderTarget.JSON,
        }

        render_target = render_target_map.get(target)
        if render_target is None:
            # Fallback for non-core targets
            return lambda w: w.project(RenderTarget.JSON)

        return lambda w: w.project(render_target)

    @classmethod
    def _make_sse_projector(cls) -> ProjectorFn:
        """Create SSE projector that delegates to to_sse() if available."""

        def sse_project(widget: KgentsWidget[Any]) -> Any:
            if hasattr(widget, "to_sse"):
                return widget.to_sse()
            # Fallback: wrap JSON in SSE format
            import json

            data = widget.to_json()
            return f"data: {json.dumps(data)}\n\n"

        return sse_project

    @classmethod
    def register(
        cls,
        name: str,
        *,
        fidelity: float = 0.5,
        description: str = "",
    ) -> Callable[[ProjectorFn], ProjectorFn]:
        """
        Decorator to register a custom projector.

        Args:
            name: Target name (e.g., "webgl", "audio")
            fidelity: Information preservation level (0.0-1.0)
            description: Human-readable description

        Returns:
            Decorator function

        Example:
            @ProjectionRegistry.register("webgl", fidelity=0.9)
            def webgl_projector(widget: KgentsWidget) -> ThreeScene:
                return convert_to_threejs(widget.state.value)
        """
        instance = cls._get_instance()

        def decorator(fn: ProjectorFn) -> ProjectorFn:
            # Check if this is a known ExtendedTarget
            target = None
            try:
                target = ExtendedTarget[name.upper()]
            except KeyError:
                pass

            projector = Projector(
                name=name.lower(),
                fn=fn,
                target=target,
                fidelity=fidelity,
                description=description or f"Custom {name} projection",
            )
            instance._projectors[name.lower()] = projector
            return fn

        return decorator

    @classmethod
    def project(
        cls,
        widget: "KgentsWidget[Any]",
        target: str | ExtendedTarget,
        *,
        fallback: str = "json",
    ) -> Any:
        """
        Project a widget to a target.

        Args:
            widget: The widget to project
            target: Target name or ExtendedTarget enum
            fallback: Fallback target if primary not found (default: json)

        Returns:
            Projected representation

        Raises:
            ValueError: If neither target nor fallback is registered

        Example:
            result = ProjectionRegistry.project(my_widget, "webgl")
            result = ProjectionRegistry.project(my_widget, ExtendedTarget.CLI)
        """
        instance = cls._get_instance()

        # Normalize target to string
        target_name = (
            target.name.lower()
            if isinstance(target, ExtendedTarget)
            else target.lower()
        )

        # Try primary target
        projector = instance._projectors.get(target_name)
        if projector is not None:
            return projector.fn(widget)

        # Try fallback
        fallback_projector = instance._projectors.get(fallback.lower())
        if fallback_projector is not None:
            return fallback_projector.fn(widget)

        raise ValueError(
            f"Unknown projection target: {target_name} (and fallback {fallback} not found)"
        )

    @classmethod
    def get(cls, name: str) -> Projector | None:
        """
        Get a registered projector by name.

        Args:
            name: Target name

        Returns:
            Projector if found, None otherwise
        """
        instance = cls._get_instance()
        return instance._projectors.get(name.lower())

    @classmethod
    def all_targets(cls) -> list[str]:
        """
        List all registered target names.

        Returns:
            Sorted list of target names
        """
        instance = cls._get_instance()
        return sorted(instance._projectors.keys())

    @classmethod
    def supports(cls, name: str) -> bool:
        """
        Check if a target is registered.

        Args:
            name: Target name

        Returns:
            True if target is registered
        """
        instance = cls._get_instance()
        return name.lower() in instance._projectors

    @classmethod
    def by_fidelity(cls, level: FidelityLevel) -> list[Projector]:
        """
        Get projectors matching a fidelity level.

        Args:
            level: Desired fidelity level

        Returns:
            List of projectors at that level, sorted by fidelity descending
        """
        instance = cls._get_instance()

        thresholds = {
            FidelityLevel.MAXIMUM: (0.9, 1.0),
            FidelityLevel.HIGH: (0.7, 0.9),
            FidelityLevel.MEDIUM: (0.4, 0.7),
            FidelityLevel.LOW: (0.0, 0.4),
            FidelityLevel.LOSSLESS: (1.0, 1.0),
        }

        low, high = thresholds[level]
        matches = [
            p for p in instance._projectors.values() if low <= p.fidelity <= high
        ]
        return sorted(matches, key=lambda p: p.fidelity, reverse=True)

    @classmethod
    def reset(cls) -> None:
        """
        Reset registry to built-in targets only.

        Use this in tests to ensure isolation:

            def test_my_projector():
                ProjectionRegistry.reset()
                # ... register and test custom projector
                ProjectionRegistry.reset()  # cleanup
        """
        cls._instance = None
        cls._get_instance()  # Re-initialize with builtins


__all__ = [
    "ProjectionRegistry",
    "Projector",
    "ProjectorFn",
    "FidelityLevel",
]
