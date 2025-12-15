---
path: plans/k-terrarium-llm-agents
status: active
progress: 5
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables: [k-gent-live, terrarium-dashboard, permanent-chatbot]
session_notes: |
  Crown jewel plan: Sophisticated, live LLM-backed agents in k-terrarium.
  Kent says "this is amazing" (HARD REQUIREMENT).
  Full 11-phase ceremony per AD-005.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched  # 2025-12-14 - discovered P1-P6 already complete!
  CROSS-SYNERGIZE: pre-analyzed  # see Pre-CROSS-SYNERGIZE section below
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.07
  spent: 0.03
  returned: 0.04
---

# K-Terrarium LLM Agents: Crown Jewel Plan

> *"Kent says 'this is amazing' to the agent"* — The north star.

**Process**: Full 11-phase ceremony (AD-005) — this is a Crown Jewel.
**Auto-Inducer**: Active (`⟿`/`⟂` signifiers at phase exits)
**Entropy Budget**: 0.07 per phase (Accursed Share 5-10%)

---

## Phase Ledger Initialization

Per `plans/skills/n-phase-cycle/phase-accountability.md`:

| Phase | Minimum Artifact |
|-------|------------------|
| PLAN | Scope + non-goals + exit criteria + attention budget + entropy sip |
| RESEARCH | File map + blockers with file:line refs |
| DEVELOP | Contract/API deltas + law assertions |
| STRATEGIZE | Sequencing with rationale + leverage plan |
| CROSS-SYNERGIZE | Named compositions or explicit skip with check |
| IMPLEMENT | Code changes or commit-ready diff |
| QA | Checklist run (mypy/lint/sec) with result |
| TEST | Tests added/updated or explicit risk declaration |
| EDUCATE | Usage notes + doc links or explicit skip |
| MEASURE | Metric hook/plan or defer with owner/timebox |
| REFLECT | Learnings + next-loop seeds |

---

## North Star & Wow-Tests

**Success Criterion**: Kent interacts with a live K-gent agent in k-terrarium and says "this is amazing."

### Evidence of "Amazing"

| Dimension | Observable | Wow Moment |
|-----------|------------|------------|
| **Responsive** | < 200ms first token | Stream starts before thought completes |
| **Personalized** | Uses Kent's eigenvectors | Feels like talking to best-day self |
| **Compositional** | Agents chain via `>>` | Pipeline of introspect → shadow → synthesize |
| **Observable** | Live metrics in dashboard | Watch tokens flow, see soul state evolve |
| **Ambient** | Not just CLI | WebSocket presence, dashboard cards, API |

### Concrete Wow-Tests

1. **Live Dialogue Stream**: `kg soul dialogue "What am I avoiding?" --stream` shows tokens arriving in real-time
2. **Dashboard Soul Card**: Terrarium dashboard shows K-gent state, eigenvector radar, live token count
3. **Compositional Pipeline**: `kg soul introspect | kg soul challenge` works with streaming
4. **Ambient Presence**: K-gent notices context (time of day, recent git activity) without being asked
5. **HotData Richness**: Demo fixtures are real LLM outputs, not synthetic stubs (AD-004)

---

## Scope & Non-Goals

### In Scope (11 Implementation Phases)

| Phase | Deliverable | Dependency | Track |
|-------|-------------|------------|-------|
| **P1** | Verify existing K-gent LLM dialogue (88 tests pass) | None | A |
| **P2** | FluxStream operators (`.filter()`, `.take()`, `.map()`) | P1 | A |
| **P3** | CLI `--stream` flag verified end-to-end | P2 | A |
| **P4** | WebSocket `/ws/soul/stream` with rate limiting | P3 | B |
| **P5** | Dashboard Soul Card (real-time state) | P4 | B |
| **P6** | Compositional pipelines (`kg soul X | kg soul Y`) | P3 | A |
| **P7** | Ambient context injection (time, git, file) | P4 | B |
| **P8** | HotData fixtures (pre-computed LLM outputs per AD-004) | Any | C |
| **P9** | Integration tests (CLI + WebSocket + operators) | P6, P7 | - |
| **P10** | Polish: error messages, loading states, joy | P9 | - |
| **P11** | Demo session: Kent says "amazing" | All | - |

