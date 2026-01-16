# Supplementary Examples

> *"Joy-inducing > merely functional"*

These supplementary examples demonstrate additional patterns. For the **canonical learning path**, see [examples/](../../examples/README.md).

---

## Supplementary Examples

Each example is <50 lines and runs standalone from the repo root:

```bash
cd impl/claude && python ../../docs/examples/composition.py
```

| File | What It Demonstrates |
|------|---------------------|
| `composition.py` | PolyAgent composition via `sequential()` |
| `operad_laws.py` | Operad verifying associativity laws |
| `voice_gate.py` | Anti-sausage protocol preserving voice |
| `trust_levels.py` | Witness trust escalation L0→L3 |
| `warp_traces.py` | TraceNode causality primitives |

### Run All

```bash
cd impl/claude
for f in ../../docs/examples/*.py; do python "$f"; done
```

---

## Main Examples

For the progressive learning path (5 examples, ~45 minutes):

**[examples/](../../examples/README.md)**
- 01: Hello Composition (category laws)
- 02: Galois Oracle (failure prediction)
- 03: Witness Trace (reasoning chains)
- 04: AGENTESE Observer (observer-dependent semantics)
- 05: Constitutional Check (7 principles, ethical floor)

---

*"The persona is a garden, not a museum."*
