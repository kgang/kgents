"""
Portal Resource System: Universal resource addressing and expansion.

Every kgents concept is addressable. Every address is expandable.

The portal system provides:
- Universal URI syntax for all kgents resources
- Resolver registry for pluggable resource handlers
- Observer-dependent expansion for access control

Resource types:
- file:         Files and paths
- chat:         Chat sessions
- turn:         Specific chat turns
- mark:         ChatMarks with constitutional scores
- crystal:      Memory crystals
- trace:        PolicyTraces
- evidence:     Evidence bundles
- constitutional: Constitutional scores
- witness:      Witness marks
- node:         AGENTESE nodes

See: spec/protocols/portal-resource-system.md

Examples:
    >>> from services.portal import PortalURI, PortalResolverRegistry
    >>> from services.portal.resolvers import FileResolver

    >>> # Parse a URI
    >>> uri = PortalURI.parse("file:spec/protocols/witness.md")
    >>> uri.resource_type
    'file'
    >>> uri.resource_path
    'spec/protocols/witness.md'

    >>> # Set up registry
    >>> registry = PortalResolverRegistry()
    >>> registry.register(FileResolver())

    >>> # Resolve a URI
    >>> resource = await registry.resolve("file:README.md", observer)
    >>> resource.exists
    True
    >>> resource.title
    'README.md'

Philosophy:
    "The portal is the universal reference. The resource comes to you."
    "You don't navigate to the resource. The resource comes to you."

AGENTESE: services.portal
"""

from __future__ import annotations

from .resolver import (
    PermissionDenied,
    PortalResolver,
    PortalResolverRegistry,
    ResolvedResource,
    ResourceNotFound,
    UnknownResourceType,
)
from .resolvers import (
    ChatResolver,
    ConstitutionalResolver,
    CrystalResolver,
    EvidenceResolver,
    FileResolver,
    MarkResolver,
    TraceResolver,
)
from .uri import KNOWN_RESOURCE_TYPES, PortalURI

__all__ = [
    # URI
    "PortalURI",
    "KNOWN_RESOURCE_TYPES",
    # Resolver
    "PortalResolver",
    "PortalResolverRegistry",
    "ResolvedResource",
    # Resolvers
    "ChatResolver",
    "ConstitutionalResolver",
    "CrystalResolver",
    "EvidenceResolver",
    "FileResolver",
    "MarkResolver",
    "TraceResolver",
    # Exceptions
    "UnknownResourceType",
    "ResourceNotFound",
    "PermissionDenied",
]
