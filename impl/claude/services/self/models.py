"""
Self-Reflective OS: Data Models for Codebase K-Blocks.

These models represent Python modules, classes, and functions as K-Blocks,
enabling the system to understand and navigate its own structure.

Philosophy:
    "The proof IS the structure. The mark IS the code."

Each Python module becomes a K-Block with:
- Identity (id, path)
- Content (docstring, summary)
- Structure (classes, functions, imports)
- Coherence (galois_loss at L5 implementation layer)
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Edge:
    """
    Edge between two ModuleKBlocks.

    Represents import relationships and derivation chains.

    Attributes:
        id: Unique edge identifier
        source_id: Source ModuleKBlock ID
        target_id: Target ModuleKBlock ID
        edge_type: Relationship type (imports, derives_from, implements)
        context: Optional description of the relationship
        confidence: Confidence score [0.0, 1.0]
    """

    id: str
    source_id: str
    target_id: str
    edge_type: str  # imports, derives_from, implements
    context: str | None = None
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type,
            "context": self.context,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Edge":
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            edge_type=data["edge_type"],
            context=data.get("context"),
            confidence=data.get("confidence", 1.0),
        )


@dataclass(frozen=True)
class ModuleKBlock:
    """
    K-Block representation of a Python module.

    Captures the essential structure of a module for the Self-Reflective OS.
    This is a lightweight representation optimized for graph operations.

    Attributes:
        id: Unique K-Block identifier
        path: Module path relative to project root
        docstring: Module-level docstring (or None)
        classes: Tuple of class names defined in the module
        functions: Tuple of function names defined in the module
        imports: Tuple of import statements (module paths)
        galois_loss: Coherence metric [0.0, 1.0] at L5 implementation layer
        content_hash: SHA256 hash of source content (first 16 chars)
        created_at: When this K-Block was created

    Philosophy:
        The ModuleKBlock is a "pocket universe" for a Python module.
        It captures enough structure to reason about relationships
        without requiring full source code.
    """

    id: str
    path: str
    docstring: str | None
    classes: tuple[str, ...]
    functions: tuple[str, ...]
    imports: tuple[str, ...]
    galois_loss: float = 0.5  # L5 implementation layer default
    content_hash: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def generate_id(cls, path: str) -> str:
        """Generate a deterministic ID from module path."""
        hash_str = hashlib.sha256(path.encode()).hexdigest()[:12]
        return f"mkb_{hash_str}"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "path": self.path,
            "docstring": self.docstring,
            "classes": list(self.classes),
            "functions": list(self.functions),
            "imports": list(self.imports),
            "galois_loss": self.galois_loss,
            "content_hash": self.content_hash,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModuleKBlock":
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            path=data["path"],
            docstring=data.get("docstring"),
            classes=tuple(data.get("classes", [])),
            functions=tuple(data.get("functions", [])),
            imports=tuple(data.get("imports", [])),
            galois_loss=data.get("galois_loss", 0.5),
            content_hash=data.get("content_hash", ""),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(timezone.utc),
        )

    def __repr__(self) -> str:
        return (
            f"ModuleKBlock(id={self.id!r}, path={self.path!r}, "
            f"classes={len(self.classes)}, functions={len(self.functions)}, "
            f"imports={len(self.imports)})"
        )


@dataclass(frozen=True)
class KBlockGraph:
    """
    Graph of ModuleKBlocks with edges.

    Represents a collection of modules and their relationships,
    suitable for visualization and navigation.

    Attributes:
        nodes: Tuple of ModuleKBlock nodes
        edges: Tuple of Edge relationships between nodes
        root_path: The root directory that was scanned
        scanned_at: When this graph was generated
    """

    nodes: tuple[ModuleKBlock, ...]
    edges: tuple[Edge, ...]
    root_path: str = ""
    scanned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "root_path": self.root_path,
            "scanned_at": self.scanned_at.isoformat(),
            "stats": {
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "avg_galois_loss": sum(n.galois_loss for n in self.nodes) / len(self.nodes)
                if self.nodes
                else 0.0,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KBlockGraph":
        """Deserialize from dictionary."""
        return cls(
            nodes=tuple(ModuleKBlock.from_dict(n) for n in data.get("nodes", [])),
            edges=tuple(Edge.from_dict(e) for e in data.get("edges", [])),
            root_path=data.get("root_path", ""),
            scanned_at=datetime.fromisoformat(data["scanned_at"])
            if "scanned_at" in data
            else datetime.now(timezone.utc),
        )

    def get_node_by_id(self, node_id: str) -> ModuleKBlock | None:
        """Find a node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_node_by_path(self, path: str) -> ModuleKBlock | None:
        """Find a node by module path."""
        for node in self.nodes:
            if node.path == path:
                return node
        return None

    def get_incoming_edges(self, node_id: str) -> list[Edge]:
        """Get all edges pointing to a node."""
        return [e for e in self.edges if e.target_id == node_id]

    def get_outgoing_edges(self, node_id: str) -> list[Edge]:
        """Get all edges from a node."""
        return [e for e in self.edges if e.source_id == node_id]


