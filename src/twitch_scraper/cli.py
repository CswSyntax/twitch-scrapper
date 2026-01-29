"""CLI interface using Typer with rich output."""

from typing import Annotated, Optional

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from twitch_scraper import __version__
from twitch_scraper.client import AuthenticationError, TwitchClient
from twitch_scraper.config import get_settings

app = typer.Typer(
    name="twitch-scraper",
    help="Find Twitch streamers and extract contact information.",
    add_completion=False,
)

console = Console()
err_console = Console(stderr=True)


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print an error message to stderr."""
    err_console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]![/yellow] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


@app.command()
def auth() -> None:
    """Test authentication with Twitch API."""
    try:
        settings = get_settings()
    except ValidationError:
        print_error("Authentication failed")
        print_error("Missing API credentials")
        console.print()
        console.print("Please ensure these environment variables are set:")
        console.print("  TWITCH_CLIENT_ID=your_client_id")
        console.print("  TWITCH_CLIENT_SECRET=your_client_secret")
        raise typer.Exit(2)

    try:
        with TwitchClient(settings) as client:
            token_data = client.authenticate()
            expires_in_days = token_data["expires_in"] // 86400

            print_success("Authentication successful")
            console.print(f"  Token expires in: {expires_in_days} days")
            console.print(f"  Rate limit: {settings.rate_limit_requests} requests/minute")

    except AuthenticationError as e:
        print_error("Authentication failed")
        print_error(str(e))
        console.print()
        console.print("Please ensure these environment variables are set:")
        console.print("  TWITCH_CLIENT_ID=your_client_id")
        console.print("  TWITCH_CLIENT_SECRET=your_client_secret")
        raise typer.Exit(2)


@app.command()
def games(
    query: Annotated[str, typer.Argument(help="Game name to search for")],
) -> None:
    """Search for game IDs by name."""
    try:
        settings = get_settings()
    except ValidationError:
        print_error("Missing API credentials. Run 'twitch-scraper auth' for help.")
        raise typer.Exit(2)

    try:
        with TwitchClient(settings) as client:
            results = client.search_games(query)

            if not results:
                print_warning(f'No games found for "{query}"')
                raise typer.Exit(0)

            console.print(f'\nSearch results for "{query}":\n')

            table = Table(show_header=True)
            table.add_column("ID", style="cyan")
            table.add_column("Name")

            for game in results[:10]:  # Show top 10
                table.add_row(game["id"], game["name"])

            console.print(table)
            console.print(f"\nUse --game-id {results[0]['id']} with the search command.")

    except AuthenticationError:
        print_error("Authentication failed. Check your credentials.")
        raise typer.Exit(2)


@app.command()
def search(
    game: Annotated[
        Optional[str],
        typer.Option("--game", "-g", help="Game/category name to filter by"),
    ] = None,
    game_id: Annotated[
        Optional[str],
        typer.Option("--game-id", help="Twitch game ID (alternative to --game)"),
    ] = None,
    min_viewers: Annotated[
        int,
        typer.Option("--min-viewers", "-m", help="Minimum viewer count"),
    ] = 0,
    max_viewers: Annotated[
        Optional[int],
        typer.Option("--max-viewers", "-M", help="Maximum viewer count"),
    ] = None,
    language: Annotated[
        str,
        typer.Option("--language", "-l", help="Broadcast language (ISO 639-1)"),
    ] = "de",
    include_offline: Annotated[
        bool,
        typer.Option("--include-offline/--live-only", help="Include offline channels"),
    ] = True,
    limit: Annotated[
        int,
        typer.Option("--limit", "-n", help="Maximum streamers to collect"),
    ] = 100,
    output: Annotated[
        str,
        typer.Option("--output", "-o", help="Output file path"),
    ] = "streamers.csv",
    format_: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: csv, json"),
    ] = "csv",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed progress"),
    ] = False,
) -> None:
    """Search for Twitch streamers based on criteria and export results."""
    from twitch_scraper.exporters import export_to_csv, export_to_json
    from twitch_scraper.models import ExportConfig, SearchCriteria
    from twitch_scraper.scraper import StreamerScraper

    # Validate format
    if format_ not in ("csv", "json"):
        print_error(f"Invalid format: {format_}. Use 'csv' or 'json'.")
        raise typer.Exit(3)

    try:
        settings = get_settings()
    except ValidationError:
        print_error("Missing API credentials. Run 'twitch-scraper auth' for help.")
        raise typer.Exit(2)

    # Build search criteria
    try:
        criteria = SearchCriteria(
            min_viewers=min_viewers,
            max_viewers=max_viewers,
            game_name=game,
            game_id=game_id,
            language=language,
            include_offline=include_offline,
            limit=limit,
        )
    except ValueError as e:
        print_error(f"Invalid search criteria: {e}")
        raise typer.Exit(3)

    # Build export config
    export_config = ExportConfig(format=format_, output_path=output)

    try:
        with TwitchClient(settings) as client:
            scraper = StreamerScraper(client, verbose=verbose)

            # Resolve game name to ID if needed
            if criteria.game_name and not criteria.game_id:
                print_info(f'Looking up game ID for "{criteria.game_name}"...')
                resolved_id = client.get_game_id(criteria.game_name)
                if not resolved_id:
                    print_error(f'Game not found: "{criteria.game_name}"')
                    print_info('Use "twitch-scraper games <name>" to search for games.')
                    raise typer.Exit(1)
                criteria.game_id = resolved_id

            # Collect streamers
            streamers = scraper.collect(criteria)

            if not streamers:
                print_warning("No streamers found matching criteria.")
                raise typer.Exit(0)

            # Export results
            if format_ == "csv":
                export_to_csv(streamers, export_config)
            else:
                export_to_json(streamers, export_config, criteria)

            # Print summary
            console.print()
            print_success(f"Found {len(streamers)} streamers")

            live_count = sum(1 for s in streamers if s.is_live)
            offline_count = len(streamers) - live_count
            with_email = sum(1 for s in streamers if s.emails)
            with_social = sum(
                1 for s in streamers
                if s.social_links.twitter or s.social_links.instagram or
                   s.social_links.youtube or s.social_links.discord or
                   s.social_links.tiktok
            )

            console.print(f"  - Live: {live_count}")
            console.print(f"  - Offline: {offline_count}")
            console.print(f"  - With email: {with_email}")
            console.print(f"  - With social links: {with_social}")
            console.print()
            print_success(f"Exported to: {output}")

    except AuthenticationError:
        print_error("Authentication failed. Check your credentials.")
        raise typer.Exit(2)
    except Exception as e:
        print_error(f"Error: {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"twitch-scraper version {__version__}")
        raise typer.Exit(0)


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version", "-V",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """Twitch Streamer Finder - Find and extract contact info from Twitch streamers."""
    pass


if __name__ == "__main__":
    app()
