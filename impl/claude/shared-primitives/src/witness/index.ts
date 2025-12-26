/**
 * Witness Components
 *
 * Daily Lab UI primitives for mark capture, trail display, and crystals.
 */

export { MarkCaptureInput } from './MarkCaptureInput';
export type { MarkCaptureInputProps, CaptureRequest, CaptureResponse, DailyTag } from './MarkCaptureInput';

export { TrailTimeline } from './TrailTimeline';
export type { TrailTimelineProps, TrailMark, TimeGap } from './TrailTimeline';

export { CrystalCard } from './CrystalCard';
export type { CrystalCardProps, Crystal, CompressionHonesty } from './CrystalCard';

export { ValueCompassRadar } from './ValueCompassRadar';
export type { ValueCompassRadarProps, PrincipleWeights, DomainCalibration } from './ValueCompassRadar';

export { GapIndicator, GapSummary } from './GapIndicator';
export type { GapIndicatorProps, GapSummaryProps, TimeGap as GapTimeGap } from './GapIndicator';
