/**
 * NumberField - Number input component
 *
 * For unbounded numbers. Fidelity 0.75.
 * Use SliderField for bounded numbers (has min AND max).
 *
 * @see spec/protocols/aspect-form-projection.md - Part IV
 */

import type { FieldComponentProps } from '../ProjectedField';

export function NumberField({
  field,
  value,
  onChange,
  onBlur,
  error,
  disabled = false,
}: FieldComponentProps) {
  const numValue = value === undefined || value === null || value === '' ? '' : Number(value);

  return (
    <input
      id={field.name}
      name={field.name}
      type="number"
      value={numValue}
      onChange={(e) => {
        const val = e.target.value;
        if (val === '') {
          onChange(undefined);
        } else {
          const num = field.type === 'integer' ? parseInt(val, 10) : parseFloat(val);
          onChange(isNaN(num) ? undefined : num);
        }
      }}
      onBlur={onBlur}
      disabled={disabled}
      min={field.min}
      max={field.max}
      step={field.type === 'integer' ? 1 : 'any'}
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

export default NumberField;
