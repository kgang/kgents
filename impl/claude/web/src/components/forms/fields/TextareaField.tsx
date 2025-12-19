/**
 * TextareaField - Multi-line text input component
 *
 * For longer text content (maxLength > 200). Fidelity 0.80.
 *
 * @see spec/protocols/aspect-form-projection.md - Part IV
 */

import type { FieldComponentProps } from '../ProjectedField';

export function TextareaField({
  field,
  value,
  onChange,
  onBlur,
  error,
  disabled = false,
}: FieldComponentProps) {
  const stringValue = value === undefined || value === null ? '' : String(value);

  // Calculate rows based on maxLength
  const rows = field.maxLength ? Math.min(Math.ceil(field.maxLength / 80), 10) : 4;

  return (
    <div className="relative">
      <textarea
        id={field.name}
        name={field.name}
        value={stringValue}
        onChange={(e) => onChange(e.target.value)}
        onBlur={onBlur}
        disabled={disabled}
        placeholder={field.description || undefined}
        maxLength={field.maxLength}
        rows={rows}
        aria-invalid={!!error}
        aria-describedby={error ? `${field.name}-error` : undefined}
        className={`
          w-full px-3 py-2 bg-gray-800 border rounded-lg
          text-white placeholder-gray-500
          focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent
          disabled:opacity-50 disabled:cursor-not-allowed
          resize-y min-h-[80px] transition-colors
          ${error ? 'border-red-500' : 'border-gray-700 hover:border-gray-600'}
        `}
      />

      {/* Character count */}
      {field.maxLength && (
        <div className="absolute bottom-2 right-2 text-xs text-gray-500">
          {stringValue.length} / {field.maxLength}
        </div>
      )}
    </div>
  );
}

export default TextareaField;
