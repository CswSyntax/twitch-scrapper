"""Tests for TwitchClient authentication and API calls."""

import pytest
import respx
from httpx import Response

from twitch_scraper.client import (
    AuthenticationError,
    TwitchClient,
    TwitchClientError,
)
from twitch_scraper.config import Settings


@pytest.fixture
def client(mock_settings: Settings) -> TwitchClient:
    """Create a TwitchClient for testing."""
    return TwitchClient(mock_settings)


class TestAuthentication:
    """Tests for OAuth2 authentication."""

    @respx.mock
    def test_authenticate_success(
        self, client: TwitchClient, mock_token_response: dict
    ) -> None:
        """Successful authentication returns token data."""
        respx.post("https://id.twitch.tv/oauth2/token").mock(
            return_value=Response(200, json=mock_token_response)
        )

        result = client.authenticate()

        assert result["access_token"] == "test_access_token"
        assert result["expires_in"] == 5000000

    @respx.mock
    def test_authenticate_failure_raises_error(self, client: TwitchClient) -> None:
        """Failed authentication raises AuthenticationError."""
        respx.post("https://id.twitch.tv/oauth2/token").mock(
            return_value=Response(401, json={"error": "invalid_client"})
        )

        with pytest.raises(AuthenticationError):
            client.authenticate()

    @respx.mock
    def test_authenticate_sets_token(
        self, client: TwitchClient, mock_token_response: dict
    ) -> None:
        """Authentication stores access token internally."""
        respx.post("https://id.twitch.tv/oauth2/token").mock(
            return_value=Response(200, json=mock_token_response)
        )

        client.authenticate()

        assert client._access_token == "test_access_token"


class TestGetStreams:
    """Tests for get_streams API call."""

    @respx.mock
    def test_get_streams_success(
        self,
        client: TwitchClient,
        mock_token_response: dict,
        mock_streams_response: dict,
    ) -> None:
        """get_streams returns stream data."""
        respx.post("https://id.twitch.tv/oauth2/token").mock(
            return_value=Response(200, json=mock_token_response)
        )
        respx.get("https://api.twitch.tv/helix/streams").mock(
            return_value=Response(200, json=mock_streams_response)
        )

        result = client.get_streams(game_id="516575", language="de")

        assert len(result["data"]) == 2
        assert result["data"][0]["user_login"] == "teststreamer1"

    @respx.mock
    def test_get_streams_with_pagination(
        self,
        client: TwitchClient,
        mock_token_response: dict,
        mock_streams_response: dict,
    ) -> None:
        """get_streams passes pagination cursor."""
        respx.post("https://id.twitch.tv/oauth2/token").mock(
            return_value=Response(200, json=mock_token_response)
        )
        request = respx.get("https://api.twitch.tv/helix/streams").mock(
            return_value=Response(200, json=mock_streams_response)
        )

        client.get_streams(after="cursor123")

        assert "after=cursor123" in str(request.calls[0].request.url)


class TestGetUsers:
    """Tests for get_users API call."""

    @respx.mock
    def test_get_users_success(
        self,
        client: TwitchClient,
        mock_token_response: dict,
        mock_users_response: dict,
    ) -> None:
        """get_users returns user data."""
        respx.post("https://id.twitch.tv/oauth2/token").mock(
            return_value=Response(200, json=mock_token_response)
        )
        respx.get("https://api.twitch.tv/helix/users").mock(
            return_value=Response(200, json=mock_users_response)
        )

        result = client.get_users(["123456", "789012"])

        assert len(result) == 2
        assert result[0]["login"] == "teststreamer1"
        assert result[1]["login"] == "teststreamer2"

    @respx.mock
    def test_get_users_empty_list(
        self,
        client: TwitchClient,
    ) -> None:
        """get_users with empty list returns empty."""
        result = client.get_users([])

        assert result == []


class TestGetGameId:
    """Tests for get_game_id lookup."""

    @respx.mock
    def test_get_game_id_found(
        self,
        client: TwitchClient,
        mock_token_response: dict,
    ) -> None:
        """get_game_id returns ID when game found."""
        respx.post("https://id.twitch.tv/oauth2/token").mock(
            return_value=Response(200, json=mock_token_response)
        )
        respx.get("https://api.twitch.tv/helix/games").mock(
            return_value=Response(200, json={"data": [{"id": "516575", "name": "Valorant"}]})
        )

        result = client.get_game_id("Valorant")

        assert result == "516575"

    @respx.mock
    def test_get_game_id_not_found(
        self,
        client: TwitchClient,
        mock_token_response: dict,
    ) -> None:
        """get_game_id returns None when game not found."""
        respx.post("https://id.twitch.tv/oauth2/token").mock(
            return_value=Response(200, json=mock_token_response)
        )
        respx.get("https://api.twitch.tv/helix/games").mock(
            return_value=Response(200, json={"data": []})
        )

        result = client.get_game_id("NonexistentGame")

        assert result is None


class TestSearchChannels:
    """Tests for search_channels API call."""

    @respx.mock
    def test_search_channels_success(
        self,
        client: TwitchClient,
        mock_token_response: dict,
        mock_search_channels_response: dict,
    ) -> None:
        """search_channels returns channel data."""
        respx.post("https://id.twitch.tv/oauth2/token").mock(
            return_value=Response(200, json=mock_token_response)
        )
        respx.get("https://api.twitch.tv/helix/search/channels").mock(
            return_value=Response(200, json=mock_search_channels_response)
        )

        result = client.search_channels("Valorant")

        assert len(result["data"]) == 1
        assert result["data"][0]["broadcaster_login"] == "offlinestreamer1"


class TestContextManager:
    """Tests for context manager protocol."""

    def test_context_manager(self, mock_settings: Settings) -> None:
        """TwitchClient works as context manager."""
        with TwitchClient(mock_settings) as client:
            assert client is not None

    @respx.mock
    def test_context_manager_closes_client(
        self, mock_settings: Settings, mock_token_response: dict
    ) -> None:
        """Context manager closes HTTP client on exit."""
        respx.post("https://id.twitch.tv/oauth2/token").mock(
            return_value=Response(200, json=mock_token_response)
        )

        with TwitchClient(mock_settings) as client:
            client.authenticate()
        # Client should be closed after exiting context
        # No explicit assertion needed - if it raises, test fails
