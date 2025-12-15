import { describe, it, expect, beforeEach } from 'vitest';
import { useTownStore } from '@/stores/townStore';
import type { CitizenSummary, TownEvent } from '@/api/types';

describe('townStore', () => {
  beforeEach(() => {
    useTownStore.getState().reset();
  });

  describe('town metadata', () => {
    it('should set and get townId', () => {
      useTownStore.getState().setTownId('test-town-1');
      expect(useTownStore.getState().townId).toBe('test-town-1');
    });

    it('should set and get townName', () => {
      useTownStore.getState().setTownName('Test Town');
      expect(useTownStore.getState().townName).toBe('Test Town');
    });

    it('should clear townId with null', () => {
      useTownStore.getState().setTownId('test-town-1');
      useTownStore.getState().setTownId(null);
      expect(useTownStore.getState().townId).toBeNull();
    });
  });

  describe('citizens', () => {
    const mockCitizens: CitizenSummary[] = [
      {
        id: 'citizen-1',
        name: 'Alice',
        archetype: 'Builder',
        region: 'square',
        phase: 'IDLE',
        is_evolving: false,
      },
      {
        id: 'citizen-2',
        name: 'Bob',
        archetype: 'Trader',
        region: 'market',
        phase: 'WORKING',
        is_evolving: false,
      },
    ];

    it('should set citizens', () => {
      useTownStore.getState().setCitizens(mockCitizens);
      expect(useTownStore.getState().citizens).toHaveLength(2);
      expect(useTownStore.getState().citizens[0].name).toBe('Alice');
    });

    it('should initialize citizen positions from regions', () => {
      useTownStore.getState().setCitizens(mockCitizens);
      const positions = useTownStore.getState().citizenPositions;
      expect(positions.has('citizen-1')).toBe(true);
      expect(positions.has('citizen-2')).toBe(true);
    });

    it('should update citizen position', () => {
      useTownStore.getState().setCitizens(mockCitizens);
      useTownStore.getState().updateCitizenPosition('citizen-1', 5, 5);
      const pos = useTownStore.getState().citizenPositions.get('citizen-1');
      expect(pos).toEqual({ x: 5, y: 5 });
    });
  });

  describe('selection', () => {
    it('should select a citizen', () => {
      useTownStore.getState().selectCitizen('citizen-1');
      expect(useTownStore.getState().selectedCitizenId).toBe('citizen-1');
    });

    it('should reset LOD when selecting new citizen', () => {
      useTownStore.getState().setLOD(3);
      useTownStore.getState().selectCitizen('citizen-1');
      expect(useTownStore.getState().currentLOD).toBe(0);
    });

    it('should clear selection with null', () => {
      useTownStore.getState().selectCitizen('citizen-1');
      useTownStore.getState().selectCitizen(null);
      expect(useTownStore.getState().selectedCitizenId).toBeNull();
    });

    it('should set and clear hovered citizen', () => {
      useTownStore.getState().hoverCitizen('citizen-1');
      expect(useTownStore.getState().hoveredCitizenId).toBe('citizen-1');

      useTownStore.getState().hoverCitizen(null);
      expect(useTownStore.getState().hoveredCitizenId).toBeNull();
    });
  });

  describe('LOD (Level of Detail)', () => {
    it('should set LOD level', () => {
      useTownStore.getState().setLOD(3);
      expect(useTownStore.getState().currentLOD).toBe(3);
    });

    it('should set selected manifest', () => {
      const manifest = {
        id: 'citizen-1',
        name: 'Alice',
        archetype: 'Builder',
        region: 'square',
        phase: 'IDLE',
      };
      useTownStore.getState().setSelectedManifest(manifest);
      expect(useTownStore.getState().selectedCitizenManifest).toEqual(manifest);
    });
  });

  describe('playback', () => {
    it('should set playing state', () => {
      useTownStore.getState().setPlaying(true);
      expect(useTownStore.getState().isPlaying).toBe(true);

      useTownStore.getState().setPlaying(false);
      expect(useTownStore.getState().isPlaying).toBe(false);
    });

    it('should set speed within bounds', () => {
      useTownStore.getState().setSpeed(2.0);
      expect(useTownStore.getState().speed).toBe(2.0);
    });

    it('should clamp speed to minimum', () => {
      useTownStore.getState().setSpeed(0.1);
      expect(useTownStore.getState().speed).toBe(0.5);
    });

    it('should clamp speed to maximum', () => {
      useTownStore.getState().setSpeed(10.0);
      expect(useTownStore.getState().speed).toBe(4.0);
    });
  });

  describe('time state', () => {
    it('should set phase', () => {
      useTownStore.getState().setPhase('AFTERNOON');
      expect(useTownStore.getState().currentPhase).toBe('AFTERNOON');
    });

    it('should increment day', () => {
      expect(useTownStore.getState().currentDay).toBe(1);
      useTownStore.getState().incrementDay();
      expect(useTownStore.getState().currentDay).toBe(2);
    });
  });

  describe('events', () => {
    const mockEvent: TownEvent = {
      tick: 100,
      phase: 'MORNING',
      operation: 'greet',
      participants: ['Alice', 'Bob'],
      success: true,
      message: 'Alice greeted Bob',
      tokens_used: 50,
      timestamp: '2024-01-01T00:00:00Z',
    };

    it('should add event', () => {
      useTownStore.getState().addEvent(mockEvent);
      expect(useTownStore.getState().events).toHaveLength(1);
      expect(useTownStore.getState().events[0].message).toBe('Alice greeted Bob');
    });

    it('should update phase and tick from event', () => {
      useTownStore.getState().addEvent(mockEvent);
      expect(useTownStore.getState().currentPhase).toBe('MORNING');
      expect(useTownStore.getState().currentTick).toBe(100);
    });

    it('should keep only last 100 events', () => {
      for (let i = 0; i < 150; i++) {
        useTownStore.getState().addEvent({
          ...mockEvent,
          tick: i,
          message: `Event ${i}`,
        });
      }
      expect(useTownStore.getState().events).toHaveLength(100);
      // Most recent should be first
      expect(useTownStore.getState().events[0].tick).toBe(149);
    });

    it('should clear events', () => {
      useTownStore.getState().addEvent(mockEvent);
      useTownStore.getState().clearEvents();
      expect(useTownStore.getState().events).toHaveLength(0);
    });
  });

  describe('interactions', () => {
    it('should add and clear interaction', () => {
      const interaction = {
        id: 'int-1',
        participants: ['Alice', 'Bob'],
        operation: 'greet',
        startTick: 100,
        fadeProgress: 0,
      };

      useTownStore.getState().addInteraction(interaction);
      expect(useTownStore.getState().activeInteractions).toHaveLength(1);

      useTownStore.getState().clearInteraction('int-1');
      expect(useTownStore.getState().activeInteractions).toHaveLength(0);
    });

    it('should fade interaction', () => {
      const interaction = {
        id: 'int-1',
        participants: ['Alice', 'Bob'],
        operation: 'greet',
        startTick: 100,
        fadeProgress: 0,
      };

      useTownStore.getState().addInteraction(interaction);
      useTownStore.getState().fadeInteraction('int-1', 0.5);

      expect(useTownStore.getState().activeInteractions[0].fadeProgress).toBe(0.5);
    });
  });

  describe('coalitions', () => {
    it('should set coalitions', () => {
      const coalitions = [
        { id: 'c1', name: 'Builders Guild', members: ['Alice', 'Bob'], size: 2, strength: 0.8 },
      ];
      useTownStore.getState().setCoalitions(coalitions);
      expect(useTownStore.getState().coalitions).toHaveLength(1);
    });
  });

  describe('reset', () => {
    it('should reset to initial state', () => {
      useTownStore.getState().setTownId('test');
      useTownStore.getState().setPlaying(true);
      useTownStore.getState().setLOD(3);

      useTownStore.getState().reset();

      expect(useTownStore.getState().townId).toBeNull();
      expect(useTownStore.getState().isPlaying).toBe(false);
      expect(useTownStore.getState().currentLOD).toBe(0);
    });
  });
});
