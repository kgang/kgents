/**
 * AspectForm - The Main Orchestrator for AGENTESE Form Projection
 *
 * This component renders forms derived from AGENTESE Contracts. It implements
 * the Form Bifunctor: FormProjector : Aspect × Observer → Form
 *
 * Core insights:
 * - Forms are projections, not pages
 * - Labels are questions, not nouns: "What shall we call it?" not "Name (required)"
 * - Submit button says "Invoke" not "Submit"
 * - Errors are warm, not bureaucratic
 *
 * @see spec/protocols/aspect-form-projection.md
 * @see docs/skills/aspect-form-projection.md
 */

import { useState, useCallback, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiClient } from '@/api/client';
import { analyzeContract, type JSONSchema } from '@/lib/schema/analyzeContract';
import {
  generateDefaults,
  type Observer,
  type DefaultContext,
} from '@/lib/schema/generateDefaults';
import type { FieldDescriptor } from '@/lib/form/FieldProjectionRegistry';
import { ProjectedField } from './ProjectedField';
import { FieldWrapper } from './FieldWrapper';

// =============================================================================
// Types
// =============================================================================

export interface AspectFormProps {
  /** AGENTESE path (e.g., 'world.town.citizen') */
  path: string;
  /** Aspect to invoke (e.g., 'create') */
  aspect: string;
  /** Observer information for form projection */
  observer: Observer;
  /** Optional JSON Schema (if already fetched) */
  schema?: JSONSchema;
  /** Entity being edited (for edit forms) */
  entity?: Record<string, unknown>;
  /** Callback when invocation succeeds */
  onSuccess?: (result: unknown) => void;
  /** Callback when invocation fails */
  onError?: (error: Error) => void;
  /** Callback when form values change */
  onChange?: (values: Record<string, unknown>) => void;
  /** Optional additional CSS classes */
  className?: string;
}

interface FormState {
  status: 'idle' | 'loading' | 'submitting' | 'success' | 'error';
  values: Record<string, unknown>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  result?: unknown;
  errorMessage?: string;
}

// =============================================================================
// Validation Tone (Observer-Dependent)
// =============================================================================

const VALIDATION_TONES: Record<string, Record<string, (e: ValidationContext) => string>> = {
  guest: {
    required: () => `This field needs a value`,
    pattern: () => `That doesn't look quite right`,
    range: (e) => `Please adjust this value (${e.min}-${e.max})`,
    minLength: (e) => `Needs to be at least ${e.minLength} characters`,
    maxLength: (e) => `Needs to be at most ${e.maxLength} characters`,
  },
  developer: {
    required: (e) => `Required: \`${e.field}\``,
    pattern: (e) => `Pattern mismatch: expected ${e.pattern}`,
    range: (e) => `Value ${e.value} outside range [${e.min}, ${e.max}]`,
    minLength: (e) => `minLength: ${e.minLength}, got: ${String(e.value).length}`,
    maxLength: (e) => `maxLength: ${e.maxLength}, got: ${String(e.value).length}`,
  },
  creator: {
    required: (e) => `Every creation needs a ${e.field}—what shall we call it?`,
    pattern: () => `Let's make sure this fits the shape we need`,
    range: () => `That's wonderful, but we need to adjust it a little`,
    minLength: (e) => `A bit more, please—at least ${e.minLength} characters`,
    maxLength: (e) => `That's wonderful, but we need to trim it a little (max ${e.maxLength})`,
  },
  admin: {
    required: (e) => `Required: ${e.field}`,
    pattern: (e) => `Invalid pattern: ${e.pattern}`,
    range: (e) => `Out of range [${e.min}, ${e.max}]`,
    minLength: (e) => `Min length: ${e.minLength}`,
    maxLength: (e) => `Max length: ${e.maxLength}`,
  },
};

interface ValidationContext {
  field: string;
  value?: unknown;
  min?: number;
  max?: number;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
}

function formatValidationError(
  type: string,
  context: ValidationContext,
  archetype: string
): string {
  const tone = VALIDATION_TONES[archetype] ?? VALIDATION_TONES.guest;
  const formatter = tone[type];
  return formatter ? formatter(context) : `Invalid ${context.field}`;
}

