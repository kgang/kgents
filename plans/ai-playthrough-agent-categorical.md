# AI Playthrough Agent System: Categorical Foundation

> *"The playthrough IS the proof. The witness IS the evidence."*

**Status**: PLANNING
**Created**: 2026-01-10
**Goal**: Create a revelatory testing system that generates ASHC evidence through AI-driven gameplay, grounded in category theory.

---

## 1. Categorical Foundation

### 1.1 The Core Insight: Playthrough as Morphism

A playthrough is not a sequence of actions - it's a **morphism** in the category of game states:

```
Playthrough : InitialState → FinalState

Where:
- Objects = Game states (position, health, upgrades, wave, etc.)
- Morphisms = Valid state transitions (actions + game physics)
- Composition = Sequential gameplay
- Identity = "Do nothing" (time still passes)
```

### 1.2 Polynomial Functor: PlayAgent[S, A, B]

Following the kgents PolyAgent pattern, a playthrough agent is a polynomial functor:

```
PlayAgent[S, A, B] = Σ(s:S) B^(A_s)

Where:
- S = Agent modes: {Strategic, Tactical, Reflexive, Observing}
- A_s = Mode-dependent inputs:
    - Strategic: (GameState, Goals) → StrategicPlan
    - Tactical: (LocalState, Threats) → TacticalAction
    - Reflexive: (Stimulus) → ReflexAction
    - Observing: (ScreenCapture) → StateUpdate
- B = Unified output: (Action, DecisionTrace, WitnessData)
```

### 1.3 The Decision Operad

Agent decisions compose via an operad structure:

```
DECISION_OPERAD = {
    operations: {
        strategic: (n) → "Combine n strategic considerations into plan"
        tactical: (n) → "Combine n tactical factors into action"
        reflex: (1) → "Single stimulus → response"
        witness: (n) → "Combine n observations into evidence"
    },

    composition_law: (strategic ∘ tactical) ∘ reflex = strategic ∘ (tactical ∘ reflex)

    # Strategic decisions decompose into tactical, which decompose into reflexes
    # But the order of decomposition doesn't matter (associativity)
}
```

### 1.4 Human-Likeness as Galois Loss

The key insight: **Human-likeness is measurable as Galois loss**

```
L(agent) = d(agent_play, C(R(agent_play)))

Where:
- R: Restructure = Extract decision patterns from playthrough
- C: Canonicalize = Rebuild playthrough from patterns (using human model)
- d: Distance = How different is AI play from human-normalized play?

Low L = Agent plays like a human
High L = Agent plays unlike any human (too optimal, too random, etc.)
```

---

## 2. Architecture

### 2.1 System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CATEGORICAL PLAYTHROUGH SYSTEM                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PERCEPTION SHEAF                                                    │   │
│  │  Local observations → Global game understanding                      │   │
│  │                                                                      │   │
│  │  Section_visual: Canvas → VisualState                                │   │
│  │  Section_api: DebugAPI → APIState                                    │   │
│  │  Section_audio: AudioBuffer → AudioCues                              │   │
│  │                                                                      │   │
│  │  Gluing: VisualState ⊗ APIState ⊗ AudioCues → UnifiedPercept        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  DECISION POLYNOMIAL PlayAgent[Mode, Percept] → (Action, Witness)    │   │
│  │                                                                      │   │
│  │  Mode = Strategic | Tactical | Reflexive | Observing                 │   │
│  │                                                                      │   │
│  │  Strategic (LLM):                                                    │   │
│  │    "Given game state, what's my build strategy?"                     │   │
│  │    "Should I play aggressive or defensive this wave?"                │   │
│  │                                                                      │   │
│  │  Tactical (Heuristics + Small LLM):                                  │   │
│  │    "Which enemy is highest priority?"                                │   │
│  │    "When should I use my ability?"                                   │   │
│  │                                                                      │   │
│  │  Reflexive (Pure Functions):                                         │   │
│  │    "Projectile incoming → Dodge direction"                           │   │
│  │    "Health low → Retreat vector"                                     │   │
│  │                                                                      │   │
│  │  Observing (State Machine):                                          │   │
│  │    "Track enemy patterns, learn timings"                             │   │
│  │    "Build internal model of game dynamics"                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  HUMAN REACTION MODEL                                                │   │
│  │  Transforms ideal actions into human-like actions                    │   │
│  │                                                                      │   │
│  │  delay: Action → DelayedAction                                       │   │
│  │    base_reaction_ms ~ N(250, 50)                                     │   │
│  │    stress_factor: threat_level → multiplier                          │   │
│  │    fatigue_curve: elapsed_time → degradation                         │   │
│  │                                                                      │   │
│  │  precision: TargetAction → NoisyAction                               │   │
│  │    aim_noise ~ N(0, σ(stress))                                       │   │
│  │    timing_jitter ~ N(0, τ(fatigue))                                  │   │
│  │                                                                      │   │
│  │  attention: AllStimuli → AttendedStimuli                             │   │
│  │    saliency_filter: what would human notice?                         │   │
│  │    tunnel_vision: stress → narrower attention                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  WITNESS ACCUMULATOR                                                 │   │
│  │  Every decision leaves a trace                                       │   │
│  │                                                                      │   │
│  │  mark(action, reasoning, game_state, mode) → WitnessMark             │   │
│  │                                                                      │   │
│  │  Accumulated evidence:                                               │   │
│  │    - Decision traces with reasoning                                  │   │
│  │    - Flow state timeline                                             │   │
│  │    - Emergence events                                                │   │
│  │    - Balance observations                                            │   │
│  │    - Fun floor violations                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Agent Personas (Morphism Variations)

