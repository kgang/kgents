---
path: docs/skills/proof-verifier-bridge
status: active
progress: 100
last_touched: 2025-12-21
touched_by: claude-opus-4
blocking: []
enables: [ashc, formal-verification, llm-proof-generation]
session_notes: |
  Created from Phase 5 Checker Bridges implementation.
  Critical operational knowledge for Dafny, Lean4, Verus.
phase_ledger:
  PLAN: complete
  ACT: complete
  REFLECT: complete
---

# Skill: Proof Verifier Bridge Patterns

> *"LLM hallucinations don't matter for proofs because proof checkers reject invalid proofs."*
> — Martin Kleppmann

**Difficulty**: Intermediate
**Prerequisites**: `crown-jewel-patterns.md`, async subprocess handling
**Source**: ASHC Proof-Generation Phase 5 implementation
**Spec**: `spec/protocols/checker-bridges.md`, `spec/protocols/proof-generation.md`

---

## Overview

The proof checker is the gatekeeper. LLMs can hallucinate all they want—mechanical verification is the source of truth. This skill covers operational knowledge for three proof verifiers:

| Verifier | Domain | Theorem Prover | Best For |
|----------|--------|----------------|----------|
| **Dafny** | Imperative | Z3 (bundled) | Algorithms, pre/postconditions |
| **Lean4** | Mathematical | Custom kernel | Category theory, formal math |
| **Verus** | Rust systems | Z3 (external) | Memory safety, ownership proofs |

---

## Pattern 1: Checker Protocol

All checkers implement a common protocol:

```python
@runtime_checkable
class ProofChecker(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def is_available(self) -> bool: ...

    async def check(
        self,
        proof_source: str,
        timeout_ms: int = 30000,
    ) -> CheckerResult: ...
```

**Why Protocol over ABC**: Duck typing without inheritance coupling. Any class with these methods works.

**Key Invariants**:
- `is_available` is cached after first check
- `check()` raises `CheckerUnavailable` if `is_available` is False
- Timeout always produces a result (never hangs)

---

## Pattern 2: Lazy Registry

Checkers are expensive to instantiate (subprocess version checks). Use lazy registration:

```python
@dataclass
class CheckerRegistry:
    _checkers: dict[str, type[ProofChecker]] = field(default_factory=dict)
    _instances: dict[str, ProofChecker] = field(default_factory=dict)

    def get(self, name: str) -> ProofChecker:
        if name not in self._instances:
            if name not in self._checkers:
                raise KeyError(f"Unknown checker: {name}")
            self._instances[name] = self._checkers[name]()  # Instantiate on first access
        return self._instances[name]
```

**Why Lazy**: Startup cost avoided when checkers aren't used. Registration is O(1), instantiation on demand.

---

## Pattern 3: Graceful Unavailability

Checkers that aren't installed degrade gracefully:

```python
@property
def is_available(self) -> bool:
    if self._available is None:
        try:
            self._verify_installation()
        except CheckerUnavailable:
            pass  # _available set by _verify_installation
    return self._available or False

async def check(self, proof_source: str, timeout_ms: int) -> CheckerResult:
    if not self.is_available:
        raise CheckerUnavailable(self.name, "Not installed. Install: ...")
    # ... actual verification
```

**Never Hang**: Unavailable checkers raise immediately, never attempt subprocess.

---

## Dafny: Imperative Proofs

### Installation

```bash
# Recommended: dotnet tool
dotnet tool install --global dafny

# VS Code extension auto-installs
code --install-extension dafny-lang.ide-vscode
```

### Command-Line Invocation

```bash
dafny verify file.dfy                     # Verification only
dafny verify --resource-limit 100000 file.dfy  # With resource limit
```

### Critical Gotchas

1. **stderr on success**: Dafny outputs to stderr even when verification succeeds. Parse exit code, not output presence.

2. **Noisy error cascades**: First error is key; subsequent errors often red herrings:
   ```
   Error: A postcondition might not hold.    ← ROOT CAUSE
   Error: This expression has type...        ← CASCADE (ignore)
   Error: Cannot resolve identifier...       ← CASCADE (ignore)
   ```

