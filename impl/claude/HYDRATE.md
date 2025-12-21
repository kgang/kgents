# HYDRATE: Session Context

**Date**: 2025-12-21 | **Phase**: Metabolic 1.3 Complete

---

## Voice Anchors (Preserve These)

> "Daring, bold, creative, opinionated but not gaudy"
> "The Mirror Test: Does K-gent feel like me on my best day?"
> "Tasteful > feature-complete"
> "The persona is a garden, not a museum"

---

## Current Focus: Metabolic Development Protocol

Phase 1.3 (Full Morning Flow) now complete. The `kg coffee begin` command wires:
- **CircadianResonance**: Matches today to similar past mornings
- **VoiceStigmergy**: Patterns from repeated intent deposits
- **Hydrator**: Intent → gotchas + likely files + voice anchors

**Next**: Phase 2.2 (Interactive Text) or Phase 3 (Voice Intelligence)

---

## Gotchas for This Session

### Critical
- **DI Container Silent Skip**: Dependencies in `@node(dependencies=(...))` must be registered in `providers.py` or they silently skip
- **@node runs at import time**: Module must be imported for node to register

### Warning
- **Diversity > Count**: 10 diverse runs > 100 identical runs for evidence
- **Circadian resonance**: Same weekday > adjacent day (Monday Kent ≠ Friday Kent)
- **Serendipity from FOSSIL only**: >14 days old = unexpected wisdom

---

## Files You'll Likely Touch

| File | Purpose |
|------|---------|
| `services/liminal/coffee/circadian.py` | CircadianResonance, archaeology layers |
| `services/liminal/coffee/cli_formatting.py` | format_circadian_context, format_hydration_context |
| `protocols/cli/handlers/coffee.py` | _run_begin (full morning flow) |
| `services/living_docs/hydrator.py` | HydrationContext, keyword matching |
| `services/metabolism/evidencing.py` | BackgroundEvidencing, DiversityScore |

---

## Key Commands

```bash
cd impl/claude

# Run coffee tests (312 passing)
uv run pytest services/liminal/coffee/_tests/ -q

# Test the morning flow
uv run python -c "from protocols.cli.handlers.coffee import cmd_coffee; cmd_coffee(['begin', '--json'])"

# Type check
uv run mypy services/liminal/coffee/ protocols/cli/handlers/coffee.py
```

---

## Test Status

| Component | Tests | Status |
|-----------|-------|--------|
| Coffee (Liminal) | 312 | Passing |
| Circadian | 24 | Passing |
| ASHC Evidencing | 29 | Passing |
| Total Metabolic | 53+ | Passing |

---

*"The morning mind knows things the afternoon mind has forgotten."*
