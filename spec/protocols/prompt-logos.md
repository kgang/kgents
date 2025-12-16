# Prompt Logos: The Universal Prompt Substrate

> *"The prompt that prompts prompts is not a prompt—it is a category."*

**Status:** Specification v0.2 (Critically Revised)
**Date:** 2025-12-16 (Revised: 2025-12-16)
**Author:** Kent + Claude (Deep Creative Exploration → Disciplined Refinement)
**Prerequisites:** `evergreen-prompt-system.md`, `agentese.md`, `projection.md`, `heritage.md`
**Guard:** `[phase=PLAN][entropy=0.08][vision=true][rigidity=0.6]`
**Revision History:** v0.1 (Vision) → v0.2 (Critical Analysis + Principle Alignment)

---

## Critical Analysis Summary (Added v0.2)

### Strengths of Original Vision
1. **Categorical Foundation**: The PromptM monad, operad, and sheaf structure aligns with AD-006 (Unified Categorical Foundation)
2. **Self-Improvement Loop**: TextGRAD + rigidity spectrum enables controlled evolution
3. **AGENTESE Integration**: `prompt.*` context is a natural extension

### Weaknesses Identified

| Weakness | Severity | Principle Violated | Resolution |
|----------|----------|-------------------|------------|
| **Context Proliferation** | HIGH | Tasteful (no 6th context) | Use `concept.prompt.*` not `prompt.*` |
| **Scope Creep** | HIGH | Curated | Distinguish v1.0 (core) from future |
| **Missing Differentiation** | MEDIUM | Composable | How is this not just Evergreen++? |
| **Rigidity Without Mechanism** | MEDIUM | Ethical | Who decides rigidity values? |
| **Meta-Prompt Halting Problem** | MEDIUM | Ethical | Self-referential improvement limits? |
| **Observer Dependency Unclear** | LOW | AGENTESE Meta-Principle | Prompts are not entities—observer semantics TBD |

### Key Revisions in v0.2

1. **CONTEXT CHANGE**: `prompt.*` → `concept.prompt.*` (respects 5-context limit)
2. **PHASE SCOPING**: Explicit MVP vs. future phases
3. **DIFFERENTIATION**: Clear value prop vs. existing Evergreen system
4. **GOVERNANCE**: Rigidity determination protocol added
5. **HALTING SAFEGUARDS**: Meta-prompt recursion limits specified

---

## Part 0: Architectural Resolution (Added v0.2)

### 0.1 The Context Debate: `prompt.*` vs `concept.prompt.*`

**The Problem**: The original spec proposed a sixth AGENTESE context (`prompt.*`). This violates the spec/principles.md §AGENTESE which explicitly states:

> "To prevent 'kitchen-sink' anti-patterns (Principle #1: Tasteful), we define exactly **five contexts**. No others are permitted without a spec change."

**Resolution Options**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **A. New `prompt.*` context** | Clean namespace | Violates 5-context limit | ❌ Rejected |
| **B. `concept.prompt.*`** | Prompts ARE concepts (abstract structures) | Namespace depth | ✅ **Selected** |
| **C. `self.prompt.*`** | Prompts are internal to agent | Conflates with agent-specific | ❌ Rejected |

**Rationale for `concept.prompt.*`**:

1. **Prompts are abstract structures** — They exist independently of any particular agent or session
2. **Concepts are generative** — `concept.*` aligns with the Generative principle
3. **Precedent** — Evergreen already uses `concept.prompt.manifest` for prompt access
4. **Tasteful** — We earn the namespace, we don't proliferate contexts

### 0.2 Differentiation from Evergreen

**Critical Question**: *What does Prompt Logos provide that Evergreen doesn't?*

| Capability | Evergreen | Prompt Logos |
|-----------|-----------|--------------|
| System prompt compilation | ✅ Yes (CLAUDE.md) | ✅ Yes (any prompt) |
| Section composition | ✅ Yes | ✅ Yes |
| Rollback/versioning | ✅ Yes | ✅ Yes |
| Self-improvement (TextGRAD) | ⚠️ Partial | ✅ Full |
| **Agent prompts** | ❌ No | ✅ Yes |
| **Task templates** | ❌ No | ✅ Yes |
| **Persona management** | ❌ No | ✅ Yes |
| **Meta-prompts** | ❌ No | ✅ Yes |
| **Cross-prompt inheritance** | ❌ No | ✅ Yes |
| **Prompt registry/search** | ❌ No | ✅ Yes |

**The Core Value Proposition**:

> **Evergreen cultivates ONE garden (CLAUDE.md). Prompt Logos cultivates a FOREST of prompts with the same categorical guarantees.**

### 0.3 Implementation Phases (Tasteful Scoping)

**Phase 1 (MVP)**: Prompt Registry + Basic Types
- Prompt registry with semantic search
- Three types: system, agent, task
- Basic inheritance (parent → child)
- CLI: `kg concept.prompt.list`, `kg concept.prompt.search`

**Phase 2**: Self-Improvement
- TextGRAD universalized for all prompt types
- Rigidity governance protocol
- Feedback loop integration

**Phase 3**: Meta-Prompts
- Self-referential prompt improvement
- Halting safeguards
- Prompt generation from descriptions

**Phase 4**: Advanced Composition
- Cross-prompt branching/merging
- Observer-dependent prompt variants
- Full operad composition

---

## Part 0-B: Governance & Safeguards (Added v0.2)

### 0-B.1 Rigidity Determination Protocol

**The Problem**: Who decides that `principles.md` has rigidity 0.9 while `task.code-review` has 0.3?

