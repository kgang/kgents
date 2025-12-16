---
path: plans/core-apps/domain-simulation
status: active
progress: 0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - monetization/enterprise-contracts
  - plans/vertical-expansions
session_notes: |
  Stub plan created from core-apps-synthesis.
  Enterprise-focused simulation platform.
  Agent Town + Tenancy + domain polynomials.
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
  spent: 0.0
  returned: 0.0
---

# Domain Simulation Engine

> *"Agent Town configured for any domain with enterprise requirements."*

**Master Plan**: `plans/core-apps-synthesis.md` (Section 2.5)
**Existing Infrastructure**: `agents/town/`, `protocols/tenancy/`

---

## Overview

| Aspect | Detail |
|--------|--------|
| **Frame** | B2B simulation platform |
| **Core Mechanic** | Domain polynomial + Town + audit logging |
| **Revenue** | $50-150k/yr enterprise contracts |
| **Status** | 75% ready (Town + Tenancy complete) |

---

## What This Plan Covers

### Absorbs These Original Ideas

| Idea | Source | Integration |
|------|--------|-------------|
| Sim-Labs for Risk/Compliance | `money-maximizing-ideas.md` | Crisis vertical |
| Regulated Data Rooms | `money-maximizing-ideas.md` | Audit feature |
| MetroMind | `open-dataset-projects.md` | Urban vertical |
| EconWeb | `open-dataset-projects.md` | Economic vertical |
| MoleculeGarden | `open-dataset-projects.md` | Research vertical |

---

## Architecture Pattern

Every domain simulation follows the same structure:

```python
DOMAIN_SIM = {
    "polynomial": DomainPolynomial,      # State machine for domain entities
    "operad": DOMAIN_OPERAD,             # Composition grammar
    "sheaf": DomainCoherence,            # Local → Global consistency
    "citizens": [DomainCitizen1, ...],   # Domain-specific agents
    "data": [DomainDataset, ...],        # Optional: external data sources
}
```

---

## Vertical Templates

| Vertical | Polynomial Positions | Operad Operations | Example Scenario |
|----------|---------------------|-------------------|------------------|
| **Crisis/Compliance** | NORMAL, INCIDENT, RESPONSE, RECOVERY | escalate, mitigate, communicate, audit | Data breach drill |
| **Urban Planning** | COMMUTING, RESIDING, WORKING, RECREATING | route, transfer, congest, develop | Bike lane impact |
| **Economic Policy** | PRODUCING, CONSUMING, INVESTING, TRADING | buy, sell, borrow, tax | Rate hike simulation |
| **Drug Discovery** | HYPOTHESIZING, DESIGNING, SIMULATING, ANALYZING | propose, test, refute, synthesize | Binding affinity search |

---

## Enterprise Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Audit logging** | SpanEmitter + action_metrics.py |
| **Multi-tenant** | TenantContext + RLS |
| **BAA compliance** | On-prem K8s deployment |
| **Kill switch** | Budget enforcement + kill_switch.py |
| **Consent ledger** | Force mechanic logging |
| **Data residency** | Configurable storage backend |
| **SSO** | SAML/OIDC integration |
| **SLA** | 99.9% uptime guarantee |

---

## Technical Foundation

```python
# Already built
from agents.town import TownEnvironment, TownFlux, TOWN_OPERAD
from agents.poly import PolyAgent
from protocols.tenancy import TenantContext, set_tenant_context
from protocols.api.action_metrics import SpanEmitter
from protocols.terrarium import Terrarium, PrismRestBridge

# To build per vertical
class CrisisPolynomial(PolyAgent):
    positions = frozenset(["NORMAL", "INCIDENT", "RESPONSE", "RECOVERY"])

CRISIS_OPERAD = Operad(
    operations={
        "escalate": Operation(arity=2),
        "mitigate": Operation(arity=1),
        "communicate": Operation(arity=3),
        "audit": Operation(arity=1),
    }
)
```

---

## Implementation Phases

### Phase 1: Crisis Vertical (Q1-Q2 2025)

**Goal**: Complete crisis simulation product

