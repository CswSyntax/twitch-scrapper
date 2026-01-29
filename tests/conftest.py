"""Shared test fixtures and mock API responses."""

import pytest

from twitch_scraper.config import Settings
from twitch_scraper.models import SearchCriteria, SocialLinks, Streamer


@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings for testing."""
    return Settings(
        twitch_client_id="test_client_id",
        twitch_client_secret="test_client_secret",
    )


@pytest.fixture
def mock_token_response() -> dict:
    """Mock OAuth token response."""
    return {
        "access_token": "test_access_token",
        "expires_in": 5000000,
        "token_type": "bearer",
    }


@pytest.fixture
def mock_streams_response() -> dict:
    """Mock streams API response."""
    return {
        "data": [
            {
                "id": "stream1",
                "user_id": "123456",
                "user_login": "teststreamer1",
                "user_name": "TestStreamer1",
                "game_id": "516575",
                "game_name": "Valorant",
                "type": "live",
                "title": "Playing Valorant!",
                "viewer_count": 250,
                "started_at": "2026-01-29T10:00:00Z",
                "language": "de",
                "tags": ["German", "FPS"],
                "is_mature": False,
            },
            {
                "id": "stream2",
                "user_id": "789012",
                "user_login": "teststreamer2",
                "user_name": "TestStreamer2",
                "game_id": "516575",
                "game_name": "Valorant",
                "type": "live",
                "title": "Ranked grind",
                "viewer_count": 100,
                "started_at": "2026-01-29T11:00:00Z",
                "language": "de",
                "tags": ["German"],
                "is_mature": False,
            },
        ],
        "pagination": {"cursor": "next_page_cursor"},
    }


@pytest.fixture
def mock_users_response() -> dict:
    """Mock users API response."""
    return {
        "data": [
            {
                "id": "123456",
                "login": "teststreamer1",
                "display_name": "TestStreamer1",
                "type": "",
                "broadcaster_type": "affiliate",
                "description": "Welcome! Contact: business@teststreamer1.com | Twitter: https://twitter.com/teststreamer1 | Discord: https://discord.gg/test123",
                "profile_image_url": "https://example.com/image1.jpg",
                "offline_image_url": "",
                "created_at": "2020-01-01T00:00:00Z",
            },
            {
                "id": "789012",
                "login": "teststreamer2",
                "display_name": "TestStreamer2",
                "type": "",
                "broadcaster_type": "partner",
                "description": "Pro player | Instagram: https://instagram.com/teststreamer2",
                "profile_image_url": "https://example.com/image2.jpg",
                "offline_image_url": "",
                "created_at": "2019-06-15T00:00:00Z",
            },
        ]
    }


@pytest.fixture
def mock_games_response() -> dict:
    """Mock games search API response."""
    return {
        "data": [
            {"id": "516575", "name": "Valorant", "box_art_url": "https://example.com/valorant.jpg"},
            {"id": "518203", "name": "VALORANT Champions", "box_art_url": "https://example.com/champions.jpg"},
        ]
    }


@pytest.fixture
def mock_search_channels_response() -> dict:
    """Mock search channels API response."""
    return {
        "data": [
            {
                "id": "111111",
                "broadcaster_login": "offlinestreamer1",
                "display_name": "OfflineStreamer1",
                "game_name": "Valorant",
                "is_live": False,
                "broadcaster_language": "de",
                "title": "Last stream title",
                "started_at": "",
            },
        ],
        "pagination": {},
    }


@pytest.fixture
def sample_streamer() -> Streamer:
    """Create a sample streamer for testing."""
    return Streamer(
        twitch_id="123456",
        username="teststreamer",
        display_name="TestStreamer",
        description="Contact me: test@example.com",
        broadcaster_type="affiliate",
        is_live=True,
        viewer_count=250,
        game_name="Valorant",
        language="de",
        emails=["test@example.com"],
        social_links=SocialLinks(
            twitter="https://twitter.com/teststreamer",
            discord="https://discord.gg/test",
        ),
    )


@pytest.fixture
def sample_streamers(sample_streamer: Streamer) -> list[Streamer]:
    """Create a list of sample streamers for testing."""
    streamer2 = Streamer(
        twitch_id="789012",
        username="anotherstreamer",
        display_name="AnotherStreamer",
        description="Pro player",
        broadcaster_type="partner",
        is_live=False,
        viewer_count=None,
        game_name="League of Legends",
        language="en",
        emails=[],
        social_links=SocialLinks(instagram="https://instagram.com/another"),
    )
    return [sample_streamer, streamer2]


@pytest.fixture
def sample_search_criteria() -> SearchCriteria:
    """Create sample search criteria for testing."""
    return SearchCriteria(
        min_viewers=50,
        max_viewers=500,
        game_name="Valorant",
        language="de",
        include_offline=True,
        limit=100,
    )
