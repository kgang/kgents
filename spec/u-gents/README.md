# U-GENT: THE UNDERSTUDY

## Specification v2.0

**Status:** Proposed Standard
**Symbol:** `U` (The Economic Compressor)
**Motto:** *"Genius is expensive. Routine should be cheap."*

---

## 1. The Concept: Black-Box Chain-of-Thought Distillation

U-gent addresses the **Intelligence-Cost Paradox**: the most capable agents (Teachers) are too expensive to run in infinite loops, while the cheapest agents (Students) lack the judgment for autonomous tasks.

U-gent implements **Black-Box Chain-of-Thought Distillation**. It does not merely copy the *output* of a teacher; it captures the *reasoning process* (the "Rationalization"), filters it for quality, and trains smaller, local, or cheaper models to mimic that reasoning.

### The Core Shift

```
FROM: Calling GPT-4 10,000 times for a repetitive classification task.

TO:   Calling GPT-4 50 times to generate a training set,
      verifying the data,
      fine-tuning a Llama-3-8B model,
      serving the remaining 9,950 calls at 1/100th the cost.
```

---

## 2. Theoretical Foundation

### 2.1 The Distillation Hierarchy

Most modern agent systems rely on proprietary APIs (Claude, OpenAI) where access to probability distributions (logits) is restricted. U-gent focuses on **Rationale Distillation**:

| Method | Access Required | U-gent Viability |
|--------|----------------|------------------|
| **Standard Distillation (White-Box)** | Probability distributions (logits) | Hard with APIs |
| **Rationale Distillation (Black-Box)** | Text outputs only | Primary method |
| **In-Context Distillation** | Few-shot prompts | Secondary method |

**Rationale Distillation**: Student learns to generate the Teacher's "Chain of Thought" before the answer. The reasoning tokens become training signal.

### 2.2 The Active Learning Loop

Random sampling of Teacher traces is inefficient. U-gent employs **Uncertainty Sampling**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACTIVE LEARNING LOOP                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    Input ──► Student attempts task                               │
│                     │                                            │
│                     ▼                                            │
│              ┌─────────────┐                                     │
│              │  Measure    │                                     │
│              │  Semantic   │                                     │
│              │  Entropy    │                                     │
│              └──────┬──────┘                                     │
│                     │                                            │
│         ┌──────────┴──────────┐                                 │
│         ▼                     ▼                                  │
│  ┌─────────────┐      ┌─────────────┐                           │
│  │    LOW      │      │    HIGH     │                           │
│  │ Uncertainty │      │ Uncertainty │                           │
│  └──────┬──────┘      └──────┬──────┘                           │
│         │                    │                                   │
│         ▼                    ▼                                   │
│  Use Student         Escalate to Teacher                        │
│  (Free)              (Cost → Investment)                        │
│                             │                                    │
│                             ▼                                    │
│                      Add to Training Set                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

This ensures the training budget is spent only on the **frontier of the Student's ignorance**.

### 2.3 The "Step-by-Step" Protocol

Research shows that small models fail at complex tasks not because they lack knowledge, but because they lack **working memory**. U-gent forces Students to output reasoning tokens before final answers, effectively "buying time to think."

```
Input → [Student] → <Reasoning Block> → Final Answer
```

The reasoning block externalizes the working memory that smaller models lack internally.

---

## 3. The Distillation Architecture

### 3.1 The Panopticon (Data Collection)

The observer must be smarter than a simple logger. It implements **Hindsight Relabeling**: if a Teacher's execution fails or errors, it is discarded or corrected before storage.

```python
@dataclass
class ShadowPanopticon:
    """
    Advanced observer that filters for 'Golden Traces'.
    Only successful, high-quality reasoning paths are stored.
    """

    trace_store: DGent[TraceDataset]
    quality_gate: Agent[Trace, bool]  # Usually a fast V-gent check

    async def observe_and_filter(self, trace: TeacherTrace):
        # 1. Outcome Check: Did the task succeed?
        if trace.status != "SUCCESS":
            return  # Discard failures

        # 2. Heuristic Check: Is the reasoning too short?
        if len(trace.reasoning_tokens) < 50:
            return  # Discard "lucky guesses" without reasoning

        # 3. Storage
        await self.trace_store.append(trace)
```

