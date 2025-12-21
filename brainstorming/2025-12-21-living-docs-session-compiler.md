# Living Docs as Session Compiler

> *"The docs don't describe the code. The docs compile context for the observer."*

**Date**: 2025-12-21
**Status**: Brainstorming
**Trigger**: Phase 6 reimagining — what if Living Docs served Claude and Kent directly?

---

## The Insight

Living Docs is currently **extractive** — it pulls documentation out of source and projects it as static markdown. But the real consumers right now are:

1. **Claude Code** at session start (needs focused context)
2. **Claude Code** during editing (needs relevant gotchas)
3. **Kent** exploring patterns (needs emergent structure)
4. **Kent** preserving voice (needs anti-sausage fuel)

What if Living Docs became **generative** — compiling context specifically optimized for these observers and their tasks?

---

## The Vision: Context Compiler

Same source material, different compilations:

```
                    ┌─────────────────────────────────────┐
                    │         Living Docs Source          │
                    │  (docstrings, specs, teaching, git) │
                    └─────────────────┬───────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │ Session Hydrate │     │  Edit-Time      │     │  Voice Anchors  │
    │                 │     │  Teaching       │     │                 │
    │ Task → Context  │     │  Path → Gotchas │     │ Git → Phrases   │
    └─────────────────┘     └─────────────────┘     └─────────────────┘
              │                       │                       │
              ▼                       ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │ /hydrate skill  │     │ Pre-edit hook   │     │ Session start   │
    │ System prompt   │     │ Claude warning  │     │ Anti-sausage    │
    └─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Capability 1: Session Hydration

**Problem**: Every Claude Code session starts with the same CLAUDE.md, but tasks vary wildly. Working on Brain persistence is different from implementing a new projector.

**Solution**: Task-aware context compilation.

```bash
kg docs hydrate "implement marimo projector"
```

**Output**: A focused markdown blob containing:
- Existing projector implementations and their patterns
- PolyAgent usage in similar contexts
- Relevant teaching moments (gotchas about projectors)
- Spec sections that apply
- Voice anchors to preserve

**Implementation Sketch**:

```python
class SessionCompiler:
    """Compile Living Docs into session-specific context."""

    def hydrate(self, task: str) -> HydrationContext:
        """
        Generate focused context for a task.

        Strategy:
        1. Extract keywords from task
        2. Find modules with matching symbols/docstrings
        3. Collect teaching moments from those modules
        4. Find related specs
        5. Extract voice anchors
        """
        keywords = self._extract_keywords(task)
        relevant_modules = self._find_relevant_modules(keywords)
        teaching = self._collect_teaching(relevant_modules)
        specs = self._find_related_specs(keywords)
        voice = self._extract_voice_anchors()

        return HydrationContext(
            task=task,
            relevant_teaching=teaching,
            relevant_specs=specs,
            related_modules=relevant_modules,
            voice_anchors=voice,
        )
```

**Integration**: The `/hydrate` skill could call this and inject the result into context.

---

## Capability 2: Edit-Time Teaching

**Problem**: Claude edits a file without knowing its gotchas. The teaching moments exist in docstrings, but they're not surfaced at the right time.

**Solution**: Pre-edit context surfacing.

```bash
kg docs relevant services/brain/persistence.py
```

**Output**:
```
🚨 CRITICAL (2)
  - Dual-track storage means Crystal table AND D-gent must both...
  - capture() returns immediately but trace recording is fire-and-forget...

⚠️ Related Files:
  - services/witness/playbook.py (shares persistence patterns)
  - agents/d/symbiont.py (D-gent integration)

📚 Specs:
  - spec/agents/d-gent.md §Persistence Layer
```

**Integration Options**:
1. **Manual**: Claude calls `kg docs relevant` before editing
2. **Skill**: `/relevant <path>` skill surfaces before changes
3. **Hook**: Claude Code pre-edit hook (if such a thing exists)

---

## Capability 3: Voice Anchor Mining

**Problem**: Kent's voice gets diluted through LLM processing. The Anti-Sausage Protocol has quotes, but they're static.

**Solution**: Dynamic voice extraction from multiple sources.

```bash
kg docs voice
```

**Sources to Mine**:
1. `_focus.md` — Direct quotes
2. Session epilogues in `_epilogues/` — Recent phrases
3. Git commit messages — Recurring patterns
4. Spec files — Philosophical statements (blockquotes)

**Output**:
```
🎯 VOICE ANCHORS (recent 30 days)

From _focus.md:
  "Daring, bold, creative, opinionated but not gaudy"
  "The Mirror Test: Does K-gent feel like me on my best day?"

From commits:
  "feat:" → uses active, first-person framing
  Recurring: "wiring > creation", "depth over breadth"

