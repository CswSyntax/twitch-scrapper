"""Tests for social media and email extraction."""

import pytest

from twitch_scraper.extractors import (
    extract_discord,
    extract_emails,
    extract_instagram,
    extract_social_links,
    extract_tiktok,
    extract_twitter,
    extract_youtube,
)


class TestTwitterExtraction:
    """Tests for Twitter/X URL extraction."""

    def test_extract_twitter_com(self) -> None:
        """Extract twitter.com URL."""
        text = "Follow me on https://twitter.com/testuser"
        result = extract_twitter(text)
        assert result == "https://twitter.com/testuser"

    def test_extract_x_com(self) -> None:
        """Extract x.com URL."""
        text = "Follow me on https://x.com/testuser"
        result = extract_twitter(text)
        assert result == "https://twitter.com/testuser"

    def test_extract_twitter_without_https(self) -> None:
        """Extract Twitter URL without protocol."""
        text = "twitter.com/myhandle"
        result = extract_twitter(text)
        assert result == "https://twitter.com/myhandle"

    def test_no_twitter_returns_none(self) -> None:
        """Return None when no Twitter URL found."""
        text = "Check out my YouTube channel!"
        result = extract_twitter(text)
        assert result is None


class TestInstagramExtraction:
    """Tests for Instagram URL extraction."""

    def test_extract_instagram(self) -> None:
        """Extract Instagram URL."""
        text = "IG: https://instagram.com/myprofile"
        result = extract_instagram(text)
        assert result == "https://instagram.com/myprofile"

    def test_extract_instagram_with_www(self) -> None:
        """Extract Instagram URL with www."""
        text = "https://www.instagram.com/user123"
        result = extract_instagram(text)
        assert result == "https://instagram.com/user123"

    def test_no_instagram_returns_none(self) -> None:
        """Return None when no Instagram URL found."""
        text = "Follow my Twitter!"
        result = extract_instagram(text)
        assert result is None


class TestYouTubeExtraction:
    """Tests for YouTube URL extraction."""

    def test_extract_youtube_channel(self) -> None:
        """Extract YouTube channel URL."""
        text = "Subscribe: https://youtube.com/c/mychannel"
        result = extract_youtube(text)
        assert result == "https://youtube.com/mychannel"

    def test_extract_youtube_user(self) -> None:
        """Extract YouTube user URL."""
        text = "https://youtube.com/user/oldstyle"
        result = extract_youtube(text)
        assert result == "https://youtube.com/oldstyle"

    def test_extract_youtube_at_handle(self) -> None:
        """Extract YouTube @handle URL."""
        text = "https://youtube.com/@newhandle"
        result = extract_youtube(text)
        assert result == "https://youtube.com/newhandle"

    def test_no_youtube_returns_none(self) -> None:
        """Return None when no YouTube URL found."""
        text = "Check out my stream!"
        result = extract_youtube(text)
        assert result is None


class TestDiscordExtraction:
    """Tests for Discord URL extraction."""

    def test_extract_discord_gg(self) -> None:
        """Extract discord.gg URL."""
        text = "Join us: https://discord.gg/abc123"
        result = extract_discord(text)
        assert result == "https://discord.gg/abc123"

    def test_extract_discord_invite(self) -> None:
        """Extract discord.com/invite URL."""
        text = "Discord: https://discord.com/invite/xyz789"
        result = extract_discord(text)
        assert result == "https://discord.gg/xyz789"

    def test_no_discord_returns_none(self) -> None:
        """Return None when no Discord URL found."""
        text = "No Discord here"
        result = extract_discord(text)
        assert result is None


class TestTikTokExtraction:
    """Tests for TikTok URL extraction."""

    def test_extract_tiktok(self) -> None:
        """Extract TikTok URL."""
        text = "TikTok: https://tiktok.com/@myaccount"
        result = extract_tiktok(text)
        assert result == "https://tiktok.com/@myaccount"

    def test_no_tiktok_returns_none(self) -> None:
        """Return None when no TikTok URL found."""
        text = "No TikTok"
        result = extract_tiktok(text)
        assert result is None


class TestSocialLinksExtraction:
    """Tests for combined social links extraction."""

    def test_extract_all_social_links(self) -> None:
        """Extract multiple social links from text."""
        text = """
        Welcome to my channel!
        Twitter: https://twitter.com/testuser
        Instagram: https://instagram.com/testuser
        YouTube: https://youtube.com/c/testuser
        Discord: https://discord.gg/test
        TikTok: https://tiktok.com/@testuser
        """
        links = extract_social_links(text)

        assert links.twitter == "https://twitter.com/testuser"
        assert links.instagram == "https://instagram.com/testuser"
        assert links.youtube == "https://youtube.com/testuser"
        assert links.discord == "https://discord.gg/test"
        assert links.tiktok == "https://tiktok.com/@testuser"

    def test_extract_partial_social_links(self) -> None:
        """Extract only available social links."""
        text = "Twitter: https://twitter.com/onlytwitter"
        links = extract_social_links(text)

        assert links.twitter == "https://twitter.com/onlytwitter"
        assert links.instagram is None
        assert links.youtube is None
        assert links.discord is None
        assert links.tiktok is None

    def test_extract_empty_text(self) -> None:
        """Handle empty text."""
        links = extract_social_links("")
        assert links.twitter is None
        assert links.instagram is None


class TestEmailExtraction:
    """Tests for email extraction."""

    def test_extract_single_email(self) -> None:
        """Extract single email from text."""
        text = "Contact: business@company.com"
        emails = extract_emails(text)
        assert emails == ["business@company.com"]

    def test_extract_multiple_emails(self) -> None:
        """Extract multiple emails from text."""
        text = "Business: biz@company.com | Personal: me@personal.org"
        emails = extract_emails(text)
        assert len(emails) == 2
        assert "biz@company.com" in emails
        assert "me@personal.org" in emails

    def test_filter_false_positive_emails(self) -> None:
        """Filter out known false positive emails."""
        text = "Contact: example@example.com or noreply@service.com or real@email.com"
        emails = extract_emails(text)
        assert emails == ["real@email.com"]

    def test_filter_noreply_emails(self) -> None:
        """Filter out noreply emails."""
        text = "noreply@twitch.tv and no-reply@company.com"
        emails = extract_emails(text)
        assert emails == []

    def test_no_duplicates(self) -> None:
        """No duplicate emails in result."""
        text = "Email: test@test.org | Also: test@test.org"
        emails = extract_emails(text)
        # Note: test@test.org is filtered as false positive, so expect empty
        # Let's use a valid email instead
        text2 = "Email: real@domain.com | Also: real@domain.com"
        emails2 = extract_emails(text2)
        assert len(emails2) == 1

    def test_empty_text(self) -> None:
        """Handle empty text."""
        emails = extract_emails("")
        assert emails == []

    def test_no_emails(self) -> None:
        """Handle text without emails."""
        text = "No contact info here!"
        emails = extract_emails(text)
        assert emails == []