**Quality Gates:**
- Outcome verification (success/failure)
- Reasoning depth thresholds
- V-gent principle validation
- Coherence scoring

### 3.2 The Curriculum Sieve (Dataset Curation)

Before training, data must be curated. U-gent synthesizes **Counterfactuals** and **Edge Cases** to robustify the dataset.

```python
class CurriculumSieve:
    """
    Refines raw traces into a high-quality training corpus.
    """

    async def synthesize_edge_cases(
        self,
        trace: TeacherTrace
    ) -> list[TeacherTrace]:
        """
        Ask the Teacher: 'What would have made this task harder?'
        Generate synthetic difficult examples to prevent
        overfitting to easy routines.
        """
        synthetic_inputs = await self.teacher.invoke(
            f"Given input '{trace.input}', generate 3 variations "
            f"that are semantically tricky or adversarial."
        )
        # Teacher solves the new tricky inputs → New Traces
        return await self.solve_and_capture(synthetic_inputs)
```

**Curriculum Learning Stages:**
1. Easy examples (high Teacher confidence)
2. Medium examples (moderate variance)
3. Hard examples (synthetic adversarials)
4. Edge cases (Teacher-identified tricky inputs)

### 3.3 The Semantic Router

The router decides who handles the request. It uses **Semantic Entropy** rather than simple logprobs, as probability metrics are often poorly calibrated.

```python
@dataclass
class SemanticRouter:
    """
    Routes based on Semantic Entropy.
    """
    student: StudentModel
    teacher: TeacherAgent
    entropy_threshold: float = 0.6

    async def route(self, input: Input) -> Output:
        # 1. Fast Draft: Student generates output
        draft = await self.student.generate(input)

        # 2. Uncertainty Check
        # Fast: Check logprobs of answer tokens
        # Robust: Sample student 3 times; if answers differ → High Uncertainty
        uncertainty = await self.estimate_uncertainty(input, draft)

        if uncertainty < self.entropy_threshold:
            return draft  # Cheap success

        # 3. Escalation
        teacher_output = await self.teacher.invoke(input)

        # 4. Loop Closure: Hard example becomes training data
        await self.u_gent.record_gap(input, teacher_output)

        return teacher_output
```

**Uncertainty Estimation Methods:**
- **Logprob Analysis**: Fast but poorly calibrated
- **Semantic Sampling**: Generate N samples, check semantic divergence
- **Confidence Tokens**: Train model to output calibrated confidence

---

## 4. Integration & Economics

### 4.1 The ROI Formula (B-gent Integration)

U-gent is an investment vehicle. B-gent allocates capital (tokens) based on projected ROI.

```
         (Cost_T - Cost_S) × N_calls - Cost_Training
ROI = ─────────────────────────────────────────────────
                     Cost_Training

Where:
  Cost_T:        Cost per Teacher call (e.g., $0.03)
  Cost_S:        Cost per Student call (e.g., $0.0002)
  N_calls:       Projected volume
  Cost_Training: Cost to gather data + fine-tune
```

**Break-Even Analysis:**
```
              Cost_Training
BEP_calls = ─────────────────
            Cost_T - Cost_S
```

If BEP < 1 week of volume, B-gent authorizes training investment.

### 4.2 Integration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    U-GENT INTEGRATION MAP                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────┐     ┌───────────┐     ┌───────────┐             │
│  │  L-gent   │────►│  B-gent   │────►│  U-gent   │             │
│  │ (Catalog) │     │ (Banker)  │     │(Distiller)│             │
│  └───────────┘     └───────────┘     └─────┬─────┘             │
│       │                                    │                    │
│       │ Reports                            │ Shadows            │
│       │ high-frequency                     ▼                    │
│       │ tasks                        ┌───────────┐              │
│       │                              │  Teacher  │              │
│       │                              │ (K-gent)  │              │
│       │                              └─────┬─────┘              │
│       │                                    │                    │
│       └────────────────────────────────────┼────────────────────│
│                                            │                    │
│                                            ▼                    │
│                                      ┌───────────┐              │
│                                      │  D-gent   │              │
│                                      │ (Traces)  │              │
│                                      └───────────┘              │
│                                                                  │
│  Flow:                                                          │
│  1. L-gent identifies high-frequency task patterns              │
│  2. B-gent calculates ROI, authorizes training budget           │
│  3. U-gent shadows Teacher, builds trace corpus                 │
│  4. U-gent trains Student, validates with V-gent                │
│  5. Student deployed; escalations feed back to training         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 U + R (Refinery Synergy)

