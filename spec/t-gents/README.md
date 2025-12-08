# T-gents: Test Agents Specification

**Theme**: Testing, Tooling, and Truthfulness

T-gents are agents explicitly designed for testing other agents, validating pipelines, and ensuring system reliability.

## Philosophy

1. **Testing is First-Class**: Test agents follow the same morphism principles as production agents
2. **Controlled Failure**: Deliberate failure modes enable validation of recovery mechanisms
3. **Compositional Testing**: Test agents compose with production agents via >> operator
4. **Observable Truth**: Testing reveals ground truth about system behavior

## Core T-gents

### FailingAgent: A → Error

Deliberately fails with configurable error patterns to test recovery strategies.

**Signature**: `FailingAgent[A, B](config: FailingConfig) :: A → Error`

**Use Cases**:
- Testing retry logic (fail N times, then succeed)
- Validating fallback strategies (consistent failures)
- Error memory pattern validation
- Pipeline resilience testing

**Configuration**:
```python
@dataclass
class FailingConfig:
    error_type: FailureType  # syntax|type|import|runtime|timeout|network
    fail_count: int  # -1 = always fail, N = fail N times then succeed
    error_message: str  # Custom error message
```

**Example**:
```python
# Fail twice with type errors, then succeed
failing = FailingAgent[Input, Output](
    FailingConfig(error_type=FailureType.TYPE, fail_count=2)
)

# Test retry strategy
for attempt in range(3):
    try:
        result = await failing.invoke(test_input)
        break  # Success!
    except Exception as e:
        # Retry with refined approach
```

### MockAgent: A → B (pre-configured)

Returns pre-configured mock outputs for fast testing without LLM calls.

**Signature**: `MockAgent[A, B](config: MockConfig) :: A → B`

**Use Cases**:
- Testing agent composition without LLM costs
- Validating pipeline behavior
- Fast iteration during development
- Performance benchmarking

**Configuration**:
```python
@dataclass
class MockConfig:
    output: Any  # Pre-configured output to return
    delay_ms: int = 0  # Simulated delay
```

**Example**:
```python
# Mock hypothesis generator
mock_hyp = MockAgent[HypothesisInput, HypothesisOutput](
    MockConfig(output=HypothesisOutput(hypotheses=["Test hypothesis"]))
)

result = await mock_hyp.invoke(any_input)
# Returns: HypothesisOutput(hypotheses=["Test hypothesis"])
```

## Composability

T-gents compose with production agents:

```python
# Test pipeline with deliberate failure
pipeline = FailingAgent[A, B](fail_config) >> RetryAgent >> SuccessValidator

# Mock expensive LLM call in pipeline
fast_pipeline = MockAgent[A, B](mock_config) >> ProcessB >> ValidateC
```

## Testing Principles

1. **Fail Fast**: Failures should be immediate and clear
2. **Fail Predictably**: Controlled failure modes, not random
3. **Fail Meaningfully**: Error messages guide debugging
4. **Recover Gracefully**: Test recovery, not just success paths

## Future T-gents

- **DelayAgent**: Adds configurable delays to test async behavior
- **CounterAgent**: Tracks invocation counts for verification
- **SpyAgent**: Records inputs/outputs for assertion
- **FlakyAgent**: Random failures to test resilience
- **TimeoutAgent**: Simulates timeout scenarios
- **ValidationAgent**: Asserts expected outputs

## Relationship to Other Agent Genera

- **E-gents**: T-gents test E-gents (evolution agents)
- **B-gents**: T-gents validate B-gents (hypothesis generation)
- **C-gents**: T-gents verify composability properties
- **K-gent**: T-gents ensure persona consistency

## Implementation Notes

T-gents must:
1. Implement `Agent[A, B]` protocol
2. Provide `name` property
3. Be deterministic (same input → same output/error)
4. Support reset() for test isolation
5. Be lightweight (minimal dependencies)

## Success Criteria

A T-gent is well-designed if:
- ✓ It reveals bugs that would otherwise be hidden
- ✓ It fails faster than production would
- ✓ It composes naturally with other agents
- ✓ It provides clear diagnostic information
- ✓ It enables confident refactoring
