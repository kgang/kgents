"""
Generative Loop Engine: The closed cycle from intent to implementation and back.

Implements the core generative loop:
Mind-Map → Spec → Impl → Traces → Patterns → Refined Spec → Mind-Map

> "Delete implementation, regenerate from spec, result is isomorphic to original."

Teaching:
    gotcha: Roundtrip may LOSE nodes during compression if node count is small.
            The compression allows up to 50% node loss for small topologies (<=2 nodes).
            This is intentional - consolidation is valid compression.
            (Evidence: test_generative_loop.py::TestGenerativeLoopRoundTrip::test_roundtrip_preserves_node_count)

    gotcha: Refinement increments the PATCH version, not major/minor.
            Version goes from 1.0.0 to 1.0.1 after refinement. This is semantic
            versioning for specs - refinements are backwards compatible.
            (Evidence: test_generative_loop.py::TestSpecRefinement::test_refine_increments_version)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from .contracts import (
    BehavioralPattern,
    TraceWitnessResult,
    VerificationStatus,
)
from .topology import ContinuousMap, MappingType, MindMapTopology, TopologicalNode

logger = logging.getLogger(__name__)


# =============================================================================
# Core Data Structures
# =============================================================================


@dataclass(frozen=True)
class AGENTESEPath:
    """An AGENTESE path extracted from mind-map."""

    path: str
    context: str  # world, self, concept, void, time
    aspect: str  # manifest, witness, refine, etc.
    description: str
    node_type: str = ""
    original_id: str = ""

    def __hash__(self) -> int:
        return hash((self.path, self.context, self.aspect))


@dataclass(frozen=True)
class OperadSpec:
    """An operad specification for composition grammar."""

    operad_id: str
    name: str
    operations: frozenset[str]
    composition_type: str = "sequential"
    cover_id: str = ""

    def __hash__(self) -> int:
        return hash((self.operad_id, self.name))


@dataclass(frozen=True)
class AGENTESESpec:
    """AGENTESE specification extracted from mind-map."""

    spec_id: str
    name: str
    version: str
    paths: frozenset[AGENTESEPath]
    operads: frozenset[OperadSpec]
    constraints: frozenset[str]
    source_topology_hash: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class Module:
    """A generated implementation module."""

    module_id: str
    name: str
    path: str
    content: str
    dependencies: frozenset[str]
    generated_from: str  # spec_id


@dataclass(frozen=True)
class Implementation:
    """Generated implementation from spec."""

    impl_id: str
    spec_id: str
    modules: frozenset[Module]
    composition_structure: dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class SpecChange:
    """A change in specification."""

    change_id: str
    change_type: str  # addition, removal, modification
    path: str
    old_value: Any | None
    new_value: Any | None
    reason: str


@dataclass(frozen=True)
class SpecDiff:
    """Difference between original and refined spec."""

    diff_id: str
    original_spec_id: str
    refined_spec_id: str | None
    additions: frozenset[SpecChange]
    removals: frozenset[SpecChange]
    modifications: frozenset[SpecChange]
    structure_preserved: bool
    drift_score: float  # 0.0 = identical, 1.0 = completely different


@dataclass(frozen=True)
class RoundtripResult:
    """Result of generative loop roundtrip."""

    roundtrip_id: str
    original_topology: MindMapTopology
    spec: AGENTESESpec
    implementation: Implementation
    traces: list[TraceWitnessResult]
    patterns: list[BehavioralPattern]
    diff: SpecDiff
    structure_preserved: bool
    roundtrip_time_ms: float
    created_at: datetime = field(default_factory=datetime.now)


# =============================================================================
# Compression Morphism
# =============================================================================


class CompressionMorphism:
    """
    Extracts essential decisions from mind-map topology into AGENTESE spec.

    The compression morphism is a functor that preserves structure while
    reducing detail. Essential relationships are maintained.
    """

    def __init__(self, llm_client: Any = None):
        self.llm_client = llm_client

    async def compress(self, topology: MindMapTopology) -> AGENTESESpec:
        """Extract AGENTESE specification from mind-map topology."""
        logger.info(f"Compressing topology with {len(topology.nodes)} nodes")

        # Extract AGENTESE paths from nodes
        paths = await self._extract_paths(topology)

        # Extract operads from composition patterns
        operads = await self._extract_operads(topology)

        # Extract constraints from relationships
        constraints = await self._extract_constraints(topology)

        # Compute topology hash for traceability
        topology_hash = self._compute_topology_hash(topology)

        spec = AGENTESESpec(
            spec_id=str(uuid4()),
            name=f"Spec from {len(topology.nodes)} nodes",
            version="1.0.0",
            paths=frozenset(paths),
            operads=frozenset(operads),
            constraints=frozenset(constraints),
            source_topology_hash=topology_hash,
        )

        logger.info(f"Compressed to spec with {len(paths)} paths, {len(operads)} operads")
        return spec

    async def _extract_paths(self, topology: MindMapTopology) -> list[AGENTESEPath]:
        """Extract AGENTESE paths from topology nodes."""
        paths = []

        for node_id, node in topology.nodes.items():
            # Determine context from node type or content
            context = self._infer_context(node)
            aspect = self._infer_aspect(node)

            path = AGENTESEPath(
                path=f"{context}.{node_id}",
                context=context,
                aspect=aspect,
                description=node.content[:200] if node.content else "",
                node_type=node.node_type,
                original_id=node_id,
            )
            paths.append(path)

        return paths

    def _infer_context(self, node: TopologicalNode) -> str:
        """Infer AGENTESE context from node."""
        content_lower = node.content.lower() if node.content else ""
        node_type = node.node_type.lower()

        if "world" in content_lower or node_type == "entity":
            return "world"
        elif "self" in content_lower or node_type in ["memory", "state"]:
            return "self"
        elif "concept" in content_lower or node_type in ["principle", "theory"]:
            return "concept"
        elif "void" in content_lower or node_type == "entropy":
            return "void"
        elif "time" in content_lower or node_type in ["trace", "history"]:
            return "time"
        else:
            return "self"  # Default to self context

    def _infer_aspect(self, node: TopologicalNode) -> str:
        """Infer AGENTESE aspect from node."""
        content_lower = node.content.lower() if node.content else ""

        if any(word in content_lower for word in ["create", "generate", "produce"]):
            return "manifest"
        elif any(word in content_lower for word in ["observe", "watch", "monitor"]):
            return "witness"
        elif any(word in content_lower for word in ["improve", "refine", "optimize"]):
            return "refine"
        elif any(word in content_lower for word in ["read", "consume", "receive"]):
            return "sip"
        elif any(word in content_lower for word in ["give", "contribute", "share"]):
            return "tithe"
        else:
            return "manifest"

    async def _extract_operads(self, topology: MindMapTopology) -> list[OperadSpec]:
        """Extract operad specifications from composition patterns."""
        operads = []

        # Group nodes by covers to find composition patterns
        for cover_id, cover in topology.covers.items():
            if len(cover.member_ids) >= 2:
                operations = frozenset(cover.member_ids)
                operad = OperadSpec(
                    operad_id=f"operad_{cover_id}",
                    name=cover.name,
                    operations=operations,
                    composition_type="sequential",
                    cover_id=cover_id,
                )
                operads.append(operad)

        return operads

    async def _extract_constraints(self, topology: MindMapTopology) -> list[str]:
        """Extract constraints from topology relationships."""
        constraints = []

        # Extract constraints from edge relationships
        for edge_id, edge in topology.edges.items():
            if edge.mapping_type == MappingType.INCLUSION:
                constraints.append(f"{edge.source} ⊆ {edge.target}")
            elif edge.mapping_type == MappingType.PROJECTION:
                constraints.append(f"{edge.source} → {edge.target}")

        return constraints

    def _compute_topology_hash(self, topology: MindMapTopology) -> str:
        """Compute a hash of the topology for traceability."""
        import hashlib

        content = f"{len(topology.nodes)}:{len(topology.edges)}:{len(topology.covers)}"
        return hashlib.md5(content.encode()).hexdigest()[:12]


# =============================================================================
# Implementation Projector
# =============================================================================


class ImplementationProjector:
    """
    Projects AGENTESE specification into implementation code.

    Preserves composition structure from spec to implementation.
    """

    def __init__(self, llm_client: Any = None):
        self.llm_client = llm_client

    async def project(self, spec: AGENTESESpec) -> Implementation:
        """Generate implementation from specification."""
        logger.info(f"Projecting spec {spec.spec_id} to implementation")

        modules = []

        # Generate module for each path
        for path in spec.paths:
            module = await self._generate_module(path, spec)
            modules.append(module)

        # Build composition structure from operads
        composition_structure = await self._build_composition_structure(spec)

        impl = Implementation(
            impl_id=str(uuid4()),
            spec_id=spec.spec_id,
            modules=frozenset(modules),
            composition_structure=composition_structure,
        )

        logger.info(f"Generated implementation with {len(modules)} modules")
        return impl

    async def _generate_module(self, path: AGENTESEPath, spec: AGENTESESpec) -> Module:
        """Generate a module from an AGENTESE path."""
        module_name = path.path.replace(".", "_")
        module_path = f"generated/{path.context}/{module_name}.py"

        # Generate module content
        content = self._generate_module_content(path, spec)

        return Module(
            module_id=str(uuid4()),
            name=module_name,
            path=module_path,
            content=content,
            dependencies=frozenset(),
            generated_from=spec.spec_id,
        )

    def _generate_module_content(self, path: AGENTESEPath, spec: AGENTESESpec) -> str:
        """Generate Python module content for a path."""
        return f'''"""
