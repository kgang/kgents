# Chrysalis: Agent Morphology Transformation

> *"The caterpillar becomes the butterfly not by growing wings, but by dissolving and reforming."*

**Status:** Spec v1.0
**Origin:** Migrated from Y-gent somatic topology (archived)
**Dependency:** Ω-gent (provides new body), Turn Protocol (manages transition)

---

## Purpose

When an agent needs to transform its morphology significantly (scale replicas, add GPU, change storage class), it cannot do so instantaneously. The **Chrysalis** is the liminal state during morphology transformation—the agent exists but is between forms.

**Why this needs to exist** (Tasteful principle):

Without Chrysalis, morphology changes are either:
1. **Abrupt**: Old pod killed, new pod started, state lost
2. **Impossible**: Agent stuck in current form forever

Chrysalis provides **graceful morphology transition** with state preservation.

---

## The Core Insight

Traditional Kubernetes treats pod replacement as "kill old, start new." This ignores that agents have:
- **State** that must survive the transition
- **Context** that shouldn't be interrupted
- **Identity** that persists across bodies

Chrysalis formalizes the transition:

```
Agent(Body_old) -> Chrysalis(Seed, Body_old, Body_new) -> Agent(Body_new)
```

The agent's **seed** (essential state) is preserved while the body transforms.

---

## Formal Definition

### Chrysalis State Machine

```python
class ChrysalisState(Enum):
    """States of morphology transformation."""
    HARVESTING = "harvesting"   # Extracting seed from old body
    DISSOLVING = "dissolving"   # Old body terminating
    DREAMING = "dreaming"       # Seed exists, no body yet
    GERMINATING = "germinating" # New body starting
    EMERGED = "emerged"         # Transformation complete
    FAILED = "failed"           # Transformation failed
```

### State Transition Diagram

```
                    +--fail---> FAILED
                    |
HARVESTING ---> DISSOLVING ---> DREAMING ---> GERMINATING ---> EMERGED
    |               |              |              |
    +--fail---------+--fail--------+--fail--------+
```

### The SoulSeed

```python
@dataclass(frozen=True)
class SoulSeed:
    """
    The preserved essence during chrysalis.

    Everything the agent needs to resume:
    - Memory (D-gent state)
    - Context (current conversation/task)
    - Identity (K-gent persona parameters)
    - Pending work (queued requests)
    """
    agent_id: str
    memory_snapshot: bytes          # D-gent serialized state
    context_hash: str               # Current context reference
    persona_params: dict            # K-gent configuration
    pending_queue: list[Any]        # Unprocessed requests
    harvested_at: datetime
    old_morphology_signature: str   # Hash of old morphology
```

---

## Chrysalis Operations

### Enter Chrysalis

```python
@dataclass
class SomaticChrysalis:
    """
    Liminal state during morphology transformation.

    The agent exists but is between forms. State is preserved
    in the seed; new body is being prepared.
    """

    seed: SoulSeed
    old_morphology: Morphology
    new_morphology: Morphology
    state: ChrysalisState
    trace: list[str]              # What happened during transformation
    attempts: int = 0
    max_attempts: int = 10

    @classmethod
    async def enter(
        cls,
        agent: Agent,
        new_morphology: Morphology,
    ) -> "SomaticChrysalis":
        """
        Begin chrysalis transformation.

        1. Harvest soul seed from current form
        2. Record old morphology
        3. Enter HARVESTING state
        """
        seed = await agent.harvest_soul()
        return cls(
            seed=seed,
            old_morphology=agent.current_morphology,
            new_morphology=new_morphology,
            state=ChrysalisState.HARVESTING,
            trace=[f"[{datetime.now()}] Entered chrysalis"],
        )
```

### Dream Phase

```python
async def dream(self, thought: str) -> None:
    """
    Low-compute processing while waiting for new form.

    The chrysalis can:
    - Plan (prepare for what comes next)
    - Queue (accumulate incoming requests)
    - Log (record transformation progress)

    The chrysalis CANNOT:
    - Act on the world (no body)
    - Respond to users (no voice)
    - Process heavy compute (no resources)
    """
    if self.state != ChrysalisState.DREAMING:
        raise InvalidState("Can only dream while DREAMING")

    self.trace.append(f"[Dream] {thought}")
```

### Await New Body

