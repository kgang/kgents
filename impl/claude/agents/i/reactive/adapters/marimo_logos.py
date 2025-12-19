"""
LogosCell: AGENTESE REPL for marimo notebooks.

Wave 3 marimo deep integration.

The LogosCell bridges AGENTESE paths to marimo cells:
    logos_cell = LogosCell(logos)
    result = await logos_cell.invoke("world.agent.manifest", umwelt)
    mo.Html(result)

Key insight from meta.md:
> marimo LogosCell pattern IS AgenteseBridge pattern—direct mapping, no adapter layer needed

This means:
1. AGENTESE paths work directly in marimo cells
2. Widget projections render as mo.Html
3. Reactivity (Signal dependencies) maps to marimo's cell dependencies

Usage in marimo notebook:
    @app.cell
    async def agent_view(mo, logos_cell, umwelt):
        result = await logos_cell.invoke("world.agent.manifest", umwelt)
        return mo.Html(result)
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from agents.i.reactive.widget import RenderTarget

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.agentese.logos import Logos


@dataclass
class LogosCellResult:
    """
    Result of a LogosCell invocation.

    Provides multiple rendering options:
    - html: HTML string for mo.Html
    - json: JSON dict for mo.Json
    - cli: CLI string for debugging
    - raw: The raw result from Logos.invoke
    """

    raw: Any
    path: str
    html: str = ""
    json: dict[str, Any] = field(default_factory=dict)
    cli: str = ""
    error: str | None = None

    def _repr_html_(self) -> str:
        """Jupyter/marimo HTML representation."""
        if self.error:
            return f'<div class="logos-error" style="color: red; padding: 8px; border: 1px solid red; border-radius: 4px;"><strong>Error:</strong> {self.error}</div>'
        return self.html

    def __str__(self) -> str:
        """CLI representation."""
        if self.error:
            return f"Error: {self.error}"
        return self.cli or str(self.raw)


@dataclass
class LogosCell:
    """
    AGENTESE REPL cell for marimo notebooks.

    Wraps a Logos instance and provides marimo-compatible invocation.

    Example:
        from protocols.agentese.logos import Logos, create_default_logos
        from agents.i.reactive.adapters.marimo_logos import LogosCell

        logos = create_default_logos()
        cell = LogosCell(logos)

        # In marimo @app.cell
        result = await cell.invoke("self.soul.manifest", umwelt)
        mo.Html(result.html)

    The LogosCell automatically:
    1. Invokes the AGENTESE path with the observer
    2. Projects the result to multiple targets (HTML, JSON, CLI)
    3. Returns a LogosCellResult for flexible rendering

    Attributes:
        logos: The AGENTESE Logos resolver
        default_target: Default render target for widgets
        auto_project: Whether to auto-project KgentsWidgets
    """

    logos: "Logos"
    default_target: RenderTarget = RenderTarget.MARIMO
    auto_project: bool = True

    async def invoke(
        self,
        path: str,
        observer: "Umwelt[Any, Any]",
        *,
        input: Any = None,
        target: RenderTarget | None = None,
    ) -> LogosCellResult:
        """
        Invoke an AGENTESE path and return marimo-compatible result.

        Args:
            path: AGENTESE path (e.g., "world.agent.manifest")
            observer: The observer's Umwelt (REQUIRED)
            input: Optional input for pipeline composition
            target: Override render target (default: MARIMO)

        Returns:
            LogosCellResult with html, json, cli, and raw fields
        """
        target = target or self.default_target

        try:
            # Invoke the AGENTESE path
            raw_result = await self.logos.invoke(path, observer, input=input)

            # Project to different targets
            html = self._project_to_html(raw_result, target)
            json_dict = self._project_to_json(raw_result)
            cli = self._project_to_cli(raw_result)

            return LogosCellResult(
                raw=raw_result,
                path=path,
                html=html,
                json=json_dict,
                cli=cli,
            )
        except Exception as e:
            return LogosCellResult(
                raw=None,
                path=path,
                error=str(e),
            )

    def invoke_sync(
        self,
        path: str,
        observer: "Umwelt[Any, Any]",
        *,
        input: Any = None,
        target: RenderTarget | None = None,
    ) -> LogosCellResult:
        """
        Synchronous invoke for non-async marimo cells.

        Creates an event loop if needed for sync execution.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In async context, use nest_asyncio pattern or return coroutine
                import nest_asyncio  # type: ignore[import-not-found]

                nest_asyncio.apply()
                return loop.run_until_complete(
                    self.invoke(path, observer, input=input, target=target)
                )
            return loop.run_until_complete(self.invoke(path, observer, input=input, target=target))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(self.invoke(path, observer, input=input, target=target))
        except ImportError:
            # nest_asyncio not available, return error
            return LogosCellResult(
                raw=None,
                path=path,
                error="nest_asyncio required for sync invoke in async context",
            )

    def _project_to_html(self, result: Any, target: RenderTarget) -> str:
        """Project result to HTML string."""
        from agents.i.reactive.widget import KgentsWidget

        # Check for KgentsWidget
        if isinstance(result, KgentsWidget):
            return str(result.project(target))

        # Check for composable widgets (HStack, VStack)
        if hasattr(result, "project"):
            return str(result.project(target))

        # Check for _repr_html_ (marimo/Jupyter protocol)
        if hasattr(result, "_repr_html_"):
            return str(result._repr_html_())

        # Fallback: wrap in pre tag
        return f"<pre>{self._escape_html(str(result))}</pre>"

    def _project_to_json(self, result: Any) -> dict[str, Any]:
        """Project result to JSON dict."""
        from agents.i.reactive.widget import KgentsWidget

        # Check for KgentsWidget
        if isinstance(result, KgentsWidget):
            projection = result.project(RenderTarget.JSON)
            if isinstance(projection, dict):
                return projection
            return {"value": projection}

        # Check for composable widgets
        if hasattr(result, "project"):
            projection = result.project(RenderTarget.JSON)
            if isinstance(projection, dict):
                return projection
            return {"value": projection}

        # Fallback
        if isinstance(result, dict):
            return result
        return {"value": str(result)}

    def _project_to_cli(self, result: Any) -> str:
        """Project result to CLI string."""
        from agents.i.reactive.widget import KgentsWidget

        # Check for KgentsWidget
        if isinstance(result, KgentsWidget):
            return str(result.project(RenderTarget.CLI))

        # Check for composable widgets
        if hasattr(result, "project"):
            return str(result.project(RenderTarget.CLI))

        return str(result)

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def path(self, path: str) -> "LogosCellPath":
        """
        Create a reusable path object for repeated invocations.

        Example:
            manifest = cell.path("world.agent.manifest")
            result = await manifest(umwelt)
        """
        return LogosCellPath(self, path)

    def __rshift__(self, path: str) -> "LogosCellPath":
        """
        Fluent path creation: cell >> "world.agent.manifest"
        """
        return self.path(path)


