/**
 * AGENTESE Docs Explorer - Phase 4 (Request Builder)
 *
 * A daring, observer-dependent API explorer that embodies AGENTESE philosophy.
 * Unlike Swagger (a form to fill), this is a world to explore.
 *
 * "Paths are PLACES, Aspects are ACTIONS"
 * - Left: Navigate contexts like a filesystem
 * - Middle: Request Builder + Response Viewer (split panel)
 * - Right: Aspect buttons for quick selection
 *
 * AD-010 Habitat Guarantee: No blank pages. Examples are one-click invocations.
 *
 * Phase 4 Additions:
 * - Postman-like Request Builder with schema-driven forms
 * - Request preview with syntax highlighting
 * - Code export (cURL, fetch, axios, Python)
 * - Headers editor (observer + custom)
 *
 * @see plans/openapi-projection-surface.md
 * @see plans/umwelt-visualization.md
 */

import { useState, useCallback, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Compass, Zap, ChevronDown, ChevronUp } from 'lucide-react';
import { useDesignPolynomial } from '@/hooks';
import { ElasticSplit } from '@/components/elastic';
import { BottomDrawer } from '@/components/elastic/BottomDrawer';
import { FloatingActions } from '@/components/elastic/FloatingActions';
import { useMotionPreferences } from '@/components/joy';

import { PathExplorer } from '@/components/docs/PathExplorer';
import { ObserverPicker, type Observer } from '@/components/docs/ObserverPicker';
import { AspectPanel } from '@/components/docs/AspectPanel';
import { ResponseViewer } from '@/components/docs/ResponseViewer';
import { GuidedTour } from '@/components/docs/GuidedTour';
import { useAgenteseDiscovery, type PathMetadata } from '@/components/docs/useAgenteseDiscovery';
import { UmweltProvider, useUmwelt } from '@/components/docs/umwelt';
import { RequestBuilder } from '@/components/docs/RequestBuilder';

/**
 * AGENTESE Docs Explorer - The main page component.
 *
 * "Does this feel like discovering a new world, or reading a manual?"
 */
export function AgenteseDocs() {
  return (
    <UmweltProvider>
      <AgenteseDocsInner />
    </UmweltProvider>
  );
}

/**
 * Inner component that uses the UmweltProvider context.
 */