3. **Timeout unreliability**: `--verification-time-limit` not always respected. Use `--resource-limit` instead:
   ```bash
   # BAD: May not be respected
   dafny verify --verification-time-limit:30 file.dfy

   # GOOD: Reliable bounded verification
   dafny verify --resource-limit:100000 file.dfy
   ```

4. **Platform non-determinism**: Same proof may verify on macOS but timeout on Ubuntu due to Z3 behavior differences.

### Error Patterns to Parse

| Pattern | Meaning |
|---------|---------|
| `error:` or `Error:` | Verification failure |
| `BP5003` | Postcondition might not hold |
| `BP5001` | Precondition might not hold |
| `assertion might not hold` | Assert failure |
| `postcondition might not hold` | Ensures clause failed |

### Trivial Test Proof

```dafny
lemma TrivialTrue()
    ensures true
{}
```

---

## Lean4: Mathematical Proofs

### Installation

```bash
# Install elan (Lean version manager)
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# Verify
lake --version
```

**AVOID Homebrew**: The `brew install lean` formula lags significantly behind official releases.

### Command-Line Invocation

```bash
# For standalone files (no project)
lean file.lean

# For project files (ALWAYS use this)
lake env lean file.lean
```

**Critical Difference**:
- `lean`: Bare compiler, may not find project dependencies
- `lake env lean`: Sets up project environment, finds imports

### Mathlib Cache (Essential)

Building mathlib from source: **20+ minutes**
With cache: **seconds**

```bash
# After cloning a mathlib-using project
lake exe cache get

# Force redownload
lake exe cache get!

# If cache fails, clean and retry
lake clean
rm -rf .lake
lake exe cache get
```

### Sorry Handling

`sorry` is an incomplete proof marker that admits any statement:

```lean
theorem incomplete : 1 = 2 := sorry  -- Compiles but is UNPROVEN
```

**ASHC treats `sorry` as FAILED**. A proof with sorry is incomplete.

### Error Patterns to Parse

| Pattern | Meaning |
|---------|---------|
| `error:` | Syntax or type error |
| `unsolved goals` | Tactic didn't complete proof |
| `type mismatch` | Type error in proof term |
| `unknown identifier` | Unbound name |

### Trivial Test Proof

```lean
theorem trivial : forall x : Nat, x = x := fun _ => rfl
```

---

## Verus: Rust Verification

### Installation

```bash
# Download release
wget https://github.com/verus-lang/verus/releases/download/.../verus-x86-macos.zip
unzip verus-*.zip

# macOS: Remove quarantine
./tools/remove-quarantine.sh

# Install correct Z3 version
./tools/get-z3.sh
```

### Z3 Version Management

Verus expects specific Z3 versions:
```
Error: Verus expects z3 version '4.12.5', found version '4.13.0'
```

**Solutions**:
1. Run `./tools/get-z3.sh` (recommended)
2. Use `--no-solver-version-check` (not recommended)

### Command-Line Invocation

```bash
verus file.rs                  # Direct verification
cargo verus verify             # Through cargo
```

### The `verus!` Macro (Critical)

All verified code must be inside `verus!`:

```rust
// WRONG - verus! inside impl is SILENTLY IGNORED
impl MyStruct {
    verus! {  // <- This does NOTHING!
        proof fn my_proof() { ... }
    }
}

// CORRECT - wrap entire impl
verus! {
    impl MyStruct {
        proof fn my_proof() { ... }
    }
}
```

**This is a critical gotcha**: The wrong pattern compiles without error but shows "0 verified".

### Code Modes

| Mode | Compiles? | Purpose |
|------|-----------|---------|
| `exec` | Yes | Normal Rust code |
| `spec` | No | Specifications only |
| `proof` | No | Proof code |
| `ghost` | No | Ghost values (can copy non-Copy) |
| `tracked` | No | Linear type tracking |

### Error Patterns to Parse

