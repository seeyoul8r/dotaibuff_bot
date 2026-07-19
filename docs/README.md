# DotAIBuffBot

DotAIBuffBot is a Telegram bot plus local FastAPI service for collecting Dota 2 Game State Integration snapshots, building an internal match state, and generating compact AI recommendations during a match.

## Project Structure

- `app/` - application source code.
  - `ai/` - Gemini system prompts and AI-facing text instructions.
  - `api/` - FastAPI endpoints, including the Dota 2 GSI receiver.
  - `bot/` - Telegram bot layer: handlers, filters, inline keyboards, and localized user/admin messages.
  - `cache/` - Redis access wrapper for runtime match state.
  - `core/` - environment config loading.
  - `models/` - SQLite table models.
  - `repositories/` - SQLite persistence layer for users, client links, and AI request logs.
  - `schemas/` - dataclasses and Pydantic schemas shared between services.
  - `services/` - business logic: match processing, match state accumulation, Dota data loading, AI advice, GSI logging, and map location detection.
- `data/` - local runtime data such as Dota cache files, SQLite DB files, and GSI snapshot logs. Runtime/generated files are gitignored where needed.
- `docs/` - user manuals, internal architecture notes, and the editable Dota map location coverage HTML.
- `run_local.py` - local process entrypoint that starts the bots, GSI API, Dota data API, and startup data loader.
- `Dockerfile` - container image definition for the bundled runtime.
- `docker-compose.yml` - local/server stack definition for the app and Redis.
- `requirements.txt` - Python dependency list.

## Runtime Flow

1. The user sends `/start` to the Telegram bot.
2. `non_user_router` registers a new user, shows the localized welcome menu, and notifies every admin chat once.
3. The bot shows localized buttons for GSI config and language switching.
4. `Получить GSI config` creates a personal GSI token and sends a `.cfg` file.
5. The user puts the config into the Dota 2 `gamestate_integration` folder and restarts Dota 2.
6. Dota 2 sends GSI snapshots to `POST /gsi`.
7. The API reads `payload["auth"]["token"]` and links the snapshot to a Telegram `user_id`.
8. `MatchService` coordinates snapshot processing.
9. When `LOG_REQUESTS=1`, sanitized snapshots are saved to JSONL files for development analysis.
10. `MatchStateService` updates the normalized internal match state in Redis.
   It locks the exact 5v5 roster from draft and live minimap markers, or from 5 live allies plus 5 known enemy minimap icons when the client missed the exact draft snapshot, then keeps updating last seen enemy positions from `minimap_enemyicon`.
11. `DotaDataService` loads OpenDota, dota2.com datafeed, and STRATZ data from the local cache file on startup, or fetches it once if no cache exists yet.
12. The match start notification shows the enemy map info button and the recommendation button. The recommendation button combines normalized match state with relevant Dota mechanics context and calls Gemini.
13. When `LOG_REQUESTS=1`, the exact model request fields are written to SQLite before the Gemini call and updated with the response or error after the call.
14. The bot sends AI advice as one message with macro gaming, build, and current micro gaming advice. Enemy map info is sent by a separate `where_are_enemies` callback.

## Main Components

`app/api/gsi.py`

Receives Dota 2 GSI snapshots. It stays thin: parse JSON, resolve user by token, pass payload to `MatchService`.

`app/services/client_link_service.py`

Creates a random GSI token with `secrets.token_urlsafe(32)`, stores it for the Telegram user, and builds the Dota 2 config file.

`app/repositories/client_link_repository.py`

Stores the long-lived `user_id -> gsi_token` link in SQLite.

`app/bot/handlers/non_user.py`

Handles only users missing from SQLite. Its `/start` handler creates the user, sends the localized welcome menu, and notifies admins. Catch-all message and callback handlers explain the service and direct unregistered users to `/start`. The router is included before `user_router`, so stale inline buttons cannot reach handlers that require a saved language.

