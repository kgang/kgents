"""
Compression Economy: The Semantic Zipper

Phase 1 of Structural Economics (B-gent × G-gent Integration).

Core insight: Language is expensive. Constraint is cheap.

The Semantic Zipper pattern:
1. Monitor inter-agent communication costs
2. When ROI > threshold, commission G-gent to create compressed pidgin
3. Incentivize agents to adopt pidgin via natural language tax
4. Track pidgin adoption and value creation

ROI Formula:
    ROI = (TokenCost_English - TokenCost_DSL - SynthesisCost) / SynthesisCost

Example savings:
    - Natural language citation: "I found a paper by Smith et al from 2020" (14 tokens)
    - Citation pidgin: "ref(Smith20,transformers)" (3 tokens)
    - Compression: 79% token reduction
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable

from .metered_functor import CentralBank, Gas, Receipt

if TYPE_CHECKING:
    pass


# =============================================================================
# Type Definitions
# =============================================================================


class AdoptionStatus(Enum):
    """Status of pidgin adoption."""

    PROPOSED = "proposed"  # Pidgin synthesized, agents notified
    PARTIAL = "partial"  # Some agents using pidgin
    ADOPTED = "adopted"  # Majority of agents using pidgin
    MANDATORY = "mandatory"  # Natural language tax enforced
    DEPRECATED = "deprecated"  # Pidgin no longer recommended


@dataclass
class CommunicationLog:
    """
    Record of inter-agent communication.

    Used to track message volume, token costs, and patterns
    between agent pairs.
    """

    sender: str
    receiver: str
    message: str
    tokens: int
    timestamp: datetime = field(default_factory=datetime.now)

    # Optional metadata
    domain: str | None = None
    using_pidgin: str | None = None  # Pidgin name if used

    @property
    def agent_pair(self) -> tuple[str, str]:
        """Canonical agent pair (sorted for consistent lookup)."""
        return tuple(sorted([self.sender, self.receiver]))


@dataclass
class CompressionROI:
    """
    Return on Investment analysis for pidgin synthesis.

    Determines whether creating a compressed language
    for an agent pair is economically justified.
    """

    # Current costs
    current_cost_tokens: int
    message_count: int
    avg_tokens_per_message: float

    # Estimated compression
    estimated_compression_ratio: float  # 0.1 = 90% reduction
    estimated_compressed_tokens: int

    # Synthesis costs
    synthesis_cost: Gas

    # Projected savings (30 days)
    projected_30day_messages: int
    projected_30day_savings: int

    # ROI calculation
    roi: float
    recommended: bool

    # Domain regularity (how compressible the communication is)
    regularity_score: float  # 0.0 to 1.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize for logging/storage."""
        return {
            "current_cost_tokens": self.current_cost_tokens,
            "message_count": self.message_count,
            "avg_tokens_per_message": self.avg_tokens_per_message,
            "estimated_compression_ratio": self.estimated_compression_ratio,
            "estimated_compressed_tokens": self.estimated_compressed_tokens,
            "synthesis_cost_tokens": self.synthesis_cost.tokens,
            "projected_30day_messages": self.projected_30day_messages,
            "projected_30day_savings": self.projected_30day_savings,
            "roi": self.roi,
            "recommended": self.recommended,
            "regularity_score": self.regularity_score,
        }


