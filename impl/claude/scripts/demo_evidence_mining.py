#!/usr/bin/env python3
"""
Evidence Mining Demo: Mine git repository for development patterns.

This demonstrates the RepositoryMiner capabilities on the kgents repository.

Usage:
    python scripts/demo_evidence_mining.py
"""

from services.evidence.mining import RepositoryMiner


def main():
    print("=" * 80)
    print("EVIDENCE MINING DEMO")
    print("=" * 80)
    print()

    # Initialize miner
    repo_path = "/Users/kentgang/git/kgents"
    miner = RepositoryMiner(repo_path)
    print(f"Mining repository: {repo_path}")
    print()

    # =========================================================================
    # 1. Commit Patterns
    # =========================================================================
    print("-" * 80)
    print("1. COMMIT PATTERNS")
    print("-" * 80)

    patterns = miner.mine_commit_patterns(max_commits=200)
    print(f"Total commits analyzed: {patterns.total_commits}")
    print(f"Date range: {patterns.date_range[0].date()} to {patterns.date_range[1].date()}" if patterns.date_range else "N/A")
    print(f"Average commit size: {patterns.avg_commit_size:.1f} lines")
    print(f"Median commit size: {patterns.median_commit_size:.1f} lines")
    print(f"Quality score: {patterns.quality_score:.2f}")
    print(f"Weekend commits: {patterns.weekend_ratio * 100:.1f}%")
    print()
    print("Commit types:")
    for ctype, count in sorted(patterns.commit_types.items(), key=lambda x: -x[1])[:5]:
        print(f"  - {ctype}: {count}")
    print()

    # =========================================================================
    # 2. File Churn
    # =========================================================================
    print("-" * 80)
    print("2. FILE CHURN & COUPLING")
    print("-" * 80)

    churn = miner.mine_file_churn(max_commits=200, top_n=10)
    print(f"Top {len(churn)} files by churn:")
    for i, metric in enumerate(churn, 1):
        print(f"\n{i}. {metric.path}")
        print(f"   Commits: {metric.commit_count}")
        print(f"   Total churn: {metric.total_churn:,} lines")
        print(f"   Avg churn/commit: {metric.avg_churn_per_commit:.1f} lines")
        print(f"   Authors: {len(metric.authors)}")
        print(f"   Coupling: {metric.coupling_strength:.2f}")
        if metric.coupled_files:
            print(f"   Coupled with: {', '.join(metric.coupled_files[:2])}")
    print()

    # =========================================================================
    # 3. Author Patterns
    # =========================================================================
    print("-" * 80)
    print("3. AUTHOR PATTERNS")
    print("-" * 80)

    authors = miner.mine_author_patterns(max_commits=200)
    print(f"Total authors: {len(authors)}")
    print()
    for i, author in enumerate(authors[:3], 1):
        print(f"{i}. {author.author}")
        print(f"   Commits: {author.total_commits}")
        print(f"   Owned files: {len(author.owned_files)}")
        print(f"   Specialization: {author.specialization_score:.2f} (0=generalist, 1=specialist)")
        print(f"   Primary domains: {', '.join(author.primary_domains[:3])}")
        print(f"   Avg commit size: {author.avg_commit_size:.1f} lines")
        if author.commit_type_distribution:
            top_types = sorted(author.commit_type_distribution.items(), key=lambda x: -x[1])[:3]
            print(f"   Top types: {', '.join(f'{t}({c})' for t, c in top_types)}")
        print()

    # =========================================================================
    # 4. Bug Correlations
    # =========================================================================
    print("-" * 80)
    print("4. BUG CORRELATIONS")
    print("-" * 80)

    bugs = miner.mine_bug_correlations(max_commits=200)
    print(f"Total fixes: {bugs.total_fixes}")
    print(f"Fix ratio: {bugs.fix_ratio * 100:.1f}%")
    print(f"Quality trend: {bugs.quality_trend}")
    print(f"Feature→Fix lag: {bugs.fix_to_feature_lag:.1f} commits")
    print()
    print("Bug-prone files (top 5):")
    for i, file_path in enumerate(bugs.bug_prone_files[:5], 1):
        print(f"  {i}. {file_path}")
    print()
    print("Fix commit sizes:")
    for category, avg_size in bugs.fix_commit_sizes.items():
        print(f"  - {category}: {avg_size:.1f} lines avg")
    print()
    if bugs.regression_indicators:
        print("Regression indicators (commits with 2+ subsequent fixes):")
        for sha in bugs.regression_indicators:
            print(f"  - {sha[:8]}")
    print()

    print("=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
