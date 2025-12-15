"""
Phase templates for N-Phase Prompt Compiler.

Design Decision (B2): Templates are hardcoded Python strings, not runtime-loaded
from markdown files. This provides:
- Faster compilation (no file I/O)
- Version control (templates change with code)
- Type safety (templates are string constants)

Future: Extract from docs/skills/n-phase-cycle/*.md if runtime flexibility needed.
"""

from typing import NamedTuple


class PhaseTemplate(NamedTuple):
    """Template for a single phase."""

    name: str
    mission: str
    actions: str
    exit_criteria: str
    continuation: str
    minimum_artifact: str


# Phase family mapping for 3-phase mode
# UNDERSTAND is the primary name (more actionable), SENSE is kept as alias for compatibility
PHASE_FAMILIES: dict[str, list[str]] = {
    "UNDERSTAND": ["PLAN", "RESEARCH", "DEVELOP", "STRATEGIZE", "CROSS-SYNERGIZE"],
    "ACT": ["IMPLEMENT", "QA", "TEST"],
    "REFLECT": ["EDUCATE", "MEASURE", "REFLECT"],
}

# Alias for backwards compatibility
PHASE_ALIASES: dict[str, str] = {
    "SENSE": "UNDERSTAND",  # Legacy name maps to new primary
}


PHASE_TEMPLATES: dict[str, PhaseTemplate] = {
    "PLAN": PhaseTemplate(
        name="PLAN",
        mission="Define scope, exit criteria, and attention budget. Draw entropy sip.",
        actions="""1. Read existing context (handles, prior phases)
2. Clarify scope boundaries (what IS and ISN'T in scope)
3. Define exit criteria for this work
4. Allocate entropy budget across phases
5. Identify parallel tracks if applicable""",
        exit_criteria="""- [ ] Scope boundaries clear
- [ ] Exit criteria defined
- [ ] Entropy budget allocated
- [ ] Parallel tracks identified (if any)""",
        continuation="RESEARCH",
        minimum_artifact="Scope, exit criteria, attention budget, entropy sip",
    ),
    "RESEARCH": PhaseTemplate(
        name="RESEARCH",
        mission="Map the terrain. Build file map, surface blockers with evidence.",
        actions="""1. Search for existing implementations
2. Document file locations with line numbers
3. Identify blockers with file:line evidence
4. Note prior art that can be reused
5. Surface invariants from existing code""",
        exit_criteria="""- [ ] File map complete with line references
- [ ] Blockers surfaced with evidence
- [ ] Prior art documented
- [ ] Did NOT modify source files""",
        continuation="DEVELOP",
        minimum_artifact="File map + blockers with refs",
    ),
    "DEVELOP": PhaseTemplate(
        name="DEVELOP",
        mission="Design contracts and APIs. Define what will be built.",
        actions="""1. Define data schemas/types
2. Specify API contracts
3. Document invariants/laws
4. Resolve blockers with design decisions
5. Create component breakdown""",
        exit_criteria="""- [ ] Schemas defined
- [ ] API contracts specified
- [ ] Invariants documented
- [ ] Blockers resolved with decisions""",
        continuation="STRATEGIZE",
        minimum_artifact="Contract/API deltas or law assertions",
    ),
    "STRATEGIZE": PhaseTemplate(
        name="STRATEGIZE",
        mission="Sequence the work. Define waves and checkpoints.",
        actions="""1. Order components by dependencies
2. Group into execution waves
3. Define checkpoints between waves
4. Identify parallelization opportunities
5. Set risk mitigation order""",
        exit_criteria="""- [ ] Waves defined with rationale
- [ ] Checkpoints specified
- [ ] Dependencies mapped
- [ ] Critical path identified""",
        continuation="CROSS-SYNERGIZE",
        minimum_artifact="Sequencing with rationale",
    ),
    "CROSS-SYNERGIZE": PhaseTemplate(
        name="CROSS-SYNERGIZE",
        mission="Find compositions. Identify cross-cutting concerns and synergies.",
        actions="""1. Identify shared types/interfaces
2. Find cross-plan dependencies
3. Document runtime compositions
4. Note potential conflicts
5. Design integration points""",
        exit_criteria="""- [ ] Cross-cutting concerns identified
- [ ] Shared interfaces documented
- [ ] Integration points designed
- [ ] Conflicts resolved or noted""",
        continuation="IMPLEMENT",
        minimum_artifact="Named compositions or explicit skip",
    ),
    "IMPLEMENT": PhaseTemplate(
        name="IMPLEMENT",
        mission="Write the code. Execute the plan.",
        actions="""1. Follow wave sequence
2. Implement each component
3. Run tests as you go
4. Document deviations from plan
5. Update handles with new artifacts""",
        exit_criteria="""- [ ] All wave components implemented
- [ ] Tests passing locally
- [ ] No new blockers introduced
- [ ] Handles updated""",
        continuation="QA",
        minimum_artifact="Code changes or commit-ready diff",
    ),
    "QA": PhaseTemplate(
        name="QA",
        mission="Verify quality. Run linters, type checkers, static analysis.",
        actions="""1. Run mypy for type checking
2. Run ruff for linting
3. Check for security issues
4. Verify code style
5. Review for edge cases""",
        exit_criteria="""- [ ] mypy clean
- [ ] ruff clean
- [ ] No security issues
- [ ] Edge cases handled""",
        continuation="TEST",
        minimum_artifact="Checklist run with result",
    ),
    "TEST": PhaseTemplate(
        name="TEST",
        mission="Verify behavior. Write and run tests.",
        actions="""1. Write unit tests for new code
2. Add integration tests if needed
3. Verify law tests pass
4. Check edge cases
5. Run full test suite""",
        exit_criteria="""- [ ] Unit tests written
- [ ] All tests passing
- [ ] Law tests verified
- [ ] Coverage acceptable""",
        continuation="EDUCATE",
        minimum_artifact="Tests added/updated or explicit no-op with risk",
    ),
    "EDUCATE": PhaseTemplate(
        name="EDUCATE",
        mission="Document for users and maintainers.",
        actions="""1. Update README if needed
2. Add inline documentation
3. Create usage examples
4. Document gotchas
5. Update CHANGELOG""",
        exit_criteria="""- [ ] User documentation updated
- [ ] Maintainer notes added
- [ ] Examples provided""",
        continuation="MEASURE",
        minimum_artifact="User/maintainer note or explicit skip",
    ),
    "MEASURE": PhaseTemplate(
        name="MEASURE",
        mission="Define metrics. Set up measurement for success.",
        actions="""1. Identify key metrics
2. Add instrumentation if needed
3. Define success criteria
4. Set up monitoring
5. Document baseline""",
        exit_criteria="""- [ ] Metrics identified
- [ ] Instrumentation in place
- [ ] Success criteria defined""",
        continuation="REFLECT",
        minimum_artifact="Metric hook/plan or defer with owner/timebox",
    ),
    "REFLECT": PhaseTemplate(
        name="REFLECT",
        mission="Extract learnings. Seed the next cycle.",
        actions="""1. Review what worked well
2. Document what didn't
3. Extract reusable patterns
4. Identify follow-up work
5. Update entropy accounting""",
        exit_criteria="""- [ ] Learnings documented
- [ ] Patterns extracted
- [ ] Follow-up work identified
- [ ] Entropy accounted""",
        continuation="COMPLETE",
        minimum_artifact="Learnings + next-loop seeds",
    ),
}


