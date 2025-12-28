# Regeneration Protocol: Isomorphic Mapping to kgents Primitives

> *"The dialectic IS the dynamical system. The outline IS the sheaf. The witness IS the morphism."*

**Status**: Draft Specification
**Version**: 1.0
**Author**: Claude (via Kent's direction)
**Axiom Grounding**: Zero Seed L1-L2, Omega Layer (0-5)

---

## Abstract

This specification establishes an **isomorphic mapping** from the pilot regeneration system to kgents categorical primitives (PolyAgent, Operad, Sheaf, Witness). The mapping preserves:

1. **Compositional structure** (Operad laws)
2. **Mode-dependent behavior** (Polynomial positions/directions)
3. **Multi-agent coherence** (Sheaf gluing)
4. **Decision provenance** (Witness morphisms)

The result: regeneration becomes a **first-class citizen** of the kgents agent ecosystem, composable with all other agents via standard categorical operations.

---

## Part I: Polynomial Agent Design

### 1.1 The Orchestrator Polynomial

The CREATIVE and ADVERSARIAL orchestrators share the **same polynomial structure** but differ in their **direction functions** (mode-dependent inputs). This captures the insight that both are dialectical partners operating on the same state space.

#### Positions (Shared State Space)

```python
from enum import Enum, auto

class OrchestratorPhase(Enum):
    """
    Positions in the Orchestrator Polynomial.

    Categorical interpretation:
      P(y) = y^{D(BOOTSTRAP)} + y^{D(DESIGN)} + y^{D(BUILD)} + ... + y^{D(COMPLETE)}

    Where D(s) denotes the directions (valid inputs) at position s.
    """
    BOOTSTRAP = auto()      # Initialize coordination lattice
    DESIGN = auto()         # Architecture decisions (iterations 1-3)
    BUILD = auto()          # Implementation (iterations 4-8)
    REFLECT = auto()        # Synthesis (iterations 9-10)
    SYNC = auto()           # Waiting for partner coordination
    EXPLORING = auto()      # Post-core exploration (ADVERSARIAL shift)
    COMPLETE = auto()       # Terminal state
    HALTED = auto()         # Error/abort state
```

#### Direction Functions (Role-Dependent)

The **critical insight**: CREATIVE and ADVERSARIAL accept different inputs at the same position. This is the polynomial functor's power.

```python
from dataclasses import dataclass
from typing import FrozenSet, Protocol, Any

# Input Types
@dataclass(frozen=True)
class DesignDecision:
    topic: str
    choice: str
    rationale: str
    request_review: bool = False

@dataclass(frozen=True)
class ComponentClaim:
    component_name: str
    approach: str

@dataclass(frozen=True)
class ContradictionReveal:
    topic: str
    what_i_see: str
    why_it_matters: str
    resolutions: list[str]
    severity: str  # "critical" | "important" | "minor" | "fyi"

@dataclass(frozen=True)
class SyncEvent:
    partner_phase: OrchestratorPhase
    components_ready: list[str]
    contradictions_pending: list[str]

@dataclass(frozen=True)
class ExplorationProposal:
    extension_name: str
    why_bold: str
    effort: str  # "small" | "medium" | "large"
    joy_factor: str

@dataclass(frozen=True)
class Iteration:
    number: int  # 1-10 (or adapted)
    phase: str   # "DESIGN" | "EXECUTION" | "REFLECTION"

# Direction Functions
def creative_directions(phase: OrchestratorPhase) -> FrozenSet[type]:
    """
    CREATIVE accepts design decisions, component claims, and sync events.

    Values: novelty, cohesion, completeness, joy
    """
    match phase:
        case OrchestratorPhase.BOOTSTRAP:
            return frozenset({DesignDecision, Iteration})
        case OrchestratorPhase.DESIGN:
            return frozenset({DesignDecision, ComponentClaim, SyncEvent})
        case OrchestratorPhase.BUILD:
            return frozenset({ComponentClaim, SyncEvent, Iteration})
        case OrchestratorPhase.REFLECT:
            return frozenset({SyncEvent, Iteration})
        case OrchestratorPhase.SYNC:
            return frozenset({SyncEvent})
        case OrchestratorPhase.EXPLORING:
            return frozenset({ExplorationProposal, SyncEvent})
        case OrchestratorPhase.COMPLETE | OrchestratorPhase.HALTED:
            return frozenset()  # Terminal - no valid inputs

def adversarial_directions(phase: OrchestratorPhase) -> FrozenSet[type]:
    """
    ADVERSARIAL accepts contradiction reveals and exploration proposals.

    Values: alignment, entropy, opportunity, coherence
    """
    match phase:
        case OrchestratorPhase.BOOTSTRAP:
            return frozenset({SyncEvent})  # Wait for CREATIVE to initialize
        case OrchestratorPhase.DESIGN:
            return frozenset({ContradictionReveal, SyncEvent})
        case OrchestratorPhase.BUILD:
            return frozenset({ContradictionReveal, SyncEvent, Iteration})
        case OrchestratorPhase.REFLECT:
            return frozenset({ContradictionReveal, SyncEvent})
        case OrchestratorPhase.SYNC:
            return frozenset({SyncEvent})
        case OrchestratorPhase.EXPLORING:
            return frozenset({ExplorationProposal, SyncEvent})  # MODE SHIFT
        case OrchestratorPhase.COMPLETE | OrchestratorPhase.HALTED:
            return frozenset()
```

#### Transition Functions

```python
@dataclass
class OrchestratorOutput:
    success: bool
    message: str
    artifacts: list[str] = field(default_factory=list)
    witness_mark_id: str | None = None

def creative_transition(
    phase: OrchestratorPhase,
    input: Any
) -> tuple[OrchestratorPhase, OrchestratorOutput]:
    """
    CREATIVE transition function.

    Pattern: Progress through iterations, yield to SYNC on partner events,
    transition to EXPLORING when core complete.
    """
    match phase:
        case OrchestratorPhase.BOOTSTRAP:
            if isinstance(input, Iteration) and input.number == 1:
                return OrchestratorPhase.DESIGN, OrchestratorOutput(
                    success=True,
                    message="Lattice initialized. Design phase begins.",
                    artifacts=[".outline.md", ".iteration", ".phase"]
                )

        case OrchestratorPhase.DESIGN:
            if isinstance(input, Iteration) and input.number >= 4:
                return OrchestratorPhase.BUILD, OrchestratorOutput(
                    success=True,
                    message="Design frozen. Execution phase begins."
                )
            if isinstance(input, SyncEvent) and input.contradictions_pending:
                return OrchestratorPhase.SYNC, OrchestratorOutput(
                    success=True,
                    message=f"Pausing for {len(input.contradictions_pending)} contradictions."
                )
            # Normal design work continues in DESIGN
            return OrchestratorPhase.DESIGN, OrchestratorOutput(
                success=True,
                message="Design decision recorded."
            )

        case OrchestratorPhase.BUILD:
            if isinstance(input, Iteration) and input.number >= 9:
                return OrchestratorPhase.REFLECT, OrchestratorOutput(
                    success=True,
                    message="Implementation complete. Reflection phase begins."
                )
            return OrchestratorPhase.BUILD, OrchestratorOutput(
                success=True,
                message="Component built."
            )

        case OrchestratorPhase.REFLECT:
            if isinstance(input, Iteration) and input.number > 10:
                return OrchestratorPhase.COMPLETE, OrchestratorOutput(
                    success=True,
                    message="Regeneration complete."
                )
            return OrchestratorPhase.REFLECT, OrchestratorOutput(
                success=True,
                message="Synthesis in progress."
            )

        case OrchestratorPhase.SYNC:
            if isinstance(input, SyncEvent) and not input.contradictions_pending:
                # Return to previous phase after sync
                return OrchestratorPhase.BUILD, OrchestratorOutput(
                    success=True,
                    message="Contradictions resolved. Continuing."
                )
            return OrchestratorPhase.SYNC, OrchestratorOutput(
                success=False,
                message="Still waiting on partner."
            )

    # Fallback: stay in current phase
    return phase, OrchestratorOutput(success=False, message="Invalid input for phase.")

def adversarial_transition(
    phase: OrchestratorPhase,
    input: Any
) -> tuple[OrchestratorPhase, OrchestratorOutput]:
    """
    ADVERSARIAL transition function.

    Pattern: Analyze and reveal contradictions, shift to EXPLORING
    when partner signals core complete.
    """
    match phase:
        case OrchestratorPhase.BOOTSTRAP:
            if isinstance(input, SyncEvent) and OrchestratorPhase.DESIGN in {input.partner_phase}:
                return OrchestratorPhase.DESIGN, OrchestratorOutput(
                    success=True,
                    message="Partner started. Beginning analysis."
                )
            return OrchestratorPhase.BOOTSTRAP, OrchestratorOutput(
                success=False,
                message="Waiting for CREATIVE to initialize."
            )

        case OrchestratorPhase.DESIGN | OrchestratorPhase.BUILD:
            if isinstance(input, SyncEvent):
                # Check for mode shift
                if "core_complete" in str(input):  # Simplified
                    return OrchestratorPhase.EXPLORING, OrchestratorOutput(
                        success=True,
                        message="Core complete. Shifting to exploration partner."
                    )
            if isinstance(input, ContradictionReveal):
                return phase, OrchestratorOutput(
                    success=True,
                    message=f"Contradiction revealed: {input.topic}",
                    artifacts=[".adversarial_insights.md"]
                )
            return phase, OrchestratorOutput(success=True, message="Analyzing...")

        case OrchestratorPhase.EXPLORING:
            if isinstance(input, ExplorationProposal):
                return OrchestratorPhase.EXPLORING, OrchestratorOutput(
                    success=True,
                    message=f"Bold extension proposed: {input.extension_name}"
                )
            return OrchestratorPhase.EXPLORING, OrchestratorOutput(
                success=True,
                message="Exploring..."
            )

    return phase, OrchestratorOutput(success=False, message="Invalid input.")
```

### 1.2 The Stage Polynomial (Sub-Agent Level)

Each regeneration **stage** is itself a polynomial agent. Stages compose into the full regeneration pipeline.

```python
class StagePhase(Enum):
    """
    Positions for individual regeneration stages.
    """
    PENDING = auto()        # Not yet started
    EXECUTING = auto()      # In progress
    SUCCEEDED = auto()      # Completed successfully
    FAILED = auto()         # Failed with error
    SKIPPED = auto()        # Skipped (e.g., SANITY when backend unavailable)

@dataclass(frozen=True)
class StageInput:
    context: dict[str, Any]     # Portal contents, run info
    previous_output: Any | None # Output from previous stage

@dataclass(frozen=True)
class StageOutput:
    status: str  # "PASS" | "FAIL" | "SKIP" | "GO" | "NO-GO" | "COMPLETE" | etc.
    artifacts: list[str]
    witness_mark_id: str
    next_stage: str | None  # "AUDIT" | "GENERATE" | "HALT" | etc.

# Stage polynomial instances (7 stages)
ARCHIVE_STAGE = PolyAgent(
    name="Archive",
    positions=frozenset(StagePhase),
    _directions=lambda p: frozenset({StageInput}) if p == StagePhase.PENDING else frozenset(),
    _transition=archive_transition
)

AUDIT_STAGE = PolyAgent(
    name="Audit",
    positions=frozenset(StagePhase),
    _directions=lambda p: frozenset({StageInput}) if p == StagePhase.PENDING else frozenset(),
    _transition=audit_transition  # Returns GO/NO-GO
)

SANITY_STAGE = PolyAgent(name="Sanity", ...)
GENERATE_STAGE = PolyAgent(name="Generate", ...)
WIRE_STAGE = PolyAgent(name="Wire", ...)
SMOKE_STAGE = PolyAgent(name="Smoke", ...)
VALIDATE_STAGE = PolyAgent(name="Validate", ...)
LEARN_STAGE = PolyAgent(name="Learn", ...)
```

---

## Part II: Operad Design (REGENERATION_OPERAD)

### 2.1 Operations

The **REGENERATION_OPERAD** extends `AGENT_OPERAD` with domain-specific operations for regeneration.

```python
from agents.operad.core import Operad, Operation, Law, AGENT_OPERAD

def create_regeneration_operad() -> Operad:
    """
    Create the REGENERATION_OPERAD.

    This operad defines the grammar of regeneration composition.
    """
    # Inherit universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add regeneration-specific operations
    ops["stage_seq"] = Operation(
        name="stage_seq",
        arity=2,
        signature="Stage[A] x Stage[B] -> Stage[A>>B]",
        compose=stage_sequential,
        description="Sequential stage composition with halt propagation"
    )

    ops["dialectic"] = Operation(
        name="dialectic",
        arity=2,
        signature="Orchestrator[CREATIVE] x Orchestrator[ADVERSARIAL] -> Orchestrator[SYNTHESIS]",
        compose=dialectic_composition,
        description="Parallel dialectical composition with contradiction resolution"
    )

    ops["witness_wrap"] = Operation(
        name="witness_wrap",
        arity=1,
        signature="Stage -> WitnessedStage",
        compose=wrap_with_witness,
        description="Add witness mark emission to stage output"
    )

    ops["halt_branch"] = Operation(
        name="halt_branch",
        arity=3,
        signature="Pred x Stage x Halt -> ConditionalStage",
        compose=halt_on_failure,
        description="Branch to HALT if predicate (failure) is true"
    )

    ops["omega_guard"] = Operation(
        name="omega_guard",
        arity=2,
        signature="OmegaAxiom x Stage -> GuardedStage",
        compose=omega_guard,
        description="Ensure Omega-layer axiom is preserved by stage"
    )

    return Operad(
        name="REGENERATION_OPERAD",
        operations=ops,
        laws=regeneration_laws(),
        description="Grammar for pilot regeneration composition"
    )
```

### 2.2 Laws

Beyond the universal laws (associativity, identity), REGENERATION_OPERAD enforces:

```python
def regeneration_laws() -> list[Law]:
    """
    Laws specific to regeneration composition.
    """
    return [
        # Inherited from AGENT_OPERAD
        *AGENT_OPERAD.laws,

        # Omega-layer preservation
        Law(
            name="omega_0_composition",
            equation="stage_seq(stage_seq(a,b),c) = stage_seq(a,stage_seq(b,c))",
            verify=verify_stage_associativity,
            description="Omega-0: Stages compose associatively"
        ),

        Law(
            name="omega_1_witnessing",
            equation="forall stage s: completed(s) => exists mark m: witnesses(m, s)",
            verify=verify_all_stages_witnessed,
            description="Omega-1: Every completed stage has a witness mark"
        ),

        Law(
            name="omega_2_coherence",
            equation="dialectic(c, a).output = synthesis(c.output, a.output)",
            verify=verify_dialectic_coherence,
            description="Omega-2: Dialectic produces coherent synthesis"
        ),

        Law(
            name="omega_4_tabula_rasa",
            equation="generate_stage.input NOT_IN previous_run.artifacts",
            verify=verify_tabula_rasa,
            description="Omega-4: Generation doesn't read previous implementations"
        ),

        Law(
            name="omega_5_full_implementation",
            equation="forall law L in spec: exists impl I: implements(I, L)",
            verify=verify_full_implementation,
            description="Omega-5: All spec laws have implementations"
        ),

        # Dialectic laws
        Law(
            name="dialectic_symmetry",
            equation="dialectic(c, a).synthesis = dialectic(a, c).synthesis",
            verify=verify_dialectic_symmetry,
            description="Synthesis is independent of argument order"
        ),

        Law(
            name="contradiction_resolution",
            equation="dialectic(c, a).contradictions_pending = 0 => dialectic(c, a).complete = true",
            verify=verify_contradiction_resolution,
            description="No pending contradictions means dialectic is complete"
        ),

        # Halt propagation
        Law(
            name="halt_propagation",
            equation="stage_seq(HALT, s) = HALT",
            verify=verify_halt_left_zero,
            description="HALT is a left-zero for stage composition"
        ),

        Law(
            name="halt_idempotent",
            equation="HALT = HALT >> HALT",
            verify=verify_halt_idempotent,
            description="HALT composed with HALT is still HALT"
        ),
    ]
```

### 2.3 The Full Pipeline as Operad Expression

The regeneration pipeline is expressible in the operad grammar:

```
REGENERATION_PIPELINE =
  omega_guard(Omega_4,
    witness_wrap(
      stage_seq(
        ARCHIVE,
        halt_branch(NO_GO,
          stage_seq(
            AUDIT,
            halt_branch(FAIL,
              stage_seq(
                SANITY,
                stage_seq(
                  GENERATE,
                  stage_seq(
                    WIRE,
                    halt_branch(SMOKE_FAIL,
                      stage_seq(
                        SMOKE,
                        stage_seq(
                          VALIDATE,
                          LEARN
                        )
                      ),
                      HALT_RETURN_TO_GENERATE
                    )
                  )
                )
              ),
              HALT
            )
          ),
          HALT
        )
      )
    )
  )
```

---

## Part III: Sheaf Design (Multi-Orchestrator Coherence)

### 3.1 The Regeneration Sheaf

A **sheaf** captures how local views (individual orchestrator states) glue into a global coherent state (the shared outline).

```python
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

T = TypeVar("T")

@dataclass
class LocalView(Generic[T]):
    """
    A local view in the sheaf.

    Each orchestrator has a local view of the regeneration state.
    """
    agent_id: str                # "creative" | "adversarial"
    value: T                     # Local state
    timestamp: float             # For staleness detection
    version: int                 # For conflict detection

@dataclass
class GluingCondition:
    """
    Condition for gluing local views into global section.
    """
    name: str
    check: Callable[[LocalView, LocalView], bool]
    merge: Callable[[LocalView, LocalView], Any]

@dataclass
class RegenerationSheaf:
    """
    Sheaf over the coordination space.

    Base space: {CREATIVE, ADVERSARIAL} (the orchestrator set)
    Stalks: OrchestratorState at each orchestrator
    Sections: Consistent global states (the outline)

    Gluing axiom: If local views agree on overlaps (shared files),
    they glue into a unique global section.
    """

    # Local views (stalks)
    creative_view: LocalView[dict]
    adversarial_view: LocalView[dict]

    # Gluing conditions
    gluing_conditions: list[GluingCondition]

    def sections_agree(self) -> bool:
        """
        Check if local sections agree on overlaps.

        The overlaps are:
        - .outline.md (both read/write)
        - .sync_state.json (both read/write)
        - components_ready (CREATIVE writes, ADVERSARIAL reads)
        - components_reviewed (ADVERSARIAL writes, CREATIVE reads)
        - contradictions (ADVERSARIAL writes, CREATIVE reads)
        """
        for condition in self.gluing_conditions:
            if not condition.check(self.creative_view, self.adversarial_view):
                return False
        return True

    def glue(self) -> dict:
        """
        Glue local views into global section (the outline).

        Precondition: sections_agree() == True
        """
        if not self.sections_agree():
            raise ValueError("Cannot glue: local sections do not agree on overlaps")

        global_section = {}
        for condition in self.gluing_conditions:
            merged = condition.merge(self.creative_view, self.adversarial_view)
            global_section.update(merged)

        return global_section

# Standard gluing conditions for regeneration
OUTLINE_GLUING = GluingCondition(
    name="outline_consistency",
    check=lambda c, a: c.value.get("iteration") == a.value.get("iteration"),
    merge=lambda c, a: {
        "iteration": c.value.get("iteration"),
        "phase": c.value.get("phase"),
        "components": {**c.value.get("components", {}), **a.value.get("reviewed", {})}
    }
)

COMPONENT_GLUING = GluingCondition(
    name="component_ownership",
    check=lambda c, a: len(
        set(c.value.get("claimed", [])) & set(a.value.get("claimed", []))
    ) == 0,  # No double-claiming
    merge=lambda c, a: {
        "creative_components": c.value.get("claimed", []),
        "adversarial_components": a.value.get("claimed", [])
    }
)

CONTRADICTION_GLUING = GluingCondition(
    name="contradiction_resolution",
    check=lambda c, a: all(
        r.get("resolved", False)
        for r in a.value.get("contradictions", [])
        if r.get("severity") == "critical"
    ),  # All critical contradictions resolved
    merge=lambda c, a: {
        "contradictions_resolved": [
            r for r in a.value.get("contradictions", [])
            if r.get("resolved", False)
        ],
        "contradictions_pending": [
            r for r in a.value.get("contradictions", [])
            if not r.get("resolved", False)
        ]
    }
)
```

### 3.2 File-Based Transaction Protocol

The sheaf is realized via file-based transactions in `/tmp/kgents-regen/{pilot}/`:

```python
import fcntl
from pathlib import Path

class CoordinationLattice:
    """
    File-based realization of the Regeneration Sheaf.

    Each file is a stalk. Locks ensure gluing consistency.
    """

    def __init__(self, pilot_name: str):
        self.base_path = Path(f"/tmp/kgents-regen/{pilot_name}")
        self.base_path.mkdir(parents=True, exist_ok=True)

    def acquire_outline_lock(self) -> None:
        """Acquire exclusive lock on outline (atomic update)."""
        lock_path = self.base_path / ".outline.lock"
        lock_path.mkdir(exist_ok=False)  # mkdir is atomic

    def release_outline_lock(self) -> None:
        """Release outline lock."""
        lock_path = self.base_path / ".outline.lock"
        lock_path.rmdir()

    def claim_component(self, agent_id: str, component: str) -> bool:
        """
        Atomically claim a component.

        Uses mkdir for atomic check-and-claim.
        Returns True if claimed, False if already claimed.
        """
        claim_path = self.base_path / f".claim.{agent_id}" / component
        try:
            claim_path.mkdir(parents=True, exist_ok=False)
            return True
        except FileExistsError:
            return False

    def read_partner_state(self, my_id: str) -> LocalView:
        """Read partner's local view."""
        partner_id = "adversarial" if my_id == "creative" else "creative"
        focus_path = self.base_path / f".focus.{partner_id}.md"

        if not focus_path.exists():
            return LocalView(agent_id=partner_id, value={}, timestamp=0, version=0)

        content = focus_path.read_text()
        return LocalView(
            agent_id=partner_id,
            value=parse_focus_file(content),
            timestamp=focus_path.stat().st_mtime,
            version=hash(content)
        )

    def update_sync_state(self, agent_id: str, updates: dict) -> None:
        """
        Update shared sync state (atomic via lock).
        """
        sync_path = self.base_path / ".sync_state.json"

        self.acquire_outline_lock()
        try:
            import json
            if sync_path.exists():
                state = json.loads(sync_path.read_text())
            else:
                state = {}

            state[f"{agent_id}_updates"] = updates
            state["last_updated_by"] = agent_id

            sync_path.write_text(json.dumps(state, indent=2))
        finally:
            self.release_outline_lock()
```

### 3.3 Gluing Conditions as Invariants

The gluing conditions correspond to these invariants:

| Condition | File(s) | Invariant | Violation Detection |
|-----------|---------|-----------|---------------------|
| Iteration Sync | `.iteration` | Both agents on same iteration | `cat .iteration` differs between reads |
| Phase Agreement | `.phase` | Phase transitions are coordinated | Phase mismatch in `.sync_state.json` |
| No Double-Claim | `.claim.*/*` | Each component owned by one agent | `mkdir` fails on second claim |
| Contradiction Resolution | `.adversarial_insights.md` | Critical contradictions resolved before proceeding | Check for `severity: critical` with `resolved: false` |
| Outline Coherence | `.outline.md` | Single consistent outline | Lock contention during merge |

---

## Part IV: Witness Morphisms

### 4.1 Stage Witness Morphisms

Every stage emits a witness mark. The witness is a **morphism** from Stage output to the Witness store.

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class WitnessMorphism:
    """
    Morphism from stage output to witness mark.

    witness: StageOutput -> Mark

    Properties:
    - Preserves provenance (output.artifacts linked to mark.evidence)
    - Records decision trace (why this outcome)
    - Composable with stage (Stage >> Witness = WitnessedStage)
    """

    stage_name: str
    pilot_name: str
    run_number: int

    def to_mark(self, output: StageOutput) -> dict:
        """Transform stage output to witness mark command."""
        return {
            "action": f"Stage {self.stage_name} complete for {self.pilot_name} run-{self.run_number:03d}",
            "tag": "regeneration",
            "reasoning": f"Status: {output.status}, Artifacts: {output.artifacts}",
            "evidence": {
                "stage": self.stage_name,
                "status": output.status,
                "artifacts": output.artifacts,
                "next": output.next_stage
            }
        }

    def emit(self, output: StageOutput) -> str:
        """
        Emit witness mark and return mark ID.

        Uses km CLI command.
        """
        import subprocess
        import json

        mark_data = self.to_mark(output)
        cmd = [
            "km",
            mark_data["action"],
            "--tag", mark_data["tag"],
            "--json"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            return response.get("mark_id", "unknown")
        return "error"
```

### 4.2 Learning Stage Crystallization

The LEARN stage produces a special witness: the **crystallization morphism** that promotes learnings to spec amendments.

```python
@dataclass
class CrystallizationMorphism:
    """
    Morphism from LEARNINGS.md to spec amendments.

    This is the "learning loop closure" - insights crystallize into
    permanent spec changes.

    Path: LEARNINGS.md -> Human Review -> PROTO_SPEC amendment -> Next run reads spec

    Note: This is NOT automatic. The morphism prepares the amendment;
    humans must approve and commit.
    """

    pilot_name: str
    run_number: int

    def extract_amendments(self, learnings_content: str) -> list[dict]:
        """
        Extract spec amendment proposals from LEARNINGS.md.
        """
        amendments = []

        # Parse YAML-style learnings
        import re

        # Find spec_amendments section
        match = re.search(r'spec_amendments:\s*\n(.*?)(?=\n## |\Z)',
                          learnings_content, re.DOTALL)

        if match:
            # Parse amendment blocks
            amendment_text = match.group(1)
            # ... parsing logic ...
            amendments.append({
                "target": "PROTO_SPEC",  # or CONTRACT_COHERENCE, REGENERATE_META
                "section": "Laws",
                "amendment": "...",
                "rationale": "...",
                "expected_delta": "+X% success rate"
            })

        return amendments

    def crystallize(self, learnings_content: str) -> dict:
        """
        Prepare crystallization for witness store.
        """
        amendments = self.extract_amendments(learnings_content)

        return {
            "type": "crystallization",
            "source": f"pilots/{self.pilot_name}/runs/run-{self.run_number:03d}/LEARNINGS.md",
            "amendments": amendments,
            "status": "pending_review",  # Human must approve
            "command": f"kg crystallize --pilot {self.pilot_name} --run {self.run_number}"
        }
```

### 4.3 Dialectic Decision Witness

When CREATIVE and ADVERSARIAL reach synthesis, the decision is witnessed:

```python
@dataclass
class DialecticWitnessMorphism:
    """
    Witness for dialectic synthesis.

    Captures: Kent's view, Claude's view (here: CREATIVE vs ADVERSARIAL),
    the synthesis, and why.
    """

    pilot_name: str

    def witness_synthesis(
        self,
        topic: str,
        creative_view: str,
        creative_reasoning: str,
        adversarial_view: str,
        adversarial_reasoning: str,
        synthesis: str,
        why: str
    ) -> str:
        """
        Emit dialectic decision witness.

        Uses kg decide command.
        """
        import subprocess

        cmd = [
            "kg", "decide",
            "--kent", creative_view,
            "--kent-reasoning", creative_reasoning,
            "--claude", adversarial_view,
            "--claude-reasoning", adversarial_reasoning,
            "--synthesis", synthesis,
            "--why", why
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return f"Decision witnessed: {topic}"
        return f"Failed to witness: {result.stderr}"
```

---

## Part V: AGENTESE Integration

### 5.1 New AGENTESE Paths

The regeneration system registers these AGENTESE paths:

```
# Orchestrator paths
concept.regeneration.orchestrator.creative      # CREATIVE orchestrator node
concept.regeneration.orchestrator.adversarial   # ADVERSARIAL orchestrator node
concept.regeneration.orchestrator.dialectic     # Composed dialectic

# Stage paths
concept.regeneration.stage.archive              # Stage 1
concept.regeneration.stage.audit                # Stage 2
concept.regeneration.stage.sanity               # Stage 2.5
concept.regeneration.stage.generate             # Stage 3
concept.regeneration.stage.wire                 # Stage 3.5
concept.regeneration.stage.smoke                # Stage 3.6
concept.regeneration.stage.validate             # Stage 4
concept.regeneration.stage.learn                # Stage 5

# Pipeline paths
concept.regeneration.pipeline.full              # Full pipeline composition
concept.regeneration.pipeline.standard          # Standard mode (single session)
concept.regeneration.pipeline.swarm             # Swarm mode (3 terminals)

# Witness paths
time.regeneration.witness.stage                 # Stage witness morphism
time.regeneration.witness.dialectic             # Dialectic witness morphism
time.regeneration.witness.crystallize           # Learning crystallization

# Coordination paths
self.regeneration.lattice                       # Coordination lattice state
self.regeneration.sync                          # Sync with partner
self.regeneration.claim                         # Claim component
```

### 5.2 Node Registration

```python
from agents.agentese.gateway import node

@node("concept.regeneration.orchestrator.creative")
class CreativeOrchestratorNode:
    """
    CREATIVE orchestrator as AGENTESE node.
    """

    def __init__(self, pilot_name: str):
        self.polynomial = CREATIVE_POLYNOMIAL
        self.lattice = CoordinationLattice(pilot_name)
        self.phase = OrchestratorPhase.BOOTSTRAP

    async def invoke(self, input: Any) -> OrchestratorOutput:
        self.phase, output = self.polynomial.invoke(self.phase, input)
        return output

@node("concept.regeneration.pipeline.full")
class RegenerationPipelineNode:
    """
    Full regeneration pipeline as composed AGENTESE node.
    """

    def __init__(self, pilot_name: str):
        self.stages = [
            ARCHIVE_STAGE,
            AUDIT_STAGE,
            SANITY_STAGE,
            GENERATE_STAGE,
            WIRE_STAGE,
            SMOKE_STAGE,
            VALIDATE_STAGE,
            LEARN_STAGE
        ]

    async def invoke(self, context: dict) -> dict:
        """Execute full pipeline."""
        results = {}
        current_input = StageInput(context=context, previous_output=None)

        for stage in self.stages:
            state, output = stage.invoke(StagePhase.PENDING, current_input)
            results[stage.name] = output

            # Check for halt conditions
            if output.next_stage == "HALT":
                break

            current_input = StageInput(
                context=context,
                previous_output=output
            )

        return results
```

---

## Part VI: Zero Seed Derivation

### 6.1 L1-L2 Grounding

Every design decision is grounded in L1 (compositional) and L2 (relational) axioms:

| Decision | L1 Grounding | L2 Grounding | Galois Loss |
|----------|--------------|--------------|-------------|
| PolyAgent for orchestrators | Orchestrators ARE dynamical systems (state + mode-dependent behavior) | State IS position in polynomial | ~0 (exact representation) |
| Shared phase enum | Both agents traverse same space | Dialectic IS morphism between local views | ~0 (structural isomorphism) |
| Operad for composition | Stages COMPOSE associatively | Laws ARE equations (Omega axioms) | ~0 (laws preserved) |
| Sheaf for coherence | Local views GLUE into global | File transactions ARE gluing morphisms | ~0.05 (timing uncertainty) |
| Witness morphisms | Marks ARE provenance | Decisions ARE witnessed | ~0 (exact trace) |

### 6.2 Galois Loss Analysis

| Component | Conceptual Precision (G) | Implementation Fidelity (F) | Loss L = 1 - min(G,F) |
|-----------|--------------------------|-----------------------------|-----------------------|
| Orchestrator Polynomial | 0.95 | 0.90 | 0.10 |
| Stage Polynomial | 0.98 | 0.95 | 0.05 |
| REGENERATION_OPERAD | 0.92 | 0.85 | 0.15 |
| Regeneration Sheaf | 0.85 | 0.80 | 0.20 |
| Witness Morphisms | 0.98 | 0.98 | 0.02 |
| AGENTESE Paths | 0.95 | 0.90 | 0.10 |

**Aggregate Loss**: ~0.10 (acceptable for initial specification)

The highest-loss component is the **Sheaf** implementation, due to:
- File-system timing uncertainties
- Lock contention in high-parallelism scenarios
- Eventual consistency vs. strong consistency trade-offs

---

## Part VII: State Diagrams

### 7.1 Orchestrator State Machine

```
                              CREATIVE                                    ADVERSARIAL
                                 │                                             │
                                 ▼                                             ▼
                          ┌──────────┐                                  ┌──────────┐
                          │BOOTSTRAP │                                  │BOOTSTRAP │
                          │          │                                  │(waiting) │
                          └────┬─────┘                                  └────┬─────┘
                               │ Iteration(1)                                │ SyncEvent(partner=DESIGN)
                               ▼                                             ▼
                          ┌──────────┐     DesignDecision              ┌──────────┐
                          │  DESIGN  │◄─────────────────────────────────│  DESIGN  │
                          │  (1-3)   │────────────────────────────────► │(analyze) │
                          └────┬─────┘     ContradictionReveal          └────┬─────┘
                               │                                             │
                               │ Iteration(4)                                │ (follow partner)
                               ▼                                             ▼
                          ┌──────────┐     ComponentClaim              ┌──────────┐
                          │  BUILD   │◄─────────────────────────────────│  BUILD   │
                          │  (4-8)   │────────────────────────────────► │(analyze) │
                          └────┬─────┘     ContradictionReveal          └────┬─────┘
                               │                                             │
                               │ Iteration(9)                                │ SyncEvent(core_complete)
                               ▼                                             ▼
                          ┌──────────┐                                  ┌──────────┐
                          │ REFLECT  │                                  │EXPLORING │
                          │  (9-10)  │◄─────────────────────────────────│(partner) │
                          └────┬─────┘     ExplorationProposal          └────┬─────┘
                               │                                             │
                               │ Iteration(11+)                              │ (parallel)
                               ▼                                             ▼
                          ┌──────────┐                                  ┌──────────┐
                          │ COMPLETE │                                  │ COMPLETE │
                          └──────────┘                                  └──────────┘
```

### 7.2 Stage Pipeline State Machine

```
        ┌───────────┐
        │  ARCHIVE  │
        │   (S1)    │
        └─────┬─────┘
              │ success
              ▼
        ┌───────────┐
        │   AUDIT   │
        │   (S2)    │
        └─────┬─────┘
              │
      ┌───────┴───────┐
      │ GO            │ NO-GO
      ▼               ▼
┌───────────┐   ┌───────────┐
│  SANITY   │   │   HALT    │
│  (S2.5)   │   └───────────┘
└─────┬─────┘
      │
      ├─── PASS ───┬─── SKIP ───┐
      │            │            │
      ▼            ▼            ▼
┌───────────┐ ┌───────────┐ ┌───────────┐
│ GENERATE  │ │ GENERATE  │ │ GENERATE  │
│   (S3)    │ │   (S3)    │ │   (S3)    │
└─────┬─────┘ └─────┬─────┘ └─────┬─────┘
      │             │             │
      │ COMPLETE    │             │
      ▼             ▼             ▼
┌───────────┐
│   WIRE    │
│  (S3.5)   │
└─────┬─────┘
      │
      │ WIRED
      ▼
┌───────────┐
│   SMOKE   │
│  (S3.6)   │
└─────┬─────┘
      │
      ├─── PASS ───────────────────┐
      │                            │
      │ FAIL                       │
      ▼                            │
┌───────────┐                      │
│ (return   │                      │
│  to S3)   │                      │
└───────────┘                      │
                                   ▼
                           ┌───────────┐
                           │ VALIDATE  │
                           │   (S4)    │
                           └─────┬─────┘
                                 │
                           ┌─────┴─────┐
                           │           │
                           ▼           ▼
                     ┌───────────┐ ┌───────────┐
                     │   LEARN   │ │   LEARN   │
                     │   (S5)    │ │   (S5)    │
                     │  (PASS)   │ │  (FAIL)   │
                     └───────────┘ └───────────┘
```

---

## Part VIII: Implementation Roadmap

### Phase 1: Core Primitives (Est. 2 days)

1. **Create `impl/claude/agents/regen/polynomial.py`**
   - OrchestratorPhase enum
   - creative_directions / adversarial_directions
   - creative_transition / adversarial_transition
   - CREATIVE_POLYNOMIAL / ADVERSARIAL_POLYNOMIAL

2. **Create `impl/claude/agents/regen/stages.py`**
   - StagePhase enum
   - Stage polynomials (ARCHIVE, AUDIT, etc.)
   - Stage transition functions

### Phase 2: Operad & Sheaf (Est. 3 days)

4. **Create `impl/claude/agents/regen/operad.py`**
   - REGENERATION_OPERAD definition
   - Stage composition operations
   - Law verification functions

5. **Create `impl/claude/agents/regen/sheaf.py`**
   - RegenerationSheaf dataclass
   - Gluing conditions
   - CoordinationLattice file-based implementation

### Phase 3: Witness Integration (Est. 1 day)

6. **Create `impl/claude/agents/regen/witness.py`**
   - WitnessMorphism
   - CrystallizationMorphism
   - DialecticWitnessMorphism

### Phase 4: AGENTESE Nodes (Est. 2 days)

7. **Create `impl/claude/agents/regen/nodes.py`**
   - @node registrations
   - CreativeOrchestratorNode
   - AdversarialOrchestratorNode
   - RegenerationPipelineNode

8. **Update `impl/claude/agents/agentese/gateway.py`**
   - Import regen nodes
   - Register paths

### Phase 5: CLI Integration (Est. 1 day)

9. **Create `impl/claude/cli/regen.py`**
   - `kg regen` command group
   - `kg regen start --pilot <name> --role <creative|adversarial>`
   - `kg regen status --pilot <name>`
   - `kg regen witness --pilot <name> --run <n>`

---

## Appendix A: Derivation from Existing System

This specification is an **isomorphic** (structure-preserving) mapping from:

| Existing Component | Category-Theoretic Mapping |
|-------------------|---------------------------|
| Regeneration pipeline | REGENERATION_OPERAD.enumerate() |
| CREATIVE orchestrator | CREATIVE_POLYNOMIAL |
| ADVERSARIAL orchestrator | ADVERSARIAL_POLYNOMIAL |
| `.sync_state.json` | RegenerationSheaf.glue() |
| `.outline.md` | Global section (sheaf gluing result) |
| `km "Stage N..."` | WitnessMorphism.emit() |
| Stage transitions | Stage polynomial invoke() |
| Iteration loop | Orchestrator polynomial run() |

The mapping is **isomorphic** because:
1. States are preserved (positions)
2. Transitions are preserved (polynomial invoke)
3. Composition is preserved (operad laws)
4. Coherence is preserved (sheaf gluing)
5. Provenance is preserved (witness morphisms)

---

## Appendix B: Example Traces

### B.1 Simple Regeneration (Standard Mode)

```
> kg regen start --pilot zero-seed --mode standard

[1/8] ARCHIVE
  Position: PENDING -> SUCCEEDED
  Output: {status: "PASS", artifacts: ["MANIFEST.md"], mark: "mark_abc123"}

[2/8] AUDIT
  Position: PENDING -> SUCCEEDED
  Output: {status: "GO", artifacts: ["CONTRACT_AUDIT.md"], mark: "mark_def456"}

[3/8] SANITY
  Position: PENDING -> SKIPPED
  Output: {status: "SKIP", reason: "Backend unavailable", mark: "mark_ghi789"}

[4/8] GENERATE
  Position: PENDING -> SUCCEEDED
  Output: {status: "COMPLETE", files: 12, mark: "mark_jkl012"}

[5/8] WIRE
  Position: PENDING -> SUCCEEDED
  Output: {status: "WIRED", components: 5, mark: "mark_mno345"}

[6/8] SMOKE
  Position: PENDING -> SUCCEEDED
  Output: {status: "SMOKE_PASS", mark: "mark_pqr678"}

[7/8] VALIDATE
  Position: PENDING -> SUCCEEDED
  Output: {status: "PASS", qas: "5/5", mark: "mark_stu901"}

[8/8] LEARN
  Position: PENDING -> SUCCEEDED
  Output: {status: "COMPLETE", insights: 3, mark: "mark_vwx234"}

REGENERATION COMPLETE: zero-seed run-002 PASS
```

### B.2 Dialectic Regeneration (Swarm Mode)

```
Terminal 0 (Archive):
  > kg regen archive --pilot disney-portal
  [Archive complete. Context destroyed. Start dialectic in fresh terminals.]

Terminal 1 (Creative):
  > kg regen start --pilot disney-portal --role creative

  [Iteration 1/10] BOOTSTRAP
    Created: .outline.md, .iteration=1, .phase=DESIGN
    Waiting for partner...

  [Iteration 2/10] DESIGN
    Decision: Component structure (monolithic DayView)
    Claimed: DayView, PortalCard, HeightBadge

  [Iteration 3/10] DESIGN (sync)
    Received contradiction: "HeightBadge not accessible to screen readers"
    Resolution: Add aria-label, announce height verbally

  [Iteration 4/10] BUILD
    Component: DayView (340 lines)
    Component: PortalCard (120 lines)
    ...

Terminal 2 (Adversarial):
  > kg regen start --pilot disney-portal --role adversarial

  [Iteration 1/10] BOOTSTRAP
    Waiting for outline...

  [Iteration 2/10] DESIGN
    Analyzing: Component structure
    Contradiction: HeightBadge lacks accessibility
    Severity: important

  [Iteration 3/10] DESIGN
    Analyzed: DayView
    No contradictions found

  [Iteration 8/10] BUILD (mode shift)
    Core complete. Shifting to exploration partner.

  [Iteration 9/10] EXPLORING
    Proposal: "Add PhotoPass integration for ride photos"
    Effort: medium
    Joy: high (surprise family with action shots)

  [Iteration 10/10] EXPLORING
    DIALECTIC COMPLETE
    Contradictions: 4 revealed, 4 resolved
    Explorations: 2 proposed, 1 implemented
```

---

*"The proof IS the decision. The mark IS the witness. The polynomial IS the agent."*

*Filed: 2025-12-27 | Zero Seed Grounded | Galois Loss: ~0.10*
