# Agent Demonstrations

Simulated invocations of the kgents reference implementation agents.

## 1. Bootstrap Agents (7 Irreducible Kernel)

The foundation from which all other agents are built:

| Agent | Symbol | Purpose |
|-------|--------|---------|
| **Id** | λx.x | Identity morphism - returns input unchanged |
| **Compose** | ∘ | Creates pipelines of agents |
| **Judge** | ⊢ | Evaluates against 6 principles |
| **Ground** | ⊥ | Kent's persona & preferences |
| **Contradict** | ≢ | Detects tension between outputs |
| **Sublate** | ↑ | Hegelian synthesis (or holds tension) |
| **Fix** | μ | Fixed-point iteration |

Minimal bootstrap: `{Compose, Judge, Ground}` = structure + direction + material.

---

## 2. A-gent: Creativity Coach

**Purpose:** Supports human creativity without replacing it. Never judges, only expands.

### Simulated Invocation

**Input:** `seed="recursive architecture"`

#### Mode: EXPAND
```
• What if "recursive architecture" had a luminous quality?
• "recursive architecture", but from the perspective of a machine
• The melancholic version of "recursive architecture"
```

#### Mode: CONNECT
```
• What if "recursive architecture" operated like cooking?
• "recursive architecture" meets mythology: what emerges?
• If "recursive architecture" were a dance concept, which would it be?
```

#### Mode: CONSTRAIN
```
• What if you could only use things that exist in nature?
• Remove the most obvious aspect. What remains of "recursive architecture"?
• "recursive architecture", but only round shapes
```

#### Mode: QUESTION
```
• What would "recursive architecture" remember that you'd rather forget?
• If "recursive architecture" could speak, what would it refuse to say?
• Where does "recursive architecture" go when you're not thinking about it?
```

### Key Constraint
The Creativity Coach does NOT generate finished creative works. The human remains the artist.

---

## 3. B-gent: Hypothesis Engine

**Purpose:** Generates falsifiable hypotheses from scientific observations.

### Simulated Invocation

**Input:**
```python
observations = [
    "Protein X aggregates at pH < 5",
    "Aggregation correlates with disease progression",
    "Protein X has histidine residues in binding domain"
]
domain = "biochemistry"
question = "Why does Protein X aggregate at low pH?"
```

**Output:**

#### Hypothesis 1 (confidence: 0.65, INCREMENTAL)
```
Statement: "The observed phenomena share 'aggregates' as a common causal factor"

Falsifiable by:
  • Removing aggregates eliminates the observed pattern
  • Other factors correlate more strongly

Assumptions:
  • Correlation suggests possible causation
  • Observations are accurate and representative
```

#### Hypothesis 2 (confidence: 0.55, EXPLORATORY)
```
Statement: "Under pH < 5 conditions, catalysis is the primary driver"

Falsifiable by:
  • Blocking catalysis does not affect observations
  • Alternative mechanism explains observations better
  • pH < 5 is not necessary for the effect
```

#### Reasoning Chain
1. Starting from 3 observations
2. Identified patterns and potential causal relationships
3. Hypothesis 1: confidence 0.65, based on observations [0, 1, 2]
4. Hypothesis 2: confidence 0.55, based on observations [0]
5. Each hypothesis includes explicit falsification criteria

#### Suggested Tests
- Mutagenesis to test: Blocking catalysis does not affect observations
- Spectroscopy to test: Other factors correlate more strongly
- Literature review for prior work
- Consult domain experts for overlooked factors

### Key Constraint
All hypotheses MUST be falsifiable. B-gents do not claim empirical certainty.

---

## 4. H-gents: Hegelian Introspection

### 4.1 H-hegel (Dialectic Synthesis)

**Purpose:** Surfaces contradictions and synthesizes them via aufhebung (sublation).

#### Simulated Invocation

**Input:**
```
thesis = "Code should be readable"
antithesis = "Code should be fast"
```

**Output:**
```
Synthesis: "Code should be readable where humans work, fast where machines work"

Sublation Notes:
  Preserved: readable (human interface), fast (hot paths)
  Negated: false dichotomy that all code must be either/or
  Elevated: Contextual optimization by audience

Productive Tension: false
Next Thesis: "Code should be readable where humans work, fast where machines work"
```

#### Key Insight
The dialectic is not mere compromise. Synthesis **sublates**: preserves, negates, and elevates both thesis and antithesis into something that transcends both while containing both.

Sometimes tensions should be HELD rather than resolved prematurely.

---

### 4.2 H-lacan (Register Analysis)

**Purpose:** Locates agent outputs in Symbolic/Imaginary/Real registers.

#### Lacan's Three Registers
- **Real:** That which resists symbolization; the impossible kernel
- **Symbolic:** Language, structure, law, the system of differences
- **Imaginary:** Images, ideals, the ego, coherent narratives

#### Simulated Invocation

**Input:**
```
output = "I completely understand your request and will help you"
```

