/**
 * StateTab: Full polynomial state and memory contents.
 *
 * Power user view for inspecting raw agent state.
 */

import { useState } from 'react';
import { cn } from '@/lib/utils';
import type { CitizenCardJSON } from '@/reactive/types';
import type { CitizenManifest } from '@/api/types';

export interface StateTabProps {
  citizen: CitizenCardJSON;
  manifest: CitizenManifest | null;
  expanded?: boolean;
}

type ViewFormat = 'tree' | 'json' | 'table';

export function StateTab({ citizen, manifest, expanded = false }: StateTabProps) {
  const [format, setFormat] = useState<ViewFormat>('tree');
  const [searchQuery, setSearchQuery] = useState('');

  // Combine citizen and manifest data
  const fullState = {
    core: {
      name: citizen.name,
      citizen_id: citizen.citizen_id,
      archetype: citizen.archetype,
      region: citizen.region,
      phase: citizen.phase,
      nphase: citizen.nphase,
    },
    metrics: {
      capability: citizen.capability,
      entropy: citizen.entropy,
      accursed_surplus: manifest?.accursed_surplus,
    },
    eigenvectors: citizen.eigenvectors ?? manifest?.eigenvectors ?? {},
    relationships: manifest?.relationships ?? {},
    semantics: {
      mood: manifest?.mood,
      cosmotechnics: manifest?.cosmotechnics,
      metaphor: manifest?.metaphor,
    },
    opacity: manifest?.opacity,
  };

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <FormatSelector value={format} onChange={setFormat} />
        <input
          type="text"
          placeholder="Search state..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="bg-town-surface/30 border border-town-accent/30 rounded-lg px-3 py-1 text-sm w-40 focus:outline-none focus:border-town-highlight"
        />
      </div>

      {/* State View */}
      <div
        className={cn(
          'bg-town-surface/20 rounded-lg border border-town-accent/20 overflow-auto',
          expanded ? 'max-h-[500px]' : 'max-h-[300px]'
        )}
      >
        {format === 'tree' && (
          <TreeView data={fullState} searchQuery={searchQuery} />
        )}
        {format === 'json' && (
          <JsonView data={fullState} searchQuery={searchQuery} />
        )}
        {format === 'table' && (
          <TableView data={fullState} searchQuery={searchQuery} />
        )}
      </div>

      {/* Polynomial State Diagram */}
      {expanded && (
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
            Polynomial State Machine
          </h3>
          <PolynomialDiagram currentPhase={citizen.phase} />
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Controls
// =============================================================================

function FormatSelector({
  value,
  onChange,
}: {
  value: ViewFormat;
  onChange: (v: ViewFormat) => void;
}) {
  const options: { id: ViewFormat; label: string; icon: string }[] = [
    { id: 'tree', label: 'Tree', icon: '🌳' },
    { id: 'json', label: 'JSON', icon: '{ }' },
    { id: 'table', label: 'Table', icon: '📋' },
  ];

  return (
    <div className="flex gap-1 bg-town-surface/30 rounded-lg p-1">
      {options.map((opt) => (
        <button
          key={opt.id}
          onClick={() => onChange(opt.id)}
          className={cn(
            'px-2 py-1 text-xs font-medium rounded transition-colors',
            value === opt.id ? 'bg-town-accent text-white' : 'text-gray-400 hover:text-white'
          )}
        >
          {opt.icon}
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// Tree View
// =============================================================================

interface TreeViewProps {
  data: Record<string, unknown>;
  searchQuery: string;
}

function TreeView({ data, searchQuery }: TreeViewProps) {
  return (
    <div className="p-3 font-mono text-sm">
      <TreeNode name="state" value={data} depth={0} searchQuery={searchQuery} defaultOpen />
    </div>
  );
}

interface TreeNodeProps {
  name: string;
  value: unknown;
  depth: number;
  searchQuery: string;
  defaultOpen?: boolean;
}

function TreeNode({ name, value, depth, searchQuery, defaultOpen }: TreeNodeProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen ?? depth < 1);
  const isObject = value !== null && typeof value === 'object';
  const isArray = Array.isArray(value);

  const matches = searchQuery && name.toLowerCase().includes(searchQuery.toLowerCase());
  const indent = depth * 16;

  // Check if any children match
  const hasMatchingChildren =
    searchQuery &&
    isObject &&
    Object.entries(value as Record<string, unknown>).some(([k, v]) => {
      if (k.toLowerCase().includes(searchQuery.toLowerCase())) return true;
      if (typeof v === 'string' && v.toLowerCase().includes(searchQuery.toLowerCase())) return true;
      return false;
    });

  if (isObject) {
    const entries = Object.entries(value as Record<string, unknown>);

    return (
      <div>
        <div
          style={{ paddingLeft: indent }}
          className={cn(
            'flex items-center gap-1 py-0.5 cursor-pointer hover:bg-town-accent/10 rounded',
            matches && 'bg-yellow-500/20'
          )}
          onClick={() => setIsOpen(!isOpen)}
        >
          <span className="text-gray-500 w-4">{isOpen ? '▼' : '▶'}</span>
          <span className="text-purple-400">{name}</span>
          <span className="text-gray-500">
            {isArray ? `[${entries.length}]` : `{${entries.length}}`}
          </span>
        </div>
        {(isOpen || hasMatchingChildren) && (
          <div>
            {entries.map(([k, v]) => (
              <TreeNode
                key={k}
                name={k}
                value={v}
                depth={depth + 1}
                searchQuery={searchQuery}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  const valueStr = formatValue(value);
  const valueMatches =
    searchQuery && valueStr.toLowerCase().includes(searchQuery.toLowerCase());

  return (
    <div
      style={{ paddingLeft: indent }}
      className={cn(
        'flex items-center gap-2 py-0.5',
        (matches || valueMatches) && 'bg-yellow-500/20 rounded'
      )}
    >
      <span className="w-4" />
      <span className="text-blue-400">{name}</span>
      <span className="text-gray-500">:</span>
      <span className={getValueColor(value)}>{valueStr}</span>
    </div>
  );
}

// =============================================================================
// JSON View
// =============================================================================

interface JsonViewProps {
  data: Record<string, unknown>;
  searchQuery: string;
}

function JsonView({ data, searchQuery }: JsonViewProps) {
  const jsonStr = JSON.stringify(data, null, 2);

  // Highlight search matches
  const highlighted = searchQuery
    ? jsonStr.replace(
        new RegExp(`(${escapeRegex(searchQuery)})`, 'gi'),
        '<mark class="bg-yellow-500/40">$1</mark>'
      )
    : jsonStr;

  return (
    <pre
      className="p-3 text-xs overflow-auto whitespace-pre text-gray-300"
      dangerouslySetInnerHTML={{ __html: highlighted }}
    />
  );
}

// =============================================================================
// Table View
// =============================================================================

interface TableViewProps {
  data: Record<string, unknown>;
  searchQuery: string;
}

function TableView({ data, searchQuery }: TableViewProps) {
  const rows = flattenObject(data);
  const filtered = searchQuery
    ? rows.filter(
        ([path, value]) =>
          path.toLowerCase().includes(searchQuery.toLowerCase()) ||
          String(value).toLowerCase().includes(searchQuery.toLowerCase())
      )
    : rows;

  return (
    <table className="w-full text-sm">
      <thead className="bg-town-surface/30 sticky top-0">
        <tr>
          <th className="text-left p-2 text-gray-400 font-medium">Path</th>
          <th className="text-left p-2 text-gray-400 font-medium">Value</th>
        </tr>
      </thead>
      <tbody>
        {filtered.map(([path, value]) => {
          const pathMatches =
            searchQuery && path.toLowerCase().includes(searchQuery.toLowerCase());
          const valueMatches =
            searchQuery && String(value).toLowerCase().includes(searchQuery.toLowerCase());

          return (
            <tr key={path} className="border-t border-town-accent/10 hover:bg-town-accent/5">
              <td className={cn('p-2 font-mono text-xs', pathMatches && 'bg-yellow-500/20')}>
                {path}
              </td>
              <td
                className={cn(
                  'p-2 font-mono text-xs',
                  getValueColor(value),
                  valueMatches && 'bg-yellow-500/20'
                )}
              >
                {formatValue(value)}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

// =============================================================================
// Polynomial Diagram
// =============================================================================

function PolynomialDiagram({ currentPhase }: { currentPhase: string }) {
  const phases = ['IDLE', 'WORKING', 'SOCIALIZING', 'REFLECTING', 'RESTING'];

  return (
    <div className="bg-town-surface/20 rounded-lg p-4">
      <div className="flex items-center justify-between">
        {phases.map((phase, i) => {
          const isCurrent = phase === currentPhase;
          const isPast = phases.indexOf(currentPhase) > i;

          return (
            <div key={phase} className="flex items-center">
              {/* Node */}
              <div
                className={cn(
                  'w-10 h-10 rounded-full flex items-center justify-center text-xs font-medium transition-all',
                  isCurrent
                    ? 'bg-town-highlight text-white ring-2 ring-town-highlight ring-offset-2 ring-offset-town-bg'
                    : isPast
                      ? 'bg-green-500/30 text-green-400 border border-green-500/50'
                      : 'bg-town-surface border border-town-accent/30 text-gray-500'
                )}
              >
                {phase.slice(0, 2)}
              </div>

              {/* Arrow */}
              {i < phases.length - 1 && (
                <div className="w-8 flex items-center justify-center">
                  <div
                    className={cn(
                      'w-full h-0.5',
                      isPast ? 'bg-green-500/50' : 'bg-town-accent/30'
                    )}
                  />
                  <span className="text-gray-500 text-xs">→</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Phase label */}
      <div className="mt-4 text-center">
        <span className="text-sm text-gray-400">Current: </span>
        <span className="text-sm font-medium text-town-highlight">{currentPhase}</span>
      </div>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function formatValue(value: unknown): string {
  if (value === null) return 'null';
  if (value === undefined) return 'undefined';
  if (typeof value === 'string') return `"${value}"`;
  if (typeof value === 'number') return value.toFixed(value % 1 === 0 ? 0 : 3);
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  return String(value);
}

function getValueColor(value: unknown): string {
  if (value === null || value === undefined) return 'text-gray-500';
  if (typeof value === 'string') return 'text-green-400';
  if (typeof value === 'number') return 'text-yellow-400';
  if (typeof value === 'boolean') return 'text-blue-400';
  return 'text-gray-300';
}

function flattenObject(
  obj: Record<string, unknown>,
  prefix = ''
): [string, unknown][] {
  const result: [string, unknown][] = [];

  for (const [key, value] of Object.entries(obj)) {
    const path = prefix ? `${prefix}.${key}` : key;

    if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
      result.push(...flattenObject(value as Record<string, unknown>, path));
    } else {
      result.push([path, value]);
    }
  }

  return result;
}

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export default StateTab;
