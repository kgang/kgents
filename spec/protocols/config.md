# Configuration as DNA: The Best Config System in the World

**Configuration is not loaded. It is expressed. The agent IS its config.**

**Status:** Specification v1.0
**Date:** 2025-12-09
**Related:** `umwelt.md`, `g-gents/tongue.md`, `d-gents/lenses.md`

---

## Prologue: Why Config Systems Fail

Traditional configuration systems share a fatal flaw: they treat configuration as **external data** that agents **load** at runtime. This creates:

1. **Temporal Coupling**: Agent behavior depends on when config was loaded
2. **State Sprawl**: Config is mutable; agents can be in inconsistent states
3. **Validation Theater**: Schemas validate structure but not semantics
4. **Testing Hell**: Mocking config requires recreating the entire system

**The DNA Insight**: Biological organisms don't "load" their genetics. They ARE their genetics. The genotype (DNA) determines the phenotype (organism). Configuration should work the same way.

---

## Part I: The DNA Model

### 1.1 Core Principles

| Traditional Config | DNA Config |
|-------------------|------------|
| Loaded at runtime | Expressed at construction |
| Mutable during lifetime | Immutable once germinated |
| External file/env | Internal to agent |
| Validated on load | Validated on germination |
| Agent uses config | Agent IS config |

### 1.2 The Germination Pattern

```python
# Traditional (bad)
agent = Agent()
agent.load_config("path/to/config.yaml")
# Agent exists before config! Temporal coupling!

# DNA (good)
agent = Agent.germinate(
    dna=AgentDNA(creativity=0.8, risk_tolerance=0.3)
)
# Agent cannot exist without DNA. No temporal coupling.
```

### 1.3 Why "Germinate" Not "Construct"

The word matters. Construction implies assembly from parts. Germination implies **expression from code**. An agent germinates from its DNA like a seed germinates into a plant. The DNA contains the full specification; germination is the unfolding.

---

## Part II: The DNA Type

### 2.1 Base Protocol

```python
from typing import Protocol, ClassVar, Self
from dataclasses import dataclass

class DNA(Protocol):
    """
    Base protocol for agent configuration.

    All agent configs implement this protocol. The key insight:
    DNA is validated at germination time using G-gent tongues,
    not at runtime using schema validators.
    """

    @classmethod
    def tongue(cls) -> "Tongue":
        """
        Return the G-gent tongue that validates this DNA.

        The tongue is auto-generated from the dataclass structure
        but can be customized for semantic constraints.
        """
        ...

    @classmethod
    def germinate(cls, **kwargs) -> Self:
        """
        Create validated DNA from keyword arguments.

        Raises DNAValidationError if tongue validation fails.
        """
        ...

    def express(self, trait: str) -> any:
        """
        Express a derived trait from the DNA.

        Traits are computed from base DNA. For example:
        - creativity=0.8 → temperature=1.2
        - risk_tolerance=0.3 → max_retries=5
        """
        ...
```

### 2.2 Concrete Implementation

