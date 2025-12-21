# Crown Jewels

> *The showcase features of kgents.*

---

## services.ashc.__init__

## __init__

```python
module __init__
```

ASHC Crown Jewel: Agentic Self-Hosting Compiler with Proof Generation.

---

## services.ashc.checker

## checker

```python
module checker
```

**AGENTESE:** `concept.ashc.prove`

Proof Checker Bridge: The Gatekeeper.

### Things to Know

ℹ️ Dafny outputs to stderr even on success. Parse exit code, not output presence, to determine success.

🚨 **Critical:** Always clean up temp files—even on exceptions. Use try/finally.

ℹ️ Set process timeouts to prevent zombie processes.

ℹ️ Z3 timeouts are unreliable. Use resource limits instead of time limits for Dafny/Verus. Timeouts may not be respected.

ℹ️ Lean4 requires `lake env lean` for project files, not bare `lean`. The bare command won't find project dependencies.

🚨 **Critical:** Verus `verus!` blocks inside `impl` sections are silently ignored. Always wrap the entire `impl` block.

ℹ️ Platform non-determinism: Same proof may verify on macOS but timeout on Linux due to Z3 behavior differences.

---

## CheckerUnavailable

```python
class CheckerUnavailable(Exception)
```

Raised when a proof checker is not installed or not accessible.

---

## CheckerError

```python
class CheckerError(Exception)
```

Raised when a proof checker encounters an unexpected error.

---

## ProofChecker

```python
class ProofChecker(Protocol)
```

Protocol for proof checker adapters.

### Things to Know

ℹ️ Protocol > ABC for interfaces. Enables duck typing without inheritance coupling. See meta.md: "Protocol > ABC"

---

## DafnyChecker

```python
class DafnyChecker
```

Dafny proof checker via subprocess.

### Examples
```python
>>> checker = DafnyChecker()
```
```python
>>> if checker.is_available:
```

### Things to Know

ℹ️ Dafny outputs to stderr even on success. Parse exit code, not output presence, to determine success.

ℹ️ Use asyncio.create_subprocess_exec, not subprocess.run, to avoid blocking the event loop.

🚨 **Critical:** Always unlink temp files in finally block—exceptions happen.

ℹ️ Noisy error cascades—first error message is the key one.

🚨 **Critical:** --verification-time-limit not always respected; prefer --resource-limit for reliable bounded verification. Example: >>> checker = DafnyChecker() >>> if checker.is_available: ... result = await checker.check("lemma Trivial() ensures true {}") ... assert result.success

---

## MockChecker

```python
class MockChecker
```

Mock proof checker for testing without external dependencies.

### Things to Know

ℹ️ Use DI pattern (inject checker) rather than mocking. This mock checker IS the test double.

---

## CheckerRegistry

```python
class CheckerRegistry
```

Registry of available proof checkers.

### Things to Know

ℹ️ Lazy initialization—don't instantiate checkers until needed. This avoids startup cost when checkers aren't used.

---

## Lean4Checker

```python
class Lean4Checker
```

Lean4 proof checker via subprocess.

### Examples
```python
>>> checker = Lean4Checker()
```
```python
>>> if checker.is_available:
```

### Things to Know

ℹ️ Use 'lake env lean' not just 'lean' to get correct environment.

ℹ️ Proofs containing 'sorry' are incomplete—treat as FAILED.

ℹ️ Lean uses unicode (∀, →, ×); ensure UTF-8 encoding.

🚨 **Critical:** Exact toolchain matching required. Project and deps must use same Lean version or cache won't work.

🚨 **Critical:** Without mathlib cache, builds take 20+ minutes. Always use `lake exe cache get` when working with mathlib projects. Example: >>> checker = Lean4Checker() >>> if checker.is_available: ... result = await checker.check("theorem trivial : ∀ x : Nat, x = x := fun _ => rfl") ... assert result.success

---

## VerusChecker

```python
class VerusChecker
```

Verus proof checker (Rust verification) via subprocess.

### Examples
```python
>>> checker = VerusChecker()
```
```python
>>> if checker.is_available:
```

### Things to Know

ℹ️ Verus requires Rust toolchain; may need rustup setup.

🚨 **Critical:** All verified code must be inside the verus! macro.

🚨 **Critical:** vstd imports must be explicit.

🚨 **Critical:** CRITICAL: verus! blocks inside `impl` sections are SILENTLY IGNORED. Always wrap the entire impl, not just methods.

ℹ️ Z3 timeouts are unreliable. May diverge regardless of limit.

