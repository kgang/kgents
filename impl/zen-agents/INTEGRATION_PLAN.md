# zen-agents + kgents Integration Plan

> **Note**: This document provides overview and diagrams. For the full implementation protocol, see `/ZENAGENTS_PROTOCOL.md` in the repo root.

## Executive Summary

**Goal**: Complete zen-agents TUI by integrating kgents agents via ClaudeCLIRuntime.

**Current State**:
- zen-agents: ~70% complete TUI for tmux session management
- Uses bootstrap patterns (Ground, Judge, Contradict, Sublate, Fix)
- **Gap**: No actual LLM integration despite session types for Claude/Gemini/OpenRouter
- **Gap**: Manual pipeline orchestration (not using `>>` composition)
- **Gap**: No tests, no persistence, no session log viewing

**Solution**: Wire kgents agents through ClaudeCLIRuntime to enable intelligent features.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        zen-agents TUI                           │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐ │
│  │ SessionList  │  │SessionDetail │  │ Intelligent Panels    │ │
│  │              │  │              │  │ - Log Analysis        │ │
│  │  [Claude]    │  │ State: RUN   │  │ - Hypothesis View     │ │
│  │  [Robin]     │  │ Exit: 0      │  │ - Creative Expand     │ │
│  │  [Research]  │  │              │  │ - K-gent Dialogue     │ │
│  └──────────────┘  └──────────────┘  └───────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AgentOrchestrator                            │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │
│  │ SessionMgr  │──▶│   Router    │──▶│  Agent Pipeline     │   │
│  │  (existing) │   │ (C-gents)   │   │  (>> composition)   │   │
│  └─────────────┘   └─────────────┘   └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    kgents Agents                                │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │ K-gent     │ │ Robin      │ │ Creativity │ │ Hegel      │   │
│  │ (persona)  │ │ (science)  │ │ Coach      │ │ (dialect)  │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ClaudeCLIRuntime                              │
│         (OAuth via Claude CLI - no API key needed)              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation (Infrastructure)

### 1.1 Add kgents as dependency

**File**: `impl/zen-agents/pyproject.toml`

```toml
[project]
dependencies = [
    "textual>=0.40.0",
    # Add path dependency to kgents
]

[tool.setuptools]
packages = ["zen_agents"]

# For development, use editable install of kgents
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
]
```

**Alternative**: Symlink or relative import from `../../claude-openrouter/`

### 1.2 Create AgentOrchestrator service

**New File**: `zen_agents/services/agent_orchestrator.py`