**Resolution**: Rigidity is **earned through provenance**, not declared:

```python
def determine_rigidity(prompt: PromptCatalogEntry) -> float:
    """
    Rigidity is computed, not declared.

    Factors:
    1. Provenance age: Older prompts resist change more
    2. Forger authority: Core team prompts are more rigid
    3. Usage stability: High success rate → more rigid
    4. Explicit override: Human can lock/unlock
    """
    base = 0.5  # Default middle ground

    # Age factor (0-0.2)
    age_days = (now() - prompt.forged_at).days
    age_factor = min(0.2, age_days / 365 * 0.2)

    # Authority factor (0-0.2)
    if prompt.forged_by in CORE_TEAM:
        authority_factor = 0.2
    elif prompt.forged_by.startswith("system"):
        authority_factor = 0.15
    else:
        authority_factor = 0.0

    # Stability factor (0-0.1)
    if prompt.usage_count > 100:
        stability_factor = min(0.1, prompt.success_rate * 0.1)
    else:
        stability_factor = 0.0

    # Explicit lock
    if prompt.locked:
        return 1.0

    return min(1.0, base + age_factor + authority_factor + stability_factor)
```

### 0-B.2 Meta-Prompt Halting Safeguards

**The Problem**: Meta-prompts can improve themselves. What prevents infinite recursion?

**Safeguards**:

1. **Recursion Depth Limit**: Meta-prompts track improvement depth
   ```python
   MAX_META_RECURSION = 3  # Cannot improve more than 3 levels deep
   ```

2. **Improvement Cooldown**: Same prompt cannot be improved twice within cooldown
   ```python
   IMPROVEMENT_COOLDOWN = timedelta(hours=1)
   ```

3. **Convergence Detection**: If improvement produces <5% change, halt
   ```python
   if similarity(old, new) > 0.95:
       return old  # Converged
   ```

4. **Human-in-the-Loop for Meta-Meta**: Improving `prompt.meta.improve` itself requires human approval

---

## Part 0-C: Alternative Approaches Considered (Added v0.2)

### 0-C.1 Industry Landscape

Research on prompt management approaches in 2024-2025 reveals several patterns:

| Approach | Example Systems | Key Insight | kgents Integration |
|----------|----------------|-------------|-------------------|
| **Prompt as Program** | DSPy, Guidance | Typed signatures, compilation | PromptM monad already captures this |
| **Prompt Versioning** | LangSmith, PromptLayer | Track changes like git | Rollback registry provides this |
| **Prompt Optimization** | OPRO, APE, PromptBreeder | Evolutionary/gradient-based | TextGRAD implements this |
| **Constraint-based** | LMQL, Outlines | Grammar constraints | G-gent provides this |
| **Prompt Chaining** | LangChain, Semantic Kernel | Sequential composition | Agent composition handles this |

**Insight**: Prompt Logos synthesizes these approaches under categorical unification.

### 0-C.2 What Others Don't Have

1. **Categorical Guarantees**: No other system provides monadic laws for prompt transformation
2. **Observer-Dependent Projection**: Prompts that render differently based on who's asking
3. **Self-Similar Architecture**: Same structure (Poly + Operad + Sheaf) at all levels
4. **Entropy Budget**: Accursed Share integration for creative exploration

### 0-C.3 Risks of the Approach

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Over-engineering** | HIGH | Complexity barrier | Phase-gated rollout, MVP first |
| **Self-improvement instability** | MEDIUM | Prompt drift | Rigidity + human approval tiers |
| **Registry sprawl** | MEDIUM | Discovery difficulty | Semantic search + curation policy |
| **Observer semantics unclear** | LOW | API awkwardness | Defer observer-dependent prompts to Phase 4 |

---

## Epigraph

> *"The Evergreen Prompt System cultivates CLAUDE.md. But CLAUDE.md is one prompt among many. What if the substrate that cultivates prompts could cultivate ALL prompts? What if prompt management were not a feature but a fundamental protocol?"*
>
> *"This is Prompt Logos—the category in which all prompts are morphisms."*

---

## Part I: The Radical Vision

### 1.1 From Evergreen to Universal

The Evergreen Prompt System represents a breakthrough: prompts that read themselves, write themselves, validate themselves, and evolve through categorical guarantees. But it is scoped to a single artifact: `CLAUDE.md`.

**The Insight**: The same principles that make CLAUDE.md self-cultivating can make ANY prompt self-cultivating.

Consider the prompts that exist in any AI-augmented development workflow:

| Prompt Type | Current State | With Prompt Logos |
|-------------|---------------|-------------------|
| System prompts (`CLAUDE.md`) | Evergreen | Self-cultivating |
| Project-specific prompts | Static files | Self-cultivating |
| Agent prompts | Hardcoded strings | Self-cultivating |
| User personas/archetypes | Manual maintenance | Self-cultivating |
| Task templates | Copy-paste | Self-cultivating |
| Slash command prompts | Static `.md` files | Self-cultivating |
| MCP server prompts | Scattered across configs | Self-cultivating |
| Memory/context prompts | Ad-hoc | Self-cultivating |
| Meta-prompts (prompts for prompts) | Rare | First-class citizens |

**Prompt Logos** is the generalization: a **universal prompt substrate** where prompts are first-class objects with categorical structure, self-improvement capability, and seamless composition.

### 1.2 The Core Claim

> **Prompts are morphisms in a category. Prompt management is functorial.**

This is not metaphor. It is the mathematical foundation that enables:

