/**
 * TextField - Single-line text input component
 *
 * The workhorse input for most string fields. Fidelity 0.75.
 *
 * @see spec/protocols/aspect-form-projection.md - Part IV
 */

import type { FieldComponentProps } from '../ProjectedField';

export function TextField({
  field,
  value,
  onChange,
  onBlur,
  error,
  disabled = false,
}: FieldComponentProps) {
  const stringValue = value === undefined || value === null ? '' : String(value);

  return (
    <input
      id={field.name}
      name={field.name}
      type="text"
      value={stringValue}
      onChange={(e) => onChange(e.target.value)}
      onBlur={onBlur}
      disabled={disabled}
      placeholder={field.description || undefined}
      maxLength={field.maxLength}
      pattern={field.pattern}
      aria-invalid={!!error}
      aria-describedby={error ? `${field.name}-error` : undefined}
      className={`
        w-full px-3 py-2 bg-gray-800 border rounded-lg
        text-white placeholder-gray-500
        focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent
        disabled:opacity-50 disabled:cursor-not-allowed
        transition-colors
        ${error ? 'border-red-500' : 'border-gray-700 hover:border-gray-600'}
      `}
    />
  );
}

export default TextField;