`app/services/match_service.py`

Coordinates each incoming snapshot:

- gets `match_id`;
- writes a sanitized snapshot to file when request logging is enabled;
- saves latest snapshot in Redis;
- updates accumulated match state;
- sends one match-start notification per `user_id + match_id`;
- saves active match id.

`app/services/gsi_snapshot_log_service.py`

Configurable development logger. When `LOG_REQUESTS=1`, it appends every sanitized snapshot to:

```text
data/gsi_snapshots/{session_id}_{user_id}_{match_id}.jsonl
```

Each line is one JSON object with `saved_at`, `user_id`, `match_id`, and sanitized `payload`. Before writing to disk, `GsiSnapshotLogService` removes `previously`, `added`, and `auth` from the saved payload. Full incoming payloads are still passed to match processing before sanitizing for disk. With `LOG_REQUESTS=0`, the service creates no directory or file. These files are for analysis only and are ignored by Git.

`app/repositories/ai_request_repository.py`

Stores the Gemini request lifecycle in SQLite when `LOG_REQUESTS=1`. `GameAdvisorService` creates one `ai_requests` row before the Gemini call with status `started`, then updates the same row to `completed` with the parsed response or to `failed` with the error text. API keys are never stored. With `LOG_REQUESTS=0`, no AI request log row is created.

`app/services/match_state_service.py`

Builds the internal match entity by applying snapshots over time. This exists because the latest GSI snapshot can be incomplete.

Current state shape:

```json
{
  "user_id": 90547891,
  "match_id": 0,
  "game_state": "DOTA_GAMERULES_STATE_STRATEGY_TIME",
  "game_time": 47,
  "clock_time": -2,
  "radiant_score": 0,
  "dire_score": 0,
  "player": {},
  "hero": {},
  "abilities": {},
  "items": {},
  "buildings": {},
  "radiant": {"heroes": {}},
  "dire": {"heroes": {}},
  "unknown_heroes": {},
  "roster_locked": false,
  "enemy_detection_ready": false,
  "created_at": "...",
  "updated_at": "..."
}
```

Current hero sources:

- local player hero from `hero.name` and `player.team_name`;
- allied heroes from `minimap_herocircle`, `minimap_herocircle_self`, and `minimap_heroinvis`;
- enemy heroes from `minimap_enemyicon`;
- draft hero pool from unique `minimap_plaincircle` names before the roster is locked;
- before the roster is locked, visible enemies from `minimap_enemyicon` already store last seen position, calibrated map location slug, game time, and current visibility;
- after the roster is locked, the last visible enemy position, calibrated map location slug, game time, and current visibility are stored for locked enemy heroes.

`minimap_plaincircle.team` and draft-layout coordinates are not reliable. Team assignment therefore follows this sequence:

1. `player.team_name` defines the local and opposing teams.
2. `HeroTeamDetector` stores the latest snapshot with exactly 10 unique `minimap_plaincircle` hero names in `draft_heroes` as the draft pool.
3. Live allied markers from `minimap_herocircle`, `minimap_herocircle_self`, and `minimap_heroinvis` build the local team candidate.
4. The primary roster lock path requires the draft pool to have exactly 10 unique heroes, the live allied candidate to have exactly 5 unique heroes, and the local hero to be one of those 5.
5. If the draft pool is unavailable but the accumulated live minimap state has 5 allied heroes and 5 enemy heroes from `minimap_enemyicon`, those 10 heroes are used to lock the roster.
6. The 5 live allied heroes are assigned to the local player's team, and the 5 enemy heroes from the draft pool or live enemy icons are assigned to the opposing team.
7. After `roster_locked = true`, minimap hero roster detection stops changing team membership, but `minimap_enemyicon` keeps updating visibility and last seen data for the locked enemy roster.

Enemy position fields stored inside each locked enemy hero state:

