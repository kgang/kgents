# HYDRATE.md - Session Context

## TL;DR

**kgents** = Kent's Agents. Spec-first agent framework with 7 irreducible bootstrap agents.

- `spec/` = Language spec (like Python)
- `impl/claude-openrouter/` = Reference impl (like CPython)
- `impl/zen-agents/` = **Production-ready** zenportal reimplementation

## Current State (Dec 2025)

| Component | Status |
|-----------|--------|
| 7 Principles | ✅ Defined (added Generative) |
| 7 Bootstrap Agents | ✅ Spec + Impl |
| 5 Agent Genera (A,B,C,H,K) | ✅ Implemented |
| zen-agents | ✅ **49 tests** |
| runtime/ | ✅ **LLM-backed** (53 tests) |
| zen-agents UI | ✅ **Phase 4** (Themes + Persistence + Templates) |

## Quick Commands

```bash
# Launch zen-agents TUI
cd impl/zen-agents && uv run zen-agents

# Run demo
cd impl/zen-agents && uv run python demo.py

# Run tests
cd impl/zen-agents && uv run pytest tests/ -v
```

## 7 Bootstrap Agents

| Agent | Symbol | Purpose |
|-------|--------|---------|
| **Id** | λx.x | Identity (composition unit) |
| **Compose** | ∘ | Agent-that-makes-agents |
| **Judge** | ⊢ | Value function (6 principles) |
| **Ground** | ⊥ | Empirical seed (persona + world) |
| **Contradict** | ≢ | Tension detection |
| **Sublate** | ↑ | Hegelian synthesis |
| **Fix** | μ | Fixed-point (self-reference) |

## Directory Map

```
kgents/
├── spec/                    # THE SPECIFICATION
│   ├── principles.md        # 6 core principles
│   ├── bootstrap.md         # 7 irreducible agents
│   └── {a,b,c,h,k}-gents/   # 5 agent genera
├── impl/claude-openrouter/  # Reference implementation
│   ├── bootstrap/           # 7 bootstrap agents (Python)
│   ├── runtime/             # LLM-backed agents (4 auth methods)
│   └── agents/{a,b,c,h,k}/  # 5 genera
└── impl/zen-agents/         # PRODUCTION APP
    ├── zen_agents/          # Core agents + ui/
    ├── pipelines/           # NewSessionPipeline, SessionTickPipeline
    └── tests/               # 49 pytest tests
```

## Key Files

- `impl/zen-agents/demo.py` - Comprehensive demo (13 sections)
- `impl/zen-agents/zen_agents/ui/` - Textual TUI
- `impl/zen-agents/zen_agents/templates.py` - Session templates
- `impl/claude-openrouter/runtime/` - LLM-backed agents
- `spec/bootstrap.md` - Bootstrap agents spec
- `docs/RESEARCH-ZEN-AGENTS-META-ANALYSIS.md` - zen-agents vs zenportal analysis

## Research Findings (Dec 2025)

**zen-agents vs zenportal meta-analysis:**

| Metric | zenportal | zen-agents | Delta |
|--------|-----------|------------|-------|
| LOC | 17,249 | 6,854 | -60% |
| Commits | 100+ organic | 7 spec-driven | spec compresses |

**Validated Principles:**
- **Polling is Fix** — iteration patterns are fixed-point searches
- **Compose, don't concatenate** — `A >> B >> C` not 130-line methods
- **Conflict is Data** — Contradict/Sublate for robustness
- **Spec is Compression** — 60% code reduction from spec-first

**LLM/Human Boundary:**
- Spec + Ground = Human (irreducible)
- Impl = LLM (mechanical translation)
- Polish = Hybrid (accumulated wisdom)

## Recent Changes

- **BOOTSTRAP_PROMPT.md** - Enhanced with LLM/human boundary, idioms, both impl targets
- **Meta-analysis** - zen-agents vs zenportal comparison complete
- **UI Phase 4** - 5 themes, persistence, templates, 49 tests
