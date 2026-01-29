"""Export functions for CSV and JSON output."""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from twitch_scraper.models import ExportConfig, SearchCriteria, Streamer


# CSV column order matching contract
CSV_COLUMNS = [
    "username",
    "display_name",
    "twitch_id",
    "is_live",
    "viewer_count",
    "game_name",
    "language",
    "broadcaster_type",
    "email",
    "twitter",
    "instagram",
    "youtube",
    "discord",
    "tiktok",
]


def _streamer_to_csv_row(streamer: Streamer) -> dict[str, str]:
    """Convert a Streamer to a CSV row dictionary.

    Args:
        streamer: Streamer to convert

    Returns:
        Dictionary with CSV column values
    """
    return {
        "username": streamer.username,
        "display_name": streamer.display_name,
        "twitch_id": streamer.twitch_id,
        "is_live": str(streamer.is_live).lower(),
        "viewer_count": str(streamer.viewer_count) if streamer.viewer_count else "",
        "game_name": streamer.game_name or "",
        "language": streamer.language or "",
        "broadcaster_type": streamer.broadcaster_type or "",
        "email": streamer.emails[0] if streamer.emails else "",
        "twitter": streamer.social_links.twitter or "",
        "instagram": streamer.social_links.instagram or "",
        "youtube": streamer.social_links.youtube or "",
        "discord": streamer.social_links.discord or "",
        "tiktok": streamer.social_links.tiktok or "",
    }


def export_to_csv(streamers: list[Streamer], config: ExportConfig) -> Path:
    """Export streamers to CSV format.

    Args:
        streamers: List of streamers to export
        config: Export configuration

    Returns:
        Path to the created CSV file
    """
    output_path = Path(config.output_path)

    # Use UTF-8 with BOM for Excel compatibility
    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()

        for streamer in streamers:
            row = _streamer_to_csv_row(streamer)
            writer.writerow(row)

    return output_path


def _streamer_to_json_dict(streamer: Streamer) -> dict[str, Any]:
    """Convert a Streamer to a JSON-serializable dictionary.

    Args:
        streamer: Streamer to convert

    Returns:
        Dictionary for JSON serialization
    """
    return {
        "twitch_id": streamer.twitch_id,
        "username": streamer.username,
        "display_name": streamer.display_name,
        "is_live": streamer.is_live,
        "viewer_count": streamer.viewer_count,
        "game_name": streamer.game_name,
        "language": streamer.language,
        "broadcaster_type": streamer.broadcaster_type,
        "emails": streamer.emails,
        "social_links": {
            "twitter": streamer.social_links.twitter,
            "instagram": streamer.social_links.instagram,
            "youtube": streamer.social_links.youtube,
            "discord": streamer.social_links.discord,
            "tiktok": streamer.social_links.tiktok,
        },
        "last_updated": streamer.last_updated.isoformat(),
    }


def export_to_json(
    streamers: list[Streamer],
    config: ExportConfig,
    criteria: Optional[SearchCriteria] = None,
) -> Path:
    """Export streamers to JSON format.

    Args:
        streamers: List of streamers to export
        config: Export configuration
        criteria: Search criteria used (for metadata)

    Returns:
        Path to the created JSON file
    """
    output_path = Path(config.output_path)

    # Build metadata
    metadata: dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_results": len(streamers),
    }

    if criteria:
        metadata["search_criteria"] = {
            "game": criteria.game_name,
            "game_id": criteria.game_id,
            "min_viewers": criteria.min_viewers,
            "max_viewers": criteria.max_viewers,
            "language": criteria.language,
            "include_offline": criteria.include_offline,
            "limit": criteria.limit,
        }

    # Build output structure
    output = {
        "metadata": metadata,
        "streamers": [_streamer_to_json_dict(s) for s in streamers],
    }

    # Write with pretty formatting
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output_path