1. **Composition**: Prompts compose lawfully (`f >> g >> h`)
2. **Transformation**: Prompts transform via functors (TextGRAD, style transfer, compression)
3. **Persistence**: Prompts version-control themselves (rollback, branching, merging)
4. **Evolution**: Prompts improve through feedback loops (monadic self-improvement)
5. **Projection**: The same prompt manifests differently to different observers

### 1.3 The Name: Prompt Logos

**Logos** (λόγος): Word, reason, principle, the underlying order of things.

In AGENTESE, the `Logos` is the resolver that maps paths to interactions. In Prompt Logos, the same concept applies: **the Logos resolves prompt paths to prompt instances**.

```python
# AGENTESE path resolution
await logos.invoke("world.house.manifest", observer)  # → House view

# Prompt Logos path resolution
await prompt_logos.invoke("prompt.system.manifest", observer)  # → System prompt
await prompt_logos.invoke("prompt.agent.scout.manifest", observer)  # → Scout agent prompt
await prompt_logos.invoke("prompt.task.code-review.manifest", observer)  # → Review template
```

The Prompt Logos IS an AGENTESE context. Prompts live in `prompt.*` alongside `world.*`, `self.*`, `concept.*`, `void.*`, and `time.*`.

---

## Part II: The Categorical Structure

### 2.1 The Prompt Category

```
Category Prompt where:
  Objects   = PromptTypes (system, agent, task, persona, meta, ...)
  Morphisms = PromptTransformations (compose, improve, compress, project, ...)
  Identity  = id_prompt : P → P (the prompt unchanged)
  Compose   = (f >> g)(p) = g(f(p)) (associative)
```

### 2.2 The Prompt Type Hierarchy

Not all prompts are equal. They form a **hierarchy of intention**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROMPT TYPE HIERARCHY                                │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                        META PROMPTS                                    │ │
│  │   • Prompts that generate prompts                                      │ │
│  │   • prompt.meta.improve, prompt.meta.generate, prompt.meta.analyze     │ │
│  │   • Self-referential: can improve themselves                           │ │
│  └─────────────────────────────────────────────────────────────────────┬──┘ │
│                                                                        │    │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                       SYSTEM PROMPTS                                   │ │
│  │   • Define agent identity and capabilities                             │ │
│  │   • prompt.system.claude, prompt.system.builder, prompt.system.scout   │ │
│  │   • High rigidity (0.7-1.0) — core identity should not drift          │ │
│  └─────────────────────────────────────────────────────────────────────┬──┘ │
│                                                                        │    │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                       AGENT PROMPTS                                    │ │
│  │   • Configure specific agent behaviors                                 │ │
│  │   • prompt.agent.kgent, prompt.agent.scout, prompt.agent.reviewer      │ │
│  │   • Medium rigidity (0.4-0.7) — behavior can evolve                   │ │
│  └─────────────────────────────────────────────────────────────────────┬──┘ │
│                                                                        │    │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                       TASK PROMPTS                                     │ │
│  │   • Templates for specific activities                                  │ │
│  │   • prompt.task.review, prompt.task.test, prompt.task.refactor         │ │
│  │   • Low-medium rigidity (0.2-0.5) — highly adaptable                  │ │
│  └─────────────────────────────────────────────────────────────────────┬──┘ │
│                                                                        │    │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      PERSONA PROMPTS                                   │ │
│  │   • Observer archetypes and user profiles                              │ │
│  │   • prompt.persona.developer, prompt.persona.architect                 │ │
│  │   • Variable rigidity based on persona stability                       │ │
│  └─────────────────────────────────────────────────────────────────────┬──┘ │
│                                                                        │    │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      CONTEXT PROMPTS                                   │ │
│  │   • Session-specific, ephemeral context injection                      │ │
│  │   • prompt.context.session, prompt.context.memory, prompt.context.focus│ │
│  │   • Lowest rigidity (0.0-0.2) — fully adaptive                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 The PromptM Monad (Generalized)

The Evergreen System introduced `PromptM` for CLAUDE.md. Prompt Logos generalizes it:

```python
@dataclass(frozen=True)
class PromptM(Generic[A]):
    """
    The Universal Prompt Monad.

    A self-improving prompt computation with categorical guarantees.
    Works for ANY prompt type, not just system prompts.

    Monadic Laws (must hold for all prompt types):
    - Left Identity:  unit(p) >>= f ≡ f(p)
    - Right Identity: m >>= unit ≡ m
    - Associativity:  (m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)
    """

    value: A                              # The prompt content
    prompt_type: PromptType               # system | agent | task | persona | context | meta
    reasoning_trace: tuple[str, ...]      # How we got here
    provenance: tuple[Source, ...]        # Where it came from
    lineage: tuple[PromptId, ...]         # Parent prompts (inheritance chain)
    checkpoint_id: str | None             # For rollback
    rigidity: float                       # 0.0 (adaptive) to 1.0 (fixed)

    @staticmethod
    def unit(content: str, prompt_type: PromptType) -> "PromptM[str]":
        """Lift content into the monad."""
        ...

    def bind(self, f: Callable[[A], "PromptM[B]"]) -> "PromptM[B]":
        """Monadic bind with trace accumulation."""
        ...

    def improve(self, feedback: str, learning_rate: float | None = None) -> "PromptM[A]":
        """Apply TextGRAD improvement (learning_rate defaults from rigidity)."""
        ...

    def fork(self, name: str) -> "PromptM[A]":
        """Create a variant branch (like git branch)."""
        ...

    def merge(self, other: "PromptM[A]", strategy: MergeStrategy) -> "PromptM[A]":
        """Merge another prompt variant (like git merge)."""
        ...
```

### 2.4 The Prompt Operad

