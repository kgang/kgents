# The Metered Functor: Central Bank Economics

> Every token has a cost. The bank tracks, limits, and allocates.

---

## The Problem

"I am using a lot of tokens and I don't want to go bankrupt."

Token costs are real. Without economic constraints, agents will bankrupt their operators. We apply mechanics from auctions and fluid dynamics to create a **Central Bank** for agent economies.

---

## The Metered Functor

```python
class MeteredFunctor:
    """
    Wraps any agent with economic metering.

    Metered: Agent[A, B] → Agent[A, MeteredResult[B]]

    The wrapped agent tracks token usage, respects budgets,
    and participates in the economic system.
    """

    def lift(
        self,
        agent: Agent[A, B],
        budget: TokenBudget
    ) -> Agent[A, MeteredResult[B]]:
        return MeteredAgent(inner=agent, budget=budget)

@dataclass
class MeteredResult(Generic[T]):
    """Result with economic metadata."""
    value: T
    tokens_used: int
    tokens_remaining: int
    cost_usd: float
    budget_percentage: float
    model: str

    @property
    def is_over_budget(self) -> bool:
        return self.tokens_remaining < 0
```

---

## Token Budget

```python
@dataclass
class TokenBudget:
    """Economic constraints for an agent or pipeline."""
    max_tokens: int
    max_cost_usd: float
    remaining_tokens: int
    remaining_cost_usd: float
    priority: int = 0  # Higher = more important

    def can_afford(self, estimated_tokens: int, cost_per_token: float) -> bool:
        """Check if we can afford this operation."""
        estimated_cost = estimated_tokens * cost_per_token
        return (
            estimated_tokens <= self.remaining_tokens and
            estimated_cost <= self.remaining_cost_usd
        )

    def consume(self, tokens: int, cost: float) -> "TokenBudget":
        """Consume tokens and return updated budget."""
        return TokenBudget(
            max_tokens=self.max_tokens,
            max_cost_usd=self.max_cost_usd,
            remaining_tokens=self.remaining_tokens - tokens,
            remaining_cost_usd=self.remaining_cost_usd - cost,
            priority=self.priority
        )

    def split(self, n: int) -> list["TokenBudget"]:
        """Split budget among n sub-agents."""
        per_agent_tokens = self.remaining_tokens // n
        per_agent_cost = self.remaining_cost_usd / n
        return [
            TokenBudget(
                max_tokens=per_agent_tokens,
                max_cost_usd=per_agent_cost,
                remaining_tokens=per_agent_tokens,
                remaining_cost_usd=per_agent_cost,
                priority=self.priority
            )
            for _ in range(n)
        ]
```

---

## Kelvin's Circulation Theorem

In fluid dynamics, Kelvin's theorem states that circulation around a closed loop is conserved in an ideal fluid. Applied to agents:

> Tokens circulate through the system. Total tokens are conserved—they don't appear or disappear.

```python
@dataclass
class CirculationBudget:
    """
    Budget that circulates through a pipeline, conserved in total.

    If agent A spends 100 tokens, that 100 must come from somewhere
    and go somewhere—it doesn't appear or disappear.
    """
    total_circulation: int      # Total tokens in the system
    allocated: dict[str, int]   # agent_id → allocated tokens
    spent: dict[str, int]       # agent_id → spent tokens

    def reallocate(self, from_agent: str, to_agent: str, amount: int) -> None:
        """Transfer budget between agents (conservation)."""
        assert self.allocated[from_agent] >= amount, "Insufficient budget"
        self.allocated[from_agent] -= amount
        self.allocated[to_agent] = self.allocated.get(to_agent, 0) + amount
        # Total circulation unchanged

    def verify_conservation(self) -> bool:
        """Verify tokens are conserved."""
        allocated_total = sum(self.allocated.values())
        spent_total = sum(self.spent.values())
        return allocated_total + spent_total == self.total_circulation
```

---

## Auction Mechanics

When multiple agents compete for limited budget:

```python
@dataclass
class TokenRequest:
    """Request for tokens from the central bank."""
    agent_id: str
    requested: int
    min_acceptable: int  # Minimum to be useful
    value_estimate: float  # Expected value of the work
    urgency: float  # 0.0 to 1.0

    @property
    def value_per_token(self) -> float:
        return self.value_estimate / self.requested if self.requested > 0 else 0

class TokenAuction:
    """
    Agents bid for tokens from the central bank.

    Uses second-price (Vickrey) auction for truthful bidding.
    """

    async def allocate(
        self,
        requests: list[TokenRequest],
        available: int
    ) -> dict[str, int]:
        """
        Allocate tokens to agents based on:
        - Urgency (how important is this task?)
        - Efficiency (how many tokens per unit value?)
        - History (has this agent been wasteful?)
        """
        # Sort by value/token ratio (most efficient first)
        ranked = sorted(requests, key=lambda r: r.value_per_token, reverse=True)

        allocations = {}
        remaining = available

        for request in ranked:
            # Allocate up to requested, but at least min_acceptable
            if remaining >= request.min_acceptable:
                allocation = min(request.requested, remaining)
                allocations[request.agent_id] = allocation
                remaining -= allocation
            else:
                allocations[request.agent_id] = 0  # Can't meet minimum

            if remaining <= 0:
                break

        return allocations
```

---

## The Central Bank

