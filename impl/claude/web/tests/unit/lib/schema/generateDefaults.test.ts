/**
 * Tests for Five-Source Default Generation
 *
 * @see spec/protocols/aspect-form-projection.md - Part III
 */

import { describe, it, expect } from 'vitest';
import {
  generateDefaults,
  generateDefaultsSync,
  generateUUID,
  enhanceForDeveloper,
  type Observer,
  type DefaultContext,
} from '@/lib/schema/generateDefaults';
import type { FieldDescriptor } from '@/lib/form/FieldProjectionRegistry';

// =============================================================================
// Test Fixtures
// =============================================================================

const guestObserver: Observer = {
  archetype: 'guest',
};

const creatorObserver: Observer = {
  archetype: 'creator',
  userId: 'creator_001',
};

const baseContext: DefaultContext = {
  path: 'world.town.citizen',
  aspect: 'create',
};

const editContext: DefaultContext = {
  path: 'world.town.citizen.kent_001',
  aspect: 'update',
  isEdit: true,
  entity: {
    name: 'Kent',
    email: 'kent@example.com',
    age: 30,
  },
};

const stringField: FieldDescriptor = {
  name: 'name',
  type: 'string',
  required: true,
  context: ['citizen', 'name'],
};

const numberField: FieldDescriptor = {
  name: 'count',
  type: 'number',
  required: false,
};

const booleanField: FieldDescriptor = {
  name: 'is_active',
  type: 'boolean',
  required: false,
};

const dateField: FieldDescriptor = {
  name: 'start_date',
  type: 'string',
  required: false,
  format: 'date',
};

const dateTimeField: FieldDescriptor = {
  name: 'created_at',
  type: 'string',
  required: false,
  format: 'date-time',
};

const fieldWithDefault: FieldDescriptor = {
  name: 'status',
  type: 'string',
  required: false,
  default: 'active',
};

const uuidField: FieldDescriptor = {
  name: 'id',
  type: 'string',
  required: true,
  format: 'uuid',
};

// =============================================================================
// Tests
// =============================================================================

