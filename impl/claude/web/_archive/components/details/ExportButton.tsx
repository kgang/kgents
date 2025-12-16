/**
 * ExportButton: Download agent state as JSON.
 *
 * Supports multiple export formats and includes LOD-appropriate data.
 */

import { useState } from 'react';
import { cn } from '@/lib/utils';
import type { CitizenCardJSON } from '@/reactive/types';
import type { CitizenManifest } from '@/api/types';

export interface ExportButtonProps {
  citizen: CitizenCardJSON;
  manifest: CitizenManifest | null;
  className?: string;
}

type ExportFormat = 'json' | 'yaml' | 'csv';

export function ExportButton({ citizen, manifest, className }: ExportButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [format, setFormat] = useState<ExportFormat>('json');

  const handleExport = () => {
    const data = buildExportData(citizen, manifest);
    const content = formatData(data, format);
    const filename = `${citizen.name.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}.${format}`;
    downloadFile(content, filename, getMimeType(format));
    setIsOpen(false);
  };

  return (
    <div className={cn('relative', className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 text-sm bg-town-surface/50 hover:bg-town-surface rounded-lg border border-town-accent/30 transition-colors"
      >
        <span>📥</span>
        <span>Export</span>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />

          {/* Dropdown */}
          <div className="absolute bottom-full mb-2 left-0 z-50 bg-town-surface border border-town-accent/30 rounded-lg shadow-xl p-3 min-w-[200px]">
            <div className="text-xs text-gray-400 uppercase tracking-wide mb-2">Format</div>

            <div className="space-y-1 mb-3">
              {(['json', 'yaml', 'csv'] as ExportFormat[]).map((f) => (
                <button
                  key={f}
                  onClick={() => setFormat(f)}
                  className={cn(
                    'w-full text-left px-3 py-2 rounded transition-colors flex items-center justify-between',
                    format === f
                      ? 'bg-town-highlight/20 text-town-highlight'
                      : 'hover:bg-town-accent/20 text-gray-300'
                  )}
                >
                  <span className="uppercase text-sm">{f}</span>
                  {format === f && <span>✓</span>}
                </button>
              ))}
            </div>

            <button
              onClick={handleExport}
              className="w-full py-2 bg-town-highlight hover:bg-town-highlight/80 rounded-lg font-medium transition-colors"
            >
              Download
            </button>
          </div>
        </>
      )}
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function buildExportData(
  citizen: CitizenCardJSON,
  manifest: CitizenManifest | null
): Record<string, unknown> {
  return {
    exported_at: new Date().toISOString(),
    version: '1.0',
    citizen: {
      id: citizen.citizen_id,
      name: citizen.name,
      archetype: citizen.archetype,
      region: citizen.region,
      phase: citizen.phase,
      nphase: citizen.nphase,
      capability: citizen.capability,
      entropy: citizen.entropy,
      eigenvectors: citizen.eigenvectors ?? manifest?.eigenvectors ?? {},
      mood: manifest?.mood,
      cosmotechnics: manifest?.cosmotechnics,
      metaphor: manifest?.metaphor,
      relationships: manifest?.relationships ?? {},
      accursed_surplus: manifest?.accursed_surplus,
      opacity: manifest?.opacity,
    },
  };
}

function formatData(data: Record<string, unknown>, format: ExportFormat): string {
  switch (format) {
    case 'json':
      return JSON.stringify(data, null, 2);

    case 'yaml':
      return toYaml(data);

    case 'csv':
      return toCsv(data);

    default:
      return JSON.stringify(data, null, 2);
  }
}

function toYaml(obj: unknown, indent = 0): string {
  const spaces = '  '.repeat(indent);

  if (obj === null || obj === undefined) return 'null';
  if (typeof obj === 'string') return obj.includes('\n') ? `|\n${spaces}  ${obj.replace(/\n/g, `\n${spaces}  `)}` : obj;
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
        if (typeof value === 'object' && value !== null) {
          return `${spaces}${key}:\n${valStr}`;
        }
        return `${spaces}${key}: ${valStr}`;
      })
      .join('\n');
  }

  return String(obj);
}

function toCsv(data: Record<string, unknown>): string {
  const citizen = data.citizen as Record<string, unknown>;
  const rows: string[][] = [];

  // Header
  rows.push(['Property', 'Value']);

  // Flatten citizen data
  const flattenForCsv = (obj: Record<string, unknown>, prefix = '') => {
    for (const [key, value] of Object.entries(obj)) {
      const fullKey = prefix ? `${prefix}.${key}` : key;

      if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
        flattenForCsv(value as Record<string, unknown>, fullKey);
      } else {
        rows.push([fullKey, formatCsvValue(value)]);
      }
    }
  };

  flattenForCsv(citizen);

  // Convert to CSV string
  return rows.map((row) => row.map((cell) => `"${cell.replace(/"/g, '""')}"`).join(',')).join('\n');
}

function formatCsvValue(value: unknown): string {
  if (value === null || value === undefined) return '';
  if (Array.isArray(value)) return value.join('; ');
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

function getMimeType(format: ExportFormat): string {
  switch (format) {
    case 'json':
      return 'application/json';
    case 'yaml':
      return 'text/yaml';
    case 'csv':
      return 'text/csv';
    default:
      return 'text/plain';
  }
}

function downloadFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export default ExportButton;
