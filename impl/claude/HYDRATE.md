# HYDRATE: Session Context

> *"The gotchas you don't read are the bugs you will write."*

---

## FIRST: Get Task-Relevant Gotchas

Before touching code, run:

```bash
kg docs hydrate "<your task>"
```

Example:
```bash
kg docs hydrate "fix brain persistence"
kg docs hydrate "implement wasm projector"
kg docs hydrate "add new AGENTESE node"
```

This surfaces:
- **Critical gotchas** for your specific task
- **Files you'll likely touch**
- **Voice anchors** to preserve Kent's intent

For file-specific work:
```bash
kg docs relevant services/brain/persistence.py
```

---

## Voice Anchors (Preserve These)

> "Daring, bold, creative, opinionated but not gaudy"
> "The Mirror Test: Does K-gent feel like me on my best day?"
> "Tasteful > feature-complete"
> "The persona is a garden, not a museum"

---

## Quick Reference

```bash
# Get gotchas for your task
kg docs hydrate "<task>"

# Get gotchas for a file
kg docs relevant <path>

# Backend quality gate
cd impl/claude && uv run pytest -q && uv run mypy .

# Frontend quality gate
cd impl/claude/web && npm run typecheck && npm run lint
```

---

*"The proof IS the decision. The mark IS the witness."*
