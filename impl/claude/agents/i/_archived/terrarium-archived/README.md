# I-gent Terrarium Archive

**Archived**: 2025-12-17
**Reason**: WebSocket client for defunct protocols/terrarium server

## What Was Archived?

1. **terrarium_tui.py** - Standalone TUI application that connected to Terrarium server
2. **terrarium_source.py** - WebSocket data source for consuming Terrarium metrics
3. **test_terrarium_tui.py** - Tests for standalone TUI
4. **test_terrarium_source.py** - Tests for WebSocket source

## What Was NOT Archived?

**`screens/terrarium.py` (TerrariumScreen)** was NOT archived because:
- It's part of the I-gent LOD navigation hierarchy (LOD 0)
- Works in demo mode without requiring the old Terrarium server
- Integrated into Observatory's zoom functionality

## Why Archived?

The protocols/terrarium server was archived and superseded by:
- AGENTESE Universal Gateway
- Synergy Event Bus
- Crown Jewel Services

This WebSocket client code connected to that server and is no longer useful.

## Deletion Policy

Per kgents archive policy, this directory will be deleted 30 days after archive date (2025-01-16).
