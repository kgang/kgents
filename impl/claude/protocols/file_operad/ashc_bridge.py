"""
ASHC Bridge: Connect FILE_OPERAD to the Proof-Generating ASHC System.

"The proof IS the decision. The mark IS the witness."

Session 6b implements the bridge between FILE_OPERAD artifacts and the ASHC
proof-generation pipeline:

1. FileTraceToEvidenceAdapter: Convert exploration traces to ASHC evidence
2. SandboxToEvidenceAdapter: Convert sandbox results to ASHC evidence
3. LawProofCompiler: Convert LawDefinition to ProofObligation

The Core Insight (from proof-generation.md):
    "LLM hallucinations don't matter for proofs because proof checkers
    reject invalid proofs." — Martin Kleppmann

See: spec/protocols/file-operad.md (Session 6b)
     spec/protocols/proof-generation.md
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, NewType, Protocol

from .law_parser import (
    LawDefinition,
    LawStatus,
    extract_verification_code,
)

if TYPE_CHECKING:
    from .sandbox import SandboxPolynomial, SandboxResult
    from .trace import FileWiringTrace


logger = logging.getLogger("kgents.file_operad.ashc_bridge")


# =============================================================================
# Type Aliases (matching ASHC contracts)
# =============================================================================

EvidenceId = NewType("EvidenceId", str)
ObligationId = NewType("ObligationId", str)


def generate_evidence_id(source: str) -> EvidenceId:
    """Generate a unique evidence ID from source."""
    hash_val = hashlib.sha256(f"{source}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    return EvidenceId(f"evidence-{hash_val}")


def generate_obligation_id(source: str) -> ObligationId:
    """Generate a unique obligation ID from source."""
    hash_val = hashlib.sha256(f"{source}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    return ObligationId(f"obligation-{hash_val}")


# =============================================================================
# Enums
# =============================================================================


class EvidenceSource(Enum):
    """Source of ASHC evidence."""

    FILE_TRACE = auto()  # From FileWiringTrace (exploration)
    SANDBOX = auto()  # From sandbox execution result
    LAW = auto()  # From law verification


class EvidenceType(Enum):
    """Type of evidence for ASHC."""

    EXPLORATION = auto()  # Navigation/expansion trail
    EXECUTION = auto()  # Code execution result
    VERIFICATION = auto()  # Law verification result


class VerificationResult(Enum):
    """Result of law verification."""

    PASSED = auto()  # Verification succeeded
    FAILED = auto()  # Verification failed
    ERROR = auto()  # Verification errored (different from failed)
    SKIPPED = auto()  # Verification skipped (no code)


# =============================================================================
# Evidence Contracts
# =============================================================================


@dataclass(frozen=True)
class FileOperadEvidence:
    """
    Evidence generated from FILE_OPERAD operations.

    This is the bridge type that connects FILE_OPERAD artifacts
    to the ASHC proof system.

    Laws:
        1. Immutability: Once created, evidence cannot be modified
        2. Traceability: source_id links back to origin
        3. Composability: evidence can be aggregated
    """

    id: EvidenceId
    source: EvidenceSource
    evidence_type: EvidenceType
    timestamp: datetime

    # What was observed/executed
    action: str  # "expand", "execute", "verify", etc.
    target: str  # Path or law name

    # Context for proof search
    context: tuple[str, ...] = ()

    # Result if applicable
    success: bool = True
    error: str | None = None

    # Cross-references
    related_ids: tuple[str, ...] = ()  # Related evidence/traces

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for persistence/API."""
        return {
            "id": str(self.id),
            "source": self.source.name,
            "evidence_type": self.evidence_type.name,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "target": self.target,
            "context": list(self.context),
            "success": self.success,
            "error": self.error,
            "related_ids": list(self.related_ids),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FileOperadEvidence":
        """Deserialize from dictionary."""
        return cls(
            id=EvidenceId(data["id"]),
            source=EvidenceSource[data["source"]],
            evidence_type=EvidenceType[data["evidence_type"]],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            action=data["action"],
            target=data["target"],
            context=tuple(data.get("context", [])),
            success=data.get("success", True),
            error=data.get("error"),
            related_ids=tuple(data.get("related_ids", [])),
        )


@dataclass(frozen=True)
class LawVerificationEvidence(FileOperadEvidence):
    """
    Specialized evidence from law verification.

    Extends FileOperadEvidence with law-specific fields.
    """

    law_name: str = ""
    law_equation: str = ""
    verification_result: VerificationResult = VerificationResult.SKIPPED
    verification_output: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize with law-specific fields."""
        base = super().to_dict()
        base.update(
            {
                "law_name": self.law_name,
                "law_equation": self.law_equation,
                "verification_result": self.verification_result.name,
                "verification_output": self.verification_output,
            }
        )
        return base


# =============================================================================
# Adapters
# =============================================================================


class FileTraceToEvidenceAdapter:
    """
    Adapter that converts FileWiringTraces to FileOperadEvidence.

    Pattern: Adapter (GoF)
    Purpose: Bridge FILE_OPERAD exploration traces to ASHC evidence format.

    Example:
        >>> adapter = FileTraceToEvidenceAdapter()
        >>> traces = store.recent(10)
        >>> evidence = adapter.convert_many(traces)
    """

    def convert(self, trace: "FileWiringTrace") -> FileOperadEvidence:
        """
        Convert a single trace to evidence.

        Args:
            trace: A FileWiringTrace from exploration

        Returns:
            FileOperadEvidence suitable for ASHC
        """
        # Build context from trace fields
        context = []
        if trace.edge_type:
            context.append(f"edge_type: {trace.edge_type}")
        if trace.parent_path:
            context.append(f"parent: {trace.parent_path}")
        if trace.depth > 0:
            context.append(f"depth: {trace.depth}")
        if trace.diff:
            context.append(f"diff: {trace.diff[:200]}")  # Truncate long diffs
        if trace.ghost_alternatives:
            context.append(f"alternatives: {', '.join(trace.ghost_alternatives[:5])}")

        return FileOperadEvidence(
            id=generate_evidence_id(f"trace:{trace.path}:{trace.operation}"),
            source=EvidenceSource.FILE_TRACE,
            evidence_type=EvidenceType.EXPLORATION,
            timestamp=trace.timestamp,
            action=trace.operation,
            target=trace.path,
            context=tuple(context),
            success=True,  # Traces are always "successful" - they happened
            related_ids=(trace.session_id,) if trace.session_id else (),
        )

    def convert_many(self, traces: list["FileWiringTrace"]) -> list[FileOperadEvidence]:
        """Convert multiple traces to evidence."""
        return [self.convert(trace) for trace in traces]

    def aggregate_session(
        self,
        traces: list["FileWiringTrace"],
        session_id: str,
    ) -> FileOperadEvidence:
        """
        Aggregate a session's traces into single evidence.

        Useful for summarizing exploration sessions for ASHC.
        """
        if not traces:
            raise ValueError("Cannot aggregate empty trace list")

        # Aggregate paths explored
        paths = sorted(set(t.path for t in traces))
        operations = sorted(set(t.operation for t in traces))

        context = [
            f"paths_explored: {len(paths)}",
            f"operations: {', '.join(operations)}",
            f"trace_count: {len(traces)}",
            f"duration: {(traces[-1].timestamp - traces[0].timestamp).total_seconds():.1f}s",
        ]

        return FileOperadEvidence(
            id=generate_evidence_id(f"session:{session_id}"),
            source=EvidenceSource.FILE_TRACE,
            evidence_type=EvidenceType.EXPLORATION,
            timestamp=traces[0].timestamp,
            action="session_aggregate",
            target=session_id,
            context=tuple(context),
            success=True,
            related_ids=tuple(f"trace:{t.path}" for t in traces[:10]),  # First 10
        )


class SandboxToEvidenceAdapter:
    """
    Adapter that converts sandbox results to FileOperadEvidence.

    Pattern: Adapter (GoF)
    Purpose: Bridge sandbox execution to ASHC evidence format.

    Example:
        >>> adapter = SandboxToEvidenceAdapter()
        >>> sandbox = store.get(sandbox_id)
        >>> evidence = adapter.convert(sandbox)
    """

    def convert(self, sandbox: "SandboxPolynomial") -> FileOperadEvidence:
        """
        Convert a sandbox to evidence.

        Args:
            sandbox: A SandboxPolynomial

        Returns:
            FileOperadEvidence suitable for ASHC
        """
        from .sandbox import SandboxPhase

        # Build context from sandbox state
        context = [
            f"phase: {sandbox.phase.name}",
            f"runtime: {sandbox.config.runtime.value}",
            f"has_modifications: {sandbox.has_modifications}",
        ]

        if sandbox.execution_results:
            last_result = sandbox.execution_results[-1]
            context.append(f"last_success: {last_result.success}")
            if last_result.error:
                context.append(f"last_error: {last_result.error[:200]}")
            context.append(f"execution_count: {len(sandbox.execution_results)}")

        if sandbox.promoted_to:
            context.append(f"promoted_to: {sandbox.promoted_to}")

        # Determine success based on phase
        success = sandbox.phase in {SandboxPhase.ACTIVE, SandboxPhase.PROMOTED}
        error = None
        if sandbox.phase == SandboxPhase.EXPIRED:
            error = "Sandbox expired before promotion"
        elif sandbox.phase == SandboxPhase.DISCARDED:
            error = "Sandbox discarded by user"

        return FileOperadEvidence(
            id=generate_evidence_id(f"sandbox:{sandbox.id}"),
            source=EvidenceSource.SANDBOX,
            evidence_type=EvidenceType.EXECUTION,
            timestamp=sandbox.created_at,
            action=f"sandbox_{sandbox.phase.name.lower()}",
            target=sandbox.source_path,
            context=tuple(context),
            success=success,
            error=error,
            related_ids=(str(sandbox.id),),
        )

    def convert_result(
        self,
        sandbox: "SandboxPolynomial",
        result: "SandboxResult",
        result_index: int = 0,
    ) -> FileOperadEvidence:
        """
        Convert a specific sandbox result to evidence.

        Args:
            sandbox: The parent sandbox
            result: A specific execution result
            result_index: Index of this result in sandbox.execution_results

        Returns:
            FileOperadEvidence for this specific execution
        """
        context = [
            f"sandbox_id: {sandbox.id}",
            f"runtime: {sandbox.config.runtime.value}",
            f"execution_time_ms: {result.execution_time_ms:.1f}",
            f"result_index: {result_index}",
        ]

        if result.stdout:
            context.append(f"stdout: {result.stdout[:200]}")
        if result.stderr:
            context.append(f"stderr: {result.stderr[:200]}")

        return FileOperadEvidence(
            id=generate_evidence_id(f"sandbox_result:{sandbox.id}:{result_index}"),
            source=EvidenceSource.SANDBOX,
            evidence_type=EvidenceType.EXECUTION,
            timestamp=sandbox.created_at,  # Result doesn't have timestamp
            action="execute",
            target=sandbox.source_path,
            context=tuple(context),
            success=result.success,
            error=result.error,
            related_ids=(str(sandbox.id),),
        )


# =============================================================================
# Proof Compiler
# =============================================================================


@dataclass(frozen=True)
class ProofObligation:
    """
    A proof obligation generated from a law.

    This is a bridge type that matches the ASHC ProofObligation contract
    but is specialized for FILE_OPERAD laws.

    From proof-generation.md:
        ProofObligation : FailedGeneration -> (Spec, Property, Witness)
    """

    id: ObligationId
    law_name: str
    property: str  # The formal statement (equation)
    source_location: str  # Path to .law file
    context: tuple[str, ...] = ()  # Hints for proof search
    created_at: datetime = field(default_factory=datetime.now)

    # Law-specific fields
    verification_code: str = ""
    operations: tuple[str, ...] = ()
    category: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "law_name": self.law_name,
            "property": self.property,
            "source_location": self.source_location,
            "context": list(self.context),
            "created_at": self.created_at.isoformat(),
            "verification_code": self.verification_code,
            "operations": list(self.operations),
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProofObligation":
        """Deserialize from dictionary."""
        return cls(
            id=ObligationId(data["id"]),
            law_name=data["law_name"],
            property=data["property"],
            source_location=data["source_location"],
            context=tuple(data.get("context", [])),
            created_at=datetime.fromisoformat(data["created_at"]),
            verification_code=data.get("verification_code", ""),
            operations=tuple(data.get("operations", [])),
            category=data.get("category", ""),
        )


class LawProofCompiler:
    """
    Compiler that converts LawDefinitions to ProofObligations.

    Pattern: Compiler
    Purpose: Transform law specifications into proof search targets.

    The proof obligation includes:
    - The formal property (equation) to prove
    - Context hints from the law (operations, category, wires_to)
    - The verification code (Python test) as additional context

    Example:
        >>> compiler = LawProofCompiler()
        >>> law = parse_law_file(path)
        >>> obligation = compiler.compile(law)
    """

    def compile(self, law: LawDefinition) -> ProofObligation:
        """
        Compile a law into a proof obligation.

        Args:
            law: A parsed LawDefinition

        Returns:
            ProofObligation ready for proof search
        """
        # Build context from law fields
        context = []

        # Category provides semantic hints
        if law.category:
            context.append(f"category: {law.category}")

        # Operations tell us what to focus on
        if law.operations:
            context.append(f"operations: {', '.join(law.operations)}")

        # Description provides human context
        if law.description:
            context.append(f"description: {law.description}")

        # Wires_to shows dependencies
        if law.wires_to:
            context.append(f"depends_on: {', '.join(law.wires_to)}")

        # Verification history
        if law.last_verified:
            context.append(f"last_verified: {law.last_verified.isoformat()}")
            if law.verified_by:
                context.append(f"verified_by: {law.verified_by}")

        # Current status
        context.append(f"current_status: {law.status.name}")

        return ProofObligation(
            id=generate_obligation_id(f"law:{law.name}"),
            law_name=law.name,
            property=law.equation,
            source_location=law.source_path or f"<law:{law.name}>",
            context=tuple(context),
            verification_code=extract_verification_code(law),
            operations=law.operations,
            category=law.category,
        )

    def compile_many(self, laws: list[LawDefinition]) -> list[ProofObligation]:
        """Compile multiple laws to obligations."""
        return [self.compile(law) for law in laws]

    def compile_unverified(self, laws: list[LawDefinition]) -> list[ProofObligation]:
        """Compile only unverified/failed laws."""
        return [
            self.compile(law)
            for law in laws
            if law.status in {LawStatus.UNVERIFIED, LawStatus.FAILED}
        ]


# =============================================================================
# Law Verifier
# =============================================================================


@dataclass
class LawVerificationResult:
    """Result of running law verification code."""

    law: LawDefinition
    result: VerificationResult
    output: str = ""
    error: str | None = None
    duration_ms: float = 0.0

    @property
    def success(self) -> bool:
        """True if verification passed."""
        return self.result == VerificationResult.PASSED

    def to_evidence(self) -> LawVerificationEvidence:
        """Convert to evidence for ASHC."""
        return LawVerificationEvidence(
            id=generate_evidence_id(f"verify:{self.law.name}"),
            source=EvidenceSource.LAW,
            evidence_type=EvidenceType.VERIFICATION,
            timestamp=datetime.now(),
            action="verify",
            target=self.law.source_path or self.law.name,
            context=(
                f"duration_ms: {self.duration_ms:.1f}",
                f"result: {self.result.name}",
            ),
            success=self.success,
            error=self.error,
            law_name=self.law.name,
            law_equation=self.law.equation,
            verification_result=self.result,
            verification_output=self.output,
        )


class LawVerifier:
    """
    Execute law verification code and produce evidence.

    Pattern: Executor
    Purpose: Run the embedded Python tests in .law files.

    SECURITY: This executes arbitrary Python code from .law files.
    Only run on trusted law files.

    Example:
        >>> verifier = LawVerifier()
        >>> result = verifier.verify(law)
        >>> if result.success:
        ...     print(f"{law.name} verified!")
    """

    def verify(self, law: LawDefinition) -> LawVerificationResult:
        """
        Execute the verification code for a law.

        Args:
            law: A LawDefinition with verification_code

        Returns:
            LawVerificationResult with execution outcome
        """
        import time

        code = extract_verification_code(law)

        if not code:
            return LawVerificationResult(
                law=law,
                result=VerificationResult.SKIPPED,
                output="No verification code provided",
            )

        start = time.perf_counter()

        try:
            # Create isolated namespace for execution
            namespace: dict[str, Any] = {
                "__name__": "__law_verification__",
                "__doc__": f"Verification for {law.name}",
            }

            # Execute the verification code
            exec(code, namespace)

            # Look for test functions and run them
            test_functions = [
                (name, func)
                for name, func in namespace.items()
                if name.startswith("test_") and callable(func)
            ]

            if not test_functions:
                return LawVerificationResult(
                    law=law,
                    result=VerificationResult.SKIPPED,
                    output="No test functions found (expected test_*)",
                    duration_ms=(time.perf_counter() - start) * 1000,
                )

            # Run each test function
            outputs = []
            for name, func in test_functions:
                try:
                    func()
                    outputs.append(f"PASSED: {name}")
                except AssertionError as e:
                    duration = (time.perf_counter() - start) * 1000
                    return LawVerificationResult(
                        law=law,
                        result=VerificationResult.FAILED,
                        output="\n".join(outputs + [f"FAILED: {name}"]),
                        error=str(e),
                        duration_ms=duration,
                    )
                except Exception as e:
                    duration = (time.perf_counter() - start) * 1000
                    return LawVerificationResult(
                        law=law,
                        result=VerificationResult.ERROR,
                        output="\n".join(outputs + [f"ERROR: {name}"]),
                        error=f"{type(e).__name__}: {e}",
                        duration_ms=duration,
                    )

            duration = (time.perf_counter() - start) * 1000
            return LawVerificationResult(
                law=law,
                result=VerificationResult.PASSED,
                output="\n".join(outputs),
                duration_ms=duration,
            )

        except SyntaxError as e:
            duration = (time.perf_counter() - start) * 1000
            return LawVerificationResult(
                law=law,
                result=VerificationResult.ERROR,
                error=f"SyntaxError: {e}",
                duration_ms=duration,
            )
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            return LawVerificationResult(
                law=law,
                result=VerificationResult.ERROR,
                error=f"{type(e).__name__}: {e}",
                duration_ms=duration,
            )

    def verify_many(self, laws: list[LawDefinition]) -> list[LawVerificationResult]:
        """Verify multiple laws."""
        return [self.verify(law) for law in laws]


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Type aliases
    "EvidenceId",
    "ObligationId",
    # Enums
    "EvidenceSource",
    "EvidenceType",
    "VerificationResult",
    # Evidence contracts
    "FileOperadEvidence",
    "LawVerificationEvidence",
    # Adapters
    "FileTraceToEvidenceAdapter",
    "SandboxToEvidenceAdapter",
    # Proof compiler
    "ProofObligation",
    "LawProofCompiler",
    # Law verification
    "LawVerificationResult",
    "LawVerifier",
    # Helpers
    "generate_evidence_id",
    "generate_obligation_id",
]
