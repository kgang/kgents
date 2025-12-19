/**
 * DateField - Date/datetime input component
 *
 * For fields with format 'date' or 'date-time'. Fidelity 0.85.
 *
 * @see spec/protocols/aspect-form-projection.md - Part IV
 */

import type { FieldComponentProps } from '../ProjectedField';

export function DateField({
  field,
  value,
  onChange,
  onBlur,
  error,
  disabled = false,
}: FieldComponentProps) {
  // Determine input type based on format
  const isDateTime = field.format === 'date-time';
  const inputType = isDateTime ? 'datetime-local' : 'date';

  // Convert value to input format
  let inputValue = '';
  if (value) {
    const date = new Date(value as string);
    if (!isNaN(date.getTime())) {
      if (isDateTime) {
        // datetime-local expects: YYYY-MM-DDTHH:MM
        inputValue = date.toISOString().slice(0, 16);
      } else {
        // date expects: YYYY-MM-DD
        inputValue = date.toISOString().slice(0, 10);
      }
    }
  }

  return (
    <input
      id={field.name}
      name={field.name}
      type={inputType}
      value={inputValue}
      onChange={(e) => {
        const val = e.target.value;
        if (!val) {
          onChange(undefined);
        } else if (isDateTime) {
          // Convert to ISO string
          onChange(new Date(val).toISOString());
        } else {
          // Keep as YYYY-MM-DD
          onChange(val);
        }
      }}
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
        [&::-webkit-calendar-picker-indicator]:filter
        [&::-webkit-calendar-picker-indicator]:invert
        ${error ? 'border-red-500' : 'border-gray-700 hover:border-gray-600'}
      `}
    />
  );
}

export default DateField;
