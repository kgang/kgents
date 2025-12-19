/**
 * TerminalService - AGENTESE Terminal Logic and Persistence
 *
 * The terminal service handles command execution, history persistence,
 * tab completion, and collections for the OS Shell terminal layer.
 *
 * Features:
 * - Full AGENTESE grammar support (paths, composition, queries)
 * - Tab completion from registry
 * - History persistence (localStorage, upgradeable to D-gent)
 * - Collections (save/load request sets)
 * - Discovery tools (?, help, affordances)
 * - Aliases for shortcuts
 *
 * @see spec/protocols/os-shell.md Part VI: Terminal Service
 */

import { nanoid } from 'nanoid';
import { apiClient } from '@/api/client';
import type {
  HistoryEntry,
  TerminalCollection,
  CompletionSuggestion,
  TerminalLine,
  PathInfo,
  Observer,
} from './types';

// =============================================================================
// Constants
// =============================================================================

/** Storage keys for persistence */
const STORAGE_KEYS = {
  history: 'kgents.terminal.history',
  collections: 'kgents.terminal.collections',
  aliases: 'kgents.terminal.aliases',
} as const;

/** Maximum history entries to retain */
const MAX_HISTORY = 100;

/** Minimum history entries to keep after pruning */
const MIN_HISTORY_AFTER_PRUNE = 20;

/** Maximum collections to retain */
const MAX_COLLECTIONS = 20;

/** Cache TTL in milliseconds (30 seconds) - AD-011 REPL Reliability */
const PATH_CACHE_TTL_MS = 30_000;

/** Default aliases */
const DEFAULT_ALIASES: Record<string, string> = {
  me: 'self.soul',
  brain: 'self.memory',
  garden: 'self.garden',
  town: 'world.town',
  park: 'world.park',
  code: 'world.codebase',
};

/** Built-in terminal commands */
const BUILTIN_COMMANDS = [
  'help',
  'clear',
  'history',
  'alias',
  'unalias',
  'save',
  'load',
  'collections',
  'affordances',
  'discover',
] as const;

type BuiltinCommand = (typeof BUILTIN_COMMANDS)[number];

// =============================================================================
// TerminalService Class
// =============================================================================

/**
 * Terminal service for AGENTESE CLI in browser.
 *
 * @example
 * ```typescript
 * const service = createTerminalService();
 *
 * // Execute command
 * const lines = await service.execute('self.memory.manifest');
 *
 * // Get completions
 * const suggestions = await service.complete('self.mem');
 *
 * // History management
 * service.searchHistory('memory');
 * ```
 */
export class TerminalService {
  private _history: HistoryEntry[] = [];
  private _collections: TerminalCollection[] = [];
  private _aliases: Record<string, string> = { ...DEFAULT_ALIASES };
  private _pathCache: PathInfo[] = [];
  private _pathCacheTimestamp: number = 0; // AD-011: Cache TTL tracking
  private _observer: Observer | null = null;

  constructor() {
    this._loadFromStorage();
  }

  // ===========================================================================
  // Public API
  // ===========================================================================

  /**
   * Set the observer context for invocations.
   */
  setObserver(observer: Observer): void {
    this._observer = observer;
  }

  /**
   * Execute a terminal command or AGENTESE path.
   *
   * @param input - The command string to execute
   * @returns Array of terminal output lines
   */
  async execute(input: string): Promise<TerminalLine[]> {
    const trimmed = input.trim();
    if (!trimmed) return [];

    const lines: TerminalLine[] = [];
    const startTime = Date.now();

    // Echo the input
    lines.push(this._createLine('input', `kg> ${trimmed}`));

    try {
      // Check for built-in commands first
      const builtin = this._parseBuiltinCommand(trimmed);
      if (builtin) {
        const result = await this._executeBuiltin(builtin.command, builtin.args);
        lines.push(...result);
        this._addHistoryEntry(trimmed, startTime, 'success');
        return lines;
      }

      // Check for query syntax (?path)
      if (trimmed.startsWith('?')) {
        const result = await this._executeQuery(trimmed.slice(1).trim());
        lines.push(...result);
        this._addHistoryEntry(trimmed, startTime, 'success');
        return lines;
      }

      // Expand aliases
      const expanded = this._expandAliases(trimmed);

      // Check for composition (>>)
      if (expanded.includes('>>')) {
        const result = await this._executeComposition(expanded);
        lines.push(...result);
        this._addHistoryEntry(trimmed, startTime, 'success');
        return lines;
      }

      // Execute as AGENTESE path
      const result = await this._executeAgentese(expanded);
      lines.push(...result);
      this._addHistoryEntry(trimmed, startTime, 'success', result);
      return lines;
    } catch (error) {
      // Format error with actionable hints
      const rawMsg = error instanceof Error ? error.message : String(error);
      const errorMsg = this._formatError(rawMsg, trimmed);
      lines.push(this._createLine('error', errorMsg));
      this._addHistoryEntry(trimmed, startTime, 'error', undefined, rawMsg);
      return lines;
    }
  }

