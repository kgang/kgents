/**
 * WASM Survivors - Performance Monitoring System
 *
 * Provides:
 * - Per-system timing breakdown
 * - Frame time history for graphs
 * - Budget enforcement and warnings
 * - Spatial partitioning for O(k) collision detection
 * - Object pooling for enemies and particles
 *
 * Target: 60fps (16.67ms frame budget)
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md (V4: JUICE - feedback delay <16ms)
 */

import type { Vector2 } from '../types';

// =============================================================================
// Performance Budget Constants
// =============================================================================

export const PERF_BUDGET = {
  targetFPS: 60,
  frameTime: 16.67,  // ms

  // Per-system budgets (must sum to <= frameTime)
  budgets: {
    input: 0.5,       // ms - event handling (already event-driven)
    physics: 3.0,     // ms - movement, enemy updates
    collision: 2.0,   // ms - collision detection
    combat: 2.0,      // ms - venom, graze, afterimage
    spawn: 0.5,       // ms - enemy spawning
    formation: 0.5,   // ms - THE BALL formation (Run 036)
    particles: 2.0,   // ms - spawn, update, cull
    render: 5.0,      // ms - draw calls
    audio: 0.5,       // ms - sound processing
    overhead: 0.17,   // ms - JS, React, buffer (reduced to fit formation)
  },

  // Hard limits to prevent spiral of death
  limits: {
    maxEnemies: 100,
    maxParticles: 500,
    maxProjectiles: 50,
    maxAudioSources: 16,
  },

  // Warning thresholds (fraction of budget)
  warnings: {
    systemOverBudget: 1.2,   // 120% of individual budget
    frameOverBudget: 1.0,    // 100% of total frame
    criticalFPS: 50,         // Below this, start degrading
    warningFPS: 55,          // Below this, show warning
  },
} as const;

// =============================================================================
// Performance Metrics
// =============================================================================

export interface SystemTimings {
  input: number;
  physics: number;
  collision: number;
  combat: number;
  melee: number;      // Run 036: Mandible Reaver melee attack system
  apex: number;       // Run 036: Apex Strike predator dash system
  spawn: number;
  formation: number;  // Run 036: THE BALL formation system
  particles: number;
  render: number;
  total: number;
}

export interface PerformanceMetrics {
  // Frame timing
  frameTime: number;
  frameTimeHistory: number[];  // Last 60 frames
  fps: number;
  fpsHistory: number[];        // Last 60 fps readings

  // System breakdown
  timings: SystemTimings;
  timingHistory: SystemTimings[];  // Last 60 frames

  // Entity counts
  counts: {
    enemies: number;
    particles: number;
    projectiles: number;
  };

  // Warnings
  warnings: string[];
  overBudgetSystems: (keyof SystemTimings)[];

  // Spatial hash stats
  spatialHashStats: {
    cellCount: number;
    avgEntitiesPerCell: number;
    queryCount: number;
    avgQueryTime: number;
  };
}

// =============================================================================
// Performance Monitor Class
// =============================================================================

export class PerformanceMonitor {
  private frameStart: number = 0;
  private systemStart: number = 0;
  private currentTimings: Partial<SystemTimings> = {};
  private frameTimeHistory: number[] = [];
  private fpsHistory: number[] = [];
  private timingHistory: SystemTimings[] = [];
  private lastFPSUpdate: number = 0;
  private framesSinceFPSUpdate: number = 0;
  private currentFPS: number = 60;
  private queryTimes: number[] = [];

  // Max history length
  private readonly HISTORY_LENGTH = 60;

  /**
   * Call at start of each frame
   */
  beginFrame(): void {
    this.frameStart = performance.now();
    this.currentTimings = {};
  }

  /**
   * Call before a system update
   */
  beginSystem(_system: keyof SystemTimings): void {
    this.systemStart = performance.now();
  }

  /**
   * Call after a system update
   */
  endSystem(system: keyof SystemTimings): void {
    const elapsed = performance.now() - this.systemStart;
    this.currentTimings[system] = elapsed;
  }

