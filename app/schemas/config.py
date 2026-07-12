from dataclasses import dataclass


@dataclass
class TgBot:
    """Store Telegram bot config."""
    token: str
    admin_ids: list[int]


@dataclass
class Config:
    """Store application bot config."""
    tg_bot: TgBot


@dataclass
class RedisConfig:
    """Store Redis config."""
    redis_url: str
    clear_gsi_state_on_start: bool


@dataclass
class LoggingConfig:
    """Store request logging config."""
    log_requests: bool


@dataclass
class AIConfig:
    """Store AI advisor config."""
    api_key: str
    model: str
    thinking_level: str
    advice_cooldown: int


@dataclass
class ServerConfig:
    """Store local server networking config."""
    gsi_host: str
    gsi_port: int
    gsi_public_url: str
    dota_data_host: str
    dota_data_port: int


@dataclass
class StratzConfig:
    """Store STRATZ API config."""
    api_token: str
