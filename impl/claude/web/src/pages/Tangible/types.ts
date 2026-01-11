/**
 * K-Games Studio Types
 *
 * Type definitions for the GameKernel, MechanicComposer, and EvidenceStream
 * components in the Self-Reflective OS Create Mode.
 *
 * Based on the GameKernel/GameOperad architecture from the backend.
 *
 * @see plans/self-reflective-os/
 */

// =============================================================================
// GameKernel Types (A1-A4 Axioms + Values)
// =============================================================================

/**
 * An axiom in the GameKernel - represents a fundamental game design truth.
 * These are the irreducible foundations from which mechanics derive.
 */
export interface Axiom {
  /** Unique identifier (e.g., 'A1', 'A2') */
  id: string;
  /** Human-readable name */
  name: string;
  /** Formal statement of the axiom */
  statement: string;
  /** Extended description */
  description: string;
  /** Evidence supporting this axiom */
  evidence: string[];
  /** Confidence in this axiom (0-1) */
  confidence: number;
}

/**
 * A value derived from axioms - represents a design principle.
 */
export interface GameValue {
  /** Unique identifier (e.g., 'V1', 'V2') */
  id: string;
  /** Human-readable name */
  name: string;
  /** Description of the value */
  description: string;
  /** Axioms this value derives from */
  derivedFrom: string[];
  /** How strongly this value is grounded (0-1) */
  strength: number;
}

/**
 * The GameKernel - the constitutional foundation of a K-Game.
 *
 * Four axioms (A1-A4):
 * - A1 (Agency): Player choices must matter
 * - A2 (Attribution): Player must understand cause/effect
 * - A3 (Mastery): Skill must be rewardable
 * - A4 (Composition): Mechanics must compose cleanly
 */
export interface GameKernel {
  /** A1: Agency axiom */
  agency: Axiom;
  /** A2: Attribution axiom */
  attribution: Axiom;
  /** A3: Mastery axiom */
  mastery: Axiom;
  /** A4: Composition axiom */
  composition: Axiom;
  /** Derived values */
  values: GameValue[];
  /** Overall kernel health (0-1) */
  health: number;
  /** Last updated timestamp */
  updatedAt: Date;
}

// =============================================================================
// Mechanic Composition Types
// =============================================================================

/**
 * A game mechanic - the atomic unit of game design.
 */
export interface Mechanic {
  /** Unique identifier */
  id: string;
  /** Human-readable name */
  name: string;
  /** Verbs this mechanic enables */
  verbs: string[];
  /** Visual/audio tells that signal this mechanic */
  tells: string[];
  /** Input type signature */
  inputType: string;
  /** Output type signature */
  outputType: string;
  /** Contrast poles (e.g., ['risk', 'safety']) */
  contrastPoles: [string, string];
  /** Description of the mechanic */
  description: string;
  /** Axioms this mechanic is grounded in */
  groundedIn: string[];
}

/**
 * Composition operations in the GameOperad.
 */
export type CompositionOp =
  | { type: 'sequential'; symbol: '>>' } // Then
  | { type: 'parallel'; symbol: '||' } // And
  | { type: 'conditional'; symbol: '?:' } // If
  | { type: 'feedback'; symbol: 'loop' }; // Repeat

/**
 * A composition node in the visual editor.
 */
export interface CompositionNode {
  /** Unique identifier */
  id: string;
  /** Type of node */
  type: 'mechanic' | 'operation' | 'group';
  /** Position in the graph */
  position: { x: number; y: number };
  /** For mechanic nodes: the mechanic reference */
  mechanicId?: string;
  /** For operation nodes: the operation type */
  operation?: CompositionOp;
  /** Child node IDs (for group/operation nodes) */
  children?: string[];
}

/**
 * An edge connecting nodes in the composition graph.
 */
export interface CompositionEdge {
  /** Unique identifier */
  id: string;
  /** Source node ID */
  source: string;
  /** Target node ID */
  target: string;
  /** Edge label (for conditional branches) */
  label?: string;
}

/**
 * A mechanic composition - the result of combining mechanics.
 */
