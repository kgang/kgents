"""
Portal Resolver: Registry and protocol for portal resource resolution.

Resolves portal URIs to expandable content:
- file: → file contents
- chat: → chat session
- mark: → chat mark with scores
- crystal: → memory crystal
etc.

See: spec/protocols/portal-resource-system.md §IV, §V
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .uri import PortalURI


@dataclass(frozen=True)
class ResolvedResource:
    """
    Result of resolving a portal URI.

    Contains metadata for portal preview and full content for expansion.

    See: spec/protocols/portal-resource-system.md §4.1
    """

    uri: str  # Original URI
    resource_type: str  # "chat", "file", etc.
    exists: bool  # Whether resource exists
    title: str  # Display title
    preview: str  # Short preview text
    content: Any  # Full content (type varies by resource)
    actions: list[str]  # Available actions (["expand", "edit", ...])
    metadata: dict[str, Any]  # Resource-specific metadata


class PortalResolver(Protocol):
    """
    Protocol for resource resolvers.

    Each resource type (chat, file, mark, etc.) implements this protocol
    to resolve URIs of that type.

    See: spec/protocols/portal-resource-system.md §4.1
    """

    @property
    def resource_type(self) -> str:
        """The resource type this resolver handles."""
        ...

    def can_resolve(self, uri: PortalURI) -> bool:
        """
        Check if this resolver can handle the given URI.

        Args:
            uri: Parsed portal URI

        Returns:
            True if this resolver handles this URI type
        """
        ...

    async def resolve(self, uri: PortalURI, observer: Any) -> ResolvedResource:
        """
        Resolve URI to resource metadata (for portal preview).

        Args:
            uri: Parsed portal URI
            observer: Observer context (for access control)

        Returns:
            Resolved resource with metadata and content

        Raises:
            ResourceNotFound: If resource doesn't exist
            PermissionDenied: If observer lacks access
        """
        ...


@dataclass
class PortalResolverRegistry:
    """
    Registry of portal resolvers by resource type.

    Maintains the mapping from resource types to resolvers and
    dispatches resolution requests to the appropriate resolver.

    See: spec/protocols/portal-resource-system.md §4.2

    Law (spec §8.3): Every registered resource type has a resolver.
    """

    _resolvers: dict[str, PortalResolver] = field(default_factory=dict)

    def register(self, resolver: PortalResolver) -> None:
        """
        Register a resolver for a resource type.

        Args:
            resolver: The resolver to register

        Raises:
            ValueError: If a resolver is already registered for this type
        """
        resource_type = resolver.resource_type

        if resource_type in self._resolvers:
            raise ValueError(f"Resolver already registered for type '{resource_type}'")

        self._resolvers[resource_type] = resolver

    def get_resolver(self, uri: PortalURI) -> PortalResolver | None:
        """
        Get resolver for a URI.

        Args:
            uri: Parsed portal URI

        Returns:
            Resolver for this URI type, or None if not found
        """
        return self._resolvers.get(uri.resource_type)

    def has_resolver(self, resource_type: str) -> bool:
        """
        Check if a resolver is registered for a resource type.

        Args:
            resource_type: Resource type to check

        Returns:
            True if a resolver is registered
        """
        return resource_type in self._resolvers

    def list_resource_types(self) -> list[str]:
        """
        List all registered resource types.

        Returns:
            List of resource type names
        """
        return sorted(self._resolvers.keys())

    async def resolve(self, uri: str | PortalURI, observer: Any) -> ResolvedResource:
        """
        Resolve any URI through appropriate resolver.

        Args:
            uri: URI string or parsed PortalURI
            observer: Observer context

        Returns:
            Resolved resource

        Raises:
            ValueError: If URI is malformed
            UnknownResourceType: If no resolver for this type
            ResourceNotFound: If resource doesn't exist
            PermissionDenied: If observer lacks access
        """
        # Parse if string
        if isinstance(uri, str):
            parsed_uri = PortalURI.parse(uri)
        else:
            parsed_uri = uri

        # Get resolver
        resolver = self.get_resolver(parsed_uri)
        if resolver is None:
            raise UnknownResourceType(
                f"No resolver registered for type '{parsed_uri.resource_type}'"
            )

        # Resolve through resolver
        return await resolver.resolve(parsed_uri, observer)


# =============================================================================
# Exceptions
# =============================================================================


class UnknownResourceType(Exception):
    """No resolver registered for this resource type."""

    pass


class ResourceNotFound(Exception):
    """Resource does not exist."""

    pass


class PermissionDenied(Exception):
    """Observer lacks permission to access this resource."""

    pass
