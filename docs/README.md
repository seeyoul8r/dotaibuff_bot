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
10. The recommendation button currently returns a short snapshot summary. Later it should use normalized match state plus Dota context for AI.

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
data/gsi_snapshots/{user_id}_{match_id}.jsonl
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
  "radiant": {"heroes": {}},
  "dire": {"heroes": {}},
  "unknown_heroes": {},
  "created_at": "...",
  "updated_at": "..."
}
```

Current hero sources:

- local player hero from `hero.name` and `player.team_name`;
- visible minimap heroes from `minimap[*].unitname`;
- `minimap.team == 2` is treated as radiant;
- `minimap.team == 3` is treated as dire;
- unknown team ids go to `unknown_heroes`.

This minimap team mapping is still experimental. Saved JSONL snapshots should be used to verify it before relying on it for AI.

`app/services/game_advisor_service.py`

Current preview implementation. It formats the latest raw snapshot. The intended next step is to use `MatchState` instead of raw GSI payload.

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

- `draft` exists but can be empty;
- `allplayers` may not arrive;
- `minimap` can contain hero unit names before or around strategy time;
- raw snapshots are currently the best way to verify what Dota actually sends.

## Current Limitations

- `match_id = 0` in test games causes different test matches to share the same Redis key unless `gsi:*` is cleared.
- Minimap team ids need more validation. Some strategy-time snapshots can assign many heroes to one team.
- The recommendation button does not call AI yet.
- Raw snapshot logging is temporary and should become optional debug behavior later.

## Next Architecture Step

Use `MatchState` as the main AI input instead of the latest raw snapshot. The AI payload should contain compact, normalized data: current stage, player hero, likely teams, abilities, items, buildings, visible map entities, and known uncertainty.