  /**
   * Call at end of frame with entity counts
   */
  endFrame(counts: { enemies: number; particles: number; projectiles: number }): PerformanceMetrics {
    const frameTime = performance.now() - this.frameStart;

    // Update frame time history
    this.frameTimeHistory.push(frameTime);
    if (this.frameTimeHistory.length > this.HISTORY_LENGTH) {
      this.frameTimeHistory.shift();
    }

    // Calculate FPS (update once per second)
    this.framesSinceFPSUpdate++;
    const now = performance.now();
    if (now - this.lastFPSUpdate >= 1000) {
      this.currentFPS = Math.round(this.framesSinceFPSUpdate * 1000 / (now - this.lastFPSUpdate));
      this.fpsHistory.push(this.currentFPS);
      if (this.fpsHistory.length > this.HISTORY_LENGTH) {
        this.fpsHistory.shift();
      }
      this.lastFPSUpdate = now;
      this.framesSinceFPSUpdate = 0;
    }

    // Build complete timings
    const timings: SystemTimings = {
      input: this.currentTimings.input ?? 0,
      physics: this.currentTimings.physics ?? 0,
      collision: this.currentTimings.collision ?? 0,
      combat: this.currentTimings.combat ?? 0,
      melee: this.currentTimings.melee ?? 0,  // Run 036: Mandible Reaver
      apex: this.currentTimings.apex ?? 0,    // Run 036: Apex Strike
      spawn: this.currentTimings.spawn ?? 0,
      formation: this.currentTimings.formation ?? 0,  // Run 036: THE BALL
      particles: this.currentTimings.particles ?? 0,
      render: this.currentTimings.render ?? 0,
      total: frameTime,
    };

    // Update timing history
    this.timingHistory.push(timings);
    if (this.timingHistory.length > this.HISTORY_LENGTH) {
      this.timingHistory.shift();
    }

    // Check for warnings
    const warnings: string[] = [];
    const overBudgetSystems: (keyof SystemTimings)[] = [];

    // Check individual system budgets
    const budgets = PERF_BUDGET.budgets;
    if (timings.physics > budgets.physics * PERF_BUDGET.warnings.systemOverBudget) {
      warnings.push(`Physics over budget: ${timings.physics.toFixed(1)}ms > ${budgets.physics}ms`);
      overBudgetSystems.push('physics');
    }
    if (timings.collision > budgets.collision * PERF_BUDGET.warnings.systemOverBudget) {
      warnings.push(`Collision over budget: ${timings.collision.toFixed(1)}ms > ${budgets.collision}ms`);
      overBudgetSystems.push('collision');
    }
    if (timings.combat > budgets.combat * PERF_BUDGET.warnings.systemOverBudget) {
      warnings.push(`Combat over budget: ${timings.combat.toFixed(1)}ms > ${budgets.combat}ms`);
      overBudgetSystems.push('combat');
    }
    if (timings.particles > budgets.particles * PERF_BUDGET.warnings.systemOverBudget) {
      warnings.push(`Particles over budget: ${timings.particles.toFixed(1)}ms > ${budgets.particles}ms`);
      overBudgetSystems.push('particles');
    }
    if (timings.render > budgets.render * PERF_BUDGET.warnings.systemOverBudget) {
      warnings.push(`Render over budget: ${timings.render.toFixed(1)}ms > ${budgets.render}ms`);
      overBudgetSystems.push('render');
    }

    // Check total frame budget
    if (frameTime > PERF_BUDGET.frameTime * PERF_BUDGET.warnings.frameOverBudget) {
      warnings.push(`Frame over budget: ${frameTime.toFixed(1)}ms > ${PERF_BUDGET.frameTime.toFixed(1)}ms`);
      overBudgetSystems.push('total');
    }

    // Check FPS thresholds
    if (this.currentFPS < PERF_BUDGET.warnings.criticalFPS) {
      warnings.push(`CRITICAL: FPS at ${this.currentFPS} - enable degradation`);
    } else if (this.currentFPS < PERF_BUDGET.warnings.warningFPS) {
      warnings.push(`WARNING: FPS at ${this.currentFPS}`);
    }

    // Check entity limits
    if (counts.enemies > PERF_BUDGET.limits.maxEnemies * 0.9) {
      warnings.push(`Approaching enemy limit: ${counts.enemies}/${PERF_BUDGET.limits.maxEnemies}`);
    }
    if (counts.particles > PERF_BUDGET.limits.maxParticles * 0.9) {
      warnings.push(`Approaching particle limit: ${counts.particles}/${PERF_BUDGET.limits.maxParticles}`);
    }

    // Calculate spatial hash stats
    const avgQueryTime = this.queryTimes.length > 0
      ? this.queryTimes.reduce((a, b) => a + b, 0) / this.queryTimes.length
      : 0;

    return {
      frameTime,
      frameTimeHistory: [...this.frameTimeHistory],
      fps: this.currentFPS,
      fpsHistory: [...this.fpsHistory],
      timings,
      timingHistory: [...this.timingHistory],
      counts,
      warnings,
      overBudgetSystems,
      spatialHashStats: {
        cellCount: 0,  // Will be filled by spatial hash
        avgEntitiesPerCell: 0,
        queryCount: this.queryTimes.length,
        avgQueryTime,
      },
    };
  }

