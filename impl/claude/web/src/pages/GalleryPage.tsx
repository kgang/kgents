/**
 * GalleryPage: Component Gallery for kgents foundation primitives.
 *
 * Post-surgical refactor: Simplified to showcase elastic, joy, and projection primitives.
 */

import { Link } from 'react-router-dom';
import { ElasticCard } from '@/components/elastic';
import { PersonalityLoading, Breathe, Pop, EmpathyError } from '@/components/joy';

const GALLERY_SECTIONS = [
  {
    title: 'Elastic Primitives',
    route: '/_/gallery/layout',
    description: 'Density-aware layout components: ElasticContainer, ElasticCard, ElasticSplit',
  },
  {
    title: 'Joy Animations',
    route: '/_/gallery/interactive-text',
    description: 'Delightful animations: Breathe, Pop, Shake, Shimmer, PersonalityLoading',
  },
];

export default function GalleryPage() {
  return (
    <div className="min-h-screen bg-surface-canvas p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-text-primary mb-2">Component Gallery</h1>
        <p className="text-text-secondary mb-8">
          Foundation primitives for kgents web. Surgical refactor 2025-12-22.
        </p>

        {/* Section Links */}
        <div className="grid gap-4 mb-12">
          {GALLERY_SECTIONS.map((section) => (
            <Link key={section.route} to={section.route}>
              <Pop trigger={true} scale={1.02}>
                <ElasticCard className="p-6 hover:border-copper-500 transition-colors">
                  <h2 className="text-xl font-semibold text-text-primary">{section.title}</h2>
                  <p className="text-text-secondary mt-1">{section.description}</p>
                </ElasticCard>
              </Pop>
            </Link>
          ))}
        </div>

        {/* Quick Demo */}
        <h2 className="text-xl font-semibold text-text-primary mb-4">Quick Demo</h2>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Loading States */}
          <ElasticCard className="p-6">
            <h3 className="font-medium mb-4">PersonalityLoading</h3>
            <div className="flex gap-4 justify-center">
              <PersonalityLoading jewel="brain" size="md" />
              <PersonalityLoading jewel="gestalt" size="md" />
              <PersonalityLoading jewel="forge" size="md" />
            </div>
          </ElasticCard>

          {/* Breathing */}
          <ElasticCard className="p-6">
            <h3 className="font-medium mb-4">Breathe Animation</h3>
            <div className="flex gap-4 justify-center">
              <Breathe intensity={0.5}>
                <div className="w-16 h-16 rounded-full bg-sage-500" />
              </Breathe>
              <Breathe intensity={0.3} speed="slow">
                <div className="w-16 h-16 rounded-lg bg-copper-500" />
              </Breathe>
            </div>
          </ElasticCard>

          {/* Error State */}
          <ElasticCard className="p-6 md:col-span-2">
            <h3 className="font-medium mb-4">EmpathyError</h3>
            <EmpathyError
              type="network"
              title="Connection Lost"
              subtitle="We're having trouble reaching the server"
              size="sm"
            />
          </ElasticCard>
        </div>
      </div>
    </div>
  );
}
