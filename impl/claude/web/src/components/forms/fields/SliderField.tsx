/**
 * SliderField - Slider for bounded numbers
 *
 * For numbers with both min AND max defined. Fidelity 0.90.
 *
 * @see spec/protocols/aspect-form-projection.md - Part IV
 */

import type { FieldComponentProps } from '../ProjectedField';

export function SliderField({
  field,
  value,
  onChange,
  onBlur,
  error,
  disabled = false,
}: FieldComponentProps) {
  const min = field.min ?? 0;
  const max = field.max ?? 100;
  const numValue = value === undefined || value === null ? min : Number(value);

  // Calculate percentage for gradient
  const percentage = ((numValue - min) / (max - min)) * 100;

  return (
    <div className="space-y-2">
      {/* Slider */}
      <div className="flex items-center gap-3">
        <input
          id={field.name}
          name={field.name}
          type="range"
          value={numValue}
          onChange={(e) => {
            const num =
              field.type === 'integer' ? parseInt(e.target.value, 10) : parseFloat(e.target.value);
            onChange(num);
          }}
          onBlur={onBlur}
          disabled={disabled}
          min={min}
          max={max}
          step={field.type === 'integer' ? 1 : (max - min) / 100}
          aria-invalid={!!error}
          aria-describedby={error ? `${field.name}-error` : undefined}
          className={`
            flex-1 h-2 rounded-full appearance-none cursor-pointer
            disabled:opacity-50 disabled:cursor-not-allowed
            ${error ? 'accent-red-500' : 'accent-cyan-500'}
          `}
          style={{
            background: `linear-gradient(to right, rgb(6, 182, 212) 0%, rgb(6, 182, 212) ${percentage}%, rgb(55, 65, 81) ${percentage}%, rgb(55, 65, 81) 100%)`,
          }}
        />

        {/* Value display */}
        <span className="w-12 text-right text-sm text-gray-300 font-mono">
          {field.type === 'integer' ? numValue : numValue.toFixed(2)}
        </span>
      </div>

      {/* Min/Max labels */}
      <div className="flex justify-between text-xs text-gray-500">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}

export default SliderField;
