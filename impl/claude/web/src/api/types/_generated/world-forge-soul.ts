/**
 * Generated types for AGENTESE path: world.forge.soul
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * K-gent soul state manifest response.
 */
export interface WorldForgeSoulManifestResponse {
  mode: string;
  eigenvectors: Record<string, number>;
  session_interactions: number;
  session_tokens: number;
  has_llm: boolean;
}

/**
 * K-gent personality eigenvector response.
 */
export interface WorldForgeSoulVibeResponse {
  dimensions: Record<string, number>;
  context: string;
}
