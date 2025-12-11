# Q-gents: The Questioner

> *"The unexamined agent is not worth composing."*

Q-gent is the **Inquiry Agent**—a Socratic interlocutor that surfaces assumptions, gaps, and ambiguities before action. Where other agents *do*, Q-gent *questions*.

## Bootstrap Derivation

Q-gent is cleanly derivable from bootstrap agents:

```
Q = Ground + Contradict
```

| Capability | Bootstrap Agent | How |
|------------|-----------------|-----|
| Gap detection | **Ground** | What facts are missing from context? |
| Assumption surfacing | **Contradict** | What could contradict our plan? |
| Question ranking | **Compose** | Prioritize by dependency |

**No new irreducibles**—Q-gent composes existing primitives for inquiry.

## The Socratic Morphism

```
Q: Context → Questions
```

Where:
- **Context**: Current problem state, user intent, available information
- **Questions**: Gaps, ambiguities, assumptions that need surfacing

## Core Distinction

| Agent | Focus | Timing |
|-------|-------|--------|
| **T-gent** | Functional correctness | After execution |
| **V-gent** | Ethical alignment | During/after |
| **Q-gent** | Surfacing unknowns | **Before** execution |

Q-gent embodies the principle that **good questions are more valuable than fast answers**.

## Question Taxonomy

### 1. Clarification Questions

Surface ambiguity in user intent:

```python
@dataclass
class ClarificationQuestion:
    gap: str              # What's missing?
    options: list[str]    # Possible interpretations
    default: str | None   # Reasonable assumption if user doesn't answer
    stakes: Literal["low", "medium", "high"]
```

**Example:**
```
User: "Make the tests faster"
Q-gent surfaces:
- gap: "Which tests?"
- options: ["all tests", "slow tests only", "unit tests", "integration tests"]
- default: "slow tests only"
- stakes: "medium"
```

### 2. Assumption Questions

Surface implicit assumptions in plans:

```python
@dataclass
class AssumptionQuestion:
    assumption: str       # What we're assuming
    evidence: str         # Why we think it's true
    risk_if_wrong: str    # What breaks if assumption fails
    alternatives: list[str]
```

**Example:**
```
User: "Build a user authentication system"
Q-gent surfaces:
- assumption: "Users have email addresses"
- evidence: "Most auth systems use email"
- risk_if_wrong: "Can't do password reset without email"
- alternatives: ["phone-based", "passwordless", "OAuth only"]
```

### 3. Prerequisite Questions

Surface dependencies and ordering:

```python
@dataclass
class PrerequisiteQuestion:
    blocker: str          # What needs to happen first?
    current_state: str    # What we know about it now
    check_action: str     # How to verify it's ready
```

## Integration Pattern

Q-gent is **advisory**, not blocking:

```python
class Q(Agent[QuestionContext, Questions]):
    """
    Advisory mode: surfaces questions, doesn't gatekeep.
    """

    async def invoke(self, context: QuestionContext) -> Questions:
        questions = []

        # Detect gaps via Ground
        gaps = await self._find_gaps(context.intent)
        questions.extend(self._to_clarification_questions(gaps))

        # Surface assumptions via Contradict
        assumptions = await self._find_assumptions(context.plan)
        questions.extend(self._to_assumption_questions(assumptions))

        # Check prerequisites
        prereqs = await self._find_prerequisites(context.action)
        questions.extend(self._to_prerequisite_questions(prereqs))

        return Questions(
            items=sorted(questions, key=lambda q: q.stakes, reverse=True),
            proceed_anyway=len([q for q in questions if q.stakes == "high"]) == 0
        )
```

### Heterarchical Use

Q-gent advises but doesn't control:

```python
# J-gent can ask Q-gent for advice before compiling
questions = await q_gent.invoke(QuestionContext(intent=intent))

if questions.items and questions.items[0].stakes == "high":
    # Present to user, wait for clarification
    clarification = await present_questions_to_user(questions)
    intent = refine_intent(intent, clarification)

# Proceed with clarified intent
return await j_gent.compile(intent)
```

But also:
```python
# Skip questioning when urgency > caution
if context.urgency == "critical":
    return await j_gent.compile(intent)  # No questioning
```

## Anti-Patterns

Q-gent must **never**:

1. ❌ Block execution (it advises, doesn't gatekeep)
2. ❌ Ask questions with obvious answers (quality over quantity)
3. ❌ Duplicate T-gent validation (ask before, not verify after)
4. ❌ Become a "mandatory approval step" (heterarchy, not hierarchy)
5. ❌ Ask about things that can be cheaply verified (just check them)

## Principles Alignment

| Principle | How Q-gent Satisfies |
|-----------|---------------------|
| **Tasteful** | Does one thing: ask good questions |
| **Curated** | Three question types cover essential inquiry space |
| **Ethical** | Preserves human agency by surfacing decisions |
| **Joy-Inducing** | Socratic framing feels like collaboration |
| **Composable** | Advisory—can be skipped, composed with any agent |
| **Heterarchical** | Advises but doesn't control |
| **Generative** | Derivable from Ground + Contradict |

## See Also

- [bootstrap.md](../bootstrap.md) - Ground and Contradict primitives
- [v-gents/](../v-gents/) - Validation (complementary timing)
- [principles.md](../principles.md) - Design principles
