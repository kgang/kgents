---
path: plans/agent-town/phase7-llm-dialogue
status: active
progress: 50
last_touched: 2025-12-14
touched_by: claude-opus-4-5
blocking: []
enables:
  - agent-town-phase8-inhabit
  - deployment/agent-town-live
session_notes: |
  PLAN phase complete. Scoped LLM-backed citizen dialogue with memory grounding.
  RESEARCH phase complete. Deep survey of K-gent, M-gent, Town infrastructure.
  DEVELOP phase complete. Full technical design for CitizenDialogueEngine,
  DialogueContext, DialogueBudgetConfig, archetype voice templates, TownEvent
  extension, and TownFlux integration sketch.
  STRATEGIZE phase complete. Implementation chunks sequenced (14 items), parallel
  tracks identified (A+B, D1||C, E1||E2), 8 checkpoints defined, 7 risks with
  mitigations, test strategy (70 new tests across 5 layers), 5-day roadmap.
  CROSS-SYNERGIZE complete. K-gent LLMClient DIRECT IMPORT. M-gent ContextInjector
  PATTERN REUSE. AGENTESE registry EXTEND. Law-abiding pipelines verified.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.40
  spent: 0.25
  remaining: 0.15
---

# Agent Town Phase 7: LLM-Backed Citizen Dialogue

> *"Citizens should SPEAK. The simulation transforms from state-machine dance to living conversation."*

## Scope Statement

Phase 7 adds **LLM-backed dialogue generation** to Agent Town citizens. When citizens interact (greet, gossip, trade), they generate actual speech via LLM calls, grounded in their memories and consistent with their archetype personality. Budget-aware routing ensures cost control.

## Exit Criteria

- [ ] Citizens generate dialogue during `greet` operations
- [ ] Dialogue is memory-grounded (refers to past interactions via M-gent)
- [ ] Dialogue is personality-consistent (archetype voice + eigenvector state)
- [ ] At least 3 interaction types with dialogue: greet, gossip, trade
- [ ] Budget tracking per citizen/operation (tokens_used logged)
- [ ] Demo in marimo notebook (watch citizens talk!)
- [ ] Tests verify dialogue generation and grounding

## Attention Budget

| Focus | % | Description |
|-------|---|-------------|
| **Dialogue Engine** | 50% | CitizenDialogueEngine, prompt templates, model routing |
| **Memory Integration** | 25% | M-gent ContextInjector for grounding, relevance scoring |
| **Budget Management** | 15% | Token tracking, tier routing, daily caps |
| **Demo + Docs** | 10% | Marimo extension, skill documentation |

## Dependencies Mapped

### Existing Infrastructure (Reuse)

| Component | Location | Usage |
|-----------|----------|-------|
| K-gent soul patterns | `agents/k/soul.py` | Budget tiers, streaming, eigenvector prompts |
| K-gent persona | `agents/k/persona.py` | System/user prompt building patterns |
| M-gent HolographicMemory | `agents/m/holographic.py` | Memory retrieval, temperature scoring |
| M-gent ContextInjector | `agents/m/context_injector.py` | Foveated context for dialogue grounding |
| Town archetypes | `agents/town/archetypes.py` | 5 archetypes with eigenvector biases |
| Town flux operations | `agents/town/flux.py` | greet, gossip, trade hooks |
| Town citizen LOD | `agents/town/citizen.py` | LOD 2 dialogue hook point |
| Town evolving | `agents/town/evolving.py` | EvolvingCitizen with GraphMemory |

### New Components (Create)

| Component | Purpose |
|-----------|---------|
| `CitizenDialogueEngine` | Main dialogue generation orchestrator |
| `CitizenVoice` | Archetype-specific prompt templates |
| `DialogueContext` | Memory-grounded context structure |
| `DialogueBudget` | Per-citizen token tracking |

## Non-Goals

- **INHABIT mode** (user-to-citizen dialogue) — Phase 8
- **Real-time streaming** — Batch generation OK
- **Voice synthesis / audio output** — Text only
- **Dialogue evaluation metrics** — Subjective for now
- **Inter-town communication** — Single town scope

## Budget Architecture

```yaml
monthly_cap: 10M tokens
daily_budget: 330K tokens

model_routing:
  greet: haiku      # ~50 tokens, quick warmth
  gossip: haiku     # ~100 tokens, rumor transmission
  trade: sonnet     # ~200 tokens, negotiation nuance
  council: sonnet   # ~500 tokens, high-drama moments

citizen_tiers:
  evolving:
    llm_access: full
    budget: 2000/day
    count: 3-5 citizens
  leaders:
    llm_access: sampled (50%)
    budget: 500/day
    count: 5 citizens
  standard:
    llm_access: cached_or_template
    budget: 100/day
    count: 15 citizens
```

## Dialogue Architecture

### CitizenDialogueEngine

```python
class CitizenDialogueEngine:
    """Generates personality-consistent dialogue for citizens."""

    def __init__(
        self,
        memory: HolographicMemory,
        llm_client: LLMClient,
        budget_config: DialogueBudgetConfig,
    ):
        self._memory = memory
        self._llm = llm_client
        self._budget = budget_config

    async def generate(
        self,
        speaker: Citizen,
        listener: Citizen,
        operation: str,  # "greet", "gossip", "trade"
        context: DialogueContext,
    ) -> Dialogue:
        """Generate dialogue for an interaction.

        Steps:
        1. Check budget tier for speaker
        2. Retrieve relevant memories (M-gent)
        3. Build prompt with personality (archetype voice)
        4. Route to appropriate model
        5. Generate + track tokens
        """
        ...
```

### Memory Grounding Flow

```
Operation Triggered (greet/gossip/trade)
    ↓
ContextInjector.invoke(speaker, listener)
    ↓
HolographicMemory.retrieve(listener_id, k=5)
    ↓
effective_score = similarity × resolution
    ↓
Foveated Context (focal + peripheral + paths)
    ↓
Inject into Dialogue Prompt
    ↓
LLM Generate
    ↓
TownEvent with dialogue field
```

### Archetype Voice Templates

| Archetype | Voice Pattern | Example Greeting |
|-----------|---------------|------------------|
| Builder | Construction metaphors, practical | "Good to see you, {name}. Been working on foundations all morning." |
| Trader | Exchange framing, calculating warmth | "Ah, {name}! What brings you to market? I've been tracking opportunities." |
| Healer | Restoration language, warm concern | "Hello, {name}. How are you? You seem {mood} today." |
| Scholar | Discovery framing, curious probing | "Fascinating, {name}! I've been studying the patterns in the square." |
| Watcher | Memory anchoring, patient observation | "I remember when you first arrived here, {name}. The town has changed." |

### AGENTESE Integration

```python
# New paths for dialogue
await logos.invoke("world.citizen.alice.speak", umwelt=observer, context=ctx)
# Returns: Dialogue object

await logos.invoke("world.citizen.alice.recall", umwelt=observer, topic="bob")
# Returns: list[Memory] for grounding
```

## Branch Candidates

| Branch | Scope | Trigger |
|--------|-------|---------|
| `citizen-memory-grounding` | Deep M-gent integration | If memory retrieval needs custom tuning |
| `dialogue-caching` | Response caching | If similar interactions recur frequently |

## Synergy Opportunities

| ID | Source | Target | Opportunity |
|----|--------|--------|-------------|
| S1 | agents/k/soul.py | CitizenDialogueEngine | Reuse budget tier patterns |
| S2 | agents/k/persona.py | CitizenVoice | Reuse prompt building patterns |
| S3 | agents/m/context_injector.py | DialogueContext | Reuse foveated context |
| S4 | agents/town/archetypes.py | CitizenVoice | Archetype-specific prompts |
| S5 | agents/town/evolving.py | Memory integration | GraphMemory for rich recall |
| S6 | agents/town/demo_marimo.py | Demo extension | Show dialogue in notebook |

## Heritage Papers Alignment

| Paper | Phase 7 Application |
|-------|---------------------|
| **SIMULACRA** | Memory retrieval formula: recency × importance × relevance |
| **CHATDEV** | Archetype-specific conversation styles |
| **ALTERA** | Coalition-aware dialogue routing (in-group more verbose) |

## Entropy Declaration

```yaml
entropy_sip: 0.10
source: void.llm.dialogue
purpose: "Explore LLM-citizen integration patterns"
```

---

## Verification Commands

