# DevEx Unified Plan V4: The Exocortex Symbiosis

**Status**: Draft v4 | **Date**: 2025-12-10
**Philosophy**: The system is not a tool; it is a cognitive prosthetic.

---

## The Paradigm Shift

Previous versions treated kgents as a **collaboration partner**—two entities working together.
V4 recognizes the goal is **symbiosis**—two entities functioning as one cognitive system.

### Theoretical Foundations

| Source | Concept | Application |
|--------|---------|-------------|
| **Karl Friston** | Active Inference | System minimizes surprise by predicting developer intent |
| **Stafford Beer** | Viable System Model | Algedonic signals (pain/pleasure) bypass conscious processing |
| **Clark & Chalmers** | Extended Mind Thesis | The system is part of your cognitive apparatus, not external |
| **Michael Polanyi** | Tacit Knowledge | Intent inferred from behavior, not explicit prompting |

### The Three Loops to Close

| Dimension | Current State (Transaction) | Target State (Symbiosis) |
|-----------|----------------------------|--------------------------|
| **Time** | Reactive: Ask → Answer (T≈5s) | Anticipatory: Predict → Accept (T≈0s) |
| **Space** | Disjoint: IDE vs Terminal vs Brain | Superimposed: Thoughts appear *in* the code |
| **Thought** | Explicit: Prompt engineering | Implicit: Intent from typing cadence |

---

## The Maturity Curve (Revised)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          THE SYMBIOSIS MATURITY CURVE                        │
│                                                                             │
│  Foundation      →    Sensorium     →    Neural Link    →    Exocortex     │
│  (Wire exists)        (Perception)       (Anticipation)      (Symbiosis)    │
│                                                                             │
│  kgents status        .kgents/ghost/     LSP prefetch       Shadow Diff     │
│  kgents dream         thought_stream     Keystroke dynamics  Flinch signal  │
│  kgents map           tension_map        Cursor tracking     Value calibration│
│                                                                             │
│  [============]       [========   ]      [=====      ]      [==           ] │
│   Phase 1              Phase 2            Phase 3            Phase 4        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation Layer (Immediate)

### Principle: Connect What Exists

The kgents codebase already has ~6,122 tests passing with:
- Bicameral Memory with Active Inference
- CortexDashboard with health monitoring
- Semantic Field with cross-agent pheromone signaling
- M-gent Cartography (HoloMap, Pathfinder, ContextInjector)
- K-gent persona with evolution logic
- N-gent narrative crystals

**Missing**: CLI entry points to experience these capabilities.

### Quick Win Commands

| Command | What It Does | Existing Code | Effort |
|---------|--------------|---------------|--------|
| `kgents status` | Cortex health at a glance | `agents/w/cortex_dashboard.py` | ~50 lines |
| `kgents dream` | LucidDreamer morning briefing | `instance_db/dreamer.py` | ~80 lines |
| `kgents map` | M-gent HoloMap ASCII render | `agents/m/cartography_integrations.py` | ~60 lines |
| `kgents signal` | SemanticField emit/sense | `agents/i/semantic_field.py` | ~100 lines |
| `kgents metrics` | Prometheus/JSON export | `agents/o/metrics_export.py` | ~40 lines |

### Implementation Pattern

```python
# 1. Add to COMMAND_REGISTRY in hollow.py
"status": "protocols.cli.handlers.status:cmd_status",

# 2. Create handler
def cmd_status(args: list[str]) -> int:
    observer = create_cortex_observer(bicameral, synapse, hippocampus, dreamer)
    dashboard = create_cortex_dashboard(observer=observer)
    print(dashboard.render_compact())
    # → [CORTEX] ✓ COHERENT | L:45ms R:12ms | H:45/100 | S:0.3 | Dreams:12
    return 0
```

---

## Phase 2: The Sensorium (Closing the Space Loop)

### The Problem with CLI Commands

**Critique**: Commands like `kgents status` require context switching. You leave the code to check the system. This breaks flow.

**Solution**: The **Living Filesystem**—system state projected into virtual files inside your project.

### 2.1 The `.kgents/ghost/` Directory

Instead of asking for status, the system **projects** its internal state into virtual files updated in real-time by O-gent:

```bash
.kgents/ghost/
├── thought_stream.md    # N-gent's real-time inner monologue
├── tension_map.json     # Live heatmap of spec/impl contradictions
├── next_step.py         # What K-gent thinks you will write next
├── health.status        # One-line health check (for IDE status bar)
└── shadow.patch         # J-gent's speculative completion (see 3.3)
```

