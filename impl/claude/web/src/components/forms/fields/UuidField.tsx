/**
 * UuidField - UUID input with generate button
 *
 * For fields with format 'uuid'. Fidelity 0.95.
 * Includes a "Generate" button for developer convenience.
 *
 * @see spec/protocols/aspect-form-projection.md - Part IV
 */

import { useCallback } from 'react';
import { generateUUID } from '@/lib/schema/generateDefaults';
import type { FieldComponentProps } from '../ProjectedField';

export function UuidField({
  field,
  value,
  onChange,
  onBlur,
  error,
  disabled = false,
  archetype,
}: FieldComponentProps) {
  const stringValue = value === undefined || value === null ? '' : String(value);

  // Generate new UUID
  const handleGenerate = useCallback(() => {
    onChange(generateUUID());
    onBlur?.();
  }, [onChange, onBlur]);

  return (
    <div className="flex gap-2">
      <input
        id={field.name}
        name={field.name}
        type="text"
        value={stringValue}
        onChange={(e) => onChange(e.target.value)}
        onBlur={onBlur}
        disabled={disabled}
        placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        pattern="[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
        aria-invalid={!!error}
        aria-describedby={error ? `${field.name}-error` : undefined}
        className={`
          flex-1 px-3 py-2 bg-gray-800 border rounded-lg
          text-white placeholder-gray-500 font-mono text-sm
          focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-colors
          ${error ? 'border-red-500' : 'border-gray-700 hover:border-gray-600'}
        `}
      />

      {/* Generate button */}
      <button
        type="button"
        onClick={handleGenerate}
        disabled={disabled}
        title={archetype === 'developer' ? 'Generate UUID v4' : 'Generate a unique ID'}
        className="
          px-3 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300
          rounded-lg transition-colors
          disabled:opacity-50 disabled:cursor-not-allowed
          text-sm whitespace-nowrap
        "
      >
        {archetype === 'developer' ? 'Gen UUID' : 'Generate'}
      </button>
    </div>
  );
}

export default UuidField;