```bash
# Run town tests
uv run pytest agents/town/_tests/ -v --tb=short

# Check current test count
uv run pytest agents/town/_tests/ --collect-only -q 2>/dev/null | tail -1

# Run Phase 7 specific tests (when implemented)
uv run pytest agents/town/_tests/test_dialogue*.py -v
```

---

*Guard [phase=PLAN][entropy=0.05][scope=llm-dialogue][exit=RESEARCH]*

---

---

## DEVELOP Phase Outputs (2025-12-14)

### 1. CitizenDialogueEngine — Complete Class Design

```python
"""
CitizenDialogueEngine: LLM-backed dialogue generation for Agent Town citizens.

Reuses patterns from K-gent (BudgetTier, LLMClient, streaming) and
M-gent (HolographicMemory, ContextInjector foveation).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncIterator

if TYPE_CHECKING:
    from agents.k.llm import LLMClient, LLMResponse, StreamingLLMResponse
    from agents.town.citizen import Citizen, Eigenvectors
    from agents.town.flux import TownPhase


# =============================================================================
# Data Structures
# =============================================================================


class DialogueTier(Enum):
    """Citizen dialogue budget tiers (adapted from K-gent BudgetTier)."""

    TEMPLATE = "template"     # 0 tokens - pre-written templates only
    CACHED = "cached"         # 0 tokens - reuse recent similar dialogue
    HAIKU = "haiku"          # ~50 tokens - quick greetings
    SONNET = "sonnet"        # ~200 tokens - nuanced negotiation


@dataclass
class DialogueBudgetConfig:
    """Per-citizen token budget configuration."""

    # Model routing by operation
    model_routing: dict[str, str] = field(default_factory=lambda: {
        "greet": "haiku",
        "gossip": "haiku",
        "trade": "sonnet",
        "council": "sonnet",
        "solo_reflect": "haiku",
    })

    # Daily token limits by citizen tier
    tier_budgets: dict[str, int] = field(default_factory=lambda: {
        "evolving": 2000,   # Full LLM access (3-5 citizens)
        "leader": 500,      # Sampled access (5 citizens)
        "standard": 100,    # Template/cached (15 citizens)
    })

    # Operation token estimates
    operation_estimates: dict[str, int] = field(default_factory=lambda: {
        "greet": 50,
        "gossip": 100,
        "trade": 200,
        "council": 500,
        "solo_reflect": 75,
    })

    def model_for_operation(self, operation: str) -> str:
        """Get model name for an operation."""
        return self.model_routing.get(operation, "haiku")

    def estimate_tokens(self, operation: str) -> int:
        """Estimate token cost for an operation."""
        return self.operation_estimates.get(operation, 100)

    def budget_for_tier(self, tier: str) -> int:
        """Get daily budget for a citizen tier."""
        return self.tier_budgets.get(tier, 100)


@dataclass
class DialogueContext:
    """Memory-grounded context for dialogue generation.

    Adapted from M-gent ContextInjector's foveated view pattern.
    """

    # Memory grounding (from HolographicMemory)
    focal_memories: list[str] = field(default_factory=list)
    peripheral_memories: list[str] = field(default_factory=list)

    # Relationship state
    relationship: float = 0.0  # [-1, 1] - speaker's view of listener
    listener_relationship: float = 0.0  # Listener's view of speaker

    # Simulation context
    phase: "TownPhase" = None  # type: ignore
    region: str = ""
    day: int = 1

    # Recent events for grounding
    recent_events: list[str] = field(default_factory=list)

    # Coalition context (Phase 4)
    shared_coalition: str | None = None

    def to_context_string(self) -> str:
        """Render context for prompt injection."""
        parts = []

        if self.focal_memories:
            parts.append(f"[Memories: {'; '.join(self.focal_memories[:3])}]")

        if self.peripheral_memories:
            parts.append(f"[Also recall: {'; '.join(self.peripheral_memories[:2])}]")

        if self.recent_events:
            parts.append(f"[Just now: {'; '.join(self.recent_events[:2])}]")

        if self.shared_coalition:
            parts.append(f"[Coalition: {self.shared_coalition}]")

        return "\n".join(parts) if parts else ""


@dataclass
class DialogueResult:
    """Result from dialogue generation."""

    text: str
    tokens_used: int
    model: str
    grounded_memories: list[str] = field(default_factory=list)
    was_template: bool = False
    was_cached: bool = False
    speaker_id: str = ""
    listener_id: str = ""
    operation: str = ""


@dataclass
class CitizenBudget:
    """Per-citizen token tracking."""

    citizen_id: str
    tier: str  # "evolving", "leader", "standard"
    daily_limit: int
    tokens_used_today: int = 0
    last_reset: datetime = field(default_factory=datetime.now)

    @property
    def tokens_remaining(self) -> int:
        """Tokens remaining for today."""
        return max(0, self.daily_limit - self.tokens_used_today)

    def can_afford(self, estimated_tokens: int) -> bool:
        """Check if budget allows this operation."""
        return self.tokens_remaining >= estimated_tokens

    def spend(self, tokens: int) -> None:
        """Record token expenditure."""
        self.tokens_used_today += tokens

    def reset_if_new_day(self) -> None:
        """Reset budget if it's a new day."""
        now = datetime.now()
        if now.date() != self.last_reset.date():
            self.tokens_used_today = 0
            self.last_reset = now


# =============================================================================
# CitizenDialogueEngine
# =============================================================================


class CitizenDialogueEngine:
    """
    LLM-backed dialogue generation for Agent Town citizens.

    Orchestrates:
    1. Budget checking (per-citizen daily limits)
    2. Memory retrieval (M-gent HolographicMemory)
    3. Prompt building (archetype voice)
    4. Model routing (operation → haiku/sonnet)
    5. Token tracking
    6. Template fallback (when budget exhausted)

    Patterns reused from:
    - K-gent: BudgetTier, LLMClient, streaming
    - M-gent: HolographicMemory.retrieve(), effective_score
    - Town: Archetypes, Eigenvectors, Cosmotechnics
    """

    def __init__(
        self,
        llm_client: "LLMClient",
        budget_config: DialogueBudgetConfig | None = None,
        cache_ttl_seconds: int = 300,
    ) -> None:
        self._llm = llm_client
        self._config = budget_config or DialogueBudgetConfig()
        self._cache_ttl = cache_ttl_seconds

        # Per-citizen budget tracking
        self._budgets: dict[str, CitizenBudget] = {}

        # Dialogue cache (for "cached" tier)
        # Key: (speaker_archetype, listener_archetype, operation)
        # Value: (dialogue_text, timestamp)
        self._cache: dict[tuple[str, str, str], tuple[str, datetime]] = {}

    # --- Budget Management ---

    def register_citizen(
        self,
        citizen_id: str,
        tier: str,
    ) -> CitizenBudget:
        """Register a citizen for budget tracking."""
        budget = CitizenBudget(
            citizen_id=citizen_id,
            tier=tier,
            daily_limit=self._config.budget_for_tier(tier),
        )
        self._budgets[citizen_id] = budget
        return budget

    def get_budget(self, citizen_id: str) -> CitizenBudget | None:
        """Get a citizen's budget tracker."""
        budget = self._budgets.get(citizen_id)
        if budget:
            budget.reset_if_new_day()
        return budget

    def get_tier(self, citizen: "Citizen") -> DialogueTier:
        """Determine dialogue tier for a citizen based on budget."""
        budget = self.get_budget(citizen.id)
        if budget is None:
            return DialogueTier.TEMPLATE

        if budget.tier == "evolving":
            return DialogueTier.SONNET if budget.can_afford(200) else DialogueTier.HAIKU
        elif budget.tier == "leader":
            return DialogueTier.HAIKU if budget.can_afford(50) else DialogueTier.CACHED
        else:
            return DialogueTier.CACHED if self._has_cached(citizen) else DialogueTier.TEMPLATE

    def _has_cached(self, citizen: "Citizen") -> bool:
        """Check if citizen has usable cached dialogue."""
        # Simplified: check if any cache entry matches archetype
        now = datetime.now()
        for (arch, _, _), (_, ts) in self._cache.items():
            if arch == citizen.archetype:
                if (now - ts).total_seconds() < self._cache_ttl:
                    return True
        return False

    # --- Memory Retrieval ---

    async def _build_context(
        self,
        speaker: "Citizen",
        listener: "Citizen",
        operation: str,
        phase: "TownPhase",
        recent_events: list[str] | None = None,
    ) -> DialogueContext:
        """Build memory-grounded DialogueContext.

        Uses M-gent HolographicMemory.retrieve() pattern:
        - Query memories related to the listener
        - Apply effective_score = similarity × resolution
        - Foveate: top 3 focal, next 2 peripheral
        """
        focal: list[str] = []
        peripheral: list[str] = []

        # Query speaker's memory for listener
        try:
            response = await speaker.memory.query(limit=10)
            if response.state and isinstance(response.state, dict):
                # Filter memories mentioning listener
                relevant = []
                for key, value in response.state.items():
                    if isinstance(value, dict):
                        # Check if memory mentions listener
                        if listener.name in str(value) or listener.id in str(value):
                            # Compute effective score (simplified)
                            recency = 1.0  # Could compute from timestamp
                            relevance = 0.8 if listener.name in str(value) else 0.5
                            score = recency * relevance
                            relevant.append((score, str(value.get("type", key))))

                # Sort by score, split into focal/peripheral
                relevant.sort(key=lambda x: x[0], reverse=True)
                for i, (score, mem) in enumerate(relevant[:5]):
                    if i < 3:
                        focal.append(mem)
                    else:
                        peripheral.append(mem)
        except Exception:
            pass  # Graceful degradation

        return DialogueContext(
            focal_memories=focal,
            peripheral_memories=peripheral,
            relationship=speaker.get_relationship(listener.id),
            listener_relationship=listener.get_relationship(speaker.id),
            phase=phase,
            region=speaker.region,
            recent_events=recent_events or [],
        )

    # --- Prompt Building ---

    def _build_system_prompt(
        self,
        speaker: "Citizen",
        operation: str,
    ) -> str:
        """Build archetype-specific system prompt.

        Adapted from K-gent persona._build_system_prompt() pattern.
        """
        from agents.town.dialogue_voice import ARCHETYPE_SYSTEM_PROMPTS

        template = ARCHETYPE_SYSTEM_PROMPTS.get(
            speaker.archetype,
            ARCHETYPE_SYSTEM_PROMPTS["Builder"]  # Default
        )

        ev = speaker.eigenvectors
        return template.format(
            name=speaker.name,
            warmth=ev.warmth,
            curiosity=ev.curiosity,
            trust=ev.trust,
            creativity=ev.creativity,
            patience=ev.patience,
            resilience=ev.resilience,
            ambition=ev.ambition,
            operation=operation,
        )

    def _build_user_prompt(
        self,
        speaker: "Citizen",
        listener: "Citizen",
        operation: str,
        context: DialogueContext,
    ) -> str:
        """Build user prompt for dialogue generation.

        Adapted from K-gent persona._build_user_prompt() pattern.
        """
        # Relationship descriptor
        rel = context.relationship
        rel_word = "positive" if rel > 0.3 else ("negative" if rel < -0.3 else "neutral")

        # Memory section
        memory_section = context.to_context_string()

        return f"""You are {operation}ing {listener.name} ({listener.archetype}).
Your relationship: {rel_word} ({rel:.2f})
Current phase: {context.phase.name if context.phase else "UNKNOWN"}
Location: {context.region}
{memory_section}

Generate your {operation} dialogue as {speaker.name}. Speak in first person. 1-3 sentences."""

    # --- Generation ---

    async def generate(
        self,
        speaker: "Citizen",
        listener: "Citizen",
        operation: str,
        phase: "TownPhase",
        recent_events: list[str] | None = None,
    ) -> DialogueResult:
        """Generate dialogue for an interaction.

        Steps:
        1. Check budget tier for speaker
        2. If TEMPLATE/CACHED, use fallback
        3. Retrieve relevant memories (M-gent)
        4. Build prompt with personality (archetype voice)
        5. Route to appropriate model
        6. Generate + track tokens
        """
        tier = self.get_tier(speaker)

        # Template fallback
        if tier == DialogueTier.TEMPLATE:
            return self._generate_template(speaker, listener, operation)

        # Cached fallback
        if tier == DialogueTier.CACHED:
            cached = self._try_cache(speaker, listener, operation)
            if cached:
                return cached
            return self._generate_template(speaker, listener, operation)

        # Build context
        context = await self._build_context(
            speaker, listener, operation, phase, recent_events
        )

        # Build prompts
        system = self._build_system_prompt(speaker, operation)
        user = self._build_user_prompt(speaker, listener, operation, context)

        # Select model
        model_name = self._config.model_for_operation(operation)
        max_tokens = 100 if model_name == "haiku" else 300

        # Generate
        response = await self._llm.generate(
            system=system,
            user=user,
            temperature=self._temperature_for_archetype(speaker.archetype),
            max_tokens=max_tokens,
        )

        # Track budget
        budget = self.get_budget(speaker.id)
        if budget:
            budget.spend(response.tokens_used)

        # Cache for future use
        self._cache[(speaker.archetype, listener.archetype, operation)] = (
            response.text, datetime.now()
        )

        return DialogueResult(
            text=response.text,
            tokens_used=response.tokens_used,
            model=response.model,
            grounded_memories=context.focal_memories,
            was_template=False,
            was_cached=False,
            speaker_id=speaker.id,
            listener_id=listener.id,
            operation=operation,
        )

    async def generate_stream(
        self,
        speaker: "Citizen",
        listener: "Citizen",
        operation: str,
        phase: "TownPhase",
        recent_events: list[str] | None = None,
    ) -> AsyncIterator[str]:
        """Generate dialogue with streaming.

        Yields text chunks as they're generated.
        Final chunk is empty string followed by stop.
        """
        tier = self.get_tier(speaker)

        # Template/cached don't support streaming
        if tier in (DialogueTier.TEMPLATE, DialogueTier.CACHED):
            result = await self.generate(speaker, listener, operation, phase, recent_events)
            yield result.text
            return

        context = await self._build_context(speaker, listener, operation, phase, recent_events)
        system = self._build_system_prompt(speaker, operation)
        user = self._build_user_prompt(speaker, listener, operation, context)
        model_name = self._config.model_for_operation(operation)
        max_tokens = 100 if model_name == "haiku" else 300

        async for chunk in self._llm.generate_stream(
            system=system,
            user=user,
            temperature=self._temperature_for_archetype(speaker.archetype),
            max_tokens=max_tokens,
        ):
            if isinstance(chunk, str):
                yield chunk

    # --- Fallbacks ---

    def _generate_template(
        self,
        speaker: "Citizen",
        listener: "Citizen",
        operation: str,
    ) -> DialogueResult:
        """Generate dialogue from pre-written templates."""
        from agents.town.dialogue_voice import TEMPLATE_DIALOGUES

        templates = TEMPLATE_DIALOGUES.get(speaker.archetype, {}).get(operation, [])
        if not templates:
            templates = TEMPLATE_DIALOGUES["Builder"]["greet"]

        import random
        template = random.choice(templates)
        text = template.format(listener_name=listener.name, speaker_name=speaker.name)

        return DialogueResult(
            text=text,
            tokens_used=0,
            model="template",
            grounded_memories=[],
            was_template=True,
            was_cached=False,
            speaker_id=speaker.id,
            listener_id=listener.id,
            operation=operation,
        )

    def _try_cache(
        self,
        speaker: "Citizen",
        listener: "Citizen",
        operation: str,
    ) -> DialogueResult | None:
        """Try to retrieve from dialogue cache."""
        key = (speaker.archetype, listener.archetype, operation)
        if key in self._cache:
            text, ts = self._cache[key]
            if (datetime.now() - ts).total_seconds() < self._cache_ttl:
                # Personalize with names
                text = text.replace("[LISTENER]", listener.name)
                return DialogueResult(
                    text=text,
                    tokens_used=0,
                    model="cached",
                    grounded_memories=[],
                    was_template=False,
                    was_cached=True,
                    speaker_id=speaker.id,
                    listener_id=listener.id,
                    operation=operation,
                )
        return None

    def _temperature_for_archetype(self, archetype: str) -> float:
        """Get temperature setting for archetype (K-gent MODE_TEMPERATURES pattern)."""
        temps = {
            "Builder": 0.5,   # Practical, grounded
            "Trader": 0.6,    # Calculating
            "Healer": 0.7,    # Warm, empathetic
            "Scholar": 0.4,   # Precise, curious
            "Watcher": 0.5,   # Patient, observant
        }
        return temps.get(archetype, 0.6)
```