### Out of Scope (Explicit Non-Goals)

- **Synthetic demos**: No fake data, no stub responses
- **Feature sprawl**: No multi-agent orchestration yet
- **UI framework migration**: Use existing Textual/marimo
- **Infrastructure changes**: K8s, databases stay as-is
- **Permanent chatbot deployment**: Separate plan (`plans/deployment/_strategy/kgent-chatbot-strategy.md`)

---

## Pre-CROSS-SYNERGIZE: In-Flight Work Analysis

Per `plans/skills/n-phase-cycle/cross-synergize.md`, we must discover compositions and entanglements with existing work. This analysis is performed proactively during PLAN.

### Active Trees Relevant to This Work

| Plan | Progress | Synergy Type | Notes |
|------|----------|--------------|-------|
| `agents/k-gent` | 97% | **COMPOSE** | CP7 complete (FluxStream). Leverage existing 589 tests. |
| `self/memory` | 75% | COMPOSE | Ghost Cache enables session persistence. |
| `devex/hotdata-infrastructure` | 0% | **MUST-USE** | AD-004 mandates HotData for fixtures. |
| `meta/forest-agentese` | 35% | COMPOSE | AGENTESE paths for `self.soul.*` already defined. |
| `deployment/permanent-kgent-chatbot` | 0% | DEFERRED | Out of scope; enable but don't implement. |
| `interfaces/visualization-strategy` | 100% | **INHERIT** | Dashboard patterns already designed. |

### Cross-Synergy Opportunities

| Composition | Type | Value | Action |
|-------------|------|-------|--------|
| `KgentSoul.dialogue_flux()` + `FluxStream` | Already done | CP7 merged | Verify, don't rebuild |
| `HotData` + demo fixtures | Must compose | AD-004 compliance | P8 implements this |
| `SoulCard` + `visualization-strategy` primitives | Compose | Consistent UX | Use existing card patterns |
| `soul.py` + `session.py` | Already composed | 58 tests | Leverage session management |
| WebSocket + `terrarium/server.py` | Exists | CP7 added `/ws/soul/stream` | Polish, don't rebuild |

### Dormant Trees to Consider (Accursed Share)

| Tree | Days Dormant | Potential Synergy |
|------|--------------|-------------------|
| `agents/t-gent` | 2 | Flaky testing patterns for streaming |
| `session-11-igent-visualization` | 0 | Visualization ideas for Soul Card |

### Law Checks Required

Per `spec/principles.md` §5 (Composable):

| Law | Verification Target | Status |
|-----|---------------------|--------|
| Identity | `Id >> KgentFlux ≡ KgentFlux ≡ KgentFlux >> Id` | PENDING (P9) |
| Associativity | `(filter >> take) >> map ≡ filter >> (take >> map)` | PENDING (P2) |
| Minimal Output | Single `FluxEvent` per yield, not arrays | EXISTING (CP7) |
| Orthogonality | FluxStream works with/without metadata | PENDING (P2) |

### Rejected Compositions (Document to Avoid Rework)

| Composition | Reason for Rejection |
|-------------|---------------------|
| `KgentFlux` + `PolyAgent` formal state machine | YAGNI per chatbot API spec; existing enum sufficient |
| Custom streaming protocol (not WebSocket) | Tasteful: use standard WebSocket |
| New dashboard framework | Curated: use existing Textual/marimo |

---

## Current State Assessment

### What Exists (97% K-gent plan complete per `_forest.md`)

