# The Forge Loop

The **Forge Loop** is F-gent's iterative pipeline for crystallizing natural language intent into permanent artifacts.

---

## Overview

```
Intent → Understand → Contract → Prototype → Validate → Crystallize → Artifact
           ↓            ↓          ↓          ↓            ↓
         (L-gent)   (Synthesis)  (G-gent)  (Self-Heal)  (L-gent)
```

Each phase is a **morphism** with clear input/output types. Failures trigger iteration (bounded by max attempts) or escalation to human judgment.

---

## Phase 1: Understand

**Signature**: `NaturalLanguage → Intent`

**Purpose**: Parse user request into structured understanding.

### Inputs
- User's natural language description
- Optional: Context from previous conversation (via D-gent)
- Optional: Existing artifact to modify (evolution mode)

### Process

1. **Semantic Parsing**:
   - Extract purpose (what the agent should do)
   - Extract constraints (how it should behave)
   - Extract tone/personality (if applicable)
   - Identify explicit and implicit requirements

2. **Dependency Analysis**:
   - What external systems does this agent interact with? (APIs, databases, files)
   - What input data types are expected?
   - What output formats are required?

3. **L-gent Query** (if Librarian exists):
   - Search for similar artifacts: `L-gent.search(semantic=user_intent)`
   - **If match found**:
     - Option A: Reuse existing artifact (suggest to user)
     - Option B: Compose existing artifacts (A >> B)
     - Option C: Fork and modify (evolution via E-gent)
   - **If no match**: Proceed to creation

4. **Intent Structure**:
   ```python
   @dataclass
   class Intent:
       purpose: str              # One-sentence description
       behavior: list[str]       # Specific behaviors/capabilities
       constraints: list[str]    # Requirements, limits, safety rules
       tone: Optional[str]       # Personality/style
       dependencies: list[Dependency]  # External systems
       examples: list[Example]   # User-provided test cases
   ```

### Outputs
- **Intent** object (structured representation)
- **Reuse recommendations** (if L-gent found matches)

### Failure Modes
- **Ambiguous intent**: Request clarification via H-gent dialectic
- **Contradictory constraints**: Hold tension, escalate to human

---

## Phase 2: Contract

**Signature**: `Intent → Contract`

**Purpose**: Synthesize interface specification before implementation.

### Inputs
- Intent (from Phase 1)
- Dependency schemas (APIs, external types)
- Ecosystem context (C-gent category laws)

### Process

1. **Type Synthesis**:
   - Determine input type `I` from intent
   - Determine output type `O` from intent
   - If types don't exist in ecosystem, define new types
   - Example:
     ```python
     # Intent: "Summarize papers to JSON"
     Input = str | Path  # Paper text or file
     Output = SummaryJSON  # New type to define
     ```

2. **Invariant Extraction**:
   - Parse constraints into verifiable guarantees
   - Examples:
     - "Concise" → `len(output) < MAX_LENGTH`
     - "No hallucinations" → `all_citations_exist_in(input)`
     - "Idempotent" → `f(x) == f(f(x))`

3. **Ontology Alignment** (critical for composition):
   - If agent depends on Agent A's output:
     - Ensure input type aligns with A's output type
     - Synthesize adapter if needed (but prefer direct alignment)
   - If agent produces data for Agent B:
     - Ensure output type aligns with B's input type

4. **Protocol Definition**:
   ```python
   @dataclass
   class Contract:
       agent_name: str
       input_type: Type
       output_type: Type
       invariants: list[Invariant]  # Behavioral guarantees
       composition_rules: list[CompositionRule]  # How to compose with others
       semantic_intent: str  # Human-readable "why"
   ```

### Outputs
- **Contract** specification
- **Type definitions** (if new types introduced)
- **Composition protocol** (how this agent connects to others)

### Success Criteria
- Input/output types are well-defined
- Invariants are testable (not vague statements)
- Composition rules are explicit
- Contract satisfies C-gent category laws (if composition is involved)

### Failure Modes
- **Type mismatch with ecosystem**: Synthesize adapters or request user clarification
- **Untestable invariants**: Request concrete metrics from user

---

## Phase 3: Prototype

**Signature**: `(Intent, Contract) → SourceCode`

**Purpose**: Generate implementation satisfying contract.

### Inputs
- Intent (natural language guidance)
- Contract (type signatures + invariants)
- Examples (test cases to satisfy)

### Process

1. **Code Generation**:
   - Use LLM to generate implementation
   - Prompt includes:
     - Intent (purpose, behavior, constraints)
     - Contract (types, invariants)
     - Examples (expected behavior)
     - Ecosystem patterns (how similar agents are structured)