@dataclass
class PidginMetadata:
    """
    Metadata about a synthesized pidgin.

    Tracks the pidgin's economic impact and adoption status.
    """

    # Identity
    name: str
    tongue_id: str | None = None  # L-gent catalog ID

    # Agent pair
    agent_a: str = ""
    agent_b: str = ""

    # Economics
    synthesis_cost: Gas = field(default_factory=lambda: Gas(tokens=0))
    projected_savings_30day: int = 0
    actual_savings_to_date: int = 0

    # Adoption
    status: AdoptionStatus = AdoptionStatus.PROPOSED
    adoption_rate: float = 0.0  # 0.0 to 1.0
    messages_using_pidgin: int = 0
    messages_using_natural_language: int = 0

    # Timeline
    created_at: datetime = field(default_factory=datetime.now)
    adopted_at: datetime | None = None
    mandatory_at: datetime | None = None

    @property
    def agent_pair(self) -> tuple[str, str]:
        """Canonical agent pair."""
        return tuple(sorted([self.agent_a, self.agent_b]))

    @property
    def is_active(self) -> bool:
        """Whether pidgin is actively recommended."""
        return self.status in (
            AdoptionStatus.PROPOSED,
            AdoptionStatus.PARTIAL,
            AdoptionStatus.ADOPTED,
            AdoptionStatus.MANDATORY,
        )

    def update_adoption_rate(self) -> None:
        """Recalculate adoption rate from message counts."""
        total = self.messages_using_pidgin + self.messages_using_natural_language
        if total > 0:
            self.adoption_rate = self.messages_using_pidgin / total
        else:
            self.adoption_rate = 0.0

        # Update status based on adoption rate
        if self.adoption_rate >= 0.8 and self.status == AdoptionStatus.PARTIAL:
            self.status = AdoptionStatus.ADOPTED
            self.adopted_at = datetime.now()
        elif self.adoption_rate > 0.0 and self.status == AdoptionStatus.PROPOSED:
            self.status = AdoptionStatus.PARTIAL


@dataclass
class PidginAvailable:
    """Notification that a pidgin is available for an agent pair."""

    pidgin_name: str
    tongue_id: str | None
    mandatory: bool = False
    savings_estimate: str = "Unknown"
    example_compression: str | None = None


@dataclass
class BudgetDecision:
    """Result of budget evaluation."""

    approved: bool
    reason: str
    actual_cost: Gas = field(default_factory=lambda: Gas(tokens=0))
    recommendation: str | None = None
    natural_language_tax: Gas | None = None


# =============================================================================
# Communication Tracker
# =============================================================================


class CommunicationTracker:
    """
    Tracks inter-agent communication patterns.

    Collects communication logs and analyzes them for
    compression opportunities.
    """

    def __init__(self, window_days: int = 7):
        """
        Initialize tracker.

        Args:
            window_days: Number of days of history to consider
        """
        self.window_days = window_days
        self.logs: dict[tuple[str, str], list[CommunicationLog]] = {}

    def log_communication(
        self,
        sender: str,
        receiver: str,
        message: str,
        tokens: int,
        domain: str | None = None,
        using_pidgin: str | None = None,
    ) -> CommunicationLog:
        """
        Log a communication event.

        Returns the created log entry.
        """
        log = CommunicationLog(
            sender=sender,
            receiver=receiver,
            message=message,
            tokens=tokens,
            domain=domain,
            using_pidgin=using_pidgin,
        )

        pair = log.agent_pair
        if pair not in self.logs:
            self.logs[pair] = []
        self.logs[pair].append(log)

        return log

    def get_logs(
        self,
        agent_a: str,
        agent_b: str,
        since: datetime | None = None,
    ) -> list[CommunicationLog]:
        """
        Get communication logs for an agent pair.

        Args:
            agent_a: First agent
            agent_b: Second agent
            since: Optional cutoff datetime

        Returns:
            List of communication logs
        """
        pair = tuple(sorted([agent_a, agent_b]))
        logs = self.logs.get(pair, [])

        if since:
            logs = [log for log in logs if log.timestamp >= since]

        return logs

    def get_all_pairs(self) -> list[tuple[str, str]]:
        """Get all agent pairs with logged communication."""
        return list(self.logs.keys())

    def prune_old_logs(self) -> int:
        """
        Remove logs older than window.

        Returns number of logs removed.
        """
        cutoff = datetime.now() - timedelta(days=self.window_days)
        removed = 0

        for pair in list(self.logs.keys()):
            original_count = len(self.logs[pair])
            self.logs[pair] = [
                log for log in self.logs[pair] if log.timestamp >= cutoff
            ]
            removed += original_count - len(self.logs[pair])

            # Remove empty pairs
            if not self.logs[pair]:
                del self.logs[pair]

        return removed

    def get_statistics(
        self,
        agent_a: str,
        agent_b: str,
    ) -> dict[str, Any]:
        """Get communication statistics for an agent pair."""
        logs = self.get_logs(agent_a, agent_b)

        if not logs:
            return {
                "message_count": 0,
                "total_tokens": 0,
                "avg_tokens_per_message": 0.0,
                "using_pidgin_count": 0,
                "using_natural_language_count": 0,
            }

        total_tokens = sum(log.tokens for log in logs)
        using_pidgin = sum(1 for log in logs if log.using_pidgin)

        return {
            "message_count": len(logs),
            "total_tokens": total_tokens,
            "avg_tokens_per_message": total_tokens / len(logs),
            "using_pidgin_count": using_pidgin,
            "using_natural_language_count": len(logs) - using_pidgin,
        }