Each persona is a **different morphism** through the same categorical structure:

```python
AGENT_PERSONAS = {
    "aggressive": PlayAgent(
        strategic_bias="maximize_dps",
        risk_tolerance=0.8,
        reaction_skill=0.9,
        exploration_rate=0.2,
    ),

    "defensive": PlayAgent(
        strategic_bias="maximize_survival",
        risk_tolerance=0.2,
        reaction_skill=0.7,
        exploration_rate=0.3,
    ),

    "explorer": PlayAgent(
        strategic_bias="try_everything",
        risk_tolerance=0.5,
        reaction_skill=0.6,
        exploration_rate=0.9,
    ),

    "optimizer": PlayAgent(
        strategic_bias="follow_meta",
        risk_tolerance=0.5,
        reaction_skill=0.95,
        exploration_rate=0.1,
    ),

    "novice": PlayAgent(
        strategic_bias="random",
        risk_tolerance=0.4,
        reaction_skill=0.3,
        exploration_rate=0.5,
    ),

    "chaotic": PlayAgent(
        strategic_bias="random",
        risk_tolerance=0.9,
        reaction_skill=0.5,
        exploration_rate=1.0,
    ),
}
```

### 2.3 Parallel Farm: Product Category

Running N agents is a **product** in the category of playthroughs:

```
ParallelFarm = PlayAgent₁ × PlayAgent₂ × ... × PlayAgentₙ

Evidence = π₁(farm) ⊕ π₂(farm) ⊕ ... ⊕ πₙ(farm)

Where:
- × = Categorical product (run in parallel)
- πᵢ = Projection (extract individual evidence)
- ⊕ = Evidence combination (aggregate findings)
```

---

## 3. Implementation Spec

### 3.1 Core Types

```python
from dataclasses import dataclass
from enum import Enum
from typing import Callable, TypeVar

# Categorical primitives
S = TypeVar("S")  # State
A = TypeVar("A")  # Input
B = TypeVar("B")  # Output

class AgentMode(Enum):
    STRATEGIC = "strategic"    # Long-term planning (LLM)
    TACTICAL = "tactical"      # Short-term decisions (heuristics + small LLM)
    REFLEXIVE = "reflexive"    # Immediate reactions (pure functions)
    OBSERVING = "observing"    # State tracking (state machine)

@dataclass
class UnifiedPercept:
    """Sheaf gluing of all perception sections."""
    player: PlayerState
    enemies: list[EnemyState]
    projectiles: list[ProjectileState]
    upgrades: list[UpgradeState]
    wave: WaveState
    audio_cues: list[AudioCue]
    screen_hash: str  # For visual state tracking
    timestamp_ms: float

@dataclass
class DecisionTrace:
    """Witness mark for a decision."""
    mode: AgentMode
    percept_hash: str
    reasoning: str
    action_chosen: str
    alternatives_considered: list[str]
    confidence: float
    reaction_time_ms: float
    human_likeness_score: float

@dataclass
class WitnessEvidence:
    """Accumulated evidence from a playthrough."""
    traces: list[DecisionTrace]
    flow_timeline: list[FlowSample]
    emergence_events: list[EmergenceEvent]
    balance_observations: list[BalanceObservation]
    fun_floor_violations: list[FunFloorViolation]
    galois_loss: float
    humanness_score: float
```

### 3.2 Polynomial Agent Implementation