@dataclass
class LogosCellPath:
    """
    A bound AGENTESE path for repeated invocations.

    Created via LogosCell.path() or >> operator.
    """

    cell: LogosCell
    path: str

    async def __call__(
        self,
        observer: "Umwelt[Any, Any]",
        *,
        input: Any = None,
        target: RenderTarget | None = None,
    ) -> LogosCellResult:
        """Invoke this path."""
        return await self.cell.invoke(self.path, observer, input=input, target=target)

    def __rshift__(self, other: str) -> "LogosCellPath":
        """Compose paths: path >> "other.path" """
        return LogosCellPath(self.cell, f"{self.path} >> {other}")


def create_logos_cell(
    logos: "Logos | None" = None,
    *,
    default_target: RenderTarget = RenderTarget.MARIMO,
    auto_project: bool = True,
) -> LogosCell:
    """
    Create a LogosCell for marimo notebooks.

    Args:
        logos: Logos instance (creates default if None)
        default_target: Default render target
        auto_project: Whether to auto-project KgentsWidgets

    Returns:
        LogosCell configured for marimo use

    Example:
        from agents.i.reactive.adapters.marimo_logos import create_logos_cell

        cell = create_logos_cell()

        # In marimo
        @app.cell
        async def view(mo, cell, umwelt):
            result = await cell.invoke("self.soul.manifest", umwelt)
            return mo.Html(result)
    """
    if logos is None:
        # Create default logos with standard contexts
        from protocols.agentese.logos import Logos

        logos = Logos()

    return LogosCell(
        logos=logos,
        default_target=default_target,
        auto_project=auto_project,
    )


# Export for adapters __init__.py
__all__ = [
    "LogosCell",
    "LogosCellPath",
    "LogosCellResult",
    "create_logos_cell",
]
