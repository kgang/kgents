/**
 * Field Projection Registry
 *
 * Maps field descriptors to appropriate UI components based on fidelity ordering.
 * Higher fidelity projectors are more specific and tried first.
 *
 * Core insight: Fields are projections, not widgets. The registry determines
 * which projection best preserves the semantic meaning of each field type.
 *
 * @see spec/protocols/aspect-form-projection.md - Part IV
 * @see docs/skills/aspect-form-projection.md - Pattern 5
 */

// =============================================================================
// Types
// =============================================================================

/**
 * JSON Schema field types (subset we support)
 */
export type FieldType = 'string' | 'number' | 'integer' | 'boolean' | 'object' | 'array';

/**
 * Describes a single field derived from a Contract's JSON Schema.
 *
 * This is the canonical representation that flows through the form system.
 * Contract → FieldDescriptor[] → FieldProjector → Component
 */
export interface FieldDescriptor {
  /** Field identifier (property name in schema) */
  name: string;

  /** JSON Schema type */
  type: FieldType;

  /** Whether field is required */
  required: boolean;

  // --- Schema metadata ---
  /** Schema default value */
  default?: unknown;

  /** Human-readable description */
  description?: string;

  /** Format hint (uuid, date, email, uri, etc.) */
  format?: string;

  // --- Constraints ---
  /** Minimum value (numbers) */
  min?: number;

  /** Maximum value (numbers) */
  max?: number;

  /** Minimum length (strings) */
  minLength?: number;

  /** Maximum length (strings) */
  maxLength?: number;

  /** Regex pattern (strings) */
  pattern?: string;

  /** Allowed values (enums) */
  enum?: string[];

  // --- Nested structure ---
  /** Child fields for objects */
  children?: FieldDescriptor[];

  /** Item descriptor for arrays */
  items?: FieldDescriptor;

  // --- Context for defaults ---
  /** Path hints for intelligent defaults: ['citizen', 'name'] */
  context?: string[];
}

/**
 * A field projector maps field descriptors to UI components.
 *
 * The registry maintains projectors sorted by fidelity (highest first).
 * Resolution finds the first projector whose `matches` returns true.
 */
export interface FieldProjector {
  /** Unique projector name */
  name: string;

  /**
   * Fidelity score (0.0 - 1.0)
   *
   * Higher fidelity = more information preserved in the projection.
   * The `json` projector has fidelity 1.0 (lossless) but poor UX.
   * Specific projectors like `uuid` have high fidelity (0.95) and good UX.
   */
  fidelity: number;

  /** Returns true if this projector can handle the field */
  matches: (field: FieldDescriptor) => boolean;

  /**
   * React component type (added in Phase 1)
   * For now, we just track the projector name.
   */
  componentName?: string;
}

// =============================================================================
// Registry Implementation
// =============================================================================

/**
 * The Field Projection Registry
 *
 * Maintains a fidelity-sorted list of projectors and resolves fields to
 * their best matching projector.
 */
class FieldProjectionRegistryImpl {
  private projectors: FieldProjector[] = [];

  /**
   * Register a new field projector.
   * Projectors are automatically sorted by fidelity (highest first).
   */
  register(projector: FieldProjector): void {
    // Remove existing projector with same name (allows re-registration)
    this.projectors = this.projectors.filter((p) => p.name !== projector.name);

    // Add and sort by fidelity descending
    this.projectors.push(projector);
    this.projectors.sort((a, b) => b.fidelity - a.fidelity);
  }

  /**
   * Resolve a field to its best matching projector.
   *
   * Tries projectors in fidelity order (highest first).
   * The `json` fallback projector always matches, ensuring resolution never fails.
   */
  resolve(field: FieldDescriptor): FieldProjector {
    const projector = this.projectors.find((p) => p.matches(field));
    if (!projector) {
      // This should never happen if JSON_FALLBACK is registered
      throw new Error(`No projector found for field: ${field.name} (type: ${field.type})`);
    }
    return projector;
  }

  /**
   * Get all registered projectors (for debugging/introspection).
   */
  getAll(): readonly FieldProjector[] {
    return this.projectors;
  }

  /**
   * Clear all projectors (useful for testing).
   */
  clear(): void {
    this.projectors = [];
  }

  /**
   * Get projector by name.
   */
  get(name: string): FieldProjector | undefined {
    return this.projectors.find((p) => p.name === name);
  }
}

// =============================================================================
// Built-in Projectors (from spec Part IV)
// =============================================================================

/**
 * UUID field projector
 * Matches: format === 'uuid'
 * Provides: UUID input with generate button
 */
export const UUID_PROJECTOR: FieldProjector = {
  name: 'uuid',
  fidelity: 0.95,
  matches: (field) => field.format === 'uuid',
  componentName: 'UuidField',
};

/**
 * AGENTESE path projector
 * Matches: name === 'path' (convention for AGENTESE paths)
 * Provides: Path picker with autocomplete
 */
export const AGENTESE_PATH_PROJECTOR: FieldProjector = {
  name: 'agentese-path',
  fidelity: 0.95,
  matches: (field) => field.name === 'path' && field.type === 'string',
  componentName: 'AgentesePathField',
};

