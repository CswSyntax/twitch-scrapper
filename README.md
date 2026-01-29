# Twitch Streamer Finder

A Python CLI tool to find Twitch streamers matching specific criteria and extract contact information for outreach campaigns.

## Features

- **Search streamers** by game, language, and viewer count (live + offline)
- **Extract social media links** (Twitter/X, Instagram, YouTube, Discord, TikTok)
- **Extract email addresses** from channel descriptions
- **Export to CSV or JSON** for spreadsheet applications or automation
- **Rate limiting** with automatic throttling (800 requests/minute)
- **Progress display** during data collection

## Quick Start

### 1. Prerequisites

- Python 3.10+
- Twitch Developer Account ([dev.twitch.tv](https://dev.twitch.tv))

### 2. Get Twitch API Credentials

1. Go to [dev.twitch.tv/console](https://dev.twitch.tv/console)
2. Click "Register Your Application"
3. Fill in:
   - Name: `Streamer Finder`
   - OAuth Redirect URLs: `http://localhost`
   - Category: `Application Integration`
4. Click "Create"
5. Copy the **Client ID** and generate a **Client Secret**

### 3. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/twitch-scrapper.git
cd twitch-scrapper

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install
pip install -e .
```

### 4. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# TWITCH_CLIENT_ID=your_client_id
# TWITCH_CLIENT_SECRET=your_client_secret
```

### 5. Verify Setup

```bash
twitch-scraper auth
```

Expected output:
```
✓ Authentication successful
  Token expires in: 58 days
  Rate limit: 800 requests/minute
```

## Usage

### Search Streamers

```bash
# Find German Valorant streamers with 50-500 viewers
twitch-scraper search --game "Valorant" --min-viewers 50 --max-viewers 500 --language de

# Export to JSON
twitch-scraper search --game "League of Legends" --format json --output lol_streamers.json

# Live streamers only
twitch-scraper search --game "Fortnite" --live-only --limit 200

# Verbose mode
twitch-scraper search -g "Minecraft" -m 100 -v -o minecraft.csv
```

### Find Game ID

```bash
twitch-scraper games "valorant"
```

### CLI Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--game` | `-g` | Game/category name | - |
| `--game-id` | - | Twitch game ID | - |
| `--min-viewers` | `-m` | Minimum viewer count | 0 |
| `--max-viewers` | `-M` | Maximum viewer count | - |
| `--language` | `-l` | Broadcast language (ISO 639-1) | de |
| `--include-offline` | - | Include offline channels | true |
| `--live-only` | - | Only live streams | false |
| `--limit` | `-n` | Max streamers to collect | 100 |
| `--output` | `-o` | Output file path | streamers.csv |
| `--format` | `-f` | Output format (csv/json) | csv |
| `--verbose` | `-v` | Show detailed progress | false |

## Output Formats

### CSV

```csv
username,display_name,twitch_id,is_live,viewer_count,game_name,language,broadcaster_type,email,twitter,instagram,youtube,discord,tiktok
streamer1,Streamer1,123456,true,250,Valorant,de,affiliate,business@email.com,https://twitter.com/streamer1,,,https://discord.gg/abc,
```

### JSON

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
    "total_results": 150
  },
  "streamers": [
    {
      "twitch_id": "123456",
      "username": "streamer1",
      "display_name": "Streamer1",
      "is_live": true,
      "viewer_count": 250,
      "emails": ["business@email.com"],
      "social_links": {
        "twitter": "https://twitter.com/streamer1",
        "discord": "https://discord.gg/abc"
      }
    }
  ]
}
```

## Development

### Setup Development Environment

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=twitch_scraper

# Type checking
mypy src/

# Linting
ruff check src/
```

### Project Structure

```
twitch-scrapper/
├── src/twitch_scraper/
│   ├── __init__.py      # Package version
│   ├── __main__.py      # Entry point
│   ├── cli.py           # Typer CLI commands
│   ├── client.py        # Twitch API client
│   ├── config.py        # Settings management
│   ├── extractors.py    # Social/email extraction
│   ├── exporters.py     # CSV/JSON export
│   ├── models.py        # Pydantic models
│   └── scraper.py       # Core scraping logic
├── tests/               # Test suite
├── specs/               # Design documents
├── pyproject.toml       # Project configuration
└── README.md
```

## API Limitations

- **Social media links**: Extracted from channel descriptions only (Twitch API doesn't expose panel data)
- **Offline channels**: Only channels active in the last 6 months are searchable
- **Rate limits**: 800 requests/minute (automatically handled)

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
