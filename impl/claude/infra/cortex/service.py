"""
Cortex Service - gRPC implementation of the Logos service.

This IS the living system. The CLI is just glass in front of it.
Business logic lives HERE, not in CLI handlers.

The Cortex Servicer implements all RPC methods defined in logos.proto:
- GetStatus: Returns cortex health and agent states
- Invoke: Universal AGENTESE path resolution
- StreamDreams: Bi-directional streaming for dream sessions
- StreamObserve: Server streaming for real-time observation
- GetMap: Returns pre-rendered HoloMap
- Tithe: Entropy discharge

Design Principles:
1. Graceful Degradation: Always return something useful
2. Transparent Infrastructure: Log and trace all operations
3. Generative: Implementation follows proto spec exactly
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator as ABCAsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Protocol, runtime_checkable

# =============================================================================
# Data Classes (Mirror proto messages for non-gRPC mode)
# =============================================================================


@dataclass
class StatusData:
    """
    Status response data structure.

    Mirrors StatusResponse from logos.proto for use in local mode
    (when gRPC is not available).
    """

    health: str = "healthy"
    agents: list[dict[str, Any]] = field(default_factory=list)
    pheromone_levels: dict[str, float] = field(default_factory=dict)
    metabolic_pressure: float = 0.0
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    components: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "health": self.health,
            "agents": self.agents,
            "pheromone_levels": self.pheromone_levels,
            "metabolic_pressure": self.metabolic_pressure,
            "instance_id": self.instance_id,
            "timestamp": self.timestamp,
            "components": self.components,
        }


@dataclass
class InvokeResult:
    """
    Result of an AGENTESE invocation.

    Mirrors InvokeResponse from logos.proto.
    """

    result: Any = None
    result_json: str = ""
    path: str = ""
    lens: str = "optics.identity"
    duration_ms: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    from_cache: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "result": self.result,
            "result_json": self.result_json,
            "metadata": {
                "path": self.path,
                "lens": self.lens,
                "duration_ms": self.duration_ms,
                "tokens_input": self.tokens_input,
                "tokens_output": self.tokens_output,
                "trace_id": self.trace_id,
                "from_cache": self.from_cache,
            },
        }


@dataclass
class TitheResult:
    """
    Result of a tithe (entropy discharge).

    Mirrors TitheResponse from logos.proto.
    """

    success: bool = True
    gratitude_response: str = ""
    remaining_pressure: float = 0.0
    discharged: float = 0.0
    fever_dream: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "gratitude_response": self.gratitude_response,
            "remaining_pressure": self.remaining_pressure,
            "discharged": self.discharged,
            "fever_dream": self.fever_dream,
        }


# =============================================================================
# Protocol Definition (for type checking without gRPC dependency)
# =============================================================================


@runtime_checkable
class LogosServicer(Protocol):
    """
    Protocol definition for Logos service implementation.

    This allows us to define the interface without requiring gRPC.
    Implementations can be:
    1. Full gRPC servicer (when grpcio is available)
    2. Local in-process servicer (for testing or fallback)
    """

    async def GetStatus(self, request: Any, context: Any = None) -> StatusData:
        """Get cortex status."""
        ...

    async def Invoke(self, request: Any, context: Any = None) -> InvokeResult:
        """Invoke an AGENTESE path."""
        ...

    async def Tithe(self, request: Any, context: Any = None) -> TitheResult:
        """Discharge entropy pressure."""
        ...


# =============================================================================
# Cortex Servicer Implementation
# =============================================================================


class CortexServicer:
    """
    gRPC implementation of Logos service.

    This IS the living system. The CLI is just glass in front of it.
    Business logic lives HERE, not in CLI handlers.

    Usage:
        servicer = CortexServicer()

        # Local mode (no gRPC)
        status = await servicer.GetStatus(StatusRequest(verbose=True))

        # gRPC mode (with grpcio)
        server = grpc.aio.server()
        logos_pb2_grpc.add_LogosServicer_to_server(servicer, server)
    """

    def __init__(
        self,
        lifecycle_state: Any = None,
        logos: Any = None,
        metabolism: Any = None,
        pheromone_field: Any = None,
        llm_runtime: Any = None,
    ):
        """
        Initialize the Cortex servicer.

        Args:
            lifecycle_state: LifecycleState from bootstrap
            logos: Logos resolver instance (for AGENTESE paths)
            metabolism: MetabolicEngine instance (for pressure/fever)
            pheromone_field: SemanticField instance (for pheromone levels)
            llm_runtime: LLM runtime for cognitive operations (ClaudeCLIRuntime)
        """
        self._lifecycle_state = lifecycle_state
        self._logos = logos
        self._metabolism = metabolism
        self._pheromone_field = pheromone_field
        self._llm_runtime = llm_runtime
        self._instance_id = str(uuid.uuid4())[:8]

        # Track metabolic pressure internally if no external engine
        self._internal_pressure = 0.0
        self._critical_threshold = 0.8

        # LLM health tracking
        self._llm_healthy: bool | None = None
        self._llm_last_check: datetime | None = None

    async def GetStatus(self, request: Any = None, context: Any = None) -> Any:
        """
        Get cortex status.

        Maps to: self.cortex.manifest
        Always returns something useful (Graceful Degradation).

        Returns protobuf StatusResponse when context is provided (gRPC mode),
        otherwise returns StatusData dataclass (local mode).
        """
        verbose = getattr(request, "verbose", False) if request else False

        # Try to get real status from lifecycle state
        health = "healthy"
        agents: list[dict[str, Any]] = []
        pheromone_levels: dict[str, float] = {}
        metabolic_pressure = 0.0
        components: list[dict[str, Any]] = []

        if self._lifecycle_state is not None:
            # Real implementation with lifecycle state
            try:
                # Use CortexObserver if available for real health data
                cortex_observer = getattr(
                    self._lifecycle_state, "cortex_observer", None
                )
                if cortex_observer is not None:
                    health_snapshot = cortex_observer.get_health()
                    health = health_snapshot.overall.value

                    # Extract agent statuses from snapshot
                    agents = await self._get_agent_statuses_from_snapshot(
                        health_snapshot
                    )

                    # Extract component health from snapshot
                    if verbose:
                        components = self._get_components_from_snapshot(health_snapshot)
                else:
                    # Fallback: check components directly
                    agents = await self._get_agent_statuses()
                    health = "healthy" if agents else "starting"
                    if verbose:
                        components = await self._get_component_health()

                # Check pheromone field
                pheromone_levels = await self._get_pheromone_levels()

                # Check metabolic pressure
                if self._metabolism:
                    metabolic_pressure = self._metabolism.pressure
                else:
                    metabolic_pressure = self._internal_pressure

            except Exception as e:
                health = "degraded"
                components.append(
                    {
                        "name": "status_collection",
                        "healthy": False,
                        "message": str(e),
                    }
                )
        else:
            # Fallback: minimal status when no lifecycle state
            health = "starting"
            components.append(
                {
                    "name": "lifecycle",
                    "healthy": False,
                    "message": "No lifecycle state available",
                }
            )

        # If context is provided, we're in gRPC mode - return protobuf
        if context is not None:
            # In gRPC mode, we MUST return a protobuf. Don't silently fall back.
            from google.protobuf.timestamp_pb2 import Timestamp
            from protocols.proto.generated import (
                AgentStatus,
                ComponentHealth,
                StatusResponse,
            )

            ts = Timestamp()
            ts.GetCurrentTime()

            # Convert agents to protobuf
            agent_protos = [
                AgentStatus(
                    name=a["name"],
                    genus=a.get("genus", "unknown"),
                    status=a.get("status", "unknown"),
                )
                for a in agents
            ]

            # Convert components to protobuf
            component_protos = [
                ComponentHealth(
                    name=c["name"],
                    healthy=c.get("healthy", False),
                    message=c.get("message", ""),
                )
                for c in components
            ]

            return StatusResponse(
                health=health,
                agents=agent_protos,
                pheromone_levels=pheromone_levels,
                metabolic_pressure=metabolic_pressure,
                instance_id=self._instance_id,
                timestamp=ts,
                components=component_protos if verbose else [],
            )

        # Local mode - return dataclass
        return StatusData(
            health=health,
            agents=agents,
            pheromone_levels=pheromone_levels,
            metabolic_pressure=metabolic_pressure,
            instance_id=self._instance_id,
            components=components if verbose else [],
        )

    async def Invoke(self, request: Any = None, context: Any = None) -> InvokeResult:
        """
        Universal AGENTESE invocation endpoint.

        This is the heart of the Logos service: every CLI command
        ultimately resolves to an AGENTESE path invocation.

        Maps to: logos.invoke(path, observer, lens, **kwargs)
        """
        import time

        start_time = time.perf_counter()

        # Extract request parameters
        path = getattr(request, "path", "") if request else ""
        observer_dna = getattr(request, "observer_dna", b"") if request else b""
        lens = (
            getattr(request, "lens", "optics.identity")
            if request
            else "optics.identity"
        )
        kwargs_map = getattr(request, "kwargs", {}) if request else {}

        if not path:
            return InvokeResult(
                result=None,
                result_json=json.dumps({"error": "No path specified"}),
                path=path,
                lens=lens,
            )

        try:
            # Parse kwargs
            kwargs = {}
            for k, v in kwargs_map.items():
                try:
                    kwargs[k] = json.loads(v)
                except json.JSONDecodeError:
                    kwargs[k] = v

            # Invoke through Logos if available
            if self._logos:
                # Full AGENTESE resolution
                result = await self._logos.invoke(
                    path,
                    observer=self._deserialize_observer(observer_dna),
                    lens=lens,
                    **kwargs,
                )
            else:
                # Fallback: handle known paths directly
                result = await self._handle_path_directly(path, kwargs)

            duration_ms = (time.perf_counter() - start_time) * 1000

            return InvokeResult(
                result=result,
                result_json=json.dumps(result, default=str) if result else "",
                path=path,
                lens=lens,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return InvokeResult(
                result=None,
                result_json=json.dumps({"error": str(e)}),
                path=path,
                lens=lens,
                duration_ms=duration_ms,
            )

    async def Tithe(self, request: Any = None, context: Any = None) -> TitheResult:
        """
        Discharge entropy pressure.

        Maps to: void.entropy.tithe
        Part of the Accursed Share - voluntary expenditure.
        """
        amount = getattr(request, "amount", 0.1) if request else 0.1
        gratitude = getattr(request, "gratitude", "") if request else ""

        if self._metabolism is None:
            return TitheResult(
                success=False,
                gratitude_response="No metabolic engine available. Tithe not processed.",
                remaining_pressure=0.0,
                discharged=0.0,
            )

        # Calculate discharge
        current_pressure = self._metabolism.pressure
        discharge_amount = current_pressure * amount

        # Apply discharge
        self._metabolism.pressure -= discharge_amount

        # Generate response
        responses = [
            "The void receives your offering with gratitude.",
            "Pressure released. The system breathes easier.",
            "Your tithe feeds the accursed share.",
            "Order restored through voluntary expenditure.",
        ]
        import random

        response = random.choice(responses)

        if gratitude:
            response += f' "{gratitude}"'

        # Check if we triggered a fever dream
        fever_dream = None
        if current_pressure > self._metabolism.critical_threshold:
            fever_dream = await self._generate_fever_dream()

        return TitheResult(
            success=True,
            gratitude_response=response,
            remaining_pressure=self._metabolism.pressure,
            discharged=discharge_amount,
            fever_dream=fever_dream,
        )

    async def StreamDreams(
        self, request_iterator: Any, context: Any = None
    ) -> AsyncIterator[Any]:
        """
        Bi-directional streaming for interactive dream sessions.

        Maps to: self.memory.consolidate (dream mode)
        """
        # Stub implementation - yields a single response
        from datetime import datetime

        # Import protobuf type if available
        try:
            from protocols.proto.generated import DreamOutput

            yield DreamOutput(
                text="Dream streaming not yet implemented. Use 'kgents dream' for now.",
                awaiting_input=False,
                phase="nrem",
            )
        except ImportError:
            # Fallback for non-protobuf mode
            yield {
                "text": "Dream streaming not yet implemented.",
                "awaiting_input": False,
                "phase": "nrem",
            }

    async def StreamObserve(
        self, request: Any, context: Any = None
    ) -> AsyncIterator[Any]:
        """
        Server streaming for real-time observation.

        Maps to: world.project.observe
        """
        # Stub implementation - yields periodic status events
        from datetime import datetime

        try:
            from google.protobuf.timestamp_pb2 import Timestamp
            from protocols.proto.generated import ObserveEvent

            ts = Timestamp()
            ts.GetCurrentTime()

            yield ObserveEvent(
                event_type="status",
                content=json.dumps({"message": "Observation stream started"}),
                timestamp=ts,
                source="cortex",
                significance=0.5,
            )
        except ImportError:
            yield {
                "event_type": "status",
                "content": {"message": "Observation stream started"},
                "source": "cortex",
                "significance": 0.5,
            }

    async def GetMap(self, request: Any = None, context: Any = None) -> Any:
        """
        Get the HoloMap for the current project.

        Maps to: world.project.manifest (with lens=optics.cartography)
        """
        try:
            from google.protobuf.timestamp_pb2 import Timestamp
            from protocols.proto.generated import (
                HoloMap,
                MapLandmark,
                MapMetadata,
                MapPosition,
            )

            ts = Timestamp()
            ts.GetCurrentTime()

            # Build basic map from lifecycle state
            landmarks = []
            if self._lifecycle_state is not None:
                # Add agents as landmarks
                agents = await self._get_agent_statuses()
                for i, agent in enumerate(agents):
                    landmarks.append(
                        MapLandmark(
                            name=agent["name"],
                            path=f"self.agent.{agent['name']}",
                            significance=0.8,
                            category="agent",
                            position=MapPosition(x=float(i), y=0.0, z=0.0),
                        )
                    )

            return HoloMap(
                landmarks=landmarks,
                desire_lines=[],
                voids=[],
                attractors=[],
                rendered="[Map visualization not yet implemented]",
                metadata=MapMetadata(
                    generated_at=ts,
                    total_files=0,
                    total_landmarks=len(landmarks),
                    resolution="low",
                ),
            )

        except ImportError:
            # Fallback for non-protobuf mode
            return {
                "landmarks": [],
                "desire_lines": [],
                "voids": [],
                "rendered": "[Map visualization not yet implemented]",
            }

    # =========================================================================
    # Helper Methods
    # =========================================================================

    async def _get_agent_statuses(self) -> list[dict[str, Any]]:
        """Get status of all running agents."""
        agents = []

        # Get from lifecycle state's bicameral memory components
        if self._lifecycle_state is not None:
            # Check synapse
            if (
                hasattr(self._lifecycle_state, "synapse")
                and self._lifecycle_state.synapse
            ):
                agents.append(
                    {
                        "name": "synapse",
                        "genus": "d-gent",
                        "status": "running",
                    }
                )

            # Check hippocampus
            if (
                hasattr(self._lifecycle_state, "hippocampus")
                and self._lifecycle_state.hippocampus
            ):
                agents.append(
                    {
                        "name": "hippocampus",
                        "genus": "d-gent",
                        "status": "running",
                    }
                )

            # Check dreamer
            if (
                hasattr(self._lifecycle_state, "dreamer")
                and self._lifecycle_state.dreamer
            ):
                agents.append(
                    {
                        "name": "dreamer",
                        "genus": "d-gent",
                        "status": "running",
                    }
                )

            # Check bicameral
            if (
                hasattr(self._lifecycle_state, "bicameral")
                and self._lifecycle_state.bicameral
            ):
                agents.append(
                    {
                        "name": "bicameral",
                        "genus": "d-gent",
                        "status": "running",
                    }
                )

            # Check cortex observer
            if (
                hasattr(self._lifecycle_state, "cortex_observer")
                and self._lifecycle_state.cortex_observer
            ):
                agents.append(
                    {
                        "name": "cortex_observer",
                        "genus": "o-gent",
                        "status": "running",
                    }
                )

        return agents

    async def _get_agent_statuses_from_snapshot(
        self, health_snapshot: Any
    ) -> list[dict[str, Any]]:
        """
        Extract agent statuses from CortexHealthSnapshot.

        Maps the health snapshot's component statuses to agent info.
        """
        agents = []

        # Map snapshot components to agents
        if health_snapshot.synapse.available:
            status = "running"
            if health_snapshot.synapse.health.value == "degraded":
                status = "degraded"
            elif health_snapshot.synapse.health.value == "critical":
                status = "critical"
            agents.append(
                {
                    "name": "synapse",
                    "genus": "d-gent",
                    "status": status,
                }
            )

        if health_snapshot.hippocampus.available:
            status = "running"
            if health_snapshot.hippocampus.health.value == "degraded":
                status = "degraded"
            agents.append(
                {
                    "name": "hippocampus",
                    "genus": "d-gent",
                    "status": status,
                }
            )

        if health_snapshot.dreamer.available:
            status = "running"
            if health_snapshot.dreamer.health.value == "degraded":
                status = "degraded"
            agents.append(
                {
                    "name": "dreamer",
                    "genus": "d-gent",
                    "status": status,
                    "phase": health_snapshot.dreamer.phase,
                }
            )

        # Always include cortex_observer since we have a snapshot
        agents.append(
            {
                "name": "cortex_observer",
                "genus": "o-gent",
                "status": "running",
            }
        )

        # Check for bicameral from left hemisphere
        if health_snapshot.left_hemisphere.available:
            agents.append(
                {
                    "name": "bicameral_left",
                    "genus": "d-gent",
                    "status": "running"
                    if health_snapshot.left_hemisphere.health.value == "healthy"
                    else "degraded",
                }
            )

        if health_snapshot.right_hemisphere.available:
            agents.append(
                {
                    "name": "bicameral_right",
                    "genus": "d-gent",
                    "status": "running"
                    if health_snapshot.right_hemisphere.health.value == "healthy"
                    else "degraded",
                }
            )

        return agents

    def _get_components_from_snapshot(
        self, health_snapshot: Any
    ) -> list[dict[str, Any]]:
        """
        Extract detailed component health from CortexHealthSnapshot.

        Returns component info for verbose status response.
        """
        components = []

        # Left Hemisphere (relational store)
        left = health_snapshot.left_hemisphere
        components.append(
            {
                "name": "left_hemisphere",
                "healthy": left.available and left.health.value == "healthy",
                "message": f"latency={left.latency_ms:.1f}ms, errors={left.errors_total}"
                if left.available
                else "Not available",
            }
        )

        # Right Hemisphere (vector store)
        right = health_snapshot.right_hemisphere
        components.append(
            {
                "name": "right_hemisphere",
                "healthy": right.available and right.health.value != "critical",
                "message": f"vectors={right.vectors_count}, latency={right.latency_ms:.1f}ms"
                if right.available
                else "Not available",
            }
        )

        # Coherency
        coherency = health_snapshot.coherency
        components.append(
            {
                "name": "coherency",
                "healthy": coherency.health.value == "healthy",
                "message": f"rate={coherency.coherency_rate:.2%}, ghosts={coherency.ghost_count}",
            }
        )

        # Synapse
        synapse = health_snapshot.synapse
        components.append(
            {
                "name": "synapse",
                "healthy": synapse.available and synapse.health.value == "healthy",
                "message": f"surprise={synapse.surprise_avg:.2f}, signals={synapse.signals_total}"
                if synapse.available
                else "Not available",
            }
        )

        # Hippocampus
        hippo = health_snapshot.hippocampus
        components.append(
            {
                "name": "hippocampus",
                "healthy": hippo.available and hippo.health.value == "healthy",
                "message": f"size={hippo.memory_count}/{hippo.max_size}, util={hippo.utilization:.1%}"
                if hippo.available
                else "Not available",
            }
        )

        # Dreamer
        dreamer = health_snapshot.dreamer
        components.append(
            {
                "name": "dreamer",
                "healthy": dreamer.available,
                "message": f"phase={dreamer.phase}, cycles={dreamer.dream_cycles_total}"
                if dreamer.available
                else "Not available",
            }
        )

        # Add lifecycle and storage
        components.append(
            {
                "name": "lifecycle",
                "healthy": True,
                "message": "OK",
            }
        )

        if (
            hasattr(self._lifecycle_state, "storage_provider")
            and self._lifecycle_state.storage_provider
        ):
            components.append(
                {
                    "name": "storage",
                    "healthy": True,
                    "message": "OK",
                }
            )

        return components

    async def _get_pheromone_levels(self) -> dict[str, float]:
        """Get pheromone field summary."""
        levels: dict[str, float] = {}

        # Try the explicit pheromone field first
        if self._pheromone_field is not None:
            if hasattr(self._pheromone_field, "get_type_totals"):
                levels = self._pheromone_field.get_type_totals()
            elif hasattr(self._pheromone_field, "pheromones"):
                # Fallback for FieldState from i-gent
                for p in self._pheromone_field.pheromones:
                    ptype = p.ptype.value if hasattr(p.ptype, "value") else str(p.ptype)
                    levels[ptype] = levels.get(ptype, 0) + p.intensity
            return levels

        # Try to get from lifecycle state
        if self._lifecycle_state is not None:
            if hasattr(self._lifecycle_state, "pheromone_field"):
                field = self._lifecycle_state.pheromone_field
                if field is not None:
                    if hasattr(field, "get_type_totals"):
                        levels = field.get_type_totals()
                    elif hasattr(field, "pheromones"):
                        for p in field.pheromones:
                            ptype = (
                                p.ptype.value
                                if hasattr(p.ptype, "value")
                                else str(p.ptype)
                            )
                            levels[ptype] = levels.get(ptype, 0) + p.intensity

        return levels

    async def _get_component_health(self) -> list[dict[str, Any]]:
        """Get detailed component health status."""
        components = []

        # Check standard components
        checks = [
            ("lifecycle", self._lifecycle_state is not None),
            ("logos", self._logos is not None),
            ("metabolism", self._metabolism is not None),
        ]

        for name, healthy in checks:
            components.append(
                {
                    "name": name,
                    "healthy": healthy,
                    "message": "OK" if healthy else "Not initialized",
                }
            )

        # Check bicameral components from lifecycle state
        if self._lifecycle_state is not None:
            bicameral_checks = [
                ("synapse", getattr(self._lifecycle_state, "synapse", None)),
                ("hippocampus", getattr(self._lifecycle_state, "hippocampus", None)),
                ("dreamer", getattr(self._lifecycle_state, "dreamer", None)),
                ("bicameral", getattr(self._lifecycle_state, "bicameral", None)),
                (
                    "cortex_observer",
                    getattr(self._lifecycle_state, "cortex_observer", None),
                ),
                ("storage", getattr(self._lifecycle_state, "storage_provider", None)),
            ]

            for name, component in bicameral_checks:
                healthy = component is not None
                components.append(
                    {
                        "name": name,
                        "healthy": healthy,
                        "message": "OK" if healthy else "Not available",
                    }
                )

            # Check operation mode
            mode = getattr(self._lifecycle_state, "mode", None)
            if mode:
                components.append(
                    {
                        "name": "operation_mode",
                        "healthy": True,
                        "message": str(mode.value)
                        if hasattr(mode, "value")
                        else str(mode),
                    }
                )

        return components

    def _deserialize_observer(self, observer_dna: bytes) -> Any:
        """Deserialize observer from protobuf bytes."""
        if not observer_dna:
            return None

        # TODO: Implement proper Umwelt deserialization
        # For now, return None (uses default observer)
        return None

    async def _handle_path_directly(self, path: str, kwargs: dict[str, Any]) -> Any:
        """
        Handle known AGENTESE paths directly without full Logos.

        This is a fallback for when the Logos resolver isn't available.
        Routes cognitive paths to LLM runtime when available.
        """
        # Parse path components
        parts = path.split(".")
        if len(parts) < 2:
            return {"error": f"Invalid path: {path}"}

        context = parts[0]
        entity = parts[1]
        aspect = parts[2] if len(parts) > 2 else "manifest"

        # Handle known paths
        if context == "self":
            if entity == "cortex" and aspect == "manifest":
                # self.cortex.manifest -> GetStatus
                status = await self.GetStatus()
                return status.to_dict()

            if entity == "cortex" and aspect == "probe":
                # self.cortex.probe -> Run cognitive probe
                return await self._run_cognitive_probe()

        elif context == "void":
            if entity == "entropy" and aspect == "tithe":
                # void.entropy.tithe -> Tithe
                result = await self.Tithe()
                return result.to_dict()

        elif context == "concept":
            # Cognitive paths - require LLM runtime
            if self._llm_runtime is None:
                return {
                    "error": f"LLM runtime required for path: {path}",
                    "suggestion": "Configure CortexServicer with llm_runtime parameter",
                }

            if entity == "define":
                # concept.define -> Define a term using LLM
                term = kwargs.get("term", "")
                return await self._invoke_llm_path("concept.define", term=term)

            if entity == "blend" and aspect == "forge":
                # concept.blend.forge -> Blend concepts
                concepts = kwargs.get("concepts", [])
                return await self._invoke_llm_path(
                    "concept.blend.forge", concepts=concepts
                )

            if entity == "refine":
                # concept.refine -> Dialectical refinement
                statement = kwargs.get("statement", "")
                return await self._invoke_llm_path("concept.refine", statement=statement)

        # Unknown path
        return {
            "error": f"Unknown path: {path}",
            "suggestion": "Available paths: self.cortex.manifest, self.cortex.probe, "
            "void.entropy.tithe, concept.define, concept.blend.forge, concept.refine",
        }

    async def _run_cognitive_probe(self) -> dict[str, Any]:
        """Run cognitive probe against LLM runtime."""
        if self._llm_runtime is None:
            return {
                "healthy": False,
                "message": "No LLM runtime configured",
                "status": "unavailable",
            }

        try:
            from .probes import CognitiveProbe

            probe = CognitiveProbe()
            result = await probe.check(self._llm_runtime)

            # Update cached health status
            self._llm_healthy = result.healthy
            self._llm_last_check = datetime.now()

            return result.to_dict()
        except Exception as e:
            return {
                "healthy": False,
                "message": str(e),
                "status": "error",
            }

    async def _invoke_llm_path(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """
        Invoke an LLM-backed AGENTESE path.

        Uses the configured LLM runtime to execute cognitive operations.
        """
        if self._llm_runtime is None:
            return {"error": "No LLM runtime configured"}

        from runtime.base import AgentContext

        # Build prompt based on path
        if path == "concept.define":
            term = kwargs.get("term", "")
            context = AgentContext(
                system_prompt=(
                    "You are a precise definition engine. "
                    "Provide a clear, concise definition."
                ),
                messages=[
                    {
                        "role": "user",
                        "content": f"Define the term: {term}\n\n"
                        "Respond with a JSON object containing:\n"
                        '{"term": "<term>", "definition": "<definition>", '
                        '"examples": ["<example1>", "<example2>"]}',
                    }
                ],
                temperature=0.3,
                max_tokens=500,
            )

        elif path == "concept.blend.forge":
            concepts = kwargs.get("concepts", [])
            context = AgentContext(
                system_prompt=(
                    "You are a concept blending engine. "
                    "Create novel concepts by blending input concepts."
                ),
                messages=[
                    {
                        "role": "user",
                        "content": f"Blend these concepts: {concepts}\n\n"
                        "Respond with a JSON object containing:\n"
                        '{"blend": "<blended_concept>", '
                        '"rationale": "<why_this_blend>", '
                        '"novel_properties": ["<property1>", "<property2>"]}',
                    }
                ],
                temperature=0.7,
                max_tokens=500,
            )

        elif path == "concept.refine":
            statement = kwargs.get("statement", "")
            context = AgentContext(
                system_prompt=(
                    "You are a dialectical refinement engine. "
                    "Challenge and improve statements through critique."
                ),
                messages=[
                    {
                        "role": "user",
                        "content": f"Refine this statement: {statement}\n\n"
                        "Respond with a JSON object containing:\n"
                        '{"original": "<original>", '
                        '"critique": "<constructive_critique>", '
                        '"refined": "<improved_statement>"}',
                    }
                ],
                temperature=0.5,
                max_tokens=500,
            )

        else:
            return {"error": f"Unknown LLM path: {path}"}

        try:
            response_text, metadata = await self._llm_runtime.raw_completion(context)

            # Try to parse as JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                result = {"raw_response": response_text}

            return {
                "path": path,
                "result": result,
                "model": metadata.get("model", "unknown"),
                "usage": metadata.get("usage", {}),
            }

        except Exception as e:
            return {
                "path": path,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    async def _generate_fever_dream(self) -> str:
        """
        Generate a fever dream from current context.

        This is the "hallucination as feature" pattern from the spec.
        """
        dreams = [
            "In the overflow, clarity emerges sideways.",
            "The pressure reveals what was hidden in the noise.",
            "Sometimes the accursed share speaks louder than intention.",
            "A tangent that returns home by unexpected paths.",
            "The fever breaks into unexpected insight.",
        ]
        import random

        return random.choice(dreams)


# =============================================================================
# Factory Function
# =============================================================================


def create_cortex_servicer(
    lifecycle_state: Any = None,
    logos: Any = None,
    metabolism: Any = None,
    pheromone_field: Any = None,
    llm_runtime: Any = None,
    use_cli_runtime: bool = False,
) -> CortexServicer:
    """
    Factory function for creating a configured Cortex servicer.

    Usage:
        # Basic servicer (for testing)
        servicer = create_cortex_servicer()

        # With lifecycle state
        servicer = create_cortex_servicer(lifecycle_state=state)

        # With LLM runtime for cognitive paths
        servicer = create_cortex_servicer(use_cli_runtime=True)

        # Full configuration
        servicer = create_cortex_servicer(
            lifecycle_state=state,
            logos=logos_instance,
            metabolism=metabolic_engine,
            pheromone_field=field_state,
            llm_runtime=custom_runtime,
        )

    Args:
        lifecycle_state: LifecycleState from bootstrap (provides bicameral stack)
        logos: Logos resolver instance (for AGENTESE paths)
        metabolism: MetabolicEngine instance (for pressure/fever)
        pheromone_field: SemanticField or FieldState (for pheromone levels)
        llm_runtime: LLM runtime for cognitive operations
        use_cli_runtime: If True, auto-create ClaudeCLIRuntime (requires Claude CLI)
    """
    # Auto-create CLI runtime if requested
    if llm_runtime is None and use_cli_runtime:
        try:
            from runtime.cli import ClaudeCLIRuntime

            llm_runtime = ClaudeCLIRuntime(timeout=60.0, max_retries=2)
        except (ImportError, RuntimeError) as e:
            # CLI not available - log warning but continue
            import sys

            print(f"[cortex] Warning: Could not create CLI runtime: {e}", file=sys.stderr)

    return CortexServicer(
        lifecycle_state=lifecycle_state,
        logos=logos,
        metabolism=metabolism,
        pheromone_field=pheromone_field,
        llm_runtime=llm_runtime,
    )
