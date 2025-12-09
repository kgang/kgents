# G-gent Implementation Plan

**Status**: Implementation Planning
**Date**: 2025-12-09
**Purpose**: Roadmap for implementing G-gent (The Grammarian) agent genus

---

## Executive Summary

This document outlines the implementation plan for **G-gent**, the Grammar agent genus that synthesizes Domain Specific Languages (DSLs) to facilitate safe, constrained agent communication.

### Key Value Propositions

1. **Safety Through Structure**: Constraints become grammatically impossible, not just forbidden
2. **Token Efficiency**: DSLs compress verbose natural language into dense protocols
3. **Composability**: Tongues integrate with existing P-gent, J-gent, F-gent infrastructure
4. **Discovery**: L-gent catalogs tongues for ecosystem-wide reuse

---

## Implementation Phases

### Phase 1: Core Types and Tongue Artifact

**Goal**: Define the foundational types and Tongue data structure

**Deliverables**:
1. `impl/claude/agents/g/types.py` - Core types
   - `Tongue` dataclass (frozen, hashable)
   - `GrammarLevel` enum (SCHEMA, COMMAND, RECURSIVE)
   - `GrammarFormat` enum (BNF, EBNF, LARK, PYDANTIC)
   - `ParserConfig` and `InterpreterConfig`
   - `ConstraintProof` for verification tracking
   - `Example` and `CounterExample`

2. `impl/claude/agents/g/tongue.py` - Tongue implementation
   - `parse()` method (delegates to P-gent)
   - `execute()` method (delegates to J-gent)
   - `validate()` method
   - `render()` method (AST → text)
   - Serialization (JSON, YAML)

3. `tests/agents/g/test_types.py` - Type tests
   - Immutability tests
   - Serialization round-trip tests
   - Validation tests

**Dependencies**: None (foundational)

**Estimated Effort**: Foundation work, creates reusable types

---

### Phase 2: Grammar Synthesis Engine

**Goal**: Implement the core G-gent reify() capability

**Deliverables**:
1. `impl/claude/agents/g/synthesis.py` - Grammar synthesis
   - `analyze_domain()` - Extract entities, operations, constraints
   - `synthesize_grammar()` - Generate BNF/EBNF from analysis
   - `_generate_schema()` - Level 1 (Pydantic)
   - `_generate_command_bnf()` - Level 2 (Verb-Noun)
   - `_generate_recursive_bnf()` - Level 3 (S-expression)

2. `impl/claude/agents/g/validation.py` - Grammar validation
   - `verify_unambiguous()` - Ambiguity detection
   - `verify_constraints()` - Constraint encoding verification
   - `verify_round_trip()` - parse → render → parse identity

3. `impl/claude/agents/g/grammarian.py` - Main G-gent class
   - `reify()` - Primary synthesis method
   - `refine()` - Grammar refinement on ambiguity
   - `crystallize()` - Finalize tongue artifact

4. `tests/agents/g/test_synthesis.py` - Synthesis tests
   - Domain analysis tests
   - Grammar generation tests per level
   - Constraint encoding tests

**Dependencies**: Phase 1

**Estimated Effort**: Core implementation, LLM-powered synthesis

---

### Phase 3: P-gent Integration

**Goal**: Integrate G-gent with P-gent parsing infrastructure

**Deliverables**:
1. `impl/claude/agents/g/parser_integration.py` - Parser integration
   - `generate_parser_config()` - Create ParserConfig from grammar
   - `create_parser()` - Instantiate P-gent parser for tongue
   - Level-specific configurations (regex, Lark, Pydantic)

2. Updates to `impl/claude/agents/p/` - P-gent enhancements
   - Support for G-gent-generated ParserConfig
   - Grammar-aware repair strategies
   - Confidence scoring based on grammar level

3. `tests/agents/g/test_parser_integration.py` - Integration tests
   - Parse valid DSL inputs
   - Reject invalid inputs
   - Repair malformed inputs

**Dependencies**: Phase 2, existing P-gent implementation

**Estimated Effort**: Integration work, may require P-gent enhancements

---

### Phase 4: J-gent Integration

**Goal**: Integrate G-gent with J-gent execution infrastructure

**Deliverables**:
1. `impl/claude/agents/g/interpreter_integration.py` - Interpreter integration
   - `generate_interpreter_config()` - Create InterpreterConfig
   - `bind_semantics()` - Map grammar productions to handlers
   - `create_interpreter()` - Instantiate J-gent interpreter

2. Updates to `impl/claude/agents/j/` - J-gent enhancements
   - Support for G-gent-generated InterpreterConfig
   - Sandbox execution for tongue interpreters
   - Entropy budget integration

3. `tests/agents/g/test_interpreter_integration.py` - Integration tests
   - Execute valid ASTs
   - Sandbox isolation tests
   - Entropy budget enforcement

