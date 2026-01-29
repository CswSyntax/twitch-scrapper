# Tasks: Twitch Streamer Finder

**Input**: Design documents from `/specs/001-twitch-streamer-finder/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-interface.md

**Tests**: Not explicitly requested in spec - included as optional enhancement tasks in Polish phase.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/twitch_scraper/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure: `src/twitch_scraper/`, `tests/`
- [x] T002 Create pyproject.toml with dependencies: httpx, typer, rich, pydantic-settings, pyrate-limiter
- [x] T003 [P] Create .env.example with TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET placeholders
- [x] T004 [P] Create .gitignore for Python project (venv, __pycache__, .env, *.csv, *.json exports)
- [x] T005 [P] Create src/twitch_scraper/__init__.py with version info
- [x] T006 [P] Create src/twitch_scraper/__main__.py as entry point

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Implement Settings class with pydantic-settings in src/twitch_scraper/config.py (TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, .env support)
- [x] T008 [P] Create base Pydantic models (Streamer, SocialLinks, SearchCriteria) in src/twitch_scraper/models.py
- [x] T009 Implement TwitchClient class with OAuth2 authentication in src/twitch_scraper/client.py
- [x] T010 Add rate limiting to TwitchClient using pyrate-limiter (800 req/min) in src/twitch_scraper/client.py
- [x] T011 Implement exponential backoff for 429 responses in src/twitch_scraper/client.py
- [x] T012 Create Typer app skeleton with `auth` command in src/twitch_scraper/cli.py
- [x] T013 Add rich console output helpers in src/twitch_scraper/cli.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Find Streamers by Criteria (Priority: P1) 🎯 MVP

**Goal**: Search for Twitch streamers based on viewer count, game, and language filters

**Independent Test**: Run `twitch-scraper search --game "Valorant" --min-viewers 50 --max-viewers 500 --language de` and verify matching live streamers are returned

### Implementation for User Story 1

- [x] T014 [US1] Implement get_streams() method in TwitchClient for live streams endpoint in src/twitch_scraper/client.py
- [x] T015 [US1] Add game_id lookup method get_game_id() to TwitchClient in src/twitch_scraper/client.py
- [x] T016 [US1] Implement get_users() batch method in TwitchClient (up to 100 IDs) in src/twitch_scraper/client.py
- [x] T017 [US1] Implement search_channels() for offline streamer discovery in src/twitch_scraper/client.py
- [x] T018 [US1] Create StreamerScraper class in src/twitch_scraper/scraper.py
- [x] T019 [US1] Implement collect_live_streams() in StreamerScraper with pagination in src/twitch_scraper/scraper.py
- [x] T020 [US1] Implement collect_offline_channels() in StreamerScraper in src/twitch_scraper/scraper.py
- [x] T021 [US1] Implement enrich_streamer_profiles() to fetch full user data in src/twitch_scraper/scraper.py
- [x] T022 [US1] Add rich.progress.Progress display during collection in src/twitch_scraper/scraper.py
- [x] T023 [US1] Implement `search` command in CLI with all options in src/twitch_scraper/cli.py
- [x] T024 [US1] Add `games` helper command for game ID lookup in src/twitch_scraper/cli.py
- [x] T025 [US1] Implement viewer count filtering (min/max) in src/twitch_scraper/scraper.py
- [x] T026 [US1] Add error handling for API failures with graceful skip in src/twitch_scraper/scraper.py

**Checkpoint**: User Story 1 complete - can search and display streamers matching criteria

---

## Phase 4: User Story 2 - Export to CSV (Priority: P2)

**Goal**: Export collected streamer data to CSV format for spreadsheet applications

**Independent Test**: Run search with `--format csv --output test.csv`, open in Excel/Google Sheets, verify all columns present

### Implementation for User Story 2

- [x] T027 [US2] Create export_to_csv() function in src/twitch_scraper/exporters.py
- [x] T028 [US2] Define CSV column order matching contract (username, display_name, twitch_id, is_live, viewer_count, game_name, language, broadcaster_type, email, twitter, instagram, youtube, discord, tiktok)
- [x] T029 [US2] Handle missing/None values as empty strings in CSV export in src/twitch_scraper/exporters.py
- [x] T030 [US2] Add UTF-8 encoding with BOM for Excel compatibility in src/twitch_scraper/exporters.py
- [x] T031 [US2] Wire CSV export to `search` command --format csv option in src/twitch_scraper/cli.py

**Checkpoint**: User Story 2 complete - can export search results to CSV

---

## Phase 5: User Story 3 - Extract Social Media Links (Priority: P2)

**Goal**: Automatically extract social media links from streamer channel descriptions

**Independent Test**: Process a description containing "twitter.com/example" and verify Twitter link is extracted to social_links.twitter

### Implementation for User Story 3

- [x] T032 [P] [US3] Create SocialMediaExtractor class in src/twitch_scraper/extractors.py
- [x] T033 [US3] Implement Twitter/X URL pattern matching (twitter.com/, x.com/) in src/twitch_scraper/extractors.py
- [x] T034 [US3] Implement Instagram URL pattern matching (instagram.com/) in src/twitch_scraper/extractors.py
- [x] T035 [US3] Implement YouTube URL pattern matching (youtube.com/, youtu.be/) in src/twitch_scraper/extractors.py
- [x] T036 [US3] Implement Discord URL pattern matching (discord.gg/, discord.com/invite/) in src/twitch_scraper/extractors.py
- [x] T037 [US3] Implement TikTok URL pattern matching (tiktok.com/@) in src/twitch_scraper/extractors.py
- [x] T038 [US3] Add extract_social_links() method returning SocialLinks model in src/twitch_scraper/extractors.py
- [x] T039 [US3] Integrate social media extraction into enrich_streamer_profiles() in src/twitch_scraper/scraper.py

**Checkpoint**: User Story 3 complete - social media links extracted from descriptions

---

## Phase 6: User Story 4 - Extract Email (Priority: P3)

**Goal**: Extract email addresses from channel descriptions for business inquiries

**Independent Test**: Process a description containing "business@example.com" and verify email is captured

### Implementation for User Story 4

- [x] T040 [P] [US4] Create EmailExtractor class in src/twitch_scraper/extractors.py
- [x] T041 [US4] Implement email regex pattern matching in src/twitch_scraper/extractors.py
- [x] T042 [US4] Add false positive filtering (exclude example@example.com, noreply@, etc.) in src/twitch_scraper/extractors.py
- [x] T043 [US4] Add extract_emails() method returning list of emails in src/twitch_scraper/extractors.py
- [x] T044 [US4] Integrate email extraction into enrich_streamer_profiles() in src/twitch_scraper/scraper.py

**Checkpoint**: User Story 4 complete - emails extracted from descriptions

---

## Phase 7: User Story 5 - Export to JSON (Priority: P3)

**Goal**: Export collected data to JSON format for programmatic use

**Independent Test**: Run search with `--format json --output test.json`, parse file, verify valid JSON with metadata

### Implementation for User Story 5

- [x] T045 [P] [US5] Create export_to_json() function in src/twitch_scraper/exporters.py
- [x] T046 [US5] Implement JSON structure with metadata section (generated_at, search_criteria, total_results) in src/twitch_scraper/exporters.py
- [x] T047 [US5] Add streamers array with nested social_links structure in src/twitch_scraper/exporters.py
- [x] T048 [US5] Use ensure_ascii=False and indent=2 for readable output in src/twitch_scraper/exporters.py
- [x] T049 [US5] Wire JSON export to `search` command --format json option in src/twitch_scraper/cli.py

**Checkpoint**: User Story 5 complete - can export to JSON format

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T050 [P] Add --verbose flag for detailed logging output in src/twitch_scraper/cli.py
- [x] T051 [P] Add summary statistics display after search (live count, offline count, with email, with social links) in src/twitch_scraper/cli.py
- [x] T052 [P] Implement exit codes per CLI contract (0=success, 2=auth failed, etc.) in src/twitch_scraper/cli.py
- [x] T053 Create tests/conftest.py with mock API response fixtures
- [x] T054 [P] Add test_client.py for TwitchClient authentication tests in tests/test_client.py
- [x] T055 [P] Add test_extractors.py for social media and email extraction in tests/test_extractors.py
- [x] T056 [P] Add test_exporters.py for CSV and JSON output in tests/test_exporters.py
- [x] T057 Run quickstart.md validation - verify setup instructions work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (P1): Core search - must complete first for MVP
  - US2 (P2): CSV export - can start after US1
  - US3 (P2): Social extraction - can run parallel with US2
  - US4 (P3): Email extraction - can run parallel with US3
  - US5 (P3): JSON export - can run parallel with US4
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Requires Foundational - no other story dependencies
- **User Story 2 (P2)**: Requires US1 output (streamers to export)
- **User Story 3 (P2)**: Requires Foundational - integrates with US1 enrichment
- **User Story 4 (P3)**: Requires Foundational - integrates with US1 enrichment
- **User Story 5 (P3)**: Requires US1 output - similar to US2

### Within Each User Story

- API client methods before scraper logic
- Scraper logic before CLI integration
- Extractors before scraper integration
- Story complete before moving to next priority

### Parallel Opportunities

- T003, T004, T005, T006 (Setup) can run in parallel
- T008 (models) can run parallel with T007 (config)
- T032, T040 (extractors) can run parallel
- T045 (JSON export) can run parallel with T040-T044 (email extraction)
- T053-T056 (tests) can all run in parallel

---

## Parallel Example: Setup Phase

```bash
# Launch all parallel setup tasks together:
Task: "T003 Create .env.example"
Task: "T004 Create .gitignore"
Task: "T005 Create __init__.py"
Task: "T006 Create __main__.py"
```

## Parallel Example: Extractors (US3 + US4)

```bash
# Launch extractor classes in parallel:
Task: "T032 Create SocialMediaExtractor class"
Task: "T040 Create EmailExtractor class"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (auth, models, client)
3. Complete Phase 3: User Story 1 (search command)
4. **STOP and VALIDATE**: Test `twitch-scraper search --game "Valorant"` works
5. Can demo/use immediately with console output

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Search works → **MVP!**
3. Add User Story 2 → CSV export works → Most users satisfied
4. Add User Story 3 → Social links extracted → Higher value data
5. Add User Story 4 → Emails extracted → Business contact info
6. Add User Story 5 → JSON export → Developer-friendly
7. Polish → Tests, logging, robustness

### Recommended Order

For single developer: P1 → P2 (CSV) → P2 (Social) → P3 (Email) → P3 (JSON) → Polish

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Total tasks: 57
