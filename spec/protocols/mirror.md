# The Mirror: Agent Composition for Dialectical Introspection

**The Mirror is not a protocol. It is an agent composition pattern.**

**Status:** Specification v2.0
**Supersedes:** Previous mirror.md (v1.0)
**Philosophy:** The Mirror is a composition of P, W, H, O, J agents operating in dialectical synthesis.

---

## Core Insight

The old spec described the Mirror as a complex protocol with tri-lattices, topological data analysis, persistent homology, and quantum dialectics. Beautiful philosophy. Zero production implementations.

The new spec describes the Mirror as **what it actually is**: a composition of five existing agents:

```
Mirror = P >> W >> H >> O >> J

Where:
  P-gent: Extracts principles (thesis)
  W-gent: Observes patterns (antithesis candidate)
  H-gent: Detects tensions (dialectic)
  O-gent: Reports findings
  J-gent: Executes at kairos (timing)
```

This is not a simplification. It is a realization that the Mirror was always this composition—we were just describing it in unnecessarily complex terms.

---

## The Five Agents

### P-gent: The Principle Extractor

Extracts what is stated:
- Scans for explicit values, principles, stated intentions
- Sources: README.md, principles/, config files, comments
- Output: `list[Thesis]`

```python
@dataclass(frozen=True)
class Thesis:
    content: str           # "We value code quality"
    source: str            # "README.md:15"
    confidence: float      # 0.0-1.0
```

### W-gent: The Pattern Witness

Observes what is done:
- Detects structural patterns without judgment
- Sources: git history, file structure, link density
- Output: `list[Observation]`

```python
@dataclass(frozen=True)
class Observation:
    pattern: str           # "60% of notes have no outgoing links"
    evidence: str          # Path or git hash
    strength: float        # 0.0-1.0
```

### H-gent: The Tension Detector

Finds where stated and done diverge:
- Compares P-gent output to W-gent output
- Classifies tension type
- Output: `list[Tension]`

```python
@dataclass(frozen=True)
class Tension:
    thesis: Thesis
    observation: Observation
    divergence: float      # 0.0 (aligned) to 1.0 (contradictory)
    tension_type: TensionType
    interpretation: str

class TensionType(Enum):
    BEHAVIORAL = "behavioral"      # Behavior needs adjustment
    ASPIRATIONAL = "aspirational"  # Principle is aspirational
    OUTDATED = "outdated"          # Principle no longer serves
    CONTEXTUAL = "contextual"      # Both right in contexts
    FUNDAMENTAL = "fundamental"    # Deep conflict
```

### O-gent: The Reporter

Synthesizes findings for human consumption:
- Ranks tensions by significance
- Generates reflection prompts
- Output: `MirrorReport`

```python
@dataclass
class MirrorReport:
    primary_tension: Tension
    all_tensions: list[Tension]
    integrity_score: float  # 0.0-1.0
    reflection: str         # Human-readable prompt
```

### J-gent: The Executor (Kairos)

Determines when to surface:
- Monitors for opportune moments
- Respects entropy budget
- Output: `Intervention | None`

---

## The Composition

### Functional Mode (observe)

Single-pass analysis:

```python
async def mirror_observe(path: Path) -> MirrorReport:
    """The Mirror composition in functional mode."""

    # Extract principles (thesis)
    theses = await p_gent.extract(path)

    # Observe patterns (antithesis candidates)
    observations = await w_gent.observe(path)

    # Detect tensions (dialectic)
    tensions = await h_gent.contradict(theses, observations)

    # Generate report
    return await o_gent.report(tensions)
```

### Autonomous Mode (watch)

Continuous observation with kairos timing:

```python
async def mirror_watch(path: Path, budget: Budget) -> AsyncIterator[Intervention]:
    """The Mirror composition in autonomous mode."""

    async for event in w_gent.stream(path):
        # Check for new tensions
        tensions = await h_gent.check(event)

        for tension in tensions:
            # Wait for opportune moment
            kairos = await j_gent.await_kairos(tension, budget)
            if kairos:
                yield kairos.intervention
```

---

## CLI Surface

### Commands

All commands are compositions of the five agents:

