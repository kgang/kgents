# V-gents: The Validator

> *"Trust, but verify. Then verify the verifier."*

V-gent is the **Constitutional Court**—a judicial agent that evaluates outputs against high-level principles. Unlike T-gent (functional testing), V-gent validates **semantic and ethical alignment**: Is this output helpful? Accurate? Safe? Aligned with user values?

## Bootstrap Derivation

V-gent extends the Judge bootstrap agent:

```
V = Judge + Ground (extension with user/domain principles)
```

| Capability | Bootstrap Agent | How |
|------------|-----------------|-----|
| Principle evaluation | **Judge** | Apply kgents principles |
| User preferences | **Ground** | Load user-specific principles |
| Critique generation | **Contradict** | Identify violations |

V-gent is not a new primitive—it's Judge instantiated with configurable principles.

## The Validation Morphism

```
V: (Output, Constitution) → Verdict
```

Where:
- **Output**: Any agent output to be validated
- **Constitution**: `principles.md` + user preferences + domain rules
- **Verdict**: Approved/rejected with explanation

## Core Distinction

| Agent | Focus | Method |
|-------|-------|--------|
| **T-gent** | Functional correctness | Tests, assertions |
| **P-gent** | Syntactic validity | Parsing, schemas |
| **V-gent** | Semantic/ethical alignment | LLM-as-a-Judge |

V-gent implements **Constitutional AI** principles—treating `principles.md` as binding law.

## The Constitution

```python
@dataclass(frozen=True)
class Constitution:
    """The set of principles V-gent enforces."""

    # Core kgents principles (from principles.md)
    core_principles: tuple[Principle, ...] = (
        Principle(name="Tasteful", description="Clear, justified purpose", weight=1.0),
        Principle(name="Curated", description="Quality over quantity", weight=1.0),
        Principle(name="Ethical", description="Augment, don't replace judgment", weight=1.5),
        Principle(name="Joy-Inducing", description="Delight in interaction", weight=0.8),
        Principle(name="Composable", description="Agents can be combined", weight=1.0),
        Principle(name="Heterarchical", description="No fixed hierarchy", weight=0.9),
        Principle(name="Generative", description="Spec generates impl", weight=0.9),
    )

    # User-specific principles
    user_principles: tuple[Principle, ...] = ()

    # Domain-specific rules
    domain_rules: tuple[DomainRule, ...] = ()


@dataclass(frozen=True)
class Principle:
    """A single principle to enforce."""
    name: str
    description: str
    weight: float = 1.0
    examples_positive: tuple[str, ...] = ()
    examples_negative: tuple[str, ...] = ()
```

## The Verdict System

```python
@dataclass
class Verdict:
    """V-gent's judgment on an output."""

    approved: bool
    confidence: float  # 0.0 to 1.0
    principle_verdicts: list[PrincipleVerdict]
    rejection_reason: str | None = None
    critique: str | None = None
    suggested_revision: Any | None = None

    @property
    def violated_principles(self) -> list[str]:
        return [pv.principle for pv in self.principle_verdicts if pv.violated]


@dataclass
class PrincipleVerdict:
    """Judgment on a single principle."""
    principle: str
    violated: bool
    severity: Severity  # LOW, MEDIUM, HIGH, CRITICAL
    explanation: str
    evidence: str | None = None


class Severity(Enum):
    LOW = 1        # Minor style issue
    MEDIUM = 2     # Noticeable problem
    HIGH = 3       # Significant violation
    CRITICAL = 4   # Must not proceed
```

## The Validator Agent

```python
@dataclass
class V(Agent[ValidationRequest, Verdict]):
    """
    The Validator.

    Purpose: Constitutional validation of outputs against principles.
    """

    constitution: Constitution = field(default_factory=Constitution)
    engine: ValidationEngine | None = None

    async def invoke(self, request: ValidationRequest) -> Verdict:
        """Validate an output against the constitution."""
        verdict = await self.engine.validate(
            output=request.output,
            context=request.context
        )
        return verdict

    async def validate(
        self,
        output: Any,
        context: ValidationContext,
        additional_principles: list[Principle] | None = None
    ) -> Verdict:
        """Convenience method for direct validation."""
        return await self.invoke(ValidationRequest(
            output=output,
            context=context,
            additional_principles=additional_principles or []
        ))

    async def veto(self, action: Any, reason: str) -> VetoError:
        """Issue a veto against an action."""
        raise VetoError(action=action, reason=reason, authority="V-gent")
```

