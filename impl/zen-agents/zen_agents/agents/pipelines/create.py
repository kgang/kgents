"""
CreateSessionPipeline: Compose-based session creation.

Pipeline:
    ValidateConfig         # Judge: config passes principles
    >> ResolveConfig       # Ground: merge tiers
    >> DetectConflicts     # Contradict: name collision, resource conflict
    >> ResolveConflicts    # Sublate: auto-resolve or surface to user
    >> SpawnTmux           # Id: pure creation
    >> DetectInitialState  # Fix: poll until state stabilizes
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


class SpawnTmux(Agent[CreateContext, "Session"]):
    """
    Id: Pure creation - spawn tmux session.

    The actual creation step. Transforms config into Session.
    """

    @property
    def name(self) -> str:
        return "SpawnTmux"

    async def invoke(self, ctx: CreateContext) -> "Session":
        """Spawn tmux session and return Session model."""
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
        return Session(
            id=uuid4(),
            name=ctx.config.name,
            session_type=ctx.config.session_type,
            state=SessionState.RUNNING,
            tmux_name=tmux_name,
            working_dir=ctx.config.working_dir,
            command=command,
        )


class DetectInitialState(Agent["Session", "Session"]):
    """
    Fix: Poll until state stabilizes.
    """

    def __init__(self, tmux: "TmuxService"):
        self._tmux = tmux

    @property
    def name(self) -> str:
        return "DetectInitialState"

    async def invoke(self, session: "Session") -> "Session":
        """Detect initial state using Fix-based polling."""
        from ..detection import detect_state
        from ...models import SessionState

        result = await detect_state(
            session=session,
            tmux=self._tmux,
            max_iterations=10,  # Quick initial check
        )

        if result.converged:
            return session.with_state(result.value.session_state)

        # If not converged, assume still running
        return session


# The composed pipeline
CreateSessionPipeline = (
    ValidateLimit
    # >> DetectConflicts  # Would need proper composition
    # >> ResolveConflicts
    # >> SpawnTmux
    # >> DetectInitialState
)


async def create_session_pipeline(
    config: "NewSessionConfig",
    zen_config: "ZenConfig",
    existing_sessions: list["Session"],
    tmux: "TmuxService",
) -> "Session":
    """
    Execute the full create session pipeline.

    This is the orchestrated version that runs all steps in sequence.
    The pipeline above shows the conceptual composition.
    """
    ctx = CreateContext(
        config=config,
        zen_config=zen_config,
        existing_sessions=existing_sessions,
        tmux=tmux,
    )

    # Step 1: Validate config (Judge)
    validate_config = ValidateConfig()
    ctx.config = await validate_config.invoke(ctx.config)

    # Step 2: Validate limit (Judge)
    validate_limit = ValidateLimit()
    ctx = await validate_limit.invoke(ctx)

    # Step 3: Detect conflicts (Contradict)
    detect_conflicts = DetectConflicts()
    ctx = await detect_conflicts.invoke(ctx)

    # Step 4: Resolve conflicts (Sublate)
    resolve_conflicts = ResolveConflicts()
    ctx = await resolve_conflicts.invoke(ctx)

    # Step 5: Spawn tmux (Id - pure creation)
    spawn = SpawnTmux()
    session = await spawn.invoke(ctx)

    # Step 6: Detect initial state (Fix)
    detect_state_agent = DetectInitialState(tmux)
    session = await detect_state_agent.invoke(session)

    return session
