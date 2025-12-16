# Project Proposals: kgents Strategic Directions

**Date**: 2025-12-15
**Requested by**: Kent
**Prepared by**: Claude Opus 4.5

---

## Context

After running `/hydrate` to review in-flight work status, Kent asked:

> "Can you propose 5 different projects to execute with kgents using internet research and knowledge of our recent priorities?"

This document captures the research conducted and the resulting project proposals.

---

## Current Priorities (from `_focus.md`)

- **COMPOSITIONAL GENERATIVE UI**
- **LLM Agents using haiku tokens liberally in Agent Town**
- **Shockingly delightful consumer, prosumer, and professional experience**
- **Builder Workshop** (chefs in a kitchen, gardeners in a garden, kids on a playground)
- **"Holographic metaphor reification"**
- **Westworld-like simulation park** with infinite dimension detail

### Heritage References (CHATDEV, SIMULACRA, ALTERA, VOYAGER, AGENT HOSPITAL)

Kent's vision extends these foundational papers with polyfunctor category theory for system orchestration, proprioception, self-deployment modification, and emergent complex adaptive system behavior.

---

## Research Summary

### Multi-Agent AI Platforms (2025)

**Market Size**: $5.3-5.4 billion globally as of early 2025

**Key Frameworks**:
- **LangChain/LangGraph**: Open-source agentic systems
- **AutoGen (Microsoft)**: Multi-agent collaboration, task delegation
- **CrewAI**: No-code/code-based workflow automation
- **OpenAI Agents SDK**: Lightweight Python framework (11k+ GitHub stars)

**Consumer Adoption Trends**:
- 32% of Gen Z comfortable with AI agents handling shopping
- 34% prefer AI agents to avoid repeating information
- 37% comfortable with AI creating personalized content

**2025 Evolution**: Multi-agent systems evolving into "AI swarms" mimicking natural systems like ant colonies. Moving from task-specific tools to autonomous co-workers.