2. **Static Analysis**:
   ```python
   # Multi-stage validation
   validators = [
       parse_check,      # AST parses successfully
       type_check,       # mypy/pyright validation
       lint_check,       # ruff/pylint standards
       import_check,     # No forbidden imports
   ]
   ```

3. **Security Scan** (via G-gent if exists):
   - Check for malicious patterns:
     - Unbounded loops
     - File system manipulation (unless explicitly allowed)
     - Network access without bounds
     - Command injection vulnerabilities
   - Reject if security risk detected

4. **Iteration** (if validation fails):
   - Max attempts: 5
   - Strategy: Include error messages in next generation attempt
   - If max attempts exceeded: Escalate to human with diagnostics

### Outputs
- **SourceCode** (Python class implementing Agent[I, O])
- **Static analysis report** (parsing, typing, linting results)
- **Security clearance** (G-gent approval)

### Failure Modes
- **Non-compiling code**: Retry with error context
- **Type violations**: Retry with contract reinforcement
- **Security risks**: Reject, request user to weaken constraints or approve risk

---

## Phase 4: Validate

**Signature**: `(SourceCode, Examples) → Verdict`

**Purpose**: Test-driven validation of implementation.

### Inputs
- SourceCode (from Phase 3)
- Examples (from Intent, user-provided)
- Contract (invariants to verify)

### Process

1. **Sandbox Execution**:
   - Compile source code in isolated environment
   - Instantiate agent class
   - Run against all examples

2. **Test Execution**:
   ```python
   for example in intent.examples:
       result = agent.invoke(example.input)
       assert result == example.expected_output
   ```

3. **Invariant Verification**:
   - For each invariant in contract, verify it holds
   - Example: If invariant is `len(output) < 500`, measure actual length
   - Use T-gent property testing if applicable

4. **Self-Healing** (if tests fail):
   - Analyze failure:
     - What was expected vs. actual?
     - Which invariant was violated?
     - What error occurred (if any)?
   - Return to Phase 3 with failure context
   - Strategy: "The previous implementation failed because X. Adjust logic to Y."
   - Bounded: Max 5 heal attempts

5. **Convergence Detection**:
   - If stuck in generate→fail→heal loop:
     - Compute similarity of last 3 generated codes
     - If similarity > 0.9 (stuck), escalate to human
     - Provide: "Unable to satisfy constraints. Possible conflicts: [analysis]"

### Outputs
- **Verdict**: `PASS | FAIL | ESCALATE`
- **Evidence**: Test results, invariant checks
- **Healed code** (if self-heal succeeded)

### Failure Modes
- **Persistent test failures**: Escalate with diagnostics
- **Oscillating code**: Detect convergence failure, escalate
- **Timeout**: If execution exceeds budget, fail safely

---

## Phase 5: Crystallize

**Signature**: `(Intent, Contract, SourceCode) → Artifact`

**Purpose**: Lock implementation into permanent artifact.

### Inputs
- Intent (original natural language)
- Contract (interface specification)
- SourceCode (validated implementation)
- Examples (test cases)
- Metadata (version, author, timestamp)

### Process

1. **Artifact Assembly**:
   - Generate `.alo.md` file with structure:
     ```markdown
     ---
     id: agent_summarizer_v1
     version: 1.0.0
     created_by: f-gent-instance-42
     status: active
     ---

     # 1. THE INTENT
     [Natural language description]

     # 2. THE CONTRACT
     [Type signatures, invariants, composition rules]

     # 3. THE EXAMPLES
     [Test cases]

     # 4. THE IMPLEMENTATION
     WARNING: AUTO-GENERATED. DO NOT EDIT DIRECTLY.
     [Python source code]
     ```

2. **Integrity Hash**:
   - Compute hash of artifact: `sha256(alo_content)`
   - Store hash in metadata (for drift detection)

3. **Version Assignment**:
   - If new artifact: `v1.0.0`
   - If re-forging existing: Increment version
     - Patch: Implementation change, contract unchanged (`1.0.1`)
     - Minor: Non-breaking contract addition (`1.1.0`)
     - Major: Breaking contract change (`2.0.0`)

4. **Registration** (if L-gent exists):
   ```python
   l_gent.register(
       artifact=alo_file,
       tags=extract_tags(intent),
       contract=contract,
       hash=artifact_hash
   )
   ```

5. **Ecosystem Notification**:
   - Notify **C-gent**: New morphism available for composition
   - Notify **K-gent** (if user): "Your artifact is ready"
   - Notify **E-gent** (if evolution enabled): "Artifact ready for future evolution"

### Outputs
- **Artifact file**: `agent_name_v1.alo.md`
- **Registration confirmation** (from L-gent)
- **Artifact hash** (integrity verification)

