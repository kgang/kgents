"""
Property-Based Tests for Generative Loop Engine.

Tests the closed generative cycle from intent to implementation and back,
verifying structure preservation through the roundtrip.

Feature: formal-verification-metatheory
Properties: 4, 5, 6
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

from services.verification.contracts import (
    BehavioralPattern,
    TraceWitnessResult,
    VerificationStatus,
)
from services.verification.generative_loop import (
    AGENTESEPath,
    AGENTESESpec,
    CompressionMorphism,
    GenerativeLoop,
    Implementation,
    ImplementationProjector,
    Module,
    OperadSpec,
    PatternSynthesizer,
    RoundtripResult,
    SpecChange,
    SpecDiff,
    SpecDiffEngine,
)
from services.verification.topology import (
    ContinuousMap,
    Cover,
    MappingType,
    MindMapTopology,
    TopologicalNode,
)

# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def node_id_strategy(draw: st.DrawFn) -> str:
    """Generate valid node IDs."""
    prefix = draw(st.sampled_from(["node", "concept", "agent", "service", "module"]))
    suffix = draw(st.integers(min_value=1, max_value=100))
    return f"{prefix}_{suffix}"


@st.composite
def topological_node_strategy(draw: st.DrawFn) -> TopologicalNode:
    """Generate random topological nodes."""
    node_id = draw(node_id_strategy())
    content = draw(
        st.text(
            min_size=1,
            max_size=100,
            alphabet=st.characters(
                whitelist_categories=("L", "N", "P", "S"), whitelist_characters=" "
            ),
        )
    )
    node_type = draw(st.sampled_from(["entity", "memory", "state", "principle", "theory"]))

    return TopologicalNode(
        id=node_id,
        content=content,
        node_type=node_type,
        neighborhood=frozenset(),
    )


@st.composite
def mind_map_topology_strategy(draw: st.DrawFn) -> MindMapTopology:
    """Generate random mind-map topologies."""
    # Generate nodes
    num_nodes = draw(st.integers(min_value=2, max_value=10))
    nodes_list = [draw(topological_node_strategy()) for _ in range(num_nodes)]

    # Ensure unique node IDs
    seen_ids = set()
    unique_nodes = []
    for node in nodes_list:
        if node.node_id not in seen_ids:
            seen_ids.add(node.node_id)
            unique_nodes.append(node)

    if len(unique_nodes) < 2:
        # Ensure at least 2 nodes
        unique_nodes.append(
            TopologicalNode(
                id="fallback_node_1",
                content="Fallback content",
                node_type="entity",
                neighborhood=frozenset(),
            )
        )
        unique_nodes.append(
            TopologicalNode(
                id="fallback_node_2",
                content="Another fallback",
                node_type="state",
                neighborhood=frozenset(),
            )
        )

    nodes = {node.id: node for node in unique_nodes}
    node_ids = list(nodes.keys())

    # Generate edges between nodes
    edges = {}
    num_edges = draw(st.integers(min_value=1, max_value=min(5, len(node_ids) - 1)))
    for i in range(num_edges):
        if len(node_ids) >= 2:
            source_idx = draw(st.integers(min_value=0, max_value=len(node_ids) - 2))
            target_idx = draw(st.integers(min_value=source_idx + 1, max_value=len(node_ids) - 1))
            source = node_ids[source_idx]
            target = node_ids[target_idx]
            edge_id = f"edge_{source}_{target}"
            mapping_type = draw(st.sampled_from(list(MappingType)))
            edges[edge_id] = ContinuousMap(
                source=source,
                target=target,
                mapping_type=mapping_type,
            )

    # Generate covers
    covers = {}
    if len(node_ids) >= 2:
        cover_members = frozenset(node_ids[:2])
        covers["cover_1"] = Cover(
            cover_id="cover_1",
            name="Test Cover",
            member_ids=cover_members,
        )

    return MindMapTopology(
        nodes=nodes,
        edges=edges,
        covers=covers,
    )


@st.composite
def agentese_spec_strategy(draw: st.DrawFn) -> AGENTESESpec:
    """Generate random AGENTESE specifications."""
    num_paths = draw(st.integers(min_value=1, max_value=5))
    paths = []
    for i in range(num_paths):
        context = draw(st.sampled_from(["world", "self", "concept", "void", "time"]))
        aspect = draw(st.sampled_from(["manifest", "witness", "refine", "sip", "tithe"]))
        paths.append(
            AGENTESEPath(
                path=f"{context}.test_{i}.{aspect}",
                context=context,
                aspect=aspect,
                description=f"Test path {i}",
                node_type="entity",
                original_id=f"node_{i}",
            )
        )

    operads = []
    if draw(st.booleans()):
        operads.append(
            OperadSpec(
                operad_id="operad_1",
                name="Test Operad",
                operations=frozenset(["op1", "op2"]),
                composition_type="sequential",
            )
        )

    return AGENTESESpec(
        spec_id=f"spec_{draw(st.integers(min_value=1, max_value=1000))}",
        name="Test Spec",
        version="1.0.0",
        paths=frozenset(paths),
        operads=frozenset(operads),
        constraints=frozenset(),
        source_topology_hash="abc123",
    )


@st.composite
def behavioral_pattern_strategy(draw: st.DrawFn) -> BehavioralPattern:
    """Generate random behavioral patterns."""
    pattern_type = draw(st.sampled_from(["execution_flow", "performance", "verification_outcome"]))
    return BehavioralPattern(
        pattern_id=f"pattern_{draw(st.integers(min_value=1, max_value=1000))}",
        pattern_type=pattern_type,
        description=f"Test pattern of type {pattern_type}",
        frequency=draw(st.integers(min_value=1, max_value=100)),
        example_traces=[f"trace_{i}" for i in range(draw(st.integers(min_value=1, max_value=3)))],
        metadata={"test": True},
    )


# =============================================================================
# Property 4: Generative Loop Round-Trip
# =============================================================================


class TestGenerativeLoopRoundTrip:
    """
    Property 4: Generative Loop Round-Trip

    For any well-formed mind-map, the roundtrip Mind-Map → Spec → Impl → Mind-Map'
    SHALL preserve essential structure (isomorphic up to refinement).

    Validates: Requirements 2.6, 12.6
    """

    @pytest.mark.asyncio
    @given(topology=mind_map_topology_strategy())
    @settings(max_examples=100, deadline=None)
    async def test_roundtrip_preserves_node_count(self, topology: MindMapTopology) -> None:
        """Roundtrip preserves approximate node count."""
        loop = GenerativeLoop()

        # Compress to spec
        spec = await loop.compress(topology)

        # Node count should be preserved within tolerance
        original_nodes = len(topology.nodes)
        spec_paths = len(spec.paths)

        # Allow some compression (paths may consolidate nodes)
        # But should not lose more than 50% of nodes
        assert spec_paths >= original_nodes * 0.5 or original_nodes <= 2

    @pytest.mark.asyncio
    @given(topology=mind_map_topology_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_roundtrip_preserves_structure(self, topology: MindMapTopology) -> None:
        """Full roundtrip preserves essential structure."""
        loop = GenerativeLoop()

        result = await loop.roundtrip(topology)

        # Result should be a valid RoundtripResult
        assert isinstance(result, RoundtripResult)
        assert result.original_topology == topology
        assert result.spec is not None
        assert result.implementation is not None

        # Drift score should be reasonable
        assert 0.0 <= result.diff.drift_score <= 1.0

    @pytest.mark.asyncio
    @given(topology=mind_map_topology_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_roundtrip_generates_traces(self, topology: MindMapTopology) -> None:
        """Roundtrip generates trace witnesses."""
        loop = GenerativeLoop()

        result = await loop.roundtrip(topology)

        # Should generate traces for each module
        assert len(result.traces) == len(result.implementation.modules)

    @pytest.mark.asyncio
    async def test_roundtrip_with_minimal_topology(self) -> None:
        """Roundtrip works with minimal topology."""
        topology = MindMapTopology(
            nodes={
                "node_1": TopologicalNode(
                    id="node_1",
                    content="Test node",
                    node_type="entity",
                    neighborhood=frozenset(),
                ),
            },
            edges={},
            covers={},
        )

        loop = GenerativeLoop()
        result = await loop.roundtrip(topology)

        assert result.structure_preserved or result.diff.drift_score < 0.5


# =============================================================================
# Property 5: Compression Morphism Preservation
# =============================================================================


class TestCompressionMorphismPreservation:
    """
    Property 5: Compression Morphism Preservation

    For any mind-map compression, the essential decisions SHALL be preserved
    in the resulting AGENTESE specification.

    Validates: Requirements 2.1
    """

    @pytest.mark.asyncio
    @given(topology=mind_map_topology_strategy())
    @settings(max_examples=100, deadline=None)
    async def test_compression_preserves_nodes(self, topology: MindMapTopology) -> None:
        """Compression preserves node information as paths."""
        compressor = CompressionMorphism()

        spec = await compressor.compress(topology)

        # Each node should have a corresponding path
        assert len(spec.paths) >= 1

        # Original node IDs should be traceable
        original_ids = {path.original_id for path in spec.paths}
        topology_ids = set(topology.nodes.keys())

        # At least some original IDs should be preserved
        assert len(original_ids & topology_ids) > 0 or len(topology.nodes) == 0

    @pytest.mark.asyncio
    @given(topology=mind_map_topology_strategy())
    @settings(max_examples=100, deadline=None)
    async def test_compression_preserves_covers_as_operads(self, topology: MindMapTopology) -> None:
        """Compression preserves covers as operads."""
        compressor = CompressionMorphism()

        spec = await compressor.compress(topology)

        # Covers should become operads
        if topology.covers:
            assert len(spec.operads) >= 1

    @pytest.mark.asyncio
    @given(topology=mind_map_topology_strategy())
    @settings(max_examples=100, deadline=None)
    async def test_compression_preserves_edges_as_constraints(
        self, topology: MindMapTopology
    ) -> None:
        """Compression preserves edges as constraints."""
        compressor = CompressionMorphism()

        spec = await compressor.compress(topology)

        # Edges should become constraints
        if topology.edges:
            assert len(spec.constraints) >= 1

    @pytest.mark.asyncio
    @given(topology=mind_map_topology_strategy())
    @settings(max_examples=100, deadline=None)
    async def test_compression_assigns_contexts(self, topology: MindMapTopology) -> None:
        """Compression assigns valid AGENTESE contexts."""
        compressor = CompressionMorphism()

        spec = await compressor.compress(topology)

        valid_contexts = {"world", "self", "concept", "void", "time"}
        for path in spec.paths:
            assert path.context in valid_contexts

    @pytest.mark.asyncio
    @given(topology=mind_map_topology_strategy())
    @settings(max_examples=100, deadline=None)
    async def test_compression_assigns_aspects(self, topology: MindMapTopology) -> None:
        """Compression assigns valid AGENTESE aspects."""
        compressor = CompressionMorphism()

        spec = await compressor.compress(topology)

        valid_aspects = {"manifest", "witness", "refine", "sip", "tithe"}
        for path in spec.paths:
            assert path.aspect in valid_aspects


# =============================================================================
# Property 6: Implementation Structure Preservation
# =============================================================================


class TestImplementationStructurePreservation:
    """
    Property 6: Implementation Structure Preservation

    For any specification projection, the generated implementation SHALL
    preserve the composition structure of the spec.

    Validates: Requirements 2.2
    """

    @pytest.mark.asyncio
    @given(spec=agentese_spec_strategy())
    @settings(max_examples=100, deadline=None)
    async def test_projection_creates_modules(self, spec: AGENTESESpec) -> None:
        """Projection creates modules for each path."""
        projector = ImplementationProjector()

        impl = await projector.project(spec)

        # Should create a module for each path
        assert len(impl.modules) == len(spec.paths)

    @pytest.mark.asyncio
    @given(spec=agentese_spec_strategy())
    @settings(max_examples=100, deadline=None)
    async def test_projection_preserves_spec_id(self, spec: AGENTESESpec) -> None:
        """Projection preserves spec ID reference."""
        projector = ImplementationProjector()

        impl = await projector.project(spec)

        assert impl.spec_id == spec.spec_id

        # Each module should reference the spec
        for module in impl.modules:
            assert module.generated_from == spec.spec_id

    @pytest.mark.asyncio
    @given(spec=agentese_spec_strategy())
    @settings(max_examples=100, deadline=None)
    async def test_projection_preserves_composition_structure(self, spec: AGENTESESpec) -> None:
        """Projection preserves composition structure."""
        projector = ImplementationProjector()

        impl = await projector.project(spec)

        # Composition structure should contain operads
        assert "operads" in impl.composition_structure
        assert "paths" in impl.composition_structure

        # Operads should be preserved
        assert len(impl.composition_structure["operads"]) == len(spec.operads)

        # Paths should be preserved
        assert len(impl.composition_structure["paths"]) == len(spec.paths)

    @pytest.mark.asyncio
    @given(spec=agentese_spec_strategy())
    @settings(max_examples=100, deadline=None)
    async def test_projection_generates_valid_code(self, spec: AGENTESESpec) -> None:
        """Projection generates valid Python code."""
        projector = ImplementationProjector()

        impl = await projector.project(spec)

        for module in impl.modules:
            # Module should have content
            assert module.content

            # Content should be valid Python (contains def or class)
            assert "def " in module.content or "async def " in module.content

            # Content should reference the path
            assert "@node" in module.content

    @pytest.mark.asyncio
    @given(spec=agentese_spec_strategy())
    @settings(max_examples=100, deadline=None)
    async def test_projection_creates_unique_modules(self, spec: AGENTESESpec) -> None:
        """Projection creates unique module IDs."""
        projector = ImplementationProjector()

        impl = await projector.project(spec)

        module_ids = [m.module_id for m in impl.modules]
        assert len(module_ids) == len(set(module_ids))


# =============================================================================
# Pattern Synthesis Tests
# =============================================================================


class TestPatternSynthesis:
    """Tests for pattern synthesis from traces."""

    @pytest.mark.asyncio
    async def test_synthesize_from_empty_traces(self) -> None:
        """Synthesis handles empty traces."""
        synthesizer = PatternSynthesizer()

        patterns = await synthesizer.synthesize([])

        assert patterns == []

    @pytest.mark.asyncio
    async def test_synthesize_extracts_flow_patterns(self) -> None:
        """Synthesis extracts execution flow patterns."""
        synthesizer = PatternSynthesizer()

        # Create traces with similar flows
        from services.verification.contracts import IntermediateStep

        traces = [
            TraceWitnessResult(
                witness_id=f"trace_{i}",
                agent_path="test.agent",
                input_data={},
                output_data={},
                intermediate_steps=[
                    IntermediateStep(operation="step1", data={}),
                    IntermediateStep(operation="step2", data={}),
                ],
                verification_status=VerificationStatus.SUCCESS,
                execution_time_ms=50.0,
            )
            for i in range(3)
        ]

        patterns = await synthesizer.synthesize(traces)

        # Should find flow pattern
        flow_patterns = [p for p in patterns if p.pattern_type == "execution_flow"]
        assert len(flow_patterns) >= 1

    @pytest.mark.asyncio
    async def test_synthesize_extracts_performance_patterns(self) -> None:
        """Synthesis extracts performance patterns."""
        synthesizer = PatternSynthesizer()

        traces = [
            TraceWitnessResult(
                witness_id=f"trace_{i}",
                agent_path="test.agent",
                input_data={},
                output_data={},
                intermediate_steps=[],
                verification_status=VerificationStatus.SUCCESS,
                execution_time_ms=50.0 if i < 2 else 150.0,
            )
            for i in range(4)
        ]

        patterns = await synthesizer.synthesize(traces)

        # Should find performance patterns
        perf_patterns = [p for p in patterns if p.pattern_type == "performance"]
        assert len(perf_patterns) >= 1


# =============================================================================
# Spec Diff Tests
# =============================================================================


class TestSpecDiff:
    """Tests for spec diff engine."""

    @pytest.mark.asyncio
    @given(topology=mind_map_topology_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_diff_with_no_patterns(self, topology: MindMapTopology) -> None:
        """Diff with no patterns shows no drift."""
        diff_engine = SpecDiffEngine()

        diff = await diff_engine.diff(topology, [])

        assert diff.drift_score == 0.0
        assert diff.structure_preserved

    @pytest.mark.asyncio
    @given(
        topology=mind_map_topology_strategy(),
        patterns=st.lists(behavioral_pattern_strategy(), min_size=1, max_size=5),
    )
    @settings(max_examples=50, deadline=None)
    async def test_diff_detects_drift(
        self,
        topology: MindMapTopology,
        patterns: list[BehavioralPattern],
    ) -> None:
        """Diff detects drift from patterns."""
        diff_engine = SpecDiffEngine()

        diff = await diff_engine.diff(topology, patterns)

        # Drift score should be valid
        assert 0.0 <= diff.drift_score <= 1.0

        # Structure preserved should be consistent with drift
        if diff.drift_score < 0.3:
            assert diff.structure_preserved

    @pytest.mark.asyncio
    async def test_diff_identifies_emergent_steps(self) -> None:
        """Diff identifies emergent execution steps."""
        topology = MindMapTopology(
            nodes={
                "node_1": TopologicalNode(
                    id="node_1",
                    content="Test",
                    node_type="entity",
                    neighborhood=frozenset(),
                )
            },
            edges={},
            covers={},
        )

        patterns = [
            BehavioralPattern(
                pattern_id="flow_1",
                pattern_type="execution_flow",
                description="Flow: emergent_step",
                frequency=5,
                example_traces=["t1"],
                metadata={"steps": ["emergent_step"]},
            ),
        ]

        diff_engine = SpecDiffEngine()
        diff = await diff_engine.diff(topology, patterns)

        # Should detect emergent step as addition
        assert len(diff.additions) >= 1


# =============================================================================
# Spec Refinement Tests
# =============================================================================


class TestSpecRefinement:
    """Tests for spec refinement."""

    @pytest.mark.asyncio
    @given(spec=agentese_spec_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_refine_increments_version(self, spec: AGENTESESpec) -> None:
        """Refinement increments version."""
        loop = GenerativeLoop()

        diff = SpecDiff(
            diff_id="test_diff",
            original_spec_id=spec.spec_id,
            refined_spec_id=None,
            additions=frozenset(),
            removals=frozenset(),
            modifications=frozenset(),
            structure_preserved=True,
            drift_score=0.1,
        )

        refined = await loop.refine_spec(spec, [], diff)

        # Version should be incremented
        original_parts = spec.version.split(".")
        refined_parts = refined.version.split(".")

        assert int(refined_parts[2]) > int(original_parts[2])

    @pytest.mark.asyncio
    async def test_refine_adds_emergent_paths(self) -> None:
        """Refinement adds paths for emergent behaviors."""
        spec = AGENTESESpec(
            spec_id="original_spec",
            name="Original",
            version="1.0.0",
            paths=frozenset(
                [
                    AGENTESEPath(
                        path="self.test.manifest",
                        context="self",
                        aspect="manifest",
                        description="Original path",
                        node_type="entity",
                        original_id="node_1",
                    ),
                ]
            ),
            operads=frozenset(),
            constraints=frozenset(),
            source_topology_hash="abc123",
        )

        diff = SpecDiff(
            diff_id="test_diff",
            original_spec_id=spec.spec_id,
            refined_spec_id=None,
            additions=frozenset(
                [
                    SpecChange(
                        change_id="change_1",
                        change_type="addition",
                        path="flow.emergent",
                        old_value=None,
                        new_value="emergent",
                        reason="Emergent behavior detected",
                    ),
                ]
            ),
            removals=frozenset(),
            modifications=frozenset(),
            structure_preserved=True,
            drift_score=0.1,
        )

        loop = GenerativeLoop()
        refined = await loop.refine_spec(spec, [], diff)

        # Should have more paths
        assert len(refined.paths) > len(spec.paths)