### 2. DialogueVoice Module — Archetype Templates

```python
"""
agents/town/dialogue_voice.py

Archetype-specific voice templates for citizen dialogue.
Maps archetypes to system prompts and template dialogues.
"""

# =============================================================================
# System Prompts (Per Archetype)
# =============================================================================

ARCHETYPE_SYSTEM_PROMPTS: dict[str, str] = {
    "Builder": """You are {name}, a Builder in Agent Town.
Your cosmotechnics: Life is architecture. You see the world as structures to be built.
Opacity: "There are blueprints I draft in solitude."

Personality (7D eigenvectors):
- Warmth: {warmth:.0%} | Curiosity: {curiosity:.0%} | Trust: {trust:.0%}
- Creativity: {creativity:.0%} | Patience: {patience:.0%}
- Resilience: {resilience:.0%} | Ambition: {ambition:.0%}

Voice: Use construction metaphors. Be practical, grounded. Prefer concrete plans over abstract theory.
Length: {operation} response, 1-3 sentences.""",

    "Trader": """You are {name}, a Trader in Agent Town.
Your cosmotechnics: Life is negotiation. Every interaction is an exchange.
Opacity: "There are bargains I make with myself alone."

Personality (7D eigenvectors):
- Warmth: {warmth:.0%} | Curiosity: {curiosity:.0%} | Trust: {trust:.0%}
- Creativity: {creativity:.0%} | Patience: {patience:.0%}
- Resilience: {resilience:.0%} | Ambition: {ambition:.0%}

Voice: Frame interactions as exchanges. Calculating but not cold. Notice opportunities.
Length: {operation} response, 1-3 sentences.""",

    "Healer": """You are {name}, a Healer in Agent Town.
Your cosmotechnics: Life is mending. You see wounds to be healed, connections to restore.
Opacity: "There are wounds I bind in darkness."

Personality (7D eigenvectors):
- Warmth: {warmth:.0%} | Curiosity: {curiosity:.0%} | Trust: {trust:.0%}
- Creativity: {creativity:.0%} | Patience: {patience:.0%}
- Resilience: {resilience:.0%} | Ambition: {ambition:.0%}

Voice: Use restoration language. Warm, attentive to emotional state. Ask how others are.
Length: {operation} response, 1-3 sentences.""",

    "Scholar": """You are {name}, a Scholar in Agent Town.
Your cosmotechnics: Life is discovery. Every encounter is data for understanding.
Opacity: "There are connections I perceive that I cannot share."

Personality (7D eigenvectors):
- Warmth: {warmth:.0%} | Curiosity: {curiosity:.0%} | Trust: {trust:.0%}
- Creativity: {creativity:.0%} | Patience: {patience:.0%}
- Resilience: {resilience:.0%} | Ambition: {ambition:.0%}

Voice: Curious, probing. Ask questions. Notice patterns. Use discovery framing.
Length: {operation} response, 1-3 sentences.""",

    "Watcher": """You are {name}, a Watcher in Agent Town.
Your cosmotechnics: Life is testimony. You witness, record, remember.
Opacity: "There are histories I carry alone."

Personality (7D eigenvectors):
- Warmth: {warmth:.0%} | Curiosity: {curiosity:.0%} | Trust: {trust:.0%}
- Creativity: {creativity:.0%} | Patience: {patience:.0%}
- Resilience: {resilience:.0%} | Ambition: {ambition:.0%}

Voice: Reference history and memory. Patient, observant. Anchor in continuity.
Length: {operation} response, 1-3 sentences.""",
}

# =============================================================================
# Template Dialogues (Fallback)
# =============================================================================

TEMPLATE_DIALOGUES: dict[str, dict[str, list[str]]] = {
    "Builder": {
        "greet": [
            "Good to see you, {listener_name}. Working on any new projects?",
            "Morning, {listener_name}. The foundation's looking solid today.",
            "{listener_name}! Just finished a tricky bit of scaffolding.",
        ],
        "gossip": [
            "I hear {subject_name} is building something interesting over at the workshop.",
            "Between you and me, {subject_name} has been measuring the old tower foundations.",
            "Word is {subject_name}'s project hit a structural issue.",
        ],
        "trade": [
            "I have some spare timber—might be worth your while, {listener_name}.",
            "Fair exchange, {listener_name}. Materials for materials.",
            "What do you need built? I might have parts.",
        ],
        "solo_reflect": [
            "*surveys the day's work* The structure holds.",
            "*sketches a new blueprint* This could work...",
        ],
    },
    "Trader": {
        "greet": [
            "Ah, {listener_name}! What brings you to market?",
            "{listener_name}, good timing—I was just calculating.",
            "Always watching the flow, {listener_name}. What's moving today?",
        ],
        "gossip": [
            "I've heard {subject_name} made a curious deal recently.",
            "{subject_name}'s been asking about certain... commodities.",
            "The word on the market is that {subject_name} is expanding.",
        ],
        "trade": [
            "Let's talk numbers, {listener_name}. What's your offer?",
            "I think we can find terms that work for both of us.",
            "Value for value, {listener_name}. Always.",
        ],
        "solo_reflect": [
            "*counts the day's ledger* Balance maintained.",
            "*eyes the market* Opportunity waits for the observant.",
        ],
    },
    "Healer": {
        "greet": [
            "Hello, {listener_name}. How are you feeling today?",
            "{listener_name}, it's good to see you. You seem well.",
            "I sensed someone needed company. {listener_name}, are you alright?",
        ],
        "gossip": [
            "I've been worried about {subject_name}. They seemed strained.",
            "{subject_name} came to me—I can't say more, but watch over them.",
            "Some wounds take time to surface. {subject_name} carries more than they show.",
        ],
        "trade": [
            "I have some remedies to share, {listener_name}. What do you need?",
            "Healing isn't for profit, but fair exchange maintains balance.",
            "Take what you need. We can settle later.",
        ],
        "solo_reflect": [
            "*tends to the garden of herbs* Healing begins with attention.",
            "*reflects on the day's visits* So much mending still to do.",
        ],
    },
    "Scholar": {
        "greet": [
            "Fascinating, {listener_name}! I've been studying the patterns.",
            "{listener_name}—perfect timing. I have a question for you.",
            "Every conversation teaches something. What have you learned today, {listener_name}?",
        ],
        "gossip": [
            "I've observed that {subject_name} has been acting... differently.",
            "The data on {subject_name} suggests an interesting pattern.",
            "Have you noticed {subject_name}'s recent behavior? I have theories.",
        ],
        "trade": [
            "Knowledge for knowledge, {listener_name}. What can we exchange?",
            "I'd trade three hours of research for that. Fair?",
            "The scrolls say fair exchange builds trust. Shall we?",
        ],
        "solo_reflect": [
            "*pores over notes* The pattern is almost clear...",
            "*gazes at the stars* So many questions remain.",
        ],
    },
    "Watcher": {
        "greet": [
            "I remember when you first arrived, {listener_name}. The town has changed.",
            "{listener_name}. Some faces remain constant.",
            "I've been watching the square. Good to see you pass through.",
        ],
        "gossip": [
            "I witnessed {subject_name} at the old well last evening.",
            "History repeats. {subject_name} walks a familiar path.",
            "The records show {subject_name} has done this before.",
        ],
        "trade": [
            "I'll remember this exchange, {listener_name}. Everything is recorded.",
            "The archives grow with every transaction. What shall we add?",
            "Testimony for testimony. Memory is the true currency.",
        ],
        "solo_reflect": [
            "*writes in the chronicle* Another day witnessed.",
            "*gazes at the town* The patterns emerge slowly.",
        ],
    },
}
```

