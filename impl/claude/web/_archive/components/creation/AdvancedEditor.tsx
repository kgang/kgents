/**
 * AdvancedEditor: JSON/YAML editor for power users.
 *
 * Direct editing of agent configuration with syntax highlighting
 * and validation feedback.
 */

import { useState, useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';
import type { Archetype, Eigenvectors } from '@/api/types';

export interface AdvancedEditorProps {
  config: {
    name: string;
    archetype: Archetype | null;
    eigenvectors: Partial<Eigenvectors>;
    region?: string;
  };
  onChange: (config: AdvancedEditorProps['config']) => void;
  onValidate?: (valid: boolean, errors?: string[]) => void;
  className?: string;
}

type EditorFormat = 'json' | 'yaml';

const DEFAULT_EIGENVECTORS: Eigenvectors = {
  warmth: 0.5,
  curiosity: 0.5,
  trust: 0.5,
  creativity: 0.5,
  patience: 0.5,
  resilience: 0.5,
  ambition: 0.5,
};

export function AdvancedEditor({
  config,
  onChange,
  onValidate,
  className,
}: AdvancedEditorProps) {
  const [format, setFormat] = useState<EditorFormat>('json');
  const [content, setContent] = useState('');
  const [errors, setErrors] = useState<string[]>([]);
  const [isDirty, setIsDirty] = useState(false);

  // Convert config to string on mount and format change
  useEffect(() => {
    const configObj = {
      name: config.name || '',
      archetype: config.archetype || 'Builder',
      eigenvectors: { ...DEFAULT_EIGENVECTORS, ...config.eigenvectors },
      region: config.region,
    };

    if (format === 'json') {
      setContent(JSON.stringify(configObj, null, 2));
    } else {
      setContent(toYaml(configObj));
    }
    setIsDirty(false);
  }, [format]);

  // Parse and validate content
  const validateAndUpdate = useCallback(() => {
    const validationErrors: string[] = [];
    let parsed: unknown = null;

    try {
      if (format === 'json') {
        parsed = JSON.parse(content);
      } else {
        parsed = parseYaml(content);
      }
    } catch (e) {
      validationErrors.push(`Parse error: ${(e as Error).message}`);
    }

    if (parsed && typeof parsed === 'object') {
      const obj = parsed as Record<string, unknown>;

      // Validate required fields
      if (!obj.name || typeof obj.name !== 'string') {
        validationErrors.push('Name is required and must be a string');
      }

      if (!obj.archetype || !isValidArchetype(obj.archetype as string)) {
        validationErrors.push('Archetype must be one of: Builder, Trader, Healer, Scholar, Watcher');
      }

      if (obj.eigenvectors) {
        const ev = obj.eigenvectors as Record<string, unknown>;
        const validKeys = ['warmth', 'curiosity', 'trust', 'creativity', 'patience', 'resilience', 'ambition'];
        for (const key of validKeys) {
          if (ev[key] !== undefined) {
            const val = ev[key] as number;
            if (typeof val !== 'number' || val < 0 || val > 1) {
              validationErrors.push(`eigenvectors.${key} must be a number between 0 and 1`);
            }
          }
        }
      }

      // If valid, update config
      if (validationErrors.length === 0) {
        onChange({
          name: obj.name as string,
          archetype: obj.archetype as Archetype,
          eigenvectors: obj.eigenvectors as Partial<Eigenvectors>,
          region: obj.region as string | undefined,
        });
      }
    }

    setErrors(validationErrors);
    onValidate?.(validationErrors.length === 0, validationErrors);
    setIsDirty(false);
  }, [content, format, onChange, onValidate]);

  // Debounced validation
  useEffect(() => {
    if (!isDirty) return;
    const timer = setTimeout(validateAndUpdate, 500);
    return () => clearTimeout(timer);
  }, [isDirty, validateAndUpdate]);

  const handleContentChange = (newContent: string) => {
    setContent(newContent);
    setIsDirty(true);
  };

  const handleFormat = () => {
    try {
      if (format === 'json') {
        const parsed = JSON.parse(content);
        setContent(JSON.stringify(parsed, null, 2));
      } else {
        const parsed = parseYaml(content);
        setContent(toYaml(parsed));
      }
      setErrors([]);
    } catch (e) {
      setErrors([`Format error: ${(e as Error).message}`]);
    }
  };

  const handleInsertTemplate = (template: string) => {
    const templates: Record<string, unknown> = {
      balanced: {
        name: 'NewCitizen',
        archetype: 'Builder',
        eigenvectors: DEFAULT_EIGENVECTORS,
      },
      explorer: {
        name: 'Explorer',
        archetype: 'Scholar',
        eigenvectors: {
          ...DEFAULT_EIGENVECTORS,
          curiosity: 0.9,
          creativity: 0.7,
          patience: 0.3,
        },
      },
      guardian: {
        name: 'Guardian',
        archetype: 'Watcher',
        eigenvectors: {
          ...DEFAULT_EIGENVECTORS,
          patience: 0.8,
          resilience: 0.9,
          trust: 0.6,
        },
      },
    };

    const templateObj = templates[template];
    if (templateObj) {
      if (format === 'json') {
        setContent(JSON.stringify(templateObj, null, 2));
      } else {
        setContent(toYaml(templateObj));
      }
      setIsDirty(true);
    }
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FormatToggle value={format} onChange={setFormat} />
          <button
            onClick={handleFormat}
            className="px-3 py-1 text-xs bg-town-surface/50 hover:bg-town-accent/30 rounded transition-colors"
            title="Format code"
          >
            ✨ Format
          </button>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Templates:</span>
          {['balanced', 'explorer', 'guardian'].map((t) => (
            <button
              key={t}
              onClick={() => handleInsertTemplate(t)}
              className="px-2 py-1 text-xs bg-town-surface/30 hover:bg-town-accent/20 rounded transition-colors capitalize"
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Editor */}
      <div className="relative">
        <textarea
          value={content}
          onChange={(e) => handleContentChange(e.target.value)}
          className={cn(
            'w-full h-80 bg-town-surface/30 border rounded-lg p-4 font-mono text-sm resize-none',
            'focus:outline-none focus:ring-2 focus:ring-town-highlight/50',
            errors.length > 0 ? 'border-red-500/50' : 'border-town-accent/30'
          )}
          spellCheck={false}
        />

        {/* Line numbers overlay */}
        <div className="absolute top-4 left-0 w-8 text-right pr-2 text-xs text-gray-600 font-mono pointer-events-none select-none">
          {content.split('\n').map((_, i) => (
            <div key={i}>{i + 1}</div>
          ))}
        </div>
      </div>

      {/* Validation Status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {errors.length === 0 ? (
            <span className="text-xs text-green-400 flex items-center gap-1">
              ✓ Valid configuration
            </span>
          ) : (
            <span className="text-xs text-red-400 flex items-center gap-1">
              ✗ {errors.length} error{errors.length > 1 ? 's' : ''}
            </span>
          )}
        </div>

        {isDirty && (
          <span className="text-xs text-yellow-400">Validating...</span>
        )}
      </div>

      {/* Error List */}
      {errors.length > 0 && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
          <h4 className="text-xs font-semibold text-red-400 mb-2">Validation Errors</h4>
          <ul className="text-xs text-red-300 space-y-1">
            {errors.map((err, i) => (
              <li key={i} className="flex items-start gap-2">
                <span>•</span>
                <span>{err}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Schema Reference */}
      <details className="text-xs text-gray-500">
        <summary className="cursor-pointer hover:text-gray-400">
          Schema Reference
        </summary>
        <pre className="mt-2 p-3 bg-town-surface/20 rounded-lg overflow-x-auto">
{`{
  "name": string,        // Required: citizen name
  "archetype": string,   // Required: Builder|Trader|Healer|Scholar|Watcher
  "eigenvectors": {
    "warmth": 0-1,       // Emotional warmth
    "curiosity": 0-1,    // Drive to explore
    "trust": 0-1,        // Openness to others
    "creativity": 0-1,   // Imaginative thinking
    "patience": 0-1,     // Tolerance for delay
    "resilience": 0-1,   // Recovery from setbacks
    "ambition": 0-1      // Drive to achieve
  },
  "region": string       // Optional: starting region
}`}
        </pre>
      </details>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

function FormatToggle({
  value,
  onChange,
}: {
  value: EditorFormat;
  onChange: (v: EditorFormat) => void;
}) {
  return (
    <div className="flex bg-town-surface/30 rounded-lg p-1">
      {(['json', 'yaml'] as EditorFormat[]).map((f) => (
        <button
          key={f}
          onClick={() => onChange(f)}
          className={cn(
            'px-3 py-1 text-xs font-medium rounded transition-colors uppercase',
            value === f ? 'bg-town-accent text-white' : 'text-gray-400 hover:text-white'
          )}
        >
          {f}
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function isValidArchetype(archetype: string): archetype is Archetype {
  return ['Builder', 'Trader', 'Healer', 'Scholar', 'Watcher'].includes(archetype);
}

function toYaml(obj: unknown, indent = 0): string {
  const spaces = '  '.repeat(indent);

  if (obj === null || obj === undefined) return 'null';
  if (typeof obj === 'string') return obj;
  if (typeof obj === 'number' || typeof obj === 'boolean') return String(obj);

  if (Array.isArray(obj)) {
    if (obj.length === 0) return '[]';
    return obj.map((item) => `${spaces}- ${toYaml(item, indent + 1).trimStart()}`).join('\n');
  }

  if (typeof obj === 'object') {
    const entries = Object.entries(obj as Record<string, unknown>);
    if (entries.length === 0) return '{}';
    return entries
      .map(([key, value]) => {
        const valStr = toYaml(value, indent + 1);
        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
          return `${spaces}${key}:\n${valStr}`;
        }
        return `${spaces}${key}: ${valStr}`;
      })
      .join('\n');
  }

  return String(obj);
}

function parseYaml(yaml: string): unknown {
  // Simple YAML parser (for basic nested objects)
  const lines = yaml.split('\n');
  const result: Record<string, unknown> = {};
  const stack: { obj: Record<string, unknown>; indent: number }[] = [{ obj: result, indent: -1 }];

  for (const line of lines) {
    if (!line.trim() || line.trim().startsWith('#')) continue;

    const match = line.match(/^(\s*)(\w+):\s*(.*)$/);
    if (!match) continue;

    const [, indentStr, key, value] = match;
    const indent = indentStr.length;

    // Pop stack to find parent
    while (stack.length > 1 && stack[stack.length - 1].indent >= indent) {
      stack.pop();
    }

    const parent = stack[stack.length - 1].obj;

    if (value) {
      // Parse value
      let parsed: unknown = value;
      if (value === 'null') parsed = null;
      else if (value === 'true') parsed = true;
      else if (value === 'false') parsed = false;
      else if (/^-?\d+\.?\d*$/.test(value)) parsed = parseFloat(value);
      else if (value.startsWith('"') && value.endsWith('"')) parsed = value.slice(1, -1);
      else if (value.startsWith("'") && value.endsWith("'")) parsed = value.slice(1, -1);

      parent[key] = parsed;
    } else {
      // Nested object
      parent[key] = {};
      stack.push({ obj: parent[key] as Record<string, unknown>, indent });
    }
  }

  return result;
}

export default AdvancedEditor;