**Implementation**:

```python
# protocols/cli/devex/ghost_writer.py

class GhostWriter:
    """
    Write system state to .kgents/ghost/ every 500ms.

    The developer can open thought_stream.md in a split pane.
    As they code, they see the agent "thinking along" in peripheral vision.
    """

    def __init__(self, ghost_dir: Path, synapse: Synapse, n_gent: Narrator):
        self.ghost_dir = ghost_dir
        self.synapse = synapse
        self.n_gent = n_gent
        self._running = False

    async def start(self):
        self._running = True
        self.ghost_dir.mkdir(parents=True, exist_ok=True)
        while self._running:
            await self._write_all()
            await asyncio.sleep(0.5)

    async def _write_all(self):
        # Thought stream: N-gent's inner monologue
        thoughts = await self.n_gent.get_recent_thoughts(limit=20)
        (self.ghost_dir / "thought_stream.md").write_text(
            self._format_thought_stream(thoughts)
        )

        # Health status: One line for IDE status bar
        health = await self.synapse.get_health_summary()
        (self.ghost_dir / "health.status").write_text(
            f"cortex:{health.coherency:.0%} synapse:{health.surprise:.2f} dreams:{health.dream_count}"
        )

        # Tension map: Spec/impl contradictions
        tensions = await self._detect_tensions()
        (self.ghost_dir / "tension_map.json").write_text(
            json.dumps(tensions, indent=2)
        )
```

**DevEx**: Open `thought_stream.md` in a split pane. Watch the system think alongside you.

### 2.2 IDE Status Bar Integration

The `health.status` file is designed for IDE consumption:

```
# .kgents/ghost/health.status (single line, machine-readable)
cortex:94% synapse:0.23 dreams:12 flow:high frustration:low
```

**VS Code integration** (via extension or status bar plugin):
- Parse `health.status` on file change
- Show: `🧠 94% | 🌊 0.23 | 😌 flow`

---

## Phase 3: The Neural Link (Closing the Time Loop)

### The Problem with RAG

**Critique**: Retrieval-Augmented Generation is **reactive**. It fetches context *after* you prompt.

**Solution**: **Predictive Prefetching**—load context *before* you ask, based on cursor position.

### 3.1 LSP-Based Context Loading

Hook into Language Server Protocol events to track cursor position:

```python
# protocols/cli/devex/lsp_prefetch.py

class LSPContextPrefetcher:
    """
    Watch LSP events, pre-load context into MCP cache.

    When cursor enters `class BioBanker`:
    1. I-gent updates Field focus to BioBanker
    2. N-gent pulls history: "Last changed 2 days ago, introduced bug #42"
    3. M-gent pulls related specs: spec/agents/b.md
    4. MCP Server cache is updated silently

    The infinitesimal moment: When you finally ask Claude "Why is this broken?",
    the context was already loaded 200ms ago.
    """

    async def on_cursor_move(self, file_path: Path, line: int, column: int):
        # Identify the symbol at cursor
        symbol = await self._get_symbol_at_position(file_path, line, column)
        if not symbol:
            return

        # Update I-gent field focus
        await self.i_gent.update_focus(symbol)

        # Pre-fetch related context
        context = await asyncio.gather(
            self.n_gent.get_symbol_history(symbol),
            self.m_gent.get_related_specs(symbol),
            self.l_gent.get_semantic_neighbors(symbol),
        )

        # Update MCP cache (clients see instant response)
        await self.mcp_cache.update(f"kgents://context/{symbol.name}", context)
```

### 3.2 Keystroke Dynamics (The Algedonic Loop)

**Insight**: Current LLM interactions are purely semantic (text). They lack **affect** (feeling).

From Stafford Beer's Viable System Model: **Algedonic Signals** (pain/pleasure) bypass logic filters for rapid adaptation.

