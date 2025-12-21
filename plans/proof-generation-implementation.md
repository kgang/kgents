# Proof-Generation Implementation Plan

> *"Failures don't just update a causal graph—they generate proof obligations."*

**Status**: Phase 3 Complete
**Created**: 2025-12-21
**Heritage**: Kleppmann (§12), Polynomial Functors (§10), Stigmergic Cognition (§13)
**Spec**: `spec/protocols/proof-generation.md`
**Timeline**: 10 weeks (realistic, depth over breadth)

---

## Review Summary

The spec work was reviewed and found to be **solid with minor housekeeping issues**:

### Issues Found (Non-Blocking)

| File | Issue | Severity | Action |
|------|-------|----------|--------|
| `heritage.md` | §11 Sheaves citation incomplete ("Robinson, David I. and others") | Minor | Future: Complete citation |
| `heritage.md` | Line 35 references `services/ashc/_tests/test_proof_generation.py` which doesn't exist yet | Correct | Test path is future (honest) |
| `heritage.md` | Line 571 "224 tests" is outdated (now 302+ across coffee) | Minor | Update count |
| `principles.md` | AD-013 references skill doc "to be updated" | Correct | Planned work, not error |
| `proof-generation.md` | References `spec/agents/witness.md` which doesn't exist | Minor | Should be `spec/protocols/witness-primitives.md` |

### Anti-Sausage Verdict

- **Rough edges preserved**: "LLM hallucinations don't matter" is daring
- **Opinionated stances intact**: "The proof checker is the gatekeeper"
- **Voice**: Technical, precise, bold—matches Kent's intent

---

## The Ground Truth

Before diving into phases, establish what we're building toward:

```
Test Failure → ProofObligation → LLM Proof Search → Checker → VerifiedLemma
                                                              ↓
                                                    Causal Graph (Lemma DB)
                                                              ↓
                                                    NEXT Generation (uses lemmas)
```

This creates a **ratchet**: each failure can add to the corpus of verified facts.

---

## Phase 0: Foundation (Week 1)

> *"The contracts are the spec in code form."*

### Deliverables

1. **Create `impl/claude/services/ashc/` directory structure**:
   ```
   services/ashc/
   ├── __init__.py
   ├── contracts.py      # ProofObligation, VerifiedLemma, ProofSearchResult
   ├── obligation.py     # Obligation extraction from failures
   ├── checker.py        # Proof checker bridge (interface)
   ├── search.py         # LLM proof search strategy
   ├── lemma_db.py       # Lemma persistence + retrieval
   └── _tests/
       ├── __init__.py
       ├── test_contracts.py
       ├── test_obligation.py
       └── test_checker.py
   ```

2. **Define core contracts** in `contracts.py`:

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import NewType

# Type aliases
ObligationId = NewType("ObligationId", str)
LemmaId = NewType("LemmaId", str)
ProofAttemptId = NewType("ProofAttemptId", str)

class ProofStatus(Enum):
    """Status of a proof obligation or attempt."""
    PENDING = auto()      # Awaiting proof search
    SEARCHING = auto()    # LLM actively searching
    VERIFIED = auto()     # Checker accepted proof
    FAILED = auto()       # All attempts exhausted
    TIMEOUT = auto()      # Budget exceeded

@dataclass(frozen=True)
class ProofObligation:
    """
    A property that needs to be proven.

    Generated from:
    - Test failures (most common)
    - Type signatures (AD-013)
    - Spec assertions

    Teaching:
        gotcha: ProofObligation is immutable. Create new obligations
                with updated context, don't mutate existing ones.
    """
    id: ObligationId
    property: str           # Formal statement to prove (Lean/Dafny syntax)
    source: str             # Where this came from ("test", "type", "spec")
    source_location: str    # File:line or AGENTESE path
    context: tuple[str, ...] = ()  # Relevant code snippets, hints
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "property": self.property,
            "source": self.source,
            "source_location": self.source_location,
            "context": list(self.context),
            "created_at": self.created_at.isoformat(),
        }

@dataclass(frozen=True)
class ProofAttempt:
    """
    A single attempt to discharge a proof obligation.

    Teaching:
        gotcha: We store failed attempts too—they inform future searches.
                "What didn't work" is as valuable as "what worked."
    """
    id: ProofAttemptId
    obligation_id: ObligationId
    proof_source: str       # The proof text (Lean/Dafny)
    checker: str            # "lean4", "dafny", "verus"
    result: ProofStatus
    checker_output: str     # Raw output from checker
    tactics_used: tuple[str, ...] = ()
    duration_ms: int = 0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class VerifiedLemma:
    """
    A proven fact in the lemma database.

    Once verified, lemmas are immutable facts. They can be:
    - Indexed for retrieval
    - Composed with other lemmas
    - Used as hints for future proof searches

    Teaching:
        gotcha: VerifiedLemma includes the full proof—not just the statement.
                This enables proof reuse and composition.
    """
    id: LemmaId
    statement: str          # The formal theorem statement
    proof: str              # The complete proof
    checker: str            # Which checker verified this
    obligation_id: ObligationId  # Origin obligation
    dependencies: tuple[LemmaId, ...] = ()  # Lemmas this builds on
    usage_count: int = 0    # For stigmergic reinforcement
    verified_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "statement": self.statement,
            "proof": self.proof,
            "checker": self.checker,
            "obligation_id": str(self.obligation_id),
            "dependencies": [str(d) for d in self.dependencies],
            "usage_count": self.usage_count,
            "verified_at": self.verified_at.isoformat(),
        }

