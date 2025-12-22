/**
 * HeadersEditor - Edit observer and custom headers
 *
 * Sections:
 * 1. Observer Headers - Archetype dropdown, Capabilities multi-select
 * 2. Custom Headers - Add/remove key-value pairs
 *
 * The observer headers are the AGENTESE-specific headers that control
 * how the request is perceived by the backend.
 */

import { useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Trash2, Check, X } from 'lucide-react';
import type { HeadersEditorProps, HttpHeader } from './types';
import { OBSERVER_ARCHETYPES, OBSERVER_CAPABILITIES } from './types';

// =============================================================================
// Observer Header Section
// =============================================================================

interface ObserverSectionProps {
  archetype: string;
  capabilities: Set<string>;
  onArchetypeChange: (archetype: string) => void;
  onCapabilitiesChange: (capabilities: Set<string>) => void;
}

function ObserverSection({
  archetype,
  capabilities,
  onArchetypeChange,
  onCapabilitiesChange,
}: ObserverSectionProps) {
  const toggleCapability = useCallback(
    (cap: string) => {
      const newCaps = new Set(capabilities);
      if (newCaps.has(cap)) {
        newCaps.delete(cap);
      } else {
        newCaps.add(cap);
      }
      onCapabilitiesChange(newCaps);
    },
    [capabilities, onCapabilitiesChange]
  );

  return (
    <div className="space-y-4">
      <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
        Observer Headers
      </h4>

      <p className="text-xs text-gray-500">
        These headers control how AGENTESE perceives your request. Different observers see different
        aspects and have different affordances.
      </p>

      {/* Archetype */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-300">X-Observer-Archetype</label>
        <select
          value={archetype}
          onChange={(e) => onArchetypeChange(e.target.value)}
          className="
            w-full px-3 py-2 rounded-lg bg-gray-700/50 border border-gray-600
            text-white focus:ring-2 focus:ring-cyan-500/50 focus:outline-none
          "
        >
          {OBSERVER_ARCHETYPES.map((arch) => (
            <option key={arch} value={arch}>
              {arch}
            </option>
          ))}
        </select>
      </div>

      {/* Capabilities */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-300">X-Observer-Capabilities</label>
        <div className="flex flex-wrap gap-2">
          {OBSERVER_CAPABILITIES.map((cap) => {
            const isActive = capabilities.has(cap);
            return (
              <button
                key={cap}
                onClick={() => toggleCapability(cap)}
                className={`
                  flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm
                  transition-all border
                  ${
                    isActive
                      ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400'
                      : 'bg-gray-700/50 border-gray-600 text-gray-400 hover:text-gray-200'
                  }
                `}
              >
                {isActive && <Check className="w-3 h-3" />}
                <span>{cap}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Preview */}
      <div className="p-3 rounded-lg bg-gray-900/50 font-mono text-xs space-y-1">
        <div>
          <span className="text-pink-400">X-Observer-Archetype</span>
          <span className="text-gray-500">: </span>
          <span className="text-cyan-400">{archetype}</span>
        </div>
        {capabilities.size > 0 && (
          <div>
            <span className="text-pink-400">X-Observer-Capabilities</span>
            <span className="text-gray-500">: </span>
            <span className="text-green-400">{Array.from(capabilities).join(',')}</span>
          </div>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Custom Headers Section
// =============================================================================

interface CustomHeadersSectionProps {
  headers: HttpHeader[];
  onChange: (headers: HttpHeader[]) => void;
}

function CustomHeadersSection({ headers, onChange }: CustomHeadersSectionProps) {
  const addHeader = () => {
    onChange([...headers, { key: '', value: '', enabled: true }]);
  };

  const updateHeader = (index: number, updates: Partial<HttpHeader>) => {
    const newHeaders = headers.map((h, i) => (i === index ? { ...h, ...updates } : h));
    onChange(newHeaders);
  };

  const removeHeader = (index: number) => {
    onChange(headers.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
          Custom Headers
        </h4>
        <button
          onClick={addHeader}
          className="
            flex items-center gap-1.5 px-2 py-1 rounded text-sm
            text-cyan-400 hover:bg-cyan-500/10 transition-colors
          "
        >
          <Plus className="w-4 h-4" />
          <span>Add</span>
        </button>
      </div>

      {headers.length === 0 ? (
        <p className="text-xs text-gray-500 italic">No custom headers. Click "Add" to add one.</p>
      ) : (
        <div className="space-y-2">
          <AnimatePresence>
            {headers.map((header, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="flex items-center gap-2"
              >
                {/* Enable/disable toggle */}
                <button
                  onClick={() => updateHeader(index, { enabled: !header.enabled })}
                  className={`
                    p-1.5 rounded transition-colors
                    ${header.enabled ? 'text-green-400' : 'text-gray-500'}
                  `}
                >
                  {header.enabled ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                </button>

                {/* Key input */}
                <input
                  type="text"
                  value={header.key}
                  onChange={(e) => updateHeader(index, { key: e.target.value })}
                  placeholder="Header-Name"
                  className={`
                    flex-1 px-2 py-1.5 rounded bg-gray-700/50 border border-gray-600
                    text-sm font-mono text-white placeholder:text-gray-500
                    focus:ring-2 focus:ring-cyan-500/50 focus:outline-none
                    ${!header.enabled && 'opacity-50'}
                  `}
                />

                {/* Separator */}
                <span className="text-gray-500">:</span>

                {/* Value input */}
                <input
                  type="text"
                  value={header.value}
                  onChange={(e) => updateHeader(index, { value: e.target.value })}
                  placeholder="value"
                  className={`
                    flex-[2] px-2 py-1.5 rounded bg-gray-700/50 border border-gray-600
                    text-sm font-mono text-white placeholder:text-gray-500
                    focus:ring-2 focus:ring-cyan-500/50 focus:outline-none
                    ${!header.enabled && 'opacity-50'}
                  `}
                />

                {/* Delete button */}
                <button
                  onClick={() => removeHeader(index)}
                  className="
                    p-1.5 rounded text-gray-400 hover:text-red-400
                    hover:bg-red-500/10 transition-colors
                  "
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Common headers suggestions */}
      {headers.length === 0 && (
        <div className="pt-2">
          <p className="text-xs text-gray-500 mb-2">Common headers:</p>
          <div className="flex flex-wrap gap-2">
            {['Authorization', 'Accept', 'X-Request-ID'].map((name) => (
              <button
                key={name}
                onClick={() => onChange([...headers, { key: name, value: '', enabled: true }])}
                className="
                  px-2 py-1 rounded text-xs
                  bg-gray-700/50 text-gray-400 hover:text-gray-200
                  transition-colors
                "
              >
                {name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function HeadersEditor({
  observer,
  customHeaders,
  onObserverChange,
  onCustomHeadersChange,
}: HeadersEditorProps) {
  return (
    <div className="p-4 space-y-6">
      <ObserverSection
        archetype={observer.archetype}
        capabilities={new Set(observer.capabilities)}
        onArchetypeChange={(archetype) => onObserverChange({ ...observer, archetype })}
        onCapabilitiesChange={(capabilities) =>
          onObserverChange({ ...observer, capabilities: Array.from(capabilities) })
        }
      />

      <div className="border-t border-gray-700/50" />

      <CustomHeadersSection headers={customHeaders} onChange={onCustomHeadersChange} />
    </div>
  );
}

export default HeadersEditor;
