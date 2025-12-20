/**
 * TerminalService Tests
 *
 * Tests for the Terminal service including:
 * - Command execution
 * - History management
 * - Collections
 * - Aliases
 * - Tab completion
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  TerminalService,
  createTerminalService,
  getTerminalService,
} from '@/shell/TerminalService';

// =============================================================================
// Mocks
// =============================================================================

// Mock the API client
vi.mock('@/api/client', () => ({
  apiClient: {
    post: vi.fn().mockImplementation(async (url: string, data?: unknown) => {
      if (url === '/v1/agentese/invoke') {
        const req = data as { path: string };
        return {
          data: {
            path: req.path,
            result: { mock: 'result', path: req.path },
            tokens_used: 0,
            cached: false,
          },
        };
      }
      return { data: {} };
    }),
    get: vi.fn().mockImplementation(async (url: string) => {
      if (url === '/api/agentese/discover') {
        return {
          data: {
            paths: [
              { path: 'self.memory', context: 'self', aspects: ['manifest'] },
              { path: 'self.soul', context: 'self', aspects: ['challenge'] },
              { path: 'world.town', context: 'world', aspects: ['manifest'] },
            ],
          },
        };
      }
      if (url === '/v1/agentese/resolve') {
        return {
          data: {
            path: 'self.memory',
            handle: 'memory',
            context: 'self',
            affordances: ['manifest', 'capture', 'ghost'],
          },
        };
      }
      // Handle /agentese/{path}/affordances pattern (AD-009 gateway)
      if (url.includes('/affordances')) {
        // Extract path from URL: /agentese/self/memory/affordances -> self.memory
        const match = url.match(/\/agentese\/(.+)\/affordances/);
        const pathFromUrl = match ? match[1].replace(/\//g, '.') : 'unknown';
        return {
          data: {
            path: pathFromUrl,
            affordances: ['manifest', 'capture', 'ghost'],
            observer_archetype: 'developer',
          },
        };
      }
      // Handle /agentese/{path}/manifest pattern for help()
      if (url.match(/\/agentese\/.+\/manifest/)) {
        const match = url.match(/\/agentese\/(.+)\/manifest/);
        const pathFromUrl = match ? match[1].replace(/\//g, '.') : 'unknown';
        return {
          data: {
            path: pathFromUrl,
            aspect: 'manifest',
            data: { description: 'Test manifest data' },
          },
        };
      }
      return { data: {} };
    }),
  },
}));

// Mock nanoid
vi.mock('nanoid', () => ({
  nanoid: vi.fn(() => 'mock-id-' + Math.random().toString(36).slice(2, 8)),
}));

// =============================================================================
// Factory Tests
// =============================================================================

describe('TerminalService factory', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('creates new instance with createTerminalService', () => {
    const service = createTerminalService();
    expect(service).toBeInstanceOf(TerminalService);
  });

  it('returns singleton with getTerminalService', () => {
    const service1 = getTerminalService();
    const service2 = getTerminalService();
    expect(service1).toBe(service2);
  });
});

// =============================================================================
// Built-in Commands Tests
// =============================================================================

describe('TerminalService built-in commands', () => {
  let service: TerminalService;

  beforeEach(() => {
    localStorage.clear();
    service = createTerminalService();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('executes help command', async () => {
    const lines = await service.execute('help');

    expect(lines.length).toBeGreaterThan(0);
    expect(lines[0].content).toBe('kg> help');
    expect(lines.some((l) => l.content.includes('Commands:'))).toBe(true);
  });

  it('executes clear command', async () => {
    const lines = await service.execute('clear');

    // Should return special clear signal
    expect(lines.some((l) => l.content === '__CLEAR__')).toBe(true);
  });

  it('executes alias command to list', async () => {
    const lines = await service.execute('alias');

    expect(lines.some((l) => l.content === 'Aliases:')).toBe(true);
    expect(lines.some((l) => l.content.includes('brain -> self.memory'))).toBe(true);
  });

  it('executes alias command to set', async () => {
    const lines = await service.execute('alias mytest self.soul.challenge');

    expect(lines.some((l) => l.content.includes('Alias set: mytest'))).toBe(true);
    expect(service.aliases.mytest).toBe('self.soul.challenge');
  });

  it('executes unalias command', async () => {
    // First set an alias
    service.setAlias('mytest', 'test.path');
    expect(service.aliases.mytest).toBe('test.path');

    // Then remove it
    const lines = await service.execute('unalias mytest');

    expect(lines.some((l) => l.content.includes('Alias removed: mytest'))).toBe(true);
    expect(service.aliases.mytest).toBeUndefined();
  });

  it('executes history command', async () => {
    // Add some history
    await service.execute('help');
    await service.execute('alias');

    const lines = await service.execute('history');

    expect(lines.some((l) => l.content.includes('Last'))).toBe(true);
  });

  it('executes discover command', async () => {
    const lines = await service.execute('discover');

    expect(lines.some((l) => l.content.includes('Available paths'))).toBe(true);
  });

  it('executes affordances command', async () => {
    const lines = await service.execute('affordances self.memory');

    expect(lines.some((l) => l.content.includes('Affordances for self.memory'))).toBe(true);
  });
});

// =============================================================================
// Query Syntax Tests
// =============================================================================

describe('TerminalService query syntax', () => {
  let service: TerminalService;

  beforeEach(() => {
    localStorage.clear();
    service = createTerminalService();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('executes query with ? prefix', async () => {
    const lines = await service.execute('?memory');

    expect(lines.some((l) => l.content.includes('Paths matching'))).toBe(true);
  });

  it('returns no results for non-matching query', async () => {
    const lines = await service.execute('?nonexistent');

    expect(lines.some((l) => l.content.includes('No paths matching'))).toBe(true);
  });
});

// =============================================================================
// AGENTESE Execution Tests
// =============================================================================

describe('TerminalService AGENTESE execution', () => {
  let service: TerminalService;

  beforeEach(() => {
    localStorage.clear();
    service = createTerminalService();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('executes AGENTESE path', async () => {
    const lines = await service.execute('self.memory.manifest');

    expect(lines.length).toBe(2); // input echo + output
    expect(lines[0].content).toBe('kg> self.memory.manifest');
    expect(lines[1].type).toBe('output');
  });

  it('expands aliases in paths', async () => {
    const lines = await service.execute('brain.manifest');

    // 'brain' should expand to 'self.memory'
    expect(lines.length).toBeGreaterThan(0);
    expect(lines[0].content).toBe('kg> brain.manifest');
  });
});

// =============================================================================
// History Tests
// =============================================================================

describe('TerminalService history', () => {
  let service: TerminalService;

  beforeEach(() => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);
    vi.mocked(localStorage.setItem).mockClear();
    service = createTerminalService();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('records history entries', async () => {
    await service.execute('help');
    await service.execute('alias');

    expect(service.history.length).toBe(2);
    expect(service.history[0].input).toBe('alias');
    expect(service.history[1].input).toBe('help');
  });

  it('limits history to MAX_HISTORY', async () => {
    // Execute many commands
    for (let i = 0; i < 110; i++) {
      await service.execute(`help`);
    }

    expect(service.history.length).toBeLessThanOrEqual(100);
  });

  it('searches history', async () => {
    await service.execute('help');
    await service.execute('alias');
    await service.execute('help topic');

    const results = service.searchHistory('help');

    expect(results.length).toBe(2);
  });

  it('clears history', async () => {
    await service.execute('help');
    await service.execute('alias');

    service.clearHistory();

    expect(service.history.length).toBe(0);
  });

  it('persists history to localStorage', async () => {
    await service.execute('help');

    // Check localStorage.setItem was called
    expect(localStorage.setItem).toHaveBeenCalledWith(
      'kgents.terminal.history',
      expect.stringContaining('help')
    );
  });

  it('loads history from localStorage', async () => {
    // Pre-populate localStorage mock
    const history = [
      {
        id: 'test-1',
        input: 'previous command',
        timestamp: new Date().toISOString(),
        duration: 50,
        status: 'success',
      },
    ];
    vi.mocked(localStorage.getItem).mockImplementation((key) => {
      if (key === 'kgents.terminal.history') {
        return JSON.stringify(history);
      }
      return null;
    });

    // Create new service
    const newService = createTerminalService();

    expect(newService.history.length).toBe(1);
    expect(newService.history[0].input).toBe('previous command');
  });
});

// =============================================================================
// Collections Tests
// =============================================================================

describe('TerminalService collections', () => {
  let service: TerminalService;

  beforeEach(() => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);
    vi.mocked(localStorage.setItem).mockClear();
    service = createTerminalService();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('saves collection', () => {
    service.saveCollection('my-collection', ['help', 'alias', 'discover']);

    expect(service.collections.length).toBe(1);
    expect(service.collections[0].name).toBe('my-collection');
    expect(service.collections[0].commands).toEqual(['help', 'alias', 'discover']);
  });

  it('loads collection', () => {
    service.saveCollection('my-collection', ['help', 'alias']);

    const commands = service.loadCollection('my-collection');

    expect(commands).toEqual(['help', 'alias']);
  });

  it('returns empty array for non-existent collection', () => {
    const commands = service.loadCollection('nonexistent');
    expect(commands).toEqual([]);
  });

  it('deletes collection', () => {
    service.saveCollection('my-collection', ['help']);
    expect(service.collections.length).toBe(1);

    service.deleteCollection('my-collection');
    expect(service.collections.length).toBe(0);
  });

  it('updates existing collection', () => {
    service.saveCollection('my-collection', ['help']);
    service.saveCollection('my-collection', ['help', 'alias']);

    expect(service.collections.length).toBe(1);
    expect(service.collections[0].commands).toEqual(['help', 'alias']);
  });

  it('persists collections to localStorage', () => {
    service.saveCollection('test', ['help']);

    // Check localStorage.setItem was called
    expect(localStorage.setItem).toHaveBeenCalledWith(
      'kgents.terminal.collections',
      expect.stringContaining('test')
    );
  });
});

// =============================================================================
// Alias Tests
// =============================================================================

describe('TerminalService aliases', () => {
  let service: TerminalService;

  beforeEach(() => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);
    vi.mocked(localStorage.setItem).mockClear();
    service = createTerminalService();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('has default aliases', () => {
    expect(service.aliases.brain).toBe('self.memory');
    expect(service.aliases.town).toBe('world.town');
  });

  it('sets custom alias', () => {
    service.setAlias('myalias', 'self.soul.challenge');
    expect(service.aliases.myalias).toBe('self.soul.challenge');
  });

  it('removes alias', () => {
    service.setAlias('myalias', 'self.soul.challenge');
    service.removeAlias('myalias');
    expect(service.aliases.myalias).toBeUndefined();
  });

  it('persists custom aliases to localStorage', () => {
    service.setAlias('myalias', 'test.path');

    // Check localStorage.setItem was called
    expect(localStorage.setItem).toHaveBeenCalledWith(
      'kgents.terminal.aliases',
      expect.stringContaining('myalias')
    );
  });

  it('does not persist default aliases', () => {
    // Trigger a save by setting and removing
    service.setAlias('temp', 'temp.path');
    service.removeAlias('temp');

    // Get the last call to setItem for aliases
    const calls = vi
      .mocked(localStorage.setItem)
      .mock.calls.filter((call) => call[0] === 'kgents.terminal.aliases');
    const lastCall = calls[calls.length - 1];

    // Should not contain default aliases (brain is a default)
    expect(lastCall?.[1]).not.toContain('"brain"');
  });
});

// =============================================================================
// Completion Tests
// =============================================================================

describe('TerminalService completion', () => {
  let service: TerminalService;

  beforeEach(() => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);
    vi.mocked(localStorage.setItem).mockClear();
    service = createTerminalService();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('suggests built-in commands', async () => {
    const suggestions = await service.complete('hel');

    expect(suggestions.some((s) => s.text === 'help' && s.type === 'command')).toBe(true);
  });

  it('suggests aliases', async () => {
    const suggestions = await service.complete('brai');

    expect(suggestions.some((s) => s.text === 'brain' && s.type === 'alias')).toBe(true);
  });

  it('suggests paths from discovery', async () => {
    const suggestions = await service.complete('self.');

    expect(suggestions.some((s) => s.type === 'path')).toBe(true);
  });

  it('limits suggestions', async () => {
    // Even with many matches, should limit
    const suggestions = await service.complete('s');

    expect(suggestions.length).toBeLessThanOrEqual(10);
  });
});

// =============================================================================
// Discovery Tests
// =============================================================================

describe('TerminalService discovery', () => {
  let service: TerminalService;

  beforeEach(() => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);
    vi.mocked(localStorage.setItem).mockClear();
    service = createTerminalService();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('discovers paths', async () => {
    const paths = await service.discover();

    expect(paths.length).toBeGreaterThan(0);
  });

  it('filters by context when API fails', async () => {
    // The mock API doesn't filter, so service falls back to well-known paths
    // when discovery fails or when context filtering is needed
    vi.mocked((await import('@/api/client')).apiClient.get).mockRejectedValueOnce(
      new Error('test')
    );

    const paths = await service.discover('self');

    // With fallback paths, all should be self context
    expect(paths.every((p) => p.context === 'self')).toBe(true);
  });

  it('caches discovery results', async () => {
    // First call
    await service.discover();

    // Second call should use cache
    const paths = await service.discover();

    expect(paths.length).toBeGreaterThan(0);
  });

  it('gets affordances for path', async () => {
    const affordances = await service.affordances('self.memory');

    expect(affordances.length).toBeGreaterThan(0);
    expect(affordances).toContain('manifest');
  });
});

// =============================================================================
// Help Tests
// =============================================================================

describe('TerminalService help', () => {
  let service: TerminalService;

  beforeEach(() => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);
    vi.mocked(localStorage.setItem).mockClear();
    service = createTerminalService();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('provides help for built-in commands', async () => {
    const helpText = await service.help('help');

    expect(helpText).toContain('Usage');
  });

  it('provides help for paths', async () => {
    const helpText = await service.help('self.memory');

    expect(helpText).toContain('Path');
    expect(helpText).toContain('self.memory');
  });
});
