# Data Model: Twitch Streamer Finder

**Date**: 2026-01-29
**Feature**: 001-twitch-streamer-finder

## Entities

### Streamer

Represents a Twitch content creator with extracted contact information.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| twitch_id | string | yes | Unique Twitch user ID |
| username | string | yes | Twitch login name (lowercase) |
| display_name | string | yes | Display name (may include caps/special chars) |
| description | string | no | Channel bio/description text |
| broadcaster_type | string | no | "partner", "affiliate", or "" |
| follower_count | integer | no | Number of followers (if available) |
| is_live | boolean | yes | Whether currently streaming |
| viewer_count | integer | no | Current viewers (if live) |
| game_name | string | no | Current/last game played |
| language | string | no | Broadcast language (ISO 639-1) |
| emails | list[string] | no | Extracted email addresses |
| social_links | SocialLinks | no | Extracted social media links |
| last_updated | datetime | yes | When this record was fetched |

### SocialLinks

Nested structure for categorized social media links.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| twitter | string | no | Twitter/X URL or handle |
| instagram | string | no | Instagram URL or handle |
| youtube | string | no | YouTube channel URL |
| discord | string | no | Discord invite URL |
| tiktok | string | no | TikTok URL or handle |
| other | list[string] | no | Other detected URLs |

### SearchCriteria

Input parameters for streamer search.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| min_viewers | integer | no | 0 | Minimum viewer count filter |
| max_viewers | integer | no | null | Maximum viewer count filter |
| game_name | string | no | null | Game/category to filter by |
| game_id | string | no | null | Twitch game ID (alternative to name) |
| language | string | no | "de" | Broadcast language (ISO 639-1) |
| include_offline | boolean | no | true | Include offline channels via search |
| limit | integer | no | 100 | Maximum streamers to return |

### ExportConfig

Configuration for data export.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| format | string | yes | "csv" | Export format: "csv" or "json" |
| output_path | string | yes | - | File path for export |
| include_description | boolean | no | false | Include full description in export |

### CollectionProgress

Tracks progress during data collection.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| total_expected | integer | no | Estimated total streamers to process |
| processed | integer | yes | Number of streamers processed |
| live_found | integer | yes | Number of live streamers found |
| offline_found | integer | yes | Number of offline streamers found |
| errors | integer | yes | Number of failed fetches |
| current_phase | string | yes | "live_streams", "offline_search", "enrichment", "export" |

## Relationships

```
SearchCriteria --[input]--> Collection Process --[produces]--> Streamer[]
                                   |
                                   v
                           CollectionProgress
                                   |
                                   v
ExportConfig --[input]--> Export Process --[produces]--> CSV/JSON file
```

## Validation Rules

### Streamer
- `twitch_id` must be non-empty string
- `username` must be lowercase alphanumeric with underscores
- `viewer_count` must be >= 0 when present
- `language` must be valid ISO 639-1 code when present

### SearchCriteria
- `min_viewers` must be >= 0
- `max_viewers` must be > `min_viewers` when both specified
- `language` must be valid ISO 639-1 code
- `limit` must be between 1 and 10000

### Email Extraction
- Must match standard email pattern: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- Exclude common false positives (e.g., example@example.com)

### Social Links
- URLs must be valid and match platform domain
- Handles extracted without URL must be marked as handle-only

## State Transitions

### Collection Process States

```
IDLE --> AUTHENTICATING --> COLLECTING_LIVE --> COLLECTING_OFFLINE --> ENRICHING --> EXPORTING --> COMPLETE
                |               |                    |                   |              |
                v               v                    v                   v              v
             [error]        [error]              [error]             [error]        [error]
                |               |                    |                   |              |
                +---------------+--------------------+-------------------+--------------+
                                                     |
                                                     v
                                                  FAILED
```

- **IDLE**: Initial state, waiting for search criteria
- **AUTHENTICATING**: Getting OAuth token from Twitch
- **COLLECTING_LIVE**: Fetching live streams matching criteria
- **COLLECTING_OFFLINE**: Searching offline channels (if enabled)
- **ENRICHING**: Fetching full user profiles for collected streamers
- **EXPORTING**: Writing data to output file
- **COMPLETE**: Successfully finished
- **FAILED**: Error occurred, may be resumable
