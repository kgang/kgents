/**
 * CodeExport - Export request as code snippets
 *
 * Export formats:
 * - cURL command
 * - JavaScript fetch
 * - TypeScript axios
 * - Python requests
 * - Raw HTTP
 *
 * Each format has a copy button with success feedback.
 */

import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Copy, Check, Terminal, Code2, FileCode, FileText } from 'lucide-react';
import type { CodeExportProps, ExportFormat, RequestConfig } from './types';

// =============================================================================
// Code Generators
// =============================================================================

function generateCurl(config: RequestConfig): string {
  const lines: string[] = [];

  // Start with curl command
  lines.push(`curl -X ${config.method} '${config.url}' \\`);

  // Add headers
  for (const header of config.headers) {
    if (header.enabled && header.key) {
      lines.push(`  -H '${header.key}: ${header.value}' \\`);
    }
  }

  // Add body for non-GET
  if (config.body && config.method !== 'GET') {
    const bodyStr = JSON.stringify(config.body);
    lines.push(`  -d '${bodyStr}'`);
  } else {
    // Remove trailing backslash from last header
    if (lines.length > 1) {
      lines[lines.length - 1] = lines[lines.length - 1].replace(/ \\$/, '');
    }
  }

  return lines.join('\n');
}

function generateFetch(config: RequestConfig): string {
  const lines: string[] = [];

  lines.push(`const response = await fetch('${config.url}', {`);
  lines.push(`  method: '${config.method}',`);

  // Headers
  const enabledHeaders = config.headers.filter((h) => h.enabled && h.key);
  if (enabledHeaders.length > 0) {
    lines.push('  headers: {');
    enabledHeaders.forEach((h, i) => {
      const comma = i < enabledHeaders.length - 1 ? ',' : '';
      lines.push(`    '${h.key}': '${h.value}'${comma}`);
    });
    lines.push('  },');
  }

  // Body
  if (config.body && config.method !== 'GET') {
    lines.push(
      `  body: JSON.stringify(${JSON.stringify(config.body, null, 2).split('\n').join('\n  ')})`
    );
  }

  lines.push('});');
  lines.push('');
  lines.push('const data = await response.json();');
  lines.push('console.log(data);');

  return lines.join('\n');
}

function generateAxios(config: RequestConfig): string {
  const lines: string[] = [];

  lines.push("import axios from 'axios';");
  lines.push('');

  const method = config.method.toLowerCase();

  if (config.method === 'GET') {
    lines.push(`const response = await axios.${method}('${config.url}', {`);
  } else {
    lines.push(
      `const response = await axios.${method}('${config.url}', ${config.body ? JSON.stringify(config.body, null, 2) : '{}'}, {`
    );
  }

  // Headers
  const enabledHeaders = config.headers.filter((h) => h.enabled && h.key);
  if (enabledHeaders.length > 0) {
    lines.push('  headers: {');
    enabledHeaders.forEach((h, i) => {
      const comma = i < enabledHeaders.length - 1 ? ',' : '';
      lines.push(`    '${h.key}': '${h.value}'${comma}`);
    });
    lines.push('  }');
  }

  lines.push('});');
  lines.push('');
  lines.push('console.log(response.data);');

  return lines.join('\n');
}

function generatePython(config: RequestConfig): string {
  const lines: string[] = [];

  lines.push('import requests');
  lines.push('');

  // Headers
  const enabledHeaders = config.headers.filter((h) => h.enabled && h.key);
  lines.push('headers = {');
  enabledHeaders.forEach((h) => {
    lines.push(`    "${h.key}": "${h.value}",`);
  });
  lines.push('}');
  lines.push('');

  // Body for POST
  if (config.body && config.method !== 'GET') {
    lines.push(`payload = ${JSON.stringify(config.body, null, 4)}`);
    lines.push('');
  }

  // Request
  const method = config.method.toLowerCase();
  if (config.method === 'GET') {
    lines.push(`response = requests.${method}("${config.url}", headers=headers)`);
  } else {
    lines.push(`response = requests.${method}("${config.url}", headers=headers, json=payload)`);
  }
  lines.push('');
  lines.push('print(response.json())');

  return lines.join('\n');
}

