"""
Conflict Detection as Contradict.

Pre-creation validation surfaces tensions before runtime errors.

IDIOM: Conflict is Data
> Tensions should be first-class citizens.

Anti-pattern: Silent failures, swallowed exceptions, "last write wins".
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional, Union, TYPE_CHECKING

from bootstrap import (
    Agent,
    Tension,
    TensionMode,
    Sublate,
    Synthesis,
    ResolutionType,
    HoldTension,
)

if TYPE_CHECKING:
    from ..models import Session, NewSessionConfig


# Constants
MAX_SESSIONS = 10


class SessionConflict(Tension):
    """
    A conflict detected before session creation.

    Extends Tension with session-specific conflict types.
    """
    conflict_type: Literal["NAME_COLLISION", "WORKTREE_CONFLICT", "LIMIT_EXCEEDED"]
    suggested_resolution: str

    def __init__(
        self,
        mode: TensionMode,
        thesis,
        antithesis,
        description: str,
        conflict_type: Literal["NAME_COLLISION", "WORKTREE_CONFLICT", "LIMIT_EXCEEDED"],
        suggested_resolution: str,
        severity: float = 0.7,
    ):
        super().__init__(
            mode=mode,
            thesis=thesis,
            antithesis=antithesis,
            description=description,
            severity=severity,
        )
        self.conflict_type = conflict_type
        self.suggested_resolution = suggested_resolution


@dataclass
class ConflictInput:
    """Input for conflict checking."""
    config: "NewSessionConfig"
    existing_sessions: list["Session"]


class SessionContradict(Agent[ConflictInput, Optional[SessionConflict]]):
    """
    Detect conflicts before session creation.

    Surfaces tensions explicitly instead of letting them become runtime errors.
    """

    @property
    def name(self) -> str:
        return "SessionContradict"

    async def invoke(self, input: ConflictInput) -> Optional[SessionConflict]:
        """
        Check for conflicts between proposed config and existing sessions.

        Returns SessionConflict if conflict found, None otherwise.
        """
        config = input.config
        existing = input.existing_sessions

        # Check 1: Name collision
        existing_names = {s.name for s in existing}
        if config.name in existing_names:
            return SessionConflict(
                mode=TensionMode.PRAGMATIC,
                thesis=config.name,
                antithesis=list(existing_names),
                description=f"Session '{config.name}' already exists",
                conflict_type="NAME_COLLISION",
                suggested_resolution=f"Use '{config.name}-{datetime.now().strftime('%H%M%S')}'",
            )

        # Check 2: Session limit
        if len(existing) >= MAX_SESSIONS:
            return SessionConflict(
                mode=TensionMode.PRAGMATIC,
                thesis=config,
                antithesis=f"Current count: {len(existing)}",
                description=f"Session limit ({MAX_SESSIONS}) reached",
                conflict_type="LIMIT_EXCEEDED",
                suggested_resolution="Kill or clean up existing sessions",
                severity=0.9,
            )

        # Check 3: Worktree conflict (same working dir for same type)
        if config.working_dir:
            for session in existing:
                if (
                    session.working_dir == config.working_dir
                    and session.session_type == config.session_type
                    and session.state.value == "running"
                ):
                    return SessionConflict(
                        mode=TensionMode.PRAGMATIC,
                        thesis=config,
                        antithesis=session,
                        description=(
                            f"Session '{session.name}' already running in "
                            f"'{config.working_dir}' as {config.session_type.value}"
                        ),
                        conflict_type="WORKTREE_CONFLICT",
                        suggested_resolution=f"Attach to '{session.name}' instead",
                    )

        # No conflicts
        return None


SublateResult = Union[Synthesis, HoldTension]


class ConflictSublate(Sublate):
    """
    Resolve session conflicts or surface them for user decision.

    Resolution strategies by conflict type:
    - NAME_COLLISION: Auto-append timestamp
    - LIMIT_EXCEEDED: Hold for user decision
    - WORKTREE_CONFLICT: Hold for user decision
    """

    @property
    def name(self) -> str:
        return "ConflictSublate"

    async def invoke(self, tension: Tension) -> SublateResult:
        """Resolve or hold the tension."""
        if not isinstance(tension, SessionConflict):
            # Delegate to parent for generic tensions
            return await super().invoke(tension)

        conflict = tension

        if conflict.conflict_type == "NAME_COLLISION":
            # Auto-resolve: append timestamp
            return Synthesis(
                resolution_type=ResolutionType.ELEVATE,
                result=conflict.suggested_resolution,
                explanation=f"Renamed session to avoid collision: {conflict.suggested_resolution}",
                preserved=[conflict.thesis],
                negated=[],
            )

        elif conflict.conflict_type == "LIMIT_EXCEEDED":
            # Cannot auto-resolve: need user to free up space
            return HoldTension(
                tension=conflict,
                reason="Session limit reached. Clean up existing sessions first.",
                revisit_conditions=[
                    "User kills a session",
                    "User explicitly overrides limit",
                ],
            )

        elif conflict.conflict_type == "WORKTREE_CONFLICT":
            # Cannot auto-resolve: user should decide whether to reuse
            return HoldTension(
                tension=conflict,
                reason="A session is already running in this directory.",
                revisit_conditions=[
                    "User chooses to attach to existing session",
                    "User confirms creating duplicate",
                ],
            )

        # Unknown conflict type: hold for safety
        return HoldTension(
            tension=conflict,
            reason=f"Unknown conflict type: {conflict.conflict_type}",
            revisit_conditions=["Conflict type handler implemented"],
        )


class NameCollisionResolver(Agent["NewSessionConfig", "NewSessionConfig"]):
    """
    Resolve name collisions by appending timestamp.

    Used in pipelines when name collision is detected.
    """

    def __init__(self, existing_names: set[str]):
        self._existing_names = existing_names

    @property
    def name(self) -> str:
        return "NameCollisionResolver"

    async def invoke(self, config: "NewSessionConfig") -> "NewSessionConfig":
        """Return config with unique name."""
        from ..models import NewSessionConfig

        if config.name not in self._existing_names:
            return config

        # Append timestamp
        timestamp = datetime.now().strftime("%H%M%S")
        new_name = f"{config.name}-{timestamp}"

        return NewSessionConfig(
            name=new_name,
            session_type=config.session_type,
            working_dir=config.working_dir,
            command=config.command,
            env=config.env,
            model=config.model,
            api_key_env=config.api_key_env,
        )
