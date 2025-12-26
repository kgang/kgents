/**
 * Download Utilities
 *
 * File download helpers for crystal export functionality.
 */

/**
 * Download a file with the given content, filename, and MIME type.
 */
export function downloadFile(content: string, filename: string, type: string): void {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = filename;

  // Append to body, click, and cleanup
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  // Revoke the object URL after a short delay
  setTimeout(() => URL.revokeObjectURL(url), 100);
}

/**
 * Download content as a Markdown file.
 */
export function downloadMarkdown(content: string, filename: string): void {
  const fullFilename = filename.endsWith('.md') ? filename : `${filename}.md`;
  downloadFile(content, fullFilename, 'text/markdown;charset=utf-8');
}

/**
 * Download data as a JSON file.
 */
export function downloadJSON(data: unknown, filename: string): void {
  const fullFilename = filename.endsWith('.json') ? filename : `${filename}.json`;
  const content = JSON.stringify(data, null, 2);
  downloadFile(content, fullFilename, 'application/json;charset=utf-8');
}

/**
 * Copy text to clipboard with fallback for older browsers.
 * Returns true if successful, false otherwise.
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  // Try modern clipboard API first
  if (navigator.clipboard && navigator.clipboard.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // Fall through to fallback
    }
  }

  // Fallback for older browsers
  try {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    textarea.style.top = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();
    const success = document.execCommand('copy');
    document.body.removeChild(textarea);
    return success;
  } catch {
    return false;
  }
}