  /**
   * Get command history.
   */
  get history(): HistoryEntry[] {
    return [...this._history];
  }

  /**
   * Search history by query.
   */
  searchHistory(query: string): HistoryEntry[] {
    const lower = query.toLowerCase();
    return this._history.filter((entry) => entry.input.toLowerCase().includes(lower));
  }

  /**
   * Clear all history.
   */
  clearHistory(): void {
    this._history = [];
    this._saveHistory();
  }

  /**
   * Get saved collections.
   */
  get collections(): TerminalCollection[] {
    return [...this._collections];
  }

  /**
   * Save commands to a named collection.
   */
  saveCollection(name: string, commands: string[]): void {
    const existing = this._collections.find((c) => c.name === name);
    const now = new Date();

    if (existing) {
      existing.commands = commands;
      existing.updatedAt = now;
    } else {
      this._collections.push({
        name,
        commands,
        createdAt: now,
        updatedAt: now,
      });
    }

    this._saveCollections();
  }

  /**
   * Load commands from a collection.
   */
  loadCollection(name: string): string[] {
    const collection = this._collections.find((c) => c.name === name);
    return collection?.commands ?? [];
  }

  /**
   * Delete a collection.
   */
  deleteCollection(name: string): void {
    this._collections = this._collections.filter((c) => c.name !== name);
    this._saveCollections();
  }

  /**
   * Discover available AGENTESE paths.
   *
   * AD-011 REPL Reliability: Uses cache with 30s TTL, surfaces errors with actionable hints.
   * Fetches metadata for richer path info (description, aspects).
   */
  async discover(context?: string): Promise<PathInfo[]> {
    const now = Date.now();
    const cacheValid =
      this._pathCache.length > 0 && now - this._pathCacheTimestamp < PATH_CACHE_TTL_MS;

    // Return cached paths if valid and not filtering by context
    if (cacheValid && !context) {
      return this._pathCache;
    }

    // Filter cached paths if context provided and cache is valid
    if (cacheValid && context) {
      return this._pathCache.filter((p) => p.context === context);
    }

    try {
      // Fetch from registry via AGENTESE gateway (AD-009)
      // Request metadata for richer path info
      const response = await apiClient.get<{
        paths: string[];
        metadata?: Record<
          string,
          {
            path: string;
            description: string | null;
            aspects: string[];
            effects: string[];
            examples: unknown[];
          }
        >;
      }>('/agentese/discover', {
        params: { include_metadata: true, ...(context ? { context } : {}) },
      });

      // Transform backend response to PathInfo format
      const pathInfos: PathInfo[] = response.data.paths.map((path) => {
        const meta = response.data.metadata?.[path];
        const pathContext = path.split('.')[0] as PathInfo['context'];

        return {
          path,
          description: meta?.description ?? undefined,
          aspects: meta?.aspects ?? ['manifest'],
          context: pathContext,
        };
      });

      // Filter by context if requested
      const filteredPaths = context ? pathInfos.filter((p) => p.context === context) : pathInfos;

      // Cache results (only for full discovery)
      if (!context) {
        this._pathCache = pathInfos;
        this._pathCacheTimestamp = now;
      }

      return filteredPaths;
    } catch (error) {
      // AD-011: Surface errors with hints, but provide fallback
      const msg = error instanceof Error ? error.message : String(error);
      console.warn(`[TerminalService] Discovery failed: ${msg}`);

      // Return well-known paths as fallback, but log the issue
      const fallback = this._getWellKnownPaths(context);
      console.info(`[TerminalService] Using ${fallback.length} well-known paths as fallback`);
      return fallback;
    }
  }

  /**
   * Get affordances for a path.
   *
   * AD-011 REPL Reliability: Surfaces errors with context, provides sensible fallback.
   */
  async affordances(path: string): Promise<string[]> {
    try {
      // Use gateway endpoint: /agentese/{path}/affordances (AD-009)
      const pathSegments = path.replace(/\./g, '/');
      const response = await apiClient.get<{
        path: string;
        affordances: string[];
      }>(`/agentese/${pathSegments}/affordances`, {
        headers: {
          'X-Observer-Archetype': this._observer?.archetype ?? 'developer',
        },
      });
      return response.data.affordances;
    } catch (error) {
      // AD-011: Log error but provide usable fallback
      const msg = error instanceof Error ? error.message : String(error);
      console.warn(`[TerminalService] Affordances lookup failed for '${path}': ${msg}`);

      // Return common affordances so completion still works
      return ['manifest', 'witness', 'refine'];
    }
  }

