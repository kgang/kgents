# Composition

Chain agents together with the `>>` operator - category theory in action.

## The >> Operator

Agents compose. Given:

```
f: Agent[A, B]
g: Agent[B, C]
```

Then `f >> g` creates a new agent:

```
Agent[A, C]
```

This is the heart of functional agent design.

## Basic Example

```python
from bootstrap.types import Agent

class DoubleAgent(Agent[int, int]):
    @property
    def name(self) -> str:
        return "double"

    async def invoke(self, input: int) -> int:
        return input * 2

class StringifyAgent(Agent[int, str]):
    @property
    def name(self) -> str:
        return "stringify"

    async def invoke(self, input: int) -> str:
        return f"Result: {input}"

# Compose them
double = DoubleAgent()
stringify = StringifyAgent()
pipeline = double >> stringify

# The pipeline is itself an agent!
result = await pipeline.invoke(21)
# -> "Result: 42"

print(pipeline.name)  # (double >> stringify)
```

## Key Insight: Composition Creates New Agents

The `>>` operator doesn't just chain functions. It creates a **new agent** that:

- Runs `f`, then `g` on `f`'s output
- Has its own `name` (automatically generated from component names)
- Is itself composable (can be used in further compositions)

```python
# pipeline is an Agent[int, str]
# You can compose it further
uppercase = UppercaseAgent()  # Agent[str, str]
full_pipeline = pipeline >> uppercase  # Agent[int, str]
```

## The Category Laws

Agents form a **category**. This means they satisfy three laws:

### 1. Identity Law

There exists an identity agent that does nothing:

```python
from bootstrap.types import Agent
from typing import TypeVar, Generic

T = TypeVar("T")

class IdentityAgent(Agent[T, T], Generic[T]):
    @property
    def name(self) -> str:
        return "identity"

    async def invoke(self, input: T) -> T:
        return input

identity: IdentityAgent[int] = IdentityAgent()
double = DoubleAgent()

# id >> f = f
result1 = await (identity >> double).invoke(10)  # 20
# f >> id = f
result2 = await (double >> identity).invoke(10)  # 20
# f alone
result3 = await double.invoke(10)  # 20

# All three are equal!
assert result1 == result2 == result3
```

### 2. Associativity Law

Grouping doesn't matter - composition is associative:

```python
class AddOneAgent(Agent[int, int]):
    @property
    def name(self) -> str:
        return "add-one"

    async def invoke(self, input: int) -> int:
        return input + 1

double = DoubleAgent()
add_one = AddOneAgent()
stringify = StringifyAgent()

# (f >> g) >> h
left = (double >> add_one) >> stringify
# f >> (g >> h)
right = double >> (add_one >> stringify)

# Both produce the same result
result_left = await left.invoke(5)   # "Result: 11"
result_right = await right.invoke(5)  # "Result: 11"

assert result_left == result_right
```

This means you can **build pipelines however you like** and get the same result.

### 3. Composition Law

If `f: A → B` and `g: B → C`, then `f >> g: A → C`.

The types must align:

```python
# Valid: output of double (int) matches input of stringify (int)
pipeline = double >> stringify  # Agent[int, str]

# Invalid: type mismatch
# pipeline = stringify >> double  # Error! str ≠ int
```

## Why This Matters

Category laws give you **guarantees** about composition:

### 1. Build Big from Small

```python
# Start with simple agents
validate = ValidateInput()      # Agent[str, str | None]
sanitize = SanitizeText()       # Agent[str, str]
analyze = AnalyzeContent()      # Agent[str, Analysis]
summarize = CreateSummary()     # Agent[Analysis, str]
format_output = FormatMarkdown()  # Agent[str, str]

# Compose into a complex pipeline
full_pipeline = (
    validate >>
    sanitize >>
    analyze >>
    summarize >>
    format_output
)

# The pipeline is predictable because of category laws
```

### 2. Reuse Components

