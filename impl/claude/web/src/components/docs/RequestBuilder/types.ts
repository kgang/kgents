/**
 * RequestBuilder Types
 *
 * TypeScript interfaces for the Postman-like AGENTESE Request Builder.
 */

import type { Observer } from '../ObserverPicker';
import type { AspectSchema } from '../useAgenteseDiscovery';

// =============================================================================
// Request State
// =============================================================================

/**
 * HTTP method for the request.
 * AGENTESE uses GET for manifest/affordances, POST for mutations.
 */
export type HttpMethod = 'GET' | 'POST';

/**
 * Active tab in the RequestBuilder.
 */
export type RequestBuilderTab = 'preview' | 'body' | 'headers' | 'export';

/**
 * Single header key-value pair.
 */
export interface HttpHeader {
  key: string;
  value: string;
  enabled: boolean;
}

/**
 * Complete request configuration.
 */
export interface RequestConfig {
  /** HTTP method */
  method: HttpMethod;
  /** Full URL (constructed from path + aspect) */
  url: string;
  /** All headers including observer headers */
  headers: HttpHeader[];
  /** Request body (for POST requests) */
  body: unknown;
  /** Whether body is valid JSON */
  bodyValid: boolean;
}

/**
 * State managed by useRequestBuilder hook.
 */
export interface RequestBuilderState {
  /** Currently active tab */
  activeTab: RequestBuilderTab;
  /** Current payload from form or raw JSON */
  payload: Record<string, unknown>;
  /** Raw JSON mode enabled */
  rawJsonMode: boolean;
  /** Raw JSON string when in raw mode */
  rawJson: string;
  /** Custom headers (beyond observer headers) */
  customHeaders: HttpHeader[];
  /** Form validation errors by field path */
  validationErrors: Record<string, string>;
  /** Whether the current form state is valid */
  isValid: boolean;
  /** Whether a request is in flight */
  isLoading: boolean;
}

// =============================================================================
// JSON Schema Types (for form generation)
// =============================================================================

/**
 * Subset of JSON Schema we support for form generation.
 */
export interface JsonSchemaProperty {
  type?: 'string' | 'number' | 'integer' | 'boolean' | 'array' | 'object';
  title?: string;
  description?: string;
  default?: unknown;
  enum?: (string | number)[];
  format?: string;
  minLength?: number;
  maxLength?: number;
  minimum?: number;
  maximum?: number;
  pattern?: string;
  items?: JsonSchemaProperty;
  properties?: Record<string, JsonSchemaProperty>;
  required?: string[];
  nullable?: boolean;
}

/**
 * Parsed JSON Schema for a request body.
 */
export interface RequestSchema {
  type: 'object';
  title?: string;
  description?: string;
  properties: Record<string, JsonSchemaProperty>;
  required: string[];
}

// =============================================================================
// Component Props
// =============================================================================

/**
 * Props for the main RequestBuilder component.
 */
export interface RequestBuilderProps {
  /** AGENTESE path (e.g., "self.memory") */
  path: string;
  /** Aspect to invoke (e.g., "capture") */
  aspect: string;
  /** JSON Schema for the request/response if available */
  schema?: AspectSchema;
  /** Current observer configuration */
  observer: Observer;
  /** Callback when observer changes */
  onObserverChange: (observer: Observer) => void;
  /** Callback when request is sent */
  onSend: (payload?: unknown) => void;
  /** Callback when request completes (with response or error) */
  onResponse?: (response: RequestResponse) => void;
  /** UI density mode */
  density: 'compact' | 'comfortable' | 'spacious';
  /** Examples from metadata for quick invocation */
  examples?: Array<{
    description?: string;
    payload?: Record<string, unknown>;
  }>;
  /** Base URL for the API */
  baseUrl?: string;
}

/**
 * Props for RequestPreview component.
 */
export interface RequestPreviewProps {
  config: RequestConfig;
  onCopy: () => void;
}

/**
 * Props for SchemaForm component.
 */
export interface SchemaFormProps {
  schema: RequestSchema | undefined;
  values: Record<string, unknown>;
  errors: Record<string, string>;
  onChange: (path: string, value: unknown) => void;
  rawJsonMode: boolean;
  rawJson: string;
  onRawJsonChange: (json: string) => void;
  onToggleRawJson: () => void;
}

/**
 * Props for individual schema form fields.
 */
export interface SchemaFieldProps {
  /** Property name */
  name: string;
  /** Full path for nested fields (e.g., "metadata.tags[0]") */
  path: string;
  /** JSON Schema for this field */
  schema: JsonSchemaProperty;
  /** Current value */
  value: unknown;
  /** Validation error if any */
  error?: string;
  /** Whether this field is required */
  required: boolean;
  /** Callback when value changes */
  onChange: (path: string, value: unknown) => void;
  /** Nesting depth for indentation */
  depth: number;
}

/**
 * Props for HeadersEditor component.
 */
export interface HeadersEditorProps {
  observer: Observer;
  customHeaders: HttpHeader[];
  onObserverChange: (observer: Observer) => void;
  onCustomHeadersChange: (headers: HttpHeader[]) => void;
}

/**
 * Props for CodeExport component.
 */
export interface CodeExportProps {
  config: RequestConfig;
  observer: Observer;
}

// =============================================================================
// Response Types
// =============================================================================

/**
 * Response from an AGENTESE invocation.
 */
export interface RequestResponse {
  /** Whether the request succeeded */
  success: boolean;
  /** Response data on success */
  data?: unknown;
  /** Error message on failure */
  error?: string;
  /** HTTP status code */
  status: number;
  /** Time taken in milliseconds */
  elapsed: number;
}

// =============================================================================
// Export Format Types
// =============================================================================

/**
 * Available code export formats.
 */
export type ExportFormat = 'curl' | 'fetch' | 'axios' | 'python' | 'http';

/**
 * Code snippet with language for syntax highlighting.
 */
export interface CodeSnippet {
  format: ExportFormat;
  label: string;
  language: string;
  code: string;
}

// =============================================================================
// Constants
// =============================================================================

/**
 * Observer archetypes available in the system.
 */
export const OBSERVER_ARCHETYPES = [
  'guest',
  'user',
  'developer',
  'mayor',
  'coalition',
  'void',
] as const;

/**
 * Observer capabilities that can be granted.
 */
export const OBSERVER_CAPABILITIES = ['read', 'write', 'admin'] as const;

/**
 * Tab configuration for the RequestBuilder.
 */
export const REQUEST_BUILDER_TABS: Array<{
  id: RequestBuilderTab;
  label: string;
  icon: string;
}> = [
  { id: 'preview', label: 'Preview', icon: '👁' },
  { id: 'body', label: 'Body', icon: '📝' },
  { id: 'headers', label: 'Headers', icon: '🏷' },
  { id: 'export', label: 'Export', icon: '📤' },
];