  /**
   * Get help text for a path or command.
   *
   * AD-011 REPL Reliability: Surfaces specific errors to help users understand what's wrong.
   * Phase 5: Includes inline examples when available (Habitat 2.0).
   */
  async help(pathOrCommand: string): Promise<string> {
    // Check if it's a built-in command
    if (BUILTIN_COMMANDS.includes(pathOrCommand as BuiltinCommand)) {
      return this._getBuiltinHelp(pathOrCommand as BuiltinCommand);
    }

    // Use gateway manifest endpoint (AD-009)
    // Manifest includes affordances and acts as path resolution
    try {
      const pathSegments = pathOrCommand.replace(/\./g, '/');
      const response = await apiClient.get<{
        path: string;
        aspect: string;
        result: Record<string, unknown>;
        error?: string;
      }>(`/agentese/${pathSegments}/manifest`, {
        headers: {
          'X-Observer-Archetype': this._observer?.archetype ?? 'developer',
        },
      });

      // AD-011: Check for error in response envelope
      if (response.data.error) {
        return `Path '${pathOrCommand}' exists but returned error:\n${response.data.error}`;
      }

      const { path } = response.data;
      const context = path.split('.')[0] || 'unknown';

      // Get affordances separately for help display
      const affords = await this.affordances(pathOrCommand);

      const helpLines = [
        `Path: ${path}`,
        `Context: ${context}`,
        `Affordances: ${affords.join(', ') || 'none'}`,
      ];

      // Phase 5 (Habitat 2.0): Try to get examples from metadata
      const pathInfo = await this._getPathMetadata(path);
      if (pathInfo?.examples && pathInfo.examples.length > 0) {
        helpLines.push('');
        helpLines.push('Examples:');
        for (const ex of pathInfo.examples.slice(0, 3)) {
          const label = ex.label || `Try ${ex.aspect}`;
          const cmd = this._formatExampleCommand(path, ex);
          helpLines.push(`  ${cmd}`);
          helpLines.push(`    ${label}`);
        }
      }

      return helpLines.join('\n');
    } catch (error) {
      // Format error with actionable hints
      const msg = error instanceof Error ? error.message : String(error);

      // Classify error for better UX
      if (msg.includes('404') || msg.includes('not found')) {
        return `Path '${pathOrCommand}' not registered.\n  → Type "discover" to see available paths`;
      }
      if (msg.includes('500') || msg.includes('Internal')) {
        return `Server error for '${pathOrCommand}'.\n  → Check backend logs for details`;
      }
      if (msg.includes('Network') || msg.includes('ECONNREFUSED')) {
        return `Connection failed.\n  → Is the server running?\n  → cd impl/claude && uv run uvicorn protocols.api.app:create_app --factory`;
      }

      return `Error: ${msg}`;
    }
  }

  /**
   * Get path metadata including examples (Habitat 2.0).
   */
  private async _getPathMetadata(path: string): Promise<{
    description?: string;
    aspects?: string[];
    examples?: Array<{
      aspect: string;
      kwargs: Record<string, unknown>;
      label?: string;
    }>;
  } | null> {
    try {
      // Use cached discovery if available
      const paths = await this.discover();
      const info = paths.find((p) => p.path === path);
      if (info) {
        // PathInfo doesn't have examples yet, need to fetch from metadata
        const response = await apiClient.get<{
          paths: string[];
          metadata?: Record<
            string,
            {
              description?: string;
              aspects?: string[];
              examples?: Array<{
                aspect: string;
                kwargs: Record<string, unknown>;
                label?: string;
              }>;
            }
          >;
        }>('/agentese/discover', { params: { include_metadata: true } });
        return response.data.metadata?.[path] ?? null;
      }
      return null;
    } catch {
      return null;
    }
  }

  /**
   * Format an example as a command string.
   */
  private _formatExampleCommand(
    path: string,
    example: { aspect: string; kwargs: Record<string, unknown> }
  ): string {
    // Simple invocation for manifest
    if (example.aspect === 'manifest' && Object.keys(example.kwargs).length === 0) {
      return path;
    }
    // With aspect
    if (Object.keys(example.kwargs).length === 0) {
      return `${path}.${example.aspect}`;
    }
    // With kwargs (show as JSON inline for now)
    const kwargsStr = JSON.stringify(example.kwargs);
    return `${path}.${example.aspect} ${kwargsStr}`;
  }

