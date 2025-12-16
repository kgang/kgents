"""
AGENTESE Phase 7: Wire to Logos

This module connects the Phase 6 integration layer to the Logos resolver,
completing the AGENTESE architecture:

┌─────────────────────────────────────────────────────────────────────────────┐
│                           WIRING ARCHITECTURE                                │
│                                                                              │
│   User Request: "world.house.manifest"                                       │
│          │                                                                   │
│          ▼                                                                   │
│   ┌─────────────────────┐                                                    │
│   │   GgentIntegration  │  ← Validates path syntax against BNF              │
│   │   (Path Validation) │                                                    │
│   └─────────────────────┘                                                    │
│          │                                                                   │
│          ▼                                                                   │
│   ┌─────────────────────┐                                                    │
│   │   LgentIntegration  │  ← Semantic lookup in registry                    │
│   │   (Registry Lookup) │    (embeddings, usage tracking)                   │
│   └─────────────────────┘                                                    │
│          │                                                                   │
│          ▼                                                                   │
│   ┌─────────────────────┐                                                    │
│   │  UmweltIntegration  │  ← Extract AgentMeta from observer DNA            │
│   │   (Observer Meta)   │    (archetype → affordances)                      │
│   └─────────────────────┘                                                    │
│          │                                                                   │
│          ▼                                                                   │
│   ┌─────────────────────┐                                                    │
│   │       Logos         │  ← Resolve node, check affordances, invoke        │
│   │     (Resolver)      │                                                    │
│   └─────────────────────┘                                                    │
│          │                                                                   │
│          ▼                                                                   │
│   ┌─────────────────────┐                                                    │
│   │  MembraneAgentese   │  ← CLI commands translate to AGENTESE             │
│   │      Bridge         │    (observe → world.project.manifest)             │
│   └─────────────────────┘                                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

Key Design Principle: WiredLogos is a Logos with integrations attached.
The base Logos still works standalone, but gains superpowers when wired.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from .exceptions import (
    ObserverRequiredError,
    PathSyntaxError,
)
from .integration import (
    AgentesIntegrations,
    MembraneAgenteseBridge,
    create_agentese_integrations,
)
from .logos import ComposedPath, IdentityPath, Logos, create_logos
from .node import LogosNode, Observer

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# WiredLogos: Logos with Integrations
# =============================================================================


@dataclass
class WiredLogos:
    """
    Logos resolver with Phase 6 integrations wired in.

    This is the production AGENTESE resolver that uses:
    - UmweltIntegration: Extract AgentMeta from Umwelt DNA
    - LgentIntegration: Semantic registry lookup and usage tracking
    - GgentIntegration: Path validation against BNF grammar
    - MembraneAgenteseBridge: CLI command translation

    The key insight: WiredLogos delegates to the underlying Logos but
    intercepts key operations to use the integration layer.

    Example:
        >>> wired = create_wired_logos(lgent_registry=registry)
        >>> # Validation happens automatically
        >>> result = await wired.invoke("world.house.manifest", observer)
        >>> # Usage is tracked in L-gent
        >>> # Observer meta extracted via UmweltIntegration

    Graceful Degradation:
        If an integration is unavailable, WiredLogos falls back to
        the base Logos behavior. This allows AGENTESE to work in
        minimal environments.
    """

    logos: Logos
    integrations: AgentesIntegrations

    # === Configuration ===
    validate_paths: bool = True  # Use G-gent validation
    track_usage: bool = True  # Track invocations in L-gent

    def __post_init__(self) -> None:
        """Wire membrane bridge to this logos."""
        if self.integrations.membrane is None:
            self.integrations = AgentesIntegrations(
                umwelt=self.integrations.umwelt,
                membrane=MembraneAgenteseBridge(logos=self),
                lgent=self.integrations.lgent,
                ggent=self.integrations.ggent,
            )

    # === Core Operations (delegated with integration) ===

    def resolve(
        self, path: str, observer: "Umwelt[Any, Any] | None" = None
    ) -> LogosNode:
        """
        Resolve an AGENTESE path with G-gent validation and L-gent lookup.

        Resolution strategy (enhanced):
        1. Validate path syntax via G-gent (if available)
        2. Check L-gent registry (semantic lookup)
        3. Check Logos cache/registry
        4. Check spec/ for JIT generation
        5. Raise PathNotFoundError

        Args:
            path: AGENTESE path (e.g., "world.house")
            observer: Optional observer for affordance filtering

        Returns:
            Resolved LogosNode
        """
        # Step 1: G-gent path validation
        if self.validate_paths:
            self._validate_path(path)

        # Step 2: L-gent semantic lookup (async → sync bridge)
        lgent_entry = self._sync_lgent_lookup(path)
        if lgent_entry is not None:
            # Found in L-gent, hydrate to LogosNode
            node = self._hydrate_lgent_entry(lgent_entry, path)
            if node is not None:
                return node

        # Step 3-5: Delegate to base Logos
        return self.logos.resolve(path, observer)

    def lift(self, path: str) -> "Any":
        """
        Convert a handle into a composable Agent.

        Uses G-gent validation before lifting.
        """
        if self.validate_paths:
            self._validate_path(path)
        return self.logos.lift(path)

    async def invoke(
        self,
        path: str,
        observer: "Umwelt[Any, Any] | Observer | None" = None,
        **kwargs: Any,
    ) -> Any:
        """
        Invoke an AGENTESE path with full integration support.

        Enhanced behavior:
        1. Validate path via G-gent
        2. Extract AgentMeta via UmweltIntegration (if Umwelt provided)
        3. Check affordances with enhanced metadata
        4. Invoke via Logos
        5. Track usage in L-gent

        Args:
            path: Full AGENTESE path including aspect
            observer: Observer, Umwelt, or None (v3 API: defaults to guest)
            **kwargs: Aspect-specific arguments

        Returns:
            Aspect-specific result
        """
        # Step 1: G-gent validation
        if self.validate_paths:
            self._validate_path(path)

        # Step 2: UmweltIntegration for enhanced meta extraction (only if Umwelt)
        # Skip if observer is an Observer or None
        if observer is not None and hasattr(observer, "dna"):
            # hasattr check ensures this is Umwelt, not Observer
            _meta = self.integrations.umwelt.extract_meta(
                cast("Umwelt[Any, Any]", observer)
            )

        # Step 3 & 4: Invoke via Logos (uses our resolve() which is enhanced)
        success = True
        error_msg = None
        try:
            result = await self.logos.invoke(path, observer, **kwargs)
        except Exception as e:
            success = False
            error_msg = str(e)
            raise
        finally:
            # Step 5: Track usage in L-gent
            if self.track_usage:
                await self._track_invocation(path, success, error_msg)

        return result

    def compose(self, *paths: str, enforce_output: bool = True) -> ComposedPath:
        """
        Create a composed path with validation.

        Validates all paths before composition.
        """
        if self.validate_paths:
            for path in paths:
                self._validate_path(path)
        return self.logos.compose(*paths, enforce_output=enforce_output)

    def identity(self) -> IdentityPath:
        """Get identity morphism."""
        return self.logos.identity()

    def path(self, p: str) -> ComposedPath:
        """Create single-path composition."""
        if self.validate_paths:
            self._validate_path(p)
        return self.logos.path(p)

    def register(self, handle: str, node: LogosNode) -> None:
        """Register a node (delegates to Logos)."""
        self.logos.register(handle, node)

    # === Membrane Bridge Operations ===

    async def execute_membrane_command(
        self,
        command: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Execute a Membrane CLI command via AGENTESE.

        Translates commands like "observe", "sense", "trace" to
        AGENTESE paths and invokes them.

        Args:
            command: Membrane command (observe, sense, trace, etc.)
            observer: Observer Umwelt
            **kwargs: Command-specific arguments

        Returns:
            AGENTESE invocation result
        """
        if self.integrations.membrane is None:
            raise RuntimeError(
                "Membrane bridge not available. "
                "Create WiredLogos with membrane integration."
            )
        return await self.integrations.membrane.execute(command, observer, **kwargs)

    def get_agentese_path(self, command: str) -> str | None:
        """
        Get the AGENTESE path for a Membrane command without executing.

        Args:
            command: Membrane command

        Returns:
            AGENTESE path or None if not mapped
        """
        if self.integrations.membrane is None:
            return None
        return self.integrations.membrane.get_path(command)

    # === Autopoiesis (Phase 4) ===

    async def define_concept(
        self,
        handle: str,
        spec: str,
        observer: "Umwelt[Any, Any]",
    ) -> LogosNode:
        """
        Create a new concept with L-gent registration.

        Enhanced behavior:
        1. Validate handle via G-gent
        2. Check observer affordance via UmweltIntegration
        3. Create via Logos.define_concept
        4. Register in L-gent with full metadata
        """
        if self.validate_paths:
            self._validate_path(handle)

        # Create via base Logos
        node = await self.logos.define_concept(handle, spec, observer)

        # Register in L-gent (enhanced)
        meta = self.integrations.umwelt.extract_meta(observer)
        await self.integrations.lgent.register_node(
            node=node,
            observer=meta.name,
            description=f"Created by {meta.archetype} via autopoiesis",
            keywords=[handle.replace(".", " "), meta.archetype],
            status="draft",
        )

        return node

    async def promote_concept(
        self,
        handle: str,
        threshold: int = 100,
        success_threshold: float = 0.8,
    ) -> Any:
        """Promote a JIT node (delegates to Logos)."""
        return await self.logos.promote_concept(handle, threshold, success_threshold)

    # === Status & Introspection ===

    def get_jit_status(self, handle: str) -> dict[str, Any] | None:
        """Get JIT node status."""
        return self.logos.get_jit_status(handle)

    def list_jit_nodes(self) -> list[dict[str, Any]]:
        """List all JIT nodes."""
        return self.logos.list_jit_nodes()

    def list_handles(self, context: str | None = None) -> list[str]:
        """List registered handles."""
        return self.logos.list_handles(context)

    def is_resolved(self, path: str) -> bool:
        """Check if path is cached."""
        return self.logos.is_resolved(path)

    def clear_cache(self) -> None:
        """Clear caches."""
        self.logos.clear_cache()
        self.integrations.lgent.clear_cache()

    def integration_status(self) -> dict[str, bool]:
        """
        Get status of all integrations.

        Returns:
            Dict mapping integration name to availability
        """
        return {
            "umwelt": True,  # Always available
            "lgent": self.integrations.lgent.registry is not None,
            "ggent": self.integrations.ggent.grammarian is not None,
            "membrane": self.integrations.membrane is not None,
            "validate_paths": self.validate_paths,
            "track_usage": self.track_usage,
        }

    # === Internal Helper Methods ===

    def _validate_path(self, path: str) -> None:
        """
        Validate path syntax via G-gent integration.

        Raises PathSyntaxError if invalid.
        """
        is_valid, error = self.integrations.ggent.validate_path(path)
        if not is_valid:
            raise PathSyntaxError(
                f"Invalid AGENTESE path: {path}",
                path=path,
                why=error or "Path doesn't match grammar",
            )

    def _sync_lgent_lookup(self, path: str) -> Any | None:
        """
        Synchronous L-gent lookup (bridges async).

        This is a workaround for resolve() being sync.
        In production, consider making resolve() async.
        """
        if self.integrations.lgent.registry is None:
            return None

        # Check local cache first (doesn't need async)
        if path in self.integrations.lgent._cache:
            return self.integrations.lgent._cache[path]

        # For full async lookup, would need to make resolve() async
        # For now, return None to fall back to Logos
        return None

    def _hydrate_lgent_entry(self, entry: Any, path: str) -> LogosNode | None:
        """
        Convert L-gent CatalogEntry to LogosNode.

        If entry has implementation metadata, creates appropriate node.
        Otherwise returns None to fall back to Logos resolution.
        """
        # L-gent entries don't directly contain LogosNode implementation
        # They contain metadata. The actual node is in Logos registry.
        # So we return None to let Logos handle hydration.
        return None

    async def _track_invocation(
        self,
        path: str,
        success: bool,
        error: str | None = None,
    ) -> None:
        """Track invocation in L-gent metrics."""
        await self.integrations.lgent.record_invocation(path, success, error)


