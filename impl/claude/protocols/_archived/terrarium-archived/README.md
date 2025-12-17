# Terrarium Archive

**Archived**: 2025-12-17
**Reason**: Superseded by AGENTESE Universal Protocol and Crown Jewel services

## What Was Terrarium?

Terrarium was the "Agent Server Web Gateway" - a generic REST/WebSocket bridge for exposing any agent to the web. It provided:

1. **Mirror Protocol** (`mirror.py`): HolographicBuffer for broadcasting agent events to N clients
2. **REST Bridge** (`rest_bridge.py`): Auto-generated REST endpoints from CLICapable agents
3. **Metrics** (`metrics.py`, `semantic_metrics.py`): Metabolism metrics (pressure/flow/temperature)
4. **Events** (`events.py`): TerriumEvent, SemaphoreEvent for widget updates
5. **WebSocket/Streaming** (`stream.py`, `server.py`): WebSocket sink for flux agents

## What Superseded It?

1. **AGENTESE Universal Gateway** (`protocols/agentese/gateway.py`)
   - The "Protocol IS the API" pattern
   - Auto-exposes all registered nodes via HTTP/WebSocket
   - More elegant, more principled than generic REST bridge

2. **Synergy Event Bus** (`protocols/synergy/bus.py`)
   - Cross-jewel communication infrastructure
   - Replaces the broadcast/mirror pattern for component events

3. **Crown Jewel Services** (`services/`)
   - Each jewel has its own event handling
   - Uses AGENTESE paths for API exposure

## What Was Preserved (Extracted to `agents/flux/`)

The following modules contained useful infrastructure and were extracted:

| Original | New Location | Used By |
|----------|--------------|---------|
| `semantic_metrics.py` | `agents/flux/semantic_metrics.py` | `self.vitals.*` AGENTESE context |
| `events.py` | `agents/flux/terrarium_events.py` | FluxAgent semaphore events |
| `mirror.py` | `agents/flux/mirror.py` | FluxAgent broadcast infrastructure |

## Deletion Policy

Per kgents archive policy, this directory will be deleted 30 days after archive date (2025-01-16).

## If You Need Something From Here

Check if it's already extracted to `agents/flux/`. If not, the functionality has likely been replaced by:
- AGENTESE Universal Gateway for HTTP/WebSocket exposure
- Synergy Event Bus for cross-component communication
- Individual Crown Jewel services for domain-specific APIs
