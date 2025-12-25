/**
 * Tests for AGENTESE path parsing utilities
 *
 * @see spec/protocols/projection-web.md
 */

import { describe, it, expect } from 'vitest';
import {
  parseAgentesePath,
  formatAgentesePath,
  isAgentesePath,
  getHolon,
  getEntityId,
  getParentPath,
  formatPathLabel,
  matchPathPattern,
  AGENTESE_CONTEXTS,
} from '@/utils/parseAgentesePath';

describe('parseAgentesePath', () => {
  describe('valid paths', () => {
    it('parses basic context.entity path', () => {
      const result = parseAgentesePath('/world.town');
      expect(result.isValid).toBe(true);
      expect(result.path).toBe('world.town');
      expect(result.context).toBe('world');
      expect(result.aspect).toBe('manifest');
      expect(result.params).toEqual({});
    });

    it('parses path with entity ID', () => {
      const result = parseAgentesePath('/world.town.citizen.kent_001');
      expect(result.isValid).toBe(true);
      expect(result.path).toBe('world.town.citizen.kent_001');
      expect(result.context).toBe('world');
    });

    it('parses path with aspect', () => {
      const result = parseAgentesePath('/world.town.citizen.kent_001:polynomial');
      expect(result.isValid).toBe(true);
      expect(result.path).toBe('world.town.citizen.kent_001');
      expect(result.aspect).toBe('polynomial');
    });

    it('parses path with query params', () => {
      const result = parseAgentesePath('/time.differance.recent?limit=20&jewel=brain');
      expect(result.isValid).toBe(true);
      expect(result.path).toBe('time.differance.recent');
      expect(result.params).toEqual({ limit: '20', jewel: 'brain' });
    });

    it('parses path with aspect and params', () => {
      const result = parseAgentesePath('/self.memory:search?query=test&limit=10');
      expect(result.isValid).toBe(true);
      expect(result.path).toBe('self.memory');
      expect(result.aspect).toBe('search');
      expect(result.params).toEqual({ query: 'test', limit: '10' });
    });

    it('handles all five contexts', () => {
      for (const ctx of AGENTESE_CONTEXTS) {
        const result = parseAgentesePath(`/${ctx}.test`);
        expect(result.isValid).toBe(true);
        expect(result.context).toBe(ctx);
      }
    });

    it('handles path without leading slash', () => {
      const result = parseAgentesePath('world.town');
      expect(result.isValid).toBe(true);
      expect(result.path).toBe('world.town');
    });
  });

  describe('invalid paths', () => {
    it('rejects reserved prefixes', () => {
      expect(parseAgentesePath('/_api/test').isValid).toBe(false);
      expect(parseAgentesePath('/api/test').isValid).toBe(false);
      expect(parseAgentesePath('/static/foo').isValid).toBe(false);
    });

    it('rejects invalid contexts', () => {
      const result = parseAgentesePath('/invalid.context.test');
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('Invalid context');
    });

    it('rejects uppercase segments', () => {
      const result = parseAgentesePath('/world.Town.citizen');
      expect(result.isValid).toBe(false);
      expect(result.error).toContain('Invalid segment');
    });

    it('rejects empty path', () => {
      const result = parseAgentesePath('/');
      expect(result.isValid).toBe(false);
    });
  });
});

describe('formatAgentesePath', () => {
  it('formats basic path', () => {
    expect(formatAgentesePath('world.town')).toBe('/world.town');
  });

  it('omits default manifest aspect', () => {
    expect(formatAgentesePath('world.town', 'manifest')).toBe('/world.town');
  });

  it('includes non-default aspect', () => {
    expect(formatAgentesePath('world.town', 'polynomial')).toBe('/world.town:polynomial');
  });

  it('includes query params', () => {
    expect(formatAgentesePath('time.differance.recent', 'manifest', { limit: '20' })).toBe(
      '/time.differance.recent?limit=20'
    );
  });

  it('includes aspect and params together', () => {
    expect(formatAgentesePath('self.memory', 'search', { query: 'test' })).toBe(
      '/self.memory:search?query=test'
    );
  });
});