  /**
   * Get tab completion suggestions.
   */
  async complete(partial: string): Promise<CompletionSuggestion[]> {
    const suggestions: CompletionSuggestion[] = [];
    const lower = partial.toLowerCase();

    // Check built-in commands
    for (const cmd of BUILTIN_COMMANDS) {
      if (cmd.startsWith(lower)) {
        suggestions.push({
          text: cmd,
          type: 'command',
          description: this._getBuiltinDescription(cmd),
        });
      }
    }

    // Check aliases
    for (const [alias, path] of Object.entries(this._aliases)) {
      if (alias.startsWith(lower)) {
        suggestions.push({
          text: alias,
          type: 'alias',
          description: `Alias for ${path}`,
        });
      }
    }

    // Check known paths
    const paths = await this.discover();
    for (const pathInfo of paths) {
      if (pathInfo.path.toLowerCase().startsWith(lower)) {
        suggestions.push({
          text: pathInfo.path,
          type: 'path',
          description: pathInfo.description,
        });
      }
    }

    // If partial looks like a path, suggest aspects
    if (partial.includes('.')) {
      const basePath = partial.split('.').slice(0, -1).join('.');
      try {
        const affords = await this.affordances(basePath);
        for (const afford of affords) {
          const fullPath = `${basePath}.${afford}`;
          if (fullPath.toLowerCase().startsWith(lower)) {
            suggestions.push({
              text: fullPath,
              type: 'aspect',
              description: `Invoke ${afford} on ${basePath}`,
            });
          }
        }
      } catch {
        // Ignore completion errors
      }
    }

    return suggestions.slice(0, 10); // Limit suggestions
  }

  /**
   * Get current aliases.
   */
  get aliases(): Record<string, string> {
    return { ...this._aliases };
  }

  /**
   * Set an alias.
   */
  setAlias(name: string, path: string): void {
    this._aliases[name] = path;
    this._saveAliases();
  }

  /**
   * Remove an alias.
   */
  removeAlias(name: string): void {
    delete this._aliases[name];
    this._saveAliases();
  }

  // ===========================================================================
  // Private Methods - Execution
  // ===========================================================================

  /**
   * Parse a built-in command from input.
   */
  private _parseBuiltinCommand(input: string): { command: BuiltinCommand; args: string[] } | null {
    const parts = input.split(/\s+/);
    const command = parts[0].toLowerCase();

    if (BUILTIN_COMMANDS.includes(command as BuiltinCommand)) {
      return {
        command: command as BuiltinCommand,
        args: parts.slice(1),
      };
    }

    return null;
  }

  /**
   * Execute a built-in command.
   */
  private async _executeBuiltin(command: BuiltinCommand, args: string[]): Promise<TerminalLine[]> {
    switch (command) {
      case 'help':
        if (args.length > 0) {
          const helpText = await this.help(args[0]);
          return [this._createLine('output', helpText)];
        }
        return this._getGeneralHelp();

      case 'clear':
        // Return special clear signal
        return [this._createLine('system', '__CLEAR__')];

      case 'history':
        return this._formatHistory(args[0] ? parseInt(args[0], 10) : 10);

      case 'alias':
        if (args.length >= 2) {
          this.setAlias(args[0], args[1]);
          return [this._createLine('info', `Alias set: ${args[0]} -> ${args[1]}`)];
        }
        return this._formatAliases();

      case 'unalias':
        if (args.length > 0) {
          this.removeAlias(args[0]);
          return [this._createLine('info', `Alias removed: ${args[0]}`)];
        }
        return [this._createLine('error', 'Usage: unalias <name>')];

      case 'save':
        if (args.length > 0) {
          const recent = this._history.slice(0, 10).map((h) => h.input);
          this.saveCollection(args[0], recent);
          return [this._createLine('info', `Collection saved: ${args[0]}`)];
        }
        return [this._createLine('error', 'Usage: save <collection-name>')];

      case 'load':
        if (args.length > 0) {
          const commands = this.loadCollection(args[0]);
          if (commands.length === 0) {
            return [this._createLine('error', `Collection not found: ${args[0]}`)];
          }
          return [
            this._createLine('info', `Collection: ${args[0]}`),
            ...commands.map((c) => this._createLine('output', `  ${c}`)),
          ];
        }
        return [this._createLine('error', 'Usage: load <collection-name>')];

      case 'collections':
        return this._formatCollections();

      case 'affordances':
        if (args.length > 0) {
          const affords = await this.affordances(args[0]);
          return [
            this._createLine('info', `Affordances for ${args[0]}:`),
            this._createLine('output', affords.join(', ') || 'none'),
          ];
        }
        return [this._createLine('error', 'Usage: affordances <path>')];

      case 'discover': {
        const paths = await this.discover(args[0]);
        return [
          this._createLine('info', `Available paths${args[0] ? ` (${args[0]})` : ''}:`),
          ...paths
            .slice(0, 20)
            .map((p) =>
              this._createLine('output', `  ${p.path}${p.description ? ` - ${p.description}` : ''}`)
            ),
          paths.length > 20
            ? this._createLine('info', `  ... and ${paths.length - 20} more`)
            : null,
        ].filter(Boolean) as TerminalLine[];
      }

      default:
        return [this._createLine('error', `Unknown command: ${command}`)];
    }
  }

