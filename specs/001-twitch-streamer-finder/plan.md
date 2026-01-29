# Implementation Plan: Twitch Streamer Finder

**Branch**: `001-twitch-streamer-finder` | **Date**: 2026-01-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-twitch-streamer-finder/spec.md`

## Summary

Build a Python CLI tool to find Twitch streamers matching specific criteria (viewer count, game, language) and extract contact information (social media links, emails) from their channel descriptions. The tool exports results to CSV or JSON for outreach campaigns.

**Key technical approach**: Use Twitch Helix API for data collection with httpx for HTTP requests, pyrate-limiter for rate limit compliance, and typer/rich for CLI with progress display.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: httpx, typer, rich, pydantic-settings, pyrate-limiter
**Storage**: File-based (CSV/JSON export only, no database)
**Testing**: pytest + respx (httpx mocking)
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: Single project (CLI tool)
**Performance Goals**: 100 streamers in <60 seconds, 1000+ streamers with automatic rate limit handling
**Constraints**: 800 requests/minute Twitch API rate limit, API-only (no web scraping)
**Scale/Scope**: Single-user CLI tool, export files up to 10,000 streamers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution not yet configured for this project. Proceeding with standard best practices:
- Tests required for core functionality
- Type hints throughout codebase
- Environment-based configuration for secrets

## Project Structure

### Documentation (this feature)

```text
specs/001-twitch-streamer-finder/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: API research and tech decisions
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Setup guide
├── contracts/           # Phase 1: Interface contracts
│   └── cli-interface.md # CLI command definitions
├── checklists/          # Quality checklists
│   └── requirements.md
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/
└── twitch_scraper/
    ├── __init__.py
    ├── __main__.py          # Entry point: python -m twitch_scraper
    ├── cli.py               # Typer CLI definitions
    ├── config.py            # Pydantic settings (env vars)
    ├── client.py            # Twitch API client with rate limiting
    ├── scraper.py           # Core collection logic
    ├── extractors.py        # Social media/email extraction
    ├── exporters.py         # CSV/JSON export functions
    └── models.py            # Pydantic data models

tests/
├── __init__.py
├── conftest.py              # Shared fixtures (mock API responses)
├── test_cli.py              # CLI command tests
├── test_client.py           # API client tests
├── test_scraper.py          # Scraper logic tests
├── test_extractors.py       # Contact extraction tests
└── test_exporters.py        # Export format tests
```

**Structure Decision**: Single project layout with src/ directory. Simple CLI tool without frontend/backend separation.

## Key Design Decisions

### 1. Social Media Extraction Limitation

The Twitch API does not provide access to channel panels or social media links. Extraction is limited to parsing the channel `description` field using regex patterns. This may result in lower extraction rates than if panel data were available.

### 2. Offline Streamer Discovery

The Search Channels endpoint only returns channels that have streamed within the last 6 months. There is no direct viewer count filter for offline channels - filtering must be done client-side based on available data.

### 3. Rate Limit Strategy

Using pyrate-limiter with httpx transport integration for automatic rate limiting at 800 requests/minute. Exponential backoff with jitter for 429 responses.

### 4. Batch Processing

Users and Channels endpoints support up to 100 IDs per request. The scraper batches requests to minimize API calls during the enrichment phase.

## Artifacts Generated

| Artifact | Path | Purpose |
|----------|------|---------|
| Research | `research.md` | API endpoints, tech stack decisions |
| Data Model | `data-model.md` | Entity definitions, validation rules |
| CLI Contract | `contracts/cli-interface.md` | Command structure, options, output formats |
| Quickstart | `quickstart.md` | Setup and usage guide |

## Next Steps

Run `/speckit.tasks` to generate the implementation task list from this plan.
