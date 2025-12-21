# NOW.md — What's Happening

> *Updated each session. No metadata. Just truth.*
> *Claude reads this first, updates it before ending.*

---

## Current Work

**CROWN JEWEL CLEANUP** — Major pruning. Removing Town, Park, Forge, Gestalt, Witness, Differance, Chat, Cockpit, Workshop, Emergence UI. Keeping Brain, Galleries, OS-Shell. See `plans/crown-jewel-cleanup.md`.

| Status | Progress |
|--------|----------|
| Frontend pages | 17 pages deleted (Canvas, Chat, Cockpit, DesignSystem, Differance, Emergence, Forge, Gestalt, Inhabit, ParkScenario, Soul, Town×4, Witness, Workshop) |
| Frontend components | ~100 component files deleted (17 directories) |
| Shell updates | CrownJewelsSection → Brain only, ToolsSection removed, registry simplified |
| Staged | ~5000 lines deleted, cleanup in progress |

---

**ASHC WORK** — New ashc service with checker and obligation modules. Interactive text gallery added.

| Item | Status |
|------|--------|
| `services/ashc/checker.py` | NEW (untracked) |
| `services/ashc/obligation.py` | NEW (untracked) |
| `services/interactive_text/` | service.py added, node.py untracked |
| Interactive Text Gallery | Page live at `/_/gallery/interactive-text` |

---

## Crown Jewel Status

| Jewel | % | One-liner |
|-------|---|-----------|
| Brain | 100 | Spatial cathedral of memory. Ship-ready. THE crown jewel. |
| Interactive Text | 75 | Gallery showcase for text rendering. |
| Living Docs | 90 | `concept.docs`, `self.docs`, `self.document` nodes. |
| Liminal | 80 | `time.coffee` morning ritual personality. |
| OS-Shell | 100 | Universal AGENTESE rendering. NavigationTree, projections. |
| ~~Town~~ | — | *Removed* |
| ~~Park~~ | — | *Removed* |
| ~~Forge~~ | — | *Removed* |
| ~~Gestalt~~ | — | *Removed* |
| ~~Witness~~ | — | *Removed* |

---

## Quality Gates

| Check | Status |
|-------|--------|
| Frontend typecheck | ✅ Clean |
| Backend mypy | ✅ Notes only (async iterator hints) |
| Backend tests (Brain, Living Docs) | ✅ 222 passing |

---

## What I'm Stuck On

Nothing right now. Cleanup is mechanical.

---

## What I Want Next

1. Complete Crown Jewel cleanup (commit cleanup batch)
2. ashc work: proof generation, session metabolism
3. Build out interactive text capabilities

*"Tasteful > feature-complete. Time to prune the garden."*

---

## Key Completions (Reference)

| Feature | Completion | Documentation |
|---------|------------|---------------|
| **Crown Jewel Cleanup** | 2025-12-21 IN PROGRESS | `plans/crown-jewel-cleanup.md` |
| A-gent Alethic Refactor | 2025-12-21 | `spec/a-gents/README.md` |
| 2D Renaissance | 2025-12-18 | `spec/protocols/2d-renaissance.md` |
| AGENTESE-as-Route | 2025-12-18 | `spec/protocols/agentese-as-route.md` |

---

*Last: 2025-12-21 (Crown Jewel Cleanup - Status Report)*
