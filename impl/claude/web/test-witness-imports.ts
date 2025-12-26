// Quick import test to verify barrel exports
import { 
  MarkCaptureInput,
  type MarkCaptureInputProps,
  type CaptureRequest,
  type CaptureResponse,
  type DailyTag,
  TrailTimeline,
  type TrailTimelineProps,
  type TrailMark,
  type TimeGap as TimeGapFromTrail,
  CrystalCard,
  type CrystalCardProps,
  type Crystal,
  type CompressionHonesty,
  ValueCompassRadar,
  type ValueCompassRadarProps,
  type PrincipleWeights,
  type DomainCalibration,
  GapIndicator,
  GapSummary,
  type GapIndicatorProps,
  type GapSummaryProps,
} from './src/components/witness';

// Type check - if this compiles, imports work
const _test: MarkCaptureInputProps = {
  onCapture: async () => undefined,
};

const _test2: TrailTimelineProps = {
  marks: [],
};

const _test3: CrystalCardProps = {
  crystal: {
    crystal_id: '',
    insight: '',
    significance: '',
    disclosure: '',
    level: 'day',
    timestamp: '',
    confidence: 0.5,
  },
};

const _test4: ValueCompassRadarProps = {
  weights: {
    tasteful: 0.5,
    curated: 0.5,
    ethical: 0.5,
    joy_inducing: 0.5,
    composable: 0.5,
    heterarchical: 0.5,
    generative: 0.5,
  },
};

const _test5: GapIndicatorProps = {
  gap: {
    start: '',
    end: '',
    duration_minutes: 30,
  },
};

console.log('All witness components can be imported successfully!');
