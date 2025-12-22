# Context Perception V2: The Cognitive Canvas

**Status:** Brainstorming
**Date:** 2025-12-22
**Author:** Kent + Claude (Dialectic)
**Derives From:** `spec/protocols/context-perception.md`, implementation analysis

---

## Epigraph

> *"The outline was training wheels. Now we need the bicycle."*
>
> *"What if context wasn't managed—but cultivated?"*

---

## 1. The Diagnosis: Where V1 Falls Short

### 1.1 The Architecture is Correct

The four-layer stack is well-designed:
```
Layer 4: CONTEXT PERCEPTION (visualization)
Layer 3: PORTAL TOKENS (expandable meaning)
Layer 2: EXPLORATION HARNESS (safety + evidence)
Layer 1: TYPED-HYPERGRAPH (nodes + edges)
```

Each layer is independently valuable. 81 tests on hypergraph, 125 on portal tokens, 110 on exploration harness. The *bones* are solid.

### 1.2 The Vision is Unrealized

But the spec describes a **cognitive canvas**—two intelligences editing an outline together—and what we have is a **file browser with collapsible sections**.

| Spec Promise | Current Reality |
|--------------|-----------------|
| "Two intelligences editing together" | Human clicks; agent watches |
| "Copy-paste includes provenance" | Backend metadata; no clipboard integration |
| "Semi-transparent UI appears/fades" | Static React components |
| "Trail IS evidence" | Trail exists; evidence connection weak |
| "Annotation is coordination" | Annotations are notes; no agent orchestration |

### 1.3 The Missing Transformation

**The spec describes WHAT. It doesn't describe WHY.**

The "why" is transformative:
- What if navigation **was** investigation?
- What if the outline **was** the agent's working memory?
- What if copy-paste **created proofs**?
- What if collaboration **was** dialectic?

---

## 2. The Radical Vision: From Canvas to Cognition

### 2.1 Core Thesis

> **Context Perception should be an *exocortex*—a shared cognitive space where human and agent think together.**

Not a document viewer. Not a file browser. A **thinking space**.

The outline isn't a representation of files. It's a representation of **attention**—what's currently being considered, by whom, why.

### 2.2 The Three Transformations

| Current | Transformation | Radical |
|---------|----------------|---------|
| **Outline** (document) | → | **Attention Graph** (cognition) |
| **Portals** (expand/collapse) | → | **Reasoning Nodes** (claim + evidence) |
| **Trail** (history) | → | **Proof Tree** (verifiable reasoning) |

---

## 3. Transformation 1: Attention Graph

### 3.1 The Insight

The outline models files. But what actually matters is **attention**.

When a human expands a portal, they're saying: "I'm looking at this now." When an agent adds an annotation, it's saying: "This is relevant to our goal."

The underlying model should be an **attention graph**, not a document tree.

### 3.2 Attention as First-Class Primitive

```python
@dataclass
class Attention:
    """
    Where focus is directed.

    Unlike files (static), attention is dynamic:
    - It has intensity (how focused)
    - It has recency (how fresh)
    - It has attribution (who's attending)
    """

    target: str  # AGENTESE path
    intensity: float  # 0.0 (peripheral) to 1.0 (focal)
    recency: datetime  # When last attended
    observer: str  # Who is attending
    reason: str | None  # Why attending

    def decay(self, now: datetime) -> "Attention":
        """Attention decays over time."""
        age = (now - self.recency).total_seconds()
        decay_rate = 0.1  # 10% per minute
        new_intensity = self.intensity * (1 - decay_rate * age / 60)
        return Attention(
            target=self.target,
            intensity=max(0.01, new_intensity),
            recency=self.recency,
            observer=self.observer,
            reason=self.reason,
        )
```

### 3.3 The Attention Graph

```python
@dataclass
class AttentionGraph:
    """
    The shared cognitive space.

    Multiple observers (human + agents) project attention onto paths.
    The graph shows where everyone is looking and why.
    """

    attentions: dict[str, list[Attention]]  # path → who's attending

    def focal_points(self) -> list[str]:
        """Paths with highest cumulative attention."""

    def contested(self) -> list[str]:
        """Paths where observers disagree."""

    def forgotten(self) -> list[str]:
        """Paths attended but now decayed."""

    def visualize(self) -> OutlineNode:
        """Project attention into outline structure."""
```

### 3.4 Impact: Outline Becomes Emergent

The outline isn't authored—it **emerges** from attention.

What you see depends on what's being attended:
- Highly-attended paths are expanded
- Decayed attention collapses
- Contested paths show disagreement markers

