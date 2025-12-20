"""
Graph Engine: Derivation graph construction from specifications.

Builds verification graphs showing logical dependencies and derivations
from high-level principles to operational implementation, with support
for contradiction detection and orphaned node identification.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from uuid import uuid4

from .contracts import (
    Contradiction,
    DerivationPath,
    GraphEdge,
    GraphNode,
    VerificationGraphResult,
    VerificationStatus,
)

logger = logging.getLogger(__name__)


class GraphEngine:
    """
    Engine for constructing and analyzing verification graphs.
    
    Builds directed graphs representing logical derivations from principles
    to implementation, with analysis for contradictions and completeness.
    """

    def __init__(self):
        self.principles_cache: dict[str, GraphNode] = {}
        self.spec_cache: dict[str, list[GraphNode]] = {}

    async def build_graph_from_specification(
        self,
        spec_path: str,
        name: str | None = None,
    ) -> VerificationGraphResult:
        """
        Build verification graph from specification documents.
        
        Analyzes requirements, design, and task documents to construct
        a graph showing derivation paths from principles to implementation.
        """

        logger.info(f"Building verification graph from specification: {spec_path}")

        # Parse specification documents
        spec_data = await self._parse_specification_documents(spec_path)

        # Extract nodes and edges
        nodes = await self._extract_nodes(spec_data)
        edges = await self._extract_edges(nodes, spec_data)

        # Analyze graph structure
        contradictions = await self._detect_contradictions(nodes, edges)
        orphaned_nodes = await self._find_orphaned_nodes(nodes, edges)
        derivation_paths = await self._analyze_derivation_paths(nodes, edges)

        # Determine overall status
        status = self._determine_status(contradictions, orphaned_nodes, derivation_paths)

        graph_name = name or f"Verification Graph for {Path(spec_path).name}"

        result = VerificationGraphResult(
            graph_id=str(uuid4()),
            name=graph_name,
            nodes=nodes,
            edges=edges,
            contradictions=contradictions,
            orphaned_nodes=[node.node_id for node in orphaned_nodes],
            derivation_paths=derivation_paths,
            status=status,
            created_at=None,  # Will be set by persistence layer
        )

        logger.info(f"Built verification graph with {len(nodes)} nodes, {len(edges)} edges")

        return result

    async def _parse_specification_documents(self, spec_path: str) -> dict[str, Any]:
        """Parse specification documents to extract structured data."""

        spec_dir = Path(spec_path)

        # Look for standard specification files
        requirements_file = spec_dir / "requirements.md"
        design_file = spec_dir / "design.md"
        tasks_file = spec_dir / "tasks.md"

        spec_data = {
            "requirements": None,
            "design": None,
            "tasks": None,
            "principles": [],
            "concepts": [],
            "implementations": [],
        }

        # Parse requirements document
        if requirements_file.exists():
            spec_data["requirements"] = await self._parse_requirements_document(requirements_file)

        # Parse design document
        if design_file.exists():
            spec_data["design"] = await self._parse_design_document(design_file)

        # Parse tasks document
        if tasks_file.exists():
            spec_data["tasks"] = await self._parse_tasks_document(tasks_file)

        # Extract cross-cutting elements
        spec_data["principles"] = await self._extract_principles(spec_data)
        spec_data["concepts"] = await self._extract_concepts(spec_data)
        spec_data["implementations"] = await self._extract_implementations(spec_data)

        return spec_data

    async def _parse_requirements_document(self, file_path: Path) -> dict[str, Any]:
        """Parse requirements.md to extract user stories and acceptance criteria."""

        try:
            content = file_path.read_text(encoding="utf-8")

            # TODO: Implement proper markdown parsing
            # For now, return basic structure
            return {
                "content": content,
                "user_stories": [],  # Extract from "User Story:" sections
                "acceptance_criteria": [],  # Extract from "Acceptance Criteria" sections
                "glossary": {},  # Extract from "Glossary" section
            }

        except Exception as e:
            logger.warning(f"Failed to parse requirements document {file_path}: {e}")
            return {}

    async def _parse_design_document(self, file_path: Path) -> dict[str, Any]:
        """Parse design.md to extract architecture and components."""

        try:
            content = file_path.read_text(encoding="utf-8")

            # TODO: Implement proper markdown parsing
            # For now, return basic structure
            return {
                "content": content,
                "architecture": {},  # Extract from "Architecture" section
                "components": [],  # Extract component definitions
                "data_models": [],  # Extract from "Data Models" section
                "correctness_properties": [],  # Extract from "Correctness Properties"
            }

        except Exception as e:
            logger.warning(f"Failed to parse design document {file_path}: {e}")
            return {}

    async def _parse_tasks_document(self, file_path: Path) -> dict[str, Any]:
        """Parse tasks.md to extract implementation tasks."""

        try:
            content = file_path.read_text(encoding="utf-8")

            # TODO: Implement proper markdown parsing
            # For now, return basic structure
            return {
                "content": content,
                "tasks": [],  # Extract task list items
                "checkpoints": [],  # Extract checkpoint tasks
                "requirements_mapping": {},  # Extract requirement references
            }

        except Exception as e:
            logger.warning(f"Failed to parse tasks document {file_path}: {e}")
            return {}

    async def _extract_nodes(self, spec_data: dict[str, Any]) -> list[GraphNode]:
        """Extract nodes from specification data."""

        nodes = []

        # Add principle nodes (from kgents 7 principles)
        principle_nodes = await self._create_principle_nodes()
        nodes.extend(principle_nodes)

        # Add requirement nodes
        if spec_data.get("requirements"):
            req_nodes = await self._create_requirement_nodes(spec_data["requirements"])
            nodes.extend(req_nodes)

        # Add design nodes
        if spec_data.get("design"):
            design_nodes = await self._create_design_nodes(spec_data["design"])
            nodes.extend(design_nodes)

        # Add implementation nodes
        if spec_data.get("tasks"):
            impl_nodes = await self._create_implementation_nodes(spec_data["tasks"])
            nodes.extend(impl_nodes)

        return nodes

    async def _create_principle_nodes(self) -> list[GraphNode]:
        """Create nodes for the 7 kgents principles."""

        principles = [
            ("tasteful", "Tasteful", "Each agent serves a clear, justified purpose"),
            ("curated", "Curated", "Intentional selection over exhaustive cataloging"),
            ("ethical", "Ethical", "Agents augment human capability, never replace judgment"),
            ("joy_inducing", "Joy-Inducing", "Delight in interaction; personality matters"),
            ("composable", "Composable", "Agents are morphisms in a category; composition is primary"),
            ("heterarchical", "Heterarchical", "Agents exist in flux, not fixed hierarchy"),
            ("generative", "Generative", "Spec is compression; design should generate implementation"),
        ]

        nodes = []
        for principle_id, name, description in principles:
            node = GraphNode(
                node_id=f"principle_{principle_id}",
                node_type="principle",
                name=name,
                description=description,
                metadata={"category": "kgents_principle", "priority": len(nodes) + 1},
            )
            nodes.append(node)

        return nodes

    async def _create_requirement_nodes(self, requirements_data: dict[str, Any]) -> list[GraphNode]:
        """Create nodes from requirements document."""

        nodes = []

        # TODO: Parse actual requirements from markdown
        # For now, create placeholder nodes
        for i in range(3):  # Placeholder: 3 requirement nodes
            node = GraphNode(
                node_id=f"requirement_{i+1}",
                node_type="requirement",
                name=f"Requirement {i+1}",
                description=f"Placeholder requirement {i+1}",
                metadata={"source": "requirements.md"},
            )
            nodes.append(node)

        return nodes

    async def _create_design_nodes(self, design_data: dict[str, Any]) -> list[GraphNode]:
        """Create nodes from design document."""

        nodes = []

        # TODO: Parse actual design elements from markdown
        # For now, create placeholder nodes
        design_elements = [
            ("architecture", "System Architecture", "Overall system design"),
            ("components", "Core Components", "Main system components"),
            ("data_models", "Data Models", "Data structure definitions"),
        ]

        for element_id, name, description in design_elements:
            node = GraphNode(
                node_id=f"design_{element_id}",
                node_type="design",
                name=name,
                description=description,
                metadata={"source": "design.md"},
            )
            nodes.append(node)

        return nodes

    async def _create_implementation_nodes(self, tasks_data: dict[str, Any]) -> list[GraphNode]:
        """Create nodes from tasks document."""

        nodes = []

        # TODO: Parse actual tasks from markdown
        # For now, create placeholder nodes
        for i in range(5):  # Placeholder: 5 implementation nodes
            node = GraphNode(
                node_id=f"implementation_{i+1}",
                node_type="implementation",
                name=f"Implementation Task {i+1}",
                description=f"Placeholder implementation task {i+1}",
                metadata={"source": "tasks.md"},
            )
            nodes.append(node)

        return nodes

    async def _extract_edges(
        self,
        nodes: list[GraphNode],
        spec_data: dict[str, Any],
    ) -> list[GraphEdge]:
        """Extract derivation edges between nodes."""

        edges = []

        # Create derivation edges from principles to requirements
        principle_nodes = [n for n in nodes if n.node_type == "principle"]
        requirement_nodes = [n for n in nodes if n.node_type == "requirement"]

        for req_node in requirement_nodes:
            # TODO: Determine actual principle derivations from content analysis
            # For now, connect each requirement to the "composable" principle
            composable_principle = next(
                (p for p in principle_nodes if "composable" in p.node_id),
                None
            )
            if composable_principle:
                edge = GraphEdge(
                    source_id=composable_principle.node_id,
                    target_id=req_node.node_id,
                    derivation_type="derives_from",
                    confidence=0.8,  # Placeholder confidence
                )
                edges.append(edge)

        # Create edges from requirements to design
        design_nodes = [n for n in nodes if n.node_type == "design"]

        for design_node in design_nodes:
            for req_node in requirement_nodes:
                edge = GraphEdge(
                    source_id=req_node.node_id,
                    target_id=design_node.node_id,
                    derivation_type="implements",
                    confidence=0.7,
                )
                edges.append(edge)

        # Create edges from design to implementation
        impl_nodes = [n for n in nodes if n.node_type == "implementation"]

        for impl_node in impl_nodes:
            for design_node in design_nodes:
                edge = GraphEdge(
                    source_id=design_node.node_id,
                    target_id=impl_node.node_id,
                    derivation_type="implements",
                    confidence=0.9,
                )
                edges.append(edge)

        return edges

    async def _detect_contradictions(
        self,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
    ) -> list[Contradiction]:
        """Detect contradictions in the verification graph."""

        contradictions = []

        # 1. Detect circular dependencies
        circular_deps = await self._detect_circular_dependencies(nodes, edges)
        contradictions.extend(circular_deps)

        # 2. Detect mutually exclusive requirements
        exclusive_conflicts = await self._detect_exclusive_conflicts(nodes)
        contradictions.extend(exclusive_conflicts)

        # 3. Detect resource conflicts
        resource_conflicts = await self._detect_resource_conflicts(nodes)
        contradictions.extend(resource_conflicts)

        # 4. Detect semantic contradictions
        semantic_conflicts = await self._detect_semantic_contradictions(nodes)
        contradictions.extend(semantic_conflicts)

        # 5. Detect over-specification
        over_spec = await self._detect_over_specification(nodes, edges)
        if over_spec:
            contradictions.append(over_spec)

        return contradictions

    async def _detect_circular_dependencies(
        self,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
    ) -> list[Contradiction]:
        """Detect circular dependencies in the derivation graph."""

        contradictions = []

        # Build adjacency list
        graph = {}
        for edge in edges:
            if edge.source_id not in graph:
                graph[edge.source_id] = []
            graph[edge.source_id].append(edge.target_id)

        # DFS to detect cycles
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str, path: list[str]) -> list[str] | None:
            if node_id in rec_stack:
                # Found cycle - return the cycle path
                cycle_start = path.index(node_id)
                return path[cycle_start:] + [node_id]

            if node_id in visited:
                return None

            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in graph.get(node_id, []):
                cycle = has_cycle(neighbor, path + [node_id])
                if cycle:
                    return cycle

            rec_stack.remove(node_id)
            return None

        # Check each node for cycles
        for node in nodes:
            if node.node_id not in visited:
                cycle = has_cycle(node.node_id, [])
                if cycle:
                    contradiction = Contradiction(
                        node_ids=cycle,
                        description=f"Circular dependency detected: {' -> '.join(cycle)}",
                        resolution_strategies=[
                            "Break the circular dependency by removing or redirecting one edge",
                            "Introduce intermediate abstraction to resolve the cycle",
                            "Reconsider the derivation logic for conflicting elements",
                        ],
                        severity="high",
                    )
                    contradictions.append(contradiction)

        return contradictions

    async def _detect_exclusive_conflicts(self, nodes: list[GraphNode]) -> list[Contradiction]:
        """Detect mutually exclusive requirements or design decisions."""

        contradictions = []

        # Look for conflicting keywords in node descriptions
        conflict_patterns = [
            (["synchronous", "asynchronous"], "Synchronous vs Asynchronous conflict"),
            (["stateful", "stateless"], "Stateful vs Stateless conflict"),
            (["centralized", "distributed"], "Centralized vs Distributed conflict"),
            (["mutable", "immutable"], "Mutable vs Immutable conflict"),
            (["blocking", "non-blocking"], "Blocking vs Non-blocking conflict"),
        ]

        for conflict_keywords, conflict_desc in conflict_patterns:
            conflicting_nodes = []

            for keyword in conflict_keywords:
                matching_nodes = [
                    node for node in nodes
                    if keyword.lower() in node.description.lower() or keyword.lower() in node.name.lower()
                ]
                if matching_nodes:
                    conflicting_nodes.extend(matching_nodes)

            # If we found nodes with conflicting keywords
            if len(set(node.node_id for node in conflicting_nodes)) > 1:
                unique_nodes = list({node.node_id: node for node in conflicting_nodes}.values())
                if len(unique_nodes) >= 2:
                    contradiction = Contradiction(
                        node_ids=[node.node_id for node in unique_nodes],
                        description=f"{conflict_desc} detected between: {', '.join(node.name for node in unique_nodes)}",
                        resolution_strategies=[
                            "Choose one approach and update conflicting specifications",
                            "Clarify the context where each approach applies",
                            "Design a hybrid solution that accommodates both needs",
                        ],
                        severity="medium",
                    )
                    contradictions.append(contradiction)

        return contradictions

    async def _detect_resource_conflicts(self, nodes: list[GraphNode]) -> list[Contradiction]:
        """Detect resource allocation conflicts."""

        contradictions = []

        # Look for resource-related conflicts
        resource_keywords = ["memory", "cpu", "storage", "bandwidth", "database", "cache"]

        resource_nodes = []
        for node in nodes:
            node_text = f"{node.name} {node.description}".lower()
            if any(keyword in node_text for keyword in resource_keywords):
                resource_nodes.append(node)

        # Simple heuristic: if multiple implementation nodes mention the same resource
        # and have high confidence edges, there might be a conflict
        if len(resource_nodes) > 2:
            contradiction = Contradiction(
                node_ids=[node.node_id for node in resource_nodes[:3]],  # Limit to first 3
                description="Potential resource allocation conflict detected",
                resolution_strategies=[
                    "Review resource requirements and allocation strategy",
                    "Consider resource pooling or sharing mechanisms",
                    "Implement resource monitoring and throttling",
                ],
                severity="low",
            )
            contradictions.append(contradiction)

        return contradictions

    async def _detect_semantic_contradictions(self, nodes: list[GraphNode]) -> list[Contradiction]:
        """Detect semantic contradictions in node content."""

        contradictions = []

        # Look for negation patterns that might indicate contradictions
        negation_patterns = [
            ("must", "must not"),
            ("shall", "shall not"),
            ("should", "should not"),
            ("will", "will not"),
            ("always", "never"),
            ("required", "optional"),
            ("mandatory", "forbidden"),
        ]

        for positive, negative in negation_patterns:
            positive_nodes = []
            negative_nodes = []

            for node in nodes:
                node_text = f"{node.name} {node.description}".lower()
                if positive in node_text:
                    positive_nodes.append(node)
                if negative in node_text:
                    negative_nodes.append(node)

            # If we have both positive and negative assertions
            if positive_nodes and negative_nodes:
                all_conflicting = positive_nodes + negative_nodes
                contradiction = Contradiction(
                    node_ids=[node.node_id for node in all_conflicting[:4]],  # Limit to 4 nodes
                    description=f"Semantic contradiction: Found both '{positive}' and '{negative}' assertions",
                    resolution_strategies=[
                        "Clarify the scope and context for each assertion",
                        "Resolve the contradiction by choosing one approach",
                        "Add conditional logic to handle both cases appropriately",
                    ],
                    severity="medium",
                )
                contradictions.append(contradiction)

        return contradictions

    async def _detect_over_specification(
        self,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
    ) -> Contradiction | None:
        """Detect over-specification (too many derivation paths)."""

        # Heuristic: if we have more than 2x edges than nodes, might be over-specified
        if len(edges) > len(nodes) * 2:
            # Find nodes with high in-degree (many things derive from them)
            in_degree = {}
            for edge in edges:
                in_degree[edge.target_id] = in_degree.get(edge.target_id, 0) + 1

            high_degree_nodes = [
                node_id for node_id, degree in in_degree.items()
                if degree > 3  # More than 3 incoming edges
            ]

            if high_degree_nodes:
                return Contradiction(
                    node_ids=high_degree_nodes[:3],  # Limit to first 3
                    description="Potential over-specification detected: Some elements have too many derivation sources",
                    resolution_strategies=[
                        "Consolidate related derivation sources",
                        "Review if all derivations are necessary",
                        "Simplify the specification hierarchy",
                        "Group related concepts into higher-level abstractions",
                    ],
                    severity="low",
                )

        return None

    async def _find_orphaned_nodes(
        self,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
    ) -> list[GraphNode]:
        """Find nodes without principled derivation (orphaned nodes)."""

        orphaned = []

        # Build sets of connected nodes
        source_nodes = {edge.source_id for edge in edges}
        target_nodes = {edge.target_id for edge in edges}

        # Find nodes that are not targets (no incoming edges)
        # These might be orphaned if they're not principles
        nodes_without_incoming = []
        for node in nodes:
            if node.node_id not in target_nodes and node.node_type != "principle":
                nodes_without_incoming.append(node)

        # Find nodes that are not sources (no outgoing edges)
        # These might be orphaned if they're not implementations
        nodes_without_outgoing = []
        for node in nodes:
            if node.node_id not in source_nodes and node.node_type != "implementation":
                nodes_without_outgoing.append(node)

        # Find nodes completely disconnected from the graph
        connected_nodes = source_nodes | target_nodes
        for node in nodes:
            if node.node_id not in connected_nodes:
                # Skip principles - they're roots by definition
                if node.node_type != "principle":
                    orphaned.append(node)

        # Find implementation nodes without clear derivation from principles
        principle_nodes = {n.node_id for n in nodes if n.node_type == "principle"}
        impl_nodes = [n for n in nodes if n.node_type == "implementation"]

        for impl_node in impl_nodes:
            # Check if there's a path from any principle to this implementation
            has_principle_path = False
            for principle_id in principle_nodes:
                path = await self._find_path(principle_id, impl_node.node_id, edges)
                if path and len(path) > 1:  # More than just the principle itself
                    has_principle_path = True
                    break

            if not has_principle_path:
                orphaned.append(impl_node)

        # Remove duplicates while preserving order
        seen = set()
        unique_orphaned = []
        for node in orphaned:
            if node.node_id not in seen:
                seen.add(node.node_id)
                unique_orphaned.append(node)

        return unique_orphaned

    async def generate_resolution_strategies(
        self,
        contradictions: list[Contradiction],
        orphaned_nodes: list[GraphNode],
    ) -> dict[str, list[str]]:
        """Generate resolution strategies for detected issues."""

        strategies = {
            "contradictions": [],
            "orphaned_nodes": [],
            "general": [],
        }

        # Strategies for contradictions
        if contradictions:
            strategies["contradictions"].extend([
                "Review conflicting requirements and resolve semantic contradictions",
                "Break circular dependencies by introducing intermediate abstractions",
                "Clarify the scope and context for conflicting assertions",
                "Consider if conflicts represent different operational modes",
            ])

        # Strategies for orphaned nodes
        if orphaned_nodes:
            orphan_types = {node.node_type for node in orphaned_nodes}

            if "requirement" in orphan_types:
                strategies["orphaned_nodes"].append(
                    "Connect orphaned requirements to relevant kgents principles"
                )

            if "design" in orphan_types:
                strategies["orphaned_nodes"].append(
                    "Link orphaned design elements to specific requirements"
                )

            if "implementation" in orphan_types:
                strategies["orphaned_nodes"].append(
                    "Establish clear derivation paths from design to orphaned implementations"
                )

            strategies["orphaned_nodes"].extend([
                "Review if orphaned elements are actually needed",
                "Consider consolidating orphaned elements with related components",
                "Add missing intermediate derivation steps",
            ])

        # General strategies
        strategies["general"].extend([
            "Ensure all elements trace back to kgents principles",
            "Maintain clear derivation chains from principles to implementation",
            "Regular review of specification consistency",
            "Use semantic analysis to detect hidden conflicts",
        ])

        return strategies

    async def _analyze_derivation_paths(
        self,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
    ) -> list[DerivationPath]:
        """Analyze derivation paths from principles to implementations."""

        paths = []

        # Find principle and implementation nodes
        principle_nodes = [n for n in nodes if n.node_type == "principle"]
        impl_nodes = [n for n in nodes if n.node_type == "implementation"]

        # For each principle-implementation pair, find paths
        for principle in principle_nodes:
            for impl in impl_nodes:
                path = await self._find_path(principle.node_id, impl.node_id, edges)
                if path:
                    derivation_path = DerivationPath(
                        principle_id=principle.node_id,
                        implementation_id=impl.node_id,
                        path_nodes=path,
                        path_edges=[e for e in edges if e.source_id in path and e.target_id in path],
                        is_complete=len(path) > 2,  # At least principle -> req -> impl
                    )
                    paths.append(derivation_path)

        return paths

    async def _find_path(
        self,
        start_id: str,
        end_id: str,
        edges: list[GraphEdge],
    ) -> list[str] | None:
        """Find path between two nodes using BFS."""

        # Build adjacency list
        graph = {}
        for edge in edges:
            if edge.source_id not in graph:
                graph[edge.source_id] = []
            graph[edge.source_id].append(edge.target_id)

        # BFS to find path
        queue = [(start_id, [start_id])]
        visited = {start_id}

        while queue:
            current, path = queue.pop(0)

            if current == end_id:
                return path

            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def _determine_status(
        self,
        contradictions: list[Contradiction],
        orphaned_nodes: list[GraphNode],
        derivation_paths: list[DerivationPath],
    ) -> VerificationStatus:
        """Determine overall verification status of the graph."""

        # Check for critical issues
        critical_contradictions = [c for c in contradictions if c.severity == "critical"]
        if critical_contradictions:
            return VerificationStatus.FAILURE

        # Check for incomplete derivations
        incomplete_paths = [p for p in derivation_paths if not p.is_complete]
        if len(incomplete_paths) > len(derivation_paths) * 0.5:  # More than 50% incomplete
            return VerificationStatus.NEEDS_REVIEW

        # Check for orphaned nodes
        if orphaned_nodes:
            return VerificationStatus.NEEDS_REVIEW

        # Check for any contradictions
        if contradictions:
            return VerificationStatus.NEEDS_REVIEW

        return VerificationStatus.SUCCESS

    async def _extract_principles(self, spec_data: dict[str, Any]) -> list[str]:
        """Extract principles referenced in the specification."""

        # TODO: Implement principle extraction from content
        return ["composable", "ethical", "joy_inducing"]

    async def _extract_concepts(self, spec_data: dict[str, Any]) -> list[str]:
        """Extract key concepts from the specification."""

        # TODO: Implement concept extraction from content
        return ["agent", "morphism", "category", "verification"]

    async def _extract_implementations(self, spec_data: dict[str, Any]) -> list[str]:
        """Extract implementation artifacts from the specification."""

        # TODO: Implement implementation extraction from content
        return ["service", "persistence", "node", "contracts"]
