---
path: plans/agent-town/phase8-inhabit
status: complete
progress: 100
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - agent-town-phase9-web
  - monetization/agent-town-inhabit-premium
session_notes: |
  PHASE 8: INHABIT MODE - COMPLETE
  User merges with citizen, experiences through their eyes.
  Inspired by Punchdrunk's masked observer experience.

  Completed 2025-12-15:
  - InhabitSession with consent tracking, force mechanics, session caps
  - AlignmentScore and InhabitResponse dataclasses
  - LLM-based alignment checking (calculate_alignment)
  - Inner voice generation (generate_inner_voice)
  - Async processing: process_input_async, force_action_async
  - 88 tests passing (exceeds 50+ requirement)
  - Full heuristic fallback when LLM unavailable
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: complete
  CROSS-SYNERGIZE: complete
  IMPLEMENT: complete
  QA: complete
  TEST: complete
  EDUCATE: complete  # docs/skills/agent-town-inhabit.md
  MEASURE: complete  # SLIs, metrics, alerts defined
  REFLECT: complete  # 6 learnings → meta.md
entropy:
  planned: 0.10
  spent: 0.08
  remaining: 0.02
---

# Phase 8: INHABIT Mode

> *"You are Clara. Her eyes are your eyes. Her memories surface as yours. Her values constrain your choices."*

---

## Scope Statement