The human doesn't manage the outline. The outline **reflects cognition**.

---

## 4. Transformation 2: Reasoning Nodes

### 4.1 The Insight

Portals are expand/collapse. But expansion **isn't neutral**—it's a reasoning step.

When you expand `[tests]`, you're implicitly claiming: "Test coverage is relevant to my current goal." That's a **micro-claim**.

### 4.2 Every Expansion is an Epistemic Act

```python
@dataclass
class ReasoningNode:
    """
    A portal with epistemic content.

    Every expansion creates:
    - An implicit claim ("this is relevant")
    - Evidence from content
    - A proof obligation
    """

    portal: PortalToken

    # Epistemic layer
    implicit_claim: str  # What expanding claims
    evidence_gathered: list[Evidence]  # What we found
    proof_status: ProofStatus  # open, partial, complete, refuted

    # Reasoning chain
    parent_reasoning: "ReasoningNode | None"  # What led here
    child_reasoning: list["ReasoningNode"]  # What follows
```

### 4.3 The Reasoning Tree

When you navigate:
1. **Focus** → "I'm investigating X"
2. **Expand tests** → "Test coverage matters for X"
3. **Expand covers** → "This function is tested"
4. **Find bug** → "The bug is in this function" (claim)

Each step is a node in a **reasoning tree**. The trail isn't just history—it's a **proof skeleton**.

### 4.4 Impact: Investigation Becomes Provable

```
Current: "I looked at auth_middleware.py and found the bug."
V2: "Claim: Bug is in validate_token. Evidence: trail[4] shows coverage gap."
```

The agent can say: "My claim is supported by these 7 reasoning nodes with combined evidence strength STRONG."

---

## 5. Transformation 3: Proof Tree

### 5.1 The Insight

ASHC (Agentic Self-Hosting Compiler) already requires proof obligations. The exploration harness already computes evidence strength.

But they're disconnected. What if the **trail WAS the proof**?

### 5.2 Trail as Proof Tree

```python
@dataclass
class ProofTree:
    """
    The navigation trail, reinterpreted as proof structure.

    Each step is a lemma. The conclusion is derived from lemmas.
    The tree can be verified: Do the lemmas actually support the claim?
    """

    claim: Claim
    lemmas: list[TrailStep]  # Each step is evidence
    subproofs: list["ProofTree"]  # Nested proofs

    def verify(self) -> VerificationResult:
        """Check if lemmas support claim."""

    def generate_witness(self) -> Witness:
        """Create cryptographic witness (witness.py)."""

    def export_lean(self) -> str:
        """Export as Lean4 proof sketch."""
```

### 5.3 Collaborative Proof Construction

Human and agent **co-construct proofs**:

```
Human: "There's a bug in auth."
Agent: "Claim: Bug in auth. Let me gather evidence."
       → Expands [tests] (lemma: tests exist)
       → Expands [covers] (lemma: function covered)
       → Finds gap (evidence: line 87 not covered)
Agent: "Claim supported with MODERATE strength. Want me to commit?"
Human: "Yes, commit."
Agent: → creates Witness mark with proof tree attached
```

### 5.4 Impact: Decisions Become Verifiable

Every decision in the system has a **proof tree**. Auditors can replay:
1. What was the claim?
2. What evidence was gathered?
3. Does the evidence support the claim?

This is **radical accountability** for AI reasoning.

---

## 6. Integration: The Cognitive Canvas

### 6.1 The Unified Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           COGNITIVE CANVAS                                   │
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ ATTENTION GRAPH                                                        │ │
│   │   ○ auth_middleware (Kent: 1.0, Claude: 0.8)  ← Both focused here     │ │
│   │   ○ validate_token (Kent: 0.3, Claude: 1.0)   ← Claude more focused   │ │
│   │   ○ jwt_utils (Kent: 0.1)                     ← Peripheral            │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                              │                                              │
│                              ▼                                              │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ REASONING NODES                                                        │ │
│   │   □ Claim: "Bug in expiry check"                                      │ │
│   │   ├─ □ Lemma: tests exist (evidence: 3 files) ✓                       │ │
│   │   ├─ □ Lemma: function covered (evidence: coverage report) ✓          │ │
│   │   └─ □ Lemma: off-by-one (evidence: line 87 uses < not <=) ✓          │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                              │                                              │
│                              ▼                                              │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │ PROOF TREE                                                             │ │
│   │   Claim: "validate_token has off-by-one in expiry"                    │ │
│   │   Evidence: 3 lemmas, strength: STRONG                                │ │
│   │   Status: COMPLETE (ready for witness)                                │ │
│   │   [Commit] [Export Lean] [Share Trail]                                │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 The Experience