| Component | Status | Evidence | File:Line |
|-----------|--------|----------|-----------|
| `KgentSoul` class | 88 tests | LLM dialogue, eigenvectors, modes | `agents/k/soul.py:1-150` |
| `KgentFlux` streaming | 39 tests | DORMANT/FLOWING modes | `agents/k/flux.py:1-100` |
| LLM client | Working | OpenRouter integration | `agents/k/llm.py` |
| FluxStream wrapper | CP7 complete | `.filter()`, `.take()`, `.map()` | `agents/k/flux.py:90-200` |
| CLI handler | Basic | `kg soul dialogue` | `protocols/cli/handlers/soul.py` |
| WebSocket endpoint | `/ws/soul/stream` | Rate limiting | `protocols/terrarium/server.py:338-495` |
| Session management | 58 tests | `SoulSession` + cache | `agents/k/session.py` |
| Dashboard | Partial | Reactive pipeline exists | `agents/i/reactive/pipeline/` |

### Gaps Identified (with file:line targets)

| Gap | Blocking What | Target File | Effort |
|-----|---------------|-------------|--------|
| FluxStream `.pipe()` operator | Pipeline composition | `agents/k/flux.py:~200` | Medium |
| Soul Card widget | Dashboard integration | `agents/i/reactive/widgets/soul_card.py` (new) | Medium |
| Ambient context injection | Personalization feel | `agents/k/soul.py:~150` | Low |
| HotData fixtures | Demo richness | `fixtures/soul/*.json` (new) | Low |
| Integration tests | Confidence | `agents/k/_tests/test_integration.py` (new) | Medium |

---

## Implementation Phase Roadmap (11 Phases)

### Phase P1: Verification

**AGENTESE**: `concept.forest.manifest[phase=P1][minimal_output=true]`

**Mission**: Verify existing infrastructure. Run tests, check LLM credentials, confirm streaming works.

**Actions**:
1. `pytest impl/claude/agents/k/` — confirm 88+ tests pass
2. `kg soul status` — verify LLM client initializes
3. `kg soul dialogue "hello" --stream` — observe token streaming
4. `mypy impl/claude/agents/k/` — type check clean

**Exit Criteria**:
- Tests: 88+ passing
- LLM: credentials verified
- Streaming: tokens arrive in terminal
- mypy: 0 errors

**Branch Check**: None expected (verification only)

**Entropy**: 0.02 (minimal exploration)

---

### Phase P2: FluxStream Operators

**AGENTESE**: `void.entropy.sip[phase=P2][entropy=0.07]`

**Mission**: Complete operator chaining on FluxStream.

**Deliverables**:
- `FluxStream.filter(predicate)` — filter events (verify existing)
- `FluxStream.take(n)` — limit stream (verify existing)
- `FluxStream.map(f)` — transform events (verify existing)
- `FluxStream.pipe(other_stream)` — composition (NEW: C20 from CP7 plan)

**Law Assertions**:
```python
# Associativity
assert await (stream.filter(p1).take(5)).collect() == await stream.filter(p1).take(5).collect()

# Identity
assert await Id().pipe(stream).collect() == await stream.collect()
```

**Exit Criteria**:
- `.pipe()` operator implemented
- Associativity test passing
- Identity test passing

**Branch Candidates**:
- [ ] BRANCH: FluxStream error recovery patterns | Impact: LOW | Blocks: no → DEFERRED

**Entropy**: 0.05

---

### Phase P3: CLI Streaming Polish

**AGENTESE**: `void.entropy.sip[phase=P3][entropy=0.05]`

**Mission**: Ensure `--stream` flag works perfectly end-to-end.

**Deliverables**:
- `kg soul dialogue "X" --stream` with clean output
- TTY detection for fallback
- Error handling for interrupts (Ctrl+C graceful)
- Progress indicator while waiting for first token

**Exit Criteria**:
- Streaming feels smooth in terminal
- No stack traces on Ctrl+C
- Non-TTY fallback works

**Branch Candidates**:
- [ ] BRANCH: Rich console output (colors, spinners) | Impact: LOW | Blocks: no → DEFERRED

