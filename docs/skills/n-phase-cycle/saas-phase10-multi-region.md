---
path: docs/skills/n-phase-cycle/saas-phase10-multi-region
status: in_progress
progress: 50
last_touched: 2025-12-14
touched_by: opus-4.5
blocking: []
enables:
  - saas/phase11-multi-region-implementation
  - saas/production-dr
session_notes: |
  DEVELOP phase complete. DR contracts defined with testable assertions:
  - API RTO < 5min, NATS RTO < 15min / RPO < 5min
  - Failover triggers (automatic + manual) documented
  - State sync requirements by component
  - Runbook updated with full DR section (failover + failback procedures)
  Artifacts: docs/saas/dr-contracts.md, docs/saas/runbook.md (DR section added)
phase_ledger:
  PLAN: complete
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: not_started
  CROSS-SYNERGIZE: not_started
  IMPLEMENT: not_started
  QA: not_started
  TEST: not_started
  EDUCATE: not_started
  MEASURE: not_started
  REFLECT: not_started
entropy:
  budget: 0.10
  spent: 0.06
  remaining: 0.04
---

# SaaS Phase 10: Multi-Region Evaluation & DR Strategy

> Evaluate multi-region options, design DR strategy, create migration path.

**Difficulty**: Medium
**Prerequisites**: Phase 9 Complete (Production Hardening), Research synthesis
**Files Touched**: `docs/saas/`, `impl/claude/infra/k8s/manifests/`

---

## Executive Summary

Phase 10 is an **evaluation and design phase**—no infrastructure deployment. Outputs are documentation artifacts that inform Phase 11+ implementation.

| Track | Weight | Deliverable | Status |
|-------|--------|-------------|--------|
| A | 40% | Multi-region pattern recommendation | Research complete |
| B | 35% | DR strategy with RPO/RTO contracts | Not started |
| C | 25% | Migration roadmap | Not started |

---

## Research Findings Summary

### Recommended Architecture

| Component | Pattern | Rationale |
|-----------|---------|-----------|
| Kubernetes | Active-Passive | Cost-effective, RTO <15min achievable |
| NATS | Super-Cluster + Mirror | Location transparency, eventual consistency OK |
| DNS | Route53/CloudFlare failover | Health-based routing, 60s TTL |
| Backup | Velero + ArgoCD GitOps | Cluster state + manifests |

### Cost Estimate

| Approach | Monthly | Complexity |
|----------|---------|------------|
| Self-hosted Active-Passive | ~$340 | High |
| Synadia Cloud + Self K8s | ~$448 | Medium |
| Full managed | ~$600+ | Low |

**Decision**: Start with self-hosted (~$340/month), evaluate Synadia if ops burden grows.

See: `docs/saas/multi-region-research.md` for full analysis.

---

## Track A: Multi-Region Evaluation (40%) - COMPLETE

### Artifacts Created

- `docs/saas/multi-region-research.md` - Pattern comparison, NATS options, cost estimates

### Key Decisions

1. **Active-Passive over Active-Active**: Current scale doesn't justify 2x cost
2. **NATS Super-Cluster with Mirroring**: Eventually consistent reads acceptable for AGENTESE
3. **DNS-based failover**: Simpler than service mesh for initial DR

---

## Track B: DR Strategy Design (35%) - COMPLETE

### Goal

Define DR contracts as testable assertions with clear RPO/RTO targets.

### Artifacts Created

- `docs/saas/dr-contracts.md` - Full DR contracts with testable assertions
- `docs/saas/runbook.md` - Updated with DR section (failover + failback)

### Proposed Targets

| Component | RTO Target | RPO Target | Justification |
|-----------|------------|------------|---------------|
| API | < 5 min | N/A (stateless) | DNS TTL + pod startup |
| NATS Streams | < 15 min | < 5 min | Mirror catchup time |
| Secrets/Config | < 30 min | < 1 hour | ESO sync + manual verify |
| Observability | < 1 hour | N/A | Non-critical, can degrade |

### Failover Trigger Conditions

```yaml
# Proposed failover triggers
triggers:
  automatic:
    - condition: "health_check_failures >= 3"
      window: "2 minutes"
      action: "dns_failover"
    - condition: "api_error_rate > 50%"
      window: "5 minutes"
      action: "alert_oncall"

  manual:
    - condition: "region_outage_declared"
      action: "execute_dr_runbook"
    - condition: "data_corruption_detected"
      action: "halt_and_investigate"
```

