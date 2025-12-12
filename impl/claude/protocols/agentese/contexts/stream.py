"""
AGENTESE Stream Context Resolver: self.stream.*

The context management subsystem - providing comonadic operations
on the agent's conversation context.

self.stream.* handles resolve to context window operations:
- self.stream.focus   -> extract() - Get current turn
- self.stream.map     -> extend()  - Apply function at each position
- self.stream.seek    -> seek()    - Move focus position
- self.stream.project -> compress() - Galois Connection compression
- self.stream.linearity -> LinearityMap operations

Category Theory:
- ContextWindow is a Store Comonad
- ContextProjector is a Galois Connection (NOT a Lens)
- LinearityMap tracks resource classes (DROPPABLE < REQUIRED < PRESERVED)

AGENTESE: self.stream.*
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from agents.d.context_window import (
    ContextWindow,
    Turn,
    TurnRole,
    create_context_window,
)
from agents.d.linearity import LinearityMap, ResourceClass
from agents.d.projector import (
    AdaptiveThreshold,
    CompressionResult,
    ContextProjector,
    create_projector,
)

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Stream Affordances ===

STREAM_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "focus": ("extract", "peek"),
    "map": ("extend", "transform"),
    "seek": ("position", "forward", "backward", "start", "end"),
    "project": ("compress", "threshold", "stats"),
    "linearity": ("tag", "promote", "drop", "stats"),
    "pressure": ("check", "auto_compress"),
}


# === Stream Focus Node ===


@dataclass
class StreamFocusNode(BaseLogosNode):
    """
    self.stream.focus - Get current context focus.

    Provides comonadic extract() operation.
    """

    _handle: str = "self.stream.focus"
    _window: ContextWindow | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return STREAM_AFFORDANCES["focus"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show current focus."""
        if self._window is None:
            return BasicRendering(
                summary="No context window",
                content="Context window not initialized",
            )

        turn = self._window.extract()
        if turn is None:
            return BasicRendering(
                summary="Empty context",
                content="No turns in context",
                metadata={"position": 0},
            )

        return BasicRendering(
            summary=f"Focus: {turn.role.value}",
            content=turn.content[:200] + ("..." if len(turn.content) > 200 else ""),
            metadata={
                "role": turn.role.value,
                "position": self._window.position,
                "total_turns": len(self._window),
                "resource_class": self._window.get_resource_class(turn),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle focus aspects."""
        if self._window is None:
            return {"error": "context window not initialized"}

        match aspect:
            case "extract":
                turn = self._window.extract()
                if turn is None:
                    return None
                return {
                    "role": turn.role.value,
                    "content": turn.content,
                    "timestamp": turn.timestamp.isoformat(),
                    "resource_id": turn.resource_id,
                }
            case "peek":
                position = kwargs.get("position", self._window.position)
                original_pos = self._window.position
                self._window.seek(position)
                turn = self._window.extract()
                self._window.seek(original_pos)
                if turn is None:
                    return None
                return {
                    "role": turn.role.value,
                    "content": turn.content,
                    "position": position,
                }
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# === Stream Map Node ===


@dataclass
class StreamMapNode(BaseLogosNode):
    """
    self.stream.map - Context-aware transformations.

    Provides comonadic extend() operation.
    """

    _handle: str = "self.stream.map"
    _window: ContextWindow | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return STREAM_AFFORDANCES["map"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show map capabilities."""
        return BasicRendering(
            summary="Stream Map Operations",
            content="Apply functions across context positions",
            metadata={
                "affordances": STREAM_AFFORDANCES["map"],
                "has_window": self._window is not None,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle map aspects."""
        if self._window is None:
            return {"error": "context window not initialized"}

        def _get_content(w: ContextWindow) -> str:
            turn = w.extract()
            return turn.content if turn else ""

        def _get_role(w: ContextWindow) -> str | None:
            turn = w.extract()
            return turn.role.value if turn else None

        def _get_tokens(w: ContextWindow) -> int:
            turn = w.extract()
            return turn.token_estimate if turn else 0

        match aspect:
            case "extend":
                # Built-in transformations
                transform = kwargs.get("transform", "content")
                match transform:
                    case "content":
                        return self._window.extend(_get_content)
                    case "role":
                        return self._window.extend(_get_role)
                    case "token_count":
                        return self._window.extend(_get_tokens)
                    case _:
                        return {"error": f"unknown transform: {transform}"}
            case "transform":
                # Summary of all turns
                return [
                    {"role": t.role.value, "tokens": t.token_estimate}
                    for t in self._window.all_turns()
                ]
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# === Stream Seek Node ===


@dataclass
class StreamSeekNode(BaseLogosNode):
    """
    self.stream.seek - Navigate context positions.

    Store-specific seek operations.
    """

    _handle: str = "self.stream.seek"
    _window: ContextWindow | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return STREAM_AFFORDANCES["seek"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show current position."""
        if self._window is None:
            return BasicRendering(
                summary="No context window",
                content="Context window not initialized",
            )

        return BasicRendering(
            summary=f"Position: {self._window.position}/{len(self._window)}",
            content=f"Currently at turn {self._window.position} of {len(self._window)}",
            metadata={
                "position": self._window.position,
                "total": len(self._window),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle seek aspects."""
        if self._window is None:
            return {"error": "context window not initialized"}

        match aspect:
            case "position":
                target = kwargs.get("target")
                if target is not None:
                    self._window.seek(int(target))
                return {"position": self._window.position}
            case "forward":
                steps = kwargs.get("steps", 1)
                self._window.seeks(lambda p: p + steps)
                return {"position": self._window.position}
            case "backward":
                steps = kwargs.get("steps", 1)
                self._window.seeks(lambda p: p - steps)
                return {"position": self._window.position}
            case "start":
                self._window.seek(1)
                return {"position": self._window.position}
            case "end":
                self._window.seek(len(self._window))
                return {"position": self._window.position}
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# === Stream Project Node ===


@dataclass
class StreamProjectNode(BaseLogosNode):
    """
    self.stream.project - Context compression via Galois Connection.

    NOT a Lens - this is fundamentally lossy.
    """

    _handle: str = "self.stream.project"
    _window: ContextWindow | None = None
    _projector: ContextProjector = field(default_factory=ContextProjector)
    _threshold: AdaptiveThreshold = field(default_factory=AdaptiveThreshold)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return STREAM_AFFORDANCES["project"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show compression state."""
        if self._window is None:
            return BasicRendering(
                summary="No context window",
                content="Context window not initialized",
            )

        return BasicRendering(
            summary=f"Pressure: {self._window.pressure:.1%}",
            content=(
                f"Context pressure: {self._window.pressure:.1%}\n"
                f"Needs compression: {self._window.needs_compression}\n"
                f"Adaptive threshold: {self._threshold.effective_threshold:.1%}"
            ),
            metadata={
                "pressure": self._window.pressure,
                "needs_compression": self._window.needs_compression,
                "threshold": self._threshold.effective_threshold,
                "compression_count": self._window._meta.compression_count,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle projection aspects."""
        if self._window is None:
            return {"error": "context window not initialized"}

        match aspect:
            case "compress":
                target = kwargs.get(
                    "target_pressure", self._threshold.effective_threshold
                )
                result = await self._projector.compress(self._window, target)
                # Update the window reference
                self._window = result.window
                return {
                    "original_tokens": result.original_tokens,
                    "compressed_tokens": result.compressed_tokens,
                    "compression_ratio": result.compression_ratio,
                    "dropped": result.dropped_count,
                    "summarized": result.summarized_count,
                    "preserved": result.preserved_count,
                }
            case "threshold":
                # Update adaptive threshold
                if "task_progress" in kwargs:
                    self._threshold.update(task_progress=kwargs["task_progress"])
                if "error_rate" in kwargs:
                    self._threshold.update(error_rate=kwargs["error_rate"])
                if "loop_detected" in kwargs:
                    self._threshold.update(loop_detected=kwargs["loop_detected"])
                return {
                    "effective_threshold": self._threshold.effective_threshold,
                    "base": self._threshold.base_threshold,
                    "task_progress": self._threshold.task_progress,
                    "error_rate": self._threshold.error_rate,
                    "loop_detected": self._threshold.loop_detected,
                }
            case "stats":
                return {
                    "pressure": self._window.pressure,
                    "total_tokens": self._window.total_tokens,
                    "max_tokens": self._window.max_tokens,
                    "turn_count": len(self._window),
                    "compression_count": self._window._meta.compression_count,
                }
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# === Stream Linearity Node ===


@dataclass
class StreamLinearityNode(BaseLogosNode):
    """
    self.stream.linearity - Resource class management.

    Access to LinearityMap for fine-grained control.
    """

    _handle: str = "self.stream.linearity"
    _window: ContextWindow | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return STREAM_AFFORDANCES["linearity"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show linearity stats."""
        if self._window is None:
            return BasicRendering(
                summary="No context window",
                content="Context window not initialized",
            )

        stats = self._window.linearity_stats
        return BasicRendering(
            summary="Resource Classes",
            content=(
                f"DROPPABLE: {stats['droppable']}\n"
                f"REQUIRED: {stats['required']}\n"
                f"PRESERVED: {stats['preserved']}\n"
                f"Total: {stats['total']}"
            ),
            metadata=stats,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle linearity aspects."""
        if self._window is None:
            return {"error": "context window not initialized"}

        match aspect:
            case "tag":
                # Tag a resource manually
                content = kwargs.get("content", "")
                rc_str = kwargs.get("resource_class", "DROPPABLE")
                provenance = kwargs.get("provenance", "manual")
                try:
                    rc = ResourceClass[rc_str.upper()]
                except KeyError:
                    return {"error": f"invalid resource class: {rc_str}"}
                rid = self._window._linearity.tag(content, rc, provenance)
                return {"resource_id": rid, "resource_class": rc.name}
            case "promote":
                resource_id = kwargs.get("resource_id")
                new_class_str = kwargs.get("new_class", "REQUIRED")
                rationale = kwargs.get("rationale", "manual promotion")
                if not resource_id:
                    return {"error": "resource_id required"}
                try:
                    new_class = ResourceClass[new_class_str.upper()]
                except KeyError:
                    return {"error": f"invalid resource class: {new_class_str}"}
                success = self._window._linearity.promote(
                    resource_id, new_class, rationale
                )
                return {"success": success, "new_class": new_class.name}
            case "drop":
                resource_id = kwargs.get("resource_id")
                if not resource_id:
                    return {"error": "resource_id required"}
                success = self._window._linearity.drop(resource_id)
                return {"success": success, "dropped": resource_id}
            case "stats":
                return self._window._linearity.stats
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# === Stream Pressure Node ===


@dataclass
class StreamPressureNode(BaseLogosNode):
    """
    self.stream.pressure - Quick pressure checks and auto-compression.
    """

    _handle: str = "self.stream.pressure"
    _window: ContextWindow | None = None
    _projector: ContextProjector = field(default_factory=ContextProjector)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return STREAM_AFFORDANCES["pressure"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show pressure status."""
        if self._window is None:
            return BasicRendering(
                summary="No context window",
                content="Context window not initialized",
            )

        status = "HIGH" if self._window.needs_compression else "OK"
        return BasicRendering(
            summary=f"Pressure: {status}",
            content=f"{self._window.pressure:.1%} of capacity",
            metadata={
                "pressure": self._window.pressure,
                "status": status,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle pressure aspects."""
        if self._window is None:
            return {"error": "context window not initialized"}

        match aspect:
            case "check":
                return {
                    "pressure": self._window.pressure,
                    "needs_compression": self._window.needs_compression,
                    "total_tokens": self._window.total_tokens,
                    "max_tokens": self._window.max_tokens,
                }
            case "auto_compress":
                if not self._window.needs_compression:
                    return {"compressed": False, "reason": "pressure below threshold"}
                result = await self._projector.compress(self._window)
                self._window = result.window
                return {
                    "compressed": True,
                    "compression_ratio": result.compression_ratio,
                    "savings": result.savings,
                }
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# === Stream Context Resolver ===


@dataclass
class StreamContextResolver:
    """
    Resolver for self.stream.* context.

    Manages the context window and provides access to all stream operations.
    """

    # The shared context window
    _window: ContextWindow | None = None

    # Singleton nodes
    _focus: StreamFocusNode | None = None
    _map: StreamMapNode | None = None
    _seek: StreamSeekNode | None = None
    _project: StreamProjectNode | None = None
    _linearity: StreamLinearityNode | None = None
    _pressure: StreamPressureNode | None = None

    def __post_init__(self) -> None:
        """Initialize nodes with shared window."""
        self._initialize_nodes()

    def _initialize_nodes(self) -> None:
        """Create or update nodes with current window."""
        self._focus = StreamFocusNode(_window=self._window)
        self._map = StreamMapNode(_window=self._window)
        self._seek = StreamSeekNode(_window=self._window)
        self._project = StreamProjectNode(_window=self._window)
        self._linearity = StreamLinearityNode(_window=self._window)
        self._pressure = StreamPressureNode(_window=self._window)

    def set_window(self, window: ContextWindow) -> None:
        """Set the context window and update all nodes."""
        self._window = window
        self._initialize_nodes()

    def get_window(self) -> ContextWindow | None:
        """Get the current context window."""
        return self._window

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode:
        """
        Resolve a self.stream.* path to a node.

        Args:
            holon: The stream subsystem (focus, map, seek, project, linearity)
            rest: Additional path components

        Returns:
            Resolved node
        """
        match holon:
            case "focus":
                return self._focus or StreamFocusNode()
            case "map":
                return self._map or StreamMapNode()
            case "seek":
                return self._seek or StreamSeekNode()
            case "project":
                return self._project or StreamProjectNode()
            case "linearity":
                return self._linearity or StreamLinearityNode()
            case "pressure":
                return self._pressure or StreamPressureNode()
            case _:
                return GenericStreamNode(holon)


# === Generic Stream Node ===


@dataclass
class GenericStreamNode(BaseLogosNode):
    """Fallback node for undefined self.stream.* paths."""

    holon: str
    _handle: str = ""

    def __post_init__(self) -> None:
        self._handle = f"self.stream.{self.holon}"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("inspect",)

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        return BasicRendering(
            summary=f"Stream: {self.holon}",
            content=f"Generic stream node for {self.holon}",
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        return {"holon": self.holon, "aspect": aspect, "kwargs": kwargs}


# === Factory Functions ===


def create_stream_resolver(
    max_tokens: int = 100_000,
    initial_system: str | None = None,
) -> StreamContextResolver:
    """
    Create a StreamContextResolver with an initialized context window.

    Args:
        max_tokens: Maximum token budget for the window
        initial_system: Optional system message

    Returns:
        Configured StreamContextResolver
    """
    resolver = StreamContextResolver()
    window = create_context_window(max_tokens=max_tokens, initial_system=initial_system)
    resolver.set_window(window)
    return resolver
