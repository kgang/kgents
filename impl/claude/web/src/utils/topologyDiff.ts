/**
 * topologyDiff - Utilities for applying incremental topology updates.
 *
 * These functions handle applying TopologyUpdate messages from SSE
 * to the local InfraTopologyResponse state, enabling smooth
 * transitions without full re-renders.
 *
 * @see plans/_continuations/gestalt-live-infra-phase2.md
 */

import type {
  TopologyUpdate,
  InfraTopologyResponse,
  InfraEntity,
  InfraConnection,
} from '../api/types';

/**
 * Apply a TopologyUpdate to the current topology state.
 *
 * Handles all update kinds:
 * - full: Replace entire topology
 * - entity_added: Add new entity
 * - entity_updated: Update existing entity
 * - entity_removed: Remove entity
 * - connection_added: Add new connection
 * - connection_updated: Update existing connection
 * - connection_removed: Remove connection
 * - metrics: Update metrics only
 */
export function applyTopologyUpdate(
  current: InfraTopologyResponse | null,
  update: TopologyUpdate
): InfraTopologyResponse | null {
  // Full update replaces everything
  if (update.kind === 'full') {
    return update.topology || null;
  }

  // If no current state, can't apply incremental updates
  if (!current) {
    return current;
  }

  switch (update.kind) {
    case 'entity_added':
      return applyEntityAdded(current, update.entity!);

    case 'entity_updated':
      return applyEntityUpdated(current, update.entity!);

    case 'entity_removed':
      return applyEntityRemoved(current, update.entity!);

    case 'connection_added':
      return applyConnectionAdded(current, update.connection!);

    case 'connection_updated':
      return applyConnectionUpdated(current, update.connection!);

    case 'connection_removed':
      return applyConnectionRemoved(current, update.connection!);

    case 'metrics':
      return applyMetricsUpdate(current, update.metrics!);

    default:
      console.warn('Unknown topology update kind:', update.kind);
      return current;
  }
}

/**
 * Add a new entity to the topology.
 */
function applyEntityAdded(
  current: InfraTopologyResponse,
  entity: InfraEntity
): InfraTopologyResponse {
  // Check if entity already exists (idempotency)
  if (current.entities.some((e) => e.id === entity.id)) {
    return applyEntityUpdated(current, entity);
  }

  const newEntities = [...current.entities, entity];

  return recalculateAggregates({
    ...current,
    entities: newEntities,
    timestamp: new Date().toISOString(),
  });
}

/**
 * Update an existing entity.
 */
function applyEntityUpdated(
  current: InfraTopologyResponse,
  entity: InfraEntity
): InfraTopologyResponse {
  const newEntities = current.entities.map((e) =>
    e.id === entity.id ? entity : e
  );

  // If entity wasn't found, this is effectively an add
  if (!current.entities.some((e) => e.id === entity.id)) {
    return applyEntityAdded(current, entity);
  }

  return recalculateAggregates({
    ...current,
    entities: newEntities,
    timestamp: new Date().toISOString(),
  });
}

/**
 * Remove an entity from the topology.
 */
function applyEntityRemoved(
  current: InfraTopologyResponse,
  entity: InfraEntity
): InfraTopologyResponse {
  const newEntities = current.entities.filter((e) => e.id !== entity.id);

  // Also remove any connections involving this entity
  const newConnections = current.connections.filter(
    (c) => c.source_id !== entity.id && c.target_id !== entity.id
  );

  return recalculateAggregates({
    ...current,
    entities: newEntities,
    connections: newConnections,
    timestamp: new Date().toISOString(),
  });
}

/**
 * Add a new connection.
 */
function applyConnectionAdded(
  current: InfraTopologyResponse,
  connection: InfraConnection
): InfraTopologyResponse {
  // Check if connection already exists (idempotency)
  if (current.connections.some((c) => c.id === connection.id)) {
    return applyConnectionUpdated(current, connection);
  }

  return {
    ...current,
    connections: [...current.connections, connection],
    timestamp: new Date().toISOString(),
  };
}

/**
 * Update an existing connection.
 */
