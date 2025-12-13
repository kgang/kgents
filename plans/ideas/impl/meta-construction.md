---
path: ideas/impl/meta-construction
status: active
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Meta-Construction System for Emergent Agent Composition.
  Primitives compose into emergent experience via careful design OR chaotic happenstance.
  Based on polynomial functors, operads, and sheaf theory.
---

# Meta-Construction System: Primitives → Emergence

> *"Don't build agents. Build the machine that builds agents."*

**Purpose**: Replace 600+ enumerated ideas with generative machinery
**Theory**: Polynomial functors + Operads + Sheaves
**Outcome**: Careful design OR chaotic happenstance → valid compositions

---

## The Vision

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     META-CONSTRUCTION SYSTEM                             │
│                                                                          │
│    ┌──────────┐      ┌──────────┐      ┌──────────┐                     │
│    │PRIMITIVES│  +   │ OPERADS  │  +   │ SHEAVES  │  =  EMERGENCE       │
│    │(atoms)   │      │(grammar) │      │(gluing)  │                     │
│    └──────────┘      └──────────┘      └──────────┘                     │
│         │                 │                 │                            │
│         ▼                 ▼                 ▼                            │
│    Base agents      Composition       Local → Global                    │
│    Types            rules             behavior                           │
│    Operations       Wiring            Emergence                          │
│                                                                          │
│    ────────────────────────────────────────────────────────────         │
│                            ↓                                             │
│                      TWO PATHS                                           │
│              ┌──────────────────────────┐                               │
│              │                          │                               │
│         Careful Design          Chaotic Happenstance                    │
│         (intentional)           (void.* entropy)                        │
│              │                          │                               │
│              └──────────┬───────────────┘                               │
│                         ▼                                                │
│                  VALID COMPOSITION                                       │
│              (operad guarantees validity)                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Primitives (The Atoms)

### Primitive Agent Protocol

Every primitive agent is a **polynomial functor**:

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable, FrozenSet

S = TypeVar("S")  # State/Position
A = TypeVar("A")  # Input/Direction
B = TypeVar("B")  # Output

@dataclass(frozen=True)
class PolyAgent(Generic[S, A, B]):
    """
    Agent as polynomial functor.

    P(y) = Σ_{s ∈ positions} y^{directions(s)}

    Following Spivak's "Polynomial Functors: A Mathematical Theory of Interaction"
    """
    name: str
    positions: FrozenSet[S]
    directions: Callable[[S], FrozenSet[A]]
    transition: Callable[[S, A], tuple[S, B]]

    def invoke(self, state: S, input: A) -> tuple[S, B]:
        """Execute one step of the dynamical system."""
        assert state in self.positions, f"Invalid state: {state}"
        assert input in self.directions(state), f"Invalid input {input} for state {state}"
        return self.transition(state, input)

    def run(self, initial: S, inputs: list[A]) -> tuple[S, list[B]]:
        """Run the system through a sequence of inputs."""
        state = initial
        outputs = []
        for inp in inputs:
            state, out = self.invoke(state, inp)
            outputs.append(out)
        return state, outputs
```

### The Primitive Catalog

```python
# Layer 1 Primitives: The 13 Atoms

