# Metabolism: void.entropy.* Implementation

> *"Without the Accursed Share, your agents are just scripts."*

**AGENTESE Context**: `void.entropy.*`
**Status**: Planned
**Principles**: Accursed Share, Joy-Inducing

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Token Thermometer** | Simple pressure metric: input/output ratio |
| **Pressure accumulation** | Activity increases pressure, natural decay |
| **Fever trigger** | High pressure → forced creative expenditure |
| **Voluntary tithe** | `kgents tithe` to discharge pressure voluntarily |
| **Fever Glitch** | UI shows oblique strategies when feverish |

---

## The Accursed Share

Every system accumulates entropy. The Accursed Share principle says this excess must be **spent, not suppressed**.

In kgents:
- **Pressure accumulates** from agent activity
- **Fever triggers** when pressure exceeds threshold
- **FeverStream** generates creative output
- **Tithe** allows voluntary discharge

---

## Metabolic Engine (📋 PLANNED)

```python
@dataclass
class MetabolicEngine:
    """
    The thermodynamic heart of the system.

    Start simple: Token Thermometer.
    Later: Sophisticated pressure dynamics.
    """
    pressure: float = 0.0
    critical_threshold: float = 1.0

    # Token tracking
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def temperature(self) -> float:
        """Token-based temperature estimate."""
        if self.output_tokens == 0:
            return 0.0
        return self.input_tokens / self.output_tokens

    def tick(self, input_count: int, output_count: int) -> FeverEvent | None:
        """Called per LLM invocation."""
        self.input_tokens += input_count
        self.output_tokens += output_count

        # Pressure accumulation
        activity = output_count * 0.01
        self.pressure += activity

        # Natural decay
        self.pressure *= 0.99

        if self.pressure > self.critical_threshold:
            return self._trigger_fever()
        return None

    def _trigger_fever(self) -> FeverEvent:
        """Forced creative expenditure."""
        self.in_fever = True
        dream = FeverDream(
            intensity=self.pressure - self.critical_threshold,
            timestamp=time.time(),
            trigger="pressure_overflow"
        )
        self.pressure *= 0.5  # Discharge through dream

        if self.pressure < self.critical_threshold:
            self.in_fever = False

        return FeverEvent(dream=dream, temperature_injection=1.2)
```

**Location**: `protocols/agentese/metabolism/__init__.py`

---

## Fever Stream (📋 PLANNED)

```python
class FeverStream:
    """
    Background thread that runs when pressure is high.
    Generates poetic misunderstandings that sometimes solve problems.
    """

    async def dream(self, context: dict) -> str:
        """
        Generate a fever dream from current context.

        This is the "hallucination as feature" pattern.
        """
        prompt = f"""
        The system is running hot. Here is the current context:
        {json.dumps(context, indent=2)}

        Generate an oblique strategy—a sideways thought that might
        illuminate the problem from an unexpected angle.

        Be brief, enigmatic, potentially useful.
        """

        return await llm.generate(
            prompt,
            temperature=1.4,  # HOT
            max_tokens=100,
        )
```

**Location**: `protocols/agentese/metabolism/fever.py`

---

## Tithe Command (📋 PLANNED)

```python
# protocols/cli/handlers/tithe.py
@expose(help="Voluntarily discharge entropy pressure")
async def tithe(self, amount: float = 0.1) -> dict:
    """kgents tithe - Pay for order, discharge pressure."""
    client = CortexClient()
    response = await client.invoke(
        "void.entropy.tithe",
        observer=get_current_umwelt(),
        amount=amount,
    )
    return {
        "gratitude": response.gratitude,
        "remaining_pressure": response.pressure
    }
```

**Usage**:
```bash
kgents tithe             # Discharge default amount
kgents tithe --amount 0.3  # Discharge more
```

---

## Fever Glitch in TUI (📋 PLANNED)

When pressure exceeds threshold, the Terrarium TUI shows:
- Random poetry in the margins
- Color shifts
- "Oblique strategies" from FeverStream

```
┌─────────────────────────────────────────────────────────────┐
│ KGENTS OBSERVATORY                    [Pressure: ▓▓▓▓▓▓▓▓░░ 82%] │
│                                       ~~~ FEVER ~~~         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [OBLIQUE] "Consider the opposite. What if you're already  │
│            at the destination?"                             │
│                                                             │
│  ...rest of TUI with subtle color distortions...           │
└─────────────────────────────────────────────────────────────┘
```

---

## AGENTESE Path Registry

| Path | Operation | Description |
|------|-----------|-------------|
| `void.entropy.sip` | Draw entropy | Branch via duplicate() |
| `void.entropy.tithe` | Pay for order | Voluntary discharge |
| `void.entropy.pour` | Compost | Delete expired crystals |
| `void.entropy.pressure` | Query | Current metabolic pressure |
| `void.entropy.fever` | Check | Is system in fever? |

---

## Integration with Context

The Metabolism system connects to context management:

```
Pressure accumulates → Fever triggers → FeverDream generated → Pressure discharged
                                              ↓
                                   "Oblique strategy" output
                                   (gratitude for waste)
```

The `void.entropy.tithe` aspect allows **voluntary** entropy discharge—paying for order.

---

## Implementation Phases

### Phase 1.3: Metabolism (📋 PLANNED)
- [ ] `MetabolicEngine` (token thermometer)
- [ ] `FeverStream` (background dreamer)
- [ ] `void.entropy.tithe` implementation
- [ ] `kgents tithe` CLI command

### Phase 4.4: TUI Integration (📋 PLANNED)
- [ ] Pressure gauge in Terrarium
- [ ] Fever Glitch visualization
- [ ] Oblique strategy display

---

## Pressure Dynamics

```
             pressure
                ^
                |
    threshold --|-------------- fever trigger
                |      /\
                |     /  \   /\
                |    /    \_/  \
                |   /           \
                |  /             \_____
                | /                    \___
                |/                          \____
                +---------------------------------> time
                     ^        ^
                     |        |
                   tick()   tithe()
```

- **tick()**: Adds pressure (per LLM call)
- **decay**: Natural 1% decay per tick
- **tithe()**: Voluntary discharge
- **fever**: Forced discharge when threshold exceeded

---

## Cross-References

- **Plans**: `void/capital.md` (Social capital), `self/stream.md` (Crystals compost)
- **Impl**: `protocols/agentese/metabolism/` (planned)
- **Spec**: `spec/principles.md` (Accursed Share)

---

*"The river that flows only downhill never discovers the mountain spring."*