```python
@dataclass(frozen=True)  # Immutable!
class AgentDNA:
    """
    Example agent DNA.

    All fields are immutable after germination.
    Derived traits are computed, not stored.
    """
    # Base genetic code
    personality: str
    creativity: float  # 0.0 to 1.0
    risk_tolerance: float  # 0.0 to 1.0
    exploration_budget: float = 0.1  # The Accursed Share

    # Class-level tongue (auto-generated)
    _tongue: ClassVar[Tongue] = None

    @classmethod
    def tongue(cls) -> Tongue:
        if cls._tongue is None:
            cls._tongue = reify_schema(
                domain=f"dna.{cls.__name__}",
                schema=cls,
                constraints=[
                    # Semantic constraints beyond type checking
                    ("creativity", lambda x: 0 <= x <= 1, "must be 0-1"),
                    ("risk_tolerance", lambda x: 0 <= x <= 1, "must be 0-1"),
                    ("exploration_budget", lambda x: 0 <= x <= 0.5, "max 50% exploration"),
                ],
            )
        return cls._tongue

    @classmethod
    def germinate(cls, **kwargs) -> "AgentDNA":
        """Create validated DNA."""
        # Construct instance
        instance = cls(**kwargs)

        # Validate against tongue
        tongue = cls.tongue()
        validation = tongue.validate(instance)
        if not validation.is_valid:
            raise DNAValidationError(
                dna_type=cls.__name__,
                errors=validation.errors,
            )

        return instance

    def express(self, trait: str) -> any:
        """
        Derive traits from base DNA.

        This is where the magic happens: simple config
        values generate complex behavioral parameters.
        """
        expressions = {
            # LLM parameters derived from creativity
            "temperature": 0.5 + (self.creativity * 0.7),
            "top_p": 0.7 + (self.creativity * 0.25),

            # Retry behavior derived from risk tolerance
            "max_retries": int(5 - (self.risk_tolerance * 4)),
            "retry_delay": 1.0 + (2.0 * (1 - self.risk_tolerance)),

            # Exploration derived from exploration_budget
            "exploration_probability": self.exploration_budget,
            "exploit_probability": 1 - self.exploration_budget,
        }

        if trait not in expressions:
            raise TraitNotFoundError(f"Unknown trait: {trait}")

        return expressions[trait]
```

---

## Part III: G-gent Tongue Integration

### 3.1 Auto-Generated Tongues

Every DNA class automatically generates a G-gent tongue:

```python
from agents.g import reify_schema, Tongue, GrammarLevel

def dna_to_tongue(dna_class: type) -> Tongue:
    """
    Generate G-gent tongue from DNA dataclass.

    The tongue provides:
    1. Schema validation (type checking)
    2. Constraint validation (semantic checking)
    3. Parsing (string → DNA)
    4. Serialization (DNA → string)
    """
    # Extract fields from dataclass
    fields = get_dataclass_fields(dna_class)

    # Build grammar rules
    rules = []
    for field in fields:
        rule = field_to_rule(field)
        rules.append(rule)

    return Tongue(
        name=f"dna.{dna_class.__name__}",
        level=GrammarLevel.SCHEMA,
        rules=rules,
        examples=[
            # Auto-generate examples from defaults
            dna_class(),
        ],
    )
```

### 3.2 Custom Constraints

Beyond type checking, tongues enforce semantic constraints:

```python
@dataclass(frozen=True)
class HypothesisDNA(DNA):
    """DNA for B-gent hypothesis agents."""
    confidence_threshold: float
    falsification_required: bool
    max_hypotheses: int

    @classmethod
    def tongue(cls) -> Tongue:
        base = dna_to_tongue(cls)

        # Add semantic constraints
        return base.with_constraints([
            # Confidence must be conservative (epistemic humility)
            Constraint(
                name="epistemic_humility",
                check=lambda d: d.confidence_threshold <= 0.8,
                message="Confidence threshold must not exceed 0.8 (Popperian)",
            ),

            # Falsification is non-negotiable for science
            Constraint(
                name="popperian_principle",
                check=lambda d: d.falsification_required == True,
                message="Falsification must be required (Popper)",
            ),

            # Resource bounds
            Constraint(
                name="hypothesis_budget",
                check=lambda d: 1 <= d.max_hypotheses <= 10,
                message="Hypothesis count must be 1-10",
            ),
        ])
```

### 3.3 Procedural Generation

Tongues can generate derived DNA from high-level intent:

```python
# High-level intent
intent = "Create a cautious, methodical agent"

# G-gent tongue generates DNA
tongue = AgentDNA.tongue()
suggested_dna = tongue.generate(intent)
# → AgentDNA(creativity=0.3, risk_tolerance=0.2, ...)

# Validation confirms it's valid
assert tongue.validate(suggested_dna).is_valid
```

---

## Part IV: The Trait Expression System

### 4.1 Why Traits?

Raw config values are meaningless without interpretation. What does `creativity=0.8` mean for LLM temperature? The trait system makes this explicit.