def get_template(phase: str) -> PhaseTemplate:
    """Get template for a phase."""
    if phase not in PHASE_TEMPLATES:
        raise ValueError(
            f"Unknown phase: {phase}. Valid: {list(PHASE_TEMPLATES.keys())}"
        )
    return PHASE_TEMPLATES[phase]


def get_compressed_template(family: str) -> PhaseTemplate:
    """Get compressed template for 3-phase mode."""
    # Resolve alias if provided
    resolved_family = PHASE_ALIASES.get(family, family)

    phases = PHASE_FAMILIES.get(resolved_family, [])
    if not phases:
        valid = list(PHASE_FAMILIES.keys()) + list(PHASE_ALIASES.keys())
        raise ValueError(f"Unknown family: {family}. Valid: {valid}")

    # Combine phase templates
    missions = [PHASE_TEMPLATES[p].mission for p in phases]
    actions = [f"### {p}\n{PHASE_TEMPLATES[p].actions}" for p in phases]
    criteria = [f"### {p}\n{PHASE_TEMPLATES[p].exit_criteria}" for p in phases]

    next_family = {"UNDERSTAND": "ACT", "ACT": "REFLECT", "REFLECT": "COMPLETE"}

    return PhaseTemplate(
        name=resolved_family,
        mission=" | ".join(missions),
        actions="\n\n".join(actions),
        exit_criteria="\n\n".join(criteria),
        continuation=next_family[resolved_family],
        minimum_artifact=", ".join(PHASE_TEMPLATES[p].minimum_artifact for p in phases),
    )
