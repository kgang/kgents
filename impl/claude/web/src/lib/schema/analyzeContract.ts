/**
 * Contract Schema Analysis
 *
 * Transforms JSON Schema (from AGENTESE contracts) into FieldDescriptor arrays.
 * This is the bridge between backend contracts and frontend form rendering.
 *
 * Core insight: The Contract IS the form schema. We derive, never duplicate.
 *
 * @see spec/protocols/aspect-form-projection.md - Part VI
 * @see docs/skills/aspect-form-projection.md - Pattern 1
 */

import type { FieldDescriptor, FieldType } from '../form/FieldProjectionRegistry';

// =============================================================================
// Types
// =============================================================================

/**
 * Subset of JSON Schema we support for form generation.
 * This mirrors what comes from /agentese/discover?include_schemas=true
 */
export interface JSONSchema {
  type?: string | string[];
  properties?: Record<string, JSONSchema>;
  required?: string[];
  items?: JSONSchema;

  // Metadata
  title?: string;
  description?: string;
  default?: unknown;
  examples?: unknown[];

  // String constraints
  format?: string;
  pattern?: string;
  minLength?: number;
  maxLength?: number;
  enum?: string[];

  // Number constraints
  minimum?: number;
  maximum?: number;
  exclusiveMinimum?: number;
  exclusiveMaximum?: number;
  multipleOf?: number;

  // Object constraints
  additionalProperties?: boolean | JSONSchema;

  // Array constraints
  minItems?: number;
  maxItems?: number;
  uniqueItems?: boolean;

  // Composition (we flatten these)
  allOf?: JSONSchema[];
  anyOf?: JSONSchema[];
  oneOf?: JSONSchema[];
}

/**
 * Observer archetypes that affect field visibility.
 * Different archetypes see different subsets of fields.
 */
export type Archetype = 'guest' | 'developer' | 'creator' | 'admin';

/**
 * Field visibility configuration per archetype.
 * '*' means all fields visible.
 */
export type ArchetypeVisibility = Record<Archetype, string[] | '*'>;

/**
 * Options for schema analysis.
 */
export interface AnalyzeOptions {
  /** Observer archetype for field filtering */
  archetype?: Archetype;

  /** Path context for intelligent defaults */
  pathContext?: string[];

  /** Custom visibility rules (overrides defaults) */
  visibility?: Partial<ArchetypeVisibility>;
}

// =============================================================================
// Default Visibility Rules
// =============================================================================

/**
 * Default field visibility by archetype.
 *
 * These are sensible defaults that can be overridden per-contract.
 * Fields not in the list are hidden for that archetype.
 *
 * @see spec/protocols/aspect-form-projection.md - Part II.1
 */
const DEFAULT_VISIBILITY: ArchetypeVisibility = {
  // Guest: Essential fields only (name, basic identifiers)
  guest: ['name', 'title', 'description', 'email', 'message'],

  // Developer: All fields visible
  developer: '*',

  // Creator: Creative fields, hide technical (IDs, timestamps)
  creator: ['name', 'title', 'description', 'content', 'message', 'tags', 'style'],

  // Admin: All fields + internal metadata
  admin: '*',
};

/**
 * Fields that are always hidden from non-developers.
 * These are internal/technical fields.
 */
const TECHNICAL_FIELDS = new Set([
  'id',
  'uuid',
  'created_at',
  'updated_at',
  'deleted_at',
  'version',
  'tenant_id',
  'user_id',
  'session_id',
  '_internal',
  '_metadata',
]);

// =============================================================================
// Schema Analysis Functions
// =============================================================================

/**
 * Normalize JSON Schema type to our FieldType.
 */
function normalizeType(schemaType: string | string[] | undefined): FieldType {
  if (!schemaType) return 'string';

  const type = Array.isArray(schemaType) ? schemaType[0] : schemaType;

  switch (type) {
    case 'string':
      return 'string';
    case 'number':
      return 'number';
    case 'integer':
      return 'integer';
    case 'boolean':
      return 'boolean';
    case 'object':
      return 'object';
    case 'array':
      return 'array';
    default:
      return 'string';
  }
}

/**
 * Analyze a single property schema into a FieldDescriptor.
 */
function analyzeProperty(
  name: string,
  schema: JSONSchema,
  required: boolean,
  pathContext: string[]
): FieldDescriptor {
  const type = normalizeType(schema.type);
  const context = [...pathContext, name];

  const field: FieldDescriptor = {
    name,
    type,
    required,
    context,
  };

  // Metadata
  if (schema.description) field.description = schema.description;
  if (schema.default !== undefined) field.default = schema.default;
  if (schema.format) field.format = schema.format;

  // String constraints
  if (schema.pattern) field.pattern = schema.pattern;
  if (schema.minLength !== undefined) field.minLength = schema.minLength;
  if (schema.maxLength !== undefined) field.maxLength = schema.maxLength;
  if (schema.enum) field.enum = schema.enum;

  // Number constraints
  if (schema.minimum !== undefined) field.min = schema.minimum;
  if (schema.maximum !== undefined) field.max = schema.maximum;
  if (schema.exclusiveMinimum !== undefined) field.min = schema.exclusiveMinimum + 1;
  if (schema.exclusiveMaximum !== undefined) field.max = schema.exclusiveMaximum - 1;

  // Nested objects
  if (type === 'object' && schema.properties) {
    field.children = analyzeProperties(schema.properties, schema.required || [], context);
  }

  // Arrays
  if (type === 'array' && schema.items) {
    field.items = analyzeProperty('item', schema.items, false, context);
  }

  return field;
}

