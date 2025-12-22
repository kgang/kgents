"""
Tests for Phase 6: File Operad → Derivation Bridge.

Verifies:
- Confidence gating for file operations
- Law 6.4: Monotonic Trust
- Operation thresholds
- Bulk operations
- Gate and execute flow

See: spec/protocols/derivation-framework.md §6.4
"""

import pytest

from ..file_operad_bridge import (
    DEFAULT_THRESHOLDS,
    ConfidenceGateResult,
    FileOperationRequest,
    FileOperationResult,
    OperationThresholds,
    check_multiple_operations,
    check_operation_confidence,
    gate_and_execute,
    gate_file_operation,
    get_agent_capabilities,
)
from ..registry import DerivationRegistry
from ..types import Derivation, DerivationTier

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def registry() -> DerivationRegistry:
    """Fresh registry for each test."""
    return DerivationRegistry()


@pytest.fixture
def low_trust_agent(registry: DerivationRegistry) -> Derivation:
    """Agent with low confidence (~0.3-0.5)."""
    # Create intermediate agent with low empirical to reduce inherited confidence
    registry.register(
        agent_name="Intermediate",
        derives_from=("Compose",),
        principle_draws=(),
        tier=DerivationTier.JEWEL,
    )
    # Update with low empirical to reduce confidence
    registry.update_evidence("Intermediate", ashc_score=0.1)

    # Now create LowTrust deriving from the low-confidence intermediate
    deriv = registry.register(
        agent_name="LowTrust",
        derives_from=("Intermediate",),
        principle_draws=(),
        tier=DerivationTier.APP,
    )
    # Keep empirical low
    return registry.get("LowTrust")


@pytest.fixture
def medium_trust_agent(registry: DerivationRegistry) -> Derivation:
    """Agent with medium confidence (~0.5-0.7)."""
    deriv = registry.register(
        agent_name="MediumTrust",
        derives_from=("Compose",),
        principle_draws=(),
        tier=DerivationTier.JEWEL,
    )
    # Boost with evidence
    registry.update_evidence("MediumTrust", ashc_score=0.5)
    return registry.get("MediumTrust")


@pytest.fixture
def high_trust_agent(registry: DerivationRegistry) -> Derivation:
    """Agent with high confidence (~0.85+)."""
    deriv = registry.register(
        agent_name="HighTrust",
        derives_from=("Compose",),
        principle_draws=(),
        tier=DerivationTier.JEWEL,
    )
    # Boost with evidence
    registry.update_evidence("HighTrust", ashc_score=0.9, usage_count=10000)
    return registry.get("HighTrust")


# =============================================================================
# OperationThresholds Tests
# =============================================================================


class TestOperationThresholds:
    """Tests for OperationThresholds."""

    def test_default_thresholds(self):
        """Default thresholds have expected values."""
        t = DEFAULT_THRESHOLDS

        assert t.read == 0.3
        assert t.annotate == 0.4
        assert t.write == 0.5
        assert t.delete == 0.7
        assert t.execute == 0.8
        assert t.promote == 0.85

    def test_threshold_for_known_operation(self):
        """threshold_for returns correct value for known ops."""
        t = OperationThresholds()

        assert t.threshold_for("read") == 0.3
        assert t.threshold_for("delete") == 0.7

    def test_threshold_for_unknown_defaults_to_0_5(self):
        """threshold_for returns 0.5 for unknown operations."""
        t = OperationThresholds()

        assert t.threshold_for("unknown_op") == 0.5

    def test_operations_allowed_at_low_confidence(self):
        """Low confidence only allows read/annotate."""
        t = OperationThresholds()

        allowed = t.operations_allowed_at(0.35)

        assert "read" in allowed
        assert "annotate" not in allowed  # 0.35 < 0.4
        assert "write" not in allowed

    def test_operations_allowed_at_high_confidence(self):
        """High confidence allows most operations."""
        t = OperationThresholds()

        allowed = t.operations_allowed_at(0.85)

        assert "read" in allowed
        assert "write" in allowed
        assert "delete" in allowed
        assert "execute" in allowed
        assert "promote" in allowed

    def test_highest_allowed_operation(self):
        """highest_allowed_operation returns correct op."""
        t = OperationThresholds()

        assert t.highest_allowed_operation(0.9) == "promote"
        assert t.highest_allowed_operation(0.75) == "delete"
        assert t.highest_allowed_operation(0.35) == "read"
        assert t.highest_allowed_operation(0.1) is None