  /**
   * Execute a query (? prefix).
   */
  private async _executeQuery(pattern: string): Promise<TerminalLine[]> {
    const paths = await this.discover();
    const matching = paths.filter((p) => p.path.toLowerCase().includes(pattern.toLowerCase()));

    if (matching.length === 0) {
      return [this._createLine('info', `No paths matching: ${pattern}`)];
    }

    return [
      this._createLine('info', `Paths matching "${pattern}":`),
      ...matching.slice(0, 20).map((p) => this._createLine('output', `  ${p.path}`)),
      matching.length > 20
        ? this._createLine('info', `  ... and ${matching.length - 20} more`)
        : null,
    ].filter(Boolean) as TerminalLine[];
  }

  /**
   * Execute composition (>>).
   */
  private async _executeComposition(input: string): Promise<TerminalLine[]> {
    const parts = input.split('>>').map((p) => p.trim());
    const lines: TerminalLine[] = [];

    let lastResult: unknown = undefined;

    for (const path of parts) {
      try {
        const result = await this._invokeAgentese(path, lastResult);
        lastResult = result;
        lines.push(this._createLine('info', `[${path}] OK`));
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        lines.push(this._createLine('error', `[${path}] Failed: ${errorMsg}`));
        break;
      }
    }

    // Show final result
    if (lastResult !== undefined) {
      lines.push(this._createLine('output', this._formatResult(lastResult), lastResult));
    }

    return lines;
  }

  /**
   * Execute an AGENTESE path.
   */
  private async _executeAgentese(path: string): Promise<TerminalLine[]> {
    const result = await this._invokeAgentese(path);
    return [this._createLine('output', this._formatResult(result), result)];
  }

  /**
   * Invoke AGENTESE path via gateway (AD-009).
   *
   * Uses /agentese/{path}/{aspect} instead of legacy /v1/agentese/invoke.
   * AD-011 REPL Reliability: Properly handles AgenteseResponse envelope and surfaces errors.
   *
   * Path resolution strategy:
   * 1. Check if full path exists in discovery → use manifest aspect
   * 2. Otherwise split last segment as aspect → invoke on remaining path
   *
   * Examples:
   *   "self.soul" → path="self.soul", aspect="manifest" (if self.soul is registered)
   *   "self.soul.witness" → path="self.soul", aspect="witness"
   *   "self.memory.capture" → path="self.memory", aspect="capture"
   */
  private async _invokeAgentese(path: string, input?: unknown): Promise<unknown> {
    // First, check if the full path is a registered node (should use manifest)
    const knownPaths = await this._getKnownPaths();
    const isRegisteredPath = knownPaths.has(path);

    let pathSegments: string;
    let aspect: string;

    if (isRegisteredPath) {
      // Full path is registered → use manifest aspect
      pathSegments = path.replace(/\./g, '/');
      aspect = 'manifest';
    } else {
      // Try splitting last segment as aspect
      const parts = path.split('.');
      aspect = parts.pop() || 'manifest';
      const basePath = parts.join('.');

      // Check if base path exists
      if (parts.length > 0 && knownPaths.has(basePath)) {
        pathSegments = basePath.replace(/\./g, '/');
      } else {
        // Neither full path nor base path found - try full path anyway
        // (might be a dynamic path or user error - let backend decide)
        pathSegments = path.replace(/\./g, '/');
        aspect = 'manifest';
      }
    }

    const response = await apiClient.post<{
      path: string;
      aspect: string;
      result: unknown;
      error?: string;
    }>(`/agentese/${pathSegments}/${aspect}`, input ? { input } : {}, {
      headers: {
        'X-Observer-Archetype': this._observer?.archetype ?? 'developer',
        'X-Observer-Capabilities': this._observer
          ? Array.from(this._observer.capabilities).join(',')
          : '',
      },
    });

    // AD-011: Check for error in response envelope
    if (response.data.error) {
      throw new Error(response.data.error);
    }

    return response.data.result;
  }

  // ===========================================================================
  // Private Methods - Helpers
  // ===========================================================================

