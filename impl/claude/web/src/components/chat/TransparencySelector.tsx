/**
 * TransparencySelector — Dropdown for transparency level
 *
 * From spec/protocols/chat-web.md Part VII.2:
 * - Minimal: Reads silent, mutations require acknowledgment
 * - Approval: Reads silent, all writes need approval
 * - Detailed: Everything shown in full action panel
 *
 * "Reads can be silent; mutations must speak AND be heard."
 */

import { useState, useRef, useEffect } from 'react';
import type { TransparencyLevel } from '../../types/chat';
import './TransparencySelector.css';

// =============================================================================
// Types
// =============================================================================

export interface TransparencySelectorProps {
  /** Current transparency level */
  level: TransparencyLevel;
  /** Callback when level changes */
  onChange: (level: TransparencyLevel) => void;
  /** Optional label */
  label?: string;
  /** Disabled state */
  disabled?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const TRANSPARENCY_LEVELS: {
  value: TransparencyLevel;
  label: string;
  description: string;
  icon: string;
}[] = [
  {
    value: 'minimal',
    label: 'Minimal',
    description: 'Reads silent, mutations acknowledged',
    icon: '○',
  },
  {
    value: 'approval',
    label: 'Approval',
    description: 'Reads silent, writes require approval',
    icon: '◐',
  },
  {
    value: 'detailed',
    label: 'Detailed',
    description: 'Everything shown in action panel',
    icon: '●',
  },
];

// =============================================================================
// Main Component
// =============================================================================

export function TransparencySelector({
  level,
  onChange,
  label = 'Transparency',
  disabled = false,
}: TransparencySelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentLevel = TRANSPARENCY_LEVELS.find((l) => l.value === level) || TRANSPARENCY_LEVELS[1];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [isOpen]);

  // Close on Escape
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => {
        document.removeEventListener('keydown', handleEscape);
      };
    }
  }, [isOpen]);

  const handleToggle = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
    }
  };

  const handleSelect = (value: TransparencyLevel) => {
    onChange(value);
    setIsOpen(false);
  };

  return (
    <div className="transparency-selector" ref={dropdownRef}>
      {/* Label */}
      {label && (
        <label className="transparency-selector__label">
          {label}:
        </label>
      )}

      {/* Trigger Button */}
      <div className="transparency-selector__trigger-container">
        <button
          className={`transparency-selector__trigger ${disabled ? 'transparency-selector__trigger--disabled' : ''}`}
          onClick={handleToggle}
          disabled={disabled}
          aria-haspopup="listbox"
          aria-expanded={isOpen}
          aria-label={`Transparency level: ${currentLevel.label}`}
        >
          <span className="transparency-selector__icon">
            {currentLevel.icon}
          </span>
          <span className="transparency-selector__value">
            {currentLevel.label}
          </span>
          <span className="transparency-selector__arrow">
            {isOpen ? '▲' : '▼'}
          </span>
        </button>

        {/* Dropdown Menu */}
        {isOpen && (
          <div
            className="transparency-selector__dropdown"
            role="listbox"
            aria-label="Transparency level options"
          >
            {TRANSPARENCY_LEVELS.map((item) => {
              const isSelected = item.value === level;

              return (
                <button
                  key={item.value}
                  className={`transparency-selector__option ${isSelected ? 'transparency-selector__option--selected' : ''}`}
                  onClick={() => handleSelect(item.value)}
                  role="option"
                  aria-selected={isSelected}
                  tabIndex={0}
                >
                  <div className="transparency-selector__option-header">
                    <span className="transparency-selector__option-icon">
                      {item.icon}
                    </span>
                    <span className="transparency-selector__option-label">
                      {item.label}
                    </span>
                    {isSelected && (
                      <span className="transparency-selector__checkmark">●</span>
                    )}
                  </div>
                  <div className="transparency-selector__option-description">
                    {item.description}
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default TransparencySelector;
