"""
Tests for Compression Economy (Semantic Zipper)

Phase 1 of Structural Economics (B-gent × G-gent Integration).

Tests cover:
1. CommunicationTracker: Log and track inter-agent communication
2. CompressionROICalculator: Calculate ROI for pidgin synthesis
3. CompressionEconomyMonitor: End-to-end monitoring and pidgin commissioning
4. SemanticZipperBudget: Budget evaluation with natural language tax
"""

from datetime import datetime, timedelta

import pytest
from agents.b.compression_economy import (
    # Types
    AdoptionStatus,
    BudgetDecision,
    CommunicationLog,
    # Classes
    CommunicationTracker,
    CompressionEconomyMonitor,
    CompressionROI,
    CompressionROICalculator,
    PidginAvailable,
    PidginMetadata,
    SemanticZipperBudget,
    analyze_compression_opportunity,
    # Convenience functions
    create_compression_monitor,
    create_zipper_budget,
)
from agents.b.metered_functor import CentralBank, Gas

# =============================================================================
# CommunicationLog Tests
# =============================================================================


class TestCommunicationLog:
    """Tests for CommunicationLog dataclass."""

    def test_create_log(self):
        """Test basic log creation."""
        log = CommunicationLog(
            sender="agent_a",
            receiver="agent_b",
            message="Hello world",
            tokens=10,
        )
        assert log.sender == "agent_a"
        assert log.receiver == "agent_b"
        assert log.message == "Hello world"
        assert log.tokens == 10
        assert log.domain is None
        assert log.using_pidgin is None

    def test_agent_pair_canonical(self):
        """Test that agent_pair is canonically sorted."""
        log1 = CommunicationLog(
            sender="agent_b",
            receiver="agent_a",
            message="Test",
            tokens=5,
        )
        log2 = CommunicationLog(
            sender="agent_a",
            receiver="agent_b",
            message="Test",
            tokens=5,
        )
        assert log1.agent_pair == log2.agent_pair
        assert log1.agent_pair == ("agent_a", "agent_b")

    def test_log_with_domain(self):
        """Test log with domain metadata."""
        log = CommunicationLog(
            sender="researcher",
            receiver="assistant",
            message="ref(Smith20,transformers)",
            tokens=3,
            domain="citations",
            using_pidgin="CitationPidgin",
        )
        assert log.domain == "citations"
        assert log.using_pidgin == "CitationPidgin"


# =============================================================================
# CompressionROI Tests
# =============================================================================


class TestCompressionROI:
    """Tests for CompressionROI dataclass."""

    def test_create_roi(self):
        """Test ROI creation."""
        roi = CompressionROI(
            current_cost_tokens=10000,
            message_count=100,
            avg_tokens_per_message=100.0,
            estimated_compression_ratio=0.2,
            estimated_compressed_tokens=2000,
            synthesis_cost=Gas(tokens=10000),
            projected_30day_messages=3000,
            projected_30day_savings=240000,
            roi=23.0,
            recommended=True,
            regularity_score=0.7,
        )
        assert roi.recommended
        assert roi.roi == 23.0

    def test_roi_to_dict(self):
        """Test ROI serialization."""
        roi = CompressionROI(
            current_cost_tokens=5000,
            message_count=50,
            avg_tokens_per_message=100.0,
            estimated_compression_ratio=0.3,
            estimated_compressed_tokens=1500,
            synthesis_cost=Gas(tokens=10000, time_ms=30000),
            projected_30day_messages=1500,
            projected_30day_savings=105000,
            roi=9.5,
            recommended=True,
            regularity_score=0.6,
        )
        d = roi.to_dict()
        assert d["current_cost_tokens"] == 5000
        assert d["message_count"] == 50
        assert d["synthesis_cost_tokens"] == 10000
        assert d["recommended"] is True


# =============================================================================
# PidginMetadata Tests
# =============================================================================


