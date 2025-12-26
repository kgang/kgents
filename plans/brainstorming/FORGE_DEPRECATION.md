# F-gent Forge API Deprecation

**Date**: 2025-12-25
**Status**: Deprecated (Available for backward compatibility)

## Summary

The F-gent Forge API (5-phase artifact generation loop) has been deprecated in favor of the new Flow API (streaming substrate with polynomial state machines).

## Architecture Evolution

### Old Architecture: Forge (5-Phase Loop)

```
Intent → Contract → Prototype → Validate → Crystallize
  ↓        ↓           ↓          ↓            ↓
Phase1   Phase2      Phase3    Phase4       Phase5
```

**Modules**:
- `agents.f.intent` - Intent parsing (NL → Intent)
- `agents.f.contract` - Contract synthesis (Intent → Contract)
- `agents.f.prototype` - Code generation (Contract → SourceCode)
- `agents.f.validate` - Testing & validation (SourceCode → Verdict)
- `agents.f.crystallize` - Artifact assembly (All → .alo.md)

**Philosophy**: Discrete 5-phase waterfall for artifact forging

### New Architecture: Flow (Streaming Substrate)

```
FlowConfig → FlowPolynomial → Flow → Stream[Events]
                                ↓
                         ChatFlow / ResearchFlow / CollaborationFlow
```

**Modules**:
- `agents.f.flow` - Core streaming substrate
- `agents.f.config` - FlowConfig (ChatConfig, ResearchConfig, etc.)
- `agents.f.polynomial` - State machines (mode-dependent transitions)
- `agents.f.state` - FlowState enum
- `agents.f.modalities/` - Chat, Research, Collaboration flows

**Philosophy**: Continuous streaming with polynomial state machines

## Migration Path

### Phase 1: Intent Parsing → FlowConfig

**Old**:
```python
from agents.f import parse_intent

intent = parse_intent("Create a chat agent that...")
```

**New**:
```python
from agents.f import ChatConfig

config = ChatConfig(
    max_turns=50,
    context_window=128_000,
    system_prompt="You are a helpful assistant"
)
```

### Phase 2: Contract Synthesis → Polynomial State Machines

**Old**:
```python
from agents.f import synthesize_contract

contract = synthesize_contract(intent, "ChatAgent")
```

**New**:
```python
from agents.f import CHAT_POLYNOMIAL, FlowState

# State machine handles contracts through transitions
# DORMANT → ACTIVE → STREAMING → PAUSED → COMPLETED
polynomial = CHAT_POLYNOMIAL
```

### Phase 3: Prototype Generation → ChatFlow

**Old**:
```python
from agents.f import generate_prototype

source = await generate_prototype(intent, contract)
```

**New**:
```python
from agents.f import ChatFlow

flow = ChatFlow(config)
# Code generation happens through streaming
async for event in flow.stream(user_input):
    print(event.value)
```

### Phase 4: Validation → Flow State Transitions

**Old**:
```python
from agents.f import validate

report = await validate(source, contract, intent)
```

**New**:
```python
# Validation happens through FlowState transitions
# ACTIVE → VALIDATING → ACTIVE (if pass) or ERROR (if fail)
# State machine handles validation internally
```

### Phase 5: Crystallization → Flow Events

**Old**:
```python
from agents.f import crystallize

artifact = crystallize(intent, contract, source)
```

**New**:
```python
# Artifacts emitted as Flow events
async for event in flow.stream(input):
    if event.event_type == "artifact":
        artifact = event.value
        # Handle artifact
```

## Why the Change?

1. **Streaming > Discrete**: Flow enables real-time interaction vs. batch processing
2. **State Machines > Phases**: Polynomial agents model mode-dependent behavior naturally
3. **Composability**: Flow agents compose via `>>` operator
4. **Modalities**: Chat/Research/Collaboration share the same substrate
5. **Simplicity**: 5 phases → 1 continuous flow with state transitions

## Backward Compatibility

The Forge API remains available for:
- **C-gent**: Contract law validation (`agents.c.contract_validator`)
- **J-gent**: Template instantiation (`agents.j.forge_integration`)
- **G-gent**: Interface embedding (`agents.g.forge_integration`)
- **L-gent**: Search integration (`agents.f.forge_with_search`)

These integrations will migrate to Flow API in future releases.

## Deprecation Timeline

- **2025-12-25**: Forge API marked deprecated, warnings added
- **TBD**: Integration migrations (C/J/G/L-gent → Flow)
- **TBD**: Forge API removal (major version bump)

## Current Usage

Files still using deprecated Forge API:

**Active Integrations**:
- `agents/c/contract_validator.py` - Uses `Contract` for validation
- `agents/j/forge_integration.py` - Uses `Contract`, `Intent` for templates
- `agents/g/forge_integration.py` - Uses `Contract` for interface embedding
- `agents/f/forge_with_search.py` - Uses `Intent`, `Contract` for L-gent search
- `agents/shared/fixtures_integration.py` - Test fixtures

**Tests** (OK to keep):
- `agents/f/_tests/test_intent.py`
- `agents/f/_tests/test_contract.py`
- `agents/f/_tests/test_crystallize.py`
- `agents/f/_tests/test_prototype.py`
- `agents/f/_tests/test_validate.py`
- `agents/f/_tests/test_f_forge_integration.py`
- `agents/f/_tests/test_reality_contracts.py`
- `agents/j/_tests/test_j_forge_integration.py`
- `agents/g/_tests/test_forge_integration.py`

## Recommendations

### For New Code

**Don't**:
```python
from agents.f import Intent, Contract, parse_intent, synthesize_contract
```

**Do**:
```python
from agents.f import ChatFlow, ChatConfig, FlowState
```

### For Existing Integrations

Keep using Forge API until migration guides are ready. The API is frozen (no new features) but stable.

### For Tests

Tests of deprecated modules are OK to keep. They ensure backward compatibility.

## Questions?

See:
- Migration guide: `impl/claude/agents/f/__init__.py` (module docstring)
- Flow API: `impl/claude/agents/f/flow.py`
- Modalities: `impl/claude/agents/f/modalities/`
- State machines: `impl/claude/agents/f/polynomial.py`
