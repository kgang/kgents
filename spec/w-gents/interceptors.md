# W-gent Interceptors

**Status**: Specification v1.0
**Purpose**: Define the middleware interceptor pattern for agent coordination

---

## Overview

Interceptors are **middleware functions** that wrap agent invocations. They run before and after every message dispatched through the W-gent bus.

```
Message → [Interceptor₁] → [Interceptor₂] → ... → Target Agent
                                                       ↓
Result ← [Interceptor₁] ← [Interceptor₂] ← ... ← ─────┘
```

Agents are **blissfully unaware** of interceptors. This is the key insight: cross-cutting concerns (metering, safety, telemetry, personalization) are infrastructure, not agent logic.

---

## Interceptor Protocol

```python
class Interceptor(Protocol):
    """
    Middleware that wraps agent invocations.

    Interceptors form a chain. Each can:
    - Transform the message before dispatch
    - Block the message (with fallback)
    - Transform the result after dispatch
    - Observe without modification
    """

    priority: int  # Lower runs first on before(), last on after()

    async def before(self, msg: BusMessage[A, B]) -> BusMessage[A, B]:
        """
        Run before message reaches target.

        Can:
        - Modify msg.payload
        - Set msg.blocked = True (with msg.fallback)
        - Pass through unchanged
        """
        ...

    async def after(self, msg: BusMessage[A, B], result: B) -> B:
        """
        Run after target returns result.

        Can:
        - Modify result
        - Log/observe
        - Pass through unchanged
        """
        ...
```

---

## Standard Interceptors

### 1. SafetyInterceptor (J-gent)

**Priority**: 50 (runs early)
**Purpose**: Gate messages by entropy budget and reality classification

```python
@dataclass
class SafetyThresholds:
    max_entropy: float = 0.8       # Maximum allowed entropy
    reality_threshold: float = 0.5  # Minimum reality confidence
    max_recursion_depth: int = 10   # Prevent infinite loops

class SafetyInterceptor(Interceptor):
    """J-gent safety gating."""

    priority = 50

    def __init__(self, thresholds: SafetyThresholds):
        self.thresholds = thresholds

    async def before(self, msg: BusMessage) -> BusMessage:
        # Check entropy budget
        if msg.entropy > self.thresholds.max_entropy:
            msg.blocked = True
            msg.block_reason = "entropy_exceeded"
            msg.fallback = Ground("Operation too chaotic")
            return msg

        # Check reality classification
        reality = classify_reality(msg.payload)
        if reality.confidence < self.thresholds.reality_threshold:
            msg.blocked = True
            msg.block_reason = "reality_uncertain"
            msg.fallback = Ground("Cannot verify reality of operation")
            return msg

        # Check recursion depth
        if msg.depth > self.thresholds.max_recursion_depth:
            msg.blocked = True
            msg.block_reason = "recursion_limit"
            msg.fallback = Ground("Maximum depth exceeded")
            return msg

        return msg
```

### 2. MeteringInterceptor (B-gent)

**Priority**: 100
**Purpose**: Token accounting for all operations

```python
class MeteringInterceptor(Interceptor):
    """B-gent economic metering. No bypass."""

    priority = 100

    def __init__(self, treasury: Treasury, oracle: CostOracle):
        self.treasury = treasury
        self.oracle = oracle

    async def before(self, msg: BusMessage) -> BusMessage:
        # Estimate cost
        cost = self.oracle.estimate(msg)

        # Check budget
        if not self.treasury.can_afford(msg.source, cost):
            # No free bypass! Apply scarcity.
            if self.policy == ScarcityPolicy.LATENCY:
                await asyncio.sleep(self.scarcity_delay)
            elif self.policy == ScarcityPolicy.ENTROPY:
                msg.payload = inject_noise(msg.payload, self.entropy_amount)

            # Record deficit for future accounting
            self.ledger.record_deficit(msg.source, cost)
        else:
            # Debit account
            self.treasury.debit(msg.source, cost)

        msg.metadata["estimated_cost"] = cost
        return msg

    async def after(self, msg: BusMessage, result: Any) -> Any:
        # Record actual cost (may differ from estimate)
        actual_cost = self.oracle.measure_actual(msg, result)
        self.ledger.record_actual(msg.source, actual_cost)
        return result
```

**Key Insight**: The "bypass" isn't free—it costs *stability*. Agents that can't pay get noisier results or higher latency. This aligns incentives with system health.

### 3. TelemetryInterceptor (O-gent)

**Priority**: 200
**Purpose**: Emit observations for all operations

```python
class TelemetryInterceptor(Interceptor):
    """O-gent observation emission."""

    priority = 200

    def __init__(self, emitter: ObservationEmitter):
        self.emitter = emitter

    async def before(self, msg: BusMessage) -> BusMessage:
        msg.metadata["telemetry_start"] = time.monotonic()
        msg.metadata["telemetry_id"] = generate_trace_id()

        self.emitter.emit(ObservationEvent(
            type="dispatch_start",
            source=msg.source,
            target=msg.target,
            trace_id=msg.metadata["telemetry_id"]
        ))

        return msg

    async def after(self, msg: BusMessage, result: Any) -> Any:
        elapsed = time.monotonic() - msg.metadata["telemetry_start"]

        self.emitter.emit(ObservationEvent(
            type="dispatch_complete",
            trace_id=msg.metadata["telemetry_id"],
            duration_ms=elapsed * 1000,
            success=not isinstance(result, Error)
        ))

        return result
```

