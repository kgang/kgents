# The Exploration Harness: A Modern Memex for Agent-Human Co-Navigation

> *"The essential feature of the memex lies in 'associative indexing'—the basic idea of which is a provision whereby any item may be caused at will to select immediately and automatically another."*
> — Vannevar Bush, "As We May Think" (1945)

> *"Every trail is evidence. Every exploration creates proof obligations."*
> — kgents Constitution (2025)

**Status:** Synthesis + Vision
**Date:** 2025-12-22
**Heritage:** Vannevar Bush's Memex, Bounded Rationality, Agent-as-Witness

---

## Executive Summary

The **Exploration Harness** transforms how Kent and AI agents navigate complex codebases together. It operationalizes three principles:

1. **Trails are first-class artifacts** — Not just navigation history, but shareable, verifiable evidence
2. **Bounded autonomy** — Exploration terminates, loops are detected, resources are finite
3. **Evidence-based claims** — You can't assert what you haven't explored

Today we completed **110 tests** across 7 implementation phases. But the harness is infrastructure for something larger: a **modern Memex**—the 80-year-old vision finally realized for human-agent collaboration.

---

## Part 1: What We Built (The Foundation)

### 1.1 The Seven Phases

| Phase | Implementation | Key Insight |
|-------|----------------|-------------|
| 1. Core Types | `ContextNode`, `Trail`, `Evidence`, `Observer` | The hypergraph is observer-dependent (Umwelt) |
| 2. Budget & Loops | `NavigationBudget`, `LoopDetector` | Exploration must terminate; spinning is prevented |
| 3. Evidence & Commitment | `TrailAsEvidence`, `ASHCCommitment` | Claims require proof; levels are irreversible |
| 4. Harness Integration | `ExplorationHarness` | Unified safety wrapper |
| 5. Derivation Bridge | Trail patterns → principle signals | Exploration feeds understanding |
| 6. CLI | `kg explore` | Human interface |
| 7. AGENTESE | `self.explore.*` | Agent interface |

### 1.2 The Architecture

```
                     Human                        Agent
                       │                            │
                       ▼                            ▼
              ┌────────────────┐           ┌────────────────┐
              │  kg explore    │           │ self.explore.* │
              │  (CLI Handler) │           │ (AGENTESE Node)│
              └───────┬────────┘           └───────┬────────┘
                      │                            │
                      └──────────┬─────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │   ExplorationHarness    │
                    │  ┌──────┐ ┌──────────┐  │
                    │  │Budget│ │LoopDetect│  │
                    │  └──────┘ └──────────┘  │
                    │  ┌─────────┐ ┌───────┐  │
                    │  │Evidence │ │Commit │  │
                    │  └─────────┘ └───────┘  │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │     ContextGraph        │
                    │  (Typed-Hypergraph)     │
                    └─────────────────────────┘
```

### 1.3 Test Evidence

| Component | Tests | Status |
|-----------|-------|--------|
| Core harness | 47 | ✅ |
| CLI handler | 28 | ✅ |
| AGENTESE node | 35 | ✅ |
| **Total** | **110** | ✅ |

---

## Part 2: Why This Matters (The Vision)

### 2.1 Vannevar Bush's Unfulfilled Vision

In 1945, Vannevar Bush imagined the **Memex**—a device where:

> *"The user builds a trail of many items. Occasionally he inserts a comment of his own, either linking it into the main trail or joining it by a side trail to a particular item."*

Bush predicted:

> *"A new profession of trailblazers would appear for those who took pleasure in finding useful trails through the enormous mass of the common record."*

The web gave us hyperlinks, but **lost the trails**. URLs are destinations, not journeys. Browser history is a log, not an artifact. We got Bush's infrastructure without his insight: **the trail itself has value**.

**The Exploration Harness recovers the trail.**

### 2.2 The AI Safety Alignment

Recent research confirms the wisdom of bounded exploration:

