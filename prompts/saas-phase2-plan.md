# kgents SaaS Phase 2: Infrastructure Track

**Date**: 2025-12-14
**Cycle**: SaaS Foundation
**Phase**: PLAN (New Cycle)
**Previous**: Phase 1 COMPLETE (⟂[PHASE_1_COMPLETE])

---

## Ledger

```yaml
phase_ledger:
  PLAN: in_progress
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

entropy:
  budget: 0.10
  spent: 0.00
  remaining: 0.10
```

---

## Context from Phase 1

### Artifacts Delivered

| Artifact | Location | Status |
|----------|----------|--------|
| AGENTESE REST API | `impl/claude/protocols/api/agentese.py` | 379 LOC |
| K-gent Sessions API | `impl/claude/protocols/api/sessions.py` | 628 LOC |
| Tenant Auth Middleware | `impl/claude/protocols/api/auth.py` | 338 LOC |
| API Quickstart | `docs/api-quickstart.md` | Complete |
| Test Suite | `impl/claude/protocols/api/_tests/` | 215 tests |

### Key Learnings (from REFLECT)

1. **Synergy wins**: Tenancy module provided 60% of auth infrastructure
2. **Simulated streaming is fragile**: SSE uses mock chunks, needs real KgentFlux
3. **datetime.utcnow() debt**: 400 deprecation warnings accumulating
4. **In-memory metering is transient**: Usage data lost on restart

### Deferred Items (Now Unblocked)

| Item | Dependency | Priority |
|------|------------|----------|
| NATS JetStream | None | High |
| OpenMeter Integration | NATS | High |
| Real SSE Streaming | KgentFlux | Medium |
| Dashboard UI | Marimo | Medium |

---

## Continuation Prompt

```
⟿[PLAN]

concept.forest.manifest[phase=PLAN][sprint=phase2_infra]@span=saas_impl

/hydrate

handles:
  - api_code: impl/claude/protocols/api/
  - tenancy_code: impl/claude/protocols/tenancy/
  - docs: docs/api-quickstart.md
  - epilogues: impl/claude/plans/_epilogues/2025-12-14-saas-phase1-complete.md

ledger: {PLAN:in_progress}
entropy: 0.10 budget

## Your Mission

Frame intent for SaaS Phase 2: Infrastructure Track. This phase wires real event streaming and billing-grade metering to the foundation built in Phase 1.

### Scope

**In Scope**:
1. NATS JetStream deployment configuration
2. OpenMeter integration for usage metering
3. Real SSE streaming from KgentFlux to sessions endpoint
4. datetime.utcnow() → datetime.now(datetime.UTC) migration

**Out of Scope** (Phase 3):
- Dashboard UI (Marimo)
- Playground UI
- Multi-region deployment
- Custom domain routing

### Questions to Answer

1. **NATS topology**: Single server vs cluster? JetStream streams vs subjects?
2. **OpenMeter schema**: How do usage events map to billing metrics?
3. **SSE backpressure**: How does KgentFlux handle slow consumers?
4. **Migration strategy**: Big-bang datetime fix or incremental?

### Attention Budget

| Track | Allocation | Rationale |
|-------|------------|-----------|
| NATS JetStream | 40% | Critical path for real streaming |
| OpenMeter | 30% | Enables billing |
| SSE Wiring | 20% | User-facing improvement |
| datetime cleanup | 10% | Tech debt reduction |

### Exit Criteria

- [ ] NATS deployment strategy documented
- [ ] OpenMeter event schema designed
- [ ] SSE wiring approach selected
- [ ] datetime migration scope defined
- [ ] Entropy sip (0.05-0.10) for exploration

## Principles Alignment

This phase emphasizes:
- **Ethical** (spec/principles.md §3): Billing accuracy, no overcharging
- **Joy-Inducing** (spec/principles.md §5): Real streaming feels alive
- **Composable** (spec/principles.md §6): NATS as universal message bus

## Continuation Imperative

Upon completing PLAN, generate the prompt for RESEARCH that:
1. Maps NATS JetStream documentation
2. Surveys OpenMeter API and SDKs
3. Traces KgentFlux → SSE path
4. Counts datetime.utcnow() occurrences

---

continuation → RESEARCH
```