describe('generateDefaults', () => {
  describe('Source 1: world.* (Entity Context)', () => {
    it('uses entity value when editing', async () => {
      const fields = [stringField, { ...numberField, name: 'age' }];

      const defaults = await generateDefaults(fields, guestObserver, editContext);

      expect(defaults.name).toBe('Kent');
      expect(defaults.age).toBe(30);
    });

    it('ignores entity when not editing', async () => {
      const contextWithEntity: DefaultContext = {
        ...baseContext,
        entity: { name: 'Should be ignored' },
        isEdit: false,
      };

      const defaults = await generateDefaults([stringField], guestObserver, contextWithEntity);

      expect(defaults.name).not.toBe('Should be ignored');
    });
  });

  describe('Source 3: concept.* (Schema Defaults)', () => {
    it('uses schema default value', async () => {
      const defaults = await generateDefaults([fieldWithDefault], guestObserver, baseContext);

      expect(defaults.status).toBe('active');
    });

    it('schema default takes precedence over type fallback', async () => {
      const fieldWithZeroDefault: FieldDescriptor = {
        name: 'count',
        type: 'number',
        required: false,
        default: 42,
      };

      const defaults = await generateDefaults([fieldWithZeroDefault], guestObserver, baseContext);

      expect(defaults.count).toBe(42);
    });
  });

  describe('Source 4: void.* (Entropy for Creators)', () => {
    it('provides creative name suggestions for creator archetype', async () => {
      const citizenNameField: FieldDescriptor = {
        name: 'name',
        type: 'string',
        required: true,
        context: ['citizen', 'name'],
      };

      const defaults = await generateDefaults([citizenNameField], creatorObserver, baseContext);

      // Should be a non-empty string (whimsical name from the pool)
      expect(typeof defaults.name).toBe('string');
      expect((defaults.name as string).length).toBeGreaterThan(0);
    });

    it('does NOT provide entropy for guest archetype', async () => {
      const citizenNameField: FieldDescriptor = {
        name: 'name',
        type: 'string',
        required: true,
        context: ['citizen', 'name'],
      };

      const defaults = await generateDefaults([citizenNameField], guestObserver, baseContext);

      // Should fall through to type fallback (empty string)
      expect(defaults.name).toBe('');
    });

    it('provides creative town names', async () => {
      const townNameField: FieldDescriptor = {
        name: 'name',
        type: 'string',
        required: true,
        context: ['town', 'name'],
      };

      const defaults = await generateDefaults([townNameField], creatorObserver, baseContext);

      expect(typeof defaults.name).toBe('string');
      expect((defaults.name as string).length).toBeGreaterThan(0);
    });

    it('can be skipped with skipEntropy option', async () => {
      const citizenNameField: FieldDescriptor = {
        name: 'name',
        type: 'string',
        required: true,
        context: ['citizen', 'name'],
      };

      const defaults = await generateDefaults([citizenNameField], creatorObserver, baseContext, {
        skipEntropy: true,
      });

      // Without entropy, should fall through to type fallback
      expect(defaults.name).toBe('');
    });
  });

  describe('Source 5: time.* (Temporal Defaults)', () => {
    const fixedDate = new Date('2025-12-19T12:00:00Z');

    it('provides date default for date format fields', async () => {
      const defaults = await generateDefaults([dateField], guestObserver, baseContext, {
        now: fixedDate,
      });

      expect(defaults.start_date).toBe('2025-12-19');
    });

    it('provides datetime default for date-time format fields', async () => {
      const defaults = await generateDefaults([dateTimeField], guestObserver, baseContext, {
        now: fixedDate,
      });

      expect(defaults.created_at).toBe('2025-12-19T12:00:00.000Z');
    });

    it('provides date for temporal field names', async () => {
      const dueDateField: FieldDescriptor = {
        name: 'due_date',
        type: 'string',
        required: false,
      };

      const defaults = await generateDefaults([dueDateField], guestObserver, baseContext, {
        now: fixedDate,
      });

      expect(defaults.due_date).toBe('2025-12-19');
    });
  });

  describe('Type Fallbacks', () => {
    it('provides empty string for strings', async () => {
      const defaults = await generateDefaults([stringField], guestObserver, baseContext);
      expect(defaults.name).toBe('');
    });

    it('provides 0 for numbers', async () => {
      const defaults = await generateDefaults([numberField], guestObserver, baseContext);
      expect(defaults.count).toBe(0);
    });

    it('provides false for booleans', async () => {
      const defaults = await generateDefaults([booleanField], guestObserver, baseContext);
      expect(defaults.is_active).toBe(false);
    });

    it('provides empty array for arrays', async () => {
      const arrayField: FieldDescriptor = {
        name: 'tags',
        type: 'array',
        required: false,
      };

      const defaults = await generateDefaults([arrayField], guestObserver, baseContext);
      expect(defaults.tags).toEqual([]);
    });

    it('provides empty object for objects', async () => {
      const objectField: FieldDescriptor = {
        name: 'metadata',
        type: 'object',
        required: false,
      };

      const defaults = await generateDefaults([objectField], guestObserver, baseContext);
      expect(defaults.metadata).toEqual({});
    });

    it('uses min value as fallback for bounded numbers', async () => {
      const boundedField: FieldDescriptor = {
        name: 'rating',
        type: 'number',
        required: false,
        min: 1,
        max: 5,
      };

      const defaults = await generateDefaults([boundedField], guestObserver, baseContext);
      expect(defaults.rating).toBe(1);
    });
  });

  describe('Priority Cascade', () => {
    it('entity value beats schema default', async () => {
      const fieldWithDefaultAndEntity: FieldDescriptor = {
        ...fieldWithDefault,
        name: 'name',
      };

      const contextWithName: DefaultContext = {
        ...editContext,
        entity: { name: 'FromEntity' },
      };

      const defaults = await generateDefaults(
        [fieldWithDefaultAndEntity],
        guestObserver,
        contextWithName
      );

      expect(defaults.name).toBe('FromEntity');
    });

    it('schema default beats type fallback', async () => {
      const defaults = await generateDefaults([fieldWithDefault], guestObserver, baseContext);

      expect(defaults.status).toBe('active');
      expect(defaults.status).not.toBe('');
    });

    it('temporal default beats type fallback for date fields', async () => {
      const fixedDate = new Date('2025-01-01T00:00:00Z');

      const defaults = await generateDefaults([dateField], guestObserver, baseContext, {
        now: fixedDate,
      });

      expect(defaults.start_date).toBe('2025-01-01');
      expect(defaults.start_date).not.toBe('');
    });
  });
});