From the [2025 AI Safety Index](https://futureoflife.org/ai-safety-index-summer-2025/):
> *"Empirical uplift studies are critical for grounding AI safety policy in observable outcomes."*

From the [International AI Safety Report 2025](https://internationalaisafetyreport.org/publication/international-ai-safety-report-2025):
> *"General-purpose AI 'agents' can autonomously plan and act to achieve goals with little or no human oversight."*

From research on [autonomous agents](https://arxiv.org/html/2502.02649v3):
> *"Greater agent autonomy amplifies the scope and severity of potential safety harms... human-defined safeguards to mitigate foreseeable issues are bounded by their initial specifications."*

The harness addresses this directly:
- **Budget bounds** prevent runaway exploration
- **Loop detection** prevents spinning
- **Evidence requirements** ground claims in observable trails
- **Commitment levels** prevent hedging

We're not adding safety as an afterthought. Per the [bounded alignment research](https://arxiv.org/pdf/2505.11866):
> *"If the goal is to make AGI agents robustly aligned, this alignment must become part of their character, not something added as an afterthought."*

### 2.3 The Human-Agent Collaboration Research

From [CHI 2024 research](https://dl.acm.org/doi/10.1145/3613904.3642564) on human-AI collaboration in shared workspaces:
> *"Previous work suggests higher autonomy does not always improve team performance—situation-dependent autonomy adaptation might be beneficial."*

The harness embodies **situational autonomy**:
- Agent can explore freely **within budget**
- Agent must commit claims **with evidence**
- Human can extend budget, reset loops, override
- Both see the same trail (shared workspace)

This aligns with [Microsoft's vision](https://www.microsoft.com/en-us/microsoft-365/blog/2025/09/18/microsoft-365-copilot-enabling-human-agent-teams/) for human-agent teams:
> *"Work is fundamentally a team sport, yet until now AI has largely been a personal assistant."*

The harness makes the agent a **co-explorer**, not just an executor.

### 2.4 The Agent-as-Witness Integration

From the kgents Constitution:
> *"The proof IS the decision. The mark IS the witness."*

The exploration harness operationalizes this:

```
Without harness: agent explores → makes claim → trust me
With harness:    agent explores → trail is evidence → claim is justified
```

Every navigation step is a mark. Every trail is proof. The harness transforms exploration from **opaque process** to **transparent witness**.

---

## Part 3: The Gap (What's Missing)

### 3.1 Abstract vs. Concrete

The hypergraph is currently **abstract**. `navigate("tests")` doesn't actually find test files—it returns synthetic nodes. The infrastructure exists (`hyperedge_resolvers.py`), but isn't wired up.

**Gap:** Exploration operates in simulation, not reality.

### 3.2 Ephemeral Trails

Trails disappear when the session ends. They're not persisted, queryable, or shareable across sessions.

**Gap:** Trails don't survive. Bush's vision of accumulated trails is lost.

### 3.3 Silent Safety

Budget and loop detection work, but silently. The agent experiences limits without understanding why.

**Gap:** Safety is invisible. Teaching mode would make it explicit.

### 3.4 Single Player

The harness tracks one exploration. Kent and agents can't co-explore the same trail simultaneously, or fork/merge trails.

**Gap:** Exploration is solitary, not collaborative.

---

## Part 4: The Transformative Vision

### 4.1 The Modern Memex

Imagine this workflow in 2026:

```
Kent: "Why is authentication failing in production?"

Agent: [Starts exploration at world.auth]
       [Navigates: auth → middleware → token_validation]
       [Detects loop: middleware calls itself recursively]
       [Records evidence: "Recursive call in validate_token line 47"]
       [Commits claim: "Token validation has unbounded recursion"
        Level: STRONG (5 evidence items, 2 strong)]

Kent: [Sees trail visualization in Web UI]
      [Forks trail to explore middleware configuration]
      [Finds: "Middleware stack misconfigured in prod"]
      [Merges trails: auth failure + config issue]

Agent: [Synthesizes: "Production auth fails because middleware
        config causes recursive validation"]
       [Trail is persisted to Witness]
       [Future sessions can replay: "Show me the auth investigation"]
```

This is **co-exploration**—Kent and agent navigating together, building shared trails, accumulating evidence.

### 4.2 The Trail as Living Document

Bush envisioned trails that grow:

> *"After a period of observation, Memex would be given instructions to search and build a new trail of thought, which it could do later even when the owner was not there."*

With the harness:
- **Trail persistence:** Saved to Witness, queryable by topic
- **Trail inheritance:** New explorations can fork from old trails
- **Trail synthesis:** Multiple trails merge into understanding
- **Trail replay:** "Walk me through how we found that bug"

### 4.3 The Evidence-First Development

Current development:
```
Write code → Test → Debug → Fix → Repeat
(Evidence scattered across logs, tickets, memory)
```

Evidence-first development:
```
Explore → Gather evidence → Commit claim → Implement fix
(Trail IS the evidence, persisted and queryable)
```

Before writing a fix, you must have explored enough to justify it. The harness enforces **epistemic hygiene**.

### 4.4 The Hot-Swap Principle

From Kent's witness marks:
> *"Hot swap kent/agents"*
> *"Health of the system is its ability to change between abstractions"*

The harness enables this:
- Same trail, different explorers
- Kent starts, agent continues
- Agent drafts, Kent refines
- Either can resume any trail

The **shared workspace** is the trail itself.

---

## Part 5: The Roadmap

### Phase 8: Concrete Resolution (Priority: HIGH)

Wire hyperedge resolvers to real files:

```python
# When navigating:
destinations = await resolve_hyperedge(current_node, "tests", project_root)
# Returns actual file paths, not synthetic nodes
```

**Impact:** Transforms from toy to tool.
**Effort:** Medium (infrastructure exists, needs wiring)
**Files:** `hyperedge_resolvers.py`, `self_explore.py`

### Phase 9: Trail Persistence (Priority: HIGH)

Persist trails to Witness service:

```python
# After significant exploration
await witness.mark(
    action="exploration_trail",
    reasoning=f"Investigated {claim}",
    trail=trail.share(),
    evidence_count=harness.get_evidence_summary().total_count,
)
```

**Impact:** Trails survive sessions, become queryable history.
**Effort:** Low (Witness exists, needs integration)
**Files:** `self_explore.py`, `services/witness.py`

### Phase 10: Web Visualization (Priority: MEDIUM)

React components for trail visualization:

```
impl/claude/web/src/components/exploration/
├── TrailView.tsx        # Graph visualization of trail
├── BudgetRing.tsx       # Circular budget indicator
├── EvidencePanel.tsx    # Evidence summary with strength badges
├── CommitDialog.tsx     # Claim commitment interface
└── ExplorationPage.tsx  # Full page experience
```

**Impact:** Visual joy, Kent can watch explorations unfold.
**Effort:** Medium (patterns exist from Town visualization)
**Inspiration:** Force-directed graph with trail as highlighted path

### Phase 11: Natural Language (Priority: MEDIUM)

Soul integration for conversational exploration:

```
Kent: "Find where we handle rate limiting"

Soul: [Translates to exploration commands]
      kg explore start world.api
      kg explore navigate middleware
      kg explore navigate rate_limit
      [Reports findings with evidence]
```

**Impact:** Kent's preferred interface, seamless exploration.
**Effort:** Medium (Soul dialogue exists, needs harness bridge)

### Phase 12: Co-Exploration (Priority: LOWER)

Multi-agent trail collaboration:

```python
# Fork a trail
forked_trail = trail.fork(name="Kent's investigation")

# Merge trails
merged = Trail.merge([agent_trail, kent_trail], strategy="union")

# Real-time sync (WebSocket)
await harness.sync(session_id="shared-investigation")
```

**Impact:** True human-agent collaboration.
**Effort:** High (new infrastructure)

### Phase 13: Semantic Loops (Priority: LOWER)

V-gent integration for semantic loop detection:

```python
class LoopDetector:
    async def check_semantic(self, node: ContextNode) -> LoopStatus:
        embedding = await self.vgent.embed(node.content)
        for prev in self.history:
            if cosine_similarity(embedding, prev) > 0.95:
                return LoopStatus.SEMANTIC_LOOP
        return LoopStatus.OK
```

**Impact:** Catches subtle loops (similar but not identical nodes).
**Effort:** Low (V-gent exists, needs wiring)

### Phase 14: Teaching Mode (Priority: LOWER)

Explain safety operations as they happen:

```
[Teaching Mode]
→ Following [tests] hyperedge from world.brain.core
→ Budget consumed: 1 step (49 remaining)
→ Evidence recorded: "Navigated tests from brain.core"
→ This evidence is WEAK (exploration fact, not conclusion)
→ To commit a claim, gather 3+ evidence items with 1+ strong
```

**Impact:** Onboarding, transparency, trust.
**Effort:** Low (logging infrastructure exists)

---

## Part 6: The Survivor Principle

From Kent's witness marks:
> *"The Survivor Principle: What survives an extinction event? Jewels with active use cases... Pattern: survival correlates with 'actually' not 'theoretically could'."*

The exploration harness survives because it **actually does something**:
- **Actually bounds** agent exploration
- **Actually detects** loops before they spin
- **Actually collects** evidence as you navigate
- **Actually requires** proof before commitment

This is not theoretical infrastructure. It's operational safety that works today.

---

## Part 7: The Constitutional Alignment

| Constitution Principle | Harness Implementation |
|------------------------|------------------------|
| **Symmetric Agency** | Same harness for Kent and agents |
| **Adversarial Cooperation** | Evidence can support or challenge claims |
| **Supersession Rights** | Higher commitment levels supersede lower |
| **The Disgust Veto** | Human can reset/halt any exploration |
| **Trust Accumulation** | Trails build evidence of alignment |
| **Fusion as Goal** | Co-exploration produces shared understanding |

---

## Conclusion: The Trailblazer's Tool

Bush predicted a profession of **trailblazers**:

> *"Those who took pleasure in finding useful trails through the enormous mass of the common record."*

The exploration harness is their tool. Not a search engine (destinations). Not a browser (history). But a **trail-first navigation system** where:

- Every step is witnessed
- Every trail is artifact
- Every claim is evidence-backed
- Every exploration is bounded

Kent and agents don't just find things—they **build trails through understanding**.

The harness doesn't constrain. It witnesses.

---

## Sources

- [Technical AI Safety Research Taxonomy 2025](https://forum.effectivealtruism.org/posts/8k6qXNEogoHiBRsjA/technical-ai-safety-research-taxonomy-attempt-2025)
- [Principles for Robust Bounded Alignment](https://arxiv.org/pdf/2505.11866)
- [Fully Autonomous AI Agents Should Not be Developed](https://arxiv.org/html/2502.02649v3)
- [International AI Safety Report 2025](https://internationalaisafetyreport.org/publication/international-ai-safety-report-2025)
- [2025 AI Safety Index](https://futureoflife.org/ai-safety-index-summer-2025/)
- [Human-AI Collaboration in Shared Workspaces (CHI 2024)](https://dl.acm.org/doi/10.1145/3613904.3642564)
- [Microsoft 365 Copilot: Human-Agent Teams](https://www.microsoft.com/en-us/microsoft-365/blog/2025/09/18/microsoft-365-copilot-enabling-human-agent-teams/)
- [Memex - Wikipedia](https://en.wikipedia.org/wiki/Memex)
- [Vannevar Bush and the Memex](https://cyberartsweb.org/cpace/ht/jhup/memex.html)
- [From Memex to Hypertext (PDF)](http://sonify.psych.gatech.edu/~ben/references/bush_memex_revisited.pdf)

---

**Filed:** 2025-12-22
**Author:** Claude (with Kent's vision)
**Status:** Ready for implementation prioritization
