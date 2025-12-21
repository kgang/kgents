/**
 * RequestBuilder - Main container for the Postman-like request builder
 *
 * "Crafting an invocation, not filling out a form"
 *
 * Features:
 * - Tab-based navigation: Preview, Body, Headers, Export
 * - Schema-driven form generation
 * - Request preview with syntax highlighting
 * - Code export (cURL, fetch, etc.)
 * - Joy-inducing animations
 */

import { useCallback, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Trash2, Code2, FileJson } from 'lucide-react';
import { useMotionPreferences, Shimmer } from '@/components/joy';
import type { RequestBuilderProps } from './types';
import { REQUEST_BUILDER_TABS } from './types';
import { useRequestBuilder } from './useRequestBuilder';
import { RequestPreview } from './RequestPreview';
import { SchemaForm } from './SchemaForm';
import { HeadersEditor } from './HeadersEditor';
import { CodeExport } from './CodeExport';

// =============================================================================
// Tab Content Components
// =============================================================================

interface TabButtonProps {
  tab: (typeof REQUEST_BUILDER_TABS)[number];
  isActive: boolean;
  onClick: () => void;
}

function TabButton({ tab, isActive, onClick }: TabButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`
        relative flex-shrink-0 px-3 py-2 text-sm font-medium transition-colors
        ${isActive ? 'text-cyan-400' : 'text-gray-400 hover:text-gray-200'}
      `}
    >
      <span className="flex items-center gap-1.5">
        <span className="text-xs">{tab.icon}</span>
        <span>{tab.label}</span>
      </span>
      {isActive && (
        <motion.div
          layoutId="activeTab"
          className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        />
      )}
    </button>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function RequestBuilder({
  path,
  aspect,
  schema,
  observer,
  onObserverChange,
  onSend,
  density,
  examples = [],
  baseUrl = '',
}: RequestBuilderProps) {
  const { shouldAnimate } = useMotionPreferences();

  // Detect platform for keyboard shortcut display
  const isMac = typeof navigator !== 'undefined' && /Mac/.test(navigator.platform);
  const shortcutKey = isMac ? '⌘' : 'Ctrl';

  // Request builder state
  const builder = useRequestBuilder({
    path,
    aspect,
    schema,
    observer,
    baseUrl,
  });

  // Determine if this is a GET request (no body needed)
  const isGetRequest = aspect === 'manifest' || aspect === 'affordances';

  // Handle send
  const handleSend = useCallback(() => {
    if (!builder.validate()) {
      return;
    }
    const body = builder.getBody();
    onSend(body);
  }, [builder, onSend]);

  // Keyboard shortcut: Cmd/Ctrl + Enter to send
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault();
        if (builder.isValid && !builder.isLoading) {
          handleSend();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleSend, builder.isValid, builder.isLoading]);

  // Handle example selection
  const handleExampleClick = useCallback(
    (examplePayload: Record<string, unknown>) => {
      builder.loadExample(examplePayload);
      builder.setActiveTab('body');
    },
    [builder]
  );

  // Get request config for preview/export
  const requestConfig = useMemo(() => builder.getRequestConfig(), [builder]);

  // Render tab content
  const renderTabContent = () => {
    switch (builder.activeTab) {
      case 'preview':
        return (
          <RequestPreview
            config={requestConfig}
            onCopy={() => {
              const { url, method, headers, body } = requestConfig;
              const headerStr = headers
                .filter((h) => h.enabled)
                .map((h) => `${h.key}: ${h.value}`)
                .join('\n');
              const text = `${method} ${url}\n${headerStr}\n\n${body ? JSON.stringify(body, null, 2) : ''}`;
              navigator.clipboard.writeText(text);
            }}
          />
        );

      case 'body':
        return (
          <div className="p-4 space-y-4">
            {/* Examples section */}
            {examples.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Examples
                </h4>
                <div className="flex flex-wrap gap-2">
                  {examples.map((example, i) => (
                    <button
                      key={i}
                      onClick={() => handleExampleClick(example.payload || {})}
                      className="
                        px-3 py-1.5 text-sm rounded-lg
                        bg-gray-700/50 hover:bg-gray-600/50
                        text-gray-300 hover:text-white
                        transition-colors
                      "
                    >
                      {example.description || `Example ${i + 1}`}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Raw JSON toggle */}
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                Request Body
              </h4>
              <button
                onClick={builder.toggleRawJsonMode}
                className={`
                  flex items-center gap-1.5 px-2 py-1 text-xs rounded
                  transition-colors
                  ${
                    builder.rawJsonMode
                      ? 'bg-cyan-500/20 text-cyan-400'
                      : 'bg-gray-700/50 text-gray-400 hover:text-gray-200'
                  }
                `}
              >
                {builder.rawJsonMode ? (
                  <>
                    <FileJson className="w-3 h-3" />
                    <span>Raw JSON</span>
                  </>
                ) : (
                  <>
                    <Code2 className="w-3 h-3" />
                    <span>Form</span>
                  </>
                )}
              </button>
            </div>

            {/* Form or raw JSON */}
            {isGetRequest ? (
              <div className="text-sm text-gray-400 italic py-8 text-center">
                This aspect uses GET and does not require a request body.
              </div>
            ) : (
              <SchemaForm
                schema={schema?.request as import('./types').RequestSchema | undefined}
                values={builder.payload}
                errors={builder.validationErrors}
                onChange={builder.setFieldValue}
                rawJsonMode={builder.rawJsonMode}
                rawJson={builder.rawJson}
                onRawJsonChange={builder.setRawJson}
                onToggleRawJson={builder.toggleRawJsonMode}
              />
            )}
          </div>
        );

      case 'headers':
        return (
          <HeadersEditor
            observer={observer}
            customHeaders={builder.customHeaders}
            onObserverChange={onObserverChange}
            onCustomHeadersChange={(headers) => {
              // Clear and reset custom headers
              while (builder.customHeaders.length > 0) {
                builder.removeCustomHeader(0);
              }
              headers.forEach((h, i) => {
                builder.addCustomHeader();
                builder.updateCustomHeader(i, h);
              });
            }}
          />
        );

      case 'export':
        return <CodeExport config={requestConfig} observer={observer} />;

      default:
        return null;
    }
  };

  // Compact layout (mobile)
  if (density === 'compact') {
    return (
      <div className="flex flex-col h-full bg-gray-800/50 rounded-lg overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-3 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <span className="text-lg">🔧</span>
            <span className="text-sm font-medium text-white truncate max-w-[150px]">
              {path}:{aspect}
            </span>
          </div>
          <button
            onClick={handleSend}
            disabled={!builder.isValid}
            className={`
              flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium
              transition-colors
              ${
                builder.isValid
                  ? 'bg-cyan-600 hover:bg-cyan-500 text-white'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              }
            `}
          >
            <Send className="w-4 h-4" />
            <span>Send</span>
          </button>
        </div>

        {/* Tabs (scrollable on mobile) */}
        <div className="flex overflow-x-auto border-b border-gray-700 scrollbar-hide">
          {REQUEST_BUILDER_TABS.map((tab) => (
            <TabButton
              key={tab.id}
              tab={tab}
              isActive={builder.activeTab === tab.id}
              onClick={() => builder.setActiveTab(tab.id)}
            />
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto">{renderTabContent()}</div>
      </div>
    );
  }

  // Comfortable/Spacious layout
  return (
    <div className="flex flex-col h-full bg-gray-800/30 rounded-lg overflow-hidden">
      {/* Header - responsive: wraps to vertical on narrow widths */}
      <div className="flex flex-col gap-2 p-3 border-b border-gray-700/50">
        {/* Top row: method + URL (truncates) + Send button (never cut off) */}
        <div className="flex items-center gap-2">
          {/* Method badge - flex-shrink-0 to never compress */}
          <span
            className={`
              flex-shrink-0 px-2 py-0.5 text-xs font-bold rounded uppercase
              ${requestConfig.method === 'GET' ? 'bg-green-500/20 text-green-400' : 'bg-amber-500/20 text-amber-400'}
            `}
          >
            {requestConfig.method}
          </span>

          {/* URL - truncates with ellipsis when narrow */}
          <code className="flex-1 min-w-0 text-sm text-gray-300 truncate">
            {requestConfig.url}
          </code>

          {/* Action buttons - flex-shrink-0 to NEVER get cut off */}
          <div className="flex-shrink-0 flex items-center gap-1.5">
            <button
              onClick={builder.clear}
              title="Clear"
              className="
                p-1.5 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-700/50
                transition-colors
              "
            >
              <Trash2 className="w-4 h-4" />
            </button>

            <Shimmer active={builder.isLoading}>
              <button
                onClick={handleSend}
                disabled={!builder.isValid || builder.isLoading}
                title={`Send Request (${shortcutKey}+Enter)`}
                className={`
                  flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium
                  transition-all
                  ${
                    builder.isValid && !builder.isLoading
                      ? 'bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-500/20'
                      : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                  }
                `}
              >
                <Send className="w-4 h-4" />
                <span>Send</span>
              </button>
            </Shimmer>
          </div>
        </div>

        {/* Bottom row: path info - smaller, secondary */}
        <div className="text-xs text-gray-500 truncate">
          {path} → {aspect}
        </div>
      </div>

      {/* Tabs - scrollable when narrow */}
      <div className="flex overflow-x-auto border-b border-gray-700/50 scrollbar-hide">
        {REQUEST_BUILDER_TABS.map((tab) => (
          <TabButton
            key={tab.id}
            tab={tab}
            isActive={builder.activeTab === tab.id}
            onClick={() => builder.setActiveTab(tab.id)}
          />
        ))}
      </div>

      {/* Content with animation */}
      <div className="flex-1 overflow-auto">
        <AnimatePresence mode="wait">
          <motion.div
            key={builder.activeTab}
            initial={shouldAnimate ? { opacity: 0, y: 10 } : undefined}
            animate={{ opacity: 1, y: 0 }}
            exit={shouldAnimate ? { opacity: 0, y: -10 } : undefined}
            transition={{ duration: 0.15 }}
            className="h-full"
          >
            {renderTabContent()}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

export default RequestBuilder;
