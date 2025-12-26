/**
 * useFeedFeedback Hook
 *
 * "Users create feedback systems WITH the feed."
 *
 * Tracks user interactions with feed items to improve algorithmic ranking:
 * - View events (impressions)
 * - Engage events (clicks, edits)
 * - Dismiss events (hide, archive)
 * - Contradict events (conflict detection)
 */

import { useCallback, useRef } from 'react';
import type {
  KBlock,
  FeedbackEvent,
  FeedbackAction,
  UseFeedFeedback,
} from './types';

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook for tracking feed item interactions.
 */
export function useFeedFeedback(): UseFeedFeedback {
  // Store feedback events in memory (could be synced to backend)
  const feedbackRef = useRef<FeedbackEvent[]>([]);

  // Track feedback event
  const trackFeedback = useCallback(
    (kblockId: string, action: FeedbackAction, metadata?: Record<string, unknown>) => {
      const event: FeedbackEvent = {
        kblockId,
        action,
        timestamp: new Date(),
        metadata,
      };

      feedbackRef.current.push(event);

      // Log in development
      if (import.meta.env.DEV) {
        console.log('[FeedFeedback]', action, kblockId, metadata);
      }

      // TODO: Sync to backend for persistence and analytics
      // await logos.invoke('self.feed.feedback/record', observer, { event });
    },
    []
  );

  // View handler
  const onView = useCallback(
    (kblock: KBlock) => {
      trackFeedback(kblock.id, 'view', {
        layer: kblock.layer,
        loss: kblock.loss,
      });
    },
    [trackFeedback]
  );

  // Engage handler
  const onEngage = useCallback(
    (kblock: KBlock) => {
      trackFeedback(kblock.id, 'engage', {
        layer: kblock.layer,
        loss: kblock.loss,
        edgeCount: kblock.edgeCount,
      });
    },
    [trackFeedback]
  );

  // Dismiss handler
  const onDismiss = useCallback(
    (kblock: KBlock) => {
      trackFeedback(kblock.id, 'dismiss', {
        layer: kblock.layer,
        loss: kblock.loss,
      });
    },
    [trackFeedback]
  );

  // Contradict handler
  const onContradict = useCallback(
    (kblockA: KBlock, kblockB: KBlock) => {
      // Track for both K-Blocks
      trackFeedback(kblockA.id, 'contradict', {
        contradictsWith: kblockB.id,
        layerA: kblockA.layer,
        layerB: kblockB.layer,
      });

      trackFeedback(kblockB.id, 'contradict', {
        contradictsWith: kblockA.id,
        layerA: kblockA.layer,
        layerB: kblockB.layer,
      });
    },
    [trackFeedback]
  );

  // Get feedback for a K-Block
  const getFeedback = useCallback((kblockId: string): FeedbackEvent[] => {
    return feedbackRef.current.filter((event) => event.kblockId === kblockId);
  }, []);

  // Clear all feedback
  const clearFeedback = useCallback(() => {
    feedbackRef.current = [];
  }, []);

  return {
    onView,
    onEngage,
    onDismiss,
    onContradict,
    getFeedback,
    clearFeedback,
  };
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Calculate engagement score for a K-Block based on feedback events.
 */
export function calculateEngagementScore(events: FeedbackEvent[]): number {
  let score = 0;

  for (const event of events) {
    switch (event.action) {
      case 'view':
        score += 0.1; // Small bump for impressions
        break;
      case 'engage':
        score += 1.0; // Significant boost for engagement
        break;
      case 'dismiss':
        score -= 0.5; // Penalty for dismissal
        break;
      case 'contradict':
        score += 0.3; // Contradictions indicate active discussion
        break;
    }
  }

  return Math.max(0, score);
}

/**
 * Get recency weight (decays over time).
 */
export function getRecencyWeight(event: FeedbackEvent): number {
  const now = new Date();
  const age = now.getTime() - event.timestamp.getTime();

  // Decay over 7 days
  const decayPeriod = 7 * 24 * 60 * 60 * 1000; // 7 days in ms
  const decay = Math.exp(-age / decayPeriod);

  return decay;
}

/**
 * Calculate algorithmic feed score.
 * Combines:
 * - Loss (coherence)
 * - Engagement
 * - Principles alignment
 * - Recency
 */
export function calculateAlgorithmicScore(
  kblock: KBlock,
  feedback: FeedbackEvent[]
): number {
  // 1. Coherence score (inverse of loss)
  const coherenceScore = 1 - kblock.loss;

  // 2. Engagement score
  const engagementScore = calculateEngagementScore(feedback);

  // 3. Recency weight
  const recentFeedback = feedback.filter(
    (event) => getRecencyWeight(event) > 0.1
  );
  const recencyWeight = recentFeedback.length > 0
    ? recentFeedback.reduce((sum, event) => sum + getRecencyWeight(event), 0) / recentFeedback.length
    : 0.5;

  // 4. Principles alignment (proxy: count of principles)
  const principlesScore = Math.min(1, kblock.principles.length / 5);

  // Weighted combination
  const score =
    coherenceScore * 0.3 +
    engagementScore * 0.4 +
    principlesScore * 0.2 +
    recencyWeight * 0.1;

  return score;
}
