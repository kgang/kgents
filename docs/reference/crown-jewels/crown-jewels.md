# Crown Jewels

> *The showcase features of kgents.*

---

## services.brain.__init__

## __init__

```python
module __init__
```

Brain Crown Jewel: Spatial Cathedral of Memory.

---

## services.brain.contracts

## contracts

```python
module contracts
```

Brain AGENTESE Contract Definitions.

---

## BrainManifestResponse

```python
class BrainManifestResponse
```

Brain health status manifest response.

---

## CaptureRequest

```python
class CaptureRequest
```

Request to capture content to holographic memory.

---

## CaptureResponse

```python
class CaptureResponse
```

Response after capturing content.

---

## SearchRequest

```python
class SearchRequest
```

Request for semantic search.

---

## SearchResultItem

```python
class SearchResultItem
```

Single search result item.

---

## SearchResponse

```python
class SearchResponse
```

Response for semantic search.

---

## SurfaceRequest

```python
class SurfaceRequest
```

Request for serendipitous surface from the void.

---

## SurfaceItem

```python
class SurfaceItem
```

Surfaced crystal item.

---

## SurfaceResponse

```python
class SurfaceResponse
```

Response for surface operation.

---

## GetRequest

```python
class GetRequest
```

Request to get specific crystal by ID.

---

## GetResponse

```python
class GetResponse
```

Response for get crystal operation.

---

## RecentRequest

```python
class RecentRequest
```

Request for recent crystals.

---

## ByTagRequest

```python
class ByTagRequest
```

Request for crystals by tag.

---

## DeleteRequest

```python
class DeleteRequest
```

Request to delete a crystal.

---

## DeleteResponse

```python
class DeleteResponse
```

Response after deleting a crystal.

---

## HealResponse

```python
class HealResponse
```

Response after healing ghost memories.

---

## TopologyNode

```python
class TopologyNode
```

A node in the brain topology.

---

## TopologyEdge

```python
class TopologyEdge
```

An edge between topology nodes.

---

## TopologyStats

```python
class TopologyStats
```

Statistics for brain topology.

---

## TopologyRequest

```python
class TopologyRequest
```

Request for brain topology.

---

## TopologyResponse

```python
class TopologyResponse
```

Response for brain topology visualization.

---

## services.brain.node

## node

```python
module node
```

Brain AGENTESE Node: @node("self.memory")

---

## BrainManifestRendering

```python
class BrainManifestRendering
```

Rendering for brain status manifest.

---

## CaptureRendering

```python
class CaptureRendering
```

Rendering for capture result.

---

## SearchRendering

```python
class SearchRendering
```

Rendering for search results.

---

## BrainNode

```python
class BrainNode(BaseLogosNode)
```

AGENTESE node for Brain Crown Jewel.

---

## __init__

```python
def __init__(self, brain_persistence: BrainPersistence) -> None
```

Initialize BrainNode.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `self.memory.manifest`

Manifest brain status to observer.

---

## services.brain.persistence

## persistence

```python
module persistence
```

Brain Persistence: TableAdapter + D-gent integration for Brain Crown Jewel.

### Things to Know

🚨 **Critical:** Dual-track storage means Crystal table AND D-gent must both succeed. If one fails after the other succeeds, you get "ghost" memories.
  - *Verified in: `test_brain_persistence.py::test_heal_ghosts`*

🚨 **Critical:** capture() returns immediately but trace recording is fire-and-forget. Never await the trace task or you'll block the hot path.
  - *Verified in: `test_brain_persistence.py::test_capture_performance`*

ℹ️ search() updates access_count via touch(). High-frequency searches will cause write amplification. Consider batching access updates.
  - *Verified in: `test_brain_persistence.py::test_access_tracking`*

---

## CaptureResult

```python
class CaptureResult
```

Result of a capture operation.

---

## SearchResult

```python
class SearchResult
```

Result of a search operation.

---

## BrainStatus

```python
class BrainStatus
```

Brain health status.

---

## BrainPersistence

```python
class BrainPersistence
```

Persistence layer for Brain Crown Jewel.

---

## capture

```python
async def capture(self, content: str, tags: list[str] | None=None, source_type: str='capture', source_ref: str | None=None, metadata: dict[str, Any] | None=None) -> CaptureResult
```

**AGENTESE:** `self.memory.capture`

Capture content to holographic memory.

---

## search

```python
async def search(self, query: str, limit: int=10, tags: list[str] | None=None) -> list[SearchResult]
```

**AGENTESE:** `self.memory.ghost.surface`

Semantic search for similar memories.

---

## surface

```python
async def surface(self, context: str | None=None, entropy: float=0.7) -> SearchResult | None
```

**AGENTESE:** `void.memory.surface`

Surface a serendipitous memory from the void.

---

## manifest

```python
async def manifest(self) -> BrainStatus
```

**AGENTESE:** `self.memory.manifest`

Get brain health status.

---

## get_by_id

```python
async def get_by_id(self, crystal_id: str) -> SearchResult | None
```

Get a specific crystal by ID.

---

## list_recent

```python
async def list_recent(self, limit: int=10) -> list[SearchResult]
```

List recent crystals.

---

## list_by_tag

```python
async def list_by_tag(self, tag: str, limit: int=10) -> list[SearchResult]
```

List crystals with a specific tag.

---

## delete

```python
async def delete(self, crystal_id: str) -> bool
```

Delete a crystal and its D-gent datum.

---

## heal_ghosts

```python
async def heal_ghosts(self) -> int
```

Heal ghost memories (crystals without D-gent datums).

---

## services.conductor.__init__

## __init__

```python
module __init__
```

**AGENTESE:** `self.conductor.`

Conductor Crown Jewel: Session orchestration for CLI v7.

---

## services.conductor.a2a

## a2a

```python
module a2a
```

A2A Protocol: Agent-to-Agent messaging via SynergyBus.

---

## A2AMessageType

```python
class A2AMessageType(Enum)
```

Types of agent-to-agent messages.

---

## A2AMessage

```python
class A2AMessage
```

Message between agents.

---

## A2ATopics

```python
class A2ATopics
```

Topic namespace for A2A events on WitnessSynergyBus.

---

## A2AChannel

```python
class A2AChannel
```

Agent-to-agent communication channel.

---

## A2ARegistry

```python
class A2ARegistry
```

Registry of active A2A channels.

---

## get_a2a_registry

```python
def get_a2a_registry() -> A2ARegistry
```

Get the global A2A registry.

---

## reset_a2a_registry

```python
def reset_a2a_registry() -> None
```

Reset the global A2A registry (for testing).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for transmission.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> 'A2AMessage'
```

Deserialize from transmission.

---

## create_response

```python
def create_response(self, payload: dict[str, Any]) -> 'A2AMessage'
```

Create a response to this message.

---

## for_type

```python
def for_type(cls, message_type: A2AMessageType) -> str
```

Get topic for message type.

---

## __init__

```python
def __init__(self, agent_id: str)
```

Create a channel for an agent.

---

## send

```python
async def send(self, message: A2AMessage) -> None
```

Send a message to another agent.

---

## request

```python
async def request(self, to_agent: str, payload: dict[str, Any], timeout: float=30.0) -> A2AMessage
```

Request/response pattern with timeout.

---

## respond

```python
async def respond(self, request: A2AMessage, payload: dict[str, Any]) -> None
```

Respond to a request.

---

## handoff

```python
async def handoff(self, to_agent: str, context: dict[str, Any], conversation: list[dict[str, Any]] | None=None) -> None
```

Hand off work to another agent with full context.

---

## notify

```python
async def notify(self, to_agent: str, payload: dict[str, Any]) -> None
```

Send a notification (no response expected).

---

## broadcast

```python
async def broadcast(self, payload: dict[str, Any]) -> None
```

Broadcast to all agents.

---

## heartbeat

```python
async def heartbeat(self) -> None
```

Send a heartbeat signal.

---

## start_subscription

```python
def start_subscription(self) -> None
```

Start subscribing to A2A messages for this agent.

---

## stop_subscription

```python
def stop_subscription(self) -> None
```

Stop subscribing to A2A messages.

---

## subscribe

```python
async def subscribe(self) -> AsyncIterator[A2AMessage]
```

Subscribe to messages addressed to this agent.

---

## receive_one

```python
async def receive_one(self, timeout: float=30.0) -> A2AMessage | None
```

Receive a single message with timeout.

---

## register

```python
def register(self, channel: A2AChannel) -> None
```

Register a channel.

---

## unregister

```python
def unregister(self, agent_id: str) -> None
```

Unregister a channel.

---

## get

```python
def get(self, agent_id: str) -> A2AChannel | None
```

Get a channel by agent ID.

---

## list_agents

```python
def list_agents(self) -> list[str]
```

List all registered agent IDs.

---

## clear

```python
def clear(self) -> None
```

Clear all channels (for testing).

---

## handler

```python
async def handler(topic: str, event: Any) -> None
```

Handle incoming A2A messages.

---

## services.conductor.behaviors

## behaviors

```python
module behaviors
```

Cursor Behaviors: Personality-driven agent movement patterns.

---

## CursorBehavior

```python
class CursorBehavior(Enum)
```

Agent cursor behavior patterns with rich personality.

---

## Position

```python
class Position
```

2D position for canvas rendering.

---

## FocusPoint

```python
class FocusPoint
```

A point of focus in the AGENTESE graph.

---

## HumanFocusTracker

```python
class HumanFocusTracker
```

Tracks human focus for behavior integration.

---

## AGENTESEGraph

```python
class AGENTESEGraph(Protocol)
```

Protocol for AGENTESE graph navigation.

---

## BehaviorAnimator

```python
class BehaviorAnimator
```

Animates agent cursor with behavior-driven movement.

---

## BehaviorModulator

```python
class BehaviorModulator
```

Modulates behavior based on context.

---

## emoji

```python
def emoji(self) -> str
```

Visual indicator reflecting personality.

---

## description

```python
def description(self) -> str
```

Human-readable personality description.

---

## follow_strength

```python
def follow_strength(self) -> float
```

How strongly this behavior tracks human focus (0.0-1.0).

---

## exploration_tendency

```python
def exploration_tendency(self) -> float
```

How likely to explore adjacent nodes (0.0-1.0).

---

## suggestion_probability

```python
def suggestion_probability(self) -> float
```

Probability of making a suggestion per second (0.0-1.0).

---

## movement_smoothness

```python
def movement_smoothness(self) -> float
```

How smooth the movement interpolation is (0.0-1.0).

---

## preferred_states

```python
def preferred_states(self) -> frozenset[CursorState]
```

States this behavior tends toward.

---

## circadian_sensitivity

```python
def circadian_sensitivity(self) -> float
```

How much circadian phase affects behavior (0.0-1.0).

---

## describe_for_phase

```python
def describe_for_phase(self, phase: CircadianPhase) -> str
```

Get behavior description modulated by circadian phase.

---

## distance_to

```python
def distance_to(self, other: 'Position') -> float
```

Euclidean distance.

---

## lerp

```python
def lerp(self, target: 'Position', t: float) -> 'Position'
```

Linear interpolation toward target.

---

## age_seconds

```python
def age_seconds(self) -> float
```

Time since this focus was set.

---

## current

```python
def current(self) -> FocusPoint | None
```

Most recent focus point.

---

## velocity

```python
def velocity(self) -> Position
```

Estimated velocity of focus movement.

---

## is_stationary

```python
def is_stationary(self) -> bool
```

True if focus hasn't moved recently.

---

## focus_duration

```python
def focus_duration(self) -> float
```

How long focus has been on current path.

---

## update

```python
def update(self, path: str, position: Position) -> None
```

Record new focus point.

---

## get_recent_paths

```python
def get_recent_paths(self, seconds: float=30.0) -> list[str]
```

Get unique paths visited in the last N seconds.

---

## get_connected_paths

```python
def get_connected_paths(self, path: str) -> list[str]
```

Get paths directly connected to this path.

---

## get_position

```python
def get_position(self, path: str) -> Position | None
```

Get canvas position for a path.

---

## get_all_paths

```python
def get_all_paths(self) -> list[str]
```

Get all registered paths.

---

## animate

```python
def animate(self, human_focus: HumanFocusTracker, graph: AGENTESEGraph | None, dt: float, phase: CircadianPhase | None=None) -> tuple[Position, str | None]
```

Compute next position and optional path.

---

## should_suggest

```python
def should_suggest(self, dt: float) -> bool
```

Check if this behavior should make a suggestion now.

---

## suggest_state

```python
def suggest_state(self) -> CursorState
```

Get preferred cursor state for this behavior.

---

## get_effective_behavior

```python
def get_effective_behavior(self, human_focus: HumanFocusTracker, task_urgency: float=0.5, phase: CircadianPhase | None=None) -> CursorBehavior
```

Compute effective behavior given current context.

---

## services.conductor.bus_bridge

## bus_bridge

```python
module bus_bridge
```

Bus Bridge: Cross-bus event forwarding for CLI v7 Phase 7 (Live Flux).

---

## wire_a2a_to_global_synergy

```python
def wire_a2a_to_global_synergy() -> Callable[[], None]
```

Bridge A2A events from WitnessSynergyBus to global SynergyBus.

---

## unwire_a2a_bridge

```python
def unwire_a2a_bridge() -> None
```

Stop the A2A bridge.

---

## is_bridge_active

```python
def is_bridge_active() -> bool
```

Check if the A2A bridge is currently active.

---

## bridge_a2a

```python
async def bridge_a2a(topic: str, event: dict[str, Any]) -> None
```

Bridge A2A events to global SynergyBus.

---

## services.conductor.contracts

## contracts

```python
module contracts
```

File I/O Contracts: Type definitions for world.file operations.

---

## FileReadRequest

```python
class FileReadRequest
```

Request to read a file.

---

## FileReadResponse

```python
class FileReadResponse
```

Response from reading a file.

---

## EditError

```python
class EditError(Enum)
```

Error types for file edit operations.

---

## FileEditRequest

```python
class FileEditRequest
```

Request to edit a file using exact string replacement.

---

## FileEditResponse

```python
class FileEditResponse
```

Response from editing a file.

---

## FileWriteRequest

```python
class FileWriteRequest
```

Request to write a new file (overwrite semantics).

---

## FileWriteResponse

```python
class FileWriteResponse
```

Response from writing a file.

---

## FileGlobRequest

```python
class FileGlobRequest
```

Request to glob for files by pattern.

---

## FileGlobResponse

```python
class FileGlobResponse
```

Response from glob operation.

---

## FileGrepRequest

```python
class FileGrepRequest
```

Request to grep for content.

---

## FileGrepMatch

```python
class FileGrepMatch
```

A single grep match.

---

## FileGrepResponse

```python
class FileGrepResponse
```

Response from grep operation.

---

## ArtifactType

```python
class ArtifactType(Enum)
```

Types of artifacts that can be output.

---

## OutputArtifactRequest

```python
class OutputArtifactRequest
```

Request to write an artifact to disk.

---

## OutputArtifactResponse

```python
class OutputArtifactResponse
```

Response from artifact output.

---

## FileCacheEntry

```python
class FileCacheEntry
```

Internal cache entry for read-before-edit validation.

---

## FileEditedPayload

```python
class FileEditedPayload
```

Payload for FILE_EDITED synergy event.

---

## FileCreatedPayload

```python
class FileCreatedPayload
```

Payload for FILE_CREATED synergy event.

---

## is_fresh

```python
def is_fresh(self, max_age_seconds: float=300) -> bool
```

Check if cache entry is still valid.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for persistence.

---

## services.conductor.file_guard

## file_guard

```python
module file_guard
```

FileEditGuard: Read-before-edit enforcement.

---

## FileGuardError

```python
class FileGuardError(Exception)
```

Base error for file guard operations.

---

## NotReadError

```python
class NotReadError(FileGuardError)
```

File was not read before edit attempt.

---

## StringNotFoundError

```python
class StringNotFoundError(FileGuardError)
```

Old string not found in file.

---

## StringNotUniqueError

```python
class StringNotUniqueError(FileGuardError)
```

Old string appears multiple times.

---

## FileChangedError

```python
class FileChangedError(FileGuardError)
```

File was modified since last read.

---

## FileEditGuard

```python
class FileEditGuard
```

Enforces Claude Code's read-before-edit pattern.

---

## get_file_guard

```python
def get_file_guard() -> FileEditGuard
```

Get or create the singleton FileEditGuard.

---

## reset_file_guard

```python
def reset_file_guard() -> None
```

Reset the singleton (for testing).

---

## set_event_emitter

```python
def set_event_emitter(self, emitter: Any) -> None
```

Inject the synergy event emitter.

---

## read_file

```python
async def read_file(self, request: FileReadRequest | str, *, agent_id: str='unknown') -> FileReadResponse
```

Read a file and cache for subsequent edits.

---

## edit_file

```python
async def edit_file(self, request: FileEditRequest, *, agent_id: str='unknown') -> FileEditResponse
```

Edit a file using exact string replacement.

---

## write_file

```python
async def write_file(self, request: FileWriteRequest, *, agent_id: str='unknown') -> FileWriteResponse
```

Write a new file (or overwrite existing).

---

## can_edit

```python
async def can_edit(self, path: str) -> bool
```

Check if a file can be edited (has been read recently).

---

## invalidate

```python
async def invalidate(self, path: str) -> bool
```

Remove a file from cache.

---

## clear_cache

```python
async def clear_cache(self) -> int
```

Clear entire cache. Returns number of entries cleared.

---

## get_statistics

```python
def get_statistics(self) -> dict[str, Any]
```

Get guard statistics.

---

## services.conductor.flux

## flux

```python
module flux
```

ConductorFlux: Reactive event integration for CLI v7 Phase 7 (Live Flux).

---

## ConductorEventType

```python
class ConductorEventType(Enum)
```

Event types for conductor-level fan-out.

---

## ConductorEvent

```python
class ConductorEvent
```

Unified event type for conductor fan-out.

---

## ConductorFlux

```python
class ConductorFlux
```

Reactive agent for CLI v7 event integration.

---

## get_conductor_flux

```python
def get_conductor_flux() -> ConductorFlux
```

Get the global ConductorFlux instance.

---

## reset_conductor_flux

```python
def reset_conductor_flux() -> None
```

Reset the global flux (for testing).

---

## start_conductor_flux

```python
def start_conductor_flux() -> ConductorFlux
```

Start the global ConductorFlux.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for WebSocket/SSE.

---

## running

```python
def running(self) -> bool
```

Check if flux is currently running.

---

## subscribe

```python
def subscribe(self, subscriber: ConductorEventSubscriber) -> Callable[[], None]
```

Subscribe to ConductorEvents.

---

## start

```python
def start(self) -> None
```

Start the ConductorFlux.

---

## stop

```python
def stop(self) -> None
```

Stop the ConductorFlux.

---

## handle

```python
async def handle(self, event: SynergyEvent) -> SynergyResult
```

Route event to ConductorFlux.

---

## services.conductor.operad

## operad

```python
module operad
```

SWARM_OPERAD: Composition grammar for agent swarms.

---

## create_swarm_operad

```python
def create_swarm_operad() -> Operad
```

Create the Swarm Operad.

---

## get_swarm_operad

```python
def get_swarm_operad() -> Operad
```

Get the SWARM_OPERAD instance.

---

## compose_spawn_delegate_workflow

```python
def compose_spawn_delegate_workflow(role: SwarmRole=RESEARCHER, coordinator: str='coordinator', worker: str='worker') -> PolyAgent[Any, Any, Any]
```

Compose a spawn -> delegate workflow.

---

## compose_parallel_research_workflow

```python
def compose_parallel_research_workflow(num_agents: int=3) -> PolyAgent[Any, Any, Any]
```

Compose a parallel research workflow.

---

## compose_implement_review_workflow

```python
def compose_implement_review_workflow(implementer: str='implementer', reviewer: str='reviewer') -> PolyAgent[Any, Any, Any]
```

Compose an implement -> review workflow.

---

## services.conductor.persistence

## persistence

```python
module persistence
```

WindowPersistence: D-gent integration for ConversationWindow state.

---

## WindowPersistence

```python
class WindowPersistence
```

Persistence layer for ConversationWindow using D-gent.

---

## get_window_persistence

```python
def get_window_persistence() -> WindowPersistence
```

Get or create the singleton WindowPersistence instance.

---

## reset_window_persistence

```python
def reset_window_persistence() -> None
```

Reset the singleton (for testing).

---

## __init__

```python
def __init__(self, dgent: DgentRouter | None=None, namespace: str='conductor_windows')
```

Initialize persistence layer.

---

## save_window

```python
async def save_window(self, session_id: str, window: 'ConversationWindow') -> str
```

Save a ConversationWindow to D-gent storage.

---

## load_window

```python
async def load_window(self, session_id: str) -> 'ConversationWindow | None'
```

Load a ConversationWindow from D-gent storage.

---

## delete_window

```python
async def delete_window(self, session_id: str) -> bool
```

Delete a persisted window.

---

## exists

```python
async def exists(self, session_id: str) -> bool
```

Check if a window exists for a session.

---

## list_windows

```python
async def list_windows(self, *, limit: int=100) -> list[tuple[str, dict[str, str]]]
```

List all persisted windows.

---

## services.conductor.presence

## presence

```python
module presence
```

Agent Presence: Visible cursor states and activity indicators.

---

## CursorState

```python
class CursorState(Enum)
```

Agent cursor state with rich properties.

---

## CircadianPhase

```python
class CircadianPhase(Enum)
```

Time of day phases for UI modulation.

---

## AgentCursor

```python
class AgentCursor
```

Represents an agent's visible presence in the workspace.

---

## PresenceEventType

```python
class PresenceEventType(Enum)
```

Types of presence events.

---

## PresenceUpdate

```python
class PresenceUpdate
```

Event emitted when agent presence changes.

---

## PresenceChannel

```python
class PresenceChannel
```

Broadcast channel for real-time cursor positions.

---

## get_presence_channel

```python
def get_presence_channel() -> PresenceChannel
```

Get or create the singleton PresenceChannel.

---

## reset_presence_channel

```python
def reset_presence_channel() -> None
```

Reset the singleton (for testing).

---

## render_presence_footer

```python
def render_presence_footer(cursors: list[AgentCursor], teaching_mode: bool=False, width: int=80) -> str
```

Render presence footer for CLI output.

---

## emoji

```python
def emoji(self) -> str
```

Visual indicator for CLI/UI display.

---

## color

```python
def color(self) -> str
```

CLI color for Rich/terminal output.

---

## tailwind_color

```python
def tailwind_color(self) -> str
```

Tailwind CSS class for web UI.

---

## animation_speed

```python
def animation_speed(self) -> float
```

Animation speed multiplier (0.0-1.0).

---

## description

```python
def description(self) -> str
```

Human-readable description of state.

---

## can_transition_to

```python
def can_transition_to(self) -> frozenset['CursorState']
```

Valid state transitions (Pattern #9: Directed State Cycle).

---

## can_transition

```python
def can_transition(self, target: 'CursorState') -> bool
```

Check if transition to target state is valid.

---

## from_hour

```python
def from_hour(cls, hour: int) -> 'CircadianPhase'
```

Get phase from hour (0-23).

---

## current

```python
def current(cls) -> 'CircadianPhase'
```

Get current phase based on local time.

---

## tempo_modifier

```python
def tempo_modifier(self) -> float
```

Animation tempo modifier.

---

## warmth

```python
def warmth(self) -> float
```

Color warmth (0.0 = cool, 1.0 = warm).

---

## emoji

```python
def emoji(self) -> str
```

Delegate to state emoji.

---

## color

```python
def color(self) -> str
```

Delegate to state color.

---

## effective_animation_speed

```python
def effective_animation_speed(self) -> float
```

Animation speed with circadian modulation.

---

## transition_to

```python
def transition_to(self, new_state: CursorState) -> bool
```

Attempt state transition.

---

## update_activity

```python
def update_activity(self, activity: str, focus_path: str | None=None) -> None
```

Update activity description and optional focus path.

---

## behavior_emoji

```python
def behavior_emoji(self) -> str
```

Get emoji combining state and behavior.

---

## to_cli

```python
def to_cli(self, teaching_mode: bool=False) -> str
```

Render for CLI output.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for persistence/API.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> 'AgentCursor'
```

Deserialize from dict.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for SSE/WebSocket.

---

## __init__

```python
def __init__(self, max_queue_size: int=100)
```

Initialize presence channel.

---

## active_cursors

```python
def active_cursors(self) -> list[AgentCursor]
```

Get all active cursors.

---

## subscriber_count

```python
def subscriber_count(self) -> int
```

Number of active subscribers.

---

## join

```python
async def join(self, cursor: AgentCursor) -> None
```

Register an agent cursor.

---

## leave

```python
async def leave(self, agent_id: str) -> bool
```

Unregister an agent cursor.

---

## broadcast

```python
async def broadcast(self, cursor: AgentCursor) -> int
```

Broadcast cursor update to all subscribers.

---

## subscribe

```python
async def subscribe(self) -> AsyncIterator[PresenceUpdate]
```

Subscribe to presence updates.

---

## get_cursor

```python
def get_cursor(self, agent_id: str) -> AgentCursor | None
```

Get cursor by agent ID.

---

## get_presence_snapshot

```python
async def get_presence_snapshot(self) -> dict[str, Any]
```

Get current presence state as a snapshot.

---

## services.conductor.summarizer

## summarizer

```python
module summarizer
```

Summarizer: LLM-powered conversation summarization.

---

## SummarizationResult

```python
class SummarizationResult
```

Result of a summarization operation.

---

## Summarizer

```python
class Summarizer
```

LLM-powered conversation summarizer.

---

## create_summarizer

```python
def create_summarizer(morpheus: 'MorpheusPersistence | None'=None, model: str | None=None) -> Summarizer
```

Create a Summarizer instance.

---

## savings

```python
def savings(self) -> int
```

Tokens saved by summarization.

---

## summarize

```python
async def summarize(self, messages: list['ContextMessage'], *, force_aggressive: bool=False) -> SummarizationResult
```

Summarize a list of messages.

---

## summarize_sync

```python
def summarize_sync(self, messages: list['ContextMessage']) -> str
```

Synchronous wrapper for use with ConversationWindow.

---

## get_statistics

```python
def get_statistics(self) -> dict[str, Any]
```

Get summarization statistics.

---

## services.conductor.swarm

## swarm

```python
module swarm
```

SwarmRole: Role = CursorBehavior x TrustLevel

---

## SwarmRole

```python
class SwarmRole
```

Role = Behavior x Trust

### Examples
```python
>>> RESEARCHER = SwarmRole(CursorBehavior.EXPLORER, TrustLevel.READ_ONLY)
```
```python
>>> - Behavior: Curious wanderer, independent discovery
```
```python
>>> - Trust: Can only read, not modify
```

---

## SpawnSignal

```python
class SpawnSignal
```

A signal contributing to agent selection.

---

## SpawnDecision

```python
class SpawnDecision
```

Result of spawn signal aggregation.

---

## SwarmSpawner

```python
class SwarmSpawner
```

