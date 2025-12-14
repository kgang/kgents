"""
AGENTESE-Marimo Bridge

Connects AGENTESE handles to marimo cell reactivity.
The key insight: marimo's DAG IS AGENTESE reactivity.

When an observer changes, cells re-execute.
When a handle is invoked, results flow through the DAG.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

T = TypeVar("T")


@dataclass
class LogosCell:
    """
    Wrap an AGENTESE handle for marimo cell execution.

    The cell re-executes when the handle or observer changes,
    following marimo's reactive model.

    Example:
        cell = LogosCell("world.field.manifest")
        result = await cell(observer)  # Returns field state

        # In marimo:
        @app.cell
        def field_view():
            cell = LogosCell("world.field.manifest")
            return await cell(current_observer)
    """

    handle: str
    logos: Any = None  # Logos instance, lazily loaded
    _cache: dict[str, Any] = field(default_factory=dict)
    _cache_key: str = ""

    def __post_init__(self) -> None:
        """Lazily load logos if not provided."""
        if self.logos is None:
            try:
                from impl.claude.protocols.agentese.logos import create_logos

                self.logos = create_logos()
            except ImportError:
                # Running without full AGENTESE stack
                self.logos = None

    async def __call__(
        self,
        observer: Any = None,
        **kwargs: Any,
    ) -> Any:
        """
        Invoke the AGENTESE handle with the given observer.

        Args:
            observer: The observer's Umwelt (if None, uses default)
            **kwargs: Additional arguments passed to invoke

        Returns:
            Result of handle invocation
        """
        if self.logos is None:
            # Fallback for when AGENTESE is not available
            return {"handle": self.handle, "observer": str(observer), "status": "mock"}

        # Create cache key from observer identity
        observer_id = (
            getattr(observer, "id", str(id(observer))) if observer else "default"
        )
        cache_key = f"{self.handle}:{observer_id}"

        # Check cache (same observer = same result in reactive model)
        if cache_key == self._cache_key and cache_key in self._cache:
            return self._cache[cache_key]

        # Invoke handle
        result = await self.logos.invoke(self.handle, observer, **kwargs)

        # Cache result
        self._cache_key = cache_key
        self._cache[cache_key] = result

        return result

    def clear_cache(self) -> None:
        """Clear the result cache (forces re-execution)."""
        self._cache.clear()
        self._cache_key = ""


@dataclass
class ObserverState:
    """
    Marimo-compatible observer state container.

    Wraps an Umwelt-like observer for use in marimo cells.
    Changes to the observer trigger cell re-execution.

    Example:
        observer_state = ObserverState.create("architect")

        @app.cell
        def current_observer(observer_state):
            return observer_state.observer

        @app.cell
        def field_view(current_observer):
            cell = LogosCell("world.field.manifest")
            return await cell(current_observer)
    """

    observer_id: str = "default"
    observer_role: str = "viewer"
    capabilities: tuple[str, ...] = ()
    perturbation_count: int = 0

    @classmethod
    def create(
        cls,
        role: str = "viewer",
        observer_id: str | None = None,
        capabilities: tuple[str, ...] = (),
    ) -> "ObserverState":
        """Create an observer state with sensible defaults."""
        return cls(
            observer_id=observer_id or f"{role}_{id(cls)}",
            observer_role=role,
            capabilities=capabilities,
        )

    @property
    def observer(self) -> "MockUmwelt":
        """Get an Umwelt-like object for AGENTESE invocation."""
        return MockUmwelt(
            name=self.observer_id,
            archetype=self.observer_role,
            capabilities=self.capabilities,
        )

    def set_role(self, role: str) -> "ObserverState":
        """Create new state with updated role (immutable)."""
        return ObserverState(
            observer_id=self.observer_id,
            observer_role=role,
            capabilities=self.capabilities,
            perturbation_count=self.perturbation_count,
        )

    def perturb(self) -> "ObserverState":
        """Create new state that forces re-execution."""
        return ObserverState(
            observer_id=self.observer_id,
            observer_role=self.observer_role,
            capabilities=self.capabilities,
            perturbation_count=self.perturbation_count + 1,
        )


@dataclass
class MockUmwelt:
    """
    Minimal Umwelt-like object for use without full bootstrap stack.

    Provides the interface that Logos.invoke() expects.
    """

    name: str = "default"
    archetype: str = "viewer"
    capabilities: tuple[str, ...] = ()

    @property
    def dna(self) -> "MockUmwelt":
        """Return self as DNA (minimal interface)."""
        return self

    @property
    def id(self) -> str:
        """Return identifier."""
        return f"{self.archetype}_{self.name}"


@dataclass
class AffordanceButton:
    """
    Represents a clickable affordance in the UI.

    Can be rendered as a marimo button or Textual button.
    """

    handle: str  # Full AGENTESE path (e.g., "world.field.witness")
    name: str  # Display name (e.g., "witness")
    description: str = ""
    enabled: bool = True


def affordances_to_buttons(
    node_handle: str,
    affordances: list[str],
) -> list[AffordanceButton]:
    """
    Convert affordance list to button definitions.

    Args:
        node_handle: The base handle (e.g., "world.field")
        affordances: List of aspect names

    Returns:
        List of AffordanceButton objects
    """
    descriptions = {
        "manifest": "Collapse to observer's view",
        "witness": "Show history and traces",
        "refine": "Dialectical challenge",
        "sip": "Draw from Accursed Share",
        "tithe": "Pay for order (gratitude)",
        "lens": "Get composable agent",
        "define": "Create new entity",
        "affordances": "List available actions",
    }

    return [
        AffordanceButton(
            handle=f"{node_handle}.{aff}",
            name=aff,
            description=descriptions.get(aff, f"Invoke {aff}"),
            enabled=True,
        )
        for aff in affordances
    ]


def create_marimo_affordances(
    node_handle: str,
    affordances: list[str],
    on_click: Callable[[str], Any] | None = None,
) -> Any:
    """
    Create marimo UI buttons for affordances.

    Args:
        node_handle: The base handle
        affordances: List of aspect names
        on_click: Optional callback when button is clicked

    Returns:
        marimo hstack of buttons
    """
    try:
        import marimo as mo
    except ImportError:
        # Return plain data if marimo not available
        return affordances_to_buttons(node_handle, affordances)

    buttons: list[Any] = []
    for aff in affordances:
        full_handle = f"{node_handle}.{aff}"

        def make_handler(handle: str) -> Callable[[Any], Any] | None:
            if on_click:
                return lambda _: on_click(handle)
            return None

        btn = mo.ui.button(
            label=aff,
            on_click=make_handler(full_handle),
        )
        buttons.append(btn)

    return mo.hstack(buttons)


async def invoke_with_marimo_output(
    handle: str,
    observer: Any,
    logos: Any = None,
) -> Any:
    """
    Invoke an AGENTESE handle and format result for marimo display.

    Args:
        handle: Full AGENTESE path
        observer: Observer Umwelt
        logos: Logos instance (lazily created if None)

    Returns:
        marimo-formatted result (md, table, or raw value)
    """
    mo: Any = None
    try:
        import marimo as mo  # noqa: F811
    except ImportError:
        pass

    if logos is None:
        try:
            from impl.claude.protocols.agentese.logos import create_logos

            logos = create_logos()
        except ImportError:
            return {"handle": handle, "status": "logos_not_available"}

    result = await logos.invoke(handle, observer)

    if mo is None:
        return result

    # Format result based on type
    if isinstance(result, str):
        return mo.md(result)
    elif isinstance(result, dict):
        # Render as formatted markdown
        lines = [f"**{k}**: {v}" for k, v in result.items()]
        return mo.md("\n\n".join(lines))
    elif isinstance(result, list):
        if result and isinstance(result[0], dict):
            # Render as table
            return mo.ui.table(result)
        return mo.md(f"```\n{result}\n```")
    else:
        return mo.md(f"```\n{result}\n```")


# Convenience function for synchronous contexts
def invoke_sync(handle: str, observer: Any = None, logos: Any = None) -> Any:
    """
    Synchronous wrapper for AGENTESE invocation.

    Useful in marimo cells that don't use async/await.
    """
    cell = LogosCell(handle, logos)

    # Get or create event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if observer is None:
        observer = MockUmwelt()

    return loop.run_until_complete(cell(observer))
