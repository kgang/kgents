/**
 * Tests for Contract Schema Analysis
 *
 * @see spec/protocols/aspect-form-projection.md - Part VI
 */

import { describe, it, expect, beforeEach } from 'vitest';
import {
  analyzeContract,
  analyzeContractCached,
  clearSchemaCache,
  getCacheKey,
  hasRequiredFields,
  getRequiredFieldNames,
  isAdvancedField,
  type JSONSchema,
} from '@/lib/schema/analyzeContract';

describe('analyzeContract', () => {
  describe('basic schema analysis', () => {
    it('extracts fields from object schema', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: {
          name: { type: 'string' },
          age: { type: 'number' },
        },
      };

      // Use developer archetype to see all fields (guest filters to essential only)
      const fields = analyzeContract(schema, { archetype: 'developer' });

      expect(fields).toHaveLength(2);
      expect(fields.find((f) => f.name === 'name')?.type).toBe('string');
      expect(fields.find((f) => f.name === 'age')?.type).toBe('number');
    });

    it('marks required fields correctly', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: {
          name: { type: 'string' },
          email: { type: 'string' },
          nickname: { type: 'string' },
        },
        required: ['name', 'email'],
      };

      const fields = analyzeContract(schema, { archetype: 'developer' });

      expect(fields.find((f) => f.name === 'name')?.required).toBe(true);
      expect(fields.find((f) => f.name === 'email')?.required).toBe(true);
      expect(fields.find((f) => f.name === 'nickname')?.required).toBe(false);
    });

    it('extracts field metadata', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: {
          status: {
            type: 'string',
            description: 'Current status',
            default: 'active',
            enum: ['active', 'inactive'],
          },
        },
      };

      const fields = analyzeContract(schema, { archetype: 'developer' });
      const statusField = fields.find((f) => f.name === 'status');

      expect(statusField?.description).toBe('Current status');
      expect(statusField?.default).toBe('active');
      expect(statusField?.enum).toEqual(['active', 'inactive']);
    });

    it('extracts string constraints', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: {
          username: {
            type: 'string',
            minLength: 3,
            maxLength: 50,
            pattern: '^[a-z0-9_]+$',
          },
        },
      };

      const fields = analyzeContract(schema, { archetype: 'developer' });
      const field = fields.find((f) => f.name === 'username');

      expect(field?.minLength).toBe(3);
      expect(field?.maxLength).toBe(50);
      expect(field?.pattern).toBe('^[a-z0-9_]+$');
    });

    it('extracts number constraints', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: {
          age: {
            type: 'integer',
            minimum: 0,
            maximum: 150,
          },
        },
      };

      const fields = analyzeContract(schema, { archetype: 'developer' });
      const field = fields.find((f) => f.name === 'age');

      expect(field?.type).toBe('integer');
      expect(field?.min).toBe(0);
      expect(field?.max).toBe(150);
    });

    it('handles exclusive min/max', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: {
          rate: {
            type: 'number',
            exclusiveMinimum: 0,
            exclusiveMaximum: 1,
          },
        },
      };

      const fields = analyzeContract(schema, { archetype: 'developer' });
      const field = fields.find((f) => f.name === 'rate');

      expect(field?.min).toBe(1); // exclusiveMinimum + 1
      expect(field?.max).toBe(0); // exclusiveMaximum - 1
    });

    it('extracts format hints', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' },
          email: { type: 'string', format: 'email' },
          created: { type: 'string', format: 'date-time' },
        },
      };

      const fields = analyzeContract(schema, { archetype: 'developer' });

      expect(fields.find((f) => f.name === 'id')?.format).toBe('uuid');
      expect(fields.find((f) => f.name === 'email')?.format).toBe('email');
      expect(fields.find((f) => f.name === 'created')?.format).toBe('date-time');
    });
  });

  describe('nested objects', () => {
    it('handles nested object properties', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: {
          address: {
            type: 'object',
            properties: {
              street: { type: 'string' },
              city: { type: 'string' },
              zip: { type: 'string' },
            },
            required: ['city'],
          },
        },
      };

      const fields = analyzeContract(schema, { archetype: 'developer' });
      const addressField = fields.find((f) => f.name === 'address');

      expect(addressField?.type).toBe('object');
      expect(addressField?.children).toHaveLength(3);
      expect(addressField?.children?.find((c) => c.name === 'city')?.required).toBe(true);
      expect(addressField?.children?.find((c) => c.name === 'street')?.required).toBe(false);
    });

    it('builds context path for nested fields', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: {
          user: {
            type: 'object',
            properties: {
              name: { type: 'string' },
            },
          },
        },
      };

      const fields = analyzeContract(schema, {
        archetype: 'developer',
        pathContext: ['world', 'citizen'],
      });

      const userField = fields.find((f) => f.name === 'user');
      expect(userField?.context).toEqual(['world', 'citizen', 'user']);

      const nameField = userField?.children?.find((c) => c.name === 'name');
      expect(nameField?.context).toEqual(['world', 'citizen', 'user', 'name']);
    });
  });

  describe('arrays', () => {
    it('handles array with items schema', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: {
          tags: {
            type: 'array',
            items: { type: 'string' },
          },
        },
      };

      const fields = analyzeContract(schema, { archetype: 'developer' });
      const tagsField = fields.find((f) => f.name === 'tags');

      expect(tagsField?.type).toBe('array');
      expect(tagsField?.items?.type).toBe('string');
    });
  });

  describe('archetype filtering', () => {
    const schema: JSONSchema = {
      type: 'object',
      properties: {
        name: { type: 'string' },
        description: { type: 'string' },
        id: { type: 'string', format: 'uuid' },
        created_at: { type: 'string', format: 'date-time' },
        tenant_id: { type: 'string' },
        internal_notes: { type: 'string' },
      },
    };

    it('guest sees only essential fields', () => {
      const fields = analyzeContract(schema, { archetype: 'guest' });

      expect(fields.map((f) => f.name)).toContain('name');
      expect(fields.map((f) => f.name)).toContain('description');
      expect(fields.map((f) => f.name)).not.toContain('id');
      expect(fields.map((f) => f.name)).not.toContain('created_at');
      expect(fields.map((f) => f.name)).not.toContain('tenant_id');
    });

    it('developer sees all fields', () => {
      const fields = analyzeContract(schema, { archetype: 'developer' });

      expect(fields).toHaveLength(6);
      expect(fields.map((f) => f.name)).toContain('id');
      expect(fields.map((f) => f.name)).toContain('created_at');
      expect(fields.map((f) => f.name)).toContain('tenant_id');
    });

    it('admin sees all fields', () => {
      const fields = analyzeContract(schema, { archetype: 'admin' });

      expect(fields).toHaveLength(6);
    });

    it('creator sees creative fields but not technical', () => {
      const fields = analyzeContract(schema, { archetype: 'creator' });

      expect(fields.map((f) => f.name)).toContain('name');
      expect(fields.map((f) => f.name)).toContain('description');
      expect(fields.map((f) => f.name)).not.toContain('id');
      expect(fields.map((f) => f.name)).not.toContain('tenant_id');
    });
  });

  describe('custom visibility', () => {
    it('allows custom visibility rules per archetype', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: {
          name: { type: 'string' },
          secret: { type: 'string' },
          public: { type: 'string' },
        },
      };

      const fields = analyzeContract(schema, {
        archetype: 'guest',
        visibility: {
          guest: ['name', 'public'],
        },
      });

      expect(fields.map((f) => f.name)).toContain('name');
      expect(fields.map((f) => f.name)).toContain('public');
      expect(fields.map((f) => f.name)).not.toContain('secret');
    });
  });

  describe('composition flattening', () => {
    it('flattens allOf schemas', () => {
      const schema: JSONSchema = {
        allOf: [
          {
            type: 'object',
            properties: { name: { type: 'string' } },
            required: ['name'],
          },
          {
            properties: { email: { type: 'string' } },
          },
        ],
      };

      const fields = analyzeContract(schema, { archetype: 'developer' });

      expect(fields).toHaveLength(2);
      expect(fields.find((f) => f.name === 'name')?.required).toBe(true);
    });
  });

  describe('edge cases', () => {
    it('handles null schema', () => {
      const fields = analyzeContract(null as any);
      expect(fields).toEqual([]);
    });

    it('handles undefined schema', () => {
      const fields = analyzeContract(undefined as any);
      expect(fields).toEqual([]);
    });

    it('handles empty object schema', () => {
      const schema: JSONSchema = { type: 'object', properties: {} };
      const fields = analyzeContract(schema);
      expect(fields).toEqual([]);
    });

    it('handles primitive schema (wraps as single field)', () => {
      const schema: JSONSchema = { type: 'string' };
      const fields = analyzeContract(schema);

      expect(fields).toHaveLength(1);
      expect(fields[0].name).toBe('value');
      expect(fields[0].type).toBe('string');
    });

    it('normalizes array type to first element', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: {
          nullable_string: { type: ['string', 'null'] as any },
        },
      };

      const fields = analyzeContract(schema, { archetype: 'developer' });
      expect(fields[0].type).toBe('string');
    });
  });
});

