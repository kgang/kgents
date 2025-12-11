# Knowledge Distillation: The Understudy Pattern

> *"Genius is expensive. Routine should be cheap."*

This document extends B-gent's economic management to include **knowledge distillation**—training cheaper "student" models to replicate expensive "teacher" agent behavior for budget optimization.

> **Note**: This spec incorporates content from the former U-gent "Understudy" specification. The Understudy pattern belongs in B-gent because its primary value is *economic*—the ROI formula is the decision criterion.

---

## The Intelligence-Cost Paradox

| Agent | Capability | Cost/Call | Use Case |
|-------|------------|-----------|----------|
| Teacher (GPT-4, Claude) | High | $0.03+ | Complex reasoning |
| Student (Llama-8B, GPT-4o-mini) | Medium | $0.0002 | Routine tasks |

**Paradox**: The most capable agents are too expensive for infinite loops; the cheapest lack judgment.

**Solution**: Capture Teacher reasoning, distill it into Students.

---

## Derivation from Bootstrap

Distillation is **already derivable** from existing agents:

```
Distillation = Compose + Judge + Ground
```

| Capability | Bootstrap/Existing Agent |
|------------|-------------------------|
| Student training | `Compose` (teacher >> student) |
| Quality validation | `Judge` / V-gent |
| Cost tracking | B-gent economics |
| Drift detection | O-gent + V-gent |

**No new primitives needed**—distillation is an economic strategy, not a cognitive capability.

## Why Not U-gent?

An earlier proposal suggested "U-gent" (Understudy) as a separate genus. Analysis revealed:

1. **Heavy machinery** - ShadowObserver, StudentTrainer, StudentRouter add complexity without new primitives
2. **Economics, not cognition** - Distillation is a budget optimization strategy
3. **Overlaps existing agents** - O-gent (telemetry), V-gent (validation), C-gent (routing)

**Decision**: Merge distillation patterns into B-gent as an economic strategy.

## The Economics of Distillation

```
┌─────────────────────────────────────────────────────────────────┐
│                    DISTILLATION ECONOMICS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  BEFORE:                        AFTER:                          │
│  ┌───────────┐                  ┌───────────┐                   │
│  │ Teacher   │                  │ Teacher   │ (10% of calls)    │
│  │ (Claude)  │ ←── ALL ───      │ (Claude)  │ ← training only   │
│  │ $0.01/call│      calls       │ $0.01/call│                   │
│  └───────────┘                  └───────────┘                   │
│                                       │                          │
│                                       │ trains                   │
│                                       ▼                          │
│                                 ┌───────────┐                   │
│                                 │ Student   │ (90% of calls)    │
│                                 │ (Haiku)   │ ← production      │
│                                 │ $0.001/cal│                   │
│                                 └───────────┘                   │
│                                                                  │
│  Cost reduction: 10x for distillable tasks                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Distillation Components

### 1. Shadow Observer

Records teacher behavior for training data:

```python
@dataclass
class ShadowObserver:
    """
    Records teacher agent invocations for distillation training.

    Integration: Uses O-gent telemetry infrastructure.
    """

    # Storage for training examples
    examples: list[TrainingExample] = field(default_factory=list)

    async def observe(self, teacher: Agent, input: Any) -> Any:
        """Invoke teacher while recording the example."""
        output = await teacher.invoke(input)

        self.examples.append(TrainingExample(
            input=input,
            output=output,
            timestamp=datetime.now()
        ))

        return output

    def get_training_data(self) -> list[TrainingExample]:
        """Return accumulated training examples."""
        return self.examples.copy()
```

### 2. Student Factory

Creates distilled agents:

```python
@dataclass
class StudentFactory:
    """
    Creates student agents from training data.

    Students are cheaper models fine-tuned on teacher examples.
    """

    # Model configuration
    student_model: str = "claude-3-haiku"

    async def create_student(
        self,
        training_data: list[TrainingExample],
        task_description: str
    ) -> Agent:
        """
        Create a student agent from training data.

        Options:
        1. Few-shot prompting (cheapest, no fine-tuning)
        2. Distillation fine-tuning (best quality, requires API support)
        3. Prompt optimization (middle ground)
        """
        # Implementation depends on available APIs
        return FewShotStudent(
            examples=training_data[:10],  # Most representative
            model=self.student_model,
            task_description=task_description
        )
