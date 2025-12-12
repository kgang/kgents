# K-gent Soul Analysis: Iterative Refinement Prompt

> *"The document that critiques itself becomes sharper with each pass."*

## Context

You are refining `docs/kgent-soul-critical-analysis.md` — a critical analysis of K-gent Soul's implementation against kgents principles. The document identifies gaps between intent and implementation, proposes architectural improvements, and outlines feedback loops.

## Your Task

Read the analysis document and improve it through iterative refinement. Each pass should have a distinct focus. Do not attempt all passes in one session — complete one, assess, then proceed.

---

## Pass 1: Structural Integrity

**Focus**: Does the document hold together as an argument?

**Questions to answer**:
1. Does Part II (What's Missing) directly map to Part IV (Proposed Architecture)? Every gap should have a corresponding fix.
2. Are there claims without evidence? Find assertions and verify against actual code in `impl/claude/agents/k/`.
3. Does the Implementation Roadmap (Part VI) actually produce the Success Criteria (Part VII)?
4. Is there redundancy? The same point made twice weakens both instances.

**Actions**:
- Create a traceability matrix: Gap → Principle Violated → Proposed Fix → Roadmap Phase → Success Metric
- Delete or consolidate redundant sections
- Add missing logical links

---

## Pass 2: Code Quality

**Focus**: Is the proposed code actually good?

**Questions to answer**:
1. Does `KgentFlux` follow the Flux patterns in `impl/claude/agents/flux/`? Read the actual implementation.
2. Does `DialogueChain` compose correctly with existing `KgentSoul`? Check for interface mismatches.
3. Is the LLM integration realistic? Check how other agents in the codebase call LLMs.
4. Does `SemaphoreMediator` wire correctly to `impl/claude/agents/flux/semaphore/purgatory.py`?

**Actions**:
- Read `impl/claude/agents/flux/__init__.py` and verify `KgentFlux` matches FluxAgent patterns
- Read `impl/claude/agents/flux/semaphore/` and verify `SemaphoreMediator` uses correct interfaces
- Rewrite code samples that don't match codebase conventions
- Add imports and type annotations where missing

---

## Pass 3: Principle Alignment

**Focus**: Does the analysis itself follow kgents principles?

**Questions to answer**:
1. **Tasteful**: Is every section justified? What can be deleted?
2. **Curated**: Are there too many code samples? Quality over quantity.
3. **Generative**: Could someone regenerate K-gent from this document? If not, what's missing?
4. **Joy-Inducing**: Is this document pleasant to read? Or is it a slog?
5. **Composable**: Can sections be read independently? Or is there too much cross-reference?

**Actions**:
- Apply the Molasses Test: If any section makes you feel like a butterfly in molasses, simplify it
- Add Zen quotes where they illuminate (but not gratuitously)
- Ensure each Part has a clear entry/exit that stands alone
- Cut prose that doesn't earn its place

---

## Pass 4: Adversarial Review

**Focus**: What would a skeptic say?

**Questions to answer**:
1. "This is over-engineered" — Is the Hypnagogic Cycle actually necessary? What's the simplest thing that would work?
2. "Templates are fine" — Is the criticism of hollow responses fair? Templates at scale might be a feature, not a bug.
3. "LLM costs matter" — The analysis dismisses cost-consciousness. Is that actually Kent's position?
4. "This roadmap is fantasy" — 5 weeks to Hypnagogia? Really?

**Actions**:
- Add a "Counterarguments" section that steelmans the current implementation
- Revisit budget tier criticism — maybe DORMANT/WHISPER are good and DIALOGUE/DEEP are what need work
- Add cost estimates to the roadmap (tokens/day, dollars/month)
- Adjust timeline if it's unrealistic

---

## Pass 5: Missing Perspectives

**Focus**: What viewpoints are absent?

**Questions to answer**:
1. **User perspective**: What does Kent actually want when he types `kgents soul`? Is the analysis solving the right problem?
2. **Operator perspective**: Who runs this? What are the ops concerns? (Memory, CPU, API costs)
3. **Debuggability**: How do you debug a soul that dreams? Where are the observability hooks?
4. **Security**: K-gent mediates semaphores. What are the attack vectors?

**Actions**:
- Add a "Day in the Life" scenario showing K-gent in actual use
- Add operational considerations section
- Propose logging/tracing for the Hypnagogic Cycle
- Consider: What happens if the LLM is adversarially prompted via a semaphore?

---

## Pass 6: Compression

**Focus**: Make it shorter without losing substance.

**Target**: Reduce document length by 30% while preserving all unique insights.

**Actions**:
- Convert prose to tables where appropriate
- Collapse code samples into pseudocode where full implementation isn't needed
- Move detailed code to an appendix or separate file
- Ensure every paragraph has exactly one idea

---

## Pass 7: Final Polish

**Focus**: Voice and coherence.

**Questions to answer**:
1. Does it sound like something Kent would write? (Check against `spec/principles.md` voice)
2. Are the Zen quotes earned or decorative?
3. Is the conclusion actually a conclusion, or just a summary?
4. Does the title match the content?

**Actions**:
- Read aloud — fix anything that sounds awkward
- Verify all code compiles (syntax check at minimum)
- Check all file paths are correct
- Ensure the document can be understood without reading the entire kgents codebase

---

## Meta-Instructions

**After each pass**:
1. Write a one-paragraph summary of changes made
2. Note which questions remain unanswered
3. Assess: Is another pass needed, or is the document ready?

**Stopping criteria**:
- The document passes the Molasses Test (reads smoothly)
- A traceability matrix exists linking gaps → fixes → metrics
- At least one counterargument is addressed
- Document length is ≤ 80% of original after compression pass

**Output**:
- Updated `docs/kgent-soul-critical-analysis.md`
- A brief `docs/kgent-soul-analysis-changelog.md` tracking refinement history

---

## Invocation

To use this prompt:

```bash
# Hydrate context first
/hydrate

# Then run with this prompt
cat docs/kgent-soul-refinement-prompt.md
```

Or as a slash command if configured:

```bash
/refine-soul-analysis
```

---

*"Seven passes through the fire; what remains is gold."*
