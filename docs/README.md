# DotAIBuffBot

DotAIBuffBot is a Telegram bot plus local FastAPI service for collecting Dota 2 Game State Integration snapshots, building an internal match state, and preparing compact data for future AI recommendations.

## Runtime Flow

1. The user sends `/start` to the Telegram bot.
2. The bot shows localized buttons for GSI config, AI recommendation, and language switching.
3. `Получить GSI config` creates a personal GSI token and sends a `.cfg` file.
4. The user puts the config into the Dota 2 `gamestate_integration` folder and restarts Dota 2.
5. Dota 2 sends GSI snapshots to `POST /gsi`.
6. The API reads `payload["auth"]["token"]` and links the snapshot to a Telegram `user_id`.
7. `MatchService` coordinates snapshot processing.
8. Raw snapshots are temporarily saved to JSONL files for development analysis.
9. `MatchStateService` updates the normalized internal match state in Redis.
10. `DotaDataService` collects OpenDota data on startup and then once per day.
11. The recommendation button returns a summary of normalized match state. The future AI prompt combines that state with relevant OpenDota context.

## Main Components

`app/api/gsi.py`

Receives Dota 2 GSI snapshots. It stays thin: parse JSON, resolve user by token, pass payload to `MatchService`.

`app/services/client_link_service.py`

Creates a random GSI token with `secrets.token_urlsafe(32)`, stores it for the Telegram user, and builds the Dota 2 config file.

`app/repositories/client_link_repository.py`

Stores the long-lived `user_id -> gsi_token` link in SQLite.

`app/services/match_service.py`

Coordinates each incoming snapshot:

- gets `match_id`;
- writes raw snapshot to file;
- saves latest snapshot in Redis;
- updates accumulated match state;
- sends one match-start notification per `user_id + match_id`;
- saves active match id.

`app/services/gsi_snapshot_log_service.py`

Temporary development logger. It appends every raw snapshot to:

```text
data/gsi_snapshots/{session_id}_{user_id}_{match_id}.jsonl
```

Each line is one JSON object with `saved_at`, `user_id`, `match_id`, and raw `payload`. These files are for analysis only and are ignored by Git.

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
  "created_at": "...",
  "updated_at": "..."
}
```

Current hero sources:

- local player hero from `hero.name` and `player.team_name`;
- allied heroes from `minimap_herocircle`, `minimap_herocircle_self`, and `minimap_heroinvis`;
- enemy heroes from `minimap_enemyicon`;
- `minimap_plaincircle` is ignored because hero-selection snapshots assign noisy team ids;
- the last reliable visible position is stored for each minimap hero.

The latest real-match replay produced an exact 5v5 composition with these rules. Enemy data remains limited to information visible to the local player.

`app/services/game_advisor_service.py`

Current preview implementation formats accumulated `MatchState`. `build_prompt()` combines it with only match-relevant OpenDota hero stats, items, abilities, latest patch metadata, and patch notes.

`app/services/dota_data_service.py`

Collects external Dota data from OpenDota and keeps it in memory. It updates once on startup and then once per day.

Current OpenDota endpoints:

```text
/heroStats
/constants/heroes
/constants/items
/constants/abilities
/constants/patch
```

OpenDota requires a non-default `User-Agent`; the service sends `DotAIBuffBot/0.1`.

`app/dota_data_api.py`

Separate FastAPI app for collected Dota data. It exposes:

```text
GET /dota-data
```

Local port in `run_local.py`:

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
gsi:match_state:{user_id}:{match_id}
```

`gsi:snapshot:{user_id}` stores the latest raw snapshot.

`gsi:active_match:{user_id}` stores the current match id.

`gsi:match_started_notified:{user_id}` stores the match id for which the user already received a start notification.

`gsi:match_state:{user_id}:{match_id}` stores the accumulated normalized match state.

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

## Local Runtime

`run_local.py` starts:

- main Telegram bot;
- admin Telegram bot;
- FastAPI GSI endpoint on `127.0.0.1:8000`.
- FastAPI Dota data endpoint on `127.0.0.1:8001`.
- daily OpenDota data updater.

Before local services start, `prepare_runtime()` creates SQLite tables. If `CLEAR_GSI_STATE_ON_START=1`, it deletes Redis keys matching `gsi:*`. This is a temporary development setting to avoid mixing test matches when Dota reports `match_id = 0`.

## Config

Required environment variables:

```text
BOT_TOKEN=...
ADMIN_BOT_TOKEN=...
ADMIN_IDS=...
REDIS_URL=redis://localhost:6379/0
CLEAR_GSI_STATE_ON_START=1
```

The generated GSI config currently requests:

```text
provider
map
player
hero
abilities
items
draft
allplayers
buildings
minimap
wearables
```

Observed behavior so far:

- `draft` was empty in recorded bot and real matches;
- `allplayers` did not arrive in recorded matches;
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
  "hero_stats": [],
  "heroes": {},
  "items": {},
  "abilities": {},
  "patches": [],
  "latest_patch": {},
  "patch_notes": {}
}
```

OpenDota provides patch metadata through `constants/patch`, but not full patch note text in the currently used endpoints. `patch_notes` is kept as a separate block for the future patch notes source.

## Current Limitations

- `match_id = 0` in test games causes different test matches to share the same Redis key unless `gsi:*` is cleared.
- Enemy items, abilities, and complete player statistics are not available through the recorded GSI payloads.
- Match completion and per-match Redis cleanup are not implemented yet.
- The recommendation button does not call AI yet.
- Raw snapshot logging is temporary and should become optional debug behavior later.

## Next Architecture Step

Add the real AI client and prompt execution, then derive important match events such as level-ups, item purchases, deaths, buybacks, and destroyed buildings from successive `MatchState` updates.
