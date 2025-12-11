"""
MemoryBudget: B-gent Integration for M-gent (Phase 4).

This module integrates M-gent's holographic memory with B-gent's token
economics, enabling budget-aware memory operations.

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    BudgetedMemory                            │
    │    (Holographic operations with token accounting)            │
    ├─────────────────────────────────────────────────────────────┤
    │   M-gent HolographicMemory      B-gent CentralBank           │
    │   (storage + retrieval)         (token economics)            │
    └─────────────────────────────────────────────────────────────┘

Key Features:
- Token-metered storage (pay for what you store)
- Budget-aware consolidation (compress when low on tokens)
- Resolution budget (hot memories get more resolution)
- Memory economics dashboard

Philosophy from spec:
    "Memory has costs: storage, retrieval, consolidation.
     Hot memories get more budget, cold memories are compressed."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Generic, Optional, Protocol, TypeVar

from .holographic import (
    CompressionLevel,
    HolographicMemory,
    MemoryPattern,
    ResonanceResult,
)

T = TypeVar("T")


# =============================================================================
# Budget Protocols (avoid circular imports with B-gent)
# =============================================================================


class TokenBudgetProtocol(Protocol):
    """Protocol for B-gent TokenBucket."""

    max_balance: int
    balance: int

    def can_afford(self, tokens: int) -> bool: ...
    def consume(self, tokens: int) -> bool: ...
    def force_consume(self, tokens: int) -> int: ...

    @property
    def available(self) -> int: ...


class CentralBankProtocol(Protocol):
    """Protocol for B-gent CentralBank."""

    bucket: TokenBudgetProtocol

    async def authorize(self, account_id: str, estimated_tokens: int) -> Any: ...
    async def settle(self, lease: Any, actual_tokens: int) -> Any: ...
    async def void(self, lease: Any) -> None: ...
    def get_balance(self) -> int: ...
    def get_stats(self) -> dict[str, Any]: ...


# =============================================================================
# Memory Cost Model
# =============================================================================


class CostCategory(Enum):
    """Categories of memory costs."""

    STORAGE = auto()  # Cost to store a pattern
    RETRIEVAL = auto()  # Cost per retrieval
    CONSOLIDATION = auto()  # Cost of background processing
    RESOLUTION_BOOST = auto()  # Cost to increase resolution


@dataclass
class MemoryCostModel:
    """Cost model for memory operations.

    Based on the philosophy:
    - Storage: Pay for embedding computation + space
    - Retrieval: Pay for similarity computation
    - Resolution: Higher resolution = higher cost
    """

    # Base costs (in tokens)
    base_storage_cost: int = 100  # Cost to store one pattern
    base_retrieval_cost: int = 10  # Cost per retrieval query
    base_consolidation_cost: int = 5  # Cost per pattern in consolidation

    # Resolution multipliers (cost × multiplier for each level)
    resolution_multipliers: dict[CompressionLevel, float] = field(
        default_factory=lambda: {
            CompressionLevel.FULL: 1.0,
            CompressionLevel.HIGH: 0.75,
            CompressionLevel.MEDIUM: 0.5,
            CompressionLevel.LOW: 0.25,
            CompressionLevel.MINIMAL: 0.1,
        }
    )

    # Content size factor (cost per 1000 characters)
    content_size_factor: float = 0.1

    # Embedding dimension factor (cost per 100 dimensions)
    embedding_dim_factor: float = 0.05

    def storage_cost(self, content: str, embedding_dim: int = 384) -> int:
        """Calculate storage cost for a pattern."""
        size_cost = len(content) * self.content_size_factor / 1000
        dim_cost = embedding_dim * self.embedding_dim_factor / 100
        return int(self.base_storage_cost * (1 + size_cost + dim_cost))

    def retrieval_cost(self, query_length: int = 100) -> int:
        """Calculate retrieval cost."""
        length_factor = 1 + query_length / 500
        return int(self.base_retrieval_cost * length_factor)

    def resolution_cost(
        self,
        from_level: CompressionLevel,
        to_level: CompressionLevel,
    ) -> int:
        """Calculate cost to change resolution."""
        from_mult = self.resolution_multipliers[from_level]
        to_mult = self.resolution_multipliers[to_level]

        # Cost is proportional to resolution increase
        if to_mult > from_mult:
            # Promoting: costs tokens
            return int(self.base_storage_cost * (to_mult - from_mult))
        else:
            # Demoting: no cost (actually saves)
            return 0

    def consolidation_cost(self, pattern_count: int) -> int:
        """Calculate consolidation cost for N patterns."""
        return self.base_consolidation_cost * pattern_count


@dataclass
class MemoryReceipt:
    """Receipt for a memory operation."""

    operation: str  # store, retrieve, consolidate, promote, demote
    tokens_charged: int
    tokens_estimated: int
    success: bool
    pattern_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def overrun(self) -> int:
        """How many tokens over estimate."""
        return max(0, self.tokens_charged - self.tokens_estimated)


# =============================================================================
# Resolution Budget
# =============================================================================


@dataclass
class ResolutionAllocation:
    """Resolution budget allocation for a pattern."""

    pattern_id: str
    allocated_resolution: CompressionLevel
    priority_score: float
    budget_share: float  # 0.0 to 1.0


class ResolutionBudget:
    """Manage memory resolution as an economic resource.

    High-resolution memories cost more tokens.
    Hot memories get more budget.
    Cold memories are compressed.

    This implements the "Resolution as Resource" principle:
    - Total resolution is bounded by token budget
    - Allocation is based on pattern priority
    - Priority = f(frequency, recency, importance)
    """

    def __init__(
        self,
        cost_model: Optional[MemoryCostModel] = None,
        max_resolution_budget: int = 10000,
    ):
        """Initialize resolution budget manager.

        Args:
            cost_model: Cost model for resolution calculations
            max_resolution_budget: Maximum tokens for resolution
        """
        self._cost_model = cost_model or MemoryCostModel()
        self._max_budget = max_resolution_budget

        # Track allocations
        self._allocations: dict[str, ResolutionAllocation] = {}

        # Priority weights
        self._frequency_weight = 0.4
        self._recency_weight = 0.3
        self._importance_weight = 0.3

    def calculate_priority(self, pattern: MemoryPattern[Any]) -> float:
        """Calculate priority score for a pattern.

        Priority = weighted sum of:
        - Frequency: log(access_count + 1) / 10
        - Recency: 1 / (1 + hours_since_access)
        - Importance: strength value
        """
        import math

        frequency = math.log1p(pattern.access_count) / 10.0
        recency = 1.0 / (1.0 + pattern.time_since_access.total_seconds() / 3600)
        importance = pattern.strength / 10.0

        return (
            self._frequency_weight * frequency
            + self._recency_weight * recency
            + self._importance_weight * importance
        )

    def allocate_resolution(
        self,
        patterns: list[MemoryPattern[Any]],
        available_budget: int,
    ) -> dict[str, ResolutionAllocation]:
        """Allocate resolution budget to patterns.

        Higher priority patterns get higher resolution.
        Total cost stays within available_budget.

        Args:
            patterns: Patterns to allocate for
            available_budget: Available token budget

        Returns:
            Dictionary of pattern ID → ResolutionAllocation
        """
        if not patterns:
            return {}

        # Calculate priorities
        priorities = [(p, self.calculate_priority(p)) for p in patterns]
        total_priority = sum(pr for _, pr in priorities)

        if total_priority <= 0:
            total_priority = 1.0

        allocations = {}
        for pattern, priority in priorities:
            # Budget share proportional to priority
            budget_share = priority / total_priority
            pattern_budget = int(budget_share * available_budget)

            # Determine resolution level based on budget
            level = self._budget_to_resolution(pattern_budget)

            allocations[pattern.id] = ResolutionAllocation(
                pattern_id=pattern.id,
                allocated_resolution=level,
                priority_score=priority,
                budget_share=budget_share,
            )

        self._allocations = allocations
        return allocations

    def _budget_to_resolution(self, budget: int) -> CompressionLevel:
        """Convert budget amount to resolution level."""
        # Resolution thresholds (tokens needed for each level)
        thresholds = [
            (100, CompressionLevel.FULL),
            (75, CompressionLevel.HIGH),
            (50, CompressionLevel.MEDIUM),
            (25, CompressionLevel.LOW),
            (0, CompressionLevel.MINIMAL),
        ]

        for threshold, level in thresholds:
            if budget >= threshold:
                return level

        return CompressionLevel.MINIMAL

    def get_allocation(self, pattern_id: str) -> Optional[ResolutionAllocation]:
        """Get current allocation for a pattern."""
        return self._allocations.get(pattern_id)

    def stats(self) -> dict[str, Any]:
        """Get resolution budget statistics."""
        if not self._allocations:
            return {"allocated_patterns": 0}

        return {
            "allocated_patterns": len(self._allocations),
            "avg_priority": sum(a.priority_score for a in self._allocations.values())
            / len(self._allocations),
            "resolution_distribution": {
                level.name: sum(
                    1
                    for a in self._allocations.values()
                    if a.allocated_resolution == level
                )
                for level in CompressionLevel
            },
        }


# =============================================================================
# Budgeted Memory
# =============================================================================


class BudgetedMemory(Generic[T]):
    """Holographic memory with token budget enforcement.

    This wraps a HolographicMemory with B-gent economics:
    - Every operation costs tokens
    - Budget exhaustion triggers compression
    - Resolution allocation based on priority

    Example:
        from agents.b.metered_functor import CentralBank

        bank = CentralBank(max_balance=100000)
        base_memory = HolographicMemory()
        memory = BudgetedMemory(base_memory, bank, account_id="m-gent")

        # Store with budget accounting
        receipt = await memory.store("m1", "User prefers dark mode")

        # Retrieve with budget accounting
        results, receipt = await memory.retrieve("preferences")

        # Check budget status
        status = memory.budget_status()
    """

    def __init__(
        self,
        memory: HolographicMemory[T],
        bank: CentralBankProtocol,
        account_id: str = "m-gent",
        cost_model: Optional[MemoryCostModel] = None,
        enable_auto_compress: bool = True,
        low_budget_threshold: float = 0.2,  # 20% budget triggers compression
    ):
        """Initialize budgeted memory.

        Args:
            memory: Underlying holographic memory
            bank: B-gent CentralBank for token economics
            account_id: Account ID for budget tracking
            cost_model: Cost model for operations
            enable_auto_compress: Auto-compress when budget low
            low_budget_threshold: Fraction of budget that triggers compression
        """
        self._memory = memory
        self._bank = bank
        self._account_id = account_id
        self._cost_model = cost_model or MemoryCostModel()
        self._enable_auto_compress = enable_auto_compress
        self._low_budget_threshold = low_budget_threshold

        # Resolution budget manager
        self._resolution_budget = ResolutionBudget(cost_model=self._cost_model)

        # Operation history
        self._receipts: list[MemoryReceipt] = []

    async def store(
        self,
        id: str,
        content: T,
        concepts: list[str] | None = None,
        embedding: list[float] | None = None,
    ) -> MemoryReceipt:
        """Store memory with budget accounting.

        Args:
            id: Unique identifier
            content: Memory content
            concepts: Semantic tags
            embedding: Pre-computed embedding

        Returns:
            MemoryReceipt with cost information

        Raises:
            InsufficientBudgetError: If budget insufficient
        """
        # Calculate cost
        content_str = str(content)
        estimated_cost = self._cost_model.storage_cost(content_str)

        # Authorize with bank
        try:
            lease = await self._bank.authorize(self._account_id, estimated_cost)
        except Exception as e:
            # Budget insufficient
            if self._enable_auto_compress:
                await self._emergency_compress()
                # Try again
                try:
                    lease = await self._bank.authorize(self._account_id, estimated_cost)
                except Exception:
                    raise InsufficientBudgetError(
                        "Cannot store: insufficient budget after compression"
                    ) from e
            else:
                raise InsufficientBudgetError(f"Cannot store: {e}") from e

        # Execute storage
        try:
            await self._memory.store(id, content, concepts, embedding)
            await self._bank.settle(lease, estimated_cost)

            receipt = MemoryReceipt(
                operation="store",
                tokens_charged=estimated_cost,
                tokens_estimated=estimated_cost,
                success=True,
                pattern_id=id,
                details={"content_length": len(content_str)},
            )
        except Exception as e:
            await self._bank.void(lease)
            receipt = MemoryReceipt(
                operation="store",
                tokens_charged=0,
                tokens_estimated=estimated_cost,
                success=False,
                pattern_id=id,
                details={"error": str(e)},
            )

        self._receipts.append(receipt)
        return receipt

    async def retrieve(
        self,
        query: str | list[float],
        limit: int = 10,
        threshold: float = 0.0,
    ) -> tuple[list[ResonanceResult[T]], MemoryReceipt]:
        """Retrieve with budget accounting.

        Args:
            query: Text query or embedding
            limit: Maximum results
            threshold: Minimum similarity

        Returns:
            Tuple of (results, receipt)
        """
        # Calculate cost
        query_str = query if isinstance(query, str) else "embedding_query"
        estimated_cost = self._cost_model.retrieval_cost(len(query_str))

        # Authorize
        try:
            lease = await self._bank.authorize(self._account_id, estimated_cost)
        except Exception as e:
            # Retrieval should be cheap, but handle gracefully
            receipt = MemoryReceipt(
                operation="retrieve",
                tokens_charged=0,
                tokens_estimated=estimated_cost,
                success=False,
                details={"error": str(e)},
            )
            self._receipts.append(receipt)
            return [], receipt

        # Execute retrieval
        try:
            results = await self._memory.retrieve(query, limit, threshold)
            await self._bank.settle(lease, estimated_cost)

            receipt = MemoryReceipt(
                operation="retrieve",
                tokens_charged=estimated_cost,
                tokens_estimated=estimated_cost,
                success=True,
                details={"results_count": len(results)},
            )
        except Exception as e:
            await self._bank.void(lease)
            results = []
            receipt = MemoryReceipt(
                operation="retrieve",
                tokens_charged=0,
                tokens_estimated=estimated_cost,
                success=False,
                details={"error": str(e)},
            )

        self._receipts.append(receipt)
        return results, receipt

    async def consolidate_with_budget(self) -> MemoryReceipt:
        """Consolidate memory with budget-aware resolution allocation.

        This combines:
        1. Standard consolidation (demote cold, promote hot)
        2. Resolution budget allocation (priority-based)

        Returns:
            MemoryReceipt with consolidation details
        """
        patterns = list(self._memory._patterns.values())
        estimated_cost = self._cost_model.consolidation_cost(len(patterns))

        # Authorize
        try:
            lease = await self._bank.authorize(self._account_id, estimated_cost)
        except Exception as e:
            receipt = MemoryReceipt(
                operation="consolidate",
                tokens_charged=0,
                tokens_estimated=estimated_cost,
                success=False,
                details={"error": str(e)},
            )
            self._receipts.append(receipt)
            return receipt

        # Execute consolidation
        try:
            # Standard consolidation
            stats = await self._memory.consolidate()

            # Resolution budget allocation
            available_budget = self._bank.get_balance()
            allocations = self._resolution_budget.allocate_resolution(
                patterns, available_budget
            )

            # Apply allocations
            for pattern_id, alloc in allocations.items():
                pattern = self._memory._patterns.get(pattern_id)
                if pattern:
                    pattern.compression = alloc.allocated_resolution

            await self._bank.settle(lease, estimated_cost)

            receipt = MemoryReceipt(
                operation="consolidate",
                tokens_charged=estimated_cost,
                tokens_estimated=estimated_cost,
                success=True,
                details={
                    **stats,
                    "allocations": len(allocations),
                },
            )
        except Exception as e:
            await self._bank.void(lease)
            receipt = MemoryReceipt(
                operation="consolidate",
                tokens_charged=0,
                tokens_estimated=estimated_cost,
                success=False,
                details={"error": str(e)},
            )

        self._receipts.append(receipt)
        return receipt

    async def _emergency_compress(self) -> int:
        """Emergency compression when budget is critically low.

        Aggressively compresses cold patterns to free up budget.

        Returns:
            Number of patterns compressed
        """
        cold = self._memory.identify_cold()
        compressed = 0

        for pattern in cold:
            # Compress to minimal
            if pattern.compression != CompressionLevel.MINIMAL:
                pattern.compression = CompressionLevel.MINIMAL
                compressed += 1

        return compressed

    def budget_status(self) -> dict[str, Any]:
        """Get current budget status.

        Returns:
            Budget status dictionary
        """
        bank_stats = self._bank.get_stats()
        current_balance = self._bank.get_balance()
        max_balance = bank_stats.get("max_balance", 100000)

        return {
            "current_balance": current_balance,
            "max_balance": max_balance,
            "utilization": 1 - (current_balance / max(max_balance, 1)),
            "is_low": current_balance < max_balance * self._low_budget_threshold,
            "receipts_count": len(self._receipts),
            "total_charged": sum(r.tokens_charged for r in self._receipts),
            "recent_operations": [
                {"op": r.operation, "cost": r.tokens_charged, "success": r.success}
                for r in self._receipts[-5:]
            ],
        }

    def memory_stats(self) -> dict[str, Any]:
        """Get combined memory and budget statistics."""
        return {
            **self._memory.stats(),
            "budget": self.budget_status(),
            "resolution_budget": self._resolution_budget.stats(),
        }

    # ========== Delegate to underlying memory ==========

    async def retrieve_by_concept(
        self, concept: str, limit: int = 10
    ) -> list[ResonanceResult[T]]:
        """Retrieve by concept (delegates to underlying memory)."""
        return await self._memory.retrieve_by_concept(concept, limit)

    def identify_hot(self) -> list[MemoryPattern[T]]:
        """Identify hot patterns."""
        return self._memory.identify_hot()

    def identify_cold(self) -> list[MemoryPattern[T]]:
        """Identify cold patterns."""
        return self._memory.identify_cold()


class InsufficientBudgetError(Exception):
    """Raised when memory budget is insufficient."""

    pass


# =============================================================================
# Memory Economics Dashboard
# =============================================================================


@dataclass
class MemoryEconomicsReport:
    """Report on memory economics over a time period."""

    period_start: datetime
    period_end: datetime

    # Token metrics
    total_tokens_spent: int
    tokens_on_storage: int
    tokens_on_retrieval: int
    tokens_on_consolidation: int

    # Operation counts
    store_count: int
    retrieve_count: int
    consolidate_count: int

    # Efficiency metrics
    avg_cost_per_store: float
    avg_cost_per_retrieve: float
    retrieval_hit_rate: float  # Successful retrievals / total

    # Budget health
    budget_utilization: float
    emergency_compressions: int


class MemoryEconomicsDashboard:
    """Dashboard for memory economics monitoring.

    Provides analytics on memory token usage,
    efficiency metrics, and budget health.
    """

    def __init__(self, budgeted_memory: BudgetedMemory[Any]) -> None:
        """Initialize dashboard.

        Args:
            budgeted_memory: Memory to monitor
        """
        self._memory = budgeted_memory

    def generate_report(
        self,
        since: Optional[datetime] = None,
    ) -> MemoryEconomicsReport:
        """Generate economics report.

        Args:
            since: Start of period (defaults to last 24 hours)

        Returns:
            MemoryEconomicsReport
        """
        now = datetime.now()
        since = since or (now - timedelta(hours=24))

        # Filter receipts in period
        receipts = [r for r in self._memory._receipts if r.timestamp >= since]

        # Aggregate by operation
        by_op: dict[str, list[MemoryReceipt]] = {
            "store": [],
            "retrieve": [],
            "consolidate": [],
        }
        for r in receipts:
            if r.operation in by_op:
                by_op[r.operation].append(r)

        # Calculate metrics
        tokens_storage = sum(r.tokens_charged for r in by_op["store"])
        tokens_retrieval = sum(r.tokens_charged for r in by_op["retrieve"])
        tokens_consolidation = sum(r.tokens_charged for r in by_op["consolidate"])

        store_count = len(by_op["store"])
        retrieve_count = len(by_op["retrieve"])
        consolidate_count = len(by_op["consolidate"])

        successful_retrieves = sum(1 for r in by_op["retrieve"] if r.success)
        hit_rate = successful_retrieves / max(retrieve_count, 1)

        budget_status = self._memory.budget_status()

        return MemoryEconomicsReport(
            period_start=since,
            period_end=now,
            total_tokens_spent=tokens_storage + tokens_retrieval + tokens_consolidation,
            tokens_on_storage=tokens_storage,
            tokens_on_retrieval=tokens_retrieval,
            tokens_on_consolidation=tokens_consolidation,
            store_count=store_count,
            retrieve_count=retrieve_count,
            consolidate_count=consolidate_count,
            avg_cost_per_store=tokens_storage / max(store_count, 1),
            avg_cost_per_retrieve=tokens_retrieval / max(retrieve_count, 1),
            retrieval_hit_rate=hit_rate,
            budget_utilization=budget_status["utilization"],
            emergency_compressions=0,  # Would need to track this
        )


# =============================================================================
# Factory Functions
# =============================================================================


def create_budgeted_memory(
    bank: CentralBankProtocol,
    account_id: str = "m-gent",
    **kwargs: Any,
) -> BudgetedMemory[Any]:
    """Create a BudgetedMemory with default configuration.

    Args:
        bank: B-gent CentralBank
        account_id: Account for budget tracking
        **kwargs: Additional config options

    Returns:
        Configured BudgetedMemory
    """
    memory: HolographicMemory[Any] = HolographicMemory()
    return BudgetedMemory(
        memory=memory,
        bank=bank,
        account_id=account_id,
        **kwargs,
    )


def create_mock_bank(
    max_balance: int = 100000,
    refill_rate: float = 100.0,
) -> CentralBankProtocol:
    """Create a mock CentralBank for testing.

    Returns a lightweight mock that implements CentralBankProtocol
    without the full B-gent dependency.

    Args:
        max_balance: Maximum token balance
        refill_rate: Token refill rate per second

    Returns:
        Mock bank object
    """

    @dataclass
    class MockLease:
        account_id: str
        estimated_tokens: int
        settled: bool = False
        voided: bool = False

    class MockBucket:
        def __init__(self, max_bal: int) -> None:
            self.max_balance = max_bal
            self.balance = max_bal

        @property
        def available(self) -> int:
            return self.balance

        def can_afford(self, tokens: int) -> bool:
            return self.balance >= tokens

        def consume(self, tokens: int) -> bool:
            if self.balance < tokens:
                return False
            self.balance -= tokens
            return True

        def force_consume(self, tokens: int) -> int:
            available = min(self.balance, tokens)
            self.balance -= available
            return tokens - available

    class MockBank:
        def __init__(self) -> None:
            self.bucket: TokenBudgetProtocol = MockBucket(max_balance)
            self._leases: dict[str, MockLease] = {}
            self._lease_counter = 0

        async def authorize(self, account_id: str, estimated_tokens: int) -> MockLease:
            if not self.bucket.can_afford(estimated_tokens):
                raise InsufficientBudgetError("Insufficient funds")
            self.bucket.consume(estimated_tokens)
            self._lease_counter += 1
            lease = MockLease(account_id, estimated_tokens)
            self._leases[f"lease_{self._lease_counter}"] = lease
            return lease

        async def settle(self, lease: MockLease, actual_tokens: int) -> None:
            if lease.settled or lease.voided:
                return
            lease.settled = True
            diff = lease.estimated_tokens - actual_tokens
            if diff > 0:
                self.bucket.balance = min(
                    self.bucket.max_balance, self.bucket.balance + diff
                )

        async def void(self, lease: MockLease) -> None:
            if lease.settled or lease.voided:
                return
            lease.voided = True
            self.bucket.balance = min(
                self.bucket.max_balance, self.bucket.balance + lease.estimated_tokens
            )

        def get_balance(self) -> int:
            return self.bucket.available

        def get_stats(self) -> dict[str, Any]:
            return {
                "balance": self.bucket.available,
                "max_balance": self.bucket.max_balance,
            }

    return MockBank()
