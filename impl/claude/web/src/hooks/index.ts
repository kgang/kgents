/**
 * Barrel exports for React hooks.
 *
 * Import hooks from this module for cleaner imports:
 * ```ts
 * import { useAsyncState, useTownStreamWidget, useOnlineStatus } from '@/hooks';
 * ```
 */

// Async state management
export {
  useAsyncState,
  type AsyncState,
  type AsyncStatus,
  type UseAsyncStateOptions,
  type UseAsyncStateReturn,
} from './useAsyncState';

// SSE streaming hooks
export {
  useTownStreamWidget,
  type UseTownStreamWidgetOptions,
  type UseTownStreamWidgetResult,
} from './useTownStreamWidget';

// Town loading hook (projection-first extraction)
export { useTownLoader } from './useTownLoader';

// Brain WebSocket streaming (Phase 1 Crown Jewels completion)
export {
  useBrainStream,
  type UseBrainStreamOptions,
  type UseBrainStreamResult,
  type BrainEvent,
} from './useBrainStream';

// Gestalt streaming (Sprint 1: Live Architecture)
export {
  useGestaltStream,
  type UseGestaltStreamOptions,
  type UseGestaltStreamReturn,
} from './useGestaltStream';

// Performance optimization
export { useBatchedEvents } from './useBatchedEvents';

// Layout and responsiveness
export {
  useLayoutContext,
  useLayoutMeasure,
  useWindowLayout,
  LayoutContextProvider,
  DEFAULT_LAYOUT_CONTEXT,
} from './useLayoutContext';

// Design polynomial state machine (mirrors Python DESIGN_POLYNOMIAL)
export {
  useDesignPolynomial,
  useAnimationCoordination,
  densityFromWidth,
  contentLevelFromWidth,
  designTransition,
  inferSyncStrategy,
  computeTemporalOverlap,
  DEFAULT_STATE as DEFAULT_DESIGN_STATE,
  type Density,
  type ContentLevel,
  type MotionType,
  type AnimationPhaseName,
  type AnimationPhase,
  type SyncStrategy,
  type AnimationConstraint,
  type DesignState,
  type DesignInput,
  type DesignOutput,
  type UseDesignPolynomialOptions,
  type UseDesignPolynomialResult,
  type UseAnimationCoordinationOptions,
  type UseAnimationCoordinationResult,
} from './useDesignPolynomial';

// Design gateway (bridges local state with AGENTESE backend)
export {
  useDesignGateway,
  type OperadInfo,
  type OperadOperationsInfo,
  type UseDesignGatewayOptions,
  type UseDesignGatewayResult,
} from './useDesignGateway';

// Connectivity
export { useOnlineStatus } from './useOnlineStatus';

// Input handling
export {
  useKeyboardShortcuts,
  createDefaultShortcuts,
  type ShortcutContext,
  type ShortcutDefinition,
  type Modifiers,
  type UseKeyboardShortcutsOptions,
  type UseKeyboardShortcutsReturn,
} from './useKeyboardShortcuts';

export {
  useTouchGestures,
  usePinchZoom,
  useLongPress,
  useSwipe,
  type PinchState,
  type LongPressState,
  type SwipeState,
  type UsePinchZoomOptions,
  type UseLongPressOptions,
  type UseSwipeOptions,
  type UseTouchGesturesOptions,
  type TouchGesturesState,
} from './useTouchGestures';

// Emergence visualization hooks
export { useCymatics, type UseCymaticsOptions, type UseCymaticsReturn } from './useCymatics';

export {
  useGrowthAnimation,
  type GrowthAnimationOptions,
  type UseGrowthAnimationReturn,
} from './useGrowthAnimation';

// Teaching mode (Phase 4: Teaching Layer)
export {
  useTeachingMode,
  useTeachingModeContext,
  useTeachingModeSafe,
  TeachingModeProvider,
  TeachingToggle,
  WhenTeaching,
  WhenNotTeaching,
  type TeachingModeState,
  type TeachingModeProviderProps,
  type TeachingToggleProps,
} from './useTeachingMode';

// Breathing animation (Town Renaissance: Everything Breathes)
export {
  useBreathing,
  getStaggeredPhaseOffset,
  getBreathingKeyframes,
  type BreathingOptions,
  type BreathingState,
} from './useBreathing';

// Crown Jewels Genesis Animation Primitives
export {
  useGrowing,
  getStaggeredGrowthDelay,
  triggerWithDelay,
  getGrowingKeyframes,
  getGrowingAnimation,
  type GrowthStage,
  type GrowingOptions,
  type GrowingState,
} from './useGrowing';

