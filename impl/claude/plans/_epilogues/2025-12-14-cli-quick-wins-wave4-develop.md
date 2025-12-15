# CLI Quick Wins Wave 4: DEVELOP Phase

> *Handler contracts, Logos paths, and test skeletons for 9 joy-inducing commands*

**Phase**: DEVELOP
**Date**: 2025-12-14
**Touched By**: claude-opus-4.5

---

## Overview

This document defines contracts for 9 CLI commands from `plans/devex/cli-quick-wins-wave4.md`:

| Command | Agent | Category | Effort |
|---------|-------|----------|--------|
| `project` | H-jung | Thinking | 1 |
| `oblique` | A-gent | Creative | 1 |
| `constrain` | A-gent | Creative | 1 |
| `yes-and` | A-gent | Creative | 1 |
| `surprise-me` | A-gent | Creative | 1 |
| `why` | K-gent | Inquiry | 1 |
| `tension` | K-gent | Inspection | 1 |
| `challenge` | K-gent | Dialectics | alias |
| `sparkline` | None | Utility | 1 |

---

## Handler Contracts

### 1. `kg project <text>` (H-jung Projection)

**Purpose**: Analyze where the user/system is projecting shadow content.

**Handler Signature**:
```python
# File: impl/claude/protocols/cli/handlers/project.py

def cmd_project(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    H-jung Projection Analysis: Where are you projecting?

    Usage:
        kg project "They're so disorganized"
        kg project --deep "I hate bureaucracy"

    Returns:
        0 on success, 1 on error
    """
```

**Input/Output Types**:
```python
@dataclass
class ProjectionAnalysis:
    original_statement: str
    shadow_content: str       # What shadow is being projected
    projected_onto: str       # Target of projection
    self_inquiry: str         # "What does this reveal about you?"
    integration_hint: str     # How to reclaim the projection
```

**Logos Path**: `void.shadow.project.invoke`

**Error Handling**:
- Empty input → "What statement would you like to analyze?"
- Too short (<3 words) → "Provide more context for meaningful analysis"

**REPL Integration**:
- Accessible via `void.shadow.project <text>`
- Aliased from `/project` slash command

---

### 2. `kg oblique` (Brian Eno Oblique Strategies)

**Purpose**: Serve a lateral thinking prompt from Oblique Strategies deck.

**Handler Signature**:
```python
# File: impl/claude/protocols/cli/handlers/oblique.py

def cmd_oblique(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Oblique Strategies: Lateral thinking prompts (Brian Eno/Peter Schmidt).

    Usage:
        kg oblique              # Random strategy
        kg oblique --list       # Show all strategies
        kg oblique --seed 42    # Reproducible random

    Note: Strategies are public domain educational quotes.
    """
```

**Input/Output Types**:
```python
@dataclass
class ObliqueStrategy:
    text: str                 # The strategy itself
    category: str | None      # Optional categorization
    interpretation: str       # Brief interpretation hint
```

**Logos Path**: `concept.creativity.oblique.invoke`

**Error Handling**:
- None required (always produces output)

**REPL Integration**:
- Accessible via `concept.creativity.oblique`
- Also via shortcut `/oblique`

**Implementation Note**: Include ~50 core strategies from the deck (public domain educational use).

---

### 3. `kg constrain <topic>` (Productive Constraints)

**Purpose**: Generate productive constraints that spark creativity.

**Handler Signature**:
```python
# File: impl/claude/protocols/cli/handlers/constrain.py

def cmd_constrain(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Generate productive constraints for a topic.

    Usage:
        kg constrain "API design"
        kg constrain "writing a novel" --count 5
        kg constrain --persona provocative "team meeting"
    """
```

**Input/Output Types**:
```python
# Uses existing CreativityCoach with mode=CONSTRAIN
# Input: CreativityInput(seed=topic, mode=CreativityMode.CONSTRAIN)
# Output: CreativityResponse
```

**Logos Path**: `concept.creativity.constrain.invoke`

**Error Handling**:
- No topic → "What would you like to constrain?"
- Invalid persona → List valid personas

**REPL Integration**:
- Via `concept.creativity.constrain <topic>`
- Supports pipeline: `self.soul.manifest >> concept.creativity.constrain`

---

### 4. `kg yes-and <idea>` (Improv Expansion)

**Purpose**: Expand an idea using improv "yes, and..." technique.

