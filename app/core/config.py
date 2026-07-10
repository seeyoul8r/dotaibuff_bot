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
    reasoning_effort: str
    advice_cooldown: int


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
        api_key=env('OPENAI_API_KEY'),
        model=env('OPENAI_MODEL'),
        reasoning_effort=env('OPENAI_REASONING_EFFORT'),
        advice_cooldown=env.int('AI_ADVICE_COOLDOWN')
    )