@dataclass
class ProofSearchResult:
    """
    Result of a proof search session.

    Contains all attempts (successful and failed) for analysis.
    """
    obligation: ProofObligation
    attempts: list[ProofAttempt] = field(default_factory=list)
    lemma: VerifiedLemma | None = None  # If successful
    budget_used: int = 0                # Attempts made
    budget_total: int = 0               # Attempts allowed

    @property
    def succeeded(self) -> bool:
        return self.lemma is not None

    @property
    def tactics_that_failed(self) -> set[str]:
        """Tactics to avoid in future searches."""
        failed = set()
        for attempt in self.attempts:
            if attempt.result == ProofStatus.FAILED:
                failed.update(attempt.tactics_used)
        return failed
```

### Test Strategy (Phase 0)

```python
# test_contracts.py
def test_proof_obligation_immutable():
    """ProofObligation cannot be mutated after creation."""
    obl = ProofObligation(
        id=ObligationId("obl-001"),
        property="∀ x. f(x) > 0",
        source="test",
        source_location="test_foo.py:42",
    )
    with pytest.raises(FrozenInstanceError):
        obl.property = "changed"

def test_verified_lemma_tracks_dependencies():
    """Lemmas can depend on other lemmas."""
    lemma1 = VerifiedLemma(id=LemmaId("lem-001"), ...)
    lemma2 = VerifiedLemma(
        id=LemmaId("lem-002"),
        dependencies=(lemma1.id,),
        ...
    )
    assert lemma1.id in lemma2.dependencies

def test_proof_search_result_tactics_failed():
    """Failed tactics are tracked for future avoidance."""
    result = ProofSearchResult(...)
    result.attempts.append(ProofAttempt(
        result=ProofStatus.FAILED,
        tactics_used=("simp", "auto"),
        ...
    ))
    assert "simp" in result.tactics_that_failed
```

### Exit Criteria (Phase 0) ✅ COMPLETE

- [x] `services/ashc/contracts.py` passes mypy strict
- [x] All contracts have `to_dict()` for serialization
- [x] Contracts follow Pattern 2 (Enum Property Pattern) where applicable
- [x] 10+ tests for contract behavior (29 tests passing)

---

## Phase 1: Proof Checker Bridge (Weeks 2-3) ✅ COMPLETE

> *"The proof checker is the gatekeeper. No hallucination survives it."*

### Implementation (2025-12-21)

Created `impl/claude/services/ashc/checker.py` with:

1. **ProofChecker Protocol** - Runtime-checkable protocol for checker adapters
2. **DafnyChecker** - Subprocess bridge to `dafny verify`
3. **MockChecker** - Test double with pattern-based responses
4. **CheckerRegistry** - Lazy-loading registry for multiple checkers
5. **Exceptions** - `CheckerUnavailable`, `CheckerError` for graceful degradation

Key Design Decisions:
- **Protocol > ABC**: Enables duck typing without inheritance coupling
- **Lazy verification**: `verify_on_init=False` option for faster startup
- **Pattern matching in MockChecker**: `always_succeed_on()` / `always_fail_on()` for precise test control
- **Temp file cleanup in finally block**: No zombie files even on exceptions
- **Process kill on timeout**: `proc.kill() + await proc.wait()` prevents zombie processes

### Test Strategy (Phase 1) ✅

- Unit tests for MockChecker (always run)
- Protocol compliance tests
- Registry tests (lazy loading, singleton)
- Integration tests marked `@pytest.mark.integration` (skipped without Dafny)
- 55 tests total (45 unit + 10 integration)

### Why Dafny First

| Checker | Install | Syntax | Error Messages | Learning Curve |
|---------|---------|--------|----------------|----------------|
| **Dafny** | Simple (dotnet tool) | Imperative-ish | Clear | Low |
| Lean4 | Complex (elan + lake) | Functional | Cryptic | High |
| Verus | Rust ecosystem | Rust-like | Medium | Medium |

**Decision**: Start with Dafny. It's the simplest path to proving. Once the pipeline works, add Lean4 for mathematical proofs.

### Interface Design

```python
# checker.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol

class ProofChecker(Protocol):
    """
    Protocol for proof checker adapters.

    Each checker must:
    1. Accept proof source as string
    2. Return verification result
    3. Handle timeouts gracefully
    """

    @property
    def name(self) -> str:
        """Checker identifier (e.g., 'dafny', 'lean4')."""
        ...

    async def check(
        self,
        proof_source: str,
        timeout_ms: int = 30000,
    ) -> CheckerResult:
        """
        Verify a proof.

        Returns CheckerResult with success/failure and diagnostics.
        """
        ...

