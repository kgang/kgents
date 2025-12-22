"""
Portal Bridge: Connect Outline Model to File Operad Portal Infrastructure.

This bridge connects the Context Perception layer (protocols/context/outline.py)
to the Portal Token infrastructure (protocols/file_operad/portal.py).

The bridge ensures that:
1. Portal expansions update both the Outline and the PortalTree
2. Trail steps are recorded in both systems
3. ContextEvents are emitted for agent context updates
4. FileLens is used for semantic content loading

Spec: spec/protocols/context-perception.md (Layer 4 → Layer 3 bridge)
      plans/portal-fullstack-integration.md §6 (Phase 4: PortalToken Unification)

Teaching:
    gotcha: Two PortalToken implementations exist! This bridge reconciles them.
            - protocols/context/outline.py::PortalToken = outline model
            - protocols/file_operad/portal.py::PortalToken = infrastructure
            (Evidence: test_portal_bridge.py::test_two_token_types)

    gotcha: The bridge is the ONLY place that coordinates state between
            Outline and PortalTree. Direct manipulation of either breaks sync.
            (Evidence: test_portal_bridge.py::test_sync_invariant)

    gotcha: UnifiedPortalBridge provides protocol-aware bidirectional conversion.
            Use it for roundtrip: file_to_outline(outline_to_file(x)) ≈ x
            (Evidence: test_portal_protocol.py::test_roundtrip_conversion)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from .outline import (
    Outline,
    OutlineNode,
    OutlineOperations,
    PortalToken as OutlinePortalToken,
    TextSnippet,
    SnippetType,
    create_outline,
)
from .lens import FileLens, FocusSpec, create_lens_for_function, create_lens_for_range
from .parser import RecognizedToken, TokenType, extract_tokens

if TYPE_CHECKING:
    from protocols.file_operad.portal import PortalTree, PortalNode, PortalOpenSignal
    from protocols.file_operad.context_bridge import ContextEvent


# =============================================================================
# Bridge Data Structures
# =============================================================================


@dataclass
class BridgeState:
    """
    Synchronized state between Outline and PortalTree.

    The bridge maintains this state to ensure consistency.
    """

    outline: Outline
    portal_tree: "PortalTree | None" = None

    # Event subscribers
    on_expand: list[Callable[["ContextEvent"], None]] = field(default_factory=list)
    on_collapse: list[Callable[["ContextEvent"], None]] = field(default_factory=list)

    # Sync tracking
    last_sync: datetime = field(default_factory=datetime.now)
    sync_count: int = 0


@dataclass
class PortalExpansionResult:
    """
    Result of a portal expansion operation.

    Contains both the expanded content and metadata for trail recording.
    Phase 3: Now includes discovered tokens from parsing.
    """

    success: bool
    portal_path: str
    edge_type: str | None = None
    content: dict[str, str] = field(default_factory=dict)
    nested_portals: list[str] = field(default_factory=list)
    error: str | None = None

    # Trail metadata
    depth: int = 0
    parent_path: str = ""

    # Phase 3: Discovered tokens from parsing
    discovered_tokens: list[RecognizedToken] = field(default_factory=list)
    agentese_paths: list[str] = field(default_factory=list)
    evidence_links: list[str] = field(default_factory=list)

    def to_trail_step(self) -> dict[str, Any]:
        """Convert to trail step dictionary."""
        return {
            "action": "expand",
            "node_path": self.portal_path,
            "edge_type": self.edge_type,
            "timestamp": datetime.now().isoformat(),
            "depth": self.depth,
            "parent_path": self.parent_path,
            "discovered_tokens": len(self.discovered_tokens),
        }


# =============================================================================
# Portal Bridge
# =============================================================================


class OutlinePortalBridge:
    """
    Bridge between Outline model and PortalTree infrastructure.

    This bridge coordinates:
    1. Portal expansions across both systems
    2. Trail recording in Outline
    3. ContextEvent emission for agents
    4. Content loading via FileLens

    Usage:
        outline = create_outline("Investigation")
        bridge = OutlinePortalBridge(outline)

        # Expand a portal - updates both systems
        result = await bridge.expand("tests/auth_test.py")

        # Get synchronized state
        state = bridge.get_state()
    """

    def __init__(
        self,
        outline: Outline | None = None,
        observer_id: str = "",
    ):
        """
        Initialize the bridge.

        Args:
            outline: Existing outline or None to create new
            observer_id: ID of the observer using this bridge
        """
        self.outline = outline or create_outline(observer_id=observer_id)
        self.observer_id = observer_id
        self._portal_tree: "PortalTree | None" = None
        self._operations = OutlineOperations(self.outline, observer_id)

        # Event subscribers
        self._on_expand: list[Callable[["ContextEvent"], None]] = []
        self._on_collapse: list[Callable[["ContextEvent"], None]] = []

    @property
    def portal_tree(self) -> "PortalTree | None":
        """Get the underlying portal tree (if initialized)."""
        return self._portal_tree

    def set_portal_tree(self, tree: "PortalTree") -> None:
        """
        Set the portal tree to bridge with.

        This should be called when a portal tree is created from a file.
        """
        self._portal_tree = tree

    def subscribe_expand(self, callback: Callable[["ContextEvent"], None]) -> None:
        """Subscribe to expand events."""
        self._on_expand.append(callback)

    def subscribe_collapse(self, callback: Callable[["ContextEvent"], None]) -> None:
        """Subscribe to collapse events."""
        self._on_collapse.append(callback)

    async def expand(
        self,
        portal_path: str,
        use_lens: bool = True,
    ) -> PortalExpansionResult:
        """
        Expand a portal, updating both Outline and PortalTree.

        Args:
            portal_path: Path to the portal (e.g., "tests/auth")
            use_lens: Whether to use FileLens for content loading

        Returns:
            PortalExpansionResult with expansion outcome

        Side effects:
            - Updates Outline portal state
            - Updates PortalTree if available
            - Records trail step
            - Emits ContextEvent to subscribers
        """
        # Find portal in outline
        node = self.outline.find_node(portal_path)
        if node is None or node.portal is None:
            return PortalExpansionResult(
                success=False,
                portal_path=portal_path,
                error=f"Portal not found: {portal_path}",
            )

        portal = node.portal

        # Already expanded?
        if portal.expanded:
            return PortalExpansionResult(
                success=True,
                portal_path=portal_path,
                edge_type=portal.edge_type,
                content=portal._content or {},
            )

        # Load content
        content: dict[str, str] = {}
        if use_lens:
            content = await self._load_with_lens(portal)
        else:
            content = await self._load_direct(portal)

        # Update portal state
        portal.expanded = True
        portal.set_content(content)

        # Update portal tree if available
        if self._portal_tree is not None:
            path_segments = portal_path.split("/")
            self._portal_tree.expand(path_segments)

        # Record trail step
        self.outline.record_step(
            action="expand",
            node_path=portal_path,
            edge_type=portal.edge_type,
        )

        # Emit context event
        await self._emit_expand_event(portal, portal_path)

        # Phase 3: Parse content for tokens
        discovered_tokens, agentese_paths, evidence_links = self._parse_content_tokens(
            content
        )

        return PortalExpansionResult(
            success=True,
            portal_path=portal_path,
            edge_type=portal.edge_type,
            content=content,
            nested_portals=list(content.keys()),
            depth=node.depth,
            discovered_tokens=discovered_tokens,
            agentese_paths=agentese_paths,
            evidence_links=evidence_links,
        )

    async def collapse(self, portal_path: str) -> bool:
        """
        Collapse a portal, updating both Outline and PortalTree.

        Args:
            portal_path: Path to the portal

        Returns:
            True if collapse succeeded
        """
        # Find portal in outline
        node = self.outline.find_node(portal_path)
        if node is None or node.portal is None:
            return False

        portal = node.portal

        # Already collapsed?
        if not portal.expanded:
            return True

        # Collapse
        portal.expanded = False

        # Update portal tree if available
        if self._portal_tree is not None:
            path_segments = portal_path.split("/")
            self._portal_tree.collapse(path_segments)

        # Record trail step
        self.outline.record_step(
            action="collapse",
            node_path=portal_path,
            edge_type=portal.edge_type,
        )

        # Emit context event
        await self._emit_collapse_event(portal, portal_path)

        return True

    async def navigate(self, target_path: str) -> bool:
        """
        Navigate to a specific node in the outline.

        Args:
            target_path: Path to navigate to

        Returns:
            True if navigation succeeded
        """
        node = self.outline.find_node(target_path)
        if node is None:
            return False

        # Record navigation
        self.outline.record_step(
            action="navigate",
            node_path=target_path,
        )

        return True

    async def create_lens(
        self,
        file_path: str,
        focus: str,
    ) -> FileLens | None:
        """
        Create a semantic lens into a file.

        Args:
            file_path: Path to the file
            focus: Focus specifier (function name, "class:ClassName", "lines:start-end")

        Returns:
            FileLens with semantic naming, or None if creation failed
        """
        path = Path(file_path)
        if not path.exists():
            return None

        # Parse focus specifier
        if focus.startswith("class:"):
            class_name = focus[6:]
            from .lens import create_lens_for_class
            return create_lens_for_class(file_path, class_name)
        elif focus.startswith("lines:"):
            range_spec = focus[6:]
            if "-" in range_spec:
                start, end = range_spec.split("-", 1)
                return create_lens_for_range(file_path, int(start), int(end))
        else:
            # Assume function name
            return create_lens_for_function(file_path, focus)

        return None

    def get_state(self) -> BridgeState:
        """Get the current synchronized state."""
        return BridgeState(
            outline=self.outline,
            portal_tree=self._portal_tree,
            on_expand=self._on_expand.copy(),
            on_collapse=self._on_collapse.copy(),
        )

    # =========================================================================
    # Private Methods
    # =========================================================================

    async def _load_with_lens(self, portal: OutlinePortalToken) -> dict[str, str]:
        """Load portal content using FileLens for semantic names."""
        content: dict[str, str] = {}

        for dest in portal.destinations:
            # Try to create a lens for the destination
            path = Path(dest) if "/" in dest else None
            if path and path.exists():
                # Read file content
                try:
                    file_content = path.read_text()
                    # Create a simple lens (full file for now)
                    lens = create_lens_for_range(str(path), 1, len(file_content.splitlines()))
                    if lens:
                        content[dest] = lens.visible_content
                    else:
                        content[dest] = file_content
                except Exception as e:
                    content[dest] = f"[Error loading {dest}: {e}]"
            else:
                # Not a file path, use placeholder
                content[dest] = f"[Content of {dest}]"

        return content

    async def _load_direct(self, portal: OutlinePortalToken) -> dict[str, str]:
        """Load portal content directly (fallback)."""
        content: dict[str, str] = {}

        for dest in portal.destinations:
            path = Path(dest) if "/" in dest else None
            if path and path.exists():
                try:
                    content[dest] = path.read_text()
                except Exception as e:
                    content[dest] = f"[Error: {e}]"
            else:
                content[dest] = f"[Content of {dest}]"

        return content

    async def _emit_expand_event(
        self,
        portal: OutlinePortalToken,
        portal_path: str,
    ) -> None:
        """Emit expand event to subscribers."""
        if not self._on_expand:
            return

        try:
            from protocols.file_operad.context_bridge import ContextEvent

            event = ContextEvent.files_opened(
                paths=portal.destinations,
                reason=f"Expanded [{portal.edge_type}]",
                depth=portal.depth,
                edge_type=portal.edge_type,
            )

            for callback in self._on_expand:
                try:
                    callback(event)
                except Exception:
                    pass  # Don't let callback errors break expansion

        except ImportError:
            pass  # ContextEvent not available

    async def _emit_collapse_event(
        self,
        portal: OutlinePortalToken,
        portal_path: str,
    ) -> None:
        """Emit collapse event to subscribers."""
        if not self._on_collapse:
            return

        try:
            from protocols.file_operad.context_bridge import ContextEvent

            event = ContextEvent.files_closed(
                paths=portal.destinations,
                reason=f"Collapsed [{portal.edge_type}]",
                depth=portal.depth,
            )

            for callback in self._on_collapse:
                try:
                    callback(event)
                except Exception:
                    pass

        except ImportError:
            pass

    def _parse_content_tokens(
        self,
        content: dict[str, str],
    ) -> tuple[list[RecognizedToken], list[str], list[str]]:
        """
        Parse loaded content for meaningful tokens.

        Discovers nested portals, AGENTESE paths, evidence links, and
        other interactive elements in the content.

        Phase 3: Live token parsing integration.

        Args:
            content: Dict of {destination: file_content}

        Returns:
            Tuple of (all_tokens, agentese_paths, evidence_links)
        """
        all_tokens: list[RecognizedToken] = []
        agentese_paths: list[str] = []
        evidence_links: list[str] = []

        for dest, text in content.items():
            # Extract tokens from this content
            tokens = extract_tokens(text)
            all_tokens.extend(tokens)

            # Collect specific token types
            for token in tokens:
                if token.token_type == TokenType.AGENTESE_PATH:
                    if token.path:
                        agentese_paths.append(token.path)
                elif token.token_type == TokenType.EVIDENCE_LINK:
                    if token.claim:
                        evidence_links.append(token.claim)
                elif token.token_type in (
                    TokenType.PORTAL_COLLAPSED,
                    TokenType.PORTAL_EXPANDED,
                ):
                    # Nested portals discovered
                    pass  # Already tracked in nested_portals list

        return all_tokens, agentese_paths, evidence_links


# =============================================================================
# Factory Functions
# =============================================================================


def create_bridge(
    outline: Outline | None = None,
    observer_id: str = "",
) -> OutlinePortalBridge:
    """Create a new OutlinePortalBridge."""
    return OutlinePortalBridge(outline=outline, observer_id=observer_id)


def create_bridge_from_file(
    file_path: str | Path,
    observer_id: str = "",
) -> OutlinePortalBridge:
    """
    Create a bridge initialized from a file.

    Reads the file, parses portal links, and creates both
    the Outline and PortalTree models.
    """
    path = Path(file_path)
    if not path.exists():
        return create_bridge(observer_id=observer_id)

    # Create outline from file
    content = path.read_text()
    outline = create_outline(root_text=content, observer_id=observer_id)

    # Create bridge
    bridge = OutlinePortalBridge(outline=outline, observer_id=observer_id)

    # Try to create portal tree
    try:
        from protocols.file_operad.portal import PortalTree

        portal_tree = PortalTree.from_file(path, expand_all=False)
        bridge.set_portal_tree(portal_tree)
    except ImportError:
        pass  # PortalTree not available

    return bridge


# =============================================================================
# Unified Portal Bridge (Phase 4: Protocol-Aware Conversion)
# =============================================================================


class UnifiedPortalBridge:
    """
    Protocol-aware bidirectional conversion between PortalToken implementations.

    This bridge translates between:
    - protocols/context/outline.py::PortalToken (outline model)
    - protocols/file_operad/portal.py::PortalToken (infrastructure)

    Both implementations satisfy protocols.portal_protocol.PortalTokenProtocol,
    enabling type-safe interoperability.

    Usage:
        from protocols.context.outline import PortalToken as OutlineToken
        from protocols.file_operad.portal import PortalToken as FileToken
        from protocols.context.portal_bridge import UnifiedPortalBridge

        bridge = UnifiedPortalBridge()

        # Convert outline → file
        file_token = bridge.outline_to_file(outline_token)

        # Convert file → outline
        outline_token = bridge.file_to_outline(file_token)

        # Roundtrip (preserves essential properties)
        assert bridge.roundtrip_outline(original) == original  # Approximately

    Teaching:
        gotcha: Roundtrip conversion is approximate, not exact. Some fields
                (like 'id') are regenerated. Use protocol fields (edge_type,
                path, is_expanded, depth) for equality comparison.
                (Evidence: test_portal_protocol.py::test_roundtrip_approximate)
    """

    def outline_to_file(
        self,
        outline_token: "OutlinePortalToken",
    ) -> "FilePortalToken":
        """
        Convert outline PortalToken to file_operad PortalToken.

        Args:
            outline_token: protocols.context.outline.PortalToken

        Returns:
            protocols.file_operad.portal.PortalToken
        """
        from protocols.file_operad.portal import (
            PortalLink,
            PortalState,
            PortalToken as FileToken,
        )

        # Create PortalLink from outline fields
        link = PortalLink(
            edge_type=outline_token.edge_type,
            path=outline_token.path,  # First destination
            note=None,
        )

        # Map expansion state
        state = PortalState.EXPANDED if outline_token.is_expanded else PortalState.COLLAPSED

        # Create file token
        token = FileToken(
            link=link,
            state=state,
            depth=outline_token.depth,
        )

        # Copy content if available (note: file token uses str, outline uses dict)
        if outline_token._content is not None:
            # Combine dict content into single string for file token
            combined = "\n---\n".join(
                f"# {path}\n{content}"
                for path, content in outline_token._content.items()
            )
            token._content = combined

        return token

    def file_to_outline(
        self,
        file_token: "FilePortalToken",
    ) -> "OutlinePortalToken":
        """
        Convert file_operad PortalToken to outline PortalToken.

        Args:
            file_token: protocols.file_operad.portal.PortalToken

        Returns:
            protocols.context.outline.PortalToken
        """
        # Create outline token
        token = OutlinePortalToken(
            source_path="",  # File token doesn't have source_path
            edge_type=file_token.edge_type,
            destinations=[file_token.path],  # Single destination from link
            expanded=file_token.is_expanded,
            depth=file_token.depth,
        )

        # Copy content if available (convert str to dict)
        if file_token._content is not None:
            token._content = {file_token.path: file_token._content}

        return token

    def roundtrip_outline(
        self,
        outline_token: "OutlinePortalToken",
    ) -> "OutlinePortalToken":
        """
        Roundtrip conversion: outline → file → outline.

        Useful for testing protocol compliance.

        Note: Not exact equality due to field differences (id regenerated,
              destinations collapsed to single path, etc.)
        """
        file_token = self.outline_to_file(outline_token)
        return self.file_to_outline(file_token)

    def roundtrip_file(
        self,
        file_token: "FilePortalToken",
    ) -> "FilePortalToken":
        """
        Roundtrip conversion: file → outline → file.

        Useful for testing protocol compliance.
        """
        outline_token = self.file_to_outline(file_token)
        return self.outline_to_file(outline_token)

    def are_equivalent(
        self,
        token_a: Any,
        token_b: Any,
    ) -> bool:
        """
        Check if two tokens are equivalent via protocol fields.

        Uses only the protocol-defined fields for comparison:
        - edge_type
        - path
        - is_expanded
        - depth

        This allows comparing across implementations.
        """
        from protocols.portal_protocol import satisfies_protocol

        if not satisfies_protocol(token_a) or not satisfies_protocol(token_b):
            return False

        # Compare protocol fields with explicit bool conversion for mypy
        edge_match: bool = token_a.edge_type == token_b.edge_type
        path_match: bool = token_a.path == token_b.path
        expanded_match: bool = token_a.is_expanded == token_b.is_expanded
        depth_match: bool = token_a.depth == token_b.depth

        return edge_match and path_match and expanded_match and depth_match


# Type aliases for the two token types
FilePortalToken = Any  # protocols.file_operad.portal.PortalToken
# OutlinePortalToken already imported at top


__all__ = [
    "BridgeState",
    "PortalExpansionResult",
    "OutlinePortalBridge",
    "UnifiedPortalBridge",
    "create_bridge",
    "create_bridge_from_file",
]
