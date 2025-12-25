/**
 * GLYPH SHOWCASE
 *
 * Visual demonstration of the kgents glyph system.
 * Use this component for testing and documentation.
 *
 * Usage:
 *   import { GlyphShowcase } from '@/components/icons/GlyphShowcase';
 *   <GlyphShowcase />
 */

import React from 'react';
import { Glyph, GLYPH_CATEGORIES, getGlyphCategory } from './index';
import './glyph-showcase.css';

export const GlyphShowcase: React.FC = () => {
  return (
    <div className="glyph-showcase">
      <header className="glyph-showcase__header">
        <h1 className="glyph-showcase__title">
          <Glyph name="axioms.morphism" size="lg" className="glyph--glow" />
          {' '}kgents Glyph System
        </h1>
        <p className="glyph-showcase__subtitle">
          Mathematical notation meets ancient glyphs. Stillness, then life.
        </p>
      </header>

      {GLYPH_CATEGORIES.map((category) => {
        const glyphs = getGlyphCategory(category);
        return (
          <section key={category} className="glyph-showcase__section">
            <h2 className="glyph-showcase__category-title">
              {category}
            </h2>
            <div className="glyph-showcase__grid">
              {Object.entries(glyphs).map(([name, glyph]) => (
                <div key={name} className="glyph-showcase__item">
                  <div className="glyph-showcase__glyph-display">
                    <Glyph
                      name={`${category}.${name}`}
                      size="lg"
                      className="glyph--hover-glow"
                    />
                  </div>
                  <div className="glyph-showcase__glyph-info">
                    <code className="glyph-showcase__glyph-name">{name}</code>
                    <span className="glyph-showcase__glyph-char">{glyph}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        );
      })}

      <section className="glyph-showcase__section">
        <h2 className="glyph-showcase__category-title">Size Variants</h2>
        <div className="glyph-showcase__size-demo">
          <div className="glyph-showcase__size-item">
            <Glyph name="status.healthy" size="xs" className="glyph--healthy" />
            <span>xs (10px)</span>
          </div>
          <div className="glyph-showcase__size-item">
            <Glyph name="status.healthy" size="sm" className="glyph--healthy" />
            <span>sm (12px)</span>
          </div>
          <div className="glyph-showcase__size-item">
            <Glyph name="status.healthy" size="md" className="glyph--healthy" />
            <span>md (14px)</span>
          </div>
          <div className="glyph-showcase__size-item">
            <Glyph name="status.healthy" size="lg" className="glyph--healthy" />
            <span>lg (18px)</span>
          </div>
        </div>
      </section>

      <section className="glyph-showcase__section">
        <h2 className="glyph-showcase__category-title">Breathing Animation (4-7-8)</h2>
        <div className="glyph-showcase__breathing-demo">
          <div className="glyph-showcase__breathing-item">
            <Glyph name="jewels.brain" size="lg" breathing className="glyph--life" />
            <span>Brain (breathing)</span>
          </div>
          <div className="glyph-showcase__breathing-item">
            <Glyph name="status.healthy" size="lg" breathing className="glyph--healthy" />
            <span>Healthy (breathing)</span>
          </div>
          <div className="glyph-showcase__breathing-item">
            <Glyph name="actions.witness" size="lg" breathing className="glyph--glow" />
            <span>Witness (breathing)</span>
          </div>
        </div>
        <p className="glyph-showcase__breathing-note">
          4-7-8 asymmetric timing: rest → gentle rise → brief hold → slow release
        </p>
      </section>

      <section className="glyph-showcase__section">
        <h2 className="glyph-showcase__category-title">Color Utilities</h2>
        <div className="glyph-showcase__color-demo">
          <div className="glyph-showcase__color-item">
            <Glyph name="axioms.entity" size="lg" className="glyph--steel" />
            <span>steel</span>
          </div>
          <div className="glyph-showcase__color-item">
            <Glyph name="axioms.entity" size="lg" className="glyph--life" />
            <span>life</span>
          </div>
          <div className="glyph-showcase__color-item">
            <Glyph name="axioms.entity" size="lg" className="glyph--glow" />
            <span>glow</span>
          </div>
          <div className="glyph-showcase__color-item">
            <Glyph name="status.healthy" size="lg" className="glyph--healthy" />
            <span>healthy</span>
          </div>
          <div className="glyph-showcase__color-item">
            <Glyph name="status.degraded" size="lg" className="glyph--degraded" />
            <span>degraded</span>
          </div>
          <div className="glyph-showcase__color-item">
            <Glyph name="status.warning" size="lg" className="glyph--warning" />
            <span>warning</span>
          </div>
          <div className="glyph-showcase__color-item">
            <Glyph name="status.error" size="lg" className="glyph--critical" />
            <span>critical</span>
          </div>
        </div>
      </section>
    </div>
  );
};

export default GlyphShowcase;
