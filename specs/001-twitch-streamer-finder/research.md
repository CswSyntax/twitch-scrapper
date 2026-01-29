# Research: Twitch Streamer Finder

**Date**: 2026-01-29
**Feature**: 001-twitch-streamer-finder

## Twitch API Findings

### Authentication
- **Decision**: OAuth2 Client Credentials Flow
- **Rationale**: Server-to-server authentication, no user interaction required, tokens last ~58 days
- **Endpoint**: `POST https://id.twitch.tv/oauth2/token`
- **Notes**: No refresh token provided - must request new token when expired

### Key API Endpoints

| Endpoint | Purpose | Max Per Request | Notes |
|----------|---------|-----------------|-------|
| GET /helix/streams | Live streamers by game/language | 100 | Returns only live streams, sorted by viewers |
| GET /helix/users | User profile with description | 100 | Contains channel bio (description field) |
| GET /helix/channels | Channel info | 100 | Game, language, title - no social links |
| GET /helix/search/channels | Find offline channels | 100 | Only returns channels active in last 6 months |

### Rate Limits
- **Decision**: 800 requests/minute with token-bucket algorithm
- **Implementation**: Track `Ratelimit-Remaining` header, implement exponential backoff for 429 errors
- **Batch optimization**: Use 100-item batches for users/channels endpoints

### Critical Limitation: No Social Media API Access
- **Finding**: Twitch Helix API does NOT provide access to channel panels or social media links
- **Impact**: Social media extraction must parse the channel `description` field only
- **Alternative Rejected**: Web scraping would violate Twitch ToS
- **Decision**: Extract social links from channel description text using regex patterns

### Data Availability for Offline Streamers
- **Finding**: Search endpoint returns channels that streamed in last 6 months
- **Limitation**: No direct filter for viewer count on offline channels
- **Decision**: Use search endpoint for discovery, then filter client-side based on historical data

## Technology Stack Decisions

### Language/Runtime
- **Decision**: Python 3.12+
- **Rationale**: Mature ecosystem, improved f-strings, 30%+ faster imports, stable library support
- **Alternative Rejected**: Python 3.13 (experimental features may have compatibility issues)

### HTTP Client
- **Decision**: httpx
- **Rationale**: Sync/async with same API, full type hints, HTTP/2 support, requests-like familiarity
- **Alternatives Considered**:
  - `requests` - no async support
  - `aiohttp` - different API, async-only

### Rate Limiting Library
- **Decision**: pyrate-limiter (v4.0+)
- **Rationale**: Direct httpx integration, leaky-bucket algorithm, sync/async support
- **Implementation**: Use `AsyncRateLimiterTransport` for automatic throttling

### CLI Framework
- **Decision**: typer + rich
- **Rationale**: Type-hint based CLI definition, beautiful progress bars and output
- **Progress Display**: `rich.progress.Progress` with task tracking for long operations

### Configuration Management
- **Decision**: pydantic-settings
- **Rationale**: Type validation, .env file support, secrets handling
- **Variables**: `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET`

### Export
- **Decision**: Python standard library (csv, json modules)
- **Rationale**: Simple requirements, no need for pandas overhead

### Testing
- **Decision**: pytest + respx
- **Rationale**: respx purpose-built for httpx mocking, pytest-asyncio for async tests

## Social Media Extraction Strategy

Since the API doesn't provide social links, extract from channel description using patterns:

| Platform | Pattern Examples |
|----------|------------------|
| Twitter/X | `twitter.com/`, `x.com/`, `@username` context |
| Instagram | `instagram.com/`, `ig:` |
| YouTube | `youtube.com/`, `youtu.be/` |
| Discord | `discord.gg/`, `discord.com/invite/` |
| TikTok | `tiktok.com/@` |
| Email | Standard email regex pattern |

## Pagination Strategy

- Use cursor-based pagination with `after` parameter
- Maximum 100 items per page
- Handle potential duplicates across pages (streams are dynamic)
- For large datasets, collect in batches and deduplicate by user_id

## Error Handling Strategy

| Error | Response |
|-------|----------|
| 401 Unauthorized | Re-authenticate, get new token |
| 429 Rate Limited | Exponential backoff using Ratelimit-Reset header |
| 500+ Server Error | Retry with exponential backoff, max 3 attempts |
| Network Error | Retry with backoff, save progress for resumption |
