# Autonomous Bootstrap Protocol

**A meta-level protocol for Kent + Claude Code to complete kgents.**

This document is self-referential: Claude Code reads it to guide implementation, and the implementation validates the protocol.

---

## Ground: What Exists

```
impl/claude-openrouter/
├── bootstrap/           # 7 irreducible agents
│   ├── id.py           # Identity: A → A
│   ├── compose.py      # Composition: (Agent, Agent) → Agent
│   ├── judge.py        # Judgment: (Agent, Principles) → Verdict
│   ├── ground.py       # Grounding: Void → Facts
│   ├── contradict.py   # Contradiction: (A, B) → Tension | None
│   ├── sublate.py      # Synthesis: Tension → Synthesis | Hold
│   ├── fix.py          # Fixed-point: (A → A) → A
│   └── types.py        # Agent[A, B] base class
├── agents/
│   ├── c/              # Category theory (Maybe, Either, parallel, race, branch, switch)
│   ├── h/              # Dialectics (Hegel, Jung, Lacan)
│   └── k/              # Persona (KgentAgent, PersonaQueryAgent, EvolutionAgent)
└── runtime/            # LLM execution (ClaudeRuntime, OpenRouterRuntime)

impl/zen-agents/        # Textual TUI demonstrating bootstrap patterns
```

**Missing:**
- `impl/claude-openrouter/agents/a/` — A-gents (AbstractSkeleton, CreativityCoach)
- `impl/claude-openrouter/agents/b/` — B-gents (HypothesisEngine, Robin)

---

## The Protocol

### Principle: Heterarchical Collaboration

Neither Kent nor Claude Code is "in charge." The collaboration is heterarchical:
- **Kent provides Ground**: preferences, judgment calls, domain knowledge
- **Claude Code provides Fix**: iteration, exploration, mechanical translation
- **Both apply Judge**: reviewing against the 7 principles

---

## Phase A: A-gents Implementation

### A.1 AbstractSkeleton

**Goal:** Formalize what `bootstrap.types.Agent[A, B]` already is.

**Claude Code Action:**
```
1. Read impl/claude-openrouter/bootstrap/types.py
2. Read spec/a-gents/abstract/skeleton.md
3. Create impl/claude-openrouter/agents/a/__init__.py
4. Create impl/claude-openrouter/agents/a/skeleton.py

skeleton.py should:
- Re-export Agent[A, B] as AbstractAgent
- Add documentation/typing that formalizes the skeleton pattern
- NOT duplicate logic (composition, not duplication)
```

**Kent Checkpoint:** Is this tasteful? Does AbstractAgent add value or just rename?

**Possible Sublation:** Maybe AbstractAgent is unnecessary—Agent[A, B] IS the skeleton. The "A-gent abstraction" is the bootstrap itself. In that case, `skeleton.py` documents rather than implements.

---

### A.2 CreativityCoach

**Goal:** An LLM-backed agent for idea expansion.

**Spec Source:** `spec/a-gents/art/creativity-coach.md`

**Claude Code Action:**
```
1. Read spec/a-gents/art/creativity-coach.md
2. Read impl/claude-openrouter/runtime/base.py (LLMAgent pattern)
3. Create impl/claude-openrouter/agents/a/creativity.py

creativity.py should:
- Define CreativityCoach(LLMAgent[str, CreativityResponse])
- CreativityResponse includes: expansions, questions, connections, constraints
- build_prompt: converts idea into expansion prompt
- parse_response: structures LLM output
```

**Types:**
```python
@dataclass
class CreativityResponse:
    original_idea: str
    expansions: list[str]        # Related concepts
    questions: list[str]         # Provocative questions
    connections: list[str]       # Unexpected links
    constraints: list[str]       # Generative constraints
```

**Kent Checkpoint:** Does this spark joy? Is the response structure right?

---

## Phase B: B-gents Implementation

### B.1 HypothesisEngine

**Goal:** Generate ranked, falsifiable hypotheses from observations.

**Spec Source:** `spec/b-gents/hypothesis-engine.md`

**Claude Code Action:**
```
1. Read spec/b-gents/hypothesis-engine.md
2. Create impl/claude-openrouter/agents/b/__init__.py
3. Create impl/claude-openrouter/agents/b/hypothesis.py

hypothesis.py should:
- Define Hypothesis dataclass with falsification_criteria
- Define HypothesisEngine(LLMAgent[str, list[Hypothesis]])
- Prompt includes epistemic humility guidance
```