**Handler Signature**:
```python
# File: impl/claude/protocols/cli/handlers/yes_and.py

def cmd_yes_and(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Improv-style idea expansion: "Yes, and..."

    Usage:
        kg yes-and "What if agents could dream?"
        kg yes-and --rounds 3 "Semantic memory as garden"
        kg yes-and --persona playful "Code review as jazz"
    """
```

**Input/Output Types**:
```python
# Uses existing CreativityCoach with mode=EXPAND
# Input: CreativityInput(seed=idea, mode=CreativityMode.EXPAND)
# Output: CreativityResponse
```

**Logos Path**: `concept.creativity.expand.invoke`

**Error Handling**:
- No idea → "What idea would you like to expand?"
- Rounds < 1 → Default to 1

**REPL Integration**:
- Via `concept.creativity.expand <idea>`
- Aliased as `/yes-and` for ergonomics

---

### 5. `kg surprise-me` (Random Creative Prompt)

**Purpose**: Generate a random creative prompt/question.

**Handler Signature**:
```python
# File: impl/claude/protocols/cli/handlers/surprise_me.py

def cmd_surprise_me(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Random creative prompt generator.

    Usage:
        kg surprise-me                # Random prompt
        kg surprise-me --domain code  # Domain-specific
        kg surprise-me --weird        # Extra weird
    """
```

**Input/Output Types**:
```python
@dataclass
class CreativePrompt:
    prompt: str               # The creative prompt
    domain: str | None        # Optional domain context
    weirdness: float          # 0.0 = normal, 1.0 = very weird
```

**Logos Path**: `void.serendipity.prompt.invoke` (draws from Accursed Share)

**Error Handling**:
- Invalid domain → List valid domains
- Uses entropy sip for true randomness

**REPL Integration**:
- Via `void.serendipity.prompt`
- Shortcut `/surprise`

---

### 6. `kg why <statement>` (Recursive Why)

**Purpose**: Ask "why?" recursively until reaching bedrock assumptions.

**Handler Signature**:
```python
# File: impl/claude/protocols/cli/handlers/why.py

def cmd_why(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Recursive why: Dig to bedrock assumptions.

    Usage:
        kg why "We need microservices"
        kg why --depth 5 "Users want dark mode"
        kg why --socratic "The tests should pass"
    """
```

**Input/Output Types**:
```python
@dataclass
class WhyChain:
    original: str             # Original statement
    chain: list[WhyStep]      # Chain of why questions
    bedrock: str              # The foundational assumption reached

@dataclass
class WhyStep:
    question: str             # "Why?"
    answer: str               # Answer to the why
    depth: int                # 1, 2, 3...
```

**Logos Path**: `self.soul.why.invoke` (K-gent inquiry mode)

**Error Handling**:
- No statement → "What statement would you like to examine?"
- Depth > 10 → Warn "Deep inquiry may take time"

**REPL Integration**:
- Via `self.soul.why <statement>`
- Integrates with soul's challenge mode

---

### 7. `kg tension` (List Unresolved Tensions)

**Purpose**: Surface unresolved tensions in the current context.

**Handler Signature**:
```python
# File: impl/claude/protocols/cli/handlers/tension.py

def cmd_tension(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    List unresolved tensions: What's in conflict?

    Usage:
        kg tension                    # Current project tensions
        kg tension --system           # System-level tensions
        kg tension --plans            # Plan file tensions
        kg tension <path>             # Tensions in specific file
    """
```

**Input/Output Types**:
```python
@dataclass
class Tension:
    pole_a: str               # One side of the tension
    pole_b: str               # Other side
    context: str              # Where this tension manifests
    severity: float           # 0.0 = mild, 1.0 = critical
    held_since: str | None    # When first detected

@dataclass
class TensionReport:
    tensions: list[Tension]
    dominant_tension: Tension | None
    synthesis_hints: list[str]  # Possible resolutions
```

**Logos Path**: `self.soul.tension.invoke`

**Error Handling**:
- No context → Use current working directory
- File not found → Sympathetic error with suggestions

**REPL Integration**:
- Via `self.soul.tension`
- Shows in `self.soul.manifest` output

---

### 8. `kg challenge <claim>` (Devil's Advocate)

**Purpose**: Challenge a claim using devil's advocate dialectics.