# =============================================================================
# ROI Calculator
# =============================================================================


class CompressionROICalculator:
    """
    Calculates ROI for pidgin synthesis.

    Determines whether creating a compressed language
    is economically justified based on communication patterns.
    """

    # Default synthesis cost (tokens for G-gent to create tongue)
    DEFAULT_SYNTHESIS_TOKENS = 10000
    DEFAULT_SYNTHESIS_TIME_MS = 30000

    # ROI threshold for recommendation
    ROI_THRESHOLD = 2.0  # 2x return required

    # Minimum message count to consider compression
    MIN_MESSAGE_COUNT = 10

    def __init__(
        self,
        synthesis_cost_tokens: int = DEFAULT_SYNTHESIS_TOKENS,
        roi_threshold: float = ROI_THRESHOLD,
        min_message_count: int = MIN_MESSAGE_COUNT,
    ):
        self.synthesis_cost_tokens = synthesis_cost_tokens
        self.roi_threshold = roi_threshold
        self.min_message_count = min_message_count

    def calculate_roi(
        self,
        logs: list[CommunicationLog],
        projection_days: int = 30,
    ) -> CompressionROI:
        """
        Calculate ROI for pidgin synthesis.

        Args:
            logs: Communication logs for agent pair
            projection_days: Days to project savings

        Returns:
            CompressionROI analysis
        """
        if not logs:
            return CompressionROI(
                current_cost_tokens=0,
                message_count=0,
                avg_tokens_per_message=0.0,
                estimated_compression_ratio=1.0,
                estimated_compressed_tokens=0,
                synthesis_cost=Gas(tokens=self.synthesis_cost_tokens),
                projected_30day_messages=0,
                projected_30day_savings=0,
                roi=0.0,
                recommended=False,
                regularity_score=0.0,
            )

        # Calculate current costs
        total_tokens = sum(log.tokens for log in logs)
        avg_tokens = total_tokens / len(logs)

        # Estimate compression ratio from message regularity
        regularity = self._measure_message_regularity(logs)
        compression_ratio = 0.1 + (0.4 * (1 - regularity))  # 10-50% of original

        # Calculate compressed tokens
        compressed_tokens = int(total_tokens * compression_ratio)

        # Create synthesis cost
        synthesis_cost = Gas(
            tokens=self.synthesis_cost_tokens,
            time_ms=self.DEFAULT_SYNTHESIS_TIME_MS,
            model_multiplier=1.0,
        )

        # Project future savings
        # Assume same message rate as observed
        days_observed = self._days_spanned(logs)
        if days_observed > 0:
            daily_messages = len(logs) / days_observed
        else:
            daily_messages = len(logs)  # All in one day

        projected_messages = int(daily_messages * projection_days)

        # Calculate savings
        tokens_saved_per_message = avg_tokens * (1 - compression_ratio)
        projected_savings = int(projected_messages * tokens_saved_per_message)

        # Calculate ROI
        if synthesis_cost.tokens > 0:
            roi = (projected_savings - synthesis_cost.tokens) / synthesis_cost.tokens
        else:
            roi = float("inf") if projected_savings > 0 else 0.0

        # Determine recommendation
        recommended = (
            roi > self.roi_threshold
            and len(logs) >= self.min_message_count
            and regularity > 0.3  # Some structure required
        )

        return CompressionROI(
            current_cost_tokens=total_tokens,
            message_count=len(logs),
            avg_tokens_per_message=avg_tokens,
            estimated_compression_ratio=compression_ratio,
            estimated_compressed_tokens=compressed_tokens,
            synthesis_cost=synthesis_cost,
            projected_30day_messages=projected_messages,
            projected_30day_savings=projected_savings,
            roi=roi,
            recommended=recommended,
            regularity_score=regularity,
        )

    def _measure_message_regularity(
        self,
        logs: list[CommunicationLog],
    ) -> float:
        """
        Measure how regular/structured the messages are.

        Higher regularity = more compressible.

        Heuristics:
        - Repeated words/phrases
        - Consistent message lengths
        - Domain-specific terms

        Returns:
            Regularity score [0.0, 1.0]
        """
        if not logs:
            return 0.0

        messages = [log.message for log in logs]

        # 1. Length consistency (std dev / mean)
        lengths = [len(m.split()) for m in messages]
        if len(lengths) > 1:
            mean_len = sum(lengths) / len(lengths)
            if mean_len > 0:
                variance = sum((x - mean_len) ** 2 for x in lengths) / len(lengths)
                std_dev = variance**0.5
                length_consistency = 1.0 - min(1.0, std_dev / mean_len)
            else:
                length_consistency = 0.0
        else:
            length_consistency = 0.5  # Neutral for single message

        # 2. Word frequency (repeated words indicate structure)
        all_words = " ".join(messages).lower().split()
        if all_words:
            word_counts: dict[str, int] = {}
            for word in all_words:
                word_counts[word] = word_counts.get(word, 0) + 1

            # Calculate what percentage of words appear more than once
            repeated_words = sum(1 for c in word_counts.values() if c > 1)
            repetition_score = repeated_words / len(word_counts)
        else:
            repetition_score = 0.0

        # 3. Domain consistency (all messages from same domain)
        domains = set(log.domain for log in logs if log.domain)
        if len(domains) == 1:
            domain_score = 1.0
        elif len(domains) == 0:
            domain_score = 0.5  # Unknown
        else:
            domain_score = 0.3  # Mixed domains

        # Weighted average
        regularity = (
            0.3 * length_consistency + 0.4 * repetition_score + 0.3 * domain_score
        )

        return min(1.0, max(0.0, regularity))

    def _days_spanned(self, logs: list[CommunicationLog]) -> float:
        """Calculate days spanned by logs."""
        if len(logs) < 2:
            return 1.0

        timestamps = [log.timestamp for log in logs]
        earliest = min(timestamps)
        latest = max(timestamps)

        delta = latest - earliest
        return max(1.0, delta.total_seconds() / 86400)


