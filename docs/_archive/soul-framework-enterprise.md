# Soul Framework: The Categorical Imperative for AI Governance

> *"The goal is not to make AI that acts like you. The goal is to make AI that helps you become more like the best version of yourself."*

**Status**: Design Treatment
**Audience**: Enterprise architects, AI platform teams, Product managers
**Core Insight**: K-gent is a **Governance Functor**, not a chatbot

---

## Executive Summary

The Soul Framework is a **Principled Personalization Layer** for AI agents. Unlike behavioral personalization (which optimizes for engagement), Soul Framework optimizes for **alignment with stated values and principles**.

In Category Theory terms: K-gent is the **Functor** that maps the Category of **Intent** (specs/principles) to the Category of **Implementation** (code/infrastructure) while preserving structure.

**Key Value Propositions:**

| Capability | Traditional AI | Soul Framework |
|------------|---------------|----------------|
| Consistency | Style guides (ignored) | Eigenvector coordinates embedded in prompts |
| Governance | Manual review (expensive) | Principle-based filtering + auto-resolution |
| Audit Trail | Post-hoc documentation | Real-time decision logging with rationale |
| Learning | Retrain model ($$$) | Lightweight eigenvector evolution |
| Multi-tenant | Complex customization | Hierarchical composition |

---

## Part I: The Four Capabilities

### Capability I: The Semantic Gatekeeper

K-gent intercepts agent actions and invalidates those that violate principles **before they execute**.

```
Agent Action ──▶ [K-gent] ──▶ Valid? ──▶ Execute
                     │
              Query Principles
              Check Alignment
              Calculate Confidence
                     │
                     └──▶ Invalid ──▶ Reject with Rationale
```

**Validation Test: The "Singleton" Rejection**
- Trigger: Agent attempts to create a global singleton (common anti-pattern)
- K-gent: *"Rejected. Singleton violates Heterarchical principle #6. Use dependency injection."*
- Impact: User never reviews "working but ugly" code

**Enterprise Value**: Architectural purity enforced automatically. Review burden reduced.

### Capability II: The Fractal Expander (The Monad)

K-gent treats user input as "seeds" and fractally expands them into full specifications.

**Validation Test: The "Seed" Explosion**
- Trigger: "We need a new agent for semantic search"
- K-gent:
  1. Retrieves agent anatomy template from principles
  2. Checks naming conventions (AGENTESE paths)
  3. Generates: spec, implementation scaffold, test harness
  4. Asks: "Prioritize recall or precision?"

**Enterprise Value**: The "blank page" problem vanishes. Move from "coding" to "correcting."

### Capability III: The Holographic Constitution

Principles are not a dead file—they are the **control plane**. When `principles.md` changes, K-gent detects architectural drift.

**Validation Test: The "Drift" Alarm**
- Trigger: Edit principle "Tasteful" to "Radical" (permit messy experimentation)
- K-gent: *"Architecture Drift: 45 modules strictly typed, violating new 'Radical' principle. Propose refactor?"*

**Enterprise Value**: Documentation becomes live infrastructure. Principle changes propagate.

### Capability IV: The Auteur Interface (Rodizio Sommelier)

K-gent pre-computes decisions, surfacing only novel problems for human attention.

**Validation Test: The "Sommelier" Pre-Computation**
- Trigger: Database schema migration (usually requires human approval)
- K-gent checks history: "14 similar non-destructive migrations approved"
- Auto-resolves with audit trail. No human attention required.

**Enterprise Value**: Human attention preserved for genuinely novel decisions.

---

## Part II: Core Concepts

### 2.1 Eigenvector Coordinates

Personality is a **continuous manifold**, not binary categories. Each axis has low/high poles:

| Axis | Low Pole | High Pole | Example |
|------|----------|-----------|---------|
| Communication | Terse | Elaborate | 0.3 = prefer brevity |
| Risk Tolerance | Conservative | Aggressive | 0.7 = lean into risk |
| Formality | Casual | Formal | 0.5 = context-dependent |
| Detail Level | Summary | Comprehensive | 0.8 = prefer thorough |
| Abstraction | Concrete | Abstract | 0.6 = moderate |
| Autonomy | Guided | Independent | 0.4 = prefers options |