**Entropy**: 0.03

---

### Phase P4: WebSocket Integration

**AGENTESE**: `void.entropy.sip[phase=P4][entropy=0.07]`

**Mission**: Polish WebSocket endpoint for external clients.

**Deliverables** (verify existing CP7 work):
- `/ws/soul/stream` with clean JSON framing
- Rate limiting verified (10 streams/IP default)
- Mode mapping (lowercase strings → DialogueMode)
- Heartbeat/ping for connection health

**Exit Criteria**:
- Can connect from browser console
- Tokens arrive as JSON frames
- Rate limiting tested

**Branch Candidates**:
- [ ] BRANCH: Authentication for WebSocket | Impact: MED | Blocks: no → DEFERRED (security)

**Entropy**: 0.05

---

### Phase P5: Dashboard Soul Card

**AGENTESE**: `void.entropy.sip[phase=P5][entropy=0.10]`

**Mission**: Add K-gent Soul Card to Terrarium dashboard.

**Deliverables**:
- `SoulCard` widget showing:
  - Current mode (DialogueMode)
  - Eigenvector radar (7 dimensions)
  - Token count (session total)
  - Last interaction timestamp
- Live updates via WebSocket subscription

**Composition**: Uses `interfaces/visualization-strategy` patterns (INHERITED)

**Exit Criteria**:
- Soul Card renders with real data
- Updates live when dialogue occurs
- Matches visualization-strategy aesthetic

**Branch Candidates**:
- [ ] BRANCH: Eigenvector radar visualization library | Impact: MED | Blocks: no → P5 implements simple version

**Entropy**: 0.08 (higher: new widget)

---

### Phase P6: Compositional Pipelines

**AGENTESE**: `void.entropy.sip[phase=P6][entropy=0.07]`

**Mission**: Enable `kg soul X | kg soul Y` chaining.

**Deliverables**:
- `FluxStream.pipe()` operator (from P2)
- CLI supports stdin streaming
- Output format compatible with piping

**Law Assertions**:
```python
# Composition law (C21 from original plan)
result_sequential = await (kg_soul_introspect >> kg_soul_challenge).invoke(input)
result_piped = await kg_soul_challenge.invoke(await kg_soul_introspect.invoke(input))
assert result_sequential == result_piped
```

**Exit Criteria**:
- `kg soul introspect | kg soul challenge` works
- Output is pipe-friendly (clean text or JSON)

**Branch Candidates**:
- [ ] BRANCH: Multi-stage pipeline DSL | Impact: LOW | Blocks: no → DEFERRED

**Entropy**: 0.05

---

### Phase P7: Ambient Context

**AGENTESE**: `void.entropy.sip[phase=P7][entropy=0.05]`

**Mission**: K-gent notices context without being asked.

**Deliverables**:
- Time of day awareness ("Good evening, Kent...")
- Git status awareness (recent commits, branch)
- Optional file context (current working directory)
- Configurable via `~/.config/kgents/ambient.yaml`

**Exit Criteria**:
- Ambient injection feels natural, not creepy
- Can be disabled
- Context is accurate

**Branch Candidates**:
- [ ] BRANCH: Calendar integration | Impact: LOW | Blocks: no → DEFERRED

**Entropy**: 0.03

---

### Phase P8: HotData Fixtures (PARALLEL)

**AGENTESE**: `void.fixture.refresh[phase=P8][entropy=0.07]`

**Mission**: Pre-compute rich demo fixtures per AD-004.

**Deliverables**:
- `fixtures/soul/introspection_deep.json` — Real LLM output
- `fixtures/soul/dialogue_modes.json` — All modes sampled
- `fixtures/soul/eigenvector_snapshot.json` — Radar data
- `kg fixture refresh soul/` — Regeneration command

**Composition**: Uses `devex/hotdata-infrastructure` pattern (MUST-USE)