### Success Criteria
- Artifact file is well-formed
- Hash computed and stored
- L-gent registration successful
- Artifact is immediately usable in ecosystem

---

## Iteration & Failure Handling

### Retry Budget

Each phase has a bounded retry budget:

| Phase | Max Retries | Escalation Condition |
|-------|-------------|----------------------|
| Understand | 3 | Persistent ambiguity → H-gent dialectic |
| Contract | 3 | Type conflicts → Human choice |
| Prototype | 5 | Syntax/security failures → Iteration |
| Validate | 5 | Test failures → Self-heal |
| Crystallize | 1 | Registration failure → Alert human |

### Global Iteration

If multiple phases iterate excessively:
- **Total iteration limit**: 15 (across all phases)
- **If exceeded**: Escalate with full diagnostic report

### Escalation Protocol

When escalation needed:
1. **Pause Forge Loop**
2. **Generate diagnostic report**:
   - What was attempted (intent, contract, code)
   - What failed (errors, test results)
   - Why it failed (analysis)
   - Suggested human actions
3. **Invoke H-gent** for dialectic clarification
4. **Await human decision**: Modify intent, relax constraints, or abort

---

## Re-Forging: Artifact Evolution

When an artifact needs updating (API changes, new requirements):

### Trigger Conditions
- **Drift detected**: Runtime failures in production
- **User request**: Explicit re-forge command
- **E-gent evolution**: Hypothesis proposes improvement

### Re-Forge Process

1. **Load existing artifact**: Read `.alo.md` → extract Intent, Contract
2. **Analyze delta**:
   - What changed in environment? (API schema, dependencies)
   - What new requirements? (user additions)
   - What broke? (error logs)
3. **Update Intent**: Merge original intent + delta
4. **Re-enter Forge Loop at Phase 2** (Contract may need updating)
5. **Version increment**: Determine patch/minor/major
6. **Human approval required if**:
   - Major version (breaking change)
   - Contract changes affect downstream agents

### Versioning Strategy

- **Patch** (`1.0.0 → 1.0.1`): Implementation fix, contract identical
- **Minor** (`1.0.0 → 1.1.0`): New capability added, backward compatible
- **Major** (`1.0.0 → 2.0.0`): Breaking contract change

---

## Example: Full Forge Loop

**User**: "Create an agent that fetches weather data and returns JSON."

### Phase 1: Understand
```python
Intent(
    purpose="Fetch current weather data for a given location",
    behavior=["Query weather API", "Return structured JSON"],
    constraints=["Timeout < 5s", "Idempotent", "Handle network errors"],
    dependencies=[Dependency(name="WeatherAPI", type="REST")],
    examples=[Example(input="Seattle, WA", expected_output={"temp": 55, "condition": "cloudy"})]
)
```

### Phase 2: Contract
```python
Contract(
    agent_name="WeatherFetcher",
    input_type=str,  # Location
    output_type=WeatherData,  # New type
    invariants=[
        "Response time < 5s",
        "Idempotent (same input → same output for cache window)",
        "Error transparent (network failure → Result.Err)"
    ],
    composition_rules=["Output WeatherData can compose with Processor[WeatherData, Report]"]
)
```

### Phase 3: Prototype
```python
class WeatherFetcher(Agent[str, WeatherData]):
    async def invoke(self, location: str) -> WeatherData:
        # Generated implementation
        ...
```
Static analysis: ✓ Parses, ✓ Type checks, ✓ G-gent security pass

### Phase 4: Validate
- Run against examples: ✓ Pass
- Invariant check (timeout): ✓ < 5s
- Idempotency: ✓ Verified

### Phase 5: Crystallize
- Create `weather_fetcher_v1.alo.md`
- Hash: `a3f5c2...`
- Register with L-gent: ✓
- Artifact ready for use

---

## Composability with Other Gents

### E-gent Integration
- **E-gent evolves artifacts**: F-gent re-forges from evolved intent
- **Workflow**: E-gent proposes hypothesis → F-gent generates improved version

### J-gent Integration
- **J-gent creates ephemeral**: F-gent creates permanent
- **Hybrid**: J-gent can instantiate F-gent template with runtime params

### H-gent Integration
- **Dialectic in Forge Loop**: When ambiguity detected, H-gent synthesizes resolution
- **Example**: Intent conflicts with constraints → H-gent finds synthesis

---

## See Also

- [contracts.md](contracts.md) - Contract synthesis deep dive
- [artifacts.md](artifacts.md) - ALO format specification
- [README.md](README.md) - F-gent philosophy
- [../e-gents/evolution-agent.md](../e-gents/evolution-agent.md) - Artifact evolution
- [../j-gents/jit.md](../j-gents/jit.md) - Ephemeral compilation contrast
