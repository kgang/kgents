"""
Mind-Map Topology Engine: Treating mind-maps as formal topological spaces.

This module implements the Mind-Map as Topological Space concept from the
Formal Verification Metatheory. Mind-maps become topological spaces where:
- Nodes are open sets
- Edges are continuous maps
- Clusters are covers
- Coherence satisfies the sheaf gluing condition

> "Local perspectives cohere into global meaning."
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Iterator

from .aesthetic import (
    ErrorCategory,
    ProgressiveResult,
    Severity,
    VerificationError,
    create_progressive_result,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Core Data Structures
# =============================================================================

class MappingType(str, Enum):
    """Types of continuous maps between open sets."""

    INCLUSION = "inclusion"  # Subset relationship
    PROJECTION = "projection"  # Quotient/collapse
    COMPOSITION = "composition"  # Derived from other maps
    REFERENCE = "reference"  # Explicit link
    SEMANTIC = "semantic"  # Meaning-based connection


@dataclass(frozen=True)
class TopologicalNode:
    """
    A node as an open set in the topology.
    
    Each node represents a concept with its own "neighborhood" —
    the set of adjacent concepts that form its local context.
    """

    id: str
    content: str
    node_type: str = "concept"  # concept, principle, requirement, etc.
    metadata: dict[str, Any] = field(default_factory=dict)
    neighborhood: frozenset[str] = field(default_factory=frozenset)

    def __hash__(self) -> int:
        return hash(self.id)

    def with_neighbor(self, neighbor_id: str) -> TopologicalNode:
        """Return new node with additional neighbor."""
        return TopologicalNode(
            id=self.id,
            content=self.content,
            node_type=self.node_type,
            metadata=self.metadata,
            neighborhood=self.neighborhood | {neighbor_id},
        )


@dataclass(frozen=True)
class ContinuousMap:
    """
    An edge as a continuous map between open sets.
    
    Continuous maps preserve the topological structure —
    nearby points map to nearby points.
    """

    source: str
    target: str
    mapping_type: MappingType
    label: str = ""
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash((self.source, self.target, self.mapping_type))


@dataclass(frozen=True)
class Cover:
    """
    A cover of the topological space.
    
    A cover is a collection of open sets whose union contains the space.
    Clusters in a mind-map form natural covers.
    """

    cover_id: str
    name: str
    member_ids: frozenset[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.cover_id)

    def overlaps_with(self, other: Cover) -> frozenset[str]:
        """Return the overlap (intersection) with another cover."""
        return self.member_ids & other.member_ids


# =============================================================================
# Sheaf Verification
# =============================================================================

@dataclass(frozen=True)
class LocalSection:
    """
    A local section of a sheaf over an open set.
    
    Represents data/meaning assigned to a region of the topology.
    """

    open_set_id: str
    value: Any
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SheafVerification:
    """Result of sheaf condition verification."""

    is_valid: bool
    conflicts: list[CoherenceConflict]
    global_section: dict[str, Any] | None
    verification_details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CoherenceConflict:
    """
    A conflict where the sheaf condition fails.
    
    This happens when local sections disagree on their overlap.
    """

    conflict_id: str
    overlap_region: frozenset[str]
    conflicting_sections: tuple[LocalSection, ...]
    description: str
    severity: Severity = Severity.CONCERN


@dataclass(frozen=True)
class RepairSuggestion:
    """A suggested repair for a coherence conflict."""

    conflict_id: str
    suggestion_type: str  # "merge", "split", "constrain", "remove"
    description: str
    proposed_value: Any | None = None
    confidence: float = 0.5


# =============================================================================
# Mind-Map Topology
# =============================================================================

@dataclass
class MindMapTopology:
    """
    Mind-map as a topological space with sheaf structure.
    
    This is the core data structure for treating mind-maps formally.
    It supports:
    - Topological operations (neighborhoods, covers)
    - Sheaf verification (local-to-global coherence)
    - Conflict detection and repair suggestions
    """

    nodes: dict[str, TopologicalNode] = field(default_factory=dict)
    edges: dict[str, ContinuousMap] = field(default_factory=dict)
    covers: dict[str, Cover] = field(default_factory=dict)
    local_sections: dict[str, LocalSection] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    # ==========================================================================
    # Construction
    # ==========================================================================

    def add_node(self, node: TopologicalNode) -> None:
        """Add a node to the topology."""
        self.nodes[node.id] = node

    def add_edge(self, edge: ContinuousMap) -> None:
        """Add an edge and update neighborhoods."""
        edge_id = f"{edge.source}->{edge.target}"
        self.edges[edge_id] = edge

        # Update neighborhoods
        if edge.source in self.nodes:
            self.nodes[edge.source] = self.nodes[edge.source].with_neighbor(edge.target)
        if edge.target in self.nodes:
            self.nodes[edge.target] = self.nodes[edge.target].with_neighbor(edge.source)

    def add_cover(self, cover: Cover) -> None:
        """Add a cover (cluster) to the topology."""
        self.covers[cover.cover_id] = cover

    def add_local_section(self, section: LocalSection) -> None:
        """Add a local section for sheaf structure."""
        self.local_sections[section.open_set_id] = section

    # ==========================================================================
    # Topological Operations
    # ==========================================================================

    def get_neighborhood(self, node_id: str) -> frozenset[str]:
        """Get the neighborhood of a node."""
        if node_id not in self.nodes:
            return frozenset()
        return self.nodes[node_id].neighborhood

    def get_connected_component(self, start_id: str) -> frozenset[str]:
        """Get the connected component containing a node."""
        if start_id not in self.nodes:
            return frozenset()

        visited: set[str] = set()
        to_visit = [start_id]

        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)

            # Add neighbors
            if current in self.nodes:
                for neighbor in self.nodes[current].neighborhood:
                    if neighbor not in visited:
                        to_visit.append(neighbor)

        return frozenset(visited)

    def is_connected(self) -> bool:
        """Check if the topology is connected."""
        if not self.nodes:
            return True

        first_node = next(iter(self.nodes.keys()))
        component = self.get_connected_component(first_node)
        return len(component) == len(self.nodes)

    def get_boundary(self, region: frozenset[str]) -> frozenset[str]:
        """Get the boundary of a region (nodes with neighbors outside)."""
        boundary: set[str] = set()

        for node_id in region:
            if node_id in self.nodes:
                for neighbor in self.nodes[node_id].neighborhood:
                    if neighbor not in region:
                        boundary.add(node_id)
                        break

        return frozenset(boundary)

    # ==========================================================================
    # Sheaf Verification
    # ==========================================================================

    def verify_sheaf_condition(self) -> SheafVerification:
        """
        Verify the sheaf gluing condition.
        
        For each pair of overlapping covers, check that local sections
        agree on the overlap. If they do, construct the global section.
        """

        conflicts: list[CoherenceConflict] = []

        # Check all pairs of covers for overlap agreement
        cover_list = list(self.covers.values())
        for i, cover1 in enumerate(cover_list):
            for cover2 in cover_list[i + 1:]:
                overlap = cover1.overlaps_with(cover2)

                if overlap:
                    # Check agreement on overlap
                    conflict = self._check_overlap_agreement(cover1, cover2, overlap)
                    if conflict:
                        conflicts.append(conflict)

        # Try to construct global section
        global_section = None
        if not conflicts:
            global_section = self._construct_global_section()

        return SheafVerification(
            is_valid=len(conflicts) == 0,
            conflicts=conflicts,
            global_section=global_section,
            verification_details={
                "covers_checked": len(cover_list),
                "overlaps_found": sum(
                    1 for i, c1 in enumerate(cover_list)
                    for c2 in cover_list[i + 1:]
                    if c1.overlaps_with(c2)
                ),
            },
        )

    def _check_overlap_agreement(
        self,
        cover1: Cover,
        cover2: Cover,
        overlap: frozenset[str],
    ) -> CoherenceConflict | None:
        """Check if local sections agree on overlap region."""

        conflicting_sections: list[LocalSection] = []

        for node_id in overlap:
            if node_id in self.local_sections:
                section = self.local_sections[node_id]

                # Check if this section conflicts with others
                for existing in conflicting_sections:
                    if existing.value != section.value:
                        return CoherenceConflict(
                            conflict_id=f"conflict_{cover1.cover_id}_{cover2.cover_id}",
                            overlap_region=overlap,
                            conflicting_sections=(existing, section),
                            description=(
                                f"Local sections disagree on overlap between "
                                f"'{cover1.name}' and '{cover2.name}': "
                                f"'{existing.value}' vs '{section.value}'"
                            ),
                        )

                conflicting_sections.append(section)

        return None

    def _construct_global_section(self) -> dict[str, Any]:
        """Construct global section from local sections."""

        global_section: dict[str, Any] = {}

        for section in self.local_sections.values():
            global_section[section.open_set_id] = section.value

        return global_section

    def identify_conflicts(self) -> list[CoherenceConflict]:
        """Identify all coherence conflicts in the topology."""

        verification = self.verify_sheaf_condition()
        return verification.conflicts

    def suggest_repairs(self, conflict: CoherenceConflict) -> list[RepairSuggestion]:
        """Suggest repairs for a coherence conflict."""

        suggestions: list[RepairSuggestion] = []

        if len(conflict.conflicting_sections) >= 2:
            section1, section2 = conflict.conflicting_sections[:2]

            # Suggestion 1: Merge values
            suggestions.append(RepairSuggestion(
                conflict_id=conflict.conflict_id,
                suggestion_type="merge",
                description=(
                    "Merge the conflicting values into a combined representation "
                    "that captures both perspectives."
                ),
                proposed_value={"merged": [section1.value, section2.value]},
                confidence=0.6,
            ))

            # Suggestion 2: Add constraint
            suggestions.append(RepairSuggestion(
                conflict_id=conflict.conflict_id,
                suggestion_type="constrain",
                description=(
                    "Add a constraint that specifies when each value applies, "
                    "making the overlap more precise."
                ),
                confidence=0.7,
            ))

            # Suggestion 3: Split the overlap
            suggestions.append(RepairSuggestion(
                conflict_id=conflict.conflict_id,
                suggestion_type="split",
                description=(
                    "Split the overlap region into non-overlapping parts, "
                    "each with a single consistent value."
                ),
                confidence=0.5,
            ))

        return suggestions


# =============================================================================
# Import/Export
# =============================================================================

class ObsidianImporter:
    """Import mind-maps from Obsidian markdown format."""

    def __init__(self):
        self.link_pattern = r'\[\[([^\]]+)\]\]'

    def import_vault(self, vault_path: Path) -> MindMapTopology:
        """Import an Obsidian vault as a topology."""
        import re

        topology = MindMapTopology()

        # Find all markdown files
        md_files = list(vault_path.glob("**/*.md"))

        for md_file in md_files:
            # Create node for each file
            node_id = self._file_to_id(md_file, vault_path)
            content = md_file.read_text(encoding="utf-8")

            # Extract metadata from frontmatter if present
            metadata = self._extract_frontmatter(content)

            node = TopologicalNode(
                id=node_id,
                content=self._extract_content(content),
                node_type=metadata.get("type", "note"),
                metadata=metadata,
            )
            topology.add_node(node)

            # Find links to create edges
            links = re.findall(self.link_pattern, content)
            for link in links:
                target_id = self._normalize_link(link)
                edge = ContinuousMap(
                    source=node_id,
                    target=target_id,
                    mapping_type=MappingType.REFERENCE,
                    label=link,
                )
                topology.add_edge(edge)

        # Auto-detect covers from folder structure
        self._create_folder_covers(topology, vault_path, md_files)

        return topology

    def _file_to_id(self, file_path: Path, vault_path: Path) -> str:
        """Convert file path to node ID."""
        relative = file_path.relative_to(vault_path)
        return str(relative.with_suffix("")).replace("/", ".")

    def _normalize_link(self, link: str) -> str:
        """Normalize an Obsidian link to a node ID."""
        # Remove any heading references
        if "#" in link:
            link = link.split("#")[0]
        # Remove any alias
        if "|" in link:
            link = link.split("|")[0]
        return link.replace("/", ".").strip()

    def _extract_frontmatter(self, content: str) -> dict[str, Any]:
        """Extract YAML frontmatter from markdown."""
        if not content.startswith("---"):
            return {}

        try:
            end = content.index("---", 3)
            frontmatter = content[3:end].strip()
            # Simple YAML parsing (key: value)
            metadata = {}
            for line in frontmatter.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()
            return metadata
        except (ValueError, IndexError):
            return {}

    def _extract_content(self, content: str) -> str:
        """Extract main content without frontmatter."""
        if content.startswith("---"):
            try:
                end = content.index("---", 3)
                return content[end + 3:].strip()
            except ValueError:
                pass
        return content

    def _create_folder_covers(
        self,
        topology: MindMapTopology,
        vault_path: Path,
        md_files: list[Path],
    ) -> None:
        """Create covers from folder structure."""

        folders: dict[str, set[str]] = {}

        for md_file in md_files:
            relative = md_file.relative_to(vault_path)
            folder = str(relative.parent) if relative.parent != Path(".") else "root"
            node_id = self._file_to_id(md_file, vault_path)

            if folder not in folders:
                folders[folder] = set()
            folders[folder].add(node_id)

        for folder_name, node_ids in folders.items():
            cover = Cover(
                cover_id=f"folder_{folder_name}",
                name=folder_name,
                member_ids=frozenset(node_ids),
            )
            topology.add_cover(cover)


def import_from_obsidian(vault_path: str | Path) -> MindMapTopology:
    """Convenience function to import from Obsidian."""
    importer = ObsidianImporter()
    return importer.import_vault(Path(vault_path))


# =============================================================================
# Visualization Data
# =============================================================================

@dataclass
class TopologyVisualization:
    """Data for visualizing the topology."""

    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    covers: list[dict[str, Any]]
    conflicts: list[dict[str, Any]]
    metadata: dict[str, Any]


def create_visualization_data(topology: MindMapTopology) -> TopologyVisualization:
    """Create visualization data from topology."""

    from .aesthetic import LivingEarthPalette

    # Verify sheaf condition
    verification = topology.verify_sheaf_condition()

    # Create node data
    nodes = []
    for node in topology.nodes.values():
        nodes.append({
            "id": node.id,
            "label": node.content[:50] + "..." if len(node.content) > 50 else node.content,
            "type": node.node_type,
            "color": LivingEarthPalette.MOSS if node.node_type == "principle" else LivingEarthPalette.STREAM,
            "size": len(node.neighborhood) + 1,
        })

    # Create edge data
    edges = []
    for edge in topology.edges.values():
        edges.append({
            "source": edge.source,
            "target": edge.target,
            "type": edge.mapping_type.value,
            "label": edge.label,
            "weight": edge.weight,
        })

    # Create cover data
    covers = []
    for cover in topology.covers.values():
        covers.append({
            "id": cover.cover_id,
            "name": cover.name,
            "members": list(cover.member_ids),
            "color": LivingEarthPalette.SPRING_LEAF,
        })

    # Create conflict data
    conflicts = []
    for conflict in verification.conflicts:
        conflicts.append({
            "id": conflict.conflict_id,
            "region": list(conflict.overlap_region),
            "description": conflict.description,
            "severity": conflict.severity.value,
            "color": LivingEarthPalette.CONCERN,
        })

    return TopologyVisualization(
        nodes=nodes,
        edges=edges,
        covers=covers,
        conflicts=conflicts,
        metadata={
            "is_connected": topology.is_connected(),
            "sheaf_valid": verification.is_valid,
            "node_count": len(topology.nodes),
            "edge_count": len(topology.edges),
        },
    )
