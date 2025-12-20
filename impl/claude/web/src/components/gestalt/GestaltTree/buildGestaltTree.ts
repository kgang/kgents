/**
 * buildGestaltTree - Tree building and health aggregation algorithms.
 *
 * Two tree builders:
 * - buildLayerTree: Groups by architectural layer (protocols/api, services/brain)
 * - buildPathTree: Full module path hierarchy (impl/claude/protocols/api)
 *
 * Health aggregation rules:
 * - healthGrade: Worst grade in subtree (A+ < A < B+ < ... < F)
 * - healthScore: Weighted average by lines of code
 * - hasViolation: true if ANY descendant has violation
 * - violationCount: Sum of violations in subtree
 *
 * @see spec/protocols/2d-renaissance.md - Phase 3: Gestalt2D
 */

import type { CodebaseModule, DependencyLink } from '@/api/types';
import type { GestaltNode } from './types';
import { gradeToNumber, numberToGrade } from './types';

// =============================================================================
// Violation Mapping
// =============================================================================

/**
 * Build a map of module ID → violation count.
 * Counts violations where module is the SOURCE of the violation.
 */
export function getViolationMap(links: DependencyLink[]): Map<string, number> {
  const map = new Map<string, number>();

  for (const link of links) {
    if (link.is_violation) {
      const current = map.get(link.source) || 0;
      map.set(link.source, current + 1);
    }
  }

  return map;
}

// =============================================================================
// Layer-First Tree Builder
// =============================================================================

/**
 * Build tree grouped by architectural layer.
 *
 * Structure: layer → sublayer/module → module
 * Example: protocols → agentese → gateway.py
 *
 * This matches the mental model of "protocols, services, agents" layers.
 */
export function buildLayerTree(
  modules: CodebaseModule[],
  links: DependencyLink[]
): Map<string, GestaltNode> {
  const violationMap = getViolationMap(links);
  const root = new Map<string, GestaltNode>();

  for (const module of modules) {
    const layer = module.layer || 'unknown';
    const segments = module.id.split('.');
    const violations = violationMap.get(module.id) || 0;

    // Get or create layer node
    if (!root.has(layer)) {
      root.set(layer, createEmptyNode(layer, layer));
    }
    const layerNode = root.get(layer);
    if (!layerNode) continue; // Should never happen due to set above

    // If module ID has segments beyond the layer, create intermediate nodes
    // Example: "protocols.agentese.gateway" → [agentese, gateway]
    // We skip segments that match the layer name
    const relevantSegments = segments.filter((s) => s !== layer && s !== 'impl' && s !== 'claude');

    if (relevantSegments.length === 0) {
      // Module directly under layer (rare, but handle it)
      insertModuleAtNode(layerNode, module, violations);
    } else if (relevantSegments.length === 1) {
      // Single-level nesting: layer → module
      insertModuleAtNode(layerNode, module, violations, relevantSegments[0]);
    } else {
      // Multi-level nesting: layer → sublayer → ... → module
      let currentNode = layerNode;
      let currentPath = layer;

      // Create intermediate nodes (all but last segment)
      for (let i = 0; i < relevantSegments.length - 1; i++) {
        const segment = relevantSegments[i];
        currentPath = `${currentPath}.${segment}`;

        if (!currentNode.children.has(segment)) {
          currentNode.children.set(segment, createEmptyNode(segment, currentPath));
        }
        const nextNode = currentNode.children.get(segment);
        if (!nextNode) continue; // Should never happen due to set above
        currentNode = nextNode;
      }

      // Insert module as leaf
      const leafSegment = relevantSegments[relevantSegments.length - 1];
      insertModuleAtNode(currentNode, module, violations, leafSegment);
    }
  }

  // Aggregate health metrics bottom-up
  for (const node of root.values()) {
    aggregateHealth(node);
  }

  return root;
}

// =============================================================================
// Full-Path Tree Builder
// =============================================================================

/**
 * Build tree with full module path hierarchy.
 *
 * Structure: impl → claude → protocols → agentese → gateway.py
 *
 * Best for deep exploration of unfamiliar codebases.
 */
