# Quickstart: Twitch Streamer Finder

**Date**: 2026-01-29
**Feature**: 001-twitch-streamer-finder

## Prerequisites

1. **Python 3.12+** installed
2. **Twitch Developer Account** at [dev.twitch.tv](https://dev.twitch.tv)
3. **Registered Twitch Application** with Client ID and Client Secret

## Setup

### 1. Get Twitch API Credentials

1. Go to [dev.twitch.tv/console](https://dev.twitch.tv/console)
2. Click "Register Your Application"
3. Fill in:
   - Name: `Streamer Finder` (or any name)
   - OAuth Redirect URLs: `http://localhost` (required but unused)
   - Category: `Application Integration`
4. Click "Create"
5. Copy the **Client ID**
6. Click "New Secret" and copy the **Client Secret**

### 2. Install the Tool

```bash
# Clone or navigate to project
cd twitch-scrapper

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 3. Configure Environment

Create a `.env` file in the project root:

```bash
TWITCH_CLIENT_ID=your_client_id_here
TWITCH_CLIENT_SECRET=your_client_secret_here
```

Or export directly:

```bash
export TWITCH_CLIENT_ID=your_client_id_here
export TWITCH_CLIENT_SECRET=your_client_secret_here
```

### 4. Verify Setup

```bash
twitch-scraper auth
```

Expected output:
```
✓ Authentication successful
  Token expires in: 58 days
  Rate limit: 800 requests/minute
```

## Basic Usage

### Find German Valorant Streamers (50-500 viewers)

```bash
twitch-scraper search --game "Valorant" --min-viewers 50 --max-viewers 500 --language de
```

### Export to JSON

```bash
twitch-scraper search --game "Valorant" --format json --output valorant_streamers.json
```

### Live Streamers Only

```bash
twitch-scraper search --game "League of Legends" --live-only --limit 200
```

### Find Game ID

```bash
twitch-scraper games "fortnite"
```

## Output Files

### CSV Format

Default output is CSV with columns:
- username, display_name, twitch_id
- is_live, viewer_count, game_name, language
- broadcaster_type
- email, twitter, instagram, youtube, discord, tiktok

### JSON Format

Use `--format json` for structured output with metadata.

## Troubleshooting

### Authentication Failed

```
Error: Invalid API credentials
```

**Solution**: Verify your `.env` file contains correct `TWITCH_CLIENT_ID` and `TWITCH_CLIENT_SECRET`.

### Rate Limited

```
Warning: Rate limited. Retrying in 30 seconds...
```

**Solution**: This is normal for large searches. The tool automatically handles rate limits with backoff.

### No Results Found

```
Found 0 streamers matching criteria
```

**Possible causes**:
- No live streamers playing that game right now
- Viewer count range too restrictive
- Language filter too specific

**Try**: Remove some filters or use `--include-offline` (enabled by default).

## Next Steps

- See `contracts/cli-interface.md` for full CLI documentation
- See `data-model.md` for output data structure details
- See `research.md` for Twitch API limitations and workarounds