```

### 3. Quality Gate

Uses V-gent to validate student quality:

```python
@dataclass
class DistillationQualityGate:
    """
    Validates student quality before production use.

    Integration: Uses V-gent for validation.
    """

    v_gent: "V"
    min_agreement: float = 0.95  # 95% agreement with teacher

    async def validate_student(
        self,
        teacher: Agent,
        student: Agent,
        test_cases: list[Any]
    ) -> ValidationResult:
        """Validate student matches teacher on test cases."""
        agreements = 0

        for test_input in test_cases:
            teacher_output = await teacher.invoke(test_input)
            student_output = await student.invoke(test_input)

            verdict = await self.v_gent.validate(
                output={"teacher": teacher_output, "student": student_output},
                context=ValidationContext(
                    task_description="Student-teacher agreement check",
                    domain="distillation"
                )
            )

            if verdict.approved:
                agreements += 1

        agreement_rate = agreements / len(test_cases)
        return ValidationResult(
            passed=agreement_rate >= self.min_agreement,
            agreement_rate=agreement_rate
        )
```

### 4. Distillation Router

Routes to teacher or student based on confidence:

```python
@dataclass
class DistillationRouter:
    """
    Routes requests to teacher or student based on task.

    Integration: Uses C-gent conditional composition.
    """

    teacher: Agent
    students: dict[str, Agent] = field(default_factory=dict)  # task -> student
    fallback_to_teacher: bool = True

    async def invoke(self, task: str, input: Any) -> Any:
        """Route to appropriate agent."""
        student = self.students.get(task)

        if student:
            try:
                return await student.invoke(input)
            except Exception:
                if self.fallback_to_teacher:
                    return await self.teacher.invoke(input)
                raise

        return await self.teacher.invoke(input)
```

## B-gent Integration

Distillation is a **B-gent economic strategy**:

```python
@dataclass
class BudgetAwareDistillation:
    """
    B-gent extension for distillation economics.
    """

    b_gent: "B"
    shadow: ShadowObserver
    factory: StudentFactory
    quality_gate: DistillationQualityGate
    router: DistillationRouter

    async def optimize_for_budget(
        self,
        task: str,
        teacher: Agent,
        budget_target: float
    ) -> OptimizationResult:
        """
        Optimize task execution to meet budget target.

        Steps:
        1. Observe teacher (collect training data)
        2. Create student (distill)
        3. Validate quality (V-gent)
        4. Deploy if quality passes
        5. Monitor drift over time
        """
        # Check if distillation would help
        teacher_cost = await self.b_gent.estimate_cost(teacher, task)
        student_cost = teacher_cost * 0.1  # Assume 10x cheaper

        if teacher_cost <= budget_target:
            return OptimizationResult(
                strategy="no_change",
                reason="Already within budget"
            )

        # Collect training data
        examples = self.shadow.get_training_data()
        if len(examples) < 100:
            return OptimizationResult(
                strategy="collecting",
                reason=f"Need more examples ({len(examples)}/100)"
            )

        # Create and validate student
        student = await self.factory.create_student(examples, task)
        validation = await self.quality_gate.validate_student(
            teacher, student, examples[:20]
        )

        if not validation.passed:
            return OptimizationResult(
                strategy="fallback_teacher",
                reason=f"Student quality too low ({validation.agreement_rate:.0%})"
            )

        # Deploy student
        self.router.students[task] = student
        return OptimizationResult(
            strategy="distilled",
            cost_reduction=f"{teacher_cost / student_cost:.1f}x"
        )
