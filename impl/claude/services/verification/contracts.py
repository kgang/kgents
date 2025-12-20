"""
Verification Contracts: Data classes for formal verification system.

These contracts define the domain types used by the verification service,
separate from the SQLAlchemy models for clean architecture.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class VerificationStatus(str, Enum):
    """Status of verification operations."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILURE = "failure"
    NEEDS_REVIEW = "needs_review"


class ViolationType(str, Enum):
    """Types of categorical law violations."""

    COMPOSITION_ASSOCIATIVITY = "composition_associativity"
    IDENTITY_LAW = "identity_law"
    FUNCTOR_PRESERVATION = "functor_preservation"
    OPERAD_COHERENCE = "operad_coherence"
    SHEAF_GLUING = "sheaf_gluing"
    SEMANTIC_INCONSISTENCY = "semantic_inconsistency"
    DERIVATION_GAP = "derivation_gap"


class ProposalStatus(str, Enum):
    """Status of improvement proposals."""

    GENERATED = "generated"
    VALIDATED = "validated"
    APPROVED = "approved"
    APPLIED = "applied"
    REJECTED = "rejected"


@dataclass(frozen=True)
class GraphNode:
    """A node in the verification graph."""

    node_id: str
    node_type: str  # principle, spec, implementation, artifact
    name: str
    description: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphEdge:
    """An edge in the verification graph representing derivation."""

    source_id: str
    target_id: str
    derivation_type: str  # derives_from, implements, refines
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Contradiction:
    """A contradiction detected in the verification graph."""

    node_ids: list[str]
    description: str
    resolution_strategies: list[str]
    severity: str  # low, medium, high, critical


@dataclass(frozen=True)
class DerivationPath:
    """A path from principle to implementation."""

    principle_id: str
    implementation_id: str
    path_nodes: list[str]
    path_edges: list[GraphEdge]
    is_complete: bool


@dataclass(frozen=True)
class VerificationGraphResult:
    """Result of verification graph analysis."""

    graph_id: str
    name: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    contradictions: list[Contradiction]
    orphaned_nodes: list[str]
    derivation_paths: list[DerivationPath]
    status: VerificationStatus
    created_at: datetime


@dataclass(frozen=True)
class AgentMorphism:
    """An agent morphism for categorical verification."""

    morphism_id: str
    name: str
    description: str
    source_type: str
    target_type: str
    implementation: dict[str, Any]


@dataclass(frozen=True)
class CounterExample:
    """A counter-example for categorical law violation."""

    test_input: dict[str, Any]
    expected_result: dict[str, Any]
    actual_result: dict[str, Any]
    morphisms: tuple[AgentMorphism, ...]


@dataclass(frozen=True)
class VerificationResult:
    """Result of categorical law verification."""

    law_name: str
    success: bool
    counter_example: CounterExample | None
    llm_analysis: str | None
    suggested_fix: str | None
    test_results: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class SpecProperty:
    """A property that must hold for a specification."""

    property_id: str
    property_type: str  # invariant, safety, liveness, composition
    formal_statement: str
    natural_language: str
    test_strategy: str


@dataclass(frozen=True)
class Specification:
    """A formal specification with properties and constraints."""

    spec_id: str
    name: str
    version: str
    properties: frozenset[SpecProperty]
    derivation_source: str | None = None


@dataclass(frozen=True)
class ExecutionStep:
    """A single step in agent execution."""

    step_id: str
    timestamp: datetime
    operation: str
    input_state: dict[str, Any]
    output_state: dict[str, Any]
    side_effects: list[dict[str, Any]]


@dataclass(frozen=True)
class TraceWitnessResult:
    """Result of trace witness verification."""

    witness_id: str
    agent_path: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    intermediate_steps: list[ExecutionStep]
    specification_id: str | None
    properties_verified: list[str]
    violations_found: list[dict[str, Any]]
    verification_status: VerificationStatus
    execution_time_ms: float | None
    created_at: datetime


@dataclass(frozen=True)
class BehavioralPattern:
    """A behavioral pattern extracted from trace corpus."""

    pattern_id: str
    pattern_type: str
    description: str
    frequency: int
    example_traces: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ImprovementProposalResult:
    """Result of improvement proposal generation."""

    proposal_id: str
    title: str
    description: str
    category: str
    source_patterns: list[BehavioralPattern]
    kgents_principle: str | None
    implementation_suggestion: str
    risk_assessment: str  # LOW, MEDIUM, HIGH
    estimated_impact: dict[str, Any]
    categorical_compliance: bool | None
    trace_impact_analysis: dict[str, Any]
    llm_validation: str | None
    status: ProposalStatus
    created_at: datetime


@dataclass(frozen=True)
class SemanticConsistencyResult:
    """Result of semantic consistency analysis."""

    document_ids: list[str]
    consistent: bool
    conflicts: list[dict[str, Any]]
    cross_references: dict[str, Any]
    backward_compatible: bool
    suggestions: list[str]


@dataclass(frozen=True)
class HoTTTypeResult:
    """Result of HoTT type representation."""

    type_id: str
    name: str
    universe_level: int
    type_definition: dict[str, Any]
    equivalences: list[dict[str, Any]]
    isomorphic_types: list[str]
    is_verified: bool
    verification_proof: str | None