# =============================================================================
# Compression Economy Monitor
# =============================================================================


class CompressionEconomyMonitor:
    """
    Monitors inter-agent communication and triggers pidgin synthesis.

    The core Semantic Zipper pattern:
    1. Track communication costs per agent pair
    2. Calculate ROI for compression
    3. Commission G-gent to synthesize pidgins when ROI > threshold
    4. Register pidgins with L-gent catalog
    5. Track adoption and enforce via natural language tax
    """

    def __init__(
        self,
        bank: CentralBank,
        grammarian: Any | None = None,  # Grammarian - optional to avoid circular import
        registry: Any | None = None,  # Registry - optional
        roi_threshold: float = 2.0,
        check_interval_hours: float = 1.0,
    ):
        """
        Initialize the compression economy monitor.

        Args:
            bank: B-gent central bank for metering
            grammarian: G-gent for pidgin synthesis (optional)
            registry: L-gent registry for pidgin registration (optional)
            roi_threshold: ROI threshold for pidgin synthesis
            check_interval_hours: How often to check for compression opportunities
        """
        self.bank = bank
        self.grammarian = grammarian
        self.registry = registry
        self.roi_threshold = roi_threshold
        self.check_interval = timedelta(hours=check_interval_hours)

        # Internal state
        self.tracker = CommunicationTracker()
        self.calculator = CompressionROICalculator(roi_threshold=roi_threshold)
        self.pidgins: dict[tuple[str, str], PidginMetadata] = {}

        # Callbacks
        self._on_pidgin_available: list[
            Callable[[PidginAvailable, str, str], None]
        ] = []

        # Monitoring state
        self._running = False
        self._last_check: datetime | None = None

    def log_communication(
        self,
        sender: str,
        receiver: str,
        message: str,
        tokens: int,
        domain: str | None = None,
    ) -> CommunicationLog:
        """
        Log an inter-agent communication.

        This is the main entry point for tracking communication costs.
        """
        # Check if there's an available pidgin
        pair = tuple(sorted([sender, receiver]))
        pidgin = self.pidgins.get(pair)
        using_pidgin = pidgin.name if pidgin and pidgin.is_active else None

        # Log the communication
        log = self.tracker.log_communication(
            sender=sender,
            receiver=receiver,
            message=message,
            tokens=tokens,
            domain=domain,
            using_pidgin=using_pidgin,
        )

        # Update pidgin statistics if applicable
        if pidgin and pidgin.is_active:
            if using_pidgin:
                pidgin.messages_using_pidgin += 1
                pidgin.actual_savings_to_date += int(
                    tokens * (1 - 0.2)  # Assume 80% savings with pidgin
                )
            else:
                pidgin.messages_using_natural_language += 1
            pidgin.update_adoption_rate()

        return log

    async def analyze_pair(
        self,
        agent_a: str,
        agent_b: str,
    ) -> CompressionROI:
        """
        Analyze compression opportunity for an agent pair.

        Returns ROI analysis.
        """
        logs = self.tracker.get_logs(agent_a, agent_b)
        return self.calculator.calculate_roi(logs)

    async def check_all_pairs(self) -> list[tuple[tuple[str, str], CompressionROI]]:
        """
        Check all agent pairs for compression opportunities.

        Returns list of (pair, roi) tuples where roi.recommended is True.
        """
        opportunities = []

        for pair in self.tracker.get_all_pairs():
            # Skip pairs that already have pidgins
            if pair in self.pidgins and self.pidgins[pair].is_active:
                continue

            logs = self.tracker.logs.get(pair, [])
            roi = self.calculator.calculate_roi(logs)

            if roi.recommended:
                opportunities.append((pair, roi))

        return opportunities

    async def commission_pidgin(
        self,
        agent_a: str,
        agent_b: str,
        roi: CompressionROI | None = None,
    ) -> PidginMetadata | None:
        """
        Commission G-gent to create a pidgin for an agent pair.

        Args:
            agent_a: First agent
            agent_b: Second agent
            roi: Pre-calculated ROI (will calculate if not provided)

        Returns:
            PidginMetadata if successful, None if failed or grammarian not available
        """
        if self.grammarian is None:
            return None

        # Calculate ROI if not provided
        if roi is None:
            roi = await self.analyze_pair(agent_a, agent_b)

        if not roi.recommended:
            return None

        # Get example messages for pidgin synthesis
        logs = self.tracker.get_logs(agent_a, agent_b)
        examples = [log.message for log in logs[:20]]  # Sample of 20

        # Determine domain from logs
        domains = [log.domain for log in logs if log.domain]
        domain = domains[0] if domains else f"Communication: {agent_a} ↔ {agent_b}"

        try:
            # Import here to avoid circular dependency
            from agents.g import GrammarLevel

            # Commission G-gent to create pidgin
            tongue = await self.grammarian.reify(
                domain=domain,
                constraints=[
                    "Maximal compression",
                    "Preserve semantic content",
                    f"Bidirectional ({agent_a} ↔ {agent_b})",
                ],
                examples=examples,
                level=GrammarLevel.COMMAND,
                name=f"{agent_a}_{agent_b}_Pidgin",
            )

            # Create pidgin metadata
            pidgin = PidginMetadata(
                name=tongue.name,
                tongue_id=None,  # Will be set after L-gent registration
                agent_a=agent_a,
                agent_b=agent_b,
                synthesis_cost=roi.synthesis_cost,
                projected_savings_30day=roi.projected_30day_savings,
                status=AdoptionStatus.PROPOSED,
            )

            # Register with L-gent if available
            if self.registry is not None:
                from agents.g import register_tongue

                entry = await register_tongue(
                    tongue, self.registry, author="CompressionEconomyMonitor"
                )
                pidgin.tongue_id = entry.id

            # Store pidgin
            pair = tuple(sorted([agent_a, agent_b]))
            self.pidgins[pair] = pidgin

            # Notify callbacks
            notification = PidginAvailable(
                pidgin_name=pidgin.name,
                tongue_id=pidgin.tongue_id,
                mandatory=False,
                savings_estimate=f"{int((1 - roi.estimated_compression_ratio) * 100)}% token reduction",
            )
            for callback in self._on_pidgin_available:
                callback(notification, agent_a, agent_b)

            return pidgin

        except Exception as e:
            # Log error but don't fail
            print(f"Failed to commission pidgin for {agent_a} ↔ {agent_b}: {e}")
            return None

    def get_pidgin(
        self,
        agent_a: str,
        agent_b: str,
    ) -> PidginMetadata | None:
        """Get pidgin for an agent pair if one exists."""
        pair = tuple(sorted([agent_a, agent_b]))
        return self.pidgins.get(pair)

    def on_pidgin_available(
        self,
        callback: Callable[[PidginAvailable, str, str], None],
    ) -> None:
        """Register callback for when pidgin becomes available."""
        self._on_pidgin_available.append(callback)

    async def start_monitoring(self) -> None:
        """
        Start the monitoring loop.

        Runs until stop_monitoring() is called.
        """
        self._running = True

        while self._running:
            try:
                # Prune old logs
                self.tracker.prune_old_logs()

                # Check for compression opportunities
                opportunities = await self.check_all_pairs()

                # Commission pidgins for recommended pairs
                for pair, roi in opportunities:
                    await self.commission_pidgin(pair[0], pair[1], roi)

                self._last_check = datetime.now()

            except Exception as e:
                print(f"Error in compression monitor: {e}")

            # Wait for next check interval
            await asyncio.sleep(self.check_interval.total_seconds())

    def stop_monitoring(self) -> None:
        """Stop the monitoring loop."""
        self._running = False

    def get_statistics(self) -> dict[str, Any]:
        """Get overall compression economy statistics."""
        total_pairs = len(self.tracker.get_all_pairs())
        active_pidgins = sum(1 for p in self.pidgins.values() if p.is_active)
        total_savings = sum(p.actual_savings_to_date for p in self.pidgins.values())
        total_synthesis_cost = sum(
            p.synthesis_cost.tokens for p in self.pidgins.values()
        )

        return {
            "total_agent_pairs": total_pairs,
            "active_pidgins": active_pidgins,
            "total_savings_tokens": total_savings,
            "total_synthesis_cost_tokens": total_synthesis_cost,
            "net_savings_tokens": total_savings - total_synthesis_cost,
            "last_check": self._last_check.isoformat() if self._last_check else None,
        }


