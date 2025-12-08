"""
CreateSessionPipeline: Compose-based session creation.

Pipeline:
    ValidateConfig         # Judge: config passes principles
    >> ValidateLimit       # Judge: check session limit
    >> DetectConflicts     # Contradict: name collision, resource conflict
    >> ResolveConflicts    # Sublate: auto-resolve or surface to user
    >> SpawnTmux           # Id: pure creation
    >> DetectInitialState  # Fix: poll until state stabilizes

Design notes:
- All pipeline agents operate on CreateContext (unified context object)
- ValidateConfig is called BEFORE entering the pipeline (on raw config)
- DetectInitialState uses a factory to capture tmux dependency
- Composition is: ValidateLimit >> DetectConflicts >> ResolveConflicts >> SpawnTmux >> DetectInitialState
"""

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
from uuid import uuid4

from bootstrap import Agent, Verdict, VerdictType, HoldTension

if TYPE_CHECKING:
    from ...models import Session, NewSessionConfig, SessionState
    from ...services.tmux import TmuxService
    from ..config import ZenConfig


class ValidationError(Exception):
    """Raised when validation fails."""
    def __init__(self, reasons: list[str]):
        self.reasons = reasons
        super().__init__(f"Validation failed: {', '.join(reasons)}")


class ConflictError(Exception):
    """Raised when a conflict cannot be auto-resolved."""
    def __init__(self, reason: str, conflict_type: str):
        self.reason = reason
        self.conflict_type = conflict_type
        super().__init__(reason)


@dataclass
class CreateContext:
    """Context passed through the create pipeline."""
    config: "NewSessionConfig"
    zen_config: "ZenConfig"
    existing_sessions: list["Session"]
    tmux: "TmuxService"


@dataclass
class SpawnResult:
    """Result of SpawnTmux, carries Session + tmux for DetectInitialState."""
    session: "Session"
    tmux: "TmuxService"


class ValidateConfig(Agent["NewSessionConfig", "NewSessionConfig"]):
    """
    Judge: Validate session configuration.

    Raises ValidationError if config is rejected.
    """

    @property
    def name(self) -> str:
        return "ValidateConfig"

    async def invoke(self, config: "NewSessionConfig") -> "NewSessionConfig":
        """Validate config using SessionJudge."""
        from ..judge import SessionJudge

        judge = SessionJudge()
        verdict = await judge.invoke(config)

        if verdict.type == VerdictType.REJECT:
            raise ValidationError(verdict.reasons)

        # Revise verdicts are warnings - continue with caution
        return config


class ValidateLimit(Agent[CreateContext, CreateContext]):
    """
    Judge: Check session limit.

    Raises ValidationError if limit exceeded.
    """

    @property
    def name(self) -> str:
        return "ValidateLimit"

    async def invoke(self, ctx: CreateContext) -> CreateContext:
        """Check if within session limit."""
        max_sessions = ctx.zen_config.max_sessions

        if len(ctx.existing_sessions) >= max_sessions:
            raise ValidationError([
                f"Session limit ({max_sessions}) reached",
                f"Current sessions: {len(ctx.existing_sessions)}",
            ])

        return ctx


class DetectConflicts(Agent[CreateContext, CreateContext]):
    """
    Contradict: Check for conflicts before creation.
    """

    @property
    def name(self) -> str:
        return "DetectConflicts"

    async def invoke(self, ctx: CreateContext) -> CreateContext:
        """Check for conflicts."""
        from ..conflict import SessionContradict, ConflictInput

        contradict = SessionContradict()
        conflict = await contradict.invoke(ConflictInput(
            config=ctx.config,
            existing_sessions=ctx.existing_sessions,
        ))

        if conflict:
            # Store conflict in context for resolution
            ctx._conflict = conflict  # type: ignore

        return ctx


class ResolveConflicts(Agent[CreateContext, CreateContext]):
    """
    Sublate: Resolve detected conflicts or raise.
    """

    @property
    def name(self) -> str:
        return "ResolveConflicts"

    async def invoke(self, ctx: CreateContext) -> CreateContext:
        """Resolve any detected conflicts."""
        from ..conflict import ConflictSublate, SessionConflict
        from ...models import NewSessionConfig

        conflict = getattr(ctx, "_conflict", None)
        if not conflict:
            return ctx

        sublate = ConflictSublate()
        result = await sublate.invoke(conflict)

        if isinstance(result, HoldTension):
            raise ConflictError(
                result.reason,
                conflict.conflict_type if isinstance(conflict, SessionConflict) else "UNKNOWN",
            )

        # Apply resolution
        if hasattr(result, "result") and result.result:
            # Name was resolved (e.g., appended timestamp)
            if isinstance(result.result, str) and conflict.conflict_type == "NAME_COLLISION":
                ctx.config = NewSessionConfig(
                    name=result.result,
                    session_type=ctx.config.session_type,
                    working_dir=ctx.config.working_dir,
                    command=ctx.config.command,
                    env=ctx.config.env,
                    model=ctx.config.model,
                    api_key_env=ctx.config.api_key_env,
                )

        return ctx


