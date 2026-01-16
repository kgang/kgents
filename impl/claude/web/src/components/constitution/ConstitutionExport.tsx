/**
 * ConstitutionExport - Export dialog for personal constitution.
 *
 * Supports multiple formats:
 * - Markdown: Human-readable summary
 * - JSON: Machine-readable data
 * - Spec: kgents specification format
 *
 * Philosophy:
 *   "Export your discovered self. Share your axioms."
 *   The constitution should be portable and shareable.
 *
 * @see stores/personalConstitutionStore.ts
 */

import { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { ExportFormat, PersonalConstitution } from './types';
import { TIMING } from '@/constants';
import './ConstitutionExport.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionExportProps {
  /** The constitution to export */
  constitution: PersonalConstitution;

  /** Whether the dialog is open */
  isOpen: boolean;

  /** Callback to close the dialog */
  onClose: () => void;

  /** Callback to get export content */
  onExport: (format: ExportFormat) => string;

  /** Custom className */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

const FORMAT_INFO: Record<ExportFormat, { label: string; description: string; extension: string }> =
  {
    markdown: {
      label: 'Markdown',
      description: 'Human-readable document for sharing',
      extension: '.md',
    },
    json: {
      label: 'JSON',
      description: 'Machine-readable data for import/backup',
      extension: '.json',
    },
    spec: {
      label: 'Spec File',
      description: 'kgents specification format with metadata',
      extension: '.md',
    },
  };

// =============================================================================
// Sub-components
// =============================================================================

interface FormatSelectorProps {
  selected: ExportFormat;
  onChange: (format: ExportFormat) => void;
}

function FormatSelector({ selected, onChange }: FormatSelectorProps) {
  return (
    <div className="format-selector">
      {(Object.keys(FORMAT_INFO) as ExportFormat[]).map((format) => (
        <button
          key={format}
          className={`format-option ${selected === format ? 'selected' : ''}`}
          onClick={() => onChange(format)}
        >
          <span className="format-label">{FORMAT_INFO[format].label}</span>
          <span className="format-desc">{FORMAT_INFO[format].description}</span>
        </button>
      ))}
    </div>
  );
}

interface PreviewPaneProps {
  content: string;
  format: ExportFormat;
}

function PreviewPane({ content, format }: PreviewPaneProps) {
  const lines = content.split('\n').slice(0, 30);
  const isTruncated = content.split('\n').length > 30;

  return (
    <div className="preview-pane">
      <div className="preview-header">
        <span className="preview-title">Preview</span>
        <span className="preview-format">{FORMAT_INFO[format].extension}</span>
      </div>
      <pre className="preview-content">
        <code>{lines.join('\n')}</code>
        {isTruncated && <span className="preview-truncated">... (truncated)</span>}
      </pre>
    </div>
  );
}

interface StatsSummaryProps {
  constitution: PersonalConstitution;
}

function StatsSummary({ constitution }: StatsSummaryProps) {
  const totalAxioms =
    constitution.axioms.length + constitution.values.length + constitution.goals.length;

  return (
    <div className="stats-summary">
      <div className="stat">
        <span className="stat-value">{constitution.axioms.length}</span>
        <span className="stat-label">L0 Axioms</span>
      </div>
      <div className="stat">
        <span className="stat-value">{constitution.values.length}</span>
        <span className="stat-label">L1 Values</span>
      </div>
      <div className="stat">
        <span className="stat-value">{constitution.goals.length}</span>
        <span className="stat-label">L2 Goals</span>
      </div>
      <div className="stat total">
        <span className="stat-value">{totalAxioms}</span>
        <span className="stat-label">Total</span>
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function ConstitutionExport({
  constitution,
  isOpen,
  onClose,
  onExport,
  className = '',
}: ConstitutionExportProps) {
  const [format, setFormat] = useState<ExportFormat>('markdown');
  const [copied, setCopied] = useState(false);

  // Get export content
  const content = useMemo(() => {
    return onExport(format);
  }, [format, onExport]);

  // Copy to clipboard
  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [content]);

  // Download file
  const handleDownload = useCallback(() => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `my-constitution${FORMAT_INFO[format].extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [content, format]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="export-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Dialog */}
          <motion.div
            className={`constitution-export ${className}`}
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: TIMING.standard / 1000 }}
          >
            {/* Header */}
            <header className="export-header">
              <h2 className="export-title">Export Constitution</h2>
              <p className="export-subtitle">Share your discovered axioms</p>
              <button className="close-btn" onClick={onClose} aria-label="Close">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path
                    d="M6 6l8 8M14 6l-8 8"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                  />
                </svg>
              </button>
            </header>

            {/* Stats */}
            <StatsSummary constitution={constitution} />

            {/* Format Selection */}
            <div className="export-section">
              <h3 className="section-label">Format</h3>
              <FormatSelector selected={format} onChange={setFormat} />
            </div>

            {/* Preview */}
            <div className="export-section">
              <PreviewPane content={content} format={format} />
            </div>

            {/* Actions */}
            <footer className="export-actions">
              <button className="action-btn secondary" onClick={onClose}>
                Cancel
              </button>
              <button className={`action-btn copy ${copied ? 'copied' : ''}`} onClick={handleCopy}>
                {copied ? 'Copied!' : 'Copy to Clipboard'}
              </button>
              <button className="action-btn primary" onClick={handleDownload}>
                Download
              </button>
            </footer>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

export default ConstitutionExport;