class TestPidginMetadata:
    """Tests for PidginMetadata dataclass."""

    def test_create_pidgin(self):
        """Test pidgin metadata creation."""
        pidgin = PidginMetadata(
            name="CitationPidgin",
            agent_a="researcher",
            agent_b="assistant",
        )
        assert pidgin.name == "CitationPidgin"
        assert pidgin.status == AdoptionStatus.PROPOSED
        assert pidgin.is_active

    def test_agent_pair_canonical(self):
        """Test canonical agent pair."""
        pidgin = PidginMetadata(
            name="TestPidgin",
            agent_a="zeta",
            agent_b="alpha",
        )
        assert pidgin.agent_pair == ("alpha", "zeta")

    def test_update_adoption_rate(self):
        """Test adoption rate calculation."""
        pidgin = PidginMetadata(
            name="TestPidgin",
            agent_a="a",
            agent_b="b",
            status=AdoptionStatus.PARTIAL,  # Start at PARTIAL for ADOPTED transition
            messages_using_pidgin=80,
            messages_using_natural_language=20,
        )
        pidgin.update_adoption_rate()
        assert pidgin.adoption_rate == 0.8
        assert pidgin.status == AdoptionStatus.ADOPTED

    def test_adoption_progression(self):
        """Test adoption status progression."""
        pidgin = PidginMetadata(
            name="TestPidgin",
            agent_a="a",
            agent_b="b",
            status=AdoptionStatus.PROPOSED,
        )

        # First use
        pidgin.messages_using_pidgin = 1
        pidgin.messages_using_natural_language = 9
        pidgin.update_adoption_rate()
        assert pidgin.status == AdoptionStatus.PARTIAL
        assert pidgin.adoption_rate == 0.1

        # More adoption
        pidgin.messages_using_pidgin = 85
        pidgin.messages_using_natural_language = 15
        pidgin.update_adoption_rate()
        assert pidgin.status == AdoptionStatus.ADOPTED
        assert pidgin.adoption_rate == 0.85

    def test_is_active_status(self):
        """Test is_active property for various statuses."""
        for status in [
            AdoptionStatus.PROPOSED,
            AdoptionStatus.PARTIAL,
            AdoptionStatus.ADOPTED,
            AdoptionStatus.MANDATORY,
        ]:
            pidgin = PidginMetadata(name="Test", status=status)
            assert pidgin.is_active

        pidgin = PidginMetadata(name="Test", status=AdoptionStatus.DEPRECATED)
        assert not pidgin.is_active


# =============================================================================
# CommunicationTracker Tests
# =============================================================================


class TestCommunicationTracker:
    """Tests for CommunicationTracker class."""

    def test_log_communication(self):
        """Test logging a communication."""
        tracker = CommunicationTracker()
        log = tracker.log_communication(
            sender="a",
            receiver="b",
            message="Hello",
            tokens=10,
        )
        assert log.sender == "a"
        assert log.receiver == "b"

    def test_get_logs(self):
        """Test retrieving logs for an agent pair."""
        tracker = CommunicationTracker()
        tracker.log_communication("a", "b", "Hello", 10)
        tracker.log_communication("b", "a", "Hi", 5)
        tracker.log_communication("c", "d", "Other", 8)

        logs = tracker.get_logs("a", "b")
        assert len(logs) == 2

        logs = tracker.get_logs("b", "a")  # Order shouldn't matter
        assert len(logs) == 2

        logs = tracker.get_logs("c", "d")
        assert len(logs) == 1

    def test_get_all_pairs(self):
        """Test getting all agent pairs."""
        tracker = CommunicationTracker()
        tracker.log_communication("a", "b", "Hello", 10)
        tracker.log_communication("c", "d", "World", 10)

        pairs = tracker.get_all_pairs()
        assert len(pairs) == 2
        assert ("a", "b") in pairs
        assert ("c", "d") in pairs

    def test_prune_old_logs(self):
        """Test pruning old logs."""
        tracker = CommunicationTracker(window_days=7)

        # Add old log
        old_log = CommunicationLog(
            sender="a",
            receiver="b",
            message="Old",
            tokens=10,
            timestamp=datetime.now() - timedelta(days=10),
        )
        tracker.logs[("a", "b")] = [old_log]

        # Add recent log
        tracker.log_communication("c", "d", "Recent", 10)

        removed = tracker.prune_old_logs()
        assert removed == 1
        assert ("a", "b") not in tracker.logs
        assert ("c", "d") in tracker.logs

    def test_get_statistics(self):
        """Test statistics calculation."""
        tracker = CommunicationTracker()
        tracker.log_communication("a", "b", "Hello", 10)
        tracker.log_communication("a", "b", "World", 20)
        tracker.log_communication("a", "b", "!", 5, using_pidgin="TestPidgin")

        stats = tracker.get_statistics("a", "b")
        assert stats["message_count"] == 3
        assert stats["total_tokens"] == 35
        assert stats["avg_tokens_per_message"] == 35 / 3
        assert stats["using_pidgin_count"] == 1
        assert stats["using_natural_language_count"] == 2


