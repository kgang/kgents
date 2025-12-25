/**
 * SelectWidget: Single/multi select component.
 *
 * Features:
 * - Single or multiple selection
 * - Searchable options
 * - Keyboard navigation
 * - Clear selection
 */

import React, { useState, useMemo, useRef, useEffect } from 'react';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
  group?: string;
}

export interface SelectWidgetProps {
  options: SelectOption[];
  /** Currently selected value(s) */
  value?: string | string[];
  /** Allow multiple selection */
  multiple?: boolean;
  /** Enable search/filter */
  searchable?: boolean;
  /** Placeholder text */
  placeholder?: string;
  /** Disabled state */
  disabled?: boolean;
  /** Change callback */
  onChange?: (value: string | string[]) => void;
}

export function SelectWidget({
  options,
  value,
  multiple = false,
  searchable = false,
  placeholder = 'Select...',
  disabled = false,
  onChange,
}: SelectWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Normalize selected values
  const selected = useMemo(() => {
    if (!value) return new Set<string>();
    return new Set(Array.isArray(value) ? value : [value]);
  }, [value]);

  // Filter options by search
  const filteredOptions = useMemo(() => {
    if (!search) return options;
    const lower = search.toLowerCase();
    return options.filter(
      (opt) =>
        opt.label.toLowerCase().includes(lower) || opt.value.toLowerCase().includes(lower)
    );
  }, [options, search]);

  // Group options
  const groupedOptions = useMemo(() => {
    const groups: Record<string, SelectOption[]> = { '': [] };
    for (const opt of filteredOptions) {
      const group = opt.group || '';
      if (!groups[group]) groups[group] = [];
      groups[group].push(opt);
    }
    return groups;
  }, [filteredOptions]);

  // Close on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setSearch('');
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleSelect = (optValue: string) => {
    if (multiple) {
      const newSelected = new Set(selected);
      if (newSelected.has(optValue)) {
        newSelected.delete(optValue);
      } else {
        newSelected.add(optValue);
      }
      onChange?.(Array.from(newSelected));
    } else {
      onChange?.(optValue);
      setIsOpen(false);
      setSearch('');
    }
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange?.(multiple ? [] : '');
  };

  const displayValue = useMemo(() => {
    if (selected.size === 0) return placeholder;
    if (selected.size === 1) {
      const opt = options.find((o) => selected.has(o.value));
      return opt?.label || Array.from(selected)[0];
    }
    return `${selected.size} selected`;
  }, [selected, options, placeholder]);

  return (
    <div
      ref={containerRef}
      className="kgents-select-widget"
      style={{
        position: 'relative',
        width: '100%',
      }}
    >
      {/* Trigger */}
      <div
        onClick={() => !disabled && setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '8px 12px',
          border: '1px solid #d1d5db',
          borderRadius: '6px',
          backgroundColor: disabled ? '#f3f4f6' : 'white',
          cursor: disabled ? 'not-allowed' : 'pointer',
          color: selected.size === 0 ? '#9ca3af' : '#1f2937',
        }}
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-disabled={disabled}
      >
        <span style={{ flex: 1 }}>{displayValue}</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          {selected.size > 0 && !disabled && (
            <button
              onClick={handleClear}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '2px',
                fontSize: '12px',
                color: '#6b7280',
              }}
              aria-label="Clear selection"
            >
              ×
            </button>
          )}
          <span style={{ fontSize: '10px', color: '#6b7280' }}>{isOpen ? '▲' : '▼'}</span>
        </div>
      </div>

      {/* Dropdown */}
      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            marginTop: '4px',
            backgroundColor: 'white',
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            zIndex: 50,
            maxHeight: '240px',
            overflowY: 'auto',
          }}
          role="listbox"
          aria-multiselectable={multiple}
        >
          {/* Search input */}
          {searchable && (
            <div style={{ padding: '8px', borderBottom: '1px solid #e5e7eb' }}>
              <input
                ref={inputRef}
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search..."
                style={{
                  width: '100%',
                  padding: '6px 8px',
                  border: '1px solid #d1d5db',
                  borderRadius: '4px',
                  fontSize: '14px',
                  outline: 'none',
                }}
                autoFocus
              />
            </div>
          )}

          {/* Options */}
          {Object.entries(groupedOptions).map(([group, opts]) => (
            <div key={group}>
              {group && (
                <div
                  style={{
                    padding: '6px 12px',
                    fontSize: '11px',
                    fontWeight: 600,
                    color: '#6b7280',
                    textTransform: 'uppercase',
                    backgroundColor: '#f9fafb',
                  }}
                >
                  {group}
                </div>
              )}
              {opts.map((opt) => {
                const isSelected = selected.has(opt.value);
                return (
                  <div
                    key={opt.value}
                    onClick={() => !opt.disabled && handleSelect(opt.value)}
                    style={{
                      padding: '8px 12px',
                      cursor: opt.disabled ? 'not-allowed' : 'pointer',
                      backgroundColor: isSelected ? '#eff6ff' : 'transparent',
                      color: opt.disabled ? '#9ca3af' : '#1f2937',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                    }}
                    role="option"
                    aria-selected={isSelected}
                    aria-disabled={opt.disabled}
                  >
                    {multiple && (
                      <input
                        type="checkbox"
                        checked={isSelected}
                        disabled={opt.disabled}
                        readOnly
                        style={{ pointerEvents: 'none' }}
                      />
                    )}
                    <span>{opt.label}</span>
                    {!multiple && isSelected && (
                      <span style={{ marginLeft: 'auto', color: '#3b82f6' }}>●</span>
                    )}
                  </div>
                );
              })}
            </div>
          ))}

          {filteredOptions.length === 0 && (
            <div style={{ padding: '12px', textAlign: 'center', color: '#9ca3af' }}>
              No options found
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SelectWidget;