PRIMITIVES = {
    # Bootstrap (7)
    "id": PolyAgent(
        name="Id",
        positions=frozenset({"ready"}),
        directions=lambda s: frozenset({Any}),
        transition=lambda s, x: ("ready", x)
    ),
    "ground": PolyAgent(
        name="Ground",
        positions=frozenset({"grounded", "floating"}),
        directions=lambda s: frozenset({Query, Void}),
        transition=ground_transition
    ),
    "judge": PolyAgent(
        name="Judge",
        positions=frozenset({"deliberating", "decided"}),
        directions=lambda s: frozenset({Claim}) if s == "deliberating" else frozenset(),
        transition=judge_transition
    ),
    "contradict": PolyAgent(
        name="Contradict",
        positions=frozenset({"seeking", "found"}),
        directions=lambda s: frozenset({Thesis}),
        transition=contradict_transition
    ),
    "sublate": PolyAgent(
        name="Sublate",
        positions=frozenset({"analyzing", "synthesized"}),
        directions=lambda s: frozenset({Contradiction}),
        transition=sublate_transition
    ),
    "compose": PolyAgent(
        name="Compose",
        positions=frozenset({"ready"}),
        directions=lambda s: frozenset({AgentPair}),
        transition=compose_transition
    ),
    "fix": PolyAgent(
        name="Fix",
        positions=frozenset({"trying", "succeeded", "failed"}),
        directions=fix_directions,
        transition=fix_transition
    ),

    # Perception (3)
    "manifest": PolyAgent(
        name="Manifest",
        positions=frozenset({"observing"}),
        directions=lambda s: frozenset({Handle, Umwelt}),
        transition=manifest_transition
    ),
    "witness": PolyAgent(
        name="Witness",
        positions=frozenset({"recording", "replaying"}),
        directions=witness_directions,
        transition=witness_transition
    ),
    "lens": PolyAgent(
        name="Lens",
        positions=frozenset({"focused"}),
        directions=lambda s: frozenset({Agent, Selector}),
        transition=lens_transition
    ),

    # Entropy (3)
    "sip": PolyAgent(
        name="Sip",
        positions=frozenset({"thirsty", "sated"}),
        directions=lambda s: frozenset({EntropyRequest}) if s == "thirsty" else frozenset(),
        transition=sip_transition
    ),
    "tithe": PolyAgent(
        name="Tithe",
        positions=frozenset({"owing", "paid"}),
        directions=lambda s: frozenset({Offering}) if s == "owing" else frozenset(),
        transition=tithe_transition
    ),
    "define": PolyAgent(
        name="Define",
        positions=frozenset({"creating"}),
        directions=lambda s: frozenset({Spec}),
        transition=define_transition
    ),
}
```

### Primitive Properties

Every primitive satisfies:

1. **Finite positions**: State space is enumerable
2. **Type-indexed directions**: Inputs depend on current state
3. **Deterministic transitions**: Same state + input → same output
4. **Composable interface**: Compatible with operad operations

---

## Layer 2: Operads (The Grammar)

### The Agent Operad

```python
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class Operation:
    """An operation in the operad."""
    name: str
    arity: int  # Number of inputs
    signature: str  # Type signature
    compose: Callable[..., PolyAgent]  # Composition function

@dataclass
class Operad:
    """
    Grammar of composition.

    Following "Operads for Complex System Design" (Spivak et al.)
    """
    name: str
    operations: dict[str, Operation]
    laws: list[str]  # Equations that must hold

    def compose(self, op_name: str, *agents: PolyAgent) -> PolyAgent:
        """Apply an operation to agents."""
        op = self.operations[op_name]
        assert len(agents) == op.arity, f"{op_name} requires {op.arity} agents"
        return op.compose(*agents)

    def enumerate(self, primitives: list[PolyAgent], depth: int) -> list[PolyAgent]:
        """Generate all valid compositions up to given depth."""
        results = list(primitives)  # Depth 0
        for d in range(1, depth + 1):
            for op in self.operations.values():
                for combo in combinations_with_replacement(results, op.arity):
                    try:
                        composed = op.compose(*combo)
                        if composed not in results:
                            results.append(composed)
                    except TypeError:
                        pass  # Type mismatch, skip
        return results