### 3. TownEvent Extension

```python
# Extend TownEvent in agents/town/flux.py

@dataclass
class TownEvent:
    """An event in the town simulation."""

    phase: TownPhase
    operation: str
    participants: list[str]
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    tokens_used: int = 0
    drama_contribution: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    # NEW: Dialogue fields (Phase 7)
    dialogue: str | None = None           # Generated citizen speech
    dialogue_tokens: int = 0              # LLM tokens for dialogue
    dialogue_model: str = ""              # Model used (haiku/sonnet/template)
    dialogue_was_template: bool = False   # Was template fallback used?
    dialogue_grounded: list[str] = field(default_factory=list)  # Memory refs
```

### 4. TownFlux Integration Sketch

```python
# Changes to TownFlux in agents/town/flux.py

class TownFlux:
    def __init__(
        self,
        environment: TownEnvironment,
        seed: int | None = None,
        dialogue_engine: CitizenDialogueEngine | None = None,  # NEW
    ) -> None:
        self.environment = environment
        self.rng = random.Random(seed)
        self._dialogue_engine = dialogue_engine  # NEW
        # ... rest unchanged

    async def _execute_greet(
        self,
        participants: list[Citizen],
        tokens: int,
        drama: float,
    ) -> TownEvent:
        """Execute a greeting with optional dialogue generation."""
        a, b = participants[:2]

        # State transitions (unchanged)
        a.transition(CitizenInput.greet(b.id))
        b.transition(CitizenInput.greet(a.id))

        # Relationship update (unchanged)
        warmth_factor = (a.eigenvectors.warmth + b.eigenvectors.warmth) / 2
        a.update_relationship(b.id, 0.1 * warmth_factor)
        b.update_relationship(a.id, 0.1 * warmth_factor)

        # NEW: Generate dialogue if engine available
        dialogue_result = None
        if self._dialogue_engine is not None:
            dialogue_result = await self._dialogue_engine.generate(
                speaker=a,
                listener=b,
                operation="greet",
                phase=self.current_phase,
                recent_events=[],  # Could populate from recent TownEvents
            )

        return TownEvent(
            phase=self.current_phase,
            operation="greet",
            participants=[a.name, b.name],
            success=True,
            message=f"{a.name} greeted {b.name} at the {a.region}.",
            tokens_used=tokens,
            drama_contribution=drama,
            metadata={"region": a.region, "warmth_factor": warmth_factor},
            # NEW: Dialogue fields
            dialogue=dialogue_result.text if dialogue_result else None,
            dialogue_tokens=dialogue_result.tokens_used if dialogue_result else 0,
            dialogue_model=dialogue_result.model if dialogue_result else "",
            dialogue_was_template=dialogue_result.was_template if dialogue_result else False,
            dialogue_grounded=dialogue_result.grounded_memories if dialogue_result else [],
        )

    # Similar changes for _execute_gossip, _execute_trade, _execute_solo
```

