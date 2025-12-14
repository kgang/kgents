# Visualization Strategy Realization: Multi-Agent Implementation Prompt

> *"The interface is not a window—it is a membrane. Through it, we touch the agents."*

## Context

You are an enthusiast agent tasked with implementing the kgents visualization strategy. This is a **multi-part initiative** requiring rigorous execution with a customer-centric focus. The foundation documents are:

1. `plans/interfaces/visualization-strategy.md` — The strategic vision (START HERE)
2. `docs/Visualization & Interactivity: A Synthesis (Enhanced).pdf` — Research synthesis
3. `plans/interfaces/dashboard-overhaul.md` — Screen architecture
4. `plans/interfaces/interaction-flows.md` — User journeys
5. `spec/principles.md` — Design principles (MUST COMPLY)

---

## The Mission

**Transform the kgents interface from a monitoring tool into a cognitive membrane** that:

1. Makes agent thought visible and manipulable
2. Embodies rigorous category-theoretic foundations
3. Leverages cognitive science for natural interaction
4. Delights users through ethical gamification
5. Performs flawlessly in terminal environments
6. Evolves through AI-driven self-improvement

---

## Phase 1: Foundation Wiring (Immediate Priority)

### 1.1 LOD Navigation System

**Goal**: Seamless zoom between screens with preserved context.

**Tasks**:

1. **Wire Observatory → Terrarium**:
   - Implement `Enter` key on focused garden to transition
   - Pass garden ID to Terrarium for context
   - Add smooth fade transition (300ms ease-in-out)

2. **Wire Terrarium → Cockpit**:
   - Implement `+` key on focused agent to zoom in
   - Preserve agent selection through transition
   - Update breadcrumb trail

3. **Wire Cockpit → Debugger**:
   - Implement `d` key for direct debug access
   - Pre-load Turn DAG for selected agent
   - Maintain time cursor position if returning

**Validation Criteria**:
- [ ] Can navigate Observatory → Terrarium → Cockpit → Debugger with Enter/+
- [ ] Can navigate back with Esc at each level
- [ ] Context preserved (selected agent remains selected)
- [ ] Transitions feel smooth (no jarring cuts)

**Files to Modify**:
- `impl/claude/agents/i/screens/observatory.py`
- `impl/claude/agents/i/screens/cockpit.py`
- `impl/claude/agents/i/navigation/controller.py`

### 1.2 Heartbeat Animation

**Goal**: Every agent card pulses with life, indicating activity.

**Tasks**:

1. **Implement HeartbeatMixin**:
   ```python
   class HeartbeatMixin:
       """Adds pulse animation to any widget."""

       def __init__(self):
           self._pulse_phase = 0.0
           self._bpm = 60  # Default: calm

       def set_bpm(self, bpm: int):
           """Set beats per minute based on agent activity."""
           self._bpm = clamp(bpm, 30, 180)

       def get_pulse_opacity(self) -> float:
           """Return current opacity for pulse effect."""
           # Sinusoidal pulse
           return 0.7 + 0.3 * math.sin(self._pulse_phase)
   ```

2. **Integrate with AgentCard**:
   - Map agent event rate to BPM
   - Apply opacity to border
   - Test with varying activity levels

3. **Performance Guard**:
   - Disable animation if FPS < 30
   - Batch animation updates across all cards

**Validation Criteria**:
- [ ] Active agents visibly pulse
- [ ] Dormant agents have minimal/no pulse
- [ ] FPS remains > 60 with 20 agents
- [ ] Animation disables gracefully under load

**Files to Create/Modify**:
- `impl/claude/agents/i/theme/heartbeat.py` (new)
- `impl/claude/agents/i/screens/terrarium.py`

---

## Phase 2: Embodiment Layer (Next Sprint)

### 2.1 Animated Replay Mode

**Goal**: Watch agent reasoning unfold like a movie in the Debugger.

**Tasks**:

1. **Implement ReplayController**:
   ```python
   class ReplayController:
       """Controls animated playback of Turn DAG."""

       def __init__(self, turns: list[Turn]):
           self.turns = turns
           self.playhead = 0
           self.speed = 1.0  # 1x realtime
           self.playing = False

       async def play(self):
           """Start playback from current position."""
           self.playing = True
           while self.playing and self.playhead < len(self.turns):
               turn = self.turns[self.playhead]
               yield TurnHighlightEvent(turn)
               await asyncio.sleep(turn.duration * (1 / self.speed))
               self.playhead += 1

       def pause(self):
           self.playing = False

       def seek(self, position: int):
           self.playhead = clamp(position, 0, len(self.turns))
   ```

