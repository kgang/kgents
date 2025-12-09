# B-gent: The Banker (The Metered Functor)

> Intelligence is infinite; Compute is finite. The B-gent does not just count beans; it manages the *thermodynamics of thought*.

---

## Why Banker is a B-gent

At first glance, "Banker" seems unrelated to "Bio/Scientific Discovery." But they share deep structural similarities:

| Aspect | Bio (Hypothesis) | Banker (Economics) |
|--------|------------------|-------------------|
| **Resource** | Attention, experiments | Tokens, compute |
| **Conservation** | Energy flows | Value flows |
| **Selection** | Falsifiability | Efficiency |
| **Metabolism** | Cellular respiration | Token consumption |
| **Ecosystem** | Species competition | Agent competition |

Both deal with **resource-constrained systems** that must allocate limited capacity across competing needs. The Banker is the metabolic controller of the agent ecosystem.

---

## Theoretical Foundation

### Linear Logic (Resource Sensitivity)

Standard logic says if $A$ is true, $A$ is always true. Linear logic says $A$ is a resource. If you use $A$ to get $B$, $A$ is *consumed*.

```
Classical: A → (A → B → C)    // A can be used twice
Linear:    A ⊸ (A ⊸ B) ⊸ C   // Each A used exactly once
```

The B-gent treats Tokens as **Linear Types**. They cannot be copied, only spent.

### Vickrey-Clarke-Groves (VCG) Mechanisms

In a multi-agent system, agents have incentive to lie ("I need 1M tokens to fix this typo!"). We must design the auction so that **truth-telling is the dominant strategy**.

The **Vickrey (Second-Price) Auction**: The winner pays the second-highest bid, not their own. This makes truthful bidding optimal—you can't gain by exaggerating.

---

## The Core Abstraction: The Metered Functor

The Metered Functor transforms any "free" agent into an "economic" agent:

```python
class Metered(Generic[A, B]):
    """
    The Metered Functor transforms an Agent into a Transaction.

    Type: Agent[A, B] → Agent[A, Receipt[B]]
    """
    def __init__(self, agent: Agent[A, B], account_id: str):
        self.agent = agent
        self.account_id = account_id

    async def invoke(self, input: A) -> Receipt[B]:
        # 1. Estimation Phase (The Quote)
        estimate = self.agent.estimate_cost(input)

        # 2. Authorization Phase (The Hold)
        # Raises InsufficientFundsError if rejected
        lease = await CentralBank.authorize(self.account_id, estimate)

        try:
            # 3. Execution Phase
            start_t = time.perf_counter()
            result = await self.agent.invoke(input)
            duration = time.perf_counter() - start_t

            # 4. Settlement Phase (The Bill)
            actual_cost = self.calculate_cost(input, result, duration)
            receipt = await CentralBank.settle(lease, actual_cost)

            return Receipt(value=result, meta=receipt)

        except Exception as e:
            # 5. Bankruptcy Protection (Rollback)
            await CentralBank.void(lease)
            raise e
```

---

## The Central Bank (The Hydraulic System)

Instead of a simple counter, the Central Bank acts as a **Hydraulic Controller**. It implements **Kelvin's Circulation Theorem**: *The flow of value must be conserved.*

### The "Leaky Bucket" Rate Limiter

We use the Token Bucket algorithm (standard in network engineering) to manage "burstiness":

```python
class Account:
    def __init__(self, max_balance: int, refill_rate: int):
        self.balance = max_balance
        self.max = max_balance
        self.refill_rate = refill_rate  # Tokens per second
        self.last_update = time.time()

    def refresh(self):
        """Hydraulic refill: Time = Money"""
        now = time.time()
        delta = now - self.last_update
        inflow = delta * self.refill_rate
        self.balance = min(self.max, self.balance + inflow)
        self.last_update = now
```

### The "Sinking Fund" (Insurance)

Every transaction pays a 1% "Tax" to the System Reserve.

**Purpose**: If a critical agent (like a `Fixer`) hits `0` budget but *must* run to save the system, the Bank grants an emergency loan from the Sinking Fund.

**Constraint**: The agent enters "Debt Mode" (reduced capabilities) until the loan is repaid.

```python
class SinkingFund:
    """
    The system's insurance reserve.
    """
    reserve: float = 0.0
    tax_rate: float = 0.01  # 1% of all transactions

    def tax(self, amount: float) -> float:
        """Collect tax from transaction."""
        tax = amount * self.tax_rate
        self.reserve += tax
        return amount - tax

    async def emergency_loan(self, agent_id: str, amount: float) -> Loan | Denial:
        """Grant emergency loan from reserve."""
        if amount > self.reserve:
            return Denial(reason="Insufficient reserve")

        self.reserve -= amount
        return Loan(
            agent_id=agent_id,
            amount=amount,
            terms=DebtModeTerms()  # Reduced capabilities until repaid
        )
```

---

## The Auction: Solving Resource Contention

When multiple agents compete for limited tokens, the Bank triggers a **Priority Auction**.

**The Mechanism**: The "Second-Price Sealed-Bid" (Vickrey Auction).

```python
async def priority_auction(bids: list[Bid]) -> Allocation:
    """
    Vickrey auction: Winner pays second-highest price.

    This mathematically proves that agents are incentivized
    to report their *true* confidence, preventing "Priority Inflation."
    """
    # Sort by Bid Value (Confidence × Criticality)
    sorted_bids = sorted(bids, key=lambda x: x.value, reverse=True)

    winner = sorted_bids[0]
    runner_up = sorted_bids[1] if len(bids) > 1 else Bid(0)

    # Winner pays the Runner Up's price (Vickrey Rule)
    clearing_price = runner_up.value

    return Allocation(winner=winner.agent_id, price=clearing_price)
```

