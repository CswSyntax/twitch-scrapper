"""Core scraping logic for collecting Twitch streamer data."""

from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from twitch_scraper.client import TwitchClient, TwitchClientError
from twitch_scraper.extractors import extract_emails, extract_social_links
from twitch_scraper.models import CollectionProgress, SearchCriteria, SocialLinks, Streamer


class StreamerScraper:
    """Scraper for collecting Twitch streamer data."""

    def __init__(self, client: TwitchClient, verbose: bool = False) -> None:
        """Initialize the scraper.

        Args:
            client: Twitch API client
            verbose: Enable verbose output
        """
        self.client = client
        self.verbose = verbose
        self.console = Console()
        self.progress = CollectionProgress()

    def collect(self, criteria: SearchCriteria) -> list[Streamer]:
        """Collect streamers matching the given criteria.

        Args:
            criteria: Search criteria for filtering streamers

        Returns:
            List of Streamer objects
        """
        streamers: dict[str, Streamer] = {}  # Use dict to deduplicate by ID

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
            transient=not self.verbose,
        ) as progress:
            # Phase 1: Collect live streams
            self.progress.current_phase = "live_streams"
            live_task = progress.add_task("Searching live streams...", total=criteria.limit)

            live_streamers = self._collect_live_streams(criteria, progress, live_task)
            for streamer in live_streamers:
                if len(streamers) >= criteria.limit:
                    break
                streamers[streamer.twitch_id] = streamer

            progress.update(live_task, completed=criteria.limit)
            self.progress.live_found = len(streamers)

            # Phase 2: Collect offline channels (if enabled and space remaining)
            if criteria.include_offline and len(streamers) < criteria.limit:
                self.progress.current_phase = "offline_search"
                remaining = criteria.limit - len(streamers)
                offline_task = progress.add_task(
                    "Searching offline channels...", total=remaining
                )

                offline_streamers = self._collect_offline_channels(
                    criteria, remaining, progress, offline_task
                )
                for streamer in offline_streamers:
                    if streamer.twitch_id not in streamers:
                        streamers[streamer.twitch_id] = streamer
                        if len(streamers) >= criteria.limit:
                            break

                progress.update(offline_task, completed=remaining)
                self.progress.offline_found = len(streamers) - self.progress.live_found

            # Phase 3: Enrich profiles
            self.progress.current_phase = "enrichment"
            enrich_task = progress.add_task(
                "Enriching profiles...", total=len(streamers)
            )

            enriched = self._enrich_streamer_profiles(
                list(streamers.values()), progress, enrich_task
            )

            progress.update(enrich_task, completed=len(streamers))

        self.progress.processed = len(enriched)
        self.progress.current_phase = "complete"

        return enriched

    def _collect_live_streams(
        self,
        criteria: SearchCriteria,
        progress: Progress,
        task_id: int,
    ) -> list[Streamer]:
        """Collect live streams matching criteria.

        Args:
            criteria: Search criteria
            progress: Progress display
            task_id: Progress task ID

        Returns:
            List of live streamers
        """
        streamers: list[Streamer] = []
        cursor: Optional[str] = None
        collected = 0

        while collected < criteria.limit:
            try:
                response = self.client.get_streams(
                    game_id=criteria.game_id,
                    language=criteria.language,
                    first=min(100, criteria.limit - collected),
                    after=cursor,
                )
            except TwitchClientError as e:
                if self.verbose:
                    self.console.print(f"[yellow]Warning: {e}[/yellow]")
                self.progress.errors += 1
                break

            data = response.get("data", [])
            if not data:
                break

            for stream in data:
                viewer_count = stream.get("viewer_count", 0)

                # Apply viewer count filters
                if viewer_count < criteria.min_viewers:
                    continue
                if criteria.max_viewers and viewer_count > criteria.max_viewers:
                    continue

                streamer = Streamer(
                    twitch_id=stream["user_id"],
                    username=stream["user_login"],
                    display_name=stream["user_name"],
                    is_live=True,
                    viewer_count=viewer_count,
                    game_name=stream.get("game_name"),
                    language=stream.get("language"),
                    last_updated=datetime.utcnow(),
                )
                streamers.append(streamer)
                collected += 1
                progress.update(task_id, advance=1)

                if collected >= criteria.limit:
                    break

            # Check for pagination
            pagination = response.get("pagination", {})
            cursor = pagination.get("cursor")
            if not cursor:
                break

        return streamers

    def _collect_offline_channels(
        self,
        criteria: SearchCriteria,
        limit: int,
        progress: Progress,
        task_id: int,
    ) -> list[Streamer]:
        """Collect offline channels via search.

        Args:
            criteria: Search criteria
            limit: Maximum channels to collect
            progress: Progress display
            task_id: Progress task ID

        Returns:
            List of offline streamers
        """
        streamers: list[Streamer] = []

        # Use game name as search query if available
        query = criteria.game_name or criteria.game_id or "streamer"
        cursor: Optional[str] = None
        collected = 0

        while collected < limit:
            try:
                response = self.client.search_channels(
                    query=query,
                    first=min(100, limit - collected),
                    after=cursor,
                    live_only=False,
                )
            except TwitchClientError as e:
                if self.verbose:
                    self.console.print(f"[yellow]Warning: {e}[/yellow]")
                self.progress.errors += 1
                break

            data = response.get("data", [])
            if not data:
                break

            for channel in data:
                # Skip live channels (already collected)
                if channel.get("is_live", False):
                    continue

                # Filter by language if specified
                if criteria.language and channel.get("broadcaster_language") != criteria.language:
                    continue

                streamer = Streamer(
                    twitch_id=channel["id"],
                    username=channel["broadcaster_login"],
                    display_name=channel["display_name"],
                    is_live=False,
                    game_name=channel.get("game_name"),
                    language=channel.get("broadcaster_language"),
                    last_updated=datetime.utcnow(),
                )
                streamers.append(streamer)
                collected += 1
                progress.update(task_id, advance=1)

                if collected >= limit:
                    break

            # Check for pagination
            pagination = response.get("pagination", {})
            cursor = pagination.get("cursor")
            if not cursor:
                break

        return streamers

    def _enrich_streamer_profiles(
        self,
        streamers: list[Streamer],
        progress: Progress,
        task_id: int,
    ) -> list[Streamer]:
        """Enrich streamers with full profile data and extract contact info.

        Args:
            streamers: List of streamers to enrich
            progress: Progress display
            task_id: Progress task ID

        Returns:
            Enriched streamers with contact info
        """
        if not streamers:
            return []

        # Batch fetch user data
        user_ids = [s.twitch_id for s in streamers]

        try:
            users_data = self.client.get_users(user_ids)
        except TwitchClientError as e:
            if self.verbose:
                self.console.print(f"[yellow]Warning: Could not fetch user data: {e}[/yellow]")
            self.progress.errors += 1
            return streamers

        # Create lookup by ID
        users_by_id = {u["id"]: u for u in users_data}

        enriched: list[Streamer] = []
        for streamer in streamers:
            user_data = users_by_id.get(streamer.twitch_id)

            if user_data:
                description = user_data.get("description", "")

                # Extract contact information
                social_links = extract_social_links(description)
                emails = extract_emails(description)

                # Update streamer with enriched data
                streamer.description = description
                streamer.broadcaster_type = user_data.get("broadcaster_type", "")
                streamer.social_links = social_links
                streamer.emails = emails

            enriched.append(streamer)
            progress.update(task_id, advance=1)

        return enriched
