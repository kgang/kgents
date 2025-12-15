# CLI Quick Wins Wave 4: STRATEGIZE Phase

> *"Choose the order of moves that maximizes leverage and resilience."*

---

## Context

**Plan**: `plans/devex/cli-quick-wins-wave4.md`
**Phase**: STRATEGIZE
**Prior Phases**: PLAN → RESEARCH → DEVELOP (all touched)
**Artifacts**: Handler contracts in `impl/claude/plans/_epilogues/2025-12-14-cli-quick-wins-wave4-develop.md`

---

## Handles (AGENTESE)

```
concept.forest.manifest[phase=STRATEGIZE][plan=cli-quick-wins-wave4]@span=strategize
void.entropy.sip[amount=0.05]@span=exploration_budget
self.soul.manifest[observer=strategist][focus=sequencing]
```

---

## Phase Ledger

```yaml
phase_ledger:
  PLAN: touched       # 2025-12-14 - Chief audit created plan
  RESEARCH: touched   # 2025-12-14 - Infrastructure mapped
  DEVELOP: touched    # 2025-12-14 - Handler contracts defined
  STRATEGIZE: touching # This session
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
  sip_allowed: true
```

---

## Inputs from DEVELOP

| Artifact | Count | Reference |
|----------|-------|-----------|
| Handler contracts | 9 | `2025-12-14-cli-quick-wins-wave4-develop.md` |
| Logos paths | 9 | `void.*`, `concept.*`, `self.*`, `world.*` |
| Test skeletons | 8 | `handlers/_tests/test_*.py` |
| REPL shortcuts | 8 | `/project`, `/oblique`, etc. |

### Commands to Sequence

| # | Command | Agent | Logos Path | Effort |
|---|---------|-------|------------|--------|
| 1 | `sparkline` | None | `world.viz.sparkline` | 1 |
| 2 | `challenge` | K-gent | `self.soul.challenge` | alias |
| 3 | `oblique` | A-gent | `concept.creativity.oblique` | 1 |
| 4 | `constrain` | A-gent | `concept.creativity.constrain` | 1 |
| 5 | `yes-and` | A-gent | `concept.creativity.expand` | 1 |
| 6 | `surprise-me` | A-gent | `void.serendipity.prompt` | 1 |
| 7 | `why` | K-gent | `self.soul.why` | 1 |
| 8 | `tension` | K-gent | `self.soul.tension` | 1 |
| 9 | `project` | H-jung | `void.shadow.project` | 1 |

---

## Mission

Sequence the 9 commands into sprints that maximize:
1. **Leverage**: Ship impactful commands early to build momentum
2. **Parallelization**: Identify independent tracks
3. **De-risking**: Put uncertain items early to surface blockers
4. **Joy**: Each sprint should produce something delightful

---

## Actions

### 1. Dependency Analysis

Map which commands depend on which infrastructure:

| Command | Dependencies | Notes |
|---------|--------------|-------|
| `sparkline` | None | Pure utility, no agent |
| `challenge` | soul.py exists | Just alias registration |
| `oblique` | Oblique Strategies data | Need to embed deck |
| `constrain` | `CreativityCoach` | Already exists in A-gent |
| `yes-and` | `CreativityCoach` | Already exists in A-gent |
| `surprise-me` | Entropy sip | Need `void.serendipity` holon |
| `why` | K-gent extensions | Need `soul.why` aspect |
| `tension` | K-gent extensions | Need `soul.tension` aspect |
| `project` | H-jung `JungShadow` | Already exists |

### 2. Identify Parallel Tracks

**Track A: Zero-Dependency (Ship Immediately)**
- `sparkline` — Pure function, no agent
- `challenge` — Alias only

**Track B: A-gent Creative (Single Context Registration)**
- `oblique`, `constrain`, `yes-and`
- Shared: Register `concept.creativity` holon in `concept.py` router
- Can run in parallel after holon registered

**Track C: Void Context (New Holons)**
- `surprise-me`, `project`
- Shared: Register `void.serendipity` and `void.shadow` holons
- Can run in parallel after holons registered

**Track D: K-gent Extensions (Soul Aspects)**
- `why`, `tension`
- Shared: Extend soul handler with new aspects
- Sequential (both touch soul.py)

### 3. Sprint Proposal

**Sprint 1: Foundation (1 hour)**
```
[Track A] sparkline + challenge (parallel)
```
- Exit: Two commands shipping, zero risk

**Sprint 2: Creative Commands (1-2 hours)**
```
[Track B] Register concept.creativity holon → oblique → constrain → yes-and
```
- Exit: Creative suite working

**Sprint 3: Void Expansion (1-2 hours)**
```
[Track C] Register void holons → surprise-me → project (parallel)
```
- Exit: Entropy and shadow commands working

**Sprint 4: Soul Deepening (1 hour)**
```
[Track D] why → tension (sequential)
```
- Exit: Full K-gent inquiry suite