Spawns agents using signal aggregation (Pattern #4).

---

## create_swarm_role

```python
def create_swarm_role(behavior: CursorBehavior | str, trust: str) -> SwarmRole
```

Factory for creating SwarmRole with string inputs.

---

## trust

```python
def trust(self) -> Any
```

Get the actual TrustLevel enum value.

---

## name

```python
def name(self) -> str
```

Human-readable role name.

---

## emoji

```python
def emoji(self) -> str
```

Combined emoji showing behavior + trust.

---

## capabilities

```python
def capabilities(self) -> FrozenSet[str]
```

Derived from trust level, NOT stored.

---

## description

```python
def description(self) -> str
```

Human-readable description.

---

## can_execute

```python
def can_execute(self, operation: str) -> bool
```

Check if role can execute an operation.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for API/persistence.

---

## evaluate_role

```python
def evaluate_role(self, task: str, context: dict[str, Any] | None=None) -> SpawnDecision
```

Evaluate best role for task using signal aggregation.

---

## spawn

```python
async def spawn(self, agent_id: str, task: str, context: dict[str, Any] | None=None) -> AgentCursor | None
```

Spawn an agent if allowed.

---

## despawn

```python
async def despawn(self, agent_id: str) -> bool
```

Remove an agent from the swarm.

---

## get_agent

```python
def get_agent(self, agent_id: str) -> AgentCursor | None
```

Get an active agent by ID.

---

## list_agents

```python
def list_agents(self) -> list[AgentCursor]
```

List all active agents.

---

## active_count

```python
def active_count(self) -> int
```

Number of active agents.

---

## at_capacity

```python
def at_capacity(self) -> bool
```

Whether the swarm is at max capacity.

---

## services.conductor.window

## window

```python
module window
```

ConversationWindow: Bounded history with context strategies.

---

## ContextMessage

```python
class ContextMessage
```

A message in the conversation window.

---

## WindowSnapshot

```python
class WindowSnapshot
```

Immutable snapshot of window state.

---

## ContextSegment

```python
class ContextSegment
```

A segment of the context window for visualization.

---

## ContextBreakdown

```python
class ContextBreakdown
```

Full breakdown of context window composition.

---

## ConversationWindow

```python
class ConversationWindow
```

Bounded conversation history with context strategies.

---

## create_window_from_config

```python
def create_window_from_config(config: 'ContextStrategy', max_turns: int=35, context_window_tokens: int=8000) -> ConversationWindow
```

Create a ConversationWindow from ChatConfig strategy.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize for LLM context.

---

## to_llm_format

```python
def to_llm_format(self) -> dict[str, str]
```

Format for LLM API (Anthropic/OpenAI compatible).

---

## __init__

```python
def __init__(self, max_turns: int=35, strategy: str='summarize', context_window_tokens: int=8000, summarization_threshold: float=0.8, summarizer: Callable[[list[ContextMessage]], str] | None=None)
```

Initialize conversation window.

---

## turn_count

```python
def turn_count(self) -> int
```

Number of turns in working memory.

---

## total_turn_count

```python
def total_turn_count(self) -> int
```

Total turns including summarized history.

---

## has_summary

```python
def has_summary(self) -> bool
```

Whether a summary exists.

---

## total_tokens

```python
def total_tokens(self) -> int
```

Total tokens in working memory (including summary).

---

## utilization

```python
def utilization(self) -> float
```

Context utilization as percentage (0.0-1.0).

---

## is_at_capacity

```python
def is_at_capacity(self) -> bool
```

Whether window is at max turns.

---

## needs_summarization

```python
def needs_summarization(self) -> bool
```

Whether summarization should be triggered.

---

## add_turn

```python
def add_turn(self, user_message: str, assistant_response: str, *, user_metadata: dict[str, Any] | None=None, assistant_metadata: dict[str, Any] | None=None) -> None
```

Add a conversation turn to the window.

---

## set_summarizer

```python
def set_summarizer(self, summarizer: Callable[[list[ContextMessage]], str]) -> None
```

Inject the summarizer function.

---

## set_system_prompt

```python
def set_system_prompt(self, prompt: str | None) -> None
```

Set the system prompt (prepended to context).

---

## get_context_messages

```python
def get_context_messages(self) -> list[ContextMessage]
```

Get messages for LLM context.

---

## get_context_for_llm

```python
def get_context_for_llm(self) -> list[dict[str, str]]
```

Get context in LLM API format.

---

## get_recent_turns

```python
def get_recent_turns(self, limit: int | None=None) -> list[tuple[str, str]]
```

Get recent turns as (user, assistant) tuples.

---

## snapshot

```python
def snapshot(self) -> WindowSnapshot
```

Create immutable snapshot of window state.

---

## get_context_breakdown

```python
def get_context_breakdown(self) -> ContextBreakdown
```

Get breakdown of context window composition.

---

## reset

```python
def reset(self) -> None
```

Clear the window (fresh start).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize window state.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> ConversationWindow
```

Deserialize window state.

---

## services.gardener.__init__

## __init__

```python
module __init__
```

Gardener Crown Jewel: Cultivation Practice for Ideas.

---

## services.gardener.contracts

## contracts

```python
module contracts
```

Gardener AGENTESE Contract Definitions.

---

## ConceptGardenerManifestResponse

```python
class ConceptGardenerManifestResponse
```

Gardener health status manifest.

---

## ConceptGardenerSessionManifestResponse

```python
class ConceptGardenerSessionManifestResponse
```

Active session status response.

---

## ConceptGardenerSessionDefineRequest

```python
class ConceptGardenerSessionDefineRequest
```

Request to start a new polynomial session.

---

## ConceptGardenerSessionDefineResponse

```python
class ConceptGardenerSessionDefineResponse
```

Response after creating a new session.

---

## ConceptGardenerSessionAdvanceRequest

```python
class ConceptGardenerSessionAdvanceRequest
```

Request to advance to the next phase.

---

## ConceptGardenerSessionAdvanceResponse

```python
class ConceptGardenerSessionAdvanceResponse
```

Response after advancing phase.

---

## ConceptGardenerPolynomialResponse

```python
class ConceptGardenerPolynomialResponse
```

Full polynomial state visualization.

---

## ConceptGardenerSessionsListResponse

```python
class ConceptGardenerSessionsListResponse
```

List of recent sessions.

---

## ConceptGardenerRouteRequest

```python
class ConceptGardenerRouteRequest
```

Request to route natural language to AGENTESE path.

---

## ConceptGardenerRouteResponse

```python
class ConceptGardenerRouteResponse
```

Route result with resolved path.

---

## ConceptGardenerProposeResponse

```python
class ConceptGardenerProposeResponse
```

Proactive suggestions for what to do next.

---

## services.gardener.persistence

## persistence

```python
module persistence
```

Gardener Persistence: TableAdapter + D-gent integration for Gardener Crown Jewel.

---

## SessionView

```python
class SessionView
```

View of a gardening session.

---

## IdeaView

```python
class IdeaView
```

View of a garden idea.

---

## PlotView

```python
class PlotView
```

View of a garden plot.

---

## ConnectionView

```python
class ConnectionView
```

View of an idea connection.

---

## GardenStatus

```python
class GardenStatus
```

Garden health status.

---

## GardenerPersistence

```python
class GardenerPersistence
```

Persistence layer for Gardener Crown Jewel.

---

## start_session

```python
async def start_session(self, title: str | None=None, notes: str | None=None) -> SessionView
```

**AGENTESE:** `concept.gardener.session.start`

Start a new gardening session.

---

## end_session

```python
async def end_session(self, session_id: str | None=None, notes: str | None=None) -> SessionView | None
```

**AGENTESE:** `concept.gardener.session.end`

End a gardening session.

---

## get_current_session

```python
async def get_current_session(self) -> SessionView | None
```

Get the current active session.

---

## get_session

```python
async def get_session(self, session_id: str) -> SessionView | None
```

Get a session by ID.

---

## list_sessions

```python
async def list_sessions(self, limit: int=20) -> list[SessionView]
```

List recent gardening sessions.

---

## plant_idea

```python
async def plant_idea(self, content: str, session_id: str | None=None, plot_id: str | None=None, tags: list[str] | None=None, confidence: float=0.3) -> IdeaView
```

**AGENTESE:** `self.garden.plant`

Plant a new idea in the garden.

---

## nurture_idea

```python
async def nurture_idea(self, idea_id: str, refinement: str | None=None, confidence_delta: float=0.1) -> IdeaView | None
```

**AGENTESE:** `self.garden.nurture`

Nurture an existing idea.

---

## harvest_idea

```python
async def harvest_idea(self, idea_id: str) -> IdeaView | None
```

**AGENTESE:** `self.garden.harvest`

Promote idea to next lifecycle stage.

---

## get_idea

```python
async def get_idea(self, idea_id: str, include_connections: bool=False) -> IdeaView | None
```

Get an idea by ID.

---

## list_ideas

```python
async def list_ideas(self, lifecycle: str | None=None, plot_id: str | None=None, session_id: str | None=None, limit: int=50) -> list[IdeaView]
```

List ideas with optional filters.

---

## create_plot

```python
async def create_plot(self, name: str, description: str | None=None, color: str | None=None) -> PlotView
```

Create a new garden plot.

---

## list_plots

```python
async def list_plots(self) -> list[PlotView]
```

List all garden plots.

---

## connect_ideas

```python
async def connect_ideas(self, source_id: str, target_id: str, connection_type: str='relates_to', strength: float=0.5, notes: str | None=None) -> ConnectionView | None
```

Create a connection between two ideas.

---

## manifest

```python
async def manifest(self) -> GardenStatus
```

**AGENTESE:** `self.garden.manifest`

Get garden health status.

---

## services.gardener.plan_parser

## plan_parser

```python
module plan_parser
```

Plan Parser: Extract progress from plan files and _forest.md.

---

## PlanMetadata

```python
class PlanMetadata
```

Parsed metadata from a plan file.

---

## parse_progress_string

```python
def parse_progress_string(progress_str: str) -> float
```

Parse a progress string like "88%" or "0.88" to a float.

---

## parse_forest_table

```python
def parse_forest_table(forest_path: Path) -> dict[str, PlanMetadata]
```

Parse the _forest.md table to extract plan progress.

---

## parse_plan_progress

```python
async def parse_plan_progress(plan_path: Path) -> PlanMetadata
```

Extract progress from an individual plan file.

---

## infer_crown_jewel

```python
def infer_crown_jewel(plan_name: str) -> str | None
```

Infer which Crown Jewel a plan corresponds to.

---

## infer_agentese_path

```python
def infer_agentese_path(plan_path: Path) -> str
```

Infer AGENTESE path from plan file location.

---

## services.gestalt.__init__

## __init__

```python
module __init__
```

Gestalt Crown Jewel: Living Garden Where Code Breathes.

---

## services.gestalt.contracts

## contracts

```python
module contracts
```

Gestalt AGENTESE Contract Definitions.

---

## GestaltManifestResponse

```python
class GestaltManifestResponse
```

Gestalt architecture manifest response.

---

## ModuleHealth

```python
class ModuleHealth
```

Health metrics for a single module.

---

## HealthResponse

```python
class HealthResponse
```

Response for health manifest aspect.

---

## TopologyNode

```python
class TopologyNode
```

A node in the 3D topology visualization.

---

## TopologyLink

```python
class TopologyLink
```

A link between topology nodes.

---

## TopologyStats

```python
class TopologyStats
```

Statistics for the topology.

---

## TopologyRequest

```python
class TopologyRequest
```

Request for topology visualization data.

---

## TopologyResponse

```python
class TopologyResponse
```

Response for topology visualization.

---

## DriftViolation

```python
class DriftViolation
```

A single drift violation.

---

## DriftResponse

```python
class DriftResponse
```

Response for drift violations.

---

## ModuleRequest

```python
class ModuleRequest
```

Request for module details.

---

## ModuleDependency

```python
class ModuleDependency
```

A module dependency.

---

## ModuleDependent

```python
class ModuleDependent
```

A module that depends on this one.

---

## ModuleResponse

```python
class ModuleResponse
```

Response for module details.

---

## ScanRequest

```python
class ScanRequest
```

Request to rescan codebase.

---

## ScanResponse

```python
class ScanResponse
```

Response after rescanning.

---

## services.gestalt.node

## node

```python
module node
```

Gestalt AGENTESE Node: @node("world.codebase")

---

## GestaltManifestRendering

```python
class GestaltManifestRendering
```

Rendering for codebase architecture manifest.

---

## TopologyRendering

```python
class TopologyRendering
```

Rendering for 3D topology visualization data.

---

## GestaltNode

```python
class GestaltNode(BaseLogosNode)
```

AGENTESE node for Gestalt Crown Jewel.

---

## __init__

```python
def __init__(self) -> None
```

Initialize GestaltNode.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `world.codebase.manifest`

Manifest codebase architecture to observer.

---

## services.gestalt.persistence

## persistence

```python
module persistence
```

Gestalt Persistence: TableAdapter + D-gent integration for Gestalt Crown Jewel.

---

## TopologyView

```python
class TopologyView
```

View of a code topology.

---

## CodeBlockView

```python
class CodeBlockView
```

View of a code block.

---

## CodeLinkView

```python
class CodeLinkView
```

View of a code link.

---

## GestaltStatus

```python
class GestaltStatus
```

Gestalt health status.

---

## GestaltPersistence

```python
class GestaltPersistence
```

Persistence layer for Gestalt Crown Jewel.

---

## create_topology

```python
async def create_topology(self, name: str, description: str | None=None, repo_path: str | None=None, git_ref: str | None=None) -> TopologyView
```

**AGENTESE:** `self.gestalt.topology.create`

Create a new code topology.

---

## get_topology

```python
async def get_topology(self, topology_id: str) -> TopologyView | None
```

Get a topology by ID.

---

## list_topologies

```python
async def list_topologies(self, limit: int=20) -> list[TopologyView]
```

List all topologies.

---

## delete_topology

```python
async def delete_topology(self, topology_id: str) -> bool
```

Delete a topology and all its blocks/links.

---

## add_block

```python
async def add_block(self, topology_id: str, name: str, block_type: str, file_path: str, line_start: int | None=None, line_end: int | None=None, position: tuple[float, float, float]=(0.0, 0.0, 0.0), test_coverage: float | None=None, complexity: float | None=None, content_hash: str | None=None) -> CodeBlockView | None
```

**AGENTESE:** `self.gestalt.block.add`

Add a code block to a topology.

---

## update_block_health

```python
async def update_block_health(self, block_id: str, test_coverage: float | None=None, complexity: float | None=None, churn_rate: float | None=None) -> CodeBlockView | None
```

**AGENTESE:** `self.gestalt.block.health`

Update block health metrics.

---

## update_block_position

```python
async def update_block_position(self, block_id: str, x: float, y: float, z: float=0.0) -> CodeBlockView | None
```

Update block 3D position.

---

## get_block

```python
async def get_block(self, block_id: str) -> CodeBlockView | None
```

Get a block by ID.

---

## list_blocks

```python
async def list_blocks(self, topology_id: str, block_type: str | None=None, file_path: str | None=None, limit: int=100) -> list[CodeBlockView]
```

List blocks in a topology with optional filters.

---

## add_link

```python
async def add_link(self, topology_id: str, source_block_id: str, target_block_id: str, link_type: str, strength: float=1.0, call_count: int | None=None, notes: str | None=None) -> CodeLinkView | None
```

**AGENTESE:** `self.gestalt.link.add`

Add a link between code blocks.

---

## list_links

```python
async def list_links(self, topology_id: str, link_type: str | None=None, block_id: str | None=None, limit: int=200) -> list[CodeLinkView]
```

List links with optional filters.

---

## trace_dependencies

```python
async def trace_dependencies(self, block_id: str, direction: str='both', max_depth: int=3) -> list[CodeLinkView]
```

**AGENTESE:** `self.gestalt.link.trace`

Trace dependency chain from a block.

---

## create_snapshot

```python
async def create_snapshot(self, topology_id: str, git_ref: str | None=None) -> str | None
```

**AGENTESE:** `self.gestalt.snapshot`

Create a snapshot of topology state.

---

## manifest

```python
async def manifest(self) -> GestaltStatus
```

**AGENTESE:** `self.gestalt.manifest`

Get gestalt health status.

---

## services.living_docs.__init__

## __init__

```python
module __init__
```

Living Docs: Documentation as Projection

---

## services.living_docs.extractor

## extractor

```python
module extractor
```

Docstring Extractor: Source -> DocNode

### Examples
```python
>>> ' and 'Example:' sections
```

### Things to Know

ℹ️ AST parsing requires valid Python syntax.
  - *Verified in: `test_extractor.py::test_invalid_syntax`*

🚨 **Critical:** Teaching section must use 'gotcha:' keyword for extraction.
  - *Verified in: `test_extractor.py::test_teaching_pattern`*

---

## DocstringExtractor

```python
class DocstringExtractor
```

Extract DocNodes from Python source files.

### Things to Know

ℹ️ Tier determination now includes agents/ and protocols/ as RICH.
  - *Verified in: `test_extractor.py::test_tier_rich_expanded`*

---

## extract_from_object

```python
def extract_from_object(obj: object) -> DocNode | None
```

Extract a DocNode from a Python object.

---

## should_extract

```python
def should_extract(self, path: Path) -> bool
```

Check if a file should be extracted (not excluded).

---

## extract_file

```python
def extract_file(self, path: Path) -> list[DocNode]
```

Extract DocNodes from a Python source file.

---

## extract_module_docstring

```python
def extract_module_docstring(self, path: Path) -> DocNode | None
```

Extract module-level docstring as a DocNode.

---

## extract_module

```python
def extract_module(self, source: str, module_name: str='') -> list[DocNode]
```

Extract DocNodes from Python source code.

---

## services.living_docs.generator

## generator

```python
module generator
```

**AGENTESE:** `concept.docs.generate`

Reference Documentation Generator

### Things to Know

ℹ️ generate_to_directory() creates directories if they don't exist. It will NOT overwrite existing files unless overwrite=True.
  - *Verified in: `test_generator.py::test_no_overwrite_by_default`*

---

## CategoryConfig

```python
class CategoryConfig
```

Configuration for a documentation category.

---

## GeneratedDocs

```python
class GeneratedDocs
```

Generated documentation output.

---

## GeneratedFile

```python
class GeneratedFile
```

Metadata for a generated documentation file.

---

## GenerationManifest

```python
class GenerationManifest
```

Manifest of all generated documentation files.

---

## ReferenceGenerator

```python
class ReferenceGenerator
```

Generate comprehensive reference documentation.

---

## generate_reference

```python
def generate_reference() -> str
```

Convenience function to generate full reference docs.

---

## generate_gotchas

```python
def generate_gotchas() -> str
```

Convenience function to generate gotchas page.

---

## generate_to_directory

```python
def generate_to_directory(output_dir: Path, overwrite: bool=False) -> GenerationManifest
```

Convenience function to generate docs to a directory.

---

## file_count

```python
def file_count(self) -> int
```

Number of files generated.

---

## to_dict

```python
def to_dict(self) -> dict[str, object]
```

Convert to dictionary for serialization.

---

## generate_all

```python
def generate_all(self) -> str
```

Generate complete reference documentation as markdown.

---

## generate_gotchas

```python
def generate_gotchas(self) -> str
```

Generate a dedicated gotchas/teaching moments page.

---

## generate_to_directory

```python
def generate_to_directory(self, output_dir: Path, overwrite: bool=False) -> GenerationManifest
```

Generate complete reference documentation to a directory structure.

---

## services.living_docs.node

## node

```python
module node
```

Living Docs AGENTESE Nodes

---

## LivingDocsNode

```python
class LivingDocsNode(BaseLogosNode)
```

AGENTESE node for Living Documentation.

### Things to Know

🚨 **Critical:** Observer kind must be one of: human, agent, ide.
  - *Verified in: `test_node.py::test_observer_validation`*

---

## SelfDocsNode

```python
class SelfDocsNode(BaseLogosNode)
```

self.docs - documentation in current scope.

---

## get_living_docs_node

```python
def get_living_docs_node() -> LivingDocsNode
```

Get a LivingDocsNode instance.

---

## get_self_docs_node

```python
def get_self_docs_node() -> SelfDocsNode
```

Get a SelfDocsNode instance.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize mutable defaults.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any] | Observer') -> Renderable
```

Collapse to observer-appropriate representation.

---

## extract

```python
async def extract(self, observer: 'Umwelt[Any, Any] | Observer', path: str) -> Renderable
```

Extract documentation from a source file.

---

## project

```python
async def project(self, observer: 'Umwelt[Any, Any] | Observer', path: str, observer_kind: Literal['human', 'agent', 'ide']='human', density: Literal['compact', 'comfortable', 'spacious']='comfortable', symbol: str | None=None) -> Renderable
```

Project documentation for a specific observer.

---

## list

```python
async def list(self, observer: 'Umwelt[Any, Any] | Observer', path: str | None=None, tier: Literal['minimal', 'standard', 'rich'] | None=None, only_with_teaching: bool=False) -> Renderable
```

List DocNodes with optional filtering.

---

## gotchas

```python
async def gotchas(self, observer: 'Umwelt[Any, Any] | Observer', path: str, severity: Literal['info', 'warning', 'critical'] | None=None) -> Renderable
```

Get all teaching moments (gotchas) from a file.

---

## manifest

```python
async def manifest(self, observer: 'Umwelt[Any, Any] | Observer') -> Renderable
```

Collapse to observer-appropriate representation.

---

## for_file

```python
async def for_file(self, observer: 'Umwelt[Any, Any] | Observer', path: str, observer_kind: Literal['human', 'agent', 'ide']='human', density: Literal['compact', 'comfortable', 'spacious']='comfortable') -> Renderable
```

Get documentation for a specific file.

---

## gotchas

```python
async def gotchas(self, observer: 'Umwelt[Any, Any] | Observer', path: str | None=None, scope: str | None=None) -> Renderable
```

Get teaching moments in the current scope.

---

## services.living_docs.projector

## projector

```python
module projector
```

Living Docs Projector: DocNode x Observer -> Surface

### Things to Know

ℹ️ Projection is a single function, not a class hierarchy.
  - *Verified in: `test_projector.py::test_single_function`*

ℹ️ Density only applies to human observers.
  - *Verified in: `test_projector.py::test_density_human_only`*

---

## DensityParams

```python
class DensityParams
```

Parameters that vary by density level.

---

## project

```python
def project(node: DocNode, observer: LivingDocsObserver) -> Surface
```

Project a DocNode to a Surface for a specific observer.

---

## LivingDocsProjector

```python
class LivingDocsProjector
```

Stateless projector for use in AGENTESE nodes.

---

## project

```python
def project(self, node: DocNode, observer: LivingDocsObserver) -> Surface
```

Project a DocNode to a Surface.

---

## project_many

```python
def project_many(self, nodes: list[DocNode], observer: LivingDocsObserver) -> list[Surface]
```

Project multiple DocNodes.

---

## project_with_filter

```python
def project_with_filter(self, nodes: list[DocNode], observer: LivingDocsObserver, *, min_tier: Tier=Tier.MINIMAL, only_with_teaching: bool=False) -> list[Surface]
```

Project nodes with filtering.

---

## services.living_docs.spec_extractor

## spec_extractor

```python
module spec_extractor
```

Spec Extractor: Markdown Spec -> DocNode

### Things to Know

ℹ️ Spec files have different structure than Python docstrings. Use markdown-aware parsing, not AST.
  - *Verified in: `test_spec_extractor.py::test_markdown_structure`*

🚨 **Critical:** Anti-patterns are warnings, Laws are critical. Severity mapping matters for proper prioritization.
  - *Verified in: `test_spec_extractor.py::test_severity_mapping`*

---

## SpecSection

```python
class SpecSection
```

A section from a markdown spec file.

---

## SpecExtractor

```python
class SpecExtractor
```

Extract DocNodes from markdown specification files.

### Things to Know

ℹ️ The extractor processes spec/ files, not impl/ Python files. Use DocstringExtractor for Python, SpecExtractor for markdown.
  - *Verified in: `test_spec_extractor.py::test_file_type_separation`*

---

## should_extract

```python
def should_extract(self, path: Path) -> bool
```

Check if a file should be extracted (not excluded).

---

## extract_file

```python
def extract_file(self, path: Path) -> list[DocNode]
```

Extract DocNodes from a markdown specification file.

---

## extract_spec

```python
def extract_spec(self, content: str, module_name: str='') -> list[DocNode]
```

Extract DocNodes from markdown specification content.

---

## extract_spec_summary

```python
def extract_spec_summary(self, path: Path) -> DocNode | None
```

Extract a top-level summary DocNode for the entire spec file.

---

## services.living_docs.teaching

## teaching

```python
module teaching
```

**AGENTESE:** `concept.docs.teaching`

Teaching Moments Query API

### Things to Know

ℹ️ Evidence paths are relative to impl/claude.
  - *Verified in: `test_teaching.py::test_evidence_path_resolution`*

---

## TeachingResult

```python
class TeachingResult
```

A teaching moment with its source context.

---

## TeachingQuery

```python
class TeachingQuery
```

Query parameters for filtering teaching moments.

---

## VerificationResult

```python
class VerificationResult
```

Result of evidence verification for a teaching moment.

---

## TeachingStats

```python
class TeachingStats
```

Statistics about teaching moments in the codebase.

---

## TeachingCollector

```python
class TeachingCollector
```

Collect and query teaching moments from the codebase.

---

## query_teaching

```python
def query_teaching(severity: Literal['critical', 'warning', 'info'] | None=None, module_pattern: str | None=None, symbol_pattern: str | None=None, with_evidence: bool | None=None) -> list[TeachingResult]
```

Query teaching moments with optional filters.

---

## verify_evidence

```python
def verify_evidence() -> list[VerificationResult]
```

Verify that all evidence paths exist.

---

## get_teaching_stats

```python
def get_teaching_stats() -> TeachingStats
```

Get statistics about teaching moments in the codebase.

---

## collect_all

```python
def collect_all(self) -> Iterator[TeachingResult]
```

Collect all teaching moments from the codebase.

---

## query

```python
def query(self, query: TeachingQuery) -> list[TeachingResult]
```

Query teaching moments with filters.

---

## verify_evidence

```python
def verify_evidence(self) -> list[VerificationResult]
```

Verify that all evidence paths exist.

---

## get_stats

```python
def get_stats(self) -> TeachingStats
```

Get statistics about teaching moments.

---

## services.living_docs.types

## types

```python
module types
```

Living Docs Core Types

---

## Tier

```python
class Tier(Enum)
```

Extraction tier determines extraction depth.

---

## TeachingMoment

```python
class TeachingMoment
```

A gotcha with provenance. The killer feature.

### Things to Know

🚨 **Critical:** Always include evidence when creating TeachingMoments.
  - *Verified in: `test_types.py::test_teaching_moment_evidence`*

---

## DocNode

```python
class DocNode
```

Atomic documentation primitive extracted from source.

### Things to Know

ℹ️ agentese_path is extracted from "AGENTESE: <path>" in docstrings. Not all symbols have AGENTESE paths—only exposed nodes do.
  - *Verified in: `test_extractor.py::test_agentese_path_extraction`*

ℹ️ related_symbols should be kept small (max 5). Too many cross-references makes navigation confusing.
  - *Verified in: `test_types.py::test_related_symbols_limit`*

---

## LivingDocsObserver

```python
class LivingDocsObserver
```

Who's reading determines what they see.

---

## Surface

```python
class Surface
```

Projected output for an observer.

---

## Verification

```python
class Verification
```

Round-trip verification result.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_text

```python
def to_text(self) -> str
```

Convert to human-readable text.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## compression_adequate

```python
def compression_adequate(self) -> bool
```

Check if docs adequately compress implementation.

---

## services.park.__init__

## __init__

```python
module __init__
```

Park Crown Jewel: Punchdrunk Westworld Where Hosts Can Say No.

---

## services.park.contracts

## contracts

```python
module contracts
```

Park AGENTESE Contract Definitions.

---

## ParkManifestResponse

```python
class ParkManifestResponse
```

Park health status manifest response.

---

## HostSummary

```python
class HostSummary
```

Summary of a park host for list views.

---

## HostDetail

```python
class HostDetail
```

Full host details.

---

## HostListResponse

```python
class HostListResponse
```

Response for host list aspect.

---

## HostGetResponse

```python
class HostGetResponse
```

Response for host get aspect.

---

## HostCreateRequest

```python
class HostCreateRequest
```

Request to create a new park host.

---

## HostCreateResponse

```python
class HostCreateResponse
```

Response after creating a host.

---

## HostUpdateRequest

```python
class HostUpdateRequest
```

Request to update host state.

---

## HostUpdateResponse

```python
class HostUpdateResponse
```

Response after updating a host.

---

## InteractionDetail

```python
class InteractionDetail
```

Details of an interaction with a host.

---

## HostInteractRequest

```python
class HostInteractRequest
```

Request to interact with a host.

---

## HostInteractResponse

```python
class HostInteractResponse
```

Response after interacting with a host.

---

## MemorySummary

```python
class MemorySummary
```

Summary of a host memory.

---

## HostWitnessRequest

```python
class HostWitnessRequest
```

Request to view host memories.

---

## HostWitnessResponse

```python
class HostWitnessResponse
```

Response for host memories.

---

## EpisodeSummary

```python
class EpisodeSummary
```

Summary of a park episode for list views.

---

## EpisodeDetail

```python
class EpisodeDetail
```

Full episode details.

---

## EpisodeListResponse

```python
class EpisodeListResponse
```

Response for episode list aspect.

---

## EpisodeStartRequest

```python
class EpisodeStartRequest
```

Request to start a park episode.

---

## EpisodeStartResponse

```python
class EpisodeStartResponse
```

Response after starting an episode.

---

## EpisodeEndRequest

```python
class EpisodeEndRequest
```

Request to end a park episode.

---

## EpisodeEndResponse

```python
class EpisodeEndResponse
```

Response after ending an episode.

---

## LocationSummary

```python
class LocationSummary
```

Summary of a park location.

---

## LocationListResponse

```python
class LocationListResponse
```

Response for location list aspect.

---

## LocationCreateRequest

```python
class LocationCreateRequest
```

Request to create a location.

---

## LocationCreateResponse

```python
class LocationCreateResponse
```

Response after creating a location.

---

## ScenarioSummary

```python
class ScenarioSummary
```

Summary of a scenario template for list views.

---

## ScenarioListResponse

```python
class ScenarioListResponse
```

Response for scenario list aspect.

---

## ScenarioDetail

```python
class ScenarioDetail
```

Full scenario template details.

---

## ScenarioGetRequest

```python
class ScenarioGetRequest
```

Request to get a scenario template.

---

## ScenarioGetResponse

```python
class ScenarioGetResponse
```

Response for scenario get aspect.

---

## ScenarioStartRequest

```python
class ScenarioStartRequest
```

Request to start a scenario session.

---

## SessionProgress

```python
class SessionProgress
```

Progress of a scenario session.

---

## ScenarioSessionDetail

```python
class ScenarioSessionDetail
```

Details of an active scenario session.

---

## ScenarioStartResponse

```python
class ScenarioStartResponse
```

Response after starting a scenario.

---

## ScenarioTickRequest

```python
class ScenarioTickRequest
```

Request to advance a scenario session.

---

## ScenarioTickResponse

```python
class ScenarioTickResponse
```

Response after advancing a scenario.

---

## ScenarioEndRequest

```python
class ScenarioEndRequest
```

Request to end/abandon a scenario session.

---

## ScenarioEndResponse

```python
class ScenarioEndResponse
```

Response after ending a scenario.

---

## ScenarioSessionListResponse

```python
class ScenarioSessionListResponse
```

Response for active sessions list.

---

## ConsentDebtRequest

```python
class ConsentDebtRequest
```

Request for consent debt operations.

---

## ConsentDebtResponse

```python
class ConsentDebtResponse
```

Response for consent debt operations.

---

## services.park.node

## node

```python
module node
```

Park AGENTESE Node: @node("world.park")

---

## ParkManifestRendering

```python
class ParkManifestRendering
```

Rendering for park manifest (status overview).

---

## HostRendering

```python
class HostRendering
```

Rendering for a single park host.

---

## HostListRendering

```python
class HostListRendering
```

Rendering for list of park hosts.

---

## EpisodeRendering

```python
class EpisodeRendering
```

Rendering for a park episode.

---

## InteractionRendering

```python
class InteractionRendering
```

Rendering for a host interaction.

---

## MemoryListRendering

```python
class MemoryListRendering
```

Rendering for host memories.

---

## LocationListRendering

```python
class LocationListRendering
```

Rendering for park locations.

---

## ParkNode

```python
class ParkNode(BaseLogosNode)
```

AGENTESE node for Park Crown Jewel.

---

## __init__

```python
def __init__(self, park_persistence: ParkPersistence, scenario_service: ScenarioService | None=None) -> None
```

Initialize ParkNode.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `world.park.manifest`

Manifest park status overview.

---

## services.park.persistence

## persistence

```python
module persistence
```

Park Persistence: TableAdapter + D-gent integration for Park Crown Jewel.

---

## HostView

```python
class HostView
```

View of a park host.

---

## MemoryView

```python
class MemoryView
```

View of a host memory.

---

## EpisodeView

```python
class EpisodeView
```

View of a park episode.

---

## InteractionView

```python
class InteractionView
```

View of a host interaction.

---

## LocationView

```python
class LocationView
```

View of a park location.

---

## ParkStatus

```python
class ParkStatus
```

Park health status.

---

## ParkPersistence

```python
class ParkPersistence
```

Persistence layer for Park Crown Jewel.

---

## create_host

```python
async def create_host(self, name: str, character: str, backstory: str | None=None, traits: dict[str, Any] | None=None, values: list[str] | None=None, boundaries: list[str] | None=None, location: str | None=None) -> HostView
```

**AGENTESE:** `world.park.host.create`

Create a new park host.

---

## get_host

```python
async def get_host(self, host_id: str) -> HostView | None
```

Get a host by ID.

---

## get_host_by_name

```python
async def get_host_by_name(self, name: str) -> HostView | None
```

Get a host by name.

---

## list_hosts

```python
async def list_hosts(self, character: str | None=None, location: str | None=None, active_only: bool=True, limit: int=50) -> list[HostView]
```

List hosts with optional filters.

---

## update_host_state

```python
async def update_host_state(self, host_id: str, mood: str | None=None, energy_level: float | None=None, location: str | None=None) -> HostView | None
```

Update host state (mood, energy, location).

---

## form_memory

```python
async def form_memory(self, host_id: str, content: str, memory_type: str='event', salience: float=0.5, emotional_valence: float=0.0, episode_id: str | None=None, visitor_id: str | None=None) -> MemoryView | None
```

**AGENTESE:** `world.park.host.remember`

Form a new memory for a host.

---

## recall_memories

```python
async def recall_memories(self, host_id: str, memory_type: str | None=None, min_salience: float=0.0, limit: int=20) -> list[MemoryView]
```

**AGENTESE:** `world.park.host.witness`

Recall host memories.

---

## decay_memories

```python
async def decay_memories(self, host_id: str, decay_rate: float=0.05, min_salience: float=0.1) -> int
```

Decay memory salience over time.

---

## start_episode

```python
async def start_episode(self, visitor_id: str | None=None, visitor_name: str | None=None, title: str | None=None) -> EpisodeView
```

**AGENTESE:** `world.park.episode.start`

Start a new park episode.

---

## end_episode

```python
async def end_episode(self, episode_id: str, summary: str | None=None, status: str='completed') -> EpisodeView | None
```

**AGENTESE:** `world.park.episode.end`

End a park episode.

---

## get_episode

```python
async def get_episode(self, episode_id: str) -> EpisodeView | None
```

Get an episode by ID.

---

## list_episodes

```python
async def list_episodes(self, visitor_id: str | None=None, status: str | None=None, limit: int=20) -> list[EpisodeView]
```

List episodes with optional filters.

---

## interact

```python
async def interact(self, episode_id: str, host_id: str, visitor_input: str, interaction_type: str='dialogue', location: str | None=None, check_consent: bool=True) -> InteractionView | None
```

**AGENTESE:** `world.park.host.interact`

Create an interaction with a host.

---

## list_interactions

```python
async def list_interactions(self, episode_id: str | None=None, host_id: str | None=None, limit: int=50) -> list[InteractionView]
```

List interactions with optional filters.

---

## create_location

```python
async def create_location(self, name: str, description: str | None=None, atmosphere: str | None=None, x: float | None=None, y: float | None=None, capacity: int | None=None, connected_to: list[str] | None=None) -> LocationView
```

Create a park location.

---

## list_locations

```python
async def list_locations(self, open_only: bool=True) -> list[LocationView]
```

List park locations.

---

## manifest

```python
async def manifest(self) -> ParkStatus
```

**AGENTESE:** `world.park.manifest`

Get park health status.

---

## services.park.scenario_service

## scenario_service

```python
module scenario_service
```

Scenario Service: Structured scenarios for Punchdrunk Park.

---

## ScenarioView

```python
class ScenarioView
```

View of a scenario template for API/CLI rendering.

---

## ScenarioDetailView

```python
class ScenarioDetailView
```

Detailed view of a scenario template.

---

## SessionView

```python
class SessionView
```

View of an active scenario session.

---

## TickResultView

```python
class TickResultView
```

View of a scenario tick result.

---

## ScenarioService

```python
class ScenarioService
```

Service layer for Scenario operations.

---

## create_scenario_service

```python
def create_scenario_service(registry: ScenarioRegistry | None=None, director: 'DirectorAgent | None'=None) -> ScenarioService
```

Create a configured ScenarioService.

---

## __init__

```python
def __init__(self, registry: ScenarioRegistry | None=None, director: 'DirectorAgent | None'=None) -> None
```

Initialize scenario service.

---

## registry

```python
def registry(self) -> ScenarioRegistry
```

Underlying scenario registry.

---

## register_template

```python
def register_template(self, template: ScenarioTemplate) -> list[str]
```

Register a scenario template.

---

## list_scenarios

```python
async def list_scenarios(self, scenario_type: ScenarioType | None=None, tags: list[str] | None=None, difficulty: str | None=None, limit: int=50) -> list[ScenarioView]
```

**AGENTESE:** `world.park.scenario.list`

List available scenario templates.

---

## get_scenario

```python
async def get_scenario(self, scenario_id: str, detail: bool=False) -> ScenarioView | ScenarioDetailView | None
```

**AGENTESE:** `world.park.scenario.get`

Get a scenario template by ID.

---

## start_session

```python
async def start_session(self, scenario_id: str) -> SessionView
```

**AGENTESE:** `world.park.scenario.start`

Start a new scenario session.

---

## get_session

```python
async def get_session(self, session_id: str) -> SessionView | None
```

Get a session by ID.

---

## list_sessions

```python
async def list_sessions(self, active_only: bool=True, limit: int=20) -> list[SessionView]
```

List scenario sessions.

---

## tick

```python
async def tick(self, session_id: str, elapsed_seconds: float=1.0) -> TickResultView
```

**AGENTESE:** `world.park.scenario.tick`

Advance a scenario session.

---

## record_interaction

```python
async def record_interaction(self, session_id: str, from_citizen: str, to_citizen: str, interaction_type: str='dialogue', content: str='') -> dict[str, Any]
```

Record an interaction in a session.

---

## reveal_information

```python
async def reveal_information(self, session_id: str, info_key: str) -> dict[str, Any]
```

Reveal information in a session (mystery scenarios).

---

## abandon_session

```python
async def abandon_session(self, session_id: str, reason: str='') -> SessionView
```

**AGENTESE:** `world.park.scenario.end`

Abandon a scenario session.

---

## complete_session

```python
async def complete_session(self, session_id: str) -> SessionView
```

Get the final state of a completed session.

---

## get_consent_debt

```python
async def get_consent_debt(self, session_id: str, citizen_name: str) -> float
```

Get consent debt for a citizen in a session.

---

## incur_consent_debt

```python
async def incur_consent_debt(self, session_id: str, citizen_name: str, amount: float=0.1) -> dict[str, Any]
```

Incur consent debt for forcing a host to act.

---

## can_inject_beat

```python
async def can_inject_beat(self, session_id: str, citizen_name: str) -> bool
```

Check if a beat can be injected for this citizen.

---

## apologize

```python
async def apologize(self, session_id: str, citizen_name: str, reduction: float=0.15) -> dict[str, Any]
```

Reduce consent debt by apologizing.

---

## services.town.__init__

## __init__

```python
module __init__
```

Town Crown Jewel: Agent Simulation Westworld.

---

## services.town.budget_service

## budget_service

```python
module budget_service
```

Town Budget Service: Credit and subscription tracking for Agent Town.

---

## SubscriptionTier

```python
class SubscriptionTier
```

Subscription tier definition per spec/town/monetization.md.

---

## ConsentState

```python
class ConsentState
```

Tracks consent debt between user and inhabited citizen.

---

## UserBudgetInfo

```python
class UserBudgetInfo
```

Complete budget information for a user.

---

## BudgetStore

```python
class BudgetStore(Protocol)
```

Protocol for budget storage backends.

---

## InMemoryBudgetStore

```python
class InMemoryBudgetStore
```

In-memory budget store for development and testing.

---

## RedisBudgetStore

```python
class RedisBudgetStore
```

Redis-backed budget store for production.

---

## create_budget_store

```python
def create_budget_store(use_redis: bool=True) -> BudgetStore
```

Create a budget store instance.

---

## can_force

```python
def can_force(self) -> bool
```

Force requires debt < 0.8 and cooldown elapsed.

---

## apply_force

```python
def apply_force(self, action: str='', severity: float=0.2) -> None
```

Force increases debt, resets cooldown, logs the action.

---

## cool_down

```python
def cool_down(self, elapsed: float) -> None
```

Debt decays over time (harmony restoration).

---

## at_rupture

```python
def at_rupture(self) -> bool
```

Citizen refuses all interaction until debt clears.

---

## apologize

```python
def apologize(self, sincerity: float=0.1) -> None
```

Apologize action reduces debt.

---

## status_message

```python
def status_message(self) -> str
```

Get human-readable status message.

---

## tier

```python
def tier(self) -> SubscriptionTier
```

Get tier configuration.

---

## monthly_remaining

```python
def monthly_remaining(self, action: str, lod_level: int | None=None) -> int
```

Get remaining included actions for this month.

---

## can_afford_credits

```python
def can_afford_credits(self, credits: int) -> bool
```

Check if user has enough credits.

---

## get_budget

```python
async def get_budget(self, user_id: str) -> UserBudgetInfo | None
```

Get budget info for a user.

---

## create_budget

```python
async def create_budget(self, user_id: str, tier: str='TOURIST') -> UserBudgetInfo
```

Create budget for a new user.

---

## spend_credits

```python
async def spend_credits(self, user_id: str, credits: int) -> bool
```

Spend credits from user's balance.

---

## add_credits

```python
async def add_credits(self, user_id: str, credits: int) -> bool
```

Add credits to user's balance (from purchase).

---

## record_action

```python
async def record_action(self, user_id: str, action: str, credits: int) -> bool
```

Record action usage (monthly counter + credit spend if needed).

---

## get_consent_state

```python
async def get_consent_state(self, user_id: str, citizen_id: str) -> ConsentState | None
```

Get consent debt state for a user-citizen pair.

---

## update_consent_state

```python
async def update_consent_state(self, user_id: str, consent: ConsentState) -> bool
```

Update consent debt state.

---

## update_subscription

```python
async def update_subscription(self, user_id: str, tier: str, renews_at: datetime) -> bool
```

Update user's subscription tier and renewal date.

---

## get_or_create

```python
async def get_or_create(self, user_id: str, tier: str='TOURIST') -> UserBudgetInfo
```

Get existing budget or create new one.

---

## get_budget

```python
async def get_budget(self, user_id: str) -> UserBudgetInfo | None
```

Get budget info for a user.

---

## create_budget

```python
async def create_budget(self, user_id: str, tier: str='TOURIST') -> UserBudgetInfo
```

Create budget for a new user.

---

## spend_credits

```python
async def spend_credits(self, user_id: str, credits: int) -> bool
```

Spend credits from user's balance.

---

## add_credits

```python
async def add_credits(self, user_id: str, credits: int) -> bool
```

Add credits to user's balance.

---

## record_action

```python
async def record_action(self, user_id: str, action: str, credits: int) -> bool
```

Record action usage.

---

## get_consent_state

```python
async def get_consent_state(self, user_id: str, citizen_id: str) -> ConsentState | None
```

Get consent debt state.

---

## update_consent_state

```python
async def update_consent_state(self, user_id: str, consent: ConsentState) -> bool
```

Update consent debt state.

---

## update_subscription

```python
async def update_subscription(self, user_id: str, tier: str, renews_at: datetime) -> bool
```

Update subscription tier and renewal.

---

## get_or_create

```python
async def get_or_create(self, user_id: str, tier: str='TOURIST') -> UserBudgetInfo
```

Get existing budget or create new one.

---

## __init__

```python
def __init__(self, redis_url: str | None=None) -> None
```

Initialize Redis connection.

---

## get_budget

```python
async def get_budget(self, user_id: str) -> UserBudgetInfo | None
```

Get budget info for a user.

---

## create_budget

```python
async def create_budget(self, user_id: str, tier: str='TOURIST') -> UserBudgetInfo
```

Create budget for a new user.

---

## spend_credits

```python
async def spend_credits(self, user_id: str, credits: int) -> bool
```

Spend credits atomically.

---

## add_credits

```python
async def add_credits(self, user_id: str, credits: int) -> bool
```

Add credits.

---

## record_action

```python
async def record_action(self, user_id: str, action: str, credits: int) -> bool
```

Record action and spend credits if needed.

---

## get_consent_state

```python
async def get_consent_state(self, user_id: str, citizen_id: str) -> ConsentState | None
```

Get consent debt state.

---

## update_consent_state

```python
async def update_consent_state(self, user_id: str, consent: ConsentState) -> bool
```

Update consent debt state.

---

## update_subscription

```python
async def update_subscription(self, user_id: str, tier: str, renews_at: datetime) -> bool
```

Update subscription tier and renewal.

---

## get_or_create

```python
async def get_or_create(self, user_id: str, tier: str='TOURIST') -> UserBudgetInfo
```

Get existing budget or create new one.

---

## services.town.bus_wiring

## bus_wiring

```python
module bus_wiring
```

Town Bus Wiring: Connect Town services to the three-bus architecture.

---

## TownSynergyBus

```python
class TownSynergyBus
```

Simplified SynergyBus for cross-jewel town events.

---

## TownEventBus

```python
class TownEventBus
```

EventBus for UI fan-out.

---

## TownDataBus

```python
class TownDataBus
```

Town-specific DataBus that emits TownEvent types.

---

## wire_data_to_synergy

```python
def wire_data_to_synergy(data_bus: TownDataBus, synergy_bus: TownSynergyBus) -> list[UnsubscribeFunc]
```

Wire DataBus events to SynergyBus topics.

---

## wire_synergy_to_event

```python
def wire_synergy_to_event(synergy_bus: TownSynergyBus, event_bus: TownEventBus, topics: list[str] | None=None) -> list[UnsubscribeFunc]
```

Wire SynergyBus topics to EventBus fan-out.

---

## kgent_narrative_handler

```python
async def kgent_narrative_handler(topic: str, event: TownEvent) -> None
```

K-gent handler: Generate narrative from gossip events.

---

## atelier_prompt_handler

```python
async def atelier_prompt_handler(topic: str, event: TownEvent) -> None
```

Atelier handler: Generate creative prompt from coalition events.

---

## mgent_stigmergy_handler

```python
async def mgent_stigmergy_handler(topic: str, event: TownEvent) -> None
```

M-gent handler: Update stigmergy from relationship events.

---

## TownBusManager

```python
class TownBusManager
```

Manages the three-bus architecture for Town.

---

## get_town_bus_manager

```python
def get_town_bus_manager() -> TownBusManager
```

Get the global TownBusManager instance.

---

## reset_town_bus_manager

```python
def reset_town_bus_manager() -> None
```

Reset the global TownBusManager (for testing).

---

## publish

```python
async def publish(self, topic: str, event: TownEvent) -> None
```

Publish an event to a topic.

---

## subscribe

```python
def subscribe(self, topic: str, handler: SynergyHandler) -> UnsubscribeFunc
```

Subscribe to a topic.

---

## stats

```python
def stats(self) -> dict[str, int]
```

Get bus statistics.

---

## clear

```python
def clear(self) -> None
```

Clear all handlers (for testing).

---

## publish

```python
async def publish(self, event: TownEvent) -> None
```

Publish event to all subscribers.

---

## subscribe

```python
def subscribe(self, handler: TownEventHandler) -> UnsubscribeFunc
```

Subscribe to all events.

---

## stats

```python
def stats(self) -> dict[str, int]
```

Get bus statistics.

---

## clear

```python
def clear(self) -> None
```

Clear all subscribers (for testing).

---

## __init__

```python
def __init__(self, base_bus: DataBus | None=None) -> None
```

Initialize with optional base DataBus.

---

## emit

```python
async def emit(self, event: TownEvent) -> None
```

Emit a town event.

---

## subscribe

```python
def subscribe(self, event_type: type[TownEvent], handler: TownEventHandler) -> UnsubscribeFunc
```

Subscribe to a specific event type.

---

## subscribe_all

```python
def subscribe_all(self, handler: TownEventHandler) -> UnsubscribeFunc
```

Subscribe to all event types.

---

## stats

```python
def stats(self) -> dict[str, int]
```

Get bus statistics.

---

## clear

```python
def clear(self) -> None
```

Clear all handlers (for testing).

---

## wire_all

```python
def wire_all(self) -> None
```

Wire all buses together.

---

## wire_cross_jewel_handlers

```python
def wire_cross_jewel_handlers(self) -> None
```

Wire cross-jewel event handlers.

---

## unwire_all

```python
def unwire_all(self) -> None
```

Disconnect all wiring.

---

## clear

```python
def clear(self) -> None
```

Clear all buses and wiring (for testing).

---

## stats

```python
def stats(self) -> dict[str, dict[str, int]]
```

Get combined statistics.

---

## services.town.citizen_node

## citizen_node

```python
module citizen_node
```

Town Citizen AGENTESE Node: @node("world.town.citizen")

---

## CitizenManifestRendering

```python
class CitizenManifestRendering
```

Rendering for citizen registry manifest.

---

## CitizenManifestResponse

```python
class CitizenManifestResponse
```

Response type for citizen manifest.

---

## CitizenNode

```python
class CitizenNode(BaseLogosNode)
```

AGENTESE node for Town Citizen Registry.

---

## __init__

```python
def __init__(self, town_persistence: TownPersistence) -> None
```

Initialize CitizenNode.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `world.town.citizen.manifest`

Manifest citizen registry overview.

---

## services.town.coalition_node

## coalition_node

```python
module coalition_node
```

Coalition AGENTESE Node: @node("world.town.coalition")

---

## CoalitionManifestRendering

```python
class CoalitionManifestRendering
```

Rendering for coalition system manifest.

---

## CoalitionRendering

```python
class CoalitionRendering
```

Rendering for coalition details.

---

## CoalitionListRendering

```python
class CoalitionListRendering
```

Rendering for coalition list.

---

## CoalitionNode

```python
class CoalitionNode(BaseLogosNode)
```

AGENTESE node for Coalition Detection Crown Jewel.

---

## __init__

```python
def __init__(self, coalition_service: CoalitionService) -> None
```

Initialize CoalitionNode.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `world.town.coalition.manifest`

Manifest coalition system status to observer.

---

## services.town.coalition_service

## coalition_service

```python
module coalition_service
```

Town Coalition Service: Coalition Detection and Reputation System.

---

## Coalition

```python
class Coalition
```

A coalition is a group of citizens with aligned eigenvectors.

---

## find_k_cliques

```python
def find_k_cliques(adjacency: dict[str, set[str]], k: int=3) -> list[frozenset[str]]
```

Find all k-cliques in an adjacency graph.

---

## percolate_cliques

```python
def percolate_cliques(cliques: list[frozenset[str]], k: int=3) -> list[set[str]]
```

Percolate k-cliques to find overlapping communities.

---

## detect_coalitions

```python
def detect_coalitions(citizens: dict[str, 'Citizen'], similarity_threshold: float=0.8, k: int=3) -> list[Coalition]
```

Detect coalitions via k-clique percolation on eigenvector similarity.

---

## ReputationGraph

```python
class ReputationGraph
```

EigenTrust-style reputation graph.

---

## CoalitionService

```python
class CoalitionService
```

Service for managing coalition lifecycle and reputation.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize defaults.

---

## size

```python
def size(self) -> int
```

Number of members.

---

## add_member

```python
def add_member(self, citizen_id: str) -> None
```

Add a member to the coalition.

---

## remove_member

```python
def remove_member(self, citizen_id: str) -> None
```

Remove a member from the coalition.

---

## compute_centroid

```python
def compute_centroid(self, citizens: dict[str, 'Citizen']) -> 'Eigenvectors'
```

Compute the centroid eigenvector of the coalition.

---

## decay

```python
def decay(self, rate: float=0.05) -> None
```

Apply decay to coalition strength.

---

## reinforce

```python
def reinforce(self, amount: float=0.1) -> None
```

Reinforce coalition strength (from collective action).

---

## is_alive

```python
def is_alive(self, threshold: float=0.1) -> bool
```

Check if coalition is still alive.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Coalition
```

Deserialize from dictionary.

---

## set_trust

```python
def set_trust(self, truster: str, trustee: str, value: float) -> None
```

Set local trust from truster to trustee.

---

## get_trust

```python
def get_trust(self, truster: str, trustee: str) -> float
```

Get local trust from truster to trustee.

---

## add_pretrusted

```python
def add_pretrusted(self, citizen_id: str) -> None
```

Mark a citizen as pre-trusted (anchor for convergence).

---

## get_reputation

```python
def get_reputation(self, citizen_id: str) -> float
```

Get global reputation for a citizen.

---

## compute_reputation

```python
def compute_reputation(self, citizens: dict[str, 'Citizen'], alpha: float=0.5, iterations: int=20, epsilon: float=0.001) -> dict[str, float]
```

Compute global reputation via EigenTrust power iteration.

---

## update_from_interaction

```python
def update_from_interaction(self, truster: str, trustee: str, success: bool, weight: float=0.1) -> None
```

Update local trust based on interaction outcome.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> ReputationGraph
```

Deserialize from dictionary.

---

## __init__

```python
def __init__(self, similarity_threshold: float=0.8, k: int=3) -> None
```

Initialize coalition service.

---

## coalitions

```python
def coalitions(self) -> dict[str, Coalition]
```

Get all coalitions.

---

## reputation

```python
def reputation(self) -> ReputationGraph
```

Get reputation graph.

---

## detect

```python
def detect(self, citizens: dict[str, 'Citizen']) -> list[Coalition]
```

Detect coalitions and update internal state.

---

## get_coalition

```python
def get_coalition(self, coalition_id: str) -> Coalition | None
```

Get a coalition by ID.

---

## get_citizen_coalitions

```python
def get_citizen_coalitions(self, citizen_id: str) -> list[Coalition]
```

Get all coalitions a citizen belongs to.

---

## get_bridge_citizens

```python
def get_bridge_citizens(self) -> list[str]
```

Get citizens that belong to multiple coalitions (bridge nodes).

---

## decay_all

```python
def decay_all(self, rate: float=0.05) -> int
```

Apply decay to all coalitions. Returns number pruned.

---

## reinforce_coalition

```python
def reinforce_coalition(self, coalition_id: str, amount: float=0.1) -> bool
```

Reinforce a coalition's strength.

---

## record_interaction

```python
def record_interaction(self, actor: str, target: str, success: bool) -> None
```

Record an interaction for reputation updates.

---

## compute_reputation

```python
def compute_reputation(self, citizens: dict[str, 'Citizen'], alpha: float=0.5) -> dict[str, float]
```

Compute global reputation scores.

---

## summary

```python
def summary(self) -> dict[str, Any]
```

Get summary statistics.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize service state.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> CoalitionService
```

Deserialize service state.

---

## services.town.collective_node

## collective_node

```python
module collective_node
```

Collective AGENTESE Node: @node("world.town.collective")

---

## CollectiveManifestResponse

```python
class CollectiveManifestResponse
```

Response for collective manifest.

---

## GossipRequest

```python
class GossipRequest
```

Request to spread gossip.

---

## GossipResponse

```python
class GossipResponse
```

Response after spreading gossip.

---

## EmergenceResponse

```python
class EmergenceResponse
```

Response for emergence metrics.

---

## ActivitySummary

```python
class ActivitySummary
```

Summary of activity in a region.

---

## ActivityResponse

```python
class ActivityResponse
```

Response for region activity.

---

## SimulationStepRequest

```python
class SimulationStepRequest
```

Request to advance simulation.

---

## SimulationStepResponse

```python
class SimulationStepResponse
```

Response after simulation step.

---

## CollectiveManifestRendering

```python
class CollectiveManifestRendering
```

Rendering for collective manifest.

---

## EmergenceRendering

```python
class EmergenceRendering
```

Rendering for emergence metrics.

---

## CollectiveNode

```python
class CollectiveNode(BaseLogosNode)
```

AGENTESE node for Collective Town operations.

---

## __init__

```python
def __init__(self, sheaf: TownSheaf | None=None, bus_manager: TownBusManager | None=None) -> None
```

Initialize CollectiveNode.

---

## set_citizen_location

```python
def set_citizen_location(self, citizen_id: str, region: str) -> None
```

Update citizen location.

---

## record_conversation

```python
def record_conversation(self, region: str) -> None
```

Record a conversation in a region.

---

## get_region_views

```python
def get_region_views(self) -> dict[TownContext, RegionView]
```

Build region views from current state.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `world.town.collective.manifest`

Manifest collective status.

---

## services.town.contracts

## contracts

```python
module contracts
```

Town AGENTESE Contract Definitions.

---

## TownManifestResponse

```python
class TownManifestResponse
```

Town health status manifest response.

---

## CitizenSummary

```python
class CitizenSummary
```

Summary of a citizen for list views.

---

## CitizenDetail

```python
class CitizenDetail
```

Full citizen details.

---

## CitizenListResponse

```python
class CitizenListResponse
```

Response for citizen list aspect.

---

## CitizenGetResponse

```python
class CitizenGetResponse
```

Response for citizen get aspect.

---

## CitizenCreateRequest

```python
class CitizenCreateRequest
```

Request to create a new citizen.

---

## CitizenCreateResponse

```python
class CitizenCreateResponse
```

Response after creating a citizen.

---

## CitizenUpdateRequest

```python
class CitizenUpdateRequest
```

Request to update a citizen.

---

## CitizenUpdateResponse

```python
class CitizenUpdateResponse
```

Response after updating a citizen.

---

## TurnSummary

```python
class TurnSummary
```

Summary of a conversation turn.

---

## ConversationDetail

```python
class ConversationDetail
```

Full conversation details.

---

## ConverseRequest

```python
class ConverseRequest
```

Request to start a conversation with a citizen.

---

## ConverseResponse

```python
class ConverseResponse
```

Response after starting a conversation.

---

## TurnRequest

```python
class TurnRequest
```

Request to add a turn to a conversation.

---

## TurnResponse

```python
class TurnResponse
```

Response after adding a turn.

---

## HistoryRequest

```python
class HistoryRequest
```

Request for dialogue history.

---

## ConversationSummary

```python
class ConversationSummary
```

Summary of a conversation for history views.

---

## HistoryResponse

```python
class HistoryResponse
```

Response for dialogue history.

---

## RelationshipSummary

```python
class RelationshipSummary
```

Summary of a citizen relationship.

---

## RelationshipsRequest

```python
class RelationshipsRequest
```

Request for citizen relationships.

---

## RelationshipsResponse

```python
class RelationshipsResponse
```

Response for citizen relationships.

---

## CoalitionManifestResponse

```python
class CoalitionManifestResponse
```

Coalition system health manifest response.

---

## CoalitionSummary

```python
class CoalitionSummary
```

Summary of a coalition for list views.

---

## CoalitionDetail

```python
class CoalitionDetail
```

Full coalition details.

---

## CoalitionListResponse

```python
class CoalitionListResponse
```

Response for coalition list aspect.

---

## CoalitionDetectRequest

```python
class CoalitionDetectRequest
```

Request to detect coalitions in citizen graph.

---

## CoalitionDetectResponse

```python
class CoalitionDetectResponse
```

Response after coalition detection.

---

## BridgeCitizensResponse

```python
class BridgeCitizensResponse
```

Response for bridge citizens aspect.

---

## CoalitionDecayResponse

```python
class CoalitionDecayResponse
```

Response after applying coalition decay.

---

## WorkshopStatusResponse

```python
class WorkshopStatusResponse
```

Response for workshop status aspect.

---

## WorkshopAssignRequest

```python
class WorkshopAssignRequest
```

Request to assign task to workshop builders.

---

## WorkshopAssignResponse

```python
class WorkshopAssignResponse
```

Response after workshop task assignment.

---

## WorkshopEventResponse

```python
class WorkshopEventResponse
```

Response for workshop event (advance, complete).

---

## WorkshopBuildersResponse

```python
class WorkshopBuildersResponse
```

Response listing available builders.

---

## OperationSummary

```python
class OperationSummary
```

Summary of a town operation.

---

## ScenarioConfig

```python
class ScenarioConfig
```

Configuration for a town scenario.

---

## ScenarioStatusResponse

```python
class ScenarioStatusResponse
```

Response for scenario status aspect.

---

## services.town.dialogue_service

## dialogue_service

```python
module dialogue_service
```

Town Dialogue Service: LLM-backed dialogue generation for Agent Town citizens.

---

## DialogueTier

```python
class DialogueTier(Enum)
```

Citizen dialogue budget tiers.

---

## DialogueContext

```python
class DialogueContext
```

Memory-grounded context for dialogue generation.

---

## DialogueResult

```python
class DialogueResult
```

Result from dialogue generation.

---

## CitizenBudget

```python
class CitizenBudget
```

Per-citizen token tracking.

---

## DialogueBudgetConfig

```python
class DialogueBudgetConfig
```

Per-citizen token budget configuration.

---

## DialogueService

```python
class DialogueService
```

LLM-backed dialogue generation service for Agent Town citizens.

---

## create_dialogue_service

```python
def create_dialogue_service(use_mock: bool=False, budget_config: DialogueBudgetConfig | None=None) -> DialogueService
```

Create a DialogueService with appropriate LLM client.

---

## to_context_string

```python
def to_context_string(self) -> str
```

Render context for prompt injection.

---

## tokens_remaining

```python
def tokens_remaining(self) -> int
```

Tokens remaining for today.

---

## can_afford

```python
def can_afford(self, estimated_tokens: int) -> bool
```

Check if budget allows this operation.

---

## spend

```python
def spend(self, tokens: int) -> None
```

Record token expenditure.

---

## reset_if_new_day

```python
def reset_if_new_day(self) -> None
```

Reset budget if it's a new day.

---

## model_for_operation

```python
def model_for_operation(self, operation: str) -> str
```

Get model name for an operation.

---

## estimate_tokens

```python
def estimate_tokens(self, operation: str) -> int
```

Estimate token cost for an operation.

---

## budget_for_tier

```python
def budget_for_tier(self, tier: str) -> int
```

Get daily budget for a citizen tier.

---

## has_llm

```python
def has_llm(self) -> bool
```

Check if LLM client is configured.

---

## register_citizen

```python
def register_citizen(self, citizen_id: str, tier: str) -> CitizenBudget
```

Register a citizen for budget tracking.

---

## get_budget

```python
def get_budget(self, citizen_id: str) -> CitizenBudget | None
```

Get a citizen's budget tracker.

---

## get_tier

```python
def get_tier(self, citizen: 'Citizen') -> DialogueTier
```

Determine dialogue tier for a citizen based on budget.

---

## generate

```python
async def generate(self, speaker: 'Citizen', listener: 'Citizen', operation: str, phase: 'TownPhase | None'=None, recent_events: list[str] | None=None) -> DialogueResult
```

Generate dialogue for an interaction.

---

## generate_stream

```python
async def generate_stream(self, speaker: 'Citizen', listener: 'Citizen', operation: str, phase: 'TownPhase | None'=None, recent_events: list[str] | None=None) -> AsyncIterator[Union[str, DialogueResult]]
```

Generate dialogue with streaming.

---

## get_stats

```python
def get_stats(self) -> dict[str, Any]
```

Get service statistics.

---

## services.town.events

## events

```python
module events
```

Town Event Definitions: DataEvent subclasses for Agent Town.

---

## TownEventType

```python
class TownEventType(Enum)
```

Types of town events.

---

## TownEvent

```python
class TownEvent
```

Base class for all town events.

---

## CitizenCreated

```python
class CitizenCreated(TownEvent)
```

Emitted when a new citizen is created.

---

## CitizenUpdated

```python
class CitizenUpdated(TownEvent)
```

Emitted when a citizen's attributes change.

---

## CitizenDeactivated

```python
class CitizenDeactivated(TownEvent)
```

Emitted when a citizen is deactivated.

---

## ConversationStarted

```python
class ConversationStarted(TownEvent)
```

Emitted when a conversation begins.

---

## ConversationTurn

```python
class ConversationTurn(TownEvent)
```

Emitted when a turn is added to a conversation.

---

## ConversationEnded

```python
class ConversationEnded(TownEvent)
```

Emitted when a conversation ends.

---

## RelationshipCreated

```python
class RelationshipCreated(TownEvent)
```

Emitted when a new relationship forms.

---

## RelationshipChanged

```python
class RelationshipChanged(TownEvent)
```

Emitted when a relationship strength changes.

---

## GossipSpread

```python
class GossipSpread(TownEvent)
```

Emitted when gossip spreads between citizens.

---

## CoalitionFormed

```python
class CoalitionFormed(TownEvent)
```

Emitted when a coalition is detected/formed.

---

## CoalitionDissolved

```python
class CoalitionDissolved(TownEvent)
```

Emitted when a coalition dissolves.

---

## InhabitStarted

```python
class InhabitStarted(TownEvent)
```

Emitted when a user starts inhabiting a citizen.

---

## InhabitEnded

```python
class InhabitEnded(TownEvent)
```

Emitted when a user stops inhabiting a citizen.

---

## ForceApplied

```python
class ForceApplied(TownEvent)
```

Emitted when a user forces a citizen action.

---

## SimulationStep

```python
class SimulationStep(TownEvent)
```

Emitted when a simulation step completes.

---

## RegionActivity

```python
class RegionActivity(TownEvent)
```

Emitted when significant activity happens in a region.

---

## TownTopics

```python
class TownTopics
```

SynergyBus topic constants for town events.

---

## create

```python
def create(cls, citizen_id: str, name: str, archetype: str, region: str='inn', traits: dict[str, Any] | None=None, causal_parent: str | None=None) -> CitizenCreated
```

Factory for creating CitizenCreated events.

---

## create

```python
def create(cls, citizen_id: str, changes: dict[str, Any], causal_parent: str | None=None) -> CitizenUpdated
```

Factory for creating CitizenUpdated events.

---

## create

```python
def create(cls, citizen_id: str, reason: str='manual', causal_parent: str | None=None) -> CitizenDeactivated
```

Factory for creating CitizenDeactivated events.

---

## create

```python
def create(cls, conversation_id: str, citizen_id: str, topic: str='', causal_parent: str | None=None) -> ConversationStarted
```

Factory for creating ConversationStarted events.

---

## create

```python
def create(cls, conversation_id: str, citizen_id: str, turn_number: int, role: str, content: str, sentiment: str | None=None, emotion: str | None=None, causal_parent: str | None=None) -> ConversationTurn
```

Factory for creating ConversationTurn events.

---

## create

```python
def create(cls, conversation_id: str, citizen_id: str, turn_count: int, summary: str='', causal_parent: str | None=None) -> ConversationEnded
```

Factory for creating ConversationEnded events.

---

## create

```python
def create(cls, relationship_id: str, citizen_a: str, citizen_b: str, relationship_type: str, initial_strength: float=0.5, causal_parent: str | None=None) -> RelationshipCreated
```

Factory for creating RelationshipCreated events.

---

## create

```python
def create(cls, relationship_id: str, citizen_a: str, citizen_b: str, old_strength: float, new_strength: float, reason: str='interaction', causal_parent: str | None=None) -> RelationshipChanged
```

Factory for creating RelationshipChanged events.

---

## create

```python
def create(cls, source_citizen: str, target_citizen: str, rumor_content: str, accuracy: float=1.0, source_region: str='', target_region: str='', causal_parent: str | None=None) -> GossipSpread
```

Factory for creating GossipSpread events.

---

## create

```python
def create(cls, coalition_id: str, members: set[str] | frozenset[str], purpose: str='', strength: float=1.0, causal_parent: str | None=None) -> CoalitionFormed
```

Factory for creating CoalitionFormed events.

---

## create

```python
def create(cls, coalition_id: str, members: set[str] | frozenset[str], reason: str='decay', causal_parent: str | None=None) -> CoalitionDissolved
```

Factory for creating CoalitionDissolved events.

---

## create

```python
def create(cls, user_id: str, citizen_id: str, inhabit_mode: str='basic', causal_parent: str | None=None) -> InhabitStarted
```

Factory for creating InhabitStarted events.

---

## create

```python
def create(cls, user_id: str, citizen_id: str, duration_seconds: float, actions_taken: int=0, causal_parent: str | None=None) -> InhabitEnded
```

Factory for creating InhabitEnded events.

---

## create

```python
def create(cls, user_id: str, citizen_id: str, action: str, severity: float=0.2, debt_after: float=0.0, causal_parent: str | None=None) -> ForceApplied
```

Factory for creating ForceApplied events.

---

## create

```python
def create(cls, step_number: int, active_citizens: int, interactions: int=0, coalitions_changed: int=0, causal_parent: str | None=None) -> SimulationStep
```

Factory for creating SimulationStep events.

---

## create

```python
def create(cls, region: str, citizen_count: int, activity_type: str, details: str='', causal_parent: str | None=None) -> RegionActivity
```

Factory for creating RegionActivity events.

---

## services.town.inhabit_node

## inhabit_node

```python
module inhabit_node
```

Town INHABIT AGENTESE Node: @node("world.town.inhabit")

---

## InhabitSessionRendering

```python
class InhabitSessionRendering
```

Rendering for INHABIT session status.

---

## InhabitActionRendering

```python
class InhabitActionRendering
```

Rendering for INHABIT action results.

---

## InhabitListRendering

```python
class InhabitListRendering
```

Rendering for active sessions list.

---

## InhabitNode

```python
class InhabitNode(BaseLogosNode)
```

AGENTESE node for INHABIT Crown Jewel feature.

---

## __init__

```python
def __init__(self, inhabit_service: InhabitService, citizen_resolver: Any=None) -> None
```

Initialize InhabitNode.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `world.town.inhabit.manifest`

Manifest INHABIT status overview.

---

## services.town.inhabit_service

## inhabit_service

```python
module inhabit_service
```

Town INHABIT Service: User-Citizen merge with consent tracking.

---

## InhabitTier

```python
class InhabitTier(Enum)
```

User subscription tiers with different INHABIT privileges.

---

## AlignmentScore

```python
class AlignmentScore
```

How well an action aligns with citizen's personality.

---

## InhabitResponse

```python
class InhabitResponse
```

Response from an INHABIT action.

---

## InhabitSession

```python
class InhabitSession
```

An INHABIT session where user merges with a citizen.

---

## calculate_alignment

```python
async def calculate_alignment(citizen: 'Citizen', proposed_action: str, llm_client: Any) -> AlignmentScore
```

Evaluate action alignment against citizen's personality.

---

## generate_inner_voice

```python
async def generate_inner_voice(citizen: 'Citizen', situation: str, llm_client: Any) -> tuple[str, int]
```

Generate citizen's inner thoughts for a situation.

---

## InhabitService

```python
class InhabitService
```

Service for managing INHABIT sessions.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Set tier-specific caps and initialize consent state.

---

## update

```python
def update(self) -> None
```

Update session timing and consent decay.

---

## is_expired

```python
def is_expired(self) -> bool
```

Check if session has exceeded time limit.

---

## check_session_expired

```python
def check_session_expired(self) -> bool
```

Check if session has exceeded its time limit.

---

## time_remaining

```python
def time_remaining(self) -> float
```

Get remaining time in seconds.

---

## can_force

```python
def can_force(self) -> bool
```

Check if force action is allowed.

---

## force_action

```python
def force_action(self, action: str, severity: float=0.2) -> dict[str, Any]
```

Force the citizen to perform an action.

---

## suggest_action

```python
def suggest_action(self, action: str) -> dict[str, Any]
```

Suggest an action to the citizen (collaborative, not forced).

---

## apologize

```python
def apologize(self, sincerity: float=0.3) -> dict[str, Any]
```

Apologize to the citizen, reducing consent debt.

---

## get_status

```python
def get_status(self) -> dict[str, Any]
```

Get session status for display.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize session to dictionary (for logging/audit).

---

## emit_inhabit_event

```python
def emit_inhabit_event(self, response: InhabitResponse) -> dict[str, Any]
```

Create an INHABIT event for TownFlux integration.

---

## start_session

```python
def start_session(self, user_id: str, citizen: 'Citizen', tier: InhabitTier, force_enabled: bool=False) -> InhabitSession
```

Start a new INHABIT session.

---

## get_session

```python
def get_session(self, user_id: str) -> InhabitSession | None
```

Get a user's active session.

---

## end_session

```python
def end_session(self, user_id: str) -> dict[str, Any] | None
```

End a user's session gracefully.

---

## list_active_sessions

```python
def list_active_sessions(self) -> list[dict[str, Any]]
```

List all active sessions.

---

## services.town.memory_service

## memory_service

```python
module memory_service
```

Town Memory Service: Citizen episodic and collective memory.

---

## ConversationEntry

```python
class ConversationEntry
```

A single conversation turn.

---

## PersistentCitizenMemory

```python
class PersistentCitizenMemory
```

Persistent memory for a citizen using D-gent.

---

## CollectiveEvent

```python
class CollectiveEvent
```

A town-wide event that citizens can reference.

---

## TownCollectiveMemory

```python
class TownCollectiveMemory
```

Shared memory for the entire town using D-gent.

---

## create_collective_memory

```python
async def create_collective_memory(town_id: str, dgent: DgentProtocol | None=None) -> TownCollectiveMemory
```

Create and load collective memory for a town.

---

## create_persistent_memory

```python
async def create_persistent_memory(citizen: 'Citizen', dgent: DgentProtocol | None=None) -> PersistentCitizenMemory
```

Create and load persistent memory for a citizen.

---

## save_citizen_state

```python
async def save_citizen_state(citizen: 'Citizen', memory: PersistentCitizenMemory) -> None
```

Save a citizen's full state to persistent memory.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> ConversationEntry
```

Deserialize from dictionary.

---

## __init__

```python
def __init__(self, citizen_id: str, dgent: DgentProtocol | None=None) -> None
```

Initialize persistent memory for a citizen.

---

## citizen_id

```python
def citizen_id(self) -> str
```

The citizen this memory belongs to.

---

## namespace

```python
def namespace(self) -> str
```

D-gent namespace prefix.

---

## load

```python
async def load(self) -> None
```

Load memory from D-gent on startup.

---

## save

```python
async def save(self) -> None
```

Persist current memory state to D-gent.

---

## graph

```python
def graph(self) -> GraphMemory
```

Access the graph memory (lazy initialization).

---

## store_memory

```python
async def store_memory(self, key: str, content: str, connections: dict[str, float] | None=None, metadata: dict[str, Any] | None=None) -> None
```

Store an episodic memory.

---

## recall_memory

```python
async def recall_memory(self, query: str, k_hops: int=2) -> list[dict[str, Any]]
```

Recall memories by graph traversal.

---

## recall_by_content

```python
async def recall_by_content(self, substring: str, k_hops: int=2) -> list[dict[str, Any]]
```

Recall memories by content search.

---

## reinforce_memory

```python
async def reinforce_memory(self, key: str, amount: float=0.1) -> bool
```

Reinforce a memory (increase strength).

---

## decay_memories

```python
async def decay_memories(self, rate: float | None=None) -> int
```

Apply decay to all memories.

---

## conversations

```python
def conversations(self) -> list[ConversationEntry]
```

All conversation entries.

---

## add_conversation

```python
async def add_conversation(self, speaker: str, message: str, topic: str | None=None, emotion: str | None=None, eigenvector_deltas: dict[str, float] | None=None) -> ConversationEntry
```

Add a conversation entry.

---

## get_recent_conversations

```python
async def get_recent_conversations(self, limit: int=10, topic: str | None=None) -> list[ConversationEntry]
```

Get recent conversations.

---

## search_conversations

```python
async def search_conversations(self, query: str) -> list[ConversationEntry]
```

Search conversations by content.

---

## save_relationships

```python
async def save_relationships(self, relationships: dict[str, float]) -> None
```

Save relationship weights to D-gent.

---

## load_relationships

```python
async def load_relationships(self) -> dict[str, float]
```

Load relationship weights from D-gent.

---

## save_eigenvectors

```python
async def save_eigenvectors(self, eigenvectors: dict[str, float]) -> None
```

Save current eigenvector snapshot with timestamp.

---

## get_eigenvector_drift

```python
async def get_eigenvector_drift(self, window_size: int=10) -> dict[str, float] | None
```

Calculate eigenvector drift over recent history.

---

## clear

```python
async def clear(self) -> None
```

Clear all memory (graph, conversations, relationships).

---

## memory_summary

```python
def memory_summary(self) -> dict[str, Any]
```

Get a summary of this citizen's memory.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Serialize to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> CollectiveEvent
```

Deserialize from dictionary.

---

## __init__

```python
def __init__(self, town_id: str, dgent: DgentProtocol | None=None, max_events: int=100) -> None
```

Initialize collective memory.

---

## load

```python
async def load(self) -> None
```

Load collective memory from D-gent.

---

## record_event

```python
async def record_event(self, event_type: str, content: str, participants: list[str] | None=None, metadata: dict[str, Any] | None=None) -> CollectiveEvent
```

Record a town-wide event.

---

## get_recent_events

```python
async def get_recent_events(self, limit: int=10, event_type: str | None=None) -> list[CollectiveEvent]
```

Get recent town events.

---

## get_events_involving

```python
async def get_events_involving(self, citizen_id: str, limit: int=5) -> list[CollectiveEvent]
```

Get events involving a specific citizen.

---

## get_shared_context

```python
async def get_shared_context(self, citizen_ids: list[str] | None=None, limit: int=5) -> list[CollectiveEvent]
```

Get shared context for dialogue grounding.

---

## summary

```python
def summary(self) -> dict[str, Any]
```

Get a summary of collective memory state.

---

## services.town.node

## node

```python
module node
```

Town AGENTESE Node: @node("world.town")

---

## TownManifestRendering

```python
class TownManifestRendering
```

Rendering for town status manifest.

---

## CitizenRendering

```python
class CitizenRendering
```

Rendering for citizen details.

---

## CitizenListRendering

```python
class CitizenListRendering
```

Rendering for citizen list.

---

## ConversationRendering

```python
class ConversationRendering
```

Rendering for conversation details.

---

## RelationshipListRendering

```python
class RelationshipListRendering
```

Rendering for relationship list.

---

## TownNode

```python
class TownNode(BaseLogosNode)
```

AGENTESE node for Agent Town Crown Jewel.

---

## __init__

```python
def __init__(self, town_persistence: TownPersistence) -> None
```

Initialize TownNode.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `world.town.manifest`

Manifest town status to observer.

---

## services.town.persistence

## persistence

```python
module persistence
```

Town Persistence: TableAdapter + D-gent integration for Agent Town Crown Jewel.

---

## CitizenView

```python
class CitizenView
```

View of a citizen for external consumption.

---

## ConversationView

```python
class ConversationView
```

View of a conversation.

---

## TurnView

```python
class TurnView
```

View of a conversation turn.

---

## RelationshipView

```python
class RelationshipView
```

View of a citizen relationship.

---

## TownStatus

```python
class TownStatus
```

Town health status.

---

## TownPersistence

```python
class TownPersistence
```

Persistence layer for Agent Town Crown Jewel.

---

## create_citizen

```python
async def create_citizen(self, name: str, archetype: str, description: str | None=None, traits: dict[str, Any] | None=None) -> CitizenView
```

**AGENTESE:** `world.town.citizen.define`

Create a new citizen in the town.

---

## get_citizen

```python
async def get_citizen(self, citizen_id: str) -> CitizenView | None
```

Get a citizen by ID.

---

## get_citizen_by_name

```python
async def get_citizen_by_name(self, name: str) -> CitizenView | None
```

Get a citizen by name.

---

## list_citizens

```python
async def list_citizens(self, active_only: bool=False, archetype: str | None=None, limit: int=50) -> list[CitizenView]
```

List citizens with optional filters.

---

## update_citizen

```python
async def update_citizen(self, citizen_id: str, description: str | None=None, traits: dict[str, Any] | None=None, is_active: bool | None=None) -> CitizenView | None
```

Update citizen attributes.

---

## start_conversation

```python
async def start_conversation(self, citizen_id: str, topic: str | None=None) -> ConversationView | None
```

**AGENTESE:** `world.town.citizen.`

Start a new conversation with a citizen.

---

## add_turn

```python
async def add_turn(self, conversation_id: str, role: str, content: str, sentiment: str | None=None, emotion: str | None=None) -> TurnView | None
```

Add a turn to a conversation.

---

## get_conversation

```python
async def get_conversation(self, conversation_id: str, include_turns: bool=True) -> ConversationView | None
```

Get a conversation with optional turns.

---

## end_conversation

```python
async def end_conversation(self, conversation_id: str, summary: str | None=None) -> bool
```

End an active conversation.

---

## get_dialogue_history

```python
async def get_dialogue_history(self, citizen_id: str, limit: int=50) -> list[ConversationView]
```

**AGENTESE:** `world.town.citizen.`

Get dialogue history for a citizen.

---

## create_relationship

```python
async def create_relationship(self, citizen_a_id: str, citizen_b_id: str, relationship_type: str, strength: float=0.5, notes: str | None=None) -> RelationshipView | None
```

Create a relationship between two citizens.

---

## get_relationships

```python
async def get_relationships(self, citizen_id: str) -> list[RelationshipView]
```

Get all relationships for a citizen.

---

## manifest

```python
async def manifest(self) -> TownStatus
```

**AGENTESE:** `world.town.manifest`

Get town health status.

---

## services.town.workshop_node

## workshop_node

```python
module workshop_node
```

Workshop AGENTESE Node: @node("world.town.workshop")

---

## WorkshopManifestRendering

```python
class WorkshopManifestRendering
```

Rendering for workshop status manifest.

---

## WorkshopBuildersRendering

```python
class WorkshopBuildersRendering
```

Rendering for builder list.

---

## WorkshopNode

```python
class WorkshopNode(BaseLogosNode)
```

AGENTESE node for Workshop Crown Jewel.

---

## __init__

```python
def __init__(self, workshop_service: WorkshopService) -> None
```

Initialize WorkshopNode.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `world.town.workshop.manifest`

Manifest workshop status to observer.

---

## services.town.workshop_service

## workshop_service

```python
module workshop_service
```

Workshop Service: Builder coordination for Town Crown Jewel.

---

## WorkshopView

```python
class WorkshopView
```

View of workshop status for API/CLI rendering.

---

## WorkshopTaskView

```python
class WorkshopTaskView
```

View of a workshop task.

---

## WorkshopPlanView

```python
class WorkshopPlanView
```

View of a workshop plan.

---

## WorkshopEventView

```python
class WorkshopEventView
```

View of a workshop event.

---

## WorkshopFluxView

```python
class WorkshopFluxView
```

View of flux execution status.

---

## WorkshopService

```python
class WorkshopService
```

Service layer for Workshop operations.

---

## create_workshop_service

```python
def create_workshop_service(builders: tuple['Builder', ...] | None=None, event_bus: 'EventBus[WorkshopEvent] | None'=None, dialogue_engine: 'CitizenDialogueEngine | None'=None) -> WorkshopService
```

Create a configured WorkshopService.

---

## __init__

```python
def __init__(self, workshop: WorkshopEnvironment | None=None, dialogue_engine: 'CitizenDialogueEngine | None'=None) -> None
```

Initialize workshop service.

---

## workshop

```python
def workshop(self) -> WorkshopEnvironment
```

Underlying workshop environment.

---

## is_active

```python
def is_active(self) -> bool
```

Check if workshop has an active task.

---

## manifest

```python
async def manifest(self, lod: int=1) -> WorkshopView
```

**AGENTESE:** `world.town.workshop.manifest`

Get workshop status.

---

## assign_task

```python
async def assign_task(self, task: str | WorkshopTask, priority: int=1) -> WorkshopPlanView
```

**AGENTESE:** `world.town.workshop.assign`

Assign a task to the workshop.

---

## advance

```python
async def advance(self) -> WorkshopEventView
```

**AGENTESE:** `world.town.workshop.advance`

Advance the workshop by one step.

---

## complete

```python
async def complete(self, summary: str='') -> WorkshopEventView
```

**AGENTESE:** `world.town.workshop.complete`

Mark the current task as complete.

---

## handoff

```python
async def handoff(self, from_archetype: str, to_archetype: str, artifact: Any=None, message: str='') -> WorkshopEventView
```

Explicit handoff between builders.

---

## reset

```python
def reset(self) -> None
```

Reset workshop to idle state.

---

## create_flux

```python
def create_flux(self, nphase_session: 'NPhaseSession | None'=None, auto_advance: bool=True, max_steps_per_phase: int=5, seed: int | None=None) -> WorkshopFlux
```

Create a WorkshopFlux for streaming execution.

---

## run_task

```python
async def run_task(self, task: str | WorkshopTask, priority: int=1, nphase_session: 'NPhaseSession | None'=None) -> AsyncIterator[WorkshopEventView]
```

Run a task to completion with streaming events.

---

## get_flux_status

```python
def get_flux_status(self) -> WorkshopFluxView | None
```

Get current flux status if active.

---

## get_metrics

```python
def get_metrics(self) -> WorkshopMetrics | None
```

Get flux execution metrics.

---

## get_builder

```python
def get_builder(self, archetype: str) -> 'Builder | None'
```

Get a builder by archetype name.

---

## list_builders

```python
def list_builders(self) -> list[str]
```

List all builder archetypes.

---

## services.verification.__init__

## __init__

```python
module __init__
```

Verification Crown Jewel: Formal Verification Metatheory System.

---

## services.verification.aesthetic

## aesthetic

```python
module aesthetic
```

Alive Workshop Aesthetic: Sympathetic error handling with Studio Ghibli warmth.

---

## ErrorCategory

```python
class ErrorCategory(str, Enum)
```

Categories of verification errors.

---

## Severity

```python
class Severity(str, Enum)
```

Error severity levels.

---

## LivingEarthPalette

```python
class LivingEarthPalette
```

Color palette inspired by Studio Ghibli's living worlds.

---

## VerificationError

```python
class VerificationError
```

Sympathetic error with learning opportunities.

---

## celebrate_success

```python
def celebrate_success(verification_type: str) -> str
```

Get a celebration message for successful verification.

---

## ProgressiveResult

```python
class ProgressiveResult
```

Result with progressive disclosure levels.

---

## create_progressive_result

```python
def create_progressive_result(success: bool, verification_type: str, details: dict[str, Any] | None=None, error: VerificationError | None=None) -> ProgressiveResult
```

Create a progressive result from verification outcome.

---

## title

```python
def title(self) -> str
```

Get sympathetic title for this error.

---

## message

```python
def message(self) -> str
```

Get sympathetic message for this error.

---

## encouragement

```python
def encouragement(self) -> str
```

Get encouraging follow-up message.

---

## educational_content

```python
def educational_content(self) -> str | None
```

Get educational content for this error type.

---

## format_for_display

```python
def format_for_display(self, verbose: bool=False) -> str
```

Format error for human-readable display.

---

## at_level

```python
def at_level(self, level: int) -> str
```

Get result at specified disclosure level (0-3).

---

## services.verification.agentese_nodes

## agentese_nodes

```python
module agentese_nodes
```

AGENTESE Integration: Verification system nodes for the AGENTESE protocol.

---

## manifest_verification_status

```python
async def manifest_verification_status(umwelt: Umwelt) -> dict[str, Any]
```

Manifest the current state of the verification system.

---

## analyze_specification

```python
async def analyze_specification(spec_path: str, umwelt: Umwelt) -> dict[str, Any]
```

Analyze a specification for consistency and principled derivation.

---

## verify_categorical_laws

```python
async def verify_categorical_laws(morphisms: list[dict[str, Any]], law_type: str, umwelt: Umwelt) -> dict[str, Any]
```

Verify categorical laws for agent morphisms.

---

## suggest_improvements

```python
async def suggest_improvements(umwelt: Umwelt) -> dict[str, Any]
```

Generate improvement suggestions based on trace analysis.

---

## capture_execution_trace

```python
async def capture_execution_trace(agent_path: str, execution_data: dict[str, Any], umwelt: Umwelt) -> dict[str, Any]
```

Capture an execution trace as a constructive proof.

---

## analyze_trace_corpus

```python
async def analyze_trace_corpus(pattern_type: str | None, umwelt: Umwelt) -> dict[str, Any]
```

Analyze the trace corpus for behavioral patterns.

---

## visualize_derivation_graph

```python
async def visualize_derivation_graph(graph_id: str, umwelt: Umwelt) -> dict[str, Any]
```

Visualize a derivation graph showing how implementation derives from principles.

---

## explore_derivation_path

```python
async def explore_derivation_path(principle_id: str, implementation_id: str, umwelt: Umwelt) -> dict[str, Any]
```

Explore the derivation path from a principle to an implementation.

---

## services.verification.categorical_checker

## categorical_checker

```python
module categorical_checker
```

Categorical Checker: Practical categorical law verification with LLM assistance.

---

## CategoricalChecker

```python
class CategoricalChecker
```

Practical categorical law verification with LLM assistance.

---

## verify_composition_associativity

```python
async def verify_composition_associativity(self, f: AgentMorphism, g: AgentMorphism, h: AgentMorphism) -> VerificationResult
```

Verify (f ∘ g) ∘ h ≡ f ∘ (g ∘ h) using practical testing.

---

## verify_identity_laws

```python
async def verify_identity_laws(self, f: AgentMorphism, identity: AgentMorphism) -> VerificationResult
```

Verify identity laws: f ∘ id = f and id ∘ f = f.

---

## verify_functor_laws

```python
async def verify_functor_laws(self, functor: AgentMorphism, f: AgentMorphism, g: AgentMorphism) -> VerificationResult
```

Verify functor laws: F(id) = id and F(g ∘ f) = F(g) ∘ F(f).

---

## verify_operad_coherence

```python
async def verify_operad_coherence(self, operad_operations: list[AgentMorphism], composition_rules: dict[str, Any]) -> VerificationResult
```

Verify operad coherence conditions.

---

## verify_sheaf_gluing

```python
async def verify_sheaf_gluing(self, local_sections: dict[str, Any], overlap_conditions: dict[str, Any]) -> VerificationResult
```

Verify sheaf gluing property.

---

## generate_counter_examples

```python
async def generate_counter_examples(self, law_name: str, morphisms: list[AgentMorphism], violation_hints: dict[str, Any] | None=None) -> list[CounterExample]
```

Generate concrete counter-examples for categorical law violations.

---

## suggest_remediation_strategies

```python
async def suggest_remediation_strategies(self, counter_examples: list[CounterExample], law_name: str) -> dict[str, Any]
```

Generate remediation strategies for categorical law violations.

---

## services.verification.contracts

## contracts

```python
module contracts
```

Verification Contracts: Data classes for formal verification system.

---

## VerificationStatus

```python
class VerificationStatus(str, Enum)
```

Status of verification operations.

---

## ViolationType

```python
class ViolationType(str, Enum)
```

Types of categorical law violations.

---

## ProposalStatus

```python
class ProposalStatus(str, Enum)
```

Status of improvement proposals.

---

## GraphNode

```python
class GraphNode
```

A node in the verification graph.

---

## GraphEdge

```python
class GraphEdge
```

An edge in the verification graph representing derivation.

---

## Contradiction

```python
class Contradiction
```

A contradiction detected in the verification graph.

---

## DerivationPath

```python
class DerivationPath
```

A path from principle to implementation.

---

## VerificationGraphResult

```python
class VerificationGraphResult
```

Result of verification graph analysis.

---

## AgentMorphism

```python
class AgentMorphism
```

An agent morphism for categorical verification.

---

## CounterExample

```python
class CounterExample
```

A counter-example for categorical law violation.

---

## VerificationResult

```python
class VerificationResult
```

Result of categorical law verification.

---

## SpecProperty

```python
class SpecProperty
```

A property that must hold for a specification.

---

## Specification

```python
class Specification
```

A formal specification with properties and constraints.

---

## ExecutionStep

```python
class ExecutionStep
```

A single step in agent execution.

---

## TraceWitnessResult

```python
class TraceWitnessResult
```

Result of trace witness verification.

---

## BehavioralPattern

```python
class BehavioralPattern
```

A behavioral pattern extracted from trace corpus.

---

## ImprovementProposalResult

```python
class ImprovementProposalResult
```

Result of improvement proposal generation.

---

## SemanticConsistencyResult

```python
class SemanticConsistencyResult
```

Result of semantic consistency analysis.

---

## HoTTTypeResult

```python
class HoTTTypeResult
```

Result of HoTT type representation.

---

## services.verification.generative_loop

## generative_loop

```python
module generative_loop
```

Generative Loop Engine: The closed cycle from intent to implementation and back.

---

## AGENTESEPath

```python
class AGENTESEPath
```

An AGENTESE path extracted from mind-map.

---

## OperadSpec

```python
class OperadSpec
```

An operad specification for composition grammar.

---

## AGENTESESpec

```python
class AGENTESESpec
```

AGENTESE specification extracted from mind-map.

---

## Module

```python
class Module
```

A generated implementation module.

---

## Implementation

```python
class Implementation
```

Generated implementation from spec.

---

## SpecChange

```python
class SpecChange
```

A change in specification.

---

## SpecDiff

```python
class SpecDiff
```

Difference between original and refined spec.

---

## RoundtripResult

```python
class RoundtripResult
```

Result of generative loop roundtrip.

---

## CompressionMorphism

```python
class CompressionMorphism
```

Extracts essential decisions from mind-map topology into AGENTESE spec.

---

## ImplementationProjector

```python
class ImplementationProjector
```

Projects AGENTESE specification into implementation code.

---

## PatternSynthesizer

```python
class PatternSynthesizer
```

Synthesizes behavioral patterns from accumulated traces.

---

## SpecDiffEngine

```python
class SpecDiffEngine
```

Compares original mind-map with patterns to detect drift.

---

## GenerativeLoop

```python
class GenerativeLoop
```

The closed generative cycle orchestrator.

---

## run_generative_loop

```python
async def run_generative_loop(mind_map: MindMapTopology) -> RoundtripResult
```

Convenience function to run the generative loop.

---

## compress_to_spec

```python
async def compress_to_spec(mind_map: MindMapTopology) -> AGENTESESpec
```

Convenience function to compress mind-map to spec.

---

## compress

```python
async def compress(self, topology: MindMapTopology) -> AGENTESESpec
```

Extract AGENTESE specification from mind-map topology.

---

## project

```python
async def project(self, spec: AGENTESESpec) -> Implementation
```

Generate implementation from specification.

---

## synthesize

```python
async def synthesize(self, traces: list[TraceWitnessResult]) -> list[BehavioralPattern]
```

Extract patterns from accumulated traces.

---

## diff

```python
async def diff(self, original: MindMapTopology, patterns: list[BehavioralPattern], spec: AGENTESESpec | None=None) -> SpecDiff
```

Identify divergence between original intent and observed behavior.

---

## compress

```python
async def compress(self, mind_map: MindMapTopology) -> AGENTESESpec
```

Extract essential decisions into AGENTESE spec.

---

## project

```python
async def project(self, spec: AGENTESESpec) -> Implementation
```

Generate implementation preserving composition structure.

---

## witness

```python
async def witness(self, implementation: Implementation) -> list[TraceWitnessResult]
```

Capture traces as constructive proofs.

---

## synthesize

```python
async def synthesize(self, traces: list[TraceWitnessResult]) -> list[BehavioralPattern]
```

Extract patterns from accumulated traces.

---

## diff

```python
async def diff(self, original: MindMapTopology, patterns: list[BehavioralPattern], spec: AGENTESESpec | None=None) -> SpecDiff
```

Identify divergence and propose updates.

---

## roundtrip

```python
async def roundtrip(self, mind_map: MindMapTopology) -> RoundtripResult
```

Full generative loop roundtrip.

---

## refine_spec

```python
async def refine_spec(self, original_spec: AGENTESESpec, patterns: list[BehavioralPattern], diff: SpecDiff) -> AGENTESESpec
```

Refine specification based on observed patterns and drift.

---

## services.verification.graph_engine

## graph_engine

```python
module graph_engine
```

Graph Engine: Derivation graph construction from specifications.

---

## GraphEngine

```python
class GraphEngine
```

Engine for constructing and analyzing verification graphs.

---

## build_graph_from_specification

```python
async def build_graph_from_specification(self, spec_path: str, name: str | None=None) -> VerificationGraphResult
```

Build verification graph from specification documents.

---

## generate_resolution_strategies

```python
async def generate_resolution_strategies(self, contradictions: list[Contradiction], orphaned_nodes: list[GraphNode]) -> dict[str, list[str]]
```

Generate resolution strategies for detected issues.

---

## services.verification.hott

## hott

```python
module hott
```

Homotopy Type Theory Foundation for Formal Verification.

---

## UniverseLevel

```python
class UniverseLevel(int, Enum)
```

Universe levels in the type hierarchy.

---

## PathType

```python
class PathType(str, Enum)
```

Types of paths (equality proofs) in HoTT.

---

## HoTTType

```python
class HoTTType
```

A type in Homotopy Type Theory.

---

## HoTTPath

```python
class HoTTPath
```

A path (proof of equality) in HoTT.

---

## Isomorphism

```python
class Isomorphism
```

An isomorphism between two structures.

---

## HoTTVerificationResult

```python
class HoTTVerificationResult
```

Result of HoTT-based verification.

---

## HoTTContext

```python
class HoTTContext
```

Homotopy Type Theory context for formal verification.

---

## verify_isomorphism

```python
async def verify_isomorphism(a: Any, b: Any, context: HoTTContext | None=None) -> bool
```

Convenience function to verify isomorphism.

---

## construct_equality_path

```python
async def construct_equality_path(a: Any, b: Any, context: HoTTContext | None=None) -> HoTTPath | None
```

Convenience function to construct equality path.

---

## are_isomorphic

```python
async def are_isomorphic(self, a: Any, b: Any) -> bool
```

Check if two structures are isomorphic.

---

## construct_path

```python
async def construct_path(self, a: Any, b: Any) -> HoTTPath | None
```

Construct a path (proof of equality) between a and b.

---

## services.verification.persistence

## persistence

```python
module persistence
```

Verification Persistence: Data access layer for formal verification system.

---

## VerificationPersistence

```python
class VerificationPersistence
```

Persistence layer for the formal verification system.

---

## create_verification_graph

```python
async def create_verification_graph(self, name: str, description: str | None=None, nodes: dict[str, Any] | None=None, edges: dict[str, Any] | None=None) -> VerificationGraphResult
```

Create a new verification graph.

---

## get_verification_graph

```python
async def get_verification_graph(self, graph_id: str) -> VerificationGraphResult | None
```

Get a verification graph by ID.

---

## update_graph_analysis

```python
async def update_graph_analysis(self, graph_id: str, contradictions: list[dict[str, Any]], orphaned_nodes: list[str], derivation_paths: dict[str, Any], status: VerificationStatus) -> None
```

Update graph analysis results.

---

## create_trace_witness

```python
async def create_trace_witness(self, agent_path: str, input_data: dict[str, Any], output_data: dict[str, Any], intermediate_steps: list[dict[str, Any]] | None=None, execution_id: str | None=None, specification_id: str | None=None) -> TraceWitnessResult
```

Create a new trace witness.

---

## get_trace_witness

```python
async def get_trace_witness(self, witness_id: str) -> TraceWitnessResult | None
```

Get a trace witness by ID.

---

## update_witness_verification

```python
async def update_witness_verification(self, witness_id: str, properties_verified: list[str], violations_found: list[dict[str, Any]], status: VerificationStatus) -> None
```

Update witness verification results.

---

## get_witnesses_by_agent

```python
async def get_witnesses_by_agent(self, agent_path: str, limit: int=100) -> list[TraceWitnessResult]
```

Get trace witnesses for a specific agent path.

---

## create_categorical_violation

```python
async def create_categorical_violation(self, violation_type: ViolationType, law_description: str, counter_example: CounterExample, llm_analysis: str | None=None, suggested_fix: str | None=None) -> str
```

Create a new categorical violation record.

---

## resolve_violation

```python
async def resolve_violation(self, violation_id: str, resolution_notes: str) -> None
```

Mark a categorical violation as resolved.

---

## create_improvement_proposal

```python
async def create_improvement_proposal(self, title: str, description: str, category: str, implementation_suggestion: str, risk_assessment: str, source_patterns: list[BehavioralPattern] | None=None, kgents_principle: str | None=None) -> ImprovementProposalResult
```

Create a new improvement proposal.

---

## update_proposal_validation

```python
async def update_proposal_validation(self, proposal_id: str, categorical_compliance: bool, trace_impact_analysis: dict[str, Any], llm_validation: str, status: ProposalStatus) -> None
```

Update proposal validation results.

---

## create_specification_document

```python
async def create_specification_document(self, name: str, document_type: str, file_path: str, concepts: list[str], semantic_hash: str, version: str='1.0.0') -> str
```

Create a new specification document record.

---

## analyze_semantic_consistency

```python
async def analyze_semantic_consistency(self, document_ids: list[str]) -> SemanticConsistencyResult
```

Analyze semantic consistency across documents.

---

## create_hott_type

```python
async def create_hott_type(self, name: str, universe_level: int, type_definition: dict[str, Any], introduction_rules: list[dict[str, Any]] | None=None, elimination_rules: list[dict[str, Any]] | None=None) -> HoTTTypeResult
```

Create a new HoTT type.

---

## services.verification.reflective_tower

## reflective_tower

```python
module reflective_tower
```

Reflective Tower: Level hierarchy with consistency verification.

---

## TowerLevel

```python
class TowerLevel(IntEnum)
```

Levels in the reflective tower.

---

## LevelArtifact

```python
class LevelArtifact
```

An artifact at a specific tower level.

---

## CompressionMorphism

```python
class CompressionMorphism
```

A morphism that compresses from higher to lower level.

---

## ConsistencyResult

```python
class ConsistencyResult
```

Result of consistency verification between levels.

---

## CorrectionProposal

```python
class CorrectionProposal
```

A proposal to correct inconsistency between levels.

---

## LevelHandler

```python
class LevelHandler
```

Base class for handling artifacts at a specific level.

---

## BehavioralPatternHandler

```python
class BehavioralPatternHandler(LevelHandler)
```

Handler for Level -2: Behavioral Patterns.

---

## TraceWitnessHandler

```python
class TraceWitnessHandler(LevelHandler)
```

Handler for Level -1: Trace Witnesses.

---

## CodeHandler

```python
class CodeHandler(LevelHandler)
```

Handler for Level 0: Implementation Code.

---

## SpecHandler

```python
class SpecHandler(LevelHandler)
```

Handler for Level 1: AGENTESE Specification.

---

## MetaSpecHandler

```python
class MetaSpecHandler(LevelHandler)
```

Handler for Level 2: Category Theory Meta-Specification.

---

## FoundationsHandler

```python
class FoundationsHandler(LevelHandler)
```

Handler for Level 3: HoTT Foundations.

---

## IntentHandler

```python
class IntentHandler(LevelHandler)
```

Handler for Level ∞: Mind-Map Intent.

---

## ConsistencyVerifier

```python
class ConsistencyVerifier
```

Verifies consistency between adjacent tower levels.

---

## ReflectiveTower

```python
class ReflectiveTower
```

The reflective tower with level hierarchy and consistency verification.

---

## create_tower

```python
async def create_tower() -> ReflectiveTower
```

Create a new reflective tower.

---

## verify_tower_consistency

```python
async def verify_tower_consistency(tower: ReflectiveTower) -> dict[str, Any]
```

Verify consistency across all tower levels.

---

## add_artifact

```python
async def add_artifact(self, artifact: LevelArtifact) -> None
```

Add an artifact to this level.

---

## get_artifact

```python
async def get_artifact(self, artifact_id: str) -> LevelArtifact | None
```

Get an artifact by ID.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract structural information from an artifact.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract pattern structure.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract trace structure.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract code structure.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract spec structure.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract meta-spec structure.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract foundations structure.

---

## extract_structure

```python
async def extract_structure(self, artifact: LevelArtifact) -> dict[str, Any]
```

Extract intent structure.

---

## verify_consistency

```python
async def verify_consistency(self, source_artifact: LevelArtifact, target_artifact: LevelArtifact) -> ConsistencyResult
```

Verify consistency between artifacts at adjacent levels.

---

## add_artifact

```python
async def add_artifact(self, artifact: LevelArtifact) -> None
```

Add an artifact to the appropriate level.

---

## get_artifact

```python
async def get_artifact(self, level: TowerLevel, artifact_id: str) -> LevelArtifact | None
```

Get an artifact from a specific level.

---

## verify_consistency

```python
async def verify_consistency(self, source_level: TowerLevel, target_level: TowerLevel) -> list[ConsistencyResult]
```

Verify consistency between all artifacts at two levels.

---

## verify_adjacent_levels

```python
async def verify_adjacent_levels(self, level: TowerLevel) -> list[ConsistencyResult]
```

Verify consistency with adjacent levels.

---

## propose_corrections

```python
async def propose_corrections(self, consistency_result: ConsistencyResult) -> list[CorrectionProposal]
```

Propose corrections for inconsistencies.

---

## get_tower_summary

```python
async def get_tower_summary(self) -> dict[str, Any]
```

Get a summary of the tower state.

---

## compress

```python
async def compress(self, artifact: LevelArtifact, target_level: TowerLevel) -> LevelArtifact | None
```

Compress an artifact to a lower level.

---

## services.verification.self_improvement

## self_improvement

```python
module self_improvement
```

Self-Improvement Engine: Autonomous specification evolution.

---

## ImprovementCategory

```python
class ImprovementCategory(str, Enum)
```

Categories of specification improvements.

---

## RiskLevel

```python
class RiskLevel(str, Enum)
```

Risk levels for improvement proposals.

---

## ImprovementProposal

```python
class ImprovementProposal
```

A formal proposal for specification improvement.

---

## PatternAnalyzer

```python
class PatternAnalyzer
```

Analyzes behavioral patterns to identify improvement opportunities.

---

## ProposalGenerator

```python
class ProposalGenerator
```

Generates formal improvement proposals from identified opportunities.

---

## CategoricalComplianceVerifier

```python
class CategoricalComplianceVerifier
```

Verifies that improvement proposals maintain categorical compliance.

---

## SelfImprovementEngine

```python
class SelfImprovementEngine
```

The self-improvement engine that orchestrates specification evolution.

---

## analyze_patterns_for_improvements

```python
async def analyze_patterns_for_improvements(patterns: list[BehavioralPattern]) -> list[ImprovementProposalResult]
```

Convenience function to analyze patterns and get improvement proposals.

---

## run_self_improvement

```python
async def run_self_improvement(patterns: list[BehavioralPattern], auto_apply: bool=False) -> dict[str, Any]
```

Convenience function to run self-improvement cycle.

---

## to_result

```python
def to_result(self) -> ImprovementProposalResult
```

Convert to immutable result.

---

## identify_improvement_opportunities

```python
async def identify_improvement_opportunities(self, patterns: list[BehavioralPattern], traces: list[TraceWitnessResult] | None=None) -> list[dict[str, Any]]
```

Identify improvement opportunities from patterns.

---

## align_with_principle

```python
def align_with_principle(self, opportunity: dict[str, Any]) -> str | None
```

Determine which kgents principle an opportunity aligns with.

---

## generate_proposal

```python
async def generate_proposal(self, opportunity: dict[str, Any]) -> ImprovementProposal
```

Generate a formal improvement proposal from an opportunity.

---

## verify_compliance

```python
async def verify_compliance(self, proposal: ImprovementProposal) -> tuple[bool, str]
```

Verify that a proposal maintains categorical compliance.

---

## analyze_and_propose

```python
async def analyze_and_propose(self, patterns: list[BehavioralPattern], traces: list[TraceWitnessResult] | None=None) -> list[ImprovementProposal]
```

Analyze patterns and generate improvement proposals.

---

## validate_proposal

```python
async def validate_proposal(self, proposal_id: str) -> tuple[bool, str]
```

Validate a specific proposal for application.

---

## apply_proposal

```python
async def apply_proposal(self, proposal_id: str, dry_run: bool=True) -> dict[str, Any]
```

Apply a validated proposal.

---

## reject_proposal

```python
async def reject_proposal(self, proposal_id: str, reason: str) -> bool
```

Reject a proposal with reason.

---

## get_proposal_summary

```python
async def get_proposal_summary(self) -> dict[str, Any]
```

Get summary of all proposals.

---

## run_improvement_cycle

```python
async def run_improvement_cycle(self, patterns: list[BehavioralPattern], auto_apply_low_risk: bool=False) -> dict[str, Any]
```

Run a complete improvement cycle.

---

## services.verification.semantic_consistency

## semantic_consistency

```python
module semantic_consistency
```

Semantic Consistency Engine: Cross-document consistency verification.

---

## SemanticConsistencyEngine

```python
class SemanticConsistencyEngine
```

Engine for verifying semantic consistency across specification documents.

---

## verify_cross_document_consistency

```python
async def verify_cross_document_consistency(self, document_paths: list[str], base_concepts: dict[str, Any] | None=None) -> SemanticConsistencyResult
```

Verify semantic consistency across multiple specification documents.

---

## services.verification.service

## service

```python
module service
```

Verification Service: Core business logic for formal verification system.

---

## VerificationService

```python
class VerificationService
```

Core verification service implementing formal verification operations.

---

## get_status

```python
async def get_status(self) -> dict[str, Any]
```

Get current verification system status.

---

## analyze_specification

```python
async def analyze_specification(self, spec_path: str) -> VerificationGraphResult
```

Analyze a specification for consistency and improvements.

---

## verify_composition_associativity

```python
async def verify_composition_associativity(self, f: AgentMorphism, g: AgentMorphism, h: AgentMorphism) -> VerificationResult
```

Verify composition associativity: (f ∘ g) ∘ h ≡ f ∘ (g ∘ h).

---

## verify_identity_laws

```python
async def verify_identity_laws(self, f: AgentMorphism, identity: AgentMorphism) -> VerificationResult
```

Verify identity laws: f ∘ id = f and id ∘ f = f.

---

## capture_trace_witness

```python
async def capture_trace_witness(self, agent_path: str, execution_data: dict[str, Any]) -> TraceWitnessResult
```

Capture a trace witness as constructive proof of behavior.

---

## generate_improvements

```python
async def generate_improvements(self) -> list[ImprovementProposalResult]
```

Generate improvement suggestions based on trace analysis.

---

## verify_semantic_consistency

```python
async def verify_semantic_consistency(self, document_paths: list[str]) -> SemanticConsistencyResult
```

Verify semantic consistency across specification documents.

---

## create_agent_hott_type

```python
async def create_agent_hott_type(self, agent_name: str, type_definition: dict[str, Any], universe_level: int=0) -> HoTTTypeResult
```

Create HoTT type representation for an agent.

---

## verify_functor_laws

```python
async def verify_functor_laws(self, functor: AgentMorphism, f: AgentMorphism, g: AgentMorphism) -> VerificationResult
```

Verify functor laws: F(id) = id and F(g ∘ f) = F(g) ∘ F(f).

---

## verify_operad_coherence

```python
async def verify_operad_coherence(self, operad_operations: list[AgentMorphism], composition_rules: dict[str, Any]) -> VerificationResult
```

Verify operad coherence conditions for multi-input compositions.

---

## verify_sheaf_gluing

```python
async def verify_sheaf_gluing(self, local_sections: dict[str, Any], overlap_conditions: dict[str, Any]) -> VerificationResult
```

Verify sheaf gluing property for local-to-global coherence.

---

## generate_counter_examples

```python
async def generate_counter_examples(self, law_name: str, morphisms: list[AgentMorphism], violation_hints: dict[str, Any] | None=None) -> list[CounterExample]
```

Generate concrete counter-examples for categorical law violations.

---

## suggest_remediation_strategies

```python
async def suggest_remediation_strategies(self, counter_examples: list[CounterExample], law_name: str) -> dict[str, Any]
```

Generate remediation strategies for categorical law violations.

---

## analyze_behavioral_patterns

```python
async def analyze_behavioral_patterns(self, pattern_type: str | None=None) -> dict[str, Any]
```

Analyze behavioral patterns in the trace corpus.

---

## get_trace_corpus_summary

```python
async def get_trace_corpus_summary(self) -> dict[str, Any]
```

Get summary statistics of the trace corpus.

---

## find_similar_traces

```python
async def find_similar_traces(self, reference_trace_id: str, similarity_threshold: float=0.7) -> list[TraceWitnessResult]
```

Find traces similar to a reference trace.

---

## services.verification.test_verification_integration

## test_verification_integration

```python
module test_verification_integration
```

Integration test for the formal verification system.

---

## TestVerificationIntegration

```python
class TestVerificationIntegration
```

Integration tests for the verification system.

---

## sample_morphisms

```python
def sample_morphisms(self)
```

Create sample morphisms for testing.

---

## sample_specification

```python
def sample_specification(self)
```

Create a sample specification for testing.

---

## test_graph_engine_integration

```python
async def test_graph_engine_integration(self, sample_specification)
```

Test graph engine with real specification.

---

## test_categorical_checker_integration

```python
async def test_categorical_checker_integration(self, sample_morphisms)
```

Test categorical checker with sample morphisms.

---

## test_counter_example_generation

```python
async def test_counter_example_generation(self, sample_morphisms)
```

Test counter-example generation.

---

## test_trace_witness_integration

```python
async def test_trace_witness_integration(self)
```

Test trace witness system.

---

## test_semantic_consistency_integration

```python
async def test_semantic_consistency_integration(self, sample_specification)
```

Test semantic consistency engine.

---

## test_remediation_strategies

```python
async def test_remediation_strategies(self, sample_morphisms)
```

Test remediation strategy generation.

---

## test_end_to_end_workflow

```python
async def test_end_to_end_workflow(self, sample_specification, sample_morphisms)
```

Test complete end-to-end verification workflow.

---

## services.verification.topology

## topology

```python
module topology
```

Mind-Map Topology Engine: Treating mind-maps as formal topological spaces.

---

## MappingType

```python
class MappingType(str, Enum)
```

Types of continuous maps between open sets.

---

## TopologicalNode

```python
class TopologicalNode
```

A node as an open set in the topology.

---

## ContinuousMap

```python
class ContinuousMap
```

An edge as a continuous map between open sets.

---

## Cover

```python
class Cover
```

A cover of the topological space.

---

## LocalSection

```python
class LocalSection
```

A local section of a sheaf over an open set.

---

## SheafVerification

```python
class SheafVerification
```

Result of sheaf condition verification.

---

## CoherenceConflict

```python
class CoherenceConflict
```

A conflict where the sheaf condition fails.

---

## RepairSuggestion

```python
class RepairSuggestion
```

A suggested repair for a coherence conflict.

---

## MindMapTopology

```python
class MindMapTopology
```

Mind-map as a topological space with sheaf structure.

---

## ObsidianImporter

```python
class ObsidianImporter
```

Import mind-maps from Obsidian markdown format.

---

## import_from_obsidian

```python
def import_from_obsidian(vault_path: str | Path) -> MindMapTopology
```

Convenience function to import from Obsidian.

---

## TopologyVisualization

```python
class TopologyVisualization
```

Data for visualizing the topology.

---

## create_visualization_data

```python
def create_visualization_data(topology: MindMapTopology) -> TopologyVisualization
```

Create visualization data from topology.

---

## with_neighbor

```python
def with_neighbor(self, neighbor_id: str) -> TopologicalNode
```

Return new node with additional neighbor.

---

## overlaps_with

```python
def overlaps_with(self, other: Cover) -> frozenset[str]
```

Return the overlap (intersection) with another cover.

---

## add_node

```python
def add_node(self, node: TopologicalNode) -> None
```

Add a node to the topology.

---

## add_edge

```python
def add_edge(self, edge: ContinuousMap) -> None
```

Add an edge and update neighborhoods.

---

## add_cover

```python
def add_cover(self, cover: Cover) -> None
```

Add a cover (cluster) to the topology.

---

## add_local_section

```python
def add_local_section(self, section: LocalSection) -> None
```

Add a local section for sheaf structure.

---

## get_neighborhood

```python
def get_neighborhood(self, node_id: str) -> frozenset[str]
```

Get the neighborhood of a node.

---

## get_connected_component

```python
def get_connected_component(self, start_id: str) -> frozenset[str]
```

Get the connected component containing a node.

---

## is_connected

```python
def is_connected(self) -> bool
```

Check if the topology is connected.

---

## get_boundary

```python
def get_boundary(self, region: frozenset[str]) -> frozenset[str]
```

Get the boundary of a region (nodes with neighbors outside).

---

## verify_sheaf_condition

```python
def verify_sheaf_condition(self) -> SheafVerification
```

Verify the sheaf gluing condition.

---

## identify_conflicts

```python
def identify_conflicts(self) -> list[CoherenceConflict]
```

Identify all coherence conflicts in the topology.

---

## suggest_repairs

```python
def suggest_repairs(self, conflict: CoherenceConflict) -> list[RepairSuggestion]
```

Suggest repairs for a coherence conflict.

---

## import_vault

```python
def import_vault(self, vault_path: Path) -> MindMapTopology
```

Import an Obsidian vault as a topology.

---

## services.verification.trace_witness

## trace_witness

```python
module trace_witness
```

Enhanced Trace Witness: Specification compliance verification with constructive proofs.

---

## EnhancedTraceWitness

```python
class EnhancedTraceWitness
```

Enhanced trace witness system for specification compliance verification.

---

## capture_execution_trace

```python
async def capture_execution_trace(self, agent_path: str, input_data: dict[str, Any], specification_id: str | None=None) -> TraceWitnessResult
```

Capture execution trace for an agent operation.

---

## analyze_behavioral_patterns

```python
async def analyze_behavioral_patterns(self, pattern_type: str | None=None) -> dict[str, Any]
```

Analyze behavioral patterns in the trace corpus.

---

## get_trace_corpus_summary

```python
async def get_trace_corpus_summary(self) -> dict[str, Any]
```

Get summary statistics of the trace corpus.

---

## find_similar_traces

```python
async def find_similar_traces(self, reference_trace_id: str, similarity_threshold: float=0.7) -> list[TraceWitnessResult]
```

Find traces similar to a reference trace.

---

## services.witness.__init__

## __init__

```python
module __init__
```

Witness Crown Jewel: The 8th Jewel That Watches, Learns, and Acts.

---

## services.witness.audit

## audit

```python
module audit
```

Witness Audit Trail: Automatic Action Recording for Cross-Jewel Operations.

---

## AuditEntry

```python
class AuditEntry
```

A single entry in the audit trail.

---

## AuditCallback

```python
class AuditCallback(Protocol)
```

Protocol for audit callbacks.

---

## AuditingInvoker

```python
class AuditingInvoker
```

JewelInvoker wrapper that automatically records actions to persistence.

---

## AuditingPipelineRunner

```python
class AuditingPipelineRunner
```

PipelineRunner wrapper that audits the entire pipeline execution.

---

## create_auditing_invoker

```python
def create_auditing_invoker(invoker: JewelInvoker, persistence: 'WitnessPersistence | None'=None, record_reads: bool=False) -> AuditingInvoker
```

Create an auditing invoker wrapper.

---

## create_auditing_runner

```python
def create_auditing_runner(invoker: 'AuditingInvoker | JewelInvoker', observer: 'Observer', persistence: 'WitnessPersistence | None'=None, record_steps: bool=False) -> AuditingPipelineRunner
```

Create an auditing pipeline runner.

---

## to_action_result

```python
def to_action_result(self) -> ActionResult
```

Convert to ActionResult for persistence.

---

## __call__

```python
async def __call__(self, entry: AuditEntry) -> None
```

Called when an action is recorded.

---

## invoke

```python
async def invoke(self, path: str, observer: 'Observer', **kwargs: Any) -> InvocationResult
```

Invoke an AGENTESE path with automatic auditing.

---

## invoke_read

```python
async def invoke_read(self, path: str, observer: 'Observer', **kwargs: Any) -> InvocationResult
```

Convenience for read-only invocations.

---

## invoke_mutation

```python
async def invoke_mutation(self, path: str, observer: 'Observer', reversible: bool=True, inverse_action: str | None=None, **kwargs: Any) -> InvocationResult
```

Invoke a mutation with explicit rollback info.

---

## add_callback

```python
def add_callback(self, callback: AuditCallback) -> None
```

Add an audit callback.

---

## get_log

```python
def get_log(self, mutations_only: bool=True, limit: int=100) -> list[AuditEntry]
```

Get recent audit entries.

---

## trust_level

```python
def trust_level(self) -> TrustLevel
```

Expose inner invoker's trust level.

---

## run

```python
async def run(self, pipeline: Pipeline, initial_kwargs: dict[str, Any] | None=None, name: str='') -> PipelineResult
```

Execute a pipeline with automatic auditing.

---

## services.witness.bus

## bus

```python
module bus
```

Witness Bus Architecture: Event-Driven Cross-Jewel Communication.

---

## WitnessTopics

```python
class WitnessTopics
```

Topic namespace for witness events.

---

## WitnessSynergyBus

```python
class WitnessSynergyBus
```

Cross-jewel pub/sub bus with wildcard support.

---

## WitnessEventBus

```python
class WitnessEventBus
```

EventBus for UI fan-out.

---

## wire_synergy_to_event

```python
def wire_synergy_to_event(synergy_bus: WitnessSynergyBus, event_bus: WitnessEventBus, topics: list[str] | None=None) -> list[UnsubscribeFunc]
```

Wire SynergyBus topics to EventBus fan-out.

---

## wire_witness_to_global_synergy

```python
def wire_witness_to_global_synergy(witness_bus: WitnessSynergyBus) -> list[UnsubscribeFunc]
```

Bridge Witness events to the global SynergyBus.

---

## register_witness_handlers

```python
def register_witness_handlers() -> list[UnsubscribeFunc]
```

Register Witness handlers with the global SynergyBus.

---

## WitnessBusManager

```python
class WitnessBusManager
```

Manages the two-bus architecture for Witness.

---

## get_witness_bus_manager

```python
def get_witness_bus_manager() -> WitnessBusManager
```

Get the global WitnessBusManager instance.

---

## reset_witness_bus_manager

```python
def reset_witness_bus_manager() -> None
```

Reset the global WitnessBusManager (for testing).

---

## get_synergy_bus

```python
def get_synergy_bus() -> WitnessSynergyBus
```

Get the global WitnessSynergyBus.

---

## publish

```python
async def publish(self, topic: str, event: Any) -> None
```

Publish an event to a topic.

---

## subscribe

```python
def subscribe(self, topic: str, handler: SynergyHandler) -> UnsubscribeFunc
```

Subscribe to a topic.

---

## stats

```python
def stats(self) -> dict[str, int]
```

Get bus statistics.

---

## clear

```python
def clear(self) -> None
```

Clear all handlers (for testing).

---

## publish

```python
async def publish(self, event: Any) -> None
```

Publish event to all subscribers.

---

## subscribe

```python
def subscribe(self, handler: WitnessEventHandler) -> UnsubscribeFunc
```

Subscribe to all events.

---

## stats

```python
def stats(self) -> dict[str, int]
```

Get bus statistics.

---

## clear

```python
def clear(self) -> None
```

Clear all subscribers (for testing).

---

## bridge_thought

```python
async def bridge_thought(topic: str, event: Any) -> None
```

Bridge thought events to global synergy.

---

## bridge_git_commit

```python
async def bridge_git_commit(topic: str, event: Any) -> None
```

Bridge git commit events to global synergy.

---

## bridge_daemon_started

```python
async def bridge_daemon_started(topic: str, event: Any) -> None
```

Bridge daemon started events to global synergy.

---

## bridge_daemon_stopped

```python
async def bridge_daemon_stopped(topic: str, event: Any) -> None
```

Bridge daemon stopped events to global synergy.

---

## wire_all

```python
def wire_all(self) -> None
```

Wire all buses together.

---

## wire_cross_jewel_handlers

```python
def wire_cross_jewel_handlers(self) -> None
```

Wire cross-jewel event handlers.

---

## unwire_all

```python
def unwire_all(self) -> None
```

Disconnect all wiring.

---

## clear

```python
def clear(self) -> None
```

Clear all buses and wiring (for testing).

---

## stats

```python
def stats(self) -> dict[str, dict[str, int]]
```

Get combined statistics.

---

## services.witness.cli

## cli

```python
module cli
```

kgentsd: The Witness Daemon CLI.

---

## cmd_summon

```python
def cmd_summon(args: list[str]) -> int
```

Summon the Witness daemon (foreground mode with TUI).

---

## cmd_release

```python
def cmd_release(args: list[str]) -> int
```

Release the Witness daemon gracefully.

---

## cmd_status

```python
def cmd_status(args: list[str]) -> int
```

Show current Witness daemon status.

---

## cmd_thoughts

```python
def cmd_thoughts(args: list[str]) -> int
```

View recent thought stream.

---

## cmd_ask

```python
def cmd_ask(args: list[str]) -> int
```

Ask the Witness a direct question.

---

## main

```python
def main(argv: list[str] | None=None) -> int
```

Main entry point for kgentsd CLI.

---

## services.witness.contracts

## contracts

```python
module contracts
```

Witness AGENTESE Contracts: Type-safe request/response definitions.

---

## WitnessManifestResponse

```python
class WitnessManifestResponse
```

Response for manifest aspect.

---

## ThoughtsRequest

```python
class ThoughtsRequest
```

Request for thoughts aspect.

---

## ThoughtItem

```python
class ThoughtItem
```

A single thought in the response.

---

## ThoughtsResponse

```python
class ThoughtsResponse
```

Response for thoughts aspect.

---

## TrustRequest

```python
class TrustRequest
```

Request for trust aspect.

---

## TrustResponse

```python
class TrustResponse
```

Response for trust aspect.

---

## CaptureThoughtRequest

```python
class CaptureThoughtRequest
```

Request for capture aspect.

---

## CaptureThoughtResponse

```python
class CaptureThoughtResponse
```

Response for capture aspect.

---

## ActionRecordRequest

```python
class ActionRecordRequest
```

Request for action aspect.

---

## ActionRecordResponse

```python
class ActionRecordResponse
```

Response for action aspect.

---

## RollbackWindowRequest

```python
class RollbackWindowRequest
```

Request for rollback aspect.

---

## RollbackActionItem

```python
class RollbackActionItem
```

A single action in the rollback response.

---

## RollbackWindowResponse

```python
class RollbackWindowResponse
```

Response for rollback aspect.

---

## EscalateRequest

```python
class EscalateRequest
```

Request for escalate aspect.

---

## EscalateResponse

```python
class EscalateResponse
```

Response for escalate aspect.

---

## InvokeRequest

```python
class InvokeRequest
```

Request for invoke aspect (cross-jewel invocation).

---

## InvokeResponse

```python
class InvokeResponse
```

Response for invoke aspect.

---

## PipelineStepItem

```python
class PipelineStepItem
```

A single step definition in a pipeline request.

---

## PipelineRequest

```python
class PipelineRequest
```

Request for pipeline aspect (cross-jewel pipeline).

---

## PipelineStepResultItem

```python
class PipelineStepResultItem
```

Result of a single step in pipeline execution.

---

## PipelineResponse

```python
class PipelineResponse
```

Response for pipeline aspect.

---

## CrystallizeRequest

```python
class CrystallizeRequest
```

Request for crystallize aspect - trigger experience crystallization.

---

## CrystalItem

```python
class CrystalItem
```

A crystal summary for list responses.

---

## CrystallizeResponse

```python
class CrystallizeResponse
```

Response for crystallize aspect.

---

## TimelineRequest

```python
class TimelineRequest
```

Request for timeline aspect - get crystallization timeline.

---

## TimelineResponse

```python
class TimelineResponse
```

Response for timeline aspect.

---

## CrystalQueryRequest

```python
class CrystalQueryRequest
```

Request for crystal aspect - retrieve specific crystal.

---

## CrystalQueryResponse

```python
class CrystalQueryResponse
```

Response for crystal aspect - full crystal detail.

---

## TerritoryRequest

```python
class TerritoryRequest
```

Request for territory aspect - codebase heat map.

---

## TerritoryResponse

```python
class TerritoryResponse
```

Response for territory aspect - codebase activity map.

---

## AttuneRequest

```python
class AttuneRequest
```

Request for attune aspect - start observation session.

---

## AttuneResponse

```python
class AttuneResponse
```

Response for attune aspect.

---

## MarkRequest

```python
class MarkRequest
```

Request for mark aspect - create user marker.

---

## MarkResponse

```python
class MarkResponse
```

Response for mark aspect.

---

## ScheduleRequest

```python
class ScheduleRequest
```

Request for schedule aspect (scheduling future invocations).

---

## SchedulePeriodicRequest

```python
class SchedulePeriodicRequest
```

Request for scheduling periodic invocations.

---

## ScheduleResponse

```python
class ScheduleResponse
```

Response for schedule aspect.

---

## ScheduleListRequest

```python
class ScheduleListRequest
```

Request for listing scheduled tasks.

---

## ScheduleListResponse

```python
class ScheduleListResponse
```

Response for listing scheduled tasks.

---

## ScheduleCancelRequest

```python
class ScheduleCancelRequest
```

Request for cancelling a scheduled task.

---

## ScheduleCancelResponse

```python
class ScheduleCancelResponse
```

Response for cancelling a scheduled task.

---

## services.witness.crystal

## crystal

```python
module crystal
```

ExperienceCrystal: The Atomic Unit of Witnessed Experience.

---

## MoodVector

```python
class MoodVector
```

Seven-dimensional affective signature of a work session.

### Examples
```python
>>> mood = MoodVector.from_thoughts(thoughts)
```
```python
>>> mood.brightness  # 0.8 if lots of success markers
```
```python
>>> mood.similarity(other_mood)  # Cosine similarity
```

---

## TopologySnapshot

```python
class TopologySnapshot
```

Snapshot of codebase topology at crystallization time.

---

## Narrative

```python
class Narrative
```

Synthesized narrative from a work session.

---

## ExperienceCrystal

```python
class ExperienceCrystal
```

The atomic unit of The Witness's memory.

### Examples
```python
>>> crystal = ExperienceCrystal.from_thoughts(thoughts, session_id="abc")
```
```python
>>> crystal.mood.brightness  # Was it a good session?
```
```python
>>> crystal.topics  # What was worked on?
```
```python
>>> crystal.as_memory()  # Project to D-gent for storage
```

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate all dimensions are in [0, 1].

---

## neutral

```python
def neutral(cls) -> MoodVector
```

Return a neutral mood (all 0.5).

---

## from_thoughts

```python
def from_thoughts(cls, thoughts: list[Thought]) -> MoodVector
```

Derive mood from a thought stream.

---

## similarity

```python
def similarity(self, other: MoodVector) -> float
```

Cosine similarity to another mood vector.

---

## to_dict

```python
def to_dict(self) -> dict[str, float]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, float]) -> MoodVector
```

Create from dictionary.

---

## dominant_quality

```python
def dominant_quality(self) -> str
```

Return the most prominent quality.

---

## from_thoughts

```python
def from_thoughts(cls, thoughts: list[Thought]) -> TopologySnapshot
```

Derive topology from thought stream.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> TopologySnapshot
```

