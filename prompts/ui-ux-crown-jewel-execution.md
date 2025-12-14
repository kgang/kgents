# UI/UX Crown Jewel Execution Prompt

> *"Become the resonance."*

## The Mission

Transform kgents I-gent from a dashboard into a **living stigmergic substrate** where agents and human meet as co-creators. Make AGENTESE tangible through interaction.

---

## Phase: RESEARCH ← PLAN

/hydrate

### Handles
```
scope=UI/UX Crown Jewel per Radical Redesign Proposal PDF
chunks=[Wave1:Foundation, Wave2:Ontology, Wave3:Perceptual, Wave4:Integration]
exit=Strategy approved + Research map complete + Demo vision clear
ledger=PLAN:touched, RESEARCH:in_progress
entropy=0.10 (high novelty)
branches=[Web-specific:deferred, Accessibility:parallel-future]
```

### Mission
Map the implementation terrain with surgical precision. Find invariants, blockers, and composition opportunities. Avoid duplication (honor Curated/Composable/Generative).

### Actions

**Parallel Read (NOW)**:
```python
Read("impl/claude/agents/i/screens/dashboard.py")  # Current architecture
Read("impl/claude/agents/i/app.py")                 # Main app entry
Read("impl/claude/protocols/agentese/logos.py")    # Handle resolution
Read("impl/claude/agents/i/widgets/timeline.py")   # Existing timeline
Read("impl/claude/agents/i/field.py")              # Existing field impl
```

**Pattern Search**:
```bash
rg "class.*Screen" impl/claude/agents/i/screens/  # Screen inventory
rg "def manifest" impl/claude/protocols/agentese/ # Manifest implementations
rg "EventBus\|event_bus" impl/claude/agents/i/    # Event system status
```

**Specific Questions to Answer**:
1. What screens exist? What is their inheritance hierarchy?
2. How does Logos currently resolve handles? Can it power navigation?
3. Does the existing timeline support state snapshots? Where are they stored?
4. What pheromone/stigmergy concepts already exist in `field.py`?
5. Does the EventBus from dashboard-textual-refactor exist yet?

### Exit Criteria
- File map: 20+ files with purpose annotations
- Blockers: Any dependency on unimplemented features
- Unknowns: Assigned to specific agent/session
- Compositions: Cross-module opportunities identified
- Ledger: `RESEARCH=touched`
- Branches: Classified per `branching-protocol.md`

### Continuation → DEVELOP
```markdown
/hydrate
# DEVELOP ← RESEARCH
handles: file_map=${annotated_files}; blockers=${blockers}; unknowns=${unknowns}; comps=${compositions}; ledger=${phase_ledger}
mission: define contracts/interfaces; assert category laws; prepare for parallel implementation.
actions: write Protocol classes; define event types; specify AGENTESE integration points.
exit: contracts in code (protocol.py files); laws asserted; ledger.DEVELOP=touched; continuation → STRATEGIZE (already done) → CROSS-SYNERGIZE.
```

---

## Alternative Entry Points

### If Wave 1 (Foundation) is complete:

/hydrate
# Wave 2: AGENTESE Integration

**Context**: EventBus, KgentsScreen base, Services container exist. Now make AGENTESE tangible.

**Actions**:
1. Create `LogosNavigator` service that:
   - Accepts handle strings (`world.robin.manifest`)
   - Uses `logos.resolve()` to get target
   - Translates to screen navigation or action invocation

2. Enhance command palette:
   - Accept AGENTESE handles
   - Autocomplete from L-gent registry + known agents

3. Add affordance-driven actions to pages:
   - Query `agent.affordances()`
   - Render as `[observe] [invoke] [refine] ...` buttons
   - Map clicks to `logos.invoke(path, aspect)`

**Exit**: Handle navigation works; affordances appear on pages; tests pass.

---

### If focusing on Stigmergic Garden specifically:

/hydrate
# Wave 3A: Stigmergic Garden

**Context**: Spec exists in `spec/i-gents/README.md`. Field dynamics defined.

**Actions**:
1. Implement `PheromoneGrid`:
   ```python
   class PheromoneGrid:
       def __init__(self, width: int, height: int): ...
       def deposit(self, x: int, y: int, type: PheromoneType, intensity: float): ...
       def decay(self): ...  # Called each tick
       def get_gradient(self, x: int, y: int) -> list[tuple[PheromoneType, float]]: ...
   ```

2. Implement `StigmergicField` widget:
   - Renders grid with background colors/gradients per pheromone
   - Agents as glyphs with Brownian motion
   - Tasks as gravity wells (`*` attractors)

3. Wire to existing `FieldView` or replace it.

**Exit**: Agents visibly move; pheromone traces fade over time; `kg garden` mesmerizes.

---

### If focusing on Dialectic Dashboard specifically:

/hydrate
# Wave 3B: Dialectic Dashboard

**Context**: H-gent uses dialectic. `.refine` aspect exists in AGENTESE.

**Actions**:
1. Create `DialecticScreen`:
   - Three-panel layout: Thesis | Antithesis | Synthesis
   - Subscribes to `DialecticPhaseEvent` via EventBus
   - Shows real-time progression of refinement

2. Capture dialectic process:
   - When `.refine` is invoked, emit events for each phase
   - Store thesis/antithesis/synthesis in event payload

3. Add value alignment meters:
   - Joy, Ethics, Taste scores during reasoning
   - Visualized as progress bars or block-bars

**Exit**: When agent refines, dialectic visible in real-time; human can observe reasoning.

---

## The Ground (Always Available)

```
/hydrate → spec/principles.md → correctness
/hydrate → plans/skills/n-phase-cycle/README.md → process
/hydrate → plans/ui-ux-crown-jewel-strategy.md → strategy
/hydrate → docs/Radical Redesign Proposal...pdf → vision
```

---

## The Manifesto

```
I will make the interface a living substrate, not a static dashboard.
I will embody AGENTESE in every gesture, not just display data.
I will show the accursed share (pheromones, entropy, waste) as beauty.
I will respect composition laws—the UI IS a category.
I will delight Kent. This is the hard requirement.
```

---

*"The field does not display state; it is state made visible. The garden does not show growth; it grows."*