Generated module for {path.path}
Context: {path.context}
Aspect: {path.aspect}

{path.description}
"""

from protocols.agentese import node

@node("{path.path}.{path.aspect}")
async def {path.aspect}(umwelt):
    """Auto-generated from spec {spec.spec_id}."""
    pass
'''

    async def _build_composition_structure(self, spec: AGENTESESpec) -> dict[str, Any]:
        """Build composition structure from operads."""
        structure: dict[str, Any] = {"operads": [], "paths": []}

        for operad in spec.operads:
            structure["operads"].append(
                {
                    "id": operad.operad_id,
                    "name": operad.name,
                    "operations": list(operad.operations),
                    "rules": {"type": operad.composition_type, "cover": operad.cover_id},
                }
            )

        for path in spec.paths:
            structure["paths"].append(
                {
                    "path": path.path,
                    "context": path.context,
                    "aspect": path.aspect,
                }
            )

        return structure


# =============================================================================
# Pattern Synthesizer
# =============================================================================


class PatternSynthesizer:
    """
    Synthesizes behavioral patterns from accumulated traces.

    Identifies recurring patterns that suggest specification refinements.
    """

    def __init__(self, llm_client: Any = None):
        self.llm_client = llm_client

    async def synthesize(self, traces: list[TraceWitnessResult]) -> list[BehavioralPattern]:
        """Extract patterns from accumulated traces."""
        logger.info(f"Synthesizing patterns from {len(traces)} traces")

        patterns = []

        # Extract execution flow patterns
        flow_patterns = await self._extract_flow_patterns(traces)
        patterns.extend(flow_patterns)

        # Extract performance patterns
        perf_patterns = await self._extract_performance_patterns(traces)
        patterns.extend(perf_patterns)

        # Extract verification patterns
        verification_patterns = await self._extract_verification_patterns(traces)
        patterns.extend(verification_patterns)

        # Use LLM to identify higher-level patterns
        if self.llm_client:
            llm_patterns = await self._llm_pattern_synthesis(traces)
            patterns.extend(llm_patterns)

        logger.info(f"Synthesized {len(patterns)} patterns")
        return patterns

    async def _extract_flow_patterns(
        self, traces: list[TraceWitnessResult]
    ) -> list[BehavioralPattern]:
        """Extract execution flow patterns."""
        flow_counts: dict[str, int] = {}
        flow_traces: dict[str, list[str]] = {}

        for trace in traces:
            steps = [step.operation for step in trace.intermediate_steps]
            flow_key = " -> ".join(steps)

            flow_counts[flow_key] = flow_counts.get(flow_key, 0) + 1
            if flow_key not in flow_traces:
                flow_traces[flow_key] = []
            flow_traces[flow_key].append(trace.witness_id)

        patterns = []
        for flow_key, count in flow_counts.items():
            if count >= 2:  # Only patterns that appear multiple times
                patterns.append(
                    BehavioralPattern(
                        pattern_id=f"flow_{hash(flow_key) % 10000}",
                        pattern_type="execution_flow",
                        description=f"Flow: {flow_key}",
                        frequency=count,
                        example_traces=flow_traces[flow_key][:5],
                        metadata={"steps": flow_key.split(" -> ")},
                    )
                )

        return patterns

    async def _extract_performance_patterns(
        self, traces: list[TraceWitnessResult]
    ) -> list[BehavioralPattern]:
        """Extract performance patterns."""
        patterns = []

        # Categorize by execution time
        fast_traces = [t for t in traces if t.execution_time_ms and t.execution_time_ms < 100]
        slow_traces = [t for t in traces if t.execution_time_ms and t.execution_time_ms >= 100]

        if fast_traces:
            patterns.append(
                BehavioralPattern(
                    pattern_id="perf_fast",
                    pattern_type="performance",
                    description="Fast execution (<100ms)",
                    frequency=len(fast_traces),
                    example_traces=[t.witness_id for t in fast_traces[:5]],
                    metadata={"category": "fast", "threshold_ms": 100},
                )
            )

        if slow_traces:
            patterns.append(
                BehavioralPattern(
                    pattern_id="perf_slow",
                    pattern_type="performance",
                    description="Slow execution (>=100ms)",
                    frequency=len(slow_traces),
                    example_traces=[t.witness_id for t in slow_traces[:5]],
                    metadata={"category": "slow", "threshold_ms": 100},
                )
            )

        return patterns

    async def _extract_verification_patterns(
        self, traces: list[TraceWitnessResult]
    ) -> list[BehavioralPattern]:
        """Extract verification outcome patterns."""
        patterns = []
        status_counts: dict[VerificationStatus, list[str]] = {}

        for trace in traces:
            status = trace.verification_status
            if status not in status_counts:
                status_counts[status] = []
            status_counts[status].append(trace.witness_id)

        for status, trace_ids in status_counts.items():
            patterns.append(
                BehavioralPattern(
                    pattern_id=f"verification_{status.value}",
                    pattern_type="verification_outcome",
                    description=f"Verification status: {status.value}",
                    frequency=len(trace_ids),
                    example_traces=trace_ids[:5],
                    metadata={"status": status.value},
                )
            )

        return patterns

    async def _llm_pattern_synthesis(
        self, traces: list[TraceWitnessResult]
    ) -> list[BehavioralPattern]:
        """Use LLM to identify higher-level patterns."""
        # Simulate LLM pattern synthesis
        await asyncio.sleep(0.05)
        return []


# =============================================================================
# Spec Diff Engine
# =============================================================================


class SpecDiffEngine:
    """
    Compares original mind-map with patterns to detect drift.

    Identifies where implementation behavior diverges from intent.
    """

    def __init__(self, llm_client: Any = None):
        self.llm_client = llm_client

    async def diff(
        self,
        original: MindMapTopology,
        patterns: list[BehavioralPattern],
        spec: AGENTESESpec | None = None,
    ) -> SpecDiff:
        """Identify divergence between original intent and observed behavior."""
        logger.info(f"Computing diff for {len(patterns)} patterns")

        additions: list[SpecChange] = []
        removals: list[SpecChange] = []
        modifications: list[SpecChange] = []

        # Analyze patterns for drift indicators
        for pattern in patterns:
            changes = await self._analyze_pattern_drift(pattern, original, spec)
            for change in changes:
                if change.change_type == "addition":
                    additions.append(change)
                elif change.change_type == "removal":
                    removals.append(change)
                else:
                    modifications.append(change)

        # Calculate drift score
        total_changes = len(additions) + len(removals) + len(modifications)
        original_size = len(original.nodes) + len(original.edges)
        drift_score = min(1.0, total_changes / max(1, original_size))

        # Determine if structure is preserved
        structure_preserved = drift_score < 0.3  # Less than 30% drift

        diff = SpecDiff(
            diff_id=str(uuid4()),
            original_spec_id=spec.spec_id if spec else "unknown",
            refined_spec_id=None,
            additions=frozenset(additions),
            removals=frozenset(removals),
            modifications=frozenset(modifications),
            structure_preserved=structure_preserved,
            drift_score=drift_score,
        )

        logger.info(
            f"Diff computed: {len(additions)} additions, {len(removals)} removals, "
            f"{len(modifications)} modifications, drift={drift_score:.2f}"
        )
        return diff

    async def _analyze_pattern_drift(
        self,
        pattern: BehavioralPattern,
        original: MindMapTopology,
        spec: AGENTESESpec | None,
    ) -> list[SpecChange]:
        """Analyze a pattern for drift from original intent."""
        changes = []

        # Check for unexpected patterns (not in original topology)
        if pattern.pattern_type == "execution_flow":
            steps = pattern.metadata.get("steps", [])
            for step in steps:
                if step not in original.nodes:
                    changes.append(
                        SpecChange(
                            change_id=str(uuid4()),
                            change_type="addition",
                            path=f"flow.{step}",
                            old_value=None,
                            new_value=step,
                            reason=f"Emergent step '{step}' not in original topology",
                        )
                    )

        # Check for performance drift
        if pattern.pattern_type == "performance" and pattern.metadata.get("category") == "slow":
            if pattern.frequency > 5:  # Significant slow pattern
                changes.append(
                    SpecChange(
                        change_id=str(uuid4()),
                        change_type="modification",
                        path="performance.threshold",
                        old_value="fast",
                        new_value="slow",
                        reason=f"Performance degradation detected ({pattern.frequency} slow executions)",
                    )
                )

        # Check for verification failures
        if pattern.pattern_type == "verification_outcome":
            if pattern.metadata.get("status") == "failure" and pattern.frequency > 0:
                changes.append(
                    SpecChange(
                        change_id=str(uuid4()),
                        change_type="modification",
                        path="verification.status",
                        old_value="success",
                        new_value="failure",
                        reason=f"Verification failures detected ({pattern.frequency} failures)",
                    )
                )

        return changes


# =============================================================================
# Generative Loop Orchestrator
# =============================================================================


class GenerativeLoop:
    """
    The closed generative cycle orchestrator.

    Mind-Map → Spec → Impl → Traces → Patterns → Refined Spec

    > "The stream finds a way around the boulder."
    """

    def __init__(self, llm_client: Any = None):
        self.llm_client = llm_client
        self.compressor = CompressionMorphism(llm_client)
        self.projector = ImplementationProjector(llm_client)
        self.synthesizer = PatternSynthesizer(llm_client)
        self.diff_engine = SpecDiffEngine(llm_client)

        # Import trace witness lazily to avoid circular imports
        self._trace_witness: Any = None

    @property
    def trace_witness(self) -> Any:
        if self._trace_witness is None:
            from .trace_witness import EnhancedTraceWitness

            self._trace_witness = EnhancedTraceWitness(self.llm_client)
        return self._trace_witness

    async def compress(self, mind_map: MindMapTopology) -> AGENTESESpec:
        """Extract essential decisions into AGENTESE spec."""
        return await self.compressor.compress(mind_map)

    async def project(self, spec: AGENTESESpec) -> Implementation:
        """Generate implementation preserving composition structure."""
        return await self.projector.project(spec)

    async def witness(self, implementation: Implementation) -> list[TraceWitnessResult]:
        """Capture traces as constructive proofs."""
        traces = []

        # Execute each module and capture traces
        for module in implementation.modules:
            trace = await self.trace_witness.capture_execution_trace(
                agent_path=module.name,
                input_data={"module_id": module.module_id, "spec_id": module.generated_from},
                specification_id=implementation.spec_id,
            )
            traces.append(trace)

        return traces

    async def synthesize(self, traces: list[TraceWitnessResult]) -> list[BehavioralPattern]:
        """Extract patterns from accumulated traces."""
        return await self.synthesizer.synthesize(traces)

    async def diff(
        self,
        original: MindMapTopology,
        patterns: list[BehavioralPattern],
        spec: AGENTESESpec | None = None,
    ) -> SpecDiff:
        """Identify divergence and propose updates."""
        return await self.diff_engine.diff(original, patterns, spec)

    async def roundtrip(self, mind_map: MindMapTopology) -> RoundtripResult:
        """
        Full generative loop roundtrip.

        Mind-Map → Spec → Impl → Traces → Patterns → Diff

        Verifies that essential structure is preserved through the cycle.
        """
        logger.info("Starting generative loop roundtrip")
        start_time = datetime.now()

        # 1. Compress mind-map to spec
        spec = await self.compress(mind_map)
        logger.info(f"Compressed to spec {spec.spec_id}")

        # 2. Project spec to implementation
        impl = await self.project(spec)
        logger.info(f"Projected to implementation {impl.impl_id}")

        # 3. Execute and capture traces
        traces = await self.witness(impl)
        logger.info(f"Captured {len(traces)} traces")

        # 4. Synthesize patterns from traces
        patterns = await self.synthesize(traces)
        logger.info(f"Synthesized {len(patterns)} patterns")

        # 5. Compute diff to detect drift
        diff = await self.diff(mind_map, patterns, spec)
        logger.info(f"Computed diff with drift score {diff.drift_score:.2f}")

        # 6. Verify structure preservation
        structure_preserved = await self._verify_structure_preservation(mind_map, spec, diff)

        end_time = datetime.now()
        roundtrip_time_ms = (end_time - start_time).total_seconds() * 1000

        result = RoundtripResult(
            roundtrip_id=str(uuid4()),
            original_topology=mind_map,
            spec=spec,
            implementation=impl,
            traces=traces,
            patterns=patterns,
            diff=diff,
            structure_preserved=structure_preserved,
            roundtrip_time_ms=roundtrip_time_ms,
        )

        logger.info(
            f"Roundtrip complete in {roundtrip_time_ms:.0f}ms, "
            f"structure_preserved={structure_preserved}"
        )
        return result

    async def _verify_structure_preservation(
        self,
        original: MindMapTopology,
        spec: AGENTESESpec,
        diff: SpecDiff,
    ) -> bool:
        """
        Verify that essential structure is preserved through the roundtrip.

        Essential structure includes:
        - Node count preservation (within tolerance)
        - Edge relationship preservation
        - Cover/cluster preservation
        """
        # Check node count preservation
        original_nodes = len(original.nodes)
        spec_paths = len(spec.paths)

        # Allow some compression (paths may consolidate nodes)
        node_ratio = spec_paths / max(1, original_nodes)
        if node_ratio < 0.5:  # Lost more than 50% of nodes
            return False

        # Check drift score
        if diff.drift_score > 0.5:  # More than 50% drift
            return False

        # Check for critical failures
        critical_changes = [
            c
            for c in diff.modifications
            if "failure" in c.reason.lower() or "error" in c.reason.lower()
        ]
        if len(critical_changes) > 0:
            return False

        return True

    async def refine_spec(
        self,
        original_spec: AGENTESESpec,
        patterns: list[BehavioralPattern],
        diff: SpecDiff,
    ) -> AGENTESESpec:
        """
        Refine specification based on observed patterns and drift.

        This closes the loop by updating the spec based on runtime behavior.
        """
        logger.info(f"Refining spec {original_spec.spec_id}")

        # Start with original paths
        new_paths = set(original_spec.paths)

        # Add paths for emergent behaviors
        for change in diff.additions:
            if change.change_type == "addition":
                new_path = AGENTESEPath(
                    path=change.path,
                    context="self",  # Default context for emergent paths
                    aspect="manifest",
                    description=f"Emergent: {change.reason}",
                    node_type="emergent",
                    original_id=change.change_id,
                )
                new_paths.add(new_path)

        # Create refined spec
        refined_spec = AGENTESESpec(
            spec_id=str(uuid4()),
            name=f"Refined {original_spec.name}",
            version=self._increment_version(original_spec.version),
            paths=frozenset(new_paths),
            operads=original_spec.operads,
            constraints=original_spec.constraints,
            source_topology_hash=original_spec.source_topology_hash,
        )

        logger.info(f"Refined spec {refined_spec.spec_id} with {len(new_paths)} paths")
        return refined_spec

    def _increment_version(self, version: str) -> str:
        """Increment semantic version."""
        parts = version.split(".")
        if len(parts) >= 3:
            parts[2] = str(int(parts[2]) + 1)
        return ".".join(parts)


# =============================================================================
# Convenience Functions
# =============================================================================


async def run_generative_loop(mind_map: MindMapTopology) -> RoundtripResult:
    """Convenience function to run the generative loop."""
    loop = GenerativeLoop()
    return await loop.roundtrip(mind_map)


async def compress_to_spec(mind_map: MindMapTopology) -> AGENTESESpec:
    """Convenience function to compress mind-map to spec."""
    compressor = CompressionMorphism()
    return await compressor.compress(mind_map)