describe('generateDefaultsSync', () => {
  it('generates defaults synchronously (faster)', () => {
    const fields = [stringField, numberField, booleanField];

    const defaults = generateDefaultsSync(fields, guestObserver, baseContext);

    expect(defaults.name).toBe('');
    expect(defaults.count).toBe(0);
    expect(defaults.is_active).toBe(false);
  });

  it('uses entity values when editing', () => {
    const fields = [stringField];

    const defaults = generateDefaultsSync(fields, guestObserver, editContext);

    expect(defaults.name).toBe('Kent');
  });

  it('uses schema defaults', () => {
    const defaults = generateDefaultsSync([fieldWithDefault], guestObserver, baseContext);

    expect(defaults.status).toBe('active');
  });

  it('uses temporal defaults', () => {
    const fixedDate = new Date('2025-06-15T00:00:00Z');

    const defaults = generateDefaultsSync([dateField], guestObserver, baseContext, {
      now: fixedDate,
    });

    expect(defaults.start_date).toBe('2025-06-15');
  });

  it('skips entropy (no creative names even for creator)', () => {
    const citizenNameField: FieldDescriptor = {
      name: 'name',
      type: 'string',
      required: true,
      context: ['citizen', 'name'],
    };

    const defaults = generateDefaultsSync([citizenNameField], creatorObserver, baseContext);

    // Sync version skips void.* source, falls through to type fallback
    expect(defaults.name).toBe('');
  });
});

describe('generateUUID', () => {
  it('generates valid UUID v4 format', () => {
    const uuid = generateUUID();

    // UUID v4 format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
    expect(uuid).toMatch(uuidRegex);
  });

  it('generates unique UUIDs', () => {
    const uuid1 = generateUUID();
    const uuid2 = generateUUID();
    const uuid3 = generateUUID();

    expect(uuid1).not.toBe(uuid2);
    expect(uuid2).not.toBe(uuid3);
    expect(uuid1).not.toBe(uuid3);
  });
});

describe('enhanceForDeveloper', () => {
  it('auto-generates UUIDs for uuid-format fields', () => {
    const fields = [uuidField, stringField];
    const defaults = { name: 'Test' };

    const enhanced = enhanceForDeveloper(defaults, fields);

    expect(enhanced.id).toBeDefined();
    expect(typeof enhanced.id).toBe('string');
    expect((enhanced.id as string).length).toBe(36); // UUID length
  });

  it('does not overwrite existing UUID values', () => {
    const fields = [uuidField];
    const defaults = { id: 'existing-uuid-value' };

    const enhanced = enhanceForDeveloper(defaults, fields);

    expect(enhanced.id).toBe('existing-uuid-value');
  });

  it('preserves other default values', () => {
    const fields = [uuidField, stringField];
    const defaults = { name: 'Kent' };

    const enhanced = enhanceForDeveloper(defaults, fields);

    expect(enhanced.name).toBe('Kent');
  });
});

describe('multiple fields', () => {
  it('generates defaults for all fields', async () => {
    const fields: FieldDescriptor[] = [
      { name: 'name', type: 'string', required: true },
      { name: 'age', type: 'number', required: false, default: 25 },
      { name: 'is_active', type: 'boolean', required: false },
      { name: 'status', type: 'string', required: false, enum: ['a', 'b'], default: 'a' },
    ];

    const defaults = await generateDefaults(fields, guestObserver, baseContext);

    expect(defaults).toEqual({
      name: '',
      age: 25,
      is_active: false,
      status: 'a',
    });
  });

  it('handles mixed sources correctly', async () => {
    const fixedDate = new Date('2025-12-19T00:00:00Z');

    const fields: FieldDescriptor[] = [
      { name: 'name', type: 'string', required: true }, // From entity
      { name: 'status', type: 'string', required: false, default: 'pending' }, // From schema
      { name: 'created_at', type: 'string', required: false, format: 'date-time' }, // From time
    ];

    const context: DefaultContext = {
      ...editContext,
      entity: { name: 'Mixed Test' },
    };

    const defaults = await generateDefaults(fields, guestObserver, context, { now: fixedDate });

    expect(defaults.name).toBe('Mixed Test'); // world.*
    expect(defaults.status).toBe('pending'); // concept.*
    expect(defaults.created_at).toBe('2025-12-19T00:00:00.000Z'); // time.*
  });
});