### 4. Checkpoints & Gates

| Checkpoint | Gate Condition |
|------------|----------------|
| After Sprint 1 | `kg sparkline 1 2 3` works, `kg challenge` aliases correctly |
| After Sprint 2 | `kg oblique` returns strategy, creativity REPL path works |
| After Sprint 3 | `void.*` paths resolve in REPL |
| After Sprint 4 | Soul handler has 6+ modes (reflect, advise, challenge, explore, why, tension) |

### 5. Abort Criteria

- **Abort Sprint 2** if Oblique Strategies licensing unclear (fallback: generate original prompts)
- **Abort Sprint 3** if entropy sip mechanism not wired (fallback: use random.choice)
- **Abort Sprint 4** if K-gent LLM unavailable (fallback: template-based responses)

---

## Oblique Lookback (Entropy Sip)

`void.entropy.sip[amount=0.02]`

**What if we did it backwards?**
- Start with `project` (hardest) → de-risks H-jung dependency
- Risk: Blocks longer if Jung agent needs fixes

**What's the scariest chunk?**
- `why` (recursive LLM calls) and `surprise-me` (entropy integration)
- Consider: Move `why` to Sprint 2 to surface LLM latency issues early

**Revised order after lookback**: Keep original—low-risk first builds momentum.

---

## Branch Candidates

| Branch | Type | Action |
|--------|------|--------|
| Oblique Strategies data curation | Parallel | Create `data/oblique_strategies.json` |
| REPL shortcut registration | Parallel | Can happen any time |
| Soul handler refactor | Deferred | If aspects exceed 10, consider subcommand router |

---

## Exit Criteria

- [x] Ordered backlog with dependencies
- [x] Parallel tracks identified (4 tracks)
- [x] Checkpoints defined (4 gates)
- [x] Abort criteria named
- [x] Branch candidates classified
- [ ] Sprint assignments (human/agent ownership) — Note: All agent-implementable

---

## Deliverables

1. **Sprint Plan**: 4 sprints, ~4-6 hours total
2. **Parallel Tracks**: A (zero-dep), B (creative), C (void), D (soul)
3. **Checkpoints**: 4 verification gates
4. **Abort Criteria**: 3 fallback conditions

---

## Next Phase Auto-Inducer

After completing STRATEGIZE, emit:

```markdown
⟿[CROSS-SYNERGIZE]

This is the *CROSS-SYNERGIZE* phase for **CLI Quick Wins Wave 4**.

/hydrate
handles: backlog=[sparkline,challenge,oblique,constrain,yes-and,surprise-me,project,why,tension]; parallel=[A,B,C,D]; checkpoints=4; gates=4; interfaces=[concept.creativity,void.shadow,void.serendipity,self.soul]; ledger={STRATEGIZE:touched}; branches=3
mission: Hunt compositions/entanglements; probe with hotdata; select law-abiding pipelines.
actions: Enumerate morphisms between commands; identify REPL pipelines; test composition laws.
exit: Chosen compositions + rationale; rejected paths noted; ledger.CROSS-SYNERGIZE=touched; continuation → IMPLEMENT.

Exit Criteria:
- [ ] Pipeline compositions identified (e.g., `soul.manifest >> tension >> sparkline`)
- [ ] Cross-context bridges documented
- [ ] Synergies with Agent Town / REPL Wave 3 noted
- [ ] Explicit "no synergy" noted for standalone commands
```

---

## Auto-Inducer (LAW)

> *"Every phase generates its successor by the same principles that generated itself."*

The following signifier triggers auto-continuation per `spec/protocols/auto-inducer.md`:

---

⟿[CROSS-SYNERGIZE]

This is the *CROSS-SYNERGIZE* phase for **CLI Quick Wins Wave 4**.

/hydrate
handles: backlog=[sparkline,challenge,oblique,constrain,yes-and,surprise-me,project,why,tension]; parallel=[A,B,C,D]; checkpoints=4; gates=4; interfaces=[concept.creativity,void.shadow,void.serendipity,self.soul]; ledger={PLAN:touched,RESEARCH:touched,DEVELOP:touched,STRATEGIZE:touched}; entropy=0.05; branches=3
mission: Hunt compositions/entanglements; probe with hotdata; select law-abiding pipelines.
actions: Enumerate morphisms between commands; identify REPL pipelines; test composition laws; check Agent Town synergies.
exit: Chosen compositions + rationale; rejected paths noted; ledger.CROSS-SYNERGIZE=touched; continuation → IMPLEMENT.

Exit Criteria:
- [ ] Pipeline compositions identified (e.g., `soul.manifest >> tension >> sparkline`)
- [ ] Cross-context bridges documented
- [ ] Synergies with Agent Town / REPL Wave 3 noted
- [ ] Explicit "no synergy" noted for standalone commands
