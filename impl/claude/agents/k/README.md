# K-gent: Kent Simulacra

A personalization layer and mirror for self-dialogue.

---

## Quick Start

### Interactive Demo
```bash
cd impl/claude
python demo_kgent.py
```

### Programmatic Usage
```python
from agents.k.persona import KgentAgent, DialogueInput, DialogueMode
from agents.k.persona import PersonaQueryAgent, PersonaQuery
from bootstrap.ground import Ground, VOID

# Initialize from Ground
ground = Ground()
facts = await ground.invoke(VOID)

# Create K-gent
kgent = KgentAgent(state=persona_state)

# Dialogue
dialogue = DialogueInput(
    message="Should I add this feature?",
    mode=DialogueMode.CHALLENGE
)
response = await kgent.invoke(dialogue)
print(response.response)

# Query preferences
query_agent = PersonaQueryAgent(state=persona_state)
query = PersonaQuery(aspect="preference", topic="communication")
prefs = await query_agent.invoke(query)
```

---

## Architecture

### Core Components

**Persona Model** (`persona.py`)
- `PersonaSeed`: Irreducible facts from Ground
- `PersonaState`: Runtime state with context
- `KgentAgent`: Main dialogue agent
- `PersonaQueryAgent`: Preference query interface

**Evolution System** (`evolution.py`)
- `EvolutionAgent`: Updates preferences over time
- `ConfidenceTracker`: Tracks belief strength
- `ChangeSource`: Explicit, inferred, inherited, decayed

### Dialogue Modes

| Mode | Purpose | Example Phrasing |
|------|---------|------------------|
| **REFLECT** | Mirror back thinking | "You've said before..." |
| **ADVISE** | Suggest aligned actions | "Your pattern is to..." |
| **CHALLENGE** | Constructive pushback | "That conflicts with..." |
| **EXPLORE** | Expand possibilities | "Given your interest in..." |

---

## Integration with Other Agents

K-gent provides personalization for the entire kgents ecosystem:

```python
# Robin (scientific agent) queries K-gent
query = PersonaQuery(
    aspect="preference",
    topic="scientific_reasoning",
    for_agent="robin"
)
style = await query_agent.invoke(query)
# Returns: "value falsifiability", "prefer mechanistic explanations"

# Robin adapts its output based on K-gent's response
```

---

## Evolution & Learning

### Confidence Tracking
- **High (0.8-1.0):** Recently confirmed, explicit
- **Medium (0.5-0.8):** Inferred or older
- **Low (0.2-0.5):** Stale, needs confirmation
- **Uncertain (<0.2):** Contradictory evidence

### Decay
- Rate: 0.1 per month without reinforcement
- Minimum: 0.1 (never fully forgotten)

### Sources
- **Explicit:** Kent directly stated
- **Inferred:** K-gent observed pattern (3+ occurrences)
- **Inherited:** From bootstrap Ground
- **Decayed:** Lost confidence over time

---

## API Reference

### PersonaQuery
```python
@dataclass
class PersonaQuery:
    aspect: str  # "preference" | "pattern" | "context" | "all"
    topic: Optional[str] = None
    for_agent: Optional[str] = None
```

### PersonaResponse
```python
@dataclass
class PersonaResponse:
    preferences: list[str]
    patterns: list[str]
    suggested_style: list[str]
    confidence: float
```

### DialogueInput
```python
@dataclass
class DialogueInput:
    message: str
    mode: DialogueMode  # REFLECT, ADVISE, CHALLENGE, EXPLORE
```

### DialogueOutput
```python
@dataclass
class DialogueOutput:
    response: str
    mode: DialogueMode
    referenced_preferences: list[str]
    referenced_patterns: list[str]
```

---

## Spec Compliance

This implementation is based on:
- `spec/k-gent/README.md` - High-level concepts
- `spec/k-gent/persona.md` - Persona model
- `spec/k-gent/evolution.md` - Evolution mechanics

**Alignment Score:** 75/100 (see `K_GENT_SESSION_SUMMARY.md`)

### Known Deviations
1. **Missing:** Access control system (spec lines 193-208)
2. **Naming:** Uses `EvolutionInput` instead of spec's `PersonaUpdate`
3. **Missing:** Spec error codes (`UNAUTHORIZED`, `PREFERENCE_CONFLICT`)
4. **Simplified:** Dialogue responses use templates vs LLM generation

### Enhancements Beyond Spec
1. **Maybe monad** for graceful error handling
2. **Structured logging** for observability
3. **Protocol-based handlers** for composability
4. **Interactive demo** for testing

---

## Bootstrap Integration

K-gent is built on the bootstrap layer:

```
Ground (bootstrap/ground.py)
  ↓ provides Facts (PersonaSeed + WorldSeed)
  ↓
PersonaState (k/persona.py)
  ↓ feeds into
KgentAgent (k/persona.py)
  ↓ composes with
Other Agents (a, b, c, ...)
```

K-gent is simultaneously:
- **An A-gent:** Follows abstract skeleton
- **A B-gent collaborator:** Personalizes scientific reasoning
- **A C-gent:** Composes with everything
- **Itself:** The only agent of its kind

---

## File Structure

```
impl/claude/agents/k/
├── __init__.py          # Public API exports
├── persona.py           # Persona model & dialogue (433 lines)
├── evolution.py         # Evolution mechanics (631 lines)
└── README.md           # This file

impl/claude/
├── demo_kgent.py        # Interactive CLI demo (284 lines)
└── bootstrap/
    └── ground.py        # Persona seed source
```

---

## Ethical Considerations

From `spec/k-gent/README.md`:

### Consent & Control
- K-gent operates only for Kent (or with explicit permission)
- Kent can view, edit, or delete any aspect
- K-gent never acts autonomously without approval

### Transparency
- K-gent clearly identifies as a simulacra, not Kent
- K-gent acknowledges uncertainty
- K-gent invites correction

### Boundaries
- K-gent does not impersonate Kent to others
- K-gent does not make commitments on Kent's behalf
- K-gent does not access private data without consent

**NOTE:** Access control not yet implemented (critical gap).

---

## Development Status

### Implemented ✅
- Core persona model
- Four dialogue modes
- Preference querying
- Evolution mechanics (confidence, decay, reinforcement)
- Pattern detection (3+ occurrences)
- Bootstrap integration
- Interactive demo

### Missing ⚠️
- Access control system
- Spec error codes
- Automatic time-based triggers
- `last_updated` timestamp tracking
- LLM-based dialogue generation

### Roadmap
See `K_GENT_SESSION_SUMMARY.md` for detailed action plan.

---

## Contributing

When enhancing K-gent:

1. **Read the spec first:** `spec/k-gent/`
2. **Maintain composability:** K-gent is an `Agent[A, B]`
3. **Preserve ethical principles:** Consent, transparency, boundaries
4. **Document deviations:** If you diverge from spec, explain why
5. **Add tests:** Ensure changes don't break composition

---

## See Also

- [Specification](../../spec/k-gent/README.md) - Original design docs
- [Bootstrap](../bootstrap/README.md) - Foundation layer
- [Session Summary](../K_GENT_SESSION_SUMMARY.md) - Latest analysis
- [Demo Script](../demo_kgent.py) - Try K-gent interactively

---

**Version:** 0.1.0
**Last Updated:** 2025-12-08
**Status:** Functional with known gaps
