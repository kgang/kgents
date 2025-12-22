/**
 * SchemaForm - JSON Schema to form field conversion
 *
 * Recursively renders form fields based on JSON Schema.
 * Supports:
 * - String (text, textarea, enum dropdown)
 * - Number/Integer
 * - Boolean (toggle)
 * - Array (add/remove items)
 * - Object (nested fieldset)
 *
 * Features:
 * - Required field indicators
 * - Inline validation errors
 * - Description tooltips
 * - Raw JSON toggle for power users
 */

import { useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Trash2, ChevronDown, ChevronRight, AlertCircle, Info } from 'lucide-react';
import type { SchemaFormProps, SchemaFieldProps, JsonSchemaProperty } from './types';

// =============================================================================
// Field Components
// =============================================================================

/**
 * String field - text input, textarea, or select for enums
 */
function StringField({ name, path, schema, value, error, onChange }: SchemaFieldProps) {
  const hasEnum = schema.enum && schema.enum.length > 0;
  const isTextarea = schema.format === 'textarea' || (schema.maxLength && schema.maxLength > 200);
  const borderClass = error ? 'border-red-500' : 'border-gray-600';

  if (hasEnum) {
    return (
      <select
        value={(value as string) || ''}
        onChange={(e) => onChange(path, e.target.value)}
        className={`
          w-full px-3 py-2 rounded-lg bg-gray-700/50 border
          text-white focus:ring-2 focus:ring-cyan-500/50 focus:outline-none
          ${borderClass}
        `}
      >
        <option value="">Select {name}...</option>
        {schema.enum!.map((opt) => (
          <option key={String(opt)} value={String(opt)}>
            {String(opt)}
          </option>
        ))}
      </select>
    );
  }

  if (isTextarea) {
    return (
      <textarea
        value={(value as string) || ''}
        onChange={(e) => onChange(path, e.target.value)}
        placeholder={schema.description || `Enter ${name}...`}
        rows={4}
        className={`
          w-full px-3 py-2 rounded-lg bg-gray-700/50 border resize-y
          text-white placeholder:text-gray-500
          focus:ring-2 focus:ring-cyan-500/50 focus:outline-none
          ${borderClass}
        `}
      />
    );
  }

  return (
    <input
      type="text"
      value={(value as string) || ''}
      onChange={(e) => onChange(path, e.target.value)}
      placeholder={schema.description || `Enter ${name}...`}
      className={`
        w-full px-3 py-2 rounded-lg bg-gray-700/50 border
        text-white placeholder:text-gray-500
        focus:ring-2 focus:ring-cyan-500/50 focus:outline-none
        ${borderClass}
      `}
    />
  );
}

/**
 * Number field - for integer and number types
 */
function NumberField({ name, path, schema, value, error, onChange }: SchemaFieldProps) {
  return (
    <input
      type="number"
      value={value !== undefined && value !== null ? Number(value) : ''}
      onChange={(e) => {
        const val = e.target.value === '' ? undefined : Number(e.target.value);
        onChange(path, val);
      }}
      placeholder={schema.description || `Enter ${name}...`}
      min={schema.minimum}
      max={schema.maximum}
      step={schema.type === 'integer' ? 1 : 'any'}
      className={`
        w-full px-3 py-2 rounded-lg bg-gray-700/50 border
        text-white placeholder:text-gray-500
        focus:ring-2 focus:ring-cyan-500/50 focus:outline-none
        ${error ? 'border-red-500' : 'border-gray-600'}
      `}
    />
  );
}

/**
 * Boolean field - toggle switch
 */
function BooleanField({
  path,
  value,
  onChange,
}: Omit<SchemaFieldProps, 'name' | 'schema' | 'error' | 'required' | 'depth'>) {
  const isChecked = Boolean(value);

  return (
    <button
      type="button"
      onClick={() => onChange(path, !isChecked)}
      className={`
        relative w-12 h-6 rounded-full transition-colors
        ${isChecked ? 'bg-cyan-600' : 'bg-gray-600'}
      `}
    >
      <motion.div
        className="absolute top-1 w-4 h-4 rounded-full bg-white"
        animate={{ left: isChecked ? '1.5rem' : '0.25rem' }}
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
      />
    </button>
  );
}