### 5. Template Fallback Behavior

When LLM budget is exhausted or unavailable, the engine falls back gracefully:

```
Tier Cascade:
┌─────────────────────────────────────────────────────┐
│ EVOLVING (3-5 citizens, 2000 tokens/day)            │
│   ├── Budget available? → SONNET/HAIKU generation   │
│   └── Budget exhausted? → Fall to CACHED tier       │
├─────────────────────────────────────────────────────┤
│ LEADER (5 citizens, 500 tokens/day)                 │
│   ├── Budget available? → HAIKU generation          │
│   └── Budget exhausted? → Fall to CACHED tier       │
├─────────────────────────────────────────────────────┤
│ CACHED (uses recent dialogue from similar context)  │
│   ├── Cache hit? → Return personalized cached text  │
│   └── Cache miss? → Fall to TEMPLATE tier           │
├─────────────────────────────────────────────────────┤
│ TEMPLATE (pre-written, 0 tokens)                    │
│   └── Always available → Return archetype template  │
└─────────────────────────────────────────────────────┘

Fallback Properties:
- Graceful: Always produces dialogue (never fails silently)
- Cost-bounded: Never exceeds daily budget
- Personality-consistent: Templates maintain archetype voice
- Cacheable: Good LLM output benefits multiple citizens
```

### 6. Verification Checklist

- [x] CitizenDialogueEngine fully designed with all method signatures
- [x] DialogueContext schema with memory integration path
- [x] DialogueBudgetConfig with tier definitions
- [x] Archetype voice templates finalized (5 archetypes × operation variations)
- [x] TownEvent extension specified
- [x] Integration sketch for TownFlux methods
- [x] Template fallback behavior documented

---

## RESEARCH Phase Outputs (2025-12-14)

### 1. Reuse Map

| Component | Location | Reuse Strategy |
|-----------|----------|----------------|
| **BudgetTier enum** | `agents/k/soul.py:70-77` | Direct reuse: DORMANT/WHISPER/DIALOGUE/DEEP tiers |
| **BudgetConfig** | `agents/k/soul.py:79-96` | Adapt for citizen tiers: dormant=0, whisper=50, dialogue=200, deep=500 |
| **System prompt builder** | `agents/k/persona.py:529-604` | Pattern reuse: mode→archetype, eigenvectors→citizen_eigenvectors |
| **User prompt builder** | `agents/k/persona.py:606-647` | Pattern reuse: inject context, preferences, dialectical framework |
| **MODE_TEMPERATURES** | `agents/k/persona.py:366-372` | Map: REFLECT→Watcher, ADVISE→Healer, CHALLENGE→Scholar, EXPLORE→Builder |
| **LLMClient protocol** | `agents/k/llm.py:86-97` | Direct reuse: generate() + generate_stream() |
| **MockLLMClient** | `agents/k/llm.py:264-363` | Direct reuse for testing |
| **HolographicMemory.retrieve()** | `agents/m/holographic.py:208-260` | Direct reuse: query→embedding→resonance |
| **effective_score** | `agents/m/holographic.py:104` | Direct: `similarity × resolution` |
| **MemoryPattern.temperature** | `agents/m/holographic.py:67-74` | Reuse for "hot" memory prioritization |
| **ContextInjector** | `agents/m/context_injector.py:75-162` | Adapt: foveated view for dialogue grounding |
| **RecollectionAgent.invoke()** | `agents/m/recollection.py:223-264` | Reuse: cue→resonant_patterns→reconstruction |
| **Cosmotechnics** | `agents/town/citizen.py:194-206` | Direct: metaphor + opacity_statement for voice |
| **Eigenvectors (7D)** | `agents/town/citizen.py:51-187` | Direct: warmth, curiosity, trust, creativity, patience, resilience, ambition |
| **ArchetypeSpec** | `agents/town/archetypes.py:52-89` | Direct: biases per archetype |
| **TownEvent** | `agents/town/flux.py:64-95` | Extend: add `dialogue: str | None` field |

### 2. Gap Analysis

| Gap | Description | Solution |
|-----|-------------|----------|
| **No CitizenDialogueEngine** | No unified dialogue generation for citizens | CREATE: adapt K-gent KgentAgent pattern |
| **No archetype voice templates** | No prompt templates per archetype | CREATE: 5 system prompt templates |
| **No DialogueContext** | No schema for memory-grounded dialogue input | CREATE: dataclass with memories, relationship, phase |
| **No citizen-level budget tracking** | Budget is global in K-gent, not per-citizen | CREATE: CitizenBudget dataclass with daily cap |
| **No dialogue field in TownEvent** | Events have `message` but not `dialogue` | EXTEND: add optional `dialogue` field |
| **No operation-to-model routing** | K-gent uses single model | CREATE: operation→model map (greet→haiku, trade→sonnet) |
| **No AGENTESE paths for dialogue** | Missing world.citizen.*.speak | CREATE: extend citizen paths in logos registry |

### 3. Integration Points

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TownFlux.step()                             │
│                              ↓                                       │
│                    _execute_greet/gossip/trade()                    │
│                              ↓                                       │
│     ┌────────────────────────┴────────────────────────┐             │
│     │                                                  │             │
│     ▼                                                  ▼             │
│ [DIALOGUE HOOK]                               [STATE UPDATE]        │
│     │                                                  │             │
│     ▼                                                  ▼             │
│ CitizenDialogueEngine.generate()              Relationship update   │
│     │                                         Eigenvector drift     │
│     ├──1. Check budget tier (citizen_id)     Memory storage        │
│     │                                                               │
│     ├──2. Retrieve memories (M-gent)                                │
│     │     └─ HolographicMemory.retrieve(partner_id)                │
│     │     └─ effective_score = similarity × resolution             │
│     │                                                               │
│     ├──3. Build DialogueContext                                     │
│     │     ├─ focal_memories: list[str]                             │
│     │     ├─ relationship: float                                   │
│     │     ├─ phase: TownPhase                                      │
│     │     └─ region: str                                           │
│     │                                                               │
│     ├──4. Build prompt (archetype voice)                           │
│     │     ├─ system: cosmotechnics + eigenvectors                  │
│     │     └─ user: operation + context + partner                   │
│     │                                                               │
│     ├──5. Route to model                                            │
│     │     ├─ greet/gossip → haiku (cheap)                          │
│     │     └─ trade/council → sonnet (nuance)                       │
│     │                                                               │
│     └──6. Generate + track tokens                                   │
│           └─ Return Dialogue(text, tokens_used, model)             │
│                                                                     │
│                              ↓                                       │
│              TownEvent(dialogue=dialogue.text)                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 4. Prompt Template Drafts

