# Chat Features Roadmap

> *"From simple conversation to self-justifying dialogue architecture"*

**Status:** Feature Roadmap
**Date:** 2025-12-25
**Spec:** spec/protocols/chat-unified.md

---

## Overview

This roadmap describes the evolution from a simple chat experience to the ambitious features enabled by the unified Chat Protocol architecture (FlowPolynomial + ValueAgent + PolicyTrace + K-Block + Evidence).

---

## Tier 0: Foundation (Current)

**What Exists Today:**

- [x] Basic chat with LLM (ChatSession)
- [x] Turn-based conversation (turns array)
- [x] K-Block branching (fork/merge/rewind)
- [x] Bayesian evidence (ChatEvidence with BetaPrior)
- [x] Context compression (WorkingContext)
- [x] Tool transparency (three modes)
- [x] Frontend ChatPanel with streaming

**What's Missing:**

- [ ] FlowPolynomial state machine
- [ ] Constitutional reward (ValueAgent)
- [ ] PolicyTrace (Witness Walk)
- [ ] Connection to F-gent infrastructure

---

## Tier 1: Simple Chat Experience (Q1 2025)

### 1.1 Core Chat

**Goal:** A delightful, simple chat that "just works."

| Feature | Description | Effort |
|---------|-------------|--------|
| **Smart context** | Auto-compress when context high, preserve important turns | S |
| **@mentions** | `@file:`, `@symbol:`, `@spec:` context injection | M |
| **Branch tree** | Visual branch navigation (D3.js tree) | M |
| **Context indicator** | Real-time token/cost display | S |
| **Keyboard shortcuts** | Ctrl+K rewind, Ctrl+Enter send, etc. | S |

### 1.2 Evidence & Confidence

**Goal:** User sees confidence in responses.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Confidence badge** | 🟢/🟡/🔴 per response | S |
| **Tool panel** | Collapsible action log per turn | S |
| **Stopping suggestion** | "Goal achieved?" when confidence high | S |
| **Evidence history** | Trend of confidence over session | M |

### 1.3 Safety & Transparency

**Goal:** Ethical mutations, transparent tools.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Mutation acknowledgment** | Click/keyboard/timeout for all writes | S |
| **Destructive approval** | Modal gate for destructive ops | S |
| **Tool manifest** | Sidebar showing available tools | S |
| **Audit trail** | Reviewable log of all actions | M |

---

## Tier 2: Enhanced Chat (Q2 2025)

### 2.1 Constitutional Visualization

**Goal:** See how the system evaluates itself.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Constitutional radar** | 7-point radar chart per turn | M |
| **Principle trend** | How each principle evolves over session | M |
| **Reward explanation** | "This scored low on Ethical because..." | L |
| **Personality attractor** | Visual basin for K-gent personality | L |

### 2.2 Advanced Branching

**Goal:** Tree-of-thought exploration in chat.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Auto-fork on uncertainty** | Fork when confidence drops | M |
| **Branch diff** | Side-by-side comparison of branches | M |
| **Merge conflict UI** | Resolve conflicting turns | L |
| **Ghost branches** | Ephemeral exploration (auto-prune) | M |

### 2.3 Context Intelligence

**Goal:** Smart context management.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Galois compression** | Semantic-preserving compression | L |
| **Priority tags** | REQUIRED/PRESERVED/DROPPABLE UI | S |
| **Context pressure** | Visual warning at 80% utilization | S |
| **Memory injection** | Auto-inject relevant past crystals | L |

---

## Tier 3: Research Flow Integration (Q3 2025)

### 3.1 Hypothesis Exploration

**Goal:** Chat spawns research subflows.

| Feature | Description | Effort |
|---------|-------------|--------|
| **"Explore this"** | Branch into tree-of-thought | M |
| **Hypothesis tree** | Visual hypothesis DAG | L |
| **Prune/expand** | Manage hypothesis branches | M |
| **Synthesize back** | Merge research into main chat | L |

### 3.2 Evidence-Driven Research

**Goal:** Research grounded in evidence.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Hypothesis scoring** | BetaPrior per hypothesis | M |
| **ASHC integration** | Chaos testing for spec changes | L |
| **Causal graphs** | Visualize evidence relationships | L |
| **Confidence convergence** | Stop when hypothesis proven | M |

### 3.3 Cross-Session Context

**Goal:** Research persists across sessions.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Research projects** | Group related sessions | M |
| **Hypothesis inheritance** | New sessions inherit conclusions | L |
| **Crystal references** | @crystal mentions for past findings | M |
| **Knowledge graph** | Zero Seed nodes from research | XL |

---

## Tier 4: Collaboration Flow Integration (Q4 2025)

### 4.1 Multi-Agent Chat

**Goal:** Chat with multiple agents.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Agent roster** | List of participating agents | M |
| **Role assignment** | Architect, Critic, Synthesizer | M |
| **Turn order** | Who speaks when | M |
| **Agent personas** | Distinct personalities per agent | L |

### 4.2 Blackboard Pattern

**Goal:** Shared state for collaboration.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Blackboard view** | Shared knowledge board | L |
| **Contribution types** | Idea, critique, question, evidence | M |
| **Voting mechanism** | Consensus on proposals | M |
| **Access control** | Per-agent read/write permissions | L |

### 4.3 Consensus Building

**Goal:** Decisions through dialogue.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Proposal lifecycle** | Draft → Discuss → Vote → Accept | L |
| **Conflict detection** | Highlight disagreements | M |
| **Resolution protocol** | Structured conflict resolution | L |
| **Decision witness** | Mark capturing final decision | M |