export {
  useUnfurling,
  getUnfurlingKeyframes,
  getUnfurlingAnimation,
  type UnfurlDirection,
  type UnfurlingOptions,
  type UnfurlingState,
} from './useUnfurling';

export {
  useFlowing,
  createCurvedPath,
  createSCurvePath,
  type Point,
  type FlowParticle,
  type FlowingOptions,
  type FlowingState,
} from './useFlowing';

// Town AGENTESE queries (Contract-Driven)
export {
  // Query keys
  townQueryKeys,
  // Town manifest
  useTownManifest,
  // Citizens
  useCitizens,
  useCitizen,
  useCreateCitizen,
  useUpdateCitizen,
  // Relationships
  useCitizenRelationships,
  // Conversations
  useConversationHistory,
  useStartConversation,
  useAddTurn,
  // Coalitions
  useCoalitionManifest,
  useCoalitions,
  useCoalition,
  useCoalitionBridges,
  useDetectCoalitions,
  useCoalitionDecay,
  // Type re-exports
  type WorldTownManifestResponse,
  type WorldTownCitizenListResponse,
  type WorldTownCitizenGetResponse,
  type WorldTownCoalitionListResponse,
  type WorldTownCoalitionManifestResponse,
} from './useTownQuery';

// Park AGENTESE queries (Contract-Driven)
export {
  // Query keys
  parkQueryKeys,
  // Park manifest
  useParkManifest,
  // Hosts
  useHosts,
  useHost,
  useCreateHost,
  useUpdateHost,
  useInteractWithHost,
  useHostMemories,
  // Episodes
  useEpisodes,
  useStartEpisode,
  useEndEpisode,
  // Locations
  useLocations,
  useCreateLocation,
  // Type re-exports
  type WorldParkManifestResponse,
  type WorldParkHostListResponse,
  type WorldParkHostGetResponse,
  type WorldParkHostCreateRequest,
  type WorldParkHostCreateResponse,
  type WorldParkHostInteractRequest,
  type WorldParkHostInteractResponse,
  type WorldParkEpisodeListResponse,
  type WorldParkEpisodeStartRequest,
  type WorldParkEpisodeStartResponse,
  type WorldParkLocationListResponse,
  type WorldParkLocationCreateRequest,
  type WorldParkLocationCreateResponse,
} from './useParkQuery';

// Forge AGENTESE queries (Contract-Driven)
export {
  // Query keys
  forgeQueryKeys,
  // Forge manifest
  useForgeManifest,
  // Workshops
  useWorkshops,
  useWorkshop,
  useCreateWorkshop,
  useEndWorkshop,
  // Artisans
  useArtisans,
  useJoinWorkshop,
  // Contributions
  useContribute,
  useContributions,
  // Exhibitions
  useCreateExhibition,
  useOpenExhibition,
  useViewExhibition,
  // Gallery
  useGalleryItems,
  useAddToGallery,
  // Festivals
  useFestivals,
  useCreateFestival,
  useEnterFestival,
  // Type re-exports
  type WorldForgeManifestResponse,
  type WorldForgeWorkshopListResponse,
  type WorldForgeWorkshopGetResponse,
  type WorldForgeArtisanListResponse,
  type WorldForgeContributionListResponse,
  type WorldForgeFestivalListResponse,
} from './useForgeQuery';

// Brain AGENTESE queries (Contract-Driven)
export {
  // Query keys
  brainQueryKeys,
  // Brain manifest
  useBrainManifest,
  // Memory queries
  useMemorySearch,
  useMemorySurface,
  useMemoryCrystal,
  useMemoryRecent,
  useMemoryByTag,
  useMemoryTopology,
  // Memory mutations
  useCaptureMemory,
  useDeleteMemory,
  useHealMemory,
  // Type re-exports
  type SelfMemoryManifestResponse,
  type SelfMemorySearchRequest,
  type SelfMemorySearchResponse,
  type SelfMemoryCaptureRequest,
  type SelfMemoryCaptureResponse,
  type SelfMemoryTopologyResponse,
} from './useBrainQuery';

// Gestalt AGENTESE queries (Contract-Driven)
export {
  // Query keys
  gestaltQueryKeys,
  // Gestalt manifest
  useGestaltManifest,
  // Codebase queries
  useCodebaseHealth,
  useCodebaseDrift,
  useCodebaseTopology,
  useCodebaseModule,
  // Codebase mutations
  useScanCodebase,
  // Type re-exports
  type WorldCodebaseManifestResponse,
  type WorldCodebaseHealthResponse,
  type WorldCodebaseDriftResponse,
  type WorldCodebaseTopologyResponse,
  type WorldCodebaseModuleResponse,
  type WorldCodebaseScanResponse,
} from './useGestaltQuery';