### State Sync Requirements

| State Type | Sync Method | Frequency | Recovery Priority |
|------------|-------------|-----------|-------------------|
| NATS Streams | Mirror replication | Continuous | P0 |
| K8s Secrets | External Secrets Operator | 5 min poll | P0 |
| K8s Manifests | ArgoCD GitOps | On commit | P1 |
| Grafana Dashboards | Git (as code) | On commit | P2 |
| Prometheus Rules | Git (as code) | On commit | P2 |

### Artifacts to Create

| File | Purpose |
|------|---------|
| `docs/saas/dr-contracts.md` | RPO/RTO as testable assertions |
| `docs/saas/runbook.md` (update) | Add DR procedures section |

---

## Track C: Migration Path Documentation (25%) - STRATEGIZE PHASE

### Goal

Document incremental steps from current single-region to multi-region.

### Proposed Migration Phases

```
Phase 11: External Backup (S3/GCS)
    │
    ▼
Phase 12: Cross-Region DNS Setup
    │
    ▼
Phase 13: Standby Cluster Deployment
    │
    ▼
Phase 14: Active-Active (if needed)
```

### Artifacts to Create

| File | Purpose |
|------|---------|
| `docs/saas/multi-region-roadmap.md` | Step-by-step migration guide |
| `docs/saas/architecture-current.md` | Single-region baseline |

---

## Sequencing

```
Track A (Evaluation) ────────────────▶ COMPLETE
         │
         └──▶ Informs RPO/RTO targets
                    │
                    ▼
Track B (DR Strategy) ───────────────▶ DEVELOP phase
         │                                  │
         │                                  ▼
         │                            DR contracts doc
         │                                  │
         └────────────────────────────────────┘
                    │
                    ▼
Track C (Migration Path) ────────────▶ STRATEGIZE phase
                                           │
                                           ▼
                                     Roadmap doc
```

---

## Non-Goals

- Actual multi-region deployment (Phase 11+)
- Cloud provider selection (defer to cost approval)
- Full active-active implementation
- Database sharding strategy
- Global load balancing implementation

---

## Entropy Budget

| Phase | Allocation | Spent | Notes |
|-------|------------|-------|-------|
| PLAN | 0.01 | 0.01 | Scope definition |
| RESEARCH | 0.03 | 0.03 | Multi-region patterns |
| DEVELOP | 0.02 | 0.00 | DR contracts |
| STRATEGIZE | 0.02 | 0.00 | Migration path |
| IMPLEMENT | 0.01 | 0.00 | Documentation only |
| QA | 0.005 | 0.00 | Doc review |
| Reserve | 0.015 | 0.00 | Unexpected |

---

## Continuation Prompt (DEVELOP)

```markdown
concept.forest.manifest[phase=DEVELOP][sprint=saas_phase10_multi_region]@span=saas_dr_contracts

/hydrate

handles:
  - research: docs/saas/multi-region-research.md
  - runbook: docs/saas/runbook.md
  - chaos-baseline: docs/saas/chaos-baseline.md
  - phase9: impl/claude/plans/_epilogues/2025-12-14-saas-phase9-production-hardening.md

ledger: {PLAN:complete, RESEARCH:touched, DEVELOP:in_progress}
entropy: 0.02 budget

## Your Mission

Define DR contracts as testable assertions. Create documentation artifacts.

### Track B: DR Strategy (Primary Focus)

1. **Define RPO/RTO Contracts** (`docs/saas/dr-contracts.md`):
   - API: RTO < 5min, RPO N/A (stateless)
   - NATS: RTO < 15min, RPO < 5min
   - Secrets: RTO < 30min, RPO < 1h
   - Express as testable assertions (e.g., `assert recovery_time < timedelta(minutes=5)`)

2. **Specify Failover Triggers**:
   - Automatic: health check failures, error rate threshold
   - Manual: region outage, data corruption
   - Document in DR contracts

3. **Document State Sync Requirements**:
   - NATS: Mirror replication (continuous)
   - Secrets: ESO sync (5 min poll)
   - Manifests: ArgoCD GitOps (on commit)

4. **Update Runbook** (`docs/saas/runbook.md`):
   - Add "Disaster Recovery" section
   - Failover procedure (step-by-step)
   - Failback procedure
   - Communication checklist

### Exit Criteria

- [ ] `docs/saas/dr-contracts.md` created with testable RPO/RTO
- [ ] Failover triggers documented
- [ ] State sync requirements specified
- [ ] Runbook DR section added
- [ ] Ledger: DEVELOP=touched

---

This is the *DEVELOP* for SaaS Phase 10: Multi-Region Evaluation.

⟿[STRATEGIZE]
/hydrate
handles: dr-contracts=docs/saas/dr-contracts.md; ledger={DEVELOP:touched}; entropy=0.02
mission: sequence migration phases; identify dependencies; create roadmap.
actions: Write(docs/saas/multi-region-roadmap.md); Write(docs/saas/architecture-current.md); order phases with effort estimates.
exit: migration roadmap complete; ledger.STRATEGIZE=touched; continuation → IMPLEMENT.
```