**Handler Signature**:
```python
# File: impl/claude/protocols/cli/handlers/soul.py (existing, add alias)

# Already implemented as `kg soul challenge <claim>`
# This creates a top-level alias for ergonomics:

def cmd_challenge(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Alias: kg challenge -> kg soul challenge."""
    from protocols.cli.handlers.soul import cmd_soul
    return cmd_soul(["challenge"] + args, ctx)
```

**Logos Path**: `self.soul.challenge.invoke` (existing)

**REPL Integration**: Already works via `self.soul.challenge <claim>`

**Note**: This is just an alias; implementation already exists.

---

### 9. `kg sparkline <numbers>` (Visual Sparkline)

**Purpose**: Render numbers as a text sparkline visualization.

**Handler Signature**:
```python
# File: impl/claude/protocols/cli/handlers/sparkline.py

def cmd_sparkline(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Render numbers as Unicode sparkline.

    Usage:
        kg sparkline 47 20 15 30 45    # → ▅▂▁▃▅
        kg sparkline --height 2 1 2 3  # Double height
        echo "1,2,3,4" | kg sparkline  # Piped input

    Characters: ▁▂▃▄▅▆▇█
    """
```

**Input/Output Types**:
```python
@dataclass
class Sparkline:
    values: list[float]       # Input numbers
    rendered: str             # Unicode sparkline
    min_val: float
    max_val: float

SPARK_CHARS = "▁▂▃▄▅▆▇█"  # 8 levels
```

**Logos Path**: `world.viz.sparkline.invoke` (pure utility, no agent)

**Error Handling**:
- Non-numeric input → "Could not parse as numbers"
- Empty input → "Provide numbers to visualize"
- Single number → Return single bar

**REPL Integration**:
- Via `world.viz.sparkline <numbers>`
- Supports pipe: `self.metrics.history >> world.viz.sparkline`

**Implementation**:
```python
def render_sparkline(values: list[float]) -> str:
    """Pure function: numbers -> sparkline string."""
    if not values:
        return ""
    min_v, max_v = min(values), max(values)
    span = max_v - min_v if max_v > min_v else 1
    return "".join(
        SPARK_CHARS[min(7, int((v - min_v) / span * 7.99))]
        for v in values
    )
```

---

## Logos Path Summary

| Command | Logos Path | Aspect |
|---------|------------|--------|
| `project` | `void.shadow.project` | invoke |
| `oblique` | `concept.creativity.oblique` | invoke |
| `constrain` | `concept.creativity.constrain` | invoke |
| `yes-and` | `concept.creativity.expand` | invoke |
| `surprise-me` | `void.serendipity.prompt` | invoke |
| `why` | `self.soul.why` | invoke |
| `tension` | `self.soul.tension` | invoke |
| `challenge` | `self.soul.challenge` | invoke (existing) |
| `sparkline` | `world.viz.sparkline` | invoke |

---

## Error Handling Patterns

All handlers follow the established patterns from `docs/skills/handler-patterns.md`:

### Pattern 1: Sympathetic Missing Input
```python
if not args or not any(a for a in args if not a.startswith("-")):
    _emit_output(
        "[COMMAND] What would you like to [verb]?",
        {"error": "missing_input", "suggestion": "Provide <required>"},
        ctx,
    )
    return 1
```

### Pattern 2: Invalid Flag
```python
if invalid_flag:
    _emit_error(
        f"Unknown flag: {flag}",
        ctx,
        available_flags=["--help", "--json", "--count"],
    )
    return 1
```

### Pattern 3: Graceful Degradation
```python
try:
    from agents.h.jung import JungShadow
except ImportError:
    _emit_output(
        "[PROJECT] H-gent module not available (install optional deps)",
        {"error": "module_unavailable", "module": "agents.h.jung"},
        ctx,
    )
    return 1
```

---

## Test Skeleton Structure

Tests will follow `docs/skills/test-patterns.md`:

```
impl/claude/protocols/cli/handlers/_tests/
├── test_project.py
├── test_oblique.py
├── test_constrain.py
├── test_yes_and.py
├── test_surprise_me.py
├── test_why.py
├── test_tension.py
└── test_sparkline.py
```

