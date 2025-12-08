# kgents Test Suite

Organized test suite for the kgents reference implementation.

## Structure

```
tests/
├── agents/          # Agent implementation tests
│   ├── e_gents/            # E-gents (evolution agents)
│   │   └── test_demo.py    # Demo tests
│   ├── j_gents/            # J-gents (judgment agents)
│   │   ├── test_phase3.py  # JIT compilation tests
│   │   └── test_phase4.py  # Advanced judgment tests
│   ├── t_gents/            # T-gents (testing agents)
│   │   └── test_phase3.py  # Type IV critics tests
│   └── test_t_gents.py     # Core T-gents tests
├── evolution/       # Meta-evolution pipeline tests
│   └── test_metrics.py     # Pipeline metrics & performance
├── layers/          # E-gents architectural layer tests
│   ├── test_prompt_layer.py   # Phase 2.5a: Prompt engineering
│   ├── test_parsing_layer.py  # Phase 2.5b: Parsing & validation
│   └── test_recovery_layer.py # Phase 2.5c: Retry & fallback
└── utils/           # Utility tests
    ├── test_ast_utils.py          # AST manipulation utilities
    └── test_regression_validator.py # Regression validation
```

## Running Tests

### Run all tests
```bash
# Using uv (recommended)
cd impl/claude
uv run pytest

# Or from workspace root
uv run pytest impl/claude/tests/
```

### Run specific test suites
```bash
# Test T-gents agents only
uv run pytest tests/agents/

# Test evolution pipeline
uv run pytest tests/evolution/

# Test E-gents layers
uv run pytest tests/layers/

# Test specific file
uv run pytest tests/agents/test_t_gents.py
```

### Run with coverage
```bash
uv run pytest --cov=agents --cov=bootstrap --cov=runtime --cov-report=term-missing
```

### Run with verbose output
```bash
uv run pytest -v
```

## CI/CD

Tests run automatically via GitHub Actions on:
- Push to `main`
- Pull requests to `main`

The CI pipeline includes:
- **Test**: Run full test suite on Python 3.11, 3.12, 3.13
- **Lint**: Run ruff format check and lint
- **Coverage**: Generate coverage reports

See `.github/workflows/ci.yml` for details.

## Writing Tests

### Test Conventions
- Use `test_*.py` naming for test files
- Use `test_*` naming for test functions
- Use `Test*` naming for test classes
- All tests should be async-compatible (pytest-asyncio)

### Example Test
```python
import pytest
from agents.t import MockAgent, MockConfig

async def test_mock_agent():
    """Test MockAgent returns configured response."""
    agent = MockAgent(MockConfig(response="test"))
    result = await agent.invoke("input")
    assert result == "test"
```

## Test Categories

### Agent Tests (`tests/agents/`)
Tests for specific agent implementations:
- **E-gents** (`e_gents/`): Evolution agents
  - `test_demo.py`: Demo and integration tests
- **J-gents** (`j_gents/`): Judgment agents
  - `test_phase3.py`: JIT compilation, MetaArchitect, Chaosmonger
  - `test_phase4.py`: Advanced judgment capabilities
- **T-gents** (`t_gents/`): Testing agents
  - `test_t_gents.py`: Core testing agents (Mock, Fixture, Failing, Spy)
  - `test_phase3.py`: Type IV Critics (Judge, Property, Oracle)

### Evolution Tests (`tests/evolution/`)
Tests for the meta-evolution system:
- Pipeline execution and metrics
- Hypothesis generation
- Experiment validation
- Sublation and incorporation

### Layer Tests (`tests/layers/`)
Tests for E-gents architectural layers:
- **Prompt Layer**: PreFlight checking, context building
- **Parsing Layer**: Response parsing, validation, repair
- **Recovery Layer**: Retry strategies, fallback, error memory

### Utility Tests (`tests/utils/`)
Tests for utility modules:
- **AST Utils**: AST parsing and manipulation for code generation
- **Regression Validator**: Regression testing framework