### 4. PersonaInterceptor (K-gent)

**Priority**: 300 (runs late, closest to agent)
**Purpose**: Inject personality priors into decision-making

```python
@dataclass
class PersonaPriors:
    """Personality as decision-making biases."""

    # Economic priors (for B-gent targets)
    discount_rate: float = 0.9     # Time preference [0,1]
    loss_aversion: float = 1.5     # Prospect theory coefficient
    risk_tolerance: float = 0.5    # Variance acceptance [0,1]

    # Safety priors (for J-gent targets)
    entropy_tolerance: float = 0.5  # Creativity vs stability [0,1]
    reality_threshold: float = 0.7  # Hallucination rejection [0,1]

class PersonaInterceptor(Interceptor):
    """K-gent prior injection. Personality is structural, not cosmetic."""

    priority = 300

    def __init__(self, priors: PersonaPriors):
        self.priors = priors

    async def before(self, msg: BusMessage) -> BusMessage:
        # Inject economic priors for B-gent
        if msg.target == "B":
            msg.payload = self.bias_utility(msg.payload)

        # Inject safety priors for J-gent
        elif msg.target == "J":
            msg.payload = self.bias_entropy(msg.payload)

        return msg

    def bias_utility(self, payload: Any) -> Any:
        """Adjust utility calculations based on persona."""
        if hasattr(payload, "utility_params"):
            payload.utility_params.discount_rate = self.priors.discount_rate
            payload.utility_params.loss_aversion = self.priors.loss_aversion
        return payload

    def bias_entropy(self, payload: Any) -> Any:
        """Adjust entropy budget based on persona."""
        if hasattr(payload, "entropy_budget"):
            payload.entropy_budget.max = self.priors.entropy_tolerance
        return payload
```

**Key Insight**: A "risk-averse" persona doesn't just *talk* carefully—it *decides* carefully. Personality affects B-gent economics and J-gent safety thresholds.

---

## Interceptor Composition

Interceptors compose by priority:

```python
def create_standard_interceptors(
    treasury: Treasury,
    thresholds: SafetyThresholds,
    priors: PersonaPriors
) -> list[Interceptor]:
    """Create the standard interceptor chain."""
    return [
        SafetyInterceptor(thresholds),      # 50
        MeteringInterceptor(treasury),       # 100
        TelemetryInterceptor(emitter),       # 200
        PersonaInterceptor(priors),          # 300
    ]

# Create bus with interceptors
bus = MiddlewareBus(interceptors=create_standard_interceptors(...))
```

### Ordering Invariants

| Order | Rationale |
|-------|-----------|
| Safety first | Block dangerous operations before metering |
| Metering second | Account for all operations (even blocked ones partially) |
| Telemetry third | Observe the metered, safe-checked message |
| Persona last | Modify just before agent sees it |

---

## Custom Interceptors

Teams can add domain-specific interceptors:

```python
class RateLimitInterceptor(Interceptor):
    """Rate limit specific agent calls."""

    priority = 75  # After safety, before metering

    def __init__(self, limits: dict[str, RateLimit]):
        self.limits = limits
        self.buckets = {k: TokenBucket(v) for k, v in limits.items()}

    async def before(self, msg: BusMessage) -> BusMessage:
        if msg.target in self.buckets:
            if not self.buckets[msg.target].acquire():
                msg.blocked = True
                msg.block_reason = "rate_limited"
                msg.fallback = Retry(delay=self.buckets[msg.target].refill_time)
        return msg
```

---

## Testing Interceptors

Interceptors should be tested in isolation:

```python
async def test_safety_blocks_high_entropy():
    interceptor = SafetyInterceptor(SafetyThresholds(max_entropy=0.5))
    msg = BusMessage(source="test", target="F", payload={}, entropy=0.9)

    result = await interceptor.before(msg)

    assert result.blocked
    assert result.block_reason == "entropy_exceeded"

async def test_metering_debits_account():
    treasury = MockTreasury(balance=100)
    interceptor = MeteringInterceptor(treasury, MockOracle(cost=10))
    msg = BusMessage(source="agent_a", target="B", payload={})

    await interceptor.before(msg)

    assert treasury.balance_of("agent_a") == 90
```

---

## See Also

- [stigmergy.md](stigmergy.md) - Pheromone-based coordination
- [wire-protocol.md](wire-protocol.md) - Wire protocol for observation
- [../protocols/cross-pollination.md](../protocols/cross-pollination.md) - Full integration architecture
- [../b-gents/banker.md](../b-gents/banker.md) - Token economics
- [../j-gents/stability.md](../j-gents/stability.md) - Entropy management
- [../k-gent/persona.md](../k-gent/persona.md) - Persona model

---

*"The best infrastructure is invisible. Agents do their work; interceptors ensure the system stays healthy."*