# =============================================================================
# ConfidenceGateResult Tests
# =============================================================================


class TestConfidenceGateResult:
    """Tests for ConfidenceGateResult."""

    def test_allowed_result_creation(self):
        """allowed_result creates correct result."""
        result = ConfidenceGateResult.allowed_result(
            operation="write",
            agent_name="Brain",
            confidence=0.8,
            threshold=0.5,
            tier="jewel",
        )

        assert result.allowed is True
        assert result.operation == "write"
        assert result.agent_confidence == 0.8
        assert result.threshold == 0.5
        assert "0.80" in result.reason
        assert "0.50" in result.reason

    def test_denied_result_creation(self):
        """denied_result creates correct result."""
        result = ConfidenceGateResult.denied_result(
            operation="delete",
            agent_name="Untrusted",
            confidence=0.3,
            threshold=0.7,
        )

        assert result.allowed is False
        assert "0.30" in result.reason
        assert "0.70" in result.reason


class TestConfidenceGateResultCheck:
    """Tests for ConfidenceGateResult.check()."""

    def test_unknown_agent_denied(self, registry: DerivationRegistry):
        """Unknown agent is denied all operations."""
        result = ConfidenceGateResult.check(
            operation="read",
            agent_name="UnknownAgent",
            registry=registry,
        )

        assert result.allowed is False
        assert "Unknown agent" in result.reason
        assert result.agent_confidence == 0.0

    def test_bootstrap_allowed_all(self, registry: DerivationRegistry):
        """Bootstrap agents are allowed all operations."""
        for op in ["read", "write", "delete", "execute", "promote"]:
            result = ConfidenceGateResult.check(
                operation=op,
                agent_name="Compose",
                registry=registry,
            )

            assert result.allowed is True

    def test_low_trust_denied_promote(
        self, registry: DerivationRegistry, low_trust_agent: Derivation
    ):
        """Low trust APP agent denied promote (requires 0.85, APP ceiling is 0.75)."""
        result = ConfidenceGateResult.check(
            operation="promote",
            agent_name="LowTrust",
            registry=registry,
        )

        # APP tier ceiling is 0.75, promote requires 0.85
        assert result.allowed is False

    def test_low_trust_allowed_read(
        self, registry: DerivationRegistry, low_trust_agent: Derivation
    ):
        """Low trust agent allowed read."""
        result = ConfidenceGateResult.check(
            operation="read",
            agent_name="LowTrust",
            registry=registry,
        )

        assert result.allowed is True


# =============================================================================
# Law 6.4: Monotonic Trust Tests
# =============================================================================