/**
 * Observer archetype projector
 * Matches: name === 'archetype'
 * Provides: Visual archetype selector
 */
export const OBSERVER_ARCHETYPE_PROJECTOR: FieldProjector = {
  name: 'observer-archetype',
  fidelity: 0.95,
  matches: (field) => field.name === 'archetype' && field.type === 'string',
  componentName: 'ObserverArchetypeField',
};

/**
 * Slider projector for bounded numbers
 * Matches: number with both min and max defined
 * Provides: Slider with value display
 */
export const SLIDER_PROJECTOR: FieldProjector = {
  name: 'slider',
  fidelity: 0.9,
  matches: (field) =>
    (field.type === 'number' || field.type === 'integer') &&
    field.min !== undefined &&
    field.max !== undefined,
  componentName: 'SliderField',
};

/**
 * Enum/select projector
 * Matches: field has enum values
 * Provides: Select dropdown
 */
export const ENUM_PROJECTOR: FieldProjector = {
  name: 'enum',
  fidelity: 0.9,
  matches: (field) => field.enum !== undefined && field.enum.length > 0,
  componentName: 'EnumField',
};

/**
 * Date projector
 * Matches: format === 'date' or 'date-time'
 * Provides: Date picker
 */
export const DATE_PROJECTOR: FieldProjector = {
  name: 'date',
  fidelity: 0.85,
  matches: (field) => field.format === 'date' || field.format === 'date-time',
  componentName: 'DateField',
};

/**
 * Boolean/toggle projector
 * Matches: boolean type
 * Provides: Toggle switch
 */
export const BOOLEAN_PROJECTOR: FieldProjector = {
  name: 'boolean',
  fidelity: 0.85,
  matches: (field) => field.type === 'boolean',
  componentName: 'BooleanField',
};

/**
 * Textarea projector for long text
 * Matches: string with maxLength > 200
 * Provides: Multi-line textarea
 */
export const TEXTAREA_PROJECTOR: FieldProjector = {
  name: 'textarea',
  fidelity: 0.8,
  matches: (field) =>
    field.type === 'string' && field.maxLength !== undefined && field.maxLength > 200,
  componentName: 'TextareaField',
};

/**
 * Text input projector (default for strings)
 * Matches: string type
 * Provides: Single-line text input
 */
export const TEXT_PROJECTOR: FieldProjector = {
  name: 'text',
  fidelity: 0.75,
  matches: (field) => field.type === 'string',
  componentName: 'TextField',
};

/**
 * Number input projector (default for numbers)
 * Matches: number or integer type
 * Provides: Number input with step buttons
 */
export const NUMBER_PROJECTOR: FieldProjector = {
  name: 'number',
  fidelity: 0.75,
  matches: (field) => field.type === 'number' || field.type === 'integer',
  componentName: 'NumberField',
};

/**
 * Object projector for nested structures
 * Matches: object type
 * Provides: Recursive field group
 */
export const OBJECT_PROJECTOR: FieldProjector = {
  name: 'object',
  fidelity: 0.7,
  matches: (field) => field.type === 'object',
  componentName: 'ObjectField',
};

/**
 * Array projector for repeatable fields
 * Matches: array type
 * Provides: Add/remove list of items
 */
export const ARRAY_PROJECTOR: FieldProjector = {
  name: 'array',
  fidelity: 0.7,
  matches: (field) => field.type === 'array',
  componentName: 'ArrayField',
};

/**
 * JSON fallback projector (lossless but not user-friendly)
 * Matches: ALWAYS (universal fallback)
 * Provides: Raw JSON editor
 *
 * Fidelity is 0.0 because while it preserves all information,
 * it provides the worst UX. It's always tried last as the universal fallback.
 */
export const JSON_FALLBACK_PROJECTOR: FieldProjector = {
  name: 'json',
  fidelity: 0.0, // Lowest fidelity = tried last (universal fallback)
  matches: () => true, // Always matches
  componentName: 'JsonField',
};

// =============================================================================
// Singleton Registry with Built-in Projectors
// =============================================================================

/**
 * The global Field Projection Registry instance.
 *
 * Pre-populated with built-in projectors from the spec.
 * Additional projectors can be registered at runtime.
 */
export const FieldProjectionRegistry = new FieldProjectionRegistryImpl();

// Register built-in projectors in fidelity order
// (Order doesn't matter since they're sorted, but this is readable)
[
  UUID_PROJECTOR,
  AGENTESE_PATH_PROJECTOR,
  OBSERVER_ARCHETYPE_PROJECTOR,
  SLIDER_PROJECTOR,
  ENUM_PROJECTOR,
  DATE_PROJECTOR,
  BOOLEAN_PROJECTOR,
  TEXTAREA_PROJECTOR,
  TEXT_PROJECTOR,
  NUMBER_PROJECTOR,
  OBJECT_PROJECTOR,
  ARRAY_PROJECTOR,
  JSON_FALLBACK_PROJECTOR,
].forEach((p) => FieldProjectionRegistry.register(p));

// =============================================================================
// Exports
// =============================================================================

export default FieldProjectionRegistry;