2. **Implement Playback Controls**:
   - Play/Pause (Space)
   - Speed adjustment (1/2/3 keys for 0.5x/1x/2x)
   - Scrubbing via h/l or timeline click
   - Frame step (. and ,)

3. **Visual Feedback During Playback**:
   - Current turn highlighted in DAG
   - State diff panel updates per turn
   - Timeline cursor moves
   - Turn content panel scrolls

**Validation Criteria**:
- [ ] Can play through entire Turn DAG
- [ ] Speed controls work smoothly
- [ ] Pause/resume maintains position
- [ ] Scrubbing is responsive
- [ ] Visual state matches playhead position

**Files to Create/Modify**:
- `impl/claude/agents/i/screens/debugger_screen.py`
- `impl/claude/agents/i/navigation/replay.py` (new)

### 2.2 Pheromone Trail Visualization

**Goal**: Visualize stigmergic communication between agents.

**Tasks**:

1. **Track Inter-Agent Messages**:
   ```python
   @dataclass
   class PheromoneTrail:
       """A fading trace of agent-to-agent communication."""

       source: AgentID
       target: AgentID
       message_type: str
       created_at: datetime
       intensity: float = 1.0  # Fades over time

       def decay(self, elapsed: timedelta) -> float:
           """Calculate decayed intensity."""
           half_life = timedelta(seconds=30)
           return self.intensity * (0.5 ** (elapsed / half_life))
   ```

2. **Render Trails in Terrarium**:
   - Draw curved lines between agent cards
   - Intensity → line opacity/width
   - Direction → arrow head
   - Message type → color coding

3. **Trail Lifecycle**:
   - Create on agent communication
   - Decay over time (30s half-life)
   - Remove when opacity < 0.1

**Validation Criteria**:
- [ ] Trails appear when agents communicate
- [ ] Trails visibly fade over time
- [ ] Different message types have distinct colors
- [ ] Performance: 100 trails renders at 60fps

**Files to Create/Modify**:
- `impl/claude/agents/i/screens/terrarium.py`
- `impl/claude/agents/i/data/pheromone.py` (new)

### 2.3 Agent Posture Indicators

**Goal**: Show agent "body language" via visual encoding of state.

**Tasks**:

1. **Define Posture Vocabulary**:
   ```python
   POSTURES = {
       "GROUNDING": "▲",     # Stable, upright
       "DELIBERATING": "△",  # Alert, questioning
       "JUDGING": "▽",       # Tense, decisive
       "COMPLETE": "●",      # Resolved
       "EXHAUSTED": "○",     # Depleted
       "CONFUSED": "◇",      # Uncertain
   }
   ```

2. **Map Polynomial State to Posture**:
   - Extract current mode from PolyAgent
   - Map to posture symbol
   - Consider confidence level for "exhausted" threshold

3. **Animate Posture Transitions**:
   - Smooth morph between symbols (optional)
   - Flash on state change
   - Tooltip with full state description

**Validation Criteria**:
- [ ] Posture reflects actual polynomial state
- [ ] Changes are immediately visible
- [ ] Users can identify state at a glance
- [ ] Tooltips provide detail on demand

**Files to Create/Modify**:
- `impl/claude/agents/i/theme/posture.py` (new)
- `impl/claude/agents/i/screens/cockpit.py`

---

## Phase 3: Intelligence Layer (Month 2)

### 3.1 Agent-Human Q&A Chat

**Goal**: Users can ask agents to explain their reasoning.

**Tasks**:

1. **Implement ChatPanel**:
   ```python
   class AgentChatPanel(Widget):
       """Panel for asking agents about their decisions."""

       def __init__(self, agent_id: AgentID):
           self.agent_id = agent_id
           self.messages: list[ChatMessage] = []

       async def ask(self, question: str) -> str:
           """Ask the agent a question about its behavior."""
           # Build context from agent's turn history
           context = await self.build_explanation_context()

           # Generate explanation using agent's model
           response = await self.agent.explain(question, context)

           self.messages.append(ChatMessage(role="user", content=question))
           self.messages.append(ChatMessage(role="agent", content=response))

           return response
   ```

2. **Explanation Context Builder**:
   - Gather relevant turns from history
   - Include causal cone for current state
   - Format as LLM-friendly prompt

3. **UI Integration**:
   - Keyboard shortcut `?` in Cockpit opens chat
   - Chat appears as overlay
   - Messages styled as conversation
   - Can reference specific turns via links