export interface MechanicComposition {
  /** Unique identifier */
  id: string;
  /** Human-readable name */
  name: string;
  /** The verbs this composition enables */
  verbs: string[];
  /** The tells this composition has */
  tells: string[];
  /** Combined input type */
  inputType: string;
  /** Combined output type */
  outputType: string;
  /** Derived contrast poles */
  contrastPoles: [string, string];
  /** Galois loss (how much information lost in composition) */
  galoisLoss: number;
  /** Nodes in the composition graph */
  nodes: CompositionNode[];
  /** Edges in the composition graph */
  edges: CompositionEdge[];
  /** Source mechanic IDs */
  sourceMechanics: string[];
  /** Composition expression (e.g., "M1 >> M2 || M3") */
  expression: string;
}

/**
 * The GameOperad - defines valid composition operations.
 */
export interface GameOperad {
  /** Available operations */
  operations: CompositionOp[];
  /** Composition laws (associativity, distributivity, etc.) */
  laws: OperadLaw[];
}

/**
 * A law governing mechanic composition.
 */
export interface OperadLaw {
  /** Law name */
  name: string;
  /** Law statement */
  statement: string;
  /** Whether this law is currently satisfied */
  satisfied: boolean;
  /** Evidence for satisfaction/violation */
  evidence?: string;
}

// =============================================================================
// Evidence Stream Types
// =============================================================================

/**
 * Evidence filter configuration.
 */
export interface EvidenceFilter {
  /** Filter by mechanic IDs */
  mechanicIds?: string[];
  /** Filter by axiom IDs */
  axiomIds?: string[];
  /** Filter by time range */
  timeRange?: { start: Date; end: Date };
  /** Filter by quality level */
  minQuality?: number;
}

/**
 * A quality crystal from a playthrough.
 */
export interface QualityCrystal {
  /** Unique identifier */
  id: string;
  /** Associated mechanic composition */
  compositionId: string;
  /** When this was crystallized */
  timestamp: Date;
  /** Quality scores by axiom */
  axiomScores: Record<string, number>;
  /** Overall quality (0-1) */
  overallQuality: number;
  /** Player actions that contributed */
  playerActions: string[];
  /** Duration in seconds */
  duration: number;
}

/**
 * Galois loss data point for visualization.
 */
export interface GaloisLossPoint {
  /** Timestamp */
  timestamp: Date;
  /** Loss value (0-1, lower is better) */
  loss: number;
  /** What contributed to this loss */
  contributors: string[];
}

/**
 * Live evidence stream data.
 */
export interface EvidenceStreamData {
  /** Current game session ID */
  sessionId: string;
  /** Recent quality crystals */
  crystals: QualityCrystal[];
  /** Galois loss over time */
  lossHistory: GaloisLossPoint[];
  /** Current aggregate loss */
  currentLoss: number;
  /** Is stream active */
  isLive: boolean;
}

// =============================================================================
// Editor State Types
// =============================================================================

/**
 * State for the MechanicComposer.
 */
export interface ComposerState {
  /** Currently selected node */
  selectedNodeId: string | null;
  /** Nodes being dragged */
  draggingNodeIds: string[];
  /** Current composition being edited */
  composition: MechanicComposition | null;
  /** Available mechanics library */
  mechanicsLibrary: Mechanic[];
  /** Zoom level (1 = 100%) */
  zoom: number;
  /** Pan offset */
  pan: { x: number; y: number };
  /** Edit mode */
  mode: 'select' | 'connect' | 'add';
}

/**
 * Action type for the composer reducer.
 */
export type ComposerAction =
  | { type: 'SELECT_NODE'; nodeId: string | null }
  | { type: 'START_DRAG'; nodeIds: string[] }
  | { type: 'END_DRAG' }
  | { type: 'MOVE_NODE'; nodeId: string; position: { x: number; y: number } }
  | { type: 'ADD_NODE'; node: CompositionNode }
  | { type: 'REMOVE_NODE'; nodeId: string }
  | { type: 'ADD_EDGE'; edge: CompositionEdge }
  | { type: 'REMOVE_EDGE'; edgeId: string }
  | { type: 'SET_ZOOM'; zoom: number }
  | { type: 'SET_PAN'; pan: { x: number; y: number } }
  | { type: 'SET_MODE'; mode: ComposerState['mode'] }
  | { type: 'LOAD_COMPOSITION'; composition: MechanicComposition }
  | { type: 'CLEAR_COMPOSITION' };

// =============================================================================
// Mock Data Factories
// =============================================================================

/**
 * Creates a default GameKernel with the four axioms.
 */