```json
{
  "was_visible": true,
  "visible": true,
  "last_seen_position": {"xpos": -3679, "ypos": -1683},
  "last_seen_location_slug": "radiant_triangle",
  "last_seen_game_time": 645,
  "last_seen_image": "minimap_enemyicon"
}
```

`last_seen_location_slug` is returned by `MapLocationService` from calibrated Dota map coordinates. It uses 30 large nearest-point circular or oval zones for highgrounds, lanes, jungles, triangles, lotus pools, tormentors, twin gates, wisdom runes, secret shops, edge areas, and separate top/bot Roshan pits. Coordinates inside a zone return that zone, and coordinates slightly outside coverage return the nearest zone up to `NEAREST_LOCATION_DISTANCE_LIMIT`. Coordinates farther away return `unknown`.

`app/services/map_location_service.py`

Maps raw GSI minimap coordinates to stable location slugs by nearest calibrated point with a per-point zone. `MapLocationPoint.radius` is the X radius. `radius_y` is optional; when it is missing, the zone stays circular. `rotation` rotates oval zones in degrees. The closest zone wins when the coordinate is inside the normalized circular or oval boundary, or when it is outside all zones but still within `NEAREST_LOCATION_DISTANCE_LIMIT = 1.35` from the nearest zone. Runtime map zones are intentionally coarse and user-facing; old tower/river/camp micro-zones were replaced by large area zones. The service returns slugs only; the user bot formats location slugs as English readable names for both RU and EN interfaces.

Zones can be inspected and edited visually in `docs/map-location-coverage.html`, which overlays GSI zones on `docs/dota_tga_d8178876.png` through the official `dota.txt` overview values: `pos_x = -9472`, `pos_y = 9472`, `scale = 18.5`. The logical overview is `1024x1024`: this maps Dota coordinates from `-9472..9472` on each axis. The editor can add zones, delete zones, move zone centers, resize X/Y radiuses, rotate ovals, and export ready-to-copy `MapLocationPoint(...)` lines for `app/services/map_location_service.py`.

The `8892275624` recording demonstrated this flow for two users on Radiant. Sven and Night Stalker both locked the same allied roster: Sven, Night Stalker, Disruptor, Grimstroke, and Medusa. Bloodseeker, Nyx Assassin, Oracle, Sniper, and Spectre were assigned to Dire.

The `8893000272` recording showed why the draft pool is stored only from exact 10-hero snapshots. Later pre-game minimap snapshots contained stale showcase heroes such as Axe and Venomancer; keeping the latest exact 10-hero pool allowed Warlock on Dire to lock Bloodseeker, Gyrocopter, Invoker, Tiny, and Warlock as allies, with Dazzle, Shadow Fiend, Pangolier, Sniper, and Tidehunter as enemies.

`app/services/game_advisor_service.py`

Builds compact AI context containing only heroes in the match, Dota 2 datafeed mechanics for those heroes, the local player inventory item mechanics, and current patch data. It uses the structured `GameAdvice` response model with `macro_gaming`, `build`, and `micro_gaming` fields, serializes the model contents once, logs the request when enabled, calls Gemini with structured output, and tracks the per-user recommendation cooldown in process memory. One async Gemini client is created when the service starts and reused for all requests.

`app/schemas/ai.py`

Stores AI response schemas such as `GameAdvice`.

`app/schemas/config.py`

Stores environment config dataclasses. `app/core/config.py` only reads environment values and returns these schema objects.

`app/schemas/match_state.py`

Stores accumulated match state schemas such as `MatchHeroState`. `MatchHeroState` is converted to a dict before Redis storage.

`app/schemas/map_location.py`

Stores map location calibration schemas such as `MapLocationPoint`.

`app/ai/prompts.py`

Stores `GAME_ADVISOR_PROMPT`. The prompt requires advice based only on supplied data and requests the answer in the user's selected language.

`app/services/dota_data_service.py`

Sends admin-bot notifications when Dota data updates start, complete, or fail.