**Exit Criteria**:
- Demos use real LLM outputs, not stubs
- Fixtures are versioned in repo
- Refresh command works

**Branch Candidates**: None (focused deliverable)

**Entropy**: 0.05

---

### Phase P9: Integration Tests

**AGENTESE**: `time.forest.witness[phase=P9][law_check=true]`

**Mission**: End-to-end confidence.

**Deliverables**:
- CLI streaming integration test
- WebSocket integration test
- Pipeline composition test
- Dashboard rendering test (snapshot)

**Law Verification**:
- Identity law for FluxStream
- Associativity law for operators
- Minimal Output principle for events

**Exit Criteria**:
- Full test suite green
- Integration confidence high
- No flaky tests

**Branch Candidates**:
- [ ] BRANCH: Performance benchmarks | Impact: LOW | Blocks: no → DEFERRED

**Entropy**: 0.05

---

### Phase P10: Polish

**AGENTESE**: `void.entropy.sip[phase=P10][entropy=0.07]`

**Mission**: Joy-inducing finishing touches (Principle §4).

**Deliverables**:
- Loading states (spinner while LLM thinks)
- Error messages (helpful, not stack traces)
- Personality consistency (eigenvector alignment)
- Keyboard shortcuts in TUI
- `--verbose` mode for power users

**Exit Criteria**:
- Feels delightful to use
- Mirror Test passes (feels like best-day Kent)
- No rough edges

**Branch Candidates**:
- [ ] BRANCH: Themes (dark/light mode) | Impact: LOW | Blocks: no → DEFERRED

**Entropy**: 0.07 (joy exploration)

---

### Phase P11: Demo Session

**AGENTESE**: `self.soul.manifest[phase=P11][minimal_output=true]`

**Mission**: Kent says "this is amazing."

**Actions**:
1. Fresh terminal session
2. `kg soul status` — show state
3. `kg soul dialogue "What should I focus on today?" --stream`
4. Open Terrarium dashboard — observe Soul Card
5. `kg soul introspect | kg soul challenge` — compositional
6. Ambient greeting — notice time/context

**Success Criterion**: Genuine "amazing" reaction.

**Exit Signifier**:
- `⟂[DETACH:cycle_complete]` if amazing
- `⟿[PLAN]` if not (new cycle with feedback)

**Entropy**: 0.02

---

## Dependency Graph

```
P1 (Verify)
 │
 ▼
P2 (Operators) ────────────────────────────────────────────────┐
 │                                                             │
 ▼                                                             │
P3 (CLI Streaming) ─────────────────────────────────┬──────────┼──→ P6 (Pipelines)
 │                                                  │          │        │
 ▼                                                  │          │        ▼
P4 (WebSocket) ─────────────────────────────────────┼──────────┼──→ P7 (Ambient)
 │                                                  │          │        │
 ▼                                                  │          │        ▼
P5 (Dashboard) ─────────────────────────────────────┴──────────┴──→ P9 (Integration)
                                                                         │
P8 (HotData) ─────────────────────────────── (parallel) ─────────────────┘
                                                                         │
                                                                         ▼
                                                                    P10 (Polish)
                                                                         │
                                                                         ▼
                                                                    P11 (Demo)
```

**Parallel Tracks**:
- **Track A**: P1 → P2 → P3 → P6 (Core streaming + pipelines)
- **Track B**: P1 → P2 → P3 → P4 → P5 → P7 (WebSocket + Dashboard + Ambient)
- **Track C**: P8 (HotData, anytime before P9)

---

## Quality Gates

| Gate | Requirement | Enforcement | File |
|------|-------------|-------------|------|
| mypy strict | 0 errors | CI blocks on failure | `pyproject.toml` |
| Tests green | 100% pass | CI blocks on failure | `pytest.ini` |
| Terrarium smoke | Dashboard loads | Manual pre-merge | — |
| Joy check | Personality present | Code review checklist | — |
| Composability check | `>>` works | Integration test | `test_integration.py` |
| HotData check | No synthetic stubs | Fixture validation | `fixtures/soul/` |
| Law check | Identity/Associativity | Property tests | `test_laws.py` |

