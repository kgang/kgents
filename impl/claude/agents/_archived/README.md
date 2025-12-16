# Archived Agent Modules

These modules are preserved for reference but no longer active.
They may be restored if needed.

## Archived Modules

| Module | Theme | Reason | Date |
|--------|-------|--------|------|
| `h/` | Dialectic (Hegel/Jung/Lacan) | Low traffic, 8 CLI commands deprecated | 2025-12-16 |
| `q/` | Quartermaster (K8s jobs) | Never deployed to production | 2025-12-16 |
| `r/` | Refinery (DSPy optimization) | No production usage | 2025-12-16 |
| `psi/` | Metaphor Engine | Speculative, MCP tool removed | 2025-12-16 |
| `poly/test_cross_polynomial.py` | Cross-polynomial composition | D-gent architecture rewrite removed `agents.d.polynomial` | 2025-12-16 |

## Restoration

To restore a module:

```bash
# 1. Move back to active
mv agents/_archived/<module> agents/<module>

# 2. Update agents/__init__.py imports
# 3. Restore CLI handlers from git history if needed
# 4. Run tests: uv run pytest agents/<module>
```

## Why Archive vs Delete?

- **Code archaeology**: These represent significant design work
- **Restoration option**: Can bring back if use case emerges
- **Learning resource**: Patterns may inform future designs