- **R-gent (Refinery):** Optimizes the *prompt* (finding the best words to make the Teacher work better)
- **U-gent (Understudy):** Removes the prompt entirely. Instructions are baked into model weights.

**Pattern:** R-gent optimizes the prompt *first*. Once stable and successful, U-gent uses that R-optimized prompt to generate the Golden Dataset for distillation.

---

## 5. Implementation Roadmap

### Phase 1: The "Hitchhiker" (Passive Shadowing)
A wrapper that sits on `Agent.invoke`. It sends inputs/outputs to a D-gent vector store. It does **not** train. It simply builds `corpus.jsonl`.

```python
shadowed_agent = u_gent.shadow(teacher)
# All teacher calls now logged
```

### Phase 2: The "Imposter" (Evaluation Mode)
The Student model runs in the background for every request (fire-and-forget). It does not return the answer to the user.

**Metric:** `AgreementRate` — How often does `Student(x) == Teacher(x)`?

When `AgreementRate > 95%` on the validation set, the Switch is enabled.

### Phase 3: The "Switch" (Active Routing)
The router is deployed. It directs traffic to the Student, escalating only on high uncertainty. The system now saves money.

### Phase 4: The "Dreamer" (Synthetic Augmentation)
The Teacher runs during off-peak hours to generate synthetic edge cases for the Student, preemptively closing knowledge gaps before users encounter them.

---

## 6. Anti-Patterns & Safety

### 6.1 The Echo Chamber
**Problem:** Training a Student on its own output.
**Rule:** Students train ONLY on Teacher outputs or verified Ground Truth.

### 6.2 The Cargo Cult
**Problem:** Distilling the answer without the reasoning.
**Rule:** Training data must be `(Input → Reasoning → Output)`.

### 6.3 The Frozen Student
**Problem:** Never updating the student after deployment.
**Rule:** Concept Drift detection monitors escalation rate. Spike triggers re-training.

### 6.4 Mode Collapse
**Problem:** Student learns "average" safe response rather than specific nuance.
**Mitigation:** Use LoRA adapters specific to narrow tasks rather than one giant "do-everything" student.

---

## 7. Technical Stack Recommendation

For implementation in `impl/claude/agents/u/`:

| Component | Recommendation | Rationale |
|-----------|---------------|-----------|
| **Student Model** | Llama-3-8B-Instruct (4-bit) | Edge deployment, low cost |
| **API Student** | GPT-4o-mini | API-based distillation |
| **Training Framework** | Unsloth or Torchtune | 2x faster training |
| **Adapter Strategy** | LoRA (Low-Rank Adaptation) | Hot-swap skills instantly |

**LoRA Adapter Pattern:**
```
Base Model: Frozen Llama-3-8B
├── Skill A (SQL Generation): LoRA Adapter A
├── Skill B (Summarization):  LoRA Adapter B
└── Skill C (Code Review):    LoRA Adapter C
```

---

## 8. Principles Alignment

| Principle | How U-gent Aligns |
|-----------|-------------------|
| **Tasteful** | Single purpose: economic compression through distillation |
| **Curated** | Only high-frequency, stable-pattern tasks are distilled |
| **Ethical** | V-gent validates Students before promotion; no quality degradation |
| **Joy-Inducing** | "Apprentice becomes master" narrative; watching cost curves drop |
| **Composable** | `u_gent.distill(any_agent, task)` works uniformly |
| **Generative** | Creates new cheap capabilities from expensive ones |

---

*"The Master fails more times than the Apprentice has even tried. The U-gent captures those trials so the Apprentice need not fail at all."*