Collects external Dota data from OpenDota, dota2.com datafeed, and the STRATZ GraphQL API, and keeps it in memory. There is no automatic periodic refresh — `load_startup_data()` runs once at process start: if `data/dota_data_cache.json` exists and is non-empty, it loads straight from that file with no network calls (fast restarts, no API usage); otherwise it runs a full `update_data()` fetch and writes the cache. The admin `Update Dota data` button always calls `update_data()` directly, which re-fetches everything from the network and overwrites the cache file — this is the only way data refreshes after the first successful load.

Every update prints start and completion messages to the console. The completion message includes hero, item, and ability counts plus the latest patch name and STRATZ record counts.

`fetch_all_stratz_data()` sends one combined GraphQL query per hero (`STRATZ_HERO_QUERY`) to `https://api.stratz.com/graphql`, authenticated with `STRATZ_API_TOKEN`. It builds:

- `hero_win_rates`: per hero, win/match count for the most recent `gameVersionId` (current patch).
- `hero_counters`: per hero, a map of opponent hero name to `win_rate`/`synergy`/`match_count`, read from `heroVsHeroMatchup(heroId, take: 150).advantage[0].vs` — a large `take` returns the full sorted list in one call instead of only the top/bottom entries.
- `hero_builds`: per hero, `starting_items`, `core_items`, `ability_min_level`, `ability_max_level`, and `talents`, each a list with one representative (highest match count) row per item/ability, sorted by match count. `normalize_stratz_rows()` does this deduplication and maps STRATZ numeric ids to names: items use the `id` field already loaded from OpenDota `/constants/items`; abilities use `/constants/ability_ids` (a separate id→name resource — `/constants/abilities` itself has no numeric id field).

