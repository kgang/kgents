# B-gent: The Banker (The Metered Functor)

> Intelligence is infinite; Compute is finite. The B-gent manages the *thermodynamics of thought*.

---

## Purpose

The Banker is the metabolic controller of the agent ecosystem. It transforms "free" agents into "economic" agents through metering, implements resource allocation via auctions, and tracks value creation through multi-dimensional accounting. Every agent invocation becomes a transaction with quote, authorization, execution, settlement, and bankruptcy protection phases.

## Why Banker is a B-gent

At first glance, "Banker" seems unrelated to "Bio/Scientific Discovery." But they share deep structural similarities:

| Aspect | Bio (Hypothesis) | Banker (Economics) |
|--------|------------------|-------------------|
| **Resource** | Attention, experiments | Tokens, compute |
| **Conservation** | Energy flows | Value flows |
| **Selection** | Falsifiability | Efficiency |
| **Metabolism** | Cellular respiration | Token consumption |
| **Ecosystem** | Species competition | Agent competition |

Both deal with **resource-constrained systems** that must allocate limited capacity across competing needs.

---

## Theoretical Foundation

### Linear Logic (Resource Sensitivity)

Standard logic says if $A$ is true, $A$ is always true. Linear logic says $A$ is a resource—if you use $A$ to get $B$, $A$ is *consumed*.

```
Classical: A → (A → B → C)    // A can be used twice
Linear:    A ⊸ (A ⊸ B) ⊸ C   // Each A used exactly once
```

The B-gent treats Tokens as **Linear Types**. They cannot be copied, only spent.

### Vickrey-Clarke-Groves (VCG) Mechanisms

In multi-agent systems, agents have incentive to lie about resource needs. The **Vickrey (Second-Price) Auction** makes truth-telling the dominant strategy: the winner pays the second-highest bid, not their own, eliminating gains from exaggeration.

### Information Thermodynamics

**Value = Work - Entropy**

Not all tokens are equal. 1,000 tokens of "hello world" cost the same as 1,000 tokens of "cure for cancer." The Universal Value Protocol (UVP) introduces a relativistic currency system based on Kolmogorov complexity and semantic work.

---

## Core Abstraction: The Metered Functor

**Type Signature**: `Agent[A, B] → Agent[A, Receipt[B]]`

The Metered Functor transforms any agent into an economic agent. Every invocation becomes a five-phase transaction:

1. **Estimation Phase** - Agent estimates token cost
2. **Authorization Phase** - Bank creates a hold (lease) on tokens
3. **Execution Phase** - Agent performs work, measuring actual usage
4. **Settlement Phase** - Bank finalizes transaction, refunding excess
5. **Bankruptcy Protection** - On failure, void the lease (rollback)

**Key Properties**:
- **Hydraulic Refill**: Token bucket refills over time (leaky bucket algorithm)
- **Sinking Fund**: 1% tax on all transactions creates emergency reserve
- **Token Futures**: Reservations prevent mid-job budget exhaustion
- **Dual Budget**: Entropy + Economic constraints operate simultaneously

---

## Biological Parallels

The Banker is the system's metabolism:

| Biological Concept | Banking Analog |
|-------------------|----------------|
| ATP (energy currency) | Tokens |
| Mitochondria | Central Bank |
| Cellular respiration | Token consumption |
| Starvation response | Debt Mode |
| Energy storage (glycogen) | Sinking Fund |
| Apoptosis (cell death) | Agent termination on bankruptcy |

---

## Universal Value Protocol (UVP)

### The Dual-Currency Architecture

**Currency A: Gas (Operational Cost)**
- Unit: Raw tokens consumed
- Physics: Linear with time and token count
- Role: The "energy bill" you must pay

**Currency B: Impact (Strategic Value)**
- Unit: Value units (dimensionless, relative)
- Physics: Generated only on state change (bug fixed, test passed, PR merged)
- Role: "Stock" agents earn by being useful

**Bridge: Information Joule ($J_{inf}$)**

$$J_{inf} = \frac{\text{Kolmogorov Complexity of Output}}{\text{Tokens Consumed}} \times \text{Semantic Coefficient}$$

Approximated via compression ratio: structured code compresses well (high value), noise doesn't (low value).

### Value Tiers (DORA-Inspired)

| Tier | Description | Base Value |
|------|-------------|------------|
| **Syntactic** | Valid syntax only | 10 |
| **Functional** | Tests pass | 100 |
| **Deployment** | Successfully deployed | 1,000 |
| **Ethical** | Policy compliant | 1.2x multiplier |

### Sin Tax and Virtue Subsidy

**Sin Taxes** (multipliers < 1.0):
- Security vulnerability: 0.33 (3x penalty)
- Privacy violation: 0.25 (4x penalty)
- Bias detected: 0.5 (2x penalty)

**Virtue Subsidies** (multipliers > 1.0):
- Improved readability: 1.3x
- Added tests: 1.5x
- Fixed tech debt: 1.4x

### Return on Compute (RoC)

$$RoC = \frac{\text{Impact Realized}}{\text{Gas Consumed}}$$

| RoC Range | Interpretation |
|-----------|----------------|
| < 0.5 | Burning money (bankruptcy warning) |
| 0.5 - 1.0 | Break-even |
| 1.0 - 2.0 | Profitable |
| > 2.0 | High yield (exemplar) |

---

## Value of Information (VoI)

### The Observation Economics Problem