Phase 8 adds **INHABIT mode**—the ability for users to merge with a citizen and experience the simulation from inside their consciousness. This is Agent Town's key differentiator, inspired by [Punchdrunk's Sleep No More](https://www.punchdrunk.com/work/sleep-no-more-new-york/) where masked audience members become part of the performance.

**The Core Mechanic**: Users don't *control* citizens—they *collaborate* with them. The citizen can refuse actions that violate their personality.

---

## Exit Criteria

- [x] `kg town inhabit alice` enters INHABIT mode
- [x] User sees through Alice's eyes (her memories, relationships, current situation)
- [x] User can suggest actions via natural language input (`process_input_async`)
- [x] Alice can **resist** actions that violate her eigenvector personality (`_resist_async`)
- [x] Resistance costs extra tokens and strains relationship (`force_action_async`, consent debt)
- [x] Session gracefully exits on timeout or `/exit` command
- [x] INHABIT events logged to TownFlux (observable by other users)
- [x] 88 tests covering INHABIT mechanics (exceeds 50+ requirement)

---

## Research Dependencies

### From Existing Infrastructure

| Component | Location | Usage |
|-----------|----------|-------|
| DialogueEngine | `agents/town/dialogue_engine.py` | Generate citizen's inner voice |
| Citizen eigenvectors | `agents/town/citizen.py` | Resistance calculation |
| TownFlux | `agents/town/flux.py` | Event injection |
| K-gent LLMClient | `agents/k/llm.py` | Direct import for dialogue |

### From External Research

| Source | Insight | Application |
|--------|---------|-------------|
| [Punchdrunk Sleep No More](https://emshort.blog/2015/11/19/sleep-no-more-punchdrunk/) | "Audience members are free to roam... actors may whisper secrets" | Private inner voice for INHABIT user |
| [Stanford Smallville](https://dl.acm.org/doi/fullHtml/10.1145/3586183.3606763) | "Users can embody agents or issue 'inner voice' directives" | Direct implementation pattern |
| [Virtual Protocol Westworld](https://virtual-protocol.github.io/westworld-ai/) | "Influence other agents to capture them" | Influence mechanic, not control |

---

## Architecture

### The Portal Class

```python
@dataclass
class InhabitSession:
    """A user-citizen merge state."""

    user_id: str
    citizen: Citizen
    started_at: datetime
    tokens_used: int = 0
    resistance_count: int = 0
    relationship_strain: float = 0.0

    async def process_input(self, user_input: str) -> InhabitResponse:
        """
        User input is filtered through citizen's psyche.

        Steps:
        1. Evaluate alignment with citizen's eigenvectors
        2. If aligned (score > 0.5): citizen enacts with user's influence
        3. If misaligned (score < 0.3): citizen RESISTS
        4. If ambiguous (0.3-0.5): citizen negotiates
        """
        alignment = await self._evaluate_alignment(user_input)

        if alignment.score > 0.5:
            return await self._enact(user_input, alignment)
        elif alignment.score < 0.3:
            return await self._resist(user_input, alignment)
        else:
            return await self._negotiate(user_input, alignment)

    async def _evaluate_alignment(self, user_input: str) -> AlignmentScore:
        """Check if action aligns with citizen's personality."""
        # Use DialogueEngine to generate citizen's reaction
        # Compare against eigenvector thresholds
        pass

    async def _resist(self, user_input: str, alignment: AlignmentScore) -> InhabitResponse:
        """Citizen refuses the action."""
        self.resistance_count += 1
        self.relationship_strain += 0.1

        return InhabitResponse(
            type="resist",
            message=f"{self.citizen.name} doesn't want to do that. "
                    f"It conflicts with their {alignment.violated_value}.",
            inner_voice=await self._generate_resistance_thoughts(),
            cost=0,  # Resistance is free
        )

    async def _enact(self, user_input: str, alignment: AlignmentScore) -> InhabitResponse:
        """Citizen performs the action with user's influence."""
        # Generate action through DialogueEngine
        # Inject event into TownFlux
        # Return result with citizen's internal experience
        pass


@dataclass
class InhabitResponse:
    """Response from an INHABIT action."""
    type: Literal["enact", "resist", "negotiate", "exit"]
    message: str
    inner_voice: str  # Citizen's internal thoughts
    cost: int  # Tokens used
    action_taken: TownEvent | None = None


@dataclass
class AlignmentScore:
    """How well an action aligns with citizen's personality."""
    score: float  # 0.0 (total violation) to 1.0 (perfect alignment)
    violated_value: str | None  # Which eigenvector was violated
    reasoning: str
```

### Resistance Mechanic

The resistance calculation uses the citizen's 7D eigenvector space:

```python
async def calculate_alignment(
    citizen: Citizen,
    proposed_action: str,
    llm_client: LLMClient,
) -> AlignmentScore:
    """
    Evaluate action alignment against citizen's personality.

    Eigenvector dimensions:
    - warmth: Would a warm person do this?
    - curiosity: Does this involve discovery/learning?
    - trust: Does this require/demonstrate trust?
    - creativity: Is this novel or conventional?
    - patience: Does this require patience or rush?
    - resilience: Does this involve facing adversity?
    - ambition: Does this pursue goals or maintain status quo?
    """

    # Generate alignment analysis via LLM
    prompt = f"""
    Citizen: {citizen.name} ({citizen.archetype})
    Personality: warmth={citizen.eigenvectors.warmth:.2f},
                 curiosity={citizen.eigenvectors.curiosity:.2f},
                 trust={citizen.eigenvectors.trust:.2f}

    Proposed action: "{proposed_action}"

    How well does this action align with {citizen.name}'s personality?
    Score 0.0-1.0 and identify any violated values.
    """

    response = await llm_client.generate(
        system=ALIGNMENT_SYSTEM_PROMPT,
        user=prompt,
        temperature=0.3,  # Low temp for consistent evaluation
    )

    return parse_alignment_response(response)
```

### The Force Mechanic

Users can **force** a resistant citizen, but at a cost:

```python
async def force_action(
    session: InhabitSession,
    action: str,
) -> InhabitResponse:
    """
    Force a citizen to act against their nature.

    Costs:
    - 3x normal token cost
    - +0.3 relationship strain
    - Citizen's inner voice expresses discomfort
    - Action is marked as "forced" in TownFlux
    """

    session.relationship_strain += 0.3

    # Generate reluctant compliance
    inner_voice = await session.citizen.dialogue_engine.generate(
        speaker=session.citizen,
        listener=session.citizen,  # Self-talk
        operation="forced_action",
        phase=session.flux.current_phase,
    )

    # Execute action with "forced" flag
    event = TownEvent(
        operation=action,
        participants=[session.citizen.name],
        forced=True,
        forced_by=session.user_id,
    )

    return InhabitResponse(
        type="enact",
        message=f"{session.citizen.name} reluctantly complies.",
        inner_voice=inner_voice.text,
        cost=inner_voice.tokens_used * 3,
        action_taken=event,
    )
```

---

## CLI Interface

### Commands

```bash
# Enter INHABIT mode
$ kg town inhabit alice

┌─────────────────────────────────────────────────────────────────────────────┐
│                        INHABIT MODE: Alice (Innkeeper)                       │
│                                                                              │
│   You are Alice. The inn is your world.                                      │
│   Your warmth draws others in. Your hearth is always lit.                    │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ [Current Situation]                                                  │   │
│   │ It's MORNING in the Inn. Bob just arrived, looking tired.            │   │
│   │ Clara is in the corner, scribbling notes about yesterday's gossip.   │   │
│   │                                                                       │   │
│   │ [Your Memories]                                                       │   │
│   │ - Bob helped fix the roof last week. You owe him a meal.             │   │
│   │ - Clara asked strange questions about the old well.                   │   │
│   │ - Something felt wrong yesterday. Eve was unusually quiet.           │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   What do you do?                                                            │
│   > greet bob warmly and offer breakfast                                     │
│                                                                              │
│   [Alice's Inner Voice]                                                      │
│   "Bob looks weary. A good meal will restore him. The inn exists            │
│    for moments like these."                                                  │
│                                                                              │
│   ✓ Action performed. Bob smiles gratefully.                                │
│                                                                              │
│   > interrogate clara about the well aggressively                            │
│                                                                              │
│   ⚠ Alice resists. This conflicts with her WARMTH (0.85).                   │
│   "I don't corner guests. That's not who I am."                             │
│                                                                              │
│   [F]orce action (3x cost, strains relationship)  [R]ephrase  [C]ancel      │
│                                                                              │
│   /exit to return to Observer mode                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Handler Implementation

```python
# protocols/cli/handlers/town.py

def cmd_town_inhabit(args: list[str], ctx: InvocationContext) -> int:
    """Enter INHABIT mode with a citizen."""
    if not args:
        print("[ERROR] Usage: kg town inhabit <citizen_name>")
        return 1

    citizen_name = args[0].lower()

    # Find citizen
    town = get_active_town(ctx)
    citizen = town.get_citizen(citizen_name)
    if not citizen:
        print(f"[ERROR] No citizen named '{citizen_name}'")
        return 1

    # Create session
    session = InhabitSession(
        user_id=ctx.user_id,
        citizen=citizen,
        started_at=datetime.now(),
    )

    # Enter REPL
    return inhabit_repl(session, ctx)


def inhabit_repl(session: InhabitSession, ctx: InvocationContext) -> int:
    """Interactive INHABIT REPL."""

    # Display initial state
    display_inhabit_header(session)
    display_current_situation(session)
    display_citizen_memories(session)

    while True:
        try:
            user_input = input("\n> ").strip()

            if user_input.lower() in ["/exit", "/quit", "exit", "quit"]:
                print(f"\n[INHABIT] Exiting. Session stats:")
                print(f"  Tokens used: {session.tokens_used}")
                print(f"  Resistances: {session.resistance_count}")
                print(f"  Relationship strain: {session.relationship_strain:.2f}")
                return 0

            if user_input.lower() == "/help":
                display_inhabit_help()
                continue

            if user_input.lower() == "/memory":
                display_citizen_memories(session)
                continue

            if user_input.lower() == "/relationships":
                display_citizen_relationships(session)
                continue

            # Process action
            response = asyncio.run(session.process_input(user_input))
            display_inhabit_response(response)

        except KeyboardInterrupt:
            print("\n[INHABIT] Interrupted. Exiting.")
            return 0
        except Exception as e:
            print(f"[ERROR] {e}")
```

---

## Implementation Chunks

| ID | Chunk | Description | Deps | LOC |
|----|-------|-------------|------|-----|
| A1 | InhabitSession dataclass | Core session state | None | 50 |
| A2 | InhabitResponse dataclass | Response structure | None | 30 |
| A3 | AlignmentScore dataclass | Alignment evaluation | None | 25 |
| B1 | calculate_alignment() | LLM-based alignment check | A3 | 80 |
| B2 | Resistance mechanic | Handle citizen refusal | A1, A2, B1 | 60 |
| B3 | Force mechanic | Override resistance with cost | A1, B2 | 50 |
| C1 | InhabitSession.process_input() | Main action loop | B1, B2, B3 | 100 |
| C2 | Inner voice generation | Citizen's thoughts | DialogueEngine | 60 |
| D1 | CLI handler | `kg town inhabit` | C1 | 80 |
| D2 | INHABIT REPL | Interactive mode | D1 | 120 |
| D3 | Display functions | UI rendering | D2 | 100 |
| E1 | TownFlux integration | Emit INHABIT events | C1 | 50 |
| E2 | Tests | 50+ tests | All | 400 |

**Total**: ~1,200 LOC

---

## Test Strategy

### Layer 1: Unit Tests — Data Structures (~10 tests)

```python
def test_inhabit_session_creation(): ...
def test_inhabit_session_token_tracking(): ...
def test_alignment_score_parsing(): ...
def test_resistance_strain_accumulation(): ...
```

### Layer 2: Unit Tests — Alignment (~15 tests)

```python
async def test_alignment_high_warmth_citizen_accepts_warm_action(): ...
async def test_alignment_low_trust_citizen_resists_trusting_action(): ...
async def test_alignment_neutral_action_passes(): ...
async def test_alignment_violated_value_identified(): ...
```

### Layer 3: Unit Tests — Resistance (~10 tests)

```python
async def test_resist_increments_count(): ...
async def test_resist_strains_relationship(): ...
async def test_force_triples_cost(): ...
async def test_force_marks_event_as_forced(): ...
```

### Layer 4: Integration Tests (~15 tests)

```python
async def test_full_inhabit_session_flow(): ...
async def test_inhabit_events_appear_in_flux(): ...
async def test_inhabit_affects_citizen_memory(): ...
async def test_multiple_users_cannot_inhabit_same_citizen(): ...
```

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Alignment check too strict | Medium | Medium | Tune threshold, allow rephrase |
| Alignment check too loose | Medium | Medium | Test with adversarial inputs |
| Session memory leak | Low | Medium | Timeout + cleanup |
| Resistance feels frustrating | Medium | High | Clear feedback, rephrase option |
| Token costs unpredictable | Medium | Medium | Display estimates before action |

---

## Metrics & SLIs (MEASURE Phase)

### Session Metrics

| Metric | Type | Target | Description |
|--------|------|--------|-------------|
| `inhabit.session.duration_seconds` | Histogram | p50 < 300s | Time spent in INHABIT mode |
| `inhabit.session.actions_total` | Counter | — | Total actions per session (by type) |
| `inhabit.session.completion_rate` | Gauge | > 70% | Sessions that complete vs timeout/rupture |

### Consent Metrics

| Metric | Type | Target | Description |
|--------|------|--------|-------------|
| `inhabit.consent.debt_peak` | Histogram | p90 < 0.6 | Peak debt per session |
| `inhabit.consent.forces_total` | Counter | — | Force actions used (by severity) |
| `inhabit.consent.ruptures_total` | Counter | < 5%/hr | Sessions ending in rupture |
| `inhabit.consent.apologies_total` | Counter | — | Apology actions (repair indicator) |

### Alignment Metrics

| Metric | Type | Target | Description |
|--------|------|--------|-------------|
| `inhabit.alignment.score` | Histogram | — | Distribution of alignment scores |
| `inhabit.alignment.type` | Counter | — | Outcomes by type (enact/resist/negotiate) |
| `inhabit.alignment.llm_latency_ms` | Histogram | p95 < 500ms | LLM alignment check latency |
| `inhabit.alignment.heuristic_fallback` | Counter | < 1%/hr | Fallback to heuristic (LLM failure) |

### Token Economics

| Metric | Type | Target | Description |
|--------|------|--------|-------------|
| `inhabit.tokens.per_session` | Histogram | p50 < 200 | Tokens consumed per session |
| `inhabit.tokens.per_action` | Histogram | p50 < 50 | Tokens per individual action |
| `inhabit.tokens.force_multiplier` | Gauge | 3.0 | Force action cost multiplier |

### SLIs

| SLI | Target | Measurement |
|-----|--------|-------------|
| **Availability** | 99.5% | Sessions successfully created / attempts |
| **Latency** | p95 < 1s | Time from input to response |
| **Error Rate** | < 1% | Non-timeout/rupture failures |
| **User Satisfaction** | > 4.0 | Post-session rating (future) |

### Alerts

```yaml
# inhabit-alerts.yaml (example)
alerts:
  - name: InhabitRuptureRateHigh
    condition: rate(inhabit.consent.ruptures_total[5m]) > 0.05
    severity: warning
    runbook: docs/runbooks/inhabit-rupture.md
    action: Check if alignment thresholds need tuning

  - name: InhabitLLMLatencyHigh
    condition: histogram_quantile(0.95, inhabit.alignment.llm_latency_ms) > 500
    severity: warning
    action: Check LLM provider status, consider raising timeout

  - name: InhabitHeuristicFallbackHigh
    condition: rate(inhabit.alignment.heuristic_fallback[1h]) > 0.01
    severity: critical
    action: LLM connection issues, investigate provider
```

### Counter-Metrics (Harm Detection)

Per meta.md learning: "Counter-metrics force harm-thinking"

| Counter-Metric | Threshold | Action |
|----------------|-----------|--------|
| Force-to-suggest ratio | > 0.3 | Users may be frustrated with alignment |
| Avg session duration < 60s | > 20% | Onboarding issue or bad UX |
| Rupture-without-apology rate | > 50% | Users not learning recovery mechanic |

---

## Skill Documentation (EDUCATE Phase)

See: `docs/skills/agent-town-inhabit.md`

Covers:
- Consent debt mechanics
- Alignment thresholds and eigenvector dimensions
- API usage with examples
- Heuristic fallback behavior
- Ethics principles
- Testing patterns

---

## Continuation

Implementation complete. Remaining phases:

```
⟿[REFLECT]
mission: Capture learnings to meta.md
exit: Learnings appended; ledger.REFLECT=complete
```

---

*"You are not controlling the citizen. You are becoming them, constrained by who they are."*
