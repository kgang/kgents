"""
Reflective Tower: Level hierarchy with consistency verification.

Implements the reflective tower from the Formal Verification Metatheory:

Level -2: Behavioral Patterns (emergent from traces)
Level -1: Trace Witnesses (constructive proofs)
Level 0:  Python/TypeScript Code (implementation)
Level 1:  AGENTESE + Operads (specification)
Level 2:  Category Theory (meta-specification)
Level 3:  HoTT/Topos Theory (foundations)
Level ∞:  Mind-Map Topology (Kent's Intent)

> "The most profound change is the rate at which we can verify and improve our own understanding."
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Tower Levels
# =============================================================================


class TowerLevel(IntEnum):
    """Levels in the reflective tower."""

    BEHAVIORAL_PATTERNS = -2  # Emergent patterns from traces
    TRACE_WITNESSES = -1  # Constructive proofs of execution
    CODE = 0  # Python/TypeScript implementation
    SPEC = 1  # AGENTESE + Operads specification
    META_SPEC = 2  # Category Theory meta-specification
    FOUNDATIONS = 3  # HoTT/Topos Theory
    INTENT = 100  # Mind-Map Topology (Kent's Intent) - "Level ∞"


LEVEL_NAMES = {
    TowerLevel.BEHAVIORAL_PATTERNS: "Behavioral Patterns",
    TowerLevel.TRACE_WITNESSES: "Trace Witnesses",
    TowerLevel.CODE: "Implementation (Code)",
    TowerLevel.SPEC: "Specification (AGENTESE)",
    TowerLevel.META_SPEC: "Meta-Specification (Category Theory)",
    TowerLevel.FOUNDATIONS: "Foundations (HoTT)",
    TowerLevel.INTENT: "Intent (Mind-Map)",
}


# =============================================================================
# Level Artifacts
# =============================================================================


@dataclass(frozen=True)
class LevelArtifact:
    """An artifact at a specific tower level."""

    artifact_id: str
    level: TowerLevel
    name: str
    content: Any
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __hash__(self) -> int:
        return hash((self.artifact_id, self.level))


@dataclass(frozen=True)
class CompressionMorphism:
    """A morphism that compresses from higher to lower level."""

    morphism_id: str
    source_level: TowerLevel
    target_level: TowerLevel
    name: str
    description: str
    preserves: frozenset[str]  # What properties are preserved
    loses: frozenset[str]  # What information is lost


@dataclass(frozen=True)
class ConsistencyResult:
    """Result of consistency verification between levels."""

    result_id: str
    source_level: TowerLevel
    target_level: TowerLevel
    is_consistent: bool
    violations: list[dict[str, Any]]
    suggestions: list[str]
    verification_time_ms: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class CorrectionProposal:
    """A proposal to correct inconsistency between levels."""

    proposal_id: str
    source_level: TowerLevel
    target_level: TowerLevel
    description: str
    correction_type: str  # "lift", "lower", "reconcile"
    affected_artifacts: list[str]
    estimated_impact: dict[str, Any]


# =============================================================================
# Level Handlers
# =============================================================================


class LevelHandler:
    """Base class for handling artifacts at a specific level."""

    def __init__(self, level: TowerLevel):
        self.level = level
        self.artifacts: dict[str, LevelArtifact] = {}

    async def add_artifact(self, artifact: LevelArtifact) -> None:
        """Add an artifact to this level."""
        if artifact.level != self.level:
            raise ValueError(
                f"Artifact level {artifact.level} doesn't match handler level {self.level}"
            )
        self.artifacts[artifact.artifact_id] = artifact

    async def get_artifact(self, artifact_id: str) -> LevelArtifact | None:
        """Get an artifact by ID."""
        return self.artifacts.get(artifact_id)

    async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]:
        """Extract structural information from an artifact."""
        return {
            "id": artifact.artifact_id,
            "level": artifact.level.name,
            "name": artifact.name,
            "content_type": type(artifact.content).__name__,
        }


class BehavioralPatternHandler(LevelHandler):
    """Handler for Level -2: Behavioral Patterns."""

    def __init__(self) -> None:
        super().__init__(TowerLevel.BEHAVIORAL_PATTERNS)

    async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]:
        """Extract pattern structure."""
        base = await super().extract_structure(artifact)
        content = artifact.content
        if isinstance(content, dict):
            base["pattern_type"] = content.get("pattern_type", "unknown")
            base["frequency"] = content.get("frequency", 0)
        return base


class TraceWitnessHandler(LevelHandler):
    """Handler for Level -1: Trace Witnesses."""

    def __init__(self) -> None:
        super().__init__(TowerLevel.TRACE_WITNESSES)

    async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]:
        """Extract trace structure."""
        base = await super().extract_structure(artifact)
        content = artifact.content
        if isinstance(content, dict):
            base["agent_path"] = content.get("agent_path", "")
            base["verification_status"] = content.get("verification_status", "unknown")
        return base


class CodeHandler(LevelHandler):
    """Handler for Level 0: Implementation Code."""

    def __init__(self) -> None:
        super().__init__(TowerLevel.CODE)

    async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]:
        """Extract code structure."""
        base = await super().extract_structure(artifact)
        content = artifact.content
        if isinstance(content, dict):
            base["module_path"] = content.get("module_path", "")
            base["functions"] = content.get("functions", [])
            base["classes"] = content.get("classes", [])
        return base


class SpecHandler(LevelHandler):
    """Handler for Level 1: AGENTESE Specification."""

    def __init__(self) -> None:
        super().__init__(TowerLevel.SPEC)

    async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]:
        """Extract spec structure."""
        base = await super().extract_structure(artifact)
        content = artifact.content
        if isinstance(content, dict):
            base["agentese_paths"] = content.get("paths", [])
            base["operads"] = content.get("operads", [])
            base["constraints"] = content.get("constraints", [])
        return base


class MetaSpecHandler(LevelHandler):
    """Handler for Level 2: Category Theory Meta-Specification."""

    def __init__(self) -> None:
        super().__init__(TowerLevel.META_SPEC)

    async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]:
        """Extract meta-spec structure."""
        base = await super().extract_structure(artifact)
        content = artifact.content
        if isinstance(content, dict):
            base["categories"] = content.get("categories", [])
            base["functors"] = content.get("functors", [])
            base["natural_transformations"] = content.get("natural_transformations", [])
        return base


class FoundationsHandler(LevelHandler):
    """Handler for Level 3: HoTT Foundations."""

    def __init__(self) -> None:
        super().__init__(TowerLevel.FOUNDATIONS)

    async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]:
        """Extract foundations structure."""
        base = await super().extract_structure(artifact)
        content = artifact.content
        if isinstance(content, dict):
            base["types"] = content.get("types", [])
            base["paths"] = content.get("paths", [])
            base["universe_level"] = content.get("universe_level", 0)
        return base


class IntentHandler(LevelHandler):
    """Handler for Level ∞: Mind-Map Intent."""

    def __init__(self) -> None:
        super().__init__(TowerLevel.INTENT)

    async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]:
        """Extract intent structure."""
        base = await super().extract_structure(artifact)
        content = artifact.content
        if isinstance(content, dict):
            base["nodes"] = content.get("nodes", [])
            base["edges"] = content.get("edges", [])
            base["covers"] = content.get("covers", [])
        return base


# =============================================================================
# Consistency Verifier
# =============================================================================


class ConsistencyVerifier:
    """Verifies consistency between adjacent tower levels."""

    def __init__(self, llm_client: Any = None):
        self.llm_client = llm_client

    async def verify_consistency(
        self,
        source_artifact: LevelArtifact,
        target_artifact: LevelArtifact,
    ) -> ConsistencyResult:
        """Verify consistency between artifacts at adjacent levels."""
        start_time = datetime.now()

        # Determine verification strategy based on levels
        source_level = source_artifact.level
        target_level = target_artifact.level

        violations: list[dict[str, Any]] = []
        suggestions: list[str] = []

        # Check level adjacency
        if abs(int(source_level) - int(target_level)) > 1:
            if not (source_level == TowerLevel.FOUNDATIONS and target_level == TowerLevel.INTENT):
                violations.append(
                    {
                        "type": "non_adjacent_levels",
                        "description": f"Levels {source_level.name} and {target_level.name} are not adjacent",
                    }
                )

        # Perform level-specific consistency checks
        level_violations = await self._check_level_consistency(source_artifact, target_artifact)
        violations.extend(level_violations)

        # Generate suggestions for violations
        if violations:
            suggestions = await self._generate_suggestions(
                violations, source_artifact, target_artifact
            )

        end_time = datetime.now()
        verification_time_ms = (end_time - start_time).total_seconds() * 1000

        return ConsistencyResult(
            result_id=str(uuid4()),
            source_level=source_level,
            target_level=target_level,
            is_consistent=len(violations) == 0,
            violations=violations,
            suggestions=suggestions,
            verification_time_ms=verification_time_ms,
        )

    async def _check_level_consistency(
        self,
        source: LevelArtifact,
        target: LevelArtifact,
    ) -> list[dict[str, Any]]:
        """Check consistency based on specific level pair."""
        violations = []

        # Patterns → Traces: patterns should be derivable from traces
        if (
            source.level == TowerLevel.BEHAVIORAL_PATTERNS
            and target.level == TowerLevel.TRACE_WITNESSES
        ):
            violations.extend(await self._check_pattern_trace_consistency(source, target))

        # Traces → Code: traces should match code behavior
        elif source.level == TowerLevel.TRACE_WITNESSES and target.level == TowerLevel.CODE:
            violations.extend(await self._check_trace_code_consistency(source, target))

        # Code → Spec: code should implement spec
        elif source.level == TowerLevel.CODE and target.level == TowerLevel.SPEC:
            violations.extend(await self._check_code_spec_consistency(source, target))

        # Spec → Meta-Spec: spec should satisfy categorical laws
        elif source.level == TowerLevel.SPEC and target.level == TowerLevel.META_SPEC:
            violations.extend(await self._check_spec_metaspec_consistency(source, target))

        # Meta-Spec → Foundations: categorical structure should be HoTT-valid
        elif source.level == TowerLevel.META_SPEC and target.level == TowerLevel.FOUNDATIONS:
            violations.extend(await self._check_metaspec_foundations_consistency(source, target))

        # Foundations → Intent: foundations should capture intent
        elif source.level == TowerLevel.FOUNDATIONS and target.level == TowerLevel.INTENT:
            violations.extend(await self._check_foundations_intent_consistency(source, target))

        return violations

    async def _check_pattern_trace_consistency(
        self,
        pattern: LevelArtifact,
        trace: LevelArtifact,
    ) -> list[dict[str, Any]]:
        """Check that patterns are derivable from traces."""
        violations = []
        pattern_content = pattern.content if isinstance(pattern.content, dict) else {}
        trace_content = trace.content if isinstance(trace.content, dict) else {}

        # Check that pattern references valid traces
        example_traces = pattern_content.get("example_traces", [])
        trace_id = trace_content.get("witness_id", "")

        if example_traces and trace_id not in example_traces:
            violations.append(
                {
                    "type": "pattern_trace_mismatch",
                    "description": f"Pattern does not reference trace {trace_id}",
                    "severity": "warning",
                }
            )

        return violations

    async def _check_trace_code_consistency(
        self,
        trace: LevelArtifact,
        code: LevelArtifact,
    ) -> list[dict[str, Any]]:
        """Check that traces match code behavior."""
        violations = []
        trace_content = trace.content if isinstance(trace.content, dict) else {}
        code_content = code.content if isinstance(code.content, dict) else {}

        # Check that trace agent_path corresponds to code module
        agent_path = trace_content.get("agent_path", "")
        module_path = code_content.get("module_path", "")

        if agent_path and module_path:
            # Simple check: agent path should relate to module
            path_parts = agent_path.split(".")
            if not any(part in module_path for part in path_parts):
                violations.append(
                    {
                        "type": "trace_code_path_mismatch",
                        "description": f"Trace path '{agent_path}' doesn't match code module '{module_path}'",
                        "severity": "info",
                    }
                )

        return violations

    async def _check_code_spec_consistency(
        self,
        code: LevelArtifact,
        spec: LevelArtifact,
    ) -> list[dict[str, Any]]:
        """Check that code implements spec."""
        violations = []
        code_content = code.content if isinstance(code.content, dict) else {}
        spec_content = spec.content if isinstance(spec.content, dict) else {}

        # Check that spec paths have corresponding code
        spec_paths = spec_content.get("paths", [])
        code_functions = code_content.get("functions", [])

        for path in spec_paths:
            path_name = path if isinstance(path, str) else path.get("path", "")
            # Check if any function implements this path
            if not any(path_name.split(".")[-1] in func for func in code_functions):
                violations.append(
                    {
                        "type": "unimplemented_spec_path",
                        "description": f"Spec path '{path_name}' has no corresponding implementation",
                        "severity": "error",
                    }
                )

        return violations

    async def _check_spec_metaspec_consistency(
        self,
        spec: LevelArtifact,
        metaspec: LevelArtifact,
    ) -> list[dict[str, Any]]:
        """Check that spec satisfies categorical laws."""
        violations = []
        spec_content = spec.content if isinstance(spec.content, dict) else {}
        metaspec_content = metaspec.content if isinstance(metaspec.content, dict) else {}

        # Check that operads satisfy coherence
        operads = spec_content.get("operads", [])
        categories = metaspec_content.get("categories", [])

        if operads and not categories:
            violations.append(
                {
                    "type": "missing_categorical_foundation",
                    "description": "Spec has operads but meta-spec has no categories",
                    "severity": "warning",
                }
            )

        return violations

    async def _check_metaspec_foundations_consistency(
        self,
        metaspec: LevelArtifact,
        foundations: LevelArtifact,
    ) -> list[dict[str, Any]]:
        """Check that categorical structure is HoTT-valid."""
        violations = []
        metaspec_content = metaspec.content if isinstance(metaspec.content, dict) else {}
        foundations_content = foundations.content if isinstance(foundations.content, dict) else {}

        # Check universe levels
        functors = metaspec_content.get("functors", [])
        universe_level = foundations_content.get("universe_level", 0)

        if functors and universe_level < 1:
            violations.append(
                {
                    "type": "universe_level_insufficient",
                    "description": "Functors require universe level >= 1",
                    "severity": "warning",
                }
            )

        return violations

    async def _check_foundations_intent_consistency(
        self,
        foundations: LevelArtifact,
        intent: LevelArtifact,
    ) -> list[dict[str, Any]]:
        """Check that foundations capture intent."""
        violations = []
        foundations_content = foundations.content if isinstance(foundations.content, dict) else {}
        intent_content = intent.content if isinstance(intent.content, dict) else {}

        # Check that intent nodes have corresponding types
        intent_nodes = intent_content.get("nodes", [])
        foundation_types = foundations_content.get("types", [])

        if intent_nodes and not foundation_types:
            violations.append(
                {
                    "type": "intent_not_formalized",
                    "description": "Intent has nodes but foundations has no types",
                    "severity": "info",
                }
            )

        return violations

    async def _generate_suggestions(
        self,
        violations: list[dict[str, Any]],
        source: LevelArtifact,
        target: LevelArtifact,
    ) -> list[str]:
        """Generate suggestions for fixing violations."""
        suggestions = []

        for violation in violations:
            violation_type = violation.get("type", "")

            if violation_type == "unimplemented_spec_path":
                suggestions.append("Implement the missing spec path in code")
            elif violation_type == "missing_categorical_foundation":
                suggestions.append("Add categorical structure to meta-spec")
            elif violation_type == "universe_level_insufficient":
                suggestions.append("Increase universe level in foundations")
            elif violation_type == "intent_not_formalized":
                suggestions.append("Formalize intent nodes as HoTT types")
            else:
                suggestions.append(f"Review {violation_type} and reconcile levels")

        return suggestions


# =============================================================================
# Reflective Tower
# =============================================================================


class ReflectiveTower:
    """
    The reflective tower with level hierarchy and consistency verification.

    Implements the vision of a self-improving system where each level
    reflects on and verifies the levels below it.
    """

    def __init__(self, llm_client: Any = None):
        self.llm_client = llm_client
        self.verifier = ConsistencyVerifier(llm_client)

        # Initialize level handlers
        self.handlers: dict[TowerLevel, LevelHandler] = {
            TowerLevel.BEHAVIORAL_PATTERNS: BehavioralPatternHandler(),
            TowerLevel.TRACE_WITNESSES: TraceWitnessHandler(),
            TowerLevel.CODE: CodeHandler(),
            TowerLevel.SPEC: SpecHandler(),
            TowerLevel.META_SPEC: MetaSpecHandler(),
            TowerLevel.FOUNDATIONS: FoundationsHandler(),
            TowerLevel.INTENT: IntentHandler(),
        }

        # Compression morphisms between levels
        self.compressions: dict[tuple[TowerLevel, TowerLevel], CompressionMorphism] = {}
        self._register_default_compressions()

    def _register_default_compressions(self) -> None:
        """Register default compression morphisms."""
        compressions = [
            CompressionMorphism(
                morphism_id="traces_to_patterns",
                source_level=TowerLevel.TRACE_WITNESSES,
                target_level=TowerLevel.BEHAVIORAL_PATTERNS,
                name="Pattern Extraction",
                description="Extract behavioral patterns from traces",
                preserves=frozenset(["frequency", "flow_structure"]),
                loses=frozenset(["individual_trace_details", "timing"]),
            ),
            CompressionMorphism(
                morphism_id="code_to_traces",
                source_level=TowerLevel.CODE,
                target_level=TowerLevel.TRACE_WITNESSES,
                name="Execution Tracing",
                description="Capture execution traces from code",
                preserves=frozenset(["execution_flow", "state_changes"]),
                loses=frozenset(["static_structure", "comments"]),
            ),
            CompressionMorphism(
                morphism_id="spec_to_code",
                source_level=TowerLevel.SPEC,
                target_level=TowerLevel.CODE,
                name="Implementation Projection",
                description="Project specification to implementation",
                preserves=frozenset(["interface", "composition_structure"]),
                loses=frozenset(["formal_constraints", "proofs"]),
            ),
            CompressionMorphism(
                morphism_id="metaspec_to_spec",
                source_level=TowerLevel.META_SPEC,
                target_level=TowerLevel.SPEC,
                name="Categorical Instantiation",
                description="Instantiate categorical structure as spec",
                preserves=frozenset(["composition_laws", "identity"]),
                loses=frozenset(["abstract_structure", "universal_properties"]),
            ),
            CompressionMorphism(
                morphism_id="foundations_to_metaspec",
                source_level=TowerLevel.FOUNDATIONS,
                target_level=TowerLevel.META_SPEC,
                name="HoTT to Category",
                description="Extract categorical structure from HoTT",
                preserves=frozenset(["types_as_objects", "paths_as_morphisms"]),
                loses=frozenset(["higher_paths", "univalence"]),
            ),
            CompressionMorphism(
                morphism_id="intent_to_foundations",
                source_level=TowerLevel.INTENT,
                target_level=TowerLevel.FOUNDATIONS,
                name="Intent Formalization",
                description="Formalize intent as HoTT types",
                preserves=frozenset(["essential_structure", "relationships"]),
                loses=frozenset(["informal_notes", "visual_layout"]),
            ),
        ]

        for compression in compressions:
            key = (compression.source_level, compression.target_level)
            self.compressions[key] = compression

    async def add_artifact(self, artifact: LevelArtifact) -> None:
        """Add an artifact to the appropriate level."""
        handler = self.handlers.get(artifact.level)
        if handler:
            await handler.add_artifact(artifact)
            logger.info(f"Added artifact {artifact.artifact_id} to level {artifact.level.name}")

    async def get_artifact(self, level: TowerLevel, artifact_id: str) -> LevelArtifact | None:
        """Get an artifact from a specific level."""
        handler = self.handlers.get(level)
        if handler:
            return await handler.get_artifact(artifact_id)
        return None

    async def verify_consistency(
        self,
        source_level: TowerLevel,
        target_level: TowerLevel,
    ) -> list[ConsistencyResult]:
        """Verify consistency between all artifacts at two levels."""
        results: list[ConsistencyResult] = []

        source_handler = self.handlers.get(source_level)
        target_handler = self.handlers.get(target_level)

        if not source_handler or not target_handler:
            return results

        # Verify each pair of artifacts
        for source_artifact in source_handler.artifacts.values():
            for target_artifact in target_handler.artifacts.values():
                result = await self.verifier.verify_consistency(source_artifact, target_artifact)
                results.append(result)

        return results

    async def verify_adjacent_levels(self, level: TowerLevel) -> list[ConsistencyResult]:
        """Verify consistency with adjacent levels."""
        results = []

        # Get adjacent levels
        level_value = int(level)
        adjacent_levels = []

        for other_level in TowerLevel:
            other_value = int(other_level)
            if abs(level_value - other_value) == 1:
                adjacent_levels.append(other_level)

        # Special case: FOUNDATIONS is adjacent to INTENT
        if level == TowerLevel.FOUNDATIONS:
            adjacent_levels.append(TowerLevel.INTENT)
        elif level == TowerLevel.INTENT:
            adjacent_levels.append(TowerLevel.FOUNDATIONS)

        # Verify with each adjacent level
        for adjacent in adjacent_levels:
            level_results = await self.verify_consistency(level, adjacent)
            results.extend(level_results)

        return results

    async def propose_corrections(
        self,
        consistency_result: ConsistencyResult,
    ) -> list[CorrectionProposal]:
        """Propose corrections for inconsistencies."""
        proposals: list[CorrectionProposal] = []

        if consistency_result.is_consistent:
            return proposals

        for violation in consistency_result.violations:
            proposal = await self._generate_correction_proposal(
                violation,
                consistency_result.source_level,
                consistency_result.target_level,
            )
            if proposal:
                proposals.append(proposal)

        return proposals

    async def _generate_correction_proposal(
        self,
        violation: dict[str, Any],
        source_level: TowerLevel,
        target_level: TowerLevel,
    ) -> CorrectionProposal | None:
        """Generate a correction proposal for a violation."""
        violation_type = violation.get("type", "")
        severity = violation.get("severity", "info")

        # Determine correction type
        if source_level < target_level:
            correction_type = "lift"  # Lift lower level to match higher
        else:
            correction_type = "lower"  # Lower higher level to match lower

        # Generate proposal based on violation type
        if violation_type == "unimplemented_spec_path":
            return CorrectionProposal(
                proposal_id=str(uuid4()),
                source_level=source_level,
                target_level=target_level,
                description="Implement missing spec path in code",
                correction_type=correction_type,
                affected_artifacts=[],
                estimated_impact={"effort": "medium", "risk": "low"},
            )
        elif violation_type == "missing_categorical_foundation":
            return CorrectionProposal(
                proposal_id=str(uuid4()),
                source_level=source_level,
                target_level=target_level,
                description="Add categorical structure to meta-spec",
                correction_type="lift",
                affected_artifacts=[],
                estimated_impact={"effort": "high", "risk": "medium"},
            )

        return None

    async def get_tower_summary(self) -> dict[str, Any]:
        """Get a summary of the tower state."""
        summary: dict[str, Any] = {
            "levels": {},
            "compressions": len(self.compressions),
            "total_artifacts": 0,
        }

        for level, handler in self.handlers.items():
            artifact_count = len(handler.artifacts)
            summary["levels"][level.name] = {
                "artifact_count": artifact_count,
                "level_value": int(level),
            }
            summary["total_artifacts"] += artifact_count

        return summary

    async def compress(
        self,
        artifact: LevelArtifact,
        target_level: TowerLevel,
    ) -> LevelArtifact | None:
        """Compress an artifact to a lower level."""
        key = (artifact.level, target_level)
        compression = self.compressions.get(key)

        if not compression:
            logger.warning(f"No compression morphism from {artifact.level} to {target_level}")
            return None

        # Apply compression (simplified - real implementation would transform content)
        compressed_content = {
            "original_id": artifact.artifact_id,
            "original_level": artifact.level.name,
            "compression": compression.name,
            "preserved": list(compression.preserves),
            "content": artifact.content,
        }

        compressed = LevelArtifact(
            artifact_id=str(uuid4()),
            level=target_level,
            name=f"Compressed: {artifact.name}",
            content=compressed_content,
            metadata={"compression_morphism": compression.morphism_id},
        )

        await self.add_artifact(compressed)
        return compressed


# =============================================================================
# Convenience Functions
# =============================================================================


async def create_tower() -> ReflectiveTower:
    """Create a new reflective tower."""
    return ReflectiveTower()


async def verify_tower_consistency(tower: ReflectiveTower) -> dict[str, Any]:
    """Verify consistency across all tower levels."""
    all_results: list[ConsistencyResult] = []

    # Verify each level with its adjacent levels
    for level in TowerLevel:
        results = await tower.verify_adjacent_levels(level)
        all_results.extend(results)

    # Summarize results
    consistent_count = sum(1 for r in all_results if r.is_consistent)
    inconsistent_count = len(all_results) - consistent_count

    return {
        "total_checks": len(all_results),
        "consistent": consistent_count,
        "inconsistent": inconsistent_count,
        "consistency_ratio": consistent_count / max(1, len(all_results)),
        "results": all_results,
    }
