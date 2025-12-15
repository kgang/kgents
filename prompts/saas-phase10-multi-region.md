```markdown
concept.forest.manifest[phase=PLAN][sprint=saas_phase10_multi_region]@span=saas_multi_region

/hydrate

handles:
  - phase9: impl/claude/plans/_epilogues/2025-12-14-saas-phase9-production-hardening.md
  - checklist: docs/saas/production-checklist.md
  - runbook: docs/saas/runbook.md
  - chaos-baseline: docs/saas/chaos-baseline.md
  - api-manifests: impl/claude/infra/k8s/manifests/api/
  - nats-manifests: impl/claude/infra/k8s/manifests/nats/
  - observability: impl/claude/infra/k8s/manifests/observability/

ledger: {PLAN:in_progress, RESEARCH:not_started, DEVELOP:not_started, STRATEGIZE:not_started, CROSS-SYNERGIZE:not_started, IMPLEMENT:not_started, QA:not_started, TEST:not_started, EDUCATE:not_started, MEASURE:not_started, REFLECT:not_started}
entropy: 0.10 budget (fresh cycle)

## Context

Phase 9 Production Hardening COMPLETE. Key achievements:
- Soak test script ready (`saas-soak.js`) with memory leak detection
- Blue/green deployment configured (RollingUpdate + PDB)
- NATS backup CronJob running daily (7-day retention)
- Chaos engineering baseline documented with 5 scenarios
- Recovery SLAs defined: API <30s, NATS <60s, Network <90s

Current infrastructure state:
- **API**: `kgents/api:latest` in `kgents-triad` (2 replicas, PDB minAvailable=1)
- **NATS**: 3-node cluster in `kgents-agents` with daily backups
- **Observability**: Prometheus, Grafana, Tempo, Loki, OTEL-Collector
- **Gateway**: Kong with API key auth + rate limiting
- **Reliability**: RollingUpdate, HPA 2-10, circuit breaker, fallback queue

## Phase 10 Scope: Multi-Region Evaluation & DR Strategy

This phase evaluates multi-region deployment options and establishes a disaster recovery strategy. **NOT** full multi-region implementation—that's Phase 11+.

## Your Mission

Evaluate multi-region options, design DR strategy, and create migration path documentation.

### Track A: Multi-Region Evaluation (40%)
1. Research multi-region deployment patterns:
   - Active-Active (full redundancy)
   - Active-Passive (warm standby)
   - Pilot Light (minimal standby)
2. Evaluate NATS multi-cluster options:
   - JetStream super-cluster
   - Cross-region replication
   - Independent clusters with gateway
3. Document trade-offs:
   - Cost implications
   - Latency considerations
   - Complexity vs. benefit
4. Recommendation for kgents SaaS tier

### Track B: DR Strategy Design (35%)
1. Define RPO/RTO targets:
   - API: RTO < 5min, RPO < 1min
   - NATS: RTO < 15min, RPO < 5min (messages)
   - State: RTO < 30min, RPO < 1h (config/secrets)
2. Design failover procedures:
   - DNS-based failover (Route53/CloudFlare)
   - Database/state replication strategy
   - Secret synchronization
3. Create DR runbook section
4. Define DR testing schedule

### Track C: Migration Path Documentation (25%)
1. Document current single-region architecture
2. Design incremental migration steps:
   - Step 1: External backup (S3/GCS)
   - Step 2: Cross-region DNS
   - Step 3: Standby cluster
   - Step 4: Active-Active (if needed)
3. Estimate effort per step
4. Create `docs/saas/multi-region-roadmap.md`

## Exit Criteria

- [ ] Multi-region patterns evaluated with recommendation
- [ ] RPO/RTO targets defined
- [ ] Failover procedure documented
- [ ] DR runbook section added
- [ ] Migration roadmap created
- [ ] Cost estimate for recommended approach

## Non-Goals

- Actual multi-region deployment (Phase 11+)
- Cloud provider selection (defer)
- Full active-active implementation
- Global load balancing implementation
- Database sharding strategy

## Attention Budget

```
Primary (40%): Track A (evaluation)
Secondary (35%): Track B (DR strategy)
Tertiary (25%): Track C (migration path)
```

## Branch Candidates

- **Active-Active chosen**: Spawn `saas-phase11-active-active` track
- **NATS super-cluster complex**: May spawn `nats-super-cluster` research track
- **Cost prohibitive**: May collapse to DR-only strategy
- **Managed service preferred**: Evaluate managed NATS (Synadia Cloud)

## Sequencing

```
Track A (Evaluation) ──────────────────────▶ Recommendation doc
         │
         └──▶ Informs RPO/RTO targets
                    │
Track B (DR Strategy) ─────────────────────▶ DR runbook + failover
         │
Track C (Migration Path) ──────────────────▶ Roadmap doc
```

Track A should complete before finalizing B and C.

## Entropy Budget

| Phase | Allocation | Notes |
|-------|------------|-------|
| PLAN | 0.01 | Scope definition (this prompt) |
| RESEARCH | 0.03 | Multi-region patterns, NATS docs |
| DEVELOP | 0.01 | DR contract definition |
| STRATEGIZE | 0.02 | Migration sequencing |
| IMPLEMENT | 0.02 | Documentation artifacts |
| QA | 0.005 | Doc review |
| Reserve | 0.015 | Unexpected complexity |

## Phase-Specific Guidance

### For RESEARCH
- Review NATS multi-cluster documentation
- Check cloud provider DR patterns (AWS, GCP)
- Review existing chaos baseline for gaps
- Estimate costs for each pattern

### For DEVELOP
- Define DR contracts (RPO/RTO as testable assertions)
- Specify failover trigger conditions
- Document state synchronization requirements

### For IMPLEMENT
- Create documentation artifacts (not infrastructure)
- Update runbook with DR procedures
- Create migration roadmap document

### For QA
- Verify documentation completeness
- Review cost estimates for accuracy
- Validate RPO/RTO targets are achievable

### For REFLECT
- Capture learnings about multi-region complexity
- Note any architectural changes needed
- Identify Phase 11 prerequisites

---

This is the *PLAN* for SaaS Phase 10: Multi-Region Evaluation & DR Strategy.

⟿[RESEARCH]
/hydrate
handles: phase10-plan=this; nats-docs=https://docs.nats.io/running-a-nats-service/nats_admin/jetstream_admin/replication; ledger={PLAN:touched}; entropy=0.03
mission: map multi-region patterns; evaluate NATS super-cluster; gather cost data; identify blockers.
actions: WebSearch(NATS JetStream multi-region); WebSearch(Kubernetes multi-region DR patterns 2025); Read(chaos-baseline); note existing gaps.
exit: pattern comparison table; NATS recommendation; cost estimates; ledger.RESEARCH=touched; continuation → DEVELOP.
```