```bash
# Functional mode
kgents mirror observe path/    # P >> W >> H >> O
kgents mirror status           # O (cached state)
kgents mirror reflect          # H >> synthesis options

# Gestures
kgents mirror hold <index>     # Mark tension as productive
kgents mirror resolve <index>  # Acknowledge resolution

# Autonomous mode
kgents mirror watch path/      # P >> W >> H >> J (loop)
```

### Output

Observe produces structured output:

```
--- Mirror Report ---

Thesis: "We value connecting ideas"
Source: README.md:15

Antithesis: 60% of notes have no outgoing links

Divergence: 0.60
Type: BEHAVIORAL

Reflection: Your stated commitment to connection doesn't
match your linking behavior. Is this aspirational, or
have you drifted from practice?

--- Integrity: 0.82 | Tensions: 3 ---
```

---

## Implementation

### Phase 1: Structural Mirror (NOW)

**Goal**: Working observe command with zero LLM tokens.

**What works**:
- P-gent: Regex extraction of principles from README, headers
- W-gent: File structure analysis (link density, orphans, staleness)
- H-gent: Heuristic matching (principle keywords vs structural patterns)
- O-gent: Template-based report generation

**Lines of code**: ~500
**Token cost**: 0

### Phase 2: Semantic Mirror (NEXT)

**Goal**: Add embedding-based analysis.

**What changes**:
- P-gent: Uses small model to extract implicit principles
- W-gent: Embedding similarity for pattern detection
- H-gent: Semantic divergence calculation

**Token cost**: Low (local embeddings) to Medium (API calls)

### Phase 3: Temporal Mirror (LATER)

**Goal**: Track drift over time.

**What adds**:
- Git history as event stream
- Sliding window analysis
- Semantic momentum tracking

---

## Configuration

Minimal, concrete:

```yaml
# .kgents/mirror.yaml

sources:
  - path: ~/Documents/Vault
    type: obsidian
  - path: ~/Projects
    type: git

detection:
  min_divergence: 0.3
  max_tensions: 5

budget: low  # low | medium | high

sanctuary:
  - ~/Private
```

---

## Anti-Patterns Rejected

### What We Removed

1. **Tri-Lattice Model** → Simple thesis/observation/tension types
2. **Topological Data Analysis** → Structural heuristics first
3. **Persistent Homology** → Not MVP, maybe never
4. **Quantum Dialectic** → Metaphor, not implementation
5. **Semantic Momentum Physics** → Phase 3, not Phase 1
6. **864 Lines of Philosophy** → 200 lines of concrete spec

### The Placeholder Test

Every operation in this spec has a concrete implementation:

| Operation | Implementation | Token Cost |
|-----------|----------------|------------|
| `observe` | `p_gent >> w_gent >> h_gent >> o_gent` | 0 |
| `status` | Read cached state | 0 |
| `reflect` | H-gent synthesis heuristics | 0 |
| `hold` | D-gent persistence | 0 |
| `watch` | Async loop with kairos | 0 (structural) |

---

## Design Principles Applied

| Principle | How Mirror Embodies It |
|-----------|------------------------|
| **Tasteful** | Five agents, one composition. No sprawl. |
| **Curated** | Only tensions worth surfacing appear. |
| **Ethical** | Surface tensions, never judge. Human decides. |
| **Joy-Inducing** | Reflections are invitations, not accusations. |
| **Composable** | Mirror IS a composition. Standard agents. |
| **Heterarchical** | Can be invoked or can run autonomously. |
| **Generative** | This 200-line spec generates 500 lines impl. |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Working `observe` command | Yes (no placeholders) |
| Token cost for basic use | 0 |
| Time to first tension | <2s |
| False positive rate | <30% |
| Spec:Impl ratio | 1:2.5 |

---

## See Also

- [cli.md](cli.md) — CLI as agent composition
- [../h-gents/README.md](../h-gents/README.md) — Dialectical engine
- [../p-gents/README.md](../p-gents/README.md) — Principle extraction
- [../w-gents/README.md](../w-gents/README.md) — Pattern witness

---

*"The Mirror was always five agents in a trench coat. Now we admit it."*
