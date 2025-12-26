/**
 * Witness Components - Daily Lab UI
 *
 * Components for the trail-to-crystal pilot.
 * Value prop: "Turn your day into proof of intention."
 *
 * Design Philosophy:
 * - FLOW first: Primary joy dimension is FLOW
 * - No hustle theater: Never optimize for "more marks"
 * - Honest gaps: Untracked time is signal, not failure
 * - Warmth in surface: Category theory in backend, warmth in UI
 *
 * @see pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md
 */

// Mark Capture (Priority 1)
export {
  MarkCaptureInput,
  type MarkCaptureInputProps,
  type CaptureRequest,
  type CaptureResponse,
  type DailyTag,
} from './MarkCaptureInput';

// Trail Timeline (Priority 1)
export {
  TrailTimeline,
  type TrailTimelineProps,
  type TrailMark,
  type TimeGap,
} from './TrailTimeline';

// Crystal Card (Priority 2)
export {
  CrystalCard,
  type CrystalCardProps,
  type Crystal,
  type CompressionHonesty,
} from './CrystalCard';

// Value Compass Radar (Priority 2)
export {
  ValueCompassRadar,
  type ValueCompassRadarProps,
  type PrincipleWeights,
  type DomainCalibration,
} from './ValueCompassRadar';

// Gap Indicator (Priority 3)
export {
  GapIndicator,
  GapSummary,
  type GapIndicatorProps,
  type GapSummaryProps,
} from './GapIndicator';