From specs:
  "The noun is a lie. There is only the rate of change."
  "Gotchas live in docstrings, not wikis."

🚨 ANTI-SAUSAGE CHECK:
  - Avoid: "comprehensive", "robust", "seamless"
  - Prefer: "tasteful", "joy-inducing", "composed"
```

**Integration**: Inject into session start context. Maybe append to CLAUDE.md dynamically?

---

## Capability 4: Drift Detection

**Problem**: Specs describe intent, implementations diverge. Over time, spec and impl drift apart.

**Solution**: Compare spec to implementation and surface divergences.

```bash
kg docs drift spec/protocols/living-docs.md
```

**Analysis**:
1. Parse spec for declared types, laws, and capabilities
2. Find corresponding implementation modules
3. Compare:
   - Are all spec types implemented?
   - Are laws verified by tests?
   - Are capabilities exposed via AGENTESE?

**Output**:
```
📊 DRIFT REPORT: spec/protocols/living-docs.md

✅ Implemented (5):
  - DocNode, TeachingMoment, Surface, Verification, Tier

⚠️ Partially Implemented (1):
  - Verification.round_trip — exists but no LLM integration

❌ Missing (2):
  - spec mentions "Semantic Similarity" — not implemented
  - spec mentions "Auto-refresh" — not implemented

🔄 Divergences:
  - Spec: "Observer determines tier" — Impl: tier is static per symbol
```

---

## Capability 5: Pattern Mining

**Problem**: Patterns emerge across the codebase but aren't documented. New Claude sessions don't know them.

**Solution**: Extract recurring structures from code.

```bash
kg docs patterns
```

**What to Mine**:
- PolyAgent instantiation patterns
- AGENTESE node registration patterns
- Test structure patterns (T-gent types)
- Error handling patterns
- Bus wiring patterns

**Output**:
```
🔮 EMERGENT PATTERNS (from 2,763 files)

1. Container-Owns-Workflow (12 instances)
   - services/brain/persistence.py
   - services/witness/playbook.py
   - services/conductor/operad.py
   Pattern: Container dataclass with Workflow nested class

2. Thin Routing Shim (8 instances)
   - protocols/cli/handlers/brain_thin.py
   - protocols/cli/handlers/docs.py
   Pattern: cmd_X routes to AGENTESE path, no business logic

3. Teaching Moment Placement (35 instances)
   Pattern: "Teaching:" section with "gotcha:" keyword
   Evidence: always includes test path
```

---

## Integration with System Prompt

Currently, Kent has the CONSTITUTION as the system prompt. But the system prompt could be **compiled** from multiple sources:

```
SYSTEM_PROMPT = compile([
    CONSTITUTION,                    # Immutable principles
    CLAUDE_MD,                       # Project-specific context
    hydrate(current_task),           # Task-specific context
    voice_anchors(recent=30),        # Anti-sausage fuel
    critical_teaching(top=10),       # Most important gotchas
])
```

This is more than a static CLAUDE.md — it's a **living context** that changes based on what you're doing.

---

## Priority Order

| Capability | Value | Effort | Priority |
|------------|-------|--------|----------|
| Session Hydration | High | Medium | 1 |
| Edit-Time Teaching | High | Low | 2 |
| Voice Anchors | Medium | Medium | 3 |
| Drift Detection | Medium | High | 4 |
| Pattern Mining | Low | High | 5 |

**Recommended Path**:
1. Phase 6 (modest): `kg docs hydrate` and `kg docs relevant`
2. Future: Voice anchor mining
3. Future: Drift detection
4. Exploratory: Pattern mining

---

## Open Questions

1. **Semantic Similarity**: Should hydration use Brain's vector store for relevance? Or is keyword matching sufficient?

2. **Context Budget**: How much context is too much? Need to respect token limits.

3. **Staleness**: How often should compiled context refresh? Every session? Every edit?

4. **Feedback Loop**: Can we learn which teaching moments were actually useful and rank accordingly?

5. **Multi-Session Memory**: Can hydration context persist across sessions for long-running tasks?

---

## Connection to Constitution

This vision aligns with the 7 principles:

| Principle | Alignment |
|-----------|-----------|
| **Tasteful** | Compile only what's needed, not everything |
| **Curated** | Rank by relevance, not dump all |
| **Ethical** | Transparent — Claude knows what context it has |
| **Joy-Inducing** | Less context-gathering drudgery |
| **Composable** | Hydration = DocExtractor >> Relevance >> Projection |
| **Heterarchical** | Context adapts to task, not fixed hierarchy |
| **Generative** | From source → context, not source → static docs |

---

*"The master's touch was always just compressed experience. Now we compile the compression."*