# =============================================================================
# Semantic Zipper Budget
# =============================================================================


class SemanticZipperBudget:
    """
    Budget that incentivizes pidgin usage via natural language tax.

    When a pidgin exists for an agent pair:
    - Using the pidgin: Normal cost
    - Using natural language: 20% tax added

    This creates economic pressure to adopt compressed languages.
    """

    # Tax rate for natural language when pidgin is available
    NATURAL_LANGUAGE_TAX_RATE = 0.20  # 20% tax

    def __init__(
        self,
        bank: CentralBank,
        compression_monitor: CompressionEconomyMonitor,
        tax_rate: float = NATURAL_LANGUAGE_TAX_RATE,
    ):
        """
        Initialize semantic zipper budget.

        Args:
            bank: B-gent central bank
            compression_monitor: Monitor for pidgin availability
            tax_rate: Tax rate for natural language when pidgin available
        """
        self.bank = bank
        self.compression_monitor = compression_monitor
        self.tax_rate = tax_rate

    def evaluate_communication(
        self,
        sender: str,
        receiver: str,
        cost: Gas,
        using_pidgin: bool = False,
    ) -> BudgetDecision:
        """
        Evaluate a communication operation for budget approval.

        Args:
            sender: Sending agent
            receiver: Receiving agent
            cost: Estimated cost
            using_pidgin: Whether communication uses available pidgin

        Returns:
            BudgetDecision with approval status and actual cost
        """
        # Check if pidgin available for this pair
        pidgin = self.compression_monitor.get_pidgin(sender, receiver)

        if pidgin and pidgin.is_active and not using_pidgin:
            # Apply natural language tax
            tax = Gas(
                tokens=int(cost.tokens * self.tax_rate),
                time_ms=0.0,
                model_multiplier=cost.model_multiplier,
            )

            actual_cost = cost + tax

            # Check if we can afford the taxed amount
            if not self.bank.bucket.can_afford(actual_cost.tokens):
                return BudgetDecision(
                    approved=False,
                    reason=f"Insufficient funds (including {int(self.tax_rate * 100)}% natural language tax)",
                    actual_cost=actual_cost,
                    recommendation=f"Switch to pidgin '{pidgin.name}' for {int((1 - 0.2) * 100)}% savings",
                )

            return BudgetDecision(
                approved=True,
                reason=f"Natural language tax applied (pidgin '{pidgin.name}' available)",
                actual_cost=actual_cost,
                recommendation=f"Switch to {pidgin.name} for reduced cost",
                natural_language_tax=tax,
            )

        # No pidgin or using pidgin - normal cost
        if not self.bank.bucket.can_afford(cost.tokens):
            return BudgetDecision(
                approved=False,
                reason="Insufficient funds",
                actual_cost=cost,
            )

        return BudgetDecision(
            approved=True,
            reason="Approved" + (" (using pidgin)" if using_pidgin else ""),
            actual_cost=cost,
        )

    async def metered_communication(
        self,
        sender: str,
        receiver: str,
        message: str,
        estimated_tokens: int,
        using_pidgin: bool = False,
        domain: str | None = None,
    ) -> Receipt[str]:
        """
        Execute a metered communication with compression economics.

        Args:
            sender: Sending agent
            receiver: Receiving agent
            message: Message content
            estimated_tokens: Estimated token cost
            using_pidgin: Whether using available pidgin
            domain: Optional domain for logging

        Returns:
            Receipt with gas cost and result
        """
        cost = Gas(tokens=estimated_tokens, time_ms=0.0, model_multiplier=1.0)

        # Evaluate budget
        decision = self.evaluate_communication(
            sender=sender,
            receiver=receiver,
            cost=cost,
            using_pidgin=using_pidgin,
        )

        if not decision.approved:
            raise ValueError(f"Communication rejected: {decision.reason}")

        # Authorize with bank
        start_time = datetime.now()
        lease = await self.bank.authorize(sender, decision.actual_cost.tokens)

        try:
            # Log communication
            self.compression_monitor.log_communication(
                sender=sender,
                receiver=receiver,
                message=message,
                tokens=estimated_tokens,
                domain=domain,
            )

            # Settle
            gas = await self.bank.settle(lease, decision.actual_cost.tokens)

            return Receipt(
                value=message,
                gas=gas,
                start_time=start_time,
                end_time=datetime.now(),
            )

        except Exception as e:
            await self.bank.void(lease)
            raise e


