"""Extractors for social media links and emails from text."""

import re
from typing import Optional

from twitch_scraper.models import SocialLinks


# Social media URL patterns
TWITTER_PATTERN = re.compile(
    r'(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)',
    re.IGNORECASE
)

INSTAGRAM_PATTERN = re.compile(
    r'(?:https?://)?(?:www\.)?instagram\.com/([a-zA-Z0-9_.]+)',
    re.IGNORECASE
)

YOUTUBE_PATTERNS = [
    re.compile(r'(?:https?://)?(?:www\.)?youtube\.com/(?:c/|channel/|user/|@)?([a-zA-Z0-9_-]+)', re.IGNORECASE),
    re.compile(r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)', re.IGNORECASE),
]

DISCORD_PATTERNS = [
    re.compile(r'(?:https?://)?(?:www\.)?discord\.gg/([a-zA-Z0-9]+)', re.IGNORECASE),
    re.compile(r'(?:https?://)?(?:www\.)?discord\.com/invite/([a-zA-Z0-9]+)', re.IGNORECASE),
]

TIKTOK_PATTERN = re.compile(
    r'(?:https?://)?(?:www\.)?tiktok\.com/@([a-zA-Z0-9_.]+)',
    re.IGNORECASE
)

# Email pattern - standard format
EMAIL_PATTERN = re.compile(
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    re.IGNORECASE
)

# False positive emails to exclude
FALSE_POSITIVE_EMAILS = {
    'example@example.com',
    'email@example.com',
    'your@email.com',
    'youremail@email.com',
    'noreply@twitch.tv',
    'support@twitch.tv',
    'test@test.com',
    'user@domain.com',
}

# False positive email patterns
FALSE_POSITIVE_EMAIL_PATTERNS = [
    re.compile(r'^noreply@', re.IGNORECASE),
    re.compile(r'^no-reply@', re.IGNORECASE),
    re.compile(r'^donotreply@', re.IGNORECASE),
    re.compile(r'^support@', re.IGNORECASE),
    re.compile(r'^info@twitch', re.IGNORECASE),
    re.compile(r'@example\.', re.IGNORECASE),
]


def extract_twitter(text: str) -> Optional[str]:
    """Extract Twitter/X URL from text.

    Args:
        text: Text to search

    Returns:
        Twitter URL if found
    """
    match = TWITTER_PATTERN.search(text)
    if match:
        username = match.group(1)
        return f"https://twitter.com/{username}"
    return None


def extract_instagram(text: str) -> Optional[str]:
    """Extract Instagram URL from text.

    Args:
        text: Text to search

    Returns:
        Instagram URL if found
    """
    match = INSTAGRAM_PATTERN.search(text)
    if match:
        username = match.group(1)
        return f"https://instagram.com/{username}"
    return None


def extract_youtube(text: str) -> Optional[str]:
    """Extract YouTube URL from text.

    Args:
        text: Text to search

    Returns:
        YouTube URL if found
    """
    for pattern in YOUTUBE_PATTERNS:
        match = pattern.search(text)
        if match:
            identifier = match.group(1)
            return f"https://youtube.com/{identifier}"
    return None


def extract_discord(text: str) -> Optional[str]:
    """Extract Discord invite URL from text.

    Args:
        text: Text to search

    Returns:
        Discord URL if found
    """
    for pattern in DISCORD_PATTERNS:
        match = pattern.search(text)
        if match:
            invite_code = match.group(1)
            return f"https://discord.gg/{invite_code}"
    return None


def extract_tiktok(text: str) -> Optional[str]:
    """Extract TikTok URL from text.

    Args:
        text: Text to search

    Returns:
        TikTok URL if found
    """
    match = TIKTOK_PATTERN.search(text)
    if match:
        username = match.group(1)
        return f"https://tiktok.com/@{username}"
    return None


def extract_social_links(text: str) -> SocialLinks:
    """Extract all social media links from text.

    Args:
        text: Text to search (typically channel description)

    Returns:
        SocialLinks object with extracted URLs
    """
    if not text:
        return SocialLinks()

    return SocialLinks(
        twitter=extract_twitter(text),
        instagram=extract_instagram(text),
        youtube=extract_youtube(text),
        discord=extract_discord(text),
        tiktok=extract_tiktok(text),
    )


def _is_false_positive_email(email: str) -> bool:
    """Check if email is a known false positive.

    Args:
        email: Email to check

    Returns:
        True if email should be excluded
    """
    email_lower = email.lower()

    # Check exact matches
    if email_lower in FALSE_POSITIVE_EMAILS:
        return True

    # Check pattern matches
    for pattern in FALSE_POSITIVE_EMAIL_PATTERNS:
        if pattern.search(email_lower):
            return True

    return False


def extract_emails(text: str) -> list[str]:
    """Extract email addresses from text.

    Args:
        text: Text to search (typically channel description)

    Returns:
        List of valid email addresses found
    """
    if not text:
        return []

    matches = EMAIL_PATTERN.findall(text)

    # Filter out false positives and duplicates
    emails: list[str] = []
    seen: set[str] = set()

    for email in matches:
        email_lower = email.lower()
        if email_lower not in seen and not _is_false_positive_email(email):
            emails.append(email)
            seen.add(email_lower)

    return emails