```python
"""Orchestrates kgents agents for zen-agents TUI."""

import sys
from pathlib import Path
from typing import Optional

# Add kgents to path (temporary until proper packaging)
KGENTS_PATH = Path(__file__).parent.parent.parent.parent / "claude-openrouter"
sys.path.insert(0, str(KGENTS_PATH))

from runtime import ClaudeCLIRuntime
from agents.a import CreativityCoach, creativity_coach, CreativityInput, CreativityMode
from agents.b import (
    HypothesisEngine, hypothesis_engine, HypothesisInput,
    RobinAgent, robin, RobinInput
)
from agents.h import HegelAgent, hegel, DialecticInput
from agents.k import KgentAgent, kgent, DialogueMode, DialogueInput, PersonaQuery


class AgentOrchestrator:
    """Central orchestrator for LLM-backed agents in zen-agents."""

    def __init__(self):
        self._runtime: Optional[ClaudeCLIRuntime] = None
        self._creativity_coach: Optional[CreativityCoach] = None
        self._hypothesis_engine: Optional[HypothesisEngine] = None
        self._robin: Optional[RobinAgent] = None
        self._hegel: Optional[HegelAgent] = None
        self._kgent: Optional[KgentAgent] = None

    @property
    def runtime(self) -> ClaudeCLIRuntime:
        if self._runtime is None:
            self._runtime = ClaudeCLIRuntime()
        return self._runtime

    async def analyze_log(self, log_content: str, domain: str = "software") -> dict:
        """Analyze session log content using HypothesisEngine."""
        engine = hypothesis_engine()
        result = await self.runtime.execute(engine, HypothesisInput(
            observations=[log_content],
            domain=domain,
            question="What's happening in this session?"
        ))
        return {
            "hypotheses": [h.statement for h in result.output.hypotheses],
            "tests": result.output.suggested_tests
        }

    async def expand_idea(self, seed: str, mode: CreativityMode = CreativityMode.EXPAND) -> list[str]:
        """Expand an idea using CreativityCoach."""
        coach = creativity_coach()
        result = await self.runtime.execute(coach, CreativityInput(
            seed=seed,
            mode=mode
        ))
        return result.output.responses

    async def scientific_dialogue(
        self,
        query: str,
        domain: str,
        mode: DialogueMode = DialogueMode.EXPLORE
    ) -> dict:
        """Have a scientific dialogue using Robin."""
        robin_agent = robin(runtime=self.runtime)
        result = await robin_agent.invoke(RobinInput(
            query=query,
            domain=domain,
            dialogue_mode=mode
        ))
        return {
            "synthesis": result.synthesis_narrative,
            "hypotheses": [h.statement for h in result.hypotheses],
            "next_questions": result.next_questions
        }

    async def kgent_dialogue(
        self,
        message: str,
        mode: DialogueMode = DialogueMode.REFLECT
    ) -> str:
        """Dialogue with K-gent for personalized responses."""
        k = kgent()
        result = await self.runtime.execute(k, DialogueInput(
            message=message,
            mode=mode
        ))
        return result.output.response

    async def dialectic_analysis(self, thesis: str, antithesis: str) -> dict:
        """Analyze contradiction using HegelAgent."""
        h = hegel()
        result = await self.runtime.execute(h, DialecticInput(
            thesis=thesis,
            antithesis=antithesis
        ))
        return {
            "synthesis": result.output.synthesis,
            "notes": result.output.sublation_notes,
            "productive_tension": result.output.productive_tension
        }
```

### 1.3 Fix pipeline composition

**Update**: `zen_agents/agents/pipelines/create.py`

Replace manual orchestration with `>>` composition:

```python
from bootstrap import compose

# BEFORE (manual):
async def execute_create_pipeline(config, manager):
    validated = await ValidateLimit().invoke(config)
    conflicts = await DetectConflicts().invoke(validated)
    resolved = await ResolveConflicts().invoke(conflicts)
    session = await SpawnTmux().invoke(resolved)
    return await DetectInitialState().invoke(session)

# AFTER (composed):
CreateSessionPipeline = (
    ValidateLimit()
    >> DetectConflicts()
    >> ResolveConflicts()
    >> SpawnTmux()
    >> DetectInitialState()
)

async def execute_create_pipeline(config, manager):
    return await CreateSessionPipeline.invoke(config)
```

### 1.4 Fix StateDetector confidence bug

**File**: `zen_agents/agents/detection.py:92`

```python
# BEFORE (bug):
confidence=min(1.0, 0.2),  # Always 0.2

# AFTER (accumulating confidence):
confidence=min(1.0, previous_confidence + 0.2),  # Builds up
```

---

## Phase 2: LLM-Powered Session Types

### 2.1 Intelligent Session Types

**Update session types** to actually use LLM agents:

```python
# zen_agents/models/session.py

class SessionType(Enum):
    SHELL = "shell"           # Plain bash
    CLAUDE = "claude"         # Claude CLI interactive
    ROBIN = "robin"           # Robin scientific companion
    CREATIVITY = "creativity" # CreativityCoach session
    HYPOTHESIS = "hypothesis" # HypothesisEngine session
    KGENT = "kgent"          # K-gent dialogue session
```

### 2.2 Session Type Handlers

**New File**: `zen_agents/services/session_handlers.py`