Just as sections compose in CLAUDE.md, prompts compose in the universal system:

```python
PROMPT_OPERAD = Operad(
    operations={
        # Composition
        "sequence": Operation(arity=2, compose=sequential_compose),
        "parallel": Operation(arity=2, compose=parallel_compose),
        "conditional": Operation(arity=3, compose=conditional_compose),  # (condition, if_true, if_false)
        "inherit": Operation(arity=2, compose=inheritance_compose),      # child extends parent

        # Transformation
        "improve": Operation(arity=1, transform=textgrad_improve),
        "compress": Operation(arity=1, transform=compress_prompt),
        "expand": Operation(arity=1, transform=expand_prompt),
        "style": Operation(arity=2, transform=style_transfer),          # (prompt, style_prompt)

        # Projection
        "project": Operation(arity=2, project=project_to_target),       # (prompt, target)
    },
    laws=[
        OperadLaw.ASSOCIATIVITY,
        OperadLaw.IDENTITY,
        OperadLaw.INTERCHANGE,  # For parallel composition
    ]
)
```

### 2.5 The Prompt Sheaf

Local prompt views must cohere globally:

```python
@dataclass
class PromptSheaf:
    """
    Global coherence from local prompt views.

    The same logical prompt may have different manifestations:
    - Different observers see different affordances
    - Different contexts yield different content
    - Different targets yield different projections

    The sheaf guarantees: these views are consistent.
    """

    def section(self, path: str, observer: Umwelt) -> PromptM[str]:
        """Get prompt section for this observer."""
        ...

    def glue(self, sections: list[PromptM[str]]) -> PromptM[str]:
        """Verify sections cohere and compose."""
        ...

    def restrict(self, prompt: PromptM[str], subpath: str) -> PromptM[str]:
        """Restrict prompt to a subpath."""
        ...
```

---

## Part III: The AGENTESE Integration

### 3.1 The `concept.prompt.*` Context (Revised v0.2)

Prompt Logos extends the existing `concept.*` context—NOT adding a sixth context:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE FIVE CONTEXTS (Preserved)                         │
├─────────────┬───────────────────────────────────────┬───────────────────────┤
│ Context     │ Ontology                              │ Principle Alignment   │
├─────────────┼───────────────────────────────────────┼───────────────────────┤
│ world.*     │ The External: entities, environments  │ Heterarchical         │
│ self.*      │ The Internal: memory, capability      │ Ethical               │
│ concept.*   │ The Abstract: platonics, definitions  │ Generative            │
│    ↳ prompt.*│   Linguistic artifacts (prompts)     │   (Composable sub-domain) │
│ void.*      │ The Accursed Share: entropy           │ Meta-Principle        │
│ time.*      │ The Temporal: history, forecast       │ Heterarchical         │
└─────────────┴───────────────────────────────────────┴───────────────────────┘
```

**Why `concept.prompt.*` (Revised Rationale)**:

1. **Prompts ARE concepts** — They are abstract structures that can be instantiated, composed, and reasoned about
2. **Respects the 5-context limit** — The Tasteful principle demands we earn namespace, not proliferate
3. **Precedent** — Evergreen already uses `concept.prompt.*` paths (see spec/protocols/evergreen-prompt-system.md §9)
4. **Pragmatic force within concepts** — Concepts like `concept.justice` also have pragmatic force when invoked; prompts are not unique in this regard

### 3.2 The `concept.prompt.*` Path Registry (Revised v0.2)

```
concept.prompt.*                           # The linguistic substrate (within concept.*)
  concept.prompt.system.*                    # System prompts
    concept.prompt.system.claude.manifest      # Current CLAUDE.md
    concept.prompt.system.claude.evolve        # Propose system evolution
    concept.prompt.system.claude.history       # Version history
    concept.prompt.system.{name}.manifest      # Named system prompt

  concept.prompt.agent.*                     # Agent-specific prompts
    concept.prompt.agent.{name}.manifest       # Get agent prompt
    concept.prompt.agent.{name}.improve        # Improve agent prompt
    concept.prompt.agent.{name}.fork           # Create variant
    concept.prompt.agent.{name}.lineage        # Show inheritance chain

  concept.prompt.task.*                      # Task templates
    concept.prompt.task.{name}.manifest        # Get task template
    concept.prompt.task.{name}.instantiate     # Create from template with vars
    concept.prompt.task.{name}.variants        # List variants

  concept.prompt.persona.*                   # Observer archetypes (Phase 4)
    concept.prompt.persona.{name}.manifest     # Get persona prompt
    concept.prompt.persona.{name}.affordances  # What can this persona do?

  concept.prompt.session.*                   # Session context
    concept.prompt.session.manifest            # Current session context
    concept.prompt.session.memory.manifest     # Memory injection prompt
    concept.prompt.session.focus.manifest      # Focus-specific context

  concept.prompt.meta.*                      # Meta-prompts (Phase 3)
    concept.prompt.meta.improve.invoke         # The prompt that improves prompts
    concept.prompt.meta.generate.invoke        # The prompt that generates prompts
    concept.prompt.meta.analyze.invoke         # The prompt that analyzes prompts
    concept.prompt.meta.compose.invoke         # The prompt that composes prompts

  concept.prompt.registry.*                  # Prompt catalog (Phase 1)
    concept.prompt.registry.list               # All registered prompts
    concept.prompt.registry.search             # Semantic search
    concept.prompt.registry.validate           # Validate prompt against type
