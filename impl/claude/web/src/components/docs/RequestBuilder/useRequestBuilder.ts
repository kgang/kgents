/**
 * useRequestBuilder - State management for the Request Builder
 *
 * Manages:
 * - Form values and validation
 * - Raw JSON mode toggle
 * - Custom headers
 * - Request configuration building
 * - Tab state
 */

import { useState, useCallback, useMemo, useEffect } from 'react';
import type { Observer } from '../ObserverPicker';
import type { AspectSchema } from '../useAgenteseDiscovery';
import type {
  RequestBuilderState,
  RequestBuilderTab,
  RequestConfig,
  HttpHeader,
  HttpMethod,
  JsonSchemaProperty,
} from './types';

// =============================================================================
// Validation
// =============================================================================

/**
 * Validate a single value against its JSON Schema.
 */
function validateValue(
  value: unknown,
  schema: JsonSchemaProperty,
  required: boolean
): string | null {
  // Required check
  if (required && (value === undefined || value === null || value === '')) {
    return 'This field is required';
  }

  // Skip further validation for empty optional fields
  if (value === undefined || value === null || value === '') {
    return null;
  }

  // Type-specific validation
  if (schema.type === 'string' && typeof value === 'string') {
    if (schema.minLength && value.length < schema.minLength) {
      return `Minimum ${schema.minLength} characters`;
    }
    if (schema.maxLength && value.length > schema.maxLength) {
      return `Maximum ${schema.maxLength} characters`;
    }
    if (schema.pattern) {
      const regex = new RegExp(schema.pattern);
      if (!regex.test(value)) {
        return `Does not match pattern: ${schema.pattern}`;
      }
    }
    if (schema.enum && !schema.enum.includes(value)) {
      return `Must be one of: ${schema.enum.join(', ')}`;
    }
  }

  if ((schema.type === 'number' || schema.type === 'integer') && typeof value === 'number') {
    if (schema.minimum !== undefined && value < schema.minimum) {
      return `Minimum value is ${schema.minimum}`;
    }
    if (schema.maximum !== undefined && value > schema.maximum) {
      return `Maximum value is ${schema.maximum}`;
    }
    if (schema.type === 'integer' && !Number.isInteger(value)) {
      return 'Must be an integer';
    }
  }

  return null;
}

/**
 * Recursively validate all fields in the payload.
 */
function validatePayload(
  payload: Record<string, unknown>,
  schema: { properties?: Record<string, JsonSchemaProperty>; required?: string[] } | undefined
): Record<string, string> {
  const errors: Record<string, string> = {};

  if (!schema?.properties) {
    return errors;
  }

  const requiredFields = new Set(schema.required || []);

  for (const [key, propSchema] of Object.entries(schema.properties)) {
    const value = payload[key];
    const isRequired = requiredFields.has(key);

    const error = validateValue(value, propSchema, isRequired);
    if (error) {
      errors[key] = error;
    }

    // Recursively validate nested objects
    if (
      propSchema.type === 'object' &&
      propSchema.properties &&
      typeof value === 'object' &&
      value !== null
    ) {
      const nestedErrors = validatePayload(value as Record<string, unknown>, propSchema);
      for (const [nestedKey, nestedError] of Object.entries(nestedErrors)) {
        errors[`${key}.${nestedKey}`] = nestedError;
      }
    }
  }

  return errors;
}

// =============================================================================
// Hook
// =============================================================================

export interface UseRequestBuilderOptions {
  path: string;
  aspect: string;
  schema?: AspectSchema;
  observer: Observer;
  baseUrl?: string;
}

export interface UseRequestBuilderReturn extends RequestBuilderState {
  /** Set active tab */
  setActiveTab: (tab: RequestBuilderTab) => void;
  /** Set a field value (supports dot notation for nested fields) */
  setFieldValue: (path: string, value: unknown) => void;
  /** Set the entire payload */
  setPayload: (payload: Record<string, unknown>) => void;
  /** Toggle raw JSON mode */
  toggleRawJsonMode: () => void;
  /** Update raw JSON string */
  setRawJson: (json: string) => void;
  /** Add a custom header */
  addCustomHeader: () => void;
  /** Update a custom header */
  updateCustomHeader: (index: number, header: Partial<HttpHeader>) => void;
  /** Remove a custom header */
  removeCustomHeader: (index: number) => void;
  /** Clear all form state */
  clear: () => void;
  /** Load example payload */
  loadExample: (payload: Record<string, unknown>) => void;
  /** Get the full request configuration */
  getRequestConfig: () => RequestConfig;
  /** Validate current payload */
  validate: () => boolean;
  /** Get the request body (handles raw JSON mode) */
  getBody: () => unknown;
}

