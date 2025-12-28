/**
 * API Contracts
 *
 * Canonical source of truth for pilot API interfaces.
 * Both frontend and backend verify against these definitions.
 *
 * NOTE: Uses explicit exports to avoid ambiguous star export conflicts.
 * When multiple contracts define the same utility (e.g., extractErrorMessage),
 * we export only one version to prevent runtime errors.
 *
 * @see pilots/CONTRACT_COHERENCE.md
 */

// Daily Lab - primary daily journaling pilot
export * from './daily-lab';

// Galois - loss calculation contracts
export * from './galois';

// Zero Seed - personal governance lab
export * from './zero-seed';

// WASM Survivors - game contracts
export * from './wasm-survivors';

// Disney Portal Planner - trip planning contracts
// This module's extractErrorMessage takes precedence (more complete implementation)
export * from './disney-portal-planner';

// Sprite Procedural Taste Lab
export * from './sprite-procedural-taste-lab';