---

## Phase 2 Track Breakdown

### Track A: NATS JetStream (40%)

**Goal**: Real event streaming for SSE and inter-agent communication.

**Research Questions**:
- JetStream consumer modes (push vs pull)
- Message persistence and replay
- Consumer group semantics
- Integration with FastAPI/Starlette SSE

**Key Files**:
- `impl/claude/protocols/api/sessions.py` (SSE endpoint)
- `impl/claude/flux/` (FluxAgent infrastructure)
- `infra/k8s/` (deployment manifests)

### Track B: OpenMeter (30%)

**Goal**: Billing-grade usage metering with event aggregation.

**Research Questions**:
- OpenMeter event schema format
- Aggregation windows (hourly, daily, monthly)
- API rate limits and batching
- Dashboard and alerting

**Key Files**:
- `impl/claude/protocols/api/metering.py` (current in-memory)
- `impl/claude/protocols/tenancy/service.py` (record_usage)

### Track C: SSE Wiring (20%)

**Goal**: Replace simulated chunks with real KgentFlux streaming.

**Research Questions**:
- KgentFlux.stream() API
- Token counting mid-stream
- Error propagation through SSE
- Connection lifecycle management

**Key Files**:
- `impl/claude/protocols/api/sessions.py:372` (send_message endpoint)
- `impl/claude/flux/kgent_flux.py` (KgentFlux)

### Track D: datetime Cleanup (10%)

**Goal**: Eliminate 400 deprecation warnings.

**Research Questions**:
- Scope of datetime.utcnow() usage
- Migration to timezone-aware datetimes
- Test fixture updates required

**Key Files**:
- `impl/claude/protocols/tenancy/*.py`
- `impl/claude/protocols/api/*.py`

---

## Branch Candidates

| Branch | Classification | Notes |
|--------|----------------|-------|
| Dashboard UI | Deferred | Phase 3 after metering works |
| Multi-region | Deferred | Phase 4+ |
| Rate limiting | Parallel | Can implement alongside OpenMeter |
| Webhook callbacks | Parallel | Billing event notifications |

---

## Continuation Prompt for Next Session

After completing this PLAN phase, the next session should use:

```markdown
⟿[RESEARCH]

# kgents SaaS Phase 2: RESEARCH

**Date**: 2025-12-XX
**Cycle**: SaaS Foundation (Phase 2)
**Phase**: RESEARCH
**Previous**: PLAN (Complete)

---

## ATTACH

/hydrate

handles:
  - plan: prompts/saas-phase2-plan.md
  - api_code: impl/claude/protocols/api/
  - flux_code: impl/claude/flux/
  - infra: infra/k8s/

ledger: {PLAN:touched, RESEARCH:in_progress}
entropy: 0.08 remaining (0.02 spent on PLAN)

## Your Mission

Map the terrain for Phase 2 implementation. Surface blockers and synergies.

### Actions

1. **NATS JetStream Research**
   - Read NATS JetStream documentation (WebFetch)
   - Survey existing kgents flux infrastructure
   - Document consumer patterns for SSE

2. **OpenMeter Research**
   - Review OpenMeter API documentation
   - Design event schema for kgents usage
   - Plan batching strategy

3. **SSE Path Trace**
   - Trace `send_message` → KgentFlux → response flow
   - Identify integration points
   - Document backpressure handling

4. **datetime Audit**
   ```bash
   grep -r "datetime.utcnow()" impl/claude/protocols/ | wc -l
   ```

### Exit Criteria

- [ ] NATS integration strategy documented
- [ ] OpenMeter event schema drafted
- [ ] SSE wiring path traced
- [ ] datetime.utcnow() occurrences counted
- [ ] Blockers surfaced with owners

## Continuation Imperative

Upon completing RESEARCH, generate the prompt for DEVELOP that:
1. Designs NATS consumer interface
2. Defines OpenMeter event types
3. Specifies SSE streaming contract
4. Plans datetime migration

---

continuation → DEVELOP
```

---

**Document Status**: Ready for PLAN execution
**Entry Point**: `⟿[PLAN]` with handles above
**Expected Output**: Scoped plan with tracks, attention budget, exit criteria