**Types:**
```python
@dataclass
class Hypothesis:
    claim: str
    supporting_evidence: list[str]
    falsification_criteria: str   # HOW to disprove (Popperian)
    confidence: float             # 0.0-1.0, epistemic humility
    domain: str                   # e.g., "molecular biology"
```

**Kent Checkpoint:** Is falsification_criteria required? Is confidence meaningful?

---

### B.2 Robin (Scientific Companion)

**Goal:** Personalized scientific dialogue combining K-gent + Hypothesis + Dialectic.

**Spec Source:** `spec/b-gents/robin.md` (if exists) or README.md

**Claude Code Action:**
```
1. Read spec/b-gents/README.md for Robin concept
2. Create impl/claude-openrouter/agents/b/robin.py

robin.py should:
- Robin composes: kgent >> hypothesis_engine >> hegel
- Personalized scientific companion
- Dialogic: responds to queries with hypotheses + dialectic
```

**Composition Pattern:**
```python
def robin(persona_seed: PersonaSeed) -> Agent[str, RobinResponse]:
    """
    Scientific companion = K-gent personalization
                         >> hypothesis generation
                         >> dialectic refinement
    """
    k = kgent(persona_seed)
    h = hypothesis_engine()
    hegel_agent = hegel()

    # This is the beautiful composition
    return k >> h >> hegel_agent
```

**Kent Checkpoint:** Is Robin an agent or a composed pipeline? (Both is fine—composition IS the agent.)

---

## Execution Protocol

### For Each Phase

```
LOOP:
  1. Claude Code reads spec
  2. Claude Code implements
  3. Kent reviews (Judge)
  4. IF accept: mark complete, next phase
     ELIF revise: Claude Code modifies
     ELIF reject: discuss, potentially Sublate
```

### Termination (Fix)

Implementation is complete when:
```python
def protocol_complete() -> bool:
    return all([
        exists("impl/claude-openrouter/agents/a/__init__.py"),
        exists("impl/claude-openrouter/agents/a/skeleton.py"),
        exists("impl/claude-openrouter/agents/a/creativity.py"),
        exists("impl/claude-openrouter/agents/b/__init__.py"),
        exists("impl/claude-openrouter/agents/b/hypothesis.py"),
        exists("impl/claude-openrouter/agents/b/robin.py"),
        all_tests_pass(),
        kent_approves(),  # Human Ground—cannot be bypassed
    ])
```

---

## Meta-Instructions for Claude Code

When reading this document:

1. **Parse Ground state** — What exists vs. what's missing
2. **Follow phase order** — A.1 → A.2 → B.1 → B.2
3. **Read specs first** — Always understand before implementing
4. **Apply 7 principles** — Especially Tasteful, Composable, Generative
5. **Ask Kent** — When judgment calls arise (use AskUserQuestion)
6. **Mark progress** — Update HYDRATE.md as phases complete
7. **Compose, don't concatenate** — Use existing patterns, don't reinvent

### On Tensions

If you encounter contradictions:
1. Surface them explicitly (Contradict)
2. Propose synthesis or hold (Sublate)
3. Let Kent decide (Judge)

### On Uncertainty

If spec is unclear:
1. Check related specs (e.g., how H-gents handle LLMAgent)
2. Ask Kent for clarification
3. Propose and iterate (Fix)

---

## Quick Start

To begin implementation:

```bash
# Kent runs this command:
claude "Read AUTONOMOUS_BOOTSTRAP_PROTOCOL.md and implement Phase A.1 (AbstractSkeleton)"
```

Claude Code will:
1. Read this protocol
2. Read the relevant specs
3. Create the implementation
4. Request review

---

## Self-Description

This protocol is itself an application of bootstrap agents:

| Protocol Element | Bootstrap Agent |
|------------------|-----------------|
| "What exists" section | Ground |
| Phase ordering | Compose |
| Kent checkpoints | Judge |
| Termination condition | Fix |
| "On Tensions" section | Contradict + Sublate |
| The protocol itself | Id (it passes through to implementation) |

The protocol bootstraps the bootstrap.

---

## Changelog

- **Dec 2025**: Initial protocol created
- **Status**: Ready for Phase A.1