# =============================================================================
# CompressionROICalculator Tests
# =============================================================================


class TestCompressionROICalculator:
    """Tests for CompressionROICalculator class."""

    def test_empty_logs(self):
        """Test ROI calculation with no logs."""
        calc = CompressionROICalculator()
        roi = calc.calculate_roi([])
        assert roi.message_count == 0
        assert roi.recommended is False

    def test_basic_roi_calculation(self):
        """Test basic ROI calculation."""
        calc = CompressionROICalculator(
            synthesis_cost_tokens=10000,
            roi_threshold=2.0,
            min_message_count=5,
        )

        # Create logs with high regularity
        logs = [
            CommunicationLog(
                sender="a",
                receiver="b",
                message=f"QUERY {i} FROM database",
                tokens=100,
                domain="queries",
            )
            for i in range(20)
        ]

        roi = calc.calculate_roi(logs)
        assert roi.message_count == 20
        assert roi.avg_tokens_per_message == 100.0
        assert roi.estimated_compression_ratio > 0
        assert roi.estimated_compression_ratio < 1.0

    def test_regularity_detection(self):
        """Test message regularity detection."""
        calc = CompressionROICalculator()

        # High regularity - repeated patterns
        high_reg_logs = [
            CommunicationLog(
                sender="a",
                receiver="b",
                message=f"GET resource_{i}",
                tokens=10,
                domain="api",
            )
            for i in range(10)
        ]

        # Low regularity - varied content
        low_reg_logs = [
            CommunicationLog(
                sender="a",
                receiver="b",
                message=f"Message {chr(65 + i)}" * (i + 1),
                tokens=20,
            )
            for i in range(10)
        ]

        high_roi = calc.calculate_roi(high_reg_logs)
        low_roi = calc.calculate_roi(low_reg_logs)

        assert high_roi.regularity_score > low_roi.regularity_score

    def test_recommendation_threshold(self):
        """Test that recommendation respects threshold."""
        calc = CompressionROICalculator(
            synthesis_cost_tokens=10000,
            roi_threshold=2.0,
            min_message_count=5,
        )

        # Few messages - should not recommend
        few_logs = [
            CommunicationLog(
                sender="a",
                receiver="b",
                message="Test message",
                tokens=1000,
            )
            for _ in range(3)
        ]

        roi = calc.calculate_roi(few_logs)
        assert not roi.recommended  # Below min_message_count

    def test_projection_days(self):
        """Test different projection periods."""
        calc = CompressionROICalculator()

        logs = [
            CommunicationLog(
                sender="a",
                receiver="b",
                message="Test",
                tokens=100,
            )
            for _ in range(10)
        ]

        roi_30 = calc.calculate_roi(logs, projection_days=30)
        roi_60 = calc.calculate_roi(logs, projection_days=60)

        assert roi_60.projected_30day_messages > roi_30.projected_30day_messages