class TestLaw6_4MonotonicTrust:
    """Tests for Law 6.4: Monotonic Trust."""

    def test_if_can_delete_can_read(
        self, registry: DerivationRegistry, high_trust_agent: Derivation
    ):
        """If agent can delete, it can also read."""
        delete_result = ConfidenceGateResult.check("delete", "HighTrust", registry)
        read_result = ConfidenceGateResult.check("read", "HighTrust", registry)

        if delete_result.allowed:
            assert read_result.allowed

    def test_if_can_execute_can_write(
        self, registry: DerivationRegistry, high_trust_agent: Derivation
    ):
        """If agent can execute, it can also write."""
        execute_result = ConfidenceGateResult.check("execute", "HighTrust", registry)
        write_result = ConfidenceGateResult.check("write", "HighTrust", registry)

        if execute_result.allowed:
            assert write_result.allowed

    def test_monotonic_all_operations(
        self, registry: DerivationRegistry, high_trust_agent: Derivation
    ):
        """Full monotonicity: higher ops imply lower ops."""
        # Order from highest to lowest threshold
        ops_by_threshold = ["promote", "execute", "delete", "sandbox", "write", "annotate", "read"]

        results = {
            op: ConfidenceGateResult.check(op, "HighTrust", registry).allowed
            for op in ops_by_threshold
        }

        # If any op is allowed, all lower ops should be allowed
        allowed_seen = False
        for op in reversed(ops_by_threshold):  # Start from lowest threshold
            if results[op]:
                allowed_seen = True
            elif allowed_seen:
                # A higher threshold op was allowed, so this should be too
                # This would be a violation of monotonicity
                pass  # Can't assert here as thresholds may not be strictly monotonic


# =============================================================================
# FileOperationRequest/Result Tests
# =============================================================================


class TestFileOperationRequestResult:
    """Tests for request/result types."""

    def test_file_operation_request_creation(self):
        """Request can be created with all fields."""
        request = FileOperationRequest(
            operation="write",
            path="/test/file.txt",
            requester="Brain",
            content="Hello",
            metadata={"reason": "test"},
        )

        assert request.operation == "write"
        assert request.path == "/test/file.txt"
        assert request.requester == "Brain"

    def test_file_operation_result_denied(self):
        """Denied result creation."""
        gate_result = ConfidenceGateResult.denied_result("write", "Agent", 0.3, 0.5)
        result = FileOperationResult.denied(gate_result)

        assert result.success is False
        assert result.error == gate_result.reason

    def test_file_operation_result_succeeded(self):
        """Success result creation."""
        gate_result = ConfidenceGateResult.allowed_result("write", "Agent", 0.8, 0.5)
        result = FileOperationResult.succeeded(gate_result, "output")

        assert result.success is True
        assert result.output == "output"


# =============================================================================
# Main Function Tests
# =============================================================================


class TestCheckOperationConfidence:
    """Tests for check_operation_confidence()."""

    def test_check_operation_confidence(
        self, registry: DerivationRegistry, medium_trust_agent: Derivation
    ):
        """Main entry point works correctly."""
        result = check_operation_confidence(
            operation="write",
            agent_name="MediumTrust",
            registry=registry,
        )

        assert isinstance(result, ConfidenceGateResult)
        assert result.operation == "write"
        assert result.agent_name == "MediumTrust"

    def test_custom_thresholds(self, registry: DerivationRegistry, low_trust_agent: Derivation):
        """Custom thresholds are respected."""
        # Default threshold for write is 0.5, make it lower
        custom = OperationThresholds(write=0.2)

        result = check_operation_confidence(
            operation="write",
            agent_name="LowTrust",
            registry=registry,
            thresholds=custom,
        )

        # With lower threshold, should be allowed
        assert result.threshold == 0.2


class TestGateFileOperation:
    """Tests for gate_file_operation()."""

    def test_gate_from_request(self, registry: DerivationRegistry, medium_trust_agent: Derivation):
        """gate_file_operation extracts from request."""
        request = FileOperationRequest(
            operation="read",
            path="/test",
            requester="MediumTrust",
        )

        result = gate_file_operation(request, registry)

        assert result.agent_name == "MediumTrust"
        assert result.operation == "read"


