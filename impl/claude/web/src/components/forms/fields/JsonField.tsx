/**
 * JsonField - Raw JSON editor (universal fallback)
 *
 * Lossless but not user-friendly. Fidelity 1.0 (always matches).
 * Used as fallback for complex/unknown field types.
 *
 * @see spec/protocols/aspect-form-projection.md - Part IV
 */

import { useState, useCallback } from 'react';
import type { FieldComponentProps } from '../ProjectedField';

export function JsonField({
  field,
  value,
  onChange,
  onBlur,
  error,
  disabled = false,
}: FieldComponentProps) {
  // Track JSON validity
  const [parseError, setParseError] = useState<string | null>(null);

  // Convert value to JSON string for editing
  const jsonString = value === undefined ? '' : JSON.stringify(value, null, 2);

  const handleChange = useCallback(
    (text: string) => {
      if (!text.trim()) {
        setParseError(null);
        onChange(undefined);
        return;
      }

      try {
        const parsed = JSON.parse(text);
        setParseError(null);
        onChange(parsed);
      } catch {
        setParseError('Invalid JSON');
        // Still update with raw text for recovery
      }
    },
    [onChange]
  );

  return (
    <div className="space-y-1">
      <textarea
        id={field.name}
        name={field.name}
        value={jsonString}
        onChange={(e) => handleChange(e.target.value)}
        onBlur={onBlur}
        disabled={disabled}
        rows={6}
        aria-invalid={!!error || !!parseError}
        aria-describedby={error ? `${field.name}-error` : undefined}
        className={`
          w-full px-3 py-2 bg-gray-800 border rounded-lg
          text-white font-mono text-sm
          focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent
          disabled:opacity-50 disabled:cursor-not-allowed
          resize-y min-h-[120px] transition-colors
          ${error || parseError ? 'border-red-500' : 'border-gray-700 hover:border-gray-600'}
        `}
        placeholder="{}"
      />

      {/* Parse error */}
      {parseError && !error && <p className="text-xs text-amber-400">⚠ {parseError}</p>}
    </div>
  );
}

export default JsonField;