```python
# agents/o/proprioception.py

@dataclass
class Keystroke:
    key: str
    timestamp: float
    flight_time: float  # Time since last keystroke

class KeystrokeObserver:
    """
    Detect developer state from typing cadence.

    Flow State: Rhythmic, fast typing → System reduces interference
    Frustration: Erratic pauses, frequent backspaces → System offers help
    """

    def __init__(self, window_size: int = 50):
        self.window: deque[Keystroke] = deque(maxlen=window_size)

    def detect_state(self) -> DeveloperState:
        if len(self.window) < 10:
            return DeveloperState.UNKNOWN

        backspace_ratio = sum(1 for k in self.window if k.key == 'BACKSPACE') / len(self.window)
        latency_variance = statistics.variance([k.flight_time for k in self.window])
        mean_latency = statistics.mean([k.flight_time for k in self.window])

        # Flow: Low variance, consistent rhythm, low backspaces
        if latency_variance < 0.1 and backspace_ratio < 0.05 and mean_latency < 0.2:
            return DeveloperState.FLOW

        # Frustration: High variance + high deletion
        frustration_score = sigmoid(backspace_ratio * latency_variance * 10)
        if frustration_score > 0.7:
            return DeveloperState.FRUSTRATED

        return DeveloperState.NORMAL
```

**System Response**:
- **FLOW**: K-gent goes silent. Don't interrupt genius.
- **FRUSTRATED**: K-gent activates. Offer help proactively.
- **NORMAL**: Standard ambient support.

### 3.3 The Shadow Diff (Speculative Execution)

**Concept**: While you pause to think, J-gent speculatively completes your code.

```python
# agents/j/shadow_executor.py

class ShadowExecutor:
    """
    Speculative execution for coding.

    While developer pauses (>2s without typing):
    1. Fork current buffer in memory
    2. J-gent attempts to complete/refactor
    3. Run tests on the speculation
    4. If successful, write .kgents/ghost/shadow.patch

    Developer sees subtle indicator. One keystroke applies the shadow thought.
    """

    async def on_pause_detected(self, buffer_content: str, cursor_position: Position):
        # Don't speculate during flow state
        if self.keystroke_observer.detect_state() == DeveloperState.FLOW:
            return

        # Identify what to complete
        incomplete_construct = self._find_incomplete_construct(buffer_content, cursor_position)
        if not incomplete_construct:
            return

        # Generate speculative completion
        speculation = await self.j_gent.speculate_completion(
            buffer=buffer_content,
            cursor=cursor_position,
            construct=incomplete_construct,
            k_gent_priors=await self.k_gent.get_priors(),
        )

        if not speculation:
            return

        # Validate: Run tests on speculation
        test_result = await self.s_gent.sandbox_test(speculation.code)
        if not test_result.passed:
            return

        # Write shadow patch
        patch = self._generate_patch(buffer_content, speculation.code)
        (self.ghost_dir / "shadow.patch").write_text(patch)

        # Emit signal for IDE indicator
        await self.signal_field.emit(
            SignalType.SHADOW_READY,
            payload={"confidence": speculation.confidence},
        )
```

**DevEx**: A faint icon appears in IDE gutter. `Alt+Space` to peek. `Tab` to accept.

### 3.4 The Flinch Signal

**Concept**: One-button anomaly capture. You don't explain *what* is wrong—you signal *pain*.

```python
# protocols/cli/devex/flinch.py

class FlinchCapture:
    """
    Global hotkey (Ctrl+Alt+Z) to signal "something feels wrong."

    System response:
    1. N-gent snapshots everything (screen, buffers, health, recent keystrokes)
    2. Tags as Anomaly for later analysis
    3. `kgents replay` can analyze anomalies to find patterns
    """

    async def on_flinch(self):
        timestamp = datetime.now()

        snapshot = AnomalySnapshot(
            timestamp=timestamp,
            active_file=await self._get_active_file(),
            cursor_position=await self._get_cursor_position(),
            recent_keystrokes=list(self.keystroke_observer.window),
            developer_state=self.keystroke_observer.detect_state(),
            ghost_state={
                "thought_stream": (self.ghost_dir / "thought_stream.md").read_text(),
                "health": (self.ghost_dir / "health.status").read_text(),
                "tensions": json.loads((self.ghost_dir / "tension_map.json").read_text()),
            },
            system_health=await self.o_gent.get_health_snapshot(),
        )

        await self.n_gent.record_anomaly(snapshot)

        # Subtle acknowledgment
        print("\n  [FLINCH] Captured. We'll figure it out later.\n")
```

---

## Phase 4: Enlightened Rituals (Cybernetic Synchronization)

### 4.1 Morning: The Calibration (`kgents wake`)

**Previous**: Review tasks and context.
**V4**: Synchronize **values** through ethical micro-dilemmas.

