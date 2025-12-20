# Executable Examples

> *"Joy-inducing > merely functional"*

Each example is <50 lines and runs standalone from the repo root:

```bash
python docs/examples/composition.py
```

## The Examples

| File | What It Shows |
|------|--------------|
| `composition.py` | PolyAgent composition via `sequential()` |
| `operad_laws.py` | Operad verifying associativity laws |
| `voice_gate.py` | Anti-sausage protocol preserving voice |
| `trust_levels.py` | Witness trust escalation L0→L3 |
| `warp_traces.py` | TraceNode causality primitives |

## Run All

```bash
for f in docs/examples/*.py; do python "$f"; done
```

---

*"The persona is a garden, not a museum."*
