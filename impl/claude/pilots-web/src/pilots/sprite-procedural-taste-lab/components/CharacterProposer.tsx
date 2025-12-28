/**
 * CharacterProposer - The creative dialogue for character creation
 *
 * L4: Proposal-Rationale Law - System explains WHY each design choice.
 * "I chose heavy boots because she needs to feel grounded."
 *
 * QA-1: Collaborating with an artist, not filling out a form.
 * QA-2: Surprising-but-fitting details.
 *
 * Flavor: All characters are foxes, kittens, or seals with playful,
 * cunning, graceful, or mischievous personalities.
 */

import { useState, useCallback } from 'react';
import type { Sprite } from '@kgents/shared-primitives';
import {
  type AnimalTheme,
  createThemedDemoSprite,
  emitMutationMark,
} from '../api';
import { SpriteCanvas } from './SpriteCanvas';

interface CharacterProposerProps {
  onAccept: (sprite: Sprite, rationale: string) => void;
  onClose: () => void;
}

interface CharacterConcept {
  sprite: Sprite;
  animalTheme: AnimalTheme;
  rationale: string;
  personalityNote: string;
  galoisLoss: number;
}

/**
 * Generate three distinct character concepts from a backstory.
 * L4: Each proposal has a rationale.
 * L-FLAV-1: All characters include fox, kitten, or seal elements.
 */
function generateConcepts(backstory: string): CharacterConcept[] {
  // Parse backstory for keywords that influence theme selection
  const themes: AnimalTheme[] = ['fox', 'kitten', 'seal'];
  const concepts: CharacterConcept[] = [];

  for (const theme of themes) {
    const sprite = createThemedDemoSprite(theme);

    // Generate a rationale that connects backstory to visual choices
    const rationale = generateRationale(backstory, theme);
    const personalityNote = generatePersonalityNote(backstory, theme);

    // Compute how "wild" this interpretation is
    const galoisLoss = computeConceptDrift(backstory, theme);

    concepts.push({
      sprite,
      animalTheme: theme,
      rationale,
      personalityNote,
      galoisLoss,
    });
  }

  return concepts;
}

/**
 * Generate a rationale explaining WHY this visual direction.
 * L4: Proposal-Rationale Law.
 */
function generateRationale(backstory: string, theme: AnimalTheme): string {
  const themeRationales: Record<AnimalTheme, (bs: string) => string> = {
    fox: (bs) => {
      if (bs.includes('clever') || bs.includes('smart')) {
        return `The fox's cunning nature mirrors the cleverness in your character's story. Those quick, alert eyes suggest someone who's always thinking three steps ahead. The warm orange tones feel earned—a warmth that comes from wisdom, not naivety.`;
      }
      if (bs.includes('guard') || bs.includes('protect')) {
        return `I gave them fox-swift reflexes because a protector needs to see danger before it arrives. The pointed ears are always listening, always alert. The mischievous glint in their eye says they've learned that humor disarms better than aggression.`;
      }
      return `The fox felt right because there's something agile about this character—they move between worlds, adapt, survive. The warm fur colors suggest someone who's made peace with themselves. Those alert ears catch every whisper.`;
    },
    kitten: (bs) => {
      if (bs.includes('young') || bs.includes('curious')) {
        return `Kitten-like curiosity radiates from every pixel. Those wide eyes see wonder in ordinary things. The fluffy, soft edges suggest someone still becoming who they'll be—full of potential energy waiting to burst.`;
      }
      if (bs.includes('gentle') || bs.includes('kind')) {
        return `I chose a kitten's softness because gentleness is their superpower. The playful bounce in their idle animation says they find joy easily. But those tiny claws remind us—kindness doesn't mean weakness.`;
      }
      return `There's a playful energy here that demanded kitten form. The bouncy movement, the wide curious eyes—this character approaches the world with wonder. The soft palette says they're approachable, fluffy, but those bright eyes miss nothing.`;
    },
    seal: (bs) => {
      if (bs.includes('sea') || bs.includes('water') || bs.includes('swim')) {
        return `The seal's grace in water felt inevitable for someone connected to the sea. That seal-smooth diving motion in their movement says they're in their element. The cool blue-gray tones echo depths they've explored.`;
      }
      if (bs.includes('calm') || bs.includes('peace')) {
        return `A seal's flowing grace perfectly captures this character's inner calm. They move like someone who's found their rhythm. The sleek, streamlined silhouette says they've shed what they don't need.`;
      }
      return `Something about this story whispered "seal" to me—maybe it's the grace, the aquatic smoothness, the way they seem to flow rather than walk. Those gentle eyes have seen deep waters and returned wiser.`;
    },
  };

  return themeRationales[theme](backstory);
}

/**
 * Generate a personality note that connects theme to animation.
 * L3: Animation-Personality Law.
 */
function generatePersonalityNote(_backstory: string, theme: AnimalTheme): string {
  const notes: Record<AnimalTheme, string> = {
    fox: `Their idle animation features fox-swift ear twitches and a tail that sways when they're scheming. When content, they curl slightly; when alert, they freeze with one paw raised.`,
    kitten: `Watch their tail flick with kitten-like curiosity when something catches their attention. Their paws knead when happy, and they do a tiny bounce before any action—pure playful energy.`,
    seal: `Their movement has that seal-smooth undulation—graceful, unhurried, like water flowing. When resting, they rock gently side to side. When curious, their whiskers wiggle first.`,
  };

  return notes[theme];
}

/**
 * Compute conceptual drift from backstory to theme.
 * Higher values = more "wild" interpretation.
 */
