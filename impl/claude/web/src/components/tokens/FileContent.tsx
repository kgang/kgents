/**
 * FileContent — Preview of file content
 *
 * Shows file content with syntax highlighting (if applicable).
 * Used when expanding file: resources in portal tokens.
 *
 * See spec/protocols/portal-resource-system.md §6.1
 */

import './tokens.css';

// =============================================================================
// Types
// =============================================================================

export interface FileContentProps {
  /** File content */
  content: string;
  /** File path (for language detection) */
  path?: string;
  /** Compact mode (shorter preview) */
  compact?: boolean;
}

// =============================================================================
// Component
// =============================================================================

/**
 * FileContent — File preview with syntax highlighting
 */
export function FileContent({ content, path, compact = false }: FileContentProps) {
  const maxLines = compact ? 10 : 50;
  const lines = content.split('\n');
  const displayLines = lines.slice(0, maxLines);
  const hasMore = lines.length > maxLines;

  // Detect language from file extension
  const language = path ? detectLanguage(path) : 'text';

  return (
    <div className="file-content">
      {path && (
        <div className="file-content__header">
          <code className="file-content__path">{path}</code>
          {language !== 'text' && (
            <span className="file-content__language">{language}</span>
          )}
        </div>
      )}

      <pre className="file-content__pre">
        <code className={`file-content__code file-content__code--${language}`}>
          {displayLines.join('\n')}
        </code>
      </pre>

      {hasMore && (
        <div className="file-content__footer">
          <span className="file-content__more">
            +{lines.length - maxLines} more lines
          </span>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Detect programming language from file path
 */
function detectLanguage(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase();

  const languageMap: Record<string, string> = {
    ts: 'typescript',
    tsx: 'typescript',
    js: 'javascript',
    jsx: 'javascript',
    py: 'python',
    md: 'markdown',
    json: 'json',
    yaml: 'yaml',
    yml: 'yaml',
    css: 'css',
    html: 'html',
    sh: 'shell',
    bash: 'shell',
    sql: 'sql',
    rs: 'rust',
    go: 'go',
    java: 'java',
    c: 'c',
    cpp: 'cpp',
    h: 'c',
    hpp: 'cpp',
  };

  return ext && ext in languageMap ? languageMap[ext] : 'text';
}

export default FileContent;
