"""
Canonical Portal Response Type.

The CONTRACT between frontend and backend for portal operations.

This module defines the exact shape that:
- Frontend (portal.ts) expects from AGENTESE gateway
- Backend (self_portal.py) produces for JSON response mode

Design principle: "You don't go to the document. The document comes to you."

Teaching:
    gotcha: PortalResponse is returned in metadata["result"] when
            response_format="json", NOT as the top-level response.
            The gateway wraps it in {path, aspect, result: ...}.
            (Evidence: test_portal_response.py::test_response_unwrapping)

    gotcha: trail_id and evidence_id are populated AFTER Phase 2
            (Witness Mark Integration). Until then, they're None.
            Frontend should null-check these fields.
            (Evidence: test_portal_response.py::test_optional_evidence_fields)

Spec: plans/portal-fullstack-integration.md Phase 1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PortalResponse:
    """
    Canonical response shape for portal operations.

    This is the CONTRACT between frontend and backend.

    Fields are grouped by purpose:
    - Core: Always present (success, path, aspect)
    - Tree state: Current portal tree
    - Operation-specific: expand/collapse results
    - Evidence: Future Phase 2 witness integration
    - Error handling: Error details when success=False

    Usage (backend):
        return PortalResponse(
            success=True,
            path="self.portal",
            aspect="manifest",
            tree=tree.to_dict(),
        )

    Usage (frontend):
        const response = await apiClient.post<AgenteseResponse<PortalResponse>>(...);
        if (response.data.result.success) {
            setTree(response.data.result.tree);
        }
    """

    # === Core (always present) ===
    success: bool
    path: str  # AGENTESE path that was invoked (e.g., "self.portal")
    aspect: str  # Which aspect was called (e.g., "manifest", "expand")

    # === Tree state (always included when available) ===
    tree: dict[str, Any] | None = None  # PortalTree.to_dict()

    # === Operation-specific ===
    expanded_path: str | None = None  # For expand operations: which path was expanded
    collapsed_path: str | None = None  # For collapse operations: which path was collapsed

    # === Evidence (Phase 2: Witness Mark Integration) ===
    trail_id: str | None = None  # Trail ID if trail was recorded/saved
    evidence_id: str | None = None  # Witness mark ID if mark was emitted

    # === Error handling ===
    error: str | None = None  # Human-readable error message
    error_code: str | None = None  # Machine-readable error code

    # === Additional metadata (for future extensibility) ===
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        JSON-serializable dict.

        Returns only non-None fields to minimize payload size.
        """
        result: dict[str, Any] = {
            "success": self.success,
            "path": self.path,
            "aspect": self.aspect,
        }

        # Add optional fields only if present
        if self.tree is not None:
            result["tree"] = self.tree

        if self.expanded_path is not None:
            result["expanded_path"] = self.expanded_path

        if self.collapsed_path is not None:
            result["collapsed_path"] = self.collapsed_path

        if self.trail_id is not None:
            result["trail_id"] = self.trail_id

        if self.evidence_id is not None:
            result["evidence_id"] = self.evidence_id

        if self.error is not None:
            result["error"] = self.error

        if self.error_code is not None:
            result["error_code"] = self.error_code

        if self.metadata:
            result["metadata"] = self.metadata

        return result

    def to_text(self) -> str:
        """
        Convert to human-readable text.

        Required by Renderable protocol for CLI output fallback.
        """
        if not self.success:
            return f"[FAILED] {self.path}.{self.aspect}: {self.error or 'Unknown error'}"

        parts = [f"[{self.aspect.upper()}] {self.path}"]

        if self.expanded_path:
            parts.append(f"  Expanded: {self.expanded_path}")

        if self.collapsed_path:
            parts.append(f"  Collapsed: {self.collapsed_path}")

        if self.trail_id:
            parts.append(f"  Trail: {self.trail_id}")

        if self.evidence_id:
            parts.append(f"  Evidence: {self.evidence_id}")

        if self.tree:
            root_path = self.tree.get("root", {}).get("path", "?")
            parts.append(f"  Tree root: {root_path}")

        return "\n".join(parts)

    @classmethod
    def manifest(
        cls,
        tree: dict[str, Any],
        *,
        observer: str = "guest",
    ) -> "PortalResponse":
        """
        Create response for manifest aspect.

        Args:
            tree: PortalTree.to_dict()
            observer: Observer archetype for metadata
        """
        return cls(
            success=True,
            path="self.portal",
            aspect="manifest",
            tree=tree,
            metadata={"observer": observer},
        )

    @classmethod
    def expand_success(
        cls,
        tree: dict[str, Any],
        expanded_path: str,
        *,
        evidence_id: str | None = None,
    ) -> "PortalResponse":
        """
        Create response for successful expand.

        Args:
            tree: Updated PortalTree.to_dict()
            expanded_path: The path that was expanded
            evidence_id: Witness mark ID (Phase 2)
        """
        return cls(
            success=True,
            path="self.portal",
            aspect="expand",
            tree=tree,
            expanded_path=expanded_path,
            evidence_id=evidence_id,
        )

    @classmethod
    def expand_failure(
        cls,
        portal_path: str,
        error: str,
        error_code: str = "expansion_failed",
        suggestion: str | None = None,
        depth: int | None = None,
        max_depth: int | None = None,
    ) -> "PortalResponse":
        """
        Create response for failed expand with sympathetic messaging.

        Args:
            portal_path: The path that failed to expand
            error: Human-readable error message
            error_code: Machine-readable error code for frontend handling
            suggestion: Helpful suggestion for what to do next
            depth: Current depth (for depth_limit_reached errors)
            max_depth: Maximum allowed depth (for depth_limit_reached errors)
        """
        metadata: dict[str, Any] = {"portal_path": portal_path}

        # Include depth info for depth limit errors
        if depth is not None:
            metadata["depth"] = depth
        if max_depth is not None:
            metadata["max_depth"] = max_depth
        if suggestion is not None:
            metadata["suggestion"] = suggestion

        return cls(
            success=False,
            path="self.portal",
            aspect="expand",
            error=error,
            error_code=error_code,
            metadata=metadata,
        )

    @classmethod
    def from_expand_result(
        cls,
        portal_path: str,
        result: Any,  # ExpandResult from file_operad.portal
        tree: dict[str, Any] | None = None,
        evidence_id: str | None = None,
    ) -> "PortalResponse":
        """
        Create a PortalResponse from an ExpandResult.

        This is the bridge between the file_operad.portal.ExpandResult
        and the frontend-facing PortalResponse.

        Args:
            portal_path: The path that was expanded/attempted
            result: ExpandResult from PortalTree.expand()
            tree: Current tree state (for success cases)
            evidence_id: Witness mark ID (Phase 2)
        """
        if result.success:
            return cls.expand_success(
                tree=tree or {},
                expanded_path=portal_path,
                evidence_id=evidence_id,
            )

        # Map error code to user-friendly response
        error_code = result.error_code.value if result.error_code else "expansion_failed"
        return cls.expand_failure(
            portal_path=portal_path,
            error=result.error_message or "Expansion failed",
            error_code=error_code,
            suggestion=result.suggestion,
            depth=result.depth if hasattr(result, "depth") else None,
            max_depth=result.max_depth if hasattr(result, "max_depth") else None,
        )

    @classmethod
    def collapse_success(
        cls,
        tree: dict[str, Any],
        collapsed_path: str,
    ) -> "PortalResponse":
        """Create response for successful collapse."""
        return cls(
            success=True,
            path="self.portal",
            aspect="collapse",
            tree=tree,
            collapsed_path=collapsed_path,
        )

    @classmethod
    def collapse_failure(
        cls,
        portal_path: str,
        error: str,
    ) -> "PortalResponse":
        """Create response for failed collapse."""
        return cls(
            success=False,
            path="self.portal",
            aspect="collapse",
            error=error,
            error_code="collapse_failed",
            metadata={"portal_path": portal_path},
        )

    @classmethod
    def trail(
        cls,
        trail_id: str,
        step_count: int,
        name: str,
    ) -> "PortalResponse":
        """Create response for trail conversion/save."""
        return cls(
            success=True,
            path="self.portal",
            aspect="trail",
            trail_id=trail_id,
            metadata={
                "step_count": step_count,
                "name": name,
            },
        )

    @classmethod
    def save_trail_success(
        cls,
        trail_id: str,
        name: str,
        step_count: int,
        file_path: str,
        evidence_id: str | None = None,
    ) -> "PortalResponse":
        """Create response for successful trail save."""
        return cls(
            success=True,
            path="self.portal",
            aspect="save_trail",
            trail_id=trail_id,
            evidence_id=evidence_id,
            metadata={
                "name": name,
                "step_count": step_count,
                "file_path": file_path,
            },
        )

    @classmethod
    def save_trail_failure(
        cls,
        error: str,
    ) -> "PortalResponse":
        """Create response for failed trail save."""
        return cls(
            success=False,
            path="self.portal",
            aspect="save_trail",
            error=error,
            error_code="save_failed",
        )

    @classmethod
    def load_trail_success(
        cls,
        trail_id: str,
        name: str,
        step_count: int,
        tree: dict[str, Any] | None = None,
    ) -> "PortalResponse":
        """Create response for successful trail load."""
        return cls(
            success=True,
            path="self.portal",
            aspect="load_trail",
            trail_id=trail_id,
            tree=tree,
            metadata={
                "name": name,
                "step_count": step_count,
            },
        )

    @classmethod
    def load_trail_failure(
        cls,
        trail_id: str,
        error: str,
    ) -> "PortalResponse":
        """Create response for failed trail load."""
        return cls(
            success=False,
            path="self.portal",
            aspect="load_trail",
            error=error,
            error_code="load_failed",
            metadata={"trail_id": trail_id},
        )

    @classmethod
    def list_trails_success(
        cls,
        trails: list[dict[str, Any]],
    ) -> "PortalResponse":
        """Create response for trail listing."""
        return cls(
            success=True,
            path="self.portal",
            aspect="list_trails",
            metadata={
                "trails": trails,
                "count": len(trails),
            },
        )

    @classmethod
    def replay_success(
        cls,
        trail_id: str,
        name: str,
        tree: dict[str, Any],
        step_count: int,
    ) -> "PortalResponse":
        """Create response for successful trail replay."""
        return cls(
            success=True,
            path="self.portal",
            aspect="replay",
            trail_id=trail_id,
            tree=tree,
            metadata={
                "name": name,
                "step_count": step_count,
                "replayed": True,
            },
        )

    @classmethod
    def replay_failure(
        cls,
        trail_id: str,
        error: str,
    ) -> "PortalResponse":
        """Create response for failed replay."""
        return cls(
            success=False,
            path="self.portal",
            aspect="replay",
            error=error,
            error_code="replay_failed",
            metadata={"trail_id": trail_id},
        )


__all__ = ["PortalResponse"]