# The Universal Agent Operad
AGENT_OPERAD = Operad(
    name="AgentOperad",
    operations={
        "seq": Operation(
            name="seq",
            arity=2,
            signature="Agent[A,B] × Agent[B,C] → Agent[A,C]",
            compose=sequential_compose
        ),
        "par": Operation(
            name="par",
            arity=2,  # Can be n-ary via currying
            signature="Agent[A,B] × Agent[A,C] → Agent[A, (B,C)]",
            compose=parallel_compose
        ),
        "branch": Operation(
            name="branch",
            arity=3,
            signature="Pred[A] × Agent[A,B] × Agent[A,B] → Agent[A,B]",
            compose=branch_compose
        ),
        "fix": Operation(
            name="fix",
            arity=2,
            signature="Pred[B] × Agent[A,B] → Agent[A,B]",
            compose=fix_compose
        ),
        "trace": Operation(
            name="trace",
            arity=1,
            signature="Agent[A,B] → Agent[A,B] (with observation)",
            compose=trace_compose
        ),
    },
    laws=[
        # Associativity
        "seq(seq(a, b), c) = seq(a, seq(b, c))",
        "par(par(a, b), c) = par(a, par(b, c))",

        # Identity
        "seq(id, a) = a",
        "seq(a, id) = a",

        # Distributivity
        "seq(branch(p, a, b), c) = branch(p, seq(a, c), seq(b, c))",

        # Trace naturality
        "seq(trace(a), b) = trace(seq(a, b))",
    ]
)
```

### Domain-Specific Operads

```python
# Soul Operad (K-gent compositions)
SOUL_OPERAD = Operad(
    name="SoulOperad",
    operations=AGENT_OPERAD.operations | {
        "introspect": Operation(
            name="introspect",
            arity=0,
            signature="() → Agent[Query, SoulInsight]",
            compose=lambda: seq(PRIMITIVES["ground"], seq(PRIMITIVES["manifest"], PRIMITIVES["witness"]))
        ),
        "shadow": Operation(
            name="shadow",
            arity=1,
            signature="Agent[A, Thesis] → Agent[A, Shadow]",
            compose=lambda a: seq(a, seq(PRIMITIVES["contradict"], jungian_project))
        ),
        "dialectic": Operation(
            name="dialectic",
            arity=2,
            signature="Agent[A, Thesis] × Agent[A, Antithesis] → Agent[A, Synthesis]",
            compose=lambda t, a: seq(par(t, a), PRIMITIVES["sublate"])
        ),
    },
    laws=AGENT_OPERAD.laws + [
        "shadow(dialectic(t, a)) = dialectic(shadow(t), shadow(a))",
    ]
)

# Parse Operad (P-gent compositions)
PARSE_OPERAD = Operad(
    name="ParseOperad",
    operations=AGENT_OPERAD.operations | {
        "confident": Operation(
            name="confident",
            arity=1,
            signature="Agent[str, ParseResult] → Agent[str, ConfidentParse]",
            compose=lambda p: trace(seq(p, confidence_annotate))
        ),
        "repair": Operation(
            name="repair",
            arity=2,
            signature="Agent[str, ParseResult] × Agent[Error, str] → Agent[str, ParseResult]",
            compose=lambda p, r: fix(lambda x: x.confidence > 0.5, seq(p, branch(is_error, r, id)))
        ),
    },
    laws=AGENT_OPERAD.laws
)

# Reality Operad (J-gent compositions)
REALITY_OPERAD = Operad(
    name="RealityOperad",
    operations=AGENT_OPERAD.operations | {
        "classify": Operation(
            name="classify",
            arity=1,
            signature="Agent[A, Claim] → Agent[A, Reality]",
            compose=lambda c: seq(c, reality_classifier)
        ),
        "collapse": Operation(
            name="collapse",
            arity=2,
            signature="Agent[A, B] × Agent[Chaotic, B] → Agent[A, B]",
            compose=lambda a, fallback: branch(
                lambda x: reality_classifier(x) != Reality.CHAOTIC,
                a,
                seq(const(VOID), fallback)
            )
        ),
    },
    laws=AGENT_OPERAD.laws
)
```

### Operad Algebras = CLI Commands

The CLI is an **O-algebra**: a functor from operad to implementation.

```python
class CLIAlgebra:
    """
    Functor: Operad → CLI Commands

    Each operad operation becomes a CLI handler.
    """

    def __init__(self, operad: Operad):
        self.operad = operad

    def to_cli(self, op_name: str) -> CLIHandler:
        """Convert operad operation to CLI handler."""
        op = self.operad.operations[op_name]

        async def handler(args: Namespace) -> int:
            # Parse inputs from args
            agent_inputs = self.parse_args(args, op.arity)
            # Compose using operad
            composed = self.operad.compose(op_name, *agent_inputs)
            # Execute
            result = composed.run(initial_state, args.input)
            # Output
            print(format_result(result))
            return 0

        return handler

    def register_all(self, cli: CLI) -> None:
        """Register all operad operations as CLI commands."""
        for op_name in self.operad.operations:
            cli.register(
                f"kg {self.operad.name.lower().replace('operad', '')} {op_name}",
                self.to_cli(op_name)
            )