// =============================================================================
// Field Validation
// =============================================================================

function validateField(
  field: FieldDescriptor,
  value: unknown,
  archetype: string
): string | undefined {
  const context: ValidationContext = {
    field: field.name,
    value,
    min: field.min,
    max: field.max,
    minLength: field.minLength,
    maxLength: field.maxLength,
    pattern: field.pattern,
  };

  // Required check
  if (field.required) {
    if (value === undefined || value === null || value === '') {
      return formatValidationError('required', context, archetype);
    }
    if (Array.isArray(value) && value.length === 0) {
      return formatValidationError('required', context, archetype);
    }
  }

  // Skip other validations if empty (and not required)
  if (value === undefined || value === null || value === '') {
    return undefined;
  }

  // String validations
  if (field.type === 'string' && typeof value === 'string') {
    if (field.minLength !== undefined && value.length < field.minLength) {
      return formatValidationError('minLength', context, archetype);
    }
    if (field.maxLength !== undefined && value.length > field.maxLength) {
      return formatValidationError('maxLength', context, archetype);
    }
    if (field.pattern) {
      const regex = new RegExp(field.pattern);
      if (!regex.test(value)) {
        return formatValidationError('pattern', context, archetype);
      }
    }
  }

  // Number validations
  if ((field.type === 'number' || field.type === 'integer') && typeof value === 'number') {
    if (field.min !== undefined && value < field.min) {
      return formatValidationError('range', context, archetype);
    }
    if (field.max !== undefined && value > field.max) {
      return formatValidationError('range', context, archetype);
    }
  }

  return undefined;
}

