# F-gents: Forge Agents

**Genus**: F (Forge)
**Theme**: Permanent artifact synthesis from natural language intent
**Motto**: *"Intent crystallizes into artifact; contracts enable composition"*

## Overview

F-gents are agents that **transmute natural language intent into permanent software artifacts**. Unlike J-gents (ephemeral, runtime JIT compilation), F-gents produce **durable, versioned, composable agents** that persist in the ecosystem.

The distinction:
- **J-gents**: Improvisational jazz—ephemeral solutions compiled at runtime, discarded after use
- **F-gents**: Classical composition—permanent structures engineered once, reused forever

## Philosophy

> "An artifact is intent made permanent; a contract is the promise it keeps."

F-gents embody three core commitments:

### 1. Intent-Driven Creation

**Natural language is the source of truth.**

The creator expresses *what* they want (purpose, behavior, constraints) in human terms. The F-gent translates this into executable form while preserving the original intent as documentation.

```
Intent → Analysis → Contract → Implementation → Artifact
```

### 2. Contract-First Design

**Interfaces precede implementations.**

Before generating agent code, F-gents synthesize the *contract*—the protocol that defines how the agent composes with others. This ensures artifacts are **composable by construction**.

Contracts specify:
- **Type signatures**: What inputs/outputs flow through the agent
- **Behavioral invariants**: What guarantees the agent promises
- **Semantic intent**: Why this interface exists (for human understanding)

### 3. Living Artifacts

**Artifacts evolve while preserving intent.**

F-gents don't just generate code; they create **living documents** that interweave:
- **Intent** (human-editable natural language)
- **Contracts** (machine-verified protocols)
- **Implementation** (auto-generated, frozen)
- **Examples** (test cases driving validation)

When the environment changes (APIs evolve, requirements shift), F-gents can **re-forge** artifacts from the original intent while adapting to new constraints.

## Core Concepts

### The Artifact: Agent Living Object (ALO)

F-gents produce `.alo.md` files—hybrid documents that are simultaneously:
- **Specification**: Human-readable intent and constraints
- **Contract**: Machine-readable interface definitions
- **Implementation**: Executable code
- **Test Suite**: Validation examples

Structure:
```markdown
---
# Metadata (versioning, lineage, status)
---

# 1. THE INTENT (Human/Architect Vision)
Natural language description of purpose, tone, directives

# 2. THE CONTRACT (Interface & Invariants)
- Type signatures
- Behavioral guarantees
- Validation rules

# 3. THE EXAMPLES (Test-Driven Validation)
Input/output pairs demonstrating correct behavior

# 4. THE IMPLEMENTATION (Auto-Generated)
WARNING: DO NOT EDIT DIRECTLY
Code synthesized by F-gent from Intent + Contract
```

### The Forge Loop

F-gents iterate through phases to crystallize artifacts:

#### Phase 1: Understand (Intent Analysis)
**Morphism**: `NaturalLanguage → (Intent, Constraints, Dependencies)`

- Parse user request for semantic meaning
- Query **L-gent** (if exists) for similar artifacts to reuse/compose
- Extract explicit and implicit requirements
- Identify dependencies on external systems

#### Phase 2: Contract (Interface Synthesis)
**Morphism**: `(Intent, Dependencies) → Contract`

- Synthesize type signatures for inputs/outputs
- Define behavioral invariants (idempotency, latency, error handling)
- Specify composition protocols (how this agent connects to others)
- **Key insight**: Ontology alignment happens *before* code generation

#### Phase 3: Prototype (Code Generation)
**Morphism**: `(Intent, Contract) → SourceCode`

- Generate implementation satisfying contract
- Static analysis: Parsing, type checking, linting
- Security scan via **G-gent** (malicious patterns, vulnerabilities)
- If validation fails → iterate (max 5 attempts)

#### Phase 4: Validate (Test-Driven Forging)
**Morphism**: `(SourceCode, Examples) → (Verdict, Evidence)`

- Execute implementation against test cases from Examples
- Compare outputs to expected results
- If mismatch → self-heal: analyze error, regenerate code
- Convergence detection: If stuck in loop, escalate to human

#### Phase 5: Crystallize (Artifact Finalization)
**Morphism**: `(Intent, Contract, SourceCode) → Artifact`

- Lock implementation into `.alo.md` file
- Generate artifact hash (integrity verification)
- Register with **L-gent** (librarian) for discoverability
- Notify **C-gent** (composer) that new tool is available

### Drift Detection & Re-Forging

Artifacts are permanent, but environments change.