---

## Metrics Hooks (MEASURE placeholders)

| Metric | Source | Purpose | Owner | Timebox |
|--------|--------|---------|-------|---------|
| First token latency | `FluxEvent.metadata.timestamp` | Responsive feel | P4 | Inline |
| Token throughput | FluxEvent count/second | Stream health | P4 | Inline |
| Eigenvector coherence | Soul state snapshot | Personality consistency | P10 | Defer |
| Wow-moment count | Demo session notes | Success tracking | P11 | Inline |
| "Amazing" captured | Human feedback | North star validation | P11 | Inline |

---

## Risk Notes

| Risk | Mitigation | Branch Classification |
|------|------------|----------------------|
| LLM rate limits | Use haiku for tests, opus for demo | `⟂[BLOCKED:rate_limit]` |
| WebSocket flakiness | Retry logic, heartbeat | Monitor in P4 |
| Dashboard complexity | Keep Soul Card minimal | Defer extras |
| Personality drift | Lock eigenvectors | Audit in P10 |
| Streaming interrupts | Graceful Ctrl+C handling | P3 handles |

---

## Branch Classification Summary

| Type | Candidates | Action |
|------|------------|--------|
| **Blocking** | None identified | — |
| **Parallel** | P8 (HotData) | Run alongside P2-P7 |
| **Deferred** | Auth, themes, benchmarks, calendar | Add to `_bounty.md` |
| **Void** | Serendipitous discoveries | Log during phases |

---

## Attention Budget

```
Primary Focus (60%):    P1-P6 (Core streaming + pipelines)
Secondary (25%):        P5, P7 (Dashboard + Ambient)
Maintenance (10%):      P8 (HotData fixtures)
Accursed Share (5%):    Emergent discoveries, joy injection
```

---

## Ledger Snapshot

```yaml
phase_ledger:
  PLAN: touched
  RESEARCH: pending  # next phase
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pre-analyzed  # done above
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

entropy:
  sipped: 0.03 (reading + pre-cross-synergize)
  returned: 0.04
  budget_remaining: 0.04 for this PLAN session

branches_emitted:
  parallel: [P8:hotdata]
  blocking: []
  deferred: [auth, themes, benchmarks, calendar, rich-console, error-recovery, multi-stage-dsl]
  void: []

compositions_chosen:
  - KgentSoul.dialogue_flux() + FluxStream (CP7)
  - HotData + fixtures (AD-004)
  - SoulCard + visualization-strategy primitives
  - soul.py + session.py

compositions_rejected:
  - PolyAgent state machine (YAGNI)
  - Custom streaming protocol (use WebSocket)
  - New dashboard framework (use Textual)
```

---

## Exit Signifier

⟿[RESEARCH]
/hydrate
handles: scope=k-terrarium-llm-agents; phase=RESEARCH; chunks=[P1:verify,P2:operators]; ledger={PLAN:touched}; entropy=0.07; branches=[P8:parallel]
mission: Verify P1 (run tests 88+, check LLM status, observe streaming), then map P2 operator terrain (FluxStream.pipe() gap, law assertion locations).
actions:
  - Bash: `pytest impl/claude/agents/k/ -v --tb=short` — capture count
  - Bash: `kg soul status` — verify LLM
  - Read: `impl/claude/agents/k/flux.py:150-250` — FluxStream operators
  - Grep: `def pipe|def filter|def take|def map` in `agents/k/flux.py`
  - Log: file map + blockers
exit: Test baseline (88+) + operator gap analysis (pipe missing?) + blockers; ledger.RESEARCH=touched; continuation → DEVELOP.
⟂[BLOCKED:llm_credentials] if no API key configured
⟂[BLOCKED:test_failures] if existing tests fail <80%

---

## STRATEGIZE Findings (2025-12-14)