/**
 * Array field - repeatable items with add/remove
 */
function ArrayField({
  name,
  path,
  schema,
  value,
  onChange,
  depth,
}: Omit<SchemaFieldProps, 'error' | 'required'>) {
  const items = Array.isArray(value) ? value : [];
  const itemSchema = schema.items || { type: 'string' };

  const handleAdd = () => {
    const defaultValue = getDefaultValue(itemSchema);
    onChange(path, [...items, defaultValue]);
  };

  const handleRemove = (index: number) => {
    onChange(
      path,
      items.filter((_, i) => i !== index)
    );
  };

  const handleItemChange = (index: number, newValue: unknown) => {
    const newItems = [...items];
    newItems[index] = newValue;
    onChange(path, newItems);
  };

  return (
    <div className="space-y-2">
      <AnimatePresence>
        {items.map((item, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="flex items-start gap-2"
          >
            <div className="flex-1">
              <SchemaField
                name={`${name}[${index}]`}
                path={`${path}[${index}]`}
                schema={itemSchema}
                value={item}
                required={false}
                onChange={(_, val) => handleItemChange(index, val)}
                depth={depth + 1}
              />
            </div>
            <button
              type="button"
              onClick={() => handleRemove(index)}
              className="
                p-2 rounded-lg text-gray-400 hover:text-red-400
                hover:bg-red-500/10 transition-colors mt-0.5
              "
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>

      <button
        type="button"
        onClick={handleAdd}
        className="
          flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm
          text-cyan-400 hover:bg-cyan-500/10 transition-colors
        "
      >
        <Plus className="w-4 h-4" />
        <span>Add {name}</span>
      </button>
    </div>
  );
}

/**
 * Object field - nested fieldset with collapsible UI
 */
function ObjectField({ name, path, schema, value, required, onChange, depth }: SchemaFieldProps) {
  const [isExpanded, setIsExpanded] = useState(depth < 2); // Auto-expand first 2 levels

  const properties = schema.properties || {};
  const requiredFields = new Set(schema.required || []);
  const objectValue = (typeof value === 'object' && value !== null ? value : {}) as Record<
    string,
    unknown
  >;

  return (
    <div className="border border-gray-700/50 rounded-lg overflow-hidden">
      {/* Header */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="
          w-full flex items-center gap-2 px-3 py-2
          bg-gray-700/30 hover:bg-gray-700/50 transition-colors
          text-left
        "
      >
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-gray-400" />
        )}
        <span className="text-sm font-medium text-gray-300">{name}</span>
        {required && <span className="text-red-400 text-xs">*</span>}
        {!isExpanded && (
          <span className="text-xs text-gray-500 ml-auto">
            {Object.keys(objectValue).length} fields
          </span>
        )}
      </button>

      {/* Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="p-3 space-y-3 border-t border-gray-700/50"
          >
            {Object.entries(properties).map(([propName, propSchema]) => (
              <SchemaField
                key={propName}
                name={propName}
                path={path ? `${path}.${propName}` : propName}
                schema={propSchema}
                value={objectValue[propName]}
                required={requiredFields.has(propName)}
                onChange={onChange}
                depth={depth + 1}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// =============================================================================
// Main Field Component
// =============================================================================

/**
 * Get default value for a schema type
 */
function getDefaultValue(schema: JsonSchemaProperty): unknown {
  if (schema.default !== undefined) return schema.default;

  switch (schema.type) {
    case 'string':
      return '';
    case 'number':
    case 'integer':
      return undefined;
    case 'boolean':
      return false;
    case 'array':
      return [];
    case 'object':
      return {};
    default:
      return undefined;
  }
}

/**
 * Recursive field renderer based on schema type
 */
function SchemaField(props: SchemaFieldProps) {
  const { name, schema, error, required } = props;

  // Field wrapper with label
  const renderWithLabel = (field: React.ReactNode) => (
    <div className="space-y-1.5">
      {/* Label row */}
      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-gray-300">
          {schema.title || name}
          {required && <span className="text-red-400 ml-0.5">*</span>}
        </label>
        {schema.description && (
          <div className="group relative">
            <Info className="w-3.5 h-3.5 text-gray-500 cursor-help" />
            <div
              className="
              absolute left-0 bottom-full mb-1 px-2 py-1
              bg-gray-800 rounded text-xs text-gray-300
              opacity-0 group-hover:opacity-100 transition-opacity
              pointer-events-none whitespace-nowrap z-10
              max-w-xs
            "
            >
              {schema.description}
            </div>
          </div>
        )}
      </div>

      {/* Field */}
      {field}

      {/* Error */}
      {error && (
        <div className="flex items-center gap-1 text-xs text-red-400">
          <AlertCircle className="w-3 h-3" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );

  // Render based on type
  switch (schema.type) {
    case 'string':
      return renderWithLabel(<StringField {...props} />);

    case 'number':
    case 'integer':
      return renderWithLabel(<NumberField {...props} />);

    case 'boolean':
      return (
        <div className="flex items-center justify-between py-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-300">{schema.title || name}</span>
            {schema.description && (
              <div className="group relative">
                <Info className="w-3.5 h-3.5 text-gray-500 cursor-help" />
                <div
                  className="
                  absolute left-0 bottom-full mb-1 px-2 py-1
                  bg-gray-800 rounded text-xs text-gray-300
                  opacity-0 group-hover:opacity-100 transition-opacity
                  pointer-events-none whitespace-nowrap z-10
                "
                >
                  {schema.description}
                </div>
              </div>
            )}
          </div>
          <BooleanField {...props} />
        </div>
      );

    case 'array':
      return renderWithLabel(<ArrayField {...props} />);

    case 'object':
      return <ObjectField {...props} />;

    default:
      // Unknown type - render as string input
      return renderWithLabel(<StringField {...props} />);
  }
}

// =============================================================================
// Main Form Component
// =============================================================================

export function SchemaForm({
  schema,
  values,
  errors,
  onChange,
  rawJsonMode,
  rawJson,
  onRawJsonChange,
  onToggleRawJson,
}: SchemaFormProps) {
  // Always call hooks at the top level (React hooks rule)
  const isValidJson = useMemo(() => {
    if (!rawJsonMode) return true; // Not relevant when not in raw mode
    try {
      JSON.parse(rawJson);
      return true;
    } catch {
      return false;
    }
  }, [rawJson, rawJsonMode]);

  // Form mode with schema - pre-compute
  const requiredFields = useMemo(() => new Set(schema?.required || []), [schema?.required]);

  // Raw JSON mode
  if (rawJsonMode) {
    return (
      <div className="space-y-2">
        <textarea
          value={rawJson}
          onChange={(e) => onRawJsonChange(e.target.value)}
          placeholder='{"key": "value"}'
          rows={12}
          className={`
            w-full px-3 py-2 rounded-lg bg-gray-900 border
            font-mono text-sm text-gray-200 placeholder:text-gray-600
            focus:ring-2 focus:ring-cyan-500/50 focus:outline-none
            resize-y
            ${isValidJson ? 'border-gray-700' : 'border-red-500'}
          `}
        />
        {!isValidJson && (
          <div className="flex items-center gap-1 text-xs text-red-400">
            <AlertCircle className="w-3 h-3" />
            <span>Invalid JSON syntax</span>
          </div>
        )}
      </div>
    );
  }

  // No schema - show empty state
  if (!schema || !schema.properties || Object.keys(schema.properties).length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No schema available for this aspect.</p>
        <button
          onClick={onToggleRawJson}
          className="mt-2 text-cyan-400 hover:text-cyan-300 text-sm"
        >
          Switch to Raw JSON mode
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {Object.entries(schema.properties).map(([propName, propSchema]) => (
        <SchemaField
          key={propName}
          name={propName}
          path={propName}
          schema={propSchema}
          value={values[propName]}
          error={errors[propName]}
          required={requiredFields.has(propName)}
          onChange={onChange}
          depth={0}
        />
      ))}
    </div>
  );
}

export default SchemaForm;