  /**
   * Record a spatial hash query time
   */
  recordQueryTime(ms: number): void {
    this.queryTimes.push(ms);
    if (this.queryTimes.length > 100) {
      this.queryTimes.shift();
    }
  }

  /**
   * Get current pressure level (0-1, where 1 = at budget limit)
   */
  getPressure(): number {
    if (this.frameTimeHistory.length === 0) return 0;

    // Average of last 10 frames
    const recentFrames = this.frameTimeHistory.slice(-10);
    const avgFrameTime = recentFrames.reduce((a, b) => a + b, 0) / recentFrames.length;

    return Math.min(1, avgFrameTime / PERF_BUDGET.frameTime);
  }

  /**
   * Check if we should enable performance degradation
   */
  shouldDegrade(): boolean {
    return this.currentFPS < PERF_BUDGET.warnings.warningFPS;
  }

  /**
   * Get degradation level (0 = none, 1 = max degradation)
   */
  getDegradationLevel(): number {
    if (this.currentFPS >= PERF_BUDGET.warnings.warningFPS) return 0;
    if (this.currentFPS <= PERF_BUDGET.warnings.criticalFPS * 0.8) return 1;

    // Linear interpolation between warning and critical
    const range = PERF_BUDGET.warnings.warningFPS - PERF_BUDGET.warnings.criticalFPS * 0.8;
    const position = PERF_BUDGET.warnings.warningFPS - this.currentFPS;
    return Math.min(1, position / range);
  }
}

// =============================================================================
// Spatial Hash for O(k) Collision Detection
// =============================================================================

interface SpatialEntity {
  id: string;
  position: Vector2;
  radius: number;
}

export class SpatialHash {
  private cellSize: number;
  private cells: Map<string, Set<string>> = new Map();
  private entityPositions: Map<string, { cellKeys: string[]; entity: SpatialEntity }> = new Map();

  constructor(cellSize: number = 64) {
    this.cellSize = cellSize;
  }

  /**
   * Get all cells that an entity overlaps
   */
  private getEntityCells(entity: SpatialEntity): string[] {
    const keys: string[] = [];
    const minX = entity.position.x - entity.radius;
    const maxX = entity.position.x + entity.radius;
    const minY = entity.position.y - entity.radius;
    const maxY = entity.position.y + entity.radius;

    const minCellX = Math.floor(minX / this.cellSize);
    const maxCellX = Math.floor(maxX / this.cellSize);
    const minCellY = Math.floor(minY / this.cellSize);
    const maxCellY = Math.floor(maxY / this.cellSize);

    for (let cx = minCellX; cx <= maxCellX; cx++) {
      for (let cy = minCellY; cy <= maxCellY; cy++) {
        keys.push(`${cx},${cy}`);
      }
    }

    return keys;
  }