- [ ] Define `CrisisPolynomial` and `CRISIS_OPERAD`
- [ ] Create 6 canonical drills:
  - [ ] Service outage
  - [ ] Data breach
  - [ ] Rogue AI incident
  - [ ] PR crisis
  - [ ] Vendor failure
  - [ ] Insider threat
- [ ] Implement audit logging
- [ ] Build multi-tenant deployment
- [ ] Create web dashboard

**Success Criteria**: First enterprise pilot

### Phase 2: Customization (Q2-Q3 2025)

**Goal**: Customer-configurable simulations

- [ ] Scenario builder UI
- [ ] Custom polynomial definition
- [ ] Data connector framework
- [ ] Integration APIs (Slack, SIEM, etc.)
- [ ] White-label option

**Success Criteria**: Customer builds own scenario

### Phase 3: Additional Verticals (Q3-Q4 2025)

**Goal**: Expand market reach

- [ ] Urban planning templates (MetroMind)
- [ ] Economic simulation templates (EconWeb)
- [ ] Research simulation templates (MoleculeGarden)
- [ ] Vertical-specific UI skins
- [ ] Vertical-specific data connectors

**Success Criteria**: 3 verticals live

### Phase 4: Marketplace (Q4 2025+)

**Goal**: Ecosystem and scale

- [ ] Scenario marketplace
- [ ] Consultant ecosystem
- [ ] Certification program
- [ ] Partner API
- [ ] Reseller agreements

**Success Criteria**: Partner-generated revenue

---

## Revenue Model

```python
ENTERPRISE_TIERS = {
    "starter": {
        "price": 50_000,  # /year
        "drills": 6,      # Pre-built templates
        "users": 25,
        "support": "email",
        "sla": "99%",
    },
    "professional": {
        "price": 100_000,
        "drills": "unlimited",
        "users": 100,
        "custom_scenarios": True,
        "support": "dedicated",
        "sla": "99.5%",
    },
    "enterprise": {
        "price": 150_000,
        "drills": "unlimited",
        "users": "unlimited",
        "custom_scenarios": True,
        "on_prem": True,
        "support": "24/7",
        "sla": "99.9%",
        "baa": True,
    },
}
```

---

## Crisis Drill Templates

### 1. Service Outage

```yaml
name: "Critical Service Outage"
polynomial: CRISIS
initial_state: INCIDENT
citizens:
  - archetype: on_call_engineer
    eigenvectors: {stress: 0.8, expertise: 0.7}
  - archetype: incident_commander
    eigenvectors: {leadership: 0.9, calm: 0.7}
  - archetype: executive
    eigenvectors: {urgency: 0.9, visibility: 0.8}
  - archetype: customer_success
    eigenvectors: {empathy: 0.9, communication: 0.8}
scenario:
  trigger: "Primary database cluster unreachable"
  escalation_path: [engineer, commander, executive]
  success_criteria: "Service restored, postmortem scheduled"
```

### 2. Data Breach

```yaml
name: "Data Breach Response"
polynomial: CRISIS
initial_state: INCIDENT
citizens:
  - archetype: security_analyst
  - archetype: legal_counsel
  - archetype: pr_director
  - archetype: ciso
scenario:
  trigger: "Anomalous data exfiltration detected"
  compliance_requirements: [GDPR_72h, SEC_4day]
  success_criteria: "Contained, notified, documented"
```

---

## Open Questions

1. **Domain authoring**: How do enterprises define their own polynomials?
2. **Data integration**: How to connect to enterprise data sources?
3. **Compliance certification**: SOC2, HIPAA, FedRAMP paths?
4. **White-label**: How much customization?
5. **LLM selection**: Customer-provided models?
6. **Scenario library**: Community-contributed templates?
7. **Pricing validation**: Are tiers right for market?

---

## Go-to-Market

### Lighthouse Customers

| Segment | Target Companies | Value Prop |
|---------|------------------|------------|
| **Tech** | Post-Series B startups | Crisis readiness without dedicated team |
| **Finance** | Regional banks | Compliance drill documentation |
| **Healthcare** | Hospital systems | HIPAA incident response training |