**Example**:
- Agent A (Research) bids 0.9 confidence ("I really need this")
- Agent B (Writing) bids 0.5 confidence ("It would help")
- Agent A wins, but pays 0.5 (Agent B's bid)
- Since A would have won anyway, truthful bidding was optimal

---

## Biological Parallels

The Banker is the system's metabolism:

| Biological Concept | Banking Analog |
|-------------------|----------------|
| ATP (energy currency) | Tokens |
| Mitochondria | Central Bank |
| Cellular respiration | Token consumption |
| Metabolism | Transaction flow |
| Starvation response | Debt Mode |
| Energy storage (glycogen) | Sinking Fund |
| Apoptosis (cell death) | Agent termination on bankruptcy |

---

## Integration with Bootstrap Agents

### Entropy × Economics (The Dual Budget)

Both entropy and economic budgets constrain agent behavior:

```python
@dataclass
class DualBudget:
    """
    Two conservation laws operating simultaneously.

    Entropy: Controls recursive depth (prevents fork bombs)
    Economic: Controls resource consumption (prevents bankruptcy)
    """
    entropy: EntropyBudget
    economic: TokenBudget

    def can_proceed(self, entropy_cost: float, token_cost: int) -> bool:
        return (
            self.entropy.can_afford(entropy_cost) and
            self.economic.can_afford(token_cost, COST_PER_TOKEN)
        )

    def spend(self, entropy_cost: float, token_cost: int) -> "DualBudget":
        return DualBudget(
            entropy=self.entropy.consume(entropy_cost),
            economic=self.economic.consume(token_cost, token_cost * COST_PER_TOKEN)
        )
```

### Judge × Banker (Value Assessment)

Judge assesses qualitative value; Banker assesses quantitative cost:

```python
async def value_aware_execution(
    task: Task,
    judge: Judge,
    bank: CentralBank
) -> Result:
    # Judge estimates value
    value_estimate = await judge.estimate_value(task)

    # Bank checks affordability
    cost_estimate = bank.estimate_cost(task)

    # Value/cost ratio must exceed threshold
    if value_estimate / cost_estimate < MINIMUM_ROI:
        return Denial(reason="Task not worth the cost")

    # Proceed with metered execution
    return await Metered(task.agent, bank).invoke(task.input)
```

---

## The Options Market (Futures)

A frontier concept for long-running jobs:

**Problem**: An agent starts a 50-step task. At step 49, the budget runs out. The work is lost.

**Solution**: Token Futures.

```python
@dataclass
class TokenFuture:
    """
    A reservation of future tokens.

    Like a financial option, this reserves capacity
    without consuming it until needed.
    """
    reserved_tokens: int
    holder: str
    expires_at: datetime
    exercise_price: float  # Premium paid for reservation

class FuturesMarket:
    async def buy_option(
        self,
        agent_id: str,
        tokens: int,
        duration: timedelta
    ) -> TokenFuture:
        """
        Buy a call option for tokens.

        The bank *reserves* that capacity.
        The agent pays a premium for the reservation.
        """
        premium = self.calculate_premium(tokens, duration)
        await self.bank.charge(agent_id, premium)

        return TokenFuture(
            reserved_tokens=tokens,
            holder=agent_id,
            expires_at=datetime.now() + duration,
            exercise_price=premium
        )

    async def exercise(self, future: TokenFuture) -> TokenGrant:
        """Exercise the option to get the reserved tokens."""
        if datetime.now() > future.expires_at:
            raise ExpiredOption()

        return await self.bank.grant(
            future.holder,
            future.reserved_tokens,
            justification="Exercising futures contract"
        )
```

**Impact**: This ensures **Atomic Economics**. Either you have the budget for the *whole* job, or you don't start.

---

## Visualization

```
┌─ THE CENTRAL BANK ───────────────────────────────────────┐
│  Global Reserves: $5.42 (▼ $0.12/hr)                     │
│  Sinking Fund:    $0.34 (1% tax)                         │
│  Entropy Tax Rate: 1.5%                                  │
├──────────────────────────────────────────────────────────┤
│  ACTIVE LEASES                                           │
│  ├─ ResearchAgent:  [██████░░░░] 600tk (Pending)         │
│  ├─ CoderAgent:     [██░░░░░░░░] 200tk (Settled)         │
│  └─ CriticAgent:    [DEBT MODE ] (Loan: 150tk)           │
├──────────────────────────────────────────────────────────┤
│  FUTURES MARKET                                          │
│  ├─ AnalysisJob:    5000tk reserved (expires 2hr)        │
│  └─ RefactorJob:    2000tk reserved (expires 30min)      │
├──────────────────────────────────────────────────────────┤
│  MARKET SIGNALS                                          │
│  » High Congestion detected. Surcharging low-priority.   │
└──────────────────────────────────────────────────────────┘
```

---

## Anti-Patterns

- **Unbounded execution**: Always meter, even for "small" tasks
- **Trust without verify**: Agents should estimate, bank should audit
- **Single currency**: Consider multiple resource types (tokens, time, memory)
- **Ignoring the Vickrey rule**: Second-price auctions prevent gaming
- **No reserve**: The Sinking Fund prevents cascading failures
- **Ignoring the Linear Logic**: Tokens are consumed, not copied

---

*Zen Principle: The wise spender counts twice; the token spent is the token gone.*

---

## See Also

- [README.md](README.md) - B-gents overview (Bio + Banker)
- [hypothesis-engine.md](hypothesis-engine.md) - Scientific hypothesis generation
- [robin.md](robin.md) - Scientific companion
- [../bootstrap.md](../bootstrap.md) - Entropy Budget (related constraint)
- [../reliability.md](../reliability.md) - Fallback on budget exhaustion
