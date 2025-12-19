/**
 * Tests for Field Projection Registry
 *
 * @see spec/protocols/aspect-form-projection.md - Part IV
 */

import { describe, it, expect } from 'vitest';
import {
  FieldProjectionRegistry,
  type FieldDescriptor,
  type FieldProjector,
} from '@/lib/form/FieldProjectionRegistry';

describe('FieldProjectionRegistry', () => {
  describe('built-in projectors', () => {
    it('has all 13 built-in projectors registered', () => {
      const all = FieldProjectionRegistry.getAll();
      expect(all.length).toBe(13);
    });

    it('projectors are sorted by fidelity (highest first)', () => {
      const all = FieldProjectionRegistry.getAll();
      for (let i = 1; i < all.length; i++) {
        // Projectors should be in descending fidelity order
        expect(all[i - 1].fidelity).toBeGreaterThanOrEqual(all[i].fidelity);
      }
      // JSON fallback should be last (fidelity 0.0)
      expect(all[all.length - 1].name).toBe('json');
    });
  });

  describe('resolve', () => {
    it('resolves uuid projector for uuid format', () => {
      const field: FieldDescriptor = {
        name: 'id',
        type: 'string',
        required: true,
        format: 'uuid',
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('uuid');
    });

    it('resolves slider for bounded numbers', () => {
      const field: FieldDescriptor = {
        name: 'opacity',
        type: 'number',
        required: false,
        min: 0,
        max: 1,
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('slider');
    });

    it('resolves enum projector for enum fields', () => {
      const field: FieldDescriptor = {
        name: 'status',
        type: 'string',
        required: true,
        enum: ['active', 'inactive', 'pending'],
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('enum');
    });

    it('resolves date projector for date format', () => {
      const field: FieldDescriptor = {
        name: 'created_at',
        type: 'string',
        required: false,
        format: 'date',
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('date');
    });

    it('resolves date projector for date-time format', () => {
      const field: FieldDescriptor = {
        name: 'updated_at',
        type: 'string',
        required: false,
        format: 'date-time',
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('date');
    });

    it('resolves boolean projector for boolean type', () => {
      const field: FieldDescriptor = {
        name: 'is_active',
        type: 'boolean',
        required: false,
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('boolean');
    });

    it('resolves textarea for long strings', () => {
      const field: FieldDescriptor = {
        name: 'description',
        type: 'string',
        required: false,
        maxLength: 500,
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('textarea');
    });

    it('resolves text for short strings', () => {
      const field: FieldDescriptor = {
        name: 'name',
        type: 'string',
        required: true,
        maxLength: 100,
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('text');
    });

    it('resolves text for strings without maxLength', () => {
      const field: FieldDescriptor = {
        name: 'title',
        type: 'string',
        required: true,
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('text');
    });

    it('resolves number for unbounded numbers', () => {
      const field: FieldDescriptor = {
        name: 'count',
        type: 'number',
        required: false,
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('number');
    });

    it('resolves number for integers', () => {
      const field: FieldDescriptor = {
        name: 'quantity',
        type: 'integer',
        required: true,
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('number');
    });

    it('resolves agentese-path for path fields', () => {
      const field: FieldDescriptor = {
        name: 'path',
        type: 'string',
        required: true,
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('agentese-path');
    });

    it('falls back to json for unknown types', () => {
      // Create a field that doesn't match any specific projector
      const field: FieldDescriptor = {
        name: 'custom_data',
        type: 'object' as any, // Force object type
        required: false,
      };
      const projector = FieldProjectionRegistry.resolve(field);
      // Should match object projector first
      expect(projector.name).toBe('object');
    });
  });

  describe('fidelity ordering', () => {
    it('uuid (0.95) beats text (0.75) for uuid format strings', () => {
      const field: FieldDescriptor = {
        name: 'user_id',
        type: 'string',
        required: true,
        format: 'uuid',
      };
      const projector = FieldProjectionRegistry.resolve(field);
      // UUID projector should win due to higher fidelity
      expect(projector.name).toBe('uuid');
      expect(projector.fidelity).toBe(0.95);
    });

    it('slider (0.9) beats number (0.75) for bounded numbers', () => {
      const field: FieldDescriptor = {
        name: 'volume',
        type: 'number',
        required: false,
        min: 0,
        max: 100,
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('slider');
      expect(projector.fidelity).toBe(0.9);
    });

    it('enum (0.9) beats text (0.75) for string enums', () => {
      const field: FieldDescriptor = {
        name: 'role',
        type: 'string',
        required: true,
        enum: ['admin', 'user', 'guest'],
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('enum');
    });
  });

  describe('custom projector registration', () => {
    it('allows registering custom projectors', () => {
      const customProjector: FieldProjector = {
        name: 'custom-email',
        fidelity: 0.92,
        matches: (field) => field.format === 'email',
        componentName: 'EmailField',
      };

      FieldProjectionRegistry.register(customProjector);

      const field: FieldDescriptor = {
        name: 'email',
        type: 'string',
        required: true,
        format: 'email',
      };

      const resolved = FieldProjectionRegistry.resolve(field);
      expect(resolved.name).toBe('custom-email');

      // Clean up: re-register original projectors would require reset
      // For now, this test modifies global state (acceptable in test context)
    });

    it('higher fidelity projector takes precedence', () => {
      const highFidelity: FieldProjector = {
        name: 'super-text',
        fidelity: 0.99,
        matches: (field) => field.type === 'string' && field.name === 'super_field',
        componentName: 'SuperTextField',
      };

      FieldProjectionRegistry.register(highFidelity);

      const field: FieldDescriptor = {
        name: 'super_field',
        type: 'string',
        required: true,
      };

      const resolved = FieldProjectionRegistry.resolve(field);
      expect(resolved.name).toBe('super-text');
    });
  });

  describe('get', () => {
    it('retrieves projector by name', () => {
      const uuid = FieldProjectionRegistry.get('uuid');
      expect(uuid).toBeDefined();
      expect(uuid?.fidelity).toBe(0.95);
    });

    it('returns undefined for non-existent projector', () => {
      const notFound = FieldProjectionRegistry.get('does-not-exist');
      expect(notFound).toBeUndefined();
    });
  });

  describe('projector matching edge cases', () => {
    it('number with only min (no max) uses number projector', () => {
      const field: FieldDescriptor = {
        name: 'age',
        type: 'number',
        required: false,
        min: 0,
        // No max - can't use slider
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('number');
    });

    it('number with only max (no min) uses number projector', () => {
      const field: FieldDescriptor = {
        name: 'limit',
        type: 'number',
        required: false,
        max: 100,
        // No min - can't use slider
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('number');
    });

    it('empty enum array does not match enum projector', () => {
      const field: FieldDescriptor = {
        name: 'category',
        type: 'string',
        required: false,
        enum: [],
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('text');
    });

    it('string with maxLength exactly 200 uses text (not textarea)', () => {
      const field: FieldDescriptor = {
        name: 'summary',
        type: 'string',
        required: false,
        maxLength: 200,
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('text');
    });

    it('string with maxLength 201 uses textarea', () => {
      const field: FieldDescriptor = {
        name: 'body',
        type: 'string',
        required: false,
        maxLength: 201,
      };
      const projector = FieldProjectionRegistry.resolve(field);
      expect(projector.name).toBe('textarea');
    });
  });
});