```

**Phase Annotations**: Paths marked with (Phase N) are deferred to that implementation phase.

### 3.3 Observer-Dependent Prompt Manifestation (Phase 4)

The AGENTESE principle "same handle, different perception" applies to prompts:

```python
# Different observers, different prompt views (Phase 4)
await logos.invoke("concept.prompt.task.code-review.manifest", junior_umwelt)
# → Detailed review template with checklist and examples

await logos.invoke("concept.prompt.task.code-review.manifest", senior_umwelt)
# → Concise review template trusting reviewer judgment

await logos.invoke("concept.prompt.task.code-review.manifest", architect_umwelt)
# → Architecture-focused review template emphasizing design patterns
```

**Note (v0.2)**: Observer-dependent prompt rendering is deferred to Phase 4. In Phases 1-3, prompts manifest identically to all observers. The infrastructure for this exists (Umwelt, affordances), but the semantics of "what does a junior developer perceive differently about a prompt?" need careful design.

This is not magic—it is the **affordance system** applied to prompts. Each prompt has observer-dependent facets.

---

## Part IV: The Self-Improvement Engine

### 4.1 TextGRAD Universalized

TextGRAD (textual gradients) was introduced for CLAUDE.md sections. Prompt Logos generalizes it to **all prompts**:

```python
class UniversalTextGRAD:
    """
    Apply textual gradients to any prompt type.

    The learning rate is derived from rigidity:
    - High rigidity (0.9) → Low learning rate (0.1) → Resist change
    - Low rigidity (0.1) → High learning rate (0.9) → Embrace change

    This ensures core identity prompts resist drift while task prompts adapt.
    """

    def improve(
        self,
        prompt: PromptM[str],
        feedback: str,
        learning_rate: float | None = None,
    ) -> PromptM[str]:
        """
        Apply feedback as textual gradient.

        Args:
            prompt: The prompt to improve
            feedback: Natural language feedback
            learning_rate: Override rigidity-derived rate (for experimentation)

        Returns:
            Improved prompt with reasoning trace
        """
        rate = learning_rate or (1.0 - prompt.rigidity)

        # Parse feedback into gradient direction
        gradient = self._parse_gradient(prompt, feedback)

        # Apply gradient with rate
        improved_content = self._apply_gradient(prompt.value, gradient, rate)

        return prompt.bind(lambda _: PromptM(
            value=improved_content,
            prompt_type=prompt.prompt_type,
            reasoning_trace=(f"TextGRAD: {feedback} (rate={rate:.2f})",),
            provenance=(Source.TEXTGRAD,),
            lineage=prompt.lineage,
            checkpoint_id=None,  # Will be assigned on checkpoint
            rigidity=prompt.rigidity,
        ))
```

### 4.2 Prompt Inheritance and Evolution

Prompts can inherit from parent prompts, creating lineages:

```python
# Define a base code review prompt
base_review = PromptM.unit("""
Review this code for:
- Correctness
- Style
- Performance
""", PromptType.TASK)

# Inherit and specialize for security review
security_review = base_review.inherit("security", """
Additionally review for:
- Input validation
- Authentication
- Authorization
- Data sanitization
""")

# The lineage is tracked
security_review.lineage
# → (prompt.task.code-review, prompt.task.code-review.security)

# Improvements can propagate or stay local
base_review.improve("add maintainability review")
# → Does security_review inherit this? Depends on propagation policy.
```

### 4.3 Prompt Branching and Merging

Like git, prompts can branch and merge:

```python
# Fork a prompt variant
experimental = prompt.fork("experimental")

# Improve the variant
experimental = experimental.improve("be more concise")

# If the experiment succeeds, merge back
prompt = prompt.merge(experimental, strategy=MergeStrategy.SEMANTIC_FUSION)

# Or discard
experimental.archive("experiment failed: too concise")
```

---

## Part V: The Prompt Registry (L-gent Integration)

### 5.1 Prompts as First-Class Catalog Entries

Every prompt is registered in the L-gent catalog:

```python
@dataclass
class PromptCatalogEntry:
    """A prompt in the L-gent registry."""

    id: str                           # prompt.task.code-review
    prompt_type: PromptType           # TASK
    name: str                         # "Code Review"
    description: str                  # "Template for reviewing code changes"
    status: Status                    # ACTIVE | DRAFT | DEPRECATED
    rigidity: float                   # 0.4
    lineage: tuple[str, ...]          # Parent prompts
    variants: tuple[str, ...]         # Child variants
    usage_count: int                  # Times invoked
    success_rate: float               # Positive feedback ratio
    embedding: list[float]            # For semantic search
    forged_by: str                    # Who created it
    forged_at: datetime               # When
    last_improved: datetime | None    # Last TextGRAD application
    checkpoint_id: str | None         # Current version
```

### 5.2 Semantic Prompt Search

Find prompts by meaning, not just name:

```python
# Semantic search
results = await prompt_logos.invoke("prompt.registry.search", observer,
    query="template for reviewing python code for security issues",
    limit=5,
)
# → [prompt.task.security-review, prompt.task.code-review, ...]

# Filter by type
results = await prompt_logos.invoke("prompt.registry.search", observer,
    query="help users debug errors",
    type=PromptType.AGENT,
    status=Status.ACTIVE,
)
```

### 5.3 Prompt Promotion Protocol

Like Evergreen's JIT reification, prompts can be promoted:

```
DRAFT ──────────────► ACTIVE ──────────────► DEPRECATED
  │                      │                        │
  │ (usage > threshold)  │ (success > threshold)  │ (superseded)
  │ (success > 0.8)      │                        │
  ▼                      ▼                        ▼
