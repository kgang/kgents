"""Create Crown Jewel tables for all seven jewels.

Revision ID: 002
Revises: 001
Create Date: 2025-12-17

Tables for the Seven Crown Jewels:
- Brain: brain_crystals, brain_crystal_tags, brain_settings
- Town: town_citizens, town_conversations, town_conversation_turns, town_citizen_relationships
- Gardener: garden_sessions, garden_ideas, garden_plots, garden_idea_connections
- Gestalt: gestalt_topologies, gestalt_code_blocks, gestalt_code_links, gestalt_topology_snapshots
- Atelier: atelier_workshops, atelier_artisans, atelier_exhibitions, atelier_gallery_items, atelier_artifact_contributions
- Coalition: coalition_coalitions, coalition_members, coalition_proposals, coalition_proposal_votes, coalition_outputs
- Park: park_hosts, park_host_memories, park_episodes, park_interactions, park_locations

AGENTESE: self.data.table.* persistence layer
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================================
    # BRAIN CROWN JEWEL
    # =========================================================================

    # brain_crystals: Crystallized knowledge with queryable metadata
    op.execute("""
        CREATE TABLE IF NOT EXISTS brain_crystals (
            id TEXT PRIMARY KEY,
            content_hash TEXT NOT NULL,
            summary TEXT NOT NULL,
            tags TEXT DEFAULT '[]',
            access_count INTEGER DEFAULT 0,
            last_accessed TEXT,
            datum_id TEXT,
            source_type TEXT,
            source_ref TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_brain_crystals_hash ON brain_crystals(content_hash)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_brain_crystals_datum ON brain_crystals(datum_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_brain_crystals_recent ON brain_crystals(created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_brain_crystals_accessed ON brain_crystals(last_accessed)")

    # brain_crystal_tags: Normalized tags for efficient queries
    op.execute("""
        CREATE TABLE IF NOT EXISTS brain_crystal_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crystal_id TEXT NOT NULL,
            tag TEXT NOT NULL,
            FOREIGN KEY (crystal_id) REFERENCES brain_crystals(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_crystal_tags_tag ON brain_crystal_tags(tag)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_crystal_tags_lookup ON brain_crystal_tags(tag, crystal_id)")

    # brain_settings: User preferences for Brain behavior
    op.execute("""
        CREATE TABLE IF NOT EXISTS brain_settings (
            id TEXT PRIMARY KEY DEFAULT 'default',
            default_tags TEXT DEFAULT '[]',
            retention_days INTEGER,
            max_crystals INTEGER,
            config TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # =========================================================================
    # TOWN CROWN JEWEL
    # =========================================================================

    # town_citizens: Agent citizens with persistent memory
    op.execute("""
        CREATE TABLE IF NOT EXISTS town_citizens (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            archetype TEXT NOT NULL,
            description TEXT,
            traits TEXT DEFAULT '{}',
            is_active INTEGER DEFAULT 1,
            last_interaction TEXT,
            interaction_count INTEGER DEFAULT 0,
            memory_datum_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_town_citizens_name ON town_citizens(name)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_town_citizens_archetype ON town_citizens(archetype)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_town_citizens_active ON town_citizens(is_active)")

    # town_conversations: Conversation sessions with citizens
    op.execute("""
        CREATE TABLE IF NOT EXISTS town_conversations (
            id TEXT PRIMARY KEY,
            citizen_id TEXT NOT NULL,
            topic TEXT,
            summary TEXT,
            turn_count INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            datum_chain_head TEXT,
            causal_parent TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (citizen_id) REFERENCES town_citizens(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_town_conversations_citizen ON town_conversations(citizen_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_town_conversations_active ON town_conversations(is_active)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_town_conversations_recent ON town_conversations(created_at)")

    # town_conversation_turns: Individual turns in conversations
    op.execute("""
        CREATE TABLE IF NOT EXISTS town_conversation_turns (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            turn_number INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            sentiment TEXT,
            emotion TEXT,
            causal_parent TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES town_conversations(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_town_turns_conversation ON town_conversation_turns(conversation_id, turn_number)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_town_turns_causal ON town_conversation_turns(causal_parent)")

    # town_citizen_relationships: Relationships between citizens
    op.execute("""
        CREATE TABLE IF NOT EXISTS town_citizen_relationships (
            id TEXT PRIMARY KEY,
            citizen_a_id TEXT NOT NULL,
            citizen_b_id TEXT NOT NULL,
            relationship_type TEXT NOT NULL,
            strength REAL DEFAULT 0.5,
            interaction_count INTEGER DEFAULT 0,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (citizen_a_id) REFERENCES town_citizens(id) ON DELETE CASCADE,
            FOREIGN KEY (citizen_b_id) REFERENCES town_citizens(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_relationships_citizens ON town_citizen_relationships(citizen_a_id, citizen_b_id)")

    # =========================================================================
    # GARDENER CROWN JEWEL
    # =========================================================================

    # garden_sessions: Gardening sessions
    op.execute("""
        CREATE TABLE IF NOT EXISTS garden_sessions (
            id TEXT PRIMARY KEY,
            title TEXT,
            notes TEXT,
            duration_seconds INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_garden_sessions_recent ON garden_sessions(created_at)")

    # garden_plots: Thematic groupings of ideas
    op.execute("""
        CREATE TABLE IF NOT EXISTS garden_plots (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            color TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_garden_plots_name ON garden_plots(name)")

    # garden_ideas: Ideas with lifecycle stages
    op.execute("""
        CREATE TABLE IF NOT EXISTS garden_ideas (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            lifecycle TEXT DEFAULT 'SEED',
            confidence REAL DEFAULT 0.3,
            session_id TEXT,
            last_nurtured TEXT,
            nurture_count INTEGER DEFAULT 0,
            plot_id TEXT,
            datum_id TEXT,
            tags TEXT DEFAULT '[]',
            causal_parent TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES garden_sessions(id) ON DELETE SET NULL,
            FOREIGN KEY (plot_id) REFERENCES garden_plots(id) ON DELETE SET NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_garden_ideas_lifecycle ON garden_ideas(lifecycle)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_garden_ideas_confidence ON garden_ideas(confidence)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_garden_ideas_plot ON garden_ideas(plot_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_garden_ideas_datum ON garden_ideas(datum_id)")

    # garden_idea_connections: Connections between ideas
    op.execute("""
        CREATE TABLE IF NOT EXISTS garden_idea_connections (
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            connection_type TEXT NOT NULL,
            strength REAL DEFAULT 0.5,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (source_id) REFERENCES garden_ideas(id) ON DELETE CASCADE,
            FOREIGN KEY (target_id) REFERENCES garden_ideas(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_garden_connections_source ON garden_idea_connections(source_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_garden_connections_target ON garden_idea_connections(target_id)")

    # =========================================================================
    # GESTALT CROWN JEWEL
    # =========================================================================

    # gestalt_topologies: Code topology snapshots
    op.execute("""
        CREATE TABLE IF NOT EXISTS gestalt_topologies (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            repo_path TEXT,
            git_ref TEXT,
            layout TEXT DEFAULT '{}',
            viewport TEXT DEFAULT '{}',
            block_count INTEGER DEFAULT 0,
            link_count INTEGER DEFAULT 0,
            complexity_score REAL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_gestalt_topologies_name ON gestalt_topologies(name)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_gestalt_topologies_repo ON gestalt_topologies(repo_path)")

    # gestalt_code_blocks: Code blocks in topologies
    op.execute("""
        CREATE TABLE IF NOT EXISTS gestalt_code_blocks (
            id TEXT PRIMARY KEY,
            topology_id TEXT NOT NULL,
            name TEXT NOT NULL,
            block_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            line_start INTEGER,
            line_end INTEGER,
            x REAL DEFAULT 0.0,
            y REAL DEFAULT 0.0,
            z REAL DEFAULT 0.0,
            test_coverage REAL,
            complexity REAL,
            churn_rate REAL,
            content_hash TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (topology_id) REFERENCES gestalt_topologies(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_gestalt_blocks_topology ON gestalt_code_blocks(topology_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_gestalt_blocks_file ON gestalt_code_blocks(file_path)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_gestalt_blocks_type ON gestalt_code_blocks(block_type)")

    # gestalt_code_links: Links between code blocks
    op.execute("""
        CREATE TABLE IF NOT EXISTS gestalt_code_links (
            id TEXT PRIMARY KEY,
            topology_id TEXT NOT NULL,
            source_block_id TEXT NOT NULL,
            target_block_id TEXT NOT NULL,
            link_type TEXT NOT NULL,
            strength REAL DEFAULT 1.0,
            call_count INTEGER,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (topology_id) REFERENCES gestalt_topologies(id) ON DELETE CASCADE,
            FOREIGN KEY (source_block_id) REFERENCES gestalt_code_blocks(id) ON DELETE CASCADE,
            FOREIGN KEY (target_block_id) REFERENCES gestalt_code_blocks(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_gestalt_links_topology ON gestalt_code_links(topology_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_gestalt_links_source ON gestalt_code_links(source_block_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_gestalt_links_target ON gestalt_code_links(target_block_id)")

    # gestalt_topology_snapshots: Historical snapshots
    op.execute("""
        CREATE TABLE IF NOT EXISTS gestalt_topology_snapshots (
            id TEXT PRIMARY KEY,
            topology_id TEXT NOT NULL,
            git_ref TEXT,
            block_count INTEGER DEFAULT 0,
            link_count INTEGER DEFAULT 0,
            complexity_score REAL,
            state_json TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (topology_id) REFERENCES gestalt_topologies(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_gestalt_snapshots_topology ON gestalt_topology_snapshots(topology_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_gestalt_snapshots_created ON gestalt_topology_snapshots(created_at)")

    # =========================================================================
    # ATELIER CROWN JEWEL
    # =========================================================================

    # atelier_workshops: Creative workshops
    op.execute("""
        CREATE TABLE IF NOT EXISTS atelier_workshops (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            theme TEXT,
            is_active INTEGER DEFAULT 1,
            started_at TEXT,
            ended_at TEXT,
            config TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_atelier_workshops_active ON atelier_workshops(is_active)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_atelier_workshops_theme ON atelier_workshops(theme)")

    # atelier_artisans: Creative agents in workshops
    op.execute("""
        CREATE TABLE IF NOT EXISTS atelier_artisans (
            id TEXT PRIMARY KEY,
            workshop_id TEXT NOT NULL,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            style TEXT,
            is_active INTEGER DEFAULT 1,
            contribution_count INTEGER DEFAULT 0,
            agent_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (workshop_id) REFERENCES atelier_workshops(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_atelier_artisans_workshop ON atelier_artisans(workshop_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_atelier_artisans_specialty ON atelier_artisans(specialty)")

    # atelier_exhibitions: Exhibitions of creative work
    op.execute("""
        CREATE TABLE IF NOT EXISTS atelier_exhibitions (
            id TEXT PRIMARY KEY,
            workshop_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            curator_notes TEXT,
            is_open INTEGER DEFAULT 0,
            opened_at TEXT,
            closed_at TEXT,
            view_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (workshop_id) REFERENCES atelier_workshops(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_atelier_exhibitions_workshop ON atelier_exhibitions(workshop_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_atelier_exhibitions_open ON atelier_exhibitions(is_open)")

    # atelier_gallery_items: Items in exhibitions
    op.execute("""
        CREATE TABLE IF NOT EXISTS atelier_gallery_items (
            id TEXT PRIMARY KEY,
            exhibition_id TEXT NOT NULL,
            artifact_type TEXT NOT NULL,
            artifact_content TEXT NOT NULL,
            artifact_metadata TEXT DEFAULT '{}',
            display_order INTEGER DEFAULT 0,
            title TEXT,
            description TEXT,
            artisan_ids TEXT DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (exhibition_id) REFERENCES atelier_exhibitions(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_atelier_gallery_exhibition ON atelier_gallery_items(exhibition_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_atelier_gallery_order ON atelier_gallery_items(exhibition_id, display_order)")

    # atelier_artifact_contributions: Contributions by artisans
    op.execute("""
        CREATE TABLE IF NOT EXISTS atelier_artifact_contributions (
            id TEXT PRIMARY KEY,
            artisan_id TEXT NOT NULL,
            contribution_type TEXT NOT NULL,
            content_type TEXT NOT NULL,
            content TEXT NOT NULL,
            prompt TEXT,
            inspiration TEXT,
            notes TEXT,
            datum_id TEXT,
            causal_parent TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (artisan_id) REFERENCES atelier_artisans(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_atelier_contributions_artisan ON atelier_artifact_contributions(artisan_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_atelier_contributions_type ON atelier_artifact_contributions(contribution_type)")

    # =========================================================================
    # COALITION CROWN JEWEL
    # =========================================================================

    # coalition_coalitions: Multi-agent coalitions
    op.execute("""
        CREATE TABLE IF NOT EXISTS coalition_coalitions (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            goal TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'forming',
            formed_at TEXT,
            dissolved_at TEXT,
            min_members INTEGER DEFAULT 2,
            max_members INTEGER,
            config TEXT DEFAULT '{}',
            proposal_count INTEGER DEFAULT 0,
            consensus_threshold REAL DEFAULT 0.66,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_coalition_status ON coalition_coalitions(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_coalition_formed ON coalition_coalitions(formed_at)")

    # coalition_members: Members of coalitions
    op.execute("""
        CREATE TABLE IF NOT EXISTS coalition_members (
            id TEXT PRIMARY KEY,
            coalition_id TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            agent_type TEXT DEFAULT 'citizen',
            role TEXT DEFAULT 'member',
            voting_power REAL DEFAULT 1.0,
            can_propose INTEGER DEFAULT 1,
            can_vote INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1,
            joined_at TEXT NOT NULL,
            left_at TEXT,
            contribution_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (coalition_id) REFERENCES coalition_coalitions(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_coalition_member_agent ON coalition_members(agent_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_coalition_member_coalition ON coalition_members(coalition_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_coalition_member_role ON coalition_members(role)")

    # coalition_proposals: Proposals within coalitions
    op.execute("""
        CREATE TABLE IF NOT EXISTS coalition_proposals (
            id TEXT PRIMARY KEY,
            coalition_id TEXT NOT NULL,
            proposer_id TEXT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            proposal_type TEXT DEFAULT 'action',
            status TEXT DEFAULT 'draft',
            voting_started_at TEXT,
            voting_ended_at TEXT,
            votes_for INTEGER DEFAULT 0,
            votes_against INTEGER DEFAULT 0,
            votes_abstain INTEGER DEFAULT 0,
            approval_score REAL,
            datum_id TEXT,
            causal_parent TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (coalition_id) REFERENCES coalition_coalitions(id) ON DELETE CASCADE,
            FOREIGN KEY (proposer_id) REFERENCES coalition_members(id) ON DELETE SET NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_coalition_proposal_coalition ON coalition_proposals(coalition_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_coalition_proposal_status ON coalition_proposals(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_coalition_proposal_type ON coalition_proposals(proposal_type)")

    # coalition_proposal_votes: Votes on proposals
    op.execute("""
        CREATE TABLE IF NOT EXISTS coalition_proposal_votes (
            id TEXT PRIMARY KEY,
            proposal_id TEXT NOT NULL,
            member_id TEXT NOT NULL,
            vote TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            rationale TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (proposal_id) REFERENCES coalition_proposals(id) ON DELETE CASCADE,
            FOREIGN KEY (member_id) REFERENCES coalition_members(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_proposal_vote_proposal ON coalition_proposal_votes(proposal_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_proposal_vote_member ON coalition_proposal_votes(member_id)")

    # coalition_outputs: Outputs produced by coalitions
    op.execute("""
        CREATE TABLE IF NOT EXISTS coalition_outputs (
            id TEXT PRIMARY KEY,
            coalition_id TEXT NOT NULL,
            proposal_id TEXT,
            output_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata_json TEXT DEFAULT '{}',
            contributor_ids TEXT DEFAULT '[]',
            datum_id TEXT,
            causal_parent TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (coalition_id) REFERENCES coalition_coalitions(id) ON DELETE CASCADE,
            FOREIGN KEY (proposal_id) REFERENCES coalition_proposals(id) ON DELETE SET NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_coalition_output_coalition ON coalition_outputs(coalition_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_coalition_output_type ON coalition_outputs(output_type)")

    # =========================================================================
    # PARK CROWN JEWEL
    # =========================================================================

    # park_hosts: Hosts (agents) in the Park
    # Note: 'values' is a reserved keyword in SQLite, so we use 'host_values'
    op.execute("""
        CREATE TABLE IF NOT EXISTS park_hosts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            character TEXT NOT NULL,
            backstory TEXT,
            traits TEXT DEFAULT '{}',
            host_values TEXT DEFAULT '[]',
            host_boundaries TEXT DEFAULT '[]',
            is_active INTEGER DEFAULT 1,
            mood TEXT,
            energy_level REAL DEFAULT 1.0,
            current_location TEXT,
            interaction_count INTEGER DEFAULT 0,
            consent_refusal_count INTEGER DEFAULT 0,
            memory_datum_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_park_hosts_character ON park_hosts(character)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_park_hosts_active ON park_hosts(is_active)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_park_hosts_location ON park_hosts(current_location)")

    # park_episodes: Episodes (sessions) in the Park
    op.execute("""
        CREATE TABLE IF NOT EXISTS park_episodes (
            id TEXT PRIMARY KEY,
            visitor_id TEXT,
            visitor_name TEXT,
            title TEXT,
            summary TEXT,
            status TEXT DEFAULT 'active',
            started_at TEXT NOT NULL,
            ended_at TEXT,
            duration_seconds INTEGER,
            interaction_count INTEGER DEFAULT 0,
            hosts_met TEXT DEFAULT '[]',
            locations_visited TEXT DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_park_episodes_visitor ON park_episodes(visitor_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_park_episodes_status ON park_episodes(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_park_episodes_started ON park_episodes(started_at)")

    # park_host_memories: Memories held by hosts
    op.execute("""
        CREATE TABLE IF NOT EXISTS park_host_memories (
            id TEXT PRIMARY KEY,
            host_id TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            content TEXT NOT NULL,
            summary TEXT,
            salience REAL DEFAULT 0.5,
            emotional_valence REAL DEFAULT 0.0,
            access_count INTEGER DEFAULT 0,
            last_accessed TEXT,
            episode_id TEXT,
            visitor_id TEXT,
            datum_id TEXT,
            causal_parent TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (host_id) REFERENCES park_hosts(id) ON DELETE CASCADE,
            FOREIGN KEY (episode_id) REFERENCES park_episodes(id) ON DELETE SET NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_park_memories_host ON park_host_memories(host_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_park_memories_type ON park_host_memories(memory_type)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_park_memories_salience ON park_host_memories(salience)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_park_memories_datum ON park_host_memories(datum_id)")

    # park_interactions: Interactions between visitors and hosts
    op.execute("""
        CREATE TABLE IF NOT EXISTS park_interactions (
            id TEXT PRIMARY KEY,
            episode_id TEXT NOT NULL,
            host_id TEXT NOT NULL,
            interaction_type TEXT NOT NULL,
            visitor_input TEXT NOT NULL,
            host_response TEXT,
            consent_requested INTEGER DEFAULT 0,
            consent_given INTEGER,
            consent_reason TEXT,
            location TEXT,
            host_emotion TEXT,
            visitor_sentiment TEXT,
            causal_parent TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (episode_id) REFERENCES park_episodes(id) ON DELETE CASCADE,
            FOREIGN KEY (host_id) REFERENCES park_hosts(id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_park_interactions_episode ON park_interactions(episode_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_park_interactions_host ON park_interactions(host_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_park_interactions_type ON park_interactions(interaction_type)")

    # park_locations: Locations in the Park
    op.execute("""
        CREATE TABLE IF NOT EXISTS park_locations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            atmosphere TEXT,
            x REAL,
            y REAL,
            connected_locations TEXT DEFAULT '[]',
            is_open INTEGER DEFAULT 1,
            capacity INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_park_locations_name ON park_locations(name)")


def downgrade() -> None:
    # Park
    op.execute("DROP TABLE IF EXISTS park_locations")
    op.execute("DROP TABLE IF EXISTS park_interactions")
    op.execute("DROP TABLE IF EXISTS park_host_memories")
    op.execute("DROP TABLE IF EXISTS park_episodes")
    op.execute("DROP TABLE IF EXISTS park_hosts")

    # Coalition
    op.execute("DROP TABLE IF EXISTS coalition_outputs")
    op.execute("DROP TABLE IF EXISTS coalition_proposal_votes")
    op.execute("DROP TABLE IF EXISTS coalition_proposals")
    op.execute("DROP TABLE IF EXISTS coalition_members")
    op.execute("DROP TABLE IF EXISTS coalition_coalitions")

    # Atelier
    op.execute("DROP TABLE IF EXISTS atelier_artifact_contributions")
    op.execute("DROP TABLE IF EXISTS atelier_gallery_items")
    op.execute("DROP TABLE IF EXISTS atelier_exhibitions")
    op.execute("DROP TABLE IF EXISTS atelier_artisans")
    op.execute("DROP TABLE IF EXISTS atelier_workshops")

    # Gestalt
    op.execute("DROP TABLE IF EXISTS gestalt_topology_snapshots")
    op.execute("DROP TABLE IF EXISTS gestalt_code_links")
    op.execute("DROP TABLE IF EXISTS gestalt_code_blocks")
    op.execute("DROP TABLE IF EXISTS gestalt_topologies")

    # Gardener
    op.execute("DROP TABLE IF EXISTS garden_idea_connections")
    op.execute("DROP TABLE IF EXISTS garden_ideas")
    op.execute("DROP TABLE IF EXISTS garden_plots")
    op.execute("DROP TABLE IF EXISTS garden_sessions")

    # Town
    op.execute("DROP TABLE IF EXISTS town_citizen_relationships")
    op.execute("DROP TABLE IF EXISTS town_conversation_turns")
    op.execute("DROP TABLE IF EXISTS town_conversations")
    op.execute("DROP TABLE IF EXISTS town_citizens")

    # Brain
    op.execute("DROP TABLE IF EXISTS brain_settings")
    op.execute("DROP TABLE IF EXISTS brain_crystal_tags")
    op.execute("DROP TABLE IF EXISTS brain_crystals")