**Drift** occurs when:
- External APIs change structure
- Runtime errors emerge in production
- Contract violations detected by monitoring

**Re-Forging** workflow:
1. **G-gent** flags artifact as "brittle" due to recurring failures
2. F-gent retrieves original intent from `.alo.md`
3. F-gent analyzes error logs + new environment
4. F-gent enters Forge Loop starting at Phase 2 (Contract may need updating)
5. New artifact version generated: `v1.0.2 → v1.0.3`
6. Human approval required if contract changes (breaking change)

## Relationship to Bootstrap Agents

F-gents are **derivable** from bootstrap primitives:

| F-gent Capability | Bootstrap Agent | How |
|-------------------|-----------------|-----|
| Intent parsing | **Ground** | Natural language grounded in syntax/semantics |
| Contract synthesis | **Compose** | Interface = composition protocol |
| Code generation | **Fix** | Iterative refinement until convergence |
| Validation | **Contradict** | Tests contradict implementation claims |
| Quality judgment | **Judge** | Principles (tasteful, ethical, composable) |
| Dialectical refinement | **Sublate** | Thesis (intent) + Antithesis (constraints) → Synthesis (artifact) |

F-gents add no new irreducibles—they orchestrate bootstrap agents into a generative pipeline.

## Relationship to Other Genera

### J-gents (Just-in-Time Intelligence)

**Complementary opposites:**
- **J-gent**: Ephemeral agent compiled at runtime, discarded after use
- **F-gent**: Permanent agent forged once, reused indefinitely

**When to use which:**
- Use **J-gent** for one-off tasks, exploratory debugging, dynamic environments
- Use **F-gent** for reusable tools, production systems, ecosystem building

**Hybrid pattern**: F-gent can create a *template* that J-gent instantiates with runtime parameters.

### E-gents (Evolution)

F-gents create artifacts; **E-gents evolve them:**
- F-gent: Intent → Artifact (initial creation)
- E-gent: Artifact(v1) → Artifact(v2) (iterative improvement)

**Integration**: E-gents use F-gent to re-generate improved implementations from updated intent.

### D-gents (Data)

**F-gents leverage D-gents for lineage tracking:**
- **PersistentAgent**: Store artifact history (all versions)
- **VectorAgent**: Semantic search over artifact library (find similar agents)
- **GraphAgent**: Dependency graph (which artifacts compose with which)

### C-gents (Category Theory)

**Contracts ARE morphisms:**
- F-gent ensures every artifact is a well-typed morphism `A → B`
- Contracts specify composition laws (associativity, identity)
- F-gent validates that artifact satisfies functor/monad laws (if applicable)

### H-gents (Hegelian Dialectic)