# =============================================================================
# Convenience Functions
# =============================================================================


def create_compression_monitor(
    bank: CentralBank | None = None,
    grammarian: Any | None = None,
    registry: Any | None = None,
    roi_threshold: float = 2.0,
) -> CompressionEconomyMonitor:
    """
    Create a compression economy monitor.

    Args:
        bank: B-gent central bank (creates default if None)
        grammarian: G-gent for pidgin synthesis
        registry: L-gent registry for pidgin registration
        roi_threshold: ROI threshold for pidgin synthesis

    Returns:
        Configured CompressionEconomyMonitor
    """
    if bank is None:
        bank = CentralBank()

    return CompressionEconomyMonitor(
        bank=bank,
        grammarian=grammarian,
        registry=registry,
        roi_threshold=roi_threshold,
    )


def create_zipper_budget(
    bank: CentralBank,
    compression_monitor: CompressionEconomyMonitor,
    tax_rate: float = 0.20,
) -> SemanticZipperBudget:
    """
    Create a semantic zipper budget.

    Args:
        bank: B-gent central bank
        compression_monitor: Compression economy monitor
        tax_rate: Tax rate for natural language when pidgin available

    Returns:
        Configured SemanticZipperBudget
    """
    return SemanticZipperBudget(
        bank=bank,
        compression_monitor=compression_monitor,
        tax_rate=tax_rate,
    )


async def analyze_compression_opportunity(
    logs: list[CommunicationLog],
    synthesis_cost_tokens: int = 10000,
    roi_threshold: float = 2.0,
) -> CompressionROI:
    """
    Analyze compression opportunity from communication logs.

    Standalone function for one-off analysis.

    Args:
        logs: Communication logs to analyze
        synthesis_cost_tokens: Cost to synthesize pidgin
        roi_threshold: ROI threshold for recommendation

    Returns:
        CompressionROI analysis
    """
    calculator = CompressionROICalculator(
        synthesis_cost_tokens=synthesis_cost_tokens,
        roi_threshold=roi_threshold,
    )
    return calculator.calculate_roi(logs)