```python
class PlaythroughAgent:
    """
    Polynomial functor: PlayAgent[Mode, Percept] → (Action, Witness)

    Implements the categorical playthrough structure.
    """

    def __init__(self, persona: AgentPersona, llm_client: LLMClient):
        self.persona = persona
        self.llm = llm_client
        self.mode = AgentMode.OBSERVING
        self.witness = WitnessAccumulator()
        self.reaction_model = HumanReactionModel(persona.reaction_skill)

    async def perceive(self, game: GameInterface) -> UnifiedPercept:
        """Sheaf: Local sections → Global percept."""
        # Glue local observations into unified percept
        visual = await game.capture_screen()
        api_state = await game.get_debug_state()
        audio = await game.get_audio_cues()

        return UnifiedPercept(
            player=api_state.player,
            enemies=api_state.enemies,
            projectiles=self._extract_projectiles(visual, api_state),
            upgrades=api_state.available_upgrades,
            wave=api_state.wave,
            audio_cues=audio,
            screen_hash=hash(visual),
            timestamp_ms=time.time() * 1000,
        )

    async def decide(self, percept: UnifiedPercept) -> tuple[Action, DecisionTrace]:
        """Polynomial: (Mode, Percept) → (Action, Trace)."""

        # Mode selection based on situation
        self.mode = self._select_mode(percept)

        match self.mode:
            case AgentMode.STRATEGIC:
                action, reasoning = await self._strategic_decision(percept)
            case AgentMode.TACTICAL:
                action, reasoning = await self._tactical_decision(percept)
            case AgentMode.REFLEXIVE:
                action, reasoning = self._reflexive_decision(percept)
            case AgentMode.OBSERVING:
                action, reasoning = Action.NONE, "Observing game state"

        # Apply human reaction model
        action = self.reaction_model.humanize(action, percept)

        # Create witness trace
        trace = DecisionTrace(
            mode=self.mode,
            percept_hash=hash(percept),
            reasoning=reasoning,
            action_chosen=str(action),
            alternatives_considered=self._get_alternatives(percept),
            confidence=self._compute_confidence(percept, action),
            reaction_time_ms=self.reaction_model.last_reaction_time,
            human_likeness_score=self.reaction_model.humanness_score(action),
        )

        self.witness.mark(trace)
        return action, trace

    async def _strategic_decision(self, percept: UnifiedPercept) -> tuple[Action, str]:
        """LLM-driven strategic planning."""
        prompt = f"""
        Game State: Wave {percept.wave.number}, Health {percept.player.health}%
        Current Build: {percept.player.upgrades}
        Available Upgrades: {percept.upgrades}

        As a {self.persona.strategic_bias} player, what should I prioritize?
        Consider: risk tolerance {self.persona.risk_tolerance}, current threats.

        Return: (recommended_action, reasoning)
        """

        response = await self.llm.complete(prompt, max_tokens=200)
        return self._parse_strategic_response(response)

    async def _tactical_decision(self, percept: UnifiedPercept) -> tuple[Action, str]:
        """Heuristic + small LLM tactical decisions."""
        # Score all possible tactical actions
        scored_actions = []

        for enemy in percept.enemies:
            threat = self._compute_threat(enemy, percept.player)
            value = self._compute_target_value(enemy)
            scored_actions.append((Action.ATTACK(enemy), threat * value))

        # Add defensive options
        if percept.player.health < 50:
            scored_actions.append((Action.RETREAT, self.persona.risk_tolerance * 100))

        # Bias by persona
        for action, score in scored_actions:
            if self.persona.strategic_bias == "maximize_dps" and action.is_attack:
                score *= 1.5
            elif self.persona.strategic_bias == "maximize_survival" and action.is_defensive:
                score *= 1.5

        best_action = max(scored_actions, key=lambda x: x[1])[0]
        return best_action, f"Tactical: {best_action} scored highest"

    def _reflexive_decision(self, percept: UnifiedPercept) -> tuple[Action, str]:
        """Pure function reflexes - no LLM needed."""
        # Check for immediate threats requiring instant response
        for proj in percept.projectiles:
            if proj.time_to_impact < 500:  # 500ms
                dodge_dir = self._compute_dodge_direction(proj, percept.player)
                return Action.MOVE(dodge_dir), "Reflexive dodge"

        # Check for critical audio cues
        for cue in percept.audio_cues:
            if cue.type == "telegraph_warning":
                return Action.ALERT, "Audio cue: incoming attack"

        return Action.NONE, "No reflex triggered"
```

### 3.3 Human Reaction Model

