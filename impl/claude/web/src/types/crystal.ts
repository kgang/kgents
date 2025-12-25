/**
 * Crystal Types — Memory Compression Units
 *
 * TypeScript types matching the backend Crystal schema.
 * See: impl/claude/services/witness/crystal.py
 */

export type CrystalLevel = 'SESSION' | 'DAY' | 'WEEK' | 'EPOCH';

export interface MoodVector {
  warmth: number;      // 0-1: Cold/clinical ↔ Warm/engaging
  weight: number;      // 0-1: Light/playful ↔ Heavy/serious
  tempo: number;       // 0-1: Slow/deliberate ↔ Fast/urgent
  texture: number;     // 0-1: Smooth/flowing ↔ Rough/struggling
  brightness: number;  // 0-1: Dim/frustrated ↔ Bright/joyful
  saturation: number;  // 0-1: Muted/routine ↔ Vivid/intense
  complexity: number;  // 0-1: Simple/focused ↔ Complex/branching
}

export interface Crystal {
  id: string;
  level: CrystalLevel;
  insight: string;
  significance: string;
  mood: MoodVector;
  confidence: number;
  sourceMarkIds: string[];
  sourceCrystalIds: string[];
  principles: string[];
  topics: string[];
  crystallizedAt: string; // ISO 8601
  periodStart?: string;   // ISO 8601
  periodEnd?: string;     // ISO 8601
  sessionId?: string;
  compressionRatio?: number;
}

/**
 * Crystallization request payload
 */
export interface CrystallizeRequest {
  sessionId?: string;
  notes?: string;
  tags?: string[];
}

/**
 * Crystallization response
 */
export interface CrystallizeResponse {
  crystal: Crystal;
  message?: string;
}
