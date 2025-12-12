"""
Generated gRPC stubs for the Logos service.

These files are generated from logos.proto using grpc_tools.protoc.
DO NOT EDIT MANUALLY - regenerate using:

    python -m grpc_tools.protoc \
        -I protocols/proto \
        -I $(python -c "import grpc_tools; print(grpc_tools.__path__[0])")/_proto \
        --python_out=protocols/proto/generated \
        --grpc_python_out=protocols/proto/generated \
        --pyi_out=protocols/proto/generated \
        protocols/proto/logos.proto

Note: After generation, fix the import in logos_pb2_grpc.py:
    Change: import logos_pb2 as logos__pb2
    To:     from . import logos_pb2 as logos__pb2

Generated files:
- logos_pb2.py: Protocol buffer message definitions
- logos_pb2_grpc.py: gRPC service stubs (LogosStub, LogosServicer)
- logos_pb2.pyi: Type stubs for IDE support
"""

from .logos_pb2 import (
    AgentStatus,
    Attractor,
    ComponentHealth,
    DesireLine,
    DreamInput,
    DreamMetadata,
    DreamOutput,
    HoloMap,
    InvokeMetadata,
    # Request/Response messages
    InvokeRequest,
    InvokeResponse,
    LogosError,
    MapHorizon,
    MapLandmark,
    MapMetadata,
    MapPosition,
    MapRequest,
    MapVoid,
    ObserveEvent,
    ObserveRequest,
    StatusRequest,
    StatusResponse,
    TitheRequest,
    TitheResponse,
    Umwelt,
)
from .logos_pb2_grpc import (
    LogosServicer,
    LogosStub,
    add_LogosServicer_to_server,
)

__all__ = [
    # Messages
    "InvokeRequest",
    "InvokeResponse",
    "InvokeMetadata",
    "StatusRequest",
    "StatusResponse",
    "AgentStatus",
    "ComponentHealth",
    "DreamInput",
    "DreamOutput",
    "DreamMetadata",
    "ObserveRequest",
    "ObserveEvent",
    "MapRequest",
    "HoloMap",
    "MapLandmark",
    "DesireLine",
    "MapVoid",
    "Attractor",
    "MapHorizon",
    "MapPosition",
    "MapMetadata",
    "TitheRequest",
    "TitheResponse",
    "Umwelt",
    "LogosError",
    # Service stubs
    "LogosStub",
    "LogosServicer",
    "add_LogosServicer_to_server",
]