```python
"""LLM-backed session type handlers."""

from ..models.session import SessionType
from .agent_orchestrator import AgentOrchestrator

class SessionTypeHandler:
    """Routes session types to appropriate agents."""

    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator

    async def handle_input(self, session_type: SessionType, input_text: str) -> str:
        """Handle user input based on session type."""
        match session_type:
            case SessionType.ROBIN:
                result = await self.orchestrator.scientific_dialogue(
                    query=input_text,
                    domain="general"
                )
                return result["synthesis"]

            case SessionType.CREATIVITY:
                ideas = await self.orchestrator.expand_idea(input_text)
                return "\n".join(f"• {idea}" for idea in ideas)

            case SessionType.HYPOTHESIS:
                result = await self.orchestrator.analyze_log(input_text)
                return "\n".join(result["hypotheses"])

            case SessionType.KGENT:
                return await self.orchestrator.kgent_dialogue(input_text)

            case _:
                return input_text  # Pass through for shell/claude
```

---

## Phase 3: UI Enhancements

### 3.1 Log Viewer Widget

**New File**: `zen_agents/widgets/log_viewer.py`

```python
"""Log viewer widget with LLM analysis."""

from textual.widgets import Static, RichLog
from textual.containers import Vertical

class LogViewer(Vertical):
    """Session log viewer with analysis panel."""

    def compose(self):
        yield RichLog(id="raw-log", wrap=True)
        yield Static(id="analysis", classes="analysis-panel")

    async def update_log(self, content: str):
        log = self.query_one("#raw-log", RichLog)
        log.write(content)

    async def show_analysis(self, analysis: dict):
        panel = self.query_one("#analysis", Static)
        text = "## Analysis\n"
        for h in analysis.get("hypotheses", []):
            text += f"• {h}\n"
        panel.update(text)
```

### 3.2 Intelligent Session Detail

**Update**: `zen_agents/screens/main.py`

Add "Analyze" button that uses HypothesisEngine:

```python
class SessionDetail(Static):
    def compose(self):
        # ... existing widgets ...
        yield Button("Analyze", id="analyze-btn", variant="primary")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "analyze-btn":
            session = self.selected_session
            if session:
                # Capture pane content
                log = await self.tmux.capture_pane(session.tmux_session)
                # Analyze with HypothesisEngine
                analysis = await self.orchestrator.analyze_log(log)
                self.app.notify(f"Found {len(analysis['hypotheses'])} hypotheses")
```

### 3.3 K-gent Integration for Session Naming

Use K-gent to suggest session names based on context:

```python
async def suggest_session_name(self, working_dir: str, session_type: SessionType) -> str:
    """K-gent suggests personalized session name."""
    response = await self.orchestrator.kgent_dialogue(
        message=f"Suggest a short, memorable session name for a {session_type.value} session in {working_dir}",
        mode=DialogueMode.ADVISE
    )
    return response.split()[0]  # First word as name
```

---

## Phase 4: Advanced Features

### 4.1 Dialectic Conflict Resolution

Enhance Contradict/Sublate with HegelAgent for complex conflicts:

```python
# zen_agents/agents/conflict.py

async def resolve_complex_conflict(self, tension: Tension) -> Synthesis:
    """Use HegelAgent for complex conflict resolution."""
    result = await self.orchestrator.dialectic_analysis(
        thesis=tension.thesis,
        antithesis=tension.antithesis
    )
    if result["productive_tension"]:
        return HoldTension(reason=result["notes"])
    return Synthesis(resolution=result["synthesis"])
```

### 4.2 Robin-Powered Research Sessions

Create a specialized research session type that uses Robin:

```python
class ResearchSession:
    """Robin-powered research companion session."""

    def __init__(self, domain: str, orchestrator: AgentOrchestrator):
        self.domain = domain
        self.orchestrator = orchestrator
        self.observations: list[str] = []

    async def observe(self, observation: str):
        """Add observation from session output."""
        self.observations.append(observation)

    async def hypothesize(self, question: str) -> dict:
        """Generate hypotheses from accumulated observations."""
        return await self.orchestrator.scientific_dialogue(
            query=question,
            domain=self.domain,
            mode=DialogueMode.EXPLORE
        )
```

### 4.3 Session Persistence

**New File**: `zen_agents/services/persistence.py`