// Workshop AGENTESE queries (Contract-Driven)
export {
  // Query keys
  workshopQueryKeys,
  // Workshop manifest
  useWorkshopManifest,
  useWorkshopBuilders,
  // Workshop mutations
  useAssignWorkshopTask,
  useAdvanceWorkshop,
  useCompleteWorkshop,
  // Type re-exports
  type WorldTownWorkshopManifestResponse,
  type WorldTownWorkshopBuildersResponse,
  type WorldTownWorkshopAssignRequest,
  type WorldTownWorkshopAssignResponse,
  type WorldTownWorkshopAdvanceResponse,
  type WorldTownWorkshopCompleteResponse,
} from './useWorkshopQuery';

// Gardener AGENTESE queries (Contract-Driven)
export {
  // Query keys
  gardenerQueryKeys,
  // Gardener manifest
  useGardenerManifest,
  // Session queries
  useGardenerSession,
  useGardenerPolynomial,
  useGardenerSessions,
  useGardenerPropose,
  // Session mutations
  useDefineSession,
  useAdvanceSession,
  useRouteInput,
  // Type re-exports
  type ConceptGardenerManifestResponse,
  type ConceptGardenerSessionManifestResponse,
  type ConceptGardenerSessionDefineRequest,
  type ConceptGardenerSessionDefineResponse,
  type ConceptGardenerSessionAdvanceRequest,
  type ConceptGardenerSessionAdvanceResponse,
  type ConceptGardenerSessionPolynomialResponse,
  type ConceptGardenerSessionsManifestResponse,
  type ConceptGardenerRouteRequest,
  type ConceptGardenerRouteResponse,
  type ConceptGardenerProposeResponse,
} from './useGardenerQuery';

// Differance AGENTESE queries (Contract-Driven) - Phase 5: FRUITING
export {
  // Query keys
  differanceQueryKeys,
  branchQueryKeys,
  // Differance manifest
  useDifferanceManifest,
  // Heritage DAG (the crown jewel)
  useHeritageDAG,
  // "Why did this happen?" (explainability)
  useWhyExplain,
  // Ghosts (unexplored alternatives)
  useGhosts,
  // Navigation
  useTraceAt,
  useReplay,
  // Branch operations
  useBranchManifest,
  useCreateBranch,
  useExploreBranch,
  useCompareBranches,
  // Type re-exports
  type DifferanceManifestResponse,
  type BranchManifestResponse,
  type HeritageRequest,
  type HeritageNodeResponse,
  type HeritageEdgeResponse,
  type HeritageResponse,
  type WhyRequest,
  type WhyChosenStep,
  type WhyResponse,
  type GhostsRequest,
  type GhostItem,
  type GhostsResponse,
  type AtRequest,
  type AtAlternative,
  type AtResponse,
  type ReplayRequest,
  type ReplayStep,
  type ReplayResponse,
  type BranchCreateRequest,
  type BranchCreateResponse,
  type BranchExploreRequest,
  type BranchExploreResponse,
  type BranchCompareRequest,
  type BranchCompareResponse,
} from './useDifferanceQuery';

// Soul AGENTESE queries (K-gent governance)
export {
  // Soul manifest
  useSoulManifest,
  useSoulVibe,
  // Utilities
  isSoulActive,
  getSoulModeIcon,
  getSoulModeLabel,
  // Type re-exports
  type SoulManifestResponse,
  type SoulVibeResponse,
} from './useSoulQuery';

// Garden AGENTESE queries (self.garden.* - garden STATE)
// Distinct from Gardener (concept.gardener.* - SESSION orchestration)
export {
  // Query keys
  gardenQueryKeys,
  // Garden manifest (full GardenJSON state)
  useGardenManifest,
  // Garden queries
  useGardenSeason,
  useGardenHealth,
  useGardenSuggest,
  // Garden mutations
  useGardenTransition,
  useGardenAccept,
  useGardenDismiss,
  // Conversion helper
  toTransitionSuggestion,
  // Type re-exports
  type GardenSeasonResponse,
  type GardenHealthResponse,
  type GardenSuggestResponse,
  type GardenTransitionRequest,
  type GardenTransitionResponse,
  type GardenAcceptResponse,
  type GardenDismissResponse,
} from './useGardenQuery';

// Simple toast notifications (general-purpose feedback)
export {
  useSimpleToast,
  simpleToast,
  type SimpleToastOptions,
  type UseSimpleToastReturn,
} from './useSimpleToast';