```python
# Define once
strip = StripWhitespace()       # Agent[str, str]
lowercase = Lowercase()         # Agent[str, str]
remove_punct = RemovePunct()    # Agent[str, str]

# Reuse in different pipelines
sanitize = strip >> lowercase >> remove_punct

# Use sanitize in multiple contexts
user_input_pipeline = sanitize >> validate >> process
search_pipeline = sanitize >> tokenize >> index
```

### 3. Test Independently

```python
# Test each agent in isolation
async def test_double():
    double = DoubleAgent()
    assert await double.invoke(5) == 10

async def test_stringify():
    stringify = StringifyAgent()
    assert await stringify.invoke(42) == "Result: 42"

# Composition guarantees correct behavior when combined
# If both tests pass, double >> stringify will work!
```

### 4. Reason Mathematically

Category laws let you **refactor with confidence**:

```python
# These are GUARANTEED to be equivalent:
pipeline1 = (a >> b) >> (c >> d)
pipeline2 = a >> (b >> c) >> d
pipeline3 = ((a >> b) >> c) >> d

# No surprises. No hidden behavior.
```

## Type Safety

TypeScript-style type checking helps catch errors at edit time:

```python
# mypy will catch type mismatches
double: Agent[int, int] = DoubleAgent()
stringify: Agent[int, str] = StringifyAgent()
uppercase: Agent[str, str] = UppercaseAgent()

# Valid
good = double >> stringify >> uppercase  # Agent[int, str]

# Invalid - mypy error!
# bad = double >> uppercase  # Error: int ≠ str
```

## Real-World Example

```python
from dataclasses import dataclass
from bootstrap.types import Agent

@dataclass
class User:
    email: str
    raw_input: str

@dataclass
class CleanInput:
    text: str
    user_email: str

@dataclass
class Analysis:
    sentiment: str
    topics: list[str]
    confidence: float

class ExtractText(Agent[User, CleanInput]):
    @property
    def name(self) -> str:
        return "extract-text"

    async def invoke(self, input: User) -> CleanInput:
        return CleanInput(
            text=input.raw_input.strip(),
            user_email=input.email
        )

class AnalyzeText(Agent[CleanInput, Analysis]):
    @property
    def name(self) -> str:
        return "analyze"

    async def invoke(self, input: CleanInput) -> Analysis:
        # Imagine calling an LLM here
        return Analysis(
            sentiment="positive",
            topics=["kgents", "agents"],
            confidence=0.92
        )

class FormatReport(Agent[Analysis, str]):
    @property
    def name(self) -> str:
        return "format-report"

    async def invoke(self, input: Analysis) -> str:
        return f"Sentiment: {input.sentiment}\nTopics: {', '.join(input.topics)}"

# Compose the full pipeline
analyze_user_input = ExtractText() >> AnalyzeText() >> FormatReport()

# Use it
user = User(email="alice@example.com", raw_input=" I love kgents! ")
report = await analyze_user_input.invoke(user)
# -> "Sentiment: positive\nTopics: kgents, agents"
```

## What's Next?

You've learned:

- Use `>>` to chain agents together
- Composition creates new agents (not just chains)
- Category laws: identity, associativity, composition
- Type safety catches errors early

**Next step**: Learn about functors - lifting agents to new contexts.

[:octicons-arrow-right-24: Explore Functors](functors.md)

## Exercises

1. **Chain three agents**: Create `double >> add_one >> stringify` and test it
2. **Verify associativity**: Prove `(a >> b) >> c = a >> (b >> c)` with your own agents
3. **Build a text processing pipeline**: `strip >> lowercase >> remove_punctuation >> word_count`

## Run the Example

```bash
python -m impl.claude.agents.examples.composed_pipeline
```

## Full Source

View the complete source code:
[impl/claude/agents/examples/composed_pipeline.py](https://github.com/kentgang/kgents/blob/main/impl/claude/agents/examples/composed_pipeline.py)
