"""
Portal Resolvers: Resource-specific resolvers for portal URIs.

This package contains individual resolver implementations for each
resource type (file, chat, mark, crystal, etc.).

See: spec/protocols/portal-resource-system.md §V
"""

from __future__ import annotations

from .chat import ChatResolver
from .constitutional import ConstitutionalResolver
from .crystal import CrystalResolver
from .evidence import EvidenceResolver
from .file import FileResolver
from .mark import MarkResolver
from .trace import TraceResolver

__all__ = [
    "ChatResolver",
    "ConstitutionalResolver",
    "CrystalResolver",
    "EvidenceResolver",
    "FileResolver",
    "MarkResolver",
    "TraceResolver",
]