auto-promote       maintain in catalog      archive + redirect
```

---

## Part VI: The Projection Protocol Integration

### 6.1 Prompts Project to Targets

The Projection Protocol applies to prompts:

```python
# Same prompt, different projections
prompt = await prompt_logos.invoke("prompt.system.claude.manifest", observer)

prompt.to_cli()      # ASCII-formatted for terminal display
prompt.to_json()     # Structured for API consumption
prompt.to_marimo()   # Interactive HTML for notebook editing
prompt.to_diff()     # Show changes from last version
```

### 6.2 Prompt Density

Prompts can compress or expand based on context pressure:

```python
# Full prompt for low-pressure context
full_prompt = prompt.project(target=RenderTarget.CLI, density="spacious")
# → All sections, full detail, examples included

# Compressed prompt for high-pressure context
compressed = prompt.project(target=RenderTarget.CLI, density="compact")
# → Essential sections only, no examples, terse language

# The compression is semantic, not just truncation
```

### 6.3 Prompt Layout (Multi-Section Prompts)

Complex prompts have layout:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROMPT LAYOUT PROJECTION                              │
│                                                                              │
│  SPACIOUS (full detail):                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ # Identity Section                                                       ││
│  │ [Full identity text with philosophy]                                     ││
│  ├─────────────────────────────────────────────────────────────────────────┤│
│  │ # Principles Section                                                     ││
│  │ [All 7 principles with examples]                                         ││
│  ├─────────────────────────────────────────────────────────────────────────┤│
│  │ # Context Section                                                        ││
│  │ [Full session context with memory crystals]                              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  COMPACT (essential only):                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ # kgents | Phase: DEVELOP | Focus: Coalition Forge                       ││
│  │ Principles: Tasteful, Composable, Ethical, Joy-Inducing                  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part VII: The Memory Integration (M-gent)

### 7.1 Prompts Inform Memory, Memory Informs Prompts

The bidirectional relationship:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PROMPT ↔ MEMORY INTEGRATION                              │
│                                                                              │
│   Prompt                              Memory                                 │
│     │                                   │                                    │
│     │ prompt.context.memory.manifest    │                                    │
│     ├──────────────────────────────────►│ Recall relevant crystals          │
│     │                                   │                                    │
│     │◄──────────────────────────────────┤ Inject into prompt context        │
│     │                                   │                                    │
│     │                                   │                                    │
│     │   Prompt execution produces       │                                    │
│     │   learnings                       │                                    │
│     │                                   │                                    │
│     │ self.memory.crystallize           │                                    │
│     ├──────────────────────────────────►│ Store as new crystals            │
│     │                                   │                                    │
│     │   Next prompt compilation         │                                    │
│     │   retrieves new crystals          │                                    │
│     │                                   │                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Prompt History as Memory

Prompt evolution history IS a form of memory:

```python
# Prompt history is queryable as memory
history = await prompt_logos.invoke("prompt.system.claude.history", observer,
    query="changes related to testing",
    limit=10,
)

# Each history entry is a memory crystal
for entry in history:
    print(f"{entry.timestamp}: {entry.reason}")
    print(f"  Sections modified: {entry.sections_modified}")
    print(f"  Reasoning: {entry.reasoning_trace}")
```

---

## Part VIII: The N-Phase Integration

### 8.1 Phase-Aware Prompts

Prompts can vary by N-Phase:

```python
# Same prompt, different phases
await prompt_logos.invoke("prompt.task.code-review.manifest", observer,
    phase=NPhase.DEVELOP)
# → Action-oriented review: "Focus on correctness. Ship fast."

await prompt_logos.invoke("prompt.task.code-review.manifest", observer,
    phase=NPhase.REFLECT)
# → Reflective review: "What patterns emerged? What did we learn?"
```

### 8.2 Prompt as Phase Transition Trigger

Prompts can trigger phase transitions (Auto-Inducer integration):

```python
# Prompt completion can signal phase transition
result = await prompt_logos.invoke("prompt.task.implement.execute", observer,
    input=task_spec,
)

# If result contains signifier, trigger transition
if "⟿[QA]" in result.output:
    await nphase.transition(NPhase.QA)
```

---

## Part IX: The CLI Integration (Revised v0.2)

### 9.1 Universal Prompt CLI

```bash
# Phase 1: Registry Operations
kg concept.prompt.registry.list                    # List all prompts
kg concept.prompt.registry.search "security review"  # Semantic search
kg concept.prompt.system.claude.manifest           # Get system prompt
kg concept.prompt.task.code-review.manifest        # Get task prompt

# Phase 2: Improvement Operations
kg concept.prompt.task.code-review.improve "be more concise"
kg concept.prompt.agent.kgent.history --limit=10
kg concept.prompt.system.claude.rollback abc123
kg concept.prompt.system.claude.diff abc123 def456

# Phase 3: Meta Operations
kg concept.prompt.meta.generate "create a prompt for debugging performance issues"
kg concept.prompt.task.code-review.fork security
kg concept.prompt.registry.validate ./my-prompt.md --type=task

