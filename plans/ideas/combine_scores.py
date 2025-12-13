#!/usr/bin/env python3
"""
Combine K-Score evaluations from four philosopher perspectives.

Each philosopher (Cobalt Spinoza, Indigo Whitehead, Obsidian Deleuze, Ochre Weil)
evaluated the same ideas. This script:
1. Loads all four CSVs
2. Normalizes idea names for matching
3. Averages scores across all perspectives
4. Recalculates K-score from averaged dimensions
5. Outputs combined analysis
"""

import csv
import json
import re
from collections import defaultdict
from pathlib import Path
import math

def normalize_name(name: str) -> str:
    """Normalize idea name for matching across files."""
    # Lowercase, remove extra whitespace
    name = name.lower().strip()
    # Remove common suffixes/variations
    name = re.sub(r'\s+tui$', '', name)
    name = re.sub(r'\s+cli$', '', name)
    name = re.sub(r'\s+visual$', '', name)
    name = re.sub(r'\s+visualizer$', '', name)
    # Remove punctuation except hyphens
    name = re.sub(r'[^\w\s-]', '', name)
    # Normalize whitespace
    name = re.sub(r'\s+', ' ', name)
    return name

def calculate_k_score(joy, comp, taste, compression, showable, complexity):
    """Calculate K-score using the official formula."""
    gen_mult = 1 + (compression * 0.3) + (showable * 0.2)
    taste_power = math.pow(taste, 1.4)
    numerator = (joy * 2 + comp * 1.5 + taste_power) * gen_mult
    denominator = (complexity * 0.7) + 1
    return numerator / denominator

def get_category(score):
    """Get K-score category."""
    if score >= 40:
        return "Crown Jewel"
    elif score >= 25:
        return "Strong Win"
    elif score >= 15:
        return "Solid"
    elif score >= 8:
        return "Consider"
    return "Reconsider"

def load_cobalt(filepath):
    """Load cobalt_spinoza.csv."""
    ideas = {}
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['idea_name']
            norm_name = normalize_name(name)
            ideas[norm_name] = {
                'original_name': name,
                'session': row['session'],
                'joy': float(row['joy']),
                'composability': float(row['composability']),
                'taste': float(row['taste']),
                'compression': float(row['compression']),
                'showable': float(row['showable']),
                'ethical': float(row['ethical']),
                'complexity': float(row['complexity']),
                'k_score': float(row['k_score']),
                'category': row.get('category', ''),
            }
    return ideas

def load_obsidian(filepath):
    """Load obsidian_deleuze.csv."""
    ideas = {}
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip comment rows
            if row['idea_name'].startswith('#'):
                continue
            name = row['idea_name']
            norm_name = normalize_name(name)
            ideas[norm_name] = {
                'original_name': name,
                'session': row['source_session'],
                'joy': float(row['joy']),
                'composability': float(row['composability']),
                'taste': float(row['taste']),
                'compression': float(row['compression']),
                'showable': float(row['showable']),
                'ethical': float(row['ethical']),
                'complexity': float(row['complexity']),
                'k_score': float(row['k_score']),
                'category': row.get('category', ''),
            }
    return ideas

def load_ochre(filepath):
    """Load ochre_weil.csv."""
    ideas = {}
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name']
            norm_name = normalize_name(name)
            ideas[norm_name] = {
                'original_name': name,
                'session': row['session'],
                'category_domain': row['category'],
                'joy': float(row['Joy']),
                'composability': float(row['Composability']),
                'taste': float(row['Taste']),
                'compression': float(row['Compression']),
                'showable': float(row['Showable']),
                'ethical': float(row['Ethical']),
                'complexity': float(row['Complexity']),
                'k_score': float(row['K_Score']),
            }
    return ideas

