"""Twitch API client with OAuth2 authentication and rate limiting."""

import time
from typing import Any, Optional

import httpx
from pyrate_limiter import Duration, Limiter, Rate

from twitch_scraper.config import Settings, get_settings


class TwitchClientError(Exception):
    """Base exception for Twitch client errors."""

    pass


class AuthenticationError(TwitchClientError):
    """Raised when authentication fails."""

    pass


class RateLimitError(TwitchClientError):
    """Raised when rate limit is exceeded after retries."""

    pass


class TwitchClient:
    """Client for interacting with the Twitch Helix API."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Initialize the Twitch client.

        Args:
            settings: Application settings. If None, loads from environment.
        """
        self.settings = settings or get_settings()
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

        # Rate limiter: 800 requests per minute
        rate = Rate(self.settings.rate_limit_requests, Duration.MINUTE)
        self._limiter = Limiter(rate)

        self._client = httpx.Client(timeout=30.0)

    def __enter__(self) -> "TwitchClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def authenticate(self) -> dict[str, Any]:
        """Authenticate with Twitch API using client credentials.

        Returns:
            Token response containing access_token and expires_in.

        Raises:
            AuthenticationError: If authentication fails.
        """
        response = self._client.post(
            self.settings.twitch_auth_url,
            data={
                "client_id": self.settings.twitch_client_id,
                "client_secret": self.settings.twitch_client_secret,
                "grant_type": "client_credentials",
            },
        )

        if response.status_code != 200:
            raise AuthenticationError(
                f"Authentication failed: {response.status_code} - {response.text}"
            )

        data = response.json()
        self._access_token = data["access_token"]
        self._token_expires_at = time.time() + data["expires_in"] - 60  # 1 min buffer

        return data

    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token."""
        if not self._access_token or time.time() >= self._token_expires_at:
            self.authenticate()

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        self._ensure_authenticated()
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self.settings.twitch_client_id,
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Make a rate-limited API request with exponential backoff.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            max_retries: Maximum number of retries for rate limit errors

        Returns:
            JSON response data

        Raises:
            RateLimitError: If rate limit exceeded after all retries
            TwitchClientError: For other API errors
        """
        url = f"{self.settings.twitch_api_base_url}{endpoint}"

        for attempt in range(max_retries + 1):
            # Wait for rate limiter
            self._limiter.try_acquire("twitch_api")

            response = self._client.request(
                method,
                url,
                params=params,
                headers=self._get_headers(),
            )

            if response.status_code == 200:
                return response.json()

            if response.status_code == 401:
                # Token expired, re-authenticate
                self.authenticate()
                continue

            if response.status_code == 429:
                # Rate limited - exponential backoff with jitter
                if attempt < max_retries:
                    reset_after = int(response.headers.get("Ratelimit-Reset", 60))
                    wait_time = min(reset_after, (2**attempt) + (time.time() % 1))
                    time.sleep(wait_time)
                    continue
                raise RateLimitError("Rate limit exceeded after retries")

            raise TwitchClientError(
                f"API error: {response.status_code} - {response.text}"
            )

        raise TwitchClientError("Max retries exceeded")

    def get_streams(
        self,
        game_id: Optional[str] = None,
        language: Optional[str] = None,
        first: int = 100,
        after: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get live streams with optional filters.

        Args:
            game_id: Filter by game ID
            language: Filter by broadcast language (ISO 639-1)
            first: Number of results (1-100)
            after: Pagination cursor

        Returns:
            API response with stream data and pagination
        """
        params: dict[str, Any] = {"first": min(first, 100)}
        if game_id:
            params["game_id"] = game_id
        if language:
            params["language"] = language
        if after:
            params["after"] = after

        return self._request("GET", "/streams", params)

    def get_game_id(self, game_name: str) -> Optional[str]:
        """Look up game ID by name.

        Args:
            game_name: Game name to search for

        Returns:
            Game ID if found, None otherwise
        """
        response = self._request("GET", "/games", {"name": game_name})
        data = response.get("data", [])
        return data[0]["id"] if data else None

    def search_games(self, query: str) -> list[dict[str, Any]]:
        """Search for games by name.

        Args:
            query: Search query

        Returns:
            List of matching games
        """
        response = self._request("GET", "/search/categories", {"query": query})
        return response.get("data", [])

    def get_users(self, user_ids: list[str]) -> list[dict[str, Any]]:
        """Get user information for multiple users.

        Args:
            user_ids: List of user IDs (max 100)

        Returns:
            List of user data
        """
        if not user_ids:
            return []

        # Batch into groups of 100
        all_users: list[dict[str, Any]] = []
        for i in range(0, len(user_ids), 100):
            batch = user_ids[i : i + 100]
            params = {"id": batch}
            response = self._request("GET", "/users", params)
            all_users.extend(response.get("data", []))

        return all_users

    def search_channels(
        self,
        query: str,
        first: int = 100,
        after: Optional[str] = None,
        live_only: bool = False,
    ) -> dict[str, Any]:
        """Search for channels by name or description.

        Args:
            query: Search query
            first: Number of results (1-100)
            after: Pagination cursor
            live_only: Only return live channels

        Returns:
            API response with channel data and pagination
        """
        params: dict[str, Any] = {
            "query": query,
            "first": min(first, 100),
        }
        if after:
            params["after"] = after
        if live_only:
            params["live_only"] = "true"

        return self._request("GET", "/search/channels", params)

    def get_channel_info(self, broadcaster_ids: list[str]) -> list[dict[str, Any]]:
        """Get channel information for multiple broadcasters.

        Args:
            broadcaster_ids: List of broadcaster IDs (max 100)

        Returns:
            List of channel data
        """
        if not broadcaster_ids:
            return []

        # Batch into groups of 100
        all_channels: list[dict[str, Any]] = []
        for i in range(0, len(broadcaster_ids), 100):
            batch = broadcaster_ids[i : i + 100]
            params = {"broadcaster_id": batch}
            response = self._request("GET", "/channels", params)
            all_channels.extend(response.get("data", []))

        return all_channels