# Phase 4: Composition Operations
kg concept.prompt.task.code-review.merge security
kg concept.prompt.persona.junior.manifest
```

### 9.2 Slash Commands (Living Commands)

```bash
# Shorthand slash commands (map to full paths)
/prompt                    # → concept.prompt.system.claude.manifest
/prompt.search "query"     # → concept.prompt.registry.search
/prompt.improve "feedback" # → concept.prompt.{current}.improve
/prompt.fork name          # → concept.prompt.{current}.fork
/prompt.list               # → concept.prompt.registry.list
```

**Note (v0.2)**: Slash commands provide ergonomic shortcuts for common operations. The `{current}` token refers to the prompt currently in focus (determined by session context).

---

## Part X: The Meta-Prompt System

### 10.1 The Prompt That Prompts Prompts

The most powerful feature of Prompt Logos: **meta-prompts**.

```python
# The meta-prompt for prompt improvement
META_IMPROVE_PROMPT = PromptM.unit("""
You are the Prompt Improver. Your task is to improve a prompt based on feedback.

The prompt to improve:
{{ prompt.content }}

The feedback:
{{ feedback }}

Improvement constraints:
- Preserve the prompt's essential purpose
- Respect the rigidity: {{ prompt.rigidity }} (0=fully adaptive, 1=resist change)
- Maintain categorical coherence
- Accumulate reasoning trace

Output the improved prompt with your reasoning.
""", PromptType.META)

# Meta-prompts can improve themselves
META_IMPROVE_PROMPT = META_IMPROVE_PROMPT.improve(
    "be more explicit about preserving type constraints"
)
```

### 10.2 Meta-Prompt Catalog

| Meta-Prompt | Purpose |
|-------------|---------|
| `prompt.meta.improve` | Improve any prompt via TextGRAD |
| `prompt.meta.generate` | Generate new prompts from descriptions |
| `prompt.meta.analyze` | Analyze prompt structure and quality |
| `prompt.meta.compose` | Compose multiple prompts |
| `prompt.meta.decompose` | Split prompt into sections |
| `prompt.meta.style` | Apply style transfer to prompt |
| `prompt.meta.compress` | Compress prompt while preserving semantics |
| `prompt.meta.expand` | Expand terse prompt with examples |
| `prompt.meta.validate` | Validate prompt against type constraints |
| `prompt.meta.translate` | Translate prompt to different observer |

### 10.3 The Self-Referential Loop

Meta-prompts can improve themselves, creating autopoietic potential:

```python
# The meta-improve prompt improves the meta-improve prompt
better_improver = await prompt_logos.invoke("prompt.meta.improve.invoke", observer,
    prompt=META_IMPROVE_PROMPT,
    feedback="be more systematic about rigidity handling",
)

# This is safe because:
# 1. Checkpointing enables rollback
# 2. Rigidity limits change rate
# 3. Validation ensures type constraints
# 4. Human approval tiers exist for high-rigidity changes
```

---

## Part XI: The Implementation Architecture

### 11.1 File Structure

```
impl/claude/protocols/prompt_logos/
├── __init__.py                    # Package exports
├── category.py                    # PromptCategory, PromptType
├── monad.py                       # PromptM monad (generalized)
├── operad.py                      # PROMPT_OPERAD
├── sheaf.py                       # PromptSheaf
├── logos.py                       # PromptLogos resolver
├── registry.py                    # Prompt catalog (L-gent integration)
├── textgrad.py                    # UniversalTextGRAD
├── inheritance.py                 # Prompt inheritance system
├── versioning.py                  # Branching, merging, rollback
├── projection.py                  # Prompt → Target projection
├── observers.py                   # Observer-dependent manifestation
├── meta/
│   ├── __init__.py
│   ├── improve.py                 # Meta-improve prompt
│   ├── generate.py                # Meta-generate prompt
│   ├── analyze.py                 # Meta-analyze prompt
│   └── compose.py                 # Meta-compose prompt
├── types/
│   ├── __init__.py
│   ├── system.py                  # System prompt type
│   ├── agent.py                   # Agent prompt type
│   ├── task.py                    # Task prompt type
│   ├── persona.py                 # Persona prompt type
│   └── context.py                 # Context prompt type
├── cli.py                         # CLI integration
└── _tests/
    ├── test_monad.py              # Monadic law tests
    ├── test_operad.py             # Operad law tests
    ├── test_sheaf.py              # Coherence tests
    ├── test_inheritance.py        # Lineage tests
    └── test_meta.py               # Meta-prompt tests

impl/claude/protocols/agentese/contexts/
└── prompt.py                      # AGENTESE context resolver (already exists, to be extended)

spec/prompt/
├── README.md                      # Index of prompt specs
├── system/
│   └── claude.md                  # Spec for CLAUDE.md
├── agent/
│   ├── kgent.md                   # Spec for K-gent prompt
│   ├── scout.md                   # Spec for scout prompt
│   └── ...
├── task/
│   ├── code-review.md             # Spec for code review template
│   ├── test-write.md              # Spec for test writing template
│   └── ...
├── persona/
│   ├── developer.md               # Developer persona spec
│   ├── architect.md               # Architect persona spec
│   └── ...
└── meta/
    ├── improve.md                 # Meta-improve spec
    ├── generate.md                # Meta-generate spec
    └── ...
```

### 11.2 Migration Path

The Evergreen Prompt System becomes a **special case** of Prompt Logos:

```
Current:                          Future:
impl/claude/protocols/prompt/     impl/claude/protocols/prompt/
                                  ├── evergreen/  ← Existing code (renamed)
                                  │   └── (all current Wave 1-6 code)
                                  └── logos/      ← New universal system
                                      └── (new architecture)
