# kgents

> *"The noun is a lie. There is only the rate of change."*

Agents are morphisms in a category. They compose. They observe. They become.

## Feel It

```python
@agent
async def parse(s: str) -> int:
    return int(s)

@agent
async def double(x: int) -> int:
    return x * 2

pipe = parse >> double  # Category theory made practical
result = await pipe.invoke("21")  # 42

# Laws are verified, not aspirational
# (f >> g) >> h == f >> (g >> h) ← BootstrapWitness.verify_composition_laws()
```

## Install

```bash
git clone https://github.com/kentgang/kgents.git && cd kgents
uv sync && kg --help
```
Python 3.12+. That's it.

## Explore

| What | Where |
|------|-------|
| Zero to agent | [docs/quickstart.md](docs/quickstart.md) |
| The seven principles | [spec/principles.md](spec/principles.md) |
| The 13 skills | [docs/skills/](docs/skills/) |
| How it works | [docs/architecture-overview.md](docs/architecture-overview.md) |

## The Garden

Ship-ready: **Brain**, **Gardener**, **Gestalt**, **Forge**
Growing: **Town** (70%), **Park** (60%), **Witness** (75%)

11,170+ tests. Strict mypy. Category laws verified at runtime.

---
MIT | [Contributing](CONTRIBUTING.md) | [Changelog](CHANGELOG.md) — *"The persona is a garden, not a museum."*