---

## Exit Signifiers

```markdown
# Normal exit from DEVELOP (auto-continue to STRATEGIZE):
⟿[STRATEGIZE]
/hydrate
handles: dr-contracts=docs/saas/dr-contracts.md; runbook-updated=true; ledger={DEVELOP:touched}; entropy=0.02
mission: sequence migration phases; order by dependency and effort; create roadmap.
actions: Write(docs/saas/multi-region-roadmap.md); Write(docs/saas/architecture-current.md); estimate effort per phase.
exit: roadmap doc created; ledger.STRATEGIZE=touched; continuation → IMPLEMENT.

# Halt conditions:
⟂[BLOCKED:cost_approval] Cost estimate requires stakeholder approval before proceeding
⟂[BLOCKED:infra_dependency] External infrastructure not available
⟂[ENTROPY_DEPLETED] Budget exhausted, need sip from void.entropy
⟂[DETACH:awaiting_human] Architecture decision requires human input
```

---

## Related Skills

- `saas-phase5-operate.md` - Prior operational patterns
- `develop.md` - DEVELOP phase conventions
- `strategize.md` - STRATEGIZE phase conventions
- `../handler-patterns.md` - API patterns

---

## References

- [NATS Multi-Region Consistency](https://www.synadia.com/blog/multi-cluster-consistency-models)
- [NATS Super-Cluster Examples](https://natsbyexample.com/examples/use-cases/cross-region-streams-supercluster/cli)
- [Azure AKS Active-Passive DR](https://learn.microsoft.com/en-us/azure/aks/active-passive-solution)
- [Kubernetes DR Best Practices](https://portworx.com/kubernetes-disaster-recovery/)
- [Synadia Cloud Pricing](https://docs.synadia.com/cloud/pricing)

---

## Changelog

- 2025-12-14: RESEARCH complete, continuation prompt for DEVELOP created
- 2025-12-14: Initial plan created for Phase 10 Multi-Region Evaluation

---

## Auto-Inducer (LAW)

> *"Every cycle MUST reach ⟂ eventually. The form generates its successor."*

```
⟿[DEVELOP]
/hydrate
handles:
  - research: docs/saas/multi-region-research.md
  - runbook: docs/saas/runbook.md
  - skill: docs/skills/n-phase-cycle/saas-phase10-multi-region.md
ledger: {PLAN:complete, RESEARCH:touched, DEVELOP:in_progress}
entropy: 0.02 budget (DEVELOP allocation)

mission: Define DR contracts (RPO/RTO as testable assertions); specify failover triggers; document state sync requirements; update runbook with DR section.

actions:
  1. Write(docs/saas/dr-contracts.md) with:
     - RPO/RTO targets as assertions
     - Failover trigger conditions (automatic + manual)
     - State sync requirements by component
     - Testing/validation approach
  2. Edit(docs/saas/runbook.md) to add:
     - "Disaster Recovery" section
     - Failover procedure (DNS, verify, communicate)
     - Failback procedure
     - Communication checklist
  3. Update ledger: DEVELOP=touched

exit: DR contracts defined with testable assertions; runbook updated; entropy.spent += 0.02; continuation → STRATEGIZE.

branch_candidates:
  - If cost approval needed: ⟂[BLOCKED:cost_approval]
  - If NATS super-cluster complexity surfaces: spawn nats-multi-cluster research track
  - If managed service preferred: evaluate Synadia Cloud track

⟿[STRATEGIZE] on success | ⟂[BLOCKED:*] on failure
```
