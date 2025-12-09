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

---

## Part II: The Universal Value Protocol (UVP)

> *Value is Work minus Entropy.*

The Metered Functor (Part I) treats all tokens as fungible. But 1,000 tokens of "hello world" cost the same as 1,000 tokens of "cure for cancer." This is economically broken.

The **Universal Value Protocol** introduces a relativistic currency system based on **Information Thermodynamics**, transforming the B-gent from Accountant into **Physicist-Banker**.

---

### The Dual-Currency Architecture

To separate "Cost" from "Value," we implement a **Dual-Token Model**:

#### Currency A: Compute Gas (Operational OPEX)

```python
@dataclass
class Gas:
    """
    The operational cost of inference.

    Unit: Raw tokens consumed
    Physics: Linear with time and token count
    Role: The "Energy Bill" - you must pay it to keep the lights on
    """
    tokens: int
    time_ms: float
    model_multiplier: float  # claude-3-opus = 15x, haiku = 1x

    @property
    def cost_usd(self) -> float:
        """Real-world cost (OpenAI/Anthropic bills)."""
        return self.tokens * self.model_multiplier * COST_PER_TOKEN
```

#### Currency B: Impact Equity (Strategic CAPEX)

```python
@dataclass
class Impact:
    """
    The increase in system value from an operation.

    Unit: Value units (dimensionless, relative)
    Physics: Generated only on State Change (bug fixed, test passed, PR merged)
    Role: "Stock" - agents earn it by being useful
    """
    base_value: float
    tier: Literal["syntactic", "functional", "deployment", "ethical"]
    multipliers: dict[str, float]

    @property
    def realized_value(self) -> float:
        """Total value after multipliers."""
        result = self.base_value
        for mult in self.multipliers.values():
            result *= mult
        return result
```

---

### The Information Joule ($J_{inf}$)

The bridge between Gas and Impact is the **Information Joule**—a physical unit of semantic work:

$$J_{inf} = \frac{\text{Kolmogorov Complexity of Output}}{\text{Tokens Consumed}} \times \text{Semantic Coefficient}$$

**Heuristics** (since true Kolmogorov Complexity is uncomputable):