### Sales Motion

1. **Demo**: Run a crisis drill in prospect's domain
2. **Pilot**: 30-day free trial with one department
3. **Land**: Starter tier for initial team
4. **Expand**: Professional/Enterprise as adoption grows

---

## Dependencies

| System | Usage |
|--------|-------|
| `agents/town/` | Simulation core |
| `agents/poly/` | Domain polynomials |
| `agents/operad/` | Domain grammar |
| `protocols/tenancy/` | Multi-tenant isolation |
| `protocols/terrarium/` | Gateway + metrics |
| `protocols/api/` | REST endpoints |
| `infra/k8s/` | Deployment manifests |

---

## Differentiator

**Authentic agent consent + full audit trail.**

> We already emit structured spans and budget enforcement.
> Competitors lack audit-first design.
> Logged force/apology mechanics reduce legal risk.

The consent ledger is not just ethical—it's a compliance feature. Every agent decision is traceable, replayable, and exportable for regulators.

---

## UX Research: Reference Flows

### Proven Patterns from Enterprise Crisis Simulation Platforms

#### 1. Immersive Labs Crisis Sim
**Source**: [Immersive Labs Crisis Sim](https://www.immersivelabs.com/products/crisis-sim)

Immersive Labs' approach to crisis simulation provides critical enterprise patterns:

| Immersive Labs Pattern | Domain Simulation Adaptation |
|-----------------------|------------------------------|
| **Scenario-based training** (emulate authentic threats) | `DomainPolynomial` — configurable states and transitions |
| **Decision-making under time constraints** | `TimePressure` — countdown timers, escalation triggers |
| **Team coordination** | `CoalitionDrills` — multi-role exercises |
| **Actionable strategies output** | `PlaybookGeneration` — export learnings as runbooks |

**Key Insight**: "Challenge teams to prioritize actions, assess risks, and make decisions under tight time constraints — just like in real-world breaches." Simulations must feel **consequential**.

#### 2. MIT Sloan Crisis Training Research
**Source**: [MIT Sloan: How to Supercharge Crisis Training](https://sloanreview.mit.edu/article/how-to-supercharge-crisis-training/)

MIT Sloan's research on modern crisis training informs adaptive simulation design:

| MIT Sloan Pattern | Domain Simulation Application |
|-------------------|-------------------------------|
| **Beyond predefined response plans** | `AdaptiveScenarios` — evolving situations |
| **Real-time adaptability** | `DynamicInjects` — runtime scenario modifications |
| **Unpredictable disruptions** | `void.sip` — entropy-driven surprises |
| **Leadership development focus** | `LeadershipMetrics` — track decision quality |

**Key Insight**: "Modern crises strike without warning or a playbook...organizations need to develop leaders' real-time adaptability." Drills must **surprise**, not just confirm.

#### 3. Conducttr Experience Platform
**Source**: [Conducttr Crisis Simulation](https://www.conducttr.com/)

Conducttr's experience platform provides exercise development patterns:

| Conducttr Pattern | Domain Simulation Application |
|-------------------|------------------------------|
| **Rapid exercise development** | `ScenarioBuilder` — template-based drill creation |
| **Engaging exercise deployment** | `ImmersiveDelivery` — multi-channel output |
| **Experience is everything** mantra | `AtmosphericRealism` — ambient pressure cues |

#### 4. YUDU Sentinel Simulations
**Source**: [YUDU Sentinel](https://www.sentinelresilience.com/crisis-simulations)

Sentinel's team training approach provides skill-building patterns:

| Sentinel Pattern | Domain Simulation Application |
|------------------|------------------------------|
| **Decision-making skill building** | `DecisionTree` — track choices over time |
| **Communication improvement** | `CommunicationMetrics` — analyze message clarity |
| **Team-working skills** | `TeamDynamics` — coalition effectiveness scores |

---

## Precise User Flows

### Flow 1: Enterprise Onboarding ("The Pilot")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: New enterprise customer evaluating platform                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. SALES DEMO (30 minutes)                                                  │
│     ├── Sales rep shares screen                                              │
│     ├── "Let me show you a data breach drill in your industry"              │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  LIVE DEMO: Healthcare Data Breach                          │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  Scenario: Anomalous data exfiltration detected             │     │
│     │   │                                                             │     │
│     │   │  Citizens active:                                           │     │
│     │   │  • 🔒 Security Analyst (you)                                │     │
│     │   │  • ⚖️ Legal Counsel (AI)                                    │     │
│     │   │  • 📢 PR Director (AI)                                      │     │
│     │   │  • 🏥 CISO (AI)                                             │     │
│     │   │                                                             │     │
│     │   │  Timer: GDPR 72h notification deadline                      │     │
│     │   │                                                             │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     ├── Prospect can take over and interact                                  │
│     └── "See how decisions cascade? Now imagine your team..."              │
│                                                                              │
│  2. PILOT AGREEMENT (same day)                                               │
│     ├── 30-day free pilot with one department                                │
│     ├── Pre-configured drill: "Critical Service Outage"                     │
│     ├── 10 seats included                                                    │
│     └── Dedicated success manager assigned                                   │
│                                                                              │
│  3. PILOT EXECUTION (weeks 1-4)                                              │
│     ├── Week 1: Team onboarding + first drill (guided)                       │
│     ├── Week 2: Second drill (less guidance)                                 │
│     ├── Week 3: Custom scenario workshop                                     │
│     └── Week 4: Independent drill + review meeting                           │
│                                                                              │
│  4. CONVERSION                                                               │
│     ├── Analytics review: "Your team improved 40% in response time"         │
│     ├── Quote presentation: Starter / Professional / Enterprise             │
│     └── Contract signature via e-sign                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 2: Running a Crisis Drill ("The Exercise")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: Team of 8 running a data breach drill                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. PRE-DRILL SETUP (15 minutes before)                                      │
│     ├── Facilitator opens admin panel                                        │
│     ├── Selects drill: "Data Breach Response v2.1"                          │
│     ├── Assigns roles:                                                       │
│     │   ├── Alice → Security Analyst                                        │
│     │   ├── Bob → Incident Commander                                        │
│     │   ├── Carol → Legal Counsel                                           │
│     │   ├── Dan → PR Director                                               │
│     │   └── Eve, Frank, Grace, Henry → Supporting roles                     │
│     ├── Sets difficulty: "Medium (some surprises)"                          │
│     └── [Launch Drill in 5 minutes]                                          │
│                                                                              │
│  2. DRILL START (T+0)                                                        │
│     ├── All participants receive notification                                │
│     ├── Screen shows: "INCIDENT DETECTED"                                   │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  🚨 ACTIVE INCIDENT                        Timer: 71:45:00  │     │
│     │   │     (GDPR 72-hour notification deadline)                    │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  SITUATION:                                                 │     │
│     │   │  Anomalous data transfer detected at 02:47 UTC.            │     │
│     │   │  Source: Database cluster DB-PROD-03                       │     │
│     │   │  Volume: ~2.3TB transferred to unknown external IP         │     │
│     │   │                                                             │     │
│     │   │  YOUR ROLE: Security Analyst                               │     │
│     │   │                                                             │     │
│     │   │  Available actions:                                         │     │
│     │   │  • [Investigate logs]                                       │     │
│     │   │  • [Contain affected systems]                               │     │
│     │   │  • [Notify Incident Commander]                              │     │
│     │   │  • [Request forensics team]                                 │     │
│     │   │                                                             │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Each role sees their relevant view and actions                       │
│                                                                              │
│  3. MID-DRILL INJECT (T+15 minutes)                                          │
│     ├── Facilitator triggers surprise inject:                                │
│     │   "Media outlet has published story about breach"                     │
│     ├── PR Director's screen lights up                                       │
│     ├── Timer pressure increases                                             │
│     └── Team must adapt to new pressure                                      │
│                                                                              │
│  4. DRILL RESOLUTION (T+45-60 minutes)                                       │
│     ├── Team reaches resolution state:                                       │
│     │   ├── Breach contained ✓                                               │
│     │   ├── Notifications sent ✓                                             │
│     │   ├── Media statement drafted ✓                                        │
│     │   └── Postmortem scheduled ✓                                           │
│     ├── [End Drill] triggered by facilitator                                 │
│     └── Transition to debrief                                                │
│                                                                              │
│  5. DEBRIEF (15-20 minutes)                                                  │
│     ├── Automatic timeline reconstruction                                    │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  DRILL ANALYSIS                                             │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  TIMELINE:                                                  │     │
│     │   │  00:00 — Incident detected                                  │     │
│     │   │  00:03 — Alice began log investigation                      │     │
│     │   │  00:07 — Bob notified (4 min delay — above target)          │     │
│     │   │  00:12 — Containment initiated                              │     │
│     │   │  00:15 — Media inject triggered                             │     │
│     │   │  00:18 — Dan drafted statement (excellent response)         │     │
│     │   │  00:35 — Carol completed legal assessment                   │     │
│     │   │  00:47 — Resolution achieved                                │     │
│     │   │                                                             │     │
│     │   │  METRICS:                                                   │     │
│     │   │  • Time to contain: 12 min (target: 15 min) ✅              │     │
│     │   │  • Escalation delay: 4 min (target: 2 min) ⚠️               │     │
│     │   │  • Communication clarity: 87% ✅                            │     │
│     │   │  • Overall score: B+                                        │     │
│     │   │                                                             │     │
│     │   │  [Export Report] [Schedule Follow-up] [Run Again]           │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Report exported to compliance folder (audit trail)                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 3: Custom Scenario Creation ("The Author")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: Customer creates domain-specific drill                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. SCENARIO BUILDER                                                         │
│     ├── Customer opens "Create New Drill"                                    │
│     ├── Template selection:                                                  │
│     │   ├── [ ] Start from scratch                                          │
│     │   ├── [x] Start from template: "Service Outage"                       │
│     │   └── [ ] Clone existing: "Q3 Tabletop Exercise"                      │
│     │                                                                        │
│     └── Enters Scenario Builder:                                             │
│                                                                              │
│         ┌─────────────────────────────────────────────────────────────┐     │
│         │  SCENARIO BUILDER                                           │     │
│         ├─────────────────────────────────────────────────────────────┤     │
│         │                                                             │     │
│         │  NAME: Vendor Payment System Failure                       │     │
│         │                                                             │     │
│         │  POLYNOMIAL STATE MACHINE:                                  │     │
│         │  ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐     │     │
│         │  │ NORMAL │ →  │INCIDENT│ →  │RESPONSE│ →  │RECOVERY│     │     │
│         │  └────────┘    └────────┘    └────────┘    └────────┘     │     │
│         │       ↑                                         │          │     │
│         │       └─────────────────────────────────────────┘          │     │
│         │                                                             │     │
│         │  CITIZENS:                                                  │     │
│         │  [+ Add Citizen]                                           │     │
│         │  • Finance Controller (eigenvectors: cautious, detail-oriented) │
│         │  • Vendor Manager (eigenvectors: relationship-focused)      │     │
│         │  • CFO (eigenvectors: strategic, impatient)                │     │
│         │                                                             │     │
│         │  INJECTS (triggers at specific times or conditions):       │     │
│         │  [+ Add Inject]                                            │     │
│         │  • T+10: "Vendor calls: payment was due yesterday"         │     │
│         │  • On RESPONSE: "Board requests update"                    │     │
│         │                                                             │     │
│         │  SUCCESS CRITERIA:                                          │     │
│         │  [x] All vendors contacted                                  │     │
│         │  [x] Backup payment method activated                        │     │
│         │  [x] Root cause identified                                  │     │
│         │                                                             │     │
│         │  [Preview] [Save Draft] [Publish]                          │     │
│         └─────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  2. PREVIEW & TEST                                                           │
│     ├── [Preview] launches solo run-through                                  │
│     ├── Customer plays all roles to verify flow                              │
│     └── Adjusts injects and citizen behaviors                                │
│                                                                              │
│  3. PUBLISH                                                                  │
│     ├── Scenario added to organization's library                             │
│     ├── Version control: v1.0                                                │
│     └── Permission settings: who can run, who can edit                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 4: Analytics Dashboard ("The Compliance View")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: CISO reviewing quarterly drill performance                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ANALYTICS DASHBOARD                                                         │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Q4 2025 PERFORMANCE                                                     ││
│  ├─────────────────────────────────────────────────────────────────────────┤│
│  │                                                                          ││
│  │  SUMMARY                                                                 ││
│  │  • Drills completed: 12                                                  ││
│  │  • Participants: 47 unique                                               ││
│  │  • Average score: B (up from C+ in Q3)                                   ││
│  │  • Compliance target: 95% (achieved: 97%)                                ││
│  │                                                                          ││
│  │  TREND: Response Time                                                    ││
│  │  ┌────────────────────────────────────────────────────┐                  ││
│  │  │        15m ╷                                        │                 ││
│  │  │            │  ╭─╮                                   │                 ││
│  │  │        10m │  │ ╰──╮        ╭──╮                   │                 ││
│  │  │            │──╯    ╰──────╮│  ╰──╮                 │                 ││
│  │  │         5m │              ╰╯    ╰─────             │                 ││
│  │  │            ├───────────────────────────────────────│                 ││
│  │  │             Oct    Nov    Dec    Jan               │                 ││
│  │  └────────────────────────────────────────────────────┘                  ││
│  │                                                                          ││
│  │  TOP PERFORMERS                    NEEDS IMPROVEMENT                     ││
│  │  • Dan (PR): 94% clarity          • Bob: Escalation speed               ││
│  │  • Alice (Security): Fast ID      • New hires: Role familiarity         ││
│  │                                                                          ││
│  │  COMPLIANCE ARTIFACTS                                                    ││
│  │  [Download Q4 Report]  [Schedule Board Review]  [Export for Audit]      ││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Interaction Micropatterns

### Role-Based View Switching

```
During drill, participants can peek at system-wide view:

┌─────────────────────────────────────────────────────────────┐
│ VIEW MODE                                                    │
│                                                              │
│ [🎯 My Role] [👥 Team View] [🗺️ System Map]                │
│                                                              │
│ My Role: See only what your character knows                 │
│ Team View: See all team member actions (read-only)          │
│ System Map: See incident topology (facilitator only)        │
└─────────────────────────────────────────────────────────────┘
```

### Audit Trail Visualization

```
Every action is logged for compliance:

┌─────────────────────────────────────────────────────────────┐
│ AUDIT LOG (Drill: Data Breach Q4)                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 14:03:47 | Alice | ACTION | Queried logs for DB-PROD-03    │
│ 14:04:12 | Alice | COMM   | Notified Bob via in-app        │
│ 14:07:33 | Bob   | DECISION | Elevated to RESPONSE state   │
│ 14:07:35 | System | STATE  | INCIDENT → RESPONSE           │
│ 14:08:01 | Carol | ACTION | Began legal assessment         │
│ ...                                                         │
│                                                              │
│ [Export JSON] [Export PDF] [Filter by Role]                 │
└─────────────────────────────────────────────────────────────┘
```

---

## References

- Master plan: `plans/core-apps-synthesis.md` §2.5
- Original ideas: `brainstorming/2025-12-15-money-maximizing-ideas.md`
- Tenancy code: `impl/claude/protocols/tenancy/`
- K8s manifests: `impl/claude/infra/k8s/manifests/`

### UX Research Sources

- [Immersive Labs Crisis Sim](https://www.immersivelabs.com/products/crisis-sim) — Cyber crisis simulation patterns
- [MIT Sloan: Supercharge Crisis Training](https://sloanreview.mit.edu/article/how-to-supercharge-crisis-training/) — Adaptive training research
- [Conducttr Crisis Platform](https://www.conducttr.com/) — Exercise development and deployment
- [YUDU Sentinel Simulations](https://www.sentinelresilience.com/crisis-simulations) — Team skill building
- [PREVENCY Crisis Simulation](https://prevency.com/en/crisis-simulation/) — Virtual crisis management training

---

*Last updated: 2025-12-15*