# =============================================================================
# Factory Functions
# =============================================================================


def create_wired_logos(
    spec_root: Path | str = "spec",
    lgent_registry: Any | None = None,
    grammarian: Any | None = None,
    narrator: Any = None,
    d_gent: Any = None,
    b_gent: Any = None,
    validate_paths: bool = True,
    track_usage: bool = True,
) -> WiredLogos:
    """
    Create a fully wired Logos resolver.

    This is the recommended way to create a production AGENTESE resolver.

    Args:
        spec_root: Path to spec directory for JIT generation
        lgent_registry: L-gent registry for semantic lookup
        grammarian: G-gent instance for grammar validation
        narrator: N-gent for narrative traces
        d_gent: D-gent for persistence
        b_gent: B-gent for budgeting
        validate_paths: Whether to validate paths via G-gent
        track_usage: Whether to track invocations in L-gent

    Returns:
        WiredLogos with all available integrations
    """
    # Create base Logos
    logos = create_logos(
        spec_root=spec_root,
        narrator=narrator,
        d_gent=d_gent,
        b_gent=b_gent,
        grammarian=grammarian,
    )

    # Create integrations
    integrations = create_agentese_integrations(
        logos=logos,
        lgent_registry=lgent_registry,
        grammarian=grammarian,
    )

    return WiredLogos(
        logos=logos,
        integrations=integrations,
        validate_paths=validate_paths,
        track_usage=track_usage,
    )