  /**
   * Insert an entity into the spatial hash
   */
  insert(entity: SpatialEntity): void {
    // Remove from old position if exists
    this.remove(entity.id);

    // Get cells this entity occupies
    const cellKeys = this.getEntityCells(entity);

    // Add to each cell
    for (const key of cellKeys) {
      if (!this.cells.has(key)) {
        this.cells.set(key, new Set());
      }
      this.cells.get(key)!.add(entity.id);
    }

    // Store entity info
    this.entityPositions.set(entity.id, { cellKeys, entity });
  }

  /**
   * Update an entity's position (optimized for small moves)
   */
  update(entity: SpatialEntity): void {
    const existing = this.entityPositions.get(entity.id);
    if (!existing) {
      this.insert(entity);
      return;
    }

    // Check if cells changed
    const newCellKeys = this.getEntityCells(entity);
    const oldKeys = new Set(existing.cellKeys);
    const newKeys = new Set(newCellKeys);

    // Check if same cells
    let same = oldKeys.size === newKeys.size;
    if (same) {
      for (const key of oldKeys) {
        if (!newKeys.has(key)) {
          same = false;
          break;
        }
      }
    }

    if (same) {
      // Just update entity reference
      existing.entity = entity;
    } else {
      // Remove from old cells
      for (const key of existing.cellKeys) {
        const cell = this.cells.get(key);
        if (cell) {
          cell.delete(entity.id);
          if (cell.size === 0) {
            this.cells.delete(key);
          }
        }
      }

      // Add to new cells
      for (const key of newCellKeys) {
        if (!this.cells.has(key)) {
          this.cells.set(key, new Set());
        }
        this.cells.get(key)!.add(entity.id);
      }

      // Update stored info
      this.entityPositions.set(entity.id, { cellKeys: newCellKeys, entity });
    }
  }

  /**
   * Remove an entity from the spatial hash
   */
  remove(entityId: string): void {
    const existing = this.entityPositions.get(entityId);
    if (!existing) return;

    // Remove from all cells
    for (const key of existing.cellKeys) {
      const cell = this.cells.get(key);
      if (cell) {
        cell.delete(entityId);
        if (cell.size === 0) {
          this.cells.delete(key);
        }
      }
    }

    this.entityPositions.delete(entityId);
  }

  /**
   * Query for entities near a position
   * Returns entity IDs within queryRadius of position
   */
  query(position: Vector2, queryRadius: number): string[] {
    const results: string[] = [];
    const seen = new Set<string>();

    // Get cells in query range
    const minCellX = Math.floor((position.x - queryRadius) / this.cellSize);
    const maxCellX = Math.floor((position.x + queryRadius) / this.cellSize);
    const minCellY = Math.floor((position.y - queryRadius) / this.cellSize);
    const maxCellY = Math.floor((position.y + queryRadius) / this.cellSize);

    for (let cx = minCellX; cx <= maxCellX; cx++) {
      for (let cy = minCellY; cy <= maxCellY; cy++) {
        const cell = this.cells.get(`${cx},${cy}`);
        if (!cell) continue;

        for (const entityId of cell) {
          if (seen.has(entityId)) continue;
          seen.add(entityId);

          const info = this.entityPositions.get(entityId);
          if (!info) continue;

          // Distance check
          const dx = info.entity.position.x - position.x;
          const dy = info.entity.position.y - position.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist <= queryRadius + info.entity.radius) {
            results.push(entityId);
          }
        }
      }
    }

    return results;
  }

  /**
   * Get all entity IDs
   */
  getAllIds(): string[] {
    return Array.from(this.entityPositions.keys());
  }

  /**
   * Get entity by ID
   */
  getEntity(id: string): SpatialEntity | undefined {
    return this.entityPositions.get(id)?.entity;
  }

  /**
   * Clear all entities
   */
  clear(): void {
    this.cells.clear();
    this.entityPositions.clear();
  }

  /**
   * Get statistics for debugging
   */
  getStats(): { cellCount: number; entityCount: number; avgPerCell: number } {
    const cellCount = this.cells.size;
    const entityCount = this.entityPositions.size;
    const totalInCells = Array.from(this.cells.values())
      .reduce((sum, cell) => sum + cell.size, 0);
    const avgPerCell = cellCount > 0 ? totalInCells / cellCount : 0;

    return { cellCount, entityCount, avgPerCell };
  }
}