# Usage: Automatic CLI generation
soul_cli = CLIAlgebra(SOUL_OPERAD)
soul_cli.register_all(kg_cli)
# Creates: kg soul introspect, kg soul shadow, kg soul dialectic
```

---

## Layer 3: Sheaves (Emergence)

### The Agent Sheaf

```python
from dataclasses import dataclass
from typing import Dict, TypeVar, Generic

Ctx = TypeVar("Ctx")  # Context type

@dataclass
class AgentSheaf(Generic[Ctx]):
    """
    Sheaf structure for emergent behavior.

    Local agents (per-context) glue into global agent.
    Following Mac Lane & Moerdijk's "Sheaves in Geometry and Logic"
    """
    contexts: set[Ctx]
    overlap: Callable[[Ctx, Ctx], Ctx | None]  # Intersection of contexts

    def restrict(self, agent: PolyAgent, subcontext: Ctx) -> PolyAgent:
        """Restrict agent behavior to subcontext."""
        restricted_positions = frozenset(
            s for s in agent.positions
            if self.position_in_context(s, subcontext)
        )
        return PolyAgent(
            name=f"{agent.name}|{subcontext}",
            positions=restricted_positions,
            directions=lambda s: agent.directions(s) if s in restricted_positions else frozenset(),
            transition=agent.transition
        )

    def compatible(self, locals: Dict[Ctx, PolyAgent]) -> bool:
        """Check if local agents agree on overlaps."""
        for ctx1, agent1 in locals.items():
            for ctx2, agent2 in locals.items():
                if ctx1 == ctx2:
                    continue
                overlap = self.overlap(ctx1, ctx2)
                if overlap is not None:
                    r1 = self.restrict(agent1, overlap)
                    r2 = self.restrict(agent2, overlap)
                    if not self.agents_equal(r1, r2):
                        return False
        return True

    def glue(self, locals: Dict[Ctx, PolyAgent]) -> PolyAgent:
        """
        Glue compatible local agents into global agent.

        This is where EMERGENCE happens: the global agent has
        behaviors that no single local agent has.
        """
        assert self.compatible(locals), "Local agents not compatible on overlaps"

        # Global positions = union of local positions
        global_positions = frozenset().union(*(
            a.positions for a in locals.values()
        ))

        # Global directions = context-aware union
        def global_directions(s):
            for ctx, agent in locals.items():
                if s in agent.positions:
                    return agent.directions(s)
            return frozenset()

        # Global transition = dispatch to appropriate local
        def global_transition(s, inp):
            for ctx, agent in locals.items():
                if s in agent.positions and inp in agent.directions(s):
                    return agent.transition(s, inp)
            raise ValueError(f"No local agent handles state {s} with input {inp}")

        return PolyAgent(
            name=f"Glued({', '.join(a.name for a in locals.values())})",
            positions=global_positions,
            directions=global_directions,
            transition=global_transition
        )


# The Soul Sheaf
SOUL_SHEAF = AgentSheaf(
    contexts={
        "aesthetic",     # Taste, beauty
        "categorical",   # Structure, types
        "gratitude",     # Sacred, appreciation
        "heterarchy",    # Peer, non-hierarchical
        "generativity",  # Creation, emergence
        "joy",           # Delight, play
    },
    overlap=eigenvector_overlap  # How eigenvector contexts intersect
)
```

### Emergent Soul Example

```python
# Local soul agents (one per eigenvector context)
local_souls = {
    "aesthetic": PolyAgent(
        name="AestheticSoul",
        positions=frozenset({"minimalist", "baroque"}),
        directions=lambda s: frozenset({AestheticQuery}),
        transition=aesthetic_judgment  # "Does this need to exist?"
    ),
    "categorical": PolyAgent(
        name="CategoricalSoul",
        positions=frozenset({"abstract", "concrete"}),
        directions=lambda s: frozenset({StructureQuery}),
        transition=categorical_judgment  # "What's the morphism?"
    ),
    "joy": PolyAgent(
        name="JoySoul",
        positions=frozenset({"playful", "austere"}),
        directions=lambda s: frozenset({JoyQuery}),
        transition=joy_judgment  # "Where's the delight?"
    ),
    # ... other eigenvectors
}

