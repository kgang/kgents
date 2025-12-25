/**
 * Mutation Detection — Identifies tools that require acknowledgment
 *
 * From spec/protocols/chat-web.md Part VII.2:
 * - READ operations: Silent (no notification needed)
 * - MUTATION operations: Require acknowledgment
 * - DESTRUCTIVE operations: Require explicit approval before execution
 *
 * "Reads can be silent; mutations must speak AND be heard."
 */

import type { ToolUse } from './store';
import type { PendingMutation } from './store';

// =============================================================================
// Tool Classification
// =============================================================================

/**
 * Tools that are pure reads (no mutation, no acknowledgment needed).
 */
const READ_TOOLS = new Set([
  'Read',
  'Grep',
  'Glob',
  'Bash', // When used for queries like 'ls', 'git status'
  'WebFetch',
  'WebSearch',
]);

/**
 * Tools that are destructive (irrecoverable mutations).
 */
const DESTRUCTIVE_TOOLS = new Set([
  'Bash', // When running destructive commands like 'rm', 'git push --force'
  // Note: Bash is context-dependent - we check command content
]);

/**
 * Tools that are mutations (require acknowledgment).
 * All tools not in READ_TOOLS are assumed to be mutations.
 * Note: This is for documentation purposes - we check against READ_TOOLS instead.
 */
const MUTATION_TOOLS = new Set([
  'Edit',
  'Write',
  'NotebookEdit',
]);

// Suppress unused warning - kept for documentation
void MUTATION_TOOLS;

// =============================================================================
// Detection Logic
// =============================================================================

/**
 * Check if a Bash command is destructive.
 */
function isBashCommandDestructive(input: Record<string, unknown>): boolean {
  const command = String(input.command || '');

  // Destructive patterns
  const destructivePatterns = [
    /\brm\s+-rf\b/,
    /\bgit\s+push\s+--force\b/,
    /\bgit\s+reset\s+--hard\b/,
    /\bdocker\s+system\s+prune\b/,
    /\bnpm\s+uninstall\b/,
  ];

  return destructivePatterns.some((pattern) => pattern.test(command));
}

/**
 * Check if a Bash command is a mutation.
 */
function isBashCommandMutation(input: Record<string, unknown>): boolean {
  const command = String(input.command || '');

  // Mutation patterns (non-destructive writes)
  const mutationPatterns = [
    /\bgit\s+commit\b/,
    /\bgit\s+push\b/,
    /\bgit\s+add\b/,
    /\bmkdir\b/,
    /\btouch\b/,
    /\bnpm\s+install\b/,
  ];

  return mutationPatterns.some((pattern) => pattern.test(command));
}

/**
 * Detect if a tool use is a mutation that requires acknowledgment.
 */
export function isMutation(tool: ToolUse): boolean {
  // READ_TOOLS are always non-mutations
  if (READ_TOOLS.has(tool.name)) {
    // Special case: Bash depends on command content
    if (tool.name === 'Bash') {
      return isBashCommandMutation(tool.input) || isBashCommandDestructive(tool.input);
    }
    return false;
  }

  // All other tools are mutations
  return true;
}

/**
 * Detect if a tool use is destructive.
 */
export function isDestructive(tool: ToolUse): boolean {
  if (DESTRUCTIVE_TOOLS.has(tool.name)) {
    if (tool.name === 'Bash') {
      return isBashCommandDestructive(tool.input);
    }
    return true;
  }
  return false;
}

/**
 * Create a pending mutation from a tool use.
 */
export function createPendingMutation(tool: ToolUse): PendingMutation {
  const is_destructive = isDestructive(tool);

  // Generate description based on tool
  let description = '';
  let target: string | undefined;

  switch (tool.name) {
    case 'Edit':
      description = 'Modified file';
      target = String(tool.input.file_path || '');
      break;
    case 'Write':
      description = 'Wrote file';
      target = String(tool.input.file_path || '');
      break;
    case 'NotebookEdit':
      description = 'Modified notebook';
      target = String(tool.input.notebook_path || '');
      break;
    case 'Bash': {
      const command = String(tool.input.command || '');
      if (isBashCommandDestructive(tool.input)) {
        description = 'Executed destructive command';
      } else {
        description = 'Executed command';
      }
      target = command.length > 50 ? command.slice(0, 50) + '...' : command;
      break;
    }
    default:
      description = 'Performed action';
      break;
  }

  return {
    id: `${tool.name}-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
    tool_name: tool.name,
    description,
    target,
    is_destructive,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Extract pending mutations from a list of tool uses.
 * Only returns tools that are mutations and succeeded.
 */
export function extractPendingMutations(tools: ToolUse[]): PendingMutation[] {
  return tools
    .filter((tool) => tool.success && isMutation(tool))
    .map(createPendingMutation);
}