class SpawnTmux(Agent[CreateContext, SpawnResult]):
    """
    Id: Pure creation - spawn tmux session.

    The actual creation step. Transforms config into SpawnResult.
    Outputs SpawnResult to carry tmux reference for DetectInitialState.
    """

    @property
    def name(self) -> str:
        return "SpawnTmux"

    async def invoke(self, ctx: CreateContext) -> SpawnResult:
        """Spawn tmux session and return SpawnResult."""
        from ...models import Session, SessionState

        # Generate tmux name
        tmux_name = f"{ctx.zen_config.tmux_prefix}-{uuid4().hex[:8]}"

        # Get command for session type
        command = ctx.config.command
        if not command:
            command = ctx.zen_config.session_commands.get(
                ctx.config.session_type.value,
                ctx.zen_config.default_shell,
            )

        # Spawn tmux session
        await ctx.tmux.create_session(
            name=tmux_name,
            command=command,
            working_dir=ctx.config.working_dir,
            env=ctx.config.env,
            scrollback=ctx.zen_config.scrollback_lines,
        )

        # Create session model
        session = Session(
            id=uuid4(),
            name=ctx.config.name,
            session_type=ctx.config.session_type,
            state=SessionState.RUNNING,
            tmux_name=tmux_name,
            working_dir=ctx.config.working_dir,
            command=command,
        )

        return SpawnResult(session=session, tmux=ctx.tmux)


class DetectInitialState(Agent[SpawnResult, "Session"]):
    """
    Fix: Poll until state stabilizes.

    Takes SpawnResult (which carries tmux) and returns final Session.
    This design enables >> composition without external dependencies.
    """

    @property
    def name(self) -> str:
        return "DetectInitialState"

    async def invoke(self, spawn_result: SpawnResult) -> "Session":
        """Detect initial state using Fix-based polling."""
        from ..detection import detect_state
        from ...models import SessionState

        session = spawn_result.session
        tmux = spawn_result.tmux

        result = await detect_state(
            session=session,
            tmux=tmux,
            max_iterations=10,  # Quick initial check
        )

        if result.converged:
            return session.with_state(result.value.session_state)

        # If not converged, assume still running
        return session


# The composed pipeline (types align!)
#
# Type flow:
#   CreateContext
#   → ValidateLimit    → CreateContext
#   → DetectConflicts  → CreateContext
#   → ResolveConflicts → CreateContext
#   → SpawnTmux        → SpawnResult
#   → DetectInitialState → Session
#
# This IS the pipeline: Compose, Don't Concatenate!
CreateSessionPipeline: Agent[CreateContext, "Session"] = (
    ValidateLimit()
    >> DetectConflicts()
    >> ResolveConflicts()
    >> SpawnTmux()
    >> DetectInitialState()
)


async def create_session_pipeline(
    config: "NewSessionConfig",
    zen_config: "ZenConfig",
    existing_sessions: list["Session"],
    tmux: "TmuxService",
) -> "Session":
    """
    Execute the full create session pipeline.

    1. ValidateConfig is called separately (different input type)
    2. CreateSessionPipeline handles: Limit >> Conflicts >> Resolve >> Spawn >> Detect

    Uses >> composition: "Compose, Don't Concatenate" (from spec/bootstrap.md).
    """
    # Pre-pipeline: Validate config (Judge) - different input type
    validate_config = ValidateConfig()
    validated_config = await validate_config.invoke(config)

    # Build context for composed pipeline
    ctx = CreateContext(
        config=validated_config,
        zen_config=zen_config,
        existing_sessions=existing_sessions,
        tmux=tmux,
    )

    # Execute composed pipeline: ValidateLimit >> DetectConflicts >> ResolveConflicts >> SpawnTmux >> DetectInitialState
    session = await CreateSessionPipeline.invoke(ctx)

    return session
