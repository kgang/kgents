# Documentation Radical Vision

> *"Don't enumerate the flowers. Describe the garden's grammar."*

---

## The Essence

The current docs are *good* but conventional. They talk ABOUT kgents principles but don't EMBODY them. Transformative documentation would:

1. **Be radically minimal** — 50-line README, everything else discovered through exploration
2. **Follow AGENTESE structure** — docs/ organized by the five contexts (world, self, concept, void, time)
3. **Be executable** — every example runs via `kg docs run <name>`
4. **Show ghosts** — alternatives that almost happened, making judgment visible
5. **Make the garden literal** — seasons in changelog, plots in skills

---

## Priority Implementation

### Phase 1: The 50-Line README

Compress README.md to radical minimalism:
- One quote
- One code example
- One install command
- Three links
- One closing aphorism

Everything else is discovered, not read.

### Phase 2: AGENTESE-Structured Docs

Restructure `docs/` into five contexts:

```
docs/
├── world/      # External-facing (visitors, evaluators)
├── self/       # Internal (developers in the codebase)
├── concept/    # Abstract (theory, philosophy, principles)
├── void/       # Accursed share (experiments, ghosts, graveyard)
└── time/       # Temporal (changelog, roadmap, archaeology)
```

### Phase 3: Executable Examples

Create `docs/examples/*.py` that are BOTH documentation AND runnable:
- `kg docs run quickstart`
- `kg docs run composition`
- `kg docs run functors`

### Phase 4: Ghost Layer

Add `<details>` blocks to major decisions showing what we almost did and why we didn't.

---

## Voice Anchors (Quote Directly)

- *"Daring, bold, creative, opinionated but not gaudy"*
- *"The Mirror Test: Does K-gent feel like me on my best day?"*
- *"Tasteful > feature-complete; Joy-inducing > merely functional"*
- *"The persona is a garden, not a museum"*

---

## Relevant Files

| File | Purpose |
|------|---------|
| [plans/docs-renaissance.md](docs-renaissance.md) | Initial audit and conventional improvements |
| [README.md](../README.md) | Current README (personality-infused but still long) |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | New contributor guide |
| [docs/quickstart.md](../docs/quickstart.md) | Current quickstart |
| [spec/principles.md](../spec/principles.md) | The seven principles + 12 ADs |
| [plans/_focus.md](_focus.md) | Human intent (voice anchors) |

---

## Anti-Sausage Check

Before any doc change, ask:
- ❓ *Did I smooth anything that should stay rough?*
- ❓ *Is this still daring, bold, creative—or did I make it safe?*
- ❓ *Does the structure embody the principles, or just describe them?*

---

## The Test

A visitor should be able to:
1. Understand the philosophy in 30 seconds (README)
2. Run something in 60 seconds (install + first command)
3. Explore without reading (REPL, tour, discovery)
4. Go deep only when they choose to

*"We don't explain everything. You explore."*

---

*Created: 2025-12-20*
