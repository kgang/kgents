/**
 * FieldWrapper - Chrome Around Fields
 *
 * Provides consistent layout and labeling for all field types:
 * - Label (as question, not noun)
 * - Required indicator
 * - Description
 * - Error message
 * - Teaching hints (for Teaching Mode)
 *
 * Voice anchors:
 * - Labels as questions: "What shall we call it?" not "Name (required)"
 * - Errors are warm: "That doesn't look quite right" not "Invalid input"
 *
 * @see spec/protocols/aspect-form-projection.md - Part VIII
 */

import { motion, AnimatePresence } from 'framer-motion';
import type { FieldDescriptor } from '@/lib/form/FieldProjectionRegistry';
import type { Observer } from '@/lib/schema/generateDefaults';

// =============================================================================
// Types
// =============================================================================

export interface FieldWrapperProps {
  /** Field descriptor */
  field: FieldDescriptor;
  /** Validation error message */
  error?: string;
  /** Observer for archetype-dependent rendering */
  observer: Observer;
  /** Field component (children) */
  children: React.ReactNode;
  /** Optional CSS classes */
  className?: string;
}

// =============================================================================
// Label Generation
// =============================================================================

/**
 * Generate human-friendly labels from field names.
 * Converts snake_case/camelCase to Title Case.
 */
function humanize(fieldName: string): string {
  return fieldName
    .replace(/_/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Convert label to question form for guest/creator archetypes.
 * "Name" → "What shall we call it?"
 * "Description" → "How would you describe it?"
 */
const QUESTION_FORMS: Record<string, string> = {
  name: 'What shall we call it?',
  title: 'What shall we call it?',
  description: 'How would you describe it?',
  content: 'What would you like to say?',
  message: 'What would you like to say?',
  email: 'Where can we reach you?',
  region: 'Where does it belong?',
  archetype: 'What kind of character?',
  password: 'Choose a secret phrase',
  topic: 'What shall we discuss?',
};

/**
 * Get label for field based on archetype.
 * - developer/admin: Technical labels ("name", "description")
 * - guest/creator: Question forms ("What shall we call it?")
 */
function getLabel(field: FieldDescriptor, archetype: string): string {
  // Developer and admin see technical labels
  if (archetype === 'developer' || archetype === 'admin') {
    return humanize(field.name);
  }

  // Guest and creator see questions
  const questionForm = QUESTION_FORMS[field.name.toLowerCase()];
  if (questionForm) {
    return questionForm;
  }

  // Fallback to humanized label
  return humanize(field.name);
}

// =============================================================================
// Teaching Hints
// =============================================================================

/**
 * Teaching hints for different field types (shown when Teaching Mode enabled).
 */
const TEACHING_HINTS: Record<string, string> = {
  uuid: 'UUIDs are globally unique identifiers. Click "Generate" to create one.',
  enum: 'These are the allowed values defined in the contract.',
  date: 'Select a date from the calendar.',
  boolean: 'Toggle on or off.',
  slider: 'Drag to adjust the value within the allowed range.',
  array: 'Click "Add" to add more items.',
  object: 'This field contains nested values.',
  json: 'Edit the raw JSON structure.',
};

function getTeachingHint(field: FieldDescriptor): string | undefined {
  // Check format first (more specific)
  if (field.format === 'uuid') return TEACHING_HINTS.uuid;
  if (field.format === 'date' || field.format === 'date-time') return TEACHING_HINTS.date;

  // Check for enum
  if (field.enum && field.enum.length > 0) return TEACHING_HINTS.enum;

  // Check type
  if (field.type === 'boolean') return TEACHING_HINTS.boolean;
  if (field.type === 'array') return TEACHING_HINTS.array;
  if (field.type === 'object') return TEACHING_HINTS.object;

  // Check if slider (bounded number)
  if (
    (field.type === 'number' || field.type === 'integer') &&
    field.min !== undefined &&
    field.max !== undefined
  ) {
    return TEACHING_HINTS.slider;
  }

  return undefined;
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * FieldWrapper provides consistent chrome around all field components.
 *
 * @example
 * ```tsx
 * <FieldWrapper field={field} error={error} observer={observer}>
 *   <TextField field={field} value={value} onChange={onChange} />
 * </FieldWrapper>
 * ```
 */
export function FieldWrapper({
  field,
  error,
  observer,
  children,
  className = '',
}: FieldWrapperProps) {
  const label = getLabel(field, observer.archetype);
  const showTeaching = false; // TODO: Get from Teaching Mode context
  const teachingHint = showTeaching ? getTeachingHint(field) : undefined;

  return (
    <div className={`space-y-1.5 ${className}`}>
      {/* Label Row */}
      <div className="flex items-baseline justify-between">
        <label
          htmlFor={field.name}
          className={`text-sm font-medium ${error ? 'text-red-400' : 'text-gray-300'}`}
        >
          {label}
          {field.required && (
            <span className="ml-0.5 text-cyan-400" title="Required">
              *
            </span>
          )}
        </label>

        {/* Developer sees type hint */}
        {observer.archetype === 'developer' && (
          <span className="text-xs text-gray-500 font-mono">
            {field.type}
            {field.format && `:${field.format}`}
          </span>
        )}
      </div>

      {/* Description */}
      {field.description && <p className="text-xs text-gray-500">{field.description}</p>}

      {/* Field Component */}
      {children}

      {/* Error Message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.15 }}
            className="overflow-hidden"
          >
            <p className="text-sm text-red-400 flex items-center gap-1">
              <span className="text-red-500">⚠</span>
              {error}
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Teaching Hint */}
      {teachingHint && <p className="text-xs text-cyan-400/70 italic">💡 {teachingHint}</p>}
    </div>
  );
}

export default FieldWrapper;
