/**
 * BooleanField - Toggle switch component
 *
 * For boolean values. Fidelity 0.85.
 *
 * @see spec/protocols/aspect-form-projection.md - Part IV
 */

import { motion } from 'framer-motion';
import type { FieldComponentProps } from '../ProjectedField';

export function BooleanField({
  field,
  value,
  onChange,
  onBlur,
  disabled = false,
}: FieldComponentProps) {
  const checked = value === true;

  return (
    <button
      id={field.name}
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => {
        onChange(!checked);
        onBlur?.();
      }}
      disabled={disabled}
      className={`
        relative inline-flex h-6 w-11 items-center rounded-full
        transition-colors duration-200 ease-in-out
        focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-gray-900
        disabled:opacity-50 disabled:cursor-not-allowed
        ${checked ? 'bg-cyan-600' : 'bg-gray-700'}
      `}
    >
      <span className="sr-only">{field.name}</span>
      <motion.span
        layout
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        className={`
          inline-block h-4 w-4 rounded-full bg-white shadow transform
          ${checked ? 'translate-x-6' : 'translate-x-1'}
        `}
      />
    </button>
  );
}

export default BooleanField;