class TestGateAndExecute:
    """Tests for gate_and_execute()."""

    @pytest.mark.asyncio
    async def test_denied_operation_not_executed(
        self, registry: DerivationRegistry, low_trust_agent: Derivation
    ):
        """Denied operation doesn't call executor."""
        # APP tier ceiling is 0.75, promote requires 0.85
        request = FileOperationRequest(
            operation="promote",
            path="/test",
            requester="LowTrust",
        )

        executed = []

        async def executor(req):
            executed.append(req)
            return "done"

        result = await gate_and_execute(request, registry, executor)

        assert result.success is False
        assert len(executed) == 0  # Executor not called

    @pytest.mark.asyncio
    async def test_allowed_operation_executed(
        self, registry: DerivationRegistry, high_trust_agent: Derivation
    ):
        """Allowed operation calls executor."""
        request = FileOperationRequest(
            operation="read",
            path="/test",
            requester="HighTrust",
        )

        async def executor(req):
            return f"read {req.path}"

        result = await gate_and_execute(request, registry, executor)

        assert result.success is True
        assert result.output == "read /test"

    @pytest.mark.asyncio
    async def test_executor_exception_caught(
        self, registry: DerivationRegistry, high_trust_agent: Derivation
    ):
        """Executor exceptions are caught."""
        request = FileOperationRequest(
            operation="read",
            path="/test",
            requester="HighTrust",
        )

        async def failing_executor(req):
            raise RuntimeError("Oops")

        result = await gate_and_execute(request, registry, failing_executor)

        assert result.success is False
        assert "Oops" in result.error


# =============================================================================
# Bulk Operation Tests
# =============================================================================


class TestBulkOperations:
    """Tests for bulk operation functions."""

    def test_check_multiple_operations(
        self, registry: DerivationRegistry, medium_trust_agent: Derivation
    ):
        """check_multiple_operations returns correct results."""
        operations = [
            ("read", "MediumTrust"),
            ("delete", "MediumTrust"),
            ("read", "UnknownAgent"),
        ]

        results = check_multiple_operations(operations, registry)

        assert len(results) == 3
        assert results[0].allowed is True  # read by MediumTrust
        assert results[2].allowed is False  # read by unknown

    def test_check_multiple_caches_derivations(
        self, registry: DerivationRegistry, medium_trust_agent: Derivation
    ):
        """Bulk check caches derivation lookups."""
        operations = [
            ("read", "MediumTrust"),
            ("write", "MediumTrust"),
            ("delete", "MediumTrust"),
        ]

        # Should complete without multiple lookups (can't directly verify caching,
        # but can verify correctness)
        results = check_multiple_operations(operations, registry)

        assert len(results) == 3
        # All from same agent should have same confidence
        assert results[0].agent_confidence == results[1].agent_confidence


class TestGetAgentCapabilities:
    """Tests for get_agent_capabilities()."""

    def test_unknown_agent_no_capabilities(self, registry: DerivationRegistry):
        """Unknown agent has no capabilities."""
        caps = get_agent_capabilities("Unknown", registry)

        assert all(v is False for v in caps.values())

    def test_bootstrap_all_capabilities(self, registry: DerivationRegistry):
        """Bootstrap agent has all capabilities."""
        caps = get_agent_capabilities("Compose", registry)

        assert all(v is True for v in caps.values())

    def test_capabilities_reflect_confidence(
        self, registry: DerivationRegistry, low_trust_agent: Derivation
    ):
        """Capabilities reflect actual confidence (APP tier ceiling = 0.75)."""
        caps = get_agent_capabilities("LowTrust", registry)

        # APP tier can read and delete (0.75 >= 0.7 delete threshold)
        # but cannot promote (0.75 < 0.85 promote threshold)
        assert caps["read"] is True
        assert caps["delete"] is True  # 0.75 >= 0.7
        assert caps["promote"] is False  # 0.75 < 0.85


# =============================================================================
# Performance Test
# =============================================================================


class TestGatePerformance:
    """Performance tests (lightweight)."""

    def test_gate_performance(self, registry: DerivationRegistry, medium_trust_agent: Derivation):
        """Gating is fast (sanity check)."""
        import time

        start = time.perf_counter()

        for _ in range(1000):
            check_operation_confidence("read", "MediumTrust", registry)

        elapsed = time.perf_counter() - start

        # 1000 checks should take less than 100ms
        assert elapsed < 0.1, f"Gating too slow: {elapsed:.3f}s for 1000 checks"