---

## Tier 5: Meta-DP & Self-Improvement (2026)

### 5.1 Learning from PolicyTrace

**Goal:** Chat improves from its own history.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Trace compression** | Compress PolicyTrace to patterns | XL |
| **Policy extraction** | Learn decision rules from traces | XL |
| **Self-evaluation** | Score past decisions retrospectively | L |
| **Feedback loop** | TextGRAD-style improvement | XL |

### 5.2 Constitutional Optimization

**Goal:** Tune Constitutional weights.

| Feature | Description | Effort |
|---------|-------------|--------|
| **User satisfaction correlation** | Link rewards to outcomes | L |
| **Weight adjustment** | Tune principle weights | XL |
| **A/B testing** | Compare reward configurations | L |
| **Calibration** | Align scores with user preferences | XL |

### 5.3 Self-Referential Specs

**Goal:** Specs that edit themselves.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Spec versioning** | Track spec evolution | M |
| **Fixed-point tests** | Ensure self-edits preserve semantics | L |
| **Behavioral drift** | Detect semantic divergence | XL |
| **Autonomous improvement** | Specs propose own improvements | XL |

---

## Tier 6: Zero Seed Integration (2026+)

### 6.1 Knowledge Extraction

**Goal:** Auto-extract knowledge from chat.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Goal extraction** | Mine L3 nodes from messages | L |
| **Spec extraction** | Mine L4 nodes from responses | L |
| **Reflection extraction** | Mine L6 nodes from meta-commentary | L |
| **Linking** | Connect extracted nodes | XL |

### 6.2 Crystallization

**Goal:** Every session becomes queryable.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Auto-crystallize** | On inactivity, overflow, or goal achieved | M |
| **Crystal search** | Semantic search over past sessions | L |
| **Crystal composition** | Merge related crystals | XL |
| **Crystal hierarchy** | Session → Day → Week → Epoch | L |

### 6.3 Knowledge Graph

**Goal:** Chat builds knowledge.

| Feature | Description | Effort |
|---------|-------------|--------|
| **Node creation** | Chat creates Zero Seed nodes | L |
| **Edge creation** | Chat creates relationships | L |
| **Graph navigation** | Browse knowledge from chat | L |
| **Graph-guided response** | Use graph for context | XL |

---

## Feature Matrix

### By Effort

| Effort | Count | Features |
|--------|-------|----------|
| S (Small) | 12 | Context indicator, Keyboard shortcuts, ... |
| M (Medium) | 22 | @mentions, Branch tree, Agent roster, ... |
| L (Large) | 18 | Galois compression, Hypothesis tree, ... |
| XL (X-Large) | 10 | Knowledge graph, Self-improvement, ... |

### By Dependency

```
Tier 0 (Foundation)
    ↓
Tier 1 (Simple Chat)     ← First user-facing release
    ↓
Tier 2 (Enhanced)        ← Constitutional + Advanced branching
    ↓
Tier 3 (Research)        ← FlowPolynomial composition
    ↓
Tier 4 (Collaboration)   ← Multi-agent integration
    ↓
Tier 5 (Meta-DP)         ← Self-improvement
    ↓
Tier 6 (Zero Seed)       ← Knowledge synthesis
```

---

## Success Metrics

### Tier 1 (Simple Chat)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Turn latency P95 | <2s | `kg metrics chat.turn_latency_p95` |
| User satisfaction | >4.0/5.0 | Survey |
| Session completion | >80% | Sessions with crystallization |
| Branch usage | >20% | Sessions with at least one fork |

### Tier 2 (Enhanced)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Constitutional score avg | >0.75 | Mean weighted score |
| Galois loss | <0.15 | Semantic loss on compression |
| Merge success | >90% | Merges without conflict |

### Tier 3+ (Advanced)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Research synthesis quality | >4.0/5.0 | User rating |
| Collaboration consensus time | <5 rounds | Rounds to accept |
| Self-improvement gain | >10% | Constitutional score improvement |
| Knowledge extraction accuracy | >80% | Verified node correctness |

---

## Risk Assessment

### High Risk

| Risk | Feature | Mitigation |
|------|---------|------------|
| Latency from Constitutional reward | Tier 2 | Async scoring, caching |
| Complexity of multi-agent | Tier 4 | Start with 2 agents |
| Self-improvement divergence | Tier 5 | Fixed-point tests, drift limits |

### Medium Risk

| Risk | Feature | Mitigation |
|------|---------|------------|
| Branch tree complexity | Tier 1 | Max 3 branches |
| Galois compression accuracy | Tier 2 | Fallback to sliding |
| Research synthesis quality | Tier 3 | Human-in-loop for synthesis |

### Low Risk

| Risk | Feature | Mitigation |
|------|---------|------------|
| Context indicator accuracy | Tier 1 | Token counting is deterministic |
| Tool transparency UX | Tier 1 | User studies for modes |
| Crystallization timing | Tier 6 | Configurable delays |

---

## Conclusion

The Chat Protocol evolution proceeds from a simple, delightful chat experience (Tier 1) through enhanced features (Tier 2) to research/collaboration integration (Tiers 3-4) and finally to self-improving, knowledge-synthesizing dialogue (Tiers 5-6).

Each tier builds on the previous, with the unified architecture (FlowPolynomial + ValueAgent + PolicyTrace) providing the foundation for increasingly sophisticated capabilities.

---

*"The best conversation is the one where both participants become someone new."*

*Last updated: 2025-12-25*