describe('isAgentesePath', () => {
  it('returns true for valid paths', () => {
    expect(isAgentesePath('/world.town')).toBe(true);
    expect(isAgentesePath('/self.memory.crystal.abc123')).toBe(true);
    expect(isAgentesePath('/time.differance:recent')).toBe(true);
  });

  it('returns false for invalid paths', () => {
    expect(isAgentesePath('/_api/test')).toBe(false);
    expect(isAgentesePath('/Invalid.Path')).toBe(false);
    expect(isAgentesePath('/notacontext.test')).toBe(false);
  });
});

describe('getHolon', () => {
  it('extracts holon from path', () => {
    expect(getHolon('world.town.citizen')).toBe('town');
    expect(getHolon('self.memory.crystal')).toBe('memory');
    expect(getHolon('concept.gardener')).toBe('gardener');
  });

  it('returns null for context-only path', () => {
    expect(getHolon('world')).toBe(null);
  });
});

describe('getEntityId', () => {
  it('extracts entity ID from path', () => {
    expect(getEntityId('world.town.citizen.kent_001')).toBe('kent_001');
    expect(getEntityId('self.memory.crystal.crystal_abc123')).toBe('crystal_abc123');
  });

  it('returns null when no entity ID', () => {
    expect(getEntityId('world.town.citizen')).toBe(null);
    expect(getEntityId('self.memory')).toBe(null);
  });
});

describe('getParentPath', () => {
  it('returns parent path', () => {
    expect(getParentPath('world.town.citizen.kent_001')).toBe('world.town.citizen');
    expect(getParentPath('world.town.citizen')).toBe('world.town');
    expect(getParentPath('world.town')).toBe('world');
  });

  it('returns null for context-only path', () => {
    expect(getParentPath('world')).toBe(null);
  });
});

describe('formatPathLabel', () => {
  it('formats last segment with capitalization', () => {
    expect(formatPathLabel('world.town.citizen')).toBe('Citizen');
    expect(formatPathLabel('self.memory')).toBe('Memory');
  });

  it('removes entity ID suffix', () => {
    expect(formatPathLabel('world.town.citizen.kent_001')).toBe('Kent');
  });
});

describe('matchPathPattern', () => {
  describe('exact patterns', () => {
    it('matches identical paths', () => {
      expect(matchPathPattern('world.town', 'world.town')).toBe(true);
    });

    it('rejects longer paths (no implicit children matching)', () => {
      expect(matchPathPattern('world.town', 'world.town.citizen')).toBe(false);
    });

    it('rejects shorter paths', () => {
      expect(matchPathPattern('world.town.citizen', 'world.town')).toBe(false);
    });
  });

  describe('single wildcard (*) - matches exactly ONE segment', () => {
    it('matches direct children', () => {
      expect(matchPathPattern('world.town.*', 'world.town.citizen')).toBe(true);
      expect(matchPathPattern('world.*', 'world.town')).toBe(true);
    });

    it('rejects grandchildren (more than one level deep)', () => {
      expect(matchPathPattern('world.town.*', 'world.town.citizen.kent_001')).toBe(false);
      expect(matchPathPattern('world.*', 'world.town.citizen')).toBe(false);
    });

    it('rejects same-level paths (no additional segment)', () => {
      expect(matchPathPattern('world.town.*', 'world.town')).toBe(false);
    });
  });

  describe('double wildcard (**) - matches any depth', () => {
    it('matches direct children', () => {
      expect(matchPathPattern('world.town.**', 'world.town.citizen')).toBe(true);
    });

    it('matches grandchildren and beyond', () => {
      expect(matchPathPattern('world.town.**', 'world.town.citizen.kent_001')).toBe(true);
      expect(matchPathPattern('world.**', 'world.town.citizen.kent_001')).toBe(true);
    });
  });

  describe('non-matching paths', () => {
    it('rejects different contexts', () => {
      expect(matchPathPattern('self.*', 'world.town')).toBe(false);
    });

    it('rejects different intermediate segments', () => {
      expect(matchPathPattern('world.town.citizen.*', 'world.town.coalition')).toBe(false);
    });
  });
});

describe('roundtrip', () => {
  it('format then parse produces equivalent result', () => {
    const original = {
      path: 'world.town.citizen.kent_001',
      aspect: 'polynomial',
      params: { include: 'graph' },
    };

    const url = formatAgentesePath(original.path, original.aspect, original.params);
    const parsed = parseAgentesePath(url);

    expect(parsed.path).toBe(original.path);
    expect(parsed.aspect).toBe(original.aspect);
    expect(parsed.params).toEqual(original.params);
  });
});