Create from dictionary.

---

## template_fallback

```python
def template_fallback(cls, thoughts: list[Thought]) -> Narrative
```

Template fallback when LLM unavailable.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Narrative
```

Create from dictionary.

---

## from_thoughts

```python
def from_thoughts(cls, thoughts: list[Thought], session_id: str='', markers: list[str] | None=None, narrative: Narrative | None=None) -> ExperienceCrystal
```

Create crystal from thought stream.

---

## as_memory

```python
def as_memory(self) -> dict[str, Any]
```

Project into D-gent-compatible format for long-term storage.

---

## to_json

```python
def to_json(self) -> dict[str, Any]
```

Convert to JSON-serializable dictionary.

---

## from_json

```python
def from_json(cls, data: dict[str, Any]) -> ExperienceCrystal
```

Create from JSON dictionary.

---

## duration_minutes

```python
def duration_minutes(self) -> float | None
```

Duration of the crystallized session in minutes.

---

## thought_count

```python
def thought_count(self) -> int
```

Number of thoughts in this crystal.

---

## services.witness.crystallization_node

## crystallization_node

```python
module crystallization_node
```

Time Witness AGENTESE Node: @node("time.witness")

---

## TimeWitnessManifestResponse

```python
class TimeWitnessManifestResponse
```

Manifest response for time.witness.

---

## TimeWitnessManifestRendering

```python
class TimeWitnessManifestRendering
```

Rendering for time.witness manifest.

---

## TimeWitnessNode

```python
class TimeWitnessNode(BaseLogosNode)
```

AGENTESE node for experience crystallization (time.witness context).

---

## __init__

```python
def __init__(self, witness_persistence: WitnessPersistence) -> None
```

Initialize TimeWitnessNode.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `time.witness.manifest`

Manifest crystallization status to observer.

---

## observe

```python
def observe(self, observation: LocalObservation) -> None
```

Add an observation from a watcher.

---

## get_crystals

```python
def get_crystals(self) -> list[ExperienceCrystal]
```

Get all crystals (for Muse integration).

---

## services.witness.daemon

## daemon

```python
module daemon
```

**AGENTESE:** `Cross`

Witness Daemon: Background Process for Continuous Observation.

---

## DaemonConfig

```python
class DaemonConfig
```

Configuration for the witness daemon.

---

## read_pid_file

```python
def read_pid_file(pid_file: Path) -> int | None
```

Read PID from file, return None if not exists or invalid.

---

## write_pid_file

```python
def write_pid_file(pid_file: Path, pid: int) -> None
```

Write PID to file.

---

## remove_pid_file

```python
def remove_pid_file(pid_file: Path) -> None
```

Remove PID file if it exists.

---

## is_process_running

```python
def is_process_running(pid: int) -> bool
```

Check if a process with given PID is running.

---

## check_daemon_status

```python
def check_daemon_status(config: DaemonConfig | None=None) -> tuple[bool, int | None]
```

Check if the daemon is running.

---

## create_watcher

```python
def create_watcher(watcher_type: str, config: DaemonConfig) -> BaseWatcher[Any] | None
```

Create a watcher instance by type.

---

## event_to_thought

```python
def event_to_thought(event: Any) -> Any
```

Convert any watcher event to a Thought.

---

## WitnessDaemon

```python
class WitnessDaemon
```

Background daemon for witness observation.

---

## start_daemon

```python
def start_daemon(config: DaemonConfig | None=None) -> int
```

Start the witness daemon in a background process.

---

## stop_daemon

```python
def stop_daemon(config: DaemonConfig | None=None) -> bool
```

Stop the witness daemon.

---

## get_daemon_status

```python
def get_daemon_status(config: DaemonConfig | None=None) -> dict[str, Any]
```

Get daemon status information.

---

## main

```python
async def main() -> None
```

Main entry point for daemon process.

---

## validate

```python
def validate(self) -> list[str]
```

Validate configuration, return list of errors.

---

## start

```python
async def start(self) -> None
```

Start the daemon and begin watching.

---

## trust_level

```python
def trust_level(self) -> Any
```

Get current trust level from persistence.

---

## trust_status

```python
def trust_status(self) -> dict[str, Any]
```

Get current trust status for display.

---

## set_suggestion_callback

```python
def set_suggestion_callback(self, callback: Any) -> None
```

Register a callback for new suggestions.

---

## is_running

```python
def is_running(self) -> bool
```

Check if daemon is running.

---

## services.witness.grant

## grant

```python
module grant
```

Grant: Negotiated Permission Contract.

---

## generate_grant_id

```python
def generate_grant_id() -> GrantId
```

Generate a unique Grant ID.

---

## GrantStatus

```python
class GrantStatus(Enum)
```

Status of a Grant.

---

## GateFallback

```python
class GateFallback(Enum)
```

What to do when a ReviewGate times out.

---

## ReviewGate

```python
class ReviewGate
```

Checkpoint requiring human review.

### Examples
```python
>>> gate = ReviewGate(
```
```python
>>> # After 5 file writes, human review is triggered
```

---

## GateOccurrence

```python
class GateOccurrence
```

Tracks occurrences of a gated operation.

---

## GrantError

```python
class GrantError(Exception)
```

Base exception for Grant errors.

---

## GrantNotGranted

```python
class GrantNotGranted(GrantError)
```

Law 1: Attempted operation without granted Grant.

---

## GrantRevoked

```python
class GrantRevoked(GrantError)
```

Law 2: Grant has been revoked.

---

## GateTriggered

```python
class GateTriggered(GrantError)
```

Law 3: Review gate threshold reached.

---

## Grant

```python
class Grant
```

Negotiated permission contract.

### Examples
```python
>>> grant = Grant.propose(
```
```python
>>> # Human reviews and grants
```
```python
>>> granted = grant.grant(granted_by="kent")
```

---

## GrantEnforcer

```python
class GrantEnforcer
```

Runtime enforcer for Grant permissions and gates.

### Examples
```python
>>> enforcer = GrantEnforcer(grant)
```
```python
>>> enforcer.check("file_read")  # OK
```
```python
>>> enforcer.check("git_push")   # Might trigger gate
```

---

## GrantStore

```python
class GrantStore
```

Persistent storage for Grants.

---

## get_grant_store

```python
def get_grant_store() -> GrantStore
```

Get the global grant store.

---

## reset_grant_store

```python
def reset_grant_store() -> None
```

Reset the global grant store (for testing).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> ReviewGate
```

Create from dictionary.

---

## record

```python
def record(self) -> bool
```

Record an occurrence. Returns True if gate threshold reached.

---

## reset

```python
def reset(self) -> None
```

Reset counter (called after review).

---

## propose

```python
def propose(cls, permissions: frozenset[str] | tuple[str, ...] | list[str], review_gates: tuple[ReviewGate, ...] | None=None, reason: str='', expires_at: datetime | None=None, description: str='') -> Grant
```

Propose a new Grant.

---

## negotiate

```python
def negotiate(self) -> Grant
```

Move to NEGOTIATING status.

---

## grant

```python
def grant(self, granted_by: str) -> Grant
```

Grant the Grant.

---

## revoke

```python
def revoke(self, revoked_by: str, reason: str='') -> Grant
```

Revoke the Grant.

---

## amend

```python
def amend(self, permissions: frozenset[str] | None=None, review_gates: tuple[ReviewGate, ...] | None=None) -> Grant
```

Amend the Grant with new terms.

---

## is_active

```python
def is_active(self) -> bool
```

Check if Grant is active and usable.

---

## check_active

```python
def check_active(self) -> None
```

Raise if Grant is not active.

---

## has_permission

```python
def has_permission(self, permission: str) -> bool
```

Check if a permission is granted.

---

## check_permission

```python
def check_permission(self, permission: str) -> None
```

Check permission, raising if not granted or Grant inactive.

---

## get_gate

```python
def get_gate(self, trigger: str) -> ReviewGate | None
```

Get the review gate for a trigger, if any.

---

## trust_level

```python
def trust_level(self) -> str
```

Backwards compat: derive from status.

---

## proposed_at

```python
def proposed_at(self) -> datetime
```

Backwards compat: alias for created_at.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Grant
```

Create from dictionary.

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize gate occurrences.

---

## check

```python
def check(self, operation: str) -> None
```

Check if operation is permitted.

---

## approve_gate

```python
def approve_gate(self, trigger: str) -> None
```

Approve a pending gate review, resetting the counter.

---

## is_gate_pending

```python
def is_gate_pending(self, trigger: str) -> bool
```

Check if a gate has a pending review.

---

## add

```python
def add(self, grant: Grant) -> None
```

Add a Grant to the store.

---

## get

```python
def get(self, grant_id: GrantId) -> Grant | None
```

Get a Grant by ID.

---

## update

```python
def update(self, grant: Grant) -> None
```

Update a Grant (replace with new version).

---

## active

```python
def active(self) -> list[Grant]
```

Get all active Grants.

---

## pending

```python
def pending(self) -> list[Grant]
```

Get Grants awaiting approval.

---

## revoked

```python
def revoked(self) -> list[Grant]
```

Get revoked Grants.

---

## services.witness.intent

## intent

```python
module intent
```

IntentTree: Typed Task Decomposition with Dependencies.

---

## generate_intent_id

```python
def generate_intent_id() -> IntentId
```

Generate a unique Intent ID.

---

## IntentType

```python
class IntentType(Enum)
```

Typed intent categories.

---

## IntentStatus

```python
class IntentStatus(Enum)
```

Status of an Intent.

---

## Intent

```python
class Intent
```

Typed goal node in the intent graph.

### Examples
```python
>>> root = Intent.create(
```
```python
>>> child = Intent.create(
```

---

## CyclicDependencyError

```python
class CyclicDependencyError(Exception)
```

Law 3: Dependencies form a DAG - cycle detected.

---

## IntentTree

```python
class IntentTree
```

Typed intent graph with dependencies.

---

## get_intent_tree

```python
def get_intent_tree() -> IntentTree
```

Get the global intent tree.

---

## reset_intent_tree

```python
def reset_intent_tree() -> None
```

Reset the global intent tree (for testing).

---

## create

```python
def create(cls, description: str, intent_type: IntentType=IntentType.IMPLEMENT, parent_id: IntentId | None=None, depends_on: tuple[IntentId, ...]=(), priority: int=0, tags: tuple[str, ...]=()) -> Intent
```

Create a new Intent.

---

## start

```python
def start(self) -> Intent
```

Transition to ACTIVE status.

---

## complete

```python
def complete(self) -> Intent
```

Transition to COMPLETE status.

---

## block

```python
def block(self, reason: str='') -> Intent
```

Transition to BLOCKED status.

---

## cancel

```python
def cancel(self) -> Intent
```

Transition to CANCELLED status.

---

## with_child

```python
def with_child(self, child_id: IntentId) -> Intent
```

Return Intent with added child.

---

## is_active

```python
def is_active(self) -> bool
```

Check if Intent is active.

---

## is_complete

```python
def is_complete(self) -> bool
```

Check if Intent is complete.

---

## is_blocked

```python
def is_blocked(self) -> bool
```

Check if Intent is blocked.

---

## is_terminal

```python
def is_terminal(self) -> bool
```

Check if Intent is in terminal state.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Intent
```

Create from dictionary.

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## add

```python
def add(self, intent: Intent) -> None
```

Add an Intent to the tree.

---

## get

```python
def get(self, intent_id: IntentId) -> Intent | None
```

Get an Intent by ID.

---

## update

```python
def update(self, intent: Intent) -> None
```

Update an existing Intent.

---

## children

```python
def children(self, intent_id: IntentId) -> list[Intent]
```

Get all children of an Intent.

---

## dependencies

```python
def dependencies(self, intent_id: IntentId) -> list[Intent]
```

Get all dependencies of an Intent.

---

## dependents

```python
def dependents(self, intent_id: IntentId) -> list[Intent]
```

Get all Intents that depend on this one.

---

## by_type

```python
def by_type(self, intent_type: IntentType) -> list[Intent]
```

Get all Intents of a given type.

---

## by_status

```python
def by_status(self, status: IntentStatus) -> list[Intent]
```

Get all Intents with a given status.

---

## ready_to_start

```python
def ready_to_start(self) -> list[Intent]
```

Get Intents that are ready to be started.

---

## blocked

```python
def blocked(self) -> list[Intent]
```

Get all blocked Intents.

---

## propagate_status

```python
def propagate_status(self, intent_id: IntentId) -> None
```

Propagate status changes up the tree.

---

## all

```python
def all(self) -> list[Intent]
```

Get all Intents.

---

## leaves

```python
def leaves(self) -> list[Intent]
```

Get all leaf Intents (no children).

---

## roots

```python
def roots(self) -> list[Intent]
```

Get all root Intents (no parent).

---

## root

```python
def root(self) -> Intent | None
```

Get the root Intent.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> IntentTree
```

Create from dictionary.

---

## services.witness.invoke

## invoke

```python
module invoke
```

Cross-Jewel Invocation: Witness Invoking Other Crown Jewels.

---

## InvocationResult

```python
class InvocationResult
```

Result of a cross-jewel invocation.

---

## classify_path

```python
def classify_path(path: str) -> tuple[str, str, str]
```

Parse an AGENTESE path into components.

---

## is_read_only_path

```python
def is_read_only_path(path: str) -> bool
```

Check if a path is read-only.

---

## is_mutation_path

```python
def is_mutation_path(path: str) -> bool
```

Check if a path is a mutation.

---

## JewelInvoker

```python
class JewelInvoker
```

Invokes other Crown Jewels on behalf of Witness.

### Examples
```python
>>> invoker = JewelInvoker(logos, gate, TrustLevel.AUTONOMOUS)
```
```python
>>> result = await invoker.invoke("world.gestalt.manifest", observer)
```
```python
>>> result = await invoker.invoke("self.memory.capture", observer, content="...")
```

---

## create_invoker

```python
def create_invoker(logos: 'Logos', trust_level: TrustLevel, boundary_checker: Any | None=None, log_invocations: bool=True) -> JewelInvoker
```

Create a JewelInvoker with appropriate configuration.

---

## is_success

```python
def is_success(self) -> bool
```

Check if invocation succeeded.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## invoke

```python
async def invoke(self, path: str, observer: 'Observer', **kwargs: Any) -> InvocationResult
```

Invoke an AGENTESE path with trust gating.

---

## invoke_read

```python
async def invoke_read(self, path: str, observer: 'Observer', **kwargs: Any) -> InvocationResult
```

Invoke a read-only path (any trust level).

---

## invoke_mutation

```python
async def invoke_mutation(self, path: str, observer: 'Observer', **kwargs: Any) -> InvocationResult
```

Invoke a mutation path (requires L3 AUTONOMOUS).

---

## can_invoke

```python
def can_invoke(self, path: str) -> bool
```

Check if a path can be invoked at current trust level.

---

## get_invocation_log

```python
def get_invocation_log(self, limit: int=100, success_only: bool=False) -> list[InvocationResult]
```

Get recent invocation log.

---

## services.witness.lesson

## lesson

```python
module lesson
```

Lesson: Curated Knowledge Layer with Versioning.

---

## generate_lesson_id

```python
def generate_lesson_id() -> LessonId
```

Generate a unique Lesson ID.

---

## LessonStatus

```python
class LessonStatus(Enum)
```

Status of a Lesson.

---

## Lesson

```python
class Lesson
```

Curated knowledge with versioning.

### Examples
```python
>>> v1 = Lesson.create(
```
```python
>>> v2 = v1.evolve(
```
```python
>>> v2.version  # 2
```
```python
>>> v2.supersedes  # v1.id
```

---

## LessonStore

```python
class LessonStore
```

Persistent storage for Lessons.

---

## get_lesson_store

```python
def get_lesson_store() -> LessonStore
```

Get the global lesson store.

---

## set_lesson_store

```python
def set_lesson_store(store: LessonStore) -> None
```

Set the global lesson store.

---

## reset_lesson_store

```python
def reset_lesson_store() -> None
```

Reset the global lesson store (for testing).

---

## create

```python
def create(cls, topic: str, content: str, tags: tuple[str, ...]=(), source: str='', confidence: float=1.0) -> Lesson
```

Create a new Lesson (version 1).

---

## evolve

```python
def evolve(self, content: str, reason: str='', tags: tuple[str, ...] | None=None, confidence: float | None=None) -> Lesson
```

Create a new version that supersedes this one.

---

## deprecate

```python
def deprecate(self, reason: str='') -> Lesson
```

Mark this Lesson as deprecated.

---

## archive

```python
def archive(self) -> Lesson
```

Mark this Lesson as archived.

---

## is_current

```python
def is_current(self) -> bool
```

Check if this is the current version.

---

## is_superseded

```python
def is_superseded(self) -> bool
```

Check if this has been superseded.

---

## is_deprecated

```python
def is_deprecated(self) -> bool
```

Check if this is deprecated.

---

## has_supersedes

```python
def has_supersedes(self) -> bool
```

Check if this supersedes another version.

---

## age_days

```python
def age_days(self) -> float
```

Get the age of this Lesson in days.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Lesson
```

Create from dictionary.

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## add

```python
def add(self, lesson: Lesson) -> None
```

Add a Lesson to the store.

---

## update

```python
def update(self, lesson: Lesson) -> None
```

Update an existing Lesson (for status changes).

---

## get

```python
def get(self, lesson_id: LessonId) -> Lesson | None
```

Get a Lesson by ID.

---

## current

```python
def current(self, topic: str) -> Lesson | None
```

Get the current (latest) version for a topic.

---

## history

```python
def history(self, topic: str) -> list[Lesson]
```

Get version history for a topic.

---

## latest

```python
def latest(self, topic: str) -> Lesson | None
```

Get the latest version for a topic (regardless of status).

---

## by_tag

```python
def by_tag(self, tag: str) -> list[Lesson]
```

Get all CURRENT Lessons with a specific tag.

---

## by_source

```python
def by_source(self, source: str) -> list[Lesson]
```

Get all CURRENT Lessons from a specific source.

---

## search

```python
def search(self, query: str) -> list[Lesson]
```

Search CURRENT Lessons by topic or content.

---

## all_current

```python
def all_current(self) -> list[Lesson]
```

Get all CURRENT Lessons.

---

## all_topics

```python
def all_topics(self) -> list[str]
```

Get all topics.

---

## deprecated

```python
def deprecated(self) -> list[Lesson]
```

Get all deprecated Lessons.

---

## recent

```python
def recent(self, limit: int=10) -> list[Lesson]
```

Get most recently created Lessons.

---

## predecessor

```python
def predecessor(self, lesson: Lesson) -> Lesson | None
```

Get the version this Lesson supersedes.

---

## successor

```python
def successor(self, lesson: Lesson) -> Lesson | None
```

Get the version that superseded this one (if any).

---

## full_chain

```python
def full_chain(self, topic: str) -> list[Lesson]
```

Get the full version chain for a topic, ordered by version.

---

## stats

```python
def stats(self) -> dict[str, int]
```

Get store statistics.

---

## services.witness.mark

## mark

```python
module mark
```

Mark: The Atomic Unit of Execution Artifact.

---

## generate_mark_id

```python
def generate_mark_id() -> MarkId
```

Generate a unique Mark ID.

---

## LinkRelation

```python
class LinkRelation(Enum)
```

Types of causal relationships between Marks.

---

## MarkLink

```python
class MarkLink
```

Causal edge between Marks or to plans.

### Examples
```python
>>> link = MarkLink(
```

---

## NPhase

```python
class NPhase(Enum)
```

N-Phase workflow phases.

---

## UmweltSnapshot

```python
class UmweltSnapshot
```

Snapshot of observer capabilities at Mark emission time.

---

## Stimulus

```python
class Stimulus
```

What triggered the Mark.

---

## Response

```python
class Response
```

What the Mark produced.

---

## Mark

```python
class Mark
```

Atomic unit of execution artifact.

### Examples
```python
>>> mark = Mark(
```
```python
>>> mark.id  # "mark-abc123def456"
```

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> MarkLink
```

Create from dictionary.

---

## family

```python
def family(self) -> str
```

Return the 3-phase family this phase belongs to.

---

## system

```python
def system(cls) -> UmweltSnapshot
```

Create a system-level umwelt (full capabilities).

---

## witness

```python
def witness(cls, trust_level: int=0) -> UmweltSnapshot
```

Create a Witness umwelt with specified trust level.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> UmweltSnapshot
```

Create from dictionary.

---

## from_agentese

```python
def from_agentese(cls, path: str, aspect: str, **kwargs: Any) -> Stimulus
```

Create stimulus from AGENTESE invocation.

---

## from_prompt

```python
def from_prompt(cls, prompt: str, source: str='user') -> Stimulus
```

Create stimulus from user prompt.

---

## from_event

```python
def from_event(cls, event_type: str, content: str, source: str) -> Stimulus
```

Create stimulus from watcher event.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Stimulus
```

Create from dictionary.

---

## thought

```python
def thought(cls, content: str, tags: tuple[str, ...]=()) -> Response
```

Create response from Witness thought.

---

## projection

```python
def projection(cls, path: str, target: str='cli') -> Response
```

Create response from AGENTESE projection.

---

## error

```python
def error(cls, message: str) -> Response
```

Create error response.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Response
```

Create from dictionary.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Validate causal links (Law 2 check deferred to store).

---

## from_thought

```python
def from_thought(cls, content: str, source: str, tags: tuple[str, ...]=(), origin: str='witness', trust_level: int=0, phase: NPhase | None=None) -> Mark
```

Create Mark from Witness Thought pattern.

---

## from_agentese

```python
def from_agentese(cls, path: str, aspect: str, response_content: str, origin: str='logos', umwelt: UmweltSnapshot | None=None, phase: NPhase | None=None, **kwargs: Any) -> Mark
```

Create Mark from AGENTESE invocation.

---

## with_link

```python
def with_link(self, link: MarkLink) -> Mark
```

Return new Mark with added link (immutable pattern).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Mark
```

Create from dictionary.

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## services.witness.node

## node

```python
module node
```

Witness AGENTESE Node: @node("self.witness")

---

## WitnessManifestRendering

```python
class WitnessManifestRendering
```

Rendering for witness status manifest.

---

## ThoughtStreamRendering

```python
class ThoughtStreamRendering
```

Rendering for thought stream.

---

## WitnessNode

```python
class WitnessNode(BaseLogosNode)
```

AGENTESE node for Witness Crown Jewel (8th Jewel).

---

## __init__

```python
def __init__(self, witness_persistence: WitnessPersistence, logos: Any=None) -> None
```

Initialize WitnessNode.

---

## manifest

```python
async def manifest(self, observer: 'Observer | Umwelt[Any, Any]') -> Renderable
```

**AGENTESE:** `self.witness.manifest`

Manifest witness status to observer.

---

## stream

```python
async def stream(self, observer: 'Observer | Umwelt[Any, Any]', **kwargs: Any) -> AsyncGenerator[dict[str, Any], None]
```

**AGENTESE:** `self.witness.stream`

Stream thoughts in real-time via Server-Sent Events.

---

## services.witness.operad

## operad

```python
module operad
```

WitnessOperad: Formal Grammar for Autonomous Developer Agency.

---

## WitnessMetabolics

```python
class WitnessMetabolics
```

Metabolic costs of a witness operation.

---

## create_witness_operad

```python
def create_witness_operad() -> Operad
```

Create the Witness Operad.

---

## compose_observe_workflow

```python
def compose_observe_workflow(sources: list[str]) -> PolyAgent[Any, Any, Any]
```

Compose a complete observation workflow.

---

## compose_suggest_workflow

```python
def compose_suggest_workflow(sources: list[str], analyzer: str, action_type: str) -> PolyAgent[Any, Any, Any]
```

Compose a complete suggestion workflow.

---

## compose_autonomous_workflow

```python
def compose_autonomous_workflow(sources: list[str], analyzer: str, action: str, target: str | None=None) -> PolyAgent[Any, Any, Any]
```

Compose a complete autonomous workflow.

---

## can_execute

```python
def can_execute(self, current_trust: TrustLevel) -> bool
```

Check if operation can execute at given trust level.

---

## services.witness.persistence

## persistence

```python
module persistence
```

Witness Persistence: Dual-Track Storage for the 8th Crown Jewel.

---

## ThoughtResult

```python
class ThoughtResult
```

Result of a thought save operation.

---

## TrustResult

```python
class TrustResult
```

Result of a trust query with decay applied.

---

## EscalationResult

```python
class EscalationResult
```

Result of an escalation record.

---

## ActionResultPersisted

```python
class ActionResultPersisted
```

Result of an action save operation.

---

## WitnessStatus

```python
class WitnessStatus
```

Witness health status.

---

## WitnessPersistence

```python
class WitnessPersistence
```

Persistence layer for Witness Crown Jewel.

---

## save_thought

```python
async def save_thought(self, thought: Thought, trust_id: str | None=None, repository_path: str | None=None) -> ThoughtResult
```

**AGENTESE:** `self.witness.thoughts.capture`

Save a thought to dual-track storage.

---

## get_thoughts

```python
async def get_thoughts(self, limit: int=50, trust_id: str | None=None, source: str | None=None, since: datetime | None=None) -> list[Thought]
```

**AGENTESE:** `self.witness.thoughts`

Get recent thoughts with optional filters.

---

## thought_stream

```python
async def thought_stream(self, limit: int=50, sources: list[str] | None=None, poll_interval: float=2.0) -> AsyncGenerator[Thought, None]
```

**AGENTESE:** `self.witness.thoughts.stream`

Stream thoughts in real-time via async generator.

---

## get_trust_level

```python
async def get_trust_level(self, git_email: str, repository_path: str | None=None, apply_decay: bool=True) -> TrustResult
```

**AGENTESE:** `self.witness.trust`

Get trust level for a user, with decay applied.

---

## update_trust_metrics

```python
async def update_trust_metrics(self, git_email: str, observation_count: int | None=None, successful_operations: int | None=None, confirmed_suggestion: bool | None=None) -> TrustResult
```

Update trust metrics for a user.

---

## record_escalation

```python
async def record_escalation(self, git_email: str, from_level: TrustLevel, to_level: TrustLevel, reason: str) -> EscalationResult
```

**AGENTESE:** `self.witness.trust.escalate`

Record a trust escalation event.

---

## record_action

```python
async def record_action(self, action: ActionResult, trust_id: str | None=None, repository_path: str | None=None, git_stash_ref: str | None=None, checkpoint_path: str | None=None) -> ActionResultPersisted
```

**AGENTESE:** `self.witness.actions.record`

Record an action with rollback info.

---

## get_rollback_window

```python
async def get_rollback_window(self, hours: int=168, limit: int=100, reversible_only: bool=True) -> list[ActionResult]
```

**AGENTESE:** `self.witness.actions.rollback_window`

Get actions within the rollback window.

---

## manifest

```python
async def manifest(self) -> WitnessStatus
```

**AGENTESE:** `self.witness.manifest`

Get witness health status.

---

## services.witness.pipeline

## pipeline

```python
module pipeline
```

Cross-Jewel Pipeline: Composable Workflows Across Crown Jewels.

---

## PipelineStatus

```python
class PipelineStatus(Enum)
```

Status of a pipeline execution.

---

## Step

```python
class Step
```

A single step in a pipeline.

---

## Branch

```python
class Branch
```

Conditional branch in a pipeline.

---

## Pipeline

```python
class Pipeline
```

Composable pipeline of jewel invocations.

---

## StepResult

```python
class StepResult
```

Result of a single step execution.

---

## PipelineResult

```python
class PipelineResult
```

Result of a complete pipeline execution.

---

## PipelineRunner

```python
class PipelineRunner
```

Executes pipelines across Crown Jewels.

---

## step

```python
def step(path: str, **kwargs: Any) -> Step
```

Create a pipeline step (convenience function).

---

## branch

```python
def branch(condition: Callable[[Any], bool], if_true: Step | Pipeline, if_false: Step | Pipeline | None=None) -> Branch
```

Create a conditional branch (convenience function).

---

## PathPipeline

```python
class PathPipeline
```

Build pipelines from AGENTESE path strings.

---

## __rshift__

```python
def __rshift__(self, other: 'Step | Branch | Pipeline') -> 'Pipeline'
```

Compose with >> operator.

---

## __rrshift__

```python
def __rrshift__(self, other: str) -> 'Pipeline'
```

Allow string >> Step.

---

## __rshift__

```python
def __rshift__(self, other: 'Step | Branch | Pipeline') -> 'Pipeline'
```

Compose with >> operator.

---

## __rrshift__

```python
def __rrshift__(self, other: str) -> 'Pipeline'
```

Allow string >> Pipeline.

---

## __len__

```python
def __len__(self) -> int
```

Number of steps in pipeline.

---

## __iter__

```python
def __iter__(self) -> 'Iterator[Step | Branch]'
```

Iterate over steps.

---

## paths

```python
def paths(self) -> list[str]
```

Get all paths in the pipeline (flattened).

---

## success

```python
def success(self) -> bool
```

Check if pipeline completed successfully.

---

## failed_step

```python
def failed_step(self) -> StepResult | None
```

Get the first failed step, if any.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## run

```python
async def run(self, pipeline: Pipeline, initial_kwargs: dict[str, Any] | None=None) -> PipelineResult
```

Execute a pipeline.

---

## from_paths

```python
def from_paths(paths: list[str]) -> Pipeline
```

Create a Pipeline from a list of path strings.

---

## empty

```python
def empty() -> Pipeline
```

Create an empty pipeline for chaining.

---

## services.witness.playbook

## playbook

```python
module playbook
```

Playbook: Lawful Workflow Orchestration.

### Things to Know

🚨 **Critical:** Always verify Grant is GRANTED status before creating Playbook. Passing a PENDING or REVOKED Grant raises MissingGrant.
  - *Verified in: `test_playbook.py::test_grant_required`*

ℹ️ Phase transitions are DIRECTED—you cannot skip phases. SENSE → ACT → REFLECT → SENSE (cycle). InvalidPhaseTransition if wrong.
  - *Verified in: `test_playbook.py::test_phase_ordering`*

ℹ️ Guards evaluate at phase boundaries, not during phase. Budget exhaustion during ACT phase only fails at ACT → REFLECT.
  - *Verified in: `test_playbook.py::test_guard_evaluation`*

🚨 **Critical:** from_dict() does NOT restore _grant and _scope objects. You must reattach them manually after deserialization.
  - *Verified in: `test_playbook.py::test_serialization_roundtrip`*

---

## generate_playbook_id

```python
def generate_playbook_id() -> PlaybookId
```

Generate a unique Playbook ID.

---

## PlaybookStatus

```python
class PlaybookStatus(Enum)
```

Status of a Playbook.

---

## GuardResult

```python
class GuardResult(Enum)
```

Result of a guard check.

---

## SentinelGuard

```python
class SentinelGuard
```

A check that must pass at phase boundaries.

---

## GuardEvaluation

```python
class GuardEvaluation
```

Result of evaluating a guard.

---

## PlaybookPhase

```python
class PlaybookPhase
```

Single phase in a Playbook state machine.

---

## PlaybookError

```python
class PlaybookError(Exception)
```

Base exception for Playbook errors.

---

## PlaybookNotActive

```python
class PlaybookNotActive(PlaybookError)
```

Playbook is not in ACTIVE status.

---

## InvalidPhaseTransition

```python
class InvalidPhaseTransition(PlaybookError)
```

Law 4: Invalid phase transition attempted.

---

## GuardFailed

```python
class GuardFailed(PlaybookError)
```

Law 3: A guard check failed.

---

## MissingGrant

```python
class MissingGrant(PlaybookError)
```

Law 1: Playbook requires a Grant.

---

## MissingScope

```python
class MissingScope(PlaybookError)
```

Law 2: Playbook requires a Scope.

---

## Playbook

```python
class Playbook
```

Curator-orchestrated workflow with explicit gates.

### Examples
```python
>>> playbook = Playbook.create(
```
```python
>>> playbook.begin()
```
```python
>>> playbook.advance_phase(NPhase.ACT)
```
```python
>>> playbook.complete()
```

---

## PlaybookStore

```python
class PlaybookStore
```

Persistent storage for Playbooks.

---

## get_playbook_store

```python
def get_playbook_store() -> PlaybookStore
```

Get the global playbook store.

---

## reset_playbook_store

```python
def reset_playbook_store() -> None
```

Reset the global playbook store (for testing).

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> SentinelGuard
```

Create from dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> PlaybookPhase
```

Create from dictionary.

---

## create

```python
def create(cls, name: str, grant: Grant, scope: Scope, phases: list[PlaybookPhase] | None=None, description: str='') -> Playbook
```

Create a new Playbook with Grant and Scope.

---

## begin

```python
def begin(self) -> None
```

Begin the Playbook.

---

## complete

```python
def complete(self) -> None
```

Mark Playbook as successfully complete.

---

## fail

```python
def fail(self, reason: str='') -> None
```

Mark Playbook as failed.

---

## cancel

```python
def cancel(self, reason: str='') -> None
```

Cancel the Playbook.

---

## pause

```python
def pause(self) -> None
```

Pause the Playbook.

---

## resume

```python
def resume(self) -> None
```

Resume a paused Playbook.

---

## can_transition

```python
def can_transition(self, to_phase: NPhase) -> bool
```

Check if transition to phase is valid.

---

## advance_phase

```python
def advance_phase(self, to_phase: NPhase) -> bool
```

Advance to a new phase.

---

## add_guard

```python
def add_guard(self, guard: SentinelGuard) -> None
```

Add an entry guard to the Playbook.

---

## record_mark

```python
def record_mark(self, mark: Mark) -> None
```

Record a Mark emitted during this Playbook.

---

## record_trace

```python
def record_trace(self, trace: Mark) -> None
```

Record a Mark (backwards compat alias).

---

## mark_count

```python
def mark_count(self) -> int
```

Number of marks recorded.

---

## trace_count

```python
def trace_count(self) -> int
```

Number of marks recorded (backwards compat alias).

---

## covenant_id

```python
def covenant_id(self) -> GrantId | None
```

Backwards compat alias for grant_id.

---

## offering_id

```python
def offering_id(self) -> ScopeId | None
```

Backwards compat alias for scope_id.

---

## current_step

```python
def current_step(self) -> int
```

Backwards compat: phases are the new steps.

---

## total_steps

```python
def total_steps(self) -> int
```

Backwards compat: count of phases.

---

## grant

```python
def grant(self) -> Grant | None
```

Get the associated Grant.

---

## covenant

```python
def covenant(self) -> Grant | None
```

Get the associated Grant (backwards compat alias).

---

## scope

```python
def scope(self) -> Scope | None
```

Get the associated Scope.

---

## offering

```python
def offering(self) -> Scope | None
```

Get the associated Scope (backwards compat alias).

---

## is_active

```python
def is_active(self) -> bool
```

Check if Playbook is active.

---

## is_complete

```python
def is_complete(self) -> bool
```

Check if Playbook is complete.

---

## duration_seconds

```python
def duration_seconds(self) -> float | None
```

Duration of the Playbook in seconds.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Playbook
```

Create from dictionary (without Grant/Scope - must be reattached).

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## add

```python
def add(self, playbook: Playbook) -> None
```

Add a Playbook to the store.

---

## get

```python
def get(self, playbook_id: PlaybookId) -> Playbook | None
```

Get a Playbook by ID.

---

## active

```python
def active(self) -> list[Playbook]
```

Get all active Playbooks.

---

## recent

```python
def recent(self, limit: int=10) -> list[Playbook]
```

Get most recent Playbooks.

---

## services.witness.polynomial

## polynomial

```python
module polynomial
```

WitnessPolynomial: Trust-Gated Behavior as State Machine.

### Examples
```python
>>> poly = WITNESS_POLYNOMIAL
```
```python
>>> state, output = poly.invoke(
```
```python
>>> print(output)
```
```python
>>> poly = WITNESS_POLYNOMIAL
```
```python
>>> state, output = poly.invoke(
```

---

## TrustLevel

```python
class TrustLevel(IntEnum)
```

Trust levels for the Witness.

---

## WitnessPhase

```python
class WitnessPhase(Enum)
```

Activity phases for the Witness.

---

## GitEvent

```python
class GitEvent
```

A git event detected by the GitWatcher.

---

## FileEvent

```python
class FileEvent
```

A filesystem event detected by the FileSystemWatcher.

---

## TestEvent

```python
class TestEvent
```

A test event detected by the TestWatcher.

---

## AgenteseEvent

```python
class AgenteseEvent
```

An AGENTESE event from SynergyBus.

---

## CIEvent

```python
class CIEvent
```

A CI/CD event from GitHub Actions.

---

## StartCommand

```python
class StartCommand
```

Command to start the witness.

---

## StopCommand

```python
class StopCommand
```

Command to stop the witness.

---

## EscalateCommand

```python
class EscalateCommand
```

Request trust escalation.

---

## ConfirmCommand

```python
class ConfirmCommand
```

Human confirmation for L2 suggestions.

---

## ActCommand

```python
class ActCommand
```

L3 action command.

---

## WitnessInputFactory

```python
class WitnessInputFactory
```

Factory for creating witness inputs.

---

## Thought

```python
class Thought
```

A thought in the thought stream.

---

## Suggestion

```python
class Suggestion
```

A suggested action (L2+).

---

## ActionResult

```python
class ActionResult
```

Result of an executed action (L3).

---

## WitnessOutput

```python
class WitnessOutput
```

Output from witness transitions.

---

## WitnessState

```python
class WitnessState
```

Complete witness state.

---

## witness_directions

```python
def witness_directions(state: WitnessState) -> FrozenSet[Any]
```

Valid inputs for each witness state.

---

## witness_transition

```python
def witness_transition(state: WitnessState, input: WitnessInput) -> tuple[WitnessState, WitnessOutput]
```

Witness state transition function.

---

## WitnessPolynomial

```python
class WitnessPolynomial
```

The Witness polynomial agent.

---

## can_write_kgents

```python
def can_write_kgents(self) -> bool
```

Can write to .kgents/ directory.

---

## can_suggest

```python
def can_suggest(self) -> bool
```

Can propose code changes for human review.

---

## can_act

```python
def can_act(self) -> bool
```

Can execute actions without human confirmation.

---

## emoji

```python
def emoji(self) -> str
```

Visual indicator for trust level.

---

## description

```python
def description(self) -> str
```

Human-readable description.

---

## git_commit

```python
def git_commit(sha: str, message: str='', author: str='') -> GitEvent
```

Create a git commit event.

---

## git_push

```python
def git_push(branch: str) -> GitEvent
```

Create a git push event.

---

## file_changed

```python
def file_changed(path: str) -> FileEvent
```

Create a file change event.

---

## test_failed

```python
def test_failed(test_id: str, error: str) -> TestEvent
```

Create a test failure event.

---

## test_session

```python
def test_session(passed: int, failed: int, skipped: int) -> TestEvent
```

Create a test session complete event.

---

## start

```python
def start(watchers: tuple[str, ...]=('git',)) -> StartCommand
```

Create a start command.

---

## stop

```python
def stop() -> StopCommand
```

Create a stop command.

---

## to_diary_line

```python
def to_diary_line(self) -> str
```

Format as a diary entry.

---

## add_thought

```python
def add_thought(self, thought: Thought) -> None
```

Add a thought to history (bounded).

---

## add_suggestion

```python
def add_suggestion(self, suggestion: Suggestion) -> None
```

Add a suggestion to history (bounded).

---

## add_action

```python
def add_action(self, action: ActionResult) -> None
```

Add an action to history (bounded).

---

## confirm_suggestion

```python
def confirm_suggestion(self, approved: bool) -> None
```

Record a suggestion confirmation.

---

## acceptance_rate

```python
def acceptance_rate(self) -> float
```

Suggestion acceptance rate.

---

## can_escalate_to_bounded

```python
def can_escalate_to_bounded(self) -> bool
```

Check if eligible for L0 → L1 escalation.

---

## can_escalate_to_suggestion

```python
def can_escalate_to_suggestion(self) -> bool
```

Check if eligible for L1 → L2 escalation.

---

## can_escalate_to_autonomous

```python
def can_escalate_to_autonomous(self) -> bool
```

Check if eligible for L2 → L3 escalation.

---

## positions

```python
def positions(self) -> FrozenSet[TrustLevel]
```

Trust levels are the primary positions.

---

## directions

```python
def directions(self, state: WitnessState) -> FrozenSet[Any]
```

Valid inputs at this state.

---

## transition

```python
def transition(self, state: WitnessState, input: WitnessInput) -> tuple[WitnessState, WitnessOutput]
```

Execute state transition.

---

## invoke

```python
def invoke(self, state: WitnessState, input: WitnessInput) -> tuple[WitnessState, WitnessOutput]
```

Invoke the polynomial (alias for transition).

---

## services.witness.reactor

## reactor

```python
module reactor
```

Witness Reactor: Event-to-Workflow Mapping.

---

## EventSource

```python
class EventSource(Enum)
```

Sources of events the reactor can subscribe to.

---

## Event

```python
class Event
```

A generic event that the reactor can respond to.

---

## git_commit_event

```python
def git_commit_event(sha: str, message: str, author: str='', files_changed: list[str] | None=None) -> Event
```

Create a git commit event.

---

## create_test_failure_event

```python
def create_test_failure_event(test_file: str, test_name: str, error_message: str='', traceback: str='') -> Event
```

Create a test failure event.

---

## pr_opened_event

```python
def pr_opened_event(pr_number: int, title: str, author: str='', base_branch: str='main', head_branch: str='') -> Event
```

Create a PR opened event.

---

## ci_status_event

```python
def ci_status_event(status: str, pipeline_name: str='', url: str='') -> Event
```

Create a CI status event.

---

## session_start_event

```python
def session_start_event(session_id: str='', context: str='') -> Event
```

Create a session start event.

---

## health_tick_event

```python
def health_tick_event() -> Event
```

Create a health check tick event.

---

## crystallization_ready_event

```python
def crystallization_ready_event(session_id: str, thought_count: int) -> Event
```

Create a crystallization ready event.

---

## ReactionStatus

```python
class ReactionStatus(Enum)
```

Status of a reaction.

---

## Reaction

```python
class Reaction
```

A pending or completed reaction to an event.

---

## EventMapping

```python
class EventMapping
```

Maps an event pattern to a workflow.

---

## EventHandler

```python
class EventHandler(Protocol)
```

Protocol for event handlers.

---

## WitnessReactor

```python
class WitnessReactor
```

The Witness's event-to-workflow reactor.

---

## create_reactor

```python
def create_reactor(invoker: 'JewelInvoker | None'=None, scheduler: 'WitnessScheduler | None'=None, observer: 'Observer | None'=None) -> WitnessReactor
```

Create a WitnessReactor instance.

---

## is_approved

```python
def is_approved(self) -> bool
```

Check if reaction has trust approval.

---

## can_run

```python
def can_run(self) -> bool
```

Check if reaction can run now.

---

## is_expired

```python
def is_expired(self) -> bool
```

Check if pending reaction has expired.

---

## approve

```python
def approve(self, trust_level: TrustLevel) -> bool
```

Approve reaction with given trust level.

---

## reject

```python
def reject(self, reason: str='') -> None
```

Reject the reaction.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## matches

```python
def matches(self, event: Event) -> bool
```

Check if this mapping matches an event.

---

## __call__

```python
async def __call__(self, event: Event) -> None
```

Handle an event.

---

## react

```python
async def react(self, event: Event) -> Reaction | None
```

React to an event.

---

## approve

```python
def approve(self, reaction_id: str, trust_level: TrustLevel) -> bool
```

Approve a pending reaction with given trust level.

---

## reject

```python
def reject(self, reaction_id: str, reason: str='') -> bool
```

Reject a pending reaction.

---

## add_mapping

```python
def add_mapping(self, mapping: EventMapping) -> None
```

Add a custom event-workflow mapping.

---

## remove_mapping

```python
def remove_mapping(self, source: EventSource, event_type: str) -> bool
```

Remove a mapping by source and event type.

---

## subscribe

```python
def subscribe(self, source: EventSource, handler: EventHandler) -> None
```

Subscribe a handler to an event source.

---

## unsubscribe

```python
def unsubscribe(self, source: EventSource, handler: EventHandler) -> None
```

Unsubscribe a handler from an event source.

---

## pending_reactions

```python
def pending_reactions(self) -> list[Reaction]
```

Get all pending reactions.

---

## active_reactions

```python
def active_reactions(self) -> list[Reaction]
```

Get all active (pending or running) reactions.

---

## get_reaction

```python
def get_reaction(self, reaction_id: str) -> Reaction | None
```

Get a reaction by ID.

---

## get_stats

```python
def get_stats(self) -> dict[str, Any]
```

Get reactor statistics.

---

## cleanup_expired

```python
def cleanup_expired(self) -> int
```

Remove expired pending reactions. Returns count removed.

---

## services.witness.schedule

## schedule

```python
module schedule
```

Witness Scheduler: Temporal Composition for Cross-Jewel Workflows.

---

## ScheduleType

```python
class ScheduleType(Enum)
```

Type of schedule.

---

## ScheduleStatus

```python
class ScheduleStatus(Enum)
```

Status of a scheduled task.

---

## ScheduledTask

```python
class ScheduledTask
```

A task scheduled for future execution.

---

## WitnessScheduler

```python
class WitnessScheduler
```

The Witness's temporal execution engine.

---

## create_scheduler

```python
def create_scheduler(invoker: JewelInvoker, observer: 'Observer', tick_interval: float=1.0, max_concurrent: int=5) -> WitnessScheduler
```

Create a WitnessScheduler instance.

---

## delay

```python
def delay(minutes: int=0, seconds: int=0, hours: int=0) -> timedelta
```

Create a timedelta for scheduling delays.

---

## every

```python
def every(minutes: int=0, seconds: int=0, hours: int=0) -> timedelta
```

Create a timedelta for periodic intervals.

---

## __lt__

```python
def __lt__(self, other: ScheduledTask) -> bool
```

Enable heapq ordering by next_run time.

---

## is_due

```python
def is_due(self) -> bool
```

Check if task is due for execution.

---

## is_active

```python
def is_active(self) -> bool
```

Check if task is still active (pending or running).

---

## can_run

```python
def can_run(self) -> bool
```

Check if task can run (not cancelled, not paused).

---

## advance_periodic

```python
def advance_periodic(self) -> None
```

Advance next_run for periodic tasks.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## schedule

```python
def schedule(self, path: str, at: datetime | None=None, delay: timedelta | None=None, name: str='', description: str='', tags: frozenset[str] | None=None, **kwargs: Any) -> ScheduledTask
```

Schedule a single AGENTESE invocation.

---

## schedule_pipeline

```python
def schedule_pipeline(self, pipeline: Pipeline, at: datetime | None=None, delay: timedelta | None=None, name: str='', description: str='', tags: frozenset[str] | None=None, initial_kwargs: dict[str, Any] | None=None) -> ScheduledTask
```

Schedule a pipeline for future execution.

---

## schedule_periodic

```python
def schedule_periodic(self, path: str, interval: timedelta, name: str='', description: str='', max_runs: int | None=None, start_immediately: bool=False, tags: frozenset[str] | None=None, **kwargs: Any) -> ScheduledTask
```

Schedule a periodic invocation.

---

## get_task

```python
def get_task(self, task_id: str) -> ScheduledTask | None
```

Get a task by ID.

---

## cancel

```python
def cancel(self, task_id: str) -> bool
```

Cancel a scheduled task.

---

## pause

```python
def pause(self, task_id: str) -> bool
```

Pause a periodic task.

---

## resume

```python
def resume(self, task_id: str) -> bool
```

Resume a paused task.

---

## tick

```python
async def tick(self) -> list[ScheduledTask]
```

Process all due tasks.

---

## run

```python
async def run(self) -> None
```

Run the scheduler loop.

---

## stop

```python
def stop(self) -> None
```

Stop the scheduler loop.

---

## pending_tasks

```python
def pending_tasks(self) -> list[ScheduledTask]
```

Get all pending tasks.

---

## active_tasks

```python
def active_tasks(self) -> list[ScheduledTask]
```

Get all active (pending or running) tasks.

---

## get_stats

```python
def get_stats(self) -> dict[str, Any]
```

Get scheduler statistics.

---

## services.witness.scope

## scope

```python
module scope
```

Scope: Explicit Context Contract with Budget Constraints.

---

## generate_scope_id

```python
def generate_scope_id() -> ScopeId
```

Generate a unique Scope ID.

---

## Budget

```python
class Budget
```

Resource constraints for a Scope.

### Examples
```python
>>> budget = Budget(tokens=10000, time_seconds=300.0, operations=50)
```
```python
>>> budget.can_consume(tokens=100)  # True
```
```python
>>> budget.remaining_after(tokens=100)  # Budget(tokens=9900, ...)
```

---

## ScopeError

```python
class ScopeError(Exception)
```

Base exception for Scope errors.

---

## BudgetExceeded

```python
class BudgetExceeded(ScopeError)
```

Law 1: Budget constraint exceeded - triggers review.

---

## ScopeExpired

```python
class ScopeExpired(ScopeError)
```

Law 3: Scope has expired.

---

## HandleNotInScope

```python
class HandleNotInScope(ScopeError)
```

Attempted to access a handle not in the Scope's scope.

---

## ScopeStatus

```python
class ScopeStatus(Enum)
```

Status of a Scope.

---

## Scope

```python
class Scope
```

Explicitly priced and scoped context contract.

### Examples
```python
>>> scope = Scope.create(
```
```python
>>> scope.is_valid()  # True
```
```python
>>> scope.can_access("time.trace.node.manifest")  # True
```
```python
>>> scope.can_access("self.lesson.manifest")  # False (not in scope)
```

---

## ScopeStore

```python
class ScopeStore
```

Persistent storage for Scopes.

---

## get_scope_store

```python
def get_scope_store() -> ScopeStore
```

Get the global scope store.

---

## reset_scope_store

```python
def reset_scope_store() -> None
```

Reset the global scope store (for testing).

---

## can_consume

```python
def can_consume(self, tokens: int=0, time_seconds: float=0.0, operations: int=0, capital: float=0.0, entropy: float=0.0) -> bool
```

Check if consumption would stay within budget.

---

## remaining_after

```python
def remaining_after(self, tokens: int=0, time_seconds: float=0.0, operations: int=0, capital: float=0.0, entropy: float=0.0) -> Budget
```

Return a new Budget with consumption deducted.

---

## is_exhausted

```python
def is_exhausted(self) -> bool
```

Check if any budget dimension is at zero.

---

## unlimited

```python
def unlimited(cls) -> Budget
```

Create an unlimited budget (all None).

---

## standard

```python
def standard(cls) -> Budget
```

Create a standard budget for typical operations.

---

## minimal

```python
def minimal(cls) -> Budget
```

Create a minimal budget for quick operations.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for serialization.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Budget
```

Create from dictionary.

---

## create

```python
def create(cls, description: str, scoped_handles: tuple[str, ...] | None=None, budget: Budget | None=None, duration: timedelta | None=None, expires_at: datetime | None=None) -> Scope
```

Create a new Scope.

---

## is_valid

```python
def is_valid(self) -> bool
```

Check if this Scope is currently valid.

---

## check_valid

```python
def check_valid(self) -> None
```

Raise ScopeExpired if not valid.

---

## time_remaining

```python
def time_remaining(self) -> timedelta | None
```

Get remaining time until expiry (None if no expiry).

---

## can_access

```python
def can_access(self, handle: str) -> bool
```

Check if a handle is within scope.

---

## check_access

```python
def check_access(self, handle: str) -> None
```

Raise HandleNotInScope if handle is not accessible.

---

## can_consume

```python
def can_consume(self, tokens: int=0, time_seconds: float=0.0, operations: int=0) -> bool
```

Check if consumption would stay within budget.

---

## consume

```python
def consume(self, tokens: int=0, time_seconds: float=0.0, operations: int=0) -> Scope
```

Return new Scope with consumption deducted.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for persistence.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Scope
```

Create from dictionary.

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## kind

```python
def kind(self) -> str
```

Backwards compat: all scopes are 'resource' kind.

---

## scope

```python
def scope(self) -> tuple[str, ...]
```

Backwards compat: alias for scoped_handles.

---

## add

```python
def add(self, scope: Scope) -> None
```

Add a Scope to the store.

---

## get

```python
def get(self, scope_id: ScopeId) -> Scope | None
```

Get a Scope by ID.

---

## update

```python
def update(self, scope: Scope) -> None
```

Update a Scope (replace with new version).

---

## active

```python
def active(self) -> list[Scope]
```

Get all currently valid Scopes.

---

## expired

```python
def expired(self) -> list[Scope]
```

Get all expired Scopes.

---

## services.witness.session_walk

## session_walk

```python
module session_walk
```

Session-Walk Bridge: Connects CLI Sessions to WARP Walks.

---

## SessionWalkBinding

```python
class SessionWalkBinding
```

Binding between a CLI session and its Walk.

---

## SessionWalkBridge

```python
class SessionWalkBridge
```

Bridge for connecting CLI sessions to WARP Walks.

---

## get_session_walk_bridge

```python
def get_session_walk_bridge() -> SessionWalkBridge
```

Get the global session-walk bridge.

---

## reset_session_walk_bridge

```python
def reset_session_walk_bridge() -> None
```

Reset the global bridge (for testing).

---

## __init__

```python
def __init__(self, walk_store: WalkStore | None=None) -> None
```

Initialize bridge.

---

## start_walk_for_session

```python
def start_walk_for_session(self, cli_session_id: str, goal: str, *, root_plan: str | PlanPath | None=None, session_name: str='') -> Walk
```

Create and bind a Walk to a CLI session.

---

## get_walk_for_session

```python
def get_walk_for_session(self, cli_session_id: str) -> Walk | None
```

Get the Walk bound to a CLI session.

---

## has_walk

```python
def has_walk(self, cli_session_id: str) -> bool
```

Check if a CLI session has a Walk bound.

---

## advance_walk

```python
def advance_walk(self, cli_session_id: str, trace_node: Mark) -> bool
```

Add a Mark to the session's Walk.

---

## transition_phase_for_session

```python
def transition_phase_for_session(self, cli_session_id: str, to_phase: str) -> bool
```

Transition the Walk's N-Phase.

---

## pause_walk

```python
def pause_walk(self, cli_session_id: str) -> bool
```

Pause the Walk when session pauses.

---

## resume_walk

```python
def resume_walk(self, cli_session_id: str) -> bool
```

Resume a paused Walk.

---

## end_session

```python
def end_session(self, cli_session_id: str, *, complete: bool=True) -> Walk | None
```

Handle CLI session end.

---

## active_sessions_with_walks

```python
def active_sessions_with_walks(self) -> list[str]
```

Get CLI session IDs that have active Walks.

---

## services.witness.sheaf

## sheaf

```python
module sheaf
```

WitnessSheaf: Emergence from Event Sources to Coherent Crystals.

---

## EventSource

```python
class EventSource(Enum)
```

Contexts in the Witness observation topology.

---

## source_overlap

```python
def source_overlap(s1: EventSource, s2: EventSource) -> frozenset[str]
```

Compute capability overlap between event sources.

---

## LocalObservation

```python
class LocalObservation
```

A local view from a single event source.

---

## GluingError

```python
class GluingError(Exception)
```

Raised when local observations cannot be glued.

---

## WitnessSheaf

```python
class WitnessSheaf
```

Sheaf structure for gluing event source observations into crystals.

### Examples
```python
>>> sheaf = WitnessSheaf()
```
```python
>>> obs1 = LocalObservation(EventSource.GIT, git_thoughts, t0, t1)
```
```python
>>> obs2 = LocalObservation(EventSource.TESTS, test_thoughts, t0, t1)
```
```python
>>> if sheaf.compatible([obs1, obs2]):
```

---

## verify_identity_law

```python
def verify_identity_law(sheaf: WitnessSheaf, observation: LocalObservation, session_id: str='test') -> bool
```

Verify the identity law: glue([single_source]) ≅ from_thoughts(source.thoughts).

---

## verify_associativity_law

```python
def verify_associativity_law(sheaf: WitnessSheaf, obs_a: LocalObservation, obs_b: LocalObservation, obs_c: LocalObservation, session_id: str='test') -> bool
```

Verify the associativity law: glue(glue([A, B]), C) ≅ glue(A, glue([B, C])).

---

## capabilities

```python
def capabilities(self) -> frozenset[str]
```

Capabilities this source provides.

---

## duration_seconds

```python
def duration_seconds(self) -> float
```

Duration of this observation window.

---

## thought_count

```python
def thought_count(self) -> int
```

Number of thoughts in this observation.

---

## overlaps_temporally

```python
def overlaps_temporally(self, other: LocalObservation) -> bool
```

Check if time windows overlap.

---

## __init__

```python
def __init__(self, time_tolerance: timedelta=timedelta(minutes=5)) -> None
```

Initialize the WitnessSheaf.

---

## overlap

```python
def overlap(self, s1: EventSource, s2: EventSource) -> frozenset[str]
```

Compute the overlap between two event sources.

---

## compatible

```python
def compatible(self, observations: Sequence[LocalObservation]) -> bool
```

Check if local observations can be glued.

---

## glue

```python
def glue(self, observations: Sequence[LocalObservation], session_id: str='', markers: list[str] | None=None, narrative: Narrative | None=None) -> ExperienceCrystal
```

Glue local observations into a coherent ExperienceCrystal.

---

## restrict

```python
def restrict(self, crystal: ExperienceCrystal, source: EventSource) -> LocalObservation
```

Restrict a crystal back to a single source view.

---

## services.witness.trace_store

## trace_store

```python
module trace_store
```

MarkStore: Append-Only Ledger for Marks.

---

## MarkStoreError

```python
class MarkStoreError(Exception)
```

Base exception for trace store errors.

---

## CausalityViolation

```python
class CausalityViolation(MarkStoreError)
```

Raised when a MarkLink violates causality (Law 2).

---

## DuplicateMarkError

```python
class DuplicateMarkError(MarkStoreError)
```

Raised when attempting to add a trace with an existing ID.

---

## MarkNotFoundError

```python
class MarkNotFoundError(MarkStoreError)
```

Raised when a referenced trace is not found.

---

## MarkQuery

```python
class MarkQuery
```

Query parameters for trace retrieval.

---

## MarkStore

```python
class MarkStore
```

Append-only ledger for Marks.

### Examples
```python
>>> store = MarkStore()
```
```python
>>> node = Mark.from_thought("Test", "git", ("test",))
```
```python
>>> store.append(node)
```
```python
>>> retrieved = store.get(node.id)
```
```python
>>> assert retrieved == node
```

---

## get_mark_store

```python
def get_mark_store() -> MarkStore
```

Get the global trace store (singleton).

---

## set_mark_store

```python
def set_mark_store(store: MarkStore) -> None
```

Set the global trace store (for testing).

---

## reset_mark_store

```python
def reset_mark_store() -> None
```

Reset the global trace store (for testing).

---

## matches

```python
def matches(self, node: Mark, store: MarkStore) -> bool
```

Check if a trace node matches this query.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize secondary indices.

---

## append

```python
def append(self, node: Mark) -> None
```

Append a Mark to the ledger.

---

## get

```python
def get(self, trace_id: MarkId) -> Mark | None
```

Get a Mark by ID.

---

## get_or_raise

```python
def get_or_raise(self, trace_id: MarkId) -> Mark
```

Get a Mark by ID, raising if not found.

---

## query

```python
def query(self, query: MarkQuery) -> Iterator[Mark]
```

Query traces matching the given criteria.

---

## count

```python
def count(self, query: MarkQuery | None=None) -> int
```

Count traces matching the query (or all traces if no query).

---

## all

```python
def all(self) -> Iterator[Mark]
```

Iterate over all traces in timestamp order.

---

## recent

```python
def recent(self, limit: int=10) -> list[Mark]
```

Get the most recent traces.

---

## get_causes

```python
def get_causes(self, trace_id: MarkId) -> list[Mark]
```

Get all traces that caused this trace (incoming CAUSES links).

---

## get_effects

```python
def get_effects(self, trace_id: MarkId) -> list[Mark]
```

Get all traces caused by this trace (outgoing CAUSES links).

---

## get_continuation

```python
def get_continuation(self, trace_id: MarkId) -> list[Mark]
```

Get traces that continue this trace (CONTINUES relation).

---

## get_branches

```python
def get_branches(self, trace_id: MarkId) -> list[Mark]
```

Get traces that branch from this trace (BRANCHES relation).

---

## get_fulfillments

```python
def get_fulfillments(self, trace_id: MarkId) -> list[Mark]
```

Get traces that fulfill intents in this trace (FULFILLS relation).

---

## get_walk_traces

```python
def get_walk_traces(self, walk_id: WalkId) -> list[Mark]
```

Get all traces in a specific Walk.

---

## save

```python
def save(self, path: Path | str) -> None
```

Save the store to a JSON file.

---

## load

```python
def load(cls, path: Path | str) -> MarkStore
```

Load a store from a JSON file.

---

## sync

```python
def sync(self) -> None
```

Sync to persistence path if set.

---

## stats

```python
def stats(self) -> dict[str, Any]
```

Get store statistics.

---

## __len__

```python
def __len__(self) -> int
```

Return the number of traces in the store.

---

## __contains__

```python
def __contains__(self, trace_id: MarkId) -> bool
```

Check if a trace ID exists in the store.

---

## services.witness.trust.__init__

## __init__

```python
module __init__
```

Witness Trust System: Earned Autonomy Through Demonstrated Competence.

---

## services.witness.trust.boundaries

## boundaries

```python
module boundaries
```

BoundaryChecker: Forbidden Actions That Should Never Be Autonomous.

---

## BoundaryViolation

```python
class BoundaryViolation
```

A detected boundary violation.

---

## BoundaryChecker

```python
class BoundaryChecker
```

Checks actions against forbidden boundaries.

---

## __init__

```python
def __init__(self, forbidden_actions: frozenset[str] | None=None, forbidden_substrings: frozenset[str] | None=None) -> None
```

Initialize boundary checker.

---

## check

```python
def check(self, action: str) -> BoundaryViolation | None
```

Check if an action violates boundaries.

---

## is_allowed

```python
def is_allowed(self, action: str) -> bool
```

Quick check if action is allowed.

---

## services.witness.trust.confirmation

## confirmation

```python
module confirmation
```

ConfirmationManager: Level 2 Suggestion Confirmation Flow.

---

## SuggestionStatus

```python
class SuggestionStatus(Enum)
```

Status of a pending suggestion.

---

## ActionPreview

```python
class ActionPreview
```

Preview of what an action will do.

---

## PendingSuggestion

```python
class PendingSuggestion
```

A suggestion awaiting human confirmation.

---

## ConfirmationResult

```python
class ConfirmationResult
```

Result of a confirmation action.

---

## ConfirmationManager

```python
class ConfirmationManager
```

Manages pending suggestions awaiting confirmation.

---

## is_expired

```python
def is_expired(self) -> bool
```

Check if suggestion has expired.

---

## time_remaining

```python
def time_remaining(self) -> timedelta
```

Time remaining before expiration.

---

## to_display

```python
def to_display(self) -> dict[str, Any]
```

Format for human review.

---

## __init__

```python
def __init__(self, notification_handler: Callable[[PendingSuggestion], Coroutine[Any, Any, None]] | None=None, execution_handler: Callable[[str], Coroutine[Any, Any, tuple[bool, str]]] | None=None, pipeline_runner: Any | None=None, expiration_hours: float=1.0) -> None
```

Initialize confirmation manager.

---

## set_pipeline_runner

```python
def set_pipeline_runner(self, runner: Any) -> None
```

Set the pipeline runner for workflow execution.

---

## submit

```python
async def submit(self, action: str, rationale: str, confidence: float=0.5, target: str | None=None, preview: ActionPreview | None=None, pipeline: Any | None=None, initial_kwargs: dict[str, Any] | None=None) -> PendingSuggestion
```

Submit a suggestion for confirmation.

---

## confirm

```python
async def confirm(self, suggestion_id: str, confirmed_by: str='user') -> ConfirmationResult
```

Confirm a pending suggestion.

---

## reject

```python
async def reject(self, suggestion_id: str, reason: str='') -> ConfirmationResult
```

Reject a pending suggestion.

---

## expire_stale

```python
async def expire_stale(self) -> int
```

Expire suggestions that have timed out.

---

## get_pending

```python
def get_pending(self) -> list[PendingSuggestion]
```

Get all pending suggestions.

---

## get_suggestion

```python
def get_suggestion(self, suggestion_id: str) -> PendingSuggestion | None
```

Get a specific suggestion.

---

## acceptance_rate

```python
def acceptance_rate(self) -> float
```

Calculate acceptance rate for escalation metrics.

---

## stats

```python
def stats(self) -> dict[str, int | float]
```

Get manager statistics.

---

## clear

```python
def clear(self) -> None
```

Clear all pending suggestions (for testing).

---

## services.witness.trust.escalation

## escalation

```python
module escalation
```

Escalation Criteria: Rules for Trust Level Transitions.

---

## ObservationStats

```python
class ObservationStats
```

Statistics for L0 → L1 escalation.

---

## OperationStats

```python
class OperationStats
```

Statistics for L1 → L2 escalation.

---

## SuggestionStats

```python
class SuggestionStats
```

Statistics for L2 → L3 escalation.

---

## EscalationResult

```python
class EscalationResult
```

Result of an escalation check.

---

## EscalationCriteria

```python
class EscalationCriteria(ABC, Generic[StatsT])
```

Abstract base for escalation criteria.

---

## Level1Criteria

```python
class Level1Criteria(EscalationCriteria[ObservationStats])
```

Criteria for L0 → L1 escalation.

---

## Level2Criteria

```python
class Level2Criteria(EscalationCriteria[OperationStats])
```

Criteria for L1 → L2 escalation.

---

## Level3Criteria

```python
class Level3Criteria(EscalationCriteria[SuggestionStats])
```

Criteria for L2 → L3 escalation.

---

## check_escalation

```python
def check_escalation(current_level: TrustLevel, stats: ObservationStats | OperationStats | SuggestionStats) -> EscalationResult | None
```

Check if escalation is possible from current level.

---

## false_positive_rate

```python
def false_positive_rate(self) -> float
```

Calculate false positive rate.

---

## failure_rate

```python
def failure_rate(self) -> float
```

Calculate failure rate.

---

## acceptance_rate

```python
def acceptance_rate(self) -> float
```

Calculate acceptance rate.

---

## progress_summary

```python
def progress_summary(self) -> str
```

Human-readable progress summary.

---

## from_level

```python
def from_level(self) -> TrustLevel
```

Source trust level.

---

## to_level

```python
def to_level(self) -> TrustLevel
```

Target trust level.

---

## check

```python
def check(self, stats: StatsT) -> EscalationResult
```

Check if escalation criteria are met.

---

## check

```python
def check(self, stats: ObservationStats) -> EscalationResult
```

Check if L1 criteria are met.

---

## check

```python
def check(self, stats: OperationStats) -> EscalationResult
```

Check if L2 criteria are met.

---

## check

```python
def check(self, stats: SuggestionStats) -> EscalationResult
```

Check if L3 criteria are met.

---

## services.witness.trust.gate

## gate

```python
module gate
```

ActionGate: Trust-Gated Execution for Witness Actions.

### Examples
```python
>>> gate = ActionGate(TrustLevel.SUGGESTION)
```
```python
>>> result = await gate.check("git commit -m 'fix: typo'")
```
```python
>>> print(result.decision)
```
```python
>>> gate = ActionGate(TrustLevel.SUGGESTION)
```
```python
>>> result = await gate.check("git commit -m 'fix: typo'")
```

---

## GateDecision

```python
class GateDecision(Enum)
```

Decision from the action gate.

---

## GateResult

```python
class GateResult
```

Result of gating an action.

---

## get_required_level

```python
def get_required_level(action: str) -> TrustLevel
```

Determine required trust level for an action.

---

## ActionGate

```python
class ActionGate
```

Gates actions based on trust level.

---

## is_allowed

```python
def is_allowed(self) -> bool
```

Check if action is allowed (ALLOW or LOG).

---

## requires_confirmation

```python
def requires_confirmation(self) -> bool
```

Check if action requires confirmation.

---

## is_denied

```python
def is_denied(self) -> bool
```

Check if action is denied.

---

## check

```python
def check(self, action: str, target: str | None=None) -> GateResult
```

Check if an action is allowed at the current trust level.

---

## can_perform

```python
def can_perform(self, capability: str) -> bool
```

Quick check if a capability is available at current trust level.

---

## update_trust

```python
def update_trust(self, new_level: TrustLevel) -> None
```

Update the trust level.

---

## services.witness.trust_persistence

## trust_persistence

```python
module trust_persistence
```

TrustPersistence: JSON-Based State Persistence for the Witness Daemon.

---

## PersistedTrustState

```python
class PersistedTrustState
```

Trust state that persists across daemon restarts.

---

## TrustPersistence

```python
class TrustPersistence
```

Manages persistence of witness trust state to disk.

---

## create_trust_persistence

```python
def create_trust_persistence(state_file: Path | None=None) -> TrustPersistence
```

Create a TrustPersistence instance.

---

## trust

```python
def trust(self) -> TrustLevel
```

Get trust level as TrustLevel enum.

---

## last_active

```python
def last_active(self) -> datetime | None
```

Get last_active as datetime.

---

## acceptance_rate

```python
def acceptance_rate(self) -> float
```

Calculate suggestion acceptance rate.

---

## apply_decay

```python
def apply_decay(self) -> bool
```

Apply trust decay based on inactivity.

---

## touch

```python
def touch(self) -> None
```

Update last_active to now.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to JSON-serializable dict.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> 'PersistedTrustState'
```

Create from dictionary.

---

## __init__

```python
def __init__(self, state_file: Path | None=None, auto_save: bool=True) -> None
```

Initialize trust persistence.

---

## current_state

```python
def current_state(self) -> PersistedTrustState
```

Get current state (load if not loaded).

---

## load

```python
async def load(self, apply_decay: bool=True) -> PersistedTrustState
```

Load trust state from disk.

---

## save

```python
async def save(self, state: PersistedTrustState | None=None) -> bool
```

Save trust state to disk.

---

## record_observation

```python
async def record_observation(self) -> None
```

Record an observation and auto-save if enabled.

---

## record_operation

```python
async def record_operation(self, success: bool=True) -> None
```

Record a bounded operation and auto-save if enabled.

---

## record_suggestion

```python
async def record_suggestion(self, confirmed: bool) -> None
```

Record a suggestion response and auto-save if enabled.

---

## escalate

```python
async def escalate(self, to_level: TrustLevel, reason: str='') -> bool
```

Escalate trust level.

---

## get_status

```python
def get_status(self) -> dict[str, Any]
```

Get current trust status for display.

---

## services.witness.tui

## tui

```python
module tui
```

Witness TUI: Textual Terminal User Interface for kgentsd.

---

## StatusPanel

```python
class StatusPanel(Static)
```

Status panel showing Witness state with trust escalation progress.

---

## ThoughtStream

```python
class ThoughtStream(RichLog)
```

Real-time thought stream display.

---

## SuggestionPrompt

```python
class SuggestionPrompt(Static)
```

L2 confirmation prompt with keyboard handling.

---

## WitnessApp

```python
class WitnessApp(App[None])
```

The Witness daemon TUI application.

---

## run_witness_tui

```python
def run_witness_tui(config: DaemonConfig) -> int
```

Run the Witness TUI application.

---

## add_thought

```python
def add_thought(self, thought: Thought) -> None
```

Add a thought to the stream.

---

## SuggestionAccepted

```python
class SuggestionAccepted(Message)
```

Emitted when user accepts a suggestion.

---

## SuggestionRejected

```python
class SuggestionRejected(Message)
```

Emitted when user rejects a suggestion.

---

## SuggestionIgnored

```python
class SuggestionIgnored(Message)
```

Emitted when user ignores a suggestion.

---

## watch_suggestion

```python
def watch_suggestion(self, suggestion: PendingSuggestion | None) -> None
```

Update display when suggestion changes.

---

## watch_is_visible

```python
def watch_is_visible(self, is_visible: bool) -> None
```

Show/hide the widget.

---

## on_key

```python
async def on_key(self, event: Any) -> None
```

Handle keyboard input for suggestion actions.

---

## show_suggestion

```python
def show_suggestion(self, suggestion: PendingSuggestion) -> None
```

Display a new suggestion.

---

## hide

```python
def hide(self) -> None
```

Hide the prompt.

---

## on_mount

```python
async def on_mount(self) -> None
```

Start the daemon when the app mounts.

---

## action_clear

```python
def action_clear(self) -> None
```

Clear the thought stream.

---

## action_status

```python
def action_status(self) -> None
```

Show detailed status.

---

## action_help

```python
def action_help(self) -> None
```

Show help.

---

## action_accept_suggestion

```python
async def action_accept_suggestion(self) -> None
```

Accept the current suggestion.

---

## action_reject_suggestion

```python
async def action_reject_suggestion(self) -> None
```

Reject the current suggestion.

---

## action_toggle_details

```python
def action_toggle_details(self) -> None
```

Toggle suggestion details view.

---

## action_ignore_suggestion

```python
def action_ignore_suggestion(self) -> None
```

Ignore the current suggestion without recording.

---

## action_quit

```python
async def action_quit(self) -> None
```

Quit the application gracefully.

---

## services.witness.voice_gate

## voice_gate

```python
module voice_gate
```

VoiceGate: Anti-Sausage Runtime Enforcement.

---

## VoiceAction

```python
class VoiceAction(Enum)
```

Action to take on voice rule match.

---

## VoiceRule

```python
class VoiceRule
```

A rule for voice checking.

### Examples
```python
>>> rule = VoiceRule(
```

---

## VoiceViolation

```python
class VoiceViolation
```

A detected voice violation.

---

## VoiceCheckResult

```python
class VoiceCheckResult
```

Result of checking text against voice rules.

---

## VoiceGate

```python
class VoiceGate
```

Runtime Anti-Sausage enforcement.

### Examples
```python
>>> gate = VoiceGate()
```
```python
>>> result = gate.check("We need to leverage synergies")
```
```python
>>> result.passed  # False - blocked by "leverage" and "synergies"
```
```python
>>> result = gate.check("Tasteful > feature-complete is our mantra")
```
```python
>>> result.anchors_referenced  # ("Tasteful > feature-complete",)
```

---

## get_voice_gate

```python
def get_voice_gate() -> VoiceGate
```

Get the global voice gate.

---

## set_voice_gate

```python
def set_voice_gate(gate: VoiceGate) -> None
```

Set the global voice gate.

---

## reset_voice_gate

```python
def reset_voice_gate() -> None
```

Reset the global voice gate (for testing).

---

## compiled

```python
def compiled(self) -> re.Pattern[str]
```

Get compiled regex pattern.

---

## matches

```python
def matches(self, text: str) -> list[str]
```

Find all matches in text.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> VoiceRule
```

Create from dictionary.

---

## action

```python
def action(self) -> VoiceAction
```

Get the action for this violation.

---

## is_blocking

```python
def is_blocking(self) -> bool
```

Check if this violation blocks output.

---

## is_warning

```python
def is_warning(self) -> bool
```

Check if this is a warning.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## has_violations

```python
def has_violations(self) -> bool
```

Check if any violations were found.

---

## has_warnings

```python
def has_warnings(self) -> bool
```

Check if any warnings were found.

---

## blocking_count

```python
def blocking_count(self) -> int
```

Count of blocking violations.

---

## warning_count

```python
def warning_count(self) -> int
```

Count of warnings.

---

## anchor_count

```python
def anchor_count(self) -> int
```

Count of anchor references.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## strict

```python
def strict(cls) -> VoiceGate
```

Create a strict VoiceGate that blocks denylist matches.

---

## permissive

```python
def permissive(cls) -> VoiceGate
```

Create a permissive VoiceGate that only warns.

---

## with_custom_rules

```python
def with_custom_rules(cls, rules: list[VoiceRule]) -> VoiceGate
```

Create with custom rules added.

---

## check

```python
def check(self, text: str) -> VoiceCheckResult
```

Check text against voice rules.

---

## is_clean

```python
def is_clean(self, text: str) -> bool
```

Quick check if text passes with no violations.

---

## has_corporate_speak

```python
def has_corporate_speak(self, text: str) -> bool
```

Check if text contains any denylist patterns.

---

## has_hedging

```python
def has_hedging(self, text: str) -> bool
```

Check if text contains hedging language.

---

## references_anchor

```python
def references_anchor(self, text: str) -> str | None
```

Check if text references any voice anchor. Returns first match.

---

## add_rule

```python
def add_rule(self, rule: VoiceRule) -> None
```

Add a custom rule.

---

## add_denylist_pattern

```python
def add_denylist_pattern(self, pattern: str, reason: str='Custom denylist pattern') -> None
```

Add a pattern to the denylist.

---

## suggest_transforms

```python
def suggest_transforms(self, text: str) -> list[tuple[str, str, str]]
```

Suggest transformations for violations.

---

## stats

```python
def stats(self) -> dict[str, int]
```

Get check statistics.

---

## reset_stats

```python
def reset_stats(self) -> None
```

Reset statistics.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> VoiceGate
```

Create from dictionary.

---

## services.witness.walk

## walk

```python
module walk
```

Walk: Durable Work Stream Tied to Forest Plans.

---

## WalkStatus

```python
class WalkStatus(Enum)
```

Status of a Walk.

---

## Participant

```python
class Participant
```

A participant in a Walk (human or agent).

---

## WalkIntent

```python
class WalkIntent
```

The goal of a Walk.

---

## Walk

```python
class Walk
```

Durable work stream tied to Forest plans.

### Examples
```python
>>> walk = Walk.create(
```
```python
>>> walk.advance(mark)
```
```python
>>> walk.transition_phase(NPhase.ACT)
```

---

## WalkStore

```python
class WalkStore
```

Persistent storage for Walks.

---

## get_walk_store

```python
def get_walk_store() -> WalkStore
```

Get the global walk store.

---

## reset_walk_store

```python
def reset_walk_store() -> None
```

Reset the global walk store (for testing).

---

## human

```python
def human(cls, name: str, role: str='orchestrator') -> Participant
```

Create a human participant.

---

## agent

```python
def agent(cls, name: str, trust_level: int=0, role: str='contributor') -> Participant
```

Create an agent participant.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Participant
```

Create from dictionary.

---

## create

```python
def create(cls, description: str, intent_type: str='implement') -> WalkIntent
```

Create a new intent.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> WalkIntent
```

Create from dictionary.

---

## __post_init__

```python
def __post_init__(self) -> None
```

Initialize phase history if empty.

---

## create

```python
def create(cls, goal: str | WalkIntent, root_plan: PlanPath | str | None=None, name: str='', initial_phase: NPhase=NPhase.SENSE) -> Walk
```

Create a new Walk.

---

## advance

```python
def advance(self, mark: Mark) -> None
```

Add a Mark to this Walk.

---

## trace_count

```python
def trace_count(self) -> int
```

Get the number of traces in this Walk.

---

## mark_count

```python
def mark_count(self) -> int
```

Backwards compat: alias for trace_count().

---

## can_transition

```python
def can_transition(self, to_phase: NPhase) -> bool
```

Check if transition to the given phase is valid.

---

## transition_phase

```python
def transition_phase(self, to_phase: NPhase, force: bool=False) -> bool
```

Transition to a new N-Phase.

---

## get_phase_duration

```python
def get_phase_duration(self, phase: NPhase) -> float
```

Get total time spent in a phase (in seconds).

---

## add_participant

```python
def add_participant(self, participant: Participant) -> None
```

Add a participant to this Walk.

---

## get_participant

```python
def get_participant(self, participant_id: str) -> Participant | None
```

Get a participant by ID.

---

## pause

```python
def pause(self) -> None
```

Pause this Walk.

---

## resume

```python
def resume(self) -> None
```

Resume a paused Walk.

---

## complete

```python
def complete(self) -> None
```

Mark this Walk as complete.

---

## abandon

```python
def abandon(self, reason: str='') -> None
```

Abandon this Walk.

---

## to_dict

```python
def to_dict(self) -> dict[str, Any]
```

Convert to dictionary for persistence.

---

## from_dict

```python
def from_dict(cls, data: dict[str, Any]) -> Walk
```

Create from dictionary.

---

## duration_seconds

```python
def duration_seconds(self) -> float
```

Total duration of the Walk in seconds.

---

## is_active

```python
def is_active(self) -> bool
```

Check if the Walk is active.

---

## is_complete

```python
def is_complete(self) -> bool
```

Check if the Walk is complete.

---

## __repr__

```python
def __repr__(self) -> str
```

Concise representation.

---

## add

```python
def add(self, walk: Walk) -> None
```

Add a Walk to the store.

---

## get

```python
def get(self, walk_id: WalkId) -> Walk | None
```

Get a Walk by ID.

---

## active_walks

```python
def active_walks(self) -> list[Walk]
```

Get all active Walks.

---

## recent_walks

```python
def recent_walks(self, limit: int=10) -> list[Walk]
```

Get most recent Walks.

---

## save

```python
def save(self, path: Path | str) -> None
```

Save to JSON file.

---

## load

```python
def load(cls, path: Path | str) -> WalkStore
```

Load from JSON file.

---

## services.witness.watchers.__init__

## __init__

```python
module __init__
```

Witness Event Sources (Watchers).

---

## services.witness.watchers.agentese

## agentese

```python
module agentese
```

AgenteseWatcher: Event-Driven Cross-Jewel Visibility.

---

## AgenteseConfig

```python
class AgenteseConfig
```

Configuration for AgenteseWatcher.

---

## parse_agentese_path

```python
def parse_agentese_path(topic: str) -> tuple[str, str, str | None]
```

Parse an AGENTESE topic into (path, aspect, jewel).

### Examples
```python
>>> "world.town.citizen.create" → ("world.town.citizen", "create", "Town")
```
```python
>>> "self.memory.capture" → ("self.memory", "capture", "Brain")
```
```python
>>> "unknown.path.action" → ("unknown.path", "action", None)
```

---

## parse_agentese_path_with_config

```python
def parse_agentese_path_with_config(topic: str, config: AgenteseConfig) -> tuple[str, str, str | None]
```

Parse with custom config (for testing).

---

## AgenteseWatcher

```python
class AgenteseWatcher(BaseWatcher[AgenteseEvent])
```

Event-driven AGENTESE watcher.

---

## create_agentese_watcher

```python
def create_agentese_watcher(bus: 'WitnessSynergyBus | None'=None, patterns: tuple[str, ...] | None=None) -> AgenteseWatcher
```

Create a configured AGENTESE watcher.

---

## services.witness.watchers.base

## base

```python
module base
```

BaseWatcher: Common Infrastructure for Event-Driven Watchers.

---

## WatcherState

```python
class WatcherState(Enum)
```

State of any watcher.

---

## WatcherStats

```python
class WatcherStats
```

Statistics for watchers (shared across all types).

---

## BaseWatcher

```python
class BaseWatcher(ABC, Generic[E])
```

Abstract base class for all Witness watchers.

### Examples
```python
>>> class MyWatcher(BaseWatcher[MyEvent]):
```

---

## record_event

```python
def record_event(self) -> None
```

Record an event emission.

---

## record_error

```python
def record_error(self) -> None
```

Record an error.

---

## add_handler

```python
def add_handler(self, handler: Callable[[E], None]) -> None
```

Add an event handler.

---

## remove_handler

```python
def remove_handler(self, handler: Callable[[E], None]) -> None
```

Remove an event handler.

---

## start

```python
async def start(self) -> None
```

Start the watcher.

---

## stop

```python
async def stop(self) -> None
```

Stop the watcher gracefully.

---

## watch

```python
async def watch(self) -> AsyncIterator[E]
```

Async iterator interface for event consumption.

---

## services.witness.watchers.ci

## ci

```python
module ci
```

CIWatcher: Poll-Based GitHub Actions Monitoring.

---

## CIConfig

```python
class CIConfig
```

Configuration for CIWatcher.

---

## WorkflowRun

```python
class WorkflowRun
```

Parsed workflow run from GitHub API.

---

## fetch_workflow_runs

```python
async def fetch_workflow_runs(owner: str, repo: str, token: str | None=None, per_page: int=10) -> tuple[list[WorkflowRun], int, int]
```

Fetch recent workflow runs from GitHub API.

---

## CIWatcher

```python
class CIWatcher(BaseWatcher[CIEvent])
```

Poll-based GitHub Actions watcher.

---

## create_ci_watcher

```python
def create_ci_watcher(owner: str='', repo: str='', token: str | None=None, poll_interval: float=60.0) -> CIWatcher
```

Create a configured CI watcher.

---

## services.witness.watchers.filesystem

## filesystem

```python
module filesystem
```

FileSystemWatcher: Event-Driven File System Monitoring.

---

## FileSystemConfig

```python
class FileSystemConfig
```

Configuration for FileSystemWatcher.

---

## Debouncer

```python
class Debouncer
```

Time-based debouncer for file events.

---

## PatternMatcher

```python
class PatternMatcher
```

Glob-based pattern matcher for file paths.

---

## FileSystemWatcher

```python
class FileSystemWatcher(BaseWatcher[FileEvent])
```

Event-driven file system watcher.

---

## create_filesystem_watcher

```python
def create_filesystem_watcher(path: Path | None=None, include: tuple[str, ...]=('*.py', '*.tsx', '*.ts'), exclude: tuple[str, ...]=('__pycache__', '.git', 'node_modules'), debounce: float=0.5) -> FileSystemWatcher
```

Create a configured filesystem watcher.

---

## for_python

```python
def for_python(cls, path: Path | None=None) -> 'FileSystemConfig'
```

Preset for Python projects.

---

## for_typescript

```python
def for_typescript(cls, path: Path | None=None) -> 'FileSystemConfig'
```

Preset for TypeScript projects.

---

## should_emit

```python
def should_emit(self, path: str) -> bool
```

Check if enough time has passed since last event for this path.

---

## clear

```python
def clear(self) -> None
```

Clear all debounce state.

---

## matches

```python
def matches(self, path: str) -> bool
```

Check if path matches include patterns and doesn't match exclude.

---

## Handler

```python
class Handler(FileSystemEventHandler)
```

Watchdog event handler that filters and enqueues events.

---

## services.witness.watchers.git

## git

```python
module git
```

GitWatcher: Event-Driven Git Monitoring.

---

## get_git_head

```python
async def get_git_head() -> str | None
```

Get current HEAD SHA.

---

## get_git_branch

```python
async def get_git_branch() -> str | None
```

Get current branch name.

---

## get_commit_info

```python
async def get_commit_info(sha: str) -> dict[str, str]
```

Get info about a specific commit.

---

## get_recent_commits

```python
async def get_recent_commits(since: datetime) -> list[str]
```

Get commits since a given time.

---

## GitWatcher

```python
class GitWatcher(BaseWatcher[GitEvent])
```

Event-driven git watcher.

---

## create_git_watcher

```python
def create_git_watcher(repo_path: Path | None=None, poll_interval: float=5.0) -> GitWatcher
```

Create a configured git watcher.

---

## services.witness.watchers.git_flux

## git_flux

```python
module git_flux
```

GitWatcherFlux: Flux-Lifted GitWatcher for Event-Driven Streaming.

---

## GitFluxState

```python
class GitFluxState(Enum)
```

Lifecycle states for GitWatcherFlux.

---

## GitWatcherProtocol

```python
class GitWatcherProtocol(Protocol)
```

Protocol for GitWatcher-like objects (for testing).

---

## GitWatcherFlux

```python
class GitWatcherFlux
```

Flux-lifted GitWatcher for event-driven streaming.

---

## create_git_watcher_flux

```python
def create_git_watcher_flux(watcher: GitWatcherProtocol) -> GitWatcherFlux
```

Create a GitWatcherFlux from a GitWatcher.

---

## start

```python
async def start(self) -> AsyncIterator['GitEvent']
```

Start streaming events from the underlying watcher.

---

## stop

```python
async def stop(self) -> None
```

Signal stop and cleanup watcher.

---

## state

```python
def state(self) -> GitFluxState
```

Current lifecycle state.

---

## services.witness.watchers.test_watcher

## test_watcher

```python
module test_watcher
```

TestWatcher: Event-Driven Pytest Result Monitoring.

---

## get_test_event_queue

```python
def get_test_event_queue() -> Queue[TestEvent]
```

Get the global test event queue.

---

## reset_test_event_queue

```python
def reset_test_event_queue() -> None
```

Reset the queue (for testing).

---

## TestWatcherConfig

```python
class TestWatcherConfig
```

Configuration for TestWatcher.

---

## TestWatcherPlugin

```python
class TestWatcherPlugin
```

Pytest plugin that captures test events and pushes to queue.

---

## TestWatcher

```python
class TestWatcher(BaseWatcher[TestEvent])
```

Event-driven test result watcher.

---

## create_test_watcher

```python
def create_test_watcher(capture_passed: bool=True, max_error_length: int=500) -> TestWatcher
```

Create a configured test watcher.

---

## create_test_plugin

```python
def create_test_plugin(capture_passed: bool=True, capture_individual: bool=True, max_error_length: int=500) -> TestWatcherPlugin
```

Create a configured pytest plugin.

---

## pytest_sessionstart

```python
def pytest_sessionstart(self, session: 'pytest.Session') -> None
```

Called at session start.

---

## pytest_runtest_logreport

```python
def pytest_runtest_logreport(self, report: Any) -> None
```

Called for each test phase (setup, call, teardown).

---

## pytest_sessionfinish

```python
def pytest_sessionfinish(self, session: 'pytest.Session', exitstatus: int) -> None
```

Called at session end.

---

## services.witness.workflows

## workflows

```python
module workflows
```

Witness Workflow Templates: Pre-Built Cross-Jewel Patterns.

---

## WorkflowCategory

```python
class WorkflowCategory(Enum)
```

Categories of workflow templates.

---

## WorkflowTemplate

```python
class WorkflowTemplate
```

A pre-built workflow template.

---

## get_workflow

```python
def get_workflow(name: str) -> WorkflowTemplate | None
```

Get a workflow template by name.

---

## list_workflows

```python
def list_workflows(category: WorkflowCategory | None=None, max_trust: int | None=None) -> list[WorkflowTemplate]
```

List available workflow templates.

---

## search_workflows

```python
def search_workflows(tag: str) -> list[WorkflowTemplate]
```

Search workflows by tag.

---

## extend_workflow

```python
def extend_workflow(base: WorkflowTemplate, *extensions: Step) -> Pipeline
```

Extend a workflow template with additional steps.

---

## chain_workflows

```python
def chain_workflows(*templates: WorkflowTemplate) -> Pipeline
```

Chain multiple workflow templates together.

---

## __call__

```python
def __call__(self, **kwargs: Any) -> Pipeline
```

Get the pipeline with optional parameter overrides.

---

*2033 symbols, 21 teaching moments*

*Generated by Living Docs — 2025-12-21*