  /**
   * Format error messages with actionable hints.
   * Neutral tone — clear and direct, not poetic.
   */
  private _formatError(rawMsg: string, path: string): string {
    const lowerMsg = rawMsg.toLowerCase();

    // Network errors
    if (
      lowerMsg.includes('network') ||
      lowerMsg.includes('econnrefused') ||
      lowerMsg.includes('fetch')
    ) {
      return `Connection failed.\n  → Is the server running?\n  → cd impl/claude && uv run uvicorn protocols.api.app:create_app --factory --port 8000`;
    }

    // 404 - Path not found
    if (lowerMsg.includes('404') || lowerMsg.includes('not found')) {
      return `Not found: '${path}'\n  → Type "discover" to see available paths\n  → Check that the node module is imported in gateway.py`;
    }

    // 500 - Server error
    if (lowerMsg.includes('500') || lowerMsg.includes('internal server')) {
      return `Server error: '${path}'\n  → Check the backend terminal for traceback`;
    }

    // 422 - Validation error
    if (lowerMsg.includes('422') || lowerMsg.includes('validation')) {
      return `Invalid input: '${path}'\n  → Type "help ${path}" to see expected format`;
    }

    // Timeout
    if (lowerMsg.includes('timeout')) {
      return `Timed out: '${path}'\n  → Try again or check backend logs`;
    }

    // 451 - Consent required
    if (lowerMsg.includes('451') || lowerMsg.includes('consent')) {
      return `Consent required: '${path}'\n  → This entity has refused the interaction`;
    }

    // 429 - Rate limited
    if (lowerMsg.includes('429') || lowerMsg.includes('rate')) {
      return `Rate limited.\n  → Wait before retrying`;
    }

    // Default: show raw error
    return `Error: ${rawMsg}`;
  }

  /**
   * Get known paths as a Set for O(1) lookup.
   * Uses the cached discovery data.
   */
  private async _getKnownPaths(): Promise<Set<string>> {
    // Use cached paths if available and fresh
    const paths = await this.discover();
    return new Set(paths.map((p) => p.path));
  }

  /**
   * Expand aliases in input.
   */
  private _expandAliases(input: string): string {
    let expanded = input;
    for (const [alias, path] of Object.entries(this._aliases)) {
      // Only expand at word boundaries
      const regex = new RegExp(`\\b${alias}\\b`, 'g');
      expanded = expanded.replace(regex, path);
    }
    return expanded;
  }

  /**
   * Create a terminal line.
   */
  private _createLine(type: TerminalLine['type'], content: string, data?: unknown): TerminalLine {
    return {
      id: nanoid(8),
      type,
      content,
      data,
      timestamp: new Date(),
    };
  }

  /**
   * Format a result for display.
   */
  private _formatResult(result: unknown): string {
    if (result === null || result === undefined) {
      return '(no result)';
    }

    if (typeof result === 'string') {
      return result;
    }

    try {
      return JSON.stringify(result, null, 2);
    } catch {
      return String(result);
    }
  }

  /**
   * Add entry to history.
   */
  private _addHistoryEntry(
    input: string,
    startTime: number,
    status: HistoryEntry['status'],
    result?: TerminalLine[],
    error?: string
  ): void {
    const entry: HistoryEntry = {
      id: nanoid(12),
      input,
      timestamp: new Date(),
      duration: Date.now() - startTime,
      status,
      output: result?.find((l) => l.type === 'output')?.data,
      error,
    };

    this._history.unshift(entry);
    this._history = this._history.slice(0, MAX_HISTORY);
    this._saveHistory();
  }

  // ===========================================================================
  // Private Methods - Formatting
  // ===========================================================================

  private _getGeneralHelp(): TerminalLine[] {
    return [
      this._createLine('info', 'AGENTESE Terminal - kgents OS Shell'),
      this._createLine('output', ''),
      this._createLine('output', 'Commands:'),
      this._createLine('output', '  help [path|cmd]    Show help for path or command'),
      this._createLine('output', '  clear              Clear terminal'),
      this._createLine('output', '  history [n]        Show last n history entries'),
      this._createLine('output', '  alias [name path]  Set or list aliases'),
      this._createLine('output', '  unalias <name>     Remove alias'),
      this._createLine('output', '  discover [ctx]     List available paths'),
      this._createLine('output', '  affordances <path> List affordances for path'),
      this._createLine('output', '  save <name>        Save recent commands to collection'),
      this._createLine('output', '  load <name>        Show collection commands'),
      this._createLine('output', '  collections        List saved collections'),
      this._createLine('output', ''),
      this._createLine('output', 'AGENTESE Syntax:'),
      this._createLine('output', '  path.to.node       Invoke manifest aspect'),
      this._createLine('output', '  path.aspect        Invoke specific aspect'),
      this._createLine('output', '  path >> path       Composition (pipe output)'),
      this._createLine('output', '  ?pattern           Query paths matching pattern'),
      this._createLine('output', ''),
      this._createLine('output', 'Contexts: world, self, concept, void, time'),
    ];
  }