```python
async def await_body(
    self,
    omega: OmegaGent,
    pod_watcher: PodWatcher,
) -> ThoughtPod:
    """
    Wait for Ω-gent to manifest new body.

    Polls until new pod is ready, with exponential backoff.
    """
    self.state = ChrysalisState.GERMINATING

    while self.attempts < self.max_attempts:
        self.attempts += 1

        # Check if new body is ready
        if await pod_watcher.is_running():
            self.trace.append(f"New body ready on attempt {self.attempts}")
            return await self.germinate(pod_watcher.pod)

        # Dream while waiting
        await self.dream(f"Waiting for body (attempt {self.attempts})...")

        # Exponential backoff
        await asyncio.sleep(2 ** self.attempts * 0.5)

    self.state = ChrysalisState.FAILED
    raise ChrysalisFailure(
        f"Body never ready after {self.attempts} attempts",
        trace=self.trace,
    )
```

### Germinate (Emerge)

```python
async def germinate(self, new_pod: ThoughtPod) -> ThoughtPod:
    """
    Implant preserved seed into new form.

    1. Restore D-gent memory state
    2. Restore K-gent persona
    3. Replay pending queue
    4. Mark transformation complete
    """
    self.state = ChrysalisState.GERMINATING

    # Restore state into new pod
    await new_pod.restore_state(self.seed)

    # Mark complete
    self.state = ChrysalisState.EMERGED
    self.trace.append(f"[{datetime.now()}] Emerged into new body")

    return new_pod
```

---

## Integration with Ω-gent

Chrysalis is orchestrated by Ω-gent, not managed independently.

### Morphology Change Flow

```
1. Agent requests morphology change via self.body.morph
2. Ω-gent computes new morphology
3. Ω-gent creates Chrysalis
4. Chrysalis harvests seed
5. Ω-gent terminates old pod (DISSOLVING)
6. Chrysalis enters DREAMING
7. Ω-gent manifests new pod (GERMINATING)
8. Chrysalis implants seed (EMERGED)
9. Agent resumes in new body
```

### Ω-gent API

```python
class OmegaGent:
    async def morph(
        self,
        agent_id: str,
        morpheme: Morpheme,
    ) -> Morphology:
        """
        Apply morpheme to running agent.

        If morphology changes significantly, enters chrysalis.
        Minor changes (env vars) may be hot-patched.
        """
        current = await self._get_current_morphology(agent_id)
        new_morphology = current >> morpheme

        if self._requires_chrysalis(current, new_morphology):
            return await self._chrysalis_transition(agent_id, new_morphology)
        else:
            return await self._hot_patch(agent_id, morpheme)

    def _requires_chrysalis(
        self,
        old: Morphology,
        new: Morphology,
    ) -> bool:
        """
        Determine if morphology change requires chrysalis.

        Chrysalis required for:
        - Resource changes (CPU, memory, GPU)
        - Replica changes
        - Storage changes
        - Image changes

        Hot-patch sufficient for:
        - Environment variable changes
        - Label/annotation changes
        - Some probe adjustments
        """
        return old.signature != new.signature
```

---

## Integration with Turn Protocol

The chrysalis transition is recorded as Turns in the Weave.

### Chrysalis Turns

```python
class ChrysalisTurnType(Enum):
    """Turn types specific to chrysalis transitions."""
    HARVEST = "chrysalis.harvest"     # Seed extracted
    DISSOLVE = "chrysalis.dissolve"   # Old body terminated
    DREAM = "chrysalis.dream"         # Processing while bodyless
    GERMINATE = "chrysalis.germinate" # Seed implanted
    EMERGE = "chrysalis.emerge"       # Transformation complete
    FAIL = "chrysalis.fail"           # Transformation failed
```

### Stability and Chrysalis

A chrysalis turn is **never stable** (state always changes during transformation). Fixed-point iteration should pause during chrysalis:

```python
def is_in_chrysalis(turn: Turn) -> bool:
    """Check if turn represents chrysalis state."""
    return turn.turn_type.value.startswith("chrysalis.")


def iterate_until_stable(agent, initial, max_iterations):
    for i in range(max_iterations):
        turn = await agent.invoke_with_turn(current)

        if is_in_chrysalis(turn):
            # Wait for chrysalis to complete
            await agent.await_chrysalis_complete()
            continue

        if is_stable(turn):
            return turn.content

        current = turn.content
```

---

## AGENTESE Integration

Chrysalis exposes state via `self.body.chrysalis.*` paths:

```
self.body.chrysalis.state    - Current ChrysalisState
self.body.chrysalis.trace    - Transformation trace log
self.body.chrysalis.attempts - Number of germination attempts
self.body.chrysalis.seed     - SoulSeed (if harvested)

# Check if currently in chrysalis
self.body.chrysalis.active   - bool: is transformation in progress?
```

