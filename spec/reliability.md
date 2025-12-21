# Reliability Patterns Specification

> Reliability is not a single layer—it's a stack of composable fallbacks.

---

## Philosophy

LLM-based agents fail in novel ways: hallucinations, format errors, context overflow, semantic drift. Traditional retry logic is insufficient. The kgents reliability stack provides **defense in depth**.

**The Insight**: Each layer addresses a different failure mode. Composition creates antifragile systems.

---

## The Three-Layer Stack

```
┌─────────────────────────────────────────────────────────┐
│                 LAYER 1: PREVENTION                      │
│            (Prompt Engineering + Pre-flight)             │
├─────────────────────────────────────────────────────────┤
│                 LAYER 2: DETECTION                       │
│            (Parsing + Validation + Type Checking)        │
├─────────────────────────────────────────────────────────┤
│                 LAYER 3: RECOVERY                        │
│            (Retry + Fallback + Learning)                 │
└─────────────────────────────────────────────────────────┘
```

---

## Layer 1: Prevention (Prompt Engineering)

> Prevent errors by giving the LLM better information.

### PreFlightChecker

Validate module health BEFORE LLM invocation:

```python
@dataclass
class PreFlightResult:
    can_proceed: bool
    warnings: list[str]
    blockers: list[str]
    suggested_context: dict

class PreFlightChecker:
    """
    Validate prerequisites before expensive LLM calls.
    """

    async def check(self, request: AgentRequest) -> PreFlightResult:
        blockers = []
        warnings = []

        # Check context size
        if request.context_tokens > self.max_context:
            blockers.append(f"Context exceeds limit: {request.context_tokens}")

        # Check required fields
        for field in self.required_fields:
            if not getattr(request, field, None):
                blockers.append(f"Missing required field: {field}")

        # Check rate limits
        if self.rate_limiter.would_exceed(request):
            warnings.append("Approaching rate limit")

        return PreFlightResult(
            can_proceed=len(blockers) == 0,
            warnings=warnings,
            blockers=blockers,
            suggested_context=self.build_context(request)
        )
```

### PromptContext

Enrich prompts with relevant context:

```python
@dataclass
class PromptContext:
    """Rich context for better LLM responses."""

    # Type information
    input_schema: dict          # Expected input structure
    output_schema: dict         # Expected output structure

    # Examples
    few_shot_examples: list     # Successful input/output pairs

    # Error patterns
    common_errors: list[str]    # "Don't do X because..."
    recovery_hints: list[str]   # "If you see X, try Y"

    # Domain context
    terminology: dict           # Domain-specific vocabulary
    constraints: list[str]      # Hard requirements
```

**Goal**: Prevent errors by giving the LLM everything it needs to succeed.

---

## Layer 2: Detection (Parsing & Validation)

> Detect malformed outputs before they propagate.

### Multi-Strategy Parsing

```python
class MultiStrategyParser:
    """
    Try multiple parsing strategies with fallbacks.
    """

    strategies: list[ParsingStrategy] = [
        JSONExtractStrategy(),      # Extract JSON from markdown
        YAMLFallbackStrategy(),     # Try YAML if JSON fails
        RegexExtractionStrategy(),  # Pattern-based extraction
        LLMRepairStrategy(),        # Ask LLM to fix its output
    ]

    async def parse(self, raw_output: str, schema: Type[T]) -> T | ParseError:
        errors = []

        for strategy in self.strategies:
            try:
                result = await strategy.parse(raw_output, schema)
                if result is not None:
                    return result
            except ParseError as e:
                errors.append((strategy.name, e))
                continue

        return ParseError(
            message="All parsing strategies failed",
            attempts=errors,
            raw_output=raw_output
        )
```

### Schema Validation (Fast Path)

```python
class SchemaValidator:
    """
    Pre-type-checker validation for quick rejection.
    """

    async def validate(self, data: dict, schema: Type[T]) -> ValidationResult:
        errors = []

        # Required fields
        for field in schema.__required_keys__:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # Type checks (shallow)
        for field, expected_type in schema.__annotations__.items():
            if field in data and not isinstance(data[field], expected_type):
                errors.append(f"Type mismatch: {field}")

        # Custom validators
        for validator in self.custom_validators:
            result = await validator.check(data)
            if not result.valid:
                errors.extend(result.errors)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors
        )
```

**Goal**: Detect malformed outputs quickly and cheaply.

---

## Layer 3: Recovery (Retry & Fallback)

> Recover gracefully, learn from failures.

### RetryStrategy (Failure-Aware)