function applyConnectionUpdated(
  current: InfraTopologyResponse,
  connection: InfraConnection
): InfraTopologyResponse {
  const newConnections = current.connections.map((c) =>
    c.id === connection.id ? connection : c
  );

  // If connection wasn't found, this is effectively an add
  if (!current.connections.some((c) => c.id === connection.id)) {
    return applyConnectionAdded(current, connection);
  }

  return {
    ...current,
    connections: newConnections,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Remove a connection.
 */
function applyConnectionRemoved(
  current: InfraTopologyResponse,
  connection: InfraConnection
): InfraTopologyResponse {
  return {
    ...current,
    connections: current.connections.filter((c) => c.id !== connection.id),
    timestamp: new Date().toISOString(),
  };
}

/**
 * Apply metrics-only update (entity_id -> metrics dict).
 */
function applyMetricsUpdate(
  current: InfraTopologyResponse,
  metrics: Record<string, Record<string, number>>
): InfraTopologyResponse {
  const newEntities = current.entities.map((entity) => {
    const entityMetrics = metrics[entity.id];
    if (!entityMetrics) return entity;

    return {
      ...entity,
      ...(entityMetrics.cpu_percent !== undefined && {
        cpu_percent: entityMetrics.cpu_percent,
      }),
      ...(entityMetrics.memory_bytes !== undefined && {
        memory_bytes: entityMetrics.memory_bytes,
      }),
      ...(entityMetrics.health !== undefined && {
        health: entityMetrics.health,
      }),
      custom_metrics: {
        ...entity.custom_metrics,
        ...Object.fromEntries(
          Object.entries(entityMetrics).filter(
            ([key]) => !['cpu_percent', 'memory_bytes', 'health'].includes(key)
          )
        ),
      },
    };
  });

  return recalculateAggregates({
    ...current,
    entities: newEntities,
    timestamp: new Date().toISOString(),
  });
}

/**
 * Recalculate aggregate statistics after entity changes.
 */
function recalculateAggregates(
  topology: InfraTopologyResponse
): InfraTopologyResponse {
  const entities = topology.entities;

  // Count by health level
  let healthyCount = 0;
  let warningCount = 0;
  let criticalCount = 0;

  for (const entity of entities) {
    if (entity.health >= 0.8) {
      healthyCount++;
    } else if (entity.health >= 0.5) {
      warningCount++;
    } else {
      criticalCount++;
    }
  }

  // Count by kind
  const entitiesByKind: Record<string, number> = {};
  for (const entity of entities) {
    entitiesByKind[entity.kind] = (entitiesByKind[entity.kind] || 0) + 1;
  }

  // Count by namespace
  const entitiesByNamespace: Record<string, number> = {};
  for (const entity of entities) {
    const ns = entity.namespace || '(none)';
    entitiesByNamespace[ns] = (entitiesByNamespace[ns] || 0) + 1;
  }

  // Calculate overall health
  const overallHealth =
    entities.length > 0
      ? entities.reduce((sum, e) => sum + e.health, 0) / entities.length
      : 1.0;

  return {
    ...topology,
    total_entities: entities.length,
    healthy_count: healthyCount,
    warning_count: warningCount,
    critical_count: criticalCount,
    overall_health: overallHealth,
    entities_by_kind: entitiesByKind,
    entities_by_namespace: entitiesByNamespace,
  };
}

/**
 * Calculate which entities need animation state changes.
 *
 * Returns a map of entity IDs to animation instructions:
 * - 'fadeIn': New entity, should fade in
 * - 'pulse': Updated entity, should pulse
 * - 'fadeOut': Removed entity, should fade out
 */
export function calculateAnimationChanges(
  prevEntities: InfraEntity[],
  nextEntities: InfraEntity[]
): Map<string, 'fadeIn' | 'pulse' | 'fadeOut'> {
  const changes = new Map<string, 'fadeIn' | 'pulse' | 'fadeOut'>();

  const prevIds = new Set(prevEntities.map((e) => e.id));
  const nextIds = new Set(nextEntities.map((e) => e.id));

  // Find new entities (fadeIn)
  for (const entity of nextEntities) {
    if (!prevIds.has(entity.id)) {
      changes.set(entity.id, 'fadeIn');
    }
  }

  // Find removed entities (fadeOut)
  for (const entity of prevEntities) {
    if (!nextIds.has(entity.id)) {
      changes.set(entity.id, 'fadeOut');
    }
  }

  // Find updated entities (pulse)
  const prevMap = new Map(prevEntities.map((e) => [e.id, e]));
  for (const entity of nextEntities) {
    const prev = prevMap.get(entity.id);
    if (prev && hasSignificantChange(prev, entity)) {
      changes.set(entity.id, 'pulse');
    }
  }

  return changes;
}

/**
 * Check if an entity has a significant change worth animating.
 */
function hasSignificantChange(prev: InfraEntity, next: InfraEntity): boolean {
  // Status change
  if (prev.status !== next.status) return true;

  // Health change > 0.1
  if (Math.abs(prev.health - next.health) > 0.1) return true;

  // CPU change > 20%
  if (Math.abs(prev.cpu_percent - next.cpu_percent) > 20) return true;

  return false;
}

export default { applyTopologyUpdate, calculateAnimationChanges };