> *"The mountain is smaller than we thought."*

### Phase Status Matrix — Updated

| Phase | Plan Expected | Reality Discovered | Status |
|-------|---------------|-------------------|--------|
| **P1** | 88+ tests | **782 tests passed** | ✅ COMPLETE (10x target) |
| **P2** | `.pipe()` operator | `flux.py:544-591` exists | ✅ COMPLETE |
| **P3** | CLI `--stream` | `soul.py:735-826` exists | ✅ COMPLETE |
| **P4** | WebSocket `/ws/soul/stream` | `server.py:342-498` full impl | ✅ COMPLETE (verify) |
| **P5** | Dashboard Soul Card | `AgentCardWidget` + `SoulAdapter` exist | ⏳ 80% (wire up) |
| **P6** | Compositional pipes | NDJSON mode `soul.py:829-908` | ✅ COMPLETE (verify) |
| **P7** | Ambient context | Some infrastructure | ⏳ 20% (minimal: time-of-day) |
| **P8** | HotData fixtures | `shared/hotdata/` infrastructure | ⏳ 30% (generate soul fixtures) |
| **P9** | Integration tests | Many exist | ⏳ Pending |
| **P10** | Polish | — | ⏳ Pending |
| **P11** | Demo | — | ⏳ Pending |

### Critical Path to "Amazing" (P11)

```
P4 verify ──┬──> P5 wire-up ──> P9 ──> P10 ──> P11 DEMO
            │
P6 verify ──┘

P7 minimal ──> (parallel, nice-to-have for demo)
P8 fixtures ──> (parallel, enriches demo)
```

**Shortest path**: Verify P4/P6 → Wire P5 → Polish P10 → Demo P11

### Parallelization Opportunities

| Track | Phases | Notes |
|-------|--------|-------|
| **Main** | P4 verify → P5 → P9 → P10 → P11 | Critical path |
| **Ambient** | P7 minimal | Time-of-day greeting only |
| **Fixtures** | P8 | Generate real LLM outputs |

### Leverage Points Discovered

1. **`AgentCardWidget`** (`agents/i/reactive/primitives/agent_card.py`)
   - Full implementation: glyph, sparkline, bar, entropy, breathing
   - Projects to CLI, TUI, MARIMO, JSON
   - No new widget needed — compose this!

2. **`SoulAdapter`** (`agents/i/reactive/wiring/adapters.py:125`)
   - Already maps `SoulState → AgentCardState`
   - DialogueMode → Phase glyph
   - Activity history tracking built-in

3. **`DashboardScreen`** (`agents/i/reactive/screens/dashboard.py`)
   - Composes AgentCards, YieldCards, DensityField
   - CLI, TUI, MARIMO projections ready
   - Just add a K-gent agent card!

4. **NDJSON Pipe Mode** (`soul.py:829-908`)
   - Auto-detects TTY vs pipe
   - Clean JSON-lines: `{"type": "chunk", "index": N, "data": "..."}`
   - Works with `jq`, other tools

### Risk Assessment

| Risk | Mitigation | Likelihood |
|------|------------|------------|
| WebSocket not actually working | Run integration test | Low |
| Pipe composition breaks on real input | Test with `kg soul introspect \| kg soul challenge` | Low |
| Missing eigenvector radar in P5 | Use sparkline as proxy (activity history) | Low |
| Demo feels "flat" | P7 ambient + P10 polish | Medium |

### Updated Dependency Graph

