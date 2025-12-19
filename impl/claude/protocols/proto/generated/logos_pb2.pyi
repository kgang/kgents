import datetime
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

from google.protobuf import (
    any_pb2 as _any_pb2,
    descriptor as _descriptor,
    duration_pb2 as _duration_pb2,
    message as _message,
    timestamp_pb2 as _timestamp_pb2,
)
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class InvokeRequest(_message.Message):
    __slots__ = ("path", "observer_dna", "lens", "kwargs")
    class KwargsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

    PATH_FIELD_NUMBER: _ClassVar[int]
    OBSERVER_DNA_FIELD_NUMBER: _ClassVar[int]
    LENS_FIELD_NUMBER: _ClassVar[int]
    KWARGS_FIELD_NUMBER: _ClassVar[int]
    path: str
    observer_dna: bytes
    lens: str
    kwargs: _containers.ScalarMap[str, str]
    def __init__(
        self,
        path: _Optional[str] = ...,
        observer_dna: _Optional[bytes] = ...,
        lens: _Optional[str] = ...,
        kwargs: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class InvokeResponse(_message.Message):
    __slots__ = ("result", "result_json", "metadata")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    RESULT_JSON_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    result: _any_pb2.Any
    result_json: str
    metadata: InvokeMetadata
    def __init__(
        self,
        result: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...,
        result_json: _Optional[str] = ...,
        metadata: _Optional[_Union[InvokeMetadata, _Mapping]] = ...,
    ) -> None: ...

class InvokeMetadata(_message.Message):
    __slots__ = (
        "path",
        "lens",
        "duration",
        "tokens_input",
        "tokens_output",
        "trace_id",
        "from_cache",
    )
    PATH_FIELD_NUMBER: _ClassVar[int]
    LENS_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    TOKENS_INPUT_FIELD_NUMBER: _ClassVar[int]
    TOKENS_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_CACHE_FIELD_NUMBER: _ClassVar[int]
    path: str
    lens: str
    duration: _duration_pb2.Duration
    tokens_input: int
    tokens_output: int
    trace_id: str
    from_cache: bool
    def __init__(
        self,
        path: _Optional[str] = ...,
        lens: _Optional[str] = ...,
        duration: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...,
        tokens_input: _Optional[int] = ...,
        tokens_output: _Optional[int] = ...,
        trace_id: _Optional[str] = ...,
        from_cache: bool = ...,
    ) -> None: ...

class StatusRequest(_message.Message):
    __slots__ = ("verbose", "components")
    VERBOSE_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    verbose: bool
    components: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self, verbose: bool = ..., components: _Optional[_Iterable[str]] = ...
    ) -> None: ...

class StatusResponse(_message.Message):
    __slots__ = (
        "health",
        "agents",
        "pheromone_levels",
        "metabolic_pressure",
        "instance_id",
        "timestamp",
        "components",
    )
    class PheromoneLevelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...

    HEALTH_FIELD_NUMBER: _ClassVar[int]
    AGENTS_FIELD_NUMBER: _ClassVar[int]
    PHEROMONE_LEVELS_FIELD_NUMBER: _ClassVar[int]
    METABOLIC_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    health: str
    agents: _containers.RepeatedCompositeFieldContainer[AgentStatus]
    pheromone_levels: _containers.ScalarMap[str, float]
    metabolic_pressure: float
    instance_id: str
    timestamp: _timestamp_pb2.Timestamp
    components: _containers.RepeatedCompositeFieldContainer[ComponentHealth]
    def __init__(
        self,
        health: _Optional[str] = ...,
        agents: _Optional[_Iterable[_Union[AgentStatus, _Mapping]]] = ...,
        pheromone_levels: _Optional[_Mapping[str, float]] = ...,
        metabolic_pressure: _Optional[float] = ...,
        instance_id: _Optional[str] = ...,
        timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...,
        components: _Optional[_Iterable[_Union[ComponentHealth, _Mapping]]] = ...,
    ) -> None: ...

