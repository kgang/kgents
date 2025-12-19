/**
 * ProjectedField - Field Dispatcher Component
 *
 * Resolves a FieldDescriptor to the appropriate field component using
 * the FieldProjectionRegistry. Higher fidelity projectors are tried first.
 *
 * @see spec/protocols/aspect-form-projection.md - Part IV
 * @see docs/skills/aspect-form-projection.md - Pattern 5
 */

import { useMemo } from 'react';
import { FieldProjectionRegistry, type FieldDescriptor } from '@/lib/form/FieldProjectionRegistry';
import type { Observer } from '@/lib/schema/generateDefaults';

// Import field components
import { TextField } from './fields/TextField';
import { TextareaField } from './fields/TextareaField';
import { NumberField } from './fields/NumberField';
import { SliderField } from './fields/SliderField';
import { BooleanField } from './fields/BooleanField';
import { EnumField } from './fields/EnumField';
import { DateField } from './fields/DateField';
import { UuidField } from './fields/UuidField';
import { JsonField } from './fields/JsonField';

// =============================================================================
// Types
// =============================================================================

export interface ProjectedFieldProps {
  /** Field descriptor from schema analysis */
  field: FieldDescriptor;
  /** Current field value */
  value: unknown;
  /** Value change handler */
  onChange: (value: unknown) => void;
  /** Blur handler for touch tracking */
  onBlur?: () => void;
  /** Observer for archetype-dependent rendering */
  observer: Observer;
  /** Validation error message */
  error?: string;
  /** Whether field is disabled */
  disabled?: boolean;
}

export interface FieldComponentProps {
  /** Field descriptor */
  field: FieldDescriptor;
  /** Current value */
  value: unknown;
  /** Change handler */
  onChange: (value: unknown) => void;
  /** Blur handler */
  onBlur?: () => void;
  /** Validation error */
  error?: string;
  /** Whether disabled */
  disabled?: boolean;
  /** Observer archetype */
  archetype: string;
}

// =============================================================================
// Component Registry Map
// =============================================================================

/**
 * Maps projector names to React components.
 * This bridges the FieldProjectionRegistry with actual implementations.
 */
const COMPONENT_MAP: Record<string, React.ComponentType<FieldComponentProps>> = {
  // High fidelity (specific)
  uuid: UuidField,
  // agentese-path: AgentesePathField, // TODO: Phase 2
  // observer-archetype: ObserverArchetypeField, // TODO: Phase 2
  slider: SliderField,
  enum: EnumField,
  date: DateField,
  boolean: BooleanField,
  textarea: TextareaField,

  // Medium fidelity (general)
  text: TextField,
  number: NumberField,

  // Low fidelity (fallback)
  // object: ObjectField, // TODO: Phase 2
  // array: ArrayField, // TODO: Phase 2
  json: JsonField,
};

// =============================================================================
// Main Component
// =============================================================================

/**
 * ProjectedField resolves a field to its best matching component.
 *
 * Resolution order is determined by the FieldProjectionRegistry's fidelity
 * ordering. Higher fidelity (more specific) projectors are tried first.
 *
 * @example
 * ```tsx
 * <ProjectedField
 *   field={{ name: 'citizen_id', type: 'string', format: 'uuid', required: true }}
 *   value={value}
 *   onChange={setValue}
 *   observer={{ archetype: 'developer' }}
 * />
 * // Resolves to UuidField (fidelity 0.95) instead of TextField (0.75)
 * ```
 */
export function ProjectedField({
  field,
  value,
  onChange,
  onBlur,
  observer,
  error,
  disabled = false,
}: ProjectedFieldProps) {
  // Resolve to best matching projector
  const projector = useMemo(() => {
    return FieldProjectionRegistry.resolve(field);
  }, [field]);

  // Get component for projector
  const Component = COMPONENT_MAP[projector.name] ?? COMPONENT_MAP.json;

  return (
    <Component
      field={field}
      value={value}
      onChange={onChange}
      onBlur={onBlur}
      error={error}
      disabled={disabled}
      archetype={observer.archetype}
    />
  );
}

export default ProjectedField;