| Pattern | Meaning |
|---------|---------|
| `error:` or `error[EXXXX]` | Compilation error |
| `verification failed` | Proof doesn't hold |
| `precondition not satisfied` | Requires clause violated |
| `postcondition not satisfied` | Ensures clause violated |

### Trivial Test Proof

```rust
use vstd::prelude::*;

verus! {
    proof fn trivial()
        ensures true
    {
    }
}
```

---

## Pattern 4: Async Subprocess with Timeout

Never let a subprocess hang. Always use timeout + kill:

```python
async def check(self, proof_source: str, timeout_ms: int) -> CheckerResult:
    proc = await asyncio.create_subprocess_exec(
        self._binary_path,
        temp_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout_ms / 1000,
        )
    except asyncio.TimeoutError:
        proc.kill()         # Kill the process
        await proc.wait()   # Reap the zombie (ESSENTIAL)
        return CheckerResult(success=False, errors=("Verification timeout",), ...)
```

**Why `await proc.wait()`**: Without it, killed process becomes zombie. Reaping is essential.

---

## Pattern 5: Temp File Cleanup

Always clean up, even on exceptions:

```python
temp_path: str | None = None
try:
    fd, temp_path = tempfile.mkstemp(suffix=".dfy", prefix="ashc_proof_")
    os.write(fd, proof_source.encode("utf-8"))
    os.close(fd)
    # ... use temp file
except OSError as e:
    raise CheckerError(...)
finally:
    if temp_path and os.path.exists(temp_path):
        try:
            os.unlink(temp_path)
        except OSError:
            pass  # Best effort cleanup
```

**Why try/finally**: Exceptions happen. Temp files must be cleaned regardless.

---

## Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Pattern |
|--------------|----------------|-----------------|
| Blocking subprocess.run | Blocks event loop | asyncio.create_subprocess_exec |
| Parsing output for success | stderr on success | Parse exit code |
| Hardcoded timeouts | Can't adapt to proof complexity | Accept timeout_ms parameter |
| No zombie reaping | Process table fills | await proc.wait() after kill |
| Silent failure on unavailable | Confusing debugging | Raise CheckerUnavailable explicitly |
| Time limits for Dafny | Not reliable | Use resource limits |
| verus! inside impl | Silently ignored | Wrap entire impl |

---

## Comparison Table

| Feature | Dafny | Lean4 | Verus |
|---------|-------|-------|-------|
| Theorem Prover | Z3 (bundled) | Custom kernel | Z3 (external) |
| Installation | dotnet tool | elan + lake | rustup + verus + Z3 |
| Main CLI | `dafny verify` | `lake env lean` | `verus` / `cargo verus` |
| Timeout Reliability | Unreliable | N/A (deterministic) | Unreliable (Z3) |
| Cache System | None | Essential (mathlib) | None |
| Critical Gotcha | Noisy error cascades | Exact toolchain matching | verus! impl placement |

---

## Testing Without Checkers

Use MockChecker for unit tests:

```python
checker = MockChecker(default_success=True)
checker.always_fail_on(r"ensures\s+false")  # Pattern matching

result = await checker.check("lemma Bad() ensures false {}")
assert not result.success
```

Integration tests use `@pytest.mark.skipif`:

```python
requires_dafny = pytest.mark.skipif(
    not dafny_available(),
    reason="Dafny not installed",
)

@requires_dafny
async def test_verifies_proof():
    checker = DafnyChecker()
    result = await checker.check("lemma Test() ensures true {}")
    assert result.success
```

---

## Cross-References

- **Implementation**: `services/ashc/checker.py`
- **Tests**: `services/ashc/_tests/test_checker.py`
- **Contracts**: `services/ashc/contracts.py`
- **Spec**: `spec/protocols/checker-bridges.md`
- **Parent**: `spec/protocols/proof-generation.md`

---

*"The proof checker is the gatekeeper. If the proof checks, the theorem holds. The LLM can hallucinate all it wants—mechanical verification is the source of truth."*