class AgentStatus(_message.Message):
    __slots__ = ("name", "genus", "status", "last_active")
    NAME_FIELD_NUMBER: _ClassVar[int]
    GENUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LAST_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    name: str
    genus: str
    status: str
    last_active: _timestamp_pb2.Timestamp
    def __init__(
        self,
        name: _Optional[str] = ...,
        genus: _Optional[str] = ...,
        status: _Optional[str] = ...,
        last_active: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class ComponentHealth(_message.Message):
    __slots__ = ("name", "healthy", "message")
    NAME_FIELD_NUMBER: _ClassVar[int]
    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    name: str
    healthy: bool
    message: str
    def __init__(
        self, name: _Optional[str] = ..., healthy: bool = ..., message: _Optional[str] = ...
    ) -> None: ...

class DreamInput(_message.Message):
    __slots__ = ("text", "start_session", "end_session", "set_phase")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    START_SESSION_FIELD_NUMBER: _ClassVar[int]
    END_SESSION_FIELD_NUMBER: _ClassVar[int]
    SET_PHASE_FIELD_NUMBER: _ClassVar[int]
    text: str
    start_session: bool
    end_session: bool
    set_phase: str
    def __init__(
        self,
        text: _Optional[str] = ...,
        start_session: bool = ...,
        end_session: bool = ...,
        set_phase: _Optional[str] = ...,
    ) -> None: ...

class DreamOutput(_message.Message):
    __slots__ = ("text", "awaiting_input", "phase", "metadata")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    AWAITING_INPUT_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    text: str
    awaiting_input: bool
    phase: str
    metadata: DreamMetadata
    def __init__(
        self,
        text: _Optional[str] = ...,
        awaiting_input: bool = ...,
        phase: _Optional[str] = ...,
        metadata: _Optional[_Union[DreamMetadata, _Mapping]] = ...,
    ) -> None: ...

class DreamMetadata(_message.Message):
    __slots__ = ("confidence", "source", "memory_ids")
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    MEMORY_IDS_FIELD_NUMBER: _ClassVar[int]
    confidence: float
    source: str
    memory_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        confidence: _Optional[float] = ...,
        source: _Optional[str] = ...,
        memory_ids: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class ObserveRequest(_message.Message):
    __slots__ = ("event_types", "min_significance", "focus_path")
    EVENT_TYPES_FIELD_NUMBER: _ClassVar[int]
    MIN_SIGNIFICANCE_FIELD_NUMBER: _ClassVar[int]
    FOCUS_PATH_FIELD_NUMBER: _ClassVar[int]
    event_types: _containers.RepeatedScalarFieldContainer[str]
    min_significance: float
    focus_path: str
    def __init__(
        self,
        event_types: _Optional[_Iterable[str]] = ...,
        min_significance: _Optional[float] = ...,
        focus_path: _Optional[str] = ...,
    ) -> None: ...

class ObserveEvent(_message.Message):
    __slots__ = ("event_type", "content", "timestamp", "source", "significance")
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SIGNIFICANCE_FIELD_NUMBER: _ClassVar[int]
    event_type: str
    content: str
    timestamp: _timestamp_pb2.Timestamp
    source: str
    significance: float
    def __init__(
        self,
        event_type: _Optional[str] = ...,
        content: _Optional[str] = ...,
        timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...,
        source: _Optional[str] = ...,
        significance: _Optional[float] = ...,
    ) -> None: ...

class MapRequest(_message.Message):
    __slots__ = (
        "focus",
        "resolution",
        "format",
        "include_desire_lines",
        "include_voids",
        "include_attractors",
    )
    FOCUS_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_DESIRE_LINES_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_VOIDS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_ATTRACTORS_FIELD_NUMBER: _ClassVar[int]
    focus: str
    resolution: str
    format: str
    include_desire_lines: bool
    include_voids: bool
    include_attractors: bool
    def __init__(
        self,
        focus: _Optional[str] = ...,
        resolution: _Optional[str] = ...,
        format: _Optional[str] = ...,
        include_desire_lines: bool = ...,
        include_voids: bool = ...,
        include_attractors: bool = ...,
    ) -> None: ...

class HoloMap(_message.Message):
    __slots__ = (
        "landmarks",
        "desire_lines",
        "voids",
        "attractors",
        "horizon",
        "rendered",
        "metadata",
    )
    LANDMARKS_FIELD_NUMBER: _ClassVar[int]
    DESIRE_LINES_FIELD_NUMBER: _ClassVar[int]
    VOIDS_FIELD_NUMBER: _ClassVar[int]
    ATTRACTORS_FIELD_NUMBER: _ClassVar[int]
    HORIZON_FIELD_NUMBER: _ClassVar[int]
    RENDERED_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    landmarks: _containers.RepeatedCompositeFieldContainer[MapLandmark]
    desire_lines: _containers.RepeatedCompositeFieldContainer[DesireLine]
    voids: _containers.RepeatedCompositeFieldContainer[MapVoid]
    attractors: _containers.RepeatedCompositeFieldContainer[Attractor]
    horizon: MapHorizon
    rendered: str
    metadata: MapMetadata
    def __init__(
        self,
        landmarks: _Optional[_Iterable[_Union[MapLandmark, _Mapping]]] = ...,
        desire_lines: _Optional[_Iterable[_Union[DesireLine, _Mapping]]] = ...,
        voids: _Optional[_Iterable[_Union[MapVoid, _Mapping]]] = ...,
        attractors: _Optional[_Iterable[_Union[Attractor, _Mapping]]] = ...,
        horizon: _Optional[_Union[MapHorizon, _Mapping]] = ...,
        rendered: _Optional[str] = ...,
        metadata: _Optional[_Union[MapMetadata, _Mapping]] = ...,
    ) -> None: ...

class MapLandmark(_message.Message):
    __slots__ = ("name", "path", "significance", "category", "position")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    SIGNIFICANCE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    name: str
    path: str
    significance: float
    category: str
    position: MapPosition
    def __init__(
        self,
        name: _Optional[str] = ...,
        path: _Optional[str] = ...,
        significance: _Optional[float] = ...,
        category: _Optional[str] = ...,
        position: _Optional[_Union[MapPosition, _Mapping]] = ...,
    ) -> None: ...

class DesireLine(_message.Message):
    __slots__ = ("from_path", "to_path", "strength", "traversal_count")
    FROM_PATH_FIELD_NUMBER: _ClassVar[int]
    TO_PATH_FIELD_NUMBER: _ClassVar[int]
    STRENGTH_FIELD_NUMBER: _ClassVar[int]
    TRAVERSAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    from_path: str
    to_path: str
    strength: float
    traversal_count: int
    def __init__(
        self,
        from_path: _Optional[str] = ...,
        to_path: _Optional[str] = ...,
        strength: _Optional[float] = ...,
        traversal_count: _Optional[int] = ...,
    ) -> None: ...

class MapVoid(_message.Message):
    __slots__ = ("path", "description", "mystery_score")
    PATH_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MYSTERY_SCORE_FIELD_NUMBER: _ClassVar[int]
    path: str
    description: str
    mystery_score: float
    def __init__(
        self,
        path: _Optional[str] = ...,
        description: _Optional[str] = ...,
        mystery_score: _Optional[float] = ...,
    ) -> None: ...

class Attractor(_message.Message):
    __slots__ = ("name", "position", "strength", "attracted_files")
    NAME_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    STRENGTH_FIELD_NUMBER: _ClassVar[int]
    ATTRACTED_FILES_FIELD_NUMBER: _ClassVar[int]
    name: str
    position: MapPosition
    strength: float
    attracted_files: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        name: _Optional[str] = ...,
        position: _Optional[_Union[MapPosition, _Mapping]] = ...,
        strength: _Optional[float] = ...,
        attracted_files: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class MapHorizon(_message.Message):
    __slots__ = ("visible_files", "beyond")
    VISIBLE_FILES_FIELD_NUMBER: _ClassVar[int]
    BEYOND_FIELD_NUMBER: _ClassVar[int]
    visible_files: _containers.RepeatedScalarFieldContainer[str]
    beyond: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        visible_files: _Optional[_Iterable[str]] = ...,
        beyond: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class MapPosition(_message.Message):
    __slots__ = ("x", "y", "z")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    def __init__(
        self, x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...
    ) -> None: ...

class MapMetadata(_message.Message):
    __slots__ = ("generated_at", "total_files", "total_landmarks", "focus", "resolution")
    GENERATED_AT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FILES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_LANDMARKS_FIELD_NUMBER: _ClassVar[int]
    FOCUS_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    generated_at: _timestamp_pb2.Timestamp
    total_files: int
    total_landmarks: int
    focus: str
    resolution: str
    def __init__(
        self,
        generated_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        total_files: _Optional[int] = ...,
        total_landmarks: _Optional[int] = ...,
        focus: _Optional[str] = ...,
        resolution: _Optional[str] = ...,
    ) -> None: ...

class TitheRequest(_message.Message):
    __slots__ = ("amount", "gratitude")
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    GRATITUDE_FIELD_NUMBER: _ClassVar[int]
    amount: float
    gratitude: str
    def __init__(self, amount: _Optional[float] = ..., gratitude: _Optional[str] = ...) -> None: ...

class TitheResponse(_message.Message):
    __slots__ = ("success", "gratitude_response", "remaining_pressure", "discharged", "fever_dream")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    GRATITUDE_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    REMAINING_PRESSURE_FIELD_NUMBER: _ClassVar[int]
    DISCHARGED_FIELD_NUMBER: _ClassVar[int]
    FEVER_DREAM_FIELD_NUMBER: _ClassVar[int]
    success: bool
    gratitude_response: str
    remaining_pressure: float
    discharged: float
    fever_dream: str
    def __init__(
        self,
        success: bool = ...,
        gratitude_response: _Optional[str] = ...,
        remaining_pressure: _Optional[float] = ...,
        discharged: _Optional[float] = ...,
        fever_dream: _Optional[str] = ...,
    ) -> None: ...

class Umwelt(_message.Message):
    __slots__ = ("id", "archetype", "permissions", "focus", "personality", "metadata")
    class PersonalityEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...

    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

    ID_FIELD_NUMBER: _ClassVar[int]
    ARCHETYPE_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    FOCUS_FIELD_NUMBER: _ClassVar[int]
    PERSONALITY_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    archetype: str
    permissions: int
    focus: str
    personality: _containers.ScalarMap[str, float]
    metadata: _containers.ScalarMap[str, str]
    def __init__(
        self,
        id: _Optional[str] = ...,
        archetype: _Optional[str] = ...,
        permissions: _Optional[int] = ...,
        focus: _Optional[str] = ...,
        personality: _Optional[_Mapping[str, float]] = ...,
        metadata: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class LogosError(_message.Message):
    __slots__ = ("code", "message", "path", "suggestions", "fallback_used")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    FALLBACK_USED_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    path: str
    suggestions: _containers.RepeatedScalarFieldContainer[str]
    fallback_used: str
    def __init__(
        self,
        code: _Optional[str] = ...,
        message: _Optional[str] = ...,
        path: _Optional[str] = ...,
        suggestions: _Optional[_Iterable[str]] = ...,
        fallback_used: _Optional[str] = ...,
    ) -> None: ...