```python
class CentralBank:
    """
    Manages the token economy for a kgents deployment.
    """
    total_budget: TokenBudget
    agent_accounts: dict[str, TokenBudget]
    transaction_log: list[Transaction]
    auction: TokenAuction

    async def request_tokens(
        self,
        agent_id: str,
        amount: int,
        justification: str
    ) -> TokenGrant | TokenDenial:
        """
        Agent requests tokens from the bank.

        Bank may grant, partially grant, or deny based on:
        - Available funds
        - Agent's history
        - Current priorities
        """
        account = self.agent_accounts.get(agent_id)

        if not account:
            return TokenDenial(reason="Agent not registered")

        if not account.can_afford(amount, self.cost_per_token):
            # Try to request from reserve
            reserve_grant = await self.request_from_reserve(
                agent_id, amount, justification
            )
            if not reserve_grant:
                return TokenDenial(
                    reason="Insufficient budget",
                    available=account.remaining_tokens
                )
            return reserve_grant

        # Grant from account
        self.agent_accounts[agent_id] = account.consume(
            amount, amount * self.cost_per_token
        )

        self.transaction_log.append(Transaction(
            agent_id=agent_id,
            amount=amount,
            type="grant",
            justification=justification,
            timestamp=datetime.now()
        ))

        return TokenGrant(
            amount=amount,
            remaining=self.agent_accounts[agent_id].remaining_tokens
        )

    async def report_usage(
        self,
        agent_id: str,
        actual_tokens: int,
        actual_cost: float
    ) -> None:
        """Report actual usage (may differ from requested)."""
        self.transaction_log.append(Transaction(
            agent_id=agent_id,
            amount=actual_tokens,
            cost=actual_cost,
            type="usage",
            timestamp=datetime.now()
        ))

    def audit(self) -> AuditReport:
        """Generate economic audit of all agent spending."""
        by_agent = defaultdict(lambda: {"tokens": 0, "cost": 0.0})

        for tx in self.transaction_log:
            if tx.type == "usage":
                by_agent[tx.agent_id]["tokens"] += tx.amount
                by_agent[tx.agent_id]["cost"] += tx.cost

        return AuditReport(
            total_tokens=sum(a["tokens"] for a in by_agent.values()),
            total_cost=sum(a["cost"] for a in by_agent.values()),
            by_agent=dict(by_agent),
            top_spenders=sorted(
                by_agent.items(),
                key=lambda x: x[1]["cost"],
                reverse=True
            )[:10]
        )
```

---

## Integration with Other Patterns

### With Ergodic Strategy

```python
# Ensemble size limited by economic budget
async def ergodic_with_budget(
    task: Task,
    budget: TokenBudget,
    cost_per_agent: int
) -> Result:
    max_instances = budget.remaining_tokens // cost_per_agent
    n_instances = min(desired_ensemble_size, max_instances)

    if n_instances < 2:
        # Can't afford ensemble, fall back to single agent
        return await single_agent.invoke(task)

    # Split budget among instances
    child_budgets = budget.split(n_instances)
    agents = [Agent.spawn_fresh() for _ in range(n_instances)]

    results = await asyncio.gather(*[
        MeteredFunctor().lift(a, b).invoke(task)
        for a, b in zip(agents, child_budgets)
    ])

    return select_best(results)
```

### With Entropy Budget

```python
# Both entropy and economic budgets constrain behavior
@dataclass
class DualBudget:
    entropy: EntropyBudget
    economic: TokenBudget

    def can_proceed(self, entropy_cost: float, token_cost: int) -> bool:
        return (
            self.entropy.can_afford(entropy_cost) and
            self.economic.can_afford(token_cost, COST_PER_TOKEN)
        )
```

---

## Metered Agent Implementation

```python
class MeteredAgent(Agent[A, MeteredResult[B]]):
    """
    Agent wrapped with economic metering.
    """

    def __init__(self, inner: Agent[A, B], budget: TokenBudget, bank: CentralBank):
        self.inner = inner
        self.budget = budget
        self.bank = bank

    async def invoke(self, input: A) -> MeteredResult[B]:
        # Estimate cost
        estimated_tokens = self.estimate_tokens(input)

        # Request from bank
        grant = await self.bank.request_tokens(
            self.inner.name,
            estimated_tokens,
            f"Invoke with input size {len(str(input))}"
        )

        if isinstance(grant, TokenDenial):
            raise BudgetExhaustedError(grant.reason)

        # Execute
        start = time.time()
        result = await self.inner.invoke(input)
        duration = time.time() - start

        # Report actual usage
        actual_tokens = self.count_tokens(input, result)
        actual_cost = actual_tokens * COST_PER_TOKEN

        await self.bank.report_usage(
            self.inner.name,
            actual_tokens,
            actual_cost
        )

        return MeteredResult(
            value=result,
            tokens_used=actual_tokens,
            tokens_remaining=grant.remaining - actual_tokens,
            cost_usd=actual_cost,
            budget_percentage=(actual_tokens / self.budget.max_tokens) * 100,
            model=self.inner.model_name
        )
```

---

## Visualization (GaugeWidget)

The economics integrates with the View Functor:

```
┌─ Budget Gauge ────────────────────────────────────┐
│                                                    │
│  Tokens:  ███████████████░░░░░░░░░░  62%          │
│  Cost:    ██████████░░░░░░░░░░░░░░░  41%          │
│                                                    │
│  Remaining: 38,000 tokens | $2.34                  │
│  Top spender: CodeReviewer (12,400 tokens)         │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## Anti-Patterns

- **Unbounded token usage**: Always set budgets
- **Agents that ignore budget constraints**: Enforce at bank level
- **Hidden costs**: All usage must be reported
- **No audit trail**: Log every transaction
- **Optimistic estimation**: Over-estimate, return unused
- **Single point of failure**: Budget denial should trigger fallback, not crash

---

*Zen Principle: The wise spender counts twice; the token spent is the token gone.*

---

## See Also

- [bootstrap.md](../bootstrap.md) - Entropy Budget (related constraint)
- [reliability.md](../reliability.md) - Fallback on budget exhaustion
- [i-gents/view-functor.md](../i-gents/view-functor.md) - GaugeWidget visualization