describe('utility functions', () => {
  describe('hasRequiredFields', () => {
    it('returns true when schema has required fields', () => {
      const schema: JSONSchema = { required: ['name', 'email'] };
      expect(hasRequiredFields(schema)).toBe(true);
    });

    it('returns false when no required fields', () => {
      const schema: JSONSchema = { type: 'object' };
      expect(hasRequiredFields(schema)).toBe(false);
    });

    it('returns false for empty required array', () => {
      const schema: JSONSchema = { required: [] };
      expect(hasRequiredFields(schema)).toBe(false);
    });
  });

  describe('getRequiredFieldNames', () => {
    it('returns required field names', () => {
      const schema: JSONSchema = { required: ['name', 'email'] };
      expect(getRequiredFieldNames(schema)).toEqual(['name', 'email']);
    });

    it('returns empty array when no required', () => {
      const schema: JSONSchema = { type: 'object' };
      expect(getRequiredFieldNames(schema)).toEqual([]);
    });
  });

  describe('isAdvancedField', () => {
    it('identifies technical fields', () => {
      expect(isAdvancedField('id')).toBe(true);
      expect(isAdvancedField('uuid')).toBe(true);
      expect(isAdvancedField('created_at')).toBe(true);
      expect(isAdvancedField('tenant_id')).toBe(true);
      expect(isAdvancedField('_internal')).toBe(true);
    });

    it('does not flag normal fields', () => {
      expect(isAdvancedField('name')).toBe(false);
      expect(isAdvancedField('description')).toBe(false);
      expect(isAdvancedField('email')).toBe(false);
    });
  });
});