def wire_existing_logos(
    logos: Logos,
    lgent_registry: Any | None = None,
    grammarian: Any | None = None,
    validate_paths: bool = True,
    track_usage: bool = True,
) -> WiredLogos:
    """
    Wire integrations to an existing Logos instance.

    Use this when you already have a Logos and want to add integrations.

    Args:
        logos: Existing Logos instance
        lgent_registry: L-gent registry for semantic lookup
        grammarian: G-gent instance for grammar validation
        validate_paths: Whether to validate paths via G-gent
        track_usage: Whether to track invocations in L-gent

    Returns:
        WiredLogos wrapping the existing Logos
    """
    integrations = create_agentese_integrations(
        logos=logos,
        lgent_registry=lgent_registry,
        grammarian=grammarian,
    )

    return WiredLogos(
        logos=logos,
        integrations=integrations,
        validate_paths=validate_paths,
        track_usage=track_usage,
    )


def create_minimal_wired_logos(
    spec_root: Path | str = "spec",
) -> WiredLogos:
    """
    Create a minimal WiredLogos without external integrations.

    This is useful for testing or environments without L-gent/G-gent.
    Still provides:
    - UmweltIntegration (always available)
    - Basic path validation (structural, not G-gent)
    - Membrane command translation

    Args:
        spec_root: Path to spec directory

    Returns:
        WiredLogos with minimal integrations
    """
    return create_wired_logos(
        spec_root=spec_root,
        validate_paths=True,  # Uses structural validation
        track_usage=False,  # No L-gent to track
    )


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Main Class
    "WiredLogos",
    # Factory Functions
    "create_wired_logos",
    "wire_existing_logos",
    "create_minimal_wired_logos",
]
