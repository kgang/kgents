---
domain: world
holon: park
polynomial:
  positions:
    - observing
    - building
    - injecting
    - cooling
    - intervening
  transition: director_transition
  directions: director_directions
operad:
  extends: AGENT_OPERAD
  operations:
    observe:
      arity: 1
      signature: "Session -> Metrics"
      description: "Observe session pacing metrics passively"
    evaluate:
      arity: 2
      signature: "(Metrics, Config) -> InjectionDecision"
      description: "Evaluate whether to inject based on metrics and config"
    build_tension:
      arity: 1
      signature: "Metrics -> TensionState"
      description: "Start building tension toward potential injection"
    inject:
      arity: 2
      signature: "(SerendipityInjection, Session) -> InjectionResult"
      description: "Inject serendipity event into session"
    cooldown:
      arity: 1
      signature: "Duration -> CooldownState"
      description: "Enter cooldown period after injection"
    intervene:
      arity: 1
      signature: "DifficultyAdjustment -> InterventionResult"
      description: "Execute special difficulty adjustment"
    director_reset:
      arity: 0
      signature: "() -> Observing"
      description: "Reset director to observing state"
    abort:
      arity: 0
      signature: "() -> Observing"
      description: "Abort current operation and return to observing"
  laws:
    consent_constraint: "inject(i, s) requires consent_debt(s) <= threshold"
    cooldown_constraint: "inject(i, s) requires time_since_injection >= min_cooldown"
    tension_flow: "build_tension(m) -> inject(_, s) | observe(s) within T"
    intervention_isolation: "intervene(a) = complete(a) | abort()"
    observe_identity: "observe(observe(s)) = observe(s)"
    reset_to_observe: "reset() -> OBSERVING"
agentese:
  path: world.park
  aspects:
    - manifest
    - sessions
    - session.create
    - session.observe
    - inject
    - intervene
    - metrics
---

# Park Agent Specification

> *"The director is invisible. The guest experiences serendipity, not direction."*

The Park Crown Jewel models Punchdrunk Park's serendipity injection system. The director orchestrates immersive experiences by injecting serendipitous events while maintaining the magic circle.

## Categorical Structure

### Polynomial (DirectorPolynomial)

The director exists in 5 operational phases:

| Position | Description | Valid Transitions |
|----------|-------------|-------------------|
| OBSERVING | Passive monitoring | -> BUILDING, INTERVENING |
| BUILDING | Building tension | -> INJECTING, OBSERVING |
| INJECTING | Executing injection | -> COOLING |
| COOLING | Post-injection cooldown | -> OBSERVING |
| INTERVENING | Difficulty adjustment | -> OBSERVING (atomic) |

**Key Property**: The director is invisible. All actions feel like serendipity to guests. The magic circle must never be broken.

### Operad (DIRECTOR_OPERAD)

The operad defines the grammar of valid director operations:

**Observation**: `observe`, `evaluate`
**Injection**: `build_tension`, `inject`, `cooldown`
**Control**: `intervene`, `director_reset`, `abort`

**Laws**:
- `consent_constraint`: High consent debt blocks injection
- `cooldown_constraint`: Must respect minimum cooldown between injections
- `tension_flow`: Building tension leads to injection or observation
- `intervention_isolation`: Interventions are atomic (complete or abort)
- `observe_identity`: Observing is idempotent
- `reset_to_observe`: Reset always returns to OBSERVING

## AGENTESE Interface

```
world.park.manifest        - Director service status
world.park.sessions        - List active sessions
world.park.session.create  - Create new session
world.park.session.observe - Get session metrics
world.park.inject          - Inject serendipity
world.park.intervene       - Difficulty adjustment
world.park.metrics         - Director metrics
```

## Consent Debt Model

Serendipity injection follows an ethical framework:

| Metric | Description |
|--------|-------------|
| consent_debt | Accumulated "surprise" load on guest |
| threshold | Maximum allowed consent debt |
| cooldown | Minimum time between injections |
| drama_potential | How surprising an injection feels |

The director must respect consent boundaries. High consent debt blocks injection until the guest has time to process.

## Implementation

- **Polynomial**: `impl/claude/agents/park/polynomial.py`
- **Operad**: `impl/claude/agents/park/operad.py`
- **Node**: `impl/claude/services/park/node.py`

---

*Canonical spec derived from implementation reflection. Last verified: 2025-12-18*
