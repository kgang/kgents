# Probe Service

> *"The laws hold, or they don't. No middle ground."*

Fast categorical law checks and Crown Jewel health probes (Phase 4 of Claude Code CLI integration strategy).

## Overview

The Probe service implements quick, cheap verification checks for:
- **Categorical Laws**: Identity, associativity, coherence
- **Health Checks**: Crown Jewel availability and basic functionality
- **Budget Tracking**: Resource consumption monitoring

## Philosophy

- **FAST**: No LLM calls for basic checks
- **CHEAP**: Only emit witness marks on FAILURE
- **CI-Friendly**: Exit code 0 = pass, 1 = fail

## CLI Usage

### Quick Health Check (kp alias)

```bash
# Check all Crown Jewels
kp health

# Check specific jewel
kp health --jewel brain

# JSON output for automation
kp health --all --json
```

### Full Command Interface

```bash
# Health probes
kg probe health --all
kg probe health --jewel <brain|witness|kblock|sovereign>

# Law probes (TODO: implement tool loading)
kg probe identity --target <target>
kg probe associativity --pipeline <pipeline>
kg probe coherence --context <context>

# Budget probes (TODO: implement harness loading)
kg probe budget --harness <harness>
```

## Programmatic Usage

### Health Checks

```python
from services.probe import HealthProbe

probe = HealthProbe()

# Check all jewels
results = await probe.check_all()
for result in results:
    print(f"{result.name}: {'✓' if result.passed else '✗'}")

# Check specific jewel
result = await probe.check_component("brain")
assert result.passed
```

### Law Verification

```python
from services.probe import IdentityProbe, AssociativityProbe

# Identity law: Id >> f == f == f >> Id
identity_probe = IdentityProbe()
result = await identity_probe.check(tool, test_input)
assert result.passed

# Associativity law: (f >> g) >> h == f >> (g >> h)
assoc_probe = AssociativityProbe()
result = await assoc_probe.check(tool_f, tool_g, tool_h, test_input)
assert result.passed
```

### Budget Tracking

```python
from services.probe import BudgetProbe

probe = BudgetProbe()

# Check harness budget
result = await probe.check_harness(void_harness)
if result.failed:
    print(f"Budget exhausted: {result.details}")

# Check token budget
result = await probe.check_token_budget(
    used=950,
    total=1000,
    threshold=0.1
)
```

## Current Status

### Implemented ✓
- [x] Probe types (ProbeResult, ProbeStatus, ProbeType)
- [x] Health probes for all Crown Jewels
- [x] Budget probes (harness + token tracking)
- [x] Law probe infrastructure (identity, associativity, coherence)
- [x] CLI handler with human-readable and JSON output
- [x] `kp` alias for quick health checks
- [x] Comprehensive test suite (24 tests passing)

### TODO
- [ ] Dynamic tool loading for identity/associativity probes
- [ ] Pipeline parsing for composition verification
- [ ] Harness instance loading for budget probes
- [ ] Integration with CI/CD pipelines
- [ ] Trust level probes

## Architecture

```
services/probe/
├── __init__.py          # Public API
├── types.py             # ProbeResult, ProbeStatus, ProbeType
├── laws.py              # Identity, associativity, coherence probes
├── health.py            # Crown Jewel health checks
├── budget.py            # Budget tracking probes
└── _tests/              # Test suite (24 tests)
    ├── test_types.py
    ├── test_laws.py
    ├── test_health.py
    └── test_budget.py
```

## Integration

### CLI Registration

- Command: `protocols.cli.handlers.probe_thin:cmd_probe`
- Alias: `kp` → `protocols.cli.kp:main`
- Registered in: `protocols.cli.hollow:COMMAND_REGISTRY`

### Witness Integration

Probes only emit marks on FAILURE:

```python
if result.failed:
    mark = Mark.from_thought(
        content=f"Probe {result.name} FAILED",
        source="probe",
        tags=("probe", "failure", result.probe_type.value),
    )
```

## See Also

- `brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md` - Phase 4 specification
- `impl/claude/services/categorical/probes.py` - LLM-based monad/sheaf probes
- `impl/claude/services/tooling/base.py` - Tool category laws
- `docs/systems-reference.md` - Crown Jewel inventory
