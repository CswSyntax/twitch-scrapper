# CLI Interface Contract: Twitch Streamer Finder

**Date**: 2026-01-29
**Feature**: 001-twitch-streamer-finder

This document defines the command-line interface contract for the Twitch Streamer Finder tool.

## Command Structure

```
twitch-scraper <command> [options]
```

## Commands

### `search`

Search for Twitch streamers based on criteria and export results.

```bash
twitch-scraper search [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--game` | `-g` | TEXT | - | Game/category name to filter by |
| `--game-id` | - | TEXT | - | Twitch game ID (alternative to --game) |
| `--min-viewers` | `-m` | INT | 0 | Minimum viewer count |
| `--max-viewers` | `-M` | INT | - | Maximum viewer count |
| `--language` | `-l` | TEXT | de | Broadcast language (ISO 639-1) |
| `--include-offline` | - | FLAG | true | Include offline channels in search |
| `--live-only` | - | FLAG | false | Only search live streams |
| `--limit` | `-n` | INT | 100 | Maximum streamers to collect |
| `--output` | `-o` | PATH | streamers.csv | Output file path |
| `--format` | `-f` | TEXT | csv | Output format: csv, json |
| `--verbose` | `-v` | FLAG | false | Show detailed progress |

#### Examples

```bash
# Find German Valorant streamers with 50-500 viewers
twitch-scraper search --game "Valorant" --min-viewers 50 --max-viewers 500 --language de

# Export as JSON
twitch-scraper search --game "League of Legends" --format json --output lol_streamers.json

# Live streamers only, limit 50
twitch-scraper search --game "Fortnite" --live-only --limit 50

# Verbose mode with custom output
twitch-scraper search -g "Minecraft" -m 100 -v -o minecraft_streamers.csv
```

#### Output

**Progress Display** (stdout):
```
Authenticating with Twitch API... ✓
Searching live streams... [################] 150/150
Searching offline channels... [########--------] 80/200
Enriching profiles... [####################] 230/230
Extracting contact info... ✓

Found 230 streamers:
  - Live: 150
  - Offline: 80
  - With email: 45
  - With social links: 198

Exported to: streamers.csv
```

**Error Display** (stderr):
```
Error: Invalid API credentials. Please check TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET.
Error: Rate limited. Retrying in 30 seconds...
Warning: Could not fetch profile for user 'xyz123' - skipping.
```

#### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Authentication failed |
| 3 | Invalid arguments |
| 4 | Network error |
| 5 | Rate limit exceeded (after retries) |

---

### `auth`

Test authentication with Twitch API.

```bash
twitch-scraper auth
```

#### Output

**Success**:
```
✓ Authentication successful
  Token expires in: 58 days
  Rate limit: 800 requests/minute
```

**Failure**:
```
✗ Authentication failed
  Error: Invalid client credentials

  Please ensure these environment variables are set:
    TWITCH_CLIENT_ID=your_client_id
    TWITCH_CLIENT_SECRET=your_client_secret
```

---

### `games`

Search for game IDs by name (helper command).

```bash
twitch-scraper games <query>
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| query | TEXT | yes | Game name to search for |

#### Output

```
Search results for "valorant":

  ID          Name
  ──────────  ────────────────────
  516575      Valorant
  518203      VALORANT Champions

Use --game-id 516575 with the search command.
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TWITCH_CLIENT_ID` | yes | Twitch application client ID |
| `TWITCH_CLIENT_SECRET` | yes | Twitch application client secret |

## Configuration File (Optional)

Location: `~/.config/twitch-scraper/config.toml` or `./.twitch-scraper.toml`

```toml
[defaults]
language = "de"
format = "csv"
include_offline = true
limit = 100

[output]
directory = "./exports"
```

## CSV Output Format

```csv
username,display_name,twitch_id,is_live,viewer_count,game_name,language,broadcaster_type,email,twitter,instagram,youtube,discord,tiktok
ninja,Ninja,19571641,true,15234,Fortnite,en,partner,business@ninja.com,https://twitter.com/Ninja,https://instagram.com/ninja,,https://discord.gg/ninja,
```

## JSON Output Format

```json
{
  "metadata": {
    "generated_at": "2026-01-29T14:30:00Z",
    "search_criteria": {
      "game": "Valorant",
      "min_viewers": 50,
      "max_viewers": 500,
      "language": "de"
    },
    "total_results": 230
  },
  "streamers": [
    {
      "twitch_id": "123456",
      "username": "examplestreamer",
      "display_name": "ExampleStreamer",
      "is_live": true,
      "viewer_count": 250,
      "game_name": "Valorant",
      "language": "de",
      "broadcaster_type": "affiliate",
      "emails": ["business@example.com"],
      "social_links": {
        "twitter": "https://twitter.com/example",
        "instagram": null,
        "youtube": "https://youtube.com/c/example",
        "discord": "https://discord.gg/example",
        "tiktok": null
      },
      "last_updated": "2026-01-29T14:25:00Z"
    }
  ]
}
```
