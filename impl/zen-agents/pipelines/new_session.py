"""
New Session Pipeline

The crown jewel: composing agents into a full session creation flow.

Pipeline: SessionConfig → Session (running in tmux)

Composed of:
    1. Judge(config) → validate config is acceptable
    2. Create(config) → create session object (CREATING state)
    3. Spawn(session) → spawn tmux session
    4. Detect(session) → detect initial state (Fix-based)

This demonstrates the research plan's key insight:
    "SessionManager" = Compose(Judge, Create, Spawn, Detect)

The pipeline is itself an agent - composition produces agents.
"""

from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Any

from bootstrap import Agent, compose, pipeline as make_pipeline
from zen_agents.types import (
    Session,
    SessionConfig,
    SessionState,
    SessionType,
    SessionVerdict,
    ZenGroundState,
)
from zen_agents.ground import ZenGround, zen_ground
from zen_agents.judge import ZenJudge, zen_judge
from zen_agents.session.create import SessionCreate, create_session
from zen_agents.session.detect import SessionDetect, detect_state, DetectionResult
from zen_agents.tmux.spawn import TmuxSpawn, spawn_tmux, SpawnInput, SpawnError


@dataclass
class PipelineResult:
    """Result of the full pipeline"""
    success: bool
    session: Session | None
    verdict: SessionVerdict | None
    detection: DetectionResult | None
    error: str | None = None

    @classmethod
    def failed(cls, error: str, verdict: SessionVerdict | None = None) -> 'PipelineResult':
        return cls(
            success=False,
            session=None,
            verdict=verdict,
            detection=None,
            error=error,
        )


class NewSessionPipeline(Agent[SessionConfig, PipelineResult]):
    """
    Full session creation pipeline.

    Type signature: NewSessionPipeline: SessionConfig → PipelineResult

    Composition:
        Judge → Create → Spawn → Detect

    This is NOT a simple pipeline composition because:
        - We need to handle errors at each step
        - Spawn needs data from both config AND session
        - We want to preserve intermediate results

    But conceptually it IS composition - each step transforms
    and passes to the next.

    In zenportal: This is SessionManager.create_session()
    In zen-agents: This is explicit composition with transparent flow.
    """

    def __init__(
        self,
        judge: ZenJudge | None = None,
        ground: ZenGround | None = None,
        spawn: TmuxSpawn | None = None,
        detect: SessionDetect | None = None,
    ):
        self._judge = judge or zen_judge
        self._ground = ground or zen_ground
        self._spawn = spawn or spawn_tmux
        self._detect = detect or detect_state

    @property
    def name(self) -> str:
        return "NewSessionPipeline"

    @property
    def genus(self) -> str:
        return "zen/pipeline"

    @property
    def purpose(self) -> str:
        return "Full session creation: config → running session"

    async def invoke(self, config: SessionConfig) -> PipelineResult:
        """
        Execute the full pipeline.

        Steps:
            1. Get ground state (for context)
            2. Judge config (validate)
            3. Create session object
            4. Build tmux command
            5. Spawn tmux session
            6. Detect initial state
        """

        # Step 1: Ground - get context
        ground_state = await self._ground.invoke(None)
        judge_with_context = self._judge.with_ground(ground_state)

        # Step 2: Judge - validate config
        verdict = await judge_with_context.invoke(config)
        if not verdict.valid:
            return PipelineResult.failed(
                error=f"Validation failed: {'; '.join(verdict.issues)}",
                verdict=verdict,
            )

        # Step 3: Create - make session object
        session = await create_session.invoke(config)

        # Step 4: Build command
        command = self._build_command(config)

        # Step 5: Spawn - create tmux session
        spawn_input = SpawnInput(
            name=session.id,
            command=command,
            working_dir=Path(config.working_dir) if config.working_dir else None,
            env=config.env,
        )

        spawn_result = await self._spawn.invoke(spawn_input)

        if isinstance(spawn_result, SpawnError):
            # Update session to FAILED
            session = replace(
                session,
                state=SessionState.FAILED,
                error=spawn_result.error,
            )
            return PipelineResult.failed(
                error=f"Spawn failed: {spawn_result.error}",
                verdict=verdict,
            )

        # Step 6: Update session with tmux info
        session = replace(
            session,
            state=SessionState.RUNNING,
            tmux=spawn_result,
            started_at=datetime.now(),
        )

        # Step 7: Detect - get initial state
        detection = await self._detect.invoke(session)

        # Update ground state
        self._ground.update_session(session)

        return PipelineResult(
            success=True,
            session=session,
            verdict=verdict,
            detection=detection,
        )

    def _build_command(self, config: SessionConfig) -> str:
        """
        Build the shell command for the session type.

        Maps to zenportal's SessionCommandBuilder.
        """
        if config.command:
            return config.command

        match config.session_type:
            case SessionType.CLAUDE:
                cmd = "claude"
                if config.model:
                    cmd += f" --model {config.model}"
                if config.system_prompt:
                    cmd += f" --system-prompt '{config.system_prompt}'"
                return cmd

            case SessionType.SHELL:
                return "zsh -l"

            case SessionType.CODEX:
                return "codex"

            case SessionType.GEMINI:
                return "gemini"

            case SessionType.CUSTOM:
                return config.command or "zsh -l"

            case _:
                return "zsh -l"


# Factory function for convenient creation
def create_session_pipeline(
    ground: ZenGround | None = None,
    tmux_prefix: str = "zen",
) -> NewSessionPipeline:
    """Create a new session pipeline with optional customization."""
    return NewSessionPipeline(
        ground=ground,
        spawn=TmuxSpawn(prefix=tmux_prefix),
    )
