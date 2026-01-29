"""Pydantic data models for Twitch Streamer Finder."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SocialLinks(BaseModel):
    """Extracted social media links from channel description."""

    twitter: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None
    discord: Optional[str] = None
    tiktok: Optional[str] = None
    other: list[str] = Field(default_factory=list)


class Streamer(BaseModel):
    """Represents a Twitch content creator with extracted contact information."""

    twitch_id: str
    username: str
    display_name: str
    description: Optional[str] = None
    broadcaster_type: Optional[str] = None
    follower_count: Optional[int] = None
    is_live: bool = False
    viewer_count: Optional[int] = None
    game_name: Optional[str] = None
    language: Optional[str] = None
    emails: list[str] = Field(default_factory=list)
    social_links: SocialLinks = Field(default_factory=SocialLinks)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class SearchCriteria(BaseModel):
    """Input parameters for streamer search."""

    min_viewers: int = 0
    max_viewers: Optional[int] = None
    game_name: Optional[str] = None
    game_id: Optional[str] = None
    language: str = "de"
    include_offline: bool = True
    limit: int = 100

    def model_post_init(self, __context: object) -> None:
        """Validate search criteria after initialization."""
        if self.max_viewers is not None and self.max_viewers <= self.min_viewers:
            raise ValueError("max_viewers must be greater than min_viewers")
        if self.limit < 1 or self.limit > 10000:
            raise ValueError("limit must be between 1 and 10000")


class ExportConfig(BaseModel):
    """Configuration for data export."""

    format: str = "csv"
    output_path: str
    include_description: bool = False

    def model_post_init(self, __context: object) -> None:
        """Validate export configuration."""
        if self.format not in ("csv", "json"):
            raise ValueError("format must be 'csv' or 'json'")


class CollectionProgress(BaseModel):
    """Tracks progress during data collection."""

    total_expected: Optional[int] = None
    processed: int = 0
    live_found: int = 0
    offline_found: int = 0
    errors: int = 0
    current_phase: str = "idle"
