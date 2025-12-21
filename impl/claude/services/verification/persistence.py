# mypy: ignore-errors
"""
Verification Persistence: Data access layer for formal verification system.

Provides persistence operations for verification graphs, trace witnesses,
improvement proposals, and categorical violations using SQLAlchemy and D-gent.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agents.d import DgentProtocol, TableAdapter
from models.verification import (
    CategoricalViolation,
    HoTTType,
    ImprovementProposal,
    ProposalStatus as ModelProposalStatus,
    SpecificationDocument,
    TraceWitness,
    VerificationGraph,
    VerificationStatus as ModelVerificationStatus,
    ViolationType as ModelViolationType,
)

from .contracts import (
    BehavioralPattern,
    CounterExample,
    HoTTTypeResult,
    ImprovementProposalResult,
    ProposalStatus,
    SemanticConsistencyResult,
    TraceWitnessResult,
    VerificationGraphResult,
    VerificationResult,
    VerificationStatus,
    ViolationType,
)

logger = logging.getLogger(__name__)


class VerificationPersistence:
    """
    Persistence layer for the formal verification system.

    Combines SQLAlchemy for structured queries with D-gent for semantic search.
    Follows the TableAdapter pattern used by other Crown Jewels.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        dgent: DgentProtocol,
    ):
        self.session_factory = session_factory
        self.dgent = dgent

        # Table adapters for each model
        self.graphs = TableAdapter(
            model=VerificationGraph,
            session_factory=session_factory,
        )
        self.witnesses = TableAdapter(
            model=TraceWitness,
            session_factory=session_factory,
        )
        self.violations = TableAdapter(
            model=CategoricalViolation,
            session_factory=session_factory,
        )
        self.proposals = TableAdapter(
            model=ImprovementProposal,
            session_factory=session_factory,
        )
        self.specifications = TableAdapter(
            model=SpecificationDocument,
            session_factory=session_factory,
        )
        self.hott_types = TableAdapter(
            model=HoTTType,
            session_factory=session_factory,
        )

    # ========================================================================
    # Verification Graphs
    # ========================================================================

    async def create_verification_graph(
        self,
        name: str,
        description: str | None = None,
        nodes: dict[str, Any] | None = None,
        edges: dict[str, Any] | None = None,
    ) -> VerificationGraphResult:
        """Create a new verification graph."""

        graph_id = str(uuid4())

        graph = VerificationGraph(
            id=graph_id,
            name=name,
            description=description,
            nodes=nodes or {},
            edges=edges or {},
            status=ModelVerificationStatus.PENDING,
        )

        await self.graphs.create(graph)

        logger.info(f"Created verification graph: {graph_id}")

        return VerificationGraphResult(
            graph_id=graph_id,
            name=name,
            nodes=[],  # Will be populated by graph engine
            edges=[],
            contradictions=[],
            orphaned_nodes=[],
            derivation_paths=[],
            status=VerificationStatus.PENDING,
            created_at=graph.created_at,
        )

    async def get_verification_graph(self, graph_id: str) -> VerificationGraphResult | None:
        """Get a verification graph by ID."""

        graph = await self.graphs.get(graph_id)
        if not graph:
            return None

        return VerificationGraphResult(
            graph_id=graph.id,
            name=graph.name,
            nodes=[],  # TODO: Convert from JSON to GraphNode objects
            edges=[],  # TODO: Convert from JSON to GraphEdge objects
            contradictions=[],  # TODO: Convert from JSON
            orphaned_nodes=graph.orphaned_nodes,
            derivation_paths=[],  # TODO: Convert from JSON
            status=VerificationStatus(graph.status.value),
            created_at=graph.created_at,
        )

    async def update_graph_analysis(
        self,
        graph_id: str,
        contradictions: list[dict[str, Any]],
        orphaned_nodes: list[str],
        derivation_paths: dict[str, Any],
        status: VerificationStatus,
    ) -> None:
        """Update graph analysis results."""

        updates = {
            "contradictions": contradictions,
            "orphaned_nodes": orphaned_nodes,
            "derivation_paths": derivation_paths,
            "status": ModelVerificationStatus(status.value),
        }

        await self.graphs.update(graph_id, updates)
        logger.info(f"Updated graph analysis: {graph_id}")

    # ========================================================================
    # Trace Witnesses
    # ========================================================================

    async def create_trace_witness(
        self,
        agent_path: str,
        input_data: dict[str, Any],
        output_data: dict[str, Any],
        intermediate_steps: list[dict[str, Any]] | None = None,
        execution_id: str | None = None,
        specification_id: str | None = None,
    ) -> TraceWitnessResult:
        """Create a new trace witness."""

        witness_id = str(uuid4())

        witness = TraceWitness(
            id=witness_id,
            agent_path=agent_path,
            execution_id=execution_id,
            input_data=input_data,
            output_data=output_data,
            intermediate_steps=intermediate_steps or [],
            specification_id=specification_id,
            verification_status=ModelVerificationStatus.PENDING,
        )

        await self.witnesses.create(witness)

        # Store semantic representation in D-gent for pattern analysis
        await self._store_witness_semantics(witness_id, agent_path, input_data, output_data)

        logger.info(f"Created trace witness: {witness_id}")

        return TraceWitnessResult(
            witness_id=witness_id,
            agent_path=agent_path,
            input_data=input_data,
            output_data=output_data,
            intermediate_steps=[],  # TODO: Convert to ExecutionStep objects
            specification_id=specification_id,
            properties_verified=[],
            violations_found=[],
            verification_status=VerificationStatus.PENDING,
            execution_time_ms=None,
            created_at=witness.created_at,
        )

    async def get_trace_witness(self, witness_id: str) -> TraceWitnessResult | None:
        """Get a trace witness by ID."""

        witness = await self.witnesses.get(witness_id)
        if not witness:
            return None

        return TraceWitnessResult(
            witness_id=witness.id,
            agent_path=witness.agent_path,
            input_data=witness.input_data,
            output_data=witness.output_data,
            intermediate_steps=[],  # TODO: Convert from JSON
            specification_id=witness.specification_id,
            properties_verified=witness.properties_verified,
            violations_found=witness.violations_found,
            verification_status=VerificationStatus(witness.verification_status.value),
            execution_time_ms=witness.execution_time_ms,
            created_at=witness.created_at,
        )

    async def update_witness_verification(
        self,
        witness_id: str,
        properties_verified: list[str],
        violations_found: list[dict[str, Any]],
        status: VerificationStatus,
    ) -> None:
        """Update witness verification results."""

        updates = {
            "properties_verified": properties_verified,
            "violations_found": violations_found,
            "verification_status": ModelVerificationStatus(status.value),
        }

        await self.witnesses.update(witness_id, updates)
        logger.info(f"Updated witness verification: {witness_id}")

    async def get_witnesses_by_agent(
        self, agent_path: str, limit: int = 100
    ) -> list[TraceWitnessResult]:
        """Get trace witnesses for a specific agent path."""

        async with self.session_factory() as session:
            stmt = (
                select(TraceWitness)
                .where(TraceWitness.agent_path == agent_path)
                .order_by(TraceWitness.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            witnesses = result.scalars().all()

        return [
            TraceWitnessResult(
                witness_id=w.id,
                agent_path=w.agent_path,
                input_data=w.input_data,
                output_data=w.output_data,
                intermediate_steps=[],
                specification_id=w.specification_id,
                properties_verified=w.properties_verified,
                violations_found=w.violations_found,
                verification_status=VerificationStatus(w.verification_status.value),
                execution_time_ms=w.execution_time_ms,
                created_at=w.created_at,
            )
            for w in witnesses
        ]

    # ========================================================================
    # Categorical Violations
    # ========================================================================

    async def create_categorical_violation(
        self,
        violation_type: ViolationType,
        law_description: str,
        counter_example: CounterExample,
        llm_analysis: str | None = None,
        suggested_fix: str | None = None,
    ) -> str:
        """Create a new categorical violation record."""

        violation_id = str(uuid4())

        violation = CategoricalViolation(
            id=violation_id,
            violation_type=ModelViolationType(violation_type.value),
            law_description=law_description,
            test_input=counter_example.test_input,
            expected_result=counter_example.expected_result,
            actual_result=counter_example.actual_result,
            llm_analysis=llm_analysis,
            suggested_fix=suggested_fix,
        )

        await self.violations.create(violation)

        logger.warning(f"Created categorical violation: {violation_id} ({violation_type.value})")

        return violation_id

    async def resolve_violation(self, violation_id: str, resolution_notes: str) -> None:
        """Mark a categorical violation as resolved."""

        updates = {
            "is_resolved": True,
            "resolution_notes": resolution_notes,
            "resolved_at": datetime.utcnow(),
        }

        await self.violations.update(violation_id, updates)
        logger.info(f"Resolved categorical violation: {violation_id}")

    # ========================================================================
    # Improvement Proposals
    # ========================================================================

    async def create_improvement_proposal(
        self,
        title: str,
        description: str,
        category: str,
        implementation_suggestion: str,
        risk_assessment: str,
        source_patterns: list[BehavioralPattern] | None = None,
        kgents_principle: str | None = None,
    ) -> ImprovementProposalResult:
        """Create a new improvement proposal."""

        proposal_id = str(uuid4())

        proposal = ImprovementProposal(
            id=proposal_id,
            title=title,
            description=description,
            category=category,
            implementation_suggestion=implementation_suggestion,
            risk_assessment=risk_assessment,
            source_patterns=[p.__dict__ for p in (source_patterns or [])],
            kgents_principle=kgents_principle,
            status=ModelProposalStatus.GENERATED,
        )

        await self.proposals.create(proposal)

        logger.info(f"Created improvement proposal: {proposal_id}")

        return ImprovementProposalResult(
            proposal_id=proposal_id,
            title=title,
            description=description,
            category=category,
            source_patterns=source_patterns or [],
            kgents_principle=kgents_principle,
            implementation_suggestion=implementation_suggestion,
            risk_assessment=risk_assessment,
            estimated_impact={},
            categorical_compliance=None,
            trace_impact_analysis={},
            llm_validation=None,
            status=ProposalStatus.GENERATED,
            created_at=proposal.created_at,
        )

    async def update_proposal_validation(
        self,
        proposal_id: str,
        categorical_compliance: bool,
        trace_impact_analysis: dict[str, Any],
        llm_validation: str,
        status: ProposalStatus,
    ) -> None:
        """Update proposal validation results."""

        updates = {
            "categorical_compliance": categorical_compliance,
            "trace_impact_analysis": trace_impact_analysis,
            "llm_validation": llm_validation,
            "status": ModelProposalStatus(status.value),
        }

        await self.proposals.update(proposal_id, updates)
        logger.info(f"Updated proposal validation: {proposal_id}")

    # ========================================================================
    # Semantic Consistency
    # ========================================================================

    async def create_specification_document(
        self,
        name: str,
        document_type: str,
        file_path: str,
        concepts: list[str],
        semantic_hash: str,
        version: str = "1.0.0",
    ) -> str:
        """Create a new specification document record."""

        doc_id = str(uuid4())

        document = SpecificationDocument(
            id=doc_id,
            name=name,
            document_type=document_type,
            file_path=file_path,
            version=version,
            concepts=concepts,
            semantic_hash=semantic_hash,
        )

        await self.specifications.create(document)

        logger.info(f"Created specification document: {doc_id}")

        return doc_id

    async def analyze_semantic_consistency(
        self,
        document_ids: list[str],
    ) -> SemanticConsistencyResult:
        """Analyze semantic consistency across documents."""

        # TODO: Implement semantic consistency analysis
        # This would involve:
        # 1. Loading documents by IDs
        # 2. Extracting concepts and cross-references
        # 3. Detecting conflicts and inconsistencies
        # 4. Checking backward compatibility

        return SemanticConsistencyResult(
            document_ids=document_ids,
            consistent=True,  # Placeholder
            conflicts=[],
            cross_references={},
            backward_compatible=True,
            suggestions=[],
        )

    # ========================================================================
    # HoTT Types
    # ========================================================================

    async def create_hott_type(
        self,
        name: str,
        universe_level: int,
        type_definition: dict[str, Any],
        introduction_rules: list[dict[str, Any]] | None = None,
        elimination_rules: list[dict[str, Any]] | None = None,
    ) -> HoTTTypeResult:
        """Create a new HoTT type."""

        type_id = str(uuid4())

        hott_type = HoTTType(
            id=type_id,
            name=name,
            universe_level=universe_level,
            type_definition=type_definition,
            introduction_rules=introduction_rules or [],
            elimination_rules=elimination_rules or [],
        )

        await self.hott_types.create(hott_type)

        logger.info(f"Created HoTT type: {type_id}")

        return HoTTTypeResult(
            type_id=type_id,
            name=name,
            universe_level=universe_level,
            type_definition=type_definition,
            equivalences=[],
            isomorphic_types=[],
            is_verified=False,
            verification_proof=None,
        )

    # ========================================================================
    # Private Methods
    # ========================================================================

    async def _store_witness_semantics(
        self,
        witness_id: str,
        agent_path: str,
        input_data: dict[str, Any],
        output_data: dict[str, Any],
    ) -> None:
        """Store trace witness in D-gent for semantic analysis."""

        try:
            # Create semantic representation for pattern analysis
            semantic_content = {
                "witness_id": witness_id,
                "agent_path": agent_path,
                "input_summary": str(input_data)[:500],  # Truncate for embedding
                "output_summary": str(output_data)[:500],
                "witness_type": "trace_execution",
            }

            await self.dgent.store(
                datum_id=f"witness_{witness_id}",
                content=semantic_content,
                metadata={
                    "type": "trace_witness",
                    "agent_path": agent_path,
                    "created_at": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.warning(f"Failed to store witness semantics: {e}")
            # Don't fail the main operation if D-gent storage fails