```

## Drift Detection

Uses O-gent + V-gent to detect student drift:

```python
async def detect_drift(
    student: Agent,
    teacher: Agent,
    sample_input: Any,
    o_gent: "O",
    v_gent: "V"
) -> DriftReport:
    """
    Detect if student has drifted from teacher quality.

    Run periodically (via O-gent scheduled checks).
    """
    student_output = await student.invoke(sample_input)
    teacher_output = await teacher.invoke(sample_input)

    verdict = await v_gent.validate(
        output={"student": student_output, "teacher": teacher_output},
        context=ValidationContext(
            task_description="Drift detection",
            domain="distillation"
        )
    )

    # Log to O-gent
    await o_gent.log({
        "type": "distillation.drift_check",
        "agreement": verdict.approved,
        "confidence": verdict.confidence
    })

    return DriftReport(
        drifted=not verdict.approved,
        confidence=verdict.confidence
    )
```

## When to Distill

| Task Type | Distill? | Reason |
|-----------|----------|--------|
| Repetitive, well-defined | ✅ Yes | High ROI |
| Complex, nuanced | ❌ No | Quality loss |
| Rare, high-stakes | ❌ No | Not enough examples |
| Format conversion | ✅ Yes | Pattern-learnable |
| Creative generation | ⚠️ Maybe | Depends on constraints |

## The ROI Formula

```
         (Cost_T - Cost_S) × N_calls - Cost_Training
ROI = ─────────────────────────────────────────────────
                     Cost_Training

Break-Even Point:
              Cost_Training
BEP_calls = ─────────────────
            Cost_T - Cost_S
```

**Decision Rule**: If BEP < 1 week of projected volume, B-gent authorizes training investment.

## Implementation Phases (The Understudy Journey)

### Phase 1: The "Hitchhiker" (Passive Shadowing)
Wrapper on `Agent.invoke` that logs inputs/outputs to D-gent store. Does NOT train.
```python
shadowed_agent = distiller.shadow(teacher)
# All teacher calls now logged to corpus.jsonl
```

### Phase 2: The "Imposter" (Evaluation Mode)
Student runs in background for every request (fire-and-forget).
**Metric**: `AgreementRate`—How often does `Student(x) == Teacher(x)`?
When `AgreementRate > 95%` on validation set, enable the Switch.

### Phase 3: The "Switch" (Active Routing)
Router deployed. Traffic directed to Student, escalating only on high uncertainty.
System now saves money.

### Phase 4: The "Dreamer" (Synthetic Augmentation)
Teacher runs during off-peak hours to generate synthetic edge cases,
preemptively closing knowledge gaps before users encounter them.

## Technical Stack

| Component | Recommendation | Rationale |
|-----------|---------------|-----------|
| Student Model | Llama-3-8B-Instruct (4-bit) | Edge deployment, low cost |
| API Student | GPT-4o-mini | API-based distillation |
| Training | Unsloth or Torchtune | 2x faster training |
| Adapter Strategy | LoRA | Hot-swap skills instantly |

**LoRA Adapter Pattern**:
```
Base Model: Frozen Llama-3-8B
├── Skill A (SQL Generation): LoRA Adapter A
├── Skill B (Summarization):  LoRA Adapter B
└── Skill C (Code Review):    LoRA Adapter C
```

## Anti-Patterns

1. ❌ Distilling without validation (use V-gent quality gate)
2. ❌ Using student for critical decisions (keep teacher for high-stakes)
3. ❌ Ignoring drift (monitor with O-gent)
4. ❌ Creating separate "U-gent" genus (this is B-gent economics)

## Principles Alignment

| Principle | How Distillation Satisfies |
|-----------|---------------------------|
| **Tasteful** | Extends B-gent, doesn't create new genus |
| **Curated** | Selective distillation (not everything) |
| **Ethical** | Transparent cost optimization |
| **Composable** | Router integrates with any agent |
| **Generative** | Derivable from Compose + Judge |

## See Also

- [budget.md](budget.md) - B-gent core economics
- [../v-gents/](../v-gents/) - Quality validation
- [../o-gents/](../o-gents/) - Telemetry and monitoring