function AgenteseDocsInner() {
  const { state: designState } = useDesignPolynomial();
  const { shouldAnimate } = useMotionPreferences();
  const { density } = designState;

  // Umwelt context for observer transitions
  const { triggerTransition } = useUmwelt();

  // Discovery data from AGENTESE
  const { paths, metadata, schemas, loading, error, refetch } = useAgenteseDiscovery();

  // Current state
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [selectedAspect, setSelectedAspect] = useState<string>('manifest');
  const [observer, setObserver] = useState<Observer>({
    archetype: 'developer',
    capabilities: ['read', 'write', 'admin'],
  });

  // Track previous observer for umwelt transitions
  const prevObserverRef = useRef<Observer>(observer);

  // Response state (from invocation)
  const [response, setResponse] = useState<{
    data: unknown;
    elapsed: number;
    status: 'idle' | 'loading' | 'success' | 'error';
    error?: string;
  }>({
    data: null,
    elapsed: 0,
    status: 'idle',
  });

  // Drawer state for mobile
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [activeDrawer, setActiveDrawer] = useState<'explorer' | 'aspects'>('explorer');

  // Collapsible section state for mobile
  const [requestExpanded, setRequestExpanded] = useState(true);

  // Get metadata for selected path
  const selectedMetadata: PathMetadata | undefined = selectedPath
    ? metadata[selectedPath]
    : undefined;

  // Get schema for selected path (all aspects)
  const selectedSchema = useMemo(() => {
    if (!selectedPath || !schemas[selectedPath]) return undefined;
    return schemas[selectedPath];
  }, [selectedPath, schemas]);

  // Handle path selection
  const handleSelectPath = useCallback((path: string) => {
    setSelectedPath(path);
    setSelectedAspect('manifest'); // Reset to manifest on path change
    setResponse({ data: null, elapsed: 0, status: 'idle' });
  }, []);

  // Handle observer change with umwelt transition
  const handleObserverChange = useCallback(
    (newObserver: Observer) => {
      // Trigger umwelt transition animation
      if (prevObserverRef.current.archetype !== newObserver.archetype) {
        triggerTransition(prevObserverRef.current, newObserver, metadata, density);
      }

      // Update observer state
      prevObserverRef.current = newObserver;
      setObserver(newObserver);
    },
    [triggerTransition, metadata, density]
  );

  // Handle aspect invocation
  const handleInvoke = useCallback(
    async (aspect: string, payload?: unknown) => {
      if (!selectedPath) return;

      setSelectedAspect(aspect);
      setResponse({ data: null, elapsed: 0, status: 'loading' });

      const startTime = performance.now();

      try {
        // Build the API URL
        const pathSegments = selectedPath.replace(/\./g, '/');
        const url = `/agentese/${pathSegments}/${aspect}`;

        // Make the request with observer headers
        const res = await fetch(url, {
          method: payload ? 'POST' : 'GET',
          headers: {
            'Content-Type': 'application/json',
            'X-Observer-Archetype': observer.archetype,
            'X-Observer-Capabilities': observer.capabilities.join(','),
          },
          body: payload ? JSON.stringify(payload) : undefined,
        });

        const elapsed = performance.now() - startTime;
        const data = await res.json();

        if (!res.ok) {
          setResponse({
            data: null,
            elapsed,
            status: 'error',
            error: data.detail || data.error || `HTTP ${res.status}`,
          });
        } else {
          setResponse({
            data: data.result ?? data,
            elapsed,
            status: 'success',
          });
        }
      } catch (err) {
        const elapsed = performance.now() - startTime;
        setResponse({
          data: null,
          elapsed,
          status: 'error',
          error: err instanceof Error ? err.message : 'Unknown error',
        });
      }
    },
    [selectedPath, observer]
  );

  // Show guided tour if no path selected and we have paths
  const showTour = !selectedPath && paths.length > 0 && !loading;

  // Compact (mobile) layout
  if (density === 'compact') {
    return (
      <div className="h-full flex flex-col bg-gray-900">
        {/* Observer picker - always visible */}
        <ObserverPicker observer={observer} onChange={handleObserverChange} density={density} />

        {/* Main content - either tour or request/response */}
        <div className="flex-1 overflow-auto">
          {loading ? (
            <div className="p-4">
              <LoadingState message="Discovering paths..." />
            </div>
          ) : error ? (
            <div className="p-4">
              <ErrorState message={error} onRetry={refetch} />
            </div>
          ) : showTour ? (
            <div className="p-4">
              <GuidedTour paths={paths} metadata={metadata} onSelectPath={handleSelectPath} />
            </div>
          ) : selectedPath ? (
            <div className="flex flex-col h-full">
              {/* Collapsible Request Builder Section */}
              <div className="border-b border-gray-700">
                <button
                  onClick={() => setRequestExpanded(!requestExpanded)}
                  className="w-full flex items-center justify-between px-4 py-3 bg-gray-800/50 hover:bg-gray-800/70 transition-colors"
                >
                  <span className="flex items-center gap-2 text-sm font-medium text-white">
                    <span>🔧</span>
                    <span>Request Builder</span>
                    <span className="text-xs text-gray-400 font-normal">
                      {selectedPath}:{selectedAspect}
                    </span>
                  </span>
                  {requestExpanded ? (
                    <ChevronUp className="w-4 h-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  )}
                </button>
                <AnimatePresence>
                  {requestExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <div className="max-h-[40vh] overflow-auto">
                        <RequestBuilder
                          path={selectedPath}
                          aspect={selectedAspect}
                          schema={selectedSchema?.[selectedAspect]}
                          observer={observer}
                          onObserverChange={handleObserverChange}
                          onSend={(payload) => {
                            handleInvoke(selectedAspect, payload);
                            setRequestExpanded(false); // Collapse after sending on mobile
                          }}
                          density={density}
                          examples={selectedMetadata?.examples?.filter(
                            (ex) => ex.aspect === selectedAspect
                          )}
                        />
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Response Viewer */}
              <div className="flex-1 min-h-0">
                <ResponseViewer
                  response={response}
                  path={selectedPath}
                  aspect={selectedAspect}
                  observer={observer}
                />
              </div>
            </div>
          ) : (
            <div className="p-4">
              <ResponseViewer
                response={response}
                path={selectedPath}
                aspect={selectedAspect}
                observer={observer}
              />
            </div>
          )}
        </div>

        {/* Floating action buttons */}
        <FloatingActions
          actions={[
            {
              id: 'explore',
              icon: <Compass className="w-5 h-5" />,
              label: 'Explore',
              onClick: () => {
                setActiveDrawer('explorer');
                setDrawerOpen(true);
              },
            },
            {
              id: 'actions',
              icon: <Zap className="w-5 h-5" />,
              label: 'Actions',
              onClick: () => {
                setActiveDrawer('aspects');
                setDrawerOpen(true);
              },
              disabled: !selectedPath,
            },
          ]}
        />

        {/* Bottom drawer */}
        <BottomDrawer
          isOpen={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          title={activeDrawer === 'explorer' ? 'AGENTESE Paths' : 'Aspects'}
        >
          {activeDrawer === 'explorer' ? (
            <PathExplorer
              paths={paths}
              metadata={metadata}
              selectedPath={selectedPath}
              onSelectPath={(p) => {
                handleSelectPath(p);
                setDrawerOpen(false);
              }}
              density={density}
            />
          ) : selectedPath && selectedMetadata ? (
            <AspectPanel
              path={selectedPath}
              metadata={selectedMetadata}
              schema={selectedSchema}
              selectedAspect={selectedAspect}
              observer={observer}
              onInvoke={(aspect, payload) => {
                handleInvoke(aspect, payload);
                setDrawerOpen(false);
              }}
              density={density}
            />
          ) : (
            <div className="p-4 text-gray-400 text-center">Select a path first</div>
          )}
        </BottomDrawer>
      </div>
    );
  }

  // Comfortable (tablet) - two columns with tabs
  if (density === 'comfortable') {
    return (
      <div className="h-full flex flex-col bg-gray-900">
        <ObserverPicker observer={observer} onChange={handleObserverChange} density={density} />

        <ElasticSplit
          direction="horizontal"
          defaultRatio={0.35}
          collapseAtDensity="compact"
          primary={
            <PathExplorer
              paths={paths}
              metadata={metadata}
              selectedPath={selectedPath}
              onSelectPath={handleSelectPath}
              loading={loading}
              error={error}
              density={density}
            />
          }
          secondary={
            <div className="h-full flex flex-col">
              {/* Tabs for response/aspects */}
              <TabBar tabs={['Response', 'Actions']} activeTab={0} onTabChange={() => {}} />
              {showTour ? (
                <GuidedTour paths={paths} metadata={metadata} onSelectPath={handleSelectPath} />
              ) : (
                <>
                  <div className="flex-1 overflow-auto">
                    <ResponseViewer
                      response={response}
                      path={selectedPath}
                      aspect={selectedAspect}
                      observer={observer}
                    />
                  </div>
                  {selectedPath && selectedMetadata && (
                    <div className="border-t border-gray-700 p-4">
                      <AspectPanel
                        path={selectedPath}
                        metadata={selectedMetadata}
                        schema={selectedSchema}
                        selectedAspect={selectedAspect}
                        observer={observer}
                        onInvoke={handleInvoke}
                        density={density}
                        compact
                      />
                    </div>
                  )}
                </>
              )}
            </div>
          }
        />
      </div>
    );
  }

  // Spacious (desktop) - full three-column layout with Request/Response split
  return (
    <div className="h-full flex flex-col bg-gray-900">
      <ObserverPicker observer={observer} onChange={handleObserverChange} density={density} />

      <div className="flex-1 flex overflow-hidden">
        {/* Left: Path Explorer */}
        <motion.div
          className="w-72 border-r border-gray-700 overflow-y-auto bg-gray-800/50"
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: shouldAnimate ? 0.3 : 0 }}
        >
          <PathExplorer
            paths={paths}
            metadata={metadata}
            selectedPath={selectedPath}
            onSelectPath={handleSelectPath}
            loading={loading}
            error={error}
            density={density}
          />
        </motion.div>

        {/* Middle: Request Builder + Response Viewer (split) */}
        <motion.div
          className="flex-1 overflow-hidden"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: shouldAnimate ? 0.2 : 0, delay: 0.1 }}
        >
          <AnimatePresence mode="wait">
            {showTour ? (
              <GuidedTour
                key="tour"
                paths={paths}
                metadata={metadata}
                onSelectPath={handleSelectPath}
              />
            ) : selectedPath ? (
              <ElasticSplit
                key="request-response"
                direction="horizontal"
                defaultRatio={0.5}
                collapseAtDensity="compact"
                primary={
                  <div className="h-full overflow-auto border-r border-gray-700/50">
                    <RequestBuilder
                      path={selectedPath}
                      aspect={selectedAspect}
                      schema={selectedSchema?.[selectedAspect]}
                      observer={observer}
                      onObserverChange={handleObserverChange}
                      onSend={(payload) => handleInvoke(selectedAspect, payload)}
                      density={density}
                      examples={selectedMetadata?.examples?.filter(
                        (ex) => ex.aspect === selectedAspect
                      )}
                    />
                  </div>
                }
                secondary={
                  <div className="h-full overflow-auto">
                    <ResponseViewer
                      response={response}
                      path={selectedPath}
                      aspect={selectedAspect}
                      observer={observer}
                    />
                  </div>
                }
              />
            ) : (
              <div
                key="empty"
                className="h-full flex items-center justify-center text-gray-500 p-8 text-center"
              >
                <div>
                  <div className="text-6xl mb-4">🌐</div>
                  <h2 className="text-xl font-semibold text-white mb-2">AGENTESE Explorer</h2>
                  <p>Select a path from the left panel to begin exploring.</p>
                </div>
              </div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Right: Aspect Panel */}
        <motion.div
          className="w-64 border-l border-gray-700 overflow-y-auto bg-gray-800/30"
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: shouldAnimate ? 0.3 : 0 }}
        >
          {selectedPath && selectedMetadata ? (
            <AspectPanel
              path={selectedPath}
              metadata={selectedMetadata}
              schema={selectedSchema}
              selectedAspect={selectedAspect}
              observer={observer}
              onInvoke={(aspect) => {
                // Just select the aspect - RequestBuilder will handle the actual send
                setSelectedAspect(aspect);
              }}
              density={density}
            />
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500 p-8 text-center">
              <div>
                <div className="text-4xl mb-4">🌌</div>
                <p>Select a path to see available actions</p>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}

// =============================================================================
// Helper Components
// =============================================================================

function LoadingState({ message }: { message: string }) {
  return (
    <div className="h-full flex items-center justify-center">
      <motion.div
        className="text-center"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <motion.div
          className="w-16 h-16 mx-auto mb-4 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
        <p className="text-gray-400">{message}</p>
      </motion.div>
    </div>
  );
}

function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="h-full flex items-center justify-center p-8">
      <div className="text-center max-w-md">
        <div className="text-6xl mb-4">🌑</div>
        <h2 className="text-xl font-semibold text-pink-400 mb-2">Lost in the Ether</h2>
        <p className="text-gray-400 mb-4">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white
                       font-medium transition-colors"
          >
            Try Again
          </button>
        )}
      </div>
    </div>
  );
}

function TabBar({
  tabs,
  activeTab,
  onTabChange,
}: {
  tabs: string[];
  activeTab: number;
  onTabChange: (index: number) => void;
}) {
  return (
    <div className="flex border-b border-gray-700">
      {tabs.map((tab, i) => (
        <button
          key={tab}
          onClick={() => onTabChange(i)}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            i === activeTab
              ? 'text-cyan-400 border-b-2 border-cyan-400'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          {tab}
        </button>
      ))}
    </div>
  );
}

export default AgenteseDocs;
