"""Tests for CSV and JSON export functions."""

import csv
import json
from pathlib import Path

import pytest

from twitch_scraper.exporters import export_to_csv, export_to_json
from twitch_scraper.models import ExportConfig, SearchCriteria, Streamer


class TestCSVExport:
    """Tests for CSV export functionality."""

    def test_export_to_csv_creates_file(
        self, sample_streamers: list[Streamer], tmp_path: Path
    ) -> None:
        """CSV export creates file with correct path."""
        output_path = tmp_path / "test_output.csv"
        config = ExportConfig(format="csv", output_path=str(output_path))

        result = export_to_csv(sample_streamers, config)

        assert result == output_path
        assert output_path.exists()

    def test_export_to_csv_has_header(
        self, sample_streamers: list[Streamer], tmp_path: Path
    ) -> None:
        """CSV export includes header row."""
        output_path = tmp_path / "test_output.csv"
        config = ExportConfig(format="csv", output_path=str(output_path))

        export_to_csv(sample_streamers, config)

        with output_path.open("r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)

        expected_columns = [
            "username", "display_name", "twitch_id", "is_live", "viewer_count",
            "game_name", "language", "broadcaster_type", "email",
            "twitter", "instagram", "youtube", "discord", "tiktok",
        ]
        assert header == expected_columns

    def test_export_to_csv_has_data_rows(
        self, sample_streamers: list[Streamer], tmp_path: Path
    ) -> None:
        """CSV export includes all streamer data."""
        output_path = tmp_path / "test_output.csv"
        config = ExportConfig(format="csv", output_path=str(output_path))

        export_to_csv(sample_streamers, config)

        with output_path.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["username"] == "teststreamer"
        assert rows[0]["is_live"] == "true"
        assert rows[1]["username"] == "anotherstreamer"
        assert rows[1]["is_live"] == "false"

    def test_export_to_csv_handles_missing_values(
        self, tmp_path: Path
    ) -> None:
        """CSV export handles None values as empty strings."""
        streamer = Streamer(
            twitch_id="999",
            username="minimal",
            display_name="Minimal",
            is_live=False,
        )
        output_path = tmp_path / "minimal.csv"
        config = ExportConfig(format="csv", output_path=str(output_path))

        export_to_csv([streamer], config)

        with output_path.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            row = next(reader)

        assert row["viewer_count"] == ""
        assert row["game_name"] == ""
        assert row["email"] == ""
        assert row["twitter"] == ""

    def test_export_to_csv_utf8_encoding(
        self, tmp_path: Path
    ) -> None:
        """CSV export uses UTF-8 encoding with BOM."""
        streamer = Streamer(
            twitch_id="unicode",
            username="unicodeuser",
            display_name="Ümläüt Strëämër",
            is_live=True,
        )
        output_path = tmp_path / "unicode.csv"
        config = ExportConfig(format="csv", output_path=str(output_path))

        export_to_csv([streamer], config)

        # Check BOM is present
        with output_path.open("rb") as f:
            bom = f.read(3)
        assert bom == b"\xef\xbb\xbf"

        # Check content is readable
        with output_path.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            row = next(reader)

        assert row["display_name"] == "Ümläüt Strëämër"


class TestJSONExport:
    """Tests for JSON export functionality."""

    def test_export_to_json_creates_file(
        self, sample_streamers: list[Streamer], tmp_path: Path
    ) -> None:
        """JSON export creates file with correct path."""
        output_path = tmp_path / "test_output.json"
        config = ExportConfig(format="json", output_path=str(output_path))

        result = export_to_json(sample_streamers, config)

        assert result == output_path
        assert output_path.exists()

    def test_export_to_json_valid_structure(
        self, sample_streamers: list[Streamer], tmp_path: Path
    ) -> None:
        """JSON export has valid structure with metadata and streamers."""
        output_path = tmp_path / "test_output.json"
        config = ExportConfig(format="json", output_path=str(output_path))

        export_to_json(sample_streamers, config)

        with output_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        assert "metadata" in data
        assert "streamers" in data
        assert "generated_at" in data["metadata"]
        assert "total_results" in data["metadata"]
        assert data["metadata"]["total_results"] == 2

    def test_export_to_json_includes_search_criteria(
        self,
        sample_streamers: list[Streamer],
        sample_search_criteria: SearchCriteria,
        tmp_path: Path,
    ) -> None:
        """JSON export includes search criteria in metadata."""
        output_path = tmp_path / "test_output.json"
        config = ExportConfig(format="json", output_path=str(output_path))

        export_to_json(sample_streamers, config, sample_search_criteria)

        with output_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        criteria = data["metadata"]["search_criteria"]
        assert criteria["game"] == "Valorant"
        assert criteria["min_viewers"] == 50
        assert criteria["max_viewers"] == 500
        assert criteria["language"] == "de"

    def test_export_to_json_streamer_structure(
        self, sample_streamer: Streamer, tmp_path: Path
    ) -> None:
        """JSON export has correct streamer structure."""
        output_path = tmp_path / "test_output.json"
        config = ExportConfig(format="json", output_path=str(output_path))

        export_to_json([sample_streamer], config)

        with output_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        streamer_data = data["streamers"][0]
        assert streamer_data["twitch_id"] == "123456"
        assert streamer_data["username"] == "teststreamer"
        assert streamer_data["is_live"] is True
        assert streamer_data["viewer_count"] == 250
        assert "social_links" in streamer_data
        assert streamer_data["social_links"]["twitter"] == "https://twitter.com/teststreamer"

    def test_export_to_json_nested_social_links(
        self, sample_streamer: Streamer, tmp_path: Path
    ) -> None:
        """JSON export preserves nested social_links structure."""
        output_path = tmp_path / "test_output.json"
        config = ExportConfig(format="json", output_path=str(output_path))

        export_to_json([sample_streamer], config)

        with output_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        social_links = data["streamers"][0]["social_links"]
        assert "twitter" in social_links
        assert "instagram" in social_links
        assert "youtube" in social_links
        assert "discord" in social_links
        assert "tiktok" in social_links

    def test_export_to_json_readable_format(
        self, sample_streamers: list[Streamer], tmp_path: Path
    ) -> None:
        """JSON export is formatted with indentation."""
        output_path = tmp_path / "test_output.json"
        config = ExportConfig(format="json", output_path=str(output_path))

        export_to_json(sample_streamers, config)

        content = output_path.read_text(encoding="utf-8")
        # Indented JSON has newlines
        assert "\n" in content
        # And spaces for indentation
        assert "  " in content
