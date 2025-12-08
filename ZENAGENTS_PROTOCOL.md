# zen-agents Integration Protocol

**A protocol for completing zen-agents TUI using kgents agents via ClaudeCLIRuntime.**

This document guides the integration of kgents' LLM-backed agents into the zen-agents Textual TUI, transforming it from a tmux session manager into an intelligent agent orchestration interface.

---

## Ground: What Exists

### zen-agents (impl/zen-agents/)

```
impl/zen-agents/
├── zen_agents/
│   ├── app.py                    # Textual App (ZenAgentsApp)
│   ├── models/session.py         # Session, SessionState, SessionType
│   ├── agents/
│   │   ├── config.py             # ConfigGround, ConfigSublate
│   │   ├── conflict.py           # SessionContradict, ConflictSublate
│   │   ├── detection.py          # StateDetector (Fix pattern)
│   │   ├── judge.py              # SessionJudge, ConfigJudge
│   │   └── pipelines/
│   │       ├── create.py         # Session creation (MANUAL orchestration)
│   │       ├── revive.py         # Session revival
│   │       └── clean.py          # Session cleanup
│   ├── services/
│   │   ├── tmux.py               # TmuxService (async tmux wrapper)
│   │   ├── session_manager.py    # SessionManager (lifecycle + events)
│   │   └── state_refresher.py    # StateRefresher (Fix-based polling)
│   ├── screens/main.py           # MainScreen, SessionDetail, CreateModal
│   └── widgets/session_list.py   # SessionList, SessionItem
```

**Status**: ~70% complete, ~3500 LOC

**What Works**:
- Textual TUI with session list, detail panel, status bar
- Session lifecycle: create, kill, revive, attach
- Bootstrap patterns: Ground, Judge, Contradict, Sublate, Fix
- Event-driven architecture