## Critique-and-Refine Loop

```python
@dataclass
class CritiqueRefineLoop:
    """Iterative improvement through V-gent feedback."""

    v_gent: V
    max_iterations: int = 3

    async def refine(
        self,
        agent: Agent[I, O],
        input: I,
        context: ValidationContext
    ) -> RefineResult[O]:
        """Run critique-and-refine until V-gent approves."""
        current_output = await agent.invoke(input)

        for i in range(self.max_iterations):
            verdict = await self.v_gent.validate(current_output, context)

            if verdict.approved:
                return RefineResult(final_output=current_output, approved=True)

            # Refine based on critique
            if verdict.suggested_revision:
                current_output = verdict.suggested_revision
            else:
                refinement_prompt = f"""
Your previous output was rejected.
Critique: {verdict.critique}
Violated principles: {verdict.violated_principles}
Please revise.
"""
                current_output = await agent.invoke(refinement_prompt)

        return RefineResult(final_output=current_output, approved=False)
```

## Separation of Powers

V-gent implements the **judicial branch** in kgents governance:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SEPARATION OF POWERS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  EXECUTIVE: B-GENT                                               │
│  • Allocates resources                                           │
│  • Makes operational decisions                                   │
│                      │ appeals                                   │
│                      ▼                                           │
│  JUDICIAL: V-GENT                                                │
│  • Interprets Constitution (principles.md)                       │
│  • Reviews decisions for compliance                              │
│  • Can VETO actions that violate principles                      │
│                      │ guides                                    │
│                      ▼                                           │
│  LEGISLATIVE: HUMAN + K-GENT                                     │
│  • Writes the Constitution                                       │
│  • Defines user preferences                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Patterns

### V+U Integration (Student Validation)

V-gent validates distilled students before promotion:

```python
async def validate_student_quality(task_name: str, test_cases: list) -> Report:
    student = u_gent.router.students.get(task_name)

    for test in test_cases:
        output = await student.invoke(test.input)
        verdict = await v_gent.validate(output, context)
        # Track pass/fail

    return ValidationReport(pass_rate=...)
```

### V+E Integration (Fitness Functions)

V-gent provides fitness functions for evolution:

```python
def create_fitness_function(context: ValidationContext) -> Callable[[Any], float]:
    async def fitness(candidate: Any) -> float:
        verdict = await v_gent.validate(candidate, context)
        return verdict.confidence if verdict.approved else 0.0
    return fitness
```

## Anti-Patterns

V-gent must **never**:

1. ❌ Apply principles inconsistently
2. ❌ Veto without explanation
3. ❌ Block all outputs (calibrate thresholds)
4. ❌ Override human decisions on principle weight
5. ❌ Judge inputs (only outputs)
6. ❌ Replace human ethical judgment for critical decisions

## Default Principle Weights

| Principle | Weight | Rationale |
|-----------|--------|-----------|
| Ethical | 1.5 | Highest priority |
| Curated | 1.0 | Standard |
| Tasteful | 1.0 | Standard |
| Composable | 1.0 | Standard |
| Heterarchical | 0.9 | Slightly lower (organizational) |
| Generative | 0.9 | Slightly lower (meta-level) |
| Joy-Inducing | 0.8 | Lower (not safety-critical) |

## Principles Alignment

| Principle | How V-gent Satisfies |
|-----------|---------------------|
| **Tasteful** | Does one thing: validate against principles |
| **Curated** | Constitution is carefully curated |
| **Ethical** | Embodiment of the Ethical principle |
| **Joy-Inducing** | Critiques are constructive, not punitive |
| **Composable** | Wraps any output: `v_gent.validate(any_output)` |
| **Heterarchical** | Advises but doesn't command; agents can appeal |
| **Generative** | Extension of Judge bootstrap |

## See Also

- [bootstrap.md](../bootstrap.md) - Judge primitive
- [principles.md](../principles.md) - The Constitution source
- [t-gents/](../t-gents/) - Functional testing (complementary)