**Key Insight**: "Neutral" is not zero—it's a specific coordinate. Every response implicitly takes a position. Soul Framework makes that position explicit and controllable.

### 2.2 Dialogue Modes

Different contexts require different epistemic stances:

| Mode | Purpose | AI Behavior |
|------|---------|-------------|
| **REFLECT** | Introspection | Mirror back, ask questions, notice patterns |
| **ADVISE** | Guidance | Offer options, ground in principles |
| **CHALLENGE** | Dialectics | Find weaknesses, stress-test, aim for synthesis |
| **EXPLORE** | Discovery | Follow tangents, generate hypotheses |

### 2.3 Budget Tiers

Cost-conscious operation at enterprise scale:

| Tier | Tokens | Use Case | Cost/Call |
|------|--------|----------|-----------|
| **DORMANT** | 0 | Template responses | $0 |
| **WHISPER** | ~100 | Quick acknowledgments | ~$0.0003 |
| **DIALOGUE** | ~4000 | Full conversations | ~$0.012 |
| **DEEP** | ~8000+ | Complex decisions | ~$0.024+ |

**30% of interactions at zero cost** using templates for common patterns.

### 2.4 Principle Library

Structured collection of organizational values:

```yaml
principles:
  - id: "security-first"
    statement: "Security concerns override feature velocity"
    weight: 0.95
    domain: ["engineering", "product"]

  - id: "customer-data-minimal"
    statement: "Collect only essential data"
    weight: 0.90
    domain: ["product", "legal"]
```

---

## Part III: Enterprise Architecture

### 3.1 Hierarchical Eigenvectors

Organizations have layered personality:

```
ORGANIZATION (communication: 0.4, formality: 0.6)
       │
       ├── ENGINEERING (detail: 0.9)
       │         └── Alice (abstraction: 0.9)
       │
       ├── SALES (formality: 0.3)
       │         └── Bob (risk: 0.8)
       │
       └── LEGAL (formality: 0.9)
                 └── Carol (risk: 0.1)
```

**Composition Rules:**
1. Individual overrides team overrides org (for specified axes)
2. Unspecified axes inherit from parent
3. Confidence scores determine override strength

### 3.2 Integration Patterns

#### Pattern A: Semaphore Mediation

```
Agent Decision Point ──▶ Yield Token
                              │
                    ┌─────────┴─────────┐
                    │   SOUL FRAMEWORK   │
                    │                    │
                    │ Query Principles   │
                    │ Calculate Confidence│
                    │                    │
                    │ confidence >= 0.8? │
                    │    ┌───┴───┐       │
                    │    ▼       ▼       │
                    │ AUTO   ANNOTATE    │
                    │ RESOLVE FOR HUMAN  │
                    └────────────────────┘
```

#### Pattern B: Ambient Presence

K-gent runs as persistent Flux stream:
- Monitors agent activities
- Emits low-frequency "stream of consciousness"
- Provides consistent personality across touchpoints
- Visible in dashboards as "organizational tone"

#### Pattern C: Async Refinement (Hypnagogia)

```
Day (Active)                    Night (Hypnagogia)
┌────────────────────┐         ┌────────────────────┐
│ Interactions flow  │         │ Analyze logs       │
│ Log decisions      │────────▶│ Infer patterns     │
│ Note corrections   │         │ Update eigenvectors│
│ Capture feedback   │         │ Prune stale rules  │
└────────────────────┘         └────────────────────┘
```

### 3.3 Deployment Models

| Model | Description | Best For |
|-------|-------------|----------|
| **Embedded** | Soul Layer per agent | Microservices |
| **Centralized** | Soul Service API | Org-wide consistency |
| **Hybrid** | Central + local overrides | Large enterprises |
| **Federated** | Regional instances | Multi-geo compliance |

---

## Part IV: API Reference

### 4.1 Soul State

```typescript
interface SoulState {
  eigenvectors: Record<string, number>;  // 0.0 to 1.0
  active_mode: DialogueMode;
  principles: PrincipleRef[];
  session_id: string;
  tokens_used_session: number;
}
```

### 4.2 Dialogue Request/Response