  private _getBuiltinHelp(command: BuiltinCommand): string {
    const help: Record<BuiltinCommand, string> = {
      help: 'Show help for a path or command.\nUsage: help [path|command]',
      clear: 'Clear the terminal output.',
      history: 'Show command history.\nUsage: history [count]',
      alias: 'Set or list aliases.\nUsage: alias [name path]',
      unalias: 'Remove an alias.\nUsage: unalias <name>',
      save: 'Save recent commands to a collection.\nUsage: save <name>',
      load: 'Show commands in a collection.\nUsage: load <name>',
      collections: 'List all saved collections.',
      affordances: 'List available affordances for a path.\nUsage: affordances <path>',
      discover: 'List available AGENTESE paths.\nUsage: discover [context]',
    };
    return help[command];
  }

  private _getBuiltinDescription(command: BuiltinCommand): string {
    const desc: Record<BuiltinCommand, string> = {
      help: 'Show help',
      clear: 'Clear terminal',
      history: 'Show history',
      alias: 'Manage aliases',
      unalias: 'Remove alias',
      save: 'Save collection',
      load: 'Load collection',
      collections: 'List collections',
      affordances: 'List affordances',
      discover: 'Discover paths',
    };
    return desc[command];
  }

  private _formatHistory(limit: number): TerminalLine[] {
    const entries = this._history.slice(0, limit);
    if (entries.length === 0) {
      return [this._createLine('info', 'No history')];
    }

    return [
      this._createLine('info', `Last ${entries.length} commands:`),
      ...entries.map((e, i) =>
        this._createLine('output', `  ${entries.length - i}. ${e.input} [${e.status}]`)
      ),
    ];
  }

  private _formatAliases(): TerminalLine[] {
    const entries = Object.entries(this._aliases);
    if (entries.length === 0) {
      return [this._createLine('info', 'No aliases')];
    }

    return [
      this._createLine('info', 'Aliases:'),
      ...entries.map(([name, path]) => this._createLine('output', `  ${name} -> ${path}`)),
    ];
  }

  private _formatCollections(): TerminalLine[] {
    if (this._collections.length === 0) {
      return [this._createLine('info', 'No collections')];
    }

    return [
      this._createLine('info', 'Collections:'),
      ...this._collections.map((c) =>
        this._createLine('output', `  ${c.name} (${c.commands.length} commands)`)
      ),
    ];
  }

  /**
   * Get well-known paths as fallback when discovery fails.
   */
  private _getWellKnownPaths(context?: string): PathInfo[] {
    const allPaths: PathInfo[] = [
      // self context
      { path: 'self.soul', context: 'self', aspects: ['manifest', 'challenge', 'reflect'] },
      { path: 'self.memory', context: 'self', aspects: ['manifest', 'capture', 'ghost'] },
      { path: 'self.garden', context: 'self', aspects: ['manifest', 'nurture', 'season'] },
      // world context
      { path: 'world.town', context: 'world', aspects: ['manifest', 'step', 'citizens'] },
      { path: 'world.park', context: 'world', aspects: ['manifest', 'scenario.start'] },
      { path: 'world.codebase', context: 'world', aspects: ['manifest', 'health', 'topology'] },
      // concept context
      { path: 'concept.gardener', context: 'concept', aspects: ['manifest', 'start', 'advance'] },
      // void context
      { path: 'void.entropy', context: 'void', aspects: ['sip', 'tithe'] },
      // time context
      { path: 'time.forest', context: 'time', aspects: ['manifest', 'status'] },
    ];

    return context ? allPaths.filter((p) => p.context === context) : allPaths;
  }

  // ===========================================================================
  // Private Methods - Persistence
  // ===========================================================================

  private _loadFromStorage(): void {
    if (typeof window === 'undefined') return;

    try {
      // Load history
      const historyJson = localStorage.getItem(STORAGE_KEYS.history);
      if (historyJson) {
        const parsed = JSON.parse(historyJson);
        this._history = parsed.map((h: HistoryEntry) => ({
          ...h,
          timestamp: new Date(h.timestamp),
        }));
      }

      // Load collections
      const collectionsJson = localStorage.getItem(STORAGE_KEYS.collections);
      if (collectionsJson) {
        const parsed = JSON.parse(collectionsJson);
        this._collections = parsed.map((c: TerminalCollection) => ({
          ...c,
          createdAt: new Date(c.createdAt),
          updatedAt: new Date(c.updatedAt),
        }));
      }

      // Load aliases
      const aliasesJson = localStorage.getItem(STORAGE_KEYS.aliases);
      if (aliasesJson) {
        this._aliases = { ...DEFAULT_ALIASES, ...JSON.parse(aliasesJson) };
      }
    } catch (error) {
      console.warn('[TerminalService] Failed to load from storage:', error);
    }
  }