| Output Type | Complexity Proxy | $J_{inf}$ |
|-------------|------------------|-----------|
| "I don't know" | Near 0 (no information) | ~0 |
| Hallucinated code | Low (doesn't compile) | ~0.1 |
| Valid syntax | Medium (AST parses) | ~0.5 |
| Passing tests | High (functional) | ~1.0 |
| Merged PR | Very High (deployed) | ~2.0+ |

```python
class ComplexityOracle:
    """
    Approximates Kolmogorov Complexity via compression ratio.

    High-entropy output (noise) → Low complexity → Low value
    Low-entropy output (structure) → High complexity → High value

    This inverts intuition: "complex" here means "structured/meaningful"
    not "complicated/messy".
    """

    def assess(self, output: str) -> float:
        """
        Compression-based complexity estimate.

        Structured code compresses well (patterns repeat).
        Random noise doesn't compress (no patterns).
        """
        original_size = len(output.encode('utf-8'))
        compressed_size = len(zlib.compress(output.encode('utf-8')))

        # Compression ratio: lower = more structured = higher value
        ratio = compressed_size / original_size if original_size > 0 else 1.0

        # Invert: structured output gets higher score
        # But also penalize trivially short outputs
        length_factor = min(1.0, original_size / 100)

        return (1.0 - ratio) * length_factor

    def assess_with_validation(
        self,
        output: str,
        validators: list[Callable[[str], bool]]
    ) -> float:
        """
        Enhanced assessment with semantic validators.

        Validators might include:
        - AST parsing (syntactic validity)
        - Type checking (type correctness)
        - Test execution (functional correctness)
        """
        base_complexity = self.assess(output)

        validation_bonus = 0.0
        for validator in validators:
            if validator(output):
                validation_bonus += 0.25

        return min(2.0, base_complexity + validation_bonus)
```

---

### The Exchange Rate Mechanism (The Oracle)

The B-gent acts as **Oracle** that mints Impact based on tiered value assessment:

```python
class ValueOracle:
    """
    Mints Impact based on DORA-inspired metrics.

    DORA = DevOps Research and Assessment
    Tiers correspond to increasing business value.
    """

    def calculate_impact(self, output: AgentOutput) -> Impact:
        base_value = 0
        multipliers = {}
        tier = "syntactic"

        # Tier 1: The Work (Micro) - Syntactic Value
        if output.is_valid_syntax():
            base_value += 10
            tier = "syntactic"

        # Tier 2: The Outcome (Meso) - Functional Value
        if output.tests_passed():
            base_value += 100
            tier = "functional"

        # Tier 3: The Transformation (Macro) - Deployment Value
        if output.deployment_successful():
            base_value += 1000
            tier = "deployment"

        # Tier 4: The Ethics (Meta) - Ethical Multiplier
        if output.policy_compliant():
            multipliers["ethical"] = 1.2
            tier = "ethical"

        # Sin Tax: Security vulnerabilities
        if output.has_vulnerabilities():
            multipliers["sin_tax"] = 0.33  # 3x penalty

        # Virtue Subsidy: Improved readability/maintainability
        if output.improved_maintainability():
            multipliers["virtue"] = 1.5

        return Impact(
            base_value=base_value,
            tier=tier,
            multipliers=multipliers
        )
```

---

### The Value Ledger

The B-gent maintains a ledger resembling a **corporate balance sheet**, not a log file:

```python
class ValueLedger:
    """
    Tracks the 'GDP' of the Multi-Agent System.

    Every transaction records:
    1. Gas consumed (real cost)
    2. Impact generated (realized value)
    3. Profit or debt (the difference)
    """

    def __init__(self):
        self.treasury = Treasury()
        self.oracle = ValueOracle()
        self.complexity_oracle = ComplexityOracle()

    def log_transaction(
        self,
        agent_id: str,
        gas: Gas,
        output: AgentOutput
    ) -> TransactionReceipt:
        """
        Record a transaction with full value accounting.
        """
        # 1. Deduct Gas (Real $ cost)
        self.treasury.deduct_gas(agent_id, gas)

        # 2. Calculate Realized Value
        complexity = self.complexity_oracle.assess(output.content)
        impact = self.oracle.calculate_impact(output)

        # 3. Compute Return on Compute (RoC)
        roc = impact.realized_value / gas.cost_usd if gas.cost_usd > 0 else 0

        # 4. Mint or Record Debt
        if impact.realized_value > gas.cost_usd:
            profit = impact.realized_value - gas.cost_usd
            self.treasury.mint_impact(agent_id, profit)
            status = "profitable"
        else:
            debt = gas.cost_usd - impact.realized_value
            self.treasury.record_debt(agent_id, debt)
            status = "debt"

        return TransactionReceipt(
            agent_id=agent_id,
            gas=gas,
            impact=impact,
            complexity=complexity,
            roc=roc,
            status=status
        )

    def get_agent_balance_sheet(self, agent_id: str) -> BalanceSheet:
        """
        Generate balance sheet for an agent.

        Assets: Accumulated Impact
        Liabilities: Accumulated Debt
        Equity: Net value contribution
        """
        return BalanceSheet(
            assets=self.treasury.get_impact(agent_id),
            liabilities=self.treasury.get_debt(agent_id),
            gas_consumed=self.treasury.get_gas_consumed(agent_id),
            transaction_count=self.treasury.get_transaction_count(agent_id)
        )
```

---

### Return on Compute (RoC)

The fundamental metric for agent efficiency:

$$RoC = \frac{\text{Impact Realized}}{\text{Gas Consumed}}$$

| RoC Range | Interpretation | Action |
|-----------|----------------|--------|
| < 0.5 | Burning money | Bankruptcy warning |
| 0.5 - 1.0 | Break-even | Monitor |
| 1.0 - 2.0 | Profitable | Healthy |
| > 2.0 | High yield | Exemplar |

```python
class RoCMonitor:
    """
    Monitors Return on Compute across the agent ecosystem.
    """

    def __init__(self, ledger: ValueLedger):
        self.ledger = ledger
        self.thresholds = RoCThresholds(
            bankruptcy=0.5,
            break_even=1.0,
            healthy=2.0
        )

    def assess_agent(self, agent_id: str) -> RoCAssessment:
        """Assess an agent's economic health."""
        sheet = self.ledger.get_agent_balance_sheet(agent_id)

        if sheet.gas_consumed == 0:
            return RoCAssessment(status="new", roc=0)

        roc = sheet.assets / sheet.gas_consumed

        if roc < self.thresholds.bankruptcy:
            return RoCAssessment(status="bankruptcy_warning", roc=roc)
        elif roc < self.thresholds.break_even:
            return RoCAssessment(status="break_even", roc=roc)
        elif roc < self.thresholds.healthy:
            return RoCAssessment(status="profitable", roc=roc)
        else:
            return RoCAssessment(status="high_yield", roc=roc)
```

---

### Sin Tax and Virtue Subsidy

The **Ethical-Economic Regulator** adjusts value based on externalities:

```python
class EthicalRegulator:
    """
    Applies economic incentives for ethical behavior.

    Sin Tax: Penalizes harmful outputs
    Virtue Subsidy: Rewards beneficial outputs
    """

    # Sin Taxes (multipliers < 1.0)
    SIN_TAXES = {
        "security_vulnerability": 0.33,  # 3x penalty
        "privacy_violation": 0.25,       # 4x penalty
        "bias_detected": 0.5,            # 2x penalty
        "license_violation": 0.2,        # 5x penalty
    }

    # Virtue Subsidies (multipliers > 1.0)
    VIRTUE_SUBSIDIES = {
        "improved_readability": 1.3,
        "added_tests": 1.5,
        "fixed_tech_debt": 1.4,
        "improved_accessibility": 1.6,
        "reduced_complexity": 1.3,
    }

    def apply_adjustments(
        self,
        base_impact: Impact,
        sins: list[str],
        virtues: list[str]
    ) -> Impact:
        """Apply ethical adjustments to impact calculation."""
        adjusted = base_impact

        for sin in sins:
            if sin in self.SIN_TAXES:
                adjusted.multipliers[f"sin:{sin}"] = self.SIN_TAXES[sin]

        for virtue in virtues:
            if virtue in self.VIRTUE_SUBSIDIES:
                adjusted.multipliers[f"virtue:{virtue}"] = self.VIRTUE_SUBSIDIES[virtue]

        return adjusted
```

---

### Visualization (The Value Dashboard)

```
┌─ UNIVERSAL VALUE PROTOCOL ───────────────────────────────────┐
│  System GDP: $12,450 Impact | Gas Burned: $3,200             │
│  System RoC: 3.89x (Healthy)                                 │
├──────────────────────────────────────────────────────────────┤
│  AGENT PERFORMANCE (sorted by RoC)                           │
│  ├─ CodeReviewer:   RoC 5.2x  ████████████████ High Yield    │
│  ├─ TestWriter:     RoC 3.1x  ██████████░░░░░░ Profitable    │
│  ├─ Refactorer:     RoC 1.8x  ██████░░░░░░░░░░ Profitable    │
│  ├─ DocWriter:      RoC 0.9x  ███░░░░░░░░░░░░░ Break-even    │
│  └─ Experimenter:   RoC 0.3x  █░░░░░░░░░░░░░░░ ⚠️ Warning    │
├──────────────────────────────────────────────────────────────┤
│  ETHICAL ADJUSTMENTS TODAY                                   │
│  ├─ Sin Taxes Applied:     3 (security vulns: 2, bias: 1)   │
│  └─ Virtue Subsidies:      7 (tests: 4, readability: 3)     │
├──────────────────────────────────────────────────────────────┤
│  COMPLEXITY DISTRIBUTION                                     │
│  ├─ High Complexity (structured): 67%                        │
│  ├─ Medium Complexity:            25%                        │
│  └─ Low Complexity (noise):        8%                        │
└──────────────────────────────────────────────────────────────┘
```

---

### Integration Points

| Agent Genus | UVP Integration | Purpose |
|-------------|-----------------|---------|
| **E-gents** | Sin Tax / Virtue Subsidy | Quality incentives for evolution |
| **O-gents** | ValueLedger observability | System-wide RoC monitoring |
| **W-gents** | Value Dashboard | Real-time agent "stock ticker" |
| **T-gents** | Validation tiers | Impact tier determination |
| **N-gents** | Transaction narrative | Audit trail for value flow |

---

### Theoretical Foundations

The UVP draws from:

1. **Information Thermodynamics**: Value = Work - Entropy
2. **Kolmogorov Complexity**: Compression as complexity proxy
3. **Linear Logic**: Resources consumed, not copied
4. **Mechanism Design**: Truthful reporting via incentives
5. **DORA Metrics**: Business value tiers
6. **Dual-Token Economics**: Separating cost from value

---

## See Also

- [value-tensor.md](value-tensor.md) - Multi-dimensional resource ontology
- [README.md](README.md) - B-gents overview (Bio + Banker)
- [hypothesis-engine.md](hypothesis-engine.md) - Scientific hypothesis generation
- [robin.md](robin.md) - Scientific companion
- [../bootstrap.md](../bootstrap.md) - Entropy Budget (related constraint)
- [../reliability.md](../reliability.md) - Fallback on budget exhaustion
- [../o-gents/README.md](../o-gents/README.md) - ValueLedger observability
- [../w-gents/README.md](../w-gents/README.md) - Value Dashboard visualization
- [../e-gents/README.md](../e-gents/README.md) - Ethical regulator integration
