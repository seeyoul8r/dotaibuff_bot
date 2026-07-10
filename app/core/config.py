from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]


@dataclass
class Config:
    tg_bot: TgBot


@dataclass
class RedisConfig:
    redis_url: str
    clear_gsi_state_on_start: bool


@dataclass
class AIConfig:
    api_key: str
    model: str
    thinking_level: str
    advice_cooldown: int


@dataclass
class ServerConfig:
    gsi_host: str
    gsi_port: int
    gsi_public_url: str
    dota_data_host: str
    dota_data_port: int


def load_config(path: str | None = None) -> Config:
    """Read main bot config from environment."""
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'), admin_ids=list(map(int, env.list('ADMIN_IDS')))))


def load_admin_config(path: str | None = None) -> Config:
    """Read admin bot config from environment."""
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('ADMIN_BOT_TOKEN'), admin_ids=list(map(int, env.list('ADMIN_IDS')))))


def load_redis_config(path: str | None = None) -> RedisConfig:
    """Read Redis config from environment."""
    env = Env()
    env.read_env(path)
    return RedisConfig(redis_url=env('REDIS_URL'), clear_gsi_state_on_start=env.bool('CLEAR_GSI_STATE_ON_START'))


def load_ai_config(path: str | None = None) -> AIConfig:
    """Read AI config from environment."""
    env = Env()
    env.read_env(path)
    return AIConfig(
        api_key=env('GEMINI_API_KEY'),
        model=env('GEMINI_MODEL'),
        thinking_level=env('GEMINI_THINKING_LEVEL'),
        advice_cooldown=env.int('AI_ADVICE_COOLDOWN')
    )


def load_server_config(path: str | None = None) -> ServerConfig:
    """Read GSI and Dota data server networking config from environment."""
    env = Env()
    env.read_env(path)
    return ServerConfig(
        # Defaults match the current local-only setup so nothing changes without an .env override.
        gsi_host=env.str('GSI_HOST', '127.0.0.1'),
        gsi_port=env.int('GSI_PORT', 8000),
        gsi_public_url=env.str('GSI_PUBLIC_URL', 'http://127.0.0.1:8000/gsi'),
        dota_data_host=env.str('DOTA_DATA_HOST', '127.0.0.1'),
        dota_data_port=env.int('DOTA_DATA_PORT', 8001)
    )