# =============================================================================
# CompressionEconomyMonitor Tests
# =============================================================================


class TestCompressionEconomyMonitor:
    """Tests for CompressionEconomyMonitor class."""

    @pytest.fixture
    def bank(self):
        """Create a CentralBank for testing."""
        return CentralBank(max_balance=100000)

    @pytest.fixture
    def monitor(self, bank):
        """Create a CompressionEconomyMonitor for testing."""
        return CompressionEconomyMonitor(
            bank=bank,
            grammarian=None,
            registry=None,
            roi_threshold=2.0,
        )

    def test_log_communication(self, monitor):
        """Test logging communication through monitor."""
        log = monitor.log_communication(
            sender="a",
            receiver="b",
            message="Hello",
            tokens=10,
            domain="test",
        )
        assert log.sender == "a"
        assert log.tokens == 10

    @pytest.mark.asyncio
    async def test_analyze_pair(self, monitor):
        """Test analyzing a single pair."""
        # Log some communications
        for i in range(15):
            monitor.log_communication(
                sender="a",
                receiver="b",
                message=f"Query item_{i}",
                tokens=50,
                domain="queries",
            )

        roi = await monitor.analyze_pair("a", "b")
        assert roi.message_count == 15
        assert roi.avg_tokens_per_message == 50.0

    @pytest.mark.asyncio
    async def test_check_all_pairs(self, monitor):
        """Test checking all pairs for opportunities."""
        # Create high-traffic pair
        for i in range(20):
            monitor.log_communication(
                sender="a",
                receiver="b",
                message=f"GET resource_{i}",
                tokens=100,
                domain="api",
            )

        # Create low-traffic pair
        for i in range(3):
            monitor.log_communication(
                sender="c",
                receiver="d",
                message=f"Hello {i}",
                tokens=10,
            )

        opportunities = await monitor.check_all_pairs()
        # High traffic pair may be recommended
        # At least some opportunities should be returned (if ROI is positive)
        _ = opportunities  # Verify it returns without error

    def test_get_pidgin(self, monitor):
        """Test retrieving pidgin for pair."""
        # No pidgin initially
        assert monitor.get_pidgin("a", "b") is None

        # Add pidgin manually
        pidgin = PidginMetadata(
            name="TestPidgin",
            agent_a="a",
            agent_b="b",
        )
        monitor.pidgins[("a", "b")] = pidgin

        # Should find it
        found = monitor.get_pidgin("a", "b")
        assert found is not None
        assert found.name == "TestPidgin"

        # Should find with reversed order
        found = monitor.get_pidgin("b", "a")
        assert found is not None

    def test_callback_registration(self, monitor):
        """Test pidgin availability callback."""
        received = []

        def callback(notification, agent_a, agent_b):
            received.append((notification, agent_a, agent_b))

        monitor.on_pidgin_available(callback)

        # Simulate pidgin becoming available
        notification = PidginAvailable(
            pidgin_name="TestPidgin",
            tongue_id=None,
            mandatory=False,
        )
        for cb in monitor._on_pidgin_available:
            cb(notification, "a", "b")

        assert len(received) == 1
        assert received[0][0].pidgin_name == "TestPidgin"

    def test_get_statistics(self, monitor):
        """Test getting overall statistics."""
        # Add some communications
        monitor.log_communication("a", "b", "Test", 10)

        # Add a pidgin
        pidgin = PidginMetadata(
            name="TestPidgin",
            agent_a="a",
            agent_b="b",
            synthesis_cost=Gas(tokens=10000),
            actual_savings_to_date=50000,
        )
        monitor.pidgins[("a", "b")] = pidgin

        stats = monitor.get_statistics()
        assert stats["total_agent_pairs"] == 1
        assert stats["active_pidgins"] == 1
        assert stats["total_savings_tokens"] == 50000
        assert stats["net_savings_tokens"] == 40000  # 50k - 10k


