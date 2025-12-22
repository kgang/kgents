"""
Tests for ASHC Bridge (Session 6b).

"The proof IS the decision. The mark IS the witness."
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from ..ashc_bridge import (
    EvidenceId,
    EvidenceSource,
    EvidenceType,
    FileOperadEvidence,
    FileTraceToEvidenceAdapter,
    LawProofCompiler,
    LawVerificationEvidence,
    LawVerificationResult,
    LawVerifier,
    ObligationId,
    ProofObligation,
    SandboxToEvidenceAdapter,
    VerificationResult,
    generate_evidence_id,
    generate_obligation_id,
)
from ..law_parser import LawDefinition, LawStatus
from ..sandbox import SandboxConfig, SandboxPhase, SandboxPolynomial, SandboxResult
from ..trace import FileWiringTrace


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_trace() -> FileWiringTrace:
    """Sample file wiring trace."""
    return FileWiringTrace(
        path="/test/path.op",
        operation="expand",
        timestamp=datetime.now(),
        actor="user",
        edge_type="enables",
        parent_path="/test/parent.op",
        depth=1,
        session_id="session-001",
    )


@pytest.fixture
def sample_traces() -> list[FileWiringTrace]:
    """Multiple sample traces for aggregation tests."""
    base_time = datetime.now()
    return [
        FileWiringTrace(
            path=f"/test/path{i}.op",
            operation="expand",
            timestamp=base_time + timedelta(seconds=i),
            actor="user",
            edge_type="enables",
            depth=i,
            session_id="session-002",
        )
        for i in range(5)
    ]


@pytest.fixture
def sample_sandbox() -> SandboxPolynomial:
    """Sample sandbox for testing."""
    return SandboxPolynomial.create(
        source_path="/test/sandbox.op",
        content="# Test sandbox content",
        config=SandboxConfig(),
    )


@pytest.fixture
def sample_law() -> LawDefinition:
    """Sample law definition."""
    return LawDefinition(
        name="test_law",
        equation="f(x) == x",
        operations=("f",),
        category="Identity",
        status=LawStatus.VERIFIED,
        verification_code="```python\ndef test_law():\n    assert 1 == 1\n```",
        description="A test law",
        wires_to=("OTHER_OPERAD/other",),
        source_path="/test/law.law",
    )


@pytest.fixture
def executable_law() -> LawDefinition:
    """Law with executable verification code."""
    return LawDefinition(
        name="executable_law",
        equation="1 + 1 == 2",
        operations=("add",),
        category="Arithmetic",
        status=LawStatus.UNVERIFIED,
        verification_code="```python\ndef test_arithmetic():\n    assert 1 + 1 == 2\n```",
        description="Basic arithmetic law",
        source_path="/test/arith.law",
    )


@pytest.fixture
def failing_law() -> LawDefinition:
    """Law with failing verification code."""
    return LawDefinition(
        name="failing_law",
        equation="1 == 2",
        operations=("fail",),
        category="Impossible",
        status=LawStatus.FAILED,
        verification_code="```python\ndef test_fails():\n    assert 1 == 2, 'Math broke'\n```",
        source_path="/test/fail.law",
    )


# =============================================================================
# ID Generation Tests
# =============================================================================


class TestIdGeneration:
    """Tests for ID generation functions."""

    def test_generate_evidence_id(self):
        """Evidence IDs are properly formatted."""
        eid = generate_evidence_id("test_source")
        assert eid.startswith("evidence-")
        assert len(eid) > len("evidence-")

    def test_generate_evidence_id_unique(self):
        """Each call generates unique ID."""
        ids = {generate_evidence_id("same_source") for _ in range(10)}
        assert len(ids) == 10

    def test_generate_obligation_id(self):
        """Obligation IDs are properly formatted."""
        oid = generate_obligation_id("test_source")
        assert oid.startswith("obligation-")
        assert len(oid) > len("obligation-")


# =============================================================================
# FileOperadEvidence Tests
# =============================================================================


class TestFileOperadEvidence:
    """Tests for FileOperadEvidence dataclass."""

    def test_create_evidence(self):
        """Create basic evidence."""
        evidence = FileOperadEvidence(
            id=EvidenceId("evidence-001"),
            source=EvidenceSource.FILE_TRACE,
            evidence_type=EvidenceType.EXPLORATION,
            timestamp=datetime.now(),
            action="expand",
            target="/test/path.op",
        )

        assert evidence.id == "evidence-001"
        assert evidence.source == EvidenceSource.FILE_TRACE
        assert evidence.success is True

    def test_evidence_is_frozen(self):
        """Evidence is immutable."""
        evidence = FileOperadEvidence(
            id=EvidenceId("evidence-002"),
            source=EvidenceSource.FILE_TRACE,
            evidence_type=EvidenceType.EXPLORATION,
            timestamp=datetime.now(),
            action="expand",
            target="/test",
        )

        with pytest.raises(AttributeError):
            evidence.action = "modified"  # type: ignore

    def test_evidence_to_dict(self):
        """Serialization works."""
        evidence = FileOperadEvidence(
            id=EvidenceId("evidence-003"),
            source=EvidenceSource.SANDBOX,
            evidence_type=EvidenceType.EXECUTION,
            timestamp=datetime(2025, 12, 22, 10, 30),
            action="execute",
            target="/test",
            context=("hint1", "hint2"),
            success=False,
            error="Test error",
        )

        d = evidence.to_dict()

        assert d["id"] == "evidence-003"
        assert d["source"] == "SANDBOX"
        assert d["evidence_type"] == "EXECUTION"
        assert d["success"] is False
        assert d["error"] == "Test error"
        assert d["context"] == ["hint1", "hint2"]

    def test_evidence_from_dict(self):
        """Deserialization works."""
        data = {
            "id": "evidence-004",
            "source": "LAW",
            "evidence_type": "VERIFICATION",
            "timestamp": "2025-12-22T10:30:00",
            "action": "verify",
            "target": "/test/law.law",
            "context": ["ctx1"],
            "success": True,
        }

        evidence = FileOperadEvidence.from_dict(data)

        assert evidence.id == "evidence-004"
        assert evidence.source == EvidenceSource.LAW
        assert evidence.evidence_type == EvidenceType.VERIFICATION
        assert evidence.success is True


# =============================================================================
# FileTraceToEvidenceAdapter Tests
# =============================================================================


class TestFileTraceToEvidenceAdapter:
    """Tests for FileTraceToEvidenceAdapter."""

    def test_convert_single_trace(self, sample_trace):
        """Convert single trace to evidence."""
        adapter = FileTraceToEvidenceAdapter()
        evidence = adapter.convert(sample_trace)

        assert evidence.source == EvidenceSource.FILE_TRACE
        assert evidence.evidence_type == EvidenceType.EXPLORATION
        assert evidence.action == "expand"
        assert evidence.target == "/test/path.op"
        assert evidence.success is True
        assert "edge_type: enables" in evidence.context

    def test_convert_preserves_parent(self, sample_trace):
        """Parent path is included in context."""
        adapter = FileTraceToEvidenceAdapter()
        evidence = adapter.convert(sample_trace)

        assert any("parent:" in c for c in evidence.context)

    def test_convert_preserves_depth(self, sample_trace):
        """Depth is included in context."""
        adapter = FileTraceToEvidenceAdapter()
        evidence = adapter.convert(sample_trace)

        assert any("depth:" in c for c in evidence.context)

    def test_convert_many(self, sample_traces):
        """Convert multiple traces."""
        adapter = FileTraceToEvidenceAdapter()
        evidence_list = adapter.convert_many(sample_traces)

        assert len(evidence_list) == 5
        assert all(e.source == EvidenceSource.FILE_TRACE for e in evidence_list)

    def test_aggregate_session(self, sample_traces):
        """Aggregate session traces into single evidence."""
        adapter = FileTraceToEvidenceAdapter()
        evidence = adapter.aggregate_session(sample_traces, "session-002")

        assert evidence.action == "session_aggregate"
        assert evidence.target == "session-002"
        assert any("paths_explored:" in c for c in evidence.context)
        assert any("trace_count: 5" in c for c in evidence.context)

    def test_aggregate_empty_raises(self):
        """Aggregating empty list raises error."""
        adapter = FileTraceToEvidenceAdapter()

        with pytest.raises(ValueError, match="empty"):
            adapter.aggregate_session([], "session")


# =============================================================================
# SandboxToEvidenceAdapter Tests
# =============================================================================


class TestSandboxToEvidenceAdapter:
    """Tests for SandboxToEvidenceAdapter."""

    def test_convert_active_sandbox(self, sample_sandbox):
        """Convert active sandbox to evidence."""
        adapter = SandboxToEvidenceAdapter()
        evidence = adapter.convert(sample_sandbox)

        assert evidence.source == EvidenceSource.SANDBOX
        assert evidence.evidence_type == EvidenceType.EXECUTION
        assert "sandbox_active" in evidence.action
        assert evidence.success is True

    def test_convert_promoted_sandbox(self, sample_sandbox):
        """Convert promoted sandbox."""
        from ..sandbox import transition_sandbox, SandboxEvent

        promoted = transition_sandbox(sample_sandbox, SandboxEvent.PROMOTE, destination="/dest")

        adapter = SandboxToEvidenceAdapter()
        evidence = adapter.convert(promoted)

        assert "sandbox_promoted" in evidence.action
        assert evidence.success is True
        assert any("promoted_to:" in c for c in evidence.context)

    def test_convert_discarded_sandbox(self, sample_sandbox):
        """Convert discarded sandbox."""
        from ..sandbox import transition_sandbox, SandboxEvent

        discarded = transition_sandbox(sample_sandbox, SandboxEvent.DISCARD)

        adapter = SandboxToEvidenceAdapter()
        evidence = adapter.convert(discarded)

        assert "sandbox_discarded" in evidence.action
        assert evidence.success is False
        assert evidence.error is not None

    def test_convert_result(self, sample_sandbox):
        """Convert specific execution result."""
        result = SandboxResult(
            success=True,
            output="test output",
            execution_time_ms=42.0,
        )

        adapter = SandboxToEvidenceAdapter()
        evidence = adapter.convert_result(sample_sandbox, result, result_index=0)

        assert evidence.action == "execute"
        assert evidence.success is True
        assert any("execution_time_ms:" in c for c in evidence.context)


# =============================================================================
# ProofObligation Tests
# =============================================================================


class TestProofObligation:
    """Tests for ProofObligation dataclass."""

    def test_create_obligation(self):
        """Create basic proof obligation."""
        obl = ProofObligation(
            id=ObligationId("obligation-001"),
            law_name="test_law",
            property="x == x",
            source_location="/test/law.law",
        )

        assert obl.law_name == "test_law"
        assert obl.property == "x == x"

    def test_obligation_is_frozen(self):
        """Obligations are immutable."""
        obl = ProofObligation(
            id=ObligationId("obligation-002"),
            law_name="frozen_law",
            property="x",
            source_location="/test",
        )

        with pytest.raises(AttributeError):
            obl.law_name = "modified"  # type: ignore

    def test_obligation_to_dict(self):
        """Serialization works."""
        obl = ProofObligation(
            id=ObligationId("obligation-003"),
            law_name="serial_law",
            property="a >> b == b >> a",
            source_location="/test/law.law",
            context=("hint1", "hint2"),
            verification_code="def test(): pass",
            operations=("seq",),
            category="Composition",
        )

        d = obl.to_dict()

        assert d["law_name"] == "serial_law"
        assert d["property"] == "a >> b == b >> a"
        assert d["context"] == ["hint1", "hint2"]
        assert d["operations"] == ["seq"]

    def test_obligation_from_dict(self):
        """Deserialization works."""
        data = {
            "id": "obligation-004",
            "law_name": "restored_law",
            "property": "x == y",
            "source_location": "/test",
            "created_at": "2025-12-22T10:30:00",
            "context": ["ctx"],
        }

        obl = ProofObligation.from_dict(data)

        assert obl.law_name == "restored_law"
        assert obl.context == ("ctx",)


# =============================================================================
# LawProofCompiler Tests
# =============================================================================


class TestLawProofCompiler:
    """Tests for LawProofCompiler."""

    def test_compile_law(self, sample_law):
        """Compile single law to obligation."""
        compiler = LawProofCompiler()
        obl = compiler.compile(sample_law)

        assert obl.law_name == "test_law"
        assert obl.property == "f(x) == x"
        assert obl.category == "Identity"
        assert "f" in obl.operations
        assert obl.source_location == "/test/law.law"

    def test_compile_includes_context(self, sample_law):
        """Compiled obligation includes context hints."""
        compiler = LawProofCompiler()
        obl = compiler.compile(sample_law)

        # Should have category, operations, description, etc.
        assert any("category:" in c for c in obl.context)
        assert any("operations:" in c for c in obl.context)
        assert any("description:" in c for c in obl.context)

    def test_compile_includes_verification_code(self, sample_law):
        """Verification code is included."""
        compiler = LawProofCompiler()
        obl = compiler.compile(sample_law)

        assert "def test_law" in obl.verification_code

    def test_compile_many(self, sample_law):
        """Compile multiple laws."""
        laws = [sample_law, sample_law]
        compiler = LawProofCompiler()
        obligations = compiler.compile_many(laws)

        assert len(obligations) == 2

    def test_compile_unverified_only(self):
        """Only compile unverified/failed laws."""
        verified = LawDefinition(
            name="verified",
            equation="x",
            operations=(),
            category="",
            status=LawStatus.VERIFIED,
            verification_code="",
        )
        unverified = LawDefinition(
            name="unverified",
            equation="y",
            operations=(),
            category="",
            status=LawStatus.UNVERIFIED,
            verification_code="",
        )
        failed = LawDefinition(
            name="failed",
            equation="z",
            operations=(),
            category="",
            status=LawStatus.FAILED,
            verification_code="",
        )

        compiler = LawProofCompiler()
        obligations = compiler.compile_unverified([verified, unverified, failed])

        assert len(obligations) == 2
        names = {o.law_name for o in obligations}
        assert "verified" not in names
        assert "unverified" in names
        assert "failed" in names


# =============================================================================
# LawVerifier Tests
# =============================================================================


class TestLawVerifier:
    """Tests for LawVerifier."""

    def test_verify_passing_law(self, executable_law):
        """Verify law with passing test."""
        verifier = LawVerifier()
        result = verifier.verify(executable_law)

        assert result.result == VerificationResult.PASSED
        assert result.success is True
        assert "PASSED: test_arithmetic" in result.output

    def test_verify_failing_law(self, failing_law):
        """Verify law with failing test."""
        verifier = LawVerifier()
        result = verifier.verify(failing_law)

        assert result.result == VerificationResult.FAILED
        assert result.success is False
        assert result.error is not None
        assert "Math broke" in result.error

    def test_verify_no_code(self):
        """Verify law with no verification code."""
        no_code_law = LawDefinition(
            name="no_code",
            equation="x",
            operations=(),
            category="",
            status=LawStatus.UNVERIFIED,
            verification_code="",
        )

        verifier = LawVerifier()
        result = verifier.verify(no_code_law)

        assert result.result == VerificationResult.SKIPPED
        assert "No verification code" in result.output

    def test_verify_no_test_function(self):
        """Verify code without test function."""
        no_test_law = LawDefinition(
            name="no_test",
            equation="x",
            operations=(),
            category="",
            status=LawStatus.UNVERIFIED,
            verification_code="```python\nx = 1\n```",
        )

        verifier = LawVerifier()
        result = verifier.verify(no_test_law)

        assert result.result == VerificationResult.SKIPPED
        assert "No test functions" in result.output

    def test_verify_syntax_error(self):
        """Verify code with syntax error."""
        bad_syntax_law = LawDefinition(
            name="bad_syntax",
            equation="x",
            operations=(),
            category="",
            status=LawStatus.UNVERIFIED,
            verification_code="```python\ndef test_bad(\n```",
        )

        verifier = LawVerifier()
        result = verifier.verify(bad_syntax_law)

        assert result.result == VerificationResult.ERROR
        assert "SyntaxError" in (result.error or "")

    def test_verify_runtime_error(self):
        """Verify code with runtime error."""
        runtime_error_law = LawDefinition(
            name="runtime_error",
            equation="x",
            operations=(),
            category="",
            status=LawStatus.UNVERIFIED,
            verification_code="```python\ndef test_runtime():\n    raise ValueError('boom')\n```",
        )

        verifier = LawVerifier()
        result = verifier.verify(runtime_error_law)

        assert result.result == VerificationResult.ERROR
        assert "ValueError" in (result.error or "")

    def test_verify_many(self, executable_law, failing_law):
        """Verify multiple laws."""
        verifier = LawVerifier()
        results = verifier.verify_many([executable_law, failing_law])

        assert len(results) == 2
        passed = sum(1 for r in results if r.result == VerificationResult.PASSED)
        failed = sum(1 for r in results if r.result == VerificationResult.FAILED)
        assert passed == 1
        assert failed == 1

    def test_result_to_evidence(self, executable_law):
        """Convert verification result to evidence."""
        verifier = LawVerifier()
        result = verifier.verify(executable_law)
        evidence = result.to_evidence()

        assert isinstance(evidence, LawVerificationEvidence)
        assert evidence.source == EvidenceSource.LAW
        assert evidence.evidence_type == EvidenceType.VERIFICATION
        assert evidence.law_name == "executable_law"
        assert evidence.verification_result == VerificationResult.PASSED

    def test_verify_duration_measured(self, executable_law):
        """Verification duration is measured."""
        verifier = LawVerifier()
        result = verifier.verify(executable_law)

        assert result.duration_ms > 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestASHCBridgeIntegration:
    """Integration tests for the full ASHC bridge pipeline."""

    def test_trace_to_evidence_to_dict(self, sample_trace):
        """Full pipeline: trace -> evidence -> dict."""
        adapter = FileTraceToEvidenceAdapter()
        evidence = adapter.convert(sample_trace)
        d = evidence.to_dict()

        # Roundtrip
        restored = FileOperadEvidence.from_dict(d)
        assert restored.target == evidence.target
        assert restored.action == evidence.action

    def test_law_to_obligation_to_dict(self, sample_law):
        """Full pipeline: law -> obligation -> dict."""
        compiler = LawProofCompiler()
        obligation = compiler.compile(sample_law)
        d = obligation.to_dict()

        # Roundtrip
        restored = ProofObligation.from_dict(d)
        assert restored.law_name == obligation.law_name
        assert restored.property == obligation.property

    def test_verify_and_generate_evidence(self, executable_law):
        """Full pipeline: verify -> result -> evidence."""
        verifier = LawVerifier()
        result = verifier.verify(executable_law)
        evidence = result.to_evidence()

        assert evidence.success is True
        assert evidence.law_equation == "1 + 1 == 2"


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_trace_without_optional_fields(self):
        """Trace with only required fields."""
        trace = FileWiringTrace(
            path="/test",
            operation="read",
            timestamp=datetime.now(),
            actor="system",
        )

        adapter = FileTraceToEvidenceAdapter()
        evidence = adapter.convert(trace)

        assert evidence.target == "/test"
        assert evidence.related_ids == ()

    def test_law_without_optional_fields(self):
        """Law with only required fields."""
        law = LawDefinition(
            name="minimal",
            equation="x",
            operations=(),
            category="",
            status=LawStatus.UNVERIFIED,
            verification_code="",
        )

        compiler = LawProofCompiler()
        obl = compiler.compile(law)

        assert obl.law_name == "minimal"
        assert obl.source_location == "<law:minimal>"

    def test_unicode_in_evidence(self):
        """Unicode content is handled."""
        evidence = FileOperadEvidence(
            id=EvidenceId("evidence-unicode"),
            source=EvidenceSource.FILE_TRACE,
            evidence_type=EvidenceType.EXPLORATION,
            timestamp=datetime.now(),
            action="探索",
            target="/测试/路径.op",
            context=("测试上下文",),
        )

        d = evidence.to_dict()
        restored = FileOperadEvidence.from_dict(d)

        assert restored.action == "探索"
        assert "测试" in restored.target