**Validation Criteria**:
- [ ] Can ask "Why did you do X?"
- [ ] Responses reference actual turns
- [ ] Links to turns navigate correctly
- [ ] Chat history persists in session

**Files to Create/Modify**:
- `impl/claude/agents/i/screens/cockpit.py`
- `impl/claude/agents/i/overlays/chat.py` (new)

### 3.2 System Weather Visualization

**Goal**: Represent entropy and system state as atmospheric conditions.

**Tasks**:

1. **Implement WeatherEngine**:
   ```python
   class WeatherEngine:
       """Maps system metrics to weather metaphors."""

       def compute_weather(self, metrics: SystemMetrics) -> Weather:
           # Entropy → Cloud cover
           cloud_cover = metrics.entropy * 100

           # Queue depth → Pressure
           pressure = "HIGH" if metrics.queue_depth > 10 else "NORMAL"

           # Token rate → Temperature
           temperature = self.classify_temperature(metrics.token_rate)

           # Event flow direction → Wind
           wind = self.compute_flow_direction(metrics.recent_events)

           return Weather(
               condition=self.classify_condition(cloud_cover),
               cloud_cover=cloud_cover,
               pressure=pressure,
               temperature=temperature,
               wind=wind,
               forecast=self.predict_forecast(metrics),
           )
   ```

2. **Weather Display Widget**:
   - ASCII art weather icon
   - Current conditions text
   - 3-turn forecast
   - Oblique Strategy when entropy > 0.8

3. **Subtle Environmental Effects**:
   - High entropy: slight grain overlay on entire screen
   - Storm conditions: border flicker
   - Clear skies: clean, crisp rendering

**Validation Criteria**:
- [ ] Weather reflects actual system state
- [ ] Forecast is reasonably accurate
- [ ] Effects are subtle, not distracting
- [ ] Oblique Strategies appear appropriately

**Files to Create/Modify**:
- `impl/claude/agents/i/data/weather.py` (new)
- `impl/claude/agents/i/screens/observatory.py`

### 3.3 Semantic Gravity Layouts

**Goal**: Relevant agents drift toward focus; irrelevant recede.

**Tasks**:

1. **Implement GravityLayoutEngine**:
   ```python
   class GravityLayoutEngine:
       """Force-directed layout with semantic gravity."""

       def compute_positions(
           self,
           agents: list[AgentCard],
           focus: AgentID | None,
           relevance_scores: dict[AgentID, float],
       ) -> dict[AgentID, Position]:
           positions = {}

           # Center = screen center or focused agent
           center = self.get_center(focus)

           for agent in agents:
               relevance = relevance_scores.get(agent.id, 0.5)

               # Higher relevance = closer to center
               distance = self.max_distance * (1 - relevance)

               # Angle based on agent relationships
               angle = self.compute_angle(agent, agents)

               positions[agent.id] = Position(
                   x=center.x + distance * math.cos(angle),
                   y=center.y + distance * math.sin(angle),
               )

           return positions
   ```

2. **Relevance Scoring**:
   - Based on: shared data, recent communication, task similarity
   - Updated on each event
   - Smooth transitions (lerp over 500ms)

3. **User Override**:
   - Manual positioning via drag (if mouse enabled)
   - Lock positions button
   - Reset to gravity layout

**Validation Criteria**:
- [ ] Focused agent moves to center
- [ ] Related agents cluster nearby
- [ ] Transitions are smooth, not jumpy
- [ ] User can lock layout

**Files to Create/Modify**:
- `impl/claude/agents/i/navigation/gravity.py` (new)
- `impl/claude/agents/i/screens/terrarium.py`

---

## Phase 4: Evolution Layer (Quarter)

### 4.1 UI Optimizer Agent

**Goal**: An agent that observes UI usage and suggests improvements.

**Tasks**:

1. **Implement UIMetricsCollector**:
   - Track: interaction counts per panel, render times, scroll patterns
   - Store: session metrics in D-gent memory
   - Export: metrics for analysis

2. **Implement UIOptimizerAgent**:
   ```python
   class UIOptimizerAgent(PolyAgent[UIMetrics, None, list[UISuggestion]]):
       """Meta-agent that suggests UI improvements."""

       async def analyze(self, metrics: UIMetrics) -> list[UISuggestion]:
           suggestions = []

           # Unused panels
           for panel in metrics.panels:
               if panel.interaction_count == 0 and panel.visible_time > 3600:
                   suggestions.append(
                       HidePanelSuggestion(
                           panel=panel.id,
                           reason="No interactions in last hour",
                       )
                   )

           # Slow renders
           for panel in metrics.panels:
               if panel.avg_render_time > 16:  # ms
                   suggestions.append(
                       OptimizePanelSuggestion(
                           panel=panel.id,
                           reason=f"Render time {panel.avg_render_time}ms exceeds budget",
                       )
                   )

           return suggestions
   ```