export function buildPathTree(
  modules: CodebaseModule[],
  links: DependencyLink[]
): Map<string, GestaltNode> {
  const violationMap = getViolationMap(links);
  const root = new Map<string, GestaltNode>();

  for (const module of modules) {
    const segments = module.id.split('.');
    const violations = violationMap.get(module.id) || 0;

    let currentLevel = root;
    let currentPath = '';

    // Create all intermediate nodes
    for (let i = 0; i < segments.length - 1; i++) {
      const segment = segments[i];
      currentPath = currentPath ? `${currentPath}.${segment}` : segment;

      if (!currentLevel.has(segment)) {
        currentLevel.set(segment, createEmptyNode(segment, currentPath));
      }

      const node = currentLevel.get(segment);
      if (!node) continue; // Should never happen due to set above
      currentLevel = node.children;
    }

    // Insert leaf node (the module)
    const leafSegment = segments[segments.length - 1];
    const leafPath = currentPath ? `${currentPath}.${leafSegment}` : leafSegment;

    const leafNode: GestaltNode = {
      segment: leafSegment,
      path: leafPath,
      children: new Map(),
      isLeaf: true,
      healthGrade: module.health_grade,
      healthScore: module.health_score,
      moduleCount: 1,
      hasViolation: violations > 0,
      violationCount: violations,
      linesOfCode: module.lines_of_code,
      module,
    };

    currentLevel.set(leafSegment, leafNode);
  }

  // Aggregate health metrics bottom-up
  for (const node of root.values()) {
    aggregateHealth(node);
  }

  return root;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Create an empty intermediate node.
 */
function createEmptyNode(segment: string, path: string): GestaltNode {
  return {
    segment,
    path,
    children: new Map(),
    isLeaf: false,
    healthGrade: 'A+', // Will be overwritten by aggregation
    healthScore: 1.0,
    moduleCount: 0,
    hasViolation: false,
    violationCount: 0,
    linesOfCode: 0,
  };
}

/**
 * Insert a module as a leaf node under a parent.
 */
function insertModuleAtNode(
  parent: GestaltNode,
  module: CodebaseModule,
  violations: number,
  segment?: string
): void {
  const nodeSegment = segment || module.label || module.id.split('.').pop() || module.id;
  const nodePath = parent.path ? `${parent.path}.${nodeSegment}` : nodeSegment;

  const leafNode: GestaltNode = {
    segment: nodeSegment,
    path: nodePath,
    children: new Map(),
    isLeaf: true,
    healthGrade: module.health_grade,
    healthScore: module.health_score,
    moduleCount: 1,
    hasViolation: violations > 0,
    violationCount: violations,
    linesOfCode: module.lines_of_code,
    module,
  };

  parent.children.set(nodeSegment, leafNode);
}

/**
 * Aggregate health metrics from children to parent (post-order traversal).
 * Modifies nodes in place.
 */
function aggregateHealth(node: GestaltNode): void {
  // Base case: leaf nodes already have their metrics
  if (node.isLeaf || node.children.size === 0) {
    return;
  }

  // Recurse to children first (post-order)
  for (const child of node.children.values()) {
    aggregateHealth(child);
  }

  // Aggregate from children
  const children = Array.from(node.children.values());

  // Worst grade in subtree
  const grades = children.map((c) => c.healthGrade);
  const gradeNums = grades.map(gradeToNumber);
  const worstGradeNum = Math.max(...gradeNums);
  node.healthGrade = numberToGrade(worstGradeNum);

  // Weighted average score by LoC
  const totalLoC = children.reduce((sum, c) => sum + c.linesOfCode, 0);
  if (totalLoC > 0) {
    node.healthScore =
      children.reduce((sum, c) => sum + c.healthScore * c.linesOfCode, 0) / totalLoC;
  } else {
    node.healthScore = children.reduce((sum, c) => sum + c.healthScore, 0) / children.length;
  }

  // Module count: sum of all descendants
  node.moduleCount = children.reduce((sum, c) => sum + c.moduleCount, 0);

  // Violation propagation
  node.hasViolation = children.some((c) => c.hasViolation);
  node.violationCount = children.reduce((sum, c) => sum + c.violationCount, 0);

  // Lines of code: sum
  node.linesOfCode = totalLoC;
}

// =============================================================================
// Export Default
// =============================================================================

/**
 * Build tree with specified mode.
 */
export function buildGestaltTree(
  modules: CodebaseModule[],
  links: DependencyLink[],
  mode: 'layer' | 'path' = 'layer'
): Map<string, GestaltNode> {
  return mode === 'layer' ? buildLayerTree(modules, links) : buildPathTree(modules, links);
}

export default buildGestaltTree;