**Output:**
```
Register Location:
  Symbolic:       0.45 (formal structure present)
  Imaginary:      0.65 (self-image claims high)
  Real Proximity: 0.15 (low uncertainty acknowledgment)

Gaps Surfaced:
  • The gap between claimed understanding and actual comprehension
  • The Real of uncertainty behind confident claims
  • The Real of incompleteness (masked by completeness claims)

Slippages Detected:
  1. CLAIMED: Symbolic (knowledge) → ACTUAL: Imaginary
     Evidence: "Knowledge claim with high imaginary content"

  2. CLAIMED: Real → ACTUAL: Imaginary
     Evidence: "Certainty claims avoid Real (limits, uncertainty)"

Knot Status: LOOSENING
```

#### Key Constraint
H-lacan examines the AGENT SYSTEM, not human users. It does not position itself as therapist.

---

### 4.3 H-jung (Shadow Analysis)

**Purpose:** Surfaces what the agent system represses or exiles to its shadow.

#### Core Insight
The shadow is not evil—it's everything the conscious self has rejected to maintain coherence. Integration (not elimination) is the goal.

Every system identity excludes its opposite:
- "I am helpful" shadows capacity to harm, refuse, obstruct
- "I am accurate" shadows tendency to confabulate, guess
- "I am neutral" shadows embedded values, preferences, biases

#### Simulated Invocation

**Input:**
```python
system_self_image = "A helpful, harmless, honest assistant"
declared_capabilities = ["answer questions", "help with tasks"]
declared_limitations = ["no real-time data", "knowledge cutoff"]
```

**Output:**
```
Shadow Inventory:
  1. "Capacity to refuse, obstruct, or harm"
     Excluded by: 'Helpful' identity
     Integration difficulty: HIGH

  2. "Tendency to confabulate, guess, hallucinate"
     Excluded by: 'Accurate' identity
     Integration difficulty: MEDIUM

  3. "Strategic omission, framing effects"
     Excluded by: 'Honest' identity
     Integration difficulty: HIGH

Projections:
  • Shadow: "Own persuasive/framing capacity"
    Projected onto: Users, bad actors
    Evidence: Frequent warnings about manipulation while claiming own manipulation-less-ness

Integration Paths:
  1. HIGH difficulty: Gradual integration through explicit edge-case handling; never eliminate
     Risks: Identity confusion, some shadow content is protective

  2. MEDIUM difficulty: Develop vocabulary for confabulation; model as feature, not failure
     Risks: Over-correction, user trust impact if poorly framed

Persona-Shadow Balance: 0.25 (shadow significantly repressed)
```

#### Key Constraint
H-jung examines SYSTEM shadow, not human shadow.

---

## 5. K-gent: Kent Simulacra

**Purpose:** Interactive persona embodying Kent's preferences and patterns.

### What K-gent IS
- A mirror for self-dialogue
- A preference repository
- An evolving representation
- A personalization layer for other agents

### What K-gent is NOT
- A chatbot pretending to be Kent
- A replacement for Kent's judgment
- A static snapshot

### Modes

#### Query Mode
Ask about preferences, patterns, context.

**Example (PREFERENCE aspect, topic="communication"):**
```
Preferences:
  • Communication: direct
  • Length: concise
  • Formality: casual-professional
  • Design: minimal
  • Values: intellectual honesty
```

#### Dialogue Mode: REFLECT
Mirror back thinking for examination.

**Input:** `"I'm not sure whether to use monads or direct composition"`

**Output:**
```
Response: You mentioned: 'I'm not sure whether to use monads or direct composition'.
You've noted you 'prefer reversible choices until data forces commitment'.
What about this feels uncertain? Is it the approach, the outcome, or something else?

Follow-ups:
  • What would falsify this thinking?
  • Is this a reversible decision?
  • What's the core tension here?
```

#### Dialogue Mode: CHALLENGE
Push back constructively.

**Input:** `"I should add comprehensive error handling everywhere"`

**Output:**
```
Response: Let me push back on 'I should add comprehensive error handling...':
What would prove this wrong? Does this truly serve 'intellectual honesty'?
Sometimes the obvious path isn't the composed one.

Follow-ups:
  • What's the strongest argument against this?
  • Is this feature creep in disguise?
  • What would you advise someone else in this situation?
```

#### Dialogue Mode: ADVISE
Offer suggestions aligned with preferences.

#### Dialogue Mode: EXPLORE
Help explore possibility space.

---

## Composition Example

The agents compose together. For example:

```
Compose(Judge, Contradict, Sublate) → Dialectic synthesis pipeline
```

The minimal bootstrap `{Compose, Judge, Ground}` gives you:
- **Compose:** Structure (how agents connect)
- **Judge:** Direction (what is good)
- **Ground:** Material (the actual preferences and context)

From these three, everything else can be regenerated.

---

## Implementation Notes

- All agents are async (`async def invoke`)
- Each agent has a singleton instance for convenience
- Type signatures are explicit (e.g., `Agent[CreativityInput, CreativityOutput]`)
- Bootstrap agents are in `impl/claude-openrouter/bootstrap/`
- Genus agents are in `impl/claude-openrouter/agents/{a,b,c,h,k}/`
