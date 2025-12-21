"""
Verification Models: SQLAlchemy models for formal verification system.

These models support the Formal Verification Metatheory system with:
- Verification graphs (derivation paths from principles to implementation)
- Trace witnesses (behavioral correctness evidence)
- Improvement proposals (self-improvement suggestions)
- Categorical law violations (counter-examples and fixes)

AGENTESE: self.verification.* foundation
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import JSON, DateTime, Enum as SQLEnum, Float, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, CausalMixin, TimestampMixin


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


class VerificationGraph(CausalMixin, TimestampMixin, Base):
    """
    Verification graph representing derivation paths from principles to implementation.

    Stores the logical structure showing how high-level principles derive
    into concrete implementations, with support for contradiction detection
    and orphaned node identification.
    """

    __tablename__ = "verification_graphs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Graph metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0.0")

    # Graph structure (JSON representation)
    nodes: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    edges: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Analysis results
    contradictions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    orphaned_nodes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    derivation_paths: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Status and metrics
    status: Mapped[VerificationStatus] = mapped_column(
        SQLEnum(VerificationStatus), nullable=False, default=VerificationStatus.PENDING
    )
    node_count: Mapped[int] = mapped_column(nullable=False, default=0)
    edge_count: Mapped[int] = mapped_column(nullable=False, default=0)

    def __repr__(self) -> str:
        return (
            f"<VerificationGraph(id={self.id!r}, name={self.name!r}, status={self.status.value})>"
        )


class TraceWitness(CausalMixin, TimestampMixin, Base):
    """
    Enhanced trace witness capturing behavioral correctness evidence.

    Extends the existing kgents witness system with formal verification
    capabilities, storing constructive proofs of specification compliance.
    """

    __tablename__ = "trace_witnesses"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Execution metadata
    agent_path: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    execution_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Trace data
    input_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    output_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    intermediate_steps: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )

    # Verification data
    specification_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    properties_verified: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    violations_found: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )

    # Performance metrics
    execution_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    resource_usage: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Status
    verification_status: Mapped[VerificationStatus] = mapped_column(
        SQLEnum(VerificationStatus), nullable=False, default=VerificationStatus.PENDING
    )

    def __repr__(self) -> str:
        return f"<TraceWitness(id={self.id!r}, agent_path={self.agent_path!r}, status={self.verification_status.value})>"


class CategoricalViolation(CausalMixin, TimestampMixin, Base):
    """
    Record of categorical law violations with counter-examples and remediation.

    Stores violations discovered during categorical law verification,
    including LLM-generated analysis and suggested fixes.
    """

    __tablename__ = "categorical_violations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Violation metadata
    violation_type: Mapped[ViolationType] = mapped_column(
        SQLEnum(ViolationType), nullable=False, index=True
    )
    law_description: Mapped[str] = mapped_column(Text, nullable=False)

    # Morphisms involved
    morphism_f: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    morphism_g: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    morphism_h: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Counter-example data
    test_input: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    expected_result: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    actual_result: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    # LLM analysis
    llm_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_fix: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Resolution
    is_resolved: Mapped[bool] = mapped_column(nullable=False, default=False)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<CategoricalViolation(id={self.id!r}, type={self.violation_type.value}, resolved={self.is_resolved})>"


class ImprovementProposal(CausalMixin, TimestampMixin, Base):
    """
    Self-improvement proposals generated from operational data analysis.

    Stores LLM-generated improvement suggestions with validation results
    and application tracking for continuous system evolution.
    """

    __tablename__ = "improvement_proposals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Proposal metadata
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Source analysis
    source_patterns: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    kgents_principle: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Proposal details
    implementation_suggestion: Mapped[str] = mapped_column(Text, nullable=False)
    risk_assessment: Mapped[str] = mapped_column(String(16), nullable=False)  # LOW/MEDIUM/HIGH
    estimated_impact: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Validation results
    categorical_compliance: Mapped[bool | None] = mapped_column(nullable=True)
    trace_impact_analysis: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    llm_validation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status and lifecycle
    status: Mapped[ProposalStatus] = mapped_column(
        SQLEnum(ProposalStatus), nullable=False, default=ProposalStatus.GENERATED, index=True
    )

    # Application tracking
    applied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    application_results: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"<ImprovementProposal(id={self.id!r}, title={self.title!r}, status={self.status.value})>"


class SpecificationDocument(CausalMixin, TimestampMixin, Base):
    """
    Specification documents for semantic consistency analysis.

    Tracks specification documents and their semantic content for
    cross-document consistency verification and evolution tracking.
    """

    __tablename__ = "specification_documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Document metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # requirements, design, tasks
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0.0")

    # Content analysis
    concepts: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    cross_references: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    semantic_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Consistency analysis
    consistency_issues: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    backward_compatibility: Mapped[bool | None] = mapped_column(nullable=True)

    # Last analysis
    last_analyzed: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    analysis_version: Mapped[str | None] = mapped_column(String(32), nullable=True)

    def __repr__(self) -> str:
        return f"<SpecificationDocument(id={self.id!r}, name={self.name!r}, type={self.document_type})>"


class HoTTType(CausalMixin, TimestampMixin, Base):
    """
    Homotopy Type Theory types for agent representation.

    Stores HoTT type definitions for agents with equivalence structure
    and path composition support for categorical law verification.
    """

    __tablename__ = "hott_types"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Type metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    universe_level: Mapped[int] = mapped_column(nullable=False, default=0)

    # Type definition
    type_definition: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    introduction_rules: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    elimination_rules: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )

    # Equivalence structure
    equivalences: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    isomorphic_types: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    # Path composition
    path_compositions: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Verification status
    is_verified: Mapped[bool] = mapped_column(nullable=False, default=False)
    verification_proof: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<HoTTType(id={self.id!r}, name={self.name!r}, level={self.universe_level})>"