/**
 * Analyze all properties in a schema.
 */
function analyzeProperties(
  properties: Record<string, JSONSchema>,
  required: string[],
  pathContext: string[]
): FieldDescriptor[] {
  const requiredSet = new Set(required);

  return Object.entries(properties).map(([name, schema]) =>
    analyzeProperty(name, schema, requiredSet.has(name), pathContext)
  );
}

/**
 * Filter fields based on archetype visibility rules.
 */
function filterForArchetype(
  fields: FieldDescriptor[],
  archetype: Archetype,
  customVisibility?: Partial<ArchetypeVisibility>
): FieldDescriptor[] {
  const visibility = customVisibility?.[archetype] ?? DEFAULT_VISIBILITY[archetype];

  // '*' means show all fields
  if (visibility === '*') {
    return fields;
  }

  const allowedSet = new Set(visibility);

  return fields.filter((field) => {
    // Always hide technical fields for non-developers
    if (archetype !== 'developer' && archetype !== 'admin') {
      if (TECHNICAL_FIELDS.has(field.name)) {
        return false;
      }
    }

    // Check if field is in allowed list
    return allowedSet.has(field.name);
  });
}

/**
 * Flatten allOf/anyOf/oneOf compositions (simple merge strategy).
 */
function flattenComposition(schema: JSONSchema): JSONSchema {
  if (!schema.allOf && !schema.anyOf && !schema.oneOf) {
    return schema;
  }

  const flattened: JSONSchema = { ...schema };
  delete flattened.allOf;
  delete flattened.anyOf;
  delete flattened.oneOf;

  const toMerge = [...(schema.allOf || []), ...(schema.anyOf || []), ...(schema.oneOf || [])];

  for (const subSchema of toMerge) {
    // Merge properties
    if (subSchema.properties) {
      flattened.properties = { ...flattened.properties, ...subSchema.properties };
    }
    // Merge required
    if (subSchema.required) {
      flattened.required = [...(flattened.required || []), ...subSchema.required];
    }
    // Take first type if not set
    if (subSchema.type && !flattened.type) {
      flattened.type = subSchema.type;
    }
  }

  return flattened;
}

// =============================================================================
// Main Export
// =============================================================================

/**
 * Analyze a JSON Schema contract into FieldDescriptor array.
 *
 * This is the primary entry point for transforming backend contracts
 * into frontend-renderable field descriptions.
 *
 * @param schema - JSON Schema from /agentese/discover
 * @param options - Analysis options (archetype, context, visibility)
 * @returns Array of FieldDescriptors ready for form rendering
 *
 * @example
 * // Basic usage
 * const fields = analyzeContract(createTownSchema);
 *
 * @example
 * // With archetype filtering
 * const fields = analyzeContract(schema, { archetype: 'guest' });
 *
 * @example
 * // With path context for defaults
 * const fields = analyzeContract(schema, {
 *   pathContext: ['world', 'town', 'citizen'],
 *   archetype: 'creator'
 * });
 */
export function analyzeContract(
  schema: JSONSchema,
  options: AnalyzeOptions = {}
): FieldDescriptor[] {
  const { archetype = 'guest', pathContext = [], visibility } = options;

  // Handle null/undefined schema
  if (!schema) {
    return [];
  }

  // Flatten compositions
  const flattened = flattenComposition(schema);

  // Must be an object schema with properties
  if (flattened.type !== 'object' && !flattened.properties) {
    // If it's a primitive type, wrap it as a single field
    if (flattened.type) {
      return [analyzeProperty('value', flattened, true, pathContext)];
    }
    return [];
  }

  // Analyze all properties
  const allFields = analyzeProperties(
    flattened.properties || {},
    flattened.required || [],
    pathContext
  );

  // Filter by archetype
  return filterForArchetype(allFields, archetype, visibility);
}

/**
 * Check if a schema has any required fields.
 */
export function hasRequiredFields(schema: JSONSchema): boolean {
  return (schema.required?.length ?? 0) > 0;
}

/**
 * Get the list of required field names from a schema.
 */
export function getRequiredFieldNames(schema: JSONSchema): string[] {
  return schema.required || [];
}

/**
 * Check if a field is considered "advanced" (hidden from guests by default).
 */
export function isAdvancedField(fieldName: string): boolean {
  return TECHNICAL_FIELDS.has(fieldName);
}

// =============================================================================
// Schema Caching
// =============================================================================

/**
 * Cache for analyzed schemas.
 * Key format: `${path}:${aspect}:${archetype}`
 */
const schemaCache = new Map<string, FieldDescriptor[]>();

/**
 * Generate cache key for schema analysis.
 */
export function getCacheKey(path: string, aspect: string, archetype: string): string {
  return `${path}:${aspect}:${archetype}`;
}

/**
 * Get cached analysis or compute and cache.
 */
export function analyzeContractCached(
  schema: JSONSchema,
  path: string,
  aspect: string,
  options: AnalyzeOptions = {}
): FieldDescriptor[] {
  const archetype = options.archetype || 'guest';
  const cacheKey = getCacheKey(path, aspect, archetype);

  const cached = schemaCache.get(cacheKey);
  if (cached) {
    return cached;
  }

  const result = analyzeContract(schema, options);
  schemaCache.set(cacheKey, result);
  return result;
}

/**
 * Clear the schema cache (useful for testing or hot reload).
 */
export function clearSchemaCache(): void {
  schemaCache.clear();
}
