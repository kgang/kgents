/**
 * FileView — Display a file with syntax highlighting
 *
 * Fetches and displays file content when a file path is focused.
 * Uses PersonalityLoading and EmpathyError for loading/error states.
 */

import { useEffect, useState } from 'react';

import { EmpathyError } from '../../components/joy/EmpathyError';
import { PersonalityLoading } from '../../components/joy/PersonalityLoading';

import './FileView.css';

// =============================================================================
// Types
// =============================================================================

interface FileViewProps {
  path: string;
}

interface FileState {
  loading: boolean;
  error: string | null;
  content: string | null;
  language: string;
}

// =============================================================================
// Component
// =============================================================================

export function FileView({ path }: FileViewProps) {
  const [state, setState] = useState<FileState>({
    loading: true,
    error: null,
    content: null,
    language: getLanguageFromPath(path),
  });

  useEffect(() => {
    let cancelled = false;

    async function fetchFile() {
      setState((prev) => ({ ...prev, loading: true, error: null }));

      try {
        // Try to fetch from backend
        // TODO: Wire to actual file endpoint
        const response = await fetch(`/api/files/read?path=${encodeURIComponent(path)}`);

        if (!response.ok) {
          throw new Error(`File not found: ${path}`);
        }

        const data = await response.json();

        if (!cancelled) {
          setState({
            loading: false,
            error: null,
            content: data.content,
            language: getLanguageFromPath(path),
          });
        }
      } catch (err) {
        if (!cancelled) {
          setState({
            loading: false,
            error: err instanceof Error ? err.message : 'Failed to load file',
            content: null,
            language: getLanguageFromPath(path),
          });
        }
      }
    }

    fetchFile();

    return () => {
      cancelled = true;
    };
  }, [path]);

  if (state.loading) {
    return (
      <div className="file-view file-view--loading">
        <PersonalityLoading jewel="brain" action="reading" size="md" />
      </div>
    );
  }

  if (state.error) {
    return (
      <div className="file-view file-view--error">
        <EmpathyError type="notfound" title="File not accessible" subtitle={state.error} />
      </div>
    );
  }

  return (
    <div className="file-view">
      <header className="file-view__header">
        <span className="file-view__path">{path}</span>
        <span className="file-view__language">{state.language}</span>
      </header>

      <pre className="file-view__content">
        <code className={`language-${state.language}`}>{state.content}</code>
      </pre>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getLanguageFromPath(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase() || '';

  const languageMap: Record<string, string> = {
    ts: 'typescript',
    tsx: 'typescript',
    js: 'javascript',
    jsx: 'javascript',
    py: 'python',
    rs: 'rust',
    go: 'go',
    md: 'markdown',
    json: 'json',
    yaml: 'yaml',
    yml: 'yaml',
    css: 'css',
    html: 'html',
    sql: 'sql',
    sh: 'bash',
    bash: 'bash',
  };

  return languageMap[ext] || 'plaintext';
}
