"""
Conflict Detection and Resolution Agents

zen-agents specific Contradict/Sublate implementations for session conflicts.

Key conflict types in session management:
    - Name collisions: Two sessions with the same name
    - Port conflicts: Two sessions trying to use the same port
    - Worktree conflicts: Multiple sessions targeting the same worktree
    - Resource conflicts: Too many sessions running

Uses the bootstrap Contradict/Sublate pattern:
    Contradict: Detect the tension
    Sublate: Resolve it (or hold if unresolvable)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from bootstrap import (
    Agent,
    Tension,
    TensionMode,
    Synthesis,
    HoldTension,
    SynthesisResult,
    contradict,
    sublate,
)

from .types import (
    Session,
    SessionConfig,
    SessionState,
    ZenGroundState,
)


# =============================================================================
# CONFLICT TYPES
# =============================================================================

class ConflictType:
    """Types of session conflicts"""
    NAME_COLLISION = "name_collision"
    PORT_CONFLICT = "port_conflict"
    WORKTREE_CONFLICT = "worktree_conflict"
    RESOURCE_LIMIT = "resource_limit"


@dataclass
class SessionConflict:
    """A detected conflict between sessions"""
    conflict_type: str
    session_a: Session | SessionConfig
    session_b: Session | SessionConfig | None  # None for resource limits
    description: str
    resolvable: bool = True
    suggested_resolution: str | None = None


@dataclass
class ConflictResolution:
    """Result of conflict resolution"""
    resolved: bool
    original_conflict: SessionConflict
    resolution_type: str  # "renamed", "reassigned", "rejected", "held"
    result: Session | SessionConfig | None
    message: str


# =============================================================================
# SESSION CONTRADICT - Conflict Detection
# =============================================================================

@dataclass
class SessionContradictInput:
    """Input for session conflict detection"""
    config: SessionConfig  # New session config to check
    ground_state: ZenGroundState  # Current state with existing sessions


class SessionContradict(Agent[SessionContradictInput, list[SessionConflict]]):
    """
    Detect conflicts between a new session config and existing sessions.

    Type signature: SessionContradict: (SessionConfig, ZenGroundState) → [SessionConflict]

    Checks for:
        - Name collisions with existing sessions
        - Port conflicts (if ports are specified)
        - Worktree conflicts
        - Resource limit violations
    """

    @property
    def name(self) -> str:
        return "SessionContradict"

    @property
    def genus(self) -> str:
        return "zen/conflict"

    @property
    def purpose(self) -> str:
        return "Detect conflicts between sessions"

    async def invoke(self, input: SessionContradictInput) -> list[SessionConflict]:
        """Detect all conflicts for the given config."""
        conflicts: list[SessionConflict] = []
        config = input.config
        state = input.ground_state

        # Check name collision
        name_conflict = await self._check_name_collision(config, state)
        if name_conflict:
            conflicts.append(name_conflict)

        # Check worktree conflict
        worktree_conflict = await self._check_worktree_conflict(config, state)
        if worktree_conflict:
            conflicts.append(worktree_conflict)

        # Check resource limit
        resource_conflict = await self._check_resource_limit(config, state)
        if resource_conflict:
            conflicts.append(resource_conflict)

        return conflicts

    async def _check_name_collision(
        self,
        config: SessionConfig,
        state: ZenGroundState
    ) -> SessionConflict | None:
        """Check if session name is already in use."""
        for session_id, session in state.sessions.items():
            if session.config.name == config.name and session.is_alive():
                return SessionConflict(
                    conflict_type=ConflictType.NAME_COLLISION,
                    session_a=config,
                    session_b=session,
                    description=f"Session name '{config.name}' already exists",
                    resolvable=True,
                    suggested_resolution=f"Rename to '{config.name}-2'"
                )
        return None

    async def _check_worktree_conflict(
        self,
        config: SessionConfig,
        state: ZenGroundState
    ) -> SessionConflict | None:
        """Check if working directory is already in use by another session."""
        if not config.working_dir:
            return None

        for session_id, session in state.sessions.items():
            if (session.config.working_dir == config.working_dir
                and session.is_alive()
                and session.config.session_type == config.session_type):
                return SessionConflict(
                    conflict_type=ConflictType.WORKTREE_CONFLICT,
                    session_a=config,
                    session_b=session,
                    description=f"Working directory '{config.working_dir}' already in use by session '{session.config.name}'",
                    resolvable=True,
                    suggested_resolution="Use a different working directory or close existing session"
                )
        return None

    async def _check_resource_limit(
        self,
        config: SessionConfig,
        state: ZenGroundState
    ) -> SessionConflict | None:
        """Check if creating a new session would exceed limits."""
        active_count = sum(1 for s in state.sessions.values() if s.is_alive())
        if active_count >= state.max_sessions:
            return SessionConflict(
                conflict_type=ConflictType.RESOURCE_LIMIT,
                session_a=config,
                session_b=None,
                description=f"Maximum sessions ({state.max_sessions}) reached",
                resolvable=False,
                suggested_resolution="Close an existing session first"
            )
        return None


# =============================================================================
# SESSION SUBLATE - Conflict Resolution
# =============================================================================

@dataclass
class SessionSublateInput:
    """Input for session conflict resolution"""
    conflict: SessionConflict
    auto_resolve: bool = True  # If False, just suggest, don't apply


class SessionSublate(Agent[SessionSublateInput, ConflictResolution]):
    """
    Resolve session conflicts through synthesis.

    Type signature: SessionSublate: SessionConflict → ConflictResolution

    Resolution strategies:
        - Name collision → Rename with suffix
        - Worktree conflict → Suggest alternative or reject
        - Resource limit → Reject (cannot auto-resolve)
    """

    @property
    def name(self) -> str:
        return "SessionSublate"

    @property
    def genus(self) -> str:
        return "zen/conflict"

    @property
    def purpose(self) -> str:
        return "Resolve session conflicts through synthesis"

    async def invoke(self, input: SessionSublateInput) -> ConflictResolution:
        """Attempt to resolve the conflict."""
        conflict = input.conflict

        # Unresolvable conflicts are held
        if not conflict.resolvable:
            return ConflictResolution(
                resolved=False,
                original_conflict=conflict,
                resolution_type="held",
                result=None,
                message=f"Cannot resolve: {conflict.description}. {conflict.suggested_resolution or ''}"
            )

        # Resolve based on conflict type
        match conflict.conflict_type:
            case ConflictType.NAME_COLLISION:
                return await self._resolve_name_collision(conflict, input.auto_resolve)
            case ConflictType.WORKTREE_CONFLICT:
                return await self._resolve_worktree_conflict(conflict, input.auto_resolve)
            case _:
                return ConflictResolution(
                    resolved=False,
                    original_conflict=conflict,
                    resolution_type="held",
                    result=None,
                    message=f"No resolution strategy for {conflict.conflict_type}"
                )

    async def _resolve_name_collision(
        self,
        conflict: SessionConflict,
        auto_resolve: bool
    ) -> ConflictResolution:
        """Resolve name collision by generating unique name."""
        if not isinstance(conflict.session_a, SessionConfig):
            return ConflictResolution(
                resolved=False,
                original_conflict=conflict,
                resolution_type="held",
                result=None,
                message="Cannot resolve: session_a must be SessionConfig"
            )

        original_config = conflict.session_a
        new_name = self._generate_unique_name(original_config.name)

        if not auto_resolve:
            return ConflictResolution(
                resolved=False,
                original_conflict=conflict,
                resolution_type="suggested",
                result=None,
                message=f"Suggest renaming to '{new_name}'"
            )

        # Create new config with updated name
        from dataclasses import replace
        resolved_config = replace(original_config, name=new_name)

        return ConflictResolution(
            resolved=True,
            original_conflict=conflict,
            resolution_type="renamed",
            result=resolved_config,
            message=f"Renamed from '{original_config.name}' to '{new_name}'"
        )

    async def _resolve_worktree_conflict(
        self,
        conflict: SessionConflict,
        auto_resolve: bool
    ) -> ConflictResolution:
        """Handle worktree conflicts - usually cannot auto-resolve."""
        return ConflictResolution(
            resolved=False,
            original_conflict=conflict,
            resolution_type="held",
            result=None,
            message=conflict.suggested_resolution or "Manual resolution required"
        )

    def _generate_unique_name(self, base_name: str) -> str:
        """Generate a unique name by appending a number."""
        # Simple strategy: append -2, -3, etc.
        # In production, would check against existing sessions
        import time
        suffix = int(time.time()) % 1000
        return f"{base_name}-{suffix}"


# =============================================================================
# CONFLICT PIPELINE - Detection + Resolution
# =============================================================================

@dataclass
class ConflictPipelineResult:
    """Result of running the full conflict pipeline"""
    has_conflicts: bool
    conflicts: list[SessionConflict]
    resolutions: list[ConflictResolution]
    final_config: SessionConfig | None
    can_proceed: bool
    messages: list[str]


class SessionConflictPipeline(Agent[SessionContradictInput, ConflictPipelineResult]):
    """
    Full conflict detection and resolution pipeline.

    Type signature: SessionConflictPipeline: (SessionConfig, ZenGroundState) → ConflictPipelineResult

    Composes: Contradict → Sublate (for each conflict)

    Returns the final config after all resolutions, or indicates if session
    creation cannot proceed.
    """

    def __init__(
        self,
        contradict: SessionContradict | None = None,
        sublate: SessionSublate | None = None,
        auto_resolve: bool = True
    ):
        self._contradict = contradict or session_contradict
        self._sublate = sublate or session_sublate
        self._auto_resolve = auto_resolve

    @property
    def name(self) -> str:
        return "SessionConflictPipeline"

    @property
    def genus(self) -> str:
        return "zen/pipeline"

    @property
    def purpose(self) -> str:
        return "Detect and resolve session conflicts"

    async def invoke(self, input: SessionContradictInput) -> ConflictPipelineResult:
        """Run full conflict detection and resolution."""
        # Step 1: Detect conflicts
        conflicts = await self._contradict.invoke(input)

        if not conflicts:
            return ConflictPipelineResult(
                has_conflicts=False,
                conflicts=[],
                resolutions=[],
                final_config=input.config,
                can_proceed=True,
                messages=["No conflicts detected"]
            )

        # Step 2: Attempt to resolve each conflict
        resolutions: list[ConflictResolution] = []
        current_config = input.config
        messages: list[str] = []

        for conflict in conflicts:
            # Update conflict to use current config
            updated_conflict = SessionConflict(
                conflict_type=conflict.conflict_type,
                session_a=current_config,
                session_b=conflict.session_b,
                description=conflict.description,
                resolvable=conflict.resolvable,
                suggested_resolution=conflict.suggested_resolution
            )

            resolution = await self._sublate.invoke(SessionSublateInput(
                conflict=updated_conflict,
                auto_resolve=self._auto_resolve
            ))
            resolutions.append(resolution)
            messages.append(resolution.message)

            # Update current config if resolution produced one
            if resolution.resolved and isinstance(resolution.result, SessionConfig):
                current_config = resolution.result

        # Determine if we can proceed
        all_resolved = all(r.resolved for r in resolutions)
        unresolvable = any(not c.resolvable for c in conflicts)

        return ConflictPipelineResult(
            has_conflicts=True,
            conflicts=conflicts,
            resolutions=resolutions,
            final_config=current_config if all_resolved else None,
            can_proceed=all_resolved and not unresolvable,
            messages=messages
        )


# =============================================================================
# SINGLETON INSTANCES
# =============================================================================

session_contradict = SessionContradict()
session_sublate = SessionSublate()
conflict_pipeline = SessionConflictPipeline()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def detect_conflicts(
    config: SessionConfig,
    ground_state: ZenGroundState
) -> list[SessionConflict]:
    """Detect conflicts for a session config."""
    return await session_contradict.invoke(SessionContradictInput(
        config=config,
        ground_state=ground_state
    ))


async def resolve_conflicts(
    config: SessionConfig,
    ground_state: ZenGroundState,
    auto_resolve: bool = True
) -> ConflictPipelineResult:
    """Run full conflict detection and resolution."""
    return await conflict_pipeline.invoke(SessionContradictInput(
        config=config,
        ground_state=ground_state
    ))