```python
# Without traits (bad)
agent = Agent(config)
# Somewhere deep in code:
temperature = config.creativity * 1.5 + 0.3  # Magic numbers!

# With traits (good)
agent = Agent(dna)
temperature = dna.express("temperature")  # Clear derivation
```

### 4.2 Trait Algebra

Traits can compose:

```python
class ComposedDNA:
    """DNA that combines traits from multiple sources."""

    def __init__(self, base: DNA, modifiers: list[DNAModifier]):
        self._base = base
        self._modifiers = modifiers

    def express(self, trait: str) -> any:
        # Start with base expression
        value = self._base.express(trait)

        # Apply modifiers
        for modifier in self._modifiers:
            value = modifier.modify(trait, value)

        return value

# Example: Context-dependent trait modification
class UrgencyModifier(DNAModifier):
    """Modify traits based on urgency level."""

    def __init__(self, urgency: float):
        self.urgency = urgency  # 0.0 to 1.0

    def modify(self, trait: str, value: any) -> any:
        if trait == "max_retries":
            # Urgent tasks get fewer retries
            return max(1, int(value * (1 - self.urgency * 0.5)))
        return value
```

### 4.3 Trait Catalog

Standard traits that agents can express:

| Trait | Derived From | Type | Description |
|-------|--------------|------|-------------|
| `temperature` | creativity | float | LLM sampling temperature |
| `top_p` | creativity | float | Nucleus sampling threshold |
| `max_retries` | risk_tolerance | int | Retry attempts on failure |
| `retry_delay` | risk_tolerance | float | Seconds between retries |
| `exploration_probability` | exploration_budget | float | P(explore) vs P(exploit) |
| `verbosity` | personality | str | Output detail level |
| `formality` | personality | float | Tone formality |

---

## Part V: Storage and Persistence

### 5.1 DNA is NOT Stored Separately

Traditional config stores config files. DNA doesn't work that way.

```python
# Traditional (separate config file)
# config.yaml → loaded → agent state

# DNA (embedded in agent state)
# Agent state includes DNA
# DNA cannot exist without agent
```

### 5.2 D-gent Integration

When persisting an agent, DNA is part of the state:

```python
@dataclass
class AgentState:
    """Persistable agent state includes DNA."""
    dna: AgentDNA  # Frozen, immutable
    memory: dict   # Mutable state
    history: list  # Audit trail

# D-gent persistence includes DNA
storage = PersistentAgent(path="agent.json", schema=AgentState)
await storage.save(AgentState(dna=dna, memory={}, history=[]))
```

### 5.3 DNA Evolution (Re-Germination)

What if DNA needs to change? Re-germinate:

```python
# Current agent with DNA v1
agent_v1 = Agent.germinate(dna_v1, umwelt)

# DNA needs to evolve (e.g., user wants more creativity)
dna_v2 = AgentDNA.germinate(
    **{**dataclasses.asdict(dna_v1), "creativity": 0.9}
)

# Re-germinate agent with new DNA
agent_v2 = Agent.germinate(dna_v2, umwelt)

# agent_v1 and agent_v2 are different instances
# Umwelt state is preserved (same lens)
# DNA is different
```

---

## Part VI: AI Agent Development Ergonomics

### 6.1 Why This Is Easy for AI Agents

AI agents (Claude, GPT, etc.) developing kgents benefit from:

1. **Type Safety**: DNA dataclasses are fully typed; AI sees the structure
2. **Auto-Documentation**: Tongue includes examples and constraints
3. **Validation Feedback**: Clear errors when DNA is invalid
4. **No Hidden State**: DNA is explicit; no config files to hunt for

```python
# AI agent can introspect DNA
print(AgentDNA.tongue().to_markdown())
# → Full documentation of valid DNA structure

# AI agent can validate before creating
validation = AgentDNA.tongue().validate(proposed_dna)
if not validation.is_valid:
    print(validation.errors)
    # → Clear guidance on what's wrong
```

### 6.2 IDE/Tool Integration