**Dependencies**: Phase 3, existing J-gent implementation

**Estimated Effort**: Integration work, may require J-gent enhancements

---

### Phase 5: L-gent Integration

**Goal**: Enable tongue discovery and cataloging

**Deliverables**:
1. `impl/claude/agents/g/catalog_integration.py` - Catalog integration
   - `register_tongue()` - Register with L-gent
   - `find_tongue()` - Query tongues by domain/constraint
   - `check_compatibility()` - Verify tongue composition

2. Updates to `impl/claude/agents/l/` - L-gent enhancements
   - Support `EntityType.TONGUE`
   - Tongue-specific metadata indexing
   - Constraint-based search

3. `tests/agents/g/test_catalog_integration.py` - Integration tests
   - Registration tests
   - Discovery tests
   - Compatibility checking

**Dependencies**: Phase 4, existing L-gent implementation

**Estimated Effort**: Integration work

---

### Phase 6: F-gent Integration

**Goal**: Enable F-gent to use G-gent for artifact interfaces

**Deliverables**:
1. `impl/claude/agents/g/forge_integration.py` - Forge integration
   - `create_artifact_interface()` - Generate tongue for artifact
   - `embed_tongue_in_contract()` - Bundle tongue with contract

2. Updates to `impl/claude/agents/f/` - F-gent enhancements
   - Contract structure includes interface tongue
   - Artifact invocation via tongue.parse >> tongue.execute

3. `tests/agents/g/test_forge_integration.py` - Integration tests
   - Artifact with G-gent interface
   - Contract with tongue validation

**Dependencies**: Phase 5, existing F-gent implementation

**Estimated Effort**: Integration work

---

### Phase 7: Advanced Features

**Goal**: Implement advanced G-gent capabilities

**Deliverables**:
1. `impl/claude/agents/g/evolution.py` - Tongue evolution
   - `extend()` - Add operations to existing tongue
   - `restrict()` - Add constraints to existing tongue
   - `compose()` - Merge two tongues
   - `version()` - Manage tongue versioning

2. `impl/claude/agents/g/inference.py` - Grammar inference
   - `infer_from_examples()` - W-gent integration
   - `hypothesize_grammar()` - Pattern → Grammar
   - `refine_hypothesis()` - Iterative refinement

3. `impl/claude/agents/g/testing.py` - T-gent integration
   - `fuzz_tongue()` - Grammar-guided fuzzing
   - `property_test_tongue()` - Property-based testing
   - `adversarial_test()` - Security testing

4. `impl/claude/agents/g/dialectic.py` - H-gent integration
   - `detect_tongue_tension()` - Find conflicting tongues
   - `reconcile_tongues()` - Synthesize unified tongue

**Dependencies**: All previous phases

**Estimated Effort**: Advanced features, lower priority

---

## File Structure

```
impl/claude/agents/g/
├── __init__.py
├── types.py              # Core types (Tongue, configs, etc.)
├── tongue.py             # Tongue implementation
├── synthesis.py          # Grammar synthesis engine
├── validation.py         # Grammar validation
├── grammarian.py         # Main G-gent class
├── parser_integration.py # P-gent integration
├── interpreter_integration.py  # J-gent integration
├── catalog_integration.py      # L-gent integration
├── forge_integration.py        # F-gent integration
├── evolution.py          # Tongue evolution
├── inference.py          # Grammar inference
├── testing.py            # T-gent integration
└── dialectic.py          # H-gent integration

tests/agents/g/
├── __init__.py
├── test_types.py
├── test_tongue.py
├── test_synthesis.py
├── test_validation.py
├── test_grammarian.py
├── test_parser_integration.py
├── test_interpreter_integration.py
├── test_catalog_integration.py
├── test_forge_integration.py
├── test_evolution.py
├── test_inference.py
├── test_testing.py
└── test_dialectic.py
```

---

## Example Use Cases

### Use Case 1: Safe Calendar Agent

```python
# User intent
# "Calendar agent that can check and add, but never delete"

# Implementation
tongue = await g_gent.reify(
    domain="Calendar Management",
    constraints=["No deletes", "No overwrites"],
    level=GrammarLevel.COMMAND
)

# Generated grammar
# CMD ::= "CHECK" DATE | "ADD" EVENT
# EVENT ::= TIME DURATION TITLE

# Usage
result = tongue.parse("CHECK 2024-12-15")
# ParseResult(success=True, value=CheckCommand(date=2024-12-15))

result = tongue.parse("DELETE meeting")
# ParseResult(success=False, error="Unknown verb: DELETE")
```

### Use Case 2: Inter-Agent Protocol

