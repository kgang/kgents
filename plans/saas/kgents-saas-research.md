---
path: saas/kgents-saas-research
status: pending
progress: 0
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables: [monetization/grand-initiative-monetization, deployment/permanent-kgent-chatbot]
session_notes: |
  GRAND INITIATIVE: kgents SaaS Transformation Research
  Full 11-phase N-Phase Cycle for comprehensive SaaS exploration.
  Builds on existing billing/licensing/API infrastructure.
  Spec: spec/saas/kgents-saas-proposal.md
phase_ledger:
  PLAN: touched
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
  planned: 0.10
  spent: 0.00
  returned: 0.10
---

# kgents SaaS Research Initiative

> *"Surface area for revenue capture."*

**Spec**: `spec/saas/kgents-saas-proposal.md`
**Status**: Awaiting approval to begin RESEARCH phase

---

## Mission

Transform kgents from specification + reference implementation into a viable SaaS business with multiple revenue streams.

---

## Research Questions (Primary)

1. **Product-Market Fit**: Which capabilities have paying demand?
2. **Pricing Model**: Usage-based, subscription, outcome-based, or hybrid?
3. **Distribution**: CLI-first, API-first, or embedded SDK?
4. **Differentiation**: Position against LangChain, AutoGen, CrewAI?
5. **Technical Architecture**: Multi-tenant vs. self-hosted vs. hybrid?
6. **Compliance**: Data residency, SOC2, HIPAA?

---

## Research Tracks (Parallel)

### Track A: Market Research
- Web searches for AI agent pricing 2025
- Market size validation
- Developer tool monetization patterns

### Track B: Technical Architecture
- Multi-tenant API patterns
- Usage metering at scale
- Kubernetes deployment options

### Track C: Competitive Analysis
- LangChain, AutoGen, CrewAI comparison
- Pricing and feature gap analysis
- Differentiation opportunities

### Track D: Community Research
- Developer forums and communities
- OSS monetization case studies
- Indie hacker success patterns

---

## Existing Infrastructure

| Component | Status | Location |
|-----------|--------|----------|
| Stripe billing | Complete | `impl/claude/protocols/billing/` |
| License tiers | Complete | `impl/claude/protocols/licensing/` |
| Soul API | Complete | `impl/claude/protocols/api/` |
| Crown Jewels | 45+ designed | `plans/ideas/impl/crown-jewels.md` |

---

## Deliverables

1. `saas/market-research.md`
2. `saas/architecture-options.md`
3. `saas/competitive-landscape.md`
4. `saas/community-insights.md`
5. `saas/mvp-specification.md`
6. `saas/pricing-model.md`
7. `saas/gtm-playbook.md`

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Sources cited | 20+ |
| Research documents | 4+ |
| Hypotheses validated | 3+ |
| Architecture decision | 1 ADR |
| MVP scope defined | Yes |

---

## Continuation Prompt

```markdown
/hydrate
# kgents SaaS Research - RESEARCH Phase

handles: plan=${spec/saas/kgents-saas-proposal.md}; infra=${impl/claude/protocols/billing,licensing,api}
mission: Execute 4-track parallel research for SaaS transformation.
ledger: PLAN=touched, RESEARCH=in_progress

## Actions

1. Spawn Agent 1: Market research (4 web searches)
2. Spawn Agent 2: Architecture research (patterns analysis)
3. Spawn Agent 3: Competitive analysis (4 products)
4. Spawn Agent 4: Community research (forums, GitHub)

## Exit Criteria
- 4 research documents created
- 20+ sources cited
- Primary questions answered
- Next phase: DEVELOP
```

---

*Awaiting approval to proceed.*