export function useRequestBuilder({
  path,
  aspect,
  schema,
  observer,
  baseUrl = '',
}: UseRequestBuilderOptions): UseRequestBuilderReturn {
  // State
  const [activeTab, setActiveTab] = useState<RequestBuilderTab>('body');
  const [payload, setPayloadState] = useState<Record<string, unknown>>({});
  const [rawJsonMode, setRawJsonMode] = useState(false);
  const [rawJson, setRawJson] = useState('{}');
  const [customHeaders, setCustomHeaders] = useState<HttpHeader[]>([]);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [isLoading] = useState(false);

  // Determine HTTP method based on aspect
  const method: HttpMethod = useMemo(() => {
    // manifest and affordances are GET
    if (aspect === 'manifest' || aspect === 'affordances') {
      return 'GET';
    }
    // Everything else is POST (mutations, queries with params)
    return 'POST';
  }, [aspect]);

  // Build URL
  const url = useMemo(() => {
    const pathSegments = path.replace(/\./g, '/');
    return `${baseUrl}/agentese/${pathSegments}/${aspect}`;
  }, [baseUrl, path, aspect]);

  // Check if form is valid
  const isValid = useMemo(() => {
    if (rawJsonMode) {
      try {
        JSON.parse(rawJson);
        return true;
      } catch {
        return false;
      }
    }
    return Object.keys(validationErrors).length === 0;
  }, [rawJsonMode, rawJson, validationErrors]);

  // Initialize payload from schema defaults
  useEffect(() => {
    if (!schema?.request?.properties) return;

    const defaults: Record<string, unknown> = {};
    for (const [key, prop] of Object.entries(
      schema.request.properties as Record<string, JsonSchemaProperty>
    )) {
      if (prop.default !== undefined) {
        defaults[key] = prop.default;
      }
    }
    if (Object.keys(defaults).length > 0) {
      setPayloadState((prev) => ({ ...defaults, ...prev }));
    }
  }, [schema]);

  // Validate on payload change
  useEffect(() => {
    if (!rawJsonMode && schema?.request) {
      const errors = validatePayload(payload, schema.request);
      setValidationErrors(errors);
    }
  }, [payload, schema, rawJsonMode]);

  // Set a single field value (supports dot notation)
  const setFieldValue = useCallback((fieldPath: string, value: unknown) => {
    setPayloadState((prev) => {
      const newPayload = { ...prev };
      const parts = fieldPath.split('.');
      let current: Record<string, unknown> = newPayload;

      for (let i = 0; i < parts.length - 1; i++) {
        const part = parts[i];
        if (!(part in current) || typeof current[part] !== 'object') {
          current[part] = {};
        }
        current = current[part] as Record<string, unknown>;
      }

      current[parts[parts.length - 1]] = value;
      return newPayload;
    });
  }, []);

  // Set entire payload
  const setPayload = useCallback((newPayload: Record<string, unknown>) => {
    setPayloadState(newPayload);
    // Also update raw JSON
    try {
      setRawJson(JSON.stringify(newPayload, null, 2));
    } catch {
      // Ignore serialization errors
    }
  }, []);

  // Toggle raw JSON mode
  const toggleRawJsonMode = useCallback(() => {
    if (!rawJsonMode) {
      // Switching to raw mode - serialize current payload
      try {
        setRawJson(JSON.stringify(payload, null, 2));
      } catch {
        setRawJson('{}');
      }
    } else {
      // Switching to form mode - parse raw JSON
      try {
        const parsed = JSON.parse(rawJson);
        if (typeof parsed === 'object' && parsed !== null) {
          setPayloadState(parsed);
        }
      } catch {
        // Keep current payload if parse fails
      }
    }
    setRawJsonMode(!rawJsonMode);
  }, [rawJsonMode, payload, rawJson]);

  // Custom header management
  const addCustomHeader = useCallback(() => {
    setCustomHeaders((prev) => [...prev, { key: '', value: '', enabled: true }]);
  }, []);

  const updateCustomHeader = useCallback((index: number, header: Partial<HttpHeader>) => {
    setCustomHeaders((prev) => prev.map((h, i) => (i === index ? { ...h, ...header } : h)));
  }, []);

  const removeCustomHeader = useCallback((index: number) => {
    setCustomHeaders((prev) => prev.filter((_, i) => i !== index));
  }, []);

  // Clear all state
  const clear = useCallback(() => {
    setPayloadState({});
    setRawJson('{}');
    setValidationErrors({});
    setCustomHeaders([]);
  }, []);

  // Load example
  const loadExample = useCallback((examplePayload: Record<string, unknown>) => {
    setPayloadState(examplePayload);
    try {
      setRawJson(JSON.stringify(examplePayload, null, 2));
    } catch {
      setRawJson('{}');
    }
    setValidationErrors({});
  }, []);

  // Get request body
  const getBody = useCallback((): unknown => {
    if (method === 'GET') {
      return undefined;
    }
    if (rawJsonMode) {
      try {
        return JSON.parse(rawJson);
      } catch {
        return undefined;
      }
    }
    return payload;
  }, [method, rawJsonMode, rawJson, payload]);

  // Build full request configuration
  const getRequestConfig = useCallback((): RequestConfig => {
    // Build headers list
    const headers: HttpHeader[] = [
      { key: 'Content-Type', value: 'application/json', enabled: true },
      { key: 'X-Observer-Archetype', value: observer.archetype, enabled: true },
      {
        key: 'X-Observer-Capabilities',
        value: observer.capabilities.join(','),
        enabled: observer.capabilities.length > 0,
      },
      ...customHeaders.filter((h) => h.enabled && h.key),
    ];

    const body = getBody();

    return {
      method,
      url,
      headers,
      body,
      bodyValid: body !== undefined || method === 'GET',
    };
  }, [method, url, observer, customHeaders, getBody]);

  // Manual validation
  const validate = useCallback((): boolean => {
    if (rawJsonMode) {
      try {
        JSON.parse(rawJson);
        return true;
      } catch {
        setValidationErrors({ _raw: 'Invalid JSON' });
        return false;
      }
    }
    if (schema?.request) {
      const errors = validatePayload(payload, schema.request);
      setValidationErrors(errors);
      return Object.keys(errors).length === 0;
    }
    return true;
  }, [rawJsonMode, rawJson, schema, payload]);

  return {
    // State
    activeTab,
    payload,
    rawJsonMode,
    rawJson,
    customHeaders,
    validationErrors,
    isValid,
    isLoading,
    // Actions
    setActiveTab,
    setFieldValue,
    setPayload,
    toggleRawJsonMode,
    setRawJson,
    addCustomHeader,
    updateCustomHeader,
    removeCustomHeader,
    clear,
    loadExample,
    getRequestConfig,
    validate,
    getBody,
  };
}

export default useRequestBuilder;