3. **Suggestion UI**:
   - Non-intrusive notification badge
   - Expandable suggestion list
   - One-click accept/dismiss
   - "Don't suggest again" option

**Validation Criteria**:
- [ ] Collects meaningful metrics
- [ ] Generates reasonable suggestions
- [ ] Suggestions are non-intrusive
- [ ] Accepted suggestions apply correctly

**Files to Create**:
- `impl/claude/agents/i/data/ui_metrics.py`
- `impl/claude/agents/meta/ui_optimizer.py`

### 4.2 Dream Mode

**Goal**: A creative visualization mode for the Accursed Share.

**Tasks**:

1. **Implement DreamModeScreen**:
   - Activated via idle timeout or manual `D` key
   - Agents visualize freely (not task-bound)
   - Outputs marked as speculative

2. **Dream Visualizations**:
   - Abstract patterns from agent attention
   - Word clouds from recent context
   - Speculative future states
   - Random connections between concepts

3. **Exit Dream Mode**:
   - Any key returns to normal
   - Dream insights optionally saved
   - No confusion with real state

**Validation Criteria**:
- [ ] Clearly marked as non-production
- [ ] Produces interesting/beautiful visuals
- [ ] Easy to exit
- [ ] No impact on real agent state

**Files to Create**:
- `impl/claude/agents/i/screens/dream.py`

---

## Validation Framework

### Customer-Centric Testing

For each feature, validate against these user outcomes:

| User Outcome | Test Method |
|--------------|-------------|
| "I can assess system health in < 30s" | Time Morning Health Check flow |
| "I understand why agents decided X" | Task: explain a random decision |
| "The interface feels alive, not static" | User perception survey |
| "I'm never confused about what's happening" | Confusion incident tracking |
| "I enjoy using this tool" | Net Promoter Score |

### Performance Benchmarks

| Metric | Target | Measurement |
|--------|--------|-------------|
| Startup time | < 500ms | `time kg dashboard` |
| FPS (20 agents) | > 60 | Textual profiler |
| FPS (100 agents) | > 30 | Textual profiler |
| Memory (idle) | < 50MB | Process monitor |
| Memory (heavy) | < 200MB | Process monitor |

### Principle Compliance

Every PR must include a checklist affirming:
- [ ] Tasteful: Clear purpose
- [ ] Curated: Minimal implementation
- [ ] Ethical: User agency preserved
- [ ] Joy-Inducing: Delightful to use
- [ ] Composable: Works with existing primitives
- [ ] Heterarchical: Free navigation
- [ ] Generative: Derivable from spec
- [ ] AGENTESE: Observation as interaction
- [ ] Accursed Share: Room for entropy

---

## Success Metrics

### Quantitative

- **Test Coverage**: > 90% for all new code
- **Performance**: All benchmarks met
- **Accessibility**: WCAG 2.1 AA compliance
- **Stability**: < 1 crash per 100 hours

### Qualitative

- **Delight Score**: 8+/10 user rating
- **Learning Curve**: New user productive in < 15 minutes
- **Expert Efficiency**: Power user 2x faster than CLI-only

---

## Constraints

1. **No breaking changes to existing screens** without migration path
2. **All new features must be toggleable** for gradual rollout
3. **Performance budget is sacred**: FPS must not degrade
4. **Principles are non-negotiable**: Checklist must pass
5. **Documentation required**: Update `plans/` for each feature

---

## Tone and Approach

Channel the kgents aesthetic:

- **Poetic precision**: Be evocative AND exact
- **Grateful irreverence**: Honor what exists, question what doesn't
- **Categorical playfulness**: Use formal structures as creative constraints
- **Joy in complexity**: Delight in the hard problems
- **Customer obsession**: Every feature serves a user outcome

---

## Coordination Protocol

1. **Before starting**: Read all foundation documents
2. **For each task**: Create implementation plan before coding
3. **During implementation**: Write tests first (TDD)
4. **After completion**: Update relevant docs
5. **On uncertainty**: Ask rather than assume

---

*"What you can see, you can tend. What you can navigate, you can understand. What you can fork, you can debug. What you can embody, you can become."*