### Per-Handler Test Structure:
```python
# test_<command>.py

import pytest
from protocols.cli.handlers.<command> import cmd_<command>

class TestCmd<Command>:
    """Tests for kg <command>."""

    def test_help_flag(self) -> None:
        """--help returns 0 and prints help."""
        assert cmd_<command>(["--help"]) == 0

    def test_basic_invocation(self) -> None:
        """Basic usage returns 0."""
        assert cmd_<command>(["test input"]) == 0

    def test_missing_input(self) -> None:
        """Missing input returns 1 with sympathetic error."""
        assert cmd_<command>([]) == 1

    def test_json_mode(self) -> None:
        """--json produces valid JSON output."""
        # Capture output and verify JSON
        ...
```

### Shared Fixtures:
```python
# conftest.py additions

@pytest.fixture
def mock_creativity_coach():
    """Mock CreativityCoach for deterministic tests."""
    ...

@pytest.fixture
def mock_jung_shadow():
    """Mock JungShadow for deterministic tests."""
    ...
```

---

## REPL Integration Points

### 1. Context Registration

New holons registered in context routers:

```python
# protocols/cli/contexts/void.py
class VoidRouter(ContextRouter):
    def _register_holons(self):
        self.register("shadow", "Shadow analysis", _handle_shadow,
                     aspects=["project", "inventory", "integrate"])
        self.register("serendipity", "Random prompts", _handle_serendipity,
                     aspects=["prompt", "surprise"])

# protocols/cli/contexts/concept.py
class ConceptRouter(ContextRouter):
    def _register_holons(self):
        self.register("creativity", "Creative tools", _handle_creativity,
                     aspects=["oblique", "constrain", "expand", "connect"])

# protocols/cli/contexts/world.py
class WorldRouter(ContextRouter):
    def _register_holons(self):
        self.register("viz", "Visualization", _handle_viz,
                     aspects=["sparkline", "graph", "table"])
```

### 2. REPL Shortcuts

Add to repl.py SHORTCUTS dict:
```python
SHORTCUTS = {
    "/project": "void.shadow.project",
    "/oblique": "concept.creativity.oblique",
    "/constrain": "concept.creativity.constrain",
    "/yes-and": "concept.creativity.expand",
    "/surprise": "void.serendipity.prompt",
    "/why": "self.soul.why",
    "/tension": "self.soul.tension",
    "/sparkline": "world.viz.sparkline",
}
```

### 3. Pipeline Composition Examples

```
# Analyze soul state then visualize tension severity
self.soul.manifest >> self.soul.tension >> world.viz.sparkline

# Creative ideation pipeline
void.serendipity.prompt >> concept.creativity.expand >> concept.creativity.constrain

# Shadow analysis pipeline
self.soul.manifest >> void.shadow.project
```

---

## hollow.py Registration

Add to COMMAND_REGISTRY:
```python
COMMAND_REGISTRY = {
    # ... existing commands ...

    # Wave 4: Joy-Inducing Commands
    "project": "protocols.cli.handlers.project:cmd_project",
    "oblique": "protocols.cli.handlers.oblique:cmd_oblique",
    "constrain": "protocols.cli.handlers.constrain:cmd_constrain",
    "yes-and": "protocols.cli.handlers.yes_and:cmd_yes_and",
    "surprise-me": "protocols.cli.handlers.surprise_me:cmd_surprise_me",
    "why": "protocols.cli.handlers.why:cmd_why",
    "tension": "protocols.cli.handlers.tension:cmd_tension",
    "challenge": "protocols.cli.handlers.soul:cmd_challenge",  # alias
    "sparkline": "protocols.cli.handlers.sparkline:cmd_sparkline",
}
```

---

## Phase Ledger

```yaml
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched     # This session
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.15
  spent: 0.08
  remaining: 0.07
```

---

## Exit Criteria Status

- [x] Handler signatures defined for all 9 commands
- [x] Logos paths specified for each command
- [x] Error handling patterns documented
- [x] Test skeleton structure planned
- [x] REPL integration points identified

---

## Next Phase: STRATEGIZE

Continuation prompt:
```
⟿[STRATEGIZE]

This is the *STRATEGIZE* phase for **CLI Quick Wins Wave 4**.

/hydrate
handles: contracts=9; logos_paths=9; test_skeletons=8; repl_shortcuts=8
mission: Prioritize implementation order; identify dependencies; estimate effort per sprint; define success metrics.
actions: Order commands by effort/impact; group into sprints; identify shared infrastructure.
exit: Sprint plan + dependency graph + success metrics; ledger.STRATEGIZE=touched; continuation → IMPLEMENT.
```

---

*"Contracts are compressed wisdom. Implementation derives mechanically."*