// =============================================================================
// Object Pools
// =============================================================================

/**
 * Generic object pool to reduce GC pressure
 */
export class ObjectPool<T> {
  private pool: T[] = [];
  private active: Set<T> = new Set();
  private factory: () => T;
  private reset: (obj: T) => void;
  private maxSize: number;

  constructor(
    factory: () => T,
    reset: (obj: T) => void,
    initialSize: number = 0,
    maxSize: number = 1000
  ) {
    this.factory = factory;
    this.reset = reset;
    this.maxSize = maxSize;

    // Pre-populate pool
    for (let i = 0; i < initialSize; i++) {
      this.pool.push(this.factory());
    }
  }

  /**
   * Acquire an object from the pool
   */
  acquire(): T {
    let obj: T;
    if (this.pool.length > 0) {
      obj = this.pool.pop()!;
    } else {
      obj = this.factory();
    }
    this.active.add(obj);
    return obj;
  }

  /**
   * Release an object back to the pool
   */
  release(obj: T): void {
    if (!this.active.has(obj)) return;

    this.active.delete(obj);
    this.reset(obj);

    if (this.pool.length < this.maxSize) {
      this.pool.push(obj);
    }
    // If over max size, let GC collect it
  }

  /**
   * Get current pool stats
   */
  getStats(): { pooled: number; active: number } {
    return {
      pooled: this.pool.length,
      active: this.active.size,
    };
  }

  /**
   * Clear the pool and release all active objects
   */
  clear(): void {
    this.pool = [];
    this.active.clear();
  }
}

// =============================================================================
// Particle Budget Enforcement
// =============================================================================

export interface ParticleBudgetConfig {
  maxParticles: number;
  warningThreshold: number;  // Fraction (0-1) where we start reducing
  criticalThreshold: number; // Fraction where we aggressively cull
}

export const DEFAULT_PARTICLE_BUDGET: ParticleBudgetConfig = {
  maxParticles: 500,
  warningThreshold: 0.7,  // At 70%, start reducing new particles
  criticalThreshold: 0.9, // At 90%, kill old particles aggressively
};

/**
 * Calculate how many particles to actually emit based on budget
 */
export function budgetParticles(
  requested: number,
  currentCount: number,
  config: ParticleBudgetConfig = DEFAULT_PARTICLE_BUDGET
): number {
  const pressure = currentCount / config.maxParticles;

  if (pressure < config.warningThreshold) {
    // Under warning threshold - emit all
    return requested;
  } else if (pressure < config.criticalThreshold) {
    // In warning zone - reduce proportionally
    const reduction = (pressure - config.warningThreshold) /
                     (config.criticalThreshold - config.warningThreshold);
    return Math.max(1, Math.floor(requested * (1 - reduction * 0.5)));
  } else {
    // In critical zone - emit minimum
    return Math.min(requested, 2);
  }
}

/**
 * Calculate how many old particles to cull based on budget
 */
export function calculateParticleCull(
  currentCount: number,
  config: ParticleBudgetConfig = DEFAULT_PARTICLE_BUDGET
): number {
  if (currentCount <= config.maxParticles) {
    return 0;
  }
  // Remove excess + 10% buffer
  return Math.ceil((currentCount - config.maxParticles) * 1.1);
}

// =============================================================================
// Singleton Instances
// =============================================================================

// Global performance monitor instance
export const perfMonitor = new PerformanceMonitor();

// Global spatial hash for enemies (64px cells work well for typical enemy sizes)
export const enemySpatialHash = new SpatialHash(64);

// Global spatial hash for projectiles (smaller cells for faster projectiles)
export const projectileSpatialHash = new SpatialHash(32);