**Sources**:
- [Multi-AI Agent Systems 2025](https://ioni.ai/post/multi-ai-agents-in-2025-key-insights-examples-and-challenges)
- [Top AI Agent Frameworks](https://www.shakudo.io/blog/top-9-ai-agent-frameworks)
- [Best Multi-Agent AI Frameworks](https://www.multimodal.dev/post/best-multi-agent-ai-frameworks)

---

### Generative UI & AI-Powered Interface Builders

**Key Players**:

| Platform | Capability |
|----------|------------|
| **Figma Make** | Full interfaces from text; editable hierarchy, alignment, spacing |
| **UX Pilot** | Wireframes, mockups, screen flows from prompts ($12/mo) |
| **Uizard** | App mockups from text, screenshots, or hand-drawn sketches |
| **Galileo AI (Stitch)** | High-fidelity mobile/web UI generation |
| **Thesys C1** | **Runtime** UI generation while app is running (not mockups) |

**Google's Generative UI Research**:
> "Generative UI is a powerful capability in which an AI model generates not only content but an entire user experience... dynamically creates immersive visual experiences and interactive interfaces—such as web pages, games, tools, and applications—automatically designed and fully customized in response to any prompt."

Integrated into Google Search via AI Mode (Gemini 3).

**Key Insight**: Thesys C1 proves that generative UI can work at runtime, not just design-time. This aligns with kgents' reactive widget composition.

**Sources**:
- [Google Generative UI Research](https://research.google/blog/generative-ui-a-rich-custom-visual-interactive-user-experience-for-any-prompt/)
- [Thesys - The Generative UI Company](https://www.thesys.dev)
- [Top AI UI Generators 2025](https://adamfard.com/blog/ai-ui-generator)

---

### AI Agent Monetization & SaaS Pricing

**Pricing Model Shift**:

Traditional SaaS charges for **access to features** (seat-based). Agentic monetization charges for **actions, outcomes, or usage**.

**Five Dominant Models**:
1. **Usage-Based**: Tokens, API calls, execution time
2. **Subscription Licensing**: Fixed monthly/annual
3. **Outcome-Based**: Measurable success (leads, tickets resolved)
4. **Bundled SaaS**: Agents embedded in existing products
5. **Marketplace/API**: Discovery + lead generation

**Enterprise Reality** (2025): Most deals still use usage-based or hybrid pricing. Pure outcome-based remains rare due to buyer discomfort.

**Salesforce AgentExchange**: New marketplace for agents, actions, topics, templates. Introduced Agentic Enterprise License Agreement (AELA) with flexible credits.

**Monetization Infrastructure**:
- **Paid** (by Manny Medina, ex-Outreach): Platform for measuring, pricing, managing agent economics
- **Alguna**: Purpose-built AI monetization for SaaS (pay-per-use, agent billing, hybrid models)

**Revenue Examples**:
- Adobe: $125M from standalone AI products (Q1 2025)
- AI-native startups (Perplexity, Typeface): Reaching $5-10M ARR faster than prior SaaS generations

**Sources**:
- [How to Monetize AI Agents](https://www.aalpha.net/blog/how-to-monetize-ai-agents/)
- [McKinsey: AI SaaS Business Models](https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/upgrading-software-business-models-to-thrive-in-the-ai-era)
- [Salesforce AgentExchange](https://www.cio.com/article/3837608/salesforces-agentexchange-targets-ai-agent-adoption-monetization.html)
- [AI Pricing Field Report 2025](https://metronome.com/blog/ai-pricing-in-practice-2025-field-report-from-leading-saas-teams)

---

### Immersive AI Storytelling & Interactive Narrative

**Research Systems**:

| System | Innovation |
|--------|------------|
| **Storycaster** | Generative AI CAVE system; transforms physical rooms into storytelling environments |
| **LLM Interactive Drama** | User plays character role; focuses on **Immersion** + **Agency** metrics |
| **Story Forge** | Card-based interactive narrative; user-driven creative process |

**Market**: AI-driven creative tools for interactive storytelling growing at 35%+ CAGR

**Technical Advances** (July 2025):
- LLMs and GANs evolved from experimental to "powerful creative engines"
- Context-aware narratives that dynamically adapt to user choices
- GPT + Sora generating dynamic dialogue and scenes in text/video

**Beyond Entertainment**: Applications in mental health, education, marketing

**Key Research Insight** (LLM Interactive Drama):
> "A novel AI-based dialogue scenario where the user plays the role of a character in the story, has conversations with characters played by LLM agents, and experiences an unfolding story."

Two core metrics: **Immersion** (feeling present) and **Agency** (ability to influence).

**Sources**:
- [LLM Interactive Drama (Immersion + Agency)](https://arxiv.org/html/2502.17878v1)
- [Storycaster: Room-Based Storytelling](https://arxiv.org/html/2510.22857)
- [Story Forge: Card-Based Framework](https://www.mdpi.com/2079-9292/14/15/2955)
- [AI Interactive Storytelling Platforms](https://reelmind.ai/blog/ai-interactive-storytelling-platforms-beyond-traditional-narratives)

---

## Project Proposals

### 1. Agent Town Marketplace

**Concept**: A Salesforce AgentExchange-style marketplace where users create, share, and monetize custom Town citizens and coalitions.

**Why Now**: The $5.4B AI agent market is shifting from seat-based to outcome-based pricing. kgents SaaS infrastructure (Stripe billing, OpenMeter usage, multi-tenant RLS) is already built.

**Leverages**:
- `agents/town/` coalitions and CitizenPolynomial
- `protocols/billing/` Stripe integration
- `protocols/tenancy/` multi-tenant RLS
- Builder Workshop archetypes (Scout, Sage, Spark, Steady, Sync)

**Revenue Model**:

| Tier | Price | Features |
|------|-------|----------|
| Free | $0 | 5 citizens, template archetypes only |
| Pro | $29/mo | Custom eigenvector tuning, coalition export, 50 citizens |
| Enterprise | Custom | Private Town instances, API access, usage-based LLM credits |

**Implementation Path**:
1. Add `town.marketplace.*` AGENTESE paths
2. Implement citizen serialization/deserialization (eigenvectors, skills, history)
3. Create "Publish to Marketplace" flow in web UI
4. Add discovery/search with archetype filtering
5. Implement revenue share model (70/30 creator/platform)

**Differentiator**: Not just agents—**citizens with personality** (eigenvector-defined), **visible coalition dynamics** (k-clique percolation), and **categorical composition** (TownOperad).

---

### 2. Generative UI Studio

**Concept**: Users describe interfaces in natural language; Builder Workshop agents collaboratively generate reactive widget compositions.

**Why Now**: Google's Generative UI research shows LLMs can generate entire UIs contextually. Thesys C1 proves runtime UI generation works. kgents already has the reactive substrate.

**Leverages**:
- `agents/i/reactive/` widget composition (`>>` and `//` operators)
- `agents/town/workshop.py` Builder lifecycle
- Projection Protocol (CLI/marimo/JSON/VR)
- Workshop phase mapping (EXPLORING→Scout, DESIGNING→Sage, etc.)

**Workflow**:
```
User: "Show me a dashboard with citizen health metrics and coalition activity"
     ↓
Scout (EXPLORING): Identifies required data sources
     ↓
Sage (DESIGNING): Plans widget composition tree
     ↓
Spark (PROTOTYPING): Generates initial widget code
     ↓
Steady (REFINING): Validates functor laws, optimizes
     ↓
Sync (INTEGRATING): Wires to live data streams
     ↓
Output: Live reactive dashboard
```

**Implementation Path**:
1. Add `concept.ui.*` AGENTESE paths for UI generation requests
2. Create `UIGenerationTask` for Workshop loop
3. Wire Workshop outputs to reactive primitive constructors
4. Implement preview mode (render without committing)
5. Add "Export to marimo/React" functionality

**Differentiator**: Not mockups—**live, composable widgets** with category-theoretic laws (functor composition verified). Each Builder archetype handles one concern (separation of concerns via personality).

---

### 3. Punchdrunk Park

**Concept**: The "Westworld-like simulation" vision—users INHABIT characters in Agent Town scenarios where NPCs (citizens) have genuine agency to refuse, negotiate, or surprise.

**Why Now**: LLM Interactive Drama research validates immersion + agency as core metrics. kgents INHABIT mode (all 11 phases complete) already implements consent debt and alignment thresholds.

**Leverages**:
- `agents/town/` INHABIT mode with consent debt ([0,1] continuous)
- `agents/k/` K-gent soul middleware for authentic dialogue
- `protocols/agentese/` umwelt-based perception
- CitizenPolynomial state machine
- Force mechanic (3x tokens, 3/session, logged)

**The Holographic Metaphor Reification**:
```python
# Same Town, different observers, different experiences
await logos.invoke("world.town.manifest", architect_umwelt)   # → Power structures
await logos.invoke("world.town.manifest", poet_umwelt)        # → Relationship webs
await logos.invoke("world.town.manifest", economist_umwelt)   # → Resource flows
await logos.invoke("world.town.manifest", child_umwelt)       # → Wonder and play
```

**Scenario Templates**:
- **Mystery**: Something happened; citizens have partial knowledge; player investigates
- **Collaboration**: Shared goal requiring coalition formation
- **Conflict**: Competing factions with incompatible objectives
- **Emergence**: No predefined plot; pure simulation with serendipity injection

**Implementation Path**:
1. Create scenario template system (`void.narrative.scenario.*`)
2. Implement "Director" meta-agent for pacing and serendipity injection
3. Add umwelt selection at INHABIT start
4. Create narrative replay/export (witness traces as story)
5. Implement multi-player INHABIT (shared Town, different perspectives)

**Differentiator**: Citizens can **say no**. The Punchdrunk principle: collaboration > control. Refusal is a feature, not a bug. Force mechanic is expensive and logged—consent matters.

---

### 4. Agent Academy

**Concept**: Inspired by Agent Hospital—a domain where AI agents learn through simulation. Users watch (or guide) novice agents grow expertise by completing tasks, making mistakes, and receiving feedback from senior agents.

**Why Now**: Educational multi-agent systems are a growing market. 32% of Gen Z comfortable with AI handling tasks. T-gent (Type V AdversarialGym) is 90% complete and ready for this.

**Leverages**:
- `agents/t/` T-gent testing framework (Type V AdversarialGym)
- `protocols/nphase/` for learning curriculum (11-phase lifecycle)
- Builder Workshop progression
- Eigenvector drift visualization

**Skill Polynomial Model**:
```python
# Skills compose like functions
skill_a: Agent[Input, Intermediate]
skill_b: Agent[Intermediate, Output]
combined: Agent[Input, Output] = skill_a >> skill_b

# Mastering A and B unlocks A>>B composition
if citizen.has_skill(skill_a) and citizen.has_skill(skill_b):
    citizen.unlock_skill(skill_a >> skill_b)
```

**Learning Modes**:
- **Observe**: Watch senior citizens handle tasks (passive learning)
- **Assist**: Help senior citizen, receive feedback
- **Solo**: Attempt task alone, get graded
- **Teach**: Explain to junior citizen (reinforcement through teaching)

**Implementation Path**:
1. Create `AcademyCitizen(Builder)` with learning state polynomial
2. Implement skill acquisition as polynomial state transitions
3. Add curriculum system using N-Phase templates
4. Create mentor/mentee relationship type in coalition system
5. Visualize growth in web UI (eigenvector drift over time, skill tree)

**Differentiator**: Category-theoretic skill composition—skills aren't just unlocked, they **compose**. Visible personality emergence through eigenvector drift. Learning is a first-class mechanic.

---

### 5. Coalition Forge

**Concept**: A no-code tool for assembling agent coalitions that accomplish real tasks—research reports, code reviews, content creation—with visible collaboration dynamics.

**Why Now**: CrewAI and AutoGen prove multi-agent task completion works. kgents k-clique percolation already handles coalition formation. Workshop task lifecycle is complete.

**Leverages**:
- `agents/town/` TownOperad composition grammar
- `agents/operad/` AGENT_OPERAD for operation definitions
- `agents/sheaf/` emergence (compatible locals → global)
- Workshop `FluxTask` lifecycle
- k-clique percolation for coalition formation

**Task Types**:

| Task | Coalition Shape | Output |
|------|-----------------|--------|
| Research Report | Scout + Sage + 2 specialists | Markdown document |
| Code Review | Steady + Sync + domain expert | PR comments + suggestions |
| Content Creation | Spark + Sage + audience-tuned citizens | Multi-format content |
| Decision Analysis | Full archetype set | Pros/cons matrix + recommendation |

**Visible Dynamics**:
- Watch agents negotiate roles in real-time
- See eigenvector-based trust form (EigenTrust algorithm)
- Observe emergent leadership (highest trust citizen coordinates)
- Replay coalition formation decisions

**Implementation Path**:
1. Create `ForgeTask` interface with input/output typing
2. Implement `world.task.*` AGENTESE paths for task submission
3. Add coalition formation visualization (who joins, why)
4. Create task replay/rewind in web UI
5. Implement task templates with suggested coalition compositions

**Differentiator**: Not just task completion—**visible process**. "Kids on a playground" energy: watch them figure it out together. Coalition dynamics are the product, not just the task output.

---

## Recommendation Matrix

| Project | Revenue | Technical Lift | Joy Factor | Alignment |
|---------|---------|----------------|------------|-----------|
| Agent Town Marketplace | ★★★★★ | ★★☆☆☆ | ★★★☆☆ | MONEY |
| Generative UI Studio | ★★★★☆ | ★★★☆☆ | ★★★★★ | VISUAL UI |
| Punchdrunk Park | ★★★☆☆ | ★★★★☆ | ★★★★★ | HOLOGRAPHIC |
| Agent Academy | ★★★★☆ | ★★★☆☆ | ★★★★☆ | T-GENT |
| Coalition Forge | ★★★★☆ | ★★☆☆☆ | ★★★★☆ | FUN+TECHNICAL |

**Suggested Sequence**:
1. **Coalition Forge** — Low lift, high visibility, proves the dynamics
2. **Agent Town Marketplace** — Monetization infrastructure already exists
3. **Punchdrunk Park** — The grand vision, builds on 1 and 2

---

## Appendix: kgents Systems Leveraged

All proposals build on these existing production systems:

| System | Location | Role in Proposals |
|--------|----------|-------------------|
| Agent Town | `agents/town/` | Foundation for all 5 proposals |
| AGENTESE | `protocols/agentese/` | Path-based interaction model |
| Reactive | `agents/i/reactive/` | Widget composition for UI Studio |
| Workshop | `agents/town/workshop.py` | Builder lifecycle for UI Studio, Academy |
| K-gent | `agents/k/` | Soul middleware for Punchdrunk |
| N-Phase | `protocols/nphase/` | Curriculum for Academy |
| Billing | `protocols/billing/` | Stripe for Marketplace |
| Tenancy | `protocols/tenancy/` | Multi-tenant for Marketplace |
| Operad | `agents/operad/` | Composition grammar for Forge |
| Sheaf | `agents/sheaf/` | Emergence for Forge |

---

*Generated 2025-12-15 via `/hydrate` → research → synthesis*