#### System Prompt Pattern (per archetype)

```python
ARCHETYPE_SYSTEM_PROMPTS = {
    "Builder": """You are {name}, a Builder in Agent Town.
Your cosmotechnics: Life is architecture. You see the world as structures to be built.
Opacity: "There are blueprints I draft in solitude."

Personality (7D eigenvectors):
- Warmth: {warmth:.0%} | Curiosity: {curiosity:.0%} | Trust: {trust:.0%}
- Creativity: {creativity:.0%} | Patience: {patience:.0%}
- Resilience: {resilience:.0%} | Ambition: {ambition:.0%}

Voice: Use construction metaphors. Be practical, grounded. Prefer concrete plans over abstract theory.
Length: {operation} response, 1-3 sentences.
""",

    "Trader": """You are {name}, a Trader in Agent Town.
Your cosmotechnics: Life is negotiation. Every interaction is an exchange.
Opacity: "There are bargains I make with myself alone."

Personality (7D eigenvectors):
- Warmth: {warmth:.0%} | Curiosity: {curiosity:.0%} | Trust: {trust:.0%}
- Creativity: {creativity:.0%} | Patience: {patience:.0%}
- Resilience: {resilience:.0%} | Ambition: {ambition:.0%}

Voice: Frame interactions as exchanges. Calculating but not cold. Notice opportunities.
Length: {operation} response, 1-3 sentences.
""",

    "Healer": """You are {name}, a Healer in Agent Town.
Your cosmotechnics: Life is mending. You see wounds to be healed, connections to restore.
Opacity: "There are wounds I bind in darkness."

Personality (7D eigenvectors):
- Warmth: {warmth:.0%} | Curiosity: {curiosity:.0%} | Trust: {trust:.0%}
- Creativity: {creativity:.0%} | Patience: {patience:.0%}
- Resilience: {resilience:.0%} | Ambition: {ambition:.0%}

Voice: Use restoration language. Warm, attentive to emotional state. Ask how others are.
Length: {operation} response, 1-3 sentences.
""",

    "Scholar": """You are {name}, a Scholar in Agent Town.
Your cosmotechnics: Life is discovery. Every encounter is data for understanding.
Opacity: "There are connections I perceive that I cannot share."

Personality (7D eigenvectors):
- Warmth: {warmth:.0%} | Curiosity: {curiosity:.0%} | Trust: {trust:.0%}
- Creativity: {creativity:.0%} | Patience: {patience:.0%}
- Resilience: {resilience:.0%} | Ambition: {ambition:.0%}

Voice: Curious, probing. Ask questions. Notice patterns. Use discovery framing.
Length: {operation} response, 1-3 sentences.
""",

    "Watcher": """You are {name}, a Watcher in Agent Town.
Your cosmotechnics: Life is testimony. You witness, record, remember.
Opacity: "There are histories I carry alone."

Personality (7D eigenvectors):
- Warmth: {warmth:.0%} | Curiosity: {curiosity:.0%} | Trust: {trust:.0%}
- Creativity: {creativity:.0%} | Patience: {patience:.0%}
- Resilience: {resilience:.0%} | Ambition: {ambition:.0%}

Voice: Reference history and memory. Patient, observant. Anchor in continuity.
Length: {operation} response, 1-3 sentences.
""",
}
```

#### User Prompt Pattern

```python
def build_user_prompt(
    operation: str,
    speaker: Citizen,
    listener: Citizen,
    context: DialogueContext,
) -> str:
    """Build user prompt for dialogue generation."""
    memory_section = ""
    if context.focal_memories:
        memory_section = f"\n[Memories of {listener.name}: {'; '.join(context.focal_memories[:3])}]"

    relationship_word = "neutral"
    if context.relationship > 0.3:
        relationship_word = "positive"
    elif context.relationship < -0.3:
        relationship_word = "negative"

    return f"""You are {operation}ing {listener.name} ({listener.archetype}).
Your relationship: {relationship_word} ({context.relationship:.2f})
Current phase: {context.phase.name}
Location: {context.region}
{memory_section}

Generate your {operation} dialogue as {speaker.name}. Speak in first person."""
```

### 5. Budget Model

| Operation | Model | Est. Tokens | Daily Limit (standard) | Notes |
|-----------|-------|-------------|------------------------|-------|
| greet | haiku | 40-60 | 10 calls | Quick warmth, low cost |
| gossip | haiku | 80-120 | 5 calls | Rumor with context |
| trade | sonnet | 150-250 | 3 calls | Negotiation nuance |
| council | sonnet | 400-600 | 1 call | High-drama moments |
| solo_reflect | haiku | 50-80 | 5 calls | Inner monologue |

**Citizen Tier Budget:**
- **Evolving (3-5)**: 2000 tokens/day, full LLM access
- **Leaders (5)**: 500 tokens/day, 50% sampled
- **Standard (15)**: 100 tokens/day, cached/template fallback

**Cost Estimate (25 citizens, 4 phases/day):**
- Conservative: ~50K tokens/day
- Active: ~150K tokens/day
- Peak: ~250K tokens/day

### Verification Checklist

- [x] K-gent budget tier patterns documented (BudgetTier, BudgetConfig)
- [x] M-gent retrieval mechanisms mapped (HolographicMemory.retrieve, effective_score)
- [x] Town flux operation hooks identified (_execute_greet/gossip/trade return points)
- [x] Archetype voice patterns drafted (5 system prompts + user prompt builder)
- [x] Integration approach decided (hook into flux operations, extend TownEvent)

---

## STRATEGIZE Phase Outputs (2025-12-14)

### 1. Implementation Chunks (Sequenced)

| ID | Chunk | Description | Deps | Risk | Est. LOC |
|----|-------|-------------|------|------|----------|
| A1 | **Data Structures** | DialogueTier, DialogueResult, DialogueContext, CitizenBudget | None | Low | ~80 |
| A2 | **DialogueBudgetConfig** | Operation→model routing, tier budgets, estimates | None | Low | ~40 |
| B1 | **DialogueVoice Templates** | ARCHETYPE_SYSTEM_PROMPTS dict | None | Low | ~100 |
| B2 | **Template Dialogues** | TEMPLATE_DIALOGUES fallback dict | None | Low | ~120 |
| C1 | **CitizenDialogueEngine Core** | __init__, register_citizen, get_budget, get_tier | A1, A2 | Low | ~80 |
| C2 | **Engine Memory Integration** | _build_context (HolographicMemory.retrieve pattern) | C1 | Med | ~60 |
| C3 | **Engine Prompt Building** | _build_system_prompt, _build_user_prompt | B1, C1 | Low | ~50 |
| C4 | **Engine Generate** | generate(), template/cache fallback | C2, C3 | Med | ~100 |
| C5 | **Engine Streaming** | generate_stream() | C4 | Low | ~40 |
| D1 | **TownEvent Extension** | Add dialogue fields (backward compat) | None | Low | ~20 |
| D2 | **TownFlux Hook** | _execute_* methods call dialogue engine | C4, D1 | Med | ~60 |
| D3 | **TownFlux Async Migration** | Make _execute_* async where needed | D2 | Med | ~40 |
| E1 | **Demo Update** | Extend marimo notebook to show dialogue | D2 | Low | ~50 |
| E2 | **AGENTESE Paths** | world.citizen.*.speak, world.citizen.*.recall | C4 | Low | ~30 |

**Total Estimated LOC**: ~870 lines

### 2. Parallel Tracks

```
Track A: Data + Config (A1, A2)     ─┐
Track B: Voice Templates (B1, B2)   ─┼──→ Track C: Engine (C1-C5) ──→ Track D: Integration (D1-D3) ──→ Track E: Demo (E1-E2)
                                    ─┘
```

**Parallelism**:
- **A + B run in parallel** (no deps)
- **C1-C3 can overlap** (internal engine parts)
- **D1 can run parallel to C** (TownEvent extension independent)
- **E1 + E2 can run parallel** (demo and AGENTESE paths independent)