```python
# Tongues generate JSON Schema for IDE support
schema = AgentDNA.tongue().to_json_schema()
# → Full JSON Schema with constraints, descriptions, examples

# Tongues generate TypeScript types for cross-language support
types = AgentDNA.tongue().to_typescript()
# → TypeScript interface definition
```

### 6.3 Testing DNA

```python
# Property-based testing of DNA
from hypothesis import given, strategies as st

@given(
    creativity=st.floats(0, 1),
    risk_tolerance=st.floats(0, 1),
)
def test_dna_always_valid_in_range(creativity, risk_tolerance):
    """Any values in valid range should germinate."""
    dna = AgentDNA.germinate(
        personality="test",
        creativity=creativity,
        risk_tolerance=risk_tolerance,
    )
    assert dna is not None

# Tongue constraint testing
def test_epistemic_humility_enforced():
    """DNA with high confidence should fail."""
    with pytest.raises(DNAValidationError) as exc:
        HypothesisDNA.germinate(
            confidence_threshold=0.95,  # Too confident!
            falsification_required=True,
            max_hypotheses=5,
        )
    assert "epistemic_humility" in str(exc.value)
```

---

## Part VII: Migration Guide

### 7.1 From @dataclass Config to DNA

```python
# Before: Mutable config
@dataclass
class JGentConfig:
    max_depth: int = 5
    entropy_budget: float = 1.0

config = JGentConfig()
config.max_depth = 10  # Mutation allowed!

# After: Immutable DNA
@dataclass(frozen=True)
class JGentDNA(DNA):
    max_depth: int = 5
    entropy_budget: float = 1.0

    @classmethod
    def tongue(cls) -> Tongue:
        return reify_schema(...)

dna = JGentDNA.germinate(max_depth=5)
dna.max_depth = 10  # FrozenInstanceError!
```

### 7.2 From Config File Loading to Germination

```python
# Before: File-based config
config = load_yaml("config.yaml")
agent = Agent(config)

# After: Germination
dna = JGentDNA.germinate(
    **yaml.safe_load(open("dna.yaml"))  # Optional: bootstrap from file
)
agent = Agent.germinate(dna, umwelt)
```

### 7.3 The 50+ Config Classes

Each existing config class becomes a DNA class:

| Old Config | New DNA | Changes |
|------------|---------|---------|
| `JGentConfig` | `JGentDNA` | Add `frozen=True`, `tongue()`, `express()` |
| `MemoryConfig` | `MemoryDNA` | Same |
| `ParserConfig` | `ParserDNA` | Same |
| ... | ... | ... |

---

## Appendix A: Standard DNA Types

```python
# Core DNA types in impl/claude/bootstrap/dna.py

@dataclass(frozen=True)
class CoreDNA:
    """DNA shared by all agents."""
    exploration_budget: float = 0.1  # The Accursed Share

@dataclass(frozen=True)
class LLMAgentDNA(CoreDNA):
    """DNA for agents that call LLMs."""
    creativity: float = 0.5
    verbosity: str = "concise"

@dataclass(frozen=True)
class StatefulAgentDNA(CoreDNA):
    """DNA for agents with persistent state."""
    history_depth: int = 100
    auto_save: bool = True
```

## Appendix B: Tongue Constraint Library

```python
# Standard constraints in impl/claude/agents/g/constraints.py

EPISTEMIC_HUMILITY = Constraint(
    name="epistemic_humility",
    check=lambda d: getattr(d, 'confidence_threshold', 0.5) <= 0.8,
    message="Confidence threshold must not exceed 0.8",
)

POSITIVE_EXPLORATION = Constraint(
    name="positive_exploration",
    check=lambda d: getattr(d, 'exploration_budget', 0.1) > 0,
    message="Must allocate some budget for exploration (Accursed Share)",
)

BOUNDED_DEPTH = Constraint(
    name="bounded_depth",
    check=lambda d: getattr(d, 'max_depth', 5) <= 20,
    message="Recursion depth must be bounded",
)
```

---

*The caterpillar's DNA already contains the butterfly. The agent's DNA already contains its behavior. Configuration is not something added—it is something expressed.*