# Glue into emergent global soul
KENT_SOUL = SOUL_SHEAF.glue(local_souls)

# The global soul has EMERGENT behavior:
# - In "minimalist" + "abstract" state, it asks:
#   "What's the simplest morphism?"
# - This question exists in neither local agent alone
```

---

## The Two Paths: Design vs. Happenstance

### Path 1: Careful Design

```python
def careful_compose(operad: Operad, operations: list[str]) -> PolyAgent:
    """
    Intentional composition via explicit operation sequence.

    The developer specifies exactly which operations to apply.
    """
    result = PRIMITIVES["id"]
    for op_name in operations:
        if op_name in PRIMITIVES:
            # Binary operation with primitive
            result = operad.compose("seq", result, PRIMITIVES[op_name])
        else:
            # Operad operation
            result = operad.compose(op_name, result)
    return result

# Usage
soul_pipeline = careful_compose(
    SOUL_OPERAD,
    ["ground", "introspect", "shadow", "dialectic"]
)
```

### Path 2: Chaotic Happenstance

```python
import random

async def chaotic_compose(
    operad: Operad,
    primitives: list[PolyAgent],
    entropy: float = 0.5,
    max_depth: int = 5
) -> PolyAgent:
    """
    Stochastic composition via void.* entropy.

    The operad GUARANTEES validity. Entropy introduces variation.
    """
    # Draw from accursed share
    seed = await logos.invoke("void.entropy.sip", {"amount": entropy})

    current = random.choice(primitives)

    for _ in range(max_depth):
        # Random operation
        op = random.choice(list(operad.operations.values()))

        # Random compatible agents
        try:
            args = [current]
            for _ in range(op.arity - 1):
                # Type-guided random selection
                compatible = [p for p in primitives if types_match(p, op, len(args))]
                if compatible:
                    args.append(random.choice(compatible))
                else:
                    break

            if len(args) == op.arity:
                current = op.compose(*args)

        except TypeError:
            # Incompatible types, try again
            continue

        # Early termination based on entropy
        if random.random() > entropy:
            break

    # Tithe gratitude for the gift
    await logos.invoke("void.gratitude.tithe", {"offering": current.name})

    return current

# Usage
emergent_agent = await chaotic_compose(
    SOUL_OPERAD,
    list(PRIMITIVES.values()),
    entropy=0.7,
    max_depth=4
)
# Result: Unpredictable but VALID composition
```

### The Key Insight

Both paths produce **valid compositions** because:
1. The **operad** defines what compositions are legal
2. The **types** constrain what can connect
3. The **sheaf conditions** ensure gluing is coherent

Chaos introduces *variation*. Structure ensures *validity*.

---

## DevEx Integration

### The Spec Projector Functor

```python
class SpecProjector:
    """
    Functor: Spec → Implementation

    Specs generate implementations, not vice versa.
    """

    def project_operad(self, operad: Operad) -> dict[str, Any]:
        """Generate CLI, tests, and docs from operad."""
        return {
            "cli_handlers": self.project_cli(operad),
            "tests": self.project_tests(operad),
            "docs": self.project_docs(operad),
        }

    def project_cli(self, operad: Operad) -> list[CLIHandler]:
        """Operad operations → CLI handlers."""
        return [CLIAlgebra(operad).to_cli(op) for op in operad.operations]

    def project_tests(self, operad: Operad) -> list[Test]:
        """Operad laws → pytest tests."""
        tests = []
        for law in operad.laws:
            tests.append(self.law_to_test(law))
        return tests

    def project_docs(self, operad: Operad) -> str:
        """Operad → markdown documentation."""
        doc = f"# {operad.name}\n\n"
        doc += "## Operations\n\n"
        for name, op in operad.operations.items():
            doc += f"### `{name}`\n"
            doc += f"- Arity: {op.arity}\n"
            doc += f"- Signature: `{op.signature}`\n\n"
        doc += "## Laws\n\n"
        for law in operad.laws:
            doc += f"- `{law}`\n"
        return doc