```python
class HumanReactionModel:
    """
    Transforms ideal AI actions into human-like actions.

    Categorical interpretation: A natural transformation
    IdealAction → HumanizedAction
    """

    def __init__(self, skill_level: float):
        self.skill = skill_level  # 0.0 = novice, 1.0 = pro
        self.base_reaction_ms = 250 - (skill_level * 100)  # 250ms novice, 150ms pro
        self.variance = 50 * (1 - skill_level * 0.5)  # Less variance for pros
        self.stress = 0.0
        self.fatigue = 0.0
        self.last_reaction_time = 0.0

    def humanize(self, action: Action, percept: UnifiedPercept) -> Action:
        """Apply human-like imperfections to ideal action."""
        # Update stress based on situation
        self.stress = self._compute_stress(percept)

        # Sample reaction time
        base = random.gauss(self.base_reaction_ms, self.variance)
        stress_factor = 1 + self.stress * 0.3
        fatigue_factor = 1 + self.fatigue * 0.2
        self.last_reaction_time = base * stress_factor * fatigue_factor

        # Apply precision noise
        if action.requires_aim:
            noise = random.gauss(0, self._aim_noise())
            action = action.with_noise(noise)

        # Attention filtering - might miss things under stress
        if self.stress > 0.7 and random.random() < 0.1:
            action = Action.NONE  # Tunnel vision - missed the cue

        return action

    def _compute_stress(self, percept: UnifiedPercept) -> float:
        """Stress increases with threats, low health, high wave."""
        threat_stress = len([e for e in percept.enemies if e.distance < 200]) * 0.1
        health_stress = (100 - percept.player.health) * 0.01
        wave_stress = percept.wave.number * 0.02
        return min(1.0, threat_stress + health_stress + wave_stress)

    def _aim_noise(self) -> float:
        """Aim gets worse under stress and fatigue."""
        base_noise = 20 * (1 - self.skill)  # 0-20 pixels
        return base_noise * (1 + self.stress * 0.5) * (1 + self.fatigue * 0.3)

    def humanness_score(self, action: Action) -> float:
        """How human-like was this action?"""
        # Check if reaction time is in human range
        if self.last_reaction_time < 100:
            return 0.3  # Too fast - inhuman
        if self.last_reaction_time > 1000:
            return 0.5  # Too slow - inattentive

        # Ideal human range: 150-400ms
        if 150 <= self.last_reaction_time <= 400:
            return 1.0

        return 0.7
```

### 3.4 Evidence Generator

```python
class ASHCEvidenceGenerator:
    """
    Transforms playthrough into ASHC-compatible evidence.

    Categorical: Playthrough → Evidence (functor)
    """

    async def generate(self, playthrough: Playthrough) -> ASHCEvidence:
        """Generate ASHC evidence from a playthrough."""

        # Compute Galois loss for human-likeness
        galois_loss = await self._compute_humanness_galois_loss(playthrough)

        # Extract emergence events
        emergence = self._detect_emergence(playthrough)

        # Compute balance observations
        balance = self._analyze_balance(playthrough)

        # Check fun floor
        fun_floor = self._check_fun_floor(playthrough)

        # Flow state analysis
        flow = self._analyze_flow_state(playthrough)

        return ASHCEvidence(
            playthrough_id=playthrough.id,
            persona=playthrough.agent.persona.name,
            duration_ms=playthrough.duration_ms,
            waves_survived=playthrough.final_wave,
            galois_loss=galois_loss,
            emergence_events=emergence,
            balance_observations=balance,
            fun_floor_violations=fun_floor,
            flow_timeline=flow,
            decision_traces=playthrough.all_traces,
            spec_alignment=self._compute_spec_alignment(playthrough),
        )

    async def _compute_humanness_galois_loss(self, playthrough: Playthrough) -> float:
        """
        L(playthrough) = d(playthrough, C(R(playthrough)))

        Where:
        - R = Extract decision patterns
        - C = Rebuild using human behavior model
        - d = Behavioral distance
        """
        # Extract decision patterns
        patterns = self._extract_patterns(playthrough)

        # Canonicalize through human model
        canonical = self._canonicalize_human(patterns)

        # Compute behavioral distance
        distance = self._behavioral_distance(playthrough, canonical)

        return distance

    def _detect_emergence(self, playthrough: Playthrough) -> list[EmergenceEvent]:
        """Detect emergent gameplay patterns."""
        events = []

        # Check for novel upgrade combinations
        upgrades = playthrough.final_upgrades
        for combo in self._get_upgrade_combos(upgrades):
            synergy = self._compute_synergy(combo, playthrough)
            if synergy > 1.5:  # Synergistic combination
                events.append(EmergenceEvent(
                    type="upgrade_synergy",
                    components=combo,
                    strength=synergy,
                    evidence=f"Combo {combo} achieved {synergy}x effectiveness"
                ))

        # Check for emergent strategies
        strategy_patterns = self._extract_strategy_patterns(playthrough)
        for pattern in strategy_patterns:
            if pattern.novelty > 0.7:
                events.append(EmergenceEvent(
                    type="novel_strategy",
                    components=[pattern.description],
                    strength=pattern.effectiveness,
                    evidence=pattern.trace,
                ))

        return events
```