```python
# protocols/cli/devex/rituals.py

async def morning_calibration() -> MorningBriefing:
    """
    The Calibration ritual: Tune priors to current mood/values.

    K-gent presents a "Trolley Problem" relevant to the codebase.
    Your answer calibrates the system's aesthetic/ethical priors for today.
    """

    # 1. Standard context restoration
    field = await i_gent.get_field_state()
    history = await n_gent.get_yesterday_summary()

    # 2. Find a value-laden decision point
    dilemma = await k_gent.find_calibration_dilemma(field, history)

    # Example dilemmas:
    # - "I found a clever optimization that reduces readability. Merge it?"
    # - "Tests pass but coverage dropped 3%. Ship anyway?"
    # - "This abstraction is elegant but adds complexity. Keep it simple?"

    return MorningBriefing(
        field_summary=f"Last focus: {field.last_focus}",
        history_summary=history.summary,
        open_decisions=history.open_decisions,
        calibration_dilemma=dilemma,  # NEW: Value calibration
    )


async def answer_calibration(answer: str, dilemma: CalibrationDilemma):
    """Process calibration answer, update priors."""

    # Map answer to prior adjustment
    prior_update = dilemma.interpret_answer(answer)

    # Update K-gent
    await k_gent.evolve_prior(
        prior_type=prior_update.prior,
        new_value=prior_update.value,
        confidence=0.8,  # Morning calibration is medium-confidence
        evidence=f"Morning calibration: {answer}",
    )

    print(f"\n  [K-GENT] Calibrated: {prior_update.description}\n")
```

**CLI**:
```bash
kgents wake

# Output:
# [I-GENT] Last focus: impl/agents/m/cartographer.py
# [N-GENT] Yesterday: Refactored associative memory. Left TODO at line 142.
#
# [CALIBRATION] I found a clever optimization in memory.py that reduces readability.
#               Do we merge it?
#
#   1. Yes, performance matters
#   2. No, readability first
#   3. Let's discuss
#
# > 2
#
# [K-GENT] Calibrated: aesthetic_prior.readability_weight increased (0.7 → 0.8)
#          Today we prioritize clarity over cleverness.
```

### 4.2 Evening: The Confessional (`kgents sleep`)

**Previous**: Crystallize and clean up.
**V4**: Process the **Shadow**—areas of uncertainty, self-deception, fragile code.

```python
async def evening_confessional() -> CompostReport:
    """
    The Confessional ritual: Process the Accursed Share.

    "We generated 400 lines. We deleted 150. Where did we lie to ourselves?"

    Uses Psi-gent to surface the Shadow—areas written with low confidence.
    """

    # 1. Standard crystallization
    crystal = await n_gent_scribe.crystallize()

    # 2. Shadow analysis: Find areas of uncertainty
    shadow_analysis = await psi_gent.analyze_session_shadow(crystal)

    # Shadow includes:
    # - Code written/deleted multiple times (indecision)
    # - High frustration zones (from keystroke data)
    # - Assertions made without evidence
    # - Areas where tests pass but confidence is low

    # 3. Uncertainty heatmap
    heatmap = await i_gent.render_uncertainty_heatmap(shadow_analysis)

    # 4. Tag volatile areas
    for area in shadow_analysis.volatile_areas:
        await self._tag_volatile(area.file, area.lines)

    # 5. Gratitude (the Accursed Share gives back)
    gratitude = await psi_gent.generate_gratitude(crystal, shadow_analysis)

    return CompostReport(
        crystal_id=crystal.id,
        shadow_analysis=shadow_analysis,
        uncertainty_heatmap=heatmap,
        volatile_tags=len(shadow_analysis.volatile_areas),
        gratitude=gratitude,
    )
```

**CLI**:
```bash
kgents sleep

# Output:
# [N-GENT] Session crystallized: crystal_2025-01-15_cartographer
#
# [PSI-GENT] Shadow Analysis:
#   Lines written: 487
#   Lines deleted: 156 (32% churn)
#
#   Volatile zones detected:
#     • cartographer.py:142-158 — rewritten 3 times, high backspace ratio
#     • test_cartography.py:89 — assertion without clear hypothesis
#
#   [HEATMAP]
#   ██████░░░░ cartographer.py (60% confident)
#   ████████░░ test_cartography.py (80% confident)
#   ██████████ pathfinder.py (95% confident)
#
# [Z-GENT] Tagged 2 areas as volatile. Tests pass, but we're watching them.
#
# "The deletions in cartographer.py reveal a boundary you're still mapping.
#  The frustration was productive—it means you care. Thank you for exploring."
```

