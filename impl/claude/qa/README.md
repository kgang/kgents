# QA: Witness Framework

> **These files are illustrative, not canonical. Do not work on fixing these unless asked.**

## Philosophy

QA in kgents is not traditional testing—it's **witnessing**.

| Concept | Traditional QA | kgents QA |
|---------|----------------|-----------|
| Purpose | Verify correctness | **Bear witness** to functionality |
| Status | Canonical (must pass) | Illustrative (demonstrates capability) |
| Failure | Bug | **Signal** (system may have evolved) |
| Output | Pass/Fail | **Evidence** (what actually happened) |

### The Witness Principle

From `spec/principles.md`:

> Agents form a category. These laws are not aspirational—they are **verified**.

A witness is evidence that a law holds. Unlike tests that assert, witnesses **observe and report**.

```
Test:    assert result == expected  # Binary: pass/fail
Witness: report(what_happened)      # Evidence: here's what I saw
```

## The Slop → Witness → Evidence Pipeline

From the Accursed Share meta-principle:

```
Raw Slop (LLM output, noise)
    ↓ filter
Refined Slop (structured but unjudged)
    ↓ curate
Curated (selected by principles)
    ↓ witness
Cherished Evidence (reproducible demonstrations)
    ↓ compost
Raw Slop (new experiments)
```

QA witnesses are **cherished evidence**—they demonstrate that the system works, frozen at a point in time.

## Structure

```
qa/
├── __init__.py          # Witness protocol + utilities
├── README.md            # This file
└── witnesses/           # Witness scripts by genus
    ├── __init__.py
    ├── e_gent_witness.py    # E-gent thermodynamic evolution
    ├── b_gent_witness.py    # B-gent economics (future)
    ├── l_gent_witness.py    # L-gent semantics (future)
    └── ...
```

## The Witness Protocol

Every witness follows this structure:

```python
class Witness(Protocol):
    """
    A witness observes and reports.

    Unlike tests that assert, witnesses bear evidence.
    The evidence may be favorable or unfavorable—both are valuable.
    """

    @property
    def name(self) -> str:
        """What is being witnessed."""
        ...

    async def observe(self) -> WitnessReport:
        """
        Observe the system and report what happened.

        Returns evidence, not judgments.
        """
        ...
```

## Running Witnesses

```bash
# Run a single witness
python -m impl.claude.qa.witnesses.e_gent_witness

# Run all witnesses (future)
python -m impl.claude.qa --all

# Run with verbose output
python -m impl.claude.qa.witnesses.e_gent_witness --verbose
```

## Witness vs Test: When to Use Each

| Use Case | Tool | Why |
|----------|------|-----|
| Law verification | pytest + law marker | Must pass, canonical |
| Property testing | pytest + hypothesis | Explores edge cases |
| Integration check | pytest integration | Contracts between agents |
| **Demonstration** | **QA Witness** | Shows system working "for real" |
| **Exploration** | **QA Witness** | Discovers what's possible |
| **Onboarding** | **QA Witness** | New developer sees system in action |

## Principles Alignment

| Principle | How QA Witnesses Align |
|-----------|------------------------|
| **Tasteful** | Each witness has a clear purpose (demonstrate one thing well) |
| **Curated** | Only witnesses that provide unique insight |
| **Ethical** | Transparent about what they are (not tests, not canonical) |
| **Joy-Inducing** | Running a witness should be satisfying |
| **Composable** | Witnesses can be combined (witness A then B) |
| **Heterarchical** | Witnesses exist in flux with the system |
| **Generative** | Witnesses can be regenerated from principles |
| **Transparent** | Witnesses communicate what's happening |

## The Gratitude Clause

> We do not resent the slop. We thank it for providing the raw material from which beauty emerges.

When a witness shows unexpected behavior:
1. **Don't panic** — this is evidence, not failure
2. **Document** — what did the witness observe?
3. **Investigate** — has the system evolved?
4. **Update or archive** — keep the witness current or retire it with gratitude

## Adding New Witnesses

1. Create `witnesses/<genus>_gent_witness.py`
2. Include the required header comment
3. Implement observation functions that **report**, not assert
4. Add to this README when mature

### Required Header

```python
#!/usr/bin/env python
"""
<Genus>-gent Witness

> These files are illustrative, not canonical.
> Do not work on fixing these unless asked.

This witness demonstrates <what> by <how>.
"""
```

---

*"The fish doesn't notice water; the LLM doesn't notice personality-space. But both swim in it."*
*— spec/principles.md*