@dataclass(frozen=True)
class ClassInfo:
    """Information about a class in a module."""

    name: str
    docstring: str | None
    methods: tuple[str, ...]
    base_classes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "docstring": self.docstring,
            "methods": list(self.methods),
            "base_classes": list(self.base_classes),
        }


@dataclass(frozen=True)
class FunctionInfo:
    """Information about a function in a module."""

    name: str
    docstring: str | None
    parameters: tuple[str, ...]
    is_async: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "docstring": self.docstring,
            "parameters": list(self.parameters),
            "is_async": self.is_async,
        }


@dataclass(frozen=True)
class KBlockInspection:
    """
    Deep inspection of a single module.

    Contains detailed information about a module's structure,
    suitable for detailed analysis and navigation.

    Attributes:
        kblock: The ModuleKBlock for this module
        classes: Detailed class information
        functions: Detailed function information
        source_lines: Number of lines in source file
        complexity_score: McCabe complexity estimate
        incoming_deps: Modules that import this module
        outgoing_deps: Modules this module imports
    """

    kblock: ModuleKBlock
    classes: tuple[ClassInfo, ...]
    functions: tuple[FunctionInfo, ...]
    source_lines: int = 0
    complexity_score: float = 0.0
    incoming_deps: tuple[str, ...] = ()
    outgoing_deps: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "kblock": self.kblock.to_dict(),
            "classes": [c.to_dict() for c in self.classes],
            "functions": [f.to_dict() for f in self.functions],
            "source_lines": self.source_lines,
            "complexity_score": self.complexity_score,
            "incoming_deps": list(self.incoming_deps),
            "outgoing_deps": list(self.outgoing_deps),
        }


@dataclass(frozen=True)
class DerivationChain:
    """
    Derivation chain for a module.

    Traces the import/derivation path from a module back to its roots.
    This enables understanding why a module exists and what it depends on.

    Attributes:
        target_id: The module ID being traced
        target_path: The module path being traced
        chain: List of (node_id, edge_type, context) tuples from target to roots
        depth: Maximum depth of the derivation chain
    """

    target_id: str
    target_path: str
    chain: tuple[tuple[str, str, str | None], ...]  # (node_id, edge_type, context)
    depth: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "target_id": self.target_id,
            "target_path": self.target_path,
            "chain": [
                {"node_id": node_id, "edge_type": edge_type, "context": context}
                for node_id, edge_type, context in self.chain
            ],
            "depth": self.depth,
        }


# Backward compatibility aliases
ConstitutionalGraph = KBlockGraph


__all__ = [
    "Edge",
    "ModuleKBlock",
    "KBlockGraph",
    "ClassInfo",
    "FunctionInfo",
    "KBlockInspection",
    "DerivationChain",
    "ConstitutionalGraph",
]