```python
# Compress citation exchange between research agents

tongue = await g_gent.reify(
    domain="Citation Exchange",
    constraints=["Minimal tokens", "Preserve semantics"],
    level=GrammarLevel.SCHEMA
)

# Generated Pydantic model
class Citation(BaseModel):
    author: str
    year: int
    topic: str
    confidence: float = 1.0

# Usage
# Before: "I found a paper by Smith from 2020 about transformers with high confidence"
# After: Citation(author="Smith", year=2020, topic="transformers", confidence=0.95)
# Token savings: ~80%
```

### Use Case 3: Artifact Interface

```python
# F-gent creates artifact with G-gent interface

artifact = await f_gent.forge(
    intent="Summarize documents",
    interface_tongue=await g_gent.reify(
        domain="Summarization Commands",
        constraints=["Max 3 arguments", "Output format required"],
        level=GrammarLevel.COMMAND
    )
)

# Usage via DSL
result = artifact.invoke("SUMMARIZE doc.pdf FORMAT json LENGTH 200")
```

---

## Testing Strategy

### Unit Tests

- Type validation (immutability, serialization)
- Grammar synthesis (per level)
- Constraint encoding verification
- Round-trip parsing

### Integration Tests

- P-gent parsing with G-gent config
- J-gent execution with G-gent interpreter
- L-gent discovery of tongues
- F-gent artifact with G-gent interface

### Property Tests

- Round-trip: `parse(render(ast)) == ast`
- Constraint structural: Forbidden ops → parse failure
- Ambiguity: All inputs have unique parse

### Fuzz Tests

- Grammar-guided fuzzing via T-gent
- Adversarial input generation
- Security testing (injection attempts)

---

## Success Criteria

| Criterion | Metric | Target |
|-----------|--------|--------|
| **Constraint Crystallization** | % constraints that are structural | 100% |
| **Grammar Unambiguity** | Fuzz tests with unique parses | 100% |
| **Round-Trip Fidelity** | parse(render(ast)) == ast | 100% |
| **P-gent Integration** | Parse success with G-gent config | 95%+ |
| **J-gent Integration** | Execute success in sandbox | 95%+ |
| **Token Compression** | DSL vs natural language | 50%+ savings |
| **Test Coverage** | Line coverage | 80%+ |

---

## Risk Analysis

### Technical Risks

| Risk | Mitigation |
|------|------------|
| Grammar ambiguity | T-gent fuzz testing, LLM refinement |
| P-gent incompatibility | Early integration testing, config versioning |
| J-gent sandbox escape | Security review, restricted interpreter |
| LLM grammar hallucination | Validation pipeline, human review for critical |

### Integration Risks

| Risk | Mitigation |
|------|------------|
| Breaking existing P-gent | Backward compatible ParserConfig |
| Breaking existing J-gent | Backward compatible InterpreterConfig |
| L-gent schema changes | Migration scripts, versioned EntityType |

---

## Dependencies

### External Libraries

- **Lark**: Grammar parsing for Level 3 (recursive)
- **Pydantic**: Schema generation for Level 1
- **regex**: Pattern matching for Level 2

### Internal Dependencies

- **P-gent**: Parsing infrastructure
- **J-gent**: JIT execution
- **L-gent**: Cataloging
- **F-gent**: Artifact forging
- **T-gent**: Testing infrastructure

---

## Alignment with Kgents Principles

| Principle | How G-gent Aligns |
|-----------|-------------------|
| **Tasteful** | Minimal grammars, no kitchen-sink DSLs |
| **Curated** | Tongues validated before registration |
| **Ethical** | Constraints are structural, not runtime |
| **Joy-Inducing** | DSLs empower users with safe capabilities |
| **Composable** | Tongues are morphisms, integrate with ecosystem |
| **Heterarchical** | G-gent creates tools, doesn't own them |
| **Generative** | Spec generates implementation |

---

## Next Steps

1. **Immediate**: Review and approve implementation plan
2. **Phase 1**: Implement core types (foundation)
3. **Phase 2**: Implement synthesis engine (core capability)
4. **Phase 3-6**: Integration phases (ecosystem connection)
5. **Phase 7**: Advanced features (enhancement)

---

## References

- `spec/g-gents/README.md` - G-gent specification
- `spec/g-gents/grammar.md` - Grammar synthesis specification
- `spec/g-gents/tongue.md` - Tongue artifact specification
- `spec/g-gents/integration.md` - Integration patterns
- `spec/p-gents/README.md` - Parser agent specification
- `spec/j-gents/README.md` - JIT agent specification
- `spec/f-gents/contracts.md` - Contract specification
- `spec/l-gents/README.md` - Librarian agent specification
- `spec/principles.md` - Design principles
- `docs/cyborg_cognition_bootstrapping.md` - Cyborg cognition context

---

*"The implementation follows from the spec. G-gent's power lies in making constraints structural—what cannot be expressed cannot be executed."*