**Forging is dialectical:**
- **Thesis**: User intent (what they want)
- **Antithesis**: Environmental constraints (what's possible)
- **Synthesis**: Artifact (reconciliation of desire and reality)

When intent and constraints conflict, F-gent **holds the tension** and requests human clarification (doesn't force invalid synthesis).

### L-gent (Librarian - Future)

**F-gent is the library's author:**
- F-gent creates artifacts → L-gent catalogs them
- L-gent enables discovery → F-gent reuses existing artifacts
- Prevents duplication: L-gent searches before F-gent forges

### K-gent (Kent Simulacra)

**K-gent can request F-gent to build tools:**
- K-gent: "I need an agent that summarizes papers"
- F-gent: *Forges SummarizerAgent from intent*
- K-gent: *Uses new tool in workflow*

## Composability

F-gents ensure artifacts are **composable by construction**:

### Contract-First Composition

Before forging Agent B that depends on Agent A, F-gent:
1. Reads Agent A's contract (output type, guarantees)
2. Synthesizes Agent B's contract to align (input type matches A's output)
3. Generates composition glue if needed (adapters, transformers)

### The Handshake Pattern

When F-gent creates two agents that must communicate:
```yaml
# Forged by F-gent
contract_name: "DataPipeline"

agents:
  - name: "Fetcher"
    output_type: "RawData"
    guarantees: ["idempotent", "timeout<5s"]

  - name: "Processor"
    input_type: "RawData"  # Matches Fetcher output
    output_type: "CleanData"
    guarantees: ["deterministic", "error-transparent"]

composition:
  pipeline: "Fetcher >> Processor"
  validation: "output type-checks, all guarantees preserved"
```

## Success Criteria

An F-gent artifact is well-forged if:

- ✓ **Intent Preserved**: Natural language intent matches generated behavior
- ✓ **Contract Explicit**: Interface fully specified (types, invariants, semantics)
- ✓ **Tests Pass**: All examples validate correctly
- ✓ **Composable**: Artifact is a valid morphism in C-gent category
- ✓ **Discoverable**: Registered with L-gent for ecosystem reuse
- ✓ **Versioned**: Lineage tracked, breaking changes flagged
- ✓ **Re-Forgeable**: Can regenerate from intent if environment changes

## Anti-Patterns

F-gents must **never**:

1. ❌ Generate code without synthesizing contract first
2. ❌ Forge artifacts that duplicate existing ones (check L-gent first)
3. ❌ Hide failures in silent retry loops (expose errors, request human input)
4. ❌ Create non-composable artifacts (all must be valid morphisms)
5. ❌ Discard original intent (must preserve in artifact)
6. ❌ Auto-deploy breaking changes (require human approval)
7. ❌ Generate artifacts without test cases

## Specifications

| Document | Description |
|----------|-------------|
| [forge.md](forge.md) | The Forge Loop: Understand → Contract → Prototype → Validate → Crystallize |
| [contracts.md](contracts.md) | Contract synthesis, ontology alignment, composition protocols |
| [artifacts.md](artifacts.md) | ALO format, versioning, lineage, re-forging |
| [integration.md](integration.md) | Ecosystem integration (L-gent, E-gent, J-gent) |

## Design Principles Alignment

### Tasteful
F-gents justify artifact existence via L-gent search (avoid duplication).

### Curated
F-gents produce artifacts that earn their place through validation and reuse.

### Ethical
Contracts make guarantees explicit (transparency, no hidden behavior).

### Joy-Inducing
Natural language intent makes creation delightful (no boilerplate drudgery).

### Composable
**Contract-first design ensures composability by construction.**

### Heterarchical
F-gents don't own artifacts—they author them for ecosystem use. No fixed hierarchy.

### Generative
Intent is the compressed spec; artifact is the generated implementation. **This is the exemplar of generative design.**

## Example: Forging a Summarizer Agent

**User Intent**:
> "I need an agent that summarizes technical papers for executive reading. Concise, objective, no jargon. Output JSON with title, key findings, confidence score."

**F-gent Forge Loop**:

1. **Understand**:
   - Intent: Summarization agent
   - Constraints: Executive audience (concise), objective tone, structured output
   - Dependencies: Input (paper text/PDF), Output (JSON)

2. **Contract**:
   ```python
   # Synthesized by F-gent
   class SummaryOutput(TypedDict):
       title: str
       key_findings: list[str]
       confidence_score: float  # 0.0-1.0

   class SummarizerAgent(Agent[str, SummaryOutput]):
       """
       Summarize technical papers for executive reading.

       Guarantees:
       - Output length < 500 words
       - No hallucinations (citations must exist in input)
       - Confidence score reflects certainty
       """
   ```

3. **Prototype**:
   - Generate implementation using LLM + prompt engineering
   - Static checks: Parsing, type validation
   - G-gent security scan: No malicious patterns

4. **Validate**:
   - Run against example papers (test cases)
   - Verify output length < 500 words
   - Check JSON schema compliance
   - If failures → iterate (refine prompt, adjust logic)

5. **Crystallize**:
   - Lock into `summarizer_v1.alo.md`
   - Register with L-gent under tags: [summarization, executive, papers]
   - Notify C-gent: SummarizerAgent available for composition

**Result**: Permanent, reusable artifact ready for ecosystem integration.

---

## Vision

F-gents transform agent creation from **artisanal crafting** to **intentional forging**:

- **Traditional**: Write code manually, debug, test, document separately
- **F-gents**: Express intent, get validated artifact, compose with ecosystem

By making **contracts first-class**, F-gents ensure artifacts are:
1. **Interoperable** (type-safe composition)
2. **Transparent** (guarantees explicit)
3. **Reusable** (discoverable via L-gent)
4. **Evolvable** (re-forgeable from intent)

They are the **foundry of the agent ecosystem**—where raw intent becomes refined capability.

---

## See Also

- [forge.md](forge.md) - The Forge Loop specification
- [contracts.md](contracts.md) - Contract synthesis deep dive
- [artifacts.md](artifacts.md) - ALO format and versioning
- [../j-gents/](../j-gents/) - Complementary ephemeral intelligence
- [../e-gents/](../e-gents/) - Artifact evolution
- [../c-gents/](../c-gents/) - Composition foundations
- [../bootstrap.md](../bootstrap.md) - Derivation from irreducibles

---

*"Intent is ephemeral; artifacts endure. The forge is where intention becomes permanence."*