def load_indigo(filepath):
    """Load indigo_whitehead.csv."""
    ideas = {}
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['Idea_Name']
            norm_name = normalize_name(name)
            ideas[norm_name] = {
                'original_name': name,
                'session': row['Session'],
                'description': row.get('Description', ''),
                'joy': float(row['Joy']),
                'composability': float(row['Composability']),
                'taste': float(row['Taste']),
                'compression': float(row['Compression']),
                'showable': float(row['Showable']),
                'ethical': float(row['Ethical']),
                'complexity': float(row['Complexity']),
                'k_score': float(row['K_Score']),
                'category': row.get('Category', ''),
            }
    return ideas

def main():
    base_path = Path(__file__).parent

    # Load all four perspectives
    print("Loading philosopher perspectives...")
    cobalt = load_cobalt(base_path / 'cobalt_spinoza.csv')
    obsidian = load_obsidian(base_path / 'obsidian_deleuze.csv')
    ochre = load_ochre(base_path / 'ochre_weil.csv')
    indigo = load_indigo(base_path / 'indigo_whitehead.csv')

    print(f"  Cobalt Spinoza:    {len(cobalt)} ideas")
    print(f"  Obsidian Deleuze:  {len(obsidian)} ideas")
    print(f"  Ochre Weil:        {len(ochre)} ideas")
    print(f"  Indigo Whitehead:  {len(indigo)} ideas")

    # Find all unique normalized names
    all_names = set(cobalt.keys()) | set(obsidian.keys()) | set(ochre.keys()) | set(indigo.keys())
    print(f"\nTotal unique ideas (normalized): {len(all_names)}")

    # Combine scores
    combined = {}
    perspective_counts = defaultdict(int)

    for norm_name in all_names:
        perspectives = []
        original_name = None
        session = None
        category_domain = None
        description = None

        if norm_name in cobalt:
            perspectives.append(('Cobalt Spinoza', cobalt[norm_name]))
            original_name = cobalt[norm_name]['original_name']
            session = cobalt[norm_name]['session']
        if norm_name in obsidian:
            perspectives.append(('Obsidian Deleuze', obsidian[norm_name]))
            if not original_name:
                original_name = obsidian[norm_name]['original_name']
                session = obsidian[norm_name]['session']
        if norm_name in ochre:
            perspectives.append(('Ochre Weil', ochre[norm_name]))
            if not original_name:
                original_name = ochre[norm_name]['original_name']
                session = ochre[norm_name]['session']
            category_domain = ochre[norm_name].get('category_domain', '')
        if norm_name in indigo:
            perspectives.append(('Indigo Whitehead', indigo[norm_name]))
            if not original_name:
                original_name = indigo[norm_name]['original_name']
                session = indigo[norm_name]['session']
            description = indigo[norm_name].get('description', '')

        perspective_counts[len(perspectives)] += 1

        # Average all dimensions
        n = len(perspectives)
        avg_joy = sum(p[1]['joy'] for p in perspectives) / n
        avg_comp = sum(p[1]['composability'] for p in perspectives) / n
        avg_taste = sum(p[1]['taste'] for p in perspectives) / n
        avg_compression = sum(p[1]['compression'] for p in perspectives) / n
        avg_showable = sum(p[1]['showable'] for p in perspectives) / n
        avg_ethical = sum(p[1]['ethical'] for p in perspectives) / n
        avg_complexity = sum(p[1]['complexity'] for p in perspectives) / n

        # Individual k_scores for comparison
        individual_scores = [p[1]['k_score'] for p in perspectives]
        avg_individual_k = sum(individual_scores) / n

        # Recalculate k_score from averaged dimensions
        recalc_k = calculate_k_score(
            avg_joy, avg_comp, avg_taste,
            avg_compression, avg_showable, avg_complexity
        )

        combined[norm_name] = {
            'name': original_name,
            'normalized_name': norm_name,
            'session': session,
            'category_domain': category_domain,
            'description': description,
            'num_perspectives': n,
            'perspectives': [p[0] for p in perspectives],
            'joy': round(avg_joy, 2),
            'composability': round(avg_comp, 2),
            'taste': round(avg_taste, 2),
            'compression': round(avg_compression, 2),
            'showable': round(avg_showable, 2),
            'ethical': round(avg_ethical, 2),
            'complexity': round(avg_complexity, 2),
            'individual_k_scores': [round(s, 2) for s in individual_scores],
            'avg_individual_k': round(avg_individual_k, 2),
            'recalculated_k': round(recalc_k, 2),
            'k_score_variance': round(max(individual_scores) - min(individual_scores), 2) if n > 1 else 0,
            'category': get_category(recalc_k),
        }

    print(f"\nPerspective coverage:")
    for n in sorted(perspective_counts.keys()):
        print(f"  {n} perspectives: {perspective_counts[n]} ideas")

    # Sort by recalculated k_score
    sorted_ideas = sorted(combined.values(), key=lambda x: x['recalculated_k'], reverse=True)

    # Calculate aggregate stats
    all_k_scores = [idea['recalculated_k'] for idea in sorted_ideas]
    avg_k = sum(all_k_scores) / len(all_k_scores)

    category_counts = defaultdict(int)
    for idea in sorted_ideas:
        category_counts[idea['category']] += 1

    avg_dims = {
        'joy': sum(idea['joy'] for idea in sorted_ideas) / len(sorted_ideas),
        'composability': sum(idea['composability'] for idea in sorted_ideas) / len(sorted_ideas),
        'taste': sum(idea['taste'] for idea in sorted_ideas) / len(sorted_ideas),
        'compression': sum(idea['compression'] for idea in sorted_ideas) / len(sorted_ideas),
        'showable': sum(idea['showable'] for idea in sorted_ideas) / len(sorted_ideas),
        'ethical': sum(idea['ethical'] for idea in sorted_ideas) / len(sorted_ideas),
        'complexity': sum(idea['complexity'] for idea in sorted_ideas) / len(sorted_ideas),
    }

    # High variance ideas (where philosophers disagreed most)
    high_variance = sorted(
        [i for i in sorted_ideas if i['num_perspectives'] > 1],
        key=lambda x: x['k_score_variance'],
        reverse=True
    )[:20]

    # Ideas with 4 perspectives (most reliable)
    four_perspective = [i for i in sorted_ideas if i['num_perspectives'] == 4]

    output = {
        'summary': {
            'total_unique_ideas': len(sorted_ideas),
            'average_k_score': round(avg_k, 2),
            'category_distribution': dict(category_counts),
            'perspective_coverage': dict(perspective_counts),
            'average_dimensions': {k: round(v, 2) for k, v in avg_dims.items()},
        },
        'top_ideas': sorted_ideas[:50],
        'high_variance_ideas': high_variance,
        'four_perspective_ideas': four_perspective[:30],
        'all_ideas': sorted_ideas,
    }

    # Write JSON output
    output_path = base_path / 'combined_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nWrote combined analysis to: {output_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("COMBINED ANALYSIS SUMMARY")
    print(f"{'='*60}")
    print(f"Total unique ideas: {len(sorted_ideas)}")
    print(f"Average K-Score: {avg_k:.2f}")
    print(f"\nCategory Distribution:")
    for cat in ['Crown Jewel', 'Strong Win', 'Solid', 'Consider', 'Reconsider']:
        count = category_counts.get(cat, 0)
        pct = count / len(sorted_ideas) * 100
        bar = '█' * int(pct / 2)
        print(f"  {cat:15} {count:4} ({pct:5.1f}%) {bar}")

    print(f"\nAverage Dimensions:")
    for dim, val in avg_dims.items():
        bar = '█' * int(val * 4)
        print(f"  {dim:15} {val:.2f} {bar}")

    print(f"\nTop 10 Ideas (by recalculated K-Score):")
    for i, idea in enumerate(sorted_ideas[:10], 1):
        persp = f"[{idea['num_perspectives']}p]"
        print(f"  {i:2}. {idea['recalculated_k']:5.1f} {persp} {idea['name']}")

    print(f"\nHighest Variance (philosophers disagreed most):")
    for idea in high_variance[:5]:
        scores = idea['individual_k_scores']
        print(f"  {idea['name'][:40]:40} var={idea['k_score_variance']:.1f} scores={scores}")

if __name__ == '__main__':
    main()
