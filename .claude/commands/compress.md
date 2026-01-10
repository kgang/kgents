# /compress - Collapse to 3-Phase

When ceremony becomes burden, compress remaining phases to UNDERSTAND → ACT → REFLECT.

## Protocol

1. **Read the plan file** specified as argument (required)
2. **Identify current phase** from `phase_ledger` in YAML header
3. **Show compression preview**:
   - List phases that will be marked `compressed`
   - Show the simplified continuation that will be generated
4. **Ask for confirmation**: "Compress N phases? (y/n)"
5. **If confirmed**:
   - Update plan file's `phase_ledger` to mark remaining detailed phases as `compressed`
   - Generate a 3-phase continuation prompt
6. **If declined**: Exit without changes

## Usage

```
/compress <plan-file>
/compress plans/my-feature.md
```

## Phase Mapping

| 3-Phase | Detailed Phases |
|---------|-----------------|
| UNDERSTAND | PLAN, RESEARCH, DEVELOP, STRATEGIZE, CROSS-SYNERGIZE |
| ACT | IMPLEMENT, QA, TEST |
| REFLECT | EDUCATE, MEASURE, REFLECT |

## Compression Rules

- Phases already marked `touched` or `completed` stay as-is
- Phases marked `pending` in the same family get marked `compressed`
- REFLECT phases are never compressed (always required)

## Output Format

After compression, generate:

```markdown
# Compressed: [Task Name]

/hydrate

Phase: [UNDERSTAND|ACT|REFLECT]
Mission: [Combined mission from remaining phases]
Exit: Tests pass, learnings captured.

---
Compressed from 11-phase. Original plan: [plan-file]
```

## When to Use

- Momentum stalled after 30+ minutes in same phase
- Ceremony overhead exceeds value
- Scope clarified and full ceremony no longer needed
- User explicitly requests simplification

## Arguments

- `<plan-file>`: Path to plan file with `phase_ledger` YAML header (required)
