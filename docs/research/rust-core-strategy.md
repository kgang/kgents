# Rust Core Strategy: kgents Categorical Kernel

> *"Servo supplies the surface; Rust supplies the laws."*

**Date**: 2025-12-20
**Status**: 📋 **PLANNED** — Python WARP primitives complete; Rust kernel is performance optimization layer
**Recommendation**: Hybrid approach — Rust for law-critical paths, Python for orchestration

---

## Executive Summary

**Decision**: Hybrid Rust kernel with PyO3 bindings (future optimization layer).

**Current State**: All WARP primitives are implemented in Python (`services/witness/`):
- TraceNode, Walk, Ritual, Offering, Intent, Covenant, Terrace, VoiceGate
- 30+ test files, production-ready

**Future Rust Layer**: Build a `kgents-core` Rust crate that owns:
1. **Operad law checking** (compile-time guarantees where possible)
2. **TraceNode ledger** (append-only, zero-copy, immutable)
3. **Covenant enforcement** (capability gating, budget enforcement)

Keep Python for:
1. **AGENTESE gateway** (routing, discovery)
2. **Crown Jewel orchestration** (business logic)
3. **LLM integration** (K-gent, Muse)

---

## Trade-off Matrix

| Component | Rust Benefit | Python Cost | Recommendation |
|-----------|--------------|-------------|----------------|
| **Operad law checking** | Compile-time associativity/identity proofs | FFI overhead on hot path | RUST |
| **TraceNode ledger** | Zero-copy, append-only, immutable | Serialize/deserialize at boundary | RUST |
| **Covenant enforcement** | Memory-safe capability checks | Simpler logic in Python | RUST |
| **AGENTESE routing** | Fast dispatch | Minimal latency gain | PYTHON |
| **LLM orchestration** | None | Python ecosystem dominance | PYTHON |
| **Crown Jewel logic** | None | Rapid iteration needed | PYTHON |

---

## PyO3 Patterns for kgents

### Frozen Types (Primary Pattern)

PyO3's `#[pyclass(frozen)]` maps to kgents' immutable dataclasses:

```rust
#[pyclass(frozen)]
#[derive(Clone)]
pub struct TraceNode {
    #[pyo3(get)]
    pub id: String,
    #[pyo3(get)]
    pub origin: String,
    #[pyo3(get)]
    pub timestamp: i64,
    // ... other fields
}
```

Benefits:
- Simpler `.get()` access (no borrow checking at runtime)
- Thread-safe by default
- Matches Python `@dataclass(frozen=True)` semantics

### Interior Mutability (For Accumulators)

For TraceNode ledger accumulation:

```rust
#[pyclass(frozen)]
pub struct TraceBuffer {
    inner: Arc<Mutex<Vec<TraceNode>>>,
}

#[pymethods]
impl TraceBuffer {
    fn append(&self, node: TraceNode) {
        self.inner.lock().unwrap().push(node);
    }
}
```

### Law Verification (Compile-Time)

Encode operad laws as traits:

```rust
pub trait Operad {
    type Operation;

    fn compose(&self, a: &Self::Operation, b: &Self::Operation) -> Self::Operation;
    fn identity(&self) -> Self::Operation;

    // Laws verified by type system:
    // compose(identity(), op) == op
    // compose(op, identity()) == op
    // compose(compose(a, b), c) == compose(a, compose(b, c))
}
```

---

## Architecture: kgents-core Crate

### Structure

```
kgents-core/
├── src/
│   ├── lib.rs          # PyO3 module registration
│   ├── operad/
│   │   ├── mod.rs
│   │   ├── laws.rs     # Law verification traits
│   │   └── compose.rs  # Composition engine
│   ├── trace/
│   │   ├── mod.rs
│   │   ├── node.rs     # TraceNode definition
│   │   ├── ledger.rs   # Append-only buffer
│   │   └── query.rs    # TraceNode queries
│   └── covenant/
│       ├── mod.rs
│       ├── gate.rs     # Capability gating
│       └── budget.rs   # Budget enforcement
├── Cargo.toml
└── pyproject.toml      # Maturin config
```

### Python Integration

```python
# Python side
from kgents_core import TraceNode, TraceLedger, verify_operad_laws

# Create nodes (immutable, frozen)
node = TraceNode(id="abc", origin="brain", timestamp=1234567890)

# Append to ledger (interior mutability)
ledger = TraceLedger()
ledger.append(node)

# Verify operad laws (compile-time guarantees exposed to runtime)
assert verify_operad_laws(my_operad)  # Raises if laws violated
```

---

## Performance Expectations

| Operation | Python Baseline | Rust + PyO3 | Speedup |
|-----------|-----------------|-------------|---------|
| TraceNode creation | 2μs | 0.3μs | ~6x |
| Ledger append (1M nodes) | 1.2s | 80ms | ~15x |
| Operad law check | 500μs | 20μs | ~25x |
| Covenant gate check | 50μs | 5μs | ~10x |

**Note**: These are estimates. Actual benchmarks needed after implementation.

---

## Implementation Roadmap (Future — When Performance Requires)

**Prerequisite**: Python WARP primitives are already complete and tested. This roadmap executes when performance profiling indicates need.

### Phase 1: Foundation (1-2 weeks)
- [ ] Create `kgents-core` crate with Maturin setup
- [ ] Implement `TraceNode` frozen struct (Rust port of `trace_node.py`)
- [ ] Implement `TraceLedger` with interior mutability
- [ ] Basic pytest integration tests

### Phase 2: Operad Laws (1 week)
- [ ] Define `Operad` trait with law verification
- [ ] Implement compile-time law checking macros
- [ ] Expose `verify_operad_laws()` to Python
- [ ] Wire into existing PolyAgent/Operad tests

### Phase 3: Covenant Enforcement (1 week)
- [ ] Implement `Covenant` struct (Rust port of `covenant.py`)
- [ ] Implement `CovenantGate` for capability checks
- [ ] Implement `Budget` tracking
- [ ] Wire into WitnessNode trust system

### Phase 4: Integration (1 week)
- [ ] Replace Python TraceNode with Rust version (swap, not rebuild)
- [ ] Add ledger persistence (append-only file)
- [ ] Performance benchmarks
- [ ] CI integration

---

## Anti-Sausage Check

- Did I hedge with "maybe Rust"? **No — committed to hybrid: Rust for laws, Python for orchestration.**
- Is the boundary clear? **Yes — laws/ledger/covenant in Rust; routing/LLM/business logic in Python.**
- Does it align with categorical foundation? **Yes — Operad laws enforced at compile time.**

---

## Sources

- [PyO3 User Guide: Frozen Classes](https://pyo3.rs/main/class.html)
- [PyO3 GitHub](https://github.com/PyO3/pyo3)
- [Maturin Documentation](https://www.maturin.rs/)
- [Efficiently Extending Python with PyO3 and Rust](https://www.blueshoe.io/blog/python-rust-pyo3/)

---

*"Spec is compression; design should generate implementation."* — Constitution §7