**For Humans:**
- Navigate normally (the canvas feels like a document)
- See where the agent is focused (presence indicators)
- See what the agent is claiming (reasoning nodes)
- Verify/reject claims (proof tree)

**For Agents:**
- Navigate to gather evidence
- Form claims from evidence
- Request human verification
- Commit verified claims as witnesses

**Together:**
- Co-construct understanding
- Debate through annotations
- Fuse perspectives into verified claims

---

## 7. Concrete Next Steps

### 7.1 Phase 1: Attention Primitives (~2 sessions)

Add attention tracking to existing outline:

```python
# In outline.py
@dataclass
class AttentiveOutline(Outline):
    attentions: dict[str, list[Attention]]

    def attend(self, path: str, observer: str, reason: str | None = None):
        """Direct attention to a path."""

    def decay_all(self, now: datetime):
        """Decay all attentions."""
```

**Exit criterion:** Expanding a portal creates an attention record. Attention decays over time.

### 7.2 Phase 2: Reasoning Nodes (~3 sessions)

Wrap portals in epistemic containers:

```python
# In portal_bridge.py
@dataclass
class ReasoningPortal(PortalToken):
    implicit_claim: str
    evidence: list[Evidence]
    proof_status: ProofStatus
```

**Exit criterion:** Each portal expansion generates an implicit claim. Claims can be marked open/partial/complete.

### 7.3 Phase 3: Proof Tree (~3 sessions)

Connect trail to ASHC:

```python
# In exploration/proof_tree.py
@dataclass
class ProofTree:
    claim: Claim
    lemmas: list[TrailStep]

    def verify(self) -> VerificationResult: ...
    def to_witness(self) -> Mark: ...
```

**Exit criterion:** `kg explore commit "claim"` creates a witness mark with proof tree attached.

### 7.4 Phase 4: UI Integration (~2 sessions)

Update frontend to show:
- Attention heatmap (who's focused where)
- Reasoning status (claim → evidence → proof)
- Proof tree panel

**Exit criterion:** Portal.tsx shows attention intensity. TrailPanel shows proof status.

---

## 8. Why This Matters

### 8.1 For Kent

This makes kgents **accountable**. Every decision has a proof. Every claim has evidence. The system can explain *why* it did what it did.

### 8.2 For Users

This makes AI **trustworthy**. Not "trust me, I'm an AI," but "here's my reasoning, verify it yourself."

### 8.3 For the Field

This advances **verifiable AI**. Most systems are black boxes. This system generates proofs.

---

## 9. Open Questions

1. **Attention decay rate:** What's the right half-life for attention? Too fast = forgetting; too slow = clutter.

2. **Implicit claim extraction:** How do we derive "this is relevant" from an expansion? LLM inference? Heuristics?

3. **Proof verification:** How formal should proofs be? Natural language? Structured logic? Lean4?

4. **UX for reasoning:** How do we show proof trees without overwhelming users?

5. **Multi-agent attention:** When agents disagree, how is contested attention visualized?

---

## 10. Relationship to Constitution

| Principle | How This Embodies It |
|-----------|----------------------|
| **Tasteful** | One system (cognitive canvas) replaces scattered components |
| **Composable** | Attention, reasoning, proof are separate layers that compose |
| **Ethical** | Human verifies agent claims; no hidden reasoning |
| **Generative** | Proofs generate from navigation; implementation follows spec |
| **Heterarchical** | Human and agent are symmetric—both attend, both reason |

---

## 11. Voice Anchor Check

*Before finalizing:*

- ❓ *Did I smooth anything that should stay rough?*
  - The "off-by-one bug" example is intentionally simple. Real reasoning is messier.

- ❓ *Did I add words Kent wouldn't use?*
  - "Exocortex" is jargon but feels daring/bold.

- ❓ *Did I lose any opinionated stances?*
  - "Proofs, not promises" is the core stance. Preserved.

- ❓ *Is this still daring, bold, creative—or did I make it safe?*
  - Claiming that navigation creates proofs is daring.
  - Claiming that AI reasoning should be verifiable is bold.
  - Kept it rough.

---

*"The outline was training wheels. The cognitive canvas is the bicycle. Now we ride."*

---

**Filed:** 2025-12-22
**Voice anchor:** *"Daring, bold, creative, opinionated but not gaudy"*