Ability names from `ability_ids` occasionally use an older internal codename than the one Dota GSI reports for the same ability (for example Warlock's abilities are `greevil_*` in OpenDota constants but `warlock_*` in live GSI payloads). This is a pre-existing OpenDota/GSI naming mismatch, not introduced by the STRATZ integration — `hero_builds` ability entries can end up keyed differently than `match_state.abilities` for the handful of heroes affected.

STRATZ queries use no rank bracket or position filter yet (all-bracket aggregate) to keep the integration minimal; the query already accepts `bracketBasicIds`/`positionIds` if per-rank filtering is added later. About 124 GraphQL calls run per update cycle, well under STRATZ's per-hour rate limit.

Current OpenDota endpoints:

```text
/heroStats
/constants/heroes
/constants/items
/constants/abilities
/constants/ability_ids
/constants/patch
```

Dota 2 datafeed endpoints used for current mechanics:

```text
/datafeed/herolist?language=english
/datafeed/herodata?language=english&hero_id={hero_id}
/datafeed/itemlist?language=english
/datafeed/itemdata?language=english&item_id={item_id}
```

Hero mechanics are loaded from cache or fetched on startup, and refreshed only by the admin update button. Item mechanics are loaded lazily for items present in the local player inventory and are also persisted in the cache file. The AI context uses English mechanics data and only the final answer language is localized.

`data/dota_data_cache.json` holds every field listed in `CACHE_FIELDS` (heroes, items, abilities, ability_ids, patches, datafeed data, hero_mechanics, item_mechanics, hero_win_rates, hero_counters, hero_builds, updated_at) as one JSON object — a full in-memory snapshot, not an append log. It is gitignored; delete it to force a full re-fetch on the next restart.
`data/dota_data_cache.json` field meanings:

- `hero_stats`: OpenDota `/heroStats` rows indexed by GSI hero name, for example `npc_dota_hero_antimage -> {"id": 1, "name": "npc_dota_hero_antimage"}`.
- `heroes`: OpenDota `/constants/heroes` definitions combined with `hero_stats`, for example `{"definition": {"localized_name": "Anti-Mage"}, "stats": {"primary_attr": "agi"}}`.
- `items`: OpenDota `/constants/items` item definitions, for example `blink -> {"id": 1, "dname": "Blink Dagger"}`.
- `abilities`: OpenDota `/constants/abilities` ability definitions, for example `antimage_mana_break -> {"dname": "Mana Break"}`.
- `ability_ids`: OpenDota `/constants/ability_ids` numeric ability id lookup used for STRATZ rows, for example `"5003" -> "antimage_mana_break"`.
- `patches`: OpenDota `/constants/patch` patch metadata list, for example `{"name": "7.39", "date": 174...}`.
- `latest_patch`: the last entry from `patches`, used as the current known patch metadata.
- `patch_notes`: reserved patch notes map; currently saved as an empty object.
- `datafeed_heroes`: dota2.com `/datafeed/herolist` hero rows indexed by hero name, for example `npc_dota_hero_antimage -> {"id": 1, "name": "npc_dota_hero_antimage"}`.
- `datafeed_items`: dota2.com `/datafeed/itemlist` item rows indexed by item name, for example `item_blink -> {"id": 1, "name": "item_blink"}`.
- `hero_mechanics`: dota2.com `/datafeed/herodata` hero detail data, including abilities, talents, facets, and innate data.
- `item_mechanics`: dota2.com `/datafeed/itemdata` item detail data; `update_data()` resets it to `{}` and item details are loaded lazily for local inventory items.
- `hero_win_rates`: STRATZ GraphQL hero win/match counts for the latest returned game version.
- `hero_counters`: STRATZ GraphQL hero-vs-hero matchup data, keyed by local hero name and enemy hero name.
- `hero_builds`: STRATZ GraphQL starting items, core items, ability order, and talents, normalized to one representative row per item/ability.
- `updated_at`: UTC ISO timestamp of the last successful cache update.

OpenDota requires a non-default `User-Agent`; the service sends `DotAIBuffBot/0.1`.

Runtime storage is indexed by GSI names:

```json
{
  "heroes": {
    "npc_dota_hero_warlock": {
      "definition": {},
      "stats": {}
    }
  },
  "items": {
    "glimmer_cape": {}
  },
  "abilities": {
    "warlock_fatal_bonds": {}
  },
  "patch": {
    "metadata": {},
    "notes": {}
  }
}
```

`app/dota_data_api.py`

Separate FastAPI app for collected Dota data. It exposes:

```text
GET /dota-data
```

Local port in `run_local.py`, from `DOTA_DATA_HOST`/`DOTA_DATA_PORT` (defaults below):

```text
127.0.0.1:8001
```

`app/bot/messages`

Stores all user-facing bot texts in `user_ru.py` and `user_en.py`. Code should read texts through `mes_user[lang]`.

`app/bot/keyboards/inline`

Stores localized inline keyboards in `user_ru.py` and `user_en.py`. Code should read user keyboards through `kb_user[lang]`.

`app/cache/redis_cache.py`

Redis runtime storage wrapper and shared instance.

## Redis Keys

```text
gsi:snapshot:{user_id}
gsi:active_match:{user_id}
gsi:match_started_notified:{user_id}
gsi:match_finished_notified:{user_id}:{match_id}
gsi:match_state:{user_id}:{match_id}
```

`gsi:snapshot:{user_id}` stores the latest raw snapshot.

`gsi:active_match:{user_id}` stores the current match id.

`gsi:match_started_notified:{user_id}` stores the match id for which the user already received a start notification.

`gsi:match_finished_notified:{user_id}:{match_id}` stores the finished match notification flag to avoid repeated post-game summaries.

`gsi:match_state:{user_id}:{match_id}` stores the accumulated normalized match state.

After the final post-game summary, `MatchService` deletes `gsi:snapshot:{user_id}`, `gsi:active_match:{user_id}`, and `gsi:match_state:{user_id}:{match_id}`. The notification flags stay in Redis so repeated post-game snapshots do not resend start or finish messages.

## User Menu Flow

The main user menu contains `GSI config` and the language toggle. `open_gsi_menu` edits only the existing message reply markup and shows `Get GSI config`, `What is GSI config?`, and `Back`. Opening this submenu must not call `ClientLinkService`, because `get_gsi_config` regenerates the long-lived client token and config file only when the user explicitly presses the download button. `back_to_main_menu` restores the main menu with `edit_reply_markup`. The enemy map info and AI recommendation buttons are attached to the match start notification instead of the main menu.

## AI Advice Flow

1. The Telegram handler verifies that accumulated match state exists.
2. It checks the in-memory cooldown for the Telegram `user_id`.
3. The handler starts an ephemeral `sendMessageDraft` with empty text. Telegram renders its native animated Thinking placeholder, and the handler refreshes the same `draft_id` every 20 seconds.
4. `GameAdvisorService.build_prompt()` creates this JSON input:

```json
{
  "language": "Russian",
  "match_state": {},
  "dota_context": {
    "updated_at": "...",
    "patch": {},
    "hero_mechanics": {},
    "local_items": {},
    "hero_win_rates": {},
    "local_hero_counters": {},
    "local_hero_builds": {}
  }
}
```

`hero_win_rates` covers every hero in the match roster. `local_hero_counters` and `local_hero_builds` are scoped to the local hero only: counters are filtered to the current enemy lineup, and builds are the local hero's own STRATZ item/ability/talent data — matching how `local_items` already scopes mechanics to the local inventory.

`match_state` is compacted before sending to AI. The Redis state keeps timestamps, source history, roster-lock metadata, enemy visibility, and full hero buckets. The prompt receives current match time, score, local player state, local hero state, current abilities/items, buildings, Radiant/Dire hero name lists, and `enemy_positions` with all locked enemy heroes, last seen location slug, coordinates, game time, and `seen_seconds_ago`.

Raw OpenDota hero definitions are not sent to AI. Hero identity comes from `match_state`, while combat details come from `hero_mechanics`, win rates, counters, and builds.

Enemy position reasoning is scoped to `macro_gaming`. The prompt treats `seen_seconds_ago` as uncertainty, not as a fixed threshold. It asks the model to infer whether missing enemies are likely farming, moving, warding, smoking, setting up Roshan, or preparing a gank from hero role, last seen area, current game time, visible enemy count, objectives, and map state. Farming cores missing near jungle/triangle/lane/edge farm areas should not automatically be treated as danger; initiators, roamers, supports, or several missing enemies increase smoke/gank/objective risk. Suggested actions should be concrete: ward, play safer, group, gank a likely farm route, push a lane, or avoid risky Roshan/highground.

`hero_mechanics` is prompt-optimized by `GameAdvisorService.compact_hero_mechanics()` before sending to AI. The local hero keeps abilities, shard, scepter, talents, and facets. Allied and enemy heroes keep abilities, shard, and scepter so the model can reason about teamfight coordination and enemy threats without sending talent data or empty technical fields.

`local_items` is also compacted with `GameAdvisorService.compact_ability_or_item()` so item descriptions, cooldowns, costs, behavior, and special values remain available without empty ability flags.

5. `GameAdvisorService.request_advice()` serializes the contents once and, when enabled, writes the exact request fields to the `ai_requests` SQLite table.
6. The service sends the JSON and `GAME_ADVISOR_PROMPT` to `gemini-3.5-flash` with the configured thinking level.
7. The Google Gen AI SDK parses the JSON response directly into `GameAdvice`.
8. The handler stops the ephemeral draft and sends one localized message containing the three advice sections.
9. The successful response message ends with the cooldown-period text and includes inline `where_are_enemies` and `get_ai_advice` buttons for follow-up requests.
10. If the Gemini request fails, the handler stops the draft and sends a localized error message.

The cooldown is configured by `AI_ADVICE_COOLDOWN` and is set before the paid API request. It is stored in `GameAdvisorService._cooldowns`, resets when the bot process restarts, and can be changed at runtime through the admin `Set advice cooldown` button.

## Enemy Map Info Flow

1. The `where_are_enemies` callback verifies that accumulated match state exists.
2. The handler formats the current match time and enemy map info from `match_state` as a readable bullet list, not a pipe-delimited table.
3. Enemy locations are recalculated from `last_seen_position` during formatting, so active Redis states use the current map zoning even if an older `last_seen_location_slug` was stored before deployment.
4. Enemy location slugs are rendered as English readable names in both languages, for example `radiant_jungle_big -> Radiant Jungle Big`.
5. Enemies with no last seen position are shown as `Not seen yet`; enemies with coordinates too far from the nearest configured zone are shown as `Unknown area`.
6. The bot sends a separate localized message with match time, enemy locations, and the same follow-up keyboard as the AI advice message.

## SQLite Tables

`users`

Base Telegram users table. It stores the selected user language in `lang`.

`client_links`

Stores one active GSI token per Telegram user:

```text
user_id
gsi_token
created_at
updated_at
```

`ai_requests`

Stores one Gemini advice request lifecycle per generated `request_id` when `LOG_REQUESTS=1`:

```text
request_id
user_id
match_id
request_started_at
request
response_finished_at
response
model
system_instruction
response_mime_type
response_schema
thinking_level
status
error
```

`status` starts as `started`, changes to `completed` after a parsed `GameAdvice` response is saved, and changes to `failed` when the Gemini call raises an exception.

## Local Runtime

## Admin Bot

The admin bot `/start` menu includes maintenance actions:

- `Manage User`: input a Telegram user id and view saved user/GSI token metadata.
- `Userlist`: show saved users from SQLite.
- `Send all`: broadcast an admin message to all saved users.
- `Update DB`: run `db.create_tables()`.
- `Update Dota data`: force `DotaDataService.update_data()` immediately. Admin chats receive update start, completion duration, loaded counts, and failure notifications.
- `Set advice cooldown`: update `AI_ADVICE_COOLDOWN` in `.env` and call `GameAdvisorService.reload_config()` so the new value applies without a container restart.
- `Error log` / `Clean log`: read or clear `error_log.txt`.

The admin bot also receives one plain-text notification when a new user registers through the main bot. Notification delivery is isolated per admin chat so one unavailable chat does not block the others.


`run_local.py` starts:

- main Telegram bot;
- admin Telegram bot;
- FastAPI GSI endpoint on `GSI_HOST:GSI_PORT` (defaults to `127.0.0.1:8000`).
- FastAPI Dota data endpoint on `DOTA_DATA_HOST:DOTA_DATA_PORT` (defaults to `127.0.0.1:8001`).
- Dota data loader (`load_startup_data()`) — cache-or-fetch-once, no periodic refresh.

Before local services start, `prepare_runtime()` creates SQLite tables. If `CLEAR_GSI_STATE_ON_START=1`, it deletes Redis keys matching `gsi:*`. This is a temporary development setting to avoid mixing test matches when Dota reports `match_id = 0`. Keep this at `0` on a server, otherwise every restart wipes every user's active match.

## Config

Required environment variables:

```text
BOT_TOKEN=...
ADMIN_BOT_TOKEN=...
ADMIN_IDS=...
REDIS_URL=redis://localhost:6379/0
CLEAR_GSI_STATE_ON_START=1
LOG_REQUESTS=1
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-3.5-flash
GEMINI_THINKING_LEVEL=low
AI_ADVICE_COOLDOWN=180
GSI_HOST=0.0.0.0
GSI_PORT=8000
GSI_PUBLIC_URL=http://193.42.60.48/gsi
DOTA_DATA_HOST=127.0.0.1
DOTA_DATA_PORT=8001
STRATZ_API_TOKEN=Bearer ...
```

`STRATZ_API_TOKEN` is the Bearer token from a STRATZ account API key (`stratz.com`, logged in via Steam) and must include the `Bearer ` prefix — `DotaDataService` sends it as-is in the `Authorization` header.

`LOG_REQUESTS=1` enables sanitized GSI snapshot files and exact AI request rows in SQLite. Set it to `0` to disable both request log writers. The value is read on process startup.

`GSI_HOST`/`GSI_PORT`/`DOTA_DATA_HOST`/`DOTA_DATA_PORT` and `GSI_PUBLIC_URL` all default to the values above, so an `.env` without them keeps today's local-only behavior unchanged.

`GSI_PUBLIC_URL` is written into the `.cfg` file `ClientLinkService.build_gsi_config()` generates — it is the address the Dota 2 client itself sends snapshots to, so it must be reachable from the player's machine. On a server behind Caddy this should be the public IP or domain without the internal FastAPI port, for example `http://193.42.60.48/gsi`.

## Docker

`Dockerfile` builds one image that runs `run_local.py` as its entrypoint, so the containerized process is the same bot + GSI API + Dota data API + Dota data loader bundle as the local run.

`docker-compose.yml` runs that image as the `app` service, starts Redis as the `redis` service with its own named volume, reads `.env` through `env_file`, overrides `REDIS_URL` to `redis://redis:6379/0` for container networking, binds FastAPI to `127.0.0.1:8000` for Caddy, publishes no public FastAPI port, and bind-mounts the whole project into `/app` so `git pull` plus an app container restart updates Python code without rebuilding the image.

After code-only changes on a server:

```text
git pull
docker compose restart app
```

Rebuild is still required when `requirements.txt` or `Dockerfile` changes:

```text
docker compose up -d --build
```

Start the full local stack with:

```text
docker compose up -d --build
```

Keep `REDIS_URL=redis://localhost:6379/0` in `.env` for direct host runs. Docker Compose overrides it with `redis://redis:6379/0` so the app container connects to the bundled Redis service.

For a server deployment, also set `GSI_HOST=0.0.0.0`, set `GSI_PUBLIC_URL` to the Caddy public address, and route `/gsi*` from Caddy to `localhost:8000`.

The generated GSI config currently requests:

```text
provider
map
player
hero
abilities
items
buildings
minimap
```

Observed behavior so far:

- full abilities and items are available only for the local player;
- minimap markers expose allied heroes and currently visible enemy heroes;
- buildings currently contain only the local player's side;
- raw snapshots are currently the best way to verify what Dota actually sends.

## Dota Data API

The Dota data service currently stores data in memory only. Endpoint response shape:

```json
{
  "updated_at": "...",
  "is_ready": true,
  "heroes": {},
  "items": {},
  "abilities": {},
  "hero_win_rates": {},
  "hero_counters": {},
  "hero_builds": {},
  "patches": [],
  "patch": {
    "metadata": {},
    "notes": {}
  }
}
```

OpenDota provides patch metadata through `constants/patch`, but not full patch note text. `patch.notes` is reserved for a future official Dota patch notes source.

## Current Limitations

- `match_id = 0` in test games causes different test matches to share the same Redis key unless `gsi:*` is cleared.
- Enemy items and complete player statistics are not available through the recorded GSI payloads.
- AI recommendations require a valid `GEMINI_API_KEY` and current accumulated match state.
- The recommendation cooldown is local to one bot process and is not shared through Redis.
- Request logs are development artifacts. GSI snapshot files and `ai_requests` SQLite rows can grow until they are removed manually.
- STRATZ data (`hero_win_rates`/`hero_counters`/`hero_builds`) is an all-bracket, all-position aggregate; rank/role filtering is not implemented yet.

## Next Architecture Step

Derive important match events such as level-ups, item purchases, deaths, buybacks, and destroyed buildings from successive `MatchState` updates. Add an official source for full patch note text.