  /**
   * Check if an error is a quota exceeded error.
   */
  private _isQuotaExceeded(error: unknown): boolean {
    if (error instanceof DOMException) {
      // Check the error name (standard)
      if (error.name === 'QuotaExceededError') return true;
      // Check the error code (legacy)
      if (error.code === 22) return true;
      // NS_ERROR_DOM_QUOTA_REACHED in Firefox
      if (error.name === 'NS_ERROR_DOM_QUOTA_REACHED') return true;
    }
    return false;
  }

  /**
   * Prune history to reduce storage size.
   * Removes older entries, keeping the most recent MIN_HISTORY_AFTER_PRUNE.
   */
  private _pruneHistory(): boolean {
    const originalLength = this._history.length;
    if (originalLength <= MIN_HISTORY_AFTER_PRUNE) {
      return false; // Nothing to prune
    }

    // Keep only the most recent entries
    this._history = this._history.slice(0, MIN_HISTORY_AFTER_PRUNE);
    console.info(
      `[TerminalService] Pruned history: ${originalLength} -> ${this._history.length} entries`
    );
    return true;
  }

  /**
   * Prune collections to reduce storage size.
   * Removes oldest collections based on updatedAt.
   */
  private _pruneCollections(): boolean {
    const originalLength = this._collections.length;
    if (originalLength <= 5) {
      return false; // Keep at least 5 collections
    }

    // Sort by updatedAt (oldest first) and keep only the most recent half
    this._collections.sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime());
    this._collections = this._collections.slice(0, Math.ceil(originalLength / 2));
    console.info(
      `[TerminalService] Pruned collections: ${originalLength} -> ${this._collections.length}`
    );
    return true;
  }

  /**
   * Safe localStorage setter with quota handling.
   * Attempts to save, and if quota is exceeded, prunes data and retries.
   *
   * @param key - Storage key
   * @param value - Value to store
   * @param pruneCallback - Callback to prune data if quota exceeded
   * @returns true if saved successfully, false otherwise
   */
  private _safeSetItem(key: string, value: string, pruneCallback?: () => boolean): boolean {
    if (typeof window === 'undefined') return false;

    try {
      localStorage.setItem(key, value);
      return true;
    } catch (error) {
      if (this._isQuotaExceeded(error)) {
        console.warn(`[TerminalService] Storage quota exceeded for ${key}, attempting to prune`);

        // Try pruning if callback provided
        if (pruneCallback && pruneCallback()) {
          // Retry save after pruning
          try {
            const prunedValue =
              key === STORAGE_KEYS.history
                ? JSON.stringify(this._history)
                : key === STORAGE_KEYS.collections
                  ? JSON.stringify(this._collections)
                  : value;
            localStorage.setItem(key, prunedValue);
            return true;
          } catch (retryError) {
            console.warn(`[TerminalService] Save failed after pruning ${key}:`, retryError);
            return false;
          }
        }

        // If no prune callback or pruning didn't help, try removing the item entirely
        try {
          localStorage.removeItem(key);
          console.warn(`[TerminalService] Removed ${key} due to quota constraints`);
        } catch {
          // Ignore removal errors
        }
        return false;
      }

      console.warn(`[TerminalService] Failed to save ${key}:`, error);
      return false;
    }
  }

  private _saveHistory(): void {
    if (typeof window === 'undefined') return;

    this._safeSetItem(STORAGE_KEYS.history, JSON.stringify(this._history), () =>
      this._pruneHistory()
    );
  }

  private _saveCollections(): void {
    if (typeof window === 'undefined') return;

    // Enforce max collections limit
    if (this._collections.length > MAX_COLLECTIONS) {
      this._collections.sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime());
      this._collections = this._collections.slice(0, MAX_COLLECTIONS);
    }

    this._safeSetItem(STORAGE_KEYS.collections, JSON.stringify(this._collections), () =>
      this._pruneCollections()
    );
  }

  private _saveAliases(): void {
    if (typeof window === 'undefined') return;

    // Only save non-default aliases
    const custom: Record<string, string> = {};
    for (const [name, path] of Object.entries(this._aliases)) {
      if (DEFAULT_ALIASES[name] !== path) {
        custom[name] = path;
      }
    }

    // Aliases are small, no pruning needed
    this._safeSetItem(STORAGE_KEYS.aliases, JSON.stringify(custom));
  }
}

// =============================================================================
// Factory Function
// =============================================================================

/**
 * Create a new TerminalService instance.
 *
 * @example
 * ```typescript
 * const service = createTerminalService();
 * const lines = await service.execute('self.memory.manifest');
 * ```
 */
export function createTerminalService(): TerminalService {
  return new TerminalService();
}

// Singleton instance for shared use
let _sharedInstance: TerminalService | null = null;

/**
 * Get the shared TerminalService instance.
 * Creates one if it doesn't exist.
 */
export function getTerminalService(): TerminalService {
  if (!_sharedInstance) {
    _sharedInstance = new TerminalService();
  }
  return _sharedInstance;
}