```typescript
interface DialogueRequest {
  message: string;
  mode?: DialogueMode;
  budget?: BudgetTier;
  context?: Record<string, any>;
  user_id?: string;
  team_id?: string;
  org_id?: string;
}

interface DialogueResponse {
  response: string;
  mode: DialogueMode;
  budget_tier: BudgetTier;
  tokens_used: number;
  referenced_principles: string[];
  confidence: number;
  audit_id: string;
}
```

### 4.3 Intercept Request/Response

```typescript
interface InterceptRequest {
  semaphore_id: string;
  prompt: string;
  context: Record<string, any>;
  urgency: number;  // 0.0 to 1.0
}

interface InterceptResponse {
  handled: boolean;
  recommendation?: "approve" | "reject" | "escalate";
  annotation?: string;
  confidence: number;
  matching_principles: string[];
  audit_trail: string;
}
```

---

## Part V: Success Metrics

### Operational

| Metric | Target |
|--------|--------|
| Response consistency | >90% (same eigenvector → similar tone) |
| Template hit rate | >30% (zero-cost responses) |
| Mediation accuracy | >85% (auto-resolved confirmed correct) |
| Latency overhead | <50ms |

### Business

| Metric | Target |
|--------|--------|
| Decision audit coverage | 100% |
| User satisfaction | >4.0/5.0 |
| Escalation reduction | -40% |
| Onboarding time | -60% |

### The Mirror Test

> When you ask the AI a hard question, the response should feel like **your organization on its best day**, reminding **your organization on its worst day** what it actually believes.

---

## Part VI: Security & Compliance

### Data Handling
- Eigenvector coordinates: non-PII metadata
- Principle libraries: may contain sensitive policy
- Audit logs: encrypted at rest and in transit

### Access Control
```yaml
roles:
  soul_admin: [manage_org_eigenvectors, manage_principles, view_all_audit]
  team_lead: [manage_team_eigenvectors, view_team_audit]
  user: [manage_personal_eigenvectors, view_personal_audit]
```

### Compliance
- **SOC2**: Audit logging, access controls, encryption
- **GDPR**: User data export, right to deletion
- **HIPAA**: BAA available, PHI isolation

---

## Part VII: Competitive Analysis

| Feature | Soul Framework | Fine-Tuning | RAG | Prompt Engineering |
|---------|---------------|-------------|-----|-------------------|
| Setup time | Hours | Weeks | Days | Minutes |
| Customization cost | Low | High | Medium | Low |
| Consistency | High | High | Medium | Low |
| Audit trail | Native | None | Partial | None |
| Multi-tenant | Native | Complex | Complex | Manual |
| Learning loop | Automated | Retrain | Re-index | Manual |
| Latency impact | <50ms | None | 100-500ms | None |

**Positioning**: Soul Framework is the right choice when you need:
- Consistent personality without fine-tuning cost
- Audit trails for compliance
- Multi-tenant personalization
- Continuous learning from feedback

---

## Appendix: Reference Implementation

The kgents reference implementation:

| Component | Location |
|-----------|----------|
| Core Soul | `impl/claude/agents/k/soul.py` |
| Eigenvectors | `impl/claude/agents/k/eigenvectors.py` |
| Templates | `impl/claude/agents/k/templates.py` |
| CLI Handler | `impl/claude/protocols/cli/handlers/soul.py` |
| Tests | `impl/claude/agents/k/_tests/test_soul.py` |

---

## Glossary

| Term | Definition |
|------|------------|
| **Eigenvector** | Personality axis with coordinates (0.0-1.0) |
| **Dialogue Mode** | Epistemic stance (REFLECT/ADVISE/CHALLENGE/EXPLORE) |
| **Budget Tier** | Token allocation (DORMANT/WHISPER/DIALOGUE/DEEP) |
| **Principle Library** | Structured organizational values |
| **Semaphore Mediation** | Intercepting agent decisions for review |
| **Hypnagogia** | Async refinement during off-peak hours |
| **Mirror Test** | Success criteria for personality alignment |
| **Categorical Imperative** | K-gent as Governance Functor |

---

*"Compute over training. Principles over prompts. The soul remembers. The mirror shows."*