@dataclass
class CheckerResult:
    """Result from a proof checker."""
    success: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    duration_ms: int = 0

    @property
    def is_timeout(self) -> bool:
        return any("timeout" in e.lower() for e in self.errors)

# dafny_bridge.py
class DafnyChecker:
    """
    Dafny proof checker via subprocess.

    Requires: dotnet tool install --global dafny

    Teaching:
        gotcha: Dafny outputs to stderr even on success. Parse exit code,
                not output presence, to determine success.
    """

    def __init__(self, dafny_path: str = "dafny"):
        self._dafny_path = dafny_path
        self._verify_installation()

    def _verify_installation(self) -> None:
        """Check that dafny is installed and accessible."""
        try:
            result = subprocess.run(
                [self._dafny_path, "--version"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode != 0:
                raise RuntimeError("Dafny not responding")
        except FileNotFoundError:
            raise RuntimeError(
                "Dafny not found. Install: dotnet tool install --global dafny"
            )

    async def check(
        self,
        proof_source: str,
        timeout_ms: int = 30000,
    ) -> CheckerResult:
        """Run Dafny verification on proof source."""
        # Write to temp file (Dafny requires file input)
        with tempfile.NamedTemporaryFile(
            suffix=".dfy",
            mode="w",
            delete=False,
        ) as f:
            f.write(proof_source)
            temp_path = f.name

        try:
            start = time.monotonic()
            proc = await asyncio.create_subprocess_exec(
                self._dafny_path, "verify", temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout_ms / 1000,
                )
            except asyncio.TimeoutError:
                proc.kill()
                return CheckerResult(
                    success=False,
                    errors=["Verification timeout"],
                    duration_ms=timeout_ms,
                )

            duration = int((time.monotonic() - start) * 1000)
            success = proc.returncode == 0

            # Parse Dafny output
            output = (stdout + stderr).decode()
            errors = self._parse_errors(output)
            warnings = self._parse_warnings(output)

            return CheckerResult(
                success=success,
                errors=errors,
                warnings=warnings,
                duration_ms=duration,
            )
        finally:
            os.unlink(temp_path)

    def _parse_errors(self, output: str) -> list[str]:
        """Extract error messages from Dafny output."""
        errors = []
        for line in output.split("\n"):
            if "error:" in line.lower():
                errors.append(line.strip())
        return errors
```

### Test Strategy (Phase 1)

```python
# test_checker.py
@pytest.mark.integration
async def test_dafny_verifies_trivial_proof():
    """Dafny accepts obviously true proofs."""
    checker = DafnyChecker()
    proof = """
    lemma TrivialTrue()
        ensures true
    {}
    """
    result = await checker.check(proof)
    assert result.success
    assert result.duration_ms < 5000

@pytest.mark.integration
async def test_dafny_rejects_false_claim():
    """Dafny rejects false claims."""
    checker = DafnyChecker()
    proof = """
    lemma FalseClaim()
        ensures 1 == 2
    {}
    """
    result = await checker.check(proof)
    assert not result.success
    assert len(result.errors) > 0

async def test_checker_handles_timeout():
    """Checker returns timeout result, doesn't hang."""
    checker = DafnyChecker()
    # Intentionally complex proof that will timeout
    proof = """
    lemma Slow()
        ensures forall x: int :: x * x >= 0
    {
        // Missing proof - will timeout trying to verify
    }
    """
    result = await checker.check(proof, timeout_ms=100)
    assert not result.success
    assert result.is_timeout
```

### Exit Criteria (Phase 1) ✅ COMPLETE

- [x] `DafnyChecker` passes all integration tests (requires Dafny installed)
- [x] Timeout handling is robust (no zombie processes)
- [x] Error parsing extracts actionable diagnostics
- [x] Checker protocol allows future Lean4/Verus adapters

---

## Phase 2: Obligation Extraction (Weeks 3-4)

> *"Every test failure is a theorem waiting to be stated."*

### Sources of Obligations

1. **Test Failures** (Primary)
   - pytest `AssertionError` → `∀ inputs. assertion holds`
   - Exception traces → `∀ inputs. no_exception`

2. **Type Signatures** (AD-013)
   - `@node` decorators with `input_type`/`output_type`
   - Function signatures → `∀ x: Input. f(x): Output`

3. **Docstring Specs** (Future)
   - `"""ensures: ..."""` annotations
   - Property declarations in specs

### Implementation

```python
# obligation.py
from dataclasses import dataclass
import ast
import re

class ObligationExtractor:
    """
    Extract proof obligations from various sources.

    Pattern: Container-Owns-Workflow (Pattern 1)
    The extractor owns a session of extractions.
    """

    def __init__(self):
        self._obligations: list[ProofObligation] = []
        self._counter = 0

    def from_test_failure(
        self,
        test_name: str,
        assertion: str,
        traceback: str,
        source_file: str,
        line_number: int,
    ) -> ProofObligation:
        """
        Extract obligation from a test failure.

        Example:
            assert x > 0  # Failed
            → ProofObligation(property="∀ x. x > 0", ...)
        """
        self._counter += 1

        # Parse assertion to formal property
        property_stmt = self._assertion_to_property(assertion)

        # Extract relevant context from traceback
        context = self._extract_context(traceback, source_file)

        obl = ProofObligation(
            id=ObligationId(f"obl-test-{self._counter:04d}"),
            property=property_stmt,
            source="test",
            source_location=f"{source_file}:{line_number}",
            context=context,
        )
        self._obligations.append(obl)
        return obl

    def from_type_signature(
        self,
        path: str,           # AGENTESE path
        input_type: str,     # Python type annotation
        output_type: str,    # Python type annotation
        effects: tuple[str, ...] = (),
    ) -> ProofObligation:
        """
        Extract obligation from AD-013 typed AGENTESE path.

        Example:
            @node(input_type=BashRequest, output_type=Witness[BashResult])
            → ProofObligation(property="∀ r: BashRequest. invoke(r): Witness[BashResult]")
        """
        self._counter += 1

        property_stmt = self._type_to_property(input_type, output_type, effects)

        obl = ProofObligation(
            id=ObligationId(f"obl-type-{self._counter:04d}"),
            property=property_stmt,
            source="type",
            source_location=path,
            context=(f"Effects: {effects}",) if effects else (),
        )
        self._obligations.append(obl)
        return obl

    def _assertion_to_property(self, assertion: str) -> str:
        """
        Convert Python assertion to formal property.

        This is intentionally simple—complex assertions need human guidance.
        """
        # Strip "assert " prefix
        if assertion.startswith("assert "):
            assertion = assertion[7:]

        # Handle common patterns
        if " > " in assertion:
            return f"∀ x. {assertion.replace('x', 'x')}"
        if " == " in assertion:
            return f"∀ x. {assertion}"

        # Fallback: wrap in forall
        return f"∀ inputs. {assertion}"

    def _type_to_property(
        self,
        input_type: str,
        output_type: str,
        effects: tuple[str, ...],
    ) -> str:
        """Convert type signature to formal property."""
        base = f"∀ x: {input_type}. invoke(x): {output_type}"
        if effects:
            base += f" {{ effects: {', '.join(effects)} }}"
        return base

    def _extract_context(
        self,
        traceback: str,
        source_file: str,
    ) -> tuple[str, ...]:
        """Extract relevant code snippets from traceback."""
        context = []

        # Extract local variables mentioned in assertion
        for line in traceback.split("\n"):
            if "=" in line and not line.strip().startswith("#"):
                context.append(line.strip())

        return tuple(context[:5])  # Limit context size
```

### Test Strategy (Phase 2)

```python
# test_obligation.py
def test_obligation_from_simple_assertion():
    """Simple assertion becomes forall property."""
    extractor = ObligationExtractor()
    obl = extractor.from_test_failure(
        test_name="test_positive",
        assertion="assert x > 0",
        traceback="...",
        source_file="test_math.py",
        line_number=42,
    )
    assert "∀" in obl.property
    assert "x > 0" in obl.property

def test_obligation_from_typed_node():
    """AD-013 type signature generates obligation."""
    extractor = ObligationExtractor()
    obl = extractor.from_type_signature(
        path="world.tools.bash",
        input_type="BashRequest",
        output_type="Witness[BashResult]",
        effects=("filesystem", "subprocess"),
    )
    assert "BashRequest" in obl.property
    assert "Witness[BashResult]" in obl.property
    assert obl.source == "type"

def test_context_limited_to_five():
    """Context extraction is bounded to prevent bloat."""
    extractor = ObligationExtractor()
    long_traceback = "\n".join([f"x{i} = {i}" for i in range(20)])
    obl = extractor.from_test_failure(
        assertion="assert False",
        traceback=long_traceback,
        ...
    )
    assert len(obl.context) <= 5
```

### Implementation (2025-12-21)

Created `impl/claude/services/ashc/obligation.py` with:

1. **ObligationExtractor** - Session container for obligation extraction
2. **from_test_failure()** - Extracts obligations from pytest failures
3. **from_type_signature()** - Extracts obligations from AD-013 @node decorators
4. **from_composition()** - Extracts obligations from pipeline composition
5. **extract_from_pytest_report()** - Convenience function for pytest JSON reports

Key Design Decisions:
- **Post-process > pytest plugin**: Simpler, testable, decoupled—plugin can come later
- **Bounded context (5 lines max)**: Prevents obligation bloat
- **Pattern-based variable extraction**: Readable properties, not AST dumps
- **UUID-based IDs**: Globally unique, session-independent

### Test Strategy (Phase 2) ✅

- 34 new tests for obligation extraction
- Variable extraction tests (keywords, builtins, constants filtered)
- Context bounding tests (max lines, truncation)
- Serialization roundtrip tests
- pytest report integration tests

### Exit Criteria (Phase 2) ✅ COMPLETE

- [x] Obligation extractor handles pytest failure format
- [x] Type signature extraction works with `@node` decorator
- [x] Context extraction is bounded (no payload bloat)
- [x] Obligations serialize cleanly to JSON

---

## Phase 3: LLM Proof Search (Weeks 4-6)

> *"The LLM can hallucinate all it wants. The proof checker is the gatekeeper."*

### The Feedback Loop

```
Obligation → Prompt → LLM → Proof Attempt → Checker
                ↑                              ↓
                └──────── Failed? ─────────────┘
                          (retry with hints)
```

### Budget Strategy (From Spec)

| Phase | Attempts | Tactics | Purpose |
|-------|----------|---------|---------|
| Quick | 10 | `simp`, `auto`, `linarith` | Catch easy proofs |
| Medium | 50 | + structured hints | Most proofs discharge here |
| Deep | 200 | + heritage patterns | Complex theorems |

### Implementation

```python
# search.py
from dataclasses import dataclass, field

@dataclass
class ProofSearchConfig:
    """Configuration for proof search phases."""
    quick_budget: int = 10
    medium_budget: int = 50
    deep_budget: int = 200
    timeout_per_attempt_ms: int = 30000

    # Tactic progressions
    quick_tactics: tuple[str, ...] = ("simp", "auto", "trivial")
    medium_tactics: tuple[str, ...] = ("simp", "auto", "linarith", "omega", "decide")
    deep_tactics: tuple[str, ...] = ("simp", "auto", "linarith", "omega", "decide", "blast", "metis")

class ProofSearcher:
    """
    LLM-assisted proof search with budget management.

    Pattern: Signal Aggregation for Decisions (Pattern 4)
    Multiple signals (tactics, hints, failures) contribute to search direction.
    """

    def __init__(
        self,
        llm: "MorpheusGateway",
        checker: ProofChecker,
        lemma_db: "LemmaDatabase",
        config: ProofSearchConfig | None = None,
    ):
        self._llm = llm
        self._checker = checker
        self._lemma_db = lemma_db
        self._config = config or ProofSearchConfig()

    async def search(
        self,
        obligation: ProofObligation,
    ) -> ProofSearchResult:
        """
        Attempt to discharge a proof obligation.

        Progresses through Quick → Medium → Deep phases,
        stopping when proof is found or budget exhausted.
        """
        result = ProofSearchResult(
            obligation=obligation,
            budget_total=(
                self._config.quick_budget +
                self._config.medium_budget +
                self._config.deep_budget
            ),
        )

        # Phase 1: Quick
        if await self._search_phase(
            obligation, result,
            budget=self._config.quick_budget,
            tactics=self._config.quick_tactics,
            hints=(),
        ):
            return result

        # Phase 2: Medium (add hints from failed attempts + lemma DB)
        hints = self._gather_hints(obligation, result)
        if await self._search_phase(
            obligation, result,
            budget=self._config.medium_budget,
            tactics=self._config.medium_tactics,
            hints=hints,
        ):
            return result

        # Phase 3: Deep (add heritage patterns)
        heritage_hints = self._heritage_hints(obligation)
        if await self._search_phase(
            obligation, result,
            budget=self._config.deep_budget,
            tactics=self._config.deep_tactics,
            hints=hints + heritage_hints,
        ):
            return result

        return result

    async def _search_phase(
        self,
        obligation: ProofObligation,
        result: ProofSearchResult,
        budget: int,
        tactics: tuple[str, ...],
        hints: tuple[str, ...],
    ) -> bool:
        """
        Run one phase of proof search.

        Returns True if proof found.
        """
        for _ in range(budget):
            result.budget_used += 1

            # Build prompt
            prompt = self._build_prompt(obligation, tactics, hints, result)

            # Generate proof attempt
            proof_source = await self._generate_proof(prompt)

            # Check proof
            check_result = await self._checker.check(
                proof_source,
                timeout_ms=self._config.timeout_per_attempt_ms,
            )

            # Record attempt
            attempt = ProofAttempt(
                id=ProofAttemptId(f"att-{result.budget_used:04d}"),
                obligation_id=obligation.id,
                proof_source=proof_source,
                checker=self._checker.name,
                result=ProofStatus.VERIFIED if check_result.success else ProofStatus.FAILED,
                checker_output="\n".join(check_result.errors + check_result.warnings),
                tactics_used=self._extract_tactics(proof_source),
                duration_ms=check_result.duration_ms,
            )
            result.attempts.append(attempt)

            if check_result.success:
                # Success! Create lemma
                result.lemma = VerifiedLemma(
                    id=LemmaId(f"lem-{obligation.id}"),
                    statement=obligation.property,
                    proof=proof_source,
                    checker=self._checker.name,
                    obligation_id=obligation.id,
                )
                return True

            # Add failure hints for next attempt
            hints = hints + (f"Failed tactic: {attempt.tactics_used}",)

        return False

    def _build_prompt(
        self,
        obligation: ProofObligation,
        tactics: tuple[str, ...],
        hints: tuple[str, ...],
        result: ProofSearchResult,
    ) -> str:
        """Build LLM prompt for proof generation."""
        prompt_parts = [
            "Generate a Dafny proof for the following property:",
            f"Property: {obligation.property}",
            f"Source: {obligation.source_location}",
            "",
            "Available tactics: " + ", ".join(tactics),
        ]

        if obligation.context:
            prompt_parts.append("\nContext:")
            for ctx in obligation.context:
                prompt_parts.append(f"  {ctx}")

        if hints:
            prompt_parts.append("\nHints from previous attempts:")
            for hint in hints[-5:]:  # Limit hints
                prompt_parts.append(f"  - {hint}")

        # Add failed tactics to avoid
        failed = result.tactics_that_failed
        if failed:
            prompt_parts.append(f"\nAvoid these tactics (already failed): {failed}")

        prompt_parts.append("\nRespond with ONLY the Dafny proof code, no explanation.")

        return "\n".join(prompt_parts)

    async def _generate_proof(self, prompt: str) -> str:
        """Generate proof attempt via LLM."""
        response = await self._llm.generate(
            prompt=prompt,
            model="claude-sonnet-4-20250514",  # Fast enough for iteration
            max_tokens=2000,
            temperature=0.3,  # Low temp for deterministic proofs
        )
        return self._extract_code(response)

    def _extract_code(self, response: str) -> str:
        """Extract Dafny code from LLM response."""
        # Try to find code blocks
        if "```dafny" in response:
            match = re.search(r"```dafny\n(.*?)\n```", response, re.DOTALL)
            if match:
                return match.group(1)
        if "```" in response:
            match = re.search(r"```\n(.*?)\n```", response, re.DOTALL)
            if match:
                return match.group(1)
        # Fallback: assume entire response is code
        return response.strip()

    def _gather_hints(
        self,
        obligation: ProofObligation,
        result: ProofSearchResult,
    ) -> tuple[str, ...]:
        """Gather hints from lemma DB and failed attempts."""
        hints = []

        # Related lemmas from DB
        related = self._lemma_db.find_related(obligation.property, limit=3)
        for lemma in related:
            hints.append(f"Related lemma: {lemma.statement}")

        # Successful tactics from attempts
        for attempt in result.attempts:
            if attempt.result == ProofStatus.VERIFIED:
                hints.append(f"Successful pattern: {attempt.tactics_used}")

        return tuple(hints)

    def _heritage_hints(self, obligation: ProofObligation) -> tuple[str, ...]:
        """Add hints from heritage papers (§10, §12)."""
        hints = []

        # Polynomial functor patterns (§10)
        if "polynomial" in obligation.property.lower():
            hints.append("Pattern: Use polynomial functor composition laws")

        # Type composition (AD-013)
        if ":" in obligation.property:
            hints.append("Pattern: Type-directed proof via substitution")

        return tuple(hints)
```

### Test Strategy (Phase 3)

```python
# test_search.py
@pytest.mark.integration
async def test_quick_phase_finds_trivial_proof():
    """Quick phase discharges trivial obligations."""
    searcher = ProofSearcher(...)
    obl = ProofObligation(property="∀ x: int. x == x", ...)
    result = await searcher.search(obl)
    assert result.succeeded
    assert result.budget_used <= 10  # Quick phase budget

async def test_failed_tactics_not_repeated():
    """Search avoids tactics that already failed."""
    searcher = ProofSearcher(...)
    # Mock LLM to track prompts
    prompts = []
    searcher._generate_proof = lambda p: prompts.append(p) or "..."

    obl = ProofObligation(property="∀ x. impossible(x)", ...)
    await searcher.search(obl)

    # Later prompts should mention avoiding failed tactics
    assert any("Avoid" in p for p in prompts[5:])

async def test_budget_respected():
    """Search stops when budget exhausted."""
    config = ProofSearchConfig(quick_budget=2, medium_budget=2, deep_budget=2)
    searcher = ProofSearcher(config=config, ...)

    obl = ProofObligation(property="∀ x. false", ...)  # Unprovable
    result = await searcher.search(obl)

    assert not result.succeeded
    assert result.budget_used == 6
```

### Exit Criteria (Phase 3) ✅ COMPLETE

- [x] LLM prompt generation is deterministic
- [x] Budget management respects phase limits
- [x] Failed tactics inform future attempts (stigmergic anti-pheromone)
- [x] Proof extraction handles various LLM output formats
- [x] Temperature is configurable via ProofSearchConfig

**Implementation Notes (2025-12-21)**:
- `search.py`: ProofSearcher with Quick→Medium→Deep phase progression
- `LemmaDatabase` protocol + `InMemoryLemmaDatabase` stub
- Heritage hints for polynomial/composition/identity patterns
- 39 new tests (128 total in ASHC)

---

## Phase 4: Lemma Database (Weeks 6-8)

> *"Agents leave proofs as traces. Future agents follow the proven paths."*

### Stigmergic Design

The lemma database is a **stigmergic surface** (§13):
- **Pheromone = usage_count**: More-used lemmas rank higher
- **Decay = relevance scoring**: Old unused lemmas fade
- **Reinforcement = composition**: Lemmas built on other lemmas strengthen the base

### Implementation

```python
# lemma_db.py
from dataclasses import dataclass, field
import sqlite3
from typing import Iterator

class LemmaDatabase:
    """
    Persistent storage for verified lemmas with stigmergic retrieval.

    Pattern: Unified Storage (via StorageProvider)
    Uses D-gent persistence for cross-session durability.
    """

    def __init__(self, storage_path: str):
        self._conn = sqlite3.connect(storage_path)
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS lemmas (
                id TEXT PRIMARY KEY,
                statement TEXT NOT NULL,
                proof TEXT NOT NULL,
                checker TEXT NOT NULL,
                obligation_id TEXT,
                usage_count INTEGER DEFAULT 0,
                verified_at TEXT NOT NULL,
                embedding BLOB  -- For semantic similarity
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS lemma_dependencies (
                lemma_id TEXT,
                depends_on TEXT,
                PRIMARY KEY (lemma_id, depends_on)
            )
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_usage ON lemmas(usage_count DESC)
        """)
        self._conn.commit()

    def add(self, lemma: VerifiedLemma) -> None:
        """Add a verified lemma to the database."""
        self._conn.execute(
            """
            INSERT OR REPLACE INTO lemmas
            (id, statement, proof, checker, obligation_id, usage_count, verified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(lemma.id),
                lemma.statement,
                lemma.proof,
                lemma.checker,
                str(lemma.obligation_id),
                lemma.usage_count,
                lemma.verified_at.isoformat(),
            ),
        )

        # Record dependencies
        for dep_id in lemma.dependencies:
            self._conn.execute(
                "INSERT OR IGNORE INTO lemma_dependencies VALUES (?, ?)",
                (str(lemma.id), str(dep_id)),
            )

        self._conn.commit()

    def get(self, lemma_id: LemmaId) -> VerifiedLemma | None:
        """Retrieve a lemma by ID."""
        row = self._conn.execute(
            "SELECT * FROM lemmas WHERE id = ?",
            (str(lemma_id),),
        ).fetchone()

        if row is None:
            return None

        return self._row_to_lemma(row)

    def find_related(
        self,
        property: str,
        limit: int = 5,
    ) -> list[VerifiedLemma]:
        """
        Find lemmas related to a property.

        Uses stigmergic ranking: usage_count × recency.
        """
        # Simple keyword matching (upgrade to embeddings in future)
        keywords = self._extract_keywords(property)

        query = """
            SELECT *,
                   usage_count * 1.0 / (julianday('now') - julianday(verified_at) + 1) as relevance
            FROM lemmas
            WHERE statement LIKE ?
            ORDER BY relevance DESC
            LIMIT ?
        """

        # Search for each keyword, union results
        results = []
        for kw in keywords[:3]:
            rows = self._conn.execute(query, (f"%{kw}%", limit)).fetchall()
            results.extend(rows)

        # Deduplicate and sort by relevance
        seen = set()
        unique = []
        for row in sorted(results, key=lambda r: r[-1], reverse=True):
            if row[0] not in seen:
                seen.add(row[0])
                unique.append(row)

        return [self._row_to_lemma(r) for r in unique[:limit]]

    def record_usage(self, lemma_id: LemmaId) -> None:
        """
        Increment usage count (stigmergic reinforcement).

        Called when a lemma is used as a hint for a successful proof.
        """
        self._conn.execute(
            "UPDATE lemmas SET usage_count = usage_count + 1 WHERE id = ?",
            (str(lemma_id),),
        )
        self._conn.commit()

    def dependency_graph(self) -> dict[LemmaId, list[LemmaId]]:
        """Return the lemma dependency graph."""
        rows = self._conn.execute(
            "SELECT lemma_id, depends_on FROM lemma_dependencies"
        ).fetchall()

        graph: dict[LemmaId, list[LemmaId]] = {}
        for lemma_id, depends_on in rows:
            lid = LemmaId(lemma_id)
            did = LemmaId(depends_on)
            if lid not in graph:
                graph[lid] = []
            graph[lid].append(did)

        return graph
```

### SynergyBus Integration

```python
# In services/ashc/__init__.py

from protocols.synergy import SynergyBus, SynergyEvent

async def wire_lemma_events(bus: SynergyBus, lemma_db: LemmaDatabase):
    """Wire lemma DB to SynergyBus for cross-service sharing."""

    async def on_lemma_verified(event: SynergyEvent):
        """When a lemma is verified, share it."""
        lemma = VerifiedLemma.from_dict(event.payload)
        lemma_db.add(lemma)

        # Broadcast to other services
        await bus.emit(SynergyEvent(
            source="ashc",
            event_type="lemma.available",
            payload=lemma.to_dict(),
        ))

    bus.subscribe("ashc.lemma.verified", on_lemma_verified)
```

### Exit Criteria (Phase 4)

- [ ] Lemma persistence survives process restart
- [ ] Stigmergic ranking (usage × recency) works correctly
- [ ] Dependency graph is queryable
- [ ] SynergyBus integration allows cross-service lemma sharing

---

## Phase 5: ASHC Integration (Weeks 8-10)

> *"Evidence without proof is merely statistical. With proof, the codebase becomes provably correct."*

### Integration Points

1. **Test Runner Hook**: Intercept pytest failures → extract obligations
2. **ASHC Generation Pipeline**: Feed lemmas to next generation
3. **Causal Graph Extension**: Lemmas become nodes in evidence graph

### Implementation Sketch

```python
# In services/ashc/integration.py

class ProofGeneratingASHC:
    """
    ASHC with proof generation capability.

    Extends existing ASHC pipeline to:
    1. Extract obligations from failures
    2. Attempt proof discharge
    3. Store verified lemmas
    4. Use lemmas in next generation
    """

    def __init__(
        self,
        extractor: ObligationExtractor,
        searcher: ProofSearcher,
        lemma_db: LemmaDatabase,
        evidence_graph: "EvidenceGraph",  # Existing ASHC component
    ):
        self._extractor = extractor
        self._searcher = searcher
        self._lemma_db = lemma_db
        self._evidence = evidence_graph

    async def on_test_failure(
        self,
        test_name: str,
        assertion: str,
        traceback: str,
        source_file: str,
        line_number: int,
    ) -> ProofSearchResult | None:
        """
        Handle a test failure: extract obligation, attempt proof.

        Returns ProofSearchResult if proof was attempted.
        """
        # Extract obligation
        obl = self._extractor.from_test_failure(
            test_name=test_name,
            assertion=assertion,
            traceback=traceback,
            source_file=source_file,
            line_number=line_number,
        )

        # Check if similar obligation already proven
        existing = self._lemma_db.find_related(obl.property, limit=1)
        if existing and existing[0].statement == obl.property:
            # Already proven - just record usage
            self._lemma_db.record_usage(existing[0].id)
            return None

        # Attempt proof
        result = await self._searcher.search(obl)

        if result.succeeded:
            # Store lemma
            self._lemma_db.add(result.lemma)

            # Add to evidence graph
            self._evidence.add_node(
                node_type="lemma",
                node_id=str(result.lemma.id),
                content=result.lemma.to_dict(),
            )

            # Create edge from failure to lemma
            self._evidence.add_edge(
                from_node=f"test:{test_name}",
                to_node=str(result.lemma.id),
                edge_type="generates",
            )
        else:
            # Record failed proof attempt as evidence
            self._evidence.add_node(
                node_type="failed_proof",
                node_id=str(obl.id),
                content={
                    "obligation": obl.to_dict(),
                    "attempts": result.budget_used,
                },
            )

        return result

    def get_hints_for_generation(self) -> list[str]:
        """Get lemma hints for next ASHC generation."""
        # Get most relevant lemmas
        lemmas = self._lemma_db.find_related("", limit=10)

        return [
            f"Verified: {lemma.statement}"
            for lemma in lemmas
        ]
```

### Metrics to Track

| Metric | Purpose | Target |
|--------|---------|--------|
| `proof_attempts_total` | Overall activity | Track |
| `proof_success_rate` | Effectiveness | >10% |
| `lemma_reuse_count` | Stigmergic value | Growing |
| `avg_attempts_to_proof` | Efficiency | <50 |
| `quick_phase_success_rate` | Triage effectiveness | >30% |

### Exit Criteria (Phase 5)

- [ ] Test runner integration captures failures automatically
- [ ] Lemmas feed into next ASHC generation
- [ ] Evidence graph includes lemma nodes
- [ ] Metrics are tracked and visible

---

## Fallback Strategy

When proof search fails:

1. **Fall back to evidence-only mode**: The failure still updates the causal graph, just without formal proof
2. **Log the obligation**: Future attempts may succeed as LLMs improve
3. **Human review queue**: Difficult obligations can be flagged for manual proof writing

The system **degrades gracefully**—lack of proofs doesn't break ASHC, just means less formal guarantees.

---

## Dependencies

| Dependency | Required By | Notes |
|------------|-------------|-------|
| Dafny | Phase 1 | `dotnet tool install --global dafny` |
| MorpheusGateway | Phase 3 | For LLM proof generation |
| StorageProvider | Phase 4 | For lemma persistence |
| SynergyBus | Phase 4 | For cross-service lemma sharing |
| Evidence graph | Phase 5 | Existing ASHC component |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Dafny installation fails | Docker container with pre-installed Dafny |
| LLM costs too high | Aggressive caching, smaller models for quick phase |
| Proof search too slow | Background workers, async processing |
| Lemma DB corruption | WAL mode SQLite, regular backups |
| Over-formalization | Budget limits, "critical paths only" policy |

---

*"The proof is not formal—it's empirical. Run the tree a thousand times, and the pattern of nudges IS the proof. Now we can run the proof checker a thousand times, and the pattern of verified lemmas IS the certificate."*