# Usage: Generate everything from operad
projector = SpecProjector()
soul_impl = projector.project_operad(SOUL_OPERAD)
# soul_impl["cli_handlers"] → ready to register
# soul_impl["tests"] → ready to run
# soul_impl["docs"] → ready to publish
```

### Ghost Sensorium Integration

```python
# Extend Ghost with meta-construction awareness
class MetaGhostCollector(GhostCollector):
    """Collect meta-construction system health."""

    async def collect(self) -> CollectorResult:
        return CollectorResult(
            success=True,
            data={
                "primitives_count": len(PRIMITIVES),
                "operads": list(OPERAD_REGISTRY.keys()),
                "compositions_today": await self.count_compositions(),
                "chaos_entropy_used": await self.entropy_usage(),
                "sheaf_gluings": await self.gluing_count(),
            }
        )

# Project to ghost files
# .kgents/ghost/meta.json shows meta-construction health
```

---

## Implementation Roadmap

### Phase 1: Polynomial Primitives (Week 1-2)

```
Tasks:
- [ ] Define PolyAgent protocol
- [ ] Convert 7 bootstrap agents to polynomial form
- [ ] Add position/direction/transition to Agent base
- [ ] Tests for polynomial laws
```

### Phase 2: Universal Operad (Week 3-4)

```
Tasks:
- [ ] Define Operad dataclass
- [ ] Implement seq, par, branch, fix, trace operations
- [ ] Verify operad laws at runtime
- [ ] Tests for associativity, identity, distributivity
```

### Phase 3: Domain Operads (Week 5-6)

```
Tasks:
- [ ] SOUL_OPERAD with introspect, shadow, dialectic
- [ ] PARSE_OPERAD with confident, repair
- [ ] REALITY_OPERAD with classify, collapse
- [ ] Tests for domain-specific laws
```

### Phase 4: Sheaf Emergence (Week 7-8)

```
Tasks:
- [ ] Define AgentSheaf with restrict/glue
- [ ] SOUL_SHEAF over eigenvector contexts
- [ ] Verify gluing conditions
- [ ] Tests for emergence properties
```

### Phase 5: Two Paths (Week 9-10)

```
Tasks:
- [ ] careful_compose for intentional design
- [ ] chaotic_compose with void.* entropy
- [ ] Integration with AGENTESE void context
- [ ] Tests for validity under both paths
```

### Phase 6: DevEx Projection (Week 11-12)

```
Tasks:
- [ ] SpecProjector functor
- [ ] Automatic CLI from operads
- [ ] Automatic tests from laws
- [ ] Automatic docs from signatures
```

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Primitives as polynomials | 13+ primitives converted |
| Operad coverage | 3+ domain operads |
| Sheaf gluings | Soul emergence working |
| Careful design path | 10+ valid compositions |
| Chaotic path | 100+ valid random compositions |
| DevEx projection | CLI auto-generated from operad |
| Law verification | 100% operad laws tested |

---

## The Meta-Insight

The 600+ ideas from creative exploration are **instances**.
The meta-construction system produces **the space of instances**.

```
Before: 600 ideas (finite, enumerated)
After:  Operad × Primitives × Entropy → ∞ valid compositions (infinite, generated)
```

This is the shift from **documentation** to **specification**.
From **output** to **grammar**.
From **enumeration** to **generation**.

The careful designer and the chaotic explorer arrive at the same garden—one through intention, one through happenstance. Both paths are valid because the operad guarantees it.

---

*"Build the machine that builds the machines."*

---

## References

- [Polynomial Functors](https://arxiv.org/abs/2312.00990) - Niu & Spivak
- [Operads for Complex System Design](https://royalsocietypublishing.org/doi/10.1098/rspa.2021.0099) - Spivak et al.
- [Sheaves in Geometry and Logic](https://link.springer.com/book/10.1007/978-1-4612-0927-0) - Mac Lane & Moerdijk
- [AlgebraicJulia](https://blog.algebraicjulia.org/) - Compositional dynamical systems
- [Category Theory for Programmers](https://github.com/hmemcpy/milewski-ctfp-pdf) - Milewski
- [Programming with Categories](http://brendanfong.com/programmingcats.html) - Fong, Milewski, Spivak