```python
@dataclass
class RetryConfig:
    max_attempts: int = 3
    backoff_base: float = 1.0
    backoff_max: float = 30.0
    failure_context: bool = True  # Include failure info in retry

class RetryStrategy:
    """
    Intelligent retry with failure-aware refinement.
    """

    async def execute(
        self,
        agent: Agent[A, B],
        input: A,
        config: RetryConfig
    ) -> B | RetryExhausted:
        attempts = []

        for attempt in range(config.max_attempts):
            try:
                # Add failure context if available
                enriched_input = input
                if config.failure_context and attempts:
                    enriched_input = self.add_failure_context(input, attempts)

                result = await agent.invoke(enriched_input)
                return result

            except AgentError as e:
                attempts.append(AttemptRecord(
                    attempt=attempt,
                    error=e,
                    timestamp=datetime.now()
                ))

                # Exponential backoff
                delay = min(
                    config.backoff_base * (2 ** attempt),
                    config.backoff_max
                )
                await asyncio.sleep(delay)

        return RetryExhausted(attempts=attempts)

    def add_failure_context(self, input: A, attempts: list) -> A:
        """Enrich input with information about previous failures."""
        return FailureAwareInput(
            original=input,
            previous_errors=[a.error.message for a in attempts],
            hint=f"Previous {len(attempts)} attempts failed. Avoid: {attempts[-1].error.category}"
        )
```

### FallbackStrategy (Progressive Simplification)

```python
class FallbackStrategy:
    """
    Progressive simplification when primary approach fails.
    """

    fallback_chain: list[Agent] = [
        primary_agent,          # Full capability
        simplified_agent,       # Reduced capability
        cached_agent,           # Use cached results
        ground_agent,           # Return safe default
    ]

    async def execute(self, input: A) -> B:
        for agent in self.fallback_chain:
            try:
                result = await agent.invoke(input)
                return result
            except AgentError:
                continue

        # Final fallback: Ground (safe default)
        return self.ground_response(input)
```

### ErrorMemory (Learning from Failures)

```python
class ErrorMemory:
    """
    Track failure patterns to improve future attempts.
    """

    patterns: dict[str, ErrorPattern] = {}

    def record(self, error: AgentError, context: dict):
        """Record a failure for pattern analysis."""
        key = self.categorize(error)

        if key not in self.patterns:
            self.patterns[key] = ErrorPattern(category=key)

        self.patterns[key].occurrences.append(
            Occurrence(error=error, context=context, timestamp=datetime.now())
        )

    def get_avoidance_hints(self, context: dict) -> list[str]:
        """Get hints based on similar past failures."""
        hints = []
        for pattern in self.patterns.values():
            if pattern.matches_context(context):
                hints.append(pattern.avoidance_hint)
        return hints

    def is_known_failure_mode(self, error: AgentError) -> bool:
        """Check if this error matches a known pattern."""
        key = self.categorize(error)
        return key in self.patterns and self.patterns[key].frequency > 3
```

---

## Fallback Composition

```python
# Happy path
pipeline = f >> g >> h

# With reliability stack
reliable_pipeline = Fix(
    Retry(
        Fallback(f, f_simple),
        max_attempts=3
    ),
    until_stable
) >> g >> h
```

---

## Integration Patterns

### Full Stack Example

```python
class ReliableAgent(Agent[A, B]):
    """
    Agent wrapped with full reliability stack.
    """

    def __init__(
        self,
        inner: Agent[A, B],
        preflight: PreFlightChecker,
        parser: MultiStrategyParser,
        retry: RetryStrategy,
        fallback: FallbackStrategy,
        memory: ErrorMemory
    ):
        self.inner = inner
        self.preflight = preflight
        self.parser = parser
        self.retry = retry
        self.fallback = fallback
        self.memory = memory

    async def invoke(self, input: A) -> B:
        # Layer 1: Prevention
        preflight = await self.preflight.check(input)
        if not preflight.can_proceed:
            return self.fallback.ground_response(input)

        # Enrich with avoidance hints
        hints = self.memory.get_avoidance_hints(input)
        enriched = self.enrich_input(input, preflight.suggested_context, hints)

        # Layer 3: Retry with Layer 2 validation
        async def attempt(inp):
            raw = await self.inner.invoke(inp)
            return await self.parser.parse(raw, self.output_schema)

        try:
            result = await self.retry.execute(attempt, enriched)
            return result
        except RetryExhausted as e:
            self.memory.record(e.last_error, {"input": input})
            return await self.fallback.execute(input)
```

---

## Anti-Patterns

- **Single point of failure**: One retry isn't a strategy
- **Silent swallowing of errors**: Log, record, learn
- **Retry without learning**: Same input → same failure
- **Fallback that breaks composition**: Fallback output must match expected type
- **Optimistic parsing**: Always validate, never assume
- **Ignoring partial failures**: Track degraded service

---

## Metrics

Track these to measure reliability:

| Metric | Description | Target |
|--------|-------------|--------|
| First-attempt success rate | % of requests succeeding without retry | > 90% |
| Retry success rate | % of retried requests eventually succeeding | > 95% |
| Fallback trigger rate | % of requests hitting fallback chain | < 5% |
| Ground response rate | % of requests returning safe default | < 1% |
| Mean recovery time | Average time to recover from failure | < 10s |

---

## See Also

- [testing.md](testing.md) - T-gents for reliability testing
- [bootstrap.md](bootstrap.md) - Fix idiom for iteration