```python
"""Session persistence layer."""

import json
from pathlib import Path
from dataclasses import asdict

SESSIONS_FILE = Path.home() / ".config" / "zen-agents" / "sessions.json"

class SessionPersistence:
    """Persist sessions across restarts."""

    def save(self, sessions: list[Session]):
        SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(s) for s in sessions]
        SESSIONS_FILE.write_text(json.dumps(data, indent=2, default=str))

    def load(self) -> list[Session]:
        if not SESSIONS_FILE.exists():
            return []
        data = json.loads(SESSIONS_FILE.read_text())
        return [Session(**d) for d in data]
```

---

## Phase 5: Testing

### 5.1 Test Structure

```
impl/zen-agents/tests/
├── conftest.py              # Fixtures (mock runtime, sessions)
├── test_agents/
│   ├── test_detection.py    # StateDetector tests
│   ├── test_conflict.py     # Contradict/Sublate tests
│   └── test_pipelines.py    # Pipeline composition tests
├── test_services/
│   ├── test_orchestrator.py # AgentOrchestrator tests
│   └── test_tmux.py         # TmuxService tests
└── test_integration/
    └── test_full_flow.py    # End-to-end tests
```

### 5.2 Key Test Cases

```python
# tests/test_services/test_orchestrator.py

import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_runtime():
    """Mock ClaudeCLIRuntime for testing."""
    runtime = AsyncMock()
    runtime.execute.return_value.output = MockOutput()
    return runtime

@pytest.mark.asyncio
async def test_analyze_log(mock_runtime):
    orch = AgentOrchestrator()
    orch._runtime = mock_runtime

    result = await orch.analyze_log("Error: connection refused", domain="networking")

    assert "hypotheses" in result
    mock_runtime.execute.assert_called_once()

@pytest.mark.asyncio
async def test_creativity_expansion(mock_runtime):
    orch = AgentOrchestrator()
    orch._runtime = mock_runtime
    mock_runtime.execute.return_value.output.responses = ["idea1", "idea2"]

    ideas = await orch.expand_idea("distributed systems")

    assert len(ideas) == 2
```

---

## Implementation Order

| Order | Task | Files | Depends On |
|-------|------|-------|------------|
| 1 | Add kgents import path | `__init__.py` | - |
| 2 | Create AgentOrchestrator | `services/agent_orchestrator.py` | 1 |
| 3 | Fix confidence bug | `agents/detection.py` | - |
| 4 | Refactor to `>>` composition | `agents/pipelines/*.py` | - |
| 5 | Add session type handlers | `services/session_handlers.py` | 2 |
| 6 | Add LogViewer widget | `widgets/log_viewer.py` | - |
| 7 | Integrate analyze button | `screens/main.py` | 2, 6 |
| 8 | Add K-gent name suggestion | `screens/main.py` | 2 |
| 9 | Add persistence | `services/persistence.py` | - |
| 10 | Add test suite | `tests/` | 1-9 |

---

## Success Criteria

1. **LLM Integration**: Sessions can invoke CreativityCoach, HypothesisEngine, Robin, K-gent
2. **Composition**: Pipelines use `>>` operator instead of manual orchestration
3. **Persistence**: Sessions survive TUI restart
4. **Analysis**: Log viewer shows LLM-generated hypotheses
5. **Personalization**: K-gent influences session naming and interactions
6. **Tests**: 80%+ coverage on services and agents

---

## Open Questions

1. **Async TUI**: How to handle long LLM calls without blocking UI?
   - Option A: Run in worker thread
   - Option B: Show progress indicator, allow cancel

2. **Token costs**: Should we cache/batch LLM calls?
   - ClaudeCLIRuntime uses OAuth (no direct cost tracking)
   - Consider local caching for repeated queries

3. **Offline mode**: What happens when Claude CLI unavailable?
   - Graceful degradation to shell-only features
   - Queue requests for when connection restored

4. **Model selection**: Should UI expose model choice?
   - ClaudeCLIRuntime uses default model
   - Could add dropdown for OpenRouter multi-model
