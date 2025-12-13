---
path: devex/gallery
status: planned
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: [devex/playground]
enables: []
session_notes: |
  Plan created from strategic recommendations.
  Priority 4 of 6 DevEx improvements.
  Blocked by playground (shares examples content).
---

# Example Gallery: Static Documentation Site

> *"Visual discovery path for new users."*

**Goal**: Static site showcasing examples with syntax highlighting, screenshots, and copy-paste code.
**Priority**: 4 (medium impact, low effort)
**Blocked by**: `devex/playground` (shares example content)

---

## The Problem

The 5 examples in `agents/examples/` are hidden in the codebase. Nobody knows they exist unless they explore the directory structure.

---

## The Solution

A static site (MkDocs + Material theme) at `docs/` or GitHub Pages:

```
┌─────────────────────────────────────────────────────────────────┐
│ kgents examples                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                │
│ │ Hello World │ │ Composition │ │ Maybe Lift  │                │
│ │ ───────────│ │ ───────────│ │ ───────────│                │
│ │ Your first  │ │ Pipe agents │ │ Handle      │                │
│ │ agent       │ │ together    │ │ optionals   │                │
│ │             │ │             │ │             │                │
│ │ [Run →]     │ │ [Run →]     │ │ [Run →]     │                │
│ └─────────────┘ └─────────────┘ └─────────────┘                │
│                                                                  │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                │
│ │ K-gent      │ │ Flux Stream │ │ Full Stack  │                │
│ │ Dialogue    │ │ Processing  │ │ (Kappa)     │                │
│ │ ───────────│ │ ───────────│ │ ───────────│                │
│ │ Chat with   │ │ Real-time   │ │ Production  │                │
│ │ persona     │ │ events      │ │ service     │                │
│ │ [Run →]     │ │ [Run →]     │ │ [Run →]     │                │
│ └─────────────┘ └─────────────┘ └─────────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Each example card links to:
1. **Full code** with syntax highlighting
2. **Explanation** of concepts used
3. **Run command** (`kgents play 1`)

---

## Research & References

### MkDocs + Material
- Fast, simple static site generator for documentation
- Markdown source, YAML config
- Material theme: sleek, responsive, feature-rich
- Code annotations for explanations
- Source: [MkDocs](https://www.mkdocs.org/)
- Source: [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)

### Notable Users
- FastAPI and Pydantic use MkDocs
- Microsoft Engineering Fundamentals Playbook
- Source: [Microsoft MkDocs Guide](https://microsoft.github.io/code-with-engineering-playbook/documentation/recipes/static-website-with-mkdocs/)

### Deployment Options
- GitHub Pages (free, automatic)
- Netlify (free tier)
- Read the Docs (free for open source)

---

## Implementation Outline

### Phase 1: MkDocs Setup (~30 min)
```yaml
# mkdocs.yml
site_name: kgents Examples
theme:
  name: material
  features:
    - content.code.copy
    - content.code.annotate
    - navigation.instant

nav:
  - Home: index.md
  - Examples:
    - Hello World: examples/hello-world.md
    - Composition: examples/composition.md
    - Maybe Lift: examples/maybe-lift.md
    - K-gent Dialogue: examples/kgent.md
    - Flux Streams: examples/flux.md
    - Full Stack: examples/kappa.md
```

### Phase 2: Example Pages (~6 pages × 50 lines)
```markdown
# Hello World

Your first agent in 3 lines.

## Code

```python
from agents import agent

@agent
async def hello(name: str) -> str:
    return f"Hello, {name}!"
```

## Run It

```bash
kgents play 1
```

## What's Happening

1. `@agent` decorator creates an `Agent[str, str]`
2. `invoke()` is the core method
3. Agents are morphisms: input → output

## Next Steps

- [Composition](composition.md) — Pipe agents together
- [Functor Field Guide](../functor-field-guide.md) — Deeper theory
```

### Phase 3: GitHub Actions (~20 LOC)
```yaml
# .github/workflows/docs.yml
name: Deploy docs
on:
  push:
    branches: [main]
    paths: ['docs/**', 'mkdocs.yml']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install mkdocs-material
      - run: mkdocs gh-deploy --force
```

---

## File Structure

```
kgents/
├── mkdocs.yml           # Site config
└── docs/
    ├── index.md         # Landing page
    ├── examples/
    │   ├── hello-world.md
    │   ├── composition.md
    │   ├── maybe-lift.md
    │   ├── kgent.md
    │   ├── flux.md
    │   └── kappa.md
    └── (existing docs)
```

---

## Success Criteria

| Criterion | Metric |
|-----------|--------|
| Site loads | < 2 seconds |
| Code is copy-pasteable | Works first try |
| Mobile responsive | Yes |
| Kent's approval | "This looks professional" |

---

## Testing Strategy

| Test Type | Coverage |
|-----------|----------|
| Build | MkDocs builds without errors |
| Links | No broken links |
| Code | Code blocks execute |
| Manual | Kent reviews on mobile |

---

## Dependencies

- `mkdocs` — Static site generator
- `mkdocs-material` — Theme
- GitHub Pages — Hosting (free)

---

## Cross-References

- **Strategic Recommendations**: `plans/ideas/strategic-recommendations-2025-12-13.md`
- **Playground**: `plans/devex/playground.md` (shares content)
- **Examples**: `agents/examples/`
- **MkDocs**: https://www.mkdocs.org/

---

*"A picture is worth a thousand lines of documentation."*
