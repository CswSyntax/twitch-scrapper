# Feature Specification: Twitch Streamer Finder

**Feature Branch**: `001-twitch-streamer-finder`
**Created**: 2026-01-29
**Status**: Draft
**Input**: User description: "Python tool to find and collect contact information from Twitch streamers using the Twitch API with filtering, social media extraction, and CSV export"

## Clarifications

### Session 2026-01-29

- Q: What is the data collection scope - live only, or both live and offline streamers? → A: Both live and offline (collect live streamers, then separately fetch offline channel data for broader coverage)
- Q: Should the system provide progress feedback during collection? → A: Yes, show progress indicator (count/percentage) as collection proceeds

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find Streamers by Criteria (Priority: P1)

As a marketing professional or business development person, I want to search for Twitch streamers based on specific criteria (viewer count, game, language) so that I can identify potential partnership candidates within my target audience.

**Why this priority**: This is the core value proposition - without the ability to find relevant streamers, no other features are useful. It enables the primary use case of discovering streamers for outreach.

**Independent Test**: Can be fully tested by searching for streamers playing a specific game with a viewer range (e.g., 50-500 viewers, Valorant, German language) and verifying that matching streamers are returned with their basic information.

**Acceptance Scenarios**:

1. **Given** valid API credentials are configured, **When** user searches for streamers with viewer count between 50-500 playing Valorant, **Then** system returns a list of currently live streamers matching these criteria
2. **Given** valid API credentials are configured, **When** user filters by German language, **Then** only streamers broadcasting in German are included in results
3. **Given** valid API credentials are configured, **When** no streamers match the criteria, **Then** system displays a clear message indicating no results found

---

### User Story 2 - Export Streamer Data to CSV (Priority: P2)

As a marketing professional, I want to export the collected streamer data to CSV format so that I can use the data in spreadsheet applications for outreach campaigns and tracking.

**Why this priority**: Export functionality enables the practical use of collected data. Without export, users cannot effectively use the information for their outreach workflows.

**Independent Test**: Can be fully tested by running a search, exporting results to CSV, and opening the file in a spreadsheet application to verify all columns are properly formatted.

**Acceptance Scenarios**:

1. **Given** a list of found streamers, **When** user exports to CSV, **Then** a properly formatted CSV file is created with columns for username, average viewers, game, email (if found), and social media links
2. **Given** a search returned 100 streamers, **When** user exports to CSV, **Then** all 100 records are included in the export
3. **Given** some streamers have missing contact information, **When** exported to CSV, **Then** empty cells are used for missing data (no errors or malformed rows)

---

### User Story 3 - Extract Social Media Links (Priority: P2)

As a marketing professional, I want the system to automatically extract social media links (Twitter/X, Instagram, YouTube, Discord, TikTok) from streamer profiles so that I have multiple contact options for outreach.

**Why this priority**: Social media links are often the most reliable contact method for streamers. This significantly increases the value of each found streamer record.

**Independent Test**: Can be fully tested by fetching a known streamer's channel information and verifying that all available social media links from their description/panels are correctly extracted and categorized.

**Acceptance Scenarios**:

1. **Given** a streamer has Twitter linked in their channel description, **When** system extracts contact info, **Then** the Twitter handle/URL is captured in the social_links field
2. **Given** a streamer has multiple social platforms, **When** system extracts contact info, **Then** all platforms (Twitter, Instagram, YouTube, Discord, TikTok) are captured separately
3. **Given** a streamer has no social links, **When** system extracts contact info, **Then** the social_links field is empty (no errors)

---

### User Story 4 - Extract Email from Channel Description (Priority: P3)

As a marketing professional, I want the system to attempt to find email addresses in streamer channel descriptions and panels so that I can use email for business inquiries.

**Why this priority**: While useful, email extraction is less reliable than social media links. Many streamers don't publicly list emails, making this a "nice to have" enhancement.

**Independent Test**: Can be fully tested by processing channel descriptions containing known email patterns and verifying correct extraction.

**Acceptance Scenarios**:

1. **Given** a streamer has "business@example.com" in their channel description, **When** system extracts contact info, **Then** the email is captured in the email field
2. **Given** a streamer has multiple emails, **When** system extracts contact info, **Then** all found emails are captured
3. **Given** a channel description contains text like "email me at" without an actual email, **When** system extracts contact info, **Then** no false positive email is captured