---

## 4. Integration Points

### 4.1 With ASHC Bootstrap

```python
async def run_playthrough_evidence_bootstrap(
    n_playthroughs: int = 10,
    personas: list[str] = None,
) -> ASHCEvidence:
    """
    Run playthrough farm and aggregate evidence.

    This replaces/augments the static qualia tests with dynamic
    AI-driven playthroughs that generate richer evidence.
    """
    personas = personas or list(AGENT_PERSONAS.keys())

    # Create agent farm
    agents = [
        PlaythroughAgent(AGENT_PERSONAS[p], llm_client)
        for p in personas
    ]

    # Run playthroughs in parallel
    playthroughs = await asyncio.gather(*[
        run_single_playthrough(agent, max_waves=10)
        for agent in agents
    ])

    # Generate evidence
    evidence_generator = ASHCEvidenceGenerator()
    all_evidence = [
        await evidence_generator.generate(p)
        for p in playthroughs
    ]

    # Aggregate
    return aggregate_evidence(all_evidence)
```

### 4.2 With Existing Qualia Tests

The AI playthrough system complements (doesn't replace) qualia tests:

```
QUALIA TESTS (Static)           PLAYTHROUGH AGENTS (Dynamic)
────────────────────            ─────────────────────────────
State machine validation        State machine exploration
Telegraph timing verification   Telegraph response testing
Emergence detection             Emergence generation
Fun floor checking              Fun floor stress testing
```

### 4.3 With Galois Loss Framework

```python
# The playthrough Galois loss composes with spec Galois loss
total_loss = α * spec_impl_loss + β * playthrough_humanness_loss

# Where α + β = 1, typically α = 0.6, β = 0.4
# This gives us: "Does impl match spec?" + "Does gameplay feel human?"
```

---

## 5. Implementation Roadmap

### Phase 1: Core Agent (Week 1)
- [ ] `PlaythroughAgent` polynomial functor
- [ ] Basic perception sheaf (debug API only)
- [ ] Reflexive decision layer (pure functions)
- [ ] Human reaction model

### Phase 2: Intelligence Layers (Week 2)
- [ ] Tactical decision layer (heuristics)
- [ ] Strategic decision layer (LLM integration)
- [ ] Persona system
- [ ] Witness accumulator

### Phase 3: Evidence Generation (Week 3)
- [ ] ASHC evidence generator
- [ ] Humanness Galois loss
- [ ] Emergence detection
- [ ] Balance analysis

### Phase 4: Farm & Integration (Week 4)
- [ ] Parallel playthrough farm
- [ ] Integration with ASHC bootstrap
- [ ] CI/CD integration
- [ ] Dashboard for evidence visualization

---

## 6. Expected Outcomes

### 6.1 Evidence Quality

| Metric | Current (Qualia) | Expected (Playthrough) |
|--------|------------------|------------------------|
| Coverage | 8 fixed scenarios | Infinite variations |
| Humanness | N/A | Measured via Galois |
| Emergence | Scripted detection | Organic discovery |
| Balance | Manual tuning | Data-driven insights |

### 6.2 Revelatory Insights

The system should reveal:
1. **Dominant strategies** - What builds always win?
2. **Fun floor violations** - Where does engagement drop?
3. **Emergent combos** - What unexpected synergies exist?
4. **Balance issues** - Which upgrades are never picked?
5. **Human-likeness gaps** - Where does AI play feel inhuman?

---

## 7. Categorical Verification

The system satisfies categorical laws:

```
IDENTITY: Id >> PlayAgent = PlayAgent = PlayAgent >> Id
  ↳ Playing with no persona bias = default agent

ASSOCIATIVITY: (Perceive >> Decide) >> Act = Perceive >> (Decide >> Act)
  ↳ Order of composition doesn't matter

COMPOSITION: PlayAgent_aggressive >> PlayAgent_defensive = PlayAgent_balanced
  ↳ Personas can be composed to create new personas

FUNCTOR LAWS:
  - PlayAgent(Id) = Id
  - PlayAgent(f >> g) = PlayAgent(f) >> PlayAgent(g)
```

---

*"The playthrough IS the proof. The witness IS the evidence. The agent IS the test."*

---

**Filed**: 2026-01-10
**Author**: Claude + Kent (dialectical synthesis)
**Status**: Ready for implementation