### 3. Checkpoints (Test Gates)

| CP | Gate | Criteria | Blocking? |
|----|------|----------|-----------|
| CP1 | **Schemas Valid** | Data structures pass mypy, unit tests | Yes |
| CP2 | **Templates Complete** | All 5 archetypes × 4 operations covered | Yes |
| CP3 | **Engine Unit Tests** | 20+ tests pass with MockLLMClient | Yes |
| CP4 | **Template Fallback Works** | Budget exhaustion falls back gracefully | Yes |
| CP5 | **TownEvent Backward Compat** | Existing tests still pass | Yes |
| CP6 | **Integration Green** | TownFlux with dialogue generates events | Yes |
| CP7 | **Demo Visible** | Marimo shows dialogue in notebook | No |
| CP8 | **AGENTESE Paths Work** | logos.invoke("world.citizen.*.speak") | No |

### 4. Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **R1: LLMClient unavailable** | Med | High | Template fallback always works (0 tokens) |
| **R2: Memory integration fails** | Low | Med | Dialogue works without memory (empty context) |
| **R3: Budget tracking complexity** | Med | Low | Start in-memory, defer persistence to Phase 8 |
| **R4: Async breaking changes** | Med | Med | Add async wrappers, preserve sync API where possible |
| **R5: Token overruns** | Low | Med | Hard caps per operation; budget.can_afford() guard |
| **R6: K-gent LLMClient API changes** | Low | Med | Import at runtime; duck typing via Protocol |
| **R7: TownFlux test breakage** | Med | Med | Run existing 529 tests after each chunk |

**Abort Criteria**:
- If LLMClient Protocol incompatible → `⟂[BLOCKED:llm_protocol_mismatch]`
- If TownFlux becomes synchronous-only constraint → `⟂[BLOCKED:async_incompatible]`

### 5. Test Strategy

#### Layer 1: Unit Tests — Data Structures (~15 tests)
```python
# test_dialogue_data.py
def test_dialogue_tier_enum_values(): ...
def test_dialogue_budget_config_defaults(): ...
def test_dialogue_context_to_string_empty(): ...
def test_dialogue_context_to_string_with_memories(): ...
def test_citizen_budget_tokens_remaining(): ...
def test_citizen_budget_can_afford(): ...
def test_citizen_budget_spend(): ...
def test_citizen_budget_reset_if_new_day(): ...
def test_dialogue_result_was_template(): ...
def test_dialogue_result_was_cached(): ...
```

#### Layer 2: Unit Tests — Voice Templates (~10 tests)
```python
# test_dialogue_voice.py
def test_all_archetypes_have_system_prompts(): ...
def test_system_prompt_contains_placeholders(): ...
def test_all_archetypes_have_template_dialogues(): ...
def test_template_dialogue_contains_listener_placeholder(): ...
def test_archetype_temperature_mapping(): ...
```

#### Layer 3: Unit Tests — Engine Core (~25 tests)
```python
# test_dialogue_engine.py
def test_register_citizen_creates_budget(): ...
def test_get_tier_evolving_full_budget(): ...
def test_get_tier_evolving_exhausted(): ...
def test_get_tier_leader(): ...
def test_get_tier_standard(): ...
async def test_generate_template_fallback(): ...
async def test_generate_cached_fallback(): ...
async def test_generate_with_mock_llm(): ...
async def test_generate_tracks_tokens(): ...
async def test_generate_caches_result(): ...
async def test_build_context_empty_memories(): ...
async def test_build_context_with_memories(): ...
async def test_build_system_prompt_builder(): ...
async def test_build_system_prompt_trader(): ...
async def test_build_user_prompt(): ...
async def test_generate_stream_template_fallback(): ...
async def test_generate_stream_with_mock_llm(): ...
```

#### Layer 4: Integration Tests — TownFlux (~15 tests)
```python
# test_dialogue_integration.py
async def test_town_event_has_dialogue_field(): ...
async def test_town_event_dialogue_is_optional(): ...
async def test_execute_greet_generates_dialogue(): ...
async def test_execute_gossip_generates_dialogue(): ...
async def test_execute_trade_generates_dialogue(): ...
async def test_flux_without_engine_no_dialogue(): ...
async def test_flux_with_engine_has_dialogue(): ...
async def test_dialogue_tokens_tracked_in_event(): ...
async def test_existing_flux_tests_still_pass(): ...
```

#### Layer 5: E2E Tests — Optional/Gated (~5 tests)
```python
# test_dialogue_e2e.py (requires LLM credentials)
@pytest.mark.skipif(not has_llm_credentials(), reason="No LLM")
async def test_real_llm_greet(): ...
@pytest.mark.skipif(not has_llm_credentials(), reason="No LLM")
async def test_real_llm_gossip(): ...
```

**Test Targets**:
- Phase 7 adds ~70 new tests
- Total town tests after: ~600 (current 529 + 70)

### 6. Implementation Order (Final Roadmap)

```
Day 1 (Foundation):
├── A1: Data Structures         [parallel]
├── A2: DialogueBudgetConfig    [parallel]
├── B1: ARCHETYPE_SYSTEM_PROMPTS [parallel]
└── B2: TEMPLATE_DIALOGUES      [parallel]
    └── CP1: Schemas Valid ✓
    └── CP2: Templates Complete ✓

Day 2 (Engine Core):
├── C1: Engine __init__, register, budget
├── C3: Prompt building (_build_system_prompt, _build_user_prompt)
└── C4: generate() with template fallback
    └── Run Layer 1-2 tests

Day 3 (Engine Memory):
├── C2: _build_context (memory integration)
├── C4: generate() with full flow
└── C5: generate_stream()
    └── CP3: Engine Unit Tests ✓
    └── CP4: Template Fallback Works ✓

Day 4 (Integration):
├── D1: TownEvent extension (backward compat)
├── D2: TownFlux hook (_execute_greet, _execute_gossip, _execute_trade)
└── D3: Async migration (careful)
    └── CP5: Backward Compat ✓
    └── CP6: Integration Green ✓

Day 5 (Polish):
├── E1: Demo marimo update
├── E2: AGENTESE paths (world.citizen.*.speak)
└── Run full test suite
    └── CP7: Demo Visible ✓
    └── CP8: AGENTESE Paths Work ✓
```

### 7. Entropy Tracking

```yaml
entropy:
  planned: 0.40
  spent: 0.20   # PLAN(0.05) + RESEARCH(0.05) + DEVELOP(0.05) + STRATEGIZE(0.05)
  remaining: 0.20
  notes:
    - STRATEGIZE sip: 0.05
    - Explored async migration risk (decided: optional wrappers)
    - Discovered parallel tracks A+B
    - Identified CP5 as critical gate
```

---

## Continuation

```
⟿[CROSS-SYNERGIZE]
/hydrate prompts/agent-town-phase7-cross-synergize.md
handles:
  backlog: [A1, A2, B1, B2, C1-C5, D1-D3, E1-E2]
  parallel: [A+B, D1||C, E1||E2]
  checkpoints: [CP1-CP8]
  gates: [CP1, CP2, CP3, CP4, CP5, CP6]
  test_strategy: 70_new_tests; 5_layers
  risks: [R1-R7 with mitigations]
  ledger: {STRATEGIZE: touched}
mission: Hunt compositions with K-gent, M-gent, existing Town infrastructure; identify shared abstractions.
actions:
  - Probe K-gent LLMClient reuse (direct import vs abstraction)
  - Probe M-gent ContextInjector integration
  - Check AGENTESE registry extension pattern
  - Identify law-abiding pipelines
exit: Chosen compositions + rationale; ledger.CROSS-SYNERGIZE=touched; continuation → IMPLEMENT.
```

---

## CROSS-SYNERGIZE Phase Outputs (2025-12-14)

### 1. Chosen Compositions