function validateAllFields(
  fields: FieldDescriptor[],
  values: Record<string, unknown>,
  archetype: string
): Record<string, string> {
  const errors: Record<string, string> = {};
  for (const field of fields) {
    const error = validateField(field, values[field.name], archetype);
    if (error) {
      errors[field.name] = error;
    }
  }
  return errors;
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * AspectForm renders and submits forms derived from AGENTESE Contracts.
 *
 * @example
 * ```tsx
 * <AspectForm
 *   path="world.town.citizen"
 *   aspect="create"
 *   observer={{ archetype: 'creator' }}
 *   onSuccess={(result) => console.log('Created:', result)}
 * />
 * ```
 */
export function AspectForm({
  path,
  aspect,
  observer,
  schema: providedSchema,
  entity,
  onSuccess,
  onError,
  onChange,
  className = '',
}: AspectFormProps) {
  // Schema state (fetched from /agentese/discover if not provided)
  // null = no input required, undefined = not yet loaded
  const [schema, setSchema] = useState<JSONSchema | null | undefined>(
    providedSchema !== undefined ? providedSchema : undefined
  );
  const [schemaLoading, setSchemaLoading] = useState(providedSchema === undefined);
  const [schemaError, setSchemaError] = useState<string | null>(null);

  // Form state
  const [state, setState] = useState<FormState>({
    status: 'idle',
    values: {},
    errors: {},
    touched: {},
  });

  // Derive fields from schema
  const fields = useMemo(() => {
    if (!schema) return [];
    return analyzeContract(schema, {
      archetype: observer.archetype,
      pathContext: path.split('.'),
    });
  }, [schema, observer.archetype, path]);

  // Fetch schema from discovery endpoint if not provided
  useEffect(() => {
    // If schema was explicitly provided (even if null = no input), use it
    if (providedSchema !== undefined) {
      setSchema(providedSchema);
      setSchemaLoading(false);
      return;
    }

    const fetchSchema = async () => {
      setSchemaLoading(true);
      setSchemaError(null);

      try {
        // Fetch contract schema from discovery endpoint
        const pathSegments = path.replace(/\./g, '/');
        const response = await apiClient.get<{
          contracts?: Record<string, { request_schema?: JSONSchema }>;
        }>(`/agentese/${pathSegments}/affordances`);

        const contract = response.data.contracts?.[aspect];
        if (contract?.request_schema) {
          setSchema(contract.request_schema);
        } else {
          // No schema = aspect doesn't require input
          setSchema(null);
        }
      } catch (e) {
        const error = e as Error;
        setSchemaError(error.message);
      } finally {
        setSchemaLoading(false);
      }
    };

    fetchSchema();
  }, [path, aspect, providedSchema]);

  // Generate defaults when fields are ready
  useEffect(() => {
    if (fields.length === 0) return;

    const defaultContext: DefaultContext = {
      path,
      aspect,
      entity,
      isEdit: !!entity,
    };

    // Use async generateDefaults for full five-source cascade
    generateDefaults(fields, observer, defaultContext, { skipHistory: true }).then((defaults) => {
      setState((prev) => ({
        ...prev,
        values: { ...defaults, ...prev.values },
      }));
    });
  }, [fields, observer, path, aspect, entity]);

  // Handle field value change
  const handleChange = useCallback(
    (name: string, value: unknown) => {
      setState((prev) => {
        const newValues = { ...prev.values, [name]: value };
        const newTouched = { ...prev.touched, [name]: true };

        // Re-validate touched field
        const field = fields.find((f) => f.name === name);
        const newErrors = { ...prev.errors };
        if (field) {
          const error = validateField(field, value, observer.archetype);
          if (error) {
            newErrors[name] = error;
          } else {
            delete newErrors[name];
          }
        }

        return {
          ...prev,
          values: newValues,
          touched: newTouched,
          errors: newErrors,
          status: 'idle', // Clear any previous status
        };
      });

      // Notify parent of change
      onChange?.({ ...state.values, [name]: value });
    },
    [fields, observer.archetype, onChange, state.values]
  );

  // Handle field blur (mark as touched)
  const handleBlur = useCallback(
    (name: string) => {
      setState((prev) => {
        if (prev.touched[name]) return prev;

        const newTouched = { ...prev.touched, [name]: true };

        // Validate on blur
        const field = fields.find((f) => f.name === name);
        const newErrors = { ...prev.errors };
        if (field) {
          const error = validateField(field, prev.values[field.name], observer.archetype);
          if (error) {
            newErrors[name] = error;
          } else {
            delete newErrors[name];
          }
        }

        return { ...prev, touched: newTouched, errors: newErrors };
      });
    },
    [fields, observer.archetype]
  );

  // Handle form submission
  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      // Validate all fields
      const errors = validateAllFields(fields, state.values, observer.archetype);
      if (Object.keys(errors).length > 0) {
        // Mark all fields as touched to show errors
        const touched = fields.reduce((acc, f) => ({ ...acc, [f.name]: true }), {});
        setState((prev) => ({ ...prev, errors, touched, status: 'idle' }));
        return;
      }

      // Submit to AGENTESE
      setState((prev) => ({ ...prev, status: 'submitting' }));

      try {
        const pathSegments = path.replace(/\./g, '/');
        const response = await apiClient.post<{
          path: string;
          aspect: string;
          result: unknown;
          error?: string;
        }>(`/agentese/${pathSegments}/${aspect}`, state.values);

        if (response.data.error) {
          throw new Error(response.data.error);
        }

        setState((prev) => ({
          ...prev,
          status: 'success',
          result: response.data.result,
        }));

        onSuccess?.(response.data.result);
      } catch (e) {
        const error = e as Error;
        setState((prev) => ({
          ...prev,
          status: 'error',
          errorMessage: error.message,
        }));
        onError?.(error);
      }
    },
    [fields, state.values, path, aspect, observer.archetype, onSuccess, onError]
  );

  // Handle form reset
  const handleReset = useCallback(() => {
    // Re-generate defaults
    const defaultContext: DefaultContext = {
      path,
      aspect,
      entity,
      isEdit: !!entity,
    };

    generateDefaults(fields, observer, defaultContext, { skipHistory: true }).then((defaults) => {
      setState({
        status: 'idle',
        values: defaults,
        errors: {},
        touched: {},
      });
    });
  }, [fields, observer, path, aspect, entity]);

  // Separate required and optional fields
  const requiredFields = fields.filter((f) => f.required);
  const optionalFields = fields.filter((f) => !f.required);

  // Loading state
  if (schemaLoading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="text-gray-400">Working...</div>
      </div>
    );
  }

  // Error state
  if (schemaError) {
    return (
      <div className={`p-4 bg-red-900/20 rounded-lg border border-red-500/30 ${className}`}>
        <div className="text-red-400 font-medium">That doesn&apos;t look quite right</div>
        <div className="text-red-300 text-sm mt-1">{schemaError}</div>
      </div>
    );
  }

  // No input required
  if (!schema || fields.length === 0) {
    return (
      <div className={`p-4 ${className}`}>
        <div className="text-gray-400 mb-4">No input required for this aspect.</div>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={state.status === 'submitting'}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          {state.status === 'submitting' ? 'Working...' : 'Invoke'}
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className={`space-y-6 ${className}`}>
      {/* Required Fields */}
      {requiredFields.length > 0 && (
        <div className="space-y-4">
          {requiredFields.map((field) => (
            <FieldWrapper
              key={field.name}
              field={field}
              error={state.touched[field.name] ? state.errors[field.name] : undefined}
              observer={observer}
            >
              <ProjectedField
                field={field}
                value={state.values[field.name]}
                onChange={(value) => handleChange(field.name, value)}
                onBlur={() => handleBlur(field.name)}
                observer={observer}
                error={state.touched[field.name] ? state.errors[field.name] : undefined}
              />
            </FieldWrapper>
          ))}
        </div>
      )}

      {/* Optional Fields (Collapsible) */}
      {optionalFields.length > 0 && (
        <OptionalFieldsSection
          fields={optionalFields}
          values={state.values}
          errors={state.errors}
          touched={state.touched}
          observer={observer}
          onChange={handleChange}
          onBlur={handleBlur}
        />
      )}

      {/* Form Actions */}
      <div className="flex items-center gap-3 pt-4 border-t border-gray-700/50">
        <button
          type="submit"
          disabled={state.status === 'submitting'}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors disabled:opacity-50 font-medium"
        >
          {state.status === 'submitting' ? 'Working...' : 'Invoke'}
        </button>

        <button
          type="button"
          onClick={handleReset}
          disabled={state.status === 'submitting'}
          className="px-4 py-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50"
        >
          Start fresh
        </button>
      </div>

      {/* Success Message */}
      <AnimatePresence>
        {state.status === 'success' && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="p-4 bg-green-900/20 rounded-lg border border-green-500/30"
          >
            <div className="text-green-400 font-medium">Done</div>
            {state.result !== undefined && observer.archetype === 'developer' && (
              <pre className="text-green-300 text-sm mt-2 overflow-auto max-h-40">
                {JSON.stringify(state.result, null, 2)}
              </pre>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Message */}
      <AnimatePresence>
        {state.status === 'error' && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="p-4 bg-red-900/20 rounded-lg border border-red-500/30"
          >
            <div className="text-red-400 font-medium">
              {observer.archetype === 'developer'
                ? 'Invocation failed'
                : "That didn't work as expected"}
            </div>
            <div className="text-red-300 text-sm mt-1">{state.errorMessage}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </form>
  );
}

// =============================================================================
// Optional Fields Section (Collapsible)
// =============================================================================

interface OptionalFieldsSectionProps {
  fields: FieldDescriptor[];
  values: Record<string, unknown>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  observer: Observer;
  onChange: (name: string, value: unknown) => void;
  onBlur: (name: string) => void;
}

function OptionalFieldsSection({
  fields,
  values,
  errors,
  touched,
  observer,
  onChange,
  onBlur,
}: OptionalFieldsSectionProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-gray-700/50 rounded-lg overflow-hidden">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-800/50 transition-colors"
      >
        <span className="text-gray-400 text-sm">
          {fields.length} optional {fields.length === 1 ? 'field' : 'fields'}
        </span>
        <motion.span
          animate={{ rotate: expanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="text-gray-500"
        >
          ▼
        </motion.span>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-gray-700/50"
          >
            <div className="p-4 space-y-4">
              {fields.map((field) => (
                <FieldWrapper
                  key={field.name}
                  field={field}
                  error={touched[field.name] ? errors[field.name] : undefined}
                  observer={observer}
                >
                  <ProjectedField
                    field={field}
                    value={values[field.name]}
                    onChange={(value) => onChange(field.name, value)}
                    onBlur={() => onBlur(field.name)}
                    observer={observer}
                    error={touched[field.name] ? errors[field.name] : undefined}
                  />
                </FieldWrapper>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default AspectForm;
