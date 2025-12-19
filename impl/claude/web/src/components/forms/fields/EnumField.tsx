/**
 * EnumField - Select dropdown for enum values
 *
 * For fields with enum constraint. Fidelity 0.90.
 *
 * @see spec/protocols/aspect-form-projection.md - Part IV
 */

import type { FieldComponentProps } from '../ProjectedField';

export function EnumField({
  field,
  value,
  onChange,
  onBlur,
  error,
  disabled = false,
}: FieldComponentProps) {
  const stringValue = value === undefined || value === null ? '' : String(value);
  const options = field.enum ?? [];

  return (
    <select
      id={field.name}
      name={field.name}
      value={stringValue}
      onChange={(e) => onChange(e.target.value || undefined)}
      onBlur={onBlur}
      disabled={disabled}
      aria-invalid={!!error}
      aria-describedby={error ? `${field.name}-error` : undefined}
      className={`
        w-full px-3 py-2 bg-gray-800 border rounded-lg
        text-white
        focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent
        disabled:opacity-50 disabled:cursor-not-allowed
        transition-colors cursor-pointer
        ${error ? 'border-red-500' : 'border-gray-700 hover:border-gray-600'}
      `}
    >
      {/* Placeholder option */}
      {!field.required && (
        <option value="" className="text-gray-500">
          Select an option...
        </option>
      )}

      {/* Enum options */}
      {options.map((option) => (
        <option key={option} value={option}>
          {humanize(option)}
        </option>
      ))}
    </select>
  );
}

/**
 * Convert snake_case/UPPER_CASE to Title Case.
 */
function humanize(text: string): string {
  return text
    .toLowerCase()
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default EnumField;