---

### User Story 5 - Export to JSON Format (Priority: P3)

As a developer or data analyst, I want to export collected data to JSON format so that I can integrate it with other tools and scripts.

**Why this priority**: JSON export is a secondary format primarily useful for technical users or automated pipelines. CSV covers the majority of use cases.

**Independent Test**: Can be fully tested by exporting results to JSON and parsing the file to verify valid JSON structure with all expected fields.

**Acceptance Scenarios**:

1. **Given** a list of found streamers, **When** user exports to JSON, **Then** a valid JSON file is created with all streamer data
2. **Given** a streamer has nested social_links data, **When** exported to JSON, **Then** the nested structure is properly preserved

---

### Edge Cases

- What happens when Twitch API rate limits are reached? System should pause and retry with appropriate delays.
- What happens when API credentials are invalid or expired? System should display clear error message with instructions to check credentials.
- What happens when a streamer's channel is banned/deleted during data collection? System should skip and continue with remaining streamers.
- How does system handle non-standard email formats in descriptions? System should use conservative pattern matching to avoid false positives.
- What happens when network connection is lost mid-collection? System should save progress and allow resumption.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST authenticate with Twitch API using OAuth2 client credentials flow
- **FR-002**: System MUST allow filtering streamers by minimum and maximum viewer count
- **FR-003**: System MUST allow filtering streamers by game/category (using game name or ID)
- **FR-004**: System MUST allow filtering streamers by broadcast language
- **FR-005**: System MUST retrieve streamer profile information including username, channel description, and follower count
- **FR-006**: System MUST extract social media links (Twitter/X, Instagram, YouTube, Discord, TikTok) from channel descriptions
- **FR-007**: System MUST attempt to extract email addresses from channel descriptions using pattern matching
- **FR-008**: System MUST export collected data to CSV format with consistent column structure
- **FR-009**: System MUST export collected data to JSON format
- **FR-010**: System MUST respect Twitch API rate limits (800 requests/minute) by implementing request throttling
- **FR-011**: System MUST handle API errors gracefully and continue processing remaining streamers
- **FR-012**: System MUST store API credentials securely using environment variables
- **FR-013**: System MUST only collect publicly available data from the Twitch API
- **FR-014**: System MUST support collecting both live streamers and offline channel data for broader coverage
- **FR-015**: System MUST display progress indicator (count/percentage) during data collection operations

### Key Entities

- **Streamer**: A Twitch content creator with attributes: twitch_id, username, average_viewers, games_played (list), email (if found), social_links (dictionary by platform), follower_count, last_updated timestamp
- **SearchCriteria**: Filter parameters for finding streamers: min_viewers, max_viewers, game_ids (list), language_code
- **ExportResult**: Output file containing streamer data in either CSV or JSON format

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can configure search criteria and retrieve matching streamers within 60 seconds for up to 100 results
- **SC-002**: System successfully extracts social media links from at least 80% of streamers who have them publicly listed
- **SC-003**: Exported CSV files open correctly in common spreadsheet applications (Excel, Google Sheets) without formatting issues
- **SC-004**: System handles rate limiting without errors, completing large requests (1000+ streamers) through automatic throttling
- **SC-005**: Users can successfully configure API credentials and run their first search within 5 minutes of initial setup

## Assumptions

- User has or will create a Twitch Developer account at dev.twitch.tv
- User will register an application to obtain Client ID and Client Secret
- System collects both live streamers (via streams endpoint) and offline channel data (via search/users endpoints) for broader coverage
- Social media links are primarily found in channel descriptions and panel content
- Email addresses follow standard email format patterns (user@domain.tld)
- Users have basic familiarity with running command-line tools
- Primary target audience speaks German (default language filter), but this can be configured

## Out of Scope

- Scraping Twitch website directly (API-only approach for ToS compliance)
- Automated outreach or messaging functionality
- Historical viewer data or analytics
- Streamer schedule or VOD information
- Real-time monitoring or alerts
- Web-based user interface (command-line tool only)
- Database storage (export-based workflow only)