describe('caching', () => {
  beforeEach(() => {
    clearSchemaCache();
  });

  describe('getCacheKey', () => {
    it('generates consistent cache keys', () => {
      const key1 = getCacheKey('world.town', 'create', 'guest');
      const key2 = getCacheKey('world.town', 'create', 'guest');
      expect(key1).toBe(key2);
    });

    it('different archetypes produce different keys', () => {
      const key1 = getCacheKey('world.town', 'create', 'guest');
      const key2 = getCacheKey('world.town', 'create', 'developer');
      expect(key1).not.toBe(key2);
    });
  });

  describe('analyzeContractCached', () => {
    it('returns cached result on second call', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: { name: { type: 'string' } },
      };

      const result1 = analyzeContractCached(schema, 'world.town', 'create', {
        archetype: 'developer',
      });
      const result2 = analyzeContractCached(schema, 'world.town', 'create', {
        archetype: 'developer',
      });

      // Same reference = cached
      expect(result1).toBe(result2);
    });

    it('different archetypes get different cached results', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: {
          name: { type: 'string' },
          id: { type: 'string' },
        },
      };

      const guestFields = analyzeContractCached(schema, 'world.town', 'create', {
        archetype: 'guest',
      });
      const devFields = analyzeContractCached(schema, 'world.town', 'create', {
        archetype: 'developer',
      });

      expect(guestFields.length).not.toBe(devFields.length);
    });
  });

  describe('clearSchemaCache', () => {
    it('clears cache so next call recomputes', () => {
      const schema: JSONSchema = {
        type: 'object',
        properties: { name: { type: 'string' } },
      };

      const result1 = analyzeContractCached(schema, 'world.town', 'create', {
        archetype: 'developer',
      });

      clearSchemaCache();

      const result2 = analyzeContractCached(schema, 'world.town', 'create', {
        archetype: 'developer',
      });

      // Different references after cache clear
      expect(result1).not.toBe(result2);
      // But same content
      expect(result1).toEqual(result2);
    });
  });
});
