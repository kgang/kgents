"""
Metered Functor: Economic Transformation of Agents

Implements the Metered Functor from spec/b-gents/banker.md:
- Type: Agent[A, B] → Agent[A, Receipt[B]]
- Token Bucket with hydraulic refill
- Sinking Fund for emergencies
- Token Futures for reservations
- Vickrey Auction for resource contention
- Dual Budget (Entropy + Economic)

The Metered Functor transforms any "free" agent into an "economic" agent.
Every invocation becomes a transaction with:
1. Estimation Phase (The Quote)
2. Authorization Phase (The Hold)
3. Execution Phase
4. Settlement Phase (The Bill)
5. Bankruptcy Protection (Rollback)

Linear Logic: Tokens are resources that are *consumed*, not copied.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Generic, Optional, Protocol, TypeVar

from .value_tensor import (
    ValueTensor,
)

# =============================================================================
# Type Variables and Protocols
# =============================================================================

A = TypeVar("A", contravariant=True)
B = TypeVar("B", covariant=True)
B_inv = TypeVar("B_inv")  # Invariant for Receipt


class Agent(Protocol[A, B]):
    """Protocol for agents that can be metered."""

    async def invoke(self, input: A) -> B: ...

    def estimate_cost(self, input: A) -> int:
        """Estimate token cost for input. Default: 1000 tokens."""
        return 1000


# =============================================================================
# Token Economics (from B-gent Banker)
# =============================================================================


@dataclass
class Gas:
    """
    The operational cost of inference (Currency A).

    Unit: Raw tokens consumed
    Physics: Linear with time and token count
    Role: The "Energy Bill" - you must pay it to keep the lights on
    """

    tokens: int = 0
    time_ms: float = 0.0
    model_multiplier: float = 1.0  # opus=15x, sonnet=3x, haiku=1x

    # Cost per token by model tier
    COST_PER_TOKEN = 0.00001  # $0.01 per 1000 tokens (base)

    @property
    def cost_usd(self) -> float:
        """Real-world cost (API bills)."""
        return self.tokens * self.model_multiplier * self.COST_PER_TOKEN

    def __add__(self, other: "Gas") -> "Gas":
        return Gas(
            tokens=self.tokens + other.tokens,
            time_ms=self.time_ms + other.time_ms,
            model_multiplier=max(self.model_multiplier, other.model_multiplier),
        )


@dataclass
class Impact:
    """
    The increase in system value from an operation (Currency B).

    Unit: Value units (dimensionless, relative)
    Physics: Generated only on State Change (bug fixed, test passed, PR merged)
    Role: "Stock" - agents earn it by being useful
    """

    base_value: float = 0.0
    tier: str = "syntactic"  # syntactic/functional/deployment/ethical
    multipliers: dict[str, float] = field(default_factory=dict)

    @property
    def realized_value(self) -> float:
        """Total value after multipliers."""
        result = self.base_value
        for mult in self.multipliers.values():
            result *= mult
        return result


@dataclass
class Receipt(Generic[B_inv]):
    """
    Receipt from metered execution.

    The Metered Functor transforms Agent[A, B] → Agent[A, Receipt[B]].
    The Receipt wraps the result with economic metadata.
    """

    value: B_inv
    gas: Gas
    impact: Optional[Impact] = None
    tensor: Optional[ValueTensor] = None

    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0

    # Status
    from_sinking_fund: bool = False
    debt_incurred: float = 0.0

    @property
    def roc(self) -> float:
        """Return on Compute."""
        if not self.impact or self.gas.cost_usd <= 0:
            return 0.0
        return self.impact.realized_value / self.gas.cost_usd


# =============================================================================
# Token Bucket (Hydraulic Controller)
# =============================================================================


@dataclass
class TokenBucket:
    """
    Token Bucket with Hydraulic Refill (from B-gent Banker).

    Implements the "Leaky Bucket" rate limiter from network engineering.
    Balance refills over time, allowing burst capacity.

    Kelvin's Circulation Theorem: The flow of value must be conserved.
    """

    max_balance: int = 100000
    balance: int = 100000
    refill_rate: float = 100.0  # Tokens per second
    last_update: float = field(default_factory=time.time)

    # Statistics
    total_consumed: int = 0
    total_refilled: int = 0

    def _refresh(self) -> None:
        """Hydraulic refill: Time = Money."""
        now = time.time()
        delta = now - self.last_update
        inflow = int(delta * self.refill_rate)
        if inflow > 0:
            old_balance = self.balance
            self.balance = min(self.max_balance, self.balance + inflow)
            self.total_refilled += self.balance - old_balance
            self.last_update = now

    @property
    def available(self) -> int:
        """Get current available balance after refresh."""
        self._refresh()
        return self.balance

    def can_afford(self, tokens: int) -> bool:
        """Check if we can afford this many tokens."""
        self._refresh()
        return self.balance >= tokens

    def consume(self, tokens: int) -> bool:
        """
        Consume tokens (Linear Logic: consumed, not copied).

        Returns True if successful, False if insufficient balance.
        """
        self._refresh()
        if self.balance < tokens:
            return False
        self.balance -= tokens
        self.total_consumed += tokens
        return True

    def force_consume(self, tokens: int) -> int:
        """
        Consume as many tokens as available.

        Returns the shortfall (0 if fully consumed).
        """
        self._refresh()
        available = min(self.balance, tokens)
        self.balance -= available
        self.total_consumed += available
        return tokens - available


# =============================================================================
# Sinking Fund (Insurance Reserve)
# =============================================================================


@dataclass
class Loan:
    """Emergency loan from sinking fund."""

    agent_id: str
    amount: int
    granted_at: datetime = field(default_factory=datetime.now)
    repaid: bool = False
    debt_mode: bool = True  # Reduced capabilities until repaid


@dataclass
class Denial:
    """Loan denial."""

    reason: str


@dataclass
class SinkingFund:
    """
    Emergency reserve from 1% tax on all transactions.

    Purpose: If a critical agent hits 0 budget but MUST run to save
    the system, the fund grants an emergency loan.

    Constraint: The agent enters "Debt Mode" (reduced capabilities)
    until the loan is repaid.
    """

    reserve: float = 0.0
    tax_rate: float = 0.01  # 1% of all transactions
    outstanding_loans: list[Loan] = field(default_factory=list)

    def tax(self, amount: int) -> int:
        """Collect tax from transaction, return remaining."""
        tax = int(amount * self.tax_rate)
        self.reserve += tax
        return amount - tax

    def can_loan(self, amount: int) -> bool:
        """Check if emergency loan is possible."""
        return self.reserve >= amount

    def emergency_loan(self, agent_id: str, amount: int) -> Loan | Denial:
        """Grant emergency loan from reserve."""
        if amount > self.reserve:
            return Denial(reason=f"Insufficient reserve: {self.reserve} < {amount}")

        self.reserve -= amount
        loan = Loan(agent_id=agent_id, amount=amount)
        self.outstanding_loans.append(loan)
        return loan

    def repay_loan(self, loan: Loan, amount: int) -> int:
        """
        Repay a loan.

        Returns remaining debt (0 if fully repaid).
        """
        if loan.repaid:
            return 0

        if amount >= loan.amount:
            loan.repaid = True
            loan.debt_mode = False
            self.reserve += loan.amount
            return 0
        else:
            loan.amount -= amount
            self.reserve += amount
            return loan.amount

    def get_outstanding_debt(self, agent_id: str) -> int:
        """Get total outstanding debt for an agent."""
        return sum(
            loan.amount
            for loan in self.outstanding_loans
            if loan.agent_id == agent_id and not loan.repaid
        )


# =============================================================================
# Token Futures (Reservations)
# =============================================================================


@dataclass
class TokenFuture:
    """
    A reservation of future tokens.

    Like a financial option, this reserves capacity without
    consuming it until needed. Ensures Atomic Economics:
    either you have budget for the whole job, or you don't start.
    """

    reserved_tokens: int
    holder: str  # Agent or job ID
    expires_at: datetime
    exercise_price: int = 0  # Premium paid for reservation

    @property
    def is_valid(self) -> bool:
        return datetime.now() < self.expires_at


class FuturesMarket:
    """
    Market for token futures.

    Prevents the case where step 49 of 50 fails due to budget exhaustion.
    """

    def __init__(self, bank: "CentralBank"):
        self.bank = bank
        self.futures: list[TokenFuture] = []

    def calculate_premium(self, tokens: int, duration: timedelta) -> int:
        """Calculate premium for reserving tokens."""
        # Premium = tokens * (1 + duration_hours * 0.01)
        hours = duration.total_seconds() / 3600
        return int(tokens * (1 + hours * 0.01))

    async def buy_option(
        self,
        agent_id: str,
        tokens: int,
        duration: timedelta,
    ) -> TokenFuture | Denial:
        """
        Buy a call option for tokens.

        The bank *reserves* that capacity.
        The agent pays a premium for the reservation.
        """
        premium = self.calculate_premium(tokens, duration)

        # Check if agent can afford premium
        if not self.bank.bucket.can_afford(premium):
            return Denial(reason="Cannot afford premium")

        # Reserve the tokens
        if not self.bank.bucket.can_afford(tokens + premium):
            return Denial(reason="Insufficient capacity to reserve")

        # Charge premium and create future
        self.bank.bucket.consume(premium)

        future = TokenFuture(
            reserved_tokens=tokens,
            holder=agent_id,
            expires_at=datetime.now() + duration,
            exercise_price=premium,
        )
        self.futures.append(future)
        return future

    async def exercise(self, future: TokenFuture) -> Gas | Denial:
        """Exercise the option to get the reserved tokens."""
        if not future.is_valid:
            return Denial(reason="Future has expired")

        if future not in self.futures:
            return Denial(reason="Unknown future")

        # Grant the reserved tokens (no additional charge)
        self.futures.remove(future)
        return Gas(tokens=future.reserved_tokens, time_ms=0.0)


# =============================================================================
# Vickrey Auction (Resource Contention)
# =============================================================================


@dataclass
class Bid:
    """A bid in the priority auction."""

    agent_id: str
    requested_tokens: int
    confidence: float  # 0.0 to 1.0
    criticality: float  # 0.0 to 1.0

    @property
    def value(self) -> float:
        """Bid value = confidence × criticality."""
        return self.confidence * self.criticality


@dataclass
class Allocation:
    """Result of auction."""

    winner: str
    tokens: int
    clearing_price: float


async def priority_auction(bids: list[Bid], available_tokens: int) -> list[Allocation]:
    """
    Vickrey auction: Winner pays second-highest price.

    This mathematically proves that agents are incentivized
    to report their *true* confidence, preventing "Priority Inflation."

    Returns allocations for all winners (may be multiple if capacity allows).
    """
    if not bids:
        return []

    # Sort by bid value (Confidence × Criticality)
    sorted_bids = sorted(bids, key=lambda x: x.value, reverse=True)

    allocations = []
    remaining = available_tokens

    for i, bid in enumerate(sorted_bids):
        if remaining <= 0:
            break

        # Allocate up to requested amount
        allocated = min(bid.requested_tokens, remaining)
        if allocated <= 0:
            continue

        # Winner pays the runner-up's price (Vickrey Rule)
        if i + 1 < len(sorted_bids):
            clearing_price = sorted_bids[i + 1].value
        else:
            clearing_price = 0.0  # No runner-up

        allocations.append(
            Allocation(
                winner=bid.agent_id,
                tokens=allocated,
                clearing_price=clearing_price,
            )
        )
        remaining -= allocated

    return allocations


# =============================================================================
# Lease (Authorization Hold)
# =============================================================================


@dataclass
class Lease:
    """
    Authorization hold on tokens.

    Like a credit card hold: tokens are reserved but not yet spent.
    """

    account_id: str
    estimated_tokens: int
    granted_at: datetime = field(default_factory=datetime.now)
    settled: bool = False
    voided: bool = False


# =============================================================================
# Central Bank
# =============================================================================


class CentralBank:
    """
    The Central Bank acts as a Hydraulic Controller.

    Implements Kelvin's Circulation Theorem: The flow of value must be conserved.

    Features:
    - Token Bucket with hydraulic refill
    - Sinking Fund for emergencies
    - Futures Market for reservations
    - Vickrey Auction for contention
    """

    def __init__(
        self,
        max_balance: int = 100000,
        refill_rate: float = 100.0,
        tax_rate: float = 0.01,
    ):
        self.bucket = TokenBucket(
            max_balance=max_balance,
            balance=max_balance,
            refill_rate=refill_rate,
        )
        self.sinking_fund = SinkingFund(tax_rate=tax_rate)
        self.futures_market = FuturesMarket(self)

        # Active leases
        self.leases: dict[str, Lease] = {}
        self._lease_counter = 0

    async def authorize(self, account_id: str, estimated_tokens: int) -> Lease:
        """
        Authorization Phase: Create a hold on tokens.

        Raises InsufficientFundsError if rejected.
        """
        # Apply tax
        after_tax = self.sinking_fund.tax(estimated_tokens)

        # Check balance
        if not self.bucket.can_afford(after_tax):
            # Try emergency loan if critical
            outstanding_debt = self.sinking_fund.get_outstanding_debt(account_id)
            if outstanding_debt > 0:
                raise InsufficientFundsError(
                    f"Agent {account_id} already in debt: {outstanding_debt}"
                )

            loan_result = self.sinking_fund.emergency_loan(account_id, after_tax)
            if isinstance(loan_result, Denial):
                raise InsufficientFundsError(loan_result.reason)

        # Create lease
        self._lease_counter += 1
        lease_id = f"lease_{self._lease_counter}"
        lease = Lease(account_id=account_id, estimated_tokens=after_tax)
        self.leases[lease_id] = lease

        # Hold tokens
        self.bucket.consume(after_tax)

        return lease

    async def settle(self, lease: Lease, actual_tokens: int) -> Gas:
        """
        Settlement Phase: Finalize the transaction.

        Returns the actual Gas consumed.
        """
        if lease.settled or lease.voided:
            raise ValueError("Lease already settled or voided")

        lease.settled = True

        # Calculate difference
        diff = lease.estimated_tokens - actual_tokens
        if diff > 0:
            # Refund excess
            self.bucket.balance = min(
                self.bucket.max_balance, self.bucket.balance + diff
            )
        elif diff < 0:
            # Additional charge (should be rare if estimates are good)
            self.bucket.force_consume(-diff)

        return Gas(tokens=actual_tokens)

    async def void(self, lease: Lease) -> None:
        """
        Bankruptcy Protection: Rollback the transaction.

        Returns held tokens to the pool.
        """
        if lease.settled or lease.voided:
            return

        lease.voided = True
        # Return held tokens
        self.bucket.balance = min(
            self.bucket.max_balance, self.bucket.balance + lease.estimated_tokens
        )

    def get_balance(self) -> int:
        """Get current token balance."""
        return self.bucket.available

    def get_stats(self) -> dict[str, Any]:
        """Get bank statistics."""
        return {
            "balance": self.bucket.available,
            "max_balance": self.bucket.max_balance,
            "total_consumed": self.bucket.total_consumed,
            "total_refilled": self.bucket.total_refilled,
            "sinking_fund_reserve": self.sinking_fund.reserve,
            "outstanding_loans": len(
                [
                    loan
                    for loan in self.sinking_fund.outstanding_loans
                    if not loan.repaid
                ]
            ),
            "active_futures": len(self.futures_market.futures),
            "active_leases": len(
                [
                    lease
                    for lease in self.leases.values()
                    if not lease.settled and not lease.voided
                ]
            ),
        }


class InsufficientFundsError(Exception):
    """Raised when there are insufficient funds for an operation."""

    pass


# =============================================================================
# Dual Budget (Entropy + Economic)
# =============================================================================


@dataclass
class EntropyBudget:
    """Entropy budget for controlling recursive depth."""

    initial: float = 1.0
    remaining: float = 1.0

    def can_afford(self, cost: float) -> bool:
        return self.remaining >= cost

    def consume(self, cost: float) -> "EntropyBudget":
        return EntropyBudget(
            initial=self.initial,
            remaining=max(0.0, self.remaining - cost),
        )


@dataclass
class DualBudget:
    """
    Two conservation laws operating simultaneously.

    Entropy: Controls recursive depth (prevents fork bombs)
    Economic: Controls resource consumption (prevents bankruptcy)
    """

    entropy: EntropyBudget
    economic: TokenBucket

    def can_proceed(self, entropy_cost: float, token_cost: int) -> bool:
        return self.entropy.can_afford(entropy_cost) and self.economic.can_afford(
            token_cost
        )

    def spend(self, entropy_cost: float, token_cost: int) -> bool:
        """
        Spend from both budgets.

        Returns True if successful, False if either budget insufficient.
        """
        if not self.can_proceed(entropy_cost, token_cost):
            return False

        self.entropy = self.entropy.consume(entropy_cost)
        self.economic.consume(token_cost)
        return True


# =============================================================================
# The Metered Functor
# =============================================================================


class Metered(Generic[A, B]):
    """
    The Metered Functor transforms an Agent into a Transaction.

    Type: Agent[A, B] → Agent[A, Receipt[B]]

    Every invocation becomes a transaction with:
    1. Estimation Phase (The Quote)
    2. Authorization Phase (The Hold)
    3. Execution Phase
    4. Settlement Phase (The Bill)
    5. Bankruptcy Protection (Rollback)
    """

    def __init__(
        self,
        agent: Agent[A, B],
        bank: CentralBank,
        account_id: str,
        model_multiplier: float = 1.0,
    ):
        self.agent = agent
        self.bank = bank
        self.account_id = account_id
        self.model_multiplier = model_multiplier

    async def invoke(self, input: A) -> Receipt[B]:
        """
        Metered invocation of the wrapped agent.

        Implements the full transaction lifecycle.
        """
        # 1. Estimation Phase (The Quote)
        estimate = self.agent.estimate_cost(input)

        # 2. Authorization Phase (The Hold)
        try:
            lease = await self.bank.authorize(self.account_id, estimate)
        except InsufficientFundsError as e:
            raise e

        # 3. Execution Phase
        start_time = datetime.now()
        start_perf = time.perf_counter()

        try:
            result = await self.agent.invoke(input)
            duration_ms = (time.perf_counter() - start_perf) * 1000

            # 4. Settlement Phase (The Bill)
            # For now, use estimate as actual (real implementation would count tokens)
            actual_tokens = estimate
            gas = await self.bank.settle(lease, actual_tokens)
            gas.time_ms = duration_ms
            gas.model_multiplier = self.model_multiplier

            return Receipt(
                value=result,
                gas=gas,
                start_time=start_time,
                end_time=datetime.now(),
                duration_ms=duration_ms,
            )

        except Exception as e:
            # 5. Bankruptcy Protection (Rollback)
            await self.bank.void(lease)
            raise e


# =============================================================================
# Convenience Functions
# =============================================================================


def meter(
    agent: Agent[A, B],
    bank: Optional[CentralBank] = None,
    account_id: str = "default",
    model_multiplier: float = 1.0,
) -> Metered[A, B]:
    """
    Wrap an agent with metering.

    Usage:
        metered_agent = meter(my_agent)
        receipt = await metered_agent.invoke(input)
        print(f"Cost: ${receipt.gas.cost_usd:.4f}")
    """
    if bank is None:
        bank = CentralBank()

    return Metered(
        agent=agent,
        bank=bank,
        account_id=account_id,
        model_multiplier=model_multiplier,
    )


async def metered_invoke(
    agent: Agent[A, B],
    input: A,
    bank: Optional[CentralBank] = None,
    account_id: str = "default",
) -> Receipt[B]:
    """
    One-shot metered invocation.

    Usage:
        receipt = await metered_invoke(my_agent, my_input)
    """
    metered_agent = meter(agent, bank, account_id)
    return await metered_agent.invoke(input)