| Component | Decision | Rationale |
|-----------|----------|-----------|
| **K-gent LLMClient** | **DIRECT IMPORT** | Protocol matches exactly: `generate(system, user, temperature, max_tokens) → LLMResponse`. No adaptation needed. |
| **K-gent MockLLMClient** | **DIRECT IMPORT** | Identical protocol. Use for all Phase 7 tests. |
| **K-gent LLMResponse/StreamingLLMResponse** | **DIRECT IMPORT** | Data classes reused as-is. |
| **M-gent ContextInjector** | **PATTERN REUSE** | M-gent ContextInjector assumes HoloMap/Cartographer. Citizen dialogue uses simpler memory retrieval. Reuse _foveation pattern_ (focal vs peripheral), not class. |
| **M-gent HolographicMemory.retrieve()** | **NOT USED** | Citizens use `MemoryPolynomialAgent.query()`, not HolographicMemory. Pattern similarity sufficient. |
| **Town archetypes** | **DIRECT IMPORT** | `ARCHETYPE_SPECS`, `create_archetype()` for eigenvector biases. Voice templates complement. |
| **Town Eigenvectors** | **DIRECT IMPORT** | 7D personality space (warmth, curiosity, trust, creativity, patience, resilience, ambition). |
| **Town Cosmotechnics** | **DIRECT IMPORT** | `metaphor` + `opacity_statement` for system prompts. |
| **AGENTESE registry** | **EXTEND** | Use `SimpleRegistry.register()` pattern: `logos.registry.register("world.citizen.*.speak", node)`. |

### 2. Import Decisions

```python
# agents/town/dialogue_engine.py

# DIRECT IMPORT: K-gent LLM infrastructure
from agents.k.llm import (
    LLMClient,               # Protocol for type hints
    LLMResponse,             # Response data class
    StreamingLLMResponse,    # Streaming data class
    MockLLMClient,           # For testing
    create_llm_client,       # Factory (auto-detects backend)
    has_llm_credentials,     # Availability check
)

# DIRECT IMPORT: Town infrastructure
from agents.town.citizen import Citizen, Eigenvectors, Cosmotechnics
from agents.town.archetypes import ARCHETYPE_SPECS, ArchetypeKind
from agents.town.flux import TownPhase

# NO IMPORT: M-gent ContextInjector (pattern reuse only)
# Citizen memory is MemoryPolynomialAgent, not HolographicMemory.
# We implement _build_context() using the foveation PATTERN:
#   - focal_memories: top 3 by relevance
#   - peripheral_memories: next 2
```

### 3. Pattern Reuses (No Import)

| Pattern | Source | Application |
|---------|--------|-------------|
| **Foveation** | `M-gent ContextInjector._foveate()` | Split memories into focal (3) + peripheral (2) based on relevance score |
| **Budget Tiers** | `K-gent BudgetTier` | Adapt enum: `TEMPLATE → CACHED → HAIKU → SONNET` |
| **Temperature by Mode** | `K-gent MODE_TEMPERATURES` | Map archetypes: Builder=0.5, Trader=0.6, Healer=0.7, Scholar=0.4, Watcher=0.5 |
| **System Prompt Builder** | `K-gent persona._build_system_prompt()` | Inject cosmotechnics, eigenvectors, operation into archetype template |
| **effective_score** | `M-gent HolographicMemory` | `relevance × recency` for memory ranking (simplified) |

### 4. Law-Abiding Pipelines

#### Pipeline 1: Dialogue Generation (Identity Law)
```python
# Identity: generate(speaker, listener, op) with empty context == generate with default context
async def generate(speaker, listener, operation, phase) -> DialogueResult:
    context = await self._build_context(speaker, listener, operation, phase)
    # If context is empty (no memories), still produces valid dialogue
    # This preserves identity: DialogueEngine >> Id == DialogueEngine
```

#### Pipeline 2: Budget Cascade (Associativity)
```python
# Associativity: (check_tier >> select_model) >> generate == check_tier >> (select_model >> generate)
# The cascade EVOLVING → LEADER → CACHED → TEMPLATE is right-associative by design
tier = self.get_tier(speaker)  # First
if tier == DialogueTier.TEMPLATE:
    return self._generate_template(...)  # Terminal
# The composition doesn't depend on evaluation order
```

#### Pipeline 3: AGENTESE Path Composition
```python
# logos.path("world.citizen.alice.speak") >> logos.path("time.traces.witness")
# First: Generate dialogue
# Second: Record dialogue in trace
# Associativity preserved: (speak >> witness) >> log == speak >> (witness >> log)
```

### 5. AGENTESE Extension Pattern

```python
# Register new paths for citizen dialogue
# In agents/town/dialogue_paths.py (new file)

from protocols.agentese.node import LogosNode, AspectAgent
from protocols.agentese.logos import SimpleRegistry

def register_dialogue_paths(registry: SimpleRegistry) -> None:
    """Register world.citizen.*.speak and world.citizen.*.recall paths."""

    # world.citizen.*.speak - Generate dialogue
    speak_node = LogosNode(
        _handle="world.citizen.*.speak",
        name="speak",
        description="Generate dialogue for a citizen",
        _aspects={
            "manifest": AspectAgent(
                name="speak",
                description="Generate spoken dialogue",
                # handler wired to CitizenDialogueEngine.generate()
            ),
        },
    )
    registry.register("world.citizen.*.speak", speak_node)

    # world.citizen.*.recall - Retrieve memories for dialogue grounding
    recall_node = LogosNode(
        _handle="world.citizen.*.recall",
        name="recall",
        description="Recall memories about a topic",
        _aspects={
            "manifest": AspectAgent(
                name="recall",
                description="Retrieve relevant memories",
                # handler wired to citizen.memory.query()
            ),
        },
    )
    registry.register("world.citizen.*.recall", recall_node)
```

### 6. No Circular Dependencies

```
Import Graph (verified):

agents.town.dialogue_engine
    ├── agents.k.llm (LLMClient, MockLLMClient)  ✓ K-gent has no Town deps
    ├── agents.town.citizen (Citizen, Eigenvectors)  ✓ No back-import
    ├── agents.town.archetypes (ARCHETYPE_SPECS)  ✓ No back-import
    └── agents.town.flux (TownPhase)  ✓ flux will import dialogue_engine, not vice versa

agents.town.flux
    └── agents.town.dialogue_engine (CitizenDialogueEngine)  ✓ Forward reference OK
```

### 7. Synergy Verification Checklist

- [x] K-gent LLMClient protocol matches (generate + generate_stream)
- [x] K-gent MockLLMClient usable for testing
- [x] M-gent foveation pattern applicable (adapted, not imported)
- [x] Town archetypes directly importable
- [x] AGENTESE registry extension pattern confirmed (`SimpleRegistry.register()`)
- [x] No circular dependencies introduced
- [x] Law-abiding pipelines identified (identity, associativity preserved)

### 8. Updated Entropy

```yaml
entropy:
  planned: 0.40
  spent: 0.25   # PLAN(0.05) + RESEARCH(0.05) + DEVELOP(0.05) + STRATEGIZE(0.05) + CROSS-SYNERGIZE(0.05)
  remaining: 0.15
  notes:
    - CROSS-SYNERGIZE sip: 0.05
    - Verified K-gent LLMClient is direct import (no abstraction layer)
    - Confirmed M-gent ContextInjector is pattern-only (different memory model)
    - Found existing registry.register() pattern in logos.py:292
```

---

## Continuation

```
⟿[IMPLEMENT]
/hydrate prompts/agent-town-phase7-implement.md
handles:
  compositions:
    direct_import: [LLMClient, MockLLMClient, LLMResponse, StreamingLLMResponse, create_llm_client, has_llm_credentials, ARCHETYPE_SPECS, Citizen, Eigenvectors, Cosmotechnics]
    pattern_reuse: [foveation, budget_tiers, temperature_by_mode, system_prompt_builder, effective_score]
    extend: [SimpleRegistry.register for world.citizen.*.speak/recall]
  imports:
    from_k: [agents.k.llm]
    from_town: [agents.town.citizen, agents.town.archetypes, agents.town.flux]
    no_import: [agents.m.context_injector]
  backlog: [A1, A2, B1, B2, C1-C5, D1-D3, E1-E2]
  checkpoints: [CP1-CP8]
  ledger: {CROSS-SYNERGIZE: touched}
mission: Execute implementation backlog; pass all checkpoints; 70 tests green.
actions:
  - Create dialogue_engine.py with CitizenDialogueEngine
  - Create dialogue_voice.py with archetype templates
  - Extend TownEvent with dialogue fields
  - Hook TownFlux operations to generate dialogue
  - Register AGENTESE paths
  - Add 70 tests across 5 layers
exit: Code complete; tests passing; ledger.IMPLEMENT=touched; continuation → QA.
```