### Example Usage

```python
# Agent sensing its own chrysalis state
if await logos.invoke("self.body.chrysalis.active", observer):
    trace = await logos.invoke("self.body.chrysalis.trace", observer)
    print(f"In chrysalis: {trace}")
```

---

## Population Topology

Chrysalis enables **agent population topology** operations inherited from Y-gent:

### Branch (Spawn Variants)

```python
async def branch_population(
    self,
    agent: Agent,
    count: int,
) -> list[Agent]:
    """
    Spawn N variants of an agent.

    Each variant gets a copy of the seed, then diverges.
    Used for: parallel search, A/B testing, redundancy.
    """
    seed = await agent.harvest_soul()
    variants = []

    for i in range(count):
        variant_morphology = agent.morphology >> with_variant_id(i)
        variant_pod = await self.omega.manifest(variant_morphology)
        await variant_pod.restore_state(seed)
        variants.append(variant_pod.agent)

    return variants
```

### Merge (Consolidate Variants)

```python
class MergeStrategy(Enum):
    """How to consolidate multiple agents."""
    WINNER = "winner"       # Best performer survives
    ENSEMBLE = "ensemble"   # All contribute to merged state
    CONSENSUS = "consensus" # Only agreed-upon state survives


async def merge_population(
    self,
    agents: list[Agent],
    strategy: MergeStrategy,
) -> Agent:
    """
    Consolidate multiple agents into one.

    Seeds are harvested, combined per strategy, then
    implanted into a single survivor.
    """
    seeds = [await a.harvest_soul() for a in agents]

    match strategy:
        case MergeStrategy.WINNER:
            winner = max(agents, key=lambda a: a.performance_score)
            # Terminate losers
            for agent in agents:
                if agent != winner:
                    await self.omega.terminate(agent)
            return winner

        case MergeStrategy.ENSEMBLE:
            merged_seed = self._ensemble_seeds(seeds)
            merged = await self._spawn_with_seed(merged_seed)
            for agent in agents:
                await self.omega.terminate(agent)
            return merged

        case MergeStrategy.CONSENSUS:
            consensus_seed = self._find_consensus(seeds)
            merged = await self._spawn_with_seed(consensus_seed)
            for agent in agents:
                await self.omega.terminate(agent)
            return merged
```

---

## CLI Commands

```bash
# Chrysalis operations
kgents body chrysalis status <agent>    # Show chrysalis state if any
kgents body chrysalis trace <agent>     # Show transformation trace
kgents body chrysalis abort <agent>     # Abort stuck chrysalis

# Population topology (via chrysalis)
kgents body branch <agent> --count=3    # Spawn variants
kgents body merge <agents...> --strategy=winner  # Consolidate
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Mitigation |
|--------------|---------|------------|
| **Seedless Chrysalis** | State lost during transformation | Always harvest seed before dissolving |
| **Eternal Dreaming** | Chrysalis never germinates | max_attempts + timeout |
| **Hot Chrysalis** | Processing during transformation | Only dream() allowed in chrysalis |
| **Parallel Chrysalis** | Same agent in multiple chrysalises | Lock agent during transformation |
| **Orphan Seed** | Seed exists but no germination | Garbage collection for stale seeds |

---

## Implementation Files

```
impl/claude/agents/omega/
├── chrysalis.py          # SomaticChrysalis, SoulSeed
├── population.py         # branch_population, merge_population
├── _tests/
│   ├── test_chrysalis.py
│   └── test_population.py

protocols/agentese/contexts/
├── self_body.py          # Extended with chrysalis.* paths
```

---

## Success Criteria

### Operational
- [ ] Agent can enter and exit chrysalis cleanly
- [ ] Seed preserves D-gent memory across transformation
- [ ] Pending requests survive chrysalis
- [ ] Failed chrysalis rolls back gracefully

### Topological
- [ ] branch_population creates N independent variants
- [ ] merge_population consolidates per strategy
- [ ] Variants can diverge then re-merge

### Observable
- [ ] Chrysalis turns appear in Weave
- [ ] `self.body.chrysalis.*` paths work
- [ ] CLI commands show chrysalis state

---

## See Also

- `README.md` - Ω-gent overview (morphology, proprioception)
- `morphemes.md` - Morpheme catalog
- `spec/protocols/turn.md` - Turn Protocol (chrysalis turns)
- `spec/y-gents-archived/` - Original Y-gent spec (chrysalis origin)

---

*"The chrysalis is not weakness—it is the courage to become."*