function computeConceptDrift(backstory: string, theme: AnimalTheme): number {
  const lowerBackstory = backstory.toLowerCase();

  // Themes have natural affinities
  const affinities: Record<AnimalTheme, string[]> = {
    fox: ['clever', 'smart', 'quick', 'orange', 'forest', 'cunning', 'mischievous', 'agile'],
    kitten: ['young', 'curious', 'playful', 'soft', 'gentle', 'fluffy', 'energetic', 'bouncy'],
    seal: ['sea', 'water', 'swim', 'calm', 'peace', 'grace', 'smooth', 'aquatic', 'sleek'],
  };

  const matches = affinities[theme].filter((word) => lowerBackstory.includes(word)).length;
  const affinity = matches / affinities[theme].length;

  // Low affinity = high drift (wild interpretation)
  return Math.max(0.05, 0.5 - affinity * 0.4);
}

export function CharacterProposer({ onAccept, onClose }: CharacterProposerProps) {
  const [backstory, setBackstory] = useState('');
  const [concepts, setConcepts] = useState<CharacterConcept[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  const handleGenerate = useCallback(async () => {
    if (!backstory.trim()) return;

    setIsGenerating(true);
    setConcepts([]);
    setSelectedIndex(null);

    // Simulate generation time (real system would call LLM)
    await new Promise((resolve) => setTimeout(resolve, 800));

    const newConcepts = generateConcepts(backstory);
    setConcepts(newConcepts);
    setIsGenerating(false);
  }, [backstory]);

  const handleAccept = useCallback(async () => {
    if (selectedIndex === null || !concepts[selectedIndex]) return;

    const concept = concepts[selectedIndex];

    // Emit witness mark for the acceptance decision (real API)
    try {
      await emitMutationMark(
        {
          id: concept.sprite.id,
          timestamp: new Date().toISOString(),
          change_description: `Created ${concept.animalTheme} character from backstory`,
          aesthetic_weights: concept.sprite.weights,
          galois_loss: concept.galoisLoss,
          status: 'accepted',
        },
        {
          reason: concept.rationale.slice(0, 100),
          affected_dimensions: ['theme', 'palette', 'silhouette'],
        },
        'accepted'
      );
    } catch (error) {
      console.error('Failed to emit mark:', error);
      // Continue anyway—UI should still work
    }

    onAccept(concept.sprite, concept.rationale);
  }, [selectedIndex, concepts, onAccept]);

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
      <div className="bg-slate-800 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-amber-300">
            ✨ Create a Character
          </h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-2xl"
          >
            ×
          </button>
        </div>

        {/* Backstory Input */}
        <div className="mb-6">
          <label className="block text-slate-300 mb-2 text-sm">
            Tell me about your character... their history, personality, dreams, fears.
          </label>
          <textarea
            value={backstory}
            onChange={(e) => setBackstory(e.target.value)}
            placeholder="A retired palace guard who saw too much and now protects the streets instead. She's tough but kind, haunted by the past but hopeful about the future..."
            className="w-full h-32 bg-slate-700 text-white rounded-lg p-4 resize-none focus:ring-2 focus:ring-amber-400 focus:outline-none"
          />
          <p className="text-slate-500 text-xs mt-2">
            I'll propose fox, kitten, and seal interpretations—each with a playful twist.
          </p>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={!backstory.trim() || isGenerating}
          className="w-full bg-amber-500 hover:bg-amber-400 disabled:bg-slate-600 text-slate-900 font-bold py-3 rounded-lg mb-6 transition-colors"
        >
          {isGenerating ? '✨ Discovering characters...' : '🦊 Propose Characters'}
        </button>

        {/* Concepts Grid */}
        {concepts.length > 0 && (
          <div className="grid md:grid-cols-3 gap-4 mb-6">
            {concepts.map((concept, index) => (
              <div
                key={concept.sprite.id}
                onClick={() => setSelectedIndex(index)}
                className={`bg-slate-700 rounded-lg p-4 cursor-pointer transition-all ${
                  selectedIndex === index
                    ? 'ring-2 ring-amber-400 bg-slate-600'
                    : 'hover:bg-slate-650'
                }`}
              >
                {/* Sprite Preview */}
                <div className="flex justify-center mb-4">
                  <SpriteCanvas
                    sprite={concept.sprite}
                    scale={10}
                    animating={selectedIndex === index}
                  />
                </div>

                {/* Theme Badge */}
                <div className="flex items-center gap-2 mb-2">
                  <span
                    className={`px-2 py-1 rounded text-xs font-bold ${
                      concept.animalTheme === 'fox'
                        ? 'bg-orange-500/20 text-orange-300'
                        : concept.animalTheme === 'kitten'
                        ? 'bg-pink-500/20 text-pink-300'
                        : 'bg-blue-500/20 text-blue-300'
                    }`}
                  >
                    {concept.animalTheme === 'fox' && '🦊 Fox'}
                    {concept.animalTheme === 'kitten' && '🐱 Kitten'}
                    {concept.animalTheme === 'seal' && '🦭 Seal'}
                  </span>
                  {concept.galoisLoss > 0.3 && (
                    <span className="px-2 py-1 rounded text-xs bg-purple-500/20 text-purple-300">
                      Wild interpretation
                    </span>
                  )}
                </div>

                {/* Rationale (L4) */}
                <p className="text-slate-300 text-sm mb-3 italic">
                  "{concept.rationale.slice(0, 150)}..."
                </p>

                {/* Personality Note (L3) */}
                <p className="text-slate-400 text-xs">
                  {concept.personalityNote}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Accept Button */}
        {selectedIndex !== null && (
          <button
            onClick={handleAccept}
            className="w-full bg-green-600 hover:bg-green-500 text-white font-bold py-3 rounded-lg transition-colors"
          >
            ✅ Accept this {concepts[selectedIndex]?.animalTheme} character
          </button>
        )}
      </div>
    </div>
  );
}

export default CharacterProposer;