# =============================================================================
# SemanticZipperBudget Tests
# =============================================================================


class TestSemanticZipperBudget:
    """Tests for SemanticZipperBudget class."""

    @pytest.fixture
    def bank(self):
        """Create a CentralBank for testing."""
        return CentralBank(max_balance=100000)

    @pytest.fixture
    def monitor(self, bank):
        """Create a monitor for testing."""
        return CompressionEconomyMonitor(bank=bank)

    @pytest.fixture
    def budget(self, bank, monitor):
        """Create a SemanticZipperBudget for testing."""
        return SemanticZipperBudget(
            bank=bank,
            compression_monitor=monitor,
            tax_rate=0.20,
        )

    def test_evaluate_no_pidgin(self, budget):
        """Test evaluation when no pidgin exists."""
        cost = Gas(tokens=1000)
        decision = budget.evaluate_communication(
            sender="a",
            receiver="b",
            cost=cost,
            using_pidgin=False,
        )
        assert decision.approved
        assert decision.actual_cost.tokens == 1000
        assert decision.natural_language_tax is None

    def test_evaluate_with_pidgin_using_natural_language(self, budget, monitor):
        """Test evaluation with pidgin available but not using it."""
        # Add pidgin
        pidgin = PidginMetadata(
            name="TestPidgin",
            agent_a="a",
            agent_b="b",
            status=AdoptionStatus.ADOPTED,
        )
        monitor.pidgins[("a", "b")] = pidgin

        cost = Gas(tokens=1000)
        decision = budget.evaluate_communication(
            sender="a",
            receiver="b",
            cost=cost,
            using_pidgin=False,
        )

        assert decision.approved
        assert decision.actual_cost.tokens == 1200  # 1000 + 20% tax
        assert decision.natural_language_tax is not None
        assert decision.natural_language_tax.tokens == 200
        assert "TestPidgin" in decision.recommendation

    def test_evaluate_with_pidgin_using_pidgin(self, budget, monitor):
        """Test evaluation when using available pidgin."""
        # Add pidgin
        pidgin = PidginMetadata(
            name="TestPidgin",
            agent_a="a",
            agent_b="b",
            status=AdoptionStatus.ADOPTED,
        )
        monitor.pidgins[("a", "b")] = pidgin

        cost = Gas(tokens=1000)
        decision = budget.evaluate_communication(
            sender="a",
            receiver="b",
            cost=cost,
            using_pidgin=True,
        )

        assert decision.approved
        assert decision.actual_cost.tokens == 1000  # No tax
        assert decision.natural_language_tax is None

    def test_evaluate_insufficient_funds(self, budget):
        """Test evaluation with insufficient funds."""
        cost = Gas(tokens=200000)  # More than bank balance
        decision = budget.evaluate_communication(
            sender="a",
            receiver="b",
            cost=cost,
            using_pidgin=False,
        )
        assert not decision.approved
        assert "Insufficient" in decision.reason

    def test_evaluate_insufficient_funds_with_tax(self, budget, monitor):
        """Test evaluation with insufficient funds after tax."""
        # Add pidgin
        pidgin = PidginMetadata(
            name="TestPidgin",
            agent_a="a",
            agent_b="b",
            status=AdoptionStatus.ADOPTED,
        )
        monitor.pidgins[("a", "b")] = pidgin

        # Set balance so base cost is affordable but not with tax
        budget.bank.bucket.balance = 1100  # Can afford 1000, not 1200

        cost = Gas(tokens=1000)
        decision = budget.evaluate_communication(
            sender="a",
            receiver="b",
            cost=cost,
            using_pidgin=False,
        )

        assert not decision.approved
        assert "tax" in decision.reason.lower()

    @pytest.mark.asyncio
    async def test_metered_communication(self, budget):
        """Test metered communication execution."""
        receipt = await budget.metered_communication(
            sender="a",
            receiver="b",
            message="Hello world",
            estimated_tokens=100,
        )

        assert receipt.value == "Hello world"
        assert receipt.gas.tokens > 0

    @pytest.mark.asyncio
    async def test_metered_communication_rejected(self, budget):
        """Test metered communication rejection."""
        budget.bank.bucket.balance = 50  # Low balance

        with pytest.raises(ValueError, match="rejected"):
            await budget.metered_communication(
                sender="a",
                receiver="b",
                message="Hello",
                estimated_tokens=1000,
            )


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_compression_monitor(self):
        """Test creating a compression monitor."""
        monitor = create_compression_monitor()
        assert monitor.bank is not None
        assert monitor.roi_threshold == 2.0

    def test_create_compression_monitor_with_params(self):
        """Test creating monitor with custom parameters."""
        bank = CentralBank(max_balance=50000)
        monitor = create_compression_monitor(
            bank=bank,
            roi_threshold=3.0,
        )
        assert monitor.bank is bank
        assert monitor.roi_threshold == 3.0

    def test_create_zipper_budget(self):
        """Test creating a zipper budget."""
        bank = CentralBank()
        monitor = create_compression_monitor(bank=bank)
        budget = create_zipper_budget(bank, monitor, tax_rate=0.25)
        assert budget.tax_rate == 0.25

    @pytest.mark.asyncio
    async def test_analyze_compression_opportunity(self):
        """Test standalone ROI analysis."""
        logs = [
            CommunicationLog(
                sender="a",
                receiver="b",
                message=f"GET /api/resource/{i}",
                tokens=100,
                domain="api",
            )
            for i in range(25)
        ]

        roi = await analyze_compression_opportunity(
            logs,
            synthesis_cost_tokens=5000,
            roi_threshold=1.5,
        )

        assert roi.message_count == 25
        assert roi.synthesis_cost.tokens == 5000


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for compression economy."""

    @pytest.mark.asyncio
    async def test_full_workflow_without_grammarian(self):
        """Test full workflow without actual G-gent."""
        bank = CentralBank(max_balance=100000)
        monitor = create_compression_monitor(bank=bank, roi_threshold=1.0)
        budget = create_zipper_budget(bank, monitor)

        # Log communications
        for i in range(30):
            await budget.metered_communication(
                sender="researcher",
                receiver="assistant",
                message=f"Found paper by Author{i % 5} on topic{i % 3}",
                estimated_tokens=50,
                domain="citations",
            )

        # Analyze opportunity
        roi = await monitor.analyze_pair("researcher", "assistant")
        assert roi.message_count == 30

        # Check for opportunities
        _ = await monitor.check_all_pairs()
        # May or may not have opportunities depending on regularity

    @pytest.mark.asyncio
    async def test_pidgin_adoption_tracking(self):
        """Test tracking pidgin adoption over time."""
        # Test the adoption status progression directly on PidginMetadata
        pidgin = PidginMetadata(
            name="CitationPidgin",
            agent_a="a",
            agent_b="b",
            status=AdoptionStatus.PROPOSED,
            messages_using_natural_language=5,  # Simulate 5 NL messages
            messages_using_pidgin=0,
        )

        # Check initial adoption rate - all natural language
        pidgin.update_adoption_rate()
        assert pidgin.adoption_rate == 0.0
        assert pidgin.status == AdoptionStatus.PROPOSED  # No change (0% adoption)

        # First use of pidgin - should transition to PARTIAL
        pidgin.messages_using_pidgin = 1
        pidgin.update_adoption_rate()
        assert pidgin.adoption_rate > 0.0
        assert pidgin.status == AdoptionStatus.PARTIAL

        # More adoption - should transition to ADOPTED at 80%+
        pidgin.messages_using_pidgin = 20
        pidgin.update_adoption_rate()
        assert pidgin.adoption_rate == 0.8  # 20/(20+5) = 0.8
        assert pidgin.status == AdoptionStatus.ADOPTED
        assert pidgin.adopted_at is not None

    @pytest.mark.asyncio
    async def test_statistics_aggregation(self):
        """Test statistics aggregation across multiple pidgins."""
        bank = CentralBank()
        monitor = create_compression_monitor(bank=bank)

        # Add multiple pidgins
        for i, pair in enumerate([("a", "b"), ("c", "d"), ("e", "f")]):
            pidgin = PidginMetadata(
                name=f"Pidgin{i}",
                agent_a=pair[0],
                agent_b=pair[1],
                synthesis_cost=Gas(tokens=10000),
                actual_savings_to_date=(i + 1) * 25000,
            )
            monitor.pidgins[pair] = pidgin

        stats = monitor.get_statistics()
        assert stats["active_pidgins"] == 3
        assert stats["total_synthesis_cost_tokens"] == 30000  # 3 × 10k
        assert stats["total_savings_tokens"] == 150000  # 25k + 50k + 75k
        assert stats["net_savings_tokens"] == 120000  # 150k - 30k


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_tracker(self):
        """Test tracker with no logs."""
        tracker = CommunicationTracker()
        assert tracker.get_all_pairs() == []
        assert tracker.get_logs("a", "b") == []

    def test_single_message_roi(self):
        """Test ROI with single message."""
        calc = CompressionROICalculator()
        logs = [CommunicationLog(sender="a", receiver="b", message="Test", tokens=100)]
        roi = calc.calculate_roi(logs)
        assert roi.message_count == 1
        assert not roi.recommended  # Below min_message_count

    def test_zero_token_messages(self):
        """Test handling of zero-token messages."""
        calc = CompressionROICalculator()
        logs = [
            CommunicationLog(sender="a", receiver="b", message="", tokens=0)
            for _ in range(10)
        ]
        roi = calc.calculate_roi(logs)
        assert roi.avg_tokens_per_message == 0.0

    def test_deprecated_pidgin(self):
        """Test that deprecated pidgins are not active."""
        pidgin = PidginMetadata(
            name="OldPidgin",
            status=AdoptionStatus.DEPRECATED,
        )
        assert not pidgin.is_active

    def test_same_agent_pair(self):
        """Test communication between same agent (edge case)."""
        tracker = CommunicationTracker()
        log = tracker.log_communication("a", "a", "Self-talk", 10)
        assert log.agent_pair == ("a", "a")

    def test_unicode_messages(self):
        """Test handling of unicode messages."""
        tracker = CommunicationTracker()
        log = tracker.log_communication(
            sender="a",
            receiver="b",
            message="こんにちは 🚀 Привет",
            tokens=20,
        )
        assert "こんにちは" in log.message

    @pytest.mark.asyncio
    async def test_commission_without_grammarian(self):
        """Test commissioning when no grammarian available."""
        bank = CentralBank()
        monitor = CompressionEconomyMonitor(
            bank=bank,
            grammarian=None,  # No G-gent
        )

        result = await monitor.commission_pidgin("a", "b")
        assert result is None  # Graceful handling

    def test_budget_decision_types(self):
        """Test BudgetDecision with various configurations."""
        # Approved without tax
        decision = BudgetDecision(
            approved=True,
            reason="Approved",
            actual_cost=Gas(tokens=100),
        )
        assert decision.approved
        assert decision.natural_language_tax is None

        # Approved with tax
        decision = BudgetDecision(
            approved=True,
            reason="Tax applied",
            actual_cost=Gas(tokens=120),
            natural_language_tax=Gas(tokens=20),
            recommendation="Use pidgin",
        )
        assert decision.natural_language_tax.tokens == 20

        # Rejected
        decision = BudgetDecision(
            approved=False,
            reason="No funds",
        )
        assert not decision.approved