```
             ┌──────────────────────────────────────────────────┐
             │              P1-P3 COMPLETE                      │
             │  (782 tests, pipe/stream operators, CLI ready)   │
             └──────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                              ▼
            ┌───────────────┐              ┌───────────────┐
            │ P4: WebSocket │              │ P6: Pipes     │
            │   (verify)    │              │   (verify)    │
            └───────┬───────┘              └───────┬───────┘
                    │                              │
                    └──────────────┬───────────────┘
                                   ▼
                    ┌───────────────────────────────┐
                    │ P5: Dashboard Soul Card       │
                    │   (wire SoulAdapter →         │
                    │    DashboardScreen)           │
                    └───────────────┬───────────────┘
                                    │
    ┌───────────────┐               │         ┌───────────────┐
    │ P7: Ambient   │◄──────────────┼────────►│ P8: HotData   │
    │  (parallel)   │               │         │  (parallel)   │
    └───────────────┘               │         └───────────────┘
                                    ▼
                    ┌───────────────────────────────┐
                    │ P9: Integration Tests         │
                    └───────────────┬───────────────┘
                                    ▼
                    ┌───────────────────────────────┐
                    │ P10: Polish                   │
                    │   (UX, demo script, joy)      │
                    └───────────────┬───────────────┘
                                    ▼
                    ┌───────────────────────────────┐
                    │ P11: DEMO                     │
                    │   "Kent says 'amazing'"       │
                    └───────────────────────────────┘
```

### Sequencing Rationale

1. **P4/P6 Verification First** (0.02 entropy)
   - Cheap to verify, expensive if broken
   - Run: `curl ws://localhost:8080/ws/soul/stream` test
   - Run: `echo "test" | kg soul --pipe reflect | head -5`

2. **P5 Wire-Up** (0.05 entropy)
   - Create `SoulCard` by composing existing primitives
   - `SoulAdapter.adapt()` already works
   - Add to Terrarium dashboard's agent list

3. **P7/P8 Parallel** (0.05 entropy combined)
   - P7: Just add time-of-day greeting (`"Good evening, Kent..."`)
   - P8: Run `kg fixture refresh soul/` to generate real outputs

4. **P10 Polish** (0.03 entropy)
   - Demo script
   - UX tweaks (colors, timing, "joy injection")
   - Ensure eigenvectors feel alive

5. **P11 Demo** (0.02 entropy)
   - The moment of truth
   - Kent says "amazing" or we iterate

### Branch Classification — Updated

| Type | Candidates | Status |
|------|------------|--------|
| **Verified Complete** | P1, P2, P3 | Done |
| **Verify & Proceed** | P4, P6 | Quick tests |
| **Wire Up** | P5 | Compose existing |
| **Parallel** | P7, P8 | Run alongside |
| **Sequential** | P9 → P10 → P11 | After P5 |

### Exit Criteria Checklist

- [x] Sequencing document with rationale
- [x] P4 code review confirms implementation
- [x] P6 code review confirms implementation
- [x] P5 effort estimate: LOW (compose, don't create)
- [x] Updated dependency graph
- [x] Branch classification finalized

---

## Exit Signifier — STRATEGIZE

⟿[IMPLEMENT]
/hydrate
see plans/k-terrarium-llm-agents.md

handles: scope=k-terrarium-llm-agents; phase=IMPLEMENT; ledger={PLAN:✓,RESEARCH:✓,DEVELOP:✓,STRATEGIZE:✓}; entropy=0.17
mission: Execute P4 verify → P5 wire-up → P7 minimal → P8 fixtures → P10 polish → P11 demo.
actions:
  - Bash: test WebSocket `/ws/soul/stream` with curl/websocat
  - Bash: test `echo "x" | kg soul --pipe reflect | head -5`
  - Edit: Wire `SoulAdapter` into Terrarium dashboard
  - Create: Time-of-day greeting in soul prompt
  - Bash: `kg fixture refresh soul/`
  - Write: Demo script for P11
exit: Working demo where Kent says "amazing"; ledger.IMPLEMENT=touched; continuation → QA.
⟂[BLOCKED:ws_failure] if WebSocket doesn't stream
⟂[BLOCKED:pipe_failure] if shell pipes don't compose
⟂[BLOCKED:llm_rate_limit] if API throttling

---

*"The soul exists. The wires are connected. Now make it amazing."*

*void.gratitude.tithe. The plan is seeded.*