function generateRawHttp(config: RequestConfig): string {
  const lines: string[] = [];

  // Request line
  const urlObj = new URL(config.url, 'http://localhost');
  lines.push(`${config.method} ${urlObj.pathname}${urlObj.search} HTTP/1.1`);
  lines.push(`Host: ${urlObj.host}`);

  // Headers
  for (const header of config.headers) {
    if (header.enabled && header.key) {
      lines.push(`${header.key}: ${header.value}`);
    }
  }

  // Body
  if (config.body && config.method !== 'GET') {
    lines.push('');
    lines.push(JSON.stringify(config.body, null, 2));
  }

  return lines.join('\n');
}

// =============================================================================
// Format Configuration
// =============================================================================

interface FormatConfig {
  id: ExportFormat;
  label: string;
  language: string;
  icon: React.ReactNode;
  generate: (config: RequestConfig) => string;
}

const FORMATS: FormatConfig[] = [
  {
    id: 'curl',
    label: 'cURL',
    language: 'bash',
    icon: <Terminal className="w-4 h-4" />,
    generate: generateCurl,
  },
  {
    id: 'fetch',
    label: 'Fetch',
    language: 'javascript',
    icon: <Code2 className="w-4 h-4" />,
    generate: generateFetch,
  },
  {
    id: 'axios',
    label: 'Axios',
    language: 'typescript',
    icon: <FileCode className="w-4 h-4" />,
    generate: generateAxios,
  },
  {
    id: 'python',
    label: 'Python',
    language: 'python',
    icon: <FileCode className="w-4 h-4" />,
    generate: generatePython,
  },
  {
    id: 'http',
    label: 'Raw HTTP',
    language: 'http',
    icon: <FileText className="w-4 h-4" />,
    generate: generateRawHttp,
  },
];

// =============================================================================
// Component
// =============================================================================

export function CodeExport({ config }: CodeExportProps) {
  const [activeFormat, setActiveFormat] = useState<ExportFormat>('curl');
  const [copied, setCopied] = useState(false);

  // Generate code for active format
  const code = useMemo(() => {
    const format = FORMATS.find((f) => f.id === activeFormat);
    return format ? format.generate(config) : '';
  }, [activeFormat, config]);

  // Handle copy
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      console.error('Failed to copy:', e);
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Format tabs */}
      <div className="flex items-center border-b border-gray-700/50 px-2">
        {FORMATS.map((format) => (
          <button
            key={format.id}
            onClick={() => setActiveFormat(format.id)}
            className={`
              flex items-center gap-1.5 px-3 py-2 text-sm
              transition-colors relative
              ${activeFormat === format.id ? 'text-cyan-400' : 'text-gray-400 hover:text-gray-200'}
            `}
          >
            {format.icon}
            <span className="hidden sm:inline">{format.label}</span>
            {activeFormat === format.id && (
              <motion.div
                layoutId="activeFormat"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"
              />
            )}
          </button>
        ))}

        {/* Spacer */}
        <div className="flex-1" />

        {/* Copy button */}
        <button
          onClick={handleCopy}
          className="
            flex items-center gap-1.5 px-3 py-1.5 rounded text-sm
            text-gray-400 hover:text-white hover:bg-gray-700/50
            transition-colors mr-2
          "
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 text-green-400" />
              <span className="text-green-400">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code content */}
      <div className="flex-1 overflow-auto p-4 bg-gray-900/50">
        <pre className="text-sm font-mono leading-relaxed">
          <code className="text-gray-200 whitespace-pre-wrap">{code}</code>
        </pre>
      </div>
    </div>
  );
}

export default CodeExport;