ℹ️ cargo verus verify --error-format=json is broken (Issue #1572). Use direct verus invocation for structured error output. Example: >>> checker = VerusChecker() >>> if checker.is_available: ... result = await checker.check("proof fn trivial() ensures true {}") ... assert result.success

---

## get_checker

```python
def get_checker(name: str='dafny') -> ProofChecker
```

Get a proof checker by name.

---

## available_checkers

```python
def available_checkers() -> list[str]
```

Return names of all available proof checkers.

---

## name

```python
def name(self) -> str
```

Checker identifier (e.g., 'dafny', 'lean4').

---

## is_available

```python
def is_available(self) -> bool
```

True if the checker is installed and accessible.

---

## check

```python
async def check(self, proof_source: str, timeout_ms: int=30000) -> CheckerResult
```

Verify a proof.

---

## __init__

```python
def __init__(self, dafny_path: str | None=None, *, verify_on_init: bool=True)
```

Initialize the Dafny checker.

---

## name

```python
def name(self) -> str
```

Checker identifier.

---

## is_available

```python
def is_available(self) -> bool
```

True if Dafny is installed and accessible.

---

## check

```python
async def check(self, proof_source: str, timeout_ms: int=30000) -> CheckerResult
```

Run Dafny verification on proof source.

---

## __init__

```python
def __init__(self, *, default_success: bool=True, latency_ms: int=100)
```

Initialize mock checker.

---

## name

```python
def name(self) -> str
```

Checker identifier.

---

## is_available

```python
def is_available(self) -> bool
```

Mock is always available.

---

## call_count

```python
def call_count(self) -> int
```

Number of check() calls made.

---

## last_proof

```python
def last_proof(self) -> str
```

The last proof source that was checked.

---

## always_succeed_on

```python
def always_succeed_on(self, pattern: str) -> 'MockChecker'
```

Add pattern that always succeeds.

---

## always_fail_on

```python
def always_fail_on(self, pattern: str) -> 'MockChecker'
```

Add pattern that always fails.

---

## check

```python
async def check(self, proof_source: str, timeout_ms: int=30000) -> CheckerResult
```

Mock verification that returns configurable results.

---

## register

```python
def register(self, name: str, checker_class: type[ProofChecker]) -> None
```

Register a checker class.

---

## get

```python
def get(self, name: str) -> ProofChecker
```

Get a checker instance by name.

---

## available_checkers

```python
def available_checkers(self) -> list[str]
```

Return names of all available (installed) checkers.

---

## __init__

```python
def __init__(self, binary_path: str | None=None, *, verify_on_init: bool=True)
```

Initialize the Lean4 checker.

---

## name

```python
def name(self) -> str
```

Checker identifier.

---

## is_available

```python
def is_available(self) -> bool
```

True if Lean4 is installed and accessible.

---

## check

```python
async def check(self, proof_source: str, timeout_ms: int=30000) -> CheckerResult
```

Run Lean4 verification on proof source.

---

## __init__

```python
def __init__(self, binary_path: str | None=None, *, verify_on_init: bool=True)
```

Initialize the Verus checker.

---

## name

```python
def name(self) -> str
```

Checker identifier.

---

## is_available

```python
def is_available(self) -> bool
```

True if Verus is installed and accessible.

---

## check

```python
async def check(self, proof_source: str, timeout_ms: int=30000) -> CheckerResult
```

Run Verus verification on proof source.

---

## services.ashc.contracts

## contracts

```python
module contracts
```

**AGENTESE:** `concept.ashc.obligation`

ASHC Proof-Generation Contracts.

### Things to Know

ℹ️ All contracts are frozen dataclasses. Create new instances with updated fields, don't mutate existing ones. This enables safe composition and audit trails.

---

## ProofStatus

```python
class ProofStatus(Enum)
```

Status of a proof obligation or attempt.

### Things to Know

ℹ️ Use auto() for status values—we care about the semantic meaning, not the underlying integer. Comparison is by enum member, not value.

---

## ObligationSource

```python
class ObligationSource(Enum)
```

Source of a proof obligation.

---

## ProofObligation

```python
class ProofObligation
```

A property that needs to be proven.

### Examples
```python
>>> obl = ProofObligation(
```
```python
>>> obl.property
```

### Things to Know

ℹ️ ProofObligation is immutable. Create new obligations with updated context, don't mutate existing ones. Example: >>> obl = ProofObligation( ... id=ObligationId("obl-001"), ... property="∀ x: int. x + 0 == x", ... source=ObligationSource.TEST, ... source_location="test_math.py:42", ... ) >>> obl.property '∀ x: int. x + 0 == x'

---

## ProofAttempt

```python
class ProofAttempt
```

A single attempt to discharge a proof obligation.

### Things to Know

ℹ️ We store failed attempts too—they inform future searches. "What didn't work" is as valuable as "what worked." The tactics_that_failed set helps avoid repeating mistakes. Laws: 1. Attempts are immutable records 2. Failed attempts inform future searches (stigmergic learning) 3. duration_ms enables performance analysis

---

## VerifiedLemma

```python
class VerifiedLemma
```

A proven fact in the lemma database.

### Things to Know

ℹ️ VerifiedLemma includes the full proof—not just the statement. This enables proof reuse and composition.

---

## ProofSearchResult

```python
class ProofSearchResult
```

Result of a proof search session.

### Things to Know

ℹ️ ProofSearchResult is the ONLY mutable contract. It accumulates attempts during search, then becomes effectively immutable once search completes.

---

## ProofSearchConfig

```python
class ProofSearchConfig
```

Configuration for proof search phases.

### Things to Know

ℹ️ Tactic progressions are tuples (immutable). Quick phase uses simple tactics; deeper phases add more sophisticated ones.

ℹ️ Temperature is a hyper-parameter for LLM proof generation. Lower (0.1-0.3) for deterministic proofs, higher (0.5-0.7) for creative exploration. Not hardcoded per Kent's decision.

---

## CheckerResult

```python
class CheckerResult
```

Result from a proof checker (Dafny, Lean4, Verus).

### Things to Know

ℹ️ Dafny outputs to stderr even on success. Parse exit code, not output presence, to determine success.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary for persistence/API.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> ProofObligation
```

Deserialize from dictionary.

---

## with_context

```python
def with_context(self, *additional: str) -> ProofObligation
```

Return a new obligation with additional context.

### Examples
```python
>>> obl2 = obl.with_context("Hint: use induction on x")
```

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary for persistence/API.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> ProofAttempt
```

Deserialize from dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary for persistence/API.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> VerifiedLemma
```

Deserialize from dictionary.

---

## with_incremented_usage

```python
def with_incremented_usage(self) -> VerifiedLemma
```

Return a new lemma with incremented usage count.

---

## succeeded

```python
def succeeded(self) -> bool
```

True if a valid proof was found.

---

## tactics_that_failed

```python
def tactics_that_failed(self) -> set[str]
```

Tactics to avoid in future searches.

---

## tactics_that_succeeded

```python
def tactics_that_succeeded(self) -> set[str]
```

Tactics that worked in successful attempts.

---

## budget_remaining

```python
def budget_remaining(self) -> int
```

Remaining proof attempts in budget.

---

## avg_attempt_duration_ms

```python
def avg_attempt_duration_ms(self) -> float
```

Average duration of proof attempts in milliseconds.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary for persistence/API.

---

## total_budget

```python
def total_budget(self) -> int
```

Total proof attempts across all phases.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## is_timeout

```python
def is_timeout(self) -> bool
```

True if verification timed out.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## services.ashc.obligation

## obligation

```python
module obligation
```

**AGENTESE:** `concept.ashc.obligation`

Obligation Extraction: From Failures to Theorems.

### Things to Know

ℹ️ Context extraction is bounded to 5 lines. Large tracebacks would bloat obligations and slow proof search. Prefer relevant excerpts over complete dumps.

ℹ️ Assertion parsing is pattern-based, not AST-based. This is intentional—we want readable properties, not compiled forms.

---

## ObligationExtractor

```python
class ObligationExtractor
```

Extract proof obligations from various sources.

### Examples
```python
>>> extractor = ObligationExtractor()
```
```python
>>> obl = extractor.from_test_failure(
```
```python
>>> "∀" in obl.property
```

---

## extract_from_pytest_report

```python
def extract_from_pytest_report(report: dict[str, Any]) -> ProofObligation | None
```

Extract obligation from a pytest JSON report entry.

### Examples
```python
>>> report = {
```
```python
>>> obl = extract_from_pytest_report(report)
```
```python
>>> obl is not None
```

---

## from_test_failure

```python
def from_test_failure(self, test_name: str, assertion: str, traceback: str, source_file: str, line_number: int) -> ProofObligation
```

Extract obligation from a test failure.

### Examples
```python
>>> obl = extractor.from_test_failure(
```
```python
>>> obl.property
```

---

## from_type_signature

```python
def from_type_signature(self, path: str, input_type: str, output_type: str, effects: tuple[str, ...]=()) -> ProofObligation
```

Extract obligation from AD-013 typed AGENTESE path.

### Examples
```python
>>> obl = extractor.from_type_signature(
```
```python
>>> "BashRequest" in obl.property
```

---

## from_composition

```python
def from_composition(self, pipeline_name: str, agents: tuple[str, ...], expected_type: str) -> ProofObligation
```

Extract obligation from pipeline composition.

### Examples
```python
>>> obl = extractor.from_composition(
```
```python
>>> "composition" in obl.property.lower()
```

---

## obligations

```python
def obligations(self) -> list[ProofObligation]
```

All obligations extracted in this session.

---

## obligation_count

```python
def obligation_count(self) -> int
```

Number of obligations extracted.

---

## clear

```python
def clear(self) -> None
```

Clear all extracted obligations (start fresh session).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize extraction session to dictionary.

---

## services.ashc.persistence

## persistence

```python
module persistence
```

**AGENTESE:** `concept.ashc.lemma.`

ASHC Persistence: Postgres-backed LemmaDatabase via D-gent patterns.

### Things to Know

ℹ️ find_related() increments usage_count for returned lemmas. This is intentional—lemmas that help more become more visible.
  - *Verified in: `test_lemma_db.py::test_stigmergic_reinforcement`*

ℹ️ store() is idempotent on id. If a lemma with the same id exists, it's updated (not duplicated). This supports proof regeneration.
  - *Verified in: `test_lemma_db.py::test_store_idempotent`*

ℹ️ Keyword matching uses simple word overlap for now. Brain vectors are deferred to Phase 5 for semantic similarity.
  - *Verified in: `test_lemma_db.py::test_keyword_matching`*

---

## LemmaStats

```python
class LemmaStats
```

Statistics about the lemma database.

---

## PostgresLemmaDatabase

```python
class PostgresLemmaDatabase
```

Postgres-backed implementation of LemmaDatabase protocol.

### Examples
```python
>>> session_factory = get_session_factory()
```
```python
>>> lemma_db = PostgresLemmaDatabase(session_factory)
```
```python
>>> await lemma_db.store(verified_lemma)
```
```python
>>> related = await lemma_db.find_related("∀ x. x == x", limit=3)
```

### Things to Know

ℹ️ PostgresLemmaDatabase is stateless between calls. All state is in the database. Safe for concurrent access.
  - *Verified in: `test_lemma_db.py::test_concurrent_access`*

---

## __init__

```python
def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None
```

Initialize Postgres-backed lemma database.

---

## find_related

```python
def find_related(self, property_stmt: str, limit: int=3) -> list[VerifiedLemma]
```

Find lemmas related to a property statement.

---

## find_related_async

```python
async def find_related_async(self, property_stmt: str, limit: int=3) -> list[VerifiedLemma]
```

Find lemmas related to a property statement (async version).

---

## store

```python
def store(self, lemma: VerifiedLemma) -> None
```

Store a newly verified lemma.

---

## store_async

```python
async def store_async(self, lemma: VerifiedLemma) -> None
```

Store a newly verified lemma (async version).

---

## get_by_id

```python
async def get_by_id(self, lemma_id: str) -> VerifiedLemma | None
```

Get a specific lemma by ID.

---

## get_by_obligation

```python
async def get_by_obligation(self, obligation_id: str) -> VerifiedLemma | None
```

Get lemma by its origin obligation.

---

## list_recent

```python
async def list_recent(self, limit: int=10) -> list[VerifiedLemma]
```

List recently verified lemmas.

---

## list_most_used

```python
async def list_most_used(self, limit: int=10) -> list[VerifiedLemma]
```

List most frequently used lemmas.

---

## stats

```python
async def stats(self) -> LemmaStats
```

Get statistics about the lemma database.

---

## count

```python
async def count(self) -> int
```

Count total lemmas.

---

## services.ashc.search

## search

```python
module search
```

**AGENTESE:** `concept.ashc.prove`

LLM Proof Search: The Hallucination-Tolerant Pipeline.

### Things to Know

ℹ️ Temperature is a hyper-parameter in ProofSearchConfig, not hardcoded. Different obligations may benefit from different temperatures.
  - *Verified in: `test_search.py::test_temperature_configurable`*

ℹ️ Failed tactics are tracked SEPARATELY, not in obligation.context. This enables cross-attempt learning without bloating obligations.
  - *Verified in: `test_search.py::test_failed_tactics_not_repeated`*

---

## LemmaDatabase

```python
class LemmaDatabase(Protocol)
```

Protocol for lemma database access.

### Things to Know

ℹ️ Protocol > ABC for interfaces. Enables duck typing without inheritance coupling. See meta.md: "Protocol > ABC"

---

## InMemoryLemmaDatabase

```python
class InMemoryLemmaDatabase
```

In-memory stub for lemma database.

### Things to Know

ℹ️ This is a STUB, not the final implementation. It stores lemmas in memory only—they're lost on restart. Phase 4 adds D-gent persistence.

---

## ProofSearcher

```python
class ProofSearcher
```

LLM-assisted proof search with budget management.

### Examples
```python
>>> searcher = ProofSearcher(gateway, checker, lemma_db)
```
```python
>>> obl = ProofObligation(property="∀ x. x == x", ...)
```
```python
>>> result = await searcher.search(obl)
```
```python
>>> if result.succeeded:
```

### Things to Know

ℹ️ The searcher is stateless between calls. Each search() invocation is independent. Failed tactics are tracked PER SEARCH, not across searches.
  - *Verified in: `test_search.py::test_searcher_stateless`*

ℹ️ Budget is ATTEMPTS, not wall time. A slow checker can exhaust budget quickly. Monitor avg_attempt_duration_ms. (Evidence: test_search.py::test_budget_is_attempt_count) Example: >>> searcher = ProofSearcher(gateway, checker, lemma_db) >>> obl = ProofObligation(property="∀ x. x == x", ...) >>> result = await searcher.search(obl) >>> if result.succeeded: ... print(f"Proved! Lemma: {result.lemma.statement}")

---

## find_related

```python
def find_related(self, property_stmt: str, limit: int=3) -> list[VerifiedLemma]
```

Find lemmas related to a property statement.

---

## store

```python
def store(self, lemma: VerifiedLemma) -> None
```

Store a newly verified lemma.

---

## find_related

```python
def find_related(self, property_stmt: str, limit: int=3) -> list[VerifiedLemma]
```

Find lemmas with overlapping keywords.

---

## store

```python
def store(self, lemma: VerifiedLemma) -> None
```

Store a newly verified lemma.

---

## lemma_count

```python
def lemma_count(self) -> int
```

Number of stored lemmas.

---

## __init__

```python
def __init__(self, gateway: 'MorpheusGateway', checker: ProofChecker, lemma_db: LemmaDatabase | None=None, config: ProofSearchConfig | None=None)
```

Initialize proof searcher.

---

## config

```python
def config(self) -> ProofSearchConfig
```

Current search configuration.

---

## search

```python
async def search(self, obligation: ProofObligation) -> ProofSearchResult
```

Attempt to discharge a proof obligation.

### Examples
```python
>>> result = await searcher.search(obligation)
```
```python
>>> if result.succeeded:
```

---

## services.brain.__init__

## __init__

```python
module __init__
```

Brain Crown Jewel: Spatial Cathedral of Memory.

---

## services.brain.contracts

## contracts

```python
module contracts
```

Brain AGENTESE Contract Definitions.

---

## BrainManifestResponse

```python
class BrainManifestResponse
```

Brain health status manifest response.

---

## CaptureRequest

```python
class CaptureRequest
```

Request to capture content to holographic memory.

---

## CaptureResponse

```python
class CaptureResponse
```

Response after capturing content.

---

## SearchRequest

```python
class SearchRequest
```

Request for semantic search.

---

## SearchResultItem

```python
class SearchResultItem
```

Single search result item.

---

## SearchResponse

```python
class SearchResponse
```

Response for semantic search.

---

## SurfaceRequest

```python
class SurfaceRequest
```

Request for serendipitous surface from the void.

---

## SurfaceItem

```python
class SurfaceItem
```

Surfaced crystal item.

---

## SurfaceResponse

```python
class SurfaceResponse
```

Response for surface operation.

---

## GetRequest

```python
class GetRequest
```

Request to get specific crystal by ID.

---

## GetResponse

```python
class GetResponse
```

Response for get crystal operation.

---

## RecentRequest

```python
class RecentRequest
```

Request for recent crystals.

---

## ByTagRequest

```python
class ByTagRequest
```

Request for crystals by tag.

---

## DeleteRequest

```python
class DeleteRequest
```

Request to delete a crystal.

---

## DeleteResponse

```python
class DeleteResponse
```

Response after deleting a crystal.

---

## HealResponse

```python
class HealResponse
```

Response after healing ghost memories.

---

## TopologyNode

```python
class TopologyNode
```

A node in the brain topology.

---

## TopologyEdge

```python
class TopologyEdge
```

An edge between topology nodes.

---

## TopologyStats

```python
class TopologyStats
```

Statistics for brain topology.

---

## TopologyRequest

```python
class TopologyRequest
```

Request for brain topology.

---

## TopologyResponse

```python
class TopologyResponse
```

Response for brain topology visualization.

---

## services.brain.node

## node

```python
module node
```

Brain AGENTESE Node: @node("self.memory")

---

## BrainManifestRendering

```python
class BrainManifestRendering
```

Rendering for brain status manifest.

---

## CaptureRendering

```python
class CaptureRendering
```

Rendering for capture result.

---

## SearchRendering

```python
class SearchRendering
```

Rendering for search results.

---

## BrainNode

```python
class BrainNode(BaseLogosNode)
```

AGENTESE node for Brain Crown Jewel.

### Examples
```python
>>> POST /agentese/self/memory/capture
```
```python
>>> {"content": "Python is great for data science"}
```
```python
>>> await logos.invoke("self.memory.capture", observer, content="...")
```
```python
>>> kgents brain capture "..."
```

### Things to Know

ℹ️ BrainNode REQUIRES brain_persistence dependency. Without it, instantiation fails with TypeError—this is intentional! It enables Logos fallback to SelfMemoryContext when DI isn't configured.
  - *Verified in: `test_node.py::TestBrainNodeRegistration::test_node_requires_persistence`*

ℹ️ Affordances vary by observer archetype. Guests can only search, newcomers can capture, developers can delete. Check archetype before assuming full access.
  - *Verified in: `test_node.py::TestBrainNodeAffordances`*

ℹ️ Every BrainNode invocation emits a Mark (WARP Law 3). Don't add manual tracing—the gateway handles it at _invoke_path().
  - *Verified in: `test_node.py::TestBrainWARPIntegration`*

ℹ️ crystal_id can come from either "crystal_id" or "id" kwargs. The get/delete aspects check both for backward compatibility.
  - *Verified in: `test_node.py::TestBrainNodeGet::test_get_without_id_returns_error`*

---

## __init__

```python
def __init__(self, brain_persistence: BrainPersistence) -> None
```

Initialize BrainNode.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `self.memory.manifest`

Manifest brain status to observer.

---

## services.brain.persistence

## persistence

```python
module persistence
```

Brain Persistence: TableAdapter + D-gent integration for Brain Crown Jewel.

### Things to Know

🚨 **Critical:** Dual-track storage means Crystal table AND D-gent must both succeed. If one fails after the other succeeds, you get "ghost" memories.
  - *Verified in: `test_brain_persistence.py::test_heal_ghosts`*

🚨 **Critical:** capture() returns immediately but trace recording is fire-and-forget. Never await the trace task or you'll block the hot path.
  - *Verified in: `test_brain_persistence.py::test_capture_performance`*

ℹ️ search() updates access_count via touch(). High-frequency searches will cause write amplification. Consider batching access updates.
  - *Verified in: `test_brain_persistence.py::test_access_tracking`*

---

## CaptureResult

```python
class CaptureResult
```

Result of a capture operation.

---

## SearchResult

```python
class SearchResult
```

Result of a search operation.

---

## BrainStatus

```python
class BrainStatus
```

Brain health status.

---

## BrainPersistence

```python
class BrainPersistence
```

Persistence layer for Brain Crown Jewel.

---

## capture

```python
async def capture(self, content: str, tags: list[str] | None=None, source_type: str='capture', source_ref: str | None=None, metadata: dict[str, Any] | None=None) -> CaptureResult
```

**AGENTESE:** `self.memory.capture`

Capture content to holographic memory.

---

## search

```python
async def search(self, query: str, limit: int=10, tags: list[str] | None=None) -> list[SearchResult]
```

**AGENTESE:** `self.memory.ghost.surface`

Semantic search for similar memories.

---

## surface

```python
async def surface(self, context: str | None=None, entropy: float=0.7) -> SearchResult | None
```

**AGENTESE:** `void.memory.surface`

Surface a serendipitous memory from the void.

---

## manifest

```python
async def manifest(self) -> BrainStatus
```

**AGENTESE:** `self.memory.manifest`

Get brain health status.

---

## get_by_id

```python
async def get_by_id(self, crystal_id: str) -> SearchResult | None
```

Get a specific crystal by ID.

---

## list_recent

```python
async def list_recent(self, limit: int=10) -> list[SearchResult]
```

List recent crystals.

---

## list_by_tag

```python
async def list_by_tag(self, tag: str, limit: int=10) -> list[SearchResult]
```

List crystals with a specific tag.

---

## delete

```python
async def delete(self, crystal_id: str) -> bool
```

Delete a crystal and its D-gent datum.

---

## heal_ghosts

```python
async def heal_ghosts(self) -> int
```

Heal ghost memories (crystals without D-gent datums).

---

## services.conductor.__init__

## __init__

```python
module __init__
```

**AGENTESE:** `self.conductor.`

Conductor Crown Jewel: Session orchestration for CLI v7.

---

## services.conductor.a2a

## a2a

```python
module a2a
```

A2A Protocol: Agent-to-Agent messaging via SynergyBus.

---

## A2AMessageType

```python
class A2AMessageType(Enum)
```

Types of agent-to-agent messages.

---

## A2AMessage

```python
class A2AMessage
```

Message between agents.

---

## A2ATopics

```python
class A2ATopics
```

Topic namespace for A2A events on WitnessSynergyBus.

---

## A2AChannel

```python
class A2AChannel
```

Agent-to-agent communication channel.

---

## A2ARegistry

```python
class A2ARegistry
```

Registry of active A2A channels.

---

## get_a2a_registry

```python
def get_a2a_registry() -> A2ARegistry
```

Get the global A2A registry.

---

## reset_a2a_registry

```python
def reset_a2a_registry() -> None
```

Reset the global A2A registry (for testing).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for transmission.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> 'A2AMessage'
```

Deserialize from transmission.

---

## create_response

```python
def create_response(self, payload: dict[str, Any]) -> 'A2AMessage'
```

Create a response to this message.

---

## for_type

```python
def for_type(cls, message_type: A2AMessageType) -> str
```

Get topic for message type.

---

## __init__

```python
def __init__(self, agent_id: str)
```

Create a channel for an agent.

---

## send

```python
async def send(self, message: A2AMessage) -> None
```

Send a message to another agent.

---

## request

```python
async def request(self, to_agent: str, payload: dict[str, Any], timeout: float=30.0) -> A2AMessage
```

Request/response pattern with timeout.

---

## respond

```python
async def respond(self, request: A2AMessage, payload: dict[str, Any]) -> None
```

Respond to a request.

---

## handoff

```python
async def handoff(self, to_agent: str, context: dict[str, Any], conversation: list[dict[str, Any]] | None=None) -> None
```

Hand off work to another agent with full context.

---

## notify

```python
async def notify(self, to_agent: str, payload: dict[str, Any]) -> None
```

Send a notification (no response expected).

---

## broadcast

```python
async def broadcast(self, payload: dict[str, Any]) -> None
```

Broadcast to all agents.

---

## heartbeat

```python
async def heartbeat(self) -> None
```

Send a heartbeat signal.

---

## start_subscription

```python
def start_subscription(self) -> None
```

Start subscribing to A2A messages for this agent.

---

## stop_subscription

```python
def stop_subscription(self) -> None
```

Stop subscribing to A2A messages.

---

## subscribe

```python
async def subscribe(self) -> AsyncIterator[A2AMessage]
```

Subscribe to messages addressed to this agent.

---

## receive_one

```python
async def receive_one(self, timeout: float=30.0) -> A2AMessage | None
```

Receive a single message with timeout.

---

## register

```python
def register(self, channel: A2AChannel) -> None
```

Register a channel.

---

## unregister

```python
def unregister(self, agent_id: str) -> None
```

Unregister a channel.

---

## get

```python
def get(self, agent_id: str) -> A2AChannel | None
```

Get a channel by agent ID.

---

## list_agents

```python
def list_agents(self) -> list[str]
```

List all registered agent IDs.

---

## clear

```python
def clear(self) -> None
```

Clear all channels (for testing).

---

## handler

```python
async def handler(topic: str, event: Any) -> None
```

Handle incoming A2A messages.

---

## services.conductor.behaviors

## behaviors

```python
module behaviors
```

Cursor Behaviors: Personality-driven agent movement patterns.

---

## CursorBehavior

```python
class CursorBehavior(Enum)
```

Agent cursor behavior patterns with rich personality.

---

## Position

```python
class Position
```

2D position for canvas rendering.

---

## FocusPoint

```python
class FocusPoint
```

A point of focus in the AGENTESE graph.

---

## HumanFocusTracker

```python
class HumanFocusTracker
```

Tracks human focus for behavior integration.

---

## AGENTESEGraph

```python
class AGENTESEGraph(Protocol)
```

Protocol for AGENTESE graph navigation.

---

## BehaviorAnimator

```python
class BehaviorAnimator
```

Animates agent cursor with behavior-driven movement.

---

## BehaviorModulator

```python
class BehaviorModulator
```

Modulates behavior based on context.

---

## emoji

```python
def emoji(self) -> str
```

Visual indicator reflecting personality.

---

## description

```python
def description(self) -> str
```

Human-readable personality description.

---

## follow_strength

```python
def follow_strength(self) -> float
```

How strongly this behavior tracks human focus (0.0-1.0).

---

## exploration_tendency

```python
def exploration_tendency(self) -> float
```

How likely to explore adjacent nodes (0.0-1.0).

---

## suggestion_probability

```python
def suggestion_probability(self) -> float
```

Probability of making a suggestion per second (0.0-1.0).

---

## movement_smoothness

```python
def movement_smoothness(self) -> float
```

How smooth the movement interpolation is (0.0-1.0).

---

## preferred_states

```python
def preferred_states(self) -> frozenset[CursorState]
```

States this behavior tends toward.

---

## circadian_sensitivity

```python
def circadian_sensitivity(self) -> float
```

How much circadian phase affects behavior (0.0-1.0).

---

## describe_for_phase

```python
def describe_for_phase(self, phase: CircadianPhase) -> str
```

Get behavior description modulated by circadian phase.

---

## distance_to

```python
def distance_to(self, other: 'Position') -> float
```

Euclidean distance.

---

## lerp

```python
def lerp(self, target: 'Position', t: float) -> 'Position'
```

Linear interpolation toward target.

---

## age_seconds

```python
def age_seconds(self) -> float
```

Time since this focus was set.

---

## current

```python
def current(self) -> FocusPoint | None
```

Most recent focus point.

---

## velocity

```python
def velocity(self) -> Position
```

Estimated velocity of focus movement.

---

## is_stationary

```python
def is_stationary(self) -> bool
```

True if focus hasn't moved recently.

---

## focus_duration

```python
def focus_duration(self) -> float
```

How long focus has been on current path.

---

## update

```python
def update(self, path: str, position: Position) -> None
```

Record new focus point.

---

## get_recent_paths

```python
def get_recent_paths(self, seconds: float=30.0) -> list[str]
```

Get unique paths visited in the last N seconds.

---

## get_connected_paths

```python
def get_connected_paths(self, path: str) -> list[str]
```

Get paths directly connected to this path.

---

## get_position

```python
def get_position(self, path: str) -> Position | None
```

Get canvas position for a path.

---

## get_all_paths

```python
def get_all_paths(self) -> list[str]
```

Get all registered paths.

---

## animate

```python
def animate(self, human_focus: HumanFocusTracker, graph: AGENTESEGraph | None, dt: float, phase: CircadianPhase | None=None) -> tuple[Position, str | None]
```

Compute next position and optional path.

---

## should_suggest

```python
def should_suggest(self, dt: float) -> bool
```

Check if this behavior should make a suggestion now.

---

## suggest_state

```python
def suggest_state(self) -> CursorState
```

Get preferred cursor state for this behavior.

---

## get_effective_behavior

```python
def get_effective_behavior(self, human_focus: HumanFocusTracker, task_urgency: float=0.5, phase: CircadianPhase | None=None) -> CursorBehavior
```

Compute effective behavior given current context.

---

## services.conductor.bus_bridge

## bus_bridge

```python
module bus_bridge
```

Bus Bridge: Cross-bus event forwarding for CLI v7 Phase 7 (Live Flux).

### Things to Know

ℹ️ wire_a2a_to_global_synergy() is idempotent - calling it twice returns the SAME unsubscribe function. This prevents duplicate bridging but means you cannot create multiple independent bridges.
  - *Verified in: `test_bus_bridge.py::TestBusBridgeLifecycle::test_double_wire_is_idempotent`*

ℹ️ Malformed A2A events do NOT crash the bridge - graceful degradation. Missing fields like from_agent/to_agent are replaced with "unknown". The bridge continues processing after errors, so a bad event won't break the entire A2A visibility pipeline.
  - *Verified in: `test_bus_bridge.py::TestBridgeErrorHandling::test_malformed_event_doesnt_crash_bridge`*

---

## wire_a2a_to_global_synergy

```python
def wire_a2a_to_global_synergy() -> Callable[[], None]
```

Bridge A2A events from WitnessSynergyBus to global SynergyBus.

---

## unwire_a2a_bridge

```python
def unwire_a2a_bridge() -> None
```

Stop the A2A bridge.

---

## is_bridge_active

```python
def is_bridge_active() -> bool
```

Check if the A2A bridge is currently active.

---

## bridge_a2a

```python
async def bridge_a2a(topic: str, event: dict[str, Any]) -> None
```

Bridge A2A events to global SynergyBus.

---

## services.conductor.contracts

## contracts

```python
module contracts
```

File I/O Contracts: Type definitions for world.file operations.

---

## FileReadRequest

```python
class FileReadRequest
```

Request to read a file.

---

## FileReadResponse

```python
class FileReadResponse
```

Response from reading a file.

---

## EditError

```python
class EditError(Enum)
```

Error types for file edit operations.

---

## FileEditRequest

```python
class FileEditRequest
```

Request to edit a file using exact string replacement.

---

## FileEditResponse

```python
class FileEditResponse
```

Response from editing a file.

---

## FileWriteRequest

```python
class FileWriteRequest
```

Request to write a new file (overwrite semantics).

---

## FileWriteResponse

```python
class FileWriteResponse
```

Response from writing a file.

---

## FileGlobRequest

```python
class FileGlobRequest
```

Request to glob for files by pattern.

---

## FileGlobResponse

```python
class FileGlobResponse
```

Response from glob operation.

---

## FileGrepRequest

```python
class FileGrepRequest
```

Request to grep for content.

---

## FileGrepMatch

```python
class FileGrepMatch
```

A single grep match.

---

## FileGrepResponse

```python
class FileGrepResponse
```

Response from grep operation.

---

## ArtifactType

```python
class ArtifactType(Enum)
```

Types of artifacts that can be output.

---

## OutputArtifactRequest

```python
class OutputArtifactRequest
```

Request to write an artifact to disk.

---

## OutputArtifactResponse

```python
class OutputArtifactResponse
```

Response from artifact output.

---

## FileCacheEntry

```python
class FileCacheEntry
```

Internal cache entry for read-before-edit validation.

---

## FileEditedPayload

```python
class FileEditedPayload
```

Payload for FILE_EDITED synergy event.

---

## FileCreatedPayload

```python
class FileCreatedPayload
```

Payload for FILE_CREATED synergy event.

---

## is_fresh

```python
def is_fresh(self, max_age_seconds: float=300) -> bool
```

Check if cache entry is still valid.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for persistence.

---

## services.conductor.file_guard

## file_guard

```python
module file_guard
```

FileEditGuard: Read-before-edit enforcement.

### Things to Know

🚨 **Critical:** Edits without prior read fail with EditError.NOT_READ. The guard returns a structured error response rather than raising, so you MUST check response.success before assuming the edit worked.
  - *Verified in: `test_file_guard.py::TestEditOperations::test_edit_requires_prior_read`*

ℹ️ Non-unique old_string returns EditError.NOT_UNIQUE, not an exception. Use replace_all=True when you intentionally want to replace all occurrences. The error response includes a suggestion to help the user.
  - *Verified in: `test_file_guard.py::TestEditOperations::test_edit_string_not_unique`*

---

## FileGuardError

```python
class FileGuardError(Exception)
```

Base error for file guard operations.

---

## NotReadError

```python
class NotReadError(FileGuardError)
```

File was not read before edit attempt.

---

## StringNotFoundError

```python
class StringNotFoundError(FileGuardError)
```

Old string not found in file.

---

## StringNotUniqueError

```python
class StringNotUniqueError(FileGuardError)
```

Old string appears multiple times.

---

## FileChangedError

```python
class FileChangedError(FileGuardError)
```

File was modified since last read.

---

## FileEditGuard

```python
class FileEditGuard
```

Enforces Claude Code's read-before-edit pattern.

---

## get_file_guard

```python
def get_file_guard() -> FileEditGuard
```

Get or create the singleton FileEditGuard.

---

## reset_file_guard

```python
def reset_file_guard() -> None
```

Reset the singleton (for testing).

---

## set_event_emitter

```python
def set_event_emitter(self, emitter: Any) -> None
```

Inject the synergy event emitter.

---

## read_file

```python
async def read_file(self, request: FileReadRequest | str, *, agent_id: str='unknown') -> FileReadResponse
```

Read a file and cache for subsequent edits.

---

## edit_file

```python
async def edit_file(self, request: FileEditRequest, *, agent_id: str='unknown') -> FileEditResponse
```

Edit a file using exact string replacement.

---

## write_file

```python
async def write_file(self, request: FileWriteRequest, *, agent_id: str='unknown') -> FileWriteResponse
```

Write a new file (or overwrite existing).

---

## can_edit

```python
async def can_edit(self, path: str) -> bool
```

Check if a file can be edited (has been read recently).

---

## invalidate

```python
async def invalidate(self, path: str) -> bool
```

Remove a file from cache.

---

## clear_cache

```python
async def clear_cache(self) -> int
```

Clear entire cache. Returns number of entries cleared.

---

## get_statistics

```python
def get_statistics(self) -> dict[str, Any]
```

Get guard statistics.

---

## services.conductor.flux

## flux

```python
module flux
```

ConductorFlux: Reactive event integration for CLI v7 Phase 7 (Live Flux).

---

## ConductorEventType

```python
class ConductorEventType(Enum)
```

Event types for conductor-level fan-out.

---

## ConductorEvent

```python
class ConductorEvent
```

Unified event type for conductor fan-out.

---

## ConductorFlux

```python
class ConductorFlux
```

Reactive agent for CLI v7 event integration.

---

## get_conductor_flux

```python
def get_conductor_flux() -> ConductorFlux
```

Get the global ConductorFlux instance.

---

## reset_conductor_flux

```python
def reset_conductor_flux() -> None
```

Reset the global flux (for testing).

---

## start_conductor_flux

```python
def start_conductor_flux() -> ConductorFlux
```

Start the global ConductorFlux.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for WebSocket/SSE.

---

## running

```python
def running(self) -> bool
```

Check if flux is currently running.

---

## subscribe

```python
def subscribe(self, subscriber: ConductorEventSubscriber) -> Callable[[], None]
```

Subscribe to ConductorEvents.

---

## start

```python
def start(self) -> None
```

Start the ConductorFlux.

---

## stop

```python
def stop(self) -> None
```

Stop the ConductorFlux.

---

## handle

```python
async def handle(self, event: SynergyEvent) -> SynergyResult
```

Route event to ConductorFlux.

---

## services.conductor.operad

## operad

```python
module operad
```

SWARM_OPERAD: Composition grammar for agent swarms.

---

## create_swarm_operad

```python
def create_swarm_operad() -> Operad
```

Create the Swarm Operad.

---

## get_swarm_operad

```python
def get_swarm_operad() -> Operad
```

Get the SWARM_OPERAD instance.

---

## compose_spawn_delegate_workflow

```python
def compose_spawn_delegate_workflow(role: SwarmRole=RESEARCHER, coordinator: str='coordinator', worker: str='worker') -> PolyAgent[Any, Any, Any]
```

Compose a spawn -> delegate workflow.

---

## compose_parallel_research_workflow

```python
def compose_parallel_research_workflow(num_agents: int=3) -> PolyAgent[Any, Any, Any]
```

Compose a parallel research workflow.

---

## compose_implement_review_workflow

```python
def compose_implement_review_workflow(implementer: str='implementer', reviewer: str='reviewer') -> PolyAgent[Any, Any, Any]
```

Compose an implement -> review workflow.

---

## services.conductor.persistence

## persistence

```python
module persistence
```

WindowPersistence: D-gent integration for ConversationWindow state.

### Things to Know

🚨 **Critical:** Corrupted JSON data returns None from load_window(), not an exception. Always handle the None case when loading - the user may have edited the underlying storage or the data may be from an incompatible version.
  - *Verified in: `test_persistence.py::TestWindowPersistenceLoad::test_load_window_handles_corrupted_data`*

ℹ️ Window persistence is independent from ChatSession lifecycle. A window can exist in D-gent even after its session is gone. Use exists() to check before assuming a load will succeed.
  - *Verified in: `test_persistence.py::TestWindowPersistenceIntegration::test_exists_check`*

---

## WindowPersistence

```python
class WindowPersistence
```

Persistence layer for ConversationWindow using D-gent.

---

## get_window_persistence

```python
def get_window_persistence() -> WindowPersistence
```

Get or create the singleton WindowPersistence instance.

---

## reset_window_persistence

```python
def reset_window_persistence() -> None
```

Reset the singleton (for testing).

---

## __init__

```python
def __init__(self, dgent: DgentRouter | None=None, namespace: str='conductor_windows')
```

Initialize persistence layer.

---

## save_window

```python
async def save_window(self, session_id: str, window: 'ConversationWindow') -> str
```

Save a ConversationWindow to D-gent storage.

---

## load_window

```python
async def load_window(self, session_id: str) -> 'ConversationWindow | None'
```

Load a ConversationWindow from D-gent storage.

---

## delete_window

```python
async def delete_window(self, session_id: str) -> bool
```

Delete a persisted window.

---

## exists

```python
async def exists(self, session_id: str) -> bool
```

Check if a window exists for a session.

---

## list_windows

```python
async def list_windows(self, *, limit: int=100) -> list[tuple[str, dict[str, str]]]
```

List all persisted windows.

---

## services.conductor.presence

## presence

```python
module presence
```

Agent Presence: Visible cursor states and activity indicators.

### Things to Know

🚨 **Critical:** Invalid state transitions are REJECTED silently (return False). WAITING cannot go directly to SUGGESTING - it must pass through WORKING or FOLLOWING first. Always check transition_to() return value.
  - *Verified in: `test_presence.py::TestAgentCursor::test_transition_to_invalid`*

ℹ️ States cannot transition to themselves - no self-loops allowed. The directed graph enforces this constraint to prevent infinite loops.
  - *Verified in: `test_presence.py::TestCursorStateTransitions::test_no_self_transitions`*

---

## CursorState

```python
class CursorState(Enum)
```

Agent cursor state with rich properties.

---

## CircadianPhase

```python
class CircadianPhase(Enum)
```

Time of day phases for UI modulation.

---

## AgentCursor

```python
class AgentCursor
```

Represents an agent's visible presence in the workspace.

---

## PresenceEventType

```python
class PresenceEventType(Enum)
```

Types of presence events.

---

## PresenceUpdate

```python
class PresenceUpdate
```

Event emitted when agent presence changes.

---

## PresenceChannel

```python
class PresenceChannel
```

Broadcast channel for real-time cursor positions.

---

## get_presence_channel

```python
def get_presence_channel() -> PresenceChannel
```

Get or create the singleton PresenceChannel.

---

## reset_presence_channel

```python
def reset_presence_channel() -> None
```

Reset the singleton (for testing).

---

## render_presence_footer

```python
def render_presence_footer(cursors: list[AgentCursor], teaching_mode: bool=False, width: int=80) -> str
```

Render presence footer for CLI output.

---

## emoji

```python
def emoji(self) -> str
```

Visual indicator for CLI/UI display.

---

## color

```python
def color(self) -> str
```

CLI color for Rich/terminal output.

---

## tailwind_color

```python
def tailwind_color(self) -> str
```

Tailwind CSS class for web UI.

---

## animation_speed

```python
def animation_speed(self) -> float
```

Animation speed multiplier (0.0-1.0).

---

## description

```python
def description(self) -> str
```

Human-readable description of state.

---

## can_transition_to

```python
def can_transition_to(self) -> frozenset['CursorState']
```

Valid state transitions (Pattern #9: Directed State Cycle).

---

## can_transition

```python
def can_transition(self, target: 'CursorState') -> bool
```

Check if transition to target state is valid.

---

## from_hour

```python
def from_hour(cls, hour: int) -> 'CircadianPhase'
```

Get phase from hour (0-23).

---

## current

```python
def current(cls) -> 'CircadianPhase'
```

Get current phase based on local time.

---

## tempo_modifier

```python
def tempo_modifier(self) -> float
```

Animation tempo modifier.

---

## warmth

```python
def warmth(self) -> float
```

Color warmth (0.0 = cool, 1.0 = warm).

---

## emoji

```python
def emoji(self) -> str
```

Delegate to state emoji.

---

## color

```python
def color(self) -> str
```

Delegate to state color.

---

## effective_animation_speed

```python
def effective_animation_speed(self) -> float
```

Animation speed with circadian modulation.

---

## transition_to

```python
def transition_to(self, new_state: CursorState) -> bool
```

Attempt state transition.

---

## update_activity

```python
def update_activity(self, activity: str, focus_path: str | None=None) -> None
```

Update activity description and optional focus path.

---

## behavior_emoji

```python
def behavior_emoji(self) -> str
```

Get emoji combining state and behavior.

---

## to_cli

```python
def to_cli(self, teaching_mode: bool=False) -> str
```

Render for CLI output.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for persistence/API.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> 'AgentCursor'
```

Deserialize from dict.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for SSE/WebSocket.

---

## __init__

```python
def __init__(self, max_queue_size: int=100)
```

Initialize presence channel.

---

## active_cursors

```python
def active_cursors(self) -> list[AgentCursor]
```

Get all active cursors.

---

## subscriber_count

```python
def subscriber_count(self) -> int
```

Number of active subscribers.

---

## join

```python
async def join(self, cursor: AgentCursor) -> None
```

Register an agent cursor.

---

## leave

```python
async def leave(self, agent_id: str) -> bool
```

Unregister an agent cursor.

---

## broadcast

```python
async def broadcast(self, cursor: AgentCursor) -> int
```

Broadcast cursor update to all subscribers.

---

## subscribe

```python
async def subscribe(self) -> AsyncIterator[PresenceUpdate]
```

Subscribe to presence updates.

---

## get_cursor

```python
def get_cursor(self, agent_id: str) -> AgentCursor | None
```

Get cursor by agent ID.

---

## get_presence_snapshot

```python
async def get_presence_snapshot(self) -> dict[str, Any]
```

Get current presence state as a snapshot.

---

## services.conductor.summarizer

## summarizer

```python
module summarizer
```

Summarizer: LLM-powered conversation summarization.

---

## SummarizationResult

```python
class SummarizationResult
```

Result of a summarization operation.

---

## Summarizer

```python
class Summarizer
```

LLM-powered conversation summarizer.

---

## create_summarizer

```python
def create_summarizer(morpheus: 'MorpheusPersistence | None'=None, model: str | None=None) -> Summarizer
```

Create a Summarizer instance.

---

## savings

```python
def savings(self) -> int
```

Tokens saved by summarization.

---

## summarize

```python
async def summarize(self, messages: list['ContextMessage'], *, force_aggressive: bool=False) -> SummarizationResult
```

Summarize a list of messages.

---

## summarize_sync

```python
def summarize_sync(self, messages: list['ContextMessage']) -> str
```

Synchronous wrapper for use with ConversationWindow.

---

## get_statistics

```python
def get_statistics(self) -> dict[str, Any]
```

Get summarization statistics.

---

## services.conductor.swarm

## swarm

```python
module swarm
```

SwarmRole: Role = CursorBehavior x TrustLevel

---

## SwarmRole

```python
class SwarmRole
```

Role = Behavior x Trust

### Examples
```python
>>> RESEARCHER = SwarmRole(CursorBehavior.EXPLORER, TrustLevel.READ_ONLY)
```
```python
>>> - Behavior: Curious wanderer, independent discovery
```
```python
>>> - Trust: Can only read, not modify
```

---

## SpawnSignal

```python
class SpawnSignal
```

A signal contributing to agent selection.

---

## SpawnDecision

```python
class SpawnDecision
```

Result of spawn signal aggregation.

---

## SwarmSpawner

```python
class SwarmSpawner
```

Spawns agents using signal aggregation (Pattern #4).

---

## create_swarm_role

```python
def create_swarm_role(behavior: CursorBehavior | str, trust: str) -> SwarmRole
```

Factory for creating SwarmRole with string inputs.

---

## trust

```python
def trust(self) -> Any
```

Get the actual TrustLevel enum value.

---

## name

```python
def name(self) -> str
```

Human-readable role name.

---

## emoji

```python
def emoji(self) -> str
```

Combined emoji showing behavior + trust.

---

## capabilities

```python
def capabilities(self) -> FrozenSet[str]
```

Derived from trust level, NOT stored.

---

## description

```python
def description(self) -> str
```

Human-readable description.

---

## can_execute

```python
def can_execute(self, operation: str) -> bool
```

Check if role can execute an operation.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for API/persistence.

---

## evaluate_role

```python
def evaluate_role(self, task: str, context: dict[str, Any] | None=None) -> SpawnDecision
```

Evaluate best role for task using signal aggregation.

---

## spawn

```python
async def spawn(self, agent_id: str, task: str, context: dict[str, Any] | None=None) -> AgentCursor | None
```

Spawn an agent if allowed.

---

## despawn

```python
async def despawn(self, agent_id: str) -> bool
```

Remove an agent from the swarm.

---

## get_agent

```python
def get_agent(self, agent_id: str) -> AgentCursor | None
```

Get an active agent by ID.

---

## list_agents

```python
def list_agents(self) -> list[AgentCursor]
```

List all active agents.

---

## active_count

```python
def active_count(self) -> int
```

Number of active agents.

---

## at_capacity

```python
def at_capacity(self) -> bool
```

Whether the swarm is at max capacity.

---

## services.conductor.window

## window

```python
module window
```

ConversationWindow: Bounded history with context strategies.

---

## ContextMessage

```python
class ContextMessage
```

A message in the conversation window.

---

## WindowSnapshot

```python
class WindowSnapshot
```

Immutable snapshot of window state.

---

## ContextSegment

```python
class ContextSegment
```

A segment of the context window for visualization.

---

## ContextBreakdown

```python
class ContextBreakdown
```

Full breakdown of context window composition.

---

## ConversationWindow

```python
class ConversationWindow
```

Bounded conversation history with context strategies.

---

## create_window_from_config

```python
def create_window_from_config(config: 'ContextStrategy', max_turns: int=35, context_window_tokens: int=8000) -> ConversationWindow
```

Create a ConversationWindow from ChatConfig strategy.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for LLM context.

---

## to_llm_format

```python
def to_llm_format(self) -> dict[str, str]
```

Format for LLM API (Anthropic/OpenAI compatible).

---

## __init__

```python
def __init__(self, max_turns: int=35, strategy: str='summarize', context_window_tokens: int=8000, summarization_threshold: float=0.8, summarizer: Callable[[list[ContextMessage]], str] | None=None)
```

Initialize conversation window.

---

## turn_count

```python
def turn_count(self) -> int
```

Number of turns in working memory.

---

## total_turn_count

```python
def total_turn_count(self) -> int
```

Total turns including summarized history.

---

## has_summary

```python
def has_summary(self) -> bool
```

Whether a summary exists.

---

## total_tokens

```python
def total_tokens(self) -> int
```

Total tokens in working memory (including summary).

---

## utilization

```python
def utilization(self) -> float
```

Context utilization as percentage (0.0-1.0).

---

## is_at_capacity

```python
def is_at_capacity(self) -> bool
```

Whether window is at max turns.

---

## needs_summarization

```python
def needs_summarization(self) -> bool
```

Whether summarization should be triggered.

---

## add_turn

```python
def add_turn(self, user_message: str, assistant_response: str, *, user_metadata: dict[str, Any] | None=None, assistant_metadata: dict[str, Any] | None=None) -> None
```

Add a conversation turn to the window.

---

## set_summarizer

```python
def set_summarizer(self, summarizer: Callable[[list[ContextMessage]], str]) -> None
```

Inject the summarizer function.

---

## set_system_prompt

```python
def set_system_prompt(self, prompt: str | None) -> None
```

Set the system prompt (prepended to context).

---

## get_context_messages

```python
def get_context_messages(self) -> list[ContextMessage]
```

Get messages for LLM context.

---

## get_context_for_llm

```python
def get_context_for_llm(self) -> list[dict[str, str]]
```

Get context in LLM API format.

---

## get_recent_turns

```python
def get_recent_turns(self, limit: int | None=None) -> list[tuple[str, str]]
```

Get recent turns as (user, assistant) tuples.

---

## snapshot

```python
def snapshot(self) -> WindowSnapshot
```

Create immutable snapshot of window state.

---

## get_context_breakdown

```python
def get_context_breakdown(self) -> ContextBreakdown
```

Get breakdown of context window composition.

---

## reset

```python
def reset(self) -> None
```

Clear the window (fresh start).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize window state.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> ConversationWindow
```

Deserialize window state.

---

## services.interactive_text.__init__

## __init__

```python
module __init__
```

Interactive Text Crown Jewel: Meaning Token Frontend Architecture.

### Things to Know

ℹ️ Six core token types are lazy-registered via TokenRegistry._ensure_initialized(). First call to get()/recognize() triggers registration of CORE_TOKEN_DEFINITIONS.
  - *Verified in: `test_registry.py::test_core_tokens_registered`*

ℹ️ DocumentPolynomial is stateless—state lives in caller, not polynomial. Each transition() call takes state as input, returns (new_state, output).
  - *Verified in: `test_properties.py::test_polynomial_stateless`*

🚨 **Critical:** Observer.density affects projection output—COMPACT truncates, SPACIOUS shows all. Always pass observer to projection; don't assume COMFORTABLE default.
  - *Verified in: `test_projectors.py::test_density_affects_output`*

ℹ️ DocumentSheaf.glue() requires compatible local views—SheafConditionError if conflict. Verify sheaf conditions before attempting multi-view merge.
  - *Verified in: `test_properties.py::test_sheaf_conflict_detection`*

---

## services.interactive_text.contracts

## contracts

```python
module contracts
```

**AGENTESE:** `concept.document.contracts`

Interactive Text AGENTESE Contract Definitions.

### Things to Know

ℹ️ Observer.capabilities is frozenset—immutable by design. Create new Observer with updated capabilities, don't mutate.
  - *Verified in: `test_contracts.py::test_observer_immutability`*

🚨 **Critical:** TokenPattern validates on __post_init__—empty name raises ValueError. Always provide a non-empty name when constructing TokenPattern.
  - *Verified in: `test_contracts.py::test_token_pattern_validation`*

🚨 **Critical:** MeaningToken.token_id default uses position (type:start:end). Custom implementations may override but must remain unique per doc.
  - *Verified in: `test_contracts.py::test_token_id_uniqueness`*

ℹ️ InteractionResult.not_available() vs failure()—semantic difference. not_available = affordance disabled; failure = execution error.
  - *Verified in: `test_contracts.py::test_interaction_result_types`*

---

## AffordanceAction

```python
class AffordanceAction(str, Enum)
```

Actions that can be performed on a token.

---

## ObserverDensity

```python
class ObserverDensity(str, Enum)
```

Display density preference for projections.

---

## ObserverRole

```python
class ObserverRole(str, Enum)
```

Role-based access control for affordances.

---

## DocumentState

```python
class DocumentState(str, Enum)
```

States in the document polynomial state machine.

---

## TokenPattern

```python
class TokenPattern
```

Pattern for recognizing a meaning token in text.

---

## Affordance

```python
class Affordance
```

An interaction possibility offered by a token.

---

## Observer

```python
class Observer
```

Entity receiving projections with specific umwelt.

---

## TokenDefinition

```python
class TokenDefinition
```

Complete definition of a meaning token type.

---

## MeaningToken

```python
class MeaningToken(ABC, Generic[T])
```

Base class for meaning tokens—semantic primitives that project to renderings.

---

## InteractionResult

```python
class InteractionResult
```

Result of interacting with a token.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate pattern configuration.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## create

```python
def create(cls, archetype: str='guest', capabilities: frozenset[str] | None=None, density: ObserverDensity=ObserverDensity.COMFORTABLE, role: ObserverRole=ObserverRole.VIEWER, metadata: dict[str, Any] | None=None) -> Observer
```

Create a new observer with a generated ID.

---

## has_capability

```python
def has_capability(self, capability: str) -> bool
```

Check if observer has a specific capability.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate token definition.

---

## get_affordance

```python
def get_affordance(self, action: AffordanceAction) -> Affordance | None
```

Get affordance by action type.

---

## token_type

```python
def token_type(self) -> str
```

Token type name from registry.

---

## source_text

```python
def source_text(self) -> str
```

Original text that was recognized as this token.

---

## source_position

```python
def source_position(self) -> tuple[int, int]
```

(start, end) position in source document.

---

## token_id

```python
def token_id(self) -> str
```

Unique identifier for this token instance.

---

## get_affordances

```python
async def get_affordances(self, observer: Observer) -> list[Affordance]
```

Get available affordances for this observer.

---

## project

```python
async def project(self, target: str, observer: Observer) -> T
```

Project token to target-specific rendering.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## success_result

```python
def success_result(cls, data: Any, witness_id: str | None=None) -> InteractionResult
```

Create a successful interaction result.

---

## not_available

```python
def not_available(cls, action: str) -> InteractionResult
```

Create a result for unavailable action.

---

## failure

```python
def failure(cls, error: str) -> InteractionResult
```

Create a failed interaction result.

---

## services.interactive_text.events

## events

```python
module events
```

**AGENTESE:** `self.document.events`

Interactive Text Event Definitions and DataBus Integration.

### Things to Know

ℹ️ DocumentEventBus.emit() uses asyncio.create_task—fire-and-forget. Handlers run in background; emit() returns immediately.
  - *Verified in: `test_properties.py::test_event_emission_non_blocking`*

🚨 **Critical:** _safe_notify() swallows exceptions—handlers must not rely on error propagation. Errors increment _error_count but don't fail emission or other handlers.
  - *Verified in: `test_properties.py::test_handler_exception_isolation`*

ℹ️ Buffer is bounded (DEFAULT_BUFFER_SIZE=1000)—old events are dropped. replay() only sees events still in buffer; don't rely on full history.
  - *Verified in: `test_properties.py::test_buffer_eviction`*

ℹ️ get_document_event_bus() returns global singleton—reset between tests. Call reset_document_event_bus() in test fixtures to avoid state leakage.
  - *Verified in: `test_properties.py::test_global_bus_reset`*

---

## DocumentEventType

```python
class DocumentEventType(Enum)
```

Types of document events emitted by the polynomial state machine.

---

## DocumentEvent

```python
class DocumentEvent
```

An event representing a document state transition.

---

## DocumentSubscriber

```python
class DocumentSubscriber
```

A subscriber to document events.

---

## DocumentEventBus

```python
class DocumentEventBus
```

Event bus for document state transitions.

---

## EventEmittingPolynomial

```python
class EventEmittingPolynomial
```

Document Polynomial wrapper that emits events on transitions.

---

## get_document_event_bus

```python
def get_document_event_bus() -> DocumentEventBus
```

Get the global document event bus instance.

---

## reset_document_event_bus

```python
def reset_document_event_bus() -> None
```

Reset the global document event bus (for testing).

---

## create

```python
def create(cls, event_type: DocumentEventType, document_path: str | Path | None, previous_state: DocumentState, new_state: DocumentState, input_action: str, output: TransitionOutput, source: str='document_polynomial', causal_parent: str | None=None, metadata: dict[str, Any] | None=None) -> DocumentEvent
```

Factory for creating document events with sensible defaults.

---

## from_transition

```python
def from_transition(cls, document_path: str | Path | None, previous_state: DocumentState, input_action: str, new_state: DocumentState, output: TransitionOutput, causal_parent: str | None=None, metadata: dict[str, Any] | None=None) -> DocumentEvent
```

Create event from a polynomial transition.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## emit

```python
async def emit(self, event: DocumentEvent) -> None
```

Emit an event to all subscribers.

---

## emit_transition

```python
async def emit_transition(self, document_path: str | Path | None, previous_state: DocumentState, input_action: str, new_state: DocumentState, output: TransitionOutput, metadata: dict[str, Any] | None=None) -> DocumentEvent
```

Emit an event for a polynomial transition.

---

## subscribe

```python
def subscribe(self, event_type: DocumentEventType, handler: DocumentEventHandler) -> Callable[[], None]
```

Subscribe to events of a specific type.

---

## subscribe_all

```python
def subscribe_all(self, handler: DocumentEventHandler) -> Callable[[], None]
```

Subscribe to ALL event types.

---

## replay

```python
async def replay(self, handler: DocumentEventHandler, since: float | None=None, event_type: DocumentEventType | None=None) -> int
```

Replay buffered events to a handler.

---

## latest

```python
def latest(self) -> DocumentEvent | None
```

Get the most recent event.

---

## stats

```python
def stats(self) -> dict[str, int]
```

Get bus statistics.

---

## clear

```python
def clear(self) -> None
```

Clear all subscribers and buffer (for testing).

---

## __init__

```python
def __init__(self, bus: DocumentEventBus, document_path: str | Path | None=None) -> None
```

Initialize event-emitting polynomial.

---

## transition

```python
async def transition(self, state: DocumentState, input_action: str, metadata: dict[str, Any] | None=None) -> tuple[DocumentState, TransitionOutput, DocumentEvent]
```

Perform transition and emit event.

---

## services.interactive_text.node

## node

```python
module node
```

Interactive Text AGENTESE Node.

### Things to Know

ℹ️ The node depends on "interactive_text_service" in the DI container. If this dependency isn't registered in providers.py, the node will be SILENTLY SKIPPED during gateway setup. No error, just missing paths.
  - *Verified in: `test_agentese_path.py::TestAGENTESEPathTokenCreation::test_create_token`*

ℹ️ Archetype-based affordances: developer/operator/admin/editor get full access (parse + task_toggle). architect/researcher get parse only. Everyone else (guest) gets parse only. Case-insensitive matching.
  - *Verified in: `test_agentese_path.py::TestAGENTESEPathActions::test_right_click_admin_has_edit`*

ℹ️ _invoke_aspect returns DICT, not Renderable. The rendering classes (ParseRendering, TaskToggleRendering) call .to_dict() immediately. This is for JSON serialization compatibility with the API layer.
  - *Verified in: `test_agentese_path.py::TestAGENTESEPathProjection::test_project_json`*

---

## DocumentManifestRendering

```python
class DocumentManifestRendering
```

Renderable wrapper for document manifest response.

---

## ParseRendering

```python
class ParseRendering
```

Renderable wrapper for parse response.

---

## TaskToggleRendering

```python
class TaskToggleRendering
```

Renderable wrapper for task toggle response.

---

## InteractiveTextNode

```python
class InteractiveTextNode(BaseLogosNode)
```

AGENTESE node for Interactive Text service.

---

## __init__

```python
def __init__(self, interactive_text_service: InteractiveTextService) -> None
```

Initialize with injected service.

---

## handle

```python
def handle(self) -> str
```

The AGENTESE path to this node.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `self.document.manifest`

Return service status and capabilities.

---

## services.interactive_text.parser

## parser

```python
module parser
```

Markdown Parser with Roundtrip Fidelity.

### Things to Know

ℹ️ Token priority determines winner on overlap. When two patterns match overlapping text (e.g., nested backticks with AGENTESE path inside), _remove_overlapping_matches() keeps the match with HIGHER priority. Sort order is: (start_pos, -priority) so higher priority wins at same position.
  - *Verified in: `test_parser.py::TestEdgeCases::test_nested_backticks`*

🚨 **Critical:** Roundtrip fidelity is THE invariant. parse(text).render() MUST equal text exactly—byte-for-byte, including all whitespace, tabs, and newlines. If rendering changes even one character, you've broken the contract.
  - *Verified in: `test_parser.py::TestRoundtripFidelity::test_roundtrip_preserves_whitespace`*

🚨 **Critical:** Empty documents are valid. parse("") returns ParsedDocument with empty spans tuple, not None. Always check token_count, not truthiness of document.
  - *Verified in: `test_parser.py::TestRoundtripFidelity::test_roundtrip_empty_document`*

ℹ️ IncrementalParser expands affected region to line boundaries. When applying edits, _find_affected_region() extends start backward to previous newline and end forward to next newline. This prevents partial token corruption but means even small edits may re-parse entire lines.
  - *Verified in: `test_parser.py::TestIncrementalParser::test_edit_preserves_tokens_before`*

---

## SourcePosition

```python
class SourcePosition
```

Position in source document.

---

## TextSpan

```python
class TextSpan
```

A span of text in the document.

---

## ParsedDocument

```python
class ParsedDocument
```

A parsed document with extracted tokens.

---

## SourceMap

```python
class SourceMap
```

Maps tokens to their source positions.

---

## MarkdownParser

```python
class MarkdownParser
```

Parser for markdown documents with token extraction.

---

## DocumentEdit

```python
class DocumentEdit
```

Represents an edit to a document.

---

## IncrementalParser

```python
class IncrementalParser
```

Parser supporting incremental updates.

---

## parse_markdown

```python
def parse_markdown(text: str, path: Path | None=None) -> ParsedDocument
```

Parse markdown text into a ParsedDocument.

---

## render_markdown

```python
def render_markdown(document: ParsedDocument) -> str
```

Render a ParsedDocument back to text.

---

## length

```python
def length(self) -> int
```

Length of the span in bytes.

---

## token_type

```python
def token_type(self) -> str | None
```

Token type name if this is a token.

---

## tokens

```python
def tokens(self) -> list[TextSpan]
```

Get all token spans.

---

## token_count

```python
def token_count(self) -> int
```

Number of tokens in the document.

---

## get_token_at

```python
def get_token_at(self, offset: int) -> TextSpan | None
```

Get token at a specific byte offset.

---

## get_tokens_in_range

```python
def get_tokens_in_range(self, start: int, end: int) -> list[TextSpan]
```

Get all tokens overlapping a byte range.

---

## render

```python
def render(self) -> str
```

Render document back to text.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Build the token index.

---

## get_token_at_position

```python
def get_token_at_position(self, line: int, column: int) -> TextSpan | None
```

Get token at a line/column position.

---

## __init__

```python
def __init__(self) -> None
```

Initialize the parser.

---

## parse

```python
def parse(self, text: str, path: Path | None=None) -> ParsedDocument
```

Parse markdown text into a ParsedDocument.

---

## parse_file

```python
def parse_file(self, path: Path) -> ParsedDocument
```

Parse a markdown file.

---

## old_length

```python
def old_length(self) -> int
```

Length of text being replaced.

---

## new_length

```python
def new_length(self) -> int
```

Length of new text.

---

## delta

```python
def delta(self) -> int
```

Change in document length.

---

## __init__

```python
def __init__(self) -> None
```

Initialize the incremental parser.

---

## parse

```python
def parse(self, text: str, path: Path | None=None) -> ParsedDocument
```

Parse a document from scratch.

---

## apply_edit

```python
def apply_edit(self, document: ParsedDocument, edit: DocumentEdit) -> ParsedDocument
```

Apply an edit to a document incrementally.

---

## services.interactive_text.polynomial

## polynomial

```python
module polynomial
```

Document Polynomial State Machine.

### Things to Know

ℹ️ Invalid inputs return (same_state, NoOp), NOT an exception. The polynomial is total—every (state, input) pair produces a valid output. Check the output type to detect invalid transitions: isinstance(output, NoOp).
  - *Verified in: `test_properties.py::TestProperty6DocumentPolynomialStateValidity::test_invalid_inputs_produce_noop`*

ℹ️ The polynomial is STATELESS—it defines the transition function, not current state. DocumentSheaf or your own state holder tracks actual document state. DocumentPolynomial.transition(state, input) is a pure function.
  - *Verified in: `test_properties.py::TestProperty6DocumentPolynomialStateValidity::test_transitions_are_deterministic`*

ℹ️ Each state has a FIXED set of valid directions. VIEWING accepts {edit, refresh, hover, click, drag}. EDITING accepts {save, cancel, continue_edit, hover}. SYNCING accepts {wait, force_local, force_remote}. CONFLICTING accepts {resolve, abort, view_diff}. Sending wrong input to wrong state → NoOp.
  - *Verified in: `test_properties.py::TestProperty6DocumentPolynomialStateValidity::test_viewing_state_accepts_correct_inputs`*

ℹ️ TransitionOutput subclasses are FROZEN dataclasses. Once created, they're immutable. This enables safe composition and prevents state corruption when outputs are passed between components.
  - *Verified in: `test_properties.py::TestProperty6DocumentPolynomialStateValidity::test_transition_outputs_are_serializable`*

---

## TransitionOutput

```python
class TransitionOutput(ABC)
```

Base class for all transition outputs.

---

## NoOp

```python
class NoOp(TransitionOutput)
```

No operation - invalid transition attempted.

---

## EditSession

```python
class EditSession(TransitionOutput)
```

Output when entering edit mode.

---

## RefreshResult

```python
class RefreshResult(TransitionOutput)
```

Output when refreshing document.

---

## HoverInfo

```python
class HoverInfo(TransitionOutput)
```

Output when hovering over element.

---

## ClickResult

```python
class ClickResult(TransitionOutput)
```

Output when clicking element.

---

## DragResult

```python
class DragResult(TransitionOutput)
```

Output when dragging element.

---

## SaveRequest

```python
class SaveRequest(TransitionOutput)
```

Output when requesting save.

---

## CancelResult

```python
class CancelResult(TransitionOutput)
```

Output when canceling edit.

---

## EditContinue

```python
class EditContinue(TransitionOutput)
```

Output when continuing edit.

---

## SyncComplete

```python
class SyncComplete(TransitionOutput)
```

Output when sync completes successfully.

---

## LocalWins

```python
class LocalWins(TransitionOutput)
```

Output when forcing local version.

---

## RemoteWins

```python
class RemoteWins(TransitionOutput)
```

Output when accepting remote version.

---

## ConflictDetected

```python
class ConflictDetected(TransitionOutput)
```

Output when conflict is detected during sync.

---

## Resolved

```python
class Resolved(TransitionOutput)
```

Output when conflict is resolved.

---

## Aborted

```python
class Aborted(TransitionOutput)
```

Output when conflict resolution is aborted.

---

## DiffView

```python
class DiffView(TransitionOutput)
```

Output when viewing diff in conflict state.

---

## DocumentPolynomial

```python
class DocumentPolynomial
```

Document as polynomial functor: editing states with mode-dependent inputs.

---

## output_type

```python
def output_type(self) -> str
```

Type identifier for this output.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## directions

```python
def directions(cls, state: DocumentState) -> frozenset[str]
```

Get valid inputs for a given state.

---

## transition

```python
def transition(cls, state: DocumentState, input_action: str) -> tuple[DocumentState, TransitionOutput]
```

Compute state transition for given state and input.

---

## is_valid_input

```python
def is_valid_input(cls, state: DocumentState, input_action: str) -> bool
```

Check if an input is valid for a given state.

---

## get_all_transitions

```python
def get_all_transitions(cls) -> dict[tuple[DocumentState, str], tuple[DocumentState, type[TransitionOutput]]]
```

Get the complete transition table.

---

## verify_determinism

```python
def verify_determinism(cls) -> bool
```

Verify that the polynomial is deterministic.

---

## verify_completeness

```python
def verify_completeness(cls) -> bool
```

Verify that all states have defined directions.

---

## verify_laws

```python
def verify_laws(cls) -> bool
```

Verify polynomial laws hold.

---

## services.interactive_text.projectors.__init__

## __init__

```python
module __init__
```

Projection functor implementations.

---

## services.interactive_text.projectors.base

## base

```python
module base
```

**AGENTESE:** `self.document.project`

Projection Functor Base Class.

### Things to Know

🚨 **Critical:** ProjectionFunctor must satisfy functor laws: P(id) = id, P(f∘g) = P(f)∘P(g). project_composition() relies on _compose() to preserve associativity.
  - *Verified in: `test_projectors.py::test_composition_law`*

ℹ️ DensityParams.for_density() is the canonical way to get parameters. Don't hardcode padding/font_size—use DENSITY_PARAMS lookup.
  - *Verified in: `test_projectors.py::test_density_params_lookup`*

ℹ️ _compose() is abstract and target-specific: CLI joins with newlines, JSON wraps in arrays, Web nests components. Override per target.
  - *Verified in: `test_projectors.py::test_cli_compose_newlines`*

---

## DensityParams

```python
class DensityParams
```

Parameters for density-based projection.

---

## ProjectionResult

```python
class ProjectionResult(Generic[Target])
```

Result of a projection operation.

---

## CompositionResult

```python
class CompositionResult(Generic[Target])
```

Result of composing multiple projections.

---

## ProjectionFunctor

```python
class ProjectionFunctor(ABC, Generic[Target])
```

Abstract base class for projection functors.

---

## for_density

```python
def for_density(cls, density: ObserverDensity) -> DensityParams
```

Get density parameters for a given density level.

---

## target_name

```python
def target_name(self) -> str
```

Name of the projection target (e.g., 'cli', 'web', 'json').

---

## project_token

```python
async def project_token(self, token: 'MeaningToken[Any]', observer: Observer) -> Target
```

Project a single token to target-specific rendering.

---

## project_document

```python
async def project_document(self, document: 'Document', observer: Observer) -> Target
```

Project an entire document to target-specific rendering.

---

## project_composition

```python
async def project_composition(self, tokens: list['MeaningToken[Any]'], composition_type: str, observer: Observer) -> CompositionResult[Target]
```

Project composed tokens.

---

## get_density_params

```python
def get_density_params(self, observer: Observer) -> DensityParams
```

Get density parameters for an observer.

---

## project_with_result

```python
async def project_with_result(self, token: 'MeaningToken[Any]', observer: Observer) -> ProjectionResult[Target]
```

Project a token and return full result with metadata.

---

## Document

```python
class Document
```

Placeholder for Document type.

---

## services.interactive_text.projectors.cli

## cli

```python
module cli
```

CLI Projection Functor.

---

## RichMarkup

```python
class RichMarkup
```

Rich terminal markup representation.

---

## CLIProjectable

```python
class CLIProjectable(Protocol)
```

Protocol for tokens that can be projected to CLI.

---

## CLIProjectionFunctor

```python
class CLIProjectionFunctor(ProjectionFunctor[str])
```

Project meaning tokens to Rich terminal markup.

---

## to_markup

```python
def to_markup(self) -> str
```

Convert to Rich markup string.

---

## token_type

```python
def token_type(self) -> str
```

Token type name.

---

## source_text

```python
def source_text(self) -> str
```

Original source text.

---

## token_id

```python
def token_id(self) -> str
```

Unique token identifier.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## project_token

```python
async def project_token(self, token: CLIProjectable, observer: Observer) -> str
```

Project token to Rich markup string.

---

## project_document

```python
async def project_document(self, document: Any, observer: Observer) -> str
```

Project document to Rich markup string.

---

## services.interactive_text.projectors.json

## json

```python
module json
```

JSON Projection Functor.

---

## JSONToken

```python
class JSONToken
```

JSON representation of a meaning token.

---

## JSONDocument

```python
class JSONDocument
```

JSON representation of a document.

---

## JSONProjectable

```python
class JSONProjectable(Protocol)
```

Protocol for tokens that can be projected to JSON.

---

## JSONProjectionFunctor

```python
class JSONProjectionFunctor(ProjectionFunctor[dict[str, Any]])
```

Project meaning tokens to API-friendly JSON structures.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for JSON serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for JSON serialization.

---

## token_type

```python
def token_type(self) -> str
```

Token type name.

---

## source_text

```python
def source_text(self) -> str
```

Original source text.

---

## source_position

```python
def source_position(self) -> tuple[int, int]
```

Source position (start, end).

---

## token_id

```python
def token_id(self) -> str
```

Unique token identifier.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## get_affordances

```python
async def get_affordances(self, observer: Observer) -> list[Affordance]
```

Get available affordances for observer.

---

## project_token

```python
async def project_token(self, token: JSONProjectable, observer: Observer) -> dict[str, Any]
```

Project token to JSON dictionary.

---

## project_document

```python
async def project_document(self, document: Any, observer: Observer) -> dict[str, Any]
```

Project document to JSON dictionary.

---

## services.interactive_text.projectors.web

## web

```python
module web
```

Web Projection Functor.

---

## ReactElement

```python
class ReactElement
```

Specification for a React element.

---

## WebProjectable

```python
class WebProjectable(Protocol)
```

Protocol for tokens that can be projected to web.

---

## WebProjectionFunctor

```python
class WebProjectionFunctor(ProjectionFunctor[ReactElement])
```

Project meaning tokens to React element specifications.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for JSON serialization.

---

## with_props

```python
def with_props(self, **new_props: Any) -> ReactElement
```

Create a new element with additional props.

---

## with_children

```python
def with_children(self, *children: 'ReactElement | str') -> ReactElement
```

Create a new element with children.

---

## token_type

```python
def token_type(self) -> str
```

Token type name.

---

## source_text

```python
def source_text(self) -> str
```

Original source text.

---

## token_id

```python
def token_id(self) -> str
```

Unique token identifier.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## get_affordances

```python
async def get_affordances(self, observer: Observer) -> list[Affordance]
```

Get available affordances for observer.

---

## project_token

```python
async def project_token(self, token: WebProjectable, observer: Observer) -> ReactElement
```

Project token to React element specification.

---

## project_document

```python
async def project_document(self, document: Any, observer: Observer) -> ReactElement
```

Project document to React element specification.

---

## services.interactive_text.registry

## registry

```python
module registry
```

**AGENTESE:** `concept.document.token`

Token Registry: Single Source of Truth for Token Definitions.

### Things to Know

ℹ️ TokenRegistry uses ClassVar—singleton pattern with class-level state. All instances share _tokens dict. Use clear() between tests.
  - *Verified in: `test_registry.py::test_register_duplicate_raises`*

ℹ️ _ensure_initialized() is lazy—core tokens not registered until first get(). Call get_all() or recognize() to trigger initialization.
  - *Verified in: `test_registry.py::test_core_tokens_lazy_init`*

ℹ️ recognize() returns sorted by (position, -priority)—priority breaks ties. Higher priority wins when patterns overlap at same position.
  - *Verified in: `test_registry.py::test_priority_ordering`*

ℹ️ register() raises ValueError on duplicate; use register_or_replace() for updates. This prevents accidental token definition clobbering.
  - *Verified in: `test_registry.py::test_register_or_replace`*

---

## TokenMatch

```python
class TokenMatch
```

A token match found in text.

---

## TokenRegistry

```python
class TokenRegistry
```

Single source of truth for token definitions (AD-011).

---

## text

```python
def text(self) -> str
```

The matched text.

---

## groups

```python
def groups(self) -> tuple[str | None, ...]
```

Captured groups from the match.

---

## register

```python
def register(cls, definition: TokenDefinition) -> None
```

Register a token type.

---

## register_or_replace

```python
def register_or_replace(cls, definition: TokenDefinition) -> None
```

Register a token type, replacing if it exists.

---

## unregister

```python
def unregister(cls, name: str) -> bool
```

Unregister a token type.

---

## get

```python
def get(cls, name: str) -> TokenDefinition | None
```

Get token definition by name.

---

## get_all

```python
def get_all(cls) -> dict[str, TokenDefinition]
```

Get all registered token definitions.

---

## recognize

```python
def recognize(cls, text: str) -> list[TokenMatch]
```

Find all tokens in text, ordered by position then priority.

---

## clear

```python
def clear(cls) -> None
```

Clear all registered tokens. Useful for testing.

---

## services.interactive_text.service

## service

```python
module service
```

Interactive Text Service: Crown Jewel Business Logic.

### Things to Know

ℹ️ Toggle requires EITHER file_path OR text, not both. When using file mode, you need file_path + (task_id OR line_number). Text mode needs text + line_number. Mixing modes or missing required params returns error response with success=False.
  - *Verified in: `test_properties.py::TestProperty6DocumentPolynomialStateValidity`*

🚨 **Critical:** Line numbers are 1-indexed for human ergonomics. The toggle_task_at_line() method converts to 0-indexed internally. Off-by-one errors are common when directly manipulating the lines list—always use (line_number - 1).
  - *Verified in: `test_parser.py::TestTokenRecognition::test_task_checkbox_checked`*

🚨 **Critical:** TraceWitness is ALWAYS captured on successful toggle, even in text mode where no file is modified. The trace captures previous_state → new_state for audit. If you need to skip trace capture, you must use the internal _toggle_task_at_line() method directly (not recommended for production use).
  - *Verified in: `test_tokens_base.py::TestTraceWitness::test_create_witness`*

---

## ParseRequest

```python
class ParseRequest
```

Request to parse markdown text.

---

## ParseResponse

```python
class ParseResponse
```

Response from parse operation.

---

## TaskToggleRequest

```python
class TaskToggleRequest
```

Request to toggle a task checkbox.

---

## TaskToggleResponse

```python
class TaskToggleResponse
```

Response from task toggle operation.

---

## DocumentManifestResponse

```python
class DocumentManifestResponse
```

Response for manifest (status) operation.

---

## InteractiveTextService

```python
class InteractiveTextService
```

Interactive Text Crown Jewel Service.

---

## get_interactive_text_service

```python
def get_interactive_text_service() -> InteractiveTextService
```

Factory function for InteractiveTextService.

---

## __init__

```python
def __init__(self) -> None
```

Initialize the service.

---

## manifest

```python
async def manifest(self) -> DocumentManifestResponse
```

Get service status and capabilities.

---

## parse_document

```python
async def parse_document(self, text: str, layout_mode: str='COMFORTABLE') -> ParseResponse
```

Parse markdown text to SceneGraph for frontend rendering.

### Examples
```python
>>> service = InteractiveTextService()
```
```python
>>> response = await service.parse_document("Check `self.brain`")
```
```python
>>> response.token_count
```

---

## toggle_task

```python
async def toggle_task(self, request: TaskToggleRequest, observer: Observer | None=None) -> TaskToggleResponse
```

Toggle a task checkbox and capture TraceWitness.

### Examples
```python
>>> service = InteractiveTextService()
```
```python
>>> request = TaskToggleRequest(
```
```python
>>> response = await service.toggle_task(request)
```
```python
>>> response.success
```

---

## services.interactive_text.sheaf

## sheaf

```python
module sheaf
```

Document Sheaf: Multi-View Coherence Structure.

### Things to Know

🚨 **Critical:** glue() RAISES SheafConditionError if views are incompatible. Always call verify_sheaf_condition() first if you want to handle conflicts gracefully. Don't assume glue() will merge conflicts—it refuses to produce invalid state.
  - *Verified in: `test_properties.py::TestProperty8DocumentSheafCoherence::test_incompatible_views_cannot_be_glued`*

ℹ️ TokenState equality compares (token_id, token_type, content, position) but IGNORES metadata. Two tokens with different metadata but same core fields are considered equal. This is intentional—metadata is view-local decoration.
  - *Verified in: `test_properties.py::TestProperty8DocumentSheafCoherence::test_token_state_equality`*

ℹ️ compatible() is SYMMETRIC: compatible(v1, v2) == compatible(v2, v1). Same for overlap(). But verify_sheaf_condition() checks ALL pairs, not just the ones you pass in. Adding a third view requires checking 3 pairs.
  - *Verified in: `test_properties.py::TestProperty8DocumentSheafCoherence::test_compatible_is_symmetric`*

🚨 **Critical:** A single view is ALWAYS coherent with itself. verify_sheaf_condition() on a sheaf with one view returns success with checked_pairs=0. The sheaf condition is about agreement between views, not internal consistency.
  - *Verified in: `test_properties.py::TestProperty8DocumentSheafCoherence::test_single_view_always_coherent`*

ℹ️ Views for DIFFERENT documents cannot be added to the same sheaf. add_view() raises ValueError if view.document_path != sheaf.document_path. Create separate sheafs per document.
  - *Verified in: `sheaf.py::DocumentSheaf::add_view validation`*

---

## TokenState

```python
class TokenState
```

State of a token in a view.

---

## DocumentView

```python
class DocumentView(Protocol)
```

Protocol for document views.

---

## TokenChange

```python
class TokenChange
```

A change to a token.

---

## FileChange

```python
class FileChange
```

A change to the underlying file.

---

## Edit

```python
class Edit
```

An edit operation on a document.

---

## SheafConflict

```python
class SheafConflict
```

A conflict between two views.

---

## SheafVerification

```python
class SheafVerification
```

Result of verifying the sheaf condition.

---

## SimpleDocumentView

```python
class SimpleDocumentView
```

Simple implementation of DocumentView for testing and basic use.

---

## DocumentSheaf

```python
class DocumentSheaf
```

Sheaf structure ensuring multi-view coherence.

---

## SheafConditionError

```python
class SheafConditionError(Exception)
```

Raised when the sheaf condition is violated.

---

## __eq__

```python
def __eq__(self, other: object) -> bool
```

Two token states are equal if their observable state matches.

---

## view_id

```python
def view_id(self) -> str
```

Unique identifier for this view.

---

## document_path

```python
def document_path(self) -> Path
```

Path to the document this view observes.

---

## tokens

```python
def tokens(self) -> frozenset[str]
```

Token IDs visible in this view.

---

## state_of

```python
def state_of(self, token_id: str) -> TokenState | None
```

Get state of a token in this view.

---

## update

```python
async def update(self, changes: list[TokenChange]) -> None
```

Apply changes to this view.

---

## created

```python
def created(cls, state: TokenState) -> TokenChange
```

Create a creation change.

---

## modified

```python
def modified(cls, old: TokenState, new: TokenState) -> TokenChange
```

Create a modification change.

---

## deleted

```python
def deleted(cls, state: TokenState) -> TokenChange
```

Create a deletion change.

---

## apply

```python
def apply(self, content: str) -> str
```

Apply this edit to content.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## success

```python
def success(cls, checked_pairs: int=0) -> SheafVerification
```

Create a successful verification result.

---

## failure

```python
def failure(cls, conflicts: list[SheafConflict], checked_pairs: int=0) -> SheafVerification
```

Create a failed verification result.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## update

```python
async def update(self, changes: list[TokenChange]) -> None
```

Apply changes to this view.

---

## add_token

```python
def add_token(self, state: TokenState) -> None
```

Add a token to this view.

---

## remove_token

```python
def remove_token(self, token_id: str) -> None
```

Remove a token from this view.

---

## create

```python
def create(cls, document_path: Path | str, tokens: list[TokenState] | None=None) -> SimpleDocumentView
```

Create a new view with optional initial tokens.

---

## overlap

```python
def overlap(self, v1: DocumentView, v2: DocumentView) -> frozenset[str]
```

Get tokens visible in both views.

---

## compatible

```python
def compatible(self, v1: DocumentView, v2: DocumentView) -> bool
```

Check if two views agree on overlapping tokens (sheaf condition).

---

## verify_sheaf_condition

```python
def verify_sheaf_condition(self) -> SheafVerification
```

Verify all views are pairwise compatible.

---

## add_view

```python
def add_view(self, view: DocumentView) -> None
```

Add a view to the sheaf.

---

## remove_view

```python
def remove_view(self, view_id: str) -> bool
```

Remove a view from the sheaf.

---

## get_view

```python
def get_view(self, view_id: str) -> DocumentView | None
```

Get a view by ID.

---

## glue

```python
def glue(self) -> dict[str, TokenState]
```

Combine compatible views into global document state.

---

## on_file_change

```python
async def on_file_change(self, change: FileChange) -> None
```

Handle file change—broadcast to all views.

---

## on_view_edit

```python
async def on_view_edit(self, view: DocumentView, edit: Edit) -> None
```

Handle edit from a view—apply to file, broadcast to all.

---

## on_change

```python
def on_change(self, handler: Callable[[list[TokenChange]], Any]) -> Callable[[], None]
```

Register a change handler.

---

## create

```python
def create(cls, document_path: Path | str) -> DocumentSheaf
```

Create a new sheaf for a document.

---

## services.interactive_text.tokens.__init__

## __init__

```python
module __init__
```

Token type implementations.

---

## services.interactive_text.tokens.agentese_path

## agentese_path

```python
module agentese_path
```

**AGENTESE:** `self.document.token.agentese`

AGENTESEPath Token Implementation.

### Things to Know

ℹ️ Ghost tokens (non-existent paths) still render but with reduced affordances. is_ghost=True disables invoke/navigate; shows "not yet implemented".
  - *Verified in: `test_agentese_path.py::test_ghost_token_affordances`*

ℹ️ Path validation uses regex matching context (world|self|concept|void|time). Invalid context prefix won't match—token won't be recognized.
  - *Verified in: `test_agentese_path.py::test_path_validation`*

ℹ️ _check_path_exists() is async and may hit registry—cache results. Repeated hover events should not repeatedly query path existence.
  - *Verified in: `test_agentese_path.py::test_path_check_caching`*

---

## PolynomialState

```python
class PolynomialState
```

State information for an AGENTESE node.

---

## HoverInfo

```python
class HoverInfo
```

Information displayed on token hover.

---

## NavigationResult

```python
class NavigationResult
```

Result of navigating to an AGENTESE path.

---

## ContextMenuResult

```python
class ContextMenuResult
```

Result of showing context menu for an AGENTESE path.

---

## DragResult

```python
class DragResult
```

Result of dragging an AGENTESE path to REPL.

---

## AGENTESEPathToken

```python
class AGENTESEPathToken(BaseMeaningToken[str])
```

Token representing an AGENTESE path in text.

---

## create_agentese_path_token

```python
def create_agentese_path_token(text: str, position: tuple[int, int] | None=None, check_exists: bool=False) -> AGENTESEPathToken | None
```

Create an AGENTESEPath token from text.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## ghost

```python
def ghost(cls, path: str) -> HoverInfo
```

Create hover info for a ghost token.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## __init__

```python
def __init__(self, source_text: str, source_position: tuple[int, int], path: str, exists: bool=True) -> None
```

Initialize an AGENTESEPath token.

---

## from_match

```python
def from_match(cls, match: re.Match[str], exists: bool=True) -> AGENTESEPathToken
```

Create token from regex match.

---

## token_type

```python
def token_type(self) -> str
```

Token type name from registry.

---

## source_text

```python
def source_text(self) -> str
```

Original text that was recognized as this token.

---

## source_position

```python
def source_position(self) -> tuple[int, int]
```

(start, end) position in source document.

---

## path

```python
def path(self) -> str
```

The AGENTESE path (without backticks).

---

## context

```python
def context(self) -> str
```

The context (world, self, concept, void, time).

---

## segments

```python
def segments(self) -> list[str]
```

Path segments after the context.

---

## exists

```python
def exists(self) -> bool
```

Whether this path exists in the registry.

---

## is_ghost

```python
def is_ghost(self) -> bool
```

Whether this is a ghost token (non-existent path).

---

## get_affordances

```python
async def get_affordances(self, observer: Observer) -> list[Affordance]
```

Get available affordances for this observer.

---

## project

```python
async def project(self, target: str, observer: Observer) -> str | dict[str, Any]
```

Project token to target-specific rendering.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## services.interactive_text.tokens.base

## base

```python
module base
```

**AGENTESE:** `self.document.token`

MeaningToken Base Class Implementation.

### Things to Know

ℹ️ on_interact() validates affordances BEFORE calling _execute_action. Order matters: check enabled + action match, THEN execute.
  - *Verified in: `test_tokens_base.py::test_on_interact_validates_affordance`*

ℹ️ capture_trace defaults to True—every interaction creates a TraceWitness. Set capture_trace=False for high-frequency operations (hover spam).
  - *Verified in: `test_tokens_base.py::test_capture_trace_default`*

ℹ️ token_id uses source_position (start:end), NOT content hash. Renumbering or editing document invalidates existing token IDs.
  - *Verified in: `test_tokens_base.py::test_token_id_format`*

ℹ️ filter_affordances_by_observer returns DISABLED affordances, not empty. UI can show "locked" affordances with capability requirements.
  - *Verified in: `test_tokens_base.py::test_filter_affordances_disabled`*

---

## ExecutionTrace

```python
class ExecutionTrace
```

Trace of a token interaction for formal verification.

---

## TraceWitness

```python
class TraceWitness
```

A constructive proof of interaction captured for formal verification.

---

## BaseMeaningToken

```python
class BaseMeaningToken(ABC, Generic[T])
```

Base implementation for meaning tokens with interaction handling.

---

## filter_affordances_by_observer

```python
def filter_affordances_by_observer(affordances: tuple[Affordance, ...], observer: Observer, required_capabilities: dict[str, frozenset[str]] | None=None) -> list[Affordance]
```

Filter affordances based on observer capabilities and role.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## token_type

```python
def token_type(self) -> str
```

Token type name from registry.

---

## source_text

```python
def source_text(self) -> str
```

Original text that was recognized as this token.

---

## source_position

```python
def source_position(self) -> tuple[int, int]
```

(start, end) position in source document.

---

## token_id

```python
def token_id(self) -> str
```

Unique identifier for this token instance.

---

## get_definition

```python
def get_definition(self) -> TokenDefinition | None
```

Get the token definition from the registry.

---

## get_affordances

```python
async def get_affordances(self, observer: Observer) -> list[Affordance]
```

Get available affordances for this observer.

---

## project

```python
async def project(self, target: str, observer: Observer) -> str | dict[str, Any]
```

Project token to target-specific rendering.

---

## on_interact

```python
async def on_interact(self, action: AffordanceAction, observer: Observer, capture_trace: bool=True, **kwargs: Any) -> InteractionResult
```

Handle interaction with this token.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## services.interactive_text.tokens.code_block

## code_block

```python
module code_block
```

CodeBlock Token Implementation.

---

## ExecutionResult

```python
class ExecutionResult
```

Result of executing a code block.

---

## CodeBlockHoverInfo

```python
class CodeBlockHoverInfo
```

Information displayed on code block hover.

---

## CodeBlockContextMenuResult

```python
class CodeBlockContextMenuResult
```

Result of showing context menu for a code block.

---

## EditFocusResult

```python
class EditFocusResult
```

Result of focusing a code block for editing.

---

## CodeBlockToken

```python
class CodeBlockToken(BaseMeaningToken[str])
```

Token representing a fenced code block.

---

## create_code_block_token

```python
def create_code_block_token(text: str, position: tuple[int, int] | None=None) -> CodeBlockToken | None
```

Create a CodeBlock token from text.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## __init__

```python
def __init__(self, source_text: str, source_position: tuple[int, int], language: str, code: str) -> None
```

Initialize a CodeBlock token.

---

## from_match

```python
def from_match(cls, match: re.Match[str]) -> CodeBlockToken
```

Create token from regex match.

---

## token_type

```python
def token_type(self) -> str
```

Token type name from registry.

---

## source_text

```python
def source_text(self) -> str
```

Original text that was recognized as this token.

---

## source_position

```python
def source_position(self) -> tuple[int, int]
```

(start, end) position in source document.

---

## language

```python
def language(self) -> str
```

Programming language.

---

## code

```python
def code(self) -> str
```

Code content.

---

## line_count

```python
def line_count(self) -> int
```

Number of lines in the code.

---

## can_execute

```python
def can_execute(self) -> bool
```

Whether this code block can be executed.

---

## get_affordances

```python
async def get_affordances(self, observer: Observer) -> list[Affordance]
```

Get available affordances for this observer.

---

## project

```python
async def project(self, target: str, observer: Observer) -> str | dict[str, Any]
```

Project token to target-specific rendering.

---

## execute

```python
async def execute(self, observer: Observer, sandboxed: bool=True) -> ExecutionResult
```

Execute the code block.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## services.interactive_text.tokens.image

## image

```python
module image
```

Image Token Implementation.

---

## ImageAnalysis

```python
class ImageAnalysis
```

AI-generated analysis of an image.

---

## ImageHoverInfo

```python
class ImageHoverInfo
```

Information displayed on image hover.

---

## ImageExpandResult

```python
class ImageExpandResult
```

Result of expanding an image to full analysis panel.

---

## ImageDragResult

```python
class ImageDragResult
```

Result of dragging an image to chat context.

---

## ImageToken

```python
class ImageToken(BaseMeaningToken[str])
```

Token representing a markdown image.

---

## create_image_token

```python
def create_image_token(text: str, position: tuple[int, int] | None=None, llm_available: bool=True) -> ImageToken | None
```

Create an Image token from text.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## __init__

```python
def __init__(self, source_text: str, source_position: tuple[int, int], alt_text: str, path: str, llm_available: bool=True) -> None
```

Initialize an Image token.

---

## from_match

```python
def from_match(cls, match: re.Match[str], llm_available: bool=True) -> ImageToken
```

Create token from regex match.

---

## token_type

```python
def token_type(self) -> str
```

Token type name from registry.

---

## source_text

```python
def source_text(self) -> str
```

Original text that was recognized as this token.

---

## source_position

```python
def source_position(self) -> tuple[int, int]
```

(start, end) position in source document.

---

## alt_text

```python
def alt_text(self) -> str
```

Image alt text.

---

## path

```python
def path(self) -> str
```

Image path/URL.

---

## llm_available

```python
def llm_available(self) -> bool
```

Whether LLM service is available.

---

## get_affordances

```python
async def get_affordances(self, observer: Observer) -> list[Affordance]
```

Get available affordances for this observer.

---

## project

```python
async def project(self, target: str, observer: Observer) -> str | dict[str, Any]
```

Project token to target-specific rendering.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## services.interactive_text.tokens.principle_ref

## principle_ref

```python
module principle_ref
```

PrincipleRef Token Implementation.

---

## PrincipleInfo

```python
class PrincipleInfo
```

Information about a design principle.

---

## PrincipleHoverInfo

```python
class PrincipleHoverInfo
```

Information displayed on principle hover.

---

## PrincipleNavigationResult

```python
class PrincipleNavigationResult
```

Result of navigating to a principle.

---

## PrincipleContextMenuResult

```python
class PrincipleContextMenuResult
```

Result of showing context menu for a principle.

---

## PrincipleRefToken

```python
class PrincipleRefToken(BaseMeaningToken[str])
```

Token representing a principle reference.

---

## create_principle_ref_token

```python
def create_principle_ref_token(text: str, position: tuple[int, int] | None=None) -> PrincipleRefToken | None
```

Create a PrincipleRef token from text.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## __init__

```python
def __init__(self, source_text: str, source_position: tuple[int, int], number: int) -> None
```

Initialize a PrincipleRef token.

---

## from_match

```python
def from_match(cls, match: re.Match[str]) -> PrincipleRefToken
```

Create token from regex match.

---

## get_affordances

```python
async def get_affordances(self, observer: Observer) -> list[Affordance]
```

Get available affordances for this observer.

---

## services.interactive_text.tokens.requirement_ref

## requirement_ref

```python
module requirement_ref
```

RequirementRef Token Implementation.

---

## RequirementInfo

```python
class RequirementInfo
```

Information about a requirement.

---

## RequirementHoverInfo

```python
class RequirementHoverInfo
```

Information displayed on requirement hover.

---

## RequirementNavigationResult

```python
class RequirementNavigationResult
```

Result of navigating to a requirement.

---

## RequirementContextMenuResult

```python
class RequirementContextMenuResult
```

Result of showing context menu for a requirement.

---

## RequirementRefToken

```python
class RequirementRefToken(BaseMeaningToken[str])
```

Token representing a requirement reference.

---

## create_requirement_ref_token

```python
def create_requirement_ref_token(text: str, position: tuple[int, int] | None=None) -> RequirementRefToken | None
```

Create a RequirementRef token from text.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## __init__

```python
def __init__(self, source_text: str, source_position: tuple[int, int], major: int, minor: int | None=None) -> None
```

Initialize a RequirementRef token.

---

## from_match

```python
def from_match(cls, match: re.Match[str]) -> RequirementRefToken
```

Create token from regex match.

---

## get_affordances

```python
async def get_affordances(self, observer: Observer) -> list[Affordance]
```

Get available affordances for this observer.

---

## services.interactive_text.tokens.task_checkbox

## task_checkbox

```python
module task_checkbox
```

TaskCheckbox Token Implementation.

---

## VerificationStatus

```python
class VerificationStatus
```

Verification status for a task.

---

## TaskHoverInfo

```python
class TaskHoverInfo
```

Information displayed on task hover.

---

## ToggleResult

```python
class ToggleResult
```

Result of toggling a task checkbox.

---

## TaskContextMenuResult

```python
class TaskContextMenuResult
```

Result of showing context menu for a task.

---

## TaskCheckboxToken

```python
class TaskCheckboxToken(BaseMeaningToken[bool])
```

Token representing a GitHub-style task checkbox.

---

## create_task_checkbox_token

```python
def create_task_checkbox_token(text: str, position: tuple[int, int] | None=None, file_path: str | None=None, line_number: int | None=None) -> TaskCheckboxToken | None
```

Create a TaskCheckbox token from text.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## __init__

```python
def __init__(self, source_text: str, source_position: tuple[int, int], checked: bool, description: str, file_path: str | None=None, line_number: int | None=None, requirement_refs: tuple[str, ...]=()) -> None
```

Initialize a TaskCheckbox token.

---

## from_match

```python
def from_match(cls, match: re.Match[str], file_path: str | None=None, line_number: int | None=None) -> TaskCheckboxToken
```

Create token from regex match.

---

## token_type

```python
def token_type(self) -> str
```

Token type name from registry.

---

## source_text

```python
def source_text(self) -> str
```

Original text that was recognized as this token.

---

## source_position

```python
def source_position(self) -> tuple[int, int]
```

(start, end) position in source document.

---

## checked

```python
def checked(self) -> bool
```

Whether the checkbox is checked.

---

## description

```python
def description(self) -> str
```

Task description text.

---

## file_path

```python
def file_path(self) -> str | None
```

Path to source file.

---

## line_number

```python
def line_number(self) -> int | None
```

Line number in source file.

---

## requirement_refs

```python
def requirement_refs(self) -> tuple[str, ...]
```

Linked requirement references.

---

## verification

```python
def verification(self) -> VerificationStatus | None
```

Verification status for this task.

---

## get_affordances

```python
async def get_affordances(self, observer: Observer) -> list[Affordance]
```

Get available affordances for this observer.

---

## project

```python
async def project(self, target: str, observer: Observer) -> str | dict[str, Any]
```

Project token to target-specific rendering.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## services.liminal.__init__

## __init__

```python
module __init__
```

Liminal Transition Protocols: Rituals that honor state changes.

---

## services.liminal.coffee.__init__

## __init__

```python
module __init__
```

Morning Coffee: Liminal Transition Protocol from Rest to Work.

---

## services.liminal.coffee.capture

## capture

```python
module capture
```

Voice Capture: What's on your mind before code takes over?

---

## CaptureQuestion

```python
class CaptureQuestion
```

A question in the voice capture flow.

---

## CaptureSession

```python
class CaptureSession
```

A voice capture session.

---

## get_voice_store_path

```python
def get_voice_store_path(base_path: Path | str | None=None) -> Path
```

Get path to voice capture store.

---

## save_voice

```python
def save_voice(voice: MorningVoice, store_path: Path | str | None=None) -> Path
```

Save a MorningVoice capture to persistent storage.

---

## load_voice

```python
def load_voice(capture_date: date, store_path: Path | str | None=None) -> MorningVoice | None
```

Load a MorningVoice capture from storage.

---

## load_recent_voices

```python
def load_recent_voices(limit: int=7, store_path: Path | str | None=None) -> list[MorningVoice]
```

Load recent voice captures.

---

## iter_all_voices

```python
def iter_all_voices(store_path: Path | str | None=None) -> Iterator[MorningVoice]
```

Iterate over all voice captures.

---

## voice_to_anchor

```python
def voice_to_anchor(voice: MorningVoice) -> dict[str, Any] | None
```

Convert MorningVoice to voice anchor format.

---

## extract_voice_patterns

```python
def extract_voice_patterns(voices: list[MorningVoice]) -> dict[str, Any]
```

Extract patterns from historical voice captures.

---

## save_voice_async

```python
async def save_voice_async(voice: MorningVoice, store_path: Path | str | None=None) -> Path
```

Async version of save_voice.

---

## load_voice_async

```python
async def load_voice_async(capture_date: date, store_path: Path | str | None=None) -> MorningVoice | None
```

Async version of load_voice.

---

## load_recent_voices_async

```python
async def load_recent_voices_async(limit: int=7, store_path: Path | str | None=None) -> list[MorningVoice]
```

Async version of load_recent_voices.

---

## questions

```python
def questions(self) -> tuple[CaptureQuestion, ...]
```

Get the capture questions.

---

## current_question

```python
def current_question(self) -> CaptureQuestion | None
```

Get the current question, or None if complete.

---

## is_complete

```python
def is_complete(self) -> bool
```

Check if all questions have been answered.

---

## progress

```python
def progress(self) -> float
```

Progress through questions (0.0-1.0).

---

## answer

```python
def answer(self, response: str | None) -> CaptureQuestion | None
```

Record answer to current question and advance.

---

## skip

```python
def skip(self) -> CaptureQuestion | None
```

Skip current question (record as None).

---

## build_voice

```python
def build_voice(self) -> MorningVoice
```

Build MorningVoice from captured answers.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize session state.

---

## services.liminal.coffee.circadian

## circadian

```python
module circadian
```

**AGENTESE:** `void.metabolism.serendipity`

Circadian Resonance: The garden knows things from yesterday.

### Things to Know

ℹ️ Day-of-week matters more than raw recency. Monday mornings resonate with Monday mornings.
  - *Verified in: `test_circadian.py::test_weekday_resonance`*

ℹ️ FOSSIL layer (> 14 days) is the serendipity goldmine. Recent voices are too familiar; ancient ones surprise.
  - *Verified in: `test_circadian.py::test_fossil_serendipity`*

---

## StratigraphyLayer

```python
class StratigraphyLayer(Enum)
```

Layers in the voice archaeology.

---

## ArchaeologicalVoice

```python
class ArchaeologicalVoice
```

A voice from the past with archaeological metadata.

---

## ResonanceMatch

```python
class ResonanceMatch
```

A past morning that resonates with today.

---

## PatternOccurrence

```python
class PatternOccurrence
```

A recurring pattern detected in voice history.

---

## SerendipityWisdom

```python
class SerendipityWisdom
```

Unexpected wisdom from the FOSSIL layer.

---

## CircadianContext

```python
class CircadianContext
```

Full circadian context for today's morning.

---

## CircadianResonance

```python
class CircadianResonance
```

Match today to similar past mornings.

---

## get_circadian_resonance

```python
def get_circadian_resonance() -> CircadianResonance
```

Get or create the global CircadianResonance service.

---

## set_circadian_resonance

```python
def set_circadian_resonance(resonance: CircadianResonance) -> None
```

Set the global CircadianResonance service (for testing).

---

## reset_circadian_resonance

```python
def reset_circadian_resonance() -> None
```

Reset the global CircadianResonance service.

---

## age_range

```python
def age_range(self) -> tuple[int, int | None]
```

Age range in days (min, max or None for unbounded).

---

## for_age

```python
def for_age(cls, days: int) -> 'StratigraphyLayer'
```

Get the layer for a given age in days.

---

## from_voice

```python
def from_voice(cls, voice: 'MorningVoice', today: date | None=None) -> 'ArchaeologicalVoice'
```

Create from a MorningVoice.

---

## weekday_name

```python
def weekday_name(self) -> str
```

Human-readable weekday name.

---

## frequency

```python
def frequency(self) -> float
```

Frequency as ratio (0.0-1.0).

---

## __init__

```python
def __init__(self, serendipity_probability: float=0.1, fossil_age_days: int=14)
```

Initialize CircadianResonance.

---

## get_context

```python
def get_context(self, voices: list['MorningVoice'], today: date | None=None, resonance_limit: int=3, pattern_limit: int=5) -> CircadianContext
```

Get full circadian context for today.

---

## find_resonances

```python
def find_resonances(self, voices: list['MorningVoice'], today: date | None=None, limit: int=3) -> list[ResonanceMatch]
```

Find past mornings that resonate with today.

---

## detect_patterns

```python
def detect_patterns(self, voices: list['MorningVoice'], limit: int=5, min_occurrences: int=2) -> list[PatternOccurrence]
```

Detect recurring patterns in voice history.

---

## maybe_serendipity

```python
def maybe_serendipity(self, voices: list['MorningVoice'], today: date | None=None) -> SerendipityWisdom | None
```

Maybe return unexpected wisdom from the FOSSIL layer.

---

## force_serendipity

```python
def force_serendipity(self, voices: list['MorningVoice'], today: date | None=None) -> SerendipityWisdom | None
```

Force serendipity trigger (for testing).

---

## services.liminal.coffee.cli_formatting

## cli_formatting

```python
module cli_formatting
```

Morning Coffee CLI Formatting: Rich terminal output for the liminal ritual.

---

## format_garden_view

```python
def format_garden_view(data: dict[str, Any]) -> str
```

Format GardenView as rich CLI output.

---

## format_weather

```python
def format_weather(data: dict[str, Any]) -> str
```

Format ConceptualWeather as rich CLI output.

---

## format_menu

```python
def format_menu(data: dict[str, Any]) -> str
```

Format ChallengeMenu as rich CLI output.

---

## format_capture_questions

```python
def format_capture_questions() -> str
```

Format voice capture questions for interactive flow.

---

## format_captured_voice

```python
def format_captured_voice(data: dict[str, Any]) -> str
```

Format the confirmation after a voice is captured.

---

## format_manifest

```python
def format_manifest(data: dict[str, Any]) -> str
```

Format ritual manifest (status overview).

---

## format_history

```python
def format_history(data: dict[str, Any]) -> str
```

Format voice capture history.

---

## format_circadian_context

```python
def format_circadian_context(data: dict[str, Any]) -> str
```

Format CircadianContext for CLI display.

---

## format_hydration_context

```python
def format_hydration_context(data: dict[str, Any]) -> str
```

Format HydrationContext (gotchas + files + anchors) for CLI display.

---

## format_transition

```python
def format_transition(chosen_item: dict[str, Any] | None=None) -> str
```

Format the transition message when beginning work.

---

## format_ritual_start

```python
def format_ritual_start() -> str
```

Header for starting the full ritual.

---

## format_movement_separator

```python
def format_movement_separator(movement_name: str) -> str
```

Separator between movements.

---

## services.liminal.coffee.core

## core

```python
module core
```

CoffeeService: Orchestrates the Morning Coffee ritual.

---

## CoffeeRitualStarted

```python
class CoffeeRitualStarted
```

Emitted when the Morning Coffee ritual begins.

---

## CoffeeMovementCompleted

```python
class CoffeeMovementCompleted
```

Emitted when a movement completes.

---

## CoffeeVoiceCaptured

```python
class CoffeeVoiceCaptured
```

Emitted when a voice capture completes.

---

## CoffeeRitualCompleted

```python
class CoffeeRitualCompleted
```

Emitted when the ritual completes successfully.

---

## CoffeeRitualExited

```python
class CoffeeRitualExited
```

Emitted when the ritual is exited early.

---

## CoffeeService

```python
class CoffeeService
```

Orchestrates the Morning Coffee ritual.

---

## get_coffee_service

```python
def get_coffee_service() -> CoffeeService
```

Get or create the global CoffeeService.

---

## set_coffee_service

```python
def set_coffee_service(service: CoffeeService) -> None
```

Set the global CoffeeService (for testing).

---

## reset_coffee_service

```python
def reset_coffee_service() -> None
```

Reset the global CoffeeService.

---

## __init__

```python
def __init__(self, repo_path: Path | str | None=None, now_md_path: Path | str | None=None, plans_path: Path | str | None=None, brainstorm_path: Path | str | None=None, voice_store_path: Path | str | None=None, synergy_bus: 'SynergyEventBus | None'=None, brain_persistence: 'BrainPersistence | None'=None, voice_stigmergy: VoiceStigmergy | None=None) -> None
```

Initialize CoffeeService.

---

## state

```python
def state(self) -> CoffeeState
```

Current ritual state.

---

## is_active

```python
def is_active(self) -> bool
```

Whether a ritual is currently active.

---

## current_movement

```python
def current_movement(self) -> str | None
```

Current movement name, or None if dormant.

---

## manifest

```python
def manifest(self) -> dict[str, Any]
```

Get ritual manifest — current state and last ritual info.

---

## garden

```python
async def garden(self) -> GardenView
```

Generate the Garden View (Movement 1).

---

## weather

```python
async def weather(self) -> ConceptualWeather
```

Generate the Conceptual Weather (Movement 2).

---

## menu

```python
async def menu(self, garden_view: GardenView | None=None, weather: ConceptualWeather | None=None) -> ChallengeMenu
```

Generate the Challenge Menu (Movement 3).

---

## start_capture

```python
def start_capture(self) -> CaptureSession
```

Start a voice capture session (Movement 4).

---

## save_capture

```python
async def save_capture(self, voice: MorningVoice) -> Path
```

Save a completed voice capture.

---

## reinforce_on_accomplishment

```python
async def reinforce_on_accomplishment(self, accomplished: bool=True) -> int
```

Reinforce pheromones when session ends with accomplishment.

---

## get_stigmergy_patterns

```python
async def get_stigmergy_patterns(self, context: str | None=None, limit: int=5) -> list[tuple[str, float]]
```

Get current stigmergy patterns for display.

---

## search_voice_archaeology

```python
async def search_voice_archaeology(self, query: str, limit: int=10) -> list[dict[str, Any]]
```

Search past voice captures using semantic search.

---

## get_voice_patterns_from_brain

```python
async def get_voice_patterns_from_brain(self) -> dict[str, Any]
```

Extract patterns from voice captures stored in Brain.

---

## wake

```python
def wake(self) -> CoffeeOutput
```

Start the ritual (DORMANT → GARDEN).

---

## advance

```python
def advance(self, command: str, **data: Any) -> CoffeeOutput
```

Advance the ritual state machine.

---

## exit_ritual

```python
def exit_ritual(self) -> CoffeeOutput
```

Exit the ritual at any point. No guilt, no nagging.

---

## quick

```python
async def quick(self) -> tuple[GardenView, ChallengeMenu]
```

Run quick ritual: Garden + Menu only.

---

## get_recent_voices

```python
def get_recent_voices(self, limit: int=7) -> list[MorningVoice]
```

Get recent voice captures.

---

## get_voice

```python
def get_voice(self, capture_date: date) -> MorningVoice | None
```

Get voice capture for a specific date.

---

## services.liminal.coffee.garden

## garden

```python
module garden
```

Garden View Generator: What grew while I slept?

---

## parse_git_stat

```python
def parse_git_stat(since: datetime | None=None, repo_path: Path | str | None=None) -> list[GardenItem]
```

Parse git diff --stat since a given time.

---

## parse_now_md

```python
def parse_now_md(now_md_path: Path | str | None=None) -> dict[str, float]
```

Parse NOW.md to extract jewel progress percentages.

---

## detect_recent_brainstorming

```python
def detect_recent_brainstorming(brainstorm_path: Path | str | None=None, since: datetime | None=None) -> list[GardenItem]
```

Detect recent brainstorming files as seeds.

---

## generate_garden_view

```python
def generate_garden_view(repo_path: Path | str | None=None, now_md_path: Path | str | None=None, brainstorm_path: Path | str | None=None, since: datetime | None=None) -> GardenView
```

Generate the complete Garden View for Morning Coffee.

---

## generate_garden_view_async

```python
async def generate_garden_view_async(repo_path: Path | str | None=None, now_md_path: Path | str | None=None, brainstorm_path: Path | str | None=None, since: datetime | None=None) -> GardenView
```

Async version of generate_garden_view.

---

## services.liminal.coffee.menu

## menu

```python
module menu
```

Menu Generator: What suits my taste this morning?

---

## extract_todos_from_plans

```python
def extract_todos_from_plans(plans_path: Path | str | None=None) -> list[dict[str, Any]]
```

Extract TODO items from plan files.

---

## extract_todos_from_now

```python
def extract_todos_from_now(now_path: Path | str | None=None) -> list[dict[str, Any]]
```

Extract actionable items from NOW.md.

---

## classify_challenge

```python
def classify_challenge(item: str) -> ChallengeLevel
```

Classify an item into a challenge level based on heuristics.

---

## estimate_cognitive_load

```python
def estimate_cognitive_load(item: str) -> float
```

Estimate cognitive load (0.0-1.0) for an item.

---

## generate_menu

```python
def generate_menu(plans_path: Path | str | None=None, now_path: Path | str | None=None, garden_view: GardenView | None=None, weather: ConceptualWeather | None=None, max_per_level: int=3) -> ChallengeMenu
```

Generate the challenge menu for Morning Coffee.

---

## generate_menu_async

```python
async def generate_menu_async(plans_path: Path | str | None=None, now_path: Path | str | None=None, garden_view: GardenView | None=None, weather: ConceptualWeather | None=None, max_per_level: int=3) -> ChallengeMenu
```

Async version of generate_menu.

---

## services.liminal.coffee.node

## node

```python
module node
```

**AGENTESE:** `time.coffee.`

Morning Coffee AGENTESE Node: time.coffee.*

---

## CoffeeManifestResponse

```python
class CoffeeManifestResponse
```

Response for manifest aspect.

---

## GardenResponse

```python
class GardenResponse
```

Response for garden aspect.

---

## WeatherResponse

```python
class WeatherResponse
```

Response for weather aspect.

---

## MenuResponse

```python
class MenuResponse
```

Response for menu aspect.

---

## CaptureRequest

```python
class CaptureRequest
```

Request for capture aspect.

---

## CaptureResponse

```python
class CaptureResponse
```

Response for capture aspect.

---

## BeginResponse

```python
class BeginResponse
```

Response for begin aspect.

---

## HistoryRequest

```python
class HistoryRequest
```

Request for history aspect.

---

## HistoryResponse

```python
class HistoryResponse
```

Response for history aspect.

---

## CoffeeNode

```python
class CoffeeNode(BaseLogosNode)
```

time.coffee — Morning Coffee liminal transition protocol.

---

## get_coffee_node

```python
def get_coffee_node() -> CoffeeNode
```

Get or create the CoffeeNode singleton.

---

## set_coffee_node

```python
def set_coffee_node(node: CoffeeNode) -> None
```

Set the CoffeeNode singleton (for testing).

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize with service.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

View current ritual state.

---

## garden

```python
async def garden(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Generate Garden View (Movement 1).

---

## weather

```python
async def weather(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Generate Conceptual Weather (Movement 2).

---

## menu

```python
async def menu(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Generate Challenge Menu (Movement 3).

---

## capture

```python
async def capture(self, observer: 'Umwelt[Any, Any]', *, non_code_thought: str | None=None, eye_catch: str | None=None, success_criteria: str | None=None, raw_feeling: str | None=None, chosen_challenge: str | None=None) -> Renderable
```

Record voice capture (Movement 4).

---

## begin

```python
async def begin(self, observer: 'Umwelt[Any, Any]') -> Renderable
```

Complete ritual, transition to work.

---

## history

```python
async def history(self, observer: 'Umwelt[Any, Any]', *, limit: int=7, capture_date: str | None=None) -> Renderable
```

View past voice captures.

---

## services.liminal.coffee.polynomial

## polynomial

```python
module polynomial
```

Morning Coffee Polynomial: State machine for the liminal transition ritual.

---

## coffee_directions

```python
def coffee_directions(state: CoffeeState) -> FrozenSet[Any]
```

Valid commands for each Coffee state.

---

## coffee_transition

```python
def coffee_transition(state: CoffeeState, input: Any) -> tuple[CoffeeState, CoffeeOutput]
```

Coffee state transition function.

---

## services.liminal.coffee.stigmergy

## stigmergy

```python
module stigmergy
```

**AGENTESE:** `void.metabolism.stigmergy`

VoiceStigmergy: Wire stigmergic memory to Morning Coffee.

### Things to Know

ℹ️ Pheromone field is in-memory by default. Persist to D-gent for cross-session stigmergy.
  - *Verified in: `test_voice_stigmergy.py::test_field_persists`*

ℹ️ Decay rate is 5% per day (0.002 per hour). This matches the spec's "reinforcement vs decay" balance.
  - *Verified in: `test_voice_stigmergy.py::TestPheromoneDecay::test_daily_decay_reduces_intensity`*

---

## PheromoneDeposit

```python
class PheromoneDeposit
```

A record of pheromones deposited from a voice capture.

---

## VoiceStigmergy

```python
class VoiceStigmergy
```

Service that connects MorningVoice to PheromoneField.

---

## get_voice_stigmergy

```python
def get_voice_stigmergy() -> VoiceStigmergy
```

Get or create the global VoiceStigmergy service.

---

## set_voice_stigmergy

```python
def set_voice_stigmergy(service: VoiceStigmergy) -> None
```

Set the global VoiceStigmergy service (for testing).

---

## reset_voice_stigmergy

```python
def reset_voice_stigmergy() -> None
```

Reset the global VoiceStigmergy service.

---

## __init__

```python
def __init__(self, field: PheromoneField | None=None, store_path: Path | str | None=None, persistence: 'MetabolismPersistence | None'=None)
```

Initialize VoiceStigmergy.

---

## deposit_from_voice

```python
async def deposit_from_voice(self, voice: 'MorningVoice', base_intensity: float=1.0) -> PheromoneDeposit
```

Deposit pheromones from a MorningVoice capture.

---

## reinforce_accomplished

```python
async def reinforce_accomplished(self, deposit: PheromoneDeposit, factor: float | None=None) -> int
```

Reinforce pheromones when a task is accomplished.

---

## reinforce_partial

```python
async def reinforce_partial(self, deposit: PheromoneDeposit) -> int
```

Reinforce pheromones for partial completion.

---

## sense_patterns

```python
async def sense_patterns(self, context: str | None=None, limit: int=10) -> list[tuple[str, float]]
```

Sense current pheromone patterns.

---

## get_top_patterns

```python
async def get_top_patterns(self, limit: int=5) -> list[tuple[str, float]]
```

Get the top N patterns without context filtering.

---

## apply_daily_decay

```python
async def apply_daily_decay(self) -> int
```

Apply a day's worth of decay to the field.

---

## save

```python
async def save(self) -> Path
```

Persist the pheromone field to storage.

---

## load

```python
async def load(self) -> bool
```

Load the pheromone field from storage.

---

## stats

```python
def stats(self) -> dict[str, Any]
```

Get field statistics.

---

## services.liminal.coffee.types

## types

```python
module types
```

Morning Coffee Types: Core data structures for the liminal transition ritual.

---

## CoffeeState

```python
class CoffeeState(Enum)
```

Positions in the Morning Coffee polynomial.

---

## ChallengeLevel

```python
class ChallengeLevel(Enum)
```

Challenge gradients for the Menu.

---

## Movement

```python
class Movement
```

A phase of the Morning Coffee ritual.

---

## GardenCategory

```python
class GardenCategory(Enum)
```

Categories of garden items.

---

## GardenItem

```python
class GardenItem
```

A single item in the garden view.

---

## GardenView

```python
class GardenView
```

The Garden View — Movement 1.

---

## WeatherType

```python
class WeatherType(Enum)
```

Types of conceptual weather patterns.

---

## WeatherPattern

```python
class WeatherPattern
```

A single conceptual weather pattern.

---

## ConceptualWeather

```python
class ConceptualWeather
```

The Conceptual Weather — Movement 2.

---

## MenuItem

```python
class MenuItem
```

A potential work item on the menu.

---

## ChallengeMenu

```python
class ChallengeMenu
```

The Menu — Movement 3.

---

## MorningVoice

```python
class MorningVoice
```

Fresh capture of Kent's authentic morning state.

---

## RitualEvent

```python
class RitualEvent
```

Input event to the Coffee polynomial.

---

## CoffeeOutput

```python
class CoffeeOutput
```

Output from the Coffee polynomial.

---

## emoji

```python
def emoji(self) -> str
```

Visual indicator for the challenge level.

---

## description

```python
def description(self) -> str
```

Human-readable description.

---

## cognitive_load

```python
def cognitive_load(self) -> float
```

Estimated cognitive load (0.0-1.0).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## is_empty

```python
def is_empty(self) -> bool
```

Check if the garden view has any items.

---

## total_items

```python
def total_items(self) -> int
```

Total number of items across all categories.

---

## emoji

```python
def emoji(self) -> str
```

Visual indicator.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## is_empty

```python
def is_empty(self) -> bool
```

Check if there are any weather patterns.

---

## all_patterns

```python
def all_patterns(self) -> list[WeatherPattern]
```

Get all patterns as a flat list.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## is_empty

```python
def is_empty(self) -> bool
```

Check if menu has any items (serendipity always available).

---

## get_items_by_level

```python
def get_items_by_level(self, level: ChallengeLevel) -> tuple[MenuItem, ...]
```

Get items for a specific challenge level.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> 'MorningVoice'
```

Create from dictionary.

---

## is_substantive

```python
def is_substantive(self) -> bool
```

Check if the capture has meaningful content.

---

## as_voice_anchor

```python
def as_voice_anchor(self) -> dict[str, Any] | None
```

Convert to a voice anchor if substantive.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## services.liminal.coffee.weather

## weather

```python
module weather
```

Conceptual Weather Analyzer: What's shifting in the atmosphere?

---

## parse_plan_headers

```python
def parse_plan_headers(plans_path: Path | str | None=None) -> list[dict[str, str]]
```

Parse plan file headers for status and context.

---

## analyze_commit_messages

```python
def analyze_commit_messages(since: datetime | None=None, repo_path: Path | str | None=None, max_commits: int=50) -> list[str]
```

Get recent commit messages for pattern analysis.

---

## detect_refactoring

```python
def detect_refactoring(commit_messages: list[str], plans: list[dict[str, str]]) -> list[WeatherPattern]
```

Detect refactoring patterns.

---

## detect_emerging

```python
def detect_emerging(commit_messages: list[str], plans: list[dict[str, str]]) -> list[WeatherPattern]
```

Detect emerging patterns and insights.

---

## detect_scaffolding

```python
def detect_scaffolding(commit_messages: list[str], plans: list[dict[str, str]]) -> list[WeatherPattern]
```

Detect scaffolding/architecture patterns.

---

## detect_tension

```python
def detect_tension(commit_messages: list[str], plans: list[dict[str, str]]) -> list[WeatherPattern]
```

Detect tensions and competing concerns.

---

## generate_weather

```python
def generate_weather(repo_path: Path | str | None=None, plans_path: Path | str | None=None, since: datetime | None=None) -> ConceptualWeather
```

Generate the Conceptual Weather for Morning Coffee.

---

## generate_weather_async

```python
async def generate_weather_async(repo_path: Path | str | None=None, plans_path: Path | str | None=None, since: datetime | None=None) -> ConceptualWeather
```

Async version of generate_weather.

---

## services.living_docs.__init__

## __init__

```python
module __init__
```

Living Docs: Documentation as Projection

---

## services.living_docs.brain_adapter

## brain_adapter

```python
module brain_adapter
```

**AGENTESE:** `concept.docs.hydrate`

HydrationBrainAdapter: Wire Brain semantic search to Living Docs hydration.

### Things to Know

ℹ️ Brain requires async session; Hydrator is sync. Use asyncio.run() or async API for integration.
  - *Verified in: `test_brain_adapter.py::TestSemanticTeaching::test_returns_teaching_from_brain_results`*

ℹ️ Brain may return empty if no crystals exist. Fall back to keyword matching gracefully.
  - *Verified in: `test_brain_adapter.py::TestSemanticTeaching::test_returns_empty_without_brain`*

---

## ScoredTeachingResult

```python
class ScoredTeachingResult
```

A teaching result with similarity score for semantic ranking.

---

## ASHCEvidence

```python
class ASHCEvidence
```

Prior evidence from ASHC for related work.

---

## HydrationBrainAdapter

```python
class HydrationBrainAdapter
```

Adapter that connects Living Docs hydration to Brain semantic search.

---

## get_hydration_brain_adapter

```python
def get_hydration_brain_adapter() -> HydrationBrainAdapter
```

Get or create the global HydrationBrainAdapter.

---

## set_hydration_brain_adapter

```python
def set_hydration_brain_adapter(adapter: HydrationBrainAdapter) -> None
```

Set the global HydrationBrainAdapter (for DI/testing).

---

## reset_hydration_brain_adapter

```python
def reset_hydration_brain_adapter() -> None
```

Reset the global adapter.

---

## __init__

```python
def __init__(self, brain: 'BrainPersistence | None'=None)
```

Initialize adapter.

---

## is_available

```python
def is_available(self) -> bool
```

Check if Brain integration is available.

---

## find_semantic_teaching

```python
async def find_semantic_teaching(self, query: str, limit: int=10, min_similarity: float=0.3) -> list[ScoredTeachingResult]
```

Find teaching moments using Brain's semantic search.

---

## find_prior_evidence

```python
async def find_prior_evidence(self, task_pattern: str, limit: int=3) -> list[ASHCEvidence]
```

Find prior ASHC evidence for similar work.

---

## semantic_hydrate

```python
async def semantic_hydrate(self, task: str, teaching_limit: int=10, evidence_limit: int=3) -> dict[str, Any]
```

Get combined semantic context for a task.

---

## services.living_docs.extractor

## extractor

```python
module extractor
```

Docstring Extractor: Source -> DocNode

### Examples
```python
>>> ' and 'Example:' sections
```

### Things to Know

ℹ️ AST parsing requires valid Python syntax.
  - *Verified in: `test_extractor.py::test_invalid_syntax`*

🚨 **Critical:** Teaching section must use 'gotcha:' keyword for extraction.
  - *Verified in: `test_extractor.py::test_teaching_pattern`*

---

## DocstringExtractor

```python
class DocstringExtractor
```

Extract DocNodes from Python source files.

### Things to Know

ℹ️ Tier determination now includes agents/ and protocols/ as RICH.
  - *Verified in: `test_extractor.py::test_tier_rich_expanded`*

---

## extract_from_object

```python
def extract_from_object(obj: object) -> DocNode | None
```

Extract a DocNode from a Python object.

---

## should_extract

```python
def should_extract(self, path: Path) -> bool
```

Check if a file should be extracted (not excluded).

---

## extract_file

```python
def extract_file(self, path: Path) -> list[DocNode]
```

Extract DocNodes from a Python source file.

---

## extract_module_docstring

```python
def extract_module_docstring(self, path: Path) -> DocNode | None
```

Extract module-level docstring as a DocNode.

---

## extract_module

```python
def extract_module(self, source: str, module_name: str='') -> list[DocNode]
```

Extract DocNodes from Python source code.

---

## services.living_docs.generator

## generator

```python
module generator
```

**AGENTESE:** `concept.docs.generate`

Reference Documentation Generator

### Things to Know

ℹ️ generate_to_directory() creates directories if they don't exist. It will NOT overwrite existing files unless overwrite=True.
  - *Verified in: `test_generator.py::test_no_overwrite_by_default`*

---

## CategoryConfig

```python
class CategoryConfig
```

Configuration for a documentation category.

---

## GeneratedDocs

```python
class GeneratedDocs
```

Generated documentation output.

---

## GeneratedFile

```python
class GeneratedFile
```

Metadata for a generated documentation file.

---

## GenerationManifest

```python
class GenerationManifest
```

Manifest of all generated documentation files.

---

## ReferenceGenerator

```python
class ReferenceGenerator
```

Generate comprehensive reference documentation.

---

## generate_reference

```python
def generate_reference() -> str
```

Convenience function to generate full reference docs.

---

## generate_gotchas

```python
def generate_gotchas() -> str
```

Convenience function to generate gotchas page.

---

## generate_to_directory

```python
def generate_to_directory(output_dir: Path, overwrite: bool=False) -> GenerationManifest
```

Convenience function to generate docs to a directory.

---

## file_count

```python
def file_count(self) -> int
```

Number of files generated.

---

## to_dict

```python
def to_dict(self) -> dict[str, object]
```

Convert to dictionary for serialization.

---

## generate_all

```python
def generate_all(self) -> str
```

Generate complete reference documentation as markdown.

---

## generate_gotchas

```python
def generate_gotchas(self) -> str
```

Generate a dedicated gotchas/teaching moments page.

---

## generate_to_directory

```python
def generate_to_directory(self, output_dir: Path, overwrite: bool=False) -> GenerationManifest
```

Generate complete reference documentation to a directory structure.

---

## services.living_docs.hydrator

## hydrator

```python
module hydrator
```

**AGENTESE:** `concept.docs.hydrate`

Hydration Context Generator for Claude Code Sessions

### Things to Know

ℹ️ hydrate_context() is keyword-based, not semantic. Use Brain vectors for semantic similarity (future work).
  - *Verified in: `test_hydrator.py::test_keyword_matching`*

ℹ️ Voice anchors are curated, not mined. They come from _focus.md, not git history.
  - *Verified in: `test_hydrator.py::test_voice_anchors`*

---

## HydrationContext

```python
class HydrationContext
```

Context blob optimized for Claude Code sessions.

### Things to Know

ℹ️ to_markdown() output is designed for system prompts. It's not a reference doc—it's a focus lens.
  - *Verified in: `test_hydrator.py::test_markdown_format`*

---

## Hydrator

```python
class Hydrator
```

Generate task-relevant context for Claude Code sessions.

### Things to Know

ℹ️ Hydrator prefers keyword matching; Brain is supplemental. Semantic matching is best-effort—graceful degradation if unavailable.
  - *Verified in: `test_hydrator.py::test_keyword_extraction`*

---

## hydrate_context

```python
def hydrate_context(task: str) -> HydrationContext
```

Generate hydration context for a task.

---

## relevant_for_file

```python
def relevant_for_file(path: str) -> HydrationContext
```

Get relevant context for editing a specific file.

---

## to_markdown

```python
def to_markdown(self) -> str
```

Render as markdown suitable for system prompt or /hydrate.

---

## to_dict

```python
def to_dict(self) -> dict[str, object]
```

Convert to dictionary for JSON serialization.

---

## hydrate

```python
def hydrate(self, task: str) -> HydrationContext
```

Generate hydration context for a task (sync version).

---

## hydrate_async

```python
async def hydrate_async(self, task: str) -> HydrationContext
```

Generate hydration context with semantic enhancement.

---

## services.living_docs.linter

## linter

```python
module linter
```

**AGENTESE:** `concept.docs.lint`

Docstring Linter: Enforce Documentation Standards

### Things to Know

ℹ️ Only lint public symbols (no _ prefix). Private helpers don't need documentation.
  - *Verified in: `test_linter.py::test_skip_private_symbols`*

ℹ️ AST parsing fails gracefully—returns empty results, not exceptions. Invalid Python is already caught by ruff.
  - *Verified in: `test_linter.py::test_invalid_syntax_graceful`*

---

## LintResult

```python
class LintResult
```

A single documentation lint issue.

---

## LintStats

```python
class LintStats
```

Statistics from a lint run.

---

## DocstringLinter

```python
class DocstringLinter
```

Linter for Python documentation standards.

### Things to Know

ℹ️ The linter uses AST, not runtime imports. This means it can lint broken code without crashes.
  - *Verified in: `test_linter.py::test_lint_broken_imports`*

---

## lint_file

```python
def lint_file(path: Path) -> list[LintResult]
```

Lint a single Python file for documentation issues.

---

## lint_directory

```python
def lint_directory(path: Path, changed_only: bool=False, changed_files: set[Path] | None=None) -> LintStats
```

Lint all Python files in a directory.

---

## get_changed_files

```python
def get_changed_files(repo_root: Path) -> set[Path]
```

Get list of Python files changed since last commit.

---

## to_dict

```python
def to_dict(self) -> dict[str, object]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, object]
```

Convert to dictionary for serialization.

---

## should_lint

```python
def should_lint(self, path: Path) -> bool
```

Check if a file should be linted (not excluded).

---

## lint_file

```python
def lint_file(self, path: Path) -> list[LintResult]
```

Lint a single Python file for documentation issues.

---

## lint_source

```python
def lint_source(self, source: str, module_name: str, path: Path | None=None) -> list[LintResult]
```

Lint Python source code for documentation issues.

---

## lint_directory

```python
def lint_directory(self, path: Path, changed_only: bool=False, changed_files: set[Path] | None=None) -> LintStats
```

Lint all Python files in a directory.

---

## services.living_docs.node

## node

```python
module node
```

Living Docs AGENTESE Nodes

---

## LivingDocsNode

```python
class LivingDocsNode(BaseLogosNode)
```

AGENTESE node for Living Documentation.

### Things to Know

🚨 **Critical:** Observer kind must be one of: human, agent, ide.
  - *Verified in: `test_node.py::test_observer_validation`*

---

## SelfDocsNode

```python
class SelfDocsNode(BaseLogosNode)
```

self.docs - documentation in current scope.

---

## get_living_docs_node

```python
def get_living_docs_node() -> LivingDocsNode
```

Get a LivingDocsNode instance.

---

## get_self_docs_node

```python
def get_self_docs_node() -> SelfDocsNode
```

Get a SelfDocsNode instance.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize mutable defaults.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any] | Observer') -> Renderable
```

Collapse to observer-appropriate representation.

---

## extract

```python
async def extract(self, observer: 'Umwelt[Any, Any] | Observer', path: str) -> Renderable
```

Extract documentation from a source file.

---

## project

```python
async def project(self, observer: 'Umwelt[Any, Any] | Observer', path: str, observer_kind: Literal['human', 'agent', 'ide']='human', density: Literal['compact', 'comfortable', 'spacious']='comfortable', symbol: str | None=None) -> Renderable
```

Project documentation for a specific observer.

---

## list

```python
async def list(self, observer: 'Umwelt[Any, Any] | Observer', path: str | None=None, tier: Literal['minimal', 'standard', 'rich'] | None=None, only_with_teaching: bool=False) -> Renderable
```

List DocNodes with optional filtering.

---

## gotchas

```python
async def gotchas(self, observer: 'Umwelt[Any, Any] | Observer', path: str, severity: Literal['info', 'warning', 'critical'] | None=None) -> Renderable
```

Get all teaching moments (gotchas) from a file.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any] | Observer') -> Renderable
```

Collapse to observer-appropriate representation.

---

## for_file

```python
async def for_file(self, observer: 'Umwelt[Any, Any] | Observer', path: str, observer_kind: Literal['human', 'agent', 'ide']='human', density: Literal['compact', 'comfortable', 'spacious']='comfortable') -> Renderable
```

Get documentation for a specific file.

---

## gotchas

```python
async def gotchas(self, observer: 'Umwelt[Any, Any] | Observer', path: str | None=None, scope: str | None=None) -> Renderable
```

Get teaching moments in the current scope.

---

## services.living_docs.projector

## projector

```python
module projector
```

Living Docs Projector: DocNode x Observer -> Surface

### Things to Know

ℹ️ Projection is a single function, not a class hierarchy.
  - *Verified in: `test_projector.py::test_single_function`*

ℹ️ Density only applies to human observers.
  - *Verified in: `test_projector.py::test_density_human_only`*

---

## DensityParams

```python
class DensityParams
```

Parameters that vary by density level.

---

## project

```python
def project(node: DocNode, observer: LivingDocsObserver) -> Surface
```

Project a DocNode to a Surface for a specific observer.

---

## LivingDocsProjector

```python
class LivingDocsProjector
```

Stateless projector for use in AGENTESE nodes.

---

## project

```python
def project(self, node: DocNode, observer: LivingDocsObserver) -> Surface
```

Project a DocNode to a Surface.

---

## project_many

```python
def project_many(self, nodes: list[DocNode], observer: LivingDocsObserver) -> list[Surface]
```

Project multiple DocNodes.

---

## project_with_filter

```python
def project_with_filter(self, nodes: list[DocNode], observer: LivingDocsObserver, *, min_tier: Tier=Tier.MINIMAL, only_with_teaching: bool=False) -> list[Surface]
```

Project nodes with filtering.

---

## services.living_docs.spec_extractor

## spec_extractor

```python
module spec_extractor
```

Spec Extractor: Markdown Spec -> DocNode

### Things to Know

ℹ️ Spec files have different structure than Python docstrings. Use markdown-aware parsing, not AST.
  - *Verified in: `test_spec_extractor.py::test_markdown_structure`*

🚨 **Critical:** Anti-patterns are warnings, Laws are critical. Severity mapping matters for proper prioritization.
  - *Verified in: `test_spec_extractor.py::test_severity_mapping`*

---

## SpecSection

```python
class SpecSection
```

A section from a markdown spec file.

---

## SpecExtractor

```python
class SpecExtractor
```

Extract DocNodes from markdown specification files.

### Things to Know

ℹ️ The extractor processes spec/ files, not impl/ Python files. Use DocstringExtractor for Python, SpecExtractor for markdown.
  - *Verified in: `test_spec_extractor.py::test_file_type_separation`*

---

## should_extract

```python
def should_extract(self, path: Path) -> bool
```

Check if a file should be extracted (not excluded).

---

## extract_file

```python
def extract_file(self, path: Path) -> list[DocNode]
```

Extract DocNodes from a markdown specification file.

---

## extract_spec

```python
def extract_spec(self, content: str, module_name: str='') -> list[DocNode]
```

Extract DocNodes from markdown specification content.

---

## extract_spec_summary

```python
def extract_spec_summary(self, path: Path) -> DocNode | None
```

Extract a top-level summary DocNode for the entire spec file.

---

## services.living_docs.teaching

## teaching

```python
module teaching
```

**AGENTESE:** `concept.docs.teaching`

Teaching Moments Query API

### Things to Know

ℹ️ Evidence paths are relative to impl/claude.
  - *Verified in: `test_teaching.py::test_evidence_path_resolution`*

---

## TeachingResult

```python
class TeachingResult
```

A teaching moment with its source context.

---

## TeachingQuery

```python
class TeachingQuery
```

Query parameters for filtering teaching moments.

---

## VerificationResult

```python
class VerificationResult
```

Result of evidence verification for a teaching moment.

---

## TeachingStats

```python
class TeachingStats
```

Statistics about teaching moments in the codebase.

---

## TeachingCollector

```python
class TeachingCollector
```

Collect and query teaching moments from the codebase.

---

## query_teaching

```python
def query_teaching(severity: Literal['critical', 'warning', 'info'] | None=None, module_pattern: str | None=None, symbol_pattern: str | None=None, with_evidence: bool | None=None) -> list[TeachingResult]
```

Query teaching moments with optional filters.

---

## verify_evidence

```python
def verify_evidence() -> list[VerificationResult]
```

Verify that all evidence paths exist.

---

## get_teaching_stats

```python
def get_teaching_stats() -> TeachingStats
```

Get statistics about teaching moments in the codebase.

---

## collect_all

```python
def collect_all(self) -> Iterator[TeachingResult]
```

Collect all teaching moments from the codebase.

---

## query

```python
def query(self, query: TeachingQuery) -> list[TeachingResult]
```

Query teaching moments with filters.

---

## verify_evidence

```python
def verify_evidence(self) -> list[VerificationResult]
```

Verify that all evidence paths exist.

---

## get_stats

```python
def get_stats(self) -> TeachingStats
```

Get statistics about teaching moments.

---

## services.living_docs.types

## types

```python
module types
```

Living Docs Core Types

---

## Tier

```python
class Tier(Enum)
```

Extraction tier determines extraction depth.

---

## TeachingMoment

```python
class TeachingMoment
```

A gotcha with provenance. The killer feature.

### Things to Know

🚨 **Critical:** Always include evidence when creating TeachingMoments.
  - *Verified in: `test_types.py::test_teaching_moment_evidence`*

---

## DocNode

```python
class DocNode
```

Atomic documentation primitive extracted from source.

### Things to Know

ℹ️ agentese_path is extracted from "AGENTESE: <path>" in docstrings. Not all symbols have AGENTESE paths—only exposed nodes do.
  - *Verified in: `test_extractor.py::test_agentese_path_extraction`*

ℹ️ related_symbols should be kept small (max 5). Too many cross-references makes navigation confusing.
  - *Verified in: `test_types.py::test_related_symbols_limit`*

---

## LivingDocsObserver

```python
class LivingDocsObserver
```

Who's reading determines what they see.

---

## Surface

```python
class Surface
```

Projected output for an observer.

---

## Verification

```python
class Verification
```

Round-trip verification result.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_text

```python
def to_text(self) -> str
```

Convert to human-readable text.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## compression_adequate

```python
def compression_adequate(self) -> bool
```

Check if docs adequately compress implementation.

---

## services.morpheus.__init__

## __init__

```python
module __init__
```

**AGENTESE:** `world.morpheus.`

Morpheus Crown Jewel: LLM Gateway as Metaphysical Fullstack Agent.

---

## services.morpheus.adapters.__init__

## __init__

```python
module __init__
```

Morpheus Adapters: LLM backend implementations.

---

## services.morpheus.adapters.base

## base

```python
module base
```

Morpheus Adapter Protocol: Interface for LLM backends.

---

## AdapterConfig

```python
class AdapterConfig
```

Base configuration for adapters.

---

## Adapter

```python
class Adapter(Protocol)
```

Protocol for LLM adapters.

---

## complete

```python
async def complete(self, request: 'ChatRequest') -> 'ChatResponse'
```

Process a chat completion request.

---

## stream

```python
async def stream(self, request: 'ChatRequest') -> AsyncIterator['StreamChunk']
```

Process a streaming chat completion request.

---

## is_available

```python
def is_available(self) -> bool
```

Check if this adapter is available and can process requests.

---

## health_check

```python
def health_check(self) -> dict[str, Any]
```

Return health status for monitoring.

---

## supports_streaming

```python
def supports_streaming(self) -> bool
```

Check if this adapter supports streaming.

---

## services.morpheus.adapters.claude_cli

## claude_cli

```python
module claude_cli
```

Claude CLI Adapter: Wraps ClaudeCLIRuntime with concurrency control.

---

## ClaudeCLIConfig

```python
class ClaudeCLIConfig
```

Configuration for Claude CLI adapter.

---

## ClaudeCLIAdapter

```python
class ClaudeCLIAdapter
```

Adapter from OpenAI-compatible requests to ClaudeCLIRuntime.

---

## request_count

```python
def request_count(self) -> int
```

Total requests processed.

---

## complete

```python
async def complete(self, request: ChatRequest) -> ChatResponse
```

Process a chat completion request.

---

## stream

```python
async def stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]
```

Process a streaming chat completion request.

---

## is_available

```python
def is_available(self) -> bool
```

Check if Claude CLI is available.

---

## supports_streaming

```python
def supports_streaming(self) -> bool
```

Claude CLI supports streaming (via result chunking).

---

## health_check

```python
def health_check(self) -> dict[str, Any]
```

Return health status for monitoring.

---

## services.morpheus.adapters.mock

## mock

```python
module mock
```

Mock Adapter: Testing adapter with queued responses.

---

## MockAdapter

```python
class MockAdapter
```

Mock adapter for testing without real LLM calls.

---

## complete

```python
async def complete(self, request: ChatRequest) -> ChatResponse
```

Return mock response.

---

## stream

```python
async def stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]
```

Stream mock response in chunks.

---

## history

```python
def history(self) -> list[ChatRequest]
```

Request history for testing assertions.

---

## queue_response

```python
def queue_response(self, response: str) -> None
```

Add a response to the queue.

---

## clear_history

```python
def clear_history(self) -> None
```

Clear request history.

---

## services.morpheus.contracts

## contracts

```python
module contracts
```

Morpheus Contracts: Request/Response types for AGENTESE aspects.

---

## MorpheusManifestResponse

```python
class MorpheusManifestResponse
```

Response for world.morpheus.manifest.

### Things to Know

ℹ️ These contract types are for AGENTESE OpenAPI schema generation. They are NOT the same as the internal types in types.py/persistence.py.
  - *Verified in: `node.py uses MorpheusManifestRendering, not this`*

---

## CompleteRequest

```python
class CompleteRequest
```

Request for world.morpheus.complete.

### Things to Know

ℹ️ `messages` is a list of dicts, not ChatMessage objects. The node converts these to ChatMessage internally.
  - *Verified in: `node.py::_handle_complete converts dicts`*

---

## CompleteResponse

```python
class CompleteResponse
```

Response for world.morpheus.complete.

### Things to Know

ℹ️ `response` is the extracted text, not the full ChatResponse. Use world.morpheus.manifest to see detailed response metadata.
  - *Verified in: `node.py::_handle_complete extracts response_text`*

---

## StreamRequest

```python
class StreamRequest
```

Request for world.morpheus.stream.

### Things to Know

ℹ️ Same structure as CompleteRequest, but the node sets stream=True internally and returns an async generator instead of a response.
  - *Verified in: `node.py::_handle_stream sets request.stream = True`*

---

## StreamResponse

```python
class StreamResponse
```

Response metadata for world.morpheus.stream (actual data is SSE).

### Things to Know

ℹ️ The actual content is delivered via SSE, not in this response. This is just metadata confirming the stream started.
  - *Verified in: `node.py::_handle_stream returns stream generator`*

---

## ProvidersResponse

```python
class ProvidersResponse
```

Response for world.morpheus.providers.

### Things to Know

ℹ️ The `filter` field indicates which filter was applied based on observer archetype: "all" (admin), "enabled" (dev), "public" (guest).
  - *Verified in: `test_node.py::TestMorpheusNodeProviders`*

---

## MetricsResponse

```python
class MetricsResponse
```

Response for world.morpheus.metrics.

### Things to Know

ℹ️ This aspect requires "developer" or "admin" archetype. Guests calling metrics get a Forbidden error.
  - *Verified in: `test_node.py::TestMorpheusNodeMetrics`*

---

## HealthResponse

```python
class HealthResponse
```

Response for world.morpheus.health.

### Things to Know

ℹ️ "healthy" means at least one provider is available—not that all are. "degraded" = some providers down, "unhealthy" = all providers down.
  - *Verified in: `test_node.py::TestMorpheusNodeHealth`*

---

## RouteRequest

```python
class RouteRequest
```

Request for world.morpheus.route.

### Things to Know

ℹ️ This is a query aspect, not a mutation. It tells you WHERE a model would route without actually making a request.
  - *Verified in: `test_node.py::TestMorpheusNodeRoute`*

---

## RouteResponse

```python
class RouteResponse
```

Response for world.morpheus.route.

### Things to Know

ℹ️ `available` is false if no provider matches the model prefix. Check `available` before making a complete/stream request.
  - *Verified in: `test_node.py::test_route_for_unknown_model`*

---

## RateLimitResponse

```python
class RateLimitResponse
```

Response for world.morpheus.rate_limit.

### Things to Know

ℹ️ `reset_at` is a timestamp hint, not a guarantee. Sliding window limits may clear earlier as old requests age out.
  - *Verified in: `gateway.py RateLimitState uses 60s sliding window`*

---

## services.morpheus.gateway

## gateway

```python
module gateway
```

**AGENTESE:** `world.morpheus`

Morpheus Gateway: Routes requests to LLM backends.

---

## ProviderConfig

```python
class ProviderConfig
```

Configuration for a single LLM provider.

### Things to Know

ℹ️ The `public` flag controls visibility to non-admin observers. Private providers (public=False) still work but aren't listed for guests. Use for internal/experimental providers.
  - *Verified in: `test_node.py::TestMorpheusNodeProviders`*

🚨 **Critical:** The `prefix` is the ONLY routing mechanism. Model names must START with this prefix. If you register prefix="claude-", then "claude-opus" routes but "anthropic-claude" does not.
  - *Verified in: `test_rate_limit.py::TestGatewayRateLimiting`*

---

## GatewayConfig

```python
class GatewayConfig
```

Configuration for the Morpheus Gateway.

### Things to Know

🚨 **Critical:** The `rate_limit_by_archetype` dict is the source of truth for per-observer limits. Unknown archetypes fall back to `rate_limit_rpm`. Always ensure new archetypes are added here BEFORE use.
  - *Verified in: `test_rate_limit.py::TestGatewayRateLimiting`*

ℹ️ Limits are PER-MINUTE sliding windows, not hard resets. A burst of 10 requests will block for ~60s, not until the next minute boundary.
  - *Verified in: `test_rate_limit.py::TestRateLimitState`*

---

## RateLimitState

```python
class RateLimitState
```

Thread-safe rate limit tracking using sliding window.

### Things to Know

ℹ️ Each archetype has its OWN window. Exhausting "guest" limits does not affect "admin" limits. This is by design—archetypes represent trust levels, not resource pools.
  - *Verified in: `test_rate_limit.py::test_check_and_record_separate_archetypes`*

ℹ️ The sliding window implementation means old entries are pruned on EVERY check. High-traffic archetypes may see O(n) cleanup cost. For production at scale, consider external rate limiting (Redis).
  - *Verified in: `test_rate_limit.py::TestRateLimitState`*

---

## RateLimitError

```python
class RateLimitError(Exception)
```

Raised when rate limit is exceeded.

### Things to Know

ℹ️ The `retry_after` field is a HINT, not a guarantee. The sliding window may clear sooner if earlier requests age out. Clients should use exponential backoff, not fixed waits.
  - *Verified in: `test_rate_limit.py::TestRateLimitError`*

ℹ️ In streaming mode, rate limit errors are YIELDED as content, not raised. Check the first chunk for "Rate limit exceeded".
  - *Verified in: `test_rate_limit.py::test_stream_respects_rate_limit`*

---

## MorpheusGateway

```python
class MorpheusGateway
```

Morpheus Gateway: Routes OpenAI-compatible requests to LLM backends.

### Things to Know

ℹ️ Providers are matched by PREFIX, first match wins. Register more specific prefixes BEFORE generic ones. "claude-3-opus" before "claude-".
  - *Verified in: `test_rate_limit.py::TestGatewayRateLimiting`*

🚨 **Critical:** Streaming errors are yielded as content, not raised as exceptions. This is intentional—SSE clients expect data, not connection drops. Always check first chunk for error messages.
  - *Verified in: `test_streaming.py::test_gateway_stream_unknown_model_yields_error`*

ℹ️ The gateway is stateless except for rate limiting. Provider registration order matters for matching, but requests are independent.
  - *Verified in: `test_node.py::TestMorpheusNodeComplete`*

---

## check_and_record

```python
def check_and_record(self, archetype: str, limit: int) -> tuple[bool, int]
```

Check rate limit and record request if allowed.

---

## get_usage

```python
def get_usage(self, archetype: str) -> int
```

Get current request count in the window.

---

## register_provider

```python
def register_provider(self, name: str, adapter: 'Adapter', prefix: str, enabled: bool=True, public: bool=True) -> None
```

Register an LLM provider.

---

## unregister_provider

```python
def unregister_provider(self, name: str) -> bool
```

Remove a provider. Returns True if removed.

---

## complete

```python
async def complete(self, request: 'ChatRequest', archetype: str='guest') -> 'ChatResponse'
```

Process a chat completion request.

---

## stream

```python
async def stream(self, request: 'ChatRequest', archetype: str='guest') -> AsyncIterator['StreamChunk']
```

Process a streaming chat completion request.

---

## list_providers

```python
def list_providers(self, *, enabled_only: bool=False, public_only: bool=False) -> list[ProviderConfig]
```

List providers with optional filtering.

---

## get_provider

```python
def get_provider(self, name: str) -> Optional[ProviderConfig]
```

Get a specific provider by name.

---

## route_info

```python
def route_info(self, model: str) -> dict[str, Any]
```

Get routing info for a model (for debugging/introspection).

---

## rate_limit_status

```python
def rate_limit_status(self, archetype: str) -> dict[str, Any]
```

Get rate limit status for an archetype.

---

## health_check

```python
def health_check(self) -> dict[str, Any]
```

Return comprehensive health status.

---

## request_count

```python
def request_count(self) -> int
```

Total requests processed.

---

## error_count

```python
def error_count(self) -> int
```

Total errors encountered.

---

## services.morpheus.node

## node

```python
module node
```

Morpheus AGENTESE Node: @node("world.morpheus")

---

## MorpheusManifestRendering

```python
class MorpheusManifestRendering
```

Rendering for Morpheus status manifest.

### Things to Know

ℹ️ This is a Renderable, not a Response. It has both to_dict() and to_text() for multi-target projection (JSON/CLI/TUI).
  - *Verified in: `test_node.py::TestMorpheusNodeManifest`*

---

## CompletionRendering

```python
class CompletionRendering
```

Rendering for completion result.

### Things to Know

ℹ️ The `response_text` is extracted from choices[0].message.content. Multi-choice completions (n>1) are not yet supported in rendering.
  - *Verified in: `test_node.py::TestMorpheusNodeComplete`*

---

## ProvidersRendering

```python
class ProvidersRendering
```

Rendering for providers list.

### Things to Know

ℹ️ The `filter_applied` field indicates which filter was used: "all" (admin), "enabled" (developer), or "public" (guest). Use this to explain why some providers aren't visible.
  - *Verified in: `test_node.py::TestMorpheusNodeProviders`*

---

## MorpheusNode

```python
class MorpheusNode(BaseLogosNode)
```

AGENTESE node for Morpheus Gateway.

### Examples
```python
>>> POST /agentese/world/morpheus/complete
```
```python
>>> {"model": "claude-sonnet-4-20250514", "messages": [...]}
```
```python
>>> await logos.invoke("world.morpheus.complete", observer, model="...", messages=[...])
```
```python
>>> kg morpheus complete --model claude-sonnet-4-20250514 --message "Hello"
```

### Things to Know

ℹ️ The `morpheus_persistence` dependency is injected by the DI container. If it's not registered in providers.py, you'll get None and all aspects will return error dicts.
  - *Verified in: `test_node.py::TestMorpheusNodeHandle`*

ℹ️ Observer archetype determines affordances AND filtering. A "guest" calling "providers" gets filtered results, not an error. An error only occurs for truly forbidden aspects like "configure".
  - *Verified in: `test_node.py::TestMorpheusNodeAffordances`*

ℹ️ The stream aspect returns a dict with a generator, not raw SSE. The transport layer (HTTP/CLI) is responsible for iterating.
  - *Verified in: `test_streaming.py::TestPersistenceStreaming`*

---

## __init__

```python
def __init__(self, morpheus_persistence: MorpheusPersistence) -> None
```

Initialize MorpheusNode.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `world.morpheus.manifest`

Manifest Morpheus status to observer.

---

## services.morpheus.observability

## observability

```python
module observability
```

Morpheus Observability: OpenTelemetry spans and metrics for LLM gateway.

---

## get_morpheus_tracer

```python
def get_morpheus_tracer() -> Tracer
```

Get the morpheus tracer, creating if needed.

---

## get_morpheus_meter

```python
def get_morpheus_meter() -> metrics.Meter
```

Get the morpheus meter, creating if needed.

---

## MorpheusMetricsState

```python
class MorpheusMetricsState
```

Thread-safe in-memory metrics state for summaries.

### Things to Know

ℹ️ This is SEPARATE from OTEL counters. reset_morpheus_metrics() clears this state but OTEL counters keep incrementing.
  - *Verified in: `test_observability.py - if exists`*

ℹ️ The _lock is per-instance but the global _state is a singleton. All record_* functions share this lock—contention possible at scale.
  - *Verified in: `persistence.py record_completion calls`*

---

## record_completion

```python
def record_completion(model: str, provider: str, archetype: str, duration_s: float, tokens_in: int, tokens_out: int, success: bool, streaming: bool=False, estimated_cost_usd: float=0.0) -> None
```

Record metrics for a completed LLM request.

---

## record_rate_limit

```python
def record_rate_limit(archetype: str, model: str='unknown') -> None
```

Record a rate limit hit.

---

## record_time_to_first_token

```python
def record_time_to_first_token(model: str, provider: str, ttft_s: float) -> None
```

Record time to first token for streaming requests.

---

## MorpheusTelemetry

```python
class MorpheusTelemetry
```

Telemetry wrapper for Morpheus gateway operations.

### Things to Know

ℹ️ The context managers are async but use sync tracer.start_as_current_span. This is intentional—OTEL spans are sync, only our I/O is async.
  - *Verified in: `persistence.py::complete uses trace_completion`*

ℹ️ Duration is recorded in the finally block, so it includes error handling time. For precise LLM latency, check provider metrics.
  - *Verified in: `test_observability.py::test_tracing - if exists`*

---

## get_morpheus_metrics_summary

```python
def get_morpheus_metrics_summary() -> dict[str, Any]
```

Get a summary of current Morpheus metrics.

---

## reset_morpheus_metrics

```python
def reset_morpheus_metrics() -> None
```

Reset in-memory metrics state.

---

## trace_completion

```python
async def trace_completion(self, request: 'ChatRequest', archetype: str, provider: str='unknown', **extra_attributes: Any) -> AsyncIterator[Span]
```

Trace a completion request.

---

## trace_stream

```python
async def trace_stream(self, request: 'ChatRequest', archetype: str, provider: str='unknown', **extra_attributes: Any) -> AsyncIterator[Span]
```

Trace a streaming request.

---

## services.morpheus.persistence

## persistence

```python
module persistence
```

Morpheus Persistence: Domain semantics for LLM gateway operations.

---

## CompletionResult

```python
class CompletionResult
```

Result of a completion operation with metadata.

### Things to Know

🚨 **Critical:** The `telemetry_span_id` is only populated when telemetry is enabled. Always check for None before using for tracing correlation.
  - *Verified in: `test_node.py::TestMorpheusNodeComplete`*

ℹ️ `latency_ms` includes network and processing time, not just LLM inference. For streaming, this is total time from request to last chunk.
  - *Verified in: `test_streaming.py::TestPersistenceStreaming`*

---

## ProviderStatus

```python
class ProviderStatus
```

Status of a single provider.

### Things to Know

ℹ️ `available` is checked at query time via adapter.is_available(). This may involve network calls—cache results if calling frequently.
  - *Verified in: `test_node.py::TestMorpheusNodeProviders`*

ℹ️ `request_count` comes from the adapter's health_check(), not the gateway's counters. Adapters track their own metrics independently.
  - *Verified in: `test_node.py::test_admin_sees_all_providers`*

---

## MorpheusStatus

```python
class MorpheusStatus
```

Overall Morpheus health status.

### Things to Know

ℹ️ `healthy` is True when AT LEAST ONE provider is available. This means "degraded but functional"—not "fully healthy". Check providers_healthy vs providers_total for full picture.
  - *Verified in: `test_node.py::TestMorpheusNodeManifest`*

ℹ️ `uptime_seconds` is from MorpheusPersistence creation, not system boot. Each persistence instance tracks its own uptime.
  - *Verified in: `test_node.py::test_manifest_returns_status`*

---

## MorpheusPersistence

```python
class MorpheusPersistence
```

Domain semantics for Morpheus Gateway.

### Things to Know

ℹ️ Telemetry is ENABLED by default. Pass telemetry_enabled=False for tests to avoid OTEL overhead and side effects.
  - *Verified in: `test_streaming.py::persistence_with_streaming`*

ℹ️ This class accesses gateway._providers and gateway._route_model() which are private. This is intentional—persistence OWNS the gateway and needs internal access for telemetry tagging.
  - *Verified in: `test_node.py::TestMorpheusNodeProviders`*

🚨 **Critical:** RateLimitError is re-raised after recording metrics. The caller must handle it—it's not silently swallowed.
  - *Verified in: `test_rate_limit.py::TestPersistenceRateLimiting`*

---

## __init__

```python
def __init__(self, gateway: Optional[MorpheusGateway]=None, *, telemetry_enabled: bool=True) -> None
```

Initialize MorpheusPersistence.

---

## gateway

```python
def gateway(self) -> MorpheusGateway
```

Access the underlying gateway.

---

## manifest

```python
async def manifest(self) -> MorpheusStatus
```

**AGENTESE:** `world.morpheus.manifest`

Return Morpheus status.

---

## complete

```python
async def complete(self, request: ChatRequest, archetype: str='guest') -> CompletionResult
```

**AGENTESE:** `world.morpheus.complete`

Process a chat completion request with telemetry.

---

## stream

```python
async def stream(self, request: ChatRequest, archetype: str='guest') -> AsyncIterator[StreamChunk]
```

**AGENTESE:** `world.morpheus.stream`

Process a streaming chat completion request with telemetry.

---

## list_providers

```python
async def list_providers(self, *, enabled_only: bool=False, public_only: bool=False) -> list[ProviderStatus]
```

**AGENTESE:** `world.morpheus.providers`

List providers with optional filtering.

---

## route_info

```python
async def route_info(self, model: str) -> dict[str, Any]
```

**AGENTESE:** `world.morpheus.route`

Get routing info for a model.

---

## health

```python
async def health(self) -> dict[str, Any]
```

**AGENTESE:** `world.morpheus.health`

Get health check info.

---

## rate_limit_status

```python
def rate_limit_status(self, archetype: str) -> dict[str, Any]
```

**AGENTESE:** `world.morpheus.rate_limit`

Get rate limit status for an archetype.

---

## services.morpheus.types

## types

```python
module types
```

Morpheus Types: OpenAI-compatible request/response schemas.

---

## ChatMessage

```python
class ChatMessage
```

A single message in the conversation.

### Things to Know

ℹ️ The `name` field is ONLY for function calls, not user display names. Using it for other purposes may confuse downstream providers.
  - *Verified in: `test_streaming.py::TestMockAdapterStreaming`*

---

## ChatRequest

```python
class ChatRequest
```

OpenAI-compatible chat completion request.

### Things to Know

ℹ️ The `stream` flag is informational here—streaming is controlled by which method you call (complete vs stream), not by this flag.
  - *Verified in: `test_streaming.py::TestGatewayStreaming`*

ℹ️ The `user` field is for rate limiting correlation, not auth. Use observer archetype for access control, user for per-user limits.
  - *Verified in: `test_rate_limit.py::TestGatewayRateLimiting`*

---

## Usage

```python
class Usage
```

Token usage statistics.

### Things to Know

ℹ️ For streaming, token counts are ESTIMATES unless the provider sends a final usage summary. Don't rely on exact counts during stream.
  - *Verified in: `test_streaming.py::TestStreamChunk`*

---

## ChatChoice

```python
class ChatChoice
```

A single completion choice.

### Things to Know

🚨 **Critical:** `finish_reason="length"` means max_tokens was hit—output may be incomplete. Always check finish_reason before assuming full response.
  - *Verified in: `test_streaming.py::TestStreamChunk`*

---

## ChatResponse

```python
class ChatResponse
```

OpenAI-compatible chat completion response.

### Things to Know

ℹ️ The `id` field is generated uniquely per response. Use it for correlating logs and telemetry across the request lifecycle.
  - *Verified in: `test_streaming.py::test_to_dict_serialization`*

🚨 **Critical:** `usage` may be None for some providers or streaming. Always null-check before accessing token counts.
  - *Verified in: `test_node.py::TestMorpheusNodeComplete`*

---

## MorpheusError

```python
class MorpheusError
```

Error response following OpenAI error format.

### Things to Know

ℹ️ Error types match OpenAI: "invalid_request_error", "rate_limit_error", "authentication_error", "server_error". Use these for client compatibility.
  - *Verified in: `test_rate_limit.py::TestRateLimitError`*

---

## StreamDelta

```python
class StreamDelta
```

Delta content in a streaming chunk.

### Things to Know

ℹ️ Both `role` and `content` can be None in the same delta—this is valid for the final chunk. Check for finish_reason instead.
  - *Verified in: `test_streaming.py::test_final_creates_finish_chunk`*

---

## StreamChoice

```python
class StreamChoice
```

A single streaming choice.

### Things to Know

ℹ️ `finish_reason` is ONLY set on the final chunk. During streaming, all chunks have finish_reason=None until the last one.
  - *Verified in: `test_streaming.py::test_stream_returns_chunks`*

---

## StreamChunk

```python
class StreamChunk
```

OpenAI-compatible streaming chunk.

### Things to Know

ℹ️ All chunks in a stream share the SAME `id`. Use this to group chunks from the same completion. Don't use it for uniqueness.
  - *Verified in: `test_streaming.py::test_from_text_creates_chunk`*

ℹ️ Use to_sse() for Server-Sent Events format. The trailing \n\n is required by SSE spec—don't strip it.
  - *Verified in: `test_streaming.py::test_to_sse_format`*

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to OpenAI API format.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> 'ChatRequest'
```

Create from dict (e.g., JSON body).

---

## from_text

```python
def from_text(cls, text: str, model: str, prompt_tokens: int=0, completion_tokens: int=0) -> 'ChatResponse'
```

Create response from plain text.

---

## to_sse

```python
def to_sse(self) -> str
```

Convert to Server-Sent Events format.

---

## from_text

```python
def from_text(cls, text: str, chunk_id: str, model: str) -> 'StreamChunk'
```

Create a content chunk from plain text.

---

## final

```python
def final(cls, chunk_id: str, model: str) -> 'StreamChunk'
```

Create a final chunk with finish_reason.

---

## services.verification.__init__

## __init__

```python
module __init__
```

Verification Crown Jewel: Formal Verification Metatheory System.

---

## services.verification.aesthetic

## aesthetic

```python
module aesthetic
```

Alive Workshop Aesthetic: Sympathetic error handling with Studio Ghibli warmth.

---

## ErrorCategory

```python
class ErrorCategory(str, Enum)
```

Categories of verification errors.

---

## Severity

```python
class Severity(str, Enum)
```

Error severity levels.

---

## LivingEarthPalette

```python
class LivingEarthPalette
```

Color palette inspired by Studio Ghibli's living worlds.

---

## VerificationError

```python
class VerificationError
```

Sympathetic error with learning opportunities.

---

## celebrate_success

```python
def celebrate_success(verification_type: str) -> str
```

Get a celebration message for successful verification.

---

## ProgressiveResult

```python
class ProgressiveResult
```

Result with progressive disclosure levels.

---

## create_progressive_result

```python
def create_progressive_result(success: bool, verification_type: str, details: dict[str, Any] | None=None, error: VerificationError | None=None) -> ProgressiveResult
```

Create a progressive result from verification outcome.

---

## title

```python
def title(self) -> str
```

Get sympathetic title for this error.

---

## message

```python
def message(self) -> str
```

Get sympathetic message for this error.

---

## encouragement

```python
def encouragement(self) -> str
```

Get encouraging follow-up message.

---

## educational_content

```python
def educational_content(self) -> str | None
```

Get educational content for this error type.

---

## format_for_display

```python
def format_for_display(self, verbose: bool=False) -> str
```

Format error for human-readable display.

---

## at_level

```python
def at_level(self, level: int) -> str
```

Get result at specified disclosure level (0-3).

---

## services.verification.agentese_nodes

## agentese_nodes

```python
module agentese_nodes
```

AGENTESE Integration: Verification system nodes for the AGENTESE protocol.

---

## manifest_verification_status

```python
async def manifest_verification_status(umwelt: Umwelt) -> dict[str, Any]
```

Manifest the current state of the verification system.

---

## analyze_specification

```python
async def analyze_specification(spec_path: str, umwelt: Umwelt) -> dict[str, Any]
```

Analyze a specification for consistency and principled derivation.

---

## verify_categorical_laws

```python
async def verify_categorical_laws(morphisms: list[dict[str, Any]], law_type: str, umwelt: Umwelt) -> dict[str, Any]
```

Verify categorical laws for agent morphisms.

---

## suggest_improvements

```python
async def suggest_improvements(umwelt: Umwelt) -> dict[str, Any]
```

Generate improvement suggestions based on trace analysis.

---

## capture_execution_trace

```python
async def capture_execution_trace(agent_path: str, execution_data: dict[str, Any], umwelt: Umwelt) -> dict[str, Any]
```

Capture an execution trace as a constructive proof.

---

## analyze_trace_corpus

```python
async def analyze_trace_corpus(pattern_type: str | None, umwelt: Umwelt) -> dict[str, Any]
```

Analyze the trace corpus for behavioral patterns.

---

## visualize_derivation_graph

```python
async def visualize_derivation_graph(graph_id: str, umwelt: Umwelt) -> dict[str, Any]
```

Visualize a derivation graph showing how implementation derives from principles.

---

## explore_derivation_path

```python
async def explore_derivation_path(principle_id: str, implementation_id: str, umwelt: Umwelt) -> dict[str, Any]
```

Explore the derivation path from a principle to an implementation.

---

## services.verification.categorical_checker

## categorical_checker

```python
module categorical_checker
```

Categorical Checker: Practical categorical law verification with LLM assistance.

### Things to Know

🚨 **Critical:** Empty counter-example list returns {"strategies": [], "analysis": "No violations found"}. Always check the analysis message - an empty list is success, not an error.
  - *Verified in: `test_categorical_checker.py::TestCounterExampleGeneration::test_empty_counter_examples_handled`*

ℹ️ Functor verification may return DIFFERENT law names for different checks. Check for law_name in ["functor_laws", "functor_identity", "functor_composition"] rather than exact equality.
  - *Verified in: `test_categorical_checker.py::TestFunctorLaws::test_functor_verification_returns_result`*

---

## CategoricalChecker

```python
class CategoricalChecker
```

Practical categorical law verification with LLM assistance.

---

## verify_composition_associativity

```python
async def verify_composition_associativity(self, f: AgentMorphism, g: AgentMorphism, h: AgentMorphism) -> VerificationResult
```

Verify (f ∘ g) ∘ h ≡ f ∘ (g ∘ h) using practical testing.

---

## verify_identity_laws

```python
async def verify_identity_laws(self, f: AgentMorphism, identity: AgentMorphism) -> VerificationResult
```

Verify identity laws: f ∘ id = f and id ∘ f = f.

---

## verify_functor_laws

```python
async def verify_functor_laws(self, functor: AgentMorphism, f: AgentMorphism, g: AgentMorphism) -> VerificationResult
```

Verify functor laws: F(id) = id and F(g ∘ f) = F(g) ∘ F(f).

---

## verify_operad_coherence

```python
async def verify_operad_coherence(self, operad_operations: list[AgentMorphism], composition_rules: dict[str, Any]) -> VerificationResult
```

Verify operad coherence conditions.

---

## verify_sheaf_gluing

```python
async def verify_sheaf_gluing(self, local_sections: dict[str, Any], overlap_conditions: dict[str, Any]) -> VerificationResult
```

Verify sheaf gluing property.

---

## generate_counter_examples

```python
async def generate_counter_examples(self, law_name: str, morphisms: list[AgentMorphism], violation_hints: dict[str, Any] | None=None) -> list[CounterExample]
```

Generate concrete counter-examples for categorical law violations.

---

## suggest_remediation_strategies

```python
async def suggest_remediation_strategies(self, counter_examples: list[CounterExample], law_name: str) -> dict[str, Any]
```

Generate remediation strategies for categorical law violations.

---

## services.verification.contracts

## contracts

```python
module contracts
```

Verification Contracts: Data classes for formal verification system.

---

## VerificationStatus

```python
class VerificationStatus(str, Enum)
```

Status of verification operations.

---

## ViolationType

```python
class ViolationType(str, Enum)
```

Types of categorical law violations.

---

## ProposalStatus

```python
class ProposalStatus(str, Enum)
```

Status of improvement proposals.

---

## GraphNode

```python
class GraphNode
```

A node in the verification graph.

---

## GraphEdge

```python
class GraphEdge
```

An edge in the verification graph representing derivation.

---

## Contradiction

```python
class Contradiction
```

A contradiction detected in the verification graph.

---

## DerivationPath

```python
class DerivationPath
```

A path from principle to implementation.

---

## VerificationGraphResult

```python
class VerificationGraphResult
```

Result of verification graph analysis.

---

## AgentMorphism

```python
class AgentMorphism
```

An agent morphism for categorical verification.

---

## CounterExample

```python
class CounterExample
```

A counter-example for categorical law violation.

---

## VerificationResult

```python
class VerificationResult
```

Result of categorical law verification.

---

## SpecProperty

```python
class SpecProperty
```

A property that must hold for a specification.

---

## Specification

```python
class Specification
```

A formal specification with properties and constraints.

---

## ExecutionStep

```python
class ExecutionStep
```

A single step in agent execution.

---

## TraceWitnessResult

```python
class TraceWitnessResult
```

Result of trace witness verification.

---

## BehavioralPattern

```python
class BehavioralPattern
```

A behavioral pattern extracted from trace corpus.

---

## ImprovementProposalResult

```python
class ImprovementProposalResult
```

Result of improvement proposal generation.

---

## SemanticConsistencyResult

```python
class SemanticConsistencyResult
```

Result of semantic consistency analysis.

---

## HoTTTypeResult

```python
class HoTTTypeResult
```

Result of HoTT type representation.

---

## services.verification.generative_loop

## generative_loop

```python
module generative_loop
```

Generative Loop Engine: The closed cycle from intent to implementation and back.

### Things to Know

ℹ️ Roundtrip may LOSE nodes during compression if node count is small. The compression allows up to 50% node loss for small topologies (<=2 nodes). This is intentional - consolidation is valid compression.
  - *Verified in: `test_generative_loop.py::TestGenerativeLoopRoundTrip::test_roundtrip_preserves_node_count`*

ℹ️ Refinement increments the PATCH version, not major/minor. Version goes from 1.0.0 to 1.0.1 after refinement. This is semantic versioning for specs - refinements are backwards compatible.
  - *Verified in: `test_generative_loop.py::TestSpecRefinement::test_refine_increments_version`*

---

## AGENTESEPath

```python
class AGENTESEPath
```

An AGENTESE path extracted from mind-map.

---

## OperadSpec

```python
class OperadSpec
```

An operad specification for composition grammar.

---

## AGENTESESpec

```python
class AGENTESESpec
```

AGENTESE specification extracted from mind-map.

---

## Module

```python
class Module
```

A generated implementation module.

---

## Implementation

```python
class Implementation
```

Generated implementation from spec.

---

## SpecChange

```python
class SpecChange
```

A change in specification.

---

## SpecDiff

```python
class SpecDiff
```

Difference between original and refined spec.

---

## RoundtripResult

```python
class RoundtripResult
```

Result of generative loop roundtrip.

---

## CompressionMorphism

```python
class CompressionMorphism
```

Extracts essential decisions from mind-map topology into AGENTESE spec.

---

## ImplementationProjector

```python
class ImplementationProjector
```

Projects AGENTESE specification into implementation code.

---

## PatternSynthesizer

```python
class PatternSynthesizer
```

Synthesizes behavioral patterns from accumulated traces.

---

## SpecDiffEngine

```python
class SpecDiffEngine
```

Compares original mind-map with patterns to detect drift.

---

## GenerativeLoop

```python
class GenerativeLoop
```

The closed generative cycle orchestrator.

---

## run_generative_loop

```python
async def run_generative_loop(mind_map: MindMapTopology) -> RoundtripResult
```

Convenience function to run the generative loop.

---

## compress_to_spec

```python
async def compress_to_spec(mind_map: MindMapTopology) -> AGENTESESpec
```

Convenience function to compress mind-map to spec.

---

## compress

```python
async def compress(self, topology: MindMapTopology) -> AGENTESESpec
```

Extract AGENTESE specification from mind-map topology.

---

## project

```python
async def project(self, spec: AGENTESESpec) -> Implementation
```

Generate implementation from specification.

---

## synthesize

```python
async def synthesize(self, traces: list[TraceWitnessResult]) -> list[BehavioralPattern]
```

Extract patterns from accumulated traces.

---

## diff

```python
async def diff(self, original: MindMapTopology, patterns: list[BehavioralPattern], spec: AGENTESESpec | None=None) -> SpecDiff
```

Identify divergence between original intent and observed behavior.

---

## compress

```python
async def compress(self, mind_map: MindMapTopology) -> AGENTESESpec
```

Extract essential decisions into AGENTESE spec.

---

## project

```python
async def project(self, spec: AGENTESESpec) -> Implementation
```

Generate implementation preserving composition structure.

---

## witness

```python
async def witness(self, implementation: Implementation) -> list[TraceWitnessResult]
```

Capture traces as constructive proofs.

---

## synthesize

```python
async def synthesize(self, traces: list[TraceWitnessResult]) -> list[BehavioralPattern]
```

Extract patterns from accumulated traces.

---

## diff

```python
async def diff(self, original: MindMapTopology, patterns: list[BehavioralPattern], spec: AGENTESESpec | None=None) -> SpecDiff
```

Identify divergence and propose updates.

---

## roundtrip

```python
async def roundtrip(self, mind_map: MindMapTopology) -> RoundtripResult
```

Full generative loop roundtrip.

---

## refine_spec

```python
async def refine_spec(self, original_spec: AGENTESESpec, patterns: list[BehavioralPattern], diff: SpecDiff) -> AGENTESESpec
```

Refine specification based on observed patterns and drift.

---

## services.verification.graph_engine

## graph_engine

```python
module graph_engine
```

Graph Engine: Derivation graph construction from specifications.

### Things to Know

🚨 **Critical:** Contradictions use HEURISTIC detection, not formal logic. The engine looks for keyword pairs like "synchronous/asynchronous" or "must/must not" in descriptions. A contradiction may be a false positive if context disambiguates the usage.
  - *Verified in: `test_graph_engine.py::TestContradictionDetection::test_detect_exclusive_conflicts`*

🚨 **Critical:** Principle nodes are ALWAYS created (7 kgents principles) regardless of spec content. They are the roots of the derivation graph. Implementation nodes without paths to these principles are flagged as orphaned.
  - *Verified in: `test_graph_engine.py::TestVerificationGraphCorrectness::test_principle_nodes_created`*

---

## GraphEngine

```python
class GraphEngine
```

Engine for constructing and analyzing verification graphs.

---

## build_graph_from_specification

```python
async def build_graph_from_specification(self, spec_path: str, name: str | None=None) -> VerificationGraphResult
```

Build verification graph from specification documents.

---

## generate_resolution_strategies

```python
async def generate_resolution_strategies(self, contradictions: list[Contradiction], orphaned_nodes: list[GraphNode]) -> dict[str, list[str]]
```

Generate resolution strategies for detected issues.

---

## services.verification.hott

## hott

```python
module hott
```

Homotopy Type Theory Foundation for Formal Verification.

---

## UniverseLevel

```python
class UniverseLevel(int, Enum)
```

Universe levels in the type hierarchy.

---

## PathType

```python
class PathType(str, Enum)
```

Types of paths (equality proofs) in HoTT.

---

## HoTTType

```python
class HoTTType
```

A type in Homotopy Type Theory.

---

## HoTTPath

```python
class HoTTPath
```

A path (proof of equality) in HoTT.

---

## Isomorphism

```python
class Isomorphism
```

An isomorphism between two structures.

---

## HoTTVerificationResult

```python
class HoTTVerificationResult
```

Result of HoTT-based verification.

---

## HoTTContext

```python
class HoTTContext
```

Homotopy Type Theory context for formal verification.

---

## verify_isomorphism

```python
async def verify_isomorphism(a: Any, b: Any, context: HoTTContext | None=None) -> bool
```

Convenience function to verify isomorphism.

---

## construct_equality_path

```python
async def construct_equality_path(a: Any, b: Any, context: HoTTContext | None=None) -> HoTTPath | None
```

Convenience function to construct equality path.

---

## are_isomorphic

```python
async def are_isomorphic(self, a: Any, b: Any) -> bool
```

Check if two structures are isomorphic.

---

## construct_path

```python
async def construct_path(self, a: Any, b: Any) -> HoTTPath | None
```

Construct a path (proof of equality) between a and b.

---

## services.verification.persistence

## persistence

```python
module persistence
```

Verification Persistence: Data access layer for formal verification system.

---

## VerificationPersistence

```python
class VerificationPersistence
```

Persistence layer for the formal verification system.

---

## create_verification_graph

```python
async def create_verification_graph(self, name: str, description: str | None=None, nodes: dict[str, Any] | None=None, edges: dict[str, Any] | None=None) -> VerificationGraphResult
```

Create a new verification graph.

---

## get_verification_graph

```python
async def get_verification_graph(self, graph_id: str) -> VerificationGraphResult | None
```

Get a verification graph by ID.

---

## update_graph_analysis

```python
async def update_graph_analysis(self, graph_id: str, contradictions: list[dict[str, Any]], orphaned_nodes: list[str], derivation_paths: dict[str, Any], status: VerificationStatus) -> None
```

Update graph analysis results.

---

## create_trace_witness

```python
async def create_trace_witness(self, agent_path: str, input_data: dict[str, Any], output_data: dict[str, Any], intermediate_steps: list[dict[str, Any]] | None=None, execution_id: str | None=None, specification_id: str | None=None) -> TraceWitnessResult
```

Create a new trace witness.

---

## get_trace_witness

```python
async def get_trace_witness(self, witness_id: str) -> TraceWitnessResult | None
```

Get a trace witness by ID.

---

## update_witness_verification

```python
async def update_witness_verification(self, witness_id: str, properties_verified: list[str], violations_found: list[dict[str, Any]], status: VerificationStatus) -> None
```

Update witness verification results.

---

## get_witnesses_by_agent

```python
async def get_witnesses_by_agent(self, agent_path: str, limit: int=100) -> list[TraceWitnessResult]
```

Get trace witnesses for a specific agent path.

---

## create_categorical_violation

```python
async def create_categorical_violation(self, violation_type: ViolationType, law_description: str, counter_example: CounterExample, llm_analysis: str | None=None, suggested_fix: str | None=None) -> str
```

Create a new categorical violation record.

---

## resolve_violation

```python
async def resolve_violation(self, violation_id: str, resolution_notes: str) -> None
```

Mark a categorical violation as resolved.

---

## create_improvement_proposal

```python
async def create_improvement_proposal(self, title: str, description: str, category: str, implementation_suggestion: str, risk_assessment: str, source_patterns: list[BehavioralPattern] | None=None, kgents_principle: str | None=None) -> ImprovementProposalResult
```

Create a new improvement proposal.

---

## update_proposal_validation

```python
async def update_proposal_validation(self, proposal_id: str, categorical_compliance: bool, trace_impact_analysis: dict[str, Any], llm_validation: str, status: ProposalStatus) -> None
```

Update proposal validation results.

---

## create_specification_document

```python
async def create_specification_document(self, name: str, document_type: str, file_path: str, concepts: list[str], semantic_hash: str, version: str='1.0.0') -> str
```

Create a new specification document record.

---

## analyze_semantic_consistency

```python
async def analyze_semantic_consistency(self, document_ids: list[str]) -> SemanticConsistencyResult
```

Analyze semantic consistency across documents.

---

## create_hott_type

```python
async def create_hott_type(self, name: str, universe_level: int, type_definition: dict[str, Any], introduction_rules: list[dict[str, Any]] | None=None, elimination_rules: list[dict[str, Any]] | None=None) -> HoTTTypeResult
```

Create a new HoTT type.

---

## services.verification.reflective_tower

## reflective_tower

```python
module reflective_tower
```

Reflective Tower: Level hierarchy with consistency verification.

---

## TowerLevel

```python
class TowerLevel(IntEnum)
```

Levels in the reflective tower.

---

## LevelArtifact

```python
class LevelArtifact
```

An artifact at a specific tower level.

---

## CompressionMorphism

```python
class CompressionMorphism
```

A morphism that compresses from higher to lower level.

---

## ConsistencyResult

```python
class ConsistencyResult
```

Result of consistency verification between levels.

---

## CorrectionProposal

```python
class CorrectionProposal
```

A proposal to correct inconsistency between levels.

---

## LevelHandler

```python
class LevelHandler
```

Base class for handling artifacts at a specific level.

---

## BehavioralPatternHandler

```python
class BehavioralPatternHandler(LevelHandler)
```

Handler for Level -2: Behavioral Patterns.

---

## TraceWitnessHandler

```python
class TraceWitnessHandler(LevelHandler)
```

Handler for Level -1: Trace Witnesses.

---

## CodeHandler

```python
class CodeHandler(LevelHandler)
```

Handler for Level 0: Implementation Code.

---

## SpecHandler

```python
class SpecHandler(LevelHandler)
```

Handler for Level 1: AGENTESE Specification.

---

## MetaSpecHandler

```python
class MetaSpecHandler(LevelHandler)
```

Handler for Level 2: Category Theory Meta-Specification.

---

## FoundationsHandler

```python
class FoundationsHandler(LevelHandler)
```

Handler for Level 3: HoTT Foundations.

---

## IntentHandler

```python
class IntentHandler(LevelHandler)
```

Handler for Level ∞: Mind-Map Intent.

---

## ConsistencyVerifier

```python
class ConsistencyVerifier
```

Verifies consistency between adjacent tower levels.

---

## ReflectiveTower

```python
class ReflectiveTower
```

The reflective tower with level hierarchy and consistency verification.

---

## create_tower

```python
async def create_tower() -> ReflectiveTower
```

Create a new reflective tower.

---

## verify_tower_consistency

```python
async def verify_tower_consistency(tower: ReflectiveTower) -> dict[str, Any]
```

Verify consistency across all tower levels.

---

## add_artifact

```python
async def add_artifact(self, artifact: LevelArtifact) -> None
```

Add an artifact to this level.

---

## get_artifact

```python
async def get_artifact(self, artifact_id: str) -> LevelArtifact | None
```

Get an artifact by ID.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract structural information from an artifact.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract pattern structure.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract trace structure.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract code structure.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract spec structure.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract meta-spec structure.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract foundations structure.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract intent structure.

---

## verify_consistency

```python
async def verify_consistency(self, source_artifact: LevelArtifact, target_artifact: LevelArtifact) -> ConsistencyResult
```

Verify consistency between artifacts at adjacent levels.

---

## add_artifact

```python
async def add_artifact(self, artifact: LevelArtifact) -> None
```

Add an artifact to the appropriate level.

---

## get_artifact

```python
async def get_artifact(self, level: TowerLevel, artifact_id: str) -> LevelArtifact | None
```

Get an artifact from a specific level.

---

## verify_consistency

```python
async def verify_consistency(self, source_level: TowerLevel, target_level: TowerLevel) -> list[ConsistencyResult]
```

Verify consistency between all artifacts at two levels.

---

## verify_adjacent_levels

```python
async def verify_adjacent_levels(self, level: TowerLevel) -> list[ConsistencyResult]
```

Verify consistency with adjacent levels.

---

## propose_corrections

```python
async def propose_corrections(self, consistency_result: ConsistencyResult) -> list[CorrectionProposal]
```

Propose corrections for inconsistencies.

---

## get_tower_summary

```python
async def get_tower_summary(self) -> dict[str, Any]
```

Get a summary of the tower state.

---

## compress

```python
async def compress(self, artifact: LevelArtifact, target_level: TowerLevel) -> LevelArtifact | None
```

Compress an artifact to a lower level.

---

## services.verification.self_improvement

## self_improvement

```python
module self_improvement
```

Self-Improvement Engine: Autonomous specification evolution.

---

## ImprovementCategory

```python
class ImprovementCategory(str, Enum)
```

Categories of specification improvements.

---

## RiskLevel

```python
class RiskLevel(str, Enum)
```

Risk levels for improvement proposals.

---

## ImprovementProposal

```python
class ImprovementProposal
```

A formal proposal for specification improvement.

---

## PatternAnalyzer

```python
class PatternAnalyzer
```

Analyzes behavioral patterns to identify improvement opportunities.

---

## ProposalGenerator

```python
class ProposalGenerator
```

Generates formal improvement proposals from identified opportunities.

---

## CategoricalComplianceVerifier

```python
class CategoricalComplianceVerifier
```

Verifies that improvement proposals maintain categorical compliance.

---

## SelfImprovementEngine

```python
class SelfImprovementEngine
```

The self-improvement engine that orchestrates specification evolution.

---

## analyze_patterns_for_improvements

```python
async def analyze_patterns_for_improvements(patterns: list[BehavioralPattern]) -> list[ImprovementProposalResult]
```

Convenience function to analyze patterns and get improvement proposals.

---

## run_self_improvement

```python
async def run_self_improvement(patterns: list[BehavioralPattern], auto_apply: bool=False) -> dict[str, Any]
```

Convenience function to run self-improvement cycle.

---

## to_result

```python
def to_result(self) -> ImprovementProposalResult
```

Convert to immutable result.

---

## identify_improvement_opportunities

```python
async def identify_improvement_opportunities(self, patterns: list[BehavioralPattern], traces: list[TraceWitnessResult] | None=None) -> list[dict[str, Any]]
```

Identify improvement opportunities from patterns.

---

## align_with_principle

```python
def align_with_principle(self, opportunity: dict[str, Any]) -> str | None
```

Determine which kgents principle an opportunity aligns with.

---

## generate_proposal

```python
async def generate_proposal(self, opportunity: dict[str, Any]) -> ImprovementProposal
```

Generate a formal improvement proposal from an opportunity.

---

## verify_compliance

```python
async def verify_compliance(self, proposal: ImprovementProposal) -> tuple[bool, str]
```

Verify that a proposal maintains categorical compliance.

---

## analyze_and_propose

```python
async def analyze_and_propose(self, patterns: list[BehavioralPattern], traces: list[TraceWitnessResult] | None=None) -> list[ImprovementProposal]
```

Analyze patterns and generate improvement proposals.

---

## validate_proposal

```python
async def validate_proposal(self, proposal_id: str) -> tuple[bool, str]
```

Validate a specific proposal for application.

---

## apply_proposal

```python
async def apply_proposal(self, proposal_id: str, dry_run: bool=True) -> dict[str, Any]
```

Apply a validated proposal.

---

## reject_proposal

```python
async def reject_proposal(self, proposal_id: str, reason: str) -> bool
```

Reject a proposal with reason.

---

## get_proposal_summary

```python
async def get_proposal_summary(self) -> dict[str, Any]
```

Get summary of all proposals.

---

## run_improvement_cycle

```python
async def run_improvement_cycle(self, patterns: list[BehavioralPattern], auto_apply_low_risk: bool=False) -> dict[str, Any]
```

Run a complete improvement cycle.

---

## services.verification.semantic_consistency

## semantic_consistency

```python
module semantic_consistency
```

Semantic Consistency Engine: Cross-document consistency verification.

---

## SemanticConsistencyEngine

```python
class SemanticConsistencyEngine
```

Engine for verifying semantic consistency across specification documents.

---

## verify_cross_document_consistency

```python
async def verify_cross_document_consistency(self, document_paths: list[str], base_concepts: dict[str, Any] | None=None) -> SemanticConsistencyResult
```

Verify semantic consistency across multiple specification documents.

---

## services.verification.service

## service

```python
module service
```

Verification Service: Core business logic for formal verification system.

---

## VerificationService

```python
class VerificationService
```

Core verification service implementing formal verification operations.

---

## get_status

```python
async def get_status(self) -> dict[str, Any]
```

Get current verification system status.

---

## analyze_specification

```python
async def analyze_specification(self, spec_path: str) -> VerificationGraphResult
```

Analyze a specification for consistency and improvements.

---

## verify_composition_associativity

```python
async def verify_composition_associativity(self, f: AgentMorphism, g: AgentMorphism, h: AgentMorphism) -> VerificationResult
```

Verify composition associativity: (f ∘ g) ∘ h ≡ f ∘ (g ∘ h).

---

## verify_identity_laws

```python
async def verify_identity_laws(self, f: AgentMorphism, identity: AgentMorphism) -> VerificationResult
```

Verify identity laws: f ∘ id = f and id ∘ f = f.

---

## capture_trace_witness

```python
async def capture_trace_witness(self, agent_path: str, execution_data: dict[str, Any]) -> TraceWitnessResult
```

Capture a trace witness as constructive proof of behavior.

---

## generate_improvements

```python
async def generate_improvements(self) -> list[ImprovementProposalResult]
```

Generate improvement suggestions based on trace analysis.

---

## verify_semantic_consistency

```python
async def verify_semantic_consistency(self, document_paths: list[str]) -> SemanticConsistencyResult
```

Verify semantic consistency across specification documents.

---

## create_agent_hott_type

```python
async def create_agent_hott_type(self, agent_name: str, type_definition: dict[str, Any], universe_level: int=0) -> HoTTTypeResult
```

Create HoTT type representation for an agent.

---

## verify_functor_laws

```python
async def verify_functor_laws(self, functor: AgentMorphism, f: AgentMorphism, g: AgentMorphism) -> VerificationResult
```

Verify functor laws: F(id) = id and F(g ∘ f) = F(g) ∘ F(f).

---

## verify_operad_coherence

```python
async def verify_operad_coherence(self, operad_operations: list[AgentMorphism], composition_rules: dict[str, Any]) -> VerificationResult
```

Verify operad coherence conditions for multi-input compositions.

---

## verify_sheaf_gluing

```python
async def verify_sheaf_gluing(self, local_sections: dict[str, Any], overlap_conditions: dict[str, Any]) -> VerificationResult
```

Verify sheaf gluing property for local-to-global coherence.

---

## generate_counter_examples

```python
async def generate_counter_examples(self, law_name: str, morphisms: list[AgentMorphism], violation_hints: dict[str, Any] | None=None) -> list[CounterExample]
```

Generate concrete counter-examples for categorical law violations.

---

## suggest_remediation_strategies

```python
async def suggest_remediation_strategies(self, counter_examples: list[CounterExample], law_name: str) -> dict[str, Any]
```

Generate remediation strategies for categorical law violations.

---

## analyze_behavioral_patterns

```python
async def analyze_behavioral_patterns(self, pattern_type: str | None=None) -> dict[str, Any]
```

Analyze behavioral patterns in the trace corpus.

---

## get_trace_corpus_summary

```python
async def get_trace_corpus_summary(self) -> dict[str, Any]
```

Get summary statistics of the trace corpus.

---

## find_similar_traces

```python
async def find_similar_traces(self, reference_trace_id: str, similarity_threshold: float=0.7) -> list[TraceWitnessResult]
```

Find traces similar to a reference trace.

---

## services.verification.test_verification_integration

## test_verification_integration

```python
module test_verification_integration
```

Integration test for the formal verification system.

---

## TestVerificationIntegration

```python
class TestVerificationIntegration
```

Integration tests for the verification system.

---

## sample_morphisms

```python
def sample_morphisms(self)
```

Create sample morphisms for testing.

---

## sample_specification

```python
def sample_specification(self)
```

Create a sample specification for testing.

---

## test_graph_engine_integration

```python
async def test_graph_engine_integration(self, sample_specification)
```

Test graph engine with real specification.

---

## test_categorical_checker_integration

```python
async def test_categorical_checker_integration(self, sample_morphisms)
```

Test categorical checker with sample morphisms.

---

## test_counter_example_generation

```python
async def test_counter_example_generation(self, sample_morphisms)
```

Test counter-example generation.

---

## test_trace_witness_integration

```python
async def test_trace_witness_integration(self)
```

Test trace witness system.

---

## test_semantic_consistency_integration

```python
async def test_semantic_consistency_integration(self, sample_specification)
```

Test semantic consistency engine.

---

## test_remediation_strategies

```python
async def test_remediation_strategies(self, sample_morphisms)
```

Test remediation strategy generation.

---

## test_end_to_end_workflow

```python
async def test_end_to_end_workflow(self, sample_specification, sample_morphisms)
```

Test complete end-to-end verification workflow.

---

## services.verification.topology

## topology

```python
module topology
```

Mind-Map Topology Engine: Treating mind-maps as formal topological spaces.

---

## MappingType

```python
class MappingType(str, Enum)
```

Types of continuous maps between open sets.

---

## TopologicalNode

```python
class TopologicalNode
```

A node as an open set in the topology.

---

## ContinuousMap

```python
class ContinuousMap
```

An edge as a continuous map between open sets.

---

## Cover

```python
class Cover
```

A cover of the topological space.

---

## LocalSection

```python
class LocalSection
```

A local section of a sheaf over an open set.

---

## SheafVerification

```python
class SheafVerification
```

Result of sheaf condition verification.

---

## CoherenceConflict

```python
class CoherenceConflict
```

A conflict where the sheaf condition fails.

---

## RepairSuggestion

```python
class RepairSuggestion
```

A suggested repair for a coherence conflict.

---

## MindMapTopology

```python
class MindMapTopology
```

Mind-map as a topological space with sheaf structure.

---

## ObsidianImporter

```python
class ObsidianImporter
```

Import mind-maps from Obsidian markdown format.

---

## import_from_obsidian

```python
def import_from_obsidian(vault_path: str | Path) -> MindMapTopology
```

Convenience function to import from Obsidian.

---

## TopologyVisualization

```python
class TopologyVisualization
```

Data for visualizing the topology.

---

## create_visualization_data

```python
def create_visualization_data(topology: MindMapTopology) -> TopologyVisualization
```

Create visualization data from topology.

---

## with_neighbor

```python
def with_neighbor(self, neighbor_id: str) -> TopologicalNode
```

Return new node with additional neighbor.

---

## overlaps_with

```python
def overlaps_with(self, other: Cover) -> frozenset[str]
```

Return the overlap (intersection) with another cover.

---

## add_node

```python
def add_node(self, node: TopologicalNode) -> None
```

Add a node to the topology.

---

## add_edge

```python
def add_edge(self, edge: ContinuousMap) -> None
```

Add an edge and update neighborhoods.

---

## add_cover

```python
def add_cover(self, cover: Cover) -> None
```

Add a cover (cluster) to the topology.

---

## add_local_section

```python
def add_local_section(self, section: LocalSection) -> None
```

Add a local section for sheaf structure.

---

## get_neighborhood

```python
def get_neighborhood(self, node_id: str) -> frozenset[str]
```

Get the neighborhood of a node.

---

## get_connected_component

```python
def get_connected_component(self, start_id: str) -> frozenset[str]
```

Get the connected component containing a node.

---

## is_connected

```python
def is_connected(self) -> bool
```

Check if the topology is connected.

---

## get_boundary

```python
def get_boundary(self, region: frozenset[str]) -> frozenset[str]
```

Get the boundary of a region (nodes with neighbors outside).

---

## verify_sheaf_condition

```python
def verify_sheaf_condition(self) -> SheafVerification
```

Verify the sheaf gluing condition.

---

## identify_conflicts

```python
def identify_conflicts(self) -> list[CoherenceConflict]
```

Identify all coherence conflicts in the topology.

---

## suggest_repairs

```python
def suggest_repairs(self, conflict: CoherenceConflict) -> list[RepairSuggestion]
```

Suggest repairs for a coherence conflict.

---

## import_vault

```python
def import_vault(self, vault_path: Path) -> MindMapTopology
```

Import an Obsidian vault as a topology.

---

## services.verification.trace_witness

## trace_witness

```python
module trace_witness
```

Enhanced Trace Witness: Specification compliance verification with constructive proofs.

---

## EnhancedTraceWitness

```python
class EnhancedTraceWitness
```

Enhanced trace witness system for specification compliance verification.

---

## capture_execution_trace

```python
async def capture_execution_trace(self, agent_path: str, input_data: dict[str, Any], specification_id: str | None=None) -> TraceWitnessResult
```

Capture execution trace for an agent operation.

---

## analyze_behavioral_patterns

```python
async def analyze_behavioral_patterns(self, pattern_type: str | None=None) -> dict[str, Any]
```

Analyze behavioral patterns in the trace corpus.

---

## get_trace_corpus_summary

```python
async def get_trace_corpus_summary(self) -> dict[str, Any]
```

Get summary statistics of the trace corpus.

---

## find_similar_traces

```python
async def find_similar_traces(self, reference_trace_id: str, similarity_threshold: float=0.7) -> list[TraceWitnessResult]
```

Find traces similar to a reference trace.

---

## services.witness.__init__

## __init__

```python
module __init__
```

Witness Crown Jewel: The 8th Jewel That Watches, Learns, and Acts.

---

## services.witness.audit

## audit

```python
module audit
```

Witness Audit Trail: Automatic Action Recording for Cross-Jewel Operations.

---

## AuditEntry

```python
class AuditEntry
```

A single entry in the audit trail.

---

## AuditCallback

```python
class AuditCallback(Protocol)
```

Protocol for audit callbacks.

---

## AuditingInvoker

```python
class AuditingInvoker
```

JewelInvoker wrapper that automatically records actions to persistence.

---

## AuditingPipelineRunner

```python
class AuditingPipelineRunner
```

PipelineRunner wrapper that audits the entire pipeline execution.

---

## create_auditing_invoker

```python
def create_auditing_invoker(invoker: JewelInvoker, persistence: 'WitnessPersistence | None'=None, record_reads: bool=False) -> AuditingInvoker
```

Create an auditing invoker wrapper.

---

## create_auditing_runner

```python
def create_auditing_runner(invoker: 'AuditingInvoker | JewelInvoker', observer: 'Observer', persistence: 'WitnessPersistence | None'=None, record_steps: bool=False) -> AuditingPipelineRunner
```

Create an auditing pipeline runner.

---

## to_action_result

```python
def to_action_result(self) -> ActionResult
```

Convert to ActionResult for persistence.

---

## __call__

```python
async def __call__(self, entry: AuditEntry) -> None
```

Called when an action is recorded.

---

## invoke

```python
async def invoke(self, path: str, observer: 'Observer', **kwargs: Any) -> InvocationResult
```

Invoke an AGENTESE path with automatic auditing.

---

## invoke_read

```python
async def invoke_read(self, path: str, observer: 'Observer', **kwargs: Any) -> InvocationResult
```

Convenience for read-only invocations.

---

## invoke_mutation

```python
async def invoke_mutation(self, path: str, observer: 'Observer', reversible: bool=True, inverse_action: str | None=None, **kwargs: Any) -> InvocationResult
```

Invoke a mutation with explicit rollback info.

---

## add_callback

```python
def add_callback(self, callback: AuditCallback) -> None
```

Add an audit callback.

---

## get_log

```python
def get_log(self, mutations_only: bool=True, limit: int=100) -> list[AuditEntry]
```

Get recent audit entries.

---

## trust_level

```python
def trust_level(self) -> TrustLevel
```

Expose inner invoker's trust level.

---

## run

```python
async def run(self, pipeline: Pipeline, initial_kwargs: dict[str, Any] | None=None, name: str='') -> PipelineResult
```

Execute a pipeline with automatic auditing.

---

## services.witness.bus

## bus

```python
module bus
```

Witness Bus Architecture: Event-Driven Cross-Jewel Communication.

---

## WitnessTopics

```python
class WitnessTopics
```

Topic namespace for witness events.

---

## WitnessSynergyBus

```python
class WitnessSynergyBus
```

Cross-jewel pub/sub bus with wildcard support.

---

## WitnessEventBus

```python
class WitnessEventBus
```

EventBus for UI fan-out.

---

## wire_synergy_to_event

```python
def wire_synergy_to_event(synergy_bus: WitnessSynergyBus, event_bus: WitnessEventBus, topics: list[str] | None=None) -> list[UnsubscribeFunc]
```

Wire SynergyBus topics to EventBus fan-out.

---

## wire_witness_to_global_synergy

```python
def wire_witness_to_global_synergy(witness_bus: WitnessSynergyBus) -> list[UnsubscribeFunc]
```

Bridge Witness events to the global SynergyBus.

---

## register_witness_handlers

```python
def register_witness_handlers() -> list[UnsubscribeFunc]
```

Register Witness handlers with the global SynergyBus.

---

## WitnessBusManager

```python
class WitnessBusManager
```

Manages the two-bus architecture for Witness.

---

## get_witness_bus_manager

```python
def get_witness_bus_manager() -> WitnessBusManager
```

Get the global WitnessBusManager instance.

---

## reset_witness_bus_manager

```python
def reset_witness_bus_manager() -> None
```

Reset the global WitnessBusManager (for testing).

---

## get_synergy_bus

```python
def get_synergy_bus() -> WitnessSynergyBus
```

Get the global WitnessSynergyBus.

---

## publish

```python
async def publish(self, topic: str, event: Any) -> None
```

Publish an event to a topic.

---

## subscribe

```python
def subscribe(self, topic: str, handler: SynergyHandler) -> UnsubscribeFunc
```

Subscribe to a topic.

---

## stats

```python
def stats(self) -> dict[str, int]
```

Get bus statistics.

---

## clear

```python
def clear(self) -> None
```

Clear all handlers (for testing).

---

## publish

```python
async def publish(self, event: Any) -> None
```

Publish event to all subscribers.

---

## subscribe

```python
def subscribe(self, handler: WitnessEventHandler) -> UnsubscribeFunc
```

Subscribe to all events.

---

## stats

```python
def stats(self) -> dict[str, int]
```

Get bus statistics.

---

## clear

```python
def clear(self) -> None
```

Clear all subscribers (for testing).

---

## bridge_thought

```python
async def bridge_thought(topic: str, event: Any) -> None
```

Bridge thought events to global synergy.

---

## bridge_git_commit

```python
async def bridge_git_commit(topic: str, event: Any) -> None
```

Bridge git commit events to global synergy.

---

## bridge_daemon_started

```python
async def bridge_daemon_started(topic: str, event: Any) -> None
```

Bridge daemon started events to global synergy.

---

## bridge_daemon_stopped

```python
async def bridge_daemon_stopped(topic: str, event: Any) -> None
```

Bridge daemon stopped events to global synergy.

---

## wire_all

```python
def wire_all(self) -> None
```

Wire all buses together.

---

## wire_cross_jewel_handlers

```python
def wire_cross_jewel_handlers(self) -> None
```

Wire cross-jewel event handlers.

---

## unwire_all

```python
def unwire_all(self) -> None
```

Disconnect all wiring.

---

## clear

```python
def clear(self) -> None
```

Clear all buses and wiring (for testing).

---

## stats

```python
def stats(self) -> dict[str, dict[str, int]]
```

Get combined statistics.

---

## services.witness.cli

## cli

```python
module cli
```

kgentsd: The Witness Daemon CLI.

---

## cmd_summon

```python
def cmd_summon(args: list[str]) -> int
```

Summon the Witness daemon (foreground mode with TUI).

---

## cmd_release

```python
def cmd_release(args: list[str]) -> int
```

Release the Witness daemon gracefully.

---

## cmd_status

```python
def cmd_status(args: list[str]) -> int
```

Show current Witness daemon status.

---

## cmd_thoughts

```python
def cmd_thoughts(args: list[str]) -> int
```

View recent thought stream.

---

## cmd_ask

```python
def cmd_ask(args: list[str]) -> int
```

Ask the Witness a direct question.

---

## main

```python
def main(argv: list[str] | None=None) -> int
```

Main entry point for kgentsd CLI.

---

## services.witness.contracts

## contracts

```python
module contracts
```

Witness AGENTESE Contracts: Type-safe request/response definitions.

---

## WitnessManifestResponse

```python
class WitnessManifestResponse
```

Response for manifest aspect.

---

## ThoughtsRequest

```python
class ThoughtsRequest
```

Request for thoughts aspect.

---

## ThoughtItem

```python
class ThoughtItem
```

A single thought in the response.

---

## ThoughtsResponse

```python
class ThoughtsResponse
```

Response for thoughts aspect.

---

## TrustRequest

```python
class TrustRequest
```

Request for trust aspect.

---

## TrustResponse

```python
class TrustResponse
```

Response for trust aspect.

---

## CaptureThoughtRequest

```python
class CaptureThoughtRequest
```

Request for capture aspect.

---

## CaptureThoughtResponse

```python
class CaptureThoughtResponse
```

Response for capture aspect.

---

## ActionRecordRequest

```python
class ActionRecordRequest
```

Request for action aspect.

---

## ActionRecordResponse

```python
class ActionRecordResponse
```

Response for action aspect.

---

## RollbackWindowRequest

```python
class RollbackWindowRequest
```

Request for rollback aspect.

---

## RollbackActionItem

```python
class RollbackActionItem
```

A single action in the rollback response.

---

## RollbackWindowResponse

```python
class RollbackWindowResponse
```

Response for rollback aspect.

---

## EscalateRequest

```python
class EscalateRequest
```

Request for escalate aspect.

---

## EscalateResponse

```python
class EscalateResponse
```

Response for escalate aspect.

---

## InvokeRequest

```python
class InvokeRequest
```

Request for invoke aspect (cross-jewel invocation).

---

## InvokeResponse

```python
class InvokeResponse
```

Response for invoke aspect.

---

## PipelineStepItem

```python
class PipelineStepItem
```

A single step definition in a pipeline request.

---

## PipelineRequest

```python
class PipelineRequest
```

Request for pipeline aspect (cross-jewel pipeline).

---

## PipelineStepResultItem

```python
class PipelineStepResultItem
```

Result of a single step in pipeline execution.

---

## PipelineResponse

```python
class PipelineResponse
```

Response for pipeline aspect.

---

## CrystallizeRequest

```python
class CrystallizeRequest
```

Request for crystallize aspect - trigger experience crystallization.

---

## CrystalItem

```python
class CrystalItem
```

A crystal summary for list responses.

---

## CrystallizeResponse

```python
class CrystallizeResponse
```

Response for crystallize aspect.

---

## TimelineRequest

```python
class TimelineRequest
```

Request for timeline aspect - get crystallization timeline.

---

## TimelineResponse

```python
class TimelineResponse
```

Response for timeline aspect.

---

## CrystalQueryRequest

```python
class CrystalQueryRequest
```

Request for crystal aspect - retrieve specific crystal.

---

## CrystalQueryResponse

```python
class CrystalQueryResponse
```

Response for crystal aspect - full crystal detail.

---

## TerritoryRequest

```python
class TerritoryRequest
```

Request for territory aspect - codebase heat map.

---

## TerritoryResponse

```python
class TerritoryResponse
```

Response for territory aspect - codebase activity map.

---

## AttuneRequest

```python
class AttuneRequest
```

Request for attune aspect - start observation session.

---

## AttuneResponse

```python
class AttuneResponse
```

Response for attune aspect.

---

## MarkRequest

```python
class MarkRequest
```

Request for mark aspect - create user marker.

---

## MarkResponse

```python
class MarkResponse
```

Response for mark aspect.

---

## ScheduleRequest

```python
class ScheduleRequest
```

Request for schedule aspect (scheduling future invocations).

---

## SchedulePeriodicRequest

```python
class SchedulePeriodicRequest
```

Request for scheduling periodic invocations.

---

## ScheduleResponse

```python
class ScheduleResponse
```

Response for schedule aspect.

---

## ScheduleListRequest

```python
class ScheduleListRequest
```

Request for listing scheduled tasks.

---

## ScheduleListResponse

```python
class ScheduleListResponse
```

Response for listing scheduled tasks.

---

## ScheduleCancelRequest

```python
class ScheduleCancelRequest
```

Request for cancelling a scheduled task.

---

## ScheduleCancelResponse

```python
class ScheduleCancelResponse
```

Response for cancelling a scheduled task.

---

## services.witness.crystal

## crystal

```python
module crystal
```

ExperienceCrystal: The Atomic Unit of Witnessed Experience.

---

## MoodVector

```python
class MoodVector
```

Seven-dimensional affective signature of a work session.

### Examples
```python
>>> mood = MoodVector.from_thoughts(thoughts)
```
```python
>>> mood.brightness  # 0.8 if lots of success markers
```
```python
>>> mood.similarity(other_mood)  # Cosine similarity
```

---

## TopologySnapshot

```python
class TopologySnapshot
```

Snapshot of codebase topology at crystallization time.

---

## Narrative

```python
class Narrative
```

Synthesized narrative from a work session.

---

## ExperienceCrystal

```python
class ExperienceCrystal
```

The atomic unit of The Witness's memory.

### Examples
```python
>>> crystal = ExperienceCrystal.from_thoughts(thoughts, session_id="abc")
```
```python
>>> crystal.mood.brightness  # Was it a good session?
```
```python
>>> crystal.topics  # What was worked on?
```
```python
>>> crystal.as_memory()  # Project to D-gent for storage
```

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate all dimensions are in [0, 1].

---

## neutral

```python
def neutral(cls) -> MoodVector
```

Return a neutral mood (all 0.5).

---

## from_thoughts

```python
def from_thoughts(cls, thoughts: list[Thought]) -> MoodVector
```

Derive mood from a thought stream.

---

## similarity

```python
def similarity(self, other: MoodVector) -> float
```

Cosine similarity to another mood vector.

---

## to_dict

```python
def to_dict(self) -> dict[str, float]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, float]) -> MoodVector
```

Create from dictionary.

---

## dominant_quality

```python
def dominant_quality(self) -> str
```

Return the most prominent quality.

---

## from_thoughts

```python
def from_thoughts(cls, thoughts: list[Thought]) -> TopologySnapshot
```

Derive topology from thought stream.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> TopologySnapshot
```

Create from dictionary.

---

## template_fallback

```python
def template_fallback(cls, thoughts: list[Thought]) -> Narrative
```

Template fallback when LLM unavailable.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Narrative
```

Create from dictionary.

---

## from_thoughts

```python
def from_thoughts(cls, thoughts: list[Thought], session_id: str='', markers: list[str] | None=None, narrative: Narrative | None=None) -> ExperienceCrystal
```

Create crystal from thought stream.

---

## as_memory

```python
def as_memory(self) -> dict[str, Any]
```

Project into D-gent-compatible format for long-term storage.

---

## to_json

```python
def to_json(self) -> dict[str, Any]
```

Convert to JSON-serializable dictionary.

---

## from_json

```python
def from_json(cls, data: dict[str, Any]) -> ExperienceCrystal
```

Create from JSON dictionary.

---

## duration_minutes

```python
def duration_minutes(self) -> float | None
```

Duration of the crystallized session in minutes.

---

## thought_count

```python
def thought_count(self) -> int
```

Number of thoughts in this crystal.

---

## services.witness.crystallization_node

## crystallization_node

```python
module crystallization_node
```

Time Witness AGENTESE Node: @node("time.witness")

---

## TimeWitnessManifestResponse

```python
class TimeWitnessManifestResponse
```

Manifest response for time.witness.

---

## TimeWitnessManifestRendering

```python
class TimeWitnessManifestRendering
```

Rendering for time.witness manifest.

---

## TimeWitnessNode

```python
class TimeWitnessNode(BaseLogosNode)
```

AGENTESE node for experience crystallization (time.witness context).

---

## __init__

```python
def __init__(self, witness_persistence: WitnessPersistence) -> None
```

Initialize TimeWitnessNode.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `time.witness.manifest`

Manifest crystallization status to observer.

---

## observe

```python
def observe(self, observation: LocalObservation) -> None
```

Add an observation from a watcher.

---

## get_crystals

```python
def get_crystals(self) -> list[ExperienceCrystal]
```

Get all crystals (for Muse integration).

---

## services.witness.daemon

## daemon

```python
module daemon
```

**AGENTESE:** `Cross`

Witness Daemon: Background Process for Continuous Observation.

---

## DaemonConfig

```python
class DaemonConfig
```

Configuration for the witness daemon.

---

## read_pid_file

```python
def read_pid_file(pid_file: Path) -> int | None
```

Read PID from file, return None if not exists or invalid.

---

## write_pid_file

```python
def write_pid_file(pid_file: Path, pid: int) -> None
```

Write PID to file.

---

## remove_pid_file

```python
def remove_pid_file(pid_file: Path) -> None
```

Remove PID file if it exists.

---

## is_process_running

```python
def is_process_running(pid: int) -> bool
```

Check if a process with given PID is running.

---

## check_daemon_status

```python
def check_daemon_status(config: DaemonConfig | None=None) -> tuple[bool, int | None]
```

Check if the daemon is running.

---

## create_watcher

```python
def create_watcher(watcher_type: str, config: DaemonConfig) -> BaseWatcher[Any] | None
```

Create a watcher instance by type.

---

## event_to_thought

```python
def event_to_thought(event: Any) -> Any
```

Convert any watcher event to a Thought.

---

## WitnessDaemon

```python
class WitnessDaemon
```

Background daemon for witness observation.

---

## start_daemon

```python
def start_daemon(config: DaemonConfig | None=None) -> int
```

Start the witness daemon in a background process.

---

## stop_daemon

```python
def stop_daemon(config: DaemonConfig | None=None) -> bool
```

Stop the witness daemon.

---

## get_daemon_status

```python
def get_daemon_status(config: DaemonConfig | None=None) -> dict[str, Any]
```

Get daemon status information.

---

## main

```python
async def main() -> None
```

Main entry point for daemon process.

---

## validate

```python
def validate(self) -> list[str]
```

Validate configuration, return list of errors.

---

## start

```python
async def start(self) -> None
```

Start the daemon and begin watching.

---

## trust_level

```python
def trust_level(self) -> Any
```

Get current trust level from persistence.

---

## trust_status

```python
def trust_status(self) -> dict[str, Any]
```

Get current trust status for display.

---

## set_suggestion_callback

```python
def set_suggestion_callback(self, callback: Any) -> None
```

Register a callback for new suggestions.

---

## is_running

```python
def is_running(self) -> bool
```

Check if daemon is running.

---

## services.witness.grant

## grant

```python
module grant
```

Grant: Negotiated Permission Contract.

### Things to Know

ℹ️ Grant status lifecycle is DIRECTIONAL. EXPIRED is terminal unless explicitly renewed. REVOKED can be re-granted, but EXPIRED cannot. Check is_active property rather than status == GRANTED for safety.
  - *Verified in: `test_ritual.py::test_grant_revocation_invalidates_ritual`*

🚨 **Critical:** GateFallback.DENY is the SAFE DEFAULT for timeout. If a ReviewGate times out, the fallback determines behavior. DENY blocks, ALLOW_LIMITED reduces scope, ESCALATE delegates. Always set explicit fallback.
  - *Verified in: `test_covenant.py::test_covenant_gate_fallback`*

---

## generate_grant_id

```python
def generate_grant_id() -> GrantId
```

Generate a unique Grant ID.

---

## GrantStatus

```python
class GrantStatus(Enum)
```

Status of a Grant.

---

## GateFallback

```python
class GateFallback(Enum)
```

What to do when a ReviewGate times out.

---

## ReviewGate

```python
class ReviewGate
```

Checkpoint requiring human review.

### Examples
```python
>>> gate = ReviewGate(
```
```python
>>> # After 5 file writes, human review is triggered
```

---

## GateOccurrence

```python
class GateOccurrence
```

Tracks occurrences of a gated operation.

---

## GrantError

```python
class GrantError(Exception)
```

Base exception for Grant errors.

---

## GrantNotGranted

```python
class GrantNotGranted(GrantError)
```

Law 1: Attempted operation without granted Grant.

---

## GrantRevoked

```python
class GrantRevoked(GrantError)
```

Law 2: Grant has been revoked.

---

## GateTriggered

```python
class GateTriggered(GrantError)
```

Law 3: Review gate threshold reached.

---

## Grant

```python
class Grant
```

Negotiated permission contract.

### Examples
```python
>>> grant = Grant.propose(
```
```python
>>> # Human reviews and grants
```
```python
>>> granted = grant.grant(granted_by="kent")
```

---

## GrantEnforcer

```python
class GrantEnforcer
```

Runtime enforcer for Grant permissions and gates.

### Examples
```python
>>> enforcer = GrantEnforcer(grant)
```
```python
>>> enforcer.check("file_read")  # OK
```
```python
>>> enforcer.check("git_push")   # Might trigger gate
```

---

## GrantStore

```python
class GrantStore
```

Persistent storage for Grants.

---

## get_grant_store

```python
def get_grant_store() -> GrantStore
```

Get the global grant store.

---

## reset_grant_store

```python
def reset_grant_store() -> None
```

Reset the global grant store (for testing).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> ReviewGate
```

Create from dictionary.

---

## record

```python
def record(self) -> bool
```

Record an occurrence. Returns True if gate threshold reached.

---

## reset

```python
def reset(self) -> None
```

Reset counter (called after review).

---

## propose

```python
def propose(cls, permissions: frozenset[str] | tuple[str, ...] | list[str], review_gates: tuple[ReviewGate, ...] | None=None, reason: str='', expires_at: datetime | None=None, description: str='') -> Grant
```

Propose a new Grant.

---

## negotiate

```python
def negotiate(self) -> Grant
```

Move to NEGOTIATING status.

---

## grant

```python
def grant(self, granted_by: str) -> Grant
```

Grant the Grant.

---

## revoke

```python
def revoke(self, revoked_by: str, reason: str='') -> Grant
```

Revoke the Grant.

---

## amend

```python
def amend(self, permissions: frozenset[str] | None=None, review_gates: tuple[ReviewGate, ...] | None=None) -> Grant
```

Amend the Grant with new terms.

---

## is_active

```python
def is_active(self) -> bool
```

Check if Grant is active and usable.

---

## check_active

```python
def check_active(self) -> None
```

Raise if Grant is not active.

---

## has_permission

```python
def has_permission(self, permission: str) -> bool
```

Check if a permission is granted.

---

## check_permission

```python
def check_permission(self, permission: str) -> None
```

Check permission, raising if not granted or Grant inactive.

---

## get_gate

```python
def get_gate(self, trigger: str) -> ReviewGate | None
```

Get the review gate for a trigger, if any.

---

## trust_level

```python
def trust_level(self) -> str
```

Backwards compat: derive from status.

---

## proposed_at

```python
def proposed_at(self) -> datetime
```

Backwards compat: alias for created_at.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Grant
```

Create from dictionary.

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize gate occurrences.

---

## check

```python
def check(self, operation: str) -> None
```

Check if operation is permitted.

---

## approve_gate

```python
def approve_gate(self, trigger: str) -> None
```

Approve a pending gate review, resetting the counter.

---

## is_gate_pending

```python
def is_gate_pending(self, trigger: str) -> bool
```

Check if a gate has a pending review.

---

## add

```python
def add(self, grant: Grant) -> None
```

Add a Grant to the store.

---

## get

```python
def get(self, grant_id: GrantId) -> Grant | None
```

Get a Grant by ID.

---

## update

```python
def update(self, grant: Grant) -> None
```

Update a Grant (replace with new version).

---

## active

```python
def active(self) -> list[Grant]
```

Get all active Grants.

---

## pending

```python
def pending(self) -> list[Grant]
```

Get Grants awaiting approval.

---

## revoked

```python
def revoked(self) -> list[Grant]
```

Get revoked Grants.

---

## services.witness.intent

## intent

```python
module intent
```

IntentTree: Typed Task Decomposition with Dependencies.

---

## generate_intent_id

```python
def generate_intent_id() -> IntentId
```

Generate a unique Intent ID.

---

## IntentType

```python
class IntentType(Enum)
```

Typed intent categories.

---

## IntentStatus

```python
class IntentStatus(Enum)
```

Status of an Intent.

---

## Intent

```python
class Intent
```

Typed goal node in the intent graph.

### Examples
```python
>>> root = Intent.create(
```
```python
>>> child = Intent.create(
```

---

## CyclicDependencyError

```python
class CyclicDependencyError(Exception)
```

Law 3: Dependencies form a DAG - cycle detected.

---

## IntentTree

```python
class IntentTree
```

Typed intent graph with dependencies.

---

## get_intent_tree

```python
def get_intent_tree() -> IntentTree
```

Get the global intent tree.

---

## reset_intent_tree

```python
def reset_intent_tree() -> None
```

Reset the global intent tree (for testing).

---

## create

```python
def create(cls, description: str, intent_type: IntentType=IntentType.IMPLEMENT, parent_id: IntentId | None=None, depends_on: tuple[IntentId, ...]=(), priority: int=0, tags: tuple[str, ...]=()) -> Intent
```

Create a new Intent.

---

## start

```python
def start(self) -> Intent
```

Transition to ACTIVE status.

---

## complete

```python
def complete(self) -> Intent
```

Transition to COMPLETE status.

---

## block

```python
def block(self, reason: str='') -> Intent
```

Transition to BLOCKED status.

---

## cancel

```python
def cancel(self) -> Intent
```

Transition to CANCELLED status.

---

## with_child

```python
def with_child(self, child_id: IntentId) -> Intent
```

Return Intent with added child.

---

## is_active

```python
def is_active(self) -> bool
```

Check if Intent is active.

---

## is_complete

```python
def is_complete(self) -> bool
```

Check if Intent is complete.

---

## is_blocked

```python
def is_blocked(self) -> bool
```

Check if Intent is blocked.

---

## is_terminal

```python
def is_terminal(self) -> bool
```

Check if Intent is in terminal state.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Intent
```

Create from dictionary.

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## add

```python
def add(self, intent: Intent) -> None
```

Add an Intent to the tree.

---

## get

```python
def get(self, intent_id: IntentId) -> Intent | None
```

Get an Intent by ID.

---

## update

```python
def update(self, intent: Intent) -> None
```

Update an existing Intent.

---

## children

```python
def children(self, intent_id: IntentId) -> list[Intent]
```

Get all children of an Intent.

---

## dependencies

```python
def dependencies(self, intent_id: IntentId) -> list[Intent]
```

Get all dependencies of an Intent.

---

## dependents

```python
def dependents(self, intent_id: IntentId) -> list[Intent]
```

Get all Intents that depend on this one.

---

## by_type

```python
def by_type(self, intent_type: IntentType) -> list[Intent]
```

Get all Intents of a given type.

---

## by_status

```python
def by_status(self, status: IntentStatus) -> list[Intent]
```

Get all Intents with a given status.

---

## ready_to_start

```python
def ready_to_start(self) -> list[Intent]
```

Get Intents that are ready to be started.

---

## blocked

```python
def blocked(self) -> list[Intent]
```

Get all blocked Intents.

---

## propagate_status

```python
def propagate_status(self, intent_id: IntentId) -> None
```

Propagate status changes up the tree.

---

## all

```python
def all(self) -> list[Intent]
```

Get all Intents.

---

## leaves

```python
def leaves(self) -> list[Intent]
```

Get all leaf Intents (no children).

---

## roots

```python
def roots(self) -> list[Intent]
```

Get all root Intents (no parent).

---

## root

```python
def root(self) -> Intent | None
```

Get the root Intent.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> IntentTree
```

Create from dictionary.

---

## services.witness.invoke

## invoke

```python
module invoke
```

Cross-Jewel Invocation: Witness Invoking Other Crown Jewels.

---

## InvocationResult

```python
class InvocationResult
```

Result of a cross-jewel invocation.

---

## classify_path

```python
def classify_path(path: str) -> tuple[str, str, str]
```

Parse an AGENTESE path into components.

---

## is_read_only_path

```python
def is_read_only_path(path: str) -> bool
```

Check if a path is read-only.

---

## is_mutation_path

```python
def is_mutation_path(path: str) -> bool
```

Check if a path is a mutation.

---

## JewelInvoker

```python
class JewelInvoker
```

Invokes other Crown Jewels on behalf of Witness.

### Examples
```python
>>> invoker = JewelInvoker(logos, gate, TrustLevel.AUTONOMOUS)
```
```python
>>> result = await invoker.invoke("world.gestalt.manifest", observer)
```
```python
>>> result = await invoker.invoke("self.memory.capture", observer, content="...")
```

---

## create_invoker

```python
def create_invoker(logos: 'Logos', trust_level: TrustLevel, boundary_checker: Any | None=None, log_invocations: bool=True) -> JewelInvoker
```

Create a JewelInvoker with appropriate configuration.

---

## is_success

```python
def is_success(self) -> bool
```

Check if invocation succeeded.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## invoke

```python
async def invoke(self, path: str, observer: 'Observer', **kwargs: Any) -> InvocationResult
```

Invoke an AGENTESE path with trust gating.

---

## invoke_read

```python
async def invoke_read(self, path: str, observer: 'Observer', **kwargs: Any) -> InvocationResult
```

Invoke a read-only path (any trust level).

---

## invoke_mutation

```python
async def invoke_mutation(self, path: str, observer: 'Observer', **kwargs: Any) -> InvocationResult
```

Invoke a mutation path (requires L3 AUTONOMOUS).

---

## can_invoke

```python
def can_invoke(self, path: str) -> bool
```

Check if a path can be invoked at current trust level.

---

## get_invocation_log

```python
def get_invocation_log(self, limit: int=100, success_only: bool=False) -> list[InvocationResult]
```

Get recent invocation log.

---

## services.witness.lesson

## lesson

```python
module lesson
```

Lesson: Curated Knowledge Layer with Versioning.

---

## generate_lesson_id

```python
def generate_lesson_id() -> LessonId
```

Generate a unique Lesson ID.

---

## LessonStatus

```python
class LessonStatus(Enum)
```

Status of a Lesson.

---

## Lesson

```python
class Lesson
```

Curated knowledge with versioning.

### Examples
```python
>>> v1 = Lesson.create(
```
```python
>>> v2 = v1.evolve(
```
```python
>>> v2.version  # 2
```
```python
>>> v2.supersedes  # v1.id
```

---

## LessonStore

```python
class LessonStore
```

Persistent storage for Lessons.

---

## get_lesson_store

```python
def get_lesson_store() -> LessonStore
```

Get the global lesson store.

---

## set_lesson_store

```python
def set_lesson_store(store: LessonStore) -> None
```

Set the global lesson store.

---

## reset_lesson_store

```python
def reset_lesson_store() -> None
```

Reset the global lesson store (for testing).

---

## create

```python
def create(cls, topic: str, content: str, tags: tuple[str, ...]=(), source: str='', confidence: float=1.0) -> Lesson
```

Create a new Lesson (version 1).

---

## evolve

```python
def evolve(self, content: str, reason: str='', tags: tuple[str, ...] | None=None, confidence: float | None=None) -> Lesson
```

Create a new version that supersedes this one.

---

## deprecate

```python
def deprecate(self, reason: str='') -> Lesson
```

Mark this Lesson as deprecated.

---

## archive

```python
def archive(self) -> Lesson
```

Mark this Lesson as archived.

---

## is_current

```python
def is_current(self) -> bool
```

Check if this is the current version.

---

## is_superseded

```python
def is_superseded(self) -> bool
```

Check if this has been superseded.

---

## is_deprecated

```python
def is_deprecated(self) -> bool
```

Check if this is deprecated.

---

## has_supersedes

```python
def has_supersedes(self) -> bool
```

Check if this supersedes another version.

---

## age_days

```python
def age_days(self) -> float
```

Get the age of this Lesson in days.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Lesson
```

Create from dictionary.

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## add

```python
def add(self, lesson: Lesson) -> None
```

Add a Lesson to the store.

---

## update

```python
def update(self, lesson: Lesson) -> None
```

Update an existing Lesson (for status changes).

---

## get

```python
def get(self, lesson_id: LessonId) -> Lesson | None
```

Get a Lesson by ID.

---

## current

```python
def current(self, topic: str) -> Lesson | None
```

Get the current (latest) version for a topic.

---

## history

```python
def history(self, topic: str) -> list[Lesson]
```

Get version history for a topic.

---

## latest

```python
def latest(self, topic: str) -> Lesson | None
```

Get the latest version for a topic (regardless of status).

---

## by_tag

```python
def by_tag(self, tag: str) -> list[Lesson]
```

Get all CURRENT Lessons with a specific tag.

---

## by_source

```python
def by_source(self, source: str) -> list[Lesson]
```

Get all CURRENT Lessons from a specific source.

---

## search

```python
def search(self, query: str) -> list[Lesson]
```

Search CURRENT Lessons by topic or content.

---

## all_current

```python
def all_current(self) -> list[Lesson]
```

Get all CURRENT Lessons.

---

## all_topics

```python
def all_topics(self) -> list[str]
```

Get all topics.

---

## deprecated

```python
def deprecated(self) -> list[Lesson]
```

Get all deprecated Lessons.

---

## recent

```python
def recent(self, limit: int=10) -> list[Lesson]
```

Get most recently created Lessons.

---

## predecessor

```python
def predecessor(self, lesson: Lesson) -> Lesson | None
```

Get the version this Lesson supersedes.

---

## successor

```python
def successor(self, lesson: Lesson) -> Lesson | None
```

Get the version that superseded this one (if any).

---

## full_chain

```python
def full_chain(self, topic: str) -> list[Lesson]
```

Get the full version chain for a topic, ordered by version.

---

## stats

```python
def stats(self) -> dict[str, int]
```

Get store statistics.

---

## services.witness.mark

## mark

```python
module mark
```

Mark: The Atomic Unit of Execution Artifact.

### Things to Know

ℹ️ Marks are IMMUTABLE (frozen=True). You cannot modify a Mark after creation. To "update" metadata, create a new Mark linked via CONTINUES relation to the original.
  - *Verified in: `test_trace_node.py::test_mark_immutability`*

ℹ️ MarkLink.source can be MarkId OR PlanPath. This allows linking marks to Forest plan files directly. When traversing links, check the type before assuming you have a MarkId.
  - *Verified in: `test_session_walk.py::TestForestIntegration::test_walk_with_root_plan`*

---

## generate_mark_id

```python
def generate_mark_id() -> MarkId
```

Generate a unique Mark ID.

---

## LinkRelation

```python
class LinkRelation(Enum)
```

Types of causal relationships between Marks.

---

## MarkLink

```python
class MarkLink
```

Causal edge between Marks or to plans.

### Examples
```python
>>> link = MarkLink(
```

---

## NPhase

```python
class NPhase(Enum)
```

N-Phase workflow phases.

---

## UmweltSnapshot

```python
class UmweltSnapshot
```

Snapshot of observer capabilities at Mark emission time.

---

## Stimulus

```python
class Stimulus
```

What triggered the Mark.

---

## Response

```python
class Response
```

What the Mark produced.

---

## Mark

```python
class Mark
```

Atomic unit of execution artifact.

### Examples
```python
>>> mark = Mark(
```
```python
>>> mark.id  # "mark-abc123def456"
```

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> MarkLink
```

Create from dictionary.

---

## family

```python
def family(self) -> str
```

Return the 3-phase family this phase belongs to.

---

## system

```python
def system(cls) -> UmweltSnapshot
```

Create a system-level umwelt (full capabilities).

---

## witness

```python
def witness(cls, trust_level: int=0) -> UmweltSnapshot
```

Create a Witness umwelt with specified trust level.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> UmweltSnapshot
```

Create from dictionary.

---

## from_agentese

```python
def from_agentese(cls, path: str, aspect: str, **kwargs: Any) -> Stimulus
```

Create stimulus from AGENTESE invocation.

---

## from_prompt

```python
def from_prompt(cls, prompt: str, source: str='user') -> Stimulus
```

Create stimulus from user prompt.

---

## from_event

```python
def from_event(cls, event_type: str, content: str, source: str) -> Stimulus
```

Create stimulus from watcher event.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Stimulus
```

Create from dictionary.

---

## thought

```python
def thought(cls, content: str, tags: tuple[str, ...]=()) -> Response
```

Create response from Witness thought.

---

## projection

```python
def projection(cls, path: str, target: str='cli') -> Response
```

Create response from AGENTESE projection.

---

## error

```python
def error(cls, message: str) -> Response
```

Create error response.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Response
```

Create from dictionary.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate causal links (Law 2 check deferred to store).

---

## from_thought

```python
def from_thought(cls, content: str, source: str, tags: tuple[str, ...]=(), origin: str='witness', trust_level: int=0, phase: NPhase | None=None) -> Mark
```

Create Mark from Witness Thought pattern.

---

## from_agentese

```python
def from_agentese(cls, path: str, aspect: str, response_content: str, origin: str='logos', umwelt: UmweltSnapshot | None=None, phase: NPhase | None=None, **kwargs: Any) -> Mark
```

Create Mark from AGENTESE invocation.

---

## with_link

```python
def with_link(self, link: MarkLink) -> Mark
```

Return new Mark with added link (immutable pattern).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Mark
```

Create from dictionary.

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## services.witness.node

## node

```python
module node
```

Witness AGENTESE Node: @node("self.witness")

---

## WitnessManifestRendering

```python
class WitnessManifestRendering
```

Rendering for witness status manifest.

---

## ThoughtStreamRendering

```python
class ThoughtStreamRendering
```

Rendering for thought stream.

---

## WitnessNode

```python
class WitnessNode(BaseLogosNode)
```

AGENTESE node for Witness Crown Jewel (8th Jewel).

---

## __init__

```python
def __init__(self, witness_persistence: WitnessPersistence, logos: Any=None) -> None
```

Initialize WitnessNode.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `self.witness.manifest`

Manifest witness status to observer.

---

## stream

```python
async def stream(self, observer: 'Observer | Umwelt[Any, Any]', **kwargs: Any) -> AsyncGenerator[dict[str, Any], None]
```

**AGENTESE:** `self.witness.stream`

Stream thoughts in real-time via Server-Sent Events.

---

## services.witness.operad

## operad

```python
module operad
```

WitnessOperad: Formal Grammar for Autonomous Developer Agency.

---

## WitnessMetabolics

```python
class WitnessMetabolics
```

Metabolic costs of a witness operation.

---

## create_witness_operad

```python
def create_witness_operad() -> Operad
```

Create the Witness Operad.

---

## compose_observe_workflow

```python
def compose_observe_workflow(sources: list[str]) -> PolyAgent[Any, Any, Any]
```

Compose a complete observation workflow.

---

## compose_suggest_workflow

```python
def compose_suggest_workflow(sources: list[str], analyzer: str, action_type: str) -> PolyAgent[Any, Any, Any]
```

Compose a complete suggestion workflow.

---

## compose_autonomous_workflow

```python
def compose_autonomous_workflow(sources: list[str], analyzer: str, action: str, target: str | None=None) -> PolyAgent[Any, Any, Any]
```

Compose a complete autonomous workflow.

---

## can_execute

```python
def can_execute(self, current_trust: TrustLevel) -> bool
```

Check if operation can execute at given trust level.

---

## services.witness.persistence

## persistence

```python
module persistence
```

Witness Persistence: Dual-Track Storage for the 8th Crown Jewel.

---

## ThoughtResult

```python
class ThoughtResult
```

Result of a thought save operation.

---

## TrustResult

```python
class TrustResult
```

Result of a trust query with decay applied.

---

## EscalationResult

```python
class EscalationResult
```

Result of an escalation record.

---

## ActionResultPersisted

```python
class ActionResultPersisted
```

Result of an action save operation.

---

## WitnessStatus

```python
class WitnessStatus
```

Witness health status.

---

## WitnessPersistence

```python
class WitnessPersistence
```

Persistence layer for Witness Crown Jewel.

---

## save_thought

```python
async def save_thought(self, thought: Thought, trust_id: str | None=None, repository_path: str | None=None) -> ThoughtResult
```

**AGENTESE:** `self.witness.thoughts.capture`

Save a thought to dual-track storage.

---

## get_thoughts

```python
async def get_thoughts(self, limit: int=50, trust_id: str | None=None, source: str | None=None, since: datetime | None=None) -> list[Thought]
```

**AGENTESE:** `self.witness.thoughts`

Get recent thoughts with optional filters.

---

## thought_stream

```python
async def thought_stream(self, limit: int=50, sources: list[str] | None=None, poll_interval: float=2.0) -> AsyncGenerator[Thought, None]
```

**AGENTESE:** `self.witness.thoughts.stream`

Stream thoughts in real-time via async generator.

---

## get_trust_level

```python
async def get_trust_level(self, git_email: str, repository_path: str | None=None, apply_decay: bool=True) -> TrustResult
```

**AGENTESE:** `self.witness.trust`

Get trust level for a user, with decay applied.

---

## update_trust_metrics

```python
async def update_trust_metrics(self, git_email: str, observation_count: int | None=None, successful_operations: int | None=None, confirmed_suggestion: bool | None=None) -> TrustResult
```

Update trust metrics for a user.

---

## record_escalation

```python
async def record_escalation(self, git_email: str, from_level: TrustLevel, to_level: TrustLevel, reason: str) -> EscalationResult
```

**AGENTESE:** `self.witness.trust.escalate`

Record a trust escalation event.

---

## record_action

```python
async def record_action(self, action: ActionResult, trust_id: str | None=None, repository_path: str | None=None, git_stash_ref: str | None=None, checkpoint_path: str | None=None) -> ActionResultPersisted
```

**AGENTESE:** `self.witness.actions.record`

Record an action with rollback info.

---

## get_rollback_window

```python
async def get_rollback_window(self, hours: int=168, limit: int=100, reversible_only: bool=True) -> list[ActionResult]
```

**AGENTESE:** `self.witness.actions.rollback_window`

Get actions within the rollback window.

---

## manifest

```python
async def manifest(self) -> WitnessStatus
```

**AGENTESE:** `self.witness.manifest`

Get witness health status.

---

## services.witness.pipeline

## pipeline

```python
module pipeline
```

Cross-Jewel Pipeline: Composable Workflows Across Crown Jewels.

---

## PipelineStatus

```python
class PipelineStatus(Enum)
```

Status of a pipeline execution.

---

## Step

```python
class Step
```

A single step in a pipeline.

---

## Branch

```python
class Branch
```

Conditional branch in a pipeline.

---

## Pipeline

```python
class Pipeline
```

Composable pipeline of jewel invocations.

---

## StepResult

```python
class StepResult
```

Result of a single step execution.

---

## PipelineResult

```python
class PipelineResult
```

Result of a complete pipeline execution.

---

## PipelineRunner

```python
class PipelineRunner
```

Executes pipelines across Crown Jewels.

---

## step

```python
def step(path: str, **kwargs: Any) -> Step
```

Create a pipeline step (convenience function).

---

## branch

```python
def branch(condition: Callable[[Any], bool], if_true: Step | Pipeline, if_false: Step | Pipeline | None=None) -> Branch
```

Create a conditional branch (convenience function).

---

## PathPipeline

```python
class PathPipeline
```

Build pipelines from AGENTESE path strings.

---

## __rshift__

```python
def __rshift__(self, other: 'Step | Branch | Pipeline') -> 'Pipeline'
```

Compose with >> operator.

---

## __rrshift__

```python
def __rrshift__(self, other: str) -> 'Pipeline'
```

Allow string >> Step.

---

## __rshift__

```python
def __rshift__(self, other: 'Step | Branch | Pipeline') -> 'Pipeline'
```

Compose with >> operator.

---

## __rrshift__

```python
def __rrshift__(self, other: str) -> 'Pipeline'
```

Allow string >> Pipeline.

---

## __len__

```python
def __len__(self) -> int
```

Number of steps in pipeline.

---

## __iter__

```python
def __iter__(self) -> 'Iterator[Step | Branch]'
```

Iterate over steps.

---

## paths

```python
def paths(self) -> list[str]
```

Get all paths in the pipeline (flattened).

---

## success

```python
def success(self) -> bool
```

Check if pipeline completed successfully.

---

## failed_step

```python
def failed_step(self) -> StepResult | None
```

Get the first failed step, if any.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## run

```python
async def run(self, pipeline: Pipeline, initial_kwargs: dict[str, Any] | None=None) -> PipelineResult
```

Execute a pipeline.

---

## from_paths

```python
def from_paths(paths: list[str]) -> Pipeline
```

Create a Pipeline from a list of path strings.

---

## empty

```python
def empty() -> Pipeline
```

Create an empty pipeline for chaining.

---

## services.witness.playbook

## playbook

```python
module playbook
```

Playbook: Lawful Workflow Orchestration.

### Things to Know

🚨 **Critical:** Always verify Grant is GRANTED status before creating Playbook. Passing a PENDING or REVOKED Grant raises MissingGrant.
  - *Verified in: `test_ritual.py::test_ritual_requires_grant`*

ℹ️ Phase transitions are DIRECTED—you cannot skip phases. SENSE → ACT → REFLECT → SENSE (cycle). InvalidPhaseTransition if wrong.
  - *Verified in: `test_ritual.py::test_invalid_transitions_blocked`*

ℹ️ Guards evaluate at phase boundaries, not during phase. Budget exhaustion during ACT phase only fails at ACT → REFLECT.
  - *Verified in: `test_ritual.py::test_guard_evaluation_recorded`*

🚨 **Critical:** from_dict() does NOT restore _grant and _scope objects. You must reattach them manually after deserialization.
  - *Verified in: `test_ritual.py::test_ritual_roundtrip`*

---

## generate_playbook_id

```python
def generate_playbook_id() -> PlaybookId
```

Generate a unique Playbook ID.

---

## PlaybookStatus

```python
class PlaybookStatus(Enum)
```

Status of a Playbook.

---

## GuardResult

```python
class GuardResult(Enum)
```

Result of a guard check.

---

## SentinelGuard

```python
class SentinelGuard
```

A check that must pass at phase boundaries.

---

## GuardEvaluation

```python
class GuardEvaluation
```

Result of evaluating a guard.

---

## PlaybookPhase

```python
class PlaybookPhase
```

Single phase in a Playbook state machine.

---

## PlaybookError

```python
class PlaybookError(Exception)
```

Base exception for Playbook errors.

---

## PlaybookNotActive

```python
class PlaybookNotActive(PlaybookError)
```

Playbook is not in ACTIVE status.

---

## InvalidPhaseTransition

```python
class InvalidPhaseTransition(PlaybookError)
```

Law 4: Invalid phase transition attempted.

---

## GuardFailed

```python
class GuardFailed(PlaybookError)
```

Law 3: A guard check failed.

---

## MissingGrant

```python
class MissingGrant(PlaybookError)
```

Law 1: Playbook requires a Grant.

---

## MissingScope

```python
class MissingScope(PlaybookError)
```

Law 2: Playbook requires a Scope.

---

## Playbook

```python
class Playbook
```

Curator-orchestrated workflow with explicit gates.

### Examples
```python
>>> playbook = Playbook.create(
```
```python
>>> playbook.begin()
```
```python
>>> playbook.advance_phase(NPhase.ACT)
```
```python
>>> playbook.complete()
```

---

## PlaybookStore

```python
class PlaybookStore
```

Persistent storage for Playbooks.

---

## get_playbook_store

```python
def get_playbook_store() -> PlaybookStore
```

Get the global playbook store.

---

## reset_playbook_store

```python
def reset_playbook_store() -> None
```

Reset the global playbook store (for testing).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> SentinelGuard
```

Create from dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> PlaybookPhase
```

Create from dictionary.

---

## create

```python
def create(cls, name: str, grant: Grant, scope: Scope, phases: list[PlaybookPhase] | None=None, description: str='') -> Playbook
```

Create a new Playbook with Grant and Scope.

---

## begin

```python
def begin(self) -> None
```

Begin the Playbook.

---

## complete

```python
def complete(self) -> None
```

Mark Playbook as successfully complete.

---

## fail

```python
def fail(self, reason: str='') -> None
```

Mark Playbook as failed.

---

## cancel

```python
def cancel(self, reason: str='') -> None
```

Cancel the Playbook.

---

## pause

```python
def pause(self) -> None
```

Pause the Playbook.

---

## resume

```python
def resume(self) -> None
```

Resume a paused Playbook.

---

## can_transition

```python
def can_transition(self, to_phase: NPhase) -> bool
```

Check if transition to phase is valid.

---

## advance_phase

```python
def advance_phase(self, to_phase: NPhase) -> bool
```

Advance to a new phase.

---

## add_guard

```python
def add_guard(self, guard: SentinelGuard) -> None
```

Add an entry guard to the Playbook.

---

## record_mark

```python
def record_mark(self, mark: Mark) -> None
```

Record a Mark emitted during this Playbook.

---

## record_trace

```python
def record_trace(self, trace: Mark) -> None
```

Record a Mark (backwards compat alias).

---

## mark_count

```python
def mark_count(self) -> int
```

Number of marks recorded.

---

## trace_count

```python
def trace_count(self) -> int
```

Number of marks recorded (backwards compat alias).

---

## covenant_id

```python
def covenant_id(self) -> GrantId | None
```

Backwards compat alias for grant_id.

---

## offering_id

```python
def offering_id(self) -> ScopeId | None
```

Backwards compat alias for scope_id.

---

## current_step

```python
def current_step(self) -> int
```

Backwards compat: phases are the new steps.

---

## total_steps

```python
def total_steps(self) -> int
```

Backwards compat: count of phases.

---

## grant

```python
def grant(self) -> Grant | None
```

Get the associated Grant.

---

## covenant

```python
def covenant(self) -> Grant | None
```

Get the associated Grant (backwards compat alias).

---

## scope

```python
def scope(self) -> Scope | None
```

Get the associated Scope.

---

## offering

```python
def offering(self) -> Scope | None
```

Get the associated Scope (backwards compat alias).

---

## is_active

```python
def is_active(self) -> bool
```

Check if Playbook is active.

---

## is_complete

```python
def is_complete(self) -> bool
```

Check if Playbook is complete.

---

## duration_seconds

```python
def duration_seconds(self) -> float | None
```

Duration of the Playbook in seconds.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Playbook
```

Create from dictionary (without Grant/Scope - must be reattached).

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## add

```python
def add(self, playbook: Playbook) -> None
```

Add a Playbook to the store.

---

## get

```python
def get(self, playbook_id: PlaybookId) -> Playbook | None
```

Get a Playbook by ID.

---

## active

```python
def active(self) -> list[Playbook]
```

Get all active Playbooks.

---

## recent

```python
def recent(self, limit: int=10) -> list[Playbook]
```

Get most recent Playbooks.

---

## services.witness.polynomial

## polynomial

```python
module polynomial
```

WitnessPolynomial: Trust-Gated Behavior as State Machine.

### Examples
```python
>>> poly = WITNESS_POLYNOMIAL
```
```python
>>> state, output = poly.invoke(
```
```python
>>> print(output)
```
```python
>>> poly = WITNESS_POLYNOMIAL
```
```python
>>> state, output = poly.invoke(
```

---

## TrustLevel

```python
class TrustLevel(IntEnum)
```

Trust levels for the Witness.

---

## WitnessPhase

```python
class WitnessPhase(Enum)
```

Activity phases for the Witness.

---

## GitEvent

```python
class GitEvent
```

A git event detected by the GitWatcher.

---

## FileEvent

```python
class FileEvent
```

A filesystem event detected by the FileSystemWatcher.

---

## TestEvent

```python
class TestEvent
```

A test event detected by the TestWatcher.

---

## AgenteseEvent

```python
class AgenteseEvent
```

An AGENTESE event from SynergyBus.

---

## CIEvent

```python
class CIEvent
```

A CI/CD event from GitHub Actions.

---

## StartCommand

```python
class StartCommand
```

Command to start the witness.

---

## StopCommand

```python
class StopCommand
```

Command to stop the witness.

---

## EscalateCommand

```python
class EscalateCommand
```

Request trust escalation.

---

## ConfirmCommand

```python
class ConfirmCommand
```

Human confirmation for L2 suggestions.

---

## ActCommand

```python
class ActCommand
```

L3 action command.

---

## WitnessInputFactory

```python
class WitnessInputFactory
```

Factory for creating witness inputs.

---

## Thought

```python
class Thought
```

A thought in the thought stream.

---

## Suggestion

```python
class Suggestion
```

A suggested action (L2+).

---

## ActionResult

```python
class ActionResult
```

Result of an executed action (L3).

---

## WitnessOutput

```python
class WitnessOutput
```

Output from witness transitions.

---

## WitnessState

```python
class WitnessState
```

Complete witness state.

---

## witness_directions

```python
def witness_directions(state: WitnessState) -> FrozenSet[Any]
```

Valid inputs for each witness state.

---

## witness_transition

```python
def witness_transition(state: WitnessState, input: WitnessInput) -> tuple[WitnessState, WitnessOutput]
```

Witness state transition function.

---

## WitnessPolynomial

```python
class WitnessPolynomial
```

The Witness polynomial agent.

---

## can_write_kgents

```python
def can_write_kgents(self) -> bool
```

Can write to .kgents/ directory.

---

## can_suggest

```python
def can_suggest(self) -> bool
```

Can propose code changes for human review.

---

## can_act

```python
def can_act(self) -> bool
```

Can execute actions without human confirmation.

---

## emoji

```python
def emoji(self) -> str
```

Visual indicator for trust level.

---

## description

```python
def description(self) -> str
```

Human-readable description.

---

## git_commit

```python
def git_commit(sha: str, message: str='', author: str='') -> GitEvent
```

Create a git commit event.

---

## git_push

```python
def git_push(branch: str) -> GitEvent
```

Create a git push event.

---

## file_changed

```python
def file_changed(path: str) -> FileEvent
```

Create a file change event.

---

## test_failed

```python
def test_failed(test_id: str, error: str) -> TestEvent
```

Create a test failure event.

---

## test_session

```python
def test_session(passed: int, failed: int, skipped: int) -> TestEvent
```

Create a test session complete event.

---

## start

```python
def start(watchers: tuple[str, ...]=('git',)) -> StartCommand
```

Create a start command.

---

## stop

```python
def stop() -> StopCommand
```

Create a stop command.

---

## to_diary_line

```python
def to_diary_line(self) -> str
```

Format as a diary entry.

---

## add_thought

```python
def add_thought(self, thought: Thought) -> None
```

Add a thought to history (bounded).

---

## add_suggestion

```python
def add_suggestion(self, suggestion: Suggestion) -> None
```

Add a suggestion to history (bounded).

---

## add_action

```python
def add_action(self, action: ActionResult) -> None
```

Add an action to history (bounded).

---

## confirm_suggestion

```python
def confirm_suggestion(self, approved: bool) -> None
```

Record a suggestion confirmation.

---

## acceptance_rate

```python
def acceptance_rate(self) -> float
```

Suggestion acceptance rate.

---

## can_escalate_to_bounded

```python
def can_escalate_to_bounded(self) -> bool
```

Check if eligible for L0 → L1 escalation.

---

## can_escalate_to_suggestion

```python
def can_escalate_to_suggestion(self) -> bool
```

Check if eligible for L1 → L2 escalation.

---

## can_escalate_to_autonomous

```python
def can_escalate_to_autonomous(self) -> bool
```

Check if eligible for L2 → L3 escalation.

---

## positions

```python
def positions(self) -> FrozenSet[TrustLevel]
```

Trust levels are the primary positions.

---

## directions

```python
def directions(self, state: WitnessState) -> FrozenSet[Any]
```

Valid inputs at this state.

---

## transition

```python
def transition(self, state: WitnessState, input: WitnessInput) -> tuple[WitnessState, WitnessOutput]
```

Execute state transition.

---

## invoke

```python
def invoke(self, state: WitnessState, input: WitnessInput) -> tuple[WitnessState, WitnessOutput]
```

Invoke the polynomial (alias for transition).

---

## services.witness.reactor

## reactor

```python
module reactor
```

Witness Reactor: Event-to-Workflow Mapping.

---

## EventSource

```python
class EventSource(Enum)
```

Sources of events the reactor can subscribe to.

---

## Event

```python
class Event
```

A generic event that the reactor can respond to.

---

## git_commit_event

```python
def git_commit_event(sha: str, message: str, author: str='', files_changed: list[str] | None=None) -> Event
```

Create a git commit event.

---

## create_test_failure_event

```python
def create_test_failure_event(test_file: str, test_name: str, error_message: str='', traceback: str='') -> Event
```

Create a test failure event.

---

## pr_opened_event

```python
def pr_opened_event(pr_number: int, title: str, author: str='', base_branch: str='main', head_branch: str='') -> Event
```

Create a PR opened event.

---

## ci_status_event

```python
def ci_status_event(status: str, pipeline_name: str='', url: str='') -> Event
```

Create a CI status event.

---

## session_start_event

```python
def session_start_event(session_id: str='', context: str='') -> Event
```

Create a session start event.

---

## health_tick_event

```python
def health_tick_event() -> Event
```

Create a health check tick event.

---

## crystallization_ready_event

```python
def crystallization_ready_event(session_id: str, thought_count: int) -> Event
```

Create a crystallization ready event.

---

## ReactionStatus

```python
class ReactionStatus(Enum)
```

Status of a reaction.

---

## Reaction

```python
class Reaction
```

A pending or completed reaction to an event.

---

## EventMapping

```python
class EventMapping
```

Maps an event pattern to a workflow.

---

## EventHandler

```python
class EventHandler(Protocol)
```

Protocol for event handlers.

---

## WitnessReactor

```python
class WitnessReactor
```

The Witness's event-to-workflow reactor.

---

## create_reactor

```python
def create_reactor(invoker: 'JewelInvoker | None'=None, scheduler: 'WitnessScheduler | None'=None, observer: 'Observer | None'=None) -> WitnessReactor
```

Create a WitnessReactor instance.

---

## is_approved

```python
def is_approved(self) -> bool
```

Check if reaction has trust approval.

---

## can_run

```python
def can_run(self) -> bool
```

Check if reaction can run now.

---

## is_expired

```python
def is_expired(self) -> bool
```

Check if pending reaction has expired.

---

## approve

```python
def approve(self, trust_level: TrustLevel) -> bool
```

Approve reaction with given trust level.

---

## reject

```python
def reject(self, reason: str='') -> None
```

Reject the reaction.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## matches

```python
def matches(self, event: Event) -> bool
```

Check if this mapping matches an event.

---

## __call__

```python
async def __call__(self, event: Event) -> None
```

Handle an event.

---

## react

```python
async def react(self, event: Event) -> Reaction | None
```

React to an event.

---

## approve

```python
def approve(self, reaction_id: str, trust_level: TrustLevel) -> bool
```

Approve a pending reaction with given trust level.

---

## reject

```python
def reject(self, reaction_id: str, reason: str='') -> bool
```

Reject a pending reaction.

---

## add_mapping

```python
def add_mapping(self, mapping: EventMapping) -> None
```

Add a custom event-workflow mapping.

---

## remove_mapping

```python
def remove_mapping(self, source: EventSource, event_type: str) -> bool
```

Remove a mapping by source and event type.

---

## subscribe

```python
def subscribe(self, source: EventSource, handler: EventHandler) -> None
```

Subscribe a handler to an event source.

---

## unsubscribe

```python
def unsubscribe(self, source: EventSource, handler: EventHandler) -> None
```

Unsubscribe a handler from an event source.

---

## pending_reactions

```python
def pending_reactions(self) -> list[Reaction]
```

Get all pending reactions.

---

## active_reactions

```python
def active_reactions(self) -> list[Reaction]
```

Get all active (pending or running) reactions.

---

## get_reaction

```python
def get_reaction(self, reaction_id: str) -> Reaction | None
```

Get a reaction by ID.

---

## get_stats

```python
def get_stats(self) -> dict[str, Any]
```

Get reactor statistics.

---

## cleanup_expired

```python
def cleanup_expired(self) -> int
```

Remove expired pending reactions. Returns count removed.

---

## services.witness.schedule

## schedule

```python
module schedule
```

Witness Scheduler: Temporal Composition for Cross-Jewel Workflows.

---

## ScheduleType

```python
class ScheduleType(Enum)
```

Type of schedule.

---

## ScheduleStatus

```python
class ScheduleStatus(Enum)
```

Status of a scheduled task.

---

## ScheduledTask

```python
class ScheduledTask
```

A task scheduled for future execution.

---

## WitnessScheduler

```python
class WitnessScheduler
```

The Witness's temporal execution engine.

---

## create_scheduler

```python
def create_scheduler(invoker: JewelInvoker, observer: 'Observer', tick_interval: float=1.0, max_concurrent: int=5) -> WitnessScheduler
```

Create a WitnessScheduler instance.

---

## delay

```python
def delay(minutes: int=0, seconds: int=0, hours: int=0) -> timedelta
```

Create a timedelta for scheduling delays.

---

## every

```python
def every(minutes: int=0, seconds: int=0, hours: int=0) -> timedelta
```

Create a timedelta for periodic intervals.

---

## __lt__

```python
def __lt__(self, other: ScheduledTask) -> bool
```

Enable heapq ordering by next_run time.

---

## is_due

```python
def is_due(self) -> bool
```

Check if task is due for execution.

---

## is_active

```python
def is_active(self) -> bool
```

Check if task is still active (pending or running).

---

## can_run

```python
def can_run(self) -> bool
```

Check if task can run (not cancelled, not paused).

---

## advance_periodic

```python
def advance_periodic(self) -> None
```

Advance next_run for periodic tasks.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## schedule

```python
def schedule(self, path: str, at: datetime | None=None, delay: timedelta | None=None, name: str='', description: str='', tags: frozenset[str] | None=None, **kwargs: Any) -> ScheduledTask
```

Schedule a single AGENTESE invocation.

---

## schedule_pipeline

```python
def schedule_pipeline(self, pipeline: Pipeline, at: datetime | None=None, delay: timedelta | None=None, name: str='', description: str='', tags: frozenset[str] | None=None, initial_kwargs: dict[str, Any] | None=None) -> ScheduledTask
```

Schedule a pipeline for future execution.

---

## schedule_periodic

```python
def schedule_periodic(self, path: str, interval: timedelta, name: str='', description: str='', max_runs: int | None=None, start_immediately: bool=False, tags: frozenset[str] | None=None, **kwargs: Any) -> ScheduledTask
```

Schedule a periodic invocation.

---

## get_task

```python
def get_task(self, task_id: str) -> ScheduledTask | None
```

Get a task by ID.

---

## cancel

```python
def cancel(self, task_id: str) -> bool
```

Cancel a scheduled task.

---

## pause

```python
def pause(self, task_id: str) -> bool
```

Pause a periodic task.

---

## resume

```python
def resume(self, task_id: str) -> bool
```

Resume a paused task.

---

## tick

```python
async def tick(self) -> list[ScheduledTask]
```

Process all due tasks.

---

## run

```python
async def run(self) -> None
```

Run the scheduler loop.

---

## stop

```python
def stop(self) -> None
```

Stop the scheduler loop.

---

## pending_tasks

```python
def pending_tasks(self) -> list[ScheduledTask]
```

Get all pending tasks.

---

## active_tasks

```python
def active_tasks(self) -> list[ScheduledTask]
```

Get all active (pending or running) tasks.

---

## get_stats

```python
def get_stats(self) -> dict[str, Any]
```

Get scheduler statistics.

---

## services.witness.scope

## scope

```python
module scope
```

Scope: Explicit Context Contract with Budget Constraints.

---

## generate_scope_id

```python
def generate_scope_id() -> ScopeId
```

Generate a unique Scope ID.

---

## Budget

```python
class Budget
```

Resource constraints for a Scope.

### Examples
```python
>>> budget = Budget(tokens=10000, time_seconds=300.0, operations=50)
```
```python
>>> budget.can_consume(tokens=100)  # True
```
```python
>>> budget.remaining_after(tokens=100)  # Budget(tokens=9900, ...)
```

---

## ScopeError

```python
class ScopeError(Exception)
```

Base exception for Scope errors.

---

## BudgetExceeded

```python
class BudgetExceeded(ScopeError)
```

Law 1: Budget constraint exceeded - triggers review.

---

## ScopeExpired

```python
class ScopeExpired(ScopeError)
```

Law 3: Scope has expired.

---

## HandleNotInScope

```python
class HandleNotInScope(ScopeError)
```

Attempted to access a handle not in the Scope's scope.

---

## ScopeStatus

```python
class ScopeStatus(Enum)
```

Status of a Scope.

---

## Scope

```python
class Scope
```

Explicitly priced and scoped context contract.

### Examples
```python
>>> scope = Scope.create(
```
```python
>>> scope.is_valid()  # True
```
```python
>>> scope.can_access("time.trace.node.manifest")  # True
```
```python
>>> scope.can_access("self.lesson.manifest")  # False (not in scope)
```

---

## ScopeStore

```python
class ScopeStore
```

Persistent storage for Scopes.

---

## get_scope_store

```python
def get_scope_store() -> ScopeStore
```

Get the global scope store.

---

## reset_scope_store

```python
def reset_scope_store() -> None
```

Reset the global scope store (for testing).

---

## can_consume

```python
def can_consume(self, tokens: int=0, time_seconds: float=0.0, operations: int=0, capital: float=0.0, entropy: float=0.0) -> bool
```

Check if consumption would stay within budget.

---

## remaining_after

```python
def remaining_after(self, tokens: int=0, time_seconds: float=0.0, operations: int=0, capital: float=0.0, entropy: float=0.0) -> Budget
```

Return a new Budget with consumption deducted.

---

## is_exhausted

```python
def is_exhausted(self) -> bool
```

Check if any budget dimension is at zero.

---

## unlimited

```python
def unlimited(cls) -> Budget
```

Create an unlimited budget (all None).

---

## standard

```python
def standard(cls) -> Budget
```

Create a standard budget for typical operations.

---

## minimal

```python
def minimal(cls) -> Budget
```

Create a minimal budget for quick operations.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Budget
```

Create from dictionary.

---

## create

```python
def create(cls, description: str, scoped_handles: tuple[str, ...] | None=None, budget: Budget | None=None, duration: timedelta | None=None, expires_at: datetime | None=None) -> Scope
```

Create a new Scope.

---

## is_valid

```python
def is_valid(self) -> bool
```

Check if this Scope is currently valid.

---

## check_valid

```python
def check_valid(self) -> None
```

Raise ScopeExpired if not valid.

---

## time_remaining

```python
def time_remaining(self) -> timedelta | None
```

Get remaining time until expiry (None if no expiry).

---

## can_access

```python
def can_access(self, handle: str) -> bool
```

Check if a handle is within scope.

---

## check_access

```python
def check_access(self, handle: str) -> None
```

Raise HandleNotInScope if handle is not accessible.

---

## can_consume

```python
def can_consume(self, tokens: int=0, time_seconds: float=0.0, operations: int=0) -> bool
```

Check if consumption would stay within budget.

---

## consume

```python
def consume(self, tokens: int=0, time_seconds: float=0.0, operations: int=0) -> Scope
```

Return new Scope with consumption deducted.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for persistence.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Scope
```

Create from dictionary.

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## kind

```python
def kind(self) -> str
```

Backwards compat: all scopes are 'resource' kind.

---

## scope

```python
def scope(self) -> tuple[str, ...]
```

Backwards compat: alias for scoped_handles.

---

## add

```python
def add(self, scope: Scope) -> None
```

Add a Scope to the store.

---

## get

```python
def get(self, scope_id: ScopeId) -> Scope | None
```

Get a Scope by ID.

---

## update

```python
def update(self, scope: Scope) -> None
```

Update a Scope (replace with new version).

---

## active

```python
def active(self) -> list[Scope]
```

Get all currently valid Scopes.

---

## expired

```python
def expired(self) -> list[Scope]
```

Get all expired Scopes.

---

## services.witness.session_walk

## session_walk

```python
module session_walk
```

Session-Walk Bridge: Connects CLI Sessions to WARP Walks.

### Things to Know

ℹ️ Starting a second Walk for a session with active Walk raises ValueError. Complete or abandon the current Walk first. Check has_walk() before calling start_walk_for_session().
  - *Verified in: `test_session_walk.py::TestLaw1SessionOwnsWalk::test_cannot_start_second_walk_when_active`*

🚨 **Critical:** advance_walk() returns False silently for sessions without Walk. It does NOT raise an exception. Always check has_walk() first if you need to know whether the Walk exists.
  - *Verified in: `test_session_walk.py::TestLaw3OptionalBinding::test_advance_walk_returns_false_without_walk`*

---

## SessionWalkBinding

```python
class SessionWalkBinding
```

Binding between a CLI session and its Walk.

---

## SessionWalkBridge

```python
class SessionWalkBridge
```

Bridge for connecting CLI sessions to WARP Walks.

---

## get_session_walk_bridge

```python
def get_session_walk_bridge() -> SessionWalkBridge
```

Get the global session-walk bridge.

---

## reset_session_walk_bridge

```python
def reset_session_walk_bridge() -> None
```

Reset the global bridge (for testing).

---

## __init__

```python
def __init__(self, walk_store: WalkStore | None=None) -> None
```

Initialize bridge.

---

## start_walk_for_session

```python
def start_walk_for_session(self, cli_session_id: str, goal: str, *, root_plan: str | PlanPath | None=None, session_name: str='') -> Walk
```

Create and bind a Walk to a CLI session.

---

## get_walk_for_session

```python
def get_walk_for_session(self, cli_session_id: str) -> Walk | None
```

Get the Walk bound to a CLI session.

---

## has_walk

```python
def has_walk(self, cli_session_id: str) -> bool
```

Check if a CLI session has a Walk bound.

---

## advance_walk

```python
def advance_walk(self, cli_session_id: str, trace_node: Mark) -> bool
```

Add a Mark to the session's Walk.

---

## transition_phase_for_session

```python
def transition_phase_for_session(self, cli_session_id: str, to_phase: str) -> bool
```

Transition the Walk's N-Phase.

---

## pause_walk

```python
def pause_walk(self, cli_session_id: str) -> bool
```

Pause the Walk when session pauses.

---

## resume_walk

```python
def resume_walk(self, cli_session_id: str) -> bool
```

Resume a paused Walk.

---

## end_session

```python
def end_session(self, cli_session_id: str, *, complete: bool=True) -> Walk | None
```

Handle CLI session end.

---

## active_sessions_with_walks

```python
def active_sessions_with_walks(self) -> list[str]
```

Get CLI session IDs that have active Walks.

---

## services.witness.sheaf

## sheaf

```python
module sheaf
```

WitnessSheaf: Emergence from Event Sources to Coherent Crystals.

---

## EventSource

```python
class EventSource(Enum)
```

Contexts in the Witness observation topology.

---

## source_overlap

```python
def source_overlap(s1: EventSource, s2: EventSource) -> frozenset[str]
```

Compute capability overlap between event sources.

---

## LocalObservation

```python
class LocalObservation
```

A local view from a single event source.

---

## GluingError

```python
class GluingError(Exception)
```

Raised when local observations cannot be glued.

---

## WitnessSheaf

```python
class WitnessSheaf
```

Sheaf structure for gluing event source observations into crystals.

### Examples
```python
>>> sheaf = WitnessSheaf()
```
```python
>>> obs1 = LocalObservation(EventSource.GIT, git_thoughts, t0, t1)
```
```python
>>> obs2 = LocalObservation(EventSource.TESTS, test_thoughts, t0, t1)
```
```python
>>> if sheaf.compatible([obs1, obs2]):
```

---

## verify_identity_law

```python
def verify_identity_law(sheaf: WitnessSheaf, observation: LocalObservation, session_id: str='test') -> bool
```

Verify the identity law: glue([single_source]) ≅ from_thoughts(source.thoughts).

---

## verify_associativity_law

```python
def verify_associativity_law(sheaf: WitnessSheaf, obs_a: LocalObservation, obs_b: LocalObservation, obs_c: LocalObservation, session_id: str='test') -> bool
```

Verify the associativity law: glue(glue([A, B]), C) ≅ glue(A, glue([B, C])).

---

## capabilities

```python
def capabilities(self) -> frozenset[str]
```

Capabilities this source provides.

---

## duration_seconds

```python
def duration_seconds(self) -> float
```

Duration of this observation window.

---

## thought_count

```python
def thought_count(self) -> int
```

Number of thoughts in this observation.

---

## overlaps_temporally

```python
def overlaps_temporally(self, other: LocalObservation) -> bool
```

Check if time windows overlap.

---

## __init__

```python
def __init__(self, time_tolerance: timedelta=timedelta(minutes=5)) -> None
```

Initialize the WitnessSheaf.

---

## overlap

```python
def overlap(self, s1: EventSource, s2: EventSource) -> frozenset[str]
```

Compute the overlap between two event sources.

---

## compatible

```python
def compatible(self, observations: Sequence[LocalObservation]) -> bool
```

Check if local observations can be glued.

---

## glue

```python
def glue(self, observations: Sequence[LocalObservation], session_id: str='', markers: list[str] | None=None, narrative: Narrative | None=None) -> ExperienceCrystal
```

Glue local observations into a coherent ExperienceCrystal.

---

## restrict

```python
def restrict(self, crystal: ExperienceCrystal, source: EventSource) -> LocalObservation
```

Restrict a crystal back to a single source view.

---

## services.witness.trace_store

## trace_store

```python
module trace_store
```

MarkStore: Append-Only Ledger for Marks.

---

## MarkStoreError

```python
class MarkStoreError(Exception)
```

Base exception for trace store errors.

---

## CausalityViolation

```python
class CausalityViolation(MarkStoreError)
```

Raised when a MarkLink violates causality (Law 2).

---

## DuplicateMarkError

```python
class DuplicateMarkError(MarkStoreError)
```

Raised when attempting to add a trace with an existing ID.

---

## MarkNotFoundError

```python
class MarkNotFoundError(MarkStoreError)
```

Raised when a referenced trace is not found.

---

## MarkQuery

```python
class MarkQuery
```

Query parameters for trace retrieval.

---

## MarkStore

```python
class MarkStore
```

Append-only ledger for Marks.

### Examples
```python
>>> store = MarkStore()
```
```python
>>> node = Mark.from_thought("Test", "git", ("test",))
```
```python
>>> store.append(node)
```
```python
>>> retrieved = store.get(node.id)
```
```python
>>> assert retrieved == node
```

---

## get_mark_store

```python
def get_mark_store() -> MarkStore
```

Get the global trace store (singleton).

---

## set_mark_store

```python
def set_mark_store(store: MarkStore) -> None
```

Set the global trace store (for testing).

---

## reset_mark_store

```python
def reset_mark_store() -> None
```

Reset the global trace store (for testing).

---

## matches

```python
def matches(self, node: Mark, store: MarkStore) -> bool
```

Check if a trace node matches this query.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize secondary indices.

---

## append

```python
def append(self, node: Mark) -> None
```

Append a Mark to the ledger.

---

## get

```python
def get(self, trace_id: MarkId) -> Mark | None
```

Get a Mark by ID.

---

## get_or_raise

```python
def get_or_raise(self, trace_id: MarkId) -> Mark
```

Get a Mark by ID, raising if not found.

---

## query

```python
def query(self, query: MarkQuery) -> Iterator[Mark]
```

Query traces matching the given criteria.

---

## count

```python
def count(self, query: MarkQuery | None=None) -> int
```

Count traces matching the query (or all traces if no query).

---

## all

```python
def all(self) -> Iterator[Mark]
```

Iterate over all traces in timestamp order.

---

## recent

```python
def recent(self, limit: int=10) -> list[Mark]
```

Get the most recent traces.

---

## get_causes

```python
def get_causes(self, trace_id: MarkId) -> list[Mark]
```

Get all traces that caused this trace (incoming CAUSES links).

---

## get_effects

```python
def get_effects(self, trace_id: MarkId) -> list[Mark]
```

Get all traces caused by this trace (outgoing CAUSES links).

---

## get_continuation

```python
def get_continuation(self, trace_id: MarkId) -> list[Mark]
```

Get traces that continue this trace (CONTINUES relation).

---

## get_branches

```python
def get_branches(self, trace_id: MarkId) -> list[Mark]
```

Get traces that branch from this trace (BRANCHES relation).

---

## get_fulfillments

```python
def get_fulfillments(self, trace_id: MarkId) -> list[Mark]
```

Get traces that fulfill intents in this trace (FULFILLS relation).

---

## get_walk_traces

```python
def get_walk_traces(self, walk_id: WalkId) -> list[Mark]
```

Get all traces in a specific Walk.

---

## save

```python
def save(self, path: Path | str) -> None
```

Save the store to a JSON file.

---

## load

```python
def load(cls, path: Path | str) -> MarkStore
```

Load a store from a JSON file.

---

## sync

```python
def sync(self) -> None
```

Sync to persistence path if set.

---

## stats

```python
def stats(self) -> dict[str, Any]
```

Get store statistics.

---

## __len__

```python
def __len__(self) -> int
```

Return the number of traces in the store.

---

## __contains__

```python
def __contains__(self, trace_id: MarkId) -> bool
```

Check if a trace ID exists in the store.

---

## services.witness.trust.__init__

## __init__

```python
module __init__
```

Witness Trust System: Earned Autonomy Through Demonstrated Competence.

---

## services.witness.trust.boundaries

## boundaries

```python
module boundaries
```

BoundaryChecker: Forbidden Actions That Should Never Be Autonomous.

---

## BoundaryViolation

```python
class BoundaryViolation
```

A detected boundary violation.

---

## BoundaryChecker

```python
class BoundaryChecker
```

Checks actions against forbidden boundaries.

---

## __init__

```python
def __init__(self, forbidden_actions: frozenset[str] | None=None, forbidden_substrings: frozenset[str] | None=None) -> None
```

Initialize boundary checker.

---

## check

```python
def check(self, action: str) -> BoundaryViolation | None
```

Check if an action violates boundaries.

---

## is_allowed

```python
def is_allowed(self, action: str) -> bool
```

Quick check if action is allowed.

---

## services.witness.trust.confirmation

## confirmation

```python
module confirmation
```

ConfirmationManager: Level 2 Suggestion Confirmation Flow.

---

## SuggestionStatus

```python
class SuggestionStatus(Enum)
```

Status of a pending suggestion.

---

## ActionPreview

```python
class ActionPreview
```

Preview of what an action will do.

---

## PendingSuggestion

```python
class PendingSuggestion
```

A suggestion awaiting human confirmation.

---

## ConfirmationResult

```python
class ConfirmationResult
```

Result of a confirmation action.

---

## ConfirmationManager

```python
class ConfirmationManager
```

Manages pending suggestions awaiting confirmation.

---

## is_expired

```python
def is_expired(self) -> bool
```

Check if suggestion has expired.

---

## time_remaining

```python
def time_remaining(self) -> timedelta
```

Time remaining before expiration.

---

## to_display

```python
def to_display(self) -> dict[str, Any]
```

Format for human review.

---

## __init__

```python
def __init__(self, notification_handler: Callable[[PendingSuggestion], Coroutine[Any, Any, None]] | None=None, execution_handler: Callable[[str], Coroutine[Any, Any, tuple[bool, str]]] | None=None, pipeline_runner: Any | None=None, expiration_hours: float=1.0) -> None
```

Initialize confirmation manager.

---

## set_pipeline_runner

```python
def set_pipeline_runner(self, runner: Any) -> None
```

Set the pipeline runner for workflow execution.

---

## submit

```python
async def submit(self, action: str, rationale: str, confidence: float=0.5, target: str | None=None, preview: ActionPreview | None=None, pipeline: Any | None=None, initial_kwargs: dict[str, Any] | None=None) -> PendingSuggestion
```

Submit a suggestion for confirmation.

---

## confirm

```python
async def confirm(self, suggestion_id: str, confirmed_by: str='user') -> ConfirmationResult
```

Confirm a pending suggestion.

---

## reject

```python
async def reject(self, suggestion_id: str, reason: str='') -> ConfirmationResult
```

Reject a pending suggestion.

---

## expire_stale

```python
async def expire_stale(self) -> int
```

Expire suggestions that have timed out.

---

## get_pending

```python
def get_pending(self) -> list[PendingSuggestion]
```

Get all pending suggestions.

---

## get_suggestion

```python
def get_suggestion(self, suggestion_id: str) -> PendingSuggestion | None
```

Get a specific suggestion.

---

## acceptance_rate

```python
def acceptance_rate(self) -> float
```

Calculate acceptance rate for escalation metrics.

---

## stats

```python
def stats(self) -> dict[str, int | float]
```

Get manager statistics.

---

## clear

```python
def clear(self) -> None
```

Clear all pending suggestions (for testing).

---

## services.witness.trust.escalation

## escalation

```python
module escalation
```

Escalation Criteria: Rules for Trust Level Transitions.

---

## ObservationStats

```python
class ObservationStats
```

Statistics for L0 → L1 escalation.

---

## OperationStats

```python
class OperationStats
```

Statistics for L1 → L2 escalation.

---

## SuggestionStats

```python
class SuggestionStats
```

Statistics for L2 → L3 escalation.

---

## EscalationResult

```python
class EscalationResult
```

Result of an escalation check.

---

## EscalationCriteria

```python
class EscalationCriteria(ABC, Generic[StatsT])
```

Abstract base for escalation criteria.

---

## Level1Criteria

```python
class Level1Criteria(EscalationCriteria[ObservationStats])
```

Criteria for L0 → L1 escalation.

---

## Level2Criteria

```python
class Level2Criteria(EscalationCriteria[OperationStats])
```

Criteria for L1 → L2 escalation.

---

## Level3Criteria

```python
class Level3Criteria(EscalationCriteria[SuggestionStats])
```

Criteria for L2 → L3 escalation.

---

## check_escalation

```python
def check_escalation(current_level: TrustLevel, stats: ObservationStats | OperationStats | SuggestionStats) -> EscalationResult | None
```

Check if escalation is possible from current level.

---

## false_positive_rate

```python
def false_positive_rate(self) -> float
```

Calculate false positive rate.

---

## failure_rate

```python
def failure_rate(self) -> float
```

Calculate failure rate.

---

## acceptance_rate

```python
def acceptance_rate(self) -> float
```

Calculate acceptance rate.

---

## progress_summary

```python
def progress_summary(self) -> str
```

Human-readable progress summary.

---

## from_level

```python
def from_level(self) -> TrustLevel
```

Source trust level.

---

## to_level

```python
def to_level(self) -> TrustLevel
```

Target trust level.

---

## check

```python
def check(self, stats: StatsT) -> EscalationResult
```

Check if escalation criteria are met.

---

## check

```python
def check(self, stats: ObservationStats) -> EscalationResult
```

Check if L1 criteria are met.

---

## check

```python
def check(self, stats: OperationStats) -> EscalationResult
```

Check if L2 criteria are met.

---

## check

```python
def check(self, stats: SuggestionStats) -> EscalationResult
```

Check if L3 criteria are met.

---

## services.witness.trust.gate

## gate

```python
module gate
```

ActionGate: Trust-Gated Execution for Witness Actions.

### Examples
```python
>>> gate = ActionGate(TrustLevel.SUGGESTION)
```
```python
>>> result = await gate.check("git commit -m 'fix: typo'")
```
```python
>>> print(result.decision)
```
```python
>>> gate = ActionGate(TrustLevel.SUGGESTION)
```
```python
>>> result = await gate.check("git commit -m 'fix: typo'")
```

---

## GateDecision

```python
class GateDecision(Enum)
```

Decision from the action gate.

---

## GateResult

```python
class GateResult
```

Result of gating an action.

---

## get_required_level

```python
def get_required_level(action: str) -> TrustLevel
```

Determine required trust level for an action.

---

## ActionGate

```python
class ActionGate
```

Gates actions based on trust level.

---

## is_allowed

```python
def is_allowed(self) -> bool
```

Check if action is allowed (ALLOW or LOG).

---

## requires_confirmation

```python
def requires_confirmation(self) -> bool
```

Check if action requires confirmation.

---

## is_denied

```python
def is_denied(self) -> bool
```

Check if action is denied.

---

## check

```python
def check(self, action: str, target: str | None=None) -> GateResult
```

Check if an action is allowed at the current trust level.

---

## can_perform

```python
def can_perform(self, capability: str) -> bool
```

Quick check if a capability is available at current trust level.

---

## update_trust

```python
def update_trust(self, new_level: TrustLevel) -> None
```

Update the trust level.

---

## services.witness.trust_persistence

## trust_persistence

```python
module trust_persistence
```

TrustPersistence: JSON-Based State Persistence for the Witness Daemon.

---

## PersistedTrustState

```python
class PersistedTrustState
```

Trust state that persists across daemon restarts.

---

## TrustPersistence

```python
class TrustPersistence
```

Manages persistence of witness trust state to disk.

---

## create_trust_persistence

```python
def create_trust_persistence(state_file: Path | None=None) -> TrustPersistence
```

Create a TrustPersistence instance.

---

## trust

```python
def trust(self) -> TrustLevel
```

Get trust level as TrustLevel enum.

---

## last_active

```python
def last_active(self) -> datetime | None
```

Get last_active as datetime.

---

## acceptance_rate

```python
def acceptance_rate(self) -> float
```

Calculate suggestion acceptance rate.

---

## apply_decay

```python
def apply_decay(self) -> bool
```

Apply trust decay based on inactivity.

---

## touch

```python
def touch(self) -> None
```

Update last_active to now.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to JSON-serializable dict.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> 'PersistedTrustState'
```

Create from dictionary.

---

## __init__

```python
def __init__(self, state_file: Path | None=None, auto_save: bool=True) -> None
```

Initialize trust persistence.

---

## current_state

```python
def current_state(self) -> PersistedTrustState
```

Get current state (load if not loaded).

---

## load

```python
async def load(self, apply_decay: bool=True) -> PersistedTrustState
```

Load trust state from disk.

---

## save

```python
async def save(self, state: PersistedTrustState | None=None) -> bool
```

Save trust state to disk.

---

## record_observation

```python
async def record_observation(self) -> None
```

Record an observation and auto-save if enabled.

---

## record_operation

```python
async def record_operation(self, success: bool=True) -> None
```

Record a bounded operation and auto-save if enabled.

---

## record_suggestion

```python
async def record_suggestion(self, confirmed: bool) -> None
```

Record a suggestion response and auto-save if enabled.

---

## escalate

```python
async def escalate(self, to_level: TrustLevel, reason: str='') -> bool
```

Escalate trust level.

---

## get_status

```python
def get_status(self) -> dict[str, Any]
```

Get current trust status for display.

---

## services.witness.tui

## tui

```python
module tui
```

Witness TUI: Textual Terminal User Interface for kgentsd.

---

## StatusPanel

```python
class StatusPanel(Static)
```

Status panel showing Witness state with trust escalation progress.

---

## ThoughtStream

```python
class ThoughtStream(RichLog)
```

Real-time thought stream display.

---

## SuggestionPrompt

```python
class SuggestionPrompt(Static)
```

L2 confirmation prompt with keyboard handling.

---

## WitnessApp

```python
class WitnessApp(App[None])
```

The Witness daemon TUI application.

---

## run_witness_tui

```python
def run_witness_tui(config: DaemonConfig) -> int
```

Run the Witness TUI application.

---

## add_thought

```python
def add_thought(self, thought: Thought) -> None
```

Add a thought to the stream.

---

## SuggestionAccepted

```python
class SuggestionAccepted(Message)
```

Emitted when user accepts a suggestion.

---

## SuggestionRejected

```python
class SuggestionRejected(Message)
```

Emitted when user rejects a suggestion.

---

## SuggestionIgnored

```python
class SuggestionIgnored(Message)
```

Emitted when user ignores a suggestion.

---

## watch_suggestion

```python
def watch_suggestion(self, suggestion: PendingSuggestion | None) -> None
```

Update display when suggestion changes.

---

## watch_is_visible

```python
def watch_is_visible(self, is_visible: bool) -> None
```

Show/hide the widget.

---

## on_key

```python
async def on_key(self, event: Any) -> None
```

Handle keyboard input for suggestion actions.

---

## show_suggestion

```python
def show_suggestion(self, suggestion: PendingSuggestion) -> None
```

Display a new suggestion.

---

## hide

```python
def hide(self) -> None
```

Hide the prompt.

---

## on_mount

```python
async def on_mount(self) -> None
```

Start the daemon when the app mounts.

---

## action_clear

```python
def action_clear(self) -> None
```

Clear the thought stream.

---

## action_status

```python
def action_status(self) -> None
```

Show detailed status.

---

## action_help

```python
def action_help(self) -> None
```

Show help.

---

## action_accept_suggestion

```python
async def action_accept_suggestion(self) -> None
```

Accept the current suggestion.

---

## action_reject_suggestion

```python
async def action_reject_suggestion(self) -> None
```

Reject the current suggestion.

---

## action_toggle_details

```python
def action_toggle_details(self) -> None
```

Toggle suggestion details view.

---

## action_ignore_suggestion

```python
def action_ignore_suggestion(self) -> None
```

Ignore the current suggestion without recording.

---

## action_quit

```python
async def action_quit(self) -> None
```

Quit the application gracefully.

---

## services.witness.voice_gate

## voice_gate

```python
module voice_gate
```

VoiceGate: Anti-Sausage Runtime Enforcement.

---

## VoiceAction

```python
class VoiceAction(Enum)
```

Action to take on voice rule match.

---

## VoiceRule

```python
class VoiceRule
```

A rule for voice checking.

### Examples
```python
>>> rule = VoiceRule(
```

---

## VoiceViolation

```python
class VoiceViolation
```

A detected voice violation.

---

## VoiceCheckResult

```python
class VoiceCheckResult
```

Result of checking text against voice rules.

---

## VoiceGate

```python
class VoiceGate
```

Runtime Anti-Sausage enforcement.

### Examples
```python
>>> gate = VoiceGate()
```
```python
>>> result = gate.check("We need to leverage synergies")
```
```python
>>> result.passed  # False - blocked by "leverage" and "synergies"
```
```python
>>> result = gate.check("Tasteful > feature-complete is our mantra")
```
```python
>>> result.anchors_referenced  # ("Tasteful > feature-complete",)
```

---

## get_voice_gate

```python
def get_voice_gate() -> VoiceGate
```

Get the global voice gate.

---

## set_voice_gate

```python
def set_voice_gate(gate: VoiceGate) -> None
```

Set the global voice gate.

---

## reset_voice_gate

```python
def reset_voice_gate() -> None
```

Reset the global voice gate (for testing).

---

## compiled

```python
def compiled(self) -> re.Pattern[str]
```

Get compiled regex pattern.

---

## matches

```python
def matches(self, text: str) -> list[str]
```

Find all matches in text.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> VoiceRule
```

Create from dictionary.

---

## action

```python
def action(self) -> VoiceAction
```

Get the action for this violation.

---

## is_blocking

```python
def is_blocking(self) -> bool
```

Check if this violation blocks output.

---

## is_warning

```python
def is_warning(self) -> bool
```

Check if this is a warning.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## has_violations

```python
def has_violations(self) -> bool
```

Check if any violations were found.

---

## has_warnings

```python
def has_warnings(self) -> bool
```

Check if any warnings were found.

---

## blocking_count

```python
def blocking_count(self) -> int
```

Count of blocking violations.

---

## warning_count

```python
def warning_count(self) -> int
```

Count of warnings.

---

## anchor_count

```python
def anchor_count(self) -> int
```

Count of anchor references.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## strict

```python
def strict(cls) -> VoiceGate
```

Create a strict VoiceGate that blocks denylist matches.

---

## permissive

```python
def permissive(cls) -> VoiceGate
```

Create a permissive VoiceGate that only warns.

---

## with_custom_rules

```python
def with_custom_rules(cls, rules: list[VoiceRule]) -> VoiceGate
```

Create with custom rules added.

---

## check

```python
def check(self, text: str) -> VoiceCheckResult
```

Check text against voice rules.

---

## is_clean

```python
def is_clean(self, text: str) -> bool
```

Quick check if text passes with no violations.

---

## has_corporate_speak

```python
def has_corporate_speak(self, text: str) -> bool
```

Check if text contains any denylist patterns.

---

## has_hedging

```python
def has_hedging(self, text: str) -> bool
```

Check if text contains hedging language.

---

## references_anchor

```python
def references_anchor(self, text: str) -> str | None
```

Check if text references any voice anchor. Returns first match.

---

## add_rule

```python
def add_rule(self, rule: VoiceRule) -> None
```

Add a custom rule.

---

## add_denylist_pattern

```python
def add_denylist_pattern(self, pattern: str, reason: str='Custom denylist pattern') -> None
```

Add a pattern to the denylist.

---

## suggest_transforms

```python
def suggest_transforms(self, text: str) -> list[tuple[str, str, str]]
```

Suggest transformations for violations.

---

## stats

```python
def stats(self) -> dict[str, int]
```

Get check statistics.

---

## reset_stats

```python
def reset_stats(self) -> None
```

Reset statistics.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> VoiceGate
```

Create from dictionary.

---

## services.witness.walk

## walk

```python
module walk
```

Walk: Durable Work Stream Tied to Forest Plans.

---

## WalkStatus

```python
class WalkStatus(Enum)
```

Status of a Walk.

---

## Participant

```python
class Participant
```

A participant in a Walk (human or agent).

---

## WalkIntent

```python
class WalkIntent
```

The goal of a Walk.

---

## Walk

```python
class Walk
```

Durable work stream tied to Forest plans.

### Examples
```python
>>> walk = Walk.create(
```
```python
>>> walk.advance(mark)
```
```python
>>> walk.transition_phase(NPhase.ACT)
```

---

## WalkStore

```python
class WalkStore
```

Persistent storage for Walks.

---

## get_walk_store

```python
def get_walk_store() -> WalkStore
```

Get the global walk store.

---

## reset_walk_store

```python
def reset_walk_store() -> None
```

Reset the global walk store (for testing).

---

## human

```python
def human(cls, name: str, role: str='orchestrator') -> Participant
```

Create a human participant.

---

## agent

```python
def agent(cls, name: str, trust_level: int=0, role: str='contributor') -> Participant
```

Create an agent participant.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Participant
```

Create from dictionary.

---

## create

```python
def create(cls, description: str, intent_type: str='implement') -> WalkIntent
```

Create a new intent.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> WalkIntent
```

Create from dictionary.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize phase history if empty.

---

## create

```python
def create(cls, goal: str | WalkIntent, root_plan: PlanPath | str | None=None, name: str='', initial_phase: NPhase=NPhase.SENSE) -> Walk
```

Create a new Walk.

---

## advance

```python
def advance(self, mark: Mark) -> None
```

Add a Mark to this Walk.

---

## trace_count

```python
def trace_count(self) -> int
```

Get the number of traces in this Walk.

---

## mark_count

```python
def mark_count(self) -> int
```

Backwards compat: alias for trace_count().

---

## can_transition

```python
def can_transition(self, to_phase: NPhase) -> bool
```

Check if transition to the given phase is valid.

---

## transition_phase

```python
def transition_phase(self, to_phase: NPhase, force: bool=False) -> bool
```

Transition to a new N-Phase.

---

## get_phase_duration

```python
def get_phase_duration(self, phase: NPhase) -> float
```

Get total time spent in a phase (in seconds).

---

## add_participant

```python
def add_participant(self, participant: Participant) -> None
```

Add a participant to this Walk.

---

## get_participant

```python
def get_participant(self, participant_id: str) -> Participant | None
```

Get a participant by ID.

---

## pause

```python
def pause(self) -> None
```

Pause this Walk.

---

## resume

```python
def resume(self) -> None
```

Resume a paused Walk.

---

## complete

```python
def complete(self) -> None
```

Mark this Walk as complete.

---

## abandon

```python
def abandon(self, reason: str='') -> None
```

Abandon this Walk.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for persistence.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Walk
```

Create from dictionary.

---

## duration_seconds

```python
def duration_seconds(self) -> float
```

Total duration of the Walk in seconds.

---

## is_active

```python
def is_active(self) -> bool
```

Check if the Walk is active.

---

## is_complete

```python
def is_complete(self) -> bool
```

Check if the Walk is complete.

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## add

```python
def add(self, walk: Walk) -> None
```

Add a Walk to the store.

---

## get

```python
def get(self, walk_id: WalkId) -> Walk | None
```

Get a Walk by ID.

---

## active_walks

```python
def active_walks(self) -> list[Walk]
```

Get all active Walks.

---

## recent_walks

```python
def recent_walks(self, limit: int=10) -> list[Walk]
```

Get most recent Walks.

---

## save

```python
def save(self, path: Path | str) -> None
```

Save to JSON file.

---

## load

```python
def load(cls, path: Path | str) -> WalkStore
```

Load from JSON file.

---

## services.witness.watchers.__init__

## __init__

```python
module __init__
```

Witness Event Sources (Watchers).

---

## services.witness.watchers.agentese

## agentese

```python
module agentese
```

AgenteseWatcher: Event-Driven Cross-Jewel Visibility.

---

## AgenteseConfig

```python
class AgenteseConfig
```

Configuration for AgenteseWatcher.

---

## parse_agentese_path

```python
def parse_agentese_path(topic: str) -> tuple[str, str, str | None]
```

Parse an AGENTESE topic into (path, aspect, jewel).

### Examples
```python
>>> "world.town.citizen.create" → ("world.town.citizen", "create", "Town")
```
```python
>>> "self.memory.capture" → ("self.memory", "capture", "Brain")
```
```python
>>> "unknown.path.action" → ("unknown.path", "action", None)
```

---

## parse_agentese_path_with_config

```python
def parse_agentese_path_with_config(topic: str, config: AgenteseConfig) -> tuple[str, str, str | None]
```

Parse with custom config (for testing).

---

## AgenteseWatcher

```python
class AgenteseWatcher(BaseWatcher[AgenteseEvent])
```

Event-driven AGENTESE watcher.

---

## create_agentese_watcher

```python
def create_agentese_watcher(bus: 'WitnessSynergyBus | None'=None, patterns: tuple[str, ...] | None=None) -> AgenteseWatcher
```

Create a configured AGENTESE watcher.

---

## services.witness.watchers.base

## base

```python
module base
```

BaseWatcher: Common Infrastructure for Event-Driven Watchers.

---

## WatcherState

```python
class WatcherState(Enum)
```

State of any watcher.

---

## WatcherStats

```python
class WatcherStats
```

Statistics for watchers (shared across all types).

---

## BaseWatcher

```python
class BaseWatcher(ABC, Generic[E])
```

Abstract base class for all Witness watchers.

### Examples
```python
>>> class MyWatcher(BaseWatcher[MyEvent]):
```

---

## record_event

```python
def record_event(self) -> None
```

Record an event emission.

---

## record_error

```python
def record_error(self) -> None
```

Record an error.

---

## add_handler

```python
def add_handler(self, handler: Callable[[E], None]) -> None
```

Add an event handler.

---

## remove_handler

```python
def remove_handler(self, handler: Callable[[E], None]) -> None
```

Remove an event handler.

---

## start

```python
async def start(self) -> None
```

Start the watcher.

---

## stop

```python
async def stop(self) -> None
```

Stop the watcher gracefully.

---

## watch

```python
async def watch(self) -> AsyncIterator[E]
```

Async iterator interface for event consumption.

---

## services.witness.watchers.ci

## ci

```python
module ci
```

CIWatcher: Poll-Based GitHub Actions Monitoring.

---

## CIConfig

```python
class CIConfig
```

Configuration for CIWatcher.

---

## WorkflowRun

```python
class WorkflowRun
```

Parsed workflow run from GitHub API.

---

## fetch_workflow_runs

```python
async def fetch_workflow_runs(owner: str, repo: str, token: str | None=None, per_page: int=10) -> tuple[list[WorkflowRun], int, int]
```

Fetch recent workflow runs from GitHub API.

---

## CIWatcher

```python
class CIWatcher(BaseWatcher[CIEvent])
```

Poll-based GitHub Actions watcher.

---

## create_ci_watcher

```python
def create_ci_watcher(owner: str='', repo: str='', token: str | None=None, poll_interval: float=60.0) -> CIWatcher
```

Create a configured CI watcher.

---

## services.witness.watchers.filesystem

## filesystem

```python
module filesystem
```

FileSystemWatcher: Event-Driven File System Monitoring.

---

## FileSystemConfig

```python
class FileSystemConfig
```

Configuration for FileSystemWatcher.

---

## Debouncer

```python
class Debouncer
```

Time-based debouncer for file events.

---

## PatternMatcher

```python
class PatternMatcher
```

Glob-based pattern matcher for file paths.

---

## FileSystemWatcher

```python
class FileSystemWatcher(BaseWatcher[FileEvent])
```

Event-driven file system watcher.

---

## create_filesystem_watcher

```python
def create_filesystem_watcher(path: Path | None=None, include: tuple[str, ...]=('*.py', '*.tsx', '*.ts'), exclude: tuple[str, ...]=('__pycache__', '.git', 'node_modules'), debounce: float=0.5) -> FileSystemWatcher
```

Create a configured filesystem watcher.

---

## for_python

```python
def for_python(cls, path: Path | None=None) -> 'FileSystemConfig'
```

Preset for Python projects.

---

## for_typescript

```python
def for_typescript(cls, path: Path | None=None) -> 'FileSystemConfig'
```

Preset for TypeScript projects.

---

## should_emit

```python
def should_emit(self, path: str) -> bool
```

Check if enough time has passed since last event for this path.

---

## clear

```python
def clear(self) -> None
```

Clear all debounce state.

---

## matches

```python
def matches(self, path: str) -> bool
```

Check if path matches include patterns and doesn't match exclude.

---

## Handler

```python
class Handler(FileSystemEventHandler)
```

Watchdog event handler that filters and enqueues events.

---

## services.witness.watchers.git

## git

```python
module git
```

GitWatcher: Event-Driven Git Monitoring.

---

## get_git_head

```python
async def get_git_head() -> str | None
```

Get current HEAD SHA.

---

## get_git_branch

```python
async def get_git_branch() -> str | None
```

Get current branch name.

---

## get_commit_info

```python
async def get_commit_info(sha: str) -> dict[str, str]
```

Get info about a specific commit.

---

## get_recent_commits

```python
async def get_recent_commits(since: datetime) -> list[str]
```

Get commits since a given time.

---

## GitWatcher

```python
class GitWatcher(BaseWatcher[GitEvent])
```

Event-driven git watcher.

---

## create_git_watcher

```python
def create_git_watcher(repo_path: Path | None=None, poll_interval: float=5.0) -> GitWatcher
```

Create a configured git watcher.

---

## services.witness.watchers.git_flux

## git_flux

```python
module git_flux
```

GitWatcherFlux: Flux-Lifted GitWatcher for Event-Driven Streaming.

---

## GitFluxState

```python
class GitFluxState(Enum)
```

Lifecycle states for GitWatcherFlux.

---

## GitWatcherProtocol

```python
class GitWatcherProtocol(Protocol)
```

Protocol for GitWatcher-like objects (for testing).

---

## GitWatcherFlux

```python
class GitWatcherFlux
```

Flux-lifted GitWatcher for event-driven streaming.

---

## create_git_watcher_flux

```python
def create_git_watcher_flux(watcher: GitWatcherProtocol) -> GitWatcherFlux
```

Create a GitWatcherFlux from a GitWatcher.

---

## start

```python
async def start(self) -> AsyncIterator['GitEvent']
```

Start streaming events from the underlying watcher.

---

## stop

```python
async def stop(self) -> None
```

Signal stop and cleanup watcher.

---

## state

```python
def state(self) -> GitFluxState
```

Current lifecycle state.

---

## services.witness.watchers.test_watcher

## test_watcher

```python
module test_watcher
```

TestWatcher: Event-Driven Pytest Result Monitoring.

---

## get_test_event_queue

```python
def get_test_event_queue() -> Queue[TestEvent]
```

Get the global test event queue.

---

## reset_test_event_queue

```python
def reset_test_event_queue() -> None
```

Reset the queue (for testing).

---

## TestWatcherConfig

```python
class TestWatcherConfig
```

Configuration for TestWatcher.

---

## TestWatcherPlugin

```python
class TestWatcherPlugin
```

Pytest plugin that captures test events and pushes to queue.

---

## TestWatcher

```python
class TestWatcher(BaseWatcher[TestEvent])
```

Event-driven test result watcher.

---

## create_test_watcher

```python
def create_test_watcher(capture_passed: bool=True, max_error_length: int=500) -> TestWatcher
```

Create a configured test watcher.

---

## create_test_plugin

```python
def create_test_plugin(capture_passed: bool=True, capture_individual: bool=True, max_error_length: int=500) -> TestWatcherPlugin
```

Create a configured pytest plugin.

---

## pytest_sessionstart

```python
def pytest_sessionstart(self, session: 'pytest.Session') -> None
```

Called at session start.

---

## pytest_runtest_logreport

```python
def pytest_runtest_logreport(self, report: Any) -> None
```

Called for each test phase (setup, call, teardown).

---

## pytest_sessionfinish

```python
def pytest_sessionfinish(self, session: 'pytest.Session', exitstatus: int) -> None
```

Called at session end.

---

## services.witness.workflows

## workflows

```python
module workflows
```

Witness Workflow Templates: Pre-Built Cross-Jewel Patterns.

---

## WorkflowCategory

```python
class WorkflowCategory(Enum)
```

Categories of workflow templates.

---

## WorkflowTemplate

```python
class WorkflowTemplate
```

A pre-built workflow template.

---

## get_workflow

```python
def get_workflow(name: str) -> WorkflowTemplate | None
```

Get a workflow template by name.

---

## list_workflows

```python
def list_workflows(category: WorkflowCategory | None=None, max_trust: int | None=None) -> list[WorkflowTemplate]
```

List available workflow templates.

---

## search_workflows

```python
def search_workflows(tag: str) -> list[WorkflowTemplate]
```

Search workflows by tag.

---

## extend_workflow

```python
def extend_workflow(base: WorkflowTemplate, *extensions: Step) -> Pipeline
```

Extend a workflow template with additional steps.

---

## chain_workflows

```python
def chain_workflows(*templates: WorkflowTemplate) -> Pipeline
```

Chain multiple workflow templates together.

---

## __call__

```python
def __call__(self, **kwargs: Any) -> Pipeline
```

Get the pipeline with optional parameter overrides.

---

*2277 symbols, 203 teaching moments*

*Generated by Living Docs — 2025-12-21*