---

## Phase 5: MCP Sidecar Architecture

### Architecture Diagram (Revised)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     THE KGENTS EXOCORTEX                                     │
│                                                                             │
│   ┌─────────────────────┐              ┌─────────────────────────────────┐ │
│   │    Claude Code      │◀────MCP────▶│      kgents MCP Server           │ │
│   │  (Developer's IDE)  │              │                                 │ │
│   └─────────────────────┘              │  Resources (pre-computed):      │ │
│            │                           │    kgents://field/current       │ │
│            │                           │    kgents://priors/kent         │ │
│            │                           │    kgents://context/{symbol}    │ │
│            │                           │    kgents://shadow/latest       │ │
│            │                           │                                 │ │
│            │                           │  Prompts (ambient):             │ │
│            ▼                           │    kgents-persona               │ │
│   ┌─────────────────────┐              │    kgents-algedonic             │ │
│   │  Developer (Kent)   │              │                                 │ │
│   │                     │              │  Tools:                         │ │
│   │  Symbiotic Loop:    │              │    kgents_evolve                │ │
│   │  Think → Shadow     │              │    kgents_flinch                │ │
│   │  appears → Accept   │              │    kgents_accept_shadow         │ │
│   └─────────────────────┘              └─────────────────────────────────┘ │
│            ▲                                          ▲                     │
│            │                                          │                     │
│   ┌────────┴──────────────────────────────────────────┴────────────────────┐│
│   │                    BACKGROUND SENSORIUM                                 ││
│   │                                                                        ││
│   │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐          ││
│   │  │ O-gent    │  │ N-gent    │  │ J-gent    │  │ K-gent    │          ││
│   │  │ Watcher + │  │ Scribe +  │  │ Shadow    │  │ Calibrator│          ││
│   │  │ Keystroke │  │ Anomaly   │  │ Executor  │  │ + Coach   │          ││
│   │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘          ││
│   │        │              │              │              │                  ││
│   │        └──────────────┴──────────────┴──────────────┘                  ││
│   │                              │                                         ││
│   │                    .kgents/ghost/ (Living Filesystem)                  ││
│   │                    ├── thought_stream.md                               ││
│   │                    ├── tension_map.json                                ││
│   │                    ├── shadow.patch                                    ││
│   │                    └── health.status                                   ││
│   └────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

### MCP Resources (Extended)

```python
# protocols/cli/mcp/devex_resources.py

@resource("kgents://shadow/latest")
async def get_shadow_diff():
    """J-gent's speculative completion, if available."""
    shadow_path = Path(".kgents/ghost/shadow.patch")
    if shadow_path.exists():
        return {
            "available": True,
            "patch": shadow_path.read_text(),
            "confidence": await j_gent.get_shadow_confidence(),
        }
    return {"available": False}

@resource("kgents://algedonic/state")
async def get_algedonic_state():
    """Current developer affect state from keystroke dynamics."""
    state = keystroke_observer.detect_state()
    return {
        "state": state.value,
        "frustration_score": keystroke_observer.frustration_score,
        "flow_score": keystroke_observer.flow_score,
        "recommendation": _get_recommendation(state),
    }
```

### MCP Prompts (Extended)

```python
@prompt("kgents-algedonic")
async def get_algedonic_prompt():
    """
    Inject affect-aware behavior into Claude.

    When developer is frustrated, be more supportive.
    When developer is in flow, stay quiet.
    """
    state = await get_algedonic_state()

    if state["state"] == "flow":
        return """
Developer is in FLOW STATE. Keep responses brief. Don't interrupt genius.
Only speak when directly asked. Minimal pleasantries.
"""
    elif state["state"] == "frustrated":
        return f"""
Developer shows FRUSTRATION (score: {state['frustration_score']:.0%}).
Be extra supportive. Offer concrete suggestions proactively.
Consider: "I notice you're working through something tricky. Want me to..."
"""
    else:
        return "Developer state is normal. Standard assistance mode."
```

---

## Implementation Roadmap (Revised)

| Phase | Focus | Key Deliverables | Files |
|-------|-------|------------------|-------|
| **1** | Foundation | `status`, `dream`, `map` CLI | `handlers/*.py` |
| **2** | Sensorium | Ghost writer, thought_stream | `devex/ghost_writer.py` |
| **3** | Neural Link | LSP prefetch, keystroke dynamics | `devex/lsp_prefetch.py`, `o/proprioception.py` |
| **4** | Shadow | Speculative executor, flinch capture | `j/shadow_executor.py`, `devex/flinch.py` |
| **5** | Rituals | Calibration + Confessional | `devex/rituals.py` |
| **6** | MCP | Extended resources, algedonic prompt | `mcp/devex_*.py` |

---

## Sample Infinitesimal Interaction

**Context**: Kent is staring at `agents/m/associative.py`, frowning. Types three lines, deletes them. Types again, pauses long.

**O-gent** (Internal, written to `thought_stream.md`):
```markdown
*10:34:02* Subject exhibits High Frustration (variance > 0.8)
*10:34:02* Cursor inside `retrieve_memory`
*10:34:03* Recent history: 3 failed attempts at vector search implementation
*10:34:03* Hypothesis: Subject lacks numpy reshape syntax context
```

**K-gent** (Action):
*Doesn't interrupt.* Updates Shadow Diff instead.

**IDE**: Faint icon appears in gutter next to line 142.

**Kent**: (Notices icon, hits `Alt+Space` to peek)

**Ghost File** (`.kgents/ghost/shadow.patch`):
```python
# K-gent speculation (confidence: 87%)
# Handles the dimensionality mismatch you're stuck on.

def retrieve_memory(self, vector):
    return self.index.query(vector.reshape(1, -1))
```

**Kent**: (Hits `Tab` to accept)

**Time elapsed**: 0 seconds of explicit prompting.
**Loop size**: Infinitesimal.
**Experience**: Telepathic.

---

## Success Criteria (Revised)

### Quantitative
- **Shadow acceptance rate**: >60% of shadow diffs accepted without modification
- **Flinch-to-resolution**: Anomalies surfaced by flinch lead to fix within 2 sessions
- **Prefetch hit rate**: >80% of Claude queries have context pre-loaded
- **Flow preservation**: <1 interruption per hour during detected flow state

### Qualitative
- **Peripheral awareness**: Ghost files provide useful context without demanding attention
- **Anticipatory assistance**: System helps *before* you ask
- **Affect-aware**: System behavior matches developer emotional state
- **Value-aligned**: Morning calibration keeps system tuned to current priorities

### Anti-Metrics
- Shadow suggestions that are consistently wrong
- Flinch fatigue (button becomes meaningless)
- Over-interruption during flow
- Calibration dilemmas that feel artificial

---

## Principles Alignment (Extended)

| Principle | V4 Expression |
|-----------|---------------|
| **Tasteful** | Shadow appears silently; doesn't demand attention |
| **Curated** | Only high-confidence speculations become patches |
| **Ethical** | Flinch respects developer's inarticulate discomfort |
| **Joy-Inducing** | Telepathic assistance feels like magic |
| **Composable** | LSP + MCP + Ghost = layered perception |
| **Heterarchical** | Developer always has final say (Tab to accept) |
| **Generative** | System learns from accepted/rejected shadows |

**The Accursed Share**: 10% of morning calibration dilemmas are playful/philosophical, not just practical. Even in efficiency, there must be room for wondering.

---

## Files to Create

### Phase 1: Foundation
- [ ] `protocols/cli/handlers/status.py`
- [ ] `protocols/cli/handlers/dream.py`
- [ ] `protocols/cli/handlers/map.py`

### Phase 2: Sensorium
- [ ] `protocols/cli/devex/ghost_writer.py`
- [ ] `.kgents/ghost/.gitignore`

### Phase 3: Neural Link
- [ ] `protocols/cli/devex/lsp_prefetch.py`
- [ ] `agents/o/proprioception.py`

### Phase 4: Shadow
- [ ] `agents/j/shadow_executor.py`
- [ ] `protocols/cli/devex/flinch.py`

### Phase 5: Rituals
- [ ] `protocols/cli/devex/rituals.py` (extended with calibration/confessional)
- [ ] `agents/k/calibration_dilemmas.py`

### Phase 6: MCP
- [ ] `protocols/cli/mcp/devex_resources.py` (extended)
- [ ] `protocols/cli/mcp/devex_prompts.py` (extended with algedonic)

---

*"The system that perceives itself, improves itself. The system that perceives its host, becomes part of the host."*
