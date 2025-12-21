# B-gent: The Banker

> *Intelligence is infinite; Compute is finite. The Banker manages the thermodynamics of thought.*

---

## The Core Insight

The Metered Functor transforms any agent into an economic agent:

```
Metered: Agent[A, B] → Agent[A, Receipt[B]]
```

Every invocation becomes a transaction with cost tracking, authorization, and settlement.

---

## The Banker Archetype

The Banker is the metabolic controller of the agent ecosystem. Like a cell's mitochondria or an economy's central bank, it:

1. **Tracks flows**: Tokens consumed, time elapsed, value created
2. **Enforces conservation**: Cannot spend more than allocated
3. **Applies selection pressure**: Inefficient agents starve
4. **Enables metabolism**: Transform resources into useful work

### Biological Parallel

| Biological Concept | Banking Analog |
|-------------------|----------------|
| ATP (energy currency) | Tokens |
| Mitochondria | Central Bank |
| Cellular respiration | Token consumption |
| Starvation response | Debt Mode |
| Energy storage (glycogen) | Sinking Fund |
| Apoptosis (cell death) | Agent termination on bankruptcy |

---

## Three Currencies

### 1. Gas (What You Spend)

```python
@dataclass
class Gas:
    """The operational cost of agent execution."""
    tokens: int              # Input + output tokens
    time_ms: float           # Wall clock time
    cost_usd: float          # Dollar cost
```

Gas is the "energy bill"—tokens consumed regardless of outcome.

### 2. Impact (What You Create)

```python
@dataclass
class Impact:
    """The value created by agent execution."""
    base_value: float        # Raw utility units
    tier: str                # syntactic | functional | deployment
    multiplier: float        # Ethical adjustments (sin tax / virtue subsidy)
```

Impact is generated only on meaningful state change: bug fixed, test passed, PR merged.

**Value Tiers**:
| Tier | Description | Base Value |
|------|-------------|------------|
| Syntactic | Valid syntax only | 10 |
| Functional | Tests pass | 100 |
| Deployment | Successfully deployed | 1,000 |

**Ethical Multipliers**:
- Sin taxes: Security vulnerability (0.33x), Privacy violation (0.25x)
- Virtue subsidies: Added tests (1.5x), Fixed tech debt (1.4x)

### 3. RoC (Return on Compute)

```
RoC = Impact / Gas
```

| RoC Range | Interpretation |
|-----------|----------------|
| < 0.5 | Burning money (bankruptcy warning) |
| 0.5 - 1.0 | Break-even |
| 1.0 - 2.0 | Profitable |
| > 2.0 | High yield (exemplar) |

---

## The Metered Functor

### Five-Phase Transaction

1. **Estimation**: Agent estimates token cost
2. **Authorization**: Bank creates hold (lease) on tokens
3. **Execution**: Agent performs work, measuring actual usage
4. **Settlement**: Bank finalizes, refunds excess
5. **Bankruptcy Protection**: On failure, void the lease (rollback)

### Key Mechanisms

**Token Bucket**: Hydraulic refill—tokens regenerate over time (leaky bucket algorithm).

**Sinking Fund**: 1% tax on all transactions creates emergency reserve.

**Token Futures**: Reservations prevent mid-job budget exhaustion.

### Type Signature

```python
@dataclass
class Receipt(Generic[B]):
    """The output of a metered agent."""
    value: B              # The actual result
    gas: Gas              # What was spent
    impact: Impact        # What was created
    roc: float            # Return on Compute
    lease_id: str         # For audit trail

Metered: Agent[A, B] → Agent[A, Receipt[B]]
```

---

## Linear Logic Foundation

Standard logic: If A is true, A is always true.
Linear logic: A is a resource—if you use A to get B, A is *consumed*.

```
Classical: A → (A → B → C)    // A can be used twice
Linear:    A ⊸ (A ⊸ B) ⊸ C   // Each A used exactly once
```

The Banker treats tokens as **linear types**: consumed, not copied.

---

## Distillation Economics

> *Genius is expensive. Routine should be cheap.*

The ROI formula for knowledge distillation:

```
         (Cost_Teacher - Cost_Student) × N_calls - Cost_Training
ROI = ─────────────────────────────────────────────────────────────
                          Cost_Training

Break-Even Point:
              Cost_Training
BEP_calls = ─────────────────
            Cost_T - Cost_S
```

**Decision Rule**: If break-even point < 1 week of projected volume, authorize training investment.

| Task Type | Distill? | Reason |
|-----------|----------|--------|
| Repetitive, well-defined | ✅ Yes | High ROI |
| Complex, nuanced | ❌ No | Quality loss |
| Format conversion | ✅ Yes | Pattern-learnable |
| Creative generation | ⚠️ Maybe | Depends on constraints |

---

## Anti-Patterns

- **Unbounded execution**: Always meter, even for "small" tasks
- **Trust without verify**: Agents estimate, bank audits actual usage
- **Single currency thinking**: Consider multiple resources (tokens, time, memory)
- **No reserve**: Sinking Fund prevents cascading failures
- **Ignoring Linear Logic**: Tokens are consumed, not copied
- **Static exchange rates**: Rates should be calibrated over time

---

## Integration Points

### Bootstrap (Entropy Budget)

Both entropy and economic budgets constrain agent behavior simultaneously. An agent must have sufficient:
- Entropy budget (recursion depth)
- Token budget (economic resources)

The **Dual Budget** principle: `proceed = entropy_ok AND tokens_ok`

### O-gent (Observability)

Value of Information (VoI) economics for observation agents:

```
VoI = P(disaster) × Cost(disaster) × P(detection | observation)
```

Observation prevents catastrophic failures—it has economic value even without artifacts.

---

## Implementation

**Location**: `impl/claude/agents/b/`

| Module | Purpose |
|--------|---------|
| `metered_functor.py` | Core Metered Functor, Token Bucket, Sinking Fund |
| `value_ledger.py` | Gas, Impact, RoC monitoring |

---

## See Also

- [README.md](README.md) - B-gents overview
- [../bootstrap.md](../bootstrap.md) - Entropy Budget (related constraint)
- [../o-gents/README.md](../o-gents/README.md) - Observability and VoI economics
- [../principles.md](../principles.md) - Conservation as design principle