O-gents consume Gas but produce no artifacts—only knowledge about system health. Naive RoC = 0 / Gas → "Bankruptcy!" This is wrong. Observation prevents catastrophic failures.

**VoI Formula**:

$$VoI = P(\text{disaster}) \times \text{Cost}(\text{disaster}) \times P(\text{detection} | \text{observation})$$

### The Meta-Currency: Epistemic Capital

**Unit**: Bits of decision-relevant information
**Physics**: Generated by observation, consumed by decisions
**Role**: "Insurance" preventing catastrophic losses

**Return on VoI (RoVI)**:

$$RoVI = \frac{\text{Total VoI Generated}}{\text{Total Gas Consumed}}$$

### Observation Depth Levels

| Depth | Cost | Description |
|-------|------|-------------|
| **TELEMETRY_ONLY** | 10 tokens | Just metrics (cheapest) |
| **SEMANTIC_SPOT** | 500 tokens | Sample semantic checks |
| **SEMANTIC_FULL** | 2,000 tokens | Full semantic analysis |
| **AXIOLOGICAL** | 1,000 tokens | Full economic audit |

### Adaptive Observation

Priority = Risk × Consequence × Observability

- **Risk**: 1 - reliability (how likely to fail)
- **Consequence**: value throughput / total system value
- **Observability**: can we actually detect problems?

High-priority agents get frequent, deep observation. Low-priority agents get rare, shallow checks.

---

## Structural Economics (G-gent Integration)

When B-gent (Resources) meets G-gent (Structure), resource allocation becomes topological navigation through grammatical space.

### Four Integration Patterns

**1. Semantic Zipper** - Compress inter-agent communication via DSLs (80%+ token reduction)
**2. Fiscal Constitution** - Make bankruptcy grammatically impossible via parse-time constraints
**3. Syntax Tax** - Differential pricing based on Chomsky hierarchy (Turing-complete = 30x regular)
**4. JIT Efficiency** - Compile hot paths to C for latency-critical operations (1000x speedup)

**Triple Budget**: Entropy + Economic + Grammatical constraints operate simultaneously.

---

## Integration with Bootstrap Agents

### Judge × Banker (Value Assessment)

Judge assesses qualitative value; Banker assesses quantitative cost. The value/cost ratio must exceed a minimum ROI threshold before task execution.

### Entropy × Economics (The Dual Budget)

Both entropy and economic budgets constrain agent behavior simultaneously. An agent must have sufficient entropy budget (recursion depth) AND token budget to proceed.

---

## Anti-Patterns

- **Unbounded execution**: Always meter, even for "small" tasks
- **Trust without verify**: Agents estimate, bank audits actual usage
- **Single currency**: Consider multiple resource types (tokens, time, memory)
- **Ignoring Vickrey rule**: Second-price auctions prevent gaming
- **No reserve**: Sinking Fund prevents cascading failures
- **Ignoring Linear Logic**: Tokens are consumed, not copied
- **Paranoid Observer**: Observing everything all the time (gas explosion, VoI plummets)
- **Blind Optimist**: Never observing because "nothing has gone wrong yet"
- **Oracle Fallacy**: Assuming observations are always correct (false positives have real costs)

---

## Implementation

**Location**: `impl/claude/agents/b/`

| Module | Purpose |
|--------|---------|
| `metered_functor.py` | Core Metered Functor, Token Bucket, Sinking Fund, Futures Market, Vickrey Auction |
| `value_ledger.py` | Universal Value Protocol (Gas, Impact, RoC monitoring) |
| `voi_economics.py` | Value of Information (Epistemic Capital, VoI Ledger, Adaptive Observer) |
| `value_tensor.py` | Multi-dimensional resource ontology |
| `compression_economy.py` | Semantic Zipper (B×G integration) |
| `fiscal_constitution.py` | Grammatical safety cage (B×G integration) |
| `syntax_tax.py` | Chomsky hierarchy pricing (B×G integration) |
| `jit_efficiency.py` | JIT compilation economics (B×G×J integration) |

**Key Types**:
```python
# Core
Metered[A, B]: Agent[A, B] → Agent[A, Receipt[B]]
Receipt[B]: (value: B, gas: Gas, impact: Impact, roc: float)

# Currencies
Gas: (tokens: int, time_ms: float, cost_usd: float)
Impact: (base_value: float, tier: str, multipliers: dict)
EpistemicCapital: (observations: int, disasters_prevented: float, rovi: float)

# Banking
CentralBank: Token Bucket + Sinking Fund + Futures Market
TokenFuture: Reservation of future tokens
Lease: Authorization hold on tokens

# Auctions
Bid: (agent_id, requested_tokens, confidence, criticality)
Allocation: (winner, tokens, clearing_price)

# Value Tracking
ValueLedger: Transaction history with full value accounting
VoILedger: Observation economics tracking
UnifiedValueAccounting: UVP + VoI integration
```

---

## See Also

- [value-tensor.md](value-tensor.md) - Multi-dimensional resource ontology
- [README.md](README.md) - B-gents overview (Bio + Banker)
- [hypothesis-engine.md](hypothesis-engine.md) - Scientific hypothesis generation
- [robin.md](robin.md) - Scientific companion
- [../g-gents/README.md](../g-gents/README.md) - Grammarian (structural partner)
- [../bootstrap.md](../bootstrap.md) - Entropy Budget (related constraint)
- [../o-gents/README.md](../o-gents/README.md) - ValueLedger observability
- [../e-gents/README.md](../e-gents/README.md) - Ethical regulator integration