export function createDefaultGameKernel(): GameKernel {
  return {
    agency: {
      id: 'A1',
      name: 'Agency',
      statement: 'Player choices must have meaningful consequences',
      description:
        'Every player action should result in a perceivable change to the game state that matters for their goals.',
      evidence: [],
      confidence: 1.0,
    },
    attribution: {
      id: 'A2',
      name: 'Attribution',
      statement: 'Players must understand the causal chain from action to outcome',
      description:
        'The relationship between player input and game response must be learnable and predictable.',
      evidence: [],
      confidence: 1.0,
    },
    mastery: {
      id: 'A3',
      name: 'Mastery',
      statement: 'Skill investment must yield proportional reward',
      description: 'Players who develop expertise should experience measurably better outcomes.',
      evidence: [],
      confidence: 1.0,
    },
    composition: {
      id: 'A4',
      name: 'Composition',
      statement: 'Mechanics must compose without emergent pathology',
      description:
        'When mechanics are combined, the result should be predictable and not produce degenerate strategies.',
      evidence: [],
      confidence: 1.0,
    },
    values: [
      {
        id: 'V1',
        name: 'Flow',
        description: 'Derived from Agency + Mastery - the state of engaged challenge',
        derivedFrom: ['A1', 'A3'],
        strength: 0.9,
      },
      {
        id: 'V2',
        name: 'Fairness',
        description: 'Derived from Attribution + Mastery - outcomes feel earned',
        derivedFrom: ['A2', 'A3'],
        strength: 0.85,
      },
      {
        id: 'V3',
        name: 'Discovery',
        description: 'Derived from Composition + Agency - exploring mechanic space',
        derivedFrom: ['A4', 'A1'],
        strength: 0.8,
      },
      {
        id: 'V4',
        name: 'Expression',
        description: 'Derived from all axioms - personal style emerges',
        derivedFrom: ['A1', 'A2', 'A3', 'A4'],
        strength: 0.75,
      },
      {
        id: 'V5',
        name: 'Learning',
        description: 'Derived from Attribution + Composition - understanding deepens',
        derivedFrom: ['A2', 'A4'],
        strength: 0.88,
      },
    ],
    health: 0.92,
    updatedAt: new Date(),
  };
}

/**
 * Creates sample mechanics for the library.
 */
export function createSampleMechanics(): Mechanic[] {
  return [
    {
      id: 'M1',
      name: 'Jump',
      verbs: ['leap', 'vault', 'bound'],
      tells: ['wind-up squat', 'jump sound', 'dust particles'],
      inputType: 'Button',
      outputType: 'Position',
      contrastPoles: ['grounded', 'airborne'],
      description: 'Vertical movement that temporarily leaves the ground',
      groundedIn: ['A1', 'A2'],
    },
    {
      id: 'M2',
      name: 'Dash',
      verbs: ['burst', 'sprint', 'rush'],
      tells: ['motion blur', 'dash sound', 'trail effect'],
      inputType: 'Direction',
      outputType: 'Velocity',
      contrastPoles: ['slow', 'fast'],
      description: 'Rapid horizontal movement with invincibility frames',
      groundedIn: ['A1', 'A3'],
    },
    {
      id: 'M3',
      name: 'Attack',
      verbs: ['strike', 'slash', 'hit'],
      tells: ['weapon arc', 'impact flash', 'hit sound'],
      inputType: 'Button',
      outputType: 'Damage',
      contrastPoles: ['vulnerable', 'threatening'],
      description: 'Offensive action that damages enemies',
      groundedIn: ['A1', 'A2', 'A3'],
    },
    {
      id: 'M4',
      name: 'Block',
      verbs: ['defend', 'parry', 'guard'],
      tells: ['shield raise', 'block sound', 'spark effect'],
      inputType: 'Hold',
      outputType: 'DamageReduction',
      contrastPoles: ['open', 'protected'],
      description: 'Defensive stance that reduces incoming damage',
      groundedIn: ['A2', 'A3'],
    },
    {
      id: 'M5',
      name: 'Collect',
      verbs: ['gather', 'pick up', 'acquire'],
      tells: ['pickup sparkle', 'collect sound', 'counter increase'],
      inputType: 'Proximity',
      outputType: 'Inventory',
      contrastPoles: ['empty', 'full'],
      description: 'Acquiring items in the game world',
      groundedIn: ['A1', 'A4'],
    },
  ];
}