**What's Missing**:
- No LLM integration (session types mention Claude/Gemini but don't connect)
- Pipelines are manually orchestrated (not using `>>` composition)
- No persistence (sessions lost on restart)
- No log viewer (tmux pane capture exists but not displayed)
- No tests
- Confidence bug in StateDetector (always 0.2)

### kgents (impl/claude-openrouter/)

```
impl/claude-openrouter/
├── bootstrap/                    # 7 irreducible agents
│   ├── types.py                  # Agent[A, B] base
│   ├── id.py, compose.py         # Identity, Composition
│   ├── judge.py, ground.py       # Judgment, Grounding
│   ├── contradict.py, sublate.py # Dialectic
│   └── fix.py                    # Fixed-point iteration
├── runtime/
│   ├── base.py                   # LLMAgent, Runtime, AgentContext
│   ├── cli.py                    # ClaudeCLIRuntime (OAuth, no API key)
│   ├── claude.py                 # ClaudeRuntime (API key)
│   └── openrouter.py             # OpenRouterRuntime (multi-model)
└── agents/
    ├── a/                        # Abstract + Creativity
    │   ├── skeleton.py           # AbstractAgent alias, AgentMeta
    │   └── creativity.py         # CreativityCoach (LLMAgent)
    ├── b/                        # Scientific discovery
    │   ├── hypothesis.py         # HypothesisEngine (Popperian)
    │   └── robin.py              # Robin (K-gent + Hypothesis + Hegel)
    ├── c/                        # Category theory
    │   ├── functor.py            # Maybe, Either
    │   ├── parallel.py           # parallel, fan_out, race
    │   └── conditional.py        # branch, switch, guarded
    ├── h/                        # Dialectic introspection
    │   ├── hegel.py              # HegelAgent (synthesis)
    │   ├── jung.py               # JungAgent (shadow)
    │   └── lacan.py              # LacanAgent (registers)
    └── k/                        # Personalization
        ├── persona.py            # KgentAgent, PersonaQuery
        └── evolution.py          # EvolutionAgent
```

**Status**: Complete implementation, ready for integration

---

## The Protocol

### Principle: Composition Over Concatenation

zen-agents already demonstrates bootstrap patterns. The goal is NOT to rewrite, but to:
1. **Wire** kgents agents via ClaudeCLIRuntime
2. **Compose** pipelines using `>>` instead of manual orchestration
3. **Extend** UI to surface LLM capabilities
4. **Test** the integrated system

---

## Phase 1: Foundation

### 1.1 Import Bridge

**Goal**: Enable zen-agents to import from kgents.

**File**: `impl/zen-agents/zen_agents/kgents_bridge.py`

**Claude Code Action**:
```
1. Create zen_agents/kgents_bridge.py
2. Add sys.path manipulation to reach impl/claude-openrouter
3. Re-export key components for clean imports
```

**Implementation**:
```python
"""Bridge to kgents implementation."""

import sys
from pathlib import Path

# Add kgents to path
KGENTS_ROOT = Path(__file__).parent.parent.parent / "claude-openrouter"
if str(KGENTS_ROOT) not in sys.path:
    sys.path.insert(0, str(KGENTS_ROOT))

# Re-export runtime
from runtime import ClaudeCLIRuntime, ClaudeRuntime, OpenRouterRuntime, LLMAgent

# Re-export bootstrap
from bootstrap import Agent, Id, compose, Judge, Ground, Contradict, Sublate, Fix, fix

# Re-export agents
from agents.a import CreativityCoach, CreativityInput, CreativityMode, creativity_coach
from agents.b import (
    HypothesisEngine, HypothesisInput, HypothesisOutput,
    Hypothesis, hypothesis_engine, rigorous_engine,
    RobinAgent, RobinInput, RobinOutput, robin
)
from agents.h import HegelAgent, hegel, DialecticInput, JungAgent, jung
from agents.k import (
    KgentAgent, kgent, DialogueMode, DialogueInput,
    PersonaQuery, query_persona
)
from agents.c import Maybe, Either, parallel, branch, switch
```

**Kent Checkpoint**: Is path manipulation acceptable, or should this be a proper package dependency?

---

### 1.2 AgentOrchestrator Service

**Goal**: Central service for executing kgents agents within zen-agents.

**File**: `impl/zen-agents/zen_agents/services/agent_orchestrator.py`

**Claude Code Action**:
```
1. Create services/agent_orchestrator.py
2. Initialize ClaudeCLIRuntime lazily
3. Provide methods for each agent interaction pattern
4. Handle async execution within Textual's event loop
```

**Implementation**:
```python
"""Orchestrates kgents agents for zen-agents TUI."""

from typing import Optional
from dataclasses import dataclass

from ..kgents_bridge import (
    ClaudeCLIRuntime,
    CreativityCoach, CreativityInput, CreativityMode, creativity_coach,
    HypothesisEngine, HypothesisInput, hypothesis_engine,
    RobinAgent, RobinInput, robin,
    HegelAgent, hegel, DialecticInput,
    KgentAgent, kgent, DialogueMode, DialogueInput,
    PersonaQuery, query_persona
)


@dataclass
class AnalysisResult:
    """Result of log analysis."""
    hypotheses: list[str]
    suggested_tests: list[str]
    reasoning: str


@dataclass
class ExpansionResult:
    """Result of idea expansion."""
    ideas: list[str]
    follow_ups: list[str]


@dataclass
class DialogueResult:
    """Result of dialogue."""
    response: str
    mode: DialogueMode


class AgentOrchestrator:
    """
    Central orchestrator for LLM-backed agents.

    Uses ClaudeCLIRuntime (OAuth via Claude CLI) by default.
    """

    def __init__(self, runtime: Optional[ClaudeCLIRuntime] = None):
        self._runtime = runtime
        self._initialized = False

    @property
    def runtime(self) -> ClaudeCLIRuntime:
        """Lazy initialization of runtime."""
        if self._runtime is None:
            self._runtime = ClaudeCLIRuntime()
        return self._runtime

    async def check_available(self) -> bool:
        """Check if Claude CLI is available for LLM calls."""
        try:
            # Quick check - will fail fast if CLI unavailable
            import subprocess
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    # --- Analysis (HypothesisEngine) ---

    async def analyze_log(
        self,
        log_content: str,
        domain: str = "software engineering",
        question: Optional[str] = None
    ) -> AnalysisResult:
        """
        Analyze session log using HypothesisEngine.

        Args:
            log_content: Raw log/output text
            domain: Domain context (e.g., "networking", "database")
            question: Specific question to answer

        Returns:
            AnalysisResult with hypotheses and suggested tests
        """
        engine = hypothesis_engine()
        result = await self.runtime.execute(
            engine,
            HypothesisInput(
                observations=[log_content],
                domain=domain,
                question=question or "What is happening in this output?"
            )
        )
        return AnalysisResult(
            hypotheses=[h.statement for h in result.output.hypotheses],
            suggested_tests=result.output.suggested_tests,
            reasoning="\n".join(result.output.reasoning_chain)
        )

    # --- Creativity (CreativityCoach) ---

    async def expand_idea(
        self,
        seed: str,
        mode: CreativityMode = CreativityMode.EXPAND,
        context: Optional[str] = None
    ) -> ExpansionResult:
        """
        Expand an idea using CreativityCoach.

        Args:
            seed: The seed idea to expand
            mode: EXPAND, CONNECT, CONSTRAIN, or QUESTION
            context: Optional context

        Returns:
            ExpansionResult with ideas and follow-ups
        """
        coach = creativity_coach()
        result = await self.runtime.execute(
            coach,
            CreativityInput(seed=seed, mode=mode, context=context)
        )
        return ExpansionResult(
            ideas=result.output.responses,
            follow_ups=result.output.follow_ups
        )

    # --- Scientific Dialogue (Robin) ---

    async def scientific_dialogue(
        self,
        query: str,
        domain: str,
        observations: Optional[list[str]] = None,
        mode: DialogueMode = DialogueMode.EXPLORE
    ) -> dict:
        """
        Scientific dialogue using Robin.

        Robin = K-gent + HypothesisEngine + Hegel

        Args:
            query: The scientific question
            domain: Domain (e.g., "neuroscience", "biochemistry")
            observations: Optional observations to base hypotheses on
            mode: Dialogue mode (EXPLORE, CHALLENGE, etc.)

        Returns:
            Dict with synthesis, hypotheses, next_questions
        """
        robin_agent = robin(runtime=self.runtime)
        result = await robin_agent.invoke(RobinInput(
            query=query,
            domain=domain,
            observations=observations or [],
            dialogue_mode=mode,
            apply_dialectic=True
        ))
        return {
            "synthesis": result.synthesis_narrative,
            "hypotheses": [h.statement for h in result.hypotheses],
            "dialectic": result.dialectic,
            "next_questions": result.next_questions,
            "personalization": result.personalization
        }

    # --- Personalization (K-gent) ---

    async def kgent_dialogue(
        self,
        message: str,
        mode: DialogueMode = DialogueMode.REFLECT
    ) -> DialogueResult:
        """
        Dialogue with K-gent for personalized responses.

        Args:
            message: The message/query
            mode: REFLECT, ADVISE, CHALLENGE, or EXPLORE

        Returns:
            DialogueResult with response and mode
        """
        k = kgent()
        result = await self.runtime.execute(
            k,
            DialogueInput(message=message, mode=mode)
        )
        return DialogueResult(
            response=result.output.response,
            mode=mode
        )

    async def query_preferences(
        self,
        aspect: str = "all",
        topic: Optional[str] = None,
        for_agent: Optional[str] = None
    ) -> dict:
        """
        Query K-gent preferences.

        Args:
            aspect: "preference", "pattern", "value", or "all"
            topic: Specific topic to query
            for_agent: Agent this is for (influences style)

        Returns:
            Dict with preferences, patterns, suggested_style
        """
        query = query_persona()
        result = await self.runtime.execute(
            query,
            PersonaQuery(aspect=aspect, topic=topic, for_agent=for_agent)
        )
        return {
            "preferences": result.output.preferences,
            "patterns": result.output.patterns,
            "suggested_style": result.output.suggested_style
        }

    # --- Dialectic (Hegel) ---

    async def dialectic_analysis(
        self,
        thesis: str,
        antithesis: str
    ) -> dict:
        """
        Dialectic analysis using HegelAgent.

        Args:
            thesis: First position
            antithesis: Opposing position

        Returns:
            Dict with synthesis, notes, productive_tension
        """
        h = hegel()
        result = await self.runtime.execute(
            h,
            DialecticInput(thesis=thesis, antithesis=antithesis)
        )
        return {
            "synthesis": result.output.synthesis,
            "notes": result.output.sublation_notes,
            "productive_tension": result.output.productive_tension,
            "next_thesis": result.output.next_thesis
        }

    # --- Convenience: Suggest Session Name ---

    async def suggest_session_name(
        self,
        working_dir: str,
        session_type: str,
        context: Optional[str] = None
    ) -> str:
        """
        Use K-gent to suggest a session name.

        Args:
            working_dir: Working directory path
            session_type: Type of session
            context: Optional additional context

        Returns:
            Suggested session name (short, memorable)
        """
        message = f"Suggest a short (1-2 word) memorable session name for a {session_type} session in {working_dir}"
        if context:
            message += f". Context: {context}"

        result = await self.kgent_dialogue(message, DialogueMode.ADVISE)
        # Extract first word/phrase as name
        name = result.response.split()[0].lower().replace('"', '').replace("'", "")
        return name[:20]  # Cap at 20 chars
```

**Kent Checkpoint**: Is the API surface right? Should we expose raw agent access or only these high-level methods?

---

### 1.3 Fix Confidence Bug

**Goal**: Fix the StateDetector confidence calculation.

**File**: `impl/zen-agents/zen_agents/agents/detection.py`

**Claude Code Action**:
```
1. Read agents/detection.py
2. Find the confidence calculation (line ~92)
3. Fix to accumulate confidence across iterations
4. Ensure convergence works correctly
```

**Before**:
```python
return DetectionState(
    session_state=SessionState.RUNNING,
    confidence=min(1.0, 0.2),  # BUG: always 0.2
)
```

**After**:
```python
return DetectionState(
    session_state=SessionState.RUNNING,
    confidence=min(1.0, previous_confidence + 0.2),  # Accumulates
)
```

**Kent Checkpoint**: What should the confidence increment be? 0.2 means 5 iterations to full confidence.

---

### 1.4 Pipeline Composition

**Goal**: Replace manual pipeline orchestration with `>>` composition.

**File**: `impl/zen-agents/zen_agents/agents/pipelines/create.py`

**Claude Code Action**:
```
1. Read agents/pipelines/create.py
2. Identify the manual orchestration pattern
3. Refactor to use >> composition
4. Ensure type alignment between pipeline stages
```

**Before** (manual):
```python
async def execute_create_pipeline(config: NewSessionConfig, manager: SessionManager):
    # Manual orchestration
    validated = await ValidateLimit().invoke(config)
    if isinstance(validated, ValidationError):
        raise validated
    conflicts = await DetectConflicts().invoke(validated)
    resolved = await ResolveConflicts().invoke(conflicts)
    session = await SpawnTmux().invoke(resolved)
    return await DetectInitialState().invoke(session)
```

**After** (composed):
```python
from ...kgents_bridge import compose

# Define pipeline as composition
CreateSessionPipeline = (
    ValidateLimit()
    >> DetectConflicts()
    >> ResolveConflicts()
    >> SpawnTmux()
    >> DetectInitialState()
)

async def execute_create_pipeline(config: NewSessionConfig, manager: SessionManager):
    return await CreateSessionPipeline.invoke(config)
```

**Note**: May need adapter agents if types don't align. Use `Maybe` or `Either` from C-gents for error handling.

**Kent Checkpoint**: Does type-safe composition add value here, or is manual orchestration clearer for error handling?

---

## Phase 2: LLM Session Types

### 2.1 Extend SessionType Enum

**Goal**: Add LLM-backed session types.

**File**: `impl/zen-agents/zen_agents/models/session.py`

**Claude Code Action**:
```
1. Read models/session.py
2. Extend SessionType enum with new types
3. Add session_requires_llm() helper
```

**Implementation**:
```python
class SessionType(Enum):
    """Types of sessions zen-agents can manage."""

    # Existing
    SHELL = "shell"           # Plain bash shell
    CLAUDE = "claude"         # Claude CLI interactive

    # New LLM-backed types
    ROBIN = "robin"           # Scientific companion (Robin agent)
    CREATIVITY = "creativity" # Idea expansion (CreativityCoach)
    HYPOTHESIS = "hypothesis" # Hypothesis generation (HypothesisEngine)
    KGENT = "kgent"          # Personalized dialogue (K-gent)
    RESEARCH = "research"     # Research session (Robin + persistence)


def session_requires_llm(session_type: SessionType) -> bool:
    """Check if session type requires LLM runtime."""
    return session_type in {
        SessionType.ROBIN,
        SessionType.CREATIVITY,
        SessionType.HYPOTHESIS,
        SessionType.KGENT,
        SessionType.RESEARCH,
    }
```

**Kent Checkpoint**: Are these the right session types? Should CLAUDE use LLM or just spawn `claude` CLI?

---

### 2.2 Session Type Handler

**Goal**: Route session input to appropriate agents.

**File**: `impl/zen-agents/zen_agents/services/session_handler.py`

**Claude Code Action**:
```
1. Create services/session_handler.py
2. Implement handler for each LLM session type
3. Integrate with AgentOrchestrator
```

**Implementation**:
```python
"""Session type handlers - route to appropriate agents."""

from typing import Optional
from ..models.session import SessionType, Session
from .agent_orchestrator import AgentOrchestrator, AnalysisResult, ExpansionResult


class SessionTypeHandler:
    """Routes session interactions to appropriate agents."""

    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator
        self._handlers = {
            SessionType.ROBIN: self._handle_robin,
            SessionType.CREATIVITY: self._handle_creativity,
            SessionType.HYPOTHESIS: self._handle_hypothesis,
            SessionType.KGENT: self._handle_kgent,
            SessionType.RESEARCH: self._handle_research,
        }

    async def handle_input(
        self,
        session: Session,
        input_text: str,
        context: Optional[str] = None
    ) -> str:
        """
        Handle user input for a session.

        Args:
            session: The session receiving input
            input_text: User's input text
            context: Optional context (e.g., recent output)

        Returns:
            Formatted response string
        """
        handler = self._handlers.get(session.session_type)
        if handler is None:
            # Non-LLM session - return input unchanged for tmux
            return input_text
        return await handler(session, input_text, context)

    async def _handle_robin(
        self,
        session: Session,
        input_text: str,
        context: Optional[str]
    ) -> str:
        """Handle Robin (scientific companion) session."""
        result = await self.orchestrator.scientific_dialogue(
            query=input_text,
            domain=session.metadata.get("domain", "general"),
            observations=[context] if context else None
        )

        output = f"## Synthesis\n{result['synthesis']}\n\n"
        if result['hypotheses']:
            output += "## Hypotheses\n"
            for h in result['hypotheses']:
                output += f"• {h}\n"
        if result['next_questions']:
            output += "\n## Next Questions\n"
            for q in result['next_questions']:
                output += f"? {q}\n"
        return output

    async def _handle_creativity(
        self,
        session: Session,
        input_text: str,
        context: Optional[str]
    ) -> str:
        """Handle creativity session."""
        result = await self.orchestrator.expand_idea(
            seed=input_text,
            context=context
        )

        output = "## Expansions\n"
        for idea in result.ideas:
            output += f"• {idea}\n"
        if result.follow_ups:
            output += "\n## Follow-ups\n"
            for f in result.follow_ups:
                output += f"→ {f}\n"
        return output

    async def _handle_hypothesis(
        self,
        session: Session,
        input_text: str,
        context: Optional[str]
    ) -> str:
        """Handle hypothesis session."""
        result = await self.orchestrator.analyze_log(
            log_content=input_text,
            domain=session.metadata.get("domain", "software engineering"),
            question=context
        )

        output = "## Hypotheses\n"
        for h in result.hypotheses:
            output += f"• {h}\n"
        if result.suggested_tests:
            output += "\n## Suggested Tests\n"
            for t in result.suggested_tests:
                output += f"✓ {t}\n"
        return output

    async def _handle_kgent(
        self,
        session: Session,
        input_text: str,
        context: Optional[str]
    ) -> str:
        """Handle K-gent dialogue session."""
        from ..kgents_bridge import DialogueMode

        # Detect mode from input prefix
        mode = DialogueMode.REFLECT
        text = input_text
        if input_text.startswith("/challenge "):
            mode = DialogueMode.CHALLENGE
            text = input_text[11:]
        elif input_text.startswith("/advise "):
            mode = DialogueMode.ADVISE
            text = input_text[8:]
        elif input_text.startswith("/explore "):
            mode = DialogueMode.EXPLORE
            text = input_text[9:]

        result = await self.orchestrator.kgent_dialogue(text, mode)
        return f"[{result.mode.value}] {result.response}"

    async def _handle_research(
        self,
        session: Session,
        input_text: str,
        context: Optional[str]
    ) -> str:
        """Handle research session (Robin + accumulating observations)."""
        # Get accumulated observations from session metadata
        observations = session.metadata.get("observations", [])

        if input_text.startswith("/observe "):
            # Add observation
            obs = input_text[9:]
            observations.append(obs)
            session.metadata["observations"] = observations
            return f"Observation recorded ({len(observations)} total)"

        elif input_text.startswith("/hypothesize"):
            # Generate hypotheses from observations
            result = await self.orchestrator.scientific_dialogue(
                query=input_text[12:].strip() or "What patterns emerge?",
                domain=session.metadata.get("domain", "general"),
                observations=observations
            )
            return f"## Analysis of {len(observations)} observations\n\n{result['synthesis']}"

        else:
            # Default: Robin dialogue with observations
            return await self._handle_robin(session, input_text, "\n".join(observations[-5:]))
```

**Kent Checkpoint**: Is the command prefix pattern (/challenge, /observe) the right UX?

---

## Phase 3: UI Enhancements

### 3.1 Log Viewer Widget

**Goal**: Display session output with LLM analysis capability.

**File**: `impl/zen-agents/zen_agents/widgets/log_viewer.py`

**Claude Code Action**:
```
1. Create widgets/log_viewer.py
2. Implement RichLog-based viewer
3. Add analysis panel that shows LLM insights
4. Integrate with AgentOrchestrator
```

**Implementation**:
```python
"""Log viewer widget with LLM analysis."""

from textual.widgets import Static, RichLog, Button
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from rich.markdown import Markdown


class LogViewer(Vertical):
    """
    Session log viewer with analysis panel.

    Shows raw log on left, analysis on right.
    """

    DEFAULT_CSS = """
    LogViewer {
        height: 100%;
    }

    LogViewer #log-container {
        height: 70%;
        border: solid $primary;
    }

    LogViewer #analysis-container {
        height: 30%;
        border: solid $secondary;
    }

    LogViewer .analysis-header {
        dock: top;
        height: 3;
        background: $surface;
    }
    """

    log_content: reactive[str] = reactive("")
    analysis_content: reactive[str] = reactive("")

    def compose(self):
        with Vertical(id="log-container"):
            yield Static("Session Output", classes="log-header")
            yield RichLog(id="raw-log", wrap=True, highlight=True)

        with Vertical(id="analysis-container"):
            with Horizontal(classes="analysis-header"):
                yield Static("Analysis")
                yield Button("Analyze", id="analyze-btn", variant="primary")
            yield Static(id="analysis-panel")

    def watch_log_content(self, content: str):
        """Update log display when content changes."""
        log = self.query_one("#raw-log", RichLog)
        log.clear()
        log.write(content)

    def watch_analysis_content(self, content: str):
        """Update analysis display when content changes."""
        panel = self.query_one("#analysis-panel", Static)
        panel.update(Markdown(content))

    def update_log(self, content: str):
        """Public method to update log content."""
        self.log_content = content

    def show_analysis(self, analysis: str):
        """Public method to show analysis."""
        self.analysis_content = analysis

    def clear(self):
        """Clear both log and analysis."""
        self.log_content = ""
        self.analysis_content = ""
```

**Kent Checkpoint**: Is 70/30 split right? Should analysis be collapsible?

---

### 3.2 Update MainScreen

**Goal**: Integrate LogViewer and analysis into main screen.

**File**: `impl/zen-agents/zen_agents/screens/main.py`

**Claude Code Action**:
```
1. Read screens/main.py
2. Add LogViewer to layout
3. Add analyze button handler
4. Wire up AgentOrchestrator
```

**Key Changes**:
```python
from ..widgets.log_viewer import LogViewer
from ..services.agent_orchestrator import AgentOrchestrator

class MainScreen(Screen):
    def __init__(self):
        super().__init__()
        self.orchestrator = AgentOrchestrator()
        self.log_viewer = LogViewer()

    def compose(self):
        yield Header()
        with Horizontal():
            yield SessionList(id="session-list")
            with Vertical(id="detail-panel"):
                yield SessionDetail(id="session-detail")
                yield self.log_viewer
        yield StatusBar()
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "analyze-btn":
            await self._analyze_current_session()

    async def _analyze_current_session(self):
        """Analyze current session's output."""
        session = self.selected_session
        if not session:
            self.notify("No session selected", severity="warning")
            return

        # Check if LLM available
        if not await self.orchestrator.check_available():
            self.notify("Claude CLI not available", severity="error")
            return

        self.notify("Analyzing...", timeout=2)

        # Capture pane content
        log = await self.tmux.capture_pane(session.tmux_session)
        self.log_viewer.update_log(log)

        # Analyze with HypothesisEngine
        try:
            result = await self.orchestrator.analyze_log(log)
            analysis = "## Hypotheses\n"
            for h in result.hypotheses:
                analysis += f"• {h}\n"
            if result.suggested_tests:
                analysis += "\n## Tests\n"
                for t in result.suggested_tests:
                    analysis += f"✓ {t}\n"
            self.log_viewer.show_analysis(analysis)
            self.notify(f"Found {len(result.hypotheses)} hypotheses")
        except Exception as e:
            self.notify(f"Analysis failed: {e}", severity="error")
```

**Kent Checkpoint**: Should analysis run automatically on session select, or only on demand?

---

### 3.3 K-gent Name Suggestions

**Goal**: Use K-gent to suggest session names in create modal.

**File**: `impl/zen-agents/zen_agents/screens/main.py` (CreateSessionModal)

**Claude Code Action**:
```
1. Find CreateSessionModal class
2. Add "Suggest" button next to name input
3. Wire to orchestrator.suggest_session_name()
```

**Key Changes**:
```python
class CreateSessionModal(ModalScreen):
    def compose(self):
        with Vertical(id="modal-content"):
            yield Static("Create New Session", id="modal-title")
            with Horizontal():
                yield Input(placeholder="session-name", id="name-input")
                yield Button("Suggest", id="suggest-btn", variant="default")
            yield Select(
                [(t.value, t) for t in SessionType],
                id="type-select"
            )
            yield Input(placeholder="/path/to/workdir", id="workdir-input")
            with Horizontal():
                yield Button("Create", id="create-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "suggest-btn":
            await self._suggest_name()
        # ... existing handlers

    async def _suggest_name(self):
        """Get K-gent name suggestion."""
        workdir = self.query_one("#workdir-input", Input).value or "~"
        session_type = self.query_one("#type-select", Select).value

        try:
            name = await self.app.orchestrator.suggest_session_name(
                working_dir=workdir,
                session_type=session_type.value if session_type else "shell"
            )
            self.query_one("#name-input", Input).value = name
        except Exception:
            # Fallback to timestamp-based name
            from datetime import datetime
            self.query_one("#name-input", Input).value = f"session-{datetime.now():%H%M}"
```

**Kent Checkpoint**: Should suggestions be cached? Rate-limited?

---

## Phase 4: Persistence

### 4.1 Session Persistence

**Goal**: Save sessions to survive TUI restart.

**File**: `impl/zen-agents/zen_agents/services/persistence.py`

**Claude Code Action**:
```
1. Create services/persistence.py
2. Implement JSON-based persistence
3. Handle session recovery on startup
```

**Implementation**:
```python
"""Session persistence layer."""

import json
from pathlib import Path
from dataclasses import asdict, fields
from datetime import datetime
from typing import Optional
from uuid import UUID

from ..models.session import Session, SessionState, SessionType


CONFIG_DIR = Path.home() / ".config" / "zen-agents"
SESSIONS_FILE = CONFIG_DIR / "sessions.json"


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime and UUID."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, (SessionState, SessionType)):
            return obj.value
        return super().default(obj)


class SessionPersistence:
    """Persist sessions across TUI restarts."""

    def __init__(self, sessions_file: Path = SESSIONS_FILE):
        self.sessions_file = sessions_file
        self.sessions_file.parent.mkdir(parents=True, exist_ok=True)

    def save(self, sessions: list[Session]) -> None:
        """Save sessions to file."""
        data = []
        for session in sessions:
            session_dict = {
                "id": str(session.id),
                "name": session.name,
                "session_type": session.session_type.value,
                "state": session.state.value,
                "tmux_session": session.tmux_session,
                "working_dir": session.working_dir,
                "created_at": session.created_at.isoformat(),
                "metadata": session.metadata,
            }
            if session.exit_code is not None:
                session_dict["exit_code"] = session.exit_code
            data.append(session_dict)

        self.sessions_file.write_text(
            json.dumps(data, indent=2, cls=DateTimeEncoder)
        )

    def load(self) -> list[Session]:
        """Load sessions from file."""
        if not self.sessions_file.exists():
            return []

        try:
            data = json.loads(self.sessions_file.read_text())
            sessions = []
            for d in data:
                session = Session(
                    id=UUID(d["id"]),
                    name=d["name"],
                    session_type=SessionType(d["session_type"]),
                    state=SessionState(d["state"]),
                    tmux_session=d["tmux_session"],
                    working_dir=d.get("working_dir", "~"),
                    created_at=datetime.fromisoformat(d["created_at"]),
                    exit_code=d.get("exit_code"),
                    metadata=d.get("metadata", {}),
                )
                sessions.append(session)
            return sessions
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Corrupted file - start fresh
            return []

    def delete(self) -> None:
        """Delete persistence file."""
        if self.sessions_file.exists():
            self.sessions_file.unlink()
```

**Kent Checkpoint**: JSON or SQLite? Should we persist session logs too?

---

### 4.2 Integrate Persistence

**File**: `impl/zen-agents/zen_agents/services/session_manager.py`

**Claude Code Action**:
```
1. Read services/session_manager.py
2. Add persistence on session create/kill/state change
3. Load on startup
4. Reconcile with actual tmux state
```

**Key Changes**:
```python
from .persistence import SessionPersistence

class SessionManager:
    def __init__(self):
        # ... existing init ...
        self._persistence = SessionPersistence()
        self._load_persisted_sessions()

    def _load_persisted_sessions(self):
        """Load sessions from persistence and reconcile with tmux."""
        persisted = self._persistence.load()
        for session in persisted:
            # Check if tmux session still exists
            if await self._tmux.session_exists(session.tmux_session):
                self._sessions[session.id] = session
            else:
                # Mark as dead
                session.state = SessionState.DEAD

    def _save(self):
        """Save current sessions to persistence."""
        self._persistence.save(list(self._sessions.values()))

    async def create_session(self, config: NewSessionConfig) -> Session:
        session = await self._execute_create_pipeline(config)
        self._sessions[session.id] = session
        self._save()  # Persist
        return session

    async def kill_session(self, session_id: UUID):
        # ... existing kill logic ...
        self._save()  # Persist
```

---

## Phase 5: Testing

### 5.1 Test Structure

**Goal**: Comprehensive test coverage.

**Directory**: `impl/zen-agents/tests/`

**Claude Code Action**:
```
1. Create tests/ directory structure
2. Create conftest.py with fixtures
3. Implement unit tests for each component
4. Implement integration tests
```

**Structure**:
```
tests/
├── conftest.py                   # Shared fixtures
├── test_agents/
│   ├── test_detection.py         # StateDetector (Fix)
│   ├── test_conflict.py          # Contradict/Sublate
│   ├── test_judge.py             # Judge validators
│   └── test_pipelines.py         # Pipeline composition
├── test_services/
│   ├── test_orchestrator.py      # AgentOrchestrator
│   ├── test_session_handler.py   # SessionTypeHandler
│   ├── test_persistence.py       # SessionPersistence
│   └── test_tmux.py              # TmuxService (mock)
└── test_integration/
    └── test_full_flow.py         # End-to-end
```

### 5.2 Key Test Fixtures

**File**: `tests/conftest.py`

```python
"""Test fixtures for zen-agents."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from zen_agents.models.session import Session, SessionState, SessionType
from zen_agents.services.agent_orchestrator import AgentOrchestrator


@pytest.fixture
def mock_session():
    """Create a mock session."""
    return Session(
        id=uuid4(),
        name="test-session",
        session_type=SessionType.SHELL,
        state=SessionState.RUNNING,
        tmux_session="zen-test-session",
        working_dir="/tmp",
        created_at=datetime.now(),
    )


@pytest.fixture
def mock_runtime():
    """Mock ClaudeCLIRuntime."""
    runtime = AsyncMock()
    runtime.execute.return_value = MagicMock(
        output=MagicMock(
            hypotheses=[
                MagicMock(statement="Test hypothesis 1"),
                MagicMock(statement="Test hypothesis 2"),
            ],
            suggested_tests=["Test A", "Test B"],
            reasoning_chain=["Step 1", "Step 2"],
        )
    )
    return runtime


@pytest.fixture
def orchestrator(mock_runtime):
    """AgentOrchestrator with mock runtime."""
    orch = AgentOrchestrator(runtime=mock_runtime)
    return orch


@pytest.fixture
def mock_tmux():
    """Mock TmuxService."""
    tmux = AsyncMock()
    tmux.session_exists.return_value = True
    tmux.is_session_alive.return_value = True
    tmux.capture_pane.return_value = "test output"
    return tmux
```

### 5.3 Example Tests

**File**: `tests/test_services/test_orchestrator.py`

```python
"""Tests for AgentOrchestrator."""

import pytest


@pytest.mark.asyncio
async def test_analyze_log(orchestrator, mock_runtime):
    """Test log analysis via HypothesisEngine."""
    result = await orchestrator.analyze_log(
        log_content="Error: connection refused",
        domain="networking"
    )

    assert len(result.hypotheses) == 2
    assert "Test hypothesis 1" in result.hypotheses
    mock_runtime.execute.assert_called_once()


@pytest.mark.asyncio
async def test_expand_idea(orchestrator, mock_runtime):
    """Test idea expansion via CreativityCoach."""
    mock_runtime.execute.return_value.output.responses = ["idea1", "idea2"]
    mock_runtime.execute.return_value.output.follow_ups = ["follow1"]

    result = await orchestrator.expand_idea("distributed systems")

    assert result.ideas == ["idea1", "idea2"]
    assert result.follow_ups == ["follow1"]


@pytest.mark.asyncio
async def test_kgent_dialogue(orchestrator, mock_runtime):
    """Test K-gent dialogue."""
    from zen_agents.kgents_bridge import DialogueMode

    mock_runtime.execute.return_value.output.response = "Reflecting on that..."

    result = await orchestrator.kgent_dialogue(
        "Should I add another feature?",
        mode=DialogueMode.REFLECT
    )

    assert result.response == "Reflecting on that..."
    assert result.mode == DialogueMode.REFLECT
```

---

## Execution Protocol

### For Each Phase

```
LOOP:
  1. Claude Code reads this protocol
  2. Claude Code implements phase
  3. Run tests (if applicable)
  4. Kent reviews (Judge)
  5. IF accept: mark complete, next phase
     ELIF revise: Claude Code modifies
     ELIF reject: discuss, potentially Sublate
```

### Termination Condition (Fix)

Implementation is complete when:
```python
def protocol_complete() -> bool:
    return all([
        # Phase 1: Foundation
        exists("zen_agents/kgents_bridge.py"),
        exists("zen_agents/services/agent_orchestrator.py"),
        confidence_bug_fixed("zen_agents/agents/detection.py"),
        pipelines_use_composition("zen_agents/agents/pipelines/"),

        # Phase 2: LLM Session Types
        session_type_extended("zen_agents/models/session.py"),
        exists("zen_agents/services/session_handler.py"),

        # Phase 3: UI
        exists("zen_agents/widgets/log_viewer.py"),
        main_screen_integrated("zen_agents/screens/main.py"),

        # Phase 4: Persistence
        exists("zen_agents/services/persistence.py"),
        persistence_integrated("zen_agents/services/session_manager.py"),

        # Phase 5: Testing
        tests_pass("tests/"),
        coverage_above(80),

        # Human Ground
        kent_approves(),
    ])
```

---

## Meta-Instructions for Claude Code

When reading this document:

1. **Follow phase order** — 1 → 2 → 3 → 4 → 5
2. **Read existing code first** — Understand before modifying
3. **Preserve working functionality** — zen-agents already works; enhance, don't break
4. **Use existing patterns** — zen-agents already uses bootstrap; align with them
5. **Test incrementally** — Run zen-agents after each phase to verify
6. **Ask Kent** — When design decisions arise
7. **Update HYDRATE.md** — As phases complete

### On Tensions

If you encounter contradictions between:
- This protocol and existing zen-agents code
- kgents patterns and Textual TUI patterns
- Desired features and complexity budget

Surface them explicitly. Propose synthesis or hold for Kent's judgment.

### On Async/UI

Textual has its own async event loop. When executing LLM calls:
1. Use `self.call_later()` or `self.run_worker()` for long operations
2. Show loading indicators
3. Don't block the UI thread

---

## Quick Start

To begin implementation:

```bash
# Kent runs:
claude "Read ZENAGENTS_PROTOCOL.md and implement Phase 1.1 (Import Bridge)"
```

Claude Code will:
1. Read this protocol
2. Create `kgents_bridge.py`
3. Verify imports work
4. Request review

---

## Success Criteria

| Criterion | Verification |
|-----------|--------------|
| LLM sessions work | Create ROBIN session, type query, get synthesis |
| Analysis works | Select session, click Analyze, see hypotheses |
| Composition works | Pipelines use `>>` operator |
| Persistence works | Create session, restart TUI, session appears |
| K-gent naming works | Click Suggest, get personalized name |
| Tests pass | `pytest tests/ -v` passes with 80%+ coverage |
| UI responsive | LLM calls don't block session list |

---

## Changelog

- **Dec 2025**: Initial protocol created
- **Status**: Ready for Phase 1.1