```

The existing Evergreen code continues to work; Prompt Logos extends it.

---

## Part XII: Success Criteria

### 12.1 Quantitative

| Metric | Target | Rationale |
|--------|--------|-----------|
| Prompt types supported | 6+ | system, agent, task, persona, context, meta |
| Monadic law pass rate | 100% | Laws are not optional |
| Operad law pass rate | 100% | Composition is fundamental |
| Meta-prompt success rate | >80% | Self-improvement should work |
| Prompt registry size | 50+ | Rich prompt ecosystem |
| Test coverage | >80% | Trustworthy system |

### 12.2 Qualitative

- [ ] **Universal**: Any prompt type can be managed
- [ ] **Composable**: Prompts compose lawfully
- [ ] **Self-Improving**: Prompts improve via feedback
- [ ] **Versioned**: Full history with rollback
- [ ] **Searchable**: Semantic prompt discovery
- [ ] **Observable**: Reasoning traces visible
- [ ] **Safe**: Rigidity + approval tiers prevent drift

### 12.3 The Ultimate Test

Can you use Prompt Logos to:

1. Create a new prompt type from description?
2. Improve it with natural language feedback?
3. Fork a variant for experimentation?
4. Merge successful experiments back?
5. Roll back failed experiments?
6. Search for related prompts semantically?
7. Compose prompts for complex workflows?
8. Use the meta-prompts to improve the meta-prompts?

If yes to all: Success.

---

## Part XIII: Open Questions

1. **Prompt Governance**: Who can modify high-rigidity prompts?
2. **Cross-Project Prompts**: Should prompts be shareable across kgents instances?
3. **Prompt Versioning**: Git-like branches or simpler linear history?
4. **Prompt Testing**: How to test prompt quality automatically?
5. **Prompt Economics**: Should prompt improvement cost entropy budget?
6. **Prompt Privacy**: Some prompts contain sensitive patterns—how to handle?

---

## Part XIV: The Vision Statement

> **Prompt Logos transforms prompt management from an afterthought into a first-class protocol.**

Today, prompts are:
- Scattered across files, configs, and codebases
- Manually maintained with no version control
- Copied and pasted with no inheritance
- Improved through ad-hoc iteration with no systematic feedback

With Prompt Logos, prompts become:
- Unified in a categorical substrate
- Automatically version-controlled with full history
- Inherited and composed with lawful guarantees
- Self-improving through TextGRAD and meta-prompts

**The prompt that prompts prompts is not a prompt—it is a category. And that category is Prompt Logos.**

---

## Appendix A: Relationship to Existing Systems

| Existing System | Relationship to Prompt Logos |
|-----------------|------------------------------|
| Evergreen Prompt System | Special case (system prompts) |
| AGENTESE | Extended context (`concept.prompt.*`) |
| L-gent Registry | Prompts as catalog entries |
| M-gent Memory | Bidirectional integration |
| N-Phase | Phase-aware prompt variants |
| Projection Protocol | Prompt projection to targets |
| Forest Protocol | Prompt evolution tracking |

---

## Appendix B: Principle Alignment Matrix (Added v0.2)

This matrix documents how Prompt Logos aligns with each principle from `spec/principles.md`:

| Principle | Alignment | Implementation | Risk |
|-----------|-----------|----------------|------|
| **1. Tasteful** | ✅ Strong | 5-context limit preserved; phases scope features; registry curation | Scope creep across phases |
| **2. Curated** | ✅ Strong | Rigidity earned through provenance; promotion protocol; deprecation path | Registry sprawl without active curation |
| **3. Ethical** | ✅ Strong | Human approval tiers; rigidity governance; halting safeguards | Meta-prompt autonomy concerns |
| **4. Joy-Inducing** | ⚠️ Moderate | Slash command ergonomics; semantic search | CLI verbosity with `concept.prompt.*` paths |
| **5. Composable** | ✅ Strong | Monadic laws; operad composition; agent integration | Complex composition chains |
| **6. Heterarchical** | ✅ Strong | No prompt hierarchy; cross-prompt inheritance | Lineage depth management |
| **7. Generative** | ✅ Strong | Spec generates registry; meta-prompts generate prompts | Self-modification stability |
| **Meta: Accursed Share** | ⚠️ Moderate | Entropy budget for prompt exploration | Not deeply integrated yet |
| **Meta: AGENTESE** | ✅ Strong | Full path resolution; no 6th context | Observer semantics TBD |
| **Meta: Personality Space** | ⚠️ Moderate | Persona prompts (Phase 4) | Deferred |

### Tensions to Navigate

1. **Tasteful vs. Generative**: Meta-prompts that generate prompts could lead to sprawl
   - *Resolution*: Promotion protocol; usage thresholds; human curation

2. **Composable vs. Joy-Inducing**: Deep paths like `concept.prompt.task.code-review.manifest` are verbose
   - *Resolution*: Slash command shortcuts; REPL context navigation

3. **Ethical vs. Heterarchical**: Who governs prompts if there's no hierarchy?
   - *Resolution*: Rigidity is earned (provenance-based); human approval tiers for high-rigidity changes

---

## Appendix C: Heritage Acknowledgment

Prompt Logos builds on:

| Heritage | Contribution |
|----------|--------------|
| DSPy | Prompts as programs |
| SPEAR | Prompt algebra |
| Meta-Prompting | Monadic self-improvement |
| TextGRAD | Textual gradients |
| Evergreen Prompt System | CLAUDE.md cultivation |
| AGENTESE | Path resolution paradigm |
| Category Theory | Mathematical foundation |

---

*"The prompt that reads itself is the prompt that writes itself. The prompt that writes prompts is Prompt Logos. The category in which all prompts are morphisms is the ground on which all language agents stand."*

---

## Appendix D: Revision Log (Added v0.2)

| Version | Date | Changes |
|---------|------|---------|
| v0.1 | 2025-12-16 | Initial vision document |
| v0.2 | 2025-12-16 | Critical analysis; context change `prompt.*` → `concept.prompt.*`; phase scoping; governance protocols; halting safeguards; principle alignment matrix |

---

*Specification v0.2 (Critically Revised) — 2025-12-16